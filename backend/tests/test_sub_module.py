from models.module import Module
from models.sub_module import SubModule


def _make_module(session, **overrides):
    defaults = {"title": "Parent Module", "description": "d", "order": 1}
    defaults.update(overrides)
    module = Module(**defaults)
    session.add(module)
    session.commit()
    session.refresh(module)
    return module


def _make_sub_module(session, module_id, **overrides):
    defaults = {"title": "Sub", "description": "d", "order": 1}
    defaults.update(overrides)
    sub_module = SubModule(module_id=module_id, **defaults)
    session.add(sub_module)
    session.commit()
    session.refresh(sub_module)
    return sub_module


def test_list_sub_modules_filtered_by_module(client, session):
    module_a = _make_module(session, title="A")
    module_b = _make_module(session, title="B", order=2)
    _make_sub_module(session, module_a.id, title="A1")
    _make_sub_module(session, module_b.id, title="B1")

    response = client.get(f"/sub-modules/?module_id={module_a.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "A1"


def test_list_sub_modules_no_filter_returns_all(client, session):
    module = _make_module(session)
    _make_sub_module(session, module.id, title="A1", order=1)
    _make_sub_module(session, module.id, title="A2", order=2)

    response = client.get("/sub-modules/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_sub_modules_unknown_module_returns_empty_list(client):
    response = client.get("/sub-modules/?module_id=999")
    assert response.status_code == 200
    assert response.json() == []


def test_get_sub_module_not_found(client):
    response = client.get("/sub-modules/999")
    assert response.status_code == 404
