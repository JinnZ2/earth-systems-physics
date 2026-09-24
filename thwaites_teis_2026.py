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
# Located by web search (index snippets + institutional repository
# listings: NERC, NSF PAR, UEA, BAS). Full text NOT opened -- the session's
# egress policy blocks publisher sites -- so quoted numbers are from
# abstracts as indexed. Upgrade to CITED after reading the paper itself.
CITED_SECONDARY = "CITED_SECONDARY"

SITE = "Thwaites Eastern Ice Shelf (TEIS)"
READ_BY = "Kavik"
READ_PERIOD = "2026-09"
SEASON = "late austral winter (pre-spring rift window)"
# The spring window has a source: Wild et al. 2024 report rapid rift
# propagation events during austral spring (LITERATURE["wild_2024"]).


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
    # The read cited "J. Glaciology, Sentinel-1 2014-2024". The sentence
    # matches Wild et al. 2024 almost verbatim ("the initially narrow band
    # of damage at the crevasse swarm widens as the ice-thickness minimum
    # spreads over a large area during downstream advection"), whose record
    # runs 2014 through MID-2023 -- the read's end year was off by one.
    "reference": "wild_2024",
    "reference_status": CITED_SECONDARY,
    "record_period": "2014 - mid-2023 (read said 2014-2024)",
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
# The loop is not new physics. Two published positive feedbacks at TEIS
# have the same sign on a neighbouring pair of variables:
#   benn_2022     damage <-> strain
#   banerjee_2025 shear-zone fracturing <-> upstream ice acceleration
# The read's loop (thinning at crack edges <-> crack growth) stays DERIVED;
# these make it a candidate member of a documented family, not confirmed.
LOOP_PUBLISHED_ANALOGUES = ["benn_2022", "banerjee_2025"]

# Candidate common drivers. A loop needs none of them; each predicts
# thinning that is NOT localized on cracks.
COMMON_DRIVER_CANDIDATES = {
    "ocean_basal_thinning": ("weakened: wild_2024 finds TEIS destabilizing "
                             "'despite low basal melt rates'"),
    "pinning_point_contact": ("open: banerjee_2025 places the shear zone "
                              "upstream of the pinning point"),
    "internal_dynamics": ("open: williams_2026 -- Thwaites keeps losing ice "
                          "for 150 yr with zero ocean melt; upstream "
                          "acceleration would thin the shelf by stretching, "
                          "broadly rather than at crack edges"),
}

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

# Published inputs the mitigation reading refers to, sourced by search.
# Where the read's wording differs from the source, PUBLISHED carries the
# SOURCE wording and the read's wording is kept beside it.
PUBLISHED_INPUTS = {
    "breakup_forecast": {
        # The source says collapse "may be initiated by intersection of
        # rifts with hidden basal crevasse zones ... as soon as 2026"
        # ("within as little as 5 years" from 2021). Conference abstract,
        # not peer reviewed. "Very likely" is a strengthening the source
        # does not make.
        "value": "may be initiated as soon as 2026",
        "read_wording": "very likely 2026",
        "source": "pettit_2021",
        "source_status": CITED_SECONDARY,
        "peer_reviewed": False,
    },
    "ice_flow_speed": {
        "value": 2.85, "units": "m/d", "when": "early 2023",
        "where": "central TEIS",
        "prior": {"value": 1.65, "units": "m/d", "when": "2019"},
        "change_pct": 70,                             # ~, as reported
        "source": "wild_2024",
        "source_status": CITED_SECONDARY,
    },
}
FLOW_SPEED_M_PER_YR = round(PUBLISHED_INPUTS["ice_flow_speed"]["value"] * 365.25)
                                                  # DERIVED: ~1041 m/yr


# ─────────────────────────────────────────────
# LITERATURE — what each source supports for THIS read
# Includes the five papers supplied 2026-09-23 as a list; corrections found
# while locating them are recorded under 'correction'.
# ─────────────────────────────────────────────

LITERATURE: Dict[str, Dict[str, object]] = {
    "wild_2024": {
        "cite": ("Wild, C. T., Kachuck, S. B., Luckman, A., Alley, K. E., et al. "
                 "(incl. Pettit, E. C.) 2024. Rift propagation signals the last act "
                 "of the Thwaites Eastern Ice Shelf despite low basal melt rates. "
                 "J. Glaciology. doi:10.1017/jog.2024.64"),
        "status": CITED_SECONDARY,
        "supports": ["O1", "O4", "spring rift window", "flow speed (R8)",
                     "weakens ocean-basal common driver"],
        "on_teis": True,
    },
    "pettit_2021": {
        "cite": ("Pettit, E. C., et al. 2021. Collapse of Thwaites Eastern Ice "
                 "Shelf by intersecting fractures. AGU Fall Meeting, C34A-07."),
        "status": CITED_SECONDARY,
        "supports": ["breakup forecast (R7): 'as soon as 2026', not 'very likely'",
                     "rifts propagating up to 2 km/yr (Sentinel-1)"],
        "on_teis": True,
    },
    "benn_2022": {
        "cite": ("Benn, D. I., et al. 2022. Rapid fragmentation of Thwaites "
                 "Eastern Ice Shelf. The Cryosphere 16, 2545. "
                 "doi:10.5194/tc-16-2545-2022"),
        "status": CITED_SECONDARY,
        "supports": ["damage-strain positive feedback (loop analogue)"],
        "on_teis": True,
    },
    "banerjee_2025": {
        "cite": ("Banerjee, D., et al. 2025. Evolution of shear-zone fractures "
                 "presages the disintegration of Thwaites Eastern Ice Shelf. "
                 "JGR Earth Surface 130(9). doi:10.1029/2025JF008352"),
        "status": CITED_SECONDARY,
        "supports": ["O1, O2 (2002-2022: shear fractures, then tensile)",
                     "fracturing-acceleration positive feedback (loop analogue)"],
        "on_teis": True,
    },
    # ── the five supplied papers ──
    "williams_2026": {
        "cite": ("Williams, C. R., Trevers, M., Sun, S., Holland, P. R., Bett, D. T., "
                 "Arthern, R. J., Bradley, A. T. 2026. Mass loss from Thwaites "
                 "Glacier continues even without ocean melting. GRL 53(14). "
                 "doi:10.1029/2026GL122843"),
        "status": CITED_SECONDARY,
        "correction": ("supplied as 'Bradley, A. T., et al.': Bradley is LAST "
                       "author, first is Williams. Published 2026-07-25."),
        "supports": ["internal-dynamics common-driver candidate"],
        "on_teis": False,
    },
    "pham_2025": {
        "cite": ("Pham, T.-S. 2025. Systematic detection of glacial earthquakes in "
                 "Thwaites Glacier, West Antarctica, by regional surface waves. "
                 "GRL. doi:10.1029/2025GL118885"),
        "status": CITED_SECONDARY,
        "correction": ("supplied as 2026; the paper is 2025 (Aug 2026 was news "
                       "coverage). 245 of 362 events near Thwaites' marine edge, "
                       "2010-2023; rate tracks speed-ups of the frontal ICE "
                       "TONGUE 2018-2020, not the eastern shelf."),
        "supports": [],
        "on_teis": False,
    },
    "killingbeck_2026": {
        "cite": ("Killingbeck, S. F., et al. 2026. Distinct groundwater regimes in "
                 "West Antarctic sedimentary basins inferred from magnetotelluric "
                 "imaging. JGR Solid Earth. doi:10.1029/2026JB033859"),
        "status": CITED_SECONDARY,
        "supports": [],
        "on_teis": False,
    },
    "pierce_2026": {
        "cite": ("Pierce, C., et al. 2026. Characterizing the subglacial environment "
                 "of lower Thwaites Glacier using radar modeling. J. Glaciology. "
                 "doi:10.1017/jog.2026.10160"),
        "status": CITED_SECONDARY,
        "correction": ("April 2026. 'Homogeneous bed' is the authors' inference "
                       "from simulated-vs-observed power correlating in 40% of "
                       "flight segments. NOT the J. Glaciology paper behind O4 "
                       "(that is wild_2024)."),
        "supports": [],
        "on_teis": False,
    },
    "goldberg_preprint_2026": {
        "cite": ("Goldberg, D. N., Holland, P. R., Naughten, K. A. Century-scale "
                 "impacts of ice-sheet model initialization on Amundsen Sea "
                 "Embayment, West Antarctica. EGUsphere preprint, "
                 "doi:10.5194/egusphere-2026-3779"),
        "status": CITED_SECONDARY,
        "correction": ("a PREPRINT under review, not a published study; the "
                       "supplied 'Comment on egusphere-2026-3779' is the "
                       "discussion page. The '2.6 mm/yr SLE by 2200' figure was "
                       "not found in any indexed text: UNCITED until read."),
        "supports": [],
        "on_teis": False,
    },
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
            "published": "%s %s (%s)" % tuple(
                PUBLISHED_INPUTS["ice_flow_speed"][k]
                for k in ("value", "units", "when")),
            "mitigation": ("FLOOR; current value higher or unquantified"
                           if loop_active else "as published"),
            "rule": "R8_STALE_RATE_FLOOR",
            "basis": (f"published {PUBLISHED_INPUTS['ice_flow_speed']['value']} m/d "
                      f"(~{FLOW_SPEED_M_PER_YR} m/yr) is early 2023, measured "
                      "during a ~70% acceleration the same source documents; "
                      "~3.5 yr older than the read"),
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
    print(f"  published analogues: {', '.join(LOOP_PUBLISHED_ANALOGUES)}")
    for k, v in COMMON_DRIVER_CANDIDATES.items():
        print(f"  common driver {k}: {v}")
    print(f"  falsifier ({LOOP_FALSIFIER['status']}): {LOOP_FALSIFIER['test']}")
    print("\nMITIGATION reading:")
    for k, r in mitigation_reading().items():
        print(f"  {k:10s} published {r['published']!s:18s} -> {r['mitigation']}"
              f"  [{r['rule']}]")
    q = quantified_cv()
    print(f"\nCV status: {q['status']}; missing: {', '.join(q['missing'])}")
