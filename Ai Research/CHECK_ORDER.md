# SetuAI — Challenge Attempt Check Order & Cost Gatekeeping

> **Design Goal**: Ensure that any invalid, over-limit, or harmful submission is caught and stopped immediately so blocked requests cost **almost nothing ($0.00)**.

---

## 📌 The Core Philosophy: "Cheapest Check First"

Every single attempt by a learner goes through a strict sequence of 7 steps.

We organize these steps from **free and fastest** to **paid and heaviest**. If a request fails any step, execution halts immediately. By placing free local checks before expensive external API calls, we ensure that:
1. Students who hit their daily limit consume **zero dollars**.
2. Unsafe or inappropriate prompts are blocked for **zero dollars**.
3. We only spend money generating images when we know the request is safe and permitted.

---

## 📊 The 7-Step Check Pipeline

| Step | Check / Action | Handled By | Costs Money? | Why It Must Be at This Exact Position |
|---|---|---|---|---|
| **1** | **Daily Limit Check** | `limits.py` | **$0.00 (Free)** | **Cheapest & Fastest Gate**: Checks in-memory/database counter. If the student has used all their tries for the day, we stop here. Zero API calls are made. |
| **2** | **Moderation Word List** | `moderation.py` | **$0.00 (Free)** | **Instant Local Safety Gate**: Checks regex patterns, PII, self-harm keywords, and entity masks (like "blood orange") in under 1 millisecond on the local CPU. Eliminates obvious bad prompts without touching an AI model. |
| **3** | **AI Prompt Moderation** | `moderation.check_prompt` | **Fraction of a cent** (~$0.0001) | **Lightweight AI Gate**: An LLM judge checks subtle or ambiguous prompts that passed the word list. It costs a tiny fraction of an image, saving us from paying for an expensive image if the prompt is subtly harmful. |
| **4** | **Image Generation** | `image_generator.py` | **Paid** (~$0.03 per image) | **The Heavy Paid Call**: This is the single most expensive part of the entire attempt. We only trigger this once the prompt has passed all quota and safety gates. |
| **5** | **AI Image Moderation** | `moderation.check_image` | **$0.00 to minimal** | **Post-Generation Safety Trap**: Catches provider filter flags (such as content-filter blocks). If the generated picture is deemed unsafe by the provider, we catch it before analyzing it. |
| **6** | **Similarity Scoring** | `similarity_scorer.py` | **$0.00 (Free)** | **Local Vector Comparison**: Uses our local CLIP model running on the server to measure similarity between target and generated images. Generates the numeric score needed for feedback. |
| **7** | **Feedback Generation** | `feedback_generator.py` | **Minimal** (~$0.0005) | **Final Pedagogical Step**: Calls the text model to produce mascot Bug's encouraging advice based on the prompt and similarity score. Only runs if the full image pipeline succeeded. |

---

## 💡 Why Order Matters (Scenario Breakdown)

### Scenario A: A student exceeds their daily attempts
- **Processed through**: Step 1 only.
- **Outcome**: Blocked instantly by `limits.py` with a friendly mascot message.
- **Total API cost**: **$0.000000** (100% saved).

### Scenario B: A student types a profanity or unsafe prompt
- **Processed through**: Steps 1 and 2.
- **Outcome**: Step 1 passes (within quota); Step 2 detects unsafe words and blocks immediately.
- **Total API cost**: **$0.000000** (100% saved).

### Scenario C: A student types a cleverly disguised harmful prompt
- **Processed through**: Steps 1, 2, and 3.
- **Outcome**: Step 1 passes; Step 2 passes; Step 3 AI judge catches the nuance and blocks.
- **Total API cost**: **~$0.0001** (Saved the full $0.03 image generation fee).

### Scenario D: A valid, creative prompt
- **Processed through**: All 7 steps in sequence.
- **Outcome**: Image is generated, scored, and friendly feedback is returned.
- **Total API cost**: Normal attempt cost logged in `cost_log.jsonl`.
