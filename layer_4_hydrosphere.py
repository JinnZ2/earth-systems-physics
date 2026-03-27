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
# COUPLING INTERFACES
# ─────────────────────────────────────────────

def coupling_state(T_ocean_C, S_ocean, T_north_C, S_north,
                   T_south_C, S_south, ice_fraction,
                   wind_stress=0.1, delta_S_melt=0.0,
                   SST_enso_anomaly=0.0, AMOC_Sv=17.0):
    """
    Full hydrosphere state vector for adjacent layer consumption.
    T_ocean_C       : mean ocean surface temperature (°C)
    S_ocean         : mean salinity (PSU)
    T_north_C       : North Atlantic surface T (°C)
    S_north         : North Atlantic salinity (PSU)
    T_south_C       : equatorial Atlantic T (°C)
    S_south         : equatorial salinity (PSU)
    ice_fraction    : current sea ice fraction of Arctic (0-1)
    wind_stress     : surface wind stress (Pa)
    delta_S_melt    : salinity reduction from meltwater (PSU)
    SST_enso_anomaly: ENSO SST anomaly (K)
    AMOC_Sv         : AMOC transport (Sv)
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
        # Cascade metadata
        "cascade_to_atmosphere":         "SST, evaporation, ENSO, AMO, ITCZ",
        "cascade_to_lithosphere":        "sea level loading, isostasy, pore pressure",
        "cascade_to_biosphere":          "temperature, acidification, stratification",
        "cascade_from_atmosphere":       "wind stress, heat flux, freshwater",
        "cascade_from_cryosphere":       "meltwater, albedo, freshwater pulse",
        "hard_threshold": "AMOC collapse — irreversible; bottom water formation shutdown",
        "note": "ocean thermal inertia means current forcing is not yet fully expressed"
    }
