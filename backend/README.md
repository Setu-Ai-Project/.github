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

## Database changes for Step 6

`create_all` creates new tables on startup but never adds columns to an
existing table. If your local database already existed before Step 6, run
these once (new databases get them automatically):

```sql
-- Step 5 (Pair B1): XP and level on users
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_xp INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS level INTEGER NOT NULL DEFAULT 1;
-- Step 6: link users to Clerk, and rules for the answer checker
ALTER TABLE users ADD COLUMN IF NOT EXISTS clerk_user_id VARCHAR(255) UNIQUE;
ALTER TABLE challenges ADD COLUMN IF NOT EXISTS rules JSON NOT NULL DEFAULT '{}';
```

The `submissions` table is created automatically when the server restarts.

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

Routes that need the database `User` row (with its integer `id`) use
`Depends(get_current_user)` from `middleware/auth.py` instead. It creates the
user on their first request and links it through `users.clerk_user_id`.

You'll need these in your `.env` (see `.env.example`):

- `CLERK_SECRET_KEY` — from the Clerk dashboard, same project as the
  frontend's `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_JWT_KEY` — optional; leave blank to use Clerk's networked JWKS
  verification instead of a local PEM key
- `CLERK_AUTHORIZED_PARTIES` — comma-separated list of allowed frontend
  origins (defaults to `http://localhost:3000`)

### Testing login manually

Use this to check that Clerk works on your machine, and to get a token for
trying any protected endpoint. Commands are for Windows PowerShell; use
`curl.exe`, not `curl` (in PowerShell 5.1 `curl` is a different command).

1. **Prepare the database.** If your database existed before Step 6, run the
   `ALTER TABLE` lines from [Database changes for Step 6](#database-changes-for-step-6).
2. **Start the backend** from the `backend/` folder, with your virtual
   environment active:
   ```powershell
   uvicorn main:app --reload
   ```
3. **Start the frontend and sign in.** In a second terminal:
   ```powershell
   cd frontend/gamifiedsetu
   npm run dev
   ```
   Open http://localhost:3000 and sign in.
4. **Get a token.** In the browser, open DevTools (F12) → Console and run:
   ```js
   await window.Clerk.session.getToken()
   ```
   Copy the printed string. Tokens expire after about 60 seconds, so get a
   fresh one right before each request.
5. **Call a protected route with the token:**
   ```powershell
   curl.exe -i -H "Authorization: Bearer <token>" http://127.0.0.1:8000/users/me
   ```
   You should get `200` and `{"clerk_user_id": "user_..."}`. Note that id.
6. **Call it without a token:**
   ```powershell
   curl.exe -i http://127.0.0.1:8000/users/me
   ```
   You should get `401`.
7. **Check that your login links to a database user.** Run this twice from
   `backend/`, with your id from step 5:
   ```powershell
   python -c "from sqlmodel import Session; from database import engine; from middleware.auth import get_current_user; s = Session(engine); u = get_current_user(clerk_user_id='user_XXX', session=s); print(u.id, u.name, u.email, u.clerk_user_id)"
   ```
   The first run creates your user (for example `3 Learner user_XXX@users.setuai.dev user_XXX`).
   The second run must print the **same** id.
8. **Read the user back:**
   ```powershell
   curl.exe -i http://127.0.0.1:8000/users/<id from step 7>
   ```
   You should get `200` with `total_xp` and `level`.

| Problem | Likely cause | Fix |
|---|---|---|
| `401` even with a token | The token expired, or the backend and frontend use different Clerk projects or origins | Get a fresh token; check `CLERK_SECRET_KEY` and `CLERK_AUTHORIZED_PARTIES` |
| `KeyError: 'CLERK_SECRET_KEY'` | It's missing from `.env` | Add it and restart uvicorn |
| `column users.... does not exist` | The `ALTER TABLE` lines weren't run | Run them (step 1) |
| `window.Clerk is undefined` | You're not signed in, or not on the frontend tab | Sign in at http://localhost:3000 first |
| `500` on `GET /users/<id>` | The user's email failed validation | Report it; auto-created users should use `@users.setuai.dev` |
