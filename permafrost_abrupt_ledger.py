#!/usr/bin/env python3
# permafrost_abrupt_ledger.py
# earth-systems-physics / Layer 6 — Arctic sibling of boreal_carbon_ledger.
# Standard budgets book GRADUAL thaw only. The large pool is the omitted one:
# abrupt thaw (thermokarst) + belowground combustion + fire-mediated thaw.
# Seeded: Schadel et al., Comms Earth Environ 2026 (OSCAR v3.0)
#   under-represented processes = +166..258% over gradual-thaw-only
#   remaining-budget reduction  = 25%+/-12% (1.5C), 17%+/-7% (2.0C)
# CC0. stdlib only.

# ── CONSTRAINTS ──────────────────────────────────────────────
# booked  remaining carbon budget policy uses (permafrost IGNORED) [GtCO2]
# gradual thaw draw = modeled (small, slow, top-down)              [GtCO2]
# under-represented = abrupt + combustion + fire (LARGE, omitted)  [GtCO2]
# audited pool = the small one. Same signature as the boreal ledger.
# ─────────────────────────────────────────────────────────────

# fraction of booked budget eaten by permafrost (seeded band)
BUDGET_REDUCT = {"1.5C": (0.13, 0.37), "2.0C": (0.10, 0.24)}
UNDER_REP_MULT = (1.66, 2.58)   # abrupt+fire draw as multiple of gradual draw


def ledger(booked_budget, scenario, gradual_draw):
    lo, hi = BUDGET_REDUCT[scenario]
    eaten_lo, eaten_hi = booked_budget * lo, booked_budget * hi
    true_lo, true_hi = booked_budget - eaten_hi, booked_budget - eaten_lo
    ur_lo = gradual_draw * (UNDER_REP_MULT[0] - 1.0)
    ur_hi = gradual_draw * (UNDER_REP_MULT[1] - 1.0)
    return dict(booked=booked_budget, gradual=gradual_draw,
                under_rep=(ur_lo, ur_hi), eaten=(eaten_lo, eaten_hi),
                true=(true_lo, true_hi))


def verdict(true_band):
    lo, hi = true_band
    if lo <= 0: return "OVERSHOT (budget gone once slow pool counted)"
    return "UNAUDITED (positive only IF omitted pool stays low — it won't)"


def report(scenario, booked_budget, gradual_draw):
    L = ledger(booked_budget, scenario, gradual_draw)
    print(f"=== {scenario}  booked budget = {booked_budget:.0f} GtCO2 ===")
    print(f"  gradual thaw (modeled):        {L['gradual']:6.0f}")
    print(f"  under-represented (omitted):   {L['under_rep'][0]:6.0f} .. {L['under_rep'][1]:.0f}")
    print(f"  budget eaten by permafrost:    {L['eaten'][0]:6.0f} .. {L['eaten'][1]:.0f}")
    print(f"  TRUE remaining budget:         {L['true'][0]:6.0f} .. {L['true'][1]:.0f}")
    print(f"  VERDICT: {verdict(L['true'])}\n")


if __name__ == "__main__":
    report("1.5C", booked_budget=200.0, gradual_draw=120.0)
    report("2.0C", booked_budget=500.0, gradual_draw=160.0)
