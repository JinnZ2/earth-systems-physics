# layer_4_hydrosphere.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Hydrosphere constraint layer.
# Governs ocean heat transport, sea ice, freshwater cycling,
# thermohaline circulation, phase transitions, and sea level.
# Water is the primary heat transport medium on Earth's surface.
# Imports constraints from layers 0-3.

import numpy as np
from scipy.constants import g, Stefan_Boltzmann
from layer_3_atmosphere import (
    saturation_vapor_pressure,
    stefan_boltzmann_flux,
    thermal_wind,
    hadley_cell_extent,
)
# Dissolved-oxygen physics lives in aquatic_deoxygenation.py (stdlib only)
# so the boundary framework can be used without the layer stack.
from aquatic_deoxygenation import (
    oxygen_solubility_umol_kg,
    umol_kg_to_mg_L,
    mg_L_to_umol_kg,
    interior_oxygen_from_ventilation,
    deoxygenation_feedback_gain,
    deoxygenation_boundary_status,
    metabolic_index,
    HYPOXIA_MG_L,
    HYPOXIC_VOLUME_FRACTION_REFERENCE,
)

# ─────────────────────────────────────────────
# FUNDAMENTAL CONSTANTS — WATER
# ─────────────────────────────────────────────

rho_freshwater  = 1000.0    # kg/m^3
rho_seawater    = 1025.0    # kg/m^3
rho_ice         = 917.0     # kg/m^3
cp_seawater     = 3850.0    # J/(kg·K)
cp_freshwater   = 4182.0    # J/(kg·K)
L_v             = 2.501e6   # J/kg latent heat vaporization
L_f             = 3.337e5   # J/kg latent heat fusion
kappa_water     = 0.58      # W/(m·K) thermal conductivity
kappa_ice       = 2.1       # W/(m·K) thermal conductivity ice
alpha_thermal   = 2.1e-4    # 1/K thermal expansion seawater ~15°C
beta_haline     = 7.4e-4    # 1/psu haline contraction

g_earth         = 9.80665   # m/s^2
R_E             = 6.371e6   # m
ocean_area      = 3.61e14   # m^2
ocean_volume    = 1.335e18  # m^3
ocean_mean_depth= 3700.0    # m

# ─────────────────────────────────────────────
# SEAWATER DENSITY
# ─────────────────────────────────────────────

def seawater_density(T, S, P=0):
    """
    Simplified equation of state for seawater.
    UNESCO linearized form — adequate for large-scale dynamics.
    T : temperature (°C)
    S : salinity (PSU)
    P : pressure (dbar), 0 = surface
    returns: density (kg/m^3)
    """
    rho_0 = 1025.0
    return rho_0 * (1 - alpha_thermal * (T - 10.0) + beta_haline * (S - 35.0))


def buoyancy_frequency_ocean(drho_dz, rho_0=1025.0):
    """
    Brunt-Vaisala frequency in ocean — governs internal wave propagation.
    drho_dz : vertical density gradient (kg/m^4) — negative = stable
    rho_0   : reference density (kg/m^3)
    returns: N (rad/s)
    """
    N2 = -(g_earth / rho_0) * drho_dz
    if N2 >= 0:
        return np.sqrt(N2)
    else:
        return 1j * np.sqrt(abs(N2))


def mixed_layer_depth(wind_stress, rho, delta_rho, latitude_deg=45.0):
    """
    Monin-Obukhov mixed layer depth approximation.
    Wind stress mixes surface layer — governs air-sea heat exchange.
    wind_stress  : surface wind stress (Pa)
    rho          : surface density (kg/m^3)
    delta_rho    : density difference across base of mixed layer (kg/m^3)
    latitude_deg : for Coriolis
    returns: mixed layer depth (m)
    """
    from layer_3_atmosphere import coriolis_parameter
    f   = abs(coriolis_parameter(latitude_deg))
    u_star = np.sqrt(wind_stress / rho)  # friction velocity
    if delta_rho <= 0 or f == 0:
        return 200.0  # default deep mixed layer
    return 0.4 * u_star / (f * np.sqrt(delta_rho / rho))


# ─────────────────────────────────────────────
# THERMOHALINE CIRCULATION
# ─────────────────────────────────────────────

def atlantic_overturning_index(T_north, S_north, T_south, S_south):
    """
    Proxy for AMOC (Atlantic Meridional Overturning Circulation) strength.
    Driven by density difference between North Atlantic deep water
    formation regions and equatorial surface water.
    Freshwater input from melting ice reduces S_north -> weakens AMOC.
    T_north, S_north : North Atlantic surface T(°C), S(PSU)
    T_south, S_south : Equatorial Atlantic surface T(°C), S(PSU)
    returns: density gradient (kg/m^3) — proxy for overturning strength
    """
    rho_north = seawater_density(T_north, S_north)
    rho_south = seawater_density(T_south, S_south)
    return rho_north - rho_south


def amoc_freshwater_sensitivity(delta_S, baseline_gradient):
    """
    Change in AMOC strength from freshwater perturbation.
    Meltwater from Greenland/Arctic reduces North Atlantic salinity.
    This is a threshold system — potential collapse below critical gradient.
    delta_S           : salinity reduction (PSU)
    baseline_gradient : current density gradient (kg/m^3)
    returns: new gradient and collapse risk flag
    """
    rho_change = beta_haline * rho_seawater * delta_S
    new_gradient = baseline_gradient - rho_change
    collapse_threshold = 0.3  # kg/m^3 — approximate, highly uncertain
    return {
        "new_density_gradient": new_gradient,
        "collapse_risk":        new_gradient < collapse_threshold,
        "collapse_threshold":   collapse_threshold,
        "note": "AMOC collapse is irreversible on human timescales — hard threshold"
    }


# ─────────────────────────────────────────────
# AMOC EXPLICIT STATE VARIABLES  (2024–2026 literature update)
# Density gradient, freshwater sensitivity, and salinity front tracked as
# named state variables rather than implicit in flux calculations.
# Critical threshold 0.8 kg/m³ across 30°N: Caesar et al. 2021,
# Boers 2021, Ditlevsen & Ditlevsen 2023.
# ─────────────────────────────────────────────

AMOC_DENSITY_GRADIENT_CRITICAL = 0.8   # kg/m³ — phase-transition threshold at 30°N


def amoc_freshwater_input_sensitivity(density_gradient_30N):
    """
    Rate of density-gradient change per unit freshwater input [kg/m³ per PSU].
    Derived from haline contraction coefficient (beta_haline).
    density_gradient_30N : current 30°N density gradient (kg/m³)
    returns: sensitivity dict including PSU margin to phase-transition threshold
    """
    sensitivity         = beta_haline * rho_seawater   # kg/m³ per PSU
    margin_to_threshold = density_gradient_30N - AMOC_DENSITY_GRADIENT_CRITICAL
    psu_to_threshold    = (margin_to_threshold / sensitivity
                           if sensitivity > 0 else float("inf"))
    return {
        "sensitivity_kgm3_per_PSU": sensitivity,
        "margin_to_threshold_kgm3": margin_to_threshold,
        "PSU_to_threshold":         psu_to_threshold,
        "threshold_kgm3":           AMOC_DENSITY_GRADIENT_CRITICAL,
    }


def amoc_density_gradient_30N(T_north, S_north,
                                T_south_30N=25.0, S_south_30N=36.5):
    """
    Explicit density gradient across the 30°N Atlantic latitude band.
    Primary AMOC stability diagnostic in post-2021 literature.
    T_north, S_north         : subpolar North Atlantic T (°C), S (PSU)
    T_south_30N, S_south_30N : subtropical 30°N surface T (°C), S (PSU)
    returns: gradient dict with regime flag
    """
    rho_n    = seawater_density(T_north,      S_north)
    rho_s    = seawater_density(T_south_30N,  S_south_30N)
    gradient = rho_n - rho_s
    return {
        "density_gradient_30N_kgm3": gradient,
        "rho_north_kgm3":            rho_n,
        "rho_south_30N_kgm3":        rho_s,
        "above_critical_threshold":  gradient > AMOC_DENSITY_GRADIENT_CRITICAL,
        "critical_threshold_kgm3":   AMOC_DENSITY_GRADIENT_CRITICAL,
    }


def amoc_salinity_front_position(S_north, S_north_baseline=35.0,
                                  front_lat_baseline=50.0):
    """
    Approximate latitude of the North Atlantic salinity front.
    Freshwater anomaly shifts the front equatorward; diagnostic of
    thermohaline geometry deformation.
    S_north           : current subpolar surface salinity (PSU)
    S_north_baseline  : Holocene-regime reference salinity (PSU)
    front_lat_baseline: Holocene-regime front latitude (°N)
    returns: estimated front latitude (°N) and shift
    """
    delta_S        = S_north - S_north_baseline
    front_shift    = delta_S * 10.0          # ~1° equatorward per 0.1 PSU freshening
    front_lat      = front_lat_baseline + front_shift
    return {
        "salinity_front_lat_N": front_lat,
        "front_shift_deg":      front_shift,
        "delta_S_PSU":          delta_S,
        "front_equatorward":    front_shift < 0,
    }


def amoc_phase_transition_check(density_gradient_30N_kgm3):
    """
    Flag regime-shift when the 30°N density gradient drops below the
    critical Holocene-regime threshold (0.8 kg/m³).
    Below threshold: linear thermohaline coupling coefficients invalid;
    system approaches bistable collapse.
    density_gradient_30N_kgm3 : density gradient across 30°N band (kg/m³)
    returns: detection dict; regime_shift_imminent=True triggers cascade protocol
    """
    below     = density_gradient_30N_kgm3 < AMOC_DENSITY_GRADIENT_CRITICAL
    margin    = density_gradient_30N_kgm3 - AMOC_DENSITY_GRADIENT_CRITICAL
    return {
        "density_gradient_30N_kgm3":   density_gradient_30N_kgm3,
        "critical_threshold_kgm3":     AMOC_DENSITY_GRADIENT_CRITICAL,
        "margin_kgm3":                 margin,
        "regime_shift_imminent":       below,
        "coupling_coefficients_valid": not below,
        "note": ("Holocene-regime coefficients invalid. Bistable collapse regime."
                 if below else "Holocene regime — coefficients valid"),
    }


def thermohaline_heat_transport(overturning_Sv, delta_T):
    """
    Heat transported poleward by thermohaline circulation.
    overturning_Sv : volume transport (Sverdrups, 1 Sv = 1e6 m^3/s)
    delta_T        : temperature difference (°C)
    returns: heat transport (W)
    Current AMOC ~17 Sv, ~1.3 PW northward heat transport
    """
    Q_Sv = overturning_Sv * 1e6  # m^3/s
    return rho_seawater * cp_seawater * Q_Sv * delta_T


# ─────────────────────────────────────────────
# BOTTOM WATER FORMATION
# Dense water production at high latitudes — the engine
# that drives the thermohaline circulation.
# Two sources: NADW (North Atlantic) and AABW (Antarctic).
# ─────────────────────────────────────────────

def brine_rejection_flux(ice_formation_rate_m_yr, S_ocean=35.0, ice_S=5.0):
    """
    Salt flux from sea ice formation.
    When seawater freezes, most salt is expelled into the underlying water.
    This densifies the surface layer, driving deep convection.
    ice_formation_rate_m_yr : ice thickness formed per year (m/yr)
    S_ocean                 : ocean salinity (PSU)
    ice_S                   : salinity of new ice (PSU) — typically 4-7
    returns: dict with salt flux, density flux, equivalent freshwater
    """
    # Salt rejected per m^2 per year
    # Mass of ice formed: rho_ice * rate (kg/m^2/yr)
    ice_mass_rate = rho_ice * ice_formation_rate_m_yr  # kg/m^2/yr
    # Salt rejected = ice_mass * (S_ocean - S_ice) / 1000 (PSU to fraction)
    salt_rejected_rate = ice_mass_rate * (S_ocean - ice_S) / 1000  # kg_salt/m^2/yr

    # Density increase in surface layer from brine rejection
    # Assume mixing into 50m surface layer
    mixed_layer = 50.0  # m
    delta_S = (S_ocean - ice_S) * ice_formation_rate_m_yr * rho_ice / (rho_seawater * mixed_layer)
    delta_rho_haline = beta_haline * rho_seawater * delta_S

    # Density decrease from cooling (ice forms at ~-1.8C)
    # Cooling from surface temp to freezing point handled elsewhere
    # Here we just track the haline component

    return {
        "salt_flux_kg_m2_yr": salt_rejected_rate,
        "delta_S_PSU": delta_S,
        "delta_rho_haline_kgm3": delta_rho_haline,
        "mixed_layer_m": mixed_layer,
    }


def deep_convection_criterion(rho_surface, rho_deep, T_surface_C, S_surface):
    """
    Determine whether deep convection is active.
    Convection occurs when surface water is denser than deep water.
    This is the ON/OFF switch for bottom water formation.
    rho_surface : surface water density (kg/m^3)
    rho_deep    : deep water density (kg/m^3) — typically ~1027.8
    T_surface_C : surface temperature (C)
    S_surface   : surface salinity (PSU)
    returns: dict with convection state and stability metrics
    """
    # Density difference (positive = surface lighter = stable)
    delta_rho = rho_deep - rho_surface
    stable = delta_rho > 0

    # Brunt-Vaisala frequency (stability measure)
    # N^2 = -(g/rho_0) * drho/dz
    # For the surface-to-deep gradient over ~4000m depth:
    depth = 4000.0  # m
    N_sq = (g_earth / rho_seawater) * delta_rho / depth
    N = np.sqrt(max(N_sq, 0))

    # Freezing point of seawater at this salinity
    T_freeze = -0.054 * S_surface  # approximate

    # How close to convective threshold?
    # Proximity: 0 = neutrally stable, 1 = very stable
    # Negative = convecting
    rho_margin = delta_rho / rho_seawater
    proximity = rho_margin / 0.003 if rho_margin > 0 else -1.0  # 0.003 is typical margin

    return {
        "convecting": not stable,
        "delta_rho_kgm3": delta_rho,
        "brunt_vaisala_rad_s": N,
        "stability_margin": rho_margin,
        "proximity_to_convection": max(0, 1.0 - proximity),
        "T_freeze_C": T_freeze,
        "surface_at_freezing": T_surface_C <= T_freeze + 0.1,
    }


def bottom_water_formation_rate(T_north_C, S_north, delta_S_melt=0.0,
                                 ice_formation_rate_m_yr=0.5,
                                 T_deep_C=1.5, S_deep=34.9):
    """
    Rate of deep/bottom water formation from surface cooling and brine rejection.
    Combines thermal and haline forcing to determine production rate.

    T_north_C              : surface temperature at formation site (C)
    S_north                : surface salinity (PSU)
    delta_S_melt           : salinity reduction from meltwater (PSU, negative for formation)
    ice_formation_rate_m_yr: annual sea ice production (m/yr)
    T_deep_C               : deep water temperature (C) — typically 1-2C
    S_deep                 : deep water salinity (PSU) — typically 34.9

    returns: dict with NADW/AABW formation rate, convection state, sensitivity
    """
    # Effective surface salinity after meltwater
    S_eff = S_north - delta_S_melt

    # Surface density (cold, salty = dense)
    rho_surface = seawater_density(T_north_C, S_eff)

    # Deep water density
    rho_deep = seawater_density(T_deep_C, S_deep)

    # Brine rejection contribution
    brine = brine_rejection_flux(ice_formation_rate_m_yr, S_eff)
    rho_surface_with_brine = rho_surface + brine["delta_rho_haline_kgm3"]

    # Convection criterion
    convection = deep_convection_criterion(rho_surface_with_brine, rho_deep,
                                            T_north_C, S_eff)

    # Formation rate estimate
    # Stommel (1961): overturning ~ k * delta_rho
    # k ~ 2e7 m^3/s per (kg/m^3) — empirical scaling for NADW
    k_stommel = 2e7  # m^3/s per (kg/m^3)
    delta_rho = rho_surface_with_brine - rho_deep

    if delta_rho > 0:
        # Surface denser than deep -> active formation
        formation_Sv = k_stommel * delta_rho / 1e6  # convert to Sv
    else:
        # Stable stratification -> no formation (or residual from wind-driven)
        formation_Sv = max(0.5, k_stommel * delta_rho / 1e6)  # minimum wind-driven

    # Meltwater shutdown sensitivity
    # How much more meltwater to shut down formation?
    # delta_S needed to make rho_surface = rho_deep
    delta_S_shutdown = delta_rho / (beta_haline * rho_seawater) if delta_rho > 0 else 0

    # AABW contribution (Antarctic)
    # AABW forms at ~-1.8C, S~34.7, driven mainly by brine rejection
    # Approximately 8-10 Sv in preindustrial, declining
    aabw_fraction = max(0, min(1.0, ice_formation_rate_m_yr / 1.0))  # scales with ice production
    aabw_Sv = 8.0 * aabw_fraction

    total_Sv = formation_Sv + aabw_Sv

    return {
        "NADW_formation_Sv": formation_Sv,
        "AABW_formation_Sv": aabw_Sv,
        "total_bottom_water_Sv": total_Sv,
        "convection_active": convection["convecting"],
        "rho_surface_kgm3": rho_surface_with_brine,
        "rho_deep_kgm3": rho_deep,
        "density_excess_kgm3": max(delta_rho, 0),
        "brine_contribution_kgm3": brine["delta_rho_haline_kgm3"],
        "meltwater_to_shutdown_PSU": delta_S_shutdown,
        "stability": convection,
        "brine": brine,
    }


def deep_water_ventilation_age(formation_rate_Sv, ocean_volume_m3=1.335e18):
    """
    Mean age of deep water — time since it was last at the surface.
    Controls how quickly atmospheric changes propagate to deep ocean.
    formation_rate_Sv : total bottom water formation rate (Sv)
    ocean_volume_m3   : total ocean volume below thermocline
    returns: ventilation timescale (years)
    """
    if formation_rate_Sv <= 0:
        return np.inf
    flow_m3_s = formation_rate_Sv * 1e6
    seconds = ocean_volume_m3 / flow_m3_s
    return seconds / (365.25 * 86400)


# ─────────────────────────────────────────────
# SOUTHERN OCEAN HEAT TRANSPORT  (Lanham et al. 2026)
# Circumpolar Deep Water poleward migration was a model PROJECTION
# with wide uncertainty bands until 2026. Lanham et al. (Comm Earth
# Env 7:371) confirmed it as observation from ship + Argo + random
# forest over a 20-yr record.
#
# Three coupled changes are now well-constrained:
#   1. CDW boundary advances poleward at 1.26 +/- 0.7 km/yr
#      (Weddell Sea hot spot 2.39 km/yr; W Antarctica 0.80).
#   2. CDW thickens NEAR the continent and thins offshore.
#   3. Antarctic Bottom Water contracts along the continental margin.
#
# Operational consequence: 2.81 TW of poleward heat transport into
# the 60-65 S band is now a measured boundary condition for ice-shelf
# basal melt cascades, not a model parameter.
#
# This sets up the positive feedback loop encoded below:
#   CDW heat -> ice shelf basal melt -> freshwater cap -> AABW
#   formation suppression -> reduced cold buffer -> more CDW
#   intrusion. Detected since the 2016 Southern Ocean sea ice
#   collapse; nonlinear releases of this kind are exactly what the
#   steady-state thermohaline equations do not capture.
# ─────────────────────────────────────────────

CDW_POLEWARD_MIGRATION = {
    "circumpolar_mean_km_per_yr": 1.26,
    "ci_95_low":                  0.53,
    "ci_95_high":                 1.98,
    "weddell_sea":                2.39,
    "east_antarctica":            1.31,
    "west_antarctica":            0.80,
    "source":                     "Lanham et al. 2026, Comm Earth Env 7:371",
    "method":                     "ship obs + Argo + random forest, 20yr record",
    "observational_status":       "confirmed (was model-projected)",
}

CDW_HEAT_FLUX_60_65S = {
    "rate_terawatts": 2.81,
    "ci_95_low":      2.0,
    "ci_95_high":     3.6,
    "layer":          "Circumpolar Deep Water, upper 2000m",
}

SOUTHERN_OCEAN_STRUCTURAL_SHIFT = {
    "CDW_thickness_near_continent":   "increasing",
    "CDW_thickness_offshore":         "decreasing",
    "AABW_thickness_along_margin":    "contracting",
    "interpretation":                 "warm layer advancing, cold buffer retreating",
}


def cdw_basal_melt_rate_Gt_yr(cdw_heat_flux_TW=2.81,
                              baseline_TW=1.5,
                              sensitivity_Gt_per_TW=80.0):
    """
    Differential ice-shelf basal melt attributable to CDW poleward
    heat flux excess above the pre-2000 baseline (~1.5 TW).
    Empirical sensitivity ~50-100 Gt/yr per TW of cross-shelf flux
    excess from intrusion-event studies (Schmidtko 2014, Naughten
    2018). Returns the ATTRIBUTABLE component, not total Antarctic
    basal melt (which is dominated by other heat sources too).
    cdw_heat_flux_TW       : current poleward CDW heat flux (TW)
    baseline_TW            : pre-2000 reference (TW)
    sensitivity_Gt_per_TW  : empirical melt sensitivity (Gt/yr per TW)
    returns: CDW-attributable basal melt rate (Gt/yr)
    """
    excess = max(0.0, cdw_heat_flux_TW - baseline_TW)
    return excess * sensitivity_Gt_per_TW


def freshwater_cap_PSU_anomaly(basal_melt_Gt_yr,
                               receiving_volume_m3=2e14,
                               S_ambient=34.7):
    """
    Annual surface salinity drop in the near-Antarctica freshwater
    lens from ice-shelf basal melt input. Mass-balance form:
        delta_S ~ - S_ambient * (V_freshwater / V_receiving)
    Default receiving volume 2e14 m^3 corresponds to ~10 m of upper
    Southern Ocean over the continental shelf zone (~2e13 m^2).
    basal_melt_Gt_yr    : freshwater input (Gt/yr)
    receiving_volume_m3 : annual mixing volume of the surface lens
    S_ambient           : ambient salinity (PSU)
    returns: salinity anomaly (PSU; negative = freshening)
    """
    freshwater_volume_m3_yr = (basal_melt_Gt_yr * 1e12) / rho_freshwater
    return -S_ambient * (freshwater_volume_m3_yr / receiving_volume_m3)


def aabw_suppression_factor(freshwater_PSU_anomaly,
                            shutdown_PSU=-0.05):
    """
    Fractional reduction in AABW formation from freshwater capping.
    Saturating exponential:
        suppression = 1 - exp(- |delta_S| / |shutdown_PSU|)
    Default shutdown scale -0.05 PSU calibrated to AABW thinning
    observations (Purkey & Johnson 2013; Silvano 2018) — that
    magnitude of cumulative freshening already produces measurable
    AABW contraction.
    freshwater_PSU_anomaly : salinity anomaly (negative = freshening)
    shutdown_PSU           : characteristic shutdown salinity scale
    returns: 0..1 suppression fraction
    """
    if freshwater_PSU_anomaly >= 0 or shutdown_PSU >= 0:
        return 0.0
    return float(1.0 - np.exp(-abs(freshwater_PSU_anomaly)
                              / abs(shutdown_PSU)))


def cdw_aabw_feedback_index(cdw_heat_flux_TW=2.81,
                            baseline_TW=1.5,
                            sensitivity_Gt_per_TW=80.0,
                            shutdown_PSU=-0.05):
    """
    Composite index for the positive feedback loop:
        CDW heat -> ice shelf basal melt -> freshwater cap ->
        AABW formation suppression -> reduced cold buffer ->
        more CDW intrusion.
    Returns a dict capturing each step plus the combined feedback
    index. Loop is flagged active when CDW-attributable melt is
    non-trivial AND AABW suppression is measurable.
    """
    melt_Gt_yr = cdw_basal_melt_rate_Gt_yr(cdw_heat_flux_TW,
                                           baseline_TW,
                                           sensitivity_Gt_per_TW)
    delta_S    = freshwater_cap_PSU_anomaly(melt_Gt_yr)
    suppression = aabw_suppression_factor(delta_S, shutdown_PSU)
    # Feedback gain proxy: melt scaled to a reference attributable
    # value (50 Gt/yr) AND multiplied by AABW suppression.
    melt_norm = min(1.0, melt_Gt_yr / 50.0)
    feedback_index = float(melt_norm * suppression)
    return {
        "cdw_heat_flux_TW":          cdw_heat_flux_TW,
        "basal_melt_Gt_yr":          melt_Gt_yr,
        "freshwater_PSU_anomaly":    delta_S,
        "aabw_suppression_factor":   suppression,
        "cdw_aabw_feedback_index":   feedback_index,
        "loop_active":               (melt_Gt_yr > 50.0
                                       and suppression > 0.05),
        "note": ("positive feedback observed since 2016 Southern Ocean "
                 "sea ice collapse; steady-state thermohaline equations "
                 "do not capture nonlinear releases of this kind"),
    }


# ─────────────────────────────────────────────
# OCEAN HEAT CONTENT
# ─────────────────────────────────────────────

def ocean_heat_content(delta_T, depth_m=700.0):
    """
    Change in ocean heat content for given temperature anomaly.
    Ocean absorbs ~93% of excess planetary heat.
    delta_T : temperature change (K)
    depth_m : layer depth (m)
    returns: heat content change (J/m^2)
    """
    return rho_seawater * cp_seawater * depth_m * delta_T


def ocean_thermal_inertia(depth_m=3700.0):
    """
    Timescale for ocean to equilibrate to surface forcing.
    Deep ocean equilibration: centuries to millennia.
    This is why committed warming exceeds current warming.
    depth_m : ocean depth for equilibration
    returns: e-folding timescale (years)
    """
    kappa_eddy = 1e-4    # m^2/s vertical eddy diffusivity
    tau_seconds = depth_m**2 / kappa_eddy
    return tau_seconds / (3.156e7)


def sea_surface_temperature_response(forcing_Wm2, lambda_feedback=-1.0):
    """
    Equilibrium SST change from radiative forcing.
    lambda_feedback : climate feedback parameter (W/m^2/K)
                      ~-1.0 W/m^2/K current best estimate
                      Less negative = more sensitive
    forcing_Wm2 : radiative forcing (W/m^2)
    returns: delta_T (K)
    """
    return -forcing_Wm2 / lambda_feedback


# ─────────────────────────────────────────────
# SEA ICE
# ─────────────────────────────────────────────

def ice_albedo_feedback(ice_fraction_change, T_ocean=271.0):
    """
    Albedo change from sea ice loss.
    Ice albedo ~0.85, open ocean ~0.06.
    Loss of ice exposes dark ocean — massive positive feedback.
    ice_fraction_change : change in ice cover fraction (negative = loss)
    T_ocean             : ocean temperature (K)
    returns: additional absorbed radiation (W/m^2)
    """
    alpha_ice   = 0.85
    alpha_ocean = 0.06
    S0 = 1361.0 / 4  # mean insolation
    delta_alpha = (alpha_ocean - alpha_ice) * ice_fraction_change
    return -S0 * delta_alpha  # positive when ice lost


def ice_thickness_growth(T_air, h_ice, snow_depth=0.0):
    """
    Stefan ice growth law — thermodynamic ice thickness change.
    T_air    : air temperature (°C, must be negative for growth)
    h_ice    : current ice thickness (m)
    snow_depth: insulating snow layer (m)
    returns: thickness change per day (m/day)
    """
    if T_air >= 0:
        return -0.01  # melt rate proxy
    kappa_eff = kappa_ice / (1 + snow_depth * kappa_ice / (kappa_water * 0.3))
    freezing_degree_days = abs(T_air)
    if h_ice <= 0:
        h_ice = 0.01
    return (kappa_eff * freezing_degree_days) / (L_f * rho_ice * h_ice * 86400)


def arctic_amplification_factor(delta_T_global):
    """
    Arctic warms 2-4x faster than global mean.
    Reduces pole-equator gradient — feeds back to layer 3 jet stream.
    delta_T_global : global mean temperature change (K)
    returns: Arctic temperature change (K)
    """
    amplification = 3.0  # observed range 2-4
    return delta_T_global * amplification


# ─────────────────────────────────────────────
# SEA LEVEL
# ─────────────────────────────────────────────

def thermal_expansion_sea_level(delta_T, depth_m=700.0):
    """
    Sea level rise from thermal expansion of upper ocean.
    delta_T : temperature change (K)
    depth_m : depth of warming layer
    returns: sea level rise (m)
    """
    return alpha_thermal * delta_T * depth_m


def ice_melt_sea_level(mass_Gt):
    """
    Sea level rise from land ice melt.
    Greenland + Antarctica + glaciers.
    mass_Gt : ice mass lost (Gigatonnes)
    returns: sea level rise (m)
    1 mm SLR ~ 362 Gt ice
    """
    return mass_Gt / (rho_freshwater * ocean_area / 1000)


def gravitational_sea_level_fingerprint(mass_loss_lat, mass_loss_lon,
                                         query_lat, query_lon, mass_Gt):
    """
    Gravitational fingerprint — sea level change is NOT uniform.
    Near melting ice sheets: sea level FALLS (gravity reduction).
    Far from ice sheets: sea level rises MORE than global mean.
    This is a physical constraint most policy discussions ignore.
    mass_loss_lat/lon : location of ice mass loss (degrees)
    query_lat/lon     : location of interest (degrees)
    mass_Gt           : ice mass lost (Gt)
    returns: local sea level change relative to global mean (fraction)
    Simplified — full computation requires geoid model
    """
    dlat = query_lat - mass_loss_lat
    dlon = query_lon - mass_loss_lon
    angular_distance = np.sqrt(dlat**2 + dlon**2)
    if angular_distance < 10:
        return -0.1  # near source — sea level falls
    elif angular_distance > 90:
        return 1.15  # far field — exceeds global mean
    else:
        return 1.0   # approximate global mean


# ─────────────────────────────────────────────
# FRESHWATER CYCLE
# ─────────────────────────────────────────────

def evaporation_rate(T_surface, wind_speed, RH=0.80):
    """
    Bulk formula for ocean evaporation.
    T_surface  : sea surface temperature (K)
    wind_speed : 10m wind speed (m/s)
    RH         : relative humidity (fraction)
    returns: evaporation rate (kg/m^2/s)
    """
    es   = saturation_vapor_pressure(T_surface)
    ea   = RH * saturation_vapor_pressure(T_surface - 2)
    C_E  = 1.5e-3  # bulk transfer coefficient
    rho_air = 1.2  # kg/m^3
    return rho_air * C_E * wind_speed * (0.622/101325.0) * (es - ea)


def river_discharge_sensitivity(delta_T, delta_precip_fraction,
                                 basin_area_m2, runoff_fraction=0.35):
    """
    River discharge change from temperature and precipitation shifts.
    Warmer atmosphere holds more moisture — intensifies both
    wet and dry extremes (thermodynamic effect).
    Circulation changes redistribute where rain falls (dynamic effect).
    delta_T                : temperature change (K)
    delta_precip_fraction  : precipitation change (fraction, +/-)
    basin_area_m2          : catchment area
    runoff_fraction        : fraction of precip becoming runoff
    returns: discharge change (m^3/s)
    """
    # Clausius-Clapeyron: ~7% more moisture per K
    moisture_amplification = 0.07 * delta_T
    total_precip_change    = delta_precip_fraction + moisture_amplification
    baseline_precip        = 1.0  # normalized
    return basin_area_m2 * baseline_precip * total_precip_change * runoff_fraction


# ─────────────────────────────────────────────
# OCEAN-ATMOSPHERE OSCILLATIONS
# ─────────────────────────────────────────────

def enso_feedback_strength(SST_anomaly_K):
    """
    El Niño/La Niña feedback — Bjerknes feedback loop.
    Warm SST -> weaker trades -> warmer SST (positive feedback).
    Critical system: small forcing -> large response -> global cascade.
    SST_anomaly_K : eastern Pacific SST anomaly (K)
    returns: wind stress feedback (Pa) and global precip redistribution proxy
    """
    bjerknes_factor = 0.8   # W/m^2 per K — approximate
    wind_feedback   = -0.02 * SST_anomaly_K  # Pa — weakening trades
    return {
        "wind_stress_change_Pa":     wind_feedback,
        "global_precip_shift":       SST_anomaly_K * 0.15,
        "drought_risk_indonesia":    SST_anomaly_K > 0.5,
        "flood_risk_peru":           SST_anomaly_K > 0.5,
        "cascade_to_atmosphere":     True,
        "cascade_to_biosphere":      True,
        "note": "ENSO is the dominant interannual climate signal globally"
    }


def atlantic_multidecadal_oscillation(phase, AMOC_strength_Sv):
    """
    AMO — multidecadal SST pattern linked to AMOC variability.
    Warm phase: enhanced hurricane activity, Sahel rainfall,
                European heat waves, Arctic sea ice loss.
    AMOC weakening shifts AMO toward cold phase — global cascade.
    phase           : 'warm' or 'cold'
    AMOC_strength_Sv: current AMOC transport (Sv)
    returns: regional impact summary
    """
    baseline_AMOC = 17.0  # Sv
    anomaly = (AMOC_strength_Sv - baseline_AMOC) / baseline_AMOC
    return {
        "AMOC_anomaly_fraction":     anomaly,
        "NE_USA_cooling_signal":     anomaly < -0.1,
        "European_warming_signal":   anomaly > 0.05,
        "hurricane_activity_proxy":  phase == "warm",
        "Sahel_drought_risk":        phase == "cold",
        "Arctic_ice_anomaly":        anomaly * (-0.5),
        "cascade_to_atmosphere":     True,
        "cascade_to_biosphere":      True,
    }


# ─────────────────────────────────────────────
# DISSOLVED OXYGEN — AQUATIC DEOXYGENATION
# Rose et al. 2024 (Nat Ecol Evol), Ferrer et al. 2026 (Limnol Oceanogr):
# dissolved oxygen decline is a planetary-boundary process in its own
# right. In this layer it is not an add-on: it falls straight out of the
# machinery already here. Bottom-water formation sets ventilation age,
# ventilation age sets interior oxygen, and surface temperature sets the
# saturation the parcel started from.
# ─────────────────────────────────────────────

def dissolved_oxygen_saturation(T_C, S=35.0):
    """
    Air-equilibrium dissolved oxygen (Garcia & Gordon 1992).
    T_C : water temperature (°C)
    S   : practical salinity (PSU)
    returns: dict with saturation in µmol/kg and mg/L
    """
    c = oxygen_solubility_umol_kg(T_C, S)
    return {
        "O2_sat_umol_kg": c,
        "O2_sat_mg_L":    umol_kg_to_mg_L(c),
    }


def hypoxic_volume_fraction(o2_interior_umol_kg, width_umol_kg=25.0):
    """
    Fraction of ocean volume below the 2 mg/L hypoxia threshold, from the
    mean interior oxygen concentration.

    The ocean interior is not uniform — a mean of 180 µmol/kg still has a
    tail of water below 62.5 µmol/kg. This maps mean to tail with a
    logistic whose width is the spread of the interior distribution:

        f = 1 / (1 + exp((O2_mean - O2_hypoxic) / width))

    Anchored so that a mean of ~160 µmol/kg returns ~2% of volume, which
    matches the present-day observed hypoxic fraction. It is a calibrated
    interpolation, not a first-principles result — the width parameter
    carries all the distributional physics.

    o2_interior_umol_kg : mean interior oxygen (µmol/kg)
    width_umol_kg       : spread of the interior O2 distribution (µmol/kg)
    returns: volume fraction below hypoxia (0-1)
    """
    o2_hypoxic = mg_L_to_umol_kg(HYPOXIA_MG_L)
    return 1.0 / (1.0 + np.exp((o2_interior_umol_kg - o2_hypoxic)
                               / max(width_umol_kg, 1e-6)))


def ocean_deoxygenation(T_outcrop_C, ventilation_age_yr, S=35.0,
                        OUR_umol_kg_yr=0.35,
                        remin_timescale_yr=500.0,
                        anoxic_area_fraction=0.02,
                        anoxic_volume_ratio_1960=None):
    """
    Ocean oxygen state from the thermohaline state already computed in
    this layer.

    Two independent forcings, both currently pushing the same direction:
      warming   -> lower saturation at the outcrop (solubility term, ~15%
                   of the observed global loss)
      slowdown  -> older interior water -> more accumulated respiration
                   (ventilation term, ~85%)

    T_outcrop_C              : temperature where the water last saw air
                                (deep-water formation region, °C)
    ventilation_age_yr       : mean interior ventilation age (yr), from
                                deep_water_ventilation_age()
    S                        : salinity (PSU)
    OUR_umol_kg_yr           : oxygen utilisation rate (µmol/kg/yr)
    remin_timescale_yr       : e-folding time of the parcel's respirable
                                carbon load (yr)
    anoxic_area_fraction     : sediment area under anoxic water (0-1)
    anoxic_volume_ratio_1960 : boundary control variable; None uses the
                                observed present-day value (4x)
    returns: dict of oxygen state, boundary status, and loop gain
    """
    o2_sat      = oxygen_solubility_umol_kg(T_outcrop_C, S)
    o2_interior = interior_oxygen_from_ventilation(
                      o2_sat, ventilation_age_yr,
                      OUR_umol_kg_yr, remin_timescale_yr)
    AOU         = o2_sat - o2_interior
    hv_frac     = hypoxic_volume_fraction(o2_interior)
    boundary    = deoxygenation_boundary_status(anoxic_volume_ratio_1960,
                                                hv_frac)
    feedback    = deoxygenation_feedback_gain(hv_frac, anoxic_area_fraction,
                                              o2_interior)
    phi         = metabolic_index(o2_interior, T_outcrop_C, S)
    return {
        "O2_sat_umol_kg":            o2_sat,
        "O2_sat_mg_L":               umol_kg_to_mg_L(o2_sat),
        "O2_interior_umol_kg":       o2_interior,
        "O2_interior_mg_L":          umol_kg_to_mg_L(o2_interior),
        "AOU_umol_kg":               AOU,
        "hypoxic_volume_fraction":   hv_frac,
        "hypoxic_expansion_ratio":   hv_frac / HYPOXIC_VOLUME_FRACTION_REFERENCE,
        "metabolic_index":           phi,
        "aerobic_habitat_viable":    phi >= 3.0,
        "anoxic_volume_ratio_1960":  boundary["control_value"],
        "deox_boundary_zone":        boundary["zone"],
        "deox_boundary_crossed":     boundary["crossed"],
        "deox_feedback_gain":        feedback["gain"],
        "n2o_yield_multiplier":      feedback["n2o_yield_multiplier"],
        "deox_loop_active":          (feedback["amplifying"] and
                                      hv_frac > HYPOXIC_VOLUME_FRACTION_REFERENCE),
        "deox_note": (
            "hypoxic fraction is derived from THIS layer's ventilation age. "
            "At BASELINE that age reflects an already-weakened bottom-water "
            "formation, so the fraction runs above the observed present-day "
            "~1.5% (aquatic_deoxygenation.HYPOXIC_VOLUME_FRACTION_PRESENT). "
            "Read it as the model's ventilation state, not as an observation."
        ),
    }


# ─────────────────────────────────────────────
# COUPLING INTERFACES
# ─────────────────────────────────────────────

def coupling_state(T_ocean_C, S_ocean, T_north_C, S_north,
                   T_south_C, S_south, ice_fraction,
                   wind_stress=0.1, delta_S_melt=0.0,
                   SST_enso_anomaly=0.0, AMOC_Sv=17.0,
                   cdw_heat_flux_TW=2.81,
                   cdw_baseline_TW=1.5,
                   cdw_sensitivity_Gt_per_TW=80.0,
                   cdw_aabw_shutdown_PSU=-0.05,
                   cdw_migration_km_yr=1.26,
                   O2_utilization_rate_umol_kg_yr=0.35,
                   O2_remin_timescale_yr=500.0,
                   anoxic_area_fraction=0.02,
                   anoxic_volume_ratio_1960=None):
    """
    Full hydrosphere state vector for adjacent layer consumption.
    T_ocean_C        : mean ocean surface temperature (°C)
    S_ocean          : mean salinity (PSU)
    T_north_C        : North Atlantic surface T (°C)
    S_north          : North Atlantic salinity (PSU)
    T_south_C        : equatorial Atlantic T (°C)
    S_south          : equatorial salinity (PSU)
    ice_fraction     : current sea ice fraction of Arctic (0-1)
    wind_stress      : surface wind stress (Pa)
    delta_S_melt     : salinity reduction from meltwater (PSU)
    SST_enso_anomaly : ENSO SST anomaly (K)
    AMOC_Sv          : AMOC transport (Sv)
    cdw_heat_flux_TW          : poleward CDW heat into the 60-65 S
                                 band (TW). Default 2.81 = Lanham 2026.
    cdw_baseline_TW           : pre-2000 reference CDW heat flux (TW).
    cdw_sensitivity_Gt_per_TW : differential melt sensitivity to CDW
                                 excess (Gt/yr per TW; literature 50-100).
    cdw_aabw_shutdown_PSU     : freshwater anomaly scale for AABW
                                 suppression (PSU; default -0.05).
    cdw_migration_km_yr       : circumpolar mean CDW poleward migration
                                 (default 1.26 km/yr from Lanham 2026;
                                 95% CI 0.53-1.98).
    O2_utilization_rate_umol_kg_yr : interior oxygen utilisation rate
                                 (µmol/kg/yr).
    O2_remin_timescale_yr     : e-folding time of a ventilated parcel's
                                 respirable carbon load (yr).
    anoxic_area_fraction      : fraction of sediment area under anoxic
                                 bottom water (drives internal P loading).
    anoxic_volume_ratio_1960  : deoxygenation boundary control variable —
                                 anoxic water volume as a multiple of
                                 1960. None uses the observed value (4x).
    """
    density         = seawater_density(T_ocean_C, S_ocean)
    AMOC_gradient   = atlantic_overturning_index(T_north_C, S_north,
                                                  T_south_C, S_south)
    AMOC_risk       = amoc_freshwater_sensitivity(delta_S_melt, AMOC_gradient)
    heat_transport  = thermohaline_heat_transport(AMOC_Sv, T_south_C - T_north_C)
    OHC             = ocean_heat_content(T_ocean_C - 14.0)
    SLR_thermal     = thermal_expansion_sea_level(T_ocean_C - 14.0)
    ice_feedback    = ice_albedo_feedback(-0.1 * (T_ocean_C - 14.0))
    arctic_T        = arctic_amplification_factor(T_ocean_C - 14.0)
    enso            = enso_feedback_strength(SST_enso_anomaly)
    AMO             = atlantic_multidecadal_oscillation("warm", AMOC_Sv)
    inertia_yrs     = ocean_thermal_inertia()

    # Explicit AMOC state variables (2024–2026 update)
    amoc_30N     = amoc_density_gradient_30N(T_north_C, S_north)
    amoc_fw_sens = amoc_freshwater_input_sensitivity(amoc_30N["density_gradient_30N_kgm3"])
    amoc_front   = amoc_salinity_front_position(S_north)
    amoc_phase   = amoc_phase_transition_check(amoc_30N["density_gradient_30N_kgm3"])

    # Bottom water formation — the engine driving thermohaline circulation
    # Ice formation rate scales inversely with ice fraction loss
    ice_formation_rate = max(0, ice_fraction * 0.8)  # m/yr, scales with ice extent
    bw = bottom_water_formation_rate(
        T_north_C, S_north, delta_S_melt,
        ice_formation_rate_m_yr=ice_formation_rate,
    )
    ventilation_yrs = deep_water_ventilation_age(bw["total_bottom_water_Sv"])

    # AMOC computed from bottom water formation (overrides input when formation active)
    AMOC_computed_Sv = bw["NADW_formation_Sv"] + bw["AABW_formation_Sv"] * 0.3  # AABW contributes ~30% to AMOC

    # Southern Ocean CDW -> basal melt -> AABW suppression positive feedback
    cdw_loop = cdw_aabw_feedback_index(cdw_heat_flux_TW,
                                       cdw_baseline_TW,
                                       cdw_sensitivity_Gt_per_TW,
                                       cdw_aabw_shutdown_PSU)

    # Dissolved oxygen — outcrop temperature is the deep-water formation
    # region, ventilation age comes from bottom-water formation above.
    deox = ocean_deoxygenation(
        T_outcrop_C              = T_north_C,
        ventilation_age_yr       = ventilation_yrs,
        S                        = S_north,
        OUR_umol_kg_yr           = O2_utilization_rate_umol_kg_yr,
        remin_timescale_yr       = O2_remin_timescale_yr,
        anoxic_area_fraction     = anoxic_area_fraction,
        anoxic_volume_ratio_1960 = anoxic_volume_ratio_1960,
    )

    return {
        "ocean_density_kgm3":            density,
        "AMOC_density_gradient":         AMOC_gradient,
        "AMOC_collapse_risk":            AMOC_risk["collapse_risk"],
        "AMOC_heat_transport_W":         heat_transport,
        "AMOC_Sv":                       AMOC_computed_Sv,
        "ocean_heat_content_Jm2":        OHC,
        "thermal_SLR_m":                 SLR_thermal,
        "ice_albedo_feedback_Wm2":       ice_feedback,
        "arctic_amplification_K":        arctic_T,
        "ENSO_state":                    enso,
        "AMO_state":                     AMO,
        "committed_warming_timescale_yr":inertia_yrs,
        # Bottom water formation
        "NADW_formation_Sv":             bw["NADW_formation_Sv"],
        "AABW_formation_Sv":             bw["AABW_formation_Sv"],
        "total_bottom_water_Sv":         bw["total_bottom_water_Sv"],
        "deep_convection_active":        bw["convection_active"],
        "brine_density_flux_kgm3":       bw["brine_contribution_kgm3"],
        "meltwater_to_shutdown_PSU":     bw["meltwater_to_shutdown_PSU"],
        "deep_water_ventilation_yr":     ventilation_yrs,
        # Southern Ocean CDW / AABW positive feedback (Lanham 2026)
        "cdw_heat_flux_TW":              cdw_heat_flux_TW,
        "cdw_migration_km_yr":           cdw_migration_km_yr,
        "cdw_basal_melt_Gt_yr":          cdw_loop["basal_melt_Gt_yr"],
        "cdw_freshwater_PSU_anomaly":    cdw_loop["freshwater_PSU_anomaly"],
        "aabw_suppression_factor":       cdw_loop["aabw_suppression_factor"],
        "cdw_aabw_feedback_index":       cdw_loop["cdw_aabw_feedback_index"],
        "cdw_aabw_loop_active":          cdw_loop["loop_active"],
        # Aquatic deoxygenation — proposed 10th planetary boundary
        # (Rose et al. 2024; Ferrer et al. 2026)
        "O2_sat_umol_kg":                deox["O2_sat_umol_kg"],
        "O2_sat_mg_L":                   deox["O2_sat_mg_L"],
        "O2_interior_umol_kg":           deox["O2_interior_umol_kg"],
        "O2_interior_mg_L":              deox["O2_interior_mg_L"],
        "AOU_umol_kg":                   deox["AOU_umol_kg"],
        "hypoxic_volume_fraction":       deox["hypoxic_volume_fraction"],
        "hypoxic_expansion_ratio":       deox["hypoxic_expansion_ratio"],
        "metabolic_index":               deox["metabolic_index"],
        "aerobic_habitat_viable":        deox["aerobic_habitat_viable"],
        "anoxic_volume_ratio_1960":      deox["anoxic_volume_ratio_1960"],
        "deox_boundary_zone":            deox["deox_boundary_zone"],
        "deox_boundary_crossed":         deox["deox_boundary_crossed"],
        "deox_feedback_gain":            deox["deox_feedback_gain"],
        "n2o_yield_multiplier":          deox["n2o_yield_multiplier"],
        "deox_loop_active":              deox["deox_loop_active"],
        "deox_note":                     deox["deox_note"],
        # Cascade metadata
        "cascade_to_atmosphere":         "SST, evaporation, ENSO, AMO, ITCZ, N2O from suboxic water",
        "cascade_to_lithosphere":        "sea level loading, isostasy, pore pressure",
        "cascade_to_biosphere":          "temperature, acidification, stratification, deep ocean ventilation, dissolved oxygen",
        "cascade_from_atmosphere":       "wind stress, heat flux, freshwater",
        "cascade_from_cryosphere":       "meltwater, albedo, freshwater pulse",
        "cascade_internal_loop":         "CDW heat -> basal melt -> freshwater cap -> AABW suppression -> reduced cold buffer -> more CDW",
        # Explicit AMOC state variables (2024–2026 update)
        "amoc_density_gradient_30N_kgm3": amoc_30N["density_gradient_30N_kgm3"],
        "amoc_above_critical_threshold":  amoc_30N["above_critical_threshold"],
        "amoc_fw_sensitivity_kgm3_PSU":   amoc_fw_sens["sensitivity_kgm3_per_PSU"],
        "amoc_PSU_to_threshold":          amoc_fw_sens["PSU_to_threshold"],
        "amoc_salinity_front_lat_N":      amoc_front["salinity_front_lat_N"],
        "amoc_front_shift_deg":           amoc_front["front_shift_deg"],
        "amoc_regime_shift_imminent":     amoc_phase["regime_shift_imminent"],
        "amoc_coupling_coeffs_valid":     amoc_phase["coupling_coefficients_valid"],
        "hard_threshold": "AMOC collapse — irreversible; bottom water formation shutdown; CDW-AABW feedback nonlinear",
        "note": "ocean thermal inertia means current forcing is not yet fully expressed"
    }
