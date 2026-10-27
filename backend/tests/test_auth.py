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


def test_verify_clerk_token_empty_or_invalid_raises():
    import pytest
    from middleware.auth import verify_clerk_token

    with pytest.raises(ValueError, match="Missing or invalid token"):
        verify_clerk_token("")

    with pytest.raises(ValueError, match="Missing or invalid token"):
        verify_clerk_token(None)  # type: ignore


def test_verify_clerk_token_valid(monkeypatch):
    from middleware.auth import verify_clerk_token

    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake")
    fake_state = RequestState(
        status=AuthStatus.SIGNED_IN,
        payload={"sub": "user_verified_999"},
    )
    with patch("middleware.auth.authenticate_request", return_value=fake_state):
        sub = verify_clerk_token("valid_token_raw")

    assert sub == "user_verified_999"


def test_verify_clerk_token_signed_out_raises(monkeypatch):
    import pytest
    from middleware.auth import verify_clerk_token

    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake")
    fake_state = RequestState(
        status=AuthStatus.SIGNED_OUT,
    )
    with patch("middleware.auth.authenticate_request", return_value=fake_state):
        with pytest.raises(ValueError, match="Token verification failed"):
            verify_clerk_token("bad_token_raw")
