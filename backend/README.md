# SetuAI Backend

FastAPI + SQLModel + PostgreSQL API for the SetuAI app: user accounts, the
curriculum data model (modules, sub-modules, progress, and mascot content),
and the endpoints the frontend reads from.

## Tech stack

- [FastAPI](https://fastapi.tiangolo.com/) — web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) — combines SQLAlchemy + Pydantic for the ORM models
- [PostgreSQL](https://www.postgresql.org/) — database
- [pytest](https://docs.pytest.org/) — test suite

There is no migration tool (no Alembic). Tables are created automatically on
startup from the SQLModel classes in `models/`.

## Prerequisites

- Python 3.11 or newer
- PostgreSQL installed and running locally
- git

## Setup

1. **Clone the repo and go to the backend folder**

   ```bash
   git clone <repo-url>
   cd backend
   ```

2. **(Recommended) Create a virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a local PostgreSQL database**

   Using `psql`, or any GUI tool (pgAdmin, TablePlus, etc.):
   ```sql
   CREATE DATABASE setuai;
   ```

5. **Configure your environment variables**

   Copy the example file and edit it to match your local database:

   ```bash
   cp .env.example .env
   ```

   Then set `DATABASE_URL` in `.env` to your own connection string, e.g.:

   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/setuai
   ```

   `.env` is gitignored — never commit your real credentials.

6. **Run the dev server**

   ```bash
   uvicorn main:app --reload
   ```
   On startup, the app automatically creates any tables that don't exist yet
   — nothing else to run. The API is now live at `http://127.0.0.1:8000`, and
   interactive docs (try every endpoint from the browser) are at
   `http://127.0.0.1:8000/docs`.

7. **(Optional) Seed sample curriculum content**

   The curriculum tables start empty. To fill them with realistic dummy data
   (modules, sub-modules, mascot content, a demo user, and progress rows) for
   local development or frontend work:

   ```bash
   python -m scripts.seed
   ```
   This is safe to re-run — it clears and reinserts curriculum content each
   time, but never touches other users. **Local/dev use only — never run it
   against a shared or production database.**

## Running tests

```bash
pytest
```

Tests run against an isolated in-memory SQLite database (not your local
Postgres), so there's no setup needed beyond `pip install -r requirements.txt`
— no running database required, and nothing you do in tests touches your
real data.

## Authentication

Login is handled by [Clerk](https://clerk.com/) — the frontend has its own
Clerk sign-in UI, and the backend's job is just to verify the token Clerk
attaches to incoming requests.

To protect a route, add `Depends(get_current_user_id)` from
`middleware/auth.py`:

```python
from fastapi import Depends
from middleware.auth import get_current_user_id

@router.get("/something")
def protected_route(clerk_user_id: str = Depends(get_current_user_id)):
    ...
```

A request with no token (or an invalid one) gets a `401`; a valid one returns
the Clerk user id (`payload["sub"]`) — a string like `user_...`, not our
Postgres `users.id`. `GET /users/me` is the example protected route.

You'll need these in your `.env` (see `.env.example`):

- `CLERK_SECRET_KEY` — from the Clerk dashboard, same project as the
  frontend's `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_JWT_KEY` — optional; leave blank to use Clerk's networked JWKS
  verification instead of a local PEM key
- `CLERK_AUTHORIZED_PARTIES` — comma-separated list of allowed frontend
  origins (defaults to `http://localhost:3000`)

To test manually end-to-end: sign in through the frontend, open the browser
console and run `await window.Clerk.session.getToken()` to get a real token,
then `curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/users/me`.
