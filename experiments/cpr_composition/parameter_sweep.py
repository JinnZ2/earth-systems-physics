# parameter_sweep.py
# earth-systems-physics / experiments/cpr_composition
# CC0 — No Rights Reserved
#
# Pilot instrument: find the regeneration rate g at which the experiment
# can measure anything.
#
# The sweep is not a result. It is a check on whether the design has a
# dependent variable. Three ways a CPR experiment produces no
# information, all of them parameter choices rather than findings:
#
#   g too low  : every group collapses whatever it does. Final stock is
#                0 for all arms. Zero variance, zero power.
#   g too high : no group can collapse even taking the cap every round.
#                Final stock is K for all arms. Same problem.
#   cap too low: the group physically cannot overshoot; the game is not
#                a commons dilemma, it is an annuity.
#
# The usable window is where restraint survives and maximisation does
# not. find_design_window() returns it. Run this BEFORE collecting data,
# and again on the pilot's realised parameters.
#
# Standard library only. Plotting is optional and guarded — a missing
# matplotlib must not stop the sweep from printing its numbers.

from typing import Dict, List, Optional, Sequence

from cpr_game import (
    GameParams, msy_total, simulate, sustainable_total,
)

# ─────────────────────────────────────────────
# SWEEP
# ─────────────────────────────────────────────


def linspace(lo: float, hi: float, n: int) -> List[float]:
    """Stdlib linspace — no numpy dependency for a nine-point sweep."""
    if n < 2:
        return [lo]
    step = (hi - lo) / (n - 1)
    return [lo + step * i for i in range(n)]


def sweep_g(g_values: Sequence[float],
            base: GameParams = GameParams()) -> List[Dict[str, object]]:
    """
    For each g: run all-max, run sustainable, and run every composition
    of maximisers, then report what the design would see.

    payoff_ratio is the quantity the original sweep was reaching for:
    total tokens under maximisation divided by total under restraint.
    Below 1 means restraint pays MORE than maximisation — the group
    dilemma is real but the individual incentive is not what it looks
    like, and that is worth knowing before running humans through it.
    """
    rows: List[Dict[str, object]] = []
    for g in g_values:
        p = GameParams(N=base.N, cap=base.cap, S0=base.S0, K=base.K,
                       g=g, T=base.T, token_value=base.token_value,
                       show_up_fee=base.show_up_fee)
        mx = simulate(p, policy="all_max").summary()
        su = simulate(p, policy="sustainable").summary()
        comps = [simulate(p, policy="mixed", n_max=k).summary()
                 for k in range(p.N + 1)]

        collapsed_flags = [c["collapsed"] for c in comps]
        rows.append({
            "g":                    g,
            "msy":                  msy_total(g, p.K),
            "sustainable_at_S0":    sustainable_total(p.S0, g, p.K),
            "max_final_S":          mx["final_stock"],
            "max_collapsed":        mx["collapsed"],
            "max_collapse_round":   mx["rounds_to_collapse"],
            "max_extracted":        mx["total_extracted"],
            "sus_final_S":          su["final_stock"],
            "sus_collapsed":        su["collapsed"],
            "sus_extracted":        su["total_extracted"],
            "payoff_ratio":         (mx["total_extracted"] / su["total_extracted"]
                                     if su["total_extracted"] > 0 else None),
            "n_compositions_collapsing": sum(collapsed_flags),
            "composition_S_over_K": [c["S_final_over_K"] for c in comps],
            "usable":               bool(mx["collapsed"]) and not bool(su["collapsed"]),
        })
    return rows


def find_design_window(rows: Sequence[Dict[str, object]]
                       ) -> Dict[str, object]:
    """
    The range of g in which the experiment has a dependent variable.

    Requires, at this g:
      - maximisation collapses the stock  (there is something to avoid)
      - restraint does not                (avoiding it is possible)
      - at least two compositions differ  (composition can matter at all)
    """
    usable = [r for r in rows if r["usable"]]
    separating = [
        r for r in usable
        if len(set(round(float(x), 6)
                   for x in r["composition_S_over_K"])) > 1
    ]
    if not separating:
        return {
            "window_found": False,
            "g_min": None, "g_max": None, "recommended_g": None,
            "note": "no swept g gives both a collapse under maximisation "
                    "and survival under restraint with composition "
                    "separation — widen the sweep or change cap/T/S0 "
                    "before recruiting anyone",
        }
    gs = [float(r["g"]) for r in separating]
    # Recommend the g whose composition curve has the largest spread:
    # that is where the design can resolve a composition effect if one
    # exists, and it is the honest place to put the pilot.
    best = max(separating,
               key=lambda r: (max(r["composition_S_over_K"])
                              - min(r["composition_S_over_K"])))
    return {
        "window_found":   True,
        "g_min":          min(gs),
        "g_max":          max(gs),
        "recommended_g":  float(best["g"]),
        "spread_at_recommended": (max(best["composition_S_over_K"])
                                  - min(best["composition_S_over_K"])),
        "n_usable":       len(separating),
        "note": "recommended g maximises the spread of final stock across "
                "compositions — the parameter at which a composition "
                "effect, if real, is resolvable",
    }


def composition_slope(rows: Sequence[Dict[str, object]], g: float
                      ) -> Dict[str, object]:
    """
    Least-squares slope of S_final/K on n_max at one g, from the
    MECHANICAL baseline.

    This is the number H2's estimate must be compared against. If the
    game itself produces a slope of -0.20 when players are pure
    maximisers or pure restrainers, then finding -0.20 in humans is not
    evidence about personality — it is evidence that some people took
    more, which was the input.

    Also reports whether the mechanical curve is a step rather than a
    line, because a linear model fitted to a threshold underestimates
    the effect at the threshold and overestimates it everywhere else.
    """
    row = min(rows, key=lambda r: abs(float(r["g"]) - g))
    y = [float(v) for v in row["composition_S_over_K"]]
    x = list(range(len(y)))
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    slope = sxy / sxx if sxx > 0 else 0.0

    # step detection: one gap dominates the others
    gaps = [abs(y[i + 1] - y[i]) for i in range(n - 1)]
    biggest = max(gaps) if gaps else 0.0
    rest = sorted(gaps)[:-1] if len(gaps) > 1 else [0.0]
    stepwise = biggest > 3.0 * (sum(rest) / len(rest) + 1e-12)

    return {
        "g":                float(row["g"]),
        "curve":            y,
        "mechanical_slope": slope,
        "is_step_not_line": stepwise,
        "step_between":     (gaps.index(biggest), gaps.index(biggest) + 1)
                            if stepwise else None,
        "note": ("the mechanical curve is a THRESHOLD, not a slope: a "
                 "linear model will estimate an average that describes "
                 "no group. Pre-register the threshold specification as "
                 "primary, or state that the linear slope is a "
                 "deliberately coarse summary"
                 if stepwise else
                 "mechanical curve is approximately linear; a linear "
                 "specification is a fair summary"),
    }


def defection_incentive(p: GameParams = GameParams()) -> Dict[str, object]:
    """
    Is this actually a social dilemma at the INDIVIDUAL level?

    Group totals can mislead: restraint can yield more tokens for the
    group while defection still yields more for the defector, which is
    the definition of the dilemma. The test is one player's own earnings:

        defect  : this player takes the cap, the other N-1 restrain
        comply  : all N restrain

    dilemma_present is True when the defector personally earns more by
    defecting. If it is False, the design is not a commons dilemma at
    these parameters — participants who maximise are making a mistake
    rather than a defection, and the study would be measuring
    comprehension, not dominance.
    """
    mixed = simulate(p, policy="mixed", n_max=1)
    comply = simulate(p, policy="sustainable")

    defector = mixed.per_player_extracted[0]
    restrainer_in_mixed = (mixed.per_player_extracted[1]
                           if p.N > 1 else 0)
    complier = comply.per_player_extracted[0]

    return {
        "defector_tokens":            defector,
        "restrainer_tokens_in_mixed": restrainer_in_mixed,
        "tokens_if_all_comply":       complier,
        "defection_gain":             defector - complier,
        "defection_gain_usd":         (defector - complier) * p.token_value,
        "dilemma_present":            defector > complier,
        "exploitation_ratio":         (defector / restrainer_in_mixed
                                       if restrainer_in_mixed > 0 else None),
        "note": ("individual incentive to defect exists — the design is a "
                 "commons dilemma"
                 if defector > complier else
                 "NO individual incentive to defect at these parameters: "
                 "maximisers earn less than restrainers even when others "
                 "restrain. The study would measure comprehension, not "
                 "dominance. Re-tune before recruiting."),
    }


# ─────────────────────────────────────────────
# OPTIONAL PLOT
# ─────────────────────────────────────────────


def plot_sweep(rows: Sequence[Dict[str, object]],
               path: str = "sweep.png") -> Optional[str]:
    """
    Write the sweep plot if matplotlib is installed. Returns the path
    written, or None. Never raises on a missing dependency — the numbers
    are the deliverable, the plot is a convenience.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")          # no display in CI or on a server
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    gs = [r["g"] for r in rows]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(gs, [r["max_final_S"] for r in rows], "o-", label="all-max")
    ax.plot(gs, [r["sus_final_S"] for r in rows], "s-", label="sustainable")
    ax.set_xlabel("regeneration rate g")
    ax.set_ylabel("final stock after T rounds")
    ax.set_title("Design window: where the two policies differ")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


if __name__ == "__main__":
    base = GameParams()
    rows = sweep_g(linspace(0.2, 0.6, 9), base)

    print("PARAMETER SWEEP — DOES THIS DESIGN HAVE A DEPENDENT VARIABLE?")
    print("=" * 78)
    print(f"  {'g':>5} {'MSY':>6} {'max S':>7} {'max rd':>7} "
          f"{'sus S':>7} {'ratio':>6} {'n comp collapse':>16} {'usable':>7}")
    for r in rows:
        ratio = r["payoff_ratio"]
        print(f"  {r['g']:5.2f} {r['msy']:6.1f} {r['max_final_S']:7.2f} "
              f"{str(r['max_collapse_round']):>7} {r['sus_final_S']:7.2f} "
              f"{(f'{ratio:.2f}' if ratio else 'n/a'):>6} "
              f"{r['n_compositions_collapsing']:16d} "
              f"{str(r['usable']):>7}")

    print("\n  ratio = tokens under all-max / tokens under restraint.")
    print("  Below 1 means restraint pays MORE in total. The dilemma in")
    print("  this parameterisation is not that defection pays the group")
    print("  less — it pays the DEFECTOR less too, over 20 rounds.")

    win = find_design_window(rows)
    print("\n\nDESIGN WINDOW")
    print("=" * 78)
    if win["window_found"]:
        print(f"  usable g range   : {win['g_min']:.2f} - {win['g_max']:.2f}")
        print(f"  recommended g    : {win['recommended_g']:.2f}")
        print(f"  spread in S/K    : {win['spread_at_recommended']:.3f}")
    print(f"  -> {win['note']}")

    print("\n\nMECHANICAL COMPOSITION BASELINE")
    print("=" * 78)
    for g in (0.30, 0.40, 0.50):
        cs = composition_slope(rows, g)
        curve = "  ".join(f"{v:.2f}" for v in cs["curve"])
        print(f"  g={cs['g']:.2f}  S/K by n_max: {curve}")
        print(f"          slope={cs['mechanical_slope']:+.3f}   "
              f"step={cs['is_step_not_line']}  "
              f"between n_max {cs['step_between']}")
    print(f"\n  {composition_slope(rows, 0.40)['note']}")

    print("\n\nIS IT A DILEMMA AT THE INDIVIDUAL LEVEL?")
    print("=" * 78)
    for g in (0.30, 0.40, 0.50):
        d = defection_incentive(GameParams(g=g))
        print(f"  g={g:.2f}  defector {d['defector_tokens']:4d} tok  vs  "
              f"all-comply {d['tokens_if_all_comply']:4d} tok  "
              f"(gain ${d['defection_gain_usd']:+.2f})  "
              f"dilemma={d['dilemma_present']}")
    print(f"\n  {defection_incentive(GameParams(g=0.40))['note']}")
    print("  Group totals said restraint pays more; individual earnings say")
    print("  defection pays the defector more. Both are true, and only the")
    print("  second one is the dilemma.")

    written = plot_sweep(rows)
    status = written or "matplotlib not installed — the numbers are the output"
    print(f"\nplot: {status}")
