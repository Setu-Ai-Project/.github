import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from models.challenge import Challenge
from models.completed_challenge import CompletedChallenge
from models.module import Module
from models.sub_module import SubModule
from models.user import User


def _create_seed_data(session: Session):
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

    sub_module = SubModule(
        title="Test SubModule",
        description="SubDesc",
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

    return user_1, user_2, challenge


def test_challenge_and_completion_table_persistence(session: Session):
    user_1, _, challenge = _create_seed_data(session)

    completion = CompletedChallenge(
        user_id=user_1.id,
        challenge_id=challenge.id,
        xp_awarded=50,
    )
    session.add(completion)
    session.commit()
    session.refresh(completion)

    assert completion.id is not None
    assert completion.user_id == user_1.id
    assert completion.challenge_id == challenge.id
    assert completion.xp_awarded == 50
    assert completion.completed_at is not None

    statement = select(CompletedChallenge).where(
        CompletedChallenge.user_id == user_1.id
    )
    records = session.exec(statement).all()
    assert len(records) == 1


def test_duplicate_completion_rejected_by_unique_constraint(session: Session):
    user_1, _, challenge = _create_seed_data(session)

    completion_1 = CompletedChallenge(
        user_id=user_1.id,
        challenge_id=challenge.id,
        xp_awarded=50,
    )
    session.add(completion_1)
    session.commit()

    completion_2 = CompletedChallenge(
        user_id=user_1.id,
        challenge_id=challenge.id,
        xp_awarded=50,
    )
    session.add(completion_2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_different_users_can_complete_same_challenge(session: Session):
    user_1, user_2, challenge = _create_seed_data(session)

    c1 = CompletedChallenge(
        user_id=user_1.id,
        challenge_id=challenge.id,
        xp_awarded=50,
    )
    c2 = CompletedChallenge(
        user_id=user_2.id,
        challenge_id=challenge.id,
        xp_awarded=50,
    )
    session.add(c1)
    session.add(c2)
    session.commit()

    records = session.exec(select(CompletedChallenge)).all()
    assert len(records) == 2


def test_same_user_can_complete_multiple_different_challenges(session: Session):
    user_1, _, challenge_1 = _create_seed_data(session)

    challenge_2 = Challenge(
        sub_module_id=challenge_1.sub_module_id,
        title="Second Challenge",
        xp_reward=100,
    )
    session.add(challenge_2)
    session.commit()
    session.refresh(challenge_2)

    c1 = CompletedChallenge(
        user_id=user_1.id,
        challenge_id=challenge_1.id,
        xp_awarded=50,
    )
    c2 = CompletedChallenge(
        user_id=user_1.id,
        challenge_id=challenge_2.id,
        xp_awarded=100,
    )
    session.add(c1)
    session.add(c2)
    session.commit()

    statement = select(CompletedChallenge).where(
        CompletedChallenge.user_id == user_1.id
    )
    records = session.exec(statement).all()
    assert len(records) == 2


def test_challenge_defaults(session: Session):
    _, _, challenge = _create_seed_data(session)
    assert challenge.xp_reward == 50
    assert challenge.title == "Intro Challenge"
