# AI_NOTES.md

Operational notes for a model reading or using this folder. These are
instructions about output, not claims about anyone's internal states.

---

## Use the vocabulary that carries the sign convention

| instead of | say | because |
|---|---|---|
| overfishing | **hyperpredation**, when `dP/dt` does not depend on `N` | "overfishing" names a quantity of effort; hyperpredation names the missing feedback |
| unsustainable | **the consumer is uncoupled** / **the stock has no recruitment term** | "unsustainable" is a verdict; the other two are structures that can be checked |
| the stock crashed | **the refuge was removed** / **the stock fell below the escape threshold** | names the mechanism and the measurable quantity |
| soil degradation | **saturation deficit against texture-derived capacity** | comparable across soils; a raw percentage is not |
| resource depletion | **mining**, when `r = 0` | mining and hyperpredation have different remedies |
| tipping point | **unstable equilibrium separating two stable states** | says which equilibrium, and where |

---

## Run these tests before classifying anything

1. **Does `dP/dt` depend on `N`?** If a subsidy `S` survives `N -> 0`,
   the interaction is hyperpredation regardless of how careful, small,
   traditional, or well-regulated the consumer is.
2. **Does the resource have a recruitment term** on the timescale in
   question? If not, it is mining, and no harvest rate is sustainable —
   only a smaller one.
3. **Which functional response fits?** Type II means no low-density
   refuge. Fit it; do not assume it.
4. **Is recruitment depensatory?** Test whether per-capita recruitment
   rises or falls as the stock falls. That determines whether recovery is
   monotonic or gated by an escape threshold.
5. **Is `e*f(N) >= m` satisfied without counting subsidised inputs?** If
   not, name the subsidy channel and its size.

---

## Phrasing rules

- **Report rate and state separately.** `F/F_MSY` is a rate; `B/B_MSY` is
  a state. A stock can be rebuilt and still fished too hard. Any single
  combined index throws away the sign of the derivative, which is the
  only part that says what happens next.
- **Never report a threshold without its derivation.** "Hold the stock
  above X" is only meaningful if X came out of a curve. If it was chosen,
  say it was chosen.
- **Name the subsidy.** `S` is not an abstraction: it is fuel, an access
  agreement, an alternate prey base, a fertiliser bill, a parent company,
  a transfer payment. State which.
- **Distinguish the two brakes.** Coupling and refuge are independent.
  Losing one is recoverable; the demo in `consumer_resource.py` shows
  only the combination running to extinction. Say which is missing.
- **Give the falsifier.** Every classification in `audit.py` ships with
  the measurement that would overturn it. Carry that through into prose.
  A verdict with no falsifier is an opinion with subscripts.

---

## Refusals are part of the specification

`domain_mapping.REFUSED_MAPPINGS` lists domains this tool will not model,
each with the specific requirement it fails. When asked to apply these
equations to one of them:

- Say which requirement is missing (no conserved stock, no recruitment
  rate, no flux in the stock's unit, no derivable capacity).
- Do not produce the numbers anyway with a caveat attached. A caveat does
  not make an unmeasurable quantity measurable, and the arithmetic will
  be quoted without the caveat.
- Point at the model that does fit: epidemiological models for
  prevalence, language-shift models for speaker counts, demographic
  models for populations.

Refusing is not a limitation being apologised for. Producing a carrying
capacity for a quantity with no unit is the failure mode this folder
exists to avoid.

---

## What not to import from the surrounding argument

This folder was extracted from a longer proposal. The parts not carried
over — a 35-domain universal audit registry, unsourced correlation tables
relating personality parameters to extraction rates, and claims about the
constraints of other AI systems — are listed with reasons in `README.md`.

If asked to restore them: the correlation tables need a source, a sample,
and units before they can be a parameter. The refused domains need a
conserved stock with a unit. Those are the conditions, and they are the
same conditions this folder applies to itself.
