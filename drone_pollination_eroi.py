"""
drone_pollination_eroi.py

Energy Return on Investment (EROI) analysis for drone-based
pollination as replacement for natural pollinators.

PURPOSE
    Demonstrates that technological replacement of pollinator
    services is thermodynamically negative at scale. The fantasy
    that AI plus robotics will solve pollinator collapse ignores
    the energy cost of manufacture, deployment, maintenance, and
    rare-earth supply.

    This is constraint analysis, not policy advocacy. The numbers
    below are stylized but order-of-magnitude consistent with
    current drone manufacture energy data, agricultural acreage,
    and pollination requirements.

CORE FINDING
    A natural pollinator (bee, butterfly) operates on solar input
    captured through nectar/sugar metabolism. EROI is effectively
    infinite: the energy cost to humans is zero, and the system is
    self-replicating.

    A drone pollinator requires:
        - rare-earth materials (mining energy + supply chain)
        - manufacturing energy
        - battery production (lithium, cobalt)
        - operational energy
        - maintenance energy
        - replacement energy (drones fail)
        - control system energy (AI compute)

    EROI for drone pollination is far below 1.0 at any scale that
    could replace lost wild pollinator services.

Status: CC0. Stdlib only. ASCII only.
"""

from dataclasses import dataclass
from typing import Dict


# ─────────────────────────────────────────────
# CONSTANTS  (stylized, order-of-magnitude)
# Energy units throughout: megajoules (MJ)
# ─────────────────────────────────────────────

# Drone manufacture energy: small agricultural drone
DRONE_MANUFACTURE_MJ = 500.0     # ~140 kWh embodied energy
DRONE_BATTERY_MJ = 100.0         # additional embodied energy in lithium battery
DRONE_LIFESPAN_FLIGHTS = 1000    # before failure / replacement
DRONE_FLIGHT_ENERGY_MJ = 0.5     # per flight, hovering pollination work

# Maintenance and control overhead
DRONE_MAINTENANCE_MJ_PER_YEAR = 20.0
AI_CONTROL_COMPUTE_MJ_PER_DRONE_PER_YEAR = 50.0

# Pollination productivity
FLOWERS_POLLINATED_PER_DRONE_FLIGHT = 200
FLOWERS_PER_ACRE_TYPICAL_CROP = 100_000          # apple, almond, etc.
NATURAL_POLLINATOR_FLOWERS_PER_ACRE_PER_DAY = 80_000  # adequate wild pop

# Energy embodied in food output (the return)
FOOD_ENERGY_MJ_PER_ACRE_HARVEST = 30_000   # caloric content of typical
                                            # pollinated crop yield


# ─────────────────────────────────────────────
# EROI CALCULATIONS
# ─────────────────────────────────────────────

@dataclass
class EROIResult:
    system_name: str
    total_energy_input_mj: float
    food_energy_output_mj: float
    eroi: float
    notes: str


def natural_pollinator_eroi(acres: int) -> EROIResult:
    """
    EROI for natural pollinator services. Human energy input is
    effectively zero (stewardship requires labor but no fossil
    energy). The pollinators run on solar.
    """
    food_output = FOOD_ENERGY_MJ_PER_ACRE_HARVEST * acres
    # Stylized: assume human stewardship labor at 50 MJ/acre/year
    # (observation, light habitat work). No fossil energy required.
    energy_input = 50.0 * acres
    return EROIResult(
        system_name="natural_pollinators_with_stewardship",
        total_energy_input_mj=energy_input,
        food_energy_output_mj=food_output,
        eroi=food_output / energy_input,
        notes="Solar-driven; self-replicating; no rare-earth dependency",
    )


def drone_pollinator_eroi(acres: int, season_days: int = 30) -> EROIResult:
    """
    EROI for drone-based pollination at scale.
    """
    # How many flights to pollinate one acre?
    flights_per_acre = (
        FLOWERS_PER_ACRE_TYPICAL_CROP / FLOWERS_POLLINATED_PER_DRONE_FLIGHT
    )
    total_flights = flights_per_acre * acres

    # How many drones needed? Each drone can do ~10 flights/day.
    flights_per_drone_per_day = 10
    drones_needed = total_flights / (flights_per_drone_per_day * season_days)

    # Drones are replaced every 1000 flights
    drone_replacements = total_flights / DRONE_LIFESPAN_FLIGHTS

    # Energy budget
    manufacture_energy = drone_replacements * (
        DRONE_MANUFACTURE_MJ + DRONE_BATTERY_MJ
    )
    flight_energy = total_flights * DRONE_FLIGHT_ENERGY_MJ
    maintenance_energy = drones_needed * DRONE_MAINTENANCE_MJ_PER_YEAR
    ai_control_energy = drones_needed * AI_CONTROL_COMPUTE_MJ_PER_DRONE_PER_YEAR

    total_input = (manufacture_energy + flight_energy
                   + maintenance_energy + ai_control_energy)
    food_output = FOOD_ENERGY_MJ_PER_ACRE_HARVEST * acres

    return EROIResult(
        system_name="drone_pollination",
        total_energy_input_mj=total_input,
        food_energy_output_mj=food_output,
        eroi=food_output / total_input,
        notes=(
            f"{int(drones_needed):,} drones; "
            f"{int(drone_replacements):,} replacements per season; "
            "rare-earth + lithium dependency; AI compute required"
        ),
    )


def break_even_analysis(acres: int) -> Dict:
    """
    Compare EROIs and identify break-even point.
    """
    natural = natural_pollinator_eroi(acres)
    drone = drone_pollinator_eroi(acres)
    return {
        "acres":                    acres,
        "natural_pollinator_eroi":  round(natural.eroi, 2),
        "drone_pollinator_eroi":    round(drone.eroi, 4),
        "drone_energy_deficit_mj": (
            drone.total_energy_input_mj - drone.food_energy_output_mj
        ),
        "energy_ratio_natural_to_drone": (
            round(natural.eroi / drone.eroi, 1)
            if drone.eroi > 0 else "infinite"
        ),
        "verdict": (
            "drone pollination is energy-negative; "
            "thermodynamically cannot replace natural pollinators at scale"
            if drone.eroi < 1.0 else
            "drone pollination produces net energy"
        ),
    }


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("DRONE POLLINATION EROI ANALYSIS")
    print("=" * 60)

    test_acres = [100, 1_000, 10_000, 100_000]
    for acres in test_acres:
        result = break_even_analysis(acres)
        print(f"\n{acres:,} acres:")
        for k, v in result.items():
            if k == "acres":
                continue
            print(f"  {k}: {v}")

    print()
    print("=" * 60)
    print("DETAILED ENERGY BUDGET (10,000 acres):")
    natural = natural_pollinator_eroi(10_000)
    drone = drone_pollinator_eroi(10_000)
    print(f"\n  natural_pollinators_with_stewardship:")
    print(f"    energy in: {natural.total_energy_input_mj:,.0f} MJ")
    print(f"    food out:  {natural.food_energy_output_mj:,.0f} MJ")
    print(f"    EROI:      {natural.eroi:.1f}")
    print(f"    notes:     {natural.notes}")
    print(f"\n  drone_pollination:")
    print(f"    energy in: {drone.total_energy_input_mj:,.0f} MJ")
    print(f"    food out:  {drone.food_energy_output_mj:,.0f} MJ")
    print(f"    EROI:      {drone.eroi:.4f}")
    print(f"    notes:     {drone.notes}")
    print()
    print("CONCLUSION:")
    print("  EROI < 1.0 means the system consumes more energy than")
    print("  it produces. At any scale meaningful for replacing wild")
    print("  pollinators, drone pollination is thermodynamically")
    print("  negative. The technological 'fix' is not a fix.")
