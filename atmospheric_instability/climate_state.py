"""
climate_state.py  --  CC0

Parameterizes the background atmospheric state and how a warming_index deforms
it. This is the knob that moves the whole stability manifold: same physics,
shifted background, different dominant modes.

warming_index w in [0,1]:
  w=0  late-20th-century baseline
  w=1  strong-forcing state (Arctic amplification + tropical upper warming)

Mechanisms encoded (all observed / physically argued, flagged where contested):
  - lower-tropospheric meridional gradient WEAKENS (Arctic amplification)   [robust]
  - upper-tropospheric tropical warming STRENGTHENS upper gradient          [robust]
  - stratification N increases slightly aloft                               [moderate]
  - jet becomes wavier / sharper curvature (d2U/dy2 up)                      [contested]
"""

from dataclasses import dataclass
from thermo import coriolis, brunt_vaisala, thermal_wind_shear


@dataclass
class AtmoState:
    lat_deg: float
    T: float                 # K, layer temperature
    dTdy_lower: float        # K/m, lower-trop meridional gradient (negative NH)
    dTdy_upper: float        # K/m, upper-trop meridional gradient
    env_lapse: float         # K/m, environmental lapse rate (=-dT/dz)
    U: float                 # m/s, mean zonal wind
    dUdy: float              # 1/s, meridional shear of U
    d2Udy2: float            # 1/(m s), jet curvature
    gw_amplitude: float      # m/s, gravity-wave amplitude
    gw_wavelength_km: float
    source: str = "EST_baseline"


def baseline_state(lat_deg=45.0):
    """A representative mid-latitude winter-ish baseline (w=0)."""
    return AtmoState(
        lat_deg=lat_deg,
        T=255.0,
        dTdy_lower=-8.0e-6,     # ~ -8 K per 1000 km
        dTdy_upper=-5.0e-6,
        env_lapse=6.5e-3,       # 6.5 K/km (standard troposphere)
        U=30.0,
        dUdy=1.0e-5,
        d2Udy2=1.0e-11,
        gw_amplitude=8.0,
        gw_wavelength_km=200.0,
    )


def apply_warming(state: AtmoState, w: float) -> AtmoState:
    """
    Deform the baseline by warming index w in [0,1]. Returns a new state.
    """
    w = max(0.0, min(1.0, w))
    return AtmoState(
        lat_deg=state.lat_deg,
        T=state.T + 4.0 * w,                                  # bulk warming
        # Arctic amplification: lower gradient weakens (toward zero)
        dTdy_lower=state.dTdy_lower * (1.0 - 0.45 * w),
        # tropical upper warming: upper gradient strengthens (more negative)
        dTdy_upper=state.dTdy_upper * (1.0 + 0.35 * w),
        # slightly more stable lapse aloft
        env_lapse=state.env_lapse * (1.0 - 0.10 * w),
        U=state.U * (1.0 + 0.05 * w),
        dUdy=state.dUdy,
        # wavier/sharper jet (contested) -- curvature up
        d2Udy2=state.d2Udy2 * (1.0 + 0.6 * w),
        # GW forcing from convection rises with warming
        gw_amplitude=state.gw_amplitude * (1.0 + 0.25 * w),
        gw_wavelength_km=state.gw_wavelength_km,
        source=f"warming_w={w:.2f}",
    )


def derived(state: AtmoState, level="lower"):
    """
    Compute the derived dynamical quantities a kernel needs from a state.
    level selects which meridional gradient to use for thermal-wind shear.
    Returns dict: f, N, N2, shear, dUdy, d2Udy2, U, lat.
    """
    f = coriolis(state.lat_deg)
    N = brunt_vaisala(state.T, state.env_lapse)
    N2 = N * abs(N)                      # signed N^2
    dTdy = state.dTdy_lower if level == "lower" else state.dTdy_upper
    shear = thermal_wind_shear(dTdy, f, state.T)
    return {
        "f": f, "N": N, "N2": N2, "shear": shear,
        "dUdy": state.dUdy, "d2Udy2": state.d2Udy2,
        "U": state.U, "lat": state.lat_deg, "T": state.T,
        "gw_amp": state.gw_amplitude, "gw_wl": state.gw_wavelength_km,
    }
