"""Seed the database with realistic curriculum content for local development.

DESTRUCTIVE: clears and reinserts all rows in modules, sub_modules,
bug_triggers, spark_terms, byte_facts, and progress (for ALL users) on
every run. Only the demo user is preserved (get-or-create by email).
Never run this against a shared or production database.

Usage (from the backend/ directory):
    python -m scripts.seed
"""

from datetime import datetime, timezone

from sqlalchemy import text
from sqlmodel import Session, SQLModel, select

from database import engine
from security import get_password_hash
from models.user import User
from models.module import Module
from models.sub_module import SubModule
from models.progress import Progress
from models.bug_trigger import BugTrigger
from models.spark_term import SparkTerm
from models.byte_fact import ByteFact

DEMO_USER_EMAIL = "demo.learner@setuai.dev"
DEMO_USER_NAME = "Demo Learner"
DEMO_USER_PASSWORD = "ChangeMe123!"

MODULES = [
    {
        "module": {
            "title": "What Is AI?",
            "description": (
                "An introduction to what counts as AI, what doesn't, and how "
                "to spot the difference."
            ),
            "order": 1,
        },
        "sub_modules": [
            {
                "title": "Swipe-Sort: AI or Not AI?",
                "description": (
                    "Sort real-world examples into AI, Not AI, and AGI hype "
                    "myth across 10-15 rounds."
                ),
                "order": 1,
            },
            {
                "title": "AI History Timeline",
                "description": (
                    "Drag key AI history events into the correct order, with "
                    "a Byte fact after each correct answer."
                ),
                "order": 2,
            },
            {
                "title": "Case Study: DeepMind & the NHS",
                "description": (
                    "A branching case study where you make decisions about "
                    "an AI eye-scan triage trial and see what really "
                    "happened."
                ),
                "order": 3,
            },
            {
                "title": "Biased Dataset Sandbox",
                "description": (
                    "Build a biased dataset and see how the AI's output "
                    "changes as a result."
                ),
                "order": 4,
            },
        ],
        "byte_facts": [
            {
                "fact": (
                    "The term 'Artificial Intelligence' was coined at the "
                    "1956 Dartmouth Conference, where researchers first "
                    "proposed that machines could be made to simulate human "
                    "learning."
                )
            },
            {
                "fact": (
                    "DeepMind's AI model for detecting eye disease from "
                    "retinal scans matched expert ophthalmologists in a "
                    "landmark NHS trial."
                )
            },
        ],
        "spark_terms": [
            {
                "term": "Algorithm",
                "definition": (
                    "A step-by-step set of instructions a computer follows "
                    "to complete a task or solve a problem."
                ),
            },
            {
                "term": "Machine Learning",
                "definition": (
                    "A type of AI where a system improves at a task by "
                    "learning patterns from data instead of being "
                    "explicitly programmed."
                ),
            },
        ],
        "bug_triggers": [
            {
                "trigger_phrase": "AI is always right",
                "warning_message": (
                    "Bug says: AI can sound confident and still be "
                    "completely wrong. Always double-check important "
                    "answers."
                ),
            },
            {
                "trigger_phrase": "AI has no bias",
                "warning_message": (
                    "Bug says: AI systems can inherit bias from the data "
                    "they were trained on, even when nobody intended it."
                ),
            },
        ],
    },
    {
        "module": {
            "title": "Prompt Engineering",
            "description": (
                "Learn how the way you ask an AI something changes the "
                "answer you get back."
            ),
            "order": 2,
        },
        "sub_modules": [
            {
                "title": "Hallucination Hunt",
                "description": (
                    "Review 5 AI answers, a mix of real and fake, and flag "
                    "which ones are made up."
                ),
                "order": 1,
            },
            {
                "title": "Prompt Lab",
                "description": (
                    "Tweak a prompt in a sandbox chatbot to hit a goal, "
                    "like getting it to write a haiku in 3 tries."
                ),
                "order": 2,
            },
            {
                "title": "Case Study: Mata v. Avianca",
                "description": (
                    "A branching courtroom-style case study based on a "
                    "real lawsuit where a lawyer cited fake AI-generated "
                    "cases."
                ),
                "order": 3,
            },
        ],
        "byte_facts": [
            {
                "fact": (
                    "Studies have shown that small changes in how a prompt "
                    "is worded, like asking an AI to 'think step by step', "
                    "can significantly change the accuracy of its answer."
                )
            },
        ],
        "spark_terms": [
            {
                "term": "Hallucination",
                "definition": (
                    "When an AI generates information that sounds "
                    "plausible but is factually incorrect or entirely made "
                    "up."
                ),
            },
            {
                "term": "Prompt",
                "definition": (
                    "The instruction or question you give an AI system to "
                    "get a particular kind of response."
                ),
            },
        ],
        "bug_triggers": [
            {
                "trigger_phrase": "citing AI-generated case law without checking it",
                "warning_message": (
                    "Bug says: in the real case Mata v. Avianca, a lawyer "
                    "submitted a legal brief with fake, AI-generated case "
                    "citations and was sanctioned by the court. Always "
                    "verify anything an AI tells you before you rely on it."
                ),
            },
        ],
    },
    {
        "module": {
            "title": "AI Entrepreneurship",
            "description": (
                "Build a simple AI-powered business idea, from a chatbot "
                "prototype to a pitch."
            ),
            "order": 6,
        },
        "sub_modules": [
            {
                "title": "Build Your MVP Chatbot",
                "description": (
                    "Build a simplified minimum viable product chatbot to "
                    "test your business idea."
                ),
                "order": 1,
            },
            {
                "title": "Lean Canvas Workshop",
                "description": (
                    "Fill in a 12-box Lean Canvas business plan by tapping "
                    "instead of writing."
                ),
                "order": 2,
            },
            {
                "title": "Record Your Pitch",
                "description": (
                    "Record an optional audio or video pitch and get peer "
                    "feedback."
                ),
                "order": 3,
            },
        ],
        "byte_facts": [],
        "spark_terms": [
            {
                "term": "MVP (Minimum Viable Product)",
                "definition": (
                    "The simplest version of a product that still lets you "
                    "test whether your idea works with real users."
                ),
            },
            {
                "term": "Lean Canvas",
                "definition": (
                    "A one-page business plan template that maps out a "
                    "problem, solution, and business model at a glance."
                ),
            },
        ],
        "bug_triggers": [],
    },
]


def clear_curriculum_tables(session: Session) -> None:
    """Truncate all curriculum tables and reset their id sequences. Never touches users."""
    session.execute(
        text(
            "TRUNCATE TABLE progress, bug_triggers, spark_terms, byte_facts, "
            "sub_modules, modules RESTART IDENTITY CASCADE"
        )
    )
    session.commit()


def get_or_create_demo_user(session: Session) -> User:
    """Return the demo user, creating it once so its id stays stable across reseeds."""
    existing = session.exec(
        select(User).where(User.email == DEMO_USER_EMAIL)
    ).first()
    if existing:
        return existing

    user = User(
        name=DEMO_USER_NAME,
        email=DEMO_USER_EMAIL,
        hashed_password=get_password_hash(DEMO_USER_PASSWORD),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def seed() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        clear_curriculum_tables(session)
        demo_user = get_or_create_demo_user(session)

        for entry in MODULES:
            module = Module(**entry["module"])
            session.add(module)
            session.commit()
            session.refresh(module)

            for sub_module in entry.get("sub_modules", []):
                session.add(SubModule(module_id=module.id, **sub_module))
            for byte_fact in entry.get("byte_facts", []):
                session.add(ByteFact(module_id=module.id, **byte_fact))
            for spark_term in entry.get("spark_terms", []):
                session.add(SparkTerm(module_id=module.id, **spark_term))
            for bug_trigger in entry.get("bug_triggers", []):
                session.add(BugTrigger(module_id=module.id, **bug_trigger))
            session.commit()

            completed = module.order == 1
            session.add(
                Progress(
                    user_id=demo_user.id,
                    module_id=module.id,
                    completed=completed,
                    completed_at=datetime.now(timezone.utc) if completed else None,
                )
            )
            session.commit()

        print("Seed complete.")


if __name__ == "__main__":
    seed()
