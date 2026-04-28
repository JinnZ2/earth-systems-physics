“””
RUN FULL STACK
Execute all modules, produce honest output with uncertainty bands.
No narrative. Just numbers and flagged unknowns.
“””

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(**file**), “..”, “src”))

import random
from wetland_core import PARAMS as W_P, carbon_storage_rate, methane_balance
from marine_core import PARAMS_MARINE, marine_drawdown_per_m2
from boundary_conditions import permafrost_net_benefit
from spike_mitigation import combined_spike_reduction, INTERVENTIONS
from adaptive_layer import adaptive_layer_net_carbon
from global_potential import terrestrial_potential, marine_potential, EXTENT
from geological_vector import erw_drawdown, ERW_PARAMS

def monte_carlo(n=2000):
“”“Sample uncertainty ranges. Return distribution of total drawdown.”””
samples = []
for _ in range(n):
# wetland - sample param ranges
W = random.uniform(0.80, 0.95)
Rp = random.uniform(0.4, 0.8)
peat_C = carbon_storage_rate(W, Rp, W_P) * EXTENT[“peatlands_drained_km2”][“value”] * 1e6 / 1e12
other_C = carbon_storage_rate(W*0.95, Rp*0.85, W_P) * (
(EXTENT[“wetlands_drained_km2”][“value”] - EXTENT[“peatlands_drained_km2”][“value”]) * 1e6
) / 1e12

```
    # marine
    kelp_per_m2 = (random.uniform(*PARAMS_MARINE["kelp_NPP"]["range"]) *
                   random.uniform(*PARAMS_MARINE["f_export_deep"]["range"]) *
                   random.uniform(*PARAMS_MARINE["millennial_seq"]["range"]))
    kelp_C = kelp_per_m2 * 2e6 * 1e6 / 1e12   # 2M km2 restoration

    # permafrost
    perm = permafrost_net_benefit(
        area_km2=random.uniform(300_000, 800_000),
        density_per_km2=random.uniform(8, 12),
        species_mix={"reindeer":0.4,"bison":0.2,"musk_ox":0.2,"yakutian_horse":0.2},
        warming_avoided_GtC=random.uniform(0.5, 1.2),
    )
    perm_C = perm["net_benefit_CO2eq_Gt_yr"] * (12/44)

    # adaptive
    adapt = adaptive_layer_net_carbon(area_ha=random.uniform(50e6, 500e6), years_operated=20)
    adapt_C = adapt["annual_drawdown_t_CO2"] * (12/44) / 1e9   # t -> Gt C

    # geological vector (ERW) - near-term realistic by year 10
    erw_area = ERW_PARAMS["deployable_area_ha"]["value"] * random.uniform(0.05, 0.20)
    erw = erw_drawdown(
        area_ha=erw_area,
        rate_t_ha_yr=random.uniform(*ERW_PARAMS["application_rate_t_per_ha_yr"]["range"]),
        acceleration_factor=random.uniform(*ERW_PARAMS["weathering_acceleration_acidic_moist"]["range"]),
        co2_per_t_basalt=random.uniform(*ERW_PARAMS["CO2_removed_per_tonne_basalt"]["range"]) / 3.0,
    )
    erw_C = erw["C_removed_Gt_yr"]

    total = peat_C + other_C + kelp_C + perm_C + adapt_C + erw_C
    samples.append(total)

samples.sort()
return {
    "n":           n,
    "p05":         samples[int(0.05*n)],
    "p25":         samples[int(0.25*n)],
    "p50":         samples[int(0.50*n)],
    "p75":         samples[int(0.75*n)],
    "p95":         samples[int(0.95*n)],
    "min":         samples[0],
    "max":         samples[-1],
}
```

def methane_spike_distribution():
“”“How much spike reduction does the intervention stack actually deliver?”””
return combined_spike_reduction(list(INTERVENTIONS.keys()))

if **name** == “**main**”:
print(”=” * 70)
print(“BIOCARBON STACK - FULL RUN WITH UNCERTAINTY”)
print(”=” * 70)

```
print("\nGLOBAL DRAWDOWN POTENTIAL (Gt C / yr)")
print("-" * 70)
mc = monte_carlo(n=3000)
print(f"  5th percentile:    {mc['p05']:.2f}")
print(f"  25th percentile:   {mc['p25']:.2f}")
print(f"  Median:            {mc['p50']:.2f}")
print(f"  75th percentile:   {mc['p75']:.2f}")
print(f"  95th percentile:   {mc['p95']:.2f}")
print(f"  Range:             {mc['min']:.2f} to {mc['max']:.2f}")

print("\nMETHANE SPIKE MITIGATION (4-intervention stack)")
print("-" * 70)
sp = methane_spike_distribution()
print(f"  Worst case reduction:   {sp['worst_case_reduction']*100:.0f}%")
print(f"  Central reduction:      {sp['central_reduction']*100:.0f}%")
print(f"  Best case reduction:    {sp['best_case_reduction']*100:.0f}%")

print("\nFRACTION OF ANTHROPOGENIC FLUX OFFSET")
print("-" * 70)
anthro = 10.0
growth = 5.3
print(f"  Median offset of emissions ({anthro} Gt C/yr): {mc['p50']/anthro*100:.0f}%")
print(f"  Median offset of growth    ({growth} Gt C/yr): {mc['p50']/growth*100:.0f}%")
print(f"  Range as fraction of growth: {mc['p05']/growth*100:.0f}% to {mc['p95']/growth*100:.0f}%")

print("\nWHAT THIS DOES NOT DO")
print("-" * 70)
print("  - Replace emissions reduction. Drawdown plus reduction, not drawdown alone.")
print("  - Solve governance. Who manages what land remains a hard constraint.")
print("  - Account for warming already locked in past 1.5C.")
print("  - Predict tipping point cascades (Amazon dieback, AMOC, etc).")
print()
print("WHAT THIS DOES DO")
print("-" * 70)
print("  - Quantify the proven biological capacity.")
print("  - Surface the buffer-of-buffer dependencies.")
print("  - Hold open the option space without collapsing to one answer.")
print("  - Give honest uncertainty bands, not point estimates.")
```
