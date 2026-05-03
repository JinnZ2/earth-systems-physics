"""
loop4_aquifer_community_automation.py

US oil phase-shift sim — Loop 4: Aquifer <-> Community <-> Automation

Substrate:
    produced-water leakage + open-lake disposal + flood overflow ->
    aquifer + surface-water contamination -> community health decline,
    outmigration, school/hospital closures -> workforce gone ->
    automation attempted as substitute -> automation fails on
    goat-trail terrain, sensor drift from vibration, mud/lightning,
    radioactive corrosion of electronics -> production drops ->
    remaining wells extracted harder to compensate -> more failures ->
    more contamination. Loop closes.

Empirical anchors (field-observed):
    ~18 bbbl/yr produced water US; <1% genuinely re-injected
    open-air storage lakes overflow during flood/rain events
    composition: Ra-226, Ra-228, U, Th, benzene, heavy metals
    sensor recalibration needed multiple times per drive on well roads
    GPS-only autonomy fails: mud, sand, washout, no cell coverage
    community trajectory: water unlivable -> property abandoned ->
        school enrollment falls -> tax base falls -> services cut ->
        remaining residents are those without exit options

Style note: this loop uses Monte Carlo with dict-based state and the
global random module, deliberately different from loops 1-3 (which
use dataclasses + isolated random.Random instances). The aggregate
stats (pct_abandoned, pct_automation_succeeded, etc.) are the
activation predicates here; there is no single deterministic
trajectory worth singling out.

License: CC0
Stdlib only. Python 3.8+.
"""

import random
from statistics import mean


# ─────────────────────────────────────────────
# EMPIRICAL CONSTANTS
# ─────────────────────────────────────────────

PRODUCED_WATER_BBL_PER_YR = 18e9
LEAK_FRACTION_BASELINE = 0.005       # 0.5% per yr, normal ops
LEAK_FRACTION_FLOOD = 0.08           # 8% during overflow events
FLOOD_PROB_PER_YR = 0.25             # base climate-driven rate

AQUIFER_RECHARGE_RATE = 0.002        # 0.2% recharge per yr (deep aquifers)
CONTAMINATION_HALF_LIFE_YR = 80      # NORM persistence; effective decay slow

COMMUNITY_HEALTH_THRESHOLD = 0.15    # contamination above which health degrades
OUTMIGRATION_RATE_BASE = 0.02        # 2%/yr baseline rural decline
OUTMIGRATION_AMP = 0.18              # additional %/yr per contamination unit

AUTOMATION_ATTEMPT_THRESHOLD = 0.5   # workforce fraction below which automation tried
AUTOMATION_FAIL_RATE_BASE = 0.40     # 40%/yr equipment failure on rough terrain
AUTOMATION_FAIL_AMP = 0.6            # additional failure from contamination exposure
AUTOMATION_RESCUE_FACTOR = 0.25      # automation only replaces 25% of lost human capacity


# ─────────────────────────────────────────────
# STEP / TRAJECTORY
# ─────────────────────────────────────────────

def step_year(state, year, params):
    # 1. Routine leakage
    routine_leak = PRODUCED_WATER_BBL_PER_YR * LEAK_FRACTION_BASELINE
    # 2. Flood-driven overflow
    flood = random.random() < (FLOOD_PROB_PER_YR * params['flood_mult'])
    flood_leak = PRODUCED_WATER_BBL_PER_YR * LEAK_FRACTION_FLOOD if flood else 0
    total_leak = routine_leak + flood_leak

    # 3. Contamination accumulates with slow decay
    decay = state['aquifer_contamination'] * (0.693 / CONTAMINATION_HALF_LIFE_YR)
    state['aquifer_contamination'] += (total_leak / PRODUCED_WATER_BBL_PER_YR) - decay
    state['aquifer_contamination'] = max(0, state['aquifer_contamination'])

    # 4. Community response
    if state['aquifer_contamination'] > COMMUNITY_HEALTH_THRESHOLD:
        outmigration = OUTMIGRATION_RATE_BASE + \
                       OUTMIGRATION_AMP * (state['aquifer_contamination']
                                            - COMMUNITY_HEALTH_THRESHOLD)
    else:
        outmigration = OUTMIGRATION_RATE_BASE
    state['community_pop'] *= (1 - outmigration)
    state['workforce_avail'] = state['community_pop'] / state['initial_pop']

    # 5. Automation deployment when workforce drops
    if (state['workforce_avail'] < AUTOMATION_ATTEMPT_THRESHOLD
            and not state['automation_active']):
        state['automation_active'] = True
        state['automation_capacity'] = 0.10  # starts at 10% of needed capacity
        state['automation_invest_yr'] = year

    # 6. Automation performance (fails fast in this environment)
    if state['automation_active']:
        contam_amp = state['aquifer_contamination'] * AUTOMATION_FAIL_AMP
        fail_rate = AUTOMATION_FAIL_RATE_BASE + contam_amp
        # Investment tries to grow capacity; failures shrink it
        state['automation_capacity'] *= (1 - fail_rate)
        state['automation_capacity'] += 0.04  # ongoing investment
        state['automation_capacity'] = min(0.40, max(0, state['automation_capacity']))
        # automation only partially substitutes
        effective_workforce = (state['workforce_avail']
                               + state['automation_capacity']
                                 * AUTOMATION_RESCUE_FACTOR)
    else:
        effective_workforce = state['workforce_avail']

    # 7. Production capacity tracks effective workforce
    state['production_capacity'] = effective_workforce

    # 8. Remaining wells extracted harder when capacity drops -> more
    #    failures -> more leak (feedback into next year's leak baseline).
    extraction_pressure = max(1.0, 1 / max(0.1, effective_workforce))
    state['well_failure_rate'] = 0.02 * extraction_pressure
    state['_leak_next_amp'] = 1 + state['well_failure_rate']

    return {
        'year': year,
        'flood_event': flood,
        'aquifer_contam': state['aquifer_contamination'],
        'community_pop': state['community_pop'],
        'workforce_avail': state['workforce_avail'],
        'automation_active': state['automation_active'],
        'automation_capacity': state.get('automation_capacity', 0),
        'production_capacity': state['production_capacity'],
        'extraction_pressure': extraction_pressure,
    }


def run_trajectory(params, years=10, seed=None):
    if seed is not None:
        random.seed(seed)
    state = {
        'aquifer_contamination': 0.05,   # already-elevated baseline
        'community_pop': 10000.0,
        'initial_pop': 10000.0,
        'workforce_avail': 1.0,
        'automation_active': False,
        'automation_capacity': 0.0,
        'production_capacity': 1.0,
        'well_failure_rate': 0.02,
        '_leak_next_amp': 1.0,
    }
    return [step_year(state, y, params) for y in range(1, years + 1)]


# ─────────────────────────────────────────────
# MONTE CARLO
# ─────────────────────────────────────────────

def monte_carlo(n=2000, years=10, master_seed=None):
    """
    Aggregate sweep across n stochastic trajectories.
    master_seed : optional int. Setting it makes the whole sweep
                  reproducible (the first flood_mult draw and the
                  ordering of per-trajectory seeds become deterministic).
    """
    if master_seed is not None:
        random.seed(master_seed)

    finals = []
    abandoned = 0               # community pop < 25% baseline
    automation_tried = 0
    automation_succeeded = 0    # capacity sustained > 0.20
    contamination_runaway = 0   # > 0.40
    traces = []

    for i in range(n):
        params = {'flood_mult': random.uniform(0.7, 1.8)}
        trace = run_trajectory(params, years=years, seed=i)
        finals.append(trace[-1])
        if trace[-1]['community_pop'] < 2500:
            abandoned += 1
        if any(t['automation_active'] for t in trace):
            automation_tried += 1
            if trace[-1]['automation_capacity'] > 0.20:
                automation_succeeded += 1
        if trace[-1]['aquifer_contam'] > 0.40:
            contamination_runaway += 1
        if i < 5:
            traces.append(trace)

    return {
        'n': n,
        'years': years,
        'mean_final_contam':         mean(f['aquifer_contam'] for f in finals),
        'mean_final_pop':            mean(f['community_pop']  for f in finals),
        'mean_final_capacity':       mean(f['production_capacity'] for f in finals),
        'pct_abandoned':             abandoned / n,
        'pct_automation_tried':      automation_tried / n,
        'pct_automation_succeeded':  (automation_succeeded
                                      / max(1, automation_tried)),
        'pct_contamination_runaway': contamination_runaway / n,
        'sample_traces':             traces,
    }


def summary(r):
    print(f"L4 aquifer/community/automation loop, n={r['n']}, {r['years']}yr")
    print(f"  mean final aquifer contam:    {r['mean_final_contam']:.3f}")
    print(f"  mean final community pop:     {r['mean_final_pop']:.0f} of 10000")
    print(f"  mean final production cap:    {r['mean_final_capacity']:.2f}")
    print(f"  community abandoned:          {r['pct_abandoned']*100:.1f}%")
    print(f"  automation attempted:         {r['pct_automation_tried']*100:.1f}%")
    print(f"  automation succeeded (>20%):  "
          f"{r['pct_automation_succeeded']*100:.1f}% of attempts")
    print(f"  runaway contamination:        "
          f"{r['pct_contamination_runaway']*100:.1f}%")


if __name__ == '__main__':
    r = monte_carlo(n=2000, years=10, master_seed=2024)
    summary(r)
