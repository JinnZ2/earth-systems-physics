# energy_return.py
# earth-systems-physics / extraction_dynamics
# CC0 — No Rights Reserved
#
# The energetic constraint that ecological consumers obey and subsidised
# extractors do not.
#
#   ecological predator :  e*f(N) >= m        net energy from prey must
#                                             cover the cost of living
#   industrial fishery  :  EROI < 1           in most fleets: more fuel
#                                             energy in than food energy out
#
# A real predator with e*f(N) < m goes extinct. An extractor with
# e*f(N) < m persists on fossil S. That is the formal statement of "not
# coupled to the ecosystem it consumes" — the same statement as the
# subsidy term in consumer_resource.py, written in energy units.
#
# ONE INTENSIVE VARIABLE FOR BOTH BRANCHES
# ----------------------------------------
# %PPR (primary production required, Pauly & Christensen 1995) and HANPP
# (human appropriation of net primary production, Haberl et al. 2007)
# are the same measurement taken in the sea and on land. Both are the
# fraction of photosynthetic production routed to one consumer. A
# fishery case and a soil case become comparable the moment they are
# both expressed this way — no narrative bridge required, just a common
# denominator.
#
# Standard library only.

from typing import Dict, Optional, Sequence

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

TROPHIC_TRANSFER_EFFICIENCY = 0.10   # ~10% per trophic level (Lindeman)
WET_WEIGHT_TO_CARBON = 9.0           # t wet weight per t C (Pauly &
                                     # Christensen 1995 conversion)

# Global net primary production, Pg C/yr. Order-of-magnitude reference
# values for normalising PPR and HANPP; substitute regional NPP when
# working at less than global scale.
NPP_TERRESTRIAL_PgC_yr = 56.0        # Field et al. 1998
NPP_MARINE_PgC_yr      = 48.5        # Field et al. 1998
NPP_GLOBAL_PgC_yr      = NPP_TERRESTRIAL_PgC_yr + NPP_MARINE_PgC_yr

# Haberl et al. 2007: ~23.8% of potential terrestrial NPP appropriated.
HANPP_TERRESTRIAL_FRACTION_2000 = 0.238

# Energy content references
ENERGY_MJ_PER_KG_FISH_EDIBLE = 4.5   # MJ/kg wet edible fish (lean-fatty range)
ENERGY_MJ_PER_L_DIESEL       = 38.6  # MJ/L marine gas oil


# ─────────────────────────────────────────────
# THE PREDATOR CONSTRAINT
# ─────────────────────────────────────────────


def predator_persistence(e: float, f_N: float, m: float) -> Dict[str, object]:
    """
    Can a consumer persist on this resource alone?

        persist  <=>  e * f(N) >= m

    e   : conversion efficiency (consumer produced per resource consumed)
    f_N : per-capita intake at the current resource density
    m   : per-capita loss rate (mortality + maintenance)
    returns: dict with the net rate and the verdict
    """
    gain = e * f_N
    return {
        "gain":        gain,
        "cost":        m,
        "net":         gain - m,
        "persists":    gain >= m,
        "deficit":     max(0.0, m - gain),
        "subsidy_required_per_consumer": max(0.0, m - gain),
        "note": ("coupled: consumer is viable on this resource"
                 if gain >= m else
                 "NOT viable on this resource — persistence at this density "
                 "requires an exogenous subsidy of at least the deficit"),
    }


def subsidy_required(e: float, f_N: float, m: float, P: float) -> float:
    """
    Total exogenous subsidy S needed to hold a consumer population P at
    a resource density where it is not self-supporting.

        S >= (m - e*f(N)) * P

    This converts the abstract S of consumer_resource.Params into a
    quantity with an invoice attached: fuel subsidies, access
    agreements, vessel-construction support, or an alternate prey base.
    """
    return max(0.0, (m - e * f_N) * P)


# ─────────────────────────────────────────────
# ENERGY RETURN ON INVESTMENT
# ─────────────────────────────────────────────


def eroi(energy_out_MJ: float, energy_in_MJ: float) -> Dict[str, object]:
    """
    Energy Return On Investment.

    < 1  : the activity is an energy SINK. It can only continue while
           something else supplies the difference.
    1-3  : marginal; cannot support the infrastructure that produces it
    > 3  : conventionally taken as the floor for a self-supporting
           industrial energy source

    Reported with the ratio, not a verdict on whether the activity is
    worthwhile — food is worth producing at EROI < 1 if the input energy
    is available. The point of the number is that the availability of
    that input energy, not the resource, is what the activity depends on.
    """
    if energy_in_MJ <= 0:
        return {"eroi": float("inf"), "energy_sink": False,
                "self_supporting": True,
                "note": "no energy input recorded"}
    ratio = energy_out_MJ / energy_in_MJ
    return {
        "eroi":            ratio,
        "energy_out_MJ":   energy_out_MJ,
        "energy_in_MJ":    energy_in_MJ,
        "energy_sink":     ratio < 1.0,
        "self_supporting": ratio >= 3.0,
        "note": ("energy sink: output cannot power the next cycle; "
                 "continuation depends on an external energy supply"
                 if ratio < 1.0 else
                 "positive but below the ~3:1 floor for self-support"
                 if ratio < 3.0 else
                 "self-supporting at the conventional threshold"),
    }


def fishery_eroi(catch_t: float, fuel_L: float,
                 edible_fraction: float = 0.5,
                 energy_MJ_per_kg: float = ENERGY_MJ_PER_KG_FISH_EDIBLE
                 ) -> Dict[str, object]:
    """
    Fuel-in versus edible-energy-out for a fishery.

    catch_t         : landed catch (tonnes wet weight)
    fuel_L          : fuel consumed (litres)
    edible_fraction : fraction of landed wet weight that is eaten
    returns: eroi() dict plus fuel intensity in L per tonne landed
    """
    out_MJ = catch_t * 1000.0 * edible_fraction * energy_MJ_per_kg
    in_MJ = fuel_L * ENERGY_MJ_PER_L_DIESEL
    r = eroi(out_MJ, in_MJ)
    r["fuel_L_per_t_landed"] = fuel_L / catch_t if catch_t > 0 else float("inf")
    return r


# ─────────────────────────────────────────────
# PRIMARY PRODUCTION REQUIRED  (%PPR)
# ─────────────────────────────────────────────


def primary_production_required(catch_t: float, trophic_level: float,
                                transfer_efficiency: float =
                                TROPHIC_TRANSFER_EFFICIENCY,
                                wet_to_carbon: float = WET_WEIGHT_TO_CARBON
                                ) -> float:
    """
    Primary production required to sustain a catch (Pauly & Christensen
    1995).

        PPR = (catch / wet_to_carbon) * (1 / TE) ** (TL - 1)

    catch_t             : catch, tonnes wet weight
    trophic_level       : mean trophic level of the catch
    transfer_efficiency : energy transferred per trophic step (~0.10)
    returns: tonnes of carbon of primary production per unit time
    """
    if trophic_level < 1.0:
        raise ValueError("trophic level must be >= 1")
    carbon_t = catch_t / wet_to_carbon
    return carbon_t * (1.0 / transfer_efficiency) ** (trophic_level - 1.0)


def ppr_fraction(catch_t: float, trophic_level: float,
                 npp_tC: float, **kwargs) -> Dict[str, float]:
    """
    %PPR — the share of an ecosystem's primary production appropriated
    by a catch. The intensive variable that makes fisheries comparable
    across systems and comparable to HANPP on land.
    """
    ppr = primary_production_required(catch_t, trophic_level, **kwargs)
    frac = ppr / npp_tC if npp_tC > 0 else float("inf")
    return {
        "PPR_tC":        ppr,
        "NPP_tC":        npp_tC,
        "PPR_fraction":  frac,
        "PPR_percent":   100.0 * frac,
        "trophic_level": trophic_level,
    }


def hanpp_fraction(appropriated_NPP_tC: float,
                   potential_NPP_tC: float) -> Dict[str, float]:
    """
    HANPP — human appropriation of net primary production, as a fraction
    of the NPP the system would produce without that appropriation.

    Same quantity as %PPR, measured on land. Reporting both in this unit
    is what lets a fishery case and a soil case be added rather than
    merely compared by analogy.
    """
    if potential_NPP_tC <= 0:
        raise ValueError("potential NPP must be positive")
    frac = appropriated_NPP_tC / potential_NPP_tC
    return {
        "HANPP_tC":       appropriated_NPP_tC,
        "potential_NPP_tC": potential_NPP_tC,
        "HANPP_fraction": frac,
        "HANPP_percent":  100.0 * frac,
        "global_reference_2000": HANPP_TERRESTRIAL_FRACTION_2000,
    }


def trophic_level_energy(trophic_level: float,
                         transfer_efficiency: float =
                         TROPHIC_TRANSFER_EFFICIENCY) -> float:
    """
    Fraction of primary production energy reaching a trophic level.

    TL 2 -> 0.1, TL 3 -> 0.01, TL 4 -> 0.001. Each step up multiplies
    the primary production required by roughly ten. This is why fishing
    down the food web looks like an efficiency gain in tonnage and is a
    tenfold change in production footprint per step.
    """
    return transfer_efficiency ** (trophic_level - 1.0)


if __name__ == "__main__":
    print("THE PREDATOR CONSTRAINT:  e*f(N) >= m")
    print("=" * 70)
    for label, e, f_N, m in (("wolf at high prey density",  0.4, 0.8, 0.2),
                             ("wolf at low prey density",   0.4, 0.3, 0.2),
                             ("wolf at collapsed prey",     0.4, 0.05, 0.2)):
        r = predator_persistence(e, f_N, m)
        print(f"  {label:28s} net={r['net']:+7.4f}  "
              f"persists={str(r['persists']):5s}  "
              f"deficit={r['deficit']:.4f}")
    print("\n  A predator failing this inequality goes extinct. An")
    print("  extractor failing it buys fuel.")

    print("\n\nFISHERY EROI")
    print("=" * 70)
    for label, catch, fuel in (("efficient small pelagic", 1000.0, 100_000.0),
                               ("mixed demersal trawl",    1000.0, 600_000.0),
                               ("distant-water high-value", 1000.0, 2_000_000.0)):
        r = fishery_eroi(catch, fuel)
        print(f"  {label:26s} EROI={r['eroi']:6.3f}  "
              f"{r['fuel_L_per_t_landed']:8.0f} L/t  "
              f"sink={r['energy_sink']}")

    print("\n\nPRIMARY PRODUCTION REQUIRED")
    print("=" * 70)
    print(f"  {'trophic level':>14} {'energy reaching it':>20} "
          f"{'PPR per t caught':>18}")
    for TL in (2.0, 3.0, 3.5, 4.0, 4.5):
        print(f"  {TL:14.1f} {trophic_level_energy(TL):20.5f} "
              f"{primary_production_required(1.0, TL):18.1f}")
    print("\n  One tonne of a TL 4.5 predator costs ~10x the primary")
    print("  production of one tonne at TL 3.5. Tonnage is not the unit")
    print("  the ecosystem is paying in.")

    print("\n\nONE UNIT, TWO BRANCHES")
    print("=" * 70)
    sea = ppr_fraction(80e6, 3.2, NPP_MARINE_PgC_yr * 1e9)
    land = hanpp_fraction(HANPP_TERRESTRIAL_FRACTION_2000
                          * NPP_TERRESTRIAL_PgC_yr * 1e9,
                          NPP_TERRESTRIAL_PgC_yr * 1e9)
    print(f"  marine %PPR at 80 Mt catch, TL 3.2 : "
          f"{sea['PPR_percent']:.2f}% of marine NPP")
    print(f"  terrestrial HANPP (Haberl 2007)    : "
          f"{land['HANPP_percent']:.2f}% of potential NPP")
    print("  same intensive variable, two ecosystems, directly addable")
