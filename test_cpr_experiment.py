# test_cpr_experiment.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Tests for experiments/cpr_composition/. The folder uses bare
# intra-folder imports, so sys.path is adjusted the same way the
# boundary_waters and extraction_dynamics tests do.

import ast
import math
import os
import sys

import pytest

CPR_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "experiments", "cpr_composition"))

_MODULES = ("cpr_game", "parameter_sweep", "design", "analysis_plan")


@pytest.fixture(autouse=True)
def _cpr_path():
    if CPR_DIR not in sys.path:
        sys.path.insert(0, CPR_DIR)
    yield
    if CPR_DIR in sys.path:
        sys.path.remove(CPR_DIR)
    for m in _MODULES:
        sys.modules.pop(m, None)


# ═════════════════════════════════════════════════════════════
# GAME ENGINE
# ═════════════════════════════════════════════════════════════

class TestCPRGame:

    def test_regeneration_is_the_logistic_map(self):
        from cpr_game import regenerate
        assert regenerate(50.0, 0.4, 100.0) == pytest.approx(60.0)
        assert regenerate(100.0, 0.4, 100.0) == pytest.approx(100.0)
        assert regenerate(0.0, 0.4, 100.0) == 0.0

    def test_regeneration_is_capped_at_K(self):
        from cpr_game import regenerate
        assert regenerate(99.0, 2.0, 100.0) <= 100.0

    def test_zero_is_absorbing(self):
        from cpr_game import GameParams, step
        S, taken, collapsed = step(0.0, [1, 1, 1, 1], GameParams())
        assert S == 0.0 and collapsed is True and taken == [0, 0, 0, 0]

    def test_rationing_conserves_the_stock(self):
        """int() truncation destroys tokens the stock could have
        supplied; largest remainder keeps the accounting closed."""
        from cpr_game import ration
        for requests, S in (([8, 8, 8, 8], 30), ([5, 3, 7, 1], 10),
                            ([1, 1, 1, 1], 3), ([8, 0, 0, 1], 5)):
            taken = ration(requests, S)
            assert sum(taken) == int(S), (requests, S, taken)

    def test_rationing_is_proportional_and_never_exceeds_request(self):
        from cpr_game import ration
        taken = ration([8, 4, 2, 2], 8)
        assert sum(taken) == 8
        assert taken[0] >= taken[1] >= taken[2]
        for t, r in zip(taken, [8, 4, 2, 2]):
            assert t <= r

    def test_rationing_below_demand_returns_requests_unchanged(self):
        from cpr_game import ration
        assert ration([2, 2, 2, 2], 50) == [2, 2, 2, 2]

    def test_sustainable_total_is_an_exact_fixed_point(self):
        """Taking exactly this much leaves the stock unchanged — that is
        what makes it sustainable rather than merely modest."""
        from cpr_game import regenerate, sustainable_total
        for S in (20.0, 35.0, 50.0, 70.0, 90.0):
            take = sustainable_total(S, 0.4, 100.0)
            assert regenerate(S - take, 0.4, 100.0) == pytest.approx(S,
                                                                     abs=1e-9)

    def test_msy_is_the_peak_of_the_sustainable_curve(self):
        from cpr_game import msy_total, sustainable_total
        peak = max(sustainable_total(S, 0.4, 100.0)
                   for S in [i * 0.5 for i in range(1, 200)])
        assert peak == pytest.approx(msy_total(0.4, 100.0), rel=0.02)

    def test_naive_split_collapses_the_stock_where_the_cap_does_not_bind(self):
        """The bug in the draft comparison arm, asserted so it cannot
        come back. Below S = N*cap, S/N each requests the whole stock."""
        from cpr_game import GameParams, step
        p = GameParams()
        for S in (12.0, 20.0, 32.0):          # all <= N*cap = 32
            naive = [min(int(S / p.N), p.cap)] * p.N
            _, _, collapsed = step(S, naive, p)
            assert collapsed is True, f"S={S} naive={naive}"

    def test_naive_split_is_all_max_where_the_cap_binds(self):
        """Above S = N*cap it degenerates to the maximum request, so the
        'sustainable' arm and the 'all-max' arm are the same arm."""
        from cpr_game import GameParams, policy_all_max
        p = GameParams()
        for S in (50.0, 90.0):                # all > N*cap = 32
            naive = [min(int(S / p.N), p.cap)] * p.N
            assert naive == policy_all_max(S, p)

    def test_sustainable_policy_is_not_identical_to_all_max(self):
        from cpr_game import GameParams, policy_all_max, policy_sustainable
        p = GameParams()
        assert policy_sustainable(50.0, p) != policy_all_max(50.0, p)

    def test_all_max_collapses_and_sustainable_does_not(self):
        from cpr_game import GameParams, simulate
        p = GameParams(g=0.4)
        assert simulate(p, policy="all_max").collapsed is True
        assert simulate(p, policy="sustainable").collapsed is False

    def test_restraint_yields_more_tokens_than_maximisation(self):
        from cpr_game import GameParams, simulate
        p = GameParams(g=0.4)
        assert (simulate(p, policy="sustainable").total_extracted
                > simulate(p, policy="all_max").total_extracted)

    def test_collapse_is_recorded_with_its_round(self):
        from cpr_game import GameParams, simulate
        r = simulate(GameParams(g=0.4), policy="all_max")
        assert r.rounds_to_collapse is not None
        assert r.final_stock == 0.0

    def test_survivors_are_censored_not_treated_as_collapsing_at_T(self):
        from cpr_game import GameParams, simulate
        s = simulate(GameParams(g=0.4), policy="sustainable").summary()
        assert s["event_observed"] is False
        assert s["duration"] == GameParams().T

    def test_composition_baseline_is_monotone_non_increasing(self):
        from cpr_game import GameParams, simulate
        p = GameParams(g=0.4)
        finals = [simulate(p, policy="mixed", n_max=k).summary()["final_stock"]
                  for k in range(p.N + 1)]
        assert all(finals[i] >= finals[i + 1] for i in range(len(finals) - 1))

    def test_gini_bounds(self):
        from cpr_game import gini
        assert gini([5, 5, 5, 5]) == pytest.approx(0.0)
        assert gini([0, 0, 0, 0]) == 0.0
        assert gini([20, 0, 0, 0]) > 0.5

    def test_subsidy_ratio_reports_the_show_up_fee_as_uncoupled(self):
        from cpr_game import GameParams, subsidy_ratio
        r = subsidy_ratio(GameParams(), 20)
        assert 0.0 < r["coupling_index"] < 1.0
        assert r["subsidy_share"] == pytest.approx(1 - r["coupling_index"])

    def test_unknown_policy_raises(self):
        from cpr_game import GameParams, simulate
        with pytest.raises(ValueError):
            simulate(GameParams(), policy="vibes")


# ═════════════════════════════════════════════════════════════
# PARAMETER SWEEP — THE PILOT INSTRUMENT
# ═════════════════════════════════════════════════════════════

class TestParameterSweep:

    def test_sweep_returns_one_row_per_g(self):
        from parameter_sweep import linspace, sweep_g
        rows = sweep_g(linspace(0.2, 0.6, 9))
        assert len(rows) == 9
        assert all("payoff_ratio" in r for r in rows)

    def test_design_window_is_found_at_default_parameters(self):
        from parameter_sweep import find_design_window, linspace, sweep_g
        win = find_design_window(sweep_g(linspace(0.2, 0.6, 9)))
        assert win["window_found"] is True
        assert win["g_min"] <= win["recommended_g"] <= win["g_max"]

    def test_window_is_refused_when_regeneration_cannot_collapse(self):
        """High g plus a low cap: no group can overshoot, so the design
        has no dependent variable and the sweep must say so."""
        from cpr_game import GameParams
        from parameter_sweep import find_design_window, sweep_g
        rows = sweep_g([1.2, 1.4], GameParams(cap=1, S0=90.0))
        assert find_design_window(rows)["window_found"] is False

    def test_mechanical_slope_is_near_the_preregistered_SESOI(self):
        """The finding that forced the null to change: arithmetic alone
        produces roughly the effect size H2 declared as its SESOI."""
        from parameter_sweep import composition_slope, linspace, sweep_g
        rows = sweep_g(linspace(0.2, 0.6, 9))
        for g in (0.3, 0.4, 0.5):
            cs = composition_slope(rows, g)
            assert -0.30 < cs["mechanical_slope"] < -0.15

    def test_mechanical_curve_is_detected_as_a_step(self):
        from parameter_sweep import composition_slope, linspace, sweep_g
        cs = composition_slope(sweep_g(linspace(0.2, 0.6, 9)), 0.4)
        assert cs["is_step_not_line"] is True

    def test_individual_defection_incentive_exists(self):
        """Group totals favour restraint; the defector still gains. Only
        the second comparison makes it a dilemma."""
        from cpr_game import GameParams
        from parameter_sweep import defection_incentive
        d = defection_incentive(GameParams(g=0.4))
        assert d["dilemma_present"] is True
        assert d["defector_tokens"] > d["tokens_if_all_comply"]

    def test_plot_is_optional_and_never_raises(self):
        from parameter_sweep import linspace, plot_sweep, sweep_g
        import tempfile
        rows = sweep_g(linspace(0.2, 0.4, 3))
        with tempfile.TemporaryDirectory() as d:
            result = plot_sweep(rows, os.path.join(d, "s.png"))
        assert result is None or result.endswith(".png")


# ═════════════════════════════════════════════════════════════
# DESIGN — POOL ARITHMETIC, POWER, RANDOMISATION
# ═════════════════════════════════════════════════════════════

class TestDesignArithmetic:

    def test_screening_pool_is_set_by_high_D_supply(self):
        from design import screening_pool_required
        r = screening_pool_required(80)
        assert r["total_groups"] == 240
        assert r["participants"] == 960
        assert r["high_d_share_required"] == pytest.approx(0.5)
        assert r["binding_constraint"] == "high-D supply"
        assert r["screening_multiple"] == pytest.approx(1.5)

    def test_unbalanceable_design_is_refused(self):
        from design import screening_pool_required
        with pytest.raises(ValueError):
            screening_pool_required(19)

    def test_draft_participant_count_was_inconsistent(self):
        """240 groups of 4 is 960 participants, not 720."""
        from design import screening_pool_required
        assert screening_pool_required(80)["participants"] != 720

    def test_power_rises_with_n_and_effect_size(self):
        from design import power_ols
        assert power_ols(0.20, 240)["power"] > power_ols(0.20, 120)["power"]
        assert power_ols(0.30, 240)["power"] > power_ols(0.20, 240)["power"]

    def test_240_groups_reaches_80pct_power_and_180_does_not(self):
        from design import power_ols, required_n
        assert power_ols(0.20, 240)["power"] > 0.80
        assert power_ols(0.20, 180)["power"] < 0.80
        assert 180 < required_n(0.20, 0.80) < 240


class TestComposite:

    def _sample(self, n=600, loading=0.5, seed=3):
        import random
        rng = random.Random(seed)
        a = [rng.gauss(0, 1) for _ in range(n)]
        b = [loading * x + rng.gauss(0, 1) for x in a]
        c = [loading * x + rng.gauss(0, 1) for x in a]
        return a, b, c

    def test_zscores_have_zero_mean(self):
        from design import zscores
        z = zscores([1.0, 2.0, 3.0, 4.0])
        assert sum(z) == pytest.approx(0.0, abs=1e-9)

    def test_constant_vector_gives_zero_zscores(self):
        from design import zscores
        assert zscores([5.0] * 10) == [0.0] * 10

    def test_coherent_composite_is_accepted(self):
        from design import composite_coherence
        a, b, c = self._sample(loading=0.6)
        r = composite_coherence(a, b, c)
        assert r["coherent"] is True
        assert r["mean_r"] > 0.2

    def test_incoherent_composite_is_flagged_with_a_fallback(self):
        """The pre-registered check that keeps the composite from being
        an average of unrelated things."""
        from design import composite_coherence
        a, b, c = self._sample(loading=0.0)
        r = composite_coherence(a, b, c)
        assert r["coherent"] is False
        assert "separate predictors" in r["recommendation"]

    def test_high_d_split_is_exactly_the_intended_fraction(self):
        from design import composite_score, high_d_flags
        a, b, c = self._sample(n=900)
        flags = high_d_flags(composite_score(a, b, c))
        assert sum(flags) == 300

    def test_split_is_exact_even_with_ties(self):
        from design import high_d_flags
        flags = high_d_flags([1.0] * 90)
        assert sum(flags) == 30


class TestRandomisation:

    def _pool(self, n_high=600, n_low=1200):
        ids = [f"P{i:05d}" for i in range(n_high + n_low)]
        flags = [True] * n_high + [False] * n_low
        return ids, flags

    def test_assignment_is_balanced(self):
        from design import assign_groups, assignment_balance
        ids, flags = self._pool()
        a = assign_groups(ids, flags, groups_per_arm=80, seed=2026)
        bal = assignment_balance(a)
        assert bal["n_groups"] == 240
        assert bal["n_participants"] == 960
        assert bal["balanced"] is True

    def test_no_participant_appears_in_two_groups(self):
        """The draft's modulo fallback could place one person in two
        groups, and its only assertion checked within-group duplicates."""
        from design import assign_groups
        ids, flags = self._pool()
        a = assign_groups(ids, flags, groups_per_arm=80, seed=11)
        members = [m for g in a for m in g.members]
        assert len(members) == len(set(members))

    def test_composition_matches_the_spec_for_every_group(self):
        from design import assign_groups
        ids, flags = self._pool()
        high = {pid for pid, f in zip(ids, flags) if f}
        for g in assign_groups(ids, flags, groups_per_arm=40, seed=5):
            assert sum(1 for m in g.members if m in high) == g.n_high_d

    def test_same_seed_gives_the_same_assignment(self):
        from design import assign_groups
        ids, flags = self._pool()
        a = assign_groups(ids, flags, groups_per_arm=20, seed=99)
        b = assign_groups(ids, flags, groups_per_arm=20, seed=99)
        assert [g.members for g in a] == [g.members for g in b]

    def test_different_seed_gives_a_different_assignment(self):
        from design import assign_groups
        ids, flags = self._pool()
        a = assign_groups(ids, flags, groups_per_arm=20, seed=1)
        b = assign_groups(ids, flags, groups_per_arm=20, seed=2)
        assert [g.members for g in a] != [g.members for g in b]

    def test_insufficient_pool_raises_instead_of_reusing_people(self):
        from design import assign_groups
        ids, flags = self._pool(n_high=10, n_low=10)
        with pytest.raises(ValueError) as exc:
            assign_groups(ids, flags, groups_per_arm=20, seed=1)
        assert "reusing participants" in str(exc.value)

    def test_unbalanceable_groups_per_arm_raises(self):
        from design import assign_groups
        ids, flags = self._pool()
        with pytest.raises(ValueError):
            assign_groups(ids, flags, groups_per_arm=7, seed=1)


# ═════════════════════════════════════════════════════════════
# ANALYSIS PLAN
# ═════════════════════════════════════════════════════════════

class TestOLS:

    def test_recovers_a_known_slope(self):
        from analysis_plan import ols
        x = [float(i) for i in range(50)]
        y = [3.0 + 2.0 * xi for xi in x]
        fit = ols(y, [[xi] for xi in x], ["x"])
        assert fit.coef[0] == pytest.approx(3.0, abs=1e-6)
        assert fit.coef[1] == pytest.approx(2.0, abs=1e-6)
        assert fit.r_squared == pytest.approx(1.0, abs=1e-9)

    def test_recovers_multiple_slopes(self):
        from analysis_plan import ols
        rows, y = [], []
        for i in range(60):
            a, b = i % 7, (i * 3) % 5
            rows.append([float(a), float(b)])
            y.append(1.0 + 2.0 * a - 3.0 * b)
        fit = ols(y, rows, ["a", "b"])
        assert fit.coef[1] == pytest.approx(2.0, abs=1e-6)
        assert fit.coef[2] == pytest.approx(-3.0, abs=1e-6)

    def test_singular_design_raises(self):
        from analysis_plan import ols
        with pytest.raises(ValueError):
            ols([1.0] * 10, [[1.0, 1.0]] * 10, ["a", "b"])

    def test_standardize_gives_unit_sd(self):
        from analysis_plan import standardize
        z = standardize([2.0, 4.0, 6.0, 8.0, 10.0])
        n = len(z)
        mean = sum(z) / n
        sd = math.sqrt(sum((v - mean) ** 2 for v in z) / (n - 1))
        assert mean == pytest.approx(0.0, abs=1e-9)
        assert sd == pytest.approx(1.0, abs=1e-9)


class TestEquivalence:

    def test_equivalent_when_ci_inside_the_band(self):
        from analysis_plan import equivalence_test
        r = equivalence_test(0.02, 0.05, sesoi=0.20, null=0.0)
        assert r["verdict"] == "EQUIVALENT"

    def test_larger_negative_when_ci_below_the_band(self):
        from analysis_plan import equivalence_test
        assert equivalence_test(-0.60, 0.05)["verdict"] == "LARGER_NEGATIVE"

    def test_wrong_sign_is_a_distinct_verdict(self):
        from analysis_plan import equivalence_test
        assert equivalence_test(0.60, 0.05)["verdict"] == "LARGER_POSITIVE"

    def test_wide_interval_is_inconclusive_not_null(self):
        from analysis_plan import equivalence_test
        r = equivalence_test(-0.10, 0.30)
        assert r["verdict"] == "INCONCLUSIVE"
        assert "power statement" in r["reading"]

    def test_the_null_changes_the_verdict(self):
        """The correction that mattered: the same coefficient is
        'supported' against zero and 'equivalent' against the
        mechanical baseline."""
        from analysis_plan import equivalence_test
        beta, se = -0.86, 0.033
        assert equivalence_test(beta, se, null=0.0)["verdict"] \
            == "LARGER_NEGATIVE"
        assert equivalence_test(beta, se, null=-0.86)["verdict"] \
            == "EQUIVALENT"

    def test_standardized_baseline_converts_units(self):
        """A raw-units slope and a standardised coefficient are not
        comparable until one is converted."""
        from analysis_plan import standardized_baseline
        x = [0.0, 1.0, 2.0, 3.0, 4.0] * 20
        y = [0.8 - 0.2 * xi for xi in x]
        r = standardized_baseline(-0.2, x, y)
        assert r["beta_std"] == pytest.approx(-1.0, abs=1e-6)
        assert r["beta_std"] != r["slope_raw"]


class TestPrimaryAnalysis:

    def _rows(self, n=240, slope=-0.2, noise=0.05, seed=17):
        """Noiseless data gives se=0 and a degenerate CI, which is a
        property of perfect data rather than of the estimator."""
        import random
        rng = random.Random(seed)
        rows = []
        for i in range(n):
            k = i % 5
            rows.append({
                "governance": ("G0", "G1", "G2")[i % 3],
                "n_high_d": k,
                "S_final_over_K": max(0.0, 0.8 + slope * k
                                      + rng.gauss(0, noise)),
                "comprehension": 0.5 + (i % 7) / 14.0,
            })
        return rows

    def test_primary_returns_a_standardised_slope_with_ci(self):
        from analysis_plan import primary_analysis
        res = primary_analysis(self._rows())
        assert res["ci90"][0] < res["beta"] < res["ci90"][1]
        assert res["ci95"][0] < res["ci90"][0]

    def test_governance_dummies_are_the_H1_contrasts(self):
        from analysis_plan import primary_analysis
        res = primary_analysis(self._rows())
        assert set(res["governance_contrasts"]) == {"arm_G1", "arm_G2"}

    def test_negative_composition_effect_is_recovered(self):
        from analysis_plan import primary_analysis
        assert primary_analysis(self._rows(slope=-0.2))["beta"] < -0.5

    def test_threshold_beats_linear_on_step_shaped_data(self):
        from analysis_plan import threshold_specification
        rows = [{"n_high_d": k, "S_final_over_K": 0.8 if k < 2 else 0.0}
                for k in range(5) for _ in range(40)]
        th = threshold_specification(rows)
        assert th["threshold_beats_linear"] is True
        assert th["best_threshold"]["cut"] == 2
        assert "not a p-value" in th["caveat"]

    def test_optional_dependencies_are_skipped_not_fatal(self):
        from analysis_plan import round_level_model, survival_analysis
        for fn, arg in ((survival_analysis, self._rows()),
                        (round_level_model, [])):
            out = fn(arg)
            assert "skipped" in out or "summary" in out


# ═════════════════════════════════════════════════════════════
# THE oTREE APP — SYNTAX AND AGREEMENT WITH THE REFERENCE ENGINE
# ═════════════════════════════════════════════════════════════

class TestOTreeApp:
    """oTree is not installed and is not a dependency; the app is
    checked structurally and its arithmetic is checked against
    cpr_game.py, which is the reference implementation."""

    APP = os.path.join(CPR_DIR, "otree_app", "__init__.py")

    def _tree(self):
        with open(self.APP, encoding="utf-8") as f:
            return ast.parse(f.read()), f

    def test_app_parses(self):
        with open(self.APP, encoding="utf-8") as f:
            ast.parse(f.read())

    def test_extraction_is_resolved_after_the_decision_page(self):
        """The draft resolved the round on a wait page BEFORE the
        decision page, so it read unset requests every round."""
        with open(self.APP, encoding="utf-8") as f:
            src = f.read()
        start = src.index("page_sequence")
        seq = src[start:]
        assert seq.index("Decision") < seq.index("ResolveWaitPage")
        assert seq.index("SetStockWaitPage") < seq.index("Decision")

    def test_comprehension_page_does_not_reuse_the_decision_field(self):
        with open(self.APP, encoding="utf-8") as f:
            src = f.read()
        comp = src[src.index("class Comprehension"):
                   src.index("class Chat")]
        assert "comp_regen" in comp
        assert "'request'" not in comp

    def test_rationing_matches_the_reference_implementation(self):
        """Two implementations of the same arithmetic must not drift."""
        import cpr_game
        with open(self.APP, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        ns: dict = {}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "ration":
                exec(compile(ast.Module(body=[node], type_ignores=[]),
                             "<otree>", "exec"), ns)
        assert "ration" in ns, "otree app has no ration() to compare"
        for requests, S in (([8, 8, 8, 8], 30), ([5, 3, 7, 1], 10),
                            ([2, 2, 2, 2], 50), ([8, 0, 0, 1], 5)):
            assert ns["ration"](requests, S) == cpr_game.ration(requests, S)


class TestModulesRunStandalone:
    """The demos are the documentation; they must execute."""

    @pytest.mark.parametrize("module", _MODULES)
    def test_module_executes(self, module):
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(CPR_DIR, module + ".py")],
            capture_output=True, text=True, cwd=CPR_DIR, timeout=300)
        assert result.returncode == 0, (
            f"{module}.py failed:\n{result.stderr[-2000:]}")
        assert result.stdout.strip()
