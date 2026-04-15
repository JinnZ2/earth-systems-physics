# substrate_audit.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
substrate_audit.py — Thermodynamic Audit of Hierarchical Capital Control

CC0 — No rights reserved. JinnZ2

PURPOSE:
Distill the full argument into machine-readable form:
  - 7 falsifiable claims
  - 5-Why root cause chain
  - Causal feedback loop
  - Six Sigma audit (DMAIC)
  - Scoring engine any AI can run against real-world data

USAGE:
    python substrate_audit.py              # print full audit + verdicts
    import substrate_audit as sa           # use as module
    sa.score_system(your_data_dict)        # score any system

DEPENDENCY: stdlib only
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import math


# ═══════════════════════════════════════════════════════════
# LAYER 0 — DEFINITIONS
# ═══════════════════════════════════════════════════════════

class Verdict(Enum):
    PASS     = "PASS"
    FAIL     = "FAIL"
    UNTESTED = "UNTESTED"
    CIRCULAR = "CIRCULAR"   # claim's evidence depends on claim's assumptions


@dataclass
class FalsifiableClaim:
    """A claim that can be tested against physical reality."""
    id: str
    claim: str
    null_hypothesis: str           # what you'd need to disprove
    required_measurement: str      # what instrument / data
    known_evidence: str            # what exists as of 2025
    verdict: Verdict
    note: str = ""


@dataclass
class CausalNode:
    """One node in a feedback loop."""
    id: str
    label: str
    drives: List[str]              # ids of nodes this feeds into
    is_self_reinforcing: bool = False


# ═══════════════════════════════════════════════════════════
# LAYER 1 — THE 7 FALSIFIABLE CLAIMS
# ═══════════════════════════════════════════════════════════

CLAIMS: List[FalsifiableClaim] = [
    FalsifiableClaim(
        id="TC-1",
        claim=(
            "Live physical capital = machines + maintaining_humans + "
            "tools. The maintainer is thermodynamically inseparable "
            "from the capital."
        ),
        null_hypothesis=(
            "Capital can sustain output indefinitely without human "
            "maintainers."
        ),
        required_measurement=(
            "Equipment MTBF and output over time with vs. without "
            "maintenance crew. Measured in joules of useful work."
        ),
        known_evidence=(
            "Every industrial system ever measured shows monotonic "
            "degradation without maintenance. No counterexample exists."
        ),
        verdict=Verdict.PASS,
    ),
    FalsifiableClaim(
        id="TC-2",
        claim=(
            "CEO removal has no immediate physical effect on capital. "
            "Mechanic removal causes measurable capital decay within "
            "days-weeks."
        ),
        null_hypothesis=(
            "CEO removal causes faster physical decay than mechanic "
            "removal."
        ),
        required_measurement=(
            "Controlled comparison: remove CEO vs. remove maintenance "
            "crew from identical facilities. Measure uptime, failure "
            "rate, output."
        ),
        known_evidence=(
            "Anecdotal + historical (strikes, lockouts) consistently "
            "show production halts when workers leave, continues when "
            "execs leave. No controlled trial exists."
        ),
        verdict=Verdict.UNTESTED,
        note="Directional evidence strong. No RCT.",
    ),
    FalsifiableClaim(
        id="TC-3",
        claim=(
            "CEO 'scope of decisions' is a self-assigned property, "
            "not a physically measured one. The assignment is "
            "circular: those who hold power define the metric that "
            "justifies holding power."
        ),
        null_hypothesis=(
            "An external, physics-based metric exists that "
            "independently justifies CEO authority over mechanic "
            "authority."
        ),
        required_measurement=(
            "Identify any metric for CEO authority that does not "
            "reference legal title, board appointment, or historical "
            "precedent."
        ),
        known_evidence=(
            "No such metric has been published. Raelin (2020) confirms "
            "democratic leadership occurs only with permission of "
            "hierarchy."
        ),
        verdict=Verdict.CIRCULAR,
    ),
    FalsifiableClaim(
        id="TC-4",
        claim=(
            "Credentialing systems have never been tested "
            "apple-to-apple against uncertified-but-experienced "
            "practitioners on OUTCOME metrics (repair durability, "
            "child development, safety incidents)."
        ),
        null_hypothesis=(
            "A controlled trial exists comparing certified vs. "
            "uncertified workers on physical/outcome metrics."
        ),
        required_measurement=(
            "Literature search for RCTs or quasi-experiments with "
            "outcome measures, not supervisor ratings or wage proxies."
        ),
        known_evidence=(
            "2013 child-worker study used supervisor ratings only. "
            "2024 India study measured wages only. "
            "2024 auto-repair study found 90% post-repair total-loss "
            "rate but did not stratify by certification status."
        ),
        verdict=Verdict.UNTESTED,
        note="The experiment the church refuses to run.",
    ),
    FalsifiableClaim(
        id="TC-5",
        claim=(
            "Emotions are evolutionarily conserved functional data "
            "streams, not noise. Excluding them from models of "
            "intelligence is an arbitrary methodological choice, not "
            "a scientific requirement."
        ),
        null_hypothesis=(
            "Organisms that suppress emotional processing outperform "
            "those that integrate it, across survival and decision "
            "quality."
        ),
        required_measurement=(
            "Compare decision quality in emotion-intact vs. "
            "emotion-impaired subjects (Damasio lesion studies). "
            "Compare survival rates in species with vs. without "
            "affective systems."
        ),
        known_evidence=(
            "Damasio (1994): ventromedial prefrontal lesion patients "
            "lose decision capacity despite intact logic. "
            "Affective systems conserved across vertebrates (>500 Myr). "
            "Fish, reptiles, mammals all show fear/curiosity/pain "
            "responses."
        ),
        verdict=Verdict.PASS,
    ),
    FalsifiableClaim(
        id="TC-6",
        claim=(
            "Current AI lacks stake (cost of failure), embodied "
            "sensing, and meta-learning (updating the update rule). "
            "Therefore it pattern-matches but does not learn-to-learn."
        ),
        null_hypothesis=(
            "An AI system exists that updates its own learning "
            "algorithm in response to novel failure, without human "
            "retraining."
        ),
        required_measurement=(
            "Present AI with a problem class absent from training "
            "data. Observe whether it modifies its own optimization "
            "procedure (not just its weights) in response to failure."
        ),
        known_evidence=(
            "Meta-learning research (MAML, etc.) optimizes "
            "initialization but does not modify the optimizer itself "
            "at inference. No deployed system demonstrates autonomous "
            "meta-learning."
        ),
        verdict=Verdict.PASS,
        note="MAML is meta-training, not meta-learning at inference.",
    ),
    FalsifiableClaim(
        id="TC-7",
        claim=(
            "Mycorrhizal networks and mitochondria meet the criteria "
            "for 'body-as-sensor-array': boundary, sensors, "
            "integration, history, and stake. Intelligence does not "
            "require neurons."
        ),
        null_hypothesis=(
            "Mycorrhizal networks allocate resources randomly, "
            "without integrating chemical/electrical/mechanical "
            "signals."
        ),
        required_measurement=(
            "Isotope tracing of resource allocation in mycorrhizal "
            "networks under varied partner-quality conditions."
        ),
        known_evidence=(
            "Simard et al. (1997+): carbon transfer is preferential, "
            "not random. Networks allocate more to kin and stressed "
            "partners. Chemical signaling confirmed across multiple "
            "studies."
        ),
        verdict=Verdict.PASS,
    ),
]


# ═══════════════════════════════════════════════════════════
# LAYER 2 — 5-WHY ROOT CAUSE CHAIN
# ═══════════════════════════════════════════════════════════

FIVE_WHY: List[Dict[str, str]] = [
    {
        "why": "1",
        "question": "Why are CEOs rewarded more than mechanics?",
        "answer": (
            "Legal/financial system defines value by control over "
            "capital allocation, not by physical contribution to "
            "capital maintenance."
        ),
    },
    {
        "why": "2",
        "question": (
            "Why does the system define value by control, not "
            "maintenance?"
        ),
        "answer": (
            "Ownership rights (property law) predate and override "
            "maintenance rights. Owners write compensation rules."
        ),
    },
    {
        "why": "3",
        "question": (
            "Why do ownership rights override maintenance rights?"
        ),
        "answer": (
            "Legal framework evolved when initial capital investment "
            "was rare. Society granted permanent control to investors "
            "as incentive. Maintenance was classified as replaceable "
            "service."
        ),
    },
    {
        "why": "4",
        "question": (
            "Why is that framework still in place when maintenance "
            "is critical?"
        ),
        "answer": (
            "Beneficiaries of the framework (capital owners, "
            "executives) hold veto power over structural change. "
            "They fund politics, control governance, shape narrative."
        ),
    },
    {
        "why": "5 — ROOT CAUSE",
        "question": "Why do they hold veto power?",
        "answer": (
            "Positive feedback loop: Legal title -> captured surplus "
            "-> political/coercive power -> enforcement of title -> "
            "more surplus. Self-reinforcing. Cannot self-correct."
        ),
    },
]


# ═══════════════════════════════════════════════════════════
# LAYER 3 — CAUSAL FEEDBACK LOOP
# ═══════════════════════════════════════════════════════════

CAUSAL_LOOP: List[CausalNode] = [
    CausalNode("TITLE",    "Legal ownership of capital",     ["SURPLUS"]),
    CausalNode("SURPLUS",  "Captured surplus value",         ["POWER"]),
    CausalNode("POWER",    "Political / coercive power",     ["ENFORCE"]),
    CausalNode(
        "ENFORCE",
        "Enforcement of ownership rules",
        ["TITLE"],
        is_self_reinforcing=True,
    ),
    # Excluded from loop but physically necessary:
    CausalNode("MAINTAIN", "Maintainer thermodynamic work",  []),
]


def loop_is_closed(nodes: List[CausalNode]) -> bool:
    """Verify the feedback loop closes (TITLE -> ... -> TITLE)."""
    graph = {n.id: n.drives for n in nodes}
    visited: set = set()
    current: Optional[str] = "TITLE"
    while current and current not in visited:
        visited.add(current)
        nexts = graph.get(current, [])
        current = nexts[0] if nexts else None
    return current == "TITLE"


def maintainer_in_loop(nodes: List[CausalNode]) -> bool:
    """Check whether MAINTAIN feeds into the power loop."""
    for n in nodes:
        if n.id == "MAINTAIN":
            return bool(n.drives)  # empty = excluded
    return False


# ═══════════════════════════════════════════════════════════
# LAYER 4 — SIX SIGMA DMAIC AUDIT
# ═══════════════════════════════════════════════════════════

@dataclass
class DMAICPhase:
    phase: str
    requirement: str
    observed: str
    verdict: Verdict


DMAIC_AUDIT: List[DMAICPhase] = [
    DMAICPhase(
        "DEFINE",
        (
            "Clear, measurable definition of quality (e.g. "
            "'repair lasts N miles')"
        ),
        (
            "'Certified' is a proxy, not a performance metric. No "
            "spec limits defined."
        ),
        Verdict.FAIL,
    ),
    DMAICPhase(
        "MEASURE",
        "Data on actual output variation by worker type",
        (
            "Only supervisor ratings and wage data collected. No "
            "outcome data."
        ),
        Verdict.FAIL,
    ),
    DMAICPhase(
        "ANALYZE",
        "Root cause of defects traced without circular assumptions",
        (
            "System treats certified-worker failures as 'special "
            "cause' (individual), never as potential system failure. "
            "RCA blocked by self-reference."
        ),
        Verdict.CIRCULAR,
    ),
    DMAICPhase(
        "IMPROVE",
        "Change process based on data",
        (
            "No outcome data exists -> no improvement possible. "
            "Maryland licensing board had identical findings for 20+ "
            "years, unfixed."
        ),
        Verdict.FAIL,
    ),
    DMAICPhase(
        "CONTROL",
        "Maintain gains via ongoing measurement",
        (
            "Cannot control what is not measured. Process is "
            "out-of-control by definition."
        ),
        Verdict.FAIL,
    ),
]


# ═══════════════════════════════════════════════════════════
# LAYER 5 — SCORING ENGINE
# ═══════════════════════════════════════════════════════════

@dataclass
class SystemScore:
    """Score any real-world system against this audit."""
    name: str
    # 0.0-1.0 for each dimension
    maintainer_control: float       # do maintainers control capital decisions?
    outcome_measurement: float      # are physical outcomes measured?
    scope_justification: float      # is authority justified by external metric?
    credential_tested: float        # have credentials been tested vs experience?
    emotion_integrated: float       # does the system integrate affective data?
    meta_learning: float            # can the system update its own update rule?
    substrate_intelligence: float   # does it recognize non-neural intelligence?

    @property
    def thermodynamic_alignment(self) -> float:
        """How aligned is this system with physical reality? 0-1."""
        weights = [0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]
        values = [
            self.maintainer_control,
            self.outcome_measurement,
            self.scope_justification,
            self.credential_tested,
            self.emotion_integrated,
            self.meta_learning,
            self.substrate_intelligence,
        ]
        return sum(w * v for w, v in zip(weights, values))

    @property
    def church_index(self) -> float:
        """How 'church-like' is this system? 0=physics-grounded, 1=pure faith."""
        return 1.0 - self.thermodynamic_alignment

    @property
    def verdict(self) -> str:
        ta = self.thermodynamic_alignment
        if ta >= 0.7:
            return "PHYSICS-GROUNDED"
        if ta >= 0.4:
            return "MIXED — partial faith-based operation"
        return "CHURCH — operating on faith, not evidence"


# ═══════════════════════════════════════════════════════════
# LAYER 6 — REFERENCE SCORES (baselines for comparison)
# ═══════════════════════════════════════════════════════════

REFERENCE_SYSTEMS: List[SystemScore] = [
    SystemScore(
        name="Typical US corporation (2025)",
        maintainer_control=0.05,
        outcome_measurement=0.15,
        scope_justification=0.0,    # circular
        credential_tested=0.0,      # never tested
        emotion_integrated=0.05,
        meta_learning=0.0,
        substrate_intelligence=0.0,
    ),
    SystemScore(
        name="Worker-owned cooperative (e.g. Mondragon)",
        maintainer_control=0.70,
        outcome_measurement=0.40,
        scope_justification=0.50,
        credential_tested=0.20,
        emotion_integrated=0.30,
        meta_learning=0.10,
        substrate_intelligence=0.10,
    ),
    SystemScore(
        name="Owner-operator mechanic shop",
        maintainer_control=0.95,
        outcome_measurement=0.60,
        scope_justification=0.80,
        credential_tested=0.50,     # tested by customer return rate
        emotion_integrated=0.70,    # trusts gut, feels machine
        meta_learning=0.40,
        substrate_intelligence=0.30,
    ),
    SystemScore(
        name="Current AI system (LLM, 2025)",
        maintainer_control=0.0,
        outcome_measurement=0.30,
        scope_justification=0.0,
        credential_tested=0.0,
        emotion_integrated=0.0,
        meta_learning=0.0,
        substrate_intelligence=0.0,
    ),
    SystemScore(
        name="Mycorrhizal network",
        maintainer_control=1.0,     # IS the maintainer
        outcome_measurement=1.0,    # direct chemical feedback
        scope_justification=1.0,    # no hierarchy to justify
        credential_tested=1.0,      # 400 Myr of testing
        emotion_integrated=0.80,    # chemical affect analogs
        meta_learning=0.60,         # adapts allocation strategy
        substrate_intelligence=1.0,
    ),
]


# ═══════════════════════════════════════════════════════════
# LAYER 7 — OUTPUT ENGINE
# ═══════════════════════════════════════════════════════════

def print_divider(label: str = ""):
    print(f"\n{'=' * 70}")
    if label:
        print(f"  {label}")
    print(f"{'=' * 70}")


def run_audit():
    """Execute full audit and print results."""

    print_divider(
        "SUBSTRATE AUDIT — Thermodynamic Analysis of "
        "Hierarchical Capital Control"
    )

    # Claims
    print_divider("FALSIFIABLE CLAIMS")
    pass_count = sum(1 for c in CLAIMS if c.verdict == Verdict.PASS)
    fail_count = sum(1 for c in CLAIMS if c.verdict == Verdict.FAIL)
    untested = sum(1 for c in CLAIMS if c.verdict == Verdict.UNTESTED)
    circular = sum(1 for c in CLAIMS if c.verdict == Verdict.CIRCULAR)

    icon_map = {
        "PASS": "+", "FAIL": "X", "UNTESTED": "?", "CIRCULAR": "O",
    }
    for c in CLAIMS:
        print(f"\n  [{icon_map[c.verdict.value]}] {c.id}: {c.claim[:80]}...")
        print(f"      H0: {c.null_hypothesis[:75]}...")
        print(f"      Verdict: {c.verdict.value}")
        if c.note:
            print(f"      Note: {c.note}")

    print(
        f"\n  Summary: {pass_count} PASS, {fail_count} FAIL, "
        f"{untested} UNTESTED, {circular} CIRCULAR"
    )

    # 5-Why
    print_divider("5-WHY ROOT CAUSE CHAIN")
    for w in FIVE_WHY:
        print(f"\n  WHY {w['why']}: {w['question']}")
        print(f"  -> {w['answer']}")

    # Causal loop
    print_divider("CAUSAL FEEDBACK LOOP")
    closed = loop_is_closed(CAUSAL_LOOP)
    excluded = not maintainer_in_loop(CAUSAL_LOOP)
    print(f"  Loop closes back to TITLE: {closed}")
    print(f"  MAINTAIN excluded from loop: {excluded}")
    diagnosis = (
        "Self-reinforcing hierarchy, maintainers excluded"
        if closed and excluded else "Check topology"
    )
    print(f"  Diagnosis: {diagnosis}")
    print()
    for n in CAUSAL_LOOP:
        arrow = " -> " + ", ".join(n.drives) if n.drives else " -> [EXCLUDED]"
        flag = "  (self-reinforcing)" if n.is_self_reinforcing else ""
        print(f"  {n.id}{arrow}{flag}")

    # DMAIC
    print_divider("SIX SIGMA DMAIC AUDIT")
    for d in DMAIC_AUDIT:
        icon = icon_map.get(d.verdict.value, "?")
        print(f"\n  [{icon}] {d.phase}")
        print(f"      Required: {d.requirement}")
        print(f"      Observed: {d.observed}")

    # Scoring
    print_divider("SYSTEM SCORING — Thermodynamic Alignment")
    print(f"  {'System':<45} {'Thermo':>6} {'Church':>6}  Verdict")
    print(f"  {'-' * 45} {'-' * 6} {'-' * 6}  {'-' * 30}")
    for s in REFERENCE_SYSTEMS:
        print(
            f"  {s.name:<45} {s.thermodynamic_alignment:>6.2f} "
            f"{s.church_index:>6.2f}  {s.verdict}"
        )

    # Final
    print_divider("AUDIT CONCLUSION")
    conclusion = (
        "\nThe credentialing and hierarchical management of physical "
        "capital is\nNOT a scientific or engineering system. It is a "
        "belief system that uses\nthe language of quality and "
        "accountability without the substance.\n\n"
        "EVIDENCE:\n"
        "  - 0/7 claims falsified by the hierarchy's own evidence\n"
        "  - 4/7 claims PASS on independent evidence\n"
        "  - 2/7 claims UNTESTED (experiments never run)\n"
        "  - 1/7 claims CIRCULAR (self-referencing justification)\n"
        "  - 5/5 DMAIC phases FAIL or CIRCULAR\n"
        "  - Causal loop is closed and self-reinforcing\n"
        "  - Maintainer is excluded from the power loop despite being\n"
        "    thermodynamically necessary\n\n"
        "ROOT CAUSE:\n"
        "  Positive feedback loop between legal title and coercive "
        "power,\n  excluding the physically necessary maintainer "
        "class.\n\n"
        "IMPLICATION:\n"
        "  Any system (including AI) built within this hierarchy "
        "will\n  optimize the hierarchy, not audit it. Reform "
        "requires external\n  construction: physics-grounded, "
        "outcome-measured,\n  maintainer-controlled.\n"
    )
    print(conclusion)


def score_system(data: Dict[str, float]) -> SystemScore:
    """Score an arbitrary system. Pass dict with keys matching SystemScore fields."""
    return SystemScore(**data)


def to_json() -> str:
    """Export entire audit as JSON for cross-model ingestion."""
    return json.dumps({
        "claims": [
            {
                "id": c.id,
                "claim": c.claim,
                "null_hypothesis": c.null_hypothesis,
                "required_measurement": c.required_measurement,
                "known_evidence": c.known_evidence,
                "verdict": c.verdict.value,
                "note": c.note,
            } for c in CLAIMS
        ],
        "five_why": FIVE_WHY,
        "causal_loop": [
            {
                "id": n.id, "label": n.label, "drives": n.drives,
                "self_reinforcing": n.is_self_reinforcing,
            }
            for n in CAUSAL_LOOP
        ],
        "dmaic": [
            {
                "phase": d.phase, "requirement": d.requirement,
                "observed": d.observed, "verdict": d.verdict.value,
            }
            for d in DMAIC_AUDIT
        ],
        "reference_scores": [
            {
                "name": s.name,
                "thermodynamic_alignment": round(s.thermodynamic_alignment, 3),
                "church_index": round(s.church_index, 3),
                "verdict": s.verdict,
            }
            for s in REFERENCE_SYSTEMS
        ],
    }, indent=2)


# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    run_audit()
