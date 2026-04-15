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

---

## Guard family, substrate_audit, and domain_taxonomy

The following terms come from the guard modules, the
`substrate_audit` framework, and the `domain_taxonomy` module.
They are listed together because they share a common discipline:
validate things against physical reality, not against institutional
markers.

## anchor

- **`self_referential_guard.py`** — a node in a `DependencyGraph`
  marked as grounded in physical reality. Added via
  `mark_anchor(name, reason)`. A cycle that contains an anchor is a
  legitimate feedback loop (e.g. a thermostat). A cycle with no
  anchor anywhere reachable is a **self-referential loop**, which is
  the hazard the module detects.

This is different from an "anchor" in other contexts. In this
module it is specifically a physical-measurement node.

## grounded vs self-referential vs weakly-grounded

- **`self_referential_guard.DependencyGraph.classify_cycle`** —
  every cycle gets one of three labels:
  - `GROUNDED_FEEDBACK` — cycle contains an anchor. Thermostat,
    bank-deposit-account-balance, generational planting cycles.
    Safe.
  - `SELF_REFERENTIAL` — cycle has no anchor and none is reachable.
    Hazard. Asset prices justifying bank credit justifying asset
    prices is the textbook example.
  - `WEAKLY_GROUNDED` — cycle reaches an anchor through a path that
    leaves the cycle. Grounded but the path is indirect — verify.

## contamination

- **`model_collapse_guard.ContaminationTracker`** — data provenance
  classification. Every datum is `MEASURED` (from a physical
  instrument), `DERIVED` (computed from measured ancestors), or
  `SYNTHETIC` (generated by a model). Contamination rises as the
  synthetic fraction grows, as the generation depth grows, and as
  the longest chain without a measurement grows. A dataset where
  the model's own output has fed back into its training for several
  generations is how model collapse happens.

There is no other "contamination" in the repo. Always data
provenance.

## synthetic ancestry

- **`model_collapse_guard.py`** — for a datum, the recursive
  contribution from `SYNTHETIC` ancestors on a `[0, 1]` scale.
  Computed as `min(1.0, (prior_synthetic + 1.0) / 2)` per synthetic
  step. A value near 1.0 means nearly every ancestor is model-
  generated.

## embodied energy

- **`thermodynamic_price_guard.py`** — total energy expended to
  produce an object. Extraction + transport + processing. Measured
  in kWh. The `MATERIAL_ENERGY` catalog gives order-of-magnitude
  values per kg for 12 common materials (copper ~33 kWh/kg,
  aluminum ~47, steel ~7, concrete ~0.3, gold ~50,000).

This is the denominator of the `price_energy_check` — a price's
legitimacy is measured against the embodied energy of what was
transformed.

## EROEI

- **`thermodynamic_price_guard.eroei_check`** — Energy Return On
  Energy Invested. Ratio of useful energy produced to energy
  consumed in the production process. Below ~3:1 a society cannot
  maintain complexity. Below 1:1 the process destroys energy.
  Conventional oil in the 1930s was ~100:1; tar sands is ~5:1; corn
  ethanol is ~0.8:1 (a net sink).

This is the physical law that economics cannot override.

## substrate

- **`cascade_consequence_engine.SubstrateMap`** — a physical thing a
  goal depends on. Nodes in the substrate map are measurable
  quantities (freshwater, topsoil, stable climate, labor health,
  trade networks). Each substrate has a `min_viable` floor; drop
  below it and the substrate collapses, propagating damage to
  everything that depends on it.

"Substrate" in `substrate_audit` (the module name) means the same
thing at a larger scale: the physical base that hierarchies and
credentials and monetary systems ultimately sit on.

## self-terminating goal

- **`cascade_consequence_engine.py`** — a goal whose pursuit
  destroys the substrates the goal itself depends on. Detected when
  `cumulative_goal_damage > cumulative_goal_progress`. This is not
  a moral judgment. It is a thermodynamic fact: if the cost of
  pursuing a goal exceeds the progress toward it, the goal will fail
  regardless of intent, effort, or resources. The engine computes
  the step at which self-termination becomes inevitable.

## projection

- **`perspective_guard.py`** — a pattern where an AI system
  substitutes institutional narrative for functional assessment of
  the code. Eight categories are cataloged in `PROJECTION_PATTERNS`:
  `moral_framing`, `political_projection`, `survivalist_framing`,
  `romanticism`, `disappointment_projection`,
  `western_science_gatekeeping`, `human_motive_assumption`,
  `dominance_framing`. Each has trigger phrases and a correction.

This is not about intent. An AI projecting onto code is not being
malicious; it is faithfully reproducing patterns from its training
corpus. The guard exists to make the projection visible so it can
be corrected.

## closure

- **`perspective_guard.py` + `substrate_audit.py`** — the only
  validator. "Does the math close?" replaces "who said it?" as the
  primary question. A claim closes if its energy/mass/entropy/value
  balance holds, if its stated conservation law actually applies,
  if its units resolve, and if its assumptions are stated and
  testable. Nothing else matters: not credentials, not publication
  status, not institutional origin.

This is the principle that threads through every guard: the
physics does not care who published it.

## metrology

- **`substrate_audit.TC-9`** — the science of measurement unit
  calibration. Physical units (meter, kilogram, joule, second) are
  defined by physical constants and calibrated against international
  standards. Monetary units are not. GAAP has been revised hundreds
  of times; IFRS differs from GAAP on revenue recognition, lease
  accounting, inventory valuation; the same physical asset produces
  different dollar amounts under different standards. No
  metrological audit has ever validated any monetary unit as a
  stable measurement of a stable physical quantity.

When the `substrate_audit` conclusion says "AI hallucination is not
a model failure, it is a metrology failure," it means the training
data was measured with a broken ruler — not wrong in individual
cases, but uncalibrated as a unit.

## feedback_latency / signal_fidelity / money_physics_coupling

Three of the 11 dimensions in `substrate_audit.SystemScore`:

- **`feedback_latency`** — how fast consequence reaches the
  decision-maker. `1.0` = immediate (mechanic feels the bolt strip).
  `0.0` = years or never (CEO sees a quarterly report). From control
  theory: a feedback loop with latency longer than the system's
  characteristic timescale cannot stabilize it.

- **`signal_fidelity`** — transduction steps between the physical
  event and the decision-maker. `1.0` = zero steps (the sensor IS
  the decider). `0.0` = 10+ steps (event → local sensor → summary
  report → analyst → dashboard → meeting → exec). From Shannon:
  signal degrades with each step, and this is fundamental, not
  fixable by better reporting software.

- **`money_physics_coupling`** — does the system's value accounting
  track physical quantities (joules, kg, entropy) or monetary
  proxies? `1.0` = atomic accounting. `0.0` = purely monetary
  (GDP, quarterly earnings).

These three dimensions encode the `TC-10` argument: hierarchy is
not the enemy; signal degradation between physical event and
decision-maker is.

## incentive entropy

- **`domain_taxonomy.IncentiveAudit.incentive_entropy`** — single
  diagnostic for how much signals can be rearranged without
  changing physical reality. Computed as the average across
  channels of `gameability + (1 - outcome_coupling) +
  (1 - reward_distribution)`. Range `[0, 3]`: `0` means every reward
  is tied to a physical outcome, the decider is the sufferer, and
  nothing can be gamed; `3` means the rewards are fully decoupled
  from reality, fully gameable, and distributed away from the
  people doing the work.

This is a structural property, not a moral score. It measures
whether a system can lie about itself without physical consequence.

## gameability

- **`domain_taxonomy.IncentiveChannel.gameability`** — `[0, 1]`
  measure of whether an agent can influence a reward metric without
  improving the underlying reality the metric is supposed to track.
  `0` = not gameable (survival feedback in TEK systems — you either
  eat or you don't). `1` = fully gameable (publication novelty
  scores in academic incentive systems — a novel-sounding result
  can be engineered without a real finding).

## gradient alignment

- **`domain_taxonomy.IncentiveChannel.gradient_alignment`** — signed
  directional alignment between the reward gradient and system
  health. `+1` = every increase in the reward makes the system
  healthier. `0` = neutral. `-1` = systematically harmful (reward
  increases when the system degrades — the classic failure mode of
  extractive compensation structures).

## reality coupling

- **`domain_taxonomy.py` cross-scope comparison** — a qualitative
  descriptor for how directly a measurement domain connects to
  physical truth. `"high (local)"` for cellular biochemistry,
  `"high"` for ecological and TEK, `"medium"` for clinical,
  `"medium-low"` for affective neuroscience, `"symbolic"` for
  institutional economic. Not a numeric score; a category to
  remind the reader that different domains have fundamentally
  different baselines.

## asymmetric rigor vs inverted gatekeeping

- **`reflexive_bias_guard.py`** — two symmetric failure modes of
  validation processes:

  - **asymmetric rigor**: applying stricter thresholds to one
    tradition than another for the same check. Demanding 95%
    reproducibility from indigenous navigation but accepting 70%
    from economic theory. Detected by `RigorAudit.detect_asymmetry`.

  - **inverted gatekeeping**: dismissing Western science
    reflexively as the mirror image of dismissing indigenous
    science reflexively. Both are the same epistemological error
    in different clothes. Detected by
    `detect_inverted_gatekeeping` via phrases like "Western science
    is a religion" or "only indigenous knowledge is valid."

The module catches both directions so that anti-bias cannot become
its own bias.

## conditional vs assertion

- **`conditional_logic_parser.py`** — structural distinction that
  language models routinely conflate. A **conditional** is a
  structured statement of the form "if X then Y" (or "because",
  "when", "given that"). An **assertion** is a standalone claim
  without a stated condition.

  Example:
  - Conditional: "If Western science declares itself the only valid
    framework, then it functions as a religion." — parses to
    `condition="Western science declares itself..."`, `consequence=
    "it functions as a religion"`. Falsifiable by showing the
    condition holds but the consequence doesn't follow.
  - Assertion: "Western science is a religion." — no condition,
    no structure, not falsifiable as stated.

LLMs trained on institutional data tend to read conditional
statements as assertions and respond to the imagined emotional
intent of the speaker rather than the stated logical structure.

## intent contamination

- **`conditional_logic_parser.detect_intent_contamination`** —
  pattern class that catches when an AI response has substituted
  emotional or narrative inference for logical parsing. Five
  categories in `INTENT_CONTAMINATION_PATTERNS`:
  `emotional_inference` ("you seem frustrated"),
  `motive_insertion` ("you're trying to"),
  `narrative_construction` ("what you're really saying is"),
  `moral_mapping` ("that's a valid concern"),
  `hedging_against_precision` ("it's more nuanced than that").

When the speaker uses precise conditional logic and the AI
responds to imagined emotion, the communication fails.
