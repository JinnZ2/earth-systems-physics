# CLAUDE.md

## Project Overview

Coupled differential equation framework mapping Earth physics as constraint layers. Pure Python, no build system. NOT a climate model or policy tool — it's a physics inventory and constraint stack.

**License:** CC0 — No Rights Reserved

## Quick Start

```bash
pip install -r requirements.txt
python cascade_engine.py              # Run all forcing scenarios
python assumption_validator/api.py    # Start REST API on port 5000
```

## Architecture

Seven physics layers, each importing from lower layers:

```
Layer 0  Electromagnetics     → layer_0_electromagnetics.py   (Maxwell equations, EM fields)
Layer 1  Magnetosphere        → layer_1_magnetosphere.py      (solar wind, field geometry)
Layer 2  Ionosphere           → layer_2_ionosphere.py         (charge distribution, EM propagation)
Layer 3  Atmosphere           → layer_3_atmosphere.py         (thermodynamics, radiation, dynamics)
Layer 4  Hydrosphere          → layer_4_hydrosphere.py        (oceans, ice, phase transitions)
Layer 5  Lithosphere          → layer_5_lithosphere.py        (crustal mechanics, isostasy)
Layer 6  Biosphere            → layer_6_biosphere.py          (energy flows, carbon cycle)
```

**Cascade Engine** (`cascade_engine.py`): Accepts forcing at any layer, propagates through all coupled systems.

**Assumption Validator** (`assumption_validator/`): Monitors layer outputs and flags when equations leave their valid domain.

### Dependency Flow

```
Layer 0 → Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5 → Layer 6
```

Each higher layer imports from lower layers. The cascade engine imports all layers.

## File Structure

```
earth-systems-physics/
├── CLAUDE.md
├── README.md
├── LICENSE
├── requirements.txt
├── cascade_engine.py                  # Core forcing propagation engine
├── layer_0_electromagnetics.py        # Base constraint layer
├── layer_1_magnetosphere.py
├── layer_2_ionosphere.py
├── layer_3_atmosphere.py
├── layer_4_hydrosphere.py
├── layer_5_lithosphere.py
├── layer_6_biosphere.py
└── assumption_validator/
    ├── __init__.py                    # Package exports (v0.1.0)
    ├── registry.py                    # Assumption boundaries & risk assessment
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

Framework: **pytest**

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
```

No tests exist yet — test files should follow `test_<module>.py` naming.

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

**BASELINE** (in `cascade_engine.py`): Reference Earth system state with values like surface temperature (288 K), CO2 delta (140 ppm above pre-industrial), surface pressure, magnetic field strength, etc.

**SCENARIOS** (in `cascade_engine.py`): Pre-configured forcing functions — CO2 pulse, AMOC collapse, geomagnetic storm, and others.

## Common Tasks

### Adding a new physics equation
1. Add the function to the appropriate `layer_N_*.py` file
2. Include full docstring with parameters, units, and return values
3. Wire it into the layer's `coupling_state()` export if it produces state variables
4. Update `cascade_engine.py` if the new equation affects forcing propagation

### Adding a new assumption boundary
1. Add entry in `assumption_validator/registry.py`
2. Define valid ranges, risk levels, and layer associations
3. The monitor (`monitors.py`) will automatically track it

### Adding a new scenario
1. Add entry to `SCENARIOS` dict in `cascade_engine.py`
2. Define which parameters are forced and by how much
3. The API will automatically expose it via `/v1/scenarios`

## Known Issues

- `layer_3_atmosphere.py` contains duplicated code near the end of the file (lines ~429-486) with an unterminated docstring that prevents compilation
- No automated tests exist yet
- No CI/CD pipeline configured
