# planetary_health_check_2026.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Observed planetary-boundary state, Planetary Health Check 2026.
#
# SOURCE (carried verbatim — do not paraphrase)
# ------
SOURCE_LINE = (
    "Planetary Health Check 2026, Summary Report, PBScience/PIK. "
    "Assessment uses latest available data; some predates 2026."
)
REPORT_RELEASED = "2026-09-21"
#
# WHAT THIS MODULE IS
# -------------------
# The 2026 control-variable (CV) table for the nine planetary boundaries,
# with the zone logic that reads it. It is the data layer that
# layer_6_biosphere.planetary_boundary_status() consumes through its new
# CV keyword arguments.
#
# THE MEASURAND RULE
# ------------------
# Several CVs changed between the Rockstrom 2009 framing this repo was
# written against and the 2023/2026 framing: ocean acidification is now
# aragonite saturation, not pH; freshwater is % of ice-free land deviated
# (blue + green), not km3 of consumptive use; land-system change is
# forest cover as % of potential, not a cropland fraction; aerosols are
# the interhemispheric AOD difference, not a single global AOD. A 2026
# number is NEVER dropped into an old-CV slot. CV_MISMATCHES lists every
# old slot and its replacement; the old slots stay in the code as legacy
# fields marked superseded.
#
# EPISTEMIC TAGS used below
#   OBSERVED  — value as reported by PHC 2026
#   DERIVED   — computed here from OBSERVED values in a visible line
#   PROPOSED  — a decision rule this repo introduces, not in the report
#
# Standard library only.

from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────
# ZONE LABELS
# ─────────────────────────────────────────────

SAFE = "SAFE"
INCREASING_RISK = "INCREASING_RISK"
HIGH_RISK = "HIGH_RISK"
REGIONAL = "REGIONAL_TRANSGRESSION"
NOT_CAPTURED = "NOT_CAPTURED"

BREACHED_WITHIN_DATASET_SPREAD = "BREACHED_WITHIN_DATASET_SPREAD"
GLOBAL_ONLY_SCOPE = "GLOBAL_ONLY_SCOPE"

_ZONE_RANK = {SAFE: 0, INCREASING_RISK: 1, HIGH_RISK: 2}


def CV_MISMATCH(old: str, new: str) -> Dict[str, str]:
    """
    Marker returned instead of a value when a caller supplies an OLD
    control variable to a slot whose 2026 measurand is different.
    old : name of the superseded CV
    new : name of the 2026 CV that replaces it
    """
    return {"status": "CV_MISMATCH", "old": old, "new": new}


# Old-CV slot -> replacement. These are the function arguments in
# layer_6_biosphere.planetary_boundary_status() that take a superseded
# measurand. The P row is DERIVED from the table: the code's 11 Tg/yr
# boundary is the ocean-flow CV; the PHC 2026 row (PB 6.2 / HR 11.2) is
# the fertilizer-to-erodible-soil CV. Same units, different measurand.
CV_MISMATCHES: List[Dict[str, str]] = [
    CV_MISMATCH("ocean_pH", "omega_arag"),
    CV_MISMATCH("freshwater_km3", "blue_water_pct_land + green_water_pct_land"),
    CV_MISMATCH("land_use_fraction", "forest_cover_pct_potential"),
    CV_MISMATCH("aerosol_AOD", "delta_AOD_interhemispheric (+ south_asia_AOD)"),
    CV_MISMATCH("P_cycle_Tg (boundary 11, ocean flow)",
                "P_fertilizer_Tg (boundary 6.2, flow to erodible soils)"),
]


# ─────────────────────────────────────────────
# CONTROL-VARIABLE TABLE — OBSERVED
# value: point value or (low, high) range as reported
# pb: planetary boundary     hr: high-risk line
# higher_is_worse: False for forest cover and aragonite saturation
# provisional: the report marks the high-risk line provisional
# ─────────────────────────────────────────────

CONTROL_VARIABLES: Dict[str, Dict[str, object]] = {
    "climate_CO2_ppm": {
        "boundary": "climate", "value": 426.0, "pb": 350.0, "hr": 450.0,
        "units": "ppm", "higher_is_worse": True, "provisional": False},
    "climate_RF_Wm2": {
        "boundary": "climate", "value": 3.10, "pb": 1.0, "hr": 1.5,
        "units": "W/m2", "higher_is_worse": True, "provisional": False},
    "biosphere_extinction_E_MSY": {
        "boundary": "biosphere_integrity", "value": (100.0, 1000.0),
        "pb": 10.0, "hr": 100.0,
        "units": "E/MSY", "higher_is_worse": True, "provisional": False},
    "biosphere_HANPP_pct": {
        "boundary": "biosphere_integrity", "value": (21.0, 30.0),
        "pb": 10.0, "hr": 20.0,
        "units": "% of pre-industrial NPP", "higher_is_worse": True,
        "provisional": False},
    "land_forest_pct_potential": {
        "boundary": "land_system_change", "value": 64.0, "pb": 78.0, "hr": 54.0,
        "units": "% of potential forest", "higher_is_worse": False,
        "provisional": False},
    "freshwater_blue_pct_land": {
        "boundary": "freshwater_change", "value": 22.6, "pb": 12.9, "hr": 50.0,
        "units": "% ice-free land deviated", "higher_is_worse": True,
        "provisional": True},
    "freshwater_green_pct_land": {
        "boundary": "freshwater_change", "value": 22.0, "pb": 12.4, "hr": 50.0,
        "units": "% ice-free land deviated", "higher_is_worse": True,
        "provisional": True},
    "biogeochem_P_Tg_yr": {
        "boundary": "biogeochemical_flows", "value": 18.2, "pb": 6.2, "hr": 11.2,
        "units": "Tg P/yr", "higher_is_worse": True, "provisional": False},
    "biogeochem_N_Tg_yr": {
        "boundary": "biogeochemical_flows", "value": 165.0, "pb": 62.0, "hr": 82.0,
        "units": "Tg N/yr", "higher_is_worse": True, "provisional": False},
    "ocean_omega_arag": {
        "boundary": "ocean_acidification", "value": 2.85, "pb": 2.86, "hr": 2.50,
        "units": "Omega_aragonite (surface mean)", "higher_is_worse": False,
        "provisional": True},
    "aerosol_delta_AOD": {
        "boundary": "aerosol_loading", "value": 0.07, "pb": 0.10, "hr": 0.25,
        "units": "interhemispheric AOD difference", "higher_is_worse": True,
        "provisional": False},
    "aerosol_south_asia_AOD": {
        "boundary": "aerosol_loading", "value": 0.32, "pb": 0.25, "hr": 0.50,
        "units": "regional AOD (South Asia)", "higher_is_worse": True,
        "provisional": False, "regional": True},
}

# Boundaries whose CV the report does not quantify. The zone is what the
# report states; the value stays NOT_CAPTURED until a sourced CV exists.
NOT_CAPTURED_BOUNDARIES: Dict[str, str] = {
    "stratospheric_ozone": SAFE,
    "novel_entities": HIGH_RISK,
}

# Zones as stated by the report, for the reproduce-check below.
REPORTED_ZONES: Dict[str, str] = {
    "climate": HIGH_RISK,               # boundary-level; CO2 CV alone is INCR
    "biosphere_integrity": HIGH_RISK,
    "land_system_change": INCREASING_RISK,
    "freshwater_change": INCREASING_RISK,
    "biogeochemical_flows": HIGH_RISK,
    "ocean_acidification": INCREASING_RISK,
    "aerosol_loading": SAFE,            # global; S. Asia regionally transgressed
    "stratospheric_ozone": SAFE,
    "novel_entities": HIGH_RISK,
}

REPORTED_TRANSGRESSED_COUNT = 7        # OBSERVED: 7 of 9
REPORTED_TOTAL_BOUNDARIES = 9
NEWEST_TRANSGRESSION = ("ocean_acidification", 2025)
ALL_TRANSGRESSED_AT_HIGHEST_RECORDED = True   # OBSERVED


# ─────────────────────────────────────────────
# LAND CARBON SINK — OBSERVED, carried as a bias note (not a fix)
# ─────────────────────────────────────────────

LAND_SINK_NOTE = (
    "PHC 2026 (OBSERVED): land carbon uptake excluding land-use change has "
    "been stagnant since ~2000. The report states Earth system models likely "
    "OVERESTIMATE land-sink resilience (average plant types, smooth recovery, "
    "no mortality spirals). Any simulation treating the land sink as stable "
    "carries that bias. Noted, not corrected."
)
LAND_SINK_STAGNANT_SINCE = 2000
ESM_LAND_SINK_RESILIENCE_BIAS = "overestimate"


# ─────────────────────────────────────────────
# ZONE LOGIC
# ─────────────────────────────────────────────

def cv_zone(value, pb: float, hr: float,
            higher_is_worse: bool = True) -> str:
    """
    Zone of one control variable against its boundary and high-risk line.

    value : float, or (low, high) range — a range is zoned on its LOW
            end (the least-alarming reading the report supports), so a
            range is never promoted past what its whole span supports
    pb    : planetary boundary (edge of safe operating space)
    hr    : high-risk line
    returns: SAFE / INCREASING_RISK / HIGH_RISK
    """
    if isinstance(value, tuple):
        v = value[0] if higher_is_worse else value[1]
    else:
        v = value
    if higher_is_worse:
        if v >= hr:
            return HIGH_RISK
        return INCREASING_RISK if v > pb else SAFE
    if v <= hr:
        return HIGH_RISK
    return INCREASING_RISK if v < pb else SAFE


def _reported_resolution(x: float) -> float:
    """One unit in the last reported decimal place (2.85 -> 0.01)."""
    s = repr(float(x))
    decimals = len(s.split(".")[1].rstrip("0")) if "." in s else 0
    return 10.0 ** (-decimals)


def ocean_acidification_status(omega_arag: float,
                               pb: float = 2.86,
                               hr: float = 2.50,
                               dataset_spread: Optional[float] = None
                               ) -> Dict[str, object]:
    """
    Ocean-acidification boundary on its 2026 CV, aragonite saturation.

    The 2026 assessment is multi-dataset and the margin is 0.01 Omega, so a
    hard binary is not honest. When the margin is within the dataset
    spread, return BREACHED_WITHIN_DATASET_SPREAD and carry the margin.
                                                              PROPOSED
    dataset_spread : Omega units. The report does not publish one; when
        None, the spread floor is one unit in the last reported decimal of
        the boundary (0.01 for 2.86) — a margin no larger than the
        reporting resolution cannot be distinguished from zero. DERIVED.

    omega_arag : surface mean aragonite saturation state (dimensionless)
    returns: dict with zone, crossed, margin, label, spread used
    """
    margin = pb - omega_arag            # > 0 means transgressed (lower is worse)
    spread = dataset_spread
    spread_basis = "supplied"
    if spread is None:
        spread = max(_reported_resolution(pb), _reported_resolution(omega_arag))
        spread_basis = "reporting resolution (no published spread)"
    zone = cv_zone(omega_arag, pb, hr, higher_is_worse=False)
    crossed = margin > 0
    if crossed and margin <= spread + 1e-12:
        label = BREACHED_WITHIN_DATASET_SPREAD
    elif not crossed and -margin <= spread + 1e-12:
        label = "SAFE_WITHIN_DATASET_SPREAD"
    else:
        label = zone
    return {
        "cv": "omega_arag",
        "value": omega_arag,
        "boundary": pb,
        "high_risk": hr,
        "zone": zone,
        "crossed": crossed,
        "margin": round(margin, 6),
        "label": label,
        "dataset_spread": spread,
        "spread_basis": spread_basis,
        "high_risk_provisional": True,
    }


def aerosol_status(delta_AOD: float,
                   south_asia_AOD: Optional[float] = None,
                   pb: float = 0.10, hr: float = 0.25,
                   regional_pb: float = 0.25,
                   regional_hr: float = 0.50) -> Dict[str, object]:
    """
    Aerosol boundary on its 2026 CV (interhemispheric AOD difference),
    with the South Asia regional field. A single global variable reads
    SAFE while South Asia is transgressed; without the regional value the
    result is scoped GLOBAL_ONLY_SCOPE rather than a clean SAFE.

    delta_AOD      : interhemispheric AOD difference (dimensionless)
    south_asia_AOD : regional annual-mean AOD, or None if not supplied
    returns: dict with global zone, regional zone (or scope flag)
    """
    g_zone = cv_zone(delta_AOD, pb, hr)
    out: Dict[str, object] = {
        "cv": "delta_AOD_interhemispheric",
        "value": delta_AOD,
        "boundary": pb,
        "high_risk": hr,
        "zone": g_zone,
        "crossed": g_zone != SAFE,
    }
    if south_asia_AOD is None:
        out["scope"] = GLOBAL_ONLY_SCOPE
        out["regional_zone"] = None
    else:
        r_zone = cv_zone(south_asia_AOD, regional_pb, regional_hr)
        out["scope"] = "GLOBAL_PLUS_SOUTH_ASIA"
        out["regional_value"] = south_asia_AOD
        out["regional_zone"] = r_zone
        out["regionally_transgressed"] = r_zone != SAFE
        if g_zone == SAFE and r_zone != SAFE:
            out["label"] = REGIONAL
    return out


def boundary_zones() -> Dict[str, Dict[str, object]]:
    """
    Boundary-level zones from the CV table. A boundary with several CVs
    takes the WORST CV zone (climate: CO2 is INCR, RF is HIGH -> HIGH).
    Aerosols are zoned on the global CV; the regional field rides along.
    returns: {boundary: {zone, transgressed, cvs: {cv: zone}}}
    """
    out: Dict[str, Dict[str, object]] = {}
    for key, cv in CONTROL_VARIABLES.items():
        if cv.get("regional"):
            continue
        b = cv["boundary"]
        z = cv_zone(cv["value"], cv["pb"], cv["hr"], cv["higher_is_worse"])
        entry = out.setdefault(b, {"zone": SAFE, "cvs": {}})
        entry["cvs"][key] = z
        if _ZONE_RANK[z] > _ZONE_RANK[entry["zone"]]:
            entry["zone"] = z
    out["ocean_acidification"]["detail"] = ocean_acidification_status(
        CONTROL_VARIABLES["ocean_omega_arag"]["value"])
    out["aerosol_loading"]["detail"] = aerosol_status(
        CONTROL_VARIABLES["aerosol_delta_AOD"]["value"],
        CONTROL_VARIABLES["aerosol_south_asia_AOD"]["value"])
    for b, z in NOT_CAPTURED_BOUNDARIES.items():
        out[b] = {"zone": z, "cvs": {}, "value": NOT_CAPTURED}
    for entry in out.values():
        entry["transgressed"] = entry["zone"] != SAFE
    return out


def transgressed_count() -> Tuple[int, int]:
    """DERIVED count of transgressed boundaries: (n, of 9)."""
    zones = boundary_zones()
    return sum(1 for e in zones.values() if e["transgressed"]), len(zones)


def reproduce_check() -> Dict[str, object]:
    """
    Does the zone logic here reproduce the report's own zones and count?
    A disagreement means the logic, not the report, needs a look.
    """
    zones = boundary_zones()
    mismatches = {b: (zones[b]["zone"], z) for b, z in REPORTED_ZONES.items()
                  if zones[b]["zone"] != z}
    n, total = transgressed_count()
    return {
        "zones_match": not mismatches,
        "mismatches": mismatches,
        "count_derived": n,
        "count_reported": REPORTED_TRANSGRESSED_COUNT,
        "count_match": n == REPORTED_TRANSGRESSED_COUNT,
        "total": total,
    }


def layer6_kwargs() -> Dict[str, float]:
    """
    The 2026 CVs as keyword arguments for
    layer_6_biosphere.planetary_boundary_status(). Ranges pass their low
    end, consistent with cv_zone().
    """
    cv = CONTROL_VARIABLES
    return {
        "radiative_forcing_Wm2": cv["climate_RF_Wm2"]["value"],
        "HANPP_pct": cv["biosphere_HANPP_pct"]["value"][0],
        "P_fertilizer_Tg": cv["biogeochem_P_Tg_yr"]["value"],
        "forest_cover_pct_potential": cv["land_forest_pct_potential"]["value"],
        "blue_water_pct_land": cv["freshwater_blue_pct_land"]["value"],
        "green_water_pct_land": cv["freshwater_green_pct_land"]["value"],
        "omega_arag": cv["ocean_omega_arag"]["value"],
        "delta_AOD": cv["aerosol_delta_AOD"]["value"],
        "south_asia_AOD": cv["aerosol_south_asia_AOD"]["value"],
    }


if __name__ == "__main__":
    print("PLANETARY HEALTH CHECK 2026 — control-variable state")
    print(SOURCE_LINE)
    print()
    zones = boundary_zones()
    for b, e in zones.items():
        print(f"  {b:24s} {e['zone']:16s} "
              f"{'TRANSGRESSED' if e['transgressed'] else ''}")
        for k, z in e["cvs"].items():
            cv = CONTROL_VARIABLES[k]
            print(f"      {k:30s} {str(cv['value']):16s} pb {cv['pb']:<7} "
                  f"hr {cv['hr']:<7} -> {z}")
    oa = zones["ocean_acidification"]["detail"]
    print(f"\n  ocean acidification: {oa['label']}, margin {oa['margin']} Omega "
          f"(spread {oa['dataset_spread']}, {oa['spread_basis']})")
    ae = zones["aerosol_loading"]["detail"]
    print(f"  aerosols: global {ae['zone']}, South Asia {ae['regional_zone']}")
    rc = reproduce_check()
    print(f"\n  transgressed: {rc['count_derived']} of {rc['total']} "
          f"(report: {rc['count_reported']}) "
          f"zones_match={rc['zones_match']}")
    print(f"\n  CV mismatches (old slot -> 2026 CV):")
    for m in CV_MISMATCHES:
        print(f"    {m['old']:40s} -> {m['new']}")
    print(f"\n  {LAND_SINK_NOTE}")
