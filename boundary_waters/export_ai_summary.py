# boundary_waters/export_ai_summary.py
# earth-systems-physics
# CC0 — No Rights Reserved
"""
Generate ai_summary.json for the boundary_waters folder.

One file, one read, full context. Any AI agent can fetch this
without running Python, without importing modules, without
sys.path manipulation. Contains all findings, falsifiable claims,
headline numbers, extraction topology, and sources.

Usage:
    cd boundary_waters && python export_ai_summary.py
    # or from repo root:
    python boundary_waters/export_ai_summary.py
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def build_summary():
    from cascade import run_cascade
    from secondary_effects import (
        run_secondary_cascade, CommunityLoopState,
        ELY_OUTFITTERS, LODGE_RESORT_COUNT,
    )
    from climate_boundary import (
        CLIMATE_TRENDS, BREAKS, CLIMATE_CLAIMS, CLIMATE_SCORING,
        WILDFIRE_TAILINGS, BASE_RATE_PROBLEM,
    )
    from extraction_topology import (
        OUTFLOWS, STAYS_BEHIND, EXTRACTION_LOOP, NET_TRANSFERS,
        EXTRACTION_SCORING,
    )
    from displacement_sources import (
        WELL_ANALOGS, FOOD_ANALOGS, PARAMETER_DERIVATION,
        INDIGENOUS_FOOD_INSECURITY, INDIGENOUS_COMPOUNDING,
    )

    # Run simulations
    scenarios = {}
    for name in ("protected", "proceed", "tailings_failure"):
        hist = run_cascade(seed=42, scenario=name)
        scenarios[name] = {
            "peak_sulfate_mg_l": round(max(r["sulfate_mg_l"] for r in hist), 1),
            "peak_forced_migrants": max(r["forced_migrants"] for r in hist),
            "peak_wells_contaminated": max(r["wells_contaminated"] for r in hist),
            "peak_forest_acres_lost": round(max(r["forest_acres_lost"] for r in hist)),
            "peak_liability_usd": max(r["liability_npv_usd"] for r in hist),
            "peak_net_jobs": min(r["net_jobs"] for r in hist),
        }

    # Secondary effects for proceed + tailings_failure
    for scenario_name in ("proceed", "tailings_failure"):
        hist = run_cascade(seed=42, scenario=scenario_name)
        state = CommunityLoopState(population=12400.0)
        for yr in range(500):
            h = hist[yr]
            sec = run_secondary_cascade(
                yr, h["mine_active"], max(0, yr - 5),
                h["cumulative_waste_Mt"] * 1e6, h, state, 12400.0,
            )
            state = sec["_community_state"]
        scenarios[scenario_name]["secondary"] = {
            "final_population": round(state.population),
            "school_open": sec["loop_school_open"],
            "hospital_open": sec["loop_hospital_open"],
            "insurance_available": sec["loop_insurance_available"],
            "outfitters_surviving": sec["biz_outfitters_surviving"],
            "outfitters_total": ELY_OUTFITTERS,
            "lodges_surviving": sec["biz_lodges_surviving"],
            "lodges_total": LODGE_RESORT_COUNT,
            "bank_failure_risk": sec["bank_bank_failure_risk"],
            "credit_contraction_pct": round(sec["bank_credit_contraction_frac"] * 100),
            "peatland_ch4_delta_co2e": round(sec["peat_co2e_tonnes_yr"]),
            "cultural_transmission_viable": sec["cultural_transmission_viable"],
        }

    # Assemble
    summary = {
        "format_version": "1.0",
        "generated_by": "boundary_waters/export_ai_summary.py",
        "license": "CC0",
        "purpose": (
            "Machine-readable summary of the BWCA sulfide-mine cascade "
            "simulation. One file, one read, full context for any AI agent."
        ),

        "one_line_finding": (
            "Value exits the state as ore, revenue, and dividends within "
            "20 years. Cost stays as AMD, mercury, community collapse, "
            "and treaty liability for centuries. The measurement system "
            "that approved it is structurally blind to the majority of "
            "the actual cost."
        ),

        "scenarios": scenarios,

        "extraction_topology": {
            "composite_score_pct": 98,
            "causal_loop": {
                k: {kk: vv for kk, vv in v.items() if kk != "is_self_reinforcing" and kk != "is_external"}
                for k, v in EXTRACTION_LOOP.items()
            },
            "value_leaves_state": [
                {"name": f.name, "destination": f.destination, "duration": f.duration}
                for f in OUTFLOWS
            ],
            "cost_stays": [
                {"name": f.name, "duration": f.duration, "reversible": f.reversible}
                for f in STAYS_BEHIND
            ],
            "net_transfers": [
                {"category": t.category, "direction": t.net_direction,
                 "time_asymmetry": t.time_asymmetry, "falsifiable": t.falsifiable}
                for t in NET_TRANSFERS
            ],
        },

        "climate_boundary": {
            "trends_count": len(CLIMATE_TRENDS),
            "trends": [
                {"variable": t.variable, "direction": t.direction,
                 "confidence": t.confidence}
                for t in CLIMATE_TRENDS
            ],
            "mitigation_breaks_count": len(BREAKS),
            "breaks": [
                {"climate_shift": b.climate_shift,
                 "mitigation_affected": b.mitigation_affected,
                 "timescale": b.timescale_of_failure}
                for b in BREAKS
            ],
            "falsifiable_claims": [
                {"id": c.id, "claim": c.claim, "state": c.state}
                for c in CLIMATE_CLAIMS
            ],
        },

        "displacement_sources": {
            "well_analogs": [
                {"site": a.site, "departure_fraction": a.departure_fraction,
                 "timeframe_years": a.timeframe_years,
                 "population_before": a.population_before,
                 "population_after": a.population_after}
                for a in WELL_ANALOGS
            ],
            "food_analogs": [
                {"site": a.site, "contaminant": a.contaminant,
                 "notes": a.notes}
                for a in FOOD_ANALOGS
            ],
            "parameter_derivation": {
                k: {"value": v["value"], "analogs": v["analogs"]}
                for k, v in PARAMETER_DERIVATION.items()
            },
            "indigenous_food_insecurity": INDIGENOUS_FOOD_INSECURITY,
            "indigenous_compounding": INDIGENOUS_COMPOUNDING,
        },

        "scoring": {
            "extraction": EXTRACTION_SCORING,
            "climate": CLIMATE_SCORING,
        },

        "sources": [
            "US Forest Service 2022 Environmental Assessment (PLO 7917)",
            "USGS 2013 Twin Metals ore body assay",
            "Singer & Stumm 1970 (pyrite oxidation kinetics)",
            "MN Rule 7050.0224 (wild rice sulfate standard)",
            "Pastor et al. 2017 (wild rice sub-lethal effects)",
            "Boundary Waters Treaty of 1909 Art. IV",
            "Trail Smelter Arbitration 1941",
            "US Census (Picher OK, Flint MI, Hinkley CA)",
            "Lancet Planetary Health 2020 (Grassy Narrows mortality)",
            "UMN Climate Adaptation Partnership 2024-2025",
            "MN DNR State Climatology Office",
            "Fifth National Climate Assessment",
            "Frelich / UMN Center for Forest Ecology (biome transition)",
            "Ely Chamber of Commerce (22 outfitters, 250k visitors)",
            "Census 2023 (Ely workforce 1,706)",
            "GAO-13-71 (community bank CRE concentration)",
            "EPA brownfields/CRA (lending near contamination)",
            "ISO CGL pollution exclusion (standard since 1986)",
            "Minamata follow-up studies (3-generation Hg effects)",
            "CDC (Pb IQ loss, no safe level)",
            "Elk Valley BC / Teck Resources (selenium analog)",
        ],
    }

    return summary


def main():
    summary = build_summary()
    output_path = os.path.join(SCRIPT_DIR, "ai_summary.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    print(f"wrote {output_path} ({os.path.getsize(output_path):,} bytes)")


if __name__ == "__main__":
    main()
