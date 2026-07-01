#!/usr/bin/env python3
# fuel_load_ratchet.py
# earth-systems-physics / Layer 6 — SIGN-INVERTED twin of boreal_recovery_ratchet.
# Same relaxor kernel: state relaxes toward K between kicks. Here the target is
# BAD (fuel -> critical connectivity) and the kick is BENEFICIAL (a burn resets
# fuel down). Boreal: forcing too frequent collapses a good mode. Fire: removing
# a good frequent forcing lets a bad slow variable ratchet up to a basin flip.
# Seeded: Mariani 2022 (Front Ecol Environ); McKemey/Banbai grevillea
#   cultural burn preserved multi-aged stand; wildfire killed 99.6% of mature.
# CC0. stdlib only.

import math

# ── CONSTRAINTS ──────────────────────────────────────────────
# F      fuel load / connectivity  0..K   (K=1 = fully connected canopy fuel)
# tau_F  fuel accumulation time                                   [yr]
# T_fire fire return interval (short=cultural, long=suppressed)   [yr]
# r_f    fuel fraction left after a burn (low-sev cultural burn)  0..1
# F_safe below this -> low severity mosaic ; F_crit above -> megafire flip
# mortality of mature cohort rises with severity S in [0,1]
# ─────────────────────────────────────────────────────────────

K = 1.0
TAU_F = 25.0
F_SAFE = 0.35
F_CRIT = 0.70


def severity(F):
    return max(0.0, min(1.0, (F - F_SAFE) / (F_CRIT - F_SAFE)))


def mature_mortality(S):
    # low-sev cultural fire ~ multi-aged preserved; high-sev ~ 99.6% killed
    return 0.05 + S * (0.996 - 0.05)


def run(label, T_fire, r_f, n_fires=6, F0=0.15):
    F = F0
    print(f"=== {label}  T_fire={T_fire}yr  r_f={r_f} ===")
    print(f"{'fire':>4}{'F_pre':>7}{'sev':>6}{'mort%':>7}  basin")
    flipped = False
    for k in range(n_fires):
        F = K - (K - F) * math.exp(-T_fire / TAU_F)   # accumulate to pre-fire load
        S = severity(F)
        mort = mature_mortality(S)
        basin = "MEGAFIRE_FLIP" if S >= 1.0 else ("mosaic" if S < 0.3 else "mixed")
        if S >= 1.0:
            flipped = True
        print(f"{k+1:>4}{F:>7.2f}{S:>6.2f}{mort*100:>7.1f}  {basin}")
        F = r_f * F                                   # the burn resets fuel down
        if flipped:
            break
    print("VERDICT:", "MEGAFIRE_FLIP (multi-aged structure lost)" if flipped
          else "MOSAIC_HELD (frequent low-sev kicks hold safe basin)", "\n")


if __name__ == "__main__":
    run("CULTURAL BURNING (frequent, chosen)", T_fire=5,  r_f=0.10)
    run("SUPPRESSION (fire excluded, then wildfire)", T_fire=90, r_f=0.10, n_fires=1)
