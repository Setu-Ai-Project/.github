"""Tests for Step 5.7c: notify_progress and realtime notifications."""

import asyncio
import logging
from unittest.mock import MagicMock
import pytest
from sqlmodel import Session

from main import app
from middleware.auth import get_current_user
from models.challenge import Challenge
from models.module import Module
from models.sub_module import SubModule
from models.user import User
from realtime.notify import notify_progress


class FakeManager:
    """Mock connection manager for isolating notification dispatch."""

    def __init__(self):
        self.loop = MagicMock(spec=asyncio.AbstractEventLoop)
        self.calls: list[tuple[int, dict]] = []

    def send_to_user(self, user_id: int, message: dict):
        self.calls.append((user_id, message))

        async def _coro():
            pass

        return _coro()


@pytest.fixture
def mock_scheduling(monkeypatch):
    """Provides a fake manager and mocked asyncio.run_coroutine_threadsafe.

    Closes coroutines to prevent unawaited-coroutine RuntimeWarnings.
    """
    fake_mgr = FakeManager()
    monkeypatch.setattr("realtime.notify.manager", fake_mgr)

    scheduled: list[tuple[any, any]] = []

    def fake_run_coroutine_threadsafe(coro, loop):
        scheduled.append((coro, loop))
        assert asyncio.iscoroutine(coro)
        coro.close()
        return MagicMock()

    monkeypatch.setattr(asyncio, "run_coroutine_threadsafe", fake_run_coroutine_threadsafe)
    return fake_mgr, scheduled


def _create_user(
    session: Session,
    *,
    clerk_id: str = "clerk_notify_test",
    email: str = "notify@example.com",
    total_xp: int = 0,
    level: int = 1,
) -> User:
    user = User(
        name="Notify Learner",
        email=email,
        hashed_password="fake_password",
        clerk_user_id=clerk_id,
        total_xp=total_xp,
        level=level,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_hierarchy(session: Session, xp_reward: int = 50) -> Challenge:
    module = Module(title="Notify Module", description="Notify Description", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)

    sub_module = SubModule(
        title="Notify SubModule",
        description="Notify SubModule Description",
        order=1,
        module_id=module.id,
    )
    session.add(sub_module)
    session.commit()
    session.refresh(sub_module)

    challenge = Challenge(
        sub_module_id=sub_module.id,
        title="Notify Challenge",
        xp_reward=xp_reward,
    )
    session.add(challenge)
    session.commit()
    session.refresh(challenge)
    return challenge


def test_1_xp_awarded_zero_sends_no_messages(mock_scheduling):
    fake_mgr, scheduled = mock_scheduling
    result = {
        "user_id": 10,
        "challenge_id": 5,
        "xp_awarded": 0,
        "total_xp": 100,
        "level": 2,
        "previous_level": 1,
        "leveled_up": True,
        "xp_to_next_level": 150,
        "badges_unlocked": [{"slug": "fast_learner", "name": "Fast Learner"}],
        "already_completed": True,
    }

    notify_progress(result)

    assert len(scheduled) == 0
    assert len(fake_mgr.calls) == 0


def test_2_level_up_sends_exact_four_field_message(mock_scheduling):
    fake_mgr, scheduled = mock_scheduling
    result = {
        "user_id": 42,
        "challenge_id": 7,
        "xp_awarded": 50,
        "total_xp": 130,
        "level": 2,
        "previous_level": 1,
        "leveled_up": True,
        "xp_to_next_level": 120,
        "badges_unlocked": [],
        "already_completed": False,
    }

    notify_progress(result)

    assert len(scheduled) == 1
    assert scheduled[0][1] == fake_mgr.loop
    assert len(fake_mgr.calls) == 1
    recipient, message = fake_mgr.calls[0]
    assert recipient == 42
    assert message == {
        "type": "level_up",
        "level": 2,
        "previous_level": 1,
        "total_xp": 130,
    }
    assert set(message.keys()) == {"type", "level", "previous_level", "total_xp"}


def test_3_every_unlocked_badge_sends_message_with_correct_structure(mock_scheduling):
    fake_mgr, scheduled = mock_scheduling
    result = {
        "user_id": 42,
        "challenge_id": 7,
        "xp_awarded": 50,
        "total_xp": 50,
        "level": 1,
        "previous_level": 1,
        "leveled_up": False,
        "xp_to_next_level": 50,
        "badges_unlocked": [
            {"slug": "first_steps", "name": "First Steps"},
            {"slug": "bug_hunter", "name": "Bug Hunter"},
        ],
        "already_completed": False,
    }

    notify_progress(result)

    assert len(scheduled) == 2
    assert len(fake_mgr.calls) == 2

    recipient_1, message_1 = fake_mgr.calls[0]
    assert recipient_1 == 42
    assert message_1 == {
        "type": "badge_unlocked",
        "badge": {
            "slug": "first_steps",
            "name": "First Steps",
        },
    }
    assert set(message_1["badge"].keys()) == {"slug", "name"}

    recipient_2, message_2 = fake_mgr.calls[1]
    assert recipient_2 == 42
    assert message_2 == {
        "type": "badge_unlocked",
        "badge": {
            "slug": "bug_hunter",
            "name": "Bug Hunter",
        },
    }
    assert set(message_2["badge"].keys()) == {"slug", "name"}


def test_4_level_up_plus_two_badges_sends_exactly_three_messages(mock_scheduling):
    fake_mgr, scheduled = mock_scheduling
    result = {
        "user_id": 42,
        "challenge_id": 7,
        "xp_awarded": 50,
        "total_xp": 150,
        "level": 2,
        "previous_level": 1,
        "leveled_up": True,
        "xp_to_next_level": 100,
        "badges_unlocked": [
            {"slug": "badge_one", "name": "Badge One"},
            {"slug": "badge_two", "name": "Badge Two"},
        ],
        "already_completed": False,
    }

    notify_progress(result)

    assert len(scheduled) == 3
    assert len(fake_mgr.calls) == 3

    assert fake_mgr.calls[0][1]["type"] == "level_up"
    assert fake_mgr.calls[1][1]["type"] == "badge_unlocked"
    assert fake_mgr.calls[1][1]["badge"]["slug"] == "badge_one"
    assert fake_mgr.calls[2][1]["type"] == "badge_unlocked"
    assert fake_mgr.calls[2][1]["badge"]["slug"] == "badge_two"


def test_5_manager_loop_none_causes_no_send_and_no_exception(monkeypatch):
    fake_mgr = FakeManager()
    fake_mgr.loop = None
    monkeypatch.setattr("realtime.notify.manager", fake_mgr)

    scheduled = []

    def fake_run_coroutine_threadsafe(coro, loop):
        scheduled.append((coro, loop))
        coro.close()

    monkeypatch.setattr(asyncio, "run_coroutine_threadsafe", fake_run_coroutine_threadsafe)

    result = {
        "user_id": 42,
        "challenge_id": 7,
        "xp_awarded": 50,
        "total_xp": 150,
        "level": 2,
        "previous_level": 1,
        "leveled_up": True,
        "xp_to_next_level": 100,
        "badges_unlocked": [{"slug": "badge_one", "name": "Badge One"}],
        "already_completed": False,
    }

    # Must not raise
    notify_progress(result)

    assert len(scheduled) == 0
    assert len(fake_mgr.calls) == 0


def test_6_send_or_scheduling_failure_is_swallowed_and_logged(monkeypatch, caplog):
    fake_mgr = FakeManager()
    monkeypatch.setattr("realtime.notify.manager", fake_mgr)

    def failing_run_coroutine_threadsafe(coro, loop):
        coro.close()
        raise RuntimeError("Event loop crashed unexpectedly")

    monkeypatch.setattr(asyncio, "run_coroutine_threadsafe", failing_run_coroutine_threadsafe)

    result = {
        "user_id": 42,
        "challenge_id": 7,
        "xp_awarded": 50,
        "total_xp": 150,
        "level": 2,
        "previous_level": 1,
        "leveled_up": True,
        "xp_to_next_level": 100,
        "badges_unlocked": [],
        "already_completed": False,
    }

    with caplog.at_level(logging.ERROR):
        # Must not raise to caller
        notify_progress(result)

    assert "Unexpected error while dispatching progress notification" in caplog.text


def test_7_notify_progress_raising_in_helper_still_returns_200_and_all_10_fields(
    client, session: Session, monkeypatch
):
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake_secret_key")
    monkeypatch.setattr("services.progression.engine", session.get_bind())
    monkeypatch.setattr(
        "services.certificates.upload_image",
        lambda data, name: f"https://mock.storage/{name}.png",
    )

    def exploding_notify(result):
        raise RuntimeError("Catastrophic notification error")

    monkeypatch.setattr("routes.challenge.notify_progress", exploding_notify)

    user = _create_user(session, clerk_id="clerk_safe", email="safe@example.com")
    challenge = _seed_hierarchy(session, xp_reward=50)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post("/complete-challenge", json={"challenge_id": challenge.id})
    assert response.status_code == 200

    data = response.json()
    expected_keys = {
        "user_id",
        "challenge_id",
        "xp_awarded",
        "total_xp",
        "level",
        "previous_level",
        "leveled_up",
        "xp_to_next_level",
        "badges_unlocked",
        "already_completed",
    }
    assert set(data.keys()) == expected_keys
    assert data["user_id"] == user.id
    assert data["challenge_id"] == challenge.id
    assert data["xp_awarded"] == 50
    assert data["total_xp"] == 50
    assert data["level"] == 1
    assert data["previous_level"] == 1
    assert data["leveled_up"] is False
    assert data["already_completed"] is False


def test_8_messages_are_sent_to_user_id_in_result_never_another_user(mock_scheduling):
    fake_mgr, scheduled = mock_scheduling
    target_user_id = 777
    other_user_id = 888

    result = {
        "user_id": target_user_id,
        "challenge_id": 1,
        "xp_awarded": 100,
        "total_xp": 200,
        "level": 2,
        "previous_level": 1,
        "leveled_up": True,
        "xp_to_next_level": 50,
        "badges_unlocked": [{"slug": "great_job", "name": "Great Job"}],
        "already_completed": False,
    }

    notify_progress(result)

    assert len(fake_mgr.calls) == 2
    for recipient, msg in fake_mgr.calls:
        assert recipient == target_user_id
        assert recipient != other_user_id
