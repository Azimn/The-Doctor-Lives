"""Ordinary Tower life drives the original reviewed Affectus weather.

This uses the exact source-pinned Spinoza donor and the existing canonical
weather checkpoint. Physical and social events provide bounded drivers, not
new facts, goals or motor commands. Values are engineering mappings, not
independently established psychological magnitudes.
"""
from pathlib import Path
from .canonical_affectus_weather import CanonicalWeather, _META

DONOR = Path(__file__).with_name("data") / "affectus_donor"
SEED = 1842


def felt_words(value):
    """Realize the original donor's coarse felt report, not hidden body data."""
    import re
    pattern=r"(valence|arousal|security|fatigue):(-?\d\.\d\d)([\^v~])"
    parts=value.split()
    matches=[re.fullmatch(pattern,p) for p in parts]
    if len(parts)!=4 or any(m is None for m in matches) or {m[1] for m in matches}!={"valence","arousal","security","fatigue"}:
        raise PermissionError("Unexpected original Affectus felt report")
    words={"valence":("I feel rather discontented.","I feel rather pleased.","I feel my mood lifting.","I feel my mood sinking."),
           "arousal":("I feel subdued.","I feel stirred up.","I feel increasingly alert.","I feel myself settling."),
           "security":("I feel uneasy.","I feel secure.","I feel more at ease.","I feel less secure."),
           "fatigue":("I feel rested.","I feel weary.","I feel weariness growing.","I feel weariness easing.")}
    result=[]
    for m in matches:
        low,high,rising,falling=words[m[1]]
        level=float(m[2])
        if not -1<=level<=1:
            raise PermissionError("Felt report outside reviewed range")
        if level<0:
            result.append(low)
        elif level>0:
            result.append(high)
        if m[3]=="^":
            result.append(rising)
        elif m[3]=="v":
            result.append(falling)
    return tuple(result or ["I cannot discern a marked change in my mood."])


def weather_for(runtime):
    saved = runtime._port.brain.store.meta(_META)
    seed = SEED if saved is None else CanonicalWeather._decode(saved)["config"]["seed"]
    return CanonicalWeather(runtime._port, donor_root=DONOR, seed=seed)


def advance(runtime, provider, receipt, memory_id):
    from .small_tower import SmallTowerSource
    from .virtual_world_port import VirtualWorldReceipt
    if (type(provider) is not SmallTowerSource
            or type(receipt) is not VirtualWorldReceipt
            or not provider.verify_receipt(receipt)):
        raise PermissionError("Original Tower receipt required for Affectus")
    memory = runtime._port.brain.store.get_memory(memory_id)
    expected = ("virtual-world:small-tower:" + receipt.world_epoch + ":"
                + receipt.kind + ":" + receipt.event_id)
    if not memory or memory["source"] != expected or memory["text"] != receipt.first_person:
        raise PermissionError("Affectus receipt differs from admitted experience")
    weather = weather_for(runtime)
    drivers = []
    if receipt.kind == "action":
        if receipt.operation in ("sleep", "rest"):
            drivers.append(weather.driver("rest_density",
                                           .8 if receipt.operation == "sleep" else .45, expected))
        else:
            drivers.append(weather.driver("goal_progress",
                                           .2 if receipt.operation == "doctor_move" else .6, expected))
    elif receipt.first_person == "I could not complete my intended activity.":
        drivers.append(weather.driver("goal_impediment", .6, expected))
    if receipt.actor is not None and receipt.social_valence:
        drivers.append(weather.driver("social_feedback", receipt.social_valence, expected))
    tick = 1 if weather.tick == -1 else weather.tick + 1
    result = weather.step(tick, tuple(drivers), authorized=True, tower_memory_id=memory_id)
    return weather, result
