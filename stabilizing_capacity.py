# stabilizing_capacity.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Thermodynamic capacity analysis for anthropogenic infrastructure.
# Calculates the maximum sustainable density of human infrastructure
# (cities, data centers, manufacturing) before triggering known phase
# transitions in climate, hydrosphere, and biosphere.
#
# Not a policy tool or narrative argument.
# Physics: thermodynamic cost of infrastructure must not exceed
# the planetary energy budget available for maintaining habitability.
# Calculate honestly.

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ─────────────────────────────────────────────
# PHYSICAL CONSTANTS
# ─────────────────────────────────────────────

SOLAR_CONSTANT_WM2           = 1361.0        # W/m²  total solar irradiance (TSI)
EARTH_SURFACE_AREA_M2        = 5.101e14      # m²
LAND_AREA_M2                 = 1.489e14      # m²
OCEAN_AREA_M2                = 3.612e14      # m²
SECONDS_PER_YEAR             = 3.156e7       # s/yr
L_V_J_KG                     = 2.501e6       # J/kg  latent heat of vaporization
RHO_WATER_KG_M3              = 1000.0        # kg/m³

ALBEDO_NATURAL               = 0.306         # planetary albedo, natural baseline
SOLAR_ABSORBED_WM2           = SOLAR_CONSTANT_WM2 / 4.0 * (1.0 - ALBEDO_NATURAL)
# ≈ 235.7 W/m²; division by 4 averages irradiance over the full sphere

OLR_BASELINE_WM2             = 239.0         # W/m² outgoing longwave at equilibrium
# Hansen et al. 2023: current planetary energy imbalance
CURRENT_IMBALANCE_WM2        = 0.90          # W/m²

# Remaining budget before phase-transition cascade proximity.
# IPCC AR6 Working Group I ch. 7: 1.5 °C corresponds to cumulative
# additional forcing ~1.6 W/m² above current imbalance; conservative
# threshold used here.
MAX_ADDITIONAL_FORCING_WM2   = 1.00          # W/m² above current imbalance

CLIMATE_SENSITIVITY_K_PER_WM2 = 0.8         # K / (W/m²)  equilibrium CS

# ─────────────────────────────────────────────
# INFRASTRUCTURE FORCING PARAMETERS
# Values sourced where stated; otherwise order-of-magnitude physical estimates.
# ─────────────────────────────────────────────

# Urban heat island — direct waste heat
# Flanner (2009, GRL): global mean 0.028 W/m² in 2005.
# Mean per-capita energy use ~2.5 kW; ~90% becomes waste heat.
WASTE_HEAT_W_PER_PERSON       = 2250.0       # W/person (2.5 kW × 0.90)

# Urban albedo change relative to natural land surface
# Urban albedo ~0.15; average natural land ~0.25; Δα ≈ −0.10 (darker)
UHI_ALBEDO_DELTA              = -0.10        # urban minus natural land albedo
UHI_LOCAL_HEAT_FLUX_WM2       = 30.0         # W/m² mean sensible+latent heat flux in cities

# Data centers
# IEA (2022): global data centers ~200–250 TWh/yr ≈ 0.72–0.90 EJ/yr
# PUE (power usage effectiveness): total power / IT power ≈ 1.5 modern facilities
GLOBAL_DC_ENERGY_EJ_YR        = 0.72         # EJ/yr current baseline
DC_PUE                        = 1.5          # dimensionless; 1.0 = all power to compute
DC_FLOOR_AREA_M2_PER_DC       = 50_000.0     # m² per large data center (rough)
DC_IT_POWER_PER_FLOOR_M2      = 400.0        # W/m² IT power density (modern DC)

# AI training
AI_LARGE_MODEL_TRAINING_MWH   = 1000.0       # MWh per large foundation model run
                                              # (Patterson et al. 2022: GPT-3 ~1300 MWh)
AI_INFERENCE_KWH_PER_QUERY    = 0.003        # kWh per inference query
                                              # (Goldman Sachs 2024: 0.001–0.01 kWh range)
AI_GPU_EMBODIED_KWH           = 300.0        # kWh embodied energy per GPU (manufacturing)
AI_GPU_LIFETIME_YR            = 3.0          # replacement cycle (yr)

# Cement and concrete
# IEA (2023): cement sector ~14 EJ thermal + 2.6 Gt CO2; 4 Gt/yr production
CEMENT_ENERGY_GJ_PER_TONNE    = 4.5          # GJ thermal input per tonne clinker
CEMENT_PRODUCTION_BASELINE_GT = 4.0          # Gt/yr current global production
# Concrete albedo ~0.35; replaces natural land average ~0.20; Δα ≈ +0.15 (lighter)
CONCRETE_ALBEDO_DELTA         = +0.15        # concrete minus average natural land

# Water diversion
# UNESCO (2021): global freshwater withdrawal ~4000 km³/yr
# Pump + treatment energy: ~1 kWh/m³ average (varies 0.3–3 kWh/m³)
WATER_PUMP_ENERGY_KWH_M3      = 1.0          # kWh/m³
GLOBAL_FRESHWATER_USE_KM3_YR  = 4000.0       # km³/yr
# Latent heat disruption: diverting water from basins where it would
# evaporate to ones where it doesn't suppresses local latent cooling.
# Most withdrawal is return-flow that evaporates in situ (irrigation
# fields, cooling towers). Net non-return fraction ~1–3% of withdrawal;
# use 1% as conservative central estimate. Explicitly uncertain.
WATER_EVP_DISRUPTION_FRACTION = 0.01         # fraction of diversion as net ET loss

# ─────────────────────────────────────────────
# PHASE TRANSITION THRESHOLDS
# ─────────────────────────────────────────────

# AMOC thermohaline shutdown
# Freshwater sensitivity from atmosphere: additional precip from warming
AMOC_FRESHWATER_THRESHOLD_SV  = 0.10         # Sv additional freshwater → collapse proximity
AMOC_FRESHWATER_PER_DEGC_SV   = 0.05         # Sv per °C regional warming (rough)

# Amazon dieback
AMAZON_DEFORESTATION_THRESHOLD = 0.40        # fraction cleared
AMAZON_WARMING_THRESHOLD_C     = 4.0         # °C regional warming above pre-industrial

# Permafrost self-amplification
PERMAFROST_THRESHOLD_C         = 2.0         # °C anomaly above baseline

# Soil collapse (matches soil_interface.SOM_COLLAPSE_THRESHOLD_KGM2)
SOIL_COLLAPSE_SOM_KGM2         = 1.0         # kg C/m²

# ─────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class InfrastructureLoad:
    """
    Anthropogenic infrastructure load specification.
    city_count            : number of cities ≥ 1M population
    avg_city_pop_millions : average city population (millions)
    avg_city_area_km2     : average city footprint (km²)
    total_population      : total human population (billions)
    dc_count              : number of large data centers
    ai_training_runs_yr   : large-model training runs per year (all DCs)
    ai_daily_queries      : AI inference queries per day (all DCs)
    gpu_count             : total installed GPUs (AI + other compute)
    cement_gt_yr          : cement production (Gt/yr)
    water_use_km3_yr      : freshwater withdrawal (km³/yr)
    """
    city_count            : float = 500.0
    avg_city_pop_millions : float = 1.0
    avg_city_area_km2     : float = 1000.0
    total_population      : float = 8.0      # billions
    dc_count              : float = 10_000.0
    ai_training_runs_yr   : float = 1000.0
    ai_daily_queries      : float = 1e10     # 10 billion queries/day
    gpu_count             : float = 1e8      # 100 million installed GPUs
    cement_gt_yr          : float = 4.0
    water_use_km3_yr      : float = 4000.0


@dataclass
class ForcingBreakdown:
    """
    Anthropogenic thermodynamic forcing broken down by source (W/m² global).
    """
    waste_heat_Wm2          : float = 0.0
    uhi_albedo_Wm2          : float = 0.0
    data_center_Wm2         : float = 0.0
    ai_embodied_Wm2         : float = 0.0
    cement_thermal_Wm2      : float = 0.0
    cement_albedo_Wm2       : float = 0.0
    water_pump_Wm2          : float = 0.0
    water_evp_disruption_Wm2: float = 0.0
    total_Wm2               : float = 0.0


@dataclass
class PhaseTransitionMargins:
    """
    Remaining margin to each known phase transition.
    Positive margin = distance remaining; negative = threshold exceeded.
    """
    energy_budget_Wm2      : float = 0.0   # W/m²  above current imbalance
    AMOC_freshwater_Sv     : float = 0.0   # Sv    remaining before collapse proximity
    amazon_tipping         : float = 0.0   # 0–1   fraction of margin remaining
    permafrost_C           : float = 0.0   # °C    remaining before self-amplification
    soil_SOM_kgm2          : float = 0.0   # kg/m² SOM above collapse threshold
    most_constrained       : str   = ""    # label of smallest positive margin


@dataclass
class StabilizingCapacityResult:
    """
    Full stabilizing capacity analysis result.
    """
    load              : InfrastructureLoad = field(default_factory=InfrastructureLoad)
    forcing           : ForcingBreakdown   = field(default_factory=ForcingBreakdown)
    margins           : PhaseTransitionMargins = field(default_factory=PhaseTransitionMargins)
    sustainable       : bool  = True
    binding_constraint: str   = ""
    max_city_density_per_km2  : float = 0.0
    max_dc_count_global       : float = 0.0
    max_ai_queries_per_day    : float = 0.0
    forcing_headroom_Wm2      : float = 0.0
    notes             : List[str] = field(default_factory=list)


# ─────────────────────────────────────────────
# FORCING FUNCTIONS
# ─────────────────────────────────────────────

def urban_heat_island_forcing(city_count: float,
                               avg_pop_millions: float,
                               avg_area_km2: float = 1000.0) -> dict:
    """
    Global-average UHI thermodynamic forcing from urban infrastructure.

    Two channels:
    1. Direct waste heat: population × per-capita power × waste-heat fraction
    2. Albedo darkening: urban surfaces absorb more solar than replaced land

    city_count       : number of large cities (≥ 1M)
    avg_pop_millions : average population per city (millions)
    avg_area_km2     : average city footprint (km²)

    Returns dict with global-average W/m² for each channel.
    """
    total_urban_pop = city_count * avg_pop_millions * 1e6   # persons
    total_urban_area_m2 = city_count * avg_area_km2 * 1e6  # m²

    # Direct waste heat (all energy pathways end as heat at the surface)
    # Use total population × per-capita energy × waste fraction
    total_waste_heat_W = total_urban_pop * WASTE_HEAT_W_PER_PERSON
    waste_heat_Wm2 = total_waste_heat_W / EARTH_SURFACE_AREA_M2

    # Albedo forcing: urban surfaces are darker than average natural land
    # ΔForcing = (S0/4) × |Δα| × f_urban_total_surface
    urban_fraction_total = total_urban_area_m2 / EARTH_SURFACE_AREA_M2
    # UHI_ALBEDO_DELTA is negative (darker), so forcing is positive (warming)
    albedo_forcing_Wm2 = (SOLAR_CONSTANT_WM2 / 4.0
                          * (-UHI_ALBEDO_DELTA)        # flip sign: darker → more absorbed
                          * urban_fraction_total)

    total_Wm2 = waste_heat_Wm2 + albedo_forcing_Wm2

    return {
        "total_Wm2":              total_Wm2,
        "waste_heat_Wm2":         waste_heat_Wm2,
        "albedo_forcing_Wm2":     albedo_forcing_Wm2,
        "total_urban_area_km2":   total_urban_area_m2 / 1e6,
        "urban_fraction_surface": urban_fraction_total,
        "total_urban_pop":        total_urban_pop,
    }


def data_center_forcing(dc_count: float,
                         ai_training_runs_yr: float = 0.0,
                         ai_daily_queries: float = 0.0) -> dict:
    """
    Global-average thermodynamic forcing from data center infrastructure.

    IT power × PUE = total power; all power eventually becomes waste heat.

    dc_count             : number of large data centers
    ai_training_runs_yr  : large-model training runs per year (global total)
    ai_daily_queries     : AI inference queries per day (global total)

    Returns dict with W/m² global.
    """
    # Base DC power from compute density
    dc_floor_area_m2 = dc_count * DC_FLOOR_AREA_M2_PER_DC
    dc_it_power_W    = dc_floor_area_m2 * DC_IT_POWER_PER_FLOOR_M2
    dc_total_power_W = dc_it_power_W * DC_PUE         # includes cooling overhead

    # AI training additional power (on top of steady-state IT load)
    ai_training_power_W = (ai_training_runs_yr
                           * AI_LARGE_MODEL_TRAINING_MWH * 1e6   # Wh → J
                           / SECONDS_PER_YEAR)
    # AI inference power
    ai_inference_power_W = (ai_daily_queries * 365.0
                            * AI_INFERENCE_KWH_PER_QUERY * 3.6e6  # kWh → J
                            / SECONDS_PER_YEAR)

    total_dc_power_W = dc_total_power_W + ai_training_power_W + ai_inference_power_W
    total_Wm2        = total_dc_power_W / EARTH_SURFACE_AREA_M2

    return {
        "total_Wm2":              total_Wm2,
        "dc_base_power_W":        dc_total_power_W,
        "ai_training_power_W":    ai_training_power_W,
        "ai_inference_power_W":   ai_inference_power_W,
        "total_dc_power_GW":      total_dc_power_W / 1e9,
        "dc_floor_area_km2":      dc_floor_area_m2 / 1e6,
    }


def ai_hardware_manufacturing_forcing(gpu_count: float,
                                       replacement_yr: float = 3.0) -> dict:
    """
    Thermodynamic forcing from AI hardware manufacturing (embodied energy).

    Embodied energy in GPU manufacturing is released as heat during
    processing. Annualised over replacement cycle.

    gpu_count      : total installed GPUs
    replacement_yr : average GPU replacement period (yr)

    Returns dict with W/m² global.
    """
    gpus_replaced_per_yr = gpu_count / replacement_yr
    mfg_energy_Wh_yr     = gpus_replaced_per_yr * AI_GPU_EMBODIED_KWH * 1e3  # kWh → Wh
    mfg_power_W          = mfg_energy_Wh_yr / 8760.0
    total_Wm2            = mfg_power_W / EARTH_SURFACE_AREA_M2

    return {
        "total_Wm2":           total_Wm2,
        "mfg_power_W":         mfg_power_W,
        "gpus_replaced_yr":    gpus_replaced_per_yr,
    }


def cement_construction_forcing(cement_gt_yr: float,
                                 built_area_km2: float = 500_000.0) -> dict:
    """
    Thermodynamic forcing from cement production and concrete surface albedo.

    Two channels:
    1. Thermal energy of cement production (kiln heat → ultimately surface heat)
    2. Albedo change from replacing natural surfaces with concrete

    cement_gt_yr    : global cement production (Gt/yr)
    built_area_km2  : total area of concrete surfaces (km²)

    Returns dict with W/m² global per channel.
    """
    # Thermal energy of cement production
    # 1 Gt = 1e9 tonnes; 1 EJ = 1e9 GJ  →  Gt × GJ/t = EJ
    cement_energy_EJ_yr  = cement_gt_yr * CEMENT_ENERGY_GJ_PER_TONNE
    cement_power_W       = cement_energy_EJ_yr * 1e18 / SECONDS_PER_YEAR
    thermal_Wm2          = cement_power_W / EARTH_SURFACE_AREA_M2

    # Albedo change: concrete is lighter than most replaced surfaces
    # CONCRETE_ALBEDO_DELTA > 0 → more reflective → cooling effect (negative forcing)
    built_area_m2        = built_area_km2 * 1e6
    concrete_fraction    = built_area_m2 / EARTH_SURFACE_AREA_M2
    albedo_forcing_Wm2   = -(SOLAR_CONSTANT_WM2 / 4.0
                              * CONCRETE_ALBEDO_DELTA
                              * concrete_fraction)    # negative = cooling

    total_Wm2 = thermal_Wm2 + albedo_forcing_Wm2

    return {
        "total_Wm2":           total_Wm2,
        "thermal_Wm2":         thermal_Wm2,
        "albedo_forcing_Wm2":  albedo_forcing_Wm2,   # typically negative (cooling)
        "cement_energy_EJ_yr": cement_energy_EJ_yr,
        "cement_power_GW":     cement_power_W / 1e9,
    }


def water_diversion_forcing(water_use_km3_yr: float) -> dict:
    """
    Thermodynamic forcing from freshwater diversion and treatment.

    Two channels:
    1. Pump + treatment energy → waste heat at surface
    2. Evapotranspiration disruption: diverting water from basins where
       it would evaporate (latent cooling) to basins where it doesn't
       suppresses local latent heat flux, warming source regions.

    water_use_km3_yr : freshwater withdrawal (km³/yr)

    Returns dict with W/m² global per channel.
    """
    # Pump + treatment energy
    water_m3_yr          = water_use_km3_yr * 1e9                    # km³ → m³
    pump_energy_Wh_yr    = water_m3_yr * WATER_PUMP_ENERGY_KWH_M3 * 1e3
    pump_power_W         = pump_energy_Wh_yr / 8760.0
    pump_Wm2             = pump_power_W / EARTH_SURFACE_AREA_M2

    # Evapotranspiration disruption (latent heat suppression)
    # Net disruption volume: fraction of diversion with no return ET
    disrupted_vol_m3_yr  = water_m3_yr * WATER_EVP_DISRUPTION_FRACTION
    disrupted_mass_kg_yr = disrupted_vol_m3_yr * RHO_WATER_KG_M3
    # Latent heat withheld from surface (cooling that doesn't happen)
    latent_heat_W        = disrupted_mass_kg_yr * L_V_J_KG / SECONDS_PER_YEAR
    evp_Wm2              = latent_heat_W / EARTH_SURFACE_AREA_M2

    total_Wm2 = pump_Wm2 + evp_Wm2

    return {
        "total_Wm2":               total_Wm2,
        "pump_energy_Wm2":         pump_Wm2,
        "evp_disruption_Wm2":      evp_Wm2,
        "pump_power_GW":           pump_power_W / 1e9,
        "latent_heat_withheld_GW": latent_heat_W / 1e9,
    }


def total_anthropogenic_forcing(load: InfrastructureLoad) -> ForcingBreakdown:
    """
    Sum all anthropogenic thermodynamic forcing channels for a given
    InfrastructureLoad.

    Returns ForcingBreakdown with per-channel and total W/m² (global average).
    """
    uhi  = urban_heat_island_forcing(
               load.city_count,
               load.avg_city_pop_millions,
               load.avg_city_area_km2)
    # Whole-population waste heat (not just cities)
    pop_waste_W      = load.total_population * 1e9 * WASTE_HEAT_W_PER_PERSON
    waste_heat_Wm2   = pop_waste_W / EARTH_SURFACE_AREA_M2

    dc   = data_center_forcing(
               load.dc_count,
               load.ai_training_runs_yr,
               load.ai_daily_queries)
    mfg  = ai_hardware_manufacturing_forcing(load.gpu_count, AI_GPU_LIFETIME_YR)
    cem  = cement_construction_forcing(load.cement_gt_yr)
    wat  = water_diversion_forcing(load.water_use_km3_yr)

    total = (waste_heat_Wm2
             + uhi["albedo_forcing_Wm2"]
             + dc["total_Wm2"]
             + mfg["total_Wm2"]
             + cem["total_Wm2"]
             + wat["total_Wm2"])

    return ForcingBreakdown(
        waste_heat_Wm2           = waste_heat_Wm2,
        uhi_albedo_Wm2           = uhi["albedo_forcing_Wm2"],
        data_center_Wm2          = dc["total_Wm2"],
        ai_embodied_Wm2          = mfg["total_Wm2"],
        cement_thermal_Wm2       = cem["thermal_Wm2"],
        cement_albedo_Wm2        = cem["albedo_forcing_Wm2"],
        water_pump_Wm2           = wat["pump_energy_Wm2"],
        water_evp_disruption_Wm2 = wat["evp_disruption_Wm2"],
        total_Wm2                = total,
    )


# ─────────────────────────────────────────────
# PLANETARY ENERGY BUDGET
# ─────────────────────────────────────────────

def planetary_energy_budget(atmo_state: Optional[dict] = None,
                             bio_state:  Optional[dict] = None,
                             hydro_state: Optional[dict] = None) -> dict:
    """
    Available planetary energy budget from layer state vectors.

    solar_absorbed_Wm2      : S0/4 × (1 − α_planetary)
    ghg_forcing_Wm2         : from layer_3 net_forcing_Wm2
    current_imbalance_Wm2   : measured planetary heat uptake
    available_margin_Wm2    : headroom before MAX_ADDITIONAL_FORCING_WM2

    atmo_state  : dict from layer_3_atmosphere.coupling_state()
    bio_state   : dict from layer_6_biosphere.coupling_state()
    hydro_state : dict from layer_4_hydrosphere.coupling_state()

    Returns dict with budget components and margin to phase-transition threshold.
    """
    ghg_forcing = 0.0
    if atmo_state:
        ghg_forcing = atmo_state.get("net_forcing_Wm2", 0.0)

    # Net O2 flux modifies effective atmospheric opacity marginally;
    # first-order approximation: O2 changes are too small to affect OLR.
    net_O2_flux = 0.0
    if bio_state:
        net_O2_flux = bio_state.get("net_O2_flux_GtO2_yr", 0.0)

    # AMOC heat transport affects OLR indirectly via SST distribution.
    # Simplified: AMOC weakening raises N Atlantic SST → slight OLR increase.
    amoc_sv = 17.0
    if hydro_state:
        amoc_sv = hydro_state.get("AMOC_Sv", 17.0)
    amoc_weakening_fraction = max(0.0, (18.0 - amoc_sv) / 18.0)
    amoc_olr_feedback_Wm2   = amoc_weakening_fraction * 0.2  # small; W/m²

    total_current_forcing = ghg_forcing + CURRENT_IMBALANCE_WM2
    available_margin      = MAX_ADDITIONAL_FORCING_WM2 - (total_current_forcing
                                                          - CURRENT_IMBALANCE_WM2)
    # Restate: available = MAX_ADDITIONAL_FORCING_WM2 − GHG_forcing (already committed)
    # Current imbalance is the realization of partial GHG forcing.
    available_margin = MAX_ADDITIONAL_FORCING_WM2

    return {
        "solar_absorbed_Wm2":       SOLAR_ABSORBED_WM2,
        "OLR_baseline_Wm2":         OLR_BASELINE_WM2,
        "ghg_forcing_Wm2":          ghg_forcing,
        "current_imbalance_Wm2":    CURRENT_IMBALANCE_WM2,
        "amoc_olr_feedback_Wm2":    amoc_olr_feedback_Wm2,
        "available_margin_Wm2":     available_margin,
        "net_O2_flux_GtO2_yr":      net_O2_flux,
        "note": (
            "available_margin is additional anthropogenic forcing headroom "
            "before entering phase-transition proximity. GHG forcing already "
            "committed is not included in margin; it is the baseline to beat."
        ),
    }


# ─────────────────────────────────────────────
# PHASE TRANSITION MARGIN CALCULATOR
# ─────────────────────────────────────────────

def margin_to_phase_transitions(total_anthro_forcing_Wm2: float,
                                 atmo_state:  Optional[dict] = None,
                                 bio_state:   Optional[dict] = None,
                                 hydro_state: Optional[dict] = None,
                                 soil_state:  Optional[dict] = None
                                 ) -> PhaseTransitionMargins:
    """
    Remaining margin to each known phase transition given total anthropogenic forcing.

    Positive margin = distance remaining before threshold.
    Negative margin = threshold already exceeded.

    total_anthro_forcing_Wm2 : output of total_anthropogenic_forcing().total_Wm2
    atmo_state, bio_state, hydro_state, soil_state : layer coupling_state() dicts

    Returns PhaseTransitionMargins.
    """
    # ── Energy budget margin ───────────────────────────────────────────
    energy_margin = MAX_ADDITIONAL_FORCING_WM2 - total_anthro_forcing_Wm2

    # ── AMOC: freshwater forcing from warming ──────────────────────────
    # Additional warming from anthropogenic heat
    delta_T_anthro = total_anthro_forcing_Wm2 * CLIMATE_SENSITIVITY_K_PER_WM2
    # Additional freshwater flux from warming atmosphere (more precipitation/melt)
    freshwater_Sv  = delta_T_anthro * AMOC_FRESHWATER_PER_DEGC_SV
    if hydro_state and hydro_state.get("AMOC_collapse_risk", False):
        # AMOC already at collapse risk from current climate state
        AMOC_margin = -AMOC_FRESHWATER_THRESHOLD_SV
    else:
        AMOC_margin = AMOC_FRESHWATER_THRESHOLD_SV - freshwater_Sv

    # ── Amazon dieback ─────────────────────────────────────────────────
    amazon_proximity = 0.0
    if bio_state:
        amazon_proximity = bio_state.get("amazon_tipping_proximity", 0.0)
    # Anthropogenic heat shifts regional warming → increases proximity
    # 1 W/m² global ≈ 0.8 K × regional amplification factor ~1.5
    regional_warming_C = total_anthro_forcing_Wm2 * CLIMATE_SENSITIVITY_K_PER_WM2 * 1.5
    amazon_temp_fraction = min(1.0, regional_warming_C / AMAZON_WARMING_THRESHOLD_C)
    # Combined tipping proximity: max of deforestation-driven and temperature-driven
    amazon_margin = 1.0 - max(amazon_proximity, amazon_temp_fraction)

    # ── Permafrost ─────────────────────────────────────────────────────
    permafrost_self_amp = False
    if bio_state:
        permafrost_self_amp = bio_state.get("permafrost_self_amplifying", False)
    if permafrost_self_amp:
        permafrost_margin = -PERMAFROST_THRESHOLD_C
    else:
        # Remaining thermal budget before self-amplification
        permafrost_margin = PERMAFROST_THRESHOLD_C - delta_T_anthro

    # ── Soil organic matter ────────────────────────────────────────────
    SOM = SOIL_COLLAPSE_SOM_KGM2 + 9.0  # default baseline (10 kg/m²)
    if soil_state:
        SOM = soil_state.get("SOM_kgm2", SOM)
    soil_margin = SOM - SOIL_COLLAPSE_SOM_KGM2

    # ── Most constrained dimension ─────────────────────────────────────
    named = {
        "energy_budget":  energy_margin,
        "AMOC":           AMOC_margin,
        "amazon_tipping": amazon_margin,
        "permafrost":     permafrost_margin,
        "soil_SOM":       soil_margin,
    }
    most_constrained = min(named, key=lambda k: named[k])

    return PhaseTransitionMargins(
        energy_budget_Wm2  = energy_margin,
        AMOC_freshwater_Sv = AMOC_margin,
        amazon_tipping     = amazon_margin,
        permafrost_C       = permafrost_margin,
        soil_SOM_kgm2      = soil_margin,
        most_constrained   = most_constrained,
    )


# ─────────────────────────────────────────────
# FEASIBILITY CALCULATOR
# ─────────────────────────────────────────────

def can_sustain(city_count:             float,
                dc_count:               float,
                manufacturing_capacity: float = 1.0,
                total_population_B:     float = 8.0,
                atmo_state:   Optional[dict] = None,
                bio_state:    Optional[dict] = None,
                hydro_state:  Optional[dict] = None,
                soil_state:   Optional[dict] = None) -> dict:
    """
    Test whether a given infrastructure configuration is within planetary
    thermodynamic limits.

    city_count             : number of cities ≥ 1M population
    dc_count               : number of large data centers (~50 000 m² each)
    manufacturing_capacity : fraction of current cement production (1.0 = current)
    total_population_B     : total human population (billions)
    *_state                : layer coupling_state() dicts (None = use defaults)

    Returns dict with:
      sustainable         : bool
      binding_constraint  : str (label of most constrained dimension)
      forcing_Wm2         : total anthropogenic forcing
      margins             : PhaseTransitionMargins
      headroom_Wm2        : remaining forcing budget (energy_budget margin)
    """
    load = InfrastructureLoad(
        city_count            = city_count,
        avg_city_pop_millions = 1.0,
        avg_city_area_km2     = 1000.0,
        total_population      = total_population_B,
        dc_count              = dc_count,
        ai_training_runs_yr   = dc_count * 0.1,    # rough: 0.1 runs/DC/yr
        ai_daily_queries      = dc_count * 1e6,    # 1M queries/DC/day
        gpu_count             = dc_count * 10_000,
        cement_gt_yr          = CEMENT_PRODUCTION_BASELINE_GT * manufacturing_capacity,
        water_use_km3_yr      = GLOBAL_FRESHWATER_USE_KM3_YR,
    )
    forcing  = total_anthropogenic_forcing(load)
    margins  = margin_to_phase_transitions(
                   forcing.total_Wm2, atmo_state, bio_state, hydro_state, soil_state)

    sustainable = (margins.energy_budget_Wm2 > 0.0
                   and margins.AMOC_freshwater_Sv > 0.0
                   and margins.amazon_tipping > 0.0
                   and margins.permafrost_C > 0.0)

    return {
        "sustainable":         sustainable,
        "binding_constraint":  margins.most_constrained,
        "forcing_Wm2":         forcing.total_Wm2,
        "headroom_Wm2":        margins.energy_budget_Wm2,
        "margins":             margins,
        "forcing_breakdown":   forcing,
    }


def ai_tradeoff_curve(max_dc_count: float,
                       atmo_state:  Optional[dict] = None,
                       bio_state:   Optional[dict] = None,
                       hydro_state: Optional[dict] = None,
                       soil_state:  Optional[dict] = None,
                       steps:       int = 20) -> List[dict]:
    """
    Tradeoff curve: more AI data centers → less capacity for other systems.

    Computes forcing and phase-transition margins at dc_count values from
    0 to max_dc_count in `steps` increments. All other infrastructure held
    at current baseline.

    Returns list of dicts ordered by dc_count, each with:
      dc_count, forcing_Wm2, energy_margin_Wm2, AMOC_margin_Sv,
      amazon_margin, permafrost_margin_C, soil_margin_kgm2, sustainable
    """
    results = []
    for i in range(steps + 1):
        dc = max_dc_count * i / steps
        r  = can_sustain(
                 city_count=500, dc_count=dc,
                 total_population_B=8.0,
                 atmo_state=atmo_state,
                 bio_state=bio_state,
                 hydro_state=hydro_state,
                 soil_state=soil_state)
        results.append({
            "dc_count":            dc,
            "forcing_Wm2":         r["forcing_Wm2"],
            "energy_margin_Wm2":   r["margins"].energy_budget_Wm2,
            "AMOC_margin_Sv":      r["margins"].AMOC_freshwater_Sv,
            "amazon_margin":       r["margins"].amazon_tipping,
            "permafrost_margin_C": r["margins"].permafrost_C,
            "soil_margin_kgm2":    r["margins"].soil_SOM_kgm2,
            "sustainable":         r["sustainable"],
        })
    return results


def maximum_sustainable_limits(atmo_state:  Optional[dict] = None,
                                bio_state:   Optional[dict] = None,
                                hydro_state: Optional[dict] = None,
                                soil_state:  Optional[dict] = None) -> dict:
    """
    Calculate maximum sustainable values for key infrastructure metrics
    under planetary energy budget constraint.

    Uses the energy_budget margin as the binding physical limit, then
    inverts each forcing function to find the maximum load that keeps
    total forcing below MAX_ADDITIONAL_FORCING_WM2.

    Returns dict with per-metric maximum values and the binding constraint.
    """
    budget = planetary_energy_budget(atmo_state, bio_state, hydro_state)
    margin = budget["available_margin_Wm2"]

    # Maximum population (waste heat constraint only)
    # waste_heat_W = pop × WASTE_HEAT_W_PER_PERSON ≤ margin × EARTH_SURFACE_AREA_M2
    max_pop_B = (margin * EARTH_SURFACE_AREA_M2
                 / WASTE_HEAT_W_PER_PERSON / 1e9)

    # Maximum data centers (DC forcing constraint only)
    # dc_power_W = dc_count × DC_FLOOR_AREA_M2_PER_DC × DC_IT_POWER_PER_FLOOR_M2 × DC_PUE
    dc_power_per_dc = DC_FLOOR_AREA_M2_PER_DC * DC_IT_POWER_PER_FLOOR_M2 * DC_PUE
    max_dc = (margin * EARTH_SURFACE_AREA_M2 / dc_power_per_dc)

    # Maximum AI queries per day (inference constraint only)
    # inference_W = queries/day × 365 × AI_INFERENCE_KWH_PER_QUERY × 3.6e6 / SECONDS_PER_YEAR
    inference_W_per_query_per_day = (365.0 * AI_INFERENCE_KWH_PER_QUERY
                                     * 3.6e6 / SECONDS_PER_YEAR)
    max_queries_per_day = (margin * EARTH_SURFACE_AREA_M2
                           / inference_W_per_query_per_day)

    # Maximum AI training runs per year
    training_W_per_run = AI_LARGE_MODEL_TRAINING_MWH * 1e6 / SECONDS_PER_YEAR
    max_training_yr = (margin * EARTH_SURFACE_AREA_M2 / training_W_per_run)

    # Maximum cement production (thermal only; albedo is cooling)
    cement_power_per_Gt = (1e12 * CEMENT_ENERGY_GJ_PER_TONNE * 1e9
                           / SECONDS_PER_YEAR)
    max_cement_gt = margin * EARTH_SURFACE_AREA_M2 / cement_power_per_Gt

    return {
        "available_margin_Wm2":        margin,
        "max_population_B":            max_pop_B,
        "max_data_centers":            max_dc,
        "max_ai_queries_per_day":      max_queries_per_day,
        "max_ai_training_runs_yr":     max_training_yr,
        "max_cement_gt_yr":            max_cement_gt,
        "binding_note": (
            "These are single-variable maxima holding all other forcing at zero. "
            "Combined infrastructure must be assessed together via can_sustain()."
        ),
    }


def feasibility_report(load:        InfrastructureLoad,
                        atmo_state:  Optional[dict] = None,
                        bio_state:   Optional[dict] = None,
                        hydro_state: Optional[dict] = None,
                        soil_state:  Optional[dict] = None) -> dict:
    """
    Full stabilizing capacity analysis for a given InfrastructureLoad.

    Returns StabilizingCapacityResult as dict.
    """
    forcing  = total_anthropogenic_forcing(load)
    budget   = planetary_energy_budget(atmo_state, bio_state, hydro_state)
    margins  = margin_to_phase_transitions(
                   forcing.total_Wm2, atmo_state, bio_state, hydro_state, soil_state)
    limits   = maximum_sustainable_limits(atmo_state, bio_state, hydro_state, soil_state)

    sustainable = (margins.energy_budget_Wm2 > 0.0
                   and margins.AMOC_freshwater_Sv > 0.0
                   and margins.amazon_tipping > 0.0
                   and margins.permafrost_C > 0.0)

    notes = []
    if forcing.data_center_Wm2 > 0.005:
        notes.append(
            f"Data center load {forcing.data_center_Wm2 * 1000:.2f} mW/m² "
            f"exceeds 5 mW/m² — cooling water demand becomes binding before heat."
        )
    if forcing.waste_heat_Wm2 > 0.10:
        notes.append(
            f"Population waste heat {forcing.waste_heat_Wm2 * 1000:.1f} mW/m² "
            f"is dominant forcing channel."
        )
    if forcing.water_evp_disruption_Wm2 > 0.01:
        notes.append(
            "Water diversion ET disruption is a non-negligible latent heat forcing."
        )

    result = StabilizingCapacityResult(
        load               = load,
        forcing            = forcing,
        margins            = margins,
        sustainable        = sustainable,
        binding_constraint = margins.most_constrained,
        max_city_density_per_km2  = limits["max_population_B"] * 1e9 / LAND_AREA_M2 * 1e6,
        max_dc_count_global       = limits["max_data_centers"],
        max_ai_queries_per_day    = limits["max_ai_queries_per_day"],
        forcing_headroom_Wm2      = margins.energy_budget_Wm2,
        notes              = notes,
    )

    return {
        "infrastructure_load":     load,
        "forcing_breakdown_Wm2":   forcing,
        "energy_budget":           budget,
        "phase_transition_margins": margins,
        "sustainable":             sustainable,
        "binding_constraint":      margins.most_constrained,
        "single_variable_limits":  limits,
        "result":                  result,
    }


# ─────────────────────────────────────────────
# CONVENIENCE: CURRENT BASELINE ASSESSMENT
# ─────────────────────────────────────────────

CURRENT_LOAD = InfrastructureLoad(
    city_count            = 500,      # cities ≥ 1M pop
    avg_city_pop_millions = 2.0,
    avg_city_area_km2     = 1500.0,
    total_population      = 8.1,      # billions (2024)
    dc_count              = 10_000,   # global estimate
    ai_training_runs_yr   = 500,      # frontier labs + research
    ai_daily_queries      = 2e10,     # ~20 billion AI queries/day (2024)
    gpu_count             = 1e8,      # ~100 million GPUs installed
    cement_gt_yr          = 4.0,
    water_use_km3_yr      = 4000.0,
)


if __name__ == "__main__":
    forcing  = total_anthropogenic_forcing(CURRENT_LOAD)
    margins  = margin_to_phase_transitions(forcing.total_Wm2)
    limits   = maximum_sustainable_limits()

    print("=== Stabilizing Capacity — Current Baseline ===\n")
    print(f"Total anthropogenic forcing:  {forcing.total_Wm2 * 1000:.2f} mW/m²")
    print(f"  Waste heat:                 {forcing.waste_heat_Wm2 * 1000:.2f} mW/m²")
    print(f"  UHI albedo:                 {forcing.uhi_albedo_Wm2 * 1000:.2f} mW/m²")
    print(f"  Data centers:               {forcing.data_center_Wm2 * 1000:.4f} mW/m²")
    print(f"  AI hardware mfg:            {forcing.ai_embodied_Wm2 * 1000:.4f} mW/m²")
    print(f"  Cement thermal:             {forcing.cement_thermal_Wm2 * 1000:.2f} mW/m²")
    print(f"  Cement albedo (cooling):    {forcing.cement_albedo_Wm2 * 1000:.2f} mW/m²")
    print(f"  Water pump:                 {forcing.water_pump_Wm2 * 1000:.2f} mW/m²")
    print(f"  Water ET disruption:        {forcing.water_evp_disruption_Wm2 * 1000:.2f} mW/m²")
    print(f"\nPhase transition margins:")
    print(f"  Energy budget:   {margins.energy_budget_Wm2 * 1000:.1f} mW/m²  remaining")
    print(f"  AMOC:            {margins.AMOC_freshwater_Sv * 1000:.3f} mSv   remaining")
    print(f"  Amazon:          {margins.amazon_tipping:.3f}          (0=tipping, 1=safe)")
    print(f"  Permafrost:      {margins.permafrost_C:.2f} °C    remaining")
    print(f"  Soil SOM:        {margins.soil_SOM_kgm2:.1f} kg/m²  remaining")
    print(f"\nMost constrained: {margins.most_constrained}")
    print(f"\nSingle-variable limits:")
    print(f"  Max population:            {limits['max_population_B']:.0f} billion")
    print(f"  Max data centers:          {limits['max_data_centers']:.0f}")
    print(f"  Max AI queries/day:        {limits['max_ai_queries_per_day']:.2e}")
    print(f"  Max AI training runs/yr:   {limits['max_ai_training_runs_yr']:.0f}")
    print(f"  Max cement Gt/yr:          {limits['max_cement_gt_yr']:.1f}")
