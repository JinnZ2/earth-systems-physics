# depensation.py
# earth-systems-physics / extraction_dynamics
# CC0 — No Rights Reserved
#
# Depensation (the Allee effect) on the recruitment side, and what it
# produces when combined with refuge removal on the mortality side.
#
#   R(S) = alpha*S^2 / (beta^2 + S^2)        depensatory recruitment
#
# Per-capita recruitment R(S)/S RISES with spawner biomass at low S,
# instead of being flat or falling. Mechanisms: mate limitation, failed
# spawning aggregations, loss of group defence, dilution of gametes,
# habitat conditioning by the population itself (oyster reef, kelp
# holdfast, coral structure).
#
# THE PREDATOR PIT
# ----------------
# Depensatory recruitment curves upward through a mortality line that is
# roughly linear at low density. When the two cross more than once, the
# low crossing is a STABLE equilibrium at near-zero biomass, the middle
# crossing is UNSTABLE, and the high crossing is the productive state.
# The region between them is the pit: a stock pushed below the unstable
# crossing falls into the low state and stays there even if fishing
# stops entirely.
#
#   refuge removal (f_III -> f_II) + depensation = predator pit,
#   absorbing state, hysteresis
#
# This is why "we stopped fishing and it did not come back" is a
# prediction of the model rather than a mystery. The relevant control
# variable is not effort. It is whether the stock is above or below the
# unstable equilibrium.
#
# Standard library only.

from typing import Dict, List, Optional, Sequence, Tuple

from functional_response import response as _functional_response

# ─────────────────────────────────────────────
# RECRUITMENT FUNCTIONS
# ─────────────────────────────────────────────


def recruitment_depensatory(S: float, alpha: float, beta: float) -> float:
    """
    Depensatory (Allee) recruitment: R = alpha*S^2 / (beta^2 + S^2).

    S     : spawner biomass or abundance
    alpha : asymptotic maximum recruitment
    beta  : half-saturation spawner biomass — recruitment is alpha/2 here
    returns: recruits per time
    """
    if S <= 0:
        return 0.0
    return alpha * S * S / (beta * beta + S * S)


def recruitment_beverton_holt(S: float, alpha: float, beta: float) -> float:
    """
    Compensatory (Beverton-Holt) recruitment: R = alpha*S / (beta + S).

    The non-depensatory reference case. Per-capita recruitment is
    HIGHEST at low S — this is the compensation that makes a stock
    resilient, and the property depensation removes.
    """
    if S <= 0:
        return 0.0
    return alpha * S / (beta + S)


def recruitment_ricker(S: float, alpha: float, beta: float) -> float:
    """Ricker: R = alpha*S*exp(-beta*S). Overcompensatory at high S."""
    if S <= 0:
        return 0.0
    return alpha * S * math_exp(-beta * S)


def math_exp(x: float) -> float:
    """Local exp to keep the module import surface to one line."""
    import math
    return math.exp(x)


def per_capita_recruitment(S: float, alpha: float, beta: float,
                           kind: str = "depensatory") -> float:
    """
    R(S)/S — the quantity that distinguishes the recruitment regimes.

    depensatory : rises with S at low S  (the danger)
    compensatory: falls with S           (the safety margin)
    """
    if S <= 0:
        return 0.0
    return recruitment(S, alpha, beta, kind) / S


def recruitment(S: float, alpha: float, beta: float,
                kind: str = "depensatory") -> float:
    """Dispatch to a named stock-recruitment function."""
    k = kind.lower().strip()
    if k in ("depensatory", "allee"):
        return recruitment_depensatory(S, alpha, beta)
    if k in ("compensatory", "beverton_holt", "bh"):
        return recruitment_beverton_holt(S, alpha, beta)
    if k == "ricker":
        return recruitment_ricker(S, alpha, beta)
    raise ValueError(f"unknown recruitment form '{kind}'")


def is_depensatory(alpha: float, beta: float, kind: str = "depensatory",
                   S_lo: float = 1e-3, S_hi: float = 1.0) -> bool:
    """
    Test for depensation directly: does per-capita recruitment INCREASE
    from S_lo to S_hi? That inequality is the definition; no appeal to
    the functional form is needed.
    """
    return (per_capita_recruitment(S_hi, alpha, beta, kind)
            > per_capita_recruitment(S_lo, alpha, beta, kind))


# ─────────────────────────────────────────────
# EQUILIBRIA AND THE PIT
# ─────────────────────────────────────────────


def net_growth(S: float, alpha: float, beta: float,
               a: float, h: float, q: float, P: float,
               kind: str = "depensatory",
               response_kind: str = "III",
               natural_mortality: float = 0.0) -> float:
    """
    dS/dt = R(S) - f(S)*P - M*S

    Recruitment minus predation/harvest minus background mortality.
    """
    return (recruitment(S, alpha, beta, kind)
            - _functional_response(S, a, h, q, response_kind) * P
            - natural_mortality * S)


def find_equilibria(alpha: float, beta: float, a: float, h: float,
                    q: float, P: float, kind: str = "depensatory",
                    response_kind: str = "III",
                    natural_mortality: float = 0.0,
                    S_max: float = 2.0, steps: int = 4000
                    ) -> List[Dict[str, object]]:
    """
    Locate interior equilibria of dS/dt by sign change on a fine grid,
    and classify each as stable or unstable from the slope of dS/dt.

    Returns a list of {'S', 'stable'} ordered by biomass. Two or more
    interior equilibria means the system has a pit.
    """
    eq: List[Dict[str, object]] = []
    prev_S = S_max / steps
    prev = net_growth(prev_S, alpha, beta, a, h, q, P, kind,
                      response_kind, natural_mortality)
    for i in range(2, steps + 1):
        S = S_max * i / steps
        cur = net_growth(S, alpha, beta, a, h, q, P, kind,
                         response_kind, natural_mortality)
        if prev == 0.0 or (prev < 0.0) != (cur < 0.0):
            # linear interpolation of the crossing
            S_cross = S if cur == prev else prev_S - prev * (S - prev_S) / (cur - prev)
            # stable if dS/dt goes from positive to negative
            eq.append({"S": S_cross, "stable": prev > cur})
        prev_S, prev = S, cur
    return eq


def predator_pit(alpha: float, beta: float, a: float, h: float,
                 q: float, P: float, kind: str = "depensatory",
                 response_kind: str = "III",
                 natural_mortality: float = 0.0,
                 S_max: float = 2.0) -> Dict[str, object]:
    """
    Detect a predator pit and report the escape threshold.

    A pit exists when there is an UNSTABLE interior equilibrium: below
    it the stock declines to the low state regardless of how much
    fishing is removed, above it the stock rebuilds.

    That unstable equilibrium is the operational floor. It is derived
    from the recruitment and mortality curves, not chosen — which is the
    difference between a mechanistic constraint and a round number.
    """
    eq = find_equilibria(alpha, beta, a, h, q, P, kind, response_kind,
                         natural_mortality, S_max)
    unstable = [e for e in eq if not e["stable"]]
    stable = [e for e in eq if e["stable"]]

    # Extinction is an equilibrium too, and under depensation it is
    # usually the stable one. Scanning only the interior misses it,
    # which is precisely the error that makes collapse look surprising.
    S_tiny = 1e-6 * S_max
    zero_stable = net_growth(S_tiny, alpha, beta, a, h, q, P, kind,
                             response_kind, natural_mortality) < 0.0

    # A pit is an unstable interior equilibrium separating two stable
    # states, where the lower state may be extinction itself.
    has_pit = len(unstable) > 0 and (zero_stable or len(stable) > 1)

    return {
        "equilibria":        eq,
        "n_equilibria":      len(eq),
        "zero_is_stable":    zero_stable,
        "pit_present":       has_pit,
        "escape_threshold":  unstable[0]["S"] if unstable else None,
        "upper_state":       max((e["S"] for e in stable), default=None),
        "lower_state":       0.0 if zero_stable else min(
            (e["S"] for e in stable), default=0.0),
        "absorbing_at_zero": zero_stable,
        "no_viable_state":   len(stable) == 0 and zero_stable,
        "interpretation": (
            "no viable state remains at this consumer pressure — the only "
            "equilibrium is extinction"
            if len(stable) == 0 and zero_stable else
            "stock below the escape threshold will not rebuild on effort "
            "reduction alone — the control variable is biomass, not effort"
            if has_pit else
            "single interior equilibrium — effort reduction rebuilds the "
            "stock monotonically"
        ),
    }


def hysteresis_gap(alpha: float, beta: float, a: float, h: float,
                   q: float, kind: str = "depensatory",
                   response_kind: str = "III",
                   natural_mortality: float = 0.0,
                   P_max: float = 1.0, steps: int = 200,
                   S_max: float = 2.0) -> Dict[str, object]:
    """
    Sweep consumer pressure P up and back down, following the state, and
    measure the gap between the collapse point and the recovery point.

    A non-zero gap is hysteresis: the pressure that has to be removed to
    get the stock back is strictly less than the pressure that broke it.
    """
    # up-sweep: start in the productive state
    S = S_max * 0.9
    collapse_P: Optional[float] = None
    for i in range(steps + 1):
        P = P_max * i / steps
        S = _relax(S, alpha, beta, a, h, q, P, kind, response_kind,
                   natural_mortality)
        if collapse_P is None and S < 0.05 * S_max:
            collapse_P = P
            break

    if collapse_P is None:
        return {"hysteresis": False, "collapse_P": None, "recovery_P": None,
                "gap": 0.0,
                "note": "no collapse within the swept pressure range"}

    # down-sweep from the collapsed state
    S = 0.01 * S_max
    recovery_P: Optional[float] = None
    for i in range(steps, -1, -1):
        P = P_max * i / steps
        S = _relax(S, alpha, beta, a, h, q, P, kind, response_kind,
                   natural_mortality)
        if S > 0.5 * S_max:
            recovery_P = P
            break

    if recovery_P is None:
        # The collapsed stock sits below the escape threshold, so no
        # reduction in pressure — not even to zero — rebuilds it. The
        # remaining lever is biomass, not effort.
        return {
            "hysteresis":  True,
            "reversible":  False,
            "collapse_P":  collapse_P,
            "recovery_P":  None,
            "gap":         float("inf"),
            "note": (
                "collapsed state is absorbing: it does not recover at ANY "
                "pressure, including zero. Effort reduction is not a "
                "recovery instrument below the escape threshold; only "
                "biomass addition or a change in the recruitment curve is."
            ),
        }

    gap = collapse_P - recovery_P
    return {
        "hysteresis":  gap > 1e-9,
        "reversible":  True,
        "collapse_P":  collapse_P,
        "recovery_P":  recovery_P,
        "gap":         gap,
        "note": (
            "pressure must fall BELOW the recovery point, not merely back "
            "to the level that caused collapse"
            if gap > 1e-9 else "reversible along the same path"
        ),
    }


def _relax(S: float, alpha: float, beta: float, a: float, h: float,
           q: float, P: float, kind: str, response_kind: str,
           natural_mortality: float,
           dt: float = 0.05, steps: int = 400) -> float:
    """Relax the stock toward equilibrium at fixed consumer pressure."""
    for _ in range(steps):
        S = max(0.0, S + dt * net_growth(S, alpha, beta, a, h, q, P,
                                         kind, response_kind,
                                         natural_mortality))
    return S


if __name__ == "__main__":
    print("DEPENSATION — PER-CAPITA RECRUITMENT")
    print("=" * 70)
    alpha, beta = 1.0, 0.5
    print(f"{'S':>8} {'R depens':>10} {'R/S depens':>12} "
          f"{'R B-H':>10} {'R/S B-H':>10}")
    for S in (1.5, 1.0, 0.5, 0.2, 0.1, 0.05):
        print(f"{S:8.3f} {recruitment_depensatory(S, alpha, beta):10.4f} "
              f"{per_capita_recruitment(S, alpha, beta):12.4f} "
              f"{recruitment_beverton_holt(S, alpha, beta):10.4f} "
              f"{per_capita_recruitment(S, alpha, beta, 'compensatory'):10.4f}")
    print("\n  Compensatory: per-capita recruitment RISES as the stock")
    print("  falls — that is the rebuilding engine. Depensatory: it FALLS.")

    print("\n\nPREDATOR PIT — REFUGE INTACT vs REFUGE REMOVED")
    print("=" * 70)
    print("  alpha=1.0 beta=0.5 a=1.2 h=1.0 M=0.4; sweeping consumer "
          "pressure P")
    print(f"\n  {'P':>5} {'escape (III)':>13} {'escape (II)':>12} "
          f"{'upper (III)':>12} {'upper (II)':>11}")
    for P in (0.1, 0.3, 0.5, 0.8):
        pit3 = predator_pit(alpha, beta, 1.2, 1.0, 2.0, P,
                            response_kind="III", natural_mortality=0.4,
                            S_max=3.0)
        pit2 = predator_pit(alpha, beta, 1.2, 1.0, 1.0, P,
                            response_kind="II", natural_mortality=0.4,
                            S_max=3.0)
        def _f(x):
            return f"{x:.3f}" if isinstance(x, float) else "none"
        print(f"  {P:5.2f} {_f(pit3['escape_threshold']):>13} "
              f"{_f(pit2['escape_threshold']):>12} "
              f"{_f(pit3['upper_state']):>12} {_f(pit2['upper_state']):>11}")
    print("\n  Removing the refuge does not only lower the stock — it "
          "RAISES\n  the biomass you have to stay above to keep it.")

    pit = predator_pit(alpha, beta, 1.2, 1.0, 1.0, 0.8,
                       response_kind="II", natural_mortality=0.5, S_max=3.0)
    print(f"\n  Type II, M=0.5, P=0.8: viable state exists? "
          f"{pit['upper_state'] is not None}")
    print(f"    -> {pit['interpretation']}")

    print("\n\nHYSTERESIS")
    print("=" * 70)
    hy = hysteresis_gap(alpha, beta, a=1.2, h=1.0, q=1.0,
                        response_kind="II", natural_mortality=0.4,
                        P_max=2.0, S_max=3.0)
    print(f"  collapse at P = {hy['collapse_P']}")
    print(f"  recovery at P = {hy['recovery_P']}")
    print(f"  gap           = {hy['gap']}")
    print(f"  -> {hy['note']}")
