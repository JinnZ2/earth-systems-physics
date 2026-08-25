#!/usr/bin/env python3
# boreal_recovery_ratchet.py
# earth-systems-physics / Layer 6 (biosphere)
# Kicked-relaxor: clear-cut rotation forcing vs community recovery time,
# with legacy-stock ratchet that makes recovery time state-dependent.
# Seeded from Macdonald & McIntosh et al., Nature Sustainability 2026
#   DOI 10.1038/s41893-026-01868-x  (190-dataset boreal/hemiboreal meta-analysis)
# CC0. stdlib only.

import copy
import math

# ── CONSTRAINTS ──────────────────────────────────────────────
# tau   recovery time to mature-forest community composition [yr]
# T     harvest rotation period [yr]              (managed forcing)
# r     community fraction retained at each cut   (0<r<1; refugia/retention)
# L     landscape legacy stock 0..1               (CWD + propagule sources)
#       tau_eff = tau / L   ← RATCHET: L falls, recovery slows
# state tracked = RECOVERED (pre-cut) composition fraction x/A
# ─────────────────────────────────────────────────────────────

# conifer-forest recovery times from the meta-analysis
MODES = {
    "broadleaf_community": dict(tau=30.0,  A=1.0, r=0.15),
    "small_mammals":       dict(tau=55.0,  A=1.0, r=0.15),
    "vascular_plants":     dict(tau=85.0,  A=1.0, r=0.15),
    "lichens":             dict(tau=95.0,  A=1.0, r=0.10),
    "bryophytes":          dict(tau=120.0, A=1.0, r=0.10),  # >100, unrecovered in-window
}


def get_modes():
    """Return a fresh deep-copy of MODES (safe for independent mutation)."""
    return copy.deepcopy(MODES)


def fixed_point(A, tau, r, T):
    """Recovered (pre-cut) fixed point of the stroboscopic map, constant tau.

    Signature matches kicked_relaxor_kernel.fixed_point(A, tau, r, T).
    Returns the constant-tau approximation; use simulate() for the ratcheted
    trajectory when landscape legacy stock L may fall below 1.
    """
    e = math.exp(-T / tau)
    return A * (1.0 - e) / (1.0 - r * e)


def simulate(mode, T, n_rot,
             legacy_decay=0.08, legacy_recover=0.03, replenish_thresh=0.55):
    """Ratcheted trajectory. Returns [(recovered_frac, L, tau_eff), ...]."""
    tau0, A, r = mode["tau"], mode["A"], mode["r"]
    L = 1.0
    x = A                                   # start mature
    traj = []
    for _ in range(n_rot):
        x = r * x                           # CUT
        tau_eff = tau0 / max(L, 1e-3)
        x = A - (A - x) * math.exp(-T / tau_eff)   # regrow to pre-cut value
        frac = x / A
        # legacy replenishes only if stand climbed back far enough
        if frac >= replenish_thresh:
            L = min(1.0, L + legacy_recover)
        else:
            L = max(0.05, L - legacy_decay)         # RATCHET down
        traj.append((frac, L, tau_eff))
    return traj


def steady_state(mode, T, n_rot=8):
    """Return the final ratcheted recovery fraction for mode dict at period T."""
    return simulate(mode, T, n_rot)[-1][0]


def verdict(frac):
    if frac >= 0.70: return "PERSIST"
    if frac >= 0.45: return "DECLINING"
    return "EXTIRPATED"


def report(T=70.0, n_rot=8, modes=None):
    if modes is None:
        modes = MODES
    print(f"T_cut = {T:.0f} yr    rotations = {n_rot}\n")
    print(f"{'mode':<20}{'tau':>5}{'tau/T':>7}{'x*fix':>8}{'x*ratchet':>11}  verdict")
    for name, m in modes.items():
        xf = fixed_point(m['A'], m['tau'], m['r'], T) / m['A']
        xr = simulate(m, T, n_rot)[-1][0]
        print(f"{name:<20}{m['tau']:>5.0f}{m['tau']/T:>7.2f}"
              f"{xf:>8.2f}{xr:>11.2f}  {verdict(xr)}")


if __name__ == "__main__":
    report(T=70)                     # current practice
    print("\n--- LEVERAGE: retention r high (variable-retention harvest) ---")
    modes_leverage = get_modes()
    for m in modes_leverage.values():
        m["r"] = min(0.45, m["r"] + 0.30)   # keep legacy islands → L holds
    report(T=70, modes=modes_leverage)
