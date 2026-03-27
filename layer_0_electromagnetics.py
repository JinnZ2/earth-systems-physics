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
# COUPLING INTERFACES
# Outputs consumed by Layer 1 (Magnetosphere) and Layer 2 (Ionosphere)
# ─────────────────────────────────────────────

def coupling_state(n_e, B_surface, E_surface, frequency_range,
                   magnonic_material=None,
                   magnomech_mineral="magnetite",
                   magnomech_grain_size=50e-6,
                   magnomech_rock_volume=1000.0,
                   magnomech_mineral_fraction=0.02,
                   magnomech_T=290.0):
    """
    State vector exported to adjacent layers.
    n_e               : electron density at interface (m^-3)
    B_surface         : magnetic field at Earth surface (T)
    E_surface         : electric field at Earth surface (V/m)
    frequency_range   : tuple (f_min, f_max) Hz — active EM band
    magnonic_material : optional material name from magnonic_sublayer.MATERIALS
    magnomech_mineral : crustal mineral for magnomechanical coupling
    magnomech_grain_size : grain diameter (m)
    magnomech_rock_volume: formation volume (m3)
    magnomech_mineral_fraction: volume fraction of magnetic mineral
    magnomech_T       : temperature (K)
    returns: dict of coupling parameters
    """
    from magnonic_sublayer import magnonic_coupling_state, MATERIALS
    from layer_0b_magnomechanical import coupling_state as magnomech_state

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
