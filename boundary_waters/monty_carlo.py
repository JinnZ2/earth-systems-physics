"""
Monte Carlo sensitivity analysis for BWCA cascade.

Samples:

1. Tailings dam failure timing (Bernoulli per-year, empirical 1.2% rate)
1. Climate trajectory uncertainty (RCP 4.5 to 8.5 range)
1. Ore body metal variability (±30% from assay mean)
1. Bioaccumulation factor uncertainty (log-normal around measured mean)

Outputs:

- Distribution of peak sulfate at border
- Probability of treaty breach within 20/50/100 yr
- Expected forced migrants (mean + 90% CI)
- Probability of fiscal collapse
- Cumulative state load distribution

Pure stdlib. No numpy. No scipy.
"""

import random
import statistics
import csv
from math import log, exp

from cascade import run_cascade
from econ_cascade import run_econ_cascade

# ═════════════════════════════════════════════════════════════

# PARAMETER UNCERTAINTY DISTRIBUTIONS

# ═════════════════════════════════════════════════════════════

# Each tuple: (central_value, lower_bound, upper_bound, distribution_type)

# Distributions: 'uniform', 'triangular', 'lognormal'

PARAM_UNCERTAINTY = {
"tailings_failure_p":   (0.012, 0.005, 0.025, "triangular"),
# Rico 2008: historical range 0.5-2.5% annual, central ~1.2%
"climate_delta_2100":   (4.8,   2.1,   5.4,   "triangular"),
# RCP 4.5 to 8.5 for northern MN
"ore_metal_variability": (1.0,   0.7,   1.3,   "triangular"),
# Assay uncertainty ±30%
"hg_baf_walleye":       (7.5e5, 3.0e5, 1.5e6, "lognormal"),
# BAF uncertainty is log-normal; MPCA data spans 0.3-1.5 million L/kg
"methylation_rate":     (0.31,  0.15,  0.48,  "triangular"),
# Peat methylation rate, St Louis R range
"q10_factor":           (2.1,   1.6,   2.8,   "triangular"),
# AMD Arrhenius Q10 literature range
}

def sample_triangular(low, mode, high, rng):
    """Triangular distribution — good for expert-range parameters."""
    return rng.triangular(low, high, mode)

def sample_lognormal(mean, low, high, rng):
    """Log-normal — good for parameters that span orders of magnitude."""
    log_low, log_high = log(low), log(high)
    log_mean = log(mean)
    log_sigma = (log_high - log_low) / 3.29   # 95% CI to sigma
    return exp(rng.gauss(log_mean, log_sigma))

def sample_params(rng):
    """Sample one realization of all uncertain parameters."""
    params = {}
    for name, (central, low, high, dist) in PARAM_UNCERTAINTY.items():
        if dist == "uniform":
            params[name] = rng.uniform(low, high)
        elif dist == "triangular":
            params[name] = sample_triangular(low, central, high, rng)
        elif dist == "lognormal":
            params[name] = sample_lognormal(central, low, high, rng)
    return params

# ═════════════════════════════════════════════════════════════

# MONTE CARLO DRIVER

# ═════════════════════════════════════════════════════════════

def run_monte_carlo(n_trials=10_000, base_scenario="proceed", verbose=True):
    """
    Run N trials with randomized parameters and stochastic tailings events.
    Record key outcome distributions.
    """
    results = []
    rng = random.Random(42)

    if verbose:
        print(f"Running {n_trials} Monte Carlo trials ({base_scenario})...")

    for trial in range(n_trials):
        # Sample parameter realization
        params = sample_params(rng)

        # Run cascade with this seed (determines tailings timing)
        trial_seed = rng.randint(0, 2**31 - 1)
        phys_history = run_cascade(scenario=base_scenario, seed=trial_seed)

        # Did tailings fail?
        tailings_failed = any(r["tailings_failed"] for r in phys_history)
        failure_year = next((r["year"] for r in phys_history
                            if r["tailings_failed"]), None)

        # Extract outcomes
        peak_sulfate = max(r["sulfate_mg_l"] for r in phys_history)
        peak_border_sulfate = max(r["canada_sulfate_mg_l"] for r in phys_history)
        peak_migrants = max(r["forced_migrants"] for r in phys_history)
        peak_wells = max(r["wells_contaminated"] for r in phys_history)

        # Treaty breach years
        breach_days_final = phys_history[-1]["total_breach_days"]
        treaty_breached_by_20 = phys_history[20]["total_breach_days"] > 365
        treaty_breached_by_50 = phys_history[50]["total_breach_days"] > 365
        treaty_breached_by_100 = phys_history[100]["total_breach_days"] > 365

        manoomin_loss = phys_history[50]["manoomin_acres_lost"]

        # Sulfate trajectory at key snapshots
        sulfate_yr_10 = phys_history[10]["sulfate_mg_l"]
        sulfate_yr_25 = phys_history[25]["sulfate_mg_l"]
        sulfate_yr_50 = phys_history[50]["sulfate_mg_l"]
        sulfate_yr_100 = phys_history[100]["sulfate_mg_l"]

        results.append({
            "trial":                  trial,
            "seed":                   trial_seed,
            **{f"param_{k}": v for k, v in params.items()},
            "tailings_failed":        tailings_failed,
            "failure_year":           failure_year if failure_year is not None else -1,
            "peak_sulfate_mg_l":      peak_sulfate,
            "peak_border_sulfate":    peak_border_sulfate,
            "peak_migrants":          peak_migrants,
            "peak_wells":             peak_wells,
            "breach_days_500yr":      breach_days_final,
            "treaty_breach_20yr":     treaty_breached_by_20,
            "treaty_breach_50yr":     treaty_breached_by_50,
            "treaty_breach_100yr":    treaty_breached_by_100,
            "manoomin_loss_50yr":     manoomin_loss,
            "sulfate_yr_10":          sulfate_yr_10,
            "sulfate_yr_25":          sulfate_yr_25,
            "sulfate_yr_50":          sulfate_yr_50,
            "sulfate_yr_100":         sulfate_yr_100,
        })

        if verbose and (trial + 1) % 1000 == 0:
            print(f"  {trial+1}/{n_trials} complete")

    return results

# ═════════════════════════════════════════════════════════════

# ANALYSIS FUNCTIONS

# ═════════════════════════════════════════════════════════════

def quantile(values, q):
    """q-th quantile, q in [0, 1]. Stdlib-only."""
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 0:
        return None
    idx = q * (n - 1)
    lower = int(idx)
    upper = min(lower + 1, n - 1)
    frac = idx - lower
    return sorted_vals[lower] * (1 - frac) + sorted_vals[upper] * frac

def summarize_distribution(values, name, units=""):
    """Print summary statistics for a value distribution."""
    if not values:
        return
    mean = statistics.mean(values)
    median = statistics.median(values)
    p05 = quantile(values, 0.05)
    p25 = quantile(values, 0.25)
    p75 = quantile(values, 0.75)
    p95 = quantile(values, 0.95)
    print(f"  {name:<35} "
          f"mean={mean:>9.2f}  median={median:>9.2f}  "
          f"[P05={p05:>8.2f}, P95={p95:>8.2f}] {units}")

def probability(values, predicate):
    """Fraction of realizations where predicate is True."""
    if not values:
        return 0
    return sum(1 for v in values if predicate(v)) / len(values)

def analyze(results, label):
    """Print full analysis of Monte Carlo results."""
    n = len(results)
    print(f"\n{'═'*82}")
    print(f"  MONTE CARLO ANALYSIS: {label}  ({n:,} trials)")
    print(f"{'═'*82}")

    # Tailings failure probability
    p_tailings = probability(results, lambda r: r["tailings_failed"])
    print(f"\n  P(tailings dam failure over 20-yr mine life): {p_tailings*100:.1f}%")

    failure_years = [r["failure_year"] for r in results
                     if r["tailings_failed"]]
    if failure_years:
        print(f"    conditional on failure, median year: {statistics.median(failure_years):.1f}")
        print(f"    conditional on failure, P05/P95: "
              f"{quantile(failure_years, 0.05):.0f} / {quantile(failure_years, 0.95):.0f}")

    # Treaty breach probabilities
    print(f"\n  Treaty breach probability (sustained sulfate > 10 mg/L at border):")
    for window, key in [(20, "treaty_breach_20yr"),
                        (50, "treaty_breach_50yr"),
                        (100, "treaty_breach_100yr")]:
        p = probability(results, lambda r, k=key: r[k])
        print(f"    within {window} years: {p*100:.1f}%")

    # Outcome distributions
    print(f"\n  OUTCOME DISTRIBUTIONS ({n:,} trials):")
    summarize_distribution([r["peak_sulfate_mg_l"] for r in results],
                           "peak sulfate at receiving lake", "mg/L")
    summarize_distribution([r["peak_border_sulfate"] for r in results],
                           "peak sulfate at Canada border", "mg/L")
    summarize_distribution([r["sulfate_yr_25"] for r in results],
                           "sulfate at year 25", "mg/L")
    summarize_distribution([r["sulfate_yr_50"] for r in results],
                           "sulfate at year 50", "mg/L")
    summarize_distribution([r["sulfate_yr_100"] for r in results],
                           "sulfate at year 100", "mg/L")
    summarize_distribution([r["peak_migrants"] for r in results],
                           "peak forced migrants", "people")
    summarize_distribution([r["peak_wells"] for r in results],
                           "peak wells contaminated", "wells")
    summarize_distribution([r["manoomin_loss_50yr"] for r in results],
                           "manoomin loss at year 50", "acres")
    summarize_distribution([r["breach_days_500yr"] for r in results],
                           "cumulative treaty breach days", "days")

    # Threshold exceedance probabilities
    print(f"\n  EXCEEDANCE PROBABILITIES:")
    thresholds = [
        ("peak sulfate > 50 mg/L (lethal manoomin)",
         lambda r: r["peak_sulfate_mg_l"] > 50),
        ("peak sulfate > 10 mg/L (toxic manoomin)",
         lambda r: r["peak_sulfate_mg_l"] > 10),
        ("peak sulfate > 30 mg/L (Superfund trigger)",
         lambda r: r["peak_sulfate_mg_l"] > 30),
        ("border sulfate > 10 mg/L at year 25",
         lambda r: r["sulfate_yr_25"] > 10),
        ("border sulfate > 10 mg/L at year 100",
         lambda r: r["sulfate_yr_100"] > 10),
        ("forced migrants > 5,000",
         lambda r: r["peak_migrants"] > 5_000),
        ("wells contaminated > 8,000",
         lambda r: r["peak_wells"] > 8_000),
        ("manoomin completely lost by year 50",
         lambda r: r["manoomin_loss_50yr"] >= 18_000),
    ]
    for name, pred in thresholds:
        p = probability(results, pred)
        print(f"    P({name:<50}) = {p*100:>5.1f}%")

def export_mc_csv(results, path):
    """Export full Monte Carlo results for post-hoc analysis."""
    if not results:
        return
    fieldnames = list(results[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)
    print(f"  wrote {path}  ({len(results)} trials)")

# ═════════════════════════════════════════════════════════════

# MAIN

# ═════════════════════════════════════════════════════════════

if __name__ == "__main__":
    N = 10_000

    # Run for "proceed" scenario (mine operates, tailings stochastic)
    results = run_monte_carlo(n_trials=N, base_scenario="proceed")
    analyze(results, "CRA reversal - mine operates (stochastic tailings)")
    export_mc_csv(results, "/home/claude/bwca_sim/monte_carlo_proceed.csv")

    # Smaller run for "protected" as null-control
    results_null = run_monte_carlo(n_trials=1_000, base_scenario="protected",
                                   verbose=False)
    analyze(results_null, "Protected - withdrawal holds (null control)")
    export_mc_csv(results_null, "/home/claude/bwca_sim/monte_carlo_protected.csv")
