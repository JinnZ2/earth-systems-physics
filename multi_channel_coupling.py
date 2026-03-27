# multi_channel_coupling.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Can multiple weak coupling channels converge to overcome
# the magnetostrictive coupling deficit in quartz/Fe?
#
# Five channels analyzed:
# 1. OPTICAL:     laser-driven phonon excitation
# 2. ACOUSTIC:    direct phonon injection (ultrasonic transducer)
# 3. THERMAL:     phonon population modulation via temperature gradient
# 4. PIEZOELECTRIC: voltage-driven strain -> phonon -> magnon
# 5. SPIN-ORBIT:  Fe3+ crystal field coupling (not magnetostriction)

import numpy as np

HBAR  = 1.0545718e-34
K_B   = 1.380649e-23
MU_0  = 4 * np.pi * 1e-7
GAMMA = 1.7608597e11
MU_B  = 9.274e-24
C_LIGHT = 2.998e8
EPSILON_0 = 8.854e-12

# ─────────────────────────────────────────────
# BASELINE: the deficit we need to overcome
# ─────────────────────────────────────────────

def baseline_magnetostrictive(
    thickness_m=0.1e-3, diameter_m=5e-3, c_sound=3764.0, rho=2650.0,
    fe_ppm=100, B_me=1e4, alpha=0.1, Q_mech=1e6, H0=1.0,
):
    """Baseline magnetostrictive cooperativity (the weak one)."""
    M_s = fe_ppm * 1.0
    r = diameter_m / 2
    V = np.pi * r**2 * thickness_m

    f_phonon = c_sound / (2 * thickness_m)
    omega_ph = 2 * np.pi * f_phonon

    x_zpf = np.sqrt(HBAR / (2 * rho * V * omega_ph))
    g_mb = (B_me / max(M_s, 1)) * x_zpf * omega_ph

    gamma_m = alpha * GAMMA * MU_0 * H0
    gamma_b = omega_ph / Q_mech

    C = (4 * g_mb**2) / (gamma_m * gamma_b) if (gamma_m > 0 and gamma_b > 0) else 0

    return {
        "C_magnetostrictive": C,
        "g_mb_Hz": g_mb / (2*np.pi),
        "gamma_m_Hz": gamma_m / (2*np.pi),
        "gamma_b_Hz": gamma_b / (2*np.pi),
        "f_phonon_Hz": f_phonon,
        "omega_ph": omega_ph,
        "x_zpf_m": x_zpf,
        "V_m3": V,
        "M_s": M_s,
        "H0": H0,
        "Q_mech": Q_mech,
    }


# ─────────────────────────────────────────────
# CHANNEL 1: OPTICAL
# ─────────────────────────────────────────────

def optical_phonon_drive(
    base, laser_power_W=0.001, wavelength_m=532e-9,
    spot_diameter_m=100e-6, absorption_coeff=0.01,
):
    """Laser-driven phonon excitation via inverse piezo, electrostriction, SBS."""
    V = base["V_m3"]
    omega_ph = base["omega_ph"]
    rho = 2650.0

    P_abs = laser_power_W * absorption_coeff
    omega_photon = 2 * np.pi * C_LIGHT / wavelength_m
    phonons_per_photon = omega_photon / omega_ph
    photon_rate = P_abs / (HBAR * omega_photon)
    phonon_rate = photon_rate * phonons_per_photon

    tau_phonon = base["Q_mech"] / omega_ph
    delta_n_thermal = phonon_rate * tau_phonon

    n_thermal_300K = K_B * 300 / (HBAR * omega_ph)
    n_eff = n_thermal_300K + delta_n_thermal
    enhancement = n_eff / n_thermal_300K

    A_spot = np.pi * (spot_diameter_m/2)**2
    E_field = np.sqrt(2 * laser_power_W / (EPSILON_0 * C_LIGHT * A_spot))
    chi_e = 4.5 - 1
    strain_electro = EPSILON_0 * chi_e * E_field**2 / (2 * rho * 3764**2)
    x_electro = strain_electro * V**(1/3)
    x_ratio = x_electro / base["x_zpf_m"]

    g_B = 0.5e-11
    I_laser = laser_power_W / A_spot
    brillouin_gain = g_B * I_laser
    brillouin_gain_crystal = brillouin_gain * V**(1/3)

    C_enhanced = base["C_magnetostrictive"] * n_eff * 2

    return {
        "channel": "OPTICAL (laser-driven phonons)",
        "P_laser_W": laser_power_W,
        "P_absorbed_W": P_abs,
        "photon_rate_Hz": photon_rate,
        "phonon_rate_Hz": phonon_rate,
        "delta_n_phonon": delta_n_thermal,
        "n_thermal_background": n_thermal_300K,
        "n_effective": n_eff,
        "enhancement_factor": enhancement,
        "E_field_V_m": E_field,
        "strain_electrostriction": strain_electro,
        "x_electrostriction_m": x_electro,
        "x_over_zpf": x_ratio,
        "brillouin_gain_per_m": brillouin_gain,
        "C_enhanced": C_enhanced,
        "C_ratio": C_enhanced / max(base["C_magnetostrictive"], 1e-99),
    }


# ─────────────────────────────────────────────
# CHANNEL 2: ACOUSTIC
# ─────────────────────────────────────────────

def acoustic_phonon_drive(
    base, transducer_power_W=0.01, coupling_efficiency=0.1, bandwidth_Hz=1000,
):
    """Glue an ultrasonic transducer to the crystal. Drive phonons directly."""
    omega_ph = base["omega_ph"]
    Q = base["Q_mech"]

    P_coupled = transducer_power_W * coupling_efficiency
    tau_phonon = Q / omega_ph
    E_stored = P_coupled * tau_phonon
    n_driven = E_stored / (HBAR * omega_ph)
    n_thermal = K_B * 300 / (HBAR * omega_ph)

    m_eff = 2650 * base["V_m3"]
    x_driven = np.sqrt(2 * n_driven * HBAR / (m_eff * omega_ph))
    x_ratio = x_driven / base["x_zpf_m"]
    strain = x_driven / base["V_m3"]**(1/3)

    C_enhanced = base["C_magnetostrictive"] * (2 * n_driven)

    d_26 = 3.1e-12
    V_piezo = d_26 * 2650 * 3764**2 * strain * base["V_m3"]**(1/3)

    return {
        "channel": "ACOUSTIC (ultrasonic transducer)",
        "P_transducer_W": transducer_power_W,
        "P_coupled_W": P_coupled,
        "E_stored_J": E_stored,
        "n_driven": n_driven,
        "n_thermal": n_thermal,
        "x_driven_m": x_driven,
        "x_over_zpf": x_ratio,
        "strain": strain,
        "V_piezo_V": V_piezo,
        "C_enhanced": C_enhanced,
        "C_ratio": C_enhanced / max(base["C_magnetostrictive"], 1e-99),
    }


# ─────────────────────────────────────────────
# CHANNEL 3: THERMAL
# ─────────────────────────────────────────────

def thermal_modulation(base, delta_T=1.0, modulation_freq_Hz=1.0):
    """Thermal expansion creates strain. Modulated T -> modulated strain -> phonons."""
    omega_ph = base["omega_ph"]
    alpha_thermal = 13.7e-6  # 1/K for quartz

    strain_thermal = alpha_thermal * delta_T
    L = base["V_m3"]**(1/3)
    x_thermal = strain_thermal * L

    T = 300.0
    n_thermal = K_B * T / (HBAR * omega_ph)
    delta_n = n_thermal * delta_T / T

    C_enhanced = base["C_magnetostrictive"] * (1 + delta_n / n_thermal)

    parametric_gain = 1.0
    if modulation_freq_Hz > 0:
        strain_threshold = 2 / (np.pi * base["Q_mech"])
        if strain_thermal > strain_threshold:
            parametric_gain = np.exp(np.pi * base["Q_mech"] * strain_thermal / 4)
            parametric_gain = min(parametric_gain, 1e20)
        else:
            parametric_gain = strain_thermal / strain_threshold

    return {
        "channel": "THERMAL (temperature modulation)",
        "delta_T_K": delta_T,
        "strain_thermal": strain_thermal,
        "x_thermal_m": x_thermal,
        "x_over_zpf": x_thermal / base["x_zpf_m"],
        "n_thermal": n_thermal,
        "delta_n": delta_n,
        "strain_threshold_parametric": 2 / (np.pi * base["Q_mech"]),
        "above_parametric_threshold": strain_thermal > 2 / (np.pi * base["Q_mech"]),
        "parametric_gain": parametric_gain,
        "C_enhanced": base["C_magnetostrictive"] * max(parametric_gain, 1),
        "C_ratio": max(parametric_gain, 1),
    }


# ─────────────────────────────────────────────
# CHANNEL 4: PIEZOELECTRIC
# ─────────────────────────────────────────────

def piezo_drive(base, V_drive=1.0):
    """Apply voltage across quartz -> piezoelectric strain -> phonons."""
    omega_ph = base["omega_ph"]
    Q = base["Q_mech"]
    rho = 2650.0
    c = 3764.0
    thickness = base["V_m3"]**(1/3)

    d_26 = 3.1e-12
    E_elec = V_drive / thickness
    strain_static = d_26 * E_elec
    strain_resonant = strain_static * Q
    x_resonant = strain_resonant * thickness

    m_eff = rho * base["V_m3"]
    n_driven = m_eff * omega_ph * x_resonant**2 / (2 * HBAR)

    A = base["V_m3"] / thickness
    C_cap = EPSILON_0 * 4.5 * A / thickness
    P_drive = 0.5 * C_cap * V_drive**2 * omega_ph / Q

    C_enhanced = base["C_magnetostrictive"] * (2 * n_driven)

    return {
        "channel": "PIEZOELECTRIC (voltage -> phonon -> magnon)",
        "V_drive_V": V_drive,
        "E_field_V_m": E_elec,
        "strain_static": strain_static,
        "strain_resonant": strain_resonant,
        "Q_amplification": Q,
        "x_resonant_m": x_resonant,
        "x_over_zpf": x_resonant / base["x_zpf_m"],
        "n_driven_phonons": n_driven,
        "P_drive_W": P_drive,
        "C_enhanced": C_enhanced,
        "C_ratio": C_enhanced / max(base["C_magnetostrictive"], 1e-99),
    }


# ─────────────────────────────────────────────
# CHANNEL 5: SPIN-ORBIT at Fe3+ defect site
# ─────────────────────────────────────────────

def spin_orbit_coupling(base, fe_ppm=100):
    """
    Fe3+ in quartz: 3d5 high-spin configuration.
    Spin-phonon coupling via crystal field modulation.
    eta ~ 0.1 - 3.4 cm-1 (from Raman spectroscopy of Fe3+ oxides).
    ORDERS OF MAGNITUDE stronger than magnetostriction for dilute ions.
    """
    omega_ph = base["omega_ph"]

    lambda_SO = -103  # cm-1
    lambda_SO_Hz = abs(lambda_SO) * 3e10
    Dq = 12000  # cm-1

    eta_spc = 1.5  # cm-1
    eta_Hz = eta_spc * 3e10
    eta_rad = 2 * np.pi * eta_Hz

    a_0 = 4.9e-10  # SiO2 lattice parameter
    g_sp_per_ion = eta_rad * base["x_zpf_m"] / a_0

    N_fe = fe_ppm * 1e-6 * base["V_m3"] * 2650 * 6.022e23 / 0.060
    g_sp_collective = g_sp_per_ion * np.sqrt(N_fe)

    ratio_to_magnetostriction = g_sp_per_ion / (base["g_mb_Hz"] * 2 * np.pi / max(N_fe, 1))

    gamma_m = base["gamma_m_Hz"] * 2 * np.pi
    gamma_b = base["gamma_b_Hz"] * 2 * np.pi
    C_sp = (4 * g_sp_collective**2) / (gamma_m * gamma_b) if (gamma_m > 0 and gamma_b > 0) else 0

    T1_estimate = 1e-7  # s

    return {
        "channel": "SPIN-ORBIT (crystal field modulation at Fe3+ site)",
        "lambda_SO_cm": lambda_SO,
        "eta_spin_phonon_cm": eta_spc,
        "eta_spin_phonon_Hz": eta_Hz,
        "g_sp_per_ion_Hz": g_sp_per_ion / (2*np.pi),
        "N_fe_ions": N_fe,
        "g_sp_collective_Hz": g_sp_collective / (2*np.pi),
        "ratio_to_magnetostriction": ratio_to_magnetostriction,
        "C_spin_orbit": C_sp,
        "T1_spin_phonon_s": T1_estimate,
        "C_ratio": C_sp / max(base["C_magnetostrictive"], 1e-99),
        "note": "eta from Raman spectroscopy of Fe3+ oxides (measured values)",
    }


# ─────────────────────────────────────────────
# STACKING: All channels combined
# ─────────────────────────────────────────────

def stacked_channels(base, fe_ppm=100):
    """
    What happens when you combine all channels simultaneously?

    Best strategy:
    1. Use spin-orbit as the base coupling (much stronger per ion)
    2. Drive phonons with piezo (mature, efficient)
    3. Use Q amplification (free -- inherent to quartz)
    4. Optional: thermal parametric amplification
    """
    ch_optical = optical_phonon_drive(base)
    ch_acoustic = acoustic_phonon_drive(base)
    ch_thermal = thermal_modulation(base)
    ch_piezo = piezo_drive(base)
    ch_spinorbit = spin_orbit_coupling(base, fe_ppm)

    # Strategy A: Piezo-driven phonons + spin-orbit coupling
    n_piezo = ch_piezo["n_driven_phonons"]
    g_sp = ch_spinorbit["g_sp_collective_Hz"] * 2 * np.pi
    gamma_m = base["gamma_m_Hz"] * 2 * np.pi
    gamma_b = base["gamma_b_Hz"] * 2 * np.pi

    C_strategy_A = (4 * g_sp**2 * (2 * n_piezo)) / (gamma_m * gamma_b) \
                   if (gamma_m > 0 and gamma_b > 0) else 0
    P_strategy_A = ch_piezo["P_drive_W"]

    # Strategy B: Strategy A + thermal parametric amplification
    parametric = ch_thermal["parametric_gain"]
    C_strategy_B = C_strategy_A * parametric

    # Strategy C: Optical phonon drive + spin-orbit
    n_optical = ch_optical["n_effective"]
    C_strategy_C = (4 * g_sp**2 * (2 * n_optical)) / (gamma_m * gamma_b) \
                   if (gamma_m > 0 and gamma_b > 0) else 0

    # Strategy D: All phonon sources combined + spin-orbit
    n_total = n_piezo + ch_acoustic["n_driven"] + ch_optical["delta_n_phonon"]
    C_strategy_D = (4 * g_sp**2 * (2 * n_total)) / (gamma_m * gamma_b) \
                   if (gamma_m > 0 and gamma_b > 0) else 0

    P_total = ch_piezo["P_drive_W"] + 0.001 + 0.01

    # What voltage is needed for C > 1?
    n_needed = gamma_m * gamma_b / (8 * g_sp**2) if g_sp > 0 else np.inf

    m_eff = 2650 * base["V_m3"]
    d_26 = 3.1e-12
    thickness = base["V_m3"]**(1/3)
    Q = base["Q_mech"]
    omega = base["omega_ph"]

    denom = m_eff * omega * (Q * d_26)**2
    V_needed = np.sqrt(2 * HBAR * n_needed / denom) if denom > 0 else np.inf

    return {
        "individual_channels": {
            "optical": ch_optical,
            "acoustic": ch_acoustic,
            "thermal": ch_thermal,
            "piezo": ch_piezo,
            "spin_orbit": ch_spinorbit,
        },
        "strategies": {
            "A_piezo_plus_spinorbit": {
                "C": C_strategy_A, "P_W": P_strategy_A,
                "desc": "Piezo drive + spin-orbit coupling",
            },
            "B_A_plus_parametric": {
                "C": C_strategy_B, "P_W": P_strategy_A,
                "desc": "Strategy A + thermal parametric amplification",
            },
            "C_optical_plus_spinorbit": {
                "C": C_strategy_C, "P_W": 0.001,
                "desc": "Optical phonon drive + spin-orbit coupling",
            },
            "D_all_combined": {
                "C": C_strategy_D, "P_W": P_total,
                "desc": "All phonon sources + spin-orbit coupling",
            },
        },
        "threshold": {
            "n_phonons_for_C1": n_needed,
            "V_drive_for_C1": V_needed,
            "achievable": V_needed < 100,
        },
    }


if __name__ == "__main__":
    print("=" * 85)
    print("MULTI-CHANNEL COUPLING ENHANCEMENT")
    print("=" * 85)

    base = baseline_magnetostrictive()
    print(f"\n  BASELINE C_magnetostrictive: {base['C_magnetostrictive']:.4e}")

    stacked = stacked_channels(base)
    for key, strat in stacked["strategies"].items():
        marker = " * C > 1!" if strat["C"] > 1 else ""
        print(f"  [{key}] C={strat['C']:.4e}  P={strat['P_W']:.4e} W{marker}")

    thresh = stacked["threshold"]
    print(f"\n  V_drive for C=1: {thresh['V_drive_for_C1']:.4e} V")
    print(f"  Achievable: {thresh['achievable']}")

    print("\n" + "=" * 85)
    print("DONE")
    print("=" * 85)
