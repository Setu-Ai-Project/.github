# SetuAI Mid-Project Audit: Detailed Findings & Risk Register

**Audit Date:** 2026-10-15  
**Audit Standard:** Formal Architecture, Security, QA & Integration Inspection  
**Location:** `docs/audit/FINDINGS.md`

---

## Severity Summary

| Severity | Count | Summary |
|---|---|---|
| **CRITICAL** | 3 | Absence of CI/CD pipelines; Missing Backend Submissions & Progression API; Database schema evolution failure |
| **HIGH** | 3 | AI Research air-gap with Backend; Hardcoded frontend mock switches masking integration gap; Missing Mentor Mode views |
| **MEDIUM** | 3 | Missing badge evaluation logic in `award_xp`; Brand token deviation in `AskDoubtForm`; In-memory SQLite test disparity with Postgres |
| **LOW** | 2 | Deprecated shim `moderator.py` maintenance overhead; Incomplete dashboard page |
| **INFORMATIONAL**| 2 | Heavy AI dependencies memory footprint; Next.js 16 / Clerk Core 3 API changes |

---

## 1. Critical Severity Findings

### FINDING-CRIT-01: Zero Automated CI/CD Pipelines
- **Severity:** Critical
- **Category:** Infrastructure & DevOps
- **Affected Path:** Entire repository (`.github/` root)
- **Description:**  
  Although the Git repository is named `.github`, there is no `.github/workflows/` directory. No continuous integration pipeline exists to automatically run `npm test`, `npx tsc --noEmit`, `npm run lint`, or `python -m pytest` when pull requests are opened or merged.
- **Root Cause:**  
  Teams relied on local manual test execution before opening PRs without automated server-side enforcement.
- **Impact:**  
  Code can be merged with broken imports, syntax errors, or regression bugs without detection. In fact, `node_modules` and virtual environments are missing from local workspaces, meaning developers cannot verify tests without local environment setup.
- **Remediation:**  
  Create GitHub Actions workflows:
  - `.github/workflows/frontend-ci.yml`: runs `npm ci`, `npx tsc --noEmit`, `npm run lint`, `npx vitest run`.
  - `.github/workflows/backend-ci.yml`: runs `pip install -r requirements.txt`, `pytest -v`.
  - `.github/workflows/ai-research-ci.yml`: runs `python verify_moderation.py`, `python verify_step1.py`.

---

### FINDING-CRIT-02: Backend Submissions & Progression APIs Missing in Code
- **Severity:** Critical
- **Category:** Cross-Team Integration & API Completeness
- **Affected Path:** `backend/routes/`, `frontend/gamifiedsetu/api/submissionApi.ts`
- **Description:**  
  The Frontend team completed Step 6 (Wave 3) Submission UI against a mock contract expecting `POST /api/submissions`. However, the Backend team's Wave 3 tickets (Tasks 1–3 in `backend/B2 ticket text`) were never merged into `main`. Neither `models/submission.py`, `services/verifier.py`, nor `routes/submissions.py` exist in the backend. Furthermore, Backend Step 5.4 (`POST /challenges/{id}/complete`) was never implemented, leaving the atomic `services/progression.py` progression engine unreachable.
- **Root Cause:**  
  Asynchronous development across separate workspaces where Frontend built against mock data while Backend feature branches were delayed or unmerged.
- **Impact:**  
  Learners cannot submit answers to challenges or earn verified XP. If `USE_MOCK` is toggled to `false`, the frontend immediately breaks with HTTP 404 errors.
- **Remediation:**  
  1. Merge or implement Backend Wave 3 Tasks 1–3 (`models/submission.py`, `services/verifier.py`, `routes/submissions.py`).
  2. Implement Step 5.4 challenge completion route handler that invokes `services.progression.award_xp`.
  3. Wire frontend `submissionApi.ts` to backend via `NEXT_PUBLIC_API_URL`.

---

### FINDING-CRIT-03: Database Schema Evolution Failure (No Alembic Migrations)
- **Severity:** Critical
- **Category:** Database Architecture & Reliability
- **Affected Path:** `backend/main.py`, `backend/database.py`, `backend/models/user.py`
- **Description:**  
  The backend relies entirely on `SQLModel.metadata.create_all(engine)` executed during FastAPI startup in `main.py`. As noted in `backend/PROGRESSION_ENGINE_HANDOVER.md`, `create_all()` creates missing tables but **cannot add new columns to pre-existing tables**. In Step 5.2, two new non-null columns (`total_xp: int = 0` and `level: int = 1`) were added to the `User` model. On any existing PostgreSQL instance, subsequent queries fail with `UndefinedColumn: column users.total_xp does not exist`.
- **Root Cause:**  
  Absence of a database migration tool (such as Alembic) in the initial architecture.
- **Impact:**  
  Deployments to persistent environments (staging, production) will fail immediately upon startup or user query unless raw SQL `ALTER TABLE` statements are manually run by developers.
- **Remediation:**  
  1. Initialize Alembic in `backend/` (`alembic init migrations`).
  2. Configure `env.py` to import `SQLModel.metadata`.
  3. Generate a baseline migration script capturing all current models.
  4. Ensure all deployment and startup scripts run `alembic upgrade head`.

---

## 2. High Severity Findings

### FINDING-HIGH-01: AI Research Modules Air-Gapped from Backend
- **Severity:** High
- **Category:** Architecture & System Integration
- **Affected Path:** `Ai Research/` and `backend/`
- **Description:**  
  The AI Research team has developed image generation, CLIP similarity scoring, Claude prompt-feedback categorization, and safety moderation. However, there is zero integration with the FastAPI backend. No service adapter, shared library, or internal HTTP/gRPC microservice interface connects `backend/` to `Ai Research/`.
- **Root Cause:**  
  Step 1 of the AI Research plan explicitly decoupled modules for isolated experimentation, but the handoff phase (Step 6 / Handoff) has not yet been executed.
- **Impact:**  
  The core value proposition of Level 2 (Recreate the Image Prompt Lab) and automated moderation cannot function in the web application.
- **Remediation:**  
  Define an architectural contract: expose a unified Python function `evaluate_submission(prompt: str, reference_image: bytes) -> dict` in a shared package or as a dedicated lightweight microservice that FastAPI calls asynchronously.

---

### FINDING-HIGH-02: Hardcoded Mock Switches Concealing Integration Failure
- **Severity:** High
- **Category:** Frontend Configuration & Maintainability
- **Affected Path:** `frontend/gamifiedsetu/api/submissionApi.ts`, `frontend/gamifiedsetu/api/doubtApi.ts`
- **Description:**  
  Both API integration modules in the frontend hardcode `export const USE_MOCK = true;` without checking environment variables:
  ```ts
  // api/submissionApi.ts line 13:
  export const USE_MOCK = true;
  ```
- **Root Cause:**  
  Frontend tickets permitted mock stubs to allow parallel frontend development before backend readiness.
- **Impact:**  
  Build configurations cannot dynamically toggle between mock and live APIs without editing code files. Production bundles risk shipping with mock endpoints permanently activated.
- **Remediation:**  
  Refactor all mock flags to environment variables with fallback:
  ```ts
  export const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK !== "false";
  ```

---

### FINDING-HIGH-03: Missing Step 7 Mentor Mode Screens (`ModeSwitch`, `MentorDashboard`)
- **Severity:** High
- **Category:** Feature Completeness
- **Affected Path:** `frontend/gamifiedsetu/`
- **Description:**  
  The frontend merged Step 7 Task 11 (`DoubtCard`) and Task 13 (`AskDoubtForm`, `MyDoubts`), but Step 7 Task 12 (`ModeContext`, `ModeSwitch`, `/dev/mentor`) and Task 14 (`MentorDashboard`) are completely missing from `main`.
- **Root Cause:**  
  Branch `feature/step7-task12-mode-switch` and `feature/step7-task14-mentor-dashboard` were never finished or merged.
- **Impact:**  
  Learners can submit doubts to `localStorage`, but there is no mechanism or UI for mentors to view, filter, or reply to doubts. The mentor side of the loop is broken.
- **Remediation:**  
  Implement `context/ModeContext.tsx`, `app/components/mentor-mode/ModeSwitch.tsx`, `MentorDashboard.tsx`, and `/dev/mentor/page.tsx` as specified in `Tickets Task2`.

---

## 3. Medium Severity Findings

### FINDING-MED-01: Badge Evaluation Unimplemented in Progression Service
- **Severity:** Medium
- **Category:** Backend Logic & Gamification
- **Affected Path:** `backend/services/progression.py` (lines 118 & 138)
- **Description:**  
  While `models/badge.py` and `models/user_badge.py` were created in Step 5.2, `award_xp` in `services/progression.py` returns a hardcoded empty list for unlocked badges:
  ```python
  # Line 138:
  "badges_unlocked": [],
  ```
- **Root Cause:**  
  Deferred to Step 5.6 in the backend progression roadmap.
- **Impact:**  
  Learners earn XP and level up, but never receive badges or milestone rewards upon completing challenges.
- **Remediation:**  
  Implement Step 5.6 badge evaluation rules checking `rule_type` (`challenges_completed`, `xp_threshold`, `level_reached`) and insert corresponding `UserBadge` records within the XP award transaction.

---

### FINDING-MED-02: Brand Token Deviation in `AskDoubtForm.tsx`
- **Severity:** Medium
- **Category:** UI/UX & Design Consistency
- **Affected Path:** `frontend/gamifiedsetu/app/components/mentor-mode/AskDoubtForm.tsx`
- **Description:**  
  `AskDoubtForm.tsx` uses standard Tailwind utilities (`border border-gray-200 bg-white shadow-sm`) instead of SetuAI's established brand tokens:
  - Specified: `border-4 border-ink bg-white shadow-[8px_8px_0_#172A32] rounded-2xl`
  - Implemented: `border border-gray-200 bg-white p-5 shadow-sm rounded-xl`
- **Root Cause:**  
  Developer oversight during Step 7 Task 13 implementation.
- **Impact:**  
  Visual discontinuity between the doubt form and adjacent components (`SubmissionPanel`, `NovaBanner`, `DoubtCard`).
- **Remediation:**  
  Update `AskDoubtForm.tsx` class names to conform to brand design tokens.

---

### FINDING-MED-03: In-Memory SQLite Test Suite Masks PostgreSQL Concurrency & Types
- **Severity:** Medium
- **Category:** QA & Test Validity
- **Affected Path:** `backend/tests/conftest.py`
- **Description:**  
  All 54 backend tests run against an in-memory SQLite database (`sqlite://` with `StaticPool`). SQLite handles transactions, constraints, and data types (such as JSON columns and concurrency locks) differently than PostgreSQL.
- **Root Cause:**  
  SQLite was adopted for fast, zero-dependency local testing.
- **Impact:**  
  Concurrency race conditions in `award_xp` and JSON column mutations on PostgreSQL may behave differently in production than in tests.
- **Remediation:**  
  Introduce testcontainers or a local dockerized PostgreSQL test runner in CI to run integration tests against real PostgreSQL.

---

## 4. Low Severity Findings

### FINDING-LOW-01: Deprecated Shim `moderator.py` Maintenance Overhead
- **Severity:** Low
- **Category:** Technical Debt
- **Affected Path:** `Ai Research/moderator.py`
- **Description:**  
  `moderator.py` was deprecated in favor of `moderation.py` during Wave 2. It currently issues a runtime `DeprecationWarning` and forwards calls.
- **Impact:**  
  Minor maintenance clutter.
- **Remediation:**  
  Update all internal references in `Ai Research` to import directly from `moderation.py` and schedule `moderator.py` for removal in the next cleanup sprint.

---

### FINDING-LOW-02: Dashboard Page is a Static Stub
- **Severity:** Low
- **Category:** Frontend Completeness
- **Affected Path:** `frontend/gamifiedsetu/app/dashboard/page.tsx`
- **Description:**  
  `app/dashboard/page.tsx` hardcodes "Level 1 · 0 XP" with a static progress bar and a "Your dashboard is coming soon" banner. It does not fetch data from the user session or backend progress API.
- **Impact:**  
  Learners who finish onboarding land on an empty, non-functional dashboard screen.
- **Remediation:**  
  Wire `dashboard/page.tsx` to read user XP and levels from backend or local session state.
