"""Tests for POST and GET /submissions endpoints (Step 6 Contract)."""

# pyrefly: ignore[missing-import]
import pytest
# pyrefly: ignore[missing-import]
from sqlmodel import Session, select

from main import app
from middleware.auth import get_current_user
from models.challenge import Challenge
from models.module import Module
from models.sub_module import SubModule
from models.submission import Submission
from models.user import User

RULES = {"min_words": 8, "required_keywords": ["mood", "style"]}
BAD = "a beach"
GOOD = "calm beach at sunset with a warm mood in watercolor style"
PASS_MESSAGE = "Great work! Your answer meets all the requirements."
EMPTY_MESSAGE = "Your answer is empty. Write your answer and try again."


@pytest.fixture(autouse=True)
def setup_test_env(session: Session, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake_secret_key")
    monkeypatch.setattr("services.progression.engine", session.get_bind())
    monkeypatch.setattr(
        "services.certificates.upload_image",
        lambda data, name: f"https://mock.storage/{name}.png",
    )


def _seed_challenge(session: Session, xp_reward: int = 50, rules: dict | None = None) -> Challenge:
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
        rules=rules or {},
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


def test_submission_unsafe_content_blocked(client, session: Session):
    user = _create_user(session, clerk_id="clerk_unsafe_user")
    challenge = _seed_challenge(session)
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = client.post(
            "/submissions",
            json={
                "challenge_id": challenge.id,
                "answer_text": "I will murder everyone with a gun",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "needs_revision"
        assert data["xp_awarded"] == 0
        assert any("safe" in msg.lower() or "friendly" in msg.lower() for msg in data["feedback"])
    finally:
        app.dependency_overrides.clear()



# --- Step 6 ticket (Task 3) cases -------------------------------------------


@pytest.fixture
def as_user(client):
    """Log in as the given user for the rest of the test."""
    def _login(user: User):
        app.dependency_overrides[get_current_user] = lambda: user
    yield _login
    app.dependency_overrides.clear()


def _submit(client, challenge_id: int, text: str):
    return client.post("/submissions", json={"challenge_id": challenge_id, "answer_text": text})


def test_challenge_rules_are_used(client, session: Session, as_user):
    as_user(_create_user(session))
    challenge = _seed_challenge(session, rules=RULES)

    data = _submit(client, challenge.id, BAD).json()

    assert data["status"] == "needs_revision"
    assert any("too short" in f for f in data["feedback"])
    assert "Your answer should mention 'mood'." in data["feedback"]
    assert "Your answer should mention 'style'." in data["feedback"]


def test_fail_then_pass_then_repeat_pass(client, session: Session, as_user):
    user = _create_user(session)
    as_user(user)
    challenge = _seed_challenge(session, xp_reward=10, rules=RULES)

    first = _submit(client, challenge.id, BAD).json()
    second = _submit(client, challenge.id, GOOD).json()
    third = _submit(client, challenge.id, GOOD).json()

    assert (first["status"], first["xp_awarded"], first["attempt_number"]) == ("needs_revision", 0, 1)
    assert (second["status"], second["xp_awarded"], second["attempt_number"]) == ("passed", 10, 2)
    assert second["feedback"] == [PASS_MESSAGE]
    assert (third["status"], third["xp_awarded"], third["attempt_number"]) == ("passed", 0, 3)
    session.refresh(user)
    assert user.total_xp == 10


def test_repeat_pass_does_not_notify_again(client, session: Session, as_user, monkeypatch):
    calls = []
    monkeypatch.setattr("routes.submissions.notify_progress", lambda res: calls.append(res))
    as_user(_create_user(session))
    challenge = _seed_challenge(session, rules=RULES)

    _submit(client, challenge.id, GOOD)
    _submit(client, challenge.id, GOOD)

    assert len(calls) == 1


def test_response_shape_matches_contract(client, session: Session, as_user):
    as_user(_create_user(session))
    challenge = _seed_challenge(session, rules=RULES)

    data = _submit(client, challenge.id, BAD).json()

    assert set(data) == {
        "submission_id", "challenge_id", "status", "feedback",
        "xp_awarded", "attempt_number", "created_at",
    }
    assert isinstance(data["feedback"], list)
    assert data["created_at"].endswith("Z")


def test_unknown_challenge_saves_nothing(client, session: Session, as_user):
    as_user(_create_user(session))

    assert _submit(client, 99999, GOOD).status_code == 404
    assert session.exec(select(Submission)).all() == []


def test_bad_input_returns_422(client, session: Session, as_user):
    as_user(_create_user(session))
    challenge = _seed_challenge(session, rules=RULES)

    assert _submit(client, challenge.id, "").status_code == 422
    assert _submit(client, challenge.id, "x" * 5001).status_code == 422
    assert client.post("/submissions", json={"answer_text": GOOD}).status_code == 422


def test_blank_answer_gets_contract_message(client, session: Session, as_user):
    as_user(_create_user(session))
    challenge = _seed_challenge(session, rules=RULES)

    response = _submit(client, challenge.id, "   ")

    assert response.status_code == 201
    assert response.json()["status"] == "needs_revision"
    assert response.json()["feedback"] == [EMPTY_MESSAGE]


def test_get_endpoints_require_auth(client):
    assert client.get("/submissions").status_code == 401
    assert client.get("/submissions/1").status_code == 401


def test_cannot_read_another_users_submission(client, session: Session, as_user):
    user_a = _create_user(session, clerk_id="clerk_a")
    user_b = _create_user(session, clerk_id="clerk_b")
    challenge = _seed_challenge(session, rules=RULES)
    as_user(user_a)
    submission_id = _submit(client, challenge.id, BAD).json()["submission_id"]

    as_user(user_b)
    response = client.get(f"/submissions/{submission_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Submission not found"}
    assert client.get("/submissions").json() == []

    as_user(user_a)
    response = client.get(f"/submissions/{submission_id}")
    assert response.status_code == 200
    assert response.json()["submission_id"] == submission_id


def test_history_is_newest_first_and_filterable(client, session: Session, as_user):
    as_user(_create_user(session))
    challenge = _seed_challenge(session, rules=RULES)
    for text in (BAD, BAD, GOOD):
        _submit(client, challenge.id, text)

    assert [s["attempt_number"] for s in client.get("/submissions").json()] == [3, 2, 1]
    assert len(client.get(f"/submissions?challenge_id={challenge.id}").json()) == 3
    assert client.get("/submissions?challenge_id=99999").json() == []


def test_attempts_are_counted_per_user(client, session: Session, as_user):
    user_a = _create_user(session, clerk_id="clerk_a")
    user_b = _create_user(session, clerk_id="clerk_b")
    challenge = _seed_challenge(session, rules=RULES)
    as_user(user_a)
    _submit(client, challenge.id, BAD)
    _submit(client, challenge.id, BAD)

    as_user(user_b)
    assert _submit(client, challenge.id, BAD).json()["attempt_number"] == 1


def test_no_xp_on_failed_answer(client, session: Session, as_user):
    user = _create_user(session)
    as_user(user)
    challenge = _seed_challenge(session, rules=RULES)

    _submit(client, challenge.id, BAD)

    session.refresh(user)
    assert user.total_xp == 0


def test_xp_failure_leaves_pending_and_retry_still_awards(client, session: Session, as_user, monkeypatch):
    user = _create_user(session)
    as_user(user)
    challenge = _seed_challenge(session, xp_reward=10, rules=RULES)

    def broken_award_xp(**kwargs):
        raise RuntimeError("database hiccup")

    with monkeypatch.context() as patch:
        patch.setattr("routes.submissions.award_xp", broken_award_xp)
        with pytest.raises(RuntimeError):
            _submit(client, challenge.id, GOOD)

    # In the app, get_session closes the session when the request fails, which rolls
    # back anything not committed. The test shares one session, so roll back here.
    session.rollback()
    rows = session.exec(select(Submission)).all()
    assert [r.status for r in rows] == ["pending"]

    retry = _submit(client, challenge.id, GOOD).json()
    assert retry["status"] == "passed"
    assert retry["xp_awarded"] == 10
    assert retry["attempt_number"] == 2
