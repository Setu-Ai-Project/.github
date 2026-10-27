"""WebSocket routes for realtime client connections."""

import logging
from fastapi import APIRouter, WebSocket, status
from sqlmodel import Session, select
from starlette.websockets import WebSocketDisconnect

import database
from middleware.auth import verify_clerk_token
from models.user import User
from realtime.manager import manager

logger = logging.getLogger(__name__)

# Module-level engine reference for easy test patching or direct access
engine = database.engine

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Authenticated WebSocket endpoint.

    Validates Clerk token, ensures local user exists without writing to DB,
    registers connection with manager, and responds to ping with pong.
    """
    token = websocket.query_params.get("token")
    if not token:
        logger.warning("WebSocket rejected: missing or empty token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        clerk_user_id = verify_clerk_token(token)
    except ValueError as exc:
        logger.warning("WebSocket rejected: token verification failed (%s)", exc)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    except Exception as exc:
        logger.warning("WebSocket rejected: unexpected token verification error (%s)", exc)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Short-lived database session for read-only user lookup
    active_engine = engine if engine is not database.engine else database.engine
    try:
        with Session(active_engine) as session:
            user = session.exec(
                select(User).where(User.clerk_user_id == clerk_user_id)
            ).first()
            user_id = user.id if user else None
    except Exception as exc:
        logger.error("WebSocket rejected: database user lookup failed (%s)", exc)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if user_id is None:
        logger.warning("WebSocket rejected: no local user found for clerk_user_id")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Accept and register connection with manager
    await manager.connect(user_id, websocket)
    try:
        while True:
            text = await websocket.receive_text()
            if text == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for user %s", user_id)
    except Exception as exc:
        logger.warning("WebSocket receive loop error for user %s: %s", user_id, exc)
    finally:
        manager.disconnect(user_id, websocket)
