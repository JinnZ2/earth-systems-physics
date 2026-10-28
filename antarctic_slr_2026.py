# antarctic_slr_2026.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Two 2026 projections of Antarctica's sea-level contribution, read against
# each other and against the observed 2025 sea-level budget in
# state_of_the_climate_2025.
#
#   M  McCormack, Morlighem, Pattyn, Robel, Seroussi (2026),
#      "Emergent decadal predictability in Antarctic contribution to sea
#      level rise", Nature 654:609-613, doi:10.1038/s41586-026-10614-4
#      (published 2026-06-18).
#      Present ice loss predicts the next 3-5 decades; the link weakens and
#      dissolves around 2080. Says it rules out an IPCC low-likelihood,
#      high-impact scenario.
#
#   L  Lin, Kopp et al. (2026), Nature Geoscience. Rutgers release
#      2026-09-30. DOI INFERRED from the linked URL as
#      10.1038/s41561-026-02102-1; not stated on the page.
#      Machine-learning emulator over an existing ice-sheet ensemble,
#      weighted by fit to 2002-2021 satellite ice loss.
#
# Co-authored, human + Claude, 2026-10-28.
#
# SOURCE GRADE
# ------------
# CITED_PRESS for both. M read through ARC SAEF news and ScienceDaily;
# L through the Rutgers release. nature.com and phys.org refused the fetch.
# The papers were not read. Upgrade to CITED after reading them.
#
# WHAT THIS MODULE DOES
# ---------------------
# 1. Reconstructs the scenario M rules out from its two press-stated rates
#    and checks the stated 30 cm total (DERIVED).
# 2. Sets the scenario's 2025 starting rate against the OBSERVED 2025 budget.
#    That rate is above the whole observed land-ice term, so the press
#    rendering cannot be the scenario as the paper used it. Recorded as a
#    RENDERING_CONFLICT, not resolved here.
# 3. Puts M and L on one scale (mm by year).
# 4. Joint reading (PROPOSED): L's observation weighting uses a window that
#    falls inside M's predictable regime, so it constrains the decades that
#    are already constrained, and says little about the post-2080 divergence
#    M names.
#
# WHAT IT DOES NOT DO
# -------------------
# Not wired into cascade_engine. No projection is made. Does not treat M and
# L as independent confirmations: they draw on overlapping ice-sheet model
# ensembles and community; independence is NOT established.

from typing import Dict, List, Tuple

from state_of_the_climate_2025 import sea_level_budget

STATED = "STATED"
DERIVED = "DERIVED"
PROPOSED = "PROPOSED"
INFERRED = "INFERRED"
NOT_IN_TEXT = "NOT_IN_TEXT"
CITED_PRESS = "CITED_PRESS"
RENDERING_CONFLICT = "RENDERING_CONFLICT"

MM_PER_INCH = 25.4

STUDIES: Dict[str, Dict] = {
    "mccormack_2026": {
        "doi": "10.1038/s41586-026-10614-4",
        "venue": "Nature 654:609-613, 2026-06-18",
        "grade": CITED_PRESS,
        "read": "arcsaef.com news; sciencedaily.com 2026-07-22 release",
    },
    "lin_kopp_2026": {
        "doi": "10.1038/s41561-026-02102-1",
        "doi_grade": INFERRED,
        "venue": "Nature Geoscience; Rutgers release 2026-09-30",
        "grade": CITED_PRESS,
        "read": "rutgers.edu news release",
    },
}

REPORTED: Dict[str, Dict] = {
    # --- McCormack et al. ---
    "M_predictable_decades": {"value": (3, 5), "grade": STATED,
                              "note": "rate over the next 3-5 decades follows from today's loss"},
    "M_predictable_until": {"value": "about mid-century", "grade": STATED},
    "M_link_dissolves_year": {"value": 2080, "grade": STATED,
                              "note": "'by roughly 2080'"},
    "M_mechanism": {"value": "reservoir time: thick ice responds slowly", "grade": STATED},
    "M_after": {"value": "marine-ice retreat feedbacks; needs bed topography", "grade": STATED},
    "M_ruled_out_rate_2025_mm_yr": {"value": 7.0, "grade": STATED,
                                    "note": "ARC SAEF rendering"},
    "M_ruled_out_rate_2055_mm_yr": {"value": 13.0, "grade": STATED},
    "M_ruled_out_total_cm": {"value": 30.0, "grade": STATED,
                             "note": "'roughly 30 cm' 2025-2055"},
    "M_ruled_out_scope": {
        "value": "Antarctic ice loss alone",
        "grade": STATED,
        "note": "ScienceDaily: 'the rate of sea level rise caused by Antarctic ice "
                "loss alone could almost double over the next 30 years'"},
    # --- Lin / Kopp et al. ---
    "L_p_net_loss_ambitious": {"value": 0.92, "grade": STATED,
                               "note": "'at least', net-zero CO2 around 2050"},
    "L_p_low_below_high": {"value": 0.89, "grade": STATED, "note": "'at least'"},
    "L_2100_high_emissions_in": {"value": {"middle": 6.0, "upper": 10.0},
                                 "grade": STATED,
                                 "note": "high-end analysis, Antarctica only, inches"},
    "L_calibration_window": {"value": (2002, 2021), "grade": STATED},
    "L_low_emissions_2100": {"value": None, "grade": NOT_IN_TEXT},
    "L_2300": {"value": None, "grade": NOT_IN_TEXT},
    "L_baseline_year": {"value": None, "grade": NOT_IN_TEXT},
}


def ramp_total_mm(rate0_mm_yr: float, rate1_mm_yr: float, years: float) -> float:
    """Total rise for a rate rising linearly from rate0 to rate1 over years."""
    return 0.5 * (rate0_mm_yr + rate1_mm_yr) * years


def ruled_out_scenario() -> Dict:
    """Reconstruct M's ruled-out scenario from its stated rates (DERIVED).

    Linear 7 -> 13 mm/yr over 2025-2055 gives 300 mm, matching 'roughly
    30 cm'. 13/7 = 1.86, matching 'almost double'. The two renderings agree
    with each other.
    """
    r0 = REPORTED["M_ruled_out_rate_2025_mm_yr"]["value"]
    r1 = REPORTED["M_ruled_out_rate_2055_mm_yr"]["value"]
    total = ramp_total_mm(r0, r1, 30.0)
    return {"total_mm": total, "stated_cm": REPORTED["M_ruled_out_total_cm"]["value"],
            "consistent_with_stated": abs(total / 10.0 - 30.0) < 1.0,
            "rate_ratio": r1 / r0, "grade": DERIVED}


def start_rate_vs_observed() -> Dict:
    """The scenario's 2025 rate against the observed 2025 sea-level budget.

    Observed (BAMS 2026, via state_of_the_climate_2025): thermal 1.6 + mass
    2.0 = 3.6 mm/yr, where 'mass' is ALL land ice (Antarctica, Greenland,
    glaciers). An Antarctic-only rate of 7 mm/yr in 2025 is 3.5x the whole
    land-ice term and about 1.9x total sea-level rise.

    So the press rendering ('Antarctic alone', 7 mm/yr in 2025) cannot be the
    scenario as observed in 2025. Either the 7 mm/yr is a different quantity
    (total sea level, a later start year, or a different unit) or the scope
    word is the press layer's. Ruling out a scenario whose starting point is
    already off-observation would be trivial, so this is a reason to read M
    before using 'rules out'. RENDERING_CONFLICT: not resolved here.
    """
    obs = sea_level_budget()
    r0 = REPORTED["M_ruled_out_rate_2025_mm_yr"]["value"]
    return {"scenario_2025_mm_yr": r0,
            "observed_total_mm_yr": obs["component_sum_mm_yr"],
            "observed_land_ice_mm_yr": obs["mass_mm_yr"],
            "x_land_ice": r0 / obs["mass_mm_yr"],
            "x_total": r0 / obs["component_sum_mm_yr"],
            "grade": DERIVED,
            "status": RENDERING_CONFLICT}


def lin_kopp_2100_mm() -> Dict[str, float]:
    """L's 2100 high-emissions Antarctic figures, inches -> mm (DERIVED)."""
    v = REPORTED["L_2100_high_emissions_in"]["value"]
    return {k: x * MM_PER_INCH for k, x in v.items()}


def one_scale() -> List[Dict]:
    """M's ruled-out scenario and L's upper estimate on one scale.

    The ruled-out scenario puts 300 mm of Antarctic rise in 30 years (by
    2055); L's upper high-emissions estimate puts 254 mm in about 75 years
    (by 2100). Two 2026 studies both exclude that scenario's magnitude.
    They are not shown to be independent (shared model ensembles).

    [CHOICE 1] L's mean rate divides by 75 years, assuming a 2025 baseline.
    L's baseline year is NOT_IN_TEXT; the 2100 totals do not depend on it.
    """
    s = ruled_out_scenario()
    l = lin_kopp_2100_mm()
    return [
        {"what": "M ruled-out scenario (Antarctic, as rendered)", "mm": s["total_mm"],
         "by": 2055, "mm_per_yr_mean": s["total_mm"] / 30.0},
        {"what": "L upper, very high emissions", "mm": l["upper"],
         "by": 2100, "mm_per_yr_mean": l["upper"] / 75.0},
        {"what": "L middle, very high emissions", "mm": l["middle"],
         "by": 2100, "mm_per_yr_mean": l["middle"] / 75.0},
    ]


def calibration_inside_predictable_regime() -> Dict:
    """Joint reading of M and L (PROPOSED).

    L weights ensemble members by fit to 2002-2021 ice loss. M says present
    loss predicts the next 3-5 decades and the link dissolves near 2080. A
    weighting by present loss therefore buys the most in exactly the window
    M already calls predictable, and the least after ~2080 where M says the
    trajectories diverge on marine-ice feedbacks. L's 2100 figures lie
    after that horizon, so their spread is the part observation weighting
    does least to narrow. L itself says processes missing from the ensemble
    leave outcomes beyond its projections open.
    """
    lo, hi = REPORTED["M_predictable_decades"]["value"]
    end_cal = REPORTED["L_calibration_window"]["value"][1]
    return {"calibration_end": end_cal,
            "predictable_through": (end_cal + 10 * lo, end_cal + 10 * hi),
            "link_dissolves": REPORTED["M_link_dissolves_year"]["value"],
            "L_projection_year": 2100,
            "projection_past_dissolve": 2100 > REPORTED["M_link_dissolves_year"]["value"],
            "grade": PROPOSED}


OPEN_CHECKS: List[Tuple[str, str, str]] = [
    ("S1", "What exactly is the 7 -> 13 mm/yr scenario in M (quantity, years, source)?",
     "resolves start_rate_vs_observed RENDERING_CONFLICT"),
    ("S2", "L's DOI and its 2300 and low-emissions numbers.",
     "INFERRED -> STATED"),
    ("S3", "Do M and L draw on the same ice-sheet ensemble (ISMIP6 or other)?",
     "independence of the two exclusions"),
    ("S4", "Is the M predictability horizon scenario-dependent?",
     "whether calibration_inside_predictable_regime holds under low emissions"),
]


def summary() -> str:
    s = ruled_out_scenario()
    o = start_rate_vs_observed()
    c = calibration_inside_predictable_regime()
    lines = ["Antarctic SLR projections 2026 (CITED_PRESS)",
             f"  M ruled-out scenario: 7 -> 13 mm/yr, linear = {s['total_mm']:.0f} mm "
             f"(stated ~{s['stated_cm']:.0f} cm, ratio {s['rate_ratio']:.2f})"]
    lines.append(f"  start rate {o['scenario_2025_mm_yr']:.1f} mm/yr vs observed 2025: "
                 f"land ice {o['observed_land_ice_mm_yr']:.1f} (x{o['x_land_ice']:.1f}), "
                 f"total {o['observed_total_mm_yr']:.1f} (x{o['x_total']:.1f})  "
                 f"[{o['status']}]")
    for r in one_scale():
        lines.append(f"  {r['what']:45s} {r['mm']:6.1f} mm by {r['by']}  "
                     f"({r['mm_per_yr_mean']:.1f} mm/yr mean)")
    lines.append(f"  L calibration ends {c['calibration_end']}; M predictable through "
                 f"{c['predictable_through'][0]}-{c['predictable_through'][1]}; link "
                 f"dissolves ~{c['link_dissolves']}; L projects to {c['L_projection_year']}"
                 f"  [{c['grade']}]")
    lines.append("  open checks: " + ", ".join(x[0] for x in OPEN_CHECKS))
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary())
