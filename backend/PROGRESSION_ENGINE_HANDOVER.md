# SetuAI Progression Engine: Team Handover Guide (Steps 5.1–5.3)

**Author:** Pair B1  
**Target Audience:** Teammates working on Steps 5.4–5.9 (Pair B1 & Pair B2)  
**Location:** `.github/backend/PROGRESSION_ENGINE_HANDOVER.md`  
**Date:** October 2026  

---

## 1. Project Overview

The **Progression Engine** is the core backend subsystem responsible for gamification and learner achievement in SetuAI. It tracks:
* **Experience Points (XP)** and **Levels**: Awarding XP for completing challenges and calculating when a learner levels up.
* **Challenge Completions**: Idempotently recording that a user completed a specific challenge so XP is never awarded twice for the same challenge.
* **Badges & User Badges**: Milestone rewards earned for achieving progression feats (e.g., reaching XP thresholds or challenge counts).
* **Certificates**: Formal records granted upon completing entire curriculum modules.

This system is designed to be atomic, reliable, and decoupled from external services.

---

## 2. Work Completed: Steps 5.1–5.3

### Step 5.1 — XP Thresholds & Pure Level Calculation Rules
* **Location:** `config/progression_rules.py`
* **What was built:** A pure Python module (zero database or network dependencies) defining:
  * `LEVEL_THRESHOLDS = {1: 0, 2: 100, 3: 250, 4: 500, 5: 1000}`
  * `MAX_LEVEL = 5`
  * `level_for_xp(total_xp: int) -> int`: Returns the highest eligible level (treating negative values safely as 0).
  * `xp_to_next_level(total_xp: int) -> int`: Returns the XP remaining until the next level, or `0` if at/above `MAX_LEVEL`.
* **Testing:** 11 parameterized and boundary tests in `tests/test_progression_rules.py`.

### Step 5.2 — Database Models & Schema Definition
* **Location:** `models/`
* **What was built:** SQLModel table definitions matching the project conventions:
  * `User` (`models/user.py`): Added persistent `total_xp: int` (default `0`, non-null) and `level: int` (default `1`, non-null). `UserRead` includes these fields; `UserCreate` remains unchanged.
  * `Challenge` (`models/challenge.py`, table `challenges`): `id`, `sub_module_id` (FK `sub_modules.id`), `title`, `xp_reward` (default `50`).
  * `CompletedChallenge` (`models/completed_challenge.py`, table `completed_challenges`): `id`, `user_id` (FK `users.id`), `challenge_id` (FK `challenges.id`), `xp_awarded`, `completed_at`. Protected by `UniqueConstraint("user_id", "challenge_id", name="uq_user_completed_challenge")`.
  * `Badge` (`models/badge.py`, table `badges`): `id`, `slug` (unique, indexed), `name`, `description`, `rule_type`, `rule_value`.
  * `UserBadge` (`models/user_badge.py`, table `user_badges`): `id`, `user_id` (FK `users.id`), `badge_id` (FK `badges.id`), `awarded_at`, and `UniqueConstraint("user_id", "badge_id", name="uq_user_badge")`.
  * `Certificate` (`models/certificate.py`, table `certificates`): `id`, `user_id` (FK `users.id`), `module_id` (FK `modules.id`), `image_url`, `issued_at`, and `UniqueConstraint("user_id", "module_id", name="uq_user_module_certificate")`.
* **Registration:** All models are exported in `models/__init__.py` and imported into `main.py` so they register with `SQLModel.metadata.create_all(engine)`.
* **Testing:** Covered in `tests/test_challenge_models.py`, `tests/test_progression_models.py`, and `tests/test_user.py`.

### Step 5.3 — Atomic XP Award Service
* **Location:** `services/progression.py`
* **Public Signature:** `award_xp(user_id: int, challenge_id: int) -> dict`
* **What was built:** An atomic service function that manages its own database session and transaction. It validates IDs, verifies whether the challenge was already completed, increments user XP, recalculates the level using Step 5.1 rules, commits atomically, and handles concurrency collisions gracefully.
* **Testing:** 8 comprehensive tests in `tests/test_award_xp.py`.

---

## 3. File and Folder Guide

The backend uses a **flat structure** directly under `.github/backend/`. **Do NOT create an `app/` directory or move files.**

```text
.github/backend/
├── config/
│   ├── __init__.py
│   └── progression_rules.py     # Pure XP/level thresholds and calculation functions (Step 5.1)
├── models/
│   ├── __init__.py              # Re-exports all models
│   ├── user.py                  # User, UserRead (contains total_xp and level)
│   ├── challenge.py             # Challenge model and schemas
│   ├── completed_challenge.py   # CompletedChallenge model (completed_challenges table)
│   ├── badge.py                 # Badge model (badges table)
│   ├── user_badge.py            # UserBadge model (user_badges table)
│   ├── certificate.py           # Certificate model (certificates table)
│   ├── module.py                # Curriculum module model
│   ├── sub_module.py            # Curriculum sub-module model
│   └── progress.py              # Existing module-level Progress model (DO NOT MODIFY)
├── services/
│   ├── __init__.py              # Services package init
│   └── progression.py           # award_xp service, UserNotFound, ChallengeNotFound (Step 5.3)
├── routes/                      # API route handlers (Step 5.4 endpoint will live here)
├── tests/
│   ├── conftest.py              # In-memory SQLite fixtures (session, client)
│   ├── test_progression_rules.py# Unit tests for Step 5.1 calculation math
│   ├── test_challenge_models.py # Unit tests for Challenge & CompletedChallenge constraints
│   ├── test_progression_models.py# Unit tests for Badge, UserBadge, Certificate constraints
│   └── test_award_xp.py         # Unit tests for award_xp service
├── database.py                  # Engine and get_session dependency
└── main.py                      # FastAPI app entry point & metadata.create_all lifespan
```

---

## 4. How the Progression Flow Works

```text
[Caller / Route Handler]
       │
       ▼ calls award_xp(user_id, challenge_id)
[services/progression.py]
       │
       ├─► 1. Lookup user in DB (raises UserNotFound if missing)
       ├─► 2. Lookup challenge in DB (raises ChallengeNotFound if missing)
       ├─► 3. Check completed_challenges for (user_id, challenge_id)
       │       │
       │       ├── ALREADY EXISTS:
       │       │   └── Return { "already_completed": True, "xp_awarded": 0, ... }
       │       │
       │       └── NOT COMPLETED YET:
       │           ├─► 4. Calculate new_total_xp = user.total_xp + challenge.xp_reward
       │           ├─► 5. Calculate new_level = level_for_xp(new_total_xp)
       │           ├─► 6. Stage CompletedChallenge record & update User fields
       │           ├─► 7. Commit Transaction (session.commit())
       │           │       │
       │           │       ├── IntegrityError (Concurrent duplicate collision):
       │           │       │   ├── Rollback session
       │           │       │   ├── Verify if (user_id, challenge_id) was written by other worker
       │           │       │   └── Return { "already_completed": True, "xp_awarded": 0, ... }
       │           │       │
       │           │       └── SUCCESS:
       │           │           └── Return 10-field contract dictionary
```

*Note on Unimplemented Behavior:*
* Badge evaluation is currently a placeholder (`badges_unlocked: []`). Step 5.6 will plug in the badge evaluation logic before transaction commit.

---

## 5. Service Response Schema

Calling `award_xp(user_id, challenge_id)` returns a dictionary matching this exact structure:

```python
{
    "user_id": 12,
    "challenge_id": 7,
    "xp_awarded": 50,
    "total_xp": 230,
    "level": 3,
    "previous_level": 2,
    "leveled_up": True,
    "xp_to_next_level": 70,
    "badges_unlocked": [],
    "already_completed": False
}
```

### Field Definitions:
* `user_id` (`int`): Local integer ID of the user (`users.id`).
* `challenge_id` (`int`): Local integer ID of the challenge (`challenges.id`).
* `xp_awarded` (`int`): XP credited for this action (always `0` if `already_completed` is `True`).
* `total_xp` (`int`): User's updated cumulative XP.
* `level` (`int`): User's current level after applying the award.
* `previous_level` (`int`): User's level prior to this award.
* `leveled_up` (`bool`): `True` if `level > previous_level`, otherwise `False`.
* `xp_to_next_level` (`int`): XP remaining to achieve `level + 1` (returns `0` if at `MAX_LEVEL = 5`).
* `badges_unlocked` (`list[dict]`): Badges unlocked by this completion. **Currently returns an empty list `[]` as a placeholder pending Step 5.6.**
* `already_completed` (`bool`): `True` if the user had already completed this challenge; `False` if this was their first completion.

---

## 6. Duplicate Completion and Error Handling

1. **Database Constraint:**
   `CompletedChallenge` enforces uniqueness via `UniqueConstraint("user_id", "challenge_id", name="uq_user_completed_challenge")`. It is impossible for duplicate completion rows to exist in the database.
2. **Pre-Check:**
   The service queries for an existing completion first. If present, it returns an idempotent response (`already_completed=True`, `xp_awarded=0`) without making database mutations.
3. **Concurrency Race Protection:**
   If two requests pass the pre-check concurrently, one commits and the second raises SQLAlchemy's `IntegrityError`. The service catches `IntegrityError` only around `session.commit()`, immediately rolls back, verifies whether the completion record now exists in the database, re-fetches the persisted user stats, and returns the idempotent response. Unrelated integrity errors are re-raised.
   *(Test limitation note: The unit test simulates this collision sequentially; multi-threaded concurrent load testing against persistent PostgreSQL has not been run).*
4. **Exceptions Raised:**
   * `UserNotFound`: When `user_id` is not found in `users`.
   * `ChallengeNotFound`: When `challenge_id` is not found in `challenges`.

---

## 7. Tests and Verification

All tests run in-memory against SQLite (`sqlite://` with `StaticPool` in `tests/conftest.py`):

| Test File | Focus | Test Count |
| :--- | :--- | :---: |
| `tests/test_progression_rules.py` | Step 5.1 level math, thresholds, boundaries, negative XP | 11 |
| `tests/test_challenge_models.py` | Step 5.2 Challenge and CompletedChallenge persistence and uniqueness | 5 |
| `tests/test_progression_models.py` | Step 5.2 Badge, UserBadge, Certificate models and constraints | 3 |
| `tests/test_award_xp.py` | Step 5.3 first completion, repeat submission, level up, exceptions, collision | 8 |
| `tests/test_user.py` | Default `total_xp=0` and `level=1` on creation and read | 3 |
| *Pre-existing tests* | Auth, main, module, sub_module, progress, mascot tests | 24 |

**Verification Command:**
```powershell
.\venv\Scripts\python -m pytest -v
```
**Status:** **54 passed, 0 failed** (as verified during Step 5.3 implementation).

---

## 8. Remaining Work for Teammates (Steps 5.4–5.9)

Based on the assignment task outline, the remaining tasks are:

* **Step 5.4 — Challenge Completion API Route (Pair B1 / B2):**
  * Create endpoint `POST /challenges/{id}/complete` (or `POST /complete-challenge`).
  * Authenticate the caller, resolve the authenticated identity to local `user.id`, invoke `award_xp(user_id, challenge_id)`, catch `ChallengeNotFound` / `UserNotFound`, and return HTTP 404 if appropriate.
* **Step 5.5 — Document Response Contract:**
  * Document the API schema and error contracts for frontend integration.
* **Step 5.6 — Badge Evaluation & Seeding (Pair B1):**
  * Implement badge rules checking `rule_type` (`"challenges_completed"`, `"xp_threshold"`, `"level_reached"`).
  * Insert new `UserBadge` rows inside the XP-award transaction.
  * Populate `badges_unlocked` in the `award_xp` return dictionary with `[{"slug": ..., "name": ...}]`.
  * Seed badge definitions in `scripts/seed.py`.
* **Step 5.7 — WebSocket Progression Notifications & Progress Polling (Pair B2):**
  * Trigger `notify_progress(result)` with `xp_awarded`, `leveled_up`, `level`, etc.
  * Provide `GET /progress` or `GET /users/me/progress` returning overall totals, badges, and certificates.
* **Step 5.8 / 5.9 — Certificate Issuance & Asset Storage (Pair B2):**
  * Issue certificates upon module completion and record in `certificates`. Ensure asset upload failures do not roll back successful progression.

---

## 9. Integration Notes and Cautions

1. **Keep the Flat Directory Structure:**
   * Use `services/...`, `models/...`, `routes/...`, and `config/...`. Do **not** prefix imports with `app.`.
2. **Reuse `award_xp`:**
   * Do not write custom XP awarding or leveling logic in route handlers. Call `services.progression.award_xp`.
3. **Clerk Identity vs. Local Integer User ID:**
   * `auth.get_current_user_id` returns a Clerk string (`"user_2xxx"`). The database `User.id` is an `int`. The route handler must resolve the Clerk identity to the integer `User.id` before calling `award_xp(user_id: int, ...)`.
4. **PostgreSQL Database Schema Warning:**
   * `SQLModel.metadata.create_all(engine)` automatically creates new tables (`challenges`, `completed_challenges`, `badges`, etc.).
   * **`create_all()` will NOT add new columns to an existing `users` table.** If working against an existing local PostgreSQL database, the following manual SQL update must be applied:
     ```sql
     ALTER TABLE users ADD COLUMN IF NOT EXISTS total_xp INTEGER NOT NULL DEFAULT 0;
     ALTER TABLE users ADD COLUMN IF NOT EXISTS level INTEGER NOT NULL DEFAULT 1;
     ```
   *(No database commands should be executed without team alignment; tests in SQLite handle this automatically).*
5. **Challenge Verification Security:**
   * `award_xp` does **not** evaluate whether a user's submitted quiz/code answers were correct. It purely awards progression for a completed challenge. Verifying the challenge submission payload is the responsibility of the route handler / verification engine in Step 5.4.

---

## 10. Recommended Integration Sequence

1. **Import existing service:**
   ```python
   from services.progression import award_xp, ChallengeNotFound, UserNotFound
   ```
2. **Build the API route in `routes/`** (e.g. `routes/progression.py` or `routes/challenge.py`).
3. **Register the router** in `main.py` (`app.include_router(...)`).
4. **Run focused pytest tests:**
   ```powershell
   .\venv\Scripts\python -m pytest tests/test_your_new_route.py -v
   ```
5. **Run the full test suite** to ensure 0 regressions:
   ```powershell
   .\venv\Scripts\python -m pytest -v
   ```

---

## 11. Handover Checklist

- [x] **Step 5.1:** Pure progression rules and math (`config/progression_rules.py`).
- [x] **Step 5.2:** Models for `User` (XP/level), `Challenge`, `CompletedChallenge`, `Badge`, `UserBadge`, `Certificate`.
- [x] **Step 5.3:** Atomic `award_xp` service with idempotency and duplicate collision handling (`services/progression.py`).
- [x] **Contracts:** `docs/contracts/award_xp.md` agreed and adhered to.
- [x] **Test Suite:** 54 passing tests with 0 regressions.
- [ ] **Step 5.4:** Route endpoint for completing challenges (`POST ...`).
- [ ] **Step 5.6:** Badge unlock evaluation rules in `award_xp`.
- [ ] **Step 5.7:** WebSocket push notification hook (`notify_progress`).
- [ ] **Step 5.8:** Progress polling endpoint (`GET /progress/me`).
- [ ] **Step 5.9:** Certificate generation and storage.
- [ ] **PostgreSQL Sync:** Run manual `ALTER TABLE users ADD COLUMN ...` on persistent PostgreSQL databases if not using a fresh DB.
