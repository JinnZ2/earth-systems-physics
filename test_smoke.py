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
