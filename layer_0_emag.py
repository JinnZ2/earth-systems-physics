"""
layer_0_emag.py

STATUS: ALTERNATE API — see layer_0_electromagnetics.py for the primary
per-instant coupling interface used by cascade_engine.py.
This module provides the FFT-based time-series transfer function
(L5 Δω history → L0 dM/dt) needed once the cascade is refactored to
operate on histories rather than single instants. It does NOT yet replace
layer_0_electromagnetics.py.

Layer 0 (alternate API): Electromagnetic dynamo response over a time
series window. Standalone module — does NOT yet replace
layer_0_electromagnetics.py for the cascade engine. The existing
per-instant L0 coupling_state continues to be the wired entry point.
This module provides the FFT-based time-series transfer function
that L5(Delta omega total) -> L0(dM/dt) needs once the cascade is
refactored to operate on histories rather than single-instant
states.

ENERGY FLOW
-----------
    L-1 (Milankovitch) ---> Delta omega_orbital --|
                                                  +---> Delta omega_total(t)
    L5 internal (ice, mantle) -> Delta omega_int -|         |
                                                            v
                                           L0 dynamo response  -->  dM/dt
                                                                    M_dipole(t)
                                                                    B_surface(t)
                                                                          |
                                                                          v
                                                                 L1 (magnetosphere)

THE BURDEN-OF-PROOF SHIFT
-------------------------
Default model: SPECTRAL (resonant transfer function).
    Coupling exists. Strength measurable. DRESDYN anchor at f_res
    ~ 1/20000 yr. Predicts a paleomagnetic spectral peak in the
    precession band (19-23 kyr). FALSIFIABLE: paleomag record either
    shows the peak or it does not.
Documented null: FLAT (linear-alpha, low-pass only).
    Encodes the implicit assumption of conventional models: orbital
    forcing diffuses into broadband noise with no spectral signature.
    Available via method="flat" for reproducing the institutional
    baseline.
Anyone arguing against the spectral model must explain the absence
of a ~20 kyr peak in paleomagnetic spectra. If the peak exists, the
argument collapses before it starts.

DESIGN RULES
------------
1. Stateless functions; the cascade engine owns time series.
2. All knobs bounded; no hardcoded magic.
3. Spectral is default. Flat is selectable for null comparison.
4. M_dipole is NON-CONSTANT and exported on every call.

UNITS
-----
    time           : years
    angles/rates   : rad/s, rad/s^2
    M_dipole       : A.m^2     (Earth present ~ 8.0e22)
    B_surface      : Tesla
    frequency      : 1/year

DEPENDENCIES
------------
numpy required. scipy.signal optional for higher-order spectral methods.

CC0. JinnZ2 / earth-systems-physics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

try:
    from scipy.signal import welch as _scipy_welch
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


# ─────────────────────────────────────────────
# PHYSICAL CONSTANTS
# ─────────────────────────────────────────────

M_DIPOLE_PRESENT     = 8.0e22         # A.m^2  present geomagnetic dipole
B_SURFACE_EQUATOR    = 3.05e-5        # T      mean equatorial field
MU_0                 = 1.25663706e-6  # T.m/A
R_EARTH              = 6.371e6        # m
OMEGA_EARTH          = 7.2921159e-5   # rad/s
YEAR_S               = 3.155693e7     # s


# ─────────────────────────────────────────────
# DYNAMO RESPONSE CONFIG
# ─────────────────────────────────────────────

@dataclass
class DynamoResponseConfig:
    """
    Tunable parameters for the L5(Delta omega) -> L0(dM/dt) transfer.

    Frequency-domain transfer function:
                       alpha_0                  Q * (f / f_res)
        H(f) = -------------------------- * --------------------------------
               1 + (2 pi f tau_dyn)^2       1 + Q^2 (f/f_res - f_res/f)^2

    For method="flat", the resonant factor is replaced by 1.0,
    leaving only the low-pass.
    """
    # DC coupling gain (rotation rate to dipole drift)
    alpha_0: float = 1.0e22
    alpha_0_bounds: Tuple[float, float] = (1.0e21, 1.0e23)

    # Diffusive cutoff timescale (low-pass corner)
    tau_dynamo_yr: float = 1500.0
    tau_dynamo_bounds: Tuple[float, float] = (100.0, 10000.0)

    # Resonance frequency (DRESDYN anchor)
    f_res_per_yr: float = 1.0 / 20000.0
    f_res_bounds: Tuple[float, float] = (1.0 / 30000.0, 1.0 / 15000.0)

    # Resonance sharpness (Q factor). The discriminator.
    Q_factor: float = 5.0
    Q_bounds: Tuple[float, float] = (1.0, 20.0)

    method: str = "spectral"   # "spectral" | "flat"

    def validate(self) -> None:
        for name, val, bounds in [
            ("alpha_0",     self.alpha_0,        self.alpha_0_bounds),
            ("tau_dynamo",  self.tau_dynamo_yr,  self.tau_dynamo_bounds),
            ("f_res",       self.f_res_per_yr,   self.f_res_bounds),
            ("Q_factor",    self.Q_factor,       self.Q_bounds),
        ]:
            lo, hi = bounds
            if not (lo <= val <= hi):
                raise ValueError(
                    f"{name}={val} outside documented bounds [{lo}, {hi}]"
                )
        if self.method not in ("spectral", "flat"):
            raise ValueError(
                f"method={self.method!r} must be 'spectral' or 'flat'"
            )


# ─────────────────────────────────────────────
# TRANSFER FUNCTION H(f)
# ─────────────────────────────────────────────

def transfer_function(f_per_yr: np.ndarray,
                      cfg: DynamoResponseConfig) -> np.ndarray:
    """
    Complex frequency-domain transfer H(f).
    Units: A.m^2 per (rad/s).
    """
    cfg.validate()
    f = np.asarray(f_per_yr, dtype=float)
    safe_f = np.where(f == 0.0, 1e-30, f)

    # Low-pass: 1 / (1 + (2 pi f tau)^2). f in 1/yr, tau in yr.
    lp_denom = 1.0 + (2.0 * math.pi * f * cfg.tau_dynamo_yr) ** 2
    low_pass = cfg.alpha_0 / lp_denom

    if cfg.method == "flat":
        return low_pass + 0.0j

    f_ratio   = safe_f / cfg.f_res_per_yr
    detuning  = f_ratio - 1.0 / f_ratio
    res_denom = 1.0 + (cfg.Q_factor * detuning) ** 2
    res_gain  = cfg.Q_factor * f_ratio / res_denom

    lp_phase  = -np.arctan(2.0 * math.pi * f * cfg.tau_dynamo_yr)
    res_phase = -np.arctan(cfg.Q_factor * detuning)

    magnitude = low_pass * (1.0 + res_gain)
    phase     = lp_phase + res_phase

    return magnitude * np.exp(1j * phase)


# ─────────────────────────────────────────────
# CORE TRANSFER: Delta omega(t) -> dM/dt
# ─────────────────────────────────────────────

def dipole_drift_from_rotation(
    delta_omega_history_rads: np.ndarray,
    t_years: np.ndarray,
    cfg: Optional[DynamoResponseConfig] = None,
) -> np.ndarray:
    """
    L5(Delta omega) -> L0(dM/dt) transfer.
    delta_omega_history_rads : Delta omega time series, units rad/s.
                                Should be the SUM of L5 internal Delta
                                omega plus L-1 orbital Delta omega.
    t_years                  : matching time array, units yr.
    cfg                      : DynamoResponseConfig (default if None).
    Returns dM/dt array, units A.m^2 per year.
    """
    if cfg is None:
        cfg = DynamoResponseConfig()
    cfg.validate()

    x = np.asarray(delta_omega_history_rads, dtype=float)
    t = np.asarray(t_years, dtype=float)
    if x.shape != t.shape:
        raise ValueError("delta_omega and t_years must have same shape")
    if x.size < 4:
        raise ValueError("need at least 4 samples for spectral transfer")

    dt = np.diff(t)
    if not np.allclose(dt, dt[0], rtol=1e-6):
        raise ValueError("t_years must be uniformly spaced for FFT method")
    dt_yr = float(dt[0])
    N = x.size

    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(N, d=dt_yr)
    H = transfer_function(f, cfg)
    Y = X * H

    return np.fft.irfft(Y, n=N)


def dipole_moment_history(
    delta_omega_history_rads: np.ndarray,
    t_years: np.ndarray,
    cfg: Optional[DynamoResponseConfig] = None,
    M0: float = M_DIPOLE_PRESENT,
) -> np.ndarray:
    """Integrate dM/dt forward to get M_dipole(t)."""
    dM_dt = dipole_drift_from_rotation(delta_omega_history_rads, t_years, cfg)
    t = np.asarray(t_years, dtype=float)
    dt_yr = float(np.diff(t).mean())

    M = M0 + np.cumsum(dM_dt) * dt_yr

    if t.min() <= 0.0 <= t.max():
        idx0 = int(np.argmin(np.abs(t)))
        M = M - M[idx0] + M0
    return M


# ─────────────────────────────────────────────
# SURFACE FIELD FROM DIPOLE
# ─────────────────────────────────────────────

def b_surface_from_dipole(M_dipole: np.ndarray,
                          latitude_rad: float = 0.0) -> np.ndarray:
    """
    Surface field magnitude (Tesla) from dipole moment, at latitude.
        B(lat) = (mu_0 / 4 pi) * M / r^3 * sqrt(1 + 3 sin^2 lat)
    """
    M = np.asarray(M_dipole, dtype=float)
    geom = math.sqrt(1.0 + 3.0 * math.sin(latitude_rad) ** 2)
    return (MU_0 / (4.0 * math.pi)) * M / (R_EARTH ** 3) * geom


# ─────────────────────────────────────────────
# DIAGNOSTIC: SPECTRAL POWER
# ─────────────────────────────────────────────

def spectral_power(
    series: np.ndarray,
    t_years: np.ndarray,
    nperseg: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Power spectral density. Uses scipy.signal.welch if available, else
    a numpy periodogram.
    Returns (frequencies_per_yr, psd).
    """
    x = np.asarray(series, dtype=float)
    t = np.asarray(t_years, dtype=float)
    dt_yr = float(np.diff(t).mean())
    fs = 1.0 / dt_yr

    if _HAS_SCIPY:
        if nperseg is None:
            nperseg = min(256, x.size)
        f, psd = _scipy_welch(x, fs=fs, nperseg=nperseg, detrend="linear")
        return f, psd

    x_dt = x - x.mean()
    X = np.fft.rfft(x_dt)
    f = np.fft.rfftfreq(x.size, d=dt_yr)
    psd = (np.abs(X) ** 2) / (fs * x.size)
    return f, psd


# ─────────────────────────────────────────────
# TOP-LEVEL EXPORT FOR (FUTURE) CASCADE WIRING
# ─────────────────────────────────────────────

@dataclass
class L0Output:
    """Bundle of L0 outputs over a cascade window."""
    t_years: np.ndarray
    M_dipole: np.ndarray             # A.m^2
    dM_dt: np.ndarray                # A.m^2/yr
    B_surface_equator: np.ndarray    # T
    method_used: str                 # "spectral" | "flat"


def compute_l0_response(
    delta_omega_total_rads: np.ndarray,
    t_years: np.ndarray,
    cfg: Optional[DynamoResponseConfig] = None,
    M0: float = M_DIPOLE_PRESENT,
) -> L0Output:
    """
    Top-level entry point. Consumes Delta omega_total(t) — the SUM of
    L5 internal and L-1 orbital — and produces dipole and surface
    field histories.

    NOTE: not yet wired into cascade_engine.run_all_layers — that
    refactor (per-instant -> time-series cascade) is a separate piece
    of work. This module is callable directly today for offline
    spectral-response analysis.
    """
    if cfg is None:
        cfg = DynamoResponseConfig()
    cfg.validate()

    dM_dt = dipole_drift_from_rotation(delta_omega_total_rads, t_years, cfg)
    M     = dipole_moment_history(delta_omega_total_rads, t_years, cfg, M0=M0)
    B_eq  = b_surface_from_dipole(M, latitude_rad=0.0)

    return L0Output(
        t_years=np.asarray(t_years, dtype=float),
        M_dipole=M,
        dM_dt=dM_dt,
        B_surface_equator=B_eq,
        method_used=cfg.method,
    )


# ─────────────────────────────────────────────
# SELF-CHECK
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 64)
    print("Layer 0 EM dynamo response (alternate API) — self-check")
    print("=" * 64)

    N = 2001
    t = np.linspace(-100_000.0, 100_000.0, N)
    dt = t[1] - t[0]

    omega_signal = (
          1.0e-12 * np.cos(2 * np.pi * t /  23_000.0) +
          0.6e-12 * np.cos(2 * np.pi * t /  41_000.0) +
          0.3e-12 * np.cos(2 * np.pi * t / 100_000.0)
    )
    rng = np.random.default_rng(42)
    omega_signal = omega_signal + 0.2e-12 * rng.standard_normal(N)

    cfg_spec = DynamoResponseConfig(method="spectral", Q_factor=5.0)
    out_spec = compute_l0_response(omega_signal, t, cfg_spec)

    cfg_flat = DynamoResponseConfig(method="flat")
    out_flat = compute_l0_response(omega_signal, t, cfg_flat)

    print(f"\n  Sample forcing: 3-tone Milankovitch + noise, N={N}, dt={dt} yr")
    print(f"  Forcing RMS:    {np.sqrt(np.mean(omega_signal**2)):.3e} rad/s")

    print(f"\n  SPECTRAL method (Q={cfg_spec.Q_factor}, "
          f"f_res=1/{1/cfg_spec.f_res_per_yr:.0f} yr):")
    print(f"    M_dipole range  : {out_spec.M_dipole.min():.4e} .. "
          f"{out_spec.M_dipole.max():.4e} A.m^2")
    print(f"    dM/dt RMS       : "
          f"{np.sqrt(np.mean(out_spec.dM_dt**2)):.3e} A.m^2/yr")
    print(f"    B_eq range      : "
          f"{out_spec.B_surface_equator.min()*1e6:.3f} .. "
          f"{out_spec.B_surface_equator.max()*1e6:.3f} uT")

    print(f"\n  FLAT method (null):")
    print(f"    M_dipole range  : {out_flat.M_dipole.min():.4e} .. "
          f"{out_flat.M_dipole.max():.4e} A.m^2")
    print(f"    dM/dt RMS       : "
          f"{np.sqrt(np.mean(out_flat.dM_dt**2)):.3e} A.m^2/yr")
    print(f"    B_eq range      : "
          f"{out_flat.B_surface_equator.min()*1e6:.3f} .. "
          f"{out_flat.B_surface_equator.max()*1e6:.3f} uT")

    def manual_psd(x, dt_yr):
        x_dt = x - x.mean()
        X = np.fft.rfft(x_dt)
        f = np.fft.rfftfreq(x.size, d=dt_yr)
        psd = (np.abs(X) ** 2) / (x.size / dt_yr)
        return f, psd

    print("\n  PSD of dM/dt (peak frequency identifies dominant period):")
    f_s, psd_s = manual_psd(out_spec.dM_dt, dt)
    f_f, psd_f = manual_psd(out_flat.dM_dt, dt)
    pk_s = f_s[1:][np.argmax(psd_s[1:])]
    pk_f = f_f[1:][np.argmax(psd_f[1:])]
    print(f"    spectral peak period : {1.0/pk_s:.0f} yr  "
          f"(expected near 20-23 kyr — DRESDYN/precession band)")
    print(f"    flat peak period     : {1.0/pk_f:.0f} yr  "
          f"(expected at lowest input tone, no resonant selection)")

    def band_power(f, psd, period_lo_yr, period_hi_yr):
        m = (f >= 1.0 / period_hi_yr) & (f <= 1.0 / period_lo_yr)
        return float(psd[m].sum()) if m.any() else 0.0

    bands = [
        ("precession (18-25 kyr)",   18000.0,  25000.0),
        ("obliquity  (35-45 kyr)",   35000.0,  45000.0),
        ("eccentr.   (90-110 kyr)",  90000.0, 110000.0),
    ]
    print("\n  Band power ratio (spectral / flat):")
    for label, lo, hi in bands:
        ps = band_power(f_s, psd_s, lo, hi)
        pf = band_power(f_f, psd_f, lo, hi)
        ratio = ps / max(pf, 1e-30)
        print(f"    {label:24s} : {ratio:6.2f}x")
    print("\n  -> spectral amplifies the precession band relative to others.")
    print("  -> falsifiable prediction: paleomag PSD should show same pattern.")
    print("  -> if it does, spectral model fits. if not, falsified.\n")

    print("OK.")
