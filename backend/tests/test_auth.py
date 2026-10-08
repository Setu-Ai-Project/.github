from unittest.mock import patch

from clerk_backend_api.security.types import AuthStatus, RequestState


def test_me_without_token_returns_401(client, monkeypatch):
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake")

    response = client.get("/users/me")

    assert response.status_code == 401


def test_me_with_valid_token_returns_clerk_user_id(client, monkeypatch):
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake")

    fake_state = RequestState(
        status=AuthStatus.SIGNED_IN,
        payload={"sub": "user_test123"},
    )

    with patch("middleware.auth.authenticate_request", return_value=fake_state):
        response = client.get(
            "/users/me", headers={"Authorization": "Bearer fake-token"}
        )

    assert response.status_code == 200
    assert response.json() == {"clerk_user_id": "user_test123"}
