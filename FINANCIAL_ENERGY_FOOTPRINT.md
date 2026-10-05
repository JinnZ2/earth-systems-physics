# FINANCIAL_ENERGY_FOOTPRINT.md

CC0 -- No Rights Reserved. Companion to `financial_energy_footprint.py`.

## Task A -- current state, recorded before any change

This section was committed alone, before the module existed. File names
given in the work order were not trusted; every location below was found
by content search across this repository and the JinnZ2 repositories
reachable from the session (99 shallow clones; this repository and
thermodynamic-accountability-framework were checked current against their
remote `main` on 2026-10-05).

### Piece 2 -- financial-metabolism model: EXISTS, as code

```text
where     earth-systems-physics/dollar_energy_metabolism.py   (fd0d99a, 1294 lines)
copy      planetary-conservation-framework/dollar_energy_metabolism.py
          (66184b7, 723 lines; older and smaller; same five layers and r values,
           one description string differs; not touched here)
exports   ai_reference/catalogs/overhead_layers.jsonl   (generated, 5 records)
          ai_reference/catalogs/finance_scenarios.jsonl (generated, 4 records)
tests     test_smoke.py :: TestDollarEnergyMetabolism
form      E_total = E_base / (1 - r_effective)   (docstring line 34)
          five OverheadLayer rows: leverage, margin_stack, taxation,
          narrative, political, each with r_low / r_high
```

What the code actually computes, read from `compute_dollar_energy`:

```text
subtotal = E_base * (1 + sum_i r_i(position))        layers enter ADDITIVELY
total    = subtotal / (1 - recursive_r)              recursive_r is a per-scenario
                                                     scalar (0.0 / 0.3 / 0.5 / 0.7)
```

Five discrepancies, recorded and not repaired in that file:

```text
A-1  docstring: r_effective = "weighted recycling fraction across all overhead
     layers".  code: recursive_r is stipulated per scenario and is not derived
     from the layer r values; no weights are defined anywhere in the repo.
A-2  layer r values enter twice in different forms: once additively in the
     subtotal, and (by the docstring's reading) again inside r_effective.
A-3  no layer r value carries a source.  r_low / r_high are numbers in the
     source file with no citation, derivation, or measurement record.
A-4  margin_stack: description gives 35-70 % intermediary capture of each
     dollar; r is 0.23-1.40.  Neither capture itself (0.35-0.70) nor
     capture/(1-capture) (0.54-2.33) reproduces 0.23-1.40.  Converting a
     money capture fraction into an energy recycling fraction also needs the
     energy intensity of intermediary spending relative to project spending,
     which is not stated.
A-5  sink threshold stated two ways.  Prose: "consumes more energy processing
     the dollar than the dollar can deliver" (overhead > delivered).  Code and
     docstring threshold: r >= 1 (series divergence).  Under the geometric
     series overhead exceeds delivered at r_effective > 0.5, not at 1.
     check_negative_eroi tests the SUM of layer r against 1; the order and the
     docstring state "any layer's r >= 1".  These are three different
     conditions.
```

### Piece 1 -- energy-flow-rate referent: EXISTS ONLY IN A RICHER FORM

`M = DeltaE_net / Delta t` with `DeltaE_net = E_delivered - E_waste - E_hidden`
was searched as literal text and as its parts. It appears in no repository
in that form. The nearest source is the Money Equation:

```text
where     thermodynamic-accountability-framework/CLAUDE.md :3064 (30038f3)
          thermodynamic-accountability-framework/money_distribution/README.md :17
form      M = sum_i[ p_i * (E_delivered * F(t) - E_waste - E_hidden * L) / (T + S)
              * (1 + K_op * K_cred) * alpha_planetary * D_complexity ]
terms     glossary.md: E_delivered = useful output that reached its destination;
          E_waste = delivered output that produced no mission value;
          E_hidden = output extracted from organisms but not accounted
code      no module computes M; money_distribution/ is an interface stub
          (CONTRACT_VERSION 0.1.0)
```

The order's referent is that equation with one receiver, `F(t) = 1`, `L = 1`,
the multiplier terms dropped, and `(T + S)` read as `Delta t`. That reduction
is a choice made here, not something found in any source.

Sense collision: this repository's own `dollar_energy_metabolism.py:605`
defines `E_waste = E_ego + E_narrative + E_lobby + E_surveillance`, which
does not match the TAF glossary definition. Both are kept as found.

### Piece 3 -- dependency chain / uncategorized footprint: NOT FOUND AS CODE

Searched: colocation, settlement rail, chip fab / transaction chip, HFT,
compliance stack, security engineering, "uncategorized", "logged under",
non-finance category. No module itemizes finance-dependent energy that is
booked under other sectors. The nearest material:

```text
Simulators/fragility-cascade/THE_FRAGILITY_CASCADE.md :57
    intermediation depth L as a count of gates (auth, metering, orchestration,
    hypervisor, server, DC power, grid, chip fab, backbone); a count, no energy
Mathematic-economics/addendum-2.md :687
    "Energy Flow Analysis of HFT"; prose, no quantities
thermodynamic-accountability-framework/concerns/substrate_externality_load_map.py
    co-location as a load principle; not finance
```

### The 2 % figure

`"Banking sector: ~2% of global electricity."` occurs only as text inside
the `leverage` layer's description string (`dollar_energy_metabolism.py:87`)
and its generated catalog copy. It carries no source, it is ELECTRICITY
rather than primary energy, and no code reads it.

### Nothing else found

Searched also: r_effective, net energy sink, margin stack, energy flow rate,
financial metabolism. Found only the locations above, plus
`thermodynamic_price_guard.eroei_check`, which uses "net energy sink" for
EROEI < 1. That is a production process, not finance.

---

## The instrument (Tasks B-E)

`financial_energy_footprint.py` -- one module, stdlib only, CC0. It imports
the layer values from `dollar_energy_metabolism.py` rather than copying them,
and edits nothing in that file. The five discrepancies A-1..A-5 above are
left in place there.

```text
python financial_energy_footprint.py                 strict reading
python financial_energy_footprint.py --mode carried  carried reading
python financial_energy_footprint.py --choices       the 8 declared choices
python financial_energy_footprint.py --json
python test_financial_energy_footprint.py            23 checks (also pytest)
```

### Scope

```text
base unit        M = (E_delivered - E_waste - E_hidden) / dt       energy per time
overhead         E_total = E_base / (1 - r_effective)
r_effective      sum of r_i over metabolism layers + dependency chain   [CHOICE 1]
join             metabolism layers -> E_waste ; chain -> E_hidden    [CHOICE 3]
                 E_delivered = E_base                                [CHOICE 2]
output           bands (lo, hi) for r_effective, E_total, E_waste, E_hidden, M;
                 three sink conditions, each TRUE / FALSE / UNDETERMINED
not in scope     any default energy-per-dollar figure (the source's 5.7 MJ/$ is
                 unsourced; E_base is an input, default 1.0 = per unit delivered)
```

### Measured vs floored vs unmeasured

```text
MEASURED            nothing. No r value in any reachable repository has a
                    measurement record.
CARRIED_UNSOURCED   the five metabolism layers' r_low / r_high; the leverage
                    3-10x positions range. Summed only in --mode carried, and
                    every carried result is labelled as resting on them.
FLOOR               banking ~2 % of global electricity. Held as a Floor object;
                    as_total() raises. Excludes the dependency chain, embodied
                    energy, the leverage multiplier, non-electric energy.
UNMEASURED          every dependency-chain item (developers, security
                    engineering, settlement rails, exchanges, transaction-chip
                    fab, HFT colocation, compliance stack, embodied
                    infrastructure); energy per leverage position. Range fields
                    are None. No number was supplied.
```

An UNMEASURED term is never read as zero. It removes the upper bound on
r_effective and E_total, and it turns M into an upper bound.

### What the two readings return (E_base = 1, dt = 1)

```text
                      strict          carried (rests on unsourced values)
r_effective           0 .. UNBOUNDED  0.54 .. UNBOUNDED
E_total               1 .. UNBOUNDED  2.1739 .. UNBOUNDED
M (least overhead)    <= 1.0          <= -0.1739
any layer r >= 1      UNDETERMINED    UNDETERMINED (margin_stack 0.23-1.40 straddles)
r_effective > 0.5     UNDETERMINED    TRUE
r_effective >= 1      UNDETERMINED    UNDETERMINED
```

In the carried reading, even the low end of the carried layer values gives a
negative net flow before any dependency-chain term enters. That result is a
property of numbers with no source. It is not a measurement.

### Open gaps (in-line as `GAP G-n` in the module)

```text
G-1   every metabolism-layer r unmeasured; carried values unsourced
G-2   r_effective weighting: source says "weighted", defines no weights
G-3   margin capture (money) -> r (energy) conversion not derivable
G-4   leverage positions -> energy: energy per position unmeasured
G-5   every dependency-chain r unmeasured; logged_under carried, unverified
G-6   embodied energy of finance infrastructure unmeasured
G-7   bounds assume r_i >= 0 and E_hidden >= 0
G-8   no disjointness check between layers and chain items (double counting)
G-9   2 % figure: unsourced, electricity only, a floor
G-10  recursion split between E_waste and E_hidden assumed proportional
G-11  referent reduced from the Money Equation; dropped terms unvalued
G-12  "net energy sink" has three conditions here; none is picked
```
