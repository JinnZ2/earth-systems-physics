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
