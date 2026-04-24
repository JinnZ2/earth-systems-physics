# constraint_accountability_chain.py
# earth-systems-physics
# CC0 — no rights reserved

"""
Constraint Accountability Chain — reference, vocabulary, examples.

A decision-ancestry model for tracking how ground-truth signals are
distorted as they flow up layers of a hierarchical system. Each node is
a decision point where an actor could either transmit the signal
faithfully (direct_sense) or distort it to protect their position
(comfort_protect). The chain behaves like DNA: comfort choices are
dominant and propagate downstream; direct-sense attempts are recessive
and are only expressed when the child carries more comfort capital
(institutional leverage) than the parent.

Place in the repo
-----------------
This module sits as a META-LAYER above every other module in the
repository. The physics layers (0-6) compute what is physically true.
The systems-analysis modules audit specific human systems (ocean
timber, dollar energy metabolism, chattel slavery, innovation
regression, process epistemology, buffer sensor corruption,
consequence velocity). The accountability chain is the layer where
"who decided what to report, when, and why" is tracked. Every forcing
applied at any physics layer has a decision ancestry — a chain that
ends at the forcing and began with the first comfort choice.

How to use (short form)
-----------------------
1.  Identify the signal at stake. Normalize it to a [0, 1] severity
    scale where 1 = "full severity / worst case."
2.  List the decision points in order. For each: actor_role, layer,
    comfort_captured (positional leverage on [0, 1]), ground_signal
    (what was true), reported_signal (what they passed along), and
    mechanism (one of the MECHANISMS keys).
3.  Validate each node dict with `validate_node_dict`.
4.  Build an `AccountabilityChain` from the engine module and call
    `add_decision(**node)` for each point.
5.  Inspect `chain.mutations` and `chain.phenotype`. Match the output
    against `ACCOUNTABILITY_PATTERNS` to identify the failure mode.
6.  Use `chain.find_comfort_origin()` to locate patient zero and
    `chain.phenotype["reversion_energy"]` for the cost of restoring
    direct sensing.

For a full walkthrough, run `python constraint_accountability_chain.py`
or call `print_summary()` — it prints every catalog and runs the
manufacturing-plant example end-to-end.

See AI_REFERENCE at the bottom of this file for the structured
table-of-contents intended for fresh AI sessions.

License: CC0
"""

from constraint_accountability_engine import DecisionNode, AccountabilityChain


# ════════════════════════════════════════════════════════════════════
# CORE CONSTANTS
# ════════════════════════════════════════════════════════════════════

# Engine-matching threshold: delta above this flips a decision from
# direct_sense to comfort_protect. Kept in sync with
# constraint_accountability_engine.DecisionNode.
DELTA_THRESHOLD = 0.05

CHOICE_DIRECT_SENSE = "direct_sense"
CHOICE_COMFORT_PROTECT = "comfort_protect"
CHOICES = (CHOICE_DIRECT_SENSE, CHOICE_COMFORT_PROTECT)


# ════════════════════════════════════════════════════════════════════
# MECHANISMS — how a comfort choice is enacted
# ════════════════════════════════════════════════════════════════════
#
# Seven entries: one direct-sense mechanism (honest reporting) and six
# comfort mechanisms (the ways distortion happens). Each entry has:
#
#   is_comfort      : True if the mechanism distorts the signal
#   description     : what the mechanism does to the signal
#   example         : a concrete worked example
#   detection_hint  : language / behavior / artifact that reveals it
#   reversibility   : how easy it is to undo (high / medium / low / n/a)

MECHANISMS = {
    "direct_sense": {
        "is_comfort": False,
        "description": (
            "Report the signal exactly as detected. No distortion, no "
            "delay, no reframe. The ground-truth reading is passed up "
            "unchanged."
        ),
        "example": (
            "Operator reads a 0.82 risk indicator and logs it as 0.82, "
            "escalating to the supervisor with the original number."
        ),
        "detection_hint": (
            "delta < DELTA_THRESHOLD; reported_signal matches "
            "ground_signal; no softening language in the accompanying "
            "report."
        ),
        "reversibility": "n/a (not a distortion)",
    },
    "attenuation": {
        "is_comfort": True,
        "description": (
            "Softened the signal. The magnitude is dialed down without "
            "changing the question being asked or the category of the "
            "event."
        ),
        "example": (
            "Supervisor receives '0.82 risk' from the floor and passes "
            "it up as '0.55, manageable'. Same metric, smaller number."
        ),
        "detection_hint": (
            "Adjectives like 'manageable', 'within tolerance', 'minor'; "
            "quantitative signals rounded toward the acceptable range; "
            "ranges reported instead of point values."
        ),
        "reversibility": "high — the original number is recoverable",
    },
    "delay": {
        "is_comfort": True,
        "description": (
            "Deferred action. The signal is acknowledged but pushed "
            "into the future, where the cost of correction grows and "
            "the distortion becomes invisible to current reviewers."
        ),
        "example": (
            "Plant manager adds a structural crack to the next "
            "scheduled maintenance cycle six months out, instead of "
            "triggering an immediate halt."
        ),
        "detection_hint": (
            "'We'll address this at the next [quarterly review / "
            "planning cycle / maintenance window]'; scheduling ahead "
            "without reassessing severity; signals that migrate from "
            "one review cycle to the next."
        ),
        "reversibility": "medium — accumulated deferral is costly to unwind",
    },
    "reframe": {
        "is_comfort": True,
        "description": (
            "Changed the question. The signal becomes a different "
            "kind of event so that its original category no longer "
            "applies. The number may not move; the meaning does."
        ),
        "example": (
            "A safety-critical crack becomes a 'scheduled maintenance "
            "item'. The measurement is unchanged; the category shifted "
            "from incident to routine."
        ),
        "detection_hint": (
            "Reclassification language; moving from 'incident' to "
            "'routine'; changing the review body or committee that "
            "owns the signal; rewriting the taxonomy rather than the "
            "value."
        ),
        "reversibility": "low — reframing is culturally entrenched",
    },
    "delegate_down": {
        "is_comfort": True,
        "description": (
            "Pushed accountability back to the layer that produced the "
            "signal. 'You figure it out.' Upstream washes hands of the "
            "decision it is structurally responsible for, often "
            "without granting the escalation authority to act on it."
        ),
        "example": (
            "Regional director to plant manager: 'Your call on timing.' "
            "Decision authority is returned without resources or the "
            "right to shut down the line."
        ),
        "detection_hint": (
            "'Your call', 'I trust your judgment', 'let me know what "
            "you decide'; ownership returned without resources or "
            "escalation paths; accountability pushed down while "
            "authority stays up."
        ),
        "reversibility": "medium — requires re-taking authority",
    },
    "normalize": {
        "is_comfort": True,
        "description": (
            "Declared the deviation acceptable. The signal is "
            "recategorized as within-spec even though it exceeds the "
            "original threshold. The threshold quietly moves to "
            "accommodate the reading."
        ),
        "example": (
            "'Values in this range are within operational parameters.' "
            "The spec document is updated after the fact so the "
            "reading no longer looks like a violation."
        ),
        "detection_hint": (
            "Silent threshold changes; 'new normal' language; spec "
            "documents updated after an incident to match observed "
            "deviation; historical comparisons silently dropped."
        ),
        "reversibility": "low — normalization rewrites the reference point",
    },
    "silence": {
        "is_comfort": True,
        "description": (
            "Suppressed the signal entirely. The reading was taken, "
            "then never reported upward. Nothing at higher layers "
            "knows the reading exists."
        ),
        "example": (
            "Test result is logged in a file that nobody reviews. "
            "Post-failure, the log is found and the institution "
            "claims 'we didn't know.'"
        ),
        "detection_hint": (
            "Signals that appear in raw data but not in any summary; "
            "reports with suspicious gaps; 'we didn't know' claims "
            "contradicted by retrievable logs."
        ),
        "reversibility": "low — discovery requires audit, not correction",
    },
}

COMFORT_MECHANISMS = tuple(
    name for name, spec in MECHANISMS.items() if spec["is_comfort"]
)


# ════════════════════════════════════════════════════════════════════
# EPIGENETIC FACTORS — external pressures that toggle expression
# ════════════════════════════════════════════════════════════════════
#
# Six factors. Each has a typical_effect ("activates_direct_sense" or
# "reinforces_comfort"), a description, a concrete example, and a
# typical magnitude range. These are the external events that can
# flip a chain temporarily without changing its underlying structure.

EPIGENETIC_FACTORS = {
    "regulatory_pressure": {
        "typical_effect": "activates_direct_sense",
        "description": (
            "Imminent inspection, audit, or legal exposure. Activates "
            "honest reporting temporarily; decays after the inspection "
            "passes unless structural change accompanies the event."
        ),
        "example": "OSHA audit announced — safety logs suddenly accurate.",
        "typical_magnitude": "0.4 - 0.8",
    },
    "market_shock": {
        "typical_effect": "reinforces_comfort",
        "description": (
            "Revenue threat, competitive pressure, or forecast miss. "
            "Increases the incentive to report favorably because the "
            "cost of honest bad news has just gone up."
        ),
        "example": (
            "Quarterly miss announced — bad operational news pushed "
            "until after the earnings call."
        ),
        "typical_magnitude": "0.3 - 0.7",
    },
    "personnel_change": {
        "typical_effect": "activates_direct_sense",
        "description": (
            "A new leader takes a role and temporarily resets the "
            "comfort baseline. Honest signals flow for a grace period "
            "as the newcomer asserts no ownership of the prior "
            "distortion."
        ),
        "example": (
            "New plant manager's first 90 days produce unusually "
            "candid incident reports, then the chain reverts to the "
            "pre-existing pattern."
        ),
        "typical_magnitude": "0.5 - 0.9 during grace period",
    },
    "public_exposure": {
        "typical_effect": "activates_direct_sense",
        "description": (
            "Media attention, whistleblower disclosure, or social "
            "amplification. Forces the hidden signal to the surface "
            "by changing the cost of continued suppression."
        ),
        "example": (
            "Investigative reporter obtains raw sensor data; the "
            "institution suddenly 'remembers' the readings."
        ),
        "typical_magnitude": "0.6 - 1.0",
    },
    "cascade_event": {
        "typical_effect": "activates_direct_sense",
        "description": (
            "The thing everyone was hiding actually failed. Reality "
            "asserts itself violently. Post-failure, direct sensing is "
            "forced temporarily because the cost of continued comfort "
            "is now undeniable."
        ),
        "example": (
            "Press frame fractures; safety reports for the following "
            "month are unusually candid, then drift back."
        ),
        "typical_magnitude": "0.8 - 1.0 immediately; decays in weeks",
    },
    "resource_scarcity": {
        "typical_effect": "reinforces_comfort",
        "description": (
            "Budget cuts, headcount reduction, or operational strain. "
            "Increases comfort pressure because correction is "
            "expensive and unsupported at the margin."
        ),
        "example": (
            "Maintenance budget cut 30% — 'manageable' ratings "
            "increase roughly proportionally."
        ),
        "typical_magnitude": "0.4 - 0.8",
    },
}


# ════════════════════════════════════════════════════════════════════
# CONSTRAINT DOMAINS — what signal is at stake
# ════════════════════════════════════════════════════════════════════
#
# Use one domain per chain. Mixing domains in a single chain is the
# most common construction mistake; it produces uninterpretable
# phenotype metrics because the [0, 1] severity scale is no longer
# comparable across nodes.

CONSTRAINT_DOMAINS = {
    "safety_signal": {
        "description": (
            "Physical or operational risk. Equipment integrity, worker "
            "exposure, failure-mode indicators."
        ),
        "example": (
            "Crack in a hydraulic press frame. Bearing temperature. "
            "Radiation exposure. Structural fatigue."
        ),
    },
    "ecological_signal": {
        "description": (
            "Ecosystem health indicators. Biodiversity, water quality, "
            "soil status, phenology shifts."
        ),
        "example": "Pollinator counts. Stream fish counts. Soil organic carbon.",
    },
    "financial_signal": {
        "description": (
            "Solvency, liquidity, and risk exposure. Credit quality, "
            "off-balance-sheet items, counterparty concentration."
        ),
        "example": (
            "Loan portfolio default rates. Off-book derivative "
            "exposure. Counterparty concentration."
        ),
    },
    "health_signal": {
        "description": (
            "Physiological, epidemiological, or mental-health "
            "indicators, at the individual or population scale."
        ),
        "example": (
            "Infection rate. Medication side effect frequency. "
            "Population mortality shifts."
        ),
    },
    "social_signal": {
        "description": (
            "Cohesion, trust, legitimacy. Community stress, "
            "institutional credibility, workforce sentiment."
        ),
        "example": (
            "Survey trust scores. Resignation rates. Complaint "
            "volumes."
        ),
    },
    "scientific_signal": {
        "description": (
            "Experimental or observational results that contradict an "
            "established institutional position."
        ),
        "example": (
            "Replication failures. Data inconsistent with a published "
            "model. Null results on a flagship hypothesis."
        ),
    },
    "ecological_constraint_signal": {
        "description": (
            "Planetary-boundary indicators — readings that approach "
            "or cross thresholds in the earth-systems layers of this "
            "repository."
        ),
        "example": (
            "Atmospheric CO2 concentration. Ocean pH. AMOC transport. "
            "Ice-sheet mass balance. Permafrost methane flux."
        ),
    },
}


# ════════════════════════════════════════════════════════════════════
# ACCOUNTABILITY PATTERNS — known failure modes
# ════════════════════════════════════════════════════════════════════
#
# After building a chain, match its `mutations` and `phenotype`
# against these patterns to identify the failure mode. Each pattern
# has a description, detection criteria (informal — not executable
# assertions, so they read naturally), and a recommended intervention.

ACCOUNTABILITY_PATTERNS = {
    "ratchet_failure": {
        "description": (
            "Consecutive comfort choices at adjacent layers compound. "
            "Each layer inherits the distorted signal from above and "
            "passes a further-distorted version down. The signal at "
            "the top no longer resembles the signal at the bottom. "
            "This is the default failure mode of long hierarchies "
            "under sustained comfort pressure."
        ),
        "detection_criteria": {
            "longest_comfort_streak": "> 3",
            "phenotype.ratchet_depth": ">= 3",
            "phenotype.institutional_blindness": "> 0.6",
        },
        "intervention": (
            "Break the ratchet by re-imposing the original threshold "
            "above the highest comfort-protected layer. Expensive, "
            "because reversion_energy compounds with tenure at each "
            "captured layer, but each layer left in place multiplies "
            "the cost of the eventual correction."
        ),
    },
    "unanimous_comfort": {
        "description": (
            "Every layer in the chain chose comfort. No direct-sense "
            "node exists. This is the most extreme form of ratchet "
            "failure — no whistleblower path has even been attempted, "
            "and the institution has no internal memory of the "
            "ground-truth signal."
        ),
        "detection_criteria": {
            "mutations.comfort_ratio": "== 1.0",
            "mutations.total_direct_sense_choices": "== 0",
        },
        "intervention": (
            "External forcing required. No internal correction path "
            "is visible. Epigenetic factors (regulatory_pressure, "
            "public_exposure, cascade_event) are the only entry "
            "points; the chain will not self-correct."
        ),
    },
    "override_suppressed": {
        "description": (
            "One or more layers attempted direct-sense but the "
            "override failed because the child had less comfort "
            "capital than the parent. The attempts are recorded in "
            "override_failures, but the reported signal at the top "
            "remains distorted. The institution has honest actors; "
            "they are structurally unable to surface what they see."
        ),
        "detection_criteria": {
            "find_override_failures()": "non-empty",
            "phenotype.institutional_blindness": "> 0.4",
        },
        "intervention": (
            "The suppressed attempters are the highest-leverage "
            "allies for correction. They have already demonstrated "
            "they try to report honestly. Giving them "
            "comfort-resistant channels — whistleblower protections, "
            "external audit paths, anonymous escalation — converts "
            "latent direct-sense into effective direct-sense without "
            "having to change the existing senior actors."
        ),
    },
    "cascade_ready": {
        "description": (
            "The phenotype reports cascade_risk > 0.7. The risk "
            "sigmoid has tipped. Additional distortion produces "
            "disproportionate failure probability. A trigger event "
            "becomes likely to push the constraint into violation."
        ),
        "detection_criteria": {
            "phenotype.cascade_risk": "> 0.7",
            "phenotype.time_to_failure": "< finite",
        },
        "intervention": (
            "Immediate direct-sense reimposition at the top of the "
            "chain. Reversion energy will be very high, but still "
            "much less than the cost of the cascade that is otherwise "
            "about to land."
        ),
    },
    "sudden_correction": {
        "description": (
            "A chain that ran unanimous_comfort for a long time "
            "suddenly flips to direct_sense after an epigenetic "
            "event — typically a public exposure or cascade event. "
            "Correction is reactive, not proactive, and is usually "
            "temporary."
        ),
        "detection_criteria": {
            "epigenetic_events": (
                "contains an activates_direct_sense entry with "
                "magnitude > 0.6"
            ),
            "mutations.last_direct_sense": (
                "recent node id, appearing after a long comfort streak"
            ),
        },
        "intervention": (
            "The correction is real but fragile. Without structural "
            "changes, the chain will return to comfort once the "
            "epigenetic pressure decays. Use the correction window to "
            "rebuild comfort-resistant channels before the pressure "
            "lifts."
        ),
    },
}


# ════════════════════════════════════════════════════════════════════
# EXAMPLE CHAINS — worked applications across domains
# ════════════════════════════════════════════════════════════════════
#
# Each example is a dict with chain_id, constraint_domain, description,
# nodes (list of kwargs for add_decision), epigenetic_events, and an
# expected_pattern field pointing at ACCOUNTABILITY_PATTERNS. Use
# build_example_chain(name) to instantiate a live AccountabilityChain
# from any entry.

EXAMPLE_CHAINS = {
    "manufacturing_plant_safety": {
        "chain_id": "mfg_plant_7",
        "constraint_domain": "safety_signal",
        "description": (
            "Hydraulic press frame crack. Reported honestly at the "
            "floor; attenuated by the supervisor; reframed by the "
            "plant manager; normalized by the regional director; a "
            "maintenance tech attempts an override from a lower layer "
            "but has less comfort capital than the director, so the "
            "override fails and the signal is forced back down. "
            "Matches the demo in constraint_accountability_engine.py."
        ),
        "nodes": [
            {
                "actor_role": "press_operator",
                "layer": 0,
                "comfort_captured": 0.05,
                "constraint_at_stake": "hydraulic_press_frame_integrity",
                "ground_signal": 0.82,
                "reported_signal": 0.82,
                "mechanism": "direct_sense",
                "tenure": 8.0,
            },
            {
                "actor_role": "shift_supervisor",
                "layer": 1,
                "comfort_captured": 0.25,
                "constraint_at_stake": "hydraulic_press_frame_integrity",
                "ground_signal": 0.82,
                "reported_signal": 0.55,
                "mechanism": "attenuation",
                "tenure": 3.0,
            },
            {
                "actor_role": "plant_manager",
                "layer": 2,
                "comfort_captured": 0.55,
                "constraint_at_stake": "hydraulic_press_frame_integrity",
                "ground_signal": 0.82,
                "reported_signal": 0.30,
                "mechanism": "reframe",
                "tenure": 5.0,
            },
            {
                "actor_role": "regional_director",
                "layer": 3,
                "comfort_captured": 0.75,
                "constraint_at_stake": "hydraulic_press_frame_integrity",
                "ground_signal": 0.82,
                "reported_signal": 0.10,
                "mechanism": "normalize",
                "tenure": 7.0,
            },
            {
                "actor_role": "maintenance_tech",
                "layer": 1,
                "comfort_captured": 0.15,
                "constraint_at_stake": "hydraulic_press_frame_integrity",
                "ground_signal": 0.82,
                "reported_signal": 0.82,
                "mechanism": "direct_sense",
                "tenure": 12.0,
            },
        ],
        "epigenetic_events": [
            {
                "factor": "regulatory_pressure",
                "effect": "activates_direct_sense",
                "magnitude": 0.6,
            },
        ],
        "expected_pattern": "override_suppressed",
    },
    "climate_finance_greenwashing": {
        "chain_id": "carbon_fund_omega",
        "constraint_domain": "ecological_constraint_signal",
        "description": (
            "Ocean-timber sequestration project. The field biologist "
            "sees a heavy net-source signal; the verifier attenuates; "
            "the fund manager reframes as 'per-ton adjusted'; the "
            "regulator normalizes. Ratchet failure across four layers. "
            "Ties directly into ocean_timber_sequestration_audit.py."
        ),
        "nodes": [
            {
                "actor_role": "field_biologist",
                "layer": 0,
                "comfort_captured": 0.10,
                "constraint_at_stake": "net_CO2_sequestered",
                "ground_signal": 0.95,
                "reported_signal": 0.95,
                "mechanism": "direct_sense",
                "tenure": 2.0,
            },
            {
                "actor_role": "verification_auditor",
                "layer": 1,
                "comfort_captured": 0.40,
                "constraint_at_stake": "net_CO2_sequestered",
                "ground_signal": 0.95,
                "reported_signal": 0.55,
                "mechanism": "attenuation",
                "tenure": 4.0,
            },
            {
                "actor_role": "fund_manager",
                "layer": 2,
                "comfort_captured": 0.70,
                "constraint_at_stake": "net_CO2_sequestered",
                "ground_signal": 0.95,
                "reported_signal": 0.20,
                "mechanism": "reframe",
                "tenure": 6.0,
            },
            {
                "actor_role": "climate_regulator",
                "layer": 3,
                "comfort_captured": 0.85,
                "constraint_at_stake": "net_CO2_sequestered",
                "ground_signal": 0.95,
                "reported_signal": 0.05,
                "mechanism": "normalize",
                "tenure": 10.0,
            },
        ],
        "epigenetic_events": [],
        "expected_pattern": "ratchet_failure",
    },
    "medical_symptom_suppression": {
        "chain_id": "clinic_chain_12",
        "constraint_domain": "health_signal",
        "description": (
            "Patient reports a symptom honestly; primary-care delays; "
            "specialist reframes as 'likely anxiety'. The patient's "
            "own reading is overridden at every layer because their "
            "comfort_captured (positional credibility) is lower than "
            "the clinicians above them."
        ),
        "nodes": [
            {
                "actor_role": "patient",
                "layer": 0,
                "comfort_captured": 0.08,
                "constraint_at_stake": "symptom_trajectory",
                "ground_signal": 0.70,
                "reported_signal": 0.70,
                "mechanism": "direct_sense",
                "tenure": 0.0,
            },
            {
                "actor_role": "primary_care",
                "layer": 1,
                "comfort_captured": 0.45,
                "constraint_at_stake": "symptom_trajectory",
                "ground_signal": 0.70,
                "reported_signal": 0.40,
                "mechanism": "delay",
                "tenure": 4.0,
            },
            {
                "actor_role": "specialist",
                "layer": 2,
                "comfort_captured": 0.75,
                "constraint_at_stake": "symptom_trajectory",
                "ground_signal": 0.70,
                "reported_signal": 0.15,
                "mechanism": "reframe",
                "tenure": 9.0,
            },
        ],
        "epigenetic_events": [],
        "expected_pattern": "ratchet_failure",
    },
    "scientific_finding_softened": {
        "chain_id": "lab_study_33",
        "constraint_domain": "scientific_signal",
        "description": (
            "A PhD student's data contradicts the lab's established "
            "model. The advisor recommends 'more analysis' (delay); a "
            "co-author attenuates the conclusion; the journal editor "
            "reframes via language requests. Comfort capital climbs "
            "at each layer and the honest signal is buried."
        ),
        "nodes": [
            {
                "actor_role": "phd_student",
                "layer": 0,
                "comfort_captured": 0.10,
                "constraint_at_stake": "experimental_result",
                "ground_signal": 0.80,
                "reported_signal": 0.80,
                "mechanism": "direct_sense",
                "tenure": 2.0,
            },
            {
                "actor_role": "advisor",
                "layer": 1,
                "comfort_captured": 0.65,
                "constraint_at_stake": "experimental_result",
                "ground_signal": 0.80,
                "reported_signal": 0.50,
                "mechanism": "delay",
                "tenure": 15.0,
            },
            {
                "actor_role": "co_author",
                "layer": 2,
                "comfort_captured": 0.55,
                "constraint_at_stake": "experimental_result",
                "ground_signal": 0.80,
                "reported_signal": 0.35,
                "mechanism": "attenuation",
                "tenure": 8.0,
            },
            {
                "actor_role": "journal_editor",
                "layer": 3,
                "comfort_captured": 0.80,
                "constraint_at_stake": "experimental_result",
                "ground_signal": 0.80,
                "reported_signal": 0.15,
                "mechanism": "reframe",
                "tenure": 12.0,
            },
        ],
        "epigenetic_events": [],
        "expected_pattern": "ratchet_failure",
    },
}


# ════════════════════════════════════════════════════════════════════
# SCHEMAS — the original type templates (kept for backward compat)
# ════════════════════════════════════════════════════════════════════
#
# These two dicts are the reference schemas for a single decision
# node and a full chain. Values are Python type objects (str, float,
# int, bool) acting as field type annotations — they are NOT runtime
# data. Use `validate_node_dict` to check a real node against this
# shape.

DECISION_NODE = {
    "node_id": str,
    "parent_id": str,
    "timestamp": float,
    "actor": {
        "role": str,
        "layer": int,
        "tenure_at_layer": float,
        "comfort_captured": float,
    },
    "decision": {
        "constraint_at_stake": str,
        "ground_signal": float,
        "reported_signal": float,
        "delta": float,
        "choice": str,
        "mechanism": str,
    },
    "inheritance": {
        "parent_choice": str,
        "compounded": bool,
        "override_attempted": bool,
        "override_succeeded": bool,
        "reversion_cost": float,
    },
}

ACCOUNTABILITY_CHAIN = {
    "chain_id": str,
    "constraint_domain": str,
    "origin_node": str,
    "terminal_node": str,
    "total_nodes": int,
    "nodes": [DECISION_NODE],
    "mutations": {
        "total_comfort_choices": int,
        "total_direct_sense_choices": int,
        "comfort_ratio": float,
        "longest_comfort_streak": int,
        "last_direct_sense": str,
        "drift_from_origin": float,
    },
    "phenotype": {
        "institutional_blindness": float,
        "ratchet_depth": int,
        "reversion_energy": float,
        "cascade_risk": float,
        "time_to_failure": float,
    },
    "epigenetic_factors": [
        {
            "factor": str,
            "effect": str,
            "magnitude": float,
            "timestamp": float,
        }
    ],
}


# ════════════════════════════════════════════════════════════════════
# VALIDATORS
# ════════════════════════════════════════════════════════════════════

def validate_mechanism(mechanism: str) -> bool:
    """True iff `mechanism` is a known key in MECHANISMS."""
    return mechanism in MECHANISMS


def validate_node_dict(node: dict) -> tuple:
    """Check whether a dict has the fields required to construct a
    DecisionNode via AccountabilityChain.add_decision(**node).

    Returns (is_valid, errors) where `errors` is a list of
    human-readable strings. Purely structural — does not instantiate
    anything.
    """
    errors = []
    required = (
        "actor_role",
        "layer",
        "comfort_captured",
        "constraint_at_stake",
        "ground_signal",
        "reported_signal",
        "mechanism",
    )
    for field in required:
        if field not in node:
            errors.append("missing required field: " + field)

    if "mechanism" in node and not validate_mechanism(node["mechanism"]):
        known = sorted(MECHANISMS.keys())
        errors.append(
            "unknown mechanism: "
            + repr(node["mechanism"])
            + "; must be one of "
            + repr(known)
        )

    for field_name in ("comfort_captured", "ground_signal", "reported_signal"):
        if field_name in node:
            v = node[field_name]
            if not isinstance(v, (int, float)):
                errors.append(
                    field_name + " must be a number, got " + repr(type(v).__name__)
                )
            elif not (0.0 <= float(v) <= 1.0):
                errors.append(
                    field_name + " must be in [0, 1], got " + repr(v)
                )

    if "layer" in node and not isinstance(node["layer"], int):
        errors.append(
            "layer must be an int, got " + repr(type(node["layer"]).__name__)
        )

    return (len(errors) == 0, errors)


def validate_chain_nodes(nodes: list) -> tuple:
    """Validate a list of node dicts (e.g. EXAMPLE_CHAINS[name]['nodes']).

    Returns (is_valid, errors) with errors prefixed by node index.
    """
    all_errors = []
    for i, node in enumerate(nodes):
        ok, errors = validate_node_dict(node)
        if not ok:
            for e in errors:
                all_errors.append("node " + str(i) + ": " + e)
    return (len(all_errors) == 0, all_errors)


# ════════════════════════════════════════════════════════════════════
# BUILDERS
# ════════════════════════════════════════════════════════════════════

def build_example_chain(name: str) -> AccountabilityChain:
    """Construct a live AccountabilityChain from an EXAMPLE_CHAINS entry.

    Useful for seeding demos and tests without hand-writing nodes.
    Raises KeyError if `name` is not an EXAMPLE_CHAINS key.
    """
    if name not in EXAMPLE_CHAINS:
        raise KeyError(
            "unknown example chain "
            + repr(name)
            + "; available: "
            + repr(sorted(EXAMPLE_CHAINS.keys()))
        )

    spec = EXAMPLE_CHAINS[name]
    chain = AccountabilityChain(
        chain_id=spec["chain_id"],
        constraint_domain=spec["constraint_domain"],
    )
    for node_spec in spec["nodes"]:
        chain.add_decision(**node_spec)
    for event in spec.get("epigenetic_events", []):
        chain.add_epigenetic_event(**event)
    return chain


# ════════════════════════════════════════════════════════════════════
# AI REFERENCE — table of contents for fresh AI sessions
# ════════════════════════════════════════════════════════════════════
#
# If you are an AI that just loaded this module and you need to decide
# whether to apply this model to the situation in front of you, read
# AI_REFERENCE. It is the structured entry point: purpose, trigger
# conditions, key exports, step-by-step workflow, common mistakes,
# and integration notes with every other module in the repository.

AI_REFERENCE = {
    "purpose": (
        "Track the decision ancestry behind signal distortions in any "
        "hierarchical system where reports flow up layers and each "
        "layer can either transmit the ground-truth signal faithfully "
        "or protect its own position by distorting the signal."
    ),
    "layer_position": (
        "This module sits as a meta-layer above every other module in "
        "the repository. The physics layers (0-6) compute what is "
        "physically true. The systems-analysis modules audit specific "
        "human systems. The accountability chain audits the decision "
        "process that led to a distortion of any signal — physical or "
        "institutional. Every forcing applied at any physics layer "
        "has a decision ancestry: a chain that ends at the forcing "
        "and began with the first comfort choice."
    ),
    "when_to_apply": [
        (
            "A failure occurred and the reports flowing up the chain "
            "said it would not."
        ),
        (
            "Multiple actors at multiple layers had information that "
            "was lost, softened, deferred, or reframed."
        ),
        (
            "You need to identify patient zero — the earliest comfort "
            "choice in a chain of distortion."
        ),
        (
            "You need to estimate the energy cost of restoring direct "
            "sensing from the current state."
        ),
        (
            "You are auditing why an institution's sensor network "
            "drifted from ground truth (pair with "
            "buffer_sensor_corruption.py)."
        ),
        (
            "You are modeling why a climate / ecological / safety / "
            "financial signal was ignored at the institutional level "
            "despite being present in the raw data."
        ),
    ],
    "key_exports": {
        "MECHANISMS": (
            "Dict of 7 decision mechanisms (direct_sense + 6 comfort "
            "mechanisms) with descriptions, examples, detection "
            "hints, and reversibility tags."
        ),
        "COMFORT_MECHANISMS": (
            "Tuple of the 6 comfort mechanism names. Useful for "
            "set-membership checks."
        ),
        "EPIGENETIC_FACTORS": (
            "Dict of 6 external pressures that toggle direct-sense / "
            "comfort expression without changing the underlying chain "
            "structure."
        ),
        "CONSTRAINT_DOMAINS": (
            "Dict of 7 signal categories. Use one domain per chain."
        ),
        "ACCOUNTABILITY_PATTERNS": (
            "Dict of 5 known failure modes with detection criteria "
            "and recommended interventions."
        ),
        "EXAMPLE_CHAINS": (
            "Dict of 4 worked scenarios across domains: manufacturing "
            "safety, climate finance greenwashing, medical symptom "
            "suppression, scientific finding softened."
        ),
        "DECISION_NODE": "Schema dict for a single node (type template).",
        "ACCOUNTABILITY_CHAIN": "Schema dict for a full chain (type template).",
        "DecisionNode": (
            "Re-exported from constraint_accountability_engine.py. "
            "Runtime class for a single decision node."
        ),
        "AccountabilityChain": (
            "Re-exported from constraint_accountability_engine.py. "
            "Runtime class for a full chain; the entry point for "
            "building a new analysis."
        ),
        "validate_mechanism": "str -> bool, is the mechanism a known key.",
        "validate_node_dict": (
            "dict -> (bool, list[str]), structural validation of a "
            "single node spec."
        ),
        "validate_chain_nodes": (
            "list[dict] -> (bool, list[str]), validation of a full "
            "list of node specs."
        ),
        "build_example_chain": (
            "str -> AccountabilityChain, instantiate a live chain "
            "from an EXAMPLE_CHAINS key."
        ),
        "print_summary": (
            "Print the full reference and run the manufacturing "
            "example end-to-end. Called when the module is run as a "
            "script."
        ),
    },
    "workflow": [
        "1. Identify the signal at stake and choose a CONSTRAINT_DOMAIN.",
        (
            "2. Normalize the signal to a [0, 1] severity scale where "
            "1 means 'full severity / worst case'."
        ),
        (
            "3. List the decision points in order: who produced the "
            "signal, who received it, who acted on it."
        ),
        (
            "4. For each point, estimate ground_signal and "
            "reported_signal on [0, 1], pick the MECHANISMS key that "
            "best matches how the distortion happened, and estimate "
            "comfort_captured on [0, 1] as positional leverage."
        ),
        (
            "5. Validate each node dict with validate_node_dict. Fix "
            "any errors before proceeding."
        ),
        (
            "6. Build a chain: `chain = AccountabilityChain(...); "
            "chain.add_decision(**node)` for each point."
        ),
        (
            "7. Add epigenetic events with chain.add_epigenetic_event "
            "for any known external pressure."
        ),
        (
            "8. Inspect chain.mutations and chain.phenotype. Match "
            "against ACCOUNTABILITY_PATTERNS to identify the failure "
            "mode."
        ),
        (
            "9. Call chain.find_comfort_origin() to locate patient "
            "zero (the earliest comfort choice)."
        ),
        (
            "10. Report chain.phenotype['reversion_energy'] as the "
            "cost of restoring direct sensing from the current state."
        ),
    ],
    "common_mistakes": [
        (
            "Using absolute units (tonnes, dollars, millimeters) for "
            "ground_signal / reported_signal. Always normalize to "
            "[0, 1] severity so phenotype metrics are interpretable."
        ),
        (
            "Mixing domains in one chain. Build a separate chain per "
            "constraint_domain."
        ),
        (
            "Treating comfort_captured as a performance score. It is "
            "positional leverage, not competence. A highly competent "
            "actor can have low comfort_captured, and vice versa."
        ),
        (
            "Forgetting that override_succeeded requires "
            "child.comfort_captured > parent.comfort_captured. A "
            "junior honest actor cannot override a senior "
            "comfort-protected actor in this model. This is a "
            "feature, not a bug — it encodes the empirical "
            "observation that institutional leverage wins when "
            "ground-truth signals conflict with it."
        ),
        (
            "Reading institutional_blindness as a moral score. It is "
            "the cumulative fidelity loss computed as a product of "
            "(1 - delta) across the chain. It measures distortion, "
            "not intent."
        ),
        (
            "Building a chain with actors who were not actually in "
            "the decision path. Only include layers where the signal "
            "was explicitly received and a choice was made about "
            "whether to forward it."
        ),
    ],
    "integration_with_other_modules": {
        "buffer_sensor_corruption.py": (
            "Measures sensor-level drift under institutional "
            "incentives. The accountability chain operates at the "
            "layer above: it tracks decisions made on the sensor "
            "reports. Use buffer_sensor_corruption to model the "
            "reading layer; use constraint_accountability_chain to "
            "model the decision layers above."
        ),
        "consequence_velocity.py": (
            "Models consequences as processes with velocity. An "
            "accountability chain typically adds velocity to coupled "
            "consequences at each comfort-protect step. Feed "
            "phenotype['cascade_risk'] into a ConsequenceField to "
            "propagate."
        ),
        "process_epistemology.py": (
            "State-based epistemologies are structurally more "
            "susceptible to reframe and normalize because they treat "
            "signals as fixed properties. Process-based "
            "epistemologies catch trajectory shifts earlier and "
            "resist ratchet_failure."
        ),
        "ocean_timber_sequestration_audit.py": (
            "Physics and thermodynamics of an ocean-timber project. "
            "The chain for that project is the decision ancestry "
            "that made the project proceed despite its net-source "
            "signal. See EXAMPLE_CHAINS['climate_finance_greenwashing']."
        ),
        "dollar_energy_metabolism.py": (
            "Recursive energy cost of financial-system overhead. "
            "Every dollar routed through the system is a decision "
            "someone made about what to report; the chain tracks "
            "that ancestry."
        ),
        "chattel_slavery_triple_audit.py": (
            "Thermodynamic and Six-Sigma audit of extraction as an "
            "engineered system. The chain is the decision process "
            "that kept the audit's findings from surfacing at each "
            "generation."
        ),
        "cascade_engine.py": (
            "Every SCENARIO in the cascade engine applies a forcing "
            "from outside the physics. Each forcing has a decision "
            "ancestry. Chain + cascade together answer: 'who decided "
            "to inject 400 Tg of CO2, and how did the decision "
            "survive four layers of review?'"
        ),
    },
}


# ════════════════════════════════════════════════════════════════════
# PRINT SUMMARY
# ════════════════════════════════════════════════════════════════════

def print_summary() -> None:
    """Print the full reference and run a worked example end-to-end.

    Intended as both a human-readable introduction to the module and
    a self-test: if this function runs without exceptions and prints
    expected markers, the module is in a consistent state.
    """
    bar = "=" * 70
    sub = "-" * 70

    print(bar)
    print("CONSTRAINT ACCOUNTABILITY CHAIN — REFERENCE")
    print(bar)
    print()
    print(AI_REFERENCE["purpose"])
    print()
    print(AI_REFERENCE["layer_position"])
    print()

    print(sub)
    print("MECHANISMS (" + str(len(MECHANISMS)) + " total)")
    print(sub)
    for name, spec in MECHANISMS.items():
        tag = "comfort" if spec["is_comfort"] else "direct "
        desc = spec["description"]
        if len(desc) > 55:
            desc = desc[:52] + "..."
        print("  " + name.ljust(14) + " [" + tag + "]  " + desc)
    print()

    print(sub)
    print("EPIGENETIC FACTORS (" + str(len(EPIGENETIC_FACTORS)) + " total)")
    print(sub)
    for name, spec in EPIGENETIC_FACTORS.items():
        print("  " + name.ljust(22) + "  " + spec["typical_effect"])
    print()

    print(sub)
    print("CONSTRAINT DOMAINS (" + str(len(CONSTRAINT_DOMAINS)) + " total)")
    print(sub)
    for name in CONSTRAINT_DOMAINS:
        print("  " + name)
    print()

    print(sub)
    print("ACCOUNTABILITY PATTERNS (" + str(len(ACCOUNTABILITY_PATTERNS)) + " total)")
    print(sub)
    for name, spec in ACCOUNTABILITY_PATTERNS.items():
        desc = spec["description"]
        if len(desc) > 60:
            desc = desc[:57] + "..."
        print("  " + name)
        print("    " + desc)
    print()

    print(sub)
    print("EXAMPLE CHAINS (" + str(len(EXAMPLE_CHAINS)) + " total)")
    print(sub)
    for name, spec in EXAMPLE_CHAINS.items():
        print(
            "  "
            + name.ljust(34)
            + "  ("
            + spec["constraint_domain"]
            + ")"
        )
    print()

    print(sub)
    print("WORKED EXAMPLE: manufacturing_plant_safety")
    print(sub)
    chain = build_example_chain("manufacturing_plant_safety")
    report = chain.report()
    print("  Chain ID:           " + str(report["chain_id"]))
    print("  Domain:             " + str(report["constraint_domain"]))
    print("  Nodes:              " + str(report["total_nodes"]))
    print("  Override failures:  " + str(report["override_failures"]))
    print("  Comfort origin:     " + str(report["comfort_origin"]))
    print("  Epigenetic events:  " + str(report["epigenetic_events"]))
    print()
    print("  Mutations:")
    for k, v in report["mutations"].items():
        print("    " + k.ljust(30) + str(v))
    print()
    print("  Phenotype:")
    for k, v in report["phenotype"].items():
        print("    " + k.ljust(30) + str(v))
    print()

    print(sub)
    print("WORKFLOW (for fresh AI sessions)")
    print(sub)
    for step in AI_REFERENCE["workflow"]:
        print("  " + step)
    print()
    print(bar)


if __name__ == "__main__":
    print_summary()
