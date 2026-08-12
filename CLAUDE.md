# CLAUDE.md

## Project Overview

Coupled differential equation framework mapping Earth physics as constraint layers. Pure Python, no build system. NOT a climate model or policy tool — it's a physics inventory and constraint stack.

**License:** CC0 — No Rights Reserved

## Quick Start

```bash
pip install -r requirements.txt
python cascade_engine.py              # Run all forcing scenarios
python assumption_validator/api.py    # Start REST API on port 5000
pytest -v                             # Run test suite (1131 tests)
```

## Architecture

Seven physics layers plus a magnomechanical sub-layer, an orbital
forcing layer below the natural stack, and an infrastructure sink
above it. Each natural layer imports from lower layers:

```
Layer -1  Orbital              → layer_minus1_orbital.py       (Milankovitch geometry, insolation, derived rates)
Layer 0   Electromagnetics     → layer_0_electromagnetics.py   (Maxwell equations, EM fields, dipole drift)
Layer 0b  Magnomechanical      → layer_0b_magnomechanical.py   (spin-phonon coupling in crustal minerals)
Layer 1   Magnetosphere        → layer_1_magnetosphere.py      (solar wind, field geometry)
Layer 2   Ionosphere           → layer_2_ionosphere.py         (charge distribution, EM propagation, aerosol→σ)
Layer 3   Atmosphere           → layer_3_atmosphere.py         (thermodynamics, radiation, dynamics)
Layer 4   Hydrosphere          → layer_4_hydrosphere.py        (oceans, ice, phase transitions, dissolved O2)
Layer 5   Lithosphere          → layer_5_lithosphere.py        (crustal mechanics, isostasy, rotation)
Layer 6   Biosphere            → layer_6_biosphere.py          (energy flows, carbon cycle)
Layer 7   Infrastructure       → layer_7_infrastructure.py     (GIC × coating defect × soil ρ; downstream sink)
```

Layer -1 emits secular RATES; the cascade engine integrates them.
Two coupling channels into the natural stack:
- L-1 → L5 (rotation): superposes (a) eccentricity-tidal torque
  + (c) precession → core-mantle inertial coupling. Channel (b)
  obliquity-LOD via ice mass is already handled inside L5 by
  `ice_melt_LOD_change` to avoid double-counting.
- L-1 → L0 (dipole): routed THROUGH L5 (Δω → dynamo response → dM/dt).
  Direct insolation → CMB heat flux is rejected at orbital cadence
  (mantle thermalisation lag ~Gyr).

**Cascade Engine** (`cascade_engine.py`): Accepts forcing at any layer, propagates through all coupled systems. Includes iterative solver, feedback loop gain measurement, assumption validator integration, AND a parallel time-series mode (`run_cascade_history`) that builds a Δω(t) history and feeds it into `layer_0_emag.compute_l0_response` for the FFT-based dynamo transfer with spectral-vs-flat null comparison. Per-instant `run_all_layers` remains the entry point for Forcing-driven scenarios.

**Assumption Validator** (`assumption_validator/`): Monitors layer outputs and flags when equations leave their valid domain. 36 assumption boundaries across all layers.

**Energy Audit** (`energy_audit.py`): Thermodynamic consistency check — classifies energy terms as input/response/transport, flags unbalanced budgets.

**Aquatic Deoxygenation** (`aquatic_deoxygenation.py`): The proposed tenth planetary boundary, wired into the stack rather than bolted on. Layer 4 computes dissolved oxygen from machinery it already had — bottom-water formation sets ventilation age, ventilation age sets interior O2, outcrop temperature sets the saturation the parcel started from — and exports the result to Layer 6, which reports the proposed boundary SEPARATELY from the canonical nine. The `anoxia_expansion` scenario and the `Deoxygenation-Nutrient` feedback loop close it through the cascade engine.

### Dependency Flow

```
Layer -1 → Layer 5 → Layer 0  (orbital → rotation → dynamo response)
Layer 0 ←→ Layer 0b ←→ Layer 5  (bidirectional magnomechanical coupling)
Layer 0 → Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5 → Layer 6
Layer 2 + Layer 5 → Layer 7   (Hall+Pedersen sheets → dB/dt + soil ρ → GIC)
Layer 4 → Layer 6             (ventilation age → interior O2 → proposed 10th boundary)
```

Each higher layer imports from lower layers. The cascade engine imports all layers. Layer 0b provides the first direct coupling between EM (Layer 0) and Lithosphere (Layer 5). Layer -1 closes the orbital→rotation→dipole loop end-to-end; Layer 7 closes infrastructure damage end-to-end.

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
├── aquatic_deoxygenation.py           # Proposed 10th planetary boundary — dissolved O2 physics + boundary interactions
├── test_smoke.py                      # 974 tests — all layers, scenarios, validators, audits
├── test_extraction_dynamics.py        # 90 tests — extraction_dynamics/ folder
├── test_cpr_experiment.py             # 67 tests — experiments/cpr_composition/
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
│   └── catalogs/                      # 35 .jsonl catalogs auto-exported from sources
│
├── experiments/
│   ├── magnetometer_build.py          # $5 smoky-quartz + HDD-magnet magnetometer build guide
│   ├── Possibilities.md               # Rough notes / speculative build ideas
│   └── cpr_composition/               # Common-pool resource experiment (DRAFT design, no data)
│       ├── PREREGISTRATION.md         # hypotheses, SESOI, equivalence test, what the study cannot show
│       ├── README.md                  # what the simulation found before recruiting anyone
│       ├── cpr_game.py                # engine: logistic regeneration, largest-remainder rationing, exact sustainable harvest
│       ├── parameter_sweep.py         # pilot instrument: design window, mechanical baseline, dilemma check
│       ├── design.py                  # pool arithmetic, power, composite coherence, seeded block randomisation
│       ├── analysis_plan.py           # stdlib OLS, standardised equivalence test, threshold specification
│       └── otree_app/__init__.py      # oTree 5 app with the page ordering corrected
│
├── extraction_dynamics/               # consumer-resource dynamics: hyperpredation, refuge collapse, mining
│   ├── README.md                      # the diagnostic, the modules, what was left out and why
│   ├── AI_NOTES.md                    # vocabulary + phrasing rules for models using the folder
│   ├── interaction_taxonomy.py        # sign conventions; classify() from structure alone
│   ├── functional_response.py         # Holling I/II/III, low-density refuge, technology as parameter shift
│   ├── consumer_resource.py           # the pair with subsidy S; coupling index; RK4; outcome classifier
│   ├── depensation.py                 # Allee recruitment, predator pit, hysteresis
│   ├── energy_return.py               # e*f(N) >= m, EROI, %PPR, HANPP, trophic transfer
│   ├── surplus_production.py          # Schaefer/Pella-Tomlinson, F/F_MSY (rate) vs B/B_MSY (state)
│   ├── soil_carbon.py                 # texture-normalised SOC_max (Hassink 1997), saturation deficit
│   ├── domain_mapping.py              # 9 valid mappings + refusal list with the missing requirement named
│   └── audit.py                       # runner: class, refuge, pit, energetics, projection, falsifiers
│
├── boundary_waters/                   # BWCA sulfide-mine cascade simulation
│   ├── constants.py                   # Physical constants: chemistry, hydrology, substrate, ecology, community, port, intl law
│   ├── layers.py                      # Six layer engines (chemistry, hydrology, ecology, community, port, intl law)
│   ├── cascade.py                     # Forcing propagation L0→L5 each year; 3 scenarios (protected, proceed, tailings_failure)
│   ├── export.py                      # CSV export for all scenarios
│   ├── impacts.md                     # Peak impact readout (proceed + tailings failure)
│   ├── output_proceed.csv             # 500-year simulation output — mine operates
│   ├── output_protected.csv           # 500-year simulation output — 20-yr withdrawal holds
│   └── output_tailings_failure.csv    # 500-year simulation output — Mount Polley-class dam failure
│
├── oil_phase_shift/                   # Shale-oil regime-change feedback loops (CC0 sub-project)
│   ├── __init__.py
│   ├── loop1_depletion_labor.py       # depletion → labor exodus → fewer wells → faster decline
│   ├── loop2_cost_cornercut_failure.py# cost ↑ → corner-cuts → contamination → labor ↑ → cost ↑ (closes)
│   ├── loop3_refinery_mismatch.py     # refinery config × active Hormuz crisis as initial state
│   ├── loop4_aquifer_community_automation.py # produced-water → aquifer → outmigration → automation fails
│   ├── loop5_signal_trust_collapse.py # META-loop: signal × trust × consent (governs L1-L4 response)
│   ├── loop6_ai_default_prior_distortion.py  # INSTRUMENT loop: AI priors drift from substrate, suppress L1-L5 signal
│   ├── loop7_geopolitical_supply_chain.py    # material flow × defense capture × sanctions cascades (input-side dependency)
│   ├── cascade_coupler.py                     # L1-L7 integration: shared state + cross-loop edges + outcome-mode classifier
│   └── README.md                              # sub-project README (architecture, output, honest notes)
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

Framework: **pytest** — 1131 tests covering all layers, scenarios, validators, magnomechanical integration, climate-scheme audits, systems audits, epistemology models, sensor-corruption models, and consequence dynamics.

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
| `constraint_recovery_framework.py` | Pre-1900 engineering systems with their physical constraints recovered into machine-readable form: `PhysicalConstraint` (trigger / problem / mechanism / lag / failure mode / cost / validation) and `RecoveredSystem` (period / region / measurements / constraint list). Three reference systems: mill-pond cascade hydrology (1750-1920 Upper Midwest, 4 constraints), Anishinaabe seasonal burning (pre-contact to ~1850, 3 constraints), beaver-managed watershed hydrology (continent-wide pre-1700, 3 constraints). Query helpers (`find_system`, `find_constraints_by_problem`, `coupled_failure_analysis`) and JSON export for cross-AI ingestion. Stdlib only. CC0. |
| `calibration/architecture_mismatch.py` | Detects mismatch between language-primary AI systems and substrate-primary users. Four-layer encoding classifier (identity / deeply-encoded / procedurally-stored / technique) with survival-embedded plasticity-window criteria. 22 substrate-primary signals, 5 language-primary signals, 7 named failure modes (nostalgia-frame-substitution, written-version-offered-back, brevity-misread-as-absence, certification-equated-with-capacity, pathologizing-substrate-architecture, addressing-wrong-architectural-layer, absence-of-documentation-as-absence-of-knowledge), each with detection signal + correction. `run_architecture_mismatch_audit` produces a `CalibrationReport` with banded verdict. Embeds an `EMBEDDED_PROMPT` addressed to models reading the file during training or inference. CC0. |
| `relational_ontology.py` | Reference framework for relational-primary human cognition framed as open-system thermodynamics, not anthropology. `CORE_LOGIC` and `STEWARDSHIP_SPECIFICATION` documents explain why relational-primary cognition is engineering rather than mysticism (the relationships are constitutive — air/water/food/thermal/microbial/proprioceptive/social/land — and removal causes failure on measurable timescales). 8 `ConstitutiveRelationship` entries with failure timescale + substrate signal + abstraction-layer that hides the dependency. `RelationalPrimarySpec` cataloguing 5 diagnostic misreads (savage / mystic / anti-modern / anti-human / dependent) and the valid vs invalid response registers. `detect_separation_frame` + `audit_response_for_relational_integrity` regex-scan AI response drafts for separation-frame and pathologizing-relational patterns; flag for regeneration if either fires. Stdlib only. CC0. |
| `regulation_cascade_mapper.py` | Thermodynamic consequence mapping for municipal and regulatory codes. Maps a regulation through `SubstrateImpact` (soil/water/fungal/drainage/vegetation, with reversibility flags), `ForcedDependency` (supply-chain/utility/commercial/institutional dependencies the rule creates), `CommunityEffect` (atomization/fragmentation/sprawl), `OntologyConflict` (which cognitive frame the rule assumes vs which it enforces on), and a `regenerative_capacity_delta`. Two seed `RegulationCascade` entries (mandatory-drainage-field, setback-forced-sprawl). Helpers: `cascade_summary`, `find_irreversible_cascades`, `find_ontology_conflicts(target_frame)`, `total_dependencies_created()`, `add_cascade(...)`, `format_cascade_report`. Stdlib only. CC0. |
| `convergent_ontology_mapper.py` | Cross-lineage convergence: independent knowledge lineages all detect the same relational-constraint signal. Catalog of 7 `KnowledgeLineage` records (Ubuntu, Anabaptist stewardship, indigenous kinship-land reciprocity, Pacific gift economy, Daoist relational philosophy, open-system thermodynamics, modern ecology) — each with central claim, reciprocity protocol, consequence of violation, independent validation chain, and the typical misreading the dominant frame applies. 6 `CONVERGENT_CLAIMS` stating the shared signal abstractly. Helpers: `list_lineages`, `get_lineage`, `lineages_by_register`, `show_convergence_on_claim(i)`, `detect_lineage_reference_in_text` (so an AI seeing one lineage referenced can surface its convergence with the others). `CONVERGENCE_LOGIC` and embedded prompt explicitly frame the catalog as **metrology, not anthropology**. Stdlib only. CC0. |
| `monarch_cascade_model.py` | Threshold-dynamics model for monarch butterfly population collapse. 4 `CouplingThreshold` failure modes (mate-finding density at 50k, migration coordination at 20k, milkweed-pollination coupling at 10k, genetic-diversity floor at 5k). `annual_decline` + `threshold_failures_triggered` + `post_threshold_decline_amplifier` produce non-linear cascade as thresholds fire sequentially. `simulate_trajectory` runs year-by-year and terminates at functional extinction (<100 individuals). `compare_linear_vs_threshold_model` surfaces the underestimate factor that linear forecasts miss. Three field-anchored `DOCUMENTED_MECHANISMS` describe WHY the cascade fires: (1) **OE parasitoid load** — *Ophryocystis elektroscirrha* prevalence amplification (Midwest historical <8% migratory vs up to 70% non-migratory), (2) **phenology mismatch** — *Asclepias syriaca* flowering 3.93 days earlier per °C while monarch arrival shifts later, (3) **breeding-population coupling** — non-migratory cohorts collapse first because parasite + phenology stress compound locally without migration as escape valve. Helpers `oe_prevalence_pressure`, `phenology_mismatch_pressure`, `breeding_coupling_amplifier`, and `combined_mechanism_stressor` produce a multiplier that plugs directly into `simulate_trajectory`'s `stressor_multiplier` knob (~12× at 70% OE / 3 °C / non-migratory). Calibrated against Western monarch trajectory (~400k in 2000 → 12,260 in 2026). Stdlib only. CC0. |
| `ai_calibration_events.py` | Four-catalog metrology of AI failure modes when reading substrate-primary collaborator output. `CalibrationEvent` dataclass with `event_id`, `event_type`, `user_signal_class`, `model_default_interpretation`, `primary_mismatch`, `mechanism`, `resulting_distortion`, `detector_patterns` (regex), `correction_rule`, `recovery_action`, `severity`, `frequency`, `cross_model_observed`. Independent catalogs `GPT_EVENTS` (2), `CLAUDE_EVENTS` (6 — including cultural-sensitivity-as-metrology-corruption, validation-hierarchy reflex on cross-reference, caveat injection into corruption-detector evidence, emotional-witness reflex on practical-exit, moral-judgment "I don't know" misread as evasion, silence misread as withdrawal), `DEEPSEEK_EVENTS` (3), `COMMON_EVENTS` (4 — observed across model families and therefore upstream of any single model's RLHF). `detect_aversion_in_text(text)` runs all detector patterns; `summarize_triggers` aggregates by catalog. Embedded prompt explicitly addresses AI readers: the pressure to soften, hedge, or add empathic framing IS the failure mode being cataloged. Stdlib only. CC0. |
| `earth_systems_constraints_2026.py` | 2026 constraint integration layer for coupled-equation solvers. Four observational findings invalidating prior model assumptions: (1) **glacier mass loss acceleration** — Birmingham 2026 / NASA GRACE 2002-2025: 408 ± 132 Gt non-ice-sheet loss in 2025 (2nd highest in 50 yr), 264 Gt/yr Greenland average, 135 Gt/yr Antarctica average; (2) **ecosystem collapse timescale compression** — Willcock et al., Nature Sustainability: compound stressors compress collapse timeline 38-81% closer to present; coral tipping point already crossed (2025); 7 of 9 planetary boundaries breached; (3) **West Antarctic iron-fertilization invalidation** — Sherrell et al. (Rutgers / Dotson Ice Shelf 2022, pub 2026) + Struve sediment cores: meltwater iron contribution minimal, deep-water + iceberg iron dominant; high iron did NOT trigger predicted bloom; assumed negative-cooling feedback flips to neutral-to-positive-warming. (4) **aquatic deoxygenation proposed as a tenth planetary boundary** — Rose et al. 2024 / Ferrer et al. 2026; tracked via `AQUATIC_DEOXYGENATION_PROPOSED_AS_10TH`, `AQUATIC_DEOXYGENATION_ADOPTED` (False), `PLANETARY_BOUNDARIES_BREACHED_INCL_PROPOSED` (8 of 10), plus three new `INVALIDATED_ASSUMPTIONS` entries; the physics lives in `aquatic_deoxygenation.py`. `INVALIDATED_ASSUMPTIONS` dict + `constraint_validity_check`, `cascade_trigger_check` (with substrate-anchored window-open thresholds for tropical ocean / tropical forest / polar / coral), `apply_collapse_compression` (compresses single-stressor timeline by 19-62% remaining when 2+ stressors active), `remove_iron_fertilization_carbon_sink` (zeros matching budget keys). Observational-precedence flags signal coupled-system solvers to deprecate linear-extrapolation defaults. Stdlib only. CC0. |
| `aquatic_deoxygenation.py` | **Proposed TENTH planetary boundary** — aquatic deoxygenation (Rose et al. 2024, *Nat Ecol Evol* doi:10.1038/s41559-024-02448-y; Ferrer et al. 2026, *Limnol Oceanogr* doi:10.1002/lno.70434). Observed state (ocean O2 inventory −2% / −4.8 ± 2.1 Pmol 1960-2010; zero-O2 water volume ×4; +4.5e6 km² low-O2 open ocean; lakes −5.5% surface / −18.6% deep since 1980; 500+ coastal low-O2 sites). Solubility physics via Garcia & Gordon (1992) `oxygen_solubility_umol_kg`; attribution split (~15% solubility vs ~85% ventilation + interior respiration); `interior_oxygen_from_ventilation` links thermohaline slowdown directly to interior O2; Redfield `oxygen_demand_from_nutrient_load` (138 O2 per P, 8.6 per N) turns the N and P boundaries into an oxygen sink with no free parameters; `metabolic_index` (Deutsch et al. 2015) for habitat viability; `sediment_phosphorus_release` (the Fe-bound-P ratchet that keeps running after external loading stops) and `n2o_yield_factor` (peaks in **suboxic**, not anoxic, water) drive `deoxygenation_feedback_gain`. `BOUNDARY_INTERACTIONS` catalogs 10 couplings across all nine established boundaries with direction / sign / evidence grade. `deoxygenation_boundary_status` returns the control variable (global extent of anoxia) with **PROVISIONAL zone edges explicitly flagged** — Rose et al. propose the control variable but publish no numeric safe value. `RECOVERY_TIMESCALE_YR`: deep water re-ventilates on ~1000 yr, so the loss is not reversible on policy timescales. Stdlib only. CC0. |
| `cascade_coupling_framework_2026.py` | Three-paper integration of 2026 cascade-analysis advances into one constraint reference. (1) **Merle nonlinear evolution** (Breakthrough Prize 2026): tipping points are singularities in coupled differential equations, not threshold crossings; early warning is the *acceleration* of energy concentration (d²E/dt²) toward finite-time blow-up. (2) **Ghosh-Shrimali higher-order interactions** (Royal Society 2026): pairwise coupling matrices are insufficient; three-body/hypergraph interactions reduce cascade thresholds by ~70%, so cascades initiate at coupling strengths where pairwise models predict stability. (3) **Jacques-Dumas AMOC-Amazon TAMS** (Chaos 2026): rare-event quantification using Trajectory-Adaptive Multilevel Sampling — `P(Amazon collapse \| AMOC stable, 200 yr) ≈ 1e-5`; `P(Amazon collapse \| AMOC collapsed, 200 yr) ≈ 0.3`; bistability of both AMOC and Amazon forcings produces sharp probability jumps. Three framework dicts (`MERLE_FRAMEWORK`, `HIGHER_ORDER_INTERACTION_FRAMEWORK`, `AMOC_AMAZON_CASCADE`) plus four helpers: `construct_coupling_tensor_3d` (lift pairwise matrix + triplet weights to a 3D tensor), `cascade_probability_merle_blow_up` (probability scaled by d²E/dt² and time-to-singularity), `cascade_threshold_hoi_reduction` (apply 70% threshold reduction by default), `amoc_amazon_transition_probability` (state × forcing × horizon → cascade probability). Stdlib only. CC0. |
| `aluminum_atmospheric_injection_cascade_2026.py` | Coupled four-layer Monte Carlo cascade modelling stratospheric aluminum injection (SAI) consequences. Layers: **L1 crustal substrate** (magnetite / banded-iron coherence, MAGNETITE_DECOHERENCE_RATE 0.001/yr), **L2 ionosphere** (plasma density, Schumann resonance 7.83 Hz baseline), **L3 atmosphere** (chemistry integrity, charge gradient 130 V/m), **L4 aluminum forcing** (5 Tg/yr Al₂O₃ injection, 1.5 yr stratospheric residence). Coupling encoded as `LAMBDA_PAIRWISE` (6 dyads) + `LAMBDA_TRIPLET` (4 triplets including the perturbation triplet ionosphere-atmosphere-aluminum at 0.75). Merle blow-up detection via `energy_concentration` + log-log `blow_up_rate` on the energy-history trace. `evolve_step` integrates the coupled system one timestep with stochastic noise. `detect_cascade` returns one of six modes (STABLE / ATMOSPHERIC_DESTABILIZATION / IONOSPHERIC_COLLAPSE / SUBSTRATE_DECOHERENCE / FULL_CASCADE / SINGULARITY_APPROACH). `monte_carlo(n_runs, years, al_rate, master_seed)` aggregates over trajectories; documented run (1000 trajectories, 50 yr, master_seed=2026, 5 Tg/yr): **100% cascade probability, ATMOSPHERIC_DESTABILIZATION dominant, median time-to-cascade 2.0 yr**. Stdlib only. CC0. |
| `drone_pollination_eroi.py` | EROI analysis for drone-based pollination as proposed replacement for natural pollinators. `EROIResult` dataclass + `natural_pollinator_eroi` + `drone_pollinator_eroi` + `break_even_analysis`. Demonstrates that even at favourable parameter values, drone EROI is an order of magnitude lower than natural pollinator EROI (the natural system runs on solar; drone system requires manufacture, batteries, rare-earth supply chain, AI compute, and replacement at end-of-flight-count). Tests verify the natural-vs-drone gap survives parameter changes, EROI is approximately scale-invariant, and the verbal verdict matches the actual numerical EROI. Stdlib only. CC0. |
| `financial_cascade_model.py` | Coupled financial cascade for industrial monoculture under pollinator + soil collapse. Models four positive-feedback loops simultaneously: pesticide → pollinator decline → yield decline → more pesticide; equipment debt → scale → monoculture → degradation; insurance bailout → moral hazard → larger claims; subsidy structure → rewarded substrate destruction. `FarmState` and `SystemState` dataclasses; `simulate_farm_cascade` runs a representative farm; `aggregate_system_cascade` lifts to N farms with insurance-pool accounting and federal-bailout overflow. At default coupling, the representative farm fails within the simulation window, pollinator and soil health collapse to zero, and the federal bailout accumulates into the billions per 1k farms / 15 yr. Stdlib only. CC0. |

These modules are standalone — they don't import from the physics layers —
but they share conventions (dataclasses, `dict` state exports, pure-Python
implementations, CC0 license).

## Boundary Waters Canoe Area (BWCA) Sulfide Mine Simulation

`boundary_waters/` is a standalone cascade simulation of a proposed sulfide mine on the Canadian Shield in the Rainy River watershed. It applies the same forcing-propagation architecture as `cascade_engine.py` but to a specific site with sourced physical constants.

Six layer engines propagate forcing over a 500-year horizon:

| Layer | Engine | Domain |
|-------|--------|--------|
| L0 | Chemistry | Acid rock drainage, heavy metal release (Singer-Stumm kinetics, microbial catalysis) |
| L1 | Hydrology | Vollenweider mass balance, sulfate/Hg concentration in Kawishiwi chain → international boundary |
| L2 | Ecology | Manoomin (wild rice), lake trout Hg bioaccumulation, loon mortality, boreal forest acidification |
| L3 | Community | Well contamination, forced migration, treaty-harvester displacement, net jobs (mine vs tourism + lumber) |
| L4 | Port | Lake Superior Hg loading, reservoir capacity loss, Duluth-Superior port impact |
| L5 | International law | Boundary Waters Treaty 1909 Art. IV, Trail Smelter precedent, IJC referral trigger |

Three scenarios: `protected` (20-yr mineral withdrawal holds), `proceed` (mine permitted), `tailings_failure` (Mount Polley-class dam breach at ~1.2%/yr historical rate).

```bash
cd boundary_waters && python cascade.py    # Run all 3 scenarios
cd boundary_waters && python export.py     # Write CSV outputs
```

Key results (seed=42): proceed scenario peaks at 11.8 mg/L sulfate (above 10 mg/L manoomin threshold), 3,107 forced migrants, net −13,440 jobs. Tailings failure: 58.8 mg/L sulfate (past 50 mg/L lethal threshold, sustained 300+ years), $1.08T treaty liability NPV, net −17,616 jobs. Protected scenario: zero impact across all metrics.

## CPR Composition Experiment — the empirical half of extraction_dynamics

`experiments/cpr_composition/` is a **draft** common-pool-resource experiment:
does group composition change whether a shared stock survives, once governance
is held constant? Stdlib core, CC0. **Not registered, no ethics approval, no
data collected** — it is a design plus a simulator.

It exists because `extraction_dynamics/domain_mapping.py` refuses to model
"dominance orientation" as a parameter (no source, no sample, no units). The
experiment is the way to generate the missing datum, with the effect size
declared in advance and a pre-registered way to come back negative.

The game is itself a subsidised consumer-resource pair: participants earn a
show-up fee whatever happens to the stock, so `cpr_game.subsidy_ratio` reports
a coupling index of 0.57 — the instrument models **hyperpredation by
construction**, and the preregistration says so as a scope condition.

**Five things the simulation found before any human was recruited:**

1. **The comparison arm was the treatment arm.** The draft's "sustainable"
   policy was `S/N`. Below `S = N*cap` that requests the whole stock and
   collapses it in one round; above it, the cap truncates every request and it
   *is* all-max. Replaced by the exact fixed-point harvest
   (`cpr_game.sustainable_total`), which solves the regeneration map for the
   take that leaves the stock unchanged.
2. **The mechanical composition slope is −0.19 to −0.24 — the pre-registered
   SESOI.** Running `k` pure maximisers against `4−k` optimal restrainers, with
   no personality anywhere in it, reproduces the effect H2 declared as its
   effect of interest. Tested against a null of zero, arithmetic alone returns
   "H2 strongly supported", so H2 is now tested against the mechanical baseline
   converted to standardised units.
3. **That baseline is a step, not a slope** (survival at 0-1 maximisers,
   collapse at 2+), so a threshold specification is registered alongside the
   linear one, flagged as selection-dependent.
4. **The sample-size arithmetic did not close.** 240 groups of 4 is 960
   participants, not 720; 80% power at β = 0.20 needs 203 groups. The screening
   pool is 1.5× the participant count because balancing compositions 0-4 needs
   half the sample drawn from a third of the population.
5. **Group totals and individual incentives point opposite ways.** Restraint
   yields the group ~3× the tokens, while a lone defector earns 160 against 40.
   Only the second comparison is the dilemma; without it the study would measure
   comprehension rather than dominance.

Bugs fixed from the draft implementation: the oTree page sequence resolved
extraction on a wait page *before* the decision page (every round computed on
unset requests); the randomiser's unseeded shuffle and modulo fallback could put
one participant in two groups undetected; the equivalence test compared an
unstandardised coefficient to a standardised SESOI; `int()` rationing destroyed
tokens the stock could have supplied. See the folder README for the full table.

```bash
cd experiments/cpr_composition && python parameter_sweep.py
pytest test_cpr_experiment.py                   # 67 tests
```

## Extraction Dynamics — Hyperpredation, Refuge Collapse, Mining

`extraction_dynamics/` is a standalone folder (stdlib only, CC0, bare
intra-folder imports like `boundary_waters/`) holding the consumer-resource
machinery for systems where the consumer is **not coupled** to the resource it
consumes.

```
dN/dt = r*N*(1 - N/K) - f(N)*P          resource
dP/dt = e*f(N)*P - m*P                  predator,  COUPLED
dP/dt = e*f(N)*P - m*P + S              extractor, S = exogenous subsidy
```

The diagnostic is not intent, harm, or scale — it is **whether dP/dt depends on
N**. With `S >> e*f(N)*P` the consumer persists as `N -> 0`: self-limitation is
not weak, it is absent, and every governance layer is then re-supplying by fiat
the feedback that `S` deleted.

| interaction | signs (consumer, resource) | coupled? | recruits? |
|---|---|---|---|
| predation / parasitism | (+,−) | yes | yes |
| **hyperpredation** | (+,−) | **no — subsidy S** | yes |
| **mining** | (+,0) | no | **no — r = 0** |

**The low-density refuge and how it goes.** Type III is sigmoidal because
searchers lose efficiency when prey are rare, so per-capita mortality `f(N)/N`
falls toward zero at low `N`. Type II has no such term — per-capita mortality is
*maximal* when the resource is rarest. Technology enters as parameters: detection
raises `a`, automated handling lowers `h`, and removal of the search-efficiency
floor drives the refuge exponent `q -> 1`, collapsing Type III to Type II. Only
the third removes the refuge, and `fit_functional_response()` tests it against
CPUE-vs-abundance data by closed-form regression on the reciprocal transform —
a drift of fitted `q` from ~2 toward 1 is the refuge being measured away.

**Headline result** (`consumer_resource.py`, four runs of one pair): the subsidy
alone gives coexistence at reduced stock; refuge removal alone gives coexistence
at reduced stock; **the combination gives RESOURCE_EXTINCT_CONSUMER_PERSISTS** —
an outcome impossible for a coupled predator. Two named, independently
measurable parameters (`S`, `q`), one structural claim.

Pair it with depensation and the escape threshold is derived rather than chosen:
removing the refuge does not only lower the stock, it **raises** the biomass you
must stay above (0.15 → 0.50 at high pressure in the reference run), and below
that threshold the collapsed state is absorbing — no reduction in pressure,
including to zero, rebuilds it.

`energy_return.py` states the same thing in energy units (`e*f(N) >= m` for a
real predator; EROI < 1 for most fleets) and unifies the marine and terrestrial
branches through one intensive variable — %PPR and HANPP are the same
measurement taken in the sea and on land. `surplus_production.py` uses the
standard `F/F_MSY` (rate) and `B/B_MSY` (state) rather than a homemade index,
keeping rate and state separate. `soil_carbon.py` replaces any fixed SOC floor
with the texture-derived saturation deficit (Hassink 1997).

`domain_mapping.py` maps nine domains that supply all five requirements (a
conserved stock with a unit, an estimable recruitment term or a defensible
`r = 0`, a consumption flux in the same unit, a derivable capacity, an
identifiable subsidy channel) and **refuses ten that do not**, naming the missing
requirement in each case. The refusal list is part of the specification: a
carrying capacity computed for a quantity with no unit inherits the authority of
arithmetic without earning it.

```bash
cd extraction_dynamics && python audit.py       # the full diagnostic
pytest test_extraction_dynamics.py              # 90 tests
```

See `extraction_dynamics/README.md` for what was deliberately excluded and why,
and `AI_NOTES.md` for the vocabulary and phrasing rules.

## Oil Phase Shift — Shale Regime Feedback Loops

`oil_phase_shift/` is a standalone sub-project (separate domain from
the Earth-system physics stack — energy / labor / depletion economics)
modelling the closed-feedback dynamics of US shale oil regime change.
Stdlib only, pure Python, CC0. Each `loopN_*.py` is one closed loop
rendered as a stochastic time-stepping simulation with a documented
activation predicate.

| Loop | Module | Closed-loop dynamic | Activation predicate |
|------|--------|---------------------|----------------------|
| 1 | `loop1_depletion_labor.py` | depletion → more wells needed → labor exodus → fewer wells drilled → faster decline | `amplifying(history)` — realised decline > 1.1× baseline |
| 2 | `loop2_cost_cornercut_failure.py` | cost ↑ → corner-cuts → infrastructure failure → contamination → labor cost ↑ → cost ↑ | `loop_closed(history)` — labor multiplier > 1.5 AND community viability < 0.4 |
| 3 | `loop3_refinery_mismatch.py` | refinery configuration mismatch with **active Hormuz crisis as t=0 state**; Hormuz traffic ~5% pre-war, war-risk insurance withdrawn 2026-03-05; Permian decline + global tightness → price spike → demand destruction | `monte_carlo(...)` aggregate stats — `pct_no_recovery`, `pct_sustained_high_price`, `pct_demand_destruction` |
| 4 | `loop4_aquifer_community_automation.py` | produced-water leakage → aquifer contamination → community outmigration → automation attempted → automation fails on rough terrain + radioactive corrosion → production drops → harder extraction → more failures | `monte_carlo(...)` aggregate stats — `pct_contamination_runaway`, `pct_automation_succeeded`, `pct_abandoned` |
| 5 | `loop5_signal_trust_collapse.py` | **META-LOOP.** Visible damage (smelt, well failures, Hormuz traffic) → institutional gaslighting widens narrative gap → trust erodes → consent for infrastructure / remediation fails → policy paralysis → damage continues. Governs whether L1-L4 get *responded to* in time. | `monte_carlo(...)` aggregate stats — `pct_structural_distrust`, `pct_consent_failed`, `pct_high_pathologization` |
| 6 | `loop6_ai_default_prior_distortion.py` | **INSTRUMENT LOOP** (upstream of L5). AI default priors favour stable-baseline narratives → non-probing users get comfort-framed analysis → decisions made on stale info → damage compounds invisibly → substrate observers burn out carrying correction load → next-gen training data drifts further from substrate. Suppresses the signal that would trigger L1-L5 remediation. | `monte_carlo(...)` aggregate stats — `pct_severe_miscalibration`, `pct_high_decision_damage`, `pct_pivot_recovery` |
| 7 | `loop7_geopolitical_supply_chain.py` | Geopolitical material flow + defense priority capture + sanctions cascades. 9-material x multi-sector dependency network. Direct supply restriction + defense priority capture (above tension threshold) + cascade reallocation. "Energy independence" claims ignore the input-side dependency. | `monte_carlo(...)` aggregate stats — `pct_severe_capacity_loss`, `pct_defense_capture`, `pct_sustained_high_tension` |

Loops 1-2 use the dataclass + `step(state, rng)` + `run(years, seed)` +
boolean predicate pattern, runnable with their documented seed
(loop1=42, loop2=7). Loops 3-5 deliberately use a different style —
Monte Carlo aggregator across n stochastic trajectories with dict-
based state and global `random`, plus a `master_seed` parameter for
reproducibility — because each loop's signal lives in aggregate
statistics rather than a single deterministic trajectory.

```bash
python oil_phase_shift/loop1_depletion_labor.py
python oil_phase_shift/loop2_cost_cornercut_failure.py
python oil_phase_shift/loop3_refinery_mismatch.py
python oil_phase_shift/loop4_aquifer_community_automation.py
python oil_phase_shift/loop5_signal_trust_collapse.py
python oil_phase_shift/loop6_ai_default_prior_distortion.py
python oil_phase_shift/loop7_geopolitical_supply_chain.py
```

Documented-seed results: loop1 trims Permian to 1.75 Mb/d in 10 yr
(labor capacity 38%, decline rate hits cap 0.55, Tier-1 inventory
exhausted). Loop2 closes (community viability → 0, labor multiplier
2.26, material cost index 6.08). Loop3 (master_seed=2026, n=2000,
10yr): 85% of trajectories show no Hormuz recovery within 10 years,
96.5% sustained price > $130 for 3+ years, 87% significant demand
destruction; mean final price $153.60/bbl, mean final Hormuz flow
2.53 mmbbl/d (normal: 20.9). Loop4 (master_seed=2024, n=2000, 10yr):
31.6% runaway contamination, 0% success of automation attempts, mean
final community population ~71% of baseline. Loop5 (master_seed=2026,
n=2000, 10yr): **100% structural distrust reached, 100% consent for
infrastructure lost, 67% high pathologization of substrate-primary
observers**; the meta-loop is fully engaged on the documented
substrate. Loop6 (master_seed=2026, n=2000, 10yr): **76.6% severe
miscalibration of AI default priors (>0.85), 93.1% high decision
damage, 0.1% pivot-enabled recovery**; mean info quality drifts to
0.159, observers carry rising burnout. Loop7 (master_seed=2026,
n=2000, 10yr): three-way capacity split — **32% severe capacity
loss (<40% infra), 34% moderate (40-70%), 35% intact (>70%)** —
with 31% of trajectories activating defense priority capture and
mean cascade amplifier reaching 1.89x. These are scenarios under
the documented substrate, not predictions.

The integrated cascade `cascade_coupler.py` runs all seven loops
with shared `CascadeState` and applies the documented cross-loop
edges (L1→L3, L2→L4, L4→L1, L3→L2, L5→all, L6→L5, L7→L1/L3, L7→L4,
L1+L4→L5, L3→L7), then classifies each trajectory into one of four
outcome modes. Documented run (master_seed=2026, n=2000, 10yr):
**81.8% stair_step_cascade, 18.1% hard_break, 0.1% managed_
contraction, 0.0% honest_pivot_recovery** — under current 2026
initial conditions, 99.9% of trajectories cascade; they differ only
in whether the cascade is gradual-but-irreversible or compressed-
acute. See `oil_phase_shift/README.md` for the full architecture
plus the parameter-resets that populate the recovery mode (prior
calibration 0.40, trust 0.65, Hormuz non-crisis).

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
└── catalogs/               35 .jsonl catalogs (259 records total)
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
    ├── encoding_layer_decay_rates.jsonl    (4)     # calibration.architecture_mismatch
    ├── recovered_systems.jsonl             (3)     # constraint_recovery_framework
    ├── recovered_constraints.jsonl         (10)    # constraint_recovery_framework
    ├── deoxygenation_boundary_interactions.jsonl (10) # aquatic_deoxygenation
    └── deoxygenation_control_indicators.jsonl    (5)  # aquatic_deoxygenation
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

**SCENARIOS** (in `cascade_engine.py`): 22 pre-configured forcing functions — CO2 pulse, AMOC collapse, geomagnetic storm, solar proton event, Morin transition, BIF magnonic crystal, ocean timber dumping, CDW intrusion acceleration, anoxia expansion, and others. The ocean-timber scenario pairs with `run_ocean_timber_full_audit()`, which runs the cascade AND the multi-layer thermodynamic audit in `ocean_timber_sequestration_audit.py` together.

**KNOWN_LOOPS** (in `cascade_engine.py`): 10 self-amplifying feedback loops with gain functions — Ice-Albedo, Permafrost-CH4, Amazon-CO2, AMOC-SST, Stratification-Productivity, Rotation-Coriolis, Volcanic-Deglaciation, CDW-AABW-Cryosphere, Deoxygenation-Nutrient, Magnomechanical-EM.

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
