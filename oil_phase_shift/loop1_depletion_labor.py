"""
loop1_depletion_labor.py
CC0 — JinnZ2 / oil_phase_shift

Feedback loop 1: depletion -> more wells needed -> more labor needed ->
labor unavailable -> fewer wells drilled -> production drops faster than
depletion curve predicted.

Substrate:
- Permian base decline ~40%/yr (was 34% in 2018)
- API: stop drilling -> -37% by yr1, -60% by yr2
- Tier-1 inventory ~3.7yr at current rate (60% drilled)
- Labor pool shrinking from 3 stacked causes:
    immigration enforcement, water/health hazard, 20hr-shift exhaustion

Loop is amplifying when:
  d(wells_needed)/dt > d(labor_capacity)/dt
"""

import random
from dataclasses import dataclass


@dataclass
class L1State:
    base_decline_rate: float        # fraction/yr (0.40 baseline)
    tier1_remaining_yr: float       # premium inventory remaining
    labor_capacity: float           # 1.0 = baseline workforce
    wells_drilled_per_yr: int
    production_bbl_per_day: float
    year: int = 0


def labor_loss_rate(state: L1State, rng: random.Random) -> float:
    """
    Three stacked drivers of labor exodus.
    Each one independent draw, additive (not multiplicative)
    because each driver removes a distinct subset of workers.
    """
    immigration_loss = rng.uniform(0.02, 0.06)   # 2-6%/yr
    health_exit       = rng.uniform(0.01, 0.04)   # workers leaving over water/health
    burnout_exit      = rng.uniform(0.02, 0.05)   # 20hr-shift attrition
    return immigration_loss + health_exit + burnout_exit


def wells_required_to_hold_flat(state: L1State) -> int:
    """
    To offset base decline you need replacement production each year.
    Assumes new well productivity ~ 50% of legacy (Goldman 2025-26).
    """
    decline_volume = state.production_bbl_per_day * state.base_decline_rate
    new_well_avg_contribution = 90.0  # bbl/day avg over yr1 after IP fall-off
    return int(decline_volume / new_well_avg_contribution)


def wells_actually_drilled(state: L1State, required: int) -> int:
    """
    Actual drilling capped by labor capacity.
    Below 1.0 capacity, you can't drill what depletion demands.
    """
    return int(required * state.labor_capacity)


def step(state: L1State, rng: random.Random) -> L1State:
    # 1. labor erodes
    new_labor = state.labor_capacity * (1.0 - labor_loss_rate(state, rng))

    # 2. depletion accelerates as you push into Tier-2/3
    tier_pressure = max(0.0, 1.0 - state.tier1_remaining_yr / 3.7)
    decline_acceleration = 0.005 + tier_pressure * 0.015  # 0.5-2%/yr
    new_decline = min(0.55, state.base_decline_rate + decline_acceleration)

    # 3. wells needed vs drilled
    needed = wells_required_to_hold_flat(state)
    drilled = wells_actually_drilled(state, needed)
    drilling_gap = max(0, needed - drilled)

    # 4. production updates: legacy decline + actual new contribution
    legacy_loss = state.production_bbl_per_day * new_decline
    new_contribution = drilled * 90.0
    new_production = max(0.0, state.production_bbl_per_day - legacy_loss + new_contribution)

    # 5. tier-1 inventory burns proportional to drilling
    inventory_burn = drilled / 5500.0  # ~5500 wells/yr exhausts ~1yr inventory
    new_tier1 = max(0.0, state.tier1_remaining_yr - inventory_burn)

    return L1State(
        base_decline_rate=new_decline,
        tier1_remaining_yr=new_tier1,
        labor_capacity=new_labor,
        wells_drilled_per_yr=drilled,
        production_bbl_per_day=new_production,
        year=state.year + 1,
    )


def run(years: int = 10, seed: int | None = None) -> list[L1State]:
    rng = random.Random(seed)
    state = L1State(
        base_decline_rate=0.40,
        tier1_remaining_yr=3.7,
        labor_capacity=1.0,
        wells_drilled_per_yr=5500,
        production_bbl_per_day=13_500_000.0,
    )
    history = [state]
    for _ in range(years):
        state = step(state, rng)
        history.append(state)
    return history


def amplifying(history: list[L1State]) -> bool:
    """Loop is amplifying if production drops faster than baseline decline."""
    if len(history) < 3:
        return False
    p0 = history[0].production_bbl_per_day
    p_end = history[-1].production_bbl_per_day
    yrs = history[-1].year
    realized_decline = 1.0 - (p_end / p0) ** (1 / yrs)
    return realized_decline > history[0].base_decline_rate * 1.1


if __name__ == "__main__":
    h = run(years=10, seed=42)
    for s in h:
        print(f"yr{s.year:2d} prod={s.production_bbl_per_day/1e6:5.2f}Mb/d "
              f"labor={s.labor_capacity:.2f} decline={s.base_decline_rate:.3f} "
              f"tier1={s.tier1_remaining_yr:.2f}yr drilled={s.wells_drilled_per_yr}")
    print(f"amplifying: {amplifying(h)}")
