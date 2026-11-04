# SetuAI — AI Research Plan

> **Live Working Research Plan & Specification Document**  
> **Workspace Location:** `Ai Research/` (`/Users/adityapathak/Desktop/.github/Ai Research`)  
> **Directives:** All AI research work, experiments, models, and scripts stay strictly inside the `Ai Research/` folder. Every directive, idea, and feedback item provided by the user is documented and tracked in this living plan.

---

## 📌 1. Project Overview & Research Objectives

SetuAI is an interactive, gamified AI learning platform designed to teach kids how AI works through practical challenges. The primary AI research scope focuses on the **"Recreate the Image" Prompt Lab challenge** (Level 2: Prompt Engineering) and supporting AI features (moderation, safety guardrails, similarity scoring, and mascot coaching).

### Core Research Goals:
1. **Model Decoupling & Modularity**: Keep generation, scoring, moderation, and feedback classification modular and independently testable before end-to-end integration.
2. **Kid-Safe AI (Safety & Moderation)**: Provide a multi-layer defense-in-depth safety engine tailored for educational AI environments.
3. **Objective Evaluation**: Accurately evaluate learner prompt quality through multi-modal similarity analysis (CLIP cosine similarity) without relying on single black-box LLMs.
4. **Pedagogical Feedback**: Translate numerical similarities and prompt gaps into friendly, actionable guidance delivered by mascot **Bug**.

---

## 🧩 2. Architecture & Modules Overview

The AI engine in `Ai Research/` is organized into independent, swappable components:

| Module / Component | Script | Functionality | Current Status |
|---|---|---|---|
| **Module 1: Text-to-Image Generation** | [`image_generator.py`](image_generator.py) | Calls Stability AI Core API (with built-in fallback/mock mode for zero-cost testing). Captures provider safety signals. | ✅ Step 1 Complete |
| **Module 2: Similarity Scorer** | [`similarity_scorer.py`](similarity_scorer.py) | Local CLIP (`openai/clip-vit-base-patch32`) computing cosine similarity between learner & target images; embedding caching. | ✅ Step 1 Complete |
| **Module 3: Feedback Classifier** | [`feedback_generator.py`](feedback_generator.py) | Anthropic Claude API (with deterministic fallback). Classifies issues into 5 fixed categories in mascot Bug's voice. | ✅ Step 1 Complete |
| **Safety & Moderation** | [`moderation.py`](moderation.py), [`moderator.py`](moderator.py) | 4-layer defense: input screening (<1ms regex/heuristics), provider traps, output guardrails, and educational coaching. | ✅ Benchmark Validated |
| **Verification & Benchmarks** | [`verify_step1.py`](verify_step1.py), [`verify_moderation.py`](verify_moderation.py), [`benchmark_moderation.py`](benchmark_moderation.py) | Comprehensive test suites testing correctness, safety intercepts, and edge cases. | ✅ Passing |

---

## 🗺️ 3. Development Roadmap & Milestones

- [x] **Step 1: Baseline Architecture & Modular Setup**
  - Implement standalone image generator, CLIP scorer, and feedback classifier with mock fallbacks.
  - Establish verification suite ([`verify_step1.py`](verify_step1.py)).
- [x] **Wave 1: Safety & Defense-in-Depth Moderation**
  - 4-layer moderation engine ([`moderator.py`](moderator.py)).
  - Comprehensive safety benchmark test suite ([`benchmark_moderation.py`](benchmark_moderation.py)).
- [ ] **Step 2: Reference Image Caching & Threshold Tuning**
  - Pre-generate and cache vector embeddings for challenge target images.
  - Calibrate dynamic thresholding based on prompt complexity (0.75 – 0.85 ranges).
- [ ] **Step 3: Feedback Classification & Mascot Prompt Tuning**
  - Refine prompt templates for Bug's mascot voice.
  - Map prompt delta analysis to the 5 standard categories:
    1. `missing details`
    2. `poor specificity`
    3. `incorrect composition`
    4. `ambiguous instructions`
    5. `missing style information`
- [ ] **Step 4: Mistake Detection Logic**
  - Stage 1: Static keyword & heuristic detection.
  - Stage 2: Semantic contrast analysis between target description and learner prompt.
- [ ] **Step 5: Personalized Hint Generation**
  - Progressive hint ladder (Level 1: General nudge → Level 2: Target property highlight → Level 3: Concrete keyword suggestion).
- [ ] **Step 6: Evaluation & Golden Benchmark Set**
  - Construct 15–20 reference test challenges with curated reference images and edge prompts.
- [ ] **Step 8: Cost Logging, Pricing Model & Rate Limits (Wave 2)**
  - Zero-guessing rule: enforce reading prices dynamically from `prices.json`.
  - Logging (`cost_log.py`, `cost_log.jsonl`): privacy-first logging of paid calls (tokens, cost) with zero child PII.
  - Analytics & Cost Model (`analyze_log.py`, `cost_model.py`): attempt cost estimation model and log reporting.
  - Daily Limits & Guardrails (`limits_config.json`, `limits.py`, `limits_checks.py`): pre-flight limits on attempts/hints checked before any paid call.
  - Pipeline Contract (`CHECK_ORDER.md`): strict check order documentation.
- [ ] **Backend Integration & Handoff**
  - Expose unified `evaluate_submission()` interface to FastAPI backend.

---

## 📝 4. User Directives & Inputs Log

*Every requirement, constraint, and instruction communicated by the user is recorded here.*

| Timestamp | Directive / Input | Impacted Area / Implementation Note | Status |
|---|---|---|---|
| Initial Setup | Everything communicated by user must be recorded inside the AI Research Plan. | Maintained in this file ([`AI_RESEARCH_PLAN.md`](AI_RESEARCH_PLAN.md)). Updated on every request. | Active |
| Initial Setup | All work must be conducted strictly inside the `Ai Research/` folder. | All code edits, new scripts, data, and tests are restricted to `/Users/adityapathak/Desktop/.github/Ai Research`. | Active |
| Step 8 Setup | Append `cost_log.jsonl` to `.gitignore`; append Wave 2 Step 8 to `PROJECT_CONTEXT.md`; create `NOTES.md` with decisions log, price sources, and backend questions. | `cost_log.jsonl` appended to `.gitignore`. | In Progress |
| Step 8 Setup | Create `prices.json` with exact zero values only (`claude_judge`, `image_generation`). Never invent/guess prices. | Created in [`prices.json`](prices.json). | Completed |
| Step 8 Setup | Create `cost_log.py` with `estimate_cost` & `log_call`, reading `prices.json` and writing to `cost_log.jsonl`. No prompt/PII logging. | Created in [`cost_log.py`](cost_log.py) & tested. | Completed |
| Step 8 Setup | Hook `log_call` into `moderation.py` inside `_ask_claude` for `claude_judge` moderation calls without logging prompt text. | Added `_ask_claude` and `log_call` import to [`moderation.py`](moderation.py). | Completed |
| Step 8 Setup | Run `moderation_checks.py` to populate `cost_log.jsonl` with API call records. | Created [`moderation_checks.py`](moderation_checks.py) & executed. | Completed |
| Step 8 Setup | Create `analyze_log.py` to aggregate calls, avg input/output tokens, and cost by feature with empty/missing file handling. | Created in [`analyze_log.py`](analyze_log.py) & verified. | Completed |
| Step 8 Setup | Create `cost_model.py` with `TOKENS` dict `(0, 0)` and `cost_per_attempt()` breaking down all 5 parts and total. | Created in [`cost_model.py`](cost_model.py) & tested. | Completed |
| Step 8 Setup | Add `daily_cost_per_user` (worst-case), `total_daily_budget` (expected), and worst-case limit comparison table to `cost_model.py`. | Implemented & verified in [`cost_model.py`](cost_model.py). | Completed |
| Step 8 Setup | Create `limits_config.json` (drafts: 15 attempts, 5 hints, UTC boundary) and `limits.py` (`LimitResult`, `check_and_record`). | Created in [`limits_config.json`](limits_config.json) & [`limits.py`](limits.py). | Completed |
| Step 8 Setup | Create `limits_checks.py` (loops limit+2 attempts, verifies block, user isolation, and action isolation). | Created in [`limits_checks.py`](limits_checks.py) & verified (VERIFY PASSED). | Completed |
| Step 8 Setup | Create `CHECK_ORDER.md` with table and plain-text cost gatekeeping pipeline explanation (no code). | Created in [`CHECK_ORDER.md`](CHECK_ORDER.md). | Completed |
| Step 8 Setup | Draft Backend coordination message: draft limits (15 attempts, 5 hints), cost driver placeholder, check order, and 4 open questions (UTC vs IST, moderation consumption, failed gen consumption, mascot copy). | Documented in [`AI_RESEARCH_PLAN.md`](AI_RESEARCH_PLAN.md). | Completed |
| Step 8 Setup | Update `README.md` with Step 8 files, script execution guides, pricing instructions, draft limits, and prototype limits without deleting existing content. | Updated in [`README.md`](README.md). | Completed |

---

## 🔬 5. Active Research & Next Immediate Steps

1. Fill official pricing values in [`prices.json`](prices.json) after checking official provider pages.
2. Record check dates in [`NOTES.md`](NOTES.md).
3. Proceed with logging and rate limits implementation (`cost_log.py`, `limits.py`, etc.).

