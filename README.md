# earth-systems-physics
CC0 — No Rights Reserved

A coupled differential equation framework mapping all known Earth physics
as constraint layers. Electromagnetic base layer upward through magnetosphere,
ionosphere, atmosphere, hydrosphere, lithosphere, biosphere. Each layer exports
state variables and coupling interfaces to adjacent layers. A cascade engine
propagates forcing functions through the full stack. An assumption validator
reads layer outputs and tells you when the equations generating them are no
longer valid.

This is not a climate model.
It is not a policy tool.
It is not built for public communication.

It is built because the planet is a single thermodynamic engine and the
equations do not care about institutional boundaries.

---

## Core Premise

Every Earth system — electromagnetic, atmospheric, hydrological, biological,
crustal, magnetospheric — is coupled. Energy and mass are conserved. Forcing
one layer redistributes across all others. Interventions cannot be isolated.
Cascade failures propagate through couplings that siloed models cannot see.

---

## Architecture

Physics is organized as a pyramid of constraint layers:

| Layer | Domain | Scope |
|-------|--------|-------|
| 0 | Electromagnetics | base constraint — atomic, molecular, field |
| 0b | Magnomechanical | spin-phonon coupling in crustal minerals |
| 1 | Magnetosphere | solar coupling, field geometry, particle trapping |
| 2 | Ionosphere | charge distribution, EM propagation, auroral energy |
| 3 | Atmosphere | thermodynamic, fluid dynamic, radiative transfer |
| 4 | Hydrosphere | phase transitions, heat transport, thermohaline |
| 5 | Lithosphere | crustal mechanics, isostasy, rotational coupling |
| 6 | Biosphere | energy flows, carbon cycle, ecosystem thresholds |

**Cascade Engine** — forcing propagation across all coupled layers
**Assumption Validator** — reads layer outputs, flags when equations break

## Magnomechanical Sub-Layer (Layer 0b)

The crust contains iron-bearing minerals (magnetite, hematite, Fe-doped quartz,
pyrrhotite, ilmenite) embedded in a crystalline lattice. Geomagnetic field
variations perturb the spin state of Fe ions in these minerals. Through
spin-phonon coupling (crystal field modulation at the Fe site), this
perturbation transfers to lattice vibrations.

This coupling is bidirectional:
- **EM -> Acoustic**: geomagnetic storm -> spin perturbation -> acoustic emission in magnetic crust
- **Acoustic -> EM**: seismic wave -> lattice perturbation -> piezomagnetic signal

The sub-layer connects Layer 0 (Electromagnetics) to Layer 5 (Lithosphere)
through a coupling mechanism that existing models treat as nonexistent.

### Supporting Modules

| File | Description |
|------|-------------|
| layer_0b_magnomechanical.py | Magnomechanical coupling state |
| magnonic_sublayer.py | Spin wave physics engine |
| magnon_polaron_hybridization.py | Magnon-phonon crossover analysis |
| confined_magnon_polaron.py | Confined mode + geological analysis |
| multi_channel_coupling.py | Multi-channel enhancement |
| earth_magnomechanical.py | Geological-scale transduction |
| banded_crystal_computer.py | Phonon band structure in layered magnonic crystals |
| cold_climate_crystal.py | Temperature-dependent sensitivity analysis |
| crystal_device_gradient.py | Frequency-shift magnetometer design |

Each layer exports:
- State variables
- Governing equations
- Coupling interfaces to adjacent layers
- Known phase transition thresholds

---

## Install

```bash
git clone https://github.com/JinnZ2/earth-systems-physics
cd earth-systems-physics
pip install -r requirements.txt
```

## Usage

```bash
# Run all forcing scenarios
python cascade_engine.py

# Start assumption validator REST API (port 5000)
python assumption_validator/api.py
```

---

## What This Is Not

- Not a simulation of a specific scenario.
- Not a tool that produces policy recommendations.
- Not a model that linearizes nonlinear systems for convenience.
- Not an explainer for general audiences.

## What This Is

- A physics inventory.
- A constraint stack.
- An equation engine that prevents bad reasoning by making costs visible.
- A system that knows when its own assumptions are breaking.

---

## File Structure

```
earth-systems-physics/
├── README.md
├── requirements.txt
├── layer_0_electromagnetics.py
├── layer_1_magnetosphere.py
├── layer_2_ionosphere.py
├── layer_3_atmosphere.py
├── layer_4_hydrosphere.py
├── layer_5_lithosphere.py
├── layer_6_biosphere.py
├── cascade_engine.py
└── assumption_validator/
    ├── __init__.py
    ├── registry.py
    ├── monitors.py
    └── api.py
```

---

## License

CC0 — No Rights Reserved.
Use it. Modify it. Build on it. No permission needed.
