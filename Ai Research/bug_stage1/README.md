# Bug Stage 1 - static mistake detection (SetuAI, Step 4)

Bug checks a learner's answer against a list of **human-tagged** mistake phrases.
If one is found, Bug shows the tagged explanation and hint. If not, Bug stays quiet.
Plain text matching. **No AI calls.** Python standard library only.

> ⚠️ `sample_mistakes.json` is **FAKE placeholder data**. Do not ship it to learners.

## Files
| File | What it is |
|---|---|
| `bug_stage1.py` | `load_mistakes`, `validate_mistakes`, `find_mistakes` |
| `sample_mistakes.json` | 5 FAKE tagged mistakes (to be replaced by the real list) |
| `mistake_checks.py` | Should-warn, should-stay-quiet, robustness and language checks |
| `NOTES.md` | Results, design decisions, known limitations, open questions |
| `PROJECT_CONTEXT.md` | Rules given to the Antigravity agent |

## Use it
```python
from bug_stage1 import load_mistakes, validate_mistakes, find_mistakes

mistakes = load_mistakes("sample_mistakes.json")
assert not validate_mistakes(mistakes)
find_mistakes("draw something nice", mistakes)
# -> [{"id": "m1-vague-words", "matched": "something nice",
#      "explanation": "...", "fix_hint": "..."}]
```
- `find_mistakes` **never raises**. On any error it returns `[]` (no warning), because a
  wrong warning is worse than none.
- `load_mistakes` **does** raise on a missing or broken file, so data problems are loud for the team.

## Connecting it to the rest of SetuAI
```python
found = find_mistakes(learner_text, mistakes)
# Log it (R2 log_store.py) - every Bug detection must be logged (SOP section 7)
log_submission(..., bug_mistake_ids=[w["id"] for w in found])
# Show it (BugTooltip: a message + dismiss) - proposed message:
messages = [f'{w["explanation"]} {w["fix_hint"]}' for w in found]
```

## Run the checks
```
python mistake_checks.py
```
It must end with `VERIFY PASSED`. The "known limits" section is printed for information only.

## Data format
```json
{
  "module": "module-1",
  "mistakes": [
    {
      "id": "m1-vague-words",
      "phrase": "something nice",
      "variants": ["something cool"],
      "explanation": "Kind sentence Bug says (written by humans).",
      "fix_hint": "Nudge toward the fix without giving the answer."
    }
  ]
}
```
Use phrases of **2 or more words**. The validator warns about one-word phrases.

## How it matches
1. Normalize both sides: lowercase, remove apostrophes, turn punctuation and symbols into
   spaces, collapse spaces. Letters of **every** script are kept, including Hindi vowel signs.
2. Match the whole phrase only. "nice" never matches inside "nicest".
3. Negation guard: skip a match if not / never / no / don't / can't / won't / isn't /
   shouldn't / avoid / without appears in the 3 words before it.
4. At most one warning per mistake.

## Swapping in the real list (Part E)
1. Add the real file (e.g. `mistakes_module1.json`). Keep the fake one for tests.
2. Run `validate_mistakes` on it. Send problems back to the tagging owner; don't silently edit their list.
3. Review every phrase for being specific enough.
4. Add 3 should-stay-quiet answers per real mistake to `mistake_checks.py`.
5. Only when everything passes is the list ready for Backend. No code changes needed.

## Known limits
See `NOTES.md`. In short, the negation guard ignores sentence boundaries, and short common
variants can cause false alarms. Stage 2 (AI detection) is intentionally **not** started.
