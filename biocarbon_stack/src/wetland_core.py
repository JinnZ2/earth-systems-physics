"""
WETLAND CARBON COUPLING - FIRST PRINCIPLES
Verb-first physics. No narrative. Constraint equations only.

State variables (per m^2):
W   water saturation fraction         [0,1]
C_p peat carbon stock                 kg C
C_m mycorrhizal carbon stock          kg C
C_a aggregate-stabilized carbon       kg C (earthworm necromass pool)
M   methane production rate           kg CH4 / yr
M_o methane oxidation rate            kg CH4 / yr
R_p plant productivity                kg C / yr  (aerenchymous spp)

Couplings (verb-first, no morality):
saturation creates anoxia
anoxia disables aerobic decomposition
anoxia enables methanogenesis
aerenchyma transports O2 to rhizosphere
rhizosphere O2 feeds methanotrophs
methanotrophs oxidize CH4 to CO2
mycorrhiza receive plant C, secrete glomalin
earthworms convert labile C to necromass aggregates

Net carbon flux (atmosphere perspective, negative = drawdown):
dC_atm/dt = -R_p + (1-f_anox)*decomp + (M - M_o)*GWP_ch4
"""

import numpy as np

# —————————————————————

# PARAMETERS - state ranges, not point values. flag uncertainty.

# —————————————————————

PARAMS = {
# hydrology
"W_anox_threshold":   {"value": 0.85, "range": (0.75, 0.95), "source": "peat anoxia onset"},
"flood_period_yr":    {"value": 1.0,  "range": (0.5, 5.0),   "source": "managed regime"},

# decomposition
"k_decomp_aerobic":   {"value": 0.05, "range": (0.02, 0.10), "unit": "1/yr"},
"k_decomp_anaerobic": {"value": 0.002,"range": (0.001,0.005),"unit": "1/yr"},

# methane fluxes
"f_methanogen":       {"value": 0.30, "range": (0.10, 0.50), "note": "fraction anaerobic C -> CH4"},
"k_methanotroph_max": {"value": 0.85, "range": (0.60, 0.95), "note": "fraction CH4 oxidized in oxic rhizosphere"},
"GWP_ch4_100yr":      {"value": 28,   "range": (27, 30),     "unit": "CO2eq"},

# mycorrhiza
"f_plant_to_myco":    {"value": 0.20, "range": (0.10, 0.30), "note": "fraction NPP to fungal partners"},
"k_glomalin_stable":  {"value": 0.40, "range": (0.30, 0.50), "note": "fraction myco C -> stable glomalin"},

# earthworm necromass
"k_aggregate_form":   {"value": 0.15, "range": (0.05, 0.25), "note": "labile C -> aggregate / yr, native worms only"},
"f_earthworm_active": {"value": 0.50, "range": (0.0, 1.0),   "FLAG": "depends on native vs invasive species"},

# plant productivity (aerenchymous wetland)
"NPP_wetland":        {"value": 0.6,  "range": (0.3, 1.2),   "unit": "kg C / m2 / yr"},

# TRANSITION SPIKE - the parameter the DeepSeek doc hid
"rewet_methane_spike_yr":  {"value": 5,   "range": (2, 15),  "FLAG": "drained peat -> rewet emits net CH4 before becoming sink"},
"spike_magnitude_factor":  {"value": 3.0, "range": (1.5, 6.0),"FLAG": "multiplier on baseline CH4 during transition"},

}

def methane_balance(W, R_p, p):
    """
    CH4 produced - CH4 oxidized at rhizosphere boundary.
    Returns net CH4 flux to atmosphere (kg CH4 / m2 / yr).
    """
    anaerobic_C = p["k_decomp_anaerobic"]["value"] * R_p * (W ** 2)
    M_produced  = p["f_methanogen"]["value"] * anaerobic_C
    aerenchyma_factor = R_p / p["NPP_wetland"]["value"]
    M_oxidized  = p["k_methanotroph_max"]["value"] * M_produced * aerenchyma_factor
    return max(0.0, M_produced - M_oxidized)

def carbon_storage_rate(W, R_p, p):
    """
    Net C storage rate in soil (kg C / m2 / yr).
    Combines peat accumulation, mycorrhizal glomalin, earthworm aggregates.
    """
    f_anox = 1.0 if W >= p["W_anox_threshold"]["value"] else W / p["W_anox_threshold"]["value"]
    peat_accum = R_p * f_anox * (1 - p["k_decomp_anaerobic"]["value"])
    myco_stable = R_p * p["f_plant_to_myco"]["value"] * p["k_glomalin_stable"]["value"]
    aggregate   = R_p * p["k_aggregate_form"]["value"] * p["f_earthworm_active"]["value"]
    return peat_accum + myco_stable + aggregate

def net_co2eq_flux(W, R_p, p, transition_year=None):
    """
    Net CO2-equivalent flux to atmosphere (kg CO2eq / m2 / yr).
    Negative = drawdown.

    transition_year: if rewetting drained peat, year since rewet.
                     During spike window, methane is amplified.
    """
    C_stored = carbon_storage_rate(W, R_p, p)
    M_net    = methane_balance(W, R_p, p)

    # transition spike - the missing parameter in the source doc
    if transition_year is not None:
        if transition_year < p["rewet_methane_spike_yr"]["value"]:
            M_net *= p["spike_magnitude_factor"]["value"]

    co2_drawdown = -C_stored * (44.0/12.0)        # C -> CO2 mass
    ch4_warming  =  M_net * p["GWP_ch4_100yr"]["value"] * (44.0/16.0)
    return co2_drawdown + ch4_warming

# —————————————————————

# AUDIT: what the source document does NOT specify

# —————————————————————

MISSING_PARAMETERS = [
"minimum viable beaver territory (km2)",
"ungulate density floor before wolf reintroduction stabilizes",
"time-to-functional-wetland after dam initiation",
"methane spike magnitude during rewet transition",  # partially captured above
"native vs invasive earthworm species distribution by region",
"mycorrhizal network reassembly time on degraded soil",
"saturation hysteresis (drained peat does not rewet symmetrically)",
"fire return interval interaction with managed burn regimes",
"permafrost boundary condition (shifts entire equation set)",
]

UNVERIFIED_CLAIMS = [
"76% more bird species - no source, no conditions",
"50% more mammal species - no source, no conditions",
"peatlands store 2x forest biomass C - true but used as conclusion not constraint",
"99% methane reduction with Asparagopsis - in vitro only, in vivo variable 21-98%",
]
