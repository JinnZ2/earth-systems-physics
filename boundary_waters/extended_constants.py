"""
Extended constants — lumber, fish consumption, climate, air quality,
wildfire, port. Sources: USFS FIA, EPA CAMD, NOAA climate projections,
CDC ATSDR, GLIFWC fish consumption surveys, MPCA Hg TMDL, Duluth Seaway
Port Authority annual reports, IMO MARPOL Annex VI.
"""

# ═════════════════════════════════════════════════════════════

# LUMBER / FOREST DEGRADATION

# ═════════════════════════════════════════════════════════════

# USFS FIA data + Scandinavian acid deposition studies (Tamm 1991)

STANDING_TIMBER_VOLUME_M3      = 14.2e6     # merchantable, corridor
PULP_VOLUME_FRAC               = 0.58        # pulp vs sawtimber split
SAWTIMBER_VALUE_USD_M3         = 180
PULPWOOD_VALUE_USD_M3          = 42

# Acid deposition impact (wet + dry from SO2 + direct sulfate plume)

ACID_DEPOSITION_GROWTH_LOSS    = 0.08        # frac/yr at high deposition
NEEDLE_RETENTION_LOSS          = 0.22        # boreal conifer mass balance
SOIL_CA_DEPLETION_HALF_LIFE_YR = 18          # Shield soils shallow Ca pool
MYCORRHIZAL_COLLAPSE_PH        = 4.3         # below this, fungal symbionts die

# Species-level vulnerability (species composition of corridor)

SPRUCE_FIR_FRAC                = 0.42
ASPEN_BIRCH_FRAC               = 0.31
PINE_FRAC                      = 0.19
CEDAR_TAMARACK_FRAC            = 0.08
SPRUCE_ACID_VULNERABILITY      = 0.85        # very high — Shield spruce
ASPEN_ACID_VULNERABILITY       = 0.45
PINE_ACID_VULNERABILITY        = 0.68
CEDAR_ACID_VULNERABILITY       = 0.92        # wetland conifers most exposed

# Pulp/paper contamination — Hg uptake in cellulose disqualifies

# certain grades (food packaging, medical)

HG_PULP_REJECTION_THRESHOLD    = 0.5          # mg/kg dry basis
PULP_GRADE_LOSS_FRAC           = 0.35         # frac of pulp rejected from premium

# Sawmill workforce

SAWMILL_JOBS_CORRIDOR          = 840
LOGGING_JOBS_CORRIDOR          = 1_260
MILL_OPERATIONS_COUNT          = 7

# ═════════════════════════════════════════════════════════════

# FISH CONSUMPTION (Ojibwe amplifier)

# ═════════════════════════════════════════════════════════════

# GLIFWC (Great Lakes Indian Fish & Wildlife Commission) subsistence

# surveys show 1854/1842/1837 Treaty band members consume 5-10×

# state-average fish. Pregnant/nursing women most vulnerable.

STATE_AVG_FISH_CONSUMPTION_G_DAY      = 18
OJIBWE_SUBSISTENCE_G_DAY              = 142   # mean
OJIBWE_HIGH_CONSUMER_G_DAY            = 285   # 90th percentile
AMPLIFICATION_FACTOR_MEAN             = 7.9
AMPLIFICATION_FACTOR_HIGH             = 15.8

# Fish species weighting (walleye + pike = top Hg accumulators)

WALLEYE_CONSUMPTION_FRAC              = 0.38
PIKE_CONSUMPTION_FRAC                 = 0.22
LAKE_TROUT_CONSUMPTION_FRAC           = 0.14
WHITEFISH_CONSUMPTION_FRAC            = 0.11
OTHER_FISH_CONSUMPTION_FRAC           = 0.15

# Tissue Hg concentration factor vs water (L/kg, empirical from MPCA data)

# Walleye in BWCA lakes: ~0.3-1.5 mg/kg at water Hg 0.5-2 ng/L methyl-Hg

WALLEYE_BAF                           = 7.5e5
PIKE_BAF                              = 6.2e5
LAKE_TROUT_BAF                        = 3.4e5
WHITEFISH_BAF                         = 1.4e5

# EPA reference dose methyl-Hg: 0.1 µg/kg bw/day

EPA_MEHG_RFD_UG_KG_DAY                = 0.1
MEAN_ADULT_BW_KG                      = 72
MEAN_CHILD_BW_KG                      = 24
MEAN_INFANT_BW_KG                     = 8    # breastfed, Hg through milk

# Pregnancy outcomes — Faroe Islands & Seychelles cohort studies

MEHG_IQ_LOSS_POINTS_PER_UG_G_HAIR     = 0.18  # developmental
OJIBWE_ENROLLMENT_TOTAL               = 8_700
OJIBWE_PREGNANCY_RATE_ANNUAL          = 0.052
OJIBWE_CHILD_FRAC                     = 0.28
OJIBWE_HIGH_CONSUMER_FRAC             = 0.35  # frac in high-consumer tier

# Cultural/economic value of subsistence harvest

HARVEST_REPLACEMENT_COST_USD_PER_CAP  = 2_400  # annual food sovereignty cost

# ═════════════════════════════════════════════════════════════

# CLIMATE AMPLIFICATION

# ═════════════════════════════════════════════════════════════

# Temperature acceleration of oxidation (Arrhenius, AMD-specific)

# Singer & Stumm 1970; Nordstrom & Alpers 1999

AMD_Q10_FACTOR                 = 2.1         # rate doubles per 10°C
BASELINE_ANNUAL_TEMP_C         = 3.4         # NE MN current
PROJECTED_TEMP_RISE_2100_C     = 4.8         # RCP 8.5 northern MN
PROJECTED_TEMP_RISE_2050_C     = 2.3

# Precipitation / flushing

BASELINE_PRECIP_MM_YR          = 720
PRECIP_INCREASE_FRAC_2100      = 0.15
EXTREME_EVENT_FREQ_MULT_2100   = 2.4          # 100-yr storms per decade

# Permafrost / frozen tailings (tailings dams rely on frozen cores)

PERMAFROST_THAW_RATE_CM_YR     = 4.2
TAILINGS_DAM_FROZEN_CORE_M     = 12           # typical design depth
DAM_FAILURE_MULT_FROM_THAW     = 3.6          # empirical, Arctic mining

# Wildfire season extension

FIRE_SEASON_DAYS_BASELINE      = 128
FIRE_SEASON_DAYS_2100          = 178
FIRE_WEATHER_EXTREME_FREQ      = 2.8          # mult vs baseline

# Drought-flood whiplash

DROUGHT_FREQ_MULT_2100         = 1.9          # concentrates contaminants
FLOOD_FREQ_MULT_2100           = 2.1          # mobilizes tailings

# ═════════════════════════════════════════════════════════════

# AIR QUALITY

# ═════════════════════════════════════════════════════════════

# SO2 from smelter (if co-located) + fugitive dust + diesel fleet

SO2_EMISSION_TONNES_YR         = 3_400        # typical Cu smelter
PM25_EMISSION_TONNES_YR        = 180          # tailings dust + diesel
PM10_EMISSION_TONNES_YR        = 620
NOX_EMISSION_TONNES_YR         = 1_200
HG_AIR_EMISSION_KG_YR          = 85           # atmospheric Hg deposition

# Health impact (EPA BenMAP equivalents)

ASTHMA_ATTACKS_PER_TONNE_SO2   = 12           # per yr, per exposed child
COPD_HOSPITALIZATIONS_PM25     = 0.0048        # per µg/m3 annual
CARDIOVASCULAR_DEATHS_PM25     = 0.0014        # per µg/m3 long-term
ACUTE_RESP_PER_TONNE_PM10      = 34

# Cost per health event

ASTHMA_ATTACK_COST_USD         = 580
COPD_HOSP_COST_USD             = 18_400
CARDIOVASCULAR_DEATH_VSL       = 11_600_000

# Visibility / regional haze (Class I areas incl. BWCA Wilderness)

BWCA_VISIBILITY_BASELINE_KM    = 165
VISIBILITY_LOSS_KM_PER_TONNE_SO2 = 0.012
CLASS_I_PROTECTION_THRESHOLD   = 135          # km; federal regulatory floor

# Crop / forage yield (downwind agricultural zones)

SOYBEAN_YIELD_LOSS_PER_PPB_O3  = 0.0012
CORN_YIELD_LOSS_PER_PPB_O3     = 0.0008
NOX_TO_OZONE_CONVERSION        = 0.34

# ═════════════════════════════════════════════════════════════

# WILDFIRE AMPLIFICATION

# ═════════════════════════════════════════════════════════════

# Forest + tailings interaction: dead/stressed timber = fuel load;

# wildfire over tailings = pyrometallurgical release of heavy metals

CORRIDOR_FOREST_ACRES          = 234_000
BASELINE_FIRE_PROBABILITY_YR   = 0.008        # per acre, baseline
STRESSED_FOREST_FIRE_MULT      = 3.4          # beetle-killed/acid-damaged
TAILINGS_OVERRUN_FRAC_PER_FIRE = 0.02         # large fires reach tailings

# Emissions from combusted tailings-contaminated biomass

HG_RELEASE_FRAC_FROM_FIRE      = 0.92         # highly volatile
PB_RELEASE_FRAC_FROM_FIRE      = 0.31
AS_RELEASE_FRAC_FROM_FIRE      = 0.48

# Firefighter exposure

FIREFIGHTER_EXPOSURE_DAYS_BIG  = 45
FIREFIGHTER_CANCER_RR          = 1.14          # NIOSH meta-analysis

# Suppression cost

SUPPRESSION_COST_USD_ACRE      = 2_800
EVAC_COST_USD_PER_RESIDENT     = 1_850
STRUCTURE_LOSS_AVG_USD         = 340_000
BWCA_RECREATION_CLOSURE_COST   = 2.8e6        # per closure event

# ═════════════════════════════════════════════════════════════

# PORT CASCADE (Duluth-Superior)

# ═════════════════════════════════════════════════════════════

# Port is Great Lakes #1 by tonnage. Cargoes: iron ore (62%),

# coal (12%), grain (14%), salt/cement/general (12%).

DULUTH_TOTAL_CARGO_TONNES_YR   = 35e6         # short tons
DULUTH_IRON_ORE_TONNES         = 21.7e6
DULUTH_COAL_TONNES             = 4.2e6
DULUTH_GRAIN_TONNES            = 4.9e6
DULUTH_OTHER_TONNES            = 4.2e6

DULUTH_PORT_JOBS_DIRECT        = 7_800
DULUTH_PORT_JOBS_INDIRECT      = 13_100
DULUTH_ECON_IMPACT_USD_YR      = 1.56e9

# St. Louis River Hg TMDL — already impaired

ST_LOUIS_R_CURRENT_HG_NG_L     = 1.8           # already above walleye advisory
ST_LOUIS_R_TMDL_LIMIT          = 1.3
SLRAOC_REMEDIATION_USD_SPENT   = 470e6         # Great Lakes Legacy Act, to date

# Contamination pathway: tailings dust + St. Louis River drainage

# converge in Duluth Harbor / Lake Superior

HARBOR_SEDIMENT_CONTAM_MULT    = 2.3           # multiplier if new loading
DREDGE_DISPOSAL_COST_USD_M3    = 180           # contaminated vs 18 clean
ANNUAL_DREDGE_M3               = 280_000

# Ship ballast / contamination transit

SHIPPING_BALLAST_DISCHARGE_M3_YR = 4.8e6
IMO_BALLAST_TREATMENT_COST      = 0.42          # USD/m3 baseline
IMO_CONTAMINATED_ADDITIONAL     = 2.8           # USD/m3 surcharge

# Canadian transit — Ontario Great Lakes access

CANADIAN_PORT_REFUSAL_PROBABILITY = 0.18        # when contamination rises
LOST_BACKHAUL_REVENUE_USD_YR   = 140e6

# Fish advisory zones closing commercial fishing

COMMERCIAL_FISHING_JOBS_LS     = 420
COMMERCIAL_FISHING_REVENUE_YR  = 38e6

# Water intake for Duluth / Superior / Two Harbors

MUNICIPAL_INTAKE_POPULATION    = 186_000
INTAKE_TREATMENT_UPGRADE_USD   = 240e6          # if Hg crosses MCL trigger
