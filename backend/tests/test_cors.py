from fastapi.testclient import TestClient

from main import get_cors_origins


def test_cors_allowed_origin_returns_header(client: TestClient):
    """A request with Origin http://localhost:3000 gets Access-Control-Allow-Origin back."""
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_unlisted_origin_gets_no_allow_header(client: TestClient):
    """A request with an unlisted origin (http://evil.example) gets no Access-Control-Allow-Origin header."""
    response = client.get("/health", headers={"Origin": "http://evil.example"})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_options_allows_auth_and_post(client: TestClient):
    """A preflight OPTIONS request from the allowed origin allows the Authorization header and POST."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    allow_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allow_methods
    allow_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "authorization" in allow_headers


def test_get_cors_origins_parses_comma_separated_values(monkeypatch):
    """get_cors_origins() with several comma-separated values and spaces is parsed correctly."""
    monkeypatch.setenv(
        "CORS_ORIGINS",
        " http://localhost:3000 , https://setuai.dev , http://localhost:8080 , ",
    )
    origins = get_cors_origins()
    assert origins == [
        "http://localhost:3000",
        "https://setuai.dev",
        "http://localhost:8080",
    ]


def test_get_cors_origins_never_allows_wildcard(monkeypatch):
    """'*' in CORS_ORIGINS is never allowed, and if it is the only entry the helper falls back to http://localhost:3000."""
    monkeypatch.setenv("CORS_ORIGINS", "*")
    assert get_cors_origins() == ["http://localhost:3000"]

    monkeypatch.setenv("CORS_ORIGINS", "*, http://example.com")
    assert get_cors_origins() == ["http://example.com"]

    monkeypatch.setenv("CORS_ORIGINS", " * , * ")
    assert get_cors_origins() == ["http://localhost:3000"]
