#!/usr/bin/env python3
"""
risk_posture.py  --  CC0 1.0 Universal, stdlib only

SAME DATA, TWO DECLARED READINGS.

  PUBLISHED   the value and zone as the source institution states it
  MITIGATION  the same source values, resolved by declared rules that
              favour preparing over waiting

What this file does NOT do: invent numbers. Every MITIGATION output is
recomputable from a PUBLISHED input plus a named rule. If you disagree
with a rule, change the rule -- the data stays the same.

Why two readings exist:
  An institution's report carries a cost for false alarm (credibility,
  policy exposure), so uncertainty is usually resolved toward the central
  estimate. A person whose work, water, food or body is directly exposed
  carries the cost of being caught unprepared, and that cost lands on
  them. Different cost of error -> different decision rule on the same
  evidence.                                           [status: DERIVED]

Scope limit, stated up front:
  The Planetary Boundaries framework already sets its boundaries at the
  precautionary end ("the lower end of the range in which serious risks
  are expected to emerge" -- PHC 2026 Summary, s1.2). MITIGATION does not
  move the boundaries. It changes how RANGES, THIN MARGINS, UNMEASURED
  items, REGIONAL vs GLOBAL scope, and SOURCE-STATED MODEL BIAS are
  resolved, and it dates each published figure against the latest
  observation (R9). Nothing else.

Rule numbering is shared with thwaites_teis_2026.py, which declares
R7_PRECURSORS_ACTIVE and R8_STALE_RATE_FLOOR; the latency rule here is
therefore R9.

Source: Planetary Health Check 2026, Summary Report, PBScience/PIK,
released 2026-09-21. Assessment uses latest available data; some
predates 2026.
"""

# ---------------------------------------------------------------------------
# RULES -- each one declared, each one reversible
# ---------------------------------------------------------------------------
RULES = {
    "R1_ADVERSE_END": (
        "When the source gives a range, read the end that is worse for "
        "the exposed party."),
    "R2_THIN_MARGIN": (
        "When the gap between value and boundary is inside the spread of "
        "the source's own datasets, treat the boundary as crossed. The "
        "source publishes no spread; the width used is R2_SPREAD_FRACTION "
        "of the boundary, which is UNSOURCED and printed with every hit."),
    "R3_UNMEASURED": (
        "What the source says is unmeasured is carried as UNMEASURED, "
        "never as safe."),
    "R4_LOCAL_OVER_GLOBAL": (
        "Where the source gives a regional value, the regional value "
        "governs for people in that region."),
    "R5_STATED_BIAS": (
        "Where the source itself says its models lean one way, apply the "
        "lean in the stated direction; do not size it."),
    "R6_PRELIMINARY": (
        "A boundary the source calls preliminary is carried with that "
        "flag; a SAFE reading against it is SAFE_PRELIMINARY."),
    "R9_LATENCY": (
        "When a published data window ends before the latest available "
        "observation, the observation governs CURRENT state and the "
        "published figure becomes the PRIOR. Marked 2026-09-23."),
}

# ---------------------------------------------------------------------------
# LATENCY RECORD (R9) -- published data window vs latest observation.
# Dates only; no value is carried forward or invented. Sibling of
# thwaites_teis_2026.R8_STALE_RATE_FLOOR (that rule floors a RATE; this
# one re-dates a STATE).
# ---------------------------------------------------------------------------
LATENCY = [
    # item, data window ends, published, latest observation, status
    ("IMBIE ice-sheet mass balance", "2023", "2026-09-16",
     "imagery, late Sept 2026", "OBSERVED"),
    ("Thwaites glacial quakes", "2023", "2026-08", "-", "OBSERVED"),
    ("Thwaites eastern shelf flow", "2026-01", "2026-05",
     "imagery read late Sept 2026: cracks lengthening + multiplying, "
     "more dark area, thinning along existing cracks", "OBSERVED"),
    ("ESA Thwaites image", "2026-02", "2026-09",
     "-", "OBSERVED (labelled illustrative by ESA)"),
]

# R2 width. PHC 2026 publishes no dataset spread for the aragonite CV, so
# this is a declared choice, not a source value: 0.02 * 2.86 = 0.057 Omega.
# It is surfaced here and in every R2 output so it can be argued with.
# (planetary_health_check_2026.ocean_acidification_status uses the
# reporting resolution, 0.01 Omega, instead; both fire on 2.85.)
R2_SPREAD_FRACTION = 0.02          # [status: UNSOURCED -- declared rule parameter]

# zones
SAFE, INCR, HIGH = "SAFE", "INCREASING_RISK", "HIGH_RISK"
UNMEASURED = "UNMEASURED"
NOT_IN_TEXT = "NOT_IN_TEXT"


def zone(value, pb, high, worse_if_higher=True):
    if value is None:
        return NOT_IN_TEXT
    if worse_if_higher:
        return SAFE if value <= pb else (INCR if value < high else HIGH)
    return SAFE if value >= pb else (INCR if value > high else HIGH)


# ---------------------------------------------------------------------------
# DATA -- PHC 2026 Summary, s3 information sheets. (lo, hi) = stated range.
# ---------------------------------------------------------------------------
CVS = [
    # name, unit, (lo, hi), pb, high_risk, worse_if_higher, notes
    ("climate_co2", "ppm", (426, 426), 350, 450, True, {}),
    ("climate_rf", "W/m2", (3.10, 3.10), 1.0, 1.5, True, {}),
    ("biosphere_extinction", "E/MSY", (100, 1000), 10, 100, True, {}),
    ("biosphere_hanpp", "%", (21, 30), 10, 20, True, {}),
    ("land_forest", "% potential", (64, 64), 78, 54, False, {}),
    ("freshwater_blue", "% land", (22.6, 22.6), 12.9, 50, True,
     {"high_risk_provisional": True}),
    ("freshwater_green", "% land", (22.0, 22.0), 12.4, 50, True,
     {"high_risk_provisional": True}),
    ("biogeochem_p", "Tg/yr", (18.2, 18.2), 6.2, 11.2, True, {}),
    ("biogeochem_n", "Tg/yr", (165, 165), 62, 82, True, {}),
    ("ocean_aragonite", "omega", (2.85, 2.85), 2.86, 2.50, False,
     {"multi_dataset": True, "high_risk_provisional": True}),
    ("aerosol_global", "dAOD", (0.07, 0.07), 0.10, 0.25, True,
     {"regional_override": "aerosol_south_asia"}),
    ("aerosol_south_asia", "AOD", (0.32, 0.32), 0.25, 0.50, True,
     {"region": "South Asia", "pb_proposed": True}),
    ("ozone_extrapolar", "DU", (None, None), 277.4, None, False,
     {"pb_preliminary": True, "series_end": 2022}),
    ("novel_entities", "none", (None, None), None, None, True,
     {"proxy_only": True}),
]

# source-stated model biases (R5). Direction only; no magnitude invented.
STATED_BIAS = {
    "land_carbon_sink": (
        "PHC 2026 s2.1: current Earth system models may OVERESTIMATE land "
        "sink resilience. Direction: carbon budgets built on them are "
        "optimistic."),
}


def read(row):
    name, unit, (lo, hi), pb, high, wih, notes = row
    out = {"cv": name, "unit": unit, "published": None,
           "mitigation": None, "rules": []}

    # novel entities: no quantified CV exists at all
    if notes.get("proxy_only"):
        out["published"] = "HIGH_RISK (transgressed by proxy)"
        out["mitigation"] = "HIGH_RISK + " + UNMEASURED
        out["rules"].append("R3_UNMEASURED")
        return out

    # value missing from citable text
    if lo is None:
        out["published"] = SAFE + " (stated), value " + NOT_IN_TEXT
        out["mitigation"] = NOT_IN_TEXT
        if notes.get("pb_preliminary"):
            out["mitigation"] += " | boundary PRELIMINARY"
            out["rules"].append("R6_PRELIMINARY")
        return out

    central = (lo + hi) / 2.0
    out["published"] = "%s @ %s" % (zone(central, pb, high, wih),
                                    lo if lo == hi else (lo, hi))

    adverse = hi if wih else lo
    if lo != hi:
        out["rules"].append("R1_ADVERSE_END")
    z = zone(adverse, pb, high, wih)

    margin = abs(adverse - pb)
    spread = R2_SPREAD_FRACTION * abs(pb)
    if notes.get("multi_dataset") and margin <= spread:
        z = ("CROSSED (within dataset spread, margin %.3g <= %.3g = "
             "R2_SPREAD_FRACTION %.3g x boundary, UNSOURCED)"
             % (margin, spread, R2_SPREAD_FRACTION))
        out["rules"].append("R2_THIN_MARGIN")

    # R6: carry every preliminary / proposed / provisional flag the source
    # attaches; a SAFE reading against such a boundary is SAFE_PRELIMINARY.
    flags = []
    if notes.get("pb_preliminary") or notes.get("pb_proposed"):
        if z == SAFE:
            z = "SAFE_PRELIMINARY"
        flags.append("boundary %s" % ("PROPOSED" if notes.get("pb_proposed")
                                      else "PRELIMINARY"))
    if notes.get("high_risk_provisional"):
        flags.append("high-risk line PROVISIONAL")
    if flags:
        z += " | " + " | ".join(flags)
        out["rules"].append("R6_PRELIMINARY")

    if notes.get("regional_override"):
        z += " | regional value governs in-region: see " + \
             notes["regional_override"]
        out["rules"].append("R4_LOCAL_OVER_GLOBAL")

    out["mitigation"] = "%s @ %s" % (z, adverse)
    return out


def main():
    print(__doc__.split("Source:")[0].strip().splitlines()[0])
    print()
    for row in CVS:
        r = read(row)
        print("%-22s PUBLISHED  %s" % (r["cv"], r["published"]))
        print("%-22s MITIGATION %s" % ("", r["mitigation"]))
        if r["rules"]:
            print("%-22s rules      %s" % ("", ", ".join(r["rules"])))
        print()
    print("STATED MODEL BIAS (R5, direction only):")
    for k, v in STATED_BIAS.items():
        print("  %s: %s" % (k, v))
    print()
    print("LATENCY (R9): data window -> published -> latest observation")
    for item, win, pub, obs, st in LATENCY:
        print("  %-30s window %-8s pub %-10s [%s]" % (item, win, pub, st))
        if obs != "-":
            print("  %-30s latest: %s" % ("", obs))
    print()
    print("RULES:")
    for k, v in RULES.items():
        print("  %s  %s" % (k, v))


if __name__ == "__main__":
    main()
