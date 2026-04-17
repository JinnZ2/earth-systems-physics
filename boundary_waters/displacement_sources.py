# boundary_waters/displacement_sources.py
# earth-systems-physics
# CC0 — No Rights Reserved
"""
Sourced displacement analogs for the BWCA cascade model.

Five displacement pathways, each documented from real cases with
census data, peer-reviewed studies, or government records. These
ground the behavioral parameters in constants.py that were
previously unsourced magic numbers.

Pathways:
    1. Poisoned-well displacement (Picher, Hinkley, Flint)
    2. Environmental-stress selective migration (Superfund literature)
    3. Food/subsistence displacement (Grassy Narrows, MN wild rice)
    4. Indigenous compounding displacement (layered colonial + env)
    5. Housing-value collapse and trapped populations
"""

from dataclasses import dataclass, field


@dataclass
class DisplacementAnalog:
    site: str
    pathway: str
    population_before: int
    population_after: int
    departure_fraction: float
    timeframe_years: int
    contaminant: str
    mechanism: str
    source: str
    notes: str = ""


# ══════════════════════════════════════════════════════════════
# PATHWAY 1: POISONED-WELL DISPLACEMENT
# ══════════════════════════════════════════════════════════════

WELL_ANALOGS = [
    DisplacementAnalog(
        site="Picher, Oklahoma (Tar Creek Superfund)",
        pathway="poisoned_well",
        population_before=1640,
        population_after=20,
        departure_fraction=0.988,
        timeframe_years=10,
        contaminant="Lead, zinc, cadmium in groundwater",
        mechanism=(
            "EPA condemned area; federal buyout 1995-2007; "
            "43% of children ages 1-5 had elevated blood lead. "
            "EF4 tornado 2008 completed evacuation. "
            "Disincorporated Sep 1, 2009."
        ),
        source=(
            "US Census 2000 (pop 1,640), 2010 (pop 20); "
            "EPA Tar Creek Superfund site profile; "
            "Picher, Oklahoma Wikipedia (census history)"
        ),
        notes="98.8% departure WITH federal buyout. Upper bound.",
    ),
    DisplacementAnalog(
        site="Hinkley, California (PG&E chromium-6)",
        pathway="poisoned_well",
        population_before=1900,
        population_after=1300,
        departure_fraction=0.316,
        timeframe_years=4,
        contaminant="Hexavalent chromium at 2500x safety standard",
        mechanism=(
            "PG&E bought 2/3 of properties and razed houses at "
            "2-3/week. No formal evacuation order — corporate "
            "buyout drove departure. Described as 'slowly becoming "
            "a ghost town' by NYT 2016."
        ),
        source=(
            "Grist 2019 ('Erin Brockovich town is still toxic'); "
            "EHN 2024 (PG&E cleanup drags on); "
            "pop 1,900 early 2012, est 1,300 by 2016"
        ),
        notes="~32% departure with corporate buyout, ongoing.",
    ),
    DisplacementAnalog(
        site="Flint, Michigan (lead in water)",
        pathway="poisoned_well",
        population_before=102434,
        population_after=81252,
        departure_fraction=0.207,
        timeframe_years=10,
        contaminant="Lead from corroded pipes; no corrosion control",
        mechanism=(
            "State emergency manager switched water source 2014. "
            "~100,000 exposed to elevated lead. White residents "
            "3x more likely to leave than Black residents. Nearly "
            "half of surveyed residents considering moving."
        ),
        source=(
            "US Census 2010 (102,434), 2020 (81,252); "
            "Detroit News 2021; ScienceDirect 2025 "
            "(racial differences in residential mobility)"
        ),
        notes=(
            "21% departure WITHOUT buyout; confounded by "
            "pre-existing economic decline. Lower bound for "
            "water-contamination-only effect."
        ),
    ),
]


# ══════════════════════════════════════════════════════════════
# PATHWAY 2: ENVIRONMENTAL-STRESS SELECTIVE MIGRATION
# ══════════════════════════════════════════════════════════════

ENVIRONMENTAL_STRESS_ANALOGS = [
    DisplacementAnalog(
        site="US Superfund sites (57-site study)",
        pathway="environmental_stress",
        population_before=0,
        population_after=0,
        departure_fraction=0.0,
        timeframe_years=0,
        contaminant="Mixed (site-dependent)",
        mechanism=(
            "Near Superfund sites: declining concentrations of "
            "children under 6, married couples with children, and "
            "higher-income households. Increasing concentrations "
            "of seniors and people stuck in same dwelling — "
            "housing rendered difficult to sell."
        ),
        source=(
            "ScienceDirect 2020 (spatial hedonic approach); "
            "NCSU cenrep working paper (disentangling property "
            "value impacts); Oregon 2016 (evidence of "
            "environmental migration)"
        ),
        notes=(
            "Selective, not total: mobile populations leave, "
            "immobile populations are trapped. Property values "
            "drop 2-6% on discovery, up to 15% at 2x the "
            "regulatory standard. Cleanup raises values 14.7%."
        ),
    ),
]

PROPERTY_VALUE_EFFECTS = {
    "discovery_drop_pct":           (2.0, 6.0),
    "severe_contamination_drop_pct": (6.0, 15.0),
    "post_cleanup_recovery_pct":    14.7,
    "source": (
        "ScienceDirect 2020; EPA working paper on "
        "groundwater contamination and agricultural runoff"
    ),
}


# ══════════════════════════════════════════════════════════════
# PATHWAY 3: FOOD / SUBSISTENCE DISPLACEMENT
# ══════════════════════════════════════════════════════════════

FOOD_ANALOGS = [
    DisplacementAnalog(
        site="Grassy Narrows First Nation, Ontario",
        pathway="food_subsistence",
        population_before=0,
        population_after=0,
        departure_fraction=0.0,
        timeframe_years=60,
        contaminant="Mercury (9,000-11,000 kg from Dryden Mill 1962-1970)",
        mechanism=(
            "90% of community members have mercury poisoning "
            "(2022 study). Walleye — dietary mainstay and cultural "
            "keystone — highest Hg in Ontario. Fishing ban "
            "destroyed economic and cultural base. Government "
            "relocated community in 1960s (colonial compounding). "
            "Community chose to stay and resist rather than "
            "disperse — displacement expressed as health collapse "
            "and cultural disruption rather than out-migration."
        ),
        source=(
            "Lancet Planetary Health 2020 (premature mortality); "
            "McGill Sociological Review (mercury poisoning and "
            "colonialism); Wikipedia (mercury contamination in "
            "Grassy Narrows); Cultural Survival Quarterly"
        ),
        notes=(
            "Critical case: indigenous communities may NOT "
            "out-migrate even under extreme contamination because "
            "land is identity, not property. Displacement is "
            "expressed as health and cultural loss, not departure. "
            "This means the BWCA model's migration_cap of 0.65 "
            "may OVERESTIMATE departure for tribal populations "
            "while UNDERESTIMATING total harm."
        ),
    ),
    DisplacementAnalog(
        site="Minnesota wild rice waters (55 impaired, 2024)",
        pathway="food_subsistence",
        population_before=0,
        population_after=0,
        departure_fraction=0.0,
        timeframe_years=0,
        contaminant="Sulfate from mining and industrial discharge",
        mechanism=(
            "MN adopted 10 mg/L wild rice sulfate standard 1973. "
            "MPCA listed 55 wild rice waters impaired by sulfate "
            "in 2024. Sulfate -> sulfide via bacterial reduction "
            "-> toxic to Zizania palustris. Wild rice specifically "
            "protected in 1837 Treaty. 1854 Treaty Authority "
            "issued own report; MCT declined state task force "
            "participation citing sovereignty."
        ),
        source=(
            "MN PCA (protecting wild rice waters); "
            "CBS Minnesota 2024 (State of Water); "
            "Clean Water Action (manoomin protection); "
            "MN Indian Affairs Resolution 02202024_04"
        ),
        notes=(
            "Direct analog to BWCA model: sulfate from copper- "
            "nickel mining is the specific threat. 10 mg/L "
            "threshold is the same value used in the model's "
            "SULFATE_TOXIC_MG_L constant."
        ),
    ),
]

INDIGENOUS_FOOD_INSECURITY = {
    "first_nations_on_reserve_range_pct": (48, 100),
    "contaminated_sites_on_reserves_pct": 29.0,
    "reserves_land_mass_pct": 0.5,
    "source": (
        "PMC 2021 (First Nations food insecurity, 92 communities); "
        "medRxiv 2022 / Wiley 2024 (contaminated sites scoping "
        "review); BMC Public Health 2023 (colonization impacts on "
        "food systems)"
    ),
    "key_finding": (
        "29% of federal contaminated sites sit on 0.5% of the "
        "land mass. Food insecurity 48-100% on affected reserves. "
        "Environmental contamination and government food-harvest "
        "restrictions compound to destroy subsistence base."
    ),
}


# ══════════════════════════════════════════════════════════════
# PATHWAY 4: INDIGENOUS COMPOUNDING DISPLACEMENT
# ══════════════════════════════════════════════════════════════

INDIGENOUS_COMPOUNDING = {
    "description": (
        "Indigenous displacement from environmental contamination "
        "is NEVER a single-cause event. It layers on top of forced "
        "relocation (reserve system, residential schools), economic "
        "exclusion, and ongoing jurisdictional conflicts. Each layer "
        "reduces capacity to resist the next."
    ),
    "layer_sequence": [
        "1. Forced relocation to reserves (19th-20th century)",
        "2. Residential schools / cultural disruption",
        "3. Environmental contamination of subsistence base",
        "4. Government fishing/harvesting bans 'for protection'",
        "5. Economic collapse from loss of subsistence + tourism",
        "6. Health crisis from contamination exposure",
        "7. Youth out-migration from lack of economic base",
    ],
    "bwca_specific": (
        "Bois Forte (3,400), Grand Portage (1,100), Fond du Lac "
        "(4,200) hold 1854 Treaty usufructuary rights to harvest "
        "manoomin in the BWCA watershed. Sulfate contamination "
        "above 10 mg/L destroys the resource the treaty protects. "
        "This is not property damage — it is a treaty violation "
        "and a destruction of identity-level cultural practice "
        "(see calibration/architecture_mismatch.py: identity_level "
        "encoding cannot be replaced by compensation)."
    ),
    "source": (
        "1854 Treaty Authority; MN Indian Affairs; "
        "Lancet Planetary Health 2020 (Grassy Narrows mortality); "
        "Cultural Survival Quarterly (Grassy Narrows 60-yr legacy)"
    ),
}


# ══════════════════════════════════════════════════════════════
# PATHWAY 5: HOUSING-VALUE COLLAPSE AND TRAPPED POPULATIONS
# ══════════════════════════════════════════════════════════════

HOUSING_ANALOGS = {
    "picher_complete_collapse": {
        "description": (
            "Picher: property values -> $0 (federal buyout at "
            "appraised value pre-contamination). 98.8% departure. "
            "Those who stayed had no economic alternative."
        ),
        "departure_frac": 0.988,
    },
    "flint_trapped_population": {
        "description": (
            "Flint: many residents CANNOT leave — homes unsellable "
            "at any price. Poverty rate 38%, median household "
            "income $28,834. Black residents 3x less likely to "
            "leave than white residents. Environmental contamination "
            "creates a trapped population that bears the full cost."
        ),
        "trapped_frac_estimate": 0.40,
    },
    "superfund_general": {
        "description": (
            "Near Superfund sites: increasing concentration of "
            "seniors, people in same dwelling, lower-income "
            "households. Mobile populations leave; immobile "
            "populations absorb the externality."
        ),
    },
    "source": (
        "US Census (Picher, Flint); ScienceDirect 2020; "
        "APM Reports 2021 (public housing near Superfund sites)"
    ),
}


# ══════════════════════════════════════════════════════════════
# PARAMETER DERIVATION — CONNECTING ANALOGS TO MODEL CONSTANTS
# ══════════════════════════════════════════════════════════════

PARAMETER_DERIVATION = {
    "MIGRATION_WEIGHT_WELLS": {
        "value": 0.7,
        "derivation": (
            "Well contamination is the dominant displacement "
            "driver in every analog. Picher (98.8% departure) "
            "was driven entirely by well/groundwater contamination "
            "+ buyout. Flint (21%) was driven by water "
            "contamination without buyout. Grassy Narrows shows "
            "food loss alone does NOT drive out-migration from "
            "indigenous communities — it drives health and "
            "cultural collapse instead. Weight of 0.7 reflects "
            "wells as primary driver; 0.3 for food/subsistence "
            "reflects that food loss contributes to pressure but "
            "is not sufficient alone for departure."
        ),
        "analogs": ["Picher", "Flint", "Hinkley", "Grassy Narrows"],
    },
    "MIGRATION_WEIGHT_MANOOMIN": {
        "value": 0.3,
        "derivation": (
            "Complement of well weight. Food/subsistence loss "
            "contributes 30% of migration pressure. Supported by "
            "Grassy Narrows (community stayed despite 90% mercury "
            "poisoning — food loss alone insufficient for "
            "departure) and MN wild rice impairment (55 waters "
            "impaired, communities persist but under stress)."
        ),
        "analogs": ["Grassy Narrows", "MN wild rice 55 waters"],
    },
    "MIGRATION_CAP_FRAC": {
        "value": 0.65,
        "derivation": (
            "Between Flint lower bound (21% without buyout, "
            "confounded by poverty trapping) and Picher upper "
            "bound (98.8% with federal buyout). 65% represents "
            "the fraction that CAN leave without federal buyout "
            "assistance — those with economic mobility. The "
            "remaining 35% are trapped by poverty, age, "
            "disability, or (for tribal members) identity-level "
            "connection to place. Hinkley (32% over 4 years with "
            "corporate buyout, ongoing) is consistent with this "
            "range for a mid-process displacement."
        ),
        "analogs": ["Picher", "Flint", "Hinkley"],
        "sensitivity_note": (
            "This is the most uncertain parameter. With federal "
            "buyout: 0.95+. Without buyout, low-income community: "
            "0.20-0.40. Mid-income without buyout: 0.50-0.70. "
            "The BWCA communities (Ely, Babbitt, Tower, Winton) "
            "are low-to-mid income with 84% well-dependent."
        ),
    },
    "WELL_CONTAMINATION_LAG_YR": {
        "value": 2,
        "derivation": (
            "Site-specific to BWCA geology: water table at 2.1 m, "
            "glacial till only 0.8 m thick, Canadian Shield "
            "granite with fracture flow. Contaminant transport "
            "is FAST in this geology — surface AMD reaches "
            "shallow wells in 1-3 years. 2 years is reasonable "
            "to conservative for this specific substrate. Would "
            "be 5-10 years in deeper alluvial aquifers."
        ),
        "analogs": ["BWCA-specific geology (constants.py)"],
    },
    "WELL_CONTAMINATION_THRESHOLD_MG_L": {
        "value": 40.0,
        "derivation": (
            "Sulfate at which shallow wells become unusable. "
            "EPA secondary MCL for sulfate is 250 mg/L (taste), "
            "but shallow wells in shield geology concentrate "
            "sulfate in the aquifer. 40 mg/L at the surface "
            "implies higher concentrations at the well intake "
            "due to residence time and evaporative concentration "
            "in the shallow aquifer. Conservative — failure may "
            "occur at lower surface concentrations."
        ),
        "analogs": ["EPA secondary MCL", "Shield hydrogeology"],
    },
}


# ══════════════════════════════════════════════════════════════
# SUMMARY TABLE
# ══════════════════════════════════════════════════════════════

def print_summary():
    print("=" * 70)
    print("  DISPLACEMENT ANALOGS — SOURCED PARAMETERS")
    print("=" * 70)

    print("\nPATHWAY 1: POISONED-WELL DISPLACEMENT")
    print("-" * 70)
    for a in WELL_ANALOGS:
        print(f"  {a.site}")
        print(f"    pop {a.population_before:,} -> {a.population_after:,}"
              f"  ({a.departure_fraction:.1%} departure"
              f" over {a.timeframe_years} yr)")
        print(f"    mechanism: {a.mechanism[:80]}...")
        print()

    print("PATHWAY 3: FOOD / SUBSISTENCE DISPLACEMENT")
    print("-" * 70)
    for a in FOOD_ANALOGS:
        print(f"  {a.site}")
        print(f"    {a.mechanism[:80]}...")
        print()

    print("PARAMETER DERIVATION")
    print("-" * 70)
    for name, info in PARAMETER_DERIVATION.items():
        print(f"  {name} = {info['value']}")
        print(f"    analogs: {', '.join(info['analogs'])}")
        print()


if __name__ == "__main__":
    print_summary()
