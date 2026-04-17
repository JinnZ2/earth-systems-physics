"""
Extended cascade driver. Couples 6 new modules onto physical cascade.
Climate module creates feedback into chemistry (oxidation rate mult).
Wildfire re-releases accumulated Hg/Pb into air stream.
"""

from cascade import run_cascade
from extended_layers import (
climate_amplifier, lumber_layer, fish_consumption_layer,
air_quality_layer, wildfire_layer, port_layer_extended
)

def run_extended_cascade(scenario="proceed", seed=42):
    phys_history = run_cascade(scenario=scenario, seed=seed)
    ext_history = []

    for phys in phys_history:
        year = phys["year"]
        year_since_start = max(0, year - 5)   # mine start = yr 5

        # Climate runs on absolute year (time since 2026)
        climate = climate_amplifier(year)

        # Apply climate oxidation multiplier as post-hoc amplifier to
        # physical state (full closed-loop would require re-running
        # chemistry; approximation for visualization)
        phys_amplified = dict(phys)
        phys_amplified["sulfate_mg_l"] *= climate["oxidation_mult"]
        phys_amplified["methyl_hg_ng_l"] *= climate["oxidation_mult"]
        phys_amplified["hg_ng_l"] *= climate["oxidation_mult"]

        lumber = lumber_layer(phys_amplified, climate,
                              phys["mine_active"], year_since_start)
        fish   = fish_consumption_layer(phys_amplified, year_since_start)
        air    = air_quality_layer(phys_amplified, phys["mine_active"], climate)
        fire   = wildfire_layer(phys_amplified, lumber, climate, year)
        port   = port_layer_extended(phys_amplified, fish, air,
                                     phys["mine_active"], year)

        ext_history.append({
            "year": year,
            "scenario": scenario,
            **climate, **lumber, **fish, **air, **fire, **port,
            # keep physical refs
            "sulfate_mg_l":        phys_amplified["sulfate_mg_l"],
            "methyl_hg_ng_l":      phys_amplified["methyl_hg_ng_l"],
            "mine_active":         phys["mine_active"],
            "tailings_failed":     phys["tailings_failed"],
        })

    return ext_history

def summarize(hist, label):
    print(f"\n{'═'*82}")
    print(f"  EXTENDED CASCADE: {label}")
    print(f"{'═'*82}")
    snaps = [10, 25, 50, 100, 250, 499]
    print(f"{'Yr':>4} {'ΔT':>5} {'Lumb$B':>8} {'Fish_IQ':>9} "
          f"{'AirDeaths':>10} {'FireAcres':>10} {'Port$M':>9}")
    print("-" * 82)
    for yr in snaps:
        h = hist[yr]
        print(f"{yr:>4} "
              f"{h['delta_T_C']:>5.2f} "
              f"{h['total_lumber_loss_usd']/1e9:>8.2f} "
              f"{h['iq_loss_per_child']:>9.2f} "
              f"{h['cardio_deaths_yr']:>10.2f} "
              f"{h['expected_burn_acres_yr']:>10.0f} "
              f"{h['total_port_annual_cost_usd']/1e6:>9.1f}")

def peak_summary(hist, label):
    print(f"\n  {label}")
    print(f"    peak temp rise         : {max(h['delta_T_C'] for h in hist):.2f} °C")
    print(f"    peak oxidation mult    : {max(h['oxidation_mult'] for h in hist):.2f}×")
    print(f"    peak lumber loss       : ${max(h['total_lumber_loss_usd'] for h in hist)/1e9:.2f} B")
    print(f"    peak timber volume lost: {max(h['timber_volume_lost_m3'] for h in hist)/1e6:.2f} M m³")
    print(f"    peak lumber jobs lost  : {max(h['lumber_jobs_lost'] for h in hist):,}")
    print(f"    peak fish tissue Hg    : {max(h['fish_tissue_hg_mg_kg'] for h in hist):.3f} mg/kg  (advisory @0.3)")
    print(f"    peak Ojibwe RfD ratio  : {max(h['ojibwe_high_rfd_ratio'] for h in hist):.1f}× EPA limit")
    print(f"    peak IQ loss per child : {max(h['iq_loss_per_child'] for h in hist):.2f} points")
    print(f"    cumulative impaired kids: {max(h['cumulative_impaired_children'] for h in hist):,}")
    print(f"    peak SO2 emission      : {max(h['so2_tonnes_yr'] for h in hist):,.0f} t/yr")
    print(f"    peak PM2.5 emission    : {max(h['pm25_tonnes_yr'] for h in hist):,.0f} t/yr")
    print(f"    peak cardio deaths     : {max(h['cardio_deaths_yr'] for h in hist):.2f}/yr")
    print(f"    peak BWCA visibility   : {min(h['bwca_visibility_km'] for h in hist):.1f} km (threshold 135)")
    print(f"    peak burn acres        : {max(h['expected_burn_acres_yr'] for h in hist):,.0f}/yr")
    print(f"    peak tailings overrun  : {max(h['tailings_overrun_acres'] for h in hist):.1f} acres")
    print(f"    peak Hg re-released    : {max(h['hg_re_released_kg_yr'] for h in hist):.2f} kg/yr")
    print(f"    peak fire cost         : ${max(h['total_fire_cost_usd'] for h in hist)/1e6:.1f} M/yr")
    print(f"    peak port annual cost  : ${max(h['total_port_annual_cost_usd'] for h in hist)/1e6:.1f} M/yr")
    print(f"    peak port jobs lost    : {max(h['port_jobs_lost'] for h in hist):,}")
    print(f"    canadian refusal prob  : {max(h['canadian_refusal_prob'] for h in hist):.2f}")

if __name__ == "__main__":
    scenarios = [
        ("protected",        "Protected (withdrawal holds)"),
        ("proceed",          "CRA reversal -> mine operates"),
        ("tailings_failure", "Mine + tailings dam failure"),
    ]
    for key, label in scenarios:
        hist = run_extended_cascade(scenario=key)
        summarize(hist, label)

    print(f"\n{'═'*82}")
    print("  PEAK IMPACT (500-yr horizon)")
    print(f"{'═'*82}")
    for key, label in scenarios:
        hist = run_extended_cascade(scenario=key)
        peak_summary(hist, label)
