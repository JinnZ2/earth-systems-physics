# test_smoke.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Smoke tests — verify all layers compile, run with BASELINE values,
# and the cascade engine produces valid results.

import pytest
import numpy as np


# ─────────────────────────────────────────────
# LAYER IMPORTS
# ─────────────────────────────────────────────

def test_import_layer_0():
    import layer_0_electromagnetics

def test_import_layer_1():
    import layer_1_magnetosphere

def test_import_layer_2():
    import layer_2_ionosphere

def test_import_layer_3():
    import layer_3_atmosphere

def test_import_layer_4():
    import layer_4_hydrosphere

def test_import_layer_5():
    import layer_5_lithosphere

def test_import_layer_6():
    import layer_6_biosphere

def test_import_cascade_engine():
    import cascade_engine

def test_import_assumption_validator():
    import assumption_validator


# ─────────────────────────────────────────────
# COUPLING STATE — BASELINE VALUES
# ─────────────────────────────────────────────

class TestLayer0CouplingState:
    def test_returns_dict(self):
        from layer_0_electromagnetics import coupling_state
        result = coupling_state(n_e=1e12, B_surface=5e-5, E_surface=1e-4,
                                frequency_range=(1e3, 1e7))
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_has_expected_keys(self):
        from layer_0_electromagnetics import coupling_state
        result = coupling_state(n_e=1e12, B_surface=5e-5, E_surface=1e-4,
                                frequency_range=(1e3, 1e7))
        assert "plasma_frequency_hz" in result
        assert "skin_depth_m" in result


class TestLayer1CouplingState:
    def test_returns_dict(self):
        from layer_1_magnetosphere import coupling_state
        result = coupling_state(B_surface=5e-5, n_sw=5e6, v_sw=450e3,
                                Bz_imf=-2e-9, kp=2.0)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_magnetopause_positive(self):
        from layer_1_magnetosphere import coupling_state
        result = coupling_state(B_surface=5e-5, n_sw=5e6, v_sw=450e3,
                                Bz_imf=-2e-9, kp=2.0)
        assert result["estimated_magnetopause_Re"] > 0


class TestLayer2CouplingState:
    def test_returns_dict(self):
        from layer_2_ionosphere import coupling_state
        result = coupling_state(n_e_F2=1e12, B_surface=5e-5, kp=2.0,
                                solar_flux=1.0, nu_en=1e3, E_field=1e-3)
        assert isinstance(result, dict)
        assert len(result) > 0


class TestLayer3CouplingState:
    def test_returns_dict(self):
        from layer_3_atmosphere import coupling_state
        result = coupling_state(T_surface=288.0, T_pole=243.0,
                                P_surface=101325.0, q_surface=0.010,
                                delta_CO2_ppm=140.0, AOD=0.15,
                                latitude_deg=45.0)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_temperature_reasonable(self):
        from layer_3_atmosphere import coupling_state
        result = coupling_state(T_surface=288.0, T_pole=243.0,
                                P_surface=101325.0, q_surface=0.010)
        assert "T_effective_K" in result
        assert result["T_effective_K"] > 0


class TestLayer4CouplingState:
    def test_returns_dict(self):
        from layer_4_hydrosphere import coupling_state
        result = coupling_state(T_ocean_C=15.0, S_ocean=35.0,
                                T_north_C=8.0, S_north=35.0,
                                T_south_C=26.0, S_south=36.0,
                                ice_fraction=0.85)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_amoc_positive(self):
        from layer_4_hydrosphere import coupling_state
        result = coupling_state(T_ocean_C=15.0, S_ocean=35.0,
                                T_north_C=8.0, S_north=35.0,
                                T_south_C=26.0, S_south=36.0,
                                ice_fraction=0.85)
        assert result["AMOC_heat_transport_W"] > 0


class TestLayer5CouplingState:
    def test_returns_dict(self):
        from layer_5_lithosphere import coupling_state
        result = coupling_state(ice_mass_loss_Gt=280.0, SLR_m=0.20,
                                T_ocean_C=15.0)
        assert isinstance(result, dict)
        assert len(result) > 0


class TestLayer6CouplingState:
    def test_returns_dict(self):
        from layer_6_biosphere import coupling_state
        result = coupling_state(T_surface_K=288.0, CO2_ppm=420.0,
                                ocean_pH=8.10)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_ocean_ph_present(self):
        from layer_6_biosphere import coupling_state
        result = coupling_state(T_surface_K=288.0, CO2_ppm=420.0,
                                ocean_pH=8.10)
        assert "ocean_pH" in result


# ─────────────────────────────────────────────
# CASCADE ENGINE
# ─────────────────────────────────────────────

class TestCascadeEngine:
    def test_run_all_layers_baseline(self):
        from cascade_engine import run_all_layers, BASELINE
        states = run_all_layers(BASELINE)
        assert len(states) == 7
        for i in range(7):
            assert isinstance(states[i], dict)
            assert len(states[i]) > 0

    def test_run_cascade_co2_pulse(self):
        from cascade_engine import run_cascade, SCENARIOS
        result = run_cascade(SCENARIOS["co2_pulse_100ppm"], verbose=False)
        assert result.forcing is not None
        assert len(result.layer_states) == 7

    def test_run_cascade_all_scenarios(self):
        from cascade_engine import run_cascade, SCENARIOS
        for name, scenario in SCENARIOS.items():
            result = run_cascade(scenario, verbose=False)
            assert result.forcing is not None, f"Scenario {name} failed"
            assert len(result.layer_states) == 7, f"Scenario {name} missing layers"

    def test_baseline_keys_valid(self):
        from cascade_engine import BASELINE
        # Verify all expected layer groups present
        assert "T_surface" in BASELINE
        assert "B_surface" in BASELINE
        assert "n_e" in BASELINE
        assert "CO2_ppm" in BASELINE

    def test_invalid_forcing_variable_raises(self):
        from cascade_engine import run_cascade, Forcing
        bad_forcing = Forcing(
            layer=3, variable="typo_variable",
            magnitude=100, description="bad variable"
        )
        with pytest.raises(ValueError, match="Unknown forcing variable"):
            run_cascade(bad_forcing, verbose=False)


# ─────────────────────────────────────────────
# ASSUMPTION VALIDATOR
# ─────────────────────────────────────────────

class TestAssumptionValidator:
    def test_registry_loads(self):
        from assumption_validator.registry import REGISTRY
        assert len(REGISTRY) > 0

    def test_full_report(self):
        from assumption_validator import full_report
        from cascade_engine import run_all_layers, BASELINE
        layer_states = run_all_layers(BASELINE)
        report = full_report(layer_states)
        assert isinstance(report, dict)
