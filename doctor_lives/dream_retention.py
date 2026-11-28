"""Direct dream recall strength, not deletion or an association gate."""
import math

MIN_ACCESSIBILITY = 0.125

def is_dream_recollection(row):
    return row["kind"] == "dream_recollection" and row["evidence_class"] == "dreamed_not_lived"

def dream_strength(row, now_tick):
    if not is_dream_recollection(row):
        return 1.0
    created = int(row["created_tick"])
    now = max(created, int(now_tick))
    rehearsal = max(0, int(row["rehearsal_count"]))
    last = row["last_rehearsed_tick"]
    anchor = min(now, max(created, int(last))) if last is not None and rehearsal else created
    salience = max(0.0, min(1.0, float(row["base_salience"])))
    half_life = min(64.0, 8.0 + 16.0 * salience + 8.0 * math.log2(1 + rehearsal))
    peak = .75 + .25 * 2.0 ** (-(anchor - created) / half_life)
    return peak * 2.0 ** (-(now - anchor) / half_life)

def dream_accessibility(row, now_tick):
    strength = dream_strength(row, now_tick)
    return strength if strength >= MIN_ACCESSIBILITY else 0.0
