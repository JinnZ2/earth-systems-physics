# energy_audit.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Cross-layer energy conservation audit.
# Verifies that the cascade engine's energy bookkeeping closes.
# When forcing is applied, the total energy change across all layers
# should be accountable — not necessarily zero (external forcing adds
# energy), but the residual should be small.

import numpy as np

from cascade_engine import (
    run_all_layers, apply_forcing, BASELINE, LAYER_NAMES,
)


# ─────────────────────────────────────────────
# ENERGY-DIMENSIONED OUTPUTS
# Maps (layer, key) -> units category for normalization
# All values are converted to W/m² equivalent for comparison
# ─────────────────────────────────────────────

EARTH_SURFACE_AREA = 5.1e14     # m^2
ATMOSPHERE_THICKNESS = 8500.0   # m  (scale height)
IONOSPHERE_THICKNESS = 300e3    # m  (D-layer to F2-layer)

ENERGY_KEYS = {
    # Layer 0 — Electromagnetics (energy densities, need volume conversion)
    (0, "electric_energy_density"):   {"units": "J/m3",  "scale": ATMOSPHERE_THICKNESS},
    (0, "magnetic_energy_density"):   {"units": "J/m3",  "scale": ATMOSPHERE_THICKNESS},
    (0, "poynting_flux_wm2"):         {"units": "W/m2",  "scale": 1.0},

    # Layer 1 — Magnetosphere
    (1, "field_energy_density_Jm3"):  {"units": "J/m3",  "scale": 6.371e6 * 10},

    # Layer 2 — Ionosphere
    (2, "joule_heating_Wm3"):         {"units": "W/m3",  "scale": IONOSPHERE_THICKNESS},
    (2, "auroral_energy_flux_mWm2"):  {"units": "mW/m2", "scale": 1e-3},

    # Layer 3 — Atmosphere (already W/m^2)
    (3, "GHG_forcing_Wm2"):          {"units": "W/m2",  "scale": 1.0},
    (3, "aerosol_forcing_Wm2"):      {"units": "W/m2",  "scale": 1.0},
    (3, "net_forcing_Wm2"):          {"units": "W/m2",  "scale": 1.0},

    # Layer 4 — Hydrosphere
    (4, "AMOC_heat_transport_W"):    {"units": "W",     "scale": 1.0 / EARTH_SURFACE_AREA},
    (4, "ocean_heat_content_Jm2"):   {"units": "J/m2",  "scale": 1.0},
    (4, "ice_albedo_feedback_Wm2"):  {"units": "W/m2",  "scale": 1.0},

    # Layer 5 — Lithosphere
    (5, "volcanic_forcing_Wm2"):     {"units": "W/m2",  "scale": 1.0},
}


def energy_delta_wm2(baseline_states, perturbed_states, layer, key, spec):
    """
    Compute the energy delta in W/m^2 equivalent for a given key.
    """
    bv = baseline_states.get(layer, {}).get(key)
    pv = perturbed_states.get(layer, {}).get(key)
    if bv is None or pv is None:
        return 0.0
    if not isinstance(bv, (int, float)) or not isinstance(pv, (int, float)):
        return 0.0
    delta = pv - bv
    return delta * spec["scale"]


def audit_energy(forcing, baseline=None, verbose=True):
    """
    Run a forcing scenario and audit energy conservation across layers.

    Returns dict with:
      - layer_deltas: energy change per layer in W/m^2 equivalent
      - total_change: sum of all energy deltas
      - input_forcing_wm2: estimated forcing input
      - residual: unaccounted energy
      - residual_pct: residual as % of input
      - energy_leak: True if residual > 5% of input

    forcing  : Forcing dataclass
    baseline : parameter dict (uses BASELINE if None)
    verbose  : print audit report
    """
    if baseline is None:
        baseline = dict(BASELINE)

    baseline_states = run_all_layers(baseline)
    perturbed_params = apply_forcing(baseline, forcing)
    perturbed_states = run_all_layers(perturbed_params)

    # Compute energy deltas per layer
    layer_deltas = {}
    layer_details = {}
    for (layer, key), spec in ENERGY_KEYS.items():
        delta = energy_delta_wm2(baseline_states, perturbed_states, layer, key, spec)
        if abs(delta) > 1e-30:
            if layer not in layer_deltas:
                layer_deltas[layer] = 0.0
                layer_details[layer] = []
            layer_deltas[layer] += delta
            layer_details[layer].append((key, delta))

    total_change = sum(layer_deltas.values())

    # Estimate input forcing in W/m^2
    # Use the primary energy-like forcing output as reference
    input_wm2 = _estimate_forcing_energy(forcing, baseline_states, perturbed_states)

    residual = total_change - input_wm2 if input_wm2 != 0 else total_change
    residual_pct = (abs(residual) / max(abs(input_wm2), 1e-30)) * 100
    energy_leak = residual_pct > 5.0

    result = {
        "layer_deltas":       layer_deltas,
        "layer_details":      layer_details,
        "total_change_wm2":   total_change,
        "input_forcing_wm2":  input_wm2,
        "residual_wm2":       residual,
        "residual_pct":       residual_pct,
        "energy_leak":        energy_leak,
    }

    if verbose:
        _print_audit(result, forcing)

    return result


def _estimate_forcing_energy(forcing, baseline_states, perturbed_states):
    """
    Estimate the primary energy input from the forcing in W/m^2.
    Uses net_forcing_Wm2 as the best single estimate when available.
    """
    # Primary: atmospheric net forcing change
    b_net = baseline_states.get(3, {}).get("net_forcing_Wm2", 0)
    p_net = perturbed_states.get(3, {}).get("net_forcing_Wm2", 0)
    if isinstance(b_net, (int, float)) and isinstance(p_net, (int, float)):
        delta_net = p_net - b_net
        if abs(delta_net) > 1e-10:
            return delta_net

    # Fallback: GHG forcing change
    b_ghg = baseline_states.get(3, {}).get("GHG_forcing_Wm2", 0)
    p_ghg = perturbed_states.get(3, {}).get("GHG_forcing_Wm2", 0)
    if isinstance(b_ghg, (int, float)) and isinstance(p_ghg, (int, float)):
        delta_ghg = p_ghg - b_ghg
        if abs(delta_ghg) > 1e-10:
            return delta_ghg

    # If no atmospheric forcing, sum all energy deltas as input estimate
    total = 0
    for (layer, key), spec in ENERGY_KEYS.items():
        delta = energy_delta_wm2(baseline_states, perturbed_states, layer, key, spec)
        total += abs(delta)
    return total if total > 0 else 1.0


def _print_audit(result, forcing):
    """Print energy audit report."""
    print("=" * 64)
    print("ENERGY CONSERVATION AUDIT")
    print("=" * 64)
    print(f"FORCING: {forcing.description}")
    print(f"  {forcing.variable} {forcing.magnitude:+.4g} {forcing.units}")
    print()

    print("─" * 64)
    print("PER-LAYER ENERGY CHANGE  (W/m² equivalent)")
    for layer in sorted(result["layer_details"].keys()):
        name = LAYER_NAMES.get(layer, f"Layer {layer}")
        total = result["layer_deltas"][layer]
        print(f"  L{layer} {name:20s}  total: {total:+.6g} W/m²")
        for key, delta in result["layer_details"][layer]:
            print(f"    {key:40s}  {delta:+.6g}")
    print()

    print("─" * 64)
    print(f"  Total energy change : {result['total_change_wm2']:+.6g} W/m²")
    print(f"  Input forcing est.  : {result['input_forcing_wm2']:+.6g} W/m²")
    print(f"  Residual            : {result['residual_wm2']:+.6g} W/m²")
    print(f"  Residual (%)        : {result['residual_pct']:.2f}%")

    if result["energy_leak"]:
        print(f"  ** ENERGY LEAK DETECTED — residual > 5% of input **")
    else:
        print(f"  Energy bookkeeping closes within 5% tolerance")
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
