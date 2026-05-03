"""
loop5_signal_trust_collapse.py

US oil phase-shift sim — Loop 5: Signal <-> Trust <-> Consent

Substrate:
    ecological/economic damage visible to substrate-primary observers
    (smelt decline, water smell, well failures, depletion curves) ->
    biological/sensory signal accurate -> institutional gaslighting
    ("energy independent", "saltwater disposal", "managed transition") ->
    gap between observed reality and official narrative widens ->
    trust in institutions collapses -> no consent for new infrastructure,
    remediation, or policy adjustment -> policy paralysis ->
    damage continues unmitigated -> more visible damage -> wider gap.
    Loop closes.

This is the META-LOOP. It governs whether L1-L4 get RESPONDED TO
in time. Without trust, no remediation; without remediation, all
other loops cascade unchecked.

Empirical anchors:
    - "Energy independent" narrative held while net imports persist
    - Strait of Hormuz: official "open" / actual ~5% pre-war traffic
    - Permian "stable" / actual 40% base decline accelerating
    - "Saltwater disposal" / actual NORM-laden produced water
    - Smelt decline blamed on year-to-year variance / 10yr trend
    - Insect/bird absence at peak migration (Fairmont corridor)
    - Workers measure ground truth; institutions report dashboard truth
    - Substrate-primary cognition pathologized as anxiety/pessimism

License: CC0
Stdlib only. Python 3.8+.
"""

import random
from statistics import mean


# ─────────────────────────────────────────────
# EMPIRICAL CONSTANTS
# Trust is bounded [0, 1]. Starts mid because some baseline still exists.
# ─────────────────────────────────────────────

TRUST_INITIAL = 0.45

# Gap between observed reality and official narrative
NARRATIVE_GAP_INITIAL = 0.30   # already substantial in 2026

# Trust dynamics
TRUST_EROSION_PER_GAP_UNIT = 0.40        # how fast gap erodes trust
TRUST_RECOVERY_FROM_HONEST_REPORTING = 0.05  # slow recovery if narrative aligns
TRUST_FLOOR_AFTER_BREACH = 0.10          # below this, recovery becomes non-linear

# Consent dynamics
CONSENT_THRESHOLD = 0.35                 # trust below which infrastructure consent fails
REMEDIATION_BLOCKED_PROB = 0.85          # when consent fails, fraction of repair work blocked

# Narrative gap dynamics
DAMAGE_VISIBILITY_RATE = 0.06            # 6%/yr more damage becomes undeniable
NARRATIVE_RIGIDITY = 0.85                # institutions resist narrative update
HONEST_PIVOT_PROB = 0.04                 # 4%/yr chance of institutional honesty event

# Crisis amplifier — Hormuz / visible failures accelerate gap recognition
VISIBILITY_AMPLIFIER_DURING_CRISIS = 2.5


# ─────────────────────────────────────────────
# DYNAMICS
# ─────────────────────────────────────────────

def step_year(state, year, params):
    # 1. Visible damage accumulates (driven by L1-L4 substrate state)
    visibility_rate = DAMAGE_VISIBILITY_RATE * params['damage_visibility_mult']
    if state['active_crisis']:
        visibility_rate *= VISIBILITY_AMPLIFIER_DURING_CRISIS
    state['visible_damage'] = min(1.0, state['visible_damage']
                                       + visibility_rate)

    # 2. Narrative may or may not pivot
    honest_pivot = random.random() < HONEST_PIVOT_PROB
    if honest_pivot:
        # narrative jumps closer to reality
        state['official_narrative'] = state['visible_damage'] * 0.85
        state['narrative_pivots'] += 1
    else:
        # narrative drifts only slowly toward reality
        drift = (state['visible_damage'] - state['official_narrative']) * (
            1 - NARRATIVE_RIGIDITY
        )
        state['official_narrative'] += drift * 0.1

    # 3. Narrative gap = observed - official
    state['narrative_gap'] = max(
        0, state['visible_damage'] - state['official_narrative']
    )

    # 4. Trust erosion driven by gap
    erosion = state['narrative_gap'] * TRUST_EROSION_PER_GAP_UNIT
    if honest_pivot:
        state['trust'] += TRUST_RECOVERY_FROM_HONEST_REPORTING
    state['trust'] -= erosion
    state['trust'] = max(0, min(1.0, state['trust']))

    # 5. Trust below floor: hysteresis kicks in
    if state['trust'] < TRUST_FLOOR_AFTER_BREACH:
        state['below_floor_years'] += 1
        # Once below floor for 2+ yrs, narrative pivots stop helping much
        if state['below_floor_years'] >= 2:
            state['structural_distrust'] = True

    # 6. Consent for infrastructure / remediation
    if state['trust'] < CONSENT_THRESHOLD:
        state['consent_active'] = False
        state['remediation_blocked_frac'] = REMEDIATION_BLOCKED_PROB
    else:
        state['consent_active'] = True
        state['remediation_blocked_frac'] = max(0, 1 - state['trust']) * 0.4

    # 7. Policy response capacity (damped by structural distrust)
    if state['structural_distrust']:
        state['policy_response_capacity'] = 0.10
    elif not state['consent_active']:
        state['policy_response_capacity'] = 0.30
    else:
        state['policy_response_capacity'] = state['trust']

    # 8. Substrate-primary observers (people reading reality directly).
    #    When narrative gap is large, more people trust their own
    #    measurement — but get pathologized for it.
    if state['narrative_gap'] > 0.20:
        state['substrate_observers'] = min(
            1.0, state['substrate_observers'] + 0.03
        )
    state['pathologized'] = (
        state['narrative_gap'] * state['substrate_observers']
    )

    return {
        'year': year,
        'visible_damage':           state['visible_damage'],
        'official_narrative':       state['official_narrative'],
        'narrative_gap':            state['narrative_gap'],
        'trust':                    state['trust'],
        'consent_active':           state['consent_active'],
        'remediation_blocked_frac': state['remediation_blocked_frac'],
        'policy_response_capacity': state['policy_response_capacity'],
        'structural_distrust':      state['structural_distrust'],
        'narrative_pivots':         state['narrative_pivots'],
        'substrate_observers':      state['substrate_observers'],
        'pathologized':             state['pathologized'],
    }


def run_trajectory(params, years=10, seed=None):
    if seed is not None:
        random.seed(seed)
    state = {
        'visible_damage':           0.30,                   # already substantial
        'official_narrative':       0.05,                   # institutions claim minimal
        'narrative_gap':            NARRATIVE_GAP_INITIAL,
        'trust':                    TRUST_INITIAL,
        'consent_active':           True,
        'remediation_blocked_frac': 0.20,
        'policy_response_capacity': 0.45,
        'structural_distrust':      False,
        'below_floor_years':        0,
        'narrative_pivots':         0,
        'substrate_observers':      0.20,
        'pathologized':             0.0,
        'active_crisis':            params.get('active_crisis', True),  # Hormuz live
    }
    return [step_year(state, y, params) for y in range(1, years + 1)]


# ─────────────────────────────────────────────
# MONTE CARLO
# ─────────────────────────────────────────────

def monte_carlo(n=2000, years=10, master_seed=None):
    if master_seed is not None:
        random.seed(master_seed)

    finals = []
    structural_distrust = 0
    consent_failed = 0
    narrative_pivot_occurred = 0
    pathologization_high = 0
    traces = []

    for i in range(n):
        params = {
            'damage_visibility_mult': random.uniform(0.7, 1.5),
            'active_crisis':          True,
        }
        trace = run_trajectory(params, years=years, seed=i)
        finals.append(trace[-1])
        if trace[-1]['structural_distrust']:
            structural_distrust += 1
        if not trace[-1]['consent_active']:
            consent_failed += 1
        if trace[-1]['narrative_pivots'] > 0:
            narrative_pivot_occurred += 1
        if trace[-1]['pathologized'] > 0.3:
            pathologization_high += 1
        if i < 5:
            traces.append(trace)

    return {
        'n': n,
        'years': years,
        'mean_final_trust':         mean(f['trust'] for f in finals),
        'mean_narrative_gap':       mean(f['narrative_gap'] for f in finals),
        'mean_policy_capacity':     mean(f['policy_response_capacity']
                                         for f in finals),
        'pct_structural_distrust':  structural_distrust / n,
        'pct_consent_failed':       consent_failed / n,
        'pct_narrative_pivot':      narrative_pivot_occurred / n,
        'pct_high_pathologization': pathologization_high / n,
        'sample_traces':            traces,
    }


def summary(r):
    print(f"L5 signal/trust/consent loop, n={r['n']}, {r['years']}yr")
    print(f"  mean final trust:                 {r['mean_final_trust']:.3f}")
    print(f"  mean final narrative gap:         {r['mean_narrative_gap']:.3f}")
    print(f"  mean policy response capacity:    {r['mean_policy_capacity']:.3f}")
    print(f"  structural distrust reached:      "
          f"{r['pct_structural_distrust']*100:.1f}%")
    print(f"  consent for infrastructure lost:  "
          f"{r['pct_consent_failed']*100:.1f}%")
    print(f"  any narrative pivot occurred:     "
          f"{r['pct_narrative_pivot']*100:.1f}%")
    print(f"  high pathologization of observers: "
          f"{r['pct_high_pathologization']*100:.1f}%")


if __name__ == '__main__':
    r = monte_carlo(n=2000, years=10, master_seed=2026)
    summary(r)
