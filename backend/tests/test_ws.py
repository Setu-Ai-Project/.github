"""Tests for the authenticated WebSocket endpoint /ws."""

from unittest.mock import MagicMock
import pytest
from sqlmodel import Session, select
from starlette.websockets import WebSocketDisconnect

from models.user import User
from realtime.manager import manager


@pytest.fixture(autouse=True)
def clean_manager_and_db(session: Session, monkeypatch: pytest.MonkeyPatch):
    """Ensure clean manager state and point ws_routes database engine to the test SQLite DB."""
    # Ensure active connections are clean before test
    manager.active.clear()

    # Direct database operations in ws_routes to the test session's SQLite engine
    monkeypatch.setattr("realtime.ws_routes.engine", session.bind)

    yield

    # Clean up after test
    manager.active.clear()


def test_ws_missing_token_rejected(client):
    """WebSocket connection without token parameter is rejected with close code 1008."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws"):
            pass

    assert exc_info.value.code == 1008
    assert manager.active == {}


def test_ws_empty_token_rejected(client):
    """WebSocket connection with empty token parameter is rejected with close code 1008."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws?token="):
            pass

    assert exc_info.value.code == 1008
    assert manager.active == {}


def test_ws_invalid_token_rejected(client, monkeypatch):
    """Invalid token fails verification and closes with 1008 before accepting."""
    monkeypatch.setattr(
        "realtime.ws_routes.verify_clerk_token",
        MagicMock(side_effect=ValueError("Token signature invalid")),
    )

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws?token=invalid_token"):
            pass

    assert exc_info.value.code == 1008
    assert manager.active == {}


def test_ws_unknown_user_rejected_and_no_row_created(client, session: Session, monkeypatch):
    """A valid token for an unknown user is rejected with 1008 and never creates a user row."""
    monkeypatch.setattr(
        "realtime.ws_routes.verify_clerk_token",
        MagicMock(return_value="user_unknown_clerk"),
    )

    count_before = len(session.exec(select(User)).all())

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws?token=valid_token_for_unknown"):
            pass

    assert exc_info.value.code == 1008

    # Assert no user row was created
    count_after = len(session.exec(select(User)).all())
    assert count_after == count_before
    unknown_user = session.exec(
        select(User).where(User.clerk_user_id == "user_unknown_clerk")
    ).first()
    assert unknown_user is None
    assert manager.active == {}


def test_ws_valid_token_ping_pong(client, session: Session, monkeypatch):
    """A valid token with matching local user establishes connection and replies to ping with pong."""
    user = User(
        name="Test Learner",
        email="learner@example.com",
        hashed_password="pw_hash_test",
        clerk_user_id="user_clerk_registered_1",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    monkeypatch.setattr(
        "realtime.ws_routes.verify_clerk_token",
        MagicMock(return_value="user_clerk_registered_1"),
    )

    with client.websocket_connect("/ws?token=valid_token_123") as ws:
        # Verify connection is registered with manager
        assert user.id in manager.active
        assert len(manager.active[user.id]) == 1

        # Test ping-pong
        ws.send_text("ping")
        response = ws.receive_text()
        assert response == "pong"


def test_ws_connection_cleanup_on_disconnect(client, session: Session, monkeypatch):
    """When a client disconnects, its connection is removed from manager.active."""
    user = User(
        name="Cleanup Learner",
        email="cleanup@example.com",
        hashed_password="pw_hash_test",
        clerk_user_id="user_clerk_cleanup_2",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    monkeypatch.setattr(
        "realtime.ws_routes.verify_clerk_token",
        MagicMock(return_value="user_clerk_cleanup_2"),
    )

    with client.websocket_connect("/ws?token=valid_token_cleanup") as ws:
        assert user.id in manager.active
        assert len(manager.active[user.id]) == 1

    # After exiting context manager, client is disconnected and manager must be cleaned up
    assert user.id not in manager.active
    assert manager.active == {}
