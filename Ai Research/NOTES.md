# Feedback Classifier - Notes (R1 Wave 2)

## Date
23 October 2026

## What I built
- feedback.py: classifies why a learner’s prompt was weak
- Uses Groq (llama-3.1-8b-instant) temporarily instead of Anthropic
- Returns 1–3 categories from the fixed list with short tips
- Safe fallback: returns {"ok": False, "categories": []} on errors

## Fixed Categories
- missing_details
- poor_specificity
- incorrect_composition
- ambiguous_instructions
- missing_style_information

## Test Results
- feedback_checks.py: 10 test cases
- eval_skeleton.py + eval_set.csv: 10/10 matches (100%)

## Key Observations
- Vague prompts correctly receive missing_details / poor_specificity / ambiguous_instructions
- High score prompts (0.88) receive only light feedback
- Empty prompt correctly returns ok: False
- Prompt injection attempt was handled safely
- Composition detection improved after adding a better example

## Known Limits
- Currently using Groq instead of Anthropic (temporary)
- Need to switch back to Anthropic when the real API key is available
- More test cases can still be added later

## Next Steps
- Share final category list again if needed
- Prepare for Step 6 full evaluation
- Switch to Anthropic when possible
