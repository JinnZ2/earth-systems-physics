# Composition Recipes

How to combine the modules in this repo to do end-to-end analysis.
None of the individual files document this because it spans the whole
framework. Each recipe below names the modules it uses, the question
it answers, the inputs you need, and the steps to run.

If you are an AI session deciding which modules to use for a new
question, start here.

---

## Recipe 1: Sensor → decisions → physics forcing

**Question**: A monitoring system is reporting a benign value but the
underlying physical state is bad. How did this happen, who decided
to distort it, and what does the underlying state mean for the
coupled physics?

**Modules**:
- `buffer_sensor_corruption.py` — model the sensor layer
- `constraint_accountability_chain.py` — model the decision layer
  above the sensor
- `cascade_engine.py` — propagate the actual physical state through
  the coupled physics

**Steps**:

1. Build a `SensorNetwork` with the sensors that produced the
   reading. Use `add_integrated_sensor` for ground-truth sensors,
   `add_institutional_sensor` for buffered ones, and
   `add_corrupted_sensor` for actively suppressing ones. Call
   `read_all(ground_truth, baseline)` to get the per-sensor
   `reported_deviation` and the network-level `reality_gap`.

2. Build an `AccountabilityChain` with `chain_id` and
   `constraint_domain="safety_signal"` (or whichever applies). Add
   one `DecisionNode` per organizational layer that handled the
   sensor reports. Use `ground_signal` from the sensor network's
   true reading and `reported_signal` from each layer's report.

3. Inspect `chain.phenotype["reversion_energy"]` for the cost of
   restoring direct sensing, and `chain.find_comfort_origin()` to
   identify patient zero.

4. Independently, take the true physical reading from step 1 and
   build a `Forcing` for `cascade_engine`. Pick the right `layer`
   and `variable` from `cascade_scenarios` in
   `ai_reference/catalogs/`. Run the cascade to see how the
   underlying physics propagates if the distorted signal is taken
   at face value.

5. Compare the cascade output against the assumption boundaries in
   `ai_reference/catalogs/assumption_boundaries.jsonl` to see how
   many constraint thresholds the distorted signal puts at risk.

**Output**: a sensor-level reality gap, a decision-level reversion
energy and patient-zero identification, and a physics-level cascade
report showing what the system is actually doing while the institution
believes everything is fine.

---

## Recipe 2: Accountability chain → consequence velocity

**Question**: Given a chain that has reached a high cascade_risk,
what does the deferred consequence look like as a process and when
does its buffer break?

**Modules**:
- `constraint_accountability_chain.py` — produce the cascade_risk
- `consequence_velocity.py` — model the deferred consequence as a
  process with velocity, coupling, and phase transitions

**Steps**:

1. Build the chain (see Recipe 1, steps 1-3).

2. Read `chain.phenotype["cascade_risk"]` and
   `chain.phenotype["time_to_failure"]`.

3. Build a `Consequence` instance with a name matching the
   constraint and a `buffer_capacity` chosen to reflect how much
   institutional energy is currently absorbing the deferred cost.
   Higher cascade_risk → smaller initial `buffer_remaining`.

4. Build a `ConsequenceField` and add the primary consequence plus
   any coupled consequences (food security, public trust, regulatory
   exposure, etc). Use `couple()` to set strengths between them.

5. Iterate with `field.step(dt=1.0)` until `system_phase` is
   `"failing"` or `"collapsed"`. The number of steps until the first
   `cascading` transition is your operational time-to-failure.

**Output**: a per-consequence trajectory showing when each buffer
breaks, which consequences propagate first, and how long the system
reports `"stable"` before it reports `"failing"`. The "no gradual
warning" pattern in `consequence_velocity` is the signature you are
looking for.

---

## Recipe 3: Climate intervention full audit

**Question**: A climate finance scheme claims to sequester X tonnes
of CO2 per year. Does the project's own funding emissions exceed its
claimed benefit? Is the project itself thermodynamically a net source?
And what decision chain made this go forward despite the answer?

**Modules**:
- `dollar_energy_metabolism.py` — financial overhead audit
- `ocean_timber_sequestration_audit.py` (or analogous module) —
  full-cycle physical audit of the intervention itself
- `constraint_accountability_chain.py` — decision ancestry
- `cascade_engine.py` — physical cascade if the intervention runs
  at scale

**Steps**:

1. Run `compute_project_audit(project, scenario)` from
   `dollar_energy_metabolism` against the project. Read
   `funding_CO2_as_fraction_of_claimed`. If this exceeds 1.0 in any
   scenario, the funding alone emits more than the project claims to
   sequester. Stop and report.

2. Run the project-specific physical audit (e.g.
   `run_simulation()` in `ocean_timber_sequestration_audit`) to get
   the net physical CO2 balance and any irreversibility flags
   (anoxic, pH, thermohaline, benthic, etc).

3. Build an `AccountabilityChain` named after the project with
   `constraint_domain="ecological_constraint_signal"`. Use the
   `EXAMPLE_CHAINS["climate_finance_greenwashing"]` template as a
   starting point — replace actor roles, comfort_captured values,
   and ground/reported signals to match the project. Validate with
   `validate_chain_nodes` before building the chain.

4. Inspect the chain's phenotype. If the chain shows
   `ratchet_failure` and the physical audit shows net source, the
   institutional and physical analyses converge on the same verdict.

5. Optionally apply the intervention as a `Forcing` in
   `cascade_engine` to see the multi-layer physics cascade.

**Output**: three independent verdicts (financial, physical,
institutional). When all three agree, the audit is decisive. When
they disagree, that disagreement is the most interesting finding —
investigate why.

---

## Recipe 4: Choosing the right epistemological frame

**Question**: Why does this institution keep failing to catch the
warning signs that show up clearly in the data?

**Modules**:
- `process_epistemology.py` — choose between state-based and
  process-based epistemological models
- `constraint_accountability_chain.py` — identify which mechanisms
  the chosen frame is structurally vulnerable to

**Steps**:

1. Inspect the institution's reporting language. Does it speak in
   fixed-property terms ("the soil is fertile", "the patient is
   stable", "the budget is on track")? That is a state-based
   epistemology. Does it speak in trajectory terms ("the soil is
   trending toward depletion at rate X", "the patient's vitals are
   shifting toward Y")? That is a process-based epistemology.

2. Build a `StateModel` or `ProcessModel` from
   `process_epistemology.py` matching the institution's frame. Feed
   it a sequence of measurements that lead toward a known failure.

3. State-based models miss the trajectory because they only
   evaluate against fixed thresholds. Process-based models catch
   the velocity and acceleration ahead of threshold crossings.

4. State-based epistemologies are structurally vulnerable to two
   specific mechanisms in `MECHANISMS`: `reframe` (because they
   treat categories as fixed, so reclassifying a signal removes it
   from the relevant register) and `normalize` (because they update
   the threshold rather than tracking the trajectory). When you
   build the accountability chain for a state-based institution,
   expect those two mechanisms to dominate the comfort choices.

**Output**: a diagnosis that frames the institution's failure as an
epistemological mismatch — not a failure of intent or competence,
but a failure of the conceptual model the institution uses to read
its own signals. Recommendation: introduce process-based metrics
alongside the state-based ones; monitor velocity and acceleration,
not just absolute values.

---

## Recipe 5: Audit a system that pre-dates the chain model

**Question**: Apply the constraint accountability chain to a
historical or extra-institutional system the chain was not designed
for (e.g. one of the systems already audited in the repo, like
chattel slavery or the dollar energy metabolism).

**Modules**:
- `constraint_accountability_chain.py` — provides the vocabulary
- the existing audit module (e.g. `chattel_slavery_triple_audit.py`,
  `slavery_system_audit.py`, `innovation_regression_audit.py`) —
  provides the domain-specific structure

**Steps**:

1. Read the existing audit module to identify the layers of the
   system being audited and the signals each layer is supposed to
   transmit. The triple audit modules already enumerate the actors
   in their `DMAIC.fishbone` and `THERMODYNAMIC_AUDIT.topology`
   sections.

2. For each actor in the audit, decide which `MECHANISMS` entry
   best matches the way that actor distorted the signal. The audit's
   own analysis usually names the mechanism in plain English (e.g.
   "narrative control reframing constraint as care" → `reframe`;
   "slave patrols" → `silence` of escape attempts).

3. Build the chain. `constraint_domain` will usually be `social_signal`
   for institutional systems, but pick whichever fits.
   `comfort_captured` should rise sharply with layer because
   extraction systems specifically concentrate institutional leverage
   at the top.

4. Inspect the phenotype. Extraction systems will typically show
   `unanimous_comfort` or very deep `ratchet_failure`. The
   reversion_energy will be very high because of the long tenure
   built into the system.

5. Cross-reference with the existing audit's verdict. If both
   agree, you have an independent confirmation from a model the
   original audit did not use. If they disagree, investigate why —
   that disagreement is itself a finding.

**Output**: a chain-shaped view of a system already audited from
another angle, providing a second independent verdict via a different
methodology. When triple-audit + accountability-chain agree, the
finding is robust.

---

## General notes for AI sessions

- **Always validate inputs first.** Use `validate_node_dict` or
  `validate_chain_nodes` from `constraint_accountability_chain`
  before building any chain. The functions catch missing fields,
  unknown mechanisms, and out-of-range values; they cost nothing.

- **Always normalize signals to `[0, 1]` severity** before feeding
  them into the chain. The chain is unit-agnostic and will not
  warn you if you mix units.

- **Use `EXAMPLE_CHAINS` as templates, not as authoritative answers.**
  The four examples cover safety, ecological, health, and
  scientific domains. Pick the closest match and adapt — do not
  assume the example numbers transfer.

- **`build_example_chain(name)` is your fastest path to a working
  demo.** If you want a phenotype to inspect for sanity-checking
  your own chain, build the manufacturing example first and look
  at its output before constructing your own.

- **Cross-reference catalogs against schemas in `index.json`.** If
  you are programmatically constructing records to feed into the
  chain, the `schema` field in `index.json` tells you exactly what
  fields each catalog expects.

- **When in doubt, run `python constraint_accountability_chain.py`
  or `print_summary()`.** It prints every catalog and runs the
  manufacturing example end-to-end. It is the fastest sanity check
  that the meta-layer is working correctly.

---

## Recipe 6: Source-blind reality audit

**Question**: A new system, dataset, or claim has been presented
to you. You need to evaluate it without using institutional
markers (peer-reviewed? open-source? credentialed author?) and
without projecting narrative onto it. How do you audit it
end-to-end using only the guard family + substrate_audit +
domain_taxonomy?

**Modules** (in order):
- `input_validation_guard.py` — structural check
- `self_referential_guard.py` — grounding check
- `model_collapse_guard.py` — provenance check (if data)
- `thermodynamic_price_guard.py` — embodied-energy check (if it
  involves value or price)
- `domain_taxonomy.py` — which measurement domain applies?
- `substrate_audit.py` — compute an 11-dimension SystemScore
- `cascade_consequence_engine.py` — does pursuit destroy
  substrates?

**Steps**:

1. **Structural check.** Call
   `input_validation_guard.decompose_claim(claim)` for each claim
   in the input. Check the `grade`: `STRONG` / `PARTIAL` / `WEAK` /
   `UNTESTABLE`. If the top-level claim is `UNTESTABLE`, stop and
   report — there is nothing to audit. Do not hedge; say so
   directly.

2. **Conservation check.** Call
   `input_validation_guard.reality_audit(claims)`. The default
   registry checks energy conservation, mass conservation, entropy
   direction, value conservation, and information channel capacity.
   Any `FAILED` verdict rejects the claim regardless of source.

3. **Grounding check.** Build a
   `self_referential_guard.DependencyGraph` for the system's
   inputs. Mark every physical-measurement input as an anchor via
   `mark_anchor`. Call `audit()`. If it reports any `hazards`
   (self-referential cycles with no anchor path), the system's
   internal logic depends on its own outputs. The hazard is not
   the cycle itself — it is the missing anchor.

4. **Provenance check** (if the input is data rather than a claim).
   Build a `model_collapse_guard.ContaminationTracker`. Call
   `add_measured`, `add_derived`, `add_synthetic` for each datum in
   the chain. Call `collapse_risk()`. If the risk is `HIGH` or
   `CRITICAL`, the data has drifted from ground truth through
   recursive synthetic generation. Report the longest ungrounded
   chain.

5. **Embodied-energy check** (if the input involves monetary claims
   or resource flows). Call
   `thermodynamic_price_guard.embodied_energy` with the materials
   listed in the claim, then `price_energy_check` against the
   stated price. Verdicts of `INFLATED` or `WASTEFUL` flag a
   thermodynamic mismatch. If it is an energy system, call
   `eroei_check` separately — anything below 3:1 cannot sustain
   social complexity.

6. **Domain classification.** Look up which
   `domain_taxonomy.MEASUREMENT_DOMAINS` entry matches the question
   you are asking. Each domain has its own failure mode; a claim
   that fails the methodology of the wrong domain is a category
   error. Pull the corresponding
   `domain_taxonomy.REFERENCE_PROFILES` entry to see what typical
   incentive values look like for that domain.

7. **SystemScore.** Fill in a `substrate_audit.SystemScore` for the
   system under audit. Use the domain reference profile from step 6
   as a calibrated starting point for `feedback_latency`,
   `signal_fidelity`, `money_physics_coupling`, and
   `maintainer_control`. Read `thermodynamic_alignment` and
   `verdict`. The thresholds are explicit: `>= 0.7`
   PHYSICS-GROUNDED, `>= 0.4` MIXED, `< 0.4` CHURCH.

8. **Consequence cascade** (if the claim involves action, not just
   observation). Build a
   `cascade_consequence_engine.SubstrateMap`, mark the substrates
   the proposed action depends on, and call `CascadeEngine.simulate`
   with the proposed actions. If `self_terminating` is True, the
   action destroys its own conditions for success — the claim's
   own math disproves it.

**Output**: A single joined audit with verdicts from every stage.
If all stages pass, the claim is accepted with the note that
closure has been verified against physics, not against
credentials. If any stage fails, report the specific failure
(conservation violation, ungrounded cycle, synthetic contamination,
embodied-energy mismatch, self-termination, low SystemScore)
without softening language. The physics does not care who
published it.

**Key invariant**: Never use institutional metadata (proprietary,
open-source, peer-reviewed, reproducibility score) as a gate. Note
it for context; never let it block or unlock a verdict.

---

## Recipe 7: AI projection self-check

**Question**: You have just finished analyzing something and are
about to write a response. Before you send it, are you actually
assessing the code, or are you telling a story about it?

**Modules**:
- `perspective_guard.py` — projection pattern detector
- `reflexive_bias_guard.py` — asymmetric rigor + inverted
  gatekeeping detector
- `conditional_logic_parser.py` — intent contamination detector

**Steps**:

1. **Projection audit.** Run your draft response through
   `perspective_guard.audit_ai_response(text)`. It returns a
   `contamination_level`: `CLEAN` / `MILD` / `MODERATE` / `HEAVY`.
   If `MODERATE` or `HEAVY`, review the triggered patterns — you
   are projecting moral, political, survivalist, or romantic
   narrative onto functional code. Remove the narrative language
   and rewrite as closure description.

2. **Reflexive bias audit.** If your response evaluates multiple
   traditions, systems, or sources, run it through
   `reflexive_bias_guard.full_reflexive_audit(validation_log,
   ai_response=text)`. Check for:
   - `asymmetric_rigor`: are you applying stricter thresholds to
     one tradition?
   - `inverted_gatekeeping`: are you dismissing Western science
     reflexively as the mirror of dismissing indigenous science?
   - `framework_favoritism`: are you framing same-score results
     differently based on origin?

   If any flag, revise. Anti-bias that becomes its own bias fails
   the reflexive test.

3. **Intent contamination audit.** If the input you are responding
   to contains conditional logic (`if X then Y`, `because X then
   Y`, `given X then Y`), run your draft through
   `conditional_logic_parser.audit_statement_handling(
   conditional_inputs, response)`. If the verdict is
   `STRUCTURAL_MISMATCH`, you are responding to imagined emotion
   instead of stated logic. Re-parse the input with
   `extract_conditionals` and respond to the condition and
   consequence separately.

4. **Closure check.** After the three audits above, read your
   response one more time. For each claim you made, ask:
   - What does this describe? (function)
   - What does it close on? (conservation)
   - Where does it fail? (assumption/boundary)
   - What would test it? (measurement)

   If a sentence in your response does not fall into one of those
   four categories, it is commentary, not assessment. Delete it or
   move it to a separate "notes" section.

**Output**: A response that describes function, closure, failure
modes, and tests. No motive inference. No political framing. No
hedging against precision. No narrative translation of
conditionals. The AI is not the protagonist; the code is.

**Key invariant**: When the input is a conditional statement, the
response must parse the conditional structure before it responds
to anything else. Conditional logic is not emotion. Parse
structure before inferring intent.

---

## Recipe 8: Magnomechanical transduction stack

**Question**: Given a candidate Fe-bearing mineral outcrop or a
proposed sensor crystal, what is the full physics chain that
converts a geomagnetic or seismic perturbation into a measurable
signal, and which testable predictions apply?

**Modules** (in stack order, bottom up):
- `layer_0_electromagnetics.py` — driving EM field (geomagnetic
  baseline + perturbation)
- `magnonic_sublayer.py` — spin-wave dispersion, damping
- `magnon_polaron_hybridization.py` — bulk crossover analysis
  (mode-volume problem)
- `confined_magnon_polaron.py` — confinement fix for mm-scale
  crystals
- `multi_channel_coupling.py` — 5 coupling channels; spin-orbit
  dominates for dilute Fe defects
- `skyrmion_rkky.py` — topological charge, RKKY oscillatory
  coupling, LLG step for centrosymmetric lattices
- `skyrmion_phonon_coupling.py` — three internal modes
  (gyrotropic / breathing / elliptic) and their phonon channels
- `earth_magnomechanical.py` — geological-scale transduction +
  5 testable predictions
- `layer_0b_magnomechanical.py` — bidirectional EM ↔ lithosphere
  coupling wired into the cascade
- `layer_5_lithosphere.py` / `cascade_engine.py` — propagate the
  coupled response through the rest of the physics stack

**Catalogs used**:
- `ai_reference/catalogs/skyrmion_materials.jsonl` — radius,
  ordering T, stabilization mechanism (DMI vs RKKY)
- `ai_reference/catalogs/skyrmion_internal_modes.jsonl` — three
  modes with frequency scaling + phonon channel
- `ai_reference/catalogs/skyrmion_spinwave_params.jsonl` —
  A_exchange, M_s, K_eff, sound speed per material (keys align
  with skyrmion_materials)

**Steps**:

1. **Identify the host material.** Look it up in
   `skyrmion_materials.jsonl`. The `rkky_relevant` flag splits
   DMI-stabilized (non-centrosymmetric, MnSi/FeGe) from
   RKKY-stabilized (centrosymmetric Gd-based). Natural
   Fe-bearing minerals (magnetite above Verwey, pyrrhotite,
   Ti-magnetite, ilmenite-hematite exsolution) fall in the
   centrosymmetric class and are the targets of prediction #5
   in `earth_magnomechanical.py`.

2. **Check confinement.** Call
   `magnon_polaron_hybridization` at Earth-field magnon
   frequencies (~1.4 kHz). Mode volume = λ³ ≈ 4,285 m³ → no
   observable hybridization in bulk. If the sample is mm-scale
   or larger, switch to `confined_magnon_polaron` — mode volume
   = crystal volume and zero-point motion is enhanced 10⁵-10⁸×.

3. **Pick the dominant coupling channel.** For dilute Fe
   defects, `multi_channel_coupling` shows spin-orbit
   (Fe³⁺ crystal field modulation, η ~ 0.1-3.4 cm⁻¹) is 10⁸×
   stronger per ion than magnetostriction. For concentrated
   magnetic phases (magnetite, pyrrhotite), magnetoelastic
   B₁/B₂ coupling dominates — use the per-mode `coupling_type`
   column in `skyrmion_internal_modes.jsonl`.

4. **Compute mode frequencies.** Join
   `skyrmion_spinwave_params.jsonl` to
   `skyrmion_materials.jsonl` on material name. Feed
   A_exchange, M_s, K_eff, and radius_nm into
   `skyrmion_phonon_coupling.all_internal_modes_Hz` (or
   `modes_for_material(name)` for defaults). Expect
   gyrotropic 0.1-1 GHz, breathing 1-10 GHz, elliptic 2× breathing.

5. **Estimate phonon coupling.** Call
   `skyrmion_phonon_coupling.coupling_strength` with the
   chosen mode and the material's sound speed. The returned
   `eta_spatial = R / λ_phonon` tells you whether the
   skyrmion is a point scatterer (η « 1) or a distributed
   resonator (η ~ 1). `g_dimensionless` is the
   magnetoelastic coupling normalized to the mode frequency.

6. **Wire to the cascade.** `layer_0b_magnomechanical.py`
   provides the bidirectional EM↔lithosphere coupling. Use
   `cascade_engine.run_scenario("magnetite_acoustic_coupling")`
   or set a custom `Forcing` on layer 0 variable
   `B_geomagnetic_delta`. The cascade report will show gain
   through the `Magnomechanical-EM` feedback loop in
   `KNOWN_LOOPS`.

7. **Map to a testable prediction.** The five predictions in
   `earth_magnomechanical.PREDICTIONS` are:
   1. Magnetite outcrops + Pc1 pulsations (0.2-5 Hz)
   2. BIF phonon band gaps
   3. Fe-doped quartz veins + geomagnetic storm voltage
   4. Storm sudden-commencement acoustic transients
   5. Skyrmion textures in natural centrosymmetric Fe minerals
      (SANS / Lorentz-TEM / MFM, 2-100 nm periodicity,
      internal modes 0.1-10 GHz)

   Pick the prediction whose `host_material` and
   `observation_technique` match your sample, then use its
   `field_window_T`, `temperature_window_K`, and
   `frequency_window_Hz` as the instrument-setting envelope.

**Output**: a material → mode → phonon-channel → cascade-loop →
testable-prediction chain. Every step is joined by name against
a catalog under `ai_reference/catalogs/`; no step depends on
running the physics modules (though running them gives sharper
numbers than the order-of-magnitude catalog values).

**Key invariant**: Centrosymmetric Fe-bearing minerals need
RKKY frustration, not DMI, to host skyrmion-like textures.
Applying MnSi/FeGe DMI parameters to magnetite or pyrrhotite
produces a category error that will silently give wrong
lifetimes and wrong fields. Always check `rkky_relevant`
before joining spin-wave params.

---
