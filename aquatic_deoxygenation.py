# aquatic_deoxygenation.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Aquatic deoxygenation as a proposed TENTH planetary boundary.
#
# Source papers
# -------------
# Rose, K.C., Ferrer, E.M., Carpenter, S.R., et al. (2024)
#   "Aquatic deoxygenation as a planetary boundary and key regulator
#    of Earth system stability."
#   Nature Ecology & Evolution.  doi:10.1038/s41559-024-02448-y
#   -> argues dissolved-oxygen decline in fresh and marine waters is
#      itself a planetary-boundary process; proposes the global extent
#      of anoxia as a preliminary control variable.
#
# Ferrer, E.M., Levin, L.A., et al. (2026)
#   "Abundant interactions and feedbacks between aquatic deoxygenation
#    and the other planetary boundaries suggest 'unsafe' levels of
#    oxygen loss with far-reaching impacts."
#   Limnology and Oceanography, published 2026-06-30.
#   doi:10.1002/lno.70434
#   -> synthesises the interactions between deoxygenation and all nine
#      established boundaries; concludes current oxygen loss is already
#      at "unsafe" levels; recovery of deep waters is centuries-scale.
#
# Supporting observational constraints
#   Schmidtko, S., Stramma, L., Visbeck, M. (2017) Nature 542:335-339
#       — global ocean O2 inventory decline 1960-2010.
#   Breitburg, D., et al. (2018) Science 359:eaam7240
#       — coastal and open-ocean deoxygenation synthesis.
#   Jane, S.F., et al. (2021) Nature 594:66-70
#       — widespread deoxygenation of temperate lakes.
#   Deutsch, C., et al. (2015) Science 348:1132-1135
#       — Metabolic Index (Phi) as habitat-viability control.
#
# HONESTY NOTE ON THE CATALOG
# ---------------------------
# BOUNDARY_INTERACTIONS below organises the deoxygenation<->boundary
# couplings by the same nine-boundary partition Ferrer et al. use, with
# the mechanism text drawn from the primary deoxygenation literature.
# It is NOT a verbatim transcription of that paper's Table 1. Each entry
# carries an `evidence` grade so a downstream solver can weight it.
#
# HONESTY NOTE ON THE BOUNDARY VALUE
# ----------------------------------
# Rose et al. propose the *control variable* (global extent of anoxia)
# but do NOT publish a numeric safe-boundary value for it. The zone
# edges in BOUNDARY_ZONES are PROVISIONAL placeholders so coupled
# solvers have something to gate on — they are flagged as such in every
# return value and must not be reported as published thresholds.
#
# Standard library only.

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────
# FUNDAMENTAL CONSTANTS — DISSOLVED OXYGEN
# ─────────────────────────────────────────────

M_O2                  = 31.9988     # g/mol — molar mass of O2
RHO_SEAWATER          = 1.025       # kg/L — used for umol/kg <-> mg/L
RHO_FRESHWATER        = 1.000       # kg/L
O2_MOLE_FRACTION_AIR  = 0.2095      # dimensionless — atmospheric O2
P_ATM_KPA             = 101.325     # kPa — standard atmosphere
K_B_EV                = 8.617333e-5 # eV/K — Boltzmann constant

# Redfield remineralisation stoichiometry (Anderson & Sarmiento 1994):
#   (CH2O)106 (NH3)16 (H3PO4) + 138 O2 -> 106 CO2 + 16 HNO3 + H3PO4
REDFIELD_O2_PER_P     = 138.0       # mol O2 per mol P remineralised
REDFIELD_C_PER_P      = 106.0       # mol C  per mol P
REDFIELD_N_PER_P      = 16.0        # mol N  per mol P
REDFIELD_O2_PER_N     = REDFIELD_O2_PER_P / REDFIELD_N_PER_P   # 8.625

# Ecological oxygen thresholds (dissolved O2)
HYPOXIA_MG_L          = 2.0         # mg/L — conventional hypoxia line
SEVERE_HYPOXIA_MG_L   = 0.5         # mg/L — mass-mortality regime
ANOXIA_MG_L           = 0.1         # mg/L — functionally zero O2
SUBOXIC_UMOL_KG       = 5.0         # umol/kg — denitrification onset
OMZ_UMOL_KG           = 70.0        # umol/kg — conventional OMZ ceiling

# Greenhouse coupling of low-O2 metabolism
N2O_GWP100            = 273.0       # IPCC AR6, 100-yr GWP of N2O
CH4_GWP100            = 27.9        # IPCC AR6, 100-yr GWP of fossil CH4

# ─────────────────────────────────────────────
# OBSERVED STATE — WHAT THE MEASUREMENTS SAY
# ─────────────────────────────────────────────

# Open ocean (Schmidtko et al. 2017; Breitburg et al. 2018)
OCEAN_O2_LOSS_PCT_1960_2010          = 2.0     # % of total inventory
OCEAN_O2_LOSS_PMOL_1960_2010         = 4.8     # petamoles O2
OCEAN_O2_LOSS_PMOL_UNCERTAINTY       = 2.1     # +/- petamoles
ANOXIC_VOLUME_MULTIPLIER_SINCE_1960  = 4.0     # zero-O2 water quadrupled
OMZ_AREA_EXPANSION_KM2_SINCE_1960    = 4.5e6   # km2 of new low-O2 water
OCEAN_O2_INVENTORY_PMOL              = 227.4   # petamoles (2% == 4.8 Pmol)

# Coastal (Breitburg et al. 2018; Diaz & Rosenberg 2008)
COASTAL_LOW_O2_SITES                 = 500     # documented low-O2 sites
COASTAL_PERSISTENT_HYPOXIC_SITES     = 200     # persistent < 2 mg/L

# Fresh water (Jane et al. 2021, temperate lakes, since 1980)
LAKE_SURFACE_O2_DECLINE_PCT          = 5.5     # % decline, surface waters
LAKE_DEEP_O2_DECLINE_PCT             = 18.6    # % decline, deep waters
LAKE_DEOX_RATE_VS_OCEAN              = 9.0     # lakes losing O2 ~3-9x faster

# Hypoxic volume reference. Present-day water below the 2 mg/L line is
# roughly 1-2% of ocean volume (waters below the 70 umol/kg OMZ ceiling
# are ~8%). The pre-industrial figure is not directly measured; 0.5% is
# used as an order-of-magnitude reference for detecting expansion, and is
# an ANCHOR, not an observation.
HYPOXIC_VOLUME_FRACTION_PRESENT       = 0.015   # ~1.5% of ocean volume
HYPOXIC_VOLUME_FRACTION_REFERENCE     = 0.005   # pre-industrial anchor

# Marine heatwave extent (State of the Climate in 2025, BAMS 2026).
# A marine heatwave lowers O2 twice over: solubility falls with
# temperature AND the stratification that sustains the heatwave cuts the
# ventilation that would resupply the interior. 2025 is the observed
# upper bound on how much of the surface ocean is exposed at once.
MARINE_HEATWAVE_OCEAN_FRACTION_2025 = 0.87    # >=1 MHW during the year
OCEAN_HEAT_CONTENT_RECORD_2025 = True         # 0-2000 m, record high

# Attribution of open-ocean loss (Schmidtko et al. 2017; Oschlies 2018)
# Warming lowers solubility; the larger share is reduced ventilation and
# increased stratification/respiration in the interior.
SOLUBILITY_SHARE_OF_OCEAN_LOSS       = 0.15    # ~15% from warming alone
VENTILATION_SHARE_OF_OCEAN_LOSS      = 0.85    # remainder: circulation/bio

# Recovery timescales — deep water exchanges on ventilation timescales,
# so oxygen loss is not reversible on policy timescales.
RECOVERY_TIMESCALE_YR = {
    "lake_surface":       1.0,
    "lake_hypolimnion":   10.0,
    "reservoir":          10.0,
    "estuary":            1.0,
    "coastal_shelf":      5.0,
    "ocean_mixed_layer":  1.0,
    "ocean_thermocline":  50.0,
    "ocean_intermediate": 250.0,
    "ocean_deep":         1000.0,
}

# Proposal status — this is a live proposal in the literature, NOT an
# adopted revision of the Stockholm Resilience nine-boundary framework.
PROPOSED_AS_TENTH_BOUNDARY   = True
PROPOSAL_STATUS              = "proposed_not_yet_adopted"
PROPOSAL_FIRST_PUBLISHED     = 2024
INTERACTION_SYNTHESIS_YEAR   = 2026

# ─────────────────────────────────────────────
# CONTROL VARIABLE AND (PROVISIONAL) BOUNDARY ZONES
# ─────────────────────────────────────────────

PRIMARY_CONTROL_VARIABLE = "global_extent_of_anoxia"

# Rose et al. list these as candidate indicators for the control
# variable. Ordered as published: extent of anoxia is primary because it
# gates anaerobic metabolism and therefore greenhouse-gas production.
CONTROL_VARIABLE_INDICATORS = [
    {
        "name":  "anoxic_extent",
        "units": "volume or area of water with O2 ~ 0",
        "why":   "gates anaerobic metabolism, N2O/CH4 production, "
                 "Fe/P/Hg redox chemistry",
        "role":  "primary",
    },
    {
        "name":  "dissolved_oxygen_concentration",
        "units": "mg/L or umol/kg",
        "why":   "direct state variable; hypoxia thresholds are defined on it",
        "role":  "indicator",
    },
    {
        "name":  "percent_oxygen_saturation",
        "units": "% of air-equilibrium saturation",
        "why":   "separates solubility (thermal) loss from biological drawdown",
        "role":  "indicator",
    },
    {
        "name":  "indicator_taxa",
        "units": "presence / absence / assemblage shift",
        "why":   "integrates exposure history; catches intermittent hypoxia",
        "role":  "indicator",
    },
    {
        "name":  "metabolic_index_phi",
        "units": "dimensionless (O2 supply / O2 demand)",
        "why":   "habitat viability; couples temperature and O2 in one number",
        "role":  "indicator",
    },
]

# PROVISIONAL — see honesty note in the module header.
BOUNDARY_ZONES_PROVISIONAL = True
BOUNDARY_ZONES = {
    # anoxic volume expressed as a multiple of the 1960 anoxic volume
    "safe_below":            1.5,
    "increasing_risk_below": 3.0,
    "high_risk_at_or_above": 3.0,
}

# ─────────────────────────────────────────────
# BOUNDARY INTERACTION CATALOG (Ferrer et al. 2026 framing)
# ─────────────────────────────────────────────


@dataclass
class BoundaryInteraction:
    """
    One coupling between aquatic deoxygenation and an established
    planetary boundary.

    boundary   : name of the established planetary-boundary process
    direction  : 'driven_by' (boundary -> deoxygenation),
                 'drives'    (deoxygenation -> boundary),
                 'bidirectional'
    sign       : 'amplifying' (positive feedback) or 'dampening'
    mechanism  : the physical/biogeochemical pathway
    layers     : earth-systems-physics layer indices touched
    evidence   : 'observed' | 'mechanistic' | 'proposed'
    timescale  : characteristic response time
    """
    boundary:   str
    direction:  str
    sign:       str
    mechanism:  str
    layers:     List[int]
    evidence:   str
    timescale:  str


BOUNDARY_INTERACTIONS: List[BoundaryInteraction] = [
    BoundaryInteraction(
        boundary="climate_change",
        direction="bidirectional",
        sign="amplifying",
        mechanism=(
            "Warming lowers O2 solubility (~15% of observed ocean loss) and "
            "strengthens stratification, cutting ventilation of the interior "
            "(~85%). The resulting low-O2 water raises N2O yield from "
            "nitrification/denitrification and permits CH4 escape from "
            "anoxic sediments — both feed back onto radiative forcing. "
            "Ocean heat content set a record in 2025 and 87% of the ocean "
            "surface saw at least one marine heatwave that year, so the "
            "forcing side of this coupling is not a projection."
        ),
        layers=[3, 4, 6],
        evidence="observed",
        timescale="decades to centuries",
    ),
    BoundaryInteraction(
        boundary="ocean_acidification",
        direction="bidirectional",
        sign="amplifying",
        mechanism=(
            "Aerobic respiration consumes O2 and produces CO2 in the same "
            "water parcel, so low-O2 water is also low-pH water: the two "
            "boundaries are stoichiometrically locked by the Redfield ratio. "
            "Combined hypoxia + acidification exceeds single-stressor "
            "tolerance for calcifiers and fish."
        ),
        layers=[4, 6],
        evidence="observed",
        timescale="decades",
    ),
    BoundaryInteraction(
        boundary="biosphere_integrity",
        direction="bidirectional",
        sign="amplifying",
        mechanism=(
            "Habitat compression: as the Metabolic Index falls below the "
            "critical value, aerobic habitat volume shrinks vertically and "
            "poleward. Loss of large-bodied fauna and bioturbating benthos "
            "changes remineralisation depth, concentrating O2 demand "
            "shallower and accelerating further deoxygenation."
        ),
        layers=[4, 6],
        evidence="observed",
        timescale="years to decades",
    ),
    BoundaryInteraction(
        boundary="biogeochemical_flows_nitrogen",
        direction="bidirectional",
        sign="amplifying",
        mechanism=(
            "Anthropogenic N loading drives production whose remineralisation "
            "consumes 8.6 mol O2 per mol N. Below ~5 umol/kg the water "
            "switches to denitrification and anammox, removing fixed N but "
            "peaking N2O yield at suboxic (not fully anoxic) conditions — "
            "the worst-case band the ocean is currently expanding into."
        ),
        layers=[4, 6],
        evidence="observed",
        timescale="years to decades",
    ),
    BoundaryInteraction(
        boundary="biogeochemical_flows_phosphorus",
        direction="bidirectional",
        sign="amplifying",
        mechanism=(
            "Anoxic sediments reduce Fe(III) oxyhydroxides and release the "
            "phosphate bound to them. Internal P loading then sustains "
            "production even after external loading is cut — the classic "
            "self-locking eutrophication ratchet in lakes and semi-enclosed "
            "basins. This is the strongest internal positive feedback in the "
            "deoxygenation system."
        ),
        layers=[4, 5, 6],
        evidence="observed",
        timescale="years to decades",
    ),
    BoundaryInteraction(
        boundary="freshwater_change",
        direction="bidirectional",
        sign="amplifying",
        mechanism=(
            "Lakes and reservoirs are deoxygenating 3-9x faster than the "
            "ocean: warming plus longer stratified seasons plus shorter ice "
            "cover. Impoundment converts rivers into long-residence-time "
            "reservoirs with hypolimnetic O2 demand, and abstraction reduces "
            "the flushing that would otherwise reset the deficit."
        ),
        layers=[4, 6],
        evidence="observed",
        timescale="years",
    ),
    BoundaryInteraction(
        boundary="land_system_change",
        direction="driven_by",
        sign="amplifying",
        mechanism=(
            "Conversion of land to row-crop agriculture and urban surface "
            "exports nutrients, sediment, and labile organic carbon to "
            "receiving waters. Coastal dead zones sit at the mouths of the "
            "most heavily converted watersheds; the coupling is dose-response "
            "and well documented."
        ),
        layers=[5, 6],
        evidence="observed",
        timescale="years",
    ),
    BoundaryInteraction(
        boundary="atmospheric_aerosol_loading",
        direction="bidirectional",
        sign="mixed",
        mechanism=(
            "Reactive-N aerosol deposition fertilises surface waters "
            "(amplifying). Aerosol dimming and wind-field changes alter "
            "mixed-layer depth and upwelling, which can go either way. "
            "Aerosol radiative cooling raises O2 solubility — one of the few "
            "genuinely dampening terms in the catalog, and one that "
            "disappears as air quality improves."
        ),
        layers=[2, 3, 4],
        evidence="mechanistic",
        timescale="years to decades",
    ),
    BoundaryInteraction(
        boundary="stratospheric_ozone_depletion",
        direction="driven_by",
        sign="amplifying",
        mechanism=(
            "Ozone loss over Antarctica intensified and shifted the Southern "
            "Ocean westerlies poleward, strengthening upwelling of old, "
            "oxygen-poor, CO2-rich deep water onto shelves. Surface UV-B "
            "additionally suppresses near-surface primary production and "
            "therefore local O2 supply."
        ),
        layers=[2, 3, 4],
        evidence="mechanistic",
        timescale="decades",
    ),
    BoundaryInteraction(
        boundary="novel_entities",
        direction="bidirectional",
        sign="amplifying",
        mechanism=(
            "Organic pollutants and untreated waste carry direct biochemical "
            "oxygen demand. Running the other way, anoxia changes metal "
            "speciation: sulfate-reducing bacteria in anoxic sediment "
            "methylate mercury, converting a stored contaminant into a "
            "bioaccumulating one. Deoxygenation therefore re-mobilises the "
            "novel-entity boundary's legacy inventory."
        ),
        layers=[4, 5, 6],
        evidence="observed",
        timescale="years to decades",
    ),
]


def interactions_by_boundary(boundary: str) -> List[BoundaryInteraction]:
    """All catalogued interactions naming `boundary` (substring match)."""
    b = boundary.lower().strip()
    return [i for i in BOUNDARY_INTERACTIONS if b in i.boundary.lower()]


def amplifying_interactions() -> List[BoundaryInteraction]:
    """Interactions whose net sign is amplifying (positive feedback)."""
    return [i for i in BOUNDARY_INTERACTIONS if i.sign == "amplifying"]


def interaction_summary() -> Dict[str, object]:
    """Aggregate counts over the interaction catalog."""
    signs: Dict[str, int] = {}
    directions: Dict[str, int] = {}
    evidence: Dict[str, int] = {}
    for i in BOUNDARY_INTERACTIONS:
        signs[i.sign] = signs.get(i.sign, 0) + 1
        directions[i.direction] = directions.get(i.direction, 0) + 1
        evidence[i.evidence] = evidence.get(i.evidence, 0) + 1
    return {
        "n_interactions":       len(BOUNDARY_INTERACTIONS),
        "n_boundaries_touched": len({i.boundary for i in BOUNDARY_INTERACTIONS}),
        "by_sign":              signs,
        "by_direction":         directions,
        "by_evidence":          evidence,
        "amplifying_fraction":  signs.get("amplifying", 0) / len(BOUNDARY_INTERACTIONS),
    }


# ─────────────────────────────────────────────
# OXYGEN SOLUBILITY — GARCIA & GORDON (1992)
# ─────────────────────────────────────────────

# Garcia & Gordon (1992) refit of the Benson & Krause data, combined
# fit coefficients; returns umol/kg at 1 atm total pressure with
# saturated water vapour.
_GG_A = (5.80871, 3.20291, 4.17887, 5.10006, -9.86643e-2, 3.80369)
_GG_B = (-7.01577e-3, -7.70028e-3, -1.13864e-2, -9.51519e-3)
_GG_C0 = -2.75915e-7


def oxygen_solubility_umol_kg(T_C: float, S: float = 35.0) -> float:
    """
    Air-equilibrium dissolved-oxygen concentration (O2 saturation).

    Garcia & Gordon (1992) combined fit to Benson & Krause data.
    Valid range: T = -2 to 40 degC, S = 0 to 42 PSU.

    T_C : water temperature (degC)
    S   : practical salinity (PSU; 0 for fresh water)
    returns: O2 solubility (umol/kg)
    """
    Ts = math.log((298.15 - T_C) / (273.15 + T_C))
    lnC = sum(a * Ts ** n for n, a in enumerate(_GG_A))
    lnC += S * sum(b * Ts ** n for n, b in enumerate(_GG_B))
    lnC += _GG_C0 * S * S
    return math.exp(lnC)


def umol_kg_to_mg_L(o2_umol_kg: float, rho_kg_L: float = RHO_SEAWATER) -> float:
    """Convert dissolved O2 from umol/kg to mg/L at density rho_kg_L."""
    return o2_umol_kg * M_O2 * rho_kg_L / 1000.0


def mg_L_to_umol_kg(o2_mg_L: float, rho_kg_L: float = RHO_SEAWATER) -> float:
    """Convert dissolved O2 from mg/L to umol/kg at density rho_kg_L."""
    return o2_mg_L * 1000.0 / (M_O2 * rho_kg_L)


def oxygen_solubility_mg_L(T_C: float, S: float = 35.0) -> float:
    """O2 solubility in mg/L (the unit hypoxia thresholds are quoted in)."""
    rho = RHO_SEAWATER if S > 1.0 else RHO_FRESHWATER
    return umol_kg_to_mg_L(oxygen_solubility_umol_kg(T_C, S), rho)


def solubility_loss_from_warming(T_C: float, delta_T: float,
                                 S: float = 35.0) -> Dict[str, float]:
    """
    Purely thermal (solubility) component of oxygen loss.

    This is the floor of deoxygenation — it happens even in a perfectly
    ventilated, biologically inert ocean. Observed loss is several times
    larger because ventilation declines and respiration continues.

    T_C     : baseline water temperature (degC)
    delta_T : warming applied (K)
    S       : salinity (PSU)
    returns: dict with before/after solubility and the implied loss
    """
    c0 = oxygen_solubility_umol_kg(T_C, S)
    c1 = oxygen_solubility_umol_kg(T_C + delta_T, S)
    return {
        "O2_sat_before_umol_kg": c0,
        "O2_sat_after_umol_kg":  c1,
        "delta_O2_umol_kg":      c1 - c0,
        "fractional_loss":       (c0 - c1) / c0 if c0 > 0 else 0.0,
        "pct_loss":              100.0 * (c0 - c1) / c0 if c0 > 0 else 0.0,
        "note": "solubility term only — excludes ventilation and respiration",
    }


def attribute_oxygen_loss(total_loss_umol_kg: float) -> Dict[str, float]:
    """
    Split an observed oxygen loss into solubility vs ventilation/biological
    components using the observed global apportionment (Schmidtko et al.
    2017; Oschlies et al. 2018): ~15% solubility, ~85% everything else.

    total_loss_umol_kg : magnitude of observed O2 decline (umol/kg)
    returns: dict of component losses
    """
    return {
        "solubility_umol_kg":   total_loss_umol_kg * SOLUBILITY_SHARE_OF_OCEAN_LOSS,
        "ventilation_umol_kg":  total_loss_umol_kg * VENTILATION_SHARE_OF_OCEAN_LOSS,
        "solubility_fraction":  SOLUBILITY_SHARE_OF_OCEAN_LOSS,
        "ventilation_fraction": VENTILATION_SHARE_OF_OCEAN_LOSS,
        "note": "ventilation term includes stratification, circulation "
                "slowdown, and interior respiration — none of which relax "
                "when surface temperature stabilises",
    }


def apparent_oxygen_utilization(o2_measured_umol_kg: float,
                                T_C: float, S: float = 35.0) -> float:
    """
    Apparent Oxygen Utilisation: how much O2 has been consumed since the
    water parcel last equilibrated with the atmosphere.

    AOU = O2_saturation(T,S) - O2_measured

    Positive AOU means net respiration has occurred since ventilation.
    """
    return oxygen_solubility_umol_kg(T_C, S) - o2_measured_umol_kg


def interior_oxygen_from_ventilation(o2_sat_umol_kg: float,
                                     ventilation_age_yr: float,
                                     OUR_umol_kg_yr: float = 0.35,
                                     remin_timescale_yr: float = 500.0
                                     ) -> float:
    """
    Interior oxygen concentration from ventilation age.

    A water parcel leaves the surface saturated and is drawn down by
    respiration of the organic carbon it carries:

        O2_interior = O2_sat - OUR * tau * (1 - exp(-age / tau))

    Young water (age << tau) reduces to the linear form
    O2 ~ O2_sat - OUR * age. Old water asymptotes to O2_sat - OUR * tau,
    because the labile carbon a ventilated parcel carries is finite — a
    parcel does not keep respiring forever just because it stays down.

    This is the mechanism that links thermohaline slowdown directly to
    deoxygenation: older water is poorer water, independent of warming.

    The transit assumption does NOT hold for basins under sustained
    overlying export production (hypolimnia, semi-enclosed basins,
    shelf dead zones). Those are supply-limited, not age-limited, and go
    fully anoxic — they enter this module through anoxic_area_fraction
    and hypoxic_volume_fraction instead.

    o2_sat_umol_kg     : saturation at the outcrop/formation region
    ventilation_age_yr : time since last surface contact (yr)
    OUR_umol_kg_yr     : oxygen utilisation rate (umol/kg/yr).
                          0.3-1.0 in the thermocline, ~0.05 in the abyss.
    remin_timescale_yr : e-folding time for the parcel's respirable
                          carbon load (yr)
    returns: interior O2 (umol/kg), floored at 0
    """
    if remin_timescale_yr <= 0:
        return max(0.0, o2_sat_umol_kg - OUR_umol_kg_yr * ventilation_age_yr)
    drawdown = (OUR_umol_kg_yr * remin_timescale_yr
                * (1.0 - math.exp(-ventilation_age_yr / remin_timescale_yr)))
    return max(0.0, o2_sat_umol_kg - drawdown)


def oxygen_demand_from_nutrient_load(N_load_Tg_yr: float = 0.0,
                                     P_load_Tg_yr: float = 0.0) -> Dict[str, float]:
    """
    Biological oxygen demand implied by nutrient loading, via Redfield.

    Every mole of new production supported by delivered N or P is
    eventually respired, consuming 8.6 mol O2 per mol N or 138 mol O2 per
    mol P. This converts the nitrogen/phosphorus planetary boundaries
    into an oxygen sink with no free parameters.

    N_load_Tg_yr : reactive nitrogen delivered to waters (Tg N/yr)
    P_load_Tg_yr : reactive phosphorus delivered (Tg P/yr)
    returns: dict with O2 demand in Tmol/yr and Tg O2/yr
    """
    # Tg -> Tmol : Tg / (g/mol) * 1e12 g/Tg / 1e12 mol/Tmol = Tg / molar mass
    N_Tmol = N_load_Tg_yr / 14.007
    P_Tmol = P_load_Tg_yr / 30.974
    O2_Tmol = N_Tmol * REDFIELD_O2_PER_N + P_Tmol * REDFIELD_O2_PER_P
    return {
        "O2_demand_Tmol_yr": O2_Tmol,
        "O2_demand_TgO2_yr": O2_Tmol * M_O2,
        "from_nitrogen_Tmol_yr": N_Tmol * REDFIELD_O2_PER_N,
        "from_phosphorus_Tmol_yr": P_Tmol * REDFIELD_O2_PER_P,
        "note": "upper bound — assumes all delivered nutrient supports new "
                "production that is fully remineralised in-system",
    }


# ─────────────────────────────────────────────
# METABOLIC INDEX — HABITAT VIABILITY (Deutsch et al. 2015)
# ─────────────────────────────────────────────


def metabolic_index(o2_umol_kg: float, T_C: float, S: float = 35.0,
                    A_o: float = 15.0, E_o_eV: float = 0.4,
                    T_ref_C: float = 15.0) -> float:
    """
    Metabolic Index Phi — ratio of oxygen supply to resting demand.

        Phi = A_o * pO2 * exp( (E_o/k_B) * (1/T - 1/T_ref) )

    Phi < 1 : water cannot meet resting metabolic demand — uninhabitable
    Phi ~ 1-3 : survivable at rest, no scope for activity
    Phi > 3 : ecologically viable habitat for active taxa

    Warming enters twice: it lowers pO2 through solubility AND raises
    demand through E_o. That double action is why habitat compresses
    faster than oxygen concentration alone suggests.

    o2_umol_kg : dissolved O2 (umol/kg)
    T_C        : temperature (degC)
    S          : salinity (PSU)
    A_o        : species-specific hypoxia tolerance (1/atm), 5-30 typical
    E_o_eV     : temperature sensitivity of hypoxia tolerance (eV)
    T_ref_C    : reference temperature for A_o (degC)
    returns: Phi (dimensionless)
    """
    o2_sat = oxygen_solubility_umol_kg(T_C, S)
    if o2_sat <= 0:
        return 0.0
    # partial pressure of O2 in the water, in atmospheres
    pO2_atm = O2_MOLE_FRACTION_AIR * (o2_umol_kg / o2_sat)
    T_K, T_ref_K = T_C + 273.15, T_ref_C + 273.15
    thermal = math.exp((E_o_eV / K_B_EV) * (1.0 / T_K - 1.0 / T_ref_K))
    return A_o * pO2_atm * thermal


def habitat_viable(o2_umol_kg: float, T_C: float, S: float = 35.0,
                   phi_crit: float = 3.0, **kwargs) -> Dict[str, object]:
    """
    Habitat viability verdict from the Metabolic Index.

    phi_crit : critical index for sustained activity (1.0 = resting only;
               2-5 typical for active pelagic taxa)
    """
    phi = metabolic_index(o2_umol_kg, T_C, S, **kwargs)
    if phi < 1.0:
        verdict = "UNINHABITABLE"
    elif phi < phi_crit:
        verdict = "RESTING_ONLY"
    else:
        verdict = "VIABLE"
    return {
        "metabolic_index": phi,
        "phi_crit":        phi_crit,
        "verdict":         verdict,
        "viable":          phi >= phi_crit,
    }


# ─────────────────────────────────────────────
# INTERNAL POSITIVE FEEDBACKS
# ─────────────────────────────────────────────


def sediment_phosphorus_release(anoxic_area_fraction: float,
                                sediment_P_pool_Tg: float = 100.0,
                                release_rate_per_yr: float = 0.02
                                ) -> Dict[str, float]:
    """
    Internal phosphorus loading from anoxic sediments.

    Under oxic conditions, phosphate adsorbs onto Fe(III) oxyhydroxides
    in surface sediment. When bottom water goes anoxic, Fe(III) is
    reduced to Fe(II), the mineral dissolves, and the bound P returns to
    the water column. The released P supports more production, which
    consumes more oxygen, which anoxifies more sediment.

    This is the ratchet: cutting external loading does not stop it,
    because the sediment has become the source.

    anoxic_area_fraction : fraction of sediment area with anoxic overlying
                           water (0-1)
    sediment_P_pool_Tg   : mobilisable Fe-bound P inventory (Tg P)
    release_rate_per_yr  : fraction of the exposed pool released per year
    returns: dict with released P and its implied O2 demand
    """
    frac = min(max(anoxic_area_fraction, 0.0), 1.0)
    P_released_Tg_yr = sediment_P_pool_Tg * frac * release_rate_per_yr
    demand = oxygen_demand_from_nutrient_load(P_load_Tg_yr=P_released_Tg_yr)
    return {
        "anoxic_area_fraction":  frac,
        "P_released_Tg_yr":      P_released_Tg_yr,
        "O2_demand_Tmol_yr":     demand["O2_demand_Tmol_yr"],
        "feedback_active":       frac > 0.01,
        "note": "internal loading — persists after external P loading stops",
    }


def n2o_yield_factor(o2_umol_kg: float) -> float:
    """
    Relative N2O yield as a function of dissolved oxygen.

    N2O production peaks in SUBOXIC water, not anoxic water: nitrification
    yield rises as O2 falls, and denitrification produces N2O as an
    intermediate but consumes it again once O2 reaches zero. The peak sits
    right where the expanding oxygen-minimum zones are heading.

    o2_umol_kg : dissolved oxygen (umol/kg)
    returns: yield multiplier relative to well-oxygenated water (1.0)
    """
    o2 = max(o2_umol_kg, 0.0)
    if o2 >= OMZ_UMOL_KG:
        return 1.0
    if o2 <= 0.5:
        # fully anoxic — N2O is consumed to N2
        return 0.5
    # log-shaped rise into the suboxic band, peak near 5-10 umol/kg
    peak = 10.0
    if o2 >= peak:
        return 1.0 + 9.0 * (OMZ_UMOL_KG - o2) / (OMZ_UMOL_KG - peak)
    return 0.5 + 9.5 * (o2 - 0.5) / (peak - 0.5)


def deoxygenation_feedback_gain(hypoxic_volume_fraction: float,
                                anoxic_area_fraction: float,
                                mean_interior_o2_umol_kg: float
                                ) -> Dict[str, float]:
    """
    Composite loop gain for the deoxygenation feedback complex.

    Three amplifying terms, all documented independently:
      1. sediment P release  -> more production -> more O2 demand
      2. N2O yield in suboxic water -> radiative forcing -> warming
         -> lower solubility and stronger stratification
      3. loss of aerobic habitat -> shallower remineralisation
         -> O2 demand concentrated where the water is already poorest

    gain > 1.0 means the system amplifies a perturbation rather than
    damping it. Returned as a dict so a solver can see the components.

    hypoxic_volume_fraction  : fraction of water volume below 2 mg/L (0-1)
    anoxic_area_fraction     : fraction of sediment area under anoxic water
    mean_interior_o2_umol_kg : mean interior oxygen concentration
    """
    P_fb = sediment_phosphorus_release(anoxic_area_fraction)
    p_term = min(P_fb["P_released_Tg_yr"] / 2.0, 1.0)
    n_term = (n2o_yield_factor(mean_interior_o2_umol_kg) - 1.0) / 9.0
    h_term = min(max(hypoxic_volume_fraction, 0.0), 1.0) * 2.0
    gain = 1.0 + 0.5 * p_term + 0.3 * max(n_term, 0.0) + h_term
    return {
        "gain":                  gain,
        "phosphorus_term":       0.5 * p_term,
        "n2o_term":              0.3 * max(n_term, 0.0),
        "habitat_term":          h_term,
        "amplifying":            gain > 1.0,
        "n2o_yield_multiplier":  n2o_yield_factor(mean_interior_o2_umol_kg),
    }


# ─────────────────────────────────────────────
# BOUNDARY STATUS
# ─────────────────────────────────────────────


def deoxygenation_boundary_status(anoxic_volume_ratio_1960: float = None,
                                  hypoxic_volume_fraction: float = None
                                  ) -> Dict[str, object]:
    """
    Status of the proposed aquatic-deoxygenation planetary boundary.

    Control variable: global extent of anoxia, expressed here as a
    multiple of the 1960 anoxic volume (observed present value ~4x).

    anoxic_volume_ratio_1960 : control variable. Defaults to the observed
                               present-day value.
    hypoxic_volume_fraction  : optional secondary indicator (0-1)

    Returns a dict carrying the PROVISIONAL flag — the zone edges are not
    published values (see module header).
    """
    ratio = (ANOXIC_VOLUME_MULTIPLIER_SINCE_1960
             if anoxic_volume_ratio_1960 is None else anoxic_volume_ratio_1960)

    if ratio < BOUNDARY_ZONES["safe_below"]:
        zone, crossed = "SAFE", False
    elif ratio < BOUNDARY_ZONES["increasing_risk_below"]:
        zone, crossed = "INCREASING_RISK", True
    else:
        zone, crossed = "HIGH_RISK", True

    return {
        "boundary":                 "aquatic_deoxygenation",
        "status":                   PROPOSAL_STATUS,
        "control_variable":         PRIMARY_CONTROL_VARIABLE,
        "control_value":            ratio,
        "control_units":            "multiple of 1960 anoxic water volume",
        "zone":                     zone,
        "crossed":                  crossed,
        "hypoxic_volume_fraction":  hypoxic_volume_fraction,
        "zone_edges_provisional":   BOUNDARY_ZONES_PROVISIONAL,
        "n_interactions_with_other_boundaries": len(BOUNDARY_INTERACTIONS),
        "note": (
            "Rose et al. 2024 propose the control variable but publish no "
            "numeric safe value; zone edges here are placeholders for solver "
            "gating, not published thresholds. Ferrer et al. 2026 conclude "
            "current oxygen loss is already at 'unsafe' levels."
        ),
    }


def recovery_timescale(compartment: str) -> Tuple[float, str]:
    """
    Characteristic time for a compartment to re-oxygenate once the
    forcing stops, set by how fast it exchanges water with the surface.

    Returns (years, note). Unknown compartments return the deep-ocean
    value with an explicit fallback note — the conservative choice, since
    the failure mode of this framework is assuming reversibility.
    """
    key = compartment.lower().strip()
    if key in RECOVERY_TIMESCALE_YR:
        return RECOVERY_TIMESCALE_YR[key], "tabulated ventilation timescale"
    return (RECOVERY_TIMESCALE_YR["ocean_deep"],
            "compartment not tabulated — defaulted to deep-ocean timescale")


def reversible_within_human_lifetime(compartment: str,
                                     lifetime_yr: float = 80.0) -> bool:
    """True if the compartment re-oxygenates within one human lifetime."""
    return recovery_timescale(compartment)[0] <= lifetime_yr


# ─────────────────────────────────────────────
# COUPLING INTERFACE
# ─────────────────────────────────────────────


def coupling_state(T_ocean_C: float = 15.0,
                   S_ocean: float = 35.0,
                   ventilation_age_yr: float = 250.0,
                   OUR_umol_kg_yr: float = 0.35,
                   remin_timescale_yr: float = 500.0,
                   anoxic_volume_ratio_1960: float = None,
                   anoxic_area_fraction: float = 0.02,
                   N_load_Tg_yr: float = 150.0,
                   P_load_Tg_yr: float = 14.0) -> Dict[str, object]:
    """
    Deoxygenation state vector for consumption by the hydrosphere and
    biosphere layers.

    T_ocean_C          : mean surface temperature of the outcrop region
    S_ocean            : salinity (PSU)
    ventilation_age_yr : mean age of interior water (from L4 bottom-water
                          formation — this is the thermohaline coupling)
    OUR_umol_kg_yr     : interior oxygen utilisation rate
    anoxic_volume_ratio_1960 : control variable (defaults to observed 4x)
    anoxic_area_fraction     : sediment area under anoxic water
    N_load_Tg_yr, P_load_Tg_yr : reactive nutrient delivery to waters
    """
    o2_sat     = oxygen_solubility_umol_kg(T_ocean_C, S_ocean)
    o2_interior = interior_oxygen_from_ventilation(o2_sat, ventilation_age_yr,
                                                   OUR_umol_kg_yr,
                                                   remin_timescale_yr)
    aou        = o2_sat - o2_interior
    hypoxic_umol = mg_L_to_umol_kg(HYPOXIA_MG_L)
    boundary   = deoxygenation_boundary_status(anoxic_volume_ratio_1960)
    demand     = oxygen_demand_from_nutrient_load(N_load_Tg_yr, P_load_Tg_yr)
    phi        = metabolic_index(o2_interior, T_ocean_C, S_ocean)
    # hypoxic volume fraction: logistic in interior O2, anchored so that
    # present-day mean interior O2 (~160 umol/kg) gives ~2% hypoxic volume
    # and the fraction rises steeply as the mean approaches the threshold.
    hv_frac    = 1.0 / (1.0 + math.exp((o2_interior - hypoxic_umol) / 25.0))
    feedback   = deoxygenation_feedback_gain(hv_frac, anoxic_area_fraction,
                                             o2_interior)
    return {
        "O2_saturation_umol_kg":     o2_sat,
        "O2_saturation_mg_L":        umol_kg_to_mg_L(o2_sat),
        "O2_interior_umol_kg":       o2_interior,
        "O2_interior_mg_L":          umol_kg_to_mg_L(o2_interior),
        "AOU_umol_kg":               aou,
        "hypoxia_threshold_umol_kg": hypoxic_umol,
        "hypoxic_volume_fraction":   hv_frac,
        "metabolic_index":           phi,
        "habitat_viable":            phi >= 3.0,
        "anoxic_volume_ratio_1960":  boundary["control_value"],
        "boundary_zone":             boundary["zone"],
        "boundary_crossed":          boundary["crossed"],
        "boundary_status":           boundary["status"],
        "nutrient_O2_demand_Tmol_yr": demand["O2_demand_Tmol_yr"],
        "n2o_yield_multiplier":      feedback["n2o_yield_multiplier"],
        "deox_feedback_gain":        feedback["gain"],
        "deox_loop_active":          (feedback["amplifying"]
                                      and hv_frac > HYPOXIC_VOLUME_FRACTION_REFERENCE),
        "recovery_timescale_yr":     recovery_timescale("ocean_deep")[0],
        "reversible_in_lifetime":    reversible_within_human_lifetime("ocean_deep"),
        "cascade_to_atmosphere":     "N2O, CH4 from anoxic water and sediment",
        "cascade_to_biosphere":      "habitat compression, benthic mortality, "
                                     "Hg methylation",
        "cascade_from_hydrosphere":  "temperature, stratification, ventilation age",
        "cascade_from_biosphere":    "nutrient loading, export production, "
                                     "remineralisation depth",
        "note": "oxygen loss is not reversible on policy timescales — deep "
                "water re-ventilates on ~1000 yr",
    }


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("AQUATIC DEOXYGENATION — PROPOSED TENTH PLANETARY BOUNDARY")
    print("=" * 64)
    print(f"  Proposal status:      {PROPOSAL_STATUS}")
    print(f"  Control variable:     {PRIMARY_CONTROL_VARIABLE}")
    print(f"  Rose et al.:          {PROPOSAL_FIRST_PUBLISHED}")
    print(f"  Ferrer et al.:        {INTERACTION_SYNTHESIS_YEAR}")

    print("\nOBSERVED STATE")
    print(f"  Ocean O2 inventory loss 1960-2010: "
          f"{OCEAN_O2_LOSS_PCT_1960_2010}% "
          f"({OCEAN_O2_LOSS_PMOL_1960_2010} +/- "
          f"{OCEAN_O2_LOSS_PMOL_UNCERTAINTY} Pmol)")
    print(f"  Zero-O2 water volume since 1960:   "
          f"x{ANOXIC_VOLUME_MULTIPLIER_SINCE_1960:.0f}")
    print(f"  New low-O2 open ocean:             "
          f"{OMZ_AREA_EXPANSION_KM2_SINCE_1960:.1e} km2")
    print(f"  Lakes since 1980:  surface {LAKE_SURFACE_O2_DECLINE_PCT}%, "
          f"deep {LAKE_DEEP_O2_DECLINE_PCT}%")
    print(f"  Coastal low-O2 sites:              {COASTAL_LOW_O2_SITES}+ "
          f"({COASTAL_PERSISTENT_HYPOXIC_SITES}+ persistently hypoxic)")

    print("\nSOLUBILITY PHYSICS")
    for T in (5.0, 15.0, 25.0):
        print(f"  {T:5.1f} degC, S=35: "
              f"{oxygen_solubility_umol_kg(T):6.1f} umol/kg  "
              f"({oxygen_solubility_mg_L(T):5.2f} mg/L)")
    warm = solubility_loss_from_warming(15.0, 2.0)
    print(f"  +2 K at 15 degC -> {warm['pct_loss']:.1f}% solubility loss")
    attr = attribute_oxygen_loss(10.0)
    print(f"  10 umol/kg observed loss -> "
          f"{attr['solubility_umol_kg']:.1f} solubility / "
          f"{attr['ventilation_umol_kg']:.1f} ventilation+biology")

    print("\nVENTILATION COUPLING")
    for age in (50.0, 250.0, 800.0, 2000.0):
        o2 = interior_oxygen_from_ventilation(
            oxygen_solubility_umol_kg(8.0), age)
        print(f"  ventilation age {age:5.0f} yr -> interior O2 "
              f"{o2:6.1f} umol/kg ({umol_kg_to_mg_L(o2):5.2f} mg/L)")

    print("\nMETABOLIC INDEX")
    for o2 in (250.0, 120.0, 60.0, 20.0):
        h = habitat_viable(o2, 15.0)
        print(f"  O2 {o2:6.1f} umol/kg -> Phi {h['metabolic_index']:5.2f} "
              f"({h['verdict']})")

    print("\nBOUNDARY STATUS")
    st = deoxygenation_boundary_status()
    print(f"  control value:  x{st['control_value']:.1f} 1960 anoxic volume")
    print(f"  zone:           {st['zone']}  (crossed={st['crossed']})")
    print(f"  zone edges provisional: {st['zone_edges_provisional']}")

    print("\nINTERACTION CATALOG")
    summ = interaction_summary()
    print(f"  interactions: {summ['n_interactions']} across "
          f"{summ['n_boundaries_touched']} boundary processes")
    print(f"  by sign:      {summ['by_sign']}")
    print(f"  by direction: {summ['by_direction']}")
    for i in BOUNDARY_INTERACTIONS:
        print(f"    - {i.boundary:34s} {i.direction:14s} {i.sign}")

    print("\nFEEDBACK GAIN")
    fb = deoxygenation_feedback_gain(0.02, 0.02, 160.0)
    print(f"  gain={fb['gain']:.3f}  P={fb['phosphorus_term']:.3f}  "
          f"N2O={fb['n2o_term']:.3f}  habitat={fb['habitat_term']:.3f}")

    print("\nRECOVERY")
    for c in ("lake_surface", "coastal_shelf", "ocean_thermocline",
              "ocean_deep", "aquifer"):
        yr, note = recovery_timescale(c)
        print(f"  {c:20s} {yr:7.0f} yr  "
              f"(within a lifetime: {reversible_within_human_lifetime(c)})")

    print("\nCOUPLING STATE")
    cs = coupling_state()
    for k in ("O2_saturation_umol_kg", "O2_interior_umol_kg", "AOU_umol_kg",
              "hypoxic_volume_fraction", "metabolic_index", "boundary_zone",
              "deox_feedback_gain", "deox_loop_active"):
        print(f"  {k:28s} {cs[k]}")
