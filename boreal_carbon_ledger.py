#!/usr/bin/env python3
# boreal_carbon_ledger.py
# earth-systems-physics / Layer 6 (biosphere) — carbon accounting layer
# Composes on boreal_recovery_ratchet.py: the biodiversity ratchet IS the
# carbon-storage machinery. Books the "clearcut + ocean-sink" geoengineering
# scheme (gross credited removal) against physical net flux.
# CC0. stdlib only.

from boreal_recovery_ratchet import MODES, simulate

# ── CONSTRAINTS ──────────────────────────────────────────────
# Pools (per unit harvested aboveground biomass B=1):
#   C_bio   aboveground      small, fast, replaceable   ← what the scheme sinks
#   C_soil  soil/peat/humus  LARGE, slow, one-way       ← what it silently vents
# cap = bryophyte recovered fraction (insulating moss cap)  [from ratchet sim]
# L   = landscape legacy stock (mycorrhiza + CWD input)     [from ratchet sim]
# soil efflux rises as (cap, L) fall: canopy gone -> warms/drains -> mycelium
# dies -> stored C oxidizes. Same modes the ratchet sends to EXTIRPATED.
#
# SEEDED (real):  biodiversity tau  (Nature Sustainability 2026)
# UNAUDITED (research whitespace, flagged):
#   p_ocean   fraction of sunk biomass that stays sequestered  <- never measured
#   max_vent  soil efflux ceiling per rotation                 <- poorly bounded
#   ratio_soil soil:biomass pool ratio (upland ~5, peat ~30+)
# ─────────────────────────────────────────────────────────────


def carbon_ledger(T=70.0, n_rot=8, B=1.0, ratio_soil=5.0,
                  s_sink=0.60, p_ocean=0.50, ocean_measured=False,
                  max_vent=0.06):
    """Gross credited removal vs physical net flux across rotations."""
    cap_traj = simulate(MODES["bryophytes"], T, n_rot)   # (frac, L, tau_eff)
    C_soil = ratio_soil * B
    booked = removed = vented = 0.0
    rows = []
    for k in range(n_rot):
        cap, L, _ = cap_traj[k]
        booked  += s_sink * B                # scheme books gross sunk biomass
        removed += s_sink * B * p_ocean      # physically retained (ocean returns some)
        disturbance = 0.5 * (1 - cap) + 0.5 * (1 - L)   # 0 intact .. 1 gone
        vent = C_soil * max_vent * disturbance          # soil oxidizes
        C_soil -= vent
        vented += vent
        rows.append((k + 1, cap, L, booked, removed - vented, C_soil))
    return rows, booked, removed, vented, ocean_measured


def verdict(net_removal, ocean_measured):
    tag = "NET_SINK" if net_removal > 0 else "NET_SOURCE"
    if not ocean_measured:
        return f"UNAUDITED  ({tag} only IF ocean permanence held — unmeasured)"
    return tag


def report(label, **kw):
    rows, booked, removed, vented, meas = carbon_ledger(**kw)
    net = removed - vented
    print(f"\n=== {label} ===")
    print(f"{'rot':>3}{'cap':>6}{'L':>6}{'booked':>9}{'net_true':>10}{'C_soil':>8}")
    for (k, cap, L, bk, nr, cs) in rows:
        print(f"{k:>3}{cap:>6.2f}{L:>6.2f}{bk:>9.2f}{nr:>10.2f}{cs:>8.2f}")
    print(f"  booked removal (scheme ledger): {booked:6.2f}")
    print(f"  physically retained:            {removed:6.2f}")
    print(f"  soil C vented (one-way):        {vented:6.2f}")
    print(f"  NET physical removal:           {net:6.2f}")
    print(f"  LAUNDER GAP (booked - net):     {booked - net:6.2f}")
    print(f"  VERDICT: {verdict(net, meas)}")


if __name__ == "__main__":
    report("UPLAND boreal  (soil 5x biomass)",  ratio_soil=5.0)
    report("PEATLAND boreal (soil 30x biomass)", ratio_soil=30.0)
