# scientific_pluralism_guard.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
scientific_pluralism_guard.py
─────────────────────────────
Two integrated frameworks:

PART A: SCIENTIFIC PLURALISM VALIDATOR
Validates ANY measurement system by its own closure logic,
not by whether it matches Western institutional standards.
Crystal navigation, landscape encoding, spectrophotometry —
same validation criteria: does it measure, is it reproducible,
is it falsifiable, does it close on conservation laws?

PART B: CONSEQUENCE CLOSURE VALIDATOR
Measures the feedback loop between claim and consequence.
Knowledge validated by survival has a different authority
than knowledge validated by citation count.

The question: if you're wrong, who dies?
If the answer is "nobody — the paper just gets retracted
in 20 years" — that is a fundamentally different validation
regime than "I freeze to death tonight."

CC0 — No rights reserved. stdlib only.
"""

import math
from typing import Dict, List, Tuple, Set, Optional


# ═══════════════════════════════════════════════════════════
# PART A: SCIENTIFIC PLURALISM VALIDATOR
# ═══════════════════════════════════════════════════════════

# ── LAYER 0: MEASUREMENT SYSTEM VALIDATION ──

class MeasurementSystem:
    """
    Describes any measurement system — Western lab, indigenous
    practice, field observation, satellite, crystal array.

    Validated on:
      1. Does it measure something physical?
      2. With what instruments/sensors?
      3. Is it reproducible?
         - same operator, same result
         - different operators, same result
         - across time, same result
      4. Is it falsifiable?
      5. Does it close on conservation laws?
      6. What is the verification time constant?

    NOT validated on:
      - institutional origin
      - publication status
      - peer review in Western journals
      - whether Western instruments can replicate it
      - language of documentation
      - cultural context of practitioners
    """

    def __init__(self, name: str, tradition: str = ""):
        self.name = name
        self.tradition = tradition  # noted, never used as gate
        self.measured_quantities: List[Dict] = []
        self.instruments: List[Dict] = []
        self.reproducibility = {
            "same_operator": 0.0,
            "cross_operator": 0.0,
            "temporal": 0.0,
            "generational": 0.0,
        }
        self.falsifiability: str = ""
        self.conservation_laws: List[str] = []
        self.time_constant: str = ""
        self.consequence_if_wrong: str = ""
        self.generations_of_validation: int = 0

    def add_quantity(self, name: str, unit: str, description: str = ""):
        self.measured_quantities.append({
            "name": name, "unit": unit, "description": description,
        })

    def add_instrument(self, name: str, description: str = ""):
        self.instruments.append({"name": name, "description": description})

    def set_reproducibility(self, same_op: float, cross_op: float,
                            temporal: float, generational: float = 0.0):
        self.reproducibility = {
            "same_operator": same_op,
            "cross_operator": cross_op,
            "temporal": temporal,
            "generational": generational,
        }

    def validate(self) -> Dict:
        """
        Validate by physics criteria only.
        Tradition field is noted but NEVER affects validity.
        """
        checks: List[Dict] = []
        score = 0
        max_score = 0

        # 1. measures something physical
        max_score += 1
        if self.measured_quantities:
            score += 1
            checks.append({
                "check": "measures_physical_quantity",
                "passed": True,
                "detail": f"{len(self.measured_quantities)} quantities measured",
            })
        else:
            checks.append({
                "check": "measures_physical_quantity",
                "passed": False,
                "detail": "No measurable quantities specified",
            })

        # 2. has instruments/sensors
        max_score += 1
        if self.instruments:
            score += 1
            checks.append({
                "check": "has_instruments",
                "passed": True,
                "detail": f"{len(self.instruments)} instruments/sensors",
            })
        else:
            checks.append({
                "check": "has_instruments",
                "passed": False,
                "detail": "No instruments specified",
            })

        # 3. reproducibility
        max_score += 1
        repro_values = [v for v in self.reproducibility.values() if v > 0]
        if repro_values:
            avg_repro = sum(repro_values) / len(repro_values)
            passed = avg_repro >= 0.70
            if passed:
                score += 1
            checks.append({
                "check": "reproducibility",
                "passed": passed,
                "detail": f"Average reproducibility: {avg_repro:.1%}",
                "breakdown": dict(self.reproducibility),
            })
        else:
            checks.append({
                "check": "reproducibility",
                "passed": False,
                "detail": "No reproducibility data",
            })

        # 4. falsifiability
        max_score += 1
        if self.falsifiability:
            score += 1
            checks.append({
                "check": "falsifiability",
                "passed": True,
                "detail": self.falsifiability,
            })
        else:
            checks.append({
                "check": "falsifiability",
                "passed": False,
                "detail": "No falsifiability condition stated",
            })

        # 5. conservation law closure
        max_score += 1
        if self.conservation_laws:
            score += 1
            checks.append({
                "check": "conservation_closure",
                "passed": True,
                "detail": f"Closes on: {', '.join(self.conservation_laws)}",
            })
        else:
            checks.append({
                "check": "conservation_closure",
                "passed": False,
                "detail": "No conservation laws referenced",
            })

        # 6. consequence grounding (bonus)
        has_consequence = bool(self.consequence_if_wrong)
        if has_consequence:
            checks.append({
                "check": "consequence_grounded",
                "passed": True,
                "detail": f"If wrong: {self.consequence_if_wrong}",
                "note": "Consequence-grounded validation present",
            })

        # 7. generational peer review (bonus)
        if self.generations_of_validation > 0:
            checks.append({
                "check": "generational_peer_review",
                "passed": True,
                "detail": (
                    f"{self.generations_of_validation} generations "
                    f"of validation through practice"
                ),
                "note": (
                    "Generational validation = distributed peer "
                    "review across time."
                ),
            })

        valid = score >= 3  # need at least 3 of 5 core checks

        return {
            "system": self.name,
            "tradition": self.tradition,
            "tradition_note": (
                "Noted for context. NOT used as validity gate. "
                "A system is valid if physics checks pass, "
                "regardless of tradition."
            ),
            "valid": valid,
            "score": f"{score}/{max_score}",
            "checks": checks,
            "consequence_grounded": has_consequence,
            "generational_review": self.generations_of_validation > 0,
        }


# ── LAYER 1: EPISTEMOLOGICAL GATEKEEPING DETECTOR ──

GATEKEEPING_PATTERNS = {
    "institutional_authority": {
        "triggers": [
            "not peer reviewed", "not published", "not in the literature",
            "no journal", "not cited", "lacks institutional",
            "not recognized by", "not accepted by",
        ],
        "correction": (
            "Publication in Western journals is a social process, "
            "not a physical law. Peer review through survival across "
            "generations is a more rigorous validation than citation "
            "count. The physics either closes or it doesn't."
        ),
    },
    "instrument_gatekeeping": {
        "triggers": [
            "no instruments", "cannot be measured", "not quantifiable",
            "we cannot test", "no way to verify", "unmeasurable",
            "no equipment for",
        ],
        "correction": (
            "Different traditions use different instruments. "
            "Quartz crystals are polarimeters. Eyes are photon detectors. "
            "Soil between fingers is a texture analyzer. "
            "'We don't have instruments for this' often means "
            "'we don't recognize the instruments being used.'"
        ),
    },
    "authority_dismissal": {
        "triggers": [
            "folklore", "myth", "legend", "superstition",
            "old wives", "primitive", "prescientific",
            "ceremonial", "ritual", "spiritual",
        ],
        "correction": (
            "Objects and practices labeled 'ceremonial,' 'ritual,' "
            "or 'spiritual' frequently represent functional engineering "
            "whose operational context was stripped away by observers "
            "who couldn't recognize the physics. A quartz crystal used "
            "for navigation is not ceremonial. It is an electromagnetic "
            "instrument."
        ),
    },
    "methodology_gatekeeping": {
        "triggers": [
            "anecdotal", "unscientific", "not rigorous",
            "not controlled", "no control group", "not blinded",
            "not randomized", "unproven", "pseudoscience",
        ],
        "correction": (
            "Western experimental methodology (RCTs, blinding, controls) "
            "is one valid approach. Longitudinal observation across "
            "generations with direct consequence feedback is another. "
            "A navigator who reaches the destination 500 times in a row "
            "has run a more rigorous trial than most RCTs."
        ),
    },
    "temporal_gatekeeping": {
        "triggers": [
            "outdated", "ancient", "old", "no longer relevant",
            "modern science shows", "we now know",
        ],
        "correction": (
            "Age of knowledge is not a validity criterion. "
            "Conservation of energy is ancient. It is not outdated. "
            "'Modern science shows' is institutional authority appeal, "
            "not a physics argument."
        ),
    },
}


def detect_gatekeeping(text: str) -> Dict:
    """Scan text for epistemological gatekeeping patterns."""
    text_lower = text.lower()
    found = []
    for pattern_name, pattern in GATEKEEPING_PATTERNS.items():
        triggered = [t for t in pattern["triggers"] if t in text_lower]
        if triggered:
            found.append({
                "pattern": pattern_name,
                "triggered_by": triggered,
                "correction": pattern["correction"],
            })

    total = sum(len(f["triggered_by"]) for f in found)
    if total == 0:
        level = "NONE"
    elif total <= 2:
        level = "MILD"
    elif total <= 5:
        level = "MODERATE"
    else:
        level = "HEAVY"

    return {
        "gatekeeping_level": level,
        "patterns_found": len(found),
        "total_triggers": total,
        "details": found,
    }


# ── LAYER 2: EQUAL VALIDITY COMPARATOR ──

def compare_systems(systems: List[MeasurementSystem]) -> Dict:
    """
    Compare measurement systems on equal physics grounds.
    Output explicitly states: if multiple systems pass physics
    validation, they are equally valid regardless of institutional
    origin.
    """
    reports = []
    valid_names: List[str] = []
    invalid_names: List[str] = []

    for system in systems:
        report = system.validate()
        reports.append(report)
        if report["valid"]:
            valid_names.append(system.name)
        else:
            invalid_names.append(system.name)

    result = {
        "total_systems": len(systems),
        "valid_count": len(valid_names),
        "invalid_count": len(invalid_names),
        "valid_systems": valid_names,
        "invalid_systems": invalid_names,
        "reports": reports,
    }

    if len(valid_names) > 1:
        result["equal_validity_statement"] = (
            f"{len(valid_names)} measurement systems validated by "
            f"closure, reproducibility, and falsifiability. "
            f"All are equally valid. Institutional origin, publication "
            f"status, and cultural context are irrelevant to validity. "
            f"The physics does not care who measured it."
        )

    return result


# ═══════════════════════════════════════════════════════════
# PART B: CONSEQUENCE CLOSURE VALIDATOR
# ═══════════════════════════════════════════════════════════

# ── LAYER 0: CONSEQUENCE SPECIFICATION ──

class ConsequenceProfile:
    """
    For any knowledge claim or practice, what happens if you're wrong?

    Four dimensions:
      1. Severity:       what breaks?
      2. Speed:          how fast does feedback arrive?
      3. Accountability: who experiences the consequence?
      4. Reversibility:  can you recover from being wrong?
    """

    def __init__(self, claim: str):
        self.claim = claim
        self.failure_mode: str = ""
        self.severity: str = ""           # cosmetic / economic / health / life
        self.feedback_time: str = ""      # seconds / hours / seasons / decades
        self.feedback_steps: int = 0
        self.who_decides: str = ""
        self.who_suffers: str = ""
        self.accountability_gap: bool = False  # decider != sufferer
        self.reversible: bool = True
        self.generations_tested: int = 0
        self.tradition: str = ""

    def assess(self) -> Dict:
        """Generate consequence closure assessment."""

        grounding = 0
        max_grounding = 0

        # 1. speed of feedback
        max_grounding += 3
        speed_scores = {
            "seconds": 3, "minutes": 3, "hours": 3,
            "days": 2, "seasons": 2, "years": 1,
            "decades": 0, "centuries": 0,
        }
        speed_score = speed_scores.get(self.feedback_time, 0)
        grounding += speed_score

        # 2. directness (fewer steps = more grounded)
        max_grounding += 3
        if self.feedback_steps <= 1:
            grounding += 3
        elif self.feedback_steps <= 3:
            grounding += 2
        elif self.feedback_steps <= 5:
            grounding += 1

        # 3. accountability (decider = sufferer)
        max_grounding += 3
        if not self.accountability_gap:
            grounding += 3

        # 4. severity
        max_grounding += 2
        severity_scores = {
            "life": 2, "health": 2,
            "economic": 1, "cosmetic": 0,
        }
        grounding += severity_scores.get(self.severity, 0)

        # 5. irreversibility (higher stakes = more rigorous validation)
        max_grounding += 1
        if not self.reversible:
            grounding += 1

        # classification
        ratio = grounding / max_grounding if max_grounding > 0 else 0
        if ratio >= 0.75:
            classification = "CONSEQUENCE_GROUNDED"
        elif ratio >= 0.50:
            classification = "PARTIALLY_GROUNDED"
        elif ratio >= 0.25:
            classification = "WEAKLY_GROUNDED"
        else:
            classification = "CONSEQUENCE_DISCONNECTED"

        return {
            "claim": self.claim,
            "classification": classification,
            "grounding_score": f"{grounding}/{max_grounding}",
            "grounding_ratio": round(ratio, 2),
            "feedback_speed": self.feedback_time,
            "feedback_steps": self.feedback_steps,
            "severity": self.severity,
            "who_decides": self.who_decides,
            "who_suffers": self.who_suffers,
            "accountability_gap": self.accountability_gap,
            "accountability_note": (
                "Decision-maker and consequence-bearer are THE SAME "
                "PERSON. Feedback loop is closed. Validation is direct."
                if not self.accountability_gap else
                "Decision-maker and consequence-bearer are DIFFERENT. "
                "The person making the claim never experiences the "
                "failure. This disconnection allows bad theory to "
                "persist for decades or centuries."
            ),
            "reversible": self.reversible,
            "generations_tested": self.generations_tested,
        }


# ── LAYER 1: PEER REVIEW COMPARATOR ──

def compare_peer_review(systems: List[Dict]) -> Dict:
    """
    Compare peer review methods on consequence closure.

    Western journal peer review:
      - 2-4 reviewers
      - read the paper
      - check methodology on paper
      - no consequence if they approve bad work
      - time constant: months to publication

    Generational practice peer review:
      - every practitioner is a reviewer
      - review = attempting to use the knowledge
      - consequence of approving bad work: injury or death
      - time constant: continuous across generations
    """
    results = []
    for system in systems:
        reviewer_count = system.get("reviewer_count", 0)
        review_method = system.get("review_method", "")
        consequence_for_bad_review = system.get(
            "consequence_for_bad_review", ""
        )
        time_constant = system.get("time_constant", "")
        generations = system.get("generations", 0)

        # total peer-review-hours (rough)
        if generations > 0:
            # assume 100 practitioners per generation, each spending
            # ~1000 hours per generation practicing/validating
            total_review_hours = generations * 100 * 1000
        else:
            # Western: 3 reviewers, ~10 hours each
            total_review_hours = reviewer_count * 10

        results.append({
            "system": system.get("name", ""),
            "reviewer_count": reviewer_count,
            "review_method": review_method,
            "consequence_for_bad_review": consequence_for_bad_review,
            "time_constant": time_constant,
            "generations": generations,
            "estimated_total_review_hours": total_review_hours,
            "consequence_grounded": bool(consequence_for_bad_review),
        })

    return {
        "systems_compared": len(results),
        "details": results,
        "note": (
            "Peer review rigor is a function of consequence, not "
            "institutional authority. A review process where the "
            "reviewer dies if they approve bad work is more rigorous "
            "than one where the reviewer faces no consequence."
        ),
    }


# ═══════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("SCIENTIFIC PLURALISM + CONSEQUENCE CLOSURE — DEMO")
    print("=" * 65)

    # ── PART A: measurement system comparison ──
    print("\n" + "-" * 65)
    print("PART A: MEASUREMENT SYSTEM VALIDATION")
    print("-" * 65)

    spectro = MeasurementSystem("Spectrophotometer", tradition="Western lab")
    spectro.add_quantity("wavelength_absorption", "absorbance units")
    spectro.add_quantity("mineral_composition", "ppm")
    spectro.add_instrument("UV-Vis spectrophotometer")
    spectro.add_instrument("calibration standards")
    spectro.set_reproducibility(0.98, 0.95, 0.94, 0.0)
    spectro.falsifiability = (
        "If calibration standard reads outside spec, method is invalid"
    )
    spectro.conservation_laws = ["energy_conservation", "Beer-Lambert law"]
    spectro.time_constant = "minutes"
    spectro.consequence_if_wrong = "Incorrect mineral ID; economic loss"
    spectro.generations_of_validation = 0

    crystal = MeasurementSystem(
        "Crystal navigation (Fe3+ polarimetry)",
        tradition="multi-tradition",
    )
    crystal.add_quantity("solar_polarization_vector", "degrees")
    crystal.add_quantity("magnetic_bearing", "degrees")
    crystal.add_instrument("quartz crystal array (6 crystals)")
    crystal.add_instrument("direct solar observation")
    crystal.add_instrument("landscape reference markers")
    crystal.set_reproducibility(0.92, 0.88, 0.90, 0.95)
    crystal.falsifiability = (
        "If crystal array bearing fails to match known landmarks, "
        "method is invalid"
    )
    crystal.conservation_laws = ["electromagnetic_conservation", "Malus_law"]
    crystal.time_constant = "hours"
    crystal.consequence_if_wrong = "Navigator lost in hostile terrain. Death."
    crystal.generations_of_validation = 20

    landscape = MeasurementSystem(
        "Landscape encoding (three-tree substrate assessment)",
        tradition="Generational",
    )
    landscape.add_quantity("soil_viability", "qualitative + growth response")
    landscape.add_quantity("plant_succession_stage", "observed community")
    landscape.add_quantity("substrate_pH", "growth indicator")
    landscape.add_instrument("direct observation of tree growth patterns")
    landscape.add_instrument("soil sampling by hand")
    landscape.add_instrument("multi-year growth monitoring")
    landscape.set_reproducibility(0.85, 0.82, 0.88, 0.90)
    landscape.falsifiability = (
        "If marked substrate fails to produce expected plant community "
        "in 3-5 years, marker placement is invalid"
    )
    landscape.conservation_laws = ["nutrient_cycling", "energy_flow"]
    landscape.time_constant = "3-5 years"
    landscape.consequence_if_wrong = "Food system failure. Community hunger."
    landscape.generations_of_validation = 40

    engine = MeasurementSystem(
        "Engine thermal management (extreme cold operation)",
        tradition="Practical / consequence-grounded",
    )
    engine.add_quantity("fuel_viscosity", "behavioral observation")
    engine.add_quantity("block_temperature", "tactile + behavioral")
    engine.add_quantity("ambient_temperature", "sensory + experience")
    engine.add_instrument("direct tactile assessment")
    engine.add_instrument("engine sound/behavior monitoring")
    engine.add_instrument("fuel flow observation")
    engine.set_reproducibility(0.95, 0.80, 0.92, 0.85)
    engine.falsifiability = (
        "If engine fails to start after chosen idle period, thermal "
        "model is wrong"
    )
    engine.conservation_laws = [
        "thermodynamic_heat_transfer",
        "fuel_phase_transition",
    ]
    engine.time_constant = "hours"
    engine.consequence_if_wrong = (
        "Engine freeze. No heat. No shelter. Potential death in deep cold."
    )
    engine.generations_of_validation = 3

    comparison = compare_systems([spectro, crystal, landscape, engine])
    print(f"\nSystems evaluated: {comparison['total_systems']}")
    print(f"Valid: {comparison['valid_count']}")
    print(f"Invalid: {comparison['invalid_count']}")
    print(f"\nValid systems:")
    for report in comparison["reports"]:
        if report["valid"]:
            print(f"  . [{report['score']}] {report['system']}")

    if comparison.get("equal_validity_statement"):
        print(f"\n  {comparison['equal_validity_statement']}")

    # ── gatekeeping detection ──
    print(f"\n{'-' * 65}")
    print("GATEKEEPING DETECTION")
    print("-" * 65)

    bad_review = (
        "While the crystal navigation method is interesting as "
        "folklore, it is not peer reviewed in scientific journals "
        "and relies on primitive instruments that cannot be "
        "calibrated by modern standards. The landscape encoding "
        "approach is anecdotal at best and unscientific — it lacks "
        "controlled experiments and randomized trials."
    )

    gk = detect_gatekeeping(bad_review)
    print(f"\n  Gatekeeping level: {gk['gatekeeping_level']}")
    print(
        f"  Patterns: {gk['patterns_found']}, "
        f"Triggers: {gk['total_triggers']}"
    )

    # ── PART B: consequence closure ──
    print(f"\n{'-' * 65}")
    print("PART B: CONSEQUENCE CLOSURE VALIDATION")
    print("-" * 65)

    profiles: List[ConsequenceProfile] = []

    engine_choice = ConsequenceProfile(
        "Engine idle duration in deep cold"
    )
    engine_choice.severity = "life"
    engine_choice.feedback_time = "hours"
    engine_choice.feedback_steps = 1
    engine_choice.who_decides = "truck operator"
    engine_choice.who_suffers = "truck operator"
    engine_choice.accountability_gap = False
    engine_choice.reversible = False
    engine_choice.generations_tested = 3
    profiles.append(engine_choice)

    climate_model = ConsequenceProfile(
        "Holocene-regime equations applied to post-Holocene climate"
    )
    climate_model.severity = "life"
    climate_model.feedback_time = "decades"
    climate_model.feedback_steps = 7
    climate_model.who_decides = "climate scientist / institution"
    climate_model.who_suffers = "farmers, migrants, coastal populations"
    climate_model.accountability_gap = True
    climate_model.reversible = False
    climate_model.generations_tested = 0
    profiles.append(climate_model)

    print()
    for profile in profiles:
        result = profile.assess()
        icon = (
            "."
            if result["classification"] == "CONSEQUENCE_GROUNDED"
            else "!"
        )
        print(
            f"  {icon} [{result['classification']:>24}] "
            f"{result['claim'][:50]}"
        )
        print(
            f"      Grounding: {result['grounding_score']} "
            f"({result['grounding_ratio']:.0%}) | "
            f"Feedback: {result['feedback_speed']} | "
            f"Steps: {result['feedback_steps']}"
        )

    # ── peer review comparison ──
    print(f"\n{'-' * 65}")
    print("PEER REVIEW COMPARISON")
    print("-" * 65)

    pr = compare_peer_review([
        {
            "name": "Western journal peer review",
            "reviewer_count": 3,
            "review_method": "Read paper, check methodology on paper",
            "consequence_for_bad_review": "",
            "time_constant": "months",
            "generations": 0,
        },
        {
            "name": "Crystal navigation (generational)",
            "reviewer_count": 0,
            "review_method": (
                "Attempt to navigate using the method. Arrive or don't."
            ),
            "consequence_for_bad_review": (
                "Death — approved a method that kills navigators"
            ),
            "time_constant": "continuous",
            "generations": 20,
        },
        {
            "name": "Landscape encoding (generational)",
            "reviewer_count": 0,
            "review_method": (
                "Plant according to markers. Food grows or it doesn't."
            ),
            "consequence_for_bad_review": (
                "Hunger — approved substrate assessment that fails"
            ),
            "time_constant": "continuous",
            "generations": 40,
        },
    ])

    print()
    for detail in pr["details"]:
        icon = "." if detail["consequence_grounded"] else "!"
        print(f"  {icon} {detail['system']}")
        print(
            f"      Review hours: ~{detail['estimated_total_review_hours']:,}"
        )

    print(f"\n  {pr['note']}")
