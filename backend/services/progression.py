"""Progression engine service for awarding XP and tracking completions.

This module implements the award_xp contract agreed in docs/contracts/award_xp.md.
"""

import logging
from typing import Any
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from config.progression_rules import level_for_xp, xp_to_next_level
from database import engine
from models.challenge import Challenge
from models.completed_challenge import CompletedChallenge
from models.sub_module import SubModule
from models.user import User
from services.badges import check_and_award_badges
from services.certificates import is_module_completed, issue_certificate

logger = logging.getLogger(__name__)


class UserNotFound(Exception):
    """Raised when the specified user_id does not exist."""


class ChallengeNotFound(Exception):
    """Raised when the specified challenge_id does not exist."""


def _execute_award_xp(session: Session, user_id: int, challenge_id: int) -> dict[str, Any]:
    """Internal helper that performs the award_xp logic within an existing database session."""
    user = session.get(User, user_id)
    if not user:
        raise UserNotFound(f"User with id {user_id} does not exist.")

    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise ChallengeNotFound(f"Challenge with id {challenge_id} does not exist.")

    # 1. Check if already completed
    existing_completion = session.exec(
        select(CompletedChallenge).where(
            CompletedChallenge.user_id == user_id,
            CompletedChallenge.challenge_id == challenge_id,
        )
    ).first()

    if existing_completion:
        return {
            "user_id": user_id,
            "challenge_id": challenge_id,
            "xp_awarded": 0,
            "total_xp": user.total_xp,
            "level": user.level,
            "previous_level": user.level,
            "leveled_up": False,
            "xp_to_next_level": xp_to_next_level(user.total_xp),
            "badges_unlocked": [],
            "already_completed": True,
        }

    # 2. Compute new state
    previous_level = user.level
    xp_to_award = challenge.xp_reward
    new_total_xp = user.total_xp + xp_to_award
    new_level = level_for_xp(new_total_xp)
    leveled_up = new_level > previous_level

    # 3. Create completion record and update user
    completion_record = CompletedChallenge(
        user_id=user_id,
        challenge_id=challenge_id,
        xp_awarded=xp_to_award,
    )
    session.add(completion_record)
    user.total_xp = new_total_xp
    user.level = new_level
    session.add(user)

    # 4. Check and award any newly unlocked badges in the same transaction
    badges_unlocked = check_and_award_badges(session, user)

    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()

        # Check if the conflict was caused by a concurrent duplicate completion for this user and challenge
        duplicate = session.exec(
            select(CompletedChallenge).where(
                CompletedChallenge.user_id == user_id,
                CompletedChallenge.challenge_id == challenge_id,
            )
        ).first()

        if duplicate:
            # Re-fetch fresh user state to return accurate persisted values
            current_user = session.get(User, user_id)
            user_xp = current_user.total_xp if current_user else user.total_xp
            user_lvl = current_user.level if current_user else user.level
            return {
                "user_id": user_id,
                "challenge_id": challenge_id,
                "xp_awarded": 0,
                "total_xp": user_xp,
                "level": user_lvl,
                "previous_level": user_lvl,
                "leveled_up": False,
                "xp_to_next_level": xp_to_next_level(user_xp),
                "badges_unlocked": [],
                "already_completed": True,
            }

        # If it was an unrelated IntegrityError, re-raise it
        raise exc

    session.refresh(user)

    # 5. Check if the module this challenge belongs to is now complete, and issue certificate if so
    module_id = None
    try:
        sub_module = session.get(SubModule, challenge.sub_module_id)
        if sub_module:
            module_id = sub_module.module_id
            if is_module_completed(session, user_id, module_id):
                issue_certificate(session, user, module_id)
    except Exception:
        logger.exception(
            "Certificate issuance failed for user %s on module %s",
            user_id,
            module_id,
        )
        session.rollback()

    return {
        "user_id": user_id,
        "challenge_id": challenge_id,
        "xp_awarded": xp_to_award,
        "total_xp": user.total_xp,
        "level": user.level,
        "previous_level": previous_level,
        "leveled_up": leveled_up,
        "xp_to_next_level": xp_to_next_level(user.total_xp),
        "badges_unlocked": badges_unlocked,
        "already_completed": False,
    }


def award_xp(user_id: int, challenge_id: int) -> dict:
    """Award experience points to a user for completing a challenge.

    Implements the public contract agreed in docs/contracts/award_xp.md.
    Manages its own database session and transaction.
    """
    with Session(engine) as session:
        return _execute_award_xp(session, user_id, challenge_id)
