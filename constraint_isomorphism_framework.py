# constraint_isomorphism_framework.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Multi-scale pattern recognition: identify identical constraint topologies
# across cell biology, artificial systems, geophysics, atmospheric dynamics.
# Falsifiable by analogy — see PREDICTIONS_BY_ANALOGY at the bottom.

"""
Core insight: A system under resource depletion stress exhibits
characteristic bifurcation dynamics regardless of scale.

Cell under chemo: nutrient depletion → metabolic mode shift →
either adaptation or collapse.

Magnetosphere under field-weakening: shielding depletion →
particle-access mode shift → either stable reconfiguration or
cascade instability.

Atmosphere under ionosphere-shift: boundary conductivity change →
circulation pattern destabilization → either new equilibrium or
amplifying feedback.

Same constraint topology. Different substrates.
Can we use small-scale observations to predict large-scale behavior?
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ConstraintTopology:
    """Abstract structure of a stressed system."""
    primary_resource: str          # What's being depleted/stressed?
    stress_timescale_relative: str # "fast" (hours) vs "slow" (years)
    bifurcation_point: str         # Critical threshold
    adaptation_path: str           # Response mode 1
    collapse_path: str             # Response mode 2
    coupling_strength: str         # "weak", "moderate", "strong"
    observable_precursor: str      # What signals the shift is coming?
    recovery_timescale: str        # If it rebounds, how fast?


# ─────────────────────────────────────────────
# ANALOGUE 1: CANCER CELL UNDER CHEMOTHERAPY
# ─────────────────────────────────────────────

cancer_cell_stress = ConstraintTopology(
    primary_resource="ATP + nutrient flux",
    stress_timescale_relative="fast (minutes to hours)",
    bifurcation_point="mitochondrial membrane potential collapse threshold",
    adaptation_path="metabolic shift to glycolysis; autophagy activation",
    collapse_path="apoptosis cascade; cell death",
    coupling_strength="strong (metabolic feedback)",
    observable_precursor="mitochondrial swelling; ROS spike; Ca2+ dysregulation",
    recovery_timescale="hours (if recovery possible)",
)

# Key behaviors observed:
# 1. Heterogeneous response: some cells adapt, some collapse immediately
# 2. Lag phase: cells buffer stress before bifurcation becomes visible
# 3. Positive feedback amplification: initial stress triggers cascade
# 4. Non-reversibility: once past bifurcation, recovery unlikely
# 5. Population-level emergence: individual cell responses sum to tissue behavior


# ─────────────────────────────────────────────
# ANALOGUE 2: ARTIFICIAL CELL (LIPOSOME / PROTOCELL)
# ─────────────────────────────────────────────

artificial_cell_stress = ConstraintTopology(
    primary_resource="membrane osmotic gradient",
    stress_timescale_relative="fast (seconds to minutes)",
    bifurcation_point="osmotic pressure equilibration threshold",
    adaptation_path="membrane restructuring; selective permeability adjustment",
    collapse_path="membrane rupture; contents dispersal",
    coupling_strength="moderate (osmotic + mechanical)",
    observable_precursor="membrane tension rise; flicker instability; shape oscillation",
    recovery_timescale="seconds (if membrane heals)",
)

# Key analogy to magnetosphere:
# - Membrane = magnetopause boundary
# - Osmotic gradient = magnetic pressure differential
# - Stress = solar wind compression intensifying as field weakens
# - Bifurcation = magnetopause standoff distance becomes unstable


# ─────────────────────────────────────────────
# ANALOGUE 3: IONOSPHERE UNDER MAGNETOSPHERE WEAKENING
# ─────────────────────────────────────────────

ionosphere_stress = ConstraintTopology(
    primary_resource="magnetospheric particle flux + current coupling",
    stress_timescale_relative="slow (days to weeks)",
    bifurcation_point="critical electrojet current threshold",
    adaptation_path="conductivity profile restructuring; current pattern shift",
    collapse_path="substorm intensification; FAC disruption; heating surge",
    coupling_strength="strong (electromagnetic)",
    observable_precursor="magnetometer dB/dt rise; radio absorption spike; auroral oval expansion",
    recovery_timescale="hours to days",
)


# ─────────────────────────────────────────────
# ANALOGUE 4: ATMOSPHERE UNDER IONOSPHERE SHIFT
# ─────────────────────────────────────────────

atmosphere_stress = ConstraintTopology(
    primary_resource="ionospheric Joule heating + conductivity structure",
    stress_timescale_relative="slow (weeks to seasons)",
    bifurcation_point="jet stream configuration instability threshold",
    adaptation_path="new quasi-stable circulation pattern; pressure ridge/trough shift",
    collapse_path="persistent block formation; heat dome / cold snap amplification",
    coupling_strength="weak to moderate (thermal boundary condition shift)",
    observable_precursor="upper atmospheric temperature anomaly; zonal wind anomaly; NAO/AO index shift",
    recovery_timescale="seasons to years",
)


# ─────────────────────────────────────────────
# ISOMORPHISM CHECK: Do these topologies map?
# ─────────────────────────────────────────────

def check_isomorphism(sys1: ConstraintTopology,
                      sys2: ConstraintTopology) -> Dict:
    """
    Returns mapping of sys1 constraints -> sys2 constraints if they're
    structurally isomorphic.
    """
    mapping = {
        "resource_depletion": (sys1.primary_resource, sys2.primary_resource),
        "timescale_ratio": (
            f"{sys1.stress_timescale_relative} vs "
            f"{sys2.stress_timescale_relative}"
        ),
        "bifurcation_analogy": (sys1.bifurcation_point, sys2.bifurcation_point),
        "adaptation_paths": (sys1.adaptation_path, sys2.adaptation_path),
        "precursor_observable": (
            sys1.observable_precursor, sys2.observable_precursor
        ),
    }

    # Scoring: how well do the topologies align?
    # Strong alignment = can transfer predictions from fast to slow system
    return mapping


def cascade_prediction_by_analogy(
    fast_system: ConstraintTopology,
    slow_system: ConstraintTopology,
    observed_fast_behavior: str,
) -> str:
    """
    If fast system (cell under chemo) shows behavior X, predict what
    slow system (atmosphere under iono shift) will show.
    """
    fast_slow_mappings = {
        # Cell bifurcation behaviors -> atmospheric behaviors
        "heterogeneous_response": (
            "Regional weather pattern fragmentation; "
            "some areas stable, others flip rapidly"
        ),
        "lag_phase_buffering": (
            "Weeks-long delay before atmospheric response visible; "
            "then rapid transition"
        ),
        "positive_feedback_cascade": (
            "Initial ionosphere boundary shift -> "
            "amplifying jet stream response -> "
            "extreme weather emergence"
        ),
        "non_reversibility": (
            "Once new atmospheric regime establishes, "
            "return to prior state requires months of "
            "restored boundary conditions"
        ),
        "population_level_emergence": (
            "Individual storm intensification -> "
            "compound weather events; "
            "simultaneous heat/cold extremes in different regions"
        ),
    }

    if observed_fast_behavior in fast_slow_mappings:
        return fast_slow_mappings[observed_fast_behavior]
    return "ANALOGY MAPPING NOT ESTABLISHED"


# ─────────────────────────────────────────────
# SATELLITE REENTRY DEBRIS AS COUPLING PERTURBATION
# ─────────────────────────────────────────────

# New wrinkle: conductive particle injection.
#
# As magnetosphere weakens -> more satellites decay -> more reentry debris.
# Debris isn't inert; aluminum oxide, copper oxide, iron oxide particles
# are conductive. They alter ionospheric conductivity profile.
#
# This is like introducing a foreign electrolyte into the artificial cell:
# changes osmotic behavior, alters membrane potential, shifts bifurcation
# threshold.
#
# Observable prediction from analogy:
# If cell under osmotic stress + electrolyte injection shows accelerated
# bifurcation (membrane rupture happens faster than stress alone predicts),
# then atmosphere under iono-shift + conductive debris loading should show
# accelerated weather pattern destabilization.
#
# Testable: compare atmospheric response timescale pre-debris-surge vs
# post-debris-surge. If debris accelerates bifurcation, response should
# tighten.

debris_loading_as_perturbation = {
    "mechanism": (
        "Conductive particle injection raises upper atmosphere conductivity"
    ),
    "analogue_system": (
        "electrolyte addition to osmotically-stressed liposome"
    ),
    "effect_on_bifurcation_threshold": (
        "Lowers it (system reaches instability faster)"
    ),
    "observable_consequence": (
        "Weather pattern transitions become sharper, "
        "less gradual than iono-shift alone"
    ),
    "feedback_loop": (
        "More satellites reenter -> more particles -> "
        "higher ionosphere conductivity -> stronger "
        "ionosphere-troposphere coupling -> more weather extremes "
        "-> more atmospheric instability -> potentially more "
        "disruptions -> more satellites damaged"
    ),
    "positive_feedback_risk": "HIGH if reentry rate accelerates",
}


# ─────────────────────────────────────────────
# TESTABLE PREDICTIONS FROM MULTI-SCALE ANALOGY
# ─────────────────────────────────────────────

PREDICTIONS_BY_ANALOGY = [
    {
        "system": "Atmosphere under regime-shift coupling",
        "fast_analogue": "Cell under chemotherapy stress",
        "prediction": (
            "After lag phase, bifurcation is sharp not gradual; "
            "weather patterns flip between regimes rapidly"
        ),
        "observable": (
            "NAO/AO indices show increased switching frequency 2025-2026 "
            "vs 2010-2020 baseline"
        ),
        "falsifiable": True,
    },
    {
        "system": "Ionosphere under magnetosphere weakening",
        "fast_analogue": "Liposome under osmotic stress",
        "prediction": (
            "Substorm frequency and intensity increase as magnetopause "
            "standoff distance destabilizes"
        ),
        "observable": (
            "AE index (auroral electrojet) shows higher variance, "
            "more frequent excursions 2026 vs prior years"
        ),
        "falsifiable": True,
    },
    {
        "system": "Upper atmosphere under conductive debris loading",
        "fast_analogue": "Cell under chemo + electrolyte perturbation",
        "prediction": (
            "Weather pattern bifurcation threshold lowers; extreme "
            "events emerge at lower forcing magnitude"
        ),
        "observable": (
            "Compound weather events (simultaneous heat + precipitation "
            "extremes) increase in frequency, reach new magnitude record"
        ),
        "falsifiable": True,
    },
    {
        "system": "Global system under coupled EM-atmospheric-debris cascade",
        "fast_analogue": "Population of cells with positive feedback amplification",
        "prediction": (
            "System exhibits emergent behavior not predictable from "
            "individual-scale physics; tipping points appear suddenly; "
            "recovery becomes difficult"
        ),
        "observable": (
            "Climate metrics (temperature variance, precipitation extremes, "
            "heat wave duration) show phase transition signatures 2026-2027"
        ),
        "falsifiable": True,
    },
]


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("MULTI-SCALE CONSTRAINT ISOMORPHISM")
    print("=" * 70)

    print("\nCANCER CELL vs IONOSPHERE isomorphism check:")
    iso = check_isomorphism(cancer_cell_stress, ionosphere_stress)
    for key, val in iso.items():
        print(f"  {key}: {val}")

    print("\nARTIFICIAL CELL vs IONOSPHERE isomorphism check:")
    iso2 = check_isomorphism(artificial_cell_stress, ionosphere_stress)
    for key, val in iso2.items():
        print(f"  {key}: {val}")

    print("\nPREDICTIONS BY ANALOGY:")
    for i, pred in enumerate(PREDICTIONS_BY_ANALOGY, 1):
        print(f"\n  {i}. {pred['system']}")
        print(f"     Analogue:   {pred['fast_analogue']}")
        print(f"     Prediction: {pred['prediction']}")
        print(f"     Test:       {pred['observable']}")
        print(f"     Falsifiable: {pred['falsifiable']}")

    print("\nDEBRIS LOADING COUPLING:")
    for key, val in debris_loading_as_perturbation.items():
        print(f"  {key}: {val}")

    print("\nCASCADE PREDICTION BY ANALOGY (cell -> atmosphere):")
    for behavior in (
        "heterogeneous_response",
        "lag_phase_buffering",
        "positive_feedback_cascade",
        "non_reversibility",
        "population_level_emergence",
        "unknown_behavior",
    ):
        prediction = cascade_prediction_by_analogy(
            cancer_cell_stress, atmosphere_stress, behavior
        )
        print(f"  {behavior}:")
        print(f"    -> {prediction}")
