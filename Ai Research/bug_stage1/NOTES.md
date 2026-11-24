# NOTES - Bug Stage 1 (Step 4)

## Results (D5), on FAKE data
- Should-warn: **12 / 12 pass**
- Should-stay-quiet: **24 / 24 pass** (at least 3 traps per mistake + general cases)
- Robustness (D3): all pass. Missing file, broken JSON, missing phrase, junk entries,
  10,000+ characters (~1 ms), punctuation only, emoji only, None, repeated phrase,
  two mistakes in one answer.
- Other languages: Hindi letters survive normalizing; Hindi phrases match as whole words.
- 6 known limitations remain (below). They are listed in `mistake_checks.py` → `KNOWN_LIMITS`.

## Changes from the guide's reference code (and why)
1. **Normalizer broke Hindi.** `re.sub(r"[^\w\s]", " ", text)` turned "लाल" into "ल ल",
   because Python's `\w` does not count Hindi vowel signs (matras) as letters.
   The guide's Hindi test only checked that Bug stays quiet, so it could not catch this.
   Fix: remove only characters Unicode labels as punctuation (P) or symbols (S).
2. **`\b` word boundaries fail after Hindi vowel signs** for the same reason.
   Fix: after normalizing, words are separated by single spaces, so the pattern uses
   "space or edge of text" as the boundary. It works in every script.
3. **One bad entry switched off the whole detector.** In the reference, an entry without
   `phrase` raised a KeyError inside the single try/except, so it returned `[]` for every
   answer. Fix: each mistake is checked in its own try/except; a bad entry is skipped.
4. **Only the first occurrence was checked.** "don't write something nice. ok, draw something
   nice" was missed because the first match was negated. Fix: check every occurrence and
   warn if any one is not negated.
5. **Validator** also catches: missing phrase, `variants` that is not a list, non-text
   phrases, missing `fix_hint`, entries that are not objects.
6. **load_mistakes** raises a clear error if the file has no `"mistakes": [...]` list.

## Known limitations (plain sentences)
| Example | What goes wrong | Fix type | Decision |
|---|---|---|---|
| "No, draw something nice" | Missed: "no" starts a new sentence but still counts as negation, because punctuation is removed before the 3-word check | Smarter guard (stop the window at sentence ends) | Accept for now. A miss is the safe kind of error |
| "I don't know, make it better" | Missed: "don't" belongs to "I don't know" | Same as above | Accept for now |
| "you know what? i mean a red dragon" | False alarm: removing the "?" joins "what" and "i mean" | Data: the phrase is fine, but a sentence-aware matcher would fix it | Flag to Step 6 eval |
| "a black and white photo with hardly any colour" | False alarm: "hardly" is not a negation word | Data or guard: add "hardly" to NEGATIONS, or tag "any colour you like" instead | Ask the curriculum owner |
| "a picnic basket with something good to eat inside" | False alarm: "something good" is normal English here | **Data**: drop the variant or make it longer ("draw something good") | Recommend removing the variant from the real list |
| "make it better by making the sky darker" | False alarm: the learner gave a specific instruction after the phrase | Data or accepted limit | Ask the curriculum owner whether this should warn |

**Pattern:** most false alarms come from short, common variants. As the guide says, it's
better to fix the data (longer, more specific phrases) than to add code tricks.

## Links to other work
- **R2 logging (Aditya, Wave 3):** `log_store.log_submission(..., bug_mistake_ids=...)` saves our
  ids comma-joined. Pass `[w["id"] for w in find_mistakes(...)]`. The validator now rejects ids
  that aren't lowercase letters, digits and hyphens, so the join can never break.
  (SOP section 7: every Bug detection must be logged.)
- **Frontend BugTooltip** expects "a message and a dismiss action" (Dev Plan, Linking to Frontend).
  Proposal: message = `explanation + " " + fix_hint`. Backend/Frontend to confirm; the shape stays
  the same when Stage 2 arrives.
- **Evaluation (SOP section 9):** 36 hand-labelled cases (12 warn, 24 quiet). That's above the 15-20 the
  SOP asks for. Results are in this file; attach them to the Pull Request.

## Open questions / blockers
- **SYNC 3:** who owns the content-tagging task, and when will the real list arrive? The Dev Plan
  says it's "covered in the Backend Development Plan", so ask Yatharth / the Backend lead.
- Format agreed with tagging owner and Backend? (B2) → *to confirm*
- BugTooltip message format (above) → *to confirm with Frontend/Design*
- Should the negation window stop at the end of a sentence? It would fix 3 of the limits
  above, but the sentence splitting needs punctuation, so it's a bigger change. Parked for review.
