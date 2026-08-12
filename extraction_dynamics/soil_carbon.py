# soil_carbon.py
# earth-systems-physics / extraction_dynamics
# CC0 — No Rights Reserved
#
# Soil organic carbon as a consumer-resource problem, with a
# texture-normalised capacity instead of a fixed percentage floor.
#
#   SOC_max = f(clay + fine silt)      saturation capacity (Hassink 1997)
#   deficit = 1 - SOC / SOC_max        dimensionless, cross-site comparable
#   dSOC/dt = h*C_input - k*SOC        humification in, decay out
#
#   extraction  <=>  C_removed > h*C_input   (dSOC/dt < 0)
#
# WHY NOT A FIXED FLOOR
# ---------------------
# "Soil is degraded below 2.0% SOC" is not a physical statement. A sandy
# soil physically cannot hold 2%; a heavy clay at 2% is severely
# depleted. The mineral surface area available to stabilise organic
# carbon is set by the fine fraction, so capacity is a property of the
# soil and the deficit against that capacity is the comparable quantity.
# Hassink (1997) measured the relation directly:
#
#   C_sat (g C/kg soil) = 4.09 + 0.37 * (% particles < 20 um)
#
# The coefficients are exposed as arguments because other regressions
# exist for other regions and depths. Substitute yours; do not inherit
# these as universal constants.
#
# WHY THIS BELONGS IN AN EXTRACTION MODULE
# ----------------------------------------
# Tillage agriculture with fertiliser substitution is the terrestrial
# instance of the same structure as a subsidised fishery: the consumer
# (yield) is maintained by an exogenous input (industrial N, P, fuel)
# while the resource (soil carbon and its associated structure, water
# holding, biology) declines. Yield stays flat while the stock is spent.
# The flat yield is the subsidy talking, not the soil.
#
# Standard library only.

import math
from typing import Dict, Optional

# ─────────────────────────────────────────────
# SATURATION CAPACITY
# ─────────────────────────────────────────────

# Hassink (1997) Plant and Soil 191:77-87, temperate soils, <20 um
# fraction, topsoil. Intercept g C/kg, slope g C/kg per % fine fraction.
HASSINK_INTERCEPT_gC_kg = 4.09
HASSINK_SLOPE_gC_kg_per_pct = 0.37


def saturation_capacity_gC_kg(fine_fraction_pct: float,
                              intercept: float = HASSINK_INTERCEPT_gC_kg,
                              slope: float = HASSINK_SLOPE_gC_kg_per_pct
                              ) -> float:
    """
    Physically protected SOC capacity from texture.

    fine_fraction_pct : mass % of particles < 20 um (clay + fine silt)
    intercept, slope  : regression coefficients — substitute a local
                        calibration rather than treating Hassink's
                        temperate topsoil fit as universal
    returns: saturation capacity (g C / kg soil)
    """
    if fine_fraction_pct < 0:
        raise ValueError("fine fraction cannot be negative")
    return intercept + slope * fine_fraction_pct


def saturation_capacity_pct(fine_fraction_pct: float, **kwargs) -> float:
    """Saturation capacity expressed as % SOC (g C per 100 g soil)."""
    return saturation_capacity_gC_kg(fine_fraction_pct, **kwargs) / 10.0


def saturation_deficit(SOC_pct: float, fine_fraction_pct: float,
                       **kwargs) -> Dict[str, float]:
    """
    Saturation deficit: 1 - SOC/SOC_max.

    Dimensionless and comparable across soils, which a raw percentage is
    not. A deficit near 0 means the soil is holding what its mineralogy
    can protect; near 1 means the protective capacity is empty and the
    gap is the sequestration headroom.

    SOC_pct           : measured soil organic carbon (%)
    fine_fraction_pct : mass % of particles < 20 um
    """
    cap = saturation_capacity_pct(fine_fraction_pct, **kwargs)
    if cap <= 0:
        raise ValueError("saturation capacity must be positive")
    ratio = SOC_pct / cap
    return {
        "SOC_pct":            SOC_pct,
        "SOC_max_pct":        cap,
        "saturation_ratio":   ratio,
        "saturation_deficit": 1.0 - ratio,
        "headroom_pct_SOC":   max(0.0, cap - SOC_pct),
        "supersaturated":     ratio > 1.0,
        "note": ("SOC exceeds the mineral-protected capacity — the excess "
                 "is particulate/unprotected carbon and is not stable"
                 if ratio > 1.0 else
                 "deficit is the physically protectable headroom"),
    }


def soc_stock_t_ha(SOC_pct: float, bulk_density_g_cm3: float = 1.3,
                   depth_cm: float = 30.0) -> float:
    """
    Areal SOC stock.

        t C/ha = SOC(%) * bulk density (g/cm3) * depth (cm)

    Percentages cannot be compared across soils of different bulk
    density or sampling depth; stocks can.
    """
    return SOC_pct * bulk_density_g_cm3 * depth_cm


# ─────────────────────────────────────────────
# DYNAMICS
# ─────────────────────────────────────────────


def dSOC_dt(SOC_pct: float, C_input_t_ha_yr: float,
            humification: float = 0.20, k_decay_yr: float = 0.02,
            bulk_density_g_cm3: float = 1.3, depth_cm: float = 30.0
            ) -> Dict[str, float]:
    """
    One-pool SOC balance.

        dSOC/dt = h*C_input - k*SOC

    h : humification coefficient — fraction of carbon input that becomes
        stabilised SOC rather than being respired within the year
        (0.10-0.30 typical; root carbon stabilises severalfold better
        than surface residue, so h depends on WHERE the carbon enters)
    k : first-order decay constant of the stabilised pool (1/yr).
        0.01-0.03 for temperate arable topsoil; rises with tillage,
        temperature, and aeration. The defaults here (h=0.20, k=0.02)
        reproduce roughly 1.3% steady-state SOC at 5 t C/ha/yr input,
        which is the right order for temperate arable. Calibrate them
        against a local time series before trusting a projection.

    Returns rates in both t C/ha/yr and %SOC/yr so the balance can be
    checked against field measurements in either unit.
    """
    stock = soc_stock_t_ha(SOC_pct, bulk_density_g_cm3, depth_cm)
    gain = humification * C_input_t_ha_yr
    loss = k_decay_yr * stock
    net = gain - loss
    per_pct = bulk_density_g_cm3 * depth_cm      # t/ha per 1% SOC
    return {
        "SOC_stock_t_ha":     stock,
        "gain_t_ha_yr":       gain,
        "loss_t_ha_yr":       loss,
        "dSOC_t_ha_yr":       net,
        "dSOC_pct_yr":        net / per_pct if per_pct > 0 else 0.0,
        "losing_carbon":      net < 0,
        "steady_state_pct":   (humification * C_input_t_ha_yr
                               / (k_decay_yr * per_pct)
                               if k_decay_yr > 0 and per_pct > 0 else 0.0),
    }


def steady_state_SOC_pct(C_input_t_ha_yr: float, humification: float = 0.20,
                         k_decay_yr: float = 0.02,
                         bulk_density_g_cm3: float = 1.3,
                         depth_cm: float = 30.0) -> float:
    """
    SOC the system converges to under a constant input regime:

        SOC* = h * C_input / (k * BD * depth)

    This is the number a management system is actually choosing when it
    sets a residue-return policy. It is a property of the inputs, not an
    aspiration.
    """
    per_pct = bulk_density_g_cm3 * depth_cm
    if k_decay_yr <= 0 or per_pct <= 0:
        return float("inf")
    return humification * C_input_t_ha_yr / (k_decay_yr * per_pct)


def C_input_required(target_SOC_pct: float, humification: float = 0.20,
                     k_decay_yr: float = 0.02,
                     bulk_density_g_cm3: float = 1.3,
                     depth_cm: float = 30.0) -> float:
    """Carbon input (t C/ha/yr) whose steady state is target_SOC_pct."""
    if humification <= 0:
        return float("inf")
    return (target_SOC_pct * k_decay_yr * bulk_density_g_cm3 * depth_cm
            / humification)


def time_to_target(SOC0_pct: float, target_SOC_pct: float,
                   C_input_t_ha_yr: float, humification: float = 0.20,
                   k_decay_yr: float = 0.02,
                   bulk_density_g_cm3: float = 1.3,
                   depth_cm: float = 30.0) -> Dict[str, object]:
    """
    Years to reach a target SOC under a constant input, from the
    analytic solution of the one-pool model:

        SOC(t) = SOC* + (SOC0 - SOC*) * exp(-k t)

    Returns reachable=False when the target lies beyond the steady state
    the inputs can support — the common case, and the one where a
    timeline gets promised that no amount of patience delivers.
    """
    SOC_star = steady_state_SOC_pct(C_input_t_ha_yr, humification,
                                    k_decay_yr, bulk_density_g_cm3, depth_cm)
    building = target_SOC_pct > SOC0_pct
    reachable = (target_SOC_pct < SOC_star if building
                 else target_SOC_pct > SOC_star)
    if not reachable or k_decay_yr <= 0:
        return {
            "reachable":    False,
            "steady_state_pct": SOC_star,
            "years":        None,
            "note": (f"target {target_SOC_pct:.2f}% is beyond the steady "
                     f"state {SOC_star:.2f}% supported by this carbon "
                     f"input; no timeline reaches it — the input has to "
                     f"change"),
        }
    ratio = (target_SOC_pct - SOC_star) / (SOC0_pct - SOC_star)
    years = -math.log(ratio) / k_decay_yr
    return {
        "reachable":        True,
        "steady_state_pct": SOC_star,
        "years":            years,
        "note": "asymptotic approach — the last increments take longest",
    }


def extraction_check(C_removed_t_ha_yr: float, C_input_t_ha_yr: float,
                     humification: float = 0.20) -> Dict[str, object]:
    """
    Is this system mining its soil carbon?

    The test is not yield, profit, or intent:

        extraction  <=>  C_removed > h * C_input

    Carbon leaving as harvest and erosion, against carbon entering the
    stabilised pool. When removal exceeds humified input, the stock
    funds the difference — and yield can stay flat throughout, because
    fertiliser substitutes for the nutrient functions of the carbon
    while it lasts.
    """
    stabilised_input = humification * C_input_t_ha_yr
    net = stabilised_input - C_removed_t_ha_yr
    return {
        "C_removed_t_ha_yr":     C_removed_t_ha_yr,
        "C_input_t_ha_yr":       C_input_t_ha_yr,
        "stabilised_input_t_ha_yr": stabilised_input,
        "net_t_ha_yr":           net,
        "extracting":            net < 0,
        "deficit_t_ha_yr":       max(0.0, -net),
        "interaction":           "mining" if net < 0 else "coupled",
        "note": ("removal exceeds stabilised input: the stock is paying "
                 "the difference, and yield will not show it while "
                 "fertiliser substitutes"
                 if net < 0 else
                 "inputs cover removal — the stock is not funding the yield"),
    }


if __name__ == "__main__":
    print("TEXTURE SETS CAPACITY — WHY A FIXED FLOOR IS NOT PHYSICS")
    print("=" * 70)
    print(f"  {'fine fraction <20um':>21} {'SOC_max %':>10} "
          f"{'SOC 1.5% deficit':>18} {'SOC 2.5% deficit':>18}")
    for ff in (5.0, 15.0, 30.0, 50.0, 70.0):
        cap = saturation_capacity_pct(ff)
        d15 = saturation_deficit(1.5, ff)["saturation_deficit"]
        d25 = saturation_deficit(2.5, ff)["saturation_deficit"]
        print(f"  {ff:21.0f} {cap:10.2f} {d15:18.3f} {d25:18.3f}")
    print("\n  A soil at 2.5% SOC is FAR ABOVE what 5% fine fraction can")
    print("  protect (deficit negative — the excess is unprotected") 
    print("  particulate carbon), and still has headroom at 70%. One")
    print("  threshold cannot describe both soils; the deficit can.")

    print("\n\nWHAT THE INPUTS ACTUALLY CHOOSE")
    print("=" * 70)
    for C_in in (2.0, 5.0, 8.0, 12.0):
        print(f"  C input {C_in:4.1f} t C/ha/yr -> steady state "
              f"{steady_state_SOC_pct(C_in):5.2f}% SOC   "
              f"(stock {soc_stock_t_ha(steady_state_SOC_pct(C_in)):6.1f} t/ha)")

    print("\n\nIS THIS SYSTEM MINING?")
    print("=" * 70)
    for label, removed, added in (("residue returned",       0.2, 4.0),
                                  ("residue baled",          0.9, 1.2),
                                  ("residue baled + erosion", 1.4, 1.2)):
        r = extraction_check(removed, added)
        print(f"  {label:24s} net={r['net_t_ha_yr']:+6.3f} t C/ha/yr  "
              f"-> {r['interaction']}")

    print("\n\nCAN THE TARGET BE REACHED?")
    print("=" * 70)
    for C_in, target in ((4.0, 2.0), (8.0, 2.0), (12.0, 2.0)):
        t = time_to_target(1.2, target, C_in)
        got = (f"{t['years']:.0f} yr" if t["reachable"] else "never")
        print(f"  from 1.2% to {target}% at {C_in:.0f} t C/ha/yr input: "
              f"{got:>8}   (steady state {t['steady_state_pct']:.2f}%)")
