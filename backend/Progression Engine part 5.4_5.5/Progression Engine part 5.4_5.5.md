# Progression Engine: Part 5.4 and 5.5

## Goal

Step 5.4 connects an authenticated learner's challenge-completion request to the existing XP award service. Step 5.5 records the response contract for frontend integration. The Python implementation remains in the backend source files listed below; this document collects the full work summary and the instructions needed to review and verify it.

## Implementation Map

- [middleware/auth.py](../middleware/auth.py) verifies the Clerk token and provides the authenticated Clerk subject.
- [routes/challenge.py](../routes/challenge.py) resolves that identity to the local user, calls `award_xp`, and maps missing users/challenges to HTTP 404.
- [models/challenge.py](../models/challenge.py) defines the request body (`challenge_id` only) and exact response schema.
- [main.py](../main.py) registers the challenge router and the required `POST /complete-challenge` alias.
- [services/progression.py](../services/progression.py) performs the atomic, idempotent XP award; the route reuses it rather than duplicating progression logic.
- [tests/test_challenge_completion_route.py](../tests/test_challenge_completion_route.py) verifies authentication, server-derived identity, unmapped users, repeat submissions, missing challenges, required request data, and all three completion routes.
- [docs/contracts/award_xp.md](../docs/contracts/award_xp.md) is the canonical API contract.

## Related Code Excerpts

These excerpts show how user identity is stored and then used by the completion endpoint. The full implementations remain in the linked Python source files.

### User creation stores the Clerk identity

In [routes/user.py](../routes/user.py), registration copies `clerk_id` onto the local user record and commits it to the database. The completion route later uses this value to map the verified Clerk subject to `users.id`.

```python
db_user = User(
	name=user_in.name,
	email=user_in.email,
	hashed_password=hashed_password,
	clerk_id=user_in.clerk_id,
)
session.add(db_user)
session.commit()
session.refresh(db_user)
return db_user
```

### Completion route uses authenticated identity

The route imports the FastAPI dependencies, SQLModel session/query support, and the real progression service. The client's request body supplies the challenge ID; the Clerk subject comes from `get_current_user_id`.

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from database import get_session
from middleware.auth import get_current_user_id
from services.progression import ChallengeNotFound, UserNotFound, award_xp
```

The route resolves the Clerk identity to a local user, then passes that user's database ID and the challenge ID to `award_xp`:

```python
def _complete_challenge(session: Session, clerk_user_id: str, challenge_id: int):
	user = resolve_user_from_clerk_id(session, clerk_user_id)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="User not found",
		)

	try:
		result = award_xp(user_id=user.id, challenge_id=challenge_id, session=session)
	except ChallengeNotFound as exc:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=str(exc),
		)
	except UserNotFound as exc:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=str(exc),
		)

	return result
```

The registered request-body endpoint invokes this helper with the authenticated identity:

```python
def complete_challenge_by_body(
	payload: ChallengeCompletionRequest,
	session: Session = Depends(get_session),
	clerk_user_id: str = Depends(get_current_user_id),
):
	return _complete_challenge(session, clerk_user_id, payload.challenge_id)
```

### XP service supports route and standalone callers

`services/progression.py` uses a single public signature. A route can pass its existing session so the request and XP update share it; standalone callers may omit the session and let the service open one.

```python
from typing import Any, Optional
from sqlmodel import Session
from database import engine

def award_xp(
	user_id: int,
	challenge_id: int,
	session: Optional[Session] = None,
) -> dict[str, Any]:
	if session is not None:
		return _execute_award_xp(session, user_id, challenge_id)
	with Session(engine) as owned_session:
		return _execute_award_xp(owned_session, user_id, challenge_id)
```

The pasted notes contained duplicate imports and two conflicting `award_xp` signatures. The version above is the current implementation; do not combine it with the older two-argument-only signature or a second `with Session(engine) as session` implementation.

### Clerk identity prerequisite

For normal Clerk subjects such as `user_...`, the local `users` row must have the same subject stored in `clerk_id`. `UserCreate.clerk_id` is optional in the model, so account provisioning must explicitly link it. An authenticated Clerk user with no matching local row receives `404 User not found` from challenge completion.

## Endpoint Contract

The frontend endpoint is `POST /complete-challenge`.

```json
{
	"challenge_id": 7
}
```

The request does not accept a `user_id`. The authenticated Clerk identity determines which local user receives XP. An extra client-supplied `user_id` is ignored; it cannot select the recipient.

Successful response fields:

```json
{
	"user_id": 12,
	"challenge_id": 7,
	"xp_awarded": 50,
	"total_xp": 230,
	"level": 3,
	"previous_level": 2,
	"leveled_up": true,
	"xp_to_next_level": 70,
	"badges_unlocked": [],
	"already_completed": false
}
```

The response always has these ten fields. Badge entries, when badge evaluation is implemented, have `slug` and `name`; currently `badges_unlocked` is empty. A repeated completion returns HTTP 200 with `already_completed: true` and `xp_awarded: 0`.

| Field | Meaning |
| --- | --- |
| `user_id` | Local integer user ID resolved from the authenticated Clerk identity. |
| `challenge_id` | Challenge submitted in the request. |
| `xp_awarded` | XP credited by this request; `0` for an already-completed challenge. |
| `total_xp` | Learner's cumulative XP after this request. |
| `level` | Learner's level after this request. |
| `previous_level` | Level before this request; unchanged for repeat completions. |
| `leveled_up` | Whether this request increased the learner's level. |
| `xp_to_next_level` | XP remaining to the next level, or `0` at the maximum level. |
| `badges_unlocked` | Badges unlocked by this request; currently an empty array. |
| `already_completed` | Whether this challenge had already been completed by this user. |

| Status | Meaning |
| --- | --- |
| `200` | Completion recorded or already completed. |
| `401` | Missing or invalid authentication. |
| `404` | Authenticated user is not found locally, or challenge ID does not exist. |
| `422` | `challenge_id` is missing or is not an integer. |

The same operation is also available at `POST /challenges/complete` and `POST /challenges/{challenge_id}/complete`.

## Frontend Contract Message

Progression contract v1 (B1)

`POST /complete-challenge` with body `{"challenge_id": 7}` returns the response above. A repeated completion returns `already_completed: true` and `xp_awarded: 0`. Error responses use FastAPI's `{"detail": "..."}` shape.

### Planned progress polling (Step 5.8; not implemented)

```http
GET /progress/me
```

Proposed response shape from the assignment guide:

```json
{
	"total_xp": 230,
	"level": 3,
	"xp_to_next_level": 70,
	"badges": [
		{"slug": "first-steps", "name": "First Steps", "awarded_at": "2025-..."}
	],
	"certificates": [
		{"module_id": 1, "image_url": "https://...", "issued_at": "2025-..."}
	]
}
```

### Planned WebSocket events (Step 5.7; not implemented)

```text
ws://HOST/ws?token=<login token>
```

Proposed messages:

```json
{"type": "level_up", "level": 3, "previous_level": 2, "total_xp": 230}
```

```json
{
	"type": "badge_unlocked",
	"badge": {"slug": "first-steps", "name": "First Steps"}
}
```

These future payloads are draft examples from the assignment guide; confirm them with the Step 5.7/5.8 owners before treating them as stable. The current `/progress/` endpoint returns module progress records and is not a substitute for `/progress/me`. Until the new polling endpoint exists, the frontend cannot poll a progression summary from this backend. Before shipping the WebSocket, agree on token transport with the security owner because query-string tokens can be captured in logs.

## Security Note

The endpoint currently allows any authenticated learner to report a challenge completion. It does not validate answers or submissions. Do not treat this endpoint as proof that a challenge was passed; connect it to validated submissions and restrict direct completion access during progression hardening. A TODO in the route marks this requirement.

## Manual Check

1. Start the backend and open `/docs`.
2. Call `POST /complete-challenge` without authentication; expect `401`.
3. Authorize with a valid Clerk token and send `{"challenge_id": 7}` for an existing challenge; expect `200` and the response fields above.
4. Send the same challenge again; expect `already_completed: true` and `xp_awarded: 0`.
5. Send `{"challenge_id": 99999}`; expect `404` with a clear detail message.
6. Send `{"challenge_id": 7, "user_id": 1}`; the authenticated learner, not the supplied ID, must receive the XP.

## Verification

The complete backend suite passed: **61 passed**. To run it from the backend directory, use:

```powershell
$env:DATABASE_URL = "sqlite://"
.venv\Scripts\python.exe -m pytest -v
```

The process-local SQLite URL avoids requiring a running PostgreSQL server just to import the app for tests. Tests themselves use isolated in-memory SQLite fixtures. The last full run emitted one Starlette/httpx deprecation warning; all tests passed.
