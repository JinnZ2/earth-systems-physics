#!/usr/bin/env python3
# amoc_hysteresis_gate.py
# earth-systems-physics / Layer 3 (ocean) — AMOC bistability as a fold in
# CO2-space. The tip is a ONE-WAY RATCHET: once collapsed, the door stays shut
# until CO2 drops below the recovery fold, not merely below the collapse fold.
# Seeded: Nian, Willeit, Wunderling, Ganopolski, Rockstrom, Comms Earth Env 2026
#   no recovery while CO2 > ~350 ppm ; present ~425 ppm and rising.
# Gulf-Stream-path shift = pre-fold early-warning channel (Comms Earth Env 2026).
# CC0. stdlib only.

# ── CONSTRAINTS ──────────────────────────────────────────────
# state q : "on" (overturning) or "off" (collapsed)
# C_collapse : upper fold — on->off when CO2 exceeds it        [ppm, illustrative]
# C_recover  : lower fold — off->on ONLY when CO2 below it      [ppm, SEEDED 350]
# hysteresis width = C_collapse - C_recover  (return != departure)
# EWS fires inside the pre-fold band (critical slowing / Gulf-Stream path)
# ─────────────────────────────────────────────────────────────

C_COLLAPSE = 480.0     # illustrative upper fold
C_RECOVER  = 350.0     # SEEDED recovery gate
EWS_BAND   = 40.0      # ppm below collapse fold where warning should already fire


def step(state, C):
    """Branch follower on the hysteresis loop."""
    ews = (state == "on") and (C >= C_COLLAPSE - EWS_BAND) and (C < C_COLLAPSE)
    if state == "on" and C >= C_COLLAPSE:
        return "off", "COLLAPSE", ews
    if state == "off" and C < C_RECOVER:
        return "on", "RECOVER", ews
    return state, "", ews


def run(co2_path, state="on"):
    print(f"hysteresis width = {C_COLLAPSE - C_RECOVER:.0f} ppm"
          f"  (collapse {C_COLLAPSE:.0f} / recover {C_RECOVER:.0f})\n")
    print(f"{'yr_idx':>6}{'CO2':>7}  state  event/EWS")
    for i, C in enumerate(co2_path):
        state, event, ews = step(state, C)
        flag = event or ("EWS: Gulf-Stream path shift" if ews else "")
        print(f"{i:>6}{C:>7.0f}  {state:<5}  {flag}")
    reachable = min(co2_path)
    print()
    if state == "off" and reachable >= C_RECOVER:
        print(f"VERDICT: LOCKED  (min CO2 {reachable:.0f} never crossed {C_RECOVER:.0f})")
    elif state == "off":
        print("VERDICT: recovered late")
    else:
        print("VERDICT: on-branch held")


if __name__ == "__main__":
    # rise past collapse, then aggressive drawdown that still parks above 350
    path = [425, 445, 465, 485, 470, 430, 395, 365, 355]
    run(path)
    print("\n--- drawdown that clears the recovery gate ---")
    run([425, 460, 490, 450, 380, 360, 345, 330], state="on")
