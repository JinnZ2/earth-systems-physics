# constraint_accountability_chain.py
# CC0 — no rights reserved

"""
Meta-Model: Constraint Accountability Chain
DNA-like ancestry of decisions where comfort
was chosen over direct sensing.

Each node = a decision point where an actor
could have maintained signal fidelity but
chose position protection instead.

The chain is walkable in both directions:
  - Forward: trace how blindness propagated
  - Backward: find the originating comfort choice

Inheritance rules (like DNA):
  - Comfort choices propagate downstream (dominant)
  - Direct-sense choices can be overridden by
    any upstream comfort choice (recessive)
  - Accumulated comfort mutations compound
  - Reversion requires explicit constraint reimposition
"""

# ── CORE NODE ────────────────────────────────
DECISION_NODE = {
    "node_id": str,                # unique hash
    "parent_id": str,              # upstream decision this inherits from
    "timestamp": float,            # when decision occurred
    "actor": {
        "role": str,               # position in hierarchy
        "layer": int,              # authority depth
        "tenure_at_layer": float,  # time in position (comfort entrenchment)
        "comfort_captured": float, # cumulative privilege [0,1]
    },
    "decision": {
        "constraint_at_stake": str,    # what physical/operational constraint
        "ground_signal": float,        # what direct sensing showed
        "reported_signal": float,      # what actor chose to report/act on
        "delta": float,               # ground - reported (distortion magnitude)
        "choice": str,                 # "direct_sense" | "comfort_protect"
        "mechanism": str,              # how comfort was chosen:
                                       #   "attenuation" — softened the signal
                                       #   "delay" — deferred action
                                       #   "reframe" — changed the question
                                       #   "delegate_down" — pushed accountability back to ground
                                       #   "normalize" — declared deviation acceptable
                                       #   "silence" — suppressed signal entirely
    },
    "inheritance": {
        "parent_choice": str,          # what upstream decided
        "compounded": bool,            # did this amplify parent distortion
        "override_attempted": bool,    # did actor try to correct upstream
        "override_succeeded": bool,    # was correction allowed through
        "reversion_cost": float,       # energy to undo this + all downstream [0,inf]
    },
}

# ── CHAIN (THE GENOME) ──────────────────────
ACCOUNTABILITY_CHAIN = {
    "chain_id": str,               # system/org identifier
    "constraint_domain": str,      # what's being tracked (safety, ecological, financial)
    "origin_node": str,            # first decision in chain
    "terminal_node": str,          # most recent decision
    "total_nodes": int,
    "nodes": [DECISION_NODE],

    # ── GENOME METRICS ───────────────────
    "mutations": {
        "total_comfort_choices": int,
        "total_direct_sense_choices": int,
        "comfort_ratio": float,            # comfort / total — institutional DNA signature
        "longest_comfort_streak": int,     # consecutive comfort choices
        "last_direct_sense": str,          # node_id of most recent honest signal
        "drift_from_origin": float,        # cumulative distortion from first node
    },

    # ── EXPRESSION (PHENOTYPE) ───────────
    "phenotype": {
        "institutional_blindness": float,  # current signal fidelity at top
        "ratchet_depth": int,              # how many layers deep comfort is locked
        "reversion_energy": float,         # total energy to restore direct sensing
        "cascade_risk": float,             # probability of failure from current state
        "time_to_failure": float,          # estimated time before constraint violation
                                           # becomes unrecoverable
    },

    # ── EPIGENETICS ──────────────────────
    # external pressures that activate/silence
    # comfort vs direct-sense expression
    "epigenetic_factors": [
        {
            "factor": str,         # "regulatory_pressure" | "market_shock" |
                                   # "personnel_change" | "public_exposure" |
                                   # "cascade_event" | "resource_scarcity"
            "effect": str,         # "activates_direct_sense" | "reinforces_comfort"
            "magnitude": float,    # [0,1]
            "timestamp": float,
        }
    ],
}
