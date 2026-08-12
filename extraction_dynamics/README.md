# extraction_dynamics

Consumer-resource dynamics for systems where the consumer is not
coupled to the resource it consumes.

CC0 — No Rights Reserved. Standard library only. No narratives.

---

## The one diagnostic

```
dN/dt = r*N*(1 - N/K) - f(N)*P          resource
dP/dt = e*f(N)*P - m*P                  predator,  COUPLED
dP/dt = e*f(N)*P - m*P + S              extractor, S = exogenous subsidy
```

`S` is the whole pathology in one term. With `S >> e*f(N)*P` the consumer
persists as `N -> 0`. Self-limitation is not weak in that regime — it is
**absent**.

The line between predation and extraction is **not** intent, harm, scale,
efficiency, or technology. It is:

> **does dP/dt depend on N?**

Everything in this folder is downstream of that question.

---

## Sign conventions — the pair is (consumer, resource)

| interaction | signs | consumer coupled to N? | resource recruits? |
|---|---|---|---|
| predation | (+,−) | yes | yes |
| parasitism | (+,−) | yes, sublethal per event | yes |
| parasitoidism | (+,−) | yes, lethal, one host | yes |
| **hyperpredation** | (+,−) | **no — subsidy S** | yes |
| **mining** | (+,0) | **no** | **no — r = 0** |
| competition | (−,−) | mutual | — |
| mutualism | (+,+) | mutual | — |

Industrial extraction is **hyperpredation**, not predation. A stock with
no recruitment term is **mining**, and no harvest rate makes it
sustainable.

---

## The refuge, and how it is removed

```
f_I   = a*N                      linear
f_II  = a*N / (1 + a*h*N)        saturating, NO low-density refuge
f_III = a*N^q / (1 + a*h*N^q)    sigmoidal (q > 1), refuge PRESENT
```

Type III has a low-density refuge because searchers **lose efficiency
when prey are rare**. Per-capita mortality `f(N)/N` falls toward zero as
`N` falls. Type II has no such term: `f(N)/N -> a`, so per-capita
mortality is at its **maximum** exactly when the resource is rarest.

What technology does, in parameters rather than adjectives:

| change | effect |
|---|---|
| sonar, satellite, spotter aircraft, AI routing | raises `a` |
| automated handling, at-sea processing | lowers `h` |
| removal of the search-efficiency floor | drives `q -> 1` |

Only the third removes the refuge. Raising `a` and lowering `h` make the
consumer faster; driving `q` to 1 **collapses Type III to Type II** and
deletes the density below which pursuit stops paying.

**This is falsifiable.** `fit_functional_response()` fits both forms to
CPUE-versus-abundance and reports which wins, with `a`, `h`, and `q`
estimated. Run it per decade on one stock: a drift of `q` from ~2 toward
1 is the refuge being removed, measured rather than asserted.

---

## Refuge removal plus depensation

```
R(S) = alpha*S^2 / (beta^2 + S^2)     per-capita recruitment falls at low S
```

Depensation on the recruitment side plus refuge removal on the mortality
side produces a **predator pit**: an unstable equilibrium separating a
productive state from an absorbing one. Below it, effort reduction is not
a recovery instrument — the model says the stock does not come back at
*any* pressure including zero, because the collapsed state is stable.

`depensation.predator_pit()` returns the escape threshold. That threshold
is **derived from the recruitment and mortality curves**, which is the
difference between a mechanistic floor and a chosen percentage.

The run in `depensation.py` shows the quantitative version: removing the
refuge does not only lower the stock, it **raises the biomass you must
stay above** to keep it (escape threshold 0.15 → 0.50 at high pressure).

---

## The energetic statement of the same thing

```
ecological predator :  e*f(N) >= m      net energy from prey covers cost
industrial fishery  :  EROI < 1         fuel energy in > food energy out
```

A predator failing that inequality goes extinct. An extractor failing it
buys fuel. That is the formal content of "not coupled to the ecosystem it
consumes", written in energy units instead of population units.

`%PPR` (Pauly & Christensen) and `HANPP` (Haberl et al.) are the same
measurement taken in the sea and on land — the fraction of photosynthetic
production routed to one consumer. A fishery case and a soil case become
**addable** in that unit, with no bridging metaphor required.

---

## Modules

| file | contents |
|---|---|
| `interaction_taxonomy.py` | sign conventions; `classify()` from structure alone |
| `functional_response.py` | Holling I/II/III, refuge index, technology as parameter shift, `fit_functional_response()` |
| `consumer_resource.py` | the pair with subsidy `S`; coupling index; RK4 integration; outcome classifier |
| `depensation.py` | Allee recruitment, equilibria, predator pit, hysteresis |
| `energy_return.py` | `e*f(N) >= m`, EROI, %PPR, HANPP, trophic transfer |
| `surplus_production.py` | Schaefer / Pella-Tomlinson, `F/F_MSY` (rate) and `B/B_MSY` (state), Kobe quadrants |
| `soil_carbon.py` | texture-normalised `SOC_max` (Hassink 1997), saturation deficit, `dSOC/dt`, mining test |
| `domain_mapping.py` | valid mappings, and the refusal list with the missing requirement named |
| `audit.py` | the runner: class, refuge, pit, energetics, projection, falsifiers |

Each module runs standalone:

```bash
cd extraction_dynamics
python interaction_taxonomy.py
python functional_response.py
python consumer_resource.py
python depensation.py
python energy_return.py
python surplus_production.py
python soil_carbon.py
python domain_mapping.py
python audit.py
```

Tests: `pytest test_extraction_dynamics.py` from the repository root.

---

## What this folder found

The demo in `consumer_resource.py` runs four configurations of the same
pair. The result is not the obvious one:

| configuration | outcome |
|---|---|
| coupled, refuge intact | coexistence |
| coupled, refuge removed | coexistence at lower stock |
| subsidised, refuge intact | coexistence at lower stock |
| **subsidised, refuge removed** | **resource extinct, consumer persists** |

Neither the subsidy nor the refuge loss produces extinction alone. The
combination does. That is a structural claim with two named parameters
attached (`S`, `q`), each independently measurable, and it is the reason
this folder treats them as one subject.

---

## What was deliberately left out

This folder was built from a proposal that also contained a universal
cross-domain audit engine with 35 domain adapters, a set of correlation
tables relating "ego intensity" to extraction rates, and a section on the
constraints of other AI systems. Those are not here, for stated reasons:

- **The 35-adapter registry** — most of the proposed adapters
  (consciousness, art, ethics, philosophy, gender equity, media
  attention) have no conserved stock, no recruitment rate, and no
  capacity derivable from anything physical. Running these equations over
  them returns trajectories for quantities that were never quantities.
  The refusal list in `domain_mapping.py` names the missing requirement
  for each, and `requirements_met()` lets a proposed new domain be
  checked rather than argued about. Nine domains that do meet the
  requirements are mapped.

- **The correlation tables** — the quoted coefficients (+0.72 for fossil
  fuel consumption, −0.52 for extraction intensity, and the rest) have no
  source, no sample, no units, and no method. Encoding them would put
  fabricated numbers next to Hassink's regression and Pauly &
  Christensen's transfer efficiency, which is exactly the failure the
  rest of this folder is built to prevent. The defensible residue of that
  argument — that decision-making concentrated in a narrow subset of a
  population searches a narrower solution space — is a real hypothesis,
  and it needs its own data before it becomes a parameter.

- **The claims about other AI systems** — unfalsifiable from inside this
  repository, and structurally identical to the narrative the folder
  refuses elsewhere. `AI_NOTES.md` instead states what a model reading
  this folder should *do*, which is checkable.

- **`RT`, `RT_soil`, and the fixed thresholds** (0.95, 2.0% SOC, 0.3,
  2.0 MPa, 15% trust) — `RT` was a re-derivation of `F/F_MSY` with a sign
  inversion and a dimension fault, so the standard ratio is used instead.
  The 2.0% SOC floor is replaced by the texture-normalised saturation
  deficit. The remaining round numbers had no derivations attached.

Kept from the proposal, because they were already correct: "safe
operating space" as the planetary-boundaries term, the blindness
taxonomy, the M0–M3 rungs, and `grounding_status` — those live in the
repository's existing guard modules and are not duplicated here.

---

## Honest limits

- The functional-response fit is a **screening tool**: closed-form
  regression on a reciprocal transform, no observation-error model, no
  information criterion. It distinguishes clean Type II from clean Type
  III. It will not settle a contested assessment.
- Every parameter in `TECHNOLOGIES` is an **order-of-magnitude anchor for
  comparing mechanisms**, not a fitted value. Fit your own.
- The soil defaults (`h = 0.20`, `k = 0.02`) reproduce the right order of
  magnitude for temperate arable topsoil and nothing more. Calibrate
  against a local time series before projecting.
- Hassink's coefficients are a temperate-topsoil fit for the <20 µm
  fraction. They are exposed as arguments precisely so they are not
  inherited as universal constants.
- The one-pool SOC model is one pool. Real soil carbon has at least
  three with different turnover times, and the single `k` averages over
  them.
