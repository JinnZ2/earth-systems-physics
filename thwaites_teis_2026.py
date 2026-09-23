# thwaites_teis_2026.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Thwaites Eastern Ice Shelf (TEIS), September 2026: a qualitative
# imagery read, its interpretation, the coupling it implies, and the
# MITIGATION reading — each carried at its own epistemic grade.
#
# SOURCE
# ------
# Imagery read by Kavik, September 2026 (late austral winter). Sensor,
# scene IDs, acquisition dates and area of interest are NOT recorded
# in the read; they are fields below, left None until supplied.
#
# EPISTEMIC TAGS (same vocabulary as planetary_health_check_2026)
#   OBSERVED              seen in the imagery
#   OBSERVED_QUALITATIVE  seen, direction only — no number yet
#   PROPOSED              an interpretation or rule this repo introduces
#   DERIVED               follows from OBSERVED items in a stated step
#
# WHAT THIS MODULE IS NOT
# -----------------------
# Not a measurement. No rift length, crack count or dark-area fraction
# exists yet. quantified_cv() returns the upgrade path; until all three
# numbers exist (with sensor, dates and a fixed AOI) the status stays
# OBSERVED_QUALITATIVE. Nothing here is wired into the cascade engine.
#
# Standard library only.

from typing import Dict, List, Optional


OBSERVED = "OBSERVED"
OBSERVED_QUALITATIVE = "OBSERVED_QUALITATIVE"
PROPOSED = "PROPOSED"
DERIVED = "DERIVED"
QUANTIFIED = "QUANTIFIED"
NOT_IN_TEXT = "NOT_IN_TEXT"
UNCITED = "UNCITED"

SITE = "Thwaites Eastern Ice Shelf (TEIS)"
READ_BY = "Kavik"
READ_PERIOD = "2026-09"
SEASON = "late austral winter (pre-spring rift window)"


# ─────────────────────────────────────────────
# OBSERVATIONS — OBSERVED, direction only
# ─────────────────────────────────────────────

OBSERVATIONS: Dict[str, Dict[str, str]] = {
    "O1": {"seen": "cracks lengthening",
           "reading": "rift propagation active",
           "grade": OBSERVED_QUALITATIVE},
    "O2": {"seen": "crack count rising",
           "reading": "new fracture initiation",
           "grade": OBSERVED_QUALITATIVE},
    "O3": {"seen": "more dark spots",
           "reading": "sensor-dependent — see O3_INTERPRETATION",
           "grade": OBSERVED_QUALITATIVE},
    "O4": {"seen": "thinning adjacent to existing cracks",
           "reading": "damage localizing on existing weakness",
           "grade": OBSERVED_QUALITATIVE},
}


# ─────────────────────────────────────────────
# INTERPRETATION — PROPOSED
# ─────────────────────────────────────────────

# O3 depends on the sensor, which the read does not record.
O3_INTERPRETATION: Dict[str, Dict[str, object]] = {
    "optical": {
        "reading": "open water, or thin / wet ice exposed",
        # Checked here, not in the read: at ~75 S in September the sun is
        # only a few degrees above the horizon. Crevasse and rift walls
        # cast long shadows that image dark. More cracks (O2) -> more
        # shadow, so an optical O3 may be O2 counted twice rather than
        # independent evidence of surface loss.
        "confound": ("low-sun shadowing in crevasse fields images dark; "
                     "not independent of O2 until sun elevation is "
                     "recorded and shadow is masked"),
        "grade": PROPOSED,
    },
    "SAR": {
        "reading": ("smooth surface: open water, or loss of surface "
                    "roughness"),
        # Two checks on the read's SAR branch. Surface melt is rare in
        # late austral winter, so 'melt' is the least likely member of
        # the list for September. And wind-roughened open water can be
        # BRIGHT in SAR, so open water is not guaranteed to appear dark.
        "confound": ("surface melt unlikely in September; wind-roughened "
                     "open water can image bright, so dark != all open "
                     "water and bright != no open water"),
        "grade": PROPOSED,
    },
}
O3_COMMON_READING = "loss of intact shelf surface (either sensor)"   # PROPOSED

O4_PATTERN = {
    "reading": ("damage band at a crevasse swarm widens as the "
                "ice-thickness minimum spreads during downstream "
                "advection; the Sept 2026 read = that process continuing, "
                "visible in late winter"),
    "reference": "J. Glaciology, Sentinel-1 record 2014-2024",
    "reference_status": UNCITED,   # authors / DOI not given in the read
    "grade": PROPOSED,
}


# ─────────────────────────────────────────────
# COUPLING — DERIVED
# ─────────────────────────────────────────────

COUPLING_EDGES: List[Dict[str, str]] = [
    {"from": "O4", "to": "O1", "why": "thin ice by cracks -> easier propagation"},
    {"from": "O1", "to": "O4", "why": "longer cracks -> more crack edges -> more thinning sites"},
    {"from": "O2", "to": "O4", "why": "more cracks -> more crack edges -> more thinning sites"},
]
LOOP_SIGN = "positive"                           # DERIVED from the edges
O3_ROLE = "surface signature of the loop"        # PROPOSED
LOOP_TIMING = "running BEFORE the spring rift window opens"   # OBSERVED (season of the read)

# The loop is inferred from four signals co-occurring in one read.
# A common driver (e.g. ocean-driven basal thinning, or changing contact
# at the pinning point) would produce the same co-occurrence with no
# loop. The two predict different geometry, so the next imagery can
# tell them apart.
LOOP_FALSIFIER = {
    "loop_predicts": ("thinning concentrated at crack edges and ahead of "
                      "crack tips; new cracks initiate preferentially in "
                      "those thinned bands"),
    "common_driver_predicts": ("thinning broadly distributed, not "
                               "localized on cracks; crack initiation "
                               "not preferentially in thinned bands"),
    "test": ("difference two dated scenes over a fixed AOI: is the "
             "thinning-change field correlated with distance to existing "
             "cracks?"),
    "status": "UNTESTED",
}


# ─────────────────────────────────────────────
# MITIGATION READING — declared rules (see risk_posture.py)
# Two rules are needed that risk_posture R1-R6 do not contain. They are
# declared here, not slipped into the reading.
# ─────────────────────────────────────────────

RULES = {
    "R7_PRECURSORS_ACTIVE": (
        "When the precursors a published forecast depends on are observed "
        "active, carry the forecast event as UNDERWAY, not FORECAST. The "
        "event itself is not claimed as observed."),
    "R8_STALE_RATE_FLOOR": (
        "A published rate measured before an observed acceleration signal "
        "is carried as a FLOOR; the current value is higher or "
        "unquantified."),
}

# Published inputs the mitigation reading refers to. The read names them
# but does not give their values or sources; they stay NOT_IN_TEXT /
# UNCITED rather than being filled from memory.
PUBLISHED_INPUTS = {
    "breakup_forecast": {"value": "very likely 2026", "source": UNCITED},
    "ice_flow_speed":   {"value": NOT_IN_TEXT, "units": "m/yr",
                         "source": UNCITED},
}


def mitigation_reading() -> Dict[str, Dict[str, object]]:
    """
    MITIGATION reading of the TEIS state, under declared rules.

    returns: {item: {published, mitigation, rule, basis}}
    """
    loop_active = all(o["grade"] in (OBSERVED, OBSERVED_QUALITATIVE)
                      for o in (OBSERVATIONS["O1"], OBSERVATIONS["O2"],
                                OBSERVATIONS["O4"]))
    out = {
        "breakup": {
            "published": PUBLISHED_INPUTS["breakup_forecast"]["value"],
            "mitigation": ("UNDERWAY (precursor loop active pre-window)"
                           if loop_active else "FORECAST"),
            "rule": "R7_PRECURSORS_ACTIVE",
            "basis": "O1, O2, O4 observed; detachment itself NOT observed",
        },
        "flow_speed": {
            "published": PUBLISHED_INPUTS["ice_flow_speed"]["value"],
            "mitigation": ("FLOOR; current value higher or unquantified"
                           if loop_active else "as published"),
            "rule": "R8_STALE_RATE_FLOOR",
            "basis": "published value predates the Sept 2026 read",
        },
    }
    return out


# ─────────────────────────────────────────────
# UPGRADE PATH — OBSERVED_QUALITATIVE -> QUANTIFIED
# ─────────────────────────────────────────────

# The three numbers that turn the read into a control variable. Counts
# and fractions are only comparable across dates on the same AOI with the
# same detection threshold and sensor, so those are required too —
# otherwise "crack count rising" could be a resolution or threshold
# change, not a change in the ice.
REQUIRED_CV_FIELDS = ("rift_length_km", "crack_count", "dark_area_fraction")
REQUIRED_METADATA = ("sensor", "scene_dates", "aoi", "detection_threshold")


def quantified_cv(rift_length_km: Optional[float] = None,
                  crack_count: Optional[int] = None,
                  dark_area_fraction: Optional[float] = None,
                  sensor: Optional[str] = None,
                  scene_dates: Optional[List[str]] = None,
                  aoi: Optional[str] = None,
                  detection_threshold: Optional[str] = None
                  ) -> Dict[str, object]:
    """
    Status of the TEIS control variable.

    rift_length_km      : longest active rift, km
    crack_count         : fractures in the AOI above detection_threshold
    dark_area_fraction  : dark pixels / AOI pixels, 0-1
    sensor              : 'optical' or 'SAR' (selects the O3 reading)
    scene_dates, aoi, detection_threshold : required for comparability
    returns: dict with status, missing fields, and the O3 reading if the
             sensor is known
    """
    vals = {"rift_length_km": rift_length_km, "crack_count": crack_count,
            "dark_area_fraction": dark_area_fraction}
    meta = {"sensor": sensor, "scene_dates": scene_dates, "aoi": aoi,
            "detection_threshold": detection_threshold}
    if dark_area_fraction is not None and not 0.0 <= dark_area_fraction <= 1.0:
        raise ValueError("dark_area_fraction must be in [0, 1]")
    if sensor is not None and sensor not in O3_INTERPRETATION:
        raise ValueError(f"sensor must be one of {list(O3_INTERPRETATION)}")
    missing = [k for k, v in {**vals, **meta}.items() if v is None]
    return {
        "status": QUANTIFIED if not missing else OBSERVED_QUALITATIVE,
        "values": vals,
        "metadata": meta,
        "missing": missing,
        "o3_reading": (O3_INTERPRETATION[sensor] if sensor
                       else "sensor unknown: both readings open"),
    }


if __name__ == "__main__":
    print(f"{SITE} — {READ_PERIOD} imagery read ({READ_BY}), {SEASON}\n")
    for k, o in OBSERVATIONS.items():
        print(f"  {k}  {o['seen']:38s} -> {o['reading']}  [{o['grade']}]")
    print("\nO3 by sensor [PROPOSED]:")
    for s, d in O3_INTERPRETATION.items():
        print(f"  {s:8s} {d['reading']}\n           confound: {d['confound']}")
    print(f"  common:  {O3_COMMON_READING}")
    print(f"\nO4 [PROPOSED]: {O4_PATTERN['reading']}")
    print(f"  ref: {O4_PATTERN['reference']} ({O4_PATTERN['reference_status']})")
    print(f"\nCoupling [DERIVED]: {LOOP_SIGN} loop, {LOOP_TIMING}")
    for e in COUPLING_EDGES:
        print(f"  {e['from']} -> {e['to']}: {e['why']}")
    print(f"  falsifier ({LOOP_FALSIFIER['status']}): {LOOP_FALSIFIER['test']}")
    print("\nMITIGATION reading:")
    for k, r in mitigation_reading().items():
        print(f"  {k:10s} published {r['published']!s:18s} -> {r['mitigation']}"
              f"  [{r['rule']}]")
    q = quantified_cv()
    print(f"\nCV status: {q['status']}; missing: {', '.join(q['missing'])}")
