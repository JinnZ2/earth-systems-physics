# antarctic_sea_ice_2026.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Two observed Antarctic sea-ice facts from 2026 reporting, read against the
# model ensemble in ice_shelf_melt_feedback_2026 (Pauling et al.) and its
# open SIGN_TENSION:
#
#   B  Breid Bay polynya, East Antarctica (16-31E, 65-68S), open 2024-08-04
#      to 2024-08-10, peak 2024-08-08, ~89,121 km^2. First opening in July or
#      August since satellite records began in 1979. Swain, Jena et al.
#      (NCPOR), Geophysical Research Letters, published 2026-09-27,
#      doi:10.1029/2026GL122580. Read through earth.com coverage.
#
#   X  2026 winter maximum: 2026-09-14, ~17.59 million km^2, third-lowest in
#      the satellite record (NSIDC data; NASA Earth Observatory, reposted by
#      ScienceDaily 2026-10-15).
#
# Co-authored, human + Claude, 2026-10-28.
#
# SOURCE GRADE
# ------------
# CITED_PRESS for both. The GRL paper was not read.
#
# A Nature news item, 'Unprecedented hole opened up in Antarctic winter sea
# ice' (d41586-026-03160-6), refused the fetch. Whether it reports B or a
# different event is UNRESOLVED; nothing from it is carried.
#
# WHAT THIS MODULE DOES
# ---------------------
# 1. Puts B on the scales already in the repo (fraction of the 2026 maximum,
#    fraction of Pauling's smallest model response). DERIVED.
# 2. Records which SIGN_TENSION reading B bears on (PROPOSED). B is driven by
#    atmospheric rivers plus subsurface warm water, with no meltwater term
#    in the coverage. So it is evidence that a non-meltwater heat path opens
#    winter ice (R2-type), not evidence against R1/R3/R4.
# 3. Points at CEED's event-induced tipping (atmospheric rivers as discrete
#    excursions); no code is shared.

from typing import Dict, List, Tuple

from ice_shelf_melt_feedback_2026 import REPORTED as P_REPORTED, SIGN_TENSION

STATED = "STATED"
DERIVED = "DERIVED"
PROPOSED = "PROPOSED"
UNRESOLVED = "UNRESOLVED"
CITED_PRESS = "CITED_PRESS"

BREID_BAY: Dict[str, Dict] = {
    "doi": {"value": "10.1029/2026GL122580", "grade": STATED},
    "area_km2": {"value": 89121.0, "grade": STATED},
    "box_deg": {"value": {"lon": (16, 31), "lat": (-68, -65)}, "grade": STATED},
    "open": {"value": ("2024-08-04", "2024-08-10"), "grade": STATED},
    "first_since": {"value": 1979, "grade": STATED,
                    "note": "ice every July-August of the satellite record until 2024"},
    "atmospheric_rivers": {"value": ["07-06", "07-13", "07-17", "07-26", "07-29", "08-06"],
                           "grade": STATED, "note": "ERA5"},
    "marine_heatwave": {"value": ("2024-07-23", "2024-08-14"), "grade": STATED},
    "subsurface": {"value": "warm salty water under colder layers (Argo 7900893, CTD 67S 21E)",
                   "grade": STATED},
    "data_caveat": {"value": "sections from GLORYS12 reanalysis; one Argo float + ship CTD",
                    "grade": STATED},
    "meltwater_term": {"value": None, "grade": "NOT_IN_TEXT"},
}

MAX_2026: Dict[str, Dict] = {
    "date": {"value": "2026-09-14", "grade": STATED},
    "extent_mkm2": {"value": 17.59, "grade": STATED},
    "rank": {"value": "third-lowest", "grade": STATED},
    "trend_1979_2014": {"value": "+~1% per decade", "grade": STATED},
    "reversal": {"value": "2015, losses from 2016", "grade": STATED},
}

NATURE_NEWS_HOLE = {"id": "d41586-026-03160-6", "same_event_as_breid_bay": None,
                    "grade": UNRESOLVED}


def breid_bay_on_repo_scales() -> Dict:
    """B against the 2026 maximum and against Pauling's model responses."""
    a_mkm2 = BREID_BAY["area_km2"]["value"] / 1e6
    lo, hi = P_REPORTED["P_sea_ice_gain_mkm2"]["value"]
    return {"area_mkm2": a_mkm2,
            "frac_of_2026_max": a_mkm2 / MAX_2026["extent_mkm2"]["value"],
            "frac_of_pauling_min": a_mkm2 / lo,
            "frac_of_pauling_max": a_mkm2 / hi,
            "grade": DERIVED,
            "caveat": "different years (2024 event vs 2026 maximum) and different "
                      "quantities (local opening vs annual-mean area change)"}


def bears_on_sign_tension() -> List[Tuple[str, str]]:
    """Which SIGN_TENSION readings B speaks to (PROPOSED). Chooses none."""
    ids = [r[0] for r in SIGN_TENSION["candidate_readings"]]
    out = [("R2", "supports a non-meltwater heat path (ARs + subsurface warm water) "
                  "opening winter ice; a heat source the surface-hosing ensemble "
                  "does not test")]
    assert all(r in ids for r, _ in out)
    return out


CROSS_REFERENCES = [
    ("CEED simulation/tipping.py", "event-induced tipping: a discrete excursion "
     "(here six atmospheric rivers) clears a barrier the mean state does not"),
    ("ice_shelf_melt_feedback_2026.SIGN_TENSION", "R2"),
    ("aaiw_reversal_2026", "same post-2016 sea-ice decline, AAIW consequence"),
]


def summary() -> str:
    s = breid_bay_on_repo_scales()
    return "\n".join([
        "Antarctic sea ice 2026 (CITED_PRESS)",
        f"  Breid Bay polynya Aug 2024: {s['area_mkm2']:.3f} million km^2, "
        f"{s['frac_of_2026_max']:.2%} of the 2026 max, "
        f"{s['frac_of_pauling_min']:.2f}x Pauling's smallest model response",
        f"  2026 max {MAX_2026['extent_mkm2']['value']} million km^2 on "
        f"{MAX_2026['date']['value']}, {MAX_2026['rank']['value']}",
        "  bears on SIGN_TENSION: " + ", ".join(r for r, _ in bears_on_sign_tension())
        + " (none chosen)",
        f"  Nature news 'hole' item: {NATURE_NEWS_HOLE['grade']}",
    ])


if __name__ == "__main__":
    print(summary())
