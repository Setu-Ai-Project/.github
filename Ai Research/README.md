# SetuAI – Feedback Classifier (Step 3)

## What it does
Takes a learner’s prompt and a similarity score, then returns 1–3 categories explaining why the prompt was weak, with short helpful tips.

## Main function
classify_feedback(prompt, score, target_description=None)

Returns:
{
  "ok": true/false,
  "categories": [
    {"id": "...", "label": "...", "tip": "..."}
  ]
}

## Fixed Categories
- missing_details
- poor_specificity
- incorrect_composition
- ambiguous_instructions
- missing_style_information

## How to run
1. Make sure you have a .env file with:
   GROQ_API_KEY=your_key_here

2. Install packages:
   pip install groq python-dotenv

3. Run the tests:
   python feedback_checks.py
   python eval_skeleton.py

## Current Status
- Working version using Groq (temporary)
- 10/10 match rate on evaluation set
- See NOTES.md for details

## Important
This version uses Groq instead of Anthropic. Switch back to Anthropic when the real API key is available.
# SetuAI — AI Research (Step 1: Model Selection & Setup)

Welcome to the AI Research workspace for **SetuAI** (Gamified AI Learning Platform).

This project implements the AI models and logic behind the **"Recreate the Image" Prompt Lab challenge** (Level 2: Prompt Engineering) and provides the core AI capabilities that will later connect to the backend and frontend.

---

## 📖 What This Project Does

In the Prompt Lab challenge, learners practice writing descriptive prompts to recreate a target image. Rather than using a single "black box" AI model to do everything, the system splits the task into three separate jobs:

1. **Generate an image** from the learner's text prompt.
2. **Compare** the learner's generated image to a reference image and calculate a numerical similarity score.
3. **Analyze** the prompt and score to produce helpful, encouraging feedback categorized into fixed, actionable areas.

> [!NOTE]
> **Step 1 Rule**: Per Step 1 of the *AI Research Development Plan*, these three modules are kept **completely separate** and are **not wired together yet**. Each module can be tested, swapped, and evaluated on its own.

---

## 🧩 The Three Modules Explained

### 1. `image_generator.py` (Module 1: Image Generation)
- **Job**: Takes a text prompt from the learner and calls an image-generation API (Stability AI Core API) to produce an image.
- **Inputs**: `prompt` (string, e.g. `"a cozy wooden treehouse at sunset"`), optional `output_path`.
- **Outputs**: Raw image bytes (PNG format).
- **Beginner-Friendly Feature**: Includes a built-in **mock mode**. If you don't have an active `STABILITY_API_KEY`, it automatically generates a labeled placeholder image so you can test code without incurring API costs.

### 2. `similarity_scorer.py` (Module 2: CLIP Similarity Scorer)
- **Job**: Uses a local open-source CLIP model (`openai/clip-vit-base-patch32` from Hugging Face) to convert images into numeric vector embeddings and calculates their **cosine similarity**.
- **Inputs**: Two images (file path, raw bytes, or PIL Image object).
- **Outputs**: A similarity score bounded between `0.0000` (completely different) and `1.0000` (identical).
- **Threshold Rule**: Includes `is_close_enough(score, threshold=0.80)` to check whether the submission meets the initial passing threshold (0.80).
- **Embedding Cache**: Automatically supports caching reference image embeddings so the same reference image isn't recomputed on every attempt.

### 3. `feedback_generator.py` (Module 3: Anthropic Feedback Classifier)
- **Job**: Calls the Anthropic Claude API to evaluate the learner's prompt and similarity score against the **5 approved feedback categories** defined in SOP-AI-001.
- **The 5 Fixed Categories**:
  - `missing details`
  - `poor specificity`
  - `incorrect composition`
  - `ambiguous instructions`
  - `missing style information`
- **Voice & Tone**: Speaks in **Bug's mascot voice** — friendly, encouraging, and supportive (never harsh, blunt, or mocking).
- **Outputs**: A clean Python dictionary:
  ```python
  {
      "similarity_score": 0.45,
      "categories": ["poor specificity", "missing style information"],
      "feedback_text": "Bug here! Great start! Try adding specific colors and an art style like watercolor to bring your image to life."
  }
  ```
- **Beginner-Friendly Feature**: Includes a **mock mode** that produces deterministic feedback if `ANTHROPIC_API_KEY` is not provided.

### 4. `moderator.py` (Track B2 Wave 1: Safety & Content Moderation)
- **Job**: Provides a 4-layer defense-in-depth safety engine tailored for educational AI learning environments for kids.
- **Layer 1 (Pre-Flight Input Screening)**: Scans learner prompts *before* costly external API calls. Detects profanity/toxicity, violence/weapons, sexual content, PII leakage (emails, phone numbers, SSNs), and prompt injection/jailbreak attempts.
- **Layer 2 (Provider Safety Signals)**: Actively catches Stability AI's `finish-reason: CONTENT_FILTERED` header and HTTP 400 moderation intercepts.
- **Layer 3 (Output Guardrails)**: Sanitizes LLM-generated feedback text to ensure no inappropriate language reaches the learner.
- **Layer 4 (Mascot Educational Intervention)**: Never shows scary technical errors (`403 Forbidden`). Instead, **Bug** delivers friendly, constructive coaching encouraging learners to rephrase positively.
- **Performance**: Instantaneous pre-flight screening (< 1ms per prompt).

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** (Python 3.13+ supported)
- **Git**
- Terminal access

### 2. Activate Virtual Environment & Install Dependencies
From this directory (`Ai Research /`):

```bash
# Activate the virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```

Open `.env` in your text editor and optionally add your API keys:
```env
STABILITY_API_KEY=your_stability_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLIP_MODEL_NAME=openai/clip-vit-base-patch32
```
*(Note: If you do not have API keys yet, all modules, moderation checks, and verification scripts run in mock/fallback mode seamlessly.)*

---

## 🧪 Testing Each Module Individually

You can run each module directly to see how it works in isolation:

### Test Module 1 (Image Generator + Safety Guardrails)
```bash
python image_generator.py
```
*Expected result*: Generates an image (or mock placeholder) for safe prompts, and cleanly blocks unsafe prompts with Bug's educational safety intervention.

### Test Module 2 (CLIP Similarity Scorer)
```bash
python similarity_scorer.py
```
*Expected result*: Loads the CLIP model, compares identical images (scores ~1.0) and different images (scores significantly lower), and checks threshold status.

### Test Module 3 (Feedback Classifier + Output Guardrails)
```bash
python feedback_generator.py
```
*Expected result*: Formats Bug's prompt template, sanitizes output text, and provides supportive guidance for both safe prompts and flagged prompts.

### Test Moderation Module (Track B2 Wave 1)
```bash
python moderator.py
```
*Expected result*: Runs self-tests on benign prompts, PII detection, prompt injection defense, harm categories, and output sanitization.

---

## ✅ Verification Test Suites

### 1. Safety & Moderation Suite (Track B2 Wave 1)
```bash
python verify_moderation.py
```
*Tests benign prompts, PII leakage, prompt injections, harm categories, image generator integration, feedback generator integration, and latency benchmarks (< 15ms).*

### 2. Step 1 Baseline Verification Suite
```bash
python verify_step1.py
```

---

## 📁 Project Structure

```
Ai Research /
├── .env.example            # Environment configuration template
├── .gitignore              # Files and directories ignored by Git (includes cost_log.jsonl)
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation (this file)
├── AI_RESEARCH_PLAN.md     # Live working research plan & user directives log
├── CHECK_ORDER.md          # 7-step fail-fast cost gatekeeping pipeline
├── prices.json             # Single source of truth for external API rates
├── cost_log.py             # Privacy-first paid API call logger & cost estimator
├── cost_log.jsonl          # Raw JSONL usage logs (git-ignored, zero PII)
├── analyze_log.py          # Summary reporter for API usage & spending by feature
├── cost_model.py           # Single-attempt and daily user cost projection formulas
├── limits_config.json      # Draft daily limits configuration (UTC boundary)
├── limits.py               # In-memory daily attempt & hint rate limiter prototype
├── limits_checks.py        # Boundary & user-isolation test suite for rate limits
├── moderator.py            # Backward-compatibility deprecation shim
├── moderation.py           # Wave 2 Consolidated Moderation (Entity masking & Claude judge hook)
├── moderation_checks.py    # Verification suite exercising moderation & logger
├── image_generator.py      # Module 1: Text-to-Image generation (with safety traps)
├── similarity_scorer.py    # Module 2: CLIP similarity scoring & embeddings
├── feedback_generator.py   # Module 3: Anthropic feedback (with output guardrails)
├── verify_moderation.py    # Wave 1 Safety & Moderation verification suite
└── verify_step1.py         # Step 1 baseline verification test suite
```

---

## 💰 Wave 2: Step 8 — Cost Modeling, Privacy-First Logging & Daily Limits

Step 8 introduces budget visibility, privacy-preserving API accounting, and early gatekeeping controls to ensure learner challenge attempts never produce unexpected cloud bills.

### 1. New Step 8 Files Overview
- **[`prices.json`](prices.json)**: The single source of truth for external model rates.
- **[`cost_log.py`](cost_log.py)**: Lightweight logging utility. Appends structured records to `cost_log.jsonl` with zero prompt strings, student names, or PII.
- **[`analyze_log.py`](analyze_log.py)**: Reads `cost_log.jsonl` and prints calls, average input/output tokens, and total cost grouped by feature.
- **[`cost_model.py`](cost_model.py)**: Mathematical breakdown of costs for ONE attempt, worst-case user spending, and platform budget projections.
- **[`limits_config.json`](limits_config.json)**: Configuration specifying daily attempt and hint allowances.
- **[`limits.py`](limits.py)**: In-memory rate limiter enforcing daily quotas before paid calls.
- **[`limits_checks.py`](limits_checks.py)**: Test runner verifying quota boundaries, user isolation, and action isolation.
- **[`CHECK_ORDER.md`](CHECK_ORDER.md)**: Architectural contract documenting the 7-step cheapest-first check pipeline.

---

### 2. How to Fill `prices.json`
`prices.json` initializes with `0.0` values so that no numbers are ever guessed:
```json
{
  "claude_judge": {
    "input_per_million": 0.0,
    "output_per_million": 0.0
  },
  "image_generation": {
    "per_image": 0.0
  },
  "_note": "FILL IN from the official pricing pages and write the date checked in NOTES.md"
}
```

To populate live prices:
1. **Claude Judge Rates**: Visit [Anthropic Pricing](https://www.anthropic.com/pricing). Locate the model configured in `feedback_generator.py` (e.g. Claude 3.5 Haiku or Sonnet) and input the price per 1M input and output tokens.
2. **Image Generation Rates**: Visit [Stability AI Platform Pricing](https://platform.stability.ai/pricing). Look up the per-generation fee for Stable Image Core (typically 3 credits = ~$0.03/image).
3. **Record Check Date**: Log the date and sources in `NOTES.md`.

---

### 3. How to Run the New Scripts

#### A. Analyze API Usage & Spending
```bash
python analyze_log.py
```
*Parses `cost_log.jsonl` and prints a formatted summary table. Gracefully informs if the log file is missing or empty.*

#### B. Run the Single-Attempt & Daily Cost Model
```bash
python cost_model.py
```
*Displays the cost parts for one attempt (moderation, image gen, similarity [$0 local], feedback) and prints a worst-case daily table for attempt limits 5, 10, 15, and 20.*

#### C. Run the Daily Limits Verification Suite
```bash
python limits_checks.py
```
*Simulates 17 attempts (15 + 2) for a test user, verifies attempt 16 and 17 are blocked with kind mascot messaging, and verifies user and hint isolation (`VERIFY PASSED`).*

#### D. Run Moderation Checks to Populate Cost Logs
```bash
python moderation_checks.py
```
*Runs core moderation checks and exercises the Claude judge hook to generate verifiable entries in `cost_log.jsonl`.*

---

### 4. Draft Usage Limits (Not Final)
The limits defined in `limits_config.json` are **DRAFTS** pending alignment with Backend:
- **Daily Prompt Attempts**: `15` tries per learner per day.
- **Daily Hints**: `5` hints per learner per day.
- **Day Boundary**: `UTC` calendar day reset.

---

### 5. Prototype Known Limitations
- **In-Memory State**: `limits.py` stores counts in memory. Counts reset when the script or server restarts.
- **Single Process**: In-memory counts do not synchronize across distributed servers or multi-worker deployments.
- **Backend Handoff**: The Backend team will store and enforce persistent, production-grade daily limits in the database/Redis as part of their Step 9 architecture.

---

## 🗺️ What Comes Next?

According to the **AI Research Development Plan**:
- **Step 2**: Deep-dive into reference image caching and similarity threshold tuning.
- **Step 3**: Refine prompt templates for feedback classification and share with the UI/UX team for mascot voice alignment.
- **Step 4**: Implement Bug's mistake detection logic (Stage 1: static keywords).
- **Step 5**: Personalized hint generation.
- **Step 6**: Build evaluation set (15–20 benchmark prompts and images).
- **Step 8**: Finalize pricing numbers in `prices.json` and align Step 9 rate limits with Backend.
- **Handoff**: Expose clean Python functions (`evaluate_submission`) to the FastAPI backend.

