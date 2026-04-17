# boundary_waters/extraction_topology.py
# earth-systems-physics
# CC0 — No Rights Reserved
"""
BWCA / Twin Metals — Extraction Topology Audit

Maps the BWCA mine cascade onto the substrate_audit CAUSAL_LOOP
and scores it. The mine is an instance of the general extraction
pattern: value concentrates upward and out of state while costs
distribute downward and persist for centuries.

Value flow:
    ORE leaves Minnesota -> smelter (likely Chile/Asia)
    REVENUE leaves Minnesota -> Antofagasta HQ (Santiago)
    DIVIDENDS leave Minnesota -> global shareholders
    JOBS stay 20 years -> then leave
    COSTS stay forever -> community, watershed, treaty nations, future

This is not speculation. It is the documented corporate structure
of Antofagasta PLC and the physical chemistry of sulfide oxidation.
"""

from dataclasses import dataclass, field
from typing import Any
import json


# ══════════════════════════════════════════════════════════════
# VALUE EXTRACTION LEDGER
# ══════════════════════════════════════════════════════════════

@dataclass
class ValueFlow:
    name: str
    origin: str
    destination: str
    stays_in_state: bool
    duration: str
    magnitude_description: str
    reversible: bool


OUTFLOWS = [
    ValueFlow(
        name="Ore concentrate",
        origin="Duluth Complex, Rainy River watershed",
        destination="Smelter — likely Antofagasta operations in Chile or contracted facility in Asia",
        stays_in_state=False,
        duration="20-year mine life",
        magnitude_description=(
            "7.3M tonnes ore/yr x 20 yr = 146M tonnes. Cu-Ni "
            "concentrate shipped out of state for processing. "
            "Minnesota retains none of the refined metal value."
        ),
        reversible=False,
    ),
    ValueFlow(
        name="Revenue / operating profit",
        origin="Mine gate sales",
        destination="Antofagasta PLC (Santiago, Chile) -> global shareholders",
        stays_in_state=False,
        duration="20-year mine life",
        magnitude_description=(
            "Antofagasta is a London-listed, Santiago-headquartered "
            "mining conglomerate. Revenue flows to corporate treasury "
            "in Chile. Dividends flow to global institutional "
            "shareholders. Minnesota sees payroll taxes and local "
            "procurement — a fraction of gross revenue."
        ),
        reversible=False,
    ),
    ValueFlow(
        name="Capital returns / dividends",
        origin="Antofagasta PLC earnings",
        destination="Luksic family (controlling shareholder, Santiago) + institutional investors (London, NYC, global)",
        stays_in_state=False,
        duration="Quarterly, 20-year mine life",
        magnitude_description=(
            "Antofagasta's dividend policy returns 35-50% of net "
            "earnings. The Luksic Group holds ~65% of Antofagasta. "
            "Zero dividend dollars stay in St. Louis County, MN."
        ),
        reversible=False,
    ),
    ValueFlow(
        name="Political access / lobbying capital",
        origin="Corporate treasury + industry association dues",
        destination="Washington DC (CRA vote), St. Paul (state legislature)",
        stays_in_state=False,
        duration="Continuous through permitting + operating life",
        magnitude_description=(
            "Twin Metals / Antofagasta lobbying expenditures funded "
            "the political pathway to the 2026-04-16 CRA vote that "
            "eliminated PLO 7917. This capital was extracted from "
            "mining revenue elsewhere and deployed to open access "
            "to this specific ore body."
        ),
        reversible=False,
    ),
    ValueFlow(
        name="Technical expertise / workforce",
        origin="Imported engineering + management staff",
        destination="Return to home offices post-closure",
        stays_in_state=False,
        duration="20-year mine life",
        magnitude_description=(
            "Senior technical and management positions filled from "
            "corporate roster, not local hire. Expertise leaves "
            "with the staff at closure. Local workforce gets "
            "operating-level positions that do not transfer to "
            "other industries."
        ),
        reversible=False,
    ),
]

STAYS_BEHIND = [
    ValueFlow(
        name="Acid rock drainage",
        origin="Exposed sulfide waste rock + tailings",
        destination="Kawishiwi chain -> BWCA -> Rainy River -> Lake of the Woods -> Canada",
        stays_in_state=True,
        duration="Centuries to millennia (Singer-Stumm kinetics, microbial catalysis, delta-G < 0)",
        magnitude_description=(
            "AMD is thermodynamically spontaneous and microbially "
            "catalyzed 10^6x. Once started, it runs until the "
            "sulfide is consumed. Half-life ~290 yr in this model. "
            "No large hardrock mine has demonstrated AMD can be "
            "stopped once initiated."
        ),
        reversible=False,
    ),
    ValueFlow(
        name="Mercury + heavy metal loading",
        origin="Waste rock leachate",
        destination="Lake sediments, fish tissue, loon tissue, human tissue",
        stays_in_state=True,
        duration="Hg: persists in sediment for centuries. Bioaccumulates 2.7e6x in lake trout.",
        magnitude_description=(
            "Methylmercury enters the food web and concentrates "
            "upward. Effects persist 3 generations in exposed "
            "populations (Minamata data). Lake Superior residence "
            "time is 191 years — pollution persists ~2 centuries "
            "in the receiving basin."
        ),
        reversible=False,
    ),
    ValueFlow(
        name="Community collapse costs",
        origin="Property value loss, business closure, institutional failure",
        destination="Ely, Babbitt, Tower, Winton residents; St. Louis County; State of MN; Medicaid",
        stays_in_state=True,
        duration="Permanent — communities do not recover from this pattern (see Picher OK)",
        magnitude_description=(
            "Secondary effects model shows: school closure, "
            "hospital closure, insurance withdrawal, bank "
            "collateral impairment, volunteer fire dept collapse, "
            "0/22 outfitters surviving (tailings failure). Tax "
            "base death spiral means no revenue to address any "
            "of it."
        ),
        reversible=False,
    ),
    ValueFlow(
        name="Treaty violation liability",
        origin="Sulfate contamination of manoomin waters",
        destination="Federal government (trust obligation) + State of MN + mining company (if still solvent)",
        stays_in_state=True,
        duration="Perpetual — treaty rights do not expire",
        magnitude_description=(
            "1854 Treaty usufructuary rights for Bois Forte, "
            "Grand Portage, Fond du Lac. Sulfate above 10 mg/L "
            "destroys the protected resource. Trail Smelter "
            "precedent: $1.08T cumulative undiscounted liability "
            "over 500-yr simulation. Federal trust obligation "
            "means US government is ultimately liable if the "
            "company is insolvent."
        ),
        reversible=False,
    ),
    ValueFlow(
        name="Cultural knowledge loss",
        origin="Displacement + resource destruction",
        destination="Lost — identity-level encoding has replacement probability 0.0",
        stays_in_state=True,
        duration="Permanent — plasticity window does not reopen",
        magnitude_description=(
            "Manoomin harvesting knowledge held at identity level "
            "by ~15% of tribal population. Displacement or resource "
            "destruction breaks transmission chain. This is not "
            "property damage that can be compensated. It is the "
            "destruction of a cognitive architecture that took "
            "generations to build. See calibration/"
            "architecture_mismatch.py."
        ),
        reversible=False,
    ),
    ValueFlow(
        name="Perpetual water treatment obligation",
        origin="AMD chemistry (thermodynamically spontaneous)",
        destination="Ratepayers, taxpayers, or unfunded",
        stays_in_state=True,
        duration="Perpetuity — no demonstrated endpoint for AMD treatment",
        magnitude_description=(
            "Active water treatment costs $2-10M/yr for comparable "
            "sites. Over centuries, this exceeds the mine's total "
            "revenue. If the company is insolvent (which is the "
            "historical pattern for hardrock mines), the cost "
            "transfers to the public."
        ),
        reversible=False,
    ),
]


# ══════════════════════════════════════════════════════════════
# CAUSAL LOOP — mapped from substrate_audit.py
# ══════════════════════════════════════════════════════════════

EXTRACTION_LOOP = {
    "TITLE": {
        "node": "Mineral lease + CRA reversal of PLO 7917",
        "description": (
            "Legal access to the ore body. The lease is the title "
            "node — without it, no extraction occurs. PLO 7917 was "
            "the constraint; CRA vote removed it."
        ),
        "drives": "SURPLUS",
    },
    "SURPLUS": {
        "node": "Ore revenue — leaves state as concentrate + profit",
        "description": (
            "Cu-Ni concentrate shipped to smelter (Chile/Asia). "
            "Revenue to Antofagasta (Santiago). Dividends to Luksic "
            "family + global shareholders. Payroll taxes are the "
            "only surplus that touches Minnesota, and they end when "
            "the mine closes."
        ),
        "drives": "POWER",
    },
    "POWER": {
        "node": "Corporate + political capital to maintain access",
        "description": (
            "Mining revenue funds lobbying, campaign contributions, "
            "and industry-association political operations. This "
            "capital maintains the political conditions that keep "
            "the lease active and resist regulatory constraint."
        ),
        "drives": "ENFORCE",
    },
    "ENFORCE": {
        "node": "CRA vote + regulatory capture + EA limitations",
        "description": (
            "The CRA mechanism bypasses environmental analysis. "
            "The EA process is bounded by stationarity assumptions "
            "(climate_boundary.py). The enforcement node prevents "
            "the constraint signal (AMD, treaty violation, community "
            "collapse) from reaching the decision layer."
        ),
        "drives": "TITLE",
        "is_self_reinforcing": True,
    },
    "CONSTRAINT": {
        "node": "Physics — AMD thermodynamics, treaty law, community capacity",
        "description": (
            "The external constraint that the loop suppresses. "
            "delta-G < 0 for sulfide oxidation (physics). Treaty "
            "rights are constitutionally protected (law). Community "
            "collapse is self-reinforcing once triggered (secondary "
            "effects). None of these constraints can be lobbied, "
            "bought, or voted away. They operate on the physical "
            "substrate, not the political one."
        ),
        "drives": "Injects perturbation into ENFORCE when buffer breaks",
        "is_external": True,
    },
}


# ══════════════════════════════════════════════════════════════
# NET TRANSFER ACCOUNTING
# ══════════════════════════════════════════════════════════════

@dataclass
class NetTransfer:
    category: str
    to_whom: str
    from_whom: str
    net_direction: str
    time_asymmetry: str
    falsifiable: str


NET_TRANSFERS = [
    NetTransfer(
        category="Mineral value",
        to_whom="Antofagasta shareholders (Santiago/London/global)",
        from_whom="Minnesota geology (non-renewable, one-time extraction)",
        net_direction="OUT of state, OUT of country",
        time_asymmetry="Extracted in 20 yr; geology took 1.1 Ga to form",
        falsifiable=(
            "Show that refined Cu-Ni products will be manufactured "
            "in Minnesota from this ore. (They will not — no "
            "smelter capacity in state.)"
        ),
    ),
    NetTransfer(
        category="Operating profit",
        to_whom="Corporate treasury -> dividends -> global capital markets",
        from_whom="Minnesota labor + Minnesota geology",
        net_direction="OUT of state",
        time_asymmetry="Captured in 20 yr; costs persist centuries",
        falsifiable=(
            "Show that Antofagasta will reinvest operating profit "
            "in Minnesota post-closure. (Their corporate charter "
            "requires fiduciary duty to shareholders, not to "
            "host communities.)"
        ),
    ),
    NetTransfer(
        category="Cleanup liability",
        to_whom="MN taxpayers, federal Superfund, or unfunded",
        from_whom="Mine operator (if still solvent — historically, they are not)",
        net_direction="STAYS in state as unfunded obligation",
        time_asymmetry="Perpetual; exceeds total mine revenue over centuries",
        falsifiable=(
            "Show a Cu-Ni sulfide mine that fully funded its "
            "perpetual AMD treatment without public subsidy. "
            "(No example exists.)"
        ),
    ),
    NetTransfer(
        category="Health costs",
        to_whom="Medicaid (62%), affected individuals, IHS (tribal)",
        from_whom="Contamination exposure (Hg, Pb, Se, Mn, sulfate)",
        net_direction="STAYS in state; partially federalized via Medicaid/IHS",
        time_asymmetry="Epigenetic effects persist 3 generations",
        falsifiable=(
            "Show that the mine's health-impact bond covers "
            "multi-generational neurodevelopmental costs. "
            "(No such bond exists in the proposal.)"
        ),
    ),
    NetTransfer(
        category="Ecosystem services",
        to_whom="Lost — no recipient; services cease to exist",
        from_whom="BWCA watershed, boreal forest, manoomin, fisheries, beaver wetlands",
        net_direction="DESTROYED, not transferred",
        time_asymmetry=(
            "Ecosystem services built over millennia; destroyed in "
            "decades; mycorrhizal recovery 80 yr, beaver habitat "
            "recovery decades, manoomin recovery unknown, boreal "
            "biome recovery: may not occur (climate transition)"
        ),
        falsifiable=(
            "Show that the closure plan's revegetation success rate "
            "holds when mycorrhizal networks are dead, earthworms "
            "have consumed the duff layer, and the reference biome "
            "is transitioning to oak savanna. (It cannot.)"
        ),
    ),
    NetTransfer(
        category="Treaty rights",
        to_whom="Destroyed — rights exist but the resource they protect does not",
        from_whom="Bois Forte, Grand Portage, Fond du Lac (1854 Treaty)",
        net_direction="DESTROYED; federal trust obligation triggered",
        time_asymmetry="Treaty is perpetual; resource destruction is irreversible",
        falsifiable=(
            "Show that sulfate below 10 mg/L can be maintained in "
            "all 1854 Treaty waters for the duration of the treaty. "
            "(The simulation shows breach within 15 years of "
            "operation, sustained for centuries.)"
        ),
    ),
    NetTransfer(
        category="Community institutional capacity",
        to_whom="Lost — school, hospital, fire dept, bank, insurance market all collapse",
        from_whom="Ely, Babbitt, Tower, Winton residents",
        net_direction="DESTROYED via self-reinforcing loops",
        time_asymmetry=(
            "Institutions built over 100+ years; collapse in "
            "10-20 years once triggered; no demonstrated recovery "
            "pathway (see Picher OK: disincorporated)"
        ),
        falsifiable=(
            "Show a community of comparable size that recovered "
            "its institutional base after mine-related population "
            "loss of >50%. (Picher: 98.8% loss, disincorporated. "
            "Flint: 21% loss, still declining.)"
        ),
    ),
]


# ══════════════════════════════════════════════════════════════
# SCORING — using substrate_audit dimensions where applicable
# ══════════════════════════════════════════════════════════════

EXTRACTION_SCORING = {
    "value_leaves_state": {
        "score": 10, "of": 10,
        "note": "Ore, revenue, dividends, expertise all exit MN. Only payroll taxes stay, and only for 20 yr.",
    },
    "cost_stays_in_state": {
        "score": 10, "of": 10,
        "note": "AMD, Hg, community collapse, treaty liability, perpetual treatment all stay. Permanently.",
    },
    "time_asymmetry": {
        "score": 10, "of": 10,
        "note": "20-yr extraction window vs centuries-to-millennia cost window. Ratio > 50:1.",
    },
    "corporate_solvency_at_closure": {
        "score": 9, "of": 10,
        "note": "Historical pattern: hardrock mining companies are insolvent at closure. Liability transfers to public.",
    },
    "regulatory_capture_completeness": {
        "score": 10, "of": 10,
        "note": "CRA bypasses environmental analysis entirely. No mechanism to require updated risk assessment.",
    },
    "community_consent": {
        "score": 10, "of": 10,
        "note": "MCT declined task force. 1854 Treaty Authority issued own report. CRA overrides local opposition.",
    },
    "wealth_consolidation_direction": {
        "score": 10, "of": 10,
        "note": "Luksic family (~$25B net worth) captures value; shallow-well homeowners (~$29k median income) absorb cost.",
    },
    "measurement_system_bias": {
        "score": 9, "of": 10,
        "note": (
            "EA measures projected impacts against stationarity assumptions. "
            "Does not measure: secondary loops, commercial cascade, cultural "
            "knowledge loss, epigenetic transmission, peatland CH4, compound "
            "hazards. The measurement system is structurally blind to the "
            "majority of the actual cost."
        ),
    },
    "reversibility": {
        "score": 10, "of": 10,
        "note": (
            "Every outflow is irreversible. Ore cannot be un-mined. AMD cannot "
            "be stopped. Cultural knowledge cannot be retrained. Ecosystem "
            "services cannot be re-purchased. Treaty rights cannot be un-violated."
        ),
    },
    "extraction_pattern_match": {
        "score": 10, "of": 10,
        "note": (
            "TITLE->SURPLUS->POWER->ENFORCE->TITLE loop is complete and "
            "self-reinforcing. Matches substrate_audit.CAUSAL_LOOP exactly. "
            "The BWCA mine is a specific instance of the general extraction "
            "topology the repo already describes."
        ),
    },
}


# ══════════════════════════════════════════════════════════════
# COMPOSITE
# ══════════════════════════════════════════════════════════════

def emit_extraction_topology():
    scores = [v["score"] for v in EXTRACTION_SCORING.values()]
    max_scores = [v["of"] for v in EXTRACTION_SCORING.values()]
    composite = sum(scores) / sum(max_scores)

    return {
        "audit_id": "BWCA-TwinMetals-ExtractionTopology-2026-04-17",
        "outflows": [f.__dict__ for f in OUTFLOWS],
        "stays_behind": [f.__dict__ for f in STAYS_BEHIND],
        "causal_loop": EXTRACTION_LOOP,
        "net_transfers": [t.__dict__ for t in NET_TRANSFERS],
        "scoring": EXTRACTION_SCORING,
        "composite_score": round(composite, 3),
        "one_line": (
            "Value exits the state as ore, revenue, and dividends "
            "within 20 years. Cost stays as AMD, mercury, community "
            "collapse, and treaty liability for centuries. The "
            "measurement system that approved it is structurally "
            "blind to the majority of the actual cost. This is not "
            "a risk assessment failure — it is an extraction topology "
            "operating as designed."
        ),
    }


def print_summary():
    print("=" * 70)
    print("  EXTRACTION TOPOLOGY — BWCA / TWIN METALS")
    print("=" * 70)

    print("\n  VALUE THAT LEAVES MINNESOTA:")
    for f in OUTFLOWS:
        print(f"    {f.name}")
        print(f"      -> {f.destination}")
        print(f"      duration: {f.duration}")
        print()

    print("  COST THAT STAYS:")
    for f in STAYS_BEHIND:
        print(f"    {f.name}")
        print(f"      duration: {f.duration}")
        print(f"      reversible: {f.reversible}")
        print()

    print("  CAUSAL LOOP:")
    for node, info in EXTRACTION_LOOP.items():
        print(f"    {node}: {info['node']}")
        print(f"      drives: {info['drives']}")
        print()

    result = emit_extraction_topology()
    print(f"  COMPOSITE SCORE: {result['composite_score']:.1%}")
    print(f"\n  NET TRANSFERS ({len(NET_TRANSFERS)}):")
    for t in NET_TRANSFERS:
        print(f"    {t.category}: {t.net_direction}")

    print(f"\n  {result['one_line']}")


if __name__ == "__main__":
    print_summary()
