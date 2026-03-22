# layer_3_atmosphere.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Atmosphere constraint layer.
# Governs thermodynamic state, radiative transfer, fluid dynamics,
# chemical composition, and energy transport.
# This is where climate models live — but here it is one layer
# in a coupled stack, not the whole system.
# Imports constraints from layers 0, 1, 2.

import numpy as np
from scipy.constants import k, R, g, Stefan_Boltzmann
from layer_0_electromagnetics import poynting_vector, electric_energy_density
from layer_2_ionosphere import (
    joule_heating,
    gravity_wave_ionospheric_signature,
    schumann_resonances,
)

# ─────────────────────────────────────────────
# FUNDAMENTAL CONSTANTS — ATMOSPHERIC
# ─────────────────────────────────────────────

R_dry    = 287.05   # J/(kg·K) — specific gas constant dry air
R_vapor  = 461.5    # J/(kg·K) — specific gas constant water vapor
cp_dry   = 1005.0   # J/(kg·K) — specific heat dry air constant pressure
cv_dry   = 718.0    # J/(kg·K) — specific heat dry air constant volume
gamma    = cp_dry / cv_dry  # adiabatic index ~1.4
L_v      = 2.501e6  # J/kg — latent heat vaporization at 0°C
L_f      = 3.337e5  # J/kg — latent heat fusion
L_s      = 2.834e6  # J/kg — latent heat sublimation
g_earth  = 9.80665  # m/s^2
R_E      = 6.371e6  # m

# ─────────────────────────────────────────────
# THERMODYNAMIC STATE
# ─────────────────────────────────────────────

def potential_temperature(T, P, P0=1e5):
    """
    Potential temperature — temperature parcel would have at reference pressure.
    Conserved for dry adiabatic processes. Fundamental state variable.
    T  : temperature (K)
    P  : pressure (Pa)
    P0 : reference pressure (Pa), default 100 kPa
    returns: theta (K)
    """
    return T * (P0 / P) ** (R_dry / cp_dry)


def virtual_temperature(T, q):
    """
    Virtual temperature — accounts for water vapor buoyancy effect.
    q : specific humidity (kg/kg)
    returns: Tv (K)
    """
    return T * (1 + 0.608 * q)


def dry_adiabatic_lapse_rate():
    """
    Temperature decrease with altitude for dry adiabatic ascent.
    ~9.8 K/km
    returns: DALR (K/m)
    """
    return g_earth / cp_dry


def moist_adiabatic_lapse_rate(T, P):
    """
    Temperature decrease with altitude for saturated adiabatic ascent.
    Less than DALR due to latent heat release.
    T : temperature (K)
    P : pressure (Pa)
    returns: MALR (K/m) — approximate
    """
    es = saturation_vapor_pressure(T)
    ws = 0.622 * es / (P - es)  # saturation mixing ratio
    numerator   = g_earth * (1 + (L_v * ws) / (R_dry * T))
    denominator = cp_dry + (L_v**2 * ws) / (R_vapor * T**2)
    return numerator / denominator


def static_stability(dtheta_dz):
    """
    Atmospheric stability from potential temperature gradient.
    dtheta_dz > 0 : stable   (resists vertical motion)
    dtheta_dz = 0 : neutral
    dtheta_dz < 0 : unstable (convection initiates)
    returns: stability classification
    """
    if dtheta_dz > 1e-4:
        return {"class": "stable",   "N2": dtheta_dz * g_earth, "convection": False}
    elif dtheta_dz < -1e-4:
        return {"class": "unstable", "N2": dtheta_dz * g_earth, "convection": True}
    else:
        return {"class": "neutral",  "N2": 0.0,                 "convection": "marginal"}


def brunt_vaisala_frequency(dtheta_dz, theta):
    """
    Buoyancy oscillation frequency — governs gravity wave propagation.
    Gravity waves carry energy from troposphere to ionosphere (layer 2 coupling).
    dtheta_dz : vertical gradient of potential temperature (K/m)
    theta     : local potential temperature (K)
    returns: N (rad/s), imaginary if unstable
    """
    N2 = (g_earth / theta) * dtheta_dz
    if N2 >= 0:
        return np.sqrt(N2)
    else:
        return 1j * np.sqrt(abs(N2))  # imaginary = convective instability


# ─────────────────────────────────────────────
# HYDROSTATICS AND PRESSURE
# ─────────────────────────────────────────────

def hydrostatic_pressure(P0, rho, dz):
    """
    Pressure change with altitude.
    dP/dz = -rho * g
    P0  : surface pressure (Pa)
    rho : air density (kg/m^3)
    dz  : altitude increment (m)
    returns: pressure at altitude (Pa)
    """
    return P0 - rho * g_earth * dz


def scale_height(T, molecular_mass=0.029):
    """
    Altitude over which pressure drops by factor e.
    T              : temperature (K)
    molecular_mass : kg/mol (dry air ~0.029)
    returns: H (m)
    """
    from scipy.constants import N_A
    m = molecular_mass / N_A  # kg per molecule
    return (k * T) / (m * g_earth)


def pressure_altitude(P, T_mean=255.0):
    """
    Altitude from pressure using scale height approximation.
    P      : pressure (Pa)
    T_mean : mean atmospheric temperature (K)
    returns: altitude (m)
    """
    P0 = 101325.0
    H  = scale_height(T_mean)
    return -H * np.log(P / P0)


# ─────────────────────────────────────────────
# RADIATIVE TRANSFER
# ─────────────────────────────────────────────

def planck_emission(T, wavelength):
    """
    Blackbody spectral radiance.
    T          : temperature (K)
    wavelength : meters
    returns: spectral radiance (W/m^2/sr/m)
    """
    from scipy.constants import h, c
    return (2 * h * c**2 / wavelength**5) / (
        np.exp(h * c / (wavelength * k * T)) - 1
    )


def stefan_boltzmann_flux(T, emissivity=1.0):
    """
    Total radiative power per unit area.
    T          : temperature (K)
    emissivity : 0-1
    returns: flux (W/m^2)
    """
    return emissivity * Stefan_Boltzmann * T**4


def effective_radiating_temperature(albedo=0.30, solar_constant=1361.0):
    """
    Earth's effective temperature from radiative balance.
    The number climate models anchor to.
    albedo         : planetary albedo (fraction reflected)
    solar_constant : W/m^2
    returns: T_eff (K) ~255 K without greenhouse, ~288 K observed
    """
    absorbed = solar_constant * (1 - albedo) / 4
    return (absorbed / Stefan_Boltzmann) ** 0.25


def greenhouse_forcing(delta_CO2_ppm, baseline_ppm=280.0):
    """
    Radiative forcing from CO2 increase.
    Logarithmic relationship — each doubling adds ~3.7 W/m^2.
    delta_CO2_ppm : increase above baseline (ppm)
    baseline_ppm  : pre-industrial baseline
    returns: forcing (W/m^2)
    """
    current = baseline_ppm + delta_CO2_ppm
    return 5.35 * np.log(current / baseline_ppm)


def optical_depth(absorption_coeff, density, path_length):
    """
    Measure of atmospheric opacity.
    tau > 1 : optically thick (radiation trapped)
    tau < 1 : optically thin (radiation escapes)
    returns: tau (dimensionless)
    """
    return absorption_coeff * density * path_length


# ─────────────────────────────────────────────
# FLUID DYNAMICS — CIRCULATION
# ─────────────────────────────────────────────

def coriolis_parameter(latitude_deg):
    """
    Coriolis parameter f — governs large-scale rotation of wind systems.
    Depends on Earth's rotation rate.
    Climate-driven LOD change modifies this — slow cascade from layer 1.
    latitude_deg : degrees
    returns: f (rad/s)
    """
    omega = 7.2921e-5  # Earth rotation rate (rad/s)
    lat   = np.radians(latitude_deg)
    return 2 * omega * np.sin(lat)


def coriolis_parameter_perturbed(latitude_deg, delta_omega):
    """
    Coriolis parameter with rotation rate perturbation.
    Connects layer 1 rotation coupling to atmospheric dynamics.
    delta_omega : change in Earth angular velocity (rad/s)
    returns: perturbed f (rad/s)
    """
    omega = 7.2921e-5 + delta_omega
    lat   = np.radians(latitude_deg)
    return 2 * omega * np.sin(lat)


def rossby_radius(N, H, f):
    """
    Length scale where rotation and buoyancy balance.
    Governs size of weather systems and jet stream meanders.
    N : Brunt-Vaisala frequency (rad/s)
    H : scale height (m)
    f : Coriolis parameter (rad/s)
    returns: Rossby radius (m)
    """
    return (N * H) / abs(f)


def thermal_wind(dT_dy, f, dz):
    """
    Wind shear from horizontal temperature gradient.
    Governs jet stream strength — links temperature gradients to wind.
    Pole-equator temperature gradient drives jet streams.
    As Arctic warms faster (Arctic amplification), gradient weakens,
    jet stream slows and meanders — cascade to weather persistence.
    dT_dy : meridional temperature gradient (K/m)
    f     : Coriolis parameter (rad/s)
    dz    : vertical layer depth (m)
    returns: wind shear (m/s per meter altitude)
    """
    return -(g_earth / (f * 273.0)) * dT_dy


def hadley_cell_extent(T_equator, T_pole):
    """
    Approximate poleward extent of Hadley circulation.
    Expands with reduced pole-equator temperature gradient.
    Cascade: tropics widen, subtropical dry zones shift poleward.
    T_equator : equatorial temperature (K)
    T_pole    : polar temperature (K)
    returns: approximate poleward boundary latitude (degrees)
    """
    delta_T = T_equator - T_pole
    # Empirical scaling — Hadley cell edge ~30 deg at current delta_T ~50K
    reference_delta_T = 50.0
    reference_latitude = 30.0
    return reference_latitude * (reference_delta_T / delta_T) ** 0.5


# ─────────────────────────────────────────────
# WATER CYCLE
# ─────────────────────────────────────────────

def saturation_vapor_pressure(T):
    """
    Clausius-Clapeyron — saturation vapor pressure.
    Governs moisture capacity of atmosphere.
    ~7% increase per degree K — amplifies precipitation extremes.
    T : temperature (K)
    returns: es (Pa)
    """
    T_c = T - 273.15
    return 611.2 * np.exp(17.67 * T_c / (T_c + 243.5))


def precipitable_water(T_surface, scale_height_m=2500.0):
    """
    Total column water vapor.
    Scales with surface temperature via Clausius-Clapeyron.
    T_surface     : surface temperature (K)
    scale_height_m: moisture scale height
    returns: precipitable water (kg/m^2 = mm)
    """
    rho_water = 1000.0
    es = saturation_vapor_pressure(T_surface)
    q_surface = 0.622 * es / 101325.0
    return q_surface * 1.2 * scale_height_m  # 1.2 kg/m^3 surface air density


def convective_available_potential_energy(T_parcel, T_env, z_top, z_base):
    """
    CAPE — energy available for convective storms.
    Integrates buoyancy over depth of instability.
    T_parcel : parcel temperature profile (array K)
    T_env    : environment temperature profile (array K)
    z_top    : top of instability layer (m)
    z_base   : base of instability layer (m)
    returns: CAPE (J/kg)
    """
    if np.isscalar(T_parcel):
        buoyancy = g_earth * (T_parcel - T_env) / T_env
        return max(0, buoyancy * (z_top - z_base))
    else:
        dz = (z_top - z_base) / len(T_parcel)
        buoyancy = g_earth * (np.array(T_parcel) - np.array(T_env)) / np.array(T_env)
        return np.sum(np.maximum(0, buoyancy)) * dz


# ─────────────────────────────────────────────
# AEROSOL AND CHEMISTRY
# ─────────────────────────────────────────────

def aerosol_direct_forcing(AOD, asymmetry=0.65, SSA=0.95):
    """
    Direct radiative forcing from aerosol optical depth.
    AOD       : aerosol optical depth (dimensionless)
    asymmetry : scattering asymmetry parameter g
    SSA       : single scattering albedo
    returns: forcing (W/m^2) — negative = cooling
    """
    S0 = 1361.0
    albedo = 0.30
    T_atm  = 0.76  # atmospheric transmittance
    beta   = 0.5 * (1 - asymmetry)
    return -S0/4 * T_atm**2 * (1 - albedo)**2 * 2 * beta * SSA * AOD


def ozone_column_forcing(delta_DU):
    """
    Radiative effect of ozone column change.
    Ozone couples stratosphere chemistry to UV surface flux
    which couples to biological productivity (layer 6).
    delta_DU : change in Dobson Units
    returns: UV flux change proxy (W/m^2 UV-B)
    ~1% UV increase per 1 DU decrease
    """
    baseline_UV = 2.5  # W/m^2 UV-B surface clear sky
    return -baseline_UV * (delta_DU / 100.0) * 0.01 * 100


# ─────────────────────────────────────────────
# COUPLING INTERFACES
# ─────────────────────────────────────────────

def coupling_state(T_surface, T_pole, P_surface, q_surface,
                   delta_CO2_ppm=140.0, AOD=0.1,
                   latitude_deg=45.0, delta_omega=0.0,
                   delta_T_stratosphere=0.0):
    """
    Full atmosphere state vector for adjacent layer consumption.
    T_surface        : surface temperature (K)
    T_pole           : polar temperature (K)
    P_surface        : surface pressure (Pa)
    q_surface        : surface specific humidity (kg/kg)
    delta_CO2_ppm    : CO2 increase above pre-industrial (ppm)
    AOD              : aerosol optical depth
    latitude_deg     : reference latitude
    delta_omega      : Earth rotation perturbation (rad/s) from layer 1
    delta_T_strato   : stratospheric temperature anomaly (K)
    """
    f           = coriolis_parameter_perturbed(latitude_deg, delta_omega)
    T_eff       = effective_radiating_temperature()
    GHG_forcing = greenhouse_forcing(delta_CO2_ppm)
    DALR        = dry_adiabatic_lapse_rate()
    H           = scale_height(T_surface)
    es          = saturation_vapor_pressure(T_surface)
    PW          = precipitable_water(T_surface)
    hadley      = hadley_cell_extent(T_surface, T_pole)
    jet_shear   = thermal_wind((T_surface - T_pole) / 5e6, f, H)
    aerosol_f   = aerosol_direct_forcing(AOD)
    N           = brunt_vaisala_frequency(DALR * 0.1, T_surface)  # stable layer proxy
    Lr          = rossby_radius(N if np.isreal(N) else 0.01, H, f)

    return {
        "T_effective_K":               T_eff,
        "GHG_forcing_Wm2":             GHG_forcing,
        "aerosol_forcing_Wm2":         aerosol_f,
        "net_forcing_Wm2":             GHG_forcing + aerosol_f,
        "DALR_Km":                     DALR * 1000,
        "scale_height_m":              H,
        "saturation_vapor_Pa":         es,
        "precipitable_water_mm":       PW,
        "coriolis_f_rads":             f,
        "hadley_extent_deg":           hadley,
        "jet_shear_proxy":             jet_shear,
        "rossby_radius_m":             Lr,
        "brunt_vaisala_rads":          float(np.real(N)),
        "convection_active":           np.imag(N) > 0,
        "gravity_wave_source":         True,  # always — couples upward to layer 2
        "cascade_to_ionosphere":       "gravity_waves + lightning + convection",
        "cascade_to_hydrosphere":      "precipitation + evaporation + runoff",
        "cascade_to_biosphere":        "temperature + CO2 + UV + precipitation timing",
        "rotation_perturbation_active": abs(delta_omega) > 1e-15,
        "note": "temperature is an output variable here, not a forcing function"
    }




# layer_3_atmosphere.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Atmosphere constraint layer.
# Governs thermodynamic state, radiative transfer, fluid dynamics,
# chemical composition, and energy transport.
# This is where climate models live — but here it is one layer
# in a coupled stack, not the whole system.
# Imports constraints from layers 0, 1, 2.

import numpy as np
from scipy.constants import k, R, g, Stefan_Boltzmann
from layer_0_electromagnetics import poynting_vector, electric_energy_density
from layer_2_ionosphere import (
    joule_heating,
    gravity_wave_ionospheric_signature,
    schumann_resonances,
)

# ─────────────────────────────────────────────
# FUNDAMENTAL CONSTANTS — ATMOSPHERIC
# ─────────────────────────────────────────────

R_dry    = 287.05   # J/(kg·K) — specific gas constant dry air
R_vapor  = 461.5    # J/(kg·K) — specific gas constant water vapor
cp_dry   = 1005.0   # J/(kg·K) — specific heat dry air constant pressure
cv_dry   = 718.0    # J/(kg·K) — specific heat dry air constant volume
gamma    = cp_dry / cv_dry  # adiabatic index ~1.4
L_v      = 2.501e6  # J/kg — latent heat vaporization at 0°C
L_f      = 3.337e5  # J/kg — latent heat fusion
L_s      = 2.834e6  # J/kg — latent heat sublimation
g_earth  = 9.80665  # m/s^2
R_E      = 6.371e6  # m

# ─────────────────────────────────────────────
# THERMODYNAMIC STATE
# ─────────────────────────────────────────────

def potential_temperature(T, P, P0=1e5):
    """
    Potential temperature — temperature parcel would have at reference pressure.
    Conserved for dry adiabatic processes. Fundamental state variable.
    T  : temperature (K)
    P  : pressure (Pa)
    P0 : reference pressure (Pa), default 100 kPa
    returns: theta (K)
    """
    return T * (P0 / P) ** (R_dry / cp_dry)


def virtual_temperature(T, q):
    """
    Virtual temperature — accounts for water vapor buoyancy effect​​​​​​​​​​​​​​​​




