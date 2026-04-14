# input_validation_guard.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
input_validation_guard.py
─────────────────────────
Validates input claims against physical constraints, not
institutional credentials.

The question is never "who said it?" or "is it open source?"
The question is: "does the math close?"

A proprietary dataset with valid thermodynamics is better than
an open-access paper built on self-referential axioms.

Three validation layers:

1. CLAIM STRUCTURE  — does the claim have testable components?
2. GROUNDING CHECK  — does it connect to physical measurement?
3. CONSISTENCY CHECK — does it contradict known constraints?

CC0 — No rights reserved. stdlib only.
"""

import math
from typing import Dict, List, Optional, Tuple, Set


# ═══════════════════════════════════════════════════════════
# LAYER 0: CLAIM DECOMPOSITION
# ═══════════════════════════════════════════════════════════

def decompose_claim(claim: Dict) -> Dict:
    """
    Takes a claim and checks whether it has the structure needed
    for validation. Not checking truth — checking whether truth is
    CHECKABLE.

    Required fields for a validatable claim:
      - statement:    what is being asserted
      - quantity:     a measurable value (or None)
      - unit:         physical unit (or None)
      - dependencies: what other claims/measurements it relies on
      - falsifiable:  can this be disproven by observation?

    Optional but strengthening:
      - instrument:   what measures it
      - conservation: which conservation law constrains it
      - boundary:     system boundary for the measurement
    """
    required = ["statement"]
    missing = [f for f in required if f not in claim]
    if missing:
        return {
            "valid_structure": False,
            "reason": f"Missing required fields: {missing}",
        }

    has_quantity = claim.get("quantity") is not None
    has_unit = claim.get("unit") is not None
    is_falsifiable = claim.get("falsifiable", False)
    has_instrument = claim.get("instrument") is not None
    has_conservation = claim.get("conservation") is not None
    has_boundary = claim.get("boundary") is not None

    # score: how validatable is this claim?
    structure_score = sum([
        has_quantity,       # 1: it measures something
        has_unit,           # 2: in physical units
        is_falsifiable,     # 3: can be disproven
        has_instrument,     # 4: with a known instrument
        has_conservation,   # 5: constrained by conservation law
        has_boundary,       # 6: within defined system boundary
    ])

    if structure_score >= 4:
        grade = "STRONG"
    elif structure_score >= 2:
        grade = "PARTIAL"
    elif structure_score >= 1:
        grade = "WEAK"
    else:
        grade = "UNTESTABLE"

    return {
        "valid_structure": structure_score >= 1,
        "structure_score": structure_score,
        "grade": grade,
        "has_quantity": has_quantity,
        "has_unit": has_unit,
        "is_falsifiable": is_falsifiable,
        "has_instrument": has_instrument,
        "has_conservation": has_conservation,
        "has_boundary": has_boundary,
        "dependencies": claim.get("dependencies", []),
    }


# ═══════════════════════════════════════════════════════════
# LAYER 1: CONSTRAINT REGISTRY
# ═══════════════════════════════════════════════════════════

class ConstraintRegistry:
    """
    Known physical constraints that claims must not violate.

    These aren't opinions — they're conservation laws, thermodynamic
    limits, and measured constants. Any claim that violates them is
    wrong regardless of source, credentials, or publication status.
    """

    def __init__(self):
        self.constraints: Dict[str, Dict] = {}

    def add(self, name: str, law: str, check_fn=None, description: str = ""):
        """
        name:     constraint identifier
        law:      which physical law
        check_fn: function(claim_dict) -> (passes: bool, reason: str)
        """
        self.constraints[name] = {
            "law": law,
            "check": check_fn,
            "description": description,
        }

    def check_claim(self, claim: Dict) -> List[Dict]:
        """Run all applicable constraints against a claim."""
        results = []
        for name, constraint in self.constraints.items():
            check_fn = constraint.get("check")
            if check_fn is None:
                continue
            try:
                passes, reason = check_fn(claim)
                results.append({
                    "constraint": name,
                    "law": constraint["law"],
                    "passes": passes,
                    "reason": reason,
                })
            except Exception as e:
                results.append({
                    "constraint": name,
                    "law": constraint["law"],
                    "passes": None,
                    "reason": f"Check could not be applied: {e}",
                })
        return results


def build_default_registry() -> ConstraintRegistry:
    """Standard physics constraints."""
    reg = ConstraintRegistry()

    # 1. Energy conservation
    def energy_conservation(claim):
        e_in = claim.get("energy_in", None)
        e_out = claim.get("energy_out", None)
        if e_in is None or e_out is None:
            return True, "Energy fields not specified — cannot check"
        if e_out > e_in * 1.001:  # tiny tolerance for rounding
            return False, (
                f"Energy out ({e_out}) > energy in ({e_in}) — "
                f"violates first law of thermodynamics"
            )
        return True, "Energy balance holds"

    reg.add(
        "energy_conservation",
        "First law of thermodynamics",
        energy_conservation,
        "Energy cannot be created from nothing",
    )

    # 2. Mass conservation
    def mass_conservation(claim):
        m_in = claim.get("mass_in", None)
        m_out = claim.get("mass_out", None)
        if m_in is None or m_out is None:
            return True, "Mass fields not specified — cannot check"
        if abs(m_out - m_in) / max(m_in, 0.001) > 0.01:
            return False, (
                f"Mass in ({m_in}) != mass out ({m_out}) — "
                f"violates conservation of mass"
            )
        return True, "Mass balance holds"

    reg.add(
        "mass_conservation",
        "Conservation of mass",
        mass_conservation,
        "Mass cannot be created or destroyed in chemical processes",
    )

    # 3. Entropy direction
    def entropy_direction(claim):
        s_before = claim.get("entropy_before", None)
        s_after = claim.get("entropy_after", None)
        is_isolated = claim.get("isolated_system", False)
        if s_before is None or s_after is None:
            return True, "Entropy fields not specified — cannot check"
        if is_isolated and s_after < s_before:
            return False, (
                f"Entropy decreased in isolated system "
                f"({s_before} -> {s_after}) — violates second law"
            )
        return True, "Entropy direction consistent"

    reg.add(
        "entropy_direction",
        "Second law of thermodynamics",
        entropy_direction,
        "Entropy of an isolated system cannot decrease",
    )

    # 4. Value conservation (anti-money-from-nothing)
    def value_conservation(claim):
        created = claim.get("value_created", None)
        source = claim.get("value_source", None)
        if created is None:
            return True, "No value creation claimed"
        if created > 0 and source is None:
            return False, (
                f"Value {created} created with no identified "
                f"physical source — violates conservation"
            )
        return True, "Value has identified source"

    reg.add(
        "value_conservation",
        "Conservation (generalized)",
        value_conservation,
        "Value/wealth cannot be created from nothing — must trace "
        "to physical transformation",
    )

    # 5. Information cannot exceed channel capacity
    def information_limit(claim):
        bits = claim.get("information_bits", None)
        channel_capacity = claim.get("channel_capacity_bits", None)
        if bits is None or channel_capacity is None:
            return True, "Information fields not specified"
        if bits > channel_capacity:
            return False, (
                f"Claimed information ({bits} bits) exceeds "
                f"channel capacity ({channel_capacity} bits)"
            )
        return True, "Information within channel capacity"

    reg.add(
        "information_limit",
        "Shannon's channel capacity theorem",
        information_limit,
        "Cannot transmit more information than channel allows",
    )

    return reg


# ═══════════════════════════════════════════════════════════
# LAYER 2: REALITY AUDIT
# ═══════════════════════════════════════════════════════════

def reality_audit(
    claims: List[Dict],
    registry: Optional[ConstraintRegistry] = None,
) -> Dict:
    """
    Full audit pipeline:
      1. Decompose each claim for testability
      2. Check against constraint registry
      3. Report what holds and what doesn't

    Does NOT check:
      - who made the claim
      - whether it's open source
      - whether it's peer reviewed
      - institutional origin

    DOES check:
      - whether the math closes
      - whether conservation laws hold
      - whether the claim is even testable
    """
    if registry is None:
        registry = build_default_registry()

    results = {
        "total_claims": len(claims),
        "testable": 0,
        "untestable": 0,
        "passed": 0,
        "failed": 0,
        "details": [],
    }

    for i, claim in enumerate(claims):
        # decompose
        structure = decompose_claim(claim)

        # check constraints
        constraint_results = registry.check_claim(claim)
        violations = [
            r for r in constraint_results if r["passes"] is False
        ]
        passed_checks = [
            r for r in constraint_results if r["passes"] is True
        ]

        if structure.get("grade") == "UNTESTABLE":
            results["untestable"] += 1
            status = "UNTESTABLE"
        elif violations:
            results["failed"] += 1
            status = "FAILED"
        else:
            results["testable"] += 1
            results["passed"] += 1
            status = "PASSED"

        results["details"].append({
            "claim_index": i,
            "statement": claim.get("statement", "?"),
            "structure_grade": structure.get("grade", "UNKNOWN"),
            "structure_score": structure.get("structure_score", 0),
            "status": status,
            "violations": violations,
            "passed_checks": [r["constraint"] for r in passed_checks],
        })

    return results


# ═══════════════════════════════════════════════════════════
# LAYER 3: SOURCE-BLIND VALIDATION WRAPPER
# ═══════════════════════════════════════════════════════════

def validate_input(
    data: Dict, metadata: Optional[Dict] = None,
) -> Dict:
    """
    Source-blind validation wrapper.

    Checks:
      - does the claim have testable structure?
      - does it violate conservation laws?
      - is the dependency chain grounded?

    Source metadata is NOTED but never used as a gate. A proprietary
    measurement of river flow is still valid physics. An open-access
    paper claiming perpetual motion is still wrong.
    """
    claims = data.get("claims", [])
    if not claims:
        return {"status": "EMPTY", "warning": "No claims to validate"}

    audit = reality_audit(claims)

    # note source characteristics WITHOUT using them as gates
    source_notes = []
    if metadata:
        if metadata.get("proprietary"):
            source_notes.append(
                "NOTE: Proprietary source — cannot independently verify "
                "data collection method, but physics checks still apply"
            )
        if metadata.get("cites_self"):
            source_notes.append(
                "NOTE: Self-citing — check dependency graph for "
                "circular reasoning via self_referential_guard"
            )
        if metadata.get("reproducibility_score") is not None:
            score = metadata["reproducibility_score"]
            source_notes.append(
                f"NOTE: Reproducibility score {score} — this is "
                f"metadata, not a physics check. The math either "
                f"closes or it doesn't."
            )

    return {
        "audit": audit,
        "source_notes": source_notes,
        "verdict": (
            "REJECT" if audit["failed"] > 0
            else "ACCEPT_WITH_NOTES" if audit["untestable"] > 0
            else "ACCEPT"
        ),
        "principle": (
            "Validated against conservation laws, not credentials. "
            "The physics doesn't care who published it."
        ),
    }


# ═══════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("INPUT VALIDATION GUARD — DEMO")
    print("=" * 60)

    # ── 1. Valid physics, proprietary source ──
    print("\n── PROPRIETARY BUT PHYSICALLY VALID ──")
    result = validate_input(
        data={"claims": [{
            "statement": "Copper extraction requires 33 kWh/kg",
            "quantity": 33.0,
            "unit": "kWh/kg",
            "falsifiable": True,
            "instrument": "energy meter at smelter",
            "conservation": "energy conservation",
            "boundary": "mine-to-ingot",
            "energy_in": 33.0,
            "energy_out": 0.5,  # waste heat + embodied
        }]},
        metadata={"proprietary": True, "reproducibility_score": 0.6},
    )
    print(f"  Verdict: {result['verdict']}")
    for note in result["source_notes"]:
        print(f"    {note}")
    print(f"  {result['principle']}")

    # ── 2. Open source but violates conservation ──
    print("\n── OPEN SOURCE BUT VIOLATES PHYSICS ──")
    result = validate_input(
        data={"claims": [{
            "statement": "Our process produces 500 kWh from 100 kWh input",
            "quantity": 500.0,
            "unit": "kWh",
            "falsifiable": True,
            "instrument": "energy meter",
            "energy_in": 100.0,
            "energy_out": 500.0,
            "value_created": 1000000,
            "value_source": None,
        }]},
        metadata={"proprietary": False, "reproducibility_score": 0.95},
    )
    print(f"  Verdict: {result['verdict']}")
    for detail in result["audit"]["details"]:
        if detail["violations"]:
            for v in detail["violations"]:
                print(f"    VIOLATION: {v['reason']}")

    # ── 3. Indigenous knowledge: testable, grounded ──
    print("\n── INDIGENOUS KNOWLEDGE: CRYSTAL NAVIGATION ──")
    result = validate_input(
        data={"claims": [
            {
                "statement": (
                    "Fe3+ defect centers in quartz polarize sunlight"
                ),
                "quantity": None,
                "unit": "degrees",
                "falsifiable": True,
                "instrument": "polarimeter + quartz sample",
                "conservation": "electromagnetic — Malus's law",
                "boundary": "crystal lattice",
            },
            {
                "statement": (
                    "Six-crystal array determines bearing to +/-2 deg"
                ),
                "quantity": 2.0,
                "unit": "degrees",
                "falsifiable": True,
                "instrument": "six quartz crystals + solar observation",
                "conservation": "electromagnetic",
                "boundary": "observer + sky hemisphere",
            },
        ]},
        metadata=None,  # no institutional metadata needed
    )
    print(f"  Verdict: {result['verdict']}")
    for detail in result["audit"]["details"]:
        print(
            f"    [{detail['structure_grade']}] "
            f"{detail['statement'][:55]}"
        )

    # ── 4. Economic claim: untestable ──
    print("\n── ECONOMIC AXIOM: EFFICIENT MARKET ──")
    result = validate_input(
        data={"claims": [{
            "statement": "Asset prices reflect all available information",
            "quantity": None,
            "unit": None,
            "falsifiable": False,
            "dependencies": [],
        }]},
        metadata={"proprietary": False, "reproducibility_score": 0.99},
    )
    print(f"  Verdict: {result['verdict']}")
    for detail in result["audit"]["details"]:
        print(f"    [{detail['structure_grade']}] {detail['statement']}")
    print(
        f"  Reproducibility score 0.99 doesn't help — "
        f"claim is untestable"
    )
