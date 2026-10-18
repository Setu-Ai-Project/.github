# SetuAI Technology Stack Audit

**Date:** 2026-10-15  
**Audit Standard:** Actual Source Code, Manifests, Lockfiles & Configuration Only (No Assumptions)  
**Location:** `docs/audit/TECH_STACK.md`

---

## 1. Frontend Technology Stack (`frontend/gamifiedsetu/`)

### Core Framework & Runtime
- **Next.js**: `16.3.5`
  - *Manifest Evidence:* `package.json` line 15 (`"next": "16.3.5"`), `package-lock.json`.
  - *Usage:* Web application shell, App Router architecture (`app/` layout, pages, and dev test routes).
  - *Implementation Status:* Fully implemented. Note: Next.js 16 conventions are followed (e.g. `proxy.ts` replaces deprecated `middleware.ts`).
- **React & React DOM**: `19.2.8`
  - *Manifest Evidence:* `package.json` lines 16–17 (`"react": "19.2.8"`, `"react-dom": "19.2.8"`).
  - *Usage:* Server and client component rendering (`"use client"` directives present on interactive elements).
  - *Implementation Status:* Fully implemented.
- **TypeScript**: `^5` (devDependencies)
  - *Manifest Evidence:* `package.json` line 33, `tsconfig.json`.
  - *Configuration:* Strict mode enabled (`"strict": true`), `@/*` path mapping configured to root.
  - *Implementation Status:* Fully implemented across all `.ts` and `.tsx` files.

### Styling & Design System
- **Tailwind CSS**: `^4.0` (`@tailwindcss/postcss: ^4`, `tailwindcss: ^4`)
  - *Manifest Evidence:* `package.json` lines 20 & 32, `postcss.config.mjs`.
  - *Usage:* CSS styling with Tailwind v4 `@theme inline` block in `app/globals.css`.
  - *Theme Tokens Defined:*
    - `--color-cream`: `#f8f7f1`
    - `--color-ink`: `#172a32`
    - `--color-coral`: `#dc6f51`
    - `--color-tealpop`: `#85cec7`
    - `--color-taskgray`: `#6e6d6c`
    - Custom shadow token: `shadow-[8px_8px_0_#172A32]`, `shadow-[4px_4px_0_#172A32]`
  - *Implementation Status:* Implemented.
  - *Audit Finding:* Minor style deviation in `AskDoubtForm.tsx` where standard Tailwind gray utilities (`border-gray-200`) were used instead of `--color-ink`.
- **Typography (Player Sans Mono)**:
  - *Manifest Evidence:* `app/fonts/PlayerSansMono8x13-{Classic,Bold,Italic}.ttf`, loaded via `next/font/local` in `app/layout.tsx`.
  - *Usage:* Set as primary display font (`--font-display`).
  - *Implementation Status:* Fully implemented.

### Animations
- **Motion**: `^13.4.1`
  - *Manifest Evidence:* `package.json` line 14 (`"motion": "^13.4.1"`).
  - *Usage:* Replaces legacy `framer-motion`. Powers `AnimatePresence` and `motion.div` transitions in `NovaBanner`, `BugTooltip`, `SparkCard`, and `ByteStrip`.
  - *Implementation Status:* Implemented and active.

### Authentication & User Identity
- **Clerk Next.js SDK**: `^7.9.4` (`@clerk/nextjs`)
  - *Manifest Evidence:* `package.json` line 13.
  - *Usage:* `<ClerkProvider>` wraps root application in `app/layout.tsx`. Route protection via `proxy.ts`. Custom form sign-in and sign-up integration using `useSignIn()` and `useSignUp()` hooks in `app/page.tsx`. Dedicated catch-all routes at `app/sign-up/[[...sign-up]]/page.tsx` and `app/sign-in/[[...sign-in]]/page.tsx`. Header user avatar via `<UserButton />` and `<Show when="signed-in">`.
  - *Implementation Status:* Implemented.
  - *Audit Risk:* Clerk Core 3 (`^7.9.4`) intentionally throws errors if legacy `<SignedIn>` or `<SignedOut>` components are called. The codebase correctly uses `<Show when="signed-in">`.

### Testing Tools
- **Vitest & React Testing Library**:
  - *Manifest Evidence:* `vitest: ^4.1.11`, `@testing-library/react: ^16.3.3`, `@testing-library/jest-dom: ^7.0.1`, `@testing-library/user-event: ^14.6.7`, `jsdom: ^29.1.1`.
  - *Configuration:* `vitest.config.mts` with `jsdom` environment and `vitest.setup.ts`.
  - *Implementation Status:* Implemented with 14 unit test suites.
  - *Audit Limitation:* `node_modules` is not committed or pre-installed in the current working copy; cannot execute tests without package install.

---

## 2. Backend Technology Stack (`backend/`)

### Core API Framework & Runtime
- **Python**: System Python `3.14.7` detected; project documentation targets Python `3.11+`.
- **FastAPI**: `>=0.141.1`
  - *Manifest Evidence:* `backend/requirements.txt` line 1, imported in `main.py`.
  - *Usage:* REST API routing, lifespan database table initialization, dependency injection.
  - *Implementation Status:* Implemented with 7 route modules included in `main.py`.
- **Uvicorn**: `>=0.53.0`
  - *Manifest Evidence:* `backend/requirements.txt` line 2, `runbackend` script (`uvicorn main:app --reload`).
  - *Implementation Status:* Implemented as local development server.

### ORM, Schemas & Database
- **SQLModel**: `>=0.0.46`
  - *Manifest Evidence:* `backend/requirements.txt` line 3, `main.py`, `database.py`.
  - *Usage:* Combines SQLAlchemy 2.0 ORM with Pydantic v2 schemas across 12 models.
  - *Database Driver:* `psycopg2-binary >= 2.9.13`.
  - *Database URL:* Configured in `database.py` via `DATABASE_URL` environment variable.
  - *Fallback URL string:* `"postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/neuroteach_db"`.
  - *Implementation Status:* Models implemented and registered in `SQLModel.metadata.create_all(engine)`.
  - *Audit Critical Risk:* **No migration framework (Alembic) exists.** `SQLModel.metadata.create_all` only creates new tables; it never modifies existing tables. Adding `total_xp` and `level` to `User` will fail on existing PostgreSQL databases unless manually altered with raw SQL.

### Backend Authentication & Middleware
- **Clerk Backend API**: `>=7.0.0` (`clerk-backend-api`)
  - *Manifest Evidence:* `backend/requirements.txt` line 11, `middleware/auth.py`.
  - *Usage:* `authenticate_request` verifies JWT session tokens. `get_current_user_id` extracts `sub` claim. `get_current_user` creates or retrieves local integer `User` record mapped to `clerk_user_id`.
  - *Implementation Status:* Implemented and verified in `tests/test_auth.py` and `tests/test_current_user.py`.

### Security & Password Hashing
- **Passlib & Bcrypt**: `passlib[bcrypt] >= 1.7.4`, `bcrypt >= 4.0.0,<5.0.0`
  - *Manifest Evidence:* `backend/requirements.txt` lines 6–7, `security.py`.
  - *Usage:* Password hashing (`pwd_context = CryptContext(schemes=["bcrypt"])`). Used by seed script for demo user.
  - *Implementation Status:* Implemented.

### Testing Tools
- **pytest & HTTPX**: `pytest >= 8.0.0`, `httpx >= 0.27.0`
  - *Manifest Evidence:* `backend/requirements.txt` lines 9–10, `pytest.ini`, `tests/conftest.py`.
  - *Configuration:* In-memory SQLite database (`sqlite://` with `StaticPool`) enables isolated tests without a live PostgreSQL instance.
  - *Implementation Status:* 16 test files with 54 passing tests recorded in git history.

---

## 3. AI Research Technology Stack (`Ai Research/`)

### Deep Learning & Computer Vision
- **PyTorch**: `>=2.2.0` (`torch`)
  - *Manifest Evidence:* `Ai Research/requirements.txt` line 2.
  - *Usage:* Vector tensor calculations, device allocation (`cuda`, `mps`, or `cpu`).
- **Hugging Face Transformers**: `>=4.40.0` (`transformers`)
  - *Manifest Evidence:* `Ai Research/requirements.txt` line 3, `similarity_scorer.py`.
  - *Model:* `openai/clip-vit-base-patch32` (`CLIPProcessor`, `CLIPModel`).
  - *Usage:* Encodes images into 512-dimensional vector embeddings, computes normalized cosine similarity.
  - *Implementation Status:* Implemented with embedding caching and threshold logic (`0.80`).
- **Pillow**: `>=10.0.0` (`PIL`)
  - *Usage:* Image loading, format conversion, and mock image generation.

### Large Language Models & Prompt Engineering
- **Anthropic Claude Python SDK**: `>=0.25.0` (`anthropic`)
  - *Manifest Evidence:* `Ai Research/requirements.txt` line 7, `feedback_generator.py`.
  - *Model:* Claude 3 Sonnet / Haiku.
  - *Usage:* Evaluates prompt text and similarity scores against 5 fixed feedback categories (`missing details`, `poor specificity`, `incorrect composition`, `ambiguous instructions`, `missing style information`). Outputs structured JSON in Bug's mascot voice.
  - *Implementation Status:* Implemented with deterministic mock mode fallback.

### Image Generation API
- **Stability AI Core REST API**:
  - *Usage:* `image_generator.py` calls `https://api.stability.ai/v2beta/stable-image/generate/core` via `requests`.
  - *Implementation Status:* Implemented with fallback mock mode when `STABILITY_API_KEY` is omitted.

### Safety & Content Moderation
- **Custom Multi-Layer Moderation Engine**:
  - *File:* `Ai Research/moderation.py` (consolidated Wave 2 engine) and backward-compatible shim `Ai Research/moderator.py`.
  - *Techniques:*
    - Phase 1: Contextual Entity Masking (`mask_entities`) substituting benign compound nouns (`comic strip`, `blood orange`, `water gun`) with semantic tokens (`**COMIC**`, `**FRUIT**`, `**TOY**`) prior to evaluation.
    - Phase 2: Regex scanning for Violence/Guns, Sexual Content, Hate Speech, PII (Email, Phone, SSN), and Prompt Injections.
    - Phase 3: Crisis Support intervention for self-harm queries with live hotline resources.
    - Phase 4: Output guardrails sanitizing LLM responses.
  - *Implementation Status:* Implemented and verified via `verify_moderation.py` and `benchmark_moderation.py`.

---

## 4. UI/UX Design Stack (`UI-UX Files/`)

- **Interactive HTML5 / CSS3 Prototypes:**
  - `index.html` & `preview.html`: Standalone auth screen prototypes using CSS variables.
  - `Onboarding Beginner Guide/setuai-onboarding.html`: Multi-step onboarding guide.
  - `Onboarding Beginner Guide/setuai-dashboard.html`: Dashboard stub.
- **Vector Assets (SVG):**
  - Bug, Byte, Nova, and Spark in 5 standardized poses: `-mascot` (idle), `-appearing`, `-back`, `-celebrating`, `-dismissed`.
- **Typography:**
  - Player Sans Mono 8x13 and 8x8 font files in TTF and OTF formats.
- **Imagery:**
  - WebP pixel-art application logo (`setuai-logo.webp`).

---

## 5. Deployment, Infrastructure & CI/CD

- **Containerization (Docker):** **Absent.** No `Dockerfile` or `docker-compose.yml` present in repository.
- **CI/CD Pipelines:** **Absent.** No GitHub Actions workflow files exist (`.github/workflows/` does not exist).
- **Environment Management:** Provided via `.env.example` templates in `backend/`, `frontend/gamifiedsetu/`, and `Ai Research/`.
- **Cloud Infrastructure:** Not configured in code.

---

## 6. Compatibility & Technical Debt Summary

1. **Next.js 16 & Clerk Core 3 API Sensitivity:**
   Next.js 16 deprecated `middleware.ts` in favor of `proxy.ts`. Clerk 7.9.4 deprecated `<SignedIn>`/`<SignedOut>` in favor of `<Show>`. Any copy-paste from outdated documentation will cause runtime crashes.
2. **Heavy AI Dependencies vs Web Backend:**
   PyTorch and Hugging Face Transformers require gigabytes of disk space and high RAM. Attempting to bundle `Ai Research` into the same execution environment as `FastAPI` will bloat backend deployment containers.
3. **Absence of Database Migrations:**
   Without Alembic, schema changes will fail on any persistent database. A migration tool must be introduced before staging deployment.
4. **Hardcoded Mock Switches:**
   `USE_MOCK = true` is hardcoded across frontend adapters (`submissionApi.ts`, `doubtApi.ts`). A dynamic environment variable (`NEXT_PUBLIC_USE_MOCK`) should control this behavior.
