"""
loop2_cost_cornercut_failure.py
CC0 — JinnZ2 / oil_phase_shift

Feedback loop 2: cost inflation -> corner-cutting -> infrastructure failure ->
contamination -> labor exodus -> cost inflation (loop closes).

Substrate:
- Specialty steel inflation, German source disruption
- Plastic/rubber/sulfur supply fragility
- Aluminum cost spikes
- Industry response: deferred maintenance, longer inspection intervals,
  thinner safety margins on equipment past design life
- Failure mode: fitting corrosion from NORM-laden produced water
  (radium-226/228, uranium, thorium) eats stainless from inside
- Contamination -> aquifer + surface water -> communities leave
- Labor cost rises (replacement labor must be imported, paid more)

Loop closes when each cycle's cost-cut savings < replacement/cleanup cost.
"""

import random
from dataclasses import dataclass


@dataclass
class L2State:
    material_cost_index: float       # 1.0 = 2020 baseline
    corner_cut_intensity: float      # 0..1, fraction of safety margin removed
    infrastructure_integrity: float  # 1.0 = fully maintained
    contamination_load: float        # arbitrary units, accumulating
    community_viability: float       # 1.0 = livable, 0 = abandoned
    labor_cost_multiplier: float     # 1.0 baseline
    year: int = 0


def material_inflation(rng: random.Random) -> float:
    """
    Annual material cost change. Skewed positive — supply chain
    fracture asymmetry. Steel/plastic/sulfur stacked.
    """
    # base inflation + supply shock probability
    base = rng.uniform(0.03, 0.08)
    shock = rng.random() < 0.25  # 25%/yr chance of supply shock
    if shock:
        base += rng.uniform(0.10, 0.30)
    return base


def corner_cut_response(state: L2State, rng: random.Random) -> float:
    """
    Higher costs push more corner-cutting.
    Bounded 0..0.85 — even worst operators keep some margin.
    """
    pressure = (state.material_cost_index - 1.0) * 0.3
    noise = rng.uniform(-0.02, 0.05)
    return max(0.0, min(0.85, state.corner_cut_intensity + pressure + noise))


def infrastructure_decay(state: L2State) -> float:
    """
    Decay rate depends on corner-cutting intensity.
    NORM corrosion is non-linear — pipes hold until they don't.
    """
    base_decay = 0.02  # 2%/yr with full maintenance
    cut_amplifier = 1.0 + state.corner_cut_intensity * 4.0
    return base_decay * cut_amplifier


def contamination_release(state: L2State, rng: random.Random) -> float:
    """
    Contamination from failures + open-air storage lake overflow.
    Heavy rain events trigger releases — Monte Carlo.
    """
    chronic = (1.0 - state.infrastructure_integrity) * 0.3
    overflow_event = rng.random() < 0.35  # ~1/3 yrs heavy enough
    acute = rng.uniform(0.5, 1.5) if overflow_event else 0.0
    return chronic + acute


def community_response(state: L2State) -> float:
    """
    Communities lose viability as contamination accumulates.
    Threshold-like: tolerance up to a point, then collapse.
    """
    if state.contamination_load < 2.0:
        loss = state.contamination_load * 0.02
    elif state.contamination_load < 5.0:
        loss = 0.05 + (state.contamination_load - 2.0) * 0.08
    else:
        loss = 0.30 + (state.contamination_load - 5.0) * 0.15
    return max(0.0, state.community_viability - loss)


def labor_cost_response(state: L2State) -> float:
    """
    As local communities collapse, labor must be imported / retained
    at premium. Multiplier rises inversely with viability.
    """
    if state.community_viability >= 0.7:
        return 1.0
    return 1.0 + (0.7 - state.community_viability) * 1.8


def step(state: L2State, rng: random.Random) -> L2State:
    new_cost = state.material_cost_index * (1.0 + material_inflation(rng))
    new_cuts = corner_cut_response(state, rng)
    decay = infrastructure_decay(state)
    new_integrity = max(0.0, state.infrastructure_integrity - decay)

    intermediate = L2State(
        material_cost_index=new_cost,
        corner_cut_intensity=new_cuts,
        infrastructure_integrity=new_integrity,
        contamination_load=state.contamination_load,
        community_viability=state.community_viability,
        labor_cost_multiplier=state.labor_cost_multiplier,
        year=state.year,
    )

    new_contam = state.contamination_load + contamination_release(intermediate, rng)
    intermediate.contamination_load = new_contam
    new_viability = community_response(intermediate)
    intermediate.community_viability = new_viability
    new_labor_cost = labor_cost_response(intermediate)

    # Loop closes: labor cost increase feeds back into next year's material
    # cost index because labor is embedded in material delivery / fabrication.
    feedback = (new_labor_cost - 1.0) * 0.15
    new_cost_with_feedback = new_cost * (1.0 + feedback)

    return L2State(
        material_cost_index=new_cost_with_feedback,
        corner_cut_intensity=new_cuts,
        infrastructure_integrity=new_integrity,
        contamination_load=new_contam,
        community_viability=new_viability,
        labor_cost_multiplier=new_labor_cost,
        year=state.year + 1,
    )


def run(years: int = 10, seed: int | None = None) -> list[L2State]:
    rng = random.Random(seed)
    state = L2State(
        material_cost_index=1.0,
        corner_cut_intensity=0.15,
        infrastructure_integrity=0.85,
        contamination_load=0.5,
        community_viability=0.85,
        labor_cost_multiplier=1.0,
    )
    history = [state]
    for _ in range(years):
        state = step(state, rng)
        history.append(state)
    return history


def loop_closed(history: list[L2State]) -> bool:
    """Loop closed if labor-cost feedback exceeds material savings from cuts."""
    if len(history) < 3:
        return False
    end = history[-1]
    return end.labor_cost_multiplier > 1.5 and end.community_viability < 0.4


if __name__ == "__main__":
    h = run(years=10, seed=7)
    for s in h:
        print(f"yr{s.year:2d} mat={s.material_cost_index:.2f} "
              f"cuts={s.corner_cut_intensity:.2f} integ={s.infrastructure_integrity:.2f} "
              f"contam={s.contamination_load:.2f} viab={s.community_viability:.2f} "
              f"labor={s.labor_cost_multiplier:.2f}")
    print(f"loop closed: {loop_closed(h)}")
