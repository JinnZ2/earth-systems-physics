#!/usr/bin/env python3
# stressor_nonadditivity.py
# earth-systems-physics / Layer 6 — multi-stressor coupling audit.
# Single-factor studies measure stressors in ISOLATION and sum them. Reality is
# SYNERGISTIC: co-occurring warming x eCO2 AMPLIFY drought, so the combined
# effect exceeds the sum. The interaction term is where the severity lives — the
# omitted pool, same signature as permafrost/boreal.
# Seeded: Tissink et al., Science Advances 2026, DOI 10.1126/sciadv.aea8988
#   "combined effect greater than sum of individual effects"; grassland
#   carbon-uptake loss up to ~4x under future-climate drought.
# CC0. stdlib only.

# ── CONSTRAINTS ──────────────────────────────────────────────
# drought : isolated drought carbon-uptake loss (fraction)
# e_warm  : isolated warming effect (small)
# e_co2   : isolated eCO2 effect (small; protective effect negligible under drought)
# gamma   : synergistic amplification of drought by co-occurring warming x eCO2
# additive  = drought + e_warm + e_co2       (what single-factor studies book)
# observed  = drought * (1 + gamma)          (drought amplified in future climate)
# ─────────────────────────────────────────────────────────────

DROUGHT = 0.15
E_WARM  = 0.03
E_CO2   = 0.02
GAMMA   = 3.0     # tuned so observed = 4x isolated-drought loss (the headline)


def additive():
    return DROUGHT + E_WARM + E_CO2


def observed():
    return DROUGHT * (1 + GAMMA)


def verdict(underbook, amplify):
    if underbook >= 1.5:
        return (f"ADDITIVE_ASSUMPTION_FALSE — drought loss amplified {amplify:.1f}x "
                f"vs isolated; severity underbooked {underbook:.1f}x by summing")
    return "additive ~ ok"


if __name__ == "__main__":
    a, o = additive(), observed()
    print("isolated effects (carbon-uptake reduction):")
    print(f"  drought {DROUGHT:.3f}   warming {E_WARM:.3f}   eCO2 {E_CO2:.3f}")
    print(f"\nadditive prediction (single-factor sum): {a:.3f}")
    print(f"synergistic observed (coupled system):   {o:.3f}")
    print(f"interaction term (the omitted pool):     {o - a:.3f}")
    print(f"amplification vs drought-alone:          {o / DROUGHT:.2f}x")
    print(f"underbooking vs additive:                {o / a:.2f}x")
    print(f"\nVERDICT: {verdict(o / a, o / DROUGHT)}")
    print("\naudited pool = isolated effects (small).")
    print("unaudited pool = the interaction (large). same shape as permafrost/boreal.")
    print("GAP (honest, per Bahn): not yet generalizable across climate zones /")
    print("ecosystem types — needs matched multifactor experiments elsewhere.")
