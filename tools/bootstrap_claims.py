#!/usr/bin/env python3
"""
tools/bootstrap_claims.py

Starter generator for the differential claim format
(see CLAIM_SCHEMA.py and DIFFERENTIAL_FRAME.md).

Reads cascade_engine.BASELINE, SCENARIOS, and KNOWN_LOOPS, casts
each as a bounded dX/dt claim, and writes:

    CLAIM_TABLE.json       — pooled unique strings + cycle enum
    cascade_engine.claims  — pipe-delimited claims, one per line

This is a single-source bootstrap so the format has a working
example. Extend by adding more sources and re-running.

Run from repo root:

    python tools/bootstrap_claims.py

CC0.
"""

import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import cascade_engine as ce  # noqa: E402

# Layer index -> short tag used in bounds / relational fields.
LAYER_TAGS = {
    0: "L0_em",
    1: "L1_mag",
    2: "L2_iono",
    3: "L3_atmo",
    4: "L4_hydro",
    5: "L5_litho",
    6: "L6_bio",
}

# BASELINE key -> (layer index, units). Pulled from the section
# comments in cascade_engine.py.
BASELINE_LAYERS = {
    # L0 — Electromagnetics
    "n_e": (0, "m^-3"),
    "B_surface": (0, "T"),
    "E_surface": (0, "V/m"),
    "freq_range": (0, "Hz"),
    "magnonic_material": (0, "—"),
    "magnomech_mineral": (0, "—"),
    "magnomech_grain_size": (0, "m"),
    "magnomech_rock_volume": (0, "m^3"),
    "magnomech_mineral_fraction": (0, "fraction"),
    # L1 — Magnetosphere
    "n_sw": (1, "m^-3"),
    "v_sw": (1, "m/s"),
    "Bz_imf": (1, "T"),
    "kp": (1, "Kp"),
    # L2 — Ionosphere
    "n_e_F2": (2, "m^-3"),
    "solar_flux": (2, "normalized"),
    "nu_en": (2, "Hz"),
    "E_convection": (2, "V/m"),
    "delta_T_thermo": (2, "K"),
    # L3 — Atmosphere
    "T_surface": (3, "K"),
    "T_pole": (3, "K"),
    "P_surface": (3, "Pa"),
    "q_surface": (3, "kg/kg"),
    "delta_CO2": (3, "ppm"),
    "AOD": (3, "—"),
    "latitude": (3, "deg"),
    "delta_omega": (3, "rad/s"),
    # L4 — Hydrosphere
    "T_ocean_C": (4, "C"),
    "S_ocean": (4, "PSU"),
    "T_north_C": (4, "C"),
    "S_north": (4, "PSU"),
    "T_south_C": (4, "C"),
    "S_south": (4, "PSU"),
    "ice_fraction": (4, "fraction"),
    "wind_stress": (4, "Pa"),
    "delta_S_melt": (4, "PSU"),
    "SST_enso": (4, "K"),
    "AMOC_Sv": (4, "Sv"),
    # L5 — Lithosphere
    "ice_mass_loss_Gt": (5, "Gt"),
    "SLR_m": (5, "m"),
    "lat_ice": (5, "deg"),
    "lon_ice": (5, "deg"),
    "fault_depth_m": (5, "m"),
    "SO2_volcanic": (5, "Tg"),
    # L6 — Biosphere
    "T_surface_K": (6, "K"),
    "CO2_ppm": (6, "ppm"),
    "ocean_pH": (6, "pH"),
    "permafrost_area": (6, "m^2"),
    "T_permafrost_anom": (6, "K"),
    "deforestation": (6, "fraction"),
    "delta_T_amazon": (6, "K"),
    "drought_index": (6, "—"),
    "GPP_GtC": (6, "GtC"),
    "anthro_GtC": (6, "GtC"),
    "AMOC_bio_Sv": (6, "Sv"),
}

# Mirrors CLAIM_SCHEMA.CYCLE_ENUM, indexed for write-side use.
CYCLE_ENUM = {
    "instantaneous": 0,
    "diurnal":       1,
    "seasonal":      2,
    "annual":        3,
    "generational":  4,
    "century":       5,
    "geologic":      6,
}


def timescale_to_cyc(ts: str) -> int:
    """Map a free-text timescale string to the closest CYCLE_ENUM value."""
    s = ts.lower()
    if "second" in s or "hour" in s or "minute" in s:
        return CYCLE_ENUM["instantaneous"]
    if "day" in s:
        return CYCLE_ENUM["diurnal"]
    if "season" in s:
        return CYCLE_ENUM["seasonal"]
    if "centur" in s:
        return CYCLE_ENUM["century"]
    if "decade" in s:
        return CYCLE_ENUM["generational"]
    if "year" in s:
        return CYCLE_ENUM["annual"]
    if "millenni" in s or "geolog" in s:
        return CYCLE_ENUM["geologic"]
    return CYCLE_ENUM["generational"]


def safe(s: str) -> str:
    """Strip characters that would break the pipe-delimited line format."""
    return (
        str(s)
        .replace("|", "/")
        .replace(",", ";")
        .replace("\n", " ")
        .strip()
    )


class Pool:
    """De-dup string -> integer index pool."""

    def __init__(self):
        self._values = []
        self._idx = {}

    def add(self, value: str) -> int:
        if value not in self._idx:
            self._idx[value] = len(self._values)
            self._values.append(value)
        return self._idx[value]

    def values(self) -> list:
        return list(self._values)


def build_claims():
    rates, bounds, cond, rel, fail, meas = (Pool() for _ in range(6))
    claims = []

    # BASELINE — steady-state reference values (dX/dt = 0 absent forcing).
    for key in ce.BASELINE:
        layer, units = BASELINE_LAYERS.get(key, (-1, "—"))
        tag = LAYER_TAGS.get(layer, "L?")
        claim = {
            "id":     f"bl_{key}",
            "rate":   f"d({key})/dt=0_at_baseline",
            "bounds": [tag, "Earth_2024_ref", units],
            "cond":   ["unforced_reference"],
            "rel":    [tag],
            "fail":   ["forcing_applied", "scope_outside_2024_envelope"],
            "meas":   [f"BASELINE['{key}']"],
            "cyc":    CYCLE_ENUM["century"],
        }
        claims.append(claim)

    # SCENARIOS — single-variable forcing impulses.
    for name, f in ce.SCENARIOS.items():
        tag = LAYER_TAGS.get(f.layer, "L?")
        other_layers = [LAYER_TAGS[i] for i in range(7) if i != f.layer]
        claim = {
            "id":     f"sc_{name}",
            "rate":   f"d({f.variable})/dt={f.magnitude:+g}_{f.units or '-'}_impulse",
            "bounds": [tag, "scenario_horizon", f.units or "—"],
            "cond":   [f"variable={f.variable}", f"layer={f.layer}"],
            "rel":    other_layers,
            "fail": [
                "variable_unknown_to_FORCING_PARAM_MAP",
                "magnitude_outside_validated_range",
            ],
            "meas":   [f"run_cascade(SCENARIOS[{name}])"],
            "cyc":    CYCLE_ENUM["generational"],
        }
        claims.append(claim)

    # KNOWN_LOOPS — feedback loops with gain functions.
    for loop in ce.KNOWN_LOOPS:
        slug = loop["name"].lower().replace("-", "_")
        layer_tags = [LAYER_TAGS.get(i, "L?") for i in loop["layers"]]
        claim = {
            "id":     f"lp_{slug}",
            "rate":   f"d(state)/dt*gain[{loop['name']}]",
            "bounds": ["+".join(layer_tags), loop["timescale"], "loop_scope"],
            "cond":   ["trigger_predicate_holds", "gain>1"],
            "rel":    layer_tags,
            "fail":   ["trigger_predicate_false", "gain<=1_dissipative"],
            "meas":   [f"detect_amplifying_loops:{loop['name']}"],
            "cyc":    timescale_to_cyc(loop["timescale"]),
        }
        claims.append(claim)

    pooled = []
    for c in claims:
        c["_bounds"] = [safe(x) for x in c["bounds"]]
        c["_cond"]   = [safe(x) for x in c["cond"]]
        c["_rel"]    = [safe(x) for x in c["rel"]]
        c["_fail"]   = [safe(x) for x in c["fail"]]
        c["_meas"]   = [safe(x) for x in c["meas"]]
        c["_rate"]   = safe(c["rate"])
        pooled.append({
            "id":         c["id"],
            "rate_idx":   rates.add(c["_rate"]),
            "bounds_idx": [bounds.add(b) for b in c["_bounds"]],
            "cond_idx":   [cond.add(x) for x in c["_cond"]],
            "rel_idx":    [rel.add(x) for x in c["_rel"]],
            "fail_idx":   [fail.add(x) for x in c["_fail"]],
            "meas_idx":   [meas.add(x) for x in c["_meas"]],
            "cyc":        c["cyc"],
            "_rate":      c["_rate"],
            "_bounds":    c["_bounds"],
            "_cond":      c["_cond"],
            "_rel":       c["_rel"],
            "_fail":      c["_fail"],
            "_meas":      c["_meas"],
        })

    table = {
        "format_version": 1,
        "source": "cascade_engine.py (BASELINE, SCENARIOS, KNOWN_LOOPS)",
        "rates":  rates.values(),
        "bounds": bounds.values(),
        "cond":   cond.values(),
        "rel":    rel.values(),
        "fail":   fail.values(),
        "meas":   meas.values(),
        "cycle_enum": {str(v): k for k, v in CYCLE_ENUM.items()},
    }
    return pooled, table


def to_line(claim: dict) -> str:
    """Render one claim as a pipe-delimited line: id|rate|bounds|cond|rel|fail|meas|cyc"""
    return "|".join([
        claim["id"],
        claim["_rate"],
        ",".join(claim["_bounds"]),
        ",".join(claim["_cond"]),
        ",".join(claim["_rel"]),
        ",".join(claim["_fail"]),
        ",".join(claim["_meas"]),
        str(claim["cyc"]),
    ])


def main():
    claims, table = build_claims()

    table_path = REPO_ROOT / "CLAIM_TABLE.json"
    claims_path = REPO_ROOT / "cascade_engine.claims"

    table_path.write_text(json.dumps(table, indent=2) + "\n")
    claims_path.write_text("\n".join(to_line(c) for c in claims) + "\n")

    n_baseline = len(ce.BASELINE)
    n_scen = len(ce.SCENARIOS)
    n_loops = len(ce.KNOWN_LOOPS)
    print(
        f"Wrote {table_path.relative_to(REPO_ROOT)} "
        f"(rates={len(table['rates'])}, bounds={len(table['bounds'])}, "
        f"cond={len(table['cond'])}, rel={len(table['rel'])}, "
        f"fail={len(table['fail'])}, meas={len(table['meas'])})"
    )
    print(
        f"Wrote {claims_path.relative_to(REPO_ROOT)} "
        f"({len(claims)} claims = {n_baseline} baseline + "
        f"{n_scen} scenarios + {n_loops} loops)"
    )


if __name__ == "__main__":
    main()
