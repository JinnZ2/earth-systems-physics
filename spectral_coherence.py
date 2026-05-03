# spectral_coherence.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Test for resonance coupling: do earthquake and extreme-weather time
# series share spectral structure (common frequencies)?
#
# THE HYPOTHESIS
#   "When enough oscillators get into commensurate frequency ratios,
#    energy stops dissipating and starts pumping between layers.
#    Power output goes nonlinear."
#
#   If true:
#     1. Common dominant frequencies across DIFFERENT system types
#        (atmospheric, oceanic, seismic).
#     2. Phase-locking between them in recent decades that was not
#        there before.
#     3. Possibly increasing coherence over time as OHC drives the
#        coupling stronger.
#   If false (institutional null):
#     Each system has its own characteristic spectrum. Seismic activity
#     governed by tectonic processes uncorrelated with surface forcing.
#
# DATA
#   USGS world earthquake counts M5+, M6+, M7+ : 1990-2024
#   Atlantic named storms                       : 1990-2024
#   US tornadoes                                : 1990-2024
#   US wildfire acres                           : 1990-2024
#   Billion-$ disasters                         : 1990-2024
#   ONI (ENSO)                                  : 1990-2024  [reference oscillator]
#
# METHOD
#   1. Detrend each series (subtract linear trend so we test
#      OSCILLATION, not just shared trend).
#   2. Compute periodogram (FFT power spectrum) for each.
#   3. Identify dominant frequencies.
#   4. Compute pairwise coherence (cross-spectrum / sqrt(power_x * power_y)).
#   5. Compare 1990-2007 vs 2008-2024 (test for increasing coherence).
#
# NOTE ON RESOLVABLE PERIODS
#   35 years of annual data is short. Frequencies resolvable: ~1/35
#   to 1/2 yr. Periods we can see: 2-17 years. ENSO band, decadal
#   oscillations -- yes. Sub-annual or multi-decadal -- no.
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
ACRES_BURNED = np.array([
    4.62, 2.95, 2.07, 1.80, 4.07, 1.84, 6.07, 2.86, 1.33, 5.63,
    7.39, 3.57, 7.18, 3.96, 8.10, 8.69, 9.87, 9.33, 5.29, 5.92,
    3.42, 8.71, 9.33, 4.32, 3.60, 10.13, 5.51, 10.03, 8.77, 4.66,
   10.12, 7.13, 7.58, 2.69, 8.92,
])
BILLION_DOLLAR = np.array([
     3,  4,  4,  4,  4,  4,  6,  3,  7,  6,
     5,  4,  5,  6,  6, 11,  6,  7, 12,  6,
     9, 16, 11,  9,  8, 10, 15, 16, 14, 14,
    22, 20, 18, 28, 27,
])
ONI = np.array([
     0.31,  0.59,  1.18,  0.36,  0.27, -0.14, -0.40,  1.42, -0.61, -1.18,
    -0.65, -0.13,  0.86,  0.29,  0.55, -0.11,  0.46, -0.93, -0.83,  0.43,
     0.21, -0.91, -0.36, -0.34, -0.20,  1.74,  0.34, -0.39,  0.45,  0.50,
    -0.60, -0.91, -0.96,  1.34,  0.40,
])


# ─────────────────────────────────────────────
# SPECTRAL HELPERS — pure numpy
# ─────────────────────────────────────────────

def detrend_linear(x):
    x = np.asarray(x, dtype=float)
    t = np.arange(len(x), dtype=float)
    a, b = np.polyfit(t, x, 1)
    return x - (a * t + b)


def periodogram(x, dt=1.0):
    """One-sided power spectrum. Returns (freqs in 1/yr, power)."""
    x = detrend_linear(x)
    n = len(x)
    w = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n) / (n - 1))
    xw = x * w
    X = np.fft.rfft(xw)
    f = np.fft.rfftfreq(n, d=dt)
    psd = (np.abs(X) ** 2) / (n * (w**2).sum())
    return f, psd


def coherence(x, y, dt=1.0, smooth=2):
    """
    Magnitude-squared coherence between two series.
    smooth=N: moving-average over N adjacent frequency bins so the
    cross-spectrum is meaningful (ergodic estimate).
    Returns (freqs, coh in [0,1]).
    """
    x = detrend_linear(x)
    y = detrend_linear(y)
    n = len(x)
    w = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n) / (n - 1))
    X = np.fft.rfft(x * w)
    Y = np.fft.rfft(y * w)
    f = np.fft.rfftfreq(n, d=dt)

    Pxx = np.abs(X) ** 2
    Pyy = np.abs(Y) ** 2
    Pxy = X * np.conj(Y)

    def boxcar(a, k):
        if k <= 1:
            return a
        kernel = np.ones(k) / k
        return np.convolve(a, kernel, mode="same")

    Pxx_s = boxcar(Pxx, smooth)
    Pyy_s = boxcar(Pyy, smooth)
    Pxy_s_re = boxcar(Pxy.real, smooth)
    Pxy_s_im = boxcar(Pxy.imag, smooth)
    Pxy_s_mag2 = Pxy_s_re ** 2 + Pxy_s_im ** 2

    coh = Pxy_s_mag2 / np.maximum(Pxx_s * Pyy_s, 1e-30)
    return f, coh


def dominant_freqs(f, psd, n_top=3):
    """Top-N frequencies sorted by power (skip f=0)."""
    idx = np.argsort(psd[1:])[::-1][:n_top] + 1
    return [(float(f[i]), float(psd[i])) for i in idx]


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────

def run_report():
    series = {
        "EQ_M5":          EQ_M5,
        "EQ_M6":          EQ_M6,
        "EQ_M7":          EQ_M7,
        "named_storms":   NAMED_STORMS,
        "tornadoes":      TORNADO_COUNT,
        "wildfire_acres": ACRES_BURNED,
        "billion_$":      BILLION_DOLLAR,
        "ONI":            ONI,
    }

    print("=" * 76)
    print("SPECTRAL COHERENCE ANALYSIS — earth-system resonance test")
    print("=" * 76)
    print(f"\n  Sample: {N} years (1990-2024). Resolvable periods: 2-17 yr.")
    print(f"  Each series detrended (linear) so we test OSCILLATION not trend.")

    # 1. Dominant frequencies
    print("\n" + "-" * 76)
    print("DOMINANT PERIODS  (top 3 by power, after detrending)")
    print("-" * 76)
    print(f"  {'series':<18} {'period 1':>12} {'period 2':>12} {'period 3':>12}")

    dom_freqs_by_series = {}
    for name, s in series.items():
        f, psd = periodogram(s)
        top = dominant_freqs(f, psd, n_top=3)
        dom_freqs_by_series[name] = [tf[0] for tf in top]
        cells = []
        for fr, _ in top:
            cells.append(f"{1.0/fr:>6.1f} yr" if fr > 0 else "    inf")
        print(f"  {name:<18} {cells[0]:>12} {cells[1]:>12} {cells[2]:>12}")

    # 2. Shared-frequency matrix
    print("\n" + "-" * 76)
    print("SHARED DOMINANT PERIODS  (within +/- 15% tolerance)")
    print("-" * 76)
    print("  Pairs that have a dominant period in common —")
    print("  candidate for resonance coupling.\n")

    names = list(series.keys())
    shared = {n: set() for n in names}
    for i, ni in enumerate(names):
        for j, nj in enumerate(names):
            if i >= j:
                continue
            for fi in dom_freqs_by_series[ni]:
                for fj in dom_freqs_by_series[nj]:
                    if fi == 0 or fj == 0:
                        continue
                    if abs(fi - fj) / max(fi, fj) < 0.15:
                        period = 1.0 / fi
                        shared[ni].add((nj, round(period, 1)))
                        shared[nj].add((ni, round(period, 1)))

    for n, partners in shared.items():
        if partners:
            entries = sorted(partners, key=lambda x: x[1])
            entry_strs = [f"{p[0]}@{p[1]}yr" for p in entries]
            print(f"  {n:<18} shares period with: {', '.join(entry_strs)}")
        else:
            print(f"  {n:<18} no shared dominant periods")

    # 3. Band-averaged coherence
    print("\n" + "-" * 76)
    print("BAND-AVERAGED COHERENCE")
    print("-" * 76)
    print("  ENSO band:    period 3-7 yr   (frequencies 1/7..1/3 per yr)")
    print("  Decadal band: period 8-15 yr  (frequencies 1/15..1/8 per yr)")
    print("  Coherence range [0,1].  >0.5 = strong common oscillation.\n")

    def band_coh(s1, s2, period_lo, period_hi):
        f, c = coherence(s1, s2, smooth=3)
        f_lo = 1.0 / period_hi
        f_hi = 1.0 / period_lo
        m = (f >= f_lo) & (f <= f_hi)
        return float(c[m].mean()) if m.any() else 0.0

    print("  Coherence with ONI (ENSO oscillator):")
    print(f"  {'series':<18} {'ENSO band':>12} {'decadal band':>15}")
    for name, s in series.items():
        if name == "ONI":
            continue
        c_enso = band_coh(s, ONI, 3, 7)
        c_dec  = band_coh(s, ONI, 8, 15)
        flag_e = "*" if c_enso >= 0.5 else " "
        flag_d = "*" if c_dec  >= 0.5 else " "
        print(f"  {name:<18} {c_enso:>10.2f} {flag_e}  "
              f"{c_dec:>13.2f} {flag_d}")

    print("\n  Cross-system coherence (seismic vs atmospheric):")
    print(f"  {'pair':<32} {'ENSO band':>12} {'decadal band':>15}")
    seismic = ["EQ_M5", "EQ_M6", "EQ_M7"]
    atmos = ["named_storms", "tornadoes", "wildfire_acres", "billion_$"]
    for sn in seismic:
        for an in atmos:
            c_enso = band_coh(series[sn], series[an], 3, 7)
            c_dec  = band_coh(series[sn], series[an], 8, 15)
            flag_e = "*" if c_enso >= 0.5 else " "
            flag_d = "*" if c_dec  >= 0.5 else " "
            print(f"  {sn:<10} <-> {an:<18} {c_enso:>10.2f} {flag_e}  "
                  f"{c_dec:>13.2f} {flag_d}")

    # 4. Epoch comparison
    print("\n" + "-" * 76)
    print("EPOCH COMPARISON  early (1990-2006) vs late (2007-2024)")
    print("-" * 76)
    print("  Question: are systems becoming MORE coherent over time?")
    print()

    early_idx = (YEARS <= 2006)
    late_idx  = (YEARS >= 2007)

    def epoch_coh(s1, s2, idx, period_lo, period_hi):
        a = s1[idx]
        b = s2[idx]
        if len(a) < 8:
            return 0.0
        f, c = coherence(a, b, smooth=2)
        f_lo = 1.0 / period_hi
        f_hi = 1.0 / period_lo
        m = (f >= f_lo) & (f <= f_hi)
        return float(c[m].mean()) if m.any() else 0.0

    pairs_to_test = [
        ("EQ_M6",        "named_storms"),
        ("EQ_M6",        "tornadoes"),
        ("EQ_M7",        "named_storms"),
        ("EQ_M5",        "wildfire_acres"),
        ("EQ_M5",        "billion_$"),
        ("named_storms", "wildfire_acres"),
        ("named_storms", "billion_$"),
        ("tornadoes",    "wildfire_acres"),
    ]

    print(f"  {'pair':<35} {'early ENSO':>12} {'late ENSO':>12} {'shift':>8}")
    for a, b in pairs_to_test:
        c_e = epoch_coh(series[a], series[b], early_idx, 3, 7)
        c_l = epoch_coh(series[a], series[b], late_idx,  3, 7)
        shift = c_l - c_e
        if shift > 0.2:    flag = "++"
        elif shift > 0.05: flag = "+ "
        elif shift < -0.2: flag = "--"
        elif shift < -0.05:flag = "- "
        else:              flag = "  "
        print(f"  {a:<14} <-> {b:<18} {c_e:>10.2f}   {c_l:>10.2f}   "
              f"{shift:>+5.2f} {flag}")

    print("\n" + "=" * 76)
    print("INTERPRETATION GUIDE")
    print("=" * 76)
    print(
        "COUPLING SIGNATURE (resonance hypothesis):\n"
        "  - Earth-system extremes share dominant periods.\n"
        "  - Seismic AND atmospheric series both show ENSO-band power.\n"
        "  - Coherence INCREASING in late epoch (2007-2024 vs 1990-2006).\n"
        "  -> consistent with resonance coupling activating as OHC rises\n"
        "\n"
        "NULL HYPOTHESIS (institutional model):\n"
        "  - Each system has independent characteristic periods.\n"
        "  - Seismic uncorrelated with atmospheric/oceanic forcing.\n"
        "  - No shift in coherence over time.\n"
        "  -> systems decoupled, current methods adequate\n"
        "\n"
        "Look for ENSO-band coherence > 0.5 (marked *) between systems\n"
        "that institutional models treat as independent (e.g. EQ_M6 vs\n"
        "named_storms). And look for ++ in the epoch comparison column —\n"
        "those mean coupling has grown stronger in the past 18 years.\n"
    )


if __name__ == "__main__":
    run_report()
