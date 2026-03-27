# layer_0b_magnomechanical.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Magnomechanical coupling sub-layer of Layer 0 (Electromagnetics).
# Spin-phonon coupling in iron-bearing crustal minerals.
#
# Sits between Layer 0 (EM fields) and Layer 5 (Lithosphere).
# Provides the coupling mechanism between geomagnetic field
# variations and acoustic/seismic responses in magnetic crust.
#
# Coupling is bidirectional:
#   EM -> Acoustic: geomagnetic storm -> spin perturbation -> acoustic emission
#   Acoustic -> EM: seismic wave -> lattice perturbation -> piezomagnetic signal

import numpy as np

from magnonic_sublayer import (
    magnonic_coupling_state,
    dispersion_relation,
    group_velocity,
    propagation_length,
    magnon_phonon_coupling_strength,
    MATERIALS as MAGNONIC_MATERIALS,
    MU_0, GAMMA, HBAR, K_B, E_CHARGE, M_E, EPSILON_0,
)


# ─────────────────────────────────────────────
# CRUSTAL MINERALS DATABASE
# ─────────────────────────────────────────────

CRUSTAL_MINERALS = {
    "magnetite": {
        "name": "Magnetite (Fe3O4)",
        "M_s": 4.8e5,           # saturation magnetization A/m
        "A_ex": 1.2e-11,        # exchange stiffness J/m
        "alpha": 0.05,          # Gilbert damping
        "conductivity": 2e4,    # S/m
        "c_sound": 5500.0,      # m/s
        "rho": 5200.0,          # kg/m3
        "B_me": 6.96e6,         # magnetoelastic coupling J/m3 (single crystal)
        "piezoelectric": False,
        "d_piezo": 0.0,         # C/N
        "morin_T_K": 0,         # no Morin transition
        "desc": "Primary crustal magnetic mineral. Strongest spin-phonon coupling.",
    },
    "hematite": {
        "name": "Hematite (Fe2O3)",
        "M_s": 2.1e3,           # weak — canted antiferromagnet above Morin
        "A_ex": 1e-13,          # weak exchange
        "alpha": 0.01,          # low damping below Morin
        "conductivity": 1e-2,   # poor conductor
        "c_sound": 6000.0,      # m/s
        "rho": 5300.0,          # kg/m3
        "B_me": 1e5,            # moderate magnetoelastic
        "piezoelectric": False,
        "d_piezo": 0.0,
        "morin_T_K": 263.0,     # -10C Morin transition
        "desc": "Morin transition at -10C changes spin-phonon coupling character.",
    },
    "quartz_fe_defect": {
        "name": "Fe-doped quartz (SiO2:Fe3+)",
        "M_s": 1e3,             # very weak — substitutional Fe
        "A_ex": 1e-14,          # negligible exchange
        "alpha": 0.1,           # high damping — dilute
        "conductivity": 1e-18,  # insulator
        "c_sound": 5720.0,      # m/s
        "rho": 2650.0,          # kg/m3
        "B_me": 5e4,            # crystalline, higher than powder
        "piezoelectric": True,
        "d_piezo": 3.1e-12,     # C/N — AT-cut quartz
        "morin_T_K": 0,
        "desc": "Piezoelectric + magnetic. Direct voltage readout of spin-phonon coupling.",
    },
    "pyrrhotite": {
        "name": "Pyrrhotite (Fe7S8)",
        "M_s": 8e4,             # ferrimagnetic
        "A_ex": 5e-12,
        "alpha": 0.08,
        "conductivity": 1e4,
        "c_sound": 4500.0,
        "rho": 4600.0,
        "B_me": 2e6,
        "piezoelectric": False,
        "d_piezo": 0.0,
        "morin_T_K": 0,
        "desc": "Common sulfide mineral. Moderate coupling. Found in ore deposits.",
    },
    "ilmenite": {
        "name": "Ilmenite (FeTiO3)",
        "M_s": 1e4,             # weak — antiferromagnetic with canting
        "A_ex": 1e-13,
        "alpha": 0.05,
        "conductivity": 10.0,
        "c_sound": 5800.0,
        "rho": 4700.0,
        "B_me": 5e5,
        "piezoelectric": False,
        "d_piezo": 0.0,
        "morin_T_K": 0,
        "desc": "Ti-bearing iron oxide. Common in mafic rocks and lunar regolith.",
    },
}


# ─────────────────────────────────────────────
# GEOMAGNETIC SIGNAL TYPES
# ─────────────────────────────────────────────

GEOMAGNETIC_SIGNALS = {
    "geomagnetic_storm_Dst": {
        "name": "Geomagnetic storm (Dst index)",
        "delta_B_T": 3e-7,     # ~300 nT Dst perturbation
        "freq_Hz": 1e-4,       # period ~hours
        "duration_s": 3600 * 24,
        "desc": "Ring current enhancement during storm. Global field depression.",
    },
    "substorm_Pi2": {
        "name": "Substorm Pi2 pulsation",
        "delta_B_T": 1e-8,     # ~10 nT
        "freq_Hz": 0.01,       # 10-100s period
        "duration_s": 600,
        "desc": "Impulsive field-aligned current onset. Sharp magnetic impulse.",
    },
    "Pc1_pulsation": {
        "name": "Pc1 micropulsation",
        "delta_B_T": 1e-9,     # ~1 nT
        "freq_Hz": 1.0,        # 0.2-5 Hz
        "duration_s": 3600,
        "desc": "EMIC waves. Propagate as guided modes. Most relevant for spin coupling.",
    },
    "Pc3_pulsation": {
        "name": "Pc3 pulsation",
        "delta_B_T": 5e-9,     # ~5 nT
        "freq_Hz": 0.03,       # 10-45s period
        "duration_s": 3600,
        "desc": "Upstream wave source. Continuous during daytime.",
    },
    "sudden_commencement": {
        "name": "Storm sudden commencement (SSC)",
        "delta_B_T": 5e-8,     # ~50 nT
        "freq_Hz": 0.001,      # sharp onset, ~minutes
        "duration_s": 60,
        "desc": "Interplanetary shock arrival. Sharp field increase.",
    },
    "diurnal_variation": {
        "name": "Diurnal Sq variation",
        "delta_B_T": 3e-8,     # ~30 nT
        "freq_Hz": 1.16e-5,    # 24-hour period
        "duration_s": 86400,
        "desc": "Solar quiet daily variation. Ionospheric current system.",
    },
    "secular_variation": {
        "name": "Secular variation",
        "delta_B_T": 1e-6,     # ~1 uT/year
        "freq_Hz": 3.17e-8,    # ~1 year period
        "duration_s": 3.15e7,
        "desc": "Core field change. Slowest but largest cumulative.",
    },
    "schumann_resonance": {
        "name": "Schumann resonance",
        "delta_B_T": 1e-12,    # ~1 pT
        "freq_Hz": 7.83,       # fundamental mode
        "duration_s": 1e6,     # continuous
        "desc": "ELF resonance in Earth-ionosphere cavity. Extremely weak.",
    },
    "lightning_sferic": {
        "name": "Lightning sferic",
        "delta_B_T": 1e-10,    # ~100 pT at distance
        "freq_Hz": 1e4,        # broadband, peak ~10 kHz
        "duration_s": 1e-3,
        "desc": "Electromagnetic pulse from lightning. Broadband, impulsive.",
    },
}


# ─────────────────────────────────────────────
# CORE COUPLING PHYSICS
# ─────────────────────────────────────────────

def spin_phonon_coupling_hz(M_s, B_me, rho, c_sound, grain_volume_m3, omega):
    """
    Spin-phonon coupling strength for a magnetic grain.

    g = (B_me / M_s) * x_zpf * omega
    where x_zpf = sqrt(hbar / (2 * rho * V * omega))

    M_s            : saturation magnetization (A/m)
    B_me           : magnetoelastic coupling (J/m3)
    rho            : density (kg/m3)
    c_sound        : speed of sound (m/s)
    grain_volume_m3: grain volume (m3)
    omega          : angular frequency (rad/s)

    returns: coupling strength (Hz)
    """
    if omega <= 0 or M_s <= 0 or grain_volume_m3 <= 0:
        return 0.0
    x_zpf = np.sqrt(HBAR / (2 * rho * grain_volume_m3 * omega))
    g = (B_me / M_s) * x_zpf * omega
    return abs(g) / (2 * np.pi)


def collective_coupling(g_single_hz, n_spins):
    """
    Collective spin-phonon coupling: g_collective = g_single * sqrt(N)

    n_spins: number of participating spin sites
    returns: collective coupling (Hz)
    """
    return g_single_hz * np.sqrt(max(n_spins, 0))


def acoustic_velocity_from_coupling(delta_B_T, M_s, B_me, rho, c_sound):
    """
    Acoustic velocity produced by magnetostrictive response to field change.

    v_acoustic = (B_me / M_s) * (delta_B / (mu_0 * M_s)) * c_sound / rho^0.5

    Simplified model: field change -> magnetostriction -> acoustic emission.

    returns: particle velocity (m/s)
    """
    if M_s <= 0 or rho <= 0:
        return 0.0
    strain = (B_me / (M_s * MU_0)) * (delta_B_T / max(M_s, 1))
    v = strain * c_sound
    return abs(v)


def detection_range_m(v_acoustic, rho, c_sound, rock_volume_m3,
                      noise_floor_m_s=1e-9):
    """
    Distance at which acoustic emission is detectable above noise floor.
    Assumes geometric spreading (1/r) and threshold velocity.

    noise_floor_m_s: seismometer threshold (default 1 nm/s)
    returns: detection range (m)
    """
    if v_acoustic <= 0 or v_acoustic <= noise_floor_m_s:
        return 0.0
    # Source amplitude scales with sqrt(volume) for coherent emission
    source_strength = v_acoustic * np.sqrt(rock_volume_m3)
    # 1/r geometric spreading
    r_detect = source_strength / noise_floor_m_s
    return min(r_detect, 1e6)  # cap at 1000 km


def piezo_voltage(d_piezo, rho, c_sound, omega, x_displacement):
    """
    Piezoelectric voltage from mechanical displacement.

    d_piezo      : piezoelectric coefficient (C/N)
    rho          : density (kg/m3)
    c_sound      : speed of sound (m/s)
    omega        : angular frequency (rad/s)
    x_displacement: displacement amplitude (m)

    returns: voltage (V)
    """
    if d_piezo <= 0:
        return 0.0
    stress = rho * c_sound**2 * omega * x_displacement
    return d_piezo * stress


# ─────────────────────────────────────────────
# COUPLING STATE EXPORT
# ─────────────────────────────────────────────

def coupling_state(
    H_field=5e-5,                    # ambient magnetic field (T) — default Earth's field
    mineral="magnetite",             # which crustal mineral
    grain_size_m=50e-6,              # grain diameter (m)
    rock_volume_m3=1000,             # formation volume (m3)
    mineral_fraction=0.02,           # volume fraction of magnetic mineral
    T=290.0,                         # temperature (K)
    signal_type="geomagnetic_storm_Dst",  # which geomagnetic signal
):
    """
    Magnomechanical coupling state export.

    Computes spin-phonon coupling in crustal minerals driven by
    geomagnetic field variations. Returns state dict for integration
    into the layer stack.

    This is the interface contract — same pattern as
    layer_0_electromagnetics.coupling_state().
    """
    min_data = CRUSTAL_MINERALS.get(mineral, CRUSTAL_MINERALS["magnetite"])
    sig_data = GEOMAGNETIC_SIGNALS.get(signal_type,
                                        GEOMAGNETIC_SIGNALS["geomagnetic_storm_Dst"])

    M_s = min_data["M_s"]
    B_me = min_data["B_me"]
    rho = min_data["rho"]
    c_sound = min_data["c_sound"]
    alpha = min_data["alpha"]
    d_piezo = min_data["d_piezo"]
    morin_T = min_data["morin_T_K"]

    delta_B = sig_data["delta_B_T"]
    sig_freq = sig_data["freq_Hz"]

    # Grain geometry
    grain_radius = grain_size_m / 2
    grain_volume = (4/3) * np.pi * grain_radius**3
    V_magnetic = rock_volume_m3 * mineral_fraction

    # Number of grains
    n_grains = V_magnetic / grain_volume if grain_volume > 0 else 0

    # Number of spin sites per grain (Fe atoms, ~1 per unit cell)
    # Magnetite unit cell: 8 formula units, a = 0.8396 nm
    a_lattice = 8.396e-10  # m
    V_unit_cell = a_lattice**3
    n_spins_per_grain = 8 * grain_volume / V_unit_cell if V_unit_cell > 0 else 0

    # Magnon frequency from ambient field
    magnon_freq_hz = GAMMA * MU_0 * H_field / (2 * np.pi)
    omega_magnon = 2 * np.pi * magnon_freq_hz

    # First phonon standing wave in grain
    phonon_mode_1_hz = c_sound / (2 * grain_size_m) if grain_size_m > 0 else 0
    omega_phonon_1 = 2 * np.pi * phonon_mode_1_hz

    # Single-grain spin-phonon coupling
    g_single = spin_phonon_coupling_hz(M_s, B_me, rho, c_sound,
                                        grain_volume, omega_phonon_1)

    # Collective coupling across all grains
    g_coll = collective_coupling(g_single, n_spins_per_grain * n_grains)

    # Acoustic velocity from magnetostrictive response
    v_acoustic = acoustic_velocity_from_coupling(delta_B, M_s, B_me, rho, c_sound)

    # Seismic detectability (threshold: 1 nm/s)
    seismo_threshold = 1e-9  # m/s
    seismo_detectable = v_acoustic > seismo_threshold

    # Detection range
    det_range = detection_range_m(v_acoustic, rho, c_sound, V_magnetic,
                                   seismo_threshold)

    # Piezoelectric voltage (if mineral supports it)
    x_displacement = v_acoustic / (omega_phonon_1) if omega_phonon_1 > 0 else 0
    v_piezo = piezo_voltage(d_piezo, rho, c_sound, omega_phonon_1, x_displacement)

    # Magnonic crystal check (periodic mineral structure)
    is_magnonic_crystal = mineral_fraction > 0.05 and grain_size_m > 1e-6

    # Morin transition check (hematite below -10C)
    morin_active = morin_T > 0 and T < morin_T

    return {
        # Frequencies
        "magnon_freq_Hz": magnon_freq_hz,
        "phonon_mode_1_Hz": phonon_mode_1_hz,

        # Coupling strengths
        "spin_phonon_coupling_Hz": g_single,
        "g_collective_Hz": g_coll,

        # Acoustic output
        "v_acoustic_m_s": v_acoustic,
        "seismo_detectable": seismo_detectable,
        "detection_range_m": det_range,

        # Piezoelectric readout
        "piezo_voltage_V": v_piezo,

        # Structure
        "magnonic_crystal": is_magnonic_crystal,

        # Temperature effects
        "morin_transition_active": morin_active,

        # Material info
        "mineral": mineral,
        "mineral_name": min_data["name"],
        "signal_type": signal_type,
        "signal_name": sig_data["name"],
        "n_grains": n_grains,
        "V_magnetic_m3": V_magnetic,
        "grain_volume_m3": grain_volume,

        # Layer coupling interfaces
        "coupling_to_layer_0": {
            "needs": "B_surface (ambient field), n_e (for plasma coupling)",
            "provides": "magnon_freq_Hz, spin_phonon_coupling_Hz",
        },
        "coupling_to_layer_5": {
            "needs": "seismic_velocity, crustal_stress",
            "provides": "v_acoustic_m_s, seismo_detectable, detection_range_m",
        },
    }


# ─────────────────────────────────────────────
# DEMO / SELF-TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("MAGNOMECHANICAL SUB-LAYER — MINERAL x SIGNAL SURVEY")
    print("=" * 70)

    # Test all minerals with default signal
    for mineral_key in CRUSTAL_MINERALS:
        state = coupling_state(mineral=mineral_key)
        m = CRUSTAL_MINERALS[mineral_key]
        print(f"\n{'─'*70}")
        print(f"  {m['name']}")
        print(f"  {m['desc']}")
        print(f"{'─'*70}")
        print(f"  magnon_freq:          {state['magnon_freq_Hz']:.4e} Hz")
        print(f"  phonon_mode_1:        {state['phonon_mode_1_Hz']:.4e} Hz")
        print(f"  g_single:             {state['spin_phonon_coupling_Hz']:.4e} Hz")
        print(f"  g_collective:         {state['g_collective_Hz']:.4e} Hz")
        print(f"  v_acoustic:           {state['v_acoustic_m_s']:.4e} m/s")
        print(f"  seismo_detectable:    {state['seismo_detectable']}")
        print(f"  detection_range:      {state['detection_range_m']:.1f} m")
        print(f"  piezo_voltage:        {state['piezo_voltage_V']:.4e} V")
        print(f"  morin_active:         {state['morin_transition_active']}")

    # Test all signal types with magnetite
    print(f"\n\n{'='*70}")
    print("SIGNAL TYPE SURVEY — Magnetite")
    print(f"{'='*70}")
    print(f"  {'Signal':30s}  {'v_acoustic':>12s}  {'detectable':>10s}  {'range_m':>10s}")
    for sig_key in GEOMAGNETIC_SIGNALS:
        state = coupling_state(signal_type=sig_key)
        print(f"  {sig_key:30s}  {state['v_acoustic_m_s']:>12.4e}  "
              f"{'YES' if state['seismo_detectable'] else 'no':>10s}  "
              f"{state['detection_range_m']:>10.1f}")

    print(f"\n{'='*70}")
    print("DONE")
    print(f"{'='*70}")
