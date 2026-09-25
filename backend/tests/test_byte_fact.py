from models.byte_fact import ByteFact
from models.module import Module


def _make_module(session):
    module = Module(title="Module", description="d", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)
    return module


def test_list_byte_facts_filtered_by_module(client, session):
    module_a = _make_module(session)
    module_b = _make_module(session)

    session.add(ByteFact(module_id=module_a.id, fact="AI was coined in 1956."))
    session.add(ByteFact(module_id=module_b.id, fact="Prompts change AI output."))
    session.commit()

    response = client.get(f"/byte-facts/?module_id={module_a.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["fact"] == "AI was coined in 1956."


def test_list_byte_facts_unknown_module_returns_empty_list(client):
    response = client.get("/byte-facts/?module_id=999")
    assert response.status_code == 200
    assert response.json() == []


def test_get_byte_fact_not_found(client):
    response = client.get("/byte-facts/999")
    assert response.status_code == 404
