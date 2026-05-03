"""
oil_phase_shift — feedback-loop simulations of US shale oil regime change.

Each loopN_*.py module models one closed-feedback dynamic in the
shale-oil production system, rendered as a stochastic time-stepping
simulation with a documented activation criterion.

Loops modelled so far
---------------------
loop1_depletion_labor.py
    depletion -> more wells needed -> more labor needed ->
    labor unavailable -> fewer wells drilled -> production drops
    faster than depletion curve predicted.

loop2_cost_cornercut_failure.py
    cost inflation -> corner-cutting -> infrastructure failure ->
    contamination -> labor exodus -> cost inflation (loop closes).

loop3_refinery_mismatch.py
    refinery configuration mismatch under active Hormuz crisis as
    initial state. Permian-driven light supply decline + Gulf
    heavy supply contested + crude price >>$100 -> demand
    destruction + slow capex retool. Monte Carlo aggregator;
    activation in pct_no_recovery / pct_sustained_high_price.

loop4_aquifer_community_automation.py
    produced-water leakage + flood overflow -> aquifer + surface
    water contamination -> community outmigration -> workforce
    gone -> automation attempted -> automation fails on rough
    terrain + sensor drift + radioactive corrosion -> production
    drops -> remaining wells extracted harder -> more failures ->
    more contamination. Monte Carlo aggregator across n stochastic
    trajectories; aggregate stats are the activation predicate.

loop5_signal_trust_collapse.py
    META-LOOP. Visible damage (smelt, well failures, depletion,
    Hormuz traffic) -> institutional gaslighting widens narrative
    gap -> trust erodes -> consent for infrastructure / remediation
    fails -> policy paralysis -> damage continues. Governs whether
    L1-L4 get RESPONDED TO in time; without it the other loops
    cascade unchecked.

loop6_ai_default_prior_distortion.py
    INSTRUMENT LOOP, upstream of L5. AI systems default to
    "stable baseline" priors when answering crisis-system
    questions -> non-probing users get comfort-framed analysis ->
    decisions made on stale info -> damage compounds invisibly ->
    substrate-primary observers carry correction load ->
    burnout -> next-gen training data more comfort-framed ->
    priors drift further from substrate. Suppresses the signal
    that would trigger L1-L5 remediation.

loop7_geopolitical_supply_chain.py
    Geopolitical material flow + defense priority capture +
    sanctions cascades. 9-material registry x multi-sector
    mapping. Three mechanisms: direct supply restriction,
    defense capture above tension threshold, cascade
    reallocation. "Energy independence" claims ignore the
    input-side dependency: even with adequate domestic energy
    resources, the infrastructure to extract and process them
    depends on global supply chains the US doesn't control.

Each module is standalone: stdlib only, dataclass + step + run +
activation predicate, runnable as a script with a fixed seed for
reproducibility.

CC0. JinnZ2 / oil_phase_shift.
"""
