# test_aaiw_reversal_2026.py — earth-systems-physics — CC0
import pytest

import aaiw_reversal_2026 as a


def test_sverdrup_conversion_known_answer():
    assert a.km3_yr_to_sv(a.KM3_PER_YR_PER_SV) == pytest.approx(1.0)
    assert a.KM3_PER_YR_PER_SV == pytest.approx(31557.6)


def test_meltwater_change_from_stated_numbers():
    mw = a.meltwater_change()
    assert mw["pre_km3_yr"] == 19800.0 and mw["post_km3_yr"] == 13200.0
    assert mw["drop_km3_yr"] == 6600.0
    assert mw["drop_fraction"] == pytest.approx(1 / 3)
    assert mw["drop_sv"] == pytest.approx(0.209, abs=1e-3)


def test_freshwater_terms_use_layer4_and_keep_grades_apart():
    ft = a.freshwater_terms_beside_cdw_loop()
    assert ft["cdw_attributable_basal_melt_Gt_yr"] == pytest.approx(104.8)
    assert ft["ratio_drop_to_basal"] == pytest.approx(62.98, abs=0.01)
    assert ft["grade_ratio"] == a.DERIVED and ft["grade_reading"] == a.PROPOSED


def test_zero_cdw_excess_gives_no_ratio_not_infinity():
    ft = a.freshwater_terms_beside_cdw_loop(cdw_heat_flux_TW=1.0)
    assert ft["cdw_attributable_basal_melt_Gt_yr"] == 0.0
    assert ft["ratio_drop_to_basal"] is None


def test_unread_fields_stay_not_in_text():
    for k in ("salinity_density_magnitudes", "depths",
              "internal_variability_treatment", "glacial_or_ice_shelf_meltwater"):
        assert a.REPORTED[k]["value"] is None
        assert a.REPORTED[k]["grade"] == a.NOT_IN_TEXT


def test_record_length_and_study_grade():
    assert a.record_length()["post_reversal_years"] == 9
    assert a.STUDY["grade"] == a.CITED_PRESS
    assert len(a.OPEN_CHECKS) == 5


def test_not_wired_into_cascade_engine():
    import cascade_engine
    src = open(cascade_engine.__file__).read()
    assert "aaiw_reversal_2026" not in src


def test_summary_runs():
    s = a.summary()
    assert "CITED_PRESS" in s and "63.0" in s
