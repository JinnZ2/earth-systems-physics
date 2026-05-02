# layer_minus1_orbital.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Layer -1: Orbital forcing (Milankovitch geometry).
# Sits below Layer 0 in the cascade. Outputs slow time-series of
# Earth's orbital elements (eccentricity, obliquity, climatic
# precession) plus daily insolation, plus derived secular rates that
# propagate upward as forcings:
#     delta_omega_orbital_rads -> Layer 5 (rotation rate perturbation)
#     dM_dipole_per_yr_Am2     -> Layer 0 (geomagnetic dipole drift,
#                                  routed via Layer 5 dynamo response)
#
# Time convention: t_kyr — thousands of years from present epoch.
#     t_kyr = 0   : present (J2000-ish epoch)
#     t_kyr < 0   : past
#     t_kyr > 0   : future
#
# Truncation: this module uses a small fixed-term approximation of
# Berger (1978) astronomical solutions, sufficient for cascade
# coupling at orbital cadence. It is NOT a substitute for La04 or
# P03 when absolute paleo-precision is needed.
#
# Architecture decisions (from design memo):
#   - L-1 -> L5 superposes channel (a) eccentricity-tidal torque +
#     channel (c) precession -> core-mantle inertial coupling.
#     Channel (b) obliquity-LOD via ice mass is handled inside L5
#     via ice_melt_LOD_change to avoid double-counting.
#   - L-1 -> L0 is routed THROUGH L5 (Delta omega -> dynamo response).
#     Direct insolation -> CMB heat flux is rejected at orbital
#     cadence (mantle thermalisation lag ~Gyr).
#   - L-1 emits RATES; the cascade engine integrates over kyr.
#     Downstream layers stay stateless.

import numpy as np

# ─────────────────────────────────────────────
# FUNDAMENTAL CONSTANTS — ORBITAL
# ─────────────────────────────────────────────

S0              = 1361.0        # W/m^2  solar constant at 1 AU
SEC_PER_YEAR    = 3.15576e7     # s
ARCSEC_PER_RAD  = 206264.806

# Present-epoch orbital elements
E0              = 0.016710      # eccentricity (dimensionless)
EPS0_DEG        = 23.439        # obliquity (degrees)
LONG_PERI0_DEG  = 102.94        # longitude of perihelion (degrees)

# Berger 1978 truncated series — leading three amplitudes per element.
# Each entry: (amplitude, period_kyr, phase_deg).
# Sign convention: t_kyr negative = past.
ECCENTRICITY_TERMS = [
    (0.01102, 405.0,  170.7),   # 405 kyr "metronome" (g2 - g5)
    (0.00873, 124.9,  109.1),   # 125 kyr
    (0.00731,  94.9,   -8.7),   #  95 kyr
]

OBLIQUITY_TERMS = [              # amplitude in degrees
    (0.582, 41.0,  86.6),       # 41 kyr — dominant Earth obliquity
    (0.242, 39.7, -45.0),       # secondary
    (0.163, 53.6,  77.0),       # tertiary
]

# Climatic precession parameter e * sin(perihelion).
# Combines eccentricity with longitude of perihelion. Periods 19/22/23 kyr.
PRECESSION_TERMS = [
    (0.018995, 23.716,   44.4),
    (0.016318, 22.428, -144.1),
    (0.013011, 18.976,   79.1),
]

# Earth physical constants used by the derived-rate transfer functions
I_EARTH                 = 8.04e37    # kg·m^2  Earth moment of inertia
M_EARTH_DIPOLE          = 8.0e22     # A·m^2   present geomagnetic dipole
OMEGA0                  = 7.2921e-5  # rad/s   present rotation rate
TAU_DYNAMO_DEFAULT_YR   = 3000.0     # yr      default dynamo response time
                                     # (literature range 1e2 - 1e4 yr)

# Coupling coefficients — wide literature ranges; expose as parameters.
# K_TIDAL_ECC: secular-average tidal-dissipation channel sensitivity
#   to orbital eccentricity (rad/s per unit e).
# K_PRECESSION_CMB: dimensionless efficiency of precessional torque
#   transmitted from mantle to surface rotation rate.
K_TIDAL_ECC_DEFAULT     = 1.0e-13
K_PRECESSION_CMB_DEFAULT= 0.05

# General precession rate (mean rate of equinoxes), present epoch:
# 50.29"/yr -> 2.44e-4 rad/yr -> 7.73e-12 rad/s
PSI_DOT_ARCSEC_PER_YR   = 50.29


# ─────────────────────────────────────────────
# MILANKOVITCH GEOMETRY
# ─────────────────────────────────────────────

def _series(terms, t_kyr, base):
    """Evaluate a truncated cosine series at time t_kyr."""
    total = base
    for amp, period, phase_deg in terms:
        omega = 2.0 * np.pi / period
        total = total + amp * np.cos(omega * t_kyr + np.radians(phase_deg))
    return total


def eccentricity(t_kyr=0.0):
    """
    Earth orbital eccentricity at time t_kyr.
    Truncated Berger 1978 series — three dominant terms (405/125/95 kyr).
    t_kyr  : thousands of years from present (negative = past)
    returns: eccentricity (dimensionless, ~0.0 - 0.07)
    """
    e = _series(ECCENTRICITY_TERMS, t_kyr, E0)
    return float(np.clip(e, 0.0, 0.07))


def obliquity_deg(t_kyr=0.0):
    """
    Earth axial tilt at time t_kyr.
    Truncated 41-kyr-dominated series.
    t_kyr  : thousands of years from present
    returns: obliquity (degrees, ~22 - 24.5)
    """
    eps = _series(OBLIQUITY_TERMS, t_kyr, EPS0_DEG)
    return float(np.clip(eps, 21.5, 24.8))


def climatic_precession(t_kyr=0.0):
    """
    Climatic precession parameter e * sin(varpi) at time t_kyr.
    Sets seasonal contrast — dominant control on monsoons,
    high-latitude summer insolation, and ice-sheet ablation.
    t_kyr  : thousands of years from present
    returns: e * sin(varpi) (dimensionless, ~-0.06 to +0.06)
    """
    return float(_series(PRECESSION_TERMS, t_kyr, 0.0))


def daily_insolation_65N_summer(t_kyr=0.0):
    """
    Daily-mean top-of-atmosphere insolation at 65 N on summer solstice.
    Canonical Milankovitch index — the high-latitude NH summer
    forcing on which classical ice-age theory hinges.
    t_kyr   : thousands of years from present
    returns : insolation (W/m^2)

    Linearised about present-day value 478 W/m^2 with sensitivities
    consistent with Huybers (2006):
        dQ/d(epsilon)        ~ +17 W/m^2 per degree
        dQ/d(climatic_prec)  ~ +191 W/m^2 per unit e*sin(varpi)
        dQ/d(eccentricity)   ~ -120 W/m^2 per unit e (small)
    """
    base    = 478.0
    e_t     = eccentricity(t_kyr)
    eps_t   = obliquity_deg(t_kyr)
    prec_t  = climatic_precession(t_kyr)

    dQ_eps  = 17.0  * (eps_t - EPS0_DEG)
    dQ_pre  = 191.0 * prec_t
    dQ_ecc  = -120.0 * (e_t - E0)

    return base + dQ_eps + dQ_pre + dQ_ecc


# ─────────────────────────────────────────────
# ORBITAL TIME DERIVATIVES
# Used by the L-1 -> L5 transfer function.
# ─────────────────────────────────────────────

def deccentricity_dt_per_yr(t_kyr=0.0, h_kyr=1.0):
    """
    Centred-difference de/dt of the truncated series.
    t_kyr : reference time (kyr)
    h_kyr : step size (kyr)
    returns: de/dt (1/yr)
    """
    de = eccentricity(t_kyr + h_kyr) - eccentricity(t_kyr - h_kyr)
    return de / (2.0 * h_kyr * 1000.0)


def dobliquity_deg_dt_per_yr(t_kyr=0.0, h_kyr=1.0):
    """
    Centred-difference d(epsilon)/dt of the truncated series.
    t_kyr : reference time (kyr)
    h_kyr : step size (kyr)
    returns: d(epsilon)/dt (degrees/yr)
    """
    de = obliquity_deg(t_kyr + h_kyr) - obliquity_deg(t_kyr - h_kyr)
    return de / (2.0 * h_kyr * 1000.0)


def general_precession_rate_rads():
    """
    Present-epoch general precession rate of the equinoxes.
    50.29"/yr converted to rad/s.
    returns: psi_dot (rad/s)
    """
    rad_per_yr = PSI_DOT_ARCSEC_PER_YR / ARCSEC_PER_RAD
    return rad_per_yr / SEC_PER_YEAR


# ─────────────────────────────────────────────
# TRANSFER FUNCTIONS
# ─────────────────────────────────────────────

def orbital_to_rotation_perturbation(t_kyr=0.0,
                                     k_tidal=K_TIDAL_ECC_DEFAULT,
                                     k_precession=K_PRECESSION_CMB_DEFAULT):
    """
    Transfer function: orbital elements -> rotation rate perturbation.
    Superposes two physical channels (per design memo):
        (a) eccentricity-modulated tidal torque (secular average)
        (c) precession -> core-mantle inertial coupling
    Channel (b) obliquity-LOD via ice-mass redistribution is NOT
    included here; it is handled inside layer_5_lithosphere via
    ice_melt_LOD_change to avoid double counting.

    t_kyr        : time (kyr from present)
    k_tidal      : eccentricity-tidal coupling coefficient (rad/s per e)
    k_precession : fraction of precession torque transmitted to mantle

    returns: dict with channel-resolved and total delta_omega (rad/s)
    """
    e_t     = eccentricity(t_kyr)
    psi_dot = general_precession_rate_rads()

    domega_tidal      = -k_tidal * e_t
    domega_precession = -k_precession * psi_dot

    total = domega_tidal + domega_precession

    return {
        "delta_omega_tidal_rads":      domega_tidal,
        "delta_omega_precession_rads": domega_precession,
        "delta_omega_orbital_rads":    total,
        "channel_a_eccentricity":      e_t,
        "channel_c_psi_dot_rads":      psi_dot,
        "k_tidal":                     k_tidal,
        "k_precession":                k_precession,
        "note": ("obliquity-LOD via ice mass routes through "
                 "layer_5.ice_melt_LOD_change to avoid double-counting"),
    }


def rotation_to_dipole_drift(delta_omega_rads,
                             tau_dynamo_yr=TAU_DYNAMO_DEFAULT_YR,
                             M0=M_EARTH_DIPOLE):
    """
    Transfer function: L5 rotation perturbation -> L0 dipole drift.
    Routed through L5 per design memo: orbital -> rotation -> dynamo
    response. Direct insolation -> CMB heat flux is rejected at
    orbital cadence (mantle thermalisation ~Gyr lag).

    Linearised first-order response:
        dM/dt = - M0 * (delta_omega / omega0) / tau_dynamo

    delta_omega_rads : rotation perturbation (rad/s)
    tau_dynamo_yr    : dynamo response timescale (yr); literature
                       range 1e2 - 1e4 yr
    M0               : reference dipole moment (A·m^2)

    returns: dM/dt (A·m^2 per year)
    """
    if tau_dynamo_yr <= 0:
        return 0.0
    fractional = delta_omega_rads / OMEGA0
    return -M0 * fractional / tau_dynamo_yr


# ─────────────────────────────────────────────
# COUPLING INTERFACE
# Outputs consumed by Layer 0 (dipole drift) and Layer 5 (rotation).
# ─────────────────────────────────────────────

def coupling_state(t_kyr=0.0,
                   k_tidal=K_TIDAL_ECC_DEFAULT,
                   k_precession=K_PRECESSION_CMB_DEFAULT,
                   tau_dynamo_yr=TAU_DYNAMO_DEFAULT_YR):
    """
    Layer -1 state vector for cascade consumption.
    t_kyr         : time (kyr from present, default = present epoch)
    k_tidal       : eccentricity-tidal coupling coefficient (rad/s per e)
    k_precession  : precession -> CMB efficiency (dimensionless)
    tau_dynamo_yr : dynamo response timescale (yr)

    returns: dict of orbital elements, rates, and cascade-ready
    forcings (delta_omega_orbital_rads, dM_dipole_per_yr_Am2).
    """
    e_t    = eccentricity(t_kyr)
    eps_t  = obliquity_deg(t_kyr)
    prec_t = climatic_precession(t_kyr)
    Q_65N  = daily_insolation_65N_summer(t_kyr)

    rot   = orbital_to_rotation_perturbation(t_kyr, k_tidal, k_precession)
    dM_dt = rotation_to_dipole_drift(rot["delta_omega_orbital_rads"],
                                     tau_dynamo_yr=tau_dynamo_yr)

    return {
        "epoch_kyr":                   t_kyr,
        "eccentricity":                e_t,
        "obliquity_deg":               eps_t,
        "climatic_precession":         prec_t,
        "insolation_65N_summer_Wm2":   Q_65N,
        "deccentricity_per_yr":        deccentricity_dt_per_yr(t_kyr),
        "dobliquity_deg_per_yr":       dobliquity_deg_dt_per_yr(t_kyr),
        "psi_dot_rads":                rot["channel_c_psi_dot_rads"],
        # cascade forcings consumed downstream
        "delta_omega_orbital_rads":    rot["delta_omega_orbital_rads"],
        "delta_omega_tidal_rads":      rot["delta_omega_tidal_rads"],
        "delta_omega_precession_rads": rot["delta_omega_precession_rads"],
        "dM_dipole_per_yr_Am2":        dM_dt,
        "tau_dynamo_yr":               tau_dynamo_yr,
        # provenance
        "cascade_to_lithosphere":      ("rotation perturbation -> length "
                                        "of day, core-mantle coupling"),
        "cascade_to_em_via_litho":     ("rotation -> dynamo response -> "
                                        "dipole drift dM/dt"),
        "rejected_pathway":            ("insolation -> CMB heat flux "
                                        "(mantle thermalisation ~Gyr)"),
        "note": ("Berger 1978 truncated 3-term series; coupling "
                 "coefficients (k_tidal, k_precession, tau_dynamo) "
                 "have wide literature ranges and are exposed as "
                 "parameters."),
    }
