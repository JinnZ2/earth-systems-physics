# functional_response.py
# earth-systems-physics / extraction_dynamics
# CC0 — No Rights Reserved
#
# Holling functional responses, the low-density refuge, and the
# mechanism by which detection technology removes it.
#
#   f_I   = a*N                        linear, no saturation
#   f_II  = a*N / (1 + a*h*N)          saturating, NO low-density refuge
#   f_III = a*N^q / (1 + a*h*N^q)      sigmoidal for q > 1, refuge present
#
# a : attack rate / search efficiency        (area or volume per time)
# h : handling time per resource item        (time per item)
# q : refuge exponent, 1 <= q <= 2
#
# WHY THE REFUGE EXISTS
# ---------------------
# Type III is sigmoidal because searchers LOSE efficiency when prey are
# rare: search image fades, prey use spatial refuges, encounter rates
# fall faster than linearly. The per-capita mortality imposed on the
# resource, f(N)/N, therefore DECLINES toward zero as N declines. That
# decline is the refuge. It is what lets a depleted population escape.
#
# Type II has no such term. f(N)/N -> a as N -> 0: per-capita mortality
# is at its MAXIMUM when the resource is rarest. A Type II consumer
# tracks the last individuals as efficiently as the first.
#
# WHAT TECHNOLOGY DOES
# --------------------
#   sonar / satellite / spotter aircraft / AI routing  ->  raises a
#   automated handling / at-sea processing             ->  lowers h
#   removal of the search-efficiency floor             ->  drives q -> 1
#
# The third is the one that matters. Raising a and lowering h make the
# consumer faster. Driving q to 1 collapses Type III to Type II and
# DELETES the refuge. The stock then has no density low enough to be
# uneconomic to pursue.
#
# This is falsifiable: fit both forms to CPUE-vs-abundance data by
# decade and test which wins. a, h, and q are estimable. The refuge is
# estimable. See fit_functional_response().
#
# Standard library only.

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

# ─────────────────────────────────────────────
# FUNCTIONAL RESPONSES
# ─────────────────────────────────────────────


def holling_I(N: float, a: float, N_sat: float = float("inf")) -> float:
    """
    Type I: linear intake, optionally truncated at a saturation density.

    N     : resource density
    a     : attack rate (intake per consumer per unit resource per time)
    N_sat : density at which intake caps (default: never)
    returns: per-consumer intake rate
    """
    return a * min(N, N_sat)


def holling_II(N: float, a: float, h: float) -> float:
    """
    Type II: saturating (disc equation). f = a*N / (1 + a*h*N).

    Maximum intake is 1/h. There is NO low-density refuge: per-capita
    mortality on the resource is maximal exactly when the resource is
    rarest.

    N : resource density
    a : attack rate
    h : handling time per item
    returns: per-consumer intake rate
    """
    if N <= 0:
        return 0.0
    return a * N / (1.0 + a * h * N)


def holling_III(N: float, a: float, h: float, q: float = 2.0) -> float:
    """
    Type III: sigmoidal. f = a*N^q / (1 + a*h*N^q).

    q = 2 is the textbook sigmoidal form. q = 1 IS Type II — the
    parameter is continuous, so refuge loss can be measured as a drift
    in q rather than a change of model.

    N : resource density
    a : attack rate
    h : handling time per item
    q : refuge exponent (1 = no refuge, 2 = full sigmoidal refuge)
    returns: per-consumer intake rate
    """
    if N <= 0:
        return 0.0
    Nq = N ** q
    return a * Nq / (1.0 + a * h * Nq)


def response(N: float, a: float, h: float, q: float = 2.0,
             kind: str = "III") -> float:
    """Dispatch to a named functional response ('I', 'II', 'III')."""
    k = kind.upper().strip()
    if k == "I":
        return holling_I(N, a)
    if k == "II":
        return holling_II(N, a, h)
    if k == "III":
        return holling_III(N, a, h, q)
    raise ValueError(f"unknown functional response '{kind}' (use I, II, III)")


# ─────────────────────────────────────────────
# THE REFUGE
# ─────────────────────────────────────────────


def per_capita_mortality(N: float, a: float, h: float, q: float = 2.0,
                         kind: str = "III") -> float:
    """
    Mortality imposed per resource individual, f(N)/N.

    This is the quantity that carries the refuge. Constant or rising as
    N falls means no refuge; falling toward zero means refuge present.
    """
    if N <= 0:
        return 0.0
    return response(N, a, h, q, kind) / N


def refuge_index(N_low: float, a: float, h: float, q: float = 2.0,
                 kind: str = "III", N_ref: Optional[float] = None) -> float:
    """
    Strength of the low-density refuge at density N_low, on [0, 1].

        refuge = 1 - (per-capita mortality at N_low) / (its maximum)

    0.0 : no refuge — the last individuals are hunted as hard as the
          first (Type II, or Type III with q -> 1)
    ->1 : strong refuge — per-capita pressure vanishes as the resource
          becomes rare

    N_low : the low density of interest
    N_ref : density used to normalise. Defaults to the density at which
            per-capita mortality peaks, found by coarse scan.
    """
    if N_low <= 0:
        return 1.0
    m_low = per_capita_mortality(N_low, a, h, q, kind)
    if N_ref is not None:
        m_max = per_capita_mortality(N_ref, a, h, q, kind)
    else:
        # scan for the maximum of f(N)/N; for Type II it sits at N -> 0
        scan = [per_capita_mortality(N_low * s, a, h, q, kind)
                for s in (1e-4, 1e-3, 1e-2, 0.1, 0.5, 1.0, 2.0, 5.0,
                          10.0, 100.0)]
        m_max = max(scan)
    if m_max <= 0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - m_low / m_max))


def escape_density(a: float, h: float, q: float = 2.0,
                   threshold: float = 0.5,
                   N_max: float = 1.0, steps: int = 4000) -> Optional[float]:
    """
    Lowest density at which the refuge is still at least `threshold`
    strong — i.e. the density above which the resource is NOT protected
    and below which it is.

    This is the mechanistic replacement for an arbitrary percentage
    floor: "hold N above the density where f_III still bends" is a
    statement about the shape of the response, not a chosen number.

    Returns None when no such density exists (Type II: never protected).
    """
    if steps < 2:
        raise ValueError("steps must be >= 2")
    lo = N_max / steps
    for i in range(1, steps + 1):
        N = N_max * i / steps
        if refuge_index(N, a, h, q, "III", N_ref=N_max) < threshold:
            return N if N > lo else lo
    return None


# ─────────────────────────────────────────────
# TECHNOLOGY AS A PARAMETER SHIFT
# ─────────────────────────────────────────────


@dataclass
class SearchTechnology:
    """
    A detection/handling technology expressed as what it does to the
    functional response parameters. No narrative, three numbers.

    a_multiplier    : factor on attack rate (detection, routing, range)
    h_multiplier    : factor on handling time (automation, processing)
    q_reduction     : absolute reduction in the refuge exponent, i.e.
                       how much of the search-efficiency floor it removes
    """
    name:         str
    a_multiplier: float
    h_multiplier: float
    q_reduction:  float
    note:         str = ""


# Reference technologies. The multipliers are ORDER-OF-MAGNITUDE
# ANCHORS for comparing mechanisms, not fitted values — fit a, h, q to
# your own CPUE series before using any number here as an estimate.
TECHNOLOGIES: Dict[str, SearchTechnology] = {
    "unaided_search": SearchTechnology(
        "unaided_search", 1.0, 1.0, 0.0,
        "baseline: searcher efficiency falls when the resource is rare"),
    "echo_sounder": SearchTechnology(
        "echo_sounder", 2.0, 1.0, 0.2,
        "direct detection replaces inference from surface signs"),
    "spotter_aircraft": SearchTechnology(
        "spotter_aircraft", 3.0, 1.0, 0.25,
        "search area per unit time rises by orders of magnitude"),
    "satellite_and_oceanographic_routing": SearchTechnology(
        "satellite_and_oceanographic_routing", 4.0, 1.0, 0.3,
        "aggregation sites predicted rather than searched for"),
    "ai_routing_on_pooled_fleet_data": SearchTechnology(
        "ai_routing_on_pooled_fleet_data", 5.0, 0.9, 0.4,
        "the fleet's collective detections remove the individual "
        "searcher's efficiency loss entirely"),
    "at_sea_processing": SearchTechnology(
        "at_sea_processing", 1.0, 0.2, 0.0,
        "handling time no longer limits intake; trip length no longer "
        "limits pursuit"),
    "automated_handling": SearchTechnology(
        "automated_handling", 1.0, 0.35, 0.0,
        "labour no longer bounds throughput"),
}


def apply_technology(a: float, h: float, q: float,
                     technologies: Sequence[str]) -> Dict[str, float]:
    """
    Apply a stack of technologies to (a, h, q) and report what happened
    to the refuge.

    Returns a dict with the shifted parameters, the refuge index before
    and after at a low density, and whether the response has effectively
    collapsed to Type II (q <= 1.05).
    """
    a_new, h_new, q_new = a, h, q
    applied = []
    for name in technologies:
        key = name.lower().strip()
        if key not in TECHNOLOGIES:
            raise KeyError(f"unknown technology '{name}'; "
                           f"valid: {sorted(TECHNOLOGIES)}")
        t = TECHNOLOGIES[key]
        a_new *= t.a_multiplier
        h_new *= t.h_multiplier
        q_new = max(1.0, q_new - t.q_reduction)
        applied.append(t.name)

    N_low = 0.05
    before = refuge_index(N_low, a, h, q, "III", N_ref=1.0)
    after = refuge_index(N_low, a_new, h_new, q_new, "III", N_ref=1.0)
    return {
        "technologies":       applied,
        "a_before":           a,
        "a_after":            a_new,
        "h_before":           h,
        "h_after":            h_new,
        "q_before":           q,
        "q_after":            q_new,
        "refuge_before":      before,
        "refuge_after":       after,
        "refuge_lost":        before - after,
        "collapsed_to_type_II": q_new <= 1.05,
        "max_intake_before":  1.0 / h if h > 0 else float("inf"),
        "max_intake_after":   1.0 / h_new if h_new > 0 else float("inf"),
    }


# ─────────────────────────────────────────────
# FITTING — THE FALSIFIABLE PART
# ─────────────────────────────────────────────


def _sse(observed: Sequence[float], predicted: Sequence[float]) -> float:
    return sum((o - p) ** 2 for o, p in zip(observed, predicted))


def _fit_ah_given_q(N: Sequence[float], intake: Sequence[float],
                    q: float) -> Optional[Dict[str, float]]:
    """
    Least-squares (a, h) for a fixed refuge exponent q, via the
    Lineweaver-Burk style linearisation of the disc equation:

        1/f = 1/(a * N^q) + h        ->  y = (1/a) * x + h

    with y = 1/f and x = 1/N^q. Slope gives a, intercept gives h. The
    regression is done in the transformed space (closed form, no
    optimiser); the reported SSE is computed in the ORIGINAL space, so
    model comparison is not distorted by the transform.

    Returns None when the fit is degenerate or gives non-physical
    (negative) parameters.
    """
    xs, ys = [], []
    for n, f in zip(N, intake):
        if n > 0 and f > 0:
            xs.append(1.0 / (n ** q))
            ys.append(1.0 / f)
    if len(xs) < 3:
        return None
    n_pts = len(xs)
    mx = sum(xs) / n_pts
    my = sum(ys) / n_pts
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    if slope <= 0:
        return None
    a = 1.0 / slope
    h = max(intercept, 0.0)      # handling time cannot be negative
    pred = [holling_III(n, a, h, q) for n in N]
    return {"a": a, "h": h, "q": q, "sse": _sse(intake, pred)}


def fit_functional_response(N: Sequence[float], intake: Sequence[float],
                            q_grid: Optional[Sequence[float]] = None,
                            improvement_threshold: float = 0.10
                            ) -> Dict[str, object]:
    """
    Fit Type II and Type III to observed intake (or CPUE) against
    resource density, and report which form wins.

    Method: for each candidate refuge exponent q, (a, h) are obtained in
    closed form by linear regression on the reciprocal transform; SSE is
    then evaluated in the original space and the best q selected. Type
    II is the q = 1 case, so the two forms are nested and comparable.

    Screening tool, not a substitute for a likelihood fit with an
    observation-error model. It exists so the refuge claim can be TESTED
    against a data series rather than asserted.

    Interpretation: run it per decade on the same stock. A drift of the
    winning model from III to II, or of fitted q from ~2 toward 1, is
    the refuge being removed. That is the measurement the argument
    stands or falls on.

    N      : resource density or abundance index
    intake : per-consumer intake, or CPUE
    q_grid : refuge exponents to scan (default 1.00 to 2.00 by 0.02)
    improvement_threshold : fractional SSE reduction Type III must
             achieve to be credited with its extra parameter
    returns: dict with both fits, the winner, and the fitted refuge
    """
    if len(N) != len(intake):
        raise ValueError("N and intake must be the same length")
    if len(N) < 4:
        raise ValueError("need at least 4 points to distinguish the forms")
    if q_grid is None:
        q_grid = [1.0 + 0.02 * k for k in range(51)]      # 1.00 .. 2.00

    N_max = max(N) or 1.0

    fit_II = _fit_ah_given_q(N, intake, 1.0)
    if fit_II is None:
        raise ValueError("degenerate data: cannot fit a functional response")
    best_II = {"sse": fit_II["sse"], "a": fit_II["a"], "h": fit_II["h"]}

    best_III = {"sse": float("inf"), "a": None, "h": None, "q": None}
    for q in q_grid:
        fit = _fit_ah_given_q(N, intake, q)
        if fit is not None and fit["sse"] < best_III["sse"]:
            best_III = fit

    if best_III["a"] is None:
        best_III = dict(fit_II)

    # Type III has one extra parameter; require a real improvement
    # before crediting it. The threshold is a screening rule, not an
    # information criterion.
    improvement = ((best_II["sse"] - best_III["sse"]) / best_II["sse"]
                   if best_II["sse"] > 0 else 0.0)
    winner = "III" if improvement > improvement_threshold else "II"

    q_fit = best_III["q"] if winner == "III" else 1.0
    a_fit = best_III["a"] if winner == "III" else best_II["a"]
    h_fit = best_III["h"] if winner == "III" else best_II["h"]

    return {
        "type_II":            best_II,
        "type_III":           best_III,
        "winner":             winner,
        "sse_improvement":    improvement,
        "q_fitted":           q_fit,
        "refuge_index_at_5pct": refuge_index(0.05 * N_max, a_fit, h_fit,
                                             q_fit, "III", N_ref=N_max),
        "refuge_present":     winner == "III" and q_fit > 1.2,
        "note": "coarse grid search; screening only. Refit with a proper "
                "likelihood and observation-error model before using the "
                "parameter values as estimates.",
    }


if __name__ == "__main__":
    print("FUNCTIONAL RESPONSE — THE LOW-DENSITY REFUGE")
    print("=" * 70)
    a, h = 2.0, 1.0
    print(f"{'N':>8} {'f_II':>10} {'f_III':>10} "
          f"{'m/cap II':>10} {'m/cap III':>10} {'refuge III':>11}")
    for N in (1.0, 0.5, 0.2, 0.1, 0.05, 0.01):
        print(f"{N:8.3f} {holling_II(N, a, h):10.4f} "
              f"{holling_III(N, a, h):10.4f} "
              f"{per_capita_mortality(N, a, h, kind='II'):10.4f} "
              f"{per_capita_mortality(N, a, h, 2.0, 'III'):10.4f} "
              f"{refuge_index(N, a, h, 2.0, 'III', N_ref=1.0):11.3f}")
    print("\n  Type II per-capita mortality is HIGHEST when the resource")
    print("  is rarest. That is the whole problem, in one column.")

    print("\n\nTECHNOLOGY STACK — REFUGE REMOVAL")
    print("=" * 70)
    for stack in (["echo_sounder"],
                  ["echo_sounder", "at_sea_processing"],
                  ["satellite_and_oceanographic_routing", "at_sea_processing"],
                  ["ai_routing_on_pooled_fleet_data", "automated_handling"]):
        r = apply_technology(2.0, 1.0, 2.0, stack)
        print(f"\n  {' + '.join(stack)}")
        print(f"    a: {r['a_before']:.2f} -> {r['a_after']:.2f}   "
              f"h: {r['h_before']:.2f} -> {r['h_after']:.2f}   "
              f"q: {r['q_before']:.2f} -> {r['q_after']:.2f}")
        print(f"    refuge at N=0.05: {r['refuge_before']:.3f} -> "
              f"{r['refuge_after']:.3f}   "
              f"(Type II: {r['collapsed_to_type_II']})")

    print("\n\nFIT TEST — CAN WE TELL THE FORMS APART?")
    print("=" * 70)
    Ns = [0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0]
    sig = [holling_III(n, 2.0, 1.0, 2.0) for n in Ns]
    sat = [holling_II(n, 2.0, 1.0) for n in Ns]
    for label, series in (("sigmoidal source", sig), ("saturating source", sat)):
        fit = fit_functional_response(Ns, series)
        print(f"  {label:20s} -> winner Type {fit['winner']}, "
              f"q={fit['q_fitted']:.2f}, "
              f"refuge={fit['refuge_index_at_5pct']:.3f}")
