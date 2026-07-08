# earth-systems-physics
CC0 — No Rights Reserved

A coupled differential equation framework mapping all known Earth physics
as constraint layers. Electromagnetic base layer upward through magnetosphere,
ionosphere, atmosphere, hydrosphere, lithosphere, biosphere. Each layer exports
state variables and coupling interfaces to adjacent layers. A cascade engine
propagates forcing functions through the full stack. An assumption validator
reads layer outputs and flags when the equations generating them are no longer
valid.

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
| -1 | Orbital | Milankovitch geometry, insolation, secular rates |
| 0 | Electromagnetics | base constraint — atomic, molecular, field |
| 0b | Magnomechanical | spin-phonon coupling in crustal minerals |
| 1 | Magnetosphere | solar coupling, field geometry, particle trapping |
| 2 | Ionosphere | charge distribution, EM propagation, auroral energy |
| 3 | Atmosphere | thermodynamic, fluid dynamic, radiative transfer |
| 4 | Hydrosphere | phase transitions, heat transport, thermohaline |
| 5 | Lithosphere | crustal mechanics, isostasy, rotational coupling |
| 6 | Biosphere | energy flows, carbon cycle, ecosystem thresholds |
| 7 | Infrastructure | GIC × coating defect × soil ρ; downstream sink |

**Cascade Engine** (`cascade_engine.py`) — forcing propagation across all coupled layers  
**Assumption Validator** (`assumption_validator/`) — reads layer outputs, flags when equations break

---

## Cross-Domain Synthesis

[`kicked_relaxor_synthesis.md`](kicked_relaxor_synthesis.md) — One kicked-relaxor
kernel, two sign conventions: boreal extraction collapse and fire-exclusion megafire
are the same stroboscopic map. Includes `T_crit` derivation, empirical anchors
(Macdonald 2026, Mariani 2022), and a refutation protocol.

---

## Extended Modules

The full module inventory (113+ files) is documented in [`CLAUDE.md`](CLAUDE.md).
Major subsystem clusters:

| Cluster | Key files |
|---------|-----------|
| Ratchet dynamics / ecosystem accounting | `kicked_relaxor_kernel.py`, `boreal_recovery_ratchet.py`, `boreal_carbon_ledger.py`, `fuel_load_ratchet.py`, `permafrost_abrupt_ledger.py`, `amoc_hysteresis_gate.py`, `stressor_nonadditivity.py` |
| Metrology | `measurement_corruption_taf.py`, `cascade_transfer.py`, `scope_carrier_density.py`, `frozen_flow_audit.py` |
| Inference / epistemic guards | `curiosity_engine.py`, `universe_constraint.py`, `continuity_audit.py`, `self_referential_guard.py`, `reflexive_bias_guard.py` |
| Magnomechanical sub-layer | `magnonic_sublayer.py`, `skyrmion_rkky.py`, `skyrmion_phonon_coupling.py`, `cavity_optomagnonics.py` |
| Systems-analysis audits | `chattel_slavery_triple_audit.py`, `ocean_timber_sequestration_audit.py`, `substrate_audit.py`, `financial_cascade_model.py` |
| Sub-projects | `boundary_waters/` (BWCA mine cascade), `oil_phase_shift/` (shale regime feedback loops) |

---

## Install

```bash
git clone https://github.com/JinnZ2/earth-systems-physics
cd earth-systems-physics
pip install -r requirements.txt
```

## Usage

```bash
python cascade_engine.py           # Run all forcing scenarios
python assumption_validator/api.py # Start validator REST API (port 5000)
pytest -v                          # Run test suite (350+ tests)
```

---

## Machine-Readable Exports

[`ai_reference/`](ai_reference/) contains 33 JSONL catalogs (242 records)
auto-exported from source modules — mechanisms, assumption boundaries, cascade
scenarios, feedback loops, and more. See [`ai_reference/README.md`](ai_reference/README.md)
for ingestion instructions.

---

## Key Documents

| Document | Content |
|----------|---------|
| [`CLAUDE.md`](CLAUDE.md) | Full architecture, module inventory, code conventions |
| [`kicked_relaxor_synthesis.md`](kicked_relaxor_synthesis.md) | Cross-domain kernel unification |
| [`ASSESS.md`](ASSESS.md) | Assessment protocol for AI systems |
| [`ai_reference/README.md`](ai_reference/README.md) | Machine-readable catalog guide |

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

## License

CC0 — No Rights Reserved.
Use it. Modify it. Build on it. No permission needed.
