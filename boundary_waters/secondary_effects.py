# boundary_waters/secondary_effects.py
# earth-systems-physics
# CC0 — No Rights Reserved
"""
Secondary and tertiary effects for the BWCA cascade.

This module adds what the linear feed-forward cascade misses:
self-reinforcing loops, missing contaminants, ecological couplings,
inter-generational effects, and a peatland-methane pathway that
links the site model back to the parent repo's atmosphere layer.

Structure:
    SECTION 1: Self-reinforcing community collapse loops
    SECTION 2: Missing contaminants (Se, Mn)
    SECTION 3: Ecological service loss (beaver, mycorrhizal, invasives)
    SECTION 4: Inter-generational transmission (epigenetic, cultural)
    SECTION 5: Peatland methane feedback
    SECTION 6: Combined secondary cascade engine
"""

from dataclasses import dataclass, field
from math import exp, log
from typing import Any


# ══════════════════════════════════════════════════════════════
# CONSTANTS — sourced where possible, noted where assumed
# ══════════════════════════════════════════════════════════════

# Selenium
SE_PER_TONNE_MG = 1.8           # mg Se / tonne Cu-Ni sulfide waste
SE_MOBILIZATION_FRAC = 0.06     # annual fraction mobilized (higher than sulfate — Se is more soluble)
SE_REPRODUCTIVE_THRESHOLD_UG_L = 3.1   # ug/L; Elk Valley (BC) cutthroat trout (Teck 2014)
SE_EGG_BAF = 5.0e3              # bioaccumulation factor in fish eggs vs water

# Manganese
MN_PER_TONNE_MG = 850.0        # mg Mn / tonne (Duluth Complex assay)
MN_MOBILIZATION_FRAC = 0.03    # conservative; Mn mobilizes under reducing conditions
MN_NEURO_THRESHOLD_UG_L = 300.0  # EPA lifetime health advisory for drinking water
MN_CHILD_NEURO_THRESHOLD_UG_L = 100.0  # lower for developing nervous systems

# School district
MIN_ENROLLMENT_VIABLE = 200     # below this, state consolidation pressure
STATE_FUNDING_PER_PUPIL_USD = 12500  # MN avg FY2024
SCHOOL_AGE_FRAC = 0.18         # fraction of population that is school-age

# Healthcare
CLINIC_VIABLE_POP = 2500       # minimum catchment for rural clinic
HOSPITAL_VIABLE_POP = 8000     # minimum for critical access hospital
ELY_HOSPITAL_POP_SERVED = 12400  # approximate catchment

# Insurance
CONTAMINATION_INSURANCE_WITHDRAWAL_THRESHOLD = 0.15  # property value drop fraction
UNINSURABLE_DEPARTURE_RATE = 0.08  # annual departure rate once insurance unavailable

# Emergency services
VOLUNTEER_POOL_FRAC = 0.03     # fraction of pop that volunteers for fire dept
MIN_VOLUNTEERS_FUNCTIONAL = 15  # minimum for a functional volunteer dept
RESPONSE_DEGRADATION_EXPONENT = 2.0  # response time scales as (needed/available)^2

# Beaver ecosystem services
BEAVER_DENSITY_PER_KM2 = 0.4   # boreal average; BWCA is higher
BEAVER_WETLAND_TREATMENT_FRAC = 0.12  # fraction of contaminant load naturally treated
BEAVER_HABITAT_SENSITIVITY_MG_L = 20.0  # sulfate above which beaver abandon

# Mycorrhizal networks
MYCORRHIZAL_HEAVY_METAL_THRESHOLD_MG_KG = 50.0  # soil Pb+Cu at which networks fragment
MYCORRHIZAL_RECOVERY_YR = 80   # decades to re-establish after metal removal
REVEGETATION_SUCCESS_WITH_NETWORK = 0.85
REVEGETATION_SUCCESS_WITHOUT_NETWORK = 0.15

# Invasive species
ROAD_KM_PER_MINE = 45.0       # new road construction for mine access
EARTHWORM_ADVANCE_RATE_KM_YR = 0.5  # documented rate into BWCA from south
DUFF_LOSS_TIMELINE_YR = 5      # years to consume duff layer once earthworms arrive

# Epigenetic / inter-generational
HG_EPIGENETIC_GENERATIONS = 3  # documented in Minamata follow-up studies
PB_IQ_LOSS_PER_UG_DL = 2.6    # CDC; no safe level
GENERATION_LENGTH_YR = 25

# Cultural transmission
IDENTITY_LEVEL_REPLACEMENT_PROBABILITY = 0.0  # cannot be retrained post-plasticity-window
MANOOMIN_KNOWLEDGE_HOLDERS_FRAC = 0.15  # fraction of tribal pop with identity-level harvesting knowledge
KNOWLEDGE_LOSS_IF_DISPLACED = 0.90  # fraction of identity-level knowledge lost if holder displaced

# Peatland methane
PEAT_DEPTH_M_BWCA = 2.5       # average in BWCA peatlands
PEAT_AREA_KM2 = 850.0         # estimated peatland area in affected watershed
BASELINE_CH4_KG_M2_YR = 0.015 # boreal peatland average
SULFATE_SUPPRESSION_FRAC = 0.30  # SRB outcompete methanogens initially
POST_SULFATE_REBOUND_MULTIPLIER = 1.8  # disturbed community overshoots baseline
SULFATE_THRESHOLD_FOR_SRB_MG_L = 5.0  # sulfate at which SRB become dominant


# ══════════════════════════════════════════════════════════════
# SECTION 1: SELF-REINFORCING COMMUNITY COLLAPSE LOOPS
# ══════════════════════════════════════════════════════════════

@dataclass
class CommunityLoopState:
    """Tracks the state of five self-reinforcing collapse loops."""
    population: float
    school_enrollment: float = 0.0
    school_open: bool = True
    school_funding_usd: float = 0.0
    clinic_open: bool = True
    hospital_open: bool = True
    insurance_available: bool = True
    insurance_departure_pressure: float = 0.0
    volunteer_firefighters: int = 0
    response_time_multiplier: float = 1.0
    tax_base_usd: float = 0.0
    infrastructure_decay_frac: float = 0.0
    property_value_multiplier: float = 1.0
    loop_departure_frac: float = 0.0


def school_district_loop(pop: float, initial_pop: float) -> dict:
    """School district death spiral."""
    enrollment = pop * SCHOOL_AGE_FRAC
    funding = enrollment * STATE_FUNDING_PER_PUPIL_USD
    viable = enrollment >= MIN_ENROLLMENT_VIABLE
    # If school closes, families with children leave
    departure_pressure = 0.0
    if not viable:
        # 80% of families with school-age children leave within 3 years
        families_with_kids_frac = SCHOOL_AGE_FRAC * 2.5  # ~45% of pop is families with kids
        departure_pressure = min(0.30, families_with_kids_frac * 0.80)
    return {
        "enrollment": enrollment,
        "funding_usd": funding,
        "school_open": viable,
        "departure_pressure": departure_pressure,
    }


def healthcare_access_loop(pop: float) -> dict:
    """Healthcare access collapse."""
    clinic_viable = pop >= CLINIC_VIABLE_POP
    hospital_viable = pop >= HOSPITAL_VIABLE_POP
    departure_pressure = 0.0
    if not hospital_viable:
        departure_pressure += 0.05  # chronic out-migration
    if not clinic_viable:
        departure_pressure += 0.10  # acute — no primary care
    return {
        "clinic_open": clinic_viable,
        "hospital_open": hospital_viable,
        "departure_pressure": departure_pressure,
    }


def insurance_market_loop(property_value_drop_frac: float) -> dict:
    """Insurance market withdrawal."""
    available = property_value_drop_frac < CONTAMINATION_INSURANCE_WITHDRAWAL_THRESHOLD
    departure_rate = 0.0 if available else UNINSURABLE_DEPARTURE_RATE
    return {
        "insurance_available": available,
        "annual_departure_rate": departure_rate,
    }


def emergency_services_loop(pop: float) -> dict:
    """Volunteer fire department collapse."""
    volunteers = int(pop * VOLUNTEER_POOL_FRAC)
    if volunteers >= MIN_VOLUNTEERS_FUNCTIONAL:
        response_multiplier = 1.0
    elif volunteers > 0:
        response_multiplier = (MIN_VOLUNTEERS_FUNCTIONAL / volunteers) ** RESPONSE_DEGRADATION_EXPONENT
    else:
        response_multiplier = 10.0  # effectively no response
    return {
        "volunteer_firefighters": volunteers,
        "response_time_multiplier": response_multiplier,
        "functional": volunteers >= MIN_VOLUNTEERS_FUNCTIONAL,
    }


def tax_base_loop(
    pop: float,
    initial_pop: float,
    property_value_multiplier: float,
    prev_infrastructure_decay: float,
) -> dict:
    """Tax base death spiral with feedback."""
    pop_frac = pop / initial_pop if initial_pop > 0 else 1.0
    # Tax base scales with population × property values
    tax_base_frac = pop_frac * property_value_multiplier
    # Infrastructure decay: deferred maintenance accumulates
    maintenance_shortfall = max(0.0, 1.0 - tax_base_frac)
    infrastructure_decay = min(1.0, prev_infrastructure_decay + maintenance_shortfall * 0.02)
    # Infrastructure decay feeds back into property values
    new_property_multiplier = max(0.1, property_value_multiplier - infrastructure_decay * 0.05)
    return {
        "tax_base_frac": tax_base_frac,
        "infrastructure_decay": infrastructure_decay,
        "property_value_multiplier": new_property_multiplier,
    }


def run_community_loops(
    pop: float,
    initial_pop: float,
    property_value_drop_frac: float,
    prev_state: CommunityLoopState,
) -> CommunityLoopState:
    """Run all five loops for one year; return updated state."""
    school = school_district_loop(pop, initial_pop)
    health = healthcare_access_loop(pop)
    insurance = insurance_market_loop(property_value_drop_frac)
    emergency = emergency_services_loop(pop)
    tax = tax_base_loop(
        pop, initial_pop,
        prev_state.property_value_multiplier,
        prev_state.infrastructure_decay_frac,
    )

    # Combine departure pressures from all loops
    combined_departure = (
        school["departure_pressure"]
        + health["departure_pressure"]
        + insurance["annual_departure_rate"]
    )
    # Infrastructure decay adds its own pressure
    if tax["infrastructure_decay"] > 0.3:
        combined_departure += 0.03

    combined_departure = min(0.25, combined_departure)  # cap annual departure

    new_pop = pop * (1.0 - combined_departure)

    return CommunityLoopState(
        population=new_pop,
        school_enrollment=school["enrollment"],
        school_open=school["school_open"],
        school_funding_usd=school["funding_usd"],
        clinic_open=health["clinic_open"],
        hospital_open=health["hospital_open"],
        insurance_available=insurance["insurance_available"],
        insurance_departure_pressure=insurance["annual_departure_rate"],
        volunteer_firefighters=emergency["volunteer_firefighters"],
        response_time_multiplier=emergency["response_time_multiplier"],
        tax_base_usd=tax["tax_base_frac"] * initial_pop * 5000,
        infrastructure_decay_frac=tax["infrastructure_decay"],
        property_value_multiplier=tax["property_value_multiplier"],
        loop_departure_frac=combined_departure,
    )


# ══════════════════════════════════════════════════════════════
# SECTION 2: MISSING CONTAMINANTS (Se, Mn)
# ══════════════════════════════════════════════════════════════

def selenium_layer(cumulative_waste_tonnes: float, exposure: float,
                   flush_rate: float, receiving_vol_m3: float) -> dict:
    """Selenium release from Cu-Ni sulfide waste.

    Se bioaccumulates in EGGS not tissue — different pathway than Hg.
    Elk Valley (BC, Teck Resources) is the direct analog: selenium
    from coal mining destroyed cutthroat trout reproduction at
    concentrations the monitoring system wasn't designed to catch.
    """
    se_mg_yr = cumulative_waste_tonnes * SE_PER_TONNE_MG * SE_MOBILIZATION_FRAC * exposure
    # Same effective-parameter approach as sulfate (see layers.py comment)
    se_ug_l = se_mg_yr / (flush_rate * receiving_vol_m3) * 1e-3
    egg_se_ug_g = se_ug_l * SE_EGG_BAF / 1000.0
    reproductive_failure = se_ug_l > SE_REPRODUCTIVE_THRESHOLD_UG_L
    return {
        "se_ug_l": se_ug_l,
        "egg_se_ug_g": egg_se_ug_g,
        "fish_reproductive_failure": reproductive_failure,
    }


def manganese_layer(cumulative_waste_tonnes: float, exposure: float,
                    flush_rate: float, receiving_vol_m3: float) -> dict:
    """Manganese — neurotoxic at low concentrations.

    Released alongside Fe in AMD under reducing conditions.
    Documented at Picher (Tar Creek) alongside Pb/Zn.
    Children's threshold is lower than adults.
    """
    mn_mg_yr = cumulative_waste_tonnes * MN_PER_TONNE_MG * MN_MOBILIZATION_FRAC * exposure
    mn_ug_l = mn_mg_yr / (flush_rate * receiving_vol_m3) * 1e-3
    adult_neuro_risk = mn_ug_l > MN_NEURO_THRESHOLD_UG_L
    child_neuro_risk = mn_ug_l > MN_CHILD_NEURO_THRESHOLD_UG_L
    return {
        "mn_ug_l": mn_ug_l,
        "adult_neuro_risk": adult_neuro_risk,
        "child_neuro_risk": child_neuro_risk,
    }


# ══════════════════════════════════════════════════════════════
# SECTION 3: ECOLOGICAL SERVICE LOSS
# ══════════════════════════════════════════════════════════════

def beaver_services(sulfate_mg_l: float, forest_loss_frac: float) -> dict:
    """Beaver dam ecosystem services as natural water treatment.

    Beaver create wetlands that trap sediment, sequester metals, and
    host sulfate-reducing bacteria. Mining destroys this for free
    subsidy the watershed currently provides.
    """
    habitat_viable = sulfate_mg_l < BEAVER_HABITAT_SENSITIVITY_MG_L
    if habitat_viable and forest_loss_frac < 0.3:
        treatment_frac = BEAVER_WETLAND_TREATMENT_FRAC
        density = BEAVER_DENSITY_PER_KM2
    else:
        treatment_frac = 0.0
        density = BEAVER_DENSITY_PER_KM2 * max(0, 1.0 - sulfate_mg_l / 50.0)
    return {
        "beaver_habitat_viable": habitat_viable,
        "natural_treatment_frac": treatment_frac,
        "beaver_density": density,
        "treatment_service_lost": not habitat_viable,
    }


def mycorrhizal_network(soil_metal_mg_kg: float,
                        years_since_contamination: int) -> dict:
    """Mycorrhizal network integrity.

    Heavy metals kill boreal soil fungi. Without mycorrhizal networks,
    trees cannot establish. Closure plans assume revegetation; this
    mechanism makes revegetation fail.
    """
    network_intact = soil_metal_mg_kg < MYCORRHIZAL_HEAVY_METAL_THRESHOLD_MG_KG
    if network_intact:
        revegetation_success = REVEGETATION_SUCCESS_WITH_NETWORK
        recovery_years_remaining = 0
    else:
        revegetation_success = REVEGETATION_SUCCESS_WITHOUT_NETWORK
        recovery_years_remaining = max(
            0, MYCORRHIZAL_RECOVERY_YR - years_since_contamination
        )
    return {
        "network_intact": network_intact,
        "revegetation_success_prob": revegetation_success,
        "recovery_years_remaining": recovery_years_remaining,
    }


def invasive_species_pressure(mine_active: bool,
                              years_since_mine_start: int) -> dict:
    """Invasive species corridor from mining roads.

    Mining roads are invasion highways for European earthworms (already
    advancing into BWCA). Earthworms consume the duff layer -> changes
    soil chemistry -> eliminates boreal understory regeneration.
    Irreversible on human timescales.
    """
    if not mine_active and years_since_mine_start <= 0:
        return {
            "road_km": 0.0,
            "earthworm_front_km": 0.0,
            "duff_layer_intact": True,
            "understory_regeneration_possible": True,
        }
    road_km = ROAD_KM_PER_MINE
    earthworm_advance = min(road_km, years_since_mine_start * EARTHWORM_ADVANCE_RATE_KM_YR)
    duff_consumed = years_since_mine_start > DUFF_LOSS_TIMELINE_YR
    return {
        "road_km": road_km,
        "earthworm_front_km": earthworm_advance,
        "duff_layer_intact": not duff_consumed,
        "understory_regeneration_possible": not duff_consumed,
    }


# ══════════════════════════════════════════════════════════════
# SECTION 4: INTER-GENERATIONAL EFFECTS
# ══════════════════════════════════════════════════════════════

def epigenetic_cascade(kids_exposed: int, hg_ng_l: float,
                       pb_mg_yr: float, mn_ug_l: float) -> dict:
    """Inter-generational transmission of contaminant effects.

    Pb and Hg exposure in utero causes effects that persist 2-3
    generations beyond the exposed individual. The model's
    kids_neuro_impaired is a point estimate for one cohort; the
    actual cost extends 60+ years per exposed child.

    Sources: Minamata follow-up studies (3-generation Hg effects);
    CDC (Pb IQ loss, no safe level); Picher (Mn + Pb co-exposure).
    """
    # Hg effects persist across generations (Minamata data)
    hg_affected_generations = HG_EPIGENETIC_GENERATIONS if hg_ng_l > 5.0 else 0
    # Pb IQ effects are per-child but the economic cost compounds
    # across the child's lifetime (lost earnings, special education)
    pb_lifetime_cost_per_child = PB_IQ_LOSS_PER_UG_DL * 15000  # $15k/IQ-point (Gould 2009)
    # Mn adds to neurodevelopmental burden
    mn_additional_risk = 1.0 if mn_ug_l > MN_CHILD_NEURO_THRESHOLD_UG_L else 0.0
    total_affected = kids_exposed * (1 + hg_affected_generations)
    total_cost = kids_exposed * pb_lifetime_cost_per_child
    return {
        "generations_affected": 1 + hg_affected_generations,
        "total_individuals_across_generations": total_affected,
        "pb_lifetime_cost_per_child_usd": pb_lifetime_cost_per_child,
        "total_epigenetic_cost_usd": total_cost,
        "mn_compounding": mn_additional_risk > 0,
    }


def cultural_transmission_break(
    tribal_pop: int,
    manoomin_acres_lost: float,
    manoomin_acres_total: float,
    forced_migrants_tribal: int,
) -> dict:
    """Cultural knowledge transmission failure.

    Manoomin harvesting is identity-level encoded (see
    calibration/architecture_mismatch.py: acquired during plasticity
    window under survival-embedded conditions). If the generation
    holding this knowledge is displaced or the resource destroyed,
    the knowledge does not transfer. Identity-level encoding cannot
    be retrained in adulthood.

    This is not property damage. It is an irreversible loss of a
    cognitive architecture that took generations to build.
    """
    knowledge_holders = int(tribal_pop * MANOOMIN_KNOWLEDGE_HOLDERS_FRAC)
    resource_loss_frac = min(1.0, manoomin_acres_lost / manoomin_acres_total) if manoomin_acres_total > 0 else 0.0
    displacement_frac = forced_migrants_tribal / tribal_pop if tribal_pop > 0 else 0.0

    # Knowledge is lost through EITHER resource destruction OR
    # holder displacement — whichever is larger
    loss_pathway = max(resource_loss_frac, displacement_frac)
    holders_lost = int(knowledge_holders * loss_pathway * KNOWLEDGE_LOSS_IF_DISPLACED)
    holders_remaining = knowledge_holders - holders_lost

    # Below critical mass, transmission chain breaks
    transmission_viable = holders_remaining >= 10
    return {
        "knowledge_holders_initial": knowledge_holders,
        "knowledge_holders_remaining": holders_remaining,
        "holders_lost": holders_lost,
        "loss_pathway": "resource_destruction" if resource_loss_frac > displacement_frac else "displacement",
        "transmission_viable": transmission_viable,
        "replacement_probability": IDENTITY_LEVEL_REPLACEMENT_PROBABILITY,
        "irreversible": not transmission_viable,
    }


# ══════════════════════════════════════════════════════════════
# SECTION 5: PEATLAND METHANE FEEDBACK
# ══════════════════════════════════════════════════════════════

def peatland_methane(sulfate_mg_l: float,
                     years_of_contamination: int) -> dict:
    """Peatland CH4 feedback — links site to global carbon cycle.

    BWCA sits on deep peat. Sulfate contamination changes the
    microbial community:
      Phase 1: SRB outcompete methanogens -> CH4 suppressed
      Phase 2: sulfate consumed -> disturbed community overshoots
               baseline CH4 production

    This connects boundary_waters/ to the parent repo's
    layer_3_atmosphere and layer_6_biosphere.
    """
    if sulfate_mg_l < SULFATE_THRESHOLD_FOR_SRB_MG_L:
        # Below threshold: normal peatland methane
        ch4_multiplier = 1.0
        phase = "baseline"
    elif years_of_contamination < 50:
        # Phase 1: SRB suppress methanogens
        suppression = min(SULFATE_SUPPRESSION_FRAC,
                          sulfate_mg_l / 100.0)
        ch4_multiplier = 1.0 - suppression
        phase = "SRB_suppression"
    else:
        # Phase 2: sulfate exhausted locally, disturbed community rebounds
        rebound_progress = min(1.0, (years_of_contamination - 50) / 100.0)
        ch4_multiplier = 1.0 + (POST_SULFATE_REBOUND_MULTIPLIER - 1.0) * rebound_progress
        phase = "post_sulfate_rebound"

    baseline_ch4_tonnes_yr = (PEAT_AREA_KM2 * 1e6
                              * BASELINE_CH4_KG_M2_YR / 1000.0)
    actual_ch4_tonnes_yr = baseline_ch4_tonnes_yr * ch4_multiplier
    delta_ch4_tonnes_yr = actual_ch4_tonnes_yr - baseline_ch4_tonnes_yr

    return {
        "phase": phase,
        "ch4_multiplier": ch4_multiplier,
        "baseline_ch4_tonnes_yr": baseline_ch4_tonnes_yr,
        "actual_ch4_tonnes_yr": actual_ch4_tonnes_yr,
        "delta_ch4_tonnes_yr": delta_ch4_tonnes_yr,
        "co2e_tonnes_yr": delta_ch4_tonnes_yr * 28.0,  # GWP-100
    }


# ══════════════════════════════════════════════════════════════
# SECTION 6: COMBINED SECONDARY CASCADE
# ══════════════════════════════════════════════════════════════

def run_secondary_cascade(
    year: int,
    mine_active: bool,
    years_since_mine_start: int,
    cumulative_waste_tonnes: float,
    primary: dict,
    prev_community: CommunityLoopState,
    initial_pop: float = 12400.0,
    tribal_pop: float = 8700.0,
) -> dict:
    """Run all secondary/tertiary effects for one year.

    Takes the primary cascade output dict and the previous year's
    community loop state; returns a combined dict of all secondary
    effects plus the updated community loop state.
    """
    from constants import (
        MEAN_LAKE_RESIDENCE_YR, MANOOMIN_ACRES_AT_RISK,
    )
    flush_rate = 1.0 / MEAN_LAKE_RESIDENCE_YR
    receiving_vol = 3.0e8
    exposure = primary.get("exposure", 0.0)

    # Section 2: missing contaminants
    se = selenium_layer(cumulative_waste_tonnes, exposure,
                        flush_rate, receiving_vol)
    mn = manganese_layer(cumulative_waste_tonnes, exposure,
                         flush_rate, receiving_vol)

    # Section 3: ecological services
    beaver = beaver_services(
        primary.get("sulfate_mg_l", 0.0),
        primary.get("forest_acres_lost", 0.0) / 234000.0,
    )
    soil_metal = primary.get("sulfate_mg_l", 0.0) * 0.8  # rough proxy
    myco = mycorrhizal_network(soil_metal, years_since_mine_start)
    invasives = invasive_species_pressure(mine_active, years_since_mine_start)

    # Section 4: inter-generational
    kids_exposed = int(prev_community.population * SCHOOL_AGE_FRAC)
    epigenetic = epigenetic_cascade(
        kids_exposed,
        primary.get("hg_ng_l", 0.0),
        primary.get("pb_mg_yr", 0.0),
        mn["mn_ug_l"],
    )
    cultural = cultural_transmission_break(
        int(tribal_pop),
        primary.get("manoomin_acres_lost", 0.0),
        MANOOMIN_ACRES_AT_RISK,
        primary.get("treaty_harvesters_displaced", 0),
    )

    # Section 5: peatland methane
    peat = peatland_methane(
        primary.get("sulfate_mg_l", 0.0),
        years_since_mine_start,
    )

    # Section 1: community loops — seeded by primary cascade
    #
    # Primary cascade's forced_migrants is a STOCK (total displaced
    # at this point), not a flow. The loop population starts at
    # initial_pop minus primary displacement, then the loops apply
    # ADDITIONAL departures from institutional collapse.
    primary_displaced = primary.get("forced_migrants", 0)
    base_pop = max(0.0, initial_pop - primary_displaced)

    # Property value driven by contamination severity + job loss
    contamination_property_drop = min(0.25, primary.get("sulfate_mg_l", 0.0) / 50.0)
    tourism_frac_lost = primary.get("tourism_jobs_lost", 0) / 17000.0
    tourism_property_drop = min(0.25, tourism_frac_lost * 0.4)
    # Infrastructure decay from prior year feeds back
    decay_property_drop = prev_community.infrastructure_decay_frac * 0.15
    total_property_drop = min(0.70, contamination_property_drop
                              + tourism_property_drop + decay_property_drop)

    # Use the SMALLER of base_pop and prev loop pop — population
    # can only go down, not recover within the model horizon
    effective_pop = min(base_pop, prev_community.population)

    adjusted_prev = CommunityLoopState(
        population=effective_pop,
        school_enrollment=prev_community.school_enrollment,
        school_open=prev_community.school_open,
        school_funding_usd=prev_community.school_funding_usd,
        clinic_open=prev_community.clinic_open,
        hospital_open=prev_community.hospital_open,
        insurance_available=prev_community.insurance_available,
        insurance_departure_pressure=prev_community.insurance_departure_pressure,
        volunteer_firefighters=prev_community.volunteer_firefighters,
        response_time_multiplier=prev_community.response_time_multiplier,
        tax_base_usd=prev_community.tax_base_usd,
        infrastructure_decay_frac=prev_community.infrastructure_decay_frac,
        property_value_multiplier=max(0.1, 1.0 - total_property_drop),
        loop_departure_frac=prev_community.loop_departure_frac,
    )

    community = run_community_loops(
        adjusted_prev.population,
        initial_pop,
        total_property_drop,
        adjusted_prev,
    )

    return {
        "secondary_year": year,
        # Contaminants
        **{f"se_{k}": v for k, v in se.items()},
        **{f"mn_{k}": v for k, v in mn.items()},
        # Ecological services
        **{f"beaver_{k}": v for k, v in beaver.items()},
        **{f"myco_{k}": v for k, v in myco.items()},
        **{f"invasive_{k}": v for k, v in invasives.items()},
        # Inter-generational
        **{f"epigenetic_{k}": v for k, v in epigenetic.items()},
        **{f"cultural_{k}": v for k, v in cultural.items()},
        # Peatland
        **{f"peat_{k}": v for k, v in peat.items()},
        # Community loops
        "loop_population": community.population,
        "loop_school_open": community.school_open,
        "loop_clinic_open": community.clinic_open,
        "loop_hospital_open": community.hospital_open,
        "loop_insurance_available": community.insurance_available,
        "loop_volunteer_firefighters": community.volunteer_firefighters,
        "loop_response_time_multiplier": community.response_time_multiplier,
        "loop_infrastructure_decay": community.infrastructure_decay_frac,
        "loop_property_value_mult": community.property_value_multiplier,
        "loop_departure_frac": community.loop_departure_frac,
        "_community_state": community,
    }


def _run_scenario(scenario_name, label):
    import sys
    if "boundary_waters" not in sys.path[0]:
        sys.path.insert(0, "boundary_waters")
    from cascade import run_cascade

    hist = run_cascade(seed=42, scenario=scenario_name)
    initial_pop = 12400.0
    state = CommunityLoopState(population=initial_pop)

    snapshots = [0, 10, 20, 30, 50, 100, 200, 499]
    print(f"\n{'=' * 80}")
    print(f"  {label}")
    print(f"{'=' * 80}")
    print(f"\n{'Yr':>4} {'Pop':>7} {'School':>6} {'Hosp':>5} "
          f"{'Insur':>5} {'Vol FF':>6} {'Se ug/L':>8} {'Mn ug/L':>8} "
          f"{'Beaver':>6} {'Myco':>5} {'CH4 x':>6}")
    print("-" * 80)

    for yr in range(500):
        h = hist[yr]
        mine_active = h["mine_active"]
        yrs = max(0, yr - 5)
        sec = run_secondary_cascade(
            yr, mine_active, yrs,
            h["cumulative_waste_Mt"] * 1e6,
            h, state, initial_pop,
        )
        state = sec["_community_state"]
        if yr in snapshots:
            print(f"{yr:>4} {state.population:>7.0f} "
                  f"{'open' if sec['loop_school_open'] else 'SHUT':>6} "
                  f"{'open' if sec['loop_hospital_open'] else 'SHUT':>5} "
                  f"{'yes' if sec['loop_insurance_available'] else 'NO':>5} "
                  f"{sec['loop_volunteer_firefighters']:>6} "
                  f"{sec['se_se_ug_l']:>8.3f} "
                  f"{sec['mn_mn_ug_l']:>8.1f} "
                  f"{'yes' if sec['beaver_beaver_habitat_viable'] else 'no':>6} "
                  f"{'yes' if sec['myco_network_intact'] else 'no':>5} "
                  f"{sec['peat_ch4_multiplier']:>6.2f}")

    print(f"\n  Cultural transmission viable: {sec['cultural_transmission_viable']}")
    print(f"  Epigenetic generations affected: {sec['epigenetic_generations_affected']}")
    print(f"  Peatland CH4 delta: {sec['peat_delta_ch4_tonnes_yr']:.0f} tonnes/yr "
          f"({sec['peat_co2e_tonnes_yr']:.0f} CO2e)")


def print_summary():
    _run_scenario("proceed", "PROCEED SCENARIO — mine operates (seed=42)")
    _run_scenario("tailings_failure", "TAILINGS FAILURE — Mount Polley-class (seed=42)")


if __name__ == "__main__":
    print_summary()

