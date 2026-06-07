# narrative_crossval.py  -- CC0, stdlib-only
#
# FALSIFIER for EVT-01 and NAR-01.
#
# The test: do the predicted high-probability windows (from coupled_model)
# cluster around independently-dated flood / island-subsidence narratives
# BETTER than:
#   (a) a fast-forcing-only NULL model (alpha=0), AND
#   (b) a Monte-Carlo shuffle null (random narrative placement)?
#
# As shipped the NARRATIVES list contains PLACEHOLDER entries only.  The
# falsifier returns NOT_SUPPORTED, which is the correct answer for placeholder
# data.  To test against the world, replace NARRATIVES with real, independently
# dated entries (sediment cores, drowned-shoreline dates, oral-tradition
# chronologies with documented provenance) and re-run.  Let the data speak.
#
# Time convention: t in years BEFORE PRESENT (BP), t >= 0.

import math
import random

from coupled_model import run as run_model, _find_peaks

# ── NARRATIVE DATA ────────────────────────────────────────────────────────────
#
# Each entry: {"t_bp": int, "location": str, "tradition": str, "source": str}
#
# PLACEHOLDER data — synthetic, evenly spaced.
# Insufficient to trigger SUPPORTED under any test (n < MIN_FOR_TEST).
# Replace with real dated entries to test the model against the world.

NARRATIVES = [
    {"t_bp": 12000, "location": "PLACEHOLDER", "tradition": "PLACEHOLDER",
     "source": "synthetic_test_only"},
    {"t_bp": 37500, "location": "PLACEHOLDER", "tradition": "PLACEHOLDER",
     "source": "synthetic_test_only"},
    {"t_bp": 75000, "location": "PLACEHOLDER", "tradition": "PLACEHOLDER",
     "source": "synthetic_test_only"},
    {"t_bp": 112500, "location": "PLACEHOLDER", "tradition": "PLACEHOLDER",
     "source": "synthetic_test_only"},
]

# Parameters
MATCH_WINDOW_YR     = 5000    # ±window around each narrative (yr)
N_MC_TRIALS         = 1000    # Monte Carlo shuffle iterations
T_RANGE_BP          = (0, 150000)   # simulation window
MIN_FOR_TEST        = 10      # minimum real narratives to attempt EVT-01
MC_SEED             = 42


def _peak_times(result: dict) -> list:
    """Extract t_bp values from run() peaks list."""
    return [t for t, _p in result["peaks"]]


def hit_count(narrative_times: list, peak_times: list,
              window_yr: int = MATCH_WINDOW_YR) -> int:
    """
    Count narratives that have at least one peak within ±window_yr.
    """
    hits = 0
    for t_nar in narrative_times:
        for t_peak in peak_times:
            if abs(t_nar - t_peak) <= window_yr:
                hits += 1
                break
    return hits


def hit_rate(narrative_times: list, peak_times: list,
             window_yr: int = MATCH_WINDOW_YR) -> float:
    """Hit fraction in [0, 1]."""
    if not narrative_times:
        return 0.0
    return hit_count(narrative_times, peak_times, window_yr) / len(narrative_times)


def monte_carlo_null(peak_times: list,
                     n_narratives: int,
                     n_trials: int = N_MC_TRIALS,
                     t_range: tuple = T_RANGE_BP,
                     window_yr: int = MATCH_WINDOW_YR,
                     seed: int = MC_SEED) -> dict:
    """
    Shuffle null: randomly place n_narratives dates n_trials times.
    Returns {"mean": float, "p95": float, "p99": float, "all_rates": list}.
    """
    rng = random.Random(seed)
    lo, hi = t_range
    rates = []
    for _ in range(n_trials):
        fake = [rng.randint(lo, hi) for _ in range(n_narratives)]
        rates.append(hit_rate(fake, peak_times, window_yr))
    rates.sort()
    n = len(rates)
    return {
        "mean": sum(rates) / n,
        "p95":  rates[int(0.95 * n)],
        "p99":  rates[int(0.99 * n)],
        "all_rates": rates,
    }


def run_falsification(narratives: list = None,
                      alpha: float = 0.6,
                      verbose: bool = False) -> dict:
    """
    Run EVT-01 and NAR-01 falsification.

    Returns a dict containing:
      verdict         "SUPPORTED" or "NOT_SUPPORTED"
      reason          plain-text explanation
      hit_rate_full   hit rate of alpha>0 model
      hit_rate_null   hit rate of alpha=0 model
      mc_p95          95th percentile of shuffle null
      n_narratives    number of narrative entries used
      n_peaks_full    number of predicted peaks (full model)
      n_peaks_null    number of predicted peaks (null model)
    """
    if narratives is None:
        narratives = NARRATIVES

    n = len(narratives)

    # Always run both models (used for reporting even if n < MIN_FOR_TEST)
    result_full = run_model(alpha=alpha)
    result_null = run_model(alpha=0.0)

    peaks_full = _peak_times(result_full)
    peaks_null = _peak_times(result_null)

    nar_times = [entry["t_bp"] for entry in narratives]

    hr_full = hit_rate(nar_times, peaks_full)
    hr_null = hit_rate(nar_times, peaks_null)

    mc = monte_carlo_null(peaks_full, n_narratives=max(1, n))
    mc_p95 = mc["p95"]
    mc_mean = mc["mean"]

    # EVT-01 requires BOTH conditions to claim SUPPORTED:
    #   1. full model beats alpha=0 null (deep water actually changes the prediction)
    #   2. full model beats random placement null (correlation is not accidental)
    # Additionally requires a minimum sample size to have any statistical power.
    if n < MIN_FOR_TEST:
        verdict = "NOT_SUPPORTED"
        reason = (f"insufficient data: {n} narrative entries, "
                  f"{MIN_FOR_TEST} required for EVT-01 test. "
                  f"Replace PLACEHOLDER entries with real dated narratives.")
    elif hr_full > hr_null and hr_full > mc_p95:
        verdict = "SUPPORTED"
        reason = (f"hit_rate_full={hr_full:.3f} beats alpha=0 null "
                  f"({hr_null:.3f}) and shuffle p95 ({mc_p95:.3f}).")
    else:
        verdict = "NOT_SUPPORTED"
        parts = []
        if hr_full <= hr_null:
            parts.append(f"deep baseline does not improve over fast-only model "
                         f"({hr_full:.3f} <= {hr_null:.3f})")
        if hr_full <= mc_p95:
            parts.append(f"hit_rate ({hr_full:.3f}) does not exceed "
                         f"shuffle p95 ({mc_p95:.3f})")
        reason = "; ".join(parts) if parts else "conditions not met"

    result = {
        "verdict":        verdict,
        "reason":         reason,
        "hit_rate_full":  hr_full,
        "hit_rate_null":  hr_null,
        "mc_p95":         mc_p95,
        "mc_mean":        mc_mean,
        "n_narratives":   n,
        "n_peaks_full":   len(peaks_full),
        "n_peaks_null":   len(peaks_null),
        "s_base":         result_full["s_base"],
        "alpha":          alpha,
    }

    if verbose:
        print("=== EVT-01 / NAR-01 FALSIFICATION ===\n")
        for k, v in result.items():
            print(f"  {k:<20} = {v}")

    return result


if __name__ == "__main__":
    result = run_falsification(verbose=True)
    print(f"\nVERDICT: {result['verdict']}")
    print(f"REASON:  {result['reason']}")
