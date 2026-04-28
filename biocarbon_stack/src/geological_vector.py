“””
GEOLOGICAL VECTOR - ENHANCED ROCK WEATHERING
Acceleration of the silicate weathering thermostat that has regulated
Earth’s CO2 over geological time.

Verb-first physics:
silicate rock dissolves in acidic water
dissolution converts CO2 to bicarbonate
bicarbonate flows through groundwater to rivers to ocean
ocean alkalinity locks carbon for ~100,000 years
reactive surface area determines reaction rate
finer grinding increases surface area
acidic moist soil accelerates dissolution
“””

# —————————————————————

# CORE PARAMETERS - peer-reviewed ranges

# —————————————————————

ERW_PARAMS = {
“application_rate_t_per_ha_yr”: {
“value”: 30, “range”: (20, 40),
“source”: “Beerling et al 2020, Nature 583”,
},
“weathering_acceleration_acidic_moist”: {
“value”: 3.0, “range”: (2.0, 4.0),
“note”: “vs dryland temperate agriculture baseline”,
“FLAG”: “field validation limited to small-plot studies; large-scale unverified”,
},
“CO2_removed_per_tonne_basalt”: {
“value”: 0.27, “range”: (0.20, 0.30),
“note”: “stoichiometric, accounting for secondary carbonate precipitation”,
},
“deployable_area_ha”: {
“value”: 1.5e9, “range”: (0.8e9, 2.5e9),
“FLAG”: “depends on stewardship-managed land base which depends on legal regime”,
},
}

# —————————————————————

# DEPLOYMENT MODELS - hold option space, do not collapse

# —————————————————————

DEPLOYMENT_OPTIONS = {
“decentralized_steward_integrated”: {
“description”: “village-scale hammer mills, local rock sourcing, application as soil amendment”,
“energy_source”: “local renewable (solar, micro-hydro, wind)”,
“EROI”: “moderate, scales with renewable buildout”,
“failure_mode”: “rock availability varies by region; some areas lack basalt”,
“compliance_logic”: “co-benefit fertility increases food yield; voluntary compliance via direct benefit”,
“scale_limit_t_per_yr”: “~5 Mt per node, cumulative scaling limited by node count”,
},
“centralized_industrial”: {
“description”: “large quarries, industrial grinding, diesel transport, agricultural broadcast”,
“energy_source”: “depends on grid carbon intensity”,
“EROI”: “negative if diesel-heavy; positive if electric/rail”,
“failure_mode”: “supply chain emissions can exceed sequestration”,
“compliance_logic”: “regulatory mandate or carbon credit market”,
“FLAG”: “this is what most published ERW proposals assume; EROI depends entirely on energy source”,
},
“hybrid_regional”: {
“description”: “regional grinding facilities serving multiple stewardship guilds”,
“energy_source”: “mixed”,
“EROI”: “variable”,
“failure_mode”: “intermediate logistics complexity”,
},
}

# —————————————————————

# TARRA PRETA AND AFRICAN DARK EARTHS - empirical precedent

# —————————————————————

INDIGENOUS_PRECEDENT = {
“Amazonian_Terra_Preta”: {
“method”: “biochar + bone + pottery shards + crushed rock added to soil over centuries”,
“outcome”: “highly fertile, deeply carbon-stable soil persisting >2000 years”,
“scale_existing”: “estimated 10-25% of Amazon basin in pre-conquest era”,
“stability”: “carbon stocks 1-3x surrounding ferralsols, persistent over millennia”,
},
“African_Dark_Earths”: {
“method”: “kitchen waste, charcoal, ash, mineral fines added to soil through household practice”,
“outcome”: “sustained agricultural productivity in nutrient-poor tropical soils”,
“scale_existing”: “documented across West Africa, Central Africa, Sahel margins”,
},
“framework_implication”: (
“ERW with rock dust amendment is not novel technology. “
“Distributed indigenous practice already validated this approach over millennia. “
“Modern ERW proposals are reinventing what stewardship cultures already know.”
),
}

def erw_drawdown(area_ha, rate_t_ha_yr, acceleration_factor, co2_per_t_basalt):
“”“Annual CO2 drawdown from ERW deployment.”””
basalt_total_t_yr = area_ha * rate_t_ha_yr
co2_removed_t_yr = basalt_total_t_yr * co2_per_t_basalt * acceleration_factor / 1.0
# acceleration_factor relative to standard rate is already absorbed into co2_per_t in some studies;
# here treated separately for explicit modeling
return {
“basalt_applied_t_yr”:       basalt_total_t_yr,
“co2_removed_t_yr”:          co2_removed_t_yr,
“co2_removed_Gt_yr”:         co2_removed_t_yr / 1e9,
“C_removed_Gt_yr”:           co2_removed_t_yr * (12/44) / 1e9,
}

def near_term_realistic(years_to_year_10=10):
“””
Bottleneck-aware estimate for year-10 deployment.
Limited by grinding capacity, distribution logistics, and stewardship adoption rate.
“””
# assume 10% of full deployable area achieves ERW deployment by year 10
realistic_area_ha = ERW_PARAMS[“deployable_area_ha”][“value”] * 0.10
return erw_drawdown(
area_ha=realistic_area_ha,
rate_t_ha_yr=ERW_PARAMS[“application_rate_t_per_ha_yr”][“value”],
acceleration_factor=ERW_PARAMS[“weathering_acceleration_acidic_moist”][“value”],
co2_per_t_basalt=ERW_PARAMS[“CO2_removed_per_tonne_basalt”][“value”] / 3.0,  # base rate, acceleration applied separately
)

# —————————————————————

# COUPLING TO BIOLOGICAL STACK

# —————————————————————

COUPLING_TO_BIO_STACK = {
“soil_pH_buffering”: (
“basalt dust raises pH of acidic soils, supporting earthworm survival “
“and reducing pre-treatment lime requirement; net carbon cost of “
“pre-treatment decreases when ERW is part of the amendment”
),
“mineral_nutrient_supply”: (
“basalt provides P, K, Ca, Mg, Si, Fe, micronutrients; “
“increases plant productivity which feeds mycorrhizal and earthworm pools”
),
“wetland_alkalinity_export”: (
“weathering products from stewardship-managed wetlands export bicarbonate “
“to coastal zones, partially buffering ocean acidification “
“and supporting kelp shellfish co-benefit zone”
),
“FLAG”: (
“these couplings are physically plausible but have not been measured “
“at coupled-system scale. Phase 0 calibration nodes should instrument “
“for ERW + biological coupling specifically.”
),
}

# —————————————————————

# WHAT ERW DOES NOT DO

# —————————————————————

ERW_LIMITS = [
“does not reduce methane (only addresses CO2)”,
“weathering rate is rate-limited by water availability and contact time”,
“ocean alkalinity flux is delayed by groundwater transit time (years to decades)”,
“potential heavy metal leaching from some basalt sources requires source screening”,
“100,000 year permanence claim depends on stable ocean chemistry; uncertain under warming”,
]
