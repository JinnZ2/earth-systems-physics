# estimate_direction_tally.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Which way do the estimates miss? A tally of earlier estimates against later
# observations, with the DIRECTION of each miss recorded, so that "mostly
# underestimated" is a count with its denominator rather than an impression.
#
# Co-authored, human + Claude, 2026-10-28. Asked for by Kavik after the
# Antarctic 2026 reads ("every estimate they run seems to end up
# underestimated ... the cascade effects end up getting lost").
#
# WHAT THIS MODULE DOES
# ---------------------
# 1. MISSES: earlier estimate vs later observation, each with a direction
#    in the harm sense (UNDER = the observed change was worse than
#    estimated; OVER = milder; SIGN = opposite sign; NO_ESTIMATE = the event
#    had no estimate at all), a kind, a status and a source grade.
# 2. A tally over the decided entries, with CONDITIONAL / OPEN entries
#    counted apart and never folded in.
# 3. CANDIDATE_OMISSIONS for McCormack et al. 2026 (the high-end exclusion):
#    couplings that may be outside its ensemble, each with the direction it
#    would push. The paper was NOT read; any of these may be in it. They are
#    questions to check, not findings.
# 4. corruption_chain direction codes (+1 UNDER, -1 OVER, 0 otherwise), so a
#    miss can enter that module's compounding / masking reconciliation.
#
# THE FRAME IS SELECTED ON THE OUTCOME
# ------------------------------------
# Entries here are misses this session encountered or remembered. A list
# built that way over-represents memorable misses, and a famous miss is
# more likely to be one where the harm came early. So the tally reports
# COUNTS and refuses a representative RATE: rate_low is None with the
# reason. The fix is a frame fixed before looking, e.g. every AR5 or AR6
# projection that has an observable by 2026, scored whatever it shows.
# That frame is PROPOSED here and not run.
#
# Stdlib only. No numbers are carried from memory: each entry's source and
# its read depth are stated.

from typing import Dict, List, Optional

UNDER = "UNDER"              # observed change worse than estimated
OVER = "OVER"                # observed change milder than estimated
SIGN = "SIGN"                # observed change has the opposite sign
NO_ESTIMATE = "NO_ESTIMATE"  # nothing was estimated; the event arrived unmodelled

DECIDED = "DECIDED"          # direction settled at the read depth stated
CONDITIONAL = "CONDITIONAL"  # direction depends on an open check
OPEN = "OPEN"                # attribution itself unsettled

CITED_ABSTRACT = "CITED_ABSTRACT"
CITED_PRESS = "CITED_PRESS"
IN_REPO = "IN_REPO"
PROPOSED = "PROPOSED"

MISSES: List[Dict] = [
    {"id": "T1", "what": "Arctic September sea-ice decline",
     "estimate": "IPCC AR4 models", "observed": "satellite + historical record, "
     "1953-2006 and 1979-2006",
     "direction": UNDER, "kind": "rate", "status": DECIDED,
     "note": "none or very few model runs match the observed trend",
     "source": "Stroeve et al. 2007, GRL 34:L09501, doi:10.1029/2007GL029703",
     "grade": CITED_ABSTRACT},
    {"id": "T2", "what": "global sea-level rise since 1990",
     "estimate": "IPCC TAR projections", "observed": "tide gauge + altimetry to ~2006",
     "direction": UNDER, "kind": "rate", "status": DECIDED,
     "note": "'may be responding more quickly ... than our current generation "
             "of models indicates'; no number in the abstract read",
     "source": "Rahmstorf et al. 2007, Science 316:709", "grade": CITED_ABSTRACT},
    {"id": "T3", "what": "Antarctic sea-ice extent trend",
     "estimate": "18 CMIP5 models, 1979-2005: decrease in every month "
                 "(largest -0.40 million km^2/decade, September)",
     "observed": "slight increase over ~30 years",
     "direction": OVER, "kind": "sign of trend", "status": DECIDED,
     "note": "models lost ice the observations did not; then after 2016 the "
             "observed ice fell faster (antarctic_sea_ice_2026). The miss is "
             "in timing and shape, not only size",
     "source": "Turner et al. 2013, J. Climate 26:1473", "grade": CITED_ABSTRACT},
    {"id": "T4", "what": "sea ice under added Antarctic meltwater",
     "estimate": "11 models: +0.71..4.14 million km^2 at 0.1 Sv",
     "observed": "decline from 2016 while ice-shelf melt rose (per the repo's loop)",
     "direction": SIGN, "kind": "mechanism sign", "status": OPEN,
     "note": "attribution open: ice_shelf_melt_feedback_2026.SIGN_TENSION R1-R4",
     "source": "Pauling et al. 2026 preprint", "grade": CITED_ABSTRACT},
    {"id": "T5", "what": "repo's CDW ice-shelf basal-melt increment",
     "estimate": "layer_4 cdw_basal_melt_rate_Gt_yr, 104.8 Gt/yr",
     "observed": "Youngs et al. 2026: feedback = 2/3 of the increase",
     "direction": UNDER, "kind": "magnitude (x3 if forced-only)",
     "status": CONDITIONAL,
     "note": "only if layer_4's sensitivity is forced-only (F1)",
     "source": "ice_shelf_melt_feedback_2026", "grade": IN_REPO},
    {"id": "T6", "what": "high-end Antarctic sea-level scenario",
     "estimate": "IPCC low-likelihood high-impact, as rendered 7 -> 13 mm/yr",
     "observed": "McCormack et al. 2026 synthesis rules it out",
     "direction": OVER, "kind": "model revision, not an observation",
     "status": OPEN,
     "note": "rendering conflict unresolved (antarctic_slr_2026 S1); see "
             "CANDIDATE_OMISSIONS for what the exclusion may leave out",
     "source": "antarctic_slr_2026", "grade": CITED_PRESS},
    {"id": "T7", "what": "Breid Bay winter polynya, August 2024",
     "estimate": None, "observed": "~89,121 km^2 opening, first since 1979",
     "direction": NO_ESTIMATE, "kind": "unmodelled event", "status": DECIDED,
     "note": "no estimate existed to miss; the cascade arrived as weather "
             "(six atmospheric rivers + subsurface warm water)",
     "source": "Swain, Jena et al. 2026, GRL, doi:10.1029/2026GL122580",
     "grade": CITED_PRESS},
]

# Couplings that may sit outside McCormack et al. 2026. PROPOSED: the paper
# was not read, so each is a check ("is it in the ensemble?"), not a finding.
CANDIDATE_OMISSIONS: List[Dict] = [
    {"id": "O1", "term": "ice-shelf melt feedback (Youngs 2026, 2/3 of the increase)",
     "push": UNDER,
     "why": "ice-sheet ensembles commonly take ocean melt as an offline forcing; "
            "an interactive cavity feedback would then be absent",
     "check": "is ocean forcing interactive or offline in M's ensemble?"},
    {"id": "O2", "term": "westward meltwater blocking warm intrusions (Youngs 2026)",
     "push": OVER,
     "why": "the negative feedback in the same paper; absent it, melt runs high "
            "downstream",
     "check": "same as O1; O1 and O2 enter together or not at all"},
    {"id": "O3", "term": "discrete events (atmospheric rivers, polynyas, marine heatwaves)",
     "push": UNDER,
     "why": "smoothed forcing has no excursions; event-induced crossing happens "
            "while the mean stays below threshold (CEED tipping.py; Breid Bay)",
     "check": "does the forcing carry sub-annual extremes or annual means?"},
    {"id": "O4", "term": "ice-shelf breakup inside the predictable window",
     "push": UNDER,
     "why": "predictability from present-day loss assumes continuity; a shelf "
            "breakup is a step change (thwaites_teis_2026 R7: precursors active)",
     "check": "do members include calving / shelf-loss events before 2055?"},
    {"id": "O5", "term": "ocean forcing from models carrying the sea-ice sign tension",
     "push": None,
     "why": "if the forcing models get post-2016 sea ice wrong, the heat delivered "
            "to the shelf is off, direction unknown",
     "check": "which CMIP models force the ensemble, and their post-2016 sea ice"},
    {"id": "O6", "term": "AAIW reversal / ocean heat routing (Mishra et al. 2026)",
     "push": None,
     "why": "changes where Southern Ocean heat goes; direction for ice-shelf "
            "melt not established",
     "check": "after reading Mishra (aaiw C1-C5)"},
]

DIRECTION_CODE = {UNDER: 1, OVER: -1, SIGN: 0, NO_ESTIMATE: 0, None: 0}


def tally(entries: Optional[List[Dict]] = None) -> Dict:
    """Count misses by direction. DECIDED entries only in the main counts.

    CONDITIONAL and OPEN entries are counted apart: folding them in would
    let an unsettled reading move the headline. No rate is returned: the
    frame is selected on the outcome (see module header).
    """
    entries = MISSES if entries is None else entries
    decided = [e for e in entries if e["status"] == DECIDED]
    counts = {d: sum(1 for e in decided if e["direction"] == d)
              for d in (UNDER, OVER, SIGN, NO_ESTIMATE)}
    held = {s: [e["id"] for e in entries if e["status"] == s]
            for s in (CONDITIONAL, OPEN)}
    return {"n_decided": len(decided), "counts": counts, "held_apart": held,
            "rate_low": None,
            "rate_low_reason": "frame selected on outcome (remembered misses); "
                               "needs a frame fixed before looking",
            "frame": "encountered or remembered in one session"}


def omission_push() -> Dict:
    """Directions the candidate McCormack omissions would push (PROPOSED)."""
    out = {UNDER: [], OVER: [], "UNKNOWN": []}
    for o in CANDIDATE_OMISSIONS:
        out[o["push"] if o["push"] else "UNKNOWN"].append(o["id"])
    out["grade"] = PROPOSED
    out["caveat"] = ("list written by one reader who knows more amplifiers than "
                     "dampers; O2 is included so the damping side is not empty "
                     "by construction")
    return out


def corruption_directions(entries: Optional[List[Dict]] = None) -> Dict[str, int]:
    """Direction codes in corruption_chain's convention (+1 under, -1 over)."""
    entries = MISSES if entries is None else entries
    return {e["id"]: DIRECTION_CODE[e["direction"]] for e in entries}


PROPOSED_FRAME = (
    "Every IPCC AR5 WG1 projection with a quantity observable by 2026 "
    "(sea-level rate, Arctic/Antarctic sea ice, ice-sheet mass loss, ocean "
    "heat content, glacier mass), listed BEFORE comparing to observations, "
    "scored UNDER/OVER/WITHIN its own range. Not run.")


def summary() -> str:
    t = tally()
    p = omission_push()
    lines = ["Estimate direction tally (frame selected on outcome; counts, no rate)"]
    for e in MISSES:
        lines.append(f"  {e['id']} {e['direction']:11s} {e['status']:11s} {e['what']}")
    lines.append(f"  decided n={t['n_decided']}: " +
                 ", ".join(f"{k} {v}" for k, v in t["counts"].items()))
    lines.append(f"  held apart: conditional {t['held_apart'][CONDITIONAL]}, "
                 f"open {t['held_apart'][OPEN]}")
    lines.append(f"  McCormack candidate omissions [PROPOSED, paper not read]: "
                 f"push UNDER {p[UNDER]}, OVER {p[OVER]}, unknown {p['UNKNOWN']}")
    lines.append("  rate_low: None (" + t["rate_low_reason"] + ")")
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary())
