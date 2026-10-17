import os

from clerk_backend_api import AuthenticateRequestOptions, authenticate_request
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database import get_session
from models.user import User


class _TokenRequest:
    """Minimal request-like object satisfying the Clerk SDK Requestish protocol."""

    def __init__(self, token: str) -> None:
        self.headers = {"Authorization": f"Bearer {token}"}


def _get_authenticate_request_options() -> AuthenticateRequestOptions:
    authorized_parties = os.getenv(
        "CLERK_AUTHORIZED_PARTIES", "http://localhost:3000"
    ).split(",")

    return AuthenticateRequestOptions(
        secret_key=os.environ["CLERK_SECRET_KEY"],
        jwt_key=os.getenv("CLERK_JWT_KEY") or None,
        authorized_parties=authorized_parties,
        accepts_token=["session_token"],
    )


def verify_clerk_token(token: str) -> str:
    """Verifies a raw Clerk session token and returns the verified Clerk user ID.

    Raises ValueError if verification fails or no valid Clerk user ID can be obtained.
    Does not raise HTTPException.
    """
    if not token or not isinstance(token, str):
        raise ValueError("Missing or invalid token")

    request = _TokenRequest(token)
    try:
        state = authenticate_request(request, _get_authenticate_request_options())
    except Exception as exc:
        raise ValueError(f"Token verification failed: {exc}") from exc

    if not state.is_signed_in:
        reason = state.reason.name if state.reason else "Unauthorized"
        raise ValueError(f"Token verification failed: {reason}")

    if not state.payload or "sub" not in state.payload:
        raise ValueError("Token payload missing subject")

    return state.payload["sub"]


def get_current_user_id(request: Request) -> str:
    """FastAPI dependency: verifies the Clerk session token on the request
    and returns the Clerk user id (payload["sub"]). Raises 401 if missing/invalid.
    """
    state = authenticate_request(
        request,
        _get_authenticate_request_options(),
    )

    if not state.is_signed_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=state.reason.name if state.reason else "Unauthorized",
        )

    return state.payload["sub"]


def get_current_user(
    clerk_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> User:
    """FastAPI dependency: returns the local User row for the logged-in Clerk user,
    creating it on their first request. Raises 401 (via get_current_user_id) if not logged in.
    """
    statement = select(User).where(User.clerk_user_id == clerk_user_id)

    # 1. Already linked: return the existing row.
    user = session.exec(statement).first()
    if user:
        return user

    # 2. First request from this Clerk user: create their local row.
    # Clerk session tokens carry no email, so use a placeholder on a real-looking
    # domain (".local" is rejected by the email validator). "!clerk" is not a valid
    # password hash, so nobody can log in to this row with a password.
    user = User(
        name="Learner",
        email=f"{clerk_user_id}@users.setuai.dev",
        hashed_password="!clerk",
        clerk_user_id=clerk_user_id,
    )
    session.add(user)

    # 3. Save it. If two first requests raced, the unique constraint rejects the
    # second insert, so roll back and return the row the other request created.
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        return session.exec(statement).one()

    session.refresh(user)
    return user
