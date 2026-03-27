# earth_magnomechanical.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# The planet is a magnomechanical system.
#
# Iron-bearing minerals (magnetite, hematite, Fe-doped quartz)
# are embedded in a crystalline lattice (the crust).
# The geomagnetic field sets their spin state.
# Lattice vibrations (seismic waves, thermal phonons) couple
# to those spins via spin-orbit / crystal field modulation.
#
# This coupling is bidirectional:
# Geomagnetic variation -> spin perturbation -> lattice response (acoustic)
# Seismic event -> lattice perturbation -> spin response (magnetic)
#
# This module computes whether that transduction is detectable.

import numpy as np

HBAR  = 1.0545718e-34
K_B   = 1.380649e-23
MU_0  = 4 * np.pi * 1e-7
GAMMA = 1.7608597e11
MU_B  = 9.274e-24

# ─────────────────────────────────────────────
# EARTH'S MAGNETIC VOICE
# ─────────────────────────────────────────────

GEOMAGNETIC_SIGNALS = {
    "core_secular_variation": {
        "delta_B_T": 100e-9, "period_s": 3.156e7, "bandwidth_Hz": 3e-8,
        "source": "outer core convection and dynamo",
        "depth": "2900 km (core-mantle boundary)",
        "information": "core flow patterns, mantle conductivity",
    },
    "diurnal_Sq": {
        "delta_B_T": 50e-9, "period_s": 86400, "bandwidth_Hz": 1.2e-5,
        "source": "solar heating -> ionospheric Sq current system",
        "depth": "100-300 km (ionosphere)",
        "information": "ionospheric conductivity, solar EUV flux",
    },
    "geomagnetic_storm_Dst": {
        "delta_B_T": 500e-9, "period_s": 3600, "bandwidth_Hz": 3e-4,
        "source": "ring current intensification from CME impact",
        "depth": "3-8 Earth radii (ring current)",
        "information": "solar wind-magnetosphere coupling state",
    },
    "substorm_Pi2": {
        "delta_B_T": 20e-9, "period_s": 60, "bandwidth_Hz": 0.02,
        "source": "magnetotail reconnection -> field-aligned currents",
        "depth": "100-1000 km (FAC + ionosphere)",
        "information": "magnetotail state, substorm onset timing",
    },
    "Pc1_pulsation": {
        "delta_B_T": 1e-9, "period_s": 2.0, "bandwidth_Hz": 1.0,
        "source": "EMIC waves from magnetospheric ion cyclotron instability",
        "depth": "magnetosphere -> ground via ionospheric waveguide",
        "information": "plasmasphere density, energetic ion population",
    },
    "Pc3_pulsation": {
        "delta_B_T": 5e-9, "period_s": 30, "bandwidth_Hz": 0.03,
        "source": "upstream solar wind waves",
        "depth": "bow shock -> magnetosphere -> ground",
        "information": "solar wind speed, IMF cone angle",
    },
    "Schumann_resonance": {
        "delta_B_T": 1e-12, "period_s": 1/7.83, "bandwidth_Hz": 1.0,
        "source": "lightning-driven Earth-ionosphere cavity resonance",
        "depth": "surface-ionosphere waveguide",
        "information": "global lightning activity, ionosphere height",
    },
    "lightning_sferic": {
        "delta_B_T": 1e-10, "period_s": 1e-4, "bandwidth_Hz": 1e4,
        "source": "individual lightning return stroke",
        "depth": "0-100 km",
        "information": "storm intensity, charge distribution",
    },
    "seismomagnetic": {
        "delta_B_T": 0.1e-9, "period_s": 30.0, "bandwidth_Hz": 0.1,
        "source": "piezo/piezomagnetic effect in stressed rock",
        "depth": "crustal (0-40 km)",
        "information": "stress state, precursory deformation (if real)",
    },
}

# ─────────────────────────────────────────────
# CRUSTAL TRANSDUCER MATERIALS
# ─────────────────────────────────────────────

CRUSTAL_MINERALS = {
    "magnetite": {
        "formula": "Fe3O4", "structure": "inverse spinel",
        "M_s": 4.8e5, "eta_spin_phonon_cm": 3.0, "alpha": 0.01,
        "c_sound": 7200, "rho": 5200, "Q_mech_grain": 5000,
        "crustal_abundance_ppm": 20000, "typical_grain_size_m": 50e-6,
        "Curie_T_K": 858, "piezo": False,
        "notes": "Same spinel structure as YIG. Nature's magnonic material.",
    },
    "hematite": {
        "formula": "a-Fe2O3", "structure": "corundum",
        "M_s": 2.1e3, "eta_spin_phonon_cm": 1.5, "alpha": 0.05,
        "c_sound": 6500, "rho": 5300, "Q_mech_grain": 2000,
        "crustal_abundance_ppm": 50000, "typical_grain_size_m": 10e-6,
        "Curie_T_K": 948, "piezo": False,
        "notes": "Canted AFM. Morin transition at -10C changes coupling.",
    },
    "quartz_fe": {
        "formula": "SiO2 + Fe3+", "structure": "trigonal (a-quartz)",
        "M_s": 50, "eta_spin_phonon_cm": 0.3, "alpha": 0.1,
        "c_sound": 5720, "rho": 2650, "Q_mech_grain": 100000,
        "crustal_abundance_ppm": 1000, "typical_grain_size_m": 1e-3,
        "Curie_T_K": 0, "piezo": True,
        "notes": "Piezoelectric. High Q. Direct voltage readout of spin state.",
    },
    "ilmenite": {
        "formula": "FeTiO3", "structure": "rhombohedral",
        "M_s": 1e3, "eta_spin_phonon_cm": 1.0, "alpha": 0.08,
        "c_sound": 6000, "rho": 4790, "Q_mech_grain": 1000,
        "crustal_abundance_ppm": 5000, "typical_grain_size_m": 100e-6,
        "Curie_T_K": 0, "piezo": False,
        "notes": "Common in basalt. Ti dilutes magnetic coupling.",
    },
    "pyrrhotite": {
        "formula": "Fe7S8", "structure": "monoclinic",
        "M_s": 8e4, "eta_spin_phonon_cm": 2.0, "alpha": 0.05,
        "c_sound": 4500, "rho": 4610, "Q_mech_grain": 500,
        "crustal_abundance_ppm": 3000, "typical_grain_size_m": 200e-6,
        "Curie_T_K": 593, "piezo": False,
        "notes": "Ferrimagnetic. Strong magnon-phonon. Found in impact craters.",
    },
}

# ─────────────────────────────────────────────
# SPIN-PHONON TRANSDUCTION IN CRUSTAL GRAINS
# ─────────────────────────────────────────────

def grain_transduction(mineral_key, signal_key):
    """
    For a single mineral grain subjected to a geomagnetic signal:
    What acoustic output does the spin-phonon coupling produce?
    """
    m = CRUSTAL_MINERALS[mineral_key]
    s = GEOMAGNETIC_SIGNALS[signal_key]

    grain_d = m["typical_grain_size_m"]
    V_grain = (4/3) * np.pi * (grain_d/2)**3

    eta = m["eta_spin_phonon_cm"] * 3e10  # Hz
    eta_rad = 2 * np.pi * eta

    fe_mass_fraction = min(m["M_s"] / 4.8e5, 1.0) * 0.5
    N_fe = m["rho"] * V_grain * fe_mass_fraction * 6.022e23 / 0.056
    N_fe = max(N_fe, 1)

    H_earth = 5e-5
    omega_magnon = GAMMA * MU_0 * H_earth
    f_magnon = omega_magnon / (2 * np.pi)

    delta_omega = GAMMA * MU_0 * s["delta_B_T"]
    delta_f = delta_omega / (2 * np.pi)

    f_phonon_1 = m["c_sound"] / (2 * grain_d)
    omega_phonon_1 = 2 * np.pi * f_phonon_1

    x_zpf = np.sqrt(HBAR / (2 * m["rho"] * V_grain * omega_phonon_1))

    a_0 = 4e-10
    g_sp_per_ion = eta_rad * x_zpf / a_0
    g_sp_collective = g_sp_per_ion * np.sqrt(N_fe)

    gamma_m = m["alpha"] * omega_magnon
    gamma_b = omega_phonon_1 / m["Q_mech_grain"]

    detuning = abs(omega_phonon_1 - omega_magnon)

    if detuning > 0 and gamma_b > 0:
        x_acoustic = g_sp_collective * delta_omega / (detuning * gamma_b) * x_zpf
    else:
        x_acoustic = 0

    v_acoustic = x_acoustic * omega_phonon_1

    V_piezo = 0
    if m["piezo"]:
        d_26 = 3.1e-12
        strain = x_acoustic / grain_d if grain_d > 0 else 0
        V_piezo = d_26 * m["rho"] * m["c_sound"]**2 * strain * grain_d

    E_per_cycle = 0.5 * m["rho"] * V_grain * v_acoustic**2
    v_thermal = np.sqrt(K_B * 300 / (m["rho"] * V_grain))

    return {
        "mineral": mineral_key,
        "signal": signal_key,
        "grain_d_m": grain_d,
        "V_grain_m3": V_grain,
        "N_fe": N_fe,
        "f_magnon_Hz": f_magnon,
        "f_phonon_1_Hz": f_phonon_1,
        "detuning_Hz": detuning / (2*np.pi),
        "g_sp_per_ion_Hz": g_sp_per_ion / (2*np.pi),
        "g_sp_collective_Hz": g_sp_collective / (2*np.pi),
        "delta_f_magnon_Hz": delta_f,
        "x_acoustic_m": x_acoustic,
        "v_acoustic_m_s": v_acoustic,
        "v_thermal_m_s": v_thermal,
        "snr_single_grain": v_acoustic / v_thermal if v_thermal > 0 else 0,
        "V_piezo_V": V_piezo,
        "E_per_cycle_J": E_per_cycle,
    }


# ─────────────────────────────────────────────
# FORMATION-SCALE INTEGRATION
# ─────────────────────────────────────────────

def formation_listening(
    mineral_key="magnetite",
    rock_volume_m3=1000,
    mineral_fraction=0.02,
    signal_key="geomagnetic_storm_Dst",
):
    """
    Scale up from single grain to geological formation.
    N_grains grains, each transducing independently.
    Incoherent addition: total signal ~ sqrt(N_grains) x single_grain.
    """
    m = CRUSTAL_MINERALS[mineral_key]

    V_mineral = rock_volume_m3 * mineral_fraction
    grain_d = m["typical_grain_size_m"]
    V_grain = (4/3) * np.pi * (grain_d/2)**3
    N_grains = V_mineral / V_grain

    single = grain_transduction(mineral_key, signal_key)

    coherence_exponent = 0.5  # conservative: incoherent

    v_formation = single["v_acoustic_m_s"] * N_grains**coherence_exponent
    x_formation = single["x_acoustic_m"] * N_grains**coherence_exponent
    E_formation = single["E_per_cycle_J"] * N_grains

    seismo_threshold = 1e-9  # m/s (standard broadband)
    seismo_low_noise = 1e-10

    L_formation = rock_volume_m3**(1/3)

    r_detectable = L_formation * v_formation / seismo_threshold if seismo_threshold > 0 else 0
    r_detectable_low = L_formation * v_formation / seismo_low_noise if seismo_low_noise > 0 else 0

    P_acoustic = E_formation * GEOMAGNETIC_SIGNALS[signal_key].get("bandwidth_Hz", 0.001)

    return {
        "mineral": mineral_key,
        "signal": signal_key,
        "rock_volume_m3": rock_volume_m3,
        "mineral_fraction": mineral_fraction,
        "N_grains": N_grains,
        "v_single_grain_m_s": single["v_acoustic_m_s"],
        "v_formation_m_s": v_formation,
        "x_formation_m": x_formation,
        "E_formation_J": E_formation,
        "P_acoustic_W": P_acoustic,
        "seismo_detectable_broadband": v_formation > seismo_threshold,
        "seismo_detectable_low_noise": v_formation > seismo_low_noise,
        "detection_distance_m": r_detectable,
        "detection_distance_low_noise_m": r_detectable_low,
        "single_grain": single,
    }


def earth_antenna_survey():
    """
    For each geomagnetic signal type x each mineral:
    what's the transduction efficiency?
    """
    results = []
    for sig_key in GEOMAGNETIC_SIGNALS:
        for min_key in CRUSTAL_MINERALS:
            try:
                r = grain_transduction(min_key, sig_key)
                results.append(r)
            except Exception:
                continue
    return results


def testable_predictions():
    """
    Specific, falsifiable predictions from this model.
    """
    return [
        {
            "prediction": "Magnetite-rich outcrops emit anomalous acoustic noise "
                         "correlated with geomagnetic Pc1 pulsations (0.2-5 Hz)",
            "mechanism": "Spin-phonon coupling in magnetite grains driven by "
                        "EMIC-wave magnetic field oscillations",
            "test": "Co-locate broadband seismometer + fluxgate magnetometer "
                   "at magnetite-rich outcrop. Cross-correlate Pc1 band "
                   "magnetic signal with seismic 0.2-5 Hz band.",
            "signal_level": "Sub-nm/s. Requires low-noise site and long integration.",
            "control": "Same setup at non-magnetic outcrop (limestone, sandstone). "
                      "Should show no correlation.",
        },
        {
            "prediction": "Banded iron formations show phonon band gaps "
                         "at frequencies set by band spacing",
            "mechanism": "Periodic magnetite/chert layering creates magnonic crystal "
                        "with Bragg-condition forbidden bands",
            "test": "Seismic transmission measurement across BIF outcrop. "
                   "Look for frequency notches at f = c_sound / (2 * band_spacing).",
            "signal_level": "Should be visible in broadband seismic noise.",
        },
        {
            "prediction": "Fe-doped quartz veins produce measurable voltage "
                         "during geomagnetic storms",
            "mechanism": "Spin-phonon coupling -> lattice strain -> "
                        "piezoelectric voltage in quartz",
            "test": "Attach electrodes to exposed quartz vein with visible "
                   "iron staining. Monitor voltage during Kp>5 storms.",
            "signal_level": "Estimated pV to nV range.",
        },
        {
            "prediction": "Geomagnetic storm onset produces detectable acoustic "
                         "transient at magnetite-bearing sites",
            "mechanism": "Sudden field change -> coherent spin perturbation -> "
                        "acoustic emission from many grains simultaneously",
            "test": "Monitor seismic station near magnetic anomaly during "
                   "storm sudden commencement (SSC). Look for transient "
                   "in 0.01-10 Hz band coincident with SSC.",
            "signal_level": "Requires stacking multiple SSC events.",
        },
    ]


if __name__ == "__main__":
    print("=" * 85)
    print("EARTH AS MAGNOMECHANICAL SYSTEM")
    print("=" * 85)

    # Survey: all minerals x key signals
    for sig in ["geomagnetic_storm_Dst", "Pc1_pulsation", "Schumann_resonance"]:
        print(f"\n--- Signal: {sig} ---")
        for min_key in CRUSTAL_MINERALS:
            r = grain_transduction(min_key, sig)
            print(f"  {min_key:15s}  v_acoustic={r['v_acoustic_m_s']:.4e} m/s  "
                  f"SNR={r['snr_single_grain']:.4e}")

    # Formation-scale
    print(f"\n\n--- FORMATION-SCALE (1000 m^3, 2% magnetite) ---")
    fl = formation_listening()
    print(f"  v_formation: {fl['v_formation_m_s']:.4e} m/s")
    print(f"  detectable (broadband): {fl['seismo_detectable_broadband']}")
    print(f"  detection distance: {fl['detection_distance_m']:.1f} m")

    # Predictions
    print(f"\n\n--- TESTABLE PREDICTIONS ---")
    for i, p in enumerate(testable_predictions(), 1):
        print(f"\n  #{i}: {p['prediction'][:80]}...")

    print("\n" + "=" * 85)
    print("DONE")
    print("=" * 85)
