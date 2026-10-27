import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from models.challenge import Challenge
from models.completed_challenge import CompletedChallenge
from models.module import Module
from models.sub_module import SubModule
from models.user import User
from services.progression import (
    ChallengeNotFound,
    UserNotFound,
    _execute_award_xp,
    award_xp,
)


def _seed_test_data(session: Session):
    user = User(
        name="Learner One",
        email="learner.one@example.com",
        hashed_password="hash",
        total_xp=0,
        level=1,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    module = Module(title="Module 1", description="Intro", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)

    sub_module = SubModule(
        title="SubModule 1",
        description="SubIntro",
        order=1,
        module_id=module.id,
    )
    session.add(sub_module)
    session.commit()
    session.refresh(sub_module)

    challenge = Challenge(
        sub_module_id=sub_module.id,
        title="Intro Challenge",
        xp_reward=50,
    )
    session.add(challenge)
    session.commit()
    session.refresh(challenge)

    return user, challenge


def test_award_xp_first_completion(session: Session):
    user, challenge = _seed_test_data(session)

    result = _execute_award_xp(session, user.id, challenge.id)

    assert result["user_id"] == user.id
    assert result["challenge_id"] == challenge.id
    assert result["xp_awarded"] == 50
    assert result["total_xp"] == 50
    assert result["level"] == 1
    assert result["previous_level"] == 1
    assert result["leveled_up"] is False
    assert result["xp_to_next_level"] == 50
    assert result["badges_unlocked"] == []
    assert result["already_completed"] is False

    # Verify persisted in database
    db_user = session.get(User, user.id)
    assert db_user.total_xp == 50
    assert db_user.level == 1

    records = session.exec(
        select(CompletedChallenge).where(
            CompletedChallenge.user_id == user.id,
            CompletedChallenge.challenge_id == challenge.id,
        )
    ).all()
    assert len(records) == 1
    assert records[0].xp_awarded == 50


def test_award_xp_repeat_completion_idempotent(session: Session):
    user, challenge = _seed_test_data(session)

    # First completion
    first_result = _execute_award_xp(session, user.id, challenge.id)
    assert first_result["already_completed"] is False
    assert first_result["xp_awarded"] == 50

    # Repeat submission
    second_result = _execute_award_xp(session, user.id, challenge.id)
    assert second_result["already_completed"] is True
    assert second_result["xp_awarded"] == 0
    assert second_result["total_xp"] == 50
    assert second_result["level"] == 1
    assert second_result["previous_level"] == 1
    assert second_result["leveled_up"] is False
    assert second_result["xp_to_next_level"] == 50
    assert second_result["badges_unlocked"] == []

    # Verify no extra completion was inserted and XP wasn't doubled
    records = session.exec(select(CompletedChallenge)).all()
    assert len(records) == 1
    db_user = session.get(User, user.id)
    assert db_user.total_xp == 50


def test_award_xp_level_up(session: Session):
    user, challenge = _seed_test_data(session)

    # Put user at 80 XP (Level 1)
    user.total_xp = 80
    user.level = 1
    session.add(user)
    session.commit()

    # Completing challenge (50 XP) brings total_xp to 130 -> Level 2 threshold is 100
    result = _execute_award_xp(session, user.id, challenge.id)

    assert result["xp_awarded"] == 50
    assert result["total_xp"] == 130
    assert result["level"] == 2
    assert result["previous_level"] == 1
    assert result["leveled_up"] is True
    # Next level 3 is at 250 XP -> 250 - 130 = 120 remaining
    assert result["xp_to_next_level"] == 120
    assert result["already_completed"] is False

    db_user = session.get(User, user.id)
    assert db_user.level == 2
    assert db_user.total_xp == 130


def test_award_xp_user_not_found(session: Session):
    _, challenge = _seed_test_data(session)

    with pytest.raises(UserNotFound):
        _execute_award_xp(session, 99999, challenge.id)


def test_award_xp_challenge_not_found(session: Session):
    user, _ = _seed_test_data(session)

    with pytest.raises(ChallengeNotFound):
        _execute_award_xp(session, user.id, 99999)


def test_award_xp_duplicate_integrity_error_handling(session: Session):
    user, challenge = _seed_test_data(session)

    # Pre-insert a completion directly into database (simulating another concurrent worker committing first)
    concurrent_completion = CompletedChallenge(
        user_id=user.id,
        challenge_id=challenge.id,
        xp_awarded=50,
    )
    session.add(concurrent_completion)
    user.total_xp = 50
    session.add(user)
    session.commit()

    # When the service runs, even if a duplicate collision triggers IntegrityError during commit,
    # it rolls back and returns an idempotent response
    result = _execute_award_xp(session, user.id, challenge.id)
    assert result["already_completed"] is True
    assert result["xp_awarded"] == 0
    assert result["total_xp"] == 50


def test_award_xp_unrelated_integrity_error_reraised(monkeypatch, session: Session):
    user, challenge = _seed_test_data(session)

    # Monkeypatch session.commit to simulate an unrelated IntegrityError
    def mock_commit():
        raise IntegrityError("mock error", params=None, orig=Exception("Unrelated DB error"))

    monkeypatch.setattr(session, "commit", mock_commit)

    with pytest.raises(IntegrityError):
        _execute_award_xp(session, user.id, challenge.id)


def test_public_award_xp_function_signature_and_contract(monkeypatch, session: Session):
    # Verify the public award_xp(user_id, challenge_id) function signature and engine interaction
    user, challenge = _seed_test_data(session)

    # Route public award_xp to use the test session's engine
    import services.progression as progression_module
    from database import engine

    monkeypatch.setattr(progression_module, "engine", session.get_bind())

    result = award_xp(user.id, challenge.id)

    # Validate exact key structure according to docs/contracts/award_xp.md
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
    assert set(result.keys()) == expected_keys
    assert result["already_completed"] is False
    assert result["xp_awarded"] == 50
    assert result["total_xp"] == 50
