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
