"""
loop3_refinery_config_trap.py
CC0 — JinnZ2 / oil_phase_shift

Feedback loop 3: light sweet glut -> refineries retooled to light ->
Permian depletes -> no flexibility back to heavy -> import dependency ->
geopolitical exposure -> price spike -> refineries can't process spike feedstock.

Substrate:
- 70% of US refining capacity nominally optimized for heavy crude
  (legacy hardware) but post-shale many units retooled for light sweet
- Switching back: 3-6 months/unit, capital cost $100M+ per refinery
- Margin gain required to justify: >$1/bbl (industry source)
- Venezuelan crude needs imported diluent (naphtha/condensate)
- Canadian heavy: stable but capacity-constrained, infrastructure-bound
- Mexican Maya: declining (Dos Bocas refinery taking domestic share)
- Light sweet from Permian: depleting on accelerating curve (loop 1)
- Strait of Hormuz already physically constrained
- Refinery design temp range exceeded in Gulf summers

Trap: configuration lock-in on a feedstock that's disappearing,
no economic path to reconfigure for heavy until light is gone,
by which time heavy supply is also constrained / geopolitically unstable.
"""

import random
from dataclasses import dataclass, field


@dataclass
class L3State:
    light_sweet_supply: float        # Mbbl/d available domestically
    heavy_processable_capacity: float # Mbbl/d, currently configured for heavy
    light_processable_capacity: float # Mbbl/d, currently configured for light
    diluent_availability: float      # 1.0 = full, 0 = none
    geopolitical_risk_index: float   # 0..1
    refinery_utilization: float      # fraction
    unprocessable_imbalance: float   # Mbbl/d that can't be matched
    year: int = 0
    config_switches_attempted: int = 0
    config_switches_completed: int = 0


def light_sweet_trajectory(state: L3State, rng: random.Random) -> float:
    """Pull from loop 1 logic: accelerating decline as Tier-1 burns."""
    decline = rng.uniform(0.05, 0.12)  # 5-12%/yr in this regime
    return state.light_sweet_supply * (1.0 - decline)


def diluent_supply_dynamics(state: L3State, rng: random.Random) -> float:
    """
    Diluent (naphtha, condensate) availability tracks light sweet
    supply (because light sweet IS a diluent source) AND geopolitical
    constraints on imports.
    """
    domestic_factor = state.light_sweet_supply / 8.0  # baseline ~8Mbbl/d
    geo_factor = 1.0 - state.geopolitical_risk_index * 0.6
    noise = rng.uniform(0.9, 1.05)
    return max(0.0, min(1.2, domestic_factor * geo_factor * noise))


def geopolitical_drift(state: L3State, rng: random.Random) -> float:
    """
    Risk index drifts up with chokepoint stress.
    Strait of Hormuz, Venezuela transition, sanctions regimes.
    """
    drift = rng.uniform(-0.02, 0.05)  # asymmetric, mostly up
    shock = rng.random() < 0.10
    if shock:
        drift += rng.uniform(0.10, 0.25)
    return max(0.0, min(1.0, state.geopolitical_risk_index + drift))


def attempt_reconfiguration(state: L3State, rng: random.Random) -> tuple[float, float, int, int]:
    """
    Refineries reconfigure heavy <- light only when margin signal exceeds
    threshold AND capital is available AND timeline is tolerable.
    With ongoing supply chain fracture, completion rate is low.
    """
    # Margin pressure rises as light sweet depletes
    margin_pressure = max(0.0, 1.0 - state.light_sweet_supply / 8.0)

    # Attempt rate scales with pressure
    attempts = int(margin_pressure * 8 + rng.uniform(0, 2))  # units/yr

    # Completion depends on supply chain (German steel etc.)
    # Assume 30-60% completion under current constraints
    completion_rate = rng.uniform(0.30, 0.60)
    completed = int(attempts * completion_rate)

    # Each completed switch moves 0.15 Mbbl/d capacity from light to heavy
    capacity_shift = completed * 0.15
    new_light_cap = max(0.5, state.light_processable_capacity - capacity_shift)
    new_heavy_cap = state.heavy_processable_capacity + capacity_shift

    return new_light_cap, new_heavy_cap, attempts, completed


def compute_imbalance(state: L3State) -> float:
    """
    Mismatch between configured capacity and available feedstock.
    Heavy imports gated by diluent availability and geopolitical access.
    """
    effective_heavy_supply = state.heavy_processable_capacity * state.diluent_availability * (
        1.0 - state.geopolitical_risk_index * 0.5
    )
    light_supply_processable = min(state.light_sweet_supply, state.light_processable_capacity)

    total_processable = effective_heavy_supply + light_supply_processable
    nominal_demand = 16.5  # Mbbl/d crude run

    return max(0.0, nominal_demand - total_processable)


def step(state: L3State, rng: random.Random) -> L3State:
    new_light_supply = light_sweet_trajectory(state, rng)
    new_geo = geopolitical_drift(state, rng)

    intermediate = L3State(
        light_sweet_supply=new_light_supply,
        heavy_processable_capacity=state.heavy_processable_capacity,
        light_processable_capacity=state.light_processable_capacity,
        diluent_availability=state.diluent_availability,
        geopolitical_risk_index=new_geo,
        refinery_utilization=state.refinery_utilization,
        unprocessable_imbalance=state.unprocessable_imbalance,
        year=state.year,
    )

    new_diluent = diluent_supply_dynamics(intermediate, rng)
    intermediate.diluent_availability = new_diluent

    new_light_cap, new_heavy_cap, attempts, completed = attempt_reconfiguration(intermediate, rng)
    intermediate.light_processable_capacity = new_light_cap
    intermediate.heavy_processable_capacity = new_heavy_cap

    imbalance = compute_imbalance(intermediate)
    # Utilization drops as imbalance grows
    util = max(0.5, 0.92 - imbalance * 0.04)

    return L3State(
        light_sweet_supply=new_light_supply,
        heavy_processable_capacity=new_heavy_cap,
        light_processable_capacity=new_light_cap,
        diluent_availability=new_diluent,
        geopolitical_risk_index=new_geo,
        refinery_utilization=util,
        unprocessable_imbalance=imbalance,
        year=state.year + 1,
        config_switches_attempted=state.config_switches_attempted + attempts,
        config_switches_completed=state.config_switches_completed + completed,
    )


def run(years: int = 10, seed: int | None = None) -> list[L3State]:
    rng = random.Random(seed)
    state = L3State(
        light_sweet_supply=8.0,
        heavy_processable_capacity=7.0,    # post-retooling, less than nominal 70%
        light_processable_capacity=9.5,
        diluent_availability=1.0,
        geopolitical_risk_index=0.35,      # already constrained at start
        refinery_utilization=0.89,
        unprocessable_imbalance=0.0,
    )
    history = [state]
    for _ in range(years):
        state = step(state, rng)
        history.append(state)
    return history


def trap_engaged(history: list[L3State]) -> bool:
    """Trap is engaged if imbalance > 1.5 Mbbl/d for >2 consecutive years."""
    if len(history) < 3:
        return False
    consecutive = 0
    for s in history:
        if s.unprocessable_imbalance > 1.5:
            consecutive += 1
            if consecutive >= 2:
                return True
        else:
            consecutive = 0
    return False


if __name__ == "__main__":
    h = run(years=10, seed=11)
    for s in h:
        print(f"yr{s.year:2d} light={s.light_sweet_supply:.2f} "
              f"capL={s.light_processable_capacity:.2f} capH={s.heavy_processable_capacity:.2f} "
              f"dil={s.diluent_availability:.2f} geo={s.geopolitical_risk_index:.2f} "
              f"util={s.refinery_utilization:.2f} imbal={s.unprocessable_imbalance:.2f}")
    print(f"trap engaged: {trap_engaged(h)}")
    print(f"switches attempted/completed: {h[-1].config_switches_attempted}/{h[-1].config_switches_completed}")
