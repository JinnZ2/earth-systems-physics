"""
Economic externality constants for BWCA sulfide mine cascade.
Sources: EPA Superfund cost accounting, HUD proximity studies,
CDC/NIOSH mining occupational health, ATSDR Hg/Pb/As tox profiles,
MN DEED infrastructure cost reports, MISO grid load studies.
CC0. Stdlib only.
"""

# ═════════════════════════════════════════════════════════════
# HOME / PROPERTY DEPRECIATION
# ═════════════════════════════════════════════════════════════
# HUD + peer-reviewed hedonic studies (Boyle & Kiel 2001, Sims 2009):
# proximity to hardrock mining depresses property values 15-35%;
# contaminated wells depress 40-60%; Superfund-listed areas 50-75%.
HOMES_WITHIN_20KM              = 5_840
MEDIAN_HOME_VALUE_USD          = 185_000    # St. Louis + Lake County, MN 2026
DEPRECIATION_ACTIVE_MINE       = 0.22       # 22% while operating
DEPRECIATION_WELL_CONTAMINATED = 0.52       # 52% loss
DEPRECIATION_SUPERFUND_LISTED  = 0.68       # 68% loss
DEPRECIATION_RECOVERY_YEARS    = 45         # post-remediation

# Commercial property (resorts, outfitters, lodges)
COMMERCIAL_PROPERTIES_AT_RISK  = 340
MEDIAN_COMMERCIAL_VALUE_USD    = 620_000
COMMERCIAL_DEPRECIATION        = 0.58       # tourism-dependent = harder hit

# Tax base collapse
PROPERTY_TAX_RATE              = 0.0112     # avg MN effective rate

# ═════════════════════════════════════════════════════════════
# WORKER HEALTH IMPACTS
# ═════════════════════════════════════════════════════════════
# NIOSH mining mortality & morbidity; ATSDR heavy metal tox
MINE_WORKFORCE                 = 700
CONTRACTOR_EXPOSURE_POOL       = 1_200      # truckers, maintenance, etc.
COMMUNITY_EXPOSURE_POOL        = 12_400     # all residents within 20km

# Occupational disease incidence (per-worker lifetime probability)
SILICOSIS_INCIDENCE            = 0.08       # underground hardrock
PULMONARY_FIBROSIS_INCIDENCE   = 0.11
HEARING_LOSS_INCIDENCE         = 0.34
MUSCULOSKELETAL_INCIDENCE      = 0.52
MINING_FATAL_INJURY_RATE       = 14.5e-5    # per worker-year (MSHA)

# Heavy metal body-burden disease (community-wide, downstream)
# Follows Hg/Pb/As exposure thresholds × years of exposure
HG_NEURO_IMPAIRMENT_THRESHOLD  = 5.8        # µg/g hair
PB_COGNITIVE_LOSS_THRESHOLD    = 5.0        # µg/dL blood
AS_CANCER_RISK_PER_UG_L        = 1.5e-4     # lifetime cancer risk per µg/L
KIDS_UNDER_18_FRAC             = 0.22       # more vulnerable to Pb/Hg

# Cost per case (lifetime, 2026 USD, CDC/ACS cost-of-illness)
COST_SILICOSIS_LIFETIME        = 680_000
COST_PULMONARY_FIBROSIS_LIFE   = 720_000
COST_HEARING_LOSS_LIFETIME     = 145_000
COST_NEURO_IMPAIRMENT_CHILD    = 1_200_000  # IQ loss, special ed, lost earnings
COST_CANCER_LIFETIME           = 430_000
COST_FATAL_INJURY_VSL          = 11_600_000  # EPA value of statistical life

# ═════════════════════════════════════════════════════════════
# LONG-TERM CARE LOAD
# ═════════════════════════════════════════════════════════════
# Per-case annualized LTC for chronic exposure disease
LTC_ANNUAL_NEURO_CASE          = 52_000     # home health + medical
LTC_ANNUAL_PULMONARY_CASE      = 38_000
LTC_ANNUAL_CANCER_CASE         = 94_000     # active treatment
LTC_FACILITY_CAPACITY_NE_MN    = 2_400      # current bed count
LTC_FACILITY_UTILIZATION       = 0.87       # baseline 87% full
LTC_MEDICAID_FRAC              = 0.62       # frac covered by state

# ═════════════════════════════════════════════════════════════
# COMMUNITY FINANCIAL LOAD
# ═════════════════════════════════════════════════════════════
# Municipal services that scale with contamination events
WATER_TREATMENT_UPGRADE_PER_CAP = 8_400     # RO + activated carbon systems
WATER_SYSTEM_OM_PER_CAP_YEAR   = 340        # ongoing treatment cost
EMERGENCY_RESPONSE_BASE_PER_CAP = 215       # baseline municipal EM budget
EMERGENCY_RESPONSE_MINE_MULT   = 2.6        # multiplier when active mine
SCHOOL_SPED_COST_PER_CASE      = 24_500     # annual, Pb/Hg cognitive impact
PUBLIC_HEALTH_SURVEILLANCE     = 85         # per-cap annual during exposure
MENTAL_HEALTH_CRISIS_PER_CAP   = 165        # displacement / loss trauma

# Tax base impact
ELY_ANNUAL_BUDGET_USD          = 6.8e6
BABBITT_ANNUAL_BUDGET_USD      = 3.1e6
TOWER_ANNUAL_BUDGET_USD        = 1.9e6
ST_LOUIS_COUNTY_BUDGET_USD     = 420e6
LAKE_COUNTY_BUDGET_USD         = 38e6

# ═════════════════════════════════════════════════════════════
# STATE FINANCIAL LOAD (MN + federal share)
# ═════════════════════════════════════════════════════════════
# EPA Superfund average cleanup cost for hardrock mine:
# $500M-$2B per site; 100-year trust fund obligations common
SUPERFUND_CLEANUP_COST_USD     = 1.2e9      # mid-range hardrock estimate
PERPETUAL_WATER_TREATMENT_YR   = 45e6       # annual, in perpetuity
MINE_CLOSURE_BOND_SHORTFALL    = 0.72       # frac of real cost NOT bonded
# (industry bonds consistently 20-35% of actual remediation cost)

# Medicaid / state healthcare
MN_MEDICAID_ANNUAL_PER_ENROLLEE = 9_800
MEDICAID_ELIGIBILITY_SHIFT      = 0.18      # frac displaced → eligible

# State economic development writeoffs when tourism collapses
MN_TOURISM_TAX_REVENUE         = 1.4e9      # statewide annual
BWCA_CORRIDOR_SHARE_OF_TOURISM = 0.09       # ~9% of state tourism tax

# Federal: IHS obligations to 1854 Treaty bands
IHS_PER_CAPITA_CURRENT         = 4_100      # drastically underfunded baseline
IHS_ADEQUATE_PER_CAPITA        = 12_800     # parity with Medicare
TREATY_BAND_ENROLLMENT         = 8_700      # Bois Forte + Grand Portage + Fond du Lac

# ═════════════════════════════════════════════════════════════
# INFRASTRUCTURE + POWER DEPLETION
# ═════════════════════════════════════════════════════════════
# Proposed Twin Metals electrical load: ~85 MW continuous
MINE_POWER_DEMAND_MW           = 85
MINE_CAPACITY_FACTOR           = 0.94       # nearly constant load

# NE MN grid context (MISO North zone)
NE_MN_CURRENT_PEAK_MW          = 820
NE_MN_RESERVE_MARGIN           = 0.13       # already below 15% target
ELY_SUBSTATION_CAPACITY_MW     = 42         # would require new substation
NEW_SUBSTATION_COST_USD        = 180e6
TRANSMISSION_UPGRADE_COST_USD  = 340e6      # new 230kV line required
RATEPAYER_SHARE_OF_UPGRADES    = 0.78       # socialized onto MN ratepayers
INDUSTRY_SHARE_OF_UPGRADES     = 0.22

# Water demand competing with communities
MINE_WATER_DEMAND_M3_DAY       = 14_000     # process + cooling
COMMUNITY_WATER_DEMAND_M3_DAY  = 4_200      # Ely + Babbitt + Tower combined
AQUIFER_RECHARGE_M3_DAY        = 22_000     # Shield hydrogeology, limited
WATER_STRESS_THRESHOLD         = 0.75       # demand/recharge ratio

# Road infrastructure (ore haul damage)
ORE_TRUCK_TRIPS_PER_DAY        = 280
ROAD_DAMAGE_MULT_VS_CAR        = 9_600      # GVWR^4 law, loaded ore truck
HWY_169_135_ANNUAL_MAINT_USD   = 3.2e6      # current
HWY_DEGRADATION_ACCELERATION   = 4.8        # multiplier when ore traffic active

# Broadband / emergency comms (rural, already fragile)
CELL_TOWERS_IN_CORRIDOR        = 18
TOWER_POWER_SHARE_OF_GRID      = 0.008
EMS_RESPONSE_TIME_BASE_MIN     = 28         # already rural-long
EMS_DEGRADATION_MULT           = 1.6        # when mine traffic / events
