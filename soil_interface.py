# soil_interface.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Soil interface module.
# Tracks nutrient cycling, microbial state, and redox feedback
# at the lithosphere-biosphere boundary.
# Receives mineral nutrient flux from Layer 5 (lithosphere weathering).
# Exports nutrient availability and redox state to Layer 6 (biosphere).
# Atmospheric O2 (Layer 3) diffuses into soil, setting aerobic/anaerobic regime.
# Land degradation, spring collapse, and ecosystem phase shifts are
# invisible to the cascade engine without this module.

import numpy as np

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

EH_ANOXIA_THRESHOLD_MV    = 0.0      # mV — below this: anaerobic decomposition pathway
EH_SUBOXIC_THRESHOLD_MV   = 300.0   # mV — below this: suboxic (O2 depleted)
SOM_COLLAPSE_THRESHOLD_KGM2 = 1.0   # kg C/m² — below this: ecosystem stress / collapse risk
O2_C_MASS_RATIO           = 32.0 / 12.0  # kg O2 consumed per kg C decomposed (stoichiometric)

DECOMP_BASE_RATE_YR       = 0.02    # yr⁻¹ base heterotrophic decomposition rate
DECOMP_Q10                = 2.0     # Q10 temperature sensitivity of decomposition

TOTAL_SOIL_POROSITY       = 0.45    # m³/m³ typical mineral soil total porosity
N_FIXATION_BASELINE_GM2_YR = 2.0   # g N/m²/yr biological nitrogen fixation


# ─────────────────────────────────────────────
# MINERAL WEATHERING → NUTRIENT FLUX
# ─────────────────────────────────────────────

def mineral_nutrient_flux(crustal_weathering_rate_m_yr,
                           mineral_P_fraction=0.001,
                           mineral_K_fraction=0.005):
    """
    P and K flux released by chemical dissolution of parent rock.
    N is not primarily supplied by weathering (biological fixation dominates).
    crustal_weathering_rate_m_yr : rock dissolution rate (m/yr); global mean ~5e-5
    mineral_P_fraction           : P mass fraction in parent rock (~0.1% apatite-bearing)
    mineral_K_fraction           : K mass fraction in parent rock (~0.5% feldspar)
    returns: dict with P_flux_gm2_yr and K_flux_gm2_yr
    """
    rho_rock = 2700.0  # kg/m³ average crustal density
    mass_dissolved_kgm2_yr = crustal_weathering_rate_m_yr * rho_rock
    P_flux = mass_dissolved_kgm2_yr * mineral_P_fraction * 1e3   # g/m²/yr
    K_flux = mass_dissolved_kgm2_yr * mineral_K_fraction * 1e3   # g/m²/yr
    return {
        "P_flux_gm2_yr":               P_flux,
        "K_flux_gm2_yr":               K_flux,
        "mineral_mass_flux_kgm2_yr":   mass_dissolved_kgm2_yr,
    }


# ─────────────────────────────────────────────
# SOIL REDOX POTENTIAL
# ─────────────────────────────────────────────

def redox_potential(theta_v, O2_soil_fraction, theta_field_capacity=0.40):
    """
    Soil redox potential Eh (mV) from volumetric water content and pore O2.
    Primary driver: water saturation blocks O2 diffusion → reducing conditions.
    Secondary: O2 partial pressure sets the aerobic ceiling.
    At field capacity (theta_v=0.40) and full atmospheric O2: Eh ≈ 400 mV.
    Saturated soils (theta_v ≥ 1.0): Eh ≈ -200 mV (strongly reducing).

    theta_v           : volumetric water content (m³/m³, 0–1)
    O2_soil_fraction  : O2 volume fraction in soil air space (0–0.2095)
    theta_field_capacity: water content at field capacity (m³/m³)
    returns: Eh (mV), range approximately [-300, 800]
    """
    # Saturation index: 0 at field capacity, 1 at full saturation
    sat_index = max(0.0, min(1.0,
        (theta_v - theta_field_capacity) / max(1e-6, 1.0 - theta_field_capacity)))

    # Aerobic Eh reduced by O2 depletion
    pO2_ratio  = max(1e-8, O2_soil_fraction / 0.2095)  # relative to atmospheric
    O2_penalty = 60.0 * max(0.0, -np.log10(pO2_ratio))  # mV per decade of O2 loss

    Eh_aerobic   =  400.0 - O2_penalty
    Eh_anaerobic = -200.0  # strongly reducing flooded soil

    Eh = Eh_aerobic * (1.0 - sat_index) + Eh_anaerobic * sat_index
    return float(np.clip(Eh, -300.0, 800.0))


# ─────────────────────────────────────────────
# MICROBIAL RESPIRATION
# ─────────────────────────────────────────────

def microbial_respiration_rate(SOM_kgm2, T_K, theta_v, Eh_mV):
    """
    Heterotrophic microbial decomposition rate of soil organic matter.
    Aerobic (Eh > 0 mV): full Q10-temperature-moisture response.
    Anaerobic (Eh ≤ 0 mV): suppressed to ~10% of aerobic rate;
      dominant pathway shifts to methanogenesis and fermentation.

    SOM_kgm2 : soil organic matter stock (kg C/m²)
    T_K      : soil temperature (K)
    theta_v  : volumetric water content (0–1)
    Eh_mV    : redox potential (mV)
    returns  : dict with decomp_rate_kgm2_yr, aerobic flag, O2 demand
    """
    T_C             = T_K - 273.15
    temp_factor     = DECOMP_Q10 ** (T_C / 10.0)
    # Moisture optimum ~0.5; too wet or too dry slows aerobic decomp
    moisture_factor = max(0.0, theta_v * (1.0 - theta_v) * 4.0)
    aerobic         = Eh_mV > EH_ANOXIA_THRESHOLD_MV
    anox_suppression = 1.0 if aerobic else 0.10

    rate = DECOMP_BASE_RATE_YR * SOM_kgm2 * temp_factor * moisture_factor * anox_suppression
    O2_demand = rate * O2_C_MASS_RATIO  # kg O2/m²/yr consumed

    return {
        "decomp_rate_kgm2_yr":  rate,
        "aerobic":              aerobic,
        "anaerobic":            not aerobic,
        "O2_demand_kgm2_yr":    O2_demand if aerobic else 0.0,
    }


# ─────────────────────────────────────────────
# NUTRIENT MINERALIZATION
# ─────────────────────────────────────────────

def nutrient_mineralization(SOM_kgm2, microbial_biomass_kgm2, T_K):
    """
    N, P, K released from organic matter during microbial decomposition.
    Stoichiometric ratios of soil organic matter:
      C:N ≈ 15:1, C:P ≈ 100:1, C:K ≈ 50:1 (mass ratios).

    SOM_kgm2           : soil organic matter (kg C/m²)
    microbial_biomass_kgm2: microbial biomass C (kg C/m²)
    T_K                : soil temperature (K)
    returns: mineralization fluxes (g/m²/yr) for N, P, K
    """
    T_C          = T_K - 273.15
    turnover_yr  = 0.02 * (DECOMP_Q10 ** (T_C / 10.0))  # yr⁻¹ slow-pool turnover
    C_min_kgm2_yr = (SOM_kgm2 * turnover_yr
                     + microbial_biomass_kgm2 * 0.50)     # microbial mortality

    N_gm2_yr = C_min_kgm2_yr * 1e3 / 15.0    # C:N = 15
    P_gm2_yr = C_min_kgm2_yr * 1e3 / 100.0   # C:P = 100
    K_gm2_yr = C_min_kgm2_yr * 1e3 / 50.0    # C:K = 50

    return {
        "N_mineralized_gm2_yr": N_gm2_yr,
        "P_mineralized_gm2_yr": P_gm2_yr,
        "K_mineralized_gm2_yr": K_gm2_yr,
    }


# ─────────────────────────────────────────────
# PLANT NUTRIENT UPTAKE DEMAND
# ─────────────────────────────────────────────

def plant_nutrient_uptake_demand(GPP_gC_m2_day):
    """
    Stoichiometric N, P, K uptake demand from plants given productivity.
    Follows Elser / Redfield stoichiometry for vegetated land:
      leaf C:N ≈ 25, C:P ≈ 200, C:K ≈ 50 (mass).
    GPP_gC_m2_day : gross primary productivity (g C/m²/day)
    returns: annual demand for N, P, K (g/m²/yr)
    """
    GPP_yr  = GPP_gC_m2_day * 365.0  # g C/m²/yr
    N_dem   = GPP_yr / 25.0
    P_dem   = GPP_yr / 200.0
    K_dem   = GPP_yr / 50.0
    return {
        "N_demand_gm2_yr": N_dem,
        "P_demand_gm2_yr": P_dem,
        "K_demand_gm2_yr": K_dem,
    }


# ─────────────────────────────────────────────
# NUTRIENT STRESS — LIEBIG'S LAW OF THE MINIMUM
# ─────────────────────────────────────────────

def nutrient_stress_factor(N_avail_gm2, P_avail_gm2, K_avail_gm2,
                            N_demand_gm2_yr, P_demand_gm2_yr, K_demand_gm2_yr):
    """
    Nutrient limitation scalar for plant productivity (Liebig's law of the minimum).
    Most limiting nutrient (lowest supply/demand ratio) governs productivity.
    Returns stress factor 0–1 (1.0 = unlimited, 0.0 = fully limited).

    Available stocks (g/m²) are compared against annual demand (g/m²/yr).
    Leaching risk: supply exceeds 2× annual demand — excess will leach.
    """
    def ratio(avail, demand):
        if demand <= 0:
            return 1.0
        return min(1.0, avail / max(demand, 1e-10))

    N_r = ratio(N_avail_gm2, N_demand_gm2_yr)
    P_r = ratio(P_avail_gm2, P_demand_gm2_yr)
    K_r = ratio(K_avail_gm2, K_demand_gm2_yr)

    limiting_val  = min(N_r, P_r, K_r)
    limiting_name = ["N", "P", "K"][[N_r, P_r, K_r].index(limiting_val)]

    # Leaching risk when any nutrient supply well exceeds demand
    def leach_risk(avail, demand):
        if demand <= 0:
            return False
        return avail > 2.0 * demand

    leaching = leach_risk(N_avail_gm2, N_demand_gm2_yr) or \
               leach_risk(P_avail_gm2, P_demand_gm2_yr) or \
               leach_risk(K_avail_gm2, K_demand_gm2_yr)

    return {
        "nutrient_stress_factor": limiting_val,
        "limiting_nutrient":      limiting_name,
        "N_supply_ratio":         N_r,
        "P_supply_ratio":         P_r,
        "K_supply_ratio":         K_r,
        "nutrient_leaching_risk": leaching,
    }


# ─────────────────────────────────────────────
# COUPLING INTERFACE
# ─────────────────────────────────────────────

def coupling_state(SOM_kgm2, microbial_biomass_kgm2,
                   N_avail_gm2, P_avail_gm2, K_avail_gm2,
                   pH, theta_v, T_soil_K,
                   crustal_weathering_rate_m_yr,
                   O2_atm_fraction=0.2095,
                   GPP_gC_m2_day=5.0):
    """
    Full soil interface state vector coupling lithosphere ↔ biosphere.

    Inputs from lithosphere (Layer 5):
      crustal_weathering_rate_m_yr : chemical weathering rate (m/yr)

    Inputs from atmosphere (Layer 3):
      O2_atm_fraction : atmospheric O2 mole fraction (diffuses into soil pores)

    Soil state variables:
      SOM_kgm2           : soil organic matter stock (kg C/m²)
      microbial_biomass_kgm2: microbial biomass C (kg C/m²)
      N_avail_gm2        : available N pool (g/m²)
      P_avail_gm2        : available P pool (g/m²)
      K_avail_gm2        : available K pool (g/m²)
      pH                 : soil pH
      theta_v            : volumetric water content (0–1)
      T_soil_K           : soil temperature (K)

    Outputs to biosphere (Layer 6):
      nutrient_stress_factor : Liebig minimum of N/P/K supply ratios (0–1)
      Eh_mV                  : redox potential (mV)
      decomp_rate_kgm2_yr    : heterotrophic respiration per m²
    """
    # O2 diffusion from atmosphere into soil pore space
    air_filled = max(0.0, TOTAL_SOIL_POROSITY - theta_v)
    tortuosity = (air_filled / TOTAL_SOIL_POROSITY) ** 1.5  # Millington-Quirk
    O2_soil_fraction = max(0.0, O2_atm_fraction * tortuosity)

    # Soil redox potential
    Eh_mV = redox_potential(theta_v, O2_soil_fraction)

    # Microbial decomposition rate
    decomp = microbial_respiration_rate(SOM_kgm2, T_soil_K, theta_v, Eh_mV)

    # Nutrient mineralization from decomposing SOM
    mineral = nutrient_mineralization(SOM_kgm2, microbial_biomass_kgm2, T_soil_K)

    # Mineral nutrient input from crustal weathering
    weath   = mineral_nutrient_flux(crustal_weathering_rate_m_yr)

    # Biological N fixation (temperature and moisture sensitive)
    T_C     = T_soil_K - 273.15
    n_fix_factor = max(0.0, min(1.0, 1.0 - abs(T_C - 20.0) / 30.0)) * theta_v * 2.0
    N_fixation_gm2_yr = N_FIXATION_BASELINE_GM2_YR * n_fix_factor

    # Total available supply (standing pool + annual mineralization + weathering + fixation)
    N_total_supply = N_avail_gm2 + mineral["N_mineralized_gm2_yr"] + N_fixation_gm2_yr
    P_total_supply = P_avail_gm2 + mineral["P_mineralized_gm2_yr"] + weath["P_flux_gm2_yr"]
    K_total_supply = K_avail_gm2 + mineral["K_mineralized_gm2_yr"] + weath["K_flux_gm2_yr"]

    # Plant uptake demand
    demand  = plant_nutrient_uptake_demand(GPP_gC_m2_day)

    # Nutrient stress / Liebig minimum
    stress  = nutrient_stress_factor(
        N_total_supply, P_total_supply, K_total_supply,
        demand["N_demand_gm2_yr"],
        demand["P_demand_gm2_yr"],
        demand["K_demand_gm2_yr"],
    )

    anoxia_active = Eh_mV < EH_ANOXIA_THRESHOLD_MV

    return {
        "SOM_kgm2":                    SOM_kgm2,
        "microbial_biomass_kgm2":      microbial_biomass_kgm2,
        "Eh_mV":                       Eh_mV,
        "aerobic":                     decomp["aerobic"],
        "anaerobic":                   decomp["anaerobic"],
        "anoxia_active":               anoxia_active,
        "SOM_below_collapse_threshold": SOM_kgm2 < SOM_COLLAPSE_THRESHOLD_KGM2,
        "O2_soil_fraction":            O2_soil_fraction,
        "decomp_rate_kgm2_yr":         decomp["decomp_rate_kgm2_yr"],
        "decomp_O2_demand_kgm2_yr":    decomp["O2_demand_kgm2_yr"],
        "N_mineralized_gm2_yr":        mineral["N_mineralized_gm2_yr"],
        "P_mineralized_gm2_yr":        mineral["P_mineralized_gm2_yr"],
        "K_mineralized_gm2_yr":        mineral["K_mineralized_gm2_yr"],
        "N_fixation_gm2_yr":           N_fixation_gm2_yr,
        "mineral_P_flux_gm2_yr":       weath["P_flux_gm2_yr"],
        "mineral_K_flux_gm2_yr":       weath["K_flux_gm2_yr"],
        "N_total_supply_gm2_yr":       N_total_supply,
        "P_total_supply_gm2_yr":       P_total_supply,
        "K_total_supply_gm2_yr":       K_total_supply,
        "N_demand_gm2_yr":             demand["N_demand_gm2_yr"],
        "P_demand_gm2_yr":             demand["P_demand_gm2_yr"],
        "K_demand_gm2_yr":             demand["K_demand_gm2_yr"],
        "nutrient_stress_factor":      stress["nutrient_stress_factor"],
        "limiting_nutrient":           stress["limiting_nutrient"],
        "N_supply_ratio":              stress["N_supply_ratio"],
        "P_supply_ratio":              stress["P_supply_ratio"],
        "K_supply_ratio":              stress["K_supply_ratio"],
        "nutrient_leaching_risk":      stress["nutrient_leaching_risk"],
        "soil_pH":                     pH,
        "theta_v":                     theta_v,
        "T_soil_K":                    T_soil_K,
        "crustal_weathering_rate_m_yr": crustal_weathering_rate_m_yr,
        "cascade_from_lithosphere":    "crustal weathering → mineral P, K flux",
        "cascade_from_atmosphere":     "O2 diffusion → soil redox state",
        "cascade_to_biosphere":        "nutrient_stress_factor, Eh_mV, decomp_rate → GPP, O2 budget",
        "note": ("anoxia kills aerobic microbial communities; triggers anaerobic "
                 "decomposition; changes nutrient cycling and CH4 production"),
    }
