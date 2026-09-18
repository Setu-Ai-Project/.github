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

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** (Python 3.14+ supported)
- **Git**
- Terminal access

### 2. Activate Virtual Environment & Install Dependencies
From this directory (`Ai Research /`):

```bash
# Activate the existing virtual environment
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
*(Note: If you do not have API keys yet, all modules and verification scripts run in mock/fallback mode seamlessly.)*

---

## 🧪 Testing Each Module Individually

You can run each module directly to see how it works in isolation:

### Test Module 1 (Image Generator)
```bash
python image_generator.py
```
*Expected result*: Generates an image (or mock placeholder if no API key is set) and saves `test_generated_image.png`.

### Test Module 2 (CLIP Similarity Scorer)
```bash
python similarity_scorer.py
```
*Expected result*: Loads the CLIP model, compares identical images (scores ~1.0) and different images (scores significantly lower), and checks threshold status.

### Test Module 3 (Feedback Classifier)
```bash
python feedback_generator.py
```
*Expected result*: Formats Bug's prompt template and returns selected categories from the fixed list along with encouraging feedback text.

---

## ✅ Running the Step 1 Verification Suite

Run the full verification script to confirm all three modules satisfy Step 1 requirements:

```bash
python verify_step1.py
```

---

## 📁 Project Structure

```
Ai Research /
├── .env.example            # Environment configuration template
├── .gitignore              # Files and directories ignored by Git
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation (this file)
├── image_generator.py      # Module 1: Text-to-Image generation
├── similarity_scorer.py    # Module 2: CLIP similarity scoring & embeddings
├── feedback_generator.py   # Module 3: Anthropic prompt feedback classifier
└── verify_step1.py         # Step 1 verification test suite
```

---

## 🗺️ What Comes Next?

According to the **AI Research Development Plan**:
- **Step 2**: Deep-dive into reference image caching and similarity threshold tuning.
- **Step 3**: Refine prompt templates for feedback classification and share with the UI/UX team for mascot voice alignment.
- **Step 4**: Implement Bug's mistake detection logic (Stage 1: static keywords).
- **Step 5**: Personalized hint generation.
- **Step 6**: Build evaluation set (15–20 benchmark prompts and images).
- **Handoff**: Expose clean Python functions (`evaluate_submission`) to the FastAPI backend.
