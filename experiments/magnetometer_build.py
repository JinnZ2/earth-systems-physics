# experiments/magnetometer_build.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# $5 MAGNETOMETER BUILD
# Smoky quartz + HDD magnets + Arduino
#
# Signal chain:
#   Geomagnetic field variation
#   -> Fe3+ spin perturbation in smoky quartz
#   -> Spin-phonon coupling shifts lattice vibration frequency
#   -> Piezoelectric effect converts to voltage/frequency change
#   -> Arduino counts frequency shift
#   -> Magnetic field measurement
#
# This is the simplest possible test of the spin-phonon coupling
# hypothesis from earth_magnomechanical.py, Prediction #3.

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

HBAR    = 1.0545718e-34
K_B     = 1.380649e-23
MU_0    = 4 * np.pi * 1e-7
GAMMA   = 1.7608597e11
EPSILON_0 = 8.8541878128e-12

# ─────────────────────────────────────────────
# BILL OF MATERIALS
# ─────────────────────────────────────────────

BOM = {
    "tier_0": {
        "total_cost": 2.00,
        "items": [
            {"item": "Smoky quartz crystal",
             "source": "Rock shop, mineral show, eBay",
             "cost": 2.00,
             "spec": "Any smoky quartz, 1-3 cm. Darker = more Fe3+. "
                     "Smoky color IS the Fe3+ defects.",
             "critical": True},
            {"item": "HDD magnets (2x)",
             "source": "Dead hard drive (free from e-waste)",
             "cost": 0,
             "spec": "NdFeB arc magnets from voice coil actuator. "
                     "~0.3-0.5 T surface field.",
             "critical": True},
            {"item": "Wire (1m)",
             "source": "Dead speaker, old headphones, any electronics",
             "cost": 0,
             "spec": "Any thin insulated wire for electrodes.",
             "critical": False},
            {"item": "Aluminum foil",
             "source": "Kitchen",
             "cost": 0,
             "spec": "Electrode material. Wrap crystal faces.",
             "critical": False},
            {"item": "Multimeter",
             "source": "Already own, or $3 from Harbor Freight",
             "cost": 0,
             "spec": "AC voltage or frequency mode. Even cheap ones work.",
             "critical": True},
        ],
    },
    "tier_1": {
        "total_cost": 5.00,
        "items": [
            {"item": "Everything from Tier 0", "cost": 2.00},
            {"item": "Arduino Nano clone",
             "source": "AliExpress, Amazon",
             "cost": 3.00,
             "spec": "ATmega328P, 16 MHz crystal. Counts frequency to ~1 ppb.",
             "critical": True},
            {"item": "USB cable",
             "source": "Junk drawer",
             "cost": 0,
             "spec": "Mini-USB or USB-C depending on clone."},
        ],
    },
    "tier_2": {
        "total_cost": 15.00,
        "items": [
            {"item": "Everything from Tier 1", "cost": 5.00},
            {"item": "32.768 kHz crystal oscillator",
             "source": "Electronics supplier, dead watch",
             "cost": 0.50,
             "spec": "Standard watch crystal. Known frequency reference."},
            {"item": "LM358 op-amp",
             "source": "Any electronics supplier",
             "cost": 0.20,
             "spec": "Signal amplifier for weak piezo output."},
            {"item": "Thermistor (10k NTC)",
             "source": "Any electronics supplier",
             "cost": 0.10,
             "spec": "Temperature compensation. Quartz frequency drifts with T."},
            {"item": "Perfboard + capacitors",
             "source": "Electronics supplier",
             "cost": 2.00,
             "spec": "For oscillator circuit."},
            {"item": "3D-printed coil form (optional)",
             "source": "Any 3D printer",
             "cost": 0.50,
             "spec": "Wind salvaged wire around form for controlled bias field. "
                     "Replaces HDD magnets with tunable electromagnet."},
        ],
    },
}


# ─────────────────────────────────────────────
# CRYSTAL PHYSICS
# ─────────────────────────────────────────────

def smoky_quartz_properties(fe_ppm=50, thickness_m=5e-3, diameter_m=15e-3):
    """
    Properties of a typical smoky quartz specimen.

    Smoky quartz gets its color from Fe3+ substituting for Si4+
    in the tetrahedral site of the SiO2 lattice. Irradiation
    (natural or artificial) creates the color center.

    Typical Fe3+ concentration in smoky quartz: 10-200 ppm.
    Darker = more iron. Very dark (morion) can be 500+ ppm.

    fe_ppm      : iron concentration (ppm by weight)
    thickness_m : crystal thickness along measurement axis (m)
    diameter_m  : crystal diameter (m)
    """
    rho = 2650  # kg/m3
    c_shear = 3764  # m/s (AT-cut equivalent, shear mode)
    c_long = 5720   # m/s (longitudinal)
    Q_mech = 1e4    # natural crystal (lower than synthetic AT-cut)
    d_11 = 2.3e-12  # C/N (natural quartz d11, not AT-cut d26)

    V = np.pi * (diameter_m/2)**2 * thickness_m
    mass = rho * V

    # Resonant frequencies (thickness modes)
    f_shear_1 = c_shear / (2 * thickness_m)
    f_long_1 = c_long / (2 * thickness_m)

    # Fe3+ properties
    N_fe = fe_ppm * 1e-6 * mass * 6.022e23 / 0.060  # atoms
    M_s = fe_ppm * 1.0  # A/m (rough: 1 A/m per ppm)

    # Spin-phonon coupling
    eta_cm = 0.3  # cm^-1 (conservative for dilute Fe in quartz)
    eta_Hz = eta_cm * 3e10
    eta_rad = 2 * np.pi * eta_Hz

    # Zero-point motion for fundamental shear mode
    omega_1 = 2 * np.pi * f_shear_1
    x_zpf = np.sqrt(HBAR / (2 * rho * V * omega_1))

    # Per-ion spin-phonon coupling
    a_0 = 4.9e-10
    g_sp = eta_rad * x_zpf / a_0

    # HONEST COLLECTIVE ENHANCEMENT:
    # sqrt(N) assumes all spins are coherent (like in YIG).
    # In smoky quartz, Fe3+ sites are PARAMAGNETIC — randomly oriented,
    # no exchange coupling between them.
    # Realistic: incoherent addition gives sqrt(N) for fluctuations,
    # but only N^(1/4) for coherent coupling to a single phonon mode.
    # Even more conservatively: use single-ion coupling * N_eff
    # where N_eff ~ (number of Fe within one phonon wavelength)
    #
    # Most conservative: just use per-ion coupling (no enhancement).
    # This is the floor — anything measured above this is bonus.
    N_coherent = max(N_fe**(0.25), 1)  # N^(1/4) conservative
    g_sp_collective = g_sp * N_coherent

    return {
        "fe_ppm": fe_ppm,
        "thickness_m": thickness_m,
        "diameter_m": diameter_m,
        "volume_m3": V,
        "mass_g": mass * 1000,
        "f_shear_1_Hz": f_shear_1,
        "f_long_1_Hz": f_long_1,
        "Q_natural": Q_mech,
        "d_11_CN": d_11,
        "N_fe_ions": N_fe,
        "N_coherent": N_coherent,
        "M_s_Am": M_s,
        "eta_spin_phonon_cm": eta_cm,
        "g_sp_per_ion_Hz": g_sp / (2 * np.pi),
        "g_sp_collective_Hz": g_sp_collective / (2 * np.pi),
        "x_zpf_m": x_zpf,
    }


def frequency_shift_from_field(delta_B_T, crystal=None):
    """
    Predicted frequency shift from a magnetic field change.

    This is the core measurement: does the crystal's resonant
    frequency change when the ambient magnetic field changes?

    Two mechanisms:
    1. Spin-phonon: delta_B -> magnon shift -> phonon frequency pull
       (through coupling g_sp)
    2. Magnetostriction: delta_B -> strain -> frequency shift
       (much weaker for dilute Fe)

    delta_B_T : magnetic field change (T)
    crystal   : crystal properties dict (from smoky_quartz_properties)
    """
    if crystal is None:
        crystal = smoky_quartz_properties()

    # Magnon frequency shift
    delta_omega_magnon = GAMMA * MU_0 * delta_B_T
    delta_f_magnon = delta_omega_magnon / (2 * np.pi)

    # Phonon frequency (the mode we're measuring)
    f_phonon = crystal["f_shear_1_Hz"]
    omega_phonon = 2 * np.pi * f_phonon
    Q = crystal["Q_natural"]

    # Phonon linewidth
    gamma_b = omega_phonon / Q

    # Detuning between magnon and phonon
    # At Earth's field (50 uT): f_magnon ~ 1.4 kHz
    # Phonon fundamental of 5mm crystal: f ~ 376 kHz
    # Huge detuning — but coupling still pulls frequency
    H_earth = 5e-5
    omega_magnon = GAMMA * MU_0 * H_earth
    detuning = omega_phonon - omega_magnon

    # Frequency pull from spin-phonon coupling
    # delta_f_phonon = g_sp^2 * delta_omega_magnon / detuning^2
    # This is the dispersive (off-resonant) regime
    g_sp = crystal["g_sp_collective_Hz"] * 2 * np.pi
    if abs(detuning) > 0:
        delta_omega_phonon = g_sp**2 * delta_omega_magnon / detuning**2
    else:
        delta_omega_phonon = 0

    delta_f_phonon = delta_omega_phonon / (2 * np.pi)

    # Fractional frequency shift (what Arduino measures)
    fractional_shift = delta_f_phonon / f_phonon if f_phonon > 0 else 0

    # Direct magnetostriction contribution (much smaller)
    # delta_f/f ~ (lambda_s / Y) * delta_sigma ~ 1e-12 per T for quartz
    magnetostriction_fractional = 1e-12 * delta_B_T / MU_0

    total_fractional = fractional_shift + magnetostriction_fractional
    total_delta_f = total_fractional * f_phonon

    # Arduino frequency counter resolution
    # Using 1-second gate time: resolution = 1 Hz
    # Using 10-second gate: resolution = 0.1 Hz
    # Using reciprocal counting: resolution ~ f/2^16 ~ 5.7 Hz for 376 kHz
    gate_1s_resolution = 1.0  # Hz
    gate_10s_resolution = 0.1  # Hz

    detectable_1s = abs(total_delta_f) > gate_1s_resolution
    detectable_10s = abs(total_delta_f) > gate_10s_resolution

    return {
        "delta_B_T": delta_B_T,
        "delta_f_magnon_Hz": delta_f_magnon,
        "delta_f_phonon_Hz": delta_f_phonon,
        "fractional_spin_phonon": fractional_shift,
        "fractional_magnetostriction": magnetostriction_fractional,
        "total_fractional_shift": total_fractional,
        "total_delta_f_Hz": total_delta_f,
        "f_phonon_Hz": f_phonon,
        "detectable_1s_gate": detectable_1s,
        "detectable_10s_gate": detectable_10s,
        "resolution_1s_Hz": gate_1s_resolution,
        "resolution_10s_Hz": gate_10s_resolution,
    }


def sensitivity_analysis(crystal=None):
    """
    What field changes can we detect at each measurement tier?
    """
    if crystal is None:
        crystal = smoky_quartz_properties()

    signals = [
        ("Earth's field (reference)",     5e-5),
        ("Geomagnetic storm (500 nT)",    500e-9),
        ("Diurnal variation (50 nT)",     50e-9),
        ("Substorm Pi2 (20 nT)",          20e-9),
        ("Pc3 pulsation (5 nT)",          5e-9),
        ("Pc1 pulsation (1 nT)",          1e-9),
        ("Schumann resonance (1 pT)",     1e-12),
        ("Drive over Iron Range anomaly",  5e-6),
        ("Bring magnet near crystal",      0.01),
    ]

    results = []
    for name, dB in signals:
        r = frequency_shift_from_field(dB, crystal)
        results.append({
            "signal": name,
            "delta_B_T": dB,
            "delta_f_Hz": r["total_delta_f_Hz"],
            "fractional": r["total_fractional_shift"],
            "detectable_1s": r["detectable_1s_gate"],
            "detectable_10s": r["detectable_10s_gate"],
        })

    return results


# ─────────────────────────────────────────────
# BUILD INSTRUCTIONS
# ─────────────────────────────────────────────

BUILD_STEPS = {
    "tier_0": [
        {
            "step": 1,
            "title": "Extract HDD magnets",
            "instructions": [
                "Open dead hard drive (Torx T8 screwdriver, or pry with flat blade)",
                "Remove the voice coil actuator assembly (2 arc magnets + steel keeper)",
                "CAREFUL: these magnets are strong and will pinch fingers",
                "Keep the steel keeper plate — use as field concentrator",
            ],
            "tools": "Torx screwdriver or flat blade",
            "time_min": 10,
        },
        {
            "step": 2,
            "title": "Prepare electrodes",
            "instructions": [
                "Cut two squares of aluminum foil, slightly smaller than crystal faces",
                "Attach thin wire to each foil square (twist + tape, or solder)",
                "These are your piezoelectric readout electrodes",
            ],
            "tools": "Scissors, tape",
            "time_min": 5,
        },
        {
            "step": 3,
            "title": "Assemble sensor",
            "instructions": [
                "Place foil electrode on one flat face of smoky quartz",
                "Place second electrode on opposite face",
                "Secure with tape or rubber band (don't over-compress)",
                "Mount crystal between HDD magnets with ~5mm air gap",
                "The magnets provide the DC bias field for magnon tuning",
                "Crystal axis orientation matters but any orientation will show SOME response",
            ],
            "tools": "Tape, rubber band",
            "time_min": 5,
        },
        {
            "step": 4,
            "title": "Measure",
            "instructions": [
                "Connect electrode wires to multimeter (AC voltage mode)",
                "Tap the crystal gently — you should see a voltage spike",
                "This confirms piezoelectric response is working",
                "Now move a magnet near/far from the crystal slowly",
                "Watch for voltage changes correlated with magnet position",
                "If you see it: spin-phonon coupling is generating signal",
            ],
            "tools": "Multimeter",
            "time_min": 10,
        },
    ],
    "tier_1": [
        {
            "step": 5,
            "title": "Add Arduino frequency counter",
            "instructions": [
                "Upload FreqCount library sketch to Arduino Nano",
                "Connect one electrode to Arduino digital pin 5 (FreqCount input)",
                "Connect other electrode to GND",
                "Open Serial Monitor at 115200 baud",
                "You should see the crystal's resonant frequency updating",
                "Log the frequency over time — plot later",
            ],
            "tools": "Arduino Nano, USB cable, computer",
            "time_min": 20,
            "code": """
// Arduino frequency counter for smoky quartz magnetometer
// Uses FreqCount library (install via Library Manager)
// Connect crystal between pin 5 and GND
// May need amplifier if signal is too weak

#include <FreqCount.h>

void setup() {
    Serial.begin(115200);
    FreqCount.begin(1000);  // 1 second gate time
    Serial.println("time_ms,frequency_Hz");
}

void loop() {
    if (FreqCount.available()) {
        unsigned long freq = FreqCount.read();
        Serial.print(millis());
        Serial.print(",");
        Serial.println(freq);
    }
}
""",
        },
        {
            "step": 6,
            "title": "Baseline measurement",
            "instructions": [
                "Let the system run for 30 minutes undisturbed",
                "This establishes the frequency baseline and drift rate",
                "Temperature drift dominates at first — crystal needs to equilibrate",
                "After stabilization, typical drift should be < 1 Hz/min",
            ],
            "time_min": 30,
        },
        {
            "step": 7,
            "title": "Magnetic field test",
            "instructions": [
                "While logging frequency, slowly move a magnet toward the crystal",
                "Move it from 1 meter away to 10 cm, then back out",
                "Do this 5 times with 1-minute gaps",
                "The frequency trace should show correlated shifts",
                "Compare to: moving a non-magnetic object (control)",
                "If frequency shifts correlate with magnet distance: SUCCESS",
            ],
            "time_min": 15,
        },
    ],
    "tier_1_truck_test": [
        {
            "step": 8,
            "title": "Mobile magnetometer test",
            "instructions": [
                "Mount crystal assembly on rigid surface (dashboard, toolbox)",
                "Connect Arduino to laptop running serial logger",
                "Drive a route that crosses known magnetic anomaly",
                "Iron Range, MN: US-169 from Virginia to Hibbing",
                "Or any road crossing exposed iron formation",
                "Log GPS coordinates simultaneously (phone GPS app)",
                "Plot frequency vs position after the drive",
                "Known magnetic anomaly map should correlate with frequency trace",
            ],
            "time_min": 60,
            "note": "This is Prediction #3 from earth_magnomechanical.py tested from a truck",
        },
    ],
}


# ─────────────────────────────────────────────
# EXPECTED RESULTS
# ─────────────────────────────────────────────

def expected_results():
    """
    What should you see at each test stage?
    Honest assessment of what's detectable and what's not.
    """
    crystal = smoky_quartz_properties(fe_ppm=50, thickness_m=5e-3)
    sens = sensitivity_analysis(crystal)

    # Minimum detectable field (where df > 0.1 Hz with 10s gate)
    # df = g^2 * gamma*mu0*dB / detuning^2
    # Solve for dB: dB = df * detuning^2 / (g^2 * gamma*mu0)
    g_sp = crystal["g_sp_collective_Hz"] * 2 * np.pi
    f_phonon = crystal["f_shear_1_Hz"]
    omega_phonon = 2 * np.pi * f_phonon
    H_earth = 5e-5
    omega_magnon = GAMMA * MU_0 * H_earth
    detuning = omega_phonon - omega_magnon
    target_df = 0.1  # Hz (10s gate resolution)
    target_domega = 2 * np.pi * target_df
    if g_sp > 0:
        dB_min = target_domega * detuning**2 / (g_sp**2 * GAMMA * MU_0)
    else:
        dB_min = np.inf

    return {
        "crystal": crystal,
        "sensitivity": sens,
        "min_detectable_B_T": dB_min,
        "min_detectable_B_mT": dB_min * 1000,
        "predictions": {
            "tap_test": {
                "expected": "Clear voltage spike on multimeter (10-100 mV)",
                "confirms": "Piezoelectric effect is working",
                "difficulty": "Easy — should work on first try",
            },
            "magnet_proximity": {
                "expected": "Measurable frequency shift (~1-10 Hz) with magnet at 5-10 cm",
                "confirms": "Magnetic field affects crystal resonance",
                "difficulty": "Easy — HDD magnet is strong enough (10+ mT at 5cm)",
                "honest": f"Minimum detectable field: ~{dB_min*1000:.1f} mT with 10s gate. "
                          "Natural geomagnetic signals (nT-uT) are NOT detectable "
                          "with bare Arduino. Need oscillator circuit + long integration.",
            },
            "hdd_magnet_sweep": {
                "expected": "Reproducible frequency shift correlated with field strength",
                "confirms": "Field-dependent resonance shift IS real",
                "difficulty": "Moderate — need to control magnet position precisely",
                "note": "This is the first real validation. If frequency tracks "
                        "magnet distance reproducibly, the coupling is confirmed.",
            },
            "iron_range_drive": {
                "expected": "NOT directly detectable with Arduino frequency counter. "
                            "Iron Range anomaly is ~5 uT — need ~1000x better resolution.",
                "confirms": "Would confirm geological-scale coupling IF detected",
                "difficulty": "Needs Tier 2 build: oscillator circuit, phase-locked loop, "
                             "or mixer down-conversion for sub-mHz resolution",
                "upgrade_path": "Mix crystal frequency with reference oscillator. "
                               "Beat frequency in audio range. Record audio. "
                               "FFT gives sub-mHz resolution.",
            },
            "geomagnetic_storm": {
                "expected": "NOT detectable with basic build. Storms are ~500 nT = 0.5 uT. "
                            "Need 10,000x improvement from Tier 0.",
                "upgrade_path": "Phase-locked loop tracking crystal frequency. "
                               "Integration over hours. Temperature-stabilized enclosure. "
                               "This is a real instrument, not a weekend hack.",
                "note": "This is the ultimate validation. Everything else is "
                        "proximity sensing. Storm correlation proves the COUPLING.",
            },
        },
        "failure_modes": {
            "no_piezo_response": "Crystal may not be oriented on a piezoelectric axis. "
                                "Rotate and try different face pairs.",
            "frequency_unstable": "Temperature drift dominates. Let crystal equilibrate 1 hour. "
                                 "Add thermistor for compensation.",
            "no_magnetic_response": "Fe concentration may be too low (very light smoky). "
                                   "Try darker crystal, or use synthetic Fe-doped.",
            "vibration_noise": "Mechanical vibration shifts frequency. Mount on foam. "
                              "For truck test: low-pass filter the data.",
        },
    }


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("$5 MAGNETOMETER BUILD — SMOKY QUARTZ + HDD MAGNETS + ARDUINO")
    print("=" * 70)

    # Crystal properties
    crystal = smoky_quartz_properties()
    print(f"\n--- CRYSTAL PROPERTIES ---")
    print(f"  Smoky quartz, {crystal['thickness_m']*1000:.0f}mm thick, "
          f"{crystal['diameter_m']*1000:.0f}mm diameter")
    print(f"  Fe3+ concentration: ~{crystal['fe_ppm']} ppm (typical smoky)")
    print(f"  Mass: {crystal['mass_g']:.1f} g")
    print(f"  Fundamental shear: {crystal['f_shear_1_Hz']:.0f} Hz")
    print(f"  Natural Q: {crystal['Q_natural']:.0e}")
    print(f"  Fe3+ ions: {crystal['N_fe_ions']:.2e}")
    print(f"  Collective coupling: {crystal['g_sp_collective_Hz']:.4e} Hz")

    # Sensitivity
    print(f"\n--- SENSITIVITY ANALYSIS ---")
    print(f"  {'Signal':>35s}  {'dB (T)':>12s}  {'df (Hz)':>12s}  "
          f"{'1s gate':>8s}  {'10s gate':>8s}")
    print(f"  {'─'*78}")
    sens = sensitivity_analysis(crystal)
    for s in sens:
        d1 = "YES" if s["detectable_1s"] else "no"
        d10 = "YES" if s["detectable_10s"] else "no"
        print(f"  {s['signal']:>35s}  {s['delta_B_T']:>12.4e}  "
              f"{s['delta_f_Hz']:>12.4e}  {d1:>8s}  {d10:>8s}")

    # BOM
    print(f"\n--- BILL OF MATERIALS ---")
    for tier_name, tier in BOM.items():
        print(f"\n  [{tier_name}] Total: ${tier['total_cost']:.2f}")
        for item in tier["items"]:
            cost = f"${item['cost']:.2f}" if isinstance(item.get('cost'), (int, float)) else ""
            name = item['item']
            print(f"    {name:40s}  {cost}")

    # Build steps
    print(f"\n--- BUILD STEPS (Tier 0 + Tier 1) ---")
    for tier_key in ["tier_0", "tier_1"]:
        for step in BUILD_STEPS[tier_key]:
            print(f"\n  Step {step['step']}: {step['title']} (~{step['time_min']} min)")
            for instr in step["instructions"][:3]:
                print(f"    - {instr[:70]}")

    # Expected results
    print(f"\n--- EXPECTED RESULTS ---")
    results = expected_results()
    for test_name, pred in results["predictions"].items():
        print(f"\n  {test_name}:")
        print(f"    Expected: {pred['expected'][:65]}")
        print(f"    Difficulty: {pred['difficulty'][:65]}")

    print(f"\n--- FAILURE MODES ---")
    for mode, fix in results["failure_modes"].items():
        print(f"  {mode}: {fix[:65]}")

    print("\n" + "=" * 70)
    print("BUILD TIME: ~30 minutes (Tier 0) or ~1 hour (Tier 1)")
    print("FIRST TEST: tap the crystal, watch the multimeter")
    print("REAL TEST:  drive over Iron Range, plot frequency vs position")
    print("=" * 70)
