“””
Export extended cascade scenarios as CSV.
“””
import csv
from extended_cascade import run_extended_cascade

SCENARIOS = [“protected”, “proceed”, “tailings_failure”]

FIELDS = [
“year”, “scenario”,
# climate
“delta_T_C”, “oxidation_mult”, “precip_mult”, “extreme_event_mult”,
“dam_risk_mult”, “fire_season_days”, “drought_mult”, “flood_mult”,
# lumber
“acid_load”, “growth_loss_frac”, “ca_depletion_frac”, “mycorrhizal_dead”,
“timber_volume_lost_m3”, “pulp_grade_rejected”,
“direct_timber_loss_usd”, “pulp_grade_loss_usd”, “total_lumber_loss_usd”,
“lumber_jobs_lost”,
# fish
“fish_tissue_hg_mg_kg”, “state_avg_rfd_ratio”, “ojibwe_mean_rfd_ratio”,
“ojibwe_high_rfd_ratio”, “iq_loss_per_child”, “cumulative_impaired_children”,
“fish_advisory_triggered”, “harvest_displacement_cost_usd”,
“treaty_rights_violation”,
# air
“so2_tonnes_yr”, “pm25_tonnes_yr”, “pm10_tonnes_yr”, “hg_atmospheric_kg_yr”,
“asthma_attacks_yr”, “copd_hospitalizations_yr”, “cardio_deaths_yr”,
“air_quality_health_cost_usd”, “bwca_visibility_km”, “class_i_violation”,
“soy_yield_loss_frac”,
# fire
“annual_fire_prob_mult”, “expected_burn_acres_yr”, “tailings_overrun_acres”,
“hg_re_released_kg_yr”, “firefighters_exposed”, “firefighter_cancer_excess”,
“residents_evacuated”, “structures_lost”, “suppression_cost_usd”,
“evacuation_cost_usd”, “structure_cost_usd”, “recreation_closure_cost”,
“total_fire_cost_usd”,
# port
“hg_loading_increase”, “intake_upgrade_required”, “intake_upgrade_capex_usd”,
“annual_dredge_cost_usd”, “canadian_refusal_prob”, “backhaul_loss_usd”,
“fishing_advisory”, “fishing_jobs_lost”, “fishing_revenue_loss_usd”,
“iron_revenue_at_risk_usd”, “ballast_surcharge_usd”, “port_jobs_lost”,
“total_port_annual_cost_usd”,
# physical refs
“sulfate_mg_l”, “methyl_hg_ng_l”, “mine_active”, “tailings_failed”,
]

def export_all():
for key in SCENARIOS:
hist = run_extended_cascade(scenario=key)
path = f”/home/claude/bwca_sim/extended_{key}.csv”
with open(path, “w”, newline=””) as f:
w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction=“ignore”)
w.writeheader()
for row in hist:
w.writerow(row)
print(f”  wrote {path}”)

if **name** == “**main**”:
export_all()
