# banded_crystal_computer.py

# earth-systems-physics

# CC0 — No Rights Reserved

# 

# THERMOPYLAE INTELLIGENCE APPLIED TO CRYSTAL DESIGN

# 

# Thermopylae principle: don't design top-down.

# Define constraints. Let the physics find the structure.

# 

# Constraints:

# 1. Energy: minimize per-operation dissipation

# 2. Materials: achievable with commodity + natural minerals

# 3. Temperature: operates in cold climate (220-280K)

# 4. Robustness: graceful degradation, no cliff failures

# 5. Self-assembly: structure should be growable/stackable

# 6. Storage: persistent without power

# 7. Compute: reconfigurable without fabrication

# 8. I/O: no external transducer needed (piezo = built-in)

# 

# The physics picks the architecture:

# Band structure = logic (pass/block = 1/0)

# Magnetization state = storage (remanent = non-volatile)

# Piezoelectric surfaces = I/O (voltage = read/write)

# Temperature = mode selector (phase transitions = switching)

# Magnetic field = programming (tunes band gaps)

# 

# This is not a von Neumann machine.

# It's a constraint-propagation engine made of rock.

import numpy as np

HBAR = 1.0545718e-34
K_B  = 1.380649e-23
MU_0 = 4 * np.pi * 1e-7
GAMMA = 1.7608597e11

# ─────────────────────────────────────────────

# LAYER TYPES — the building blocks

# ─────────────────────────────────────────────

LAYER_TYPES = {
    "quartz": {
    "role": "PHONON WAVEGUIDE + PIEZO I/O",
    "c_sound": 5720,           # m/s longitudinal
    "c_shear": 3764,           # m/s shear (AT-cut)
    "rho": 2650,               # kg/m³
    "Q_mech_300K": 1e6,
    "Q_mech_250K": 1.5e6,
    "Q_mech_77K": 1e7,
    "piezo": True,
    "d_26": 3.1e-12,           # C/N
    "magnetic": False,
    "epsilon_r": 4.5,
    "notes": "The waveguide. Carries phonons with minimal loss. "
    "Piezo surfaces are natural I/O ports.",
    },
    "magnetite": {
    "role": "MAGNONIC LAYER + STORAGE",
    "c_sound": 7200,
    "rho": 5200,
    "Q_mech_300K": 5000,
    "Q_mech_250K": 6000,
    "Q_mech_77K": 20000,
    "piezo": False,
    "magnetic": True,
    "M_s": 4.8e5,              # A/m
    "H_c": 500,                # A/m coercivity (soft)
    "eta_spc": 3.0,            # cm⁻¹ spin-phonon coupling
    "T_Curie": 858,            # K
    "storage": True,           # remanent magnetization = memory
    "notes": "The compute/storage layer. Band gap is tunable by "
    "magnetization state. Same spinel as YIG.",
    },
    "hematite": {
    "role": "PHASE-TRANSITION SWITCH",
    "c_sound": 6500,
    "rho": 5300,
    "Q_mech_300K": 2000,
    "Q_mech_250K": 2500,
    "Q_mech_77K": 10000,
    "piezo": False,
    "magnetic": True,
    "M_s": 2100,               # A/m (canted AFM)
    "M_s_below_morin": 10,     # A/m (pure AFM)
    "T_Morin": 263,            # K (-10°C)
    "eta_spc": 1.5,
    "storage": True,           # state depends on temperature history
    "notes": "Binary switch at -10°C. Above: spin-phonon active. "
    "Below: different coupling. Temperature = clock.",
    },
    "iron_metal": {
    "role": "HIGH-M COUPLING LAYER",
    "c_sound": 5120,
    "rho": 7874,
    "Q_mech_300K": 1000,
    "Q_mech_250K": 1200,
    "Q_mech_77K": 5000,
    "piezo": False,
    "magnetic": True,
    "M_s": 1.71e6,             # A/m — highest of common materials
    "H_c": 80,                 # A/m (pure Fe, very soft)
    "eta_spc": 2.0,
    "storage": True,
    "notes": "Strongest magnetization. Thin film between quartz layers "
    "creates maximum magnon-phonon coupling contrast.",
    },
    "air_gap": {
    "role": "ACOUSTIC MIRROR / ISOLATION",
    "c_sound": 343,
    "rho": 1.225,
    "Q_mech_300K": 0,          # no resonance
    "piezo": False,
    "magnetic": False,
    "notes": "Massive acoustic impedance mismatch with any solid. "
    "Acts as perfect phonon mirror. Creates cavity.",
    },
}

# ─────────────────────────────────────────────

# BAND STRUCTURE COMPUTATION

# ─────────────────────────────────────────────

def acoustic_impedance(rho, c_sound):
    """Z = ρc. Impedance mismatch drives reflection."""
    return rho * c_sound

def reflection_coefficient(Z1, Z2):
    """Amplitude reflection at interface. R = (Z2-Z1)/(Z2+Z1)."""
    return (Z2 - Z1) / (Z2 + Z1)

def transmission_coefficient(Z1, Z2):
    """Amplitude transmission at interface. T = 2Z2/(Z1+Z2)."""
    return 2 * Z2 / (Z1 + Z2)

def transfer_matrix_layer(thickness_m, c_sound, rho, freq_Hz, loss_Q=np.inf):
    """
    Transfer matrix for a single layer.
    Phonon propagation through a uniform layer.

    [p_out]   [cos(kd)       i Z sin(kd)] [p_in]
    [v_out] = [i sin(kd)/Z   cos(kd)     ] [v_in]
    """
    omega = 2 * np.pi * freq_Hz
    k = omega / c_sound

    # Add loss
    if loss_Q < np.inf and loss_Q > 0:
        k = k * (1 + 1j / (2 * loss_Q))

    Z = rho * c_sound
    kd = k * thickness_m

    M = np.array([
        [np.cos(kd), 1j * Z * np.sin(kd)],
        [1j * np.sin(kd) / Z, np.cos(kd)],
    ], dtype=complex)

    return M

def stack_transmission(layers, freq_array_Hz, T_K=300):
    """
    Compute phonon transmission through a layered stack.

    layers: list of (layer_type_key, thickness_m) tuples
    freq_array_Hz: array of frequencies to compute
    T_K: temperature (affects Q)

    Returns: transmission amplitude vs frequency
    """
    # Get Q at temperature
    Q_key = "Q_mech_300K"
    if T_K < 200:
        Q_key = "Q_mech_77K"
    elif T_K < 270:
        Q_key = "Q_mech_250K"

    transmissions = []

    for f in freq_array_Hz:
        M_total = np.eye(2, dtype=complex)
    
        for layer_key, thickness in layers:
            lt = LAYER_TYPES[layer_key]
            Q = lt.get(Q_key, lt.get("Q_mech_300K", 1000))
        
            M = transfer_matrix_layer(
                thickness, lt["c_sound"], lt["rho"], f, Q
            )
            M_total = M_total @ M
    
        # Transmission coefficient: T = 1/M[0,0] (simplified)
        T_amp = 1.0 / M_total[0, 0]
        transmissions.append(abs(T_amp)**2)

    return np.array(transmissions)

# ─────────────────────────────────────────────

# DEVICE ARCHITECTURES

# ─────────────────────────────────────────────

def architecture_basic_magnonic_crystal():
    """
    BASIC: Alternating quartz/magnetite layers.

    This is the BIF pattern — nature already built this.
    We're just doing it at controlled dimensions.

    Bragg reflection creates band gaps.
    Magnetite magnetization state tunes the gap.
    Quartz piezo surfaces read/write phonons.
    """
    # 10 periods of quartz/magnetite
    d_quartz = 100e-6      # 100 μm quartz
    d_magnetite = 50e-6    # 50 μm magnetite

    layers = []
    for i in range(10):
        layers.append(("quartz", d_quartz))
        layers.append(("magnetite", d_magnetite))
    layers.append(("quartz", d_quartz))  # cap layer

    # Bragg frequency
    d_period = d_quartz + d_magnetite
    c_avg = (5720 * d_quartz + 7200 * d_magnetite) / d_period
    f_bragg = c_avg / (2 * d_period)

    return {
        "name": "Basic Magnonic Crystal (BIF-inspired)",
        "layers": layers,
        "n_periods": 10,
        "d_period_m": d_period,
        "f_bragg_Hz": f_bragg,
        "total_thickness_m": sum(t for _, t in layers),
        "compute": "Band gap presence/absence = logic state",
        "storage": "Magnetite remanent magnetization = non-volatile bit",
        "io": "Piezo voltage at quartz cap layers",
        "tune": "External H field or write current pulse",
        "bits": 10,  # one per magnetite layer
    }

def architecture_morin_switched():
    """
    MORIN-SWITCHED: Quartz/hematite layers with temperature gating.

    Above -10°C: hematite is canted AFM, spin-phonon coupling ON
    Below -10°C: hematite is pure AFM, coupling character CHANGES

    Temperature crossing = mode switch.
    In the corridor, this happens naturally every autumn/spring.
    The device has two operating modes selected by weather.
    """
    d_quartz = 100e-6
    d_hematite = 30e-6

    layers = []
    for i in range(15):
        layers.append(("quartz", d_quartz))
        layers.append(("hematite", d_hematite))
    layers.append(("quartz", d_quartz))

    d_period = d_quartz + d_hematite
    c_avg = (5720 * d_quartz + 6500 * d_hematite) / d_period
    f_bragg = c_avg / (2 * d_period)

    return {
        "name": "Morin-Switched Crystal (temperature-gated)",
        "layers": layers,
        "n_periods": 15,
        "d_period_m": d_period,
        "f_bragg_Hz": f_bragg,
        "total_thickness_m": sum(t for _, t in layers),
        "compute": "Temperature selects operating mode",
        "storage": "Hematite magnetic state + thermal hysteresis",
        "io": "Piezo at quartz surfaces",
        "tune": "Temperature (natural) + H field (coil)",
        "T_switch_K": 263,
        "notes": "Two stable modes. Transition at -10°C. "
                 "Natural clock in cold climate.",
    }

def architecture_hybrid_compute():
    """
    HYBRID: Multiple magnetic materials at different thicknesses.

    Different layers create DIFFERENT band gaps.
    The frequency spectrum becomes the address space.
    Each frequency band maps to a specific layer's state.

    Multiple bits read simultaneously by frequency-domain multiplexing.
    """
    layers = [
        ("quartz", 200e-6),       # thick I/O layer
        ("magnetite", 50e-6),     # band gap 1
        ("quartz", 100e-6),       # spacer
        ("hematite", 30e-6),      # band gap 2 (temp-switched)
        ("quartz", 80e-6),        # spacer
        ("iron_metal", 10e-6),    # band gap 3 (highest coupling)
        ("quartz", 120e-6),       # spacer
        ("magnetite", 80e-6),     # band gap 4 (different freq from #1)
        ("quartz", 60e-6),        # spacer
        ("hematite", 50e-6),      # band gap 5
        ("quartz", 200e-6),       # thick I/O layer
    ]

    return {
        "name": "Hybrid Frequency-Multiplexed Computer",
        "layers": layers,
        "total_thickness_m": sum(t for _, t in layers),
        "compute": "Each magnetic layer = one band gap = one bit. "
                   "Broadband phonon pulse reads ALL bits simultaneously.",
        "storage": "5 independent magnetic layers = 5 bits = 32 states",
        "io": "Broadband piezo pulse in, frequency spectrum out",
        "tune": "Independent H field per layer (or single sweep)",
        "bits": 5,
        "states": 32,
        "notes": "Frequency-domain multiplexing. No sequential addressing. "
                 "All bits read in one pulse. Massively parallel for small N.",
    }

# ─────────────────────────────────────────────

# THERMOPYLAE CONSTRAINT EVALUATION

# ─────────────────────────────────────────────

def thermopylae_evaluate(architecture):
    """
    Evaluate an architecture against Thermopylae constraints.

    Thermopylae optimization: minimize total energy cost
    subject to constraints, let physics pick the details.
    """
    layers = architecture["layers"]
    total_t = architecture["total_thickness_m"]

    # ── Energy per operation ──
    # A phonon pulse traversing the stack
    # Energy = ℏω per phonon, need ~10³ phonons for SNR
    f_op = architecture.get("f_bragg_Hz", 20e6)
    E_phonon = HBAR * 2 * np.pi * f_op
    n_phonons_needed = 1000
    E_per_read = E_phonon * n_phonons_needed

    # Piezo drive energy for those phonons
    # E_drive = E_per_read / k² (electromechanical coupling)
    k_sq = 0.0081
    E_drive = E_per_read / k_sq

    # ── Storage energy ──
    # Writing a bit = flipping magnetization in one layer
    # E_write ~ μ₀ M_s H_c V_layer
    # Approximate for magnetite layer
    mag_layers = [(k, t) for k, t in layers if LAYER_TYPES[k].get("magnetic")]
    if mag_layers:
        key, t = mag_layers[0]
        lt = LAYER_TYPES[key]
        r = 4e-3  # 4mm radius
        V = np.pi * r**2 * t
        E_write = MU_0 * lt.get("M_s", 1e5) * lt.get("H_c", 500) * V
    else:
        E_write = 0

    # ── Dissipation ──
    # Energy lost per traversal = E_read / Q_effective
    Q_eff = min(LAYER_TYPES[k].get("Q_mech_250K", 1000) for k, t in layers)
    E_dissipated = E_per_read / Q_eff

    # ── Comparison to CMOS ──
    E_cmos = 10e-15  # 10 fJ per operation
    ratio_vs_cmos = E_drive / E_cmos

    # ── Robustness ──
    failure_modes = []
    has_piezo = any(LAYER_TYPES[k].get("piezo") for k, _ in layers)
    has_magnetic = any(LAYER_TYPES[k].get("magnetic") for k, _ in layers)
    has_morin = any(k == "hematite" for k, _ in layers)

    if not has_piezo:
        failure_modes.append("No I/O — needs external transducer")
    if not has_magnetic:
        failure_modes.append("No storage — volatile only")

    # ── Materials assessment ──
    materials_needed = set(k for k, _ in layers)
    commodity = {
        "quartz": "Commodity. Watch crystals, mineral dealers, synthetic.",
        "magnetite": "Natural mineral. Fe₃O₄ powder or sintered.",
        "hematite": "Natural mineral. Fe₂O₃. Red ochre = ground hematite.",
        "iron_metal": "Hardware store. Steel shim stock, iron filings.",
        "air_gap": "Free.",
    }

    # ── Self-assembly potential ──
    # Can this be grown/deposited rather than machined?
    # Sputtering: yes (all materials can be sputtered)
    # Sintering: yes (press powder layers, fire)
    # Natural: BIF does this (geological timescale)
    # Electrodeposition: Fe layers yes, oxides tricky

    return {
        "architecture": architecture["name"],
        "bits": architecture.get("bits", 0),
        "total_thickness_mm": total_t * 1e3,
        "f_operating_Hz": f_op,
        "E_per_read_J": E_per_read,
        "E_drive_J": E_drive,
        "E_write_J": E_write,
        "E_dissipated_J": E_dissipated,
        "Q_effective": Q_eff,
        "ratio_vs_CMOS": ratio_vs_cmos,
        "has_piezo_io": has_piezo,
        "has_nonvolatile": has_magnetic,
        "has_temp_switch": has_morin,
        "failure_modes": failure_modes if failure_modes else ["NONE — graceful"],
        "materials": {k: commodity.get(k, "unknown") for k in materials_needed},
        "fabrication_options": [
            "Thin film sputtering (most precise, needs vacuum)",
            "Powder sintering (press + fire, no vacuum needed)",
            "Mechanical stacking (shim stock + cut crystal, hand-assembled)",
            "Natural (find a BIF outcrop, it's already built)",
        ],
    }

# ─────────────────────────────────────────────

# MAIN

# ─────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 85)
    print("BANDED CRYSTAL COMPUTE/STORAGE DEVICE")
    print("Thermopylae-constrained design")
    print("=" * 85)

    # ── Build architectures ──
    archs = [
        architecture_basic_magnonic_crystal(),
        architecture_morin_switched(),
        architecture_hybrid_compute(),
    ]

    for arch in archs:
        print(f"\n{'─'*85}")
        print(f"  {arch['name']}")
        print(f"{'─'*85}")
        print(f"  Total thickness:  {arch['total_thickness_m']*1e3:.2f} mm")
        print(f"  Bragg freq:       {arch.get('f_bragg_Hz', 0):.4e} Hz")
        print(f"  Compute:          {arch['compute']}")
        print(f"  Storage:          {arch['storage']}")
        print(f"  I/O:              {arch['io']}")
        print(f"  Bits:             {arch.get('bits', '?')}")

        # Evaluate
        ev = thermopylae_evaluate(arch)
        print(f"\n  THERMOPYLAE EVALUATION:")
        print(f"    E per read:     {ev['E_per_read_J']:.4e} J")
        print(f"    E drive (piezo):{ev['E_drive_J']:.4e} J")
        print(f"    E write (mag):  {ev['E_write_J']:.4e} J")
        print(f"    E dissipated:   {ev['E_dissipated_J']:.4e} J")
        print(f"    Q effective:    {ev['Q_effective']:.0f}")
        print(f"    vs CMOS:        {ev['ratio_vs_CMOS']:.4e} ×")
        print(f"    Piezo I/O:      {ev['has_piezo_io']}")
        print(f"    Non-volatile:   {ev['has_nonvolatile']}")
        print(f"    Temp switch:    {ev['has_temp_switch']}")
        print(f"    Failure modes:  {ev['failure_modes']}")

    # ── Transmission spectra ──
    print(f"\n{'='*85}")
    print("PHONON TRANSMISSION SPECTRA")
    print(f"{'='*85}")

    arch = archs[0]  # basic magnonic crystal
    f_bragg = arch["f_bragg_Hz"]
    freqs = np.linspace(f_bragg * 0.5, f_bragg * 1.5, 200)

    T_list = [300, 263, 233, 77]
    print(f"\n  Basic magnonic crystal — transmission at Bragg freq region")
    print(f"  f_Bragg = {f_bragg:.4e} Hz")

    for T in T_list:
        trans = stack_transmission(arch["layers"], freqs, T_K=T)
        # Find band gap depth
        gap_idx = np.argmin(trans)
        gap_depth = trans[gap_idx]
        gap_freq = freqs[gap_idx]
        passband = np.max(trans)
        contrast_dB = 10 * np.log10(passband / max(gap_depth, 1e-30))

        print(f"    T={T:>4d}K: gap depth={gap_depth:.4e}  "
              f"contrast={contrast_dB:.1f} dB  "
              f"gap freq={gap_freq:.4e} Hz")

    # ── Hybrid architecture spectrum ──
    arch_h = archs[2]
    freqs_wide = np.linspace(1e6, 100e6, 500)
    trans_h = stack_transmission(arch_h["layers"], freqs_wide, T_K=250)

    # Find all dips (band gaps)
    dips = []
    for i in range(1, len(trans_h)-1):
        if trans_h[i] < trans_h[i-1] and trans_h[i] < trans_h[i+1]:
            if trans_h[i] < 0.5 * np.median(trans_h):
                dips.append((freqs_wide[i], trans_h[i]))

    print(f"\n  Hybrid architecture — band gaps found at 250K:")
    for f, t in dips[:10]:
        print(f"    f = {f:.4e} Hz  transmission = {t:.4e}")

    # ── Fabrication paths ──
    print(f"\n{'='*85}")
    print("FABRICATION PATHS — from simple to optimized")
    print(f"{'='*85}")
    print("""

    PATH A: HAND-STACKED (weekend project)
    Materials:
    - Quartz: buy AT-cut blanks ($1-5 each) or cut smoky quartz
    - Magnetite: grind natural magnetite, sinter at 1200°C
    OR: buy Fe₃O₄ powder, press into discs
    - Iron: hardware store steel shim stock (0.001" = 25μm)

    Assembly:
    - Stack layers with thin epoxy or mechanical clamping
    - Wire electrodes to quartz surfaces (silver paint + wire)
    - Oscillator circuit on breadboard

    Limitations:
    - Poor thickness control → broad band gaps
    - Epoxy introduces acoustic loss
    - Manual alignment

    Cost: $20-50

    PATH B: POWDER SINTERING (garage fabrication)
    Materials:
    - Quartz powder (ground crystal) + Fe₃O₄ powder
    - Die/press (can be steel tubing + hydraulic jack)

    Process:
    1. Layer powders in die: quartz → magnetite → quartz → ...
    2. Press at ~100 MPa (hydraulic jack handles this)
    3. Sinter at 1000-1200°C (pottery kiln)
    4. Polish faces, apply electrodes

    Advantages:
    - Good layer adhesion (sintered interface)
    - Scalable to many layers
    - Thickness controlled by powder weight

    Limitations:
    - Quartz transforms to cristobalite above 1470°C
    - Magnetite can reduce to Fe above 1400°C
    - Temperature control is critical

    Cost: $50-200 (plus kiln access)

    PATH C: THIN FILM (university/makerspace with sputtering)
    Materials:
    - SiO₂ target, Fe₃O₄ target, Fe target
    - Substrate: polished quartz disc

    Process:
    - Magnetron sputtering, alternating targets
    - ~1 μm layers (not 100 μm — different freq range)
    - f_Bragg moves to GHz range

    Advantages:
    - Precise thickness control (nm level)
    - Clean interfaces
    - Standard thin film equipment

    Limitations:
    - Needs vacuum equipment
    - GHz range means different oscillator circuit

    Cost: $100-500 (with equipment access)

    PATH D: NATURAL (zero fabrication)
    Go to the Iron Range.
    Find a BIF outcrop with 1-5 cm banding.
    It's already built. 2 billion years ago.
    Bring a seismometer and a magnetometer.
    The outcrop IS the computer.

    Cost: gas money

    """)

    print(f"{'='*85}")
    print("THE THERMOPYLAE INSIGHT")
    print(f"{'='*85}")
    print("""

    The Thermopylae architecture self-assembled from orbital debris
    using constraint propagation, not design blueprints.

    Apply the same principle to the crystal computer:

    Don't DESIGN the layer thicknesses.
    GROW them.

    Hydrothermal growth of quartz with periodic Fe injection:

    1. Start growing quartz crystal from seed
    1. Periodically add FeCl₃ to the growth solution
    1. Fe incorporates into the growing crystal
    1. Remove FeCl₃, pure growth continues
    1. Repeat

    The crystal self-assembles with banded Fe content.
    The periodicity is set by the injection timing.
    The thickness is set by the growth rate.
    No machining. No stacking. No epoxy.

    One crystal. Banded internally.
    Piezoelectric everywhere (it's all quartz).
    Magnetic bands tunable by external field.
    Band structure set by growth timing.

    This is the slime mold path:
    Don't build the structure. GROW it.
    Let the physics do the fabrication.
    """)
    print("=" * 85)
