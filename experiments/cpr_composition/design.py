# design.py
# earth-systems-physics / experiments/cpr_composition
# CC0 — No Rights Reserved
#
# Block randomisation and the sample-size arithmetic that has to hold
# before anyone is recruited.
#
# Three failure modes this module is written to prevent, all of them
# present in the first draft of the randomiser:
#
#   1. UNSEEDED SHUFFLE. The participant draw was seeded; the shuffle of
#      group specifications was not. The assignment could not be
#      reproduced, which means it could not be audited.
#   2. SILENT DUPLICATE ASSIGNMENT. The fallback path re-drew from the
#      pool with a modulo index, so a participant could be placed in two
#      groups. The only assertion checked for duplicates WITHIN a group,
#      so a cross-group duplicate passed. assign_groups() raises instead
#      of falling back.
#   3. AN INFEASIBLE POOL, DISCOVERED LATE. A design balanced across
#      compositions 0..4 needs half its participants to be high-D, while
#      a top-tercile split supplies a third. The pool has to be sized
#      from the binding constraint, and the check belongs here, not in
#      the recruiting spreadsheet.
#
# Standard library only. Uses random.Random(seed) — reproducible from
# the seed alone, with no global state.

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

GOVERNANCE_ARMS = ("G0", "G1", "G2")


# ─────────────────────────────────────────────
# FEASIBILITY ARITHMETIC
# ─────────────────────────────────────────────


def screening_pool_required(groups_per_arm: int, n_arms: int = 3,
                            group_size: int = 4,
                            high_d_quantile: float = 1.0 / 3.0
                            ) -> Dict[str, object]:
    """
    How many people must be screened to fill a composition-balanced
    design.

    With compositions 0..group_size represented equally, the mean number
    of high-D members per group is group_size/2, so HALF of all
    participants must be high-D. A top-tercile screen supplies a third.
    The screening pool is therefore set by the high-D requirement:

        n_screened >= high_d_needed / high_d_quantile

    Returns every intermediate quantity, because a recruitment budget
    built on a single number is a recruitment budget nobody can check.
    """
    compositions = group_size + 1
    if groups_per_arm % compositions != 0:
        raise ValueError(
            f"groups_per_arm={groups_per_arm} is not divisible by "
            f"{compositions} compositions; the design cannot be balanced. "
            f"Use a multiple of {compositions}.")

    groups_per_composition = groups_per_arm // compositions
    total_groups = groups_per_arm * n_arms
    participants = total_groups * group_size

    # high-D slots: sum over compositions k=0..group_size, per arm
    high_per_arm = sum(k * groups_per_composition
                       for k in range(compositions))
    high_needed = high_per_arm * n_arms
    low_needed = participants - high_needed

    screened_for_high = math.ceil(high_needed / high_d_quantile)
    screened_for_low = math.ceil(low_needed / (1.0 - high_d_quantile))
    screened = max(screened_for_high, screened_for_low)

    return {
        "groups_per_arm":        groups_per_arm,
        "groups_per_composition": groups_per_composition,
        "total_groups":          total_groups,
        "participants":          participants,
        "high_d_needed":         high_needed,
        "low_d_needed":          low_needed,
        "high_d_share_required": high_needed / participants,
        "high_d_share_available": high_d_quantile,
        "binding_constraint":    ("high-D supply"
                                  if screened_for_high >= screened_for_low
                                  else "low-D supply"),
        "screening_pool":        screened,
        "screening_multiple":    screened / participants,
    }


def power_ols(effect_size: float, n_groups: int, n_predictors: int = 5,
              alpha: float = 0.05) -> Dict[str, float]:
    """
    Approximate power for a standardised regression slope, using the
    normal approximation to the t-test.

        se(beta) ~ sqrt((1 - R2_partial) / (n - k - 1))
        power    ~ P(|Z| > z_{alpha/2} - |beta| / se)

    Adequate for design arithmetic at n in the hundreds. It is NOT a
    substitute for a simulation-based power analysis on the actual
    estimator, and the preregistration says so.
    """
    df = max(n_groups - n_predictors - 1, 1)
    se = math.sqrt(1.0 / df)
    z_alpha = 1.959963984540054 if abs(alpha - 0.05) < 1e-9 else \
        _z_from_two_sided_alpha(alpha)
    z = abs(effect_size) / se
    power = _normal_cdf(z - z_alpha) + _normal_cdf(-z - z_alpha)
    return {
        "effect_size":   effect_size,
        "n_groups":      n_groups,
        "se_beta":       se,
        "power":         power,
        "n_for_80pct":   required_n(effect_size, 0.80, n_predictors, alpha),
    }


def required_n(effect_size: float, power: float = 0.80,
               n_predictors: int = 5, alpha: float = 0.05) -> int:
    """Groups needed to reach `power` for a standardised slope."""
    if effect_size == 0:
        return 10 ** 9
    z_alpha = _z_from_two_sided_alpha(alpha)
    z_beta = _z_from_power(power)
    n = ((z_alpha + z_beta) / abs(effect_size)) ** 2
    return int(math.ceil(n)) + n_predictors + 1


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _normal_ppf(q: float) -> float:
    """Inverse normal CDF by bisection — adequate and dependency-free."""
    if not 0.0 < q < 1.0:
        raise ValueError("q must be in (0,1)")
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _normal_cdf(mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _z_from_two_sided_alpha(alpha: float) -> float:
    return _normal_ppf(1.0 - alpha / 2.0)


def _z_from_power(power: float) -> float:
    return _normal_ppf(power)


# ─────────────────────────────────────────────
# COMPOSITE SCREENING SCORE
# ─────────────────────────────────────────────


def zscores(values: Sequence[float]) -> List[float]:
    """Sample z-scores. Returns zeros for a constant vector."""
    n = len(values)
    if n == 0:
        return []
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1) if n > 1 else 0.0
    sd = math.sqrt(var)
    if sd == 0:
        return [0.0] * n
    return [(v - mean) / sd for v in values]


def pearson(a: Sequence[float], b: Sequence[float]) -> float:
    """Pearson correlation, for the composite's coherence check."""
    n = len(a)
    if n < 2 or n != len(b):
        return float("nan")
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db) if da > 0 and db > 0 else float("nan")


def composite_coherence(sdo: Sequence[float], risk: Sequence[float],
                        discount: Sequence[float]) -> Dict[str, object]:
    """
    Do the three screening measures actually cohere into one dimension?

    The design averages z-scores of SDO-dominance, risk preference, and
    delay discounting into a single 'D score'. That average is only
    meaningful if the three covary. If they do not, the composite is a
    sum of unrelated things and its tercile split classifies nobody in
    particular.

    Reports the pairwise correlations and Cronbach's alpha for the
    three-item composite, and flags when the components should be
    analysed separately instead. Run this on the pilot, before the
    composite is used to assign anyone.
    """
    z1, z2, z3 = zscores(sdo), zscores(risk), zscores(discount)
    r12, r13, r23 = pearson(z1, z2), pearson(z1, z3), pearson(z2, z3)
    rs = [r for r in (r12, r13, r23) if r == r]     # drop NaN
    mean_r = sum(rs) / len(rs) if rs else float("nan")
    k = 3
    alpha = (k * mean_r) / (1.0 + (k - 1) * mean_r) if mean_r == mean_r \
        and (1.0 + (k - 1) * mean_r) != 0 else float("nan")
    coherent = mean_r == mean_r and mean_r >= 0.20

    return {
        "r_sdo_risk":       r12,
        "r_sdo_discount":   r13,
        "r_risk_discount":  r23,
        "mean_r":           mean_r,
        "cronbach_alpha":   alpha,
        "coherent":         coherent,
        "recommendation": (
            "composite is defensible; proceed with the D score"
            if coherent else
            "components do not cohere (mean r < 0.20): the composite "
            "averages unrelated constructs. Pre-registered fallback is "
            "to drop the composite and test the three components as "
            "separate predictors, accepting the multiplicity correction."
        ),
    }


def composite_score(sdo: Sequence[float], risk: Sequence[float],
                    discount: Sequence[float]) -> List[float]:
    """Mean of the three z-scores — the D score."""
    z1, z2, z3 = zscores(sdo), zscores(risk), zscores(discount)
    return [(a + b + c) / 3.0 for a, b, c in zip(z1, z2, z3)]


def high_d_flags(scores: Sequence[float],
                 quantile: float = 1.0 / 3.0) -> List[bool]:
    """
    Top-tercile split on the composite.

    Ties at the cut are resolved by rank, not by value, so the number of
    high-D participants is exactly the intended fraction even when the
    score has ties. A split that silently returns 40% high-D breaks the
    pool arithmetic above.
    """
    n = len(scores)
    if n == 0:
        return []
    n_high = int(round(n * quantile))
    order = sorted(range(n), key=lambda i: (-scores[i], i))
    flags = [False] * n
    for i in order[:n_high]:
        flags[i] = True
    return flags


# ─────────────────────────────────────────────
# BLOCK RANDOMISATION
# ─────────────────────────────────────────────


@dataclass
class GroupAssignment:
    group_id: int
    governance: str
    n_high_d: int
    members: List[str] = field(default_factory=list)


def assign_groups(participant_ids: Sequence[str],
                  high_d: Sequence[bool],
                  groups_per_arm: int,
                  seed: int,
                  arms: Sequence[str] = GOVERNANCE_ARMS,
                  group_size: int = 4) -> List[GroupAssignment]:
    """
    Block-randomise participants into groups crossed by composition
    (0..group_size high-D members) and governance arm.

    Every participant appears in AT MOST ONE group. If the pool cannot
    fill the design, this raises with the shortfall rather than reusing
    people — a duplicate participant is not a degraded design, it is
    fabricated data.

    seed : required, not optional. The assignment must be reproducible
           from the preregistration.
    """
    if len(participant_ids) != len(high_d):
        raise ValueError("participant_ids and high_d must be the same length")
    compositions = group_size + 1
    if groups_per_arm % compositions != 0:
        raise ValueError(
            f"groups_per_arm must be divisible by {compositions} to "
            f"balance compositions; got {groups_per_arm}")

    rng = random.Random(seed)

    high_pool = [pid for pid, h in zip(participant_ids, high_d) if h]
    low_pool = [pid for pid, h in zip(participant_ids, high_d) if not h]
    rng.shuffle(high_pool)
    rng.shuffle(low_pool)

    specs: List[Tuple[str, int]] = []
    per_comp = groups_per_arm // compositions
    for arm in arms:
        for k in range(compositions):
            specs.extend([(arm, k)] * per_comp)

    need_high = sum(k for _, k in specs)
    need_low = sum(group_size - k for _, k in specs)
    if need_high > len(high_pool) or need_low > len(low_pool):
        raise ValueError(
            f"pool cannot fill the design without reusing participants: "
            f"need {need_high} high-D (have {len(high_pool)}), "
            f"need {need_low} low-D (have {len(low_pool)}). "
            f"See screening_pool_required().")

    rng.shuffle(specs)                      # seeded, therefore auditable

    assignments: List[GroupAssignment] = []
    hi = lo = 0
    for gid, (arm, k) in enumerate(specs, start=1):
        members = high_pool[hi:hi + k] + low_pool[lo:lo + (group_size - k)]
        hi += k
        lo += group_size - k
        assignments.append(GroupAssignment(gid, arm, k, members))

    _validate(assignments, group_size)
    return assignments


def _validate(assignments: Sequence[GroupAssignment], group_size: int) -> None:
    """Every group full; every participant used at most once, globally."""
    seen = set()
    for a in assignments:
        if len(a.members) != group_size:
            raise AssertionError(
                f"group {a.group_id} has {len(a.members)} members")
        for m in a.members:
            if m in seen:
                raise AssertionError(
                    f"participant {m} assigned to more than one group")
            seen.add(m)


def assignment_balance(assignments: Sequence[GroupAssignment]
                       ) -> Dict[str, object]:
    """Cross-tabulate composition against governance arm."""
    table: Dict[str, Dict[int, int]] = {}
    for a in assignments:
        table.setdefault(a.governance, {})
        table[a.governance][a.n_high_d] = \
            table[a.governance].get(a.n_high_d, 0) + 1
    counts = [c for arm in table.values() for c in arm.values()]
    return {
        "table":     table,
        "balanced":  len(set(counts)) <= 1,
        "n_groups":  len(assignments),
        "n_participants": sum(len(a.members) for a in assignments),
    }


if __name__ == "__main__":
    print("SAMPLE-SIZE ARITHMETIC")
    print("=" * 74)
    for gpa in (20, 40, 60, 80):
        try:
            r = screening_pool_required(gpa)
        except ValueError as e:
            print(f"  groups/arm {gpa:3d}: INFEASIBLE — {e}")
            continue
        print(f"  groups/arm {gpa:3d} -> {r['total_groups']:3d} groups, "
              f"{r['participants']:4d} participants, "
              f"screen {r['screening_pool']:4d} "
              f"({r['screening_multiple']:.2f}x)  "
              f"binding: {r['binding_constraint']}")
    print("\n  Composition balance forces half the sample to be high-D while")
    print("  a top-tercile screen supplies a third. The 1.5x multiple is")
    print("  not slack — it is the design.")

    print("\n\nPOWER FOR THE COMPOSITION SLOPE")
    print("=" * 74)
    print(f"  {'groups':>8} {'power at b=0.20':>17} {'power at b=0.30':>17}")
    for n in (60, 120, 180, 240, 300):
        p20 = power_ols(0.20, n)["power"]
        p30 = power_ols(0.30, n)["power"]
        print(f"  {n:8d} {p20:17.3f} {p30:17.3f}")
    print(f"\n  groups needed for 80% power at b=0.20: "
          f"{required_n(0.20):d}")
    print(f"  groups needed for 80% power at b=0.30: "
          f"{required_n(0.30):d}")

    print("\n\nBLOCK RANDOMISATION")
    print("=" * 74)
    n_screen = 1500
    rng = random.Random(7)
    pids = [f"P{i:04d}" for i in range(n_screen)]
    sdo = [rng.gauss(0, 1) for _ in pids]
    risk = [0.4 * s + rng.gauss(0, 1) for s in sdo]
    disc = [0.3 * s + rng.gauss(0, 1) for s in sdo]

    coh = composite_coherence(sdo, risk, disc)
    print(f"  composite coherence: mean r = {coh['mean_r']:.3f}, "
          f"alpha = {coh['cronbach_alpha']:.3f}, "
          f"coherent = {coh['coherent']}")

    scores = composite_score(sdo, risk, disc)
    flags = high_d_flags(scores)
    print(f"  high-D flagged: {sum(flags)} of {len(flags)} "
          f"({sum(flags) / len(flags):.3f})")

    assignments = assign_groups(pids, flags, groups_per_arm=80, seed=2026)
    bal = assignment_balance(assignments)
    print(f"  assigned {bal['n_groups']} groups, "
          f"{bal['n_participants']} participants, "
          f"balanced = {bal['balanced']}")
    for arm, row in sorted(bal["table"].items()):
        print(f"    {arm}: " + "  ".join(f"n_high_d={k}: {v}"
                                          for k, v in sorted(row.items())))

    print("\n  Same seed, same assignment. Re-run to audit.")
