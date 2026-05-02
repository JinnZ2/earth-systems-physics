# phase_lock_detector.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Test whether named-storm cluster years align with PHASE-LOCK
# WINDOWS between the lunar nodal cycle (18.6 yr) and ENSO
# (variable 3-7 yr).
#
# CORE IDEA
#   Two oscillators with different periods drift in/out of phase.
#   When their phase difference d(phi)/dt -> 0 (stays flat for several
#   years), they are PHASE-LOCKED. During lock, their amplitudes ADD
#   constructively. That is when "rogue wave" extremes should cluster.
#
# METHOD
#   1. Generate deterministic lunar nodal cycle (18.6 yr, zero noise).
#   2. Extract ENSO phase from ONI via Hilbert transform (ENSO is
#      irregular - Hilbert gives instantaneous phase from a real
#      signal by constructing the analytic signal).
#   3. Compute phase difference d_phi(t) = phi_lunar(t) - phi_ENSO(t).
#   4. Compute |d(d_phi)/dt|: flat = locked, steep = drifting apart.
#   5. Flag PHASE-LOCK WINDOWS where |d(d_phi)/dt| stays below a
#      threshold for at least 3 consecutive years.
#   6. Test whether named-storm counts spike during lock windows.
#
# DECISION RULE
#   If mean(storms | locked) > mean(storms | unlocked) by Cohen's
#   d >= 0.5 AND cluster years (2005, 2020, 2024) fall in lock
#   windows -> phase-lock mechanism is supported.
#   If not -> frame is wrong, pivot.
#
# DATA SOURCES
#   ONI 1990-2024     : NOAA CPC annual means
#   Storms 1990-2024  : NHC Atlantic Storm Totals Table
#   Lunar nodal       : Meeus, Astronomical Algorithms (J2000 epoch)
#
# DATA QUALITY NOTE
#   Garbage in, garbage out. Phase-lock detection is sensitive to
#   measurement noise and calibration drift in ONI/storm-count
#   records. Calibrated-measurement methodology (instrument bias,
#   detection-threshold drift in NHC records, ONI redefinitions)
#   lives in the companion repository:
#       https://github.com/JinnZ2/thermodynamic-accountability-framework/tree/main/metrology
#   Treat the verdict from this script as conditional on the
#   metrology audit of its inputs.

from __future__ import annotations
import numpy as np

YEARS = np.arange(1990, 2025)
N = len(YEARS)

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────

ONI = np.array([
     0.31,  0.59,  1.18,  0.36,  0.27, -0.14, -0.40,  1.42, -0.61, -1.18,
    -0.65, -0.13,  0.86,  0.29,  0.55, -0.11,  0.46, -0.93, -0.83,  0.43,
     0.21, -0.91, -0.36, -0.34, -0.20,  1.74,  0.34, -0.39,  0.45,  0.50,
    -0.60, -0.91, -0.96,  1.34,  0.40,
])

NAMED_STORMS = np.array([
    14,  8,  7,  8,  7, 19, 13,  8, 14, 12,
    15, 15, 12, 16, 15, 28, 10, 15, 16,  9,
    19, 19, 19, 14,  8, 11, 15, 17, 15, 18,
    30, 21, 14, 20, 18,
])

# Cluster years from prior analysis (>= 4 categories spiked simultaneously)
CLUSTER_YEARS = [2005, 2020, 2024]


# ─────────────────────────────────────────────
# LUNAR NODAL CYCLE
# ─────────────────────────────────────────────

def lunar_nodal_phase(years):
    """
    Lunar ascending node longitude as a continuous, monotonic phase.
    Simplified Meeus formula. The lunar node regresses with period
    18.6128 yr. Reference epoch: J2000.0 (year 2000.0), node at
    ~125.04 deg.
    Sign convention: node regresses (decreases), but we return -Omega
    so phase increases with time, matching standard oscillator form.
    years   : array of decimal years
    returns : phase (rad), increasing monotonically with time
    """
    T = (np.asarray(years, dtype=float) - 2000.0)
    period = 18.6128
    phase = 2.0 * np.pi * T / period
    phase = phase + np.pi * 125.04 / 180.0
    return phase


def lunar_nodal_signal(years):
    """
    Observable cosine of the nodal phase.
    Peaks every 18.6 yr at 'major lunar standstill', when the moon's
    declination range is maximum and tidal asymmetry largest.
    """
    return np.cos(lunar_nodal_phase(years))


# ─────────────────────────────────────────────
# HILBERT TRANSFORM (numpy only, no scipy)
# ─────────────────────────────────────────────

def hilbert_transform(x):
    """
    Analytic signal via FFT-based Hilbert transform.
    The analytic signal is x(t) + i * H[x](t); its argument is the
    instantaneous phase. Implementation: zero out negative
    frequencies in the FFT, double positive frequencies, inverse FFT.
    """
    n = len(x)
    X = np.fft.fft(x)
    h = np.zeros(n)
    if n % 2 == 0:
        h[0] = h[n // 2] = 1
        h[1:n // 2] = 2
    else:
        h[0] = 1
        h[1:(n + 1) // 2] = 2
    return np.fft.ifft(X * h)


def instantaneous_phase(x):
    """Phase of the analytic signal, unwrapped (no 2 pi jumps)."""
    analytic = hilbert_transform(x)
    return np.unwrap(np.angle(analytic))


# ─────────────────────────────────────────────
# PHASE-LOCK DETECTION
# ─────────────────────────────────────────────

def detrend(x):
    """Remove linear trend from a 1-D series."""
    x = np.asarray(x, dtype=float)
    t = np.arange(len(x), dtype=float)
    a, b = np.polyfit(t, x, 1)
    return x - (a * t + b)


def phase_lock_windows(phase_diff, drift_threshold, min_window):
    """
    Identify contiguous regions where |d(phase_diff)/dt| stays below
    drift_threshold for at least min_window consecutive samples.
    phase_diff      : array of phase differences (rad)
    drift_threshold : maximum drift to count as locked (rad/sample)
    min_window      : minimum consecutive locked samples
    returns         : (mask, drift_array) — boolean mask same length
                       as phase_diff, drift array same length
    """
    drift = np.abs(np.diff(phase_diff))
    drift = np.concatenate([drift, [drift[-1]]])  # pad to full length

    locked_pointwise = drift < drift_threshold
    locked_window = np.zeros_like(locked_pointwise)
    run = 0
    for i in range(len(locked_pointwise)):
        if locked_pointwise[i]:
            run += 1
        else:
            if run >= min_window:
                locked_window[i - run:i] = True
            run = 0
    if run >= min_window:
        locked_window[len(locked_pointwise) - run:] = True

    return locked_window, drift


# ─────────────────────────────────────────────
# COUPLING INTERFACE — for module composition
# ─────────────────────────────────────────────

def detect(years=YEARS, oni=ONI, storms=NAMED_STORMS,
           cluster_years=CLUSTER_YEARS,
           drift_factor=0.6, min_window=3):
    """
    Run the phase-lock detector and return a structured result dict.
    Pure function — no printing. Use run_report() for CLI output.
    years         : decimal-year array
    oni           : ONI (Oceanic Nino Index) annual means, same length
    storms        : named-storm counts, same length
    cluster_years : list of years flagged as multi-extreme clusters
    drift_factor  : threshold = drift_factor * median(|d(d_phi)/dt|)
    min_window    : minimum consecutive years to count as locked
    returns       : dict of arrays and statistics
    """
    years = np.asarray(years, dtype=float)
    oni   = np.asarray(oni,   dtype=float)
    storms= np.asarray(storms, dtype=float)

    lunar_signal = lunar_nodal_signal(years)
    lunar_phase  = lunar_nodal_phase(years)
    enso_phase   = instantaneous_phase(detrend(oni))

    phase_diff = lunar_phase - enso_phase
    phase_diff = phase_diff - phase_diff[0]

    drift_all = np.abs(np.diff(phase_diff))
    threshold = float(np.median(drift_all) * drift_factor)
    locked, drift_full = phase_lock_windows(phase_diff,
                                            drift_threshold=threshold,
                                            min_window=min_window)

    # Lock-window boundaries
    windows = []
    in_window = False
    start = None
    for i in range(len(locked)):
        if locked[i] and not in_window:
            start = float(years[i])
            in_window = True
        elif not locked[i] and in_window:
            windows.append((start, float(years[i - 1])))
            in_window = False
    if in_window:
        windows.append((start, float(years[-1])))

    storms_locked   = storms[locked]
    storms_unlocked = storms[~locked]

    cohens_d = 0.0
    m_l = m_u = sd_l = sd_u = 0.0
    if len(storms_locked) > 0 and len(storms_unlocked) > 0:
        m_l, m_u = float(storms_locked.mean()), float(storms_unlocked.mean())
        sd_l, sd_u = float(storms_locked.std()), float(storms_unlocked.std())
        pooled = float(np.sqrt((sd_l ** 2 + sd_u ** 2) / 2))
        cohens_d = (m_l - m_u) / pooled if pooled > 0 else 0.0

    cluster_in_lock = []
    for cy in cluster_years:
        idx_arr = np.where(np.asarray(years, dtype=int) == cy)[0]
        if len(idx_arr) == 0:
            continue
        idx = int(idx_arr[0])
        cluster_in_lock.append((cy, bool(locked[idx]), int(storms[idx])))

    p_chance = float(locked.sum()) / float(len(locked))
    n_in_lock = sum(1 for _, in_lock, _ in cluster_in_lock if in_lock)
    expected_in_lock = p_chance * len(cluster_in_lock)

    return {
        "years":            years,
        "lunar_signal":     lunar_signal,
        "lunar_phase":      lunar_phase,
        "enso_phase":       enso_phase,
        "phase_diff":       phase_diff,
        "drift":            drift_full,
        "threshold":        threshold,
        "locked":           locked,
        "windows":          windows,
        "storms_locked":    storms_locked,
        "storms_unlocked":  storms_unlocked,
        "mean_storms_locked":   m_l,
        "mean_storms_unlocked": m_u,
        "cohens_d":         cohens_d,
        "cluster_in_lock":  cluster_in_lock,
        "n_clusters_in_lock":   n_in_lock,
        "expected_clusters_in_lock": expected_in_lock,
    }


# ─────────────────────────────────────────────
# CLI REPORT
# ─────────────────────────────────────────────

def run_report():
    """Run detect() on the module's bundled series and print a report."""
    print("=" * 78)
    print("PHASE-LOCK DETECTOR  -  lunar nodal x ENSO vs Atlantic storms")
    print("=" * 78)
    print(f"\n  Sample: {N} years (1990-2024)")
    print(f"  Reference oscillator 1: lunar nodal cycle (18.6 yr, deterministic)")
    print(f"  Reference oscillator 2: ENSO via Hilbert phase of ONI")
    print(f"  Test signal: Atlantic named-storm counts\n")

    r = detect()

    print("-" * 78)
    print("PHASE TRAJECTORY")
    print("-" * 78)
    print(f"  {'year':>6} {'lunar cos':>10} {'ENSO phase':>11} "
          f"{'d_phi':>9} {'|drift|':>9} {'locked?':>8} "
          f"{'storms':>7} {'cluster':>8}")
    for i, year in enumerate(YEARS):
        lock_flag    = "LOCK" if r["locked"][i] else "    "
        cluster_flag = "***"  if year in CLUSTER_YEARS else ""
        print(f"  {year:>6} {r['lunar_signal'][i]:>+10.3f} "
              f"{r['enso_phase'][i]:>+11.3f} "
              f"{r['phase_diff'][i]:>+9.3f} {r['drift'][i]:>9.3f} "
              f"{lock_flag:>8} {NAMED_STORMS[i]:>7} {cluster_flag:>8}")

    print("\n" + "-" * 78)
    print("LOCK WINDOWS DETECTED")
    print("-" * 78)
    if not r["windows"]:
        print("  No lock windows detected at this threshold.")
    else:
        for w_start, w_end in r["windows"]:
            mask = (YEARS >= w_start) & (YEARS <= w_end)
            mean_storms = NAMED_STORMS[mask].mean()
            n_clusters = sum(1 for y in CLUSTER_YEARS
                             if w_start <= y <= w_end)
            duration = int(w_end - w_start + 1)
            print(f"  {int(w_start)}-{int(w_end)} ({duration} yr) "
                  f"mean storms = {mean_storms:.1f}  "
                  f"cluster years inside = {n_clusters}")

    print("\n" + "-" * 78)
    print("STORMS DURING LOCK vs NON-LOCK")
    print("-" * 78)
    if len(r["storms_locked"]) > 0 and len(r["storms_unlocked"]) > 0:
        print(f"  Locked years   (n={len(r['storms_locked']):2d}): "
              f"mean = {r['mean_storms_locked']:5.2f}")
        print(f"  Unlocked years (n={len(r['storms_unlocked']):2d}): "
              f"mean = {r['mean_storms_unlocked']:5.2f}")
        print(f"  Difference: "
              f"{r['mean_storms_locked'] - r['mean_storms_unlocked']:+.2f}"
              f" storms/yr")
        print(f"  Cohen's d:  {r['cohens_d']:+.3f}")

        d = r["cohens_d"]
        if d >= 0.5:
            verdict = ">> SUPPORTED  - locked years have notably more storms"
        elif d >= 0.2:
            verdict = ">  marginal effect"
        elif d >= -0.2:
            verdict = "   no detectable effect"
        else:
            verdict = "!! INVERSE    - locked years have FEWER storms"
        print(f"\n  Verdict: {verdict}")

    print("\n" + "-" * 78)
    print("CLUSTER-YEAR ALIGNMENT")
    print("-" * 78)
    for cy, in_lock, storms_cy in r["cluster_in_lock"]:
        flag = "IN LOCK WINDOW" if in_lock else "not in lock window"
        print(f"  {cy}: {flag}  (storms = {storms_cy})")
    print(f"\n  {r['n_clusters_in_lock']}/{len(r['cluster_in_lock'])} "
          f"cluster years fall in lock windows")
    print(f"  Chance expectation: {r['expected_clusters_in_lock']:.2f}/"
          f"{len(r['cluster_in_lock'])}")
    if r["n_clusters_in_lock"] > r["expected_clusters_in_lock"] + 0.5:
        print("  -> Cluster years OVERREPRESENTED in lock windows.")
    elif r["n_clusters_in_lock"] < r["expected_clusters_in_lock"] - 0.5:
        print("  -> Cluster years UNDERREPRESENTED.")
    else:
        print("  -> Distribution roughly matches chance.")

    print("\n" + "=" * 78)
    print("DIAGNOSIS")
    print("=" * 78)
    print(
        "REMINDERS:\n"
        "  - This is a 2-oscillator test. The full hypothesis is\n"
        "    N-oscillator superposition (lunar + ENSO + PDO + AMOC +\n"
        "    solar). Lock windows detected here will be PARTIAL — true\n"
        "    rogue events need more oscillators aligning.\n"
        "  - Hilbert phase on ONI extracts the dominant ENSO mode but\n"
        "    loses sub-annual detail. Lock detection is at year scale.\n"
        "  - 35-yr sample = roughly 2 lunar nodal cycles. Statistical\n"
        "    power is limited. Result is directional, not definitive.\n"
        "  - Conditional on the metrology audit of the input series\n"
        "    (see github.com/JinnZ2/thermodynamic-accountability-\n"
        "    framework/tree/main/metrology).\n"
        "\n"
        "NEXT STEPS IF SUPPORTED:\n"
        "  1. Add PDO + AMOC + solar phases. Compute pairwise lock\n"
        "     matrix.\n"
        "  2. Define 'super-lock' as N >= 3 oscillator pairs locked\n"
        "     simultaneously.\n"
        "  3. Test super-lock windows against MULTI-extreme cluster\n"
        "     years (the original 2005, 2020, 2024 with 4-5 categories\n"
        "     spiking).\n"
        "  4. Predict next super-lock window from forward phase\n"
        "     trajectories.\n"
        "\n"
        "NEXT STEPS IF NOT SUPPORTED:\n"
        "  - Try band-limited phase-lock (only ENSO modes in 4-5 yr\n"
        "    band).\n"
        "  - Or pivot to wavelet coherence (time-frequency localised).\n"
        "  - Or accept that 2-oscillator simple lock is too coarse.\n"
    )
    print("=" * 78)
    print("END")
    print("=" * 78)


if __name__ == "__main__":
    run_report()
