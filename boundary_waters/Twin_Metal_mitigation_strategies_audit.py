"""
BWCA / Twin Metals — Thermodynamic, EROI, and Externality Audit

CC0. Stdlib only.

Companion to bwca_audit.py.

Purpose:
The first audit checked whether claims match physics and whether the
operator's behavior matches its PR. This one goes underneath:

```
    - What does each "innovation" ACTUALLY depend on, thermodynamically?
    - What externalities does each one shift, hide, or amplify?
    - What is the net energy balance of the whole proposition?

Every mitigation technology has an energy backbone, a materials
backbone, and a failure surface. The failure surface is where the
externalities live. This audit walks each one.
```

Structure:
SECTION A: Dependency stack per mitigation (what keeps it running)
SECTION B: Externality burden ledger (who pays, in what units, over what timescale)
SECTION C: EROI — energy return on investment, with proper boundaries
SECTION D: Energy-flow diagram of the whole system
SECTION E: Failure-mode thermodynamics (where entropy actually lives)
SECTION F: Falsifiable thermodynamic claims (TT-1 through TT-10)
"""

from dataclasses import dataclass, field
from typing import Optional

# ==============================================================================

# SECTION A — DEPENDENCY STACK PER MITIGATION

# ==============================================================================

# For each "innovation" offered by Antofagasta / Twin Metals, list what it

# actually requires to work. If any dependency fails, the mitigation fails.

@dataclass
class Mitigation:
    name: str
    claimed_function: str
    dependencies_energy: list        # continuous energy inputs required
    dependencies_materials: list     # material inputs / consumables
    dependencies_information: list   # sensors, models, expertise, governance
    dependencies_time: str           # how long these must hold
    single_point_failures: list      # what takes the whole thing down
    externality_if_failed: str       # what the watershed eats

MITIGATIONS = [
    Mitigation(
        name="Dry-stack tailings storage",
        claimed_function="Filter tailings to ~15-20% moisture and stack them dry to reduce acid/heavy-metal leachate vs. wet tailings ponds.",
        dependencies_energy=[
            "Continuous electrical power for pressure/vacuum filtration (energy-intensive, ~2-5x wet tailings for dewatering).",
            "Diesel for stacker conveyors, haul trucks, compactors.",
            "Continuous power for liner monitoring, drainage collection pumps.",
        ],
        dependencies_materials=[
            "Filter press consumables (cloths, cake-release agents).",
            "Impermeable liners (HDPE or equivalent) -- finite service life, 20-50 yr typical vs. perpetuity required.",
            "Cover materials (soil, vegetation, geomembrane) for closure.",
            "Reagents to suppress oxidation (lime, limestone) -- consumed continuously.",
        ],
        dependencies_information=[
            "Real-time moisture monitoring (if tailings wet up, they liquefy).",
            "Seepage monitoring network (liner leak detection).",
            "Active management by a solvent corporation with on-site expertise.",
        ],
        dependencies_time="Perpetuity. Dam engineer David Chambers: '10,000 years is a conservative estimate' for required integrity.",
        single_point_failures=[
            "Corporate bankruptcy / abandonment -- mine closes, power stops, liners fail.",
            "Liner puncture during stacking (documented cause at multiple operations).",
            "Extreme precipitation event re-saturating the stack (wet boreal climate).",
            "Freeze-thaw cycling on exposed faces (Minnesota: ~120 cycles/yr).",
            "Reagent supply chain interruption -- oxidation resumes on hour-scale.",
        ],
        externality_if_failed=(
            "Acid generation resumes; sulfuric acid + heavy metals mobilize; "
            "gravity-fed into Rainy River watershed; perpetual water treatment "
            "required. Five reference dry-stack operations (2 US lower-48 + 3 AK) "
            "combined >8,000 spill events per April 2022 report."
        ),
    ),

    Mitigation(
        name="Closed-loop water recycling",
        claimed_function="Recirculate process water so no mine contact water discharges to the environment.",
        dependencies_energy=[
            "Continuous pumping energy (high-head, high-volume).",
            "Power for reverse osmosis / ion exchange / lime neutralization.",
            "Power for cooling (to prevent evaporative concentration of salts).",
        ],
        dependencies_materials=[
            "Membrane replacement (RO membranes: 3-7 yr service life).",
            "Ion-exchange resins (foul, require regeneration with acid/base).",
            "Lime, caustic, coagulants, flocculants — consumed continuously.",
            "Freshwater make-up — evaporation and ore moisture losses mean "
            "the 'closed' loop is always net-importing water.",
        ],
        dependencies_information=[
            "Continuous water chemistry monitoring (pH, metals, sulfate, "
            "sulfide, conductivity).",
            "Flow balance accounting to detect leakage.",
        ],
        dependencies_time=(
            "Operating life + post-closure period, which for AMD-generating "
            "mines is effectively perpetual. No large hardrock mine has "
            "demonstrated AMD can be stopped once started."
        ),
        single_point_failures=[
            "Power loss (containment pond overtops).",
            "Groundwater inflow in glacially-fractured bedrock (geologically "
            "guaranteed in the Duluth Complex; mine becomes net water IMPORTER).",
            "Snowmelt / rainfall events exceeding freeboard design.",
            "Pump failure, valve failure, pipeline rupture (see Los Pelambres "
            "2022 pipeline leak).",
        ],
        externality_if_failed=(
            "Contaminated process water enters Birch Lake / South Kawishiwi → "
            "BWCAW → Voyageurs NP → Quetico (Canada). Transboundary. "
            "Sulfate contamination destroys wild rice (Zizania palustris) at "
            "concentrations above ~10 mg/L; treaty-protected resource for "
            "Anishinaabe peoples."
        ),
    ),

    Mitigation(
        name="AI / SIRO platform optimization (MIT partnership)",
        claimed_function="Machine learning optimizes ore processing to improve copper recovery and reduce reagent consumption.",
        dependencies_energy=[
            "Data center compute (training + inference).",
            "Sensor network power (XRF, hyperspectral, flotation cameras).",
            "Communication bandwidth to cloud infrastructure.",
        ],
        dependencies_materials=[
            "GPU/TPU hardware (itself copper-intensive — recursive dependency).",
            "Sensor equipment replacement on operational timescales.",
        ],
        dependencies_information=[
            "Training data quality — model is only as good as labeled history.",
            "Assumption that optimization target correlates with stakeholder "
            "welfare (it does not — optimizes per-ton intensity, not watershed flux).",
        ],
        dependencies_time="Continuous; model drift if ore body heterogeneity changes.",
        single_point_failures=[
            "Scope 3 blind spot: the optimized objective function EXCLUDES "
            "watershed-scale externalities by construction.",
            "Jevons paradox: efficiency gains lower per-unit cost, which "
            "increases economic viability of lower-grade ore, which "
            "INCREASES total material throughput and total tailings.",
        ],
        externality_if_failed=(
            "The failure mode is NOT the AI breaking. The failure mode is "
            "the AI WORKING PERFECTLY at the wrong objective. It accelerates "
            "the extraction rate, increases the tailings generation rate, and "
            "reports its own success as an intensity metric (efficiency per "
            "ton), which is orthogonal to the harm function (flux to watershed "
            "over multi-century timescales)."
        ),
    ),

    Mitigation(
        name="Autonomous haul truck fleet (Centinela model)",
        claimed_function="24/7 autonomous operation reduces human hazard exposure and operating cost per ton.",
        dependencies_energy=[
            "Diesel (primary). Battery-electric pilot fleets exist but are "
            "copper-intensive themselves.",
            "Continuous compute for vehicle autonomy stack.",
            "High-precision GPS + cellular/radio infrastructure.",
        ],
        dependencies_materials=[
            "Tires (per-unit cost $40-80K, 6-12 mo life at 24/7 duty).",
            "Wear components (frames, suspension, hydraulics).",
            "Replacement sensors (LIDAR, radar).",
        ],
        dependencies_information=[
            "High-definition mine maps, updated continuously.",
            "Communication backbone.",
        ],
        dependencies_time="Operating life only — these do not persist post-closure.",
        single_point_failures=[
            "Softens the labor-cost ceiling that historically constrained "
            "mine expansion. Bottleneck removed = MORE ore moved, not safer ore moved.",
        ],
        externality_if_failed=(
            "Even working perfectly, these amplify every downstream physical "
            "harm pathway: more ore moved → more rock broken → more sulfide "
            "surface area exposed → more acid potential → more tailings volume. "
            "The 'worker safety' framing is technically true but it's "
            "constraint-relaxation, not harm-reduction."
        ),
    ),

    Mitigation(
        name="Renewable-powered mine (Nueva Centinela $4.4B expansion)",
        claimed_function="Renewable electricity powers operations, reducing CO2 per ton copper.",
        dependencies_energy=[
            "Solar + wind + grid contracts; battery storage for 24/7 continuity.",
            "Firming capacity (gas, hydro, or curtailment-tolerant ops).",
        ],
        dependencies_materials=[
            "Solar panels (silver, silicon, aluminum — recursive metal demand).",
            "Wind turbines (rare earths, copper, steel).",
            "Batteries (lithium, nickel, cobalt, copper).",
        ],
        dependencies_information=[
            "Grid-balancing algorithms.",
            "ESG reporting frameworks (Scope 1/2 only — excludes Scope 3 watershed impacts).",
        ],
        dependencies_time="Operating life; hardware replaces on 20-30 yr cycles.",
        single_point_failures=[
            "The reported metric (Scope 1/2 CO2) is DECOUPLED from the "
            "actual harm metric (watershed flux). Renewable energy changes "
            "the carbon footprint of the bulldozer; it does not change "
            "what the bulldozer does.",
            "Explicit production target is +30% — so even if intensity "
            "falls, absolute extraction rises, along with absolute tailings.",
        ],
        externality_if_failed=(
            "Same as above — this is a metric-swap, not a harm reduction. "
            "The renewable claim answers a question (decarbonization) that "
            "was not asked by the Boundary Waters fight (water / ecosystem / "
            "treaty integrity). Wrong axis."
        ),
    ),
]

# ==============================================================================

# SECTION B -- EXTERNALITY BURDEN LEDGER

# ==============================================================================

# The company's cost sheet and the REAL cost sheet diverge. This is the gap.

@dataclass
class Externality:
    category: str
    who_pays: str
    units: str
    timescale: str
    on_balance_sheet: bool
    notes: str

EXTERNALITIES = [
    Externality(
        category="Perpetual water treatment",
        who_pays="Downstream public / taxpayers (via Superfund if company fails)",
        units="USD/yr, in perpetuity",
        timescale="Centuries to millennia",
        on_balance_sheet=False,
        notes=(
            "Industry bonding is typically sized for decades, not centuries. "
            "Earthworks estimates 40 US hardrock mines will generate 17-27 "
            "BILLION gallons of polluted water per year requiring treatment "
            "in perpetuity. Mount Polley (BC, 2014) cleanup still ongoing."
        ),
    ),
    Externality(
        category="Tailings dam failure contingent liability",
        who_pays="Downstream communities, ecosystem, Canadian transboundary",
        units="Lives + cubic meters of release + cleanup USD",
        timescale="Instantaneous event; consequences multi-century",
        on_balance_sheet=False,
        notes=(
            "Global tailings dam failure rate ~4.4/yr (1947-2021). "
            "'19 catastrophic failures predicted globally between 2018 and 2027' "
            "(Earthworks). Parent company Antofagasta has an open record of "
            "tailings management sanctions (2022 SMA charges) and a Chilean "
            "Supreme Court demolition order (2014) with which it has not complied."
        ),
    ),
    Externality(
        category="Wild rice / treaty resource destruction",
        who_pays="Anishinaabe peoples (Fond du Lac, Grand Portage, Bois Forte, 1854 ceded territory)",
        units="Acres of sulfate-impaired waters; loss of treaty-protected harvest",
        timescale="Multi-generational",
        on_balance_sheet=False,
        notes=(
            "Wild rice (manoomin) is destroyed at sulfate >10 mg/L. "
            "Sulfate is the defining byproduct of sulfide-ore mining. "
            "Treaty rights are federal law; damage is non-monetizable under "
            "treaty terms. Birch Lake already listed as sulfate-impaired."
        ),
    ),
    Externality(
        category="Outdoor recreation economy displacement",
        who_pays="Northeastern Minnesota regional economy",
        units="Jobs + annual GDP",
        timescale="Mine lifetime + post-closure decades",
        on_balance_sheet=False,
        notes=(
            "Outdoor recreation economy in NE Minnesota: 17,000+ jobs, "
            "$1B+ annual sales (American Fisheries Society 2026). "
            "One containment failure upstream of BWCAW eliminates the "
            "wilderness-brand premium on which this economy runs."
        ),
    ),
    Externality(
        category="Fish / wildlife / biodiversity loss",
        who_pays="Ecosystem; downstream wildlife; anglers/hunters",
        units="Population declines; species-level extirpation risk",
        timescale="Multi-decadal to permanent",
        on_balance_sheet=False,
        notes=(
            "Low-pH, metals-laden water eliminates aquatic macroinvertebrates "
            "(base of food web). Documented recovery timescales at recovering "
            "AMD sites: 15-30+ years AFTER treatment begins, and only partial."
        ),
    ),
    Externality(
        category="Precedent spillover (policy externality)",
        who_pays="Every community living near a federal public land order issued since 1996",
        units="Number of reversible protections",
        timescale="Permanent change to rule of law",
        on_balance_sheet=False,
        notes=(
            "First-ever CRA kill of a mineral withdrawal. Every post-1996 "
            "public land order is now theoretically reversible by simple "
            "majority vote. This is a political externality with no price tag."
        ),
    ),
    Externality(
        category="Geopolitical / trade externality",
        who_pays="US strategic mineral security narrative",
        units="Credibility of 'critical minerals' framing",
        timescale="Ongoing",
        on_balance_sheet=False,
        notes=(
            "Sen. Smith's floor statement: ore from this mine would be sent "
            "to Chinese smelters. If true, the national-security argument "
            "collapses: the US eats the watershed damage; China gets the "
            "refined metal. This is the exact opposite of the stated policy goal."
        ),
    ),
    Externality(
        category="Embedded-energy externality",
        who_pays="Global energy budget; climate",
        units="GJ / kg Cu produced",
        timescale="Ongoing + cumulative",
        on_balance_sheet=False,
        notes=(
            "Declining ore grades mean rising energy input per kg Cu. "
            "Koppelaar 2016: energy cost 52-255 MJ/kg Cu surface mining at "
            "0.3-0.5% ore grade. Calvo/Mudd: Chilean copper ore grade fell "
            "~28.8% in 10 years; energy consumption rose 46% while copper "
            "production rose only 30%. Efficiency gains are already being "
            "OUTRUN by grade decline."
        ),
    ),
]

# ==============================================================================

# SECTION C -- EROI (Energy Return on Investment), proper boundaries

# ==============================================================================

# Copper is not a fuel; it doesn't "return" energy the way oil does.

# But you can still compute a useful EROI-analog by asking:

# What is the ratio of useful energy delivered over the copper's service life

# to the lifecycle energy invested to mine, refine, transport, and remediate?

@dataclass
class EROIComponent:
    name: str
    value_range: str
    source_basis: str
    notes: str

EROI_STACK = [
    EROIComponent(
        name="Mining + beneficiation energy cost (E_extract)",
        value_range="52-255 MJ/kg Cu (surface); 60-447 MJ/kg Cu (underground)",
        source_basis="Koppelaar 2016, regression over 28 Cu mines, 191-value dataset",
        notes=(
            "Underground mine + declining ore grade puts Twin Metals at the "
            "HIGH end of this range. 0.5% ore grade: 60 MJ/kg. 0.3%: 447 MJ/kg. "
            "This is BEFORE smelting, refining, and transport. Depth + wet "
            "climate + remote site pushes it higher still."
        ),
    ),
    EROIComponent(
        name="Smelting + refining energy (E_refine)",
        value_range="+10-40 MJ/kg Cu additional",
        source_basis="Global industry averages (USGS, Norgate et al.)",
        notes="If ore ships to Chinese smelters, this energy is spent overseas; emissions are offshored.",
    ),
    EROIComponent(
        name="Transport energy (E_transport)",
        value_range="+5-30 MJ/kg Cu (varies with shipping distance)",
        source_basis="LCA literature",
        notes="Minnesota -> Chinese smelter -> finished goods -> back to US market = global circumnavigation.",
    ),
    EROIComponent(
        name="Perpetual water treatment energy (E_treat)",
        value_range=(
            "Effectively INFINITE at boundary-condition if integrated over "
            "required timescale. Any positive annual energy flux x infinite "
            "time -> undefined finite EROI."
        ),
        source_basis="Chambers: 10,000 yr minimum integrity requirement for tailings structures.",
        notes=(
            "This is the hidden term that breaks naive EROI calculations. "
            "Conventional LCAs truncate at 100 yr, burying the long-tail "
            "energy liability. Honest EROI accounting at this site is "
            "non-convergent."
        ),
    ),
    EROIComponent(
        name="Useful energy delivered by copper over service life (E_service)",
        value_range=(
            "Depends on end use. In an EV motor or solar inverter over 20-30 yr, "
            "the copper enables ~10-100x its embodied energy in delivered "
            "electricity if everything else in the system works."
        ),
        source_basis="Fizaine & Court 2015; Dupont et al. 2018",
        notes=(
            "The 'renewable energy needs copper' argument is real -- at the "
            "system scale. But it depends on: (a) the copper actually going "
            "to renewables (not, e.g., Chinese smelter -> Chinese construction "
            "sector), (b) being recycled at end of life (Harmsen 2013 shows "
            "recycling saturates in a growing system), and (c) the ore grade "
            "holding up (it isn't)."
        ),
    ),
]

EROI_HEADLINE = """
HEADLINE EROI FINDING

Three structural problems with the "responsible copper = green transition" EROI argument:

(1) ORE-GRADE DECLINE IS OUTPACING EFFICIENCY GAINS.
Chilean Cu ore grade fell ~28.8% over 10 years (Calvo/Mudd).
Energy consumption rose 46% while copper production rose 30% over the same period.
Net: energy-per-kg-Cu is rising. AI optimization narrows the gap; it does not close it.

(2) THE PERPETUAL-TREATMENT TERM IS NON-CONVERGENT.
Any AMD-generating mine has a post-closure energy obligation that runs
for centuries-to-millennia. Standard LCA truncation at 100 yr hides this.
Honest integration makes site-level EROI undefined (bounded energy
return / unbounded energy liability -> zero in the limit).

(3) THE "CRITICAL MINERALS FOR CLEAN ENERGY" FRAMING IS STRUCTURALLY VULNERABLE.
If the output ore goes to Chinese smelters, the renewable-transition
argument dissolves. The US eats the energy, water, and ecosystem cost;
another economy receives the refined metal. The supply-chain destination
is the axis of the argument, and it is unverified in PR materials.

Conclusion: at this specific site, with this specific operator, under current
ore-grade trends and current end-use uncertainty, the EROI case for "Boundary
Waters mining as part of the energy transition" does not close.
"""

# ==============================================================================

# SECTION D -- ENERGY-FLOW DIAGRAM

# ==============================================================================

# Where the joules actually go, and where the entropy accumulates.

FLOW_DIAGRAM = r"""
INPUTS (energy + materials)                OUTPUTS
+----------------------------------------------+   +----------------------+
| Diesel for fleet (24/7)                      |   | Cu concentrate       |
| Grid/renewable electricity                   |   | (~30% Cu, exported   |
| Explosives                                   |-->|  to smelter, likely  |
| Water (net import despite "closed loop")     |   |  overseas)           |
| Reagents (lime, flocculants, cyanide,        |   +----------------------+
|           collectors, frothers)              |               |
| Labor (small on-site)                        |               v
| Capital ($1.7B stated, will rise)            |   +----------------------+
| Regulatory + legal + PR expenditure          |   | Refined Cu -> end use|
+----------------------------------------------+   | (EVs? construction?  |
              |                           |  grid? uncertain)    |
              v                           +----------------------+
+-----------------------------+                        |
|  Ore body (0.3-0.6% Cu,     |              ~30 yr service life
|  Duluth Complex sulfide)    |              embodied energy paid back
|  ~1% of rock mass is metal  |              IF it goes to productive end use
|  ~99% becomes tailings      |                        |
+-----------------------------+                        v
              |                            +----------------------+
+---------------+----------------+           | Recycled at EoL?     |
v                                v           | (recycling saturates |
+-----------+                   +-------------+    |  in growing systems  |
| 30% Cu    |                   | Tailings    |    |  -- Harmsen 2013)    |
| product   |                   | (~99% of    |    +----------------------+
| (exits)   |                   |  mass)      |
+-----------+                   | + waste rock|
                                +-------------+
                                      |
              +---------------------------+---------------------------+
              v                           v                           v
+------------+             +------------+              +------------+
| Heat       |             | Sulfide    |              | Fine       |
| dissipated |             | surface    |              | particulate|
| (crushing, |             | area       |              | (dust)     |
|  grinding) |             | exposed to |              +------------+
+------------+             | O2 + H2O   |                    |
                           +------------+                    v
                                 |              +--------------------+
                                 v              | Airborne metals    |
                    +-------------------+    | (Pb, As, Ni)       |
                    | 4 FeS2 + 15 O2 +  |    +--------------------+
                    | 14 H2O ->         |              |
                    | 4 Fe(OH)3 +       |              v
                    | 8 H2SO4           |    deposition on snow,
                    | (accelerated 1e2- |    lakes, vegetation
                    |  1e6x by microbes)|
                    +-------------------+
                                 |
                                 v
                    +---------------------+
                    | H+, SO4(2-), Cu(2+),|
                    | Ni(2+), Zn(2+),     |
                    | Pb(2+),             |
                    | As, Hg, Cd mobilized|
                    +---------------------+
                                 |
                                 v
                    +---------------------+
                    | ENTROPY DUMP:       |
                    | Rainy River         |
                    | watershed ->        |
                    | BWCAW ->            |
                    | Voyageurs NP ->     |
                    | Quetico (Canada)    |
                    +---------------------+
                                 |
                                 v
                    +---------------------+
                    | Absorbed by:        |
                    | * Wild rice         |
                    | * Fish              |
                    | * Sediments         |
                    | * Treaty rights     |
                    | * Tourism economy   |
                    | * Downstream health |
                    +---------------------+

Key property of this diagram:
The "innovations" (AI, autonomous fleet, renewable power, dry-stack)
all operate on the LEFT side of the diagram -- the input side.
The harm is on the RIGHT side -- the output / dump side.
The couplings from input-side optimizations to output-side harm are
WEAK (renewable power, AI) or INVERTED (autonomous fleet -> more throughput).
"""

# ==============================================================================

# SECTION E -- FAILURE-MODE THERMODYNAMICS

# ==============================================================================

# Entropy has to go somewhere. Here is where.

FAILURE_THERMO = """
FAILURE-MODE THERMODYNAMICS

Second law framing:
A sulfide-ore copper mine is a large-scale entropy concentrator
(it moves Cu from dispersed low-concentration ore into concentrated
refined product). This concentration is paid for by a correspondingly
large entropy export. The entropy export MUST go somewhere.

Exported entropy, by pathway:

1. THERMAL entropy -> atmosphere
   Waste heat from crushing, grinding, smelting.
   Disperses rapidly. Not the bottleneck.

2. CHEMICAL entropy -> watershed
   Sulfides oxidize into sulfates + acid + mobilized heavy metals.
   This is the DOMINANT entropy export at a sulfide mine.
   It has a multi-century residence time in the watershed.
   Containment strategies (dry-stack, liners, water treatment) do
   not eliminate this entropy -- they attempt to SLOW its release.

3. MATERIAL entropy -> tailings volume
   ~99% of mined rock becomes finely ground tailings.
   Mass is permanent (matter conserved). Location is permanent
   (tailings don't go back to the pit economically).
   The volume is the permanent scar.

4. INFORMATIONAL entropy -> loss of institutional memory
   Operators change; bonds lapse; monitoring degrades.
   Post-closure knowledge decay is a documented failure mode
   (the cliff failure at ~20-25 years in knowledge-decay models).
   The Jinn2 urban-resilience-sim soil module encodes this explicitly.

5. POLITICAL / LEGAL entropy -> precedent
   The CRA bypass is a one-way ratchet. Once the tool has been used
   to kill a mineral withdrawal, every existing withdrawal is
   reversible by the same mechanism. This degrades the structural
   entropy-export capacity of the legal system for all future
   conservation decisions.

Thermodynamic identity of the proposition:
Small, temporary, localized concentration event (refined copper
exits the site, payable in cash to shareholders over ~30-year mine life)
paid for by
Large, permanent, distributed entropy export
(watershed + atmosphere + community + legal system, indefinite timescale).

The books do not balance at the site boundary.
They are made to appear to balance by truncating the accounting.
"""

# ==============================================================================

# SECTION F -- FALSIFIABLE THERMODYNAMIC CLAIMS (TT-1 through TT-10)

# ==============================================================================

@dataclass
class ThermoClaim:
    id: str
    claim: str
    falsifier: str
    state: str

    THERMO_CLAIMS = [
    ThermoClaim(
    id="TT-1",
    claim="Dry-stack tailings in wet boreal climate are a net thermodynamic improvement over wet tailings.",
    falsifier="Show a wet-climate dry-stack facility with zero spill / leak events over operational life AND documented post-closure acid-generation suppression for >50 yr.",
    state="UNFALSIFIED (>8,000 spills across 5 reference operations; MN DNR rejected for wet climate).",
    ),
    ThermoClaim(
    id="TT-2",
    claim="A 'closed-loop' water system in glacially-fractured Duluth Complex bedrock is physically achievable.",
    falsifier="Demonstrate a comparable-hydrogeology mine with net-zero water exchange with surroundings across a full hydrologic year, including spring freshet.",
    state="UNFALSIFIED (no precedent in literature).",
    ),
    ThermoClaim(
    id="TT-3",
    claim="AI optimization of mine operations reduces ABSOLUTE watershed flux of metals, not just per-ton intensity.",
    falsifier="Produce peer-reviewed study showing an AI-optimized mine reduced watershed-scale metal flux vs. baseline while maintaining or increasing production.",
    state="UNFALSIFIED (all published AI metrics are intensity, not flux; Jevons-paradox dynamics suggest coupling runs in the opposite direction).",
    ),
    ThermoClaim(
    id="TT-4",
    claim="Renewable-powered mining reduces the relevant harm function at Boundary Waters.",
    falsifier="Show that watershed-scale acid and metal flux depends on the carbon intensity of the energy used to break the rock.",
    state="TRIVIALLY UNFALSIFIABLE (rock chemistry is indifferent to the source of the bulldozer's power).",
    ),
    ThermoClaim(
    id="TT-5",
    claim="Autonomous haul fleets reduce net environmental impact.",
    falsifier="Show that increased throughput (which is the explicit purpose of 24/7 autonomous ops) correlates with reduced total tailings generation.",
    state="UNFALSIFIED; the relationship is physically inverted — more throughput = more tailings.",
    ),
    ThermoClaim(
    id="TT-6",
    claim="Current ore grade decline is being offset by efficiency gains.",
    falsifier="Show industry-wide energy/kg-Cu declining while ore grades decline.",
    state="UNFALSIFIED. Calvo/Mudd: Chilean Cu industry used 46% more energy to produce 30% more Cu over 10 yr while grades fell ~29%.",
    ),
    ThermoClaim(
    id="TT-7",
    claim="Perpetual post-closure treatment costs are bonded adequately.",
    falsifier="Show a hardrock metal mine with a closure bond sized to fund treatment at market energy prices for >=500 years.",
    state="UNFALSIFIED (industry-standard bonds are sized for decades).",
    ),
    ThermoClaim(
    id="TT-8",
    claim="The EROI of Twin Metals output, over full life-cycle boundary, is positive.",
    falsifier="Present a full life-cycle EROI with perpetual-treatment term included out to the pyrite-oxidation extinction timescale.",
    state="UNFALSIFIED; with the perpetual-treatment term included, site-level EROI is non-convergent.",
    ),
    ThermoClaim(
    id="TT-9",
    claim="Ore from Twin Metals will be refined and used in a way that serves US energy transition / national security.",
    falsifier="Show signed offtake agreements directing the ore to US-domestic smelters serving US-domestic clean-energy manufacturing.",
    state="UNFALSIFIED. Public statements indicate export to Chinese smelters is the likely path.",
    ),
    ThermoClaim(
    id="TT-10",
    claim="The mitigation stack collectively reduces risk to the watershed to 'acceptable' levels.",
    falsifier="Show that the joint failure probability across all mitigation layers (dry-stack + closed-loop + monitoring + bonding + corporate compliance) is below the base rate for this mine class (~7% non-failure).",
    state=(
    "UNFALSIFIED. US base rate for sulfide-ore Cu mine water-quality success: ~7%. "
    "Parent-company compliance track record: documented Supreme-Court non-compliance. "
    "Joint success probability is bounded ABOVE by the minimum of the layer probabilities, "
    "which is the corporate-compliance layer at this site."
    ),
    ),
    ]

    # ==============================================================================

    # SCORING (thermodynamic audit dimensions)

    # ==============================================================================

    THERMO_SCORING = {
    "dependency_stack_brittleness":       {"score": 9, "of": 10, "note": "Every mitigation has multiple single-point failure modes over required timescale."},
    "externality_off_balance_sheet":      {"score": 10, "of": 10, "note": "All major externalities are externalized; bonding is orders of magnitude short."},
    "eroi_integrability":                 {"score": 10, "of": 10, "note": "Perpetual-treatment term makes site-level EROI non-convergent."},
    "ore_grade_headwind":                 {"score": 9, "of": 10, "note": "Efficiency gains already being outrun by grade decline (Chile data)."},
    "jevons_coupling":                    {"score": 9, "of": 10, "note": "AI/automation efficiency gains correlate with INCREASED absolute throughput."},
    "entropy_export_timescale_mismatch":  {"score": 10, "of": 10, "note": "30 yr benefit / 10,000 yr liability."},
    "metric_to_harm_coupling":            {"score": 10, "of": 10, "note": "Reported metrics (intensity, Scope 1/2 CO2) uncoupled from harm function (watershed flux, treaty rights)."},
    "supply_chain_alignment":             {"score": 9, "of": 10, "note": "National-security framing depends on end use the company has not confirmed (and that public statements contradict)."},
    "institutional_memory_decay":         {"score": 8, "of": 10, "note": "Post-closure governance requires institutions more durable than any that exist."},
    "failure_base_rate":                  {"score": 9, "of": 10, "note": "US sulfide-ore Cu mines: ~93% failure rate in watershed protection."},
    }

    # ==============================================================================

    # TOP-LEVEL REPORT

    # ==============================================================================

    import json

def emit_thermo_audit():
    return {
    "audit_id": "BWCA-TwinMetals-ThermoEROI-2026-04-16",
    "section_A_mitigation_dependencies": [m.__dict__ for m in MITIGATIONS],
    "section_B_externality_ledger":       [e.__dict__ for e in EXTERNALITIES],
    "section_C_eroi_stack":               [c.__dict__ for c in EROI_STACK],
    "section_C_headline":                  EROI_HEADLINE,
    "section_D_flow_diagram":              FLOW_DIAGRAM,
    "section_E_failure_thermodynamics":    FAILURE_THERMO,
    "section_F_falsifiable_thermo_claims":[t.__dict__ for t in THERMO_CLAIMS],
    "scoring":                             THERMO_SCORING,
    "one_line_finding": (
    "The mitigation stack is a set of input-side efficiency improvements "
    "loosely coupled or inversely coupled to the output-side harm function; "
    "the EROI does not integrate to a finite positive number once the "
    "perpetual-treatment tail is included; and the entropy export has no "
    "place to go except the watershed, the treaty rights, and the "
    "precedent-vulnerable federal public-lands system."
    ),
    }

if __name__ == "__main__":
    print(json.dumps(emit_thermo_audit(), indent=2, default=str))
