# “””
BWCA / Twin Metals / Antofagasta Audit

CC0. Stdlib only. No external dependencies.

Structure:
LAYER 0: Legislative fact (what happened, 2026-04-16)
LAYER 1: Physical / geochemical constraints (watershed thermodynamics)
LAYER 2: Parent-company track record (ground-truth empirical data)
LAYER 3: “AI-optimized responsible mining” claim audit
LAYER 4: Bottleneck / leverage map (where the energy actually flows)
LAYER 5: Falsifiable claims registry (TC-1 through TC-10)

Purpose:
Translate the PR framing into constraint equations and check closure.
Treat every marketing claim as a hypothesis with measurable failure modes.
“””

from dataclasses import dataclass, field
from typing import Optional
import json

# ==============================================================================

# LAYER 0 — LEGISLATIVE FACT

# ==============================================================================

LAYER_0 = {
“event”: “Senate vote on H.J.Res. 140 (Congressional Review Act)”,
“date”: “2026-04-16”,
“tally”: “50-49”,
“effect”: “Revokes Public Land Order 7917 (2023 mineral withdrawal)”,
“area_affected_acres”: 225_378,
“location”: “Rainy River Watershed, Superior National Forest, upstream of BWCAW”,
“next_step”: “To President Trump’s desk for signature”,
“mechanism_novelty”: (
“First time a mineral withdrawal has been killed by the CRA. “
“CRA historically used for administrative rules, not public land orders. “
“Bypasses the 60-vote Senate threshold and the FLPMA process for “
“amending/rescinding mineral withdrawals — no environmental analysis, “
“no public comment.”
),
“underlying_science_being_bypassed”: {
“agency”: “U.S. Forest Service”,
“year”: 2022,
“public_comments”: 675_000,
“comments_favoring_protection”: “over 95%”,
“conclusion”: (
“Sulfide-ore copper mining near the Boundary Waters would cause “
“IRREVERSIBLE harm to the ecosystem and downstream Voyageurs “
“National Park.”
),
},
}

# ==============================================================================

# LAYER 1 — PHYSICAL / GEOCHEMICAL CONSTRAINTS

# ==============================================================================

# These are the physics the PR framing has to survive. None of them are opinions.

@dataclass
class PhysicalConstraint:
name: str
equation_or_rule: str
ground_truth: str
time_constant: str
reversibility: str

PHYSICS = [
PhysicalConstraint(
name=“Acid generation (pyrite oxidation)”,
equation_or_rule=(
“4 FeS2 + 15 O2 + 14 H2O -> 4 Fe(OH)3 + 8 H2SO4\n”
“Rate accelerated 10^2 to 10^6 by Acidithiobacillus ferrooxidans.”
),
ground_truth=(
“Reaction runs whenever sulfide ore contacts O2 + H2O. “
“There is no engineering control that removes this coupling “
“from a wet, oxygenated environment — only containment, “
“which must hold forever.”
),
time_constant=“Onset: 2-5 yr to decades. Duration: decades to centuries.”,
reversibility=“NONE once established. No large hardrock surface mine has demonstrated that AMD can be stopped after onset.”,
),

```
PhysicalConstraint(
    name="Watershed hydrology (BWCA specific)",
    equation_or_rule=(
        "Lakes + wetlands ~20% of surface area. "
        "Mine site is UPSTREAM (Birch Lake / Kawishiwi / Rainy) "
        "with continuous hydraulic connection to 1,000+ lakes "
        "through the Wilderness and downstream to Voyageurs NP "
        "and Quetico Provincial Park (Canada)."
    ),
    ground_truth=(
        "Every failure mode is GRAVITY-FED into the wilderness. "
        "Containment failures cannot be intercepted downstream "
        "because there is no downstream infrastructure — it is wilderness."
    ),
    time_constant="Advection: days to years. Contamination residence: centuries.",
    reversibility="None at the watershed scale.",
),

PhysicalConstraint(
    name="Empirical base rate (14-mine US study, Kuipers 2012)",
    equation_or_rule="P(water quality failure | US sulfide-ore copper mine) = 13/14 ≈ 0.93",
    ground_truth=(
        "Former USFS Chief Tom Tidwell cited this study: of 14 US "
        "sulfide-ore copper mines, 13 failed to control pollution "
        "into surrounding waters. Smith's Senate floor statement "
        "('100% of the instances have always caused pollution') "
        "is within the error bar of this base rate."
    ),
    time_constant="Observed over operating lifetime + post-closure monitoring.",
    reversibility="Failures have required Superfund perpetual treatment.",
),

PhysicalConstraint(
    name="Dry-stack tailings failure rate (the company's offered 'innovation')",
    equation_or_rule=(
        "Twin Metals' proposed mitigation = dry-stack tailings. "
        "MN DNR rejected this technique for PolyMet in 2018 as "
        "unsuitable for wet climates. "
        "Two US mines cited as dry-stack successes, plus three in "
        "Alaska, recorded >8,000 spills combined per April 2022 report."
    ),
    ground_truth=(
        "The engineering control being offered has already failed "
        "under empirical test in wetter-equivalent conditions."
    ),
    time_constant="Spills occur throughout operating life.",
    reversibility="Partial at best; contamination from spills persists.",
),

PhysicalConstraint(
    name="Closed-loop water claim",
    equation_or_rule=(
        "Company claim: 'closed-loop water supply and recycling.' "
        "Physical reality: no mine in a 20%-surface-water, precipitation-"
        "positive boreal watershed has ever achieved a true closed loop. "
        "Infiltration + snowmelt + groundwater intrusion all inject "
        "uncontrolled water into the system."
    ),
    ground_truth=(
        "A closed loop in this hydrogeology requires impermeable "
        "boundaries at every interface — which don't exist in "
        "glacially-fractured bedrock with a high water table."
    ),
    time_constant="Water balance deviation observable within first wet season.",
    reversibility="Once loop is breached, contaminated water enters watershed.",
),
```

]

# ==============================================================================

# LAYER 2 — PARENT COMPANY TRACK RECORD (ground-truth empirical data)

# ==============================================================================

# Antofagasta plc / Antofagasta Minerals / Minera Los Pelambres.

# This is the calibration data for “will they comply?”

ANTOFAGASTA_RECORD = [
{
“year”: 2013,
“event”: “Chilean Supreme Court ruling”,
“finding”: “El Mauro tailings dam is a ‘danger to human life’; company held culpable for any loss of life in a collapse.”,
“source”: “Chilean Supreme Court, per London Mining Network”,
},
{
“year”: 2014,
“event”: “Chilean Supreme Court orders water restoration”,
“finding”: “Supreme Court orders Minera Los Pelambres to restore the free flow of uncontaminated water to the Pupio basin — by demolishing the tailings dam.”,
“source”: “Chilean Supreme Court”,
},
{
“year”: 2014,
“event”: “Environmental fine”,
“finding”: “Superintendencia del Medio Ambiente fines Minera Los Pelambres US$2.3M for damage to archaeological heritage.”,
“source”: “SMA Chile”,
},
{
“year”: 2022,
“event”: “Concentrate pipeline leak (Los Pelambres)”,
“finding”: “Copper concentrate pipeline ruptures and contaminates agricultural land.”,
“source”: “Mongabay 2024, Mining Weekly 2022”,
},
{
“year”: 2022,
“event”: “SMA sanction process opened”,
“finding”: “1 minor + 2 major charges for improper use and deficiencies in emergency tailings pools and tailings management.”,
“source”: “SMA Chile, via Mining Weekly”,
},
{
“year”: 2024,
“event”: “Illegal water extraction finding”,
“finding”: “Los Pelambres illegally extracted 990,423 m^3 of water from 17 wells in a region officially designated as water-scarce.”,
“source”: “Mongabay 2024”,
},
{
“year”: 2024,
“event”: “SLAPP-style litigation”,
“finding”: “Mining company sues 32 local residents of the affected community.”,
“source”: “Mongabay 2024”,
},
{
“year”: 2026,
“event”: “Chilean regulator fine (~US$775K)”,
“finding”: “Failure to follow water management and monitoring protocols.”,
“source”: “Per user’s original research brief”,
},
]

# Record pattern:

# - Courts rule against the company: >= 2 Chilean Supreme Court losses.

# - Company response to court orders: non-compliance with demolition order;

# dam still stands.

# - Water: illegal extraction in a water-scarce region; contamination

# of downstream communities.

# - Community response: SLAPP lawsuits against residents who organize.

# - Regulator response: repeated, escalating sanctions; company continues operating.

# 

# This is not a “legacy” problem from a prior owner.

# This is the operating behavior of the current parent during its current tenure.

# ==============================================================================

# LAYER 3 — “AI-OPTIMIZED RESPONSIBLE MINING” CLAIM AUDIT

# ==============================================================================

# The user flagged this correctly as the key manipulation surface.

AI_CLAIMS = [
{
“claim”: “AI (SIRO platform, MIT partnership) improves copper recovery and reduces acid consumption.”,
“what_it_optimizes”: “Recovery % per ton of ore processed. Reagent cost per ton.”,
“what_it_does_NOT_optimize”: [
“Total sulfide surface area exposed to O2 + H2O”,
“Total tailings volume generated”,
“Watershed-scale heavy metal flux”,
“Multi-century post-closure water treatment burden”,
“Probability of containment failure under seismic / flood / freeze-thaw loading”,
“Downstream ecosystem, cultural, and treaty impacts”,
],
“why_this_is_a_trap”: (
“A linear efficiency metric (recovery per ton) IMPROVES when you “
“process MORE ore. Processing more ore increases every term in “
“the environmental cost function. The AI is optimizing the “
“numerator of a ratio whose denominator is the thing causing the harm.”
),
},
{
“claim”: “Autonomous haul truck fleet (Centinela) reduces human exposure to hazards and runs 24/7.”,
“what_it_optimizes”: “Uptime, tons moved per day, labor cost per ton.”,
“what_it_does_NOT_optimize”: [
“Aggregate material moved (it INCREASES it)”,
“Energy throughput”,
“Tailings generation rate”,
“Local community exposure (community is downstream, not in the truck)”,
],
“why_this_is_a_trap”: (
“Worker safety framing conceals that 24/7 operation accelerates “
“every downstream harm pathway. The bottleneck being removed “
“is a labor constraint, not a physical or ecological constraint.”
),
},
{
“claim”: “$4.4B expansion at Nueva Centinela powered by renewable energy.”,
“what_it_optimizes”: “Scope 1/2 CO2 per ton copper. Reportable ESG metric.”,
“what_it_does_NOT_optimize”: [
“Total extraction volume (explicit goal: +30% production)”,
“Total tailings produced”,
“Total water consumption”,
“Acid generation potential”,
],
“why_this_is_a_trap”: (
“‘Renewable-powered mine’ decouples the energy metric from the “
“material-flow metric and reports only the former. The physical “
“harms at Boundary Waters scale are material-flow harms, not “
“energy-mix harms. Swapping the fuel of a bulldozer does not “
“change what the bulldozer does.”
),
},
]

# Generalization:

# Every “AI / automation / innovation” claim in the press materials is an

# EFFICIENCY claim (output per input). None of them are SCALE claims

# (total flux through the watershed). The efficiency metrics are not

# coupled to the harm function. They are orthogonal.

# ==============================================================================

# LAYER 4 — ENERGY FLOW / BOTTLENECK / LEVERAGE MAP

# ==============================================================================

# System shape. This is where the whole thing actually lives.

FLOW_MAP = “””
┌─────────────────────────────┐
│  Chilean parent: Antofagasta│
│  capital + political access │
└──────────────┬──────────────┘
│ wholly-owns
▼
┌─────────────────────────────┐
│  Twin Metals Minnesota LLC  │
│  small Ely, MN staff        │
└──────────────┬──────────────┘
│
┌────────────────────────────────────┼────────────────────────────────────┐
│                                    │                                    │
▼                                    ▼                                    ▼
┌───────────────┐                 ┌───────────────────┐                 ┌───────────────────┐
│ LEGAL LEVER   │                 │ PHYSICAL LEVER    │                 │ NARRATIVE LEVER   │
│ CRA bypass    │                 │ Mine → watershed  │                 │ “Critical minerals│
│ of FLPMA +    │                 │ sulfide → acid →  │                 │  for EVs / China  │
│ public process│                 │ heavy metals      │                 │  / national def.” │
└───────┬───────┘                 └─────────┬─────────┘                 └─────────┬─────────┘
│                                   │                                     │
│                                   ▼                                     │
│                         ┌───────────────────┐                           │
│                         │ Downstream sink:  │                           │
│                         │ BWCAW → Voyageurs │                           │
│                         │ → Quetico (CA)    │                           │
│                         │ Wild rice, treaty │                           │
│                         │ rights, 17K jobs  │                           │
│                         │ $1B+ outdoor econ │                           │
│                         └───────────────────┘                           │
│                                                                         │
└─────────────────────────┐                   ┌───────────────────────────┘
▼                   ▼
┌──────────────────────────────────┐
│  BOTTLENECK (real one):          │
│  Federal mineral leases must be  │
│  reinstated + state permits +    │
│  tribal treaty challenges +      │
│  copper price cycle              │
└──────────────────────────────────┘

Leverage points for defenders (ordered by physical irreversibility they protect):

(1) Tribal treaty challenges (White Earth, Fond du Lac, Bois Forte, Grand Portage).
Treaty rights are federal law and cannot be overridden by a CRA vote.
This is the single highest-leverage node because it sits upstream of
every permit.

(2) State-level permits (MN DNR). The DNR already rejected dry-stack
storage on state land in Feb 2022 citing ‘unacceptable financial
risk to the State.’ State agencies have not been CRA-bypassed.

(3) Lease reinstatement litigation. The 2022 legal opinion invalidating
the leases was reversed by DOI memo in 2025, but that memo is
litigable.

(4) Downstream international treaty (Boundary Waters Treaty of 1909,
US-Canada). Quetico sits downstream. Transboundary pollution is
a diplomatic-legal vector.

(5) Copper price cycle. Low prices killed the INCO proposal in the
1970s. Market conditions remain an external filter.

Bottleneck for the mining side (what they need to get past):
Every one of the above, sequentially.

Bottleneck for the watershed (what one failure costs):
A single containment breach is multi-century.
Base rate of containment breach in this mine class: ~93%.
“””

# ==============================================================================

# LAYER 5 — FALSIFIABLE CLAIMS REGISTRY

# ==============================================================================

# Each claim can be checked against future evidence. No opinions — only

# conditions under which each claim would be falsified.

@dataclass
class FalsifiableClaim:
id: str
claim: str
falsifier: str
current_evidence_state: str

CLAIMS = [
FalsifiableClaim(
id=“TC-1”,
claim=“Sulfide-ore copper mining in a wet watershed produces AMD.”,
falsifier=“Demonstrate an operating sulfide-ore Cu mine in a comparable wet climate that has zero measurable AMD signal for >= 50 yr post-opening.”,
current_evidence_state=“UNFALSIFIED. 13/14 US sulfide-ore Cu mines have documented AMD failures (Kuipers 2012).”,
),
FalsifiableClaim(
id=“TC-2”,
claim=“Antofagasta’s compliance pattern at Los Pelambres predicts compliance at Twin Metals MN.”,
falsifier=“Show that Antofagasta has, in the past decade, voluntarily complied with a Chilean Supreme Court order to dismantle a tailings facility.”,
current_evidence_state=“UNFALSIFIED AGAINST COMPANY. 2014 Supreme Court demolition order not complied with; dam remains; 2022 and 2026 sanctions continued.”,
),
FalsifiableClaim(
id=“TC-3”,
claim=“AI/automation reduces total environmental harm from copper mining.”,
falsifier=“Produce a peer-reviewed study showing that an AI-optimized mine reduced ABSOLUTE watershed-scale metal flux (not per-ton efficiency) vs. baseline.”,
current_evidence_state=“UNFALSIFIED IN FAVOR OF CLAIM. All published AI/automation metrics are intensity metrics (per-ton efficiency), not flux metrics.”,
),
FalsifiableClaim(
id=“TC-4”,
claim=”‘Dry-stack tailings’ is a safe mitigation in wet boreal climates.”,
falsifier=“Show a wet-climate dry-stack operation with zero measurable spill/leachate events over operational lifetime.”,
current_evidence_state=“UNFALSIFIED. 5 reference dry-stack mines (2 US lower-48 + 3 AK) combined >8,000 spills per April 2022 report. MN DNR rejected technique for PolyMet in 2018.”,
),
FalsifiableClaim(
id=“TC-5”,
claim=“The CRA vote changed the physical risk profile of the mine.”,
falsifier=“Show that the pyrite oxidation reaction rate depends on which federal statute applies.”,
current_evidence_state=“TRIVIALLY UNFALSIFIABLE. Chemistry is statute-invariant. CRA vote changed access, not risk.”,
),
FalsifiableClaim(
id=“TC-6”,
claim=”‘Closed-loop water’ is achievable in the BWCA watershed.”,
falsifier=“Demonstrate a mine in comparable glacially-fractured boreal bedrock with net-zero water exchange with surrounding groundwater/surface water over full year, including spring snowmelt.”,
current_evidence_state=“UNFALSIFIED. No precedent in published literature.”,
),
FalsifiableClaim(
id=“TC-7”,
claim=”‘Critical minerals for EVs/national defense’ framing requires THIS site.”,
falsifier=“Show that Twin Metals production is non-substitutable — that equivalent ore grades do not exist on lower-risk sites, and that recycling + existing mines cannot meet projected demand in the relevant time window.”,
current_evidence_state=“UNFALSIFIED IN FAVOR OF CLAIM. Argument has not been published with substitution analysis. Company also has explicit plan to ship ore to Chinese smelters per Sen. Smith’s floor statement — directly contradicting national-security framing.”,
),
FalsifiableClaim(
id=“TC-8”,
claim=“17,000 outdoor jobs + $1B+ regional outdoor economy are at acceptable risk.”,
falsifier=“Show a sulfide-ore Cu mine that operated upstream of a wilderness-based tourism economy without measurable tourism-sector decline.”,
current_evidence_state=“UNFALSIFIED IN FAVOR OF CLAIM. No counter-example documented.”,
),
FalsifiableClaim(
id=“TC-9”,
claim=“Tribal treaty rights are adequately protected by the CRA bypass.”,
falsifier=“Show that the 1854 Treaty ceded territory can be commercially exploited without tribal consent.”,
current_evidence_state=“UNFALSIFIED IN FAVOR OF CLAIM. Treaties are federal law; White Earth chairman has already declared intent to contest. Transboundary (Canada) adds Quetico + treaty obligations.”,
),
FalsifiableClaim(
id=“TC-10”,
claim=“The CRA is the appropriate tool for reversing a public land order.”,
falsifier=“Show a prior successful use of CRA against a mineral withdrawal.”,
current_evidence_state=“UNFALSIFIED. Per Earthjustice: this is the FIRST time a mineral withdrawal has been killed by CRA. Sets precedent; every prior public land order since 1996 now theoretically reversible.”,
),
]

# ==============================================================================

# SCORING DIMENSIONS

# ==============================================================================

SCORING = {
“physical_irreversibility”:     {“score”: 10, “of”: 10, “note”: “AMD is permanent at watershed scale.”},
“empirical_base_rate”:          {“score”:  9, “of”: 10, “note”: “13/14 documented failures.”},
“parent_compliance_history”:    {“score”:  9, “of”: 10, “note”: “Court-ordered demolition ignored; ongoing sanctions.”},
“mitigation_technology_validity”:{“score”: 8, “of”: 10, “note”: “Dry-stack fails empirically in wet climates.”},
“ai_claim_coupling_to_harm”:    {“score”: 10, “of”: 10, “note”: “Completely uncoupled. Intensity metrics, not flux metrics.”},
“process_bypass_severity”:      {“score”: 10, “of”: 10, “note”: “First CRA kill of a mineral withdrawal; FLPMA bypassed.”},
“treaty_rights_exposure”:       {“score”:  9, “of”: 10, “note”: “1854 Treaty territory; transboundary treaty with Canada.”},
“economic_substitution_alt”:    {“score”:  7, “of”: 10, “note”: “Outdoor economy (17K jobs, $1B+) is the recurring revenue.”},
“national_security_framing”:    {“score”:  8, “of”: 10, “note”: “Ore destined for Chinese smelters contradicts framing.”},
“public_consent_signal”:        {“score”:  9, “of”: 10, “note”: “95%+ of 675K comments favored protection. 70% of MN supports ban.”},
“precedent_spillover”:          {“score”: 10, “of”: 10, “note”: “Every post-1996 public land order now exposed to CRA.”},
}

# ==============================================================================

# TOP-LEVEL SUMMARY FUNCTION

# ==============================================================================

def emit_audit_report():
report = {
“audit_id”: “BWCA-TwinMetals-Antofagasta-2026-04-16”,
“layer_0_legislative_fact”: LAYER_0,
“layer_1_physics”: [c.**dict** for c in PHYSICS],
“layer_2_company_record”: ANTOFAGASTA_RECORD,
“layer_3_ai_claim_audit”: AI_CLAIMS,
“layer_4_flow_map”: FLOW_MAP,
“layer_5_falsifiable_claims”: [c.**dict** for c in CLAIMS],
“scoring_dimensions”: SCORING,
“headline_finding”: (
“The CRA vote changes the LEGAL access pathway to the site. “
“It does not change any of the physical, geochemical, or “
“corporate-behavioral constraints. Every ‘innovation’ and “
“‘responsible mining’ claim in the PR stack optimizes an “
“intensity metric (output per ton) that is orthogonal to — “
“or positively correlated with — the harm function “
“(watershed-scale metal flux over multi-century timescales). “
“The mine is, in physical terms, the same mine it was before “
“the vote. The watershed is the same watershed. The base rate “
“of containment failure for this mine class in the US is ~93%. “
“The operator’s parent has a documented pattern of ignoring “
“Supreme Court remediation orders in its home jurisdiction. “
“The leverage for defenders now sits in (1) tribal treaty “
“litigation, (2) state-level permits, (3) international “
“transboundary pollution treaty, and (4) copper market cycle.”
),
}
return report

if **name** == “**main**”:
print(json.dumps(emit_audit_report(), indent=2, default=str))
