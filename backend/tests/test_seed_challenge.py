from sqlmodel import Session, select

from models.challenge import Challenge
from models.module import Module
from models.sub_module import SubModule
from scripts.seed_challenge import seed_challenge


def test_seed_challenge_empty_db(session: Session):
    result = seed_challenge(session)
    assert result is None
    assert session.exec(select(Challenge)).all() == []


def test_seed_challenge_with_sub_module(session: Session):
    module = Module(title="M", description="d", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)

    sub = SubModule(title="S", description="d", order=1, module_id=module.id)
    session.add(sub)
    session.commit()
    session.refresh(sub)

    challenge = seed_challenge(session)
    assert challenge is not None
    assert challenge.title == "Describe a sunset"
    assert challenge.xp_reward == 10
    assert challenge.rules == {"min_words": 8, "required_keywords": ["mood", "style"]}
    assert challenge.sub_module_id == sub.id


def test_seed_challenge_called_twice(session: Session):
    module = Module(title="M", description="d", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)

    sub = SubModule(title="S", description="d", order=1, module_id=module.id)
    session.add(sub)
    session.commit()
    session.refresh(sub)

    challenge_1 = seed_challenge(session)
    challenge_2 = seed_challenge(session)
    assert challenge_1 is not None
    assert challenge_2 is not None
    assert challenge_1.id == challenge_2.id

    challenges = session.exec(
        select(Challenge).where(Challenge.title == "Describe a sunset")
    ).all()
    assert len(challenges) == 1
