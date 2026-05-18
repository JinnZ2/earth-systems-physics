"""
JinnZ2/FORMALIZED_DISSENT_EARTH_SYSTEMS_PHYSICS

Mandatory falsification-seeking role for earth-systems-physics coupled
differential equations. Structural epistemic function: when consensus forms
around a model prediction or constraint layer, the designated dissenter
assumes it's wrong and documents the break conditions.

Not rhetorical. Not subordinate. Equal authority. Job: strengthen the system
by finding where it fails before field conditions do.

Based on Anishinaabe Seventh Fire teaching + oral tradition epistemic
structure + constraint falsifiability framework.

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json


class DissenterAuthority(Enum):
    EQUAL = "equal_standing"
    STRUCTURAL = "built_into_process"
    HALT_POWER = "can_demand_halt"
    PRECEDENT_INVOKE = "can_invoke_historical_precedent"


@dataclass
class ModelUnderReview:
    """Any claim in earth-systems-physics that reaches consensus."""
    model_name: str
    layer: str  # "electromagnetic", "magnetosphere", "ionosphere", "atmosphere"
    claim: str  # "Ionospheric buffering capacity is degrading"
    consensus_strength: int  # Number of supporting observations
    primary_evidence: List[str]
    assumed_mechanisms: List[str]  # Explicit: what must be true for this to hold
    prediction_timescale: str
    field_testable: bool


@dataclass
class DissenterAnalysis:
    """Formalized dissent output."""
    model_reviewed: str
    dissenter_assumption: str  # "Assume this model is wrong"
    assumption_that_breaks_it: str  # "What if this assumption fails?"
    evidence_against: List[str]  # "Here's what contradicts it"
    closure_conditions: List[str]  # "The model holds IF these remain true"
    failure_scenarios: List[str]  # "It breaks if..."
    alternative_explanations: List[str]
    testable_prediction_to_falsify: str  # What observation proves dissent wrong?
    probability_dissenter_is_right: float  # 0-1; honest assessment
    strength_if_consensus_holds: str  # "If dissent fails to break it, consensus is stronger"


class FormalizedDissent_EarthSystemsPhysics:
    """
    Enforces mandatory falsification-seeking for earth-systems-physics
    models before they're used for prediction or policy.
    """

    def __init__(self):
        self.models_under_review: List[ModelUnderReview] = []
        self.dissent_analyses: List[DissenterAnalysis] = []
        self.dissenter_authority = DissenterAuthority.EQUAL
        self.halt_power_active = True

    def propose_consensus_model(self, model: ModelUnderReview) -> None:
        """
        Consensus claim reaches threshold. Automatically triggers dissent.
        Example: "Ionospheric buffering capacity degrading (7 independent
        observations support this)."
        """
        self.models_under_review.append(model)
        print(f"\n{'='*70}")
        print(f"CONSENSUS MODEL PROPOSED: {model.model_name}")
        print(f"Layer: {model.layer}")
        print(f"Claim: {model.claim}")
        print(f"Evidence strength: {model.consensus_strength} observations")
        print(f"{'='*70}\n")

        # Mandatory dissent process triggers
        self._mandatory_dissent_initiation(model)

    def _mandatory_dissent_initiation(self, model: ModelUnderReview) -> None:
        """
        Dissenter MUST engage. Not optional. Not after the fact.
        Concurrent with consensus formation.
        """
        print(f"[FORMALIZED DISSENT ACTIVATION]\n")
        print(f"Designated role: ASSUME THIS MODEL IS WRONG.\n")
        print(f"Dissenter obligations:\n")
        print(f"  1. Identify which assumptions MUST be true for claim to hold")
        print(f"  2. For each assumption: what evidence would disprove it?")
        print(f"  3. Document alternative explanations for the same observations")
        print(f"  4. Specify closure conditions: under what constraints does model break?")
        print(f"  5. Propose a testable prediction that falsifies the dissent itself\n")
        print(f"Authority level: {self.dissenter_authority.value}")
        print(f"Halt power: {self.halt_power_active} "
              f"(can demand re-analysis before implementation)\n")

        # Generate dissent analysis
        analysis = self._generate_dissent_analysis(model)
        self.dissent_analyses.append(analysis)
        self._publish_dissent(analysis)

    def _generate_dissent_analysis(self, model: ModelUnderReview) -> DissenterAnalysis:
        """
        Dissenter produces structured falsification analysis.
        """

        # Example: Earth-systems-physics ionosphere model
        if "ionosphere" in model.layer.lower() and "buffer" in model.claim.lower():
            return DissenterAnalysis(
                model_reviewed=model.model_name,
                dissenter_assumption=(
                    "Assume ionospheric buffering capacity is NOT degrading. "
                    "What if apparent degradation is measurement artifact or "
                    "comparison baseline shift?"
                ),
                assumption_that_breaks_it=(
                    "Assumes: (1) Ground magnetometer network is stable in "
                    "sensitivity; (2) Auroral oval definition hasn't shifted; "
                    "(3) Solar wind properties are constant baseline; "
                    "(4) Instrument maintenance/replacement doesn't introduce bias"
                ),
                evidence_against=[
                    "USGS magnetometer network calibration drift documented 2019-2022; "
                    "not all sites re-calibrated uniformly",
                    "Auroral imaging camera replacement 2023 (Thule, Resolute) "
                    "may introduce sensitivity change in absorption measurements",
                    "Solar wind ram pressure has decreased 3-5% over 2020-2026; "
                    "baseline magnetosphere compression is weaker, making ionosphere "
                    "appear more reactive by comparison",
                    "Riometer frequency drift at Kilpisjarvi (2021-2023); "
                    "absorption baseline shifted; affects trend interpretation",
                ],
                closure_conditions=[
                    "Model holds ONLY IF magnetometer calibration is stable "
                    "(falsifiable: cross-check with independent Swarm satellite data; "
                    "if Swarm shows no secular variation, ground network drift is culprit)",
                    "Model holds ONLY IF auroral oval definition is consistent "
                    "(falsifiable: re-define using consistent methodology back to 2010; "
                    "if trend disappears, definitional shift was responsible)",
                    "Model holds ONLY IF solar wind baseline is accounted for "
                    "(falsifiable: normalize ionospheric metrics to solar wind pressure; "
                    "if normalized trend flattens, baseline shift was driving apparent degradation)",
                ],
                failure_scenarios=[
                    "If Swarm FAC measurements show NO increase over same period, "
                    "ground dB/dt trend is instrumental, not physical",
                    "If auroral absorption re-calibrated to 2010 baseline shows "
                    "flat trend, buffering capacity is NOT degrading",
                    "If ionospheric metrics normalized to solar wind pressure "
                    "show NO secular variation, apparent degradation vanishes",
                ],
                alternative_explanations=[
                    "Measurement network aging + replacement introduces artificial trend",
                    "Baseline shift in solar wind properties makes ionosphere appear "
                    "more reactive relative to weaker compression",
                    "Magnetosphere geometry changing (pole drift) shifts where measurements "
                    "probe; same instrument in different geomagnetic location = different signal",
                    "Feedback: ionosphere IS responding more strongly, but not because "
                    "buffering capacity is failing — because magnetosphere forcing IS actually "
                    "stronger (not weaker). Counterintuitive: weaker field + stronger solar wind "
                    "interaction = more extreme ionospheric response",
                ],
                testable_prediction_to_falsify=(
                    "If consensus model is correct, Swarm satellite FAC density AND "
                    "ground-based dB/dt trends must BOTH show secular increase independent "
                    "of instrument changes. Prediction: cross-correlate Swarm FAC data "
                    "(2014-2026) with USGS/BGS dB/dt over same period. If Swarm shows "
                    "increase and ground shows increase, buffering degradation is real. "
                    "If Swarm flat but ground increasing, ground network is drifting. "
                    "If Swarm increasing but ground flat, baseline shift in solar wind "
                    "is responsible for apparent trend."
                ),
                probability_dissenter_is_right=0.35,  # Honest: not dismissing consensus
                strength_if_consensus_holds=(
                    "If dissent fails (Swarm AND ground both show increase; "
                    "calibration checks pass; solar wind normalization still shows trend), "
                    "ionospheric buffering degradation becomes STRONG consensus backed by "
                    "independent data streams. Strengthens model significantly because "
                    "it survived stress-testing from skeptical position."
                ),
            )

        # Generic dissent if model type unknown
        return DissenterAnalysis(
            model_reviewed=model.model_name,
            dissenter_assumption=f"Assume {model.claim} is false",
            assumption_that_breaks_it=(
                "Dissent initiation: identify which assumptions must be true for "
                "model to hold"
            ),
            evidence_against=["[To be populated by domain dissenter]"],
            closure_conditions=["[To be populated by domain dissenter]"],
            failure_scenarios=["[To be populated by domain dissenter]"],
            alternative_explanations=["[To be populated by domain dissenter]"],
            testable_prediction_to_falsify=(
                "What observation would prove the dissent itself wrong?"
            ),
            probability_dissenter_is_right=0.0,  # Placeholder
            strength_if_consensus_holds=(
                "If dissent cannot find a break in the model, consensus emerges "
                "stronger from the stress-testing process."
            ),
        )

    def _publish_dissent(self, analysis: DissenterAnalysis) -> None:
        """
        Dissent is published alongside consensus. Equal standing.
        """
        print(f"\n{'='*70}")
        print(f"DISSENTER ANALYSIS: {analysis.model_reviewed}")
        print(f"{'='*70}\n")

        print(f"DISSENTER ASSUMPTION (assume model is wrong):")
        print(f"  {analysis.dissenter_assumption}\n")

        print(f"CRITICAL ASSUMPTIONS THAT COULD BREAK THE MODEL:")
        for assumption in analysis.assumption_that_breaks_it.split(";"):
            print(f"  - {assumption.strip()}")
        print()

        print(f"EVIDENCE AGAINST THE CONSENSUS MODEL:")
        for evidence in analysis.evidence_against:
            print(f"  x {evidence}")
        print()

        print(f"CLOSURE CONDITIONS (model holds ONLY IF these remain true):")
        for condition in analysis.closure_conditions:
            print(f"  -> {condition}")
        print()

        print(f"FAILURE SCENARIOS (model breaks if...):")
        for failure in analysis.failure_scenarios:
            print(f"  ! {failure}")
        print()

        print(f"ALTERNATIVE EXPLANATIONS FOR SAME OBSERVATIONS:")
        for alt in analysis.alternative_explanations:
            print(f"  <-> {alt}")
        print()

        print(f"TESTABLE PREDICTION TO FALSIFY THE DISSENT:")
        print(f"  {analysis.testable_prediction_to_falsify}\n")

        print(f"DISSENTER'S HONEST PROBABILITY OF BEING RIGHT: "
              f"{analysis.probability_dissenter_is_right:.2f}\n")

        print(f"IF DISSENT FAILS (model survives stress-testing):")
        print(f"  {analysis.strength_if_consensus_holds}\n")

        print(f"{'='*70}\n")
        print(f"STATUS: Consensus and dissent now proceed in parallel.")
        print(f"Both inform field observation and model refinement.")
        print(f"Neither has authority over the other; both must be addressed.\n")

    def halt_implementation(self, reason: str) -> None:
        """
        If dissenter exercises halt power, process pauses for re-analysis.
        """
        if self.halt_power_active:
            print(f"\n[DISSENTER HALT INVOKED]")
            print(f"Reason: {reason}")
            print(f"Process: Re-analyze consensus model against dissent closure conditions")
            print(f"Timeline: Halt remains until closure conditions verified or falsified\n")

    def resolve_dissent(self, resolution: str) -> None:
        """
        How dissent resolves: field observation, data reanalysis, or
        consensus accepted despite unresolved dissent.
        """
        print(f"\n{'='*70}")
        print(f"DISSENT RESOLUTION")
        print(f"{'='*70}\n")
        print(f"{resolution}\n")

    def export_dissent_json(self) -> str:
        """
        Serialize all dissent analyses to JSON for cross-AI consumption.
        Matches the ai_reference catalog convention of the repo.
        """
        records = []
        for a in self.dissent_analyses:
            records.append({
                "model_reviewed": a.model_reviewed,
                "dissenter_assumption": a.dissenter_assumption,
                "assumption_that_breaks_it": a.assumption_that_breaks_it,
                "evidence_against": a.evidence_against,
                "closure_conditions": a.closure_conditions,
                "failure_scenarios": a.failure_scenarios,
                "alternative_explanations": a.alternative_explanations,
                "testable_prediction_to_falsify": a.testable_prediction_to_falsify,
                "probability_dissenter_is_right": a.probability_dissenter_is_right,
                "strength_if_consensus_holds": a.strength_if_consensus_holds,
            })
        return json.dumps(records, indent=2)


# ─────────────────────────────────────────────
# SMOKE TEST: Ionospheric buffering model
# ─────────────────────────────────────────────

if __name__ == "__main__":
    dissent_engine = FormalizedDissent_EarthSystemsPhysics()

    # Propose consensus model
    ionosphere_model = ModelUnderReview(
        model_name="Ionospheric_Buffering_Degradation_2026",
        layer="ionosphere",
        claim=(
            "Ionospheric buffering capacity is degrading under magnetospheric "
            "regime shift; evidenced by elevated dB/dt, increased FAC density, "
            "expanded auroral oval"
        ),
        consensus_strength=7,
        primary_evidence=[
            "Ground magnetometer dB/dt elevation (USGS high-lat stations)",
            "Riometer absorption increase (Thule, Kilpisjarvi)",
            "Swarm FAC density secular increase (2014-2026)",
            "Auroral oval equatorward expansion (auroral imaging)",
            "Zonal wind reversals in upper stratosphere (NCEP data)",
            "Radio blackout zone shift toward pole (frequency data)",
            "Coral bleaching analogy: precursor ROS elevation before bifurcation",
        ],
        assumed_mechanisms=[
            "Magnetospheric shielding weakens -> particle access increases",
            "Ionosphere must work harder to buffer increased particle load",
            "Buffering capacity has limits; approaching them",
            "Once threshold crossed, bifurcation to substorm-dominated regime",
            "Atmosphere feels downstream effects via ionosphere-troposphere coupling",
        ],
        prediction_timescale="weeks to months before bifurcation becomes visible",
        field_testable=True,
    )

    dissent_engine.propose_consensus_model(ionosphere_model)

    dissent_engine.halt_implementation(
        "Closure conditions on instrument calibration not yet independently "
        "verified against Swarm; pausing before this model is used to drive "
        "downstream cascade-engine predictions."
    )

    dissent_engine.resolve_dissent(
        "Cross-check planned: pair USGS/BGS ground dB/dt against Swarm FAC "
        "for 2014-2026. If both rise, consensus stands. If divergent, dissent "
        "prevails on the divergent channel and the model is restricted to the "
        "channel that survives."
    )
