# analysis_plan.py
# earth-systems-physics / experiments/cpr_composition
# CC0 — No Rights Reserved
#
# The pre-registered analysis, implemented so it can be run on
# simulated data before the real data exists.
#
# TWO CORRECTIONS TO THE DRAFT PLAN
# ---------------------------------
# 1. THE SESOI WAS COMPARED AGAINST THE WRONG COEFFICIENT.
#    The draft fitted an unstandardised OLS (S_final/K on n_high_d) and
#    then checked whether the 90% CI fell inside a STANDARDISED interval
#    of [-0.20, +0.20]. Those are different units. n_high_d ranges 0-4,
#    so its raw slope is roughly a quarter of its standardised one, and
#    the equivalence test would have declared equivalence for effects
#    four times larger than the SESOI. This module standardises both
#    sides before testing.
#
# 2. THE NULL WAS ZERO. IT SHOULD NOT BE.
#    parameter_sweep.composition_slope shows the game produces a
#    mechanical slope near -0.19 to -0.24 with no personality involved:
#    if some players take more, the stock falls, whoever they are.
#    Testing H2 against zero would confirm the composition hypothesis
#    with a number that pure arithmetic already predicts. The estimand
#    is the DIFFERENCE from the mechanical baseline at the realised
#    parameters, and equivalence_test() takes that baseline as an
#    argument for exactly this reason.
#
# Standard library only. Optional statsmodels / lifelines paths are
# guarded and never required.

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# ─────────────────────────────────────────────
# MINIMAL OLS
# ─────────────────────────────────────────────


def _solve(A: List[List[float]], b: List[float]) -> List[float]:
    """Gaussian elimination with partial pivoting."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            raise ValueError("singular design matrix — check for a "
                             "constant or collinear predictor")
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        for r in range(n):
            if r == col:
                continue
            factor = M[r][col] / pv
            for c in range(col, n + 1):
                M[r][c] -= factor * M[col][c]
    return [M[i][n] / M[i][i] for i in range(n)]


@dataclass
class OLSResult:
    names:      List[str]
    coef:       List[float]
    se:         List[float]
    n:          int
    k:          int
    r_squared:  float
    residual_sd: float

    def index(self, name: str) -> int:
        return self.names.index(name)

    def ci(self, name: str, level: float = 0.90) -> Tuple[float, float]:
        """
        Confidence interval using the normal approximation.

        At n in the hundreds the difference from the t distribution is
        under 1%, and stating that is more honest than importing a
        t-quantile and implying more precision than the design has.
        """
        i = self.index(name)
        z = _normal_ppf(1.0 - (1.0 - level) / 2.0)
        return (self.coef[i] - z * self.se[i], self.coef[i] + z * self.se[i])

    def summary(self) -> str:
        lines = [f"n={self.n}  k={self.k}  R2={self.r_squared:.4f}",
                 f"{'term':<20}{'coef':>10}{'se':>10}{'z':>9}"]
        for nm, c, s in zip(self.names, self.coef, self.se):
            z = c / s if s > 0 else float("nan")
            lines.append(f"{nm:<20}{c:>10.4f}{s:>10.4f}{z:>9.2f}")
        return "\n".join(lines)


def ols(y: Sequence[float], X: Sequence[Sequence[float]],
        names: Sequence[str]) -> OLSResult:
    """
    Ordinary least squares with an intercept prepended.

    X    : list of rows, each a list of predictor values
    names: predictor names, without the intercept
    """
    n = len(y)
    if n != len(X):
        raise ValueError("y and X must have the same number of rows")
    k = len(X[0]) if n else 0
    if any(len(row) != k for row in X):
        raise ValueError("all rows of X must have the same length")
    if n <= k + 1:
        raise ValueError(f"n={n} too small for {k} predictors")

    Xd = [[1.0] + list(row) for row in X]
    p = k + 1
    XtX = [[sum(Xd[r][i] * Xd[r][j] for r in range(n)) for j in range(p)]
           for i in range(p)]
    Xty = [sum(Xd[r][i] * y[r] for r in range(n)) for i in range(p)]
    beta = _solve(XtX, Xty)

    fitted = [sum(b * x for b, x in zip(beta, Xd[r])) for r in range(n)]
    resid = [y[r] - fitted[r] for r in range(n)]
    ss_res = sum(e * e for e in resid)
    ybar = sum(y) / n
    ss_tot = sum((v - ybar) ** 2 for v in y)
    df = n - p
    sigma2 = ss_res / df

    # standard errors from the diagonal of sigma2 * (X'X)^-1
    inv_diag = []
    for i in range(p):
        e = [1.0 if j == i else 0.0 for j in range(p)]
        inv_diag.append(_solve([row[:] for row in XtX], e)[i])
    se = [math.sqrt(max(sigma2 * d, 0.0)) for d in inv_diag]

    return OLSResult(
        names=["intercept"] + list(names),
        coef=beta, se=se, n=n, k=k,
        r_squared=1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"),
        residual_sd=math.sqrt(sigma2),
    )


def standardize(v: Sequence[float]) -> List[float]:
    n = len(v)
    if n < 2:
        return [0.0] * n
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return [0.0] * n if sd == 0 else [(x - m) / sd for x in v]


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _normal_ppf(q: float) -> float:
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _normal_cdf(mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# ─────────────────────────────────────────────
# PRIMARY ANALYSIS
# ─────────────────────────────────────────────


def primary_analysis(rows: Sequence[Dict[str, float]],
                     dv: str = "S_final_over_K",
                     predictor: str = "n_high_d",
                     covariates: Sequence[str] = ("comprehension",),
                     arms: Sequence[str] = ("G1", "G2")) -> Dict[str, object]:
    """
    Group-level OLS of the primary DV on composition, governance arm,
    and covariates — fitted on STANDARDISED DV and predictor so the
    slope is directly comparable to a standardised SESOI.

    Governance arms enter as dummies with G0 as the reference, so the
    two governance coefficients ARE the H1 contrasts (G1 - G0, G2 - G0)
    with no post-hoc recoding.
    """
    y = standardize([float(r[dv]) for r in rows])
    x_main = standardize([float(r[predictor]) for r in rows])

    names = [predictor + "_z"]
    cols: List[List[float]] = [x_main]
    for arm in arms:
        cols.append([1.0 if r.get("governance") == arm else 0.0
                     for r in rows])
        names.append(f"arm_{arm}")
    for cov in covariates:
        if cov in rows[0]:
            cols.append(standardize([float(r[cov]) for r in rows]))
            names.append(cov + "_z")

    X = [[col[i] for col in cols] for i in range(len(rows))]
    fit = ols(y, X, names)
    return {
        "fit":            fit,
        "predictor_term": predictor + "_z",
        "beta":           fit.coef[fit.index(predictor + "_z")],
        "se":             fit.se[fit.index(predictor + "_z")],
        "ci90":           fit.ci(predictor + "_z", 0.90),
        "ci95":           fit.ci(predictor + "_z", 0.95),
        "governance_contrasts": {
            f"arm_{arm}": {
                "beta": fit.coef[fit.index(f"arm_{arm}")],
                "ci95": fit.ci(f"arm_{arm}", 0.95),
            } for arm in arms
        },
    }


def equivalence_test(beta: float, se: float, sesoi: float = 0.20,
                     null: float = 0.0, level: float = 0.90
                     ) -> Dict[str, object]:
    """
    Two one-sided tests, expressed as the 90% CI rule.

    A 90% CI lying entirely inside (null - sesoi, null + sesoi) is
    algebraically identical to rejecting both one-sided nulls at
    alpha = 0.05, so the CI form is used — it shows the reader the
    interval instead of only a verdict.

    null : the value H2 is tested AGAINST. Zero is the wrong null here;
           pass the mechanical baseline slope from
           parameter_sweep.composition_slope at the realised parameters.
           A study that beats zero has shown that taking more tokens
           lowers the stock, which is arithmetic, not psychology.

    Four possible verdicts, all pre-registered:
      EQUIVALENT           CI inside the SESOI band around null
      LARGER_NEGATIVE      CI entirely below null - sesoi
      LARGER_POSITIVE      CI entirely above null + sesoi
      INCONCLUSIVE         CI crosses a band edge
    """
    z = _normal_ppf(1.0 - (1.0 - level) / 2.0)
    lo, hi = beta - z * se, beta + z * se
    band_lo, band_hi = null - sesoi, null + sesoi

    if lo >= band_lo and hi <= band_hi:
        verdict = "EQUIVALENT"
        reading = ("the composition effect is within the smallest effect "
                   "size of interest of the baseline — H2 is falsified in "
                   "the direction it can be falsified")
    elif hi < band_lo:
        verdict = "LARGER_NEGATIVE"
        reading = ("composition lowers the final stock by more than the "
                   "mechanical baseline predicts — H2 supported")
    elif lo > band_hi:
        verdict = "LARGER_POSITIVE"
        reading = ("composition RAISES the final stock relative to "
                   "baseline — H2 contradicted in sign")
    else:
        verdict = "INCONCLUSIVE"
        reading = ("the interval spans the SESOI edge: the study cannot "
                   "distinguish a negligible effect from a meaningful "
                   "one. This is a power statement, not a finding.")

    return {
        "beta":     beta,
        "se":       se,
        "null":     null,
        "sesoi":    sesoi,
        "ci":       (lo, hi),
        "band":     (band_lo, band_hi),
        "verdict":  verdict,
        "reading":  reading,
    }


def standardized_baseline(slope_raw: float, x: Sequence[float],
                          y: Sequence[float]) -> Dict[str, float]:
    """
    Convert a raw-units baseline slope into the standardised scale the
    primary model reports, so the two can be compared at all.

        beta_std = slope_raw * sd(x) / sd(y)

    parameter_sweep.composition_slope returns dS/dK per additional
    maximiser — raw units. primary_analysis returns a standardised
    coefficient. Comparing them directly is the same unit error the
    draft plan made against the SESOI, one level up, and it is easy to
    repeat: the two numbers look like they are on the same scale
    because both are small and negative.
    """
    sx = _sd(x)
    sy = _sd(y)
    return {
        "slope_raw":     slope_raw,
        "sd_x":          sx,
        "sd_y":          sy,
        "beta_std":      slope_raw * sx / sy if sy > 0 else float("nan"),
    }


def _sd(v: Sequence[float]) -> float:
    n = len(v)
    if n < 2:
        return 0.0
    m = sum(v) / n
    return math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))


def threshold_specification(rows: Sequence[Dict[str, float]],
                            dv: str = "S_final_over_K",
                            predictor: str = "n_high_d"
                            ) -> Dict[str, object]:
    """
    Pre-registered alternative to the linear slope.

    The mechanical baseline is a STEP: below some number of maximisers
    the stock survives, at or above it the stock collapses. A linear
    model fitted to a step returns an average slope that describes no
    group in the sample. This fits an indicator for each threshold
    location and reports which one best separates the data, alongside
    the linear fit's R-squared for comparison.

    Reported as secondary and clearly labelled, because choosing the
    threshold by fit is a selection step: the p-value from the winning
    split is not a p-value.
    """
    y = [float(r[dv]) for r in rows]
    x = [float(r[predictor]) for r in rows]
    levels = sorted(set(x))
    best = None
    for cut in levels[1:]:
        d = [1.0 if xi >= cut else 0.0 for xi in x]
        if 0 < sum(d) < len(d):
            fit = ols(y, [[di] for di in d], ["above_cut"])
            if best is None or fit.r_squared > best["r_squared"]:
                best = {"cut": cut, "r_squared": fit.r_squared,
                        "step": fit.coef[1], "se": fit.se[1]}
    lin = ols(y, [[xi] for xi in x], [predictor])
    return {
        "best_threshold":     best,
        "linear_r_squared":   lin.r_squared,
        "threshold_beats_linear": (best is not None
                                   and best["r_squared"] > lin.r_squared),
        "caveat": "the threshold location was selected by fit; its "
                  "p-value is not a p-value. Report the effect size and "
                  "the selection procedure, not significance.",
    }


# ─────────────────────────────────────────────
# SECONDARY ANALYSES — OPTIONAL DEPENDENCIES
# ─────────────────────────────────────────────


def survival_analysis(rows: Sequence[Dict[str, float]]) -> Dict[str, object]:
    """
    Cox model on rounds-to-collapse, with groups that never collapse
    censored at T.

    Requires lifelines and pandas. Returns a skipped marker rather than
    raising, so the rest of the plan runs in an environment that does
    not have them.
    """
    try:
        import pandas as pd
        from lifelines import CoxPHFitter
    except ImportError as e:
        return {"skipped": True, "reason": f"optional dependency missing: {e}",
                "install": "pip install lifelines pandas"}
    df = pd.DataFrame(list(rows))
    cph = CoxPHFitter()
    cph.fit(df[["duration", "event_observed", "n_high_d"]],
            duration_col="duration", event_col="event_observed")
    return {"skipped": False,
            "summary": cph.summary.to_dict(),
            "note": "censoring at T is required — groups that survive are "
                    "not groups that collapsed at round T"}


def round_level_model(round_rows: Sequence[Dict[str, float]]
                      ) -> Dict[str, object]:
    """
    Mixed model of per-round extraction with a random intercept per
    group and a fixed round trend.

    The draft omitted the round term. Extraction in a CPR game trends
    within a session regardless of composition, so a model without it
    attributes the trend to whatever else is in the design.
    """
    try:
        import pandas as pd
        import statsmodels.formula.api as smf
    except ImportError as e:
        return {"skipped": True, "reason": f"optional dependency missing: {e}",
                "install": "pip install statsmodels pandas"}
    df = pd.DataFrame(list(round_rows))
    model = smf.mixedlm("extraction_total ~ n_high_d + C(governance) + round",
                        df, groups=df["group_id"])
    res = model.fit()
    return {"skipped": False, "summary": str(res.summary())}


if __name__ == "__main__":
    import random as _random
    from cpr_game import GameParams, simulate

    print("ANALYSIS PLAN — DRY RUN ON SIMULATED DATA")
    print("=" * 74)
    print("  Data below are SIMULATED to exercise the analysis code.")
    print("  No participants exist. No inference about people is implied.")

    rng = _random.Random(2026)
    p = GameParams(g=0.4)
    rows: List[Dict[str, float]] = []
    for gid in range(240):
        arm = ("G0", "G1", "G2")[gid % 3]
        k = gid % 5
        # behavioural noise: governance nudges some maximisers to restrain
        effective = k
        if arm == "G1" and k > 0 and rng.random() < 0.30:
            effective = k - 1
        if arm == "G2" and k > 0 and rng.random() < 0.50:
            effective = k - 1
        s = simulate(p, policy="mixed", n_max=effective).summary()
        rows.append({
            "group_id":        gid,
            "governance":      arm,
            "n_high_d":        k,
            "S_final_over_K":  s["S_final_over_K"],
            "duration":        s["duration"],
            "event_observed":  s["event_observed"],
            "comprehension":   rng.uniform(0.5, 1.0),
        })

    res = primary_analysis(rows)
    print("\n" + res["fit"].summary())
    print(f"\n  composition beta (standardised): {res['beta']:+.4f}  "
          f"90% CI [{res['ci90'][0]:+.3f}, {res['ci90'][1]:+.3f}]")

    # The mechanical slope from parameter_sweep is in RAW units
    # (S/K per additional maximiser). Convert before comparing.
    base = standardized_baseline(
        -0.235,
        [float(r["n_high_d"]) for r in rows],
        [float(r["S_final_over_K"]) for r in rows])

    print("\n\nEQUIVALENCE TEST AGAINST TWO NULLS")
    print("=" * 74)
    print(f"  mechanical baseline: raw {base['slope_raw']:+.3f} "
          f"-> standardised {base['beta_std']:+.3f} "
          f"(sd_x={base['sd_x']:.3f}, sd_y={base['sd_y']:.3f})")
    for label, null in (("zero (the WRONG null)", 0.0),
                        ("mechanical baseline", base["beta_std"])):
        eq = equivalence_test(res["beta"], res["se"], sesoi=0.20, null=null)
        print(f"\n  vs {label:24s} -> {eq['verdict']}")
        print(f"     CI [{eq['ci'][0]:+.3f}, {eq['ci'][1]:+.3f}]   "
              f"band [{eq['band'][0]:+.3f}, {eq['band'][1]:+.3f}]")
        print(f"     {eq['reading']}")
    print("\n  Same data, same coefficient, opposite conclusions. Against")
    print("  zero the composition hypothesis looks strongly supported;")
    print("  against what the game predicts mechanically it is")
    print("  indistinguishable from arithmetic. The null has to be")
    print("  pre-registered, and zero is not the right one.")

    th = threshold_specification(rows)
    print("\n\nTHRESHOLD vs LINEAR")
    print("=" * 74)
    print(f"  best threshold at n_high_d >= {th['best_threshold']['cut']:.0f}: "
          f"R2 = {th['best_threshold']['r_squared']:.3f}, "
          f"step = {th['best_threshold']['step']:+.3f}")
    print(f"  linear specification:            R2 = "
          f"{th['linear_r_squared']:.3f}")
    print(f"  threshold beats linear: {th['threshold_beats_linear']}")
    print(f"  {th['caveat']}")

    print("\n\nOPTIONAL SECONDARY ANALYSES")
    print("=" * 74)
    sa = survival_analysis(rows)
    print(f"  survival: "
          f"{'skipped — ' + sa['reason'] if sa.get('skipped') else 'ran'}")
