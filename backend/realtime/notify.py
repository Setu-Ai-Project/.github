"""Progression notification dispatch for realtime WebSocket subscribers."""

import asyncio
import logging

try:
    from realtime.manager import manager
except ImportError:
    from backend.realtime.manager import manager

logger = logging.getLogger(__name__)


def notify_progress(result: dict) -> None:
    """Send progression event notifications to the authenticated user via WebSocket.

    Why asyncio.run_coroutine_threadsafe is necessary:
    Synchronous endpoints execute in worker threads, while WebSocket connections
    belong to the main event loop. The coroutine must be scheduled on that existing
    loop rather than awaited directly or run on a new event loop.
    """
    try:
        # 1. If xp_awarded == 0, do nothing (e.g. repeated challenge or duplicate completion)
        if result.get("xp_awarded", 0) == 0:
            return

        # 4. If manager.loop is None, return without sending or raising
        if manager.loop is None:
            return

        user_id = result.get("user_id")
        if user_id is None:
            return

        # 2. If leveled_up is true, send level_up message with exactly 4 fields
        if result.get("leveled_up"):
            level_up_message = {
                "type": "level_up",
                "level": result["level"],
                "previous_level": result["previous_level"],
                "total_xp": result["total_xp"],
            }
            # asyncio.run_coroutine_threadsafe is necessary because synchronous endpoints
            # execute in worker threads, while WebSocket connections belong to the main
            # event loop. The coroutine must be scheduled on that existing loop rather
            # than awaited directly or run on a new event loop.
            asyncio.run_coroutine_threadsafe(
                manager.send_to_user(user_id, level_up_message),
                manager.loop,
            )

        # 3. For each item in badges_unlocked, send badge_unlocked message
        badges = result.get("badges_unlocked") or []
        for badge in badges:
            if isinstance(badge, dict):
                badge_slug = badge["slug"]
                badge_name = badge["name"]
            else:
                badge_slug = getattr(badge, "slug")
                badge_name = getattr(badge, "name")

            badge_message = {
                "type": "badge_unlocked",
                "badge": {
                    "slug": badge_slug,
                    "name": badge_name,
                },
            }
            asyncio.run_coroutine_threadsafe(
                manager.send_to_user(user_id, badge_message),
                manager.loop,
            )

    except Exception:
        # 5. Must never raise an exception to its caller; log full traceback
        logger.exception("Unexpected error while dispatching progress notification for result: %s", result)
