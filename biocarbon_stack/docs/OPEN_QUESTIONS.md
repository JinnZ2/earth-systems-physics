# Open questions and missing layers

What this framework does NOT yet cover. Each is a real gap, not a
rhetorical flourish. Each can be added as a module without disturbing
the existing structure.

## Missing biological layers

- **Mangrove and seagrass coastal carbon.** Currently lumped under
  “marine kelp.” Mangrove peat formation is closer to terrestrial
  peat dynamics than to kelp deep-export. Seagrass meadows have
  separate kinetics. Both deserve their own module.
- **Boreal and tropical forest mycorrhizal restoration.** Currently
  the adaptive layer covers earthworm + AMF. Ectomycorrhizal forest
  systems and ericoid bog systems need their own protocols.
- **Soil cyanobacterial crusts.** Drylands have biological soil crusts
  that fix nitrogen and carbon. Not in current framework. Significant
  in arid and semi-arid lands.
- **Coral-reef biogeochemistry.** Reefs are net CO2 sources via
  calcification, but reef-associated systems (seagrass behind reefs,
  algal flats) couple to net drawdown. Complex; deferred.

## Missing parameter modeling

- **Saturation hysteresis.** Drained peat does not rewet symmetrically.
  The peat structure collapses, hydraulic conductivity changes, and
  the rewet system is not the same as the original. Recovery functions
  are nonlinear. Module needed.
- **Permafrost boundary regime shift.** Once permafrost crosses thaw
  threshold, the entire equation set changes regime. Current framework
  treats permafrost as protectable. If it has already passed threshold
  in some regions, the math is different.
- **Beaver thermal range contraction.** Southern beaver range is
  contracting under warming. Hydrological regulation function has
  to be replaced or accepted as lost in those zones. Maps onto the
  range-shift option space but needs region-specific implementation.
- **Methane GWP horizon choice.** Currently using GWP100 = 28.
  GWP20 = 84. The choice matters enormously for transition spike
  accounting. Framework should run both and report both.

## Missing systems-level couplings

- **Atmospheric circulation effects of large-scale rewetting.** Major
  wetland restoration alters regional surface energy balance, latent
  heat flux, and downstream precipitation patterns. The biotic pump
  hypothesis (Makarieva and Gorshkov) suggests forest cover drives
  continental moisture transport. Restored peatlands may shift
  regional hydroclimate. Not modeled.
- **Ocean nutrient coupling from terrestrial restoration.** Restored
  wetlands change nitrogen and phosphorus delivery to coastal zones.
  Eutrophication-stressed kelp regions may recover. Hypoxic dead
  zones may shrink. Not modeled.
- **Albedo feedbacks at scale.** Permafrost herbivore restoration
  changes summer albedo. Wetland restoration changes evapotranspiration
  and cloud cover. These feed back to the temperature trajectory.
  Not currently coupled.

## Missing governance and social layers

- **Indigenous and treaty rights mapping.** The framework holds
  governance as an option space but does not enumerate which lands
  have existing recognized stewardship rights, which have unresolved
  treaty claims, and which are under contested colonial title.
- **Funding flow architecture.** “Pay people to manage land” requires
  a funding mechanism. Carbon credits are fragile. Public funding
  through what mechanism, by what authority, with what accountability?
- **AI coordination layer specification.** The framework references
  AI as monitoring and adaptive management infrastructure but does
  not specify the architecture. Voice-first cloud orchestrator
  (separate JinnZ2 build target) is the candidate. Needs explicit
  integration spec.
- **Conflict resolution between stewardship guilds.** Multi-tribal
  watersheds, contested ranges, overlapping competence claims.
  Framework needs protocol.

## Audit and validation

- **First-principles audit pass.** Run the JinnZ2 first_principles_audit
  module across every parameter and coupling in this framework. Report
  bias detection, design choice accountability, formulation comparison.
- **Coating detector pass.** Run the coating detector across this
  README and the module docstrings. Flag any self-reinforcing logic
  hiding missing parameters.
- **Cross-AI validation.** Have DeepSeek, Gemini, and Claude each
  audit this framework independently with energy_english constraint
  gate active. Report disagreements. Disagreements are signal.

## Phase 2 quantification

Phase 2 options listed in `spike_mitigation.PHASE_2_OPTIONS` are
qualitative. Each needs:

- realistic potential range (Gt C / yr) given current technology
- EROI calculation including supply chain
- failure mode analysis
- timeline to scale
- competition with Phase 1 land base

Once Phase 2 options are quantified, framework can compute:
emissions cut + Phase 1 biological + Phase 2 chosen options = total trajectory.

## Validation against observed flux data

The framework’s median estimate is 3.6 Gt C / yr drawdown from
biological systems at full restoration. Current observed terrestrial
sink is about 3.2 Gt C / yr (Global Carbon Budget 2023). Framework
should reconcile its numbers with observed sink-source partitioning,
not produce an independent estimate that floats free of measurement.
