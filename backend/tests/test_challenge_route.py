"""Tests for POST /complete-challenge endpoint."""

import pytest
from sqlmodel import Session

from config.progression_rules import xp_to_next_level
from main import app
from middleware.auth import get_current_user
from models.challenge import Challenge
from models.module import Module
from models.sub_module import SubModule
from models.user import User


@pytest.fixture(autouse=True)
def setup_test_env(session: Session, monkeypatch: pytest.MonkeyPatch):
    """Point progression engine to test SQLite DB and prevent external network calls."""
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake_secret_key")
    monkeypatch.setattr("services.progression.engine", session.get_bind())
    monkeypatch.setattr(
        "services.certificates.upload_image",
        lambda data, name: f"https://mock.storage/{name}.png",
    )


def _seed_hierarchy(session: Session, xp_reward: int = 50) -> Challenge:
    module = Module(title="Test Module", description="Test Description", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)

    sub_module = SubModule(
        title="Test SubModule",
        description="Test SubModule Description",
        order=1,
        module_id=module.id,
    )
    session.add(sub_module)
    session.commit()
    session.refresh(sub_module)

    challenge = Challenge(
        sub_module_id=sub_module.id,
        title="Test Challenge",
        xp_reward=xp_reward,
    )
    session.add(challenge)
    session.commit()
    session.refresh(challenge)
    return challenge


def _create_user(
    session: Session,
    *,
    clerk_id: str = "clerk_test_user",
    email: str = "testuser@example.com",
    total_xp: int = 0,
    level: int = 1,
) -> User:
    user = User(
        name="Test Learner",
        email=email,
        hashed_password="fake_hashed_pw",
        clerk_user_id=clerk_id,
        total_xp=total_xp,
        level=level,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_1_no_token_gives_401(client, session: Session):
    challenge = _seed_hierarchy(session)
    response = client.post("/complete-challenge", json={"challenge_id": challenge.id})
    assert response.status_code == 401


def test_2_valid_user_and_existing_challenge_gives_200_with_all_10_fields(client, session: Session):
    user = _create_user(session, clerk_id="clerk_u2", email="u2@example.com", total_xp=0, level=1)
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
    assert data["xp_to_next_level"] == xp_to_next_level(50)
    assert isinstance(data["badges_unlocked"], list)
    assert data["already_completed"] is False


def test_3_repeating_gives_already_completed_true_and_xp_awarded_0(client, session: Session):
    user = _create_user(session, clerk_id="clerk_u3", email="u3@example.com", total_xp=0, level=1)
    challenge = _seed_hierarchy(session, xp_reward=50)

    app.dependency_overrides[get_current_user] = lambda: user

    # First attempt
    first_resp = client.post("/complete-challenge", json={"challenge_id": challenge.id})
    assert first_resp.status_code == 200
    first_data = first_resp.json()
    assert first_data["already_completed"] is False
    assert first_data["xp_awarded"] == 50

    # Second attempt
    second_resp = client.post("/complete-challenge", json={"challenge_id": challenge.id})
    assert second_resp.status_code == 200
    second_data = second_resp.json()
    assert second_data["already_completed"] is True
    assert second_data["xp_awarded"] == 0
    assert second_data["total_xp"] == 50
    assert second_data["level"] == 1
    assert second_data["previous_level"] == 1
    assert second_data["leveled_up"] is False


def test_4_challenge_id_99999_gives_404_with_clear_detail(client, session: Session):
    user = _create_user(session, clerk_id="clerk_u4", email="u4@example.com")
    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post("/complete-challenge", json={"challenge_id": 99999})
    assert response.status_code == 404
    detail = response.json().get("detail", "")
    assert "99999" in detail


def test_5_missing_or_non_integer_challenge_id_gives_422(client, session: Session):
    user = _create_user(session, clerk_id="clerk_u5", email="u5@example.com")
    app.dependency_overrides[get_current_user] = lambda: user

    # Missing challenge_id
    resp_missing = client.post("/complete-challenge", json={})
    assert resp_missing.status_code == 422

    # Non-integer challenge_id (string)
    resp_str = client.post("/complete-challenge", json={"challenge_id": "not-an-integer"})
    assert resp_str.status_code == 422

    # Non-integer challenge_id (null)
    resp_null = client.post("/complete-challenge", json={"challenge_id": None})
    assert resp_null.status_code == 422


def test_6_extra_user_id_in_body_is_ignored_and_auth_user_gets_xp(client, session: Session):
    user_auth = _create_user(session, clerk_id="clerk_auth", email="auth@example.com", total_xp=0, level=1)
    user_other = _create_user(session, clerk_id="clerk_other", email="other@example.com", total_xp=0, level=1)
    challenge = _seed_hierarchy(session, xp_reward=50)

    app.dependency_overrides[get_current_user] = lambda: user_auth

    # Post with user_id targeting user_other
    response = client.post(
        "/complete-challenge",
        json={"challenge_id": challenge.id, "user_id": user_other.id},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == user_auth.id
    assert data["xp_awarded"] == 50
    assert data["total_xp"] == 50

    # Ensure in the database that user_auth received the XP and user_other was untouched
    session.refresh(user_auth)
    session.refresh(user_other)
    assert user_auth.total_xp == 50
    assert user_other.total_xp == 0


def test_7_crossing_level_boundary_returns_leveled_up_true(client, session: Session):
    # Threshold for Level 2 is 100 XP. Starting at 80 + 50 = 130 XP (Level 2).
    user = _create_user(
        session,
        clerk_id="clerk_lvl",
        email="lvl@example.com",
        total_xp=80,
        level=1,
    )
    challenge = _seed_hierarchy(session, xp_reward=50)

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post("/complete-challenge", json={"challenge_id": challenge.id})
    assert response.status_code == 200
    data = response.json()

    assert data["previous_level"] == 1
    assert data["level"] == 2
    assert data["leveled_up"] is True
    assert data["total_xp"] == 130
    assert data["xp_to_next_level"] == 120
