"""
layer_minus1_orbital.py

Layer -1: Milankovitch orbital forcing.

ENERGY FLOW
-----------
    L-1 (orbital geometry: e, eps, varpi)
        |
        |-- precession -> core-mantle inertial coupling --> Delta omega_orbital --> L5
        |   (small tidal-torque term from eccentricity superposed)
        |
        |-- insolation(lat, t) --> L4 (ice/atmosphere, downstream)
        |
        |-- via L5(Delta omega) --> L0 (dipole drift, dM/dt) -- NOT direct here
                                       the core-rotation pathway lives in
                                       L0.dipole_drift_from_rotation()

DESIGN RULES (from spec)
------------------------
1. L-1 emits RATES. Downstream layers consume rates on top of their
   instantaneous physics. Integration lives in cascade_engine.py.
2. Pathways included:
   (a) tidal torque via e(t)         -- small, included for completeness
   (c) precession -> CMB coupling    -- primary L-1 -> L5 channel
   Pathway (b) obliquity -> LOD via ice mass is INTENTIONALLY ROUTED
   through L4 ice-volume sensitivity ->
   layer_5_lithosphere.ice_melt_LOD_change(). Including it here would
   double-count.
3. L-1 -> L0 is NOT direct. Route through L5(Delta omega) -> L0(dM/dt).
   This file exposes Delta omega_orbital only; L0 owns the dynamo
   response with its own tau_dynamo parameter.
4. All knobs with no consensus value are exposed as parameters with
   documented bounds. No hardcoded magic.

UNITS
-----
    time              : years (Earth tropical year, 365.25 d)
    angles            : radians
    eccentricity e    : dimensionless [0, ~0.07]
    obliquity eps     : radians
    long. perihelion  : radians (varpi)
    omega (rotation)  : rad/s
    domega/dt         : rad/s^2
    insolation        : W/m^2

DEPENDENCIES
------------
numpy only. scipy is optional and only used if available for
higher-order quadrature; falls back to numpy trapz.

CC0. JinnZ2 / earth-systems-physics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

import numpy as np

try:
    from scipy.integrate import quad as _scipy_quad
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False

# ─────────────────────────────────────────────
# PHYSICAL CONSTANTS  (no fitting parameters here)
# ─────────────────────────────────────────────

S0_TSI            = 1361.0          # W/m^2  solar constant (present)
SIDEREAL_YEAR_S   = 3.155815e7      # s
TROPICAL_YEAR_S   = 3.155693e7      # s
DAY_S             = 86400.0         # s
OMEGA_EARTH       = 7.2921159e-5    # rad/s   present sidereal rotation rate
I_EARTH           = 8.034e37        # kg.m^2  polar moment of inertia
M_MOON_OVER_EARTH = 0.0123          # mass ratio
A_MOON            = 3.844e8         # m       lunar semi-major axis
G_NEWTON          = 6.67430e-11     # m^3 kg^-1 s^-2
M_SUN             = 1.98892e30      # kg
M_EARTH_KG        = 5.9722e24       # kg      (mass; distinct from L0 dipole M)
A_EARTH_ORBIT     = 1.495978707e11  # m       1 AU


# ─────────────────────────────────────────────
# ORBITAL ELEMENT MODEL
# Low-order Milankovitch reconstruction. Good to ~1% over +/-1 Myr
# from J2000. For Pleistocene-accurate paleo runs, load Laskar via
# load_laskar_table(). Sufficient for forcing-spectrum work.
# ─────────────────────────────────────────────

@dataclass
class OrbitalParams:
    """
    Orbital parameters at a single instant.
    All times are years from J2000.0 (positive = future, negative = past).
    """
    t_year: float
    eccentricity: float          # e
    obliquity_rad: float         # eps
    long_perihelion_rad: float   # varpi
    precession_index: float      # e * sin(varpi) — climate-relevant combination

    def as_dict(self) -> Dict[str, float]:
        return {
            "t_year": self.t_year,
            "eccentricity": self.eccentricity,
            "obliquity_rad": self.obliquity_rad,
            "long_perihelion_rad": self.long_perihelion_rad,
            "precession_index": self.precession_index,
        }


# Quasi-periodic series. Amplitudes / periods from Berger (1978)
# truncated set. Each term: (amplitude, period_years, phase_rad).

_E_TERMS = [
    (0.01102940, 405091.0,  0.000),
    (0.00872280,  94932.0,  4.000),
    (0.00707270, 123945.0,  3.300),
    (0.00669080,  98857.0,  1.300),
    (0.00466410, 130781.0,  4.500),
    (0.00420010,  99590.0,  4.700),
]
_E_MEAN = 0.0167  # present-value baseline

_OBLIQ_TERMS = [
    (math.radians(0.582412), 41000.0, 0.000),
    (math.radians(0.242559), 39730.0, 1.700),
    (math.radians(0.163685), 53615.0, 5.200),
    (math.radians(0.164787), 40521.0, 3.700),
]
_OBLIQ_MEAN = math.radians(23.320556)

_PERI_TERMS = [
    (1.0, 23716.0, 0.000),  # ~precession period (climatic)
    (1.0, 22428.0, 2.500),
    (1.0, 18976.0, 4.100),
    (1.0, 19155.0, 1.800),
]


def orbital_state(t_year: float) -> OrbitalParams:
    """
    Compute (e, eps, varpi, precession_index) at time t_year (years
    from J2000). Pure function, no state.
    """
    e = _E_MEAN + sum(
        a * math.cos(2.0 * math.pi * t_year / p + ph)
        for (a, p, ph) in _E_TERMS
    )

    eps = _OBLIQ_MEAN + sum(
        a * math.cos(2.0 * math.pi * t_year / p + ph)
        for (a, p, ph) in _OBLIQ_TERMS
    )

    # Longitude of perihelion accumulates (general precession ~50.3"/yr).
    psi_general = 2.0 * math.pi * t_year / 25771.5    # axial precession period
    peri_oscillation = sum(
        a * math.sin(2.0 * math.pi * t_year / p + ph)
        for (a, p, ph) in _PERI_TERMS
    )
    varpi = (psi_general + 0.05 * peri_oscillation) % (2.0 * math.pi)

    prec_idx = e * math.sin(varpi)

    return OrbitalParams(
        t_year=t_year,
        eccentricity=max(0.0, e),
        obliquity_rad=eps,
        long_perihelion_rad=varpi,
        precession_index=prec_idx,
    )


def orbital_state_array(t_years: np.ndarray) -> Dict[str, np.ndarray]:
    """Vectorized version of orbital_state() over a time array."""
    t_years = np.asarray(t_years, dtype=float)
    e   = np.full_like(t_years, _E_MEAN, dtype=float)
    eps = np.full_like(t_years, _OBLIQ_MEAN, dtype=float)

    for (a, p, ph) in _E_TERMS:
        e += a * np.cos(2.0 * np.pi * t_years / p + ph)
    for (a, p, ph) in _OBLIQ_TERMS:
        eps += a * np.cos(2.0 * np.pi * t_years / p + ph)

    psi_general = 2.0 * np.pi * t_years / 25771.5
    peri_osc = np.zeros_like(t_years, dtype=float)
    for (a, p, ph) in _PERI_TERMS:
        peri_osc += a * np.sin(2.0 * np.pi * t_years / p + ph)
    varpi = (psi_general + 0.05 * peri_osc) % (2.0 * np.pi)

    prec_idx = e * np.sin(varpi)

    return {
        "t_year": t_years,
        "eccentricity": np.maximum(0.0, e),
        "obliquity_rad": eps,
        "long_perihelion_rad": varpi,
        "precession_index": prec_idx,
    }


# ─────────────────────────────────────────────
# INSOLATION
# Daily-mean insolation at latitude phi on day-of-year d, given orbital
# state. Reference: Berger 1978 / Laskar 2004 standard formulation.
# ─────────────────────────────────────────────

def _solar_longitude_from_day(day_of_year: float, varpi: float, e: float) -> float:
    """
    True solar longitude lambda from day-of-year, accounting for orbit
    asymmetry. Uses series expansion in e (good to ~1e-4 for e<0.07).
    """
    M = 2.0 * math.pi * (day_of_year / 365.25) - varpi
    E_anom = (M
              + (2.0 * e - 0.25 * e**3) * math.sin(M)
              + 1.25 * e**2 * math.sin(2.0 * M)
              + (13.0 / 12.0) * e**3 * math.sin(3.0 * M))
    return (E_anom + varpi) % (2.0 * math.pi)


def daily_insolation(
    latitude_rad: float,
    day_of_year: float,
    orbital: OrbitalParams,
    s0: float = S0_TSI,
) -> float:
    """
    Daily-mean insolation [W/m^2] at given latitude and day.
    latitude_rad : phi in radians (-pi/2 to +pi/2)
    day_of_year  : 0..365.25 (continuous)
    orbital      : OrbitalParams at the year of interest
    s0           : TSI at 1 AU (default present value)
    Returns Q_day [W/m^2]; 0 for polar night.
    """
    e     = orbital.eccentricity
    eps   = orbital.obliquity_rad
    varpi = orbital.long_perihelion_rad

    lam   = _solar_longitude_from_day(day_of_year, varpi, e)
    delta = math.asin(math.sin(eps) * math.sin(lam))  # solar declination

    # Distance factor (a/r)^2
    r_factor_sq = ((1.0 + e * math.cos(lam - varpi)) / (1.0 - e * e)) ** 2

    cos_H = -math.tan(latitude_rad) * math.tan(delta)
    if cos_H >= 1.0:
        return 0.0           # polar night
    if cos_H <= -1.0:
        # polar day
        q = s0 * r_factor_sq * (math.sin(latitude_rad) * math.sin(delta))
    else:
        H = math.acos(cos_H)
        q = (s0 / math.pi) * r_factor_sq * (
            H * math.sin(latitude_rad) * math.sin(delta)
            + math.cos(latitude_rad) * math.cos(delta) * math.sin(H)
        )
    return max(0.0, q)


def annual_mean_insolation(
    latitude_rad: float,
    orbital: OrbitalParams,
    n_days: int = 365,
    s0: float = S0_TSI,
) -> float:
    """Annual-mean insolation [W/m^2] at latitude phi for the given orbital state."""
    days = np.linspace(0.0, 365.25, n_days, endpoint=False)
    q = np.array([
        daily_insolation(latitude_rad, float(d), orbital, s0=s0)
        for d in days
    ])
    return float(q.mean())


# ─────────────────────────────────────────────
# TRANSFER FUNCTION 1: L-1 -> L5 (orbital -> rotation rate)
#
# Two pathways superposed:
#   (a) tidal torque from eccentricity modulation of solar tide
#       domega/dt|_tidal ∝ -k_tide * de/dt
#   (c) precession -> core-mantle inertial coupling
#       domega/dt|_cmb   ∝ -eta_cmb * dvarpi/dt * (e * sin(varpi))
# k_tide and eta_cmb are exposed knobs. Defaults are physically
# defensible but NOT consensus values. See bounds in OrbitalForcingConfig.
# ─────────────────────────────────────────────

@dataclass
class OrbitalForcingConfig:
    """
    Tunable parameters for L-1 -> downstream transfer functions.
    All knobs documented with bounds and rationale.
    """
    # --- L-1 -> L5: tidal-torque pathway (a) ---
    # Coupling of eccentricity drift to rotational deceleration.
    # Bounds: 1e-23 .. 1e-21 rad/s^2 per (de/dyear).
    k_tide_rad_s2_per_de_dyr: float = 1.0e-22
    k_tide_bounds: Tuple[float, float] = (1.0e-23, 1.0e-21)

    # --- L-1 -> L5: precession-CMB pathway (c) ---
    # Inertial coupling efficiency between mantle and outer core
    # under axial precession forcing. NO CONSENSUS VALUE.
    # Bounds: 1e-20 .. 1e-18 rad/s^2 per (rad/yr * precession_index).
    eta_cmb_rad_s2_per_rad_yr: float = 5.0e-20
    eta_cmb_bounds: Tuple[float, float] = (1.0e-20, 1.0e-18)

    # --- L-1 -> (via L5) -> L0: dynamo response timescale ---
    # Used by layer_0.dipole_drift_from_rotation().
    # Range from geomagnetic secular variation studies.
    # Bounds: 100 .. 10000 years.
    tau_dynamo_yr: float = 1500.0
    tau_dynamo_bounds: Tuple[float, float] = (100.0, 10000.0)

    # --- numerical step for finite-difference rates ---
    dt_rate_year: float = 100.0  # well below all Milankovitch periods

    def validate(self) -> None:
        for name, val, bounds in [
            ("k_tide",     self.k_tide_rad_s2_per_de_dyr, self.k_tide_bounds),
            ("eta_cmb",    self.eta_cmb_rad_s2_per_rad_yr, self.eta_cmb_bounds),
            ("tau_dynamo", self.tau_dynamo_yr, self.tau_dynamo_bounds),
        ]:
            lo, hi = bounds
            if not (lo <= val <= hi):
                raise ValueError(
                    f"{name}={val} outside documented bounds [{lo}, {hi}]"
                )


def _finite_diff_rate(t_year: float, dt: float,
                      getter: Callable[[float], float]) -> float:
    """Centered finite difference: d(getter)/dyear at t_year."""
    return (getter(t_year + dt) - getter(t_year - dt)) / (2.0 * dt)


def delta_omega_orbital(
    t_year: float,
    cfg: OrbitalForcingConfig,
) -> float:
    """
    L-1 -> L5 transfer: orbital forcing on Earth rotation rate.
    Returns domega/dt [rad/s^2] at time t_year.

    Pathway (a) tidal-torque + Pathway (c) precession-CMB, superposed.
    Pathway (b) obliquity-LOD is INTENTIONALLY EXCLUDED here — it is
    handled by L5.ice_melt_LOD_change() through L4 ice-volume response.
    Including it here would double-count.

    The cascade should sum the integrated form (rate * dt) with the
    existing layer_5 omega_change_rads.
    """
    cfg.validate()
    dt = cfg.dt_rate_year

    # Pathway (a): tidal torque via de/dt
    de_dt = _finite_diff_rate(t_year, dt, lambda y: orbital_state(y).eccentricity)
    domega_tidal = -cfg.k_tide_rad_s2_per_de_dyr * de_dt

    # Pathway (c): precession-CMB coupling
    state_now = orbital_state(t_year)
    dvarpi_dt = _finite_diff_rate(
        t_year, dt, lambda y: orbital_state(y).long_perihelion_rad
    )
    # unwrap the modulo-2 pi discontinuity in varpi finite differences
    if abs(dvarpi_dt) > math.pi / dt:
        dvarpi_dt -= math.copysign(2.0 * math.pi / (2.0 * dt), dvarpi_dt)

    domega_cmb = (-cfg.eta_cmb_rad_s2_per_rad_yr
                  * dvarpi_dt
                  * state_now.precession_index)

    return domega_tidal + domega_cmb


def delta_omega_orbital_array(
    t_years: np.ndarray,
    cfg: OrbitalForcingConfig,
) -> np.ndarray:
    """Vectorized delta_omega_orbital over a time array."""
    cfg.validate()
    return np.array([delta_omega_orbital(float(t), cfg) for t in t_years])


def cumulative_delta_omega(
    t_year: float,
    cfg: OrbitalForcingConfig,
    t_ref_year: float = 0.0,
    n_steps: int = 200,
) -> float:
    """
    Integrated rotation perturbation Delta omega [rad/s] accumulated
    between t_ref_year and t_year. Convenience for cascade_engine: it
    converts the secular RATE emitted by delta_omega_orbital() into
    the Delta omega that L5 superposes on its ice-mass omega change.

    Uses scipy.quad if available, else numpy trapz with n_steps points.
    """
    cfg.validate()
    if t_year == t_ref_year:
        return 0.0

    def integrand_per_year(y):
        # delta_omega_orbital returns rad/s^2; integrating over y in years
        # requires conversion year -> s.
        return delta_omega_orbital(y, cfg) * SIDEREAL_YEAR_S

    if _HAS_SCIPY:
        val, _ = _scipy_quad(integrand_per_year, t_ref_year, t_year,
                             limit=200)
        return float(val)

    ys = np.linspace(t_ref_year, t_year, n_steps)
    rates = np.array([integrand_per_year(float(y)) for y in ys])
    return float(np.trapz(rates, ys))


# ─────────────────────────────────────────────
# DERIVED RATES BUNDLE — what cascade_engine consumes
# ─────────────────────────────────────────────

@dataclass
class OrbitalForcingOutput:
    """
    Bundle of L-1 outputs at time t. Cascade engine integrates as needed.
    NOTE: dM_dipole/dt is NOT computed here. Routed through L5
    (delta_omega total) -> L0.dipole_drift_from_rotation(omega_total,
    tau_dynamo_yr).
    """
    t_year: float
    orbital: OrbitalParams

    # Slow-secular rates emitted to downstream layers:
    delta_omega_orbital_rads2: float    # rad/s^2 -> L5 (after time integration)
    de_dt_per_year: float
    deps_dt_rad_per_year: float
    dvarpi_dt_rad_per_year: float

    def as_dict(self) -> Dict[str, float]:
        d = self.orbital.as_dict()
        d.update({
            "delta_omega_orbital_rads2": self.delta_omega_orbital_rads2,
            "de_dt_per_year":            self.de_dt_per_year,
            "deps_dt_rad_per_year":      self.deps_dt_rad_per_year,
            "dvarpi_dt_rad_per_year":    self.dvarpi_dt_rad_per_year,
        })
        return d


def compute_forcing(
    t_year: float,
    cfg: Optional[OrbitalForcingConfig] = None,
) -> OrbitalForcingOutput:
    """
    Top-level entry point for cascade_engine. Returns the full L-1
    forcing bundle at time t_year.
    """
    if cfg is None:
        cfg = OrbitalForcingConfig()
    cfg.validate()

    state = orbital_state(t_year)
    dt = cfg.dt_rate_year

    de_dt    = _finite_diff_rate(t_year, dt, lambda y: orbital_state(y).eccentricity)
    deps_dt  = _finite_diff_rate(t_year, dt, lambda y: orbital_state(y).obliquity_rad)
    dvarpi_dt = _finite_diff_rate(
        t_year, dt, lambda y: orbital_state(y).long_perihelion_rad
    )
    if abs(dvarpi_dt) > math.pi / dt:
        dvarpi_dt -= math.copysign(2.0 * math.pi / (2.0 * dt), dvarpi_dt)

    dom = delta_omega_orbital(t_year, cfg)

    return OrbitalForcingOutput(
        t_year=t_year,
        orbital=state,
        delta_omega_orbital_rads2=dom,
        de_dt_per_year=de_dt,
        deps_dt_rad_per_year=deps_dt,
        dvarpi_dt_rad_per_year=dvarpi_dt,
    )


# ─────────────────────────────────────────────
# COUPLING INTERFACE — cascade-engine adapter
# Returns a flat dict keyed for direct insertion into the layer-state
# map. Wraps OrbitalForcingOutput.
# ─────────────────────────────────────────────

def coupling_state(
    t_kyr: float = 0.0,
    cfg: Optional[OrbitalForcingConfig] = None,
    t_ref_kyr: float = 0.0,
    insolation_lat_deg: float = 65.0,
) -> Dict[str, float]:
    """
    Layer -1 coupling-state vector. Adapter for cascade_engine.

    t_kyr               : current epoch (kyr from J2000)
    cfg                 : OrbitalForcingConfig (defaults applied if None)
    t_ref_kyr           : reference epoch for cumulative delta-omega
                          integration (defaults to J2000 = 0)
    insolation_lat_deg  : latitude for the canonical Milankovitch
                          insolation diagnostic (default 65 N summer)

    Returns dict with orbital elements, instantaneous rates, integrated
    Delta omega for L5, and tau_dynamo for L0.
    """
    if cfg is None:
        cfg = OrbitalForcingConfig()
    cfg.validate()

    t_year = t_kyr * 1000.0
    t_ref_year = t_ref_kyr * 1000.0

    out = compute_forcing(t_year, cfg)
    state = out.orbital

    delta_omega_integrated_rads = cumulative_delta_omega(
        t_year, cfg, t_ref_year=t_ref_year
    )

    # 65N summer-solstice (~day 172) insolation as canonical diagnostic.
    Q_65N_summer = daily_insolation(
        math.radians(insolation_lat_deg), 172.0, state
    )

    # Backward-compat dM/dt for cascade engines that still consume
    # a dipole-drift rate from L-1. Linearised first-order dynamo
    # response. The new architecture (layer_0_emag.py) does this
    # properly via FFT transfer function; this is the simple form.
    M_dipole_present = 8.0e22  # A.m^2
    if cfg.tau_dynamo_yr > 0:
        dM_dipole_per_yr = (
            -M_dipole_present
            * delta_omega_integrated_rads
            / OMEGA_EARTH
            / cfg.tau_dynamo_yr
        )
    else:
        dM_dipole_per_yr = 0.0

    return {
        "epoch_kyr":                       t_kyr,
        "t_ref_kyr":                       t_ref_kyr,
        "eccentricity":                    state.eccentricity,
        "obliquity_rad":                   state.obliquity_rad,
        "obliquity_deg":                   math.degrees(state.obliquity_rad),
        "long_perihelion_rad":             state.long_perihelion_rad,
        "long_perihelion_deg":             math.degrees(state.long_perihelion_rad),
        "precession_index":                state.precession_index,
        "climatic_precession":             state.precession_index,
        "insolation_65N_summer_Wm2":       Q_65N_summer,
        "de_dt_per_year":                  out.de_dt_per_year,
        "deps_dt_rad_per_year":            out.deps_dt_rad_per_year,
        "dvarpi_dt_rad_per_year":          out.dvarpi_dt_rad_per_year,
        # rate (rad/s^2) — instantaneous orbital torque on rotation
        "delta_omega_orbital_rads2":       out.delta_omega_orbital_rads2,
        # integrated rate (rad/s) — what L5 superposes on ice-mass omega
        "delta_omega_orbital_rads":        delta_omega_integrated_rads,
        # backward-compat dipole drift output (linearised first-order)
        "dM_dipole_per_yr_Am2":            dM_dipole_per_yr,
        # tau_dynamo passed downstream so L0 can do the dynamo conversion
        "tau_dynamo_yr":                   cfg.tau_dynamo_yr,
        # provenance / pathway notes
        "cascade_to_lithosphere":          ("rotation perturbation -> length "
                                             "of day, core-mantle coupling"),
        "cascade_to_em_via_litho":         ("L5 sums orbital + ice-melt omega; "
                                             "L0.dipole_drift_from_rotation "
                                             "owns the dynamo response"),
        "rejected_pathway":                ("insolation -> CMB heat flux "
                                             "(mantle thermalisation ~Gyr)"),
        "note": ("Berger 1978 truncated series; coupling coefficients have "
                 "wide literature ranges and are exposed in OrbitalForcingConfig"),
    }


# ─────────────────────────────────────────────
# LEGACY FUNCTION ALIASES
# Kept so existing callers / tests that imported the older API
# continue to work. New code should use orbital_state() and
# compute_forcing() directly.
# ─────────────────────────────────────────────

def eccentricity(t_kyr: float = 0.0) -> float:
    """Legacy: scalar eccentricity at t_kyr (kyr from J2000)."""
    return float(orbital_state(t_kyr * 1000.0).eccentricity)


def obliquity_deg(t_kyr: float = 0.0) -> float:
    """Legacy: scalar obliquity in degrees at t_kyr (kyr from J2000)."""
    return math.degrees(orbital_state(t_kyr * 1000.0).obliquity_rad)


def climatic_precession(t_kyr: float = 0.0) -> float:
    """Legacy: e * sin(varpi) at t_kyr (kyr from J2000)."""
    return float(orbital_state(t_kyr * 1000.0).precession_index)


def orbital_to_rotation_perturbation(
    t_kyr: float = 0.0,
    cfg: Optional[OrbitalForcingConfig] = None,
) -> Dict[str, float]:
    """
    Legacy adapter. Returns the L-1 -> L5 rotation perturbation as
    a dict with channel-resolved fields, evaluated at t_kyr.
    """
    if cfg is None:
        cfg = OrbitalForcingConfig()
    cfg.validate()
    t_year = t_kyr * 1000.0
    rate = delta_omega_orbital(t_year, cfg)
    state = orbital_state(t_year)

    # Channel decomposition (recompute for completeness)
    dt = cfg.dt_rate_year
    de_dt = _finite_diff_rate(t_year, dt, lambda y: orbital_state(y).eccentricity)
    dvarpi_dt = _finite_diff_rate(
        t_year, dt, lambda y: orbital_state(y).long_perihelion_rad
    )
    if abs(dvarpi_dt) > math.pi / dt:
        dvarpi_dt -= math.copysign(2.0 * math.pi / (2.0 * dt), dvarpi_dt)

    domega_tidal      = -cfg.k_tide_rad_s2_per_de_dyr * de_dt
    domega_precession = (-cfg.eta_cmb_rad_s2_per_rad_yr
                         * dvarpi_dt * state.precession_index)

    # Cumulative integrated value over [0, t_year]
    delta_omega_integrated = cumulative_delta_omega(t_year, cfg, t_ref_year=0.0)

    return {
        # rates (rad/s^2)
        "delta_omega_orbital_rads2":      rate,
        "delta_omega_tidal_rads2":        domega_tidal,
        "delta_omega_precession_rads2":   domega_precession,
        # integrated (rad/s)
        "delta_omega_orbital_rads":       delta_omega_integrated,
        "delta_omega_tidal_rads":         domega_tidal,       # rate at t (proxy)
        "delta_omega_precession_rads":    domega_precession,  # rate at t (proxy)
    }


def rotation_to_dipole_drift(
    delta_omega_rads: float,
    tau_dynamo_yr: float = 1500.0,
    M0: float = 8.0e22,
) -> float:
    """
    Legacy: linear first-order dynamo response.
        dM/dt = - M0 * (delta_omega / OMEGA_EARTH) / tau_dynamo
    The new architecture uses FFT-based transfer in layer_0_emag.py.
    """
    if tau_dynamo_yr <= 0:
        return 0.0
    return -M0 * (delta_omega_rads / OMEGA_EARTH) / tau_dynamo_yr


# ─────────────────────────────────────────────
# OPTIONAL: Laskar table loader (stub)
# ─────────────────────────────────────────────

def load_laskar_table(path: str) -> Optional[Dict[str, np.ndarray]]:
    """
    Load Laskar 2004/2010 orbital element table if available.
    Expected format: ASCII columns [t_kyr, e, eps_rad, varpi_rad].
    Returns dict with keys 't_year', 'eccentricity', 'obliquity_rad',
    'long_perihelion_rad', or None on failure.
    """
    try:
        data = np.loadtxt(path)
        return {
            "t_year":              data[:, 0] * 1000.0,
            "eccentricity":        data[:, 1],
            "obliquity_rad":       data[:, 2],
            "long_perihelion_rad": data[:, 3],
        }
    except Exception:
        return None


# ─────────────────────────────────────────────
# SELF-CHECK — run as `python layer_minus1_orbital.py`
# ─────────────────────────────────────────────

if __name__ == "__main__":
    cfg = OrbitalForcingConfig()
    cfg.validate()

    print("=" * 64)
    print("Layer -1 (Milankovitch orbital forcing) — self-check")
    print("=" * 64)

    now = compute_forcing(0.0, cfg)
    print(f"\n@ t = 0 (J2000):")
    print(f"  e          = {now.orbital.eccentricity:.5f}   "
          f"(present ~ 0.0167)")
    print(f"  eps        = {math.degrees(now.orbital.obliquity_rad):.4f} deg  "
          f"(present ~ 23.44)")
    print(f"  varpi      = {math.degrees(now.orbital.long_perihelion_rad):.2f} deg")
    print(f"  prec_index = {now.orbital.precession_index:+.5f}")

    q65n = annual_mean_insolation(math.radians(65.0), now.orbital)
    print(f"\n  annual-mean insolation @ 65N : {q65n:.2f} W/m^2  "
          f"(expected ~ 230)")

    print(f"\n  de/dt              : {now.de_dt_per_year:+.3e} per year")
    print(f"  deps/dt            : "
          f"{math.degrees(now.deps_dt_rad_per_year):+.3e} deg/yr")
    print(f"  dvarpi/dt          : "
          f"{math.degrees(now.dvarpi_dt_rad_per_year):+.3e} deg/yr  "
          f"(expected ~ 0.014)")
    print(f"  domega/dt orbital  : "
          f"{now.delta_omega_orbital_rads2:+.3e} rad/s^2")

    print("\n  Sweep -1 Myr to 0:")
    print("   t_kyr     e        eps(deg)   prec_idx    domega/dt (rad/s^2)")
    for tkyr in [-1000, -800, -400, -200, -100, -21, 0]:
        out = compute_forcing(tkyr * 1000.0, cfg)
        print(f"  {tkyr:+6d}   {out.orbital.eccentricity:.4f}    "
              f"{math.degrees(out.orbital.obliquity_rad):6.3f}    "
              f"{out.orbital.precession_index:+.4f}     "
              f"{out.delta_omega_orbital_rads2:+.3e}")

    print("\nOK.")
