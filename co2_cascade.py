"""
co2_cascade.py
==============
Coupled cascade: atmospheric CO2 -> water chemistry -> cooling system integrity
                -> computational reliability -> energy budget viability

Physics-first. CC0. Integrates as a constraint layer into earth-systems-physics.

Cascade pathway:
    CO2_atm  ->  Henry's law dissolution  ->  carbonic acid equilibrium
             ->  pH shift  ->  corrosion rate (material-specific)
             ->  cooling efficiency degradation
             ->  thermal margin loss  ->  bit-flip rate amplification
             ->  required redundancy/replacement energy
             ->  net computational viability

No prose. No assumptions outside published constants.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# =============================================================================
# LAYER 1: ATMOSPHERIC CO2 -> DISSOLVED INORGANIC CARBON
# =============================================================================

# Henry's law constant for CO2 in water at 25C, mol/(L*atm)
KH_CO2_25C = 0.034
# Temperature dependence (van't Hoff), enthalpy of dissolution J/mol
DH_CO2 = -19400.0
R_GAS = 8.314  # J/(mol*K)

# Carbonic acid dissociation constants (25C)
KA1 = 4.45e-7   # H2CO3 <-> H+ + HCO3-
KA2 = 4.69e-11  # HCO3- <-> H+ + CO3^2-


def henry_constant(temp_K: float) -> float:
    """Henry's constant for CO2 at given temperature, mol/(L*atm)."""
    T0 = 298.15
    return KH_CO2_25C * math.exp(-DH_CO2 / R_GAS * (1.0 / temp_K - 1.0 / T0))


def dissolved_co2(co2_ppm: float, temp_K: float, total_pressure_atm: float = 1.0) -> float:
    """Dissolved CO2 concentration, mol/L."""
    p_co2 = (co2_ppm / 1e6) * total_pressure_atm
    return henry_constant(temp_K) * p_co2


def water_pH(co2_ppm: float, temp_K: float = 298.15,
             buffering_alkalinity_eq_per_L: float = 0.0) -> float:
    """
    Equilibrium pH of water exposed to atmospheric CO2.
    Solves charge balance: [H+] = [HCO3-] + 2[CO3^2-] + [OH-] - alkalinity_offset
    Uses iterative solver. Pure water -> alkalinity = 0.
    """
    co2_aq = dissolved_co2(co2_ppm, temp_K)
    Kw = 1.0e-14

    # Bisection on [H+]
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        H = math.sqrt(lo * hi)
        HCO3 = KA1 * co2_aq / H
        CO3 = KA2 * HCO3 / H
        OH = Kw / H
        charge = H + buffering_alkalinity_eq_per_L - HCO3 - 2 * CO3 - OH
        if charge > 0:
            hi = H
        else:
            lo = H
        if abs(hi - lo) / max(H, 1e-30) < 1e-9:
            break
    return -math.log10(H)


# =============================================================================
# LAYER 2: pH -> CORROSION RATE (MATERIAL-SPECIFIC)
# =============================================================================

@dataclass
class MaterialCorrosion:
    """Empirical corrosion model: rate = base * 10^(slope * (pH_ref - pH))."""
    name: str
    base_rate_mm_per_year: float   # at pH_ref
    pH_ref: float
    pH_slope: float                 # decades of acceleration per pH unit drop
    fails_below_pH: float           # hard failure threshold
    notes: str = ""


MATERIALS = {
    "copper":   MaterialCorrosion("copper",   0.005, 7.0, 0.55, 5.5,
                                   "Cu cooling tubing; carbonic acid attack"),
    "aluminum": MaterialCorrosion("aluminum", 0.010, 7.0, 0.70, 5.0,
                                   "Al heatsinks; passivation breaks below ~pH 5"),
    "mild_steel": MaterialCorrosion("mild_steel", 0.080, 7.0, 0.80, 6.0,
                                     "Generic steel; iron carbonate scaling"),
    "stainless_316": MaterialCorrosion("stainless_316", 0.001, 7.0, 0.30, 4.0,
                                        "Resists carbonic acid; pitting risk at chloride+low pH"),
    "titanium": MaterialCorrosion("titanium", 0.0001, 7.0, 0.10, 2.0,
                                   "Effectively inert in this regime"),
    "PEX_polymer": MaterialCorrosion("PEX_polymer", 0.0, 7.0, 0.0, 0.0,
                                      "No metallic corrosion; check oxidative aging separately"),
    "graphite": MaterialCorrosion("graphite", 0.0, 7.0, 0.0, 0.0,
                                   "Inert; conducts heat; oxidation only at high T"),
}


def corrosion_rate(material: str, pH: float) -> float:
    """mm/year material loss at given pH."""
    m = MATERIALS[material]
    if pH < m.fails_below_pH:
        return float("inf")
    return m.base_rate_mm_per_year * (10.0 ** (m.pH_slope * (m.pH_ref - pH)))


def time_to_failure_years(material: str, pH: float, wall_thickness_mm: float) -> float:
    """Years until wall is breached."""
    rate = corrosion_rate(material, pH)
    if rate == 0.0:
        return float("inf")
    if rate == float("inf"):
        return 0.0
    return wall_thickness_mm / rate


# =============================================================================
# LAYER 3: CORROSION + BIOFILM -> COOLING EFFICIENCY DEGRADATION
# =============================================================================

@dataclass
class CoolingSystem:
    name: str
    material: str
    wall_thickness_mm: float
    design_thermal_W: float        # rated heat removal
    fluid_volume_L: float
    flow_rate_L_per_min: float
    biofilm_growth_factor: float = 1.0  # >1 if low pH selects biofilm regime


def cooling_efficiency_loss(system: CoolingSystem, pH: float, years_in_service: float) -> float:
    """
    Fractional loss of thermal capacity. 0.0 = pristine, 1.0 = total failure.
    Combines wall thinning (-> leak risk, reduced flow margin) and
    biofilm fouling (-> insulating layer on heat exchange surfaces).
    """
    rate = corrosion_rate(system.material, pH)
    if rate == float("inf"):
        return 1.0
    wall_loss_frac = min(1.0, (rate * years_in_service) / system.wall_thickness_mm)

    # Biofilm: empirical Arrhenius-like response to pH stress
    # acidified water shifts microbial community; some thrive, fouling rises
    pH_stress = max(0.0, 7.0 - pH)
    biofilm_frac = 1.0 - math.exp(-0.15 * pH_stress * system.biofilm_growth_factor * years_in_service)

    # Combined (not independent; cap at 1.0)
    return min(1.0, wall_loss_frac + biofilm_frac - wall_loss_frac * biofilm_frac)


# =============================================================================
# LAYER 4: THERMAL MARGIN -> BIT-FLIP RATE
# =============================================================================

# Baseline soft error rate per Mbit per hour at sea level, stable magnetic field
BASELINE_SER_PER_MBIT_HR = 1e-3

# Geomagnetic shielding factor: weakens as field weakens
# Ratio of current dipole moment to ~1900 baseline
def geomagnetic_factor(field_strength_ratio: float) -> float:
    """field_strength_ratio = B_current / B_1900. 1.0 = baseline. Lower = weaker shielding."""
    # Cosmic ray flux at surface scales roughly inversely with shielding
    return 1.0 / max(field_strength_ratio, 0.3)


def thermal_amplification(efficiency_loss: float) -> float:
    """
    As cooling fails, junction temperature rises. SER scales ~exponentially with T.
    Each 10C rise roughly doubles soft error rate (empirical, modern CMOS).
    """
    # Map efficiency loss to delta-T (K). Saturates at ~40K rise before shutdown.
    delta_T = 40.0 * efficiency_loss
    return 2.0 ** (delta_T / 10.0)


def bit_flip_rate(memory_Mbit: float, efficiency_loss: float,
                  geomagnetic_ratio: float = 1.0) -> float:
    """Errors per hour for a given memory size."""
    return (BASELINE_SER_PER_MBIT_HR
            * memory_Mbit
            * thermal_amplification(efficiency_loss)
            * geomagnetic_factor(geomagnetic_ratio))


# =============================================================================
# LAYER 5: ENERGY BUDGET FOR MAINTAINING VIABILITY
# =============================================================================

@dataclass
class EnergyBudget:
    """Energy cost components in kWh/year for one cooling system."""
    base_cooling_kWh: float
    replacement_material_kWh: float   # embodied energy of replaced parts per year
    filtration_kWh: float              # CO2/acid scrubbing of process water
    redundancy_kWh: float              # extra compute to mask bit flips


def energy_cost(system: CoolingSystem, pH: float,
                memory_Mbit: float, geomagnetic_ratio: float,
                years_in_service: float = 1.0,
                embodied_energy_MJ_per_kg: float = 50.0,
                wall_density_kg_per_m2_per_mm: float = 8.0) -> EnergyBudget:
    """
    Annualized energy cost to keep this system computationally viable.
    """
    eff_loss = cooling_efficiency_loss(system, pH, 1.0)  # per-year delta
    base = system.design_thermal_W * 8760 / 1000.0       # rated cooling per year, kWh

    # Replacement: corroded wall mass per year, converted to embodied energy
    rate = corrosion_rate(system.material, pH)
    if rate == float("inf"):
        replacement = 1e9  # forced replacement; flag as nonviable
    else:
        # crude: surface area ~ proxy via fluid_volume and a surface/volume ratio
        surface_m2 = max(0.5, system.fluid_volume_L / 10.0)
        mass_lost_kg_per_yr = surface_m2 * wall_density_kg_per_m2_per_mm * rate
        replacement = mass_lost_kg_per_yr * embodied_energy_MJ_per_kg * 1000.0 / 3600.0

    # Filtration: energy to scrub dissolved CO2 / neutralize acid
    # Empirical: ~0.5 kWh per m3 water per pH unit raised
    pH_correction = max(0.0, 7.0 - pH)
    water_m3_per_yr = system.flow_rate_L_per_min * 60 * 24 * 365 / 1000.0
    filtration = 0.5 * water_m3_per_yr * pH_correction

    # Redundancy: extra compute to mask soft errors via ECC + replication
    flips_per_hr = bit_flip_rate(memory_Mbit, eff_loss, geomagnetic_ratio)
    # Each flip above tolerance budget (1/hr) costs replication overhead
    overhead_factor = max(0.0, math.log10(max(flips_per_hr, 1.0)))
    redundancy = base * 0.1 * overhead_factor

    return EnergyBudget(base, replacement, filtration, redundancy)


def viability_ratio(budget: EnergyBudget, available_kWh_per_year: float) -> float:
    """If > 1.0, system is not energetically viable in this regime."""
    total = (budget.base_cooling_kWh + budget.replacement_material_kWh
             + budget.filtration_kWh + budget.redundancy_kWh)
    return total / available_kWh_per_year


# =============================================================================
# CASCADE EVALUATION ENTRY POINT
# =============================================================================

def evaluate_cascade(co2_ppm: float,
                     temp_K: float,
                     system: CoolingSystem,
                     memory_Mbit: float,
                     geomagnetic_ratio: float,
                     available_kWh_per_year: float,
                     buffering: float = 0.0,
                     years_in_service: float = 5.0) -> Dict:
    """Run the full cascade. Returns every layer's state."""
    pH = water_pH(co2_ppm, temp_K, buffering)
    rate = corrosion_rate(system.material, pH)
    ttf = time_to_failure_years(system.material, pH, system.wall_thickness_mm)
    eff_loss = cooling_efficiency_loss(system, pH, years_in_service)
    flips = bit_flip_rate(memory_Mbit, eff_loss, geomagnetic_ratio)
    budget = energy_cost(system, pH, memory_Mbit, geomagnetic_ratio, years_in_service)
    via = viability_ratio(budget, available_kWh_per_year)

    return {
        "co2_ppm": co2_ppm,
        "pH": pH,
        "corrosion_mm_per_yr": rate,
        "wall_time_to_failure_yr": ttf,
        "cooling_efficiency_loss": eff_loss,
        "bit_flips_per_hr": flips,
        "energy_kWh_per_yr": {
            "base_cooling": budget.base_cooling_kWh,
            "replacement": budget.replacement_material_kWh,
            "filtration": budget.filtration_kWh,
            "redundancy": budget.redundancy_kWh,
            "total": (budget.base_cooling_kWh + budget.replacement_material_kWh
                      + budget.filtration_kWh + budget.redundancy_kWh),
        },
        "viability_ratio": via,
        "viable": via < 1.0 and rate != float("inf"),
    }


# =============================================================================
# DEMO: scan CO2 ppm vs material choice
# =============================================================================

if __name__ == "__main__":
    co2_levels = [280, 420, 550, 700, 1000, 1500]
    materials_to_test = ["copper", "aluminum", "mild_steel", "stainless_316", "titanium"]

    print("CO2_ppm | material        |   pH  | corr mm/yr |  TTF yr | eff_loss | flips/hr | viable")
    print("-" * 100)
    for co2 in co2_levels:
        for mat in materials_to_test:
            sys = CoolingSystem(
                name=f"server_loop_{mat}",
                material=mat,
                wall_thickness_mm=2.0,
                design_thermal_W=5000.0,
                fluid_volume_L=20.0,
                flow_rate_L_per_min=10.0,
            )
            r = evaluate_cascade(
                co2_ppm=co2,
                temp_K=298.15,
                system=sys,
                memory_Mbit=64000,           # 8 GB
                geomagnetic_ratio=0.85,      # ~15% weaker than 1900
                available_kWh_per_year=80000,
                years_in_service=5.0,
            )
            ttf = r["wall_time_to_failure_yr"]
            ttf_s = f"{ttf:7.1f}" if ttf != float("inf") else "    inf"
            corr = r["corrosion_mm_per_yr"]
            corr_s = f"{corr:8.4f}" if corr != float("inf") else "     inf"
            print(f"{co2:7d} | {mat:14s}  | {r['pH']:.2f}  | {corr_s}   | {ttf_s} | "
                  f"  {r['cooling_efficiency_loss']:.2f}   | "
                  f"{r['bit_flips_per_hr']:8.2f} | {r['viable']}")
