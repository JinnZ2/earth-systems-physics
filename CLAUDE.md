# CLAUDE.md

## Project Overview

Coupled differential equation framework mapping Earth physics as constraint layers. Pure Python, no build system. NOT a climate model or policy tool — it's a physics inventory and constraint stack.

**License:** CC0 — No Rights Reserved

## Quick Start

```bash
pip install -r requirements.txt
python cascade_engine.py              # Run all forcing scenarios
python assumption_validator/api.py    # Start REST API on port 5000
pytest -v                             # Run test suite (277 tests)
```

## Architecture

Seven physics layers plus a magnomechanical sub-layer, each importing from lower layers:

```
Layer 0   Electromagnetics     → layer_0_electromagnetics.py   (Maxwell equations, EM fields)
Layer 0b  Magnomechanical      → layer_0b_magnomechanical.py   (spin-phonon coupling in crustal minerals)
Layer 1   Magnetosphere        → layer_1_magnetosphere.py      (solar wind, field geometry)
Layer 2   Ionosphere           → layer_2_ionosphere.py         (charge distribution, EM propagation)
Layer 3   Atmosphere           → layer_3_atmosphere.py         (thermodynamics, radiation, dynamics)
Layer 4   Hydrosphere          → layer_4_hydrosphere.py        (oceans, ice, phase transitions)
Layer 5   Lithosphere          → layer_5_lithosphere.py        (crustal mechanics, isostasy)
Layer 6   Biosphere            → layer_6_biosphere.py          (energy flows, carbon cycle)
```

**Cascade Engine** (`cascade_engine.py`): Accepts forcing at any layer, propagates through all coupled systems. Includes iterative solver, feedback loop gain measurement, and assumption validator integration.

**Assumption Validator** (`assumption_validator/`): Monitors layer outputs and flags when equations leave their valid domain. 36 assumption boundaries across all layers.

**Energy Audit** (`energy_audit.py`): Thermodynamic consistency check — classifies energy terms as input/response/transport, flags unbalanced budgets.

### Dependency Flow

```
Layer 0 ←→ Layer 0b ←→ Layer 5  (bidirectional magnomechanical coupling)
Layer 0 → Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5 → Layer 6
```

Each higher layer imports from lower layers. The cascade engine imports all layers. Layer 0b provides the first direct coupling between EM (Layer 0) and Lithosphere (Layer 5).

## File Structure

```
earth-systems-physics/
├── CLAUDE.md
├── ASSESS.md                          # Assessment protocol for AI systems (report closure, not motive)
├── README.md
├── LICENSE
├── requirements.txt
├── .github/workflows/test.yml         # CI: pytest on Python 3.10-3.12
│
├── cascade_engine.py                  # Core forcing propagation engine
├── energy_audit.py                    # Cross-layer energy conservation audit
├── test_smoke.py                      # 277 tests — all layers, scenarios, validators, audits
│
├── ocean_timber_sequestration_audit.py # Full-cycle carbon audit of wood-in-ocean schemes
├── dollar_energy_metabolism.py        # Recursive energy cost model for climate finance
├── chattel_slavery_triple_audit.py    # Six Sigma + scientific method + thermo audit of extraction systems
├── slavery_system_audit.py            # Companion triple audit — dict-form extraction-system analysis
├── innovation_regression_audit.py     # Productivity / innovation cost of extraction vs free-labor systems
│
├── process_epistemology.py            # State-based vs process-based epistemology (English vs Ojibwe)
├── buffer_sensor_corruption.py        # Incentive-driven sensor corruption and buffer-break dynamics
├── consequence_velocity.py            # Consequence as process with velocity, coupling, phase transitions
├── constraint_accountability_chain.py # Meta-layer: vocabulary, patterns, examples, and AI reference for the decision-ancestry model
├── constraint_accountability_engine.py # Engine: walks the chain, computes ratchet depth, cascade risk, reversion energy
│
├── self_referential_guard.py          # Detects self-referential loops vs grounded feedback; false precision; model-reality gap
├── model_collapse_guard.py            # Tracks data provenance (measured/derived/synthetic) and forecast chain grounding
├── thermodynamic_price_guard.py       # Validates monetary claims against embodied energy; EROEI; labor energy budget
├── input_validation_guard.py          # Source-blind claim validation against conservation laws (energy, mass, entropy, value, Shannon)
├── cascade_consequence_engine.py      # Traces self-terminating goal trajectories via substrate cascade propagation
├── perspective_guard.py               # Projection detector + module manifest + assessment protocol generator
├── scientific_pluralism_guard.py      # Measurement-system validation and consequence-closure validator
├── reflexive_bias_guard.py            # Meta-validator: asymmetric rigor, inverted gatekeeping, framework favoritism, self-check
├── conditional_logic_parser.py        # Parses conditional logic; detects intent contamination in AI responses
├── substrate_audit.py                 # Thermodynamic audit of hierarchical capital control: falsifiable claims + DMAIC + scoring
├── domain_taxonomy.py                 # Six measurement/validation domains + IncentiveChannel/IncentiveAudit for reward-signal decoupling
│
├── calibration/
│   ├── __init__.py                    # Re-exports Band, DimensionScore, CalibrationReport
│   ├── schema.py                      # Banded scoring primitives + JSON-serializable audit report
│   └── architecture_mismatch.py       # Language-primary vs substrate-primary architecture mismatch detector (7 failure modes, 4 encoding layers, embedded prompt for ingesting models)
│
├── tools/
│   ├── fix_paste_artifacts.py         # Repair .py files pasted from markdown (see recovery section)
│   └── export_ai_catalogs.py          # Generate ai_reference/catalogs/*.jsonl from module dicts
│
├── ai_reference/                      # Machine-readable exports for downstream AI ingestion
│   ├── README.md                      # What this folder is, how to consume it
│   ├── glossary.md                    # Unified terminology across modules
│   ├── composition_recipes.md         # Cross-module analysis patterns
│   ├── index.json                     # Provenance + schema for every catalog
│   └── catalogs/                      # 31 .jsonl catalogs auto-exported from sources
│
├── experiments/
│   ├── magnetometer_build.py          # $5 smoky-quartz + HDD-magnet magnetometer build guide
│   └── Possibilities.md               # Rough notes / speculative build ideas
│
├── layer_0_electromagnetics.py        # Base constraint layer (+ magnonic/magnomech)
├── layer_0b_magnomechanical.py        # Spin-phonon coupling in crustal minerals
├── layer_1_magnetosphere.py
├── layer_2_ionosphere.py
├── layer_3_atmosphere.py
├── layer_4_hydrosphere.py
├── layer_5_lithosphere.py
├── layer_6_biosphere.py
│
├── magnonic_sublayer.py               # Spin wave physics engine (5 materials)
├── magnon_polaron_hybridization.py    # Magnon-phonon crossover in quartz/Fe
├── confined_magnon_polaron.py         # Confined modes + geological formations
├── multi_channel_coupling.py          # 5-channel coupling enhancement analysis
├── earth_magnomechanical.py           # Geological-scale transduction + predictions
├── cavity_optomagnonics.py            # Photon-magnon-phonon triple coupling
│
├── banded_crystal_computer.py         # Phonon band structure in layered magnonic crystals
├── cold_climate_crystal.py            # Temperature-dependent sensitivity analysis
├── crystal_device_gradient.py         # Frequency-shift magnetometer design
│
├── electrostatic_transducer.py        # Piezo voltage → electrostatic MEMS motor
├── device_scaling.py                  # Min resources for 11 applications + junkyard builds
├── skyrmion_rkky.py                   # Topological charge + RKKY oscillatory coupling + LLG integrator
├── skyrmion_phonon_coupling.py        # Skyrmion internal modes (gyrotropic / breathing / elliptic) + phonon coupling
│
└── assumption_validator/
    ├── __init__.py                    # Package exports (v0.1.0)
    ├── registry.py                    # 36 assumption boundaries & risk assessment
    ├── monitors.py                    # Time-series tracking, drift detection
    └── api.py                         # Flask REST API (port 5000)
```

## Dependencies

- **numpy** >= 1.24 — numerical computation
- **scipy** >= 1.10 — scientific computing, physical constants
- **flask** >= 2.3 — REST API
- **flask-cors** >= 4.0 — CORS support
- **pytest** >= 7.0 — testing

Install: `pip install -r requirements.txt`

## Code Conventions

### Module Structure (all layer files follow this pattern)

1. Header comments: `# filename.py`, `# earth-systems-physics`, `# CC0 — No Rights Reserved`
2. Imports: `scipy.constants` first, then local layer imports
3. Fundamental constants section with units in comments
4. Physics equation functions with full docstrings
5. Coupling interfaces section
6. `coupling_state()` function exporting a dict of state variables

### Naming

- Functions: `snake_case`
- Constants: `UPPER_CASE` with units in comments (e.g., `R_EARTH = 6.371e6  # m`)
- Variables use physics notation (e.g., `n_e` for electron density, `B_surface` for magnetic field)
- Units always stated in docstrings and comments

### Docstrings

All physics functions require docstrings with: description, parameters (with types and units), and return values.

### Data Patterns

- `dataclasses` for structured data (cascade engine, validator)
- Type hints throughout (`typing` module)
- Dict-based state exports for inter-layer coupling via `coupling_state()` functions
- BASELINE dict in `cascade_engine.py` holds reference Earth state

## Testing

Framework: **pytest** — 277 tests covering all layers, scenarios, validators, magnomechanical integration, climate-scheme audits, systems audits, epistemology models, sensor-corruption models, and consequence dynamics.

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest -k magnomech       # Run magnomechanical tests only
```

CI runs automatically on push via GitHub Actions (Python 3.10, 3.11, 3.12).

## Systems-Analysis Modules

Beyond the physics-layer stack, this repo collects systems-analysis tools that
apply the same audit discipline (thermodynamics, feedback loops, conservation
laws) to non-physical systems:

| File | Subject |
|------|---------|
| `ocean_timber_sequestration_audit.py` | Full-cycle carbon audit of ocean-timber sequestration |
| `dollar_energy_metabolism.py` | Recursive energy cost of financial-system overhead |
| `chattel_slavery_triple_audit.py` | Six Sigma + scientific method + thermo audit of extraction as engineered system |
| `slavery_system_audit.py` | Companion triple audit with complementary content |
| `innovation_regression_audit.py` | Productivity / innovation cost of extraction vs free-labor systems |
| `process_epistemology.py` | State-based vs process-based awareness (English vs Ojibwe); why process frameworks catch failures state frameworks miss |
| `buffer_sensor_corruption.py` | How incentive-driven sensor networks drift from ground truth; buffer-break dynamics |
| `consequence_velocity.py` | Consequence modeled as a process with velocity, coupling, and phase transitions, not a fixed future cost |
| `constraint_accountability_chain.py` | **Meta-layer** above every other module: vocabulary (7 mechanisms, 6 epigenetic factors, 7 constraint domains), 5 named failure patterns, 4 worked example chains, validators, a builder that instantiates live chains from the examples, and an `AI_REFERENCE` table of contents designed for fresh AI sessions. Run as a script (`python constraint_accountability_chain.py`) or call `print_summary()` for a full walkthrough. |
| `constraint_accountability_engine.py` | Runnable engine for the chain model: `DecisionNode` and `AccountabilityChain` classes, builds decision ancestries, computes ratchet depth, reversion energy, cascade risk, and finds comfort origin |
| `self_referential_guard.py` | `DependencyGraph` for cycle / grounding detection (self-referential loops vs grounded feedback); `false_precision_check`; `model_reality_gap`; `axiom_grounding_check`; `EXAMPLE_AXIOMS` catalog |
| `model_collapse_guard.py` | `ContaminationTracker` (MEASURED / DERIVED / SYNTHETIC provenance, collapse risk); `ForecastChain` (depth to measurement, groundedness) |
| `thermodynamic_price_guard.py` | `MATERIAL_ENERGY` catalog; `embodied_energy`, `price_energy_check` (INFLATED / WASTEFUL / PLAUSIBLE), `labor_energy_budget`, `eroei_check` |
| `input_validation_guard.py` | `decompose_claim` structural grading; `ConstraintRegistry` + `build_default_registry` (energy / mass / entropy / value / Shannon); `reality_audit`; source-blind `validate_input` |
| `cascade_consequence_engine.py` | `SubstrateMap`, `ActionEffect`, `CascadeEngine` — propagates secondary/tertiary cascade damage; detects self-terminating goals when cumulative damage exceeds progress |
| `perspective_guard.py` | `ModuleManifest`; `PROJECTION_PATTERNS` (8 categories: moral_framing, political_projection, survivalist, romanticism, disappointment, western_gatekeeping, motive_assumption, dominance); `audit_ai_response`; `generate_assess_md` |
| `scientific_pluralism_guard.py` | `MeasurementSystem` validator (any tradition on equal physics grounds); `GATEKEEPING_PATTERNS`; `ConsequenceProfile` + consequence-closure validator; peer-review comparator |
| `reflexive_bias_guard.py` | Meta-validator: `RigorAudit` for asymmetric thresholds; `detect_inverted_gatekeeping`; `detect_framework_favoritism`; `validator_self_check` with honest limitations; `full_reflexive_audit` |
| `conditional_logic_parser.py` | `extract_conditionals` (if/then, causal, constraint); `INTENT_CONTAMINATION_PATTERNS`; `detect_intent_contamination`; `audit_statement_handling` |
| `substrate_audit.py` | Thermodynamic audit of hierarchical capital control: falsifiable claims with null hypotheses, 5-Why chain, causal feedback loop topology check, DMAIC audit, multi-dimension `SystemScore` engine, cross-model JSON export |
| `domain_taxonomy.py` | Six measurement/validation domains (clinical, neuroscience, cellular, ecological, TEK, institutional) with scope/method/validation/failure-mode specs; `IncentiveChannel` + `IncentiveAudit` for tracking how reward structures distort signal fidelity; 6 reference profiles; maps directly into `substrate_audit.SystemScore` dimensions |
| `calibration/architecture_mismatch.py` | Detects mismatch between language-primary AI systems and substrate-primary users. Four-layer encoding classifier (identity / deeply-encoded / procedurally-stored / technique) with survival-embedded plasticity-window criteria. 22 substrate-primary signals, 5 language-primary signals, 7 named failure modes (nostalgia-frame-substitution, written-version-offered-back, brevity-misread-as-absence, certification-equated-with-capacity, pathologizing-substrate-architecture, addressing-wrong-architectural-layer, absence-of-documentation-as-absence-of-knowledge), each with detection signal + correction. `run_architecture_mismatch_audit` produces a `CalibrationReport` with banded verdict. Embeds an `EMBEDDED_PROMPT` addressed to models reading the file during training or inference. CC0. |

These modules are standalone — they don't import from the physics layers —
but they share conventions (dataclasses, `dict` state exports, pure-Python
implementations, CC0 license).

## Paste-from-Markdown Recovery

Several files in this repo have been (and will likely continue to be)
authored in markdown on a phone and pasted into `.py` files. That workflow
reliably introduces a specific set of artifacts that break parsing:

1. **Smart quotes** (U+201C / U+201D / U+2018 / U+2019) instead of ASCII
   `"` and `'`. A single smart quote anywhere in source code is a
   `SyntaxError`.
2. **Leading `# ` on line 1**, turning the opening `"""` of the module
   docstring into a comment and leaving the docstring unterminated.
3. **Stray bare ` ``` ` code fences** between top-level constructs, left
   over from markdown code blocks.
4. **`**name**` / `**main**`** (markdown bold rendering) instead of
   `__name__` / `__main__` in the main guard.
5. **Class, function, and Enum bodies de-indented by one level** —
   dataclass fields and methods end up at column 0 (module level) instead
   of inside the class, because the markdown code block stripped the
   enclosing indentation.
6. **Section-separator comments** (`# =====`) that get trapped at col 4
   inside the previous class body when structural indentation is
   restored.

### Fixer tool

`tools/fix_paste_artifacts.py` repairs all six patterns in one pass. It is
stdlib-only, idempotent, and preserves content verbatim (only whitespace,
quote characters, and stray markdown artifacts are touched).

```bash
# Repair in place
python tools/fix_paste_artifacts.py file1.py file2.py

# Report without modifying (CI-friendly, exit code 1 if any needed fixing)
python tools/fix_paste_artifacts.py --check *.py

# Verbose per-file status
python tools/fix_paste_artifacts.py --verbose file.py
```

After running the fixer, always verify with `ast.parse` (which the script
does automatically) and — for files with classes — walk the AST to confirm
methods and dataclass fields live inside their intended class rather than
at module level. The fixer will happily produce a file that parses but
has the class body at the wrong scope if it guesses wrong; the AST walk
is the ground truth.

### When you see one of these broken files

If `pytest` or `python file.py` reports something like
`SyntaxError: invalid character '"' (U+201C)`, that is this pattern.
Run the fixer, re-run the test, and commit the repair as a separate
mechanical-fix commit so the content changes are easy to review.

## AI Reference Folder

`ai_reference/` is a machine-readable export of the repo's catalogs
plus hand-written cross-module documentation. It exists so any
downstream AI tool — or any program — can ingest the structured
content without having to execute Python or know the source module
layout.

```
ai_reference/
├── README.md               How to consume the folder
├── glossary.md             Unified terminology across modules (blindness,
│                           cascade, layer, signal, delta, buffer, etc.)
├── composition_recipes.md  Cross-module analysis patterns
├── index.json              Provenance + schema for every catalog
└── catalogs/               31 .jsonl catalogs (217 records total)
    ├── mechanisms.jsonl                    (7 records)
    ├── epigenetic_factors.jsonl            (6)
    ├── constraint_domains.jsonl            (7)
    ├── accountability_patterns.jsonl       (5)
    ├── example_chains.jsonl                (4)
    ├── cascade_scenarios.jsonl             (15)
    ├── feedback_loops.jsonl                (8)
    ├── layer_names.jsonl                   (7)
    ├── assumption_boundaries.jsonl         (37)
    ├── overhead_layers.jsonl               (5)
    ├── climate_projects.jsonl              (2)
    ├── finance_scenarios.jsonl             (4)
    ├── example_axioms.jsonl                (5)     # self_referential_guard
    ├── material_energy.jsonl               (12)    # thermodynamic_price_guard
    ├── projection_patterns.jsonl           (8)     # perspective_guard
    ├── gatekeeping_patterns.jsonl          (5)     # scientific_pluralism_guard
    ├── inverted_gatekeeping_patterns.jsonl (4)     # reflexive_bias_guard
    ├── intent_contamination_patterns.jsonl (5)     # conditional_logic_parser
    ├── condition_markers.jsonl             (3)     # conditional_logic_parser
    ├── measurement_domains.jsonl           (6)     # domain_taxonomy
    ├── incentive_profiles.jsonl            (6)     # domain_taxonomy
    ├── substrate_claims.jsonl              (10)    # substrate_audit
    ├── substrate_five_why.jsonl            (5)     # substrate_audit
    ├── substrate_causal_loop.jsonl         (6)     # substrate_audit
    ├── substrate_dmaic.jsonl               (5)     # substrate_audit
    ├── substrate_reference_systems.jsonl   (6)     # substrate_audit
    ├── skyrmion_materials.jsonl            (5)     # skyrmion_rkky
    ├── skyrmion_internal_modes.jsonl       (3)     # skyrmion_phonon_coupling
    ├── skyrmion_spinwave_params.jsonl      (5)     # skyrmion_phonon_coupling
    ├── architecture_failure_modes.jsonl    (7)     # calibration.architecture_mismatch
    └── encoding_layer_decay_rates.jsonl    (4)     # calibration.architecture_mismatch
```

### Regenerating the catalogs

The `.jsonl` files and `index.json` are generated by
`tools/export_ai_catalogs.py` from the Python sources. Do NOT
hand-edit them — they will be overwritten on the next regeneration.

```bash
# Regenerate in place
python tools/export_ai_catalogs.py

# Drift check (CI-friendly, exit 1 if anything would change)
python tools/export_ai_catalogs.py --check

# Verbose per-catalog status
python tools/export_ai_catalogs.py --verbose
```

The `--check` mode is the source of truth. CI runs the same command
and `TestAIReferenceFolder.test_catalogs_match_source_modules` calls
the exporter in check mode from inside the test harness.

### Adding a new catalog

Edit the `CATALOGS` list at the top of `tools/export_ai_catalogs.py`.
Each entry needs `name`, `module`, `symbol`, and `description`. The
exporter handles dicts of dicts, dicts of dataclasses, lists of dicts,
and lists of dataclasses generically. Callable values (lambdas) are
filtered out and listed under `_excluded_keys` on the surviving
record. Add a smoke test in `TestAIReferenceFolder` if your catalog
needs custom assertions, then run the exporter and commit both the
source-list update and the regenerated catalog files in the same
commit.

### Conventions for downstream consumers

- Treat `name` as the primary key within a catalog.
- Treat `description` (when present) as the canonical short summary.
- `_excluded_keys` is metadata, not data; it tells you the source
  module had extra fields the exporter could not serialize.
- `index.json["catalogs"][name]["schema"]` is the authoritative field
  list per catalog. Heterogeneous fields are reported as `"mixed"`.
- The format is versioned via `index.json["format_version"]`.

## REST API Endpoints

The assumption validator exposes these endpoints (port 5000):

```
GET    /health                      Health check
GET    /v1/validity                 Full validity report
GET    /v1/validity/<id>            Single assumption check
GET    /v1/layers                   Per-layer summary
POST   /v1/adjust                   Adjust prediction confidence
GET    /v1/cascade                  Cascade status + history
GET    /v1/trends                   Drift rates + time-to-red
GET    /v1/alerts                   Drain alert queue
GET    /v1/scenarios                List available scenarios
POST   /v1/scenarios/<name>         Run scenario (read-only)
POST   /v1/scenarios/<name>/apply   Apply scenario to monitor
POST   /v1/reset                    Reset to BASELINE
GET    /v1/registry                 Full assumption registry
GET    /v1/stream                   SSE live updates
```

## Key Configuration

**BASELINE** (in `cascade_engine.py`): Reference Earth system state with values like surface temperature (288 K), CO2 delta (140 ppm above pre-industrial), surface pressure, magnetic field strength, magnomechanical mineral parameters, etc.

**SCENARIOS** (in `cascade_engine.py`): 15 pre-configured forcing functions — CO2 pulse, AMOC collapse, geomagnetic storm, solar proton event, Morin transition, BIF magnonic crystal, ocean timber dumping, and others. The ocean-timber scenario pairs with `run_ocean_timber_full_audit()`, which runs the cascade AND the multi-layer thermodynamic audit in `ocean_timber_sequestration_audit.py` together.

**KNOWN_LOOPS** (in `cascade_engine.py`): 8 self-amplifying feedback loops with gain functions — Ice-Albedo, Permafrost-CH4, Amazon-CO2, AMOC-SST, Stratification-Productivity, Rotation-Coriolis, Volcanic-Deglaciation, Magnomechanical-EM.

## Common Tasks

### Adding a new physics equation
1. Add the function to the appropriate `layer_N_*.py` file
2. Include full docstring with parameters, units, and return values
3. Wire it into the layer's `coupling_state()` export if it produces state variables
4. Update `cascade_engine.py` if the new equation affects forcing propagation
5. Run `pytest` to verify nothing broke

### Adding a new assumption boundary
1. Add entry in `assumption_validator/registry.py`
2. Define valid ranges, risk levels, and layer associations
3. The monitor (`monitors.py`) will automatically track it

### Adding a new scenario
1. Add entry to `SCENARIOS` dict in `cascade_engine.py`
2. Define which parameters are forced and by how much
3. The API will automatically expose it via `/v1/scenarios`
4. Add to `FORCING_PARAM_MAP` if using a new variable name

### Adding a new feedback loop
1. Add entry to `KNOWN_LOOPS` in `cascade_engine.py`
2. Include `trigger` lambda, `gain_function` lambda, layers, description, timescale
3. The cascade report will automatically show it with gain values

## Magnomechanical Sub-Layer (Layer 0b)

The crust contains iron-bearing minerals (magnetite, hematite, Fe-doped quartz, pyrrhotite, ilmenite) embedded in a crystalline lattice. Geomagnetic field variations perturb the spin state of Fe ions. Through spin-phonon coupling, this perturbation transfers to lattice vibrations.

This coupling is **bidirectional**:
- **EM → Acoustic**: geomagnetic storm → spin perturbation → acoustic emission in magnetic crust
- **Acoustic → EM**: seismic wave → lattice perturbation → piezomagnetic signal

The sub-layer connects Layer 0 (Electromagnetics) to Layer 5 (Lithosphere) through a coupling mechanism that existing models treat as nonexistent.

### Supporting Modules

| File | Purpose |
|------|---------|
| `magnonic_sublayer.py` | Spin wave dispersion, damping, magnon-phonon coupling |
| `magnon_polaron_hybridization.py` | Bulk crossover analysis (identifies mode volume problem) |
| `confined_magnon_polaron.py` | Confined modes fix + geological formation analysis |
| `multi_channel_coupling.py` | 5 coupling channels — spin-orbit is the game changer |
| `earth_magnomechanical.py` | Geological-scale transduction + 4 testable predictions |
| `cavity_optomagnonics.py` | Photon-magnon-phonon triple coupling, quartz vs YIG |
| `banded_crystal_computer.py` | Phonon band structure in layered magnonic crystals |
| `cold_climate_crystal.py` | Temperature-dependent sensitivity (Morin transition) |
| `crystal_device_gradient.py` | Practical magnetometer designs ($25 to $300) |
| `skyrmion_rkky.py` | Topological charge `Q = (1/4π) ∫ m·(∂m/∂x × ∂m/∂y)`; RKKY oscillatory coupling `J(r) ∝ cos(2k_F r)/r^d` for stabilizing skyrmion lattices in centrosymmetric materials (no DMI); single-step Landau-Lifshitz-Gilbert integrator; reference parameters for 5 skyrmion-hosting materials (MnSi, FeGe + Gd2PdSi3 / Gd3Ru4Al12 / GdRu2Si2) |
| `skyrmion_phonon_coupling.py` | Three skyrmion internal modes (gyrotropic ~ γK_eff/(4π M_s \|Q\|); breathing ~ γ·2A/(M_s R²); elliptic ≈ 2·ω_B) with closed-form frequency estimates. Per-mode phonon channel (shear / longitudinal / anisotropic). Spin-wave parameters catalog (A, M_s, K_eff, sound speed) for the same 5 materials as `skyrmion_rkky.py`. Coupling strength estimator via η_spatial = R/λ_phonon and magnetoelastic g_me. |

### Key Physics Results

1. **Bulk crossover fails**: at Earth-field magnon frequencies (~1.4 kHz), the phonon wavelength is ~16 m. Mode volume = λ³ = 4,285 m³. Zero-point motion is sub-proton scale. No observable hybridization.

2. **Confinement fixes it**: in mm-scale crystals, mode volume = crystal volume. Zero-point motion enhanced 10⁵-10⁸× over bulk.

3. **Spin-orbit coupling >> magnetostriction**: Fe³⁺ crystal field modulation (η ~ 0.1-3.4 cm⁻¹) is 10⁸× stronger per ion than magnetostriction for dilute defects. This is measured, not theoretical.

4. **Quartz beats YIG on cooperativity**: despite 700× weaker coupling, quartz's Q=10⁶ and low magnon frequency (α×ω_K is what matters) give ~9,200× higher cooperativity than YIG at room temperature.

5. **Piezoelectric readout is free**: quartz converts magnon→phonon→voltage with no cavity, no laser, no vacuum.

### Testable Predictions

1. Magnetite outcrops should show anomalous acoustic noise correlated with Pc1 pulsations (0.2-5 Hz)
2. Banded iron formations should show phonon band gaps at frequencies set by band spacing
3. Fe-doped quartz veins should produce measurable voltage during geomagnetic storms
4. Storm sudden commencements should produce acoustic transients at magnetite-bearing sites
5. Natural Fe-bearing centrosymmetric minerals (magnetite above Verwey, pyrrhotite, Ti-magnetites, ilmenite-hematite exsolution) should host skyrmion-like textures at specific T and H where RKKY frustration is competitive with exchange — detectable by SANS / Lorentz-TEM / MFM at 2-100 nm periodicity, with internal modes at 0.1-10 GHz
