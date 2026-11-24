"""mistake_checks.py - known-bad answers must warn; correct answers must not.

Run:  python mistake_checks.py
Ends with VERIFY PASSED when everything is fine.
"""
import json
import tempfile
import time
from pathlib import Path

from bug_stage1 import load_mistakes, validate_mistakes, find_mistakes, _normalize

DATA_FILE = "sample_mistakes.json"
mistakes = load_mistakes(DATA_FILE)
print("data problems:", validate_mistakes(mistakes) or "none")

bad = 0


def check(label, ok, detail=""):
    """Print PASS/FAIL for one check and count failures."""
    global bad
    bad += not ok
    print("PASS" if ok else "FAIL", label, detail)


def ids(text, data=None):
    return [g["id"] for g in find_mistakes(text, mistakes if data is None else data)]


# ---------------------------------------------------------------------------
# D1. Known-bad answers MUST warn (with the expected mistake id)
# ---------------------------------------------------------------------------
SHOULD_WARN = [
    ("Draw something nice with trees",              "m1-vague-words"),
    ("SOMETHING   COOL!!!",                         "m1-vague-words"),
    ("a dog doing something good",                  "m1-vague-words"),
    ("paint it in any colour you like",             "m1-any-colour"),
    ("a car in any color",                          "m1-any-colour"),
    ("whatever colour is fine",                     "m1-any-colour"),
    ("you know what I mean, right?",                "m1-you-know-what-i-mean"),
    ("a dragon, in the usual style",                "m1-usual-style"),
    ("The Usual   Style please",                    "m1-usual-style"),
    ("make it better",                              "m1-make-it-better"),
    ("Make it nicer!!",                             "m1-make-it-better"),
    # one negated use AND one real use: the real one must still warn
    ("don't write something nice. ok, draw something nice", "m1-vague-words"),
]

# ---------------------------------------------------------------------------
# D1 + D2. Correct answers MUST stay quiet (3+ traps per mistake)
# ---------------------------------------------------------------------------
SHOULD_STAY_QUIET = [
    # general (from the guide)
    "a red kite flying over a green hill at sunset, watercolour style",
    "",
    "   ",
    "तीन लाल पतंगे",   # Hindi: three red kites
    # m1-vague-words
    "a nicely drawn castle",                                   # 'nice' only inside a word
    "never write 'something nice' in a prompt, be specific",   # negated
    "I don't want something nice, I want a red kite.",         # negation, other form
    "the nicest dragon with shiny green scales",               # word-inside-word
    "a cool blue lake under a full moon",                      # 'cool' alone is fine
    "Avoid saying something cool - say what it looks like",
    # m1-any-colour
    "a car without any colour, just a pencil sketch",
    "a robot that is not any color except silver",
    "a parrot with many colours on its wings",
    "colour the sky orange; is there any coloured paper left?", # 'coloured' != 'colour'
    # m1-you-know-what-i-mean
    "a girl whispering a secret to her friend",
    "never end with 'you know what i mean'",
    "do you know what animal is fastest? a cheetah running",
    # m1-usual-style
    "a castle drawn in an unusual style with floating towers",  # 'unusual' != 'usual'
    "not the usual style - bold pixel art with neon colours",
    "avoid the usual style, use thick charcoal lines",
    # m1-make-it-better
    "Do not write 'make it better'.",
    "make it bigger and brighter, with a yellow sun",
    "the toymaker makes it better every day",                   # 'makes' != 'make'
    "without asking to make it nicer, just add a red roof",
]

for text, want in SHOULD_WARN:
    got = ids(text)
    check("warn ", want in got and got.count(want) == 1, f"{text!r} -> {got}")
for text in SHOULD_STAY_QUIET:
    got = ids(text)
    check("quiet", not got, f"{text!r} -> {got}")

# ---------------------------------------------------------------------------
# D3. Try to break it
# ---------------------------------------------------------------------------
print("\n-- robustness (D3) --")

# Missing file -> a clear, loud error for the team (learners never see this)
try:
    load_mistakes("does_not_exist.json")
    check("missing file raises", False)
except FileNotFoundError:
    check("missing file raises FileNotFoundError", True)

# Broken JSON -> clear error too
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    f.write('{"mistakes": [ {"id": "x",, } ]}')
try:
    load_mistakes(f.name)
    check("broken JSON raises", False)
except json.JSONDecodeError:
    check("broken JSON raises JSONDecodeError", True)
Path(f.name).unlink()

# Entry missing 'phrase': validator reports it, matcher does not crash,
# and the OTHER mistakes still work.
broken = [{"id": "no-phrase", "explanation": "x", "fix_hint": "y"}] + mistakes
check("validator reports missing phrase",
      any("missing phrase" in p for p in validate_mistakes(broken)))
check("matcher survives entry without phrase + still finds others",
      ids("draw something nice", broken) == ["m1-vague-words"])

# Other bad data the validator must catch
bad_data = [
    {"id": "a", "phrase": "nice", "explanation": "x", "fix_hint": "y"},          # one word
    {"id": "a", "phrase": "two words", "explanation": "x", "fix_hint": "y"},     # duplicate id
    {"phrase": "no id here", "explanation": "x", "fix_hint": "y"},               # missing id
    {"id": "b", "phrase": "good words", "variants": "oops", "explanation": "x"},  # bad variants, no hint
    {"id": "c", "phrase": "fine phrase", "variants": [""], "fix_hint": "y"},      # empty variant, no explanation
    "not even an object",
    {"id": "m1,vague words", "phrase": "two words", "explanation": "x", "fix_hint": "y"},  # bad id
]
problems = validate_mistakes(bad_data)
for needle in ["one-word", "duplicate id", "missing id", "'variants' must be a list",
               "missing fix_hint", "empty phrase", "missing explanation", "not an object",
               "must use only a-z"]:
    check(f"validator catches: {needle}", any(needle in p for p in problems))
check("matcher survives junk data", find_mistakes("make it better", bad_data + mistakes)
      == find_mistakes("make it better", mistakes))

# Very long submission
long_text = ("a red kite over a hill " * 450) + " make it better"
t0 = time.perf_counter()
got = ids(long_text)
ms = (time.perf_counter() - t0) * 1000
check("10,000+ chars: correct and fast", got == ["m1-make-it-better"] and ms < 500,
      f"({len(long_text)} chars, {ms:.1f} ms)")

check("only punctuation", ids("!!!???") == [])
check("emoji only", ids("\U0001F600\U0001F680\U0001F308") == [])
check("None as input", ids(None) == [])
check("number as input", ids(12345) == [])
check("same phrase 3 times -> one warning",
      ids("something nice, something nice, something nice") == ["m1-vague-words"])
check("ids join safely for the R2 log (bug_mistake_ids)",
      ",".join(ids("something nice in any colour")).count(",") == 1)
check("two different mistakes -> two warnings",
      sorted(ids("something nice in any colour")) == ["m1-any-colour", "m1-vague-words"])

# Hindi / other scripts: letters must survive normalizing, and matching must work
print("\n-- other languages --")
check("normalizer keeps Hindi vowel signs",
      _normalize("लाल पतंग!") ==
      "लाल पतंग", repr(_normalize("लाल पतंग!")))
hindi_list = [{"id": "hi-vague", "phrase": "कुछ अच्छा", "explanation": "x", "fix_hint": "y"}]
check("Hindi phrase is found", ids("कुछ अच्छा बनाओ!", hindi_list) == ["hi-vague"])
check("Hindi phrase not found inside a longer word",
      ids("कुछ अच्छाई के बारे में", hindi_list) == [])
check("accented Latin kept", _normalize("Café NIÑO") == "café niño")

# ---------------------------------------------------------------------------
# D5. Known limitations: reported honestly, NOT counted as failures.
# If one of these starts behaving "correctly", great - move it to the lists above.
# ---------------------------------------------------------------------------
KNOWN_LIMITS = [
    # (text, should it warn?, why it goes wrong)
    ("No, draw something nice",            True,
     "missed: 'no' at the start of the sentence counts as negation"),
    ("I don't know, make it better",       True,
     "missed: 'dont' belongs to 'I don't know', not to the mistake"),
    ("you know what? i mean a red dragon", False,
     "false alarm: punctuation is removed, so 'what? i mean' joins up"),
    ("a black and white photo with hardly any colour", False,
     "false alarm: 'hardly' is not in the negation list"),
    ("a picnic basket with something good to eat inside", False,
     "false alarm: 'something good' is a fine phrase in this sentence"),
    ("make it better by making the sky darker and adding birds", False,
     "false alarm: phrase is followed by a specific instruction"),
]
print("\n-- known limits (not counted) --")
for text, should_warn, why in KNOWN_LIMITS:
    behaves = bool(ids(text)) == should_warn
    print("OK  " if behaves else "LIMIT", repr(text), "-", "now fixed!" if behaves else why)

total = len(SHOULD_WARN) + len(SHOULD_STAY_QUIET)
print(f"\nshould-warn: {len(SHOULD_WARN)} cases, should-stay-quiet: {len(SHOULD_STAY_QUIET)} cases")
print("\nVERIFY PASSED" if bad == 0 else f"\n{bad} problem(s) - read the FAIL lines")
