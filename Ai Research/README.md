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
