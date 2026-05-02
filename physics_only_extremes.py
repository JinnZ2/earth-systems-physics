# physics_only_extremes.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Rebuild the extreme-event correlation analysis using ONLY
# physics-based measurements. Strip out the monetary / exposure
# overlay that contaminates both billion-$ counts AND EF tornado
# ratings.
#
# THE MEASUREMENT PROBLEM (documented in SPC literature)
#   1. EF rating: damage-based, not wind-based. Same vortex hitting
#      empty land -> EF0; hitting a city -> EF3. Rating != physics.
#   2. Tornado total count: artificially inflated post-1991 by
#      NEXRAD Doppler deployment (better detection, not more
#      tornadoes). SPC: "annual tornado activity is increasing at
#      almost 15 events per year" — this is OBSERVATIONAL bias.
#   3. Strong+violent tornado count (EF3+): DECREASING by ~1.5 per
#      year since the 1950s. Cleanest physics signal — major
#      tornadoes are too destructive to miss.
#   4. Billion-$ disasters: CPI-adjusted but not EXPOSURE-adjusted.
#      More coastal buildout = more billion-$ events even with
#      constant physics.
#
# CLEANEST PHYSICS PROXIES (used in this script)
#   - Major hurricanes (Cat 3+): well-observed since aircraft +
#     satellite era.
#   - Strong / violent tornadoes (F3+ / EF3+): too destructive to
#     miss.
#   - Wildfire ACRES burned (not count): physical extent, not
#     detection.
#   - Earthquake M6+ count: USGS catalogs, complete since ~1990.
#   - Earthquake M7+ count: complete back to ~1900, very clean.
#   - Named storms: imperfect (some weak ones missed pre-satellite)
#     but acceptable post-1990 in Atlantic basin.
#
# REMOVED FROM ANALYSIS
#   - Total tornado count (EF0/EF1 dominated, observational
#     artifact).
#   - Billion-$ disasters (exposure-confounded).
#   - Total fire count (better land-management reporting, not more
#     fires).
#
# QUESTION
#   Does the 17.5-yr resonance signal survive when we use ONLY
#   exposure-independent, observation-stable physics measurements?
#   YES -> resonance is real Earth-system physics.
#   NO  -> the prior signal was a measurement artifact.
#
# DATA QUALITY NOTE
#   See the companion measurement-system audit (instrument bias,
#   detection-threshold drift, redefinition events) that scopes the
#   validity of these series:
#       https://github.com/JinnZ2/thermodynamic-accountability-framework/tree/main/metrology

from __future__ import annotations
import numpy as np

YEARS = np.arange(1990, 2025)
N = len(YEARS)

# ─────────────────────────────────────────────
# CLEAN PHYSICS SERIES
# Exposure / detection bias minimised.
# ─────────────────────────────────────────────

# Atlantic major hurricanes (Cat 3+). Well-observed since ~1965
# satellite era. Source: NHC HURDAT2.
MAJOR_HURRICANES = np.array([
    1, 2, 1, 1, 0, 5, 6, 1, 3, 5,
    3, 4, 2, 3, 6, 7, 2, 2, 5, 2,
    5, 4, 2, 0, 2, 2, 4, 6, 2, 3,
    7, 4, 2, 3, 5,
])

# US strong+violent tornadoes (EF3+ / F3+). Too destructive to miss.
# Counts are stable across the radar era because EF3+ damage survey
# is unambiguous regardless of population density.
STRONG_TORNADOES = np.array([
    21, 23, 28, 16, 23, 22, 23, 24, 35, 36,    # 1990-1999
    20, 23, 16, 32, 25, 14, 17, 31, 51, 22,    # 2000-2009
    47, 42, 11, 14, 12, 17, 25, 28, 13, 21,    # 2010-2019
    14, 25, 12, 18, 32,                        # 2020-2024
])

# Wildfire acres burned (millions). Physical extent, not detection.
# Source: NIFC TotalFires.pdf
ACRES_BURNED = np.array([
    4.62,  2.95,  2.07,  1.80, 4.07, 1.84, 6.07, 2.86, 1.33, 5.63,
    7.39,  3.57,  7.18,  3.96, 8.10, 8.69, 9.87, 9.33, 5.29, 5.92,
    3.42,  8.71,  9.33,  4.32, 3.60, 10.13, 5.51, 10.03, 8.77, 4.66,
    10.12, 7.13,  7.58,  2.69, 8.92,
])

# Worldwide earthquakes M6+. USGS PDE catalog, complete since 1990.
EQ_M6 = np.array([
    109,  96, 166, 137, 146, 183, 149, 120, 117, 116,
    146, 121, 127, 140, 141, 140, 142, 178, 168, 144,
    150, 185, 108, 123, 143, 127, 130, 104, 117, 135,
    112, 140, 116, 129,  90,
])

# Worldwide earthquakes M7+. Complete back to ~1900; cleanest signal.
EQ_M7 = np.array([
    18, 16, 13, 12, 11, 18, 14, 16, 11, 18,
    14, 15, 13, 14, 14, 10,  9, 14, 12, 16,
    23, 19, 12, 17, 11, 18, 16,  6, 16,  9,
     9, 16, 12, 19, 11,
])

# Atlantic named storms. Reasonable post-satellite (~1965+),
# included as borderline-clean reference.
NAMED_STORMS = np.array([
    14,  8,  7,  8,  7, 19, 13,  8, 14, 12,
    15, 15, 12, 16, 15, 28, 10, 15, 16,  9,
    19, 19, 19, 14,  8, 11, 15, 17, 15, 18,
    30, 21, 14, 20, 18,
])

# ─────────────────────────────────────────────
# CONTAMINATED SERIES
# Kept only for COMPARISON — never as physics evidence.
# ─────────────────────────────────────────────

# Total tornado count (NEXRAD-inflated post-1991).
TORNADO_TOTAL = np.array([
    1133, 1132, 1297, 1176, 1082, 1235, 1170, 1148, 1424, 1342,
    1075, 1213,  934, 1376, 1817, 1265, 1106, 1098, 1692, 1156,
    1282, 1690,  938,  906,  886, 1177,  976, 1418, 1126, 1517,
    1075, 1376, 1331, 1423, 1797,
])

# Billion-$ disasters (exposure-contaminated).
BILLION_DOLLAR = np.array([
     3,  4,  4,  4,  4,  4,  6,  3,  7,  6,
     5,  4,  5,  6,  6, 11,  6,  7, 12,  6,
     9, 16, 11,  9,  8, 10, 15, 16, 14, 14,
    22, 20, 18, 28, 27,
])

# Ocean Heat Content anomaly (10^22 J) — driver test.
OHC = np.array([
    -1.0, -1.5, -3.0, -2.0, -1.5, -1.0, -1.5, -0.5,  1.0,  1.5,
     2.5,  3.0,  3.5,  4.5,  6.0,  7.0,  7.5,  8.0,  9.0, 10.0,
    11.0, 12.5, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0,
    30.0, 32.0, 35.0, 38.0, 40.0,
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
    return (x - x.mean()) / (x.std() + 1e-30)


def pearson(x, y):
    return float(np.corrcoef(x, y)[0, 1])


def trend_slope_per_decade(x):
    """Linear trend in original units per decade."""
    t = np.arange(len(x), dtype=float)
    a, _ = np.polyfit(t, x, 1)
    return a * 10.0


def bandpass_fft(x, period_low_yr, period_high_yr, dt_yr=1.0):
    x = detrend_linear(x)
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, d=dt_yr)
    f_lo = 1.0 / period_high_yr
    f_hi = 1.0 / period_low_yr
    mask = (f >= f_lo) & (f <= f_hi)
    return np.fft.irfft(np.where(mask, X, 0), n=n)


def find_clusters(series_dict, threshold_z=1.0):
    z_dict = {n: zscore(s) for n, s in series_dict.items()}
    clusters = {}
    for i, year in enumerate(YEARS):
        hits = [n for n, z in z_dict.items() if z[i] > threshold_z]
        if len(hits) >= 2:
            clusters[int(year)] = hits
    return clusters


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────

def run_report():
    print("=" * 78)
    print("PHYSICS-ONLY EXTREME ANALYSIS  1990-2024")
    print("=" * 78)
    print("\n  Strips exposure/detection bias from prior analysis.")
    print("  Tests whether the 17.5-yr resonance signal survives in")
    print("  observation-stable, physical-unit measurements only.\n")

    physics_clean = {
        "major_hurricanes": MAJOR_HURRICANES,
        "strong_tornadoes": STRONG_TORNADOES,
        "wildfire_acres":   ACRES_BURNED,
        "EQ_M6":            EQ_M6,
        "EQ_M7":            EQ_M7,
        "named_storms":     NAMED_STORMS,
    }
    contaminated = {
        "tornado_total":  TORNADO_TOTAL,
        "billion_dollar": BILLION_DOLLAR,
    }

    # 1. Linear trends
    print("-" * 78)
    print("LINEAR TRENDS — does the 'acceleration' survive in clean data?")
    print("-" * 78)
    print(f"  {'series':<22} {'category':<14} {'trend/decade':>14} "
          f"{'% of mean':>10}")
    for name, s in physics_clean.items():
        slope = trend_slope_per_decade(s)
        pct = (slope / s.mean()) * 100
        print(f"  {name:<22} {'PHYSICS':<14} "
              f"{slope:>+13.2f}  {pct:>+8.1f}%")
    for name, s in contaminated.items():
        slope = trend_slope_per_decade(s)
        pct = (slope / s.mean()) * 100
        print(f"  {name:<22} {'CONTAMINATED':<14} "
              f"{slope:>+13.2f}  {pct:>+8.1f}%")

    # 2. Correlation matrix
    print("\n" + "-" * 78)
    print("PEARSON CORRELATIONS — physics-clean series only")
    print("-" * 78)
    names = list(physics_clean.keys())
    print(f"  {'':<19}" + "".join(f"{n[:9]:>10}" for n in names))
    for i, ni in enumerate(names):
        row = f"  {ni:<19}"
        for j, nj in enumerate(names):
            r = pearson(physics_clean[ni], physics_clean[nj])
            if i == j:
                row += f"{'  --':>10}"
            else:
                marker = "*" if abs(r) >= 0.4 else " "
                row += f"{r:+.2f}{marker:>5}"
        print(row)
    print("\n  * = |r| >= 0.4 (notable)")

    # 3. Strongest couplings
    print("\n" + "-" * 78)
    print("STRONGEST COUPLINGS in physics-clean data")
    print("-" * 78)
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            r = pearson(physics_clean[names[i]], physics_clean[names[j]])
            pairs.append((abs(r), r, names[i], names[j]))
    pairs.sort(reverse=True)
    for _, r, a, b in pairs[:6]:
        flag = "**" if abs(r) >= 0.5 else ("*" if abs(r) >= 0.3 else " ")
        print(f"  {a:<22} <-> {b:<22}  r = {r:+.3f}  {flag}")

    # 4. Cluster years
    print("\n" + "-" * 78)
    print("CLUSTER YEARS  (z >= 1.0 in 2+ physics-clean series)")
    print("-" * 78)
    clusters_clean  = find_clusters(physics_clean,  threshold_z=1.0)
    clusters_contam = find_clusters({**physics_clean, **contaminated},
                                    threshold_z=1.0)

    print("  CLEAN series only:")
    for year in sorted(clusters_clean.keys()):
        hits = clusters_clean[year]
        print(f"    {year}  ({len(hits)})  : {', '.join(hits)}")

    print("\n  WITH contaminated (for comparison):")
    for year in sorted(clusters_contam.keys()):
        hits = clusters_contam[year]
        n_clean  = sum(1 for h in hits if h in physics_clean)
        n_contam = len(hits) - n_clean
        print(f"    {year}  (clean={n_clean}, contam={n_contam})  : "
              f"{', '.join(hits)}")

    print("\n  Cluster-year frequency by decade:")
    decades = {"1990s": (1990, 1999), "2000s": (2000, 2009),
               "2010s": (2010, 2019), "2020s": (2020, 2024)}
    print(f"    {'decade':<8} {'clean only':>12} {'with contam':>12}")
    for label, (lo, hi) in decades.items():
        n_clean  = sum(1 for y in clusters_clean  if lo <= y <= hi)
        n_contam = sum(1 for y in clusters_contam if lo <= y <= hi)
        yrs = (hi - lo + 1)
        print(f"    {label:<8} {n_clean:>4}/{yrs} ({n_clean/yrs*100:>3.0f}%)"
              f"  {n_contam:>4}/{yrs} ({n_contam/yrs*100:>3.0f}%)")

    # 5. 17.5-yr band power
    print("\n" + "-" * 78)
    print("17.5-YR BAND POWER  (variance in 12-24 yr band / total variance)")
    print("-" * 78)
    print("  If the resonance is real physics, it appears in clean series.")
    print("  If it's exposure-driven, it weakens or disappears.\n")
    print(f"  {'series':<22} {'category':<14} {'band/total':>12}")
    for name, s in physics_clean.items():
        s_dt  = detrend_linear(s)
        bp    = bandpass_fft(s, 12.0, 24.0)
        ratio = np.var(bp) / max(np.var(s_dt), 1e-30)
        flag  = "**" if ratio > 0.3 else ("*" if ratio > 0.15 else " ")
        print(f"  {name:<22} {'PHYSICS':<14} {ratio:>11.3f}  {flag}")
    for name, s in contaminated.items():
        s_dt  = detrend_linear(s)
        bp    = bandpass_fft(s, 12.0, 24.0)
        ratio = np.var(bp) / max(np.var(s_dt), 1e-30)
        flag  = "**" if ratio > 0.3 else ("*" if ratio > 0.15 else " ")
        print(f"  {name:<22} {'CONTAMINATED':<14} {ratio:>11.3f}  {flag}")
    print("\n  ** = strong band concentration (>30% of variance)")
    print("  *  = moderate (>15%)")

    # 6. OHC coupling
    print("\n" + "-" * 78)
    print("OHC COUPLING — does it weaken when we use clean data?")
    print("-" * 78)
    print("  Original finding: OHC <-> billion-$ events  r = +0.92")
    print("  But billion-$ events scale with EXPOSURE, not physics.")
    print("  Clean version below removes exposure overlay:\n")
    print(f"  {'series':<22} {'category':<14} {'r vs OHC':>10}")
    for name, s in physics_clean.items():
        r = pearson(s, OHC)
        flag = "**" if abs(r) >= 0.5 else ("*" if abs(r) >= 0.3 else " ")
        print(f"  {name:<22} {'PHYSICS':<14} {r:>+9.3f}  {flag}")
    for name, s in contaminated.items():
        r = pearson(s, OHC)
        flag = "**" if abs(r) >= 0.5 else ("*" if abs(r) >= 0.3 else " ")
        print(f"  {name:<22} {'CONTAMINATED':<14} {r:>+9.3f}  {flag}")

    # 7. Verdict
    print("\n" + "=" * 78)
    print("DIAGNOSIS")
    print("=" * 78)
    print(
        "INTERPRETATION GUIDE:\n"
        "\n"
        "  [A] If physics-clean series show:\n"
        "      - strong cross-correlations (r >= 0.4)\n"
        "      - cluster-year acceleration (more clusters in 2020s)\n"
        "      - 17.5-yr band power surviving\n"
        "      - OHC correlation persisting (r >= 0.4)\n"
        "      -> Earth-system resonance is REAL physics.\n"
        "      -> Prior 'rogue wave' framing holds.\n"
        "\n"
        "  [B] If physics-clean series show much WEAKER signals than\n"
        "      contaminated series:\n"
        "      -> Most of the apparent acceleration was EXPOSURE-DRIVEN.\n"
        "      -> The Earth system is not entering a new regime.\n"
        "      -> Damage is increasing because we put more in harm's way.\n"
        "      -> Real physics signal exists but is much smaller than\n"
        "         institutional reports suggest.\n"
        "\n"
        "  [C] Hybrid result (some clean signals strong, some weak):\n"
        "      -> Atmospheric extremes (hurricanes, tornadoes) coupled\n"
        "         to OHC via real physics.\n"
        "      -> Damage metrics amplified by exposure.\n"
        "      -> Both stories true at different layers.\n"
        "\n"
        "THE KEY OBSERVATION FROM SPC LITERATURE:\n"
        "  Strong tornadoes (EF3+) have been DECREASING by ~1.5/year\n"
        "  since the 1950s, even as total tornado count appears to rise.\n"
        "  This is the cleanest single test: if the system is forcing\n"
        "  more violent weather, EF3+ should track upward, not down.\n"
        "  It is tracking DOWN. That is a critical falsifier.\n"
        "\n"
        "NEXT STEPS:\n"
        "  1. Add radar-derived peak vorticity (Vrot) when SPC dataset\n"
        "     becomes available — physics-clean tornado intensity (post\n"
        "     2009 only).\n"
        "  2. Add seismic moment release (energy units, not count).\n"
        "  3. Add ACE (Accumulated Cyclone Energy) in place of storm\n"
        "     count.\n"
        "\n"
        "  See github.com/JinnZ2/thermodynamic-accountability-framework\n"
        "  /tree/main/metrology for the measurement audit that scopes\n"
        "  which series are admissible.\n"
    )
    print("=" * 78)
    print("END")
    print("=" * 78)


if __name__ == "__main__":
    run_report()
