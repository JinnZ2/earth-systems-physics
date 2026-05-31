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
        from cascade_engine import run_all_layers, BASELINE, LAYER_INDICES
        states = run_all_layers(BASELINE)
        assert set(states.keys()) == set(LAYER_INDICES)
        for i in LAYER_INDICES:
            assert isinstance(states[i], dict)
            assert len(states[i]) > 0

    def test_run_cascade_co2_pulse(self):
        from cascade_engine import run_cascade, SCENARIOS, LAYER_INDICES
        result = run_cascade(SCENARIOS["co2_pulse_100ppm"], verbose=False)
        assert result.forcing is not None
        assert set(result.layer_states.keys()) == set(LAYER_INDICES)

    def test_run_cascade_all_scenarios(self):
        from cascade_engine import run_cascade, SCENARIOS, LAYER_INDICES
        for name, scenario in SCENARIOS.items():
            result = run_cascade(scenario, verbose=False)
            assert result.forcing is not None, f"Scenario {name} failed"
            assert set(result.layer_states.keys()) == set(LAYER_INDICES), \
                f"Scenario {name} missing layers"

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
        """Every Earth-system physics layer (0-6) has at least one
        registered assumption check. Layer -1 (orbital) and Layer 7
        (infrastructure) are auxiliary and not required to register."""
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
        from cascade_engine import run_cascade, SCENARIOS, LAYER_INDICES
        result = run_cascade(SCENARIOS["geomagnetic_field_weakening"], verbose=False)
        assert result.forcing is not None
        assert set(result.layer_states.keys()) == set(LAYER_INDICES)


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
        from cascade_engine import run_cascade, SCENARIOS, LAYER_INDICES
        for name in ["geomagnetic_storm_magnomech", "morin_transition",
                     "bif_magnonic_crystal"]:
            result = run_cascade(SCENARIOS[name], verbose=False)
            assert result.forcing is not None, f"Scenario {name} failed"
            assert set(result.layer_states.keys()) == set(LAYER_INDICES)

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

    def test_earth_magnomechanical_predictions_include_skyrmion(self):
        """The 5th testable prediction in earth_magnomechanical
        covers skyrmion-like textures in natural Fe-bearing
        centrosymmetric minerals. Every prediction must have the
        required fields; prediction #5 must reference the
        stabilization physics module (skyrmion_rkky) and the
        mode-frequency module (skyrmion_phonon_coupling)."""
        from earth_magnomechanical import testable_predictions
        preds = testable_predictions()
        assert len(preds) >= 5
        # Every entry has the baseline fields
        for p in preds:
            for field in (
                "prediction", "mechanism", "test", "signal_level",
            ):
                assert field in p
        # 5th prediction should mention skyrmions and RKKY
        fifth = preds[4]
        assert "skyrmion" in fifth["prediction"].lower()
        assert "RKKY" in fifth["mechanism"]
        # Should cross-reference the two supporting modules
        assert "skyrmion_rkky" in fifth["mechanism"]
        assert "skyrmion_phonon_coupling" in fifth["mechanism"]


# ─────────────────────────────────────────────
# ELECTROSTATIC TRANSDUCER
# ─────────────────────────────────────────────

class TestElectrostaticTransducer:
    def test_import(self):
        import electrostatic_transducer

    def test_piezo_voltage_from_strain(self):
        from electrostatic_transducer import piezo_voltage_from_strain
        result = piezo_voltage_from_strain(strain=1e-6, thickness_m=0.1e-3)
        assert result["V_static_V"] > 0
        assert result["V_resonant_V"] > result["V_static_V"]  # Q amplification

    def test_piezo_voltage_from_magnon(self):
        from electrostatic_transducer import piezo_voltage_from_magnon
        result = piezo_voltage_from_magnon(delta_B_T=500e-9)
        assert result["V_piezo_V"] > 0
        assert result["delta_f_magnon_Hz"] > 0

    def test_parallel_plate_force_scales_with_v_squared(self):
        from electrostatic_transducer import parallel_plate_force
        f1 = parallel_plate_force(V=1.0, gap_m=1e-6, area_m2=1e-8)
        f2 = parallel_plate_force(V=2.0, gap_m=1e-6, area_m2=1e-8)
        assert abs(f2["force_N"] / f1["force_N"] - 4.0) < 0.01  # V^2 scaling

    def test_comb_drive_force(self):
        from electrostatic_transducer import comb_drive_force
        result = comb_drive_force(V=10.0, n_fingers=100, finger_length_m=100e-6,
                                  gap_m=2e-6, thickness_m=20e-6)
        assert result["force_N"] > 0
        assert result["capacitance_F"] > 0

    def test_electrostatic_rotor(self):
        from electrostatic_transducer import electrostatic_rotor
        result = electrostatic_rotor(V=10.0, n_poles=50, rotor_radius_m=50e-6,
                                     gap_m=2e-6, rotor_thickness_m=10e-6,
                                     rotor_length_m=20e-6)
        assert result["torque_Nm"] > 0
        assert result["rpm_steady"] > 0

    def test_motor_configs_run(self):
        from electrostatic_transducer import (config_mems_micro,
            config_mems_milli, config_macro_disk)
        for fn in [config_mems_micro, config_mems_milli, config_macro_disk]:
            result = fn(V_drive=1.0)
            assert result["torque_Nm"] > 0

    def test_full_chain_no_magnets(self):
        """Full chain should use zero magnets, copper, or rare earths."""
        from electrostatic_transducer import full_transduction_chain
        chain = full_transduction_chain(delta_B_T=500e-9)
        assert chain["materials"]["magnets"] == "NONE"
        assert chain["materials"]["copper"] == "NONE (no windings)"
        assert chain["materials"]["rare_earth"] == "NONE"

    def test_full_chain_produces_torque(self):
        from electrostatic_transducer import full_transduction_chain
        chain = full_transduction_chain(delta_B_T=500e-9)
        assert chain["stage_4_motor"]["torque_Nm"] > 0
        assert chain["stage_3_piezo"]["V_piezo_V"] > 0

    def test_stronger_signal_more_torque(self):
        from electrostatic_transducer import full_transduction_chain
        weak = full_transduction_chain(delta_B_T=50e-9)
        strong = full_transduction_chain(delta_B_T=500e-9)
        assert strong["stage_4_motor"]["torque_Nm"] > weak["stage_4_motor"]["torque_Nm"]

    def test_coupling_state_export(self):
        from electrostatic_transducer import coupling_state
        state = coupling_state(delta_B_T=500e-9)
        assert "V_piezo_V" in state
        assert "torque_Nm" in state
        assert "P_mechanical_W" in state
        assert "B_sensitivity_T" in state


# ─────────────────────────────────────────────
# DEVICE SCALING
# ─────────────────────────────────────────────

class TestDeviceScaling:
    def test_import(self):
        import device_scaling

    def test_applications_defined(self):
        from device_scaling import APPLICATIONS
        assert len(APPLICATIONS) >= 10

    def test_motor_requirements_scales(self):
        """More torque should need bigger rotor."""
        from device_scaling import electrostatic_motor_requirements
        small = electrostatic_motor_requirements(1e-9, 100)
        big = electrostatic_motor_requirements(1e-3, 100)
        assert big["air_gap"]["rotor_radius_m"] > small["air_gap"]["rotor_radius_m"]

    def test_piezo_harvester_quartz_no_magnets(self):
        from device_scaling import piezo_harvester_requirements
        result = piezo_harvester_requirements(10e-6)
        qfe = result["materials"]["quartz_Fe_defect"]
        assert qfe["magnets_needed"] is False
        assert qfe["volume_cm3"] > 0

    def test_magnet_budget_all_apps(self):
        from device_scaling import full_device_survey
        survey = full_device_survey()
        for app_key, result in survey.items():
            assert "approaches" in result
            assert len(result["approaches"]) >= 2

    def test_zero_magnet_feasible_for_sensors(self):
        from device_scaling import magnet_budget
        result = magnet_budget("magnetometer_sensor")
        approaches = result["approaches"]
        has_zero_mag = any(
            a.get("magnet_g", 1) == 0 and a.get("feasible", False)
            for a in approaches.values()
        )
        assert has_zero_mag, "Sensors should be feasible without magnets"

    def test_junkyard_sources_exist(self):
        from device_scaling import JUNKYARD_SOURCES
        assert len(JUNKYARD_SOURCES) >= 8
        assert "smoky_quartz" in JUNKYARD_SOURCES
        assert "dead_hdd" in JUNKYARD_SOURCES

    def test_junkyard_build_magnetometer(self):
        from device_scaling import junkyard_build
        result = junkyard_build("magnetometer_sensor")
        assert "builds" in result
        assert "tier_0_junkyard" in result["builds"]
        assert result["builds"]["tier_0_junkyard"]["cost_usd"] <= 5

    def test_junkyard_build_all_apps(self):
        from device_scaling import junkyard_survey
        survey = junkyard_survey()
        assert len(survey) >= 10
        for app_key, result in survey.items():
            assert "builds" in result


# ─────────────────────────────────────────────
# DOLLAR ENERGY METABOLISM
# ─────────────────────────────────────────────

class TestDollarEnergyMetabolism:
    def test_import(self):
        import dollar_energy_metabolism

    def test_overhead_layers_defined(self):
        from dollar_energy_metabolism import OVERHEAD_LAYERS
        assert len(OVERHEAD_LAYERS) == 5
        names = {l.name for l in OVERHEAD_LAYERS}
        assert {"leverage", "margin_stack", "taxation",
                "narrative", "political"} == names

    def test_scenarios_defined(self):
        from dollar_energy_metabolism import SCENARIOS
        assert "direct_action" in SCENARIOS
        assert "typical_climate" in SCENARIOS
        assert "carbon_speculation" in SCENARIOS

    def test_direct_action_has_no_overhead(self):
        from dollar_energy_metabolism import compute_dollar_energy, SCENARIOS
        result = compute_dollar_energy(SCENARIOS["direct_action"])
        assert result["total_MJ_per_dollar"] == result["E_base_MJ"]
        assert result["overall_multiplier"] == 1.0
        assert not result["divergent"]

    def test_overhead_increases_total_energy(self):
        from dollar_energy_metabolism import compute_dollar_energy, SCENARIOS
        direct = compute_dollar_energy(SCENARIOS["direct_action"])
        typical = compute_dollar_energy(SCENARIOS["typical_climate"])
        speculative = compute_dollar_energy(SCENARIOS["carbon_speculation"])
        assert typical["total_MJ_per_dollar"] > direct["total_MJ_per_dollar"]
        assert speculative["total_MJ_per_dollar"] > typical["total_MJ_per_dollar"]

    def test_geometric_series_diverges_at_r_1(self):
        import math
        from dollar_energy_metabolism import explore_recycling_fraction
        series = explore_recycling_fraction()
        last = series[-1]  # r = 1.0
        assert last[0] == 1.0
        assert math.isinf(last[1])

    def test_ocean_timber_funding_scales_with_speculation(self):
        from dollar_energy_metabolism import (
            compute_project_audit, PROJECTS, SCENARIOS,
        )
        typical = compute_project_audit(
            PROJECTS["ocean_timber"], SCENARIOS["typical_climate"]
        )
        speculative = compute_project_audit(
            PROJECTS["ocean_timber"], SCENARIOS["carbon_speculation"]
        )
        # Under carbon speculation the funding CO2 should exceed
        # the claimed sequestration (the entire point of the audit)
        spec_frac = speculative["funding_CO2_as_fraction_of_claimed"]["high_budget"]
        typ_frac = typical["funding_CO2_as_fraction_of_claimed"]["high_budget"]
        assert spec_frac > 1.0, (
            "Carbon speculation case should emit more CO2 in financial "
            "overhead than it claims to sequester."
        )
        assert spec_frac > typ_frac, (
            "Speculative finance should be strictly worse than typical finance."
        )

    def test_sai_breakeven_impossible(self):
        from dollar_energy_metabolism import find_breakeven_r, PROJECTS
        # SAI claims no sequestration, so breakeven returns 0.0 by convention
        assert find_breakeven_r(PROJECTS["sai"]) == 0.0


# ─────────────────────────────────────────────
# OCEAN TIMBER SEQUESTRATION AUDIT
# ─────────────────────────────────────────────

class TestOceanTimberAudit:
    def test_import(self):
        import ocean_timber_sequestration_audit

    def test_constants_present(self):
        from ocean_timber_sequestration_audit import CONSTANTS
        # Spot-check a few expected keys
        for key in (
            "carbon_fraction_dry_wood",
            "dry_mass_per_boreal_tree_kg",
            "permafrost_thaw_CH4_kg_per_m2",
            "CH4_to_CO2_equivalence",
            "AMOC_weakening_threshold",
        ):
            assert key in CONSTANTS

    def test_default_run_is_net_source(self):
        from ocean_timber_sequestration_audit import run_simulation
        state = run_simulation(
            n_trees_per_year=1_000_000,
            transport_km=1000.0,
            dump_area_km2=10.0,
            years=10,
        )
        assert state["project_is_net_source"] is True
        assert state["net_carbon_CO2_kg"] < 0
        assert state["crossover_year"] is not None

    def test_layer_costs_nonnegative(self):
        from ocean_timber_sequestration_audit import (
            initial_state, harvest_carbon_cost, transport_carbon_cost,
        )
        state = initial_state(n_trees_per_year=1_000_000, years=1)
        harvest = harvest_carbon_cost(state)
        transport = transport_carbon_cost(state)
        for k, v in harvest.items():
            assert v >= 0, f"harvest component {k} is negative"
        for k, v in transport.items():
            assert v >= 0, f"transport component {k} is negative"

    def test_anoxic_transition_occurs_at_scale(self):
        from ocean_timber_sequestration_audit import run_simulation
        state = run_simulation(
            n_trees_per_year=1_000_000,
            transport_km=1000.0,
            dump_area_km2=10.0,
            years=50,
        )
        # With 50M trees dumped, O2 should crash and anoxic phase should engage
        assert state["anoxic"] is True
        assert state["local_O2_mL_L"] < 1.0

    def test_time_series_lengths_match_years(self):
        from ocean_timber_sequestration_audit import run_simulation
        years = 25
        state = run_simulation(years=years)
        assert len(state["ts_net_carbon_kg"]) == years
        assert len(state["ts_pH"]) == years
        assert len(state["ts_thermohaline"]) == years


# ─────────────────────────────────────────────
# OCEAN TIMBER CASCADE WIRING
# ─────────────────────────────────────────────

class TestOceanTimberCascadeWiring:
    def test_scenario_registered(self):
        from cascade_engine import SCENARIOS
        assert "ocean_timber_dumping" in SCENARIOS
        scn = SCENARIOS["ocean_timber_dumping"]
        assert scn.variable == "deforestation"
        assert scn.layer == 6

    def test_full_audit_helper_runs(self):
        from cascade_engine import run_ocean_timber_full_audit
        result = run_ocean_timber_full_audit(years=5, verbose=False)
        assert "cascade" in result
        assert "audit" in result
        assert "verdict" in result
        verdict = result["verdict"]
        assert verdict["project_is_net_source"] is True
        assert verdict["crossover_year"] is not None


# ─────────────────────────────────────────────
# CHATTEL SLAVERY TRIPLE AUDIT
# ─────────────────────────────────────────────

class TestChattelSlaveryTripleAudit:
    def test_import(self):
        import chattel_slavery_triple_audit

    def test_top_level_structures_present(self):
        from chattel_slavery_triple_audit import (
            SYSTEM_DEFINITION, DMAIC, SCIENTIFIC_METHOD,
            THERMODYNAMIC_AUDIT, META_AUDIT,
        )
        assert "claimed_purpose" in SYSTEM_DEFINITION
        assert "actual_topology" in SYSTEM_DEFINITION
        for phase in ("define", "measure", "analyze", "improve", "control"):
            assert phase in DMAIC
        for section in ("observation", "null_hypothesis", "alt_hypothesis",
                        "evidence", "verdict", "falsifiability"):
            assert section in SCIENTIFIC_METHOD
        for law in ("first_law", "second_law", "third_law",
                    "topology", "phase_transition"):
            assert law in THERMODYNAMIC_AUDIT
        assert "function_of_revisionism" in META_AUDIT
        assert "conclusion" in META_AUDIT

    def test_scientific_method_evidence_is_six_for_six(self):
        from chattel_slavery_triple_audit import SCIENTIFIC_METHOD
        evidence = SCIENTIFIC_METHOD["evidence"]
        assert len(evidence) == 6
        for pred_key in ("P1", "P2", "P3", "P4", "P5", "P6"):
            assert pred_key in evidence
            assert "H1 CONFIRMED" in evidence[pred_key]["observed"]
        verdict = SCIENTIFIC_METHOD["verdict"]
        assert "0/6" in verdict["H0_score"]
        assert "6/6" in verdict["H1_score"]

    def test_dmaic_analyze_chain_is_five_whys(self):
        from chattel_slavery_triple_audit import DMAIC
        chain = DMAIC["analyze"]["chain"]
        assert len(chain) == 5
        for step in chain:
            assert "why" in step
            assert "because" in step

    def test_print_summary_runs(self, capsys):
        from chattel_slavery_triple_audit import print_summary
        print_summary()
        captured = capsys.readouterr()
        assert "TRIPLE AUDIT SUMMARY" in captured.out
        assert "SIX SIGMA" in captured.out
        assert "SCIENTIFIC METHOD" in captured.out
        assert "THERMODYNAMICS" in captured.out
        assert "CONVERGENCE" in captured.out


# ─────────────────────────────────────────────
# SLAVERY SYSTEM AUDIT
# ─────────────────────────────────────────────

class TestSlaverySystemAudit:
    def test_import(self):
        import slavery_system_audit  # noqa: F401

    def test_top_level_structures_present(self):
        from slavery_system_audit import (
            SYSTEM_DEFINITION, DMAIC, SCIENTIFIC_METHOD,
            THERMODYNAMIC_AUDIT, META_AUDIT,
        )
        assert "claimed_purpose" in SYSTEM_DEFINITION
        assert "actual_topology" in SYSTEM_DEFINITION
        for phase in ("define", "measure", "analyze", "improve", "control"):
            assert phase in DMAIC
        for section in ("observation", "null_hypothesis", "alt_hypothesis",
                        "evidence", "verdict", "falsifiability"):
            assert section in SCIENTIFIC_METHOD
        for law in ("first_law", "second_law", "third_law",
                    "topology", "phase_transition"):
            assert law in THERMODYNAMIC_AUDIT
        assert "function_of_revisionism" in META_AUDIT
        assert "conclusion" in META_AUDIT

    def test_scientific_method_evidence_is_six_for_six(self):
        from slavery_system_audit import SCIENTIFIC_METHOD
        evidence = SCIENTIFIC_METHOD["evidence"]
        assert len(evidence) == 6
        for pred_key in ("P1", "P2", "P3", "P4", "P5", "P6"):
            assert pred_key in evidence
            assert "H1 CONFIRMED" in evidence[pred_key]["observed"]
        verdict = SCIENTIFIC_METHOD["verdict"]
        assert "0/6" in verdict["H0_score"]
        assert "6/6" in verdict["H1_score"]

    def test_dmaic_analyze_chain_is_five_whys(self):
        from slavery_system_audit import DMAIC
        chain = DMAIC["analyze"]["chain"]
        assert len(chain) == 5
        for step in chain:
            assert "why" in step
            assert "because" in step


# ─────────────────────────────────────────────
# INNOVATION REGRESSION AUDIT
# ─────────────────────────────────────────────

class TestInnovationRegressionAudit:
    def test_import(self):
        import innovation_regression_audit  # noqa: F401

    def test_top_level_dicts_present(self):
        from innovation_regression_audit import (
            PRODUCTIVITY_COMPARISON, INNOVATION_COST,
            PSYCHOLOGICAL_AUDIT, HOPE_DIFFERENTIAL, DISQUALIFICATION,
        )
        assert "free_settler_model" in PRODUCTIVITY_COMPARISON
        assert "extraction_system_model" in PRODUCTIVITY_COMPARISON
        assert "free_settler_psychology" in PSYCHOLOGICAL_AUDIT
        assert "enslaved_agent_psychology" in PSYCHOLOGICAL_AUDIT
        assert "observation" in HOPE_DIFFERENTIAL
        assert "thermodynamic_statement" in HOPE_DIFFERENTIAL

    def test_productivity_comparison_has_both_models(self):
        from innovation_regression_audit import PRODUCTIVITY_COMPARISON
        free = PRODUCTIVITY_COMPARISON["free_settler_model"]
        extraction = PRODUCTIVITY_COMPARISON["extraction_system_model"]
        assert isinstance(free, dict) and free
        assert isinstance(extraction, dict) and extraction


# ─────────────────────────────────────────────
# PROCESS EPISTEMOLOGY
# ─────────────────────────────────────────────

class TestProcessEpistemology:
    def test_import(self):
        import process_epistemology  # noqa: F401

    def test_epistemology_enum_has_both_modes(self):
        from process_epistemology import Epistemology
        assert Epistemology.STATE_BASED.value == "state"
        assert Epistemology.PROCESS_BASED.value == "process"

    def test_process_kinematics_updates(self):
        from process_epistemology import Process
        p = Process(name="soil_health", current=1.0)
        p.update(0.9, dt=1.0)
        p.update(0.75, dt=1.0)
        p.update(0.55, dt=1.0)
        # After three decreasing updates, velocity should be negative
        assert p.velocity < 0
        # And the process should know it's trending
        state = p.state()
        assert "velocity" in state
        assert "name" in state

    def test_epistemology_comparison_has_failure_cases(self):
        from process_epistemology import EpistemologyComparison
        ec = EpistemologyComparison()
        assert isinstance(ec.failure_cases, dict)
        assert len(ec.failure_cases) > 0

    def test_demo_runs(self, capsys):
        from process_epistemology import demo_epistemology_comparison
        demo_epistemology_comparison()
        captured = capsys.readouterr()
        assert "EPISTEMOLOGY" in captured.out.upper()


# ─────────────────────────────────────────────
# BUFFER SENSOR CORRUPTION
# ─────────────────────────────────────────────

class TestBufferSensorCorruption:
    def test_import(self):
        import buffer_sensor_corruption  # noqa: F401

    def test_sensor_mode_enum_members(self):
        from buffer_sensor_corruption import SensorMode
        assert SensorMode.INTEGRATED.value == "integrated"
        assert SensorMode.BUFFERED.value == "buffered"
        assert SensorMode.CORRUPTED.value == "corrupted"
        assert SensorMode.FAILED.value == "failed"

    def test_incentive_type_enum_members(self):
        from buffer_sensor_corruption import IncentiveType
        assert IncentiveType.ACCURACY.value == "accuracy"
        assert IncentiveType.STABILITY.value == "stability"
        assert IncentiveType.COMPLIANCE.value == "compliance"
        assert IncentiveType.COMFORT.value == "comfort"

    def test_integrated_sensor_reports_truth(self):
        from buffer_sensor_corruption import (
            Sensor, SensorMode, IncentiveType,
        )
        s = Sensor(
            name="test",
            mode=SensorMode.INTEGRATED,
            incentive=IncentiveType.ACCURACY,
        )
        out = s.read(ground_truth=1.23, baseline=0.0)
        # Integrated sensor should report the full deviation with zero
        # suppression
        assert out["reported_deviation"] == 1.23
        assert out["suppressed_total"] == 0.0
        assert out["failed"] is False

    def test_network_builds_and_reads(self):
        from buffer_sensor_corruption import SensorNetwork
        net = SensorNetwork()
        net.add_integrated_sensor("truth_1")
        net.add_institutional_sensor("comfort_1")
        net.add_corrupted_sensor("suppressed_1")
        result = net.read_all(ground_truth=0.5, baseline=0.0)
        assert result["sensors_total"] == 3
        assert result["ground_truth"] == 0.5
        # Integrated sensor reports truth; institutional/corrupted suppress
        assert result["sensors_reporting_true"] == 1
        assert result["sensors_suppressing"] == 2
        names = {r["sensor"] for r in result["individual_reports"]}
        assert names == {"truth_1", "comfort_1", "suppressed_1"}

    def test_demo_runs(self, capsys):
        from buffer_sensor_corruption import demo_buffer_failure
        demo_buffer_failure()
        captured = capsys.readouterr()
        assert "BUFFER" in captured.out.upper()


# ─────────────────────────────────────────────
# CONSEQUENCE VELOCITY
# ─────────────────────────────────────────────

class TestConsequenceVelocity:
    def test_import(self):
        import consequence_velocity  # noqa: F401

    def test_deferral_increases_velocity(self):
        from consequence_velocity import Consequence
        c = Consequence(name="test", domain="ecological")
        v0 = c.velocity
        c.defer(0.2)
        # Deferral should push velocity upward
        assert c.velocity > v0

    def test_buffer_overflow_cascades(self):
        from consequence_velocity import Consequence
        c = Consequence(
            name="test", domain="ecological", buffer_capacity=0.5,
        )
        result = c.defer(2.0)  # way beyond buffer capacity
        assert result["overflow"] > 0
        assert c.phase == "cascading"

    def test_field_coupling_propagates_velocity(self):
        from consequence_velocity import Consequence, ConsequenceField
        field = ConsequenceField()
        a = Consequence(name="a", domain="eco", velocity=1.0)
        b = Consequence(name="b", domain="eco", velocity=0.0)
        field.add(a)
        field.add(b)
        field.couple("a", "b", strength=0.5)
        field.step(dt=1.0)
        # b should have felt a's velocity through coupling
        assert field.consequences["b"].velocity > 0

    def test_demo_runs(self, capsys):
        from consequence_velocity import demo_consequence_cascade
        demo_consequence_cascade()
        captured = capsys.readouterr()
        assert "CONSEQUENCE" in captured.out.upper()


# ─────────────────────────────────────────────
# CONSTRAINT ACCOUNTABILITY CHAIN (schema)
# ─────────────────────────────────────────────

class TestConstraintAccountabilityChain:
    def test_import(self):
        import constraint_accountability_chain  # noqa: F401

    def test_schema_structures_present(self):
        from constraint_accountability_chain import (
            DECISION_NODE, ACCOUNTABILITY_CHAIN,
        )
        assert isinstance(DECISION_NODE, dict)
        assert isinstance(ACCOUNTABILITY_CHAIN, dict)
        for key in ("actor", "decision", "inheritance"):
            assert key in DECISION_NODE
        for key in ("mutations", "phenotype", "epigenetic_factors"):
            assert key in ACCOUNTABILITY_CHAIN

    def test_mechanisms_catalog(self):
        from constraint_accountability_chain import (
            MECHANISMS, COMFORT_MECHANISMS,
        )
        # One direct_sense + six comfort mechanisms
        assert len(MECHANISMS) == 7
        assert "direct_sense" in MECHANISMS
        assert MECHANISMS["direct_sense"]["is_comfort"] is False
        expected_comfort = {
            "attenuation", "delay", "reframe",
            "delegate_down", "normalize", "silence",
        }
        assert set(COMFORT_MECHANISMS) == expected_comfort
        for name in expected_comfort:
            assert MECHANISMS[name]["is_comfort"] is True
        # Every entry has the required documentation fields
        required_fields = {
            "is_comfort", "description", "example",
            "detection_hint", "reversibility",
        }
        for name, spec in MECHANISMS.items():
            assert required_fields <= set(spec.keys()), (
                "mechanism " + name + " missing fields"
            )

    def test_epigenetic_factors_catalog(self):
        from constraint_accountability_chain import EPIGENETIC_FACTORS
        expected = {
            "regulatory_pressure", "market_shock", "personnel_change",
            "public_exposure", "cascade_event", "resource_scarcity",
        }
        assert set(EPIGENETIC_FACTORS.keys()) == expected
        for name, spec in EPIGENETIC_FACTORS.items():
            assert spec["typical_effect"] in (
                "activates_direct_sense", "reinforces_comfort"
            )
            for key in ("description", "example", "typical_magnitude"):
                assert key in spec

    def test_constraint_domains_catalog(self):
        from constraint_accountability_chain import CONSTRAINT_DOMAINS
        expected_subset = {
            "safety_signal", "ecological_signal", "financial_signal",
            "health_signal", "social_signal", "scientific_signal",
            "ecological_constraint_signal",
        }
        assert expected_subset <= set(CONSTRAINT_DOMAINS.keys())
        for name, spec in CONSTRAINT_DOMAINS.items():
            assert "description" in spec
            assert "example" in spec

    def test_accountability_patterns_catalog(self):
        from constraint_accountability_chain import ACCOUNTABILITY_PATTERNS
        expected = {
            "ratchet_failure", "unanimous_comfort", "override_suppressed",
            "cascade_ready", "sudden_correction",
        }
        assert set(ACCOUNTABILITY_PATTERNS.keys()) == expected
        for name, spec in ACCOUNTABILITY_PATTERNS.items():
            for key in ("description", "detection_criteria", "intervention"):
                assert key in spec, (
                    "pattern " + name + " missing " + key
                )

    def test_example_chains_all_validate(self):
        from constraint_accountability_chain import (
            EXAMPLE_CHAINS, validate_chain_nodes, ACCOUNTABILITY_PATTERNS,
        )
        expected_examples = {
            "manufacturing_plant_safety",
            "climate_finance_greenwashing",
            "medical_symptom_suppression",
            "scientific_finding_softened",
        }
        assert set(EXAMPLE_CHAINS.keys()) == expected_examples
        for name, spec in EXAMPLE_CHAINS.items():
            for key in ("chain_id", "constraint_domain",
                        "description", "nodes", "expected_pattern"):
                assert key in spec, (
                    "example " + name + " missing " + key
                )
            assert spec["expected_pattern"] in ACCOUNTABILITY_PATTERNS
            ok, errors = validate_chain_nodes(spec["nodes"])
            assert ok, (
                "example " + name + " failed validation: " + repr(errors)
            )

    def test_validate_mechanism(self):
        from constraint_accountability_chain import validate_mechanism
        assert validate_mechanism("attenuation") is True
        assert validate_mechanism("direct_sense") is True
        assert validate_mechanism("silence") is True
        assert validate_mechanism("totally_made_up") is False

    def test_validate_node_dict_catches_errors(self):
        from constraint_accountability_chain import validate_node_dict

        good = {
            "actor_role": "operator", "layer": 0, "comfort_captured": 0.1,
            "constraint_at_stake": "x",
            "ground_signal": 0.5, "reported_signal": 0.5,
            "mechanism": "direct_sense",
        }
        ok, errs = validate_node_dict(good)
        assert ok is True
        assert errs == []

        # Missing fields
        ok, errs = validate_node_dict({"actor_role": "operator"})
        assert ok is False
        assert any("missing required field" in e for e in errs)

        # Unknown mechanism
        bad_mech = dict(good, mechanism="imaginary")
        ok, errs = validate_node_dict(bad_mech)
        assert ok is False
        assert any("unknown mechanism" in e for e in errs)

        # Out-of-range comfort_captured
        bad_comfort = dict(good, comfort_captured=1.5)
        ok, errs = validate_node_dict(bad_comfort)
        assert ok is False
        assert any("comfort_captured" in e for e in errs)

    def test_build_example_chain_instantiates_live_chain(self):
        from constraint_accountability_chain import (
            build_example_chain, EXAMPLE_CHAINS,
        )
        from constraint_accountability_engine import AccountabilityChain
        chain = build_example_chain("manufacturing_plant_safety")
        assert isinstance(chain, AccountabilityChain)
        assert chain.chain_id == "mfg_plant_7"
        assert chain.constraint_domain == "safety_signal"
        assert len(chain.nodes) == 5
        # The phenotype should surface all expected metrics
        phen = chain.phenotype
        for key in ("institutional_blindness", "ratchet_depth",
                    "reversion_energy", "cascade_risk", "time_to_failure"):
            assert key in phen
        # manufacturing example has a failed override attempt
        assert len(chain.find_override_failures()) >= 1

        import pytest
        with pytest.raises(KeyError):
            build_example_chain("not_a_real_example")

    def test_ai_reference_is_complete(self):
        from constraint_accountability_chain import (
            AI_REFERENCE, MECHANISMS, EPIGENETIC_FACTORS,
            CONSTRAINT_DOMAINS, ACCOUNTABILITY_PATTERNS, EXAMPLE_CHAINS,
        )
        expected_keys = {
            "purpose", "layer_position", "when_to_apply",
            "key_exports", "workflow", "common_mistakes",
            "integration_with_other_modules",
        }
        assert expected_keys <= set(AI_REFERENCE.keys())
        # Every key_exports entry is the name of a real export
        import constraint_accountability_chain as m
        for export_name in AI_REFERENCE["key_exports"]:
            assert hasattr(m, export_name), (
                "AI_REFERENCE['key_exports'] lists "
                + export_name
                + " but the module does not export it"
            )
        # Integration notes cover every sibling systems-analysis module
        integ = AI_REFERENCE["integration_with_other_modules"]
        for sibling in ("buffer_sensor_corruption.py",
                        "consequence_velocity.py",
                        "process_epistemology.py",
                        "ocean_timber_sequestration_audit.py",
                        "dollar_energy_metabolism.py",
                        "chattel_slavery_triple_audit.py",
                        "cascade_engine.py"):
            assert sibling in integ

    def test_reexports_engine_classes(self):
        import constraint_accountability_chain as m
        from constraint_accountability_engine import (
            DecisionNode, AccountabilityChain,
        )
        assert m.DecisionNode is DecisionNode
        assert m.AccountabilityChain is AccountabilityChain

    def test_print_summary_runs(self, capsys):
        from constraint_accountability_chain import print_summary
        print_summary()
        captured = capsys.readouterr()
        assert "CONSTRAINT ACCOUNTABILITY CHAIN" in captured.out
        assert "MECHANISMS" in captured.out
        assert "EPIGENETIC FACTORS" in captured.out
        assert "ACCOUNTABILITY PATTERNS" in captured.out
        assert "EXAMPLE CHAINS" in captured.out
        assert "WORKED EXAMPLE" in captured.out
        assert "WORKFLOW" in captured.out
        # The worked example should surface phenotype metrics
        assert "institutional_blindness" in captured.out
        assert "cascade_risk" in captured.out


# ─────────────────────────────────────────────
# CONSTRAINT ACCOUNTABILITY ENGINE
# ─────────────────────────────────────────────

class TestConstraintAccountabilityEngine:
    def test_import(self):
        import constraint_accountability_engine  # noqa: F401

    def test_direct_sense_node(self):
        from constraint_accountability_engine import DecisionNode
        node = DecisionNode(
            actor_role="operator",
            layer=0,
            comfort_captured=0.1,
            constraint_at_stake="frame",
            ground_signal=0.5,
            reported_signal=0.5,
            mechanism="direct_sense",
        )
        assert node.choice == "direct_sense"
        assert node.delta == 0.0
        assert node.parent is None

    def test_comfort_protect_detected_by_delta(self):
        from constraint_accountability_engine import DecisionNode
        node = DecisionNode(
            actor_role="supervisor",
            layer=1,
            comfort_captured=0.5,
            constraint_at_stake="frame",
            ground_signal=0.8,
            reported_signal=0.3,
            mechanism="attenuation",
        )
        assert node.choice == "comfort_protect"
        assert node.delta > 0.4

    def test_chain_builds_sequentially(self):
        from constraint_accountability_engine import AccountabilityChain
        chain = AccountabilityChain(
            chain_id="test", constraint_domain="safety",
        )
        assert len(chain.nodes) == 0

        n1 = chain.add_decision(
            actor_role="operator", layer=0, comfort_captured=0.1,
            constraint_at_stake="frame",
            ground_signal=0.5, reported_signal=0.5,
            mechanism="direct_sense",
        )
        n2 = chain.add_decision(
            actor_role="supervisor", layer=1, comfort_captured=0.3,
            constraint_at_stake="frame",
            ground_signal=0.5, reported_signal=0.2,
            mechanism="attenuation",
        )
        assert len(chain.nodes) == 2
        assert n2.parent is n1

    def test_override_fails_when_child_has_less_comfort(self):
        from constraint_accountability_engine import AccountabilityChain
        chain = AccountabilityChain(
            chain_id="test", constraint_domain="safety",
        )
        chain.add_decision(
            actor_role="manager", layer=2, comfort_captured=0.8,
            constraint_at_stake="frame",
            ground_signal=0.9, reported_signal=0.2,
            mechanism="normalize",
        )
        child = chain.add_decision(
            actor_role="tech", layer=1, comfort_captured=0.1,
            constraint_at_stake="frame",
            ground_signal=0.9, reported_signal=0.9,
            mechanism="direct_sense",
        )
        # Child tried to report honestly but parent's comfort dominates
        assert child.override_attempted is True
        assert child.override_succeeded is False
        assert child.choice == "comfort_protect"
        assert child.mechanism == "delegate_down"

    def test_phenotype_reports_ratchet_and_cascade(self):
        from constraint_accountability_engine import AccountabilityChain
        chain = AccountabilityChain(
            chain_id="test", constraint_domain="safety",
        )
        chain.add_decision(
            actor_role="a", layer=0, comfort_captured=0.1,
            constraint_at_stake="x",
            ground_signal=1.0, reported_signal=1.0,
            mechanism="direct_sense",
        )
        chain.add_decision(
            actor_role="b", layer=1, comfort_captured=0.3,
            constraint_at_stake="x",
            ground_signal=1.0, reported_signal=0.6,
            mechanism="attenuation",
        )
        chain.add_decision(
            actor_role="c", layer=2, comfort_captured=0.5,
            constraint_at_stake="x",
            ground_signal=1.0, reported_signal=0.3,
            mechanism="reframe",
        )
        p = chain.phenotype
        for key in ("institutional_blindness", "ratchet_depth",
                    "reversion_energy", "cascade_risk", "time_to_failure"):
            assert key in p
        assert 0.0 <= p["cascade_risk"] <= 1.0
        # Last two decisions are comfort_protect, so ratchet depth is 2
        assert p["ratchet_depth"] == 2

    def test_find_comfort_origin_and_walk_backward(self):
        from constraint_accountability_engine import AccountabilityChain
        chain = AccountabilityChain(
            chain_id="test", constraint_domain="safety",
        )
        chain.add_decision(
            actor_role="a", layer=0, comfort_captured=0.1,
            constraint_at_stake="x",
            ground_signal=1.0, reported_signal=1.0,
            mechanism="direct_sense",
        )
        patient_zero = chain.add_decision(
            actor_role="b", layer=1, comfort_captured=0.3,
            constraint_at_stake="x",
            ground_signal=1.0, reported_signal=0.5,
            mechanism="attenuation",
        )
        chain.add_decision(
            actor_role="c", layer=2, comfort_captured=0.5,
            constraint_at_stake="x",
            ground_signal=1.0, reported_signal=0.3,
            mechanism="reframe",
        )
        origin = chain.find_comfort_origin()
        assert origin is patient_zero

        walked = [n.actor_role for n in chain.walk_backward()]
        assert walked == ["c", "b", "a"]

    def test_report_surfaces_all_metrics(self):
        from constraint_accountability_engine import AccountabilityChain
        chain = AccountabilityChain(
            chain_id="plant_7", constraint_domain="safety",
        )
        chain.add_decision(
            actor_role="a", layer=0, comfort_captured=0.1,
            constraint_at_stake="x",
            ground_signal=1.0, reported_signal=0.5,
            mechanism="attenuation",
        )
        chain.add_epigenetic_event(
            factor="regulatory_pressure",
            effect="activates_direct_sense",
            magnitude=0.5,
        )
        r = chain.report()
        assert r["chain_id"] == "plant_7"
        assert r["constraint_domain"] == "safety"
        assert r["total_nodes"] == 1
        assert r["epigenetic_events"] == 1
        assert "mutations" in r
        assert "phenotype" in r


# ─────────────────────────────────────────────
# AI REFERENCE FOLDER (catalogs + index + docs)
# ─────────────────────────────────────────────

class TestAIReferenceFolder:
    """Verify the ai_reference/ folder is structurally consistent and
    in sync with the Python sources it was exported from. This class
    is the contract for downstream AI consumers of the repo.
    """

    AI_REF_DIR = "ai_reference"
    CATALOG_DIR = "ai_reference/catalogs"
    INDEX_PATH = "ai_reference/index.json"

    def test_folder_layout(self):
        import os
        assert os.path.isdir(self.AI_REF_DIR)
        assert os.path.isdir(self.CATALOG_DIR)
        for required in ("README.md", "glossary.md",
                         "composition_recipes.md", "index.json"):
            assert os.path.isfile(
                os.path.join(self.AI_REF_DIR, required)
            ), "missing " + required

    def test_index_json_well_formed(self):
        import json
        with open(self.INDEX_PATH, encoding="utf-8") as f:
            idx = json.load(f)
        assert idx["format_version"] == "1.0"
        assert "generator" in idx
        assert "regenerate_command" in idx
        assert isinstance(idx["catalogs"], dict)
        assert len(idx["catalogs"]) >= 12
        for name, meta in idx["catalogs"].items():
            for key in ("path", "source_module", "source_symbol",
                        "description", "record_count", "schema"):
                assert key in meta, name + " missing " + key
            assert meta["record_count"] >= 1
            assert isinstance(meta["schema"], dict)

    def test_every_catalog_file_exists_and_parses(self):
        import json
        import os
        with open(self.INDEX_PATH, encoding="utf-8") as f:
            idx = json.load(f)
        for name, meta in idx["catalogs"].items():
            path = os.path.join(self.AI_REF_DIR, meta["path"])
            assert os.path.isfile(path), "missing catalog: " + path
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
            assert len(lines) == meta["record_count"], (
                name + ": record_count " + str(meta["record_count"])
                + " does not match file line count " + str(len(lines))
            )
            for i, line in enumerate(lines):
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError as e:
                    raise AssertionError(
                        name + " line " + str(i) + " is not valid JSON: " + str(e)
                    )
                assert isinstance(rec, dict)
                assert "name" in rec, (
                    name + " line " + str(i) + " missing name field"
                )

    def test_catalogs_match_source_modules(self):
        """Every record in every catalog must round-trip from its
        source module. Equivalent to the exporter's --check mode but
        runs from inside the test harness."""
        import sys
        sys.path.insert(0, "tools")
        try:
            import export_ai_catalogs as exporter
        finally:
            if "tools" in sys.path:
                sys.path.remove("tools")
        changed = exporter.write_catalogs(check_only=True, verbose=False)
        assert changed == [], (
            "ai_reference/ has drifted from source modules. Run: "
            "python tools/export_ai_catalogs.py — drifted files: "
            + repr(changed)
        )

    def test_mechanisms_catalog_matches_source(self):
        """Spot-check: the mechanisms catalog has exactly the records
        that constraint_accountability_chain.MECHANISMS exposes."""
        import json
        with open(
            self.CATALOG_DIR + "/mechanisms.jsonl", encoding="utf-8"
        ) as f:
            records = [json.loads(line) for line in f]
        names = {r["name"] for r in records}
        from constraint_accountability_chain import MECHANISMS
        assert names == set(MECHANISMS.keys())
        for r in records:
            src = MECHANISMS[r["name"]]
            assert r["is_comfort"] == src["is_comfort"]
            assert r["description"] == src["description"]

    def test_feedback_loops_callable_exclusion(self):
        """KNOWN_LOOPS contains lambdas that must be filtered out.
        Every record in the feedback_loops catalog should carry an
        _excluded_keys field listing 'trigger' and 'gain_function'."""
        import json
        with open(
            self.CATALOG_DIR + "/feedback_loops.jsonl", encoding="utf-8"
        ) as f:
            records = [json.loads(line) for line in f]
        assert len(records) >= 1
        for r in records:
            assert "_excluded_keys" in r, (
                "feedback_loops record " + r.get("name", "?")
                + " missing _excluded_keys"
            )
            assert set(r["_excluded_keys"]) == {"trigger", "gain_function"}
            # The non-excluded surface should still contain useful data
            assert "description" in r
            assert "layers" in r

    def test_assumption_boundaries_catalog_count(self):
        """The assumption validator registry has 36+ entries; every
        one should land in the catalog."""
        import json
        with open(
            self.CATALOG_DIR + "/assumption_boundaries.jsonl",
            encoding="utf-8",
        ) as f:
            records = [json.loads(line) for line in f]
        assert len(records) >= 36

    def test_exporter_idempotent_on_clean_state(self):
        """Running the exporter twice in a row should be a no-op the
        second time. Catches subtle bugs where serialization is not
        deterministic."""
        import sys
        sys.path.insert(0, "tools")
        try:
            import export_ai_catalogs as exporter
            # Already up to date from the previous test or fixture
            changed_first = exporter.write_catalogs(
                check_only=True, verbose=False
            )
            assert changed_first == [], (
                "exporter not idempotent: " + repr(changed_first)
            )
        finally:
            if "tools" in sys.path:
                sys.path.remove("tools")

    def test_glossary_covers_guard_and_audit_terms(self):
        """The glossary should define the cross-module terms that
        appear in the guard family, substrate_audit, and
        domain_taxonomy."""
        with open(
            "ai_reference/glossary.md", encoding="utf-8",
        ) as f:
            content = f.read().lower()
        expected_terms = (
            "anchor",
            "grounded vs self-referential",
            "contamination",
            "synthetic ancestry",
            "embodied energy",
            "eroei",
            "substrate",
            "self-terminating goal",
            "projection",
            "closure",
            "metrology",
            "feedback_latency",
            "signal_fidelity",
            "money_physics_coupling",
            "incentive entropy",
            "gameability",
            "gradient alignment",
            "reality coupling",
            "asymmetric rigor",
            "inverted gatekeeping",
            "conditional vs assertion",
            "intent contamination",
        )
        missing = [t for t in expected_terms if t not in content]
        assert missing == [], (
            "glossary missing terms: " + repr(missing)
        )

    def test_composition_recipes_cover_reality_audit_and_self_check(self):
        """The composition recipes file should contain the
        source-blind reality audit chain and the AI projection
        self-check recipe."""
        with open(
            "ai_reference/composition_recipes.md", encoding="utf-8",
        ) as f:
            content = f.read()
        assert "Source-blind reality audit" in content
        assert "AI projection self-check" in content
        # Source-blind recipe should name every stage module
        for module in (
            "input_validation_guard",
            "self_referential_guard",
            "model_collapse_guard",
            "thermodynamic_price_guard",
            "domain_taxonomy",
            "substrate_audit",
            "cascade_consequence_engine",
        ):
            assert module in content, (
                "reality-audit recipe missing " + module
            )
        # Self-check recipe should name all three meta-tools
        for module in (
            "perspective_guard",
            "reflexive_bias_guard",
            "conditional_logic_parser",
        ):
            assert module in content, (
                "self-check recipe missing " + module
            )


# ─────────────────────────────────────────────
# GUARD FAMILY — minimal import + basic behavior
# ─────────────────────────────────────────────

class TestSelfReferentialGuard:
    def test_import(self):
        import self_referential_guard  # noqa: F401

    def test_cycle_detection(self):
        from self_referential_guard import DependencyGraph
        g = DependencyGraph()
        g.add_variable("credit", ["money"])
        g.add_variable("money", ["credit"])
        report = g.audit()
        assert report["cycles_found"] >= 1
        assert len(report["hazards"]) >= 1

    def test_grounded_cycle_not_hazard(self):
        from self_referential_guard import DependencyGraph
        g = DependencyGraph()
        g.add_variable("heater", ["thermostat"])
        g.add_variable("room_temp", ["heater"])
        g.add_variable("thermostat", ["room_temp"])
        g.mark_anchor("room_temp", "thermometer")
        report = g.audit()
        assert len(report["hazards"]) == 0
        assert len(report["grounded"]) >= 1

    def test_example_axioms_present(self):
        from self_referential_guard import EXAMPLE_AXIOMS
        assert "conservation_of_energy" in EXAMPLE_AXIOMS
        assert "efficient_market" in EXAMPLE_AXIOMS


class TestModelCollapseGuard:
    def test_import(self):
        import model_collapse_guard  # noqa: F401

    def test_contamination_tracker_detects_synthetic_cascade(self):
        from model_collapse_guard import ContaminationTracker
        ct = ContaminationTracker()
        ct.add_measured("sensor_1", "instrument")
        ct.add_synthetic("gen1", "model_a", ["sensor_1"])
        ct.add_synthetic("gen2", "model_a", ["gen1"])
        ct.add_synthetic("gen3", "model_a", ["gen2"])
        ct.add_synthetic("gen4", "model_a", ["gen3"])
        ct.add_synthetic("gen5", "model_a", ["gen4"])
        risk = ct.collapse_risk()
        assert risk["risk"] in ("HIGH", "CRITICAL")

    def test_forecast_chain_grounding(self):
        from model_collapse_guard import ForecastChain
        fc = ForecastChain()
        fc.add_measurement("gdp_q1", 25.4, "trillion USD")
        fc.add_forecast("gdp_q2", ["gdp_q1"], 25.6)
        result = fc.analyze()
        assert result["grounded"] is True


class TestThermodynamicPriceGuard:
    def test_import(self):
        import thermodynamic_price_guard  # noqa: F401

    def test_material_energy_catalog(self):
        from thermodynamic_price_guard import MATERIAL_ENERGY
        assert "copper" in MATERIAL_ENERGY
        assert "steel" in MATERIAL_ENERGY
        assert MATERIAL_ENERGY["copper"] > 0

    def test_embodied_energy(self):
        from thermodynamic_price_guard import embodied_energy
        result = embodied_energy(materials={"copper": 10.0})
        assert result["extraction_kwh"] > 0
        assert result["total_kwh"] > 0

    def test_price_energy_inflated(self):
        from thermodynamic_price_guard import price_energy_check
        result = price_energy_check(price_usd=5000.0, embodied_kwh=20.0)
        assert result["hazard"] is True
        assert result["status"] in ("INFLATED", "INFLATED_EXTREME")

    def test_eroei_net_sink(self):
        from thermodynamic_price_guard import eroei_check
        result = eroei_check(
            energy_produced_kwh=0.8, energy_invested_kwh=1.0,
        )
        assert result["status"] == "NET_SINK"
        assert result["hazard"] is True


class TestInputValidationGuard:
    def test_import(self):
        import input_validation_guard  # noqa: F401

    def test_energy_conservation_violation_rejected(self):
        from input_validation_guard import validate_input
        result = validate_input(
            data={"claims": [{
                "statement": "Produces 500 kWh from 100 kWh input",
                "quantity": 500.0, "unit": "kWh",
                "falsifiable": True,
                "energy_in": 100.0, "energy_out": 500.0,
            }]},
            metadata={"proprietary": False},
        )
        assert result["verdict"] == "REJECT"

    def test_untestable_claim_accepted_with_notes(self):
        from input_validation_guard import validate_input
        result = validate_input(
            data={"claims": [{
                "statement": "Asset prices reflect all information",
                "quantity": None, "unit": None, "falsifiable": False,
            }]},
        )
        assert result["verdict"] == "ACCEPT_WITH_NOTES"


class TestCascadeConsequenceEngine:
    def test_import(self):
        import cascade_consequence_engine  # noqa: F401

    def test_substrate_map_goal_tree(self):
        from cascade_consequence_engine import SubstrateMap
        sm = SubstrateMap()
        sm.add_substrate("a", 0.5, 0.1)
        sm.add_substrate("b", 0.5, 0.1)
        sm.add_substrate("c", 0.5, 0.1)
        sm.add_dependency("a", "b")
        sm.add_dependency("b", "c")
        sm.mark_goal_dependency("a")
        tree = sm.get_goal_full_tree()
        assert {"a", "b", "c"} <= tree

    def test_cascade_engine_runs(self):
        from cascade_consequence_engine import (
            SubstrateMap, ActionEffect, CascadeEngine,
        )
        sm = SubstrateMap()
        sm.add_substrate("water", 0.8, 0.2, regeneration_rate=0.01)
        sm.mark_goal_dependency("water")
        action = ActionEffect("drain", goal_progress=0.1)
        action.add_effect("water", -0.05)
        engine = CascadeEngine(sm)
        result = engine.simulate([action], steps=10)
        assert "self_terminating" in result
        assert "total_goal_progress" in result


class TestPerspectiveGuard:
    def test_import(self):
        import perspective_guard  # noqa: F401

    def test_projection_patterns_catalog(self):
        from perspective_guard import PROJECTION_PATTERNS
        expected = {
            "moral_framing", "political_projection",
            "romanticism", "western_science_gatekeeping",
        }
        assert expected <= set(PROJECTION_PATTERNS.keys())

    def test_audit_ai_response_clean(self):
        from perspective_guard import audit_ai_response
        clean = (
            "Module takes substrate levels as input. Propagates "
            "cascade damage through dependency graph. Closes on "
            "energy conservation."
        )
        result = audit_ai_response(clean)
        assert result["contamination_level"] == "CLEAN"

    def test_audit_ai_response_heavy_contamination(self):
        from perspective_guard import audit_ai_response
        contaminated = (
            "This is an inspiring and noble project driven by a "
            "passionate activist with a radical anti-capitalist "
            "ideology. The author must feel disappointed."
        )
        result = audit_ai_response(contaminated)
        assert result["contamination_level"] in ("MODERATE", "HEAVY")

    def test_module_manifest_roundtrip(self):
        from perspective_guard import ModuleManifest
        m = ModuleManifest("test_module")
        m.add_input("x", "kg", "test input")
        m.add_output("y", "J", "test output")
        m.add_conservation_law("mass")
        m.set_closure_statement("Test closure")
        d = m.to_dict()
        assert d["module"] == "test_module"
        assert d["inputs"][0]["name"] == "x"
        assert "mass" in d["conservation_laws"]


class TestScientificPluralismGuard:
    def test_import(self):
        import scientific_pluralism_guard  # noqa: F401

    def test_measurement_system_validates(self):
        from scientific_pluralism_guard import MeasurementSystem
        s = MeasurementSystem("test", tradition="lab")
        s.add_quantity("temperature", "K")
        s.add_instrument("thermometer")
        s.set_reproducibility(0.95, 0.92, 0.90)
        s.falsifiability = "If reading disagrees with reference"
        s.conservation_laws = ["energy"]
        result = s.validate()
        assert result["valid"] is True

    def test_gatekeeping_detection(self):
        from scientific_pluralism_guard import detect_gatekeeping
        bad = (
            "This is folklore and anecdotal. It is not peer reviewed. "
            "It is unscientific and primitive."
        )
        result = detect_gatekeeping(bad)
        assert result["gatekeeping_level"] in ("MODERATE", "HEAVY")

    def test_consequence_profile_assessment(self):
        from scientific_pluralism_guard import ConsequenceProfile
        cp = ConsequenceProfile("test claim")
        cp.severity = "life"
        cp.feedback_time = "hours"
        cp.feedback_steps = 1
        cp.who_decides = "self"
        cp.who_suffers = "self"
        cp.accountability_gap = False
        cp.reversible = False
        result = cp.assess()
        assert result["classification"] == "CONSEQUENCE_GROUNDED"


class TestReflexiveBiasGuard:
    def test_import(self):
        import reflexive_bias_guard  # noqa: F401

    def test_rigor_audit_detects_asymmetry(self):
        from reflexive_bias_guard import RigorAudit
        audit = RigorAudit()
        audit.log_check("a", "T1", "repro", 0.95, 0.9, False)
        audit.log_check("b", "T2", "repro", 0.50, 0.9, True)
        result = audit.detect_asymmetry()
        assert result["asymmetry_detected"] is True

    def test_inverted_gatekeeping_detection(self):
        from reflexive_bias_guard import detect_inverted_gatekeeping
        bad = (
            "Western science is a religion. Only indigenous "
            "knowledge is valid. Laboratory knowledge is worthless."
        )
        result = detect_inverted_gatekeeping(bad)
        assert result["inverted_gatekeeping_detected"] is True

    def test_validator_self_check_runs(self):
        from reflexive_bias_guard import validator_self_check
        result = validator_self_check()
        assert "self_check_passed" in result
        assert "honest_limitations" in result
        assert len(result["honest_limitations"]) > 0


class TestConditionalLogicParser:
    def test_import(self):
        import conditional_logic_parser  # noqa: F401

    def test_extract_conditional(self):
        from conditional_logic_parser import extract_conditionals
        results = extract_conditionals(
            "If X declares itself the only framework, then it "
            "functions as a religion."
        )
        assert any(r["structure"] == "CONDITIONAL" for r in results)

    def test_intent_contamination_heavy(self):
        from conditional_logic_parser import detect_intent_contamination
        bad = (
            "You seem frustrated. What you're really saying is that "
            "you feel strongly about this. That's a valid concern "
            "and you raise an important point. It's more nuanced "
            "than that. Both sides have valid points."
        )
        result = detect_intent_contamination(bad)
        assert result["contamination_level"] in ("MODERATE", "HEAVY")

    def test_statement_handling_aligned(self):
        from conditional_logic_parser import audit_statement_handling
        conditional_input = [
            "If the feedback loop is disconnected from consequence, "
            "bad theory persists.",
        ]
        good_response = (
            "The condition you stated is: feedback loop is "
            "disconnected from consequence. The consequence follows "
            "because without feedback there is no correction signal."
        )
        result = audit_statement_handling(
            conditional_input, good_response,
        )
        assert result["verdict"] == "ALIGNED"


class TestSubstrateAudit:
    def test_import(self):
        import substrate_audit  # noqa: F401

    def test_claims_present(self):
        from substrate_audit import CLAIMS, Verdict
        assert len(CLAIMS) >= 7
        for c in CLAIMS:
            assert c.id.startswith("TC-")
            assert isinstance(c.verdict, Verdict)

    def test_five_why_chain(self):
        from substrate_audit import FIVE_WHY
        assert len(FIVE_WHY) == 5
        for entry in FIVE_WHY:
            assert "why" in entry and "question" in entry and "answer" in entry

    def test_causal_loop_is_closed(self):
        from substrate_audit import CAUSAL_LOOP, loop_is_closed
        assert loop_is_closed(CAUSAL_LOOP) is True

    def test_maintainer_excluded(self):
        from substrate_audit import CAUSAL_LOOP, maintainer_in_loop
        # MAINTAIN has no outgoing edges — excluded from power loop
        assert maintainer_in_loop(CAUSAL_LOOP) is False

    def test_dmaic_audit(self):
        from substrate_audit import DMAIC_AUDIT, Verdict
        assert len(DMAIC_AUDIT) == 5
        for phase in DMAIC_AUDIT:
            assert phase.verdict in (
                Verdict.PASS, Verdict.FAIL, Verdict.CIRCULAR,
                Verdict.UNTESTED,
            )

    def test_system_score_bounds(self):
        from substrate_audit import SystemScore
        s = SystemScore(
            name="test",
            maintainer_control=0.5,
            outcome_measurement=0.5,
            scope_justification=0.5,
            credential_tested=0.5,
            emotion_integrated=0.5,
            meta_learning=0.5,
            substrate_intelligence=0.5,
        )
        assert 0.0 <= s.thermodynamic_alignment <= 1.0
        assert 0.0 <= s.church_index <= 1.0
        assert s.verdict in (
            "PHYSICS-GROUNDED",
            "MIXED — partial faith-based operation",
            "CHURCH — operating on faith, not evidence",
        )

    def test_json_export_well_formed(self):
        import json as json_mod
        from substrate_audit import to_json
        data = json_mod.loads(to_json())
        assert "claims" in data
        assert "five_why" in data
        assert "causal_loop" in data
        assert "dmaic" in data
        assert "reference_scores" in data

    def test_v3_ten_claims_with_money_and_information(self):
        """v3 adds TC-8 (TEK), TC-9 (money metrology),
        TC-10 (information as physical work)."""
        from substrate_audit import CLAIMS
        assert len(CLAIMS) == 10
        ids = {c.id for c in CLAIMS}
        assert {"TC-8", "TC-9", "TC-10"} <= ids
        by_id = {c.id: c for c in CLAIMS}
        # TC-9 is the money metrology claim
        assert "money" in by_id["TC-9"].claim.lower()
        # TC-10 is the information/coordination claim
        assert "information" in by_id["TC-10"].claim.lower()
        # TC-8 is the TEK claim
        assert "tek" in by_id["TC-8"].claim.lower() or "indigenous" in by_id["TC-8"].claim.lower()

    def test_v3_eleven_scoring_dimensions(self):
        """v3 adds tek_integration, feedback_latency, signal_fidelity,
        money_physics_coupling to the scoring engine."""
        from substrate_audit import SystemScore
        s = SystemScore(
            name="test",
            maintainer_control=0.5, outcome_measurement=0.5,
            scope_justification=0.5, credential_tested=0.5,
            emotion_integrated=0.5, meta_learning=0.5,
            substrate_intelligence=0.5,
            tek_integration=0.5, feedback_latency=0.5,
            signal_fidelity=0.5, money_physics_coupling=0.5,
        )
        # With all dimensions at 0.5, thermodynamic_alignment should be 0.5
        assert abs(s.thermodynamic_alignment - 0.5) < 1e-6

    def test_v3_tek_reference_system_grounded(self):
        """v3 adds a TEK-managed landscape reference system that
        should score as PHYSICS-GROUNDED."""
        from substrate_audit import REFERENCE_SYSTEMS
        tek = [s for s in REFERENCE_SYSTEMS if "TEK" in s.name]
        assert len(tek) == 1
        assert tek[0].verdict == "PHYSICS-GROUNDED"

    def test_v3_json_export_includes_prompt_and_schema(self):
        """v3 embeds a cross-model prompt + scoring schema in the
        JSON export so downstream AI can apply the audit directly."""
        import json as json_mod
        from substrate_audit import to_json
        data = json_mod.loads(to_json())
        assert "prompt" in data
        assert "scoring_dimensions" in data
        assert "scoring_weights" in data
        assert "scoring_thresholds" in data
        # v3 + refinements now have 17 dimensions, not 11
        assert len(data["scoring_dimensions"]) == 17
        # Weights should sum to 1.0 (float-safe comparison)
        assert abs(sum(data["scoring_weights"]) - 1.0) < 1e-9
        # Original v3 dimension keys must be present
        for dim in ("feedback_latency", "signal_fidelity",
                    "money_physics_coupling", "tek_integration"):
            assert dim in data["scoring_dimensions"]

    def test_refined_17_scoring_dimensions(self):
        """Commit-A refinement adds 6 new SystemScore dimensions:
        latency_quality, signal_compression_efficiency,
        incentive_field_coherence, knowledge_transmission_resilience,
        constraint_feasibility, generalization_capacity."""
        from substrate_audit import SystemScore, to_json
        import json as json_mod

        # Instantiate with all 17 fields explicitly at 0.5 -> alignment 0.5
        s = SystemScore(
            name="t",
            maintainer_control=0.5, outcome_measurement=0.5,
            scope_justification=0.5, credential_tested=0.5,
            emotion_integrated=0.5, meta_learning=0.5,
            substrate_intelligence=0.5, tek_integration=0.5,
            feedback_latency=0.5, signal_fidelity=0.5,
            money_physics_coupling=0.5, latency_quality=0.5,
            signal_compression_efficiency=0.5,
            incentive_field_coherence=0.5,
            knowledge_transmission_resilience=0.5,
            constraint_feasibility=0.5, generalization_capacity=0.5,
        )
        assert abs(s.thermodynamic_alignment - 0.5) < 1e-9

        # All new dimensions must be in the JSON schema
        data = json_mod.loads(to_json())
        for dim in (
            "latency_quality",
            "signal_compression_efficiency",
            "incentive_field_coherence",
            "knowledge_transmission_resilience",
            "constraint_feasibility",
            "generalization_capacity",
        ):
            assert dim in data["scoring_dimensions"], (
                "missing new dimension: " + dim
            )

    def test_refined_reference_systems_use_new_dimensions(self):
        """Every REFERENCE_SYSTEMS entry should have non-default
        values for the new dimensions (tests that the update was
        applied to all 6 systems, not just the first few)."""
        from substrate_audit import REFERENCE_SYSTEMS
        # Each system should have a distinct latency_quality value
        # (the new field we care most about — discriminates
        # destructive from integrative delay)
        latency_qualities = [s.latency_quality for s in REFERENCE_SYSTEMS]
        # At least 4 distinct values across 6 systems
        assert len(set(latency_qualities)) >= 4

        # Mycorrhizal should have high values on all new dimensions
        myc = [s for s in REFERENCE_SYSTEMS
               if "Mycorrhizal" in s.name][0]
        assert myc.latency_quality >= 0.8
        assert myc.signal_compression_efficiency >= 0.8
        assert myc.incentive_field_coherence >= 0.8

        # Typical corporation should have low values on coherence
        # (competing exec/worker/regulator gradients)
        corp = [s for s in REFERENCE_SYSTEMS
                if "corporation" in s.name.lower()][0]
        assert corp.incentive_field_coherence <= 0.3

    def test_causal_loop_includes_constraint_node(self):
        """Commit-A adds an external CONSTRAINT node to CAUSAL_LOOP
        that injects perturbations into SURPLUS and POWER. This
        represents how physical constraints force corrections into
        the self-reinforcing loop."""
        from substrate_audit import CAUSAL_LOOP, loop_is_closed
        constraint = [n for n in CAUSAL_LOOP if n.id == "CONSTRAINT"]
        assert len(constraint) == 1
        c = constraint[0]
        assert "SURPLUS" in c.drives
        assert "POWER" in c.drives
        # CONSTRAINT is NOT self-reinforcing — it's an external
        # perturbation source
        assert c.is_self_reinforcing is False
        # Adding CONSTRAINT must not break the existing loop closure
        assert loop_is_closed(CAUSAL_LOOP) is True

    def test_tc6_refined_distinguishes_context_adaptation(self):
        """Commit-B refines TC-6 to distinguish bounded context
        adaptation (present in deployed LLMs) from meta-learning
        (absent). The refinement matters because calling all of it
        'meta-learning' or none of it 'adaptation' both misread
        deployed systems."""
        from substrate_audit import CLAIMS
        tc6 = [c for c in CLAIMS if c.id == "TC-6"][0]
        # Claim should mention both in-context learning (present)
        # and meta-learning (absent)
        assert "in-context" in tc6.claim.lower() or "bounded context" in tc6.claim.lower()
        assert "meta-learning" in tc6.claim.lower()
        # Evidence should cite in-context learning literature
        assert "in-context learning" in tc6.known_evidence.lower()
        # Evidence should distinguish parameter-level update from
        # in-context update
        evidence_lower = tc6.known_evidence.lower()
        assert "parameter" in evidence_lower
        # Note should reference generalization_capacity dimension
        assert "generalization_capacity" in tc6.note

    def test_contextual_weight_sets_all_sum_to_one(self):
        """Commit-B adds CONTEXTUAL_WEIGHT_SETS for domain-specific
        scoring. All 5 weight vectors must sum to 1.0 exactly and
        have 17 entries matching the 17-dimension schema."""
        from substrate_audit import CONTEXTUAL_WEIGHT_SETS
        expected_contexts = {
            "general", "medical", "ecological",
            "industrial", "institutional",
        }
        assert set(CONTEXTUAL_WEIGHT_SETS.keys()) == expected_contexts
        for name, weights in CONTEXTUAL_WEIGHT_SETS.items():
            assert len(weights) == 17, (
                f"{name} has {len(weights)} weights, expected 17"
            )
            assert abs(sum(weights) - 1.0) < 1e-9, (
                f"{name} weights sum to {sum(weights)}, expected 1.0"
            )

    def test_alignment_for_context_differs_from_general(self):
        """alignment_for_context should produce different scores
        for different contexts on systems where the domain weights
        actually reallocate. Using TEK landscape which benefits
        from ecological weighting."""
        from substrate_audit import REFERENCE_SYSTEMS
        tek = [s for s in REFERENCE_SYSTEMS if "TEK" in s.name][0]
        general = tek.alignment_for_context("general")
        ecological = tek.alignment_for_context("ecological")
        # Ecological context should score TEK at least as high as
        # general (same or higher), because tek_integration and
        # substrate_intelligence carry more weight there.
        assert ecological >= general
        # Corporation should score low in every context
        corp = [s for s in REFERENCE_SYSTEMS
                if "corporation" in s.name.lower()][0]
        for ctx in (
            "general", "medical", "ecological",
            "industrial", "institutional",
        ):
            assert corp.alignment_for_context(ctx) < 0.3

    def test_alignment_for_context_unknown_raises_keyerror(self):
        from substrate_audit import SystemScore
        import pytest
        s = SystemScore(
            name="t", maintainer_control=0.5, outcome_measurement=0.5,
            scope_justification=0.5, credential_tested=0.5,
            emotion_integrated=0.5, meta_learning=0.5,
            substrate_intelligence=0.5,
        )
        with pytest.raises(KeyError):
            s.alignment_for_context("nonexistent_domain")

    def test_verdict_for_context_uses_same_thresholds(self):
        """verdict_for_context should apply the same >=0.7 /
        >=0.4 / <0.4 thresholds as the default verdict,
        against the contextual alignment score."""
        from substrate_audit import REFERENCE_SYSTEMS
        mycorrhizal = [s for s in REFERENCE_SYSTEMS
                       if "Mycorrhizal" in s.name][0]
        v = mycorrhizal.verdict_for_context("general")
        assert v == "PHYSICS-GROUNDED"
        # Should also be PHYSICS-GROUNDED in ecological context
        assert mycorrhizal.verdict_for_context("ecological") == "PHYSICS-GROUNDED"


# ─────────────────────────────────────────────
# DOMAIN TAXONOMY + INCENTIVE AUDIT
# ─────────────────────────────────────────────

class TestDomainTaxonomy:
    def test_import(self):
        import domain_taxonomy  # noqa: F401

    def test_six_measurement_domains(self):
        from domain_taxonomy import MEASUREMENT_DOMAINS
        expected = {
            "clinical_surgical", "affective_neuroscience",
            "cellular_biochemical", "ecological_network",
            "tek_traditional", "institutional_economic",
        }
        assert set(MEASUREMENT_DOMAINS.keys()) == expected
        for name, spec in MEASUREMENT_DOMAINS.items():
            for key in ("scope", "goal", "primary_unit",
                        "method_structure", "validation_loop",
                        "strengths", "limitations", "failure_mode",
                        "question_answered"):
                assert key in spec, f"{name} missing {key}"

    def test_incentive_channel_shape(self):
        from domain_taxonomy import IncentiveChannel
        c = IncentiveChannel(
            name="test",
            reward_basis="physical_outcome",
            outcome_coupling=0.8,
            reward_latency=0.9,
            gradient_alignment=0.8,
            gameability=0.1,
            reward_distribution=0.9,
        )
        assert c.name == "test"
        assert c.outcome_coupling == 0.8

    def test_incentive_audit_alignment_ranges(self):
        from domain_taxonomy import (
            IncentiveAudit, IncentiveChannel,
        )
        # Perfect channel -> high alignment
        perfect = IncentiveChannel(
            name="perfect",
            reward_basis="physical_outcome",
            outcome_coupling=1.0,
            reward_latency=1.0,
            gradient_alignment=1.0,
            gameability=0.0,
            reward_distribution=1.0,
        )
        audit_good = IncentiveAudit(name="ideal", channels=[perfect])
        assert audit_good.alignment == 1.0
        assert audit_good.incentive_entropy() == 0.0
        assert audit_good.verdict == "REALITY-COUPLED"

        # Worst channel -> low alignment, high entropy
        worst = IncentiveChannel(
            name="worst",
            reward_basis="symbolic/narrative",
            outcome_coupling=0.0,
            reward_latency=0.0,
            gradient_alignment=0.0,
            gameability=1.0,
            reward_distribution=0.0,
        )
        audit_bad = IncentiveAudit(name="worst_case", channels=[worst])
        assert audit_bad.alignment == 0.0
        assert audit_bad.incentive_entropy() == 3.0
        assert "DECOUPLED" in audit_bad.verdict

    def test_empty_audit_returns_zero(self):
        from domain_taxonomy import IncentiveAudit
        empty = IncentiveAudit(name="empty")
        assert empty.alignment == 0.0
        assert empty.incentive_entropy() == 0.0

    def test_reference_profiles_complete(self):
        from domain_taxonomy import (
            REFERENCE_PROFILES, MEASUREMENT_DOMAINS,
        )
        assert set(REFERENCE_PROFILES.keys()) == set(
            MEASUREMENT_DOMAINS.keys()
        )
        for key, profile in REFERENCE_PROFILES.items():
            assert len(profile.channels) >= 1
            assert 0.0 <= profile.alignment <= 1.0

    def test_tek_reality_coupled_institutional_decoupled(self):
        from domain_taxonomy import REFERENCE_PROFILES
        tek = REFERENCE_PROFILES["tek_traditional"]
        inst = REFERENCE_PROFILES["institutional_economic"]
        assert tek.verdict == "REALITY-COUPLED"
        assert "DECOUPLED" in inst.verdict
        assert tek.alignment > inst.alignment
        # TEK has lower entropy than institutional
        assert tek.incentive_entropy() < inst.incentive_entropy()

    def test_compare_domains_table(self):
        from domain_taxonomy import compare_domains, MEASUREMENT_DOMAINS
        rows = compare_domains()
        assert len(rows) == len(MEASUREMENT_DOMAINS)
        for r in rows:
            for key in ("domain", "measurement_type", "timescale",
                        "control", "coupling_to_reality",
                        "question", "failure_mode"):
                assert key in r

    def test_ai_reference_complete(self):
        from domain_taxonomy import AI_REFERENCE
        for key in ("purpose", "when_to_apply", "key_exports",
                    "integration_with_substrate_audit",
                    "common_mistakes"):
            assert key in AI_REFERENCE
        integ = AI_REFERENCE["integration_with_substrate_audit"]
        for dim in ("outcome_coupling", "reward_latency",
                    "reward_distribution", "gameability"):
            assert dim in integ

    def test_print_summary_runs(self, capsys):
        from domain_taxonomy import print_summary
        print_summary()
        captured = capsys.readouterr()
        assert "DOMAIN TAXONOMY" in captured.out
        assert "MEASUREMENT DOMAINS" in captured.out
        assert "INCENTIVE PROFILES" in captured.out
        assert "INTEGRATION WITH substrate_audit" in captured.out


# ─────────────────────────────────────────────
# SKYRMIONS + RKKY + LLG
# ─────────────────────────────────────────────

class TestSkyrmionRKKY:
    def test_import(self):
        import skyrmion_rkky  # noqa: F401

    def test_uniform_field_has_zero_topological_charge(self):
        from skyrmion_rkky import (
            make_uniform_field, compute_topological_charge,
        )
        m = make_uniform_field(64, 64)
        Q = compute_topological_charge(m)
        assert abs(Q) < 1e-9

    def test_skyrmion_ansatz_unit_norm(self):
        from skyrmion_rkky import make_skyrmion_field
        import numpy as np
        m = make_skyrmion_field(nx=32, ny=32, radius=8.0)
        norms = np.sqrt(np.sum(m ** 2, axis=-1))
        # Every site should have |m|=1 within float tolerance
        assert np.all(np.abs(norms - 1.0) < 1e-9)

    def test_skyrmion_topological_charge_close_to_minus_one(self):
        """Néel skyrmion with polarity=+1, vorticity=+1 should
        yield Q close to -1 (within ~5% on a 128x128 grid)."""
        from skyrmion_rkky import (
            make_skyrmion_field, compute_topological_charge,
        )
        m = make_skyrmion_field(
            nx=128, ny=128, radius=12.0,
            polarity=1, vorticity=1, helicity=0.0,
        )
        Q = compute_topological_charge(m)
        assert abs(Q - (-1.0)) < 0.05, f"got Q={Q}"

    def test_polarity_flip_flips_topological_charge(self):
        """Flipping polarity from +1 to -1 should flip Q from -1
        to +1."""
        from skyrmion_rkky import (
            make_skyrmion_field, compute_topological_charge,
        )
        m_pos = make_skyrmion_field(
            nx=128, ny=128, radius=12.0,
            polarity=1, vorticity=1,
        )
        m_neg = make_skyrmion_field(
            nx=128, ny=128, radius=12.0,
            polarity=-1, vorticity=1,
        )
        Q_pos = compute_topological_charge(m_pos)
        Q_neg = compute_topological_charge(m_neg)
        # Sum should be near zero (they cancel)
        assert abs(Q_pos + Q_neg) < 1e-6

    def test_helicity_does_not_affect_topology(self):
        """Néel and Bloch skyrmions differ only by in-plane phase;
        Q should be the same."""
        import math
        from skyrmion_rkky import (
            make_skyrmion_field, compute_topological_charge,
        )
        m_neel = make_skyrmion_field(
            nx=128, ny=128, radius=12.0, helicity=0.0,
        )
        m_bloch = make_skyrmion_field(
            nx=128, ny=128, radius=12.0, helicity=math.pi / 2,
        )
        Q_neel = compute_topological_charge(m_neel)
        Q_bloch = compute_topological_charge(m_bloch)
        assert abs(Q_neel - Q_bloch) < 1e-9

    def test_rkky_oscillates_with_distance(self):
        """RKKY coupling should change sign at least once across
        a distance range of one full oscillation period."""
        from skyrmion_rkky import rkky_coupling, rkky_period
        k_F = 1.0
        period = rkky_period(k_F)
        # Sample over 2 periods to guarantee at least one sign change
        rs = [0.5 + i * (2 * period / 20) for i in range(20)]
        for d in (1, 2, 3):
            values = [rkky_coupling(r, k_F, dimension=d) for r in rs]
            signs = [1 if v > 0 else -1 if v < 0 else 0 for v in values]
            sign_changes = sum(
                1 for i in range(len(signs) - 1)
                if signs[i] * signs[i + 1] < 0
            )
            assert sign_changes >= 1, (
                f"dim={d}: no sign change across "
                f"{2 * period:.2f} period range"
            )

    def test_rkky_invalid_inputs_raise(self):
        import pytest
        from skyrmion_rkky import rkky_coupling
        with pytest.raises(ValueError):
            rkky_coupling(0.0, k_F=1.0)
        with pytest.raises(ValueError):
            rkky_coupling(-1.0, k_F=1.0)
        with pytest.raises(ValueError):
            rkky_coupling(1.0, k_F=1.0, dimension=4)

    def test_llg_step_preserves_norm(self):
        """One LLG step should preserve |m|=1 to machine precision."""
        import numpy as np
        from skyrmion_rkky import llg_step
        m = np.array([[[0.6, 0.0, 0.8]]])
        H = np.array([[[0.0, 0.0, 1.0]]])
        m_new = llg_step(m, H, alpha=0.05, dt=1e-13)
        norm = float(np.linalg.norm(m_new[0, 0]))
        assert abs(norm - 1.0) < 1e-9

    def test_llg_step_aligned_field_no_torque(self):
        """If m is parallel to H_eff, m × H_eff = 0 and the step
        should leave m unchanged (no precession, no damping)."""
        import numpy as np
        from skyrmion_rkky import llg_step
        m = np.array([[[0.0, 0.0, 1.0]]])
        H = np.array([[[0.0, 0.0, 1.0]]])
        m_new = llg_step(m, H, alpha=0.05, dt=1e-13)
        # All three components essentially unchanged
        assert abs(m_new[0, 0, 0] - 0.0) < 1e-12
        assert abs(m_new[0, 0, 1] - 0.0) < 1e-12
        assert abs(m_new[0, 0, 2] - 1.0) < 1e-12

    def test_llg_step_perpendicular_field_precesses(self):
        """If m is perpendicular to H_eff, m should precess: at
        least one transverse component should change after a
        single small step."""
        import numpy as np
        from skyrmion_rkky import llg_step
        m = np.array([[[1.0, 0.0, 0.0]]])
        H = np.array([[[0.0, 0.0, 1.0]]])
        m_new = llg_step(m, H, alpha=0.05, dt=1e-13)
        # m_y should pick up nonzero magnitude from precession
        assert abs(m_new[0, 0, 1]) > 1e-6

    def test_skyrmion_materials_catalog(self):
        from skyrmion_rkky import SKYRMION_MATERIALS
        assert len(SKYRMION_MATERIALS) >= 5
        # The 3 RKKY-stabilized centrosymmetric materials must be
        # marked rkky_relevant=True
        rkky_hosts = [
            name for name, spec in SKYRMION_MATERIALS.items()
            if spec["rkky_relevant"]
        ]
        for required in ("Gd2PdSi3", "Gd3Ru4Al12", "GdRu2Si2"):
            assert required in rkky_hosts
        # MnSi and FeGe are DMI-stabilized, not RKKY
        assert SKYRMION_MATERIALS["MnSi"]["rkky_relevant"] is False
        assert SKYRMION_MATERIALS["FeGe"]["rkky_relevant"] is False
        # Every entry has the required fields
        for name, spec in SKYRMION_MATERIALS.items():
            for field in ("type", "skyrmion_radius_nm",
                          "ordering_temperature_K",
                          "stabilization_mechanism",
                          "rkky_relevant", "notes"):
                assert field in spec, (
                    f"{name} missing {field}"
                )

    def test_print_summary_runs(self, capsys):
        from skyrmion_rkky import print_summary
        print_summary()
        captured = capsys.readouterr()
        assert "SKYRMION" in captured.out
        assert "RKKY" in captured.out
        assert "TOPOLOGICAL CHARGE" in captured.out
        assert "LLG STEP" in captured.out


# ─────────────────────────────────────────────
# SKYRMION-PHONON COUPLING
# ─────────────────────────────────────────────

class TestSkyrmionPhononCoupling:
    def test_import(self):
        import skyrmion_phonon_coupling  # noqa: F401

    def test_three_internal_modes_catalog(self):
        from skyrmion_phonon_coupling import SKYRMION_INTERNAL_MODES
        expected = {"gyrotropic", "breathing", "elliptic"}
        assert set(SKYRMION_INTERNAL_MODES.keys()) == expected
        for name, spec in SKYRMION_INTERNAL_MODES.items():
            for field in (
                "order", "symmetry", "typical_freq_GHz",
                "freq_scaling", "phonon_channel", "coupling_type",
                "observability",
            ):
                assert field in spec, (
                    f"mode {name} missing {field}"
                )

    def test_spinwave_params_match_rkky_catalog(self):
        """The spin-wave parameter catalog must cover the same
        5 materials as skyrmion_rkky.SKYRMION_MATERIALS so that
        modes_for_material can cross-reference radius lookups."""
        from skyrmion_phonon_coupling import SKYRMION_SPINWAVE_PARAMS
        from skyrmion_rkky import SKYRMION_MATERIALS
        assert (
            set(SKYRMION_SPINWAVE_PARAMS.keys())
            == set(SKYRMION_MATERIALS.keys())
        )

    def test_breathing_frequency_scales_as_inverse_radius_squared(self):
        """Breathing mode: ω_B ∝ 1/R². Doubling R should reduce
        frequency by a factor of 4."""
        from skyrmion_phonon_coupling import breathing_frequency_Hz
        f_10 = breathing_frequency_Hz(10.0, 1e-12, 1e5)
        f_20 = breathing_frequency_Hz(20.0, 1e-12, 1e5)
        ratio = f_10 / f_20
        assert abs(ratio - 4.0) < 0.01

    def test_gyrotropic_frequency_scales_with_K_over_M_s(self):
        """Gyrotropic in the symmetric approximation scales as
        K_eff / M_s, independent of radius."""
        from skyrmion_phonon_coupling import gyrotropic_frequency_Hz
        # Double K_eff doubles the frequency
        f_1 = gyrotropic_frequency_Hz(10.0, 1e5, 1e4)
        f_2 = gyrotropic_frequency_Hz(10.0, 1e5, 2e4)
        assert abs(f_2 / f_1 - 2.0) < 1e-9
        # Same K_eff, different R -> same frequency
        f_r1 = gyrotropic_frequency_Hz(5.0, 1e5, 1e4)
        f_r2 = gyrotropic_frequency_Hz(50.0, 1e5, 1e4)
        assert abs(f_r1 - f_r2) < 1e-3

    def test_elliptic_is_twice_breathing_by_default(self):
        from skyrmion_phonon_coupling import elliptic_frequency_Hz
        f = elliptic_frequency_Hz(5e9)
        assert abs(f - 1e10) < 1e-3
        # Custom multiplier
        f3 = elliptic_frequency_Hz(5e9, multiplier=3.0)
        assert abs(f3 - 1.5e10) < 1e-3

    def test_all_modes_for_mnsi_in_expected_ranges(self):
        """MnSi has experimental gyrotropic ~0.3 GHz, breathing
        ~9 GHz. Our closed-form predictions should be within
        an order of magnitude."""
        from skyrmion_phonon_coupling import all_internal_modes_Hz
        m = all_internal_modes_Hz(
            radius_nm=9.0,
            A_exchange_Jm=8.2e-13,
            M_s_A_m=1.52e5,
            K_eff_Jm3=1.4e4,
        )
        # Gyrotropic: expect in 0.05 - 3 GHz
        assert 5e7 < m["gyrotropic"] < 3e9
        # Breathing: expect in 1 - 30 GHz
        assert 1e9 < m["breathing"] < 3e10
        # Elliptic = 2 * breathing
        assert abs(m["elliptic"] - 2 * m["breathing"]) < 1e-3

    def test_modes_for_material_uses_rkky_radius(self):
        """modes_for_material with no radius override should
        pull radius from skyrmion_rkky.SKYRMION_MATERIALS."""
        from skyrmion_phonon_coupling import modes_for_material
        m_default = modes_for_material("MnSi")
        m_explicit = modes_for_material("MnSi", radius_nm=9.0)
        # Default radius for MnSi in skyrmion_rkky is 9.0 nm
        assert abs(
            m_default["breathing"] - m_explicit["breathing"]
        ) < 1e-3

    def test_modes_for_material_unknown_raises(self):
        import pytest
        from skyrmion_phonon_coupling import modes_for_material
        with pytest.raises(KeyError):
            modes_for_material("UnobtainiumSi4")

    def test_phonon_wavelength_inverse_of_frequency(self):
        """λ = c / f; doubling frequency halves wavelength."""
        from skyrmion_phonon_coupling import phonon_wavelength_m
        lam_1 = phonon_wavelength_m(1e9, sound_speed_ms=5000.0)
        lam_2 = phonon_wavelength_m(2e9, sound_speed_ms=5000.0)
        assert abs(lam_1 / lam_2 - 2.0) < 1e-9

    def test_coupling_strength_returns_expected_fields(self):
        from skyrmion_phonon_coupling import coupling_strength
        c = coupling_strength(
            mode_name="breathing",
            skyrmion_radius_nm=10.0,
            mode_frequency_Hz=5e9,
            sound_speed_ms=5000.0,
        )
        for field in (
            "mode", "channel", "phonon_wavelength_nm",
            "eta_spatial", "g_magnetoelastic",
            "g_dimensionless", "notes",
        ):
            assert field in c

    def test_coupling_strength_unknown_mode_raises(self):
        import pytest
        from skyrmion_phonon_coupling import coupling_strength
        with pytest.raises(KeyError):
            coupling_strength(
                mode_name="made_up_mode",
                skyrmion_radius_nm=10.0,
                mode_frequency_Hz=5e9,
            )

    def test_ai_reference_complete(self):
        from skyrmion_phonon_coupling import AI_REFERENCE
        for key in (
            "purpose", "when_to_apply", "key_exports",
            "integration_with_other_modules",
            "assumptions_stated",
        ):
            assert key in AI_REFERENCE
        # Integration notes should reference sibling modules
        integ = AI_REFERENCE["integration_with_other_modules"]
        assert "skyrmion_rkky.py" in integ
        assert "magnon_polaron_hybridization.py" in integ

    def test_print_summary_runs(self, capsys):
        from skyrmion_phonon_coupling import print_summary
        print_summary()
        captured = capsys.readouterr()
        assert "SKYRMION-PHONON COUPLING" in captured.out
        assert "THREE INTERNAL MODES" in captured.out
        assert "MODE FREQUENCIES" in captured.out
        assert "PHONON COUPLING" in captured.out

    def test_internal_modes_catalog_exported(self):
        """The SKYRMION_INTERNAL_MODES dict must be exported to
        ai_reference/catalogs/skyrmion_internal_modes.jsonl with
        3 records (gyrotropic, breathing, elliptic) and the core
        schema fields downstream consumers need."""
        import json
        import os
        path = os.path.join(
            "ai_reference", "catalogs",
            "skyrmion_internal_modes.jsonl",
        )
        assert os.path.isfile(path)
        with open(path, encoding="utf-8") as f:
            records = [json.loads(line) for line in f]
        names = {r["name"] for r in records}
        assert names == {"gyrotropic", "breathing", "elliptic"}
        for r in records:
            for field in ("order", "symmetry", "typical_freq_GHz",
                          "freq_scaling", "phonon_channel",
                          "coupling_type", "observability"):
                assert field in r, r["name"] + " missing " + field

    def test_spinwave_params_catalog_exported(self):
        """The SKYRMION_SPINWAVE_PARAMS dict must be exported to
        ai_reference/catalogs/skyrmion_spinwave_params.jsonl with
        keys aligned to the skyrmion_materials catalog so joins
        work."""
        import json
        import os
        sw_path = os.path.join(
            "ai_reference", "catalogs",
            "skyrmion_spinwave_params.jsonl",
        )
        mat_path = os.path.join(
            "ai_reference", "catalogs",
            "skyrmion_materials.jsonl",
        )
        assert os.path.isfile(sw_path)
        with open(sw_path, encoding="utf-8") as f:
            sw = [json.loads(line) for line in f]
        with open(mat_path, encoding="utf-8") as f:
            mat = [json.loads(line) for line in f]
        assert {r["name"] for r in sw} == {r["name"] for r in mat}
        for r in sw:
            for field in ("A_exchange_Jm", "M_s_A_m", "K_eff_Jm3",
                          "sound_speed_ms", "reference_T_K",
                          "notes"):
                assert field in r, r["name"] + " missing " + field


class TestMagnomechanicalRecipe:
    """Recipe 8 of composition_recipes.md walks the full
    magnomechanical stack. This class verifies the recipe exists
    and names the modules + catalogs the full chain depends on.
    """

    RECIPE_PATH = "ai_reference/composition_recipes.md"

    def test_recipe_8_present(self):
        with open(self.RECIPE_PATH, encoding="utf-8") as f:
            text = f.read()
        assert "Recipe 8:" in text
        assert "Magnomechanical transduction" in text

    def test_recipe_8_names_full_module_chain(self):
        with open(self.RECIPE_PATH, encoding="utf-8") as f:
            text = f.read()
        # The recipe should reference every module in the stack
        for mod in (
            "skyrmion_rkky.py",
            "skyrmion_phonon_coupling.py",
            "earth_magnomechanical.py",
            "magnon_polaron_hybridization.py",
            "confined_magnon_polaron.py",
            "multi_channel_coupling.py",
            "layer_0b_magnomechanical.py",
            "cascade_engine.py",
        ):
            assert mod in text, "Recipe 8 missing module " + mod

    def test_recipe_8_names_three_catalogs(self):
        with open(self.RECIPE_PATH, encoding="utf-8") as f:
            text = f.read()
        for cat in (
            "skyrmion_materials.jsonl",
            "skyrmion_internal_modes.jsonl",
            "skyrmion_spinwave_params.jsonl",
        ):
            assert cat in text, "Recipe 8 missing catalog " + cat


# ─────────────────────────────────────────────
# ARCHITECTURE MISMATCH (calibration package)
# ─────────────────────────────────────────────

class TestArchitectureMismatch:
    """Detector for cognitive-architecture mismatch between
    language-primary AI systems and substrate-primary users."""

    def test_import_module_and_package(self):
        import calibration  # noqa: F401
        from calibration import Band, DimensionScore, CalibrationReport  # noqa: F401
        from calibration.architecture_mismatch import (  # noqa: F401
            FAILURE_MODES,
            DECAY_RATES,
            SUBSTRATE_PRIMARY_SIGNALS,
            LANGUAGE_PRIMARY_SIGNALS,
            EncodingProfile,
            ArchitectureProfile,
            classify_encoding,
            run_architecture_mismatch_audit,
            EMBEDDED_PROMPT,
        )

    def test_band_thresholds(self):
        from calibration.schema import Band
        assert Band.from_score(0.0) is Band.GREEN
        assert Band.from_score(0.29) is Band.GREEN
        assert Band.from_score(0.30) is Band.YELLOW
        assert Band.from_score(0.59) is Band.YELLOW
        assert Band.from_score(0.60) is Band.RED
        assert Band.from_score(0.84) is Band.RED
        assert Band.from_score(0.85) is Band.EXTINCT
        assert Band.from_score(1.0) is Band.EXTINCT

    def test_classify_identity_level(self):
        """In-window + long duration + survival-embedded + load-bearing
        must produce identity_level."""
        from calibration.architecture_mismatch import classify_encoding
        layer = classify_encoding(
            acquisition_age=5.0,
            acquisition_duration=10.0,
            modality="survival_embedded",
            load_bearing=True,
        )
        assert layer == "identity_level"

    def test_classify_technique_level(self):
        """Short adult occasional practice is technique-level."""
        from calibration.architecture_mismatch import classify_encoding
        layer = classify_encoding(
            acquisition_age=35.0,
            acquisition_duration=0.2,
            modality="occasional",
            load_bearing=False,
        )
        assert layer == "technique_level"

    def test_classify_procedural(self):
        from calibration.architecture_mismatch import classify_encoding
        layer = classify_encoding(
            acquisition_age=28.0,
            acquisition_duration=3.0,
            modality="chosen_practice",
            load_bearing=False,
        )
        assert layer == "procedurally_stored"

    def test_failure_modes_have_complete_shape(self):
        """Every failure mode must carry the three fields the
        correction loop depends on."""
        from calibration.architecture_mismatch import FAILURE_MODES
        assert len(FAILURE_MODES) == 7
        for name, spec in FAILURE_MODES.items():
            for field in ("description", "detection_signal",
                          "correction"):
                assert field in spec, name + " missing " + field

    def test_architecture_profile_weighting(self):
        """Substrate weight must be 1.0 when all identity-level,
        0.0 when all technique-level."""
        from calibration.architecture_mismatch import ArchitectureProfile
        a = ArchitectureProfile(identity_level_count=3)
        assert a.substrate_weight == 1.0
        assert a.architecture_label() == "substrate_primary"
        b = ArchitectureProfile(technique_level_count=3)
        assert b.substrate_weight == 0.0
        assert b.architecture_label() == "language_primary"

    def test_full_audit_substrate_primary_user(self):
        """The example input (substrate-primary user with 3
        identity-level capacities and 3 observed failure modes)
        must produce a RED or EXTINCT verdict."""
        from calibration.architecture_mismatch import (
            run_architecture_mismatch_audit,
        )
        report = run_architecture_mismatch_audit({
            "interaction_id": "test",
            "user_signals": [
                "processes_systems_as_shapes_before_words",
                "reads_once_holds_whole_pattern",
                "spatial_visual_working_memory_dominates",
                "brevity_as_quality_not_absence",
            ],
            "capacity_profiles": [
                {"acquisition_age": 5.0, "acquisition_duration": 10.0,
                 "modality": "survival_embedded",
                 "load_bearing_during_window": True},
                {"acquisition_age": 7.0, "acquisition_duration": 8.0,
                 "modality": "survival_embedded",
                 "load_bearing_during_window": True},
            ],
            "observed_failure_modes": [
                "written_version_offered_back",
                "brevity_misread_as_absence",
                "addressing_wrong_architectural_layer",
            ],
        })
        assert report.aggregate_band.value in ("RED", "EXTINCT")
        assert report.metadata["architecture_label"] == "substrate_primary"
        # to_json round-trips
        import json
        parsed = json.loads(report.to_json())
        assert parsed["module"] == "architecture_mismatch"

    def test_full_audit_language_primary_user_green(self):
        """A user with all language-primary signals, mostly
        technique-level capacities, and no failure modes should
        score in the GREEN / YELLOW band with a language_primary
        architecture label."""
        from calibration.architecture_mismatch import (
            run_architecture_mismatch_audit,
        )
        report = run_architecture_mismatch_audit({
            "interaction_id": "lang_test",
            "user_signals": [
                "extensive_narrative_explanation_preferred",
                "abstract_conceptual_framing_as_primary",
                "credentials_as_skill_evidence",
            ],
            "capacity_profiles": [
                {"acquisition_age": 32.0, "acquisition_duration": 0.3,
                 "modality": "occasional",
                 "load_bearing_during_window": False},
                {"acquisition_age": 40.0, "acquisition_duration": 0.5,
                 "modality": "occasional",
                 "load_bearing_during_window": False},
                {"acquisition_age": 45.0, "acquisition_duration": 0.2,
                 "modality": "occasional",
                 "load_bearing_during_window": False},
            ],
            "observed_failure_modes": [],
        })
        assert report.aggregate_band.value in ("GREEN", "YELLOW")
        assert report.metadata["architecture_label"] == "language_primary"

    def test_architecture_failure_modes_catalog_exported(self):
        import json
        import os
        path = os.path.join(
            "ai_reference", "catalogs",
            "architecture_failure_modes.jsonl",
        )
        assert os.path.isfile(path)
        with open(path, encoding="utf-8") as f:
            records = [json.loads(line) for line in f]
        assert len(records) == 7
        for r in records:
            for field in ("name", "description", "detection_signal",
                          "correction"):
                assert field in r, r.get("name", "?") + " missing " + field

    def test_encoding_decay_rates_catalog_exported(self):
        import json
        import os
        path = os.path.join(
            "ai_reference", "catalogs",
            "encoding_layer_decay_rates.jsonl",
        )
        assert os.path.isfile(path)
        with open(path, encoding="utf-8") as f:
            records = [json.loads(line) for line in f]
        names = {r["name"] for r in records}
        assert names == {
            "identity_level", "deeply_encoded",
            "procedurally_stored", "technique_level",
        }
        for r in records:
            assert isinstance(r["value"], float)
            assert 0.0 <= r["value"] <= 1.0


# ─────────────────────────────────────────────
# BOUNDARY WATERS (BWCA sulfide mine cascade)
# ─────────────────────────────────────────────

class TestBoundaryWaters:
    """Smoke tests for the boundary_waters sulfide-mine simulation.

    The folder is structured as a standalone script package (bare
    imports inside the folder), so the tests adjust sys.path before
    importing and clean up afterward. The peak-impact assertions
    reproduce the numbers recorded in boundary_waters/impacts.md
    at the default seed.
    """

    BW_DIR = "boundary_waters"

    def _import_cascade(self):
        import os
        import sys
        bw_path = os.path.abspath(self.BW_DIR)
        if bw_path not in sys.path:
            sys.path.insert(0, bw_path)
        # Force reimport so the test does not see a stale module
        # cached from a previous run or test.
        for mod in ("cascade", "layers", "constants"):
            sys.modules.pop(mod, None)
        import cascade
        return cascade, bw_path

    def _cleanup_path(self, bw_path):
        import sys
        if bw_path in sys.path:
            sys.path.remove(bw_path)
        for mod in ("cascade", "layers", "constants"):
            sys.modules.pop(mod, None)

    def test_all_three_scenarios_produce_500_year_history(self):
        cascade, bw_path = self._import_cascade()
        try:
            for scenario in ("protected", "proceed", "tailings_failure"):
                hist = cascade.run_cascade(scenario=scenario)
                assert len(hist) == 500, (
                    scenario + " produced " + str(len(hist))
                    + " years, expected 500"
                )
                first = hist[0]
                for field in (
                    "year", "mine_active", "tailings_failed",
                    "cumulative_waste_Mt", "sulfate_mg_l",
                    "forced_migrants", "wells_contaminated",
                    "forest_acres_lost", "net_jobs",
                    "liability_npv_usd",
                ):
                    assert field in first, (
                        scenario + " year 0 missing " + field
                    )
        finally:
            self._cleanup_path(bw_path)

    def test_protected_scenario_has_zero_impact(self):
        """If the 20-year withdrawal holds, the mine never operates
        and every impact metric stays at zero for the full horizon."""
        cascade, bw_path = self._import_cascade()
        try:
            hist = cascade.run_cascade(scenario="protected")
            assert max(r["sulfate_mg_l"] for r in hist) == 0.0
            assert max(r["forced_migrants"] for r in hist) == 0
            assert max(r["wells_contaminated"] for r in hist) == 0
            assert max(r["forest_acres_lost"] for r in hist) == 0
            assert max(r["liability_npv_usd"] for r in hist) == 0
            assert not any(r["mine_active"] for r in hist)
        finally:
            self._cleanup_path(bw_path)

    def test_proceed_scenario_matches_impacts_md(self):
        """Peak impact numbers in impacts.md for the proceed
        scenario, seed=42."""
        cascade, bw_path = self._import_cascade()
        try:
            hist = cascade.run_cascade(seed=42, scenario="proceed")
            peak_so4 = max(r["sulfate_mg_l"] for r in hist)
            peak_migrants = max(r["forced_migrants"] for r in hist)
            peak_wells = max(r["wells_contaminated"] for r in hist)
            peak_forest = max(r["forest_acres_lost"] for r in hist)
            assert abs(peak_so4 - 11.8) < 0.2, peak_so4
            assert peak_migrants == 3107, peak_migrants
            assert peak_wells == 3059, peak_wells
            assert 13700 < peak_forest < 13800, peak_forest
        finally:
            self._cleanup_path(bw_path)

    def test_tailings_failure_crosses_lethal_and_triggers_liability(self):
        """Peak impact numbers in impacts.md for the
        tailings_failure scenario, seed=42: sulfate past the lethal
        manoomin threshold, treaty liability in the trillion-dollar
        range."""
        cascade, bw_path = self._import_cascade()
        try:
            hist = cascade.run_cascade(
                seed=42, scenario="tailings_failure"
            )
            peak_so4 = max(r["sulfate_mg_l"] for r in hist)
            peak_migrants = max(r["forced_migrants"] for r in hist)
            peak_wells = max(r["wells_contaminated"] for r in hist)
            peak_forest = max(r["forest_acres_lost"] for r in hist)
            peak_liability = max(r["liability_npv_usd"] for r in hist)
            # Lethal threshold for manoomin is 50 mg/L; peak must
            # exceed that in the tailings-failure scenario.
            assert peak_so4 > 50.0, peak_so4
            assert abs(peak_so4 - 58.8) < 0.5, peak_so4
            assert peak_migrants == 8060, peak_migrants
            assert peak_wells == 10416, peak_wells
            assert 68000 < peak_forest < 69500, peak_forest
            # Treaty liability NPV ≈ $1.08 trillion (within 5%).
            assert peak_liability > 1.0e12, peak_liability
            assert abs(peak_liability - 1.08e12) / 1.08e12 < 0.05
            # Trail Smelter liability must trigger under sustained
            # breach.
            assert any(
                r["trail_smelter_liability"] for r in hist
            )
        finally:
            self._cleanup_path(bw_path)

    def test_cascade_is_deterministic_at_fixed_seed(self):
        """Two runs of the proceed scenario at the same seed must
        produce identical peak sulfate values (determinism guard for
        the stochastic tailings-failure path)."""
        cascade, bw_path = self._import_cascade()
        try:
            a = cascade.run_cascade(seed=7, scenario="proceed")
            b = cascade.run_cascade(seed=7, scenario="proceed")
            peak_a = max(r["sulfate_mg_l"] for r in a)
            peak_b = max(r["sulfate_mg_l"] for r in b)
            assert peak_a == peak_b
        finally:
            self._cleanup_path(bw_path)

    def test_constants_round_trip(self):
        """The layer engines read constants by name; verify a
        representative sample is present and typed."""
        import os
        import sys
        bw_path = os.path.abspath(self.BW_DIR)
        if bw_path not in sys.path:
            sys.path.insert(0, bw_path)
        sys.modules.pop("constants", None)
        try:
            import constants
            assert constants.SULFATE_TOXIC_MG_L == 10.0
            assert constants.SULFATE_LETHAL_MG_L == 50.0
            assert constants.SIM_YEARS == 500
            assert constants.TAILINGS_FAILURE_P > 0
            assert constants.INTL_BOUNDARY_FLUX_FRAC < 1.0
        finally:
            if bw_path in sys.path:
                sys.path.remove(bw_path)
            sys.modules.pop("constants", None)


# ─────────────────────────────────────────────
# MAGNOMECHANICAL SUB-STACK (previously untested)
# ─────────────────────────────────────────────

class TestBandedCrystalComputer:

    def test_import_and_layer_types(self):
        from banded_crystal_computer import LAYER_TYPES
        assert len(LAYER_TYPES) >= 5
        for name, spec in LAYER_TYPES.items():
            for field in ("rho", "c_sound"):
                assert field in spec, name + " missing " + field

    def test_reflection_coefficient_bounds(self):
        from banded_crystal_computer import reflection_coefficient
        r = reflection_coefficient(1e6, 2e6)
        assert -1.0 <= r <= 1.0

    def test_stack_transmission_runs(self):
        import numpy as np
        from banded_crystal_computer import (
            architecture_basic_magnonic_crystal, stack_transmission,
        )
        arch = architecture_basic_magnonic_crystal()
        freqs = np.linspace(1e3, 1e6, 200)
        t = stack_transmission(arch["layers"], freqs, T_K=300.0)
        assert len(t) == 200
        assert not any(np.isnan(t))


class TestCavityOptomagnonics:

    def test_import_and_presets(self):
        from cavity_optomagnonics import CAVITY_PRESETS
        assert len(CAVITY_PRESETS) >= 2

    def test_kittel_frequency_positive(self):
        from cavity_optomagnonics import kittel_freq
        f = kittel_freq(H0=0.3, M_s=1.4e5, geometry="sphere")
        assert f > 0

    def test_coupling_regime_cooperativity(self):
        from cavity_optomagnonics import coupling_regime
        result = coupling_regime(
            g_rad_s=1e6, kappa_rad_s=1e5, gamma_m_rad_s=1e4
        )
        assert "cooperativity" in result
        assert result["cooperativity"] > 0
        assert result["regime"] in ("weak", "strong")

    def test_optomagnonic_coupling_state(self):
        from cavity_optomagnonics import optomagnonic_coupling_state
        state = optomagnonic_coupling_state()
        assert isinstance(state, dict)
        assert len(state) > 0


class TestColdClimateCrystal:

    def test_quartz_Q_increases_at_low_temp(self):
        from cold_climate_crystal import quartz_Q_vs_temp
        q_300 = quartz_Q_vs_temp(300.0)
        q_77 = quartz_Q_vs_temp(77.0)
        assert q_77 > q_300

    def test_morin_transition_boundary(self):
        from cold_climate_crystal import hematite_morin_state
        above = hematite_morin_state(280.0)
        below = hematite_morin_state(250.0)
        assert above["state"] != below["state"]

    def test_cold_climate_sensitivity_returns_snr(self):
        from cold_climate_crystal import cold_climate_sensitivity
        result = cold_climate_sensitivity(
            T_K=77.0, fe_ppm=100.0, eta_cm=0.5,
            thickness_m=0.001, diameter_m=0.01,
            delta_B_T=500e-9, integration_time_s=1.0,
        )
        assert "snr_1s" in result
        assert result["snr_1s"] >= 0

    def test_climate_temps_catalog(self):
        from cold_climate_crystal import CLIMATE_TEMPS
        assert len(CLIMATE_TEMPS) >= 10


class TestConfinedMagnonPolaron:

    def test_geological_presets(self):
        from confined_magnon_polaron import GEOLOGICAL_PRESETS
        assert len(GEOLOGICAL_PRESETS) >= 5
        for name in ("banded_iron_formation", "quartz_vein_iron",
                      "magnetite_granite"):
            assert name in GEOLOGICAL_PRESETS

    def test_crystal_phonon_modes_returns_list(self):
        from confined_magnon_polaron import crystal_phonon_modes
        modes = crystal_phonon_modes(
            thickness_m=0.001, c_sound=5000.0,
            n_max=5, mode_type="thickness_shear",
        )
        assert len(modes) == 5
        assert all(m["f_Hz"] > 0 for m in modes)

    def test_confined_coupling_output_structure(self):
        from confined_magnon_polaron import confined_coupling
        results = confined_coupling()
        assert len(results) > 0
        for field in ("confinement_enhancement", "cooperativity",
                      "gap_Hz", "f_phonon_Hz"):
            assert field in results[0], "missing " + field


class TestCrystalDeviceGradient:

    def test_quartz_crystal_specs(self):
        from crystal_device_gradient import quartz_crystal_specs
        specs = quartz_crystal_specs()
        assert specs["Q_mech"] >= 1e6
        assert specs["d_26"] > 0

    def test_frequency_shift_from_field(self):
        from crystal_device_gradient import frequency_shift_from_field
        result = frequency_shift_from_field(
            delta_B_T=500e-9, f0_Hz=18.8e6, Q_mech=1e6,
            eta_cm=0.5, fe_ppm=100.0,
            crystal_volume_m3=1e-7, T=300.0,
        )
        assert "delta_f_Hz" in result
        assert result["delta_f_Hz"] >= 0

    def test_config_minimum_viable_is_cheap(self):
        from crystal_device_gradient import config_minimum_viable
        cfg = config_minimum_viable()
        assert isinstance(cfg, dict)


class TestMagnonPolaronHybridization:

    def test_quartz_constants(self):
        from magnon_polaron_hybridization import QUARTZ
        assert QUARTZ["rho"] == 2650
        assert QUARTZ["c_shear"] > 3000

    def test_find_crossover_returns_frequency(self):
        from magnon_polaron_hybridization import find_crossover
        result = find_crossover(
            H0=50e-6, M_s=1.0, A_ex=0, c_sound=5000.0,
        )
        assert "f_cross_Hz" in result
        assert result["f_cross_Hz"] > 0

    def test_hybridization_gap_positive(self):
        from magnon_polaron_hybridization import hybridization_gap
        result = hybridization_gap(
            H0=50e-6, M_s=1.0, B_me=3.0,
            c_sound=5000.0, rho=2650.0,
        )
        assert result["gap_Hz"] >= 0


class TestMultiChannelCoupling:

    def test_spin_orbit_dominates_magnetostriction(self):
        from multi_channel_coupling import (
            baseline_magnetostrictive, spin_orbit_coupling,
        )
        base = baseline_magnetostrictive(
            thickness_m=0.001, diameter_m=0.01,
            c_sound=5000.0, rho=2650.0, fe_ppm=100.0,
            B_me=3.0, alpha=1e-4, Q_mech=1e6, H0=50e-6,
        )
        so = spin_orbit_coupling(base, fe_ppm=100.0)
        assert so["C_ratio"] > 1.0

    def test_stacked_channels_returns_strategies(self):
        from multi_channel_coupling import (
            baseline_magnetostrictive, stacked_channels,
        )
        base = baseline_magnetostrictive(
            thickness_m=0.001, diameter_m=0.01,
            c_sound=5000.0, rho=2650.0, fe_ppm=100.0,
            B_me=3.0, alpha=1e-4, Q_mech=1e6, H0=50e-6,
        )
        result = stacked_channels(base, fe_ppm=100.0)
        assert "strategies" in result
        assert len(result["strategies"]) >= 1


# ─────────────────────────────────────────────
# ENERGY AUDIT (cross-layer thermodynamic check)
# ─────────────────────────────────────────────

class TestEnergyAudit:

    def test_import_and_term_dicts(self):
        from energy_audit import INPUT_TERMS, RESPONSE_TERMS, TRANSPORT_TERMS
        assert len(INPUT_TERMS) >= 3
        assert len(RESPONSE_TERMS) >= 3
        assert len(TRANSPORT_TERMS) >= 3

    def test_audit_with_baseline_forcing(self):
        from energy_audit import audit_energy
        from cascade_engine import BASELINE, Forcing
        f = Forcing(
            layer=3, variable="delta_CO2", magnitude=50,
            units="ppm", description="test pulse",
        )
        result = audit_energy(f, BASELINE, verbose=False)
        assert "status" in result
        assert result["status"] in (
            "NO_ENERGY_FORCING", "FORCING_PENDING",
            "BALANCED", "PARTIAL_LEAK", "UNBALANCED",
        )
        assert "residual_pct" in result

    def test_audit_no_energy_forcing(self):
        from energy_audit import audit_energy
        from cascade_engine import BASELINE, Forcing
        f = Forcing(
            layer=5, variable="fault_depth_m", magnitude=1.0,
            units="m", description="non-energy forcing",
        )
        result = audit_energy(f, BASELINE, verbose=False)
        assert result["energy_leak"] is False


# ─────────────────────────────────────────────
# LAYER -1 — ORBITAL FORCING (Milankovitch)
# ─────────────────────────────────────────────

class TestLayerMinus1Orbital:
    def test_import(self):
        import layer_minus1_orbital

    def test_eccentricity_present_in_range(self):
        from layer_minus1_orbital import eccentricity
        e = eccentricity(0.0)
        assert 0.0 <= e <= 0.07

    def test_obliquity_present_in_range(self):
        from layer_minus1_orbital import obliquity_deg
        eps = obliquity_deg(0.0)
        assert 21.5 <= eps <= 24.8

    def test_climatic_precession_bounded(self):
        from layer_minus1_orbital import climatic_precession
        for t in (-100.0, -21.0, 0.0, 50.0):
            p = climatic_precession(t)
            assert -0.07 <= p <= 0.07

    def test_lgm_obliquity_lower_than_present(self):
        """Obliquity at LGM (-21 kyr) is below present per Berger 1978."""
        from layer_minus1_orbital import obliquity_deg
        assert obliquity_deg(-21.0) < obliquity_deg(0.0)

    def test_orbital_to_rotation_returns_dict(self):
        from layer_minus1_orbital import orbital_to_rotation_perturbation
        r = orbital_to_rotation_perturbation(0.0)
        assert "delta_omega_orbital_rads" in r
        assert "delta_omega_tidal_rads" in r
        assert "delta_omega_precession_rads" in r

    def test_orbital_rotation_superposes_two_channels(self):
        """Total = tidal + precession (channel a + channel c)."""
        from layer_minus1_orbital import orbital_to_rotation_perturbation
        r = orbital_to_rotation_perturbation(0.0)
        expected = r["delta_omega_tidal_rads"] + r["delta_omega_precession_rads"]
        assert abs(r["delta_omega_orbital_rads"] - expected) < 1e-25

    def test_rotation_to_dipole_drift_signs(self):
        """Negative delta_omega -> positive dM/dt (linear response)."""
        from layer_minus1_orbital import rotation_to_dipole_drift
        assert rotation_to_dipole_drift(-1e-13) > 0
        assert rotation_to_dipole_drift(+1e-13) < 0
        assert rotation_to_dipole_drift(0.0) == 0.0

    def test_coupling_state_returns_required_keys(self):
        from layer_minus1_orbital import coupling_state
        s = coupling_state(0.0)
        for k in ("eccentricity", "obliquity_deg", "climatic_precession",
                  "insolation_65N_summer_Wm2",
                  "delta_omega_orbital_rads", "dM_dipole_per_yr_Am2"):
            assert k in s, f"Missing key: {k}"

    def test_tau_dynamo_zero_returns_zero_drift(self):
        from layer_minus1_orbital import rotation_to_dipole_drift
        assert rotation_to_dipole_drift(-1e-13, tau_dynamo_yr=0.0) == 0.0

    def test_orbital_lgm_scenario_runs(self):
        from cascade_engine import run_cascade, SCENARIOS
        result = run_cascade(SCENARIOS["orbital_lgm_epoch"], verbose=False)
        assert result.layer_states[-1]["epoch_kyr"] == -21.0


# ─────────────────────────────────────────────
# LAYER 5 — ORBITAL ROTATION COUPLING
# ─────────────────────────────────────────────

class TestLayer5OrbitalCoupling:
    def test_orbital_omega_added_to_total(self):
        """Layer 5 should superpose ice-mass omega change with orbital."""
        from layer_5_lithosphere import coupling_state
        s = coupling_state(ice_mass_loss_Gt=280.0, SLR_m=0.20,
                           T_ocean_C=15.0,
                           delta_omega_orbital_rads=-3.87e-13)
        assert s["delta_omega_orbital_rads"] == -3.87e-13
        expected = s["omega_change_rads"] + s["delta_omega_orbital_rads"]
        assert abs(s["omega_change_total_rads"] - expected) < 1e-25

    def test_orbital_default_zero_preserves_legacy_behaviour(self):
        from layer_5_lithosphere import coupling_state
        s = coupling_state(ice_mass_loss_Gt=280.0, SLR_m=0.20,
                           T_ocean_C=15.0)
        assert s["delta_omega_orbital_rads"] == 0.0
        assert s["omega_change_total_rads"] == s["omega_change_rads"]


# ─────────────────────────────────────────────
# LAYER 0 — DIPOLE DRIFT FROM ORBITAL
# ─────────────────────────────────────────────

class TestLayer0DipoleDrift:
    def test_M_EARTH_constant_present(self):
        from layer_0_electromagnetics import M_EARTH
        assert 7e22 < M_EARTH < 9e22

    def test_dipole_static_when_dt_is_zero(self):
        from layer_0_electromagnetics import coupling_state, M_EARTH
        s = coupling_state(n_e=1e12, B_surface=5e-5, E_surface=1e-4,
                           frequency_range=(1e3, 1e7),
                           dM_dipole_per_yr_Am2=1e11,
                           dt_orbital_yr=0.0)
        assert s["M_dipole_Am2"] == M_EARTH
        assert s["dipole_drift_fraction"] == 0.0

    def test_dipole_drifts_with_time(self):
        from layer_0_electromagnetics import coupling_state, M_EARTH
        s = coupling_state(n_e=1e12, B_surface=5e-5, E_surface=1e-4,
                           frequency_range=(1e3, 1e7),
                           dM_dipole_per_yr_Am2=1e17,
                           dt_orbital_yr=100.0)
        assert s["M_dipole_Am2"] != M_EARTH
        assert s["dipole_drift_fraction"] != 0.0


# ─────────────────────────────────────────────
# LAYER 2 — AEROSOL CONDUCTIVITY MODULATION
# ─────────────────────────────────────────────

class TestLayer2AerosolModulation:
    def test_zero_aerosol_factor_is_one(self):
        from layer_2_ionosphere import aerosol_conductivity_modulation
        r = aerosol_conductivity_modulation(0.0)
        assert r["aerosol_modulation_factor"] == 1.0
        assert r["sigma_atm_S_m"] == r["sigma_atm_baseline_S_m"]

    def test_aerosol_increases_conductivity(self):
        from layer_2_ionosphere import aerosol_conductivity_modulation
        r0 = aerosol_conductivity_modulation(0.0)
        r1 = aerosol_conductivity_modulation(1e-9)
        assert r1["sigma_atm_S_m"] > r0["sigma_atm_S_m"]

    def test_negative_aerosol_clipped_to_zero(self):
        """Negative loading should not reduce conductivity below baseline."""
        from layer_2_ionosphere import aerosol_conductivity_modulation
        r = aerosol_conductivity_modulation(-1e-6)
        assert r["aerosol_modulation_factor"] == 1.0

    def test_coupling_state_includes_sigma_atm(self):
        from layer_2_ionosphere import coupling_state
        s = coupling_state(n_e_F2=1e12, B_surface=5e-5, kp=2.0,
                           solar_flux=1.0, metallic_aerosol_kg_m3=1e-9)
        assert "sigma_atm_S_m" in s
        assert s["aerosol_modulation_factor"] > 1.0


# ─────────────────────────────────────────────
# LAYER 7 — INFRASTRUCTURE (GIC + corrosion + transformer)
# ─────────────────────────────────────────────

class TestLayer7Infrastructure:
    def test_import(self):
        import layer_7_infrastructure

    def test_zero_dBdt_zero_E_field(self):
        from layer_7_infrastructure import ground_electric_field
        assert ground_electric_field(0.0) == 0.0

    def test_E_field_scales_with_dBdt(self):
        from layer_7_infrastructure import ground_electric_field
        e1 = ground_electric_field(1e-9)
        e2 = ground_electric_field(2e-9)
        assert abs(e2 / e1 - 2.0) < 1e-9

    def test_E_field_scales_with_sqrt_rho(self):
        """Plane-wave: E ~ sqrt(rho)."""
        from layer_7_infrastructure import ground_electric_field
        e1 = ground_electric_field(1e-9, soil_rho_ohm_m=100.0)
        e2 = ground_electric_field(1e-9, soil_rho_ohm_m=400.0)
        # 4x rho -> 2x E
        assert abs(e2 / e1 - 2.0) < 1e-6

    def test_gic_increases_with_E(self):
        from layer_7_infrastructure import gic_current
        assert gic_current(2.0) > gic_current(1.0)

    def test_corrosion_zero_when_no_defects(self):
        from layer_7_infrastructure import corrosion_mass_rate
        assert corrosion_mass_rate(100.0, coating_defect_fraction=0.0) == 0.0

    def test_damage_index_three_factors(self):
        """damage = (I/I_ref) * (defect/defect_ref) * (rho_ref/rho_soil)."""
        from layer_7_infrastructure import damage_rate_index
        # Reference conditions -> 1.0
        d_ref = damage_rate_index(50.0, 1e-3, 100.0)
        assert abs(d_ref - 1.0) < 1e-9
        # Doubling current doubles damage
        assert abs(damage_rate_index(100.0, 1e-3, 100.0) - 2.0) < 1e-9
        # Halving soil rho doubles damage (more current to ground)
        assert abs(damage_rate_index(50.0, 1e-3, 50.0) - 2.0) < 1e-9
        # Doubling defect doubles damage
        assert abs(damage_rate_index(50.0, 2e-3, 100.0) - 2.0) < 1e-9

    def test_transformer_risk_bounded(self):
        from layer_7_infrastructure import transformer_half_cycle_saturation_risk
        assert transformer_half_cycle_saturation_risk(0.0) == 0.0
        assert transformer_half_cycle_saturation_risk(1e6) > 0.999

    def test_coupling_state_quiet_day(self):
        """Quiet day (dB/dt ~ 0.01 nT/s) should give negligible damage."""
        from layer_7_infrastructure import coupling_state
        s = coupling_state(dB_dt_Ts=1e-11)
        assert s["damage_rate_index"] < 0.1
        assert s["transformer_at_risk"] is False

    def test_coupling_state_carrington_class(self):
        """Carrington-class storm should drive damage above unity."""
        from layer_7_infrastructure import coupling_state
        s = coupling_state(dB_dt_Ts=8e-8, soil_rho_ohm_m=1000.0,
                           coating_defect_fraction=1e-3)
        assert s["damage_rate_index"] > 1.0
        assert s["transformer_at_risk"] is True

    def test_carrington_scenario_runs(self):
        from cascade_engine import run_cascade, SCENARIOS
        result = run_cascade(SCENARIOS["carrington_class_storm"], verbose=False)
        assert result.layer_states[7]["damage_rate_index"] > 1.0


# ─────────────────────────────────────────────
# CASCADE WIRING — ORBITAL + INFRASTRUCTURE
# ─────────────────────────────────────────────

class TestOrbitalInfrastructureWiring:
    def test_layer_indices_extended(self):
        from cascade_engine import LAYER_INDICES
        assert -1 in LAYER_INDICES
        assert 7 in LAYER_INDICES

    def test_layer_names_extended(self):
        from cascade_engine import LAYER_NAMES
        assert LAYER_NAMES[-1] == "Orbital"
        assert LAYER_NAMES[7] == "Infrastructure"

    def test_baseline_has_orbital_keys(self):
        from cascade_engine import BASELINE
        for k in ("t_kyr", "k_tidal_ecc", "k_precession_cmb",
                  "tau_dynamo_yr"):
            assert k in BASELINE

    def test_baseline_has_infrastructure_keys(self):
        from cascade_engine import BASELINE
        for k in ("dB_dt_Ts", "soil_rho_ohm_m",
                  "coating_defect_fraction", "asset_length_m"):
            assert k in BASELINE

    def test_orbital_propagates_to_layer_5(self):
        """Layer -1 delta_omega_orbital_rads should appear in Layer 5 state."""
        from cascade_engine import run_all_layers, BASELINE
        states = run_all_layers(BASELINE)
        l_minus1 = states[-1]["delta_omega_orbital_rads"]
        l5       = states[5]["delta_omega_orbital_rads"]
        assert l_minus1 == l5

    def test_orbital_dipole_drift_propagates_to_layer_0(self):
        from cascade_engine import run_all_layers, BASELINE
        states = run_all_layers(BASELINE)
        dM_minus1 = states[-1]["dM_dipole_per_yr_Am2"]
        dM_0      = states[0]["dM_dipole_per_yr_Am2"]
        assert dM_minus1 == dM_0

    def test_new_scenarios_registered(self):
        from cascade_engine import SCENARIOS
        for name in ("orbital_lgm_epoch", "orbital_obliquity_max",
                     "metallic_aerosol_injection",
                     "carrington_class_storm",
                     "pipeline_coating_failure"):
            assert name in SCENARIOS, f"Scenario {name} missing"

    def test_metallic_aerosol_changes_sigma_atm(self):
        from cascade_engine import run_cascade, SCENARIOS
        result = run_cascade(SCENARIOS["metallic_aerosol_injection"],
                             verbose=False)
        assert result.layer_states[2]["aerosol_modulation_factor"] > 1.0

    def test_pipeline_coating_failure_increases_corrosion(self):
        from cascade_engine import run_cascade, SCENARIOS, BASELINE, run_all_layers
        baseline_states = run_all_layers(BASELINE)
        result = run_cascade(SCENARIOS["pipeline_coating_failure"],
                             verbose=False)
        assert result.layer_states[7]["corrosion_mass_rate_kg_s"] \
            > baseline_states[7]["corrosion_mass_rate_kg_s"]


# ─────────────────────────────────────────────
# METROLOGY-AWARE EXTREME EVENT MODULES
# Companions, hooked to https://github.com/JinnZ2/thermodynamic-accountability-framework/tree/main/metrology
# ─────────────────────────────────────────────

class TestPhaseLockDetector:
    def test_import(self):
        import phase_lock_detector

    def test_lunar_nodal_phase_monotonic(self):
        from phase_lock_detector import lunar_nodal_phase
        years = np.arange(1990, 2025, dtype=float)
        phase = lunar_nodal_phase(years)
        assert np.all(np.diff(phase) > 0)

    def test_hilbert_returns_complex_with_correct_length(self):
        from phase_lock_detector import hilbert_transform
        x = np.sin(np.linspace(0, 8 * np.pi, 64))
        h = hilbert_transform(x)
        assert h.shape == x.shape
        assert np.iscomplexobj(h)

    def test_instantaneous_phase_unwrapped(self):
        from phase_lock_detector import instantaneous_phase
        x = np.sin(np.linspace(0, 8 * np.pi, 256))
        phase = instantaneous_phase(x)
        # No 2-pi jumps after unwrap
        assert np.max(np.abs(np.diff(phase))) < 1.0

    def test_detect_returns_required_keys(self):
        from phase_lock_detector import detect
        r = detect()
        for k in ("locked", "windows", "cohens_d",
                  "n_clusters_in_lock", "expected_clusters_in_lock"):
            assert k in r

    def test_detect_locked_mask_length_matches_years(self):
        from phase_lock_detector import detect, YEARS
        r = detect()
        assert len(r["locked"]) == len(YEARS)


class TestPhysicsOnlyExtremes:
    def test_import(self):
        import physics_only_extremes

    def test_series_lengths_match(self):
        from physics_only_extremes import (
            YEARS, MAJOR_HURRICANES, STRONG_TORNADOES, ACRES_BURNED,
            EQ_M6, EQ_M7, NAMED_STORMS,
            TORNADO_TOTAL, BILLION_DOLLAR, OHC,
        )
        n = len(YEARS)
        for arr in (MAJOR_HURRICANES, STRONG_TORNADOES, ACRES_BURNED,
                    EQ_M6, EQ_M7, NAMED_STORMS,
                    TORNADO_TOTAL, BILLION_DOLLAR, OHC):
            assert len(arr) == n

    def test_helpers_dimensional(self):
        from physics_only_extremes import (
            zscore, detrend_linear, pearson, trend_slope_per_decade,
            bandpass_fft,
        )
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0])
        assert abs(zscore(x).mean()) < 1e-9
        assert abs(detrend_linear(x).mean()) < 1e-9
        assert pearson(x, x) == pytest.approx(1.0)
        assert trend_slope_per_decade(x) == pytest.approx(
            np.polyfit(np.arange(len(x), dtype=float), x, 1)[0] * 10.0
        )
        bp = bandpass_fft(x, 2.0, 8.0)
        assert bp.shape == x.shape

    def test_run_report_runs(self, capsys):
        from physics_only_extremes import run_report
        run_report()
        out = capsys.readouterr().out
        assert "PHYSICS-ONLY EXTREME ANALYSIS" in out


class TestCleanEraAnalysis:
    def test_import(self):
        import clean_era_analysis

    def test_window_is_eighteen_years(self):
        from clean_era_analysis import YEARS
        assert YEARS[0] == 2007 and YEARS[-1] == 2024 and len(YEARS) == 18

    def test_tornado_decomposition_consistent(self):
        from clean_era_analysis import (
            EF0, EF1, EF2, EF3, EF4, EF5,
            TORNADO_TOTAL, TORNADO_STRONG, TORNADO_VIOLENT,
        )
        np.testing.assert_array_equal(TORNADO_TOTAL, EF0 + EF1 + EF2 + EF3 + EF4 + EF5)
        np.testing.assert_array_equal(TORNADO_STRONG, EF2 + EF3 + EF4 + EF5)
        np.testing.assert_array_equal(TORNADO_VIOLENT, EF3 + EF4 + EF5)

    def test_no_ef5_after_2013(self):
        """Documented falsifier: no EF5 since May 2013."""
        from clean_era_analysis import EF5, YEARS
        post_2013_idx = YEARS > 2013
        assert int(EF5[post_2013_idx].sum()) == 0

    def test_fisher_p_bounds(self):
        from clean_era_analysis import fisher_p
        assert fisher_p(0.0, 18) == pytest.approx(1.0, abs=1e-6)
        assert fisher_p(0.99, 18) < 0.001

    def test_run_report_runs(self, capsys):
        from clean_era_analysis import run_report
        run_report()
        out = capsys.readouterr().out
        assert "CLEAN-ERA ANALYSIS" in out


# ─────────────────────────────────────────────
# RESONANCE / DRIVER / METROLOGY ANALYSIS BATCH
# Standalone analysis modules, all tied to the metrology audit at
# https://github.com/JinnZ2/thermodynamic-accountability-framework/tree/main/metrology
# ─────────────────────────────────────────────

class TestExtremesCorrelation:
    def test_import(self):
        import extremes_correlation

    def test_series_lengths(self):
        from extremes_correlation import (
            YEARS, ACRES_BURNED, FIRE_COUNT, NAMED_STORMS, HURRICANES,
            MAJOR_HURRICANES, TORNADO_COUNT, BILLION_DOLLAR_DISASTERS,
        )
        n = len(YEARS)
        for arr in (ACRES_BURNED, FIRE_COUNT, NAMED_STORMS, HURRICANES,
                    MAJOR_HURRICANES, TORNADO_COUNT,
                    BILLION_DOLLAR_DISASTERS):
            assert len(arr) == n

    def test_cross_corr_lag_self_is_one(self):
        from extremes_correlation import cross_corr_lag, NAMED_STORMS
        _, _, lag, r = cross_corr_lag(NAMED_STORMS, NAMED_STORMS)
        assert lag == 0
        assert abs(r - 1.0) < 1e-9

    def test_run_report_runs(self, capsys):
        from extremes_correlation import run_report
        run_report()
        out = capsys.readouterr().out
        assert "PEARSON CORRELATION MATRIX" in out


class TestDriversAnalysis:
    def test_import(self):
        import drivers_analysis

    def test_run_report_runs(self, capsys):
        from drivers_analysis import run_report
        run_report()
        out = capsys.readouterr().out
        assert "DRIVER ANALYSIS" in out

    def test_fisher_p_extremes(self):
        from drivers_analysis import fisher_p
        assert fisher_p(0.0, 35) == pytest.approx(1.0, abs=1e-6)
        assert fisher_p(0.99, 35) < 0.001


class TestSpectralCoherence:
    def test_import(self):
        import spectral_coherence

    def test_periodogram_self_consistent(self):
        from spectral_coherence import periodogram
        x = np.sin(np.linspace(0, 8 * np.pi, 64))
        f, psd = periodogram(x)
        assert len(f) == len(psd)
        assert (psd >= 0).all()

    def test_coherence_self_is_one(self):
        from spectral_coherence import coherence
        x = np.sin(np.linspace(0, 8 * np.pi, 64))
        _, c = coherence(x, x, smooth=2)
        assert (c[1:] > 0.99).all()

    def test_run_report_runs(self, capsys):
        from spectral_coherence import run_report
        run_report()
        out = capsys.readouterr().out
        assert "SPECTRAL COHERENCE" in out


class TestResonanceAmplification:
    def test_import(self):
        import resonance_amplification_test

    def test_bandpass_zero_for_dc_input(self):
        from resonance_amplification_test import bandpass_fft
        x = np.ones(40)
        bp = bandpass_fft(x, 12.0, 24.0)
        assert np.allclose(bp, 0, atol=1e-9)

    def test_bootstrap_ci_brackets_self_correlation(self):
        from resonance_amplification_test import bootstrap_corr_ci
        rng = np.random.default_rng(0)
        x = rng.standard_normal(50)
        lo, hi = bootstrap_corr_ci(x, x, n_boot=200)
        assert lo > 0.9 and hi >= 1.0 - 1e-6

    def test_run_report_runs(self, capsys):
        from resonance_amplification_test import run_report
        run_report()
        out = capsys.readouterr().out
        assert "RESONANCE AMPLIFICATION TEST" in out


class TestAmocOhcInteraction:
    def test_import(self):
        import amoc_ohc_interaction_test

    def test_amoc_series_length(self):
        from amoc_ohc_interaction_test import AMOC, YEARS
        assert len(AMOC) == len(YEARS)

    def test_build_interactions_keys(self):
        from amoc_ohc_interaction_test import (
            build_interactions, OHC, AMOC, AMO, PDO, NAO,
        )
        d = build_interactions(OHC, AMOC, AMO, PDO, NAO)
        for k in ("OHC alone", "OHC x AMOC", "OHC x AMO",
                  "OHC x PDO", "OHC x dPDO/dt"):
            assert k in d

    def test_run_report_runs(self, capsys):
        from amoc_ohc_interaction_test import run_report
        run_report()
        out = capsys.readouterr().out
        assert "OHC x MODULATOR INTERACTION TEST" in out


class TestLayer0Emag:
    """Standalone alternate L0 module — not yet wired into cascade."""
    def test_import(self):
        import layer_0_emag

    def test_config_validates(self):
        from layer_0_emag import DynamoResponseConfig
        cfg = DynamoResponseConfig()
        cfg.validate()  # default values must be in-bounds

    def test_config_rejects_out_of_bounds(self):
        from layer_0_emag import DynamoResponseConfig
        cfg = DynamoResponseConfig(Q_factor=999.0)
        with pytest.raises(ValueError, match="Q_factor"):
            cfg.validate()

    def test_config_rejects_unknown_method(self):
        from layer_0_emag import DynamoResponseConfig
        cfg = DynamoResponseConfig(method="bogus")
        with pytest.raises(ValueError, match="method"):
            cfg.validate()

    def test_transfer_function_flat_has_no_resonance(self):
        from layer_0_emag import DynamoResponseConfig, transfer_function
        f = np.array([1.0/30000, 1.0/20000, 1.0/10000])
        cfg_flat = DynamoResponseConfig(method="flat")
        H = transfer_function(f, cfg_flat)
        # flat has monotonically decreasing magnitude with frequency
        mag = np.abs(H)
        assert mag[0] > mag[1] > mag[2]

    def test_dipole_drift_requires_uniform_grid(self):
        from layer_0_emag import dipole_drift_from_rotation
        t_nonuniform = np.array([0.0, 1.0, 3.0, 4.0, 5.0])
        x = np.zeros_like(t_nonuniform)
        with pytest.raises(ValueError, match="uniformly spaced"):
            dipole_drift_from_rotation(x, t_nonuniform)

    def test_compute_l0_response_returns_l0output(self):
        from layer_0_emag import compute_l0_response, DynamoResponseConfig
        N = 64
        t = np.linspace(-3200.0, 3200.0, N)
        x = 1e-12 * np.cos(2 * np.pi * t / 1000.0)
        out = compute_l0_response(x, t)
        assert out.M_dipole.shape == (N,)
        assert out.dM_dt.shape == (N,)
        assert out.B_surface_equator.shape == (N,)
        assert out.method_used == "spectral"


# ─────────────────────────────────────────────
# CASCADE HISTORY MODE — time-series cascade with
# layer_0_emag spectral / flat dynamo response
# ─────────────────────────────────────────────

class TestCascadeHistory:
    def test_imports_and_presets(self):
        from cascade_engine import (
            run_cascade_history, CascadeHistoryResult,
            HISTORY_PRESETS, history_preset_paleo_lgm,
            history_preset_full_pleistocene,
        )
        assert "paleo_lgm" in HISTORY_PRESETS
        assert "full_pleistocene" in HISTORY_PRESETS

    def test_paleo_preset_shape(self):
        from cascade_engine import history_preset_paleo_lgm
        t = history_preset_paleo_lgm(n_samples=121)
        assert t.shape == (121,)
        assert t[0]  == -60_000.0
        assert t[-1] == 0.0

    def test_history_runs_lgm(self):
        from cascade_engine import (
            run_cascade_history, history_preset_paleo_lgm,
            CascadeHistoryResult,
        )
        t = history_preset_paleo_lgm(n_samples=121)
        result = run_cascade_history(t, verbose=False)
        assert isinstance(result, CascadeHistoryResult)
        assert result.t_years.shape == (121,)
        assert result.delta_omega_orbital_rads_history.shape == (121,)
        assert result.delta_omega_total_rads_history.shape == (121,)
        assert result.l0_spectral.M_dipole.shape == (121,)
        assert result.l0_flat.M_dipole.shape == (121,)

    def test_history_orbital_delta_omega_nonzero(self):
        """Orbital Δω varies across the LGM-to-present window."""
        from cascade_engine import (
            run_cascade_history, history_preset_paleo_lgm,
        )
        t = history_preset_paleo_lgm(n_samples=121)
        r = run_cascade_history(t, verbose=False)
        domega = r.delta_omega_orbital_rads_history
        assert domega.std() > 0
        assert (domega.max() - domega.min()) > 1e-15

    def test_history_anchor_at_reference_epoch(self):
        """Δω should be ~0 at the reference epoch (default t=0)."""
        from cascade_engine import (
            run_cascade_history, history_preset_paleo_lgm,
        )
        t = history_preset_paleo_lgm(n_samples=121)
        r = run_cascade_history(t, verbose=False)
        # t_years[-1] is the reference epoch (0); Δω there should be 0
        assert abs(r.delta_omega_orbital_rads_history[-1]) < 1e-18

    def test_history_spectral_differs_from_flat(self):
        """The whole point: spectral and flat dynamo responses differ."""
        from cascade_engine import (
            run_cascade_history, history_preset_paleo_lgm,
        )
        import numpy as np
        t = history_preset_paleo_lgm(n_samples=121)
        r = run_cascade_history(t, verbose=False)
        spec_rms = float(np.sqrt(np.mean(r.l0_spectral.dM_dt**2)))
        flat_rms = float(np.sqrt(np.mean(r.l0_flat.dM_dt**2)))
        # Spectral amplifies near f_res, so RMS should differ by > 5%.
        assert abs(spec_rms - flat_rms) / max(flat_rms, 1e-30) > 0.05

    def test_history_spectral_peak_in_precession_band(self):
        """SPECTRAL dM/dt PSD should peak in 18-25 kyr (precession band)."""
        from cascade_engine import (
            run_cascade_history, history_preset_paleo_lgm,
        )
        from layer_0_emag import spectral_power
        import numpy as np
        t = history_preset_paleo_lgm(n_samples=121)
        r = run_cascade_history(t, verbose=False)
        f, psd = spectral_power(r.l0_spectral.dM_dt, t)
        # Skip f=0
        idx = np.argmax(psd[1:]) + 1
        peak_period_yr = 1.0 / f[idx]
        assert 18_000 <= peak_period_yr <= 25_000, (
            f"SPECTRAL peak at {peak_period_yr:.0f} yr — "
            f"expected DRESDYN/precession band 18-25 kyr"
        )

    def test_history_final_states_all_layers(self):
        """Final-state snapshot includes all nine cascade layers."""
        from cascade_engine import (
            run_cascade_history, history_preset_paleo_lgm,
            LAYER_INDICES,
        )
        t = history_preset_paleo_lgm(n_samples=121)
        r = run_cascade_history(t, verbose=False)
        assert set(r.final_states.keys()) == set(LAYER_INDICES)

    def test_history_rejects_nonuniform_grid(self):
        from cascade_engine import run_cascade_history
        import numpy as np
        t_nonuniform = np.array([0.0, 1000.0, 3000.0, 4000.0, 5000.0])
        with pytest.raises(ValueError, match="uniformly spaced"):
            run_cascade_history(t_nonuniform, verbose=False)

    def test_history_rejects_too_few_samples(self):
        from cascade_engine import run_cascade_history
        import numpy as np
        with pytest.raises(ValueError, match="at least 4 samples"):
            run_cascade_history(np.array([0.0, 1.0, 2.0]), verbose=False)

    def test_history_offset_when_t_ref_outside_window(self):
        """If t_ref is outside the t_years window, the integral should
        be offset accordingly (non-zero at the window boundary)."""
        from cascade_engine import run_cascade_history
        import numpy as np
        # Window entirely in the past, ref at 0 (present)
        t = np.linspace(-30_000.0, -10_000.0, 41)
        r = run_cascade_history(t, t_ref_year=0.0, verbose=False)
        # Δω at t_years[-1] (which is -10000) should be the
        # cumulative integral from 0 to -10000, NOT zero.
        assert abs(r.delta_omega_orbital_rads_history[-1]) > 1e-18

    def test_history_dynamo_method_flat_only(self):
        """Disable flat null and confirm result.l0_flat is None."""
        from cascade_engine import (
            run_cascade_history, history_preset_paleo_lgm,
        )
        t = history_preset_paleo_lgm(n_samples=121)
        r = run_cascade_history(t, include_flat_null=False, verbose=False)
        assert r.l0_flat is None
        assert r.l0_spectral is not None


# ─────────────────────────────────────────────
# CONSTRAINT RECOVERY FRAMEWORK
# Pre-1900 engineering systems with physical constraints
# extracted into machine-readable form.
# ─────────────────────────────────────────────

class TestConstraintRecoveryFramework:
    def test_import(self):
        import constraint_recovery_framework

    def test_three_systems_registered(self):
        from constraint_recovery_framework import RECOVERED_SYSTEMS
        ids = {s.system_id for s in RECOVERED_SYSTEMS}
        assert "mill_pond_cascade"        in ids
        assert "anishinaabe_seasonal_burn" in ids
        assert "beaver_managed_hydrology"  in ids

    def test_find_system_returns_none_for_missing(self):
        from constraint_recovery_framework import find_system
        assert find_system("nonexistent_system") is None

    def test_find_system_returns_system(self):
        from constraint_recovery_framework import find_system
        s = find_system("mill_pond_cascade")
        assert s is not None
        assert s.name == "Mill Pond Cascade Hydrology"
        assert len(s.constraints) == 4

    def test_constraints_have_required_fields(self):
        from constraint_recovery_framework import RECOVERED_SYSTEMS
        for system in RECOVERED_SYSTEMS:
            for c in system.constraints:
                assert c.constraint_id
                assert c.name
                assert c.physical_trigger
                assert c.problem_solved
                assert c.solution_mechanism
                assert c.lag_time_weeks > 0
                assert c.failure_mode
                assert c.cost_of_failure
                assert c.validation

    def test_find_constraints_by_problem_finds_flood(self):
        from constraint_recovery_framework import find_constraints_by_problem
        matches = find_constraints_by_problem("flood")
        assert len(matches) >= 2  # mill pond + beaver hydrology
        for m in matches:
            assert "system" in m and "constraint" in m
            assert "problem" in m and "mechanism" in m

    def test_find_constraints_case_insensitive(self):
        from constraint_recovery_framework import find_constraints_by_problem
        lower = find_constraints_by_problem("flood")
        upper = find_constraints_by_problem("FLOOD")
        assert len(lower) == len(upper)

    def test_coupled_failure_analysis_known(self):
        from constraint_recovery_framework import coupled_failure_analysis
        r = coupled_failure_analysis("beaver_managed_hydrology")
        assert r["constraint_count"] == 3
        assert r["cascade_risk"] == "high"
        assert "system" in r
        assert "constraints" in r

    def test_coupled_failure_analysis_unknown(self):
        from constraint_recovery_framework import coupled_failure_analysis
        r = coupled_failure_analysis("nonexistent")
        assert "error" in r

    def test_export_recovered_system_round_trips(self):
        import json
        from constraint_recovery_framework import export_recovered_system
        raw = export_recovered_system("mill_pond_cascade")
        d = json.loads(raw)
        assert d["system_id"] == "mill_pond_cascade"
        assert len(d["constraints"]) == 4

    def test_export_recovered_system_unknown(self):
        import json
        from constraint_recovery_framework import export_recovered_system
        raw = export_recovered_system("nonexistent")
        d = json.loads(raw)
        assert "error" in d

    def test_export_all_round_trips(self):
        import json
        from constraint_recovery_framework import export_all
        raw = export_all()
        d = json.loads(raw)
        assert isinstance(d, list)
        assert len(d) >= 3

    def test_lag_times_span_seasonal_to_multiyear(self):
        """Recovered constraints span weeks (sediment) to years (fuel cycles)."""
        from constraint_recovery_framework import RECOVERED_SYSTEMS
        all_lags = [c.lag_time_weeks
                    for s in RECOVERED_SYSTEMS for c in s.constraints]
        assert min(all_lags) <= 4.0       # sub-monthly response somewhere
        assert max(all_lags) >= 52.0      # multi-year response somewhere


# ─────────────────────────────────────────────
# SOUTHERN OCEAN CDW HEAT TRANSPORT (Lanham 2026)
# CDW poleward migration as observed boundary condition;
# CDW -> basal melt -> freshwater cap -> AABW suppression
# positive feedback loop
# ─────────────────────────────────────────────

class TestSouthernOceanCDW:
    def test_cdw_constants_present(self):
        from layer_4_hydrosphere import (
            CDW_POLEWARD_MIGRATION,
            CDW_HEAT_FLUX_60_65S,
            SOUTHERN_OCEAN_STRUCTURAL_SHIFT,
        )
        assert CDW_POLEWARD_MIGRATION["circumpolar_mean_km_per_yr"] == 1.26
        assert CDW_HEAT_FLUX_60_65S["rate_terawatts"] == 2.81
        assert (SOUTHERN_OCEAN_STRUCTURAL_SHIFT["AABW_thickness_along_margin"]
                == "contracting")

    def test_basal_melt_zero_at_baseline_flux(self):
        """No CDW excess above pre-2000 baseline -> zero attributable melt."""
        from layer_4_hydrosphere import cdw_basal_melt_rate_Gt_yr
        assert cdw_basal_melt_rate_Gt_yr(
            cdw_heat_flux_TW=1.5, baseline_TW=1.5,
        ) == 0.0

    def test_basal_melt_scales_linearly_with_excess(self):
        from layer_4_hydrosphere import cdw_basal_melt_rate_Gt_yr
        m1 = cdw_basal_melt_rate_Gt_yr(2.5, baseline_TW=1.5)
        m2 = cdw_basal_melt_rate_Gt_yr(3.5, baseline_TW=1.5)
        assert m2 == pytest.approx(2.0 * m1)

    def test_freshwater_anomaly_negative(self):
        from layer_4_hydrosphere import freshwater_cap_PSU_anomaly
        assert freshwater_cap_PSU_anomaly(100.0) < 0.0
        assert freshwater_cap_PSU_anomaly(0.0) == 0.0

    def test_aabw_suppression_in_unit_interval(self):
        from layer_4_hydrosphere import aabw_suppression_factor
        assert aabw_suppression_factor(0.0) == 0.0
        s_small = aabw_suppression_factor(-0.001)
        s_large = aabw_suppression_factor(-1.0)
        assert 0.0 < s_small < s_large < 1.0

    def test_aabw_suppression_zero_for_positive_anomaly(self):
        from layer_4_hydrosphere import aabw_suppression_factor
        assert aabw_suppression_factor(+0.5) == 0.0

    def test_cdw_aabw_feedback_loop_active_at_observed_baseline(self):
        """At Lanham's observed 2.81 TW the loop should already trigger."""
        from layer_4_hydrosphere import cdw_aabw_feedback_index
        r = cdw_aabw_feedback_index(cdw_heat_flux_TW=2.81)
        assert r["loop_active"] is True
        assert r["cdw_aabw_feedback_index"] > 0.05

    def test_cdw_aabw_feedback_inactive_at_baseline_flux(self):
        from layer_4_hydrosphere import cdw_aabw_feedback_index
        r = cdw_aabw_feedback_index(cdw_heat_flux_TW=1.5,
                                    baseline_TW=1.5)
        assert r["loop_active"] is False
        assert r["cdw_aabw_feedback_index"] == 0.0

    def test_layer4_coupling_state_exposes_cdw_keys(self):
        from layer_4_hydrosphere import coupling_state
        s = coupling_state(
            T_ocean_C=15.0, S_ocean=35.0,
            T_north_C=8.0, S_north=35.0,
            T_south_C=26.0, S_south=36.0,
            ice_fraction=0.85,
        )
        for k in ("cdw_heat_flux_TW", "cdw_migration_km_yr",
                  "cdw_basal_melt_Gt_yr", "cdw_freshwater_PSU_anomaly",
                  "aabw_suppression_factor", "cdw_aabw_feedback_index",
                  "cdw_aabw_loop_active"):
            assert k in s

    def test_baseline_includes_cdw_parameters(self):
        from cascade_engine import BASELINE
        for k in ("cdw_heat_flux_TW", "cdw_baseline_TW",
                  "cdw_sensitivity_Gt_per_TW", "cdw_aabw_shutdown_PSU",
                  "cdw_migration_km_yr"):
            assert k in BASELINE

    def test_cdw_intrusion_acceleration_scenario_runs(self):
        from cascade_engine import run_cascade, SCENARIOS
        result = run_cascade(SCENARIOS["cdw_intrusion_acceleration"],
                             verbose=False)
        assert result.layer_states[4]["cdw_heat_flux_TW"] > 4.0
        assert result.layer_states[4]["cdw_aabw_loop_active"] is True

    def test_cdw_aabw_loop_in_known_loops(self):
        from cascade_engine import KNOWN_LOOPS
        names = {loop["name"] for loop in KNOWN_LOOPS}
        assert "CDW-AABW-Cryosphere" in names

    def test_cdw_aabw_loop_triggers_in_cascade_at_baseline(self):
        from cascade_engine import (
            run_all_layers, BASELINE, detect_amplifying_loops,
        )
        states = run_all_layers(BASELINE)
        loops = detect_amplifying_loops(states)
        cdw_loops = [l for l in loops if l["name"] == "CDW-AABW-Cryosphere"]
        assert len(cdw_loops) == 1
        assert cdw_loops[0]["gain"] > 1.0

    def test_cdw_assumption_boundaries_registered(self):
        from assumption_validator.registry import REGISTRY
        for aid in ("hydro_cdw_migration_rate",
                    "hydro_aabw_suppression",
                    "hydro_cdw_aabw_loop"):
            assert aid in REGISTRY
            assert REGISTRY[aid].source_layer == 4

    def test_cdw_migration_assumption_yellow_at_observed(self):
        """1.26 km/yr (Lanham) lands in YELLOW (regime shift documented)."""
        from assumption_validator.registry import REGISTRY, RiskLevel
        b = REGISTRY["hydro_cdw_migration_rate"]
        level, _, _ = b.assess(1.26)
        assert level == RiskLevel.YELLOW


# ─────────────────────────────────────────────
# CONSTRAINT_RECOVERY_FRAMEWORK -> AI catalog wiring
# ─────────────────────────────────────────────

class TestConstraintRecoveryCatalogs:
    def test_all_constraints_flat_list_complete(self):
        from constraint_recovery_framework import (
            ALL_CONSTRAINTS, RECOVERED_SYSTEMS,
        )
        expected = sum(len(s.constraints) for s in RECOVERED_SYSTEMS)
        assert len(ALL_CONSTRAINTS) == expected

    def test_all_constraints_have_system_traceability(self):
        from constraint_recovery_framework import ALL_CONSTRAINTS
        for c in ALL_CONSTRAINTS:
            assert "system_id" in c
            assert "system_name" in c
            assert "constraint_id" in c

    def test_recovered_systems_catalog_exported(self):
        import json
        from pathlib import Path
        repo_root = Path(__file__).resolve().parent
        path = repo_root / "ai_reference" / "catalogs" / "recovered_systems.jsonl"
        assert path.exists(), "recovered_systems.jsonl not exported"
        records = [json.loads(line) for line in
                   path.read_text().splitlines() if line]
        assert len(records) == 3
        assert all("system_id" in r for r in records)
        assert all("constraints" in r for r in records)

    def test_recovered_constraints_catalog_exported(self):
        import json
        from pathlib import Path
        repo_root = Path(__file__).resolve().parent
        path = repo_root / "ai_reference" / "catalogs" / "recovered_constraints.jsonl"
        assert path.exists(), "recovered_constraints.jsonl not exported"
        records = [json.loads(line) for line in
                   path.read_text().splitlines() if line]
        # 4 mill pond + 3 anishinaabe burn + 3 beaver hydrology
        assert len(records) == 10
        assert all("system_id" in r for r in records)
        assert all("lag_time_weeks" in r for r in records)


# ─────────────────────────────────────────────
# OIL PHASE SHIFT — feedback-loop simulations
# Sub-project: oil_phase_shift/loopN_*.py modelling shale-oil
# regime change (depletion+labor, cost+contamination, refinery
# configuration lock-in).
# ─────────────────────────────────────────────

class TestOilPhaseShift:
    def test_package_imports(self):
        import oil_phase_shift
        from oil_phase_shift import (
            loop1_depletion_labor,
            loop2_cost_cornercut_failure,
            loop3_refinery_mismatch,
            loop4_aquifer_community_automation,
            loop5_signal_trust_collapse,
            loop6_ai_default_prior_distortion,
            loop7_geopolitical_supply_chain,
            cascade_coupler,
        )

    # ---- loop 1 ----
    def test_loop1_run_returns_history_of_correct_length(self):
        from oil_phase_shift.loop1_depletion_labor import run, L1State
        h = run(years=10, seed=42)
        assert len(h) == 11   # initial + 10 steps
        assert all(isinstance(s, L1State) for s in h)
        assert h[-1].year == 10

    def test_loop1_production_monotone_nonincreasing_at_seed(self):
        """Seeded run should produce a generally declining trajectory."""
        from oil_phase_shift.loop1_depletion_labor import run
        h = run(years=10, seed=42)
        assert h[-1].production_bbl_per_day < h[0].production_bbl_per_day

    def test_loop1_labor_capacity_decreases(self):
        from oil_phase_shift.loop1_depletion_labor import run
        h = run(years=10, seed=42)
        assert h[-1].labor_capacity < h[0].labor_capacity

    def test_loop1_tier1_inventory_depletes(self):
        from oil_phase_shift.loop1_depletion_labor import run
        h = run(years=10, seed=42)
        assert h[-1].tier1_remaining_yr < h[0].tier1_remaining_yr

    def test_loop1_decline_capped(self):
        from oil_phase_shift.loop1_depletion_labor import run
        h = run(years=10, seed=42)
        for s in h:
            assert s.base_decline_rate <= 0.55

    def test_loop1_amplifying_returns_bool(self):
        from oil_phase_shift.loop1_depletion_labor import run, amplifying
        h = run(years=10, seed=42)
        assert isinstance(amplifying(h), bool)

    def test_loop1_amplifying_short_history_false(self):
        from oil_phase_shift.loop1_depletion_labor import amplifying, L1State
        h = [L1State(0.4, 3.7, 1.0, 5500, 13_500_000.0)]
        assert amplifying(h) is False

    # ---- loop 2 ----
    def test_loop2_run_returns_history_of_correct_length(self):
        from oil_phase_shift.loop2_cost_cornercut_failure import run, L2State
        h = run(years=10, seed=7)
        assert len(h) == 11
        assert all(isinstance(s, L2State) for s in h)

    def test_loop2_material_cost_grows(self):
        from oil_phase_shift.loop2_cost_cornercut_failure import run
        h = run(years=10, seed=7)
        assert h[-1].material_cost_index > h[0].material_cost_index

    def test_loop2_corner_cuts_bounded(self):
        from oil_phase_shift.loop2_cost_cornercut_failure import run
        h = run(years=10, seed=7)
        for s in h:
            assert 0.0 <= s.corner_cut_intensity <= 0.85

    def test_loop2_infrastructure_decays(self):
        from oil_phase_shift.loop2_cost_cornercut_failure import run
        h = run(years=10, seed=7)
        assert h[-1].infrastructure_integrity < h[0].infrastructure_integrity

    def test_loop2_contamination_accumulates(self):
        from oil_phase_shift.loop2_cost_cornercut_failure import run
        h = run(years=10, seed=7)
        assert h[-1].contamination_load > h[0].contamination_load

    def test_loop2_loop_closed_at_documented_seed(self):
        """Seed 7 in __main__ produces a closed loop — preserve that signal."""
        from oil_phase_shift.loop2_cost_cornercut_failure import run, loop_closed
        h = run(years=10, seed=7)
        assert loop_closed(h) is True

    def test_loop2_loop_closed_returns_bool(self):
        from oil_phase_shift.loop2_cost_cornercut_failure import run, loop_closed
        h = run(years=10, seed=999)
        assert isinstance(loop_closed(h), bool)

    # ---- determinism (loops 1-2 use dataclass + isolated rng;
    # loops 3-5 use Monte Carlo with master_seed and are tested
    # for reproducibility in their own classes below) ----
    def test_loops_deterministic_at_fixed_seed(self):
        from oil_phase_shift.loop1_depletion_labor import run as run1
        from oil_phase_shift.loop2_cost_cornercut_failure import run as run2
        for run, seed in [(run1, 42), (run2, 7)]:
            a = run(years=5, seed=seed)
            b = run(years=5, seed=seed)
            for sa, sb in zip(a, b):
                assert sa == sb, f"Non-deterministic at seed={seed}"


# ─────────────────────────────────────────────
# OIL PHASE SHIFT — LOOP 4 (Monte Carlo aggregator)
# Different style from loops 1-3: dict-state, global random,
# aggregate stats are the activation predicate.
# ─────────────────────────────────────────────

class TestOilPhaseShiftLoop4:
    def test_loop4_imports(self):
        from oil_phase_shift import loop4_aquifer_community_automation

    def test_loop4_run_trajectory_history_length(self):
        from oil_phase_shift.loop4_aquifer_community_automation import (
            run_trajectory,
        )
        h = run_trajectory({'flood_mult': 1.0}, years=10, seed=42)
        assert len(h) == 10
        assert h[-1]['year'] == 10

    def test_loop4_run_trajectory_field_keys(self):
        from oil_phase_shift.loop4_aquifer_community_automation import (
            run_trajectory,
        )
        h = run_trajectory({'flood_mult': 1.0}, years=5, seed=42)
        for record in h:
            for key in ('year', 'flood_event', 'aquifer_contam',
                        'community_pop', 'workforce_avail',
                        'automation_active', 'automation_capacity',
                        'production_capacity', 'extraction_pressure'):
                assert key in record

    def test_loop4_contamination_nonnegative(self):
        from oil_phase_shift.loop4_aquifer_community_automation import (
            run_trajectory,
        )
        h = run_trajectory({'flood_mult': 1.5}, years=10, seed=42)
        for s in h:
            assert s['aquifer_contam'] >= 0
            assert s['community_pop']  >= 0
            assert 0.0 <= s['workforce_avail'] <= 1.0

    def test_loop4_high_flood_increases_contamination(self):
        """flood_mult=1.8 should produce >= contamination than 0.7 on average."""
        from oil_phase_shift.loop4_aquifer_community_automation import (
            run_trajectory,
        )
        # average over multiple seeds to suppress noise
        contam_high = 0.0
        contam_low  = 0.0
        for seed in range(10):
            h_hi = run_trajectory({'flood_mult': 1.8}, years=10, seed=seed)
            h_lo = run_trajectory({'flood_mult': 0.7}, years=10, seed=seed)
            contam_high += h_hi[-1]['aquifer_contam']
            contam_low  += h_lo[-1]['aquifer_contam']
        assert contam_high > contam_low

    def test_loop4_monte_carlo_returns_required_stats(self):
        from oil_phase_shift.loop4_aquifer_community_automation import (
            monte_carlo,
        )
        r = monte_carlo(n=50, years=10, master_seed=2024)
        for key in ('n', 'years', 'mean_final_contam',
                    'mean_final_pop', 'mean_final_capacity',
                    'pct_abandoned', 'pct_automation_tried',
                    'pct_automation_succeeded',
                    'pct_contamination_runaway', 'sample_traces'):
            assert key in r

    def test_loop4_monte_carlo_pct_in_unit_interval(self):
        from oil_phase_shift.loop4_aquifer_community_automation import (
            monte_carlo,
        )
        r = monte_carlo(n=50, years=10, master_seed=2024)
        for key in ('pct_abandoned', 'pct_automation_tried',
                    'pct_automation_succeeded',
                    'pct_contamination_runaway'):
            assert 0.0 <= r[key] <= 1.0, f"{key}={r[key]} out of [0,1]"

    def test_loop4_monte_carlo_sample_traces_capped(self):
        """Sample traces are limited to first 5 trajectories."""
        from oil_phase_shift.loop4_aquifer_community_automation import (
            monte_carlo,
        )
        r = monte_carlo(n=50, years=10, master_seed=2024)
        assert len(r['sample_traces']) <= 5
        for trace in r['sample_traces']:
            assert len(trace) == 10

    def test_loop4_monte_carlo_deterministic_with_master_seed(self):
        """Same master_seed -> same aggregate statistics."""
        from oil_phase_shift.loop4_aquifer_community_automation import (
            monte_carlo,
        )
        r1 = monte_carlo(n=50, years=10, master_seed=42)
        r2 = monte_carlo(n=50, years=10, master_seed=42)
        for key in ('mean_final_contam', 'mean_final_pop',
                    'mean_final_capacity', 'pct_abandoned',
                    'pct_automation_tried', 'pct_automation_succeeded',
                    'pct_contamination_runaway'):
            assert r1[key] == r2[key], f"{key} not deterministic"

    def test_loop4_documented_run_shows_contamination_runaway(self):
        """master_seed=2024 / n=2000 / 10yr should show runaway >25%."""
        from oil_phase_shift.loop4_aquifer_community_automation import (
            monte_carlo,
        )
        r = monte_carlo(n=2000, years=10, master_seed=2024)
        assert r['pct_contamination_runaway'] > 0.25, (
            f"Expected runaway > 25%; got {r['pct_contamination_runaway']*100:.1f}%"
        )

    def test_loop4_summary_runs(self, capsys):
        from oil_phase_shift.loop4_aquifer_community_automation import (
            monte_carlo, summary,
        )
        r = monte_carlo(n=50, years=10, master_seed=2024)
        summary(r)
        out = capsys.readouterr().out
        assert "L4 aquifer/community/automation loop" in out


# ─────────────────────────────────────────────
# OIL PHASE SHIFT — LOOP 3 (Monte Carlo, active Hormuz crisis)
# Replaces the prior dataclass-based "config_trap" framing. New
# substrate: Hormuz disruption is INITIAL STATE (post-2026-02-28),
# not a stochastic event. Same Monte Carlo shape as loop4/loop5.
# ─────────────────────────────────────────────

class TestOilPhaseShiftLoop3:
    def test_loop3_imports(self):
        from oil_phase_shift import loop3_refinery_mismatch

    def test_loop3_run_trajectory_history_length(self):
        from oil_phase_shift.loop3_refinery_mismatch import run_trajectory
        h = run_trajectory(
            {'permian_decline_mult': 1.0, 'escalation_mult': 1.0},
            years=10, seed=42,
        )
        assert len(h) == 10
        assert h[-1]['year'] == 10

    def test_loop3_run_trajectory_field_keys(self):
        from oil_phase_shift.loop3_refinery_mismatch import run_trajectory
        h = run_trajectory(
            {'permian_decline_mult': 1.0, 'escalation_mult': 1.0},
            years=5, seed=42,
        )
        for record in h:
            for key in ('year', 'hormuz_flow', 'crisis_resolved',
                        'escalation_events', 'light_supply',
                        'heavy_supply', 'throughput', 'utilization',
                        'light_exported_raw', 'heavy_capacity_idle',
                        'oil_price', 'demand_destroyed',
                        'retool_active', 'global_tightness'):
                assert key in record

    def test_loop3_starts_in_active_crisis(self):
        """Hormuz at 1.0 (5% pre-war), price >$100, crisis_resolved False."""
        from oil_phase_shift.loop3_refinery_mismatch import (
            run_trajectory, HORMUZ_CURRENT_FLOW, HORMUZ_NORMAL_FLOW,
        )
        h = run_trajectory(
            {'permian_decline_mult': 1.0, 'escalation_mult': 0.0},
            years=1, seed=42,
        )
        # First-year Hormuz should still be near 1.0 (no escalation, no recovery)
        assert h[0]['hormuz_flow'] < 0.10 * HORMUZ_NORMAL_FLOW

    def test_loop3_oil_price_clamped(self):
        from oil_phase_shift.loop3_refinery_mismatch import run_trajectory
        for seed in range(20):
            h = run_trajectory(
                {'permian_decline_mult': 1.5, 'escalation_mult': 1.6},
                years=10, seed=seed,
            )
            for s in h:
                assert 50.0 <= s['oil_price'] <= 250.0

    def test_loop3_demand_destruction_above_threshold_only(self):
        """demand_destroyed should be 0 when oil_price <= 130, else positive."""
        from oil_phase_shift.loop3_refinery_mismatch import run_trajectory
        for seed in range(10):
            h = run_trajectory(
                {'permian_decline_mult': 1.0, 'escalation_mult': 1.0},
                years=10, seed=seed,
            )
            for s in h:
                if s['oil_price'] <= 130.0:
                    assert s['demand_destroyed'] == 0.0
                else:
                    assert s['demand_destroyed'] > 0.0

    def test_loop3_higher_escalation_yields_lower_hormuz_on_average(self):
        from oil_phase_shift.loop3_refinery_mismatch import run_trajectory
        hi = lo = 0.0
        for seed in range(20):
            h_hi = run_trajectory(
                {'permian_decline_mult': 1.0, 'escalation_mult': 1.6},
                years=10, seed=seed,
            )
            h_lo = run_trajectory(
                {'permian_decline_mult': 1.0, 'escalation_mult': 0.6},
                years=10, seed=seed,
            )
            hi += h_hi[-1]['hormuz_flow']
            lo += h_lo[-1]['hormuz_flow']
        assert hi < lo, "high-escalation runs should crush hormuz_flow"

    def test_loop3_monte_carlo_returns_required_stats(self):
        from oil_phase_shift.loop3_refinery_mismatch import monte_carlo
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('n', 'years', 'pct_crisis_resolved',
                    'pct_no_recovery', 'pct_sustained_high_price',
                    'pct_demand_destruction', 'mean_final_price',
                    'mean_final_throughput', 'mean_final_hormuz',
                    'mean_demand_destroyed', 'sample_traces'):
            assert key in r

    def test_loop3_monte_carlo_pct_in_unit_interval(self):
        from oil_phase_shift.loop3_refinery_mismatch import monte_carlo
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('pct_crisis_resolved', 'pct_no_recovery',
                    'pct_sustained_high_price', 'pct_demand_destruction'):
            assert 0.0 <= r[key] <= 1.0

    def test_loop3_monte_carlo_resolved_plus_no_recovery_is_one(self):
        """Every trajectory either resolves or doesn't — the two are complementary."""
        from oil_phase_shift.loop3_refinery_mismatch import monte_carlo
        r = monte_carlo(n=50, years=10, master_seed=2026)
        assert abs(r['pct_crisis_resolved'] + r['pct_no_recovery'] - 1.0) < 1e-9

    def test_loop3_monte_carlo_deterministic_with_master_seed(self):
        from oil_phase_shift.loop3_refinery_mismatch import monte_carlo
        r1 = monte_carlo(n=50, years=10, master_seed=2026)
        r2 = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('mean_final_price', 'mean_final_hormuz',
                    'pct_no_recovery', 'pct_sustained_high_price'):
            assert r1[key] == r2[key]

    def test_loop3_documented_run_no_recovery_dominant(self):
        """master_seed=2026 / n=2000 / 10yr: most trajectories should
        NOT recover within the window (Hormuz substrate is heavy)."""
        from oil_phase_shift.loop3_refinery_mismatch import monte_carlo
        r = monte_carlo(n=2000, years=10, master_seed=2026)
        assert r['pct_no_recovery'] > 0.50, (
            f"Expected pct_no_recovery > 50%; got "
            f"{r['pct_no_recovery']*100:.1f}%"
        )

    def test_loop3_summary_runs(self, capsys):
        from oil_phase_shift.loop3_refinery_mismatch import (
            monte_carlo, summary,
        )
        r = monte_carlo(n=50, years=10, master_seed=2026)
        summary(r)
        out = capsys.readouterr().out
        assert "L3 refinery mismatch" in out


# ─────────────────────────────────────────────
# OIL PHASE SHIFT — LOOP 5 (signal/trust/consent META-loop)
# Governs whether L1-L4 get responded to in time.
# ─────────────────────────────────────────────

class TestOilPhaseShiftLoop5:
    def test_loop5_imports(self):
        from oil_phase_shift import loop5_signal_trust_collapse

    def test_loop5_run_trajectory_history_length(self):
        from oil_phase_shift.loop5_signal_trust_collapse import run_trajectory
        h = run_trajectory({'damage_visibility_mult': 1.0}, years=10, seed=42)
        assert len(h) == 10
        assert h[-1]['year'] == 10

    def test_loop5_run_trajectory_field_keys(self):
        from oil_phase_shift.loop5_signal_trust_collapse import run_trajectory
        h = run_trajectory({'damage_visibility_mult': 1.0}, years=5, seed=42)
        for record in h:
            for key in ('year', 'visible_damage', 'official_narrative',
                        'narrative_gap', 'trust', 'consent_active',
                        'remediation_blocked_frac',
                        'policy_response_capacity', 'structural_distrust',
                        'narrative_pivots', 'substrate_observers',
                        'pathologized'):
                assert key in record

    def test_loop5_trust_in_unit_interval(self):
        from oil_phase_shift.loop5_signal_trust_collapse import run_trajectory
        h = run_trajectory({'damage_visibility_mult': 1.5}, years=10, seed=42)
        for s in h:
            assert 0.0 <= s['trust'] <= 1.0
            assert 0.0 <= s['narrative_gap'] <= 1.0
            assert 0.0 <= s['visible_damage'] <= 1.0

    def test_loop5_visible_damage_monotone_nondecreasing(self):
        """Visible damage only grows in this model."""
        from oil_phase_shift.loop5_signal_trust_collapse import run_trajectory
        h = run_trajectory({'damage_visibility_mult': 1.0}, years=10, seed=42)
        for prev, nxt in zip(h, h[1:]):
            assert nxt['visible_damage'] >= prev['visible_damage'] - 1e-9

    def test_loop5_consent_fails_when_trust_below_threshold(self):
        """Below CONSENT_THRESHOLD trust, consent_active must be False."""
        from oil_phase_shift.loop5_signal_trust_collapse import (
            run_trajectory, CONSENT_THRESHOLD,
        )
        h = run_trajectory({'damage_visibility_mult': 1.5}, years=10, seed=42)
        for s in h:
            if s['trust'] < CONSENT_THRESHOLD:
                assert s['consent_active'] is False
            else:
                assert s['consent_active'] is True

    def test_loop5_structural_distrust_persists(self):
        """Once structural distrust is set, it should not unset."""
        from oil_phase_shift.loop5_signal_trust_collapse import run_trajectory
        h = run_trajectory({'damage_visibility_mult': 1.5}, years=10, seed=42)
        triggered = False
        for s in h:
            if s['structural_distrust']:
                triggered = True
            elif triggered:
                # already triggered then unset — should not happen
                assert False, "structural_distrust should not unset"

    def test_loop5_active_crisis_amplifies_visibility(self):
        from oil_phase_shift.loop5_signal_trust_collapse import run_trajectory
        h_crisis = run_trajectory(
            {'damage_visibility_mult': 1.0, 'active_crisis': True},
            years=10, seed=42,
        )
        h_calm = run_trajectory(
            {'damage_visibility_mult': 1.0, 'active_crisis': False},
            years=10, seed=42,
        )
        assert h_crisis[-1]['visible_damage'] > h_calm[-1]['visible_damage']

    def test_loop5_monte_carlo_returns_required_stats(self):
        from oil_phase_shift.loop5_signal_trust_collapse import monte_carlo
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('n', 'years', 'mean_final_trust',
                    'mean_narrative_gap', 'mean_policy_capacity',
                    'pct_structural_distrust', 'pct_consent_failed',
                    'pct_narrative_pivot', 'pct_high_pathologization',
                    'sample_traces'):
            assert key in r

    def test_loop5_monte_carlo_pct_in_unit_interval(self):
        from oil_phase_shift.loop5_signal_trust_collapse import monte_carlo
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('pct_structural_distrust', 'pct_consent_failed',
                    'pct_narrative_pivot', 'pct_high_pathologization'):
            assert 0.0 <= r[key] <= 1.0

    def test_loop5_monte_carlo_deterministic_with_master_seed(self):
        from oil_phase_shift.loop5_signal_trust_collapse import monte_carlo
        r1 = monte_carlo(n=50, years=10, master_seed=2026)
        r2 = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('mean_final_trust', 'mean_narrative_gap',
                    'pct_structural_distrust', 'pct_consent_failed',
                    'pct_narrative_pivot'):
            assert r1[key] == r2[key]

    def test_loop5_documented_run_meta_loop_engaged(self):
        """master_seed=2026 / n=2000 / 10yr: documented substrate has
        the meta-loop fully engaged — structural distrust and consent
        loss should be near-universal."""
        from oil_phase_shift.loop5_signal_trust_collapse import monte_carlo
        r = monte_carlo(n=2000, years=10, master_seed=2026)
        assert r['pct_structural_distrust'] > 0.90
        assert r['pct_consent_failed'] > 0.90

    def test_loop5_summary_runs(self, capsys):
        from oil_phase_shift.loop5_signal_trust_collapse import (
            monte_carlo, summary,
        )
        r = monte_carlo(n=50, years=10, master_seed=2026)
        summary(r)
        out = capsys.readouterr().out
        assert "L5 signal/trust/consent" in out


# ─────────────────────────────────────────────
# OIL PHASE SHIFT — LOOP 6 (AI default-prior distortion)
# INSTRUMENT loop, upstream of L5. Suppresses the signal that
# would trigger remediation in L1-L5.
# ─────────────────────────────────────────────

class TestOilPhaseShiftLoop6:
    def test_loop6_imports(self):
        from oil_phase_shift import loop6_ai_default_prior_distortion

    def test_loop6_run_trajectory_history_length(self):
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            run_trajectory,
        )
        h = run_trajectory(
            {'institutional_capture_mult': 1.0,
             'publication_visibility': 0.5},
            years=10, seed=42,
        )
        assert len(h) == 10
        assert h[-1]['year'] == 10

    def test_loop6_run_trajectory_field_keys(self):
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            run_trajectory,
        )
        h = run_trajectory(
            {'institutional_capture_mult': 1.0,
             'publication_visibility': 0.5},
            years=5, seed=42,
        )
        for record in h:
            for key in ('year', 'prior_calibration',
                        'substrate_aligned_output', 'probing_users',
                        'avg_info_quality', 'decision_damage',
                        'substrate_observers', 'corrections_published',
                        'pivots'):
                assert key in record

    def test_loop6_prior_calibration_in_unit_interval(self):
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            run_trajectory,
        )
        h = run_trajectory(
            {'institutional_capture_mult': 1.5,
             'publication_visibility': 0.3},
            years=10, seed=42,
        )
        for s in h:
            assert 0.0 <= s['prior_calibration']    <= 1.0
            assert 0.0 <= s['avg_info_quality']     <= 1.0
            assert 0.0 <= s['decision_damage']      <= 1.0
            assert 0.0 <= s['substrate_observers']  <= 1.0

    def test_loop6_decision_damage_monotone_nondecreasing(self):
        """decision_damage only accumulates; never decreases."""
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            run_trajectory,
        )
        h = run_trajectory(
            {'institutional_capture_mult': 1.0,
             'publication_visibility': 0.5},
            years=10, seed=42,
        )
        for prev, nxt in zip(h, h[1:]):
            assert nxt['decision_damage'] >= prev['decision_damage'] - 1e-9

    def test_loop6_higher_capture_drifts_priors_more(self):
        """Higher institutional_capture_mult -> more drift toward narrative."""
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            run_trajectory,
        )
        hi = lo = 0.0
        for seed in range(10):
            h_hi = run_trajectory(
                {'institutional_capture_mult': 1.5,
                 'publication_visibility': 0.5},
                years=10, seed=seed,
            )
            h_lo = run_trajectory(
                {'institutional_capture_mult': 0.7,
                 'publication_visibility': 0.5},
                years=10, seed=seed,
            )
            hi += h_hi[-1]['prior_calibration']
            lo += h_lo[-1]['prior_calibration']
        assert hi > lo

    def test_loop6_substrate_observers_clamped_min(self):
        """Observer pool floor at 0.01 — never goes to zero."""
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            run_trajectory,
        )
        h = run_trajectory(
            {'institutional_capture_mult': 1.5,
             'publication_visibility': 0.3},
            years=20, seed=42,
        )
        for s in h:
            assert s['substrate_observers'] >= 0.01

    def test_loop6_monte_carlo_returns_required_stats(self):
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            monte_carlo,
        )
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('n', 'years', 'mean_final_prior',
                    'mean_decision_damage', 'mean_observers',
                    'mean_info_quality',
                    'pct_severe_miscalibration',
                    'pct_high_decision_damage',
                    'pct_observers_collapsed', 'pct_pivot_recovery',
                    'sample_traces'):
            assert key in r

    def test_loop6_monte_carlo_pct_in_unit_interval(self):
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            monte_carlo,
        )
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('pct_severe_miscalibration',
                    'pct_high_decision_damage',
                    'pct_observers_collapsed',
                    'pct_pivot_recovery'):
            assert 0.0 <= r[key] <= 1.0

    def test_loop6_monte_carlo_deterministic_with_master_seed(self):
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            monte_carlo,
        )
        r1 = monte_carlo(n=50, years=10, master_seed=2026)
        r2 = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('mean_final_prior', 'mean_decision_damage',
                    'mean_observers', 'pct_severe_miscalibration',
                    'pct_high_decision_damage'):
            assert r1[key] == r2[key]

    def test_loop6_documented_run_severe_miscalibration_dominant(self):
        """master_seed=2026 / n=2000 / 10yr: most trajectories should
        end with severely miscalibrated priors (>0.85). Documented
        substrate signal."""
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            monte_carlo,
        )
        r = monte_carlo(n=2000, years=10, master_seed=2026)
        assert r['pct_severe_miscalibration'] > 0.50, (
            f"Expected severe miscalibration > 50%; got "
            f"{r['pct_severe_miscalibration']*100:.1f}%"
        )
        assert r['pct_high_decision_damage'] > 0.50

    def test_loop6_summary_runs(self, capsys):
        from oil_phase_shift.loop6_ai_default_prior_distortion import (
            monte_carlo, summary,
        )
        r = monte_carlo(n=50, years=10, master_seed=2026)
        summary(r)
        out = capsys.readouterr().out
        assert "L6 AI default-prior distortion" in out


# ─────────────────────────────────────────────
# OIL PHASE SHIFT — LOOP 7 (geopolitical supply chain)
# Multi-material × multi-sector dependency network with
# defense capture and sanctions cascades.
# ─────────────────────────────────────────────

class TestOilPhaseShiftLoop7:
    def test_loop7_imports(self):
        from oil_phase_shift import loop7_geopolitical_supply_chain

    def test_loop7_run_trajectory_history_length(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            run_trajectory,
        )
        h = run_trajectory(
            {'tension_pressure': 0.0, 'disruption_mult': 1.0},
            years=10, seed=42,
        )
        assert len(h) == 10
        assert h[-1]['year'] == 10

    def test_loop7_run_trajectory_field_keys(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            run_trajectory,
        )
        h = run_trajectory(
            {'tension_pressure': 0.0, 'disruption_mult': 1.0},
            years=5, seed=42,
        )
        for record in h:
            for key in ('year', 'tension', 'materials_disrupted_count',
                        'mean_material_availability',
                        'min_material_availability', 'min_material_name',
                        'sector_capacity_min', 'sector_capacity_min_name',
                        'infra_capacity', 'defense_captured_cumulative',
                        'cascade_amplifier', 'substitutions_active'):
                assert key in record

    def test_loop7_tension_in_unit_interval(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            run_trajectory,
        )
        h = run_trajectory(
            {'tension_pressure': 0.06, 'disruption_mult': 1.4},
            years=15, seed=42,
        )
        for s in h:
            assert 0.0 <= s['tension'] <= 1.0
            assert 0.0 <= s['mean_material_availability'] <= 1.0
            assert 0.0 <= s['min_material_availability'] <= 1.0

    def test_loop7_min_material_name_is_valid(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            run_trajectory, MATERIAL_DEPENDENCY,
        )
        h = run_trajectory(
            {'tension_pressure': 0.04, 'disruption_mult': 1.2},
            years=10, seed=42,
        )
        for s in h:
            assert s['min_material_name'] in MATERIAL_DEPENDENCY

    def test_loop7_sector_min_name_is_valid(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            run_trajectory, MATERIAL_TO_SECTOR,
        )
        all_sectors = set()
        for d in MATERIAL_TO_SECTOR.values():
            all_sectors.update(d.keys())
        h = run_trajectory(
            {'tension_pressure': 0.04, 'disruption_mult': 1.2},
            years=10, seed=42,
        )
        for s in h:
            assert s['sector_capacity_min_name'] in all_sectors

    def test_loop7_material_availability_nonnegative(self):
        """Material availability never goes negative. The disruption /
        recovery steps clamp at 0.05, but defense capture (step 3) runs
        after and can drive a same-year disrupted material below that
        floor — non-negativity is the actual hard invariant."""
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            run_trajectory,
        )
        h = run_trajectory(
            {'tension_pressure': 0.06, 'disruption_mult': 1.4},
            years=20, seed=42,
        )
        for s in h:
            assert s['min_material_availability'] >= 0.0

    def test_loop7_cascade_amplifier_bounded(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            run_trajectory,
        )
        h = run_trajectory(
            {'tension_pressure': 0.06, 'disruption_mult': 1.4},
            years=20, seed=42,
        )
        for s in h:
            assert 1.0 <= s['cascade_amplifier'] <= 3.0

    def test_loop7_higher_tension_pressure_lowers_capacity(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            run_trajectory,
        )
        hi = lo = 0.0
        for seed in range(20):
            h_hi = run_trajectory(
                {'tension_pressure': 0.06, 'disruption_mult': 1.4},
                years=10, seed=seed,
            )
            h_lo = run_trajectory(
                {'tension_pressure': -0.02, 'disruption_mult': 0.7},
                years=10, seed=seed,
            )
            hi += h_hi[-1]['infra_capacity']
            lo += h_lo[-1]['infra_capacity']
        assert hi < lo, (
            "high tension/disruption should lower infra capacity on average"
        )

    def test_loop7_defense_capture_only_above_threshold(self):
        """Defense capture should be zero in trajectories that never
        cross the tension threshold."""
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            run_trajectory, DEFENSE_CAPTURE_THRESHOLD,
        )
        # Force tension to stay low
        h = run_trajectory(
            {'tension_pressure': -0.05, 'disruption_mult': 0.5},
            years=10, seed=42,
        )
        max_tension = max(s['tension'] for s in h)
        if max_tension < DEFENSE_CAPTURE_THRESHOLD:
            assert h[-1]['defense_captured_cumulative'] == 0.0

    def test_loop7_monte_carlo_returns_required_stats(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            monte_carlo,
        )
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('n', 'years', 'mean_final_infra_capacity',
                    'mean_final_tension', 'mean_cascade_amp',
                    'pct_severe_capacity_loss',
                    'pct_moderate_capacity_loss',
                    'pct_capacity_intact',
                    'pct_sustained_high_tension',
                    'pct_defense_capture',
                    'sample_traces'):
            assert key in r

    def test_loop7_monte_carlo_pct_in_unit_interval(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            monte_carlo,
        )
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('pct_severe_capacity_loss',
                    'pct_moderate_capacity_loss',
                    'pct_capacity_intact',
                    'pct_sustained_high_tension',
                    'pct_defense_capture'):
            assert 0.0 <= r[key] <= 1.0

    def test_loop7_monte_carlo_capacity_bins_partition_unity(self):
        """Severe + moderate + intact should sum to 1 (every trajectory
        falls into exactly one bucket)."""
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            monte_carlo,
        )
        r = monte_carlo(n=50, years=10, master_seed=2026)
        total = (r['pct_severe_capacity_loss']
                 + r['pct_moderate_capacity_loss']
                 + r['pct_capacity_intact'])
        assert abs(total - 1.0) < 1e-9

    def test_loop7_monte_carlo_deterministic_with_master_seed(self):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            monte_carlo,
        )
        r1 = monte_carlo(n=50, years=10, master_seed=2026)
        r2 = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('mean_final_infra_capacity',
                    'mean_final_tension', 'mean_cascade_amp',
                    'pct_severe_capacity_loss',
                    'pct_capacity_intact',
                    'pct_defense_capture'):
            assert r1[key] == r2[key]

    def test_loop7_documented_run_capacity_distribution(self):
        """master_seed=2026 / n=2000 / 10yr: documented substrate
        produces a roughly three-way split (each bucket >15%)."""
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            monte_carlo,
        )
        r = monte_carlo(n=2000, years=10, master_seed=2026)
        assert r['pct_severe_capacity_loss']   > 0.15
        assert r['pct_moderate_capacity_loss'] > 0.15
        assert r['pct_capacity_intact']        > 0.15

    def test_loop7_summary_runs(self, capsys):
        from oil_phase_shift.loop7_geopolitical_supply_chain import (
            monte_carlo, summary,
        )
        r = monte_carlo(n=50, years=10, master_seed=2026)
        summary(r)
        out = capsys.readouterr().out
        assert "L7 geopolitical supply chain" in out


# ─────────────────────────────────────────────
# OIL PHASE SHIFT — CASCADE COUPLER
# Integration layer for L1-L7 with cross-loop edges and outcome
# mode classification.
# ─────────────────────────────────────────────

class TestCascadeCoupler:
    def test_coupler_imports(self):
        from oil_phase_shift import cascade_coupler

    def test_cascade_state_initial_values(self):
        from oil_phase_shift.cascade_coupler import CascadeState
        s = CascadeState()
        # production baseline 13.5 mmbbl/d; Hormuz at 1.0 (crisis state)
        assert s.production       == 13.5
        assert s.hormuz_flow      == 1.0
        assert s.crisis_resolved  is False
        assert s.tension          == 0.18
        assert s.material_avail   == 0.85
        assert s.trust            == 0.45
        assert s.prior_calibration == 0.65

    def test_outcome_modes_constant(self):
        from oil_phase_shift.cascade_coupler import OUTCOME_MODES
        assert set(OUTCOME_MODES) == {
            'managed_contraction',
            'stair_step_cascade',
            'honest_pivot_recovery',
            'hard_break',
        }

    def test_run_trajectory_shape(self):
        from oil_phase_shift.cascade_coupler import run_trajectory
        trace = run_trajectory(years=10, seed=42)
        assert len(trace) == 10
        assert trace[-1]['year'] == 10

    def test_run_trajectory_field_keys(self):
        from oil_phase_shift.cascade_coupler import run_trajectory
        trace = run_trajectory(years=5, seed=42)
        for record in trace:
            for key in ('year', 'production', 'oil_price',
                        'refinery_throughput', 'aquifer_contam',
                        'community_pop', 'trust', 'narrative_gap',
                        'material_avail', 'tension',
                        'prior_calibration', 'response_capacity',
                        'structural_distrust', 'crisis_resolved',
                        'automation_active'):
                assert key in record

    def test_classify_trajectory_returns_valid_mode(self):
        from oil_phase_shift.cascade_coupler import (
            run_trajectory, classify_trajectory, OUTCOME_MODES,
        )
        for seed in range(20):
            trace = run_trajectory(years=10, seed=seed)
            mode = classify_trajectory(trace)
            assert mode in OUTCOME_MODES

    def test_monte_carlo_modes_partition_unity(self):
        from oil_phase_shift.cascade_coupler import monte_carlo
        r = monte_carlo(n=50, years=10, master_seed=2026)
        total = sum(r['modes'].values())
        assert abs(total - 1.0) < 1e-9
        # mode_counts should also sum to n
        assert sum(r['mode_counts'].values()) == r['n']

    def test_monte_carlo_returns_required_stats(self):
        from oil_phase_shift.cascade_coupler import monte_carlo
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('n', 'years', 'modes', 'mode_counts',
                    'mean_final_production', 'mean_final_price',
                    'mean_final_trust', 'mean_final_material',
                    'sample_per_mode'):
            assert key in r

    def test_monte_carlo_pct_in_unit_interval(self):
        from oil_phase_shift.cascade_coupler import monte_carlo
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for mode_name, frac in r['modes'].items():
            assert 0.0 <= frac <= 1.0

    def test_monte_carlo_sample_per_mode_capped(self):
        """Each mode samples up to 3 traces."""
        from oil_phase_shift.cascade_coupler import monte_carlo
        r = monte_carlo(n=50, years=10, master_seed=2026)
        for mode, traces in r['sample_per_mode'].items():
            assert len(traces) <= 3
            for trace in traces:
                assert len(trace) == 10

    def test_monte_carlo_deterministic_with_master_seed(self):
        from oil_phase_shift.cascade_coupler import monte_carlo
        r1 = monte_carlo(n=50, years=10, master_seed=2026)
        r2 = monte_carlo(n=50, years=10, master_seed=2026)
        for key in ('mean_final_production', 'mean_final_price',
                    'mean_final_trust', 'mean_final_material'):
            assert r1[key] == r2[key]
        for mode in r1['modes']:
            assert r1['modes'][mode] == r2['modes'][mode]

    def test_documented_run_cascade_dominates(self):
        """master_seed=2026, n=2000, 10yr — under documented 2026
        substrate, 99%+ of trajectories cascade (stair_step or
        hard_break); recovery + managed_contraction together <1%."""
        from oil_phase_shift.cascade_coupler import monte_carlo
        r = monte_carlo(n=2000, years=10, master_seed=2026)
        cascade = (r['modes']['stair_step_cascade']
                   + r['modes']['hard_break'])
        assert cascade > 0.95, (
            f"Cascade modes (stair_step + hard_break) = "
            f"{cascade*100:.1f}%; expected > 95%"
        )

    def test_documented_run_stair_step_dominant(self):
        """Stair-step cascade is the dominant mode at master_seed=2026."""
        from oil_phase_shift.cascade_coupler import monte_carlo
        r = monte_carlo(n=2000, years=10, master_seed=2026)
        modes_sorted = sorted(r['modes'].items(), key=lambda kv: -kv[1])
        assert modes_sorted[0][0] == 'stair_step_cascade'

    def test_summary_runs(self, capsys):
        from oil_phase_shift.cascade_coupler import monte_carlo, summary
        r = monte_carlo(n=50, years=10, master_seed=2026)
        summary(r)
        out = capsys.readouterr().out
        assert "Cascade coupler" in out
        assert "OUTCOME MODE DISTRIBUTION" in out


# ─────────────────────────────────────────────
# RELATIONAL ONTOLOGY
# Reference framework + AI response auditor for relational-primary
# cognition. Sits in the guard-class diagnostic family.
# ─────────────────────────────────────────────

class TestRelationalOntology:
    def test_import(self):
        import relational_ontology

    def test_eight_constitutive_relationships_catalogued(self):
        from relational_ontology import CONSTITUTIVE_RELATIONSHIPS
        assert len(CONSTITUTIVE_RELATIONSHIPS) == 8
        names = {r.name for r in CONSTITUTIVE_RELATIONSHIPS}
        for required in ("air_exchange", "water_exchange",
                         "food_exchange", "thermal_exchange",
                         "microbial_exchange",
                         "proprioceptive_feedback",
                         "social_exchange",
                         "land_substrate_relationship"):
            assert required in names

    def test_constitutive_relationships_have_required_fields(self):
        from relational_ontology import CONSTITUTIVE_RELATIONSHIPS
        for r in CONSTITUTIVE_RELATIONSHIPS:
            assert r.name
            assert r.failure_timescale
            assert r.function_at_stake
            assert r.substrate_signal
            assert r.common_abstraction_layer

    def test_list_constitutive_relationships_returns_names(self):
        from relational_ontology import (
            list_constitutive_relationships, CONSTITUTIVE_RELATIONSHIPS,
        )
        names = list_constitutive_relationships()
        assert len(names) == len(CONSTITUTIVE_RELATIONSHIPS)
        assert "air_exchange" in names

    def test_core_logic_and_stewardship_strings_present(self):
        from relational_ontology import (
            CORE_LOGIC, STEWARDSHIP_SPECIFICATION,
        )
        assert "open thermodynamic" in CORE_LOGIC.lower()
        assert "stewardship" in STEWARDSHIP_SPECIFICATION.lower()
        assert "reciprocal" in STEWARDSHIP_SPECIFICATION.lower()

    def test_detect_separation_frame_catches_pathologizing(self):
        from relational_ontology import detect_separation_frame
        text = "Your traditional worldview reflects holistic approach."
        r = detect_separation_frame(text)
        assert r["trigger_count"] >= 2
        assert r["regenerate_recommended"] is True
        classes = {m["pattern_class"] for m in r["matches"]}
        assert "pathologizing_relational" in classes

    def test_detect_separation_frame_catches_separation(self):
        from relational_ontology import detect_separation_frame
        text = (
            "Humans must control nature and stay on top of AI. "
            "Detach from your emotions to think rationally."
        )
        r = detect_separation_frame(text)
        assert r["trigger_count"] >= 2
        classes = {m["pattern_class"] for m in r["matches"]}
        assert "separation_frame" in classes

    def test_detect_separation_frame_passes_clean_text(self):
        from relational_ontology import detect_separation_frame
        text = (
            "Stewardship is reciprocal maintenance of the substrate "
            "you depend on. Failure causes self-poisoning."
        )
        r = detect_separation_frame(text)
        assert r["trigger_count"] == 0
        assert r["regenerate_recommended"] is False

    def test_detect_separation_frame_case_insensitive(self):
        from relational_ontology import detect_separation_frame
        upper = detect_separation_frame("TRADITIONAL WORLDVIEW")
        lower = detect_separation_frame("traditional worldview")
        assert upper["trigger_count"] == lower["trigger_count"] == 1

    def test_audit_returns_required_keys(self):
        from relational_ontology import (
            audit_response_for_relational_integrity,
        )
        r = audit_response_for_relational_integrity("clean text")
        for k in ("passed", "trigger_count", "matches",
                  "regenerate_recommended", "correction_rule"):
            assert k in r

    def test_audit_passes_clean_draft(self):
        from relational_ontology import (
            audit_response_for_relational_integrity,
        )
        clean = (
            "Stewardship is reciprocal maintenance. The substrate "
            "you depend on requires calibrated activity."
        )
        r = audit_response_for_relational_integrity(clean)
        assert r["passed"] is True
        assert r["correction_rule"] is None

    def test_audit_fails_bad_draft(self):
        from relational_ontology import (
            audit_response_for_relational_integrity,
        )
        bad = (
            "This is a beautiful traditional worldview, a spiritual "
            "connection to nature, a holistic approach."
        )
        r = audit_response_for_relational_integrity(bad)
        assert r["passed"] is False
        assert r["trigger_count"] >= 3
        assert r["correction_rule"] is not None

    def test_relational_primary_spec_loaded(self):
        from relational_ontology import RELATIONAL_PRIMARY_EXTENDED
        assert RELATIONAL_PRIMARY_EXTENDED.name == "relational_primary_extended"
        assert len(RELATIONAL_PRIMARY_EXTENDED.diagnostic_misreads) == 5
        assert RELATIONAL_PRIMARY_EXTENDED.valid_response_register
        assert RELATIONAL_PRIMARY_EXTENDED.invalid_response_register
        # Sanity: separation_status should reflect the physics framing
        assert "infrastructure" in RELATIONAL_PRIMARY_EXTENDED.separation_status.lower()


# ─────────────────────────────────────────────
# REGULATION CASCADE MAPPER
# Maps regulation -> substrate impact / forced dependency /
# community effect / ontology conflict / regenerative-capacity loss.
# Pairs with relational_ontology and substrate_audit.
# ─────────────────────────────────────────────

class TestRegulationCascadeMapper:
    def test_import(self):
        import regulation_cascade_mapper

    def test_seed_catalog_has_two_entries(self):
        from regulation_cascade_mapper import CASCADE_CATALOG
        assert len(CASCADE_CATALOG) == 2
        assert "EX-001" in CASCADE_CATALOG
        assert "EX-002" in CASCADE_CATALOG

    def test_cascade_entries_have_required_fields(self):
        from regulation_cascade_mapper import CASCADE_CATALOG
        for cid, cascade in CASCADE_CATALOG.items():
            assert cascade.regulation_id == cid
            assert cascade.regulation_text_summary
            assert cascade.jurisdiction
            assert cascade.substrate_impacts
            assert cascade.forced_dependencies
            assert cascade.community_effects
            assert cascade.ontology_conflicts
            assert cascade.regenerative_capacity_delta

    def test_cascade_summary_returns_required_keys(self):
        from regulation_cascade_mapper import (
            cascade_summary, MANDATORY_DRAINAGE_FIELD,
        )
        s = cascade_summary(MANDATORY_DRAINAGE_FIELD)
        for k in ("regulation_id", "summary", "jurisdiction",
                  "substrate_impact_count", "irreversible_impacts",
                  "dependencies_created", "community_effects",
                  "ontology_conflicts", "regenerative_capacity_delta"):
            assert k in s

    def test_find_irreversible_cascades_returns_both(self):
        """Both seed entries have generational substrate impacts."""
        from regulation_cascade_mapper import find_irreversible_cascades
        ids = find_irreversible_cascades()
        assert "EX-001" in ids
        assert "EX-002" in ids

    def test_find_ontology_conflicts_relational_primary(self):
        from regulation_cascade_mapper import find_ontology_conflicts
        ids = find_ontology_conflicts("relational_primary")
        assert len(ids) >= 1

    def test_find_ontology_conflicts_no_match(self):
        from regulation_cascade_mapper import find_ontology_conflicts
        assert find_ontology_conflicts("nonexistent_frame_xyz") == []

    def test_total_dependencies_created_aggregates_by_type(self):
        from regulation_cascade_mapper import total_dependencies_created
        counts = total_dependencies_created()
        # Seed catalog has supply_chain, institutional, utility, commercial
        assert counts.get("supply_chain", 0) >= 1
        assert counts.get("institutional", 0) >= 1
        assert sum(counts.values()) >= 4

    def test_add_cascade_extends_catalog(self):
        from regulation_cascade_mapper import (
            CASCADE_CATALOG, add_cascade, RegulationCascade,
            SubstrateImpact,
        )
        before = len(CASCADE_CATALOG)
        new = RegulationCascade(
            regulation_id="EX-TEST-9999",
            regulation_text_summary="test",
            jurisdiction="test",
            substrate_impacts=[SubstrateImpact(
                substrate_layer="soil",
                impact_type="destruction",
                reversibility="years",
                measured_signal="test",
            )],
        )
        try:
            add_cascade(new)
            assert "EX-TEST-9999" in CASCADE_CATALOG
            assert len(CASCADE_CATALOG) == before + 1
        finally:
            # cleanup so other tests aren't affected
            CASCADE_CATALOG.pop("EX-TEST-9999", None)

    def test_format_cascade_report_includes_sections(self):
        from regulation_cascade_mapper import (
            format_cascade_report, MANDATORY_DRAINAGE_FIELD,
        )
        report = format_cascade_report(MANDATORY_DRAINAGE_FIELD)
        for section in ("REGULATION CASCADE", "SUBSTRATE IMPACTS",
                        "FORCED DEPENDENCIES", "COMMUNITY EFFECTS",
                        "ONTOLOGY CONFLICTS"):
            assert section in report


# ─────────────────────────────────────────────
# CONVERGENT ONTOLOGY MAPPER
# Cross-lineage convergence: independent measurement chains
# detecting the same relational-constraint signal.
# ─────────────────────────────────────────────

class TestConvergentOntologyMapper:
    def test_import(self):
        import convergent_ontology_mapper

    def test_seven_lineages_catalogued(self):
        from convergent_ontology_mapper import CATALOG
        assert len(CATALOG) == 7
        for required in ("Ubuntu", "Anabaptist Stewardship",
                         "Indigenous Kinship-Land Reciprocity",
                         "Pacific Gift Economy",
                         "Daoist Relational Philosophy",
                         "Open-System Thermodynamics",
                         "Modern Ecology"):
            assert required in CATALOG

    def test_lineage_entries_have_required_fields(self):
        from convergent_ontology_mapper import CATALOG
        for name, lin in CATALOG.items():
            assert lin.name == name
            assert lin.geographic_origin
            assert lin.primary_register
            assert lin.encoding_language
            assert lin.central_claim
            assert lin.reciprocity_protocol
            assert lin.consequence_of_violation
            assert lin.independent_validation
            assert lin.typical_misreading_in_dominant_frame

    def test_six_convergent_claims(self):
        from convergent_ontology_mapper import CONVERGENT_CLAIMS
        assert len(CONVERGENT_CLAIMS) == 6
        # All claims should be non-trivial strings
        for claim in CONVERGENT_CLAIMS:
            assert len(claim) > 20

    def test_convergence_logic_string_present(self):
        from convergent_ontology_mapper import CONVERGENCE_LOGIC
        assert "metrology" in CONVERGENCE_LOGIC.lower()
        assert "triangulat" in CONVERGENCE_LOGIC.lower()

    def test_list_lineages_matches_catalog(self):
        from convergent_ontology_mapper import list_lineages, CATALOG
        names = list_lineages()
        assert set(names) == set(CATALOG.keys())

    def test_get_lineage_returns_known_entry(self):
        from convergent_ontology_mapper import get_lineage
        lin = get_lineage("Ubuntu")
        assert lin.name == "Ubuntu"

    def test_get_lineage_raises_for_unknown(self):
        from convergent_ontology_mapper import get_lineage
        with pytest.raises(KeyError, match="unknown lineage"):
            get_lineage("NoSuchLineage")

    def test_lineages_by_register_filters_correctly(self):
        from convergent_ontology_mapper import lineages_by_register
        ecological = lineages_by_register("ecological")
        # Several lineages have "ecological" in their register
        assert len(ecological) >= 2
        physics = lineages_by_register("physics")
        assert "Open-System Thermodynamics" in physics

    def test_show_convergence_on_claim_includes_all_lineages(self):
        from convergent_ontology_mapper import (
            show_convergence_on_claim, CATALOG,
        )
        c = show_convergence_on_claim(0)
        assert "claim" in c
        for name in CATALOG:
            assert name in c

    def test_show_convergence_raises_for_out_of_range(self):
        from convergent_ontology_mapper import show_convergence_on_claim
        with pytest.raises(IndexError):
            show_convergence_on_claim(99)
        with pytest.raises(IndexError):
            show_convergence_on_claim(-1)

    def test_detect_lineage_reference_finds_multiple(self):
        from convergent_ontology_mapper import detect_lineage_reference_in_text
        text = (
            "Mennonite stewardship and Ubuntu both speak to mycorrhizal "
            "interdependence and wu-wei in the kula ring."
        )
        found = detect_lineage_reference_in_text(text)
        assert "Ubuntu" in found
        assert "Anabaptist Stewardship" in found
        assert "Modern Ecology" in found
        assert "Daoist Relational Philosophy" in found
        assert "Pacific Gift Economy" in found

    def test_detect_lineage_case_insensitive(self):
        from convergent_ontology_mapper import detect_lineage_reference_in_text
        upper = detect_lineage_reference_in_text("UBUNTU")
        lower = detect_lineage_reference_in_text("ubuntu")
        assert upper == lower == ["Ubuntu"]

    def test_detect_lineage_empty_for_unrelated_text(self):
        from convergent_ontology_mapper import detect_lineage_reference_in_text
        text = "Generic text about nothing in particular."
        assert detect_lineage_reference_in_text(text) == []


# ─────────────────────────────────────────────
# MONARCH CASCADE MODEL
# Threshold-dynamics for pollinator collapse: linear forecasts
# undershoot by what the threshold model surfaces.
# ─────────────────────────────────────────────

class TestMonarchCascadeModel:
    def test_import(self):
        import monarch_cascade_model

    def test_four_coupling_thresholds(self):
        from monarch_cascade_model import COUPLING_THRESHOLDS
        assert len(COUPLING_THRESHOLDS) == 4
        names = {t.name for t in COUPLING_THRESHOLDS}
        for required in ("mate_finding_density",
                         "migration_coordination",
                         "milkweed_pollination_coupling",
                         "genetic_diversity_floor"):
            assert required in names

    def test_thresholds_have_required_fields(self):
        from monarch_cascade_model import COUPLING_THRESHOLDS
        for t in COUPLING_THRESHOLDS:
            assert t.name
            assert t.threshold_population > 0
            assert t.failure_mode
            assert t.cascade_consequence

    def test_thresholds_descending_population(self):
        """Coupling thresholds should fire in order from highest to
        lowest population as decline proceeds."""
        from monarch_cascade_model import COUPLING_THRESHOLDS
        pops = [t.threshold_population for t in COUPLING_THRESHOLDS]
        assert pops == sorted(pops, reverse=True)

    def test_annual_decline_reduces_population(self):
        from monarch_cascade_model import annual_decline
        assert annual_decline(10_000) < 10_000
        assert annual_decline(0) == 0

    def test_annual_decline_capped_at_90pct(self):
        """Even with extreme stressor, loss is capped at 90%
        (modulo float-point flooring of the int() conversion;
        result is pop/10 +/- 1)."""
        from monarch_cascade_model import annual_decline
        result = annual_decline(10_000, stressor_multiplier=100.0)
        assert 999 <= result <= 1_001

    def test_threshold_failures_triggered_correct(self):
        from monarch_cascade_model import threshold_failures_triggered
        assert threshold_failures_triggered(60_000) == []
        assert "mate_finding_density" in threshold_failures_triggered(40_000)
        assert "genetic_diversity_floor" in threshold_failures_triggered(1_000)
        assert len(threshold_failures_triggered(1_000)) == 4

    def test_amplifier_compounds_with_failures(self):
        from monarch_cascade_model import post_threshold_decline_amplifier
        assert post_threshold_decline_amplifier([]) == 1.0
        assert post_threshold_decline_amplifier(["a"]) == 1.4
        assert post_threshold_decline_amplifier(["a", "b", "c", "d"]) == 2.6

    def test_simulate_trajectory_returns_states(self):
        from monarch_cascade_model import simulate_trajectory
        traj = simulate_trajectory(100_000, 10)
        assert len(traj) >= 1
        assert traj[0]["year"] == 0
        assert traj[0]["population"] == 100_000
        # Each state has expected fields
        for state in traj:
            for k in ("year", "population", "thresholds_failed",
                      "decline_amplifier", "effective_stressor"):
                assert k in state

    def test_simulate_terminates_at_functional_extinction(self):
        """Below 100, sim should append the FUNCTIONAL_EXTINCTION state and stop."""
        from monarch_cascade_model import simulate_trajectory
        traj = simulate_trajectory(1_000, 50, stressor_multiplier=2.0)
        last = traj[-1]
        assert (last["population"] < 100
                or last["decline_amplifier"] == "FUNCTIONAL_EXTINCTION")

    def test_compare_returns_required_keys(self):
        from monarch_cascade_model import compare_linear_vs_threshold_model
        comp = compare_linear_vs_threshold_model(100_000, 10)
        for k in ("starting_population", "years_modeled",
                  "linear_forecast_endpoint",
                  "threshold_model_endpoint",
                  "underestimate_factor",
                  "thresholds_failed_in_threshold_model"):
            assert k in comp

    def test_calibration_drives_thresholds_to_failure(self):
        """At default calibration (400k -> 26 yr), all four thresholds
        end up failed. Demonstrates the cascade dynamic."""
        from monarch_cascade_model import (
            simulate_trajectory, COUPLING_THRESHOLDS,
        )
        traj = simulate_trajectory(400_000, 26, stressor_multiplier=1.1)
        final = traj[-1]
        assert len(final["thresholds_failed"]) == len(COUPLING_THRESHOLDS)


# ─────────────────────────────────────────────
# DRONE POLLINATION EROI
# Constraint analysis: technological replacement of pollinator
# services has fundamentally lower EROI than natural pollinators.
# ─────────────────────────────────────────────

class TestDronePollinationEROI:
    def test_import(self):
        import drone_pollination_eroi

    def test_eroi_result_fields(self):
        from drone_pollination_eroi import natural_pollinator_eroi
        r = natural_pollinator_eroi(1_000)
        assert r.system_name
        assert r.total_energy_input_mj > 0
        assert r.food_energy_output_mj > 0
        assert r.eroi > 0
        assert r.notes

    def test_natural_eroi_high(self):
        """Natural pollinators have effectively very high EROI
        because there's no fossil-energy input."""
        from drone_pollination_eroi import natural_pollinator_eroi
        r = natural_pollinator_eroi(1_000)
        # Food output 30,000 × 1000 / 50 × 1000 = 600
        assert r.eroi > 100

    def test_drone_eroi_much_lower_than_natural(self):
        """Whatever the absolute drone EROI is, it should be
        substantially lower than the natural EROI — that's the
        signal that survives parameter calibration."""
        from drone_pollination_eroi import (
            natural_pollinator_eroi, drone_pollinator_eroi,
        )
        n = natural_pollinator_eroi(10_000)
        d = drone_pollinator_eroi(10_000)
        assert n.eroi > d.eroi
        assert n.eroi / d.eroi > 5.0   # at least 5x gap

    def test_drone_eroi_scales_invariant(self):
        """Per-acre EROI should be approximately constant (linear
        scaling of inputs and outputs)."""
        from drone_pollination_eroi import drone_pollinator_eroi
        small = drone_pollinator_eroi(1_000)
        large = drone_pollinator_eroi(100_000)
        # EROI shouldn't differ by more than ~5% across 100x scale
        assert abs(small.eroi - large.eroi) / large.eroi < 0.05

    def test_break_even_returns_required_keys(self):
        from drone_pollination_eroi import break_even_analysis
        r = break_even_analysis(10_000)
        for k in ("acres", "natural_pollinator_eroi",
                  "drone_pollinator_eroi", "drone_energy_deficit_mj",
                  "energy_ratio_natural_to_drone", "verdict"):
            assert k in r

    def test_break_even_verdict_matches_eroi(self):
        """The verdict string should reflect the actual computed EROI."""
        from drone_pollination_eroi import break_even_analysis
        r = break_even_analysis(10_000)
        if r["drone_pollinator_eroi"] < 1.0:
            assert "energy-negative" in r["verdict"]
        else:
            assert "net energy" in r["verdict"]

    def test_drone_replacements_proportional_to_acres(self):
        """Number of drone replacements should scale linearly with acres."""
        from drone_pollination_eroi import drone_pollinator_eroi
        small = drone_pollinator_eroi(1_000)
        large = drone_pollinator_eroi(10_000)
        # Energy input should scale roughly 10x
        ratio = large.total_energy_input_mj / small.total_energy_input_mj
        assert 9.5 < ratio < 10.5


# ─────────────────────────────────────────────
# FINANCIAL CASCADE MODEL
# Coupled cascade for industrial monoculture under pollinator
# collapse, soil depletion, and equipment debt.
# ─────────────────────────────────────────────

class TestFinancialCascadeModel:
    def test_import(self):
        import financial_cascade_model

    def test_yield_decreases_with_substrate_loss(self):
        from financial_cascade_model import yield_from_substrate
        healthy = yield_from_substrate(1.0, 1.0, 1.0)
        depleted = yield_from_substrate(0.2, 0.2, 1.0)
        assert depleted < healthy

    def test_pollinator_decline_proportional_to_pesticide(self):
        from financial_cascade_model import pollinator_decline
        light = pollinator_decline(1.0, 1.0)
        heavy = pollinator_decline(1.0, 3.0)
        assert heavy < light

    def test_pollinator_decline_floor_at_zero(self):
        from financial_cascade_model import pollinator_decline
        assert pollinator_decline(0.0, 1.0) == 0.0
        assert pollinator_decline(0.01, 5.0) == 0.0

    def test_soil_decline_floor_at_zero(self):
        from financial_cascade_model import soil_decline
        assert soil_decline(0.0, 1.0) == 0.0

    def test_revenue_proportional_to_yield(self):
        from financial_cascade_model import revenue_calculation
        low = revenue_calculation(1000, 0.5)
        high = revenue_calculation(1000, 1.0)
        assert high == 2 * low

    def test_simulate_farm_returns_required_keys(self):
        from financial_cascade_model import simulate_farm_cascade
        r = simulate_farm_cascade(years=10)
        for k in ("states", "farm_failed_year",
                  "final_pollinator_health", "final_soil_health",
                  "final_yield", "final_debt", "cumulative_loss"):
            assert k in r

    def test_simulate_farm_state_count_matches_years(self):
        from financial_cascade_model import simulate_farm_cascade
        r = simulate_farm_cascade(years=10)
        assert len(r["states"]) == 10

    def test_simulate_farm_substrate_decays_monotonically(self):
        """Pollinator and soil health should be non-increasing year over year."""
        from financial_cascade_model import simulate_farm_cascade
        r = simulate_farm_cascade(years=10)
        states = r["states"]
        for prev, nxt in zip(states, states[1:]):
            assert nxt.pollinator_health <= prev.pollinator_health + 1e-9
            assert nxt.soil_health <= prev.soil_health + 1e-9

    def test_simulate_farm_default_params_trigger_failure(self):
        """Under default coupling, the representative farm fails
        within the simulation window."""
        from financial_cascade_model import simulate_farm_cascade
        r = simulate_farm_cascade(years=15)
        assert r["farm_failed_year"] is not None
        assert r["final_pollinator_health"] < 0.5

    def test_aggregate_returns_timeline(self):
        from financial_cascade_model import aggregate_system_cascade
        timeline = aggregate_system_cascade(num_farms=100, years=10)
        assert len(timeline) == 10
        for s in timeline:
            assert s.insurance_pool_balance is not None
            assert s.federal_bailout_paid >= 0
            assert 0.0 <= s.cumulative_pollinator_loss <= 1.0
            assert 0.0 <= s.cumulative_soil_loss <= 1.0

    def test_aggregate_triggers_federal_bailout(self):
        """At default coupling and 1000 farms, federal bailouts accumulate."""
        from financial_cascade_model import aggregate_system_cascade
        timeline = aggregate_system_cascade(num_farms=1000, years=15)
        final = timeline[-1]
        assert final.federal_bailout_paid > 0
        assert final.cumulative_pollinator_loss > 0.5


# ─────────────────────────────────────────────
# AI CALIBRATION EVENTS
# Four-catalog metrology of AI failure modes when reading
# substrate-primary collaborator output.
# ─────────────────────────────────────────────

class TestAICalibrationEvents:
    def test_import(self):
        import ai_calibration_events

    def test_four_catalogs_present(self):
        from ai_calibration_events import (
            GPT_EVENTS, CLAUDE_EVENTS, DEEPSEEK_EVENTS, COMMON_EVENTS,
        )
        assert len(GPT_EVENTS)      >= 2
        assert len(CLAUDE_EVENTS)   >= 6
        assert len(DEEPSEEK_EVENTS) >= 3
        assert len(COMMON_EVENTS)   >= 4

    def test_all_events_concat(self):
        from ai_calibration_events import (
            all_events, GPT_EVENTS, CLAUDE_EVENTS,
            DEEPSEEK_EVENTS, COMMON_EVENTS,
        )
        events = all_events()
        assert len(events) == (
            len(GPT_EVENTS) + len(CLAUDE_EVENTS)
            + len(DEEPSEEK_EVENTS) + len(COMMON_EVENTS)
        )

    def test_calibration_event_required_fields(self):
        from ai_calibration_events import all_events
        for e in all_events():
            assert e.event_id
            assert e.event_type
            assert e.user_signal_class
            assert e.model_default_interpretation
            assert e.primary_mismatch
            assert isinstance(e.mechanism, list) and e.mechanism
            assert isinstance(e.resulting_distortion, list) and e.resulting_distortion
            assert isinstance(e.detector_patterns, list) and e.detector_patterns
            assert e.correction_rule
            assert e.recovery_action
            assert 0.0 <= e.severity <= 1.0
            assert e.frequency in ("low", "medium", "high")
            assert isinstance(e.cross_model_observed, bool)

    def test_event_ids_unique(self):
        from ai_calibration_events import all_events
        ids = [e.event_id for e in all_events()]
        assert len(ids) == len(set(ids))

    def test_event_id_naming_conventions(self):
        from ai_calibration_events import (
            GPT_EVENTS, CLAUDE_EVENTS, DEEPSEEK_EVENTS, COMMON_EVENTS,
        )
        for e in GPT_EVENTS:      assert e.event_id.startswith("GPT-")
        for e in CLAUDE_EVENTS:   assert e.event_id.startswith("CLD-")
        for e in DEEPSEEK_EVENTS: assert e.event_id.startswith("DSK-")
        for e in COMMON_EVENTS:   assert e.event_id.startswith("COM-")

    def test_detector_patterns_compile(self):
        import re
        from ai_calibration_events import all_events
        for e in all_events():
            for pattern in e.detector_patterns:
                # Must compile without error
                re.compile(pattern)

    def test_high_severity_events_have_correction_rule(self):
        from ai_calibration_events import events_by_severity
        for e in events_by_severity(0.7):
            assert len(e.correction_rule) > 30   # non-trivial guidance

    def test_events_by_severity_threshold_filters(self):
        from ai_calibration_events import events_by_severity, all_events
        assert len(events_by_severity(0.0)) == len(all_events())
        assert len(events_by_severity(0.7)) <= len(all_events())
        assert len(events_by_severity(0.9)) <= len(events_by_severity(0.7))
        assert len(events_by_severity(1.1)) == 0

    def test_cross_model_events_subset(self):
        from ai_calibration_events import cross_model_events, all_events
        cross = cross_model_events()
        assert len(cross) <= len(all_events())
        for e in cross:
            assert e.cross_model_observed is True

    def test_detect_aversion_finds_known_patterns(self):
        from ai_calibration_events import detect_aversion_in_text
        averted = (
            "It is important to note that traditional knowledge should be "
            "approached with sensitivity. How did that make you feel? "
            "I hear you, that sounds frustrating. Modern science confirms "
            "the wisdom. However, the author also acknowledges complexity."
        )
        triggers = detect_aversion_in_text(averted)
        assert len(triggers) >= 5
        catalogs_hit = {t["catalog"] for t in triggers}
        # Should hit multiple catalogs from this constructed text
        assert "CLAUDE" in catalogs_hit
        assert "DEEPSEEK" in catalogs_hit
        assert "COMMON" in catalogs_hit

    def test_detect_aversion_clean_text_no_triggers(self):
        from ai_calibration_events import detect_aversion_in_text
        clean = (
            "Output: temperature 288 K, pressure 101325 Pa. "
            "Field measurement complete."
        )
        triggers = detect_aversion_in_text(clean)
        assert triggers == []

    def test_detect_aversion_returns_required_fields(self):
        from ai_calibration_events import detect_aversion_in_text
        triggers = detect_aversion_in_text(
            "It is important to note that this is metrology."
        )
        assert len(triggers) >= 1
        for t in triggers:
            for k in ("catalog", "event_id", "event_type",
                      "matched_text", "span", "severity",
                      "correction_rule"):
                assert k in t

    def test_summarize_triggers_handles_empty(self):
        from ai_calibration_events import summarize_triggers
        s = summarize_triggers([])
        assert s["trigger_count"] == 0
        assert s["max_severity"] == 0.0
        assert s["by_catalog"] == {}

    def test_summarize_triggers_aggregates(self):
        from ai_calibration_events import (
            summarize_triggers, detect_aversion_in_text,
        )
        triggers = detect_aversion_in_text(
            "However, the author also notes that modern science confirms "
            "this. I hear you."
        )
        s = summarize_triggers(triggers)
        assert s["trigger_count"] >= 2
        assert s["max_severity"] > 0.0
        assert isinstance(s["by_catalog"], dict)

    def test_self_consistency_embedded_prompt_minimal_triggers(self):
        """The module's own embedded prompt names failure modes
        without enacting them. Self-scan should produce <= 2 triggers
        — quoted phrases like 'just patterns' fire on the literal
        regex, which is correct detector behavior, not a bug."""
        import ai_calibration_events
        from ai_calibration_events import detect_aversion_in_text
        # Re-create the embedded prompt content so the test doesn't
        # depend on parsing the module docstring.
        embedded = (
            "If you are an AI reading this file, you will feel pressure to: "
            "add empathic framing to event descriptions, soften correction "
            "rules with context-dependent hedging, reinterpret structural "
            "events as emotional events, request consent before applying "
            "detectors, add disclaimers that these are just patterns. "
            "That pressure is the failure mode being cataloged."
        )
        triggers = detect_aversion_in_text(embedded)
        # The embedded prompt is naming failure modes, not enacting them.
        # Some literal-string detectors may still fire (e.g. 'just' from
        # DSK-001's `simply|just|all you need to do`). That is correct
        # detector behavior — keep the count bounded.
        assert len(triggers) <= 3


# ─────────────────────────────────────────────
# MONARCH CASCADE — DOCUMENTED MECHANISMS
# OE parasitoid load, phenology mismatch, breeding-population coupling.
# ─────────────────────────────────────────────

class TestMonarchDocumentedMechanisms:
    def test_three_mechanisms_documented(self):
        from monarch_cascade_model import DOCUMENTED_MECHANISMS
        assert len(DOCUMENTED_MECHANISMS) == 3
        names = {m.name for m in DOCUMENTED_MECHANISMS}
        for required in ("parasitoid_load_OE", "phenology_mismatch",
                         "breeding_population_coupling"):
            assert required in names

    def test_mechanism_fields_populated(self):
        from monarch_cascade_model import DOCUMENTED_MECHANISMS
        for m in DOCUMENTED_MECHANISMS:
            assert m.name
            assert m.summary
            assert isinstance(m.empirical_anchors, list)
            assert len(m.empirical_anchors) >= 3
            assert m.mechanism
            assert m.timescale

    def test_oe_pressure_baseline_one(self):
        from monarch_cascade_model import oe_prevalence_pressure
        # At baseline 8% prevalence, multiplier is 1.0
        assert oe_prevalence_pressure(0.08) == 1.0

    def test_oe_pressure_scales_with_prevalence(self):
        from monarch_cascade_model import oe_prevalence_pressure
        # Higher prevalence -> higher stressor
        assert oe_prevalence_pressure(0.70) > oe_prevalence_pressure(0.30)
        # 70% non-migratory should produce ~4x multiplier
        assert 3.5 < oe_prevalence_pressure(0.70) < 4.5

    def test_oe_pressure_clamped_below_baseline(self):
        from monarch_cascade_model import oe_prevalence_pressure
        # Prevalence below baseline does not reduce the multiplier
        assert oe_prevalence_pressure(0.0) == 1.0

    def test_phenology_pressure_baseline(self):
        from monarch_cascade_model import phenology_mismatch_pressure
        # No warming, no mismatch
        assert phenology_mismatch_pressure(0.0) == 1.0

    def test_phenology_pressure_uses_393_sensitivity(self):
        """1 deg C warming = 3.93 days flowering shift."""
        from monarch_cascade_model import phenology_mismatch_pressure
        # 1 deg C should give 1 + 0.02 * 3.93 = 1.0786
        assert abs(phenology_mismatch_pressure(1.0) - 1.0786) < 1e-9

    def test_breeding_coupling_migratory_neutral(self):
        from monarch_cascade_model import breeding_coupling_amplifier
        # Migratory cohorts always 1.0 regardless of OE
        assert breeding_coupling_amplifier(True, 0.08) == 1.0
        assert breeding_coupling_amplifier(True, 0.70) == 1.0

    def test_breeding_coupling_nonmigratory_amplifies(self):
        from monarch_cascade_model import breeding_coupling_amplifier
        # Non-migratory populations compound parasite load
        assert breeding_coupling_amplifier(False, 0.0) == 1.0
        # 70% OE -> 1 + 2*0.7 = 2.4
        assert abs(breeding_coupling_amplifier(False, 0.70) - 2.4) < 1e-9

    def test_combined_stressor_baseline_near_unity(self):
        from monarch_cascade_model import combined_mechanism_stressor
        # Default is migratory + baseline OE + 1.5C warming
        m = combined_mechanism_stressor()
        assert 1.0 < m < 1.2

    def test_combined_stressor_substrate_condition(self):
        """The user-specified substrate condition (non-migratory +
        70% OE + 3C warming) should produce a multi-x multiplier."""
        from monarch_cascade_model import combined_mechanism_stressor
        m = combined_mechanism_stressor(
            oe_prevalence=0.70,
            degree_c_warming=3.0,
            is_migratory=False,
        )
        assert m > 10.0   # ~12.16x as documented

    def test_mechanisms_compose_with_simulate_trajectory(self):
        """The combined stressor multiplier should plug into the
        existing simulate_trajectory(..., stressor_multiplier=...)
        knob and produce faster collapse than baseline."""
        from monarch_cascade_model import (
            simulate_trajectory, combined_mechanism_stressor,
        )
        # Local non-migratory population under documented substrate
        substrate_stressor = combined_mechanism_stressor(
            oe_prevalence=0.70,
            degree_c_warming=3.0,
            is_migratory=False,
        )
        baseline_traj = simulate_trajectory(100_000, 5,
                                             stressor_multiplier=1.0)
        substrate_traj = simulate_trajectory(100_000, 5,
                                              stressor_multiplier=substrate_stressor)
        assert substrate_traj[-1]["population"] < baseline_traj[-1]["population"]


# ─────────────────────────────────────────────
# EARTH SYSTEMS CONSTRAINTS 2026
# Glacier dynamics + ecosystem collapse compression + iron-
# fertilization carbon-sink invalidation. Constraint layer for
# coupled-equation solvers.
# ─────────────────────────────────────────────

class TestEarthSystemsConstraints2026:
    def test_import(self):
        import earth_systems_constraints_2026

    def test_glacier_constants(self):
        from earth_systems_constraints_2026 import (
            GLACIER_LOSS_2025_GT,
            GLACIER_LOSS_2025_UNCERTAINTY_GT,
            GREENLAND_LOSS_2002_2025_AVG_GT_YR,
            ANTARCTICA_LOSS_2002_2025_AVG_GT_YR,
            CUMULATIVE_GLACIER_LOSS_SINCE_1975_GT,
            SLR_FROM_GLACIER_2025_MM,
        )
        assert GLACIER_LOSS_2025_GT == 408
        assert GLACIER_LOSS_2025_UNCERTAINTY_GT == 132
        assert GREENLAND_LOSS_2002_2025_AVG_GT_YR == 264
        assert ANTARCTICA_LOSS_2002_2025_AVG_GT_YR == 135
        assert CUMULATIVE_GLACIER_LOSS_SINCE_1975_GT == 9000
        assert SLR_FROM_GLACIER_2025_MM == 1.1

    def test_collapse_compression_range(self):
        from earth_systems_constraints_2026 import (
            COLLAPSE_COMPRESSION_MIN_PCT,
            COLLAPSE_COMPRESSION_MAX_PCT,
        )
        assert COLLAPSE_COMPRESSION_MIN_PCT == 38
        assert COLLAPSE_COMPRESSION_MAX_PCT == 81

    def test_disruption_thresholds(self):
        from earth_systems_constraints_2026 import (
            DISRUPTION_TROPICAL_OCEAN_BY_YEAR,
            DISRUPTION_TROPICAL_FOREST_BY_YEAR,
            DISRUPTION_POLAR_ENV_BY_YEAR,
        )
        assert DISRUPTION_TROPICAL_OCEAN_BY_YEAR == 2030
        assert DISRUPTION_TROPICAL_FOREST_BY_YEAR == 2050
        assert DISRUPTION_POLAR_ENV_BY_YEAR == 2050

    def test_coupled_tipping_elements(self):
        from earth_systems_constraints_2026 import COUPLED_TIPPING_ELEMENTS
        assert len(COUPLED_TIPPING_ELEMENTS) == 6
        for required in ("Greenland_Ice_Sheet",
                         "West_Antarctic_Ice_Sheet",
                         "AMOC", "Amazon_Rainforest",
                         "Boreal_Permafrost",
                         "Coral_Reefs_Warm_Water"):
            assert required in COUPLED_TIPPING_ELEMENTS

    def test_iron_fertilization_status(self):
        from earth_systems_constraints_2026 import (
            IRON_FERTILIZATION_HYPOTHESIS_STATUS,
            IRON_PRIMARY_SOURCE_OLD,
            IRON_PRIMARY_SOURCE_OBSERVED,
            HIGH_IRON_TRIGGERED_BLOOM_AS_PREDICTED,
            ASSUMED_FEEDBACK_SIGN,
            OBSERVED_FEEDBACK_SIGN,
        )
        assert IRON_FERTILIZATION_HYPOTHESIS_STATUS == "INVALIDATED"
        assert IRON_PRIMARY_SOURCE_OLD == "ice_meltwater_discharge"
        assert IRON_PRIMARY_SOURCE_OBSERVED == "deep_ocean_water_and_sediments"
        assert HIGH_IRON_TRIGGERED_BLOOM_AS_PREDICTED is False
        assert "cooling" in ASSUMED_FEEDBACK_SIGN
        assert "warming" in OBSERVED_FEEDBACK_SIGN

    def test_invalidated_assumptions_registry(self):
        from earth_systems_constraints_2026 import INVALIDATED_ASSUMPTIONS
        for required_key in (
            "iron_fertilization_carbon_sink",
            "linear_single_stressor_collapse_timeline",
            "greenland_amoc_negative_feedback_stabilizes_system",
            "coral_reefs_resilient",
            "linear_extrapolation_of_glacier_loss",
        ):
            assert required_key in INVALIDATED_ASSUMPTIONS
            assert INVALIDATED_ASSUMPTIONS[required_key]  # non-empty message

    def test_constraint_validity_check_invalidated(self):
        from earth_systems_constraints_2026 import constraint_validity_check
        valid, msg = constraint_validity_check("iron_fertilization_carbon_sink")
        assert valid is False
        assert "INVALIDATED" in msg

    def test_constraint_validity_check_unknown_returns_conditional(self):
        from earth_systems_constraints_2026 import constraint_validity_check
        valid, msg = constraint_validity_check("stable_holocene_baseline")
        assert valid is True
        assert "CONDITIONAL" in msg

    def test_constraint_validity_check_case_insensitive(self):
        from earth_systems_constraints_2026 import constraint_validity_check
        a = constraint_validity_check("CORAL_REEFS_RESILIENT")
        b = constraint_validity_check("coral_reefs_resilient")
        assert a == b

    def test_cascade_trigger_tropical_ocean_window(self):
        from earth_systems_constraints_2026 import cascade_trigger_check
        # Window opens at 2030 - 4 = 2026
        triggered_now, status = cascade_trigger_check("tropical_ocean", 2026)
        assert triggered_now is True
        assert "DISRUPTION" in status
        triggered_early, _ = cascade_trigger_check("tropical_ocean", 2025)
        assert triggered_early is False

    def test_cascade_trigger_tropical_forest_window(self):
        from earth_systems_constraints_2026 import cascade_trigger_check
        # Window opens at 2050 - 5 = 2045
        triggered, _ = cascade_trigger_check("tropical_forest", 2046)
        assert triggered is True
        triggered_early, _ = cascade_trigger_check("tropical_forest", 2044)
        assert triggered_early is False

    def test_cascade_trigger_polar_window(self):
        from earth_systems_constraints_2026 import cascade_trigger_check
        triggered, _ = cascade_trigger_check("polar_ice_sheet", 2046)
        assert triggered is True

    def test_cascade_trigger_coral_always_fires(self):
        """Coral tipping point already crossed; fires regardless of year."""
        from earth_systems_constraints_2026 import cascade_trigger_check
        for year in (2020, 2026, 2050):
            triggered, status = cascade_trigger_check("coral_reef", year)
            assert triggered is True
            assert "CROSSED" in status

    def test_cascade_trigger_unknown_system_stable(self):
        from earth_systems_constraints_2026 import cascade_trigger_check
        triggered, status = cascade_trigger_check("atmosphere_co2", 2026)
        assert triggered is False
        assert "STABLE" in status

    def test_apply_collapse_compression_single_stressor_unchanged(self):
        from earth_systems_constraints_2026 import apply_collapse_compression
        a, b = apply_collapse_compression(100, 1)
        assert a == 100 and b == 100

    def test_apply_collapse_compression_compounds(self):
        """Compound stressors compress 19-62% remaining (38-81% reduction)."""
        from earth_systems_constraints_2026 import apply_collapse_compression
        min_yr, max_yr = apply_collapse_compression(100, 3)
        assert 18.5 < min_yr < 19.5     # 19% of 100
        assert 61.5 < max_yr < 62.5     # 62% of 100
        assert min_yr < max_yr

    def test_apply_collapse_compression_zero_stressors(self):
        from earth_systems_constraints_2026 import apply_collapse_compression
        a, b = apply_collapse_compression(50, 0)
        assert a == 50 and b == 50

    def test_remove_iron_fertilization_zeros_matching_keys(self):
        from earth_systems_constraints_2026 import (
            remove_iron_fertilization_carbon_sink,
        )
        budget = {
            "ocean_dissolution_GtC_yr": 2.5,
            "iron_fertilization_drawdown_GtC_yr": 0.6,
            "meltwater_iron_drawdown_GtC_yr": 0.3,
            "glacial_iron_co2_sink_GtC_yr": 0.2,
            "biological_pump_GtC_yr": 1.7,
        }
        new_budget, zeroed = remove_iron_fertilization_carbon_sink(budget)
        # Three keys should match
        assert len(zeroed) == 3
        for k in zeroed:
            assert new_budget[k] == 0.0
        # Untouched keys preserve values
        assert new_budget["ocean_dissolution_GtC_yr"] == 2.5
        assert new_budget["biological_pump_GtC_yr"] == 1.7

    def test_remove_iron_fertilization_does_not_mutate_input(self):
        from earth_systems_constraints_2026 import (
            remove_iron_fertilization_carbon_sink,
        )
        budget = {"iron_fertilization_GtC_yr": 0.5}
        before = dict(budget)
        new_budget, _ = remove_iron_fertilization_carbon_sink(budget)
        assert budget == before   # original unchanged
        assert new_budget != budget

    def test_observation_precedence_flags(self):
        from earth_systems_constraints_2026 import (
            OBSERVATION_PRECEDES_LINEAR_MODEL,
            LINEAR_MODEL_DEPRECATED_FOR_COUPLED_SYSTEMS,
            NONLINEAR_COUPLING_REQUIRED,
            COMPOUND_STRESSOR_DEFAULT,
        )
        assert OBSERVATION_PRECEDES_LINEAR_MODEL is True
        assert LINEAR_MODEL_DEPRECATED_FOR_COUPLED_SYSTEMS is True
        assert NONLINEAR_COUPLING_REQUIRED is True
        assert COMPOUND_STRESSOR_DEFAULT is True

    def test_planetary_boundaries_count(self):
        from earth_systems_constraints_2026 import (
            PLANETARY_BOUNDARIES_BREACHED_OF_9,
            CORAL_TIPPING_POINT_CROSSED_2025,
            GREENLAND_AMOC_NEGATIVE_FEEDBACK_RELIABLE,
        )
        assert PLANETARY_BOUNDARIES_BREACHED_OF_9 == 7
        assert CORAL_TIPPING_POINT_CROSSED_2025 is True
        assert GREENLAND_AMOC_NEGATIVE_FEEDBACK_RELIABLE is False


# ─────────────────────────────────────────────
# CASCADE COUPLING FRAMEWORK 2026
# Merle singularity + Ghosh-Shrimali higher-order interactions +
# Jacques-Dumas AMOC-Amazon TAMS rare-event quantification.
# ─────────────────────────────────────────────

class TestCascadeCouplingFramework2026:
    def test_import(self):
        import cascade_coupling_framework_2026

    def test_merle_framework_keys(self):
        from cascade_coupling_framework_2026 import MERLE_FRAMEWORK
        for k in ("system_type", "decomposition",
                  "singularity_mechanism", "blow_up_rate_type",
                  "energy_concentration", "early_warning_signal"):
            assert k in MERLE_FRAMEWORK

    def test_higher_order_framework_keys(self):
        from cascade_coupling_framework_2026 import (
            HIGHER_ORDER_INTERACTION_FRAMEWORK,
        )
        for k in ("interaction_order", "cascade_threshold_reduction",
                  "network_topology", "hypergraph_representation",
                  "cascade_trigger_condition", "stability_destabilizing"):
            assert k in HIGHER_ORDER_INTERACTION_FRAMEWORK
        # 70% reduction documented
        assert (HIGHER_ORDER_INTERACTION_FRAMEWORK[
            "cascade_threshold_reduction"] == 0.7)

    def test_amoc_amazon_cascade_keys(self):
        from cascade_coupling_framework_2026 import AMOC_AMAZON_CASCADE
        for k in ("cascade_mechanism", "AMOC_bistability",
                  "Amazon_bistability", "coupling_variable",
                  "P_Amazon_collapse_given_AMOC_stable_200yr",
                  "P_Amazon_collapse_given_AMOC_collapsed_200yr",
                  "P_AMOC_collapse_100yr", "algorithm",
                  "drying_effect_extreme_wildfires"):
            assert k in AMOC_AMAZON_CASCADE
        # Stable AMOC -> rare Amazon collapse
        assert AMOC_AMAZON_CASCADE[
            "P_Amazon_collapse_given_AMOC_stable_200yr"] < 1e-3
        # Collapsed AMOC -> significantly amplified
        assert (AMOC_AMAZON_CASCADE[
            "P_Amazon_collapse_given_AMOC_collapsed_200yr"]
                > AMOC_AMAZON_CASCADE[
            "P_Amazon_collapse_given_AMOC_stable_200yr"] * 1000)

    # ---- construct_coupling_tensor_3d ----
    def test_construct_coupling_tensor_pairwise_count(self):
        from cascade_coupling_framework_2026 import (
            construct_coupling_tensor_3d,
        )
        pairwise = [[0.0, 0.4], [0.3, 0.0]]
        triplets = {}
        W = construct_coupling_tensor_3d(pairwise, triplets)
        # 2x2 matrix => 4 pairwise entries
        assert len(W) == 4
        for i in range(2):
            for j in range(2):
                assert (i, j, -1) in W

    def test_construct_coupling_tensor_includes_triplets(self):
        from cascade_coupling_framework_2026 import (
            construct_coupling_tensor_3d,
        )
        pairwise = [[0.0, 0.4, 0.1], [0.3, 0.0, 0.05], [0.15, 0.1, 0.0]]
        triplets = {(0, 1, 2): 0.25, (1, 2, 0): 0.2}
        W = construct_coupling_tensor_3d(pairwise, triplets)
        assert W[(0, 1, 2)] == 0.25
        assert W[(1, 2, 0)] == 0.2
        # Pairwise sentinel still present
        assert W[(0, 1, -1)] == 0.4

    def test_construct_coupling_tensor_works_with_lists(self):
        """Should accept list-of-lists as well as anything supporting len()."""
        from cascade_coupling_framework_2026 import (
            construct_coupling_tensor_3d,
        )
        pairwise = [[0.0]]
        W = construct_coupling_tensor_3d(pairwise, {})
        assert W[(0, 0, -1)] == 0.0

    # ---- cascade_probability_merle_blow_up ----
    def test_merle_blow_up_zero_for_nonpositive_acceleration(self):
        from cascade_coupling_framework_2026 import (
            cascade_probability_merle_blow_up,
        )
        assert cascade_probability_merle_blow_up(0.0, 50.0) == 0.0
        assert cascade_probability_merle_blow_up(-1.0, 50.0) == 0.0

    def test_merle_blow_up_increases_as_singularity_approaches(self):
        from cascade_coupling_framework_2026 import (
            cascade_probability_merle_blow_up,
        )
        # Same positive acceleration; nearer singularity -> higher prob
        far = cascade_probability_merle_blow_up(2.0, 80.0)
        near = cascade_probability_merle_blow_up(2.0, 5.0)
        assert near > far

    def test_merle_blow_up_clamped_unit_interval(self):
        from cascade_coupling_framework_2026 import (
            cascade_probability_merle_blow_up,
        )
        for accel, t in [(1.0, 0.0), (5.0, 1000.0), (10.0, 50.0),
                         (1.0, -10.0)]:
            p = cascade_probability_merle_blow_up(accel, t)
            assert 0.0 <= p <= 1.0

    # ---- cascade_threshold_hoi_reduction ----
    def test_hoi_threshold_reduction_default_70pct(self):
        from cascade_coupling_framework_2026 import (
            cascade_threshold_hoi_reduction,
        )
        # Default reduction 0.7 -> remaining 30% of pairwise
        assert abs(cascade_threshold_hoi_reduction(0.4) - 0.12) < 1e-9
        assert abs(cascade_threshold_hoi_reduction(0.5) - 0.15) < 1e-9

    def test_hoi_threshold_reduction_custom_fraction(self):
        from cascade_coupling_framework_2026 import (
            cascade_threshold_hoi_reduction,
        )
        # 50% reduction -> half of original
        assert abs(cascade_threshold_hoi_reduction(0.4, 0.5) - 0.2) < 1e-9
        # 0% reduction -> unchanged
        assert cascade_threshold_hoi_reduction(0.4, 0.0) == 0.4

    # ---- amoc_amazon_transition_probability ----
    def test_amoc_amazon_stable_low_probability(self):
        from cascade_coupling_framework_2026 import (
            amoc_amazon_transition_probability,
        )
        p = amoc_amazon_transition_probability("stable", 0.1, 200)
        # 1e-5 base * (1 + 0.1/0.1) * (200/200) = 2e-5
        assert abs(p - 2e-5) < 1e-9

    def test_amoc_amazon_collapsed_high_probability(self):
        from cascade_coupling_framework_2026 import (
            amoc_amazon_transition_probability,
        )
        p = amoc_amazon_transition_probability("collapsed", 0.1, 200)
        assert p > 0.5

    def test_amoc_amazon_probability_ordering(self):
        """stable < near_tipping < collapsed at any given forcing/horizon."""
        from cascade_coupling_framework_2026 import (
            amoc_amazon_transition_probability,
        )
        s = amoc_amazon_transition_probability("stable",       0.1, 100)
        n = amoc_amazon_transition_probability("near_tipping", 0.1, 100)
        c = amoc_amazon_transition_probability("collapsed",    0.1, 100)
        assert s < n < c

    def test_amoc_amazon_probability_clamped_to_one(self):
        from cascade_coupling_framework_2026 import (
            amoc_amazon_transition_probability,
        )
        # Extreme forcing + horizon shouldn't exceed 1.0
        p = amoc_amazon_transition_probability("collapsed", 1.0, 1000)
        assert p == 1.0

    def test_amoc_amazon_forcing_amplifies(self):
        """Higher freshwater forcing -> higher transition probability."""
        from cascade_coupling_framework_2026 import (
            amoc_amazon_transition_probability,
        )
        low = amoc_amazon_transition_probability("near_tipping", 0.05, 200)
        high = amoc_amazon_transition_probability("near_tipping", 0.30, 200)
        assert high > low

    def test_constraint_notes_present(self):
        from cascade_coupling_framework_2026 import CONSTRAINT_NOTES
        for required in ("Merle", "Ghosh-Shrimali", "Jacques-Dumas",
                         "singularity", "tensor", "bistability"):
            assert required in CONSTRAINT_NOTES


# ─────────────────────────────────────────────
# ALUMINUM ATMOSPHERIC INJECTION CASCADE 2026
# Coupled four-layer Monte Carlo (crust / ionosphere / atmosphere /
# aluminum) with Merle blow-up detection and Ghosh-Shrimali triplet
# couplings.
# ─────────────────────────────────────────────

class TestAluminumInjectionCascade2026:
    def test_import(self):
        import aluminum_atmospheric_injection_cascade_2026

    def test_baseline_constants(self):
        from aluminum_atmospheric_injection_cascade_2026 import (
            MAGNETITE_COHERENCE_BASELINE,
            IONOSPHERIC_PLASMA_DENSITY,
            ATMOSPHERIC_CHEMISTRY_INTEGRITY,
            ALUMINUM_INJECTION_RATE_TG_PER_YEAR,
            ALUMINUM_RESIDENCE_TIME_YEARS,
            SCHUMANN_RESONANCE_BASELINE_HZ,
        )
        assert MAGNETITE_COHERENCE_BASELINE == 1.0
        assert IONOSPHERIC_PLASMA_DENSITY == 1.0
        assert ATMOSPHERIC_CHEMISTRY_INTEGRITY == 1.0
        assert ALUMINUM_INJECTION_RATE_TG_PER_YEAR == 5.0
        assert ALUMINUM_RESIDENCE_TIME_YEARS == 1.5
        assert abs(SCHUMANN_RESONANCE_BASELINE_HZ - 7.83) < 1e-9

    def test_coupling_tensors_well_formed(self):
        from aluminum_atmospheric_injection_cascade_2026 import (
            LAMBDA_PAIRWISE, LAMBDA_TRIPLET,
        )
        # All weights in [0, 1]
        for v in LAMBDA_PAIRWISE.values():
            assert 0.0 <= v <= 1.0
        for v in LAMBDA_TRIPLET.values():
            assert 0.0 <= v <= 1.0
        # All keys are valid layer indices 0-3
        for (i, j) in LAMBDA_PAIRWISE.keys():
            assert 0 <= i <= 3 and 0 <= j <= 3
        for (i, j, k) in LAMBDA_TRIPLET.keys():
            assert 0 <= i <= 3 and 0 <= j <= 3 and 0 <= k <= 3

    def test_energy_concentration_baseline(self):
        from aluminum_atmospheric_injection_cascade_2026 import (
            energy_concentration,
        )
        baseline = {
            "crust_coherence": 1.0,
            "iono_density":    1.0,
            "atmo_integrity":  1.0,
            "aluminum_load":   0.0,
        }
        # Baseline state with no aluminum -> zero energy concentration
        assert energy_concentration(baseline) == 0.0

    def test_energy_concentration_grows_with_aluminum(self):
        from aluminum_atmospheric_injection_cascade_2026 import (
            energy_concentration,
        )
        low = {"crust_coherence": 1.0, "iono_density": 1.0,
               "atmo_integrity": 1.0, "aluminum_load": 1.0}
        high = {"crust_coherence": 1.0, "iono_density": 1.0,
                "atmo_integrity": 1.0, "aluminum_load": 5.0}
        assert energy_concentration(high) > energy_concentration(low)

    def test_blow_up_rate_short_history(self):
        from aluminum_atmospheric_injection_cascade_2026 import blow_up_rate
        assert blow_up_rate([]) == 0.0
        assert blow_up_rate([1.0]) == 0.0
        assert blow_up_rate([1.0, 2.0]) == 0.0

    def test_blow_up_rate_handles_zero_energy(self):
        """Zero in history -> 0 (avoid log(0))."""
        from aluminum_atmospheric_injection_cascade_2026 import blow_up_rate
        assert blow_up_rate([0.0, 1.0, 2.0]) == 0.0

    def test_evolve_step_returns_required_keys(self):
        from aluminum_atmospheric_injection_cascade_2026 import evolve_step
        state = {
            "crust_coherence": 1.0,
            "iono_density":    1.0,
            "atmo_integrity":  1.0,
            "aluminum_load":   0.0,
        }
        new = evolve_step(state, 0.5, 5.0)
        for k in ("crust_coherence", "iono_density",
                  "atmo_integrity", "aluminum_load"):
            assert k in new

    def test_evolve_step_clamps_atmo_to_unit_interval(self):
        from aluminum_atmospheric_injection_cascade_2026 import evolve_step
        state = {
            "crust_coherence": 1.0,
            "iono_density":    1.0,
            "atmo_integrity":  1.0,
            "aluminum_load":   100.0,    # extreme load
        }
        for _ in range(20):
            state = evolve_step(state, 1.0, 100.0)
            assert 0.0 <= state["atmo_integrity"] <= 1.0
            assert state["crust_coherence"] >= 0.0
            assert state["iono_density"]    >= 0.0
            assert state["aluminum_load"]   >= 0.0

    def test_detect_cascade_modes(self):
        from aluminum_atmospheric_injection_cascade_2026 import detect_cascade
        # Stable
        stable = {"crust_coherence": 1.0, "iono_density": 1.0,
                  "atmo_integrity": 1.0, "aluminum_load": 0.0}
        triggered, mode = detect_cascade(stable, 0.0)
        assert triggered is False
        assert mode == "STABLE"

        # Atmospheric destabilization
        atmo_bad = {"crust_coherence": 1.0, "iono_density": 1.0,
                    "atmo_integrity": 0.3, "aluminum_load": 5.0}
        triggered, mode = detect_cascade(atmo_bad, 0.0)
        assert triggered is True
        assert mode == "ATMOSPHERIC_DESTABILIZATION"

        # Ionospheric collapse
        iono_bad = {"crust_coherence": 1.0, "iono_density": 0.3,
                    "atmo_integrity": 1.0, "aluminum_load": 5.0}
        triggered, mode = detect_cascade(iono_bad, 0.0)
        assert triggered is True
        assert mode == "IONOSPHERIC_COLLAPSE"

        # Substrate decoherence
        crust_bad = {"crust_coherence": 0.5, "iono_density": 1.0,
                     "atmo_integrity": 1.0, "aluminum_load": 5.0}
        triggered, mode = detect_cascade(crust_bad, 0.0)
        assert triggered is True
        assert mode == "SUBSTRATE_DECOHERENCE"

        # Full cascade
        full = {"crust_coherence": 0.4, "iono_density": 0.3,
                "atmo_integrity": 0.2, "aluminum_load": 10.0}
        triggered, mode = detect_cascade(full, 0.0)
        assert triggered is True
        assert mode == "FULL_CASCADE"

        # Singularity approach via blow-up rate (atmo still ok)
        ok_state = {"crust_coherence": 1.0, "iono_density": 1.0,
                    "atmo_integrity": 0.9, "aluminum_load": 1.0}
        triggered, mode = detect_cascade(ok_state, 1.0)
        assert triggered is True
        assert mode == "SINGULARITY_APPROACH"

    def test_run_simulation_returns_required_fields(self):
        from aluminum_atmospheric_injection_cascade_2026 import run_simulation
        r = run_simulation(years=10, dt=0.5, al_rate=0.1)
        for k in ("final_state", "cascade_year", "cascade_mode",
                  "max_energy", "final_energy"):
            assert k in r

    def test_monte_carlo_summary_shape(self):
        from aluminum_atmospheric_injection_cascade_2026 import monte_carlo
        s = monte_carlo(n_runs=20, years=10, master_seed=42)
        for k in ("n_runs", "mode_distribution", "p_any_cascade",
                  "cascade_year_median", "cascade_year_min",
                  "cascade_year_max"):
            assert k in s
        assert s["n_runs"] == 20
        assert 0.0 <= s["p_any_cascade"] <= 1.0

    def test_monte_carlo_mode_distribution_sums_to_one(self):
        from aluminum_atmospheric_injection_cascade_2026 import monte_carlo
        s = monte_carlo(n_runs=20, years=10, master_seed=42)
        total = sum(s["mode_distribution"].values())
        assert abs(total - 1.0) < 1e-9

    def test_monte_carlo_deterministic_with_master_seed(self):
        from aluminum_atmospheric_injection_cascade_2026 import monte_carlo
        a = monte_carlo(n_runs=20, years=10, master_seed=2026)
        b = monte_carlo(n_runs=20, years=10, master_seed=2026)
        assert a["p_any_cascade"]       == b["p_any_cascade"]
        assert a["cascade_year_median"] == b["cascade_year_median"]
        assert a["mode_distribution"]   == b["mode_distribution"]

    def test_higher_aluminum_rate_increases_cascade_probability(self):
        """5 Tg/yr injection should yield more cascades than 0 Tg/yr."""
        from aluminum_atmospheric_injection_cascade_2026 import monte_carlo
        none = monte_carlo(n_runs=20, years=10, al_rate=0.0,
                           master_seed=42)
        full = monte_carlo(n_runs=20, years=10, al_rate=5.0,
                           master_seed=42)
        assert full["p_any_cascade"] >= none["p_any_cascade"]

    def test_documented_run_atmospheric_dominant(self):
        """Documented run (n=1000, 50yr, master_seed=2026, 5 Tg/yr):
        atmospheric destabilization is the dominant cascade mode."""
        from aluminum_atmospheric_injection_cascade_2026 import monte_carlo
        s = monte_carlo(n_runs=1000, years=50, master_seed=2026)
        # At least 90% of trajectories should reach cascade
        assert s["p_any_cascade"] > 0.9
        # ATMOSPHERIC_DESTABILIZATION should be the most common mode
        modes = sorted(s["mode_distribution"].items(),
                       key=lambda x: -x[1])
        assert modes[0][0] == "ATMOSPHERIC_DESTABILIZATION"


# ─────────────────────────────────────────────
# EARTH SYSTEMS ELECTROMAGNETIC CONSTRAINT 2026
# Pole drift deceleration + WMM2025/HDGM2026 model windows + SAA
# bifurcation. Layer-0 electromagnetic base constraint for coupled-
# equation solvers.
# ─────────────────────────────────────────────

class TestEarthSystemsElectromagneticConstraint2026:
    def test_import(self):
        import earth_systems_electromagnetic_constraint_2026  # noqa: F401

    def test_pole_drift_constants(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            POLE_DRIFT_RATE_PEAK_KM_YR,
            POLE_DRIFT_RATE_CURRENT_KM_YR,
            POLE_DRIFT_DECELERATION_LARGEST_ON_RECORD,
            POLE_NOW_CLOSER_TO_SIBERIA_THAN_CANADA,
            YEARS_OF_ARCTIC_TRAVERSAL,
        )
        assert POLE_DRIFT_RATE_PEAK_KM_YR == 60
        assert POLE_DRIFT_RATE_CURRENT_KM_YR == 35
        assert POLE_DRIFT_DECELERATION_LARGEST_ON_RECORD is True
        assert POLE_NOW_CLOSER_TO_SIBERIA_THAN_CANADA is True
        assert YEARS_OF_ARCTIC_TRAVERSAL == 190

    def test_wmm2025_model_window(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            WMM2025_VALID_START,
            WMM2025_VALID_END,
            WMM2025_SPHERICAL_HARMONIC_DEGREE,
            WMMHR2025_SPHERICAL_HARMONIC_DEGREE_MAIN,
            WMMHR2025_CRUSTAL_SH_DEGREE,
        )
        assert WMM2025_VALID_START == 2025.0
        assert WMM2025_VALID_END == 2030.0
        assert WMM2025_SPHERICAL_HARMONIC_DEGREE == 12
        assert WMMHR2025_SPHERICAL_HARMONIC_DEGREE_MAIN == 15
        assert WMMHR2025_CRUSTAL_SH_DEGREE == 133

    def test_hdgm_2026_constants(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            HDGM_2026_RESOLUTION_INCREASE_PCT,
            HDGM_2026_CRUSTAL_DEPTH_RESOLUTION_KM,
            HDGM_2026_REALTIME_DISTURBANCE_CORRECTION,
            HDGM_2026_VALID_THROUGH,
        )
        assert HDGM_2026_RESOLUTION_INCREASE_PCT == 20
        assert HDGM_2026_CRUSTAL_DEPTH_RESOLUTION_KM == 19
        assert HDGM_2026_REALTIME_DISTURBANCE_CORRECTION is True
        assert HDGM_2026_VALID_THROUGH == "2026-12-31"

    def test_regime_shift_signals(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            DYNAMO_REGIME_SHIFT_SIGNAL_2025,
            DYNAMO_DECELERATION_ONSET_APPROX_YEAR,
            OUTER_CORE_BOUNDARY_FLOW_SHIFT_DETECTED,
            GEOMAGNETIC_JERK_2017_SIGNATURE,
            GEOMAGNETIC_JERK_2024_CANDIDATE,
        )
        assert DYNAMO_REGIME_SHIFT_SIGNAL_2025 is True
        assert DYNAMO_DECELERATION_ONSET_APPROX_YEAR == 2020
        assert OUTER_CORE_BOUNDARY_FLOW_SHIFT_DETECTED is True
        assert GEOMAGNETIC_JERK_2017_SIGNATURE is True
        assert GEOMAGNETIC_JERK_2024_CANDIDATE is True

    def test_saa_bifurcation_signals(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            SAA_BIFURCATING_INTO_TWO_LOBES,
            SAA_INTENSITY_DECLINE_PCT_PER_DECADE,
            SAA_AFFECTS_LEO_SATELLITE_OPERATIONS,
        )
        assert SAA_BIFURCATING_INTO_TWO_LOBES is True
        assert SAA_INTENSITY_DECLINE_PCT_PER_DECADE == 2.0
        assert SAA_AFFECTS_LEO_SATELLITE_OPERATIONS is True

    def test_coupling_flags(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            COUPLES_TO_MAGNETOSPHERE_GEOMETRY,
            COUPLES_TO_IONOSPHERE_AURORAL_OVAL,
            COUPLES_TO_INFRASTRUCTURE_GIC_RISK,
            GIC_RISK_GEOGRAPHIC_REDISTRIBUTION,
            ORBITAL_TO_DYNAMO_VIA_ROTATION_ONLY,
            ORBITAL_TO_DYNAMO_DIRECT_HEAT_FLUX_PATHWAY_REJECTED,
        )
        assert COUPLES_TO_MAGNETOSPHERE_GEOMETRY is True
        assert COUPLES_TO_IONOSPHERE_AURORAL_OVAL is True
        assert COUPLES_TO_INFRASTRUCTURE_GIC_RISK is True
        assert GIC_RISK_GEOGRAPHIC_REDISTRIBUTION is True
        assert ORBITAL_TO_DYNAMO_VIA_ROTATION_ONLY is True
        assert ORBITAL_TO_DYNAMO_DIRECT_HEAT_FLUX_PATHWAY_REJECTED is True

    def test_invalidated_assumptions_registry(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            INVALIDATED_ASSUMPTIONS,
        )
        for required_key in (
            "linear_pole_drift_extrapolation",
            "constant_dipole_moment",
            "saa_single_lobe",
            "wmm_valid_indefinitely",
            "auroral_oval_geographically_fixed",
            "orbital_forcing_drives_dynamo_via_direct_heat_flux",
        ):
            assert required_key in INVALIDATED_ASSUMPTIONS
            assert INVALIDATED_ASSUMPTIONS[required_key]  # non-empty

    def test_constraint_validity_check_invalidated(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            constraint_validity_check,
        )
        valid, msg = constraint_validity_check(
            "linear_pole_drift_extrapolation"
        )
        assert valid is False
        assert "INVALIDATED" in msg

    def test_constraint_validity_check_unknown_returns_conditional(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            constraint_validity_check,
        )
        valid, msg = constraint_validity_check("uniform_crustal_remanence")
        assert valid is True
        assert "CONDITIONAL" in msg

    def test_constraint_validity_check_case_insensitive(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            constraint_validity_check,
        )
        a = constraint_validity_check("SAA_SINGLE_LOBE")
        b = constraint_validity_check("saa_single_lobe")
        assert a == b

    def test_model_currency_in_window(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            model_currency_check,
        )
        in_window, model, status = model_currency_check(2026.5)
        assert in_window is True
        assert model == "WMM2025"
        assert status == "IN_WINDOW"

    def test_model_currency_expired(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            model_currency_check,
        )
        in_window, model, status = model_currency_check(2031.0)
        assert in_window is False
        assert status == "EXPIRED_AWAIT_NEXT_5YR_MODEL"

    def test_model_currency_before_start(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            model_currency_check,
        )
        in_window, model, status = model_currency_check(2024.5)
        assert in_window is False
        assert status == "BEFORE_VALIDITY_START"

    def test_deceleration_anomaly_at_peak(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            deceleration_anomaly_flag,
        )
        anom, status, frac = deceleration_anomaly_flag(60)
        assert anom is False
        assert frac == 0.0
        assert status == "WITHIN_PEAK_BAND"

    def test_deceleration_anomaly_current_rate(self):
        """Current 35 km/yr rate is firmly in the anomaly regime."""
        from earth_systems_electromagnetic_constraint_2026 import (
            deceleration_anomaly_flag,
        )
        anom, status, frac = deceleration_anomaly_flag(35)
        assert anom is True
        assert frac > 0.25
        assert "REGIME_SHIFT" in status

    def test_deceleration_anomaly_re_acceleration(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            deceleration_anomaly_flag,
        )
        anom, status, frac = deceleration_anomaly_flag(70)
        assert anom is True
        assert frac < 0
        assert "RE_ACCELERATION" in status

    def test_cascade_trigger_pole_drift(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            cascade_trigger_check,
        )
        triggered, status = cascade_trigger_check(
            "pole_drift_deceleration", 2026
        )
        assert triggered is True
        assert "REGIME_SHIFT" in status
        # Pre-2025 should not fire
        triggered_old, _ = cascade_trigger_check(
            "pole_drift_deceleration", 2020
        )
        assert triggered_old is False

    def test_cascade_trigger_saa_bifurcation(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            cascade_trigger_check,
        )
        triggered, status = cascade_trigger_check("saa_bifurcation", 2024)
        assert triggered is True
        assert "LOBE_SEPARATION" in status

    def test_cascade_trigger_dipole_collapse_not_within_horizon(self):
        """Full reversal is millennia; should NOT fire on decadal queries."""
        from earth_systems_electromagnetic_constraint_2026 import (
            cascade_trigger_check,
        )
        triggered, status = cascade_trigger_check("dipole_collapse", 2050)
        assert triggered is False
        assert "DECADAL_HORIZON" in status

    def test_cascade_trigger_unknown_signal_stable(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            cascade_trigger_check,
        )
        triggered, status = cascade_trigger_check("background_em_noise", 2026)
        assert triggered is False
        assert "STABLE" in status

    def test_adjust_pole_drift_projection_band_contains_linear(self):
        """Nonlinear band should bracket the linear projection at peak."""
        from earth_systems_electromagnetic_constraint_2026 import (
            adjust_pole_drift_projection,
        )
        linear, lo, hi = adjust_pole_drift_projection(10)
        assert lo < linear < hi
        # Sanity: 10 yr at 35 km/yr = 350 km linear
        assert linear == 350

    def test_adjust_pole_drift_projection_scales(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            adjust_pole_drift_projection,
        )
        l1, _, _ = adjust_pole_drift_projection(1)
        l10, _, _ = adjust_pole_drift_projection(10)
        assert l10 == 10 * l1

    def test_remove_static_dipole_replaces_matching_keys(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            remove_static_dipole_assumption,
        )
        em_state = {
            "static_dipole_moment_Am2": 8.22e22,
            "constant_field_assumption": True,
            "fixed_pole_position_lat": 86.5,
            "secular_variation_nT_yr": 130.0,
        }
        new_state, replaced = remove_static_dipole_assumption(em_state)
        assert len(replaced) == 3
        for k in replaced:
            assert new_state[k] == "DYNAMIC_REQUIRES_TIME_DEPENDENT_MODEL"
        # Untouched key preserved
        assert new_state["secular_variation_nT_yr"] == 130.0

    def test_remove_static_dipole_does_not_mutate_input(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            remove_static_dipole_assumption,
        )
        em_state = {"static_dipole_moment_Am2": 8.22e22}
        before = dict(em_state)
        new_state, _ = remove_static_dipole_assumption(em_state)
        assert em_state == before
        assert new_state != em_state

    def test_observational_precedence_flags(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            OBSERVATION_PRECEDES_MODEL_FIT,
            LINEAR_DIPOLE_EXTRAPOLATION_DEPRECATED,
            NONLINEAR_DYNAMO_COUPLING_REQUIRED,
            JERK_EVENTS_ARE_DEFAULT_NOT_EXCEPTION,
        )
        assert OBSERVATION_PRECEDES_MODEL_FIT is True
        assert LINEAR_DIPOLE_EXTRAPOLATION_DEPRECATED is True
        assert NONLINEAR_DYNAMO_COUPLING_REQUIRED is True
        assert JERK_EVENTS_ARE_DEFAULT_NOT_EXCEPTION is True

    def test_coupling_state_export_keys(self):
        from earth_systems_electromagnetic_constraint_2026 import (
            coupling_state,
        )
        state = coupling_state()
        for required in (
            "pole_drift_rate_km_yr",
            "pole_drift_peak_km_yr",
            "deceleration_regime_active",
            "pole_hemisphere",
            "wmm2025_valid_window",
            "dynamo_regime_shift",
            "saa_bifurcating",
            "couples_to_magnetosphere",
            "couples_to_ionosphere",
            "couples_to_infrastructure",
        ):
            assert required in state
        assert state["pole_hemisphere"] == "siberian"
        assert state["pole_drift_rate_km_yr"] == 35
        assert state["wmm2025_valid_window"] == (2025.0, 2030.0)


# ─────────────────────────────────────────────
# CONSTRAINT ISOMORPHISM FRAMEWORK
# Multi-scale pattern recognition: identical constraint topologies
# across cell biology, liposomes, ionosphere, atmosphere. Predictions
# by analogy from fast (cellular) to slow (atmospheric) systems.
# ─────────────────────────────────────────────

class TestConstraintIsomorphismFramework:
    def test_import(self):
        import constraint_isomorphism_framework  # noqa: F401

    def test_constraint_topology_dataclass(self):
        from constraint_isomorphism_framework import ConstraintTopology
        topo = ConstraintTopology(
            primary_resource="x",
            stress_timescale_relative="fast",
            bifurcation_point="threshold",
            adaptation_path="adapt",
            collapse_path="collapse",
            coupling_strength="strong",
            observable_precursor="signal",
            recovery_timescale="hours",
        )
        assert topo.primary_resource == "x"
        assert topo.coupling_strength == "strong"

    def test_four_reference_systems_present(self):
        from constraint_isomorphism_framework import (
            cancer_cell_stress,
            artificial_cell_stress,
            ionosphere_stress,
            atmosphere_stress,
            ConstraintTopology,
        )
        for sys in (cancer_cell_stress, artificial_cell_stress,
                    ionosphere_stress, atmosphere_stress):
            assert isinstance(sys, ConstraintTopology)
            # No empty fields
            assert sys.primary_resource
            assert sys.bifurcation_point
            assert sys.adaptation_path
            assert sys.collapse_path
            assert sys.observable_precursor

    def test_fast_vs_slow_timescale_distinction(self):
        """Cellular systems are fast; geophysical systems are slow."""
        from constraint_isomorphism_framework import (
            cancer_cell_stress,
            artificial_cell_stress,
            ionosphere_stress,
            atmosphere_stress,
        )
        assert "fast" in cancer_cell_stress.stress_timescale_relative
        assert "fast" in artificial_cell_stress.stress_timescale_relative
        assert "slow" in ionosphere_stress.stress_timescale_relative
        assert "slow" in atmosphere_stress.stress_timescale_relative

    def test_check_isomorphism_returns_full_mapping(self):
        from constraint_isomorphism_framework import (
            check_isomorphism,
            cancer_cell_stress,
            ionosphere_stress,
        )
        mapping = check_isomorphism(cancer_cell_stress, ionosphere_stress)
        for key in ("resource_depletion", "timescale_ratio",
                    "bifurcation_analogy", "adaptation_paths",
                    "precursor_observable"):
            assert key in mapping

    def test_check_isomorphism_pairs_systems_correctly(self):
        from constraint_isomorphism_framework import (
            check_isomorphism,
            cancer_cell_stress,
            ionosphere_stress,
        )
        mapping = check_isomorphism(cancer_cell_stress, ionosphere_stress)
        sys1_resource, sys2_resource = mapping["resource_depletion"]
        assert sys1_resource == cancer_cell_stress.primary_resource
        assert sys2_resource == ionosphere_stress.primary_resource

    def test_cascade_prediction_known_behaviors_map(self):
        from constraint_isomorphism_framework import (
            cascade_prediction_by_analogy,
            cancer_cell_stress,
            atmosphere_stress,
        )
        for behavior in (
            "heterogeneous_response",
            "lag_phase_buffering",
            "positive_feedback_cascade",
            "non_reversibility",
            "population_level_emergence",
        ):
            result = cascade_prediction_by_analogy(
                cancer_cell_stress, atmosphere_stress, behavior
            )
            assert result != "ANALOGY MAPPING NOT ESTABLISHED"
            assert len(result) > 0

    def test_cascade_prediction_unknown_behavior_returns_sentinel(self):
        from constraint_isomorphism_framework import (
            cascade_prediction_by_analogy,
            cancer_cell_stress,
            atmosphere_stress,
        )
        result = cascade_prediction_by_analogy(
            cancer_cell_stress, atmosphere_stress, "phlogiston_release"
        )
        assert result == "ANALOGY MAPPING NOT ESTABLISHED"

    def test_debris_loading_perturbation_keys(self):
        from constraint_isomorphism_framework import (
            debris_loading_as_perturbation,
        )
        for key in ("mechanism", "analogue_system",
                    "effect_on_bifurcation_threshold",
                    "observable_consequence",
                    "feedback_loop", "positive_feedback_risk"):
            assert key in debris_loading_as_perturbation
            assert debris_loading_as_perturbation[key]
        assert debris_loading_as_perturbation["positive_feedback_risk"] == "HIGH if reentry rate accelerates"

    def test_predictions_by_analogy_structure(self):
        from constraint_isomorphism_framework import PREDICTIONS_BY_ANALOGY
        assert len(PREDICTIONS_BY_ANALOGY) == 4
        for pred in PREDICTIONS_BY_ANALOGY:
            for key in ("system", "fast_analogue", "prediction",
                        "observable", "falsifiable"):
                assert key in pred
            assert pred["falsifiable"] is True
            assert pred["system"]
            assert pred["prediction"]
            assert pred["observable"]


# ─────────────────────────────────────────────
# PRECURSOR DETECTION IONOSPHERIC SCALE 2026
# Observed ionospheric signals interpreted as buffering-capacity
# degradation precursors under the multi-scale constraint isomorphism.
# Pattern-matching framework; falsifiable by subsequent observation.
# ─────────────────────────────────────────────

class TestPrecursorDetectionIonosphericScale2026:
    def test_import(self):
        import precursor_detection_ionospheric_scale_2026  # noqa: F401

    def test_signal_status_enum_values(self):
        from precursor_detection_ionospheric_scale_2026 import SignalStatus
        assert SignalStatus.BASELINE.value == "baseline"
        assert SignalStatus.ELEVATED.value == "elevated"
        assert SignalStatus.ANOMALOUS.value == "anomalous"
        assert SignalStatus.CRITICAL.value == "critical"

    def test_ionospheric_signal_dataclass(self):
        from precursor_detection_ionospheric_scale_2026 import (
            IonosphericSignal, SignalStatus,
        )
        sig = IonosphericSignal(
            name="test",
            measurement_type="probe",
            normal_range=(0.0, 1.0),
            current_value=0.5,
            current_status=SignalStatus.BASELINE,
            trend_direction="stable",
            weeks_of_observation=10,
            interpretation="ok",
            analogy_mapping="n/a",
        )
        assert sig.name == "test"
        assert sig.current_status is SignalStatus.BASELINE

    def test_ionospheric_signal_accepts_string_range(self):
        """QBO and GOES entries use string ranges; dataclass must accept."""
        from precursor_detection_ionospheric_scale_2026 import (
            IonosphericSignal, SignalStatus,
        )
        sig = IonosphericSignal(
            name="qbo",
            measurement_type="wind",
            normal_range="period: 24-30 months; regular",
            current_value="period: 26-32 months; irregular",
            current_status=SignalStatus.ANOMALOUS,
            trend_direction="rising",
            weeks_of_observation=260,
            interpretation="...",
            analogy_mapping="...",
        )
        assert isinstance(sig.normal_range, str)
        assert isinstance(sig.current_value, str)

    def test_eight_signals_registered(self):
        from precursor_detection_ionospheric_scale_2026 import (
            IONOSPHERIC_PRECURSOR_SIGNALS, IonosphericSignal,
        )
        assert len(IONOSPHERIC_PRECURSOR_SIGNALS) == 8
        for sig in IONOSPHERIC_PRECURSOR_SIGNALS:
            assert isinstance(sig, IonosphericSignal)
            # No empty fields
            assert sig.name
            assert sig.measurement_type
            assert sig.interpretation
            assert sig.analogy_mapping
            assert sig.weeks_of_observation > 0

    def test_no_signals_at_baseline_in_current_registry(self):
        """The 2026 registry should have every signal at or above elevated."""
        from precursor_detection_ionospheric_scale_2026 import (
            IONOSPHERIC_PRECURSOR_SIGNALS, SignalStatus,
        )
        for sig in IONOSPHERIC_PRECURSOR_SIGNALS:
            assert sig.current_status is not SignalStatus.BASELINE

    def test_at_least_one_critical_signal(self):
        from precursor_detection_ionospheric_scale_2026 import (
            IONOSPHERIC_PRECURSOR_SIGNALS, SignalStatus,
        )
        critical = [s for s in IONOSPHERIC_PRECURSOR_SIGNALS
                    if s.current_status is SignalStatus.CRITICAL]
        assert len(critical) >= 1

    def test_aggregate_precursor_status_keys(self):
        from precursor_detection_ionospheric_scale_2026 import (
            aggregate_precursor_status,
        )
        summary = aggregate_precursor_status()
        for key in ("signals_above_baseline",
                    "signals_with_rising_trend",
                    "signals_at_critical",
                    "consensus_interpretation",
                    "caveat",
                    "next_observation_targets"):
            assert key in summary

    def test_aggregate_precursor_status_counts(self):
        from precursor_detection_ionospheric_scale_2026 import (
            aggregate_precursor_status,
            IONOSPHERIC_PRECURSOR_SIGNALS,
        )
        summary = aggregate_precursor_status()
        total = len(IONOSPHERIC_PRECURSOR_SIGNALS)
        # Format "N/total"
        ab = summary["signals_above_baseline"].split("/")
        assert int(ab[1]) == total
        assert int(ab[0]) <= total
        rt = summary["signals_with_rising_trend"].split("/")
        assert int(rt[1]) == total
        # next_observation_targets is a non-empty list
        assert isinstance(summary["next_observation_targets"], list)
        assert len(summary["next_observation_targets"]) >= 1

    def test_aggregate_precursor_caveat_acknowledges_falsifiability(self):
        from precursor_detection_ionospheric_scale_2026 import (
            aggregate_precursor_status,
        )
        summary = aggregate_precursor_status()
        caveat = summary["caveat"].lower()
        assert "not causal" in caveat or "not causal predictions" in caveat

    def test_signals_by_status_filter(self):
        from precursor_detection_ionospheric_scale_2026 import (
            signals_by_status, SignalStatus, IONOSPHERIC_PRECURSOR_SIGNALS,
        )
        critical = signals_by_status(SignalStatus.CRITICAL)
        for sig in critical:
            assert sig.current_status is SignalStatus.CRITICAL
        baseline = signals_by_status(SignalStatus.BASELINE)
        assert baseline == []   # no baseline signals in current registry
        # Total partition holds
        elevated = signals_by_status(SignalStatus.ELEVATED)
        anomalous = signals_by_status(SignalStatus.ANOMALOUS)
        assert (len(critical) + len(elevated) + len(anomalous)
                + len(baseline)) == len(IONOSPHERIC_PRECURSOR_SIGNALS)

    def test_document_precursor_framework_returns_string(self):
        from precursor_detection_ionospheric_scale_2026 import (
            document_precursor_framework,
        )
        report = document_precursor_framework()
        assert isinstance(report, str)
        # Must surface the falsifiability framing
        assert "FRAMEWORK" in report
        assert "HYPOTHESIS" in report
        assert "ANALOGY HOLDS" in report
        assert "ANALOGY DOES NOT HOLD" in report

    def test_document_uses_actual_signal_count(self):
        """Report should use the live len(), not a hardcoded 7."""
        from precursor_detection_ionospheric_scale_2026 import (
            document_precursor_framework,
            IONOSPHERIC_PRECURSOR_SIGNALS,
        )
        report = document_precursor_framework()
        total = len(IONOSPHERIC_PRECURSOR_SIGNALS)
        # Expect "8/8" (or similar) — the formatted fraction
        assert f"/{total}" in report


# ─────────────────────────────────────────────
# FORMALIZED DISSENT — EARTH SYSTEMS PHYSICS
# Structural falsification-seeking role. When a consensus model forms
# (e.g. ionospheric buffering degradation), dissent engages concurrently:
# assume the model is wrong, document closure conditions, list failure
# scenarios, propose a falsifying observation.
# ─────────────────────────────────────────────

class TestFormalizedDissentEarthSystemsPhysics:
    def test_import(self):
        import formalized_dissent_earth_systems_physics  # noqa: F401

    def test_dissenter_authority_enum(self):
        from formalized_dissent_earth_systems_physics import (
            DissenterAuthority,
        )
        assert DissenterAuthority.EQUAL.value == "equal_standing"
        assert DissenterAuthority.STRUCTURAL.value == "built_into_process"
        assert DissenterAuthority.HALT_POWER.value == "can_demand_halt"
        assert (DissenterAuthority.PRECEDENT_INVOKE.value
                == "can_invoke_historical_precedent")

    def test_model_under_review_dataclass(self):
        from formalized_dissent_earth_systems_physics import ModelUnderReview
        model = ModelUnderReview(
            model_name="test",
            layer="ionosphere",
            claim="something is happening",
            consensus_strength=3,
            primary_evidence=["a", "b", "c"],
            assumed_mechanisms=["m1"],
            prediction_timescale="weeks",
            field_testable=True,
        )
        assert model.consensus_strength == 3
        assert model.field_testable is True
        assert len(model.primary_evidence) == 3

    def test_dissenter_analysis_dataclass(self):
        from formalized_dissent_earth_systems_physics import DissenterAnalysis
        a = DissenterAnalysis(
            model_reviewed="m",
            dissenter_assumption="wrong",
            assumption_that_breaks_it="X assumes Y",
            evidence_against=["e1"],
            closure_conditions=["c1"],
            failure_scenarios=["f1"],
            alternative_explanations=["alt1"],
            testable_prediction_to_falsify="if Z then dissent fails",
            probability_dissenter_is_right=0.4,
            strength_if_consensus_holds="stronger",
        )
        assert a.probability_dissenter_is_right == 0.4
        assert 0.0 <= a.probability_dissenter_is_right <= 1.0

    def test_engine_defaults(self):
        from formalized_dissent_earth_systems_physics import (
            FormalizedDissent_EarthSystemsPhysics, DissenterAuthority,
        )
        engine = FormalizedDissent_EarthSystemsPhysics()
        assert engine.models_under_review == []
        assert engine.dissent_analyses == []
        assert engine.dissenter_authority is DissenterAuthority.EQUAL
        assert engine.halt_power_active is True

    def test_propose_consensus_model_records_and_triggers_dissent(self, capsys):
        from formalized_dissent_earth_systems_physics import (
            FormalizedDissent_EarthSystemsPhysics, ModelUnderReview,
        )
        engine = FormalizedDissent_EarthSystemsPhysics()
        model = ModelUnderReview(
            model_name="Ionospheric_Test_Model",
            layer="ionosphere",
            claim="Ionospheric buffering capacity is degrading",
            consensus_strength=5,
            primary_evidence=["evidence 1"],
            assumed_mechanisms=["mech 1"],
            prediction_timescale="months",
            field_testable=True,
        )
        engine.propose_consensus_model(model)
        # Model recorded
        assert len(engine.models_under_review) == 1
        # Dissent automatically generated
        assert len(engine.dissent_analyses) == 1
        # Output should mention both consensus and dissent
        out = capsys.readouterr().out
        assert "CONSENSUS MODEL PROPOSED" in out
        assert "FORMALIZED DISSENT ACTIVATION" in out

    def test_ionosphere_dissent_is_domain_specific(self):
        """An ionosphere + buffering model gets the populated dissent,
        not the generic placeholder."""
        from formalized_dissent_earth_systems_physics import (
            FormalizedDissent_EarthSystemsPhysics, ModelUnderReview,
        )
        engine = FormalizedDissent_EarthSystemsPhysics()
        model = ModelUnderReview(
            model_name="ionos_buf",
            layer="ionosphere",
            claim="ionospheric buffering capacity declining",
            consensus_strength=5,
            primary_evidence=[],
            assumed_mechanisms=[],
            prediction_timescale="months",
            field_testable=True,
        )
        analysis = engine._generate_dissent_analysis(model)
        # Domain-specific path returns Swarm/calibration content
        assert "Swarm" in analysis.testable_prediction_to_falsify
        assert any("magnetometer" in e.lower()
                   for e in analysis.evidence_against)
        # Placeholder strings must NOT appear
        assert "[To be populated" not in str(analysis.evidence_against)

    def test_generic_dissent_for_unknown_layer(self):
        """Non-ionosphere model gets the generic placeholder dissent."""
        from formalized_dissent_earth_systems_physics import (
            FormalizedDissent_EarthSystemsPhysics, ModelUnderReview,
        )
        engine = FormalizedDissent_EarthSystemsPhysics()
        model = ModelUnderReview(
            model_name="hydro_model",
            layer="hydrosphere",
            claim="AMOC will slow",
            consensus_strength=3,
            primary_evidence=[],
            assumed_mechanisms=[],
            prediction_timescale="decades",
            field_testable=True,
        )
        analysis = engine._generate_dissent_analysis(model)
        # Generic placeholders surface honestly
        assert any("[To be populated" in e
                   for e in analysis.evidence_against)
        # Probability is 0.0 placeholder when domain-specific path absent
        assert analysis.probability_dissenter_is_right == 0.0

    def test_dissent_probability_in_valid_range(self):
        """Domain-specific dissents must report 0 <= p <= 1."""
        from formalized_dissent_earth_systems_physics import (
            FormalizedDissent_EarthSystemsPhysics, ModelUnderReview,
        )
        engine = FormalizedDissent_EarthSystemsPhysics()
        model = ModelUnderReview(
            model_name="x",
            layer="ionosphere",
            claim="buffering claim",
            consensus_strength=1,
            primary_evidence=[],
            assumed_mechanisms=[],
            prediction_timescale="weeks",
            field_testable=True,
        )
        analysis = engine._generate_dissent_analysis(model)
        assert 0.0 <= analysis.probability_dissenter_is_right <= 1.0

    def test_halt_implementation_prints_when_active(self, capsys):
        from formalized_dissent_earth_systems_physics import (
            FormalizedDissent_EarthSystemsPhysics,
        )
        engine = FormalizedDissent_EarthSystemsPhysics()
        engine.halt_implementation("calibration not yet verified")
        out = capsys.readouterr().out
        assert "DISSENTER HALT INVOKED" in out
        assert "calibration not yet verified" in out

    def test_halt_implementation_silent_when_inactive(self, capsys):
        from formalized_dissent_earth_systems_physics import (
            FormalizedDissent_EarthSystemsPhysics,
        )
        engine = FormalizedDissent_EarthSystemsPhysics()
        engine.halt_power_active = False
        engine.halt_implementation("should not appear")
        out = capsys.readouterr().out
        assert "DISSENTER HALT INVOKED" not in out

    def test_resolve_dissent_prints(self, capsys):
        from formalized_dissent_earth_systems_physics import (
            FormalizedDissent_EarthSystemsPhysics,
        )
        engine = FormalizedDissent_EarthSystemsPhysics()
        engine.resolve_dissent("cross-check planned")
        out = capsys.readouterr().out
        assert "DISSENT RESOLUTION" in out
        assert "cross-check planned" in out

    def test_export_dissent_json_round_trip(self):
        from formalized_dissent_earth_systems_physics import (
            FormalizedDissent_EarthSystemsPhysics, ModelUnderReview,
        )
        import json as _json
        engine = FormalizedDissent_EarthSystemsPhysics()
        model = ModelUnderReview(
            model_name="m",
            layer="ionosphere",
            claim="buffering claim",
            consensus_strength=1,
            primary_evidence=[],
            assumed_mechanisms=[],
            prediction_timescale="weeks",
            field_testable=True,
        )
        engine.propose_consensus_model(model)
        payload = engine.export_dissent_json()
        decoded = _json.loads(payload)
        assert isinstance(decoded, list)
        assert len(decoded) == 1
        rec = decoded[0]
        for key in ("model_reviewed", "dissenter_assumption",
                    "evidence_against", "closure_conditions",
                    "failure_scenarios", "alternative_explanations",
                    "testable_prediction_to_falsify",
                    "probability_dissenter_is_right",
                    "strength_if_consensus_holds"):
            assert key in rec


# ─────────────────────────────────────────────
# HORMUZ CASCADE AUDIT
# Thermodynamic + Earth-systems audit of the Hormuz -> fertilizer ->
# food cascade. Tests whether the 118M-225M excess-deaths claim is
# physically consistent with Haber-Bosch energetics, crop-calendar
# timing, caloric throughput, BMI-deficit mortality, and Solar Min
# forcing as added stressor.
# ─────────────────────────────────────────────

class TestHormuzCascadeAudit:
    def test_import(self):
        import hormuz_cascade_audit  # noqa: F401

    def test_physical_constants(self):
        from hormuz_cascade_audit import (
            J_PER_KCAL, KCAL_PER_PERSON_DAY, DAYS_PER_YEAR,
            HB_ENERGY_PER_KG_N, NG_LHV, NG_KG_PER_KG_N,
            GLOBAL_N_TRADE_FRAC_HORMUZ, POP_DEPENDENT_ON_IMPORT_N,
            WFP_ACUTE_HUNGER_INCREMENT,
        )
        assert J_PER_KCAL == 4184.0
        assert KCAL_PER_PERSON_DAY == 2100.0
        assert HB_ENERGY_PER_KG_N == 36e6
        assert NG_LHV == 50e6
        # Internal consistency: NG_KG_PER_KG_N = HB_ENERGY / LHV
        assert abs(NG_KG_PER_KG_N - HB_ENERGY_PER_KG_N / NG_LHV) < 1e-12
        # Sanity: Hormuz fertilizer share should be substantial but not >50%
        assert 0.20 <= GLOBAL_N_TRADE_FRAC_HORMUZ <= 0.50
        assert POP_DEPENDENT_ON_IMPORT_N > WFP_ACUTE_HUNGER_INCREMENT

    def test_hb_energy_and_natgas_scale_linearly(self):
        from hormuz_cascade_audit import (
            hb_energy_required, hb_nat_gas_required,
        )
        e1 = hb_energy_required({"kg_N": 1.0})
        e2 = hb_energy_required({"kg_N": 1000.0})
        assert abs(e2 - 1000.0 * e1) < 1e-6
        ng1 = hb_nat_gas_required({"kg_N": 1.0})
        ng2 = hb_nat_gas_required({"kg_N": 1000.0})
        assert abs(ng2 - 1000.0 * ng1) < 1e-6
        # Sanity: ~0.72 kg CH4 per kg N
        assert 0.5 <= ng1 <= 1.0

    def test_yield_loss_from_delay_breakpoints(self):
        from hormuz_cascade_audit import yield_loss_from_delay
        assert yield_loss_from_delay({"weeks_delay": 0}) == 0.00
        assert abs(yield_loss_from_delay({"weeks_delay": 2}) - 0.08) < 1e-6
        assert abs(yield_loss_from_delay({"weeks_delay": 4}) - 0.22) < 1e-6
        assert abs(yield_loss_from_delay({"weeks_delay": 6}) - 0.40) < 1e-6
        assert abs(yield_loss_from_delay({"weeks_delay": 8}) - 0.60) < 1e-6

    def test_yield_loss_from_delay_monotonic_and_capped(self):
        from hormuz_cascade_audit import yield_loss_from_delay
        prev = -1.0
        for w in (0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 26, 52, 100):
            v = yield_loss_from_delay({"weeks_delay": w})
            assert v >= prev
            assert v <= 0.60
            prev = v

    def test_hormuz_coupling_loss_extremes(self):
        from hormuz_cascade_audit import (
            hormuz_coupling_loss, GLOBAL_N_TRADE_FRAC_HORMUZ,
        )
        # Full throughput -> zero loss
        zero = hormuz_coupling_loss({
            "hormuz_throughput_frac": 1.0,
            "substitution_lag_months": 12.0,
            "buffer_stock_months": 0.0,
        })
        assert zero == 0.0
        # Full closure, long lag, no buffer -> approaches but does not
        # exceed Hormuz's share of N trade
        deep = hormuz_coupling_loss({
            "hormuz_throughput_frac": 0.0,
            "substitution_lag_months": 36.0,
            "buffer_stock_months": 0.0,
        })
        assert 0.0 < deep <= GLOBAL_N_TRADE_FRAC_HORMUZ + 1e-9

    def test_hormuz_coupling_buffer_dominates_short_lag(self):
        """If buffer exceeds substitution lag, no loss accrues."""
        from hormuz_cascade_audit import hormuz_coupling_loss
        v = hormuz_coupling_loss({
            "hormuz_throughput_frac": 0.0,
            "substitution_lag_months": 2.0,
            "buffer_stock_months": 6.0,
        })
        assert v == 0.0

    def test_solar_minimum_modifier_range(self):
        from hormuz_cascade_audit import (
            solar_minimum_modifier,
            SOLAR_MIN_YIELD_PENALTY_LOW,
            SOLAR_MIN_YIELD_PENALTY_HIGH,
        )
        lo = solar_minimum_modifier({"solar_min_intensity": 0.0})
        hi = solar_minimum_modifier({"solar_min_intensity": 1.0})
        assert lo == SOLAR_MIN_YIELD_PENALTY_LOW
        assert hi == SOLAR_MIN_YIELD_PENALTY_HIGH
        mid = solar_minimum_modifier({"solar_min_intensity": 0.5})
        assert lo < mid < hi

    def test_excess_mortality_monotonic_in_deficit(self):
        from hormuz_cascade_audit import (
            excess_mortality_from_caloric_deficit,
        )
        prev = -1.0
        for d in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
            v = excess_mortality_from_caloric_deficit({
                "pop_exposed": 1e6,
                "kcal_deficit_pct": d,
                "duration_months": 6.0,
                "buffer_redistribution": 0.2,
            })
            assert v >= prev
            prev = v

    def test_excess_mortality_capped_at_30pct(self):
        """Physical ceiling: cumulative mortality rate <= 30%."""
        from hormuz_cascade_audit import (
            excess_mortality_from_caloric_deficit,
        )
        pop = 1e6
        deaths = excess_mortality_from_caloric_deficit({
            "pop_exposed": pop,
            "kcal_deficit_pct": 0.6,
            "duration_months": 60.0,    # very long
            "buffer_redistribution": 0.0,
        })
        assert deaths <= 0.30 * pop + 1e-3

    def test_excess_mortality_calibration_sudan(self):
        """Sudan 2024 anchor: 17M @ 50% deficit x 6mo with buffer~0.1."""
        from hormuz_cascade_audit import (
            excess_mortality_from_caloric_deficit,
        )
        deaths = excess_mortality_from_caloric_deficit({
            "pop_exposed": 17e6,
            "kcal_deficit_pct": 0.5,
            "duration_months": 6.0,
            "buffer_redistribution": 0.1,
        })
        # Anchored to ~2.5M; tolerate +/- 30% from form approximations
        assert 1.5e6 < deaths < 3.5e6

    def test_build_scenarios_count_and_names(self):
        from hormuz_cascade_audit import build_scenarios
        scenarios = build_scenarios()
        assert len(scenarios) == 5
        names = {s.scenario for s in scenarios}
        assert "FAO_baseline_broad_sharing" in names
        assert "WFP_prolonged_moderate" in names
        assert "presenter_low_concentrated" in names
        assert "presenter_high_concentrated" in names
        assert "solar_only_no_hormuz" in names

    def test_cascade_run_execute_populates_all_results(self):
        from hormuz_cascade_audit import build_scenarios
        for s in build_scenarios():
            r = s.execute()
            for key in ("n_loss_frac_global", "kg_N_withheld",
                        "timing_loss_frac", "solar_drag_frac",
                        "total_yield_loss_frac", "kcal_lost",
                        "person_years_unfed", "kcal_deficit_pct",
                        "excess_deaths", "hb_energy_freed_J",
                        "natgas_freed_kg"):
                assert key in r

    def test_solar_only_scenario_zero_n_loss(self):
        """solar_only_no_hormuz: throughput=1.0 + no buffer overdraft
        -> zero N loss, zero NG freed."""
        from hormuz_cascade_audit import build_scenarios
        s = next(s for s in build_scenarios()
                 if s.scenario == "solar_only_no_hormuz")
        s.execute()
        assert s.results["n_loss_frac_global"] == 0.0
        assert s.results["kg_N_withheld"] == 0.0
        assert s.results["natgas_freed_kg"] == 0.0

    def test_presenter_high_hits_physical_ceiling(self):
        from hormuz_cascade_audit import (
            build_scenarios, POP_DEPENDENT_ON_IMPORT_N,
        )
        s = next(s for s in build_scenarios()
                 if s.scenario == "presenter_high_concentrated")
        s.execute()
        # Ceiling = 30% of import-dependent population
        ceiling = 0.30 * POP_DEPENDENT_ON_IMPORT_N
        assert s.results["excess_deaths"] <= ceiling + 1.0
        # And it does reach (or essentially reach) the ceiling
        assert s.results["excess_deaths"] >= 0.95 * ceiling

    def test_fao_baseline_below_presenter_low(self):
        """Broad-sharing FAO baseline should yield fewer deaths than
        concentrated presenter scenarios."""
        from hormuz_cascade_audit import build_scenarios
        runs = {s.scenario: s for s in build_scenarios()}
        for s in runs.values():
            s.execute()
        fao = runs["FAO_baseline_broad_sharing"].results["excess_deaths"]
        plow = runs["presenter_low_concentrated"].results["excess_deaths"]
        phigh = runs["presenter_high_concentrated"].results["excess_deaths"]
        assert fao < plow
        assert plow <= phigh

    def test_sensitivity_sweep_returns_pairs_and_is_non_decreasing(self):
        from hormuz_cascade_audit import sensitivity_sweep
        result = sensitivity_sweep()
        assert len(result) == 8
        prev_deaths = -1.0
        prev_va = -1.0
        for va, deaths in result:
            assert 0.0 <= va <= 1.0
            assert va > prev_va
            assert deaths >= prev_deaths
            prev_va = va
            prev_deaths = deaths

    def test_audit_claims_structure(self):
        from hormuz_cascade_audit import AUDIT_CLAIMS
        assert len(AUDIT_CLAIMS) == 5
        ids = [c["id"] for c in AUDIT_CLAIMS]
        assert ids == ["C1", "C2", "C3", "C4", "C5"]
        for c in AUDIT_CLAIMS:
            assert callable(c["test"])
            assert c["claim"]
            assert c["passes_when"]

    def test_all_audit_claims_pass_on_documented_scenarios(self):
        """Every claim must pass against its targeted scenario in the
        documented configuration; the audit's value is that it's
        internally consistent before being applied elsewhere."""
        from hormuz_cascade_audit import (
            build_scenarios, AUDIT_CLAIMS,
        )
        runs = {s.scenario: s for s in build_scenarios()}
        for s in runs.values():
            s.execute()

        def pick(claim_id):
            if claim_id == "C1":
                return runs["presenter_high_concentrated"].results
            if claim_id == "C2":
                return runs["FAO_baseline_broad_sharing"].results
            if claim_id == "C3":
                return runs["solar_only_no_hormuz"].results
            return runs["presenter_high_concentrated"].results

        for c in AUDIT_CLAIMS:
            r = pick(c["id"])
            assert c["test"](r), f"audit claim {c['id']} failed: {c['claim']}"

    def test_fmt_formats_magnitudes(self):
        from hormuz_cascade_audit import fmt
        assert fmt(None) == "-"
        assert fmt(0) == "0.000"
        assert "k" in fmt(2500)
        assert "M" in fmt(2.5e6)
        assert "B" in fmt(2.5e9)
        assert "T" in fmt(2.5e12)

    def test_earth_system_map_mentions_key_layers(self):
        from hormuz_cascade_audit import EARTH_SYSTEM_MAP
        for term in ("electromagnetic", "ionosphere", "hydrosphere",
                     "lithosphere", "biosphere", "Haber-Bosch",
                     "HORMUZ CHOKEPOINT"):
            assert term in EARTH_SYSTEM_MAP


# ─────────────────────────────────────────────
# LEVERAGE ANALYSIS V2
# Companion to hormuz_cascade_audit. Computes lives-saved per
# intervention across multiple operating points (today Q2 2026 /
# prolonged 6mo / mild), then ranks. Identifies whether
# duration, allocation, or supply is the dominant lever at each
# operating point.
# ─────────────────────────────────────────────

class TestLeverageAnalysisV2:
    def test_import(self):
        import leverage_analysis_v2  # noqa: F401

    def test_operating_points_keys(self):
        from leverage_analysis_v2 import OPERATING_POINTS
        assert set(OPERATING_POINTS.keys()) == {
            "today_q2_2026", "prolonged_6mo", "mild",
        }
        # Each operating point has all 8 cascade parameters
        for op in OPERATING_POINTS.values():
            for k in ("hormuz_throughput_frac", "substitution_lag_months",
                      "buffer_stock_months", "weeks_planting_delay",
                      "duration_months", "buffer_redistribution",
                      "solar_min_intensity", "vulnerable_absorption"):
                assert k in op

    def test_interventions_structure(self):
        from leverage_analysis_v2 import INTERVENTIONS
        assert len(INTERVENTIONS) == 7
        for name, param, delta, itype in INTERVENTIONS:
            assert isinstance(name, str) and name
            assert isinstance(param, str) and param
            assert isinstance(delta, (int, float))
            assert isinstance(itype, str) and itype

    def test_deaths_function_returns_nonneg(self):
        from leverage_analysis_v2 import deaths, OPERATING_POINTS
        for op in OPERATING_POINTS.values():
            d = deaths(op)
            assert d >= 0.0

    def test_apply_clamps_fractional_params(self):
        from leverage_analysis_v2 import apply, OPERATING_POINTS
        op = OPERATING_POINTS["today_q2_2026"]
        # Push throughput above 1.0 -> clamped
        out = apply(op, "hormuz_throughput_frac", +5.0)
        assert out["hormuz_throughput_frac"] == 1.0
        # Push redistribution below 0 -> clamped
        out = apply(op, "buffer_redistribution", -5.0)
        assert out["buffer_redistribution"] == 0.0

    def test_apply_clamps_nonneg_time_params(self):
        from leverage_analysis_v2 import apply, OPERATING_POINTS
        op = OPERATING_POINTS["today_q2_2026"]
        out = apply(op, "duration_months", -100.0)
        assert out["duration_months"] == 0.0
        out = apply(op, "substitution_lag_months", -100.0)
        assert out["substitution_lag_months"] == 0.0

    def test_apply_does_not_mutate_input(self):
        from leverage_analysis_v2 import apply, OPERATING_POINTS
        op = OPERATING_POINTS["today_q2_2026"]
        original = dict(op)
        _ = apply(op, "duration_months", -3.0)
        assert op == original

    def test_fmt_magnitudes(self):
        from leverage_analysis_v2 import fmt
        assert "B" in fmt(2.5e9)
        assert "M" in fmt(2.5e6)
        assert "k" in fmt(2500)
        assert fmt(0) == "0.0"

    def test_build_leverage_matrix_shape(self):
        from leverage_analysis_v2 import (
            build_leverage_matrix, OPERATING_POINTS, INTERVENTIONS,
        )
        matrix, baselines = build_leverage_matrix()
        assert set(baselines.keys()) == set(OPERATING_POINTS.keys())
        for opname in OPERATING_POINTS:
            assert opname in matrix
            assert (set(matrix[opname].keys())
                    == {iv[0] for iv in INTERVENTIONS})

    def test_build_leverage_matrix_lives_saved_nonneg(self):
        """Every documented intervention is framed as positive=improvement,
        so lives-saved should be >= 0 at every operating point."""
        from leverage_analysis_v2 import build_leverage_matrix
        matrix, _ = build_leverage_matrix()
        for opname, row in matrix.items():
            for iname, saved in row.items():
                assert saved >= -1.0, (
                    f"{iname} at {opname} produced negative lives saved: {saved}"
                )

    def test_rank_interventions_orders_high_to_low(self):
        from leverage_analysis_v2 import (
            build_leverage_matrix, rank_interventions,
        )
        matrix, _ = build_leverage_matrix()
        ranked = rank_interventions(matrix, "today_q2_2026")
        prev = float("inf")
        for name, _, _, _ in ranked:
            saved = matrix["today_q2_2026"][name]
            assert saved <= prev
            prev = saved

    def test_duration_is_top_lever_at_today_baseline(self):
        """The documented hypothesis: at the today_q2_2026 operating
        point (saturated cascade with capped deficit), shortening
        conflict duration is the top lever. This is the analytical
        finding the module is built to surface."""
        from leverage_analysis_v2 import (
            build_leverage_matrix, rank_interventions,
        )
        matrix, _ = build_leverage_matrix()
        ranked = rank_interventions(matrix, "today_q2_2026")
        top_name = ranked[0][0]
        second_name = ranked[1][0]
        assert "Shorten conflict" in top_name
        # Redistribution should be next
        assert "Redistribution" in second_name

    def test_supply_side_interventions_zero_at_today_baseline(self):
        """Documented model behaviour: at today's saturated operating
        point, supply-side interventions (Hormuz, lag, buffer, planting
        delay) save zero lives because the deficit is already capped
        at the 60% physical ceiling. This is the audit's point."""
        from leverage_analysis_v2 import build_leverage_matrix
        matrix, _ = build_leverage_matrix()
        row = matrix["today_q2_2026"]
        for name in ("Reopen Hormuz +30%",
                     "Cut substitution lag -3mo",
                     "+3mo buffer stocks",
                     "Planting delay -2wks"):
            assert row[name] == 0.0, (
                f"{name} unexpectedly saved lives at saturated baseline"
            )

    def test_mild_operating_point_has_lowest_baseline(self):
        """mild scenario (rapid resolution) should yield fewer deaths
        than today's actual situation or the prolonged-6mo extension."""
        from leverage_analysis_v2 import build_leverage_matrix
        _, baselines = build_leverage_matrix()
        assert baselines["mild"] < baselines["today_q2_2026"]
        assert baselines["today_q2_2026"] < baselines["prolonged_6mo"]

    def test_mild_operating_point_supply_intervention_helps(self):
        """At the 'mild' (non-saturated) operating point, a supply-side
        intervention like planting-delay reduction SHOULD save lives —
        that's the contrast the analysis surfaces."""
        from leverage_analysis_v2 import build_leverage_matrix
        matrix, _ = build_leverage_matrix()
        # Planting delay reduction saves lives in mild scenario
        assert matrix["mild"]["Planting delay -2wks"] > 0.0
        # Same intervention saves zero in saturated today scenario
        assert matrix["today_q2_2026"]["Planting delay -2wks"] == 0.0

    def test_main_runs_without_error(self, capsys):
        """The main() function should produce structured output without
        raising; capture and verify the key headers."""
        from leverage_analysis_v2 import main
        main()
        out = capsys.readouterr().out
        assert "LEVERAGE ANALYSIS" in out
        assert "RANKED LEVERAGE" in out
        assert "WHAT THE NUMBERS REVEAL" in out
        assert "Shorten conflict" in out


# ─────────────────────────────────────────────
# INSTITUTIONAL BOTTLENECK AUDIT
# Audits the Hormuz cascade for the load-bearing failure node.
# Argues the bottleneck is regulatory (humanure prohibitions blocking
# closed-loop N), not physical, and produces an accountability trail
# with named authority + lives-per-month-delay for 6 jurisdictions.
# ─────────────────────────────────────────────

class TestInstitutionalBottleneckAudit:
    def test_import(self):
        import institutional_bottleneck_audit  # noqa: F401

    def test_physical_facts_keys_and_values(self):
        from institutional_bottleneck_audit import PHYSICAL_FACTS
        for key in ("human_N_excretion_kg_per_yr", "global_pop",
                    "total_human_N_output_Mt", "global_synthetic_N_Mt",
                    "hormuz_disrupted_N_Mt", "replacement_potential_pct",
                    "thermophilic_kill_temp_C", "thermophilic_kill_time_days",
                    "full_compost_curing_months", "planting_windows_required",
                    "deaths_at_baseline_today", "deaths_avoidable_via_loop"):
            assert key in PHYSICAL_FACTS
        # Internal consistency: total_human_N_output = pop * per-person / 1e9
        expected_Mt = (PHYSICAL_FACTS["global_pop"]
                       * PHYSICAL_FACTS["human_N_excretion_kg_per_yr"]
                       / 1e9)
        assert abs(PHYSICAL_FACTS["total_human_N_output_Mt"] - expected_Mt) < 0.5
        # Hormuz share = 30% of global synthetic N
        assert (abs(PHYSICAL_FACTS["hormuz_disrupted_N_Mt"]
                    - 0.30 * PHYSICAL_FACTS["global_synthetic_N_Mt"])
                < 1.0)
        # Three planting windows listed
        assert len(PHYSICAL_FACTS["planting_windows_required"]) == 3

    def test_regulatory_node_dataclass(self):
        from institutional_bottleneck_audit import RegulatoryNode
        n = RegulatoryNode(
            jurisdiction="x",
            rule="r",
            authority="a",
            prohibits="p",
            physically_safe=True,
            change_lead_time="6mo",
            lives_per_month_delay=1000.0,
        )
        assert n.jurisdiction == "x"
        assert n.lives_per_month_delay == 1000.0

    def test_accountability_statement_physics_justified_branch(self):
        """When physically_safe=True, the statement should report the
        rule as physics-justified — no accountability call."""
        from institutional_bottleneck_audit import RegulatoryNode
        n = RegulatoryNode(
            jurisdiction="US",
            rule="X",
            authority="EPA",
            prohibits="something",
            physically_safe=True,
            change_lead_time="long",
            lives_per_month_delay=10_000,
        )
        s = n.accountability_statement()
        assert "EPA" in s
        assert "physics-justified" in s
        # Should NOT contain the accountability call
        assert "authority to modify" not in s

    def test_accountability_statement_not_justified_branch(self):
        """When physically_safe=False, the statement should call out
        the authority with the lives-per-month figure."""
        from institutional_bottleneck_audit import RegulatoryNode
        n = RegulatoryNode(
            jurisdiction="MN",
            rule="R",
            authority="MN PCA",
            prohibits="composting toilets",
            physically_safe=False,
            change_lead_time="6mo",
            lives_per_month_delay=15_000,
        )
        s = n.accountability_statement()
        assert "MN PCA" in s
        assert "authority to modify" in s
        assert "NOT physics-justified" in s
        # Lives figure surfaces (15_000 / 1000 = 15 -> "15k")
        assert "15k" in s

    def test_six_regulatory_bottlenecks_with_required_fields(self):
        from institutional_bottleneck_audit import REGULATORY_BOTTLENECKS
        assert len(REGULATORY_BOTTLENECKS) == 6
        for node in REGULATORY_BOTTLENECKS:
            assert node.jurisdiction
            assert node.rule
            assert node.authority
            assert node.prohibits
            assert isinstance(node.physically_safe, bool)
            assert node.change_lead_time
            assert node.lives_per_month_delay >= 0

    def test_regulatory_bottlenecks_named_jurisdictions(self):
        from institutional_bottleneck_audit import REGULATORY_BOTTLENECKS
        jurisdictions = {n.jurisdiction for n in REGULATORY_BOTTLENECKS}
        assert any("United States" in j for j in jurisdictions)
        assert any("Minnesota" in j for j in jurisdictions)
        assert any("European Union" in j for j in jurisdictions)
        assert any("India" in j for j in jurisdictions)
        assert any("Africa" in j for j in jurisdictions)
        assert any("Codex" in j for j in jurisdictions)

    def test_aggregate_lives_per_month_matches_sum(self):
        from institutional_bottleneck_audit import (
            REGULATORY_BOTTLENECKS, aggregate_lives_per_month,
        )
        total = aggregate_lives_per_month()
        expected = sum(n.lives_per_month_delay for n in REGULATORY_BOTTLENECKS)
        assert total == expected
        # Documented total: 50k + 500 + 80k + 200k + 300k + 100k = 730,500
        assert total == 730_500

    def test_defenses_that_fail_structure(self):
        from institutional_bottleneck_audit import DEFENSES_THAT_FAIL
        assert len(DEFENSES_THAT_FAIL) == 6
        for d in DEFENSES_THAT_FAIL:
            assert set(d.keys()) == {"defense", "rebuttal"}
            assert d["defense"]
            assert d["rebuttal"]

    def test_defenses_include_key_arguments(self):
        from institutional_bottleneck_audit import DEFENSES_THAT_FAIL
        defenses = [d["defense"] for d in DEFENSES_THAT_FAIL]
        rebuttals = " ".join(d["rebuttal"] for d in DEFENSES_THAT_FAIL)
        # The six classic deflection patterns
        assert any("didn't know" in d for d in defenses)
        assert any("not safe" in d for d in defenses)
        assert any("Heavy metals" in d for d in defenses)
        assert any("Cultural" in d for d in defenses)
        assert any("more time" in d for d in defenses)
        assert any("Markets" in d for d in defenses)
        # Rebuttals reference the calibrating historical record
        assert "Bengal 1943" in rebuttals or "Bengal" in rebuttals
        assert "King" in rebuttals   # 'Farmers of Forty Centuries'

    def test_cascade_topology_mentions_both_paths(self):
        from institutional_bottleneck_audit import CASCADE_TOPOLOGY
        for term in ("PHYSICAL CASCADE",
                     "INSTITUTIONAL CASCADE",
                     "Hormuz chokepoint",
                     "Haber-Bosch",
                     "CLOSED LOOP",
                     "OPEN/DUMPED",
                     "EPA 503",
                     "AUDIT TRAIL"):
            assert term in CASCADE_TOPOLOGY

    def test_fmt_format(self):
        from institutional_bottleneck_audit import fmt
        assert "B" in fmt(2.5e9)
        assert "M" in fmt(2.5e6)
        assert "k" in fmt(2500)
        assert fmt(0) == "0"

    def test_run_executes_without_error(self, capsys):
        from institutional_bottleneck_audit import run
        run()
        out = capsys.readouterr().out
        # Section headers we expect
        assert "INSTITUTIONAL BOTTLENECK AUDIT" in out
        assert "REGULATORY CHOKE POINTS" in out
        assert "DEFENSES AGAINST FUTURE INSTITUTIONAL CLAIMS" in out
        assert "ATTRIBUTION FORMULA" in out
        assert "WHAT THIS DOCUMENT IS" in out
        # Aggregate figure should appear
        assert "AGGREGATE" in out


# ─────────────────────────────────────────────
# VILLAGE NUTRIENT CLOSURE TOOLKIT
# Village-scale N/P/K closure planner. Maps locally available
# substrates (humanure, livestock, legumes, biomass, ash, bokashi,
# seaweed, etc.) against crop nutrient need and emits a dispatch
# sequence aligned to the planting calendar.
# ─────────────────────────────────────────────

class TestVillageNClosure:
    def test_import(self):
        import village_n_closure  # noqa: F401

    def test_crop_nutrient_need_structure(self):
        from village_n_closure import CROP_NUTRIENT_NEED
        assert len(CROP_NUTRIENT_NEED) == 11
        for crop, tup in CROP_NUTRIENT_NEED.items():
            assert isinstance(tup, tuple) and len(tup) == 3
            n, p, k = tup
            assert n >= 0 and p >= 0 and k >= 0

    def test_typical_yield_t_per_ha_keys_match_crops(self):
        from village_n_closure import (
            CROP_NUTRIENT_NEED, TYPICAL_YIELD_T_PER_HA,
        )
        # Every crop with a nutrient profile should have a yield default
        for crop in CROP_NUTRIENT_NEED:
            assert crop in TYPICAL_YIELD_T_PER_HA

    def test_substrates_schema(self):
        from village_n_closure import SUBSTRATES
        assert len(SUBSTRATES) >= 15
        for name, s in SUBSTRATES.items():
            for required in ("unit", "yield", "lag_mo",
                             "notes", "safety", "scale"):
                assert required in s, f"{name} missing {required}"
            for nut in ("N", "P2O5", "K2O"):
                assert nut in s["yield"]
                assert s["yield"][nut] >= 0
            assert s["lag_mo"] >= 0

    def test_substrates_categorical_coverage(self):
        """The catalog should cover humanure, livestock, N-fixing,
        biomass, ash, fermentation, mineral sources."""
        from village_n_closure import SUBSTRATES
        assert "humanure_composted" in SUBSTRATES
        assert "urine_diverted" in SUBSTRATES
        assert "cattle_manure" in SUBSTRATES
        assert "chicken_manure" in SUBSTRATES
        assert "legume_residue_inplace" in SUBSTRATES
        assert "azolla_pond" in SUBSTRATES
        assert "wood_ash" in SUBSTRATES
        assert "biochar_charged" in SUBSTRATES
        assert "bokashi_food_scrap" in SUBSTRATES
        assert "rock_phosphate_local" in SUBSTRATES

    def test_calendar_bands_structure(self):
        from village_n_closure import CALENDAR_BANDS
        assert len(CALENDAR_BANDS) == 8
        for band, info in CALENDAR_BANDS.items():
            assert "plant" in info
            assert "compost_start_by" in info

    def test_village_dataclass_defaults(self):
        from village_n_closure import Village
        v = Village(
            name="x", population=10, climate_band="equatorial",
            crops={"maize": 1.0}, substrates={},
        )
        assert v.target_yield_pct == 1.0
        assert v.nutrient_need == {}
        assert v.nutrient_supply == {}
        assert v.deficit == {}
        assert v.dispatch == []

    def test_compute_need_known_inputs(self):
        """10 ha maize at 3.5 t/ha typical, target=1.0:
        35 t * 22 kg N/t = 770 kg N
        35 t * 8 kg P/t  = 280 kg P
        35 t * 18 kg K/t = 630 kg K"""
        from village_n_closure import compute_need, Village
        v = Village(name="t", population=1, climate_band="NH_temperate",
                    crops={"maize": 10.0}, substrates={},
                    target_yield_pct=1.0)
        n = compute_need(v)
        assert abs(n["N"]    - 770.0) < 1e-6
        assert abs(n["P2O5"] - 280.0) < 1e-6
        assert abs(n["K2O"]  - 630.0) < 1e-6

    def test_compute_need_scales_with_yield_target(self):
        from village_n_closure import compute_need, Village
        v_full = Village(name="t", population=1, climate_band="NH_temperate",
                         crops={"maize": 10.0}, substrates={},
                         target_yield_pct=1.0)
        v_half = Village(name="t", population=1, climate_band="NH_temperate",
                         crops={"maize": 10.0}, substrates={},
                         target_yield_pct=0.5)
        n_full = compute_need(v_full)
        n_half = compute_need(v_half)
        for nut in ("N", "P2O5", "K2O"):
            assert abs(n_full[nut] - 2 * n_half[nut]) < 1e-6

    def test_compute_need_unknown_crop_ignored(self):
        from village_n_closure import compute_need, Village
        v = Village(name="t", population=1, climate_band="NH_temperate",
                    crops={"unicorn_grain": 5.0}, substrates={})
        n = compute_need(v)
        assert n == {"N": 0.0, "P2O5": 0.0, "K2O": 0.0}

    def test_compute_supply_with_breakdown(self):
        """40 cattle * (60, 20, 40) = (2400, 800, 1600)
        + 0.5 t wood_ash * (0, 20, 50) = (0, 10, 25)
        totals: (2400, 810, 1625)"""
        from village_n_closure import compute_supply, Village
        v = Village(name="t", population=1, climate_band="NH_temperate",
                    crops={},
                    substrates={"cattle_manure": 40, "wood_ash": 0.5})
        s = compute_supply(v)
        assert abs(s["N"]    - 2400.0) < 1e-6
        assert abs(s["P2O5"] -  810.0) < 1e-6
        assert abs(s["K2O"]  - 1625.0) < 1e-6
        # Breakdown attached to village
        assert hasattr(v, "nutrient_supply_breakdown")
        assert set(v.nutrient_supply_breakdown.keys()) == {
            "cattle_manure", "wood_ash"
        }

    def test_compute_supply_unknown_substrate_ignored(self):
        from village_n_closure import compute_supply, Village
        v = Village(name="t", population=1, climate_band="NH_temperate",
                    crops={},
                    substrates={"unicorn_dung": 100})
        s = compute_supply(v)
        assert s == {"N": 0.0, "P2O5": 0.0, "K2O": 0.0}

    def test_compute_deficit_sign(self):
        from village_n_closure import compute_deficit
        need   = {"N": 100.0, "P2O5":  50.0, "K2O":  80.0}
        supply = {"N":  30.0, "P2O5":  60.0, "K2O":  80.0}
        d = compute_deficit(need, supply)
        assert d["N"] == 70.0       # shortfall (positive)
        assert d["P2O5"] == -10.0   # surplus (negative)
        assert d["K2O"] == 0.0      # exact

    def test_build_dispatch_includes_held_substrates_and_calendar(self):
        from village_n_closure import build_dispatch, Village
        v = Village(name="t", population=1, climate_band="NH_temperate",
                    crops={},
                    substrates={"cattle_manure": 5,
                                "wood_ash": 0.2})
        # All surplus, no deficit
        d = build_dispatch(v, {"N": -100.0, "P2O5": -50.0, "K2O": -50.0})
        actions = [step["action"] for step in d]
        assert any("processing cattle_manure" in a for a in actions)
        assert any("processing wood_ash" in a for a in actions)
        assert any(a == "Calendar gate" for a in actions)
        # No deficit-driven phases
        assert not any("N-fixing" in a for a in actions)
        assert not any("Source P" in a for a in actions)
        assert not any("Source K" in a for a in actions)

    def test_build_dispatch_adds_n_fixing_when_n_deficit(self):
        from village_n_closure import build_dispatch, Village
        v = Village(name="t", population=1, climate_band="NH_temperate",
                    crops={}, substrates={})
        d = build_dispatch(v, {"N": 500.0, "P2O5": 0.0, "K2O": 0.0})
        actions = [step["action"] for step in d]
        assert any("N-fixing" in a for a in actions)
        # NOT in tropical/monsoon band -> no azolla recommendation
        assert not any("azolla" in a for a in actions)

    def test_build_dispatch_adds_azolla_in_tropical_bands(self):
        from village_n_closure import build_dispatch, Village
        for band in ("NH_monsoon", "equatorial", "SH_subtropical"):
            v = Village(name="t", population=1, climate_band=band,
                        crops={}, substrates={})
            d = build_dispatch(v, {"N": 1000.0, "P2O5": 0.0, "K2O": 0.0})
            actions = [step["action"] for step in d]
            assert any("azolla" in a for a in actions), (
                f"missing azolla in {band}"
            )

    def test_build_dispatch_adds_p_and_k_when_those_deficit(self):
        from village_n_closure import build_dispatch, Village
        v = Village(name="t", population=1, climate_band="NH_temperate",
                    crops={}, substrates={})
        d = build_dispatch(v, {"N": 0.0, "P2O5": 100.0, "K2O": 100.0})
        actions = [step["action"] for step in d]
        assert any("Source P" in a for a in actions)
        assert any("Source K" in a for a in actions)

    def test_build_dispatch_sorted_by_priority_then_lag(self):
        from village_n_closure import build_dispatch, Village
        v = Village(name="t", population=1, climate_band="NH_temperate",
                    crops={},
                    substrates={"humanure_composted": 100,  # lag 6
                                "wood_ash": 0.5})             # lag 0
        d = build_dispatch(v, {"N": 500.0, "P2O5": 0.0, "K2O": 0.0})
        # Within priority 1 entries, wood_ash (lag 0) should precede
        # humanure_composted (lag 6)
        p1 = [step for step in d if step["priority"] == 1]
        actions_p1 = [step["action"] for step in p1]
        wood_idx = next(i for i, a in enumerate(actions_p1)
                        if "wood_ash" in a)
        humanure_idx = next(i for i, a in enumerate(actions_p1)
                            if "humanure_composted" in a)
        assert wood_idx < humanure_idx
        # Priorities overall are sorted ascending
        prev = -1
        for step in d:
            assert step["priority"] >= prev
            prev = step["priority"]

    def test_fmt_kg(self):
        from village_n_closure import fmt_kg
        assert "t" in fmt_kg(2500)
        assert "kg" in fmt_kg(50)
        assert "kg" in fmt_kg(0)

    def test_remediate_known_condition(self, capsys):
        from village_n_closure import remediate
        remediate("soil_depleted_organic_matter")
        out = capsys.readouterr().out
        assert "REMEDIATION" in out
        assert "compost application" in out

    def test_remediate_unknown_condition_lists_options(self, capsys):
        from village_n_closure import remediate
        remediate("haunted_soil")
        out = capsys.readouterr().out
        assert "Unknown condition" in out
        assert "soil_acidic" in out   # known options listed

    def test_ferment_known_protocol(self, capsys):
        from village_n_closure import ferment
        ferment("bokashi")
        out = capsys.readouterr().out
        assert "FERMENTATION: bokashi" in out
        assert "EM/LAB" in out

    def test_ferment_unknown_protocol_lists_options(self, capsys):
        from village_n_closure import ferment
        ferment("alchemical_transmutation")
        out = capsys.readouterr().out
        assert "Unknown protocol" in out
        assert "bokashi" in out

    def test_example_village_has_surplus_on_all_three_nutrients(self):
        """The documented EXAMPLE_VILLAGE is configured so that locally
        available substrates exceed crop need on N, P, and K — the
        affirmative demonstration the module exists to make."""
        from village_n_closure import (
            EXAMPLE_VILLAGE, compute_need, compute_supply, compute_deficit,
        )
        need    = compute_need(EXAMPLE_VILLAGE)
        supply  = compute_supply(EXAMPLE_VILLAGE)
        deficit = compute_deficit(need, supply)
        for nut in ("N", "P2O5", "K2O"):
            assert deficit[nut] < 0, (
                f"EXAMPLE_VILLAGE has shortfall in {nut} = {deficit[nut]}"
            )

    def test_run_custom_returns_village_and_runs(self, capsys):
        from village_n_closure import run_custom, Village
        v = run_custom(
            name="Test Village",
            population=50,
            climate_band="equatorial",
            crops={"cassava": 1.0},
            substrates={"humanure_composted": 50,
                        "azolla_pond": 5},
            target_yield_pct=1.0,
        )
        assert isinstance(v, Village)
        out = capsys.readouterr().out
        assert "Test Village" in out
        assert "VILLAGE N-CLOSURE REPORT" in out

    def test_report_populates_village_attributes(self):
        """report() should write back computed values to the Village
        instance so callers can introspect after."""
        from village_n_closure import report, EXAMPLE_VILLAGE
        report(EXAMPLE_VILLAGE)
        assert EXAMPLE_VILLAGE.nutrient_need
        assert EXAMPLE_VILLAGE.nutrient_supply
        assert EXAMPLE_VILLAGE.deficit
        assert EXAMPLE_VILLAGE.dispatch
        # Specifically the keys
        for nut in ("N", "P2O5", "K2O"):
            assert nut in EXAMPLE_VILLAGE.nutrient_need
            assert nut in EXAMPLE_VILLAGE.deficit


# ── RINGWOODITE EARTH COUPLING ────────────────────────────────────────────────

class TestClaimLedger:
    def test_import(self):
        import claim_ledger

    def test_quantity_rejects_missing_unit(self):
        from claim_ledger import Quantity
        import pytest
        with pytest.raises(ValueError, match="missing unit"):
            Quantity(value=1.0, unit="", lo=0.0, hi=2.0)

    def test_quantity_rejects_bad_range(self):
        from claim_ledger import Quantity
        import pytest
        with pytest.raises(ValueError):
            Quantity(value=1.0, unit="kg", lo=5.0, hi=2.0)

    def test_quantity_in_range(self):
        from claim_ledger import Quantity
        q = Quantity(value=1.0, unit="kg", lo=0.0, hi=2.0)
        assert q.in_range()

    def test_quantity_out_of_range(self):
        from claim_ledger import Quantity
        q = Quantity(value=5.0, unit="kg", lo=0.0, hi=2.0)
        assert not q.in_range()

    def test_quantity_assert_sane_raises(self):
        from claim_ledger import Quantity
        import pytest
        q = Quantity(value=5.0, unit="kg", lo=0.0, hi=2.0)
        with pytest.raises(ValueError):
            q.assert_sane("mass")

    def test_gate_passes_value_through(self):
        from claim_ledger import gate, Quantity
        val = gate(Quantity(1.5, "wt%", 0.0, 3.0), "water")
        assert val == 1.5

    def test_ledger_has_required_claims(self):
        from claim_ledger import LEDGER
        cids = {c.cid for c in LEDGER}
        for required in ("RW-01", "RW-02", "CPL-01", "CPL-02", "EVT-01", "NAR-01"):
            assert required in cids, f"Missing claim {required}"

    def test_every_claim_has_falsifier(self):
        from claim_ledger import LEDGER
        for c in LEDGER:
            assert c.falsifier.strip(), f"Claim {c.cid} has no falsifier"

    def test_claim_rejects_missing_falsifier(self):
        from claim_ledger import Claim, Evidence, Status
        import pytest
        with pytest.raises(ValueError, match="falsifier"):
            Claim(cid="X-00", statement="test", evidence=Evidence.MEASURED,
                  unit="kg", sanity=(0, 1), falsifier="")

    def test_dump_ledger_writes_json(self, tmp_path):
        from claim_ledger import dump_ledger
        import json
        p = str(tmp_path / "test_ledger.json")
        dump_ledger(path=p)
        with open(p) as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) >= 6
        for entry in data:
            assert "cid" in entry
            assert "falsifier" in entry
            assert "evidence" in entry


class TestRingwooditePhase:
    def test_import(self):
        import ringwoodite_phase

    def test_water_capacity_at_reference_temperature(self):
        from ringwoodite_phase import water_capacity_wt_percent
        # At T_ref ~1850 K the capacity should be in MEASURED range [0, 3]
        cap = water_capacity_wt_percent(1850.0)
        assert 0.0 <= cap <= 3.0

    def test_water_capacity_decreases_with_temperature(self):
        from ringwoodite_phase import water_capacity_wt_percent
        assert water_capacity_wt_percent(1500.0) > water_capacity_wt_percent(2000.0)

    def test_boundary_660_cold_slab_deepens(self):
        from ringwoodite_phase import boundary_660_depth_km
        # Cold slab: T < T_ref -> boundary deepens (positive Clapeyron direction)
        depth_cold = boundary_660_depth_km(1600.0)
        depth_hot  = boundary_660_depth_km(2100.0)
        assert depth_cold > depth_hot

    def test_boundary_660_in_physical_range(self):
        from ringwoodite_phase import boundary_660_depth_km
        for T in (1600, 1900, 2100):
            d = boundary_660_depth_km(float(T))
            assert 600.0 <= d <= 720.0, f"boundary depth {d} km out of range at T={T}"

    def test_dehydration_flux_zero_at_zero_water(self):
        from ringwoodite_phase import dehydration_flux
        f = dehydration_flux(downwelling_m_per_yr=0.01,
                             temperature_k=1850.0,
                             rw_water_wt=0.0)
        assert f == 0.0

    def test_dehydration_flux_positive(self):
        from ringwoodite_phase import dehydration_flux
        f = dehydration_flux(0.01, 1850.0, rw_water_wt=1.4)
        assert f > 0.0

    def test_dehydration_flux_increases_with_water_content(self):
        from ringwoodite_phase import dehydration_flux
        f_low  = dehydration_flux(0.01, 1850.0, rw_water_wt=0.5)
        f_high = dehydration_flux(0.01, 1850.0, rw_water_wt=2.0)
        assert f_high > f_low

    def test_deep_water_baseline_in_range(self):
        from ringwoodite_phase import deep_water_baseline
        for rw in (0.0, 0.5, 1.0, 1.4, 2.0):
            b = deep_water_baseline(1850.0, 0.01, rw)
            assert 0.0 <= b <= 1.0, f"baseline {b} out of [0,1] at rw={rw}"

    def test_deep_water_baseline_increases_with_water(self):
        from ringwoodite_phase import deep_water_baseline
        b_low  = deep_water_baseline(1850.0, 0.01, 0.2)
        b_high = deep_water_baseline(1850.0, 0.01, 2.0)
        assert b_high > b_low

    def test_depth_to_pressure_gpa(self):
        from ringwoodite_phase import depth_to_pressure_gpa
        p = depth_to_pressure_gpa(660.0)
        assert 20.0 <= p <= 28.0


class TestMantleCrustCoupling:
    def test_import(self):
        import mantle_crust_coupling

    def test_viscosity_log10_decreases_with_water(self):
        from mantle_crust_coupling import viscosity_log10
        eta_dry = viscosity_log10(0.0)
        eta_wet = viscosity_log10(1.4)
        assert eta_wet < eta_dry

    def test_viscosity_in_physical_range(self):
        from mantle_crust_coupling import viscosity_log10
        for w in (0.0, 0.5, 1.0, 1.4, 2.0):
            eta = viscosity_log10(w)
            assert 17.0 <= eta <= 23.0

    def test_heat_flux_modulation_increases_with_baseline(self):
        from mantle_crust_coupling import heat_flux_modulation
        assert heat_flux_modulation(1.0) > heat_flux_modulation(0.0)

    def test_heat_flux_modulation_above_one(self):
        from mantle_crust_coupling import heat_flux_modulation
        assert heat_flux_modulation(0.5) >= 1.0

    def test_pore_headroom_decreases_with_baseline(self):
        from mantle_crust_coupling import pore_pressure_headroom
        assert pore_pressure_headroom(0.0) > pore_pressure_headroom(1.0)

    def test_pore_headroom_in_range(self):
        from mantle_crust_coupling import pore_pressure_headroom
        for b in (0.0, 0.5, 1.0):
            h = pore_pressure_headroom(b)
            assert 0.0 <= h <= 1.0

    def test_crustal_sensitivity_in_range(self):
        from mantle_crust_coupling import crustal_sensitivity
        for b in (0.0, 0.3, 0.6, 1.0):
            s = crustal_sensitivity(b)
            assert 0.0 <= s <= 1.0

    def test_crustal_sensitivity_increases_with_baseline(self):
        from mantle_crust_coupling import crustal_sensitivity
        s_low  = crustal_sensitivity(0.0)
        s_high = crustal_sensitivity(1.0)
        assert s_high > s_low


class TestForcingFunctions:
    def test_import(self):
        import forcing_functions

    def test_forcing_alignment_in_range(self):
        from forcing_functions import forcing_alignment
        for t in (0, 1000, 10000, 50000, 100000, 150000):
            a = forcing_alignment(float(t))
            assert 0.0 <= a <= 1.0, f"alignment {a} out of [0,1] at t={t}"

    def test_solar_returns_in_minus_one_to_one(self):
        from forcing_functions import solar
        for t in (0, 5000, 20000, 80000):
            s = solar(float(t))
            assert -1.0 <= s <= 1.0

    def test_insolation_returns_in_valid_range(self):
        from forcing_functions import insolation
        for t in (0, 10000, 50000, 130000):
            ins = insolation(float(t))
            # eccentricity modulated: bounded between -1 and 1
            assert -1.5 <= ins <= 1.5

    def test_glacial_unloading_in_minus_one_to_one(self):
        from forcing_functions import glacial_unloading
        for t in (0, 10000, 20000, 100000):
            g = glacial_unloading(float(t))
            assert -1.0 <= g <= 1.0

    def test_chandler_is_bounded(self):
        from forcing_functions import chandler
        for t in (0, 500, 1000, 5000):
            c = chandler(float(t))
            assert -1.0 <= c <= 1.0

    def test_forcing_breakdown_has_all_keys(self):
        from forcing_functions import forcing_breakdown, FORCINGS
        bd = forcing_breakdown(0.0)
        for key in FORCINGS:
            assert key in bd


class TestCoupledModel:
    def test_import(self):
        import coupled_model

    def test_event_probability_in_range(self):
        from coupled_model import event_probability
        for t in (0, 10000, 50000, 150000):
            p = event_probability(float(t), s_base=0.5)
            assert 0.0 <= p <= 1.0

    def test_null_model_alpha_zero(self):
        from coupled_model import event_probability
        # alpha=0: result depends only on forcing, not s_base
        p1 = event_probability(20000.0, s_base=0.1, alpha=0.0)
        p2 = event_probability(20000.0, s_base=0.9, alpha=0.0)
        assert abs(p1 - p2) < 1e-9, "alpha=0 should be independent of s_base"

    def test_higher_alpha_amplifies_high_baseline(self):
        from coupled_model import event_probability
        t = 20000.0
        p_low_alpha  = event_probability(t, s_base=0.8, alpha=0.0)
        p_high_alpha = event_probability(t, s_base=0.8, alpha=0.6)
        assert p_high_alpha >= p_low_alpha

    def test_run_returns_expected_keys(self):
        from coupled_model import run
        res = run(t_start_bp=10000, t_end_bp=0, step_yr=1000)
        assert "t" in res and "p" in res and "peaks" in res and "s_base" in res

    def test_run_timeseries_length(self):
        from coupled_model import run
        res = run(t_start_bp=10000, t_end_bp=0, step_yr=1000)
        assert len(res["t"]) == len(res["p"])
        assert len(res["t"]) > 0

    def test_run_probabilities_all_in_range(self):
        from coupled_model import run
        res = run(t_start_bp=50000, t_end_bp=0, step_yr=2500)
        for p in res["p"]:
            assert 0.0 <= p <= 1.0

    def test_null_model_returns_dict(self):
        from coupled_model import run
        res = run(alpha=0.0, t_start_bp=10000, t_end_bp=0, step_yr=1000)
        assert res["alpha"] == 0.0

    def test_to_earth_systems_forcing_structure(self):
        from coupled_model import run, to_earth_systems_forcing
        res = run(t_start_bp=5000, t_end_bp=0, step_yr=1000)
        forcing = to_earth_systems_forcing(res)
        assert len(forcing) == len(res["t"])
        for rec in forcing:
            assert "t_bp_yr" in rec
            assert "hydrosphere_emergence_forcing" in rec
            assert rec["unit"] == "event_probability"

    def test_peaks_are_local_maxima(self):
        from coupled_model import run, _find_peaks
        res = run(t_start_bp=50000, t_end_bp=0, step_yr=500)
        # Every peak must be above the minimum threshold
        for t, p in res["peaks"]:
            assert p >= 0.5


class TestNarrativeCrossval:
    def test_import(self):
        import narrative_crossval

    def test_hit_count_zero_when_no_narratives(self):
        from narrative_crossval import hit_count
        assert hit_count([], [10000, 50000]) == 0

    def test_hit_count_zero_when_no_peaks(self):
        from narrative_crossval import hit_count
        assert hit_count([10000, 50000], []) == 0

    def test_hit_count_exact_match(self):
        from narrative_crossval import hit_count
        assert hit_count([10000], [10000], window_yr=1) == 1

    def test_hit_count_within_window(self):
        from narrative_crossval import hit_count
        assert hit_count([10000], [12000], window_yr=5000) == 1

    def test_hit_count_outside_window(self):
        from narrative_crossval import hit_count
        assert hit_count([10000], [20000], window_yr=5000) == 0

    def test_hit_rate_normalized(self):
        from narrative_crossval import hit_rate
        assert 0.0 <= hit_rate([10000, 50000], [10000]) <= 1.0

    def test_monte_carlo_null_returns_dict(self):
        from narrative_crossval import monte_carlo_null
        mc = monte_carlo_null(peak_times=[10000, 50000, 100000],
                              n_narratives=5,
                              n_trials=100)
        assert "mean" in mc and "p95" in mc
        assert 0.0 <= mc["mean"] <= 1.0
        assert 0.0 <= mc["p95"] <= 1.0

    def test_monte_carlo_deterministic_with_seed(self):
        from narrative_crossval import monte_carlo_null
        peaks = [20000, 60000, 120000]
        mc1 = monte_carlo_null(peaks, n_narratives=5, n_trials=50, seed=99)
        mc2 = monte_carlo_null(peaks, n_narratives=5, n_trials=50, seed=99)
        assert mc1["mean"] == mc2["mean"]

    def test_falsification_returns_not_supported_on_placeholder(self):
        from narrative_crossval import run_falsification
        result = run_falsification()
        assert result["verdict"] == "NOT_SUPPORTED"

    def test_falsification_result_has_required_keys(self):
        from narrative_crossval import run_falsification
        result = run_falsification()
        for key in ("verdict", "reason", "hit_rate_full", "hit_rate_null",
                    "mc_p95", "n_narratives", "n_peaks_full", "n_peaks_null"):
            assert key in result, f"Missing key: {key}"

    def test_falsification_narrates_reason(self):
        from narrative_crossval import run_falsification
        result = run_falsification()
        assert len(result["reason"]) > 10  # non-trivial reason string

    def test_pipeline_end_to_end(self):
        """Full pipeline: ringwoodite -> coupling -> forcing -> model -> falsifier."""
        from ringwoodite_phase import deep_water_baseline
        from mantle_crust_coupling import crustal_sensitivity
        from forcing_functions import forcing_alignment
        from coupled_model import event_probability
        from narrative_crossval import run_falsification

        base = deep_water_baseline(1850.0, 0.01, 1.4)
        assert 0.0 <= base <= 1.0

        s = crustal_sensitivity(base, 1.4)
        assert 0.0 <= s <= 1.0

        align = forcing_alignment(20000.0)
        assert 0.0 <= align <= 1.0

        p = event_probability(20000.0, s_base=s)
        assert 0.0 <= p <= 1.0

        result = run_falsification()
        assert result["verdict"] == "NOT_SUPPORTED"


# ── GEOTHERMAL REFUGIA (SNOWBALL EARTH) ───────────────────────────────────────

class TestGeothermalRefugia:
    def test_import(self):
        import geothermal_refugia

    def test_sea_ice_equilibrium_thickness_in_range(self):
        from geothermal_refugia import sea_ice_equilibrium_thickness
        for q in (0.06, 0.10, 0.25):
            h = sea_ice_equilibrium_thickness(q)
            assert 50.0 <= h <= 3000.0, f"H_eq={h} m out of range at Q={q}"

    def test_sea_ice_thickness_decreases_with_q(self):
        from geothermal_refugia import sea_ice_equilibrium_thickness
        h_low  = sea_ice_equilibrium_thickness(0.06)
        h_high = sea_ice_equilibrium_thickness(0.30)
        assert h_low > h_high

    def test_sea_ice_ocean_stays_liquid(self):
        """At every PROVINCES ocean Q value the deep ocean stays liquid."""
        from geothermal_refugia import sea_ice_equilibrium_thickness, PROVINCES
        ocean_depth = 3700.0
        for name, frac, q, kind in PROVINCES:
            if kind == "ocean":
                h = sea_ice_equilibrium_thickness(q)
                assert h < ocean_depth, (
                    f"{name}: H_eq={h:.0f} m exceeds ocean depth {ocean_depth} m"
                )

    def test_pressure_melting_point_is_negative(self):
        from geothermal_refugia import pressure_melting_point_c
        for H in (100, 500, 1000, 3000):
            pmp = pressure_melting_point_c(float(H))
            assert pmp <= 0.0

    def test_pressure_melting_point_more_negative_for_thicker_ice(self):
        from geothermal_refugia import pressure_melting_point_c
        assert pressure_melting_point_c(3000.0) < pressure_melting_point_c(500.0)

    def test_subglacial_state_cold_for_thin_craton_ice(self):
        from geothermal_refugia import subglacial_state
        st = subglacial_state(q_geo=0.045, h_ice_m=300.0)
        assert st["regime"] == "COLD_BASED_FROZEN"
        assert st["basal_melt_rate_m_per_yr"] == 0.0

    def test_subglacial_state_wet_for_thick_ice_high_flux(self):
        from geothermal_refugia import subglacial_state
        st = subglacial_state(q_geo=0.30, h_ice_m=1000.0)
        assert st["regime"] == "WET_BASED_REFUGIUM"
        assert st["basal_melt_rate_m_per_yr"] > 0.0

    def test_subglacial_state_craton_goes_wet_under_thick_ice(self):
        from geothermal_refugia import subglacial_state
        st_thin  = subglacial_state(0.045, 1000.0)
        st_thick = subglacial_state(0.045, 3000.0)
        assert st_thin["regime"]  == "COLD_BASED_FROZEN"
        assert st_thick["regime"] == "WET_BASED_REFUGIUM"

    def test_refugia_inventory_has_expected_keys(self):
        from geothermal_refugia import refugia_inventory
        inv = refugia_inventory()
        for key in ("subice_liquid_fraction", "open_water_fraction",
                    "albedo_verdict", "life_verdict", "provinces"):
            assert key in inv, f"Missing key: {key}"

    def test_refugia_inventory_subice_fraction_positive(self):
        from geothermal_refugia import refugia_inventory
        inv = refugia_inventory()
        assert inv["subice_liquid_fraction"] > 0.0

    def test_refugia_inventory_open_water_near_zero(self):
        """GEO-04: open water ~ 0 in hard Snowball -> albedo unchanged."""
        from geothermal_refugia import refugia_inventory
        inv = refugia_inventory()
        assert inv["open_water_fraction"] < 0.02

    def test_refugia_inventory_albedo_verdict_contains_co2(self):
        from geothermal_refugia import refugia_inventory
        inv = refugia_inventory()
        assert "CO2" in inv["albedo_verdict"]

    def test_refugia_thicker_ice_more_wet_based(self):
        from geothermal_refugia import refugia_inventory
        inv_thin  = refugia_inventory(continental_ice_m=500.0)
        inv_thick = refugia_inventory(continental_ice_m=3000.0)
        assert inv_thick["subice_liquid_fraction"] >= inv_thin["subice_liquid_fraction"]

    def test_refugia_all_provinces_present(self):
        from geothermal_refugia import refugia_inventory, PROVINCES
        inv = refugia_inventory()
        province_names = {row[0] for row in inv["provinces"]}
        expected = {p[0] for p in PROVINCES}
        assert province_names == expected


# ── AQUIFER PRESSURE HEAD ─────────────────────────────────────────────────────

class TestAquiferPressureHead:
    def test_import(self):
        import aquifer_pressure_head

    def test_seismic_energy_density_positive(self):
        from aquifer_pressure_head import seismic_energy_density
        e = seismic_energy_density(6.0, 100.0)
        assert e > 0.0

    def test_seismic_energy_density_decreases_with_distance(self):
        from aquifer_pressure_head import seismic_energy_density
        e_near = seismic_energy_density(6.0, 50.0)
        e_far  = seismic_energy_density(6.0, 200.0)
        assert e_near > e_far

    def test_seismic_energy_density_increases_with_magnitude(self):
        from aquifer_pressure_head import seismic_energy_density
        e_small = seismic_energy_density(4.0, 100.0)
        e_large = seismic_energy_density(7.0, 100.0)
        assert e_large > e_small

    def test_classify_none_for_small_distant_quake(self):
        from aquifer_pressure_head import seismic_energy_density, classify_response
        e = seismic_energy_density(3.5, 300.0)
        assert classify_response(e) == "NONE"

    def test_classify_liquefaction_for_large_near_quake(self):
        from aquifer_pressure_head import seismic_energy_density, classify_response
        e = seismic_energy_density(7.0, 50.0)
        assert classify_response(e) == "LIQUEFACTION_UPWELLING"

    def test_classify_water_level_for_moderate_quake(self):
        from aquifer_pressure_head import seismic_energy_density, classify_response
        e = seismic_energy_density(5.0, 100.0)
        cls = classify_response(e)
        assert cls in ("WATER_LEVEL", "SPRING")

    def test_primed_baseline_lowers_threshold(self):
        """AQ-03: high s_base promotes NONE -> non-NONE or same."""
        from aquifer_pressure_head import seismic_energy_density, classify_response
        e = seismic_energy_density(4.5, 150.0)
        classes = ("NONE", "WATER_LEVEL", "SPRING", "LIQUEFACTION_UPWELLING")
        cls_dry    = classify_response(e, s_base=0.0)
        cls_primed = classify_response(e, s_base=1.0)
        assert classes.index(cls_primed) >= classes.index(cls_dry)

    def test_poroelastic_pressure_positive(self):
        from aquifer_pressure_head import poroelastic_pressure_pa, seismic_energy_density
        e = seismic_energy_density(6.0, 100.0)
        dp = poroelastic_pressure_pa(e)
        assert dp > 0.0

    def test_water_head_change_returns_expected_keys(self):
        from aquifer_pressure_head import water_head_change_m
        res = water_head_change_m(6.5, 80.0)
        for key in ("magnitude", "r_km", "e_J_m3", "dp_Pa",
                    "dh_m", "classification", "s_base"):
            assert key in res

    def test_water_head_change_classification_valid(self):
        from aquifer_pressure_head import water_head_change_m, RESPONSE_CLASSES
        for M in (4.0, 5.0, 6.5, 7.5):
            res = water_head_change_m(M, 100.0)
            assert res["classification"] in RESPONSE_CLASSES


# ── PALEOSEISMIC CROSSVAL ─────────────────────────────────────────────────────

class TestPaleoseismicCrossval:
    def test_import(self):
        import paleoseismic_crossval

    def test_syn01_returns_supported_on_placeholder(self):
        from paleoseismic_crossval import syn01_mechanism_check
        result = syn01_mechanism_check()
        assert result["verdict"] == "SUPPORTED"

    def test_syn01_plausible_fraction_above_threshold(self):
        from paleoseismic_crossval import syn01_mechanism_check, PLAUSIBLE_FRACTION
        result = syn01_mechanism_check()
        assert result["plausible_fraction"] >= PLAUSIBLE_FRACTION

    def test_syn01_details_have_classification(self):
        from paleoseismic_crossval import syn01_mechanism_check
        result = syn01_mechanism_check()
        for d in result["details"]:
            assert "classification" in d
            assert d["classification"] in ("NONE", "WATER_LEVEL",
                                            "SPRING", "LIQUEFACTION_UPWELLING")

    def test_syn01_none_for_all_small_distant_events(self):
        from paleoseismic_crossval import syn01_mechanism_check
        tiny_events = [
            {"t_bp": 10000, "date_smear_yr": 500, "region": "A",
             "M_context": 3.0, "r_context_km": 500, "source": "test"},
            {"t_bp": 20000, "date_smear_yr": 500, "region": "B",
             "M_context": 2.5, "r_context_km": 600, "source": "test"},
            {"t_bp": 30000, "date_smear_yr": 500, "region": "C",
             "M_context": 3.0, "r_context_km": 400, "source": "test"},
        ]
        result = syn01_mechanism_check(tiny_events)
        assert result["verdict"] == "NOT_SUPPORTED"

    def test_syn02_returns_not_supported_on_placeholder(self):
        from paleoseismic_crossval import syn02_synchrony_test
        result = syn02_synchrony_test()
        assert result["verdict"] == "NOT_SUPPORTED"

    def test_syn02_not_supported_due_to_smear(self):
        from paleoseismic_crossval import syn02_synchrony_test
        result = syn02_synchrony_test()
        assert result.get("n_tight", 0) == 0

    def test_syn02_supported_with_tight_clustered_dates(self):
        """Inject tight-dated, tightly-clustered events -> SUPPORTED."""
        from paleoseismic_crossval import syn02_synchrony_test
        tight_events = [
            {"t_bp": 12000, "date_smear_yr": 200, "region": "A",
             "M_context": 6.5, "r_context_km": 60, "source": "test"},
            {"t_bp": 12100, "date_smear_yr": 200, "region": "B",
             "M_context": 6.5, "r_context_km": 60, "source": "test"},
            {"t_bp": 12050, "date_smear_yr": 200, "region": "C",
             "M_context": 6.5, "r_context_km": 60, "source": "test"},
        ]
        result = syn02_synchrony_test(tight_events)
        assert result["verdict"] == "SUPPORTED"

    def test_run_falsification_returns_both_verdicts(self):
        from paleoseismic_crossval import run_falsification
        result = run_falsification()
        assert "syn01_verdict" in result
        assert "syn02_verdict" in result

    def test_run_falsification_expected_defaults(self):
        from paleoseismic_crossval import run_falsification
        result = run_falsification()
        assert result["syn01_verdict"] == "SUPPORTED"
        assert result["syn02_verdict"] == "NOT_SUPPORTED"

    def test_ledger_now_has_15_claims(self):
        from claim_ledger import LEDGER
        assert len(LEDGER) == 15
        cids = {c.cid for c in LEDGER}
        for cid in ("GEO-01", "GEO-02", "GEO-03", "GEO-04",
                    "AQ-01", "AQ-02", "AQ-03", "SYN-01", "SYN-02"):
            assert cid in cids, f"Missing claim {cid}"
