"""WebSocket Connection Manager for managing per-user active connections."""

import asyncio
from typing import Optional
from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections grouped by user ID."""

    loop: Optional[asyncio.AbstractEventLoop] = None

    def __init__(self) -> None:
        self.active: dict[int, set[WebSocket]] = {}
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        """Accept the WebSocket connection and store it under the specified user ID."""
        await websocket.accept()
        if user_id not in self.active:
            self.active[user_id] = set()
        self.active[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """Remove a WebSocket connection.

        If the user's connection set becomes empty, remove the user ID from active.
        """
        if user_id in self.active:
            self.active[user_id].discard(websocket)
            if not self.active[user_id]:
                del self.active[user_id]

    async def send_to_user(self, user_id: int, message: dict) -> None:
        """Send a JSON message to every active WebSocket connection for that user.

        If sending fails for one connection, remove that connection and continue
        attempting to send to the others. Never propagate send failures to the caller.
        """
        connections = self.active.get(user_id)
        if not connections:
            return

        failed_connections: list[WebSocket] = []
        for websocket in list(connections):
            try:
                await websocket.send_json(message)
            except Exception:
                failed_connections.append(websocket)

        for failed_ws in failed_connections:
            self.disconnect(user_id, failed_ws)


# Shared instance across the application
manager = ConnectionManager()
