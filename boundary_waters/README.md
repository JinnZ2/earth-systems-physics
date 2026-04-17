# BWCA Sulfide Mine Cascade Simulation

**A physics-grounded, coupled-systems simulation of the cascading impacts of
proposed sulfide-ore copper-nickel mining in the Rainy River watershed above
the Boundary Waters Canoe Area Wilderness.**

500-year horizon. Three scenarios. 18 coupled subsystems.
Six audits. Five self-reinforcing collapse loops.
Stdlib-only Python. CC0. Falsifiable. Zero external dependencies.

-----

## Why this exists

On April 15, 2026, the U.S. Senate used a Congressional Review Act resolution
to nullify Public Land Order 7917 — the 20-year withdrawal that protected
225,378 acres of Superior National Forest headwaters from sulfide-ore copper
mining. The withdrawal was built on the U.S. Forest Service’s 2022
environmental assessment, which incorporated 675,000 public comments (95%+
in favor of protection) and concluded that sulfide-ore copper mining near the
Boundary Waters would cause **irreversible harm** to the ecosystem and
downstream Voyageurs National Park.

The CRA vote did not rebut the science. It routed around it via a procedural
maneuver that bypasses the normal 60-vote Senate threshold.

This simulation exists because:

1. The decision to permit sulfide mining in this watershed is being made on
   timescales of weeks, with damage horizons of centuries.
1. Existing environmental assessments are siloed: water quality, employment,
   health, and infrastructure are treated as separate domains. They are not.
1. The cascades that link chemistry to treaty obligations to Duluth port jobs
   are continuous and deterministic. They can be modeled directly from first
   principles.
1. Every parameter, every threshold, every coupling in this model is open,
   sourced, and falsifiable. Disagree with a value? Change it and re-run.

-----

## The thermodynamic argument in one paragraph

Pyrite (FeS₂) exposed to oxygen and water produces sulfuric acid and
dissolved heavy metals. The reaction has negative ΔG — it proceeds without
permission. Acidithiobacillus bacteria catalyze it at ~10⁶× the abiotic
rate. The Canadian Shield bedrock beneath the BWCA has near-zero carbonate
buffering capacity. Glacial till is thin. Water residence time in the lake
chain is ~3 years. Peat-rich wetlands methylate mercury at ~31% efficiency.
Lake trout concentrate methyl-Hg at ~7.5×10⁵ L/kg. Ojibwe subsistence fish
consumption is 7.9× the state average, protected under 1854 Treaty
usufructuary rights. The Boundary Waters Treaty of 1909 prohibits
transboundary pollution “to the injury of health or property on the other”
side. Climate warming doubles AMD oxidation kinetics per 10°C (Arrhenius
Q₁₀ ≈ 2.1). None of these are politically negotiable. They are thermodynamic,
hydrologic, biochemical, and legal facts. The cascade that links them is
what this model simulates.

-----

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHYSICAL CASCADE (cascade.py)                    │
│                                                                         │
│  L0 Chemistry   ──►  L1 Hydrology  ──►  L2 Ecology                      │
│  (AMD kinetics,      (Vollenweider     (manoomin, trout,                │
│   microbial           mass balance,     loon, amphibian,                │
│   catalysis,          lake residence    boreal forest)                  │
│   metal leach)        time)                                             │
│                                                                         │
│                           │                                             │
│                           ▼                                             │
│                                                                         │
│  L3 Community   ──►  L4 Port/Reservoir  ──►  L5 International Law       │
│  (wells, migration,  (Lake Superior           (BWT 1909, Trail Smelter  │
│   labor, treaty       loading, drinking       1941, IJC referral,       │
│   harvesters)         water, jobs)            state liability NPV)      │
└─────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    ECONOMIC CASCADE (econ_cascade.py)                   │
│                                                                         │
│  E0 Home/Property     E1 Worker Health     E2 Long-Term Care            │
│  (hedonic model,      (NIOSH + ATSDR:      (facility capacity,          │
│   tax base, Superfund  silicosis, Pb/Hg     Medicaid share,             │
│   listing trigger)     neuro, VSL)          family displacement)        │
│                                                                         │
│  E3 Community         E4 State/Federal     E5 Infrastructure            │
│  (water upgrades,     (Medicaid, unfunded  (85 MW grid load,            │
│   emergency response,  Superfund gap,       ratepayer subsidy,          │
│   school SpEd,         tourism tax,         water stress,               │
│   mental health)       IHS treaty gap)      road, EMS)                  │
└─────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  EXTENDED CASCADE (extended_cascade.py)                 │
│                                                                         │
│   X0 Climate Amplifier  (Arrhenius feedback → modifies L0 upstream)     │
│   X1 Lumber/Forest      (acid deposition, pulp contamination, jobs)     │
│   X2 Fish Consumption   (Ojibwe 7.9× amplifier, IQ loss, treaty)        │
│   X3 Air Quality        (SO₂, PM, Hg(g), BenMAP equivalents)            │
│   X4 Wildfire Amp       (fuel load + tailings overrun + Hg re-release)  │
│   X5 Port Cascade       (St Louis R, Canadian transit, fishing, dredge) │
└─────────────────────────────────────────────────────────────────────────┘
```

```
                           |
                           v
+-------------------------------------------------------------------------+
|               SECONDARY EFFECTS (secondary_effects.py)                  |
|                                                                         |
|  Self-reinforcing loops:                                                |
|    School death spiral   Healthcare collapse   Tax base death spiral    |
|    Insurance withdrawal  Emergency services collapse                    |
|                                                                         |
|  Missing contaminants:        Ecological services:                      |
|    Selenium (egg pathway)       Beaver dam water treatment              |
|    Manganese (neurotoxin)       Mycorrhizal network integrity           |
|                                 Invasive species corridors              |
|                                                                         |
|  Inter-generational:          Commercial cascade:                       |
|    Epigenetic (3 gen Hg)        22 outfitters, 35 lodges, 60 retail     |
|    Cultural knowledge break     Bank collateral impairment              |
|    (identity-level, p=0.0)      Insurance market withdrawal             |
|                                                                         |
|  Peatland methane:            Extraction topology:                      |
|    SRB suppression phase        TITLE->SURPLUS->POWER->ENFORCE->TITLE   |
|    Post-sulfate CH4 rebound     Value exits state; cost stays forever   |
|    Links to parent repo L3      Net transfers: 7 categories, all       |
|                                   irreversible                          |
+-------------------------------------------------------------------------+
```

```
+-------------------------------------------------------------------------+
|                    AUDITS (4 independent pipelines)                      |
|                                                                         |
|  Twin_Metals_audit.py              Corporate record + claim verification|
|  Twin_Metal_mitigation_             Thermodynamic + EROI + externality  |
|    strategies_audit.py              audit of each mitigation            |
|  hidden_dependancies.py            Supply chain + ratepayer cost-shift  |
|  climate_boundary.py               Stationarity collapse across all    |
|                                     engineering assumptions             |
|                                                                         |
|  Each audit produces scored, falsifiable claims. No single axis         |
|  requires the others to fail. The proposition needs all four to hold.   |
|  None does.                                                             |
+-------------------------------------------------------------------------+
```

Each layer is a pure function: `state_out = layer(state_in)`. No hidden
state. No mutable globals. Deterministic given a seed. Stochastic paths
(tailings dam failure probability) are explicit and seedable.

The secondary effects module adds **feedback loops** that the linear
cascade misses. These loops make the real trajectory worse than the
single-pass prediction because community collapse accelerates the
conditions that caused it.

-----

## Scenarios

|Key               |Description                                                           |
|------------------|----------------------------------------------------------------------|
|`protected`       |Public Land Order 7917 holds. No mine. Climate warms anyway.          |
|`proceed`         |CRA reversal stands. Twin Metals permitted, operates 20 years, closes.|
|`tailings_failure`|Mine operates + Mount Polley-class tailings dam failure at year 12.   |

Tailings dam failure in the `proceed` scenario is stochastic at 1.2% per
year per active facility — the empirical historical rate. Run multiple seeds
to sample the distribution. The `tailings_failure` scenario forces the event
for demonstration.

-----

## Headline results (500-year peak impact)

|Signal                       |Protected|Mine operates|Mine + tailings failure|
|-----------------------------|--------:|------------:|----------------------:|
|Border sulfate (mg/L)        |0        |12           |59                     |
|Manoomin acres lost          |0        |18,400       |18,400                 |
|Forced migrants              |0        |3,107        |8,060                  |
|Wells contaminated           |0        |3,059        |10,416                 |
|Boreal forest lost (acres)   |0        |13,748       |68,742                 |
|Treaty liability NPV         |$0       |$0           |$1.08 T                |
|Property loss                |$0       |$0.90 B      |$0.93 B                |
|Lifetime health cost         |$0       |$0.67 B      |$0.77 B                |
|Kids neuro-impaired          |0        |409          |409                    |
|Fish tissue Hg (mg/kg)       |0        |3.4          |3.4                    |
|Ojibwe RfD exceedance        |0        |134×         |134×                   |
|Cumulative impaired children |0        |6,333        |6,333                  |
|Lumber loss                  |$0       |$1.25 B      |$1.42 B                |
|Wildfire cost ($/yr peak)    |$17.1 M  |$54.0 M      |$58.8 M                |
|Port cost ($/yr peak)        |$0       |$120.6 M     |$145.8 M               |
|State annual load ($/yr peak)|$0       |$178.9 M     |$292.9 M               |
|Cumulative state 500-yr      |$0       |$56.7 B      |$118.9 B               |
|Fiscal collapse year         |—        |5            |5                      |

**The one-sentence summary:** The mine captures $3-5 B in ore revenue over
20 years; Minnesota absorbs $57-119 B in externalities over 500 years
across homeowners, workers, municipalities, ratepayers, treaty-band
harvesters, port operators, and the state general fund.

### Secondary effects (self-reinforcing loops, seed=42)

|Signal                            |Proceed  |Tailings failure|
|----------------------------------|--------:|---------------:|
|Community pop at year 30          |     754 |            179 |
|School district                   |  CLOSED |         CLOSED |
|Hospital                          |  CLOSED |         CLOSED |
|Property insurance                |WITHDREW |       WITHDREW |
|Volunteer firefighters at yr 30   |      30 |              7 |
|Outfitters surviving              |   16/22 |           0/22 |
|Lodges surviving                  |   26/35 |           0/35 |
|Bank collateral impaired          |     Yes |            Yes |
|Bank failure risk                 |      No |            Yes |
|Credit contraction                |     27% |           80%  |
|Peatland CH4 rebound (t CO2e/yr)  |       0 |       285,600  |
|Cultural transmission viable      |     Yes |            Yes |

### Extraction topology (extraction_topology.py)

|What                  |Direction           |Duration        |Reversible|
|----------------------|--------------------|----------------|----------|
|Ore concentrate       |OUT (Chile/Asia)    |20 yr           |No        |
|Revenue / dividends   |OUT (Santiago/London)|20 yr          |No        |
|Lobbying capital      |OUT (DC/St. Paul)   |Continuous      |No        |
|AMD                   |STAYS               |Centuries       |No        |
|Hg loading            |STAYS               |Centuries       |No        |
|Community collapse    |STAYS               |Permanent       |No        |
|Treaty liability      |STAYS               |Perpetual       |No        |
|Cultural knowledge    |DESTROYED           |Permanent       |No        |
|Perpetual treatment   |STAYS (unfunded)    |Perpetuity      |No        |

Composite extraction score: **98%**. The CAUSAL_LOOP from
`substrate_audit.py` maps exactly: TITLE (lease) -> SURPLUS (ore revenue,
exits state) -> POWER (lobbying) -> ENFORCE (CRA vote) -> TITLE.

-----

## Files

### Physical cascade

- `constants.py` — L0–L5 physical parameters (chemistry, hydrology, ecology,
  community, port, intl law). Every value sourced.
- `layers.py` — L0–L5 engine functions. Pure, stateless, deterministic.
- `cascade.py` — Year-by-year propagator with stochastic tailings failure.
- `export.py` — CSV output per scenario.

### Economic externality cascade

- `econ_constants.py` — E0–E5 parameters (property, health, LTC,
  municipal, state, infrastructure).
- `econ_layers.py` — Six externality engines.
- `econ_cascade.py` — Reads physical cascade, layers economic engines.
- `econ_export.py` — CSV output.

### Extended cascade (lumber, fish, climate, air, fire, port)

- `extended_constants.py` — X0–X5 parameters.
- `extended_layers.py` — Six extended engines.
- `extended_cascade.py` — Reads physical cascade, layers extended engines,
  applies climate feedback to chemistry.
- `extended_export.py` — CSV output.

### Secondary effects and extraction analysis

- `secondary_effects.py` — Five self-reinforcing community collapse loops
  (school, healthcare, insurance, emergency services, tax base), missing
  contaminants (Se, Mn), ecological service loss (beaver, mycorrhizal,
  invasives), inter-generational effects (epigenetic, cultural transmission
  break), peatland CH4 feedback, and commercial cascade (22 outfitters,
  35 lodges, banking, insurance).
- `displacement_sources.py` — Sourced displacement analogs from Picher OK
  (98.8% departure), Hinkley CA (32%), Flint MI (21%), Grassy Narrows ON
  (90% mercury poisoning, community stayed). Documents the five displacement
  pathways and derives the model's behavioral parameters from census data.
- `extraction_topology.py` — Maps the mine onto `substrate_audit.CAUSAL_LOOP`.
  Value flow ledger (5 outflows, 6 costs that stay), net transfer accounting
  (7 categories, each with falsifiable claim), composite score 98%.

### Audits (four independent pipelines)

- `Twin_Metals_audit.py` — Corporate record, claim verification, public
  statements vs actual operational history of Antofagasta.
- `Twin_Metal_mitigation_strategies_audit.py` — Thermodynamic dependency
  stack, EROI, and externality burden for each proposed mitigation.
- `hidden_dependancies.py` — Supply chain dependencies, ratepayer cost-shift,
  grid stress, reagent chain fragility.
- `climate_boundary.py` — Climate boundary-condition audit: 10 ground-truth
  trends, 8 mitigation breaks, wildfire x tailings coupling, 10 falsifiable
  claims, stationarity collapse table.

### Monte Carlo

- `monty_carlo.py` — Stochastic analysis over tailings failure timing.

### Output data

- `output_*.csv` — Physical cascade, 500 rows x 31 fields per scenario.
- `econ_*.csv` — Economic cascade, 500 rows x 42 fields per scenario.
- `extended_*.csv` — Extended cascade, 500 rows x 58 fields per scenario.

-----

## Running it

```bash
# No dependencies. Python 3.8+ stdlib only.

python3 cascade.py          # physical cascade, console summary
python3 econ_cascade.py     # physical + economic, console summary
python3 extended_cascade.py # physical + extended (lumber/fish/etc)

python3 export.py           # CSV exports for physical layers
python3 econ_export.py      # CSV exports for economic layers
python3 extended_export.py  # CSV exports for extended layers
```

Parameterize scenario and seed:

```python
from extended_cascade import run_extended_cascade

history = run_extended_cascade(scenario="proceed", seed=42)
for row in history:
    print(row["year"], row["sulfate_mg_l"], row["iq_loss_per_child"])
```

Run a Monte Carlo over tailings failure:

```python
from cascade import run_cascade

outcomes = []
for seed in range(1000):
    h = run_cascade(scenario="proceed", seed=seed)
    tailings_failed = any(r["tailings_failed"] for r in h)
    peak_sulfate = max(r["sulfate_mg_l"] for r in h)
    outcomes.append((seed, tailings_failed, peak_sulfate))
```

-----

## Physical basis (what’s modeled, where the numbers come from)

### L0 — Chemistry

- **Pyrite oxidation** (Singer & Stumm 1970): `FeS₂ + 7/2 O₂ + H₂O → Fe²⁺ + 2 SO₄²⁻ + 2 H⁺`
- Sulfate generation: 45 kg SO₄ per tonne waste rock (typical ore grade)
- Microbial catalysis factor: 10⁶× abiotic (Acidithiobacillus ferrooxidans)
- Heavy metal loading from USGS 2013 Twin Metals ore body assay:
  Hg 2.4 mg/t, Pb 180 mg/t, As 95 mg/t
- Post-closure decay half-life: ~290 years (empirical from abandoned hardrock
  mines, EPA Superfund records)

### L1 — Hydrology (Vollenweider mass balance)

- `dC/dt = (L - kC) / V`  →  steady state `C* = L / (kV)`
- Kawishiwi discharge: 24 m³/s (USGS gauge 05124480)
- Receiving lake chain volume: 3.0×10⁸ m³ (Birch Lake + South Kawishiwi)
- Mean lake residence time: 3.2 years
- Empirical ceiling at 4,000 mg/L SO₄, 15 ng/L Hg (observed AMD max)

### L2 — Ecology

- **Wild rice (manoomin)** sulfate toxicity: 10 mg/L (MN Rule 7050.0224,
  Pastor et al. 2017)
- **Lake trout Hg BAF**: 3.4×10⁵ L/kg (MPCA 2010 fish tissue database)
- **Loon Hg mortality**: 4 ppm whole-body (Evers et al. 2008)
- **Amphibian pH threshold**: 5.2 (egg-stage lethal)
- **Peat Hg methylation rate**: 31% (St. Louis River TMDL background)

### L3 — Community

- **Wells dependent on shallow aquifer**: 84% (MN DNR well logs, NE MN)
- **Treaty-band enrollment (usufructuary rights)**:
  Bois Forte 3,400 + Grand Portage 1,100 + Fond du Lac 4,200 = 8,700

### L4 — Port/Reservoir

- **Duluth-Superior tonnage**: 35 M short tons/yr (Great Lakes #1)
- **Port jobs direct**: 7,800; indirect: 13,100
- **Lake Superior residence time**: 191 years

### L5 — International Law

- **Boundary Waters Treaty 1909**, Article IV: “waters…shall not be
  polluted on either side to the injury of health or property on the other”
- **Trail Smelter Arbitration 1941**: customary international law precedent
  that transboundary air/water pollution creates state liability
- **IJC referral threshold**: 90 days sustained exceedance of treaty standard
- **Liability NPV**: $2.8 B/yr annualized (estimate based on manoomin loss,
  fishing rights impairment, and treaty-band subsistence harm)

### E0 — Home depreciation (hedonic models)

- Active mine proximity: 22% depreciation (Boyle & Kiel 2001)
- Contaminated well: 52% (Sims 2009)
- Superfund listing: 68% (Kiel & Williams 2007)

### E1 — Worker health (NIOSH/MSHA)

- Silicosis incidence: 8% lifetime per underground hardrock worker
- Mining fatal injury rate: 14.5 per 100,000 worker-years (MSHA)
- Value of Statistical Life: $11.6 M (EPA 2024)
- Pediatric cognitive loss: $1.2 M lifetime per child (IQ loss economic
  valuation, Trasande & Liu 2011)

### X0 — Climate amplification

- **Arrhenius Q₁₀ = 2.1** for AMD kinetics (Nordstrom & Alpers 1999)
- **Temperature rise 2100 RCP 8.5 (northern MN)**: +4.8 °C
- **Fire season extension**: 128 → 178 days
- **Extreme storm frequency**: 2.4× by 2100

### X2 — Fish consumption (treaty amplifier)

- **GLIFWC subsistence surveys**: Ojibwe mean consumption 142 g/day vs
  state average 18 g/day (7.9× amplifier)
- **EPA methyl-Hg RfD**: 0.1 µg/kg bw/day
- **IQ loss coefficient**: 0.18 points per µg/g maternal hair Hg
  (Faroe Islands cohort, Grandjean et al. 1997)
- **Hair/blood ratio**: 250 (WHO convention)

### X4 — Wildfire amplification

- **Hg volatilization from fire**: 92% (Friedli et al. 2003)
- **Stressed-forest fire multiplier**: 3.4× (USFS FIA plus beetle-kill
  analogy)
- **Suppression cost**: $2,800/acre (NIFC average large-fire cost 2020–2024)

### X5 — Port cascade

- **St Louis River current Hg**: 1.8 ng/L (MPCA, above TMDL of 1.3)
- **Contaminated dredge disposal**: $180/m³ vs $18/m³ clean (USACE)
- **IMO ballast treatment surcharge**: $2.80/m³ for contaminated origin

-----

## Scenario mechanics in detail

### Tailings dam failure stochastics

Historical base rate of major tailings dam failures: ~1.2% per year per
active major facility (Rico et al. 2008, Owen et al. 2020). Over a 20-year
mine life, cumulative probability of at least one failure is:

```
P(failure) = 1 - (1 - 0.012)²⁰ ≈ 22%
```

This is not a rare event. Mount Polley (2014), Brumadinho (2019), Samarco
(2015), Merriespruit (1994) — tailings dam failures are routine on
geological timescales.

The model triggers a failure stochastically in `proceed` scenario and
deterministically at year 12 in `tailings_failure`. A failure dumps 10
years of waste rock inventory instantly, amplifying downstream load 10×.

### Climate feedback loop

Climate warming accelerates pyrite oxidation via Arrhenius Q₁₀:

```
oxidation_rate(T) = oxidation_rate(T_baseline) × Q₁₀^((T - T_baseline) / 10)
```

At +4.8°C by 2100, rate multiplier is 2.1^0.48 ≈ 1.43×. Current
implementation applies this as a post-hoc multiplier to chemistry outputs
(good approximation for visualization; full closed-loop requires iterating
L0 within each year step).

Permafrost thaw separately degrades tailings dam frozen cores (in northern
facilities that rely on them), raising failure probability 3.6× by 2100.

### Why the mine operates at a permanent regional net loss

```
Mine revenue (20 yr @ ~$400 M/yr):              $8.0 B
                                                 ─────

Offset by annual regional externalities:
    Duluth port impact                   $125 M/yr × 500 yr
    Lumber/forest degradation            $25 M/yr × 500 yr
    Wildfire cost                        $40 M/yr × 500 yr
    Commercial fishing Lake Superior     $38 M/yr × 500 yr
    State Medicaid + Superfund gap       $60 M/yr × 500 yr
    Ratepayer grid subsidy               $406 M (one-time, year 5)

Cumulative 500-yr externality:           $142 B (proceed scenario)
```

The mine is economic for the operator (Antofagasta, Chile) because the
externalities are distributed onto parties who don’t sign the permit —
homeowners, ratepayers, Medicaid enrollees, Ojibwe harvesters, downstream
port workers, Canadian citizens, and the Minnesota state general fund.

This is a textbook externality transfer, not a mystery.

-----

## Falsifiability

Every threshold, every coefficient, every coupling is in a named constant.
This is deliberate. If you believe:

- The Hg BAF should be 5×10⁵ not 7.5×10⁵ → edit `WALLEYE_BAF`, re-run.
- The tailings failure rate is 0.5% not 1.2% → edit `TAILINGS_FAILURE_P`.
- The Q₁₀ for AMD is 1.8 not 2.1 → edit `AMD_Q10_FACTOR`.
- The mine won’t actually produce 20 kt/day → edit `ORE_TONNES_ANNUAL`.
- Some subsystem is missing → add a new layer file, import into cascade.

**What the model commits to:** that these are the right *categories* of
coupling. You cannot run the sulfate → manoomin → treaty rights cascade
without the manoomin threshold firing at roughly the measured value. You
cannot run the chemistry → hydrology → community cascade without wells
contaminating at roughly the expected rate. The values are arguable; the
coupling structure is not.

**What the model does not commit to:** specific timing of discrete events
(which year the tailings dam fails, which year the Superfund listing drops,
which year the Ojibwe file the suit). These are stochastic over the
ensemble; run multiple seeds.

-----

## Known limitations and next modules

### Addressed in this version

- **Secondary community collapse loops**: school, healthcare, insurance,
  emergency services, tax base death spirals now modeled with feedback
  (`secondary_effects.py`)
- **Missing contaminants**: selenium (egg bioaccumulation pathway) and
  manganese (child neurotoxicity) now tracked
- **Ecological service loss**: beaver dam treatment, mycorrhizal network
  integrity, invasive species corridors now modeled
- **Inter-generational effects**: epigenetic Hg transmission (3 gen,
  Minamata data), cultural knowledge transmission break (identity-level,
  replacement probability 0.0)
- **Peatland methane feedback**: SRB suppression -> post-sulfate CH4
  rebound linking to parent repo's atmosphere layer
- **Commercial cascade**: 22 outfitters, 35 lodges, 60 retail, banking
  collateral impairment, insurance market withdrawal
- **Displacement sourcing**: five pathways documented from Picher, Hinkley,
  Flint, Grassy Narrows census data (`displacement_sources.py`)
- **Extraction topology**: CAUSAL_LOOP mapping, value flow ledger, net
  transfer accounting (`extraction_topology.py`)
- **Climate boundary audit**: 10 trends, 8 mitigation breaks, wildfire x
  tailings, stationarity collapse (`climate_boundary.py`)

### Still outstanding

- Climate->chemistry feedback is post-hoc rather than closed-loop iteration
- No explicit groundwater transport model (uses residence-time proxy)
- Heavy metal speciation simplified (assumes equilibrium)
- Discount rate not applied to future costs (figures are undiscounted)
- Inflation not modeled (2026 USD held constant across 500 yr)
- Ojibwe fish consumption uses population average; household-level
  distribution would show worse tails
- Iron Range permit-cascade effect (if BWCA contamination triggers regional
  opposition to *any* mining, 62% of Duluth tonnage at risk not 5%)
- Canadian retaliation beyond port refusal (water-quality litigation,
  ballast-water treatment premiums, customs inspection multipliers)
- Moose population decline (winter tick + climate + habitat fragmentation)
- Pollinator cascade (heavy metals in wildflowers -> bee decline -> berry
  production -> food web)

### Integration points

- Link to `earth-systems-physics` L5 lithosphere layer for geomechanical
  tailings-dam stability modeling
- Link to `assumption_validator` to convert hardcoded thresholds into
  GREEN/YELLOW/RED falsifiable boundaries
- Link to `substrate_audit.py` — extraction topology already mapped;
  CAUSAL_LOOP confirmed as exact instance
- Link to `calibration/architecture_mismatch.py` — cultural knowledge loss
  already wired via identity-level encoding classifier
- Peatland CH4 -> `layer_3_atmosphere.py` coupling (pathway identified,
  not yet wired into parent cascade_engine)

-----

## Provenance and sourcing

All physical parameters reference published peer-reviewed literature,
government datasets, or peer-review environmental assessments. Key sources:

- **U.S. Forest Service 2022 Environmental Assessment** for PLO 7917
- **USGS 2013 Twin Metals ore body assay** for metal loadings
- **Singer & Stumm 1970** (pyrite oxidation kinetics)
- **Nordstrom & Alpers 1999** (AMD thermodynamics)
- **MPCA 2010 Minnesota Fish Tissue Database**
- **GLIFWC Subsistence Fish Consumption Surveys**
- **Faroe Islands Cohort (Grandjean et al. 1997)** for pediatric Hg
  neurotoxicity
- **EPA BenMAP** equivalents for air-quality health endpoints
- **NIOSH/MSHA** for mining occupational health
- **Rico et al. 2008** and **Owen et al. 2020** for tailings dam failure
  base rates
- **Boundary Waters Treaty of 1909** (text)
- **Trail Smelter Arbitration (U.S. v. Canada, 1941)**
- **IPCC AR6 Working Group 1** for regional climate projections
- **Great Lakes Legacy Act** records for St Louis River remediation
- **USFS FIA** (Forest Inventory & Analysis) for standing timber
- **Duluth Seaway Port Authority** annual reports

Every numerical constant is named and cited at the source file. Disagree
with a value? Find a better source and substitute. That’s the point.

-----

## Intellectual framing

This model is not advocacy. It is a mechanistic description of what happens
when a specific chemical reaction is initiated in a specific hydrological
configuration with specific downstream biological, human, legal, and
economic couplings.

The chemistry is not political. The manoomin sulfate threshold is not
political. The Boundary Waters Treaty is not political. The Trail Smelter
precedent is not political. Arrhenius kinetics are not political. Lake
Superior’s 191-year residence time is not political.

What *is* political is whether to initiate the reaction. This model exists
so that decision can be made with a clear account of what the reaction does
— not what stakeholders claim it will do, not what bonded surety estimates
it will do, but what the physics and chemistry and hydrology and biology
and treaty law, coupled honestly, say it does.

If the answer is “proceed anyway because the political economy demands
copper” — fine. Make that argument honestly, against this baseline. Don’t
make it by suppressing the 2022 study, routing around the 675,000 public
comments, or pretending the cascade stops at the permit boundary.

-----

## License and use

**CC0 — Public Domain Dedication.** No rights reserved. Use freely for any
purpose without attribution. Reverse-engineer it. Improve it. Fork it.
Delete my name. Put your own in. Submit it as testimony. Cite it in
litigation. Teach it in classrooms. Feed it to another AI for audit.

This framework was built by a long-haul trucker on a cell phone (well educated) during fuel
stops in the upper Midwest corridor, using open science, first-principles
reasoning, and the thermodynamic constraints that physical systems obey
regardless of political preference.

The watershed belongs to everyone downstream, including the people who will
be downstream in 2526.

Base rates locked in:
	
   •	2012 study of 14 American sulfide-ore copper mines, 13 of which were unable to control pollution into surrounding waters  — ~93% failure rate, which is what Sen. Smith was gesturing at from the floor
	
   •	At some mines, acidic drainage is detected within 2–5 years after mining begins, whereas at other mines, it is not detected for several decades. In addition, acidic drainage may be generated for decades or centuries after it is first detected 
	
   •	Water treatment will be required in perpetuity  once AMD establishes
	
   •	MN DNR rejected dry stacking for PolyMet in 2018  as unsuitable for wet climates — this is Twin Metals’ offered mitigation
Antofagasta as calibration data, not legacy:
	
   •	2014, the Supreme Court of Chile determined that Minera Los Pelambres should return the water to the community  — order not complied with; dam still stands
	
   •	Chile’s environmental regulator initiated a sanction process against the copper mine for deficiencies associated with tailings management  (2022)
	
   •	the Los Pelambres Mining Company had illegally extracted a total of 990,423 cubic meters (35 million cubic feet) of water from 17 wells  in a water-scarce region
	
   •	a copper mining project tainted by environmental damage sues 32 locals  — SLAPP response to community organizing
Leverage points (ordered by physical irreversibility they protect):
	
   1.	Tribal treaty litigation — 1854 Treaty territory, federal law, CRA-immune. Michael Fairbanks, chairman of White Earth Nation, said tribes will continue partnering with environmental, sporting and other groups to stop mining projects that “cross our boundary when it comes to our treaty rights” 
	
   2.	MN DNR state permits — already rejected dry-stack storage in Feb 2022
	
   3.	Boundary Waters Treaty of 1909 — Quetico is downstream, transboundary vector
	
   4.	Lease reinstatement litigation — 2025 DOI memo reversing 2022 legal opinion is itself litigable
	
   5.	Copper price cycle — killed INCO in the 1970s, same physics still applies
The precedent spillover is the sleeper hazard:
“If and when President Trump signs this indefensible bill, it will mark the first time a mineral withdrawal was killed by the Congressional Review Act” . Every public land order since 1996 is now theoretically reversible by a simple-majority vote with no environmental review. That’s a much bigger structural change than the Twin Metals decision itself.




-----

## Related repositories

- [`earth-systems-physics`](https://github.com/JinnZ2/earth-systems-physics) — Seven-layer coupled differential equation stack (EM → magnetosphere → ionosphere → atmosphere → hydrosphere → lithosphere → biosphere)
- [`assumption_validator`](https://github.com/JinnZ2/assumption_validator) — Falsifiable GREEN/YELLOW/RED threshold monitoring
- [`substrate_audit.py`](https://github.com/JinnZ2) — Metrology-based AI hallucination audit (TC-1 through TC-10)
- [`first_principles_audit.py`](https://github.com/JinnZ2) — Six Sigma DMAIC validation engine
- [`Regenerative-intelligence-core`](https://github.com/JinnZ2/Regenerative-intelligence-core) — Physics-first civilizational governance framework
- Fairmont Ecological Recovery Framework — Real-time cascade collapse detection






All CC0. All falsifiable. All built for the long haul.
