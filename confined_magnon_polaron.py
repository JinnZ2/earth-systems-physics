# confined_magnon_polaron.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Two analyses:
# 1. CONFINED MODES in mm-scale quartz crystals
#    Discrete phonon spectrum, crystal-volume mode volume,
#    magnon tuned through resonances with 4-axis coil.
#
# 2. GEOLOGICAL FORMATIONS as natural magnomechanical cavities
#    Iron-bearing quartz veins, banded iron formations,
#    magnetite in granite — do they show magnon-polaron physics?
#
# The bulk crossover analysis (magnon_polaron_hybridization.py)
# showed the coupling vanishes because mode volume -> lambda^3.
# Confinement fixes this: mode volume -> crystal volume.

import numpy as np

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

HBAR    = 1.0545718e-34
K_B     = 1.380649e-23
MU_0    = 4 * np.pi * 1e-7
GAMMA   = 1.7608597e11
MU_B    = 9.274e-24
C_LIGHT = 2.998e8

# ─────────────────────────────────────────────
# PART 1: CONFINED CRYSTAL MODES
# ─────────────────────────────────────────────

def crystal_phonon_modes(thickness_m, c_sound, n_max=10, mode_type="thickness_shear"):
    """
    Discrete phonon modes of a finite crystal.

    Thickness shear (AT-cut quartz):
      f_n = n * c_shear / (2 * thickness)

    These are the modes the magnon can couple to.
    Returns list of dicts with mode_number, frequency_Hz, omega_rad_s.
    """
    modes = []
    for n in range(1, n_max + 1):
        if mode_type == "thickness_shear":
            f = n * c_sound / (2 * thickness_m)
        elif mode_type == "longitudinal":
            f = n * c_sound / (2 * thickness_m)
        elif mode_type == "flexural":
            f = (n**2) * c_sound * thickness_m / (4 * np.pi * (thickness_m/2)**2)
        else:
            f = n * c_sound / (2 * thickness_m)

        modes.append({
            "n": n,
            "f_Hz": f,
            "omega_rad_s": 2 * np.pi * f,
        })
    return modes


def magnon_freq_from_field(H0):
    """Zeeman magnon frequency for dilute spins: f = gamma*mu_0*H0/(2*pi)"""
    return GAMMA * MU_0 * H0 / (2 * np.pi)


def field_for_frequency(f_target):
    """H0 needed to put magnon at target frequency."""
    return 2 * np.pi * f_target / (GAMMA * MU_0)


def confined_coupling(
    thickness_m=0.1e-3,
    diameter_m=5e-3,
    c_sound=3764.0,
    rho=2650.0,
    fe_ppm=100,
    B_me=1e4,
    alpha=0.1,
    Q_mech=1e6,
    T=300.0,
):
    """
    Magnon-phonon coupling in a CONFINED crystal.

    KEY DIFFERENCE from bulk:
    Mode volume = crystal volume (not lambda^3)
    This makes zero-point motion MUCH larger.
    """
    M_s = fe_ppm * 1.0  # A/m
    r = diameter_m / 2
    V_crystal = np.pi * r**2 * thickness_m

    # Discrete phonon modes
    modes = crystal_phonon_modes(thickness_m, c_sound, n_max=10)

    results = []

    for mode in modes:
        f_phonon = mode["f_Hz"]
        omega_phonon = mode["omega_rad_s"]
        n_mode = mode["n"]

        # H0 needed to match magnon to this phonon mode
        H0_match = field_for_frequency(f_phonon)

        # Zero-point motion -- CONFINED mode volume
        x_zpf = np.sqrt(HBAR / (2 * rho * V_crystal * omega_phonon))

        # Compare to bulk x_zpf (mode volume = lambda^3)
        lambda_phonon = c_sound / f_phonon
        V_bulk = lambda_phonon**3
        x_zpf_bulk = np.sqrt(HBAR / (2 * rho * V_bulk * omega_phonon))

        confinement_enhancement = x_zpf / x_zpf_bulk if x_zpf_bulk > 0 else 0

        # Magnomechanical coupling at resonance
        g_mb = (B_me / max(M_s, 1)) * x_zpf * omega_phonon

        # Linewidths
        gamma_m = alpha * GAMMA * MU_0 * H0_match  # magnon linewidth
        gamma_b = omega_phonon / Q_mech              # phonon linewidth

        # Cooperativity
        C_mb = (4 * g_mb**2) / (gamma_m * gamma_b) if (gamma_m > 0 and gamma_b > 0) else 0

        # Gap vs linewidths
        gap = 2 * g_mb
        total_linewidth = gamma_m + gamma_b
        gap_resolved = gap > total_linewidth
        gap_ratio = gap / total_linewidth if total_linewidth > 0 else 0

        # Thermal phonon occupation
        x_th = HBAR * omega_phonon / (K_B * T)
        n_thermal = 1 / (np.exp(min(x_th, 500)) - 1) if x_th < 500 else 0

        # Piezoelectric voltage from zero-point motion
        d_26 = 3.1e-12  # C/N
        V_piezo = d_26 * rho * c_sound**2 * omega_phonon * x_zpf

        # Energy per magnon-polaron
        E_polaron = HBAR * omega_phonon
        E_per_bit = E_polaron / Q_mech

        # Phonon lifetime
        tau_phonon = Q_mech / omega_phonon

        results.append({
            "mode_n": n_mode,
            "f_phonon_Hz": f_phonon,
            "H0_match_T": H0_match,
            "x_zpf_confined_m": x_zpf,
            "x_zpf_bulk_m": x_zpf_bulk,
            "confinement_enhancement": confinement_enhancement,
            "g_mb_Hz": g_mb / (2 * np.pi),
            "g_mb_rad_s": g_mb,
            "gamma_m_Hz": gamma_m / (2 * np.pi),
            "gamma_b_Hz": gamma_b / (2 * np.pi),
            "cooperativity": C_mb,
            "gap_Hz": gap / (2 * np.pi),
            "gap_resolved": gap_resolved,
            "gap_over_linewidth": gap_ratio,
            "n_thermal": n_thermal,
            "V_piezo_zpf_V": V_piezo,
            "E_polaron_J": E_polaron,
            "E_per_bit_J": E_per_bit,
            "tau_phonon_s": tau_phonon,
            "V_crystal_m3": V_crystal,
        })

    return results


# ─────────────────────────────────────────────
# PART 2: GEOLOGICAL FORMATIONS
# ─────────────────────────────────────────────

GEOLOGICAL_PRESETS = {
    "banded_iron_formation": {
        "name": "Banded Iron Formation (BIF)",
        "desc": "Precambrian iron-silica layers. Alternating magnetite/chert bands. "
                "Natural magnonic crystal -- periodic magnetic/non-magnetic structure.",
        "thickness_m": 0.01, "length_m": 100.0, "width_m": 50.0,
        "M_s": 4.8e5, "B_me": 3e6, "alpha": 0.05, "c_sound": 5500.0,
        "rho": 5200.0, "Q_mech": 500, "T": 290.0, "H_earth": 5e-5,
        "fe_fraction": 0.30, "periodicity_m": 0.02,
    },
    "quartz_vein_iron": {
        "name": "Iron-bearing quartz vein",
        "desc": "Hydrothermal quartz with Fe3+ substitution. "
                "Natural single-crystal-ish with piezoelectric response.",
        "thickness_m": 0.5, "length_m": 20.0, "width_m": 2.0,
        "M_s": 500.0, "B_me": 5e4, "alpha": 0.08, "c_sound": 5720.0,
        "rho": 2650.0, "Q_mech": 1e4, "T": 285.0, "H_earth": 5e-5,
        "fe_fraction": 0.001, "periodicity_m": 0,
    },
    "magnetite_granite": {
        "name": "Magnetite in granite batholith",
        "desc": "Disseminated magnetite grains in granitic host. "
                "Each grain is a magnonic resonator. Host is the acoustic cavity.",
        "thickness_m": 0.001, "length_m": 1000.0, "width_m": 500.0,
        "M_s": 4.8e5, "B_me": 6.96e6, "alpha": 0.01, "c_sound": 7200.0,
        "rho": 5200.0, "Q_mech": 5000, "T": 295.0, "H_earth": 5e-5,
        "fe_fraction": 0.02, "periodicity_m": 0.05,
    },
    "lodestone_outcrop": {
        "name": "Natural lodestone outcrop",
        "desc": "Lightning-magnetized magnetite. Strong remanent magnetization. "
                "Already a natural permanent magnet -- no external field needed.",
        "thickness_m": 1.0, "length_m": 10.0, "width_m": 5.0,
        "M_s": 4.8e5, "B_me": 6.96e6, "alpha": 0.05, "c_sound": 5500.0,
        "rho": 5200.0, "Q_mech": 200, "T": 290.0, "H_earth": 5e-5,
        "fe_fraction": 0.80, "periodicity_m": 0,
    },
    "pillow_basalt_ocean": {
        "name": "Pillow basalt (ocean floor)",
        "desc": "Submarine volcanic rock with titanomagnetite. Records paleomagnetic "
                "field. Potential magnon-phonon coupling with ocean acoustic modes.",
        "thickness_m": 0.3, "length_m": 1.0, "width_m": 0.5,
        "M_s": 1e5, "B_me": 2e6, "alpha": 0.08, "c_sound": 6000.0,
        "rho": 2900.0, "Q_mech": 100, "T": 275.0, "H_earth": 5e-5,
        "fe_fraction": 0.05, "periodicity_m": 0.3,
    },
}


def geological_magnomechanical(preset_key):
    """
    Analyze a geological formation as a natural magnomechanical system.

    The formation is:
    - MAGNON HOST: magnetic mineral (magnetite, Fe-bearing quartz)
    - PHONON CAVITY: the rock itself (acoustic resonator)
    - EXTERNAL FIELD: Earth's magnetic field
    - READOUT: seismic/acoustic sensors? Magnetometer?
    """
    p = GEOLOGICAL_PRESETS[preset_key]

    V_formation = p["thickness_m"] * p["length_m"] * p["width_m"]
    V_magnetic = V_formation * p["fe_fraction"]

    # Phonon modes of the formation
    modes = crystal_phonon_modes(p["thickness_m"], p["c_sound"], n_max=5)

    # Magnon frequency from Earth's field
    f_magnon_earth = GAMMA * MU_0 * p["H_earth"] / (2 * np.pi)

    results = {
        "name": p["name"],
        "desc": p["desc"],
        "V_formation_m3": V_formation,
        "V_magnetic_m3": V_magnetic,
        "f_magnon_earth_Hz": f_magnon_earth,
        "phonon_modes": [],
        "magnonic_crystal": p["periodicity_m"] > 0,
    }

    # Magnonic crystal analysis (for periodic structures)
    if p["periodicity_m"] > 0:
        k_bragg = np.pi / p["periodicity_m"]
        f_bragg = p["c_sound"] * k_bragg / (2 * np.pi)
        bandgap_frac = p["fe_fraction"] * 0.1
        bandgap_Hz = f_bragg * bandgap_frac

        results["magnonic_crystal_data"] = {
            "periodicity_m": p["periodicity_m"],
            "k_bragg": k_bragg,
            "f_bragg_Hz": f_bragg,
            "bandgap_Hz": bandgap_Hz,
            "bandgap_wavelength_m": p["c_sound"] / bandgap_Hz if bandgap_Hz > 0 else np.inf,
        }

    for mode in modes:
        f_phonon = mode["f_Hz"]
        omega_phonon = mode["omega_rad_s"]

        # H0 to match
        H_match = field_for_frequency(f_phonon)

        # With Earth's field only: detuning
        detuning = abs(f_phonon - f_magnon_earth)

        # Zero-point motion (confined to magnetic volume)
        x_zpf = np.sqrt(HBAR / (2 * p["rho"] * V_magnetic * omega_phonon))

        # Coupling
        g_mb = (p["B_me"] / max(p["M_s"], 1)) * x_zpf * omega_phonon

        # Linewidths
        gamma_m = p["alpha"] * GAMMA * MU_0 * p["H_earth"]
        gamma_b = omega_phonon / p["Q_mech"]

        # Cooperativity
        C = (4 * g_mb**2) / (gamma_m * gamma_b) if (gamma_m > 0 and gamma_b > 0) else 0

        # Thermal occupation
        n_th = K_B * p["T"] / (HBAR * omega_phonon) if omega_phonon > 0 else 0

        # Energy stored in thermal phonon mode
        E_thermal = n_th * HBAR * omega_phonon

        # Magnon-phonon energy exchange rate
        P_exchange = g_mb * HBAR * omega_phonon * n_th  # W (per mode)

        # Seismic detection threshold
        v_zpf = x_zpf * omega_phonon
        seismometer_threshold = 1e-9  # m/s

        # Thermal velocity amplitude (classical)
        v_thermal = np.sqrt(K_B * p["T"] / (p["rho"] * V_magnetic))

        # Magnetically-driven phonon amplitude
        delta_H = 50e-9  # T (daily variation)
        delta_omega_magnon = GAMMA * MU_0 * delta_H
        x_driven = g_mb * delta_omega_magnon / (gamma_b * omega_phonon) * \
                   np.sqrt(HBAR / (2 * p["rho"] * V_magnetic * omega_phonon))
        v_driven = x_driven * omega_phonon

        results["phonon_modes"].append({
            "mode_n": mode["n"],
            "f_phonon_Hz": f_phonon,
            "H_match_T": H_match,
            "detuning_from_earth_Hz": detuning,
            "x_zpf_m": x_zpf,
            "g_mb_Hz": g_mb / (2 * np.pi),
            "gamma_m_Hz": gamma_m / (2 * np.pi),
            "gamma_b_Hz": gamma_b / (2 * np.pi),
            "cooperativity": C,
            "n_thermal": n_th,
            "v_zpf_m_s": v_zpf,
            "v_thermal_m_s": v_thermal,
            "v_driven_m_s": v_driven,
            "seismic_detectable": v_driven > seismometer_threshold,
        })

    return results


# ─────────────────────────────────────────────
# PART 3: EARTH SYSTEMS COUPLING
# ─────────────────────────────────────────────

def geomagnetic_magnon_phonon_coupling():
    """
    Can geomagnetic field variations drive measurable phonon excitation
    in magnetic geological formations?

    Sources of geomagnetic variation:
    1. Diurnal variation:     ~50 nT, period 24h
    2. Geomagnetic storms:    ~100-1000 nT, hours
    3. Pc1 pulsations:        ~1 nT, 0.2-5 Hz
    4. Schumann resonances:   ~1 pT, 7.83 Hz fundamental
    5. Solar wind pressure:   ~10 nT, minutes

    Each of these is a FORCING FUNCTION on the magnon system.
    This is testable.
    """
    sources = [
        {"name": "Diurnal variation", "delta_B_T": 50e-9,
         "period_s": 86400, "f_Hz": 1/86400,
         "mechanism": "solar heating of ionosphere -> Sq current"},
        {"name": "Geomagnetic storm (Dst)", "delta_B_T": 500e-9,
         "period_s": 3600, "f_Hz": 1/3600,
         "mechanism": "ring current intensification"},
        {"name": "Pc1 pulsation", "delta_B_T": 1e-9,
         "period_s": 1.0, "f_Hz": 1.0,
         "mechanism": "EMIC waves from magnetosphere"},
        {"name": "Schumann resonance", "delta_B_T": 1e-12,
         "period_s": 1/7.83, "f_Hz": 7.83,
         "mechanism": "Earth-ionosphere cavity EM mode"},
        {"name": "Pc3-4 pulsation", "delta_B_T": 5e-9,
         "period_s": 0.1, "f_Hz": 10.0,
         "mechanism": "upstream solar wind waves"},
        {"name": "Solar wind shock", "delta_B_T": 100e-9,
         "period_s": 60, "f_Hz": 1/60,
         "mechanism": "CME/CIR impact on magnetopause"},
    ]

    results = []

    for src in sources:
        delta_omega_magnon = GAMMA * MU_0 * src["delta_B_T"]
        delta_f_magnon = delta_omega_magnon / (2 * np.pi)

        E_injected = HBAR * delta_omega_magnon
        N_sites = 1e8
        E_total_per_cycle = N_sites * E_injected

        results.append({
            "source": src["name"],
            "delta_B_T": src["delta_B_T"],
            "f_source_Hz": src["f_Hz"],
            "mechanism": src["mechanism"],
            "delta_f_magnon_Hz": delta_f_magnon,
            "E_per_magnon_J": E_injected,
            "E_total_per_cycle_J": E_total_per_cycle,
        })

    return results


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 85)
    print("PART 1: CONFINED CRYSTAL -- mm-SCALE QUARTZ + Fe DEFECTS")
    print("=" * 85)

    confined = confined_coupling()

    print(f"\n  Crystal: 5mm x 100um AT-cut quartz, 100 ppm Fe3+")
    print(f"  V_crystal: {confined[0]['V_crystal_m3']:.4e} m^3")

    for r in confined[:3]:
        print(f"  mode {r['mode_n']}: f={r['f_phonon_Hz']:.4e} Hz  "
              f"g_mb={r['g_mb_Hz']:.4e} Hz  C={r['cooperativity']:.4e}")

    print("\n" + "=" * 85)
    print("PART 2: GEOLOGICAL FORMATIONS")
    print("=" * 85)

    for key in GEOLOGICAL_PRESETS:
        geo = geological_magnomechanical(key)
        print(f"\n  {geo['name']}  V={geo['V_formation_m3']:.2e} m^3  "
              f"magnonic_crystal={geo['magnonic_crystal']}")

    print("\n" + "=" * 85)
    print("PART 3: GEOMAGNETIC FORCING")
    print("=" * 85)

    geo_forcing = geomagnetic_magnon_phonon_coupling()
    for gf in geo_forcing:
        print(f"  {gf['source']:>25s}  dB={gf['delta_B_T']:.4e} T  "
              f"df_magnon={gf['delta_f_magnon_Hz']:.4e} Hz")

    print("\n" + "=" * 85)
    print("DONE")
    print("=" * 85)
