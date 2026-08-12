# cpr_composition

A common-pool resource experiment: does group composition change whether a
shared stock survives, once governance is held constant?

CC0 — No Rights Reserved. Core is standard library only. **Draft design, not
registered, no data collected, no ethics approval.**

---

## Why this is here

`extraction_dynamics/` says the diagnostic for extraction is whether `dP/dt`
depends on `N` — whether the consumer's persistence is coupled to the resource.
It also refuses to model "dominance orientation" as a parameter, because the
correlations offered for it had no source, sample, or units.

This folder is the other half of that refusal. If the claim is that composition
of decision-makers changes extraction outcomes, then the way to find out is to
run it, with the effect size declared in advance and a way to come back
negative. The experiment is the answer to the objection, not a workaround for it.

The game is itself a subsidised consumer-resource system: participants earn a
show-up fee whatever happens to the stock. `cpr_game.subsidy_ratio` puts the
coupling index at 0.57 — 43% of maximum earnings are independent of the
resource. The instrument models hyperpredation by construction.

---

## Files

| file | contents |
|---|---|
| `PREREGISTRATION.md` | the design, with the five corrections the simulation forced |
| `cpr_game.py` | engine: logistic regeneration, largest-remainder rationing, exact sustainable harvest, policies, Gini, coupling index |
| `parameter_sweep.py` | pilot instrument: design window, mechanical composition baseline, individual-level dilemma check |
| `design.py` | screening-pool arithmetic, power, composite coherence, seeded block randomisation |
| `analysis_plan.py` | stdlib OLS, standardised equivalence test, threshold specification, guarded optional survival/mixed models |
| `otree_app/__init__.py` | oTree 5 implementation with the page ordering corrected |

```bash
cd experiments/cpr_composition
python cpr_game.py
python parameter_sweep.py
python design.py
python analysis_plan.py
```

Tests: `pytest test_cpr_experiment.py` from the repository root.

---

## What the simulation found before any human was recruited

**1. The comparison arm was the same as the treatment arm.** The draft's
"sustainable" policy was `S/N` — split the standing stock evenly. It fails in
two ways depending on where the cap binds: below S = N·cap it requests the
whole stock and collapses it in one round; above S = N·cap the cap truncates
every request to the cap, so at S = 50 it asks for 12 each, is truncated to 8,
and *is* all-max. Neither branch is restraint. The exact sustainable harvest is
a fixed point of the regeneration map, not a share of the stock:

| stock | exact sustainable total | per player | naive S/N |
|---|---|---|---|
| 20 | 5.08 | 1.27 | 5.00 |
| 50 | 9.63 | 2.41 | 12.50 |
| 90 | 5.14 | 1.28 | 22.50 |

**2. The mechanical baseline is the pre-registered effect size.** Running the
game with `k` pure maximisers and `4−k` optimal restrainers — no personality
anywhere in it — gives a composition slope of −0.19 to −0.24 depending on `g`.
H2's SESOI was −0.20. Tested against a null of zero, arithmetic alone returns
"H2 strongly supported."

The dry run in `analysis_plan.py` shows both verdicts on the same simulated
data:

```
vs zero (the WRONG null)    -> LARGER_NEGATIVE   H2 supported
vs mechanical baseline      -> EQUIVALENT        indistinguishable from arithmetic
```

**3. The baseline is a step, not a slope.** At g = 0.4 the stock survives with
0 or 1 maximisers and collapses at 2 or more. A linear model fitted to that
returns an average describing no group in the sample. Both specifications are
now registered, with the threshold one flagged as selection-dependent.

**4. The sample-size arithmetic did not close.** 720 participants and 240
groups of 4 cannot both be true. 240 groups needs 960 participants and a
screening pool of 1440 — the pool set by high-D supply, because balancing
compositions 0–4 requires half the sample from a third of the population.
80% power at β = 0.20 needs 203 groups, so 240 is the right number and the
draft's 180 was not.

**5. Group totals and individual incentives point opposite ways.** Over 20
rounds, restraint yields the group about three times the tokens of
maximisation — but a lone defector among restrainers earns 160 tokens against
40 under universal restraint. Only the second comparison is the dilemma. If it
were absent the study would measure comprehension, not dominance.

---

## Bugs fixed from the draft code

| where | bug | consequence if unfixed |
|---|---|---|
| oTree page sequence | extraction resolved on a wait page **before** the decision page | every round computed on unset requests |
| oTree comprehension page | `form_fields = ['request']` as a placeholder | collides with the decision field |
| randomiser | `np.random.shuffle` unseeded while the draw was seeded | assignment not reproducible, not auditable |
| randomiser | modulo fallback re-drew from the pool; the duplicate assertion only checked *within* a group | one participant in two groups, undetected |
| randomiser | `groups_per_arm // 5` silently produced fewer groups when not divisible | design quietly unbalanced |
| equivalence test | unstandardised coefficient compared to a standardised SESOI | equivalence declared for effects ~4× the SESOI |
| rationing | `int()` truncation destroyed tokens the stock could have supplied | payoff data does not close |
| survival analysis | no censoring indicator described | survivors treated as collapsing at T |
| round-level model | no round term | within-session trend attributed to composition |

The unit error in the equivalence test recurred once more while this folder was
being written — the mechanical baseline is in raw units and the primary
coefficient is standardised, and the first version of the demo compared them
directly. `analysis_plan.standardized_baseline` exists because of that, and the
docstring says so.

---

## Honest limits

- **Not registered, no ethics approval, no data.** This is a design and a
  simulator.
- The power calculation is a normal approximation, adequate for design
  arithmetic and not a simulation-based power analysis of the actual estimator.
  The preregistration says to run one before registering.
- `high-D` is a label for the top tercile of a three-item composite in one
  sample. Whether those three items cohere at all is a pre-registered check
  with a pre-registered fallback, not an assumption.
- oTree is not installed in this repository and is not a dependency. The app is
  version-controlled documentation of the instrument; the test suite
  syntax-checks it and verifies its rationing arithmetic matches `cpr_game.py`,
  which is the reference implementation.
- A 20-round game with four participants and a show-up fee is not a
  civilisation, and no result from it should be described as though it were.
