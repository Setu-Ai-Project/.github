from models.module import Module
from models.spark_term import SparkTerm


def _make_module(session):
    module = Module(title="Module", description="d", order=1)
    session.add(module)
    session.commit()
    session.refresh(module)
    return module


def test_list_spark_terms_filtered_by_module(client, session):
    module_a = _make_module(session)
    module_b = _make_module(session)

    session.add(
        SparkTerm(module_id=module_a.id, term="Algorithm", definition="A set of steps.")
    )
    session.add(
        SparkTerm(module_id=module_b.id, term="Prompt", definition="An instruction to an AI.")
    )
    session.commit()

    response = client.get(f"/spark-terms/?module_id={module_a.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["term"] == "Algorithm"


def test_list_spark_terms_unknown_module_returns_empty_list(client):
    response = client.get("/spark-terms/?module_id=999")
    assert response.status_code == 200
    assert response.json() == []


def test_get_spark_term_not_found(client):
    response = client.get("/spark-terms/999")
    assert response.status_code == 404
