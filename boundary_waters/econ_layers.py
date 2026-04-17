"""
Economic externality layers. Each reads physical cascade state
and computes dollar / case / MW / m3 loads distributed across
homeowners, workers, communities, state, and shared infrastructure.

Coupling:
physical_cascade ──► home_depreciation_layer
├──► worker_health_layer
├──► community_load_layer
├──► state_load_layer
└──► infrastructure_layer
↑
└── power_water_layer (competes with community)
"""

from math import exp
from econ_constants import *
from constants import MINE_JOB_DURATION_YR

# ═════════════════════════════════════════════════════════════

# E0 — HOME / PROPERTY DEPRECIATION

# ═════════════════════════════════════════════════════════════

def home_depreciation_layer(phys, mine_active):
    """
    Home value loss scales with contamination severity.
    Wells contaminated = immediate severe depreciation.
    Superfund listing triggers additional loss (happens when
    sulfate or Hg exceeds chronic thresholds for >5 yr).
    Commercial loss amplifies with cumulative population outmigration.
    """
    # No mine contamination, no active mining -> no economic loss
    no_impact = (not mine_active
                 and phys["sulfate_mg_l"] == 0
                 and phys["wells_contaminated"] == 0
                 and phys["forced_migrants"] == 0)
    if no_impact:
        return {
            "depreciation_frac": 0.0,
            "residential_loss_usd": 0.0,
            "commercial_loss_usd": 0.0,
            "total_property_loss_usd": 0.0,
            "annual_tax_base_loss": 0.0,
            "superfund_flag": False,
        }

    # Fraction of homes with contaminated wells
    well_frac = phys["wells_contaminated"] / max(HOMES_WITHIN_20KM, 1)
    well_frac = min(1.0, well_frac)

    # Superfund-class contamination trigger
    superfund_flag = phys["sulfate_mg_l"] > 30 or phys["hg_ng_l"] > 10

    # Blended depreciation factor
    if superfund_flag:
        dep_frac = DEPRECIATION_SUPERFUND_LISTED
    elif well_frac > 0.3:
        dep_frac = DEPRECIATION_WELL_CONTAMINATED * well_frac + \
                   DEPRECIATION_ACTIVE_MINE * (1 - well_frac)
    elif mine_active:
        dep_frac = DEPRECIATION_ACTIVE_MINE
    else:
        # Post-closure partial recovery (slow)
        dep_frac = DEPRECIATION_ACTIVE_MINE * 0.4

    # Outmigration amplifies commercial abandonment
    # (empty town = resort/lodge value collapses further)
    migration_frac = phys["forced_migrants"] / max(HOMES_WITHIN_20KM, 1)
    abandonment_mult = 1.0 + migration_frac * 0.6
    commercial_dep = min(0.92, COMMERCIAL_DEPRECIATION * abandonment_mult)

    residential_loss_usd = HOMES_WITHIN_20KM * MEDIAN_HOME_VALUE_USD * dep_frac
    commercial_loss_usd  = COMMERCIAL_PROPERTIES_AT_RISK * MEDIAN_COMMERCIAL_VALUE_USD * \
                           commercial_dep * (1 if mine_active or superfund_flag else 0.5)

    tax_base_loss = (residential_loss_usd + commercial_loss_usd) * PROPERTY_TAX_RATE

    return {
        "depreciation_frac":       dep_frac,
        "residential_loss_usd":    residential_loss_usd,
        "commercial_loss_usd":     commercial_loss_usd,
        "total_property_loss_usd": residential_loss_usd + commercial_loss_usd,
        "annual_tax_base_loss":    tax_base_loss,
        "superfund_flag":          superfund_flag,
    }

# ═════════════════════════════════════════════════════════════

# E1 — WORKER + COMMUNITY HEALTH

# ═════════════════════════════════════════════════════════════

def worker_health_layer(phys, mine_active, years_mine_active):
    """
    Occupational: mining workforce exposure.
    Community: downstream metal body-burden.
    Pediatric: Pb/Hg neurodevelopmental (irreversible).
    Costs compound over worker tenure and exposure duration.
    """
    # Occupational disease (cumulative over mine life)
    active_exposure_yrs = min(years_mine_active, MINE_JOB_DURATION_YR)
    worker_yr_exposure = MINE_WORKFORCE * active_exposure_yrs

    silicosis_cases      = int(worker_yr_exposure * SILICOSIS_INCIDENCE / MINE_JOB_DURATION_YR)
    fibrosis_cases       = int(worker_yr_exposure * PULMONARY_FIBROSIS_INCIDENCE / MINE_JOB_DURATION_YR)
    hearing_loss_cases   = int(worker_yr_exposure * HEARING_LOSS_INCIDENCE / MINE_JOB_DURATION_YR)
    fatal_injuries       = worker_yr_exposure * MINING_FATAL_INJURY_RATE

    # Community metal exposure — scales with ambient contamination
    # Hg body burden follows methyl-Hg in fish × consumption
    hg_exposure_factor = min(1.0, phys["methyl_hg_ng_l"] / HG_NEURO_IMPAIRMENT_THRESHOLD)
    as_exposure_factor = min(1.0, phys["sulfate_mg_l"] / 100.0)   # As co-leaches

    # Children most affected
    kids_exposed = int(COMMUNITY_EXPOSURE_POOL * KIDS_UNDER_18_FRAC)
    kids_neuro_impaired = int(kids_exposed * hg_exposure_factor * 0.15)
    adult_cancer_cases  = int(COMMUNITY_EXPOSURE_POOL * as_exposure_factor * 0.04)

    # Cost aggregation (lifetime)
    worker_health_cost = (
        silicosis_cases * COST_SILICOSIS_LIFETIME +
        fibrosis_cases * COST_PULMONARY_FIBROSIS_LIFE +
        hearing_loss_cases * COST_HEARING_LOSS_LIFETIME +
        fatal_injuries * COST_FATAL_INJURY_VSL
    )

    community_health_cost = (
        kids_neuro_impaired * COST_NEURO_IMPAIRMENT_CHILD +
        adult_cancer_cases * COST_CANCER_LIFETIME
    )

    return {
        "silicosis_cases":        silicosis_cases,
        "fibrosis_cases":         fibrosis_cases,
        "hearing_loss_cases":     hearing_loss_cases,
        "fatal_injuries":         fatal_injuries,
        "kids_neuro_impaired":    kids_neuro_impaired,
        "adult_cancer_cases":     adult_cancer_cases,
        "worker_health_cost_usd": worker_health_cost,
        "community_health_cost_usd": community_health_cost,
        "total_health_cost_usd":  worker_health_cost + community_health_cost,
    }

# ═════════════════════════════════════════════════════════════

# E2 — LONG-TERM CARE LOAD

# ═════════════════════════════════════════════════════════════

def ltc_layer(health):
    """
    Chronic disease population creates annualized LTC load.
    NE MN LTC capacity already 87% utilized — spillover forces
    out-of-region placement (family separation, higher cost).
    """
    annual_cases_active = (
        health["kids_neuro_impaired"] +
        health["fibrosis_cases"] +
        health["adult_cancer_cases"]
    )

    ltc_annual_cost = (
        health["kids_neuro_impaired"] * LTC_ANNUAL_NEURO_CASE +
        health["fibrosis_cases"] * LTC_ANNUAL_PULMONARY_CASE +
        health["adult_cancer_cases"] * LTC_ANNUAL_CANCER_CASE
    )

    # Facility capacity strain
    baseline_utilization = LTC_FACILITY_CAPACITY_NE_MN * LTC_FACILITY_UTILIZATION
    available_beds = LTC_FACILITY_CAPACITY_NE_MN - baseline_utilization
    new_demand = annual_cases_active * 0.4   # frac needing facility care
    capacity_shortfall = max(0, new_demand - available_beds)

    medicaid_ltc_cost = ltc_annual_cost * LTC_MEDICAID_FRAC

    return {
        "ltc_annual_cases":         annual_cases_active,
        "ltc_annual_cost_usd":      ltc_annual_cost,
        "ltc_medicaid_cost_usd":    medicaid_ltc_cost,
        "ltc_capacity_shortfall":   capacity_shortfall,
        "families_displaced_ltc":   int(capacity_shortfall),
    }

# ═════════════════════════════════════════════════════════════

# E3 — COMMUNITY FINANCIAL LOAD

# ═════════════════════════════════════════════════════════════

def community_load_layer(phys, prop, health, mine_active):
    """
    Municipal costs that scale with contamination + population
    displacement. Compared against actual municipal budgets
    to show where fiscal cliff hits.
    Zero load when no contamination and no mine.
    """
    # No mine, no contamination -> no incremental municipal load
    no_impact = (not mine_active
                 and phys["sulfate_mg_l"] == 0
                 and phys["forced_migrants"] == 0)
    if no_impact:
        return {
            "water_upgrade_capex_usd": 0, "water_om_annual_usd": 0,
            "em_annual_usd": 0, "sped_annual_usd": 0,
            "ph_surveillance_usd": 0, "mental_health_usd": 0,
            "municipal_annual_usd": 0, "tax_revenue_loss_usd": 0,
            "effective_deficit_usd": 0, "fiscal_stress_ratio": 0,
            "fiscal_collapse_flag": False,
        }

    exposed_pop = COMMUNITY_EXPOSURE_POOL

    # Water infrastructure upgrades (one-time + ongoing)
    water_upgrade_capex = phys["wells_contaminated"] * WATER_TREATMENT_UPGRADE_PER_CAP
    water_om_annual = exposed_pop * WATER_SYSTEM_OM_PER_CAP_YEAR

    # Emergency response
    em_multiplier = EMERGENCY_RESPONSE_MINE_MULT if mine_active else 1.2
    em_annual = exposed_pop * EMERGENCY_RESPONSE_BASE_PER_CAP * em_multiplier

    # School special ed (Pb/Hg cognitive impact on kids)
    sped_annual = health["kids_neuro_impaired"] * SCHOOL_SPED_COST_PER_CASE

    # Public health surveillance
    ph_annual = exposed_pop * PUBLIC_HEALTH_SURVEILLANCE if (mine_active or phys["sulfate_mg_l"] > 5) else 0

    # Mental health / displacement trauma
    mh_annual = phys["forced_migrants"] * MENTAL_HEALTH_CRISIS_PER_CAP

    municipal_annual = water_om_annual + em_annual + sped_annual + ph_annual + mh_annual

    # Compare to aggregate local budget
    local_budget_total = (ELY_ANNUAL_BUDGET_USD + BABBITT_ANNUAL_BUDGET_USD +
                          TOWER_ANNUAL_BUDGET_USD + LAKE_COUNTY_BUDGET_USD)
    fiscal_stress = municipal_annual / local_budget_total

    # Lost property tax revenue makes this worse
    revenue_loss = prop["annual_tax_base_loss"]
    effective_deficit = municipal_annual + revenue_loss

    return {
        "water_upgrade_capex_usd":  water_upgrade_capex,
        "water_om_annual_usd":      water_om_annual,
        "em_annual_usd":            em_annual,
        "sped_annual_usd":          sped_annual,
        "ph_surveillance_usd":      ph_annual,
        "mental_health_usd":        mh_annual,
        "municipal_annual_usd":     municipal_annual,
        "tax_revenue_loss_usd":     revenue_loss,
        "effective_deficit_usd":    effective_deficit,
        "fiscal_stress_ratio":      fiscal_stress,
        "fiscal_collapse_flag":     fiscal_stress > 0.20,
    }

# ═════════════════════════════════════════════════════════════

# E4 — STATE + FEDERAL FINANCIAL LOAD

# ═════════════════════════════════════════════════════════════

def state_load_layer(phys, health, ltc, comm, mine_active, year, superfund_flag, mine_ever_operated):
    """
    State picks up Medicaid, unfunded Superfund remediation gap,
    tourism tax revenue collapse, IHS treaty obligations.
    """
    # Medicaid shift (displaced population loses employer coverage)
    new_medicaid_enrollees = int(phys["forced_migrants"] * MEDICAID_ELIGIBILITY_SHIFT)
    medicaid_annual = (new_medicaid_enrollees * MN_MEDICAID_ANNUAL_PER_ENROLLEE +
                       ltc["ltc_medicaid_cost_usd"])

    # Superfund remediation gap (closure bond covers only ~28% of real cost)
    if superfund_flag:
        unfunded_cleanup = SUPERFUND_CLEANUP_COST_USD * MINE_CLOSURE_BOND_SHORTFALL
        perpetual_treatment_annual = PERPETUAL_WATER_TREATMENT_YR
    elif mine_ever_operated and not mine_active and year > 25:
        unfunded_cleanup = 0
        perpetual_treatment_annual = PERPETUAL_WATER_TREATMENT_YR * 0.3
    else:
        unfunded_cleanup = 0
        perpetual_treatment_annual = 0

    # Tourism tax revenue collapse
    tourism_frac_lost = min(1.0, phys["sulfate_mg_l"] / 15.0)
    tourism_tax_loss = MN_TOURISM_TAX_REVENUE * BWCA_CORRIDOR_SHARE_OF_TOURISM * tourism_frac_lost

    # Federal IHS treaty obligation (Bois Forte, Grand Portage, Fond du Lac)
    ihs_gap = (IHS_ADEQUATE_PER_CAPITA - IHS_PER_CAPITA_CURRENT) * TREATY_BAND_ENROLLMENT
    # Only booked when usufructuary rights impaired (manoomin loss)
    manoomin_lost = phys.get("manoomin_acres_lost", 0)
    treaty_violation_factor = manoomin_lost / 18_400 if manoomin_lost > 0 else 0
    ihs_obligation_annual = ihs_gap * treaty_violation_factor

    state_annual_load = medicaid_annual + perpetual_treatment_annual + \
                        tourism_tax_loss + ihs_obligation_annual

    return {
        "medicaid_annual_usd":      medicaid_annual,
        "unfunded_cleanup_usd":     unfunded_cleanup,
        "perpetual_treatment_usd":  perpetual_treatment_annual,
        "tourism_tax_loss_usd":     tourism_tax_loss,
        "ihs_obligation_usd":       ihs_obligation_annual,
        "state_annual_load_usd":    state_annual_load,
    }

# ═════════════════════════════════════════════════════════════

# E5 — INFRASTRUCTURE + POWER / WATER COMPETITION

# ═════════════════════════════════════════════════════════════

def infrastructure_layer(mine_active):
    """
    Grid capacity: mine wants 85 MW continuous from a region
    already below its 15% reserve margin target. Upgrades get
    socialized onto ratepayers (~78% per MN PUC pattern).

    Water: mine demands 3.3x combined community demand from
    limited Shield aquifer recharge.

    Roads: ore haul damage scales with GVWR^4 (9,600x car).
    """
    if not mine_active:
        return {
            "power_demand_mw":          0,
            "grid_reserve_margin":      NE_MN_RESERVE_MARGIN,
            "grid_stress_flag":         False,
            "transmission_capex_usd":   0,
            "ratepayer_burden_usd":     0,
            "water_stress_ratio":       COMMUNITY_WATER_DEMAND_M3_DAY / AQUIFER_RECHARGE_M3_DAY,
            "water_conflict_flag":      False,
            "road_maint_annual_usd":    HWY_169_135_ANNUAL_MAINT_USD,
            "ems_response_time_min":    EMS_RESPONSE_TIME_BASE_MIN,
        }

    # Power
    new_peak = NE_MN_CURRENT_PEAK_MW + MINE_POWER_DEMAND_MW * MINE_CAPACITY_FACTOR
    new_reserve_margin = (NE_MN_CURRENT_PEAK_MW * (1 + NE_MN_RESERVE_MARGIN) - new_peak) / new_peak
    grid_stress = new_reserve_margin < 0.10

    transmission_capex = NEW_SUBSTATION_COST_USD + TRANSMISSION_UPGRADE_COST_USD
    ratepayer_burden = transmission_capex * RATEPAYER_SHARE_OF_UPGRADES

    # Water
    total_water_demand = MINE_WATER_DEMAND_M3_DAY + COMMUNITY_WATER_DEMAND_M3_DAY
    water_stress = total_water_demand / AQUIFER_RECHARGE_M3_DAY
    water_conflict = water_stress > WATER_STRESS_THRESHOLD

    # Road damage
    road_maint = HWY_169_135_ANNUAL_MAINT_USD * HWY_DEGRADATION_ACCELERATION

    # Emergency services degraded by mine traffic + spread of responders
    ems_time = EMS_RESPONSE_TIME_BASE_MIN * EMS_DEGRADATION_MULT

    return {
        "power_demand_mw":          MINE_POWER_DEMAND_MW,
        "grid_reserve_margin":      new_reserve_margin,
        "grid_stress_flag":         grid_stress,
        "transmission_capex_usd":   transmission_capex,
        "ratepayer_burden_usd":     ratepayer_burden,
        "water_stress_ratio":       water_stress,
        "water_conflict_flag":      water_conflict,
        "road_maint_annual_usd":    road_maint,
        "ems_response_time_min":    ems_time,
    }
