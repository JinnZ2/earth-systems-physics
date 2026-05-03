# drivers_analysis.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Test which large-scale climate driver(s) modulate the multi-extreme
# cluster years identified in extremes_correlation.py.
#
# CANDIDATE DRIVERS (annual means, 1990-2024)
#   ONI  : Oceanic Nino Index (NOAA CPC ERSSTv5)
#   AMO  : Atlantic Multidecadal Oscillation (NOAA PSL Kaplan SST)
#   PDO  : Pacific Decadal Oscillation (NOAA NCEI)
#   NAO  : North Atlantic Oscillation (NOAA CPC)
#   AO   : Arctic Oscillation (NOAA CPC)
#   GMST : Global Mean Surface Temp anomaly (NASA GISTEMP v4)
#   OHC  : Ocean Heat Content 0-2000 m anomaly (NOAA NCEI)
#
# QUESTIONS
#   1. Which driver(s) correlate with the seven extreme series?
#   2. Do cluster years share a driver-state signature?
#   3. Is a single common forcing variable identifiable?
#   4. Or do only superpositions trigger clusters?
#
# DATA QUALITY NOTE
#   See https://github.com/JinnZ2/thermodynamic-accountability-framework/tree/main/metrology

from __future__ import annotations
import math
import numpy as np

YEARS = np.arange(1990, 2025)

# ─────────────────────────────────────────────
# EXTREME SERIES  (re-imported from extremes_correlation.py for standalone use)
# ─────────────────────────────────────────────

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
HURRICANES = np.array([
     8,  4,  4,  4,  3, 11,  9,  3, 10,  8,
     8,  9,  4,  7,  9, 15,  5,  6,  8,  3,
    12,  7, 10,  2,  6,  4,  7, 10,  8,  6,
    14,  7,  8,  7, 11,
])
MAJOR_HURRICANES = np.array([
    1, 2, 1, 1, 0, 5, 6, 1, 3, 5,
    3, 4, 2, 3, 6, 7, 2, 2, 5, 2,
    5, 4, 2, 0, 2, 2, 4, 6, 2, 3,
    7, 4, 2, 3, 5,
])
TORNADO_COUNT = np.array([
    1133, 1132, 1297, 1176, 1082, 1235, 1170, 1148, 1424, 1342,
    1075, 1213,  934, 1376, 1817, 1265, 1106, 1098, 1692, 1156,
    1282, 1690,  938,  906,  886, 1177,  976, 1418, 1126, 1517,
    1075, 1376, 1331, 1423, 1797,
])
BILLION_DOLLAR = np.array([
     3,  4,  4,  4,  4,  4,  6,  3,  7,  6,
     5,  4,  5,  6,  6, 11,  6,  7, 12,  6,
     9, 16, 11,  9,  8, 10, 15, 16, 14, 14,
    22, 20, 18, 28, 27,
])

# ─────────────────────────────────────────────
# DRIVER TIME SERIES — annual means 1990-2024
# ─────────────────────────────────────────────

ONI = np.array([
     0.31,  0.59,  1.18,  0.36,  0.27, -0.14, -0.40,  1.42, -0.61, -1.18,
    -0.65, -0.13,  0.86,  0.29,  0.55, -0.11,  0.46, -0.93, -0.83,  0.43,
     0.21, -0.91, -0.36, -0.34, -0.20,  1.74,  0.34, -0.39,  0.45,  0.50,
    -0.60, -0.91, -0.96,  1.34,  0.40,
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

AO = np.array([
     0.61,  0.14,  0.55,  0.77,  0.36, -0.20,  0.02, -0.03,  0.18, -0.37,
    -0.09, -0.31, -0.21,  0.08, -0.17, -0.14, -0.08, -0.07,  0.01, -1.07,
    -1.34,  0.01,  0.36, -0.10,  0.27,  0.99,  0.13, -0.20,  0.27,  0.36,
     0.32,  0.21, -0.15, -0.25,  0.02,
])

GMST = np.array([
     0.45,  0.40,  0.22,  0.23,  0.31,  0.45,  0.33,  0.46,  0.61,  0.39,
     0.40,  0.54,  0.63,  0.62,  0.53,  0.68,  0.63,  0.66,  0.54,  0.66,
     0.72,  0.61,  0.65,  0.68,  0.75,  0.90,  1.02,  0.92,  0.85,  0.98,
     1.02,  0.85,  0.89,  1.17,  1.28,
])

OHC = np.array([
    -1.0, -1.5, -3.0, -2.0, -1.5, -1.0, -1.5, -0.5,  1.0,  1.5,
     2.5,  3.0,  3.5,  4.5,  6.0,  7.0,  7.5,  8.0,  9.0, 10.0,
    11.0, 12.5, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0,
    30.0, 32.0, 35.0, 38.0, 40.0,
])


# ─────────────────────────────────────────────
# STATS HELPERS
# ─────────────────────────────────────────────

def zscore(x):
    x = np.asarray(x, dtype=float)
    return (x - x.mean()) / x.std()


def pearson(x, y):
    return float(np.corrcoef(x, y)[0, 1])


def fisher_p(r, n):
    """Approximate two-sided p-value via Fisher z-transform."""
    if abs(r) >= 0.9999:
        return 0.0
    z = 0.5 * np.log((1 + r) / (1 - r))
    se = 1.0 / np.sqrt(n - 3)
    z_score = abs(z) / se
    return float(2 * (1 - 0.5 * (1 + math.erf(z_score / math.sqrt(2)))))


def lag_corr(x, y, max_lag=3):
    x, y = zscore(x), zscore(y)
    n = len(x)
    best_r, best_lag = 0.0, 0
    for L in range(-max_lag, max_lag + 1):
        if L < 0:
            xs, ys = x[-L:], y[:n + L]
        elif L > 0:
            xs, ys = x[:n - L], y[L:]
        else:
            xs, ys = x, y
        r = float(np.corrcoef(xs, ys)[0, 1])
        if abs(r) > abs(best_r):
            best_r, best_lag = r, L
    return best_r, best_lag


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────

def run_report():
    extremes = {
        "wildfire_acres":   ACRES_BURNED,
        "named_storms":     NAMED_STORMS,
        "hurricanes":       HURRICANES,
        "major_hurricanes": MAJOR_HURRICANES,
        "tornadoes":        TORNADO_COUNT,
        "billion_$_events": BILLION_DOLLAR,
    }
    drivers = {
        "ONI (ENSO)":  ONI,
        "AMO":         AMO,
        "PDO":         PDO,
        "NAO":         NAO,
        "AO":          AO,
        "GMST":        GMST,
        "OHC":         OHC,
    }
    n = len(YEARS)

    print("=" * 76)
    print("DRIVER ANALYSIS — what modulates US extreme weather, 1990-2024")
    print("=" * 76)

    # 1. Zero-lag Pearson
    print("\n" + "-" * 76)
    print("ZERO-LAG CORRELATIONS  driver -> extreme")
    print("-" * 76)
    header = f"  {'driver':<14}"
    for ex in extremes:
        header += f"{ex[:9]:>11}"
    print(header)
    for dn, dv in drivers.items():
        row = f"  {dn:<14}"
        for ex_name, ex_val in extremes.items():
            r = pearson(dv, ex_val)
            mark = "*" if abs(r) >= 0.4 else " "
            row += f"{r:+.2f}{mark:>6}"
        print(row)
    print("\n  * = |r| >= 0.4 (notable)")

    # 2. Best driver per extreme with lag
    print("\n" + "-" * 76)
    print("BEST SINGLE DRIVER for each extreme (with lead/lag in years)")
    print("-" * 76)
    print(f"  {'extreme':<20} {'best driver':<15} {'r':>7} {'lag':>5}  interpretation")
    for ex_name, ex_val in extremes.items():
        best = (0.0, "", 0)
        for dn, dv in drivers.items():
            r, lag = lag_corr(dv, ex_val, max_lag=3)
            if abs(r) > abs(best[0]):
                best = (r, dn, lag)
        r, dn, lag = best
        if lag > 0:
            interp = f"{dn} leads by {lag} yr"
        elif lag < 0:
            interp = f"{ex_name} leads by {-lag} yr"
        else:
            interp = "synchronous"
        print(f"  {ex_name:<20} {dn:<15} {r:+.3f}   {lag:+d}    {interp}")

    # 3. Cluster-year driver signature
    cluster_years = [1996, 2004, 2005, 2006, 2007, 2011, 2017, 2020, 2021, 2024]
    nonclust_years = [y for y in YEARS if y not in cluster_years]

    print("\n" + "-" * 76)
    print("CLUSTER-YEAR DRIVER SIGNATURE")
    print("-" * 76)
    print(f"  Cluster years (n={len(cluster_years)})    : mean driver value")
    print(f"  Non-cluster   (n={len(nonclust_years)})   : mean driver value")
    print( "  Difference / pooled-std = effect size (Cohen's d)\n")
    print(f"  {'driver':<14} {'cluster mean':>13} {'noncluster mean':>17} "
          f"{'diff':>8} {'effect d':>10}")
    for dn, dv in drivers.items():
        cluster_mask  = np.isin(YEARS, cluster_years)
        nonclust_mask = ~cluster_mask
        m_c = dv[cluster_mask].mean()
        m_n = dv[nonclust_mask].mean()
        sd_c = dv[cluster_mask].std()
        sd_n = dv[nonclust_mask].std()
        pooled = np.sqrt((sd_c**2 + sd_n**2) / 2)
        d = (m_c - m_n) / pooled if pooled > 0 else 0
        marker = "*" if abs(d) >= 0.5 else " "
        print(f"  {dn:<14} {m_c:>13.2f} {m_n:>17.2f}  "
              f"{m_c - m_n:>+7.2f}  {d:>+8.2f}  {marker}")
    print("\n  * = |d| >= 0.5 (cluster years have notably different driver state)")

    # 4. Superposition test
    print("\n" + "-" * 76)
    print("SUPERPOSITION TEST")
    print("-" * 76)
    print("  Hypothesis: clusters trigger when MULTIPLE drivers align,")
    print("  not when any single driver hits an extreme value.\n")
    print("  composite_warm = z(GMST) + z(AMO) + z(OHC)\n")

    composite_warm = zscore(GMST) + zscore(AMO) + zscore(OHC)
    cluster_mask = np.isin(YEARS, cluster_years)
    m_c = composite_warm[cluster_mask].mean()
    m_n = composite_warm[~cluster_mask].mean()
    pooled = np.sqrt((composite_warm[cluster_mask].std()**2
                      + composite_warm[~cluster_mask].std()**2) / 2)
    d_warm = (m_c - m_n) / pooled if pooled > 0 else 0
    print(f"  composite_warm in cluster years:    {m_c:+.2f}")
    print(f"  composite_warm in non-cluster yrs:  {m_n:+.2f}")
    print(f"  effect size d:                      {d_warm:+.2f}")

    composite_osc = zscore(ONI) + zscore(NAO) - zscore(PDO)
    m_c2 = composite_osc[cluster_mask].mean()
    m_n2 = composite_osc[~cluster_mask].mean()
    pooled2 = np.sqrt((composite_osc[cluster_mask].std()**2
                       + composite_osc[~cluster_mask].std()**2) / 2)
    d_osc = (m_c2 - m_n2) / pooled2 if pooled2 > 0 else 0
    print()
    print(f"  composite_osc = z(ONI) + z(NAO) - z(PDO)  in clusters:  {m_c2:+.2f}")
    print(f"  composite_osc in non-cluster years:                     {m_n2:+.2f}")
    print(f"  effect size d:                                          {d_osc:+.2f}")

    r_warm_bd = pearson(composite_warm, BILLION_DOLLAR)
    r_osc_bd  = pearson(composite_osc, BILLION_DOLLAR)
    print()
    print(f"  composite_warm  vs billion-$ events:  r = {r_warm_bd:+.3f}")
    print(f"  composite_osc   vs billion-$ events:  r = {r_osc_bd:+.3f}")

    # 5. Driver vs decade
    print("\n" + "-" * 76)
    print("DRIVER vs DECADE: which drivers shifted between decades?")
    print("-" * 76)
    print(f"  {'driver':<14} {'1990s':>10} {'2000s':>10} "
          f"{'2010s':>10} {'2020s':>10} {'shift':>8}")
    decades = [(1990, 1999), (2000, 2009), (2010, 2019), (2020, 2024)]
    for dn, dv in drivers.items():
        means = []
        for lo, hi in decades:
            m = (YEARS >= lo) & (YEARS <= hi)
            means.append(float(dv[m].mean()))
        shift = means[-1] - means[0]
        marker = "*" if abs(shift) > abs(np.std(dv)) else " "
        row = f"  {dn:<14}"
        for m in means:
            row += f"  {m:>+8.2f}"
        row += f"  {shift:>+7.2f}  {marker}"
        print(row)
    print("\n  * = decade-to-decade shift > 1 std of full series")

    print("\n" + "=" * 76)
    print("INTERPRETATION SUMMARY")
    print("=" * 76)
    print(
        "  - ONI/AMO/PDO/NAO/AO are oscillatory; they cycle and do not trend.\n"
        "  - GMST and OHC are trending; they monotonically increase.\n"
        "  - If a single oscillator drove clusters, cluster years would all\n"
        "    share the same phase (e.g. all El Nino years).\n"
        "  - If trending drivers are the issue, cluster frequency should\n"
        "    accelerate monotonically with GMST/OHC — which is what the\n"
        "    60% in 2020s suggests.\n"
        "  - The composite tests check: are clusters phase-locked to\n"
        "    oscillators or amplitude-locked to trends?\n"
    )


if __name__ == "__main__":
    run_report()
