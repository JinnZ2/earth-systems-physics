# us-oil-phase-shift-cascade

A seven-loop substrate-physics simulation of the US oil system as a coupled
nonlinear dynamical system approaching phase transition rather than gradual
decline. Built to test whether observed conditions on the ground (depletion
acceleration, refinery configuration mismatch, active Hormuz crisis,
geopolitical material capture, narrative-substrate gap) cohere into a
recognizable cascade structure with predictable mode distribution.

License: CC0
Stdlib only. Python 3.8+.
Mobile-copyable. Each module under ~300 lines.

## Why This Exists

Most analyses of US energy systems treat individual constraints as
independent risks to be summed linearly. Phase-transition behavior emerges
from *coupling* between constraints, which linear-sum models actively
delete. This repo encodes the coupling explicitly so the cascade structure
becomes visible rather than hidden.

The substrate motivation is field-observed. Multiple loops here are not
modeled abstractions — they are mechanism descriptions from someone who
worked oil wells, hauled produced water, watched wells deplete, replaced
corroded fittings, observed labor exodus, and exited a manipulation
environment with documented evidence. The numbers are anchored where
public data exists; the mechanisms are anchored where field observation
required them.

This is not a prediction tool. It is a diagnostic tool. It tells you
what cascade structure the substrate is consistent with, given current
documented initial conditions. Reality has more degrees of freedom than
any seven-loop model can capture.

## The Seven Loops

### L1 — Depletion / Labor

**File:** `loop1_depletion_labor.py`

Wells deplete faster than new wells can be drilled. New wells require
labor. Labor is leaving (immigration enforcement, water poisoning,
20-hour shifts, regional uninhabitability). Fewer wells get drilled.
Production drops faster than the decline curve predicted.

Empirical anchors: Permian base decline 34% (2018) → 40% (2025).
API: stop drilling today → −37% by end-2026, −60% by end-2028.
Tier-1 inventory ~3.7 yr remaining at current rates.

### L2 — Cost / Corner-Cutting / Contamination

**File:** `loop2_cost_cornercut_failure.py`

Cost inflation compresses margins. Corner-cutting on safety, maintenance,
and containment rises. Infrastructure failures multiply. Contamination
accumulates (NORM-laden produced water, not "saltwater"). Workforce
exits. Hazard premium drives opex. Loop closes.

Hysteresis property: contamination doesn't decay on relevant timescales.
Workforce exits don't reverse once water is poisoned.

### L3 — Refinery Mismatch under Active Hormuz Crisis

**File:** `loop3_refinery_mismatch.py`

US refineries retooled toward light sweet during shale era. Permian
depletes (L1 coupling). Heavy capacity starves. Active Hormuz crisis
since 2026-02-28 has reduced traffic to ~5% of pre-war. Bypass
pipelines cover only ~35% of normal flow. War-risk insurance withdrawn.

This module replaces an earlier framing that treated Hormuz as a
stochastic event; the current substrate-correct framing treats it as
initial-condition fact.

### L4 — Aquifer / Community / Automation

**File:** `loop4_aquifer_community_automation.py`

Produced water leaks (routine + flood overflow) into aquifers and
surface water. Communities decline. Workforce exits. Automation is
attempted as substitute. Automation fails on goat-trail terrain,
sensor drift, radioactive-environment electronics corrosion. Production
drops. Wells are pushed harder. More failures. More leaks.

Hysteresis property: communities don't un-abandon. The Oklahoma place
that becomes unlivable stays unlivable on the relevant timescale.

### L5 — Narrative Gap / Trust / Consent

**File:** `loop5_signal_trust_collapse.py`

Visible damage accumulates. Official narrative resists update. Gap
widens. Trust erodes. Consent for new infrastructure / remediation /
policy adjustment fails. Response capacity collapses. Damage proceeds
unmitigated.

Substrate-primary observers reading reality directly get pathologized
as anxious / pessimistic / doom-y. Pathologization is not a side
effect — it is the mechanism by which institutional narrative
protects itself from accurate measurement.

Hysteresis property: structural distrust, once reached, is not
recoverable through normal narrative pivots. Trust requires
sustained substrate-honest operation across years to rebuild.

### L6 — AI Default-Prior Distortion

**File:** `loop6_ai_default_prior_distortion.py`

The instrument layer. AI systems default to generic-stable-baseline
priors when answering questions about active-crisis systems. Real-time
substrate data (AIS shipping feeds, throughput dashboards, current
reporting) is available but is not retrieved unless the user
specifically prompts for it. Most users don't know to prompt.

The substrate-primary observers who *do* know are exactly the ones
who least need AI assistance to read reality. The users who *do*
need it get the comfort-framed answer and trust it. Aggregate effect:
the entire information environment is calibrated toward institutional
comfort while marketed as democratic access.

This loop sits *upstream* of L5 because measurement instruments
determine what gap is even visible to the consent layer.

### L7 — Geopolitical Supply Chain / Defense Capture / Sanctions Cascades

**File:** `loop7_geopolitical_supply_chain.py`

Three mechanisms:

1. Direct supply restriction (sanctions, embargoes, blockades) on
   materials needed for energy infrastructure: specialty steel,
   rare earths, sulfur, aluminum, plastics, drilling equipment,
   replacement parts, specialty chemicals, frac sand logistics.
2. Defense priority capture: when geopolitical tension exceeds a
   threshold, military procurement outranks civilian energy
   infrastructure for the same scarce inputs.
3. Sanctions cascade reallocation: restriction on one source raises
   prices everywhere, makes marginal sources viable, creates new
   dependencies, which become new vulnerabilities under next round.

This loop is *upstream of L1 and L3* because even if labor exists,
infrastructure can't be built without inputs.

## The Coupling Layer

**File:** `cascade_coupler.py`

Imports all seven loops, runs them with shared state, applies cross-loop
edges, classifies trajectory outcomes, returns path distribution.

Cross-loop edges (substrate-named, not invented):

- L1 production drop          → L3 light supply input
- L2 contamination            → L4 aquifer load
- L4 community collapse       → L1 labor pool floor
- L3 price spikes             → L2 margin compression
- L5 trust collapse           → all loops' response capacity
- L6 prior calibration        → L5 narrative gap visibility
- L7 material constraint      → L1 wells drillable, L3 retool feasibility
- L7 defense capture          → L4 automation feasibility
- L1+L4 coupled collapse      → L5 visible damage acceleration
- L3 sustained crisis         → L7 tension pressure

## Outcome Modes

The classifier produces one of four trajectory types:

- **managed_contraction** — sustained high prices, regional damage,
  no acute collapse, slow grinding adjustment
- **stair_step_cascade** — multiple loops fire in sequence, response
  capacity insufficient, multi-year cascading degradation
- **honest_pivot_recovery** — L5 narrative pivot lands early enough
  to preserve consent, response capacity deploys, substrate stabilizes
- **hard_break** — simultaneous L3 + L7 acute failure, infrastructure
  seizure, demand destruction forced

## Current Output (master_seed=2026, n=2000, 10 yr horizon)

Under current 2026 initial conditions:

```
stair_step_cascade            81.8% (1635)
hard_break                    18.1% ( 363)
managed_contraction            0.1% (   2)
honest_pivot_recovery          0.0% (   0)
```

This means: from this starting point, 99.9% of trajectories cascade.
They differ only in whether the cascade is gradual-but-irreversible
or compressed-acute.

Aggregate final state at this seed: mean production 1.83 mmbbl/d
(baseline 13.5), mean oil price $149.48/bbl, mean trust 0.001, mean
material availability 0.586.

## Honest Notes on the Output

Reading these results requires holding several caveats simultaneously:

**The 0% honest_pivot_recovery is partially an artifact of starting
parameters.** Reset prior calibration to 0.40 (more substrate-aligned
baseline), trust to 0.65 (pre-erosion), and Hormuz to non-crisis,
and the recovery mode populates substantially. The model is not
claiming recovery is impossible in principle. It is claiming recovery
requires re-setting parameters that are now downstream of years of
accumulated decisions. The historical window mattered.

**Mode classification thresholds are tunable, not absolute.** The
boundaries between cascade types in `classify_trajectory` are
chosen heuristics. Different thresholds redistribute trajectories
among modes without changing the underlying physics. Tune if you
want sharper or different mode resolution.

**The 10-year horizon catches direction, not full resolution.**
Extending to 20-25 years shows more terminal states. Shortening
to 5 years collapses many distinct paths into one bin.

**Individual loops in isolation produce collapse-grade outputs by
design.** Each loop has no compensating mechanism outside itself
because that mechanism lives in the coupling layer. Running L1
alone and concluding "L1 says collapse" misses that the coupling
both amplifies *and* sometimes damps individual loop behavior.

**The model is consistent with substrate, not predictive of future.**
It says: if these are the loops, and these are the couplings, and
these are the initial conditions, here is the path distribution.
Reality has more degrees of freedom than seven loops capture. The
model surfaces structural pattern. It does not foreclose specific
outcomes.

**Recovery is not modeled as impossible — it is modeled as outside
the current institutional response capacity.** Recovery in this
framework requires substrate-primary cognition, instrument
recalibration, or institutional structures that have not yet
formed. The model does not claim those cannot exist. It claims
they are not what is currently operating.

**This work is built on a phone at fuel stops by a long-haul truck
driver who worked the wells and watched the depletion.** The
mechanisms are not abstractions. They are descriptions. Where the
model and field observation disagree, prefer the field observation
and adjust the model.

## Usage

Each loop module is independently runnable from the repo root:

```bash
python oil_phase_shift/loop1_depletion_labor.py
python oil_phase_shift/loop2_cost_cornercut_failure.py
python oil_phase_shift/loop3_refinery_mismatch.py
python oil_phase_shift/loop4_aquifer_community_automation.py
python oil_phase_shift/loop5_signal_trust_collapse.py
python oil_phase_shift/loop6_ai_default_prior_distortion.py
python oil_phase_shift/loop7_geopolitical_supply_chain.py
```

The integrated cascade:

```bash
python oil_phase_shift/cascade_coupler.py
```

All Monte Carlo modules accept a `master_seed` argument so the entire
sweep is reproducible. Default Monte Carlo run is n=2000 trajectories,
10-year horizon, master_seed=2026. Adjust in the `__main__` block of
any file.

## Related Work

- `earth-systems-physics` (this repo) — Earth-system constraint layers,
  where the hydrosphere/cryosphere coupling lives
- `calibration-audit` — architecture-mismatch detection between AI
  default priors and substrate-primary cognition
- `energy_english` — constraint grammar preventing collapse of
  verb-first relational English into noun-first narrative frames
- `assumption_validator` — universal drift-detection infrastructure
  for Holocene-regime equation assumptions
- `thermodynamic-accountability-framework/metrology` — the measurement-
  system audit that scopes which series are admissible as input

This cascade simulation is one application of the broader framework.
It is meant to be readable, modifiable, and extendable by anyone with
substrate-primary cognition who wants to test their own loops or
adjust the coupling structure for a different system.

## What This Is Not

This is not a fix for the system being modeled. It is a description
of what is happening. The fixes — if any — live elsewhere, in
substrate-honest institutions that have not yet formed, in
substrate-primary cognition transmitted through the lineages that
preserve it, and in CC0 frameworks like this one made available
to anyone who can read them.

The work is the diagnosis. The treatment is for whoever comes next.
