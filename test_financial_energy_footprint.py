# test_financial_energy_footprint.py
# earth-systems-physics
# CC0 -- No Rights Reserved
"""
Tests for financial_energy_footprint.py. stdlib only; runs under pytest or
directly (python test_financial_energy_footprint.py prints a count).

Fixtures marked CONSTRUCTED are authored here with known answers. A pass on
them is a regression result about the arithmetic, not evidence about any
financial system.
"""

import ast
import io
import os
import re
import subprocess
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import dollar_energy_metabolism as dem
import financial_energy_footprint as fef

SRC_PATH = os.path.join(HERE, "financial_energy_footprint.py")
with open(SRC_PATH) as _f:
    SRC = _f.read()

ORDER_CHAIN = {"financial_software_developers", "security_engineering",
               "settlement_rails", "exchanges", "transaction_chip_fab",
               "hft_colocation", "compliance_stack"}


def _m(name, lo, hi, group="metabolism"):
    """CONSTRUCTED measured layer."""
    return fef.Layer(name, group, fef.RRange(lo, hi, fef.MEASURED,
                                             "CONSTRUCTED fixture"), "test")


def _u(name, group="chain"):
    return fef.Layer(name, group, fef.RRange(None, None, fef.UNMEASURED,
                                             "CONSTRUCTED fixture"), "test")


def _near(a, b, tol=1e-12):
    return abs(a - b) <= tol


# ---------------------------------------------------------------- referent

def test_referent_exact():
    r = fef.flow_rate_referent(10.0, 3.0, 2.0, 5.0)
    assert r["bound"] == fef.EXACT and _near(r["M"], 1.0)


def test_referent_hidden_none_is_upper_bound_not_zero():
    r = fef.flow_rate_referent(10.0, 3.0, None, 5.0)
    assert r["bound"] == fef.UPPER_BOUND and _near(r["M"], 1.4)
    z = fef.flow_rate_referent(10.0, 3.0, 0.0, 5.0)
    assert z["bound"] == fef.EXACT     # measured zero is not None


def test_referent_not_computable():
    assert fef.flow_rate_referent(None, 1.0, 1.0, 1.0)["M"] is None
    assert fef.flow_rate_referent(1.0, None, 1.0, 1.0)["bound"] == fef.NOT_COMPUTABLE
    assert fef.flow_rate_referent(1.0, 1.0, 1.0, 0.0)["bound"] == fef.NOT_COMPUTABLE
    assert fef.flow_rate_referent(1.0, 1.0, 1.0, None)["bound"] == fef.NOT_COMPUTABLE


# ---------------------------------------------------------------- multiplier

def test_multiplier_known_answers():
    assert _near(fef.multiplier(0.0), 1.0)
    assert _near(fef.multiplier(0.5), 2.0)
    assert _near(fef.multiplier(0.75), 4.0)
    assert fef.multiplier(1.0) == fef.DIVERGENT
    assert fef.multiplier(1.4) == fef.DIVERGENT


def test_matches_source_series_at_shared_point():
    # dollar_energy_metabolism.explore_recycling_fraction uses subtotal/(1-r)
    series = dict((r, tot) for r, tot, _ in
                  dem.explore_recycling_fraction(E_base=1.0, subtotal=1.0,
                                                 r_range=[0.3, 0.6]))
    assert _near(series[0.3], fef.multiplier(0.3))
    assert _near(series[0.6], fef.multiplier(0.6))


# ---------------------------------------------------------------- statuses

def test_layers_imported_not_copied_and_all_carried():
    assert len(fef.METABOLISM_LAYERS) == len(dem.OVERHEAD_LAYERS)
    for lay, src in zip(fef.METABOLISM_LAYERS, dem.OVERHEAD_LAYERS):
        assert lay.name == src.name
        assert lay.r.lo == src.r_low and lay.r.hi == src.r_high
        assert lay.r.status == fef.CARRIED_UNSOURCED
    for name in ("0.11", "0.56", "1.40", "0.23"):
        assert name not in re.sub(r"#.*", "", SRC.split("_CARRIED_SOURCE")[1]
                                  .split("ENERGY_PER_POSITION")[0])


def test_no_layer_claims_measured():
    for lay in fef.METABOLISM_LAYERS + fef.DEPENDENCY_CHAIN:
        assert lay.r.status != fef.MEASURED


def test_chain_covers_order_and_carries_no_number():
    names = {l.name for l in fef.DEPENDENCY_CHAIN}
    assert ORDER_CHAIN <= names
    for lay in fef.DEPENDENCY_CHAIN:
        assert lay.group == "chain"
        assert lay.r.status == fef.UNMEASURED
        assert lay.r.lo is None and lay.r.hi is None
        assert lay.logged_under and lay.would_measure


def test_rrange_refuses_number_on_unmeasured_and_missing_source():
    for bad in (lambda: fef.RRange(0.1, None, fef.UNMEASURED, "x"),
                lambda: fef.RRange(None, None, fef.MEASURED, "x"),
                lambda: fef.RRange(0.5, 0.2, fef.MEASURED, "x"),
                lambda: fef.RRange(0.1, 0.2, fef.MEASURED, " "),
                lambda: fef.RRange(0.1, 0.2, "GUESSED", "x")):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError("RRange accepted an invalid range")


# ---------------------------------------------------------------- floor

def test_floor_refuses_to_be_a_total():
    fl = fef.BANKING_ELECTRICITY_FLOOR
    try:
        fl.as_total()
    except fef.FloorIsNotATotal as e:
        assert "FLOOR" in str(e)
    else:
        raise AssertionError("floor read as total")
    joined = " ".join(fl.excludes)
    for need in ("dependency chain", "embodied", "leverage"):
        assert need in joined
    assert fl.status == fef.CARRIED_UNSOURCED


# ---------------------------------------------------------------- bands

def test_strict_default_sums_nothing():
    f = fef.footprint(mode="strict")
    assert f["r_effective"]["lo"] == 0.0
    assert f["r_effective"]["hi"] == fef.UNBOUNDED
    assert f["contributing"] == []
    assert set(f["sink_conditions"].values()) == {fef.UNDETERMINED}
    assert f["M"]["hi"]["bound"] == fef.UPPER_BOUND
    assert f["M"]["lo"]["bound"] == fef.UNBOUNDED
    assert not f["rests_on_carried"]


def test_carried_lo_reproduces_source_sum():
    expect = sum(l.r_low for l in dem.OVERHEAD_LAYERS)
    f = fef.footprint(mode="carried")
    assert _near(f["r_effective"]["lo"], expect)
    assert f["r_effective"]["hi"] == fef.UNBOUNDED   # chain unmeasured
    assert f["rests_on_carried"]
    assert f["sink_conditions"]["r_effective_gt_half"] == fef.TRUE
    assert f["sink_conditions"]["r_effective_ge_1"] == fef.UNDETERMINED


def test_all_measured_fixture_closes():
    # CONSTRUCTED: r_vis 0.2, r_hid 0.1 -> r 0.3, m = 1/0.7
    lays = (_m("a", 0.2, 0.2), _m("b", 0.1, 0.1, group="chain"))
    f = fef.footprint(E_base=7.0, dt=2.0, layers=lays)
    m = 1.0 / 0.7
    assert _near(f["E_total"]["lo"], 7.0 * m)
    assert _near(f["E_total"]["hi"], 7.0 * m)
    tot = f["E_waste"]["lo"] + f["E_hidden"]["lo"]
    assert _near(tot, f["E_total"]["lo"] - 7.0)          # closure
    assert f["M"]["hi"]["bound"] == fef.EXACT
    assert _near(f["M"]["hi"]["M"], (7.0 - 7.0 * 0.3 * m) / 2.0)
    assert set(f["sink_conditions"].values()) == {fef.FALSE}


def test_three_sink_conditions_separate():
    # CONSTRUCTED: r 0.6 -> gt_half TRUE, ge_1 FALSE, any_layer FALSE
    f = fef.footprint(layers=(_m("a", 0.3, 0.3), _m("b", 0.3, 0.3)))
    sc = f["sink_conditions"]
    assert sc["r_effective_gt_half"] == fef.TRUE
    assert sc["r_effective_ge_1"] == fef.FALSE
    assert sc["any_layer_r_ge_1"] == fef.FALSE
    assert f["M"]["hi"]["M"] < 0                         # M < 0 below r = 1
    # CONSTRUCTED: r 0.5 exactly -> gt_half FALSE (strict >), M == 0
    f2 = fef.footprint(layers=(_m("a", 0.5, 0.5),))
    assert f2["sink_conditions"]["r_effective_gt_half"] == fef.FALSE
    assert _near(f2["M"]["hi"]["M"], 0.0)
    # CONSTRUCTED: one layer r 1.2 -> any_layer TRUE and divergent TRUE
    f3 = fef.footprint(layers=(_m("a", 1.2, 1.2),))
    assert f3["sink_conditions"]["any_layer_r_ge_1"] == fef.TRUE
    assert f3["sink_conditions"]["r_effective_ge_1"] == fef.TRUE
    assert f3["E_total"]["lo"] == fef.DIVERGENT
    assert f3["M"]["hi"]["bound"] == fef.DIVERGENT


def test_band_straddle_is_undetermined():
    f = fef.footprint(layers=(_m("a", 0.4, 1.3),))
    assert f["sink_conditions"]["r_effective_ge_1"] == fef.UNDETERMINED
    assert f["sink_conditions"]["any_layer_r_ge_1"] == fef.UNDETERMINED
    assert f["E_total"]["hi"] == fef.DIVERGENT


def test_unmeasured_term_makes_bound_one_sided_never_zero():
    f = fef.footprint(layers=(_m("a", 0.2, 0.2), _u("c")))
    assert f["r_effective"]["hi"] == fef.UNBOUNDED
    assert f["E_hidden"]["hi"] == fef.UNBOUNDED
    assert f["M"]["hi"]["bound"] == fef.UPPER_BOUND
    assert f["excluded"] == ["c"]


def test_mode_and_base_validation():
    for bad in (lambda: fef.footprint(mode="guess"),
                lambda: fef.footprint(E_base=0.0)):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError("accepted invalid input")


# ---------------------------------------------------------------- source

def test_stdlib_only():
    allowed = set(sys.stdlib_module_names) if hasattr(
        sys, "stdlib_module_names") else {"json", "sys", "dataclasses",
                                          "typing"}
    allowed |= {"dollar_energy_metabolism"}
    for node in ast.walk(ast.parse(SRC)):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split(".")[0] in allowed, a.name
        elif isinstance(node, ast.ImportFrom):
            assert node.module.split(".")[0] in allowed, node.module


def test_ascii_source():
    SRC.encode("ascii")


def test_every_gap_is_marked_inline():
    ids = [g[0] for g in fef.GAPS]
    assert len(ids) == len(set(ids))
    body = SRC.split("GAPS = (")[0] + SRC.split("GAPS = (")[1].split("\n)\n", 1)[1]
    for gid in ids:
        assert re.search(r"GAP %s\b" % re.escape(gid), body), gid


def test_every_choice_cited_outside_its_declaration():
    after = SRC.split("CHOICES = {")[1].split("\n}\n", 1)[1]
    for k in fef.CHOICES:
        assert "[CHOICE %d]" % k in after, k


def test_selftest_refused_and_render_deterministic():
    assert fef.main(["--selftest"]) == 2
    for mode in fef.MODES:
        assert fef.render(mode) == fef.render(mode)
        fef.render(mode).encode("ascii")
    buf = io.StringIO()
    with redirect_stdout(buf):
        assert fef.main(["--choices"]) == 0
    assert buf.getvalue().count("[CHOICE") == len(fef.CHOICES)
    assert fef.main(["--mode", "nonsense"]) == 2


def test_source_module_unchanged_behaviour():
    r = dem.compute_dollar_energy(dem.SCENARIOS["direct_action"])
    assert r["overall_multiplier"] == 1.0


def _run_all():
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for n, f in tests:
        try:
            f()
        except Exception as e:      # report and continue
            failed += 1
            print("FAIL %s: %r" % (n, e))
    print("checks: %d   failed: %d" % (len(tests), failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
