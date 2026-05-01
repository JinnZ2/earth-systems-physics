# biocarbon_stack

Constraint-equation framework for proven biological carbon and methane
mitigation pathways. Verb-first physics. No novel genetics. No
machine-biological hybrids. No narrative closure.

CC0. Fork freely. Modify as constraints reveal.

## What this is

A coupled differential-equation skeleton that quantifies the drawdown
potential of biological systems already validated at planetary scale over
millions of years:

- wetland aerenchyma + methanotroph oxidation + peat formation
- mycorrhizal carbon locking + earthworm aggregate stabilization
- kelp forest + sea otter buffer + nested predator guild
- permafrost protection via large herbivore snow compaction
- enhanced rock weathering as held option (not collapsed answer)

The framework treats each layer as state variables coupled through
constraint equations. Parameters are given as ranges, not point estimates.
Uncertainty propagates through Monte Carlo to honest output bands.

## What this is not

Not a policy proposal. Not a moral argument. Not a forecast. The framework
holds option spaces open and surfaces the constraints that select between
options. Users (humans, AIs, communities) apply the framework to their
specific land base and knowledge holders.

## Headline numbers

```
TOTAL DRAWDOWN POTENTIAL (Monte Carlo, n=3000):
  Median:            4.0 Gt C / yr
  90% CI:            3.1 to 4.9 Gt C / yr

OFFSET OF ANTHROPOGENIC EMISSIONS (10 Gt C / yr):
  Median:            40%
  Range:             31% to 49%

OFFSET OF ATMOSPHERIC GROWTH (5.3 Gt C / yr):
  Median:            75%
  Range:             59% to 93%
```

This is not 100% of the problem. Drawdown plus emissions reduction, not
drawdown alone. The framework explicitly does not substitute for emissions
cuts.

## Module structure

```
biocarbon_stack/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md         module coupling map + composition with other JinnZ2 frameworks
│   └── OPEN_QUESTIONS.md       gaps, missing layers, validation TODOs
├── scripts/
│   └── run_full_stack.py       Monte Carlo over all parameter ranges (n=3000)
└── src/
    ├── wetland_core.py             hydrology -> anoxia -> CH4 balance -> peat
    ├── marine_core.py              kelp NPP -> deep export -> millennial seq
    ├── spike_mitigation.py         managed drawdown / harvest / inoculation / Fe-S
    ├── boundary_conditions.py      nested buffer thresholds (otter, herbivore)
    ├── redundancy_and_range_shift.py  guild stacking + 7-option range-shift space
    ├── adaptive_layer.py           earthworm + mycorrhizal load-bearing infra
    ├── geological_vector.py        ERW with stewardship integration
    ├── governance_constraints.py   constraint geometry, not specific Act
    ├── global_potential.py         extent estimates + aggregation
    ├── backwards_building.py       5-step procedure, validated on 3 geometries
    └── cross_couplings.py          documented inter-component couplings for coupled MC
```

## Verb-first physics

The framework is structured as state variables with verb-first coupling:

- saturation creates anoxia
- anoxia disables aerobic decomposition
- aerenchyma transports O2 to rhizosphere
- methanotrophs oxidize CH4
- mycorrhiza receive plant C, secrete glomalin
- earthworms convert labile C to aggregate-protected pool
- predators suppress grazers, suppression enables sink species recovery

Every coupling is a process, not an entity. This matters: it prevents
collapse to morality framing or hero-species narratives.

## What the framework explicitly holds open

These are option spaces, not resolved answers:

1. **Range-shift response** to warming (7 options from passive tracking
   to managed retreat to assisted migration to functional analog)
1. **Phase 2 drawdown** beyond the biological wedge (rock weathering,
   biochar, ocean alkalinity, BECCS, DAC - each with own EROI)
1. **Governance protocol** (competence demonstration, treaty
   recognition, land back, co-management, bottom-up continuation)
1. **Verification mechanism** (low-tech robust, not uncheatable)

Any framework that pre-selects answers to these is coating, not constraint.

## Hard limits and flagged unknowns

The Monte Carlo runs over published parameter ranges. Parameters flagged
`FLAG` in the source are not well-characterized empirically and are
treated with wider uncertainty. Examples:

- methane spike compression factors (estimated from mechanism, not derived)
- coupling lag reductions across sinks (physically plausible, not measured)
- regional invasive species risk (varies by biogeographic province)
- pre-treatment carbon cost (depends entirely on energy source)
- scaling bottlenecks (logistics, not biology, are the rate limiter)

## Regional species filter

Critical: the framework does not deploy organisms outside their native
range without explicit consideration. In particular:

- glaciated North American forests: NO European earthworm inoculation
  (Lumbricus species cause net carbon LOSS in these systems by
  stripping the duff layer)
- tropical regions: native species only, no Amynthas outside range
- wetland aquatic: native semi-aquatic species only

## Phase 0 calibration

Before scaling, deploy 100 instrumented test nodes across the major
peatland biomes (Congo, West Siberia, Hudson Bay, Sundaland, Patagonia,
Okavango, Fennoscandia, Great Lakes). Three years of high-resolution
flux data produces biome-specific Bayesian-updated rate constants.
Year 4 scale-up runs on data, not extrapolation.

## Not in this repo

- Anti-tribal-bias mitigation (separate JinnZ2 framework)
- Energy English constraint grammar (separate JinnZ2 framework)
- First-principles audit engine (separate JinnZ2 framework)
- Coating detector (separate JinnZ2 framework)
- ARM civilizational governance framework (separate JinnZ2 repo)

These compose. Run audit and coating detector across this framework
before deploying any module.

## License

CC0 1.0 Universal. Public domain. No restrictions, no attribution
required. Fork, modify, contradict, replace.

## Status

Draft. Built collaboratively across Claude and DeepSeek over a single
session that included a tornado on I-94. The framework survived the
tornado. The author was already through the worst of it before this
repo was committed.
