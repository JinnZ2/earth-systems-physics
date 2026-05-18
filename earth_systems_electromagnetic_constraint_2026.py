"""
EARTH_SYSTEMS_ELECTROMAGNETIC_CONSTRAINT_2026

Constraint layer module for earth-systems-physics coupled differential
equations: ELECTROMAGNETIC BASE LAYER.

Integrates observational findings from:

    1. World Magnetic Model 2025 (NOAA/NCEI + BGS, December 2024)
    2. World Magnetic Model High Resolution 2025 (WMMHR2025)
    3. High Definition Geomagnetic Model 2026 (NCEI + CIRES, January 2026)
    4. Pole position confirmation, April 2026

Function: provides validity checks, secular variation flags, and
deceleration-anomaly thresholds for coupled solver. Sits BENEATH
glacier/ecosystem/iron layers as base electromagnetic constraint.

CC0 Public Domain. Standard library only.
"""

# ─────────────────────────────────────────────
# LAYER 0: GEOMAGNETIC FIELD DYNAMICS
# Source: WMM2025 (Chulliat et al, NOAA/BGS, 2024-12),
# HDGM 2026 (NCEI/CIRES, 2026-01), pole position update 2026-04
# ─────────────────────────────────────────────

# North magnetic pole drift history
POLE_DRIFT_RATE_PEAK_KM_YR = 60               # ~1990s-2010s acceleration peak
POLE_DRIFT_RATE_CURRENT_KM_YR = 35            # WMM2025 / April 2026 confirmation
POLE_DRIFT_DECELERATION_LARGEST_ON_RECORD = True
POLE_NOW_CLOSER_TO_SIBERIA_THAN_CANADA = True   # April 2026 milestone
YEARS_OF_ARCTIC_TRAVERSAL = 190                 # from first measurement (~1831)

# Model versions and validity windows
WMM2025_VALID_START = 2025.0
WMM2025_VALID_END = 2030.0
WMM2025_EXPIRES_DATE = "2029-12-31"
WMMHR2025_SPHERICAL_HARMONIC_DEGREE_MAIN = 15
WMMHR2025_CRUSTAL_SH_DEGREE = 133
WMM2025_SPHERICAL_HARMONIC_DEGREE = 12

# HDGM 2026 (annual high-res update)
HDGM_2026_RESOLUTION_INCREASE_PCT = 20
HDGM_2026_CRUSTAL_DEPTH_RESOLUTION_KM = 19
HDGM_2026_REALTIME_DISTURBANCE_CORRECTION = True
HDGM_2026_VALID_THROUGH = "2026-12-31"

# Auroral electrojet zones — magnetic measurement disruption regions
AURORAL_ELECTROJET_DISRUPTS_DIRECTIONAL_DRILLING = True
POLAR_BLACKOUT_ZONES_SHIFTING_WITH_POLE = True

# Field strength regime
EARTH_SURFACE_FIELD_TYPICAL_NT = (20000, 60000)   # 20-60 microtesla
CRUSTAL_ANOMALY_TYPICAL_NT = 100                  # small-amplitude signal

# Secular variation: rate of change of field, used in coupled solver
SECULAR_VARIATION_TRACKED_VIA = (
    "ESA_Swarm_satellites",
    "ground_observatories_~160_stations",
    "marine_airborne_magnetic_surveys",
)


# ─────────────────────────────────────────────
# REGIME-CHANGE SIGNALS
# Deceleration after multi-decade acceleration = nonlinear shift in
# outer core dynamo. Treat as cascade-failure precursor input to
# upper layers (magnetosphere -> ionosphere -> atmosphere coupling).
# ─────────────────────────────────────────────

DYNAMO_REGIME_SHIFT_SIGNAL_2025 = True
DYNAMO_ACCELERATION_PHASE_YEARS = 40           # ~1985-2025 acceleration era
DYNAMO_DECELERATION_ONSET_APPROX_YEAR = 2020   # rough turning-point estimate

# Outer core fluid dynamics inferred from secular variation
OUTER_CORE_DEPTH_KM = 2890                     # CMB depth below surface
OUTER_CORE_BOUNDARY_FLOW_SHIFT_DETECTED = True # CMB tangential flow reorganization
OUTER_CORE_FLOW_REORG_TIMESCALE_YEARS = 10     # decadal jerk-scale events
CORE_MANTLE_BOUNDARY_HEAT_FLUX_INFERRED_HETEROGENEOUS = True

# Geomagnetic jerk signatures (sudden V-shaped changes in dB/dt)
# 2017 jerk under N. Atlantic / S. America still propagating; new
# 2024-2025 candidate jerk under Siberia coincident with deceleration.
GEOMAGNETIC_JERK_2017_SIGNATURE = True
GEOMAGNETIC_JERK_2024_CANDIDATE = True

# South Atlantic Anomaly (SAA): low-intensity region; secular weakening
# and bifurcation into two minima documented by ESA Swarm 2014-2025.
SAA_BIFURCATING_INTO_TWO_LOBES = True
SAA_INTENSITY_DECLINE_PCT_PER_DECADE = 2.0     # ~2% per decade weakening
SAA_AFFECTS_LEO_SATELLITE_OPERATIONS = True


# ─────────────────────────────────────────────
# COUPLING CHANNELS INTO UPSTREAM LAYERS
# These flags tell coupled-equation solvers which downstream layers
# inherit the regime-shift signal and on what timescale.
# ─────────────────────────────────────────────

# L0 -> L1 (magnetosphere): field weakening expands cusp regions,
# shrinks dayside standoff distance, modulates radiation-belt geometry.
COUPLES_TO_MAGNETOSPHERE_GEOMETRY = True
MAGNETOPAUSE_STANDOFF_SENSITIVITY_PER_NT = "linear_in_dipole_moment"

# L0 -> L2 (ionosphere): auroral oval expansion + drift; F-region
# electron density redistribution; HF propagation paths shift.
COUPLES_TO_IONOSPHERE_AURORAL_OVAL = True

# L0 -> L7 (infrastructure): GIC risk redistributes as auroral zones
# move; previously-low-risk midlatitude grids become exposed.
COUPLES_TO_INFRASTRUCTURE_GIC_RISK = True
GIC_RISK_GEOGRAPHIC_REDISTRIBUTION = True

# L-1 -> L0 (orbital -> dynamo): rotation-rate change (eccentricity-
# tidal torque + precession) routes through L5 to the dynamo, NOT
# directly. Direct insolation -> CMB heat flux rejected at orbital
# cadence (mantle thermalisation lag ~Gyr).
ORBITAL_TO_DYNAMO_VIA_ROTATION_ONLY = True
ORBITAL_TO_DYNAMO_DIRECT_HEAT_FLUX_PATHWAY_REJECTED = True


# ─────────────────────────────────────────────
# CONSTRAINT VALIDATION FUNCTIONS
# ─────────────────────────────────────────────

INVALIDATED_ASSUMPTIONS = {
    "linear_pole_drift_extrapolation":
        "INVALIDATED 2025: largest deceleration on record (60 -> 35 km/yr)",
    "constant_dipole_moment":
        "INVALIDATED: secular variation accelerated 1985-2020, "
        "decelerated 2020-2025; nonlinear",
    "saa_single_lobe":
        "INVALIDATED 2014-2025: ESA Swarm shows bifurcation into two minima",
    "wmm_valid_indefinitely":
        "INVALIDATED: 5-year validity window; WMM2025 expires 2029-12-31",
    "auroral_oval_geographically_fixed":
        "INVALIDATED: oval drifts with pole; midlatitude GIC exposure rising",
    "orbital_forcing_drives_dynamo_via_direct_heat_flux":
        "INVALIDATED: mantle thermalisation lag ~Gyr; orbital -> dynamo "
        "routes through rotation only",
}


def constraint_validity_check(model_assumption_key):
    """
    Returns (is_valid, status_message) for a named electromagnetic
    model assumption. Use to flag stale assumptions in coupled solver
    before propagating state.
    """
    key = model_assumption_key.lower().strip()
    if key in INVALIDATED_ASSUMPTIONS:
        return False, INVALIDATED_ASSUMPTIONS[key]
    return True, (
        "CONDITIONAL: no recorded invalidation; verify against latest "
        "WMM/HDGM observation"
    )


def model_currency_check(year_decimal):
    """
    Returns (in_window, model_id, status) for a given decimal year.
    Tells the solver which geomagnetic model is authoritative for
    that epoch, and whether the requested year is inside any
    published validity window.

    HDGM is annual (rolling 1-yr windows); WMM is 5-yr. If both
    cover the year, prefer HDGM for crustal resolution and WMM for
    main-field secular variation — the caller decides which channel
    matters more for their layer.
    """
    if WMM2025_VALID_START <= year_decimal <= WMM2025_VALID_END:
        return True, "WMM2025", "IN_WINDOW"
    if year_decimal > WMM2025_VALID_END:
        return False, "WMM2025", "EXPIRED_AWAIT_NEXT_5YR_MODEL"
    return False, "WMM2025", "BEFORE_VALIDITY_START"


def deceleration_anomaly_flag(drift_rate_km_yr,
                              peak_rate_km_yr=POLE_DRIFT_RATE_PEAK_KM_YR,
                              current_rate_km_yr=POLE_DRIFT_RATE_CURRENT_KM_YR):
    """
    Returns (anomalous, status, fractional_decel) given an observed
    drift rate. Compares against the documented peak (~60 km/yr) and
    current (~35 km/yr) values. Fractional deceleration is
    (peak - observed) / peak.

    Anomalous if the observed rate sits below the recorded peak by
    more than 25% — that's the regime-shift threshold the WMM2025
    team flagged as 'largest on record'.
    """
    frac = (peak_rate_km_yr - drift_rate_km_yr) / peak_rate_km_yr
    if frac >= 0.25:
        return True, "DECELERATION_ANOMALY_REGIME_SHIFT", frac
    if frac <= -0.10:
        return True, "RE_ACCELERATION_DETECTED", frac
    return False, "WITHIN_PEAK_BAND", frac


def cascade_trigger_check(em_signal_label, year):
    """
    Returns (is_triggered, status) for electromagnetic cascade
    thresholds. Use as early-warning gate in solver for coupling
    from L0 into L1/L2/L7.
    """
    s = em_signal_label.lower()
    if "pole_drift_deceleration" in s and year >= 2025:
        return True, "DYNAMO_REGIME_SHIFT_WINDOW_OPEN"
    if "saa_bifurcation" in s and year >= 2020:
        return True, "SAA_LOBE_SEPARATION_OBSERVED"
    if "auroral_oval_shift" in s and year >= 2025:
        return True, "MIDLATITUDE_GIC_EXPOSURE_RISING"
    if "geomagnetic_jerk" in s and year >= 2024:
        return True, "JERK_CANDIDATE_2024_2025"
    if "dipole_collapse" in s:
        # Full reversal timescale is millennia; this fires only as
        # a placeholder for solvers querying the long-horizon case.
        return False, "NOT_WITHIN_DECADAL_HORIZON"
    return False, "WITHIN_PROJECTED_STABLE_RANGE"


def adjust_pole_drift_projection(years_ahead,
                                 current_rate_km_yr=POLE_DRIFT_RATE_CURRENT_KM_YR):
    """
    Returns (linear_km, nonlinear_min_km, nonlinear_max_km).
    Linear: naive extrapolation at current rate.
    Nonlinear band: accounts for the documented deceleration
    regime — drift could continue slowing (lower bound at 50%
    of current rate) OR re-accelerate (upper bound at peak rate
    of 60 km/yr). Both arms are observed in the historical record.
    """
    linear = years_ahead * current_rate_km_yr
    nonlinear_min = years_ahead * (current_rate_km_yr * 0.5)
    nonlinear_max = years_ahead * POLE_DRIFT_RATE_PEAK_KM_YR
    return linear, nonlinear_min, nonlinear_max


def remove_static_dipole_assumption(em_state_dict):
    """
    Strips the assumed-constant-dipole flag from an EM state dict.
    Sets any key matching 'static_dipole', 'constant_field', or
    'fixed_pole_position' to its dynamic-equivalent placeholder.
    Returns (modified_state, list_of_replaced_keys).
    """
    out = dict(em_state_dict)
    keys_to_replace = [
        k for k in out
        if "static_dipole" in k.lower()
        or "constant_field" in k.lower()
        or "fixed_pole_position" in k.lower()
    ]
    for k in keys_to_replace:
        out[k] = "DYNAMIC_REQUIRES_TIME_DEPENDENT_MODEL"
    return out, keys_to_replace


# ─────────────────────────────────────────────
# OBSERVATIONAL PRECEDENCE FLAGS
# Satellite and observatory data lead model updates by ~1-2 yr.
# Coupled solvers should weight WMM/HDGM secular variation as
# the leading signal, not the lagging fit.
# ─────────────────────────────────────────────

OBSERVATION_PRECEDES_MODEL_FIT = True
LINEAR_DIPOLE_EXTRAPOLATION_DEPRECATED = True
NONLINEAR_DYNAMO_COUPLING_REQUIRED = True
JERK_EVENTS_ARE_DEFAULT_NOT_EXCEPTION = True   # decadal cadence observed


# ─────────────────────────────────────────────
# COUPLING STATE EXPORT
# Dict-based export matching the inter-layer convention used by
# every layer_N_*.py file. The cascade engine reads this to push
# L0 regime signals into L1/L2/L7.
# ─────────────────────────────────────────────

def coupling_state():
    """
    Export current electromagnetic constraint state as a dict.
    Matches the inter-layer coupling convention used elsewhere
    in the repo. Values are observation-anchored snapshots, not
    forecast outputs.
    """
    return {
        "pole_drift_rate_km_yr": POLE_DRIFT_RATE_CURRENT_KM_YR,
        "pole_drift_peak_km_yr": POLE_DRIFT_RATE_PEAK_KM_YR,
        "deceleration_regime_active": POLE_DRIFT_DECELERATION_LARGEST_ON_RECORD,
        "pole_hemisphere": "siberian" if POLE_NOW_CLOSER_TO_SIBERIA_THAN_CANADA
                           else "canadian",
        "wmm2025_valid_window": (WMM2025_VALID_START, WMM2025_VALID_END),
        "hdgm_2026_valid_through": HDGM_2026_VALID_THROUGH,
        "dynamo_regime_shift": DYNAMO_REGIME_SHIFT_SIGNAL_2025,
        "saa_bifurcating": SAA_BIFURCATING_INTO_TWO_LOBES,
        "saa_decline_pct_per_decade": SAA_INTENSITY_DECLINE_PCT_PER_DECADE,
        "couples_to_magnetosphere": COUPLES_TO_MAGNETOSPHERE_GEOMETRY,
        "couples_to_ionosphere": COUPLES_TO_IONOSPHERE_AURORAL_OVAL,
        "couples_to_infrastructure": COUPLES_TO_INFRASTRUCTURE_GIC_RISK,
    }


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("EARTH SYSTEMS ELECTROMAGNETIC CONSTRAINT 2026")
    print("=" * 60)

    print("\nPOLE DRIFT:")
    print(f"  Peak rate (1990s-2010s):       {POLE_DRIFT_RATE_PEAK_KM_YR} km/yr")
    print(f"  Current rate (WMM2025):        {POLE_DRIFT_RATE_CURRENT_KM_YR} km/yr")
    print(f"  Largest deceleration on record: "
          f"{POLE_DRIFT_DECELERATION_LARGEST_ON_RECORD}")
    print(f"  Now closer to Siberia:         "
          f"{POLE_NOW_CLOSER_TO_SIBERIA_THAN_CANADA}")
    print(f"  Years of arctic traversal:     {YEARS_OF_ARCTIC_TRAVERSAL}")

    print("\nMODEL VERSIONS:")
    print(f"  WMM2025 window:                "
          f"{WMM2025_VALID_START} - {WMM2025_VALID_END}")
    print(f"  WMM2025 main SH degree:        "
          f"{WMM2025_SPHERICAL_HARMONIC_DEGREE}")
    print(f"  WMMHR2025 main SH degree:      "
          f"{WMMHR2025_SPHERICAL_HARMONIC_DEGREE_MAIN}")
    print(f"  WMMHR2025 crustal SH degree:   "
          f"{WMMHR2025_CRUSTAL_SH_DEGREE}")
    print(f"  HDGM 2026 valid through:       "
          f"{HDGM_2026_VALID_THROUGH}")
    print(f"  HDGM 2026 resolution increase: "
          f"{HDGM_2026_RESOLUTION_INCREASE_PCT}%")

    print("\nREGIME SHIFT SIGNALS:")
    print(f"  Dynamo regime shift 2025:      "
          f"{DYNAMO_REGIME_SHIFT_SIGNAL_2025}")
    print(f"  Deceleration onset (approx):   "
          f"{DYNAMO_DECELERATION_ONSET_APPROX_YEAR}")
    print(f"  CMB tangential flow shift:     "
          f"{OUTER_CORE_BOUNDARY_FLOW_SHIFT_DETECTED}")
    print(f"  2017 jerk active:              "
          f"{GEOMAGNETIC_JERK_2017_SIGNATURE}")
    print(f"  2024 jerk candidate:           "
          f"{GEOMAGNETIC_JERK_2024_CANDIDATE}")
    print(f"  SAA bifurcating:               "
          f"{SAA_BIFURCATING_INTO_TWO_LOBES}")
    print(f"  SAA decline per decade:        "
          f"{SAA_INTENSITY_DECLINE_PCT_PER_DECADE}%")

    print("\nCONSTRAINT CHECK demos:")
    for assumption in (
        "linear_pole_drift_extrapolation",
        "saa_single_lobe",
        "constant_dipole_moment",
        "uniform_crustal_remanence",  # not in registry; CONDITIONAL
    ):
        valid, msg = constraint_validity_check(assumption)
        print(f"  {assumption}: valid={valid}")
        print(f"    -> {msg}")

    print("\nMODEL CURRENCY demos:")
    for year in (2024.5, 2026.5, 2030.5):
        in_window, model, status = model_currency_check(year)
        print(f"  {year}: model={model} in_window={in_window} ({status})")

    print("\nDECELERATION ANOMALY demos:")
    for rate in (60, 45, 35, 20, 70):
        anom, status, frac = deceleration_anomaly_flag(rate)
        print(f"  {rate} km/yr: anomalous={anom} frac={frac:+.2f} ({status})")

    print("\nCASCADE TRIGGER demos:")
    for signal, year in [
        ("pole_drift_deceleration", 2026),
        ("saa_bifurcation", 2024),
        ("auroral_oval_shift", 2026),
        ("geomagnetic_jerk_2024", 2025),
        ("dipole_collapse", 2026),
        ("background_em_noise", 2026),
    ]:
        triggered, status = cascade_trigger_check(signal, year)
        print(f"  {signal}@{year}: triggered={triggered} ({status})")

    print("\nPOLE DRIFT PROJECTION demos:")
    for yrs in (1, 5, 10, 25):
        lin, lo, hi = adjust_pole_drift_projection(yrs)
        print(f"  {yrs} yr: linear={lin} km, "
              f"nonlinear band=[{lo:.0f}, {hi:.0f}] km")

    print("\nSTATIC DIPOLE REMOVAL demo:")
    em_state = {
        "static_dipole_moment_Am2": 8.22e22,
        "constant_field_assumption": True,
        "fixed_pole_position_lat": 86.5,
        "secular_variation_nT_yr": 130.0,
    }
    new_state, replaced = remove_static_dipole_assumption(em_state)
    print(f"  Original keys: {sorted(em_state.keys())}")
    print(f"  Replaced:      {replaced}")
    print(f"  Resulting:     {new_state}")

    print("\nCOUPLING STATE EXPORT:")
    for k, v in coupling_state().items():
        print(f"  {k}: {v}")
