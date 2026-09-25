"""Shared pytest fixtures for the test suite.

Every test runs against a fresh in-memory SQLite database instead of the
real Postgres database, so tests are fast, isolated, and don't require a
running Postgres server or any environment setup. The FastAPI app's
get_session dependency is overridden to use this test database, and the
app's lifespan (which would otherwise create tables against the real
Postgres engine) is deliberately never triggered.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from database import get_session
from main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    # Not used as a context manager on purpose: this avoids triggering the
    # app's lifespan, which would call SQLModel.metadata.create_all against
    # the real Postgres engine from database.py.
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
