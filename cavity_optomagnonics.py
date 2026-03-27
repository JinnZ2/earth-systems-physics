# cavity_optomagnonics.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Cavity optomagnonics physics engine.
# Three coupled systems: photon <-> magnon <-> phonon
# Covers: microwave cavity magnonics, optical optomagnonics,
# magnomechanics, transduction, dark matter sensitivity.
#
# Depends on: numpy only
# Couples to: magnonic_sublayer.py, layer_0_electromagnetics.py

import numpy as np

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

HBAR    = 1.0545718e-34         # reduced Planck (J*s)
K_B     = 1.380649e-23          # Boltzmann (J/K)
MU_0    = 4 * np.pi * 1e-7     # permeability of free space (T*m/A)
MU_B    = 9.274e-24             # Bohr magneton (J/T)
GAMMA   = 1.7608597e11          # gyromagnetic ratio (rad/s/T)
C_LIGHT = 2.998e8               # speed of light (m/s)
E_CHARGE = 1.602176634e-19      # elementary charge (C)
EPSILON_0 = 8.8541878128e-12    # permittivity of free space (F/m)
M_E     = 9.1093837015e-31      # electron mass (kg)

# ─────────────────────────────────────────────
# CAVITY PHOTON MODE
# ─────────────────────────────────────────────

def cavity_freq_fabry_perot(L_m, mode_n=1):
    """Fabry-Perot cavity: f = n*c/(2L). Returns Hz."""
    return (mode_n * C_LIGHT) / (2 * L_m)


def cavity_freq_wgm(radius_m, n_refract=2.2, mode_l=1):
    """
    Whispering gallery mode estimate.
    f ~ l * c / (2*pi * n * R)
    Returns Hz.
    """
    return (mode_l * C_LIGHT) / (2 * np.pi * n_refract * radius_m)


def cavity_linewidth(f_cav, Q):
    """Total photon loss rate kappa = omega_c / Q. Returns rad/s."""
    return (2 * np.pi * f_cav) / Q


def intracavity_photons(power_W, f_cav, kappa):
    """
    Steady-state intracavity photon number.
    n = P / (hbar * omega_c * kappa)
    """
    omega = 2 * np.pi * f_cav
    if omega <= 0 or kappa <= 0:
        return 0.0
    return power_W / (HBAR * omega * kappa)


# ─────────────────────────────────────────────
# MAGNON MODE (KITTEL)
# ─────────────────────────────────────────────

def kittel_freq(H0, M_s, geometry="sphere"):
    """
    Kittel mode -- uniform precession frequency.
    Sphere:   omega = gamma * mu_0 * (H0 + M_s/3)
    Thin film: omega = gamma * mu_0 * sqrt(H0*(H0 + M_s))
    Returns Hz.
    """
    if geometry == "sphere":
        omega = GAMMA * MU_0 * (H0 + M_s / 3)
    elif geometry == "film":
        omega = GAMMA * MU_0 * np.sqrt(H0 * (H0 + M_s))
    else:
        omega = GAMMA * MU_0 * H0
    return omega / (2 * np.pi)


def magnon_linewidth(alpha, H0, M_s, geometry="sphere"):
    """Magnon linewidth from Gilbert damping: gamma_m = alpha * omega_K. Returns rad/s."""
    omega_K = 2 * np.pi * kittel_freq(H0, M_s, geometry)
    return alpha * omega_K


def total_spin_number(M_s, V_m3, g_factor=2.0):
    """Total spin number S = M_s * V / (g * mu_B)."""
    return (M_s * V_m3) / (g_factor * MU_B)


# ─────────────────────────────────────────────
# PHOTON-MAGNON COUPLING
# ─────────────────────────────────────────────

def coupling_mw_magnetic_dipole(f_cav, V_cav_m3, M_s, V_sphere_m3):
    """
    Microwave regime -- magnetic dipole coupling.
    Single-magnon: g0 = (gamma/2) * sqrt(mu_0 * hbar * omega_c / V_cav)
    Collective: g_eff = g0 * sqrt(2S)
    """
    S = total_spin_number(M_s, V_sphere_m3)
    omega_c = 2 * np.pi * f_cav

    g0 = 0.5 * GAMMA * np.sqrt((MU_0 * HBAR * omega_c) / V_cav_m3)
    g_eff = g0 * np.sqrt(2 * S)

    return {
        "g0_rad_s": g0,
        "g0_Hz": g0 / (2 * np.pi),
        "g_eff_rad_s": g_eff,
        "g_eff_Hz": g_eff / (2 * np.pi),
        "total_spin_S": S,
        "enhancement_factor": np.sqrt(2 * S),
    }


def coupling_optical_faraday(theta_F_deg_per_cm, M_s, V_mode_m3, n_photon,
                             wavelength_m=1.2e-6, n_refract=2.2):
    """
    Optical regime -- Faraday rotation coupling.
    The magnon modulates the dielectric tensor (parametric two-photon process).
    """
    theta_F_rad_per_m = theta_F_deg_per_cm * (np.pi / 180) * 100

    g_single = (theta_F_rad_per_m * C_LIGHT / n_refract) * \
               np.sqrt(HBAR / (2 * M_s * V_mode_m3)) / np.sqrt(V_mode_m3)

    g_enhanced = g_single * np.sqrt(max(n_photon, 1))

    return {
        "g_single_rad_s": g_single,
        "g_single_Hz": g_single / (2 * np.pi),
        "g_enhanced_rad_s": g_enhanced,
        "g_enhanced_Hz": g_enhanced / (2 * np.pi),
        "n_photon": n_photon,
        "theta_F_rad_per_m": theta_F_rad_per_m,
    }


# ─────────────────────────────────────────────
# MAGNON-PHONON COUPLING (MAGNOMECHANICS)
# ─────────────────────────────────────────────

def magnetostrictive_coupling(B_me, M_s, V_m3, omega_mech, rho):
    """
    Magnetostrictive (magnomechanical) coupling.
    g_mb = (B_me / M_s) * x_zpf * omega_b
    where x_zpf = sqrt(hbar / (2 * rho * V * omega_b))
    """
    x_zpf = np.sqrt(HBAR / (2 * rho * V_m3 * omega_mech))
    g_mb = (B_me / M_s) * x_zpf * omega_mech

    return {
        "g_mb_rad_s": g_mb,
        "g_mb_Hz": g_mb / (2 * np.pi),
        "x_zpf_m": x_zpf,
        "omega_mech_Hz": omega_mech / (2 * np.pi),
    }


def phonon_freq_sphere(radius_m, c_sound, mode="breathing"):
    """
    Mechanical resonance of a sphere.
    Breathing mode: f ~ 0.85 * c_sound / (2R)
    """
    if mode == "breathing":
        return 0.85 * c_sound / (2 * radius_m)
    return c_sound / (2 * radius_m)


def phonon_Q_material(material="YIG"):
    """Typical mechanical Q factors."""
    Q_table = {
        "YIG": 5000,
        "quartz": 1e6,
        "quartz_cryo": 1e9,
        "silicon": 1e5,
        "diamond": 1e6,
    }
    return Q_table.get(material, 1000)


# ─────────────────────────────────────────────
# COUPLING REGIME ANALYSIS
# ─────────────────────────────────────────────

def coupling_regime(g_rad_s, kappa_rad_s, gamma_m_rad_s):
    """
    Determine coupling regime from rates.
    Cooperativity: C = 4g^2 / (kappa * gamma_m)
    Strong coupling: g > kappa AND g > gamma_m
    """
    if kappa_rad_s <= 0 or gamma_m_rad_s <= 0:
        return {"cooperativity": 0, "regime": "undefined"}

    C = (4 * g_rad_s**2) / (kappa_rad_s * gamma_m_rad_s)

    ratio_kappa = g_rad_s / kappa_rad_s
    ratio_gamma = g_rad_s / gamma_m_rad_s

    if g_rad_s > kappa_rad_s and g_rad_s > gamma_m_rad_s:
        regime = "strong"
    elif C > 1:
        regime = "cooperativity>1"
    else:
        regime = "weak"

    return {
        "cooperativity": C,
        "regime": regime,
        "g_over_kappa": ratio_kappa,
        "g_over_gamma_m": ratio_gamma,
        "kappa_Hz": kappa_rad_s / (2 * np.pi),
        "gamma_m_Hz": gamma_m_rad_s / (2 * np.pi),
    }


# ─────────────────────────────────────────────
# HYBRID MODES (ANTICROSSING)
# ─────────────────────────────────────────────

def anticrossing_spectrum(f_cav, f_magnon_center, g_Hz, n_points=200):
    """
    Compute hybridized mode frequencies as magnon is swept through cavity.
    omega_pm = (omega_c + omega_m)/2 +/- sqrt(g^2 + delta^2/4)
    """
    results = []
    for i in range(n_points + 1):
        frac = i / n_points
        f_m = f_magnon_center * (0.7 + 0.6 * frac)
        delta = f_cav - f_m
        avg = (f_cav + f_m) / 2
        split = np.sqrt(g_Hz**2 + (delta**2) / 4)
        results.append({
            "H_frac": frac,
            "f_magnon": f_m,
            "f_plus": avg + split,
            "f_minus": avg - split,
            "f_cavity": f_cav,
            "gap_Hz": 2 * split,
            "detuning_Hz": delta,
        })
    return results


# ─────────────────────────────────────────────
# TRANSDUCTION
# ─────────────────────────────────────────────

def mw_to_optical_efficiency(g_mw, kappa_mw, g_opt, kappa_opt, gamma_m):
    """
    Microwave -> magnon -> optical photon conversion.
    eta = C_mw * C_opt / (1 + C_mw + C_opt)^2
    Maximum eta = 1 when C_mw = C_opt >> 1.
    """
    C_mw = (4 * g_mw**2) / (kappa_mw * gamma_m)
    C_opt = (4 * g_opt**2) / (kappa_opt * gamma_m)

    denom = (1 + C_mw + C_opt)**2
    eta = (C_mw * C_opt) / denom if denom > 0 else 0

    return {
        "C_mw": C_mw,
        "C_opt": C_opt,
        "eta": eta,
        "eta_dB": 10 * np.log10(max(eta, 1e-30)),
        "eta_percent": eta * 100,
        "optimal_C_mw_for_unity": 1 + C_opt,
    }


# ─────────────────────────────────────────────
# DARK MATTER SENSITIVITY
# ─────────────────────────────────────────────

def axion_magnon_sensitivity(g_eff_rad_s, kappa_rad_s, gamma_m_rad_s,
                             f_magnon, T, t_integration_s):
    """
    Axion dark matter detection via magnon excitation.
    Axion field couples to magnetization -> drives magnon excitation.
    Detection: single magnon -> cavity photon -> readout.
    """
    omega = 2 * np.pi * f_magnon

    x = (HBAR * omega) / (K_B * T) if T > 0 else 1e10
    n_thermal = 1 / (np.exp(min(x, 500)) - 1) if x < 500 else 0

    C = (4 * g_eff_rad_s**2) / (kappa_rad_s * gamma_m_rad_s)

    rate_limit = min(kappa_rad_s, gamma_m_rad_s) if C > 1 else kappa_rad_s
    snr = (g_eff_rad_s**2 * t_integration_s) / (rate_limit * (n_thermal + 0.5))

    scan_rate_Hz_per_s = gamma_m_rad_s / (2 * np.pi * t_integration_s)

    f_min = kittel_freq(0.01, 1.4e5)
    f_max = kittel_freq(1.0, 1.4e5)

    return {
        "n_thermal": n_thermal,
        "cooperativity": C,
        "snr_estimate": snr,
        "scan_rate_Hz_per_s": scan_rate_Hz_per_s,
        "freq_range_min_Hz": f_min,
        "freq_range_max_Hz": f_max,
        "time_to_scan_full_range_hr": (f_max - f_min) / (scan_rate_Hz_per_s * 3600) if scan_rate_Hz_per_s > 0 else np.inf,
    }


# ─────────────────────────────────────────────
# QUARTZ/Fe DEFECT COMPENSATION ANALYSIS
# ─────────────────────────────────────────────

def quartz_fe_compensation(
    quartz_Q_mech=1e6, quartz_c_sound=5720.0, quartz_rho=2650.0,
    quartz_d_mm=5.0, quartz_thickness_mm=0.1,
    fe_concentration_ppm=100, fe_M_s_per_ppm=1.0,
    fe_alpha=0.1, fe_B_me=1e4,
    H0=0.01, cavity_Q=1e4, T=300.0,
    yig_M_s=1.4e5, yig_alpha=3e-5, yig_B_me=6.96e6,
    yig_Q_mech=5000, yig_rho=5170.0, yig_d_mm=0.25,
):
    """
    Can quartz's superior phonon Q compensate for its much weaker magnetic coupling?
    Returns detailed comparison dict.
    """
    # Quartz geometry
    r_quartz = (quartz_d_mm / 2) * 1e-3
    t_quartz = quartz_thickness_mm * 1e-3
    V_quartz = np.pi * r_quartz**2 * t_quartz

    M_s_quartz = fe_concentration_ppm * fe_M_s_per_ppm

    f_mech_quartz = quartz_c_sound / (2 * t_quartz)
    omega_mech_quartz = 2 * np.pi * f_mech_quartz
    gamma_b_quartz = omega_mech_quartz / quartz_Q_mech

    f_magnon_quartz = kittel_freq(H0, M_s_quartz, geometry="bare")
    gamma_m_quartz = magnon_linewidth(fe_alpha, H0, M_s_quartz, geometry="bare")

    x_zpf_quartz = np.sqrt(HBAR / (2 * quartz_rho * V_quartz * omega_mech_quartz))
    g_mb_quartz = (fe_B_me / max(M_s_quartz, 1)) * x_zpf_quartz * omega_mech_quartz

    C_mb_quartz = (4 * g_mb_quartz**2) / (gamma_m_quartz * gamma_b_quartz) \
                  if (gamma_m_quartz > 0 and gamma_b_quartz > 0) else 0
    tau_phonon_quartz = 1.0 / gamma_b_quartz if gamma_b_quartz > 0 else 0

    # YIG reference
    r_yig = (yig_d_mm / 2) * 1e-3
    V_yig = (4/3) * np.pi * r_yig**3

    f_mech_yig = phonon_freq_sphere(r_yig, 7209.0)
    omega_mech_yig = 2 * np.pi * f_mech_yig
    gamma_b_yig = omega_mech_yig / yig_Q_mech

    f_magnon_yig = kittel_freq(H0, yig_M_s, geometry="sphere")
    gamma_m_yig = magnon_linewidth(yig_alpha, H0, yig_M_s, geometry="sphere")

    x_zpf_yig = np.sqrt(HBAR / (2 * yig_rho * V_yig * omega_mech_yig))
    g_mb_yig = (yig_B_me / yig_M_s) * x_zpf_yig * omega_mech_yig

    C_mb_yig = (4 * g_mb_yig**2) / (gamma_m_yig * gamma_b_yig) \
               if (gamma_m_yig > 0 and gamma_b_yig > 0) else 0
    tau_phonon_yig = 1.0 / gamma_b_yig if gamma_b_yig > 0 else 0

    # Compensation analysis
    coupling_ratio = (g_mb_quartz / g_mb_yig)**2 if g_mb_yig > 0 else 0
    magnon_loss_ratio = gamma_m_yig / gamma_m_quartz if gamma_m_quartz > 0 else 0
    phonon_Q_ratio = quartz_Q_mech / yig_Q_mech
    net_factor = coupling_ratio * magnon_loss_ratio * phonon_Q_ratio

    Q_needed = yig_Q_mech * (C_mb_yig / max(C_mb_quartz * yig_Q_mech / quartz_Q_mech, 1e-30))
    B_me_needed = fe_B_me * np.sqrt(C_mb_yig / max(C_mb_quartz, 1e-30))

    # Piezoelectric advantage
    d_26 = 3.1e-12
    k_sq = 0.0081
    V_piezo_zpf = d_26 * quartz_rho * quartz_c_sound**2 * omega_mech_quartz * x_zpf_quartz
    R_quartz = 10.0
    delta_f = f_mech_quartz / quartz_Q_mech
    V_noise = np.sqrt(4 * K_B * T * R_quartz * delta_f)
    piezo_snr_single_phonon = V_piezo_zpf / V_noise if V_noise > 0 else 0

    # Cryogenic projection
    quartz_Q_cryo = 1e9
    gamma_b_cryo = omega_mech_quartz / quartz_Q_cryo
    C_mb_cryo = (4 * g_mb_quartz**2) / (gamma_m_quartz * gamma_b_cryo) \
                if (gamma_m_quartz > 0 and gamma_b_cryo > 0) else 0
    x_cryo = (HBAR * 2 * np.pi * f_magnon_quartz) / (K_B * 4.0)
    n_thermal_cryo = 1 / (np.exp(min(x_cryo, 500)) - 1) if x_cryo < 500 else 0

    return {
        "quartz": {
            "M_s_A_m": M_s_quartz, "fe_concentration_ppm": fe_concentration_ppm,
            "f_mech_Hz": f_mech_quartz, "Q_mech": quartz_Q_mech,
            "phonon_lifetime_s": tau_phonon_quartz, "f_magnon_Hz": f_magnon_quartz,
            "gamma_m_Hz": gamma_m_quartz / (2 * np.pi),
            "gamma_b_Hz": gamma_b_quartz / (2 * np.pi),
            "g_mb_Hz": g_mb_quartz / (2 * np.pi),
            "x_zpf_m": x_zpf_quartz, "C_magnomech": C_mb_quartz, "V_m3": V_quartz,
        },
        "yig": {
            "M_s_A_m": yig_M_s, "f_mech_Hz": f_mech_yig, "Q_mech": yig_Q_mech,
            "phonon_lifetime_s": tau_phonon_yig, "f_magnon_Hz": f_magnon_yig,
            "gamma_m_Hz": gamma_m_yig / (2 * np.pi),
            "gamma_b_Hz": gamma_b_yig / (2 * np.pi),
            "g_mb_Hz": g_mb_yig / (2 * np.pi),
            "x_zpf_m": x_zpf_yig, "C_magnomech": C_mb_yig, "V_m3": V_yig,
        },
        "compensation": {
            "coupling_ratio_sq": coupling_ratio,
            "magnon_loss_advantage": magnon_loss_ratio,
            "phonon_Q_advantage": phonon_Q_ratio,
            "net_cooperativity_factor": net_factor,
            "quartz_wins": C_mb_quartz > C_mb_yig,
            "C_ratio_quartz_over_yig": C_mb_quartz / max(C_mb_yig, 1e-30),
            "Q_mech_needed_to_match": Q_needed,
            "B_me_needed_to_match_J_m3": B_me_needed,
        },
        "piezo": {
            "k_squared": k_sq, "V_zpf_volts": V_piezo_zpf,
            "V_noise_volts": V_noise, "snr_single_phonon": piezo_snr_single_phonon,
            "piezo_advantage": "DIRECT electrical readout -- no cavity needed",
        },
        "cryo_4K": {
            "Q_mech_cryo": quartz_Q_cryo, "C_magnomech_cryo": C_mb_cryo,
            "C_ratio_cryo_over_yig": C_mb_cryo / max(C_mb_yig, 1e-30),
            "n_thermal_magnon": n_thermal_cryo,
            "phonon_lifetime_s": 1.0 / gamma_b_cryo if gamma_b_cryo > 0 else 0,
        },
    }


# ─────────────────────────────────────────────
# MATERIAL PRESETS
# ─────────────────────────────────────────────

CAVITY_PRESETS = {
    "YIG_MW_sphere": {
        "desc": "Standard: 250um YIG sphere in 3D copper cavity, ~8 GHz",
        "M_s": 1.4e5, "alpha": 3e-5,
        "sphere_d_m": 250e-6,
        "cavity_L_m": 21.5e-3, "cavity_Q": 2000,
        "B_me": 6.96e6, "rho": 5170,
        "c_sound": 7209, "theta_F": 240,
    },
    "YIG_SC_cavity": {
        "desc": "YIG sphere in superconducting cavity, Q ~ 1e6",
        "M_s": 1.4e5, "alpha": 3e-5,
        "sphere_d_m": 250e-6,
        "cavity_L_m": 21.5e-3, "cavity_Q": 1e6,
        "B_me": 6.96e6, "rho": 5170,
        "c_sound": 7209, "theta_F": 240,
    },
}

# ─────────────────────────────────────────────
# FULL COUPLING STATE EXPORT
# ─────────────────────────────────────────────

def optomagnonic_coupling_state(
    H0=0.285, M_s=1.4e5, alpha=3e-5, sphere_d_m=250e-6,
    cavity_L_m=21.5e-3, cavity_Q=2000, B_me=6.96e6, rho=5170.0,
    c_sound=7209.0, theta_F_deg_per_cm=240.0, T=0.020,
    drive_power_W=1e-5, geometry="sphere",
):
    """
    Full optomagnonic state export for coupling to other layers.
    Same interface contract as magnonic_sublayer.magnonic_coupling_state().
    """
    r = sphere_d_m / 2
    V_sphere = (4/3) * np.pi * r**3
    V_cav = cavity_L_m**3 * 0.5

    f_cav = cavity_freq_fabry_perot(cavity_L_m)
    kappa = cavity_linewidth(f_cav, cavity_Q)
    n_cav = intracavity_photons(drive_power_W, f_cav, kappa)

    f_mag = kittel_freq(H0, M_s, geometry)
    gamma_m = magnon_linewidth(alpha, H0, M_s, geometry)

    mw = coupling_mw_magnetic_dipole(f_cav, V_cav, M_s, V_sphere)
    regime = coupling_regime(mw["g_eff_rad_s"], kappa, gamma_m)

    f_mech = phonon_freq_sphere(r, c_sound)
    omega_mech = 2 * np.pi * f_mech
    mech = magnetostrictive_coupling(B_me, M_s, V_sphere, omega_mech, rho)

    V_mode = V_sphere * 0.1
    opt = coupling_optical_faraday(theta_F_deg_per_cm, M_s, V_mode, n_cav)

    trans = mw_to_optical_efficiency(
        mw["g_eff_rad_s"], kappa,
        opt["g_enhanced_rad_s"],
        cavity_linewidth(cavity_freq_wgm(r), 1e6),
        gamma_m,
    )

    dm = axion_magnon_sensitivity(
        mw["g_eff_rad_s"], kappa, gamma_m,
        f_mag, T, 3600,
    )

    return {
        "cavity_freq_Hz": f_cav,
        "cavity_linewidth_Hz": kappa / (2 * np.pi),
        "cavity_Q": cavity_Q,
        "intracavity_photons": n_cav,
        "kittel_freq_Hz": f_mag,
        "magnon_linewidth_Hz": gamma_m / (2 * np.pi),
        "total_spin_S": mw["total_spin_S"],
        "g0_Hz": mw["g0_Hz"],
        "g_eff_Hz": mw["g_eff_Hz"],
        "cooperativity": regime["cooperativity"],
        "coupling_regime": regime["regime"],
        "g_over_kappa": regime["g_over_kappa"],
        "phonon_freq_Hz": f_mech,
        "g_magnomech_Hz": mech["g_mb_Hz"],
        "x_zpf_m": mech["x_zpf_m"],
        "g_optical_single_Hz": opt["g_single_Hz"],
        "g_optical_enhanced_Hz": opt["g_enhanced_Hz"],
        "transduction_eta": trans["eta"],
        "transduction_dB": trans["eta_dB"],
        "dm_sensitivity_snr": dm["snr_estimate"],
        "dm_n_thermal": dm["n_thermal"],
    }


def _fmt(v, width=12):
    if isinstance(v, float):
        if abs(v) == 0:
            return f"{'0':>{width}}"
        if abs(v) > 1e6 or abs(v) < 1e-3:
            return f"{v:>{width}.4e}"
        return f"{v:>{width}.4f}"
    return f"{str(v):>{width}}"


if __name__ == "__main__":
    print("=" * 90)
    print("CAVITY OPTOMAGNONICS -- FULL STATE REPORT")
    print("=" * 90)

    yig_state = optomagnonic_coupling_state()
    print("\n--- YIG Standard (250um sphere, Cu cavity, 20 mK) ---")
    for k, v in yig_state.items():
        print(f"  {k:40s} {_fmt(v)}")

    print("\n" + "=" * 90)
    print("QUARTZ/Fe DEFECT COMPENSATION ANALYSIS")
    print("=" * 90)

    comp = quartz_fe_compensation()
    q = comp["quartz"]
    y = comp["yig"]

    print(f"\n  {'Parameter':40s} {'QUARTZ+Fe':>12s} {'YIG':>12s}")
    print("  " + "-" * 70)
    print(f"  {'Coupling g_mb (Hz)':40s} {_fmt(q['g_mb_Hz'])} {_fmt(y['g_mb_Hz'])}")
    print(f"  {'Mechanical Q':40s} {_fmt(q['Q_mech'])} {_fmt(y['Q_mech'])}")
    print(f"  {'COOPERATIVITY':40s} {_fmt(q['C_magnomech'])} {_fmt(y['C_magnomech'])}")

    c = comp["compensation"]
    print(f"\n  Quartz wins? {c['quartz_wins']}  (ratio: {c['C_ratio_quartz_over_yig']:.2e})")

    print("\n" + "=" * 90)
    print("DONE")
    print("=" * 90)
