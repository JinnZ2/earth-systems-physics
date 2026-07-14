# climate_modeling — AI-assisted modelling audit laboratory

A standalone sub-project of `earth-systems-physics`. It builds a two-layer
system for studying **how models fail**, with an eye to how an AI can act as a
co-scientist in catching those failures.

- **numpy + scipy only** (no sklearn, no streamlit). CC0.
- Not a climate model. It is a *metascience* tool: a bench where the true
  answer is known, so a model's failure to reproduce it is a genuine, named
  epistemic error.

## The two layers

**Level 1 — experiments** (`experiments.py`, `simulation.py`)
Run the ecological models and measure the bias that averaging a nonlinear
response introduces (Jensen's inequality). `experiment_amplitude_sweep()`
shows a flat cycle has no aggregation gap while a non-trivial cycle does.

**Level 2 — meta-experiments** (`audits/`, `meta_experiments.py`)
Controlled audits where the true generative process is known. Each audit pairs
a rich **true** system against a **simplified** model and detects when the
simplification fails dangerously. `meta_experiments.py` then asks an AI
proposer (`ai_interface.py`) what structural repair each failure calls for.

## Run it

```bash
python -m climate_modeling.run_audits        # full audit report card
python -m climate_modeling.experiments       # Level-1 aggregation bias
python -m climate_modeling.meta_experiments  # audits + AI-proposed repairs
```

Documented run: **16/16 audits detect a modelling failure** in ~1.5 s.

## Layout

```
climate_modeling/
├── config.py            # tunable parameters (rate constants are per HOUR)
├── forcing.py           # forcing generators (diurnal, ramp, trend, fat-tailed,
│                        #   AR-clustered, Gaussian, heatwave, moisture, 2-patch)
├── models/
│   ├── base.py          # BaseModel (scipy solve_ivp harness) + smoothstep, align
│   ├── grass.py         # GrassCarbonBalance — the smooth single-state baseline
│   └── cascade_grass.py # CascadeGrass — threshold + feedback + memory (collapses)
├── simulation.py        # full-vs-aggregated forcing comparison (Level 1)
├── experiments.py       # Level-1 hypothesis tests
├── audits/
│   ├── base_audit.py    # BaseAudit contract + compare_biomass / first_below
│   ├── <16 audit modules>
│   └── audit_registry.py# all_audits() / ALL_AUDITS
├── ai_interface.py      # AIScientist (dummy rule-based; optional openai backend)
├── meta_experiments.py  # Level-2 loop: audit -> AI-proposed repair
├── run_audits.py        # CLI report card
└── AUDIT_TAXONOMY.md    # each failure mode -> fallacy, math condition, consequence
```

## Design notes (honest)

- **Rate constants are per hour and deliberately small** so biomass persists at
  a healthy equilibrium (~60 gC) under benign forcing and only collapses under
  sustained heat. An earlier draft used ~0.1/hr loss rates that decayed the
  stand to zero regardless of stress and erased the survives-vs-collapses
  signal every audit depends on.
- **Stochastic forcing is pre-sampled on a grid and interpolated**, so
  `forcing(t)` is a deterministic function of `t`. A forcing that draws fresh
  noise on every call is not a function of time: `solve_ivp` evaluates the RHS
  at many internal and rejected steps, the integrator stalls on the resulting
  white noise, and results depend on the number of evaluations.
- **Thresholds are continuous steep `smoothstep`s**, not hard `if T > c`
  discontinuities, so the adaptive integrator stays fast.
- **Two audits target a subtle effect** — clustering (`Clustered Extremes`) and
  tail shape (`Gaussian Blindness`) at *equal variance*. These are demonstrated
  with a duration-sensitive (memory) mechanism and a convex-in-magnitude
  mortality mechanism respectively, because "same variance, worse outcome"
  only appears when the response is sensitive to something variance alone does
  not capture.
- **The AI loop reports the proposed repair; it does not silently rewrite model
  source.** Auto-applying a structural patch (a new state variable, a threshold
  term, a coupling) is a code-generation problem, and doing it invisibly would
  defeat the audit's purpose. The proposal is the deliverable.
