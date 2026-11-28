"""Bounded associative recovery of faded imagery through the existing owned recall path."""
import re
from .dream_retention import dream_accessibility, dream_strength, is_dream_recollection

_PREFIX = "I recall a dream: "
_SOURCE = "phantasmagorium:dream-recollection:"
_STOP = frozenset("about again after before could dream dreams during from have into just like might recall remember seemed shall should some something that their there these they this those through upon very were what when where which while with would image place fleeting".split())

def _terms(text):
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in _STOP}

def _images(row):
    text = row["text"]
    if not text.startswith(_PREFIX):
        return ()
    body = text[len(_PREFIX):].strip()
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", body)
    if len(words) < 7:
        return ()
    phrases = set()
    for clause in re.split(r"[.!?;,:\n]+", body):
        parts = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", clause)
        for start in range(len(parts)):
            for width in range(3, min(6, len(parts)-start)+1):
                if width < len(words):
                    phrase = " ".join(parts[start:start+width])
                    if len(_terms(phrase)) >= 3:
                        phrases.add(phrase)
    return tuple(sorted(phrases))

def fragment_line(phrase):
    return "I have a fleeting image of " + phrase + "; I cannot quite place it."

def fragment_options(row, now, cue):
    if not row.get("active") or not is_dream_recollection(row) or dream_accessibility(row, now) != 0:
        return ()
    terms = _terms(cue)
    if len(terms) < 2:
        return ()
    latent = dream_strength(row, now) ** .5
    if latent < .08:
        return ()
    result = []
    for phrase in _images(row):
        words = _terms(phrase)
        overlap = len(words & terms)
        if overlap >= 2 and words - terms:
            score = latent * overlap / len(words)
            if score >= .06:
                result.append((score, fragment_line(phrase)))
    return tuple(sorted(result, key=lambda x: (-x[0], len(x[1]), x[1])))

def _owned_source(row, history):
    source = row.get("source", "")
    if not source.startswith(_SOURCE) or not row.get("external"):
        return False
    key = "ipseity:tower-history:imagination:" + source[len(_SOURCE):]
    return any(entry["key"] == key and entry["phase"] == "imagination"
               and any(item["organ"] == "Phantasmagorium"
                       and item["mode"] == "recollection"
                       and item["attribution"] == "dreamed"
                       and item["external"] is True
                       and item["text"] == row["text"]
                       and len(item["source_refs"]) == 2
                       and item["source_refs"][1] == row["id"]
                       for item in entry["content"]) for entry in history)

def select_fragment(rows, history, now, cue):
    candidates = []
    for row in rows:
        options = fragment_options(row, now, cue)
        if options and _owned_source(row, history):
            score, line = options[0]
            candidates.append((score, row["id"], line))
    return min(candidates, key=lambda x: (-x[0], x[1], x[2])) if candidates else None

def verify_fragment(row, history, now, line):
    return bool(row and row.get("active") and is_dream_recollection(row)
                and dream_accessibility(row, now) == 0
                and dream_strength(row, now) ** .5 >= .08
                and _owned_source(row, history)
                and line in {fragment_line(phrase) for phrase in _images(row)})

def selected_recall_question(brain, recall_id):
    """A policy row is evidence of selection, not a reusable authorization."""
    from contextlib import closing
    from hashlib import sha256
    import json
    from .mnemosyne_pilot import _TRIGGER, _SOURCE as CONCERN_SOURCE, _ACTOR
    with closing(brain.store.connect()) as db:
        decision = db.execute("SELECT tick,trigger,selected_action,state_pressure_json FROM policy_decisions WHERE id=?",
                              (recall_id,)).fetchone()
    if (decision is None or decision["trigger"] != _TRIGGER
            or decision["selected_action"] != "recall" or decision["tick"] != brain.store.tick):
        return None
    audit = json.loads(decision["state_pressure_json"])
    selected = audit.get("selected_gap_ids")
    if not isinstance(selected, list) or len(selected) != 1:
        return None
    concern = next((c for c in brain.store.open_concerns() if c["id"] == selected[0]
                    and c["source"] == CONCERN_SOURCE and c["actor"] == _ACTOR), None)
    if concern is None:
        return None
    description = " ".join(str(concern["description"]).split()).rstrip(".?")
    question = f"What do I remember of {description}?"
    if sha256(question.encode()).hexdigest() != audit.get("question_sha256"):
        return None
    return question


def verify_selected_fragment(brain, history, recall_id, memory_id, line):
    question = selected_recall_question(brain, recall_id)
    if question is None:
        return False
    suppressed = brain.store.canon_conflict_suppressed_memory_ids()
    rows = [r for r in brain.store.memories_with_classification() if r["id"] not in suppressed]
    candidate = select_fragment(rows, history, brain.store.tick, question)
    return bool(candidate and candidate[1:] == (memory_id, line))
