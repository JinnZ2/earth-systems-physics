# test_antarctic_2026.py — earth-systems-physics — CC0
import pytest

import antarctic_sea_ice_2026 as si
import antarctic_slr_2026 as slr


def test_ramp_known_answer():
    assert slr.ramp_total_mm(7.0, 13.0, 30.0) == 300.0
    assert slr.ramp_total_mm(5.0, 5.0, 10.0) == 50.0


def test_ruled_out_scenario_reproduces_stated_total():
    s = slr.ruled_out_scenario()
    assert s["consistent_with_stated"] is True
    assert s["rate_ratio"] == pytest.approx(1.857, abs=1e-3)


def test_start_rate_exceeds_observed_land_ice_and_total():
    o = slr.start_rate_vs_observed()
    assert o["observed_land_ice_mm_yr"] == pytest.approx(2.0)
    assert o["observed_total_mm_yr"] == pytest.approx(3.6)
    assert o["x_land_ice"] == pytest.approx(3.5)
    assert o["x_total"] > 1.0
    assert o["status"] == slr.RENDERING_CONFLICT


def test_inches_to_mm():
    l = slr.lin_kopp_2100_mm()
    assert l["middle"] == pytest.approx(152.4) and l["upper"] == pytest.approx(254.0)


def test_ruled_out_exceeds_lin_kopp_upper_in_less_time():
    rows = slr.one_scale()
    assert rows[0]["mm"] > rows[1]["mm"] and rows[0]["by"] < rows[1]["by"]


def test_calibration_window_inside_predictable_regime():
    c = slr.calibration_inside_predictable_regime()
    assert c["predictable_through"] == (2051, 2071)
    assert c["projection_past_dissolve"] is True
    assert c["grade"] == slr.PROPOSED


def test_lin_kopp_doi_is_marked_inferred_and_gaps_absent():
    assert slr.STUDIES["lin_kopp_2026"]["doi_grade"] == slr.INFERRED
    for k in ("L_low_emissions_2100", "L_2300", "L_baseline_year"):
        assert slr.REPORTED[k]["value"] is None


def test_breid_bay_scales():
    s = si.breid_bay_on_repo_scales()
    assert s["area_mkm2"] == pytest.approx(0.089121)
    assert s["frac_of_2026_max"] == pytest.approx(0.005067, abs=1e-5)
    assert s["frac_of_pauling_min"] == pytest.approx(0.1255, abs=1e-3)


def test_breid_bay_bears_on_existing_reading_and_chooses_none():
    from ice_shelf_melt_feedback_2026 import SIGN_TENSION
    assert [r for r, _ in si.bears_on_sign_tension()] == ["R2"]
    assert SIGN_TENSION["chosen"] is None


def test_unresolved_items_stay_unresolved():
    assert si.NATURE_NEWS_HOLE["same_event_as_breid_bay"] is None
    assert si.BREID_BAY["meltwater_term"]["value"] is None


def test_summaries_run():
    assert "RENDERING_CONFLICT" in slr.summary()
    assert "Breid Bay" in si.summary()


def test_ar6_anchor_sharpens_conflict():
    a = slr.ar6_anchor_check()
    assert a["ar6_antarctic_mm_yr"][0] == pytest.approx(0.409, abs=1e-3)
    assert a["x_ar6_antarctic_central"] == pytest.approx(17.1, abs=0.1)
    assert a["x_ar6_antarctic_upper"] > 10
    assert a["status"] == slr.RENDERING_CONFLICT
    assert slr.AR6["box_9_4_rates"]["value"] is None
