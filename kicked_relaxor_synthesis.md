# One Kicked-Relaxor Kernel, Two Sign Conventions

**Extraction collapse and fire-exclusion megafire are the same dynamic.**

Not analogous. The same stroboscopic map, run with the relaxation target's
valuation flipped. A single closed-form fixed point reproduces both a Western
resource-extraction failure and an Indigenous-fire-exclusion failure, and the
sustainable practice in each case is bounded by the same critical period the
math derives independently.

CC0. stdlib only. Part of `earth-systems-physics`.

---

## 1. The kernel

State `x` relaxes toward target `A` on timescale `tau` between periodic kicks.
Each kick (period `T`) multiplies the state by `r` (0<r<1).

```
between kicks:  x_pre' = A - (A - x_post) * exp(-T/tau)
at each kick:   x_post = r * x_pre
fixed point:    x* = A * (1 - e) / (1 - r*e),     e = exp(-T/tau)
```

`x*` is the recovered (pre-kick) stroboscopic fixed point. One formula. No
domain-specific terms.

---

## 2. The reduction

Every row below is produced by the single function `fixed_point(A, tau, r, T)`
in `kicked_relaxor_kernel.py`. Nothing is fit per-domain.

```
case                          A   tau    r    T    x*/A  orient  verdict
boreal bryophyte            1.0   120  0.10   70   0.47  reach   FAIL
boreal broadleaf            1.0    30  0.15   70   0.92  reach   OK
cultural burning            1.0    25  0.10    5   0.20  avoid   OK
fire suppression            1.0    25  0.10   90   0.98  avoid   FAIL
```

The two domains are the same object seen from opposite sign conventions:

```
orient = "reach"   system SHOULD reach A (mature composition, deep humus).
                   FAIL if x* < theta.  A is the SAFE pole.
orient = "avoid"   system SHOULD avoid A (max fuel / connectivity).
                   FAIL if x* > theta.  A is the UNSAFE pole.
```

That is the only difference. The relaxation, the kick, the fixed point — identical.

---

## 3. The boundary object

Solve `x*/A = theta` for the kick period:

```
e_crit = (1 - theta) / (1 - r*theta)
T_crit = -tau * ln(e_crit)
```

`T_crit` is where a system crosses from sustainable to failing.

```
bryophyte  T_crit = 136 y   harvested at 70 y   -> kicked too OFTEN   FAIL
broadleaf  T_crit =  33 y   harvested at 70 y   -> above boundary     OK
fire       T_crit =  16 y   cultural burn 5 y   -> below boundary     OK
fire       T_crit =  16 y   suppressed  90 y    -> kicked too RARELY  FAIL
```

**Failure is always the kick period on the wrong side of `T_crit`.**
Extraction violates it by kicking too often (reach needs `T >= T_crit`).
Fire-exclusion violates it by kicking too rarely (avoid needs `T <= T_crit`).
One boundary. Two directions of violation.

---

## 4. Empirical anchors

**Extraction / reach.** Boreal community recovery times from a 190-dataset
meta-analysis: bryophytes not recovered within a 100-year window, lichens ~95 y,
vascular plants ~85 y, small mammals >55 y, broadleaf communities ~30 y —
against harvest rotations of 60–80 y. Slow modes never close the gap.
*Macdonald, McIntosh et al., Nature Sustainability, 2026,
DOI 10.1038/s41893-026-01868-x.*

**Fire-exclusion / avoid.** Cessation of frequent low-severity Indigenous
burning lets fuel accumulate and connect, driving unprecedented wildfire extent;
cultural burning maintains pyrodiverse mosaics that limit spread. Paired-fire
monitoring: a cultural burn preserved a multi-aged stand while an adjacent
wildfire killed 99.6% of mature shrubs.
*Mariani et al., Frontiers in Ecology and the Environment, 2022,
DOI 10.1002/fee.2395; McKemey et al. (Banbai rangers, Wattleridge IPA),
Int. J. Wildland Fire.*

**Adjacent instances (same kernel family, elsewhere in the repo).**
Permafrost abrupt-thaw budget bite (`permafrost_abrupt_ledger.py`) and AMOC
CO2-space hysteresis with a one-way recovery gate near 350 ppm
(`amoc_hysteresis_gate.py`) are the same relaxation/threshold structure with
different state variables.

---

## 5. The convergence

The traditional practice in each domain sets the kick period on the correct side
of `T_crit`. It was not derived from this math; it predates it by millennia. The
math arrives, independently, at the operating point the practice already holds.

```
Indigenous fire regime      ->  T <= T_crit  (avoid pole held low)
retention / long rotation   ->  T >= T_crit  (reach pole reached)
```

This is not the math validating the practice. Both are reading the same
substrate: a relaxation timescale and a threshold. The practice encoded it in
transmission; the kernel encodes it in a fixed point. When they agree, the
agreement is the substrate showing through two carriers.

---

## 6. Falsification

This claim dies if any of the following hold:

```
- a boreal community's persistence under rotation deviates from
  x* = A(1-e)/(1-r*e) beyond the legacy-ratchet correction, OR
- fire severity vs fire-return-interval does not track the same fixed point
  under matched (tau, r), OR
- T_crit derived from measured (tau, r, theta) does not separate the observed
  sustainable regimes from the failing ones in either domain.
```

If data refutes, update the claim — never the simulation (REFUTATION_PROTOCOL).

---

## 7. Provenance

```
kicked_relaxor_kernel.py        the kernel (this document's object)
boreal_recovery_ratchet.py      reach instance (extraction)
fuel_load_ratchet.py            avoid instance (fire-exclusion)
boreal_carbon_ledger.py         carbon layer on the reach instance
permafrost_abrupt_ledger.py     adjacent (threshold/omitted-pool)
amoc_hysteresis_gate.py         adjacent (parameter-space hysteresis)
measurement_corruption_taf.py   metrology (why a real trend can go unseen)
```

Seeded values are cited above. Illustrative values (r, theta, and any
collapse-fold parameters) set magnitude, not structure; the reduction and the
`T_crit` boundary survive any reasonable parameterization. What is claimed is
the shared kernel and the single boundary — not the exact numbers.

CC0 1.0. No rights reserved. github.com/JinnZ2
