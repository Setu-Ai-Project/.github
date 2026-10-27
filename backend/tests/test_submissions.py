"""Tests for POST and GET /submissions endpoints (Step 6 Contract)."""

import pytest
from sqlmodel import Session

from main import app
from middleware.auth import get_current_user
from models.challenge import Challenge
from models.module import Module
from models.sub_module import SubModule
from models.user import User


@pytest.fixture(autouse=True)
def setup_test_env(session: Session, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake_secret_key")
    monkeypatch.setattr("services.progression.engine", session.get_bind())
    monkeypatch.setattr(
        "services.certificates.upload_image",
        lambda data, name: f"https://mock.storage/{name}.png",
    )


def _seed_challenge(session: Session, xp_reward: int = 50) -> Challenge:
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


def _create_user(session: Session, clerk_id: str = "clerk_sub_user") -> User:
    user = User(
        name="Submission Learner",
        email=f"{clerk_id}@example.com",
        hashed_password="fake_hashed_pw",
        clerk_user_id=clerk_id,
        total_xp=0,
        level=1,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_submissions_requires_auth(client):
    response = client.post("/submissions", json={"challenge_id": 1, "answer_text": "hello world"})
    assert response.status_code == 401


def test_submissions_404_missing_challenge(client, session: Session):
    user = _create_user(session)
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = client.post(
            "/submissions",
            json={"challenge_id": 99999, "answer_text": "This is a valid long answer."},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Challenge not found"
    finally:
        app.dependency_overrides.clear()


def test_submission_needs_revision(client, session: Session):
    user = _create_user(session, clerk_id="clerk_rev_user")
    challenge = _seed_challenge(session)
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = client.post(
            "/submissions",
            json={"challenge_id": challenge.id, "answer_text": "short"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "needs_revision"
        assert data["xp_awarded"] == 0
        assert data["attempt_number"] == 1
        assert len(data["feedback"]) > 0
    finally:
        app.dependency_overrides.clear()


def test_submission_passes_and_awards_xp(client, session: Session):
    user = _create_user(session, clerk_id="clerk_pass_user")
    challenge = _seed_challenge(session, xp_reward=60)
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = client.post(
            "/submissions",
            json={
                "challenge_id": challenge.id,
                "answer_text": "Here is a complete and thoughtful response to the challenge question.",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "passed"
        assert data["xp_awarded"] == 60
        assert data["attempt_number"] == 1

        # Check list endpoint
        list_res = client.get("/submissions")
        assert list_res.status_code == 200
        submissions = list_res.json()
        assert len(submissions) >= 1
        assert submissions[0]["submission_id"] == data["submission_id"]
    finally:
        app.dependency_overrides.clear()
