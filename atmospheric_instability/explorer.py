"""
explorer.py  --  CC0

The exploration engine. Evaluates every instability kernel against a given
atmospheric state, sweeps the warming index (or any parameter), and locates
where each mode CROSSES from stable to unstable.

stdlib only. Returns data structures; rendering is the caller's job.
"""

from climate_state import baseline_state, apply_warming, derived
from coupling import trace_cascade, cascade_reachable
import instabilities as K


def evaluate_state(state, level="lower"):
    """
    Run all kernels against one state. Returns {mode: result_dict}.
    """
    d = derived(state, level=level)
    results = {}
    results["kelvin_helmholtz"] = K.kelvin_helmholtz(d["N2"], d["shear"])
    results["baroclinic_eady"] = K.baroclinic_eady(d["f"], d["N"], d["shear"])
    results["inertial"] = K.inertial(d["f"], d["dUdy"])
    results["symmetric"] = K.symmetric(d["f"], d["N2"], d["shear"])
    results["gravity_wave"] = K.gravity_wave(d["N"], d["U"], d["gw_wl"], d["gw_amp"])
    results["convective"] = K.convective(d["N2"])
    results["rossby_barotropic"] = K.rossby_barotropic(d["lat"], d["U"], d["d2Udy2"])
    return results, d


def active_set(results):
    return {m for m, r in results.items() if r.get("active")}


def sweep_warming(lat_deg=45.0, level="lower", steps=21):
    """
    Sweep warming_index 0->1. For each step record growth rate of every mode
    and the active set. Returns list of per-step dicts.
    """
    base = baseline_state(lat_deg)
    out = []
    for i in range(steps):
        w = i / (steps - 1)
        st = apply_warming(base, w)
        res, d = evaluate_state(st, level=level)
        out.append({
            "w": w,
            "growth": {m: res[m].get("growth", 0.0) for m in res},
            "active": sorted(active_set(res)),
            "shear": d["shear"],
            "N": d["N"],
            "Ri": res["kelvin_helmholtz"]["Ri"],
            "eady_hr": res["baroclinic_eady"].get("timescale_hr", float("inf")),
        })
    return out


def find_crossings(sweep):
    """
    For each mode, find warming_index values where it transitions
    inactive->active (onset) or active->inactive (suppression).
    Returns {mode: [(w, 'onset'|'suppress'), ...]}.
    """
    modes = K.ALL_KERNELS
    crossings = {m: [] for m in modes}
    prev = None
    for step in sweep:
        cur = set(step["active"])
        if prev is not None:
            for m in modes:
                was, now = (m in prev), (m in cur)
                if now and not was:
                    crossings[m].append((round(step["w"], 3), "onset"))
                elif was and not now:
                    crossings[m].append((round(step["w"], 3), "suppress"))
        prev = cur
    return {m: c for m, c in crossings.items() if c}


def cascade_at(lat_deg=45.0, w=0.5, level="lower", max_depth=4):
    """
    Evaluate at a single (lat, w), find active modes, trace the cascade chain.
    """
    st = apply_warming(baseline_state(lat_deg), w)
    res, d = evaluate_state(st, level=level)
    act = active_set(res)
    steps = trace_cascade(act, max_depth=max_depth)
    reach = cascade_reachable(act, max_depth=max_depth)
    return {
        "w": w, "lat": lat_deg, "level": level,
        "active": sorted(act),
        "cascade_reachable": sorted(reach),
        "steps": steps,
        "growth": {m: res[m].get("growth", 0.0) for m in res},
    }


def latitude_warming_grid(lats, ws, level="lower", mode="baroclinic_eady"):
    """
    2D field of one mode's growth rate over (latitude x warming) for surface plots.
    Returns (lats, ws, grid[len(ws)][len(lats)]).
    """
    grid = []
    for w in ws:
        row = []
        for lat in lats:
            st = apply_warming(baseline_state(lat), w)
            res, _ = evaluate_state(st, level=level)
            row.append(res[mode].get("growth", 0.0))
        grid.append(row)
    return lats, ws, grid
