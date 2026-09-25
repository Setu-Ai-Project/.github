from models.module import Module


def _make_module(session, **overrides):
    defaults = {"title": "Test Module", "description": "A test module.", "order": 1}
    defaults.update(overrides)
    module = Module(**defaults)
    session.add(module)
    session.commit()
    session.refresh(module)
    return module


def test_list_modules_empty(client):
    response = client.get("/modules/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_modules_ordered_by_order(client, session):
    _make_module(session, title="Second", order=2)
    _make_module(session, title="First", order=1)

    response = client.get("/modules/")
    assert response.status_code == 200
    titles = [module["title"] for module in response.json()]
    assert titles == ["First", "Second"]


def test_get_module_by_id(client, session):
    module = _make_module(session)

    response = client.get(f"/modules/{module.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Module"


def test_get_module_not_found(client):
    response = client.get("/modules/999")
    assert response.status_code == 404
