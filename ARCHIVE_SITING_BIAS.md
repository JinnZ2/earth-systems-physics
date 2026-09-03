# MARKER: archive siting bias

CC0. No rights reserved.
Repo: earth-systems-physics
Status: MARKER — a place marker for a sensed shape that needs more
exploration. Not a thesis. Not a position under defense.
Correct reader response: test whether it fits, extend it into an
uncovered domain, or report where it breaks. A break is a measurement
and goes in the claim table.

Computable half: [`archive_siting_bias.py`](archive_siting_bias.py).
Tests: `TestArchiveSitingBias` in `test_smoke.py` (33 tests).

---

## SHAPE

An archive sits where preservation happens.
A signal originates where the source is.
Those two locations are set by different physics.

Where they anti-correlate, every reconstruction built from the archive
carries a bias whose SIGN is known before any data is collected.

```
archive_location  = f(preservation conditions)
source_location   = g(process physics)
bias_sign         = sign( correlation( f, g ) )   ← knowable a priori
bias_magnitude    = h( transport operator, distance )
correctability    = class( transport operator )
```

Ice exists where cold is. Cold is far from tropical sources.
Corals exist where reefs grow. Tree rings need a limiting season.
Sediment preserves in anoxic basins, not productive oxic ones.
Fossils need rapid burial. Documents need dry storage.

The environment that PRESERVES is not the environment that HOSTS.

```
ENERGY-FLOW READ
  source box ──transport operator──▶ archive box ──inversion──▶ estimate
              (loss λ, exchange k)                (assumes mixing)

  The operator attenuates the signal in transit. If the inversion does
  not model the attenuation, it reports A = estimate/truth < 1. The
  attenuation is set by λ/k: a shorter-lived species loses more of its
  signal before it reaches the archive, so the bias grows as lifetime
  shrinks. The bottleneck is the operator; the leverage point is the
  ONE at-source measurement that pins the box the inversion was guessing.
```

---

## CALIBRATION POINT 1 — CH4, physical transport

Source: Lamantia et al., Nature (2026), doi 10.1038/s41586-026-10938-1
Nevado Huascarán Summit Core A, -9.122°S -77.605°W, 6768 m asl
2,000 yr record, n=51 CH4, n=5 d13C-CH4, no replicates
Data + box-model code: doi 10.5281/zenodo.18657346

Four-box atmospheric model, average source strength 0-1800 CE, Tg/yr:

| box | polar-only | +SCA | delta |
|---|---|---|---|
| NH 30-90N | ~36 | — | — |
| TN 0-30N | ~82 | 88 | +6 (+7%) |
| TS 0-30S | ~81 | ~125 | +44 (+54%) |
| SH 30-90S | 10 | 10 | fixed |
| **tropics TN+TS** | **163** | **213** | **+50 (+24%)** |

The measured box moved +54%. The still-interpolated box moved +7%.
Error localized to the unmeasured cell (88% of the total delta;
`ch4_error_localization()`).

Concentration offsets, pre-industrial, SCA above:

| against | ppb |
|---|---|
| GISP2 (Greenland) | +46 |
| NEEM (Greenland) | +48 |
| Law Dome (Antarctica) | +78 |
| WAIS (Antarctica) | +94 |

Interpolated pole-to-pole gradient (IPD, GISP2 minus WAIS):
44 +/- 7 ppb (800-1750 CE); 48 ppb (PI 0-1850).

**The offset the two-endpoint system could not see (94 ppb) is roughly
twice the entire gradient it was built to resolve (48 ppb)**
(`offset_vs_gradient_ratio()` → 1.96).

Error budget comparison:

| source | magnitude |
|---|---|
| missing equatorial box | +50 Tg/yr (+24%) |
| +/-30% perturbation, CH4 lifetime | smaller than above |
| +/-30% perturbation, transport exchange | max +/-17.5 Tg/yr |
| interpolated TN swapped for real data | max +/-3 Tg/yr |
| Monte Carlo obs noise, TS box | +/-2.59% |

Siting bias exceeded the full quantified parameter uncertainty
(`siting_bias_vs_envelope()`: 50 vs 17.5 Tg/yr).

Archive validation: SCA vs Mauna Loa 1985-2012 overlap +/-4 ppb;
measurement SD +/-3.7 ppb; PC1 covariance with GISP2+WAIS 91%;
no dust/Ca2+ correlation; no visible melt layers.

CONFOUND, unresolved in the published data: in the polar-only run TS
is SOLVED by the model; in the SCA run TS is PRESCRIBED by observation.
Part of the +54% is a change in what the box IS, not only in what it
says. Partial defence: swapping the TN box between interpolated and
real (East Rongbuk) data changed results by at most 3 Tg/yr, so
structure is not the driver. Not separable from the published data.
The separation procedure lives in `soft_prior_sweep()` and needs the
Zenodo model re-run (HANDOFF item 1).

---

## FOUR-BOX SYNTHETIC — mechanism, not the published inversion

`archive_siting_bias.py` carries an independent four-box steady-state
model (`FourBoxModel`), NOT the Zenodo code, which was unreachable from
the drafting session. It exists to show the mechanism on a
self-consistent truth: take the +SCA source column as truth, forward-
model concentrations, then invert with only the two polar boxes and
read back A. Any A < 1 there is the operator plus the interpolation,
nothing else.

```
tau=9.1 yr, exchange=0.5 yr, +SCA truth
  A_TS = 0.53   A_tropics = 0.60   A_global = 0.98
```

Two error channels, separated by the model:

- **Attribution error** — interpolation moves source between boxes.
  Per-box A saturates at a geometric floor (~0.46 here) that does NOT
  vanish as lifetime → ∞.
- **Total error** — only loss in the unseen boxes changes the global
  budget, and that scales with 1/lifetime. `A_global` → 1 for long-
  lived species, < 1 for CH4, far below 1 for CO.

The soft-prior sweep exposes a second artifact: prescribing ONE
tropical box while interpolating the other is itself a bias, of the
opposite sign. With TN still interpolated, A_TS overshoots to 1.28 at
full weight; with both prescribed it lands on 1.00.

---

## CALIBRATION POINT 2 — ENSO, statistical transport

Centre of action: eastern + central equatorial Pacific.
At-source archive: coral. Records average ~50 yr, longest under 200 yr,
temporally and spatially sporadic. This is WHY teleconnection
reconstructions exist.
Remote archive: tree ring, sediment, ice, coral from teleconnected
regions. Long, numerous, and dependent on a stationarity assumption.

Findings that make this the CONTRASTING case, not a second instance:

- All reconstruction methods lose ENSO variance in pseudoproxy tests.
  Amplitude under-read, same direction as CH4.
- BUT at low frequency the bias may INVERT. Multiproxy reconstructions
  routinely find greater low-frequency variance than models predict;
  a live hypothesis is that method bias OVERSTATES low-frequency
  importance. Sources named: too few records, chronological
  uncertainty, per-record noise, geographic distribution of network.
- Teleconnections are documented as NON-STATIONARY. The transport
  operator's parameters drift.
- Caution flagged for networks from a single teleconnected region or
  using under ~20 proxies.

---

## THE AXIS

```
ATTENUATION FACTOR
A = (source estimate from remote archive)
    / (source estimate from at-source archive)

CH4, TS box                 81 / 125  = 0.65
CH4, combined tropics      163 / 213  = 0.77
ENSO, ENSO band            < 1, recoverable from published
                             pseudoproxy variance-loss figures
ENSO, low frequency        possibly > 1 — OPPOSITE SIGN
```

```
OPERATOR CLASS SETS CORRECTABILITY  (classify_operator())

PHYSICAL + STATIONARY
  fixed parameters (lifetime, exchange rate)
  A is a CONSTANT
  bias correctable a priori, without going to the source
  CH4: sign and rough size derivable before drilling

STATISTICAL + NON-STATIONARY
  parameters drift with era
  A is a RANDOM VARIABLE with its own variance
  bias BOUNDABLE only, never corrected
  ENSO: teleconnection strength is itself a variable
```

The stationarity criterion is measurable, not a judgement call:
`stationarity_index` = max |p − mean| / |mean| across eras, compared
to the model's own perturbation envelope (default 0.30, the +/-30%
the CH4 box model already carried). Drift inside the envelope is
already paid for; drift outside it is a new variable.

Corollary, cross-domain: any event → record chain whose transport is a
ROUTING RULE rather than a physical process falls in the second class.
Routing rules drift with institutional practice. Bound, do not correct.
This is where the axis reaches the gap-quantification-protocol repo:
a classification exclusion, a reporting exemption, or a charter
boundary is a routing rule on the event→record map, so its bias is
boundable but not a priori correctable.

---

## CLAIM_TABLE

Mirror of `CLAIM_TABLE` in `archive_siting_bias.py`.

| id | claim | refuted by | status |
|---|---|---|---|
| ASB-01 | Archive location for preserved-medium proxies is set by preservation conditions, not source location | a proxy class whose preservation conditions are independent of climate/chemistry | MARKER |
| ASB-02 | Where the two anti-correlate, remote reconstruction under-reads source strength; sign known a priori | a case with anti-correlated siting where the remote reconstruction OVER-read the source, physical operator | SUPPORTED (CH4, n=1) |
| ASB-03 | A < 1 for physical-transport operators | measured A >= 1 in a physical-transport case | SUPPORTED (CH4; four-box synthetic) |
| ASB-04 | CH4 A = 0.65 (TS box), 0.77 (combined tropics) | reanalysis of the Zenodo box model returning different ratios | MEASURED |
| ASB-05 | Siting bias can exceed the full quantified parameter uncertainty of the model carrying it | a case where the missing-box term is inside the parameter envelope | SUPPORTED (50 vs 17.5 Tg/yr) |
| ASB-06 | Bias magnitude scales inversely with species atmospheric lifetime | a long-lived species showing larger A-deviation than a short-lived one, same geometry | PREDICTED (total budget; attribution error has no lifetime floor) |
| ASB-07 | Correctability is set by operator class: physical+stationary correctable, statistical+non-stationary boundable only | an a priori correction that verifies against an at-source record for a non-stationary operator | MARKER |
| ASB-08 | For statistical operators the bias sign is frequency dependent | ENSO variance loss found uniform across all frequency bands | MARKER (ENSO literature, sign only) |
| ASB-09 | The axis extends to non-geophysical archives whose event->record transport is a routing rule | a routing-rule archive whose bias proves correctable a priori | MARKER |

REFUTATION PROTOCOL: update the claim. Never retune to save it.

Note on ASB-06: the four-box model splits the claim. The GLOBAL budget
error scales with 1/lifetime as written (CO < CH4 < N2O < CO2 → 1). The
per-box ATTRIBUTION error saturates at a geometric floor set by
interpolation and does NOT vanish for long-lived species. The claim
holds for the total, not for the attribution.

---

## TESTS

**T-1 lifetime scaling (closes ASB-06)** — `lifetime_scaling()`
Rank atmospheric species by tropospheric lifetime. For each with both a
polar-only reconstruction and an at-source measurement, compute A.
Predict monotone: shorter lifetime → larger deviation from 1.
CO2 ~0, N2O small, CH4 measured at 0.65-0.77, CO large and currently
unconstrained by any polar record.

**T-2 ENSO A by frequency band (closes ASB-08)** — `enso_band_attenuation()`
Recompute A from published pseudoproxy variance-loss results, split
ENSO band vs low frequency. Predict A<1 in band, A>=1 at low frequency.

**T-3 a priori bound coverage (closes ASB-07)** — `a_priori_bound()` + `bound_coverage()`
For each quantity: compute predicted A from operator parameters BEFORE
consulting the at-source record. Check whether the later measurement
falls inside the bound. Physical cases should hit. Statistical cases
should miss at least one band.

**T-4 network geometry (closes ASB-01, ASB-02)** — `network_geometry()`
For each reconstructed quantity, correlate proxy-network spatial
density against the source-strength map of the process. Negative
correlation predicts the bias sign directly, no at-source record
needed.

---

## SIBLING ARCHIVES — untested, same predicted shape

`SIBLING_ARCHIVES` in the module.

| archive | preservation condition | under-sampled host |
|---|---|---|
| ice cores | cold, dry, high accumulation | low latitude, low altitude |
| corals | reef-forming water | outside reef range |
| tree rings | seasonally limiting growth | wet tropics |
| speleothems | carbonate terrain | non-carbonate |
| sediment cores | anoxic basin | productive oxic zone |
| fossils | rapid burial | upland habitat |
| documents | dry storage, stable institutions | humid, non-literate, mobile |

---

## HANDOFF — what a larger model should compute

1. Pull the Zenodo box model, re-run with TS SOLVED but constrained by
   the SCA data as a soft prior rather than PRESCRIBED. This separates
   the prescribed-vs-solved confound noted above. Report A under both.
   `soft_prior_sweep()` is the generic form; it needs the real inversion.
2. Run T-1 across the species list. The CO cell is the interesting one:
   predict the size of the error in any polar-derived tropical CO
   history, which currently has no at-source constraint.
3. Run T-4 on the PAGES-class proxy network against gridded source maps.
   This is the cheapest test and needs no new field data.
4. Formalize the operator-class split as a decision procedure with a
   measurable stationarity criterion, so classification is not a
   judgement call. Done in `classify_operator()`; verify the
   stationarity criterion against a case with a known drifting operator.

Provenance: shape drafted in session, model Claude Opus 5, 2026-09-03;
computable half and this file drafted 2026-09-03. Source data are cited
above and are open access. Nothing here is a finished result.
