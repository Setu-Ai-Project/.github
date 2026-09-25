from datetime import datetime, timezone

from models.module import Module
from models.progress import Progress
from models.user import User


def _make_user(session, email="learner@example.com"):
    user = User(name="Learner", email=email, hashed_password="hashed")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_module(session, order=1):
    module = Module(title=f"Module {order}", description="d", order=order)
    session.add(module)
    session.commit()
    session.refresh(module)
    return module


def test_progress_filtered_by_user_and_module(client, session):
    user = _make_user(session)
    module_a = _make_module(session, order=1)
    module_b = _make_module(session, order=2)

    session.add(
        Progress(
            user_id=user.id,
            module_id=module_a.id,
            completed=True,
            completed_at=datetime.now(timezone.utc),
        )
    )
    session.add(Progress(user_id=user.id, module_id=module_b.id, completed=False))
    session.commit()

    response = client.get(f"/progress/?user_id={user.id}&module_id={module_a.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["completed"] is True
    assert data[0]["completed_at"] is not None


def test_progress_filtered_by_user_only(client, session):
    user = _make_user(session)
    module_a = _make_module(session, order=1)
    module_b = _make_module(session, order=2)

    session.add(Progress(user_id=user.id, module_id=module_a.id, completed=False))
    session.add(Progress(user_id=user.id, module_id=module_b.id, completed=False))
    session.commit()

    response = client.get(f"/progress/?user_id={user.id}")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_progress_get_by_id_not_found(client):
    response = client.get("/progress/999")
    assert response.status_code == 404
