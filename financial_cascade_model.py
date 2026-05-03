"""
financial_cascade_model.py

Coupled financial cascade model for industrial monoculture
agriculture under pollinator collapse.

PURPOSE
    Actuarial models for agricultural insurance treat crop failure,
    pollinator decline, soil degradation, and equipment debt as
    independent variables. They are not. They are coupled, with
    positive feedback loops that produce non-linear cascade failure
    when any single variable crosses threshold.

    This module models the coupling explicitly. It demonstrates that
    the current insurance + subsidy + equipment-financing structure
    is mathematically unsustainable on the actual physical timeline,
    not the political timeline.

CORE COUPLING LOOPS
    Loop 1: pesticide use -> pollinator decline -> yield decline
            -> revenue decline -> need more acreage -> more pesticide

    Loop 2: equipment debt -> need scale to service debt ->
            monoculture -> soil degradation + pollinator loss ->
            yield decline -> need more debt to maintain scale

    Loop 3: insurance bailout -> moral hazard -> continued
            unsustainable practice -> larger eventual claim ->
            insurance pool collapse

    Loop 4: subsidy structure -> rewards production volume ->
            rewards scale and chemical use -> rewards substrate
            destruction

    These loops do not balance. They compound. The system is
    mining its own substrate.

Status: CC0. Stdlib only. ASCII only.
"""

from dataclasses import dataclass
from typing import List, Dict


# ─────────────────────────────────────────────
# STATE PRIMITIVES
# ─────────────────────────────────────────────

@dataclass
class FarmState:
    year: int
    acreage: int
    yield_per_acre: float       # bushels/acre, normalized
    pesticide_load: float       # 1.0 = baseline, increases over time
    pollinator_health: float    # 1.0 = healthy, 0.0 = collapsed
    soil_health: float          # 1.0 = healthy, 0.0 = depleted
    equipment_debt: float       # dollars
    annual_revenue: float
    annual_subsidy: float
    insurance_payout: float
    cumulative_loss: float


@dataclass
class SystemState:
    year: int
    insurance_pool_balance: float
    federal_bailout_paid: float
    cumulative_pollinator_loss: float   # 0.0 to 1.0
    cumulative_soil_loss: float         # 0.0 to 1.0
    food_supply_index: float            # 1.0 = baseline, < 1.0 = decline
    farms_failed: int


# ─────────────────────────────────────────────
# COUPLING DYNAMICS
# ─────────────────────────────────────────────

def yield_from_substrate(pollinator_health: float,
                         soil_health: float,
                         pesticide_load: float) -> float:
    """
    Yield is a function of the substrate. Pesticide gives short-term
    boost but degrades pollinator and soil. Coupling is multiplicative.
    """
    # Pesticide short-term boost flattens, then becomes net negative
    pesticide_factor = max(0.5, 1.2 - 0.2 * pesticide_load)
    return pollinator_health * soil_health * pesticide_factor


def pollinator_decline(current_health: float,
                       pesticide_load: float) -> float:
    """Pollinator population health degrades with pesticide load."""
    decline = 0.05 + 0.08 * pesticide_load
    return max(0.0, current_health - decline)


def soil_decline(current_health: float,
                 pesticide_load: float,
                 monoculture_pressure: float = 1.0) -> float:
    """Soil health degrades with pesticide load and monoculture intensity."""
    decline = 0.03 + 0.04 * pesticide_load * monoculture_pressure
    return max(0.0, current_health - decline)


def revenue_calculation(acreage: int,
                        yield_per_acre: float,
                        price_per_bushel: float = 4.0) -> float:
    """Annual gross revenue from production."""
    return acreage * yield_per_acre * 50.0 * price_per_bushel


def equipment_debt_servicing(debt: float,
                             interest_rate: float = 0.06) -> float:
    """Annual debt service cost."""
    return debt * interest_rate


# ─────────────────────────────────────────────
# CASCADE SIMULATION
# ─────────────────────────────────────────────

def simulate_farm_cascade(years: int = 15,
                          starting_acreage: int = 1000,
                          starting_debt: float = 800_000.0,
                          subsidy_per_acre: float = 50.0) -> Dict:
    """
    Simulate a representative farm under current incentive structure.
    Track cascade across coupled variables.
    """
    states: List[FarmState] = []
    pollinator = 1.0
    soil = 1.0
    pesticide = 1.0
    debt = starting_debt
    cumulative_loss = 0.0
    farm_failed_year = None

    for year in range(years):
        yield_per_acre = yield_from_substrate(pollinator, soil, pesticide)
        revenue = revenue_calculation(starting_acreage, yield_per_acre)
        subsidy = subsidy_per_acre * starting_acreage
        debt_service = equipment_debt_servicing(debt)
        operating_cost = starting_acreage * 200.0 * pesticide
        net = revenue + subsidy - debt_service - operating_cost
        if net < 0:
            cumulative_loss += abs(net)
            insurance_payout = min(abs(net) * 0.6, 100_000.0)
            cumulative_loss -= insurance_payout
        else:
            insurance_payout = 0.0

        states.append(FarmState(
            year=year,
            acreage=starting_acreage,
            yield_per_acre=round(yield_per_acre, 3),
            pesticide_load=round(pesticide, 2),
            pollinator_health=round(pollinator, 3),
            soil_health=round(soil, 3),
            equipment_debt=debt,
            annual_revenue=round(revenue, 0),
            annual_subsidy=subsidy,
            insurance_payout=round(insurance_payout, 0),
            cumulative_loss=round(cumulative_loss, 0),
        ))

        # Year-end updates: substrate degrades, debt grows if losing
        pollinator = pollinator_decline(pollinator, pesticide)
        soil = soil_decline(soil, pesticide)
        # Farmer responds to declining yield by increasing pesticide
        pesticide = min(3.0, pesticide + 0.1)
        # Debt grows if operating at loss
        if net < 0:
            debt += abs(net) * 0.5

        if cumulative_loss > 500_000 and farm_failed_year is None:
            farm_failed_year = year + 1

    return {
        "states":                   states,
        "farm_failed_year":         farm_failed_year,
        "final_pollinator_health":  states[-1].pollinator_health,
        "final_soil_health":        states[-1].soil_health,
        "final_yield":              states[-1].yield_per_acre,
        "final_debt":               states[-1].equipment_debt,
        "cumulative_loss":          states[-1].cumulative_loss,
    }


def aggregate_system_cascade(num_farms: int = 1000,
                             years: int = 15) -> List[SystemState]:
    """
    Aggregate impact across many farms. Insurance pool tracks
    cumulative payouts. Federal bailout represents externalization.
    """
    insurance_pool = 50_000_000.0    # initial pool
    federal_bailout = 0.0
    pollinator_loss = 0.0
    soil_loss = 0.0
    farms_failed = 0
    timeline: List[SystemState] = []

    sample = simulate_farm_cascade(years=years)
    states = sample["states"]
    for year_idx, farm_state in enumerate(states):
        annual_payout_per_farm = farm_state.insurance_payout
        total_payout = annual_payout_per_farm * num_farms
        insurance_pool -= total_payout
        if insurance_pool < 0:
            federal_bailout += abs(insurance_pool)
            insurance_pool = 10_000_000.0   # bailed out, repeats
        pollinator_loss = 1.0 - farm_state.pollinator_health
        soil_loss = 1.0 - farm_state.soil_health
        food_supply = farm_state.yield_per_acre  # normalized
        if (sample["farm_failed_year"]
                and year_idx >= sample["farm_failed_year"]):
            farms_failed = num_farms

        timeline.append(SystemState(
            year=year_idx,
            insurance_pool_balance=round(insurance_pool, 0),
            federal_bailout_paid=round(federal_bailout, 0),
            cumulative_pollinator_loss=round(pollinator_loss, 3),
            cumulative_soil_loss=round(soil_loss, 3),
            food_supply_index=round(food_supply, 3),
            farms_failed=farms_failed,
        ))
    return timeline


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("FINANCIAL CASCADE MODEL")
    print("=" * 60)
    print("\nSingle representative farm, 15 years:")
    farm = simulate_farm_cascade(years=15)
    print(f"  failed in year: {farm['farm_failed_year']}")
    print(f"  final pollinator health: {farm['final_pollinator_health']}")
    print(f"  final soil health: {farm['final_soil_health']}")
    print(f"  final yield: {farm['final_yield']}")
    print(f"  final debt: ${farm['final_debt']:,.0f}")
    print(f"  cumulative loss: ${farm['cumulative_loss']:,.0f}")
    print()
    print("Annual trajectory (selected years):")
    for state in farm['states'][::3]:
        print(f"  year {state.year}: yield={state.yield_per_acre} "
              f"poll={state.pollinator_health} soil={state.soil_health} "
              f"debt=${state.equipment_debt:,.0f}")
    print()
    print("=" * 60)
    print("AGGREGATE (1,000 representative farms, 15 years):")
    system = aggregate_system_cascade(num_farms=1000, years=15)
    final = system[-1]
    print(f"  insurance pool balance: ${final.insurance_pool_balance:,.0f}")
    print(f"  federal bailout cumulative: ${final.federal_bailout_paid:,.0f}")
    print(f"  pollinator loss: {final.cumulative_pollinator_loss * 100:.1f}%")
    print(f"  soil loss: {final.cumulative_soil_loss * 100:.1f}%")
    print(f"  food supply index: {final.food_supply_index}")
    print(f"  farms failed: {final.farms_failed:,}")
    print()
    print("CONCLUSION:")
    print("  The current system requires repeated federal bailouts")
    print("  to maintain insurance pool solvency. Pollinator and soil")
    print("  loss compound. Food supply degrades. The cascade is")
    print("  externalizing all losses to taxpayer and substrate, while")
    print("  internalizing all profits. This is not actuarially sound.")
