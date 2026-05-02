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
