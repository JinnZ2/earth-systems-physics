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

def coupling_state(n_e, B_surface, E_surface, frequency_range):
    """
    State vector exported to adjacent layers.
    n_e             : electron density at interface (m^-3)
    B_surface       : magnetic field at Earth surface (T)
    E_surface       : electric field at Earth surface (V/m)
    frequency_range : tuple (f_min, f_max) Hz — active EM band
    returns: dict of coupling parameters
    """
    f_plasma = plasma_frequency(n_e)
    delta = skin_depth(frequency_range[0], 1e-4)  # upper atmosphere conductivity ~1e-4 S/m
    f_cyclotron = cyclotron_frequency(e, B_surface, m_e)

    return {
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
