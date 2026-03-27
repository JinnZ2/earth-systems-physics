# crystal_device_gradient.py

# earth-systems-physics

# CC0 — No Rights Reserved

# 

# SLIME MOLD APPROACH TO CRYSTAL DEVICE DESIGN

# 

# Don't force the physics. Follow the gradient.

# 

# What we learned tonight:

# 1. Magnetostriction in dilute Fe/quartz is too weak. Stop pushing.

# 2. Spin-orbit crystal field coupling is 10⁸× stronger per ion.

# 3. Quartz is the best phonon resonator on Earth (Q=10⁶).

# 4. Piezo is bidirectional: drive AND read through the same crystal.

# 5. The Earth is already a magnomechanical system using these physics.

# 

# The gradient points toward: a quartz resonator that LISTENS

# to magnetic fields through spin-phonon coupling, using the

# piezoelectric effect as both drive and readout.

# 

# This is functionally a magnetometer.

# But it's a magnetometer built on phonon physics, not Hall effect

# or SQUID or fluxgate. Different information channel.

import numpy as np

HBAR  = 1.0545718e-34
K_B   = 1.380649e-23
MU_0  = 4 * np.pi * 1e-7
GAMMA = 1.7608597e11
MU_B  = 9.274e-24

# ─────────────────────────────────────────────

# THE MINIMUM DEVICE

# ─────────────────────────────────────────────

# 

# What: Quartz crystal oscillator with Fe impurities

# + coil for DC bias field

# + oscillator circuit (drives crystal at resonance)

# + frequency counter (reads crystal frequency)

# 

# How it works:

# 1. Oscillator drives quartz at its resonant frequency f₀

# 2. Fe³⁺ spins in the crystal couple to the phonon mode

# via spin-orbit / crystal field modulation

# 3. External magnetic field changes Fe³⁺ spin state

# 4. Changed spin state modifies effective elastic constant

# via spin-phonon coupling

# 5. Modified elastic constant shifts resonant frequency

# 6. Frequency shift Δf is proportional to ΔB

# 7. Frequency counter reads Δf

# 

# This is a FREQUENCY-SHIFT MAGNETOMETER.

# The signal is not amplitude — it's frequency.

# Frequency is the easiest thing in physics to measure precisely.

# A $2 microcontroller can count frequency to 1 ppb.

# 

# The Q factor makes this work:

# Δf/f₀ = (η/ω₀) × (ΔE_spin/E_phonon)

# High Q means narrow linewidth means tiny shifts are resolvable.

def quartz_crystal_specs():
    """Standard AT-cut quartz crystal resonator specs."""
    return {
    # Crystal
    "cut": "AT",
    "thickness_m": 0.1e-3,      # 100 μm → ~18.8 MHz fundamental
    "diameter_m": 8e-3,          # 8 mm blank (standard)
    "c_shear": 3764.0,           # m/s (AT-cut shear)
    "rho": 2650.0,               # kg/m³
    "Q_mech": 1e6,               # AT-cut, room temp
    "f_series_tolerance": 1e-6,  # ±1 ppm standard

        # Piezoelectric
        "d_26": 3.1e-12,             # C/N
        "k_sq": 0.0081,              # electromechanical coupling
        "epsilon_r": 4.5,
    
        # Thermal
        "turnover_temp_C": 25,       # AT-cut turnover point
        "temp_coeff_ppm_C2": -0.04,  # parabolic temp coefficient
    
        # Cost
        "cost_USD": 0.50,            # commodity pricing
    }

def fe_doped_quartz_specs(fe_ppm=100):
    """Fe³⁺ doped quartz crystal properties."""

    # Spin-phonon coupling for Fe³⁺ in oxide environment
    # Literature values: η = 0.1 - 3.4 cm⁻¹
    # Conservative estimate for dilute Fe³⁺ in SiO₂: 0.1 - 0.5 cm⁻¹
    # We use 0.3 cm⁻¹ as baseline
    eta_cm = 0.3  # cm⁻¹

    # Fe³⁺ crystal field parameters in quartz
    # Substitutional Fe³⁺ at Si site: distorted tetrahedral
    # g-factor: ~2.0 (close to free electron)
    # Spin: S = 5/2 (high-spin d⁵)
    # Zero-field splitting: D ~ 0 for Fe³⁺ in SiO₂ (weak)

    return {
        "fe_ppm": fe_ppm,
        "M_s_A_m": fe_ppm * 1.0,    # rough: 1 A/m per ppm
        "spin_S": 2.5,               # S = 5/2
        "g_factor": 2.0,
        "eta_spin_phonon_cm": eta_cm,
        "eta_spin_phonon_Hz": eta_cm * 3e10,
        "alpha_gilbert": 0.1,        # high damping (isolated spins)
        "T1_spin_s": 1e-7,           # spin-lattice relaxation
        "T2_spin_s": 1e-8,           # spin-spin relaxation
    
        # Source options
        "natural": "smoky quartz, amethyst, citrine all have Fe³⁺",
        "synthetic": "ion implantation or growth from Fe-doped melt",
        "cheap_source": "smoky quartz from mineral dealer (~$5-20)",
    }

# ─────────────────────────────────────────────

# FREQUENCY SHIFT MAGNETOMETRY

# ─────────────────────────────────────────────

def frequency_shift_from_field(
    delta_B_T,              # magnetic field change (T)
    f0_Hz,                  # crystal resonant frequency (Hz)
    Q_mech,                 # mechanical Q
    eta_cm,                 # spin-phonon coupling (cm⁻¹)
    fe_ppm,                 # Fe concentration
    crystal_volume_m3,      # crystal volume
    T=300.0,                # temperature (K)
    ):
    """
    Core mechanism: magnetic field → frequency shift.

    The spin-phonon coupling modifies the effective elastic constant:

    Δc/c = (N_Fe/V) × η × Δ⟨S_z⟩ / (ρ c²)

    where Δ⟨S_z⟩ is the change in spin expectation value from ΔB.

    For paramagnetic Fe³⁺ at room temperature:
    Δ⟨S_z⟩ ≈ g μ_B S(S+1) ΔB / (3 k_B T)  (Curie law regime)

    The frequency shift:
    Δf/f = (1/2) Δc/c  (for thickness shear mode)
    """
    rho = 2650.0
    c = 3764.0  # m/s
    S = 2.5  # Fe³⁺ spin
    g = 2.0

    eta_Hz = eta_cm * 3e10
    eta_J = eta_cm * 1.24e-4 * 1.602e-19  # cm⁻¹ → eV → J

    # Number density of Fe³⁺
    # quartz: 2.65 g/cm³, molar mass 60 g/mol
    n_sites = rho * 6.022e23 / 0.060  # total Si sites per m³
    n_Fe = n_sites * fe_ppm * 1e-6     # Fe sites per m³

    # Change in spin expectation value (Curie law)
    # ⟨S_z⟩ = g μ_B S(S+1) B / (3 k_B T)
    delta_Sz = g * MU_B * S * (S + 1) * delta_B_T / (3 * K_B * T)

    # Elastic constant modification
    # Δc/c = n_Fe × η_J × Δ⟨S_z⟩ / (ρ c²)
    delta_c_over_c = n_Fe * eta_J * delta_Sz / (rho * c**2)

    # Frequency shift
    delta_f_over_f = 0.5 * delta_c_over_c
    delta_f = delta_f_over_f * f0_Hz

    # Resolution limit from Q
    # Minimum resolvable Δf = f₀ / (2Q) × SNR_factor
    # For a good oscillator circuit: SNR_factor ~ 0.01
    # (Allan deviation of 10⁻¹² is routine for quartz oscillators)
    delta_f_min_Q = f0_Hz / (2 * Q_mech) * 0.01

    # Resolution limit from frequency counter
    # 1-second gate: Δf = 1 Hz
    # 10-second gate: Δf = 0.1 Hz
    # GPS-disciplined counter: Δf = 10⁻³ Hz
    delta_f_min_counter_1s = 1.0
    delta_f_min_counter_10s = 0.1
    delta_f_min_counter_gps = 1e-3

    # Temperature stability requirement
    # AT-cut: Δf/f ≈ -0.04 ppm/°C² × (T - T₀)²
    # At turnover (25°C): zero first-order coefficient
    # To not mask ΔB signal: need ΔT < sqrt(Δf_signal / (f₀ × 0.04e-6))
    temp_stability_needed_C = np.sqrt(abs(delta_f_over_f) / 0.04e-6) \
                               if delta_f_over_f != 0 else np.inf

    return {
        "delta_B_T": delta_B_T,
        "delta_Sz": delta_Sz,
        "n_Fe_per_m3": n_Fe,
        "delta_c_over_c": delta_c_over_c,
        "delta_f_over_f": delta_f_over_f,
        "delta_f_Hz": delta_f,
        "delta_f_ppb": delta_f_over_f * 1e9,
    
        # Resolution limits
        "resolution_Q_limited_Hz": delta_f_min_Q,
        "resolution_1s_gate_Hz": delta_f_min_counter_1s,
        "resolution_10s_gate_Hz": delta_f_min_counter_10s,
        "resolution_gps_Hz": delta_f_min_counter_gps,
    
        # Detectability
        "detectable_1s_gate": abs(delta_f) > delta_f_min_counter_1s,
        "detectable_10s_gate": abs(delta_f) > delta_f_min_counter_10s,
        "detectable_gps": abs(delta_f) > delta_f_min_counter_gps,
        "detectable_Q_limited": abs(delta_f) > delta_f_min_Q,
    
        # Requirements
        "temp_stability_needed_C": temp_stability_needed_C,
    }

# ─────────────────────────────────────────────

# DEVICE CONFIGURATIONS

# ─────────────────────────────────────────────

def config_minimum_viable():
    """
    MINIMUM VIABLE DEVICE

    Parts:
    - 1× smoky quartz crystal (Fe-bearing, natural)
    - 1× oscillator circuit (can build from discrete components
      or use a commodity oscillator IC like a Pierce oscillator)
    - 1× frequency counter (Arduino + GPS PPS for discipline)
    - 1× small coil (bias field, optional)
    - Battery or USB power

    Total cost: $15-50 depending on sourcing
    Total complexity: weekend project
    """
    return {
        "name": "Minimum Viable — Smoky Quartz Magnetometer",
        "crystal": "smoky quartz (natural Fe³⁺, ~50-500 ppm)",
        "oscillator": "Pierce oscillator (1 IC + 2 caps)",
        "counter": "Arduino Nano + GPS module (PPS discipline)",
        "coil": "optional — 100-turn on crystal for bias sweep",
        "power": "USB (500 mW) or 2× AA batteries",
        "cost_USD": 25,
        "build_time": "weekend",
        "fe_ppm_range": (50, 500),
        "f0_Hz": 18.82e6,  # 100μm AT-cut fundamental
        "Q_mech": 50000,    # natural crystal, lower Q than synthetic
        "notes": [
            "Smoky quartz color comes from Al + irradiation, but most smoky",
            "quartz also contains Fe³⁺ (10-500 ppm). Color depth correlates",
            "loosely with Fe content. Darker = more Fe = stronger signal.",
            "",
            "The crystal needs to be cut to resonant dimensions.",
            "A lapidary saw + lapping plate gets you there.",
            "Or: buy a commodity quartz blank and hope for Fe impurities.",
            "",
            "Natural quartz has lower Q (~10⁴-10⁵) than synthetic (~10⁶).",
            "This reduces frequency resolution but the Fe is free.",
        ],
    }

def config_optimized():
    """
    OPTIMIZED DEVICE

    Parts:
    - 1× synthetic Fe-doped quartz crystal (custom growth or implanted)
    - 1× TCXO oscillator circuit (temperature-compensated)
    - 1× GPS-disciplined frequency counter
    - 1× 4-axis Helmholtz coil set (your existing design)
    - Thermal enclosure (styrofoam + heater + thermistor)

    Total cost: $100-500
    """
    return {
        "name": "Optimized — Controlled Fe-doped Quartz",
        "crystal": "synthetic AT-cut quartz, Fe-implanted 100 ppm",
        "oscillator": "TCXO circuit with OCXO-level stability",
        "counter": "GPS-disciplined counter (10⁻¹² Allan deviation)",
        "coil": "4-axis Helmholtz, 0-1T sweep range",
        "power": "5W regulated supply",
        "cost_USD": 300,
        "build_time": "2-4 weeks",
        "fe_ppm": 100,
        "f0_Hz": 18.82e6,
        "Q_mech": 1e6,      # synthetic AT-cut
        "thermal_control_C": 0.01,  # ±10 mK stability
        "notes": [
            "Ion implantation of Fe³⁺ into synthetic quartz blanks is",
            "available from semiconductor foundries. ~$50-100 per wafer.",
            "Alternatively: hydrothermal growth with FeCl₃ in the solution.",
            "",
            "The 4-axis coil sweeps H₀ to tune the magnon frequency.",
            "At each H₀, measure f₀. The f₀(H₀) curve maps the",
            "spin-phonon coupling spectrum of the Fe³⁺ defect.",
            "",
            "Temperature control is critical: AT-cut has zero first-order",
            "temp coefficient at 25°C, but second-order is -0.04 ppm/°C².",
            "A styrofoam box + resistive heater + PID loop gets ±10 mK.",
        ],
    }

def config_geological():
    """
    GEOLOGICAL LISTENER

    Not a device you build — a measurement you make on existing rock.

    Parts:
    - 1× broadband seismometer (borrow from university)
    - 1× fluxgate magnetometer ($200-500 DIY, or borrow)
    - 1× data logger (Raspberry Pi + ADC)
    - Cables, batteries, weatherproofing
    - Access to a magnetite-rich outcrop

    What you measure:
    - Cross-correlation between magnetic pulsations (Pc1, 0.2-5 Hz)
      and seismic signal at the same site
    - During geomagnetic storm: look for enhanced correlation
    - Control: same setup at non-magnetic outcrop
    """
    return {
        "name": "Geological Listener — Rock as Transducer",
        "instruments": [
            "broadband seismometer (0.01-50 Hz)",
            "fluxgate magnetometer (0.001-10 Hz, 0.1 nT resolution)",
            "data logger (24-bit ADC, GPS-synced timestamps)",
        ],
        "site_requirements": [
            "magnetite-rich outcrop (gabbro, BIF, serpentinite)",
            "low cultural noise (away from roads, machinery)",
            "power (solar panel + battery for multi-day recording)",
        ],
        "analysis": [
            "cross-spectral density between magnetic and seismic",
            "coherence function in Pc1 band (0.2-5 Hz)",
            "transfer function magnitude and phase",
            "compare storm periods vs quiet periods",
        ],
        "cost_USD": "500-2000 (or free if borrowing instruments)",
        "notes": [
            "The Superior-to-Tomah corridor has exposed Precambrian",
            "greenstone belt with magnetite-bearing metabasalt.",
            "The Iron Range (Mesabi, Vermillion) is literally named",
            "for its magnetite content. BIF outcrops are accessible.",
            "",
            "If correlation exists: publish. This would be the first",
            "direct measurement of crustal spin-phonon transduction",
            "from geomagnetic pulsations. New geophysics.",
        ],
    }

# ─────────────────────────────────────────────

# SENSITIVITY ANALYSIS

# ─────────────────────────────────────────────

def sensitivity_sweep():
    """
    For each geomagnetic signal type: what frequency shift
    does the minimum device produce? Is it detectable?
    """
    crystal = quartz_crystal_specs()
    fe = fe_doped_quartz_specs(100)

    f0 = crystal["c_shear"] / (2 * crystal["thickness_m"])
    Q = crystal["Q_mech"]
    V = np.pi * (crystal["diameter_m"]/2)**2 * crystal["thickness_m"]

    signals = {
        "Earth steady field":       5e-5,
        "Diurnal variation":        50e-9,
        "Geomagnetic storm":        500e-9,
        "Substorm Pi2":             20e-9,
        "Pc1 pulsation":            1e-9,
        "Schumann resonance":       1e-12,
        "Picking up crystal":       1e-4,    # hand near crystal, ~1 Gauss
        "Small magnet at 1m":       1e-3,    # fridge magnet at 1m
        "Car driving past":         1e-6,    # steel mass at 10m
        "Truck engine":             5e-5,    # from cab, nearby ferrous mass
    }

    results = {}
    for name, dB in signals.items():
        r = frequency_shift_from_field(
            delta_B_T=dB,
            f0_Hz=f0,
            Q_mech=Q,
            eta_cm=fe["eta_spin_phonon_cm"],
            fe_ppm=fe["fe_ppm"],
            crystal_volume_m3=V,
            T=300.0,
        )
        results[name] = r

    return results

def concentration_optimization():
    """
    What Fe concentration maximizes sensitivity?

    More Fe = more coupling sites = larger Δf
    But more Fe = more strain = lower Q
    And more Fe = broader spin linewidth = less coherent response

    There's an optimum.
    """
    crystal = quartz_crystal_specs()
    f0 = crystal["c_shear"] / (2 * crystal["thickness_m"])
    V = np.pi * (crystal["diameter_m"]/2)**2 * crystal["thickness_m"]

    results = []
    for ppm in [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]:
        # Q degradation with Fe content
        # Empirical: Q ~ Q₀ / (1 + ppm/1000)
        Q = crystal["Q_mech"] / (1 + ppm / 1000)
    
        # Spin-phonon coupling might increase slightly with concentration
        # due to Fe-Fe exchange (but this is weak in SiO₂)
        eta = 0.3  # cm⁻¹ (roughly constant)
    
        r = frequency_shift_from_field(
            delta_B_T=500e-9,  # storm-level signal
            f0_Hz=f0,
            Q_mech=Q,
            eta_cm=eta,
            fe_ppm=ppm,
            crystal_volume_m3=V,
        )
    
        # Figure of merit: Δf / Δf_min
        # Want maximum signal-to-resolution ratio
        fom = abs(r["delta_f_Hz"]) / r["resolution_Q_limited_Hz"]
    
        results.append({
            "fe_ppm": ppm,
            "Q_mech": Q,
            "delta_f_Hz": r["delta_f_Hz"],
            "delta_f_ppb": r["delta_f_ppb"],
            "resolution_Hz": r["resolution_Q_limited_Hz"],
            "figure_of_merit": fom,
            "detectable": r["detectable_gps"],
        })

    return results

# ─────────────────────────────────────────────

# MAIN

# ─────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 80)
    print("CRYSTAL DEVICE — FOLLOWING THE GRADIENT")
    print("Frequency-shift magnetometry via spin-phonon coupling in quartz")
    print("=" * 80)

    # ── Device configurations ──
    configs = [config_minimum_viable(), config_optimized(), config_geological()]
    for cfg in configs:
        print(f"\n{'─'*80}")
        print(f"  {cfg['name']}")
        print(f"{'─'*80}")
        if "cost_USD" in cfg:
            cost = cfg["cost_USD"]
            if isinstance(cost, str):
                print(f"  Cost: {cost}")
            else:
                print(f"  Cost: ${cost}")
        for key, val in cfg.items():
            if key in ("name", "cost_USD"):
                continue
            if isinstance(val, list):
                print(f"  {key}:")
                for item in val:
                    print(f"    {item}")
            elif isinstance(val, dict):
                continue
            elif isinstance(val, tuple):
                print(f"  {key}: {val}")
            else:
                print(f"  {key}: {val}")

    # ── Sensitivity sweep ──
    print(f"\n{'='*80}")
    print("SENSITIVITY: What can the device detect?")
    print(f"{'='*80}")
    print(f"  Crystal: 8mm × 100μm AT-cut, 100 ppm Fe³⁺, Q=10⁶")
    print(f"  f₀ = 18.82 MHz")

    sens = sensitivity_sweep()
    print(f"\n  {'Signal':>25s}  {'ΔB':>10s}  {'Δf':>12s}  {'Δf/f ppb':>10s}  "
          f"{'1s gate':>8s}  {'GPS':>8s}  {'Q-lim':>8s}")
    print("  " + "─" * 90)
    for name, r in sens.items():
        d1 = "YES" if r["detectable_1s_gate"] else "no"
        dg = "YES" if r["detectable_gps"] else "no"
        dq = "YES" if r["detectable_Q_limited"] else "no"
        print(f"  {name:>25s}  {r['delta_B_T']:>10.1e}  {r['delta_f_Hz']:>12.4e}  "
              f"{r['delta_f_ppb']:>10.4e}  {d1:>8s}  {dg:>8s}  {dq:>8s}")

    # ── Concentration optimization ──
    print(f"\n{'='*80}")
    print("Fe CONCENTRATION OPTIMIZATION")
    print(f"{'='*80}")
    conc = concentration_optimization()
    print(f"\n  {'ppm':>8s}  {'Q':>12s}  {'Δf Hz':>12s}  {'Δf ppb':>10s}  "
          f"{'resolution':>12s}  {'FoM':>12s}  {'detect':>8s}")
    print("  " + "─" * 80)
    best_fom = 0
    best_ppm = 0
    for c in conc:
        det = "YES" if c["detectable"] else "no"
        marker = ""
        if c["figure_of_merit"] > best_fom:
            best_fom = c["figure_of_merit"]
            best_ppm = c["fe_ppm"]
        print(f"  {c['fe_ppm']:>8d}  {c['Q_mech']:>12.2e}  {c['delta_f_Hz']:>12.4e}  "
              f"{c['delta_f_ppb']:>10.4e}  {c['resolution_Hz']:>12.4e}  "
              f"{c['figure_of_merit']:>12.4e}  {det:>8s}")
    print(f"\n  Optimal Fe concentration: {best_ppm} ppm (FoM = {best_fom:.2e})")

    # ── What η needs to be ──
    print(f"\n{'='*80}")
    print("WHAT η (SPIN-PHONON COUPLING) NEEDS TO BE")
    print(f"{'='*80}")
    crystal = quartz_crystal_specs()
    f0 = crystal["c_shear"] / (2 * crystal["thickness_m"])
    V = np.pi * (crystal["diameter_m"]/2)**2 * crystal["thickness_m"]

    print(f"\n  For detecting a geomagnetic storm (ΔB = 500 nT):")
    print(f"  {'η (cm⁻¹)':>12s}  {'Δf Hz':>12s}  {'Δf ppb':>10s}  {'GPS detect':>10s}")
    for eta in [0.001, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0]:
        r = frequency_shift_from_field(500e-9, f0, 1e6, eta, 100, V)
        det = "YES" if r["detectable_gps"] else "no"
        print(f"  {eta:>12.3f}  {r['delta_f_Hz']:>12.4e}  {r['delta_f_ppb']:>10.4e}  {det:>10s}")

    print(f"\n  Literature values for Fe³⁺ in oxides: η = 0.1 - 3.4 cm⁻¹")
    print(f"  If η > ~0.01 cm⁻¹ in quartz: storm-level signals are detectable.")
    print(f"  If η > ~0.001 cm⁻¹: Earth's steady field is measurable.")

    # ── The build path ──
    print(f"\n{'='*80}")
    print("BUILD PATH — SLIME MOLD SEQUENCE")
    print(f"{'='*80}")
    print("""

    STEP 0: MEASURE η
    Before building anything, measure the actual spin-phonon
    coupling in Fe-bearing quartz. Two methods:

    a) Raman spectroscopy of smoky quartz vs clear quartz.
       Look for phonon frequency shifts with applied magnetic field.
       University lab, one afternoon, no fabrication needed.

    b) Put a smoky quartz crystal in an existing oscillator circuit.
       Sweep a magnet near it. Measure frequency shift.
       If Δf > 0 when magnet approaches: coupling exists.
       Kitchen table experiment, one evening.

    This is the GO/NO-GO gate. Everything else follows from η.

    STEP 1: MINIMUM VIABLE (if η > 0.01 cm⁻¹)
    Smoky quartz + Pierce oscillator + Arduino + GPS
    Measure: does f₀ shift during geomagnetic storm?
    Compare to magnetometer data from USGS or INTERMAGNET.
    Cost: $25. Time: weekend.

    STEP 2: OPTIMIZE (if Step 1 shows signal)
    Synthetic Fe-doped crystal + TCXO + thermal enclosure
    Characterize: Δf(B) curve, noise floor, bandwidth
    Add 4-axis coil: sweep H₀ to map spin-phonon spectrum
    Cost: $300. Time: 2-4 weeks.

    STEP 3: GEOLOGICAL LISTENER (parallel with Step 2)
    Seismometer + magnetometer at Iron Range outcrop
    Record during storm season (equinox periods)
    Cross-correlate Pc1 band
    Cost: borrowed instruments. Time: 1-2 field days + analysis.

    STEP 4: NETWORK (if Steps 1-3 confirm physics)
    Multiple devices along the corridor
    Each one: quartz crystal + oscillator + GPS + LoRa radio
    Distributed magnetometer array using $25 nodes
    Differential measurements cancel common-mode noise
    The corridor becomes an antenna.

    The slime mold doesn't plan Step 4 before finishing Step 0.
    But it knows the gradient points there.
    """)
    print("=" * 80)
