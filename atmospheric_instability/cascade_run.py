"""
cascade_run.py  --  CC0

Entry point for the atmospheric instability cascade explorer.

USAGE
  python3 cascade_run.py                         # full report at lat 45
  python3 cascade_run.py --lat 60 --level lower
  python3 cascade_run.py --cascade --w 0.7       # cascade trace at warming 0.7
  python3 cascade_run.py --surface               # ASCII growth-rate surface
  python3 cascade_run.py --json                  # machine-readable sweep
"""

import argparse
import json

from explorer import (
    sweep_warming, find_crossings, cascade_at, latitude_warming_grid,
)
from ensemble import ensemble, grow_perturbation
import instabilities as K


BAR = "=" * 74


def render_sweep(lat, level):
    sweep = sweep_warming(lat_deg=lat, level=level)
    print(BAR)
    print(f"ATMOSPHERIC INSTABILITY SWEEP  lat={lat}  level={level}")
    print("warming_index 0 (baseline) -> 1 (strong forcing)")
    print(BAR)
    # growth-rate table (scaled 1e5 for readability, units 1/s)
    modes = K.ALL_KERNELS
    hdr = f"{'w':>5} " + "".join(f"{m[:7]:>9}" for m in modes)
    print(hdr)
    print("-" * len(hdr))
    for step in sweep:
        row = f"{step['w']:>5.2f} "
        for m in modes:
            g = step["growth"][m] * 1e5
            row += f"{g:>9.2f}"
        print(row)
    print("-" * len(hdr))
    print("growth rates x1e5 [1/s].  >0 = unstable & amplifying.")
    print(BAR)

    print("ZERO-CROSSINGS  (where a mode switches state as warming rises)")
    print("-" * 74)
    cr = find_crossings(sweep)
    if not cr:
        print("  no state changes across the sweep at this lat/level.")
    for m, events in cr.items():
        ev = ", ".join(f"w={w} {kind}" for w, kind in events)
        print(f"  {m:18s} {ev}")
    print(BAR)

    # baroclinic timescale + Ri trajectory
    print("KEY TRAJECTORIES")
    print("-" * 74)
    print(f"{'w':>5}{'Ri':>9}{'shear/1e3':>12}{'N/1e2':>10}{'eady_hr':>10}")
    for step in sweep[::4]:
        ri = step["Ri"]
        ri_s = f"{ri:.2f}" if ri != float('inf') else "inf"
        eh = step["eady_hr"]
        eh_s = f"{eh:.1f}" if eh != float('inf') else "inf"
        print(f"{step['w']:>5.2f}{ri_s:>9}{step['shear']*1e3:>12.3f}"
              f"{step['N']*1e2:>10.3f}{eh_s:>10}")
    print(BAR)


def render_cascade(lat, w, level):
    c = cascade_at(lat_deg=lat, w=w, level=level)
    print(BAR)
    print(f"CASCADE TRACE  lat={lat}  w={w}  level={level}")
    print(BAR)
    print(f"active (broken) modes : {c['active'] or '[none]'}")
    print(f"cascade-reachable     : {c['cascade_reachable'] or '[none]'}")
    print("-" * 74)
    if not c["steps"]:
        print("no coupling steps (no active mode to propagate).")
    else:
        print("propagation chain (+ amplifies, - damps):")
        for depth, src, tgt, sign, mech, strength in c["steps"]:
            s = "+" if sign > 0 else "-"
            indent = "  " * depth
            print(f"{indent}[{s}{strength:.1f}] {src} -> {tgt}")
            print(f"{indent}      {mech}")
    print(BAR)


def render_surface(level, mode="baroclinic_eady"):
    lats = [20, 30, 40, 45, 50, 60, 70]
    ws = [i / 10 for i in range(11)]
    lats, ws, grid = latitude_warming_grid(lats, ws, level=level, mode=mode)
    # normalize for shading
    flat = [v for row in grid for v in row]
    mx = max(flat) or 1.0
    shades = " .:-=+*#%@"
    print(BAR)
    print(f"GROWTH-RATE SURFACE  mode={mode}  level={level}")
    print(f"rows = warming 0..1 (top=0)   cols = latitude {lats}")
    print(BAR)
    print("      " + "".join(f"{l:>5}" for l in lats))
    for w, row in zip(ws, grid):
        line = f"w={w:>3.1f} "
        for v in row:
            idx = int((v / mx) * (len(shades) - 1)) if mx > 0 else 0
            line += f"  {shades[idx]}  "
        print(line)
    print("-" * 74)
    print(f"shade scale low->high: '{shades}'  max growth={mx*1e5:.2f} x1e5 1/s")
    print(BAR)


def render_ensemble(lat, w, level):
    e = ensemble(lat_deg=lat, w=w, level=level, n=6000, seed=3)
    print(BAR)
    print(f"MONTE CARLO ENSEMBLE  lat={lat}  w={w}  level={level}")
    print(f"n={e['n']}  perturbation sigma={e['rel_sigma']}  (realistic synoptic noise)")
    print(BAR)
    print(f"{'mode':20s}{'P(active)':>11}{'mean_g x1e5':>13}{'24h amplify':>13}")
    print("-" * 74)
    for m in K.ALL_KERNELS:
        p = e["activation_prob"][m]
        if p > 0:
            amp = grow_perturbation(e["mean_growth"][m], 24.0)
            print(f"{m:20s}{p:>11.2f}{e['mean_growth'][m]*1e5:>13.2f}{amp:>12.2f}x")
    print("-" * 74)
    print("co-activation sets (which modes fire together under noise):")
    for combo, cnt in e["top_coactivation"]:
        print(f"  {cnt:>6d}  {combo}")
    print(BAR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, default=45.0)
    ap.add_argument("--level", choices=["lower", "upper"], default="lower")
    ap.add_argument("--w", type=float, default=0.5)
    ap.add_argument("--cascade", action="store_true")
    ap.add_argument("--surface", action="store_true")
    ap.add_argument("--ensemble", action="store_true")
    ap.add_argument("--mode", default="baroclinic_eady")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.json:
        sweep = sweep_warming(lat_deg=args.lat, level=args.level)
        print(json.dumps({
            "lat": args.lat, "level": args.level,
            "sweep": sweep,
            "crossings": find_crossings(sweep),
        }, indent=2))
        return

    if args.cascade:
        render_cascade(args.lat, args.w, args.level)
        return

    if args.surface:
        render_surface(args.level, mode=args.mode)
        return

    if args.ensemble:
        render_ensemble(args.lat, args.w, args.level)
        return

    render_sweep(args.lat, args.level)
    print()
    render_cascade(args.lat, args.w, args.level)


if __name__ == "__main__":
    main()
