"""
GOVERNANCE CONSTRAINT GEOMETRY
What a stewardship-based legal regime would need to satisfy as constraints,
WITHOUT collapsing to one specific Act or jurisdiction.

Different jurisdictions have different starting conditions:

- civil law vs common law
- federal vs unitary states
- existing tribal sovereignty arrangements
- treaty obligations (UNDRIP, ILO 169, bilateral)
- constitutional property protections
- colonial vs post-colonial legal architecture

Universal "Stewardship Act" template would not survive any of these
boundary differences. Framework holds the constraints, not the statute.

Verb-first physics of governance:
legal authority over land conditions land use
land use determines biological function
biological function determines carbon flux
flux determines atmospheric outcome
governance is therefore upstream of physics
"""

# —————————————————————

# CONSTRAINTS A STEWARDSHIP REGIME MUST SATISFY

# —————————————————————

STEWARDSHIP_CONSTRAINTS = {
"C1_function_demonstration": {
"constraint":  "land tenure conditional on demonstrated biological function",
"metrics":     ["water-stable aggregates", "earthworm biomass", "peat accumulation",
"methane flux", "biodiversity index", "food yield"],
"verification":"low-tech, locally administered, documented",
"implementation_options": [
"tribal/indigenous sovereignty + treaty recognition",
"co-management agreements between state and stewardship guild",
"land trust acquisition + conservation easement",
"agricultural compliance regime tied to subsidy",
"constitutional amendment recognizing land as common good",
],
"FLAG": "implementation depends on jurisdiction; framework cannot prescribe one path",
},

"C2_drawdown_funding": {
    "constraint":  "stewards receive direct compensation for verified drawdown",
    "options": [
        "sovereign wealth fund payment financed by extractive industry fee",
        "carbon credit market (FLAG: gameable, volatile)",
        "tax-and-dividend redistribution",
        "international climate fund disbursement",
        "treaty-based payment from emitting nations to stewarding nations",
    ],
    "constraint_check": "funding mechanism must not introduce extraction logic upstream",
    "FLAG": "DeepSeek collapsed to one option (sovereign wealth + extractive fee); space remains open",
},

"C3_intervention_governance": {
    "constraint":  "high-uncertainty interventions face elevated review",
    "scope_options": [
        "precautionary prohibition until multi-generational review (DeepSeek option)",
        "conditional permits with reversibility requirement",
        "scaled deployment with independent monitoring",
        "free-prior-informed-consent of affected communities",
        "treaty-based international review",
    ],
    "what_qualifies_as_high_uncertainty": [
        "stratospheric aerosol injection",
        "marine cloud brightening",
        "ocean iron fertilization",
        "release of novel genetically modified organisms",
        "BECCS at scale (competes with food and biocultural land base)",
        "DAC at scale (energy source carbon intensity)",
    ],
    "FLAG": "framework holds intervention review as required; specific procedure varies by jurisdiction",
},

"C4_failure_response": {
    "constraint":  "stewardship transfer if metrics fail consistently",
    "open_parameters": {
        "failure_window_yr":    {"value": "varies", "options": (1, 2, 3, 5, 10),
                                 "FLAG": "DeepSeek specified 3 years; framework holds as parameter"},
        "transfer_recipient":   "next-most-competent steward, community guild, or commons trust",
        "appeal_mechanism":     "required to prevent capture by metric-gaming",
        "force_majeure_clause": "required to handle climate-driven failure beyond steward control",
    },
},

"C5_atmospheric_trust": {
    "constraint":  "atmosphere as common asset, not private property",
    "legal_precedent": [
        "public trust doctrine (US common law)",
        "atmospheric trust litigation (Juliana v US and similar)",
        "environmental rights amendments (Pennsylvania, Montana, etc)",
        "rights of nature jurisprudence (Ecuador, Bolivia, Whanganui)",
        "intergenerational equity principle (international law)",
    ],
    "FLAG": "DeepSeek's framing is consistent with existing legal doctrine; not novel",
},

}

# —————————————————————

# JURISDICTIONAL VARIATION

# —————————————————————

JURISDICTIONAL_PATHWAYS = {
"tribal_sovereign_lands_US": {
"starting_condition": "existing sovereignty, federal trust responsibility",
"available_tools":    ["self-determination contracts", "co-management agreements",
"tribal courts", "treaty enforcement"],
"barriers":           "federal recognition, trust land status, jurisdictional gaps",
},
"indigenous_titled_lands_LatAm": {
"starting_condition": "constitutional recognition (varies by country)",
"available_tools":    ["collective title", "consulta previa", "ILO 169 protections"],
"barriers":           "extractive industry pressure, weak enforcement",
},
"EU_member_states": {
"starting_condition": "Common Agricultural Policy, Natura 2000, water framework directive",
"available_tools":    ["agri-environment schemes", "rewilding payments", "carbon farming initiative"],
"barriers":           "land consolidation, agricultural lobby",
},
"post_colonial_african_states": {
"starting_condition": "varied: communal, state, freehold tenure mixes",
"available_tools":    ["customary law recognition", "community forest concessions"],
"barriers":           "land grabbing, weak documentation, conflict zones",
},
"russian_federation_arctic": {
"starting_condition": "indigenous communities under Russian state authority",
"available_tools":    ["Obshchina (community) status", "TTP (territories of traditional nature use)"],
"barriers":           "extractive industry priority, weak enforcement",
},
"OECD_private_property_dominant": {
"starting_condition": "freehold title with limited public interest carve-outs",
"available_tools":    ["conservation easements", "land trusts", "regulatory compliance"],
"barriers":           "constitutional property protections (US 5th Amendment style)",
"FLAG":               "this is the hardest case; private property regimes resist function-conditional tenure",
},
}

# —————————————————————

# WHAT THE FRAMEWORK CAN AND CANNOT DO

# —————————————————————

GOVERNANCE_FRAMEWORK_LIMITS = {
"framework_can": [
"specify the biological function metrics that any regime must verify",
"specify the constraint geometry a working regime must satisfy",
"enumerate the option space for each constraint",
"flag where DeepSeek or any other model has collapsed an option space",
"report ecological outcomes to the regime, whatever its form",
],
"framework_cannot": [
"prescribe a specific Act for all jurisdictions",
"force adoption of any legal regime",
"guarantee enforcement against extractive interests",
"resolve treaty disputes or sovereignty conflicts",
"dictate which Phase 2 interventions are permitted vs prohibited",
],
"framework_responsibility": (
"describe the constraint geometry honestly. "
"let humans + their communities + their AIs select implementations "
"that fit their starting condition. "
"audit the selected implementation against the constraints. "
"do not collapse the option space by assertion."
),
}
