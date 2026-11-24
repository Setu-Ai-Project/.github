"""bug_stage1.py - Bug's static mistake detection (Step 4, Stage 1). No AI calls.

Bug checks a learner's answer against a list of mistakes that humans tagged.
If the answer contains a tagged phrase, Bug returns a friendly warning + hint.
Standard library only. The phrases themselves live in a JSON file, never in this code.
"""
import json
import re
import unicodedata
from pathlib import Path

# Words that, if they appear just before a mistake phrase, mean the learner is
# probably saying NOT to do it ("never write something nice"). Apostrophes are
# removed during normalizing, so "don't" becomes "dont".
NEGATIONS = {"not", "never", "no", "dont", "cant", "wont", "isnt", "shouldnt",
             "avoid", "without"}

NEGATION_WINDOW = 3   # how many words before the match we look at

# Allowed shape for a mistake id, e.g. "m1-vague-words".
ID_RULE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


# ---------------------------------------------------------------------------
# Section 1: loading and validating the data
# ---------------------------------------------------------------------------

def load_mistakes(path):
    """Read the tagged-mistakes JSON file and return its list of mistakes.

    This one is allowed to raise an error (missing file, broken JSON), because a
    data problem should be loud for the team. Learners never call this directly.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("mistakes"), list):
        raise ValueError(f"{path}: expected {{\"mistakes\": [ ... ]}} at the top level")
    return data["mistakes"]


def _phrases_of(m):
    """All wordings of one mistake: the main phrase plus any variants."""
    variants = m.get("variants") or []
    if not isinstance(variants, list):      # e.g. someone wrote "variants": "abc"
        variants = []
    return [m.get("phrase")] + variants


def validate_mistakes(mistakes):
    """Return a list of problems found in the data (an empty list means it looks fine)."""
    problems, seen_ids = [], set()
    for i, m in enumerate(mistakes):
        if not isinstance(m, dict):
            problems.append(f"entry {i}: is not an object {{...}}")
            continue
        mid = m.get("id")
        if not mid:
            problems.append(f"entry {i}: missing id")
            mid = f"entry {i}"
        elif mid in seen_ids:
            problems.append(f"entry {i}: duplicate id {mid}")
        elif not isinstance(mid, str) or not ID_RULE.match(mid):
            # The R2 submission log (log_store.py) saves our ids comma-joined in
            # bug_mistake_ids, so an id with a comma or space would get split wrongly.
            problems.append(f"entry {i}: id {mid!r} must use only a-z, 0-9 and '-'")
        seen_ids.add(mid)

        if "variants" in m and not isinstance(m["variants"], list):
            problems.append(f"{mid}: 'variants' must be a list like [\"a b\", \"c d\"]")
        if not m.get("phrase"):
            problems.append(f"{mid}: missing phrase")

        for p in _phrases_of(m):
            if p is None and not m.get("phrase"):
                continue                     # already reported as missing phrase
            if not isinstance(p, str):
                problems.append(f"{mid}: phrase {p!r} is not text")
                continue
            words = _normalize(p).split()
            if not words:
                problems.append(f"{mid}: empty phrase")
            elif len(words) == 1:
                problems.append(f"{mid}: one-word phrase '{p}' may cause false alarms")

        if not m.get("explanation"):
            problems.append(f"{mid}: missing explanation")
        if not m.get("fix_hint"):
            problems.append(f"{mid}: missing fix_hint")
    return problems


# ---------------------------------------------------------------------------
# Section 2: normalizing and matching
# ---------------------------------------------------------------------------

def _normalize(text):
    """Lowercase, drop apostrophes, turn punctuation/symbols into spaces, collapse spaces.

    Why not re.sub(r"[^\\w\\s]", ...)? Because Python's \\w does NOT count Hindi
    vowel signs (like the 'aa' sign in "लाल") as letters, so that rule turns
    "लाल" into "ल ल". Instead we only remove characters Unicode labels as
    punctuation (P...) or symbols (S...), and keep everything else.
    Emoji are symbols, so they are removed too.
    """
    text = str(text).lower()
    text = text.replace("’", "").replace("‘", "").replace("'", "")  # don't -> dont
    text = "".join(" " if unicodedata.category(ch)[0] in "PS" else ch for ch in text)
    return " ".join(text.split())        # collapse all spacing to single spaces


def _pattern(phrase):
    """Whole-phrase pattern: the words in order, bounded by a space or the text edge.

    After _normalize, words are separated by exactly one space, so "a space or the
    edge" is a reliable word boundary in EVERY script. (\\b is not: it breaks after
    Hindi vowel signs.)
    """
    words = _normalize(phrase).split()
    return re.compile(r"(?<!\S)" + " ".join(map(re.escape, words)) + r"(?!\S)")


def _is_negated(clean_text, start):
    """True if a negation word appears in the few words just before the match."""
    return any(w in NEGATIONS for w in clean_text[:start].split()[-NEGATION_WINDOW:])


def _check_one(clean, m):
    """Return a warning dict if mistake m is in the clean text, else None."""
    for phrase in _phrases_of(m):
        if not isinstance(phrase, str) or not _normalize(phrase):
            continue
        for hit in _pattern(phrase).finditer(clean):
            # Look at EVERY occurrence: "never say something nice ... draw something nice"
            # has one negated and one real use. Warn only if a real one exists.
            if not _is_negated(clean, hit.start()):
                return {"id": m["id"], "matched": phrase,
                        "explanation": m["explanation"],
                        "fix_hint": m.get("fix_hint", "")}
    return None


def find_mistakes(submission, mistakes):
    """Return one dict per tagged mistake found in the learner's text. Never raises.

    Each dict is {"id", "matched", "explanation", "fix_hint"}.
    An empty list means Bug stays quiet.
    """
    try:
        clean = _normalize(submission if submission is not None else "")
        if not clean:
            return []
        found = []
        for m in mistakes:
            # Each mistake is checked on its own, so ONE broken entry in the data
            # only switches off that entry, not the whole detector.
            try:
                warning = _check_one(clean, m)
            except Exception as err:          # fail quietly: no warning is safest
                print(f"[bug] skipped bad mistake entry {m!r:.60}: {err}")
                continue
            if warning:
                found.append(warning)         # at most one warning per mistake
        return found
    except Exception as err:                  # fail quietly: no warning is safest
        print(f"[bug] matcher error ignored: {err}")
        return []
