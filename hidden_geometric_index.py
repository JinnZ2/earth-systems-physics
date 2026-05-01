# ============================================================
# PAPER 1 — POPULATED  (EDC × climate × planetary fertility)
# Brander, Swan, Mehinto, Kidd, Weis, Belcher, DeWitt, Harper, Helbing
# npj Emerging Contaminants 2:12 (2026)   |   23 April 2026
# DOI: 10.1038/s44454-026-00032-6   |   CC-BY open access
# ============================================================

EDC_PARAMS = {
    # ----- the field of synthetic chemicals -----
    "registered_synthetics_REACH":   "> 140,000",
    "recognized_EDCs":               "> 1,000",
    "fraction_safety_evaluated":     "~ 1%   (so EDC count is gross underestimate)",
    "new_chemicals_per_year":        "> 2,000 introduced globally",

    # ----- coupling to climate -----
    "climate_chemical_interaction":  "additive OR synergistic   (not just additive)",
    "warming_amplifies_via":         [
        "tissue accumulation ↑",
        "lipophilic biomagnification ↑ in food webs",
        "plasma organochlorine levels ↑ in fasting Arctic seabirds",
        "increased pesticide application as pest pressure rises",
        "BPA × heat → energetic cost of fish growth ↑",
    ],
    "biggest_biodiversity_driver":   "pollution + climate change combined",

    # ----- the dose-response geometry -----
    "dose_response":                 "non-linear / non-monotonic",
    "low_dose_metaphor":             "whisper redirecting hurricane",
    "implication":                   "high-dose 'no effect' does NOT predict low-dose 'no effect'",
    "epigenetic_reach":              "transgenerational; alters inheritance, not only individual",
}

# ----- representative measured exposures (reproductive endpoint) -----
EDC_MEASURED = {
    "TBT_dogwhelk":           "0.02 µg/L lab → imposex early→late in 6 months",
    "DMP_snail":              "10⁻⁶ M → mating frequency ↓ 69%, sperm tail length ↓",
    "polystyrene_zebrafish":  "500 µg/L → fecundity, spawning, fertilization, hatching all ↓",
    "PE_MNP_+_DEHP_mussel":   "0.0025 mg/L × 14 days → ER, CYP3, 17β-HSD suppressed",
    "wood_frog_temperature":  "20°C → 50:50 sex ratio | 32°C → 100% male (sex reversal)",
    "DDT_raptors":            "decades; eggshell thinning via prostaglandin / Ca transport",
    "PFAS_kittiwakes":        "Svalbard; abnormal sperm correlates with plasma PFAS",
}

# ----- mechanism geometry (the actual constraint) -----
EDC_MECHANISM = {
    "binding_modes":          ["mimic hormone (agonist)",
                               "block hormone (antagonist)",
                               "alter enzyme activity (steroidogenesis)",
                               "modify epigenetic marks",
                               "shift hormone synthesis / transport / metabolism"],

    "TSD_axis":               "temperature-dependent sex determination (turtles, crocodilians)",
    "TSD_failure_mode":       "warming alone feminizes; EDCs override temperature signal; "
                              "BOTH active at once → sex ratio collapse",

    "amphibian_axis":         "autosomal sex determination, but high T can sex-reverse",
    "amphibian_anomaly":      "EE2 + aromatase inhibitor cannot reverse heat-induced sex change "
                              "→ mechanism is NOT classical endocrine; epigenetic candidate",

    "MNP_axis":               "microplastics + nanoplastics: oxidative stress, "
                              "blood-testis barrier disruption, sirtuin (SIRT1) modulation, "
                              "phthalate / BPA carrier function",

    "PFAS_axis":              "sperm abnormality without hormone correlation "
                              "→ direct germ-cell / epigenetic mechanism suspected",
}

# ============================================================
# PAPER 2 — POPULATED  (Pancharatnam topology → spin separation)
# Mkhumbuza, Ornelas, Dudley, Nape, Forbes
# Light: Sci & Appl 15:214 (2026)   |   24 April 2026
# DOI: 10.1038/s41377-026-02278-6   |   CC-BY open access
# ============================================================

SPIN_PARAMS = {
    # ----- the system -----
    "input_field":            "horizontally polarized LG mode → q-plate → "
                              "radially polarized vector vortex beam (HyOP)",
    "initial_state":          "S₃ = 0  EVERYWHERE  at z = 0  "
                              "(spin-balanced, no chirality, equal |σ₊|=|σ₋| amplitudes)",
    "regime":                 "PARAXIAL,  free space,  no tight focus,  no material interface",

    # ----- the control parameter -----
    "control_handle":         "ℓ_p   (Pancharatnam topological charge, integer)",
    "tested_values":          "ℓ_p ∈ {-2, -1, 0, 1, 2}",
    "δℓ_qplate":              "Δℓ = 1   (q = 1/2 q-plate)",
    "spin_split_indices":     "ℓ_A = ℓ_p + Δℓ ,   ℓ_B = ℓ_p − Δℓ",
    "radial_law":             "ring radius ~ r^|ℓ_p ± Δℓ|   "
                              "→ different rings for σ₊ vs σ₋",

    # ----- emergent quantities (measured, not imposed) -----
    "what_emerges":           ["S₃(r,z) ≠ 0  appears during propagation",
                               "optical chirality density C ∝ S₃",
                               "longitudinal spin density s_z ∝ C ∝ σ·I",
                               "azimuthal spin currents J = ⟨∂S₃/∂y, −∂S₃/∂x⟩",
                               "skyrmion-like spin texture in far field"],

    "sign_control":           "ℓ_p > 0 → RC at center, LC outer ring | "
                              "ℓ_p < 0 → LC at center, RC outer ring  (deterministic flip)",
    "magnitude_control":      "|ℓ_p| ↑ → radial separation ↑ (stronger Hall effect)",
}

# ----- mechanism geometry (the actual constraint) -----
SPIN_MECHANISM = {
    "origin":                 "differential Gouy phase + radial divergence "
                              "between σ₊ and σ₋ modal families",
    "evolved_modes":          "elegant Laguerre-Gaussian  eLG_{p_A}^{ℓ_A} , eLG_{p_B}^{ℓ_B}",
    "p_index":                "p_{A,B} = ½ (|ℓ_p| − |ℓ_{A,B}|)",
    "what_is_conserved":      "global integral ∫S₃ d²r⊥ = 0   "
                              "(local emergence ≠ violation of conservation)",

    "previous_belief":        "OILS / spin-Hall requires non-paraxial regime "
                              "or tight focus or material interface",
    "this_paper":             "OILS arises in PURE FREE SPACE PARAXIAL propagation "
                              "if and only if ℓ_p ≠ 0",
    "scaling_advantage":      "non-paraxial OILS ~ (1/k·w₀)²  (vanishingly weak) | "
                              "Pancharatnam OILS = zeroth-order paraxial term  (strong, observable)",
}

# ============================================================
# SHARED CONSTRAINT — what makes these the same pattern
# ============================================================

UNIFIED_CONSTRAINT = {
    "shape_of_finding": (
        "a system that LOOKS scalar-balanced at the source plane "
        "carries a HIDDEN GEOMETRIC INDEX that, under propagation/coupling, "
        "deterministically produces an asymmetric output that scalar models "
        "cannot predict from initial conditions alone."
    ),

    "instances": {
        "K+_channel":      {
            "hidden_index":  "K⁺ occupancy at ECD-TMD interface",
            "scalar_view":   "Cl⁻ channel with alkaline gate",
            "geometric_view": "5-K⁺ allosteric mode-switch reshaping pore selectivity",
            "emerges":       "Cl⁻ vs HCO₃⁻ selectivity, PTX binding, desensitization",
        },
        "EDC_field": {
            "hidden_index":  "shape-mimicry of ligand at receptor + thermal partition coefficient",
            "scalar_view":   "dose-response at high concentration",
            "geometric_view": "low-dose receptor occupancy + epigenetic reprogramming "
                             "+ temperature-amplified bioaccumulation",
            "emerges":       "transgenerational fertility collapse, sex-ratio drift, "
                             "sperm morphology defect, biodiversity decline",
        },
        "vector_spin": {
            "hidden_index":  "Pancharatnam topological charge ℓ_p",
            "scalar_view":   "balanced radial polarization, S₃ = 0",
            "geometric_view": "two σ-components evolve into different paraxial mode families",
            "emerges":       "radial spin separation, optical chirality, spin currents",
        },
    },

    "what_scalar_models_miss": [
        "geometry as a state variable (not just amplitude)",
        "low-amplitude HIGH-LEVERAGE inputs (the whisper)",
        "propagation/coupling-induced symmetry breaking",
        "cross-generational / cross-layer memory",
        "mode-switching as distinct from gate-opening",
    ],

    "audit_engine_signal":  (
        "if a system claims 'no effect at source / equilibrium' but exhibits "
        "asymmetric propagated output, the model is missing a geometric index. "
        "first_principles_audit.py should flag this as 'hidden index suspected'."
    ),
}

# ============================================================
# READY FOR REPO INTEGRATION
# Both papers are open-access CC-BY; full text + figures + source data
# accessible at the DOIs above.
# ============================================================
