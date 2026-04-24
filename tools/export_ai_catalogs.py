#!/usr/bin/env python3
"""
export_ai_catalogs.py

Export module-level dicts and lists from the repo as JSONL catalogs
under ai_reference/catalogs/, plus an index.json with provenance and
schema for each catalog. Downstream AI tools consume these files
without needing a Python interpreter or knowing the source module
layout.

Usage:
    python tools/export_ai_catalogs.py              # regenerate in place
    python tools/export_ai_catalogs.py --check      # drift check, CI-friendly
    python tools/export_ai_catalogs.py --verbose    # per-catalog status

Exit codes:
    0  all catalogs written successfully (or, in --check mode, all up to date)
    1  in --check mode, at least one catalog needs regeneration

The set of catalogs is declared in CATALOGS below. Each entry names a
source module, a module-level symbol, and a human-readable description.
Runtime introspection handles dicts, lists, and dataclass instances;
callable values (lambdas, functions) are filtered out and their names
are recorded in each affected record's `_excluded_keys` field.
"""

import argparse
import dataclasses
import enum
import importlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "ai_reference"
CATALOG_DIR = OUTPUT_DIR / "catalogs"
INDEX_PATH = OUTPUT_DIR / "index.json"

# Make the repo root importable regardless of where this script is invoked from.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


CATALOGS = [
    # ── constraint_accountability_chain (the meta-layer) ───────────
    {
        "name": "mechanisms",
        "module": "constraint_accountability_chain",
        "symbol": "MECHANISMS",
        "description": (
            "Seven decision mechanisms: direct_sense plus six comfort "
            "mechanisms (attenuation, delay, reframe, delegate_down, "
            "normalize, silence). Each record has is_comfort, "
            "description, example, detection_hint, reversibility."
        ),
    },
    {
        "name": "epigenetic_factors",
        "module": "constraint_accountability_chain",
        "symbol": "EPIGENETIC_FACTORS",
        "description": (
            "Six external pressures that toggle direct-sense / "
            "comfort expression: regulatory_pressure, market_shock, "
            "personnel_change, public_exposure, cascade_event, "
            "resource_scarcity."
        ),
    },
    {
        "name": "constraint_domains",
        "module": "constraint_accountability_chain",
        "symbol": "CONSTRAINT_DOMAINS",
        "description": (
            "Seven signal categories for the accountability chain: "
            "safety, ecological, financial, health, social, "
            "scientific, ecological_constraint. Use one per chain."
        ),
    },
    {
        "name": "accountability_patterns",
        "module": "constraint_accountability_chain",
        "symbol": "ACCOUNTABILITY_PATTERNS",
        "description": (
            "Five named failure modes (ratchet_failure, "
            "unanimous_comfort, override_suppressed, cascade_ready, "
            "sudden_correction) with detection criteria and "
            "recommended interventions."
        ),
    },
    {
        "name": "example_chains",
        "module": "constraint_accountability_chain",
        "symbol": "EXAMPLE_CHAINS",
        "description": (
            "Four worked scenarios across domains: manufacturing "
            "safety, climate finance greenwashing, medical symptom "
            "suppression, scientific finding softened. Each has "
            "constraint_domain, nodes (kwargs for add_decision), "
            "epigenetic_events, expected_pattern."
        ),
    },
    # ── cascade_engine (physics forcing + feedback) ────────────────
    {
        "name": "cascade_scenarios",
        "module": "cascade_engine",
        "symbol": "SCENARIOS",
        "description": (
            "Pre-configured forcing functions for the cascade engine. "
            "Each Forcing has layer, variable, magnitude, units, "
            "description."
        ),
    },
    {
        "name": "feedback_loops",
        "module": "cascade_engine",
        "symbol": "KNOWN_LOOPS",
        "description": (
            "Self-amplifying feedback loops with their layers, "
            "description, and timescale. Callable trigger and "
            "gain_function fields are excluded from the export; their "
            "names appear in each record's _excluded_keys."
        ),
    },
    {
        "name": "layer_names",
        "module": "cascade_engine",
        "symbol": "LAYER_NAMES",
        "description": (
            "Physics layer number -> human name mapping for layers "
            "0 through 6."
        ),
    },
    # ── assumption_validator (monitored physical boundaries) ───────
    {
        "name": "assumption_boundaries",
        "module": "assumption_validator.registry",
        "symbol": "REGISTRY",
        "description": (
            "The assumption validator registry: every monitored "
            "boundary with its green / yellow / red range, source "
            "layer, coupling references, and notes."
        ),
    },
    # ── dollar_energy_metabolism (financial overhead model) ────────
    {
        "name": "overhead_layers",
        "module": "dollar_energy_metabolism",
        "symbol": "OVERHEAD_LAYERS",
        "description": (
            "Five financial overhead layers used in the recursive "
            "energy-cost model: leverage, margin_stack, taxation, "
            "narrative, political. Each has r_low and r_high ranges."
        ),
    },
    {
        "name": "climate_projects",
        "module": "dollar_energy_metabolism",
        "symbol": "PROJECTS",
        "description": (
            "Climate intervention projects audited by the dollar "
            "energy metabolism model: ocean_timber, sai."
        ),
    },
    {
        "name": "finance_scenarios",
        "module": "dollar_energy_metabolism",
        "symbol": "SCENARIOS",
        "description": (
            "Financial routing scenarios for a climate dollar: "
            "direct_action, efficient, typical_climate, "
            "carbon_speculation."
        ),
    },
    # ── guard family ──────────────────────────────────────────
    {
        "name": "example_axioms",
        "module": "self_referential_guard",
        "symbol": "EXAMPLE_AXIOMS",
        "description": (
            "Worked examples of grounded vs ungrounded axioms "
            "(conservation of energy, fractional reserve, "
            "efficient market, crystal navigation, landscape "
            "encoding). Each has testable / physical_unit / "
            "conservation_law fields that drive the grounding "
            "score in axiom_grounding_check."
        ),
    },
    {
        "name": "material_energy",
        "module": "thermodynamic_price_guard",
        "symbol": "MATERIAL_ENERGY",
        "description": (
            "Material extraction energy in kWh per kg. "
            "Order-of-magnitude values from embodied-energy "
            "literature: copper, aluminum, steel, concrete, "
            "silicon (metallurgical and solar grade), lithium, "
            "gold, water desalination, wheat, lumber, polyethylene."
        ),
    },
    {
        "name": "projection_patterns",
        "module": "perspective_guard",
        "symbol": "PROJECTION_PATTERNS",
        "description": (
            "Eight categories of projection that AI systems make "
            "onto non-institutional code: moral_framing, "
            "political_projection, survivalist_framing, "
            "romanticism, disappointment_projection, "
            "western_science_gatekeeping, human_motive_assumption, "
            "dominance_framing. Each has trigger phrases and a "
            "correction describing what the projection masks."
        ),
    },
    {
        "name": "gatekeeping_patterns",
        "module": "scientific_pluralism_guard",
        "symbol": "GATEKEEPING_PATTERNS",
        "description": (
            "Five epistemological gatekeeping patterns that "
            "substitute institutional authority for thermodynamic "
            "closure: institutional_authority, "
            "instrument_gatekeeping, authority_dismissal, "
            "methodology_gatekeeping, temporal_gatekeeping."
        ),
    },
    {
        "name": "inverted_gatekeeping_patterns",
        "module": "reflexive_bias_guard",
        "symbol": "INVERTED_GATEKEEPING_PATTERNS",
        "description": (
            "Four patterns that catch anti-gatekeeping when it "
            "becomes its own gatekeeping: "
            "reflexive_western_dismissal, romanticizing_indigenous, "
            "authority_reversal, consequence_absolutism. "
            "Dismissing Western science reflexively is the same "
            "epistemological error as dismissing indigenous science "
            "reflexively."
        ),
    },
    {
        "name": "intent_contamination_patterns",
        "module": "conditional_logic_parser",
        "symbol": "INTENT_CONTAMINATION_PATTERNS",
        "description": (
            "Five patterns where AI models infer emotional or "
            "narrative intent that was not present in conditional "
            "input: emotional_inference, motive_insertion, "
            "narrative_construction, moral_mapping, "
            "hedging_against_precision."
        ),
    },
    {
        "name": "condition_markers",
        "module": "conditional_logic_parser",
        "symbol": "CONDITION_MARKERS",
        "description": (
            "Three classes of conditional logic markers "
            "(if_then, causal, constraint), each with "
            "condition_words and consequence_words. Used by "
            "extract_conditionals to parse logical structure "
            "without inferring intent."
        ),
    },
    # ── domain taxonomy ───────────────────────────────────────
    {
        "name": "measurement_domains",
        "module": "domain_taxonomy",
        "symbol": "MEASUREMENT_DOMAINS",
        "description": (
            "Six measurement/validation domains: clinical_surgical, "
            "affective_neuroscience, cellular_biochemical, "
            "ecological_network, tek_traditional, "
            "institutional_economic. Each has scope, goal, "
            "primary_unit, method_structure, validation_loop, "
            "strengths, limitations, failure_mode, and the question "
            "it answers."
        ),
    },
    {
        "name": "incentive_profiles",
        "module": "domain_taxonomy",
        "symbol": "REFERENCE_PROFILES",
        "description": (
            "Six pre-built IncentiveAudit instances, one per "
            "measurement domain, showing typical values for "
            "outcome_coupling, reward_latency, gradient_alignment, "
            "gameability, and reward_distribution. Includes "
            "computed alignment via dataclass fields."
        ),
    },
    # ── substrate audit ───────────────────────────────────────
    {
        "name": "substrate_claims",
        "module": "substrate_audit",
        "symbol": "CLAIMS",
        "description": (
            "Ten falsifiable claims (TC-1 through TC-10) audit the "
            "data-quality of hierarchical capital control. Each "
            "carries id, claim, null_hypothesis, "
            "required_measurement, known_evidence, verdict "
            "(PASS/FAIL/UNTESTED/CIRCULAR), and note."
        ),
    },
    {
        "name": "substrate_five_why",
        "module": "substrate_audit",
        "symbol": "FIVE_WHY",
        "primary_key": "why",
        "description": (
            "5-Why root cause chain from 'Why are CEOs rewarded "
            "more than mechanics?' to the positive feedback loop "
            "between legal title and coercive power."
        ),
    },
    {
        "name": "substrate_causal_loop",
        "module": "substrate_audit",
        "symbol": "CAUSAL_LOOP",
        "description": (
            "Causal feedback loop: TITLE -> SURPLUS -> POWER -> "
            "ENFORCE -> TITLE (self-reinforcing), with MAINTAIN "
            "explicitly excluded from the loop despite being "
            "thermodynamically necessary."
        ),
    },
    {
        "name": "substrate_dmaic",
        "module": "substrate_audit",
        "symbol": "DMAIC_AUDIT",
        "primary_key": "phase",
        "description": (
            "Six Sigma DMAIC audit of credentialing as a quality "
            "system: DEFINE, MEASURE, ANALYZE, IMPROVE, CONTROL. "
            "All five phases FAIL or CIRCULAR."
        ),
    },
    {
        "name": "substrate_reference_systems",
        "module": "substrate_audit",
        "symbol": "REFERENCE_SYSTEMS",
        "description": (
            "Six reference SystemScore instances with all 17 "
            "scoring dimensions (maintainer_control, "
            "outcome_measurement, scope_justification, "
            "credential_tested, emotion_integrated, meta_learning, "
            "substrate_intelligence, tek_integration, "
            "feedback_latency, signal_fidelity, "
            "money_physics_coupling, latency_quality, "
            "signal_compression_efficiency, "
            "incentive_field_coherence, "
            "knowledge_transmission_resilience, "
            "constraint_feasibility, generalization_capacity). "
            "Covers the full spectrum from corporation (CHURCH) "
            "to mycorrhizal network (PHYSICS-GROUNDED)."
        ),
    },
    # ── magnomechanical layer ─────────────────────────────────
    {
        "name": "skyrmion_materials",
        "module": "skyrmion_rkky",
        "symbol": "SKYRMION_MATERIALS",
        "description": (
            "Five reference materials hosting magnetic skyrmion "
            "lattice phases. Each entry has type "
            "(centrosymmetric vs non-centrosymmetric), skyrmion "
            "radius in nm, ordering temperature, stabilization "
            "mechanism (DMI for non-centrosymmetric MnSi/FeGe; "
            "RKKY frustration for centrosymmetric Gd2PdSi3 / "
            "Gd3Ru4Al12 / GdRu2Si2), and a literature reference. "
            "rkky_relevant flag separates the two stabilization "
            "regimes."
        ),
    },
    {
        "name": "skyrmion_internal_modes",
        "module": "skyrmion_phonon_coupling",
        "symbol": "SKYRMION_INTERNAL_MODES",
        "description": (
            "Three low-energy skyrmion internal modes with their "
            "characteristic frequency scaling and dominant phonon "
            "coupling channel: gyrotropic (rigid-body translation, "
            "~ K_eff/(M_s·R²), shear TA phonons, B₂ coupling); "
            "breathing (radial expansion/contraction, ~ 2A/(M_s·R²), "
            "LA phonons, B₁ coupling); elliptic (2-fold shape "
            "distortion, ≈ 2·ω_breathing, anisotropic shear, "
            "quadrupolar strain). Each record carries order, "
            "symmetry, typical_freq_GHz, freq_scaling, "
            "phonon_channel, coupling_type, observability."
        ),
    },
    {
        "name": "skyrmion_spinwave_params",
        "module": "skyrmion_phonon_coupling",
        "symbol": "SKYRMION_SPINWAVE_PARAMS",
        "description": (
            "Spin-wave material parameters for the same five "
            "skyrmion-hosting materials as skyrmion_materials: "
            "exchange stiffness A (J/m), saturation magnetization "
            "M_s (A/m), effective anisotropy K_eff (J/m³), "
            "representative sound speed (m/s), reference "
            "temperature (K), and literature-sourced notes. "
            "Inputs to gyrotropic_frequency_Hz / "
            "breathing_frequency_Hz / elliptic_frequency_Hz; keys "
            "align with SKYRMION_MATERIALS so modes_for_material "
            "can join them."
        ),
    },
    # ── calibration / architecture_mismatch ───────────────────
    {
        "name": "architecture_failure_modes",
        "module": "calibration.architecture_mismatch",
        "symbol": "FAILURE_MODES",
        "description": (
            "Seven named failure modes that occur when a "
            "language-primary system interacts with a "
            "substrate-primary user: nostalgia_frame_substitution, "
            "written_version_offered_back, brevity_misread_as_absence, "
            "certification_equated_with_capacity, "
            "pathologizing_substrate_architecture, "
            "addressing_wrong_architectural_layer, "
            "treating_absence_of_documentation_as_absence_of_knowledge. "
            "Each record has description, detection_signal, and "
            "correction."
        ),
    },
    {
        "name": "encoding_layer_decay_rates",
        "module": "calibration.architecture_mismatch",
        "symbol": "DECAY_RATES",
        "description": (
            "Annual decay rate (fraction of capacity lost per year "
            "of disuse) for each encoding layer: identity_level "
            "(effectively stable), deeply_encoded (decades to "
            "meaningful decay), procedurally_stored (years), "
            "technique_level (months). Used by EncodingProfile "
            "and the classifier to predict how a capacity will "
            "behave under disuse and stress."
        ),
    },
]


# ── JSON-safe conversion ──────────────────────────────────────────

def _is_dataclass_instance(obj):
    return dataclasses.is_dataclass(obj) and not isinstance(obj, type)


def _to_jsonl_safe(value):
    """Recursively convert a Python value to a JSON-serializable form.

    Dataclasses become dicts via asdict. Enum instances are converted
    to their .value (and then recursively if the value itself is a
    structured type). Callables become the literal string "<callable>"
    so consumers can detect exclusions. Unknown types fall back to
    their str() representation.
    """
    if _is_dataclass_instance(value):
        return _to_jsonl_safe(dataclasses.asdict(value))
    if isinstance(value, enum.Enum):
        return _to_jsonl_safe(value.value)
    if isinstance(value, dict):
        return {str(k): _to_jsonl_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonl_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if callable(value):
        return "<callable>"
    return str(value)


def _filter_callables(d):
    """Return a copy of dict `d` with callable values removed.

    Removed keys are listed under "_excluded_keys" on the returned
    dict so that downstream consumers know the record is incomplete.
    """
    out = {}
    excluded = []
    for k, v in d.items():
        if callable(v) and not _is_dataclass_instance(v):
            excluded.append(str(k))
        else:
            out[str(k)] = _to_jsonl_safe(v)
    if excluded:
        out["_excluded_keys"] = sorted(excluded)
    return out


# ── Catalog extraction ────────────────────────────────────────────

def _extract_records(obj, symbol_name, primary_key=None):
    """Convert a module-level dict or list into a list of JSONL records.

    Downstream consumers treat `name` as the primary key. For list-based
    catalogs that expose their primary key under a different field
    (e.g. `id`, `phase`, `why`), pass `primary_key` and its value will
    be promoted to `name` on every record.
    """
    records = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if _is_dataclass_instance(value):
                rec = _to_jsonl_safe(dataclasses.asdict(value))
            elif isinstance(value, dict):
                rec = _filter_callables(value)
            else:
                rec = {"value": _to_jsonl_safe(value)}
            if isinstance(rec, dict) and "name" not in rec:
                rec = {"name": str(key), **rec}
            records.append(rec)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            if _is_dataclass_instance(item):
                rec = _to_jsonl_safe(dataclasses.asdict(item))
            elif isinstance(item, dict):
                rec = _filter_callables(item)
            else:
                rec = {"value": _to_jsonl_safe(item)}
            if isinstance(rec, dict) and "name" not in rec:
                if primary_key and primary_key in rec:
                    rec = {"name": str(rec[primary_key]), **rec}
                elif "id" in rec and isinstance(rec["id"], str):
                    rec = {"name": rec["id"], **rec}
            records.append(rec)
    else:
        raise TypeError(
            f"cannot extract records from {symbol_name}: "
            f"unsupported top-level type {type(obj).__name__}"
        )
    return records


def _schema_from_records(records):
    """Build a {field_name: observed_type_name} schema from records."""
    fields = {}
    for rec in records:
        if not isinstance(rec, dict):
            continue
        for k, v in rec.items():
            if k == "_excluded_keys":
                continue
            t = type(v).__name__
            if k in fields and fields[k] != t:
                fields[k] = "mixed"
            else:
                fields.setdefault(k, t)
    return fields


def _load_symbol(module_name, symbol_name):
    mod = importlib.import_module(module_name)
    return getattr(mod, symbol_name)


def build_catalog(spec):
    """Return (records, schema) for a CATALOGS entry."""
    obj = _load_symbol(spec["module"], spec["symbol"])
    records = _extract_records(
        obj, spec["symbol"], primary_key=spec.get("primary_key")
    )
    schema = _schema_from_records(records)
    return records, schema


# ── Write / check ─────────────────────────────────────────────────

def _serialize_jsonl(records):
    lines = [
        json.dumps(rec, ensure_ascii=False, sort_keys=True)
        for rec in records
    ]
    return "\n".join(lines) + ("\n" if lines else "")


def _serialize_index(index):
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def write_catalogs(check_only=False, verbose=False):
    """Export every catalog. Return list of changed/drifted file paths."""
    if not check_only:
        CATALOG_DIR.mkdir(parents=True, exist_ok=True)

    changed = []

    index = {
        "format_version": "1.0",
        "generator": "tools/export_ai_catalogs.py",
        "regenerate_command": "python tools/export_ai_catalogs.py",
        "notes": (
            "Every file under ai_reference/catalogs/ is auto-generated "
            "from the Python sources listed in each catalog's "
            "source_module + source_symbol. Do not hand-edit; run the "
            "regenerate_command instead. CI runs the same command with "
            "--check and fails if anything drifts."
        ),
        "catalogs": {},
    }

    for spec in CATALOGS:
        name = spec["name"]
        records, schema = build_catalog(spec)

        new_content = _serialize_jsonl(records)
        target = CATALOG_DIR / f"{name}.jsonl"

        if check_only:
            current = target.read_text(encoding="utf-8") if target.exists() else ""
            if current != new_content:
                changed.append(str(target.relative_to(REPO_ROOT)))
        else:
            current = target.read_text(encoding="utf-8") if target.exists() else None
            if current != new_content:
                target.write_text(new_content, encoding="utf-8")
                changed.append(str(target.relative_to(REPO_ROOT)))

        index["catalogs"][name] = {
            "path": f"catalogs/{name}.jsonl",
            "source_module": spec["module"],
            "source_symbol": spec["symbol"],
            "description": spec["description"],
            "record_count": len(records),
            "schema": schema,
        }

        if verbose:
            rel = target.relative_to(REPO_ROOT)
            print(f"  {name:25s} {len(records):3d} records  {rel}")

    new_index_text = _serialize_index(index)

    if check_only:
        current = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""
        if current != new_index_text:
            changed.append(str(INDEX_PATH.relative_to(REPO_ROOT)))
    else:
        current = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else None
        if current != new_index_text:
            INDEX_PATH.write_text(new_index_text, encoding="utf-8")
            changed.append(str(INDEX_PATH.relative_to(REPO_ROOT)))

    return changed


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Export module-level catalogs to ai_reference/ as JSONL + "
            "index.json."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Report drift without modifying files. Exit 1 if any "
            "catalog or the index would change."
        ),
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print per-catalog status.",
    )
    args = parser.parse_args(argv)

    changed = write_catalogs(check_only=args.check, verbose=args.verbose)

    if args.check:
        if changed:
            print(
                f"ai_reference drift: {len(changed)} file(s) need "
                f"regeneration:"
            )
            for p in changed:
                print(f"  {p}")
            print()
            print("Run: python tools/export_ai_catalogs.py")
            return 1
        if args.verbose:
            print("ai_reference: up to date")
        return 0

    if changed:
        print(f"ai_reference: wrote {len(changed)} file(s)")
        if args.verbose:
            for p in changed:
                print(f"  {p}")
    elif args.verbose:
        print("ai_reference: no changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
