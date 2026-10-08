import os

from clerk_backend_api import AuthenticateRequestOptions, authenticate_request
from fastapi import HTTPException, Request, status


def get_current_user_id(request: Request) -> str:
    """FastAPI dependency: verifies the Clerk session token on the request
    and returns the Clerk user id (payload["sub"]). Raises 401 if missing/invalid.
    """
    authorized_parties = os.getenv(
        "CLERK_AUTHORIZED_PARTIES", "http://localhost:3000"
    ).split(",")

    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=os.environ["CLERK_SECRET_KEY"],
            jwt_key=os.getenv("CLERK_JWT_KEY") or None,
            authorized_parties=authorized_parties,
            accepts_token=["session_token"],
        ),
    )

    if not state.is_signed_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=state.reason.name if state.reason else "Unauthorized",
        )

    return state.payload["sub"]
