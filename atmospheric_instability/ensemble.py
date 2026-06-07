"""
ensemble.py  --  CC0

Monte Carlo perturbation ensemble. The deterministic sweep tells you where a
mode CAN go unstable. This asks the harder question: under realistic noise in
the background state, what fraction of realizations actually cross threshold,
and does a small perturbation GROW or DECAY?

stdlib + random only. No numpy.
"""

import random
from climate_state import baseline_state, apply_warming, AtmoState, derived
from explorer import evaluate_state, active_set
import instabilities as K


def perturb_state(rng, state, rel_sigma=0.12):
    """
    Multiplicative Gaussian noise on the dynamically active fields. rel_sigma
    is the relative standard deviation (0.12 = 12% spread). Gradients can flip
    sign under strong perturbation -- that is physical (synoptic variability).
    """
    def jit(x):
        return x * (1.0 + rng.gauss(0.0, rel_sigma))
    return AtmoState(
        lat_deg=state.lat_deg,
        T=jit(state.T),
        dTdy_lower=jit(state.dTdy_lower),
        dTdy_upper=jit(state.dTdy_upper),
        env_lapse=jit(state.env_lapse),
        U=jit(state.U),
        dUdy=jit(state.dUdy),
        d2Udy2=jit(state.d2Udy2),
        gw_amplitude=jit(state.gw_amplitude),
        gw_wavelength_km=state.gw_wavelength_km,
        source=state.source + "+noise",
    )


def ensemble(lat_deg=45.0, w=0.5, level="lower", n=5000, seed=1, rel_sigma=0.12):
    """
    Run n perturbed realizations of the (lat, w) state. Report:
      - activation probability per mode
      - mean growth rate per mode (over realizations where active)
      - co-activation counts (which modes tend to fire together)
    """
    rng = random.Random(seed)
    base = apply_warming(baseline_state(lat_deg), w)
    modes = K.ALL_KERNELS

    activations = {m: 0 for m in modes}
    growth_sum = {m: 0.0 for m in modes}
    coactiv = {}

    for _ in range(n):
        st = perturb_state(rng, base, rel_sigma=rel_sigma)
        res, _ = evaluate_state(st, level=level)
        act = active_set(res)
        for m in act:
            activations[m] += 1
            growth_sum[m] += res[m].get("growth", 0.0)
        key = tuple(sorted(act))
        coactiv[key] = coactiv.get(key, 0) + 1

    prob = {m: activations[m] / n for m in modes}
    mean_growth = {m: (growth_sum[m] / activations[m] if activations[m] else 0.0)
                   for m in modes}
    top_co = sorted(coactiv.items(), key=lambda kv: kv[1], reverse=True)[:6]
    return {
        "lat": lat_deg, "w": w, "level": level, "n": n, "rel_sigma": rel_sigma,
        "activation_prob": prob,
        "mean_growth": mean_growth,
        "top_coactivation": [(list(k) or ["[stable]"], v) for k, v in top_co],
    }


def grow_perturbation(growth_rate, hours, dt_min=10.0, a0=1e-3):
    """
    Integrate a single mode amplitude a(t) = a0 * exp(growth_rate * t) over a
    window, returning amplification factor. Demonstrates whether the linear
    growth rate produces meaningful amplitude on weather timescales.
    """
    t = hours * 3600.0
    amp = a0 * (2.718281828 ** (growth_rate * t))
    return amp / a0


if __name__ == "__main__":
    for lvl in ("lower", "upper"):
        e = ensemble(lat_deg=45.0, w=0.7, level=lvl, n=4000, seed=2)
        print(f"\n[{lvl}] lat45 w0.7  n={e['n']}  sigma={e['rel_sigma']}")
        for m in K.ALL_KERNELS:
            p = e["activation_prob"][m]
            if p > 0:
                amp = grow_perturbation(e["mean_growth"][m], 24.0)
                print(f"  {m:18s} P(active)={p:5.2f}  "
                      f"mean_growth={e['mean_growth'][m]*1e5:6.2f}x1e5  "
                      f"24h_amplify={amp:8.2f}x")
        print("  top co-activation sets:")
        for combo, cnt in e["top_coactivation"][:4]:
            print(f"    {cnt:5d}  {combo}")
