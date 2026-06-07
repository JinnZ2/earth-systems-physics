# atmospheric_instability/dynamics.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
Atmospheric instability and wave dynamics.

Instability manifold: Richardson, Brunt-Väisälä, thermal wind, Eady baroclinic
growth, inertial/symmetric instability, gravity wave dispersion, convection.

Climate knob: Arctic amplification lowers lower-level dT/dy; tropical moistening
raises upper-level dT/dy; stratification N shifts — every growth rate moves
simultaneously, deforming the full instability manifold.
"""

import math
from scipy.constants import g as G_STD


# ── Fundamental constants ─────────────────────────────────────────────────────

G = G_STD          # m s⁻²  gravitational acceleration
EADY_COEFF = 0.31  # dimensionless  Eady (1949) maximum growth-rate coefficient


# ── Core instability equations ────────────────────────────────────────────────

def brunt_vaisala_squared(theta: float, dtheta_dz: float) -> float:
    """
    Squared Brunt-Väisälä (buoyancy) frequency.

    N² = (g/θ)(dθ/dz)

    N² > 0 → stable stratification (oscillatory)
    N² < 0 → convective instability (direct overturning)
    N² = 0 → neutral

    Parameters
    ----------
    theta : float
        Potential temperature [K]
    dtheta_dz : float
        Vertical gradient of potential temperature [K m⁻¹]

    Returns
    -------
    float
        N² [s⁻²]
    """
    return (G / theta) * dtheta_dz


def richardson_number(N_sq: float, S_sq: float) -> float:
    """
    Gradient Richardson number.

    Ri = N² / S²

    Kelvin-Helmholtz onset criterion: Ri < 0.25
    Necessary condition for KH instability: Ri < 0.25 somewhere in the profile.

    Parameters
    ----------
    N_sq : float
        N² [s⁻²]
    S_sq : float
        Squared vertical wind shear S² = (dU/dz)² [s⁻²]; must be > 0

    Returns
    -------
    float
        Ri [dimensionless]

    Raises
    ------
    ValueError
        If S_sq <= 0.
    """
    if S_sq <= 0.0:
        raise ValueError("S_sq must be positive (non-zero shear required)")
    return N_sq / S_sq


def kelvin_helmholtz_unstable(Ri: float, threshold: float = 0.25) -> bool:
    """
    Return True if Ri satisfies the KH onset criterion.

    Parameters
    ----------
    Ri : float
        Richardson number [dimensionless]
    threshold : float
        Critical Ri; default 0.25 (Miles-Howard necessary condition)

    Returns
    -------
    bool
    """
    return Ri < threshold


def thermal_wind_shear(
    f: float, T: float, dT_dy: float
) -> float:
    """
    Vertical shear of geostrophic wind (thermal wind equation).

    Λ = dU/dz = -(g / (f · T)) · (dT/dy)

    Positive dT/dy (warm south → cold north in NH) → negative shear (wind
    decreases with height); the sign follows from geostrophic balance.

    Parameters
    ----------
    f : float
        Coriolis parameter [s⁻¹]; must be non-zero
    T : float
        Representative temperature [K]
    dT_dy : float
        Meridional temperature gradient [K m⁻¹]

    Returns
    -------
    float
        dU/dz [s⁻¹]

    Raises
    ------
    ValueError
        If f == 0 (equatorial singularity).
    """
    if f == 0.0:
        raise ValueError("Coriolis parameter f must be non-zero")
    return -(G / (f * T)) * dT_dy


def eady_growth_rate(f: float, Lambda: float, N: float) -> float:
    """
    Maximum Eady baroclinic instability growth rate.

    σ = 0.31 · f · Λ / N

    Governs mid-latitude synoptic storm amplification on a 1–2 day e-folding
    timescale under typical tropospheric conditions.

    Parameters
    ----------
    f : float
        Coriolis parameter [s⁻¹]
    Lambda : float
        Thermal wind shear dU/dz [s⁻¹]
    N : float
        Brunt-Väisälä frequency [s⁻¹]; must be > 0

    Returns
    -------
    float
        Growth rate σ [s⁻¹]

    Raises
    ------
    ValueError
        If N <= 0 (stable stratification required for Eady framework).
    """
    if N <= 0.0:
        raise ValueError("N must be positive for Eady growth rate")
    return EADY_COEFF * abs(f) * abs(Lambda) / N


def inertial_symmetric_unstable(
    f: float, relative_vorticity: float, PV: float
) -> bool:
    """
    Check inertial / symmetric instability conditions.

    Inertial instability:       f · (f + ζ) < 0
    Symmetric instability:      PV · f < 0
      (where PV is the Ertel potential vorticity)

    Either condition suffices for instability.

    Parameters
    ----------
    f : float
        Coriolis parameter [s⁻¹]
    relative_vorticity : float
        Relative vertical vorticity ζ [s⁻¹]
    PV : float
        Ertel potential vorticity [K m² kg⁻¹ s⁻¹]

    Returns
    -------
    bool
        True if either instability criterion is satisfied.
    """
    inertial = f * (f + relative_vorticity) < 0.0
    symmetric = PV * f < 0.0
    return inertial or symmetric


def gravity_wave_frequency(N: float, k_h: float, k_mag: float) -> float:
    """
    Intrinsic frequency of an internal gravity wave (non-rotating limit).

    ω = N · k_h / |k|

    Valid for |k| >> f (sub-inertial waves excluded). Wave breaking (static
    instability) occurs when the wave amplitude drives N²_local < 0.

    Parameters
    ----------
    N : float
        Brunt-Väisälä frequency [s⁻¹]
    k_h : float
        Horizontal wavenumber magnitude √(kx²+ky²) [m⁻¹]
    k_mag : float
        Total wavenumber magnitude |k| = √(kx²+ky²+kz²) [m⁻¹]; must be > 0

    Returns
    -------
    float
        Intrinsic frequency ω [s⁻¹]

    Raises
    ------
    ValueError
        If k_mag <= 0.
    """
    if k_mag <= 0.0:
        raise ValueError("k_mag must be positive")
    return N * k_h / k_mag


def convectively_unstable(N_sq: float) -> bool:
    """
    Return True if the layer is convectively (statically) unstable.

    N² < 0 ↔ dθ/dz < 0 ↔ direct overturning.

    Parameters
    ----------
    N_sq : float
        N² [s⁻²]

    Returns
    -------
    bool
    """
    return N_sq < 0.0


# ── Climate-knob deformation of the instability manifold ─────────────────────

def climate_knob_delta(
    warming_K: float,
    arctic_amp_factor: float = 2.5,
    tropical_moist_factor: float = 1.3,
) -> dict:
    """
    First-order shifts in dT/dy and N from a warming index.

    Arctic amplification (observed ~2–3× global mean) reduces lower-level
    meridional temperature gradient; tropical upper-troposphere moistening
    amplifies upper-level lapse-rate changes and effectively raises N there.
    Both effects shift every instability growth rate simultaneously.

    This is a linearised diagnostic, not a prognostic model.

    Parameters
    ----------
    warming_K : float
        Global-mean surface warming relative to reference state [K]
    arctic_amp_factor : float
        Ratio of Arctic warming to global mean (default 2.5)
    tropical_moist_factor : float
        Upper-level N amplification factor per K of tropical warming (default 1.3)

    Returns
    -------
    dict with keys:
        delta_dTdy_lower : float   Change in lower-level dT/dy [K m⁻¹ per K warming]
        delta_dTdy_upper : float   Change in upper-level dT/dy [K m⁻¹ per K warming]
        N_upper_scale    : float   Multiplicative change in upper N (unitless)
    """
    # Arctic amplification reduces poleward gradient at lower levels
    delta_lower = -warming_K * (arctic_amp_factor - 1.0) * 1e-6  # K m⁻¹ estimate

    # Tropical warm core increases upper-level gradient (warm tropics, cold strat)
    delta_upper = warming_K * (tropical_moist_factor - 1.0) * 0.5e-6

    N_upper_scale = 1.0 + 0.04 * warming_K * (tropical_moist_factor - 1.0)

    return {
        "delta_dTdy_lower": delta_lower,
        "delta_dTdy_upper": delta_upper,
        "N_upper_scale": N_upper_scale,
    }


# ── Coupling state export ─────────────────────────────────────────────────────

def coupling_state(
    theta: float,
    dtheta_dz: float,
    S_sq: float,
    f: float,
    T: float,
    dT_dy: float,
    PV: float,
    relative_vorticity: float = 0.0,
) -> dict:
    """
    Compute and export all instability diagnostics as a state dict.

    Parameters
    ----------
    theta : float
        Potential temperature [K]
    dtheta_dz : float
        dθ/dz [K m⁻¹]
    S_sq : float
        (dU/dz)² [s⁻²]
    f : float
        Coriolis parameter [s⁻¹]
    T : float
        Representative temperature [K]
    dT_dy : float
        Meridional temperature gradient [K m⁻¹]
    PV : float
        Ertel potential vorticity [K m² kg⁻¹ s⁻¹]
    relative_vorticity : float
        Relative vorticity ζ [s⁻¹]; default 0

    Returns
    -------
    dict
    """
    N_sq = brunt_vaisala_squared(theta, dtheta_dz)
    N = math.sqrt(abs(N_sq)) if N_sq >= 0.0 else 0.0
    Ri = richardson_number(N_sq, S_sq) if S_sq > 0.0 else float("inf")
    Lambda = thermal_wind_shear(f, T, dT_dy)
    sigma_eady = eady_growth_rate(f, Lambda, N) if N > 0.0 else 0.0

    return {
        "N_sq": N_sq,
        "N": N,
        "Ri": Ri,
        "KH_unstable": kelvin_helmholtz_unstable(Ri),
        "convectively_unstable": convectively_unstable(N_sq),
        "thermal_wind_shear": Lambda,
        "eady_growth_rate": sigma_eady,
        "inertial_symmetric_unstable": inertial_symmetric_unstable(
            f, relative_vorticity, PV
        ),
    }
