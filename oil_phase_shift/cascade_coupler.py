"""
cascade_coupler.py

US oil phase-shift sim — Integration layer for L1-L7 with cross-loop edges.

Substrate principle:
    Each loop in isolation produces a collapse-grade output because
    there are no damping or compensating mechanisms outside the loop.
    In reality, loops modulate each other — sometimes amplifying,
    sometimes (rarely) damping. The cascade detector must:
        1. Run all 7 loops with shared state
        2. Apply cross-loop edges (output of one loop modifies input
           of others)
        3. Produce a PATH DISTRIBUTION over outcome modes, not a
           single trajectory
        4. Surface which loops are leading drivers in each mode

Cross-loop edges (substrate-named, not invented):
    L1 production drop          -> L3 light supply input
    L2 contamination            -> L4 aquifer load
    L4 community collapse       -> L1 labor pool floor
    L3 price spikes             -> L2 margin compression
    L5 trust collapse           -> ALL loops' response_capacity
    L6 prior calibration        -> L5 narrative gap visibility
    L7 material constraint      -> L1 wells drillable, L3 refinery retool
    L7 defense capture          -> L4 automation feasibility
    L1 + L4 coupled collapse    -> L5 visible damage acceleration
    L3 sustained crisis         -> L7 tension pressure

Outcome modes (predicted before run):
    A. managed_contraction       — sustained high prices, regional
                                    damage, no acute collapse,
                                    ~15-25 yr adjustment
    B. stair_step_cascade        — multiple loops fire in sequence,
                                    response capacity insufficient,
                                    5-8 yr crisis
    C. honest_pivot_recovery     — L5 narrative pivot early enough
                                    to preserve consent, response
                                    deploys
    D. hard_break                — L3 + L7 simultaneous,
                                    infrastructure seizure, demand
                                    destruction forced

License: CC0
Stdlib only. Python 3.8+.
"""

import random
from statistics import mean


# ─────────────────────────────────────────────
# SHARED STATE
# ─────────────────────────────────────────────

class CascadeState:
    """Shared state across all loops. Each loop reads what it needs
    and writes its own outputs back. Cross-loop edges live here."""

    def __init__(self):
        # L1 state (depletion-labor)
        self.production = 13.5
        self.decline_rate = 0.40
        self.labor_pool = 1.0
        self.tier1_remaining = 3.7
        self.avg_well_ip = 0.000433

        # L2 state (cost / corner-cutting)
        self.opex_per_bbl = 35.0
        self.corner_cut_intensity = 0.20
        self.contamination_load = 0.0
        self.failure_rate = 0.02

        # L3 state (refinery + Hormuz)
        self.light_supply = 13.5
        self.heavy_supply = 5.5 * 0.7
        self.hormuz_flow = 1.0       # crisis baseline
        self.crisis_resolved = False
        self.oil_price = 105.0
        self.refinery_throughput = 0.0

        # L4 state (aquifer-community-automation)
        self.aquifer_contamination = 0.05
        self.community_pop = 1.0
        self.automation_active = False
        self.automation_capacity = 0.0

        # L5 state (trust-consent)
        self.visible_damage = 0.30
        self.official_narrative = 0.05
        self.narrative_gap = 0.30
        self.trust = 0.45
        self.policy_response_capacity = 0.45
        self.structural_distrust = False

        # L6 state (AI prior)
        self.prior_calibration = 0.65
        self.info_quality = 0.40
        self.substrate_observers = 0.20

        # L7 state (geopolitical)
        self.tension = 0.18
        self.material_avail = 0.85   # aggregate
        self.defense_capture_active = False
        self.cascade_amplifier = 1.0


# ─────────────────────────────────────────────
# COUPLED LOOP STEPS
# Each step reads shared state, applies its loop's dynamics, and
# writes back. Cross-loop edges are the cross-references between
# state fields written by one step and read by another.
# ─────────────────────────────────────────────

def step_L1(s, p):
    """Depletion-labor with L4 community + L7 material coupling."""
    s.decline_rate = min(0.65, s.decline_rate + 0.0086 * p['decline_accel'])
    labor_floor = s.community_pop * 0.4
    s.labor_pool = max(labor_floor,
                       s.labor_pool * (1 - random.uniform(0.02, 0.12)))

    target_wells = s.production * s.decline_rate / s.avg_well_ip
    max_wells_labor = s.labor_pool * 5000
    max_wells_material = s.material_avail * 5000
    actual_wells = min(target_wells, max_wells_labor, max_wells_material)

    s.tier1_remaining = max(0, s.tier1_remaining - actual_wells / 5000)
    if s.tier1_remaining <= 0:
        s.avg_well_ip *= 0.97

    decline_loss = s.production * s.decline_rate
    new_added = actual_wells * s.avg_well_ip
    s.production = max(0, s.production - decline_loss + new_added)


def step_L2(s, p):
    """Cost / corner-cutting with L3 price + L4 aquifer feedback."""
    inflation = random.uniform(0.04, p['inflation_ceil'])
    s.opex_per_bbl *= (1 + inflation * s.cascade_amplifier)
    margin_ratio = (s.oil_price - s.opex_per_bbl) / max(1, s.oil_price)
    if margin_ratio < 0.15:
        s.corner_cut_intensity = min(1.0, s.corner_cut_intensity + 0.10)
    else:
        s.corner_cut_intensity = max(0.0, s.corner_cut_intensity - 0.02)

    fail_rate = 0.02 * (1 + s.corner_cut_intensity * 4.0)
    s.failure_rate = fail_rate
    contam_added = fail_rate * 100000 * 0.001
    s.contamination_load += contam_added
    # feeds aquifer
    s.aquifer_contamination += contam_added * 0.3


def step_L3(s, p):
    """Refinery + Hormuz crisis with L1 supply + L7 retool material coupling."""
    s.light_supply = s.production  # direct couple from L1

    # Hormuz dynamics
    if not s.crisis_resolved:
        if random.random() < 0.15 * p['escalation']:
            s.hormuz_flow = max(0.1, s.hormuz_flow * 0.5)
        if random.random() < 0.06 and s.tension < 0.4:
            s.crisis_resolved = True
    else:
        s.hormuz_flow += (16.7 - s.hormuz_flow) * 0.30

    global_tightness = max(0, (20.9 - s.hormuz_flow - 5.0) / 100)
    s.heavy_supply = 5.5 * 0.7 * (1 - global_tightness * 0.6)

    light_processable = min(s.light_supply, 18.4 * 0.45)
    heavy_processable = min(s.heavy_supply, 18.4 * 0.55)
    s.refinery_throughput = light_processable + heavy_processable

    base_price = 100 + global_tightness * 400
    s.oil_price = max(50, min(250, base_price + random.gauss(0, 10)))


def step_L4(s, p):
    """Aquifer-community-automation with L7 material constraint on automation."""
    flood = random.random() < (0.25 * p['flood_mult'])
    leak_amp = 1 + s.failure_rate * 5
    routine = 0.005 * leak_amp
    flood_leak = 0.08 if flood else 0
    s.aquifer_contamination += (
        (routine + flood_leak) - s.aquifer_contamination * 0.0087
    )
    s.aquifer_contamination = max(0, s.aquifer_contamination)

    if s.aquifer_contamination > 0.15:
        outmig = 0.02 + 0.18 * (s.aquifer_contamination - 0.15)
    else:
        outmig = 0.02
    s.community_pop *= (1 - outmig)

    if s.community_pop < 0.5 and not s.automation_active:
        if s.material_avail > 0.5:  # need materials to deploy automation
            s.automation_active = True
            s.automation_capacity = 0.10

    if s.automation_active:
        fail = 0.40 + s.aquifer_contamination * 0.6
        # defense capture removes materials needed for automation maintenance
        if s.defense_capture_active:
            fail += 0.15
        s.automation_capacity = max(
            0,
            min(0.40,
                s.automation_capacity * (1 - fail)
                + 0.04 * s.material_avail)
        )


def step_L5(s, p):
    """Trust / consent with L1+L4 damage + L6 instrument coupling."""
    # Visible damage tracks substrate-real conditions
    real_damage = 1 - mean([
        s.production / 13.5,
        s.community_pop,
        max(0, 1 - s.aquifer_contamination * 2),
        s.refinery_throughput / 18.4,
        s.material_avail,
    ])
    real_damage = max(0, min(1, real_damage))

    # Visibility of that damage is gated by L6 prior calibration.
    visibility_factor = 1 - s.prior_calibration * 0.7
    s.visible_damage = min(
        1.0,
        s.visible_damage
        + (real_damage - s.visible_damage) * 0.3 * visibility_factor
    )

    # Narrative pivots rare under high prior calibration
    pivot_prob = 0.04 * (1 - s.prior_calibration * 0.5)
    if random.random() < pivot_prob:
        s.official_narrative = s.visible_damage * 0.85
    else:
        drift = (s.visible_damage - s.official_narrative) * 0.15
        s.official_narrative += drift

    s.narrative_gap = max(0, s.visible_damage - s.official_narrative)
    erosion = s.narrative_gap * 0.40
    s.trust = max(0, min(1.0, s.trust - erosion))

    if s.trust < 0.10:
        s.structural_distrust = True

    if s.structural_distrust:
        s.policy_response_capacity = 0.10
    elif s.trust < 0.35:
        s.policy_response_capacity = 0.30
    else:
        s.policy_response_capacity = s.trust


def step_L6(s, p):
    """AI prior calibration with substrate observer load."""
    s.prior_calibration = max(
        0,
        min(1.0,
            s.prior_calibration
            + 0.03 * p['institutional_capture']
            - s.substrate_observers * 0.02)
    )
    if random.random() < 0.03:
        s.prior_calibration = max(0.20, s.prior_calibration - 0.15)
    s.info_quality = (0.05 * 0.85) + (0.95 * (1 - s.prior_calibration))
    s.substrate_observers = max(
        0.05,
        min(1.0,
            s.substrate_observers * (1 - 0.08 * s.prior_calibration)
            + 0.02)
    )


def step_L7(s, p):
    """Geopolitical supply chain — feeds L1 (drilling) and L3 (retool)."""
    # Sustained L3 crisis raises geopolitical tension
    crisis_pressure = 0.04 if not s.crisis_resolved else -0.01
    drift = random.gauss(0, 0.05) + p['tension_pressure'] + crisis_pressure
    s.tension = max(0, min(1.0, s.tension + drift))

    # Material disruptions
    n_disrupted = sum(
        1 for _ in range(9)
        if random.random() < s.tension * 0.5 * p['disruption_mult']
    )
    if n_disrupted > 0:
        loss = sum(random.uniform(0.05, 0.15)
                   for _ in range(n_disrupted)) / 9
        s.material_avail = max(0.10, s.material_avail - loss)

    # Defense capture
    s.defense_capture_active = (s.tension > 0.55)
    if s.defense_capture_active:
        s.material_avail *= (1 - 0.08)

    # Slow recovery if tension drops
    if s.tension < 0.4:
        s.material_avail = min(1.0, s.material_avail + 0.04)

    # Cascade amplifier
    if n_disrupted > 2:
        s.cascade_amplifier = min(3.0, s.cascade_amplifier * 1.6)
    else:
        s.cascade_amplifier = max(1.0, s.cascade_amplifier * 0.95)


# ─────────────────────────────────────────────
# RUN ONE TRAJECTORY
# ─────────────────────────────────────────────

def run_trajectory(years=10, seed=None):
    if seed is not None:
        random.seed(seed)
    s = CascadeState()
    params = {
        'decline_accel':         random.uniform(0.8, 1.5),
        'inflation_ceil':        random.uniform(0.10, 0.18),
        'escalation':            random.uniform(0.6, 1.6),
        'flood_mult':            random.uniform(0.7, 1.8),
        'institutional_capture': random.uniform(0.7, 1.5),
        'tension_pressure':      random.uniform(-0.02, 0.06),
        'disruption_mult':       random.uniform(0.7, 1.4),
    }
    trace = []
    for year in range(1, years + 1):
        # Order matters: instrument first, then physical, then market,
        # then response capacity. L6 sets visibility for L5.
        step_L6(s, params)
        step_L7(s, params)
        step_L1(s, params)
        step_L2(s, params)
        step_L3(s, params)
        step_L4(s, params)
        step_L5(s, params)
        trace.append({
            'year':                 year,
            'production':           s.production,
            'oil_price':            s.oil_price,
            'refinery_throughput':  s.refinery_throughput,
            'aquifer_contam':       s.aquifer_contamination,
            'community_pop':        s.community_pop,
            'trust':                s.trust,
            'narrative_gap':        s.narrative_gap,
            'material_avail':       s.material_avail,
            'tension':              s.tension,
            'prior_calibration':    s.prior_calibration,
            'response_capacity':    s.policy_response_capacity,
            'structural_distrust':  s.structural_distrust,
            'crisis_resolved':      s.crisis_resolved,
            'automation_active':    s.automation_active,
        })
    return trace


# ─────────────────────────────────────────────
# MODE CLASSIFICATION
# ─────────────────────────────────────────────

OUTCOME_MODES = (
    'managed_contraction',
    'stair_step_cascade',
    'honest_pivot_recovery',
    'hard_break',
)


def classify_trajectory(trace):
    """
    Return one of the four OUTCOME_MODES. Order of checks matters:
    hard_break is the most extreme, honest_pivot_recovery is the
    cleanest, stair_step_cascade is structural collapse, and
    managed_contraction is the slow-grinding default.
    """
    final = trace[-1]
    prod_ratio = final['production'] / 13.5
    pop_ratio = final['community_pop']
    trust = final['trust']
    crisis_resolved = final['crisis_resolved']
    avg_price = mean(t['oil_price'] for t in trace)
    max_contam = max(t['aquifer_contam'] for t in trace)
    min_material = min(t['material_avail'] for t in trace)

    # Hard break: sustained high price + low material + no resolution
    if avg_price > 150 and min_material < 0.3 and not crisis_resolved:
        return 'hard_break'

    # Honest pivot recovery: trust preserved, response active, substrate stable
    if trust > 0.30 and prod_ratio > 0.65 and pop_ratio > 0.7:
        return 'honest_pivot_recovery'

    # Stair-step cascade: structural distrust, contamination significant,
    # population declining, multiple loops fired
    if (final['structural_distrust']
            and pop_ratio < 0.6
            and max_contam > 0.3):
        return 'stair_step_cascade'

    # Default: managed contraction (the slow grinding case)
    return 'managed_contraction'


# ─────────────────────────────────────────────
# MONTE CARLO
# ─────────────────────────────────────────────

def monte_carlo(n=2000, years=10, master_seed=None):
    """
    Aggregate sweep across n coupled trajectories.
    master_seed : optional int making the whole sweep reproducible
                   (fixes the random state seen by each trajectory's
                   internal random.seed(i) prelude).
    """
    if master_seed is not None:
        random.seed(master_seed)

    modes = {m: 0 for m in OUTCOME_MODES}
    finals = []
    sample_per_mode = {m: [] for m in OUTCOME_MODES}

    for i in range(n):
        trace = run_trajectory(years=years, seed=i)
        mode = classify_trajectory(trace)
        modes[mode] += 1
        finals.append((trace[-1], mode))
        if len(sample_per_mode[mode]) < 3:
            sample_per_mode[mode].append(trace)

    return {
        'n': n,
        'years': years,
        'modes':       {k: v / n for k, v in modes.items()},
        'mode_counts': modes,
        'mean_final_production':  mean(f[0]['production']     for f in finals),
        'mean_final_price':       mean(f[0]['oil_price']      for f in finals),
        'mean_final_trust':       mean(f[0]['trust']          for f in finals),
        'mean_final_material':    mean(f[0]['material_avail'] for f in finals),
        'sample_per_mode': sample_per_mode,
    }


def summary(r):
    print(f"Cascade coupler — n={r['n']}, {r['years']}yr horizon")
    print()
    print("OUTCOME MODE DISTRIBUTION:")
    for mode, frac in sorted(r['modes'].items(), key=lambda x: -x[1]):
        count = r['mode_counts'][mode]
        bar = '#' * int(frac * 50)
        print(f"  {mode:28s} {frac*100:5.1f}% ({count:4d})  {bar}")
    print()
    print("AGGREGATE FINAL STATE:")
    print(f"  mean production:    "
          f"{r['mean_final_production']:.2f} mmbbl/d (baseline 13.5)")
    print(f"  mean oil price:     "
          f"${r['mean_final_price']:.2f}/bbl")
    print(f"  mean trust:         {r['mean_final_trust']:.3f}")
    print(f"  mean material avail: {r['mean_final_material']:.3f}")


if __name__ == '__main__':
    r = monte_carlo(n=2000, years=10, master_seed=2026)
    summary(r)
