"""
instabilities.py  --  CC0

The instability kernels. Each returns a growth rate (1/s) or a dimensionless
proximity-to-threshold. Positive growth rate => mode is unstable and amplifying.
All grounded in standard dynamical meteorology. stdlib only.

A mode is "active" when growth_rate > 0 (or threshold crossed). The explorer
walks parameter space looking for where each crosses zero.
"""

import math
from thermo import (
    G, brunt_vaisala_sq, richardson, thermal_wind_shear, coriolis, beta,
)


# ---------------------------------------------------------------------------
# 1. KELVIN-HELMHOLTZ  (shear instability at a density interface)
# ---------------------------------------------------------------------------
def kelvin_helmholtz(N2, shear):
    """
    KH unstable when Ri = N2/S^2 < 0.25.
    Return growth_proxy = (0.25 - Ri)  scaled; >0 means unstable.
    Also return an approximate growth rate ~ S/2 * sqrt(1 - 4*Ri) when unstable.
    """
    Ri = richardson(N2, shear)
    proxy = 0.25 - Ri
    if Ri < 0.25 and shear != 0:
        gr = 0.5 * abs(shear) * math.sqrt(max(0.0, 1.0 - 4.0 * Ri))
    else:
        gr = 0.0
    return {"mode": "kelvin_helmholtz", "Ri": Ri, "proxy": proxy, "growth": gr,
            "active": Ri < 0.25}


# ---------------------------------------------------------------------------
# 2. BAROCLINIC  (Eady model -- mid-latitude cyclogenesis)
# ---------------------------------------------------------------------------
def baroclinic_eady(f, N, shear):
    """
    Eady maximum growth rate:  sigma = 0.31 * f * |dU/dz| / N    [1/s]
    Requires N>0 (stable stratification) and nonzero shear.
    This is THE engine of mid-latitude weather. Climate change moves f (no),
    N (yes, slightly), and shear (yes, strongly via thermal wind).
    """
    if N <= 0:
        # no baroclinic mode in convectively unstable layer; convection dominates
        return {"mode": "baroclinic_eady", "growth": 0.0, "active": False,
                "note": "N<=0, convective regime"}
    sigma = 0.31 * abs(f) * abs(shear) / N
    return {"mode": "baroclinic_eady", "growth": sigma, "active": sigma > 0,
            "timescale_hr": (1.0 / sigma) / 3600.0 if sigma > 0 else float("inf")}


# ---------------------------------------------------------------------------
# 3. INERTIAL  (absolute vorticity sign change)
# ---------------------------------------------------------------------------
def inertial(f, dUdy):
    """
    Inertial instability when absolute vorticity (f - dU/dy in NH for zonal
    flow) times f < 0, i.e. f*(f - dU/dy) < 0.
    dUdy = meridional shear of zonal wind, 1/s.
    """
    abs_vort = f - dUdy
    product = f * abs_vort
    active = product < 0
    gr = math.sqrt(abs(product)) if active else 0.0
    return {"mode": "inertial", "abs_vort": abs_vort, "product": product,
            "growth": gr, "active": active}


# ---------------------------------------------------------------------------
# 4. SYMMETRIC / SLANTWISE  (negative potential vorticity)
# ---------------------------------------------------------------------------
def symmetric(f, N2, shear, q_pv=None):
    """
    Symmetric (slantwise convective) instability when moist PV * f < 0.
    Simplified Bennetts-Hoskins proxy: instability favored when the
    Richardson number is low AND stratification weak. We use:
        PV_proxy = f * N2 - shear^2 * f   (sign indicates)
    active when PV_proxy < 0 (NH, f>0).
    """
    if q_pv is None:
        q_pv = f * N2 - (shear * shear) * f
    active = (q_pv * f) < 0
    gr = abs(shear) * 0.5 if active else 0.0
    return {"mode": "symmetric", "pv_proxy": q_pv, "growth": gr, "active": active}


# ---------------------------------------------------------------------------
# 5. GRAVITY-WAVE BREAKING  (saturation / overturning)
# ---------------------------------------------------------------------------
def gravity_wave(N, U_bg, wavelength_km, amplitude_ms):
    """
    Internal gravity wave breaks (overturns) when its amplitude reaches the
    saturation limit u_sat ~ |c - U| (wave-induced velocity exceeds intrinsic
    phase speed -> convective overturning).
    intrinsic phase speed c_i = N / k (hydrostatic, vertical propagation).
    Here k_h horizontal wavenumber. Return breaking margin.
    """
    if N <= 0:
        return {"mode": "gravity_wave", "growth": 0.0, "active": False,
                "note": "N<=0 no GW"}
    k = 2.0 * math.pi / (wavelength_km * 1000.0)
    c_i = N / k                       # intrinsic phase speed scale, m/s
    u_sat = abs(c_i)                  # saturation velocity amplitude
    margin = amplitude_ms - u_sat     # >0 => breaking
    gr = N * (margin / u_sat) if (u_sat > 0 and margin > 0) else 0.0
    return {"mode": "gravity_wave", "c_intrinsic": c_i, "u_sat": u_sat,
            "margin": margin, "growth": max(0.0, gr), "active": margin > 0}


# ---------------------------------------------------------------------------
# 6. CONVECTIVE  (static instability)
# ---------------------------------------------------------------------------
def convective(N2):
    """
    Direct static instability: N2 < 0. Growth rate = sqrt(-N2) (parcel
    acceleration timescale). The fastest mode when it's active.
    """
    active = N2 < 0
    gr = math.sqrt(-N2) if active else 0.0
    return {"mode": "convective", "N2": N2, "growth": gr, "active": active}


# ---------------------------------------------------------------------------
# 7. ROSSBY-WAVE / BAROTROPIC  (meridional PV gradient & critical shear)
# ---------------------------------------------------------------------------
def rossby_barotropic(lat_deg, U, dUdy2):
    """
    Barotropic (Rayleigh-Kuo) instability requires the meridional gradient of
    absolute vorticity (beta - d2U/dy2) to change sign somewhere.
    dUdy2 = d^2U/dy^2 (curvature of jet), 1/(m s).
    Return how close beta - d2U/dy2 is to zero (sign change = necessary cond).
    """
    b = beta(lat_deg)
    pv_grad = b - dUdy2
    # necessary condition for instability: pv_grad changes sign -> proximity
    proxy = -pv_grad        # >0 when d2U/dy2 > beta (sharp jet) -> unstable-prone
    active = pv_grad < 0
    gr = abs(U) * 1e-6 if active else 0.0   # crude scaling
    return {"mode": "rossby_barotropic", "beta": b, "pv_grad": pv_grad,
            "proxy": proxy, "growth": gr, "active": active}


ALL_KERNELS = [
    "kelvin_helmholtz", "baroclinic_eady", "inertial",
    "symmetric", "gravity_wave", "convective", "rossby_barotropic",
]
