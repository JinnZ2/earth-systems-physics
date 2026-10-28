# ice_shelf_melt_feedback_2026.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Two 2026 studies on the Antarctic ice-shelf freshwater budget, read beside
# layer_4's CDW basal-melt term and aaiw_reversal_2026's sea-ice meltwater:
#
#   Y  Youngs, Stewart, Si, Thompson, Schodlok et al. (2026),
#      "Antarctic ice-shelf basal melt shaped by competing feedbacks",
#      Nature Geoscience 19:675-682, doi:10.1038/s41561-026-01975-6.
#      How much melt the shelves make, and how much of the increase is the
#      melt feeding back on itself.
#
#   P  Pauling, Smith, Martin, Ridley, Stevens, Thomas, Beadling, Danek,
#      Hattermann, Li, Marshall, Muilwijk, Purich, Swart (2026),
#      "Antarctic sea ice response to meltwater due to Antarctic ice sheet
#      mass loss in a multi-model ensemble", EGUsphere preprint
#      egusphere-2026-658, doi:10.5194/egusphere-2026-658.
#      What that meltwater does to sea ice once it is out, across 11 models.
#
# Co-authored, human + Claude, 2026-10-28.
#
# SOURCE GRADE
# ------------
# CITED_ABSTRACT for both: the abstract / landing page was read through a
# fetch tool on 2026-10-28; figures, supplements and methods were NOT read.
# Y's numbers beyond the two-thirds share are NOT_IN_TEXT. P is a preprint
# (not yet peer reviewed). Upgrade to CITED after reading the papers.
#
# WHAT THIS MODULE DOES
# ---------------------
# 1. Carries the stated numbers with their grade.
# 2. Puts every freshwater term this repo now holds on one scale (Sv and
#    Gt/yr), arithmetic only (DERIVED).
# 3. Turns Y's two-thirds into the factor by which a forced-only melt term
#    misses the increase, and states when that factor applies to layer_4
#    and when it does not (SCOPE: the answer depends on where layer_4's
#    sensitivity came from, which is not settled here).
# 4. Records the sign tension between P (meltwater -> more sea ice, in every
#    model) and the post-2016 observed sea-ice decline, with candidate
#    readings listed and NONE chosen.
#
# WHAT IT DOES NOT DO
# -------------------
# Does not modify layer_4 or cascade_engine; repairing the melt term is the
# owner's call. Does not supply a total Antarctic basal melt figure (none was
# in the material read; not carried from memory). Does not model the
# regional sign flips Y reports.
#
# Standard library plus layer_4_hydrosphere and aaiw_reversal_2026.

from typing import Dict, List, Optional, Tuple

from aaiw_reversal_2026 import KM3_PER_YR_PER_SV, meltwater_change
from layer_4_hydrosphere import cdw_basal_melt_rate_Gt_yr

STATED = "STATED"
DERIVED = "DERIVED"
PROPOSED = "PROPOSED"
NOT_IN_TEXT = "NOT_IN_TEXT"
CITED_ABSTRACT = "CITED_ABSTRACT"

# 1 Gt of freshwater ~ 1 km^3 (density 1000 kg/m^3), as in aaiw_reversal_2026.
GT_YR_PER_SV = KM3_PER_YR_PER_SV

STUDIES: Dict[str, Dict] = {
    "youngs_2026": {
        "doi": "10.1038/s41561-026-01975-6",
        "venue": "Nature Geoscience 19:675-682 (published 2026-05-15)",
        "kind": "circumpolar ocean-sea-ice model with interactive ice shelves",
        "grade": CITED_ABSTRACT,
        "peer_reviewed": True,
    },
    "pauling_2026": {
        "doi": "10.5194/egusphere-2026-658",
        "venue": "EGUsphere preprint (2026-04-09)",
        "kind": "11-model, 43-member meltwater-hosing ensemble, pre-industrial forcing",
        "grade": CITED_ABSTRACT,
        "peer_reviewed": False,
    },
}

REPORTED: Dict[str, Dict] = {
    # --- Youngs et al. ---
    "Y_feedback_share_of_increase": {
        "value": 2.0 / 3.0, "grade": STATED,
        "note": "positive melt feedback = 'two-thirds of the increased melt rate "
                "over all ice shelves' (circumpolar total)"},
    "Y_feedback_vs_forced": {
        "value": "comparable magnitude; opposite sign in some regions",
        "grade": STATED},
    "Y_positive_mechanism": {
        "value": "dense-shelf regions: meltwater makes shelf water lighter, "
                 "letting warmer water reach the cavities",
        "grade": STATED},
    "Y_negative_mechanism": {
        "value": "westward-advected meltwater freshens the shelf downstream and "
                 "blocks warm intrusions",
        "grade": STATED},
    "Y_melt_rates": {"value": None, "grade": NOT_IN_TEXT,
                     "note": "no Gt/yr or m/yr in the abstract"},
    "Y_regional_shares": {"value": None, "grade": NOT_IN_TEXT},
    # --- Pauling et al. ---
    "P_hosing_sv": {"value": 0.1, "grade": STATED,
                    "note": "surface meltwater around the coast"},
    "P_n_models": {"value": 11, "grade": STATED},
    "P_n_members": {"value": 43, "grade": STATED},
    "P_sea_ice_gain_mkm2": {
        "value": (0.71, 4.14), "grade": STATED,
        "note": "annual-mean area increase, million km^2; positive in all models"},
    "P_spread_attributed_to": {
        "value": "mean-state sea-ice area and volume, open-ocean deep convection, "
                 "ocean stratification",
        "grade": STATED},
    "P_injection_depth": {
        "value": "surface", "grade": STATED,
        "note": "basal melt in reality leaves the cavity at depth (see SIGN_TENSION)"},
    "P_net_vs_gross": {"value": None, "grade": NOT_IN_TEXT},
}


# --------------------------------------------------------------------------
# Units
# --------------------------------------------------------------------------

def sv_to_gt_yr(sv: float) -> float:
    """Volume flux Sv -> Gt/yr of freshwater (1 Gt ~ 1 km^3)."""
    return sv * GT_YR_PER_SV


def gt_yr_to_sv(gt_yr: float) -> float:
    """Freshwater Gt/yr -> Sv."""
    return gt_yr / GT_YR_PER_SV


def freshwater_scale(cdw_heat_flux_TW: float = 2.81) -> List[Dict]:
    """Every Southern Ocean freshwater term this repo holds, on one scale.

    DERIVED arithmetic. The terms are NOT the same kind of flux and are not
    to be summed: the hosing is an imposed model forcing, the sea-ice drop is
    a change in gross seasonal melt (net vs gross open, aaiw C2), and the
    layer_4 term is the CDW-attributable increment only.
    """
    hosing = REPORTED["P_hosing_sv"]["value"]
    basal = cdw_basal_melt_rate_Gt_yr(cdw_heat_flux_TW)
    seaice_drop = meltwater_change()["drop_km3_yr"]
    rows = [
        ("P hosing (model forcing)", sv_to_gt_yr(hosing), hosing),
        ("AAIW sea-ice meltwater drop 2016-2024", seaice_drop, gt_yr_to_sv(seaice_drop)),
        ("layer_4 CDW-attributable basal melt", basal, gt_yr_to_sv(basal)),
    ]
    return [{"term": t, "gt_yr": g, "sv": s, "x_layer4": g / basal if basal else None,
             "grade": DERIVED} for t, g, s in rows]


# --------------------------------------------------------------------------
# Youngs: what a forced-only melt term misses
# --------------------------------------------------------------------------

def forced_only_underestimate(feedback_share: float) -> float:
    """Factor by which a forced-only term underestimates the melt INCREASE.

    If feedback carries a share f of the total increase, the forced part is
    (1 - f) of it, so total / forced = 1 / (1 - f). f = 2/3 gives 3.0.
    Applies to the increment, not to total melt. f must lie in [0, 1).
    A negative f (net negative feedback) is allowed and gives a factor < 1.
    """
    if feedback_share >= 1.0:
        raise ValueError("feedback share >= 1 means the forced part is zero or negative")
    return 1.0 / (1.0 - feedback_share)


def layer4_melt_band(cdw_heat_flux_TW: float = 2.81) -> Dict:
    """layer_4's CDW basal-melt increment read under Y, as a band (SCOPE).

    layer_4's sensitivity (80 Gt/yr per TW) is documented as 'empirical, from
    intrusion-event studies (Schmidtko 2014, Naughten 2018)'. Whether it
    already contains the melt feedback depends on which: an observed
    relationship includes whatever feedback operated during the events; a
    forced-only model response does not. That origin is not settled here,
    so both ends are returned and neither is picked:

      lower  : sensitivity already includes feedback -> factor 1
      upper  : sensitivity is forced-only, Y's 2/3 applies -> factor 3

    The circumpolar 2/3 is a total over shelves with opposite-sign regions;
    applying it to a CDW-intrusion term (largely Amundsen/Bellingshausen) is
    itself a scope transfer, flagged.
    """
    f = REPORTED["Y_feedback_share_of_increase"]["value"]
    base = cdw_basal_melt_rate_Gt_yr(cdw_heat_flux_TW)
    k = forced_only_underestimate(f)
    return {"layer4_gt_yr": base,
            "band_gt_yr": (base, base * k),
            "band_sv": (gt_yr_to_sv(base), gt_yr_to_sv(base * k)),
            "factor_if_forced_only": k,
            "grade": DERIVED,
            "scope": ("band, not a correction: depends on whether layer_4's "
                      "sensitivity is observed (feedback in) or forced-only "
                      "(feedback out); circumpolar share applied to a regional "
                      "term"),
            "grade_scope": PROPOSED}


# --------------------------------------------------------------------------
# Pauling: the model spread, and the sign tension with observations
# --------------------------------------------------------------------------

def sea_ice_sensitivity_mkm2_per_sv() -> Tuple[float, float]:
    """Sea-ice area gain per Sv of surface meltwater, across the ensemble.

    DERIVED by dividing the stated range by 0.1 Sv. Valid AT 0.1 Sv under
    pre-industrial forcing only; the response need not be linear.
    """
    lo, hi = REPORTED["P_sea_ice_gain_mkm2"]["value"]
    s = REPORTED["P_hosing_sv"]["value"]
    return (lo / s, hi / s)


def model_spread_factor() -> float:
    """Ratio of the largest to smallest model response (DERIVED)."""
    lo, hi = REPORTED["P_sea_ice_gain_mkm2"]["value"]
    return hi / lo


def layer4_term_through_pauling(cdw_heat_flux_TW: float = 2.81) -> Dict:
    """What P's ensemble would say about layer_4's increment, if linear.

    PROPOSED and OUT OF RANGE: the layer_4 term is ~30x smaller than the
    hosing, enters at depth not at the surface, and sits on present-day not
    pre-industrial forcing. Returned to show the size of the gap, not as a
    prediction. Uses the layer4_melt_band so both ends propagate.
    """
    lo_s, hi_s = sea_ice_sensitivity_mkm2_per_sv()
    band = layer4_melt_band(cdw_heat_flux_TW)["band_sv"]
    return {"mkm2_band": (band[0] * lo_s, band[1] * hi_s),
            "in_tested_range": False,
            "grade": PROPOSED,
            "why_out_of_range": ["amplitude ~30x below 0.1 Sv",
                                 "depth injection vs surface",
                                 "present-day vs pre-industrial mean state"]}


SIGN_TENSION: Dict = {
    "models": "added coastal meltwater -> MORE sea ice, in all 11 models (P)",
    "observed": "sea ice dropped from 2016 (aaiw_reversal_2026; Spira 2026) while "
                "the repo's CDW-AABW-Cryosphere loop has basal melt rising",
    "status": "OPEN",
    "candidate_readings": [
        ("R1", "amplitude: the post-2016 meltwater increase is far below the "
               "0.1 Sv the ensemble was run at, so its sea-ice effect is small "
               "against other drivers", PROPOSED),
        ("R2", "competing driver: wind-driven mixing of warm Winter Water "
               "(Spira 2026) outweighs any meltwater stratification", PROPOSED),
        ("R3", "injection depth: ensemble meltwater enters at the surface; basal "
               "melt leaves the cavity at depth and Y's feedbacks act on shelf "
               "water, so the surface-freshening path the models test may not "
               "be the path that operates", PROPOSED),
        ("R4", "mean-state bias: P itself attributes its 5.8x spread to model "
               "mean states; the observed ocean may sit outside the ensemble",
               PROPOSED),
    ],
    "chosen": None,
    "what_would_split_them": (
        "R1 vs the rest: an observed post-2016 meltwater flux in Sv. "
        "R2 vs R3: a hosing run with the same flux injected at depth "
        "(the ensemble's own 'missing boundary condition'). "
        "R4: where observed mean-state sea-ice area falls in P's model list."),
}

OPEN_CHECKS: List[Tuple[str, str, str]] = [
    ("F1", "Is layer_4's 80 Gt/yr/TW sensitivity observed or forced-only model output?",
     "collapses layer4_melt_band to one end"),
    ("F2", "Y's regional melt and feedback shares (figures / SI).",
     "replaces the circumpolar-to-regional scope transfer"),
    ("F3", "Observed net Antarctic meltwater increase since 2016, in Sv.",
     "settles R1 of SIGN_TENSION"),
    ("F4", "Does P separate net from gross, and does it say what the response is at depth?",
     "R3; links to aaiw_reversal_2026 C2 and C3"),
    ("F5", "P is a preprint: check the reviewed version's numbers.",
     "STATED values may move"),
]


def summary() -> str:
    lines = ["Ice-shelf melt feedback + meltwater-sea-ice ensemble (2026, CITED_ABSTRACT)"]
    lines.append("  freshwater terms on one scale  [DERIVED, not summable]")
    for r in freshwater_scale():
        lines.append(f"    {r['term']:40s} {r['gt_yr']:8.1f} Gt/yr  {r['sv']:.4f} Sv  "
                     f"{r['x_layer4']:6.1f}x layer_4")
    b = layer4_melt_band()
    lines.append(f"  Y: feedback 2/3 of increase -> forced-only misses x"
                 f"{b['factor_if_forced_only']:.1f}")
    lines.append(f"     layer_4 band {b['band_gt_yr'][0]:.1f} .. {b['band_gt_yr'][1]:.1f} Gt/yr"
                 f"  (which end: F1)")
    lo, hi = sea_ice_sensitivity_mkm2_per_sv()
    lines.append(f"  P: {lo:.1f} .. {hi:.1f} million km^2 per Sv at 0.1 Sv, "
                 f"spread x{model_spread_factor():.2f}")
    t = layer4_term_through_pauling()
    lines.append(f"     layer_4 through P (out of range): {t['mkm2_band'][0]:.3f} .. "
                 f"{t['mkm2_band'][1]:.3f} million km^2")
    lines.append(f"  sign tension: {SIGN_TENSION['status']}, readings "
                 + ", ".join(r[0] for r in SIGN_TENSION["candidate_readings"])
                 + ", none chosen")
    lines.append("  open checks: " + ", ".join(c[0] for c in OPEN_CHECKS))
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary())
