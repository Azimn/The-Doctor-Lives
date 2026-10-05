"""The Doctor Lives: persistent renderer-neutral Pretorius cognition."""

from .causal_audit import AuditIntervention, CausalAuditHarness
from .chassis import PretoriusBrainPort
from .cognition import PretoriusBrain
from .models import CognitiveView, Experience, Provenance, RenderRequest, ViewItem
from .phenomenology import (
    AwarenessLevel,
    CertaintyBand,
    IntensityBand,
    ObjectiveProvenance,
    PhenomenalEvent,
    PhenomenalMode,
    PrivacyState,
    Recollection,
    SubjectiveSourceAttribution,
    SubjectiveSourceKind,
    VividnessBand,
)

__all__ = [
    "PretoriusBrain",
    "CausalAuditHarness",
    "AuditIntervention",
    "PretoriusBrainPort",
    "Experience",
    "Provenance",
    "ViewItem",
    "CognitiveView",
    "RenderRequest",
    "PhenomenalMode",
    "AwarenessLevel",
    "PrivacyState",
    "SubjectiveSourceKind",
    "CertaintyBand",
    "VividnessBand",
    "IntensityBand",
    "ObjectiveProvenance",
    "SubjectiveSourceAttribution",
    "PhenomenalEvent",
    "Recollection",
]
