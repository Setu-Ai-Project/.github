from sqlmodel import Session, select

from models.challenge import Challenge
from models.module import Module
from models.sub_module import SubModule
from models.submission import Submission, SubmissionStatus
from models.user import User


def _make_user_and_challenge(session: Session) -> tuple[User, Challenge]:
    user = User(name="A", email="a@example.com", hashed_password="pw")
    session.add(user)
    session.commit()
    session.refresh(user)

    module = Module(title="M", description="d", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)

    sub = SubModule(title="S", description="d", order=1, module_id=module.id)
    session.add(sub)
    session.commit()
    session.refresh(sub)

    challenge = Challenge(sub_module_id=sub.id, title="C", xp_reward=10)
    session.add(challenge)
    session.commit()
    session.refresh(challenge)

    return user, challenge


def test_submission_defaults(session: Session):
    user, challenge = _make_user_and_challenge(session)

    submission = Submission(
        user_id=user.id,
        challenge_id=challenge.id,
        answer_text="hi",
    )
    session.add(submission)
    session.commit()
    session.refresh(submission)

    assert submission.id is not None
    assert submission.status == "pending"
    assert submission.feedback == []
    assert submission.xp_awarded == 0
    assert submission.attempt_number == 1
    assert submission.created_at is not None


def test_submission_feedback_persistence(session: Session):
    user, challenge = _make_user_and_challenge(session)

    submission = Submission(
        user_id=user.id,
        challenge_id=challenge.id,
        answer_text="hi",
        feedback=["a", "b"],
    )
    session.add(submission)
    session.commit()
    sub_id = submission.id

    session.expire_all()
    loaded = session.get(Submission, sub_id)
    assert loaded is not None
    assert loaded.feedback == ["a", "b"]


def test_submission_feedback_update(session: Session):
    user, challenge = _make_user_and_challenge(session)

    sub = Submission(
        user_id=user.id,
        challenge_id=challenge.id,
        answer_text="hi",
        feedback=["a", "b"],
    )
    session.add(sub)
    session.commit()
    sub_id = sub.id

    sub.feedback = ["x"]
    session.add(sub)
    session.commit()

    session.expire_all()
    loaded = session.get(Submission, sub_id)
    assert loaded is not None
    assert loaded.feedback == ["x"]


def test_submission_status_constants():
    assert SubmissionStatus.PENDING == "pending"
    assert SubmissionStatus.PASSED == "passed"
    assert SubmissionStatus.NEEDS_REVISION == "needs_revision"


def test_challenge_rules(session: Session):
    user, challenge = _make_user_and_challenge(session)
    assert challenge.rules == {}

    challenge_with_rules = Challenge(
        sub_module_id=challenge.sub_module_id,
        title="With Rules",
        xp_reward=10,
        rules={"min_words": 8, "required_keywords": ["mood"]},
    )
    session.add(challenge_with_rules)
    session.commit()
    c_id = challenge_with_rules.id

    session.expire_all()
    loaded = session.get(Challenge, c_id)
    assert loaded is not None
    assert loaded.rules == {"min_words": 8, "required_keywords": ["mood"]}


def test_multiple_submissions_same_user_and_challenge(session: Session):
    user, challenge = _make_user_and_challenge(session)

    sub_1 = Submission(
        user_id=user.id,
        challenge_id=challenge.id,
        answer_text="first attempt",
        attempt_number=1,
    )
    sub_2 = Submission(
        user_id=user.id,
        challenge_id=challenge.id,
        answer_text="second attempt",
        attempt_number=2,
    )
    session.add(sub_1)
    session.add(sub_2)
    session.commit()

    submissions = session.exec(
        select(Submission).where(
            Submission.user_id == user.id,
            Submission.challenge_id == challenge.id,
        )
    ).all()
    assert len(submissions) == 2
