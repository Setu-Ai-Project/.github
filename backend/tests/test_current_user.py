from sqlmodel import Session, select

from middleware.auth import get_current_user
from models.user import User, UserRead


def _user_count(session: Session) -> int:
    return len(session.exec(select(User)).all())


def test_unknown_clerk_id_creates_user(session: Session):
    user = get_current_user(clerk_user_id="user_new", session=session)

    assert isinstance(user.id, int)
    assert user.clerk_user_id == "user_new"
    assert _user_count(session) == 1


def test_same_clerk_id_returns_same_user(session: Session):
    first = get_current_user(clerk_user_id="user_new", session=session)
    second = get_current_user(clerk_user_id="user_new", session=session)

    assert first.id == second.id
    assert _user_count(session) == 1


def test_existing_linked_user_is_returned(session: Session):
    existing = User(
        name="Old",
        email="old@example.com",
        hashed_password="pw",
        clerk_user_id="user_old",
    )
    session.add(existing)
    session.commit()
    session.refresh(existing)

    user = get_current_user(clerk_user_id="user_old", session=session)

    assert user.id == existing.id
    assert user.name == "Old"
    assert _user_count(session) == 1


def test_different_clerk_ids_create_different_users(session: Session):
    user_a = get_current_user(clerk_user_id="user_a", session=session)
    user_b = get_current_user(clerk_user_id="user_b", session=session)

    assert user_a.id != user_b.id
    assert _user_count(session) == 2


def test_created_user_has_valid_email(session: Session):
    user = get_current_user(clerk_user_id="user_new", session=session)

    # Would raise if the placeholder email were rejected (e.g. a ".local" domain).
    UserRead.model_validate(user)
