# auth.py - ALL Clerk-specific authentication logic lives in this one file
from typing import Optional
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from config import get_settings
from database import get_session
from models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

_jwks_client: Optional[PyJWKClient] = None


def get_jwks_client() -> PyJWKClient:
    """Helper to get or initialize the Clerk PyJWKClient using the configured CLERK_ISSUER."""
    global _jwks_client
    if _jwks_client is None:
        settings = get_settings()
        jwks_url = f"{settings.clerk_issuer}/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


def _unauthorized(detail: str) -> HTTPException:
    """Return an HTTP 401 Unauthorized exception with the required WWW-Authenticate header."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


# Reads the Bearer token, verifies its RS256 signature against Clerk's JWKS, checks issuer and expiry, and returns claims
def get_current_claims(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    """Check the token and return what is inside it."""
    if creds is None:
        raise _unauthorized("Missing token")

    token = creds.credentials
    if not token or not isinstance(token, str):
        raise _unauthorized("Missing or invalid token")

    try:
        settings = get_settings()
        client = get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],  # Only accept RS256 signatures
            issuer=settings.clerk_issuer,  # Must match our configured Clerk issuer
            options={"verify_aud": False},  # Clerk session tokens omit aud
        )  # Expiry ('exp') is automatically verified by PyJWT
        return claims
    except (jwt.PyJWTError, Exception):
        # Never crash with 500 for a bad, expired, or malformed token
        raise _unauthorized("Invalid or expired token")


# Extracts the verified user ID (sub claim) from the token
def get_current_user_id(claims: dict = Depends(get_current_claims)) -> str:
    """Return the Clerk user id from verified claims."""
    sub = claims.get("sub")
    if not sub:
        raise _unauthorized("Token payload missing subject")
    return sub


# Looks up the user in the database by clerk_id, or creates a new record on first login (just-in-time provisioning)
def get_current_user(
    claims: Optional[dict] = Depends(get_current_claims),
    session: Session = Depends(get_session),
    clerk_user_id: Optional[str] = None,
    clerk_id: Optional[str] = None,
) -> User:
    """Find our database user for this token. Create one on first login."""
    target_id = clerk_id or clerk_user_id
    if not target_id and claims:
        target_id = claims.get("sub")

    if not target_id:
        raise _unauthorized("Token payload missing subject")

    # Look for matching user by clerk_id (or legacy clerk_user_id)
    statement = select(User).where(
        (User.clerk_id == target_id) | (User.clerk_user_id == target_id)
    )
    user = session.exec(statement).first()

    if user is None:
        # Create user record just-in-time
        user = User(clerk_id=target_id, clerk_user_id=target_id)
        session.add(user)
        try:
            session.commit()
            session.refresh(user)
        except IntegrityError:
            # Handle concurrent first logins gracefully
            session.rollback()
            user = session.exec(statement).first()

    return user


# Validates a raw token string (e.g. for WebSocket connections) and returns verified Clerk user ID
def verify_clerk_token(token: str) -> str:
    """Verifies a raw Clerk session token and returns the verified Clerk user ID.

    Raises ValueError if verification fails. Does not raise HTTPException.
    """
    if not token or not isinstance(token, str):
        raise ValueError("Missing or invalid token")

    try:
        settings = get_settings()
        client = get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.clerk_issuer,
            options={"verify_aud": False},
        )
        sub = claims.get("sub")
        if not sub:
            raise ValueError("Token payload missing subject")
        return sub
    except Exception as exc:
        raise ValueError(f"Token verification failed: {exc}") from exc
