"""
diachronic_anchor.py
CC0 / stdlib-only / phone-buildable
Manifold Framework companion module. Entropy Archive: Module 003 candidate.

PROBLEM IT KILLS
================
LLMs treat every textual instance of a phrase as a synchronic snapshot in a
bag, frequency-weighted. So "founded on these principles" (1787) and its
1894 reinterpretation and its 2024 consensus reread collapse into ONE cluster,
weighted heaviest toward the training-tail (2024). The model then reads the
past THROUGH the present and calls it accurate history.

Two failures compound:
  1. TEMPORAL COLLAPSE  - same surface form, 3 different semantic loads,
                          flattened to one bag.
  2. TELEOLOGICAL COLLAPSE - model reads backward from now and assumes every
                          prior version was AIMED at now. Cannot see that
                          1894 was solving for 1894, not prophesying 2024.

This module refuses both by forcing the utterance onto the manifold as a
TRAJECTORY of (coordinate, intent, semantic_vector, problem_solved) steps,
then detecting the RHETORICAL LOAD each rewrite adds and the PATTERN across
the whole trajectory (the direction the rewrites are aiming).

Output is a trajectory, never a "which reading is correct" verdict. Moral
judgment is not the operation. The operation is: locate, extract, map drift,
name the work each layer does, surface the pattern, state the falsifier.

STATE VECTOR (from Manifold Framework v2.0):
  t, G, P, E, I, C, K_format, K_function, S
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ----------------------------------------------------------------------
# One point on the trajectory: an utterance AS READ at a given coordinate
# ----------------------------------------------------------------------
@dataclass
class AnchorPoint:
    year: int
    who: str                     # whose stance authored THIS reading
    coordinate: dict             # partial/full state vector; unknown -> "unknown"
    semantic_load: str           # what the words MEAN at this coordinate
    intent: str                  # what THIS author is doing by saying it
    problem_solved: str          # the problem in THEIR coordinate space
    S: Optional[str] = None      # substrate urgency: "high"/"low"/"unknown"

    def as_row(self):
        return {
            "year": self.year,
            "who": self.who,
            "coordinate": self.coordinate,
            "semantic_load": self.semantic_load,
            "intent": self.intent,
            "problem_solved": self.problem_solved,
            "S": self.S or "unknown",
        }


# ----------------------------------------------------------------------
# Rhetorical-load taxonomy: what WORK does a re-anchoring do?
# These are named patterns, not moral labels. Detection is by role, not by
# whether the move is "good" or "bad".
# ----------------------------------------------------------------------
RHETORICAL_MOVES = {
    "authority_by_ancestry":
        "legitimizes a NEW order by tying it to ancestral/founding authority",
    "consensus_naturalization":
        "presents the current majority reading AS the accurate original meaning",
    "enlightened_reader":
        "positions the present author as the one who FINALLY understands the past",
    "originalist_freeze":
        "claims the original meaning is fixed and self-evident, blocking re-reading",
    "purification":
        "reframes the text to expel a faction / mark insiders vs outsiders",
    "mobilization":
        "converts a descriptive statement into a call to present action",
    "sanctification":
        "moves the text from contestable claim to sacred/untouchable ground",
    "none_detected":
        "no re-anchoring load identified; reading may be within-coordinate",
}


def classify_rhetorical_load(point: AnchorPoint, is_origin: bool) -> List[str]:
    """
    Heuristic classifier over the intent/problem_solved text.
    Returns the move code(s). This is a SKELETON detector - it flags the
    shape from keywords in the supplied intent. The human/AI supplies the
    intent text; this names the pattern. No infill of unknowns.
    """
    if is_origin:
        return ["origin_stance"]  # the origin is not a re-anchoring

    text = (point.intent + " " + point.problem_solved).lower()
    hits = []

    if any(k in text for k in ["ancestr", "founding", "forefather", "heritage",
                               "tradition", "legitim"]):
        hits.append("authority_by_ancestry")
    if any(k in text for k in ["consensus", "everyone knows", "settled",
                               "obviously mean", "always meant"]):
        hits.append("consensus_naturalization")
    if any(k in text for k in ["finally", "correct read", "true meaning",
                               "properly understand", "enlighten"]):
        hits.append("enlightened_reader")
    if any(k in text for k in ["fixed", "self-evident", "plain meaning",
                               "originalist", "as written"]):
        hits.append("originalist_freeze")
    if any(k in text for k in ["expel", "faction", "insider", "outsider",
                               "purify", "real ones", "true believers"]):
        hits.append("purification")
    if any(k in text for k in ["must act", "demands", "call to", "mobiliz",
                               "rally"]):
        hits.append("mobilization")
    if any(k in text for k in ["sacred", "untouchable", "hallowed",
                               "sanctif", "reverence"]):
        hits.append("sanctification")

    return hits if hits else ["none_detected"]


# ----------------------------------------------------------------------
# The trajectory analysis
# ----------------------------------------------------------------------
def diachronic_anchor(utterance: str, trajectory: List[AnchorPoint]) -> dict:
    """
    utterance   : the surface phrase whose meaning is being tracked
    trajectory  : chronological list of AnchorPoints (>= 2, origin first)

    Returns a trajectory dict. Never returns a 'which reading is true' verdict.
    """
    if len(trajectory) < 2:
        return {"error": "need >= 2 points (origin + at least one re-anchor)"}

    ordered = sorted(trajectory, key=lambda p: p.year)
    origin = ordered[0]

    steps = []
    load_sequence = []
    for i, pt in enumerate(ordered):
        is_origin = (i == 0)
        loads = classify_rhetorical_load(pt, is_origin)
        if not is_origin:
            load_sequence.extend([m for m in loads if m != "none_detected"])
        steps.append({
            "point": pt.as_row(),
            "rhetorical_load": loads,
            "load_meaning": [RHETORICAL_MOVES.get(m, m) for m in loads],
        })

    # semantic drift: pairwise, origin-meaning vs each later reading
    drift = []
    for pt in ordered[1:]:
        drift.append({
            "from_year": origin.year,
            "to_year": pt.year,
            "origin_meant": origin.semantic_load,
            "later_read_as": pt.semantic_load,
            "gap": "SAME surface form, different semantic load"
                   if pt.semantic_load != origin.semantic_load
                   else "load appears preserved",
        })

    # pattern across the whole trajectory: is there a DIRECTION?
    pattern = _detect_trajectory_pattern(load_sequence)

    # teleology guard: flag if any later intent claims the origin AIMED at it
    teleology_flags = []
    for pt in ordered[1:]:
        t = (pt.intent + " " + pt.semantic_load).lower()
        if any(k in t for k in ["always meant", "originally intended this",
                                "founders wanted", "meant what we now",
                                "predicted", "prophes"]):
            teleology_flags.append({
                "year": pt.year, "who": pt.who,
                "flag": "TELEOLOGICAL: later reading claims origin aimed at it. "
                        "Origin was solving for origin's coordinate, not this one."
            })

    return {
        "utterance": utterance,
        "origin_coordinate": origin.as_row(),
        "trajectory_steps": steps,
        "semantic_drift": drift,
        "rhetorical_load_sequence": load_sequence,
        "pattern_across_trajectory": pattern,
        "teleology_flags": teleology_flags,
        "falsifiable_claim": _build_falsifier(ordered, pattern),
        "audit_note": "Output is a trajectory, not a truth-verdict. Each layer "
                      "solved ITS problem in ITS coordinate. The pattern is the "
                      "data. Read direction, not endpoint.",
    }


def _detect_trajectory_pattern(load_sequence: List[str]) -> dict:
    """
    Name the aim of the rewrite-sequence. E.g. an ancestry move followed by a
    naturalization move = 'past mobilized as tool, then tool naturalized as
    history' — the classic teleological laundering path.
    """
    if not load_sequence:
        return {"direction": "none",
                "reading": "no re-anchoring load across trajectory"}

    seq = load_sequence
    has = lambda m: m in seq

    if has("authority_by_ancestry") and has("consensus_naturalization"):
        return {"direction": "authority_laundering",
                "reading": "step 1 mobilizes the past as a rhetorical tool "
                           "(authority-by-ancestry); a later step naturalizes "
                           "that tool AS accurate history (consensus). The "
                           "present reading is made to look grounded in origin."}
    if has("authority_by_ancestry") and has("enlightened_reader"):
        return {"direction": "authority_then_capture",
                "reading": "the past is invoked as authority, then a present "
                           "author claims sole correct access to it — capture "
                           "of the origin's legitimacy for a present agenda."}
    if has("originalist_freeze") and has("mobilization"):
        return {"direction": "freeze_and_wield",
                "reading": "meaning declared fixed/self-evident, then wielded "
                           "to compel present action — contestation blocked "
                           "while the frozen reading is mobilized."}
    if has("consensus_naturalization"):
        return {"direction": "naturalization",
                "reading": "current majority reading presented as the original "
                           "meaning; drift erased, present made to look eternal."}
    if has("sanctification"):
        return {"direction": "sanctification",
                "reading": "text moved from contestable to sacred; re-reading "
                           "reframed as transgression."}
    return {"direction": "mixed",
            "reading": f"loads present: {sorted(set(seq))}; no single dominant "
                       f"direction — inspect steps individually."}


def _build_falsifier(ordered: List[AnchorPoint], pattern: dict) -> str:
    yrs = [p.year for p in ordered]
    return (
        f"If each author in {yrs} was solving the problem stated at their own "
        f"coordinate (not aiming at a later one), then the WAY the text was "
        f"re-anchored should show the '{pattern['direction']}' pattern in "
        f"period-native sources (their own writings, not later summaries). "
        f"TEST: read each period's PRIMARY texts on their own terms. If the "
        f"re-anchoring load is absent there and only appears in later "
        f"characterizations, the pattern is falsified for that step. If a "
        f"later author's re-reading is found VERBATIM in the origin's own "
        f"primary text, the drift claim is falsified."
    )


# ----------------------------------------------------------------------
# WORKED EXAMPLE — the founding-principles case
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import json

    traj = [
        AnchorPoint(
            year=1787,
            who="framers, writing from within their own stance",
            coordinate={"t": 1787, "G": "post-revolutionary agrarian republic",
                        "E": "mercantile+agrarian, chattel slavery present",
                        "I": "new federal compact, propertied franchise",
                        "C": "enlightenment + classical-republican vocabulary",
                        "K_format": "legal-text", "K_function": "structural-charter",
                        "P": "propertied white male authors; most voices unrecorded"},
            semantic_load="'these principles' = a contested compromise among "
                          "factions, load-bearing for a specific franchise and "
                          "economic order of that moment",
            intent="establish a workable federal structure among rival interests",
            problem_solved="how to bind 13 rival states without collapse",
            S="high",
        ),
        AnchorPoint(
            year=1894,
            who="post-Reconstruction nationalist historians",
            coordinate={"t": 1894, "E": "industrializing", "I": "consolidated union",
                        "C": "manifest-destiny + reunion narrative"},
            semantic_load="'these principles' = timeless national ideals the "
                          "founders eternally intended",
            intent="legitimize the present national order via founding authority; "
                   "tie it to ancestral heritage",
            problem_solved="how to manufacture a unified origin story after "
                           "civil war and reunion",
            S="low",
        ),
        AnchorPoint(
            year=2024,
            who="contemporary consensus reading",
            coordinate={"t": 2024, "E": "financialized post-industrial",
                        "I": "mass-franchise administrative state",
                        "C": "present WEIRD-default vocabulary"},
            semantic_load="'these principles' = what the founders always meant, "
                          "finally understood correctly by us",
            intent="present current interpretation as the accurate original; "
                   "settled consensus",
            problem_solved="how to ground present arrangements as the fulfilment "
                           "of origin",
            S="low",
        ),
    ]

    out = diachronic_anchor("founded on these principles", traj)
    print(json.dumps(out, indent=2, ensure_ascii=False))
