# surplus_production.py
# earth-systems-physics / extraction_dynamics
# CC0 — No Rights Reserved
#
# Surplus production and the two standardised intensive ratios that
# stock assessment already uses. Every term is in tonnes or tonnes/yr;
# there is no dimension fault to reconcile and no new index to invent.
#
#   P_B   = r*B*(1 - B/K)          surplus production (Schaefer)
#   dB/dt = P_B - Y                biomass, Y = yield
#
#   F / F_MSY   > 1  overfishing is OCCURRING          (a RATE)
#   B / B_MSY   < 1  the stock is OVERFISHED           (a STATE)
#   B / B_0          depletion, comparable across stocks
#
# The rate/state distinction is the part homemade indices usually lose.
# A stock can be rebuilt (B/B_MSY > 1) while being fished too hard
# (F/F_MSY > 1), and vice versa. Collapsing them into one number throws
# away the sign of the derivative, which is the only part that tells you
# what happens next.
#
# Schaefer reference points fall straight out of the logistic:
#   B_MSY = K/2      F_MSY = r/2      MSY = r*K/4
#
# Pella-Tomlinson generalises the production curve with a shape
# parameter p, so B_MSY/K need not be 0.5. Use it when the stock's
# productivity peaks away from half of carrying capacity — which is most
# of them.
#
# Standard library only.

import math
from typing import Dict, List, Optional, Sequence

# ─────────────────────────────────────────────
# PRODUCTION CURVES
# ─────────────────────────────────────────────


def surplus_production(B: float, r: float, K: float) -> float:
    """
    Schaefer surplus production, tonnes/yr.

        P_B = r*B*(1 - B/K)

    B : current biomass (t)
    r : intrinsic rate of increase (1/yr)
    K : unfished biomass / carrying capacity (t)
    """
    if K <= 0:
        return 0.0
    return r * B * (1.0 - B / K)


def surplus_production_pella_tomlinson(B: float, r: float, K: float,
                                       p: float = 1.0) -> float:
    """
    Pella-Tomlinson surplus production.

        P_B = (r/p) * B * (1 - (B/K)^p)

    p = 1 recovers Schaefer (B_MSY = K/2). p < 1 shifts peak production
    to lower biomass; p > 1 shifts it higher. Fox model is the p -> 0
    limit.
    """
    if K <= 0 or p <= 0:
        return 0.0
    return (r / p) * B * (1.0 - (B / K) ** p)


def biomass_rate(B: float, r: float, K: float, Y: float,
                 p: Optional[float] = None) -> float:
    """dB/dt = P_B - Y. Yield Y in tonnes/yr, same units as production."""
    P_B = (surplus_production(B, r, K) if p is None
           else surplus_production_pella_tomlinson(B, r, K, p))
    return P_B - Y


# ─────────────────────────────────────────────
# REFERENCE POINTS
# ─────────────────────────────────────────────


def reference_points(r: float, K: float,
                     p: Optional[float] = None) -> Dict[str, float]:
    """
    MSY reference points.

    Schaefer:  B_MSY = K/2, F_MSY = r/2, MSY = r*K/4
    Pella-Tomlinson: B_MSY = K * (1/(1+p))^(1/p)
    """
    if p is None or abs(p - 1.0) < 1e-12:
        B_msy = K / 2.0
        F_msy = r / 2.0
        MSY = r * K / 4.0
    else:
        B_msy = K * (1.0 / (1.0 + p)) ** (1.0 / p)
        MSY = (r / p) * B_msy * (1.0 - (B_msy / K) ** p)
        F_msy = MSY / B_msy if B_msy > 0 else 0.0
    return {
        "B_MSY": B_msy,
        "F_MSY": F_msy,
        "MSY":   MSY,
        "B_0":   K,
        "B_MSY_over_B_0": B_msy / K if K > 0 else float("nan"),
        "shape_p": 1.0 if p is None else p,
    }


def fishing_mortality(Y: float, B: float) -> float:
    """
    F = Y / B — instantaneous fishing mortality approximated as the
    exploitation rate. A RATE, per year, not a state.
    """
    return Y / B if B > 0 else float("inf")


# ─────────────────────────────────────────────
# STOCK STATUS — RATE AND STATE, KEPT SEPARATE
# ─────────────────────────────────────────────


def stock_status(B: float, Y: float, r: float, K: float,
                 p: Optional[float] = None) -> Dict[str, object]:
    """
    Full status in the standard ratios, with the Kobe-plot quadrant.

    Returns both ratios and the quadrant, because the pair is the
    diagnosis: B/B_MSY says where the stock IS, F/F_MSY says where it is
    GOING. Reporting one without the other is how a rebuilding stock and
    a collapsing stock end up with the same score.
    """
    rp = reference_points(r, K, p)
    F = fishing_mortality(Y, B)
    b_ratio = B / rp["B_MSY"] if rp["B_MSY"] > 0 else float("nan")
    f_ratio = F / rp["F_MSY"] if rp["F_MSY"] > 0 else float("inf")
    depletion = B / rp["B_0"] if rp["B_0"] > 0 else float("nan")

    overfished = b_ratio < 1.0
    overfishing = f_ratio > 1.0
    if overfished and overfishing:
        quadrant = "OVERFISHED_AND_OVERFISHING"
    elif overfished:
        quadrant = "OVERFISHED_REBUILDING"
    elif overfishing:
        quadrant = "OVERFISHING_NOT_YET_OVERFISHED"
    else:
        quadrant = "HEALTHY"

    return {
        "B":            B,
        "Y":            Y,
        "F":            F,
        "B_over_B_MSY": b_ratio,
        "F_over_F_MSY": f_ratio,
        "B_over_B_0":   depletion,
        "overfished":   overfished,      # STATE
        "overfishing":  overfishing,     # RATE
        "quadrant":     quadrant,
        "surplus_production": (surplus_production(B, r, K) if p is None
                               else surplus_production_pella_tomlinson(
                                   B, r, K, p)),
        "dB_dt":        biomass_rate(B, r, K, Y, p),
        "reference_points": rp,
    }


def project(B0: float, r: float, K: float,
            yields: Sequence[float],
            p: Optional[float] = None) -> List[Dict[str, float]]:
    """
    Project biomass forward under a yield series (annual time step,
    Euler). Returns one record per year with the standard ratios, so a
    management path can be read as a trajectory across the Kobe plot
    rather than a single verdict.
    """
    rp = reference_points(r, K, p)
    out: List[Dict[str, float]] = []
    B = B0
    for year, Y in enumerate(yields, start=1):
        dB = biomass_rate(B, r, K, Y, p)
        B = max(0.0, B + dB)
        out.append({
            "year":         year,
            "yield":        Y,
            "B":            B,
            "B_over_B_MSY": B / rp["B_MSY"] if rp["B_MSY"] > 0 else float("nan"),
            "B_over_B_0":   B / rp["B_0"] if rp["B_0"] > 0 else float("nan"),
            "F_over_F_MSY": (fishing_mortality(Y, B) / rp["F_MSY"]
                             if rp["F_MSY"] > 0 and B > 0 else float("inf")),
        })
    return out


def msy_is_a_ceiling_not_a_target(B: float, r: float, K: float
                                  ) -> Dict[str, object]:
    """
    Fishing exactly at MSY leaves zero margin: at B_MSY the stock sits at
    the top of the production curve, where any downward error in r, K, or
    recruitment turns the target into an overshoot with no surplus left
    to absorb it.

    Returns the production CHANGE from a downward biomass error at B_MSY
    versus at a more conservative biomass. Positive = production lost.
    Negative = production gained, which is the asymmetry: above the peak,
    an error walks you toward higher production; at the peak, every error
    is a loss, in both directions.
    """
    rp = reference_points(r, K)
    B_msy = rp["B_MSY"]
    err = 0.1 * B_msy
    loss_at_msy = (surplus_production(B_msy, r, K)
                   - surplus_production(B_msy - err, r, K))
    B_cons = 0.75 * K
    loss_at_cons = (surplus_production(B_cons, r, K)
                    - surplus_production(B_cons - err, r, K))
    return {
        "B_MSY":              B_msy,
        "MSY":                rp["MSY"],
        "production_change_from_10pct_error_at_B_MSY":  loss_at_msy,
        "production_change_from_same_error_at_0.75K":   loss_at_cons,
        "error_is_all_downside_at_B_MSY": loss_at_msy >= 0 > loss_at_cons,
        "buffer_at_B_MSY":    surplus_production(B_msy, r, K) - rp["MSY"],
        "note": "at B_MSY the surplus curve is flat and the stock is at "
                "peak production with no reserve; error in either "
                "direction is absorbed by the stock, not the quota",
    }


if __name__ == "__main__":
    print("SURPLUS PRODUCTION — SCHAEFER")
    print("=" * 70)
    r, K = 0.4, 100_000.0
    rp = reference_points(r, K)
    print(f"  r = {r}, K = {K:,.0f} t")
    print(f"  B_MSY = {rp['B_MSY']:,.0f} t   F_MSY = {rp['F_MSY']:.3f}/yr   "
          f"MSY = {rp['MSY']:,.0f} t/yr")

    print("\n\nRATE AND STATE ARE DIFFERENT QUESTIONS")
    print("=" * 70)
    print(f"  {'B (t)':>10} {'Y (t/yr)':>10} {'B/B_MSY':>9} {'F/F_MSY':>9} "
          f"{'B/B_0':>7}  quadrant")
    for B, Y in ((80_000, 8_000), (50_000, 10_000), (50_000, 15_000),
                 (20_000, 5_000), (20_000, 1_000), (8_000, 500)):
        s = stock_status(B, Y, r, K)
        print(f"  {B:10,.0f} {Y:10,.0f} {s['B_over_B_MSY']:9.2f} "
              f"{s['F_over_F_MSY']:9.2f} {s['B_over_B_0']:7.2f}  "
              f"{s['quadrant']}")
    print("\n  Rows 4 and 5 are the same stock at the same biomass. One is")
    print("  rebuilding, one is not. A single combined index cannot say")
    print("  which — that is why the two ratios are reported separately.")

    print("\n\nMSY AS A CEILING")
    print("=" * 70)
    m = msy_is_a_ceiling_not_a_target(rp["B_MSY"], r, K)
    print(f"  production change from a 10% biomass drop at B_MSY : "
          f"{m['production_change_from_10pct_error_at_B_MSY']:+,.0f} t/yr")
    print(f"  same drop at 0.75K                                 : "
          f"{m['production_change_from_same_error_at_0.75K']:+,.0f} t/yr")
    print("  (positive = production lost). Above the peak an error buys")
    print("  production back; at the peak both directions cost.")

    print("\n\nPROJECTION AT CONSTANT YIELD = MSY")
    print("=" * 70)
    path = project(rp["B_MSY"], r, K, [rp["MSY"] * 1.05] * 12)
    for rec in path[::3]:
        print(f"  year {rec['year']:2d}: B = {rec['B']:9,.0f} t   "
              f"B/B_MSY = {rec['B_over_B_MSY']:.3f}   "
              f"F/F_MSY = {rec['F_over_F_MSY']:.3f}")
    print("\n  5% above MSY, held constant, walks the stock down. The quota")
    print("  never changed; the surplus that was funding it did.")
