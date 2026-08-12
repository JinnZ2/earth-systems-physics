# domain_mapping.py
# earth-systems-physics / extraction_dynamics
# CC0 — No Rights Reserved
#
# Mapping real systems onto the consumer-resource variables — and a
# standing refusal to do it where the variables have no referent.
#
# WHAT MAKES A MAPPING VALID
# --------------------------
# The consumer-resource equations are not a metaphor that can be laid
# over anything with a rise and a fall. They require, at minimum:
#
#   1. a CONSERVED STOCK N with a unit that can be measured twice
#   2. a RECRUITMENT term with an estimable rate, or a defensible r = 0
#   3. a CONSUMPTION flux in the same unit per unit time as the stock
#   4. a CAPACITY K derivable from something physical, not chosen
#   5. an identifiable SUBSIDY channel S, or a demonstration that none
#      exists
#
# A domain that supplies all five gets a mapping. A domain that supplies
# fewer gets an entry in REFUSED_MAPPINGS with the missing element
# named. This is not a claim that the refused domains are unimportant,
# unreal, or unstudiable. It is a claim about THIS tool: applying these
# equations to a stock with no unit produces numbers that cannot be
# checked, and numbers that cannot be checked are worse than no numbers,
# because they inherit the authority of arithmetic without earning it.
#
# The refusal list is therefore part of the specification, not an
# apology for an incomplete one.
#
# Standard library only.

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────
# VALID MAPPINGS
# ─────────────────────────────────────────────


@dataclass(frozen=True)
class DomainMapping:
    """
    One domain expressed in consumer-resource variables.

    stock          : what N is, with its unit
    recruitment    : what r*N*(1-N/K) is, with its unit, or 'none'
    consumption    : what f(N)*P is
    capacity       : what K is and where it comes from
    subsidy        : the S channel, if any
    measurement    : how the stock is actually observed
    typical_class  : predation / hyperpredation / mining, as usually
                     configured at present
    refuge         : whether a low-density refuge exists and what
                     removes it
    """
    domain:        str
    stock:         str
    recruitment:   str
    consumption:   str
    capacity:      str
    subsidy:       str
    measurement:   str
    typical_class: str
    refuge:        str


MAPPINGS: Dict[str, DomainMapping] = {
    "wild_fishery": DomainMapping(
        domain="wild_fishery",
        stock="spawning stock biomass (tonnes)",
        recruitment="recruits per spawner per year, from a fitted "
                    "stock-recruitment curve (tonnes/yr)",
        consumption="landings + discard mortality (tonnes/yr)",
        capacity="unfished biomass B_0, from assessment or "
                 "pre-exploitation reconstruction (tonnes)",
        subsidy="fuel subsidy, access agreements, vessel construction "
                "support, alternate target species",
        measurement="survey index, CPUE standardised for effort creep, "
                    "age structure",
        typical_class="hyperpredation",
        refuge="Type III search-efficiency refuge; removed by acoustic "
               "detection, aggregation-site prediction, and pooled-fleet "
               "routing",
    ),
    "soil_carbon": DomainMapping(
        domain="soil_carbon",
        stock="soil organic carbon (t C/ha to a stated depth)",
        recruitment="humified carbon input h*C_in (t C/ha/yr)",
        consumption="harvest removal + erosion + accelerated "
                    "mineralisation (t C/ha/yr)",
        capacity="texture-derived saturation capacity (Hassink 1997), "
                 "not a chosen percentage",
        subsidy="industrial N, P, K and fuel substituting for the "
                "nutrient and structural functions of the lost carbon",
        measurement="SOC % with bulk density and depth, repeated on the "
                    "same georeferenced points",
        typical_class="mining",
        refuge="none — soil carbon has no behavioural refuge; the "
               "analogue is physical protection inside aggregates",
    ),
    "groundwater_recharging": DomainMapping(
        domain="groundwater_recharging",
        stock="aquifer storage (km3 or m head)",
        recruitment="natural recharge (km3/yr)",
        consumption="abstraction (km3/yr)",
        capacity="saturated pore volume above the economic lift depth",
        subsidy="energy subsidy for deeper lift; surface-water transfers",
        measurement="water table elevation, GRACE mass anomaly, "
                    "metered abstraction",
        typical_class="hyperpredation",
        refuge="rising pumping cost with depth — removed by subsidised "
               "energy and deeper wells",
    ),
    "groundwater_fossil": DomainMapping(
        domain="groundwater_fossil",
        stock="fossil aquifer storage (km3)",
        recruitment="none — recharge is negligible on human timescales "
                    "(r = 0)",
        consumption="abstraction (km3/yr)",
        capacity="total recoverable storage",
        subsidy="energy for lift",
        measurement="water table decline rate, isotopic age of water",
        typical_class="mining",
        refuge="none",
    ),
    "timber_managed_forest": DomainMapping(
        domain="timber_managed_forest",
        stock="standing merchantable volume (m3/ha)",
        recruitment="net annual increment (m3/ha/yr)",
        consumption="harvest (m3/ha/yr)",
        capacity="site index / maximum standing volume for the site",
        subsidy="road subsidies, fire suppression costs borne publicly, "
                "conversion of old growth as one-time income",
        measurement="forest inventory plots, remote sensing biomass",
        typical_class="predation (when increment-bound) or mining (when "
                      "harvesting old growth against zero increment)",
        refuge="access cost in remote or steep terrain — removed by "
               "road building and helicopter/cable systems",
    ),
    "pollinator_dependent_crop": DomainMapping(
        domain="pollinator_dependent_crop",
        stock="wild pollinator abundance supporting the crop",
        recruitment="pollinator population growth (per year)",
        consumption="mortality from pesticide, habitat loss, and "
                    "pathogen spillover attributable to the cropping "
                    "system",
        capacity="floral and nesting resource availability in the "
                 "landscape",
        subsidy="managed-hive rental substituting for the wild "
                "population, which lets yield persist while the wild "
                "stock declines",
        measurement="pollinator surveys, visitation rates, pollination "
                    "deficit experiments",
        typical_class="hyperpredation",
        refuge="landscape refugia in uncropped habitat — removed by "
               "field-margin elimination",
    ),
    "phosphate_rock": DomainMapping(
        domain="phosphate_rock",
        stock="economically recoverable phosphate reserve (Mt P2O5)",
        recruitment="none on human timescales (r = 0)",
        consumption="extraction (Mt/yr)",
        capacity="reserve base at a stated ore grade and price",
        subsidy="not applicable — extraction is the whole activity",
        measurement="reserve statements, ore grade, production",
        typical_class="mining",
        refuge="none — declining ore grade is a cost gradient, not a "
               "refuge, because it does not restore the stock",
    ),
    "fossil_hydrocarbon": DomainMapping(
        domain="fossil_hydrocarbon",
        stock="recoverable reserves (Gb or Gt)",
        recruitment="none on human timescales (r = 0)",
        consumption="production (Gb/yr)",
        capacity="technically recoverable resource at a stated price and "
                 "EROI floor",
        subsidy="not applicable to the stock; the EROI floor is the "
                "binding constraint",
        measurement="reserve bookings, decline curves, EROI studies",
        typical_class="mining",
        refuge="none",
    ),
    "wild_harvest_terrestrial": DomainMapping(
        domain="wild_harvest_terrestrial",
        stock="population abundance of the harvested species",
        recruitment="births minus natural deaths (individuals/yr)",
        consumption="harvest offtake (individuals/yr)",
        capacity="habitat-limited carrying capacity",
        subsidy="agricultural income supporting hunters regardless of "
                "offtake; market access subsidising long-distance "
                "pursuit",
        measurement="mark-recapture, harvest reporting, transect counts",
        typical_class="predation or hyperpredation depending on whether "
                      "the hunter's livelihood depends on this species",
        refuge="search cost at low density and in inaccessible terrain — "
               "removed by roads, vehicles, and thermal optics",
    ),
}


def get_mapping(domain: str) -> DomainMapping:
    """Look up a mapping, or raise with the refusal reason if refused."""
    key = domain.lower().strip()
    if key in MAPPINGS:
        return MAPPINGS[key]
    if key in REFUSED_MAPPINGS:
        raise ValueError(
            f"'{domain}' is on the refusal list: {REFUSED_MAPPINGS[key]}"
        )
    raise KeyError(
        f"no mapping for '{domain}'. Valid: {sorted(MAPPINGS)}. "
        f"Refused: {sorted(REFUSED_MAPPINGS)}. To add one, supply the "
        f"five requirements listed at the top of this module."
    )


# ─────────────────────────────────────────────
# REFUSED MAPPINGS
# ─────────────────────────────────────────────

# Each entry names the specific missing requirement. "Not measurable"
# is not a verdict on the domain — it is a verdict on running THESE
# equations over it. Several of these domains have perfectly good
# quantitative literatures using models that fit their own subject.
REFUSED_MAPPINGS: Dict[str, str] = {
    "consciousness":
        "no conserved stock with a unit; 'cognitive capacity' has no "
        "measurement that can be taken twice and differenced. Fails "
        "requirement 1.",
    "art":
        "no conserved stock, no recruitment rate, and 'cultural "
        "attention' has no capacity derivable from anything physical. "
        "Fails 1, 2 and 4.",
    "ethics":
        "'moral consistency' is not a stock and has no flux; the "
        "equations would return a trajectory for a quantity that was "
        "never a quantity. Fails 1 and 3.",
    "religion":
        "adherent counts ARE measurable, but the 'resource' (meaning, "
        "cultural capital) has no unit and no capacity, so the pair is "
        "half-specified. Model adherent demography directly if that is "
        "the question. Fails 1 and 4.",
    "philosophy":
        "'explanatory power' has no unit and no conservation law. "
        "Fails 1.",
    "gender_equity":
        "equity is a distributional property of a population, not a "
        "stock that is consumed; treating people or their standing as "
        "a resource being eaten is a category error, not a bold "
        "reframe. Fails 1 and 3.",
    "psychology_population":
        "distress prevalence is measurable but it is a RATE in a "
        "population, not a stock with recruitment and consumption; use "
        "epidemiological models, which already fit this structure. "
        "Fails 2.",
    "language":
        "speaker counts and language counts are measurable, and "
        "language shift models exist — but there is no consumption "
        "FLUX in speaker-units, so the consumer side is undefined. "
        "Fails 3. Use documented language-shift models instead.",
    "governance_trust":
        "'public trust' is an index on [0,1] with no conserved "
        "quantity behind it; indices do not obey mass balance and will "
        "produce arbitrary carrying capacities. Fails 1 and 4.",
    "media_attention":
        "attention-hours are measurable, but the 'stock' being "
        "consumed is not conserved — attention is regenerated daily "
        "and has no capacity that survives measurement. Fails 1 and 4.",
}


def is_refused(domain: str) -> Tuple[bool, Optional[str]]:
    """(refused?, reason). Reason is None when the domain is not listed."""
    key = domain.lower().strip()
    return (key in REFUSED_MAPPINGS, REFUSED_MAPPINGS.get(key))


def requirements_met(stock_has_unit: bool, recruitment_estimable: bool,
                     consumption_flux_same_unit: bool,
                     capacity_derivable: bool,
                     subsidy_identifiable: bool) -> Dict[str, object]:
    """
    Check a proposed new domain against the five requirements.

    Use this before adding a mapping. The output names which
    requirement failed, so the answer to "why won't it model my
    domain" is a specific missing measurement rather than a refusal.
    """
    checks = {
        "1_stock_has_unit":              stock_has_unit,
        "2_recruitment_estimable":       recruitment_estimable,
        "3_consumption_flux_same_unit":  consumption_flux_same_unit,
        "4_capacity_derivable":          capacity_derivable,
        "5_subsidy_identifiable":        subsidy_identifiable,
    }
    failed = [k for k, v in checks.items() if not v]
    return {
        "checks":       checks,
        "mappable":     not failed,
        "failed":       failed,
        "verdict": ("mappable — supply the mapping and the equations apply"
                    if not failed else
                    f"not mappable with these equations; missing {failed}"),
    }


def list_domains() -> Dict[str, List[str]]:
    """Everything this module will and will not map."""
    return {
        "mapped":  sorted(MAPPINGS),
        "refused": sorted(REFUSED_MAPPINGS),
    }


if __name__ == "__main__":
    print("DOMAIN MAPPINGS")
    print("=" * 70)
    for m in MAPPINGS.values():
        print(f"\n{m.domain}")
        print(f"  N      : {m.stock}")
        print(f"  r*N    : {m.recruitment}")
        print(f"  f(N)*P : {m.consumption}")
        print(f"  K      : {m.capacity}")
        print(f"  S      : {m.subsidy}")
        print(f"  class  : {m.typical_class}")
        print(f"  refuge : {m.refuge}")

    print("\n\nREFUSED — AND WHY")
    print("=" * 70)
    for name, reason in sorted(REFUSED_MAPPINGS.items()):
        print(f"\n  {name}")
        print(f"    {reason}")

    print("\n\nCHECKING A PROPOSED DOMAIN")
    print("=" * 70)
    ok = requirements_met(True, True, True, True, True)
    no = requirements_met(False, False, True, False, True)
    print(f"  fully specified : {ok['verdict']}")
    print(f"  index-based     : {no['verdict']}")
