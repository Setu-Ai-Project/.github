"""Simple WebSocket test client for verifying the /ws endpoint.

Usage:
    python scripts/ws_test_client.py <CLERK_TOKEN>
"""

import asyncio
import sys
import urllib.parse
import websockets
from websockets.exceptions import WebSocketException


async def run_client() -> None:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("Error: Missing Clerk token argument.", file=sys.stderr)
        print("Usage: python scripts/ws_test_client.py <CLERK_TOKEN>", file=sys.stderr)
        sys.exit(1)

    raw_token = sys.argv[1].strip()
    encoded_token = urllib.parse.quote(raw_token, safe="")
    ws_url = f"ws://localhost:8000/ws?token={encoded_token}"

    print("Connecting to ws://localhost:8000/ws ...")

    try:
        async with websockets.connect(ws_url) as websocket:
            print("Connected successfully.")
            print("Sending 'ping'...")
            await websocket.send("ping")

            async for message in websocket:
                print(f"Received message: {message}")
    except websockets.exceptions.InvalidStatus as exc:
        print(
            f"Connection rejected by server (HTTP status: {exc.response.status_code}).",
            file=sys.stderr,
        )
        sys.exit(1)
    except websockets.exceptions.ConnectionClosed as exc:
        print(
            f"WebSocket connection closed (code: {exc.rcvd.code if exc.rcvd else 'unknown'}, "
            f"reason: {exc.rcvd.reason if exc.rcvd else 'none'}).",
            file=sys.stderr,
        )
        sys.exit(1)
    except WebSocketException as exc:
        print(f"WebSocket error: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
    except ConnectionRefusedError:
        print(
            "Connection failed: Could not connect to localhost:8000. Is the backend server running?",
            file=sys.stderr,
        )
        sys.exit(1)
    except OSError as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        print("\nExiting WebSocket test client.")


if __name__ == "__main__":
    main()
