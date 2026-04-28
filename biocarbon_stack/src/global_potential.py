“””
PLANETARY POTENTIAL - what the math actually says.
No narrative. Just the bounds.

Question: if the coupled wetland + marine system is restored to historical
extent, what fraction of current anthropogenic C/CH4 flux can it absorb?

Reference fluxes (current, ~2024):
Anthropogenic CO2 emissions:     ~37 Gt CO2 / yr = ~10 Gt C / yr
Anthropogenic CH4 emissions:     ~360 Tg CH4 / yr (~half of total ~580 Tg)
Atmospheric CO2 growth rate:     ~5.3 Gt C / yr (the rest goes to ocean+land sinks)
“””

from wetland_core import PARAMS, carbon_storage_rate, methane_balance
from marine_core import PARAMS_MARINE, marine_drawdown_per_m2

# —————————————————————

# HISTORICAL vs CURRENT extent

# —————————————————————

EXTENT = {
“wetlands_historical_km2”:    {“value”: 12.1e6, “range”: (10e6, 14e6), “source”: “pre-industrial estimate”},
“wetlands_current_km2”:       {“value”:  8.6e6, “range”: (8e6, 9e6),   “source”: “Ramsar 2018”},
“wetlands_drained_km2”:       {“value”:  3.5e6, “range”: (2e6, 5e6),   “note”: “loss = restoration target”},

```
"peatlands_km2":              {"value":  4.0e6, "range": (3.5e6,4.5e6),"note": "subset, highest C density"},
"peatlands_drained_km2":      {"value":  0.5e6, "range": (0.4e6,0.6e6),"note": "actively oxidizing, net source"},

"kelp_historical_km2":        {"value":  3.5e6, "range": (2e6, 5e6),   "FLAG": "estimate, poor data"},
"kelp_current_km2":           {"value":  1.5e6, "range": (1e6, 2e6),   "FLAG": "estimate"},
```

}

def terrestrial_potential():
“””
Restoration of drained wetlands + protection of remaining wetlands.
Returns dict of annual fluxes at full restoration.
“””
p = PARAMS

```
# restored peatlands (highest C density, anoxic, low CH4 once stable)
peat_restore_m2 = EXTENT["peatlands_drained_km2"]["value"] * 1e6
peat_C_rate = carbon_storage_rate(W=0.95, R_p=0.6, p=p)   # kg C / m2 / yr
peat_drawdown_GtC = peat_C_rate * peat_restore_m2 / 1e12

# other restored wetlands (lower C density, more variable)
other_restore_m2 = (EXTENT["wetlands_drained_km2"]["value"] -
                    EXTENT["peatlands_drained_km2"]["value"]) * 1e6
other_C_rate = carbon_storage_rate(W=0.85, R_p=0.5, p=p)
other_drawdown_GtC = other_C_rate * other_restore_m2 / 1e12

# methane during transition (the spike the source doc hid)
transition_CH4_Tg = (peat_restore_m2 + other_restore_m2) * 0.02 / 1e9   # rough, kg/m2 spike avg

# protection of remaining (avoiding loss)
protect_m2 = EXTENT["wetlands_current_km2"]["value"] * 1e6
avoided_emission_C_rate = 0.3   # kg C / m2 / yr, peat oxidation if drained
avoided_GtC = avoided_emission_C_rate * protect_m2 * 0.05 / 1e12  # 5% loss/yr without protection

return {
    "peat_restoration_GtC_yr":    peat_drawdown_GtC,
    "other_wetland_GtC_yr":       other_drawdown_GtC,
    "transition_methane_TgCH4":   transition_CH4_Tg,
    "avoided_emissions_GtC_yr":   avoided_GtC,
    "total_drawdown_GtC_yr":      peat_drawdown_GtC + other_drawdown_GtC + avoided_GtC,
}
```

def marine_potential():
“”“Kelp restoration to historical extent.”””
p = PARAMS_MARINE
restore_km2 = EXTENT[“kelp_historical_km2”][“value”] - EXTENT[“kelp_current_km2”][“value”]
per_m2 = marine_drawdown_per_m2(p)   # kg C / m2 / yr long-term sequestered
total_GtC = per_m2 * restore_km2 * 1e6 / 1e12
return {
“kelp_restoration_km2”: restore_km2,
“per_m2_kg_C_yr”:       per_m2,
“total_drawdown_GtC_yr”: total_GtC,
}

def global_balance():
“”“Compare biological potential to anthropogenic flux.”””
t = terrestrial_potential()
m = marine_potential()

```
bio_total_GtC = t["total_drawdown_GtC_yr"] + m["total_drawdown_GtC_yr"]
anthro_GtC    = 10.0  # current annual emissions
atm_growth    = 5.3   # current annual atmospheric C accumulation

return {
    "biological_drawdown_GtC_yr":  bio_total_GtC,
    "anthropogenic_emissions_GtC": anthro_GtC,
    "atmospheric_growth_GtC_yr":   atm_growth,
    "fraction_emissions_offset":   bio_total_GtC / anthro_GtC,
    "fraction_growth_offset":      bio_total_GtC / atm_growth,
    "transition_CH4_warming_yr":   "spike during years 2-15 of restoration, must be planned for",
    "VERDICT":                     None,  # populated by audit
}
```

if **name** == “**main**”:
t = terrestrial_potential()
m = marine_potential()
g = global_balance()

```
print("TERRESTRIAL")
for k,v in t.items(): print(f"  {k}: {v}")
print("\nMARINE")
for k,v in m.items(): print(f"  {k}: {v}")
print("\nGLOBAL BALANCE")
for k,v in g.items(): print(f"  {k}: {v}")
```
