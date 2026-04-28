"""
BOUNDARY CONDITIONS - NESTED THRESHOLDS
The buffer species that protect the carbon-sink species have their own boundaries.
If buffer crosses threshold, sink fails.

Verb-first physics:
warming exceeds kelp tolerance UNLESS otter suppresses urchin
warming exceeds otter tolerance -> otter buffer fails -> kelp buffer fails
permafrost thaws UNLESS herbivore density compacts snow + maintains albedo
herbivore enteric methane partially offsets permafrost C protection
warming exceeds herbivore range -> herbivore buffer fails -> permafrost protection fails

This is nested: the buffer has a buffer has a constraint.
"""

# —————————————————————

# KELP - OTTER NESTED BUFFER

# —————————————————————

KELP_BUFFER = {
"kelp_thermal_max_C": {
"value": 22, "range": (20, 24),
"note": "varies by species; bull kelp lower, giant kelp higher",
},
"otter_thermal_max_C": {
"value": 20, "range": (16, 22),
"FLAG": "sea otters need cold water for fur insulation thermoregulation; not a hard kill threshold but range-shift driver",
},
"otter_kelp_thermal_lift_C": {
"value": 2.5, "range": (1.5, 4.0),
"source": "empirical from 2014-2016 NE Pacific MHW survival comparison",
"note": "kelp survives ~2.5C higher SST when otters present, via urchin suppression",
},
"lobster_atlantic_substitute": {
"applies_to": "North Atlantic green urchin systems",
"thermal_lift_C": {"value": 1.8, "range": (1.0, 3.0), "FLAG": "less data than otter case"},
},

"FAILURE_MODE_NESTED": (
    "if SST > otter_thermal_max for sustained period, otter range shifts north, "
    "leaving lower-latitude kelp without buffer; kelp then fails at its own threshold"
),

}

# —————————————————————

# PERMAFROST - HERBIVORE NESTED BUFFER

# —————————————————————

PERMAFROST_BUFFER = {
"soil_T_thaw_threshold_C": {
"value": 0.0,
"note": "permafrost defined as soil <0C for >2 consecutive years",
},
"herbivore_winter_cooling_C": {
"value": 2.0, "range": (1.5, 4.0),
"source": "Zimov et al, Pleistocene Park, soil T at 1m depth",
"FLAG": "single-site data; replication elsewhere not yet done at scale",
},
"herbivore_summer_albedo_lift": {
"value": 0.10, "range": (0.05, 0.15),
"note": "grassland albedo ~0.20 vs dark shrub/larch ~0.10",
},

# the methane coupling DeepSeek skipped
"enteric_CH4_per_animal_kg_yr": {
    "reindeer":      {"value":  20, "range": (15, 25)},
    "yakutian_horse":{"value":  35, "range": (25, 45)},
    "bison":         {"value":  60, "range": (50, 75)},
    "musk_ox":       {"value":  25, "range": (20, 35)},
},

"required_density_per_km2": {
    "value": 10, "range": (5, 20),
    "note": "Pleistocene Park target stocking density, mixed species LSU equivalent",
},

"FAILURE_MODE_NESTED": (
    "if regional warming exceeds herbivore range tolerance (varies by species), "
    "or if predator pressure not managed, herbivore density falls below threshold, "
    "snow no longer compacted, summer albedo not maintained, permafrost thaws"
),

}

def permafrost_net_benefit(area_km2, density_per_km2, species_mix, warming_avoided_GtC):
    """
    Compute net warming benefit of herbivore-permafrost protection.
    Subtracts enteric CH4 cost from C-protection benefit.

    ```
    species_mix: dict of fraction by species, e.g. {"reindeer": 0.5, "bison": 0.3, ...}
    warming_avoided_GtC: gross C kept frozen if intervention works
    """
    p = PERMAFROST_BUFFER["enteric_CH4_per_animal_kg_yr"]
    total_animals = area_km2 * density_per_km2

    annual_CH4_kg = 0
    for sp, frac in species_mix.items():
        annual_CH4_kg += total_animals * frac * p[sp]["value"]

    # CH4 in CO2eq, GWP100=28
    annual_CH4_CO2eq_Gt = annual_CH4_kg * 28 * (44/16) / 1e12

    # gross C avoided -> CO2eq
    avoided_CO2eq_Gt = warming_avoided_GtC * (44/12)

    return {
        "gross_avoided_CO2eq_Gt_yr":   avoided_CO2eq_Gt,
        "enteric_CH4_CO2eq_Gt_yr":     annual_CH4_CO2eq_Gt,
        "net_benefit_CO2eq_Gt_yr":     avoided_CO2eq_Gt - annual_CH4_CO2eq_Gt,
        "ratio_benefit_to_cost":       avoided_CO2eq_Gt / annual_CH4_CO2eq_Gt if annual_CH4_CO2eq_Gt else float('inf'),
    }

# —————————————————————

# GOVERNANCE - HELD AS OPTION SPACE, NOT RESOLVED

# —————————————————————

GOVERNANCE_PROTOCOLS = {
"competence_demonstration": {
"description": "DeepSeek proposal: authority flows from demonstrated ecological outcomes",
"constraint":  "requires both parties to consent to the test and accept outcomes",
"failure_mode":"existing legal-political system may not recognize outcome",
},
"treaty_recognition": {
"description": "honor existing indigenous treaty rights as recognized by international law (UNDRIP)",
"constraint":  "treaty enforcement varies by state",
"failure_mode":"signatory states may withdraw or fail to implement",
},
"land_back_purchase": {
"description": "philanthropic or trust-based return of title to historical stewards",
"constraint":  "requires capital and willing seller",
"failure_mode":"slow; cannot scale to planetary timeline within decade",
},
"co_management": {
"description": "shared decision authority between state agencies and stewardship guilds",
"constraint":  "depends on existing legal frameworks (e.g., US-tribal co-management)",
"failure_mode":"state can revoke; subject to political cycles",
},
"bottom_up_continuation": {
"description": "stewards continue practice on accessible land regardless of formal recognition",
"constraint":  "limited to land already accessible; cannot recover drained peat under private title",
"failure_mode":"cannot reach planetary scale without legal change",
},
}

# —————————————————————

# STAGED COMMITMENT STRUCTURE

# —————————————————————

STAGED_ROLLOUT = {
"phase_0_calibration": {
"duration_yr":  3,
"scope":        "100 test nodes across major peat biomes + paired marine sites",
"biomes":       ["Congo basin peat", "West Siberian lowland", "Hudson Bay lowland",
"Sundaland peat domes", "Patagonian muskeg", "Okavango delta",
"Boreal Fennoscandia", "North American Great Lakes peatlands"],
"instruments":  ["flux towers", "airborne CH4 lidar", "stewardship guild observations"],
"output":       "biome-specific Bayesian-updated rate constants",
},
"phase_1_constrained_scale": {
"duration_yr":  "starts year 4",
"scope":        "scale to biomes where calibration data shows positive net flux benefit",
"constraint":   "do not scale into biomes where uncertainty bounds cross zero",
"output":       "data-constrained global drawdown estimate with narrow bounds",
},
"ongoing_adaptive": {
"scope":        "stewardship guilds as sensor and actuator at each site",
"feedback":     "near-real-time water level, grazer density, harvest intensity adjustments",
"global_total": "distributed computation, continuously updated, not theoretical projection",
},
}
