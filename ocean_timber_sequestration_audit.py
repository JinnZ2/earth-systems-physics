"""
ocean_timber_sequestration_audit.py

Full-cycle thermodynamic audit of wood-in-ocean carbon sequestration schemes.
Coupled differential equation model across six constraint layers:

    Layer 0: Harvest Carbon Budget (soil, diesel, infrastructure)
    Layer 1: Transport Carbon Cost (road, truck, vessel)
    Layer 2: Benthic Physical Impact (smothering, accumulation)
    Layer 3: Ocean Chemistry Cascade (pH, O2, leachate)
    Layer 4: Decomposition Gas Production (CO2, CH4, H2S)
    Layer 5: Current / Stratification Disruption (thermohaline coupling)

Each layer produces a carbon-equivalent flow.
Net balance = stored carbon - ALL layer costs.
If net <= 0, the project is a carbon SOURCE sold as a carbon SINK.

CC0 — No rights reserved.
Part of: github.com/JinnZ2/earth-systems-physics

Dependencies: None (stdlib only)
"""

import math


# ═══════════════════════════════════════════════════════════════
# CONSTANTS — physical, not policy
# ═══════════════════════════════════════════════════════════════

CONSTANTS = {
    # Carbon content
    "carbon_fraction_dry_wood": 0.50,        # kg C / kg dry wood
    "dry_mass_per_boreal_tree_kg": 150.0,     # small boreal avg
    "wet_to_dry_ratio": 0.55,                 # boreal softwood

    # Diesel emissions
    "kg_CO2_per_liter_diesel": 2.68,          # combustion only
    "liters_diesel_per_feller_buncher_day": 200.0,
    "liters_diesel_per_skidder_day": 300.0,
    "trees_per_machine_day": 200.0,           # boreal, dispersed

    # Transport
    "truck_fuel_L_per_100km_loaded": 60.0,
    "trees_per_truck_load": 30.0,             # boreal, small stems
    "vessel_fuel_kg_per_tonne_km": 0.005,     # bulk carrier

    # Road construction through shield rock
    "kg_CO2_per_km_road_construction": 50000.0,  # blasting, aggregate, grading
    "km_road_per_1000_trees": 0.5,               # access road density

    # Soil carbon
    "boreal_soil_organic_C_kg_per_m2": 8.0,   # thin but dense organic mat
    "soil_disturbance_radius_m": 3.0,         # per tree harvest point (conservative)
    "soil_C_release_fraction": 0.30,          # immediate liberation from compaction/exposure
    "permafrost_fraction_of_boreal": 0.40,    # fraction of harvest area w/ permafrost
    "permafrost_thaw_CH4_kg_per_m2": 0.2,     # conservative, highly variable
    "CH4_to_CO2_equivalence": 80.0,           # 20-year GWP

    # Lost ongoing sequestration
    "boreal_tree_annual_C_uptake_kg": 2.0,    # per tree per year while alive
    "forest_regrowth_time_years": 200.0,      # boreal on shield, if ever

    # Ocean — decomposition
    "bark_sapwood_fraction": 0.35,            # decomposes in 0-50 yr
    "heartwood_fraction": 0.65,               # decomposes in 50-500 yr
    "decomp_O2_kg_per_kg_organic": 1.07,      # stoichiometric
    "leachate_DOC_fraction": 0.05,            # dissolved organic carbon released fast

    # Ocean — chemistry
    "tannin_pH_depression_per_tonne": 0.001,  # local, within 1km radius
    "CaCO3_dissolution_pH_threshold": 7.8,    # approximate saturation horizon
    "baseline_deep_ocean_pH": 7.95,

    # Ocean — methane production (anoxic phase)
    "anoxic_onset_O2_threshold_mL_L": 0.5,
    "CH4_yield_fraction_anoxic_wood": 0.02,   # kg CH4 per kg wood in anoxic conditions
    "years_to_anoxic_transition": 10.0,       # at scale, estimated

    # Benthic
    "benthic_kill_zone_m2_per_tonne_wood": 2.0,
    "benthic_recovery_time_years": 1000.0,    # conservative
    "foram_C_burial_kg_per_m2_per_year": 0.01,  # lost carbon burial capacity

    # Thermohaline sensitivity (dimensionless perturbation)
    "density_anomaly_per_Mt_wood": 1e-6,      # fractional, at formation site
    "AMOC_weakening_threshold": 0.01,         # fractional density perturbation
}


# ═══════════════════════════════════════════════════════════════
# CORE STATE VECTOR
# ═══════════════════════════════════════════════════════════════

def initial_state(n_trees_per_year=1_000_000, transport_km=1000.0,
                  ocean_depth_m=3000.0, dump_area_km2=10.0,
                  years=50):
    """
    Build initial state dictionary for simulation.
    All units SI or explicitly labeled.
    """
    dry_mass_per_tree = CONSTANTS["dry_mass_per_boreal_tree_kg"]
    total_dry_mass_per_year = n_trees_per_year * dry_mass_per_tree  # kg/yr

    return {
        # Scenario parameters
        "n_trees_per_year": n_trees_per_year,
        "transport_km": transport_km,
        "ocean_depth_m": ocean_depth_m,
        "dump_area_m2": dump_area_km2 * 1e6,
        "years": years,
        "dt": 1.0,  # year timestep

        # Mass flows
        "dry_mass_per_year_kg": total_dry_mass_per_year,
        "carbon_stored_per_year_kg": total_dry_mass_per_year * CONSTANTS["carbon_fraction_dry_wood"],

        # Accumulating state (initialized)
        "cumulative_wood_on_floor_kg": 0.0,
        "cumulative_carbon_stored_kg": 0.0,
        "cumulative_carbon_cost_kg": 0.0,
        "cumulative_methane_CO2e_kg": 0.0,
        "cumulative_benthic_kill_m2": 0.0,
        "cumulative_foram_burial_lost_kg": 0.0,
        "local_pH": CONSTANTS["baseline_deep_ocean_pH"],
        "local_O2_mL_L": 5.0,  # healthy deep ocean
        "anoxic": False,
        "thermohaline_perturbation": 0.0,

        # Time series storage
        "ts_net_carbon_kg": [],
        "ts_pH": [],
        "ts_O2": [],
        "ts_methane_CO2e_kg": [],
        "ts_benthic_kill_m2": [],
        "ts_thermohaline": [],
    }


# ═══════════════════════════════════════════════════════════════
# LAYER 0: HARVEST CARBON BUDGET
# ═══════════════════════════════════════════════════════════════

def harvest_carbon_cost(state):
    """
    Annual carbon cost of harvest operations.
    Returns kg CO2 equivalent.
    """
    C = CONSTANTS
    n = state["n_trees_per_year"]

    # Machine days
    machine_days = n / C["trees_per_machine_day"]

    # Diesel: feller-buncher + skidder
    diesel_L = machine_days * (
        C["liters_diesel_per_feller_buncher_day"] +
        C["liters_diesel_per_skidder_day"]
    )
    diesel_CO2 = diesel_L * C["kg_CO2_per_liter_diesel"]

    # Road construction
    road_km = (n / 1000.0) * C["km_road_per_1000_trees"]
    road_CO2 = road_km * C["kg_CO2_per_km_road_construction"]

    # Soil carbon liberation
    area_per_tree = math.pi * C["soil_disturbance_radius_m"] ** 2
    total_disturbed_m2 = n * area_per_tree
    soil_C_released = (
        total_disturbed_m2 *
        C["boreal_soil_organic_C_kg_per_m2"] *
        C["soil_C_release_fraction"]
    )
    soil_CO2 = soil_C_released * (44.0 / 12.0)  # C to CO2

    # Permafrost thaw methane (fraction of disturbed area)
    permafrost_area = total_disturbed_m2 * C["permafrost_fraction_of_boreal"]
    CH4_kg = permafrost_area * C["permafrost_thaw_CH4_kg_per_m2"]
    permafrost_CO2e = CH4_kg * C["CH4_to_CO2_equivalence"]

    # Lost ongoing sequestration (per year, cumulative over forest lifetime)
    lost_annual_uptake_C = n * C["boreal_tree_annual_C_uptake_kg"]
    lost_uptake_CO2 = lost_annual_uptake_C * (44.0 / 12.0)

    return {
        "diesel_CO2_kg": diesel_CO2,
        "road_CO2_kg": road_CO2,
        "soil_CO2_kg": soil_CO2,
        "permafrost_CO2e_kg": permafrost_CO2e,
        "lost_uptake_CO2_kg": lost_uptake_CO2,
        "total_kg": diesel_CO2 + road_CO2 + soil_CO2 + permafrost_CO2e + lost_uptake_CO2,
    }


# ═══════════════════════════════════════════════════════════════
# LAYER 1: TRANSPORT CARBON COST
# ═══════════════════════════════════════════════════════════════

def transport_carbon_cost(state):
    """
    Annual carbon cost of moving trees to ocean.
    Returns kg CO2.
    """
    C = CONSTANTS
    n = state["n_trees_per_year"]
    d = state["transport_km"]

    # Truck loads
    n_loads = n / C["trees_per_truck_load"]
    truck_diesel_L = n_loads * d * C["truck_fuel_L_per_100km_loaded"] / 100.0
    truck_CO2 = truck_diesel_L * C["kg_CO2_per_liter_diesel"]

    # Vessel (assume 200km ocean transit to dump site)
    ocean_km = 200.0
    total_mass_tonnes = state["dry_mass_per_year_kg"] / C["wet_to_dry_ratio"] / 1000.0
    vessel_fuel_kg = total_mass_tonnes * ocean_km * C["vessel_fuel_kg_per_tonne_km"]
    vessel_CO2 = vessel_fuel_kg * (44.0 / 12.0)  # approximate

    return {
        "truck_CO2_kg": truck_CO2,
        "vessel_CO2_kg": vessel_CO2,
        "total_kg": truck_CO2 + vessel_CO2,
    }


# ═══════════════════════════════════════════════════════════════
# LAYER 2: BENTHIC PHYSICAL IMPACT
# ═══════════════════════════════════════════════════════════════

def benthic_impact(state):
    """
    Cumulative seafloor destruction and lost carbon burial.
    """
    C = CONSTANTS
    wood_tonnes = state["cumulative_wood_on_floor_kg"] / 1000.0

    kill_zone_m2 = wood_tonnes * C["benthic_kill_zone_m2_per_tonne_wood"]
    foram_burial_lost_kg = kill_zone_m2 * C["foram_C_burial_kg_per_m2_per_year"]
    foram_burial_lost_CO2 = foram_burial_lost_kg * (44.0 / 12.0)

    return {
        "kill_zone_m2": kill_zone_m2,
        "foram_burial_lost_CO2_kg_per_year": foram_burial_lost_CO2,
    }


# ═══════════════════════════════════════════════════════════════
# LAYER 3: OCEAN CHEMISTRY — pH AND O2
# ═══════════════════════════════════════════════════════════════

def ocean_chemistry_step(state):
    """
    Update local pH and O2 based on cumulative wood load.
    Returns updated values.
    """
    C = CONSTANTS
    wood_tonnes = state["cumulative_wood_on_floor_kg"] / 1000.0
    area_m2 = state["dump_area_m2"]

    # pH depression from tannin/acid load
    pH_drop = wood_tonnes * C["tannin_pH_depression_per_tonne"]
    new_pH = max(6.0, C["baseline_deep_ocean_pH"] - pH_drop)

    # O2 consumption from decomposing fraction
    # bark/sapwood fraction decomposes first
    decomposing_mass = wood_tonnes * 1000.0 * C["bark_sapwood_fraction"]
    # spread over dump area, consume O2 from water column above
    # simplified: O2 demand per m2 per year
    O2_demand_kg_per_m2 = (decomposing_mass * C["decomp_O2_kg_per_kg_organic"] * 0.02) / area_m2
    # convert to mL/L equivalent (very rough, depends on water volume)
    # assume 100m water column above pile exchanges
    water_volume_L_per_m2 = 100.0 * 1000.0  # 100m * 1000 L/m3
    O2_consumed_mL_L = (O2_demand_kg_per_m2 * 1e6 / 1.429) / water_volume_L_per_m2  # 1.429 kg/m3 O2 density
    new_O2 = max(0.0, state["local_O2_mL_L"] - O2_consumed_mL_L)

    anoxic = new_O2 < C["anoxic_onset_O2_threshold_mL_L"]

    return {
        "pH": new_pH,
        "O2_mL_L": new_O2,
        "anoxic": anoxic,
        "CaCO3_dissolving": new_pH < C["CaCO3_dissolution_pH_threshold"],
    }


# ═══════════════════════════════════════════════════════════════
# LAYER 4: DECOMPOSITION GAS PRODUCTION
# ═══════════════════════════════════════════════════════════════

def gas_production(state, year):
    """
    CO2 and CH4 production from decomposing wood mass.
    CH4 only produced after anoxic transition.
    Returns kg CO2 equivalent.
    """
    C = CONSTANTS
    wood_kg = state["cumulative_wood_on_floor_kg"]

    # Aerobic decomposition CO2 (always, from bark/sapwood)
    aerobic_CO2_kg = (
        wood_kg * C["bark_sapwood_fraction"] * 0.01 *  # 1% per year turnover
        C["carbon_fraction_dry_wood"] * (44.0 / 12.0)
    )

    # Anaerobic CH4 (only after anoxic transition)
    CH4_CO2e_kg = 0.0
    if state["anoxic"]:
        CH4_kg = wood_kg * C["CH4_yield_fraction_anoxic_wood"] * 0.01  # per year
        CH4_CO2e_kg = CH4_kg * C["CH4_to_CO2_equivalence"]

    return {
        "aerobic_CO2_kg": aerobic_CO2_kg,
        "CH4_CO2e_kg": CH4_CO2e_kg,
        "total_CO2e_kg": aerobic_CO2_kg + CH4_CO2e_kg,
    }


# ═══════════════════════════════════════════════════════════════
# LAYER 5: THERMOHALINE PERTURBATION
# ═══════════════════════════════════════════════════════════════

def thermohaline_perturbation(state):
    """
    Dimensionless density perturbation estimate.
    Flags when approaching AMOC disruption threshold.
    """
    C = CONSTANTS
    wood_Mt = state["cumulative_wood_on_floor_kg"] / 1e9  # megatonnes

    perturbation = wood_Mt * C["density_anomaly_per_Mt_wood"]
    threshold_fraction = perturbation / C["AMOC_weakening_threshold"]

    return {
        "perturbation": perturbation,
        "threshold_fraction": threshold_fraction,
        "warning": threshold_fraction > 0.1,
        "critical": threshold_fraction > 0.5,
    }


# ═══════════════════════════════════════════════════════════════
# SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════

def run_simulation(n_trees_per_year=1_000_000, transport_km=1000.0,
                   ocean_depth_m=3000.0, dump_area_km2=10.0,
                   years=50):
    """
    Run full coupled simulation.
    Returns state dict with time series and final audit.
    """
    state = initial_state(n_trees_per_year, transport_km,
                          ocean_depth_m, dump_area_km2, years)

    cumulative_cost_CO2 = 0.0
    cumulative_stored_C = 0.0
    cumulative_lost_uptake_CO2 = 0.0

    for year in range(1, years + 1):

        # ── Layer 0: Harvest ──
        harvest = harvest_carbon_cost(state)

        # ── Layer 1: Transport ──
        transport = transport_carbon_cost(state)

        # ── Accumulate wood on floor ──
        state["cumulative_wood_on_floor_kg"] += state["dry_mass_per_year_kg"]

        # ── Layer 2: Benthic ──
        benthic = benthic_impact(state)

        # ── Layer 3: Chemistry ──
        chem = ocean_chemistry_step(state)
        state["local_pH"] = chem["pH"]
        state["local_O2_mL_L"] = chem["O2_mL_L"]
        state["anoxic"] = chem["anoxic"]

        # ── Layer 4: Gas production ──
        gas = gas_production(state, year)

        # ── Layer 5: Thermohaline ──
        thermo = thermohaline_perturbation(state)
        state["thermohaline_perturbation"] = thermo["perturbation"]

        # ── Accounting ──
        year_carbon_stored_CO2 = state["carbon_stored_per_year_kg"] * (44.0 / 12.0)

        # Lost uptake is cumulative: each year's killed trees KEEP not sequestering
        cumulative_lost_uptake_CO2 += harvest["lost_uptake_CO2_kg"]

        year_total_cost = (
            harvest["total_kg"] +
            transport["total_kg"] +
            gas["total_CO2e_kg"] +
            benthic["foram_burial_lost_CO2_kg_per_year"] +
            cumulative_lost_uptake_CO2  # grows every year
        )

        cumulative_stored_C += year_carbon_stored_CO2
        cumulative_cost_CO2 += year_total_cost

        net = cumulative_stored_C - cumulative_cost_CO2

        # ── Store time series ──
        state["ts_net_carbon_kg"].append(net)
        state["ts_pH"].append(chem["pH"])
        state["ts_O2"].append(chem["O2_mL_L"])
        state["ts_methane_CO2e_kg"].append(gas["CH4_CO2e_kg"])
        state["ts_benthic_kill_m2"].append(benthic["kill_zone_m2"])
        state["ts_thermohaline"].append(thermo["threshold_fraction"])

    # ── Final state ──
    state["cumulative_carbon_stored_kg"] = cumulative_stored_C
    state["cumulative_carbon_cost_kg"] = cumulative_cost_CO2
    state["net_carbon_CO2_kg"] = cumulative_stored_C - cumulative_cost_CO2
    state["project_is_net_source"] = (cumulative_stored_C - cumulative_cost_CO2) < 0
    state["crossover_year"] = None

    for i, net in enumerate(state["ts_net_carbon_kg"]):
        if net < 0:
            state["crossover_year"] = i + 1
            break

    return state


# ═══════════════════════════════════════════════════════════════
# AUDIT REPORT
# ═══════════════════════════════════════════════════════════════

def print_audit(state):
    """Print human-readable audit of simulation results."""

    print("=" * 60)
    print("OCEAN TIMBER SEQUESTRATION — FULL-CYCLE CARBON AUDIT")
    print("=" * 60)
    print()
    print(f"  Scenario: {state['n_trees_per_year']:,.0f} trees/year")
    print(f"  Transport distance: {state['transport_km']:.0f} km")
    print(f"  Duration: {state['years']} years")
    print(f"  Dump area: {state['dump_area_m2']/1e6:.1f} km²")
    print()
    print("-" * 60)
    print("CARBON BALANCE")
    print("-" * 60)
    stored = state["cumulative_carbon_stored_kg"]
    cost = state["cumulative_carbon_cost_kg"]
    net = state["net_carbon_CO2_kg"]
    print(f"  Carbon stored (claimed):  {stored/1e3:>14,.1f} tonnes CO₂")
    print(f"  Carbon cost (actual):     {cost/1e3:>14,.1f} tonnes CO₂e")
    print(f"  ────────────────────────────────────────────")
    print(f"  NET:                      {net/1e3:>14,.1f} tonnes CO₂e")
    print()

    if state["project_is_net_source"]:
        print("  ██ PROJECT IS A NET CARBON SOURCE ██")
        print(f"  Crossed zero at year: {state['crossover_year']}")
    else:
        print("  Project shows net sequestration on paper.")
        print("  WARNING: Many costs conservatively estimated.")
        print("  WARNING: Cascade failures not fully monetized.")
    print()

    print("-" * 60)
    print("OCEAN IMPACT (end of simulation)")
    print("-" * 60)
    print(f"  Local pH:               {state['local_pH']:.2f}  (baseline: 7.95)")
    print(f"  Local O₂:              {state['local_O2_mL_L']:.2f} mL/L  (healthy: 5.0)")
    print(f"  Anoxic:                 {'YES' if state['anoxic'] else 'No'}")
    print(f"  Benthic kill zone:      {state['ts_benthic_kill_m2'][-1]/1e6:.2f} km²")
    print(f"  Thermohaline fraction:  {state['ts_thermohaline'][-1]:.4f} of threshold")
    print()

    print("-" * 60)
    print("IRREVERSIBILITY FLAGS")
    print("-" * 60)
    flags = []
    if state["anoxic"]:
        flags.append("ANOXIC ZONE ESTABLISHED — methane production active")
    if state["local_pH"] < CONSTANTS["CaCO3_dissolution_pH_threshold"]:
        flags.append("pH BELOW CaCO3 SATURATION — shell dissolution active")
    if state["ts_thermohaline"][-1] > 0.1:
        flags.append("THERMOHALINE PERTURBATION >10% of threshold")
    if state["crossover_year"] and state["crossover_year"] < state["years"]:
        flags.append(f"NET SOURCE after year {state['crossover_year']}")
    flags.append(f"BENTHIC RECOVERY TIME: ~{CONSTANTS['benthic_recovery_time_years']:.0f} years")
    flags.append("CANNOT RETRIEVE WOOD FROM OCEAN FLOOR — no abort mechanism")

    for f in flags:
        print(f"  ⚠ {f}")

    print()
    print("=" * 60)
    print("VERDICT: Every cost above is CONSERVATIVE.")
    print("Real-world cascade failures will be worse.")
    print("Unmodeled interactions (insect migration,")
    print("  forest ecosystem services, fishery impacts)")
    print("  are additional uncounted negatives.")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    print("Running default scenario: 1M trees/year, 50 years, 1000km transport")
    print()

    state = run_simulation(
        n_trees_per_year=1_000_000,
        transport_km=1000.0,
        ocean_depth_m=3000.0,
        dump_area_km2=10.0,
        years=50,
    )

    print_audit(state)

    # Sensitivity: what if they claim shorter transport?
    print()
    print()
    print("=" * 60)
    print("SENSITIVITY: 500km transport, 100-year horizon")
    print("=" * 60)

    state2 = run_simulation(
        n_trees_per_year=1_000_000,
        transport_km=500.0,
        ocean_depth_m=3000.0,
        dump_area_km2=10.0,
        years=100,
    )

    print_audit(state2)
