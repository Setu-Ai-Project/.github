# SetuAI Task Tracker & Reconstructed Inventory

**Audit Date:** 2026-10-15  
**Audit Standard:** Reconstructed from Git Commits, PRs, Tickets, and Codebase Evidence  
**Location:** `docs/audit/TASK_TRACKER.md`

### Status Glossary:
- **Verified Complete**: Code implemented, verified with tests, merged into `main`.
- **Implemented but Unverified**: Code exists on `main`, but lacks comprehensive automated test verification or live verification.
- **Partially Implemented**: Partial code or placeholder exists; core capabilities remain unfinished.
- **Not Found / Not Implemented**: Task specified in project tickets or roadmap, but completely absent from repository.
- **Blocked**: Cannot proceed due to unmet dependencies or architectural roadblocks.
- **Needs Investigation**: Code exhibits anomalies, conflicting implementations, or indeterminate status.

---

## 1. Frontend Team Tasks (`frontend/gamifiedsetu/`)

| Task ID | Feature Description | Evidence & Files | Status | Test Evidence | Dependencies & Blockers | Remaining Work | Recommended Action |
|---|---|---|---|---|---|---|---|
| `FE-TASK-00` | Wave 3 Test Setup & Vitest Framework | `vitest.config.mts`, `vitest.setup.ts`, `tests/smoke.test.tsx`, `package.json` | **Verified Complete** | `tests/smoke.test.tsx` written | None | None | Keep configuration unchanged. |
| `FE-TASK-01` | Clerk SDK Install & Environment Setup | `package.json` (`@clerk/nextjs`), `proxy.ts`, `.env.example` | **Verified Complete** | Builds without Clerk setup error | None | Populate real Clerk API keys in local `.env` | Document developer onboarding key acquisition. |
| `FE-TASK-02` | ClerkProvider & App Shell Layout | `app/layout.tsx` (wraps `<ClerkProvider>`, `<Show when="signed-in">`, `<UserButton>`) | **Verified Complete** | Component renders with Player Sans and Clerk headers | `FE-TASK-01` | None | None. |
| `FE-TASK-03` | Branded Landing Page & Auth Screens | `app/page.tsx`, `app/sign-up/[[...sign-up]]/page.tsx`, `app/sign-in/[[...sign-in]]/page.tsx` | **Verified Complete** | Custom interactive form with `useSignIn`/`useSignUp` hooks | `FE-TASK-01`, `FE-TASK-02` | Complete email verification flow when Clerk enforces OTP | Verify password reset and error banners under live credentials. |
| `FE-TASK-04` | NovaBanner Mascot Component | `app/components/mascots/NovaBanner.tsx`, `app/dev/nova-test/page.tsx` | **Verified Complete** | Visual test route in `/dev/nova-test` | `motion` package | None | Ready for inclusion in challenge levels. |
| `FE-TASK-05` | BugTooltip Mascot Component | `app/components/mascots/BugTooltip.tsx`, `app/dev/bug-test/page.tsx` | **Verified Complete** | Visual test route in `/dev/bug-test` | `motion` package | None | Ready for contextual hint display. |
| `FE-TASK-06` | SparkCard Mascot Component | `app/components/mascots/SparkCard.tsx`, `app/dev/spark-test/page.tsx` | **Verified Complete** | Visual test route in `/dev/spark-test` | `motion` package | None | Ready for term definitions display. |
| `FE-TASK-07` | ByteStrip Mascot Component | `app/components/mascots/ByteStrip.tsx`, `app/dev/byte-test/page.tsx` | **Verified Complete** | Visual test route in `/dev/byte-test` | `motion` package | None | Ready for stat and timeline call-outs. |
| `FE-TASK-08` | Submission Types, Mock API & StatusBadge | `types/submission.ts`, `api/mockSubmission.ts`, `api/submissionApi.ts`, `app/components/submission/StatusBadge.tsx` | **Verified Complete** | `api/mockSubmission.test.ts`, `api/submissionApi.test.ts`, `StatusBadge.test.tsx` | `FE-TASK-00` | None | Toggle `USE_MOCK = false` once backend endpoint lands. |
| `FE-TASK-09` | SubmitButton, FeedbackList & useSubmission Hook | `app/components/submission/SubmitButton.tsx`, `FeedbackList.tsx`, `hooks/useSubmission.ts` | **Verified Complete** | `SubmitButton.test.tsx`, `FeedbackList.test.tsx`, `useSubmission.test.ts` | `FE-TASK-08` | None | Ready for integration into challenge screens. |
| `FE-TASK-10` | SubmissionPanel Component & Demo Page | `app/components/submission/SubmissionPanel.tsx`, `app/dev/submission/page.tsx` | **Verified Complete** | `SubmissionPanel.test.tsx`, visual demo at `/dev/submission` | `FE-TASK-08`, `FE-TASK-09` | Connect real challenge ID and server XP response | Wire to real challenge runner. |
| `FE-TASK-11` | Doubt Types, Mock Queue & DoubtCard | `types/doubt.ts`, `api/mockDoubtApi.ts`, `api/doubtApi.ts`, `app/components/mentor-mode/DoubtCard.tsx` | **Verified Complete** | `mockDoubtApi.test.ts`, `doubtApi.test.ts`, `DoubtCard.test.tsx` | `FE-TASK-00` | None | Ready for mentor dashboard. |
| `FE-TASK-13` | Learner Doubt UI (`AskDoubtForm` & `MyDoubts`) | `app/components/mentor-mode/AskDoubtForm.tsx`, `MyDoubts.tsx`, `app/dev/learner-doubts-test/page.tsx` | **Verified Complete** | `AskDoubtForm.test.tsx`, `MyDoubts.test.tsx`, dev page | `FE-TASK-11` | Fix styling inconsistency in `AskDoubtForm.tsx` (use brand tokens) | Refactor `border-gray-200` to `border-ink` and add drop shadow. |
| `FE-TASK-12` | ModeContext, ModeSwitch & `/dev/mentor` Page | Ticket specified in `Tickets Task2`; files `context/ModeContext.tsx`, `ModeSwitch.tsx`, `/dev/mentor/page.tsx` | **Not Found / Not Implemented** | None in repository | `FE-TASK-11`, `FE-TASK-13` | Entire task missing from branch/repo | Create branch `feature/step7-task12-mode-switch` and build per ticket. |
| `FE-TASK-14` | MentorDashboard & Queue Response Management | Ticket specified in `Tickets Task2`; file `app/components/mentor-mode/MentorDashboard.tsx` | **Not Found / Not Implemented** | None in repository | `FE-TASK-11`, `FE-TASK-12` | Entire mentor view missing | Implement MentorDashboard tabbed view and reply inputs. |
| `FE-LEVELS-1-7` | 7 Curriculum Interactive Levels (Swipe-sort, Timeline, Case Studies, Canvas) | Described in `README.md` | **Not Found / Not Implemented** | None | Component library (`FE-TASK-04` through `FE-TASK-10`) | All 7 levels unbuilt | Begin Level 6 (AI Entrepreneurship) flagship level. |

---

## 2. Backend Team Tasks (`backend/`)

| Task ID | Feature Description | Evidence & Files | Status | Test Evidence | Dependencies & Blockers | Remaining Work | Recommended Action |
|---|---|---|---|---|---|---|---|
| `BE-CORE-01` | Backend Skeleton & Database Connection | `database.py`, `main.py`, `security.py`, `requirements.txt` | **Verified Complete** | `tests/test_main.py` | None | None | Replace placeholder DB URL with clean env default. |
| `BE-USER-01` | User Model & CRUD Endpoints | `models/user.py`, `routes/user.py` | **Verified Complete** | `tests/test_user.py` | `BE-CORE-01` | None | Maintained and active. |
| `BE-AUTH-01` | Clerk Authentication Middleware & User Sync | `middleware/auth.py` (`get_current_user_id`, `get_current_user`) | **Verified Complete** | `tests/test_auth.py`, `tests/test_current_user.py` | `BE-USER-01` | None | Integrate with upcoming challenge and progress routes. |
| `BE-CURR-01` | Curriculum Core Entities (Ticket A) | `models/{module,sub_module,progress}.py`, `routes/{module,sub_module,progress}.py` | **Verified Complete** | `tests/test_{module,sub_module,progress}.py` | `BE-CORE-01` | None | Maintained and active. |
| `BE-CURR-02` | Mascot Content Entities (Ticket B) | `models/{bug_trigger,spark_term,byte_fact}.py`, routes | **Verified Complete** | `tests/test_{bug_trigger,spark_term,byte_fact}.py` | `BE-CURR-01` | None | Maintained and active. |
| `BE-CURR-03` | Curriculum Seed Script & App Wiring (Ticket C) | `scripts/seed.py`, `main.py` routers inclusion | **Verified Complete** | `seed.py` successfully populates database | `BE-CURR-01`, `BE-CURR-02` | Add challenges and badges to seed script | Extend `seed.py` to seed `challenges` and `badges`. |
| `BE-PROG-01` | XP Thresholds & Pure Level Math (Step 5.1) | `config/progression_rules.py` | **Verified Complete** | 11 tests in `tests/test_progression_rules.py` | None | None | Reused by `services/progression.py`. |
| `BE-PROG-02` | Progression Database Models (Step 5.2) | `models/{challenge,completed_challenge,badge,user_badge,certificate}.py` | **Verified Complete** | `tests/test_challenge_models.py`, `tests/test_progression_models.py` | `BE-PROG-01` | Add migration scripts for persistent PostgreSQL | Run `ALTER TABLE users ADD COLUMN total_xp...` on persistent DBs. |
| `BE-PROG-03` | Atomic XP Award Service (Step 5.3) | `services/progression.py` (`award_xp`) | **Verified Complete** | 8 tests in `tests/test_award_xp.py` | `BE-PROG-01`, `BE-PROG-02` | None | Ready for route handler integration. |
| `BE-STEP6-01` | Submission Model & Challenge Rules (Wave 3 BE 1) | Ticket specified in `backend/B2 ticket text`; `models/submission.py` | **Not Found / Not Implemented** | None | `BE-PROG-02` | Entire model missing | Implement `models/submission.py` and register in `main.py`. |
| `BE-STEP6-02` | Answer Verifier Service & Contract (Wave 3 BE 2) | Ticket specified in `backend/B2 ticket text`; `services/verifier.py` | **Not Found / Not Implemented** | None | `BE-STEP6-01` | Verification rules logic | Implement `verify_answer(answer_text, rules)`. |
| `BE-STEP6-03` | Submissions API Route (Wave 3 BE 3) | Ticket specified in `backend/B2 ticket text`; `routes/submissions.py` | **Not Found / Not Implemented** | None | `BE-STEP6-01`, `BE-STEP6-02`, `BE-PROG-03` | Route endpoint missing | Implement `POST /submissions` and wire to `award_xp`. |
| `BE-PROG-04` | Challenge Completion API Route (Step 5.4) | Handover specified `POST /challenges/{id}/complete` | **Not Found / Not Implemented** | None | `BE-PROG-03` | Endpoint missing | Implement route handler connecting frontend to `award_xp`. |
| `BE-PROG-06` | Badge Evaluation Engine (Step 5.6) | Placeholder in `services/progression.py` (`badges_unlocked: []`) | **Partially Implemented** | None | `BE-PROG-03` | Rule evaluation logic | Implement rule checker evaluating XP, level, and challenge counts. |
| `BE-PROG-07` | WebSocket Progression Notifications (Step 5.7) | Handover specified `notify_progress` WebSocket | **Not Found / Not Implemented** | None | `BE-PROG-03` | Full WebSocket system | Implement FastAPI WebSocket route or defer to polling. |
| `BE-PROG-08` | Progress Polling Endpoint (Step 5.8) | Handover specified `GET /users/me/progress` | **Not Found / Not Implemented** | None | `BE-PROG-03` | Aggregation endpoint | Implement summary endpoint returning totals, badges, certificates. |
| `BE-MENTOR-01` | Mentor Doubts API & Storage | Frontend expects `GET/POST /api/doubts` | **Not Found / Not Implemented** | None | `BE-USER-01` | Entire backend subsystem missing | Design `Doubt` model, create migration, and implement routes. |

---

## 3. UI/UX Design Team Tasks (`UI-UX Files/`)

| Task ID | Feature Description | Evidence & Files | Status | Test Evidence | Dependencies & Blockers | Remaining Work | Recommended Action |
|---|---|---|---|---|---|---|---|
| `UI-AUTH-01` | Auth Screen Interactive Prototypes | `UI-UX Files/index.html`, `preview.html`, `Onboarding Beginner Guide/setuai-auth-page.html` | **Verified Complete** | Standalone HTML files render in browser | None | None | Baseline established. |
| `UI-ONB-01` | 4-Screen Onboarding Tour | `UI-UX Files/Onboarding Beginner Guide/setuai-onboarding.html` | **Verified Complete** | Renders 4 tour steps with Spark mascot | None | None | Baseline established. |
| `UI-DASH-01` | Dashboard Stub Design | `UI-UX Files/Onboarding Beginner Guide/setuai-dashboard.html` | **Verified Complete** | Renders Level/XP bar | None | None | Baseline established. |
| `UI-ASSETS-01` | Vector SVG Mascot Library | `UI-UX Files/SetuAI mascots/mascots svg/{Bug,Byte,Nova,Spark}/` | **Verified Complete** | All 4 mascots across 5 poses exist | None | None | Fully imported to frontend `public/mascots`. |
| `UI-FONTS-01` | Typography Distribution (Player Sans Mono) | `UI-UX Files/Onboarding Beginner Guide/fonts/` | **Verified Complete** | TTF and OTF files verified | None | None | Active in frontend. |
| `UI-LEVELS-DESIGN`| Level 1–7 Gameplay Interaction Specs | Described in `README.md` | **Not Found / Not Implemented** | None | Product specification | Wireframes and visual mocks for all 7 levels | Create interactive prototypes for Level 1 Swipe-Sort & Level 6 Lean Canvas. |
| `UI-SUBMISSION-DESIGN`| Submission Panel & Feedback Card Mockup | Implemented in frontend | **Implemented but Unverified** | Frontend implementation exists | None | Formal design specification in `UI-UX Files/` | Archive component design spec in `UI-UX Files/`. |
| `UI-MENTOR-DESIGN` | Mentor Mode & Doubt Card Mockup | Implemented in frontend | **Implemented but Unverified** | Frontend implementation exists | None | Formal design specification in `UI-UX Files/` | Archive mentor mode design spec in `UI-UX Files/`. |

---

## 4. AI Research Team Tasks (`Ai Research/`)

| Task ID | Feature Description | Evidence & Files | Status | Test Evidence | Dependencies & Blockers | Remaining Work | Recommended Action |
|---|---|---|---|---|---|---|---|
| `AI-MOD-01` | Text-to-Image Generation Module | `Ai Research/image_generator.py` | **Verified Complete** | Self-tests in file, fallback placeholder generation | Stability AI API Key (optional) | Connect to backend challenge endpoint | Maintain mock mode for offline dev. |
| `AI-MOD-02` | CLIP Similarity Scorer | `Ai Research/similarity_scorer.py` | **Verified Complete** | Self-tests in file, cosine math verified | PyTorch, Transformers | Connect to backend verification service | Tune threshold on real learner dataset. |
| `AI-MOD-03` | Anthropic Claude Feedback Generator | `Ai Research/feedback_generator.py` | **Verified Complete** | Self-tests in file, 5 category classification | Anthropic API Key (optional) | Connect to backend verification service | Maintain mock mode for zero-cost testing. |
| `AI-SAFE-01` | Wave 1 Safety & Content Moderation | `Ai Research/moderator.py` | **Verified Complete** | Verified in `test_moderation.py` | None | Deprecated in favor of `moderation.py` | Keep as backward-compatible shim. |
| `AI-SAFE-02` | Wave 2 Consolidated Moderation & Entity Masking | `Ai Research/moderation.py` | **Verified Complete** | Verified in `verify_moderation.py`, `benchmark_moderation.py` | None | None | Production-ready safety engine. |
| `AI-EXP-01` | Experimental Multi-Modal CLIP Moderator | `Ai Research/experimental_clip_moderator.py` | **Implemented but Unverified** | Standalone experimental script | PyTorch, Transformers | Production benchmark evaluation | Keep in experimental status. |
| `AI-TEST-01` | Verification & Benchmark Test Suites | `verify_step1.py`, `verify_moderation.py`, `benchmark_moderation.py` | **Verified Complete** | Verification scripts execute without failures | None | None | Run as part of AI Research release gate. |
| `AI-INT-01` | Backend Integration Wrapper (`evaluate_submission`) | Roadmap Step 6 / Handoff | **Not Found / Not Implemented** | None | `AI-MOD-01` through `AI-MOD-03`, `AI-SAFE-02` | Python export wrapper or HTTP microservice | Expose clean `evaluate_submission()` function for backend ingestion. |
| `AI-EVAL-01` | Benchmark Evaluation Dataset | Roadmap Step 6 | **Not Found / Not Implemented** | None | Curriculum prompt definitions | 15–20 benchmark prompt/image pairs | Curate standardized test evaluation set. |
