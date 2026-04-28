"""
REDUNDANCY STACKING + RANGE SHIFT OPTION SPACE
Buffer species don't have to be single points of failure if guilds are stacked.
Range shifts under warming are not a single binary choice.

Verb-first physics:
multiple species suppress urchins -> suppression persists if any species holds
multiple herbivores compact snow -> cooling persists if any species density holds
multiple engineers regulate hydrology -> wetland persists if any engineer functions
warming shifts ranges poleward -> some species track on their own, some need assist
naive ecosystems may show novel interactions when colonizers arrive
"""

# —————————————————————

# REDUNDANCY GUILDS

# —————————————————————

URCHIN_SUPPRESSORS = {
"sea_otter": {
"lat_range": (25, 60), "thermal_max_C": 22,
"predation_rate": "high", "depth_range_m": (0, 30),
"status": "recovering in N Pacific, extirpated in N Atlantic",
},
"sunflower_sea_star": {
"lat_range": (30, 60), "thermal_max_C": 18,
"predation_rate": "high", "depth_range_m": (0, 435),
"status": "captive breeding active post-2013 wasting disease collapse",
"FLAG": "deeper/colder than otter, complementary not duplicate",
},
"california_sheephead": {
"lat_range": (24, 38), "thermal_max_C": 24,
"predation_rate": "moderate", "depth_range_m": (1, 50),
"status": "fishery-impacted, recovering with MPAs",
},
"atlantic_wolffish": {
"lat_range": (40, 75), "thermal_max_C": 11,
"predation_rate": "moderate", "depth_range_m": (0, 600),
"status": "depleted by bycatch, requires fishery reform",
},
}

SNOW_COMPACTORS = {
"reindeer_caribou":   {"lat_range": (55, 80), "ROS_vulnerability": "high",
"FLAG": "Yamal 2013 mass mortality from rain-on-snow event"},
"musk_ox":            {"lat_range": (65, 83), "ROS_vulnerability": "moderate",
"note": "can break ice crust, tolerates harder conditions"},
"yakutian_horse":     {"lat_range": (55, 75), "ROS_vulnerability": "moderate",
"note": "paws snow effectively, broad forage"},
"wood_bison":         {"lat_range": (55, 70), "ROS_vulnerability": "low-moderate",
"note": "high body mass effective snow compaction"},
"saiga_antelope":     {"lat_range": (45, 55), "ROS_vulnerability": "low",
"FLAG": "vulnerable to disease outbreaks (2015 mass die-off)"},
}

HYDROLOGICAL_ENGINEERS = {
"north_american_beaver": {"lat_range": (30, 70), "thermal_max_C": 25,
"ecosystem_native": ["NA"]},
"european_beaver":       {"lat_range": (40, 70), "thermal_max_C": 25,
"ecosystem_native": ["Eurasia"]},
"capybara":              {"lat_range": (-35, 10), "thermal_max_C": 35,
"ecosystem_native": ["S America"]},
"hippopotamus":          {"lat_range": (-30, 15), "thermal_max_C": 40,
"ecosystem_native": ["Africa"]},
"european_bison":        {"lat_range": (45, 65), "thermal_max_C": 28,
"ecosystem_native": ["Europe"], "role": "riparian grazer not engineer"},
}

# —————————————————————

# RANGE SHIFT OPTION SPACE - DO NOT COLLAPSE TO BINARY

# —————————————————————

RANGE_SHIFT_OPTIONS = {
"passive_natural_tracking": {
"description":  "remove barriers (dams, fences, roads) and let species track climate on their own",
"applies_when": "receiving habitat is contiguous with current range",
"intervention_intensity": "low",
"ecological_risk": "low - this is what species do under climate change anyway",
"example":      "removing fish-passage barriers as warmwater species shift north",
"constraint":   "requires removing physical barriers, often crosses jurisdictions",
},
"corridor_creation": {
"description":  "actively restore connectivity between current and projected future range",
"applies_when": "fragmented landscape blocks natural tracking",
"intervention_intensity": "moderate",
"ecological_risk": "low-moderate",
"example":      "riparian corridor restoration for beaver northward spread",
},
"assisted_migration_intra_provincial": {
"description":  "move species to suitable habitat within same biogeographic province",
"applies_when": "natural tracking too slow vs warming rate, but receiving ecosystem co-evolved with species genus",
"intervention_intensity": "moderate",
"ecological_risk": "moderate - genetic mixing, local adaptation loss",
"example":      "moving Wisconsin beaver populations to northern Manitoba",
},
"assisted_migration_inter_provincial": {
"description":  "move species across biogeographic boundaries to naive ecosystems",
"applies_when": "no functional analog exists in receiving system AND function is critical",
"intervention_intensity": "high",
"ecological_risk": "high - novel interactions, invasion potential",
"example":      "introducing North American beaver to Patagonia (already happened, mixed outcome)",
"FLAG":         "this is the controversial case; framework holds it as available, not recommended",
},
"functional_analog_substitution": {
"description":  "use locally-native species that perform analogous function",
"applies_when": "native analog exists with similar ecological role",
"intervention_intensity": "low-moderate",
"ecological_risk": "low",
"example":      "European bison as riparian grazer instead of beaver in cold Eurasian rivers",
},
"managed_retreat": {
"description":  "accept loss of sink in unsupportable region, redirect effort to viable regions",
"applies_when": "buffer species cannot be supported AND no analog exists AND function not critical",
"intervention_intensity": "minimal",
"ecological_risk": "minimal",
"example":      "accept loss of southern beaver-engineered wetlands in lower Mississippi as warming progresses",
"trade_off":    "loss of regional sink; may be acceptable if total network maintains drawdown",
},
"rest_let_system_decide": {
"description":  "step back and observe; ecosystems show emergent reorganization that prediction misses",
"applies_when": "uncertainty too high for any active intervention",
"intervention_intensity": "zero",
"ecological_risk": "depends on what emerges",
"FLAG":         "this is the option DeepSeek skipped",
},
}

# —————————————————————

# DECISION CRITERIA - what constraints select from the option space

# —————————————————————

DECISION_CRITERIA = {
"ecosystem_naivety":       "is receiving system co-evolved with this species or its close relatives?",
"warming_rate_vs_dispersal":"is climate moving faster than the species can track naturally?",
"function_redundancy":     "is there a functional analog already present in receiving system?",
"reversibility":           "can intervention be undone if it goes wrong?",
"scale_of_intervention":   "individual organisms, breeding populations, or whole guild?",
"stakeholder_consent":     "do the people living with the receiving ecosystem consent?",
"unknown_unknowns":        "what emergent interactions cannot be predicted from current knowledge?",
}

# —————————————————————

# CASCADING FAILURE - the scenario DeepSeek mapped, formalized

# —————————————————————

CASCADE_RISK = {
"trigger_events": [
"sequential rain-on-snow winters (Arctic herbivore mortality)",
"marine heatwave (kelp + otter stress)",
"El Nino drought (peat fire ignition)",
"novel pathogen (sea star wasting, saiga die-off type events)",
],
"first_order_failures": {
"permafrost":  "herbivore density collapse -> snow insulation returns -> thaw acceleration",
"kelp":        "otter retreat or mortality -> urchin explosion -> kelp barrens",
"wetland":     "drought + peat oxidation -> fire ignition -> sink reversal to source",
},
"cascade_couplings": {
"atmospheric":  "same circulation patterns can stress all three sinks simultaneously",
"hydrological": "wetland drying reduces marine nutrient delivery, cascading to kelp",
"albedo":       "Arctic snow loss accelerates warming, cascading to lower-latitude sinks",
},
"redundancy_response": {
"multi_species_guilds":     "deploy stacked species across full functional guild",
"geographic_dispersion":    "no single climate event affects all nodes",
"stewardship_distributed":  "local sensors detect early; central monitoring cannot",
"phase_0_calibration_role": "100 nodes diversifies risk during the learning phase",
},
}
