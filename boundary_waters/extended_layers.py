“””
Extended layer engines: lumber, fish, climate, air, wildfire, port.
Each reads physical cascade state + year index.
Pure functions. Deterministic given inputs.
“””

from math import exp, log
from extended_constants import *

# ═════════════════════════════════════════════════════════════

# X0 — CLIMATE AMPLIFICATION (feeds back into chemistry)

# ═════════════════════════════════════════════════════════════

def climate_amplifier(year):
“””
Arrhenius acceleration of AMD. Q10 ≈ 2.1 for pyrite oxidation.
Also: permafrost thaw degrades tailings dam frozen cores.
Simulation year 0 = 2026.
“””
# Linear temperature trajectory to 2100 (year 74)
t_progress = min(1.0, year / 74.0)
delta_T = PROJECTED_TEMP_RISE_2100_C * t_progress

```
# Arrhenius Q10 factor
oxidation_mult = AMD_Q10_FACTOR ** (delta_T / 10.0)

# Precipitation change
precip_mult = 1 + PRECIP_INCREASE_FRAC_2100 * t_progress

# Extreme event frequency
extreme_event_mult = 1 + (EXTREME_EVENT_FREQ_MULT_2100 - 1) * t_progress

# Tailings dam risk from permafrost degradation
frozen_core_loss_m = PERMAFROST_THAW_RATE_CM_YR / 100 * year
frozen_core_remaining = max(0, TAILINGS_DAM_FROZEN_CORE_M - frozen_core_loss_m)
dam_risk_mult = 1 + (DAM_FAILURE_MULT_FROM_THAW - 1) * \
                (1 - frozen_core_remaining / TAILINGS_DAM_FROZEN_CORE_M)

# Fire season extension
fire_season_extension = (FIRE_SEASON_DAYS_2100 - FIRE_SEASON_DAYS_BASELINE) * t_progress

return {
    "delta_T_C":              delta_T,
    "oxidation_mult":         oxidation_mult,
    "precip_mult":            precip_mult,
    "extreme_event_mult":     extreme_event_mult,
    "dam_risk_mult":          dam_risk_mult,
    "fire_season_days":       FIRE_SEASON_DAYS_BASELINE + fire_season_extension,
    "drought_mult":           1 + (DROUGHT_FREQ_MULT_2100 - 1) * t_progress,
    "flood_mult":             1 + (FLOOD_FREQ_MULT_2100 - 1) * t_progress,
}
```

# ═════════════════════════════════════════════════════════════

# X1 — LUMBER / FOREST DEGRADATION

# ═════════════════════════════════════════════════════════════

def lumber_layer(phys, climate, mine_active, year_since_start):
“””
Three damage pathways:
1. Acid deposition (SO2 dry/wet + direct sulfate plume)
→ growth loss + needle retention loss + mycorrhizal collapse
2. Soil Ca depletion on Shield granite → base cation shortage
3. Hg uptake in pulp → premium grade rejection
Species-weighted vulnerability.
“””
# Composite acid exposure proxy
acid_load = phys[“sulfate_mg_l”] / 50.0  # normalized
acid_load = min(1.0, acid_load)

```
# Weighted species vulnerability
weighted_vuln = (
    SPRUCE_FIR_FRAC * SPRUCE_ACID_VULNERABILITY +
    ASPEN_BIRCH_FRAC * ASPEN_ACID_VULNERABILITY +
    PINE_FRAC * PINE_ACID_VULNERABILITY +
    CEDAR_TAMARACK_FRAC * CEDAR_ACID_VULNERABILITY
)

# Growth loss compounds with cumulative exposure
annual_growth_loss = ACID_DEPOSITION_GROWTH_LOSS * acid_load * weighted_vuln
cumulative_growth_loss_frac = 1 - exp(-annual_growth_loss * year_since_start)

# Soil Ca depletion (slower, irreversible on human timescale)
ca_depletion_frac = 1 - exp(-year_since_start / SOIL_CA_DEPLETION_HALF_LIFE_YR) \
                    if acid_load > 0.1 else 0

# Mycorrhizal collapse threshold
mycorrhizal_dead = acid_load > 0.35  # proxy for pH < 4.3
if mycorrhizal_dead:
    cumulative_growth_loss_frac = min(1.0, cumulative_growth_loss_frac * 1.8)

# Merchantable volume loss
volume_lost_m3 = STANDING_TIMBER_VOLUME_M3 * cumulative_growth_loss_frac
sawtimber_lost = volume_lost_m3 * (1 - PULP_VOLUME_FRAC)
pulpwood_lost = volume_lost_m3 * PULP_VOLUME_FRAC

# Pulp grade contamination (Hg in wood fiber)
hg_in_wood_ppm = phys["methyl_hg_ng_l"] * 1e-3 * 4.2  # rough uptake factor
pulp_grade_rejected = hg_in_wood_ppm > HG_PULP_REJECTION_THRESHOLD
pulp_premium_loss = PULP_GRADE_LOSS_FRAC if pulp_grade_rejected else 0

# Economic loss
direct_timber_loss_usd = (sawtimber_lost * SAWTIMBER_VALUE_USD_M3 +
                          pulpwood_lost * PULPWOOD_VALUE_USD_M3)
pulp_grade_loss_usd = (STANDING_TIMBER_VOLUME_M3 * PULP_VOLUME_FRAC *
                       pulp_premium_loss * PULPWOOD_VALUE_USD_M3 * 0.4)

# Jobs at risk
lumber_jobs_lost = int((SAWMILL_JOBS_CORRIDOR + LOGGING_JOBS_CORRIDOR) *
                       cumulative_growth_loss_frac)

return {
    "acid_load":                acid_load,
    "growth_loss_frac":         cumulative_growth_loss_frac,
    "ca_depletion_frac":        ca_depletion_frac,
    "mycorrhizal_dead":         mycorrhizal_dead,
    "timber_volume_lost_m3":    volume_lost_m3,
    "pulp_grade_rejected":      pulp_grade_rejected,
    "direct_timber_loss_usd":   direct_timber_loss_usd,
    "pulp_grade_loss_usd":      pulp_grade_loss_usd,
    "total_lumber_loss_usd":    direct_timber_loss_usd + pulp_grade_loss_usd,
    "lumber_jobs_lost":         lumber_jobs_lost,
}
```

# ═════════════════════════════════════════════════════════════

# X2 — FISH CONSUMPTION (Ojibwe amplifier)

# ═════════════════════════════════════════════════════════════

def fish_consumption_layer(phys, year_since_start):
“””
GLIFWC-documented subsistence consumption 5-10× state avg.
Tissue Hg concentrates via BAF; walleye and pike top accumulators.
Pregnancy exposure → IQ loss in offspring (irreversible).
“””
water_hg_ng_l = phys[“methyl_hg_ng_l”]

```
# Zero exposure -> zero downstream effect
if water_hg_ng_l <= 0:
    return {
        "fish_tissue_hg_mg_kg": 0, "state_avg_rfd_ratio": 0,
        "ojibwe_mean_rfd_ratio": 0, "ojibwe_high_rfd_ratio": 0,
        "iq_loss_per_child": 0, "cumulative_impaired_children": 0,
        "fish_advisory_triggered": False,
        "harvest_displacement_cost_usd": 0,
        "treaty_rights_violation": False,
    }

# Weighted BAF across species consumed
weighted_baf = (
    WALLEYE_CONSUMPTION_FRAC * WALLEYE_BAF +
    PIKE_CONSUMPTION_FRAC * PIKE_BAF +
    LAKE_TROUT_CONSUMPTION_FRAC * LAKE_TROUT_BAF +
    WHITEFISH_CONSUMPTION_FRAC * WHITEFISH_BAF +
    OTHER_FISH_CONSUMPTION_FRAC * LAKE_TROUT_BAF * 0.5
)

# Tissue Hg (mg/kg wet):
# water_hg_ng_l = ng Hg / L water
# BAF dimensionless = (mg/kg fish) / (mg/L water) = (ng/g fish) / (ng/mL water)
# 1 ng/L water = 1e-6 mg/L water
# tissue_mg_kg = water_mg_L × BAF  (both in matching conc units)
water_hg_mg_l = water_hg_ng_l * 1e-6
fish_tissue_hg_mg_kg = water_hg_mg_l * weighted_baf

# Daily intake for each consumer tier (µg/day)
# tissue mg/kg × grams/day × (1g/1000g) × (1000 µg/mg) = µg/day
intake_state_avg  = fish_tissue_hg_mg_kg * STATE_AVG_FISH_CONSUMPTION_G_DAY / 1000 * 1000
intake_ojibwe_mean = fish_tissue_hg_mg_kg * OJIBWE_SUBSISTENCE_G_DAY / 1000 * 1000
intake_ojibwe_high = fish_tissue_hg_mg_kg * OJIBWE_HIGH_CONSUMER_G_DAY / 1000 * 1000

# Simplify: intake µg/day = tissue mg/kg × g/day
intake_state_avg   = fish_tissue_hg_mg_kg * STATE_AVG_FISH_CONSUMPTION_G_DAY
intake_ojibwe_mean = fish_tissue_hg_mg_kg * OJIBWE_SUBSISTENCE_G_DAY
intake_ojibwe_high = fish_tissue_hg_mg_kg * OJIBWE_HIGH_CONSUMER_G_DAY

# RfD exceedance
state_rfd_ratio   = (intake_state_avg / MEAN_ADULT_BW_KG) / EPA_MEHG_RFD_UG_KG_DAY
ojibwe_mean_rfd   = (intake_ojibwe_mean / MEAN_ADULT_BW_KG) / EPA_MEHG_RFD_UG_KG_DAY
ojibwe_high_rfd   = (intake_ojibwe_high / MEAN_ADULT_BW_KG) / EPA_MEHG_RFD_UG_KG_DAY

# Hair Hg µg/g ≈ blood Hg µg/L ÷ 250; blood Hg ≈ daily intake × 1.6
ojibwe_blood_hg_ug_l = intake_ojibwe_high * 1.6
ojibwe_hair_hg = ojibwe_blood_hg_ug_l / 250
iq_loss_per_child = MEHG_IQ_LOSS_POINTS_PER_UG_G_HAIR * ojibwe_hair_hg

# Annual affected pregnancies
annual_pregnancies = OJIBWE_ENROLLMENT_TOTAL * OJIBWE_PREGNANCY_RATE_ANNUAL
high_consumer_pregnancies = annual_pregnancies * OJIBWE_HIGH_CONSUMER_FRAC

# Only count exposed pregnancies (iq loss > 0.1 pt)
if iq_loss_per_child > 0.1:
    exposed_years = min(year_since_start, 40)
    cumulative_impaired = int(high_consumer_pregnancies * exposed_years)
else:
    cumulative_impaired = 0

# Advisory trigger (MN "do not eat")
advisory_triggered = fish_tissue_hg_mg_kg > 0.3
harvest_cost = (OJIBWE_ENROLLMENT_TOTAL * HARVEST_REPLACEMENT_COST_USD_PER_CAP
                if advisory_triggered else 0)

return {
    "fish_tissue_hg_mg_kg":       fish_tissue_hg_mg_kg,
    "state_avg_rfd_ratio":        state_rfd_ratio,
    "ojibwe_mean_rfd_ratio":      ojibwe_mean_rfd,
    "ojibwe_high_rfd_ratio":      ojibwe_high_rfd,
    "iq_loss_per_child":          iq_loss_per_child,
    "cumulative_impaired_children": cumulative_impaired,
    "fish_advisory_triggered":    advisory_triggered,
    "harvest_displacement_cost_usd": harvest_cost,
    "treaty_rights_violation":    advisory_triggered,
}
```

# ═════════════════════════════════════════════════════════════

# X3 — AIR QUALITY

# ═════════════════════════════════════════════════════════════

def air_quality_layer(phys, mine_active, climate):
“””
SO2, PM, NOx, Hg(g) emissions. Health impacts via BenMAP
equivalents. Visibility impairment in Class I wilderness.
Downwind crop yield loss via ozone precursor chemistry.
“””
if not mine_active:
# Post-closure: fugitive tailings dust only
so2_tonnes = 0
pm25_tonnes = PM25_EMISSION_TONNES_YR * 0.25 if phys[“cumulative_waste_Mt”] > 0 else 0
pm10_tonnes = PM10_EMISSION_TONNES_YR * 0.25 if phys[“cumulative_waste_Mt”] > 0 else 0
nox_tonnes = 0
hg_air_kg = HG_AIR_EMISSION_KG_YR * 0.15 if phys[“cumulative_waste_Mt”] > 0 else 0
else:
# Dust emissions amplified by drought
dust_mult = climate[“drought_mult”]
so2_tonnes = SO2_EMISSION_TONNES_YR
pm25_tonnes = PM25_EMISSION_TONNES_YR * dust_mult
pm10_tonnes = PM10_EMISSION_TONNES_YR * dust_mult
nox_tonnes = NOX_EMISSION_TONNES_YR
hg_air_kg = HG_AIR_EMISSION_KG_YR

```
# Health events
kids_in_exposure_zone = int(12_400 * 0.22)  # 22% of pop under 18
asthma_attacks = kids_in_exposure_zone * ASTHMA_ATTACKS_PER_TONNE_SO2 * so2_tonnes / 3400

# BenMAP uses µg/m3; rough conversion: 1 tonne/yr over 400 km2 ≈ 0.3 µg/m3
pm25_concentration = pm25_tonnes / 400 * 0.3
copd_hosp = 12_400 * COPD_HOSPITALIZATIONS_PM25 * pm25_concentration
cardio_deaths = 12_400 * CARDIOVASCULAR_DEATHS_PM25 * pm25_concentration

acute_resp = acute_resp = pm10_tonnes * ACUTE_RESP_PER_TONNE_PM10 / 620

# Health cost
health_cost = (asthma_attacks * ASTHMA_ATTACK_COST_USD +
               copd_hosp * COPD_HOSP_COST_USD +
               cardio_deaths * CARDIOVASCULAR_DEATH_VSL)

# Visibility impairment (BWCA Class I)
visibility_loss_km = so2_tonnes * VISIBILITY_LOSS_KM_PER_TONNE_SO2
current_visibility_km = BWCA_VISIBILITY_BASELINE_KM - visibility_loss_km
class_i_violation = current_visibility_km < CLASS_I_PROTECTION_THRESHOLD

# Crop yield (downwind Iron Range + Arrowhead agriculture limited)
ozone_ppb_increase = nox_tonnes * NOX_TO_OZONE_CONVERSION / 1000
soy_yield_loss = SOYBEAN_YIELD_LOSS_PER_PPB_O3 * ozone_ppb_increase

return {
    "so2_tonnes_yr":             so2_tonnes,
    "pm25_tonnes_yr":            pm25_tonnes,
    "pm10_tonnes_yr":            pm10_tonnes,
    "hg_atmospheric_kg_yr":      hg_air_kg,
    "asthma_attacks_yr":         asthma_attacks,
    "copd_hospitalizations_yr":  copd_hosp,
    "cardio_deaths_yr":          cardio_deaths,
    "air_quality_health_cost_usd": health_cost,
    "bwca_visibility_km":        current_visibility_km,
    "class_i_violation":         class_i_violation,
    "soy_yield_loss_frac":       soy_yield_loss,
}
```

# ═════════════════════════════════════════════════════════════

# X4 — WILDFIRE AMPLIFICATION

# ═════════════════════════════════════════════════════════════

def wildfire_layer(phys, lumber, climate, year):
“””
Climate lengthens fire season. Acid-stressed forest = elevated fuel.
Fires reaching tailings = pyrometallurgical release of Hg/Pb/As.
Firefighter exposure + suppression cost + structural loss.
“””
# Baseline probability modified by climate + forest stress
climate_mult = 1 + (climate[“fire_season_days”] - FIRE_SEASON_DAYS_BASELINE) /   
(FIRE_SEASON_DAYS_2100 - FIRE_SEASON_DAYS_BASELINE) *   
(FIRE_WEATHER_EXTREME_FREQ - 1)
forest_stress_mult = 1 + lumber[“growth_loss_frac”] * (STRESSED_FOREST_FIRE_MULT - 1)

```
annual_fire_prob = BASELINE_FIRE_PROBABILITY_YR * climate_mult * forest_stress_mult
expected_burn_acres = CORRIDOR_FOREST_ACRES * annual_fire_prob

# Probability fire reaches tailings area
tailings_overrun = expected_burn_acres * TAILINGS_OVERRUN_FRAC_PER_FIRE \
                   if phys["cumulative_waste_Mt"] > 0 else 0

# Metal re-release from burned contaminated biomass
hg_re_released_kg = phys["cumulative_waste_Mt"] * HG_PER_TONNE_FIRE_RELEASE_MULT \
                    if False else 0  # placeholder — real calc below

# Simpler: fraction of deposited/accumulated Hg re-volatilized
if tailings_overrun > 0 and phys["cumulative_waste_Mt"] > 0:
    # Cumulative Hg in biomass + tailings surface
    hg_in_burn_zone_mg = phys["cumulative_waste_Mt"] * 1e6 * \
                         HG_PER_TONNE_FIRE_BASELINE_MG * \
                         (tailings_overrun / CORRIDOR_FOREST_ACRES)
    hg_re_released_kg = hg_in_burn_zone_mg * HG_RELEASE_FRAC_FROM_FIRE / 1e6
else:
    hg_re_released_kg = 0

# Firefighter exposure cases
firefighters_exposed = int(expected_burn_acres / 1000) * 15
firefighter_cancer_excess = firefighters_exposed * (FIREFIGHTER_CANCER_RR - 1) * 0.35

# Suppression + evacuation + structure loss
suppression_cost = expected_burn_acres * SUPPRESSION_COST_USD_ACRE
residents_evacuated = int(expected_burn_acres / 50_000 * 12_400)
evac_cost = residents_evacuated * EVAC_COST_USD_PER_RESIDENT

structures_lost = int(expected_burn_acres / 8_000)
structure_cost = structures_lost * STRUCTURE_LOSS_AVG_USD

# BWCA recreation closure
recreation_closure_events = max(0, int(expected_burn_acres / 25_000))
recreation_cost = recreation_closure_events * BWCA_RECREATION_CLOSURE_COST

total_fire_cost = (suppression_cost + evac_cost + structure_cost +
                   recreation_cost)

return {
    "annual_fire_prob_mult":      climate_mult * forest_stress_mult,
    "expected_burn_acres_yr":     expected_burn_acres,
    "tailings_overrun_acres":     tailings_overrun,
    "hg_re_released_kg_yr":       hg_re_released_kg,
    "firefighters_exposed":       firefighters_exposed,
    "firefighter_cancer_excess":  firefighter_cancer_excess,
    "residents_evacuated":        residents_evacuated,
    "structures_lost":            structures_lost,
    "suppression_cost_usd":       suppression_cost,
    "evacuation_cost_usd":        evac_cost,
    "structure_cost_usd":         structure_cost,
    "recreation_closure_cost":    recreation_cost,
    "total_fire_cost_usd":        total_fire_cost,
}
```

# Placeholder constants referenced above (add to extended_constants.py if needed)

HG_PER_TONNE_FIRE_BASELINE_MG = 0.08
HG_PER_TONNE_FIRE_RELEASE_MULT = 0.92

# ═════════════════════════════════════════════════════════════

# X5 — PORT CASCADE (Duluth-Superior)

# ═════════════════════════════════════════════════════════════

def port_layer_extended(phys, fish, air, mine_active, year):
“””
Three pathways hit the port:
1. St. Louis River contamination (already impaired, new Hg loading)
2. Canadian transit restrictions (bilateral under Boundary Waters Treaty)
3. Harbor sediment contamination → dredge disposal cost multiplier
Plus commercial fishing collapse on Lake Superior.
“””
# No mine impact -> no incremental port load
no_impact = (not mine_active
and phys[“methyl_hg_ng_l”] == 0
and phys[“canada_sulfate_mg_l”] == 0
and not fish[“fish_advisory_triggered”])
if no_impact:
return {
“hg_loading_increase”: 0, “intake_upgrade_required”: False,
“intake_upgrade_capex_usd”: 0, “annual_dredge_cost_usd”: 0,
“canadian_refusal_prob”: 0, “backhaul_loss_usd”: 0,
“fishing_advisory”: False, “fishing_jobs_lost”: 0,
“fishing_revenue_loss_usd”: 0, “iron_revenue_at_risk_usd”: 0,
“ballast_surcharge_usd”: 0, “port_jobs_lost”: 0,
“total_port_annual_cost_usd”: 0,
}

```
# St. Louis River additional loading (Hg dominant)
new_hg_loading_mult = 1 + (phys["methyl_hg_ng_l"] * 0.12 /
                           ST_LOUIS_R_CURRENT_HG_NG_L)

# Municipal water intake impact
intake_upgrade_required = phys["methyl_hg_ng_l"] * 0.12 > 2.0  # ng/L
intake_cost = INTAKE_TREATMENT_UPGRADE_USD if intake_upgrade_required else 0

# Dredge disposal cost escalation
harbor_contaminated_frac = min(1.0, new_hg_loading_mult - 1)
annual_dredge_cost = (ANNUAL_DREDGE_M3 *
                      (DREDGE_DISPOSAL_COST_USD_M3 * harbor_contaminated_frac +
                       18 * (1 - harbor_contaminated_frac)))

# Canadian transit restrictions
# Triggered when canada_sulfate_mg_l exceeds treaty threshold sustainably
canadian_refusal_prob = (CANADIAN_PORT_REFUSAL_PROBABILITY
                         if phys["canada_sulfate_mg_l"] > 10 else 0)
backhaul_revenue_loss = LOST_BACKHAUL_REVENUE_USD_YR * canadian_refusal_prob

# Commercial fishing collapse on Lake Superior
fishing_advisory_triggered = fish["fish_advisory_triggered"]
fishing_job_loss = COMMERCIAL_FISHING_JOBS_LS if fishing_advisory_triggered else 0
fishing_revenue_loss = COMMERCIAL_FISHING_REVENUE_YR if fishing_advisory_triggered else 0

# Iron ore throughput impact — Iron Range mines use same transport
# corridor; if regional opposition blocks permits, ore doesn't reach port
iron_ore_throughput_risk = 0.05 if mine_active else 0
iron_revenue_at_risk = DULUTH_ECON_IMPACT_USD_YR * \
                       (DULUTH_IRON_ORE_TONNES / DULUTH_TOTAL_CARGO_TONNES_YR) * \
                       iron_ore_throughput_risk

# Ship ballast treatment surcharge
ballast_surcharge = (SHIPPING_BALLAST_DISCHARGE_M3_YR *
                     IMO_CONTAMINATED_ADDITIONAL *
                     min(1.0, phys["methyl_hg_ng_l"] / 5.0))

# Port jobs at risk (direct + indirect)
port_jobs_frac_at_risk = min(0.18,
                             (harbor_contaminated_frac * 0.4 +
                              (1 if fishing_advisory_triggered else 0) * 0.08 +
                              canadian_refusal_prob * 0.5))
port_jobs_lost = int((DULUTH_PORT_JOBS_DIRECT + DULUTH_PORT_JOBS_INDIRECT) *
                     port_jobs_frac_at_risk)

total_port_annual_cost = (annual_dredge_cost + backhaul_revenue_loss +
                          fishing_revenue_loss + iron_revenue_at_risk +
                          ballast_surcharge)

return {
    "hg_loading_increase":          new_hg_loading_mult - 1,
    "intake_upgrade_required":      intake_upgrade_required,
    "intake_upgrade_capex_usd":     intake_cost,
    "annual_dredge_cost_usd":       annual_dredge_cost,
    "canadian_refusal_prob":        canadian_refusal_prob,
    "backhaul_loss_usd":            backhaul_revenue_loss,
    "fishing_advisory":             fishing_advisory_triggered,
    "fishing_jobs_lost":            fishing_job_loss,
    "fishing_revenue_loss_usd":     fishing_revenue_loss,
    "iron_revenue_at_risk_usd":     iron_revenue_at_risk,
    "ballast_surcharge_usd":        ballast_surcharge,
    "port_jobs_lost":               port_jobs_lost,
    "total_port_annual_cost_usd":   total_port_annual_cost,
}
```
