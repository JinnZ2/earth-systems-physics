“””
ADAPTIVE LAYER - EARTHWORM + MYCORRHIZAL INFRASTRUCTURE
The load-bearing foundation under wetland, kelp, and permafrost sinks.

Verb-first physics:
earthworms ingest soil and organic matter
ingestion forms casts
casts stabilize into water-stable macroaggregates
aggregates physically protect particulate organic carbon
burrows create macropores
macropores infiltrate flood water and retain capillary water
mycorrhizal hyphae enmesh aggregates
glomalin coats aggregates and resists water erosion
hyphae extend plant access to water during drought
“””

# —————————————————————

# DOUBLING TIME by soil condition (peer-reviewed range)

# —————————————————————

DOUBLING_TIMES = {
“optimal”:     {“weeks”: (8, 14),   “SOM_pct”: (8, 15),  “pH”: (6.5, 7.5)},
“sub_optimal”: {“weeks”: (22, 40),  “SOM_pct”: (3, 5),   “pH”: (5.5, 6.5)},
“degraded”:    {“weeks”: (52, None),“SOM_pct”: (0, 2),   “pH”: (None, 5.0),
“FLAG”: “population declines without pre-treatment”},
“waterlogged”: {“weeks”: (18, 30),  “SOM_pct”: “variable”,“pH”: “variable”,
“note”: “native semi-aquatic species only”},
}

# —————————————————————

# MIN VIABLE BIOMASS per flood-drought intensity

# —————————————————————

BIOMASS_THRESHOLDS = {
“moderate”:          {“tonnes_ha”: 3,  “ind_per_m2”: 300,
“scenario”: “50mm rain, 3wk dry”},
“severe”:            {“tonnes_ha”: 7,  “ind_per_m2”: 700,
“scenario”: “100mm rain, 2mo drought”,
“note”: “minimum for carbon-loss-free volatility”},
“extreme_volatility”:{“tonnes_ha”: 12, “ind_per_m2”: 1200,
“scenario”: “rain-on-snow, flash flood, 6mo dry”,
“guild_required”: [“anecic”, “endogeic”, “epigeic”]},
}

# —————————————————————

# REGIONAL SPECIES FILTER - what DeepSeek skipped

# —————————————————————

REGIONAL_SPECIES_FILTER = {
“glaciated_north_america”: {
“native_status”: “no native earthworms since last glaciation (~12k yr)”,
“permitted_species”: [
“Sparganophilus eatoni (semi-aquatic, native)”,
“Bimastos parvus (native, limited range)”,
],
“PROHIBITED”: [
“Lumbricus terrestris”, “Lumbricus rubellus”, “Aporrectodea caliginosa”,
“Octolasion cyaneum”, “Eisenia fetida (in forest soils)”,
],
“REASON”: (
“European Lumbricus species in Great Lakes hardwood forests strip the duff “
“layer, eliminate spring ephemerals, mobilize previously stable C, and “
“accelerate net C LOSS. Inoculation in these forests would reverse the goal.”
),
“FLAG”: “this region requires mycorrhizal-only restoration in forest soils”,
},
“non_glaciated_temperate”: {
“permitted_species”: “regional native guild (varies by continent)”,
“note”: “most agricultural soils have lost native worms, can re-establish”,
},
“tropical”: {
“permitted_species”: “Pontoscolex, Glossoscolex, Amynthas (regionally native only)”,
“FLAG”: “Asian Amynthas species highly invasive outside native range”,
},
“wetland_aquatic”: {
“permitted_species”: “Sparganophilus spp. (NA), Glyphidrilus spp. (SE Asia), regional natives only”,
},
}

# —————————————————————

# MYCORRHIZAL INOCULATION - independent protocol

# —————————————————————

MYCORRHIZAL_PROTOCOLS = {
“AMF”: {
“applies_to”: “grasslands, most crops, wetland herbaceous plants”,
“host_plants”: “~80% of vascular plants”,
“inoculation”: “spore slurry from native prairie/grassland or commercial native-strain product”,
“establishment_time”: “8-16 weeks to functional network”,
“FLAG”: “commercial inoculants frequently contaminated with non-native strains”,
},
“ectomycorrhizal”: {
“applies_to”: “boreal and temperate forests (pine, spruce, oak, beech, birch)”,
“host_plants”: “~10% of vascular plants but dominant in cold-climate forests”,
“inoculation”: “soil transfer from healthy adjacent forest, or live seedling planting”,
“establishment_time”: “1-3 years to functional network”,
“note”: “this is the protocol for glaciated NA forests where earthworm inoculation is prohibited”,
},
“ericoid”: {
“applies_to”: “heath, bog, peat systems (cranberry, blueberry, leatherleaf, sphagnum)”,
“host_plants”: “ericaceous plants, critical in northern peatlands”,
“inoculation”: “established in peat substrate, rarely needs supplementation if peat intact”,
“FLAG”: “these systems are the hardest to restore once peat is gone”,
},
}

# —————————————————————

# PRE-TREATMENT CARBON ACCOUNTING - what DeepSeek skipped

# —————————————————————

PRETREATMENT_CARBON_COST = {
“lime_application”: {
“rate_tonnes_ha”:      {“value”: 2.5, “range”: (1, 5)},
“CO2_released_per_t”:  {“value”: 0.44, “note”: “lime kiln + carbonate decomposition”},
“CO2_cost_ha”:         {“value”: 1.1, “range”: (0.4, 2.2), “unit”: “t CO2 / ha”},
},
“biochar_application”: {
“rate_tonnes_ha”:      {“value”: 5, “range”: (2, 10)},
“CO2_balance”:         “NET NEGATIVE if pyrolysis uses waste biomass and waste heat”,
“CO2_cost_ha”:         {“value”: -2.0, “range”: (-5, +1),
“FLAG”: “depends entirely on feedstock and energy source”},
},
“compost_application”: {
“rate_tonnes_ha”:      {“value”: 3, “range”: (1, 8)},
“CO2_cost_ha”:         {“value”: 0.2, “range”: (0, 0.5),
“note”: “transport + handling, mostly C neutral if local”},
},
}

def adaptive_layer_net_carbon(area_ha, years_operated):
“””
Net carbon over operational lifetime, accounting for pre-treatment cost.
“””
pretreat_cost_ha = (PRETREATMENT_CARBON_COST[“lime_application”][“CO2_cost_ha”][“value”] +
PRETREATMENT_CARBON_COST[“biochar_application”][“CO2_cost_ha”][“value”] +
PRETREATMENT_CARBON_COST[“compost_application”][“CO2_cost_ha”][“value”])

```
pretreat_total_t = pretreat_cost_ha * area_ha   # t CO2

# post-establishment annual sequestration
annual_seq_t_ha = 1.5   # t C / ha / yr, mid-range for stabilized aggregate + glomalin
annual_seq_CO2_t = annual_seq_t_ha * (44/12) * area_ha

return {
    "pretreatment_one_time_t_CO2": pretreat_total_t,
    "annual_drawdown_t_CO2":       annual_seq_CO2_t,
    "cumulative_after_yr":         years_operated * annual_seq_CO2_t - pretreat_total_t,
    "payback_period_yr":           pretreat_total_t / annual_seq_CO2_t if annual_seq_CO2_t > 0 else None,
}
```

# —————————————————————

# SCALING - bottleneck-aware

# —————————————————————

SCALING_BOTTLENECKS = {
“biology”:             “earthworm doubling at optimal conditions = 8-14 weeks. NOT the bottleneck.”,
“vermicomposting_distribution”:  “100x multiplication per 2yr is target; assumes no bottleneck on substrate or labor”,
“pretreatment_logistics”:        “lime, biochar feedstock, compost transport. THE primary bottleneck.”,
“trained_verification_personnel”:“ring infiltrometer use, soil pit assessment, aggregate stability test”,
“land_access”:                   “compliance mandate requires legal-political infrastructure”,
“social_political_acceptance”:   “stewardship-as-condition-of-ownership requires policy change”,
“regional_species_sourcing”:     “native earthworm starter cultures are scarce; vermicomposting must use natives”,
}

DEEPSEEK_PROJECTION_HONEST = {
“claimed”:   “50M ha/yr deployment by year 10 via 1M nodes”,
“ceiling”:   “this is geometric growth assuming no bottlenecks”,
“realistic”: “any of the bottlenecks above can throttle by factor 2-10x”,
“framework_position”: “hold target as goal; report actual rate empirically each year”,
}

# —————————————————————

# COUPLING TO OTHER SINKS - the load-bearing foundation

# —————————————————————

COUPLING_TO_OTHER_SINKS = {
“wetland_methane_spike”: {
“mechanism”:         “earthworm porosity maintains aerobic rhizosphere during drawdowns”,
“claimed_lag_reduction”: {“value”: 0.30, “FLAG”: “ESTIMATED, no peer-reviewed source”,
“honest_range”: (0.15, 0.45)},
},
“permafrost_thermokarst”: {
“mechanism”:         “burrow network on upland margins drains excess meltwater, prevents waterlogging trigger”,
“applies_to”:        “permafrost MARGINS only, not active permafrost zone (worms cannot survive in frozen soil)”,
“FLAG”:              “this is a buffer for the buffer, not a primary mechanism”,
},
“kelp_coastal_forest_drought_resistance”: {
“mechanism”:         “mycorrhizal-connected coastal forest stabilized by earthworm aggregates resists drought during marine heatwaves”,
“claimed_outcome”:   “reduces simultaneous coastal C release during MHW events”,
“FLAG”:              “physically plausible, no direct empirical study cited”,
},
}

# —————————————————————

# COMPLIANCE MANDATE - honestly framed

# —————————————————————

COMPLIANCE_FRAMEWORK = {
“year_1_3_pretreatment”: {
“requirement”: “1 t/ha/yr biochar-compost-lime slurry until pH > 5.5 and SOM > 2%”,
“verification”: “annual soil test, locally administered”,
},
“year_3_plus_inoculation”: {
“requirement”: “regionally native earthworm guild at >= 200 ind/m2”,
“verification”: “soil pit count by trained verifier”,
},
“year_5_plus_function”: {
“requirement”: “>30% water-stable macroaggregates in top 20cm AND infiltration >50mm/hr”,
“verification”: “ring infiltrometer + wet sieving”,
},
“verification_robustness”: {
“claim”:  “harder to game than carbon credit accounting”,
“limits”: [
“verifiers can be bought (governance challenge, not technical)”,
“samples can be collected from optimal locations only”,
“measurements can be timed for favorable conditions”,
],
“honest_framing”: “robust and low-tech, not uncheatable”,
},
}
