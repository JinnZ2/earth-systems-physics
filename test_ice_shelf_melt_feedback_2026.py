# test_ice_shelf_melt_feedback_2026.py — earth-systems-physics — CC0
import ast
import inspect

import pytest

import ice_shelf_melt_feedback_2026 as m


def test_sv_gt_round_trip_known_answer():
    assert m.sv_to_gt_yr(1.0) == pytest.approx(31557.6)
    assert m.gt_yr_to_sv(m.sv_to_gt_yr(0.1)) == pytest.approx(0.1)


def test_freshwater_scale_matches_both_sibling_modules():
    rows = {r["term"].split(" ")[0]: r for r in m.freshwater_scale()}
    assert rows["P"]["gt_yr"] == pytest.approx(3155.76)
    assert rows["AAIW"]["sv"] == pytest.approx(0.209, abs=1e-3)
    assert rows["layer_4"]["gt_yr"] == pytest.approx(104.8)
    assert rows["P"]["x_layer4"] == pytest.approx(30.1, abs=0.1)
    assert all(r["grade"] == m.DERIVED for r in m.freshwater_scale())


def test_freshwater_scale_zero_layer4_gives_none_not_inf():
    rows = m.freshwater_scale(cdw_heat_flux_TW=1.0)
    assert all(r["x_layer4"] is None for r in rows)


def test_forced_only_factor_known_answers():
    assert m.forced_only_underestimate(2 / 3) == pytest.approx(3.0)
    assert m.forced_only_underestimate(0.0) == 1.0
    # net negative feedback: forced-only OVERestimates the increase
    assert m.forced_only_underestimate(-1.0) == pytest.approx(0.5)
    with pytest.raises(ValueError):
        m.forced_only_underestimate(1.0)


def test_layer4_band_is_a_band_not_a_correction():
    b = m.layer4_melt_band()
    lo, hi = b["band_gt_yr"]
    assert lo == pytest.approx(104.8) and hi == pytest.approx(314.4)
    assert b["grade_scope"] == m.PROPOSED
    assert "F1" in [c[0] for c in m.OPEN_CHECKS]


def test_layer4_module_not_modified_by_reading():
    import layer_4_hydrosphere as l4
    m.layer4_melt_band()
    assert l4.cdw_basal_melt_rate_Gt_yr(2.81) == pytest.approx(104.8)


def test_pauling_sensitivity_and_spread():
    lo, hi = m.sea_ice_sensitivity_mkm2_per_sv()
    assert lo == pytest.approx(7.1) and hi == pytest.approx(41.4)
    assert m.model_spread_factor() == pytest.approx(5.83, abs=0.01)


def test_pauling_extrapolation_flagged_out_of_range():
    t = m.layer4_term_through_pauling()
    assert t["in_tested_range"] is False and t["grade"] == m.PROPOSED
    assert t["mkm2_band"][0] < t["mkm2_band"][1]


def test_sign_tension_open_none_chosen():
    st = m.SIGN_TENSION
    assert st["status"] == "OPEN" and st["chosen"] is None
    assert all(r[2] == m.PROPOSED for r in st["candidate_readings"])


def test_absent_numbers_stay_absent():
    for k in ("Y_melt_rates", "Y_regional_shares", "P_net_vs_gross"):
        assert m.REPORTED[k]["value"] is None
        assert m.REPORTED[k]["grade"] == m.NOT_IN_TEXT


def test_preprint_flagged():
    assert m.STUDIES["pauling_2026"]["peer_reviewed"] is False
    assert all(s["grade"] == m.CITED_ABSTRACT for s in m.STUDIES.values())


def test_no_total_basal_melt_supplied_from_memory():
    # module states it does not carry a total Antarctic basal melt figure
    src = inspect.getsource(m)
    tree = ast.parse(src)
    floats = {n.value for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)}
    assert not any(v > 1000 for v in floats)


def test_summary_runs():
    s = m.summary()
    assert "sign tension: OPEN" in s and "x3.0" in s
