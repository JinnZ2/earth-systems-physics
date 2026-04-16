# domain_taxonomy.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
domain_taxonomy.py
──────────────────
Six measurement / validation domains, defined by what each
measures, how each validates, and where each fails. Kept separate
so that one domain's validation method is not used to invalidate
another.

Each domain answers a different class of question:
  - Clinical / surgical      : Does this intervention work?
  - Affective neuroscience   : What mechanism produces this behavior?
  - Cellular / biochemical   : What are the dynamics at micro scale?
  - Ecological network       : How do resources move in real environments?
  - TEK (traditional)        : What persists across generations?
  - Institutional / economic : How do we coordinate at scale?

Problems arise when:
  - One system's validation method is used to invalidate another
  - Outputs from one are treated as complete representations
    of reality

This module also provides IncentiveChannel and IncentiveAudit
classes for tracking how reward structures distort signal
fidelity within any domain. Incentives are not separate from
signal — they are the driver of signal deformation.

Place in the repo:
  - Complements substrate_audit.py by providing reference
    profiles for each domain's incentive structure
  - Each IncentiveChannel maps to specific substrate_audit
    SystemScore dimensions (signal_fidelity, feedback_latency,
    maintainer_control, money_physics_coupling)

CC0 — No rights reserved. stdlib only.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════
# LAYER 0: MEASUREMENT DOMAINS
# ═══════════════════════════════════════════════════════════

MEASUREMENT_DOMAINS = {
    "clinical_surgical": {
        "scope": "Acute human intervention under controlled conditions",
        "goal": "Reduce immediate morbidity/mortality",
        "primary_unit": [
            "Patient outcomes (mortality, complications, readmission)",
            "Physiological metrics (bleeding, infection rate, recovery time)",
        ],
        "method_structure": [
            "Randomized controlled trials (RCTs) when feasible",
            "Cohort studies, registries, meta-analyses when not",
        ],
        "validation_loop": (
            "Short to medium term (days to years); statistical "
            "significance + peer replication"
        ),
        "strengths": [
            "Strong control over variables in narrow contexts",
            "Clear causal inference in constrained systems",
        ],
        "limitations": [
            "Selection bias: patients filtered before inclusion",
            "Proxy substitution: '30-day survival' instead of lifetime function",
            "Context stripping: environment, lifestyle, long-term adaptation excluded",
            "Intervention bias: favors what can be isolated and billed",
            "Time truncation: long-term systemic effects underweighted",
        ],
        "failure_mode": (
            "Optimizes local intervention success while "
            "under-measuring system-level outcomes"
        ),
        "question_answered": (
            "Does this intervention work under controlled conditions?"
        ),
    },
    "affective_neuroscience": {
        "scope": "Brain-behavior relationships",
        "goal": "Map functional circuits and decision processes",
        "primary_unit": [
            "Behavioral output (choices, reaction time)",
            "Neural activation patterns",
        ],
        "method_structure": [
            "Controlled tasks (lab environments)",
            "Lesion studies, imaging, stimulation",
        ],
        "validation_loop": "Replication across subjects and labs",
        "strengths": [
            "High repeatability",
            "Good for isolating specific mechanisms",
        ],
        "limitations": [
            "Proxy-heavy (tasks != real-world decisions)",
            "Ecological validity gap",
            "Internal states inferred, not directly measured",
        ],
        "failure_mode": (
            "Confuses task performance with real-world adaptive success"
        ),
        "question_answered": "What mechanism produces this behavior?",
    },
    "cellular_biochemical": {
        "scope": "Sub-cellular processes",
        "goal": "Direct measurement of energy and material flow",
        "primary_unit": [
            "ATP production, membrane potential, molecular flux",
        ],
        "method_structure": [
            "Controlled lab instrumentation",
            "Direct measurement (fluorescence, electrophysiology)",
        ],
        "validation_loop": "High repeatability under identical conditions",
        "strengths": [
            "Direct physical measurement (low abstraction)",
            "Strong causal linkage",
        ],
        "limitations": [
            "Scale isolation (cell != organism)",
            "Environmental complexity removed",
        ],
        "failure_mode": "Correct locally, incomplete globally",
        "question_answered": (
            "What are the physical dynamics at micro scale?"
        ),
    },
    "ecological_network": {
        "scope": "Multi-organism, open systems",
        "goal": "Track resource flows and interactions",
        "primary_unit": [
            "Carbon/nutrient transfer",
            "Growth, survival, network connectivity",
        ],
        "method_structure": [
            "Field experiments + tracing (isotopes, tagging)",
            "Partial controls",
        ],
        "validation_loop": "Seasonal to multi-year",
        "strengths": [
            "Real-world substrate",
            "Direct material tracking",
        ],
        "limitations": [
            "Incomplete control (many variables)",
            "Attribution ambiguity (multiple pathways)",
        ],
        "failure_mode": "Cannot fully isolate causality in complex systems",
        "question_answered": (
            "How do resources move in real environments?"
        ),
    },
    "tek_traditional": {
        "scope": "Long-duration human-environment interaction",
        "goal": "Survival, stability, regeneration",
        "primary_unit": [
            "Yield stability (food, water)",
            "Biodiversity, fire behavior, species cycles",
        ],
        "method_structure": [
            "Iterative observation, practice, transmission",
            (
                "Embedded in daily use (no separation between "
                "observer and system)"
            ),
        ],
        "validation_loop": (
            "Multi-generational (decades to millennia)"
        ),
        "strengths": [
            "Long timescale validation",
            "Direct coupling to survival (high stake)",
            "Integrated variables (not artificially isolated)",
        ],
        "limitations": [
            "Low formal standardization",
            "Hard to isolate single-variable causality",
            (
                "Knowledge encoded in language/practice, not always "
                "abstracted"
            ),
        ],
        "failure_mode": (
            "Difficult to translate into external measurement frameworks"
        ),
        "question_answered": (
            "What persists across generations under real constraints?"
        ),
    },
    "institutional_economic": {
        "scope": "Coordination of large-scale human activity",
        "goal": "Allocation of resources",
        "primary_unit": [
            "Monetary values, KPIs, financial metrics",
        ],
        "method_structure": [
            "Accounting systems (GAAP/IFRS)",
            "Reporting hierarchies",
        ],
        "validation_loop": "Quarterly to annual (often lagged)",
        "strengths": [
            "Scales coordination across large populations",
            "Enables abstract planning",
        ],
        "limitations": [
            "Indirect measurement (money != physical output)",
            "Signal latency",
            "Multiple competing metrics",
            "Incentive distortion",
        ],
        "failure_mode": (
            "Symbolic consistency without physical grounding"
        ),
        "question_answered": "How do we coordinate at scale?",
    },
}


# ═══════════════════════════════════════════════════════════
# LAYER 1: INCENTIVE CHANNEL
# ═══════════════════════════════════════════════════════════

@dataclass
class IncentiveChannel:
    """
    One incentive channel operating on a system. Describes what is
    actually rewarded and how well the reward couples to physical
    reality.
    """
    name: str

    # What is actually rewarded?
    # One of: "physical_outcome", "proxy_metric", "symbolic/narrative"
    reward_basis: str

    # Coupling to real-world outcomes (0-1)
    outcome_coupling: float

    # Time delay between action and reward (0-1, 1 = immediate)
    reward_latency: float

    # Directional alignment with system health (-1 to 1)
    #  1 = always improves system
    #  0 = neutral
    # -1 = systematically harmful
    gradient_alignment: float

    # Can the agent influence the metric directly without
    # improving reality? (0 = no, 1 = fully gameable)
    gameability: float

    # Who receives the reward vs who does the work?
    # 1 = same entity (mechanic paid for fix)
    # 0 = fully decoupled (exec bonus vs worker output)
    reward_distribution: float


# ═══════════════════════════════════════════════════════════
# LAYER 2: INCENTIVE AUDIT
# ═══════════════════════════════════════════════════════════

@dataclass
class IncentiveAudit:
    """
    Aggregates incentive channels on a single system and computes
    alignment with physical reality.
    """
    name: str
    channels: List[IncentiveChannel] = field(default_factory=list)

    @property
    def alignment(self) -> float:
        """
        Weighted alignment across all channels. Gameability is
        applied as (1 - gameability): high gameability degrades
        alignment.
        """
        if not self.channels:
            return 0.0
        weights = {
            "outcome_coupling":    0.25,
            "reward_latency":      0.20,
            "gradient_alignment":  0.20,
            "gameability":         0.15,  # applied as (1 - gameability)
            "reward_distribution": 0.20,
        }
        total = 0.0
        for c in self.channels:
            total += (
                weights["outcome_coupling"] * c.outcome_coupling
                + weights["reward_latency"] * c.reward_latency
                + weights["gradient_alignment"] * max(0.0, c.gradient_alignment)
                + weights["gameability"] * (1.0 - c.gameability)
                + weights["reward_distribution"] * c.reward_distribution
            )
        return total / len(self.channels)

    def incentive_entropy(self) -> float:
        """
        Single diagnostic: how much can signals be rearranged
        without changing physical reality?

        entropy = gameability + (1 - outcome_coupling)
                  + (1 - reward_distribution)

        Averaged across channels. Higher = more disconnected
        from physical outcomes.
        """
        if not self.channels:
            return 0.0
        total = 0.0
        for c in self.channels:
            total += (
                c.gameability
                + (1.0 - c.outcome_coupling)
                + (1.0 - c.reward_distribution)
            )
        return total / len(self.channels)

    @property
    def verdict(self) -> str:
        a = self.alignment
        if a >= 0.7:
            return "REALITY-COUPLED"
        if a >= 0.4:
            return "MIXED — partial decoupling"
        return "DECOUPLED — symbolic without physical basis"


# ═══════════════════════════════════════════════════════════
# LAYER 3: REFERENCE PROFILES — one per domain
# ═══════════════════════════════════════════════════════════

def _make_profile(
    name: str,
    channels: List[IncentiveChannel],
) -> IncentiveAudit:
    audit = IncentiveAudit(name=name)
    audit.channels = channels
    return audit


REFERENCE_PROFILES: Dict[str, IncentiveAudit] = {
    "clinical_surgical": _make_profile(
        "Clinical / surgical system",
        [
            IncentiveChannel(
                name="procedure_reimbursement",
                reward_basis="proxy_metric",
                outcome_coupling=0.6,
                reward_latency=0.4,
                gradient_alignment=0.5,
                gameability=0.5,
                reward_distribution=0.6,
            ),
        ],
    ),
    "affective_neuroscience": _make_profile(
        "Affective / behavioral neuroscience",
        [
            IncentiveChannel(
                name="publication_novelty",
                reward_basis="symbolic/narrative",
                outcome_coupling=0.2,
                reward_latency=0.2,
                gradient_alignment=0.3,
                gameability=0.7,
                reward_distribution=0.5,
            ),
        ],
    ),
    "cellular_biochemical": _make_profile(
        "Cellular / lab biology",
        [
            IncentiveChannel(
                name="reproducible_signal",
                reward_basis="proxy_metric",
                outcome_coupling=0.4,
                reward_latency=0.3,
                gradient_alignment=0.5,
                gameability=0.4,
                reward_distribution=0.5,
            ),
        ],
    ),
    "ecological_network": _make_profile(
        "Ecological field science",
        [
            IncentiveChannel(
                name="longterm_study",
                reward_basis="proxy_metric",
                outcome_coupling=0.6,
                reward_latency=0.2,
                gradient_alignment=0.6,
                gameability=0.4,
                reward_distribution=0.5,
            ),
        ],
    ),
    "tek_traditional": _make_profile(
        "TEK systems",
        [
            IncentiveChannel(
                name="survival_feedback",
                reward_basis="physical_outcome",
                outcome_coupling=1.0,
                reward_latency=0.7,
                gradient_alignment=0.9,
                gameability=0.1,
                reward_distribution=0.9,
            ),
        ],
    ),
    "institutional_economic": _make_profile(
        "Institutional / corporate systems",
        [
            IncentiveChannel(
                name="stock_price_compensation",
                reward_basis="symbolic/narrative",
                outcome_coupling=0.2,
                reward_latency=0.2,
                gradient_alignment=0.2,
                gameability=0.8,
                reward_distribution=0.1,
            ),
        ],
    ),
}


# ═══════════════════════════════════════════════════════════
# LAYER 4: CROSS-SCOPE COMPARISON
# ═══════════════════════════════════════════════════════════

_TIMESCALE_MAP = {
    "clinical_surgical":      "short",
    "affective_neuroscience": "short",
    "cellular_biochemical":   "instant",
    "ecological_network":     "medium-long",
    "tek_traditional":        "very long",
    "institutional_economic": "lagged",
}

_CONTROL_MAP = {
    "clinical_surgical":      "high",
    "affective_neuroscience": "high",
    "cellular_biochemical":   "very high",
    "ecological_network":     "medium",
    "tek_traditional":        "low formal",
    "institutional_economic": "low",
}

_REALITY_COUPLING_MAP = {
    "clinical_surgical":      "medium",
    "affective_neuroscience": "medium-low",
    "cellular_biochemical":   "high (local)",
    "ecological_network":     "high",
    "tek_traditional":        "high",
    "institutional_economic": "symbolic",
}

_MEASUREMENT_TYPE_MAP = {
    "clinical_surgical":      "direct + proxy",
    "affective_neuroscience": "proxy-heavy",
    "cellular_biochemical":   "direct",
    "ecological_network":     "direct (partial)",
    "tek_traditional":        "direct (integrated)",
    "institutional_economic": "symbolic",
}


def compare_domains() -> List[Dict]:
    """
    Compressed cross-scope comparison. Returns one record per
    domain with the key dimensions needed to decide which domain
    applies to a given question.
    """
    rows: List[Dict] = []
    for key, spec in MEASUREMENT_DOMAINS.items():
        rows.append({
            "domain": key,
            "measurement_type": _MEASUREMENT_TYPE_MAP[key],
            "timescale": _TIMESCALE_MAP[key],
            "control": _CONTROL_MAP[key],
            "coupling_to_reality": _REALITY_COUPLING_MAP[key],
            "question": spec["question_answered"],
            "failure_mode": spec["failure_mode"],
        })
    return rows


# ═══════════════════════════════════════════════════════════
# AI REFERENCE
# ═══════════════════════════════════════════════════════════

AI_REFERENCE = {
    "purpose": (
        "Six measurement / validation domains, kept separate so "
        "that one domain's validation method is not used to "
        "invalidate another. Plus an IncentiveChannel / "
        "IncentiveAudit system for tracking how reward structures "
        "distort signal fidelity within any domain."
    ),
    "when_to_apply": [
        (
            "You need to decide which validation framework applies "
            "to a given question."
        ),
        (
            "You are comparing results across domains and need to "
            "avoid category errors."
        ),
        (
            "You are tracking why a system's reported metrics drift "
            "from its physical outcomes."
        ),
        (
            "You are scoring a system for substrate_audit.SystemScore "
            "and need reference values for signal_fidelity, "
            "feedback_latency, money_physics_coupling, or "
            "maintainer_control."
        ),
    ],
    "key_exports": {
        "MEASUREMENT_DOMAINS": (
            "Dict of 6 domain specs with scope, method, validation "
            "loop, strengths, limitations, failure mode, and the "
            "question each one answers."
        ),
        "IncentiveChannel": (
            "Dataclass: one reward channel with reward_basis, "
            "outcome_coupling, reward_latency, gradient_alignment, "
            "gameability, reward_distribution."
        ),
        "IncentiveAudit": (
            "Dataclass: aggregates channels on a system; computes "
            "alignment, incentive_entropy, and verdict."
        ),
        "REFERENCE_PROFILES": (
            "Dict of 6 pre-built IncentiveAudit instances, one per "
            "domain, showing typical values."
        ),
        "compare_domains": (
            "Function: returns compressed cross-scope comparison "
            "table (one record per domain)."
        ),
    },
    "integration_with_substrate_audit": {
        "outcome_coupling": (
            "Proxies substrate_audit.SystemScore.money_physics_coupling "
            "for the incentive layer."
        ),
        "reward_latency": (
            "Identical to substrate_audit.SystemScore.feedback_latency."
        ),
        "reward_distribution": (
            "Proxies substrate_audit.SystemScore.maintainer_control."
        ),
        "gameability": (
            "Degrades substrate_audit.SystemScore.signal_fidelity. "
            "Higher gameability means the signal can be rearranged "
            "without changing reality."
        ),
    },
    "common_mistakes": [
        (
            "Using one domain's validation method to invalidate "
            "another. Controlled RCTs are not superior to "
            "generational observation — they answer different "
            "questions."
        ),
        (
            "Treating outputs from one domain as complete "
            "representations of reality. Cellular biochemistry is "
            "correct locally but incomplete globally."
        ),
        (
            "Conflating high outcome_coupling with physical "
            "accuracy. A proxy metric can have high coupling to a "
            "lagged outcome and still miss systemic effects."
        ),
        (
            "Reading incentive_entropy as a moral score. It measures "
            "the degree to which signals can be rearranged without "
            "changing reality — a structural property, not a "
            "judgment about intent."
        ),
    ],
}


# ═══════════════════════════════════════════════════════════
# PRINT SUMMARY
# ═══════════════════════════════════════════════════════════

def print_summary() -> None:
    """Print full reference: 6 domains, cross-scope comparison,
    6 incentive profiles, and integration notes."""
    bar = "=" * 70
    sub = "-" * 70

    print(bar)
    print("DOMAIN TAXONOMY + INCENTIVE AUDIT — REFERENCE")
    print(bar)
    print()
    print(AI_REFERENCE["purpose"])
    print()

    print(sub)
    print("6 MEASUREMENT DOMAINS")
    print(sub)
    for key, spec in MEASUREMENT_DOMAINS.items():
        print(f"\n  {key}")
        print(f"    scope:    {spec['scope']}")
        print(f"    goal:     {spec['goal']}")
        print(f"    question: {spec['question_answered']}")
        print(f"    failure:  {spec['failure_mode']}")

    print()
    print(sub)
    print("CROSS-SCOPE COMPARISON")
    print(sub)
    header = (
        f"{'domain':<25} {'measurement':<20} "
        f"{'timescale':<14} {'coupling':<14}"
    )
    print(f"  {header}")
    print(f"  {'-' * 74}")
    for r in compare_domains():
        print(
            f"  {r['domain']:<25} {r['measurement_type']:<20} "
            f"{r['timescale']:<14} {r['coupling_to_reality']:<14}"
        )

    print()
    print(sub)
    print("INCENTIVE PROFILES BY DOMAIN")
    print(sub)
    print()
    for key, profile in REFERENCE_PROFILES.items():
        print(f"  {profile.name}")
        print(f"    alignment:         {profile.alignment:.3f}")
        print(f"    incentive_entropy: {profile.incentive_entropy():.3f}")
        print(f"    verdict:           {profile.verdict}")
        for c in profile.channels:
            print(
                f"      [{c.name}] "
                f"outcome={c.outcome_coupling} "
                f"latency={c.reward_latency} "
                f"gameable={c.gameability} "
                f"dist={c.reward_distribution}"
            )
        print()

    print(sub)
    print("INTEGRATION WITH substrate_audit.py")
    print(sub)
    integ = AI_REFERENCE["integration_with_substrate_audit"]
    for k, v in integ.items():
        print(f"  {k}:")
        words = v.split()
        line = "    "
        for w in words:
            if len(line) + len(w) > 64:
                print(line)
                line = "    " + w
            else:
                line += (w + " ")
        if line.strip():
            print(line)
        print()
    print(bar)


if __name__ == "__main__":
    print_summary()
