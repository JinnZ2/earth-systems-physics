# aquifer_pressure_head.py  -- CC0, stdlib-only
#
# Seismic emergence mechanism: water FROM the ground, not from the sky.
#
# Two-step physics:
#   1. Seismic energy density  e(M, r)     [Wang 2007]                AQ-02
#   2. Poroelastic pore-pressure change    dp = B * d_sigma  [Skempton] AQ-01
#   3. Classify response: NONE / WATER_LEVEL / SPRING / LIQUEFACTION_UPWELLING
#
# Key coupling (AQ-03): S_base from mantle_crust_coupling lowers response
# thresholds. A primed deep baseline makes the aquifer easier to trip.
# This is the SPECULATIVE coupling claim; AQ-01 and AQ-02 are MEASURED.
#
# References:
#   Wang (2007)     Hydrology of the Earth's interior — energy density thresholds
#   Skempton (1954) The pore-pressure coefficients A and B — Geotechnique
#   Manga et al. (2012) — review of seismo-hydrological responses

import math
from claim_ledger import Quantity, gate

# ── MEASURED CONSTANTS ────────────────────────────────────────────────────────

B_SKEMPTON = 0.7           # Skempton coefficient — saturated sediment [MEASURED 0.5..0.9]
K_UNDRAINED_PA = 2.5e9     # undrained bulk modulus — saturated sandstone [MEASURED]

# Wang (2007) global empirical response thresholds [J/m³]  [MEASURED]
THRESHOLD_WATER_LEVEL  = 1.0e-4   # minimum for well-level / water-table response
THRESHOLD_SPRING       = 1.0e-3   # minimum for spring / stream discharge increase
THRESHOLD_LIQUEFACTION = 1.0e-1   # minimum for liquefaction / upwelling

# Response classes ordered ascending by energy requirement
RESPONSE_CLASSES = (
    "NONE",
    "WATER_LEVEL",
    "SPRING",
    "LIQUEFACTION_UPWELLING",
)


# ── PHYSICS FUNCTIONS ─────────────────────────────────────────────────────────

def seismic_energy_density(magnitude: float, r_km: float) -> float:
    """
    Seismic energy density at distance r from an M earthquake. AQ-02.

    Wang (2007) Eq. 1 based on Gutenberg-Richter energy relation:
      E_s = 10^(1.5 M + 4.8)  J   (total radiated seismic energy)
      e   = E_s / (4 pi r^3)  J/m³

    magnitude : Richter / moment magnitude
    r_km      : epicentral distance (km)
    returns   : seismic energy density (J/m³)
    evidence  : MEASURED [Wang 2007 global compilation]
    """
    E_s = 10.0 ** (1.5 * magnitude + 4.8)   # J
    r_m = r_km * 1000.0
    e = E_s / (4.0 * math.pi * r_m ** 3)
    return gate(Quantity(e, "J_per_m3", 0.0, 1.0e7), "seismic_energy_density")


def poroelastic_pressure_pa(e: float,
                             K_pa: float = K_UNDRAINED_PA) -> float:
    """
    Skempton pore-pressure change from seismic loading. AQ-01.

      Δσ ≈ √(2 K e)  (seismic stress amplitude from energy density)
      Δp = B * Δσ

    e    : seismic energy density (J/m³)
    K_pa : undrained bulk modulus (Pa)
    returns: pore-pressure change (Pa)
    evidence: MEASURED [Skempton 1954; Manga 2012]
    """
    d_sigma = math.sqrt(2.0 * K_pa * e)
    dp = B_SKEMPTON * d_sigma
    return gate(Quantity(dp, "Pa", 0.0, 1.0e8), "poroelastic_dp")


def classify_response(e: float, s_base: float = 0.0) -> str:
    """
    Classify hydrological response type. AQ-03 coupling included.

    s_base (crustal sensitivity from mantle_crust_coupling) lowers thresholds:
      threshold_effective = threshold_base × max(0.2, 1 - 0.5 * s_base)
    At s_base=0 (dry baseline): standard Wang thresholds apply.
    At s_base=1 (fully primed): thresholds halved.

    returns: one of RESPONSE_CLASSES
    evidence: thresholds MEASURED [Wang 2007]; s_base coupling SPECULATIVE [AQ-03]
    """
    factor = max(0.2, 1.0 - 0.5 * s_base)
    if e >= THRESHOLD_LIQUEFACTION * factor:
        return "LIQUEFACTION_UPWELLING"
    elif e >= THRESHOLD_SPRING * factor:
        return "SPRING"
    elif e >= THRESHOLD_WATER_LEVEL * factor:
        return "WATER_LEVEL"
    return "NONE"


def water_head_change_m(magnitude: float, r_km: float,
                         s_base: float = 0.0,
                         K_pa: float = K_UNDRAINED_PA) -> dict:
    """
    Full emergence assessment for a seismic event.

    magnitude : earthquake magnitude
    r_km      : epicentral distance (km)
    s_base    : crustal sensitivity from mantle_crust_coupling [0,1]
    returns   : dict with energy density, pressure, head change, classification
    """
    e = seismic_energy_density(magnitude, r_km)
    dp = poroelastic_pressure_pa(e, K_pa)
    rho_w_g = 1000.0 * 9.81      # Pa/m
    dh = dp / rho_w_g             # m water head change
    classification = classify_response(e, s_base)
    return {
        "magnitude":       magnitude,
        "r_km":            r_km,
        "e_J_m3":          round(e, 6),
        "dp_Pa":           round(dp, 1),
        "dh_m":            round(dh, 3),
        "classification":  classification,
        "s_base":          s_base,
    }


if __name__ == "__main__":
    print("=== aquifer_pressure_head.py — seismic water emergence ===\n")
    print("Seismic energy density vs distance (M 6.5):")
    for r in (30, 60, 100, 200, 500):
        e = seismic_energy_density(6.5, r)
        cls = classify_response(e)
        print(f"  r={r:4d} km   e={e:.2e} J/m3   {cls}")

    print("\nResponse classification vs magnitude (r=100 km, s_base=0):")
    for M in (4.0, 5.0, 6.0, 6.5, 7.0, 7.5):
        res = water_head_change_m(M, 100.0)
        print(f"  M={M:.1f}   e={res['e_J_m3']:.2e}   dh={res['dh_m']:6.1f} m   "
              f"{res['classification']}")

    print("\nEffect of primed baseline (M 5.5, r=120 km):")
    for sb in (0.0, 0.3, 0.6, 1.0):
        res = water_head_change_m(5.5, 120.0, s_base=sb)
        print(f"  s_base={sb:.1f}   {res['classification']}  "
              f"(threshold factor {max(0.2, 1-0.5*sb):.2f}x)")
