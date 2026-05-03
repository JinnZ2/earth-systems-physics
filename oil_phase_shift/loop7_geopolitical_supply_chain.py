"""
loop7_geopolitical_supply_chain.py

US oil phase-shift sim — Loop 7: Geopolitical material flow +
defense priority capture + sanctions cascades.

Substrate (field-verified):
    Materials needed for US energy infrastructure substantially
    originate outside US borders or depend on global supply
    networks:
        - Specialty steel (Germany, Japan, South Korea)
        - Sulfur (byproduct of refining; geopolitically distributed)
        - Aluminum (energy-intensive production; shifting jurisdictions)
        - Plastics / polymers (refining feedstock; circular dependency)
        - Specialty chemicals / diluents (refinery solvents)
        - Drilling equipment, drill shafts, drill bits
        - Frac sand logistics (domestic but trucking-dependent)
        - Rare earths (China-dominant for many grades)
        - Replacement fittings for produced-water-resistant applications

When geopolitical tension rises, three mechanisms fire:
    M1: Direct supply restriction (sanctions, embargoes, blockade)
    M2: Defense priority capture (military procurement outranks
        civilian)
    M3: Cascade reallocation (restriction on one source shifts
        demand to others -> price rises everywhere -> marginal
        sources viable -> new dependencies -> new vulnerabilities)

Result: even with adequate domestic energy resources, the
*infrastructure to extract and process them* depends on global
supply chains that can be cut by events the US doesn't control.
"Energy independence" claims ignore the input-side dependency.

Empirical anchors (2026-05-03):
    - Brownsville refinery: behind on German steel, plastic supply
    - Active Hormuz crisis: 2026-02-28
    - Active US blockade of Iranian ports: 2026-04-13
    - China-US trade tensions: ongoing
    - Russia exclusion from Western markets: ongoing since 2022
    - Defense procurement budget rising; civilian capex competing
    - Rare earth processing: ~85% China; alternatives capacity-limited

License: CC0
Stdlib only. Python 3.8+.
"""

import random
from statistics import mean


# ─────────────────────────────────────────────
# EMPIRICAL CONSTANTS
# ─────────────────────────────────────────────

# Material categories with foreign-supply dependency
# (0 = fully domestic, 1 = fully foreign)
MATERIAL_DEPENDENCY = {
    'specialty_steel':     0.75,   # Germany, Japan, Korea dominant
    'rare_earths':         0.85,   # China-dominant
    'aluminum':            0.55,   # mixed
    'sulfur':              0.40,   # global circulation
    'plastics_polymers':   0.30,   # partly circular (refining byproduct)
    'specialty_chems':     0.65,   # diluents, solvents, catalysts
    'drilling_equipment':  0.50,   # mixed manufacturing
    'replacement_parts':   0.45,   # specialty alloys imported
    'frac_sand_logistics': 0.10,   # domestic supply but labor-constrained
}

# How much each material affects each downstream sector
# (0 = none, 1 = critical)
MATERIAL_TO_SECTOR = {
    'specialty_steel':     {'refinery_build':  0.95, 'pipelines':    0.80,
                            'wells':           0.40},
    'rare_earths':         {'control_systems': 0.85, 'sensors':      0.70,
                            'motors':          0.60},
    'aluminum':            {'pipelines':       0.50, 'storage':      0.60,
                            'transport':       0.55},
    'sulfur':              {'refining':        0.85, 'chemicals':    0.70},
    'plastics_polymers':   {'sealing':         0.70, 'pipes':        0.40,
                            'electronics':     0.50},
    'specialty_chems':     {'refining':        0.90, 'extraction':   0.55},
    'drilling_equipment':  {'wells':           0.95},
    'replacement_parts':   {'maintenance':     0.85, 'wells':        0.60,
                            'refining':        0.55},
    'frac_sand_logistics': {'extraction':      0.80},
}

# Geopolitical tension drivers (probability per year of disruption event)
TENSION_BASELINE = 0.18              # current elevated baseline
DEFENSE_CAPTURE_THRESHOLD = 0.55     # tension above which defense begins
                                     # capturing materials
DEFENSE_CAPTURE_RATE = 0.30          # fraction of supply diverted to defense

SANCTIONS_CASCADE_AMPLIFIER = 1.6    # each restriction raises prices
                                     # ~1.6x downstream
SUBSTITUTION_DELAY_YEARS = 2.0       # how long to qualify alt-supplier
SUBSTITUTION_SUCCESS_RATE = 0.40     # most substitutions don't fully replace


# ─────────────────────────────────────────────
# DYNAMICS
# ─────────────────────────────────────────────

def step_year(state, year, params):
    # 1. Geopolitical tension level evolves
    tension_drift = random.gauss(0, 0.05) + params['tension_pressure']
    state['tension'] = max(0.0, min(1.0, state['tension'] + tension_drift))

    # 2. Disruption events fire on tension-weighted probability
    materials_disrupted = []
    for material, dependency in MATERIAL_DEPENDENCY.items():
        # Higher dependency * higher tension = higher disruption probability
        disruption_prob = (state['tension'] * dependency
                           * params['disruption_mult'])
        if random.random() < disruption_prob:
            materials_disrupted.append(material)
            current = state['material_availability'][material]
            severity = random.uniform(0.3, 0.8)
            state['material_availability'][material] = max(
                0.05, current * (1 - severity)
            )

    # 3. Defense priority capture
    if state['tension'] > DEFENSE_CAPTURE_THRESHOLD:
        for material in MATERIAL_DEPENDENCY:
            available = state['material_availability'][material]
            captured = available * DEFENSE_CAPTURE_RATE
            state['material_availability'][material] = available - captured
            state['defense_captured_materials'] += captured

    # 4. Substitution attempts (slow, partial)
    for material in materials_disrupted:
        if material not in state['substitution_in_progress']:
            state['substitution_in_progress'][material] = (
                year + SUBSTITUTION_DELAY_YEARS
            )

    # Substitutions that complete this year
    completing = [
        m for m, eta in state['substitution_in_progress'].items()
        if eta <= year
    ]
    for material in completing:
        if random.random() < SUBSTITUTION_SUCCESS_RATE:
            recovered = (1 - state['material_availability'][material]) * 0.4
            state['material_availability'][material] += recovered
        del state['substitution_in_progress'][material]

    # 5. Recovery for materials NOT under active disruption (partial)
    for material in MATERIAL_DEPENDENCY:
        if material not in materials_disrupted:
            current = state['material_availability'][material]
            target = (1.0 - MATERIAL_DEPENDENCY[material] * 0.3
                          * state['tension'])
            state['material_availability'][material] += (
                (target - current) * 0.20
            )
            state['material_availability'][material] = max(
                0.05, min(1.0, state['material_availability'][material])
            )

    # 6. Compute sector-level capacity from material availability
    sector_capacity = {}
    sectors = set()
    for sector_dict in MATERIAL_TO_SECTOR.values():
        sectors.update(sector_dict.keys())

    for sector in sectors:
        # sector capacity = product of (material_availability ^ criticality)
        capacity = 1.0
        for material, sector_dict in MATERIAL_TO_SECTOR.items():
            if sector in sector_dict:
                criticality = sector_dict[sector]
                avail = state['material_availability'][material]
                # criticality weights how much this material constrains
                # the sector
                capacity *= (avail ** criticality)
        sector_capacity[sector] = capacity
    state['sector_capacity'] = sector_capacity

    # 7. Aggregate energy-infrastructure capacity (geometric mean of sectors)
    sector_values = list(sector_capacity.values())
    if sector_values:
        product = 1.0
        for v in sector_values:
            product *= max(v, 0.01)
        geom_mean = product ** (1.0 / len(sector_values))
        state['infra_capacity'] = geom_mean
    else:
        state['infra_capacity'] = 0.0

    # 8. Sanctions cascade — tracks price-amplification propagation
    if len(materials_disrupted) > 2:
        state['cascade_amplifier'] = min(
            3.0, state['cascade_amplifier'] * SANCTIONS_CASCADE_AMPLIFIER
        )
    else:
        state['cascade_amplifier'] = max(
            1.0, state['cascade_amplifier'] * 0.95
        )

    return {
        'year': year,
        'tension':                     state['tension'],
        'materials_disrupted_count':   len(materials_disrupted),
        'mean_material_availability':  mean(state['material_availability'].values()),
        'min_material_availability':   min(state['material_availability'].values()),
        'min_material_name':           min(state['material_availability'],
                                            key=state['material_availability'].get),
        'sector_capacity_min':         (min(sector_capacity.values())
                                         if sector_capacity else 0),
        'sector_capacity_min_name':    (min(sector_capacity,
                                            key=sector_capacity.get)
                                         if sector_capacity else None),
        'infra_capacity':              state['infra_capacity'],
        'defense_captured_cumulative': state['defense_captured_materials'],
        'cascade_amplifier':           state['cascade_amplifier'],
        'substitutions_active':        len(state['substitution_in_progress']),
    }


def run_trajectory(params, years=10, seed=None):
    if seed is not None:
        random.seed(seed)
    state = {
        'tension': TENSION_BASELINE,
        'material_availability': {
            m: 1.0 - MATERIAL_DEPENDENCY[m] * 0.15
            for m in MATERIAL_DEPENDENCY
        },
        'substitution_in_progress':   {},
        'defense_captured_materials': 0.0,
        'cascade_amplifier':          1.0,
        'sector_capacity':            {},
        'infra_capacity':             1.0,
    }
    return [step_year(state, y, params) for y in range(1, years + 1)]


# ─────────────────────────────────────────────
# MONTE CARLO
# ─────────────────────────────────────────────

def monte_carlo(n=2000, years=10, master_seed=None):
    if master_seed is not None:
        random.seed(master_seed)

    finals = []
    severe_capacity_loss = 0       # infra_capacity < 0.40
    moderate_capacity_loss = 0     # 0.40 - 0.70
    capacity_intact = 0            # > 0.70
    sustained_high_tension = 0     # tension > 0.7 for 3+ yrs
    defense_capture_significant = 0
    traces = []

    for i in range(n):
        params = {
            'tension_pressure': random.uniform(-0.02, 0.06),  # bias toward escalation
            'disruption_mult':  random.uniform(0.7, 1.4),
        }
        trace = run_trajectory(params, years=years, seed=i)
        finals.append(trace[-1])
        final_cap = trace[-1]['infra_capacity']
        if final_cap < 0.40:
            severe_capacity_loss += 1
        elif final_cap < 0.70:
            moderate_capacity_loss += 1
        else:
            capacity_intact += 1

        high_tension_years = sum(1 for t in trace if t['tension'] > 0.7)
        if high_tension_years >= 3:
            sustained_high_tension += 1
        if trace[-1]['defense_captured_cumulative'] > 1.0:
            defense_capture_significant += 1
        if i < 5:
            traces.append(trace)

    return {
        'n': n,
        'years': years,
        'mean_final_infra_capacity':   mean(f['infra_capacity']  for f in finals),
        'mean_final_tension':          mean(f['tension']         for f in finals),
        'mean_cascade_amp':            mean(f['cascade_amplifier'] for f in finals),
        'pct_severe_capacity_loss':    severe_capacity_loss / n,
        'pct_moderate_capacity_loss':  moderate_capacity_loss / n,
        'pct_capacity_intact':         capacity_intact / n,
        'pct_sustained_high_tension':  sustained_high_tension / n,
        'pct_defense_capture':         defense_capture_significant / n,
        'sample_traces':               traces,
    }


def summary(r):
    print(f"L7 geopolitical supply chain loop, "
          f"n={r['n']}, {r['years']}yr")
    print(f"  mean final infra capacity:        "
          f"{r['mean_final_infra_capacity']:.3f}")
    print(f"  mean final tension:                "
          f"{r['mean_final_tension']:.3f}")
    print(f"  mean cascade amplifier:            "
          f"{r['mean_cascade_amp']:.2f}x")
    print(f"  severe capacity loss (<40%):       "
          f"{r['pct_severe_capacity_loss']*100:.1f}%")
    print(f"  moderate capacity loss (40-70%):   "
          f"{r['pct_moderate_capacity_loss']*100:.1f}%")
    print(f"  capacity intact (>70%):            "
          f"{r['pct_capacity_intact']*100:.1f}%")
    print(f"  sustained high tension (3+ yr):    "
          f"{r['pct_sustained_high_tension']*100:.1f}%")
    print(f"  significant defense capture:       "
          f"{r['pct_defense_capture']*100:.1f}%")


if __name__ == '__main__':
    r = monte_carlo(n=2000, years=10, master_seed=2026)
    summary(r)
