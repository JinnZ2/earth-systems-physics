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

loop3_refinery_config_trap.py
    light sweet glut -> refineries retooled to light -> Permian
    depletes -> no flexibility back to heavy -> import dependency
    -> geopolitical exposure -> price spike -> refineries can't
    process spike feedstock (configuration lock-in trap).

loop4_aquifer_community_automation.py
    produced-water leakage + flood overflow -> aquifer + surface
    water contamination -> community outmigration -> workforce
    gone -> automation attempted -> automation fails on rough
    terrain + sensor drift + radioactive corrosion -> production
    drops -> remaining wells extracted harder -> more failures ->
    more contamination. Monte Carlo aggregator across n stochastic
    trajectories; aggregate stats are the activation predicate.

Each module is standalone: stdlib only, dataclass + step + run +
activation predicate, runnable as a script with a fixed seed for
reproducibility.

CC0. JinnZ2 / oil_phase_shift.
"""
