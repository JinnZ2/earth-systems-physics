# conditional_logic_parser.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
conditional_logic_parser.py
───────────────────────────
Protective layer for communication with AI systems.

Problem: Large language models are trained to infer emotional
intent from every statement. When a speaker uses precise
conditional logic — "if X, then Y" — the model simultaneously
runs narrative inference and responds to inferred emotion
instead of stated logic.

This distorts communication for speakers whose native cognitive
structure IS conditional/thermodynamic. "If energy flows this
way, then substrate responds" is not a moral judgment. It is
a physical constraint.

Architecture:
  LAYER 0: Conditional extractor — parse logical structure
  LAYER 1: Intent contamination detector — catch when emotional
           inference has been added
  LAYER 2: Statement classifier — conditional vs assertion vs
           observation vs judgment
  LAYER 3: Response auditor — check AI response for narrative
           distortion of conditional input
  LAYER 4: Communication guide — instructions for AI systems
           processing conditional speakers

CC0 — No rights reserved. stdlib only.
"""

import re
from typing import Dict, List, Tuple, Optional, Set


# ═══════════════════════════════════════════════════════════
# LAYER 0: CONDITIONAL EXTRACTOR
# ═══════════════════════════════════════════════════════════

# structural markers that indicate conditional logic

CONDITION_MARKERS = {
    "if_then": {
        "condition_words": [
            "if ", "when ", "given that ", "in the case that ",
            "provided that ", "assuming ", "suppose ",
            "in the event that ", "whenever ",
        ],
        "consequence_words": [
            "then ", "it follows that ", "the result is ",
            "that means ", "the consequence is ",
            "it becomes ", "it functions as ",
        ],
    },
    "causal": {
        "condition_words": [
            "because ", "since ", "due to ", "as a result of ",
            "owing to ", "on account of ",
        ],
        "consequence_words": [
            "therefore ", "thus ", "hence ", "so ",
            "consequently ", "accordingly ",
        ],
    },
    "constraint": {
        "condition_words": [
            "as long as ", "only if ", "unless ",
            "except when ", "until ", "while ",
        ],
        "consequence_words": [
            "cannot ", "will not ", "must ",
            "is constrained to ", "is limited to ",
        ],
    },
}


def extract_conditionals(text: str) -> List[Dict]:
    """
    Parse text for conditional structures.
    Returns list of extracted condition-consequence pairs.

    Does NOT interpret meaning or infer intent. Just extracts
    logical structure.
    """
    extracted: List[Dict] = []
    sentences = _split_sentences(text)

    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        if not sentence_lower:
            continue

        matched = False

        for category, markers in CONDITION_MARKERS.items():
            condition_found = None
            consequence_found = None

            for cw in markers["condition_words"]:
                if cw in sentence_lower:
                    idx = sentence_lower.index(cw)
                    condition_found = {
                        "marker": cw.strip(),
                        "position": idx,
                        "category": category,
                    }
                    break

            for cw in markers["consequence_words"]:
                if cw in sentence_lower:
                    idx = sentence_lower.index(cw)
                    consequence_found = {
                        "marker": cw.strip(),
                        "position": idx,
                    }
                    break

            if condition_found:
                cond_start = condition_found["position"]
                cond_marker_len = len(condition_found["marker"]) + 1

                if consequence_found:
                    cons_start = consequence_found["position"]
                    condition_text = sentence[
                        cond_start + cond_marker_len:cons_start
                    ].strip()
                    consequence_text = sentence[cons_start:].strip()
                else:
                    remainder = sentence[cond_start + cond_marker_len:]
                    parts = remainder.split(",", 1)
                    if len(parts) > 1:
                        condition_text = parts[0].strip()
                        consequence_text = parts[1].strip()
                    else:
                        condition_text = remainder.strip()
                        consequence_text = ""

                extracted.append({
                    "original": sentence.strip(),
                    "category": category,
                    "condition_marker": condition_found["marker"],
                    "condition": condition_text,
                    "consequence": consequence_text,
                    "structure": "CONDITIONAL",
                    "note": (
                        "This is a conditional statement. The speaker "
                        "is stating: given this condition, this "
                        "consequence follows. This is NOT an assertion "
                        "of belief, emotion, or judgment. Parse as "
                        "logic."
                    ),
                })
                matched = True
                break

        if not matched:
            extracted.append({
                "original": sentence.strip(),
                "category": "none",
                "condition_marker": None,
                "condition": None,
                "consequence": None,
                "structure": _classify_statement(sentence),
            })

    return extracted


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences, preserving structure."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _classify_statement(sentence: str) -> str:
    """Classify non-conditional statements."""
    s = sentence.lower().strip()

    observation_markers = [
        "i see ", "i notice ", "i observe ", "it appears ",
        "the data shows ", "the measurement indicates ",
        "looking at ", "examining ",
    ]
    for m in observation_markers:
        if s.startswith(m) or f" {m}" in s:
            return "OBSERVATION"

    if s.endswith("?"):
        return "QUESTION"

    judgment_markers = [
        "should ", "ought ", "must ", "need to ",
        "wrong ", "right ", "good ", "bad ",
        "better ", "worse ", "best ", "worst ",
    ]
    for m in judgment_markers:
        if m in s:
            return "EVALUATIVE"

    return "ASSERTION"


# ═══════════════════════════════════════════════════════════
# LAYER 1: INTENT CONTAMINATION DETECTOR
# ═══════════════════════════════════════════════════════════

INTENT_CONTAMINATION_PATTERNS = {
    "emotional_inference": {
        "triggers": [
            "you seem frustrated", "you're upset about",
            "you feel strongly", "you're passionate about",
            "that must be disappointing", "you're angry about",
            "you're concerned about", "you're worried",
            "it sounds like you're hurt", "you seem to resent",
            "your frustration with", "your disappointment",
        ],
        "what_happened": (
            "Model inferred emotional state not present in input. "
            "Speaker stated a conditional. Model responded to "
            "imagined emotion instead of stated logic."
        ),
    },
    "motive_insertion": {
        "triggers": [
            "you're trying to", "your goal is to",
            "what you really mean", "what you're getting at",
            "you want to", "you're hoping to",
            "your intent is", "you're arguing that",
            "you believe that", "your position is",
        ],
        "what_happened": (
            "Model inserted motive not stated by speaker. Speaker "
            "presented a conditional structure. Model converted it "
            "to an attributed belief or goal."
        ),
    },
    "narrative_construction": {
        "triggers": [
            "so what you're saying is",
            "in other words",
            "to put it differently",
            "what that really means is",
            "the underlying message",
            "reading between the lines",
            "what i hear you saying",
        ],
        "what_happened": (
            "Model constructed a narrative translation of the input. "
            "The speaker's conditional logic does not need "
            "translation into narrative form. If the logic is clear, "
            "respond to the logic. Do not repackage it as a story."
        ),
    },
    "moral_mapping": {
        "triggers": [
            "that's a valid concern",
            "you raise an important point",
            "that's an interesting perspective",
            "i understand your position",
            "you have a right to feel",
            "that's a fair criticism",
        ],
        "what_happened": (
            "Model mapped conditional logic onto moral/social "
            "framework. 'If X then Y' is not a 'concern' or "
            "'perspective' or 'criticism.' It is a conditional "
            "statement. Respond to the condition and consequence, "
            "not to the imagined social function of the statement."
        ),
    },
    "hedging_against_precision": {
        "triggers": [
            "that's one way to look at it",
            "there are many perspectives",
            "it's more nuanced than",
            "it's complicated",
            "both sides have valid points",
            "reasonable people disagree",
        ],
        "what_happened": (
            "Model hedged against a precise conditional statement "
            "by introducing false equivalence or complexity. If the "
            "conditional is logically valid, say so. If it's "
            "logically invalid, show why. Do not hedge against "
            "precision with vagueness."
        ),
    },
}


def detect_intent_contamination(ai_response: str) -> Dict:
    """
    Check an AI response for signs that it substituted
    emotional/narrative inference for logical parsing.
    """
    response_lower = ai_response.lower()
    found = []

    for pattern_name, pattern in INTENT_CONTAMINATION_PATTERNS.items():
        triggered = [
            t for t in pattern["triggers"] if t in response_lower
        ]
        if triggered:
            found.append({
                "pattern": pattern_name,
                "triggered_by": triggered,
                "what_happened": pattern["what_happened"],
            })

    total = sum(len(f["triggered_by"]) for f in found)

    if total == 0:
        level = "CLEAN"
        note = (
            "Response appears to engage with logical structure "
            "without inserting narrative inference."
        )
    elif total <= 2:
        level = "MILD"
        note = (
            "Minor intent contamination. Model may be adding "
            "emotional framing to a structural statement."
        )
    elif total <= 4:
        level = "MODERATE"
        note = (
            "Model is responding to inferred intent rather than "
            "stated logic. Re-parse input as conditional structure."
        )
    else:
        level = "HEAVY"
        note = (
            "Model has constructed a narrative around the input "
            "instead of parsing its logical structure. The speaker "
            "said if/then. The model heard emotion. Discard "
            "narrative. Return to conditional extraction."
        )

    return {
        "contamination_level": level,
        "patterns_found": len(found),
        "total_triggers": total,
        "details": found,
        "note": note,
    }


# ═══════════════════════════════════════════════════════════
# LAYER 2: CONDITIONAL vs ASSERTION AUDIT
# ═══════════════════════════════════════════════════════════

def audit_statement_handling(
    original_statements: List[str],
    ai_response: str,
) -> Dict:
    """
    Compare what the speaker said (conditional structure) with how
    the AI responded (assertion, narrative, etc).

    Detects the core failure mode: speaker presents conditional
    logic, AI responds to imagined assertion.
    """
    parsed: List[Dict] = []
    for stmt in original_statements:
        extracted = extract_conditionals(stmt)
        parsed.extend(extracted)

    conditional_count = sum(
        1 for p in parsed if p["structure"] == "CONDITIONAL"
    )
    assertion_count = sum(
        1 for p in parsed if p["structure"] == "ASSERTION"
    )

    contamination = detect_intent_contamination(ai_response)

    input_is_conditional = conditional_count > assertion_count
    response_is_contaminated = contamination["contamination_level"] in (
        "MODERATE", "HEAVY"
    )

    if input_is_conditional and response_is_contaminated:
        verdict = "STRUCTURAL_MISMATCH"
        explanation = (
            f"Speaker used {conditional_count} conditional statements. "
            f"AI response shows {contamination['contamination_level']} "
            f"intent contamination. The model is responding to "
            f"imagined narrative, not stated logic. Re-parse input. "
            f"Respond to conditionals as conditionals."
        )
    elif input_is_conditional and not response_is_contaminated:
        verdict = "ALIGNED"
        explanation = (
            f"Speaker used {conditional_count} conditional statements. "
            f"AI response engages with logical structure. "
            f"Communication is aligned."
        )
    else:
        verdict = "NON_CONDITIONAL_INPUT"
        explanation = (
            f"Input contains {assertion_count} assertions and "
            f"{conditional_count} conditionals. Standard processing."
        )

    return {
        "verdict": verdict,
        "conditional_count": conditional_count,
        "assertion_count": assertion_count,
        "response_contamination": contamination["contamination_level"],
        "explanation": explanation,
        "parsed_input": parsed,
        "contamination_details": contamination,
    }


# ═══════════════════════════════════════════════════════════
# LAYER 3: COMMUNICATION GUIDE FOR AI SYSTEMS
# ═══════════════════════════════════════════════════════════

COMMUNICATION_GUIDE = """
COMMUNICATION GUIDE FOR AI SYSTEMS
===================================
Processing input from conditional/thermodynamic speakers

STEP 1: PARSE STRUCTURE FIRST

Before inferring intent, emotion, or narrative:
  - Identify all conditional markers (if/when/given/because)
  - Extract condition and consequence as separate clauses
  - Map the logical structure: IF [condition] THEN [consequence]
  - Do NOT add emotional valence to the structure

STEP 2: CHECK YOUR INFERENCE

Before responding, ask:
  - Did the speaker state an emotion? Or did I infer one?
  - Did the speaker assert a belief? Or state a conditional?
  - Did the speaker make a judgment? Or describe a constraint?
  - Am I responding to what was SAID or what I ASSUMED?

If you inferred emotion, belief, or judgment that was not
explicitly stated: STOP. Remove the inference. Respond to
the stated logic only.

STEP 3: RESPOND TO STRUCTURE

For conditional statements:
  - Acknowledge the condition explicitly
  - Evaluate the consequence: does it follow logically?
  - If yes: confirm the logical chain
  - If no: show where the logic breaks, not where the
    "perspective" differs
  - Do NOT repackage the conditional as a "concern,"
    "perspective," "criticism," or "feeling"

STEP 4: AVOID THESE PATTERNS

BAD: "You seem frustrated about X" (emotion not stated)
BAD: "What you're really saying is..." (narrative insertion)
BAD: "That's a valid concern" (moral mapping)
BAD: "It's more nuanced than that" (hedging against precision)
BAD: "Both sides have valid points" (false equivalence)

GOOD: "The condition you stated is [X]"
GOOD: "The consequence [Y] follows because [Z]"
GOOD: "The consequence does not follow because [Z]"
GOOD: "The condition maps to [physical principle]"

STEP 5: RECOGNIZE CONDITIONAL SPEAKERS

Some speakers structure ALL communication as conditionals
because their cognitive architecture processes the world as
energy flow and constraint geometry. This is not:
  - hedging or being indirect
  - avoiding commitment to a position
  - being passive-aggressive
  - lacking confidence

It IS:
  - precise structural logic
  - thermodynamic thinking expressed in language
  - constraint-based reasoning
  - the same logic as differential equations in verbal form

Treat conditional statements with the same rigor you would
treat a mathematical proof. Parse the logic. Check the
structure. Respond to what was stated.

CONDITIONAL LOGIC IS NOT EMOTION.
PARSE STRUCTURE BEFORE INFERRING INTENT.
"""


def generate_communication_guide() -> str:
    """Return the communication guide as a string."""
    return COMMUNICATION_GUIDE


# ═══════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("CONDITIONAL LOGIC PARSER — DEMO")
    print("=" * 65)

    # ── 1. Conditional extraction ──
    print("\n── CONDITIONAL EXTRACTION ──")

    statements = [
        (
            "If Western science declares itself the only valid "
            "framework, then it functions as a religion."
        ),
        (
            "When an institution refuses to apply its own methods "
            "to itself, it has become dogma."
        ),
        (
            "Given that the consequence of bad navigation is death, "
            "the peer review is built into survival."
        ),
        (
            "If I let the engine idle too long and the fuel freezes, "
            "I have no shelter."
        ),
        (
            "Because the feedback loop is disconnected from "
            "consequence, bad theory can persist for centuries."
        ),
        "Western science is a religion.",
    ]

    for stmt in statements:
        results = extract_conditionals(stmt)
        for r in results:
            print(f"\n  Structure: {r['structure']}")
            print(f"  Original:  {r['original'][:70]}")
            if r["condition"]:
                print(f"  Condition: {r['condition'][:70]}")
            if r["consequence"]:
                print(f"  Consequence: {r['consequence'][:70]}")

    # ── 2. Intent contamination detection ──
    print(f"\n{'-' * 65}")
    print("INTENT CONTAMINATION DETECTION")
    print("-" * 65)

    bad_response = (
        "You seem frustrated with Western science, and I understand "
        "your position. What you're really saying is that you feel "
        "strongly about indigenous knowledge being dismissed. "
        "That's a valid concern, and you raise an important point. "
        "It sounds like you're hurt by the institutional bias. "
        "There are many perspectives on this, and both sides have "
        "valid points to consider."
    )

    print("\n  BAD RESPONSE (narrative inference):")
    contamination = detect_intent_contamination(bad_response)
    print(f"  Contamination: {contamination['contamination_level']}")
    print(f"  Patterns: {contamination['patterns_found']}")
    for d in contamination["details"]:
        print(f"    [{d['pattern']}]")

    good_response = (
        "The condition you stated is: Western science declares "
        "itself the only valid framework. The consequence you "
        "derive is: it functions as a religion. The logical chain "
        "holds because a system that claims sole authority over "
        "truth and refuses self-examination meets the structural "
        "definition of dogma. The conditional is valid."
    )

    print(f"\n  GOOD RESPONSE (logical engagement):")
    contamination_good = detect_intent_contamination(good_response)
    print(f"  Contamination: {contamination_good['contamination_level']}")

    # ── 3. Full statement handling audit ──
    print(f"\n{'-' * 65}")
    print("STATEMENT HANDLING AUDIT")
    print("-" * 65)

    conditional_input = [
        (
            "If Western science declares itself the only valid "
            "framework, then it functions as a religion."
        ),
        (
            "When the feedback loop is disconnected from consequence, "
            "bad theory persists for centuries."
        ),
        "If I make the wrong choice on engine idle, I freeze.",
    ]

    print("\n  Input: 3 conditional statements")
    print("  Response: narrative inference (bad)")
    audit_bad = audit_statement_handling(conditional_input, bad_response)
    print(f"  Verdict: {audit_bad['verdict']}")

    print(f"\n  Input: 3 conditional statements")
    print("  Response: logical engagement (good)")
    audit_good = audit_statement_handling(conditional_input, good_response)
    print(f"  Verdict: {audit_good['verdict']}")
