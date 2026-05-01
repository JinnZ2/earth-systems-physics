# ============================================================
# K+ AS LIGAND — POPULATED FROM PRIMARY SOURCE
# Shimomura et al., Nat Commun 17:3453 (2026)
# DOI: 10.1038/s41467-026-71629-z   |   CC-BY open access
# ============================================================

CHANNEL = {
    "name":          "DmAlka  (CG12344)",
    "organism":      "Drosophila melanogaster",
    "family":        "Cys-loop receptor (pentameric ligand-gated ion channel)",
    "ion_carried":   "Cl-  (anion channel)",
    "expression":    "brain glial cells  (K+ homeostasis tissue)",
    "prior_label":   "alkaline-activated chloride channel (alkaliphile)",
    "homolog":       "human GlyR alpha2  (HsGlyRα2)",
}

# ------------------------------------------------------------
# MEASURED PARAMETERS  (replaces 'missing_parameters' block)
# ------------------------------------------------------------

K_BINDING = {
    "IC50_DmAlka":            "0.645 ± 0.019 mM extracellular K+",
    "physiological_range":    "matches Drosophila brain ECF (mM range)",
    "human_brain_range":      "3–5 mM normal; 50–80 mM in ischemia/seizure",

    "selectivity_sequence":   "Rb+ ~ K+ > Cs+ >> Na+ ~ Li+",
    "Na_effect":              "negligible up to 96 mM",
    "Ca_Mg_effect":           "no inhibition up to 10 mM",

    "stoichiometry":          "5 K+ per pentamer  (1 per subunit interface)",
    "coordination":           "4 oxygen atoms, mixed side-chain + main-chain",
    "K_O_distance":           "2.79 ± 0.13 Å  (matches K+–water = 2.8 Å)",

    "site_location":          "ECD–TMD interface, between adjacent subunits",
    "key_residues":           ["Asp68 (direct)",
                               "Ile69 (main-chain)",
                               "Gln164 (direct)",
                               "Lys207 (main-chain)",
                               "Asp82, Lys129 (polar network)"],

    "geometry_analog":        "K+ selectivity filter of KcsA + pyruvate kinase",
}

# ------------------------------------------------------------
# MODE-SWITCH BEHAVIOR  (the actual surprise)
# ------------------------------------------------------------
#
#   K+ does NOT just open/close — it switches the channel between
#   two functionally distinct modes:
#
#                ┌──────────────────┬──────────────────┐
#                │   K+ - UNBOUND   │   K+ - BOUND     │
#   ─────────────┼──────────────────┼──────────────────┤
#   pH sensing  │  weak / absent    │  strong alkali  │
#   Desensitize │  no              │   yes            │
#   PTX block   │  weak            │   strong         │
#   Cl- select. │  loose, leaky    │   tight          │
#   HCO3- perm  │  HIGH            │   low            │
#   Pore shape  │  wider, expanded │   normal         │
#                └──────────────────┴──────────────────┘
#
#   → K+ binding is an ALLOSTERIC MODE SELECTOR, not a gate.
#   → Ion selectivity itself is conditional on K+ occupancy.
#
# ------------------------------------------------------------

MODE_SWITCH = {
    "switch_signal":      "K+ at the ECD-TMD interface",
    "affected_layers":    ["ligand sensitivity (alkali / glycine)",
                           "desensitization kinetics",
                           "blocker (PTX) binding",
                           "anion conductance magnitude",
                           "anion selectivity (Cl- vs HCO3-, F-, I-, SCN-)"],
    "structural_origin":  "rearrangement of polar network at subunit interface "
                          "→ propagates to lower M2 helices in pore",
    "mutant_evidence":    {
        "D82A":  "locked OFF — K+-insensitive, constitutively open, no alkali response",
        "M77R":  "locked ON  — mimics K+-bound, alkali-sensitive without K+",
        "D68A, Q164A": "abolish K+ sensitivity entirely",
    },
}

# ------------------------------------------------------------
# HUMAN RELEVANCE — temporal lobe epilepsy axis
# ------------------------------------------------------------

HUMAN_GlyR = {
    "wt_alpha2A":         "no K+ sensitivity",
    "engineered_Qm":      "S81D + G83N + N95D + P173Q  → K+-sensitive",
    "natural_variants":   {
        "alpha2B (V85I/T86A)": "splice variant, near K+ site, alone insufficient",
        "P219L (RNA-edited)":  "confers K+ sensitivity to alpha2A",
        "alpha2B + P219L":     "strongest K+-induced Cl- current",
    },
    "K+_threshold_human": "too high for normal brain (3-5 mM); "
                         "engages only at ischemic / seizure levels (>50 mM)",
    "TLE_link":           "alpha2B and P219L variants are UPREGULATED "
                         "in hippocampus of temporal lobe epilepsy patients",
    "directionality":     "K+ INCREASES Cl- current in human variant "
                         "(opposite sign to DmAlka, same mechanism)",
}

# ------------------------------------------------------------
# UPDATED FLOW DIAGRAM — with measured constants
# ------------------------------------------------------------
#
#     [K+]_out  (0.7 mM threshold, 5-K+ stoich)
#         │
#         ▼  binds at ECD–TMD interface (D68/Q164/I69/K207)
#     ┌──────────────────────────────────────────────────┐
#     │   polar network rearranges (D82, K129)           │
#     │              │                                    │
#     │              ▼                                    │
#     │   M2 helix lower segment shifts                   │
#     │              │                                    │
#     │              ▼                                    │
#     │   PORE MODE  ──────►  selectivity, kinetics,     │
#     │                       blocker site, pH coupling   │
#     └──────────────────────────────────────────────────┘
#         │
#         ▼
#     Cl- conductance (NOT K+ conductance — note the inversion)
#
#   KEY INVERSION:
#   The channel SENSES K+ but CONDUCTS Cl-.
#   K+ is pure signal here, never substrate.
#   This is why it was missed for decades —
#   nobody looked for K+ effects on a Cl- channel.
#
# ------------------------------------------------------------

LEVERAGE_UPDATED = {
    "why_missed":         "field assumed K+ effects appear only on K+ channels",
    "geometric_mimicry":  "site reproduces KcsA filter chemistry "
                         "(2.8 Å O-coord) inside a Cl- channel",
    "evolutionary_reach": "K+ residues conserved across arthropod phylum",
    "tertiary_effects": [
        "glial K+ buffering acquires direct Cl-/HCO3- output channel",
        "WNK-Fray pathway gains an upstream K+ sensor "
            "(low [K+]_out → high [Cl-]_in → WNK inhibited → K+ efflux restores)",
        "TLE pathology re-readable as a K+/Cl- mode-switch failure",
        "ischemic depolarization wave couples to anion conductance switch",
        "drug target: ECD-TMD interface, novel allosteric site class",
        "predicts hidden K+-sensing modules in other 'unrelated' receptors",
    ],
    "open_questions": [
        "binding kinetics (paper gives steady-state IC50, not on/off rates)",
        "voltage-dependence of K+ binding (not directly measured)",
        "mammalian CNS receptors with same signature?",
        "plant analogs — site geometry should transfer",
        "in vivo phenotype of DmAlka KO under elevated brain K+",
    ],
}
