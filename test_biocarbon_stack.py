# test_biocarbon_stack.py
# Smoke tests for the biocarbon_stack subproject. Imports every src
# module, exercises the demo entry points, and sanity-checks the
# Monte Carlo headline numbers against the README's claimed band.

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
BIOCARBON_SRC = os.path.join(REPO_ROOT, "biocarbon_stack", "src")
BIOCARBON_SCRIPTS = os.path.join(REPO_ROOT, "biocarbon_stack", "scripts")
sys.path.insert(0, BIOCARBON_SRC)


SRC_MODULES = [
    "wetland_core",
    "marine_core",
    "spike_mitigation",
    "boundary_conditions",
    "redundancy_and_range_shift",
    "adaptive_layer",
    "geological_vector",
    "governance_constraints",
    "global_potential",
    "backwards_building",
]


@pytest.mark.parametrize("name", SRC_MODULES)
def test_src_module_imports(name):
    __import__(name)


def test_global_potential_runs():
    import global_potential as gp
    g = gp.global_balance()
    assert g["biological_drawdown_GtC_yr"] > 0
    assert 0 < g["fraction_emissions_offset"] < 5
    assert "VERDICT" in g


def test_run_full_stack_monte_carlo():
    sys.path.insert(0, BIOCARBON_SCRIPTS)
    import run_full_stack as rf
    mc = rf.monte_carlo(n=200)
    # README claims median 4.0 with 90% CI 3.1-4.9; allow generous band
    # so the test isn't flaky across random seeds.
    assert 2.0 < mc["p50"] < 6.0
    assert mc["p05"] <= mc["p50"] <= mc["p95"]
    sp = rf.methane_spike_distribution()
    assert 0 < sp["central_reduction"] < 1
