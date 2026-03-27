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

    def test_bottom_water_formation_present(self):
        from layer_4_hydrosphere import coupling_state
        result = coupling_state(T_ocean_C=15.0, S_ocean=35.0,
                                T_north_C=8.0, S_north=35.0,
                                T_south_C=26.0, S_south=36.0,
                                ice_fraction=0.85)
        assert "NADW_formation_Sv" in result
        assert "AABW_formation_Sv" in result
        assert "total_bottom_water_Sv" in result
        assert "deep_convection_active" in result
        assert "deep_water_ventilation_yr" in result

    def test_bottom_water_positive(self):
        """Bottom water formation should be positive under baseline conditions."""
        from layer_4_hydrosphere import coupling_state
        result = coupling_state(T_ocean_C=15.0, S_ocean=35.0,
                                T_north_C=8.0, S_north=35.0,
                                T_south_C=26.0, S_south=36.0,
                                ice_fraction=0.85)
        assert result["total_bottom_water_Sv"] > 0

    def test_meltwater_reduces_formation(self):
        """Freshwater input should reduce bottom water formation."""
        from layer_4_hydrosphere import bottom_water_formation_rate
        baseline = bottom_water_formation_rate(T_north_C=2.0, S_north=35.0,
                                               delta_S_melt=0.0)
        freshened = bottom_water_formation_rate(T_north_C=2.0, S_north=35.0,
                                                delta_S_melt=0.3)
        assert freshened["NADW_formation_Sv"] < baseline["NADW_formation_Sv"]

    def test_brine_rejection_positive(self):
        """Brine rejection should increase density."""
        from layer_4_hydrosphere import brine_rejection_flux
        result = brine_rejection_flux(ice_formation_rate_m_yr=0.5)
        assert result["delta_rho_haline_kgm3"] > 0
        assert result["salt_flux_kg_m2_yr"] > 0

    def test_ventilation_age_finite(self):
        """Ventilation age should be finite and positive."""
        from layer_4_hydrosphere import deep_water_ventilation_age
        age = deep_water_ventilation_age(formation_rate_Sv=20.0)
        assert 0 < age < 10000  # typical 500-2000 years

    def test_ventilation_age_infinite_at_zero(self):
        """Zero formation rate -> infinite ventilation age."""
        from layer_4_hydrosphere import deep_water_ventilation_age
        age = deep_water_ventilation_age(formation_rate_Sv=0.0)
        assert age == np.inf


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

    def test_cascade_result_has_summary(self):
        from cascade_engine import run_cascade, SCENARIOS
        for name, scenario in SCENARIOS.items():
            result = run_cascade(scenario, verbose=False)
            assert isinstance(result.summary, dict), f"Scenario {name} has no summary"
            assert len(result.summary) > 0, f"Scenario {name} has empty summary"

    def test_baseline_keys_valid(self):
        from cascade_engine import BASELINE
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

    def test_threshold_crossing_triggered(self):
        """At least one scenario triggers a threshold crossing."""
        from cascade_engine import run_cascade, SCENARIOS
        any_crossing = False
        for name, scenario in SCENARIOS.items():
            result = run_cascade(scenario, verbose=False)
            if result.threshold_crossings:
                any_crossing = True
                break
        assert any_crossing, "No scenario triggered any threshold crossing"

    def test_amplifying_loop_triggered(self):
        """At least one scenario triggers an amplifying loop."""
        from cascade_engine import run_cascade, SCENARIOS
        any_loop = False
        for name, scenario in SCENARIOS.items():
            result = run_cascade(scenario, verbose=False)
            if result.amplifying_loops:
                any_loop = True
                break
        assert any_loop, "No scenario triggered any amplifying loop"


# ─────────────────────────────────────────────
# BASELINE PHYSICAL SANITY
# ─────────────────────────────────────────────

class TestBaselineSanity:
    def test_no_negative_temperatures(self):
        from cascade_engine import BASELINE
        temp_keys = ["T_surface", "T_pole", "T_surface_K"]
        for k in temp_keys:
            assert BASELINE[k] > 0, f"Negative temperature: {k}={BASELINE[k]}"

    def test_no_negative_densities(self):
        from cascade_engine import BASELINE
        density_keys = ["n_e", "n_e_F2", "n_sw"]
        for k in density_keys:
            assert BASELINE[k] > 0, f"Negative density: {k}={BASELINE[k]}"

    def test_pressure_positive(self):
        from cascade_engine import BASELINE
        assert BASELINE["P_surface"] > 0

    def test_salinity_reasonable(self):
        from cascade_engine import BASELINE
        assert 30 <= BASELINE["S_ocean"] <= 40
        assert 30 <= BASELINE["S_north"] <= 40
        assert 30 <= BASELINE["S_south"] <= 40

    def test_co2_reasonable(self):
        from cascade_engine import BASELINE
        assert 350 <= BASELINE["CO2_ppm"] <= 500

    def test_ocean_ph_reasonable(self):
        from cascade_engine import BASELINE
        assert 7.0 <= BASELINE["ocean_pH"] <= 8.5

    def test_layer_outputs_physically_reasonable(self):
        """Verify layer outputs don't contain negative temperatures or densities."""
        from cascade_engine import run_all_layers, BASELINE
        states = run_all_layers(BASELINE)
        for layer_num, state in states.items():
            for key, val in state.items():
                if isinstance(val, (int, float)):
                    # Temperature keys should be positive
                    if "temperature" in key.lower() or key.endswith("_K"):
                        assert val > 0, f"Layer {layer_num}: negative temperature {key}={val}"
                    # Density keys should be non-negative
                    if "density" in key.lower() and "energy" not in key.lower():
                        assert val >= 0, f"Layer {layer_num}: negative density {key}={val}"


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

    def test_every_layer_has_assumption(self):
        """Every layer (0-6) has at least one registered assumption check."""
        from assumption_validator.registry import REGISTRY
        layers_covered = set()
        for boundary in REGISTRY.values():
            layers_covered.add(boundary.source_layer)
        for layer_num in range(7):
            assert layer_num in layers_covered, \
                f"Layer {layer_num} has no registered assumption check"

    def test_assumptions_have_required_fields(self):
        """Each assumption has validity_range, description, and severity."""
        from assumption_validator.registry import REGISTRY
        for aid, boundary in REGISTRY.items():
            assert boundary.green_range is not None, f"{aid}: missing green_range"
            assert boundary.yellow_range is not None, f"{aid}: missing yellow_range"
            assert boundary.red_threshold is not None, f"{aid}: missing red_threshold"
            assert boundary.notes, f"{aid}: missing notes (description)"

    def test_assess_from_layer_states(self):
        from assumption_validator.registry import assess_from_layer_states
        from cascade_engine import run_all_layers, BASELINE
        states = run_all_layers(BASELINE)
        results = assess_from_layer_states(states)
        assert len(results) > 0
        for aid, data in results.items():
            assert "status" in data


# ─────────────────────────────────────────────
# MAGNONIC SUBLAYER
# ─────────────────────────────────────────────

class TestMagnonicSublayer:
    def test_import(self):
        import magnonic_sublayer

    def test_dispersion_relation_positive(self):
        from magnonic_sublayer import dispersion_relation
        omega = dispersion_relation(k=1e7, H0=0.1, M_s=1.4e5, A_ex=3.65e-12)
        assert omega > 0

    def test_dispersion_k_zero(self):
        """k=0 should give the FMR frequency (band bottom)."""
        from magnonic_sublayer import dispersion_relation
        omega = dispersion_relation(k=0, H0=0.1, M_s=1.4e5, A_ex=3.65e-12, theta_deg=90)
        assert omega > 0  # Damon-Eshbach has nonzero gap at k=0

    def test_group_velocity_finite(self):
        from magnonic_sublayer import group_velocity
        vg = group_velocity(k=1e7, H0=0.1, M_s=1.4e5, A_ex=3.65e-12)
        assert np.isfinite(vg)

    def test_propagation_length_yig_longer_than_permalloy(self):
        """YIG (ultra-low damping) should propagate further than Permalloy."""
        from magnonic_sublayer import propagation_length
        lp_yig = propagation_length(k=1e7, H0=0.1, M_s=1.4e5, A_ex=3.65e-12, alpha=3e-5)
        lp_py = propagation_length(k=1e7, H0=0.1, M_s=8.6e5, A_ex=1.3e-11, alpha=0.008)
        assert lp_yig > lp_py

    def test_thermal_magnon_number_positive(self):
        from magnonic_sublayer import thermal_magnon_number, dispersion_relation
        omega = dispersion_relation(k=1e7, H0=0.1, M_s=1.4e5, A_ex=3.65e-12)
        n = thermal_magnon_number(omega, T=300.0)
        assert n >= 0

    def test_thermal_magnon_zero_at_zero_T(self):
        from magnonic_sublayer import thermal_magnon_number
        assert thermal_magnon_number(1e10, T=0) == 0.0

    def test_magnon_phonon_coupling_returns_dict(self):
        from magnonic_sublayer import magnon_phonon_coupling_strength
        result = magnon_phonon_coupling_strength(A_ex=3.65e-12, M_s=1.4e5, c_sound=7209)
        assert isinstance(result, dict)
        assert "crossover_k" in result
        assert "coupling_regime" in result

    def test_coupling_state_returns_all_keys(self):
        from magnonic_sublayer import magnonic_coupling_state
        state = magnonic_coupling_state()
        expected = [
            "magnon_band_bottom_Hz", "magnon_freq_dipolar_Hz",
            "magnon_vg_dipolar_m_s", "magnon_prop_length_exchange_m",
            "alpha_total", "thermal_occupation_exchange",
            "magnon_phonon_crossover_Hz", "magnon_phonon_regime",
            "thermal_regime", "magnon_energy_density_J",
        ]
        for key in expected:
            assert key in state, f"Missing key: {key}"

    def test_coupling_state_plasma_coupling(self):
        """When n_e is provided, plasma coupling fields should be populated."""
        from magnonic_sublayer import magnonic_coupling_state
        state = magnonic_coupling_state(n_e=1e12)
        assert state["plasma_frequency_Hz"] > 0
        assert state["magnon_plasma_freq_ratio"] > 0

    def test_materials_all_run(self):
        from magnonic_sublayer import magnonic_coupling_state, MATERIALS
        for name, params in MATERIALS.items():
            state = magnonic_coupling_state(
                H0=0.1, M_s=params["M_s"], A_ex=params["A_ex"],
                alpha=params["alpha"], conductivity=params["conductivity"],
                c_sound=params["c_sound"],
            )
            assert len(state) > 0, f"Material {name} returned empty state"

    def test_layer0_includes_magnonic_keys(self):
        """Layer 0 coupling_state should include magnonic outputs."""
        from layer_0_electromagnetics import coupling_state
        state = coupling_state(n_e=1e12, B_surface=5e-5, E_surface=1e-4,
                               frequency_range=(1e3, 1e7))
        assert "magnonic_energy_density_J" in state
        assert "magnonic_band_bottom_Hz" in state
        assert "magnonic_damping_total" in state

    def test_layer0_explicit_material(self):
        """Layer 0 coupling_state with explicit magnonic material."""
        from layer_0_electromagnetics import coupling_state
        state = coupling_state(n_e=1e12, B_surface=5e-5, E_surface=1e-4,
                               frequency_range=(1e3, 1e7),
                               magnonic_material="YIG")
        # Should have prefixed magnonic keys
        assert "magnonic_magnon_band_bottom_Hz" in state
        assert "magnonic_magnon_phonon_regime" in state

    def test_geomagnetic_scenario_runs(self):
        """The geomagnetic_field_weakening scenario should run."""
        from cascade_engine import run_cascade, SCENARIOS
        result = run_cascade(SCENARIOS["geomagnetic_field_weakening"], verbose=False)
        assert result.forcing is not None
        assert len(result.layer_states) == 7


# ─────────────────────────────────────────────
# MAGNOMECHANICAL SUB-LAYER (Layer 0b)
# ─────────────────────────────────────────────

class TestMagnomechanicalSublayer:
    def test_import(self):
        import layer_0b_magnomechanical

    def test_coupling_state_returns_dict(self):
        from layer_0b_magnomechanical import coupling_state
        state = coupling_state()
        assert isinstance(state, dict)
        assert len(state) > 0

    def test_coupling_state_expected_keys(self):
        from layer_0b_magnomechanical import coupling_state
        state = coupling_state()
        expected = [
            "magnon_freq_Hz", "spin_phonon_coupling_Hz",
            "g_collective_Hz", "phonon_mode_1_Hz",
            "v_acoustic_m_s", "seismo_detectable",
            "detection_range_m", "piezo_voltage_V",
            "magnonic_crystal", "morin_transition_active",
        ]
        for key in expected:
            assert key in state, f"Missing key: {key}"

    def test_all_minerals_valid(self):
        """All 5 minerals produce valid outputs."""
        from layer_0b_magnomechanical import coupling_state, CRUSTAL_MINERALS
        for mineral_key in CRUSTAL_MINERALS:
            state = coupling_state(mineral=mineral_key)
            assert state["spin_phonon_coupling_Hz"] >= 0, \
                f"{mineral_key}: negative coupling"
            assert state["g_collective_Hz"] >= 0, \
                f"{mineral_key}: negative collective coupling"
            assert np.isfinite(state["v_acoustic_m_s"]), \
                f"{mineral_key}: infinite velocity"

    def test_all_signals_valid(self):
        """All 9 signal types produce valid outputs."""
        from layer_0b_magnomechanical import coupling_state, GEOMAGNETIC_SIGNALS
        for sig_key in GEOMAGNETIC_SIGNALS:
            state = coupling_state(signal_type=sig_key)
            assert state["v_acoustic_m_s"] >= 0, \
                f"{sig_key}: negative acoustic velocity"
            assert np.isfinite(state["detection_range_m"]), \
                f"{sig_key}: infinite detection range"

    def test_all_minerals_x_signals(self):
        """5 minerals x 9 signals = 45 combos, all valid."""
        from layer_0b_magnomechanical import (
            coupling_state, CRUSTAL_MINERALS, GEOMAGNETIC_SIGNALS
        )
        for mineral in CRUSTAL_MINERALS:
            for signal in GEOMAGNETIC_SIGNALS:
                state = coupling_state(mineral=mineral, signal_type=signal)
                assert state["g_collective_Hz"] >= 0

    def test_morin_transition_hematite(self):
        """Hematite below -10C should have Morin transition active."""
        from layer_0b_magnomechanical import coupling_state
        cold = coupling_state(mineral="hematite", T=250.0)
        warm = coupling_state(mineral="hematite", T=300.0)
        assert cold["morin_transition_active"] is True
        assert warm["morin_transition_active"] is False

    def test_piezo_voltage_quartz_only(self):
        """Only quartz_fe_defect should have nonzero piezo voltage."""
        from layer_0b_magnomechanical import coupling_state
        quartz = coupling_state(mineral="quartz_fe_defect")
        magnetite = coupling_state(mineral="magnetite")
        assert quartz["piezo_voltage_V"] > 0
        assert magnetite["piezo_voltage_V"] == 0

    def test_layer0_includes_magnomech_keys(self):
        """Layer 0 coupling_state should include magnomech_ keys."""
        from layer_0_electromagnetics import coupling_state
        state = coupling_state(n_e=1e12, B_surface=5e-5, E_surface=1e-4,
                               frequency_range=(1e3, 1e7))
        assert "magnomech_v_acoustic_m_s" in state
        assert "magnomech_seismo_detectable" in state
        assert "magnomech_g_collective_Hz" in state
        assert "magnomech_piezo_voltage_V" in state

    def test_new_scenarios_run(self):
        """New magnomechanical scenarios should run."""
        from cascade_engine import run_cascade, SCENARIOS
        for name in ["geomagnetic_storm_magnomech", "morin_transition",
                     "bif_magnonic_crystal"]:
            result = run_cascade(SCENARIOS[name], verbose=False)
            assert result.forcing is not None, f"Scenario {name} failed"
            assert len(result.layer_states) == 7

    def test_magnomechanical_feedback_loop_exists(self):
        """The Magnomechanical-EM loop should be in KNOWN_LOOPS."""
        from cascade_engine import KNOWN_LOOPS
        names = [loop["name"] for loop in KNOWN_LOOPS]
        assert "Magnomechanical-EM" in names

    def test_bidirectional_cascade(self):
        """Layer 0 forcing should produce Layer 5 signal and vice versa."""
        from cascade_engine import run_cascade, Forcing
        # Layer 0 -> Layer 5
        f0 = Forcing(layer=0, variable="B_surface", magnitude=-2e-5,
                     description="test L0->L5", units="T")
        r0 = run_cascade(f0, verbose=False)
        has_l5 = any(s["target_layer"] == 5 for s in r0.cascade_signals)
        assert has_l5, "L0 forcing did not produce L5 cascade signal"

        # Layer 5 -> Layer 0
        f5 = Forcing(layer=5, variable="ice_mass_loss_Gt", magnitude=500.0,
                     description="test L5->L0", units="Gt")
        r5 = run_cascade(f5, verbose=False)
        has_l0 = any(s["target_layer"] == 0 for s in r5.cascade_signals)
        assert has_l0, "L5 forcing did not produce L0 cascade signal"
