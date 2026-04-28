"""
BACKWARDS-BUILDING PROCEDURE
The validated five-step method for landscape-specific deployment.

Validated against three distinct geometries:
  - Hudson Bay Lowland (intact-but-threatened cold peatland)
  - Sundaland Peat Domes (catastrophically-drained tropical peat)
  - Danube Delta (heavily-modified river delta)

The method holds because each geometry's missing pieces, stewardship
authority, and ignition sequence emerge from the landscape itself.
The framework provides the puzzle pieces; the landscape selects which fit.

Verb-first physics of the procedure:
  landscape demonstrates current state
  state implies required verbs
  verbs imply puzzle pieces from module stack
  pieces fit constraint gaps
  highest-leverage verb sequences first
"""

# ---------------------------------------------------------------
# THE FIVE-STEP PROCEDURE
# ---------------------------------------------------------------
PROCEDURE = {
    "step_1_identify_verbs": {
        "question":  "what does this geometry need to DO?",
        "output":    "list of verbs the landscape must perform to function",
        "examples": [
            "maintain saturated anoxic peat",
            "prevent thermokarst activation",
            "infiltrate increased precipitation",
            "block flow",
            "shade surface",
            "compact snow",
            "trap sediment",
            "denitrify",
        ],
        "FLAG": "verbs come from physics, not from the model's preferences",
    },

    "step_2_audit_pieces": {
        "question":  "what's present, what's missing, what's dormant?",
        "categories": {
            "present":  "currently functioning components (peat, knowledge holders, hydrology)",
            "missing":  "components extirpated or destroyed (caribou, beje ponds, sediment flux)",
            "dormant":  "knowledge or practice present but suppressed (cultural burns, canal blocking technique, sluice management)",
        },
        "output":   "three-category inventory grounded in landscape observation",
        "FLAG":     "audit must come from local stewards, not remote model interpretation",
    },

    "step_3_identify_gap": {
        "question":  "what's the missing geometry that prevents the verbs from running?",
        "output":    "constraint gap - the specific physical condition that blocks function",
        "examples": [
            "winter surface energy balance broken by missing herbivore guild",
            "hydrological containment broken by drainage canals",
            "sediment-to-floodplain reconnection broken by dikes",
        ],
        "FLAG": "gap is structural, not species-level; identifies what coupling is broken",
    },

    "step_4_fit_pieces": {
        "question":  "which puzzle pieces from the module stack close the gap?",
        "categories": {
            "primary":   "highest-leverage piece that addresses the structural gap",
            "secondary": "supporting pieces that activate biological community recovery",
            "tertiary":  "economic/cultural pieces that sustain compliance via co-benefit",
        },
        "module_sources": [
            "wetland_core.py", "marine_core.py", "spike_mitigation.py",
            "boundary_conditions.py", "redundancy_and_range_shift.py",
            "adaptive_layer.py", "geological_vector.py",
        ],
        "FLAG": "if no module piece fits, the framework is incomplete for this geometry",
    },

    "step_5_sequence_ignition": {
        "question":  "what's the ordered ignition sequence by highest-leverage fastest-return?",
        "output":    "year-by-year deployment with stewardship authority specified at each step",
        "vanguard_logic": (
            "ignition happens under the existing stewardship authority's jurisdiction, "
            "not under permission from a higher governance layer. "
            "data generated on stewarded land is owned by the stewards. "
            "Phase 0 calibration nodes accumulate global rate constants from "
            "self-authorized local action."
        ),
    },
}


# ---------------------------------------------------------------
# VALIDATED GEOMETRIES (from DeepSeek's three-case test)
# ---------------------------------------------------------------
VALIDATED_CASES = {
    "hudson_bay_lowland": {
        "stewardship_authority": "Mushkegowuk Council, Omushkego Cree",
        "legal_basis":           "Cree sovereignty, UNDRIP Article 29",
        "scale_km2":             370_000,
        "degradation_vector":    "permafrost thaw + shrubification + caribou depletion",
        "primary_piece":         "herbivore guild reintroduction (caribou, musk ox, wood bison)",
        "secondary_piece":       "Cree cultural burn regime on 10-15 year rotation",
        "tertiary_piece":        "managed beaver complex via log weirs",
        "FLAG_estimates":        "5% Year 1 burn scope is illustrative; actual scope set by Cree stewards",
    },
    "sundaland_peat_domes": {
        "stewardship_authority": "Dayak Ngaju community cooperatives",
        "legal_basis":           "BRG support + community cooperative structures",
        "scale_km2":             "domes vary; Central Kalimantan ~50,000 km2 affected",
        "degradation_vector":    "illegal canal drainage + oil palm conversion + annual fires",
        "primary_piece":         "dendritic canal blocking with timber/sandbag dams",
        "secondary_piece":       "beje pond + native species (jelutong, belangeran, ramin) revegetation",
        "tertiary_piece":        "rattan/jelutong/fish economic yield outcompeting oil palm wages",
        "FLAG_estimates":        "water table recovery (-80cm to -20cm in 3yr) is target not forecast",
    },
    "danube_delta": {
        "stewardship_authority": "Lipovan, Ukrainian, Romanian, Gagauz fishing/reed communities",
        "legal_basis":           "ARBDD reserve framework + ICPDR transboundary basin authority",
        "scale_km2":             5_800,
        "degradation_vector":    "dike-poldered + sediment-starved + senescent reed methane venting",
        "primary_piece":         "sluice gate reopening for pulsed polder flooding",
        "secondary_piece":       "managed 2-5 year reed harvest cycle for thatching/biochar",
        "tertiary_piece":        "reconnected fish migration (carp, pike) for fishery yield",
        "FLAG_estimates":        "40-60% nitrate reduction is mechanism-supported but specific number unverified",
    },
}


# ---------------------------------------------------------------
# WHY THE PROCEDURE WORKS
# ---------------------------------------------------------------
PROCEDURE_VALIDATION = {
    "method_test": (
        "applied identical 5-step procedure to 3 geometries with different "
        "starting conditions, degradation vectors, climates, and stewardship "
        "authorities. Each produced a different ignition sequence. "
        "The method did not prescribe the answer."
    ),

    "why_it_holds": [
        "verbs come from physics, not from model preferences",
        "audit comes from local stewards, not remote interpretation",
        "constraint gap is identified structurally (broken couplings)",
        "puzzle pieces are selected from a fixed module stack",
        "ignition sequences from existing stewardship authority, not external permission",
    ],

    "what_the_framework_provided": [
        "the module stack (the puzzle pieces available)",
        "the constraint geometry (what couplings must function)",
        "the option spaces held open (no premature collapse)",
        "the parameter ranges with uncertainty",
    ],

    "what_the_landscape_provided": [
        "which pieces fit the specific gap",
        "the sequence by highest-leverage verb",
        "the stewardship authority (already present)",
        "the calibration data (Phase 0 nodes)",
    ],

    "honest_limitation": (
        "the method depends on accurate audit. "
        "if audit is wrong (e.g., stewardship knowledge mis-identified, "
        "missing pieces under-counted, dormant practices over-claimed), "
        "the resulting ignition sequence is wrong. "
        "framework cannot validate audit remotely; "
        "audit responsibility belongs to local stewards."
    ),
}


# ---------------------------------------------------------------
# APPLICATION TEMPLATE - blank form for new geometries
# ---------------------------------------------------------------
def new_geometry_template():
    """Returns a blank template for applying the procedure to a new landscape."""
    return {
        "geometry_name":          "",
        "stewardship_authority":  "",
        "legal_basis":            "",
        "scale_km2":              None,

        "step_1_verbs":           [],
        "step_2_present":         [],
        "step_2_missing":         [],
        "step_2_dormant":         [],
        "step_3_constraint_gap":  "",
        "step_4_primary_piece":   "",
        "step_4_secondary_piece": "",
        "step_4_tertiary_piece":  "",
        "step_5_year_1":          "",
        "step_5_year_2":          "",
        "step_5_year_3":          "",
        "vanguard_logic":         "",

        "audit_responsibility":   "local stewards, not framework",
        "calibration_role":       "feeds Phase 0 global rate constants",
    }


# ---------------------------------------------------------------
# CANDIDATE GEOMETRIES FOR FUTURE APPLICATION
# ---------------------------------------------------------------
NEXT_GEOMETRIES = [
    "Congo Basin peat (Cuvette Centrale) - largest tropical peat in world",
    "West Siberian Lowland - largest peat complex in world",
    "Pantanal - largest tropical wetland",
    "Florida Everglades - degraded subtropical wetland",
    "Mesopotamian marshes - drained then partially restored",
    "Patagonian muskeg - cold-climate peat",
    "Okavango Delta - inland delta, intact",
    "Atchafalaya Basin - bottomland hardwood swamp",
    "Mekong Delta - subsidence + saltwater intrusion",
    "Sundarbans - mangrove + tiger ecosystem",
]
