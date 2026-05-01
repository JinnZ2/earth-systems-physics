"""
CROSS-COMPONENT COUPLINGS
The architecture's documented couplings between sinks, made
quantitative for Monte Carlo propagation.

Verb-first physics:
  wetland traps N -> coast de-eutrophies -> kelp stabilizes -> deeper export
  basalt raises soil pH -> earthworm survival improves -> aggregate formation rises
  earthworm porosity maintains aerobic rhizosphere -> wetland CH4 spike reduced
  herbivore density compacts snow -> winter cooling persists -> permafrost C protected

The simple-sum Monte Carlo in run_full_stack.monte_carlo treats the
six components as independent. The architecture (docs/ARCHITECTURE.md)
documents real couplings between them. This module makes the couplings
explicit so a coupled Monte Carlo can be run alongside the independent
one and the headline difference reported honestly.

Each coupling is FLAGGED as ESTIMATED. None is measured at coupled-
system scale. Multiplier ranges are deliberately small (<= 15%) so the
coupled Monte Carlo perturbs the headline rather than restructuring it.
"""

# ---------------------------------------------------------------
# COUPLING DEFINITIONS
# ---------------------------------------------------------------

COUPLINGS = {
    "wetland_to_kelp": {
        "verb_chain":       "wetland traps N -> coast de-eutrophies -> kelp stabilizes -> deeper export",
        "affects":          "kelp",
        "direction":        "positive",
        "multiplier_range": (1.00, 1.10),
        "FLAG":             "ESTIMATED. No coupled-system measurement at scale.",
        "source":           "marine_core.COUPLING_TERMS.river_nutrient_export",
    },

    "erw_to_adaptive": {
        "verb_chain":       "basalt dust raises soil pH -> earthworm survival improves -> aggregate formation rises",
        "affects":          "adaptive",
        "direction":        "positive",
        "multiplier_range": (1.00, 1.08),
        "FLAG":             "ESTIMATED. Effect size depends on geographic overlap of ERW deployment with adaptive stewardship area.",
        "source":           "geological_vector.COUPLING_TO_BIO_STACK.soil_pH_buffering",
    },

    "adaptive_to_wetland_spike": {
        "verb_chain":       "earthworm porosity maintains aerobic rhizosphere -> wetland CH4 spike reduced",
        "affects":          "wetland_spike_only",  # transient, not steady-state headline
        "direction":        "positive",
        "multiplier_range": (0.55, 1.00),  # reduces spike by 0-45%
        "FLAG":             "ESTIMATED. Affects transient (years 2-15) only; not applied to the steady-state headline.",
        "source":           "adaptive_layer.COUPLING_TO_OTHER_SINKS.wetland_methane_spike",
    },

    "herbivore_to_albedo": {
        "verb_chain":       "herbivore density compacts snow -> winter cooling persists -> summer albedo lifted -> permafrost C protected",
        "affects":          "permafrost",
        "direction":        "positive",
        "multiplier_range": (1.00, 1.05),
        "FLAG":             "ESTIMATED. Largely captured already in the permafrost warming_avoided_GtC input range; small additional bump.",
        "source":           "boundary_conditions.PERMAFROST_BUFFER.herbivore_summer_albedo_lift",
    },
}


# ---------------------------------------------------------------
# WHAT IS NOT MODELED HERE
# ---------------------------------------------------------------

NOT_MODELED = {
    "land_overlap_double_counting": (
        "Adaptive layer (50-500M ha) and ERW (75-300M ha) can deploy on "
        "the same hectares. They are NOT double-counting because adaptive "
        "stores C as soil aggregates + glomalin (top 30cm), while ERW "
        "exports C as bicarbonate to the ocean (different carbon pool, "
        "different residence-time domain). Same field, different sinks."
    ),
    "wetland_overlap": (
        "Wetland restoration occurs on saturated land; adaptive layer and "
        "ERW occur on aerobic land. Geographic overlap is small; not modeled."
    ),
    "transient_methane_spike": (
        "Wetland CH4 spike during years 2-15 of restoration is real and "
        "documented in wetland_core.PARAMS.spike_magnitude_factor (3x baseline). "
        "The steady-state headline does NOT include the transient. The "
        "adaptive_to_wetland_spike coupling above modulates the transient "
        "but is not applied to the steady-state Monte Carlo."
    ),
    "ocean_alkalinity_feedback": (
        "Wetland alkalinity export to coastal zones partially buffers "
        "ocean acidification, supporting kelp. Same direction as "
        "wetland_to_kelp; folded into that coupling rather than modeled "
        "separately to avoid double-counting."
    ),
}


# ---------------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------------

def sample_coupling_multipliers(rng):
    """
    Draw one Monte Carlo sample of coupling multipliers.
    rng must expose .uniform(a, b) (the stdlib `random` module qualifies).
    Returns a dict keyed by coupling name.
    """
    return {k: rng.uniform(*v["multiplier_range"]) for k, v in COUPLINGS.items()}


def apply_to_components(components, multipliers):
    """
    Apply sampled coupling multipliers to a per-iteration components dict.

    components: dict with keys peat, other, kelp, perm, adapt, erw (Gt C / yr each)
    multipliers: dict from sample_coupling_multipliers()
    Returns: new components dict with couplings applied.

    Couplings affecting only the transient spike are NOT applied here;
    they are tracked in COUPLINGS but the steady-state headline ignores them.
    """
    out = dict(components)
    out["kelp"]  *= multipliers["wetland_to_kelp"]
    out["adapt"] *= multipliers["erw_to_adaptive"]
    out["perm"]  *= multipliers["herbivore_to_albedo"]
    # adaptive_to_wetland_spike: transient only, not applied here
    return out
