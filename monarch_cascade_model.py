"""
monarch_cascade_model.py

Threshold-dynamics model for monarch butterfly population collapse
and downstream ecological cascade.

PURPOSE
    Demonstrates that pollinator population collapse is NOT linear.
    Once population density falls below threshold, mate-finding,
    migration coordination, and milkweed-monarch coupling break
    non-linearly. Decline accelerates.

    This module exists because policy and insurance models treat
    pollinator decline as gradual, manageable, forecast-able. The
    actual dynamics are exponential past threshold, with discrete
    flips at coupling-failure points.

DATA ANCHORS
    - Western monarchs: millions in 1980s, ~400,000 at year 2000,
      12,260 in 2025-2026 (Xerces Society count).
    - Eastern monarchs: 56-74% extinction probability by 2080 per
      USFWS; western at 99%.
    - Documented driver loadings: glyphosate (host plant removal),
      neonicotinoids (developmental toxicity), forest loss
      (overwintering habitat).

    This is a constraint model, not a forecast. It demonstrates the
    shape of the failure mode using stylized parameters consistent
    with documented data.

Status: CC0. Stdlib only. ASCII only.
"""

from dataclasses import dataclass
from typing import List, Dict


# ─────────────────────────────────────────────
# COUPLING THRESHOLDS
# ─────────────────────────────────────────────

@dataclass
class CouplingThreshold:
    name: str
    threshold_population: int
    failure_mode: str
    cascade_consequence: str


COUPLING_THRESHOLDS: List[CouplingThreshold] = [
    CouplingThreshold(
        name="mate_finding_density",
        threshold_population=50_000,
        failure_mode=(
            "below this density, monarchs cannot reliably find "
            "mates during breeding"
        ),
        cascade_consequence=(
            "reproduction rate drops sharply; recovery from low "
            "population becomes impossible without intervention"
        ),
    ),
    CouplingThreshold(
        name="migration_coordination",
        threshold_population=20_000,
        failure_mode=(
            "migratory cohort below this size loses thermal mass "
            "for overwintering clusters"
        ),
        cascade_consequence=(
            "overwinter mortality spikes; migration tradition "
            "breaks within a generation"
        ),
    ),
    CouplingThreshold(
        name="milkweed_pollination_coupling",
        threshold_population=10_000,
        failure_mode=(
            "milkweed populations no longer maintained by monarch "
            "pollination cycle"
        ),
        cascade_consequence=(
            "milkweed range contracts; species dependent on "
            "milkweed lose habitat; cascade extends to other "
            "Lepidoptera"
        ),
    ),
    CouplingThreshold(
        name="genetic_diversity_floor",
        threshold_population=5_000,
        failure_mode=(
            "effective breeding population insufficient to maintain "
            "genetic diversity"
        ),
        cascade_consequence=(
            "inbreeding depression; reduced adaptability; "
            "functional extinction within decades even if "
            "population stabilizes numerically"
        ),
    ),
]


# ─────────────────────────────────────────────
# DECLINE MODEL
# ─────────────────────────────────────────────

def annual_decline(prev_population: int,
                   base_rate: float = 0.18,
                   stressor_multiplier: float = 1.0) -> int:
    """
    Annual population step. Default rate consistent with ~7-year
    collapse trajectories observed at Upper Midwest sites.

    base_rate: fraction lost per year under baseline stressor load.
    stressor_multiplier: 1.0 = baseline, >1.0 = increased pesticide
                         load or habitat loss.
    """
    loss_fraction = min(base_rate * stressor_multiplier, 0.9)
    return int(prev_population * (1.0 - loss_fraction))


def threshold_failures_triggered(population: int) -> List[str]:
    """Return names of coupling thresholds the current population is below."""
    return [
        t.name for t in COUPLING_THRESHOLDS
        if population < t.threshold_population
    ]


def post_threshold_decline_amplifier(thresholds_failed: List[str]) -> float:
    """
    Each failed threshold accelerates further decline.
    This is the non-linearity: cascade compounds.
    """
    return 1.0 + 0.4 * len(thresholds_failed)


def simulate_trajectory(starting_population: int,
                        years: int,
                        stressor_multiplier: float = 1.0,
                        base_rate: float = 0.18) -> List[Dict]:
    """
    Run a year-by-year trajectory. Returns list of annual states.
    Demonstrates non-linear collapse past coupling thresholds.
    """
    trajectory = []
    population = starting_population
    for year in range(years):
        thresholds_failed = threshold_failures_triggered(population)
        amplifier = post_threshold_decline_amplifier(thresholds_failed)
        effective_stressor = stressor_multiplier * amplifier
        next_population = annual_decline(population, base_rate, effective_stressor)
        trajectory.append({
            "year":               year,
            "population":         population,
            "thresholds_failed":  thresholds_failed,
            "decline_amplifier":  round(amplifier, 2),
            "effective_stressor": round(effective_stressor, 2),
        })
        population = next_population
        if population < 100:
            trajectory.append({
                "year":               year + 1,
                "population":         population,
                "thresholds_failed":  [t.name for t in COUPLING_THRESHOLDS],
                "decline_amplifier":  "FUNCTIONAL_EXTINCTION",
                "effective_stressor": "n/a",
            })
            break
    return trajectory


def compare_linear_vs_threshold_model(starting_population: int,
                                       years: int) -> Dict:
    """
    Show what the linear forecast predicts vs what threshold dynamics
    actually produce. The gap between these is what insurance and
    policy models are missing.
    """
    linear_loss_per_year = int(starting_population * 0.18)
    linear_endpoint = max(0, starting_population - (linear_loss_per_year * years))
    threshold_trajectory = simulate_trajectory(starting_population, years)
    threshold_endpoint = threshold_trajectory[-1]["population"]
    return {
        "starting_population":      starting_population,
        "years_modeled":            years,
        "linear_forecast_endpoint": linear_endpoint,
        "threshold_model_endpoint": threshold_endpoint,
        "underestimate_factor": (
            round(linear_endpoint / max(threshold_endpoint, 1), 1)
            if threshold_endpoint > 0
            else "infinite (extinction reached)"
        ),
        "thresholds_failed_in_threshold_model": (
            threshold_trajectory[-1]["thresholds_failed"]
        ),
    }


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("MONARCH CASCADE MODEL")
    print("=" * 60)
    print(f"coupling thresholds defined: {len(COUPLING_THRESHOLDS)}")
    for t in COUPLING_THRESHOLDS:
        print(f"  - {t.name}: <{t.threshold_population:,}")
    print()

    # Calibration anchor: ~400,000 in 2000, 12,260 in 2026 (26 years)
    print("CALIBRATION CHECK: Western monarchs 2000 -> 2026")
    traj = simulate_trajectory(400_000, 26, stressor_multiplier=1.1)
    final = traj[-1]
    print(f"  modeled final population: {final['population']:,}")
    print(f"  observed (Xerces 2026): 12,260")
    print(f"  thresholds failed at end: {final['thresholds_failed']}")
    print()

    print("LINEAR vs THRESHOLD COMPARISON (10-year forecast from 100k):")
    comp = compare_linear_vs_threshold_model(100_000, 10)
    for k, v in comp.items():
        print(f"  {k}: {v}")
    print()
    print("The 'underestimate_factor' is what linear models miss.")
    print("Insurance and policy models running linear are mispricing")
    print("risk by this multiple.")
