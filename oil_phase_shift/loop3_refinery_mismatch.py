"""
loop3_refinery_mismatch.py

US oil phase-shift sim — Loop 3: Refinery configuration mismatch
under active Hormuz crisis initial conditions.

Substrate change vs prior framing: Hormuz disruption is no longer a
stochastic event with ~12% annual probability. As of 2026-02-28 it
is initial state. The strait has been effectively closed since
Operation Epic Fury; traffic running at ~5% of pre-war (~154 vessels
March 2026 vs ~3000/mo pre-war); war-risk insurance withdrawn
2026-03-05.

Substrate update:
- Hormuz transit: 5% of pre-war as t=0 condition
- Bypass pipeline coverage: 7 mmbbl/d vs 20 mmbbl/d normal = 35%
- Net global supply tightness: ~13% sustained (was modeled as a
  15% pulse event)
- Brent: peaked $126, currently >$100 (vs $65 pre-war)
- Iran-permitted transit lane exists for non-US/Israel/ally cargo
- Recovery is a state-dependent random variable, not assumed

Empirical anchors (2026-05-03):
    Pre-war Hormuz throughput:        20.9 mmbbl/d
    Current effective throughput:     ~1.0 mmbbl/d (5% of pre-war)
    Bypass pipeline aggregate:        ~7 mmbbl/d nameplate, ~5 effective
    Net Gulf crude reaching market:   ~6 mmbbl/d (was 20.9)
    Global supply removed:            ~14 mmbbl/d (~14% of global ~100)
    Brent pre-war:                    $65/bbl
    Brent peak post-war:              $126/bbl
    Brent current:                    ~$100-110/bbl
    Insurance status:                 war-risk withdrawn

License: CC0
Stdlib only. Python 3.8+.
"""

import random
from statistics import mean


# ─────────────────────────────────────────────
# EMPIRICAL CONSTANTS  (current state)
# ─────────────────────────────────────────────

US_REFINERY_CAPACITY_MMBBL = 18.4
LIGHT_SWEET_CONFIGURED_FRAC = 0.45
HEAVY_CONFIGURED_FRAC = 0.55

LIGHT_SWEET_DOMESTIC_SUPPLY = 13.5
HEAVY_IMPORT_BASELINE_PRE_CRISIS = 5.5

# Crisis state
HORMUZ_NORMAL_FLOW = 20.9
HORMUZ_CURRENT_FLOW = 1.0          # ~5% of pre-war
BYPASS_NAMEPLATE = 7.0
BYPASS_EFFECTIVE = 5.0
GLOBAL_SUPPLY_REMOVED = HORMUZ_NORMAL_FLOW - HORMUZ_CURRENT_FLOW - BYPASS_EFFECTIVE
# ~14.9 mmbbl/d removed from global supply

DEMAND_DESTRUCTION_THRESHOLD = 130

# Recovery dynamics: not a coin flip per year, but state-dependent
RECOVERY_BASE_PROB = 0.06          # 6%/yr conditional on no escalation
ESCALATION_PROB_PER_YR = 0.15      # 15%/yr the situation gets worse
DEEP_FREEZE_THRESHOLD_YR = 2       # after 2 yrs, recovery prob drops


# ─────────────────────────────────────────────
# DYNAMICS
# ─────────────────────────────────────────────

def hormuz_state_dynamics(state, year, params):
    """Update Hormuz throughput based on crisis trajectory."""
    if state['crisis_resolved']:
        # gradual recovery toward normal, capped at 80% in 5yr window
        target = 0.80 * HORMUZ_NORMAL_FLOW
        state['hormuz_flow'] += (target - state['hormuz_flow']) * 0.30
        return

    # Roll for escalation
    escalate = random.random() < (ESCALATION_PROB_PER_YR
                                  * params['escalation_mult'])
    if escalate:
        state['hormuz_flow'] = max(0.1, state['hormuz_flow'] * 0.5)
        state['escalation_events'] += 1

    # Roll for resolution
    crisis_age = year - state['crisis_start_yr']
    if crisis_age <= DEEP_FREEZE_THRESHOLD_YR:
        recovery_prob = RECOVERY_BASE_PROB
    else:
        # after 2 years, structural reorganization makes recovery harder
        recovery_prob = RECOVERY_BASE_PROB * 0.4
    if (random.random() < recovery_prob
            and state['escalation_events'] == 0):
        state['crisis_resolved'] = True


def step_year(state, year, params):
    # 1. Permian-driven light supply decline (couples to L1 in cascade layer)
    decline = random.uniform(0.04, 0.10) * params['permian_decline_mult']
    state['light_supply'] *= (1 - decline)

    # 2. Hormuz state evolves
    hormuz_state_dynamics(state, year, params)

    # 3. Heavy import availability — degraded by Hormuz state and global tightness
    global_tightness = (HORMUZ_NORMAL_FLOW - state['hormuz_flow']
                        - BYPASS_EFFECTIVE) / 100
    global_tightness = max(0, global_tightness)

    # Non-Gulf heavy (Canada, Mexico) becomes more contested as
    # Asia/Europe scramble for alternatives.
    canadian_mexican_avail = HEAVY_IMPORT_BASELINE_PRE_CRISIS * (
        1 - global_tightness * 0.6
    )
    state['heavy_supply'] = canadian_mexican_avail

    # 4. Refinery throughput — feedstock-config match
    light_processable = min(
        state['light_supply'],
        US_REFINERY_CAPACITY_MMBBL * LIGHT_SWEET_CONFIGURED_FRAC
    )
    heavy_processable = min(
        state['heavy_supply'],
        US_REFINERY_CAPACITY_MMBBL * HEAVY_CONFIGURED_FRAC
    )
    state['throughput'] = light_processable + heavy_processable
    state['utilization'] = state['throughput'] / US_REFINERY_CAPACITY_MMBBL

    state['light_exported_raw'] = max(
        0, state['light_supply'] - light_processable
    )
    state['heavy_capacity_idle'] = max(
        0,
        US_REFINERY_CAPACITY_MMBBL * HEAVY_CONFIGURED_FRAC - heavy_processable
    )

    # 5. Crude price — anchored to current ~$100 baseline, scales with tightness
    base_price = 100 + global_tightness * 400
    state['oil_price'] = base_price + random.gauss(0, 10)
    state['oil_price'] = max(50, min(250, state['oil_price']))

    # 6. Demand destruction
    if state['oil_price'] > DEMAND_DESTRUCTION_THRESHOLD:
        state['demand_destroyed'] = (
            (state['oil_price'] - DEMAND_DESTRUCTION_THRESHOLD) * 0.025
        )
    else:
        state['demand_destroyed'] = 0.0

    # 7. Retool decision — slower than the prior framing because crisis
    #    volatility delays capex (8% trigger rate vs ~15% in stable regime).
    margin_signal = (state['oil_price'] - 75) / 75
    if margin_signal > 0.40 and not state['retool_initiated']:
        if random.random() < 0.08:
            state['retool_initiated'] = True
            state['retool_eta_yr'] = year + 3   # longer build time

    return {
        'year': year,
        'hormuz_flow':         state['hormuz_flow'],
        'crisis_resolved':     state['crisis_resolved'],
        'escalation_events':   state['escalation_events'],
        'light_supply':        state['light_supply'],
        'heavy_supply':        state['heavy_supply'],
        'throughput':          state['throughput'],
        'utilization':         state['utilization'],
        'light_exported_raw':  state['light_exported_raw'],
        'heavy_capacity_idle': state['heavy_capacity_idle'],
        'oil_price':           state['oil_price'],
        'demand_destroyed':    state['demand_destroyed'],
        'retool_active':       state['retool_initiated'],
        'global_tightness':    global_tightness,
    }


def run_trajectory(params, years=10, seed=None):
    if seed is not None:
        random.seed(seed)
    state = {
        # Start in active crisis state
        'hormuz_flow':       HORMUZ_CURRENT_FLOW,
        'crisis_start_yr':   0,
        'crisis_resolved':   False,
        'escalation_events': 0,
        'light_supply':      LIGHT_SWEET_DOMESTIC_SUPPLY,
        # Heavy supply already degraded by Asia/Europe scramble
        'heavy_supply':      HEAVY_IMPORT_BASELINE_PRE_CRISIS * 0.7,
        'throughput':        0.0,
        'utilization':       0.85,
        'light_exported_raw':  0.0,
        'heavy_capacity_idle': 0.0,
        'oil_price':         105.0,
        'demand_destroyed':  0.0,
        'retool_initiated':  False,
    }
    return [step_year(state, y, params) for y in range(1, years + 1)]


# ─────────────────────────────────────────────
# MONTE CARLO
# ─────────────────────────────────────────────

def monte_carlo(n=2000, years=10, master_seed=None):
    """
    Aggregate sweep across n stochastic trajectories.
    master_seed : optional int making the whole sweep reproducible.
    """
    if master_seed is not None:
        random.seed(master_seed)

    finals = []
    no_recovery = 0
    crisis_resolved = 0
    sustained_high_price = 0    # price > $130 for 3+ yrs
    demand_destruction_significant = 0
    traces = []

    for i in range(n):
        params = {
            'permian_decline_mult': random.uniform(0.7, 1.5),
            'escalation_mult':      random.uniform(0.6, 1.6),
        }
        trace = run_trajectory(params, years=years, seed=i)
        finals.append(trace[-1])
        if trace[-1]['crisis_resolved']:
            crisis_resolved += 1
        else:
            no_recovery += 1
        high_price_yrs = sum(1 for t in trace if t['oil_price'] > 130)
        if high_price_yrs >= 3:
            sustained_high_price += 1
        if mean(t['demand_destroyed'] for t in trace) > 0.5:
            demand_destruction_significant += 1
        if i < 5:
            traces.append(trace)

    return {
        'n': n,
        'years': years,
        'pct_crisis_resolved':      crisis_resolved / n,
        'pct_no_recovery':          no_recovery / n,
        'pct_sustained_high_price': sustained_high_price / n,
        'pct_demand_destruction':   demand_destruction_significant / n,
        'mean_final_price':         mean(f['oil_price'] for f in finals),
        'mean_final_throughput':    mean(f['throughput'] for f in finals),
        'mean_final_hormuz':        mean(f['hormuz_flow'] for f in finals),
        'mean_demand_destroyed':    mean(f['demand_destroyed'] for f in finals),
        'sample_traces':            traces,
    }


def summary(r):
    print(f"L3 refinery mismatch + active Hormuz crisis, "
          f"n={r['n']}, {r['years']}yr")
    print(f"  mean final price:                ${r['mean_final_price']:.2f}/bbl")
    print(f"  mean final Hormuz flow:           "
          f"{r['mean_final_hormuz']:.2f} mmbbl/d (normal: 20.9)")
    print(f"  mean final US throughput:         "
          f"{r['mean_final_throughput']:.2f} mmbbl/d")
    print(f"  mean demand destroyed:            "
          f"{r['mean_demand_destroyed']:.3f} mmbbl/d")
    print(f"  crisis resolved within {r['years']}yr:  "
          f"{r['pct_crisis_resolved']*100:.1f}%")
    print(f"  no recovery in window:            "
          f"{r['pct_no_recovery']*100:.1f}%")
    print(f"  sustained high price (3+ yr):     "
          f"{r['pct_sustained_high_price']*100:.1f}%")
    print(f"  significant demand destruction:   "
          f"{r['pct_demand_destruction']*100:.1f}%")


if __name__ == '__main__':
    r = monte_carlo(n=2000, years=10, master_seed=2026)
    summary(r)
