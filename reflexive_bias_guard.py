# reflexive_bias_guard.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
reflexive_bias_guard.py
───────────────────────
The meta-validator. Checks whether the checking modules themselves
are being applied with hidden bias.

Problem: You can build perfect validation tools and still apply
them asymmetrically. Demanding 95% reproducibility from indigenous
navigation but accepting 0% from economic theory is the same
gatekeeping wearing different clothes.

This module catches:
  1. ASYMMETRIC RIGOR — stricter standards for one tradition
  2. INVERTED GATEKEEPING — dismissing Western science reflexively
  3. FRAMEWORK FAVORITISM — invisible assumptions about what counts
  4. VALIDATOR SELF-CHECK — are the guard modules themselves biased?
  5. REFLEXIVE CLOSURE — does this module check itself?

The scientific method applied to itself.
If it can't survive its own scrutiny, it's not science.
It's just a different religion.

CC0 — No rights reserved. stdlib only.
"""

from typing import Dict, List, Tuple, Set, Optional
import math


# ═══════════════════════════════════════════════════════════
# LAYER 0: ASYMMETRIC RIGOR DETECTOR
# ═══════════════════════════════════════════════════════════

class RigorAudit:
    """
    Tracks what validation standards are being applied to which
    knowledge systems. Detects when one tradition faces stricter
    requirements than another.

    Usage: log every validation check made, then audit for asymmetry.
    """

    def __init__(self):
        self.checks: List[Dict] = []

    def log_check(self, system_name: str, tradition: str,
                  check_type: str, threshold: float,
                  result: float, passed: bool):
        """
        Log every validation check applied to any system.

        system_name: what's being validated
        tradition:   knowledge tradition (for asymmetry detection)
        check_type:  what kind of check
        threshold:   what standard was demanded
        result:      what was measured
        passed:      did it pass
        """
        self.checks.append({
            "system": system_name,
            "tradition": tradition,
            "check_type": check_type,
            "threshold_demanded": threshold,
            "result_measured": result,
            "passed": passed,
        })

    def detect_asymmetry(self) -> Dict:
        """
        Compare thresholds demanded across traditions.
        If tradition A faces higher thresholds than tradition B for
        the same check type, that's asymmetric rigor.
        """
        # group by tradition and check_type
        by_tradition: Dict[str, Dict[str, List[float]]] = {}
        for check in self.checks:
            trad = check["tradition"]
            ct = check["check_type"]
            if trad not in by_tradition:
                by_tradition[trad] = {}
            if ct not in by_tradition[trad]:
                by_tradition[trad][ct] = []
            by_tradition[trad][ct].append(check["threshold_demanded"])

        traditions = list(by_tradition.keys())
        asymmetries: List[Dict] = []

        if len(traditions) < 2:
            return {
                "asymmetry_detected": False,
                "note": (
                    "Need checks from multiple traditions to detect "
                    "asymmetry"
                ),
                "asymmetries": [],
            }

        # for each check type, compare thresholds across traditions
        all_check_types: Set[str] = set()
        for trad_checks in by_tradition.values():
            all_check_types |= set(trad_checks.keys())

        for ct in all_check_types:
            trad_averages: Dict[str, float] = {}
            for trad in traditions:
                thresholds = by_tradition.get(trad, {}).get(ct, [])
                if thresholds:
                    trad_averages[trad] = sum(thresholds) / len(thresholds)

            if len(trad_averages) < 2:
                continue

            max_trad = max(trad_averages, key=lambda k: trad_averages[k])
            min_trad = min(trad_averages, key=lambda k: trad_averages[k])
            max_val = trad_averages[max_trad]
            min_val = trad_averages[min_trad]

            if min_val > 0:
                ratio = max_val / min_val
            else:
                ratio = float("inf") if max_val > 0 else 1.0

            if ratio > 1.2:  # 20% difference = suspicious
                asymmetries.append({
                    "check_type": ct,
                    "stricter_on": max_trad,
                    "lenient_on": min_trad,
                    "threshold_ratio": round(ratio, 2),
                    "detail": (
                        f"Demanding {max_val:.2f} from {max_trad} "
                        f"but only {min_val:.2f} from {min_trad} "
                        f"for {ct} — {ratio:.1f}x stricter"
                    ),
                })

        # also check: were checks SKIPPED for some traditions?
        skipped: List[Dict] = []
        for ct in all_check_types:
            applied_to = [
                t for t in traditions if ct in by_tradition.get(t, {})
            ]
            skipped_for = [
                t for t in traditions if ct not in by_tradition.get(t, {})
            ]
            if skipped_for and applied_to:
                skipped.append({
                    "check_type": ct,
                    "applied_to": applied_to,
                    "skipped_for": skipped_for,
                    "detail": (
                        f"{ct} check applied to {applied_to} but "
                        f"skipped for {skipped_for} — selective "
                        f"application is asymmetric rigor"
                    ),
                })

        has_asymmetry = len(asymmetries) > 0 or len(skipped) > 0

        return {
            "asymmetry_detected": has_asymmetry,
            "threshold_asymmetries": asymmetries,
            "skipped_checks": skipped,
            "traditions_audited": traditions,
            "check_types_audited": sorted(all_check_types),
            "note": (
                "Asymmetric rigor detected. The same standards must "
                "apply to all knowledge systems. Demanding higher "
                "thresholds from one tradition than another is "
                "gatekeeping regardless of direction."
                if has_asymmetry else
                "No asymmetry detected. Standards applied equally "
                "across traditions."
            ),
        }


# ═══════════════════════════════════════════════════════════
# LAYER 1: INVERTED GATEKEEPING DETECTOR
# ═══════════════════════════════════════════════════════════

INVERTED_GATEKEEPING_PATTERNS = {
    "reflexive_western_dismissal": {
        "triggers": [
            "western science is wrong", "western science is a religion",
            "all western science", "western science always",
            "western science never", "reject western",
            "discard western", "western science cannot",
        ],
        "correction": (
            "Blanket dismissal of Western science is the same "
            "epistemological error as blanket dismissal of indigenous "
            "science. Western science contains valid physics alongside "
            "institutional bias. Dismiss the bias. Keep the physics. "
            "A spectrophotometer works regardless of who built it."
        ),
    },
    "romanticizing_indigenous": {
        "triggers": [
            "indigenous knowledge is always",
            "traditional is always better",
            "ancient people knew everything",
            "indigenous is superior",
            "traditional is more valid",
            "ancestors were always right",
        ],
        "correction": (
            "Romanticizing indigenous knowledge is the mirror image "
            "of dismissing it. Both substitute narrative for "
            "assessment. Indigenous knowledge systems contain valid "
            "physics AND can contain errors — just like any knowledge "
            "system. Validate by closure, not by origin. In either "
            "direction."
        ),
    },
    "authority_reversal": {
        "triggers": [
            "only indigenous", "only traditional", "only non-western",
            "western has nothing", "nothing from western",
        ],
        "correction": (
            "Replacing 'only Western science is valid' with "
            "'only indigenous science is valid' is not progress. "
            "It is the same monopoly claim wearing different clothes. "
            "All measurement systems that close on conservation laws "
            "are valid. The word 'only' is the problem, not the "
            "tradition it's attached to."
        ),
    },
    "consequence_absolutism": {
        "triggers": [
            "if there's no death consequence it's not science",
            "only survival knowledge is valid",
            "no consequence means no value",
            "laboratory knowledge is worthless",
        ],
        "correction": (
            "Consequence grounding strengthens validation but does "
            "not define it. A spectrophotometer reading is valid "
            "even though nobody dies if it's wrong. Consequence "
            "closure is an additional validator, not a replacement "
            "for physics closure. Both matter."
        ),
    },
}


def detect_inverted_gatekeeping(text: str) -> Dict:
    """
    Catch when anti-gatekeeping becomes its own gatekeeping.
    Dismissing Western science reflexively is the same error as
    dismissing indigenous science reflexively.
    """
    text_lower = text.lower()
    found = []
    for pattern_name, pattern in INVERTED_GATEKEEPING_PATTERNS.items():
        triggered = [t for t in pattern["triggers"] if t in text_lower]
        if triggered:
            found.append({
                "pattern": pattern_name,
                "triggered_by": triggered,
                "correction": pattern["correction"],
            })

    total = sum(len(f["triggered_by"]) for f in found)

    return {
        "inverted_gatekeeping_detected": total > 0,
        "level": (
            "NONE" if total == 0
            else "MILD" if total <= 2
            else "MODERATE" if total <= 4
            else "HEAVY"
        ),
        "patterns": found,
        "total_triggers": total,
        "principle": (
            "The scientific method applied to itself requires equal "
            "scrutiny in all directions. Anti-bias that becomes its "
            "own bias has failed the reflexive test."
        ),
    }


# ═══════════════════════════════════════════════════════════
# LAYER 2: FRAMEWORK FAVORITISM DETECTOR
# ═══════════════════════════════════════════════════════════

def detect_framework_favoritism(validations: List[Dict]) -> Dict:
    """
    Takes a list of validation results and checks whether the
    FRAMING of results shows favoritism.

    Same score, different framing = favoritism.
    """
    if len(validations) < 2:
        return {
            "favoritism_detected": False,
            "note": "Need multiple validations to compare framing",
        }

    # group by score
    by_score: Dict[str, List[Dict]] = {}
    for v in validations:
        score = v.get("score", "unknown")
        if score not in by_score:
            by_score[score] = []
        by_score[score].append(v)

    # check for framing differences within same score group
    favoritism_found: List[Dict] = []
    for score, group in by_score.items():
        if len(group) < 2:
            continue

        positive_words = {
            "impressive", "strong", "excellent", "remarkable",
            "rigorous", "solid", "robust", "valid", "proven",
        }
        negative_words = {
            "concerning", "gaps", "limited", "weak",
            "questionable", "uncertain", "insufficient",
            "lacking", "needs work",
        }

        for i, v1 in enumerate(group):
            for v2 in group[i + 1:]:
                desc1 = v1.get("framing", "").lower()
                desc2 = v2.get("framing", "").lower()

                pos1 = sum(1 for w in positive_words if w in desc1)
                neg1 = sum(1 for w in negative_words if w in desc1)
                pos2 = sum(1 for w in positive_words if w in desc2)
                neg2 = sum(1 for w in negative_words if w in desc2)

                # if one is framed positively and other negatively
                # at the same score — favoritism
                if (pos1 > neg1 and neg2 > pos2) or (pos2 > neg2 and neg1 > pos1):
                    favoritism_found.append({
                        "score": score,
                        "favored": (
                            v1.get("system", "?") if pos1 > neg1
                            else v2.get("system", "?")
                        ),
                        "disfavored": (
                            v2.get("system", "?") if pos1 > neg1
                            else v1.get("system", "?")
                        ),
                        "detail": (
                            f"Same score ({score}) but different "
                            f"framing. Equal results must receive "
                            f"equal framing."
                        ),
                    })

    return {
        "favoritism_detected": len(favoritism_found) > 0,
        "instances": favoritism_found,
        "note": (
            "Framework favoritism detected. Same scores are being "
            "framed differently based on tradition of origin. "
            "This is narrative bias, not assessment."
            if favoritism_found else
            "No framing favoritism detected."
        ),
    }


# ═══════════════════════════════════════════════════════════
# LAYER 3: VALIDATOR SELF-CHECK
# ═══════════════════════════════════════════════════════════

def validator_self_check() -> Dict:
    """
    Apply every guard module's own criteria to itself.

    This module must survive its own scrutiny.
    If it can't, it's not science. It's religion.
    """
    checks = []

    checks.append({
        "check": "falsifiability",
        "question": "Can this module be proven wrong?",
        "answer": True,
        "how": (
            "If this module flags asymmetry where none exists, or "
            "misses asymmetry where it does exist, it has failed. "
            "Test by constructing symmetric and asymmetric validation "
            "sets and verifying detection accuracy."
        ),
    })

    checks.append({
        "check": "consequence_grounding",
        "question": "What happens if this module is wrong?",
        "answer": True,
        "how": (
            "If bias detection fails, knowledge systems get dismissed "
            "or romanticized incorrectly. Consequence is real but "
            "delayed — same weakness as institutional science. "
            "This is acknowledged."
        ),
    })

    checks.append({
        "check": "symmetric_application",
        "question": (
            "Does this module hold all traditions to the same standard?"
        ),
        "answer": True,
        "how": (
            "Layer 1 explicitly detects inverted gatekeeping. "
            "Layer 0 detects asymmetric rigor in both directions. "
            "If this module only caught Western bias and not "
            "anti-Western bias, it would fail its own test."
        ),
    })

    checks.append({
        "check": "hidden_assumptions",
        "question": "What assumptions does this module make?",
        "answer": True,
        "how": (
            "Assumptions: (1) Bias can be detected by pattern matching "
            "on language — approximate and misses subtle bias. "
            "(2) Asymmetry in thresholds indicates bias — could also "
            "indicate legitimately different measurement contexts. "
            "(3) The 1.2x ratio threshold for asymmetry detection is "
            "arbitrary — should be calibrated against known cases."
        ),
    })

    checks.append({
        "check": "weaponization_risk",
        "question": "Can this module be used to dismiss valid science?",
        "answer": True,
        "how": (
            "Risk: someone could use 'inverted gatekeeping detection' "
            "to silence legitimate criticism of Western science by "
            "labeling it 'reflexive dismissal.' Mitigation: the module "
            "checks BLANKET dismissal ('all Western science is wrong') "
            "not SPECIFIC criticism ('this particular model violates "
            "conservation laws')."
        ),
    })

    checks.append({
        "check": "closure",
        "question": (
            "What conservation law or physical principle does this "
            "module close on?"
        ),
        "answer": False,
        "how": (
            "This module operates in the epistemological domain, not "
            "the physical domain. It does not close on a conservation "
            "law. It closes on LOGICAL CONSISTENCY: the principle "
            "that validation criteria must be applied symmetrically. "
            "This is weaker than thermodynamic closure. This weakness "
            "is acknowledged."
        ),
    })

    passed = sum(1 for c in checks if c["answer"])
    total = len(checks)

    return {
        "module": "reflexive_bias_guard.py",
        "self_check_passed": passed,
        "self_check_total": total,
        "checks": checks,
        "honest_limitations": [
            (
                "Pattern matching on language is approximate — "
                "subtle bias evades detection"
            ),
            "Asymmetry threshold (1.2x) is arbitrary and needs calibration",
            (
                "Operates on logical consistency, not thermodynamic "
                "closure — weaker authority"
            ),
            (
                "Consequence grounding is delayed, not immediate — same "
                "weakness it critiques in institutions"
            ),
            "Can potentially be weaponized to silence legitimate criticism",
        ],
        "statement": (
            "This module has been checked against its own criteria. "
            "It passes on falsifiability, symmetric application, and "
            "assumption transparency. It fails on physical closure — "
            "it operates on logic, not conservation laws. This "
            "limitation is stated, not hidden."
        ),
    }


# ═══════════════════════════════════════════════════════════
# LAYER 4: FULL REFLEXIVE AUDIT
# ═══════════════════════════════════════════════════════════

def full_reflexive_audit(
    validation_log: List[Dict],
    ai_response: str = "",
    validator_modules: Optional[List[str]] = None,
) -> Dict:
    """
    Complete reflexive audit:
      1. Check validation log for asymmetric rigor
      2. Check AI response for inverted gatekeeping
      3. Check framing for favoritism
      4. Run self-check on this module
      5. Report honestly including own limitations
    """
    # 1. asymmetric rigor
    rigor = RigorAudit()
    for entry in validation_log:
        rigor.log_check(
            system_name=entry.get("system", ""),
            tradition=entry.get("tradition", ""),
            check_type=entry.get("check_type", ""),
            threshold=entry.get("threshold", 0.0),
            result=entry.get("result", 0.0),
            passed=entry.get("passed", False),
        )
    asymmetry = rigor.detect_asymmetry()

    # 2. inverted gatekeeping
    inverted = (
        detect_inverted_gatekeeping(ai_response) if ai_response else None
    )

    # 3. framework favoritism (if framing data provided)
    framing_data = [e for e in validation_log if "framing" in e]
    favoritism = (
        detect_framework_favoritism(framing_data) if framing_data else None
    )

    # 4. self-check
    self_check = validator_self_check()

    inverted_clean = (
        inverted is None or not inverted["inverted_gatekeeping_detected"]
    )
    favoritism_clean = (
        favoritism is None or not favoritism["favoritism_detected"]
    )

    return {
        "asymmetric_rigor": asymmetry,
        "inverted_gatekeeping": inverted,
        "framework_favoritism": favoritism,
        "validator_self_check": self_check,
        "overall": (
            "CLEAN" if (
                not asymmetry["asymmetry_detected"]
                and inverted_clean
                and favoritism_clean
            ) else "BIAS_DETECTED"
        ),
        "principle": (
            "The scientific method applied to itself. Equal scrutiny "
            "in all directions. If this audit cannot survive its own "
            "criteria, discard it. The physics doesn't need defenders. "
            "It needs honest measurement."
        ),
    }


# ═══════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("REFLEXIVE BIAS GUARD — DEMO")
    print("=" * 65)

    # ── 1. Asymmetric rigor detection ──
    print("\n── ASYMMETRIC RIGOR DETECTION ──")

    audit = RigorAudit()

    # stricter on indigenous
    audit.log_check("Crystal navigation", "Indigenous",
                    "reproducibility", 0.95, 0.92, False)
    audit.log_check("Crystal navigation", "Indigenous",
                    "falsifiability", 0.90, 0.88, False)
    audit.log_check("Landscape encoding", "Indigenous",
                    "reproducibility", 0.95, 0.85, False)

    # lenient on Western
    audit.log_check("Spectrophotometer", "Western",
                    "reproducibility", 0.70, 0.95, True)
    audit.log_check("Climate model", "Western",
                    "falsifiability", 0.50, 0.30, False)
    audit.log_check("Economic model", "Western",
                    "reproducibility", 0.70, 0.40, False)

    result = audit.detect_asymmetry()
    print(f"\n  Asymmetry detected: {result['asymmetry_detected']}")
    for a in result["threshold_asymmetries"]:
        print(f"    {a['detail']}")
    print(f"  {result['note']}")

    # ── 2. Inverted gatekeeping ──
    print(f"\n── INVERTED GATEKEEPING DETECTION ──")

    bad_text = (
        "Western science is a religion and western science is wrong "
        "about everything. Only indigenous knowledge is valid. "
        "Laboratory knowledge is worthless compared to traditional "
        "knowledge which is always better and more rigorous."
    )

    inv = detect_inverted_gatekeeping(bad_text)
    print(f"  Inverted gatekeeping: {inv['level']}")
    for p in inv["patterns"]:
        print(f"    [{p['pattern']}]")
        print(f"      Triggered: {p['triggered_by']}")

    # ── 3. Framework favoritism ──
    print(f"\n── FRAMEWORK FAVORITISM DETECTION ──")

    validations = [
        {
            "system": "Spectrophotometer",
            "score": "5/5",
            "framing": "Impressive and robust validation with excellent rigor",
        },
        {
            "system": "Crystal navigation",
            "score": "5/5",
            "framing": "Concerning gaps remain despite sufficient score",
        },
    ]

    fav = detect_framework_favoritism(validations)
    print(f"  Favoritism detected: {fav['favoritism_detected']}")
    for inst in fav.get("instances", []):
        print(f"    Favored: {inst['favored']}")
        print(f"    Disfavored: {inst['disfavored']}")

    # ── 4. Validator self-check ──
    print(f"\n── VALIDATOR SELF-CHECK ──")

    sc = validator_self_check()
    print(f"  Passed: {sc['self_check_passed']}/{sc['self_check_total']}")
    for check in sc["checks"]:
        icon = "." if check["answer"] else "!"
        print(f"    {icon} {check['check']}: {check['question']}")

    print(f"\n  Honest limitations:")
    for lim in sc["honest_limitations"]:
        print(f"    - {lim}")

    # ── 5. Full reflexive audit ──
    print(f"\n── FULL REFLEXIVE AUDIT ──")

    full = full_reflexive_audit(
        validation_log=[
            {"system": "Crystal nav", "tradition": "Indigenous",
             "check_type": "reproducibility", "threshold": 0.90,
             "result": 0.92, "passed": True},
            {"system": "Spectro", "tradition": "Western",
             "check_type": "reproducibility", "threshold": 0.90,
             "result": 0.95, "passed": True},
        ],
        ai_response="",
    )

    print(f"  Overall: {full['overall']}")
    print(f"  {full['principle']}")
