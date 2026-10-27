from sqlmodel import Session, select
from database import engine
from models.challenge import Challenge
from models.sub_module import SubModule

SEED_TITLE = "Describe a sunset"
SEED_RULES = {"min_words": 8, "required_keywords": ["mood", "style"]}


def seed_challenge(session: Session) -> Challenge | None:
    existing = session.exec(
        select(Challenge).where(Challenge.title == SEED_TITLE)
    ).first()
    if existing:
        return existing

    sub_module = session.exec(
        select(SubModule).order_by(SubModule.id)
    ).first()
    if not sub_module:
        print("No sub-modules found. Run python -m scripts.seed first.")
        return None

    challenge = Challenge(
        title=SEED_TITLE,
        sub_module_id=sub_module.id,
        xp_reward=10,
        rules=SEED_RULES,
    )
    session.add(challenge)
    session.commit()
    session.refresh(challenge)
    return challenge


if __name__ == "__main__":
    with Session(engine) as session:
        challenge = seed_challenge(session)
        if challenge:
            print(f"Challenge id = {challenge.id}")
