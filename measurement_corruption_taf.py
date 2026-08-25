#!/usr/bin/env python3
# measurement_corruption_taf.py
# earth-systems-physics / metrology layer — instantiates the TAF identity:
#   corruption(trend) = corruption(measurement) x corruption(framework)
# A REAL trend can be driven below detectability by degrading the sensing
# channel, with zero change to the physical world. Framework corruption then
# reports "no significant change" — the inspection step-function, epistemic form.
# Seeded: radiosonde cuts degrade 48h NH forecasts 4-10% (ECMWF/WMO 2025);
#         5G encroachment on 23.8 GHz water-vapor sounding (Golparvar 2026).
# CC0. stdlib only.

import math

# ── CONSTRAINTS ──────────────────────────────────────────────
# true_trend  physical signal over horizon (real, nonzero)   [units/decade]
# sigma0      baseline observational noise                     [units]
# m           measurement corruption 0..1 (sensor loss, band encroachment)
#             effective noise sigma = sigma0 / (1 - m)   -> blows up as m->1
# f           framework corruption 0..1 (raises the bar to "detect")
#             z_crit = 1.96 * (1 + f)
# detect if   z = true_trend*horizon / sigma  >  z_crit
# ─────────────────────────────────────────────────────────────


def detect(true_trend, horizon, sigma0, m, f):
    sigma = sigma0 / max(1e-3, (1.0 - m))
    z = (true_trend * horizon) / sigma
    z_crit = 1.96 * (1.0 + f)
    return z, z_crit, z > z_crit, sigma   # sigma returned so callers avoid recomputing


def sweep(true_trend=0.30, horizon=3.0, sigma0=0.30, f=0.0):
    print(f"true_trend={true_trend}/dec  horizon={horizon}dec  "
          f"sigma0={sigma0}  framework_corruption f={f}")
    print(f"{'m':>5}{'sigma':>8}{'z':>7}{'z_crit':>8}  verdict")
    masked_at = None
    for m in [0.0, 0.05, 0.10, 0.20, 0.35, 0.50, 0.60]:
        z, zc, ok, sigma = detect(true_trend, horizon, sigma0, m, f)
        v = "TREND_VISIBLE" if ok else "TREND_MASKED (real, unseen)"
        if not ok and masked_at is None:
            masked_at = m
        print(f"{m:>5.2f}{sigma:>8.2f}{z:>7.2f}{zc:>8.2f}  {v}")
    print("VERDICT:", f"real trend goes invisible at measurement corruption m>={masked_at:.2f}"
          if masked_at is not None else "trend robust across tested corruption", "\n")


if __name__ == "__main__":
    sweep(f=0.0)          # honest framework
    print("--- add framework corruption (institutional denial raises the bar) ---")
    sweep(f=0.30)         # measurement x framework compound -> masked earlier
