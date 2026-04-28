# Audit findings — biocarbon_stack

First-pass audit of the framework's quantitative claims, run on the
post-paste-repair tree (2026-04-28). Records what was checked, what
held, and what's worth tracking forward. This is structural and
internal-consistency auditing, not domain-physics validation.

## Scope

What this audit covered:

- per-component contribution breakdown of the headline Monte Carlo
- unit cascade through every component's calculation chain
- reproducibility under explicit random seed
- cross-check of cited constants against published sources
- structural auditability via the repo's `input_validation_guard`

What this audit did NOT cover (real gaps, not throat-clearing):

- physics correctness against peer-reviewed peat / kelp / ERW models
- coupled-system effects (the MC adds components as independent)
- sensitivity analysis (one-at-a-time perturbation across parameter ranges)
- the local-steward audit that `backwards_building.py` says is the
  only audit that actually matters; framework explicitly notes this
  cannot be done remotely

## Findings

### 1. "Other wetland" carries 43% of the headline median

Per-component breakdown (Monte Carlo, seed=42, n=3000):

| Component | p05 | median | p95 | share of median |
|---|---:|---:|---:|---:|
| peat | 0.24 | 0.34 | 0.45 | 9% |
| **other wetland** | **1.20** | **1.71** | **2.24** | **43%** |
| kelp | 0.07 | 0.26 | 0.68 | 7% |
| permafrost | 0.53 | 0.85 | 1.16 | 21% |
| adaptive | 0.11 | 0.41 | 0.71 | 10% |
| erw | 0.14 | 0.35 | 0.75 | 9% |
| **total** | 3.11 | 3.99 | 4.95 | 100% |

Driver: `run_full_stack.monte_carlo` applies the peat-style
`carbon_storage_rate` (with W=0.85, R_p=0.5 — modestly reduced from
peat's 0.95 / 0.6) to ~3M km² of non-peat drained wetland.
`carbon_storage_rate` treats anoxic NPP as essentially permanently
stored (`1 − k_decomp_anaerobic = 0.998`). For non-peat wetlands that
assumption is almost certainly too high. The single largest
sensitivity in the headline number lives here.

### 2. `permafrost_net_benefit` is functionally a passthrough

The function takes `warming_avoided_GtC` (sampled 0.5–1.2 in the MC),
multiplies by 44/12 internally, and the caller in `run_full_stack`
multiplies back by 12/44. The only physics in the function is the
enteric-CH4 subtraction, and at the default species mix that cost is
about 250× smaller than the avoided benefit. The 21% headline
permafrost contribution is therefore essentially the assumed input
range, not a derived result.

### 3. ERW acceleration factor is handled twice

`run_full_stack.py` divides `co2_per_t_basalt` by 3.0 before passing
it in; `geological_vector.erw_drawdown` then multiplies by
`acceleration_factor=3.0` inside the function. The two cancel
exactly today, but any future change to either side that doesn't
update the other will silently mis-calibrate. The function's
docstring mentions this convention; the convention is fragile.

Suggested fix: pick one site for the acceleration factor (either the
caller or the function), document it, and remove the other.

### 4. `adaptive_layer_net_carbon` returns a field the MC ignores

The function returns four fields (`pretreatment_one_time_t_CO2`,
`annual_drawdown_t_CO2`, `cumulative_after_yr`, `payback_period_yr`).
`run_full_stack.monte_carlo` uses only `annual_drawdown_t_CO2`.

The pretreatment cost is *negative* at default parameters (biochar's
−2.0 t CO2/ha outweighs lime's +1.1 and compost's +0.2), so the MC
under-counts rather than over-counts. Still a quiet bug: the
function's full output isn't propagated.

### 5. Wetland peat accumulation rate is high-end

At nominal inputs (W=0.95, R_p=0.6), `carbon_storage_rate` returns
0.69 kg C/m²/yr. Peer-reviewed steady-state peat accumulation
typically falls in 0.05–0.5 kg C/m²/yr. The framework's rate is
defensible for the first 10–20 yr of a restored bog (where fresh
sphagnum hasn't decomposed yet) but optimistic at long-term steady
state. The MC applies the high rate at full restoration scale
without time-decay.

### 6. ERW permanence claim depends on stable ocean chemistry

`geological_vector.ERW_LIMITS` flags this honestly: "100,000 year
permanence claim depends on stable ocean chemistry; uncertain under
warming." Worth restating as an audit finding because ERW is the
only Phase-1 component whose permanence is literally geological —
and that geology runs through the most-perturbed buffer in the
system (ocean carbonate chemistry).

## What held under audit

- **Headline constants vs published sources** — 6/6 anchor values
  match:

  | claim in code | source | status |
  |---|---|---|
  | wetlands historical 12.1M km² | Davidson 2014 / Mitsch & Gosselink | ✓ |
  | peatland extent 4.0M km² | Yu 2010, Xu 2018 | ✓ |
  | kelp NPP 0.5–3 kg C/m²/yr | Mann 1973 et seq. | ✓ |
  | kelp deep-export 0.04–0.20 | Krause-Jensen & Duarte 2016 (cited) | ✓ exact |
  | anthropogenic CO2 10 GtC/yr | GCB 2024 | ✓ |
  | atmospheric growth 5.3 GtC/yr | GCB 2023 | ✓ |

- **Unit cascade** — kg ↔ Gt conversions, C ↔ CO2 stoichiometry
  (12/44 and 44/16), and area ↔ m² conversions check out through
  every component.

- **Reproducibility** — `random.seed(42)` produces deterministic MC
  output across runs.

- **Run-to-run noise** — at n=500 the median's standard deviation
  across unseeded runs is ~0.025 GtC/yr (≈0.6%); narrower at n=3000.

- **Structural auditability** — all 7 headline claims (six components
  + total) grade STRONG against the repo's `input_validation_guard`
  (specify quantity, unit, instrument, conservation law, boundary,
  and falsifiability). The guard checks claim *shape*, not *truth*.

## Independence assumption

The Monte Carlo sums the six components arithmetically as if they
were independent. The framework's own `docs/ARCHITECTURE.md` lists
explicit cross-component couplings: wetland N retention enables
stable kelp; ERW raises soil pH which feeds the adaptive layer;
adaptive-layer porosity affects wetland CH4 spike; herbivore
restoration affects regional albedo which couples to atmospheric
trajectory. None of these couplings appear in the MC sum. They
likely produce both positive and negative interaction terms; net
sign is not analytically obvious. Worth a follow-up: a coupled MC
that propagates at least the largest documented couplings.

## Composite verdict

The headline number (4.0 GtC/yr median, 3.1–4.9 90% CI) is
internally consistent: units cascade, constants match published
anchors, code is reproducible, claims are structurally auditable.

The number is sensitive to two parameter choices that deserve
domain-expert review:

1. The non-peat wetland storage rate (43% of total).
2. The assumed `warming_avoided_GtC` input to permafrost (21% of
   total).

Together these are 64% of the headline. The other four components
(peat, kelp, adaptive, ERW) are each ≤10% and rest on better-anchored
parameter ranges.

The framework explicitly holds itself out as a "constraint-equation
skeleton" and "draft" with parameter ranges rather than point
estimates. The audit findings are consistent with that self-framing
— the framework's claims about its own status are honest. The
findings are not "the framework is wrong"; they are "here is where
the leverage actually sits, so future calibration effort knows
where to point."
