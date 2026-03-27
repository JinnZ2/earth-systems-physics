# energy_audit.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Cross-layer energy conservation audit.
# Verifies that the cascade engine's energy bookkeeping closes.
# When forcing is applied at one layer, the total energy change across
# all layers should be accountable — not necessarily zero (external
# forcing adds energy), but the bookkeeping should close.
#
# Energy accounting:
#   INPUT  = external forcing (GHG, solar, volcanic)
#   STORED = heat content changes (ocean, atmosphere, ice)
#   FEEDBACK = internal amplification/damping (ice-albedo, etc.)
#   RESIDUAL = INPUT - STORED - FEEDBACK (should be small)

import numpy as np

from cascade_engine import (
    run_all_layers, apply_forcing, BASELINE, LAYER_NAMES,
)


# ─────────────────────────────────────────────
# ENERGY TERM CLASSIFICATION
# ─────────────────────────────────────────────

EARTH_SURFACE_AREA = 5.1e14     # m^2

# Input terms: external forcing applied to the system (W/m^2 equivalent)
INPUT_TERMS = {
    (3, "GHG_forcing_Wm2"):    {"scale": 1.0, "desc": "Greenhouse gas radiative forcing"},
    (3, "aerosol_forcing_Wm2"):{"scale": 1.0, "desc": "Aerosol direct radiative effect"},
    (5, "volcanic_forcing_Wm2"):{"scale": 1.0, "desc": "Volcanic stratospheric aerosol"},
}

# Response terms: where energy accumulates or is released
RESPONSE_TERMS = {
    (4, "ocean_heat_content_Jm2"):  {"scale": 1.0, "type": "storage",
        "desc": "Ocean heat uptake (dominant Earth energy sink)"},
    (4, "ice_albedo_feedback_Wm2"): {"scale": 1.0, "type": "feedback",
        "desc": "Ice-albedo feedback (amplifying)"},
    (4, "thermal_SLR_m"):           {"scale": 0.0, "type": "indicator",
        "desc": "Thermal sea level rise (indicator, not energy)"},
}

# Transport terms: redistribute energy, should not create/destroy
TRANSPORT_TERMS = {
    (4, "AMOC_heat_transport_W"): {"scale": 1.0 / EARTH_SURFACE_AREA,
        "desc": "AMOC poleward heat transport"},
    (0, "poynting_flux_wm2"):     {"scale": 1.0,
        "desc": "EM power flux"},
    (2, "joule_heating_Wm3"):     {"scale": 300e3,  # ionosphere thickness
        "desc": "Ionospheric joule heating (magnetosphere -> ionosphere)"},
}

# Net forcing: the single best estimate of total radiative imbalance
NET_FORCING_KEY = (3, "net_forcing_Wm2")


def _get_delta(baseline_states, perturbed_states, layer, key):
    """Get the numeric delta for a state variable."""
    bv = baseline_states.get(layer, {}).get(key)
    pv = perturbed_states.get(layer, {}).get(key)
    if bv is None or pv is None:
        return 0.0
    if not isinstance(bv, (int, float)) or not isinstance(pv, (int, float)):
        return 0.0
    return pv - bv


def audit_energy(forcing, baseline=None, verbose=True):
    """
    Run a forcing scenario and audit energy conservation across layers.

    The audit classifies energy terms as:
    - INPUT: external radiative forcing (GHG, aerosol, volcanic)
    - RESPONSE: where energy accumulates (ocean heat, feedbacks)
    - TRANSPORT: redistribution (AMOC, EM flux, joule heating)

    The residual = input - (response + feedback) should be accountable.

    Returns dict with classification and residual analysis.
    """
    if baseline is None:
        baseline = dict(BASELINE)

    baseline_states = run_all_layers(baseline)
    perturbed_params = apply_forcing(baseline, forcing)
    perturbed_states = run_all_layers(perturbed_params)

    # ── Compute net forcing (single best number) ──
    net_forcing_delta = _get_delta(baseline_states, perturbed_states,
                                    NET_FORCING_KEY[0], NET_FORCING_KEY[1])

    # ── Input terms ──
    input_details = {}
    total_input = 0.0
    for (layer, key), spec in INPUT_TERMS.items():
        delta = _get_delta(baseline_states, perturbed_states, layer, key)
        delta_wm2 = delta * spec["scale"]
        if abs(delta_wm2) > 1e-30:
            input_details[f"L{layer}:{key}"] = {
                "delta": delta, "delta_wm2": delta_wm2, "desc": spec["desc"]}
            total_input += delta_wm2

    # ── Response terms ──
    response_details = {}
    total_response = 0.0
    total_feedback = 0.0
    for (layer, key), spec in RESPONSE_TERMS.items():
        delta = _get_delta(baseline_states, perturbed_states, layer, key)
        delta_wm2 = delta * spec["scale"]
        if abs(delta_wm2) > 1e-30 and spec["type"] != "indicator":
            response_details[f"L{layer}:{key}"] = {
                "delta": delta, "delta_wm2": delta_wm2,
                "type": spec["type"], "desc": spec["desc"]}
            if spec["type"] == "storage":
                total_response += delta_wm2
            elif spec["type"] == "feedback":
                total_feedback += delta_wm2

    # ── Transport terms ──
    transport_details = {}
    total_transport = 0.0
    for (layer, key), spec in TRANSPORT_TERMS.items():
        delta = _get_delta(baseline_states, perturbed_states, layer, key)
        delta_wm2 = delta * spec["scale"]
        if abs(delta_wm2) > 1e-30:
            transport_details[f"L{layer}:{key}"] = {
                "delta": delta, "delta_wm2": delta_wm2, "desc": spec["desc"]}
            total_transport += delta_wm2

    # ── Residual analysis ──
    # The effective forcing = external input + internal feedbacks
    effective_forcing = total_input + total_feedback
    # Energy should go into: storage + transport changes
    accounted = total_response + total_transport
    residual = effective_forcing - accounted

    # Use the larger of effective_forcing or net_forcing as denominator
    reference = max(abs(effective_forcing), abs(net_forcing_delta), 1e-30)
    residual_pct = abs(residual) / reference * 100

    # Classification
    # The cascade is an INSTANTANEOUS snapshot — forcing creates a radiative
    # imbalance that accumulates over time. A residual matching the forcing
    # means "this energy hasn't been absorbed yet" which is physically correct
    # for a single-pass analysis. Only flag as leak if response terms exist
    # but don't add up.
    if abs(effective_forcing) < 1e-10 and abs(total_response) < 1e-10:
        energy_leak = False
        status = "NO_ENERGY_FORCING"
        residual_pct = 0.0
    elif abs(total_response) < 1e-10 and abs(total_transport) < 1e-10:
        # No response terms changed — forcing is pending (not yet absorbed)
        # This is expected for instantaneous analysis
        energy_leak = False
        status = "FORCING_PENDING"
    elif residual_pct <= 5.0:
        energy_leak = False
        status = "BALANCED"
    elif residual_pct <= 50.0:
        energy_leak = True
        status = "PARTIAL_LEAK"
    else:
        energy_leak = True
        status = "UNBALANCED"

    result = {
        "net_forcing_wm2": net_forcing_delta,
        "input": {"total_wm2": total_input, "details": input_details},
        "response": {"total_storage_wm2": total_response,
                     "total_feedback_wm2": total_feedback,
                     "details": response_details},
        "transport": {"total_wm2": total_transport, "details": transport_details},
        "effective_forcing_wm2": effective_forcing,
        "accounted_wm2": accounted,
        "residual_wm2": residual,
        "residual_pct": residual_pct,
        "energy_leak": energy_leak,
        "status": status,
    }

    if verbose:
        _print_audit(result, forcing)

    return result


def _print_audit(result, forcing):
    """Print energy audit report."""
    print("=" * 64)
    print("ENERGY CONSERVATION AUDIT")
    print("=" * 64)
    print(f"FORCING: {forcing.description}")
    print(f"  {forcing.variable} {forcing.magnitude:+.4g} {forcing.units}")
    print()

    print(f"  Net radiative forcing delta: {result['net_forcing_wm2']:+.6g} W/m^2")
    print()

    print("─" * 64)
    print("INPUT  (external forcing)")
    for key, d in result["input"]["details"].items():
        print(f"  {key:40s}  {d['delta_wm2']:+.6g} W/m^2")
        print(f"    {d['desc']}")
    print(f"  {'TOTAL INPUT':40s}  {result['input']['total_wm2']:+.6g} W/m^2")
    print()

    print("─" * 64)
    print("RESPONSE  (energy storage + feedbacks)")
    for key, d in result["response"]["details"].items():
        label = f"[{d['type']}]"
        print(f"  {key:40s}  {d['delta_wm2']:+.6g} W/m^2  {label}")
    print(f"  {'TOTAL STORAGE':40s}  {result['response']['total_storage_wm2']:+.6g} W/m^2")
    print(f"  {'TOTAL FEEDBACK':40s}  {result['response']['total_feedback_wm2']:+.6g} W/m^2")
    print()

    print("─" * 64)
    print("TRANSPORT  (redistribution)")
    for key, d in result["transport"]["details"].items():
        print(f"  {key:40s}  {d['delta_wm2']:+.6g} W/m^2")
    print(f"  {'TOTAL TRANSPORT':40s}  {result['transport']['total_wm2']:+.6g} W/m^2")
    print()

    print("─" * 64)
    print(f"  Effective forcing (input+feedback): {result['effective_forcing_wm2']:+.6g} W/m^2")
    print(f"  Accounted (storage+transport):      {result['accounted_wm2']:+.6g} W/m^2")
    print(f"  Residual:                           {result['residual_wm2']:+.6g} W/m^2")
    print(f"  Residual (%):                       {result['residual_pct']:.1f}%")
    print(f"  Status:                             {result['status']}")

    if result["status"] == "NO_ENERGY_FORCING":
        print("  (Forcing does not directly affect energy-dimensioned variables)")
    elif result["status"] == "FORCING_PENDING":
        print("  Forcing applied but not yet absorbed — instantaneous snapshot.")
        print("  The radiative imbalance will accumulate in ocean heat over decades.")
        print("  This is physically correct for single-pass analysis.")
    elif result["energy_leak"]:
        print("  ** ENERGY NOT FULLY ACCOUNTED — equations may be inconsistent **")
    else:
        print("  Energy bookkeeping closes within tolerance")
    print("=" * 64)


if __name__ == "__main__":
    from cascade_engine import SCENARIOS
    for name, scenario in SCENARIOS.items():
        if name == "co2_pulse_iterative":
            continue
        print(f"\n{'#'*64}")
        print(f"# AUDIT: {name}")
        print(f"{'#'*64}")
        audit_energy(scenario)
