# layer_6_biosphere.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Biosphere constraint layer.
# Governs energy flows through living systems, biogeochemical cycling,
# feedback loops between life and physical Earth systems,
# and threshold behaviors in ecological state transitions.
# Life is not separate from Earth physics — it is a coupled subsystem
# that actively modifies every layer below it.
# Imports constraints from layers 0-5.

import numpy as np
from scipy.constants import k, R
from layer_3_atmosphere import (
    saturation_vapor_pressure,
    greenhouse_forcing,
    stefan_boltzmann_flux,
)
from layer_4_hydrosphere import (
    seawater_density,
    ocean_heat_content,
    evaporation_rate,
)
from layer_5_lithosphere import (
    deglaciation_volcanic_coupling,
    tectonic_co2_outgassing,
)

# ─────────────────────────────────────────────
# FUNDAMENTAL CONSTANTS — BIOSPHERE
# ─────────────────────────────────────────────

E_activation_photosyn = 0.32    # eV — activation energy photosynthesis
E_activation_respir   = 0.65    # eV — activation energy respiration
Q10_respiration       = 2.0     # respiration rate doubles per 10°C
Q10_photosynthesis    = 1.4     # photosynthesis less temperature sensitive
k_eV                  = 8.617e-5 # eV/K Boltzmann in eV
PAR_fraction          = 0.45    # fraction of solar radiation photosynthetically active
max_photosyn_eff      = 0.11    # theoretical max photosynthetic efficiency
typical_photosyn_eff  = 0.02    # realized global mean ~2%

# ─────────────────────────────────────────────
# PRIMARY PRODUCTIVITY
# ─────────────────────────────────────────────

def gross_primary_productivity(PAR_Wm2, T_K, CO2_ppm, water_stress=1.0):
    """
    Gross primary productivity — carbon fixed by photosynthesis.
    Arrhenius temperature dependence — peaks then crashes above optimum.
    PAR_Wm2      : photosynthetically active radiation (W/m^2)
    T_K          : temperature (K)
    CO2_ppm      : atmospheric CO2 concentration
    water_stress : 0-1, 1=no stress
    returns: GPP (g C / m^2 / day)
    """
    T_opt = 298.0  # K — approximate optimum
    T_max = 318.0  # K — ~45°C upper limit for most vegetation

    if T_K >= T_max:
        return 0.0

    # Arrhenius scaling
    temp_factor = np.exp(-E_activation_photosyn / (k_eV * T_K)) * \
                  np.exp( E_activation_photosyn / (k_eV * T_opt))

    # CO2 fertilization — logarithmic saturation
    co2_factor = np.log(CO2_ppm / 280.0) / np.log(2.0) * 0.3 + 1.0

    # Light use efficiency
    LUE = typical_photosyn_eff * temp_factor * co2_factor * water_stress

    # Convert W/m^2 to mol photons/m^2/day
    mol_photons = PAR_Wm2 * 86400 / (2.0e5)  # rough conversion
    gC_per_mol  = 12.0 * 0.5  # ~0.5 mol C per mol photons typical
    return LUE * mol_photons * gC_per_mol


def ecosystem_respiration(GPP, T_K, T_ref_K=283.0):
    """
    Total ecosystem respiration — carbon released back to atmosphere.
    More temperature sensitive than photosynthesis (higher Q10).
    At sufficient warming: respiration exceeds GPP — ecosystem becomes
    carbon source instead of sink. Hard threshold.
    GPP    : gross primary productivity (g C/m^2/day)
    T_K    : temperature (K)
    T_ref_K: reference temperature
    returns: respiration rate (g C/m^2/day)
    """
    delta_T = T_K - T_ref_K
    R_factor = Q10_respiration ** (delta_T / 10.0)
    # Respiration typically ~50-70% of GPP at reference temperature
    return 0.60 * GPP * R_factor


def net_ecosystem_productivity(GPP, T_K, T_ref_K=283.0):
    """
    NEP = GPP - Respiration
    Positive: ecosystem is carbon sink
    Negative: ecosystem is carbon source
    Sign change is a critical threshold — warming can flip large
    carbon sinks to sources with no mechanism to reverse quickly.
    """
    R_eco = ecosystem_respiration(GPP, T_K, T_ref_K)
    NEP   = GPP - R_eco
    return {
        "NEP_gC_m2_day":  NEP,
        "carbon_sink":    NEP > 0,
        "carbon_source":  NEP < 0,
        "respiration_GPP_ratio": R_eco / GPP if GPP > 0 else np.inf,
        "threshold_warning": NEP < 0,
    }


# ─────────────────────────────────────────────
# SOIL CARBON
# ─────────────────────────────────────────────

def soil_carbon_decomposition(C_soil, T_K, moisture=0.6):
    """
    Soil carbon decomposition rate — microbial respiration.
    Soil contains ~2x more carbon than atmosphere.
    Permafrost holds ~1.5 trillion tonnes — currently frozen.
    T_K      : soil temperature (K)
    moisture : volumetric soil moisture (0-1), optimum ~0.6
    C_soil   : soil carbon stock (kg C/m^2)
    returns: decomposition rate (kg C/m^2/year)
    """
    T_C = T_K - 273.15
    # Optimal moisture function — too dry or too wet slows decomposition
    moisture_factor = moisture * (1 - moisture) * 4.0
    # Temperature function
    temp_factor = Q10_respiration ** (T_C / 10.0)
    k_decomp = 0.03  # year^-1 base rate
    return k_decomp * C_soil * temp_factor * moisture_factor


def permafrost_thaw_carbon_flux(permafrost_area_m2, T_anomaly_K,
                                 C_density_kgm2=60.0):
    """
    Carbon release from permafrost thaw.
    ~1.5e12 tonnes C in permafrost globally.
    Releases as CO2 (aerobic) and CH4 (anaerobic — 28x more potent).
    Nonlinear: slow at first, accelerates as active layer deepens.
    This is the largest potential self-amplifying feedback in the system.
    permafrost_area_m2 : area of thawing permafrost
    T_anomaly_K        : warming above permafrost stability threshold
    C_density_kgm2     : carbon density of permafrost soil
    returns: annual carbon flux (Gt C/year) and CH4 fraction
    """
    if T_anomaly_K <= 0:
        return {"CO2_flux_GtC_yr": 0.0, "CH4_flux_GtC_yr": 0.0,
                "total_GtC_yr": 0.0, "note": "permafrost stable"}

    thaw_depth_m  = 0.1 * T_anomaly_K ** 1.5   # nonlinear thaw depth
    active_volume = permafrost_area_m2 * thaw_depth_m
    C_available   = active_volume * C_density_kgm2 / 1e12  # Gt C

    # ~20% releases as CH4 in waterlogged conditions
    CH4_fraction = 0.20
    annual_fraction = 0.05  # ~5% of newly thawed C releases per year

    CO2_flux = C_available * annual_fraction * (1 - CH4_fraction)
    CH4_flux = C_available * annual_fraction * CH4_fraction

    return {
        "CO2_flux_GtC_yr":  CO2_flux,
        "CH4_flux_GtC_yr":  CH4_flux,
        "total_GtC_yr":     CO2_flux + CH4_flux * 28,  # CO2-equivalent
        "thaw_depth_m":     thaw_depth_m,
        "cascade_to_atmosphere": True,
        "self_amplifying":  True,
        "reversibility":    "irreversible on human timescales once initiated",
        "note": "largest single self-amplifying feedback — poorly constrained timing"
    }


# ─────────────────────────────────────────────
# OCEAN BIOLOGY
# ─────────────────────────────────────────────

def ocean_acidification(delta_CO2_ppm, baseline_pH=8.2):
    """
    Ocean pH change from CO2 absorption.
    CO2 + H2O -> H2CO3 -> H+ + HCO3-
    pH has dropped 0.1 units since industrial revolution — 26% more acidic.
    Logarithmic scale means each 0.1 unit = significant biological impact.
    Calcifying organisms (coral, shellfish, pteropods) dissolve below
    aragonite saturation threshold — hard biological limit.
    delta_CO2_ppm : CO2 increase above pre-industrial (ppm)
    returns: pH change and aragonite saturation state
    """
    # Empirical: ~0.1 pH units per 100 ppm CO2 increase (approximate)
    delta_pH    = -0.0009 * delta_CO2_ppm
    current_pH  = baseline_pH + delta_pH
    # Aragonite saturation state Omega — below 1.0 = dissolution
    omega_aragonite = 3.5 * np.exp(delta_pH * 2.3)  # proxy scaling
    return {
        "delta_pH":              delta_pH,
        "current_pH":            current_pH,
        "omega_aragonite":       omega_aragonite,
        "coral_dissolution":     omega_aragonite < 1.0,
        "pteropod_stress":       omega_aragonite < 1.5,
        "cascade_to_food_web":   True,
        "note": "ocean has absorbed ~30% of anthropogenic CO2 — buffering capacity finite"
    }


def marine_productivity_stratification(delta_T_surface, mixed_layer_depth_m):
    """
    Warming stratifies ocean — reduces nutrient upwelling to surface.
    Productivity collapses in stratified oligotrophic gyres.
    Phytoplankton produce ~50% of Earth's oxygen.
    delta_T_surface    : surface warming (K)
    mixed_layer_depth_m: current mixed layer depth (m)
    returns: productivity change fraction and oxygen production proxy
    """
    # Stratification increases with surface warming
    stratification_increase = delta_T_surface * 0.04  # m per K shoaling
    new_MLD = mixed_layer_depth_m - stratification_increase * 10
    # Nutrient flux scales with mixed layer depth
    nutrient_flux_change = (new_MLD - mixed_layer_depth_m) / mixed_layer_depth_m
    productivity_change  = nutrient_flux_change * 0.7  # not 1:1
    return {
        "mixed_layer_shoaling_m":    stratification_increase * 10,
        "nutrient_flux_change":      nutrient_flux_change,
        "productivity_change_frac":  productivity_change,
        "O2_production_change":      productivity_change * 0.5,
        "cascade_to_atmosphere":     "reduced CO2 uptake, reduced O2 production",
        "cascade_to_food_web":       True,
        "note": "oligotrophic gyres already expanding measurably"
    }


def biological_pump_efficiency(T_surface_C, productivity_change):
    """
    Biological pump — sinking of organic carbon to deep ocean.
    Sequesters carbon on centennial-millennial timescales.
    Warming reduces export efficiency — more remineralization in upper ocean.
    T_surface_C          : surface temperature (°C)
    productivity_change  : fractional change in surface productivity
    returns: carbon export flux change (fraction of baseline)
    """
    # Martin curve: flux ~ depth^(-b), b increases with temperature
    b_baseline = 0.86
    b_warmed   = b_baseline + 0.004 * (T_surface_C - 15.0)
    export_change = (1 + productivity_change) * (b_baseline / b_warmed)
    return {
        "export_efficiency_change": export_change - 1.0,
        "martin_curve_b":          b_warmed,
        "deep_carbon_flux_change": export_change - 1.0,
        "cascade_to_hydrosphere":  "deep ocean oxygen, carbonate chemistry",
    }


# ─────────────────────────────────────────────
# TERRESTRIAL FEEDBACKS
# ─────────────────────────────────────────────

def albedo_vegetation_feedback(vegetation_type, delta_T_K):
    """
    Vegetation shifts change surface albedo — direct climate feedback.
    Boreal forest advancing into tundra: darker surface absorbs more.
    Tropical forest die-back: increases albedo slightly but loses
    evapotranspiration cooling — net positive forcing.
    vegetation_type : 'boreal', 'tropical', 'tundra', 'grassland', 'desert'
    delta_T_K       : temperature change driving shift
    returns: albedo change and net forcing estimate (W/m^2)
    """
    albedos = {
        "boreal":    0.12,
        "tropical":  0.13,
        "tundra":    0.20,
        "grassland": 0.18,
        "desert":    0.30,
        "snow":      0.80,
    }
    transitions = {
        "tundra":   ("boreal",    0.02),   # boreal advances at 0.02 K threshold
        "boreal":   ("grassland", 0.05),   # drought stress
        "tropical": ("grassland", 0.04),   # dieback threshold
        "grassland":("desert",    0.03),   # desertification
    }
    S0 = 1361.0 / 4
    if vegetation_type in transitions and delta_T_K > transitions[vegetation_type][1]:
        new_type    = transitions[vegetation_type][0]
        delta_alpha = albedos[new_type] - albedos[vegetation_type]
        forcing     = -S0 * delta_alpha
        return {
            "transition":      f"{vegetation_type} -> {new_type}",
            "albedo_change":   delta_alpha,
            "forcing_Wm2":     forcing,
            "cascade_to_atmosphere": True,
            "irreversible":    delta_T_K > transitions[vegetation_type][1] * 2,
        }
    return {"transition": "none", "albedo_change": 0.0, "forcing_Wm2": 0.0}


def evapotranspiration_cooling(LAI, T_K, VPD_Pa, soil_moisture=0.6):
    """
    Evapotranspiration — vegetation as cooling engine.
    Tropical forests transpire ~3mm/day — drives regional moisture recycling.
    Deforestation removes this cooling AND disrupts precipitation patterns
    over continental interiors. Amazon moisture recycling covers ~50% of
    South American precipitation — its loss is a continental-scale cascade.
    LAI          : leaf area index (m^2 leaf / m^2 ground)
    T_K          : air temperature (K)
    VPD_Pa       : vapor pressure deficit (Pa)
    soil_moisture: volumetric soil moisture fraction
    returns: ET flux (kg/m^2/day) and cooling equivalent (W/m^2)
    """
    L_v = 2.501e6  # J/kg
    # Penman-Monteith simplified
    g_s = 0.01 * LAI * soil_moisture  # stomatal conductance proxy m/s
    rho_air = 1.2   # kg/m^3
    ET_kgs  = rho_air * g_s * VPD_Pa / 101325.0 * 86400  # kg/m^2/day
    cooling = ET_kgs * L_v / 86400  # W/m^2
    return {
        "ET_mm_day":           ET_kgs,
        "cooling_Wm2":         cooling,
        "cascade_to_atmosphere": "moisture recycling, latent heat, precipitation",
        "cascade_to_hydrosphere":"river discharge, groundwater recharge",
    }


def amazon_tipping_point(deforestation_fraction, delta_T_K, drought_index):
    """
    Amazon dieback threshold — Nobre et al. framework.
    Three interacting stressors: deforestation, warming, drought.
    System has two stable states: forest / savanna.
    Transition is nonlinear and largely irreversible.
    deforestation_fraction : fraction of Amazon already cleared (0-1)
    delta_T_K              : regional warming (K)
    drought_index          : 0-1, 1 = severe multi-year drought
    returns: proximity to tipping point and cascade consequences
    """
    # Each stressor contributes — combined effect nonlinear
    stress = (deforestation_fraction / 0.40 +
              delta_T_K / 4.0 +
              drought_index / 0.8)
    tipping_proximity = min(1.0, stress / 3.0)

    return {
        "tipping_proximity":        tipping_proximity,
        "tipping_imminent":         tipping_proximity > 0.8,
        "current_deforestation":    deforestation_fraction,
        "dieback_cascade": {
            "CO2_release_GtC":       150.0 * tipping_proximity,
            "precipitation_loss_SA": 0.25 * tipping_proximity,
            "albedo_forcing_Wm2":    2.0 * tipping_proximity,
            "global_T_amplification":0.3 * tipping_proximity,
        },
        "reversibility":            "irreversible above tipping point",
        "cascade_to_atmosphere":    True,
        "cascade_to_hydrosphere":   True,
        "note": "current estimate ~20% deforested — threshold ~25-40%"
    }


# ─────────────────────────────────────────────
# BIOGEOCHEMICAL CYCLES
# ─────────────────────────────────────────────

def carbon_cycle_budget(GPP_GtC_yr, respiration_GtC_yr,
                         ocean_uptake_GtC_yr, anthropogenic_GtC_yr,
                         permafrost_flux_GtC_yr=0.0):
    """
    Global carbon budget — conservation law applied to carbon.
    Atmospheric accumulation = sources - sinks.
    All terms must balance — this is a hard constraint.
    Imbalance = missing source or sink — currently ~1 GtC/yr unaccounted.
    returns: atmospheric accumulation rate and budget closure
    """
    land_NEP    = GPP_GtC_yr - respiration_GtC_yr
    total_sink  = land_NEP + ocean_uptake_GtC_yr
    total_source= anthropogenic_GtC_yr + permafrost_flux_GtC_yr
    accumulation= total_source - total_sink

    return {
        "land_sink_GtC_yr":          land_NEP,
        "ocean_sink_GtC_yr":         ocean_uptake_GtC_yr,
        "total_sink_GtC_yr":         total_sink,
        "anthropogenic_GtC_yr":      anthropogenic_GtC_yr,
        "permafrost_flux_GtC_yr":    permafrost_flux_GtC_yr,
        "atmospheric_accumulation":  accumulation,
        "ppm_per_year":              accumulation / 2.13,  # 1 ppm ~ 2.13 GtC
        "sink_fraction":             total_sink / anthropogenic_GtC_yr,
        "note": "land+ocean currently absorbing ~55% of anthropogenic emissions"
    }


def nitrogen_cycle_disruption(synthetic_N_Tg_yr, deposition_N_Tg_yr):
    """
    Reactive nitrogen cascade — Vitousek framework.
    Humans have doubled reactive N in biosphere.
    Excess N: eutrophication, dead zones, N2O production (310x CO2),
    soil acidification, biodiversity loss, ozone depletion.
    synthetic_N_Tg_yr  : synthetic fertilizer application (Tg N/year)
    deposition_N_Tg_yr : atmospheric N deposition (Tg N/year)
    returns: cascade impact summary
    """
    total_reactive_N = synthetic_N_Tg_yr + deposition_N_Tg_yr
    N2O_flux_Tg_yr   = total_reactive_N * 0.01  # ~1% denitrification to N2O
    GWP_equivalent   = N2O_flux_Tg_yr * 310      # CO2-equivalent

    return {
        "total_reactive_N_Tg_yr":  total_reactive_N,
        "N2O_flux_Tg_yr":          N2O_flux_Tg_yr,
        "GWP_CO2_equivalent":      GWP_equivalent,
        "eutrophication_risk":      total_reactive_N > 100,
        "cascade_to_atmosphere":   "N2O forcing, ozone chemistry",
        "cascade_to_hydrosphere":  "dead zones, algal blooms",
        "cascade_to_biosphere":    "biodiversity loss, species composition shift",
    }


def methane_budget(wetland_flux, permafrost_flux, livestock_flux,
                   fossil_flux, OH_sink_fraction=0.88):
    """
    Global methane budget — 28x CO2 over 100 years.
    OH radical is primary atmospheric sink — OH concentration
    itself affected by temperature, pollution, UV.
    Feedback: warming -> more wetland/permafrost flux ->
              more CH4 -> more warming.
    returns: net atmospheric accumulation and OH sensitivity
    """
    total_source = wetland_flux + permafrost_flux + livestock_flux + fossil_flux
    OH_sink      = total_source * OH_sink_fraction
    accumulation = total_source - OH_sink
    return {
        "total_source_TgCH4_yr":   total_source,
        "OH_sink_TgCH4_yr":        OH_sink,
        "accumulation_TgCH4_yr":   accumulation,
        "GWP_CO2_equivalent":      accumulation * 28,
        "OH_feedback": "warming reduces OH -> longer CH4 lifetime -> more warming",
        "cascade_to_atmosphere":   True,
        "self_amplifying":         permafrost_flux > 0,
    }


# ─────────────────────────────────────────────
# PLANETARY BOUNDARIES — THRESHOLD TRACKING
# ─────────────────────────────────────────────

def planetary_boundary_status(CO2_ppm, extinction_rate_relative,
                               N_cycle_Tg, P_cycle_Tg,
                               freshwater_km3, land_use_fraction,
                               ocean_pH, aerosol_AOD,
                               ozone_DU, novel_entities=True):
    """
    Rockstrom planetary boundaries — nine Earth system processes
    with identified safe operating space.
    Crossing boundaries increases risk of abrupt, nonlinear change.
    Multiple boundaries crossed simultaneously: interactions unknown.
    returns: status for each boundary
    """
    return {
        "climate":          {"value": CO2_ppm,      "boundary": 350,   "crossed": CO2_ppm > 350},
        "biodiversity":     {"value": extinction_rate_relative,
                             "boundary": 10,          "crossed": extinction_rate_relative > 10},
        "nitrogen":         {"value": N_cycle_Tg,   "boundary": 62,    "crossed": N_cycle_Tg > 62},
        "phosphorus":       {"value": P_cycle_Tg,   "boundary": 11,    "crossed": P_cycle_Tg > 11},
        "freshwater":       {"value": freshwater_km3,"boundary": 4000,  "crossed": freshwater_km3 > 4000},
        "land_use":         {"value": land_use_fraction,"boundary": 0.15,"crossed": land_use_fraction > 0.15},
        "ocean_acidification":{"value": ocean_pH,   "boundary": 8.05,  "crossed": ocean_pH < 8.05},
        "aerosol_loading":  {"value": aerosol_AOD,  "boundary": 0.25,  "crossed": aerosol_AOD > 0.25},
        "ozone":            {"value": ozone_DU,      "boundary": 276,   "crossed": ozone_DU < 276},
        "novel_entities":   {"value": "unknown",     "boundary": "unknown", "crossed": novel_entities},
        "boundaries_crossed": sum([
            CO2_ppm > 350, extinction_rate_relative > 10,
            N_cycle_Tg > 62, P_cycle_Tg > 11,
            freshwater_km3 > 4000, land_use_fraction > 0.15,
            ocean_pH < 8.05, aerosol_AOD > 0.25,
            ozone_DU < 276, novel_entities
        ]),
        "note": "6+ boundaries currently crossed — interaction effects unquantified"
    }


# ─────────────────────────────────────────────
# COUPLING INTERFACES
# ─────────────────────────────────────────────

def coupling_state(T_surface_K, CO2_ppm, ocean_pH,
                   permafrost_area_m2=1.5e13,
                   T_permafrost_anomaly=1.5,
                   deforestation_fraction=0.20,
                   delta_T_amazon=1.5,
                   drought_index=0.4,
                   GPP_GtC_yr=120.0,
                   anthropogenic_GtC_yr=10.0,
                   AMOC_Sv=17.0):
    """
    Full biosphere state vector for adjacent layer consumption.
    """
    T_C         = T_surface_K - 273.15
    NEP         = net_ecosystem_productivity(
                    gross_primary_productivity(200, T_surface_K, CO2_ppm),
                    T_surface_K)
    permafrost  = permafrost_thaw_carbon_flux(permafrost_area_m2,
                                               T_permafrost_anomaly)
    acidify     = ocean_acidification(CO2_ppm - 280)
    strat       = marine_productivity_stratification(T_C - 14.0, 50.0)
    amazon      = amazon_tipping_point(deforestation_fraction,
                                        delta_T_amazon, drought_index)
    budget      = carbon_cycle_budget(
                    GPP_GtC_yr, GPP_GtC_yr * 0.55,
                    2.5, anthropogenic_GtC_yr,
                    permafrost["total_GtC_yr"])
    CH4         = methane_budget(180, permafrost["CH4_flux_GtC_yr"] * 1000,
                                  100, 580)
    boundaries  = planetary_boundary_status(
                    CO2_ppm, 100, 150, 14, 2600, 0.50,
                    acidify["current_pH"], 0.15, 295)

    return {
        "NEP_carbon_sink":               NEP["carbon_sink"],
        "NEP_gC_m2_day":                 NEP["NEP_gC_m2_day"],
        "permafrost_CO2_GtC_yr":         permafrost["CO2_flux_GtC_yr"],
        "permafrost_CH4_GtC_yr":         permafrost["CH4_flux_GtC_yr"],
        "permafrost_self_amplifying":    permafrost["self_amplifying"],
        "ocean_pH":                      acidify["current_pH"],
        "coral_dissolution_active":      acidify["coral_dissolution"],
        "marine_productivity_change":    strat["productivity_change_frac"],
        "amazon_tipping_proximity":      amazon["tipping_proximity"],
        "amazon_tipping_imminent":       amazon["tipping_imminent"],
        "atmospheric_CO2_accumulation":  budget["ppm_per_year"],
        "CH4_accumulation_GWP":          CH4["GWP_CO2_equivalent"],
        "planetary_boundaries_crossed":  boundaries["boundaries_crossed"],
        "cascade_to_atmosphere":         "CO2, CH4, N2O, ET, albedo, aerosols",
        "cascade_to_hydrosphere":        "ocean chemistry, dead zones, river discharge",
        "cascade_to_lithosphere":        "soil formation, root weathering, peat",
        "cascade_from_atmosphere":       "CO2, temperature, precipitation, UV",
        "cascade_from_hydrosphere":      "nutrients, pH, stratification, AMOC",
        "self_amplifying_feedbacks": [
            "permafrost thaw -> CH4/CO2 -> warming -> more thaw",
            "Amazon dieback -> CO2 + albedo -> warming -> more dieback",
            "ice loss -> albedo -> warming -> more ice loss",
            "ocean stratification -> less uptake -> more CO2 -> more warming",
            "ecosystem respiration > GPP -> source -> more warming",
        ],
        "hard_thresholds": [
            "permafrost: initiated, accelerating, irreversible",
            "Amazon: ~20% cleared, threshold ~25-40%, unknown interaction",
            "coral: pH 8.05 boundary crossed, aragonite saturation declining",
            "AMOC: weakening signal measurable, collapse timing unknown",
        ],
        "note": "biosphere is not a passive responder — it is an active Earth system driver"
    }
