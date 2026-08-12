# interaction_taxonomy.py
# earth-systems-physics / extraction_dynamics
# CC0 — No Rights Reserved
#
# Sign conventions for pairwise species interactions, and the one
# diagnostic that separates predation from extraction.
#
# The pair is written (consumer, resource). The sign is the effect of
# the interaction on each partner's per-capita growth rate.
#
#   predation        (+,-)  consumer numerical response COUPLED to resource
#   parasitism       (+,-)  coupled, sublethal per event
#   parasitoidism    (+,-)  coupled, lethal, one host per consumer
#   hyperpredation   (+,-)  consumer sustained by an ALTERNATE or exogenous
#                            source while depressing this resource toward
#                            extinction
#   mining           (+,0)  resource has no recruitment term at all
#   competition      (-,-)  mutual interference
#   mutualism        (+,+)  reciprocal benefit
#   commensalism     (+,0)  one benefits, other unaffected
#   amensalism       (-,0)  one harmed, other unaffected
#
# THE DIAGNOSTIC
# --------------
# The line between predation and extraction is NOT intent, harm, scale,
# efficiency, or technology. It is one question:
#
#       does dP/dt depend on N ?
#
# A predator whose prey collapses loses its own growth term and declines.
# That coupling IS the negative feedback that bounds the interaction.
# An extractor carrying an exogenous subsidy S keeps its growth term when
# N goes to zero. Self-limitation is not weak in that case — it is
# ABSENT, and every governance layer proposed for such a system is an
# attempt to re-supply by fiat the feedback that S deleted.
#
# Standard library only.

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────
# TAXONOMY
# ─────────────────────────────────────────────


@dataclass(frozen=True)
class Interaction:
    """
    One pairwise interaction type.

    name              : label
    sign_pair         : (effect on consumer, effect on resource) in
                        {'+', '-', '0'}
    consumer_coupled  : does the consumer's growth term depend on this
                        resource's density?
    resource_recruits : does the resource have a recruitment/regeneration
                        term on the timescale of the interaction?
    diagnostic        : the operational test that identifies it
    bounding_feedback : what stops the interaction, if anything
    """
    name:              str
    sign_pair:         Tuple[str, str]
    consumer_coupled:  bool
    resource_recruits: bool
    diagnostic:        str
    bounding_feedback: str
    examples:          Tuple[str, ...]


INTERACTIONS: Dict[str, Interaction] = {
    "predation": Interaction(
        name="predation",
        sign_pair=("+", "-"),
        consumer_coupled=True,
        resource_recruits=True,
        diagnostic="dP/dt contains e*f(N)*P and no term that survives N -> 0",
        bounding_feedback=(
            "prey depletion removes the consumer's own growth term; "
            "consumer declines before prey is eliminated"
        ),
        examples=("lynx-hare", "wolf-moose", "cod-capelin"),
    ),
    "parasitism": Interaction(
        name="parasitism",
        sign_pair=("+", "-"),
        consumer_coupled=True,
        resource_recruits=True,
        diagnostic="per-event effect sublethal; consumer reproduction "
                   "still scales with host density",
        bounding_feedback="host decline reduces transmission and consumer "
                          "reproduction",
        examples=("Ophryocystis elektroscirrha in monarchs",
                  "sea lice on salmon"),
    ),
    "parasitoidism": Interaction(
        name="parasitoidism",
        sign_pair=("+", "-"),
        consumer_coupled=True,
        resource_recruits=True,
        diagnostic="one host consumed per consumer generation; strongly "
                   "coupled, often with delay",
        bounding_feedback="host scarcity collapses consumer recruitment "
                          "one generation later",
        examples=("ichneumonid wasps", "tachinid flies"),
    ),
    "hyperpredation": Interaction(
        name="hyperpredation",
        sign_pair=("+", "-"),
        consumer_coupled=False,
        resource_recruits=True,
        diagnostic=(
            "dP/dt retains a subsidy term S that does not vanish as "
            "N -> 0; consumer persists at, and past, resource extinction"
        ),
        bounding_feedback=(
            "NONE internal to the pair. Bounding must be imposed from "
            "outside, and any such rule is a substitute for the feedback "
            "the subsidy removed."
        ),
        examples=("introduced cats subsidised by rabbits driving native "
                  "prey extinct",
                  "fossil-subsidised fishing fleet on a depleted stock",
                  "tillage agriculture subsidised by fertiliser on "
                  "declining soil carbon"),
    ),
    "mining": Interaction(
        name="mining",
        sign_pair=("+", "0"),
        consumer_coupled=False,
        resource_recruits=False,
        diagnostic="the resource equation has no recruitment term on any "
                   "human-relevant timescale (r = 0)",
        bounding_feedback="stock exhaustion only; no regeneration to "
                          "outrun and none to wait for",
        examples=("phosphate rock", "fossil hydrocarbons",
                  "fossil groundwater", "helium"),
    ),
    "competition": Interaction(
        name="competition",
        sign_pair=("-", "-"),
        consumer_coupled=True,
        resource_recruits=True,
        diagnostic="each population depresses the other's per-capita "
                   "growth rate",
        bounding_feedback="mutual depression; exclusion or coexistence "
                          "depending on relative interference",
        examples=("interference competition", "resource competition"),
    ),
    "mutualism": Interaction(
        name="mutualism",
        sign_pair=("+", "+"),
        consumer_coupled=True,
        resource_recruits=True,
        diagnostic="both per-capita growth rates increase with the "
                   "partner's density",
        bounding_feedback="saturation; otherwise unbounded positive "
                          "feedback (the 'orgy of mutual benefaction')",
        examples=("mycorrhizae-plant", "pollinator-plant",
                  "coral-zooxanthellae"),
    ),
    "commensalism": Interaction(
        name="commensalism",
        sign_pair=("+", "0"),
        consumer_coupled=True,
        resource_recruits=True,
        diagnostic="consumer benefits; resource per-capita growth "
                   "unchanged within measurement error",
        bounding_feedback="consumer's own density dependence only",
        examples=("epiphytes on trees", "cattle egrets"),
    ),
    "amensalism": Interaction(
        name="amensalism",
        sign_pair=("-", "0"),
        consumer_coupled=False,
        resource_recruits=True,
        diagnostic="one population is depressed; the other gains nothing "
                   "measurable",
        bounding_feedback="none from the pair; the harming population is "
                          "indifferent to the outcome",
        examples=("trampling", "allelopathy without uptake",
                  "bycatch discard mortality"),
    ),
}


# Interactions in which the consumer's growth does NOT depend on this
# resource's density. These are the ones with no internal brake.
UNCOUPLED = tuple(k for k, v in INTERACTIONS.items() if not v.consumer_coupled)


def get(name: str) -> Interaction:
    """Look up an interaction by name. Raises KeyError with the valid set."""
    key = name.lower().strip()
    if key not in INTERACTIONS:
        raise KeyError(
            f"unknown interaction '{name}'; "
            f"valid: {sorted(INTERACTIONS)}"
        )
    return INTERACTIONS[key]


def classify(consumer_coupled: bool, resource_recruits: bool,
             consumer_benefits: bool = True,
             resource_harmed: bool = True) -> str:
    """
    Classify an interaction from its structural properties alone.

    This is the whole point of the taxonomy: the classification is a
    function of the EQUATIONS, not of intent, harm, scale, or technology.

    consumer_coupled  : does the consumer's growth term depend on N?
    resource_recruits : does the resource regenerate on the interaction's
                         timescale?
    consumer_benefits : does the consumer gain?
    resource_harmed   : is the resource depressed?
    returns: interaction name
    """
    if not resource_harmed:
        return "commensalism" if consumer_benefits else "neutral"
    if not consumer_benefits:
        return "amensalism"
    if not resource_recruits:
        return "mining"
    return "predation" if consumer_coupled else "hyperpredation"


def summary() -> List[Dict[str, object]]:
    """Flat, JSON-safe view of the taxonomy."""
    return [
        {
            "name": i.name,
            "sign_pair": "".join(i.sign_pair),
            "consumer_coupled": i.consumer_coupled,
            "resource_recruits": i.resource_recruits,
            "diagnostic": i.diagnostic,
            "bounding_feedback": i.bounding_feedback,
            "examples": list(i.examples),
        }
        for i in INTERACTIONS.values()
    ]


if __name__ == "__main__":
    print("PAIRWISE INTERACTION TAXONOMY  (consumer, resource)")
    print("=" * 70)
    for i in INTERACTIONS.values():
        print(f"\n{i.name.upper():16s} {''.join(i.sign_pair)}   "
              f"coupled={i.consumer_coupled}  "
              f"recruits={i.resource_recruits}")
        print(f"  test:  {i.diagnostic}")
        print(f"  brake: {i.bounding_feedback}")

    print("\n\nSTRUCTURAL CLASSIFICATION")
    print("=" * 70)
    cases = [
        ("wolf on moose",              True,  True),
        ("subsidised fleet on stock",  False, True),
        ("pump on fossil aquifer",     False, False),
        ("pump on recharging aquifer", True,  True),
    ]
    for label, coupled, recruits in cases:
        print(f"  {label:30s} coupled={str(coupled):5s} "
              f"recruits={str(recruits):5s} -> {classify(coupled, recruits)}")

    print(f"\nuncoupled (no internal brake): {UNCOUPLED}")
