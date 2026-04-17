"""
BWCA sulfide mine cascade simulation — physical constants.
All values sourced from peer-reviewed lit, EPA records, or USFS 2022 EA.
CC0. Stdlib only.
"""

# ─────────────────────────────────────────────────────────────

# LAYER 0 — CHEMISTRY (non-negotiable, ΔG < 0)

# ─────────────────────────────────────────────────────────────

# Acid generation from pyrite oxidation (Singer-Stumm, 1970)

# FeS2 + 7/2 O2 + H2O -> Fe2+ + 2 SO4(2-) + 2 H+

SULFATE_PER_TONNE_ORE_KG     = 45.0    # kg SO4 per tonne waste rock
ACID_GENERATION_RATE_MOL_YR  = 0.18    # mol H+/kg sulfide/yr (catalyzed)
MICROBIAL_AMPLIFICATION      = 1e6     # Acidithiobacillus vs abiotic

# Heavy metal release (USGS 2013, Twin Metals ore body assay)

HG_PER_TONNE_MG      = 2.4
PB_PER_TONNE_MG      = 180.0
AS_PER_TONNE_MG      = 95.0
CU_LEACH_FRAC        = 0.015   # dissolved fraction under AMD conditions
NI_LEACH_FRAC        = 0.022

# ─────────────────────────────────────────────────────────────

# LAYER 1 — HYDROLOGY (Rainy River watershed)

# ─────────────────────────────────────────────────────────────

# Gravity-driven, unidirectional. No reverse flow.

KAWISHIWI_DISCHARGE_M3_S      = 24.0    # mean annual
BWCA_LAKE_COUNT               = 1175
BWCA_INTERCONNECT_FRAC        = 0.78    # frac linked by portage/stream
MEAN_LAKE_RESIDENCE_YR        = 3.2     # low flush -> accumulation
RAINY_TO_LOTW_TRANSIT_DAYS    = 180
INTL_BOUNDARY_FLUX_FRAC       = 0.62    # frac reaching Canada

# Wild rice sulfate threshold (MN Rule 7050.0224, manoomin science)

SULFATE_STRESS_MG_L           = 5.0     # onset of sub-lethal effects (Pastor et al. 2017)
SULFATE_TOXIC_MG_L            = 10.0    # MN Rule 7050.0224 wild-rice standard
SULFATE_LETHAL_MG_L           = 50.0    # lethal to Zizania palustris (Myrbo et al. 2017)

# ─────────────────────────────────────────────────────────────
# LAYER 2 — ECOLOGY (behavioral / sociological assumptions)
# ─────────────────────────────────────────────────────────────
# These are structural assumptions, not measured constants.
# They drive the community-layer headline numbers (forced
# migrants, wells contaminated). Sensitivity analysis should
# vary them.

WELL_CONTAMINATION_THRESHOLD_MG_L = 40.0   # sulfate at which all shallow wells fail
WELL_CONTAMINATION_LAG_YR         = 2      # transport time surface -> shallow aquifer
MIGRATION_WEIGHT_WELLS            = 0.7    # weight: well failure drives migration
MIGRATION_WEIGHT_MANOOMIN         = 0.3    # weight: manoomin loss drives migration
MIGRATION_CAP_FRAC                = 0.65   # max fraction of population that migrates
FOREST_LOSS_CAP_FRAC              = 0.4    # max fraction of corridor affected
FOREST_SENSITIVITY_MG_L           = 200.0  # sulfate at which forest loss hits cap
PORT_IMPACT_CAP_FRAC              = 0.3    # max fraction of port jobs at risk
AMPHIBIAN_COLLAPSE_MG_L           = 30.0   # sulfate threshold for amphibian collapse
TOURISM_COLLAPSE_MG_L             = 15.0   # sulfate at which tourism fully collapses

# ─────────────────────────────────────────────────────────────

CARBONATE_BUFFER_EQ_KG_M2     = 0.04    # near zero on Shield granite
PEAT_HG_METHYLATION_RATE      = 0.31    # frac inorganic Hg -> MeHg
GLACIAL_TILL_DEPTH_M          = 0.8     # thin, minimal acid attenuation
WATER_TABLE_DEPTH_M           = 2.1     # shallow — contamination fast

# ─────────────────────────────────────────────────────────────

# LAYER 3 — ECOLOGY

# ─────────────────────────────────────────────────────────────

LAKE_TROUT_HG_BAF             = 2.7e6   # bioaccumulation factor
LOON_HG_LETHAL_PPM            = 4.0
MANOOMIN_ACRES_AT_RISK        = 18_400
BOREAL_FOREST_ACRES_CORRIDOR  = 234_000
AMPHIBIAN_PH_LETHAL           = 5.2

# ─────────────────────────────────────────────────────────────

# LAYER 4 — HUMAN SYSTEMS

# ─────────────────────────────────────────────────────────────

# Employment (Antofagasta / Twin Metals projection vs Harvard 2020)

MINE_JOBS_DIRECT              = 700
MINE_JOB_DURATION_YR          = 20
TOURISM_JOBS_CURRENT          = 17_000   # NE MN, BWCA-dependent
TOURISM_REVENUE_ANNUAL_USD    = 540e6
LUMBER_JOBS_CORRIDOR          = 2_100
LUMBER_REVENUE_ANNUAL_USD     = 185e6

# Population at risk (Ely, Babbitt, Tower, Winton, reservation lands)

RESIDENTS_WITHIN_20KM         = 12_400
WELL_DEPENDENT_FRAC           = 0.84    # shallow wells, Shield geology
BOIS_FORTE_ENROLLMENT         = 3_400
GRAND_PORTAGE_ENROLLMENT      = 1_100
FOND_DU_LAC_ENROLLMENT        = 4_200

# ─────────────────────────────────────────────────────────────

# LAYER 5 — PORT / RESERVOIR FUNCTIONS

# ─────────────────────────────────────────────────────────────

# Duluth-Superior is #1 Great Lakes port by tonnage

DULUTH_SUPERIOR_TONNAGE_ANNUAL = 35e6   # short tons
DULUTH_PORT_JOBS              = 7_800
IRON_ORE_FRAC_OF_PORT_TRAFFIC = 0.62
LAKE_SUPERIOR_RESIDENCE_YR    = 191     # pollution persists ~2 centuries

# Reservoir capacity for drought / wildfire suppression

BWCA_RESERVOIR_CAPACITY_KM3   = 12.4
DOWNSTREAM_USERS_RELIANT      = 680_000  # Rainy R. + LOTW basin

# ─────────────────────────────────────────────────────────────

# LAYER 6 — INTERNATIONAL LAW

# ─────────────────────────────────────────────────────────────

# Boundary Waters Treaty 1909, Art. IV:

# "waters…shall not be polluted on either side to the injury

# of health or property on the other"

# Trail Smelter arbitration (1941) precedent: transboundary harm

# creates state liability under customary intl law.

TREATY_SULFATE_BREACH_MG_L    = 10.0    # manoomin/IJC standard
IJC_TRIGGER_DAYS              = 90      # sustained exceedance -> referral
BREACH_LIABILITY_USD_ANNUAL   = 2.8e9   # est. NPV of treaty damages

# ─────────────────────────────────────────────────────────────

# SIMULATION PARAMETERS

# ─────────────────────────────────────────────────────────────

SIM_YEARS           = 500    # sulfide drainage persists centuries
MINE_START_YEAR     = 5      # permitting lag
ORE_TONNES_ANNUAL   = 20_000 * 365    # 20 kt/day design
WASTE_ROCK_RATIO    = 2.8             # waste:ore
TAILINGS_FAILURE_P  = 0.012           # annual, Mount Polley-class basis
