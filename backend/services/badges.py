"""Badges service for evaluating unlock rules and awarding user badges.

This module supports rule evaluation for learner badges:
- 'challenges_completed': Unlocked when completed challenges >= rule_value.
- 'level_reached': Unlocked when user.level >= rule_value.

All badge awards are staged directly in the caller's database session without
committing or independently managing the transaction boundaries.
"""

from typing import Any
from sqlmodel import Session, func, select

from models.badge import Badge
from models.completed_challenge import CompletedChallenge
from models.user import User
from models.user_badge import UserBadge


def check_and_award_badges(session: Session, user: User) -> list[dict[str, str]]:
    """Evaluate badge rules for a user and stage any newly earned badges.

    Args:
        session: Active SQLModel/SQLAlchemy session. No commits are performed.
        user: The User instance whose stats and achievements are being checked.

    Returns:
        A list of dictionaries for badges newly unlocked in this call.
        Each entry contains 'slug' and 'name'.
    """
    # 1. Fetch already awarded badge IDs for this user to guarantee duplicate prevention
    existing_badge_ids = set(
        session.exec(
            select(UserBadge.badge_id).where(UserBadge.user_id == user.id)
        ).all()
    )

    # Also check uncommitted UserBadge objects staged in the current session
    for staged_obj in session.new:
        if isinstance(staged_obj, UserBadge) and staged_obj.user_id == user.id:
            existing_badge_ids.add(staged_obj.badge_id)

    # 2. Compute user stats relevant to rule types
    # Counting CompletedChallenge for the user (autoflush will include any staged records)
    completed_challenges_count: int = session.exec(
        select(func.count(CompletedChallenge.id)).where(
            CompletedChallenge.user_id == user.id
        )
    ).one()

    # 3. Retrieve all defined badges
    all_badges = session.exec(select(Badge).order_by(Badge.id)).all()

    newly_unlocked: list[dict[str, str]] = []

    # 4. Evaluate each badge rule
    for badge in all_badges:
        if badge.id in existing_badge_ids:
            continue

        qualifies = False
        if badge.rule_type == "challenges_completed":
            if completed_challenges_count >= badge.rule_value:
                qualifies = True
        elif badge.rule_type == "level_reached":
            if user.level >= badge.rule_value:
                qualifies = True

        if qualifies:
            user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
            session.add(user_badge)
            existing_badge_ids.add(badge.id)
            newly_unlocked.append({
                "slug": badge.slug,
                "name": badge.name,
            })

    return newly_unlocked
