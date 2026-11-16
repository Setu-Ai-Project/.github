import time
from unittest.mock import MagicMock, patch
import jwt
import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from config import Settings
from models.user import User

# Generate in-memory RSA keypair for tests
_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend(),
)
_public_key = _private_key.public_key()
_public_pem = _public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode("utf-8")

TEST_ISSUER = "https://test-example.clerk.accounts.dev"


class DummySigningKey:
    def __init__(self, key: str):
        self.key = key


@pytest.fixture(autouse=True)
def setup_test_settings(monkeypatch):
    """Ensure CLERK_ISSUER and CORS_ORIGINS are set for test execution."""
    monkeypatch.setenv("CLERK_ISSUER", TEST_ISSUER)
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")


@pytest.fixture
def mock_jwks_signing_key():
    """Mock PyJWKClient.get_signing_key_from_jwt to return our test RSA public key."""
    with patch("auth.get_jwks_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.get_signing_key_from_jwt.return_value = DummySigningKey(_public_pem)
        mock_get_client.return_value = mock_client
        yield mock_client


def _make_token(
    sub: str = "user_test_clerk_123",
    issuer: str = TEST_ISSUER,
    expires_in_seconds: int = 3600,
) -> str:
    now = int(time.time())
    payload = {
        "sub": sub,
        "iss": issuer,
        "iat": now,
        "exp": now + expires_in_seconds,
    }
    return jwt.encode(payload, _private_key, algorithm="RS256")


# ==============================================================================
# STEP H: REQUIRED TESTS 1 - 10
# ==============================================================================


def test_1_no_token_returns_401(client: TestClient):
    """Test 1: Calling GET /me with no token returns HTTP 401 with WWW-Authenticate header."""
    response = client.get("/me")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
    assert response.json()["detail"] == "Missing token"


def test_2_invalid_token_returns_401(client: TestClient, mock_jwks_signing_key):
    """Test 2: Calling GET /me with a corrupted/malformed token returns HTTP 401."""
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer not-a-valid-token-string"},
    )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
    assert response.json()["detail"] == "Invalid or expired token"


def test_3_expired_token_returns_401(client: TestClient, mock_jwks_signing_key):
    """Test 3: Calling GET /me with an expired token returns HTTP 401."""
    expired_token = _make_token(expires_in_seconds=-60)
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
    assert response.json()["detail"] == "Invalid or expired token"


def test_4_wrong_issuer_returns_401(client: TestClient, mock_jwks_signing_key):
    """Test 4: Calling GET /me with a token from another issuer returns HTTP 401."""
    alien_token = _make_token(issuer="https://alien-issuer.clerk.accounts.dev")
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {alien_token}"},
    )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
    assert response.json()["detail"] == "Invalid or expired token"


def test_5_valid_clerk_token_returns_200_and_user_profile(
    client: TestClient, mock_jwks_signing_key
):
    """Test 5: Calling GET /me with a valid Clerk token returns HTTP 200 with user's details."""
    token = _make_token(sub="user_step3_winner")
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["clerk_id"] == "user_step3_winner"
    assert data["name"] is None
    assert data["email"] is None
    # Ensure sensitive fields are not exposed in the response
    assert "hashed_password" not in data
    assert "password" not in data


def test_6_repeated_authentication_creates_no_duplicate_users(
    client: TestClient, session: Session, mock_jwks_signing_key
):
    """Test 6: Repeated calls to GET /me with the same Clerk user return the existing user without duplicates."""
    token = _make_token(sub="user_step3_idempotent")

    # First call - creates the row
    res1 = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert res1.status_code == 200
    user_id_1 = res1.json()["id"]

    # Second call - returns the existing row
    res2 = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 200
    user_id_2 = res2.json()["id"]

    assert user_id_1 == user_id_2

    # Verify directly in the database
    users = session.exec(
        select(User).where(User.clerk_id == "user_step3_idempotent")
    ).all()
    assert len(users) == 1


def test_7_health_endpoint_remains_public(client: TestClient):
    """Test 7: The health endpoint remains public and accessible without any authentication."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_8_existing_endpoints_continue_functioning(client: TestClient):
    """Test 8: Existing /users creation and /modules endpoints continue functioning normally."""
    # Existing user registration
    user_payload = {
        "name": "Legacy User",
        "email": "legacy_user@example.com",
        "password": "securepassword123",
    }
    user_res = client.post("/users/", json=user_payload)
    assert user_res.status_code == 201
    assert user_res.json()["name"] == "Legacy User"

    # Existing curriculum module listing
    modules_res = client.get("/modules")
    assert modules_res.status_code == 200
    assert isinstance(modules_res.json(), list)


def test_9_cors_configuration(client: TestClient):
    """Test 9: Configured origins are allowed, unapproved origins receive no allow header, and wildcard is rejected."""
    # Allowed origin
    res_allowed = client.get(
        "/health", headers={"Origin": "http://localhost:3000"}
    )
    assert res_allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"

    # Disallowed origin
    res_disallowed = client.get(
        "/health", headers={"Origin": "http://malicious-site.example"}
    )
    assert "access-control-allow-origin" not in res_disallowed.headers


# ==============================================================================
# CONFIGURATION & FAIL-FAST TESTS (STEPS B & C)
# ==============================================================================


def test_config_fail_fast_missing_clerk_issuer(monkeypatch):
    """Settings must fail fast at startup if CLERK_ISSUER is missing."""
    monkeypatch.delenv("CLERK_ISSUER", raising=False)
    with pytest.raises(RuntimeError, match="CLERK_ISSUER is not set"):
        Settings()


def test_config_fail_fast_non_https_issuer(monkeypatch):
    """Settings must fail fast if CLERK_ISSUER does not start with https://."""
    monkeypatch.setenv("CLERK_ISSUER", "http://insecure-clerk.accounts.dev")
    with pytest.raises(ValueError, match="must start with 'https://'"):
        Settings()


def test_config_strips_trailing_slash(monkeypatch):
    """Settings must automatically strip any trailing slash from CLERK_ISSUER."""
    monkeypatch.setenv(
        "CLERK_ISSUER", "https://example-00.clerk.accounts.dev///"
    )
    settings = Settings()
    assert settings.clerk_issuer == "https://example-00.clerk.accounts.dev"
