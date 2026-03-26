# cascade_engine.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Cascade integration engine.
# Accepts a forcing function applied at any layer.
# Propagates consequences through all coupled systems.
# Shows where forcing resonates, where it damps, where thresholds exist.
# This is the reason the layer stack exists.

import numpy as np
from dataclasses import dataclass, field
from typing import Any

from layer_0_electromagnetics import coupling_state as em_state
from layer_1_magnetosphere    import coupling_state as mag_state
from layer_2_ionosphere       import coupling_state as iono_state
from layer_3_atmosphere       import coupling_state as atmo_state
from layer_4_hydrosphere      import coupling_state as hydro_state
from layer_5_lithosphere      import coupling_state as litho_state
from layer_6_biosphere        import coupling_state as bio_state

# ─────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class Forcing:
    """
    A forcing function applied at a specific layer.
    layer        : 0-6 target layer
    variable     : which state variable is perturbed
    magnitude    : size of perturbation (units depend on variable)
    description  : human-readable description
    """
    layer       : int
    variable    : str
    magnitude   : float
    description : str
    units       : str = ""


@dataclass
class CascadeResult:
    """
    Full cascade propagation result.
    """
    forcing             : Forcing
    layer_states        : dict = field(default_factory=dict)
    cascade_signals     : list = field(default_factory=list)
    threshold_crossings : list = field(default_factory=list)
    amplifying_loops    : list = field(default_factory=list)
    damping_signals     : list = field(default_factory=list)
    summary             : dict = field(default_factory=dict)
    assumption_violations : list = field(default_factory=list)


# ─────────────────────────────────────────────
# BASELINE STATE
# Current Earth system state — 2024 approximate values
# ─────────────────────────────────────────────

BASELINE = {
    # Layer 0 — Electromagnetics
    "n_e":              1e12,       # F2 electron density m^-3
    "B_surface":        5e-5,       # Earth surface field T
    "E_surface":        1e-4,       # surface electric field V/m
    "freq_range":       (1e3, 1e7), # Hz

    # Layer 1 — Magnetosphere
    "n_sw":             5e6,        # solar wind density m^-3
    "v_sw":             450e3,      # solar wind speed m/s
    "Bz_imf":           -2e-9,      # IMF Bz T (slightly southward)
    "kp":               2.0,        # quiet geomagnetic conditions

    # Layer 2 — Ionosphere
    "n_e_F2":           1e12,       # F2 peak electron density
    "solar_flux":       1.0,        # normalized quiet sun
    "nu_en":            1e3,        # electron-neutral collision Hz
    "E_convection":     1e-3,       # convection electric field V/m
    "delta_T_thermo":   0.0,        # thermosphere anomaly K

    # Layer 3 — Atmosphere
    "T_surface":        288.0,      # K global mean surface temp
    "T_pole":           243.0,      # K polar temperature
    "P_surface":        101325.0,   # Pa
    "q_surface":        0.010,      # specific humidity kg/kg
    "delta_CO2":        140.0,      # ppm above pre-industrial
    "AOD":              0.15,       # aerosol optical depth
    "latitude":         45.0,       # reference latitude deg
    "delta_omega":      0.0,        # rotation perturbation rad/s

    # Layer 4 — Hydrosphere
    "T_ocean_C":        15.0,       # mean SST °C
    "S_ocean":          35.0,       # salinity PSU
    "T_north_C":        8.0,        # N Atlantic °C
    "S_north":          35.0,       # N Atlantic salinity
    "T_south_C":        26.0,       # equatorial Atlantic °C
    "S_south":          36.0,       # equatorial salinity
    "ice_fraction":     0.85,       # Arctic ice fraction (reduced)
    "wind_stress":      0.10,       # Pa
    "delta_S_melt":     0.10,       # PSU reduction from meltwater
    "SST_enso":         0.0,        # ENSO anomaly K
    "AMOC_Sv":          16.0,       # current weakened AMOC

    # Layer 5 — Lithosphere
    "ice_mass_loss_Gt": 280.0,      # cumulative Gt
    "SLR_m":            0.20,       # sea level rise m
    "lat_ice":          71.0,       # Greenland
    "lon_ice":          -40.0,
    "fault_depth_m":    10e3,       # m
    "SO2_volcanic":     0.0,        # Tg

    # Layer 6 — Biosphere
    "T_surface_K":      288.0,
    "CO2_ppm":          420.0,
    "ocean_pH":         8.10,
    "permafrost_area":  1.5e13,     # m^2
    "T_permafrost_anom":1.5,        # K above threshold
    "deforestation":    0.20,       # Amazon fraction cleared
    "delta_T_amazon":   1.5,        # K regional warming
    "drought_index":    0.4,
    "GPP_GtC":          120.0,
    "anthro_GtC":       10.0,
    "AMOC_bio_Sv":      16.0,
}


# ─────────────────────────────────────────────
# LAYER RUNNERS
# Each runs its coupling_state with current parameter set
# ─────────────────────────────────────────────

def run_all_layers(p):
    """
    Run all seven layer coupling states with parameter set p.
    Returns dict of layer outputs.
    """
    states = {}

    states[0] = em_state(
        n_e          = p["n_e"],
        B_surface    = p["B_surface"],
        E_surface    = p["E_surface"],
        frequency_range = p["freq_range"],
    )
    states[1] = mag_state(
        B_surface    = p["B_surface"],
        n_sw         = p["n_sw"],
        v_sw         = p["v_sw"],
        Bz_imf       = p["Bz_imf"],
        kp           = p["kp"],
        delta_omega  = p["delta_omega"],
    )
    states[2] = iono_state(
        n_e_F2       = p["n_e_F2"],
        B_surface    = p["B_surface"],
        kp           = p["kp"],
        solar_flux   = p["solar_flux"],
        nu_en        = p["nu_en"],
        E_field      = p["E_convection"],
        delta_T_thermo = p["delta_T_thermo"],
    )
    states[3] = atmo_state(
        T_surface    = p["T_surface"],
        T_pole       = p["T_pole"],
        P_surface    = p["P_surface"],
        q_surface    = p["q_surface"],
        delta_CO2_ppm= p["delta_CO2"],
        AOD          = p["AOD"],
        latitude_deg = p["latitude"],
        delta_omega  = p["delta_omega"],
    )
    states[4] = hydro_state(
        T_ocean_C    = p["T_ocean_C"],
        S_ocean      = p["S_ocean"],
        T_north_C    = p["T_north_C"],
        S_north      = p["S_north"],
        T_south_C    = p["T_south_C"],
        S_south      = p["S_south"],
        ice_fraction = p["ice_fraction"],
        wind_stress  = p["wind_stress"],
        delta_S_melt = p["delta_S_melt"],
        SST_enso_anomaly = p["SST_enso"],
        AMOC_Sv      = p["AMOC_Sv"],
    )
    states[5] = litho_state(
        ice_mass_loss_Gt = p["ice_mass_loss_Gt"],
        SLR_m            = p["SLR_m"],
        T_ocean_C        = p["T_ocean_C"],
        lat_ice          = p["lat_ice"],
        lon_ice          = p["lon_ice"],
        fault_depth_m    = p["fault_depth_m"],
        SO2_volcanic_Tg  = p["SO2_volcanic"],
    )
    states[6] = bio_state(
        T_surface_K      = p["T_surface_K"],
        CO2_ppm          = p["CO2_ppm"],
        ocean_pH         = p["ocean_pH"],
        permafrost_area_m2 = p["permafrost_area"],
        T_permafrost_anomaly = p["T_permafrost_anom"],
        deforestation_fraction = p["deforestation"],
        delta_T_amazon   = p["delta_T_amazon"],
        drought_index    = p["drought_index"],
        GPP_GtC_yr       = p["GPP_GtC"],
        anthropogenic_GtC_yr = p["anthro_GtC"],
        AMOC_Sv          = p["AMOC_bio_Sv"],
    )
    return states


# ─────────────────────────────────────────────
# THRESHOLD SCANNER
# ─────────────────────────────────────────────

THRESHOLDS = [
    # (layer, key, comparator, value, label, reversible)
    (4, "AMOC_collapse_risk",      lambda v, _: v is True,     None,
        "AMOC collapse imminent — irreversible thermohaline shutdown",       False),
    (6, "amazon_tipping_imminent", lambda v, _: v is True,     None,
        "Amazon tipping point imminent — forest-savanna transition",         False),
    (6, "coral_dissolution_active",lambda v, _: v is True,     None,
        "Coral dissolution active — aragonite saturation below 1.0",        False),
    (6, "permafrost_self_amplifying", lambda v, _: v is True,  None,
        "Permafrost feedback self-amplifying — irreversible at scale",       False),
    (6, "NEP_carbon_sink",         lambda v, _: v is False,    None,
        "Terrestrial biosphere flipped to carbon source",                    False),
    (3, "convection_active",       lambda v, _: v is True,     None,
        "Atmospheric convective instability active",                         True),
    (4, "committed_warming_timescale_yr", lambda v, t: v > t,  200,
        "Committed warming timescale exceeds 200 years",                     False),
    (6, "planetary_boundaries_crossed", lambda v, t: v >= t,   6,
        "Six or more planetary boundaries crossed simultaneously",           False),
    (5, "volcanic_enhancement",    lambda v, t: v > t,         1.5,
        "Volcanic activity enhanced >50% above baseline",                    True),
    (1, "cascade_to_ionosphere",   lambda v, _: v is True,     None,
        "Magnetospheric energy actively coupling into ionosphere",           True),
]


def scan_thresholds(states):
    """
    Check all layer states against known threshold conditions.
    Returns list of active threshold crossings.
    """
    crossings = []
    for layer, key, comparator, value, label, reversible in THRESHOLDS:
        state = states.get(layer, {})
        v = state.get(key)
        if v is None:
            continue
        try:
            if comparator(v, value):
                crossings.append({
                    "layer":       layer,
                    "variable":    key,
                    "value":       v,
                    "label":       label,
                    "reversible":  reversible,
                })
        except Exception:
            continue
    return crossings


# ─────────────────────────────────────────────
# CASCADE SIGNAL TRACER
# ─────────────────────────────────────────────

CASCADE_MAP = {
    # (source_layer, signal) -> [(target_layer, mechanism, amplifying)]

    # ── LAYER 0 — ELECTROMAGNETICS ──────────────────────────────────
    (0, "plasma_frequency_Hz"):       [(2, "ionospheric reflection cutoff shift", True),
                                       (1, "magnetospheric wave coupling change", True)],
    (0, "skin_depth_m"):              [(5, "ground-penetrating EM attenuation change", False),
                                       (2, "ionospheric absorption depth change", True)],
    (0, "cyclotron_frequency_Hz"):    [(1, "particle trapping resonance shift", True)],

    # ── LAYERS 1-6 ──────────────────────────────────────────────────
    (3, "GHG_forcing_Wm2"):        [(4, "SST increase", True),
                                    (6, "GPP/respiration shift", True),
                                    (5, "ice melt -> LOD", True)],
    (4, "AMOC_collapse_risk"):     [(3, "N Atlantic cooling / redistribution", False),
                                    (6, "marine productivity collapse", False),
                                    (2, "SST -> ionosphere via atmosphere", False)],
    (6, "permafrost_self_amplifying"):[(3, "CO2+CH4 forcing", True),
                                       (4, "additional warming -> more melt", True)],
    (5, "LOD_change_ms"):          [(1, "rotation -> field geometry", True),
                                    (3, "Coriolis shift -> circulation", True)],
    (6, "amazon_tipping_imminent"):[(3, "CO2 release + albedo change", True),
                                    (4, "continental precipitation collapse", False)],
    (2, "cascade_to_atmosphere"):  [(3, "joule heating -> thermosphere winds", True),
                                    (3, "gravity wave modulation", False)],
    (4, "ice_albedo_feedback_Wm2"):[(3, "additional absorbed radiation", True),
                                    (6, "habitat loss", False)],
    (5, "volcanic_enhancement"):   [(3, "SO2 -> aerosol cooling", False),
                                    (6, "reduced photosynthesis", False),
                                    (3, "CO2 from enhanced outgassing", True)],
}


def trace_cascade_signals(states, forcing):
    """
    Trace active cascade signals from forcing through coupled layers.
    Returns list of active signal pathways.
    """
    signals = []
    for (src_layer, key), targets in CASCADE_MAP.items():
        state = states.get(src_layer, {})
        value = state.get(key)
        if value is None:
            continue
        active = False
        if isinstance(value, bool) and value:
            active = True
        elif isinstance(value, (int, float)) and abs(value) > 1e-10:
            active = True
        if active:
            for tgt_layer, mechanism, amplifying in targets:
                signals.append({
                    "source_layer":  src_layer,
                    "target_layer":  tgt_layer,
                    "signal_key":    key,
                    "signal_value":  value,
                    "mechanism":     mechanism,
                    "amplifying":    amplifying,
                })
    return signals


# ─────────────────────────────────────────────
# SELF-AMPLIFYING LOOP DETECTOR
# ─────────────────────────────────────────────

KNOWN_LOOPS = [
    {
        "name":     "Ice-Albedo",
        "layers":   [3, 4, 6],
        "trigger":  lambda s: s[4].get("ice_albedo_feedback_Wm2", 0) > 0.5,
        "gain_function": lambda s: 1.0 + (
            s[4].get("ice_albedo_feedback_Wm2", 0) /
            max(abs(s[3].get("GHG_forcing_Wm2", 1.0)), 0.01)
        ),
        "description": "ice loss -> darker surface -> more absorption -> more melt",
        "timescale": "years to decades",
    },
    {
        "name":     "Permafrost-CH4",
        "layers":   [5, 6, 3],
        "trigger":  lambda s: s[6].get("permafrost_self_amplifying", False),
        "gain_function": lambda s: 1.0 + (
            (s[6].get("permafrost_CO2_GtC_yr", 0) + s[6].get("permafrost_CH4_GtC_yr", 0) * 28) /
            max(s[6].get("atmospheric_CO2_accumulation", 1.0), 0.01)
        ),
        "description": "permafrost thaw -> CH4/CO2 -> warming -> more thaw",
        "timescale": "decades to centuries",
    },
    {
        "name":     "Amazon-CO2",
        "layers":   [6, 3],
        "trigger":  lambda s: s[6].get("amazon_tipping_proximity", 0) > 0.6,
        "gain_function": lambda s: 1.0 + s[6].get("amazon_tipping_proximity", 0),
        "description": "dieback -> CO2+albedo change -> warming -> more dieback",
        "timescale": "decades",
    },
    {
        "name":     "AMOC-SST",
        "layers":   [4, 3, 4],
        "trigger":  lambda s: s[4].get("AMOC_Sv", 17) < 15,
        "gain_function": lambda s: 1.0 + max(0, (17.0 - s[4].get("AMOC_Sv", 17)) / 17.0),
        "description": "AMOC weakening -> N Atlantic cooling -> atmospheric changes -> further weakening",
        "timescale": "decades to centuries",
    },
    {
        "name":     "Stratification-Productivity",
        "layers":   [4, 6, 3],
        "trigger":  lambda s: s[6].get("marine_productivity_change", 0) < -0.05,
        "gain_function": lambda s: 1.0 + abs(min(s[6].get("marine_productivity_change", 0), 0)),
        "description": "warming -> stratification -> less uptake -> more CO2 -> more warming",
        "timescale": "decades",
    },
    {
        "name":     "Rotation-Coriolis",
        "layers":   [5, 1, 3],
        "trigger":  lambda s: abs(s[5].get("LOD_change_ms", 0)) > 0.5,
        "gain_function": lambda s: 1.0 + abs(s[5].get("LOD_change_ms", 0)) / 5.0,
        "description": "ice melt -> LOD change -> Coriolis shift -> circulation change -> field geometry",
        "timescale": "centuries",
    },
    {
        "name":     "Volcanic-Deglaciation",
        "layers":   [5, 3, 4],
        "trigger":  lambda s: s[5].get("volcanic_enhancement", 1.0) > 1.2,
        "gain_function": lambda s: s[5].get("volcanic_enhancement", 1.0),
        "description": "ice unloading -> volcanic enhancement -> SO2/CO2 -> warming -> more unloading",
        "timescale": "centuries",
    },
]


def detect_amplifying_loops(states):
    """
    Detect which self-amplifying feedback loops are currently active.
    Returns gain per active loop:
      gain < 1.0: dissipative (loop is damping)
      gain = 1.0: neutral
      gain > 1.0: amplifying
    """
    active = []
    for loop in KNOWN_LOOPS:
        try:
            if loop["trigger"](states):
                gain = 1.0
                gain_fn = loop.get("gain_function")
                if gain_fn is not None:
                    try:
                        gain = gain_fn(states)
                    except Exception:
                        gain = 1.0
                active.append({
                    "name":        loop["name"],
                    "layers":      loop["layers"],
                    "description": loop["description"],
                    "timescale":   loop["timescale"],
                    "gain":        gain,
                })
        except Exception:
            continue
    return active


# ─────────────────────────────────────────────
# PERTURBATION RUNNER
# Apply forcing delta to baseline and compare states
# ─────────────────────────────────────────────

FORCING_PARAM_MAP = {
    # forcing variable -> baseline parameter key
    "CO2_ppm":          ["delta_CO2", "CO2_ppm"],
    "T_surface":        ["T_surface", "T_surface_K"],
    "T_pole":           ["T_pole"],
    "ice_mass_loss_Gt": ["ice_mass_loss_Gt"],
    "delta_S_melt":     ["delta_S_melt"],
    "AMOC_Sv":          ["AMOC_Sv", "AMOC_bio_Sv"],
    "kp":               ["kp"],
    "Bz_imf":           ["Bz_imf"],
    "SO2_volcanic":     ["SO2_volcanic"],
    "deforestation":    ["deforestation"],
    "AOD":              ["AOD"],
    "delta_omega":      ["delta_omega"],
    "T_permafrost_anom":["T_permafrost_anom"],
    "drought_index":    ["drought_index"],
    "v_sw":             ["v_sw"],
    "SST_enso":         ["SST_enso"],
    "n_e":              ["n_e", "n_e_F2"],
    "B_surface":        ["B_surface"],
    "n_sw":             ["n_sw"],
}


def apply_forcing(baseline, forcing):
    """
    Apply a forcing perturbation to baseline parameters.
    Returns perturbed parameter set.
    Raises ValueError if forcing variable is not recognized.
    """
    p = dict(baseline)
    keys = FORCING_PARAM_MAP.get(forcing.variable, [forcing.variable])
    matched = [k for k in keys if k in p]
    if not matched:
        known = sorted(set(FORCING_PARAM_MAP.keys()) | set(baseline.keys()))
        raise ValueError(
            f"Unknown forcing variable '{forcing.variable}'. "
            f"Valid variables: {known}"
        )
    for key in matched:
        p[key] = p[key] + forcing.magnitude
    return p


# ─────────────────────────────────────────────
# MAIN CASCADE ENGINE
# ─────────────────────────────────────────────

def run_cascade(forcing, baseline=None, verbose=True, audit_energy=False):
    """
    Full cascade analysis from a single forcing.
    forcing      : Forcing dataclass instance
    baseline     : parameter dict (uses BASELINE if None)
    verbose      : print report
    audit_energy : if True, run energy conservation audit after cascade
    returns      : CascadeResult
    """
    if baseline is None:
        baseline = dict(BASELINE)

    # Baseline states
    baseline_states   = run_all_layers(baseline)

    # Perturbed states
    perturbed_params  = apply_forcing(baseline, forcing)
    perturbed_states  = run_all_layers(perturbed_params)

    # Analysis
    thresholds  = scan_thresholds(perturbed_states)
    signals     = trace_cascade_signals(perturbed_states, forcing)
    loops       = detect_amplifying_loops(perturbed_states)

    # Assumption validator — check for violations (lazy import to avoid circular dependency)
    from assumption_validator.registry import full_report as validator_full_report
    validity_report = validator_full_report(perturbed_states)
    violations = []
    for aid, data in validity_report.get("assumptions", {}).items():
        status = data.get("status")
        if status in ("YELLOW", "RED"):
            violations.append({
                "assumption_id": aid,
                "name":          data.get("name", aid),
                "status":        status,
                "value":         data.get("value"),
                "units":         data.get("units", ""),
                "source_layer":  data.get("source_layer"),
                "notes":         data.get("notes", ""),
            })

    # Separate amplifying vs damping signals
    amplifying = [s for s in signals if s["amplifying"]]
    damping    = [s for s in signals if not s["amplifying"]]

    # Compute layer-level delta summary
    delta_summary = {}
    for layer in range(7):
        bs = baseline_states.get(layer, {})
        ps = perturbed_states.get(layer, {})
        deltas = {}
        for key in bs:
            bv = bs[key]
            pv = ps.get(key)
            if isinstance(bv, (int, float)) and isinstance(pv, (int, float)):
                delta = pv - bv
                if abs(delta) > 1e-30:
                    deltas[key] = {"baseline": bv, "perturbed": pv, "delta": delta}
        if deltas:
            delta_summary[layer] = deltas

    result = CascadeResult(
        forcing             = forcing,
        layer_states        = perturbed_states,
        cascade_signals     = signals,
        threshold_crossings = thresholds,
        amplifying_loops    = loops,
        damping_signals     = damping,
        summary             = delta_summary,
        assumption_violations = violations,
    )

    if verbose:
        _print_report(result)

    if audit_energy:
        from energy_audit import audit_energy as _audit
        _audit(forcing, baseline, verbose=verbose)

    return result


# ─────────────────────────────────────────────
# REVERSE MAP: layer output key -> forcing variable
# Used by iterative cascade solver
# ─────────────────────────────────────────────

def _build_output_to_forcing_map():
    """
    Build a reverse map from known layer output keys to forcing variable names.
    Only maps keys that appear in FORCING_PARAM_MAP.
    """
    reverse = {}
    # Direct baseline keys that are also forcing variables
    for forcing_var, baseline_keys in FORCING_PARAM_MAP.items():
        for bk in baseline_keys:
            reverse[bk] = forcing_var
    return reverse

_OUTPUT_TO_FORCING = _build_output_to_forcing_map()


# ─────────────────────────────────────────────
# ITERATIVE CASCADE SOLVER
# ─────────────────────────────────────────────

def run_cascade_iterative(forcing, baseline=None, max_steps=20,
                          convergence_threshold=1e-6, verbose=True):
    """
    Iterate cascade until:
    - deltas converge (stable state)
    - deltas diverge (runaway detected)
    - max_steps reached (report non-convergence)

    forcing              : Forcing dataclass instance
    baseline             : parameter dict (uses BASELINE if None)
    max_steps            : maximum iteration count
    convergence_threshold: delta magnitude below which variable is considered converged
    verbose              : print report
    returns              : CascadeResult with iteration_history field in summary
    """
    if baseline is None:
        baseline = dict(BASELINE)

    baseline_states = run_all_layers(baseline)
    current_params = apply_forcing(baseline, forcing)
    iteration_history = []
    converged = False
    diverged = False
    divergence_drivers = []

    prev_max_delta = None

    for step in range(max_steps):
        perturbed_states = run_all_layers(current_params)

        # Compute deltas between perturbed and baseline
        step_deltas = {}
        for layer in range(7):
            bs = baseline_states.get(layer, {})
            ps = perturbed_states.get(layer, {})
            for key in bs:
                bv = bs[key]
                pv = ps.get(key)
                if isinstance(bv, (int, float)) and isinstance(pv, (int, float)):
                    delta = pv - bv
                    if abs(delta) > 1e-30:
                        step_deltas[(layer, key)] = delta

        iteration_history.append(dict(step_deltas))

        # Check convergence: all deltas below threshold
        max_delta = max((abs(d) for d in step_deltas.values()), default=0)
        significant = {k: d for k, d in step_deltas.items()
                       if abs(d) > convergence_threshold}

        if not significant:
            converged = True
            break

        # Check divergence: max delta growing step-over-step
        if prev_max_delta is not None and max_delta > prev_max_delta * 1.01:
            # Find which variables are driving divergence
            if len(iteration_history) >= 2:
                prev_deltas = iteration_history[-2]
                for k, d in step_deltas.items():
                    pd = prev_deltas.get(k, 0)
                    if abs(d) > abs(pd) * 1.01 and abs(d) > convergence_threshold:
                        divergence_drivers.append({
                            "layer": k[0],
                            "variable": k[1],
                            "delta": d,
                            "prev_delta": pd,
                        })
            if divergence_drivers:
                diverged = True
                break

        prev_max_delta = max_delta

        # Generate secondary forcings from deltas that exceed threshold
        secondary_applied = False
        for (layer, key), delta in significant.items():
            # Try to map this output key back to a forcing variable
            forcing_var = _OUTPUT_TO_FORCING.get(key)
            if forcing_var is None:
                continue
            # Apply as secondary perturbation (fraction of delta)
            param_keys = FORCING_PARAM_MAP.get(forcing_var, [forcing_var])
            for pk in param_keys:
                if pk in current_params:
                    current_params[pk] = current_params[pk] + delta * 0.1
                    secondary_applied = True

        if not secondary_applied:
            # No mappable deltas found — converged by exhaustion
            converged = True
            break

    # Final analysis on last state
    final_states = run_all_layers(current_params)
    thresholds = scan_thresholds(final_states)
    signals = trace_cascade_signals(final_states, forcing)
    loops = detect_amplifying_loops(final_states)

    from assumption_validator.registry import full_report as validator_full_report
    validity_report = validator_full_report(final_states)
    violations = []
    for aid, data in validity_report.get("assumptions", {}).items():
        status = data.get("status")
        if status in ("YELLOW", "RED"):
            violations.append({
                "assumption_id": aid,
                "name":          data.get("name", aid),
                "status":        status,
                "value":         data.get("value"),
                "units":         data.get("units", ""),
                "source_layer":  data.get("source_layer"),
                "notes":         data.get("notes", ""),
            })

    amplifying = [s for s in signals if s["amplifying"]]
    damping = [s for s in signals if not s["amplifying"]]

    # Delta summary for final state
    delta_summary = {}
    for layer in range(7):
        bs = baseline_states.get(layer, {})
        ps = final_states.get(layer, {})
        deltas = {}
        for key in bs:
            bv = bs[key]
            pv = ps.get(key)
            if isinstance(bv, (int, float)) and isinstance(pv, (int, float)):
                d = pv - bv
                if abs(d) > 1e-30:
                    deltas[key] = {"baseline": bv, "perturbed": pv, "delta": d}
        if deltas:
            delta_summary[layer] = deltas

    # Build iteration metadata
    n_steps = len(iteration_history)
    if converged:
        status_str = f"CONVERGED in {n_steps} steps"
    elif diverged:
        status_str = f"DIVERGED at step {n_steps}"
    else:
        status_str = f"NON-CONVERGENT after {max_steps} steps"

    delta_summary["_iteration"] = {
        "steps": n_steps,
        "converged": converged,
        "diverged": diverged,
        "status": status_str,
        "divergence_drivers": divergence_drivers,
        "iteration_history": iteration_history,
    }

    result = CascadeResult(
        forcing=forcing,
        layer_states=final_states,
        cascade_signals=signals,
        threshold_crossings=thresholds,
        amplifying_loops=loops,
        damping_signals=damping,
        summary=delta_summary,
        assumption_violations=violations,
    )

    if verbose:
        _print_iterative_report(result)

    return result


def _print_iterative_report(result):
    """Print report for iterative cascade, then delegate to standard report."""
    meta = result.summary.get("_iteration", {})
    print("=" * 64)
    print("ITERATIVE CASCADE ANALYSIS")
    print("=" * 64)
    print(f"  Status     : {meta.get('status', 'unknown')}")
    print(f"  Iterations : {meta.get('steps', 0)}")

    if meta.get("diverged") and meta.get("divergence_drivers"):
        print("  DIVERGENCE DRIVERS:")
        for d in meta["divergence_drivers"]:
            print(f"    L{d['layer']} {d['variable']}  "
                  f"delta={d['delta']:+.4g}  prev={d['prev_delta']:+.4g}")
    print()

    _print_report(result)


# ─────────────────────────────────────────────
# REPORT PRINTER
# ─────────────────────────────────────────────

LAYER_NAMES = {
    0: "Electromagnetics",
    1: "Magnetosphere",
    2: "Ionosphere",
    3: "Atmosphere",
    4: "Hydrosphere",
    5: "Lithosphere",
    6: "Biosphere",
}


def _print_report(result):
    r = result
    f = r.forcing
    print("=" * 64)
    print("CASCADE ANALYSIS")
    print("=" * 64)
    print(f"FORCING    : {f.description}")
    print(f"  Layer    : {f.layer} — {LAYER_NAMES[f.layer]}")
    print(f"  Variable : {f.variable}")
    print(f"  Delta    : {f.magnitude:+.4g} {f.units}")
    print()

    if r.threshold_crossings:
        print("─" * 64)
        print("THRESHOLD CROSSINGS")
        for t in r.threshold_crossings:
            rev = "reversible" if t["reversible"] else "IRREVERSIBLE"
            print(f"  [L{t['layer']}] {t['label']}")
            print(f"       {rev}")
    else:
        print("  No threshold crossings detected")
    print()

    if r.amplifying_loops:
        print("─" * 64)
        print("ACTIVE SELF-AMPLIFYING LOOPS")
        for loop in r.amplifying_loops:
            layers_str = " -> ".join(
                f"L{l}({LAYER_NAMES[l]})" for l in loop["layers"]
            )
            gain = loop.get("gain", 1.0)
            if gain > 1.0:
                gain_label = f"AMPLIFYING (gain={gain:.3f})"
            elif gain < 1.0:
                gain_label = f"dissipative (gain={gain:.3f})"
            else:
                gain_label = f"neutral (gain={gain:.3f})"
            print(f"  [{loop['name']}]  {loop['timescale']}  {gain_label}")
            print(f"    {loop['description']}")
            print(f"    Path: {layers_str}")
    else:
        print("  No self-amplifying loops active")
    print()

    if r.cascade_signals:
        print("─" * 64)
        print("CASCADE SIGNAL PATHWAYS")
        for s in r.cascade_signals:
            amp = "↑ AMPLIFYING" if s["amplifying"] else "↓ damping"
            print(f"  L{s['source_layer']}({LAYER_NAMES[s['source_layer']]}) "
                  f"-> L{s['target_layer']}({LAYER_NAMES[s['target_layer']]})  "
                  f"{amp}")
            print(f"    via: {s['mechanism']}")
    print()

    if r.assumption_violations:
        print("─" * 64)
        print("ASSUMPTION VIOLATIONS")
        for v in r.assumption_violations:
            sev = v["status"]
            marker = "!!" if sev == "RED" else " !"
            print(f"  {marker} [{sev}] L{v['source_layer']} {v['name']}")
            print(f"       value={v['value']}  {v['units']}")
            if v["notes"]:
                print(f"       {v['notes']}")
    else:
        print("  No assumption violations")
    print()

    print("─" * 64)
    print("LAYER DELTA SUMMARY  (significant changes only)")
    for layer, deltas in r.summary.items():
        if not isinstance(layer, int):
            continue  # skip metadata keys like _iteration
        print(f"  Layer {layer} — {LAYER_NAMES[layer]}")
        for key, vals in list(deltas.items())[:5]:  # top 5 per layer
            print(f"    {key:40s}  "
                  f"baseline={vals['baseline']:+.4g}  "
                  f"delta={vals['delta']:+.4g}")
    print("=" * 64)


# ─────────────────────────────────────────────
# CONVENIENCE SCENARIOS
# Ready to run — remove or expand as needed
# ─────────────────────────────────────────────

SCENARIOS = {
    "co2_pulse_100ppm": Forcing(
        layer=3, variable="CO2_ppm", magnitude=100.0,
        description="100 ppm CO2 pulse above current", units="ppm"
    ),
    "amoc_collapse": Forcing(
        layer=4, variable="AMOC_Sv", magnitude=-8.0,
        description="AMOC weakening 8 Sv — partial collapse", units="Sv"
    ),
    "greenland_pulse": Forcing(
        layer=5, variable="ice_mass_loss_Gt", magnitude=500.0,
        description="500 Gt Greenland melt pulse", units="Gt"
    ),
    "solar_storm_kp8": Forcing(
        layer=1, variable="kp", magnitude=6.0,
        description="Major geomagnetic storm Kp=8", units="Kp"
    ),
    "amazon_dieback": Forcing(
        layer=6, variable="deforestation", magnitude=0.15,
        description="Amazon deforestation reaches 35%", units="fraction"
    ),
    "sulfate_geoengineering": Forcing(
        layer=3, variable="AOD", magnitude=0.15,
        description="Stratospheric aerosol injection — AOD +0.15", units="AOD"
    ),
    "permafrost_acceleration": Forcing(
        layer=6, variable="T_permafrost_anom", magnitude=1.5,
        description="Permafrost warming +1.5K above current", units="K"
    ),
    "rotation_slowdown": Forcing(
        layer=5, variable="delta_omega", magnitude=-1.4e-14,
        description="LOD increase 1ms from ice melt redistribution", units="rad/s"
    ),
    "solar_proton_event": Forcing(
        layer=0, variable="n_e", magnitude=1e13,
        description="Solar proton event — ionospheric electron density surge", units="m^-3"
    ),
    "co2_pulse_iterative": Forcing(
        layer=3, variable="CO2_ppm", magnitude=100.0,
        description="100 ppm CO2 pulse — iterative cascade", units="ppm"
    ),
}


if __name__ == "__main__":
    # Run all standard scenarios
    for name, scenario in SCENARIOS.items():
        if name == "co2_pulse_iterative":
            continue  # run separately below
        print(f"\n{'#'*64}")
        print(f"# SCENARIO: {name}")
        print(f"{'#'*64}")
        run_cascade(scenario)

    # Run iterative cascade scenario
    print(f"\n{'#'*64}")
    print(f"# SCENARIO: co2_pulse_iterative (ITERATIVE)")
    print(f"{'#'*64}")
    run_cascade_iterative(SCENARIOS["co2_pulse_iterative"])
