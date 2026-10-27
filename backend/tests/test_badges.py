"""Tests for Step 5.6: Badge evaluation, unlocks, and badge seeding."""

import pytest
from sqlmodel import Session, select

from models.badge import Badge
from models.challenge import Challenge
from models.completed_challenge import CompletedChallenge
from models.module import Module
from models.sub_module import SubModule
from models.user import User
from models.user_badge import UserBadge
from scripts.seed_badges import seed_badges
from services.badges import check_and_award_badges
from services.progression import _execute_award_xp, award_xp


def _create_user_and_challenge(session: Session, xp_reward: int = 50):
    user = User(
        name="Badge Learner",
        email="badge.learner@example.com",
        hashed_password="hashed_pw",
        total_xp=0,
        level=1,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    module = Module(title="Module Badges", description="Testing", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)

    sub_module = SubModule(
        title="SubModule Badges",
        description="Testing",
        order=1,
        module_id=module.id,
    )
    session.add(sub_module)
    session.commit()
    session.refresh(sub_module)

    challenge = Challenge(
        sub_module_id=sub_module.id,
        title="Badge Challenge",
        xp_reward=xp_reward,
    )
    session.add(challenge)
    session.commit()
    session.refresh(challenge)

    return user, challenge


def test_first_challenge_unlocks_first_steps(session: Session):
    """1. Completing the first challenge unlocks first-steps and includes slug and name."""
    seed_badges(session)
    user, challenge = _create_user_and_challenge(session, xp_reward=50)

    result = _execute_award_xp(session, user.id, challenge.id)

    assert result["already_completed"] is False
    assert result["xp_awarded"] == 50
    assert result["level"] == 1
    # Check badges_unlocked contains first-steps
    assert result["badges_unlocked"] == [
        {"slug": "first-steps", "name": "First Steps"}
    ]

    # Verify persisted in user_badges table
    first_steps_badge = session.exec(
        select(Badge).where(Badge.slug == "first-steps")
    ).one()
    user_badges = session.exec(
        select(UserBadge).where(
            UserBadge.user_id == user.id,
            UserBadge.badge_id == first_steps_badge.id,
        )
    ).all()
    assert len(user_badges) == 1
    assert user_badges[0].awarded_at is not None


def test_repeated_processing_does_not_award_duplicate_badges(session: Session):
    """2. Repeated processing does not award the same badge twice or duplicate its DB record."""
    seed_badges(session)
    user, challenge1 = _create_user_and_challenge(session, xp_reward=50)

    # First completion awards first-steps
    first_result = _execute_award_xp(session, user.id, challenge1.id)
    assert first_result["badges_unlocked"] == [
        {"slug": "first-steps", "name": "First Steps"}
    ]

    # Repeat submission for the exact same challenge
    second_result = _execute_award_xp(session, user.id, challenge1.id)
    assert second_result["already_completed"] is True
    assert second_result["xp_awarded"] == 0
    assert second_result["badges_unlocked"] == []

    # Completing a second different challenge
    sub_module = session.exec(select(SubModule)).first()
    challenge2 = Challenge(
        sub_module_id=sub_module.id,
        title="Second Challenge",
        xp_reward=30,  # Total XP becomes 80 (still level 1)
    )
    session.add(challenge2)
    session.commit()
    session.refresh(challenge2)

    third_result = _execute_award_xp(session, user.id, challenge2.id)
    assert third_result["already_completed"] is False
    assert third_result["xp_awarded"] == 30
    assert third_result["total_xp"] == 80
    assert third_result["level"] == 1
    # first-steps is NOT awarded again
    assert third_result["badges_unlocked"] == []

    # Database has strictly one user_badge record for first-steps
    first_steps_badge = session.exec(
        select(Badge).where(Badge.slug == "first-steps")
    ).one()
    records = session.exec(
        select(UserBadge).where(
            UserBadge.user_id == user.id,
            UserBadge.badge_id == first_steps_badge.id,
        )
    ).all()
    assert len(records) == 1


def test_reaching_level_2_unlocks_level_2_badge(session: Session):
    """3. Reaching level 2 unlocks level-2."""
    seed_badges(session)
    user, challenge1 = _create_user_and_challenge(session, xp_reward=50)

    # Complete challenge 1 (50 XP, level 1)
    _execute_award_xp(session, user.id, challenge1.id)

    # Challenge 2 gives 60 XP -> total 110 XP (threshold for Level 2 is 100)
    sub_module = session.exec(select(SubModule)).first()
    challenge2 = Challenge(
        sub_module_id=sub_module.id,
        title="Level Up Challenge",
        xp_reward=60,
    )
    session.add(challenge2)
    session.commit()
    session.refresh(challenge2)

    result = _execute_award_xp(session, user.id, challenge2.id)
    assert result["level"] == 2
    assert result["leveled_up"] is True
    assert result["badges_unlocked"] == [
        {"slug": "level-2", "name": "Level 2"}
    ]

    # Verify level-2 UserBadge record in database
    lvl2_badge = session.exec(select(Badge).where(Badge.slug == "level-2")).one()
    user_badges = session.exec(
        select(UserBadge).where(
            UserBadge.user_id == user.id,
            UserBadge.badge_id == lvl2_badge.id,
        )
    ).all()
    assert len(user_badges) == 1


def test_unlocking_multiple_badges_simultaneously(session: Session):
    """Test unlocking both first-steps and level-2 on the very first challenge."""
    seed_badges(session)
    # Challenge awards 120 XP -> immediately reaches level 2 on first challenge
    user, challenge = _create_user_and_challenge(session, xp_reward=120)

    result = _execute_award_xp(session, user.id, challenge.id)

    assert result["level"] == 2
    assert result["leveled_up"] is True
    assert result["badges_unlocked"] == [
        {"slug": "first-steps", "name": "First Steps"},
        {"slug": "level-2", "name": "Level 2"},
    ]


def test_existing_xp_behavior_and_response_fields_preserved(session: Session):
    """4. Existing XP behavior and response fields remain unchanged."""
    seed_badges(session)
    user, challenge = _create_user_and_challenge(session, xp_reward=50)

    result = _execute_award_xp(session, user.id, challenge.id)

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
    assert result["user_id"] == user.id
    assert result["challenge_id"] == challenge.id
    assert result["xp_awarded"] == 50
    assert result["total_xp"] == 50
    assert result["level"] == 1
    assert result["previous_level"] == 1
    assert result["leveled_up"] is False
    assert result["xp_to_next_level"] == 50
    assert result["already_completed"] is False


def test_seed_badges_idempotency(session: Session):
    """5. The seed script can be run repeatedly without creating duplicate badge records."""
    # Run 1
    badges_run1 = seed_badges(session)
    assert len(badges_run1) == 4
    slugs_run1 = [b.slug for b in badges_run1]
    assert "first-steps" in slugs_run1
    assert "getting-warm" in slugs_run1
    assert "level-2" in slugs_run1

    # Run 2
    badges_run2 = seed_badges(session)
    assert len(badges_run2) == 4

    # Run 3
    badges_run3 = seed_badges(session)
    assert len(badges_run3) == 4

    # Verify database total badge count is strictly 4
    all_db_badges = session.exec(select(Badge)).all()
    assert len(all_db_badges) == 4
    assert len(set(b.slug for b in all_db_badges)) == 4


def test_completing_five_challenges_unlocks_getting_warm(session: Session):
    """Completing 5 challenges unlocks getting-warm with name Getting Warm."""
    seed_badges(session)
    user, first_challenge = _create_user_and_challenge(session, xp_reward=10)
    _execute_award_xp(session, user.id, first_challenge.id)

    sub_module = session.exec(select(SubModule)).first()

    # Complete challenges 2 through 4
    for i in range(2, 5):
        ch = Challenge(
            sub_module_id=sub_module.id,
            title=f"Challenge {i}",
            xp_reward=10,
        )
        session.add(ch)
        session.commit()
        session.refresh(ch)
        res = _execute_award_xp(session, user.id, ch.id)
        # getting-warm should not be unlocked yet
        assert not any(b["slug"] == "getting-warm" for b in res["badges_unlocked"])

    # 5th challenge completes 5 challenges
    ch5 = Challenge(
        sub_module_id=sub_module.id,
        title="Challenge 5",
        xp_reward=10,
    )
    session.add(ch5)
    session.commit()
    session.refresh(ch5)

    res5 = _execute_award_xp(session, user.id, ch5.id)
    assert any(
        b["slug"] == "getting-warm" and b["name"] == "Getting Warm"
        for b in res5["badges_unlocked"]
    )

    # Verify in DB
    gw_badge = session.exec(select(Badge).where(Badge.slug == "getting-warm")).one()
    records = session.exec(
        select(UserBadge).where(
            UserBadge.user_id == user.id,
            UserBadge.badge_id == gw_badge.id,
        )
    ).all()
    assert len(records) == 1


def test_check_and_award_badges_does_not_commit(session: Session):
    """Verify check_and_award_badges stages UserBadge objects without committing."""
    seed_badges(session)
    user, challenge = _create_user_and_challenge(session, xp_reward=50)

    # Stage a completed challenge without committing
    completion = CompletedChallenge(
        user_id=user.id,
        challenge_id=challenge.id,
        xp_awarded=50,
    )
    session.add(completion)

    # Call badge evaluation
    newly_unlocked = check_and_award_badges(session, user)
    assert len(newly_unlocked) == 1
    assert newly_unlocked[0]["slug"] == "first-steps"

    # Roll back transaction - since check_and_award_badges did not commit, everything is rolled back
    session.rollback()

    db_user_badges = session.exec(
        select(UserBadge).where(UserBadge.user_id == user.id)
    ).all()
    assert len(db_user_badges) == 0
