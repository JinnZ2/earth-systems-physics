“””
dollar_energy_metabolism.py

Recursive energy cost model for financial system overhead.
Every dollar routed through the financial system carries
a metabolic energy load that compounds through leverage,
margin capture, taxation, advertising, and political
infrastructure — each layer generating economic activity
subject to the same overhead.

This is a geometric series. If any layer’s recycling
fraction r >= 1, the system is a net energy sink:
it consumes more energy processing the dollar than
the dollar can deliver to the project.

Applied to: ocean timber sequestration, stratospheric
aerosol injection, and arbitrary climate finance schemes.

Core equation:
E_total = E_base / (1 - r_effective)
where r_effective = weighted recycling fraction
across all overhead layers

CC0 — No rights reserved.
Part of: github.com/JinnZ2/earth-systems-physics

Dependencies: None (stdlib only)
“””

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ═══════════════════════════════════════════════════════════════

# OVERHEAD LAYER DEFINITIONS

# ═══════════════════════════════════════════════════════════════

@dataclass
class OverheadLayer:
“””
Single layer of financial system energy overhead.

```
name:       human identifier
r_low:      conservative recycling fraction (MJ added / MJ base)
r_high:     extractive-case recycling fraction
description: what this layer represents physically
"""
name: str
r_low: float
r_high: float
description: str
```

# The six overhead layers, empirically bounded

OVERHEAD_LAYERS = [
OverheadLayer(
name=“leverage”,
r_low=0.11,
r_high=0.56,
description=(
“Banking infrastructure maintaining 3-10x leverage “
“per deployed dollar. Buildings, servers, staff, “
“clearinghouses, custodians, auditors, regulators. “
“Banking sector: ~2% of global electricity.”
),
),
OverheadLayer(
name=“margin_stack”,
r_low=0.23,
r_high=1.40,
description=(
“Fund managers (15-25%), project developers (10-20%), “
“verification bodies (5-10%), credit brokers (5-15%). “
“Total intermediary capture: 35-70% of each dollar. “
“r > 1 means intermediaries consume more energy “
“than the project receives. This is real.”
),
),
OverheadLayer(
name=“taxation”,
r_low=0.04,
r_high=0.68,
description=(
“Tax collection, processing, redistribution. “
“Each margin transaction taxed, tax spent on “
“government operations including military “
“(DOD: ~77M barrels oil/year). “
“Recursive: tax revenue generates taxable activity.”
),
),
OverheadLayer(
name=“narrative”,
r_low=0.05,
r_high=0.40,
description=(
“PR firms, websites, social media campaigns, “
“video production, data center infrastructure “
“for ad targeting (GPU clusters 24/7), “
“conference travel, white papers. “
“Energy cost of persuasion often exceeds “
“energy cost of intervention.”
),
),
OverheadLayer(
name=“political”,
r_low=0.11,
r_high=0.30,
description=(
“Lobbyists ($300-800/hr), campaign contributions, “
“think tanks, regulatory process (environmental “
“review, public comment, legal challenges, “
“compliance monitoring). Davos alone: ~1,500 “
“private jets to discuss climate.”
),
),
]

# ═══════════════════════════════════════════════════════════════

# SCENARIO PRESETS

# ═══════════════════════════════════════════════════════════════

@dataclass
class Scenario:
“”“Financial routing scenario for a climate dollar.”””
name: str
E_base_MJ: float          # direct energy intensity of $1 GDP
layer_positions: str       # ‘low’, ‘mid’, ‘high’ — where in range
recursive_r: float         # effective recycling fraction for geometric series
description: str

SCENARIOS = {
“direct_action”: Scenario(
name=“Direct action (no intermediaries)”,
E_base_MJ=5.0,
layer_positions=“none”,
recursive_r=0.0,
description=“You do the work yourself. No financial system overhead.”,
),
“efficient”: Scenario(
name=“Efficient project finance”,
E_base_MJ=5.0,
layer_positions=“low”,
recursive_r=0.30,
description=“Low margin, fast permitting, minimal leverage.”,
),
“typical_climate”: Scenario(
name=“Typical climate finance”,
E_base_MJ=6.0,
layer_positions=“mid”,
recursive_r=0.50,
description=“50% margin stack, 3-year permitting, standard leverage.”,
),
“carbon_speculation”: Scenario(
name=“Carbon credit speculation”,
E_base_MJ=7.0,
layer_positions=“high”,
recursive_r=0.70,
description=“70% margin stack, 7-year permitting, high leverage, speculative.”,
),
}

# ═══════════════════════════════════════════════════════════════

# PROJECT DEFINITIONS

# ═══════════════════════════════════════════════════════════════

@dataclass
class ClimateProject:
“”“A climate intervention scheme to audit.”””
name: str
capitalization_low_USD: float
capitalization_high_USD: float
annual_budget_low_USD: float
annual_budget_high_USD: float
claimed_annual_CO2_tonnes: float   # claimed sequestration or offset
is_sequestration: bool             # True = claims to remove CO2
description: str

PROJECTS = {
“ocean_timber”: ClimateProject(
name=“Ocean Timber Sequestration”,
capitalization_low_USD=50e6,
capitalization_high_USD=200e6,
annual_budget_low_USD=10e6,
annual_budget_high_USD=50e6,
claimed_annual_CO2_tonnes=275_000,
is_sequestration=True,
description=(
“Cut 1M boreal trees/year, sink in deep ocean. “
“Claimed: permanent carbon removal. “
“Actual: net carbon source before financial overhead.”
),
),
“sai”: ClimateProject(
name=“Stratospheric Aerosol Injection”,
capitalization_low_USD=500e6,
capitalization_high_USD=5e9,
annual_budget_low_USD=2e9,
annual_budget_high_USD=10e9,
claimed_annual_CO2_tonnes=0,  # doesn’t sequester, only masks
is_sequestration=False,
description=(
“Mine bauxite, refine aluminum, mill to nanoparticles, “
“fly 60,000 sorties/year into stratosphere. “
“Masks warming but sequesters nothing. “
“Termination shock if stopped. Perpetual commitment.”
),
),
}

# ═══════════════════════════════════════════════════════════════

# CORE ENGINE

# ═══════════════════════════════════════════════════════════════

def layer_energy(layer: OverheadLayer, position: str, E_base: float) -> float:
“””
Calculate energy added by a single overhead layer.

```
position: 'low', 'mid', 'high', or 'none'
Returns MJ added per dollar.
"""
if position == "none":
    return 0.0

if position == "low":
    r = layer.r_low
elif position == "high":
    r = layer.r_high
else:  # mid
    r = (layer.r_low + layer.r_high) / 2.0

return r * E_base
```

def compute_dollar_energy(scenario: Scenario) -> dict:
“””
Compute total energy cost per dollar for a given scenario.

```
Returns dict with full decomposition.
"""
E_base = scenario.E_base_MJ
pos = scenario.layer_positions

# Sum layer contributions
layer_breakdown = {}
subtotal_additions = 0.0

for layer in OVERHEAD_LAYERS:
    added = layer_energy(layer, pos, E_base)
    layer_breakdown[layer.name] = {
        "MJ_added": added,
        "r_fraction": added / E_base if E_base > 0 else 0.0,
        "description": layer.description,
    }
    subtotal_additions += added

subtotal = E_base + subtotal_additions

# Geometric series: recursive overhead
r = scenario.recursive_r
if r >= 1.0:
    # Divergent: infinite energy cost
    recursive_multiplier = float('inf')
    total_MJ = float('inf')
else:
    recursive_multiplier = 1.0 / (1.0 - r)
    total_MJ = subtotal * recursive_multiplier

overall_multiplier = total_MJ / E_base if E_base > 0 else float('inf')

return {
    "scenario": scenario.name,
    "E_base_MJ": E_base,
    "layer_breakdown": layer_breakdown,
    "subtotal_before_recursion_MJ": subtotal,
    "recursive_r": r,
    "recursive_multiplier": recursive_multiplier,
    "total_MJ_per_dollar": total_MJ,
    "overall_multiplier": overall_multiplier,
    "divergent": r >= 1.0,
}
```

def compute_project_audit(project: ClimateProject, scenario: Scenario) -> dict:
“””
Apply dollar energy metabolism to a specific climate project.
Returns full audit with CO2 equivalence.
“””
dollar_energy = compute_dollar_energy(scenario)

```
MJ_per_dollar = dollar_energy["total_MJ_per_dollar"]

# Global average grid emission factor: ~70 g CO2/MJ primary energy
# (conservative — includes fossil fuel mix)
CO2_per_MJ_kg = 0.070  # kg CO2 per MJ

results = {}

for label, USD in [
    ("capitalization_low", project.capitalization_low_USD),
    ("capitalization_high", project.capitalization_high_USD),
    ("annual_budget_low", project.annual_budget_low_USD),
    ("annual_budget_high", project.annual_budget_high_USD),
]:
    if math.isinf(MJ_per_dollar):
        energy_TJ = float('inf')
        CO2_tonnes = float('inf')
    else:
        energy_MJ = USD * MJ_per_dollar
        energy_TJ = energy_MJ / 1e6
        CO2_tonnes = (energy_MJ * CO2_per_MJ_kg) / 1000.0  # kg to tonnes
    
    results[label] = {
        "USD": USD,
        "energy_TJ": energy_TJ,
        "CO2_tonnes": CO2_tonnes,
    }

# Compare to claimed sequestration
claimed = project.claimed_annual_CO2_tonnes

if claimed > 0 and not math.isinf(results["annual_budget_low"]["CO2_tonnes"]):
    funding_years_low = results["annual_budget_low"]["CO2_tonnes"] / claimed
    funding_years_high = results["annual_budget_high"]["CO2_tonnes"] / claimed
else:
    funding_years_low = float('inf')
    funding_years_high = float('inf')

return {
    "project": project.name,
    "scenario": scenario.name,
    "dollar_energy": dollar_energy,
    "project_costs": results,
    "claimed_annual_CO2_tonnes": claimed,
    "funding_CO2_as_fraction_of_claimed": {
        "low_budget": funding_years_low,
        "high_budget": funding_years_high,
    },
    "is_sequestration": project.is_sequestration,
    "description": project.description,
}
```

# ═══════════════════════════════════════════════════════════════

# GEOMETRIC SERIES EXPLORER

# ═══════════════════════════════════════════════════════════════

def explore_recycling_fraction(E_base: float = 6.0,
subtotal: float = 13.7,
r_range: Optional[List[float]] = None) -> list:
“””
Show how total energy scales with recycling fraction r.
Demonstrates approach to divergence.

```
Returns list of (r, total_MJ, multiplier) tuples.
"""
if r_range is None:
    r_range = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]

results = []
for r in r_range:
    if r >= 1.0:
        results.append((r, float('inf'), float('inf')))
    else:
        total = subtotal / (1.0 - r)
        multiplier = total / E_base
        results.append((r, total, multiplier))

return results
```

# ═══════════════════════════════════════════════════════════════

# THRESHOLD FINDER

# ═══════════════════════════════════════════════════════════════

def find_breakeven_r(project: ClimateProject, E_base: float = 6.0,
subtotal: float = 13.7) -> Optional[float]:
“””
Find the recycling fraction r at which the funding’s
own CO2 emissions equal the project’s claimed annual
sequestration.

```
If claimed = 0 (SAI), returns 0.0 (always net negative).
If no breakeven exists, returns None.
"""
if project.claimed_annual_CO2_tonnes <= 0:
    return 0.0  # no sequestration claim, always net negative

CO2_per_MJ_kg = 0.070
target_CO2_kg = project.claimed_annual_CO2_tonnes * 1000.0  # tonnes to kg

# Use midpoint annual budget
annual_USD = (project.annual_budget_low_USD + project.annual_budget_high_USD) / 2.0

# E_total = subtotal / (1-r)
# CO2 = annual_USD * E_total * CO2_per_MJ_kg
# Set CO2 = target_CO2_kg, solve for r:
# target = annual_USD * subtotal / (1-r) * CO2_per_MJ_kg
# (1-r) = annual_USD * subtotal * CO2_per_MJ_kg / target
# r = 1 - (annual_USD * subtotal * CO2_per_MJ_kg / target)

denominator = target_CO2_kg
numerator = annual_USD * subtotal * CO2_per_MJ_kg

ratio = numerator / denominator
r_breakeven = 1.0 - ratio

if r_breakeven < 0.0:
    return None  # funding emissions exceed claimed benefit even at r=0
elif r_breakeven >= 1.0:
    return None  # impossible to reach breakeven
else:
    return r_breakeven
```

# ═══════════════════════════════════════════════════════════════

# NEGATIVE EROI DETECTOR

# ═══════════════════════════════════════════════════════════════

def check_negative_eroi(layer_r_values: List[float]) -> dict:
“””
Check if any overhead layer has r >= 1.0,
meaning it consumes more energy than the
base activity it supports.

```
This is the "intermediaries consume more than
the project receives" condition.
"""
total_r = sum(layer_r_values)
max_r = max(layer_r_values) if layer_r_values else 0.0

return {
    "any_layer_exceeds_1": max_r >= 1.0,
    "total_r_exceeds_1": total_r >= 1.0,
    "max_layer_r": max_r,
    "total_r": total_r,
    "verdict": (
        "NEGATIVE EROI: overhead exceeds project energy"
        if total_r >= 1.0
        else "Positive EROI at layer level (recursive effects may still push negative)"
    ),
}
```

# ═══════════════════════════════════════════════════════════════

# FULL SIMULATION

# ═══════════════════════════════════════════════════════════════

def run_full_audit():
“”“Run complete audit across all scenarios and projects.”””

```
results = {}

for proj_key, project in PROJECTS.items():
    results[proj_key] = {}
    for scen_key, scenario in SCENARIOS.items():
        audit = compute_project_audit(project, scenario)
        results[proj_key][scen_key] = audit

return results
```

# ═══════════════════════════════════════════════════════════════

# PRINT ENGINE

# ═══════════════════════════════════════════════════════════════

def print_dollar_anatomy():
“”“Print the full energy anatomy of a dollar.”””

```
print()
print("=" * 65)
print("THE ENERGY ANATOMY OF A DOLLAR")
print("Recursive metabolic cost of financial system overhead")
print("=" * 65)
print()

for scen_key, scenario in SCENARIOS.items():
    result = compute_dollar_energy(scenario)
    
    print(f"  {scenario.name}")
    print(f"  {'─' * 55}")
    print(f"    Base energy:              {result['E_base_MJ']:>8.1f} MJ")
    
    if scenario.layer_positions != "none":
        for lname, ldata in result["layer_breakdown"].items():
            if ldata["MJ_added"] > 0:
                print(f"    + {lname:20s}      {ldata['MJ_added']:>8.2f} MJ  (r={ldata['r_fraction']:.2f})")
        
        print(f"    {'─' * 40}")
        print(f"    Subtotal:                 {result['subtotal_before_recursion_MJ']:>8.1f} MJ")
        print(f"    Recursive r:              {result['recursive_r']:>8.2f}")
        print(f"    Recursive multiplier:     {result['recursive_multiplier']:>8.2f}x")
    
    if math.isinf(result["total_MJ_per_dollar"]):
        print(f"    TOTAL:                    DIVERGENT (infinite)")
    else:
        print(f"    TOTAL:                    {result['total_MJ_per_dollar']:>8.1f} MJ per dollar")
    
    print(f"    Overall multiplier:       {result['overall_multiplier']:>8.1f}x base energy")
    print()
```

def print_geometric_series():
“”“Print the geometric series table showing divergence.”””

```
print()
print("=" * 65)
print("GEOMETRIC SERIES: RECYCLING FRACTION vs TOTAL ENERGY")
print("E_base = 6.0 MJ, Subtotal = 13.7 MJ (typical climate finance)")
print("=" * 65)
print()
print(f"    {'r':>6s}  {'E_total (MJ)':>14s}  {'Multiplier':>12s}  {'Status'}")
print(f"    {'─'*6}  {'─'*14}  {'─'*12}  {'─'*20}")

for r, total, mult in explore_recycling_fraction():
    if math.isinf(total):
        print(f"    {r:>6.2f}  {'DIVERGENT':>14s}  {'INFINITE':>12s}  SYSTEM IS NET SINK")
    else:
        status = ""
        if r >= 0.7:
            status = "← carbon speculation"
        elif r >= 0.5:
            status = "← typical climate finance"
        elif r >= 0.3:
            status = "← efficient finance"
        print(f"    {r:>6.2f}  {total:>14.1f}  {mult:>12.1f}x  {status}")

print()
print("  As r → 1.0, energy cost → infinity.")
print("  The financial system's own metabolism")
print("  consumes the project's energy budget.")
print()
```

def print_project_audits():
“”“Print full audits for all project/scenario combinations.”””

```
results = run_full_audit()

for proj_key, project in PROJECTS.items():
    print()
    print("=" * 65)
    print(f"PROJECT: {project.name.upper()}")
    print(f"  {project.description}")
    print("=" * 65)
    
    if project.claimed_annual_CO2_tonnes > 0:
        print(f"  Claimed annual sequestration: {project.claimed_annual_CO2_tonnes:,.0f} tonnes CO₂")
    else:
        print(f"  Claimed sequestration: NONE (masking only)")
    print()
    
    for scen_key, scenario in SCENARIOS.items():
        audit = results[proj_key][scen_key]
        de = audit["dollar_energy"]
        
        print(f"  Scenario: {scenario.name}")
        print(f"  {'─' * 55}")
        
        if math.isinf(de["total_MJ_per_dollar"]):
            print(f"    Energy per dollar: DIVERGENT")
            print(f"    Multiplier: INFINITE")
        else:
            print(f"    Energy per dollar: {de['total_MJ_per_dollar']:.1f} MJ  ({de['overall_multiplier']:.1f}x)")
        
        # Annual budget emissions
        for label in ["annual_budget_low", "annual_budget_high"]:
            pc = audit["project_costs"][label]
            tag = "low" if "low" in label else "high"
            
            if math.isinf(pc["CO2_tonnes"]):
                print(f"    Annual budget ({tag}): ${pc['USD']/1e6:.0f}M → INFINITE CO₂")
            else:
                print(f"    Annual budget ({tag}): ${pc['USD']/1e6:.0f}M → "
                      f"{pc['energy_TJ']:.0f} TJ → "
                      f"{pc['CO2_tonnes']:,.0f} t CO₂")
        
        # Comparison to claimed
        if project.claimed_annual_CO2_tonnes > 0:
            frac = audit["funding_CO2_as_fraction_of_claimed"]
            for bkey, blabel in [("low_budget", "low"), ("high_budget", "high")]:
                f = frac[bkey]
                if math.isinf(f):
                    print(f"    Funding CO₂ ({blabel} budget) = INFINITE × claimed")
                else:
                    print(f"    Funding CO₂ ({blabel} budget) = {f:.2f}x claimed annual sequestration")
                    if f >= 1.0:
                        print(f"      ██ FUNDING ALONE EMITS MORE THAN PROJECT CLAIMS ██")
        
        print()
    
    # Breakeven analysis
    r_break = find_breakeven_r(project)
    if project.claimed_annual_CO2_tonnes > 0:
        if r_break is None:
            print(f"  BREAKEVEN: Funding emissions EXCEED claimed benefit")
            print(f"             at ALL recycling fractions. No r makes this work.")
        elif r_break <= 0.0:
            print(f"  BREAKEVEN: r = 0 (only direct action, zero overhead)")
        else:
            print(f"  BREAKEVEN r = {r_break:.3f}")
            print(f"    Funding CO₂ = claimed CO₂ when r = {r_break:.3f}")
            if r_break < 0.3:
                print(f"    This requires financial efficiency that DOES NOT EXIST")
                print(f"    in any known climate finance structure.")
    else:
        print(f"  BREAKEVEN: N/A — project claims no sequestration.")
        print(f"  All funding emissions are pure additional cost.")
    
    print()
```

def print_negative_eroi_analysis():
“”“Print EROI analysis for each scenario.”””

```
print()
print("=" * 65)
print("NEGATIVE EROI DETECTION")
print("Does any layer consume more energy than it processes?")
print("=" * 65)
print()

for pos_label, pos in [("Conservative", "low"), ("Mid-range", "mid"), ("Extractive", "high")]:
    E_base = 6.0
    r_values = [layer_energy(layer, pos, E_base) / E_base for layer in OVERHEAD_LAYERS]
    names = [layer.name for layer in OVERHEAD_LAYERS]
    
    result = check_negative_eroi(r_values)
    
    print(f"  {pos_label} case:")
    for name, r in zip(names, r_values):
        flag = " ← EXCEEDS 1.0" if r >= 1.0 else ""
        print(f"    {name:20s}  r = {r:.3f}{flag}")
    print(f"    {'─' * 40}")
    print(f"    Total r:            {result['total_r']:.3f}")
    print(f"    Verdict:            {result['verdict']}")
    print()
```

def print_verdicts():
“”“Print the thermodynamic verdicts.”””

```
print()
print("=" * 65)
print("THERMODYNAMIC VERDICTS")
print("=" * 65)
print()
print("  1. The financial system is a heat engine that converts")
print("     primary energy into claims on future energy.")
print()
print("  2. When you route a dollar through this engine to fund")
print("     a climate project, the engine's own thermal losses")
print("     exceed the project's energetic benefit in most")
print("     configurations.")
print()
print("  3. The margin stack (r₂) can exceed 1.0 in extractive")
print("     configurations. This is the negative EROI condition:")
print("     intermediaries consume more energy per dollar than")
print("     the project receives.")
print()
print("  4. The recursive nature of overhead (each layer generates")
print("     economic activity subject to all other layers) creates")
print("     a geometric series that approaches divergence as the")
print("     financial system becomes more complex.")
print()
print("  5. The only climate interventions with closed energy")
print("     budgets are:")
print()
print("       a. Direct action (no financial intermediation)")
print("       b. Negative cost (stop subsidizing extraction)")
print("       c. Regulatory prohibition (no transaction needed)")
print()
print("  6. Everything else — every carbon credit, every green")
print("     bond, every climate fund — carries an energy debt")
print("     that compounds faster than the project's energy")
print("     dividend.")
print()
print("  7. The dollar is not neutral. The dollar is a unit of")
print("     extraction wrapped in abstraction layers designed")
print("     to make the extraction invisible.")
print()
print("=" * 65)
print("  Leave the forest standing. It already works.")
print("  It doesn't need funding. It doesn't need a pitch deck.")
print("  It just needs to not be cut down.")
print("  But 'don't cut it down' has no revenue model.")
print("  And that's the whole problem.")
print("=" * 65)
print()
```

# ═══════════════════════════════════════════════════════════════

# ENTRY POINT

# ═══════════════════════════════════════════════════════════════

if **name** == “**main**”:
print_dollar_anatomy()
print_geometric_series()
print_negative_eroi_analysis()
print_project_audits()
print_verdicts()
