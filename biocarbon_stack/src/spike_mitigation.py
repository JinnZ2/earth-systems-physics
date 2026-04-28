"""
TRANSITION METHANE MITIGATION
Management interventions during the rewet-spike window.

Verb-first physics:
drawdown exposes sediment to O2
O2 kills obligate methanogens
O2 enables methanotroph colonization
selective harvest removes aerenchyma chimney
sphagnum inoculation seeds CH4 oxidizer community
Fe/SO4 amendment shifts substrate competition away from methanogens

All compression factors are ESTIMATED, not derived.
Flagged as such. Bracket ranges given.
"""

INTERVENTIONS = {
"managed_drawdown_seasonal": {
"mechanism":          "expose sediment to O2 in non-growing season",
"spike_reduction":    {"value": 0.30, "range": (0.15, 0.50), "FLAG": "ESTIMATED, no peer-reviewed compression factor"},
"co_benefit":         "drawdown-germinating species: wild rice, smartweed",
"constraint":         "requires hydrologic control infrastructure or beaver complex with managed outlets",
"failure_mode":       "if drawdown too deep/long, accelerates peat oxidation -> CO2 release",
},

"methane_chimney_harvest": {
    "mechanism":          "remove aerenchymous plant tissue that bypasses rhizosphere oxidation",
    "spike_reduction":    {"value": 0.20, "range": (0.10, 0.35), "FLAG": "ESTIMATED, varies by species and harvest intensity"},
    "co_benefit":         "rhizome starch, pollen, fiber yield",
    "constraint":         "must distinguish native cattail/bulrush from invasive Phragmites; only native fits the steady-state community",
    "failure_mode":       "over-harvest -> loss of O2 transport to root zone -> increased deep methanogenesis",
},

"sphagnum_methanotroph_inoculation": {
    "mechanism":          "seed CH4-oxidizing bacterial community on water surface",
    "spike_reduction":    {"value": 0.25, "range": (0.10, 0.40), "FLAG": "ESTIMATED, depends on inoculant viability and source-recipient match"},
    "co_benefit":         "accelerates peat formation timeline",
    "constraint":         "requires donor wetland with established methanotroph community; biocompatibility check on local water chemistry",
    "failure_mode":       "donor community may not establish under different pH/temp regime",
},

"iron_sulfate_amendment": {
    "mechanism":          "shift microbial substrate competition from methanogenesis to Fe/SO4 reduction",
    "spike_reduction":    {"value": 0.35, "range": (0.20, 0.55), "FLAG": "supported by AOM literature, but field-scale dosing not well-characterized"},
    "co_benefit":         "mimics natural mineral weathering pulse",
    "constraint":         "dose must stay below toxicity threshold for native invertebrates and amphibians",
    "failure_mode":       "over-dose -> sulfide accumulation -> shift from CH4 problem to H2S problem",
},

}

def combined_spike_reduction(active_interventions, params=INTERVENTIONS):
    """
    Combine reductions multiplicatively (not additively - they target overlapping CH4 sources).
    Returns (best_case, central_case, worst_case) reduction fractions.
    """
    best = central = worst = 1.0
    for k in active_interventions:
        r = params[k]["spike_reduction"]
        worst   *= (1 - r["range"][0])
        central *= (1 - r["value"])
        best    *= (1 - r["range"][1])
    return {
    "best_case_remaining_spike":    best,
    "central_remaining_spike":      central,
    "worst_case_remaining_spike":   worst,
    "best_case_reduction":          1 - best,
    "central_reduction":            1 - central,
    "worst_case_reduction":         1 - worst,
    }

# —————————————————————

# OPTION SPACE for Phase 2 - hold the space, don't collapse it

# —————————————————————

PHASE_2_OPTIONS = {
"enhanced_rock_weathering": {
"mechanism":     "ground basalt + acidic peatland water -> bicarbonate -> ocean alkalinity",
"potential_GtC": (0.5, 4.0),
"EROI":          "moderate, mining + grinding + transport",
"failure_mode":  "particle size dependent; too coarse = no reaction; too fine = dust hazard",
"timescale":     "100,000 yr lock-in once converted to bicarbonate",
"FLAG":          "DeepSeek doc collapsed to this option; it is one of several",
},
"biochar_at_scale": {
"mechanism":     "pyrolysis of biomass waste -> stable C in soil",
"potential_GtC": (0.5, 2.0),
"EROI":          "depends entirely on feedstock and pyrolysis energy source",
"failure_mode":  "feedstock competition with other land uses",
"timescale":     "100-1000 yr stability in soil",
},
"ocean_alkalinity_enhancement": {
"mechanism":     "direct addition of alkaline minerals to surface ocean",
"potential_GtC": (0.1, 5.0),
"EROI":          "highly variable",
"failure_mode":  "ecosystem effects of pH manipulation; mining footprint",
"timescale":     "10,000+ yr",
"FLAG":          "high uncertainty, contested",
},
"BECCS": {
"mechanism":     "bioenergy with carbon capture and storage",
"potential_GtC": (0.5, 5.0),
"EROI":          "negative without subsidy in most current configurations",
"failure_mode":  "land use competition with food and biocultural restoration",
"timescale":     "geologic, if storage holds",
"FLAG":          "competes directly with Phase 1 land base",
},
"DAC": {
"mechanism":     "direct air capture, mechanical/chemical",
"potential_GtC": (0.0, 2.0),
"EROI":          "negative at current tech, depends on energy source",
"failure_mode":  "energy source carbon intensity",
"timescale":     "depends on storage method",
"FLAG":          "brittle; the geoengineering straw man for a reason",
},
}

# —————————————————————

# REMAINING UNRESOLVED COATING IN THE MERGED FRAMEWORK

# —————————————————————

COATING_FLAGS = [
"compression factors (40-60%, 5-7yr) are estimated, not derived from spike physics",
"'emergency brake' framing is interpretation, not equation",
"'Phase 2 must come from rock weathering' collapses option space prematurely",
"no uncertainty propagation through the GtC totals",
"no boundary condition: what if warming crosses kelp/permafrost thresholds during Phase 1?",
"no political/economic constraint on what 'restoration' actually means in occupied land",
]
