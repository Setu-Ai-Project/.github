"""Seed initial badges for the SetuAI progression engine.

Idempotent: safe to run repeatedly without creating duplicate badge records.
Uses existing slug uniqueness constraints and get-or-create logic.

Usage (from the backend/ directory):
    python -m scripts.seed_badges
"""

from typing import Optional
from sqlmodel import Session, SQLModel, select

from database import engine
from models.badge import Badge

INITIAL_BADGES = [
    {
        "slug": "first-steps",
        "name": "First Steps",
        "description": "Completed your first challenge",
        "rule_type": "challenges_completed",
        "rule_value": 1,
    },
    {
        "slug": "getting-warm",
        "name": "Getting Warm",
        "description": "Completed 5 challenges",
        "rule_type": "challenges_completed",
        "rule_value": 5,
    },
    {
        "slug": "level-2",
        "name": "Level 2",
        "description": "Reached level 2",
        "rule_type": "level_reached",
        "rule_value": 2,
    },
    {
        "slug": "level-3",
        "name": "Level 3",
        "description": "Reached level 3",
        "rule_type": "level_reached",
        "rule_value": 3,
    },
]


def _execute_seed_badges(session: Session) -> list[Badge]:
    """Seed or update badges in the provided database session."""
    seeded_badges: list[Badge] = []
    for badge_data in INITIAL_BADGES:
        existing = session.exec(
            select(Badge).where(Badge.slug == badge_data["slug"])
        ).first()

        if existing:
            existing.name = badge_data["name"]
            existing.description = badge_data["description"]
            existing.rule_type = badge_data["rule_type"]
            existing.rule_value = badge_data["rule_value"]
            session.add(existing)
            seeded_badges.append(existing)
        else:
            badge = Badge(**badge_data)
            session.add(badge)
            seeded_badges.append(badge)

    session.commit()
    for badge in seeded_badges:
        session.refresh(badge)
    return seeded_badges


def seed_badges(session: Optional[Session] = None) -> list[Badge]:
    """Seed the initial set of badges idempotently.

    If session is provided (e.g. from tests), uses it.
    Otherwise, creates tables if missing, opens a session using engine, and commits.
    """
    if session is not None:
        return _execute_seed_badges(session)

    SQLModel.metadata.create_all(engine)
    with Session(engine) as new_session:
        return _execute_seed_badges(new_session)


if __name__ == "__main__":
    badges = seed_badges()
    print(f"Successfully seeded {len(badges)} badges.")
