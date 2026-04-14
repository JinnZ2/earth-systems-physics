# Glossary

Terms that appear in multiple modules with subtly different meanings.
The same word can mean different specific things depending on which
file you are reading; this page keeps them straight so AI sessions and
human readers do not conflate them.

If you see a term used in the codebase that confuses you, check this
page first. If it isn't here, the convention is whatever the source
module's docstring says.

---

## blindness

- **`buffer_sensor_corruption.py`** — sensor-level deviation from
  ground truth caused by an incentive structure that rewards comfort
  over accuracy. Measured per sensor as the gap between
  `ground_truth_deviation` and `reported_deviation`.

- **`constraint_accountability_chain.py`** — institutional-level
  cumulative fidelity loss across a decision chain. Reported as
  `phenotype["institutional_blindness"]` and computed as
  `1 - product((1 - delta) for each node in the chain)`. Measures
  distortion, not intent.

The two are layered: sensor-level blindness produces the readings
that feed into the decision chain; institutional blindness is what
happens when those readings flow through several layers of comfort
choices on the way to whoever has authority to act.

## cascade

- **`cascade_engine.py`** — physics forcing propagation. A cascade is
  what happens when you apply a forcing at one layer (e.g. a 100 ppm
  CO2 pulse at Layer 3) and let it propagate through every coupled
  system. The output is a per-layer state vector after propagation.

- **`constraint_accountability_chain.py`** — `phenotype["cascade_risk"]`
  is the sigmoid-shaped probability that a chain is about to produce
  an institutional failure. It is bounded `[0, 1]` and uses
  `institutional_blindness` as its argument. Not a physical cascade;
  the metric of "this chain is about to fall over."

- **`consequence_velocity.py`** — `"cascading"` is one of the four
  phase states a `Consequence` can be in (`deferred`, `accumulating`,
  `cascading`, `realized`). It means buffer broke, deferral failed,
  and the consequence is now propagating to coupled consequences.

These three "cascades" are independent. A high `cascade_risk` in the
accountability chain may or may not eventually drive a physics
cascade in `cascade_engine`; that mapping is the analyst's job.

## layer

- **Physics layers (0-6)** in `cascade_engine.py`,
  `layer_0_electromagnetics.py` through `layer_6_biosphere.py`, and
  the magnomechanical sub-layer `layer_0b_magnomechanical.py`. These
  are constraint layers in the Earth-systems sense.

- **Institutional layers** in `constraint_accountability_chain.py`
  and `constraint_accountability_engine.py`. These are organizational
  positions in a hierarchy: `layer=0` is typically the layer where
  the ground signal is generated (worker, sensor, patient,
  researcher), and higher numbers are management / authority levels.
  Comfort_captured is supposed to climb with layer.

These two uses of "layer" do not share a coordinate system. A
`layer=3` in `cascade_engine` means atmosphere; a `layer=3` in an
accountability chain means three steps up from the ground-signal
producer in the decision hierarchy.

## signal

- **Physics**: the actual physical quantity (CO2 ppm, ocean pH, AMOC
  transport in Sv, magnetic field strength in T). Units are explicit
  everywhere in the layer modules.

- **Institutional**: a normalized severity in `[0, 1]` where 1 means
  "full severity / worst case." Used in `buffer_sensor_corruption`
  and `constraint_accountability_chain`. The normalization is
  deliberate: the chain model is unit-agnostic so it can be applied
  across domains. The cost is that absolute physical units have to
  be normalized before the chain can consume them.

Mixing the two: when an accountability chain is applied to a physics
problem (e.g. the climate finance greenwashing example), the field
biologist's `ground_signal` of 0.95 is a normalized severity, not a
specific CO2 number. The mapping from real-world physical units to
the normalized severity is the analyst's responsibility.

## delta

- **`cascade_engine.py` BASELINE**: `CO2_delta_ppm = 140` etc — the
  pre-industrial offset of the current Earth-system state. A baseline
  parameter, not a chain field.

- **`constraint_accountability_chain.py`**: `delta = abs(ground_signal - reported_signal)`,
  the per-node distortion magnitude. `delta < DELTA_THRESHOLD` (0.05)
  is the cutoff below which a decision counts as `direct_sense`;
  above it, the decision is `comfort_protect`.

When you see "delta" in a context that does not name a module, the
default meaning is usually the chain definition (per-node distortion).

## buffer

- **`buffer_sensor_corruption.py`** — the suppression capacity a
  sensor accumulates before its readings start deviating. Sensors
  with non-empty buffers can hide deviations; sensors with empty
  buffers report ground truth (or fail).

- **`consequence_velocity.py`** — `buffer_capacity` is how much of a
  consequence can be deferred before it starts producing velocity.
  `buffer_remaining` is what's left. When `buffer_remaining` hits
  zero, the consequence overflows and the phase advances toward
  `cascading`.

Both meanings share the underlying intuition: a buffer is the
accumulator that hides accumulating cost until it can no longer
absorb it. The two modules apply that intuition at different scales
(individual sensor vs. whole-consequence).

## reversion

- **`constraint_accountability_chain.py`**: the energy cost to undo a
  comfort choice. `phenotype["reversion_energy"]` is the total cost
  for the whole chain, scaled by tenure (entrenchment) and downstream
  child count. Higher tenure = more reversion energy because the
  comfort is more deeply embedded in institutional habit.

There is no other "reversion" in the repo. Always institutional.

## mechanism

- **`constraint_accountability_chain.py` MECHANISMS**: how a comfort
  distortion was enacted at a single decision point. Seven values:
  `direct_sense`, `attenuation`, `delay`, `reframe`, `delegate_down`,
  `normalize`, `silence`.

- **Magnomechanical sub-layer**: physical coupling mechanism between
  spin and phonon (e.g. magnetostriction, spin-orbit coupling, etc).
  See `multi_channel_coupling.py`.

These two uses of "mechanism" do not overlap. The chain's mechanism
is about decision behavior; the magnomechanical mechanism is about
spin-lattice physics.

## phenotype

Only used in `constraint_accountability_chain.py` and its engine. The
`phenotype` dict on a chain contains the computed outputs:
`institutional_blindness`, `ratchet_depth`, `reversion_energy`,
`cascade_risk`, `time_to_failure`. The metaphor is biological:
mutations (the per-node comfort choices) are the genome; the
phenotype is the expression of those mutations as observable
institution-level behavior.

## ratchet

- **`constraint_accountability_chain.py`**: `phenotype["ratchet_depth"]`
  counts the number of consecutive comfort_protect choices at the
  top of the chain (terminal end). The metaphor: each comfort choice
  is a notch on a ratchet that resists going back. The deeper the
  ratchet, the more institutional energy it takes to reverse course.

- `ratchet_failure` is one of the named `ACCOUNTABILITY_PATTERNS`:
  the failure mode where consecutive comfort choices compound. It is
  the default failure mode of long hierarchies under sustained
  comfort pressure.

## scenario

- **`cascade_engine.SCENARIOS`** — 15 pre-configured `Forcing` objects
  for the cascade engine. Each is a single physical forcing
  (CO2 pulse, AMOC collapse, geomagnetic storm, etc) with a layer,
  variable, magnitude, units.

- **`dollar_energy_metabolism.SCENARIOS`** — 4 financial routing
  scenarios for a climate dollar (`direct_action`, `efficient`,
  `typical_climate`, `carbon_speculation`).

- **`assumption_validator`** has its own scenario application that
  feeds a forcing from the cascade engine into the validator.

These don't conflict because the source module is always explicit,
but be careful when mixing them in conversation: "the scenarios"
without a module name is ambiguous.

## comfort_captured

Only used in `constraint_accountability_chain.py` and its engine.
It is the actor's positional leverage on `[0, 1]`, NOT a performance
score. A highly competent actor can have low `comfort_captured`
(e.g. a tenured maintenance tech in the manufacturing example) and a
less competent actor can have high `comfort_captured` (e.g. a
regional director). The model uses comfort_captured to decide
whether an attempted override succeeds: a child's direct-sense
attempt only succeeds if its `comfort_captured` exceeds the parent's.

This is a feature, not a bug. It encodes the empirical observation
that institutional leverage wins when ground-truth signals conflict
with it. If you read `comfort_captured` as "merit," you will
misinterpret every chain.

## forcing

- **`cascade_engine.py`** — a `Forcing` dataclass: an external
  perturbation applied to one of the physics layers. Has `layer`,
  `variable`, `magnitude`, `units`, `description`. The cascade engine
  propagates a forcing through every coupled system and reports the
  resulting state.

There is no other "forcing" in the repo. Always physical.

## direct_sense vs comfort_protect

Two of the most foundational terms in the meta-layer:

- **`direct_sense`** — the actor reported the signal as detected. No
  distortion. `delta < DELTA_THRESHOLD`. The dictionary spelling is
  `direct_sense` everywhere; do not write it as `direct sense` or
  `direct-sense` in code.

- **`comfort_protect`** — the actor distorted the signal in a way
  that protects their position. `delta >= DELTA_THRESHOLD`. The
  specific way the distortion happened is named by `mechanism`.

When you see `choice == "direct_sense"` or `choice == "comfort_protect"`
in code, those are the only two valid string values for that field.
The vocabulary constants `CHOICE_DIRECT_SENSE` and
`CHOICE_COMFORT_PROTECT` in `constraint_accountability_chain.py` are
the canonical spellings.
