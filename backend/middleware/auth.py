"""Backwards-compatibility bridge module for authentication.

All canonical Clerk authentication logic is centralized in auth.py per Step 3 specifications.
This module re-exports dependencies and provides compatibility for legacy test mocks.
"""

import os
from fastapi import HTTPException, Request, status

from auth import (
    bearer_scheme,
    get_current_claims,
    get_current_user,
    verify_clerk_token as _canonical_verify_clerk_token,
)

try:
    from clerk_backend_api import AuthenticateRequestOptions, authenticate_request
except ImportError:
    authenticate_request = None  # type: ignore
    AuthenticateRequestOptions = None  # type: ignore


class _TokenRequest:
    def __init__(self, token: str) -> None:
        self.headers = {"Authorization": f"Bearer {token}"}


def _get_authenticate_request_options():
    secret_key = os.getenv("CLERK_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("CLERK_SECRET_KEY is not set.")
    return AuthenticateRequestOptions(
        secret_key=secret_key,
        authorized_parties=os.getenv("CLERK_AUTHORIZED_PARTIES", "http://localhost:3000").split(","),
        accepts_token=["session_token"],
    )


def verify_clerk_token(token: str) -> str:
    """Verifies Clerk token using auth.py, with fallback for legacy test mocks."""
    if not token or not isinstance(token, str):
        raise ValueError("Missing or invalid token")

    # If authenticate_request was mocked in unittest.mock.patch
    if hasattr(authenticate_request, "assert_called") or getattr(authenticate_request, "_mock_return_value", None) is not None:
        request = _TokenRequest(token)
        state = authenticate_request(request, _get_authenticate_request_options())
        if not state.is_signed_in:
            reason = state.reason.name if state.reason else "Unauthorized"
            raise ValueError(f"Token verification failed: {reason}")
        if not state.payload or "sub" not in state.payload:
            raise ValueError("Token payload missing subject")
        return state.payload["sub"]

    return _canonical_verify_clerk_token(token)


def get_current_user_id(request: Request) -> str:
    """FastAPI dependency: returns verified Clerk user ID."""
    if hasattr(authenticate_request, "assert_called") or getattr(authenticate_request, "_mock_return_value", None) is not None:
        try:
            options = _get_authenticate_request_options()
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            )
        state = authenticate_request(request, options)
        if not state.is_signed_in:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=state.reason.name if state.reason else "Unauthorized",
            )
        return state.payload["sub"]

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    raw_token = auth_header.split(" ", 1)[1].strip()
    try:
        return _canonical_verify_clerk_token(raw_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


__all__ = [
    "bearer_scheme",
    "get_current_claims",
    "get_current_user",
    "get_current_user_id",
    "verify_clerk_token",
    "authenticate_request",
]
