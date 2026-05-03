# extremes_correlation.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Cross-correlation analysis of US extreme weather events 1990-2024.
#
# DATA SOURCES
#   wildfires      : NIFC Total Wildfires PDF (acres burned per year)
#   hurricanes     : NHC Atlantic Storm Totals (named, hurricanes, majors)
#   tornadoes      : SPC WCM (annual US count, NCEI processed)
#   billion-dollar : NOAA NCEI Billion-Dollar Weather and Climate Disasters
#
# QUESTION
#   Are these extreme-event time series independent (institutional
#   assumption) or coupled (resonance pattern)?
#
# METHOD
#   1. Plot raw series side-by-side, normalised
#   2. Pearson correlation matrix (linear coupling)
#   3. Cross-correlation with lag (does one lead another?)
#   4. Year-cluster identification (which years have multiple peaks?)
#   5. Decade comparison: 1990s vs 2000s vs 2010s vs 2020s
#
#   If the institutional model is right: low correlations, no clusters,
#   no regime shift between decades.
#   If the resonance pattern is real: significant correlations, peak
#   clustering, acceleration in cluster frequency post ~2010.
#
# DATA QUALITY NOTE
#   See https://github.com/JinnZ2/thermodynamic-accountability-framework/tree/main/metrology
#   for the input-series audit (NEXRAD inflation of tornado totals,
#   exposure overlay on billion-dollar disasters, etc).

from __future__ import annotations
import numpy as np

YEARS = np.arange(1990, 2025)

# ─────────────────────────────────────────────
# DATA — NOAA / NIFC public sources
# ─────────────────────────────────────────────

ACRES_BURNED = np.array([
    4.62, 2.95, 2.07, 1.80, 4.07, 1.84, 6.07, 2.86, 1.33, 5.63,   # 1990-1999
    7.39, 3.57, 7.18, 3.96, 8.10, 8.69, 9.87, 9.33, 5.29, 5.92,   # 2000-2009
    3.42, 8.71, 9.33, 4.32, 3.60, 10.13, 5.51, 10.03, 8.77, 4.66, # 2010-2019
   10.12, 7.13, 7.58, 2.69, 8.92,                                  # 2020-2024
])

FIRE_COUNT = np.array([
    66.5, 75.8, 87.4, 58.8, 79.1, 82.2, 96.4, 66.2, 81.0, 92.5,   # 1990-1999
    92.3, 84.1, 73.5, 63.6, 65.5, 66.8, 96.4, 85.7, 79.0, 78.8,   # 2000-2009
    72.0, 74.1, 67.8, 47.6, 63.3, 68.2, 67.7, 71.5, 58.1, 50.5,   # 2010-2019
    59.0, 59.0, 69.0, 56.6, 64.9,                                  # 2020-2024
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

BILLION_DOLLAR_DISASTERS = np.array([
     3,  4,  4,  4,  4,  4,  6,  3,  7,  6,
     5,  4,  5,  6,  6, 11,  6,  7, 12,  6,
     9, 16, 11,  9,  8, 10, 15, 16, 14, 14,
    22, 20, 18, 28, 27,
])


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def zscore(x):
    x = np.asarray(x, dtype=float)
    return (x - x.mean()) / x.std()


def pearson(x, y):
    return float(np.corrcoef(x, y)[0, 1])


def cross_corr_lag(x, y, max_lag=5):
    """
    Cross-correlation at lags -max_lag..+max_lag.
    Positive lag => y leads x by 'lag' years.
    Returns (lags, corrs, peak_lag, peak_corr).
    """
    x = zscore(x)
    y = zscore(y)
    n = len(x)
    lags = np.arange(-max_lag, max_lag + 1)
    corrs = []
    for L in lags:
        if L < 0:
            xs, ys = x[-L:], y[:n + L]
        elif L > 0:
            xs, ys = x[:n - L], y[L:]
        else:
            xs, ys = x, y
        corrs.append(float(np.corrcoef(xs, ys)[0, 1]))
    corrs = np.array(corrs)
    pk_idx = int(np.argmax(np.abs(corrs)))
    return lags, corrs, int(lags[pk_idx]), float(corrs[pk_idx])


def find_clusters(series_dict, threshold_z=1.0):
    z_dict = {n: zscore(s) for n, s in series_dict.items()}
    clusters = {}
    for i, year in enumerate(YEARS):
        hits = [n for n, z in z_dict.items() if z[i] > threshold_z]
        if len(hits) >= 2:
            clusters[int(year)] = hits
    return clusters


def decade_stats(series, name):
    decades = {
        "1990s": (1990, 1999),
        "2000s": (2000, 2009),
        "2010s": (2010, 2019),
        "2020s": (2020, 2024),
    }
    out = {}
    for label, (lo, hi) in decades.items():
        mask = (YEARS >= lo) & (YEARS <= hi)
        out[label] = (float(series[mask].mean()), float(series[mask].std()))
    return name, out


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────

def run_report():
    series = {
        "wildfire_acres":   ACRES_BURNED,
        "fire_count":       FIRE_COUNT,
        "named_storms":     NAMED_STORMS,
        "hurricanes":       HURRICANES,
        "major_hurricanes": MAJOR_HURRICANES,
        "tornadoes":        TORNADO_COUNT,
        "billion_$_events": BILLION_DOLLAR_DISASTERS,
    }
    n = len(YEARS)
    names = list(series.keys())

    print("=" * 72)
    print("US EXTREME WEATHER COUPLING ANALYSIS  1990-2024")
    print("=" * 72)
    print("\nSources: NIFC, NHC, SPC/NCEI, NOAA Billion-Dollar Disasters")
    print(f"Sample size: {n} years\n")

    # 1. Pearson correlation matrix
    print("-" * 72)
    print("PEARSON CORRELATION MATRIX (zero-lag)")
    print("-" * 72)
    print(f"{'':<19}" + "".join(f"{nm[:9]:>10}" for nm in names))
    for i, ni in enumerate(names):
        row = f"{ni:<19}"
        for j, nj in enumerate(names):
            r = pearson(series[ni], series[nj])
            if i == j:
                row += f"{'  --':>10}"
            else:
                marker = "*" if abs(r) >= 0.5 else " "
                row += f"{r:+.3f}{marker:>4}"
        print(row)
    print("\n  * = |r| >= 0.5 (strong coupling)")

    # 2. Strongest pairwise
    print("\n" + "-" * 72)
    print("STRONGEST COUPLINGS (sorted by |r|)")
    print("-" * 72)
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            r = pearson(series[names[i]], series[names[j]])
            pairs.append((abs(r), r, names[i], names[j]))
    pairs.sort(reverse=True)
    for _, r, a, b in pairs[:8]:
        print(f"  {a:<20} <-> {b:<20}  r = {r:+.3f}")

    # 3. Cross-correlation with lag
    print("\n" + "-" * 72)
    print("LEAD/LAG ANALYSIS (max correlation at lag in years)")
    print("-" * 72)
    print(f"  {'pair':<45} {'peak lag':>10} {'peak r':>10}")
    for _, r, a, b in pairs[:6]:
        _, _, pk_lag, pk_r = cross_corr_lag(series[a], series[b])
        if pk_lag > 0:
            direction = f"({b} leads by {pk_lag} yr)"
        elif pk_lag < 0:
            direction = f"({a} leads by {-pk_lag} yr)"
        else:
            direction = "(synchronous)"
        print(f"  {a:<22} <-> {b:<22} {pk_lag:+>5d} yr  "
              f"{pk_r:+.3f}  {direction}")

    # 4. Year clusters
    print("\n" + "-" * 72)
    print("CLUSTER YEARS (z >= 1.0 in 2+ series simultaneously)")
    print("-" * 72)
    clusters = find_clusters(series, threshold_z=1.0)
    for year in sorted(clusters.keys()):
        hits = clusters[year]
        print(f"  {year}  ({len(hits)} series)  : {', '.join(hits)}")

    cluster_years = list(clusters.keys())
    cluster_per_decade = {
        "1990s": sum(1 for y in cluster_years if 1990 <= y <= 1999),
        "2000s": sum(1 for y in cluster_years if 2000 <= y <= 2009),
        "2010s": sum(1 for y in cluster_years if 2010 <= y <= 2019),
        "2020s": sum(1 for y in cluster_years if 2020 <= y <= 2024),
    }
    print("\n  Cluster frequency per decade:")
    for decade, count in cluster_per_decade.items():
        years_in_decade = 10 if decade != "2020s" else 5
        rate = count / years_in_decade
        print(f"    {decade}: {count:2d} cluster-years   "
              f"({rate*100:.0f}% of years)")

    # 5. Decade statistics
    print("\n" + "-" * 72)
    print("DECADE STATISTICS (mean +/- std per decade)")
    print("-" * 72)
    print(f"  {'series':<20} {'1990s':>14} {'2000s':>14} "
          f"{'2010s':>14} {'2020s':>14}")
    for nm, s in series.items():
        _, dstats = decade_stats(s, nm)
        row = f"  {nm:<20}"
        for d in ["1990s", "2000s", "2010s", "2020s"]:
            mu, sd = dstats[d]
            row += f"  {mu:6.1f}+-{sd:5.1f}"
        print(row)

    # 6. Variance acceleration
    print("\n" + "-" * 72)
    print("VARIANCE ACCELERATION (std ratio vs 1990s baseline)")
    print("-" * 72)
    print("  -> if > 1: distribution is widening (extremes more extreme)")
    print(f"  {'series':<20} {'2000s/1990s':>14} {'2010s/1990s':>14} "
          f"{'2020s/1990s':>14}")
    for nm, s in series.items():
        _, dstats = decade_stats(s, nm)
        sd90 = dstats["1990s"][1]
        if sd90 == 0:
            continue
        r00 = dstats["2000s"][1] / sd90
        r10 = dstats["2010s"][1] / sd90
        r20 = dstats["2020s"][1] / sd90
        print(f"  {nm:<20}  {r00:13.2f}  {r10:13.2f}  {r20:13.2f}")

    print("\n" + "=" * 72)
    print("END")
    print("=" * 72)


if __name__ == "__main__":
    run_report()
