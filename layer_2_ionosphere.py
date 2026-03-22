# layer_2_ionosphere.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Ionosphere constraint layer.
# Governs atmospheric ionization, EM wave propagation and reflection,
# charge transport, auroral energy deposition, and coupling between
# magnetosphere above and neutral atmosphere below.
# Imports base constraints from layer_0 and layer_1.

import numpy as np
from scipy.constants import epsilon_0, mu_0, e, m_e, k, c
from layer_0_electromagnetics import (
    plasma_frequency,
    skin_depth,
    em_wave_speed,
    electric_energy_density,
)
from layer_1_magnetosphere import (
    alfven_speed,
    loss_cone_angle,
    coupling_state as mag_coupling_state,
)

# ─────────────────────────────────────────────
# IONOSPHERIC LAYER STRUCTURE
# Approximate altitude boundaries and typical electron densities
# ─────────────────────────────────────────────

LAYERS = {
    "D": {"alt_km": (60, 90),   "n_e_m3": 1e8,  "note": "absorbs LF/MF, disappears at night"},
    "E": {"alt_km": (90, 150),  "n_e_m3": 1e11, "note": "reflects MF, sporadic-E scattering"},
    "F1": {"alt_km": (150, 200),"n_e_m3": 2e11, "note": "daytime only, merges with F2 at night"},
    "F2": {"alt_km": (200, 500),"n_e_m3": 1e12, "note": "primary HF reflection layer, persists at night"},
}


def critical_frequency(n_e):
    """
    Maximum frequency reflected by ionospheric layer.
    EM above this passes through to space.
    EM below this reflects back to Earth.
    n_e : electron density (m^-3)
    returns: critical frequency (Hz)
    """
    return plasma_frequency(n_e)


def maximum_usable_frequency(n_e, elevation_angle_deg):
    """
    MUF — highest frequency that reflects at given elevation angle.
    Governs HF radio propagation — relevant for communication resilience.
    n_e              : electron density (m^-3)
    elevation_angle  : degrees above horizon (0=horizontal, 90=vertical)
    returns: MUF (Hz)
    """
    f_c = critical_frequency(n_e)
    theta = np.radians(elevation_angle_deg)
    return f_c / np.sin(theta)


def refractive_index(f, n_e, B=0, collision_freq=0):
    """
    Appleton-Hartree refractive index for EM wave in magnetized plasma.
    Simplified form without magnetic field splitting (B=0 case).
    f              : wave frequency (Hz)
    n_e            : electron density (m^-3)
    collision_freq : electron-neutral collision frequency (Hz)
    returns: complex refractive index (real=propagation, imag=absorption)
    """
    omega = 2 * np.pi * f
    omega_p = 2 * np.pi * plasma_frequency(n_e)
    nu = collision_freq

    X = (omega_p / omega)**2
    Z = nu / omega

    n_squared = 1 - X / (1 - 1j * Z)
    return np.sqrt(n_squared)


# ─────────────────────────────────────────────
# IONIZATION PROCESSES
# ─────────────────────────────────────────────

def photoionization_rate(solar_flux, absorption_cross_section, n_neutral):
    """
    Rate of ionization by solar UV/EUV photons.
    Primary daytime ionization source.
    solar_flux             : photon flux (m^-2 s^-1)
    absorption_cross_section: m^2
    n_neutral              : neutral gas density (m^-3)
    returns: ionization rate (m^-3 s^-1)
    """
    return solar_flux * absorption_cross_section * n_neutral


def recombination_rate(alpha, n_e):
    """
    Rate of electron-ion recombination.
    Governs nighttime ionosphere decay.
    alpha : recombination coefficient (m^3/s) ~1e-13 for F layer
    n_e   : electron density (m^-3)
    returns: recombination rate (m^-3 s^-1)
    """
    return alpha * n_e**2


def equilibrium_electron_density(q, alpha):
    """
    Steady-state electron density when production = loss.
    q     : production rate (m^-3 s^-1)
    alpha : recombination coefficient (m^3/s)
    returns: equilibrium n_e (m^-3)
    """
    return np.sqrt(q / alpha)


def cosmic_ray_ionization(altitude_km, solar_activity="moderate"):
    """
    Galactic cosmic ray contribution to D-layer ionization.
    Enhanced during solar minimum — anti-correlated with solar activity.
    Affects cloud nucleation — coupling to troposphere.
    altitude_km    : altitude (km)
    solar_activity : 'low', 'moderate', 'high'
    returns: relative ionization rate proxy (normalized)
    """
    activity_factor = {"low": 1.4, "moderate": 1.0, "high": 0.7}
    af = activity_factor.get(solar_activity, 1.0)
    # Peak ionization ~15 km (Pfotzer maximum), decays above and below
    pfotzer_peak = 15.0
    if altitude_km < 60:
        return af * np.exp(-((altitude_km - pfotzer_peak)**2) / 200)
    else:
        return af * 0.01  # minimal above stratosphere


# ─────────────────────────────────────────────
# AURORAL ENERGY DEPOSITION
# Magnetosphere energy dumps into ionosphere at high latitudes
# ─────────────────────────────────────────────

def auroral_energy_flux(kp):
    """
    Empirical auroral energy flux as function of geomagnetic activity.
    Converts magnetospheric particle precipitation to ionospheric heating.
    kp : 0-9 geomagnetic index
    returns: energy flux (mW/m^2)
    Quiet ~1 mW/m^2, storm ~10-100 mW/m^2
    """
    return 0.5 * np.exp(0.6 * kp)


def auroral_ionization_rate(energy_flux_mWm2, altitude_km):
    """
    Electron density production from auroral particle precipitation.
    Couples magnetospheric energy directly into neutral atmosphere chemistry.
    energy_flux_mWm2 : precipitating particle energy flux (mW/m^2)
    altitude_km      : altitude of deposition (km)
    returns: ionization rate proxy (m^-3 s^-1), normalized
    Peak deposition ~110 km altitude
    """
    peak_alt = 110.0
    width = 20.0
    altitude_factor = np.exp(-((altitude_km - peak_alt)**2) / (2 * width**2))
    return energy_flux_mWm2 * 1e-3 * altitude_factor * 1e10


def joule_heating(sigma_P, E_field):
    """
    Joule heating of ionosphere by magnetospheric electric fields.
    Major energy input to thermosphere — drives neutral winds.
    sigma_P  : Pedersen conductivity (S/m)
    E_field  : electric field magnitude (V/m)
    returns: heating rate (W/m^3)
    """
    return sigma_P * E_field**2


# ─────────────────────────────────────────────
# CONDUCTIVITY TENSOR
# Ionosphere conducts differently parallel vs perpendicular to B
# ─────────────────────────────────────────────

def pedersen_conductivity(n_e, B, nu_en):
    """
    Pedersen conductivity — current parallel to E, perpendicular to B.
    Governs magnetosphere-ionosphere current closure.
    n_e  : electron density (m^-3)
    B    : magnetic field (T)
    nu_en: electron-neutral collision frequency (Hz)
    returns: sigma_P (S/m)
    """
    omega_e = e * B / m_e  # electron gyrofrequency
    return (n_e * e**2 / m_e) * (nu_en / (nu_en**2 + omega_e**2))


def hall_conductivity(n_e, B, nu_en):
    """
    Hall conductivity — current perpendicular to both E and B.
    Drives electrojet currents — generates magnetic perturbations
    detectable at Earth surface (Kp, Dst indices).
    n_e  : electron density (m^-3)
    B    : magnetic field (T)
    nu_en: electron-neutral collision frequency (Hz)
    returns: sigma_H (S/m)
    """
    omega_e = e * B / m_e
    return (n_e * e**2 / m_e) * (omega_e / (nu_en**2 + omega_e**2))


def parallel_conductivity(n_e, nu_en):
    """
    Field-aligned conductivity — very high, nearly lossless.
    Governs current flow along magnetic field lines.
    n_e  : electron density (m^-3)
    nu_en: collision frequency (Hz)
    returns: sigma_parallel (S/m)
    """
    return n_e * e**2 / (m_e * nu_en)


# ─────────────────────────────────────────────
# ATMOSPHERIC COUPLING — bottom side
# Ionosphere couples downward to neutral atmosphere
# ─────────────────────────────────────────────

def schumann_resonances(mode=1):
    """
    ELF resonances of Earth-ionosphere cavity.
    Fundamental ~7.83 Hz and harmonics.
    These are a direct measure of global lightning activity
    and couple ionospheric conductivity to tropospheric convection.
    mode : resonance mode number (1, 2, 3...)
    returns: resonant frequency (Hz)
    """
    c_light = 3e8
    R_E = 6.371e6
    return (c_light / (2 * np.pi * R_E)) * np.sqrt(mode * (mode + 1))


def schumann_frequency_shift(delta_T_ionosphere):
    """
    Temperature-driven ionosphere height change shifts Schumann frequencies.
    Links climate-driven thermosphere changes to global EM cavity properties.
    delta_T_ionosphere : temperature change in thermosphere (K)
    returns: frequency shift (Hz) — approximate
    ~0.01 Hz per 1 km height change, ~1-2 km per 50K
    """
    delta_h_km = delta_T_ionosphere * 0.03  # rough scale height sensitivity
    base_freq = schumann_resonances(1)
    R_E_km = 6371.0
    return -base_freq * (delta_h_km / R_E_km)


def gravity_wave_ionospheric_signature(wave_period_min, amplitude_ms):
    """
    Atmospheric gravity waves from tropospheric storms propagate upward
    and create traveling ionospheric disturbances (TIDs).
    This is a direct troposphere-to-ionosphere coupling pathway.
    wave_period_min : gravity wave period (minutes)
    amplitude_ms    : neutral wind perturbation amplitude (m/s)
    returns: estimated electron density perturbation fraction
    """
    # Empirical: amplitude scales with wave energy flux conserved in density
    # rho decreases ~1000x from troposphere to ionosphere
    # velocity amplitude scales as rho^(-1/2) ~ 30x amplification
    amplification = 30.0
    ionospheric_wind_ms = amplitude_ms * amplification
    # 1 m/s neutral wind ~ 0.1% electron density perturbation (rough)
    return ionospheric_wind_ms * 0.001


# ─────────────────────────────────────────────
# COUPLING INTERFACES
# ─────────────────────────────────────────────

def coupling_state(n_e_F2, B_surface, kp, solar_flux,
                   nu_en=1e3, E_field=1e-3, delta_T_thermo=0.0):
    """
    Full ionosphere state vector for adjacent layer consumption.
    n_e_F2       : F2 layer peak electron density (m^-3)
    B_surface    : surface magnetic field (T)
    kp           : geomagnetic index
    solar_flux   : solar EUV proxy (normalized, 1.0 = quiet sun)
    nu_en        : electron-neutral collision frequency (Hz)
    E_field      : convection electric field (V/m)
    delta_T_thermo: thermosphere temperature anomaly (K)
    """
    f_c   = critical_frequency(n_e_F2)
    sigma_P = pedersen_conductivity(n_e_F2, B_surface, nu_en)
    sigma_H = hall_conductivity(n_e_F2, B_surface, nu_en)
    sr1   = schumann_resonances(1)
    sr_shift = schumann_frequency_shift(delta_T_thermo)
    joule = joule_heating(sigma_P, E_field)
    aurora_flux = auroral_energy_flux(kp)

    return {
        "critical_frequency_hz":         f_c,
        "muf_vertical_hz":               f_c,
        "pedersen_conductivity_Sm":      sigma_P,
        "hall_conductivity_Sm":          sigma_H,
        "joule_heating_Wm3":             joule,
        "auroral_energy_flux_mWm2":      aurora_flux,
        "schumann_f1_hz":                sr1,
        "schumann_f1_shift_hz":          sr_shift,
        "cosmic_ray_D_layer_proxy":      cosmic_ray_ionization(75, "moderate"),
        "gravity_wave_coupling_active":  True,
        "cascade_to_atmosphere":         joule > 1e-9,
        "cascade_to_magnetosphere":      sigma_P > 1e-4,
        "cascade_from_troposphere":      "gravity_waves, lightning, convection",
        "note": "ionosphere is not a boundary — it is a bidirectional coupling membrane"
    }
