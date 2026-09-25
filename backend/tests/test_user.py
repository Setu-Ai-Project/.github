def test_create_and_get_user(client):
    response = client.post(
        "/users/",
        json={"name": "Jane Doe", "email": "jane@example.com", "password": "supersecret"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Jane Doe"
    assert body["email"] == "jane@example.com"
    assert "hashed_password" not in body

    user_id = body["id"]
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Jane Doe"


def test_create_user_duplicate_email_rejected(client):
    payload = {"name": "Jane Doe", "email": "jane@example.com", "password": "supersecret"}
    first = client.post("/users/", json=payload)
    assert first.status_code == 201

    second = client.post("/users/", json=payload)
    assert second.status_code == 400


def test_get_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404
