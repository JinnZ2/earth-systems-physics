# “””
BWCA / Twin Metals — Hidden Dependency Layer Audit

CC0. Stdlib only.

Third audit in the series:
bwca_audit.py          → physics + corporate record + claim verification
bwca_thermo_audit.py   → mitigation dependencies + externalities + EROI
bwca_hidden_deps.py    → THIS FILE

Purpose:
Walk one layer deeper. Every mitigation technology is itself a product
of a manufacturing chain that has its own energy, chip, water, grid,
and raw-material dependencies — all of which are in shortage right now,
competing with every other large-load claimant on the same grid
(data centers, EVs, HVAC expansion, electrified manufacturing).

```
Ground truth (April 2026):
    * US data centers: 75.8 GW forecast 2026 → 134.4 GW 2030
    * 50% of global data center projects facing delays from power limits
      and grid equipment shortages
    * PJM projects 6 GW short of reliability requirements in 2027
    * Pad-mount 3-phase transformer lead times: 24-48 months
    * Large power transformer lead times: ~2+ years since 2023
    * Transformer prices up 4-6x since 2022 (Wood Mackenzie)
    * Residential electricity prices up ~33% over 5 yr, 1.5x faster than CPI
    * Wholesale prices +267% in data-center-heavy areas (Bloomberg)

The empirical question is NOT "will there be shortages" — shortages
are already here. The empirical question is: WHO LOSES POWER FIRST
when the grid gets squeezed? The answer has a name: least-powerful
customer. Not the mine. Not the data center. Not the military base.
The homeowner, the renter, the small municipality, the school, the
hospital, the rural co-op.
```

Structure:
SECTION G: Scarce-resource contention map (what’s already short)
SECTION H: Manufacturing-chain backfill (what each mitigation needs
that has to be made by someone else under shortage)
SECTION I: Power triage ordering (who loses first in a squeeze)
SECTION J: Ratepayer externality mechanism (how the bill shifts)
SECTION K: Failure cascades across grid events
SECTION L: Falsifiable hidden-dependency claims (TH-1 through TH-10)
“””

from dataclasses import dataclass, field
from typing import Optional
import json

# ==============================================================================

# SECTION G — SCARCE-RESOURCE CONTENTION MAP

# ==============================================================================

# As of April 2026. Sources inline in notes.

@dataclass
class ScarceResource:
resource: str
status_2026: str
lead_time: str
price_trajectory: str
other_claimants: list        # who else wants this resource
chain_position: str          # where it sits in mitigation chain

SCARCE = [
ScarceResource(
resource=“Pad-mount 3-phase distribution transformers”,
status_2026=“Shortage worsening. Wood Mackenzie forecast.”,
lead_time=“24-48 months (was 6-12 months pre-2020)”,
price_trajectory=“4-6x pre-2022 prices; +60-80% in last 18 months”,
other_claimants=[
“Hyperscale data centers (AI buildout)”,
“EV charger networks”,
“New manufacturing facilities (CHIPS Act, IRA)”,
“Residential service replacement (50%+ of in-service “
“distribution transformers are >30 yr old, reaching EoL)”,
“Solar farm interconnections”,
],
chain_position=“Required for grid connection of any new mine load AND for any residential replacement.”,
),

```
ScarceResource(
    resource="Large power transformers (GSU, substation)",
    status_2026="30% market deficit (power), 47% deficit (GSUs) per Wood Mackenzie",
    lead_time="100+ weeks (~2 yr) since 2023",
    price_trajectory="Up to 95% increase per Electrical Trader analysis",
    other_claimants=[
        "Every utility rebuilding transmission for data centers",
        "Solar/wind interconnection at substation scale",
        "Replacement of aging transformers nationwide",
    ],
    chain_position="Required for mine's grid interconnection at MV/HV level.",
),

ScarceResource(
    resource="Grid-interactive battery storage",
    status_2026="Available but competing for same manufacturing capacity as EVs and portable electronics",
    lead_time="18-36 months for utility-scale",
    price_trajectory="Declined historically, now re-rising under demand pressure",
    other_claimants=[
        "Data centers seeking firming capacity",
        "EV manufacturers",
        "Residential + commercial behind-the-meter storage",
        "Utility peaking applications",
    ],
    chain_position="Required for any 'renewable-powered' claim at mine site; required for municipal/residential resilience.",
),

ScarceResource(
    resource="Water (cooling + process + closed-loop makeup)",
    status_2026="Regional shortages; MN generally wetter but Duluth Complex wells are bedrock-limited",
    lead_time="N/A — either present or absent",
    price_trajectory="Rising where metered; contested where allocated by permit",
    other_claimants=[
        "Municipal drinking water systems",
        "Agricultural irrigation (soybean, corn in southern MN)",
        "Existing taconite operations on the Iron Range",
        "Data center liquid cooling",
        "Fish and wildlife (senior water rights in tribal treaty territory)",
    ],
    chain_position="Required for ore processing, dust suppression, water treatment plant operation.",
),

ScarceResource(
    resource="Semiconductor chips (industrial-grade controllers, sensors)",
    status_2026="Memory chip shortage (HBM) driven by AI data centers rippling into industrial-grade",
    lead_time="Variable; industrial controllers 12-26 weeks normal, now extended",
    price_trajectory="Industrial chip prices up alongside consumer prices",
    other_claimants=[
        "Data center AI accelerators (dominant demand)",
        "Automotive (EV + ADAS)",
        "Defense",
        "Consumer electronics",
        "Grid monitoring equipment itself",
    ],
    chain_position="Required for AI optimization, autonomous fleet, sensor networks, dry-stack monitoring, water treatment controllers.",
),

ScarceResource(
    resource="Skilled electrical engineering / grid workforce",
    status_2026="Documented shortage in every ISO/RTO; retirement wave ongoing",
    lead_time="Training pipeline ~4-10 yr",
    price_trajectory="Wages rising rapidly",
    other_claimants=[
        "Utilities themselves",
        "Data center build-out",
        "Defense industrial base",
        "Renewable project development",
    ],
    chain_position="Required for mine electrification, grid interconnection study, ongoing O&M.",
),

ScarceResource(
    resource="Grid-scale generation capacity (firm, dispatchable)",
    status_2026="PJM short ~6 GW reliability in 2027; Morgan Stanley forecasts 49 GW US shortfall by 2028",
    lead_time="New CCGT: 3-5 yr. New nuclear: 8-15 yr. Reactor restart: 2-4 yr.",
    price_trajectory="Wholesale spot prices up ~267% in data-center-heavy regions",
    other_claimants=[
        "Data centers (dominant new load)",
        "Reshored manufacturing",
        "Electrified heating loads (heat pumps)",
        "EV charging",
        "Every existing customer",
    ],
    chain_position="Required to supply mine's 24/7 load and every mitigation system's continuous power need.",
),

ScarceResource(
    resource="Interconnection queue position (MISO — serves Minnesota)",
    status_2026="Median interconnection time 54 months in 2026 (was 22 months in 2000)",
    lead_time="4-5 years before a new large load gets energized",
    price_trajectory="Queue study costs rising; reform ongoing but incomplete",
    other_claimants=[
        "Data center developers",
        "Large manufacturing",
        "Solar/wind generators",
    ],
    chain_position="Required just to START getting power to the mine site.",
),
```

]

# ==============================================================================

# SECTION H — MANUFACTURING-CHAIN BACKFILL

# ==============================================================================

# Each mitigation technology has to be MANUFACTURED. Tracing what that takes.

@dataclass
class ManufacturingChain:
mitigation: str
direct_manufacturing_inputs: list
upstream_scarcities_tapped: list
grid_load_to_manufacture: str
comparison: str              # other claimants on same inputs

MFG_CHAINS = [
ManufacturingChain(
mitigation=“Dry-stack tailings filter presses”,
direct_manufacturing_inputs=[
“Steel (carbon + stainless)”,
“Hydraulic systems (precision machined components)”,
“High-pressure pumps (copper windings, rare-earth magnets)”,
“Filter media (synthetic polymer cloth — petrochemical feedstock)”,
“Programmable controllers (industrial chips)”,
“Electric drive motors (copper, steel, rare earths)”,
],
upstream_scarcities_tapped=[
“Copper (recursive — mining more copper to mitigate mining for copper)”,
“Industrial-grade chips”,
“Rare earth magnets (NdFeB)”,
“Skilled welding / fitting labor”,
],
grid_load_to_manufacture=“Energy-intensive: steel mills, motor winding, plastics extrusion. On the order of hundreds of MWh per large filter press.”,
comparison=“Every filter press built for this mine is not built for municipal water treatment, food processing, or pharma.”,
),

```
ManufacturingChain(
    mitigation="Impermeable HDPE liners for tailings storage",
    direct_manufacturing_inputs=[
        "HDPE resin (petrochemical; natural gas feedstock)",
        "Geotextile layers (polypropylene)",
        "Welding equipment for seam sealing",
    ],
    upstream_scarcities_tapped=[
        "Natural gas (competing with heating, electricity, data center backup)",
        "Petrochemical cracker capacity",
        "Installation crews (same labor pool as pipeline work, landfill capping)",
    ],
    grid_load_to_manufacture="Plastics manufacturing ~10-30 GJ/tonne.",
    comparison="Liner material is finite service life (20-50 yr under ideal conditions vs. perpetuity required).",
),

ManufacturingChain(
    mitigation="Water treatment plant (membrane RO + ion exchange)",
    direct_manufacturing_inputs=[
        "RO membranes (thin-film composite polyamide)",
        "Ion exchange resins",
        "High-pressure pumps (similar copper/RE dependency)",
        "Stainless steel vessels",
        "Chemical feedstock (lime, caustic, sulfuric acid — recursive)",
        "Instrumentation (sensors, chips, controllers)",
    ],
    upstream_scarcities_tapped=[
        "Advanced polymer manufacturing",
        "Specialty chemicals",
        "Skilled operators",
    ],
    grid_load_to_manufacture="Continuous electrical draw during operation (2-6 kWh per m3 treated water).",
    comparison="Every RO system here is one fewer for desalination, municipal potable, or industrial reuse.",
),

ManufacturingChain(
    mitigation="AI optimization infrastructure (SIRO / sensor network)",
    direct_manufacturing_inputs=[
        "GPUs / AI accelerators (cutting-edge chips)",
        "Industrial sensors (XRF, hyperspectral — specialty semiconductors)",
        "Networking equipment (copper, fiber, chips)",
        "Edge compute nodes",
        "Cloud/data center backend (!)",
    ],
    upstream_scarcities_tapped=[
        "AI-class chips (severe shortage, 2026 HBM crunch)",
        "Grid capacity for compute (compete directly with data centers)",
        "Water for data center cooling (same as below)",
    ],
    grid_load_to_manufacture="AI buildout is THE primary grid-stress cause in 2026. Every compute cycle spent optimizing mine ops is one not available for medical imaging, weather prediction, grid management.",
    comparison="Antofagasta MIT/SIRO partnership presupposes access to AI compute — the scarcest resource on the grid right now.",
),

ManufacturingChain(
    mitigation="Autonomous haul truck fleet",
    direct_manufacturing_inputs=[
        "Mining trucks (hundreds of tonnes steel each; ~$5-7M per unit)",
        "LIDAR units (specialty photonics)",
        "Radar, cameras, GPS modules (chips)",
        "Tires (specialty rubber, steel cord, carbon black)",
        "Batteries (lithium, copper, nickel, cobalt) if electric variant",
        "Compute stack per vehicle (~$50-200K chip cost)",
    ],
    upstream_scarcities_tapped=[
        "Giant tire supply chain (global bottleneck)",
        "Specialty sensors",
        "Diesel supply (still primary for most fleets)",
    ],
    grid_load_to_manufacture="Each truck ~200-500 MWh of embodied energy to manufacture.",
    comparison="One haul truck's sensor stack could instrument a small city's grid monitoring.",
),

ManufacturingChain(
    mitigation="Renewable generation + storage for mine site",
    direct_manufacturing_inputs=[
        "Solar panels (silicon wafers, silver, aluminum)",
        "Wind turbines (rare earths, steel, copper, composites)",
        "Utility-scale batteries (lithium, cobalt, nickel, copper)",
        "Inverters (silicon carbide power electronics)",
        "Collection system (miles of copper cable and transformers !)",
    ],
    upstream_scarcities_tapped=[
        "Transformer shortage (SAME queue as residential/municipal)",
        "Copper (recursive)",
        "Battery supply chain (competing with EVs)",
        "Skilled installation labor",
    ],
    grid_load_to_manufacture="Manufacturing 100 MW of solar ~150-200 GWh embodied energy. Wind higher.",
    comparison="Every MW of solar capacity committed to a mine is one not available for community microgrids, school electrification, residential rooftop programs.",
),
```

]

# ==============================================================================

# SECTION I — POWER TRIAGE ORDERING

# ==============================================================================

# Empirical fact: in a grid squeeze, someone loses first.

# Rank order from “loses first” to “loses last”.

# POWER_TRIAGE = “””
EMPIRICAL POWER TRIAGE ORDER (WHO LOSES FIRST IN A GRID SQUEEZE)

Rank 1 — FIRST to lose (most exposed):
• Small rural municipalities on co-op distribution
• Renters in older buildings (pre-paid meters, shutoffs)
• Mobile home parks
• Households behind unmaintained secondary-side transformers
• Small businesses without demand-response contracts
• Seasonal / temporary workers in rural housing

Rank 2:
• Suburban residential
• Small commercial customers
• Schools and libraries
• Small clinics / rural hospitals without tier-1 reliability contracts

Rank 3:
• Larger commercial / industrial (contractual tariff protections)
• Municipal water/sewer systems (sometimes Rank 1 in reality due to
aging infrastructure)
• Medium industrial customers

Rank 4:
• Large industrial customers with firm supply contracts
• Hospitals and 911/emergency dispatch
• Military bases

Rank 5 — LAST to lose:
• Hyperscale data centers with direct-contract 15-yr power purchase
agreements, dedicated substations, and behind-the-meter generation
• Behind-the-meter generation customers (Oracle-style Stargate model)
• Defense nuclear / national-security designated loads
• Large extractive operations with dedicated substations and long-term
PPAs — THIS IS WHERE TWIN METALS SITS

Mechanism:
The mine will be designed with its own dedicated substation. The
15-yr PPA or equivalent contract will put it near the top of the
reliability stack. When grid stress hits (and it will — PJM is
already projecting 6 GW short for 2027), load shedding protocols
will not start at the mine. They start at distribution feeders
serving residential and small commercial.

```
This is not a hypothetical. It is how firm-contract reliability
is ALREADY being allocated in 2026. Xcel's new data center tariff
in Minnesota explicitly structures contracts so that large new
customers bear their own costs but also get firm service. The
residual risk — blackouts, brownouts, voltage sags — falls on
everyone else on the same feeder.
```

Key empirical data point:
Residential electricity prices rose ~33% over past 5 years, 1.5x
faster than CPI. Wholesale prices in data-center-heavy areas rose
267%. Grid costs are being passed to residential ratepayers.
The mine will tap the same cost-socialization mechanism.
“””

# ==============================================================================

# SECTION J — RATEPAYER EXTERNALITY MECHANISM

# ==============================================================================

# How, exactly, does the community end up paying?

# RATEPAYER_MECHANISM = “””
HOW THE COST ACTUALLY SHIFTS TO THE COMMUNITY

(1) TRANSMISSION UPGRADES
A new 50-200 MW mine load requires:
• New substation (dedicated)
• Transmission-line reconductoring or new line build
• System protection upgrades (breakers, relays, SCADA)
• Possibly new generation or firming capacity
In MISO (the RTO serving northern MN), network upgrade costs
are allocated partly to the requesting customer, partly socialized.
Transmission-related charges get rolled into every ratepayer’s bill
through the utility’s revenue requirement.

(2) COST-OF-SERVICE RATEMAKING
Utilities earn a return on rate base. A mine requires more rate
base (substations, transformers, lines). The utility earns a
return on that capital — paid for by ALL customers in the service
territory through rates. Industrial tariffs subsidize residential
and vice versa depending on structure; the net effect in rural
and semi-rural territories is that residential customers
cross-subsidize industrial loads.

(3) CAPACITY MARKET EFFECTS
In constrained capacity markets, adding a large new load raises
the clearing price for capacity. Every other customer in the
capacity zone pays more per kW of capacity obligation.

(4) WHOLESALE ENERGY PRICE EFFECTS
A 24/7 ~50 MW mine load will push up spot market prices in northern
MN / MISO North. Bloomberg documents wholesale prices up 267% in
data-center-heavy regions. The same mechanism applies.

(5) TRANSFORMER SUPPLY DIVERSION
A single mine substation might need 3-8 large transformers plus
distribution equipment. With 24-48 month lead times and 30-47%
market deficits, a mine order DISPLACES orders from:
• Residential replacement programs
• Municipal upgrades
• School / hospital expansions
• Renewable interconnection
The residential customer waiting for a new service after a storm
waits longer. The school waiting to add a wing waits longer. The
co-op waiting to replace a 40-yr-old transformer waits longer.
This is a REAL resource allocation, not a hypothetical.

(6) WATER RIGHTS & PERMITTING LOAD
Mine water appropriation permits tie up state agency capacity that
would otherwise process municipal, agricultural, residential water
permit requests. This is an administrative externality.

(7) POST-CLOSURE SHIFT
When the mine closes, the load goes away but the water treatment
stays. Treatment electricity use continues indefinitely. If the
company defaults, the state eats the power bill AND the treatment
bill. Either way, the infrastructure BUILT for the mine (substations,
transformers, transmission) continues to earn a return for the
utility — paid for by ratepayers — but serves no load.

NET EFFECT:
Over the mine’s 30-year operating life, residential and small-
commercial ratepayers in the service territory will pay:
• Higher base rates (more rate base to recover)
• Higher energy prices (wholesale market pressure)
• Higher capacity charges (tightening capacity markets)
• Worse reliability (they sit below the mine in triage)
• Longer equipment replacement waits (supply diversion)
• Higher water rates if watershed treatment costs socialize

```
The mine books its output at market copper prices.
The ratepayers book their share of the grid buildout indefinitely.
Same structure as the post-closure water treatment liability.
```

“””

# ==============================================================================

# SECTION K — FAILURE CASCADES ACROSS GRID EVENTS

# ==============================================================================

# What happens when grid events hit DURING mine operation?

# CASCADE_MODES = “””
FAILURE CASCADES — WHAT A GRID EVENT DOES TO THIS MINE’S MITIGATION STACK

Scenario K-1: Summer peak load-shed event (community tier shed first)
Mine: unaffected (firm contract).
Community: outage.
Mitigations continue running.
Net: mine harm is not paused; community just lost power too.

Scenario K-2: Transmission line failure affecting mine circuit
Mine: loses power.
Water treatment plant: loses pumping.
Dry-stack stack drainage pumps: off.
Tailings pond: overtops if freeboard margin was thin.
Recovery time depends on backup generation (diesel — same supply
chain as every other backup, and diesel itself is constrained in
multi-region events).
Externality: during outage, AMD chemistry does not pause. Sulfide
oxidation continues. Recovery after power restoration includes
flushing accumulated acid load into the watershed.

Scenario K-3: Transformer failure at mine substation (24-48 mo replacement)
Mine operations suspend — but the site’s geochemistry does not
suspend. Without power, water treatment stops. The company must
either truck diesel generators (fuel supply chain) or accept
progressive watershed discharge.

Scenario K-4: Cybersecurity event on mine control system
Increasing probability as mines digitize and connect to cloud
services. All “AI-optimized” operations are attack surfaces.
Possible consequences: misdosed reagents, false-negative monitoring,
uncontrolled discharge during incident response.

Scenario K-5: Chip/electronics supply disruption
Control systems, sensors, PLCs all require industrial-grade chips.
A Taiwan Strait event, major fab outage, or ongoing HBM crunch
rippling into industrial grade extends replacement time for any
failed component. Mitigation systems are no more robust than their
weakest available spare.

Scenario K-6: Extreme weather (ice storm, derecho, polar vortex)
Simultaneously: grid stress, community outages, mine outage,
emergency response diversion. A cascade failure during a weather
event is the highest-probability AMD release scenario.

Scenario K-7: Corporate cash-flow stress event (copper price crash)
Historically, mines under financial stress cut maintenance first.
Monitoring, sampling, and non-critical treatment get deferred.
The company may “care-and-maintenance” the site without formally
closing it — in which case regulatory closure bonds are not yet
triggered, but active environmental management is reduced.
“””

# ==============================================================================

# SECTION L — FALSIFIABLE HIDDEN-DEPENDENCY CLAIMS

# ==============================================================================

@dataclass
class HiddenDepClaim:
id: str
claim: str
falsifier: str
state: str

HIDDEN_CLAIMS = [
HiddenDepClaim(
id=“TH-1”,
claim=“The mitigation stack can be manufactured and delivered in a grid-equipment market with 24-48 month transformer lead times and 30-47% deficits.”,
falsifier=“Show transformer procurement contracts already signed for this specific project with delivery inside standard mine-build timeline.”,
state=“UNFALSIFIED. No such contracts disclosed. In general, Antofagasta would compete with every utility, data center, and manufacturer for the same equipment.”,
),
HiddenDepClaim(
id=“TH-2”,
claim=“The mine’s grid interconnection does not degrade service reliability for residential and small-commercial ratepayers in its feeder zone.”,
falsifier=“Show a comparable 50-200 MW industrial interconnection in MISO where residential reliability and rates were not affected over 5+ years.”,
state=“UNFALSIFIED. Documented pattern in data-center-heavy zones is +267% wholesale price and +33% residential rates over 5 yr. Same mechanism applies.”,
),
HiddenDepClaim(
id=“TH-3”,
claim=“The community will not lose power before the mine in a grid squeeze.”,
falsifier=“Show the tariff document specifying that the mine’s firm-service contract includes load-shed priority BELOW residential service.”,
state=“UNFALSIFIED. Firm industrial contracts with dedicated substations are universally prioritized ABOVE distribution-feeder residential in load-shed protocols.”,
),
HiddenDepClaim(
id=“TH-4”,
claim=“The AI optimization claim is compatible with current AI compute scarcity.”,
falsifier=“Show that Antofagasta’s SIRO deployment has secured dedicated compute capacity independent of the hyperscaler queue.”,
state=“UNFALSIFIED. MIT partnership does not grant compute precedence. In 2026, compute is allocated commercially; mine compute competes with every other workload.”,
),
HiddenDepClaim(
id=“TH-5”,
claim=“Post-closure water treatment electricity needs will be met from the grid at competitive rates in perpetuity.”,
falsifier=“Show a closure plan with funded grid-power commitment for water treatment over 500+ years at any realistic rate projection.”,
state=“UNFALSIFIED. Closure plans extend decades, not centuries. Every post-closure dollar is a future ratepayer / taxpayer externality.”,
),
HiddenDepClaim(
id=“TH-6”,
claim=“Mitigation-system manufacturing does not displace manufacturing of similar equipment for community, municipal, and renewable projects.”,
falsifier=“Show that transformer, motor, membrane, and battery orders for this project were produced from incremental capacity that did not compete with any other queue.”,
state=“UNFALSIFIED. Manufacturing capacity is fungible and in shortage. Every order displaces another.”,
),
HiddenDepClaim(
id=“TH-7”,
claim=“The mine’s water appropriation does not compete with municipal and tribal water rights.”,
falsifier=“Show water permits in the Rainy River watershed where the cumulative appropriation of mining + data center + municipal + agricultural + tribal claims is under the sustainable yield.”,
state=“UNFALSIFIED. The 1854 treaty waters carry senior rights; the hydrogeology of the Duluth Complex is fractured and poorly characterized.”,
),
HiddenDepClaim(
id=“TH-8”,
claim=“The mine’s grid load will be served by NEW generation capacity, not by taking existing generation from other customers.”,
falsifier=“Show a specific generation project that will be built WITH the mine, WHOSE OUTPUT IS ALLOCATED TO THE MINE, and that would not have been built otherwise.”,
state=“UNFALSIFIED. No such project is associated with Twin Metals. MISO capacity is already tightening.”,
),
HiddenDepClaim(
id=“TH-9”,
claim=“A grid-level failure during operations will not translate into a watershed pollution event.”,
falsifier=“Show redundant power paths and backup generation capacity with fuel supply sized to outlast any realistic MISO outage event (polar vortex, derecho, transformer failure).”,
state=“UNFALSIFIED. Backup generation on extractive sites is typically sized for hours-to-days, not weeks.”,
),
HiddenDepClaim(
id=“TH-10”,
claim=“The current grid crisis, documented across bipartisan political commentary, leaves enough capacity for a new 50-200 MW mine load with mitigation overhead without accelerating community harm.”,
falsifier=“Show MISO North reliability forecasts for 2027-2035 that accommodate the mine’s firm load AND maintain current reliability tiers AND do not require new fossil generation AND do not raise residential rates.”,
state=“UNFALSIFIED. Every public forecast shows tightening conditions. NERC warned of elevated summer shortfall risk in 2025, 2026, and onward.”,
),
]

# ==============================================================================

# HIDDEN DEPENDENCY SCORING

# ==============================================================================

HIDDEN_SCORING = {
“grid_equipment_supply_risk”:       {“score”: 10, “of”: 10, “note”: “Transformers at 24-48 mo lead time, 30-47% deficit; mine competes with every other large load.”},
“power_triage_exposure”:            {“score”: 10, “of”: 10, “note”: “Community is structurally below mine in load-shed priority under firm-contract regimes.”},
“ratepayer_cost_shift”:             {“score”: 9, “of”: 10, “note”: “Documented mechanism; same structure as data-center cost socialization.”},
“ai_compute_dependency”:            {“score”: 8, “of”: 10, “note”: “SIRO depends on scarce AI compute; mine has no claim of precedence.”},
“manufacturing_capacity_displacement”:{“score”:9, “of”: 10, “note”: “Every mitigation component displaces community/renewable/EV equivalents.”},
“water_rights_contention”:          {“score”: 9, “of”: 10, “note”: “Treaty waters, fractured bedrock, multiple senior claimants.”},
“cascade_failure_correlation”:      {“score”: 10, “of”: 10, “note”: “Grid events correlate with peak-harm AMD events (weather, outages, cash-flow stress).”},
“post_closure_infrastructure_orphan”:{“score”: 9, “of”: 10, “note”: “Substation built for the mine persists in rate base after closure; ratepayers continue to pay.”},
“chip_and_control_system_risk”:     {“score”: 8, “of”: 10, “note”: “Every mitigation depends on industrial chips; supply is globally contested.”},
“interconnection_queue_opportunity_cost”:{“score”:8, “of”: 10, “note”: “A queue slot used for the mine is one not used for community resilience or distributed renewables.”},
}

# ==============================================================================

# TOP-LEVEL REPORT

# ==============================================================================

def emit_hidden_dep_audit():
return {
“audit_id”: “BWCA-TwinMetals-HiddenDeps-2026-04-16”,
“section_G_scarce_resources”:        [s.**dict** for s in SCARCE],
“section_H_manufacturing_chains”:    [m.**dict** for m in MFG_CHAINS],
“section_I_power_triage”:             POWER_TRIAGE,
“section_J_ratepayer_mechanism”:      RATEPAYER_MECHANISM,
“section_K_failure_cascades”:         CASCADE_MODES,
“section_L_falsifiable_claims”:      [c.**dict** for c in HIDDEN_CLAIMS],
“scoring”:                            HIDDEN_SCORING,
“one_line_finding”: (
“The mitigation stack is ALSO a demand claim on a grid, chip, “
“water, transformer, labor, and AI-compute supply chain that “
“is already failing to meet existing demand — and the mine “
“will sit higher in the reliability and supply queue than “
“the community it operates in. The structural pattern is “
“unambiguous: the community loses power, service reliability, “
“and equipment-replacement capacity before the mine does. “
“This is the same cost-socialization pattern already visible “
“with data centers, scaled to a 30-year extractive operation “
“with permanent watershed liability.”
),
“composite_takeaway”: (
“Across three audits, the mine’s promises collapse on three “
“independent axes: (1) the PHYSICS is against them — sulfide + “
“water + watershed is a one-way entropy export; (2) the “
“THERMODYNAMICS is against them — EROI non-convergent, “
“mitigations coupled to wrong metrics; (3) the SUPPLY CHAIN “
“is against them — every mitigation depends on resources “
“already in shortage and higher-priority-queued by other “
“buyers. The project needs all three axes to hold. None does.”
),
}

if **name** == “**main**”:
print(json.dumps(emit_hidden_dep_audit(), indent=2, default=str))
