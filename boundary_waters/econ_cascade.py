“””
Economic externality cascade. Consumes physical cascade output
and produces year-by-year dollar/case distribution across
homeowners, workers, communities, state, infrastructure.
“””

from cascade import run_cascade
from econ_layers import (
home_depreciation_layer, worker_health_layer, ltc_layer,
community_load_layer, state_load_layer, infrastructure_layer
)

def run_econ_cascade(scenario=“proceed”, seed=42):
phys_history = run_cascade(scenario=scenario, seed=seed)
econ_history = []
years_mine_active = 0
mine_ever_operated = False

```
for phys in phys_history:
    if phys["mine_active"]:
        years_mine_active += 1
        mine_ever_operated = True

    prop   = home_depreciation_layer(phys, phys["mine_active"])
    health = worker_health_layer(phys, phys["mine_active"], years_mine_active)
    ltc    = ltc_layer(health)
    comm   = community_load_layer(phys, prop, health, phys["mine_active"])
    state  = state_load_layer(phys, health, ltc, comm,
                              phys["mine_active"], phys["year"],
                              prop["superfund_flag"], mine_ever_operated)
    infra  = infrastructure_layer(phys["mine_active"])

    econ_history.append({
        "year": phys["year"],
        "scenario": scenario,
        **prop, **health, **ltc, **comm, **state, **infra,
        # physical signals kept for cross-ref
        "sulfate_mg_l":        phys["sulfate_mg_l"],
        "wells_contaminated":  phys["wells_contaminated"],
        "forced_migrants":     phys["forced_migrants"],
        "tailings_failed":     phys["tailings_failed"],
    })

return econ_history
```

def summarize_econ(hist, label):
print(f”\n{‘═’*72}”)
print(f”  ECON CASCADE: {label}”)
print(f”{‘═’*72}”)
snapshots = [10, 20, 30, 50, 100, 250, 499]
print(f”{‘Year’:>5} {‘PropLoss$B’:>11} {‘HealthLife$B’:>13} “
f”{‘StateAnn$M’:>11} {‘MuniAnn$M’:>11} {‘Ratepayer$M’:>12}”)
print(”-” * 72)
for yr in snapshots:
h = hist[yr]
print(f”{yr:>5} “
f”{h[‘total_property_loss_usd’]/1e9:>11.2f} “
f”{h[‘total_health_cost_usd’]/1e9:>13.2f} “
f”{h[‘state_annual_load_usd’]/1e6:>11.1f} “
f”{h[‘municipal_annual_usd’]/1e6:>11.2f} “
f”{h[‘ratepayer_burden_usd’]/1e6:>12.1f}”)

def peak_summary(hist, label):
peak = {
“property_loss_usd”:   max(h[“total_property_loss_usd”] for h in hist),
“health_lifetime_usd”: max(h[“total_health_cost_usd”] for h in hist),
“state_annual_usd”:    max(h[“state_annual_load_usd”] for h in hist),
“muni_annual_usd”:     max(h[“municipal_annual_usd”] for h in hist),
“unfunded_cleanup”:    max(h[“unfunded_cleanup_usd”] for h in hist),
“kids_impaired”:       max(h[“kids_neuro_impaired”] for h in hist),
“fiscal_collapse_yr”:  next((h[“year”] for h in hist if h[“fiscal_collapse_flag”]), None),
“superfund_yr”:        next((h[“year”] for h in hist if h[“superfund_flag”]), None),
“cumulative_state_load”: sum(h[“state_annual_load_usd”] for h in hist),
}
print(f”\n  {label}”)
print(f”    peak property loss     : ${peak[‘property_loss_usd’]/1e9:>7.2f} B”)
print(f”    peak lifetime health   : ${peak[‘health_lifetime_usd’]/1e9:>7.2f} B”)
print(f”    peak state annual load : ${peak[‘state_annual_usd’]/1e6:>7.1f} M/yr”)
print(f”    peak municipal annual  : ${peak[‘muni_annual_usd’]/1e6:>7.1f} M/yr”)
print(f”    unfunded cleanup gap   : ${peak[‘unfunded_cleanup’]/1e9:>7.2f} B”)
print(f”    peak kids neuro-impaired: {peak[‘kids_impaired’]:>6}”)
print(f”    fiscal collapse at year: {peak[‘fiscal_collapse_yr’]}”)
print(f”    superfund listing year : {peak[‘superfund_yr’]}”)
print(f”    cumulative state 500yr : ${peak[‘cumulative_state_load’]/1e9:>7.1f} B”)
return peak

if **name** == “**main**”:
scenarios = [
(“protected”,        “20-yr withdrawal holds”),
(“proceed”,          “CRA reversal -> mine operates”),
(“tailings_failure”, “Mine + Mount Polley-class dam failure”),
]
all_runs = {}
for key, label in scenarios:
hist = run_econ_cascade(scenario=key)
all_runs[key] = hist
summarize_econ(hist, label)

```
print(f"\n{'═'*72}")
print("  PEAK EXTERNALITY (500-year horizon)")
print(f"{'═'*72}")
peaks = {}
for key, label in scenarios:
    peaks[key] = peak_summary(all_runs[key], label)

# Infrastructure snapshot during active mining (yr 10)
print(f"\n{'═'*72}")
print("  INFRASTRUCTURE COMPETITION (year 10, mine active)")
print(f"{'═'*72}")
h = all_runs["proceed"][10]
print(f"    power demand          : {h['power_demand_mw']} MW (mine)")
print(f"    new grid reserve margin: {h['grid_reserve_margin']*100:.1f}%  (target ≥15%)")
print(f"    grid stress flag      : {h['grid_stress_flag']}")
print(f"    transmission upgrades : ${h['transmission_capex_usd']/1e6:.0f} M")
print(f"    ratepayer burden      : ${h['ratepayer_burden_usd']/1e6:.0f} M (socialized)")
print(f"    water stress ratio    : {h['water_stress_ratio']:.2f} (>0.75 = conflict)")
print(f"    water conflict flag   : {h['water_conflict_flag']}")
print(f"    road maint annual     : ${h['road_maint_annual_usd']/1e6:.1f} M")
print(f"    EMS response time     : {h['ems_response_time_min']:.0f} min")
```
