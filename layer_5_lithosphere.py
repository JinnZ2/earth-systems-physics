# layer_5_lithosphere.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Lithosphere constraint layer.
# Governs crustal mechanics, isostatic adjustment, seismic stress,
# volcanic forcing, rotational coupling, and mantle dynamics.
# The solid Earth is not static — it responds to every other layer
# on timescales from seconds to millions of years.
# Imports constraints from layers 0-4.

import numpy as np
from scipy.constants import g
from layer_1_magnetosphere import rotation_rate_to_field_drift
from layer_4_hydrosphere import (
    ice_melt_sea_level,
    ocean_heat_content,
    thermal_expansion_sea_level,
)

# ─────────────────────────────────────────────
# FUNDAMENTAL CONSTANTS — LITHOSPHERE
# ─────────────────────────────────────────────

g_earth          = 9.80665      # m/s^2
R_E              = 6.371e6      # m
rho_crust        = 2800.0       # kg/m^3 continental crust
rho_mantle       = 3300.0       # kg/m^3 upper mantle
rho_water        = 1025.0       # kg/m^3 seawater
rho_ice          = 917.0        # kg/m^3
E_young          = 70e9         # Pa Young's modulus continental crust
nu_poisson       = 0.25         # Poisson's ratio
mu_rigidity      = 3e10         # Pa shear modulus crust
eta_mantle       = 1e21         # Pa·s mantle viscosity (upper)
eta_asthenosphere= 1e19         # Pa·s asthenosphere viscosity

# ─────────────────────────────────────────────
# ISOSTASY — SURFACE LOAD RESPONSE
# ─────────────────────────────────────────────

def isostatic_depression(load_thickness, load_density=917.0):
    """
    Crustal depression under surface load (ice, water, sediment).
    Archimedes principle applied to crust floating on mantle.
    load_thickness : thickness of load (m)
    load_density   : density of load (kg/m^3)
    returns: depression depth (m)
    Ice sheet: ~1/3 thickness depression
    """
    return load_thickness * (load_density / rho_mantle)


def glacial_isostatic_adjustment_rate(ice_mass_change_Gt, elapsed_years):
    """
    Rate of crustal rebound/subsidence from ice mass change.
    Mantle viscosity governs timescale — centuries to millennia lag.
    Current Scandinavia/Canada still rebounding from last glacial maximum.
    New suppression from modern ice loss creates new signal on top.
    ice_mass_change_Gt : mass change (Gt, negative = loss)
    elapsed_years      : time since load change
    returns: rebound rate (mm/year)
    """
    # Maxwell relaxation time ~ eta / mu
    tau_maxwell = eta_mantle / mu_rigidity  # ~1000 years
    tau_years   = tau_maxwell / 3.156e7
    # Exponential relaxation
    total_rebound_mm = (ice_mass_change_Gt / 1e6) * 1000 * (rho_ice / rho_mantle)
    rate = (total_rebound_mm / tau_years) * np.exp(-elapsed_years / tau_years)
    return rate


def sea_level_load_crustal_stress(delta_SLR_m, lithosphere_thickness=100e3):
    """
    Stress on continental margins from sea level loading.
    Sea level rise adds water load on continental shelves.
    Redistributes stress — can trigger shelf sediment failure,
    submarine landslides, and potentially influence fault systems.
    delta_SLR_m           : sea level change (m)
    lithosphere_thickness : elastic thickness (m)
    returns: stress change (Pa)
    """
    load_pressure = rho_water * g_earth * delta_SLR_m
    # Flexural stress in plate — simplified
    stress = load_pressure * (R_E / lithosphere_thickness)
    return stress


def elastic_rebound_stress(load_change_Pa, depth_m):
    """
    Elastic stress change from surface load redistribution.
    Relevant for fault stability — Coulomb stress change.
    load_change_Pa : change in surface pressure (Pa)
    depth_m        : depth of interest (m)
    returns: stress change at depth (Pa)
    """
    # Boussinesq solution — stress decays with depth
    return load_change_Pa * (1 / (1 + (depth_m / 1000)**2))


# ─────────────────────────────────────────────
# FAULT MECHANICS
# ─────────────────────────────────────────────

def coulomb_stress_change(delta_shear, delta_normal, friction=0.6, B=0.5):
    """
    Coulomb Failure Function change.
    Positive delta_CFF brings fault closer to failure.
    Negative delta_CFF stabilizes fault.
    delta_shear  : shear stress change on fault (Pa)
    delta_normal : normal stress change on fault (Pa, compression positive)
    friction     : coefficient of friction (~0.6 Byerlee's law)
    B            : Skempton's coefficient (pore pressure coupling)
    returns: delta_CFF (Pa)
    """
    delta_pore = -B * delta_normal
    return delta_shear - friction * (delta_normal + delta_pore)


def fault_slip_rate(driving_stress, friction, cohesion=1e6):
    """
    Approximate fault slip rate from driving stress.
    driving_stress : tectonic stress (Pa)
    friction       : fault friction coefficient
    cohesion       : fault cohesion (Pa)
    returns: normalized slip tendency (0-1)
    """
    strength = cohesion + friction * driving_stress
    if strength <= 0:
        return 1.0
    tendency = driving_stress / strength
    return min(1.0, max(0.0, tendency))


def reservoir_induced_seismicity(water_depth_change_m, reservoir_area_m2,
                                  depth_to_fault_m, friction=0.6):
    """
    Seismic hazard change from water reservoir loading.
    Applies equally to sea level change over continental shelves.
    Pore pressure diffusion timescale governs when fault feels loading.
    water_depth_change_m : change in water column height (m)
    reservoir_area_m2    : area of loading (m^2)
    depth_to_fault_m     : fault depth (m)
    returns: Coulomb stress change estimate (Pa) and pore diffusion time (years)
    """
    load_Pa   = rho_water * g_earth * water_depth_change_m
    delta_CFF = coulomb_stress_change(
        delta_shear  = load_Pa * 0.3,
        delta_normal = load_Pa * 0.7,
        friction     = friction
    )
    # Pore pressure diffusion timescale
    hydraulic_diffusivity = 1e-2  # m^2/s typical crustal rock
    tau_pore = depth_to_fault_m**2 / hydraulic_diffusivity
    tau_years = tau_pore / 3.156e7
    return {
        "coulomb_stress_change_Pa": delta_CFF,
        "pore_diffusion_years":     tau_years,
        "failure_tendency":         fault_slip_rate(load_Pa, friction),
        "note": "sea level rise loads continental shelves — same physics as reservoirs"
    }


# ─────────────────────────────────────────────
# EARTH ROTATION COUPLING
# ─────────────────────────────────────────────

def length_of_day_change(delta_I):
    """
    Change in length of day from moment of inertia change.
    Angular momentum conserved: I * omega = constant
    Mass redistribution (ice melt, sea level) changes I -> changes omega.
    delta_I : change in moment of inertia (kg·m^2)
    returns: change in length of day (seconds)
    """
    I_earth = 8.04e37   # kg·m^2 Earth moment of inertia
    omega   = 7.2921e-5  # rad/s
    LOD     = 86400.0    # seconds
    delta_omega = -omega * delta_I / I_earth
    return -LOD**2 * delta_omega / (2 * np.pi)


def ice_melt_LOD_change(mass_Gt, lat_deg, lon_deg):
    """
    Change in LOD from ice mass redistribution to ocean.
    Moving mass from polar ice sheets to equatorial ocean
    increases moment of inertia -> slows rotation -> longer day.
    Couples to magnetosphere (layer 1) and atmosphere Coriolis (layer 3).
    mass_Gt  : ice mass lost (Gt = 1e12 kg)
    lat_deg  : latitude of ice source
    lon_deg  : longitude of ice source
    returns: LOD change (milliseconds) and omega change (rad/s)
    """
    mass_kg  = mass_Gt * 1e12
    lat_rad  = np.radians(lat_deg)
    # Ice location contribution to moment of inertia
    r_ice    = R_E * np.cos(lat_rad)
    delta_I_ice = -mass_kg * r_ice**2  # removing from ice
    # Redistributed to ocean — approximate equatorial spread
    r_ocean  = R_E * np.cos(np.radians(20.0))  # ~20 deg mean ocean lat
    delta_I_ocean = mass_kg * r_ocean**2
    delta_I  = delta_I_ice + delta_I_ocean
    LOD_ms   = length_of_day_change(delta_I) * 1000
    I_earth  = 8.04e37
    omega    = 7.2921e-5
    delta_omega = -omega * delta_I / I_earth
    return {
        "LOD_change_ms":    LOD_ms,
        "omega_change_rads":delta_omega,
        "cascade_to_magnetosphere": True,
        "cascade_to_atmosphere_coriolis": True,
        "note": "Greenland melt LOD signal already measurable — ~1ms/century"
    }


def polar_wander_velocity(mass_redistribution_events):
    """
    True polar wander — rotation axis shifts as mass redistributes.
    Climate-driven ice melt is currently causing measurable polar drift.
    mass_redistribution_events : list of (mass_Gt, lat, lon) tuples
    returns: polar drift direction and rate (degrees/year)
    """
    # Simplified — full computation requires degree-2 geoid coefficients
    total_I_change = 0.0
    for mass_Gt, lat, lon in mass_redistribution_events:
        mass_kg = mass_Gt * 1e12
        lat_rad = np.radians(lat)
        total_I_change += mass_kg * R_E**2 * np.cos(lat_rad)
    I_earth = 8.04e37
    drift_rate_deg_yr = abs(total_I_change) / I_earth * (180/np.pi) * 3.156e7
    return {
        "polar_drift_deg_yr": drift_rate_deg_yr,
        "observation": "GPS polar position shift matches ice melt signal",
        "cascade_to_crust": "changing load distribution alters crustal stress field"
    }


# ─────────────────────────────────────────────
# VOLCANIC FORCING
# ─────────────────────────────────────────────

def volcanic_radiative_forcing(SO2_Tg, injection_altitude_km):
    """
    Stratospheric aerosol forcing from volcanic SO2 injection.
    SO2 -> H2SO4 aerosols -> scatter solar radiation -> cooling.
    This is the natural analog to proposed solar geoengineering.
    SO2_Tg              : sulfur dioxide mass (Teragram)
    injection_altitude_km: injection altitude — must reach stratosphere
    returns: peak forcing (W/m^2) and duration estimate (years)
    Pinatubo 1991: ~20 Tg SO2, ~-3 W/m^2 peak, ~2 year duration
    """
    if injection_altitude_km < 15:
        return {"forcing_Wm2": 0.0, "duration_years": 0,
                "note": "tropospheric injection — rained out too fast"}
    forcing = -0.15 * SO2_Tg
    duration = 1.0 + SO2_Tg / 20.0
    return {
        "peak_forcing_Wm2": forcing,
        "duration_years":   duration,
        "SO2_Tg":           SO2_Tg,
        "cascade_to_atmosphere": True,
        "cascade_to_biosphere":  "reduced photosynthesis during high-AOD period",
        "note": "does not address ocean acidification — treats symptom not cause"
    }


def deglaciation_volcanic_coupling(ice_mass_loss_Gt_per_yr):
    """
    Unloading of ice increases volcanic and seismic activity.
    Reduced lithostatic pressure allows magma ascent.
    Iceland post-glacial eruption rate was 30-50x higher.
    Current ice loss is beginning to reproduce this signal.
    ice_mass_loss_Gt_per_yr : current melt rate
    returns: volcanic activity enhancement proxy
    """
    baseline_loss = 500.0  # Gt/yr — approximate current global
    enhancement   = ice_mass_loss_Gt_per_yr / baseline_loss
    return {
        "volcanic_activity_enhancement": enhancement,
        "seismic_activity_enhancement":  enhancement * 0.5,
        "primary_regions": ["Iceland", "West Antarctica", "Alaska", "Andes"],
        "timescale": "decades to centuries — pressure diffusion limited",
        "cascade_to_atmosphere": "SO2, CO2 from enhanced volcanism",
        "note": "ice loss -> volcanic enhancement -> atmospheric forcing -> more ice loss"
    }


# ─────────────────────────────────────────────
# MANTLE DYNAMICS
# ─────────────────────────────────────────────

def mantle_convection_velocity(delta_T_mantle, depth_m=660e3):
    """
    Approximate mantle convection velocity from thermal buoyancy.
    Drives plate tectonics on geological timescales.
    Climate perturbations too fast for mantle response —
    but mantle state sets baseline stress field plates move within.
    delta_T_mantle : temperature anomaly in mantle (K)
    depth_m        : convection depth scale
    returns: convection velocity (m/year)
    """
    alpha_mantle = 3e-5   # 1/K thermal expansion
    kappa_mantle = 1e-6   # m^2/s thermal diffusivity
    g_buoyancy   = g_earth * alpha_mantle * delta_T_mantle
    Ra_proxy     = g_buoyancy * depth_m**3 / (kappa_mantle * eta_mantle / rho_mantle)
    v_ms = kappa_mantle / depth_m * Ra_proxy**(1/3) * 0.1
    return v_ms * 3.156e7  # m/year


def tectonic_co2_outgassing(spreading_rate_km_yr, arc_length_km):
    """
    Geological CO2 from mid-ocean ridges and volcanic arcs.
    Long-term carbon cycle baseline — sets pCO2 over millions of years.
    Perturbations to spreading rate from rotation changes are negligible
    on human timescales but set the geological context.
    spreading_rate_km_yr : plate spreading rate
    arc_length_km        : total arc/ridge length
    returns: CO2 flux (Gt C/year)
    Current geological outgassing ~0.1-0.4 Gt C/year
    vs anthropogenic ~10 Gt C/year — human signal 25-100x geological
    """
    flux_per_km = 2e-5  # Gt C / year / km ridge — approximate
    return spreading_rate_km_yr * arc_length_km * flux_per_km


# ─────────────────────────────────────────────
# COUPLING INTERFACES
# ─────────────────────────────────────────────

def coupling_state(ice_mass_loss_Gt, SLR_m, T_ocean_C,
                   lat_ice=71.0, lon_ice=-40.0,
                   fault_depth_m=10e3, SO2_volcanic_Tg=0.0):
    """
    Full lithosphere state vector for adjacent layer consumption.
    ice_mass_loss_Gt : cumulative land ice loss (Gt)
    SLR_m            : sea level rise (m)
    T_ocean_C        : ocean temperature for thermal load (°C)
    lat_ice/lon_ice  : primary ice source location (Greenland default)
    fault_depth_m    : representative fault system depth (m)
    SO2_volcanic_Tg  : volcanic SO2 injection (Tg)
    """
    GIA_rate       = glacial_isostatic_adjustment_rate(ice_mass_loss_Gt, 100)
    shelf_stress   = sea_level_load_crustal_stress(SLR_m)
    reservoir_seis = reservoir_induced_seismicity(SLR_m, 1e13, fault_depth_m)
    LOD            = ice_melt_LOD_change(ice_mass_loss_Gt, lat_ice, lon_ice)
    polar_drift    = polar_wander_velocity([(ice_mass_loss_Gt, lat_ice, lon_ice)])
    deglac_volc    = deglaciation_volcanic_coupling(ice_mass_loss_Gt / 100)
    volc_forcing   = volcanic_radiative_forcing(SO2_volcanic_Tg, 20.0)
    geo_co2        = tectonic_co2_outgassing(5.0, 60000)

    return {
        "GIA_rebound_rate_mm_yr":        GIA_rate,
        "shelf_stress_Pa":               shelf_stress,
        "fault_coulomb_change_Pa":       reservoir_seis["coulomb_stress_change_Pa"],
        "pore_pressure_diffusion_yr":    reservoir_seis["pore_diffusion_years"],
        "LOD_change_ms":                 LOD["LOD_change_ms"],
        "omega_change_rads":             LOD["omega_change_rads"],
        "polar_drift_deg_yr":            polar_drift["polar_drift_deg_yr"],
        "volcanic_enhancement":          deglac_volc["volcanic_activity_enhancement"],
        "volcanic_forcing_Wm2":          volc_forcing.get("peak_forcing_Wm2", 0),
        "geological_co2_GtC_yr":         geo_co2,
        "cascade_to_magnetosphere":      "LOD change -> core coupling -> field geometry",
        "cascade_to_atmosphere":         "volcanic SO2, CO2 outgassing, dust",
        "cascade_to_hydrosphere":        "isostasy changes basin geometry, SLR feedbacks",
        "cascade_to_biosphere":          "volcanic nutrients, soil formation, habitat change",
        "cascade_from_hydrosphere":      "ice load, sea level, pore pressure",
        "hard_threshold": "deglaciation volcanic feedback — self-amplifying once triggered",
        "note": "solid Earth responds to climate forcing — it is not a static boundary"
    }
