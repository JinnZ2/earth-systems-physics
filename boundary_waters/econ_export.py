“””
Export econ cascade results to CSV.
“””
import csv
from econ_cascade import run_econ_cascade

SCENARIOS = [“protected”, “proceed”, “tailings_failure”]

FIELDS = [
“year”,
# property
“depreciation_frac”, “residential_loss_usd”, “commercial_loss_usd”,
“total_property_loss_usd”, “annual_tax_base_loss”, “superfund_flag”,
# health
“silicosis_cases”, “fibrosis_cases”, “hearing_loss_cases”,
“fatal_injuries”, “kids_neuro_impaired”, “adult_cancer_cases”,
“worker_health_cost_usd”, “community_health_cost_usd”, “total_health_cost_usd”,
# ltc
“ltc_annual_cases”, “ltc_annual_cost_usd”, “ltc_medicaid_cost_usd”,
“ltc_capacity_shortfall”, “families_displaced_ltc”,
# community
“water_upgrade_capex_usd”, “water_om_annual_usd”, “em_annual_usd”,
“sped_annual_usd”, “ph_surveillance_usd”, “mental_health_usd”,
“municipal_annual_usd”, “tax_revenue_loss_usd”, “effective_deficit_usd”,
“fiscal_stress_ratio”, “fiscal_collapse_flag”,
# state
“medicaid_annual_usd”, “unfunded_cleanup_usd”, “perpetual_treatment_usd”,
“tourism_tax_loss_usd”, “ihs_obligation_usd”, “state_annual_load_usd”,
# infrastructure
“power_demand_mw”, “grid_reserve_margin”, “grid_stress_flag”,
“transmission_capex_usd”, “ratepayer_burden_usd”,
“water_stress_ratio”, “water_conflict_flag”,
“road_maint_annual_usd”, “ems_response_time_min”,
# physical refs
“sulfate_mg_l”, “wells_contaminated”, “forced_migrants”, “tailings_failed”,
]

def export_all():
for key in SCENARIOS:
hist = run_econ_cascade(scenario=key)
path = f”/home/claude/bwca_sim/econ_{key}.csv”
with open(path, “w”, newline=””) as f:
w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction=“ignore”)
w.writeheader()
for row in hist:
w.writerow(row)
print(f”  wrote {path}”)

if **name** == “**main**”:
export_all()
