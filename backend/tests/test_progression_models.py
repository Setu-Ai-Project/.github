from datetime import datetime, timezone
import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from models.badge import Badge
from models.certificate import Certificate
from models.module import Module
from models.user import User
from models.user_badge import UserBadge


def _create_base_user_and_module(session: Session):
    user_1 = User(name="User 1", email="u1@example.com", hashed_password="pw")
    user_2 = User(name="User 2", email="u2@example.com", hashed_password="pw")
    session.add(user_1)
    session.add(user_2)
    session.commit()
    session.refresh(user_1)
    session.refresh(user_2)

    module = Module(title="Test Module", description="Desc", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)

    return user_1, user_2, module


def test_badge_creation_and_uniqueness(session: Session):
    badge_1 = Badge(
        slug="first-steps",
        name="First Steps",
        description="Completed your first challenge",
        rule_type="challenges_completed",
        rule_value=1,
    )
    session.add(badge_1)
    session.commit()
    session.refresh(badge_1)

    assert badge_1.id is not None
    assert badge_1.slug == "first-steps"
    assert badge_1.rule_type == "challenges_completed"
    assert badge_1.rule_value == 1

    # Duplicate slug should be rejected
    badge_duplicate = Badge(
        slug="first-steps",
        name="Duplicate First Steps",
        description="Duplicate",
        rule_type="challenges_completed",
        rule_value=1,
    )
    session.add(badge_duplicate)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_user_badge_persistence_and_uniqueness(session: Session):
    user_1, user_2, _ = _create_base_user_and_module(session)

    badge = Badge(
        slug="speed-demon",
        name="Speed Demon",
        rule_type="xp_threshold",
        rule_value=500,
    )
    session.add(badge)
    session.commit()
    session.refresh(badge)

    user_badge = UserBadge(user_id=user_1.id, badge_id=badge.id)
    session.add(user_badge)
    session.commit()
    session.refresh(user_badge)

    assert user_badge.id is not None
    assert user_badge.user_id == user_1.id
    assert user_badge.badge_id == badge.id
    assert user_badge.awarded_at is not None

    # Duplicate user_badge for same user and badge should be rejected
    duplicate_user_badge = UserBadge(user_id=user_1.id, badge_id=badge.id)
    session.add(duplicate_user_badge)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Another user can receive the same badge
    other_user_badge = UserBadge(user_id=user_2.id, badge_id=badge.id)
    session.add(other_user_badge)
    session.commit()
    session.refresh(other_user_badge)
    assert other_user_badge.id is not None


def test_certificate_persistence_and_uniqueness(session: Session):
    user_1, user_2, module = _create_base_user_and_module(session)

    cert = Certificate(
        user_id=user_1.id,
        module_id=module.id,
        image_url="https://example.com/certs/cert_1.png",
    )
    session.add(cert)
    session.commit()
    session.refresh(cert)

    assert cert.id is not None
    assert cert.user_id == user_1.id
    assert cert.module_id == module.id
    assert cert.image_url == "https://example.com/certs/cert_1.png"
    assert cert.issued_at is not None

    # Duplicate certificate for same user and module should be rejected
    dup_cert = Certificate(
        user_id=user_1.id,
        module_id=module.id,
        image_url="https://example.com/certs/cert_dup.png",
    )
    session.add(dup_cert)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Different user can receive certificate for the module
    user_2_cert = Certificate(
        user_id=user_2.id,
        module_id=module.id,
        image_url="https://example.com/certs/cert_2.png",
    )
    session.add(user_2_cert)
    session.commit()
    session.refresh(user_2_cert)
    assert user_2_cert.id is not None
