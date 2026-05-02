# amoc_ohc_interaction_test.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# THE REVISED HYPOTHESIS
#   17.5-yr resonance is amplified by the INTERACTION between OHC and
#   another oscillator (AMOC, PDO, or core/dipole drift).
#   Energy in the system + a phase-modulator -> beat frequency at 17.5 yr.
#   Neither alone amplifies the resonance. The PRODUCT does.
#
# THE TEST
#   1. Build interaction terms:
#        OHC × AMOC      (Atlantic overturning modulation)
#        OHC × PDO       (Pacific decadal oscillation modulation)
#        OHC × dPDO/dt   (rate of PDO change, not the level)
#        OHC × dAMO/dt   (rate of AMO change)
#   2. Bandpass each interaction term around 17.5 yr.
#   3. Compare with bandpassed extreme-event series.
#   4. If correlation is HIGHER for the interaction than for OHC alone,
#      the interaction is the lever.
#
# CAVEAT
#   RAPID AMOC data only goes back to 2004 (21 years of overlap).
#   For 1990-2003 we use a proxy (AMO + NAO regression, Smeed 2014)
#   scaled to RAPID climatology. Pre-2004 values are approximations.
#
# DATA QUALITY NOTE
#   See https://github.com/JinnZ2/thermodynamic-accountability-framework/tree/main/metrology

from __future__ import annotations
import numpy as np

YEARS = np.arange(1990, 2025)
N = len(YEARS)


# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────

EQ_M5 = np.array([
    1617, 1457, 1498, 1426, 1542, 1318, 1222, 1113,  979, 1104,
    1344, 1224, 1201, 1203, 1515, 1693, 1712, 2074, 1768, 1896,
    2209, 2276, 1401, 1453, 1574, 1419, 1550, 1455, 1674, 1492,
    1312, 2047, 1850, 2300, 1374,
])
EQ_M7 = np.array([
    18, 16, 13, 12, 11, 18, 14, 16, 11, 18,
    14, 15, 13, 14, 14, 10,  9, 14, 12, 16,
    23, 19, 12, 17, 11, 18, 16,  6, 16,  9,
     9, 16, 12, 19, 11,
])
ACRES_BURNED = np.array([
    4.62, 2.95, 2.07, 1.80, 4.07, 1.84, 6.07, 2.86, 1.33, 5.63,
    7.39, 3.57, 7.18, 3.96, 8.10, 8.69, 9.87, 9.33, 5.29, 5.92,
    3.42, 8.71, 9.33, 4.32, 3.60, 10.13, 5.51, 10.03, 8.77, 4.66,
   10.12, 7.13, 7.58, 2.69, 8.92,
])
NAMED_STORMS = np.array([
    14,  8,  7,  8,  7, 19, 13,  8, 14, 12,
    15, 15, 12, 16, 15, 28, 10, 15, 16,  9,
    19, 19, 19, 14,  8, 11, 15, 17, 15, 18,
    30, 21, 14, 20, 18,
])
BILLION_DOLLAR = np.array([
     3,  4,  4,  4,  4,  4,  6,  3,  7,  6,
     5,  4,  5,  6,  6, 11,  6,  7, 12,  6,
     9, 16, 11,  9,  8, 10, 15, 16, 14, 14,
    22, 20, 18, 28, 27,
])

OHC = np.array([
    -1.0, -1.5, -3.0, -2.0, -1.5, -1.0, -1.5, -0.5,  1.0,  1.5,
     2.5,  3.0,  3.5,  4.5,  6.0,  7.0,  7.5,  8.0,  9.0, 10.0,
    11.0, 12.5, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0,
    30.0, 32.0, 35.0, 38.0, 40.0,
])
AMO = np.array([
     0.04, -0.04, -0.18, -0.18, -0.06,  0.07, -0.02,  0.03,  0.16,  0.04,
     0.06,  0.16,  0.21,  0.30,  0.20,  0.30,  0.27,  0.16,  0.05,  0.13,
     0.30,  0.10,  0.21,  0.13,  0.17,  0.19,  0.32,  0.26,  0.16,  0.20,
     0.27,  0.21,  0.27,  0.41,  0.45,
])
PDO = np.array([
     0.15,  0.36,  0.96,  1.32,  0.20,  0.05,  0.05, -0.04,  0.36, -1.12,
    -0.15, -0.45, -0.05,  0.35,  0.41,  0.35, -0.07, -0.41, -1.49, -0.79,
    -0.86, -1.09, -1.25, -0.41,  0.81,  1.57,  0.71,  0.00, -0.05,  0.41,
    -0.74, -1.40, -2.00, -2.50, -2.30,
])
NAO = np.array([
     1.05,  0.40,  0.59,  0.76,  0.48,  0.23, -0.27,  0.10,  0.18,  0.32,
     0.22, -0.38, -0.09, -0.04,  0.18,  0.16, -0.21, -0.12,  0.26, -0.69,
    -1.17, -0.23,  0.10,  0.22,  0.30,  0.85,  0.04, -0.05,  0.04,  0.20,
     0.45,  0.21,  0.06, -0.20,  0.00,
])

# RAPID AMOC at 26.5N, annual mean (Sv).
# 1990-2003: AMO+NAO-based proxy reconstruction (Smeed 2014 style),
#            scaled to RAPID climatology (~17 Sv mean).
# 2004-2024: RAPID array annual means (Moat et al. 2024).
AMOC = np.array([
    18.5, 18.0, 18.2, 18.5, 18.1, 18.3, 17.8, 17.9, 17.5, 17.7,
    17.6, 17.2, 17.4, 17.3,
    18.7, 18.5, 18.4, 18.5, 17.5, 14.9, 15.3, 17.0, 17.5, 16.9,
    17.1, 16.6, 16.7, 17.5, 17.0, 17.1, 17.6, 15.9, 15.2, 16.4, 16.5,
])


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def detrend_linear(x):
    x = np.asarray(x, dtype=float)
    t = np.arange(len(x), dtype=float)
    a, b = np.polyfit(t, x, 1)
    return x - (a * t + b)


def zscore(x):
    x = np.asarray(x, dtype=float)
    return (x - x.mean()) / x.std()


def bandpass_fft(x, period_low_yr, period_high_yr, dt_yr=1.0):
    x = detrend_linear(x)
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, d=dt_yr)
    f_lo = 1.0 / period_high_yr
    f_hi = 1.0 / period_low_yr
    mask = (f >= f_lo) & (f <= f_hi)
    return np.fft.irfft(np.where(mask, X, 0), n=n)


def pearson(x, y):
    return float(np.corrcoef(x, y)[0, 1])


def first_diff_pad(x):
    """First difference, padded with mean so length is preserved."""
    d = np.diff(x)
    return np.concatenate([[d.mean()], d])


def build_interactions(ohc, amoc, amo, pdo, nao):
    """OHC times oscillating-component, z-scored so products are dimensionless."""
    z_ohc   = zscore(ohc)
    z_amoc  = zscore(amoc)
    z_amo   = zscore(amo)
    z_pdo   = zscore(pdo)
    z_nao   = zscore(nao)
    z_dpdo  = zscore(first_diff_pad(pdo))
    z_damo  = zscore(first_diff_pad(amo))
    z_damoc = zscore(first_diff_pad(amoc))
    return {
        "OHC alone":       z_ohc,
        "OHC x AMOC":      z_ohc * z_amoc,
        "OHC x AMO":       z_ohc * z_amo,
        "OHC x PDO":       z_ohc * z_pdo,
        "OHC x NAO":       z_ohc * z_nao,
        "OHC x dAMOC/dt":  z_ohc * z_damoc,
        "OHC x dPDO/dt":   z_ohc * z_dpdo,
        "OHC x dAMO/dt":   z_ohc * z_damo,
        "AMOC x PDO":      z_amoc * z_pdo,
        "AMO x NAO":       z_amo * z_nao,
    }


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────

P_LOW  = 12.0
P_HIGH = 24.0


def run_report():
    extremes = {
        "EQ_M5":          EQ_M5,
        "EQ_M7":          EQ_M7,
        "named_storms":   NAMED_STORMS,
        "wildfire_acres": ACRES_BURNED,
        "billion_$":      BILLION_DOLLAR,
    }

    print("=" * 78)
    print("OHC x MODULATOR INTERACTION TEST  for 17.5-yr resonance")
    print("=" * 78)
    print(f"\n  Hypothesis: 17.5-yr signal is amplified by OHC x oscillating_term.")
    print(f"  Bandpass: {P_LOW}-{P_HIGH} yr.")
    print(f"  Sample: {N} years (1990-2024).")
    print(f"  AMOC: RAPID array 2004+, AMO/NAO proxy 1990-2003.\n")

    interactions = build_interactions(OHC, AMOC, AMO, PDO, NAO)

    bp_inter = {name: bandpass_fft(v, P_LOW, P_HIGH)
                for name, v in interactions.items()}
    bp_ext = {name: bandpass_fft(v, P_LOW, P_HIGH)
              for name, v in extremes.items()}

    inter_names = list(interactions.keys())
    ext_names   = list(extremes.keys())

    # 1. Correlation matrix
    print("-" * 78)
    print("CORRELATION:  bandpassed(interaction)  vs  bandpassed(extreme)")
    print("-" * 78)
    print("  Higher r -> that interaction term explains the 17.5-yr signal in the extreme.")
    print("  Compare each row to 'OHC alone' baseline.\n")
    header = f"  {'interaction':<22}"
    for en in ext_names:
        header += f"{en[:11]:>13}"
    print(header)
    print("  " + "-" * 76)
    for in_n in inter_names:
        row = f"  {in_n:<22}"
        for en in ext_names:
            r = pearson(bp_inter[in_n], bp_ext[en])
            if abs(r) >= 0.6:
                row += f"{r:+.2f}** " + "    "
            elif abs(r) >= 0.4:
                row += f"{r:+.2f}*  " + "    "
            else:
                row += f"{r:+.2f}   " + "    "
        print(row)
    print("\n  ** = |r| >= 0.6 (strong)   * = |r| >= 0.4 (notable)")

    # 2. Improvement over OHC alone
    print("\n" + "-" * 78)
    print("IMPROVEMENT OVER 'OHC ALONE' BASELINE")
    print("-" * 78)
    print("  For each extreme, find the interaction that beats OHC alone the most.\n")
    print(f"  {'extreme':<20} {'best interaction':<22} {'r_inter':>8} "
          f"{'r_OHC':>8} {'gain':>7}")
    print("  " + "-" * 76)
    for en in ext_names:
        bp_e = bp_ext[en]
        r_baseline = pearson(bp_inter["OHC alone"], bp_e)
        best_name = "OHC alone"
        best_r = r_baseline
        for in_n in inter_names:
            if in_n == "OHC alone":
                continue
            r = pearson(bp_inter[in_n], bp_e)
            if abs(r) > abs(best_r):
                best_r = r
                best_name = in_n
        gain = abs(best_r) - abs(r_baseline)
        if gain > 0.3:   flag = "++"
        elif gain > 0.1: flag = "+ "
        else:            flag = "  "
        print(f"  {en:<20} {best_name:<22} {best_r:>+7.3f}  "
              f"{r_baseline:>+7.3f}  {gain:>+6.3f} {flag}")

    # 3. Average across extremes
    print("\n" + "-" * 78)
    print("AVERAGE PERFORMANCE ACROSS ALL EXTREMES")
    print("-" * 78)
    print("  Mean |r| of each interaction term against all 5 extreme series.\n")
    mean_perf = {}
    for in_n in inter_names:
        rs = [abs(pearson(bp_inter[in_n], bp_ext[en])) for en in ext_names]
        mean_perf[in_n] = float(np.mean(rs))
    sorted_perf = sorted(mean_perf.items(), key=lambda kv: -kv[1])
    print(f"  {'rank':>4}  {'interaction':<22} {'mean |r|':>10}")
    for rank, (n, p) in enumerate(sorted_perf, 1):
        flag = " <- BEST" if rank == 1 else ""
        baseline_flag = " (baseline)" if n == "OHC alone" else ""
        print(f"  {rank:>4}  {n:<22} {p:>10.3f}{flag}{baseline_flag}")

    # 4. Verdict
    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    best_name, best_perf = sorted_perf[0]
    baseline_perf = mean_perf["OHC alone"]
    gain = best_perf - baseline_perf
    if best_name == "OHC alone":
        print("\n  -> No interaction beats OHC alone. The 'OHC x X' hypothesis")
        print("     is NOT supported in this dataset.")
    elif gain > 0.15:
        print("\n  -> INTERACTION HYPOTHESIS SUPPORTED.")
        print(f"     '{best_name}' explains the 17.5-yr signal better than OHC alone")
        print(f"     by Δr = +{gain:.3f}.")
    elif gain > 0.05:
        print("\n  -> INTERACTION HYPOTHESIS WEAKLY SUPPORTED.")
        print(f"     '{best_name}' edges out OHC alone (Δr = +{gain:.3f}),")
        print( "     but the gain is small at this sample size.")
    else:
        print("\n  -> INTERACTION HYPOTHESIS NOT CLEARLY SUPPORTED.")
        print(f"     Best interaction '{best_name}' barely beats OHC alone")
        print(f"     (Δr = +{gain:.3f}). At 35 yr of data, can't distinguish.")

    print(
        "\nCAVEATS:\n"
        "  - AMOC pre-2004 is a proxy reconstruction, not direct measurement.\n"
        "  - 35 yr is short for testing 17.5-yr resonance.\n"
        "  - Bandpass + product operations compound noise.\n"
        "  - Result is directional, not definitive.\n"
        "\n"
        "IF THE WINNING INTERACTION INVOLVES AMOC:\n"
        "  consistent with AMOC phase x OHC level -> Atlantic heat\n"
        "  redistribution drives the 17.5-yr beat through jet-stream\n"
        "  blocking and crustal isostatic adjustment.\n"
        "\n"
        "IF IT INVOLVES PDO or its rate of change:\n"
        "  Pacific reorganization is the lever (matches the strong PDO\n"
        "  drop in the 2020s shown in earlier driver analysis).\n"
    )


if __name__ == "__main__":
    run_report()
