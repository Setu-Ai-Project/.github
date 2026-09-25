from models.bug_trigger import BugTrigger
from models.module import Module


def _make_module(session):
    module = Module(title="Module", description="d", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)
    return module


def test_list_bug_triggers_filtered_by_module(client, session):
    module_a = _make_module(session)
    module_b = _make_module(session)

    session.add(
        BugTrigger(
            module_id=module_a.id,
            trigger_phrase="AI is always right",
            warning_message="Bug says: double-check important answers.",
        )
    )
    session.add(
        BugTrigger(
            module_id=module_b.id,
            trigger_phrase="AI has no bias",
            warning_message="Bug says: AI can inherit bias from training data.",
        )
    )
    session.commit()

    response = client.get(f"/bug-triggers/?module_id={module_a.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["trigger_phrase"] == "AI is always right"


def test_list_bug_triggers_unknown_module_returns_empty_list(client):
    response = client.get("/bug-triggers/?module_id=999")
    assert response.status_code == 200
    assert response.json() == []


def test_get_bug_trigger_not_found(client):
    response = client.get("/bug-triggers/999")
    assert response.status_code == 404
