# CLAUDE.md

## Project Overview

Coupled differential equation framework mapping Earth physics as constraint layers. Pure Python, no build system. NOT a climate model or policy tool — it's a physics inventory and constraint stack.

**License:** CC0 — No Rights Reserved

## Quick Start

```bash
pip install -r requirements.txt
python cascade_engine.py              # Run all forcing scenarios
python assumption_validator/api.py    # Start REST API on port 5000
pytest -v                             # Run test suite (93 tests)
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
├── README.md
├── LICENSE
├── requirements.txt
├── .github/workflows/test.yml         # CI: pytest on Python 3.10-3.12
│
├── cascade_engine.py                  # Core forcing propagation engine
├── energy_audit.py                    # Cross-layer energy conservation audit
├── test_smoke.py                      # 93 tests — all layers, scenarios, validators
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

Framework: **pytest** — 93 tests covering all layers, scenarios, validators, and magnomechanical integration.

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest -k magnomech       # Run magnomechanical tests only
```

CI runs automatically on push via GitHub Actions (Python 3.10, 3.11, 3.12).

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

**SCENARIOS** (in `cascade_engine.py`): 14 pre-configured forcing functions — CO2 pulse, AMOC collapse, geomagnetic storm, solar proton event, Morin transition, BIF magnonic crystal, and others.

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
