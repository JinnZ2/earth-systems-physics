# layer_1_magnetosphere.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Magnetosphere constraint layer.
# Governs solar wind interaction, field geometry, particle trapping,
# magnetic reconnection, and coupling to ionosphere and crust.
# Imports base constraints from layer_0.

import numpy as np
from scipy.constants import mu_0, m_p, m_e, e, k
from layer_0_electromagnetics import (
    lorentz_force,
    plasma_frequency,
    poynting_vector,
    magnetic_energy_density,
)

# ─────────────────────────────────────────────
# EARTH DIPOLE FIELD
# ─────────────────────────────────────────────

# Earth's magnetic dipole moment (A·m^2)
M_EARTH = 8.0e22

def dipole_field_magnitude(M, r, theta):
    """
    Magnetic field magnitude of a dipole at distance r and colatitude theta.
    M     : magnetic moment (A·m^2)
    r     : radial distance from center (m)
    theta : colatitude from magnetic pole (radians)
    returns: field magnitude (T)
    """
    return (mu_0 / (4 * np.pi)) * (M / r**3) * np.sqrt(1 + 3 * np.cos(theta)**2)


def dipole_field_components(M, r, theta):
    """
    Radial and tangential components of dipole field.
    returns: (B_r, B_theta) in Tesla
    """
    prefactor = (mu_0 / (4 * np.pi)) * (M / r**3)
    B_r     = -2 * prefactor * np.cos(theta)
    B_theta = -prefactor * np.sin(theta)
    return B_r, B_theta


def field_line_radius(L, theta):
    """
    Dipole field line equation.
    L     : L-shell parameter (Earth radii) — field line label
    theta : colatitude (radians)
    returns: radial distance in Earth radii
    L=1 is Earth surface at equator
    L=6.6 is geostationary orbit
    """
    R_E = 6.371e6  # Earth radius (m)
    return L * R_E * np.sin(theta)**2


# ─────────────────────────────────────────────
# SOLAR WIND INTERACTION
# ─────────────────────────────────────────────

def magnetopause_standoff(B_surface, n_sw, v_sw):
    """
    Chapman-Ferraro distance — where solar wind ram pressure
    balances Earth's magnetic pressure.
    B_surface : Earth surface equatorial field (T)
    n_sw      : solar wind number density (m^-3)
    v_sw      : solar wind velocity (m/s)
    returns: standoff distance (m)
    Typical ~10 Earth radii on dayside.
    """
    R_E = 6.371e6
    B_eq = B_surface  # equatorial surface field ~3e-5 T
    rho_sw = n_sw * m_p  # solar wind mass density
    ram_pressure = 0.5 * rho_sw * v_sw**2
    mag_pressure = B_eq**2 / (2 * mu_0)
    # pressure balance: B^2/(2mu0) ~ rho*v^2/2 scaled by geometry factor ~0.077
    return R_E * (0.077 * mag_pressure / ram_pressure) ** (1/6)


def solar_wind_dynamic_pressure(n_sw, v_sw):
    """
    Ram pressure of solar wind.
    n_sw : particle number density (m^-3)
    v_sw : velocity (m/s)
    returns: pressure (Pa)
    """
    return 0.5 * n_sw * m_p * v_sw**2


def interplanetary_magnetic_field_coupling(Bz_imf):
    """
    Southward IMF drives magnetic reconnection at magnetopause.
    Bz_imf : z-component of interplanetary magnetic field (T)
             negative = southward = couples into magnetosphere
    returns: coupling efficiency (0-1) and reconnection state
    """
    if Bz_imf >= 0:
        return {"efficiency": 0.0, "state": "closed — northward IMF, minimal coupling"}
    else:
        efficiency = min(1.0, abs(Bz_imf) / 20e-9)  # saturates ~20 nT
        return {
            "efficiency": efficiency,
            "state": "open — southward IMF, reconnection active",
            "energy_input_proxy": efficiency  # scales geomagnetic storm intensity
        }


# ─────────────────────────────────────────────
# PARTICLE TRAPPING — VAN ALLEN BELTS
# ─────────────────────────────────────────────

def gyroradius(mass, v_perp, B):
    """
    Radius of circular motion of charged particle in magnetic field.
    mass   : particle mass (kg)
    v_perp : velocity perpendicular to field (m/s)
    B      : magnetic field magnitude (T)
    returns: gyroradius (m)
    """
    return (mass * v_perp) / (abs(e) * B)


def bounce_period(L, v_total, alpha_eq):
    """
    Approximate bounce period of trapped particle between mirror points.
    L       : L-shell (Earth radii)
    v_total : particle speed (m/s)
    alpha_eq: equatorial pitch angle (radians)
    returns: bounce period (s)
    Approximation valid for equatorial pitch angles not near 90 degrees.
    """
    R_E = 6.371e6
    # Field line length approximation
    path = 2 * np.pi * L * R_E * (1.30 - 0.56 * np.sin(alpha_eq))
    return path / v_total


def mirror_point_latitude(alpha_eq):
    """
    Magnetic latitude where particle mirrors (v_parallel -> 0).
    alpha_eq : equatorial pitch angle (radians)
    returns: mirror latitude (radians)
    """
    # sin^2(lambda_m) = cos^6(lambda_m) / sin^2(alpha_eq)  — solved numerically
    from scipy.optimize import brentq
    def equation(lam):
        return np.sin(alpha_eq)**2 - np.cos(lam)**6 / np.sqrt(1 + 3*np.sin(lam)**2)
    try:
        return brentq(equation, 0, np.pi/2 - 1e-6)
    except:
        return np.pi/2  # loss cone — particle precipitates


def loss_cone_angle(r, B_mirror, B_eq):
    """
    Pitch angles below loss cone precipitate into atmosphere.
    B_mirror : field at mirror point (T)
    B_eq     : field at equator on same field line (T)
    returns: loss cone half-angle (radians)
    """
    return np.arcsin(np.sqrt(B_eq / B_mirror))


# ─────────────────────────────────────────────
# MAGNETIC RECONNECTION
# ─────────────────────────────────────────────

def reconnection_rate(v_in, v_alfven):
    """
    Sweet-Parker reconnection rate.
    Energy release rate during field line reconnection.
    v_in     : inflow velocity (m/s)
    v_alfven : Alfven speed in region (m/s)
    returns: dimensionless reconnection rate (0-1)
    Petschek model allows faster rates ~0.1
    """
    return v_in / v_alfven


def alfven_speed(B, n, mass=m_p):
    """
    Speed of magnetic tension waves — governs energy transport
    through magnetosphere and into ionosphere.
    B    : field magnitude (T)
    n    : number density (m^-3)
    mass : particle mass (default proton)
    returns: Alfven speed (m/s)
    """
    rho = n * mass
    return B / np.sqrt(mu_0 * rho)


# ─────────────────────────────────────────────
# GEOMAGNETIC INDICES — observational coupling
# ─────────────────────────────────────────────

def kp_to_magnetopause_compression(kp):
    """
    Empirical: Kp index maps to magnetopause compression.
    kp : 0-9 geomagnetic activity index
    returns: approximate standoff distance (Earth radii)
    Quiet: ~10 Re  Storm: ~6-7 Re  Extreme: <5 Re
    """
    return 11.0 * np.exp(-0.065 * kp)


def dst_to_ring_current_energy(dst_nT):
    """
    Dst index (nT) encodes ring current energy injection.
    Negative Dst = enhanced ring current = geomagnetic storm.
    dst_nT : Dst index in nanotesla (negative during storms)
    returns: approximate ring current energy (J) via Burton formula
    """
    # Dessler-Parker-Sckopke relation
    # delta_B / B0 ~ -2 * E_ring / (3 * E_dipole)
    E_dipole = 8e17  # J — approximate Earth dipole field energy
    return abs(dst_nT) / 30.4e-9 * (2/3) * E_dipole * 1e-9


# ─────────────────────────────────────────────
# ROTATIONAL COUPLING
# Earth rotation change -> magnetic field geometry change
# ─────────────────────────────────────────────

def rotation_rate_to_field_drift(delta_omega):
    """
    Change in Earth rotation rate perturbs core convection patterns
    which shift magnetic field geometry over decades.
    delta_omega : change in angular velocity (rad/s)
                  climate-driven LOD change ~1ms/century
                  = delta_omega ~ 1.4e-14 rad/s/year
    returns: qualitative coupling flag and drift proxy
    This is a slow cascade — years to decades timescale.
    """
    omega_earth = 7.2921e-5  # rad/s
    fractional_change = delta_omega / omega_earth
    return {
        "fractional_rotation_change": fractional_change,
        "core_convection_perturbation": fractional_change * 1e3,  # scaled proxy
        "timescale": "decadal to centennial",
        "cascade_to": ["layer_1_field_geometry", "layer_5_crustal_stress"],
        "note": "climate mass redistribution alters LOD which couples to outer core"
    }


# ─────────────────────────────────────────────
# COUPLING INTERFACES
# Outputs consumed by Layer 0, Layer 2 (Ionosphere), Layer 5 (Lithosphere)
# ─────────────────────────────────────────────

def coupling_state(B_surface, n_sw, v_sw, Bz_imf, kp, delta_omega=0.0):
    """
    Full magnetosphere state vector for adjacent layer consumption.
    """
    standoff = magnetopause_standoff(B_surface, n_sw, v_sw)
    imf      = interplanetary_magnetic_field_coupling(Bz_imf)
    v_A      = alfven_speed(B_surface, n_sw)
    rotation = rotation_rate_to_field_drift(delta_omega)

    return {
        "magnetopause_standoff_m":       standoff,
        "magnetopause_standoff_Re":      standoff / 6.371e6,
        "imf_coupling":                  imf,
        "alfven_speed_ms":               v_A,
        "ring_current_proxy_kp":         kp,
        "estimated_magnetopause_Re":     kp_to_magnetopause_compression(kp),
        "rotation_coupling":             rotation,
        "solar_wind_ram_pressure_Pa":    solar_wind_dynamic_pressure(n_sw, v_sw),
        "cascade_to_ionosphere":         imf["efficiency"] > 0.1,
        "cascade_to_crust":              abs(delta_omega) > 1e-15,
        "field_energy_density_Jm3":      magnetic_energy_density(B_surface),
    }
