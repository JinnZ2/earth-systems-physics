# test_extraction_dynamics.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Tests for extraction_dynamics/. The folder is a standalone script
# package (bare imports inside the folder), so these tests adjust
# sys.path the same way the boundary_waters tests do.

import os
import sys

import pytest

ED_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "extraction_dynamics"))

_MODULES = ("interaction_taxonomy", "functional_response",
            "consumer_resource", "depensation", "energy_return",
            "surplus_production", "soil_carbon", "domain_mapping", "audit")


@pytest.fixture(autouse=True)
def _extraction_path():
    """Put the folder on sys.path for each test and clean up after."""
    if ED_DIR not in sys.path:
        sys.path.insert(0, ED_DIR)
    yield
    if ED_DIR in sys.path:
        sys.path.remove(ED_DIR)
    for m in _MODULES:
        sys.modules.pop(m, None)


# ═════════════════════════════════════════════════════════════
# INTERACTION TAXONOMY
# ═════════════════════════════════════════════════════════════

class TestInteractionTaxonomy:

    def test_sign_pairs_are_correct(self):
        import interaction_taxonomy as it
        assert it.get("predation").sign_pair == ("+", "-")
        assert it.get("hyperpredation").sign_pair == ("+", "-")
        assert it.get("mining").sign_pair == ("+", "0")
        assert it.get("competition").sign_pair == ("-", "-")
        assert it.get("mutualism").sign_pair == ("+", "+")

    def test_predation_and_hyperpredation_share_signs_differ_in_coupling(self):
        """The signs cannot distinguish them. Only the coupling can —
        which is the entire point of the taxonomy."""
        import interaction_taxonomy as it
        pred, hyper = it.get("predation"), it.get("hyperpredation")
        assert pred.sign_pair == hyper.sign_pair
        assert pred.consumer_coupled is True
        assert hyper.consumer_coupled is False

    def test_mining_has_no_recruitment_term(self):
        import interaction_taxonomy as it
        assert it.get("mining").resource_recruits is False

    def test_classify_from_structure_alone(self):
        import interaction_taxonomy as it
        assert it.classify(True, True) == "predation"
        assert it.classify(False, True) == "hyperpredation"
        assert it.classify(False, False) == "mining"
        assert it.classify(True, False) == "mining"

    def test_uncoupled_set_names_the_brakeless_interactions(self):
        import interaction_taxonomy as it
        assert "hyperpredation" in it.UNCOUPLED
        assert "mining" in it.UNCOUPLED
        assert "predation" not in it.UNCOUPLED

    def test_unknown_interaction_raises_with_valid_set(self):
        import interaction_taxonomy as it
        with pytest.raises(KeyError):
            it.get("extractivism")


# ═════════════════════════════════════════════════════════════
# FUNCTIONAL RESPONSE AND THE REFUGE
# ═════════════════════════════════════════════════════════════

class TestFunctionalResponse:

    def test_type_II_saturates_at_one_over_h(self):
        import functional_response as fr
        assert fr.holling_II(1e9, 2.0, 0.5) == pytest.approx(2.0, rel=1e-3)

    def test_type_III_is_below_type_II_at_low_density(self):
        import functional_response as fr
        assert fr.holling_III(0.05, 2.0, 1.0) < fr.holling_II(0.05, 2.0, 1.0)

    def test_type_III_with_q_equal_one_IS_type_II(self):
        """q is continuous, so refuge loss is a drift in a parameter
        rather than a change of model."""
        import functional_response as fr
        for N in (0.01, 0.1, 1.0, 10.0):
            assert fr.holling_III(N, 2.0, 1.0, 1.0) == pytest.approx(
                fr.holling_II(N, 2.0, 1.0))

    def test_type_II_per_capita_mortality_is_maximal_when_rarest(self):
        """The whole problem in one assertion."""
        import functional_response as fr
        m_rare = fr.per_capita_mortality(0.01, 2.0, 1.0, kind="II")
        m_common = fr.per_capita_mortality(1.0, 2.0, 1.0, kind="II")
        assert m_rare > m_common

    def test_type_III_per_capita_mortality_falls_toward_zero(self):
        import functional_response as fr
        m_rare = fr.per_capita_mortality(0.01, 2.0, 1.0, 2.0, "III")
        m_common = fr.per_capita_mortality(1.0, 2.0, 1.0, 2.0, "III")
        assert m_rare < m_common
        assert m_rare == pytest.approx(0.0, abs=0.05)

    def test_refuge_index_high_for_type_III_zero_for_type_II(self):
        import functional_response as fr
        assert fr.refuge_index(0.05, 2.0, 1.0, 2.0, "III", N_ref=1.0) > 0.8
        assert fr.refuge_index(0.05, 2.0, 1.0, 1.0, "II", N_ref=1.0) < 0.1

    def test_technology_raises_a_lowers_h_reduces_q(self):
        import functional_response as fr
        r = fr.apply_technology(2.0, 1.0, 2.0,
                                ["echo_sounder", "at_sea_processing"])
        assert r["a_after"] > r["a_before"]
        assert r["h_after"] < r["h_before"]
        assert r["q_after"] < r["q_before"]

    def test_only_q_reduction_removes_the_refuge(self):
        """Handling-time automation makes the consumer faster; it does
        not remove the low-density refuge. Only the search-efficiency
        floor does."""
        import functional_response as fr
        handling_only = fr.apply_technology(2.0, 1.0, 2.0,
                                            ["at_sea_processing"])
        detection = fr.apply_technology(
            2.0, 1.0, 2.0, ["ai_routing_on_pooled_fleet_data"])
        assert handling_only["refuge_lost"] < 0.05
        assert detection["refuge_lost"] > 0.3

    def test_stacked_detection_collapses_to_type_II(self):
        import functional_response as fr
        r = fr.apply_technology(
            2.0, 1.0, 2.0,
            ["echo_sounder", "spotter_aircraft",
             "satellite_and_oceanographic_routing",
             "ai_routing_on_pooled_fleet_data"])
        assert r["collapsed_to_type_II"] is True
        assert r["q_after"] == pytest.approx(1.0)

    def test_unknown_technology_raises(self):
        import functional_response as fr
        with pytest.raises(KeyError):
            fr.apply_technology(1.0, 1.0, 2.0, ["telepathy"])


class TestFunctionalResponseFit:
    """The falsifiable part: can the two forms be told apart?"""

    N_SERIES = [0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0]

    def test_recovers_type_III_from_sigmoidal_data(self):
        import functional_response as fr
        y = [fr.holling_III(n, 2.0, 1.0, 2.0) for n in self.N_SERIES]
        fit = fr.fit_functional_response(self.N_SERIES, y)
        assert fit["winner"] == "III"
        assert fit["q_fitted"] == pytest.approx(2.0, abs=0.1)
        assert fit["refuge_present"] is True

    def test_recovers_type_II_from_saturating_data(self):
        import functional_response as fr
        y = [fr.holling_II(n, 2.0, 1.0) for n in self.N_SERIES]
        fit = fr.fit_functional_response(self.N_SERIES, y)
        assert fit["winner"] == "II"
        assert fit["q_fitted"] == pytest.approx(1.0, abs=0.05)
        assert fit["refuge_present"] is False

    def test_recovers_parameters_not_just_the_form(self):
        import functional_response as fr
        y = [fr.holling_III(n, 3.0, 0.5, 1.8) for n in self.N_SERIES]
        fit = fr.fit_functional_response(self.N_SERIES, y)
        assert fit["type_III"]["a"] == pytest.approx(3.0, rel=0.15)
        assert fit["type_III"]["h"] == pytest.approx(0.5, rel=0.15)
        assert fit["type_III"]["q"] == pytest.approx(1.8, abs=0.1)

    def test_survives_moderate_noise(self):
        """A decade of CPUE data is not noiseless."""
        import functional_response as fr
        import random
        rng = random.Random(42)
        y = [fr.holling_III(n, 2.0, 1.0, 2.0) * (1 + rng.uniform(-0.05, 0.05))
             for n in self.N_SERIES]
        fit = fr.fit_functional_response(self.N_SERIES, y)
        assert fit["winner"] == "III"

    def test_refuse_to_fit_too_few_points(self):
        import functional_response as fr
        with pytest.raises(ValueError):
            fr.fit_functional_response([0.1, 0.5], [0.1, 0.4])


# ═════════════════════════════════════════════════════════════
# CONSUMER-RESOURCE AND THE SUBSIDY TERM
# ═════════════════════════════════════════════════════════════

class TestConsumerResource:

    BASE = dict(r=0.5, K=1.0, a=2.0, h=1.0, e=0.45, m=0.2)

    def test_coupling_index_is_one_without_subsidy(self):
        import consumer_resource as cr
        p = cr.Params(**self.BASE, S=0.0)
        assert cr.coupling_index(0.8, 0.1, p) == pytest.approx(1.0)

    def test_coupling_index_falls_with_subsidy(self):
        import consumer_resource as cr
        low = cr.coupling_index(0.8, 0.1, cr.Params(**self.BASE, S=0.01))
        high = cr.coupling_index(0.8, 0.1, cr.Params(**self.BASE, S=0.2))
        assert 0.0 < high < low < 1.0

    def test_coupling_is_state_dependent_not_a_fixed_property(self):
        """A fleet can be coupled at high stock and uncoupled at low
        stock. That transition is how the change gets missed."""
        import consumer_resource as cr
        p = cr.Params(**self.BASE, S=0.05)
        assert (cr.coupling_index(0.05, 0.1, p)
                < cr.coupling_index(0.9, 0.1, p))

    def test_consumer_standing_stock_at_zero_resource_is_S_over_m(self):
        import consumer_resource as cr
        p = cr.Params(**self.BASE, S=0.05)
        assert cr.refuge_at_zero(p) == pytest.approx(0.25)
        assert cr.persists_at_zero_resource(p) is True
        assert cr.persists_at_zero_resource(cr.Params(**self.BASE, S=0.0)) \
            is False

    def test_classification_tracks_the_equations(self):
        import consumer_resource as cr
        assert cr.classify(0.8, 0.1, cr.Params(**self.BASE, S=0.0)
                           )["interaction"] == "predation"
        assert cr.classify(0.8, 0.1, cr.Params(**self.BASE, S=0.05)
                           )["interaction"] == "hyperpredation"
        mined = dict(self.BASE)
        mined["r"] = 0.0
        assert cr.classify(0.8, 0.1, cr.Params(**mined, S=0.05)
                           )["interaction"] == "mining"

    def test_coupled_predator_does_not_exterminate_its_resource(self):
        import consumer_resource as cr
        p = cr.Params(**self.BASE, q=2.0, S=0.0, kind="III")
        out = cr.outcome(cr.simulate(0.9, 0.1, p, t_end=300.0), p)
        assert out["mode"] != "RESOURCE_EXTINCT_CONSUMER_PERSISTS"
        assert out["N_final"] > 0.01

    def test_subsidy_plus_refuge_removal_extinguishes_the_resource(self):
        """The headline result: neither term alone does it."""
        import consumer_resource as cr
        both = cr.Params(**self.BASE, q=1.0, S=0.05, kind="II")
        out = cr.outcome(cr.simulate(0.9, 0.1, both, t_end=300.0), both)
        assert out["mode"] == "RESOURCE_EXTINCT_CONSUMER_PERSISTS"
        assert out["P_final"] > 0.0

    def test_neither_term_alone_extinguishes_the_resource(self):
        import consumer_resource as cr
        subsidy_only = cr.Params(**self.BASE, q=2.0, S=0.05, kind="III")
        refuge_only = cr.Params(**self.BASE, q=1.0, S=0.0, kind="II")
        for p in (subsidy_only, refuge_only):
            out = cr.outcome(cr.simulate(0.9, 0.1, p, t_end=300.0), p)
            assert out["mode"] != "RESOURCE_EXTINCT_CONSUMER_PERSISTS", (
                "single-mechanism run should not exterminate the resource")

    def test_resource_extinct_consumer_persists_is_impossible_unsubsidised(self):
        import consumer_resource as cr
        for q, kind in ((2.0, "III"), (1.0, "II")):
            p = cr.Params(**self.BASE, q=q, S=0.0, kind=kind)
            out = cr.outcome(cr.simulate(0.9, 0.1, p, t_end=400.0), p)
            assert out["mode"] != "RESOURCE_EXTINCT_CONSUMER_PERSISTS"

    def test_integration_conserves_non_negativity(self):
        import consumer_resource as cr
        p = cr.Params(**self.BASE, q=1.0, S=0.3, kind="II")
        traj = cr.simulate(0.9, 0.5, p, t_end=200.0)
        assert min(traj.N) >= 0.0
        assert min(traj.P) >= 0.0


# ═════════════════════════════════════════════════════════════
# DEPENSATION
# ═════════════════════════════════════════════════════════════

class TestDepensation:

    def test_depensatory_per_capita_recruitment_falls_at_low_stock(self):
        import depensation as dp
        assert (dp.per_capita_recruitment(0.05, 1.0, 0.5)
                < dp.per_capita_recruitment(1.0, 1.0, 0.5))

    def test_compensatory_per_capita_recruitment_rises_at_low_stock(self):
        """Compensation is the rebuilding engine; depensation removes it."""
        import depensation as dp
        assert (dp.per_capita_recruitment(0.05, 1.0, 0.5, "compensatory")
                > dp.per_capita_recruitment(1.0, 1.0, 0.5, "compensatory"))

    def test_is_depensatory_detects_the_form_from_behaviour(self):
        import depensation as dp
        assert dp.is_depensatory(1.0, 0.5, "depensatory") is True
        assert dp.is_depensatory(1.0, 0.5, "compensatory") is False

    def test_pit_has_unstable_equilibrium_and_stable_zero(self):
        import depensation as dp
        pit = dp.predator_pit(1.0, 0.5, 1.2, 1.0, 1.0, 0.3,
                              response_kind="II", natural_mortality=0.4,
                              S_max=3.0)
        assert pit["zero_is_stable"] is True
        assert pit["pit_present"] is True
        assert pit["escape_threshold"] > 0.0
        assert pit["upper_state"] > pit["escape_threshold"]

    def test_refuge_removal_raises_the_escape_threshold(self):
        """Removing the refuge does not only lower the stock — it raises
        the biomass you must stay above to keep it."""
        import depensation as dp
        kw = dict(natural_mortality=0.4, S_max=3.0)
        for P in (0.3, 0.5, 0.8):
            with_refuge = dp.predator_pit(1.0, 0.5, 1.2, 1.0, 2.0, P,
                                          response_kind="III", **kw)
            without = dp.predator_pit(1.0, 0.5, 1.2, 1.0, 1.0, P,
                                      response_kind="II", **kw)
            assert without["escape_threshold"] > with_refuge["escape_threshold"]

    def test_high_pressure_without_refuge_leaves_no_viable_state(self):
        import depensation as dp
        pit = dp.predator_pit(1.0, 0.5, 1.2, 1.0, 1.0, 0.8,
                              response_kind="II", natural_mortality=0.5,
                              S_max=3.0)
        assert pit["upper_state"] is None
        assert pit["no_viable_state"] is True

    def test_collapsed_state_is_absorbing(self):
        """Below the escape threshold, removing pressure is not a
        recovery instrument."""
        import depensation as dp
        hy = dp.hysteresis_gap(1.0, 0.5, 1.2, 1.0, 1.0,
                               response_kind="II", natural_mortality=0.4,
                               P_max=2.0, S_max=3.0)
        assert hy["hysteresis"] is True
        assert hy["reversible"] is False
        assert hy["collapse_P"] is not None


# ═════════════════════════════════════════════════════════════
# ENERGY RETURN
# ═════════════════════════════════════════════════════════════

class TestEnergyReturn:

    def test_predator_persistence_is_the_inequality(self):
        import energy_return as er
        assert er.predator_persistence(0.4, 0.8, 0.2)["persists"] is True
        assert er.predator_persistence(0.4, 0.05, 0.2)["persists"] is False

    def test_deficit_equals_required_subsidy_per_consumer(self):
        import energy_return as er
        r = er.predator_persistence(0.4, 0.05, 0.2)
        assert r["deficit"] == pytest.approx(0.2 - 0.4 * 0.05)
        assert er.subsidy_required(0.4, 0.05, 0.2, 10.0) == pytest.approx(
            r["deficit"] * 10.0)

    def test_eroi_below_one_is_an_energy_sink(self):
        import energy_return as er
        assert er.eroi(50.0, 100.0)["energy_sink"] is True
        assert er.eroi(500.0, 100.0)["energy_sink"] is False
        assert er.eroi(500.0, 100.0)["self_supporting"] is True

    def test_fishery_eroi_is_below_one_at_realistic_fuel_intensity(self):
        import energy_return as er
        r = er.fishery_eroi(1000.0, 600_000.0)
        assert r["energy_sink"] is True
        assert r["fuel_L_per_t_landed"] == pytest.approx(600.0)

    def test_ppr_scales_by_ten_per_trophic_level(self):
        import energy_return as er
        tl3 = er.primary_production_required(1.0, 3.0)
        tl4 = er.primary_production_required(1.0, 4.0)
        assert tl4 / tl3 == pytest.approx(10.0, rel=1e-6)

    def test_trophic_transfer_efficiency_compounds(self):
        import energy_return as er
        assert er.trophic_level_energy(3.0) == pytest.approx(0.01)
        assert er.trophic_level_energy(4.0) == pytest.approx(0.001)

    def test_ppr_and_hanpp_are_the_same_intensive_variable(self):
        """Both return a fraction of NPP, which is what makes the marine
        and terrestrial cases addable."""
        import energy_return as er
        sea = er.ppr_fraction(1e6, 3.0, 1e9)
        land = er.hanpp_fraction(2.38e8, 1e9)
        assert 0.0 < sea["PPR_fraction"] < 1.0
        assert land["HANPP_fraction"] == pytest.approx(0.238)

    def test_trophic_level_below_one_is_rejected(self):
        import energy_return as er
        with pytest.raises(ValueError):
            er.primary_production_required(1.0, 0.5)


# ═════════════════════════════════════════════════════════════
# SURPLUS PRODUCTION
# ═════════════════════════════════════════════════════════════

class TestSurplusProduction:

    R, K = 0.4, 100_000.0

    def test_schaefer_reference_points(self):
        import surplus_production as sp
        rp = sp.reference_points(self.R, self.K)
        assert rp["B_MSY"] == pytest.approx(self.K / 2)
        assert rp["F_MSY"] == pytest.approx(self.R / 2)
        assert rp["MSY"] == pytest.approx(self.R * self.K / 4)

    def test_production_peaks_at_B_MSY(self):
        import surplus_production as sp
        peak = sp.surplus_production(self.K / 2, self.R, self.K)
        for B in (0.2 * self.K, 0.4 * self.K, 0.7 * self.K, 0.9 * self.K):
            assert sp.surplus_production(B, self.R, self.K) <= peak + 1e-6

    def test_pella_tomlinson_shifts_B_MSY_off_half_K(self):
        import surplus_production as sp
        low = sp.reference_points(self.R, self.K, p=0.4)
        high = sp.reference_points(self.R, self.K, p=2.0)
        assert low["B_MSY_over_B_0"] < 0.5 < high["B_MSY_over_B_0"]

    def test_rate_and_state_are_independent(self):
        """Same biomass, different fishing mortality — one rebuilding,
        one not. A single index cannot say which."""
        import surplus_production as sp
        rebuilding = sp.stock_status(20_000, 1_000, self.R, self.K)
        still_going = sp.stock_status(20_000, 5_000, self.R, self.K)
        assert rebuilding["B_over_B_MSY"] == still_going["B_over_B_MSY"]
        assert rebuilding["overfished"] is still_going["overfished"] is True
        assert rebuilding["overfishing"] is False
        assert still_going["overfishing"] is True
        assert rebuilding["quadrant"] != still_going["quadrant"]

    def test_all_four_kobe_quadrants_are_reachable(self):
        import surplus_production as sp
        quadrants = {
            sp.stock_status(B, Y, self.R, self.K)["quadrant"]
            for B, Y in ((80_000, 8_000), (50_000, 15_000),
                         (20_000, 5_000), (20_000, 1_000))
        }
        assert quadrants == {
            "HEALTHY", "OVERFISHING_NOT_YET_OVERFISHED",
            "OVERFISHED_AND_OVERFISHING", "OVERFISHED_REBUILDING"}

    def test_depletion_ratio_is_comparable_across_stocks(self):
        import surplus_production as sp
        small = sp.stock_status(500, 10, 0.4, 1_000)
        large = sp.stock_status(50_000, 1_000, 0.4, 100_000)
        assert small["B_over_B_0"] == pytest.approx(large["B_over_B_0"])

    def test_constant_yield_above_MSY_walks_the_stock_down(self):
        import surplus_production as sp
        rp = sp.reference_points(self.R, self.K)
        path = sp.project(rp["B_MSY"], self.R, self.K,
                          [rp["MSY"] * 1.05] * 15)
        assert path[-1]["B"] < path[0]["B"]
        assert path[-1]["F_over_F_MSY"] > path[0]["F_over_F_MSY"]

    def test_error_at_B_MSY_is_all_downside(self):
        import surplus_production as sp
        m = sp.msy_is_a_ceiling_not_a_target(self.K / 2, self.R, self.K)
        assert m["error_is_all_downside_at_B_MSY"] is True


# ═════════════════════════════════════════════════════════════
# SOIL CARBON
# ═════════════════════════════════════════════════════════════

class TestSoilCarbon:

    def test_hassink_relation(self):
        import soil_carbon as sc
        assert sc.saturation_capacity_gC_kg(0.0) == pytest.approx(4.09)
        assert sc.saturation_capacity_gC_kg(50.0) == pytest.approx(
            4.09 + 0.37 * 50.0)

    def test_capacity_rises_with_fine_fraction(self):
        import soil_carbon as sc
        assert (sc.saturation_capacity_pct(60.0)
                > sc.saturation_capacity_pct(10.0))

    def test_same_SOC_is_a_different_verdict_on_different_soils(self):
        """Why a fixed percentage floor is not physics."""
        import soil_carbon as sc
        sandy = sc.saturation_deficit(2.0, 5.0)
        clay = sc.saturation_deficit(2.0, 70.0)
        assert sandy["supersaturated"] is True
        assert clay["supersaturated"] is False
        assert clay["saturation_deficit"] > 0.0

    def test_deficit_is_dimensionless_and_bounded_above(self):
        import soil_carbon as sc
        d = sc.saturation_deficit(0.0, 40.0)
        assert d["saturation_deficit"] == pytest.approx(1.0)

    def test_stock_conversion(self):
        import soil_carbon as sc
        assert sc.soc_stock_t_ha(2.0, 1.3, 30.0) == pytest.approx(78.0)

    def test_steady_state_is_set_by_the_inputs(self):
        import soil_carbon as sc
        low = sc.steady_state_SOC_pct(2.0)
        high = sc.steady_state_SOC_pct(8.0)
        assert high == pytest.approx(4 * low)

    def test_defaults_are_consistent_across_functions(self):
        """dSOC_dt and steady_state_SOC_pct must agree, or a projection
        and its asymptote come from different models."""
        import soil_carbon as sc
        assert sc.dSOC_dt(1.0, 5.0)["steady_state_pct"] == pytest.approx(
            sc.steady_state_SOC_pct(5.0))

    def test_steady_state_is_a_fixed_point(self):
        import soil_carbon as sc
        star = sc.steady_state_SOC_pct(6.0)
        assert sc.dSOC_dt(star, 6.0)["dSOC_t_ha_yr"] == pytest.approx(
            0.0, abs=1e-9)

    def test_C_input_required_inverts_steady_state(self):
        import soil_carbon as sc
        need = sc.C_input_required(2.0)
        assert sc.steady_state_SOC_pct(need) == pytest.approx(2.0)

    def test_extraction_test_is_removal_versus_humified_input(self):
        import soil_carbon as sc
        assert sc.extraction_check(0.2, 4.0)["extracting"] is False
        assert sc.extraction_check(0.9, 1.2)["extracting"] is True
        assert sc.extraction_check(0.9, 1.2)["interaction"] == "mining"

    def test_target_beyond_steady_state_is_unreachable_not_slow(self):
        """The failure mode is a promised timeline for a target the
        inputs cannot support."""
        import soil_carbon as sc
        t = sc.time_to_target(1.2, 2.0, 4.0)
        assert t["reachable"] is False
        assert t["years"] is None
        t2 = sc.time_to_target(1.2, 2.0, 12.0)
        assert t2["reachable"] is True
        assert t2["years"] > 0


# ═════════════════════════════════════════════════════════════
# DOMAIN MAPPING AND ITS REFUSALS
# ═════════════════════════════════════════════════════════════

class TestDomainMapping:

    def test_mapped_domains_have_all_five_elements(self):
        import domain_mapping as dm
        for m in dm.MAPPINGS.values():
            for field in (m.stock, m.recruitment, m.consumption,
                          m.capacity, m.subsidy, m.measurement):
                assert isinstance(field, str) and len(field) > 5

    def test_fossil_stocks_are_classified_as_mining(self):
        import domain_mapping as dm
        assert dm.get_mapping("phosphate_rock").typical_class == "mining"
        assert dm.get_mapping("fossil_hydrocarbon").typical_class == "mining"
        assert dm.get_mapping("groundwater_fossil").typical_class == "mining"

    def test_recharging_and_fossil_groundwater_map_differently(self):
        """Same physical substance, different interaction class, because
        the recruitment term differs."""
        import domain_mapping as dm
        assert dm.get_mapping("groundwater_recharging").typical_class \
            == "hyperpredation"
        assert dm.get_mapping("groundwater_fossil").typical_class == "mining"

    def test_refused_domains_name_the_missing_requirement(self):
        import domain_mapping as dm
        for name, reason in dm.REFUSED_MAPPINGS.items():
            assert "Fails" in reason, f"{name} refusal states no requirement"

    def test_refused_domain_raises_with_its_reason(self):
        import domain_mapping as dm
        with pytest.raises(ValueError) as exc:
            dm.get_mapping("consciousness")
        assert "refusal list" in str(exc.value)

    def test_is_refused_reports_cleanly(self):
        import domain_mapping as dm
        refused, reason = dm.is_refused("art")
        assert refused is True and reason
        assert dm.is_refused("wild_fishery") == (False, None)

    def test_requirements_check_names_what_is_missing(self):
        import domain_mapping as dm
        ok = dm.requirements_met(True, True, True, True, True)
        assert ok["mappable"] is True and ok["failed"] == []
        bad = dm.requirements_met(False, True, True, False, True)
        assert bad["mappable"] is False
        assert "1_stock_has_unit" in bad["failed"]
        assert "4_capacity_derivable" in bad["failed"]

    def test_mapped_and_refused_sets_are_disjoint(self):
        import domain_mapping as dm
        d = dm.list_domains()
        assert set(d["mapped"]).isdisjoint(set(d["refused"]))


# ═════════════════════════════════════════════════════════════
# THE AUDIT RUNNER
# ═════════════════════════════════════════════════════════════

class TestAudit:

    BASE = dict(r=0.5, K=1.0, a=2.0, h=1.0, e=0.45, m=0.2)

    def _system(self, name, q, S, kind, **kw):
        import audit as ad
        import consumer_resource as cr
        return ad.System(name, N=0.8, P=0.1,
                         params=cr.Params(**self.BASE, q=q, S=S, kind=kind),
                         alpha=1.0, beta=0.5, natural_mortality=0.4, **kw)

    def test_ecological_predator_is_coupled_and_refuged(self):
        import audit as ad
        r = ad.audit(self._system("predator", 2.0, 0.0, "III"))
        assert r["verdict"]["headline"] == "COUPLED_AND_REFUGED"
        assert r["classification"]["interaction"] == "predation"

    def test_subsidised_and_unrefuged_is_flagged(self):
        import audit as ad
        r = ad.audit(self._system("fleet", 1.0, 0.05, "II"))
        assert r["verdict"]["headline"] == "UNCOUPLED_AND_UNREFUGED"
        assert r["verdict"]["consumer_uncoupled"] is True
        assert r["verdict"]["refuge_removed"] is True
        assert r["projection"]["mode"] == "RESOURCE_EXTINCT_CONSUMER_PERSISTS"

    def test_the_two_brakes_are_reported_separately(self):
        import audit as ad
        subsidy_only = ad.audit(self._system("subsidy only", 2.0, 0.05, "III"))
        refuge_only = ad.audit(self._system("refuge only", 1.0, 0.0, "II"))
        assert subsidy_only["verdict"]["headline"] == "UNCOUPLED_REFUGE_INTACT"
        assert refuge_only["verdict"]["headline"] == "COUPLED_REFUGE_REMOVED"

    def test_audit_reports_an_escape_threshold_in_biomass(self):
        import audit as ad
        r = ad.audit(self._system("fleet", 1.0, 0.05, "II"))
        assert r["verdict"]["escape_threshold"] > 0.0

    def test_pit_analysis_is_skipped_not_guessed_without_a_curve(self):
        import audit as ad
        import consumer_resource as cr
        s = ad.System("no recruitment curve", N=0.8, P=0.1,
                      params=cr.Params(**self.BASE, q=1.0, S=0.05, kind="II"))
        r = ad.audit(s)
        assert r["pit"]["pit_present"] is None
        assert "skipped" in r["pit"]["note"]

    def test_unmeasured_inputs_are_flagged_in_provenance(self):
        import audit as ad
        assumed = ad.audit(self._system("assumed", 1.0, 0.05, "II"))
        measured = ad.audit(self._system("measured", 1.0, 0.05, "II",
                                         stock_measured=True,
                                         subsidy_measured=True))
        assert assumed["provenance"]["warning"] is not None
        assert measured["provenance"]["warning"] is None

    def test_every_audit_ships_falsifiers(self):
        import audit as ad
        r = ad.audit(self._system("fleet", 1.0, 0.05, "II"))
        assert len(r["falsifiers"]) >= 4
        for f in r["falsifiers"]:
            assert f["claim"] and f["falsified_by"] and f["statistic"]

    def test_compare_returns_one_row_per_system(self):
        import audit as ad
        rows = ad.compare([self._system("a", 2.0, 0.0, "III"),
                           self._system("b", 1.0, 0.05, "II")])
        assert len(rows) == 2
        assert rows[0]["interaction"] == "predation"
        assert rows[1]["interaction"] == "hyperpredation"


class TestModulesRunStandalone:
    """Every module's __main__ demo must execute without error — the
    demos are the documentation."""

    @pytest.mark.parametrize("module", _MODULES)
    def test_module_executes(self, module):
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(ED_DIR, module + ".py")],
            capture_output=True, text=True, cwd=ED_DIR, timeout=180)
        assert result.returncode == 0, (
            f"{module}.py failed:\n{result.stderr[-2000:]}")
        assert result.stdout.strip(), f"{module}.py printed nothing"
