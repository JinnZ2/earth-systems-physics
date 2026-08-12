# config.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Centralised tunable parameters. All model assumptions (linearity,
# additivity, memory, thresholds) are exposed here or as model kwargs so an
# audit — or an AI in the meta-experiment loop — can vary them systematically.

# Rate constants are per HOUR. They are deliberately small so biomass persists
# at a healthy equilibrium (~60 gC) under benign forcing over multi-day
# horizons and only collapses under sustained heat — the contrast every audit
# depends on. (An earlier draft used ~0.1/hr loss rates, which decayed the
# stand to zero regardless of stress and erased the survives-vs-collapses
# signal.) At these constants: benign 22-24 C -> ~60; 34 C -> ~15; 36 C -> ~10.
GRASS_DEFAULTS = {
    "P_max": 2.0,         # max photosynthetic flux (gC/hr)
    "T_opt": 25.0,        # optimal temperature (deg C)
    "sigma": 8.0,         # width of the Gaussian photosynthesis curve (deg C)
    "R_base": 0.01,       # base respiration rate at 20 deg C (1/hr)
    "Q10": 2.0,           # respiration temperature sensitivity (dimensionless)
    "transfer": 0.004,    # biomass -> soil carbon transfer (1/hr)
}

SIM_DEFAULTS = {
    "duration_hours": 100.0,   # default integration horizon (hr)
    "max_step": 1.0,           # max integrator step (hr)
    "rtol": 1e-5,              # loosened for CI speed; forcing is smooth in t
    "atol": 1e-7,
}

FORCING_DEFAULTS = {
    "T_mean": 20.0,       # mean temperature (deg C)
    "amplitude": 10.0,    # diurnal amplitude (deg C)
    "day_fraction": 0.5,  # fraction of the 24 hr period that is lit
    "period": 24.0,       # diurnal period (hr)
}
