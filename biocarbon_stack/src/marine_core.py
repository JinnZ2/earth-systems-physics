“””
MARINE CARBON COUPLING
Kelp / macroalgae as the marine analog of wetland carbon pump.

Verb-first physics:
upwelling delivers nutrients
nutrients enable kelp growth
kelp fixes CO2 via photosynthesis
detritus exports to deep ocean
deep export sequesters C from atmosphere on millennial timescale
shellfish/grazers cycle C in surface (not sequestration)

State variables (per m^2 of kelp forest):
N    nutrient availability (NO3-)        kg N / m2
K    kelp standing biomass               kg C / m2
D    detrital export flux                kg C / m2 / yr
S    sequestration fraction              [0,1]
“””

PARAMS_MARINE = {
“kelp_NPP”:           {“value”: 1.5,  “range”: (0.5, 3.0),  “unit”: “kg C / m2 / yr”},
“f_export_deep”:      {“value”: 0.11, “range”: (0.04, 0.20),“note”: “Krause-Jensen & Duarte 2016, fraction of NPP exported >1000m”},
“millennial_seq”:     {“value”: 0.85, “range”: (0.50, 0.95),“note”: “fraction of deep-exported C sequestered >1000yr”},
“ocean_alkalinization_per_kg_C”: {“value”: 1.0, “range”: (0.7, 1.3), “note”: “secondary CO2 drawdown via shell formation when grazers integrated”},

```
# CONSTRAINTS that limit scaling
"max_kelp_area_km2":  {"value": 48e6, "range": (24e6, 72e6),"FLAG": "physical upper bound, continental shelf area"},
"current_kelp_area_km2": {"value": 1.5e6, "range": (1e6, 2e6), "note": "remaining wild kelp forests"},

# FAILURE MODES
"warming_collapse_temp_C": {"value": 22, "range": (20, 24), "FLAG": "kelp dies above this surface T"},
"urchin_barren_threshold": {"value": 0.7, "range": (0.5, 0.9), "FLAG": "predator removal -> urchin overgraze -> kelp loss"},
```

}

def marine_drawdown_per_m2(p):
“”“Net long-term C drawdown per m2 of healthy kelp forest, kg C / m2 / yr.”””
return p[“kelp_NPP”][“value”] * p[“f_export_deep”][“value”] * p[“millennial_seq”][“value”]

def marine_global_potential(area_km2, p):
“”“Total annual drawdown if area_km2 is healthy kelp forest. Tg C / yr.”””
per_m2 = marine_drawdown_per_m2(p)
area_m2 = area_km2 * 1e6
return per_m2 * area_m2 / 1e9   # kg -> Tg

# —————————————————————

# COUPLING TO TERRESTRIAL: where the systems interact

# —————————————————————

COUPLING_TERMS = {
“river_nutrient_export”: “wetland N retention reduces coastal eutrophication, enables stable kelp”,
“sediment_flux”:         “wetland trapping of sediment reduces coastal turbidity, enables kelp depth range”,
“atmospheric_CH4”:       “terrestrial CH4 oxidation reduces global CH4, marine systems unaffected directly”,
“ocean_alkalinity”:      “enhanced weathering on land (with mycorrhizal acceleration) -> bicarbonate flux to ocean -> long-term CO2 buffering”,
}

MARINE_MISSING = [
“kelp species distribution under warming (range shift rate)”,
“interaction with ocean acidification (calcifier coupling)”,
“deep ocean turnover time at specific latitudes”,
“seafloor sediment burial fraction (truly permanent vs respired in 100s of yr)”,
“scaling: at what area does kelp restoration alter regional ocean chemistry?”,
]
