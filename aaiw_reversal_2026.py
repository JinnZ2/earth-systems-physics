# aaiw_reversal_2026.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Antarctic Intermediate Water (AAIW) reversal, 2016-2024, as reported in
# press coverage of Mishra, Gayen & Naveira Garabato (2026), Nature Climate
# Change, doi:10.1038/s41558-026-02758-y, "Reversal of Antarctic
# Intermediate Water trends triggered by sea ice decline".
#
# Co-authored, human + Claude, 2026-10-28.
#
# SOURCE GRADE
# ------------
# CITED_PRESS: read from press coverage only (Scientific Frontline,
# Oceanographic, Phys.org screenshot), 2026-10-28. The paper, its figures,
# salinity/density magnitudes, depths and methods were NOT read (publisher
# and university pages refused the fetch). Upgrade to CITED after reading it.
#
# WHAT THIS MODULE DOES
# ---------------------
# 1. Carries the reported numbers with their grade (STATED).
# 2. Converts the meltwater comparison into units this repo already uses
#    (km^3/yr, Gt/yr, Sv) and sets it beside layer_4's CDW-attributable
#    ice-shelf basal melt, the freshwater term the CDW-AABW-Cryosphere loop
#    runs on (DERIVED, arithmetic).
# 3. Records what the press material leaves open and the cheapest checks
#    (PROPOSED).
#
# WHAT IT DOES NOT DO
# -------------------
# Not wired into cascade_engine. No salinity or density value exists here:
# none was reported in the material read.
#
# Standard library plus layer_4_hydrosphere (already in the stack).

from typing import Dict

from layer_4_hydrosphere import cdw_basal_melt_rate_Gt_yr

STATED = "STATED"            # number as the press material gives it
DERIVED = "DERIVED"          # arithmetic on STATED values, step shown
PROPOSED = "PROPOSED"        # a reading this module introduces
NOT_IN_TEXT = "NOT_IN_TEXT"  # asked for, absent from the material read
CITED_PRESS = "CITED_PRESS"

KM3_PER_YR_PER_SV = 1e6 * 365.25 * 86400 / 1e9   # 1 Sv = 1e6 m^3/s -> km^3/yr

STUDY: Dict[str, str] = {
    "title": "Reversal of Antarctic Intermediate Water trends triggered by sea ice decline",
    "authors": "Kaushik Mishra, Bishakhdatta Gayen, Alberto C. Naveira Garabato",
    "journal": "Nature Climate Change (2026)",
    "doi": "10.1038/s41558-026-02758-y",
    "grade": CITED_PRESS,
    "read": "Scientific Frontline 2026-10-28 (sflorg.com/2026/10/oce10282601.html); "
            "Oceanographic 2026-10-28; Phys.org screenshot supplied by Kavik",
}

REPORTED: Dict[str, Dict] = {
    "stable_window": {"value": (1995, 2015), "grade": STATED,
                      "note": "summer sea-ice melt kept AAIW 'healthy'"},
    "reversal_window": {"value": (2016, 2024), "grade": STATED},
    "melt_pre_2016_x_amazon": {"value": 3.0, "grade": STATED,
                               "note": "'about three times' the Amazon's annual flow"},
    "melt_post_2016_x_amazon": {"value": 2.0, "grade": STATED,
                                "note": "'about double'"},
    "amazon_km3_yr": {"value": 6600.0, "grade": STATED,
                      "note": "as given in the coverage"},
    "data": {"value": "Argo (~4,000 floats), satellite, atmospheric datasets",
             "grade": STATED},
    "past_transition": {"value": "about 130,000 years ago, end of last interglacial; "
                                 "'took thousands of years, not two decades'",
                        "grade": STATED},
    "salinity_density_magnitudes": {"value": None, "grade": NOT_IN_TEXT},
    "depths": {"value": None, "grade": NOT_IN_TEXT},
    "internal_variability_treatment": {"value": None, "grade": NOT_IN_TEXT},
    "glacial_or_ice_shelf_meltwater": {"value": None, "grade": NOT_IN_TEXT,
                                       "note": "not mentioned in the coverage read"},
}

# A same-journal, same-year study of the 2015-16 sea-ice drop itself.
RELATED = {
    "spira_2026": {
        "citation": "Spira et al. 2026, Nature Climate Change 16:583-590, "
                    "doi:10.1038/s41558-026-02601-4",
        "grade": "CITED_SECONDARY (open-access PDF read through a fetch tool)",
        "finding": "Winter Water thinned 2005-2015 (1.7 m/yr); strong winds in 2015 mixed "
                   "warm, salty water upward and drove the sea-ice decline",
        "bearing": "the AAIW 'trigger' (sea-ice decline) is itself downstream of wind "
                   "and Winter Water preconditioning; the chain is wind -> upper-ocean "
                   "mixing -> sea ice -> meltwater -> AAIW",
    },
}


def meltwater_km3_yr(x_amazon: float, amazon_km3_yr: float = 6600.0) -> float:
    """Sea-ice meltwater volume from the 'times the Amazon' comparison.

    x_amazon      : multiple of the Amazon's annual flow (dimensionless)
    amazon_km3_yr : Amazon annual flow as stated in the coverage (km^3/yr)
    returns       : melt volume (km^3/yr)
    """
    return x_amazon * amazon_km3_yr


def km3_yr_to_sv(km3_yr: float) -> float:
    """Volume flux km^3/yr -> Sverdrup (1 Sv = 1e6 m^3/s)."""
    return km3_yr / KM3_PER_YR_PER_SV


def meltwater_change() -> Dict[str, float]:
    """Drop in summer sea-ice meltwater, 1995-2015 vs 2016-2024 (DERIVED).

    1 km^3 of freshwater ~ 1 Gt, so km^3/yr and Gt/yr are read as equal here.
    The comparison is of MELT VOLUME as stated. Whether it is gross seasonal
    melt or net freshwater delivered to the AAIW source region is not in the
    material read; sea ice that forms and melts in the same place delivers
    no net freshwater over a year.
    """
    pre = meltwater_km3_yr(REPORTED["melt_pre_2016_x_amazon"]["value"])
    post = meltwater_km3_yr(REPORTED["melt_post_2016_x_amazon"]["value"])
    drop = pre - post
    return {"pre_km3_yr": pre, "post_km3_yr": post, "drop_km3_yr": drop,
            "pre_sv": km3_yr_to_sv(pre), "post_sv": km3_yr_to_sv(post),
            "drop_sv": km3_yr_to_sv(drop), "drop_fraction": drop / pre}


def freshwater_terms_beside_cdw_loop(cdw_heat_flux_TW: float = 2.81) -> Dict:
    """Set the sea-ice meltwater drop beside layer_4's CDW basal-melt term.

    The CDW-AABW-Cryosphere loop in cascade_engine says ice-shelf basal melt
    has added freshwater since the 2016 sea-ice collapse. This study says
    sea-ice meltwater fell over the same years. Two freshwater terms, same
    years, opposite directions, different water masses:

      basal melt      -> continental shelf -> AABW (dense, sinks)
      sea-ice melt    -> north toward the polar front -> AAIW (intermediate)

    Not a contradiction (different regions); a budget neither module carries
    whole. Ratio is DERIVED; reading is PROPOSED.
    """
    basal = cdw_basal_melt_rate_Gt_yr(cdw_heat_flux_TW)
    mw = meltwater_change()
    return {
        "cdw_attributable_basal_melt_Gt_yr": basal,
        "sea_ice_meltwater_drop_Gt_yr": mw["drop_km3_yr"],
        "ratio_drop_to_basal": mw["drop_km3_yr"] / basal if basal else None,
        "grade_ratio": DERIVED,
        "reading": ("The sea-ice term changed by about 60x the CDW-attributable "
                    "basal-melt term the repo's loop runs on. A freshwater budget "
                    "for the Southern Ocean that carries only the ice-shelf term "
                    "is missing the larger moving term (E1, dropped variable), "
                    "if the stated melt volumes are net delivery (open, see "
                    "meltwater_change)."),
        "grade_reading": PROPOSED,
    }


def record_length() -> Dict:
    """Post-reversal window length against the claim it carries (DERIVED/PROPOSED)."""
    a, b = REPORTED["reversal_window"]["value"]
    n = b - a + 1
    return {
        "post_reversal_years": n,
        "internal_variability_treatment": REPORTED["internal_variability_treatment"]["grade"],
        "reading": (f"{n} years after the reversal. A trend reversal over {n} years "
                    "and the ~130 kyr interglacial transition are different objects "
                    "(a window statistic vs a state change); 'thousands of years, not "
                    "two decades' compares them as one quantity. Whether the reversal "
                    "persists or is a multi-year excursion needs the paper's treatment "
                    "of internal variability, not in the material read."),
        "grade_reading": PROPOSED,
    }


OPEN_CHECKS = [
    ("C1", "Read the paper: salinity/density magnitudes, depth range, uncertainty.",
     "upgrade CITED_PRESS -> CITED"),
    ("C2", "Is the 3x / 2x Amazon figure gross seasonal melt or net freshwater "
           "delivered to the AAIW formation region?",
     "decides whether freshwater_terms_beside_cdw_loop() reading stands"),
    ("C3", "Does the paper carry ice-shelf (including Amundsen Sea / Thwaites) "
           "meltwater in its freshwater budget?",
     "absent in coverage; if absent in paper, E1 candidate"),
    ("C4", "Post-2016 trend against a null of internal variability (SAM, ENSO).",
     "persistence vs excursion"),
    ("C5", "Deep-ocean warming and sea-level 'underestimated': a computed number, "
           "or the conditional 'could' of the coverage?",
     "currently conditional; no figure in the material read"),
]


def summary() -> str:
    mw = meltwater_change()
    ft = freshwater_terms_beside_cdw_loop()
    rl = record_length()
    lines = [
        f"AAIW reversal 2026 ({STUDY['grade']}): {STUDY['doi']}",
        f"  sea-ice meltwater  pre {mw['pre_km3_yr']:.0f}  post {mw['post_km3_yr']:.0f}  "
        f"drop {mw['drop_km3_yr']:.0f} km^3/yr ({mw['drop_sv']:.3f} Sv, "
        f"{mw['drop_fraction']:.0%})",
        f"  CDW-attributable basal melt (layer_4): "
        f"{ft['cdw_attributable_basal_melt_Gt_yr']:.1f} Gt/yr",
        f"  ratio drop / basal: {ft['ratio_drop_to_basal']:.1f}  [{DERIVED}]",
        f"  post-reversal record: {rl['post_reversal_years']} yr; internal variability "
        f"{rl['internal_variability_treatment']}",
        "  open checks: " + ", ".join(c[0] for c in OPEN_CHECKS),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary())
