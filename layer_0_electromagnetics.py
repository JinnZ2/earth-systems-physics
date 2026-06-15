# layer_0_electromagnetics.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Base constraint layer.
# All other layers inherit from these relationships.
# Nothing above this layer operates outside these constraints.

import numpy as np
from scipy.constants import (
    epsilon_0,   # permittivity of free space
    mu_0,        # permeability of free space
    c,           # speed of light
    e,           # elementary charge
    m_e,         # electron mass
    m_p,         # proton mass
    k,           # Boltzmann constant
    h,           # Planck constant
    hbar,        # reduced Planck constant
)

# ─────────────────────────────────────────────
# FUNDAMENTAL FIELD EQUATIONS
# ─────────────────────────────────────────────

def gauss_electric(rho, dV):
    """
    Gauss's Law — Electric
    div(E) = rho / epsilon_0
    Total electric flux through closed surface = enclosed charge / epsilon_0
    rho : charge density (C/m^3)
    dV  : volume element (m^3)
    returns: flux (V·m)
    """
    return (rho * dV) / epsilon_0


def gauss_magnetic():
    """
    Gauss's Law — Magnetic
    div(B) = 0
    Magnetic monopoles do not exist.
    No source or sink of magnetic flux.
    Returns constraint statement only — this is a hard boundary condition.
    """
    return "div(B) = 0 : magnetic flux is always conserved, no monopoles"


def faraday_induction(dB_dt, dA):
    """
    Faraday's Law
    curl(E) = -dB/dt
    Changing magnetic flux induces electric field.
    dB_dt : rate of change of magnetic field (T/s)
    dA    : area element (m^2)
    returns: induced EMF (V)
    """
    return -dB_dt * dA


def ampere_maxwell(J, dE_dt):
    """
    Ampere-Maxwell Law
    curl(B) = mu_0 * J + mu_0 * epsilon_0 * dE/dt
    Current AND changing electric field produce magnetic field.
    J     : current density (A/m^2)
    dE_dt : rate of change of electric field (V/m/s)
    returns: curl of B (T/m)
    """
    return mu_0 * J + mu_0 * epsilon_0 * dE_dt


# ─────────────────────────────────────────────
# WAVE PROPAGATION
# ─────────────────────────────────────────────

def em_wave_speed(epsilon_r=1.0, mu_r=1.0):
    """
    Speed of EM wave through a medium.
    epsilon_r : relative permittivity of medium
    mu_r      : relative permeability of medium
    returns: wave speed (m/s)
    """
    return c / np.sqrt(epsilon_r * mu_r)


def skin_depth(frequency, conductivity, mu_r=1.0):
    """
    Depth at which EM wave amplitude decays to 1/e in a conductive medium.
    Critical for ionospheric coupling and ground penetration.
    frequency   : Hz
    conductivity: S/m
    mu_r        : relative permeability
    returns: skin depth (m)
    """
    omega = 2 * np.pi * frequency
    return np.sqrt(2 / (omega * mu_0 * mu_r * conductivity))


def plasma_frequency(n_e):
    """
    Natural oscillation frequency of free electrons in plasma.
    Governs what EM frequencies the ionosphere reflects vs transmits.
    n_e : electron number density (m^-3)
    returns: plasma frequency (Hz)
    """
    return (1 / (2 * np.pi)) * np.sqrt((n_e * e**2) / (epsilon_0 * m_e))


def cyclotron_frequency(q, B, m):
    """
    Cyclotron (gyro) frequency of a charged particle in a magnetic field.
    Governs particle trapping and resonance in the magnetosphere.
    q : charge (C)
    B : magnetic field magnitude (T)
    m : particle mass (kg)
    returns: cyclotron frequency (Hz)
    """
    return abs(q) * B / (2 * np.pi * m)


# ─────────────────────────────────────────────
# ENERGY DENSITY
# ─────────────────────────────────────────────

def electric_energy_density(E_field):
    """
    Energy stored per unit volume in electric field.
    E_field : electric field magnitude (V/m)
    returns: energy density (J/m^3)
    """
    return 0.5 * epsilon_0 * E_field**2


def magnetic_energy_density(B_field):
    """
    Energy stored per unit volume in magnetic field.
    B_field : magnetic field magnitude (T)
    returns: energy density (J/m^3)
    """
    return B_field**2 / (2 * mu_0)


def poynting_vector(E_field, B_field):
    """
    Energy flux — power per unit area carried by EM field.
    Direction: E cross B
    E_field : electric field magnitude (V/m)
    B_field : magnetic field magnitude (T)
    returns: power per unit area (W/m^2)
    """
    return (E_field * B_field) / mu_0


# ─────────────────────────────────────────────
# LORENTZ FORCE — particle coupling to fields
# ─────────────────────────────────────────────

def lorentz_force(q, E_field, v, B_field):
    """
    Force on charged particle in EM field.
    F = q(E + v x B)
    Governs particle motion in magnetosphere, ionosphere, solar wind.
    q       : charge (C)
    E_field : electric field (V/m)
    v       : particle velocity (m/s)
    B_field : magnetic field (T)
    returns: force (N)
    Cross product handled as magnitudes assuming perpendicular geometry.
    """
    return q * (E_field + v * B_field)


# ─────────────────────────────────────────────
# GEOMAGNETIC DIPOLE
# Present-epoch reference and orbital-driven secular drift.
# Coupling to Layer -1 routed THROUGH Layer 5: orbital forcing
# perturbs rotation rate (Layer 5), rotation perturbation drives
# dynamo response, dynamo response drifts the dipole moment.
# ─────────────────────────────────────────────

M_EARTH = 8.0e22   # A·m^2  present-epoch geomagnetic dipole moment

MANTLE_CONVECTION_CRITICAL_M_S = 3.0e-10   # m/s — ~1 cm/yr; below this dynamo efficiency falls
MANTLE_TEMP_REFERENCE_K        = 4000.0    # K — reference mantle temperature for convection scaling


def dynamo_efficiency(mantle_convection_rate_m_s):
    """
    Geodynamo efficiency as function of mantle convection rate.
    Below the critical threshold, CMB heat flux falls and outer-core
    convective driving of the geodynamo weakens proportionally.
    mantle_convection_rate_m_s : mantle convection speed (m/s)
    returns: efficiency (0.0–1.0)
    """
    if mantle_convection_rate_m_s <= 0.0:
        return 0.0
    return min(1.0, mantle_convection_rate_m_s / MANTLE_CONVECTION_CRITICAL_M_S)


def mantle_temperature_forcing(T_mantle_K, T_mantle_reference_K=MANTLE_TEMP_REFERENCE_K):
    """
    Translate mantle temperature into convection rate and dynamo efficiency.
    Convection vigor scales linearly with temperature excess above reference
    over a ~500 K window; below reference the dynamo enters the weakening regime.
    T_mantle_K          : current mantle temperature (K)
    T_mantle_reference_K: reference mantle temperature (K)
    returns: dict with convection_rate_m_s, dynamo_efficiency, DYNAMO_PHASE_SHIFT
    """
    delta_T = T_mantle_K - T_mantle_reference_K
    convection_rate = MANTLE_CONVECTION_CRITICAL_M_S * (1.0 + delta_T / 500.0)
    convection_rate = max(0.0, convection_rate)
    eff = dynamo_efficiency(convection_rate)
    return {
        "convection_rate_m_s": convection_rate,
        "dynamo_efficiency":   eff,
        "DYNAMO_PHASE_SHIFT":  eff < 0.5,
    }


def field_drift_velocity(M_dipole_Am2, dM_per_yr_Am2):
    """
    Fractional drift rate of the geomagnetic dipole moment.
    Negative value indicates a weakening field.
    M_dipole_Am2  : current dipole moment (A·m²)
    dM_per_yr_Am2 : secular drift rate (A·m²/yr)
    returns: fractional drift rate (yr⁻¹)
    """
    if M_dipole_Am2 == 0.0:
        return 0.0
    return dM_per_yr_Am2 / M_dipole_Am2


def dipole_drift_response(M0, dM_dipole_per_yr_Am2, dt_yr):
    """
    Apply a secular dipole-moment drift to the reference moment.
    First-order linear update — adequate at orbital cadence where
    dt_yr * dM/dt is small compared to M0.
    M0                     : reference dipole moment (A·m^2)
    dM_dipole_per_yr_Am2   : secular drift rate (A·m^2/yr) from Layer -1
    dt_yr                  : elapsed years over which to apply drift
    returns: updated dipole moment (A·m^2)
    """
    return M0 + dM_dipole_per_yr_Am2 * dt_yr


def surface_field_from_dipole(M_dipole, R_planet=6.371e6):
    """
    Equatorial surface magnetic field from dipole moment.
    B_eq = mu_0 * M / (4 pi R^3)
    M_dipole : magnetic dipole moment (A·m^2)
    R_planet : planetary radius (m)
    returns: equatorial surface B (T)
    """
    return mu_0 * M_dipole / (4 * np.pi * R_planet**3)


# ─────────────────────────────────────────────
# COUPLING INTERFACES
# Outputs consumed by Layer 1 (Magnetosphere) and Layer 2 (Ionosphere)
# ─────────────────────────────────────────────

def coupling_state(n_e, B_surface, E_surface, frequency_range,
                   magnonic_material=None,
                   magnomech_mineral="magnetite",
                   magnomech_grain_size=50e-6,
                   magnomech_rock_volume=1000.0,
                   magnomech_mineral_fraction=0.02,
                   magnomech_T=290.0,
                   dM_dipole_per_yr_Am2=0.0,
                   dt_orbital_yr=0.0,
                   T_mantle_K=MANTLE_TEMP_REFERENCE_K,
                   T_mantle_reference_K=MANTLE_TEMP_REFERENCE_K):
    """
    State vector exported to adjacent layers.
    n_e                  : electron density at interface (m^-3)
    B_surface            : magnetic field at Earth surface (T)
    E_surface            : electric field at Earth surface (V/m)
    frequency_range      : tuple (f_min, f_max) Hz — active EM band
    magnonic_material    : optional material name from magnonic_sublayer.MATERIALS
    magnomech_mineral    : crustal mineral for magnomechanical coupling
    magnomech_grain_size : grain diameter (m)
    magnomech_rock_volume: formation volume (m3)
    magnomech_mineral_fraction: volume fraction of magnetic mineral
    magnomech_T          : temperature (K)
    dM_dipole_per_yr_Am2 : secular dipole drift rate from Layer -1
                            orbital forcing (A·m^2/yr), routed via L5.
    dt_orbital_yr        : elapsed time since reference epoch (yr).
                            Multiplies dM/dt to update the dipole.
    returns: dict of coupling parameters
    """
    from magnonic_sublayer import magnonic_coupling_state, MATERIALS
    from layer_0b_magnomechanical import coupling_state as magnomech_state

    # Apply orbital-driven dipole drift before any field-dependent
    # quantity is computed. dt_orbital_yr=0 reproduces the previous
    # stationary-dipole behaviour exactly.
    M_dipole_now = dipole_drift_response(M_EARTH, dM_dipole_per_yr_Am2,
                                         dt_orbital_yr)

    _mantle    = mantle_temperature_forcing(T_mantle_K, T_mantle_reference_K)
    _drift_vel = field_drift_velocity(M_dipole_now, dM_dipole_per_yr_Am2)

    f_plasma = plasma_frequency(n_e)
    delta = skin_depth(frequency_range[0], 1e-4)  # upper atmosphere conductivity ~1e-4 S/m
    f_cyclotron = cyclotron_frequency(e, B_surface, m_e)

    state = {
        "plasma_frequency_hz":       f_plasma,
        "plasma_frequency_Hz":       f_plasma,
        "skin_depth_m":              delta,
        "cyclotron_frequency_Hz":    f_cyclotron,
        "electric_energy_density":   electric_energy_density(E_surface),
        "magnetic_energy_density":   magnetic_energy_density(B_surface),
        "poynting_flux_wm2":         poynting_vector(E_surface, B_surface),
        "reflection_threshold_hz":   f_plasma,  # EM below this reflects off ionosphere
        "transmission_threshold_hz": f_plasma,  # EM above this passes through
        "M_dipole_Am2":              M_dipole_now,
        "M_dipole_reference_Am2":    M_EARTH,
        "dM_dipole_per_yr_Am2":      dM_dipole_per_yr_Am2,
        "dipole_drift_fraction":     (
            (M_dipole_now - M_EARTH) / M_EARTH if M_EARTH else 0.0
        ),
        "B_surface_dipole_eq_T":     surface_field_from_dipole(M_dipole_now),
        "field_strength_T":          surface_field_from_dipole(M_dipole_now),
        "field_drift_velocity_per_yr": _drift_vel,
        "dynamo_efficiency":         _mantle["dynamo_efficiency"],
        "DYNAMO_PHASE_SHIFT":        _mantle["DYNAMO_PHASE_SHIFT"],
        "mantle_convection_rate_m_s": _mantle["convection_rate_m_s"],
        "T_mantle_K":                T_mantle_K,
        "constraint": gauss_magnetic(),
    }

    # Magnonic sublayer — spin wave physics in magnetic media
    if magnonic_material is not None and magnonic_material in MATERIALS:
        mat = MATERIALS[magnonic_material]
        mag_state = magnonic_coupling_state(
            H0=B_surface / (4 * np.pi * 1e-7),  # convert B to H (free space)
            M_s=mat["M_s"],
            A_ex=mat["A_ex"],
            alpha=mat["alpha"],
            T=300.0,
            conductivity=mat["conductivity"],
            c_sound=mat["c_sound"],
            n_e=n_e,
        )
        # Prefix magnonic keys to avoid collisions
        for mk, mv in mag_state.items():
            state[f"magnonic_{mk}"] = mv
    else:
        # Always run with Magnetite defaults for natural crustal coupling
        mag_state = magnonic_coupling_state(
            H0=B_surface / (4 * np.pi * 1e-7),
            M_s=4.8e5,       # Magnetite
            A_ex=1.2e-11,
            alpha=0.05,
            T=300.0,
            conductivity=2e4,
            c_sound=5500.0,
            n_e=n_e,
        )
        state["magnonic_energy_density_J"] = mag_state["magnon_energy_density_J"]
        state["magnonic_prop_length_m"] = mag_state["magnon_prop_length_exchange_m"]
        state["magnonic_phonon_regime"] = mag_state["magnon_phonon_regime"]
        state["magnonic_band_bottom_Hz"] = mag_state["magnon_band_bottom_Hz"]
        state["magnonic_damping_total"] = mag_state["alpha_total"]

    # Magnomechanical sublayer — spin-phonon coupling in crustal minerals
    mm_state = magnomech_state(
        H_field=B_surface,
        mineral=magnomech_mineral,
        grain_size_m=magnomech_grain_size,
        rock_volume_m3=magnomech_rock_volume,
        mineral_fraction=magnomech_mineral_fraction,
        T=magnomech_T,
    )
    # Merge with magnomech_ prefix
    for mk, mv in mm_state.items():
        if mk.startswith("coupling_to_"):
            continue  # skip nested dicts for layer state
        state[f"magnomech_{mk}"] = mv

    return state
