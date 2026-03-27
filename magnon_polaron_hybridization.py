# magnon_polaron_hybridization.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# The crossover zone: where magnon and phonon dispersions intersect
# in quartz with iron defect centers.
#
# At this crossing, neither mode is purely spin nor purely lattice.
# The hybrid quasiparticle — the magnon-polaron — inherits
# properties of both: magnetic tunability + mechanical coherence.
#
# This is where the 4-axis coil geometry has maximum leverage.

import numpy as np

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

HBAR    = 1.0545718e-34
K_B     = 1.380649e-23
MU_0    = 4 * np.pi * 1e-7
GAMMA   = 1.7608597e11
MU_B    = 9.274e-24

# ─────────────────────────────────────────────
# QUARTZ PROPERTIES
# ─────────────────────────────────────────────

# AT-cut quartz crystal properties
QUARTZ = {
    "rho": 2650.0,              # kg/m^3
    "c_long": 5720.0,           # longitudinal sound speed m/s
    "c_shear": 3764.0,          # shear sound speed m/s
    "Q_mech_300K": 1e6,         # mechanical Q at 300K
    "Q_mech_77K": 1e7,          # at liquid nitrogen
    "Q_mech_4K": 1e9,           # at liquid helium
    "d_26": 3.1e-12,            # piezoelectric coefficient C/N
    "epsilon_r": 4.5,           # relative permittivity
    "k_sq": 0.0081,             # electromechanical coupling k^2
    "thermal_conductivity": 6.5, # W/(m*K) at 300K
    "debye_temp": 470.0,        # K
}

# Iron defect in quartz
FE_DEFECT = {
    "g_factor": 2.0,            # Lande g-factor for Fe3+
    "S_spin": 5/2,              # spin quantum number Fe3+ (high spin d5)
    "D_zfs_cm": 0.0,            # zero-field splitting (small for Fe3+ in SiO2)
    "linewidth_mT": 50.0,       # ESR linewidth (broad -- site disorder)
}

# ─────────────────────────────────────────────
# DISPERSION RELATIONS
# ─────────────────────────────────────────────

def phonon_dispersion(k, c_sound=5720.0, branch="acoustic"):
    """
    Phonon dispersion: omega = c*k (acoustic branch).
    Linear to zone boundary.
    """
    if branch == "acoustic":
        return c_sound * k
    # Optical branch -- flat with slight dispersion
    omega_opt = 2 * np.pi * 15e12  # ~15 THz SiO2 optical phonon
    return omega_opt - 0.1 * omega_opt * (k / 1e10)**2


def magnon_dispersion_dilute(k, H0, M_s, A_ex, theta_deg=90.0):
    """
    Magnon dispersion for dilute magnetic defects in non-magnetic host.

    Unlike bulk ferromagnets, exchange coupling between Fe3+ sites
    is negligible at low concentration. The "magnon" is really
    localized spin precession with weak k-dependence from
    dipolar coupling.

    At low concentration:
      omega ~ gamma*mu_0*H0 + D_dip*k^2
    where D_dip is a dipolar dispersion coefficient.
    D_dip << exchange dispersion in bulk magnets.
    """
    omega_Z = GAMMA * MU_0 * H0  # Zeeman term (dominant)

    # Dipolar dispersion -- weak, scales with M_s^2
    k_cutoff = 1e8  # lattice cutoff
    D_dip = MU_0 * GAMMA * M_s / (4 * np.pi * k_cutoff)

    theta = np.radians(theta_deg)
    omega = omega_Z + D_dip * k**2 + \
            GAMMA * MU_0 * M_s * np.sin(theta)**2 * 0.001  # tiny dipolar anisotropy

    return omega


def find_crossover(H0, M_s, A_ex, c_sound=5720.0, theta_deg=90.0):
    """
    Find the k-vector where magnon and phonon dispersions cross.

    Phonon: omega = c*k
    Magnon: omega ~ gamma*mu_0*H0 + D*k^2 (approximately flat for dilute spins)

    Crossover: c*k_cross = gamma*mu_0*H0
    -> k_cross = gamma*mu_0*H0 / c

    This is exact for flat magnon dispersion.
    """
    omega_magnon_0 = GAMMA * MU_0 * H0  # band bottom

    # Simple linear crossing
    k_cross = omega_magnon_0 / c_sound
    omega_cross = omega_magnon_0
    f_cross = omega_cross / (2 * np.pi)
    lambda_cross = 2 * np.pi / k_cross if k_cross > 0 else np.inf

    return {
        "k_cross": k_cross,
        "omega_cross": omega_cross,
        "f_cross_Hz": f_cross,
        "lambda_cross_m": lambda_cross,
    }


# ─────────────────────────────────────────────
# MAGNON-POLARON HYBRIDIZATION
# ─────────────────────────────────────────────

def hybridization_gap(H0, M_s, B_me, c_sound=5720.0, rho=2650.0):
    """
    At the magnon-phonon crossover, the coupling opens an ANTICROSSING GAP.

    The gap width Delta is determined by the magnon-phonon coupling strength.

    For magnetostrictive coupling:
      Delta = 2 * |g_mp| where g_mp is the magnon-phonon coupling at k_cross

    The coupling at the crossover is:
      g_mp ~ B_me / M_s * sqrt(hbar k_cross / (2 rho c))

    Returns dict with gap parameters.
    """
    cross = find_crossover(H0, M_s, 0, c_sound)
    k_cross = cross["k_cross"]
    omega_cross = cross["omega_cross"]

    if k_cross <= 0 or M_s <= 0:
        return {"gap_Hz": 0, "gap_rad_s": 0, "hybridization": "none"}

    # Zero-point displacement at crossover k
    lambda_cross = 2 * np.pi / k_cross
    V_mode = lambda_cross**3
    x_zpf = np.sqrt(HBAR / (2 * rho * V_mode * omega_cross))

    # Magnon-phonon coupling at crossover
    g_mp = (B_me / M_s) * x_zpf * omega_cross

    # Gap
    gap_rad = 2 * abs(g_mp)
    gap_Hz = gap_rad / (2 * np.pi)

    return {
        "k_cross": k_cross,
        "f_cross_Hz": omega_cross / (2 * np.pi),
        "lambda_cross_m": lambda_cross,
        "g_mp_rad_s": g_mp,
        "g_mp_Hz": g_mp / (2 * np.pi),
        "gap_rad_s": gap_rad,
        "gap_Hz": gap_Hz,
        "x_zpf_at_cross_m": x_zpf,
        "V_mode_m3": V_mode,
    }


def polaron_spectrum(H0, M_s, B_me, c_sound=5720.0, rho=2650.0,
                     k_range_factor=5.0, n_points=300):
    """
    Compute the full magnon-polaron spectrum around the crossover.

    Upper polaron branch (omega+) and lower polaron branch (omega-):
      omega_pm = (omega_phonon + omega_magnon)/2 +/- sqrt(g^2_mp + delta^2/4)
    where delta = omega_phonon - omega_magnon (detuning at each k)
    """
    cross = find_crossover(H0, M_s, 0, c_sound)
    gap = hybridization_gap(H0, M_s, B_me, c_sound, rho)

    k_cross = cross["k_cross"]
    g_mp = gap["g_mp_rad_s"]

    # Sweep k around crossover
    k_min = k_cross / k_range_factor
    k_max = k_cross * k_range_factor

    k_arr = np.linspace(k_min, k_max, n_points)

    omega_ph = phonon_dispersion(k_arr, c_sound)
    omega_mag = np.array([magnon_dispersion_dilute(k, H0, M_s, 0) for k in k_arr])

    # Hybridized modes
    delta = omega_ph - omega_mag
    avg = (omega_ph + omega_mag) / 2

    split = np.sqrt(g_mp**2 + (delta/2)**2)

    omega_plus = avg + split
    omega_minus = avg - split

    # Magnon fraction of each branch
    magnon_frac_minus = 0.5 * (1 - delta / (2 * split))
    magnon_frac_plus = 0.5 * (1 + delta / (2 * split))

    return {
        "k": k_arr,
        "omega_plus": omega_plus,
        "omega_minus": omega_minus,
        "omega_phonon_bare": omega_ph,
        "omega_magnon_bare": omega_mag,
        "magnon_fraction_plus": magnon_frac_plus,
        "magnon_fraction_minus": magnon_frac_minus,
        "gap_Hz": gap["gap_Hz"],
        "k_cross": k_cross,
    }


# ─────────────────────────────────────────────
# ENERGY EFFICIENCY ANALYSIS
# ─────────────────────────────────────────────

def energy_efficiency_comparison(H0=0.01, fe_ppm=100, T=300.0):
    """
    Compare energy costs of information processing:

    1. Electronic (CMOS):      ~10 fJ/bit
    2. Spintronic (STT-MRAM):  ~100 fJ/bit
    3. Magnonic (YIG):         ~1 aJ/bit (theoretical)
    4. Quartz magnon-polaron:  what we're computing

    The Landauer limit: k_B T ln(2) = 2.87e-21 J at 300K
    """
    M_s = fe_ppm * 1.0  # A/m
    B_me = 1e4  # J/m^3 (estimated)

    cross = find_crossover(H0, M_s, 0)
    omega_op = cross["omega_cross"]
    f_op = cross["f_cross_Hz"]

    # Energy per magnon-polaron excitation
    E_polaron = HBAR * omega_op

    # Landauer limit
    E_landauer = K_B * T * np.log(2)

    # CMOS reference
    E_cmos = 10e-15  # 10 fJ

    # YIG magnonic reference (theoretical best)
    E_yig_magnon = HBAR * 2 * np.pi * 10e9  # 10 GHz magnon

    # Operations per dissipation event
    Q_key = f"Q_mech_{300 if T > 200 else 77 if T > 10 else 4}K"
    Q_mech = QUARTZ[Q_key]
    ops_per_dissipation = Q_mech

    # Effective energy per bit (amortized over Q oscillations)
    E_per_bit_effective = E_polaron / Q_mech

    # Power for continuous operation at f_op
    P_single_mode = E_polaron * f_op
    P_per_bit_rate = E_per_bit_effective * f_op

    # Comparison ratios
    ratio_vs_cmos = E_cmos / E_per_bit_effective
    ratio_vs_landauer = E_per_bit_effective / E_landauer

    # Coil power (4-axis, estimated)
    n_turns = 100
    I_coil = H0 / (MU_0 * n_turns / 0.01)  # 1cm coil
    R_coil = 1.0  # Ohm
    P_coil = I_coil**2 * R_coil

    # Total system power
    P_total = P_single_mode + P_coil

    # Energy harvesting potential
    P_harvest_typical = 50e-6  # W

    # Can the system self-power from ambient vibration?
    self_powered = P_total < P_harvest_typical

    return {
        "crossover_freq_Hz": f_op,
        "E_polaron_J": E_polaron,
        "E_polaron_eV": E_polaron / 1.602e-19,
        "E_landauer_J": E_landauer,
        "E_cmos_J": E_cmos,
        "E_yig_magnon_J": E_yig_magnon,
        "Q_mech": Q_mech,
        "ops_per_dissipation": ops_per_dissipation,
        "E_per_bit_effective_J": E_per_bit_effective,
        "ratio_below_landauer": ratio_vs_landauer,
        "ratio_vs_cmos_advantage": ratio_vs_cmos,
        "P_single_mode_W": P_single_mode,
        "P_coil_W": P_coil,
        "P_total_W": P_total,
        "P_harvest_W": P_harvest_typical,
        "self_powered_possible": self_powered,
        "overhead": {
            "cavity": "NONE -- piezoelectric readout",
            "cryogenics": "NONE at room temp (Q=1e6)",
            "optical_alignment": "NONE",
            "vacuum": "NONE",
            "total_infrastructure": "coil + quartz crystal + wire",
        },
    }


def robustness_analysis(fe_ppm=100, T=300.0):
    """
    Robustness analysis -- how the system degrades under stress.

    Failure modes:
    1. Temperature increase -> Q_mech degrades -> longer dissipation
    2. Field instability -> crossover shifts -> polaron detunes
    3. Crystal damage -> Fe sites disorder -> linewidth broadens
    4. Mechanical shock -> phonon modes shift -> temporary disruption
    """
    M_s = fe_ppm * 1.0
    B_me = 1e4

    results = {}

    # Temperature sweep -- how does Q_mech degrade?
    temps = [4, 20, 77, 150, 300, 400, 500]
    for t in temps:
        if t <= 4:
            Q = 1e9
        elif t <= 77:
            Q = 1e9 * (4/t)**3
        elif t <= 300:
            Q = 1e7 * (77/t)
        else:
            Q = 1e6 * (300/t)**2  # accelerated degradation

        cross = find_crossover(0.01, M_s, 0)
        E_polaron = HBAR * cross["omega_cross"]
        E_per_bit = E_polaron / Q

        results[f"T={t}K"] = {
            "Q_mech": Q,
            "E_per_bit_J": E_per_bit,
            "ops_before_loss": Q,
            "functional": Q > 100,
        }

    # Field stability
    H0 = 0.01
    cross_nominal = find_crossover(H0, M_s, 0)
    gap = hybridization_gap(H0, M_s, B_me)

    delta_H_max = gap["gap_rad_s"] / (2 * GAMMA * MU_0)

    field_stability = {
        "H0_nominal_T": H0,
        "gap_Hz": gap["gap_Hz"],
        "max_field_jitter_T": delta_H_max,
        "max_field_jitter_ppm": delta_H_max / H0 * 1e6,
        "earth_field_variation_T": 5e-5,
        "earth_field_disrupts": 5e-5 > delta_H_max,
    }

    # Graceful degradation profile
    degradation = {
        "mode": "GRACEFUL",
        "reason": ("No cliff edges -- Q degrades smoothly with temperature, "
                   "field detuning reduces efficiency but doesn't crash, "
                   "crystal survives mechanical shock (quartz is hard), "
                   "no vacuum seal to breach, no alignment to lose, "
                   "no superconducting transition to cross."),
        "comparison": {
            "CMOS": "CLIFF -- below V_threshold: dead",
            "optical_cavity": "CLIFF -- alignment lost: dead",
            "SC_qubit": "CLIFF -- above T_c: dead",
            "quartz_polaron": "SLOPE -- degrades proportionally, keeps working",
        },
    }

    return {
        "temperature_sweep": results,
        "field_stability": field_stability,
        "degradation": degradation,
    }


# ─────────────────────────────────────────────
# FULL ANALYSIS
# ─────────────────────────────────────────────

def full_magnon_polaron_analysis(H0=0.01, fe_ppm=100, B_me=1e4, T=300.0):
    """
    Run the complete magnon-polaron analysis for quartz/Fe defects.
    """
    M_s = fe_ppm * 1.0
    A_ex = 1e-14  # negligible

    cross = find_crossover(H0, M_s, A_ex)
    gap = hybridization_gap(H0, M_s, B_me)
    spectrum = polaron_spectrum(H0, M_s, B_me)
    energy = energy_efficiency_comparison(H0, fe_ppm, T)
    robust = robustness_analysis(fe_ppm, T)

    return {
        "crossover": cross,
        "gap": gap,
        "spectrum": spectrum,
        "energy": energy,
        "robustness": robust,
    }


def _fmt(v, w=14):
    if isinstance(v, float):
        if v == 0:
            return f"{'0':>{w}}"
        if abs(v) > 1e6 or abs(v) < 1e-3:
            return f"{v:>{w}.4e}"
        return f"{v:>{w}.6f}"
    if isinstance(v, bool):
        return f"{str(v):>{w}}"
    if isinstance(v, int):
        return f"{v:>{w}d}"
    return f"{str(v):>{w}}"


if __name__ == "__main__":
    print("=" * 80)
    print("MAGNON-POLARON HYBRIDIZATION IN QUARTZ/Fe DEFECTS")
    print("=" * 80)

    result = full_magnon_polaron_analysis()

    c = result["crossover"]
    print(f"\n--- CROSSOVER POINT ---")
    print(f"  k_cross:           {c['k_cross']:.6e} rad/m")
    print(f"  f_cross:           {c['f_cross_Hz']:.6e} Hz")
    print(f"  lambda_cross:      {c['lambda_cross_m']:.6e} m")

    g = result["gap"]
    print(f"\n--- HYBRIDIZATION GAP ---")
    print(f"  g_mp coupling:     {g['g_mp_Hz']:.6e} Hz")
    print(f"  Gap width:         {g['gap_Hz']:.6e} Hz")
    print(f"  x_zpf at cross:    {g['x_zpf_at_cross_m']:.6e} m")
    print(f"  Mode volume:       {g['V_mode_m3']:.6e} m^3")

    e = result["energy"]
    print(f"\n--- ENERGY EFFICIENCY ---")
    print(f"  E per polaron:     {e['E_polaron_J']:.4e} J  ({e['E_polaron_eV']:.4e} eV)")
    print(f"  Landauer limit:    {e['E_landauer_J']:.4e} J")
    print(f"  CMOS per bit:      {e['E_cmos_J']:.4e} J")
    print(f"  Q_mech:            {e['Q_mech']:.4e}")
    print(f"  Effective E/bit:   {e['E_per_bit_effective_J']:.4e} J")
    print(f"  Self-powered:      {e['self_powered_possible']}")

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)
