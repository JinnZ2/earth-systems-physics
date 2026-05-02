# resonance_amplification_test.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# THE HYPOTHESIS
#   Add energy to a coupled oscillator system -> the system's natural
#   modes get amplified. The 17.5-yr oscillation in seismic + wildfire
#   data was always there, but it becomes DOMINANT as the energy
#   budget rises.
#
#   Therefore: amplitude of the 17.5-yr component in extreme-event
#   time series should correlate with OHC level in the same window.
#
#   More OHC -> bigger oscillation amplitude -> more visible cluster events.
#
# THE TEST
#   1. Bandpass each time series around the 17.5-yr period.
#   2. Compute rolling RMS amplitude in N-year windows.
#   3. Compare to rolling OHC level in the same windows.
#   4. If r(amplitude, OHC) > 0.5 -> energy is amplifying the resonance.
#
# NULL HYPOTHESIS
#   The 17.5-yr signal is incidental. Its amplitude does not depend on
#   OHC. Energy in the system has no effect on the resonance strength.
#
# EDGE CASES
#   - 35 years of annual data is short. Bandpass + windowing reduces
#     effective sample size further. Statistical power is limited.
#   - Uncertainty estimated by bootstrapping over windows.
#   - Result is suggestive, not definitive. Useful as a directional test.
#
# DATA QUALITY NOTE
#   See https://github.com/JinnZ2/thermodynamic-accountability-framework/tree/main/metrology

from __future__ import annotations
import numpy as np

YEARS = np.arange(1990, 2025)
N = len(YEARS)

# Series from prior scripts
EQ_M5 = np.array([
    1617, 1457, 1498, 1426, 1542, 1318, 1222, 1113,  979, 1104,
    1344, 1224, 1201, 1203, 1515, 1693, 1712, 2074, 1768, 1896,
    2209, 2276, 1401, 1453, 1574, 1419, 1550, 1455, 1674, 1492,
    1312, 2047, 1850, 2300, 1374,
])
EQ_M6 = np.array([
    109,  96, 166, 137, 146, 183, 149, 120, 117, 116,
    146, 121, 127, 140, 141, 140, 142, 178, 168, 144,
    150, 185, 108, 123, 143, 127, 130, 104, 117, 135,
    112, 140, 116, 129,  90,
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
OHC = np.array([
    -1.0, -1.5, -3.0, -2.0, -1.5, -1.0, -1.5, -0.5,  1.0,  1.5,
     2.5,  3.0,  3.5,  4.5,  6.0,  7.0,  7.5,  8.0,  9.0, 10.0,
    11.0, 12.5, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0,
    30.0, 32.0, 35.0, 38.0, 40.0,
])


# ─────────────────────────────────────────────
# SIGNAL PROCESSING — pure numpy
# ─────────────────────────────────────────────

def detrend_linear(x):
    x = np.asarray(x, dtype=float)
    t = np.arange(len(x), dtype=float)
    a, b = np.polyfit(t, x, 1)
    return x - (a * t + b)


def bandpass_fft(x, period_low_yr, period_high_yr, dt_yr=1.0):
    """Zero-phase bandpass via FFT mask. Keeps frequencies in
    [1/period_high, 1/period_low]."""
    x = detrend_linear(x)
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, d=dt_yr)
    f_lo = 1.0 / period_high_yr
    f_hi = 1.0 / period_low_yr
    mask = (f >= f_lo) & (f <= f_hi)
    X_filtered = np.where(mask, X, 0)
    return np.fft.irfft(X_filtered, n=n)


def rolling_rms(x, window):
    x = np.asarray(x, dtype=float)
    out = np.empty(len(x) - window + 1)
    for i in range(len(out)):
        seg = x[i:i + window]
        out[i] = np.sqrt(np.mean(seg ** 2))
    return out


def rolling_mean(x, window):
    x = np.asarray(x, dtype=float)
    out = np.empty(len(x) - window + 1)
    for i in range(len(out)):
        out[i] = x[i:i + window].mean()
    return out


def pearson(x, y):
    return float(np.corrcoef(x, y)[0, 1])


def bootstrap_corr_ci(x, y, n_boot=2000, seed=42):
    """Bootstrap 95% CI on Pearson correlation."""
    rng = np.random.default_rng(seed)
    n = len(x)
    rs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        rs[i] = pearson(x[idx], y[idx])
    return float(np.quantile(rs, 0.025)), float(np.quantile(rs, 0.975))


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────

P_CENTER = 17.5
P_LOW    = 12.0
P_HIGH   = 24.0
WINDOW   = 11    # 11-yr rolling window


def run_report():
    series = {
        "EQ_M5":          EQ_M5,
        "EQ_M6":          EQ_M6,
        "EQ_M7":          EQ_M7,
        "named_storms":   NAMED_STORMS,
        "tornadoes":      TORNADO_COUNT,
        "wildfire_acres": ACRES_BURNED,
        "billion_$":      BILLION_DOLLAR,
    }

    print("=" * 76)
    print("RESONANCE AMPLIFICATION TEST")
    print("=" * 76)
    print(f"\n  HYPOTHESIS: 17.5-yr oscillation amplitude scales with OHC.")
    print(f"  Bandpass: {P_LOW}-{P_HIGH} yr (centered on {P_CENTER} yr)")
    print(f"  Rolling RMS window: {WINDOW} yr")
    print(f"  Sample: {N} years (1990-2024)")

    # 1. Bandpass each series
    print("\n" + "-" * 76)
    print("BAND-PASSED 17.5-YR COMPONENT — RMS in full series")
    print("-" * 76)
    print(f"  {'series':<18} {'full RMS':>10}  {'note':<40}")
    bp = {}
    for name, s in series.items():
        b = bandpass_fft(s, P_LOW, P_HIGH)
        bp[name] = b
        rms = float(np.sqrt(np.mean(b ** 2)))
        print(f"  {name:<18} {rms:>10.3f}  bandpassed [{P_LOW}-{P_HIGH}] yr")

    # 2. Rolling amplitude vs rolling OHC
    print("\n" + "-" * 76)
    print(f"AMPLITUDE GROWS WITH OHC?  ({WINDOW}-yr rolling windows)")
    print("-" * 76)
    print("  Pearson r between rolling-RMS(bandpassed_signal) and rolling-mean(OHC).")
    print("  Positive r -> 17.5-yr oscillation grows as OHC rises (hypothesis).")
    print("  Near-zero r -> no relationship (null hypothesis).\n")

    ohc_roll = rolling_mean(OHC, WINDOW)
    print(f"  {'series':<18} {'r':>8} {'95% CI':>20} {'interpretation':<30}")

    results = {}
    for name, b in bp.items():
        amp_roll = rolling_rms(b, WINDOW)
        r = pearson(amp_roll, ohc_roll)
        ci_lo, ci_hi = bootstrap_corr_ci(amp_roll, ohc_roll)
        if r > 0.5 and ci_lo > 0:
            interp = "STRONG amplification"
            mark = "**"
        elif r > 0.3:
            interp = "moderate amplification"
            mark = "* "
        elif r > -0.3:
            interp = "no clear effect"
            mark = "  "
        else:
            interp = "INVERSE (suppression?)"
            mark = "!!"
        results[name] = (r, ci_lo, ci_hi)
        print(f"  {name:<18} {r:>+7.3f}  [{ci_lo:>+5.2f},{ci_hi:>+5.2f}]   "
              f"{mark} {interp}")

    # 3. Energy budget
    print("\n" + "-" * 76)
    print("ENERGY BUDGET — what fraction of total variance is in the 17.5-yr band?")
    print("-" * 76)
    print("  Higher early-vs-late ratio -> resonance growing relative to total noise.\n")
    half = N // 2
    print(f"  {'series':<18} {'early band/total':>17} {'late band/total':>17} "
          f"{'change':>10}")
    for name, s in series.items():
        b = bp[name]
        s_dt = detrend_linear(s)
        var_total_e = np.var(s_dt[:half])
        var_band_e  = np.var(b[:half])
        ratio_e = var_band_e / max(var_total_e, 1e-30)
        var_total_l = np.var(s_dt[half:])
        var_band_l  = np.var(b[half:])
        ratio_l = var_band_l / max(var_total_l, 1e-30)
        change = ratio_l - ratio_e
        if change > 0.10:    flag = "++"
        elif change > 0.03:  flag = "+ "
        elif change < -0.10: flag = "--"
        elif change < -0.03: flag = "- "
        else:                flag = "  "
        print(f"  {name:<18} {ratio_e:>16.3f} {ratio_l:>16.3f} "
              f"{change:>+8.3f} {flag}")

    # 4. Verdict
    print("\n" + "=" * 76)
    print("VERDICT")
    print("=" * 76)
    strong = sum(1 for r, lo, _ in results.values() if r > 0.5 and lo > 0)
    moderate = sum(1 for r, lo, _ in results.values()
                   if r > 0.3 and (lo > 0 or r > 0.5))
    inverse = sum(1 for r, _, hi in results.values() if r < -0.3 and hi < 0)
    null = len(results) - strong - moderate - inverse

    print(f"\n  Of {len(results)} series tested:")
    print(f"    {strong:2d} show STRONG amplification  (r > 0.5, 95% CI excludes 0)")
    print(f"    {moderate:2d} show moderate amplification")
    print(f"    {null:2d} show no clear effect")
    print(f"    {inverse:2d} show INVERSE relationship")

    if strong >= 4:
        print("\n  -> HYPOTHESIS SUPPORTED: 17.5-yr resonance grows with OHC")
        print("     across multiple independent systems.")
    elif strong + moderate >= 4:
        print("\n  -> HYPOTHESIS PARTIALLY SUPPORTED: amplification visible in")
        print("     several series but not all. Statistical-power-limited at N=35.")
    else:
        print("\n  -> HYPOTHESIS NOT CLEARLY SUPPORTED in this dataset.")

    print(
        "\nNOTES ON STATISTICAL POWER:\n"
        "  - 35 years of annual data gives 25 rolling-window samples.\n"
        "  - Bandpass to 17.5-yr period leaves ~2 cycles in the record.\n"
        "  - Bootstrap CIs are wide because of small N.\n"
        "  - Directional test, not proof. Longer records (paleo proxies:\n"
        "    tree rings, varve cores, charcoal layers) would resolve.\n"
    )


if __name__ == "__main__":
    run_report()
