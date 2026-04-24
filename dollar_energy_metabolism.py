# dollar_energy_metabolism.py
# earth-systems-physics
# CC0 — No Rights Reserved
"""
Recursive energy cost model for financial system overhead.

Every dollar routed through the financial system carries a metabolic
energy load that compounds through leverage, margin capture, taxation,
narrative infrastructure, and political machinery — each layer
generating economic activity subject to the same overhead.

This is a geometric series. If any layer's recycling fraction r >= 1,
the system is a net energy sink: it consumes more energy processing the
dollar than the dollar can deliver to the project.

Thermodynamic backbone from Geometric-to-Binary-Computational-Bridge:
  - Gibbs free energy:  DeltaG = DeltaH - T*DeltaS
  - Stability ratio:    maintenance / restoration  (want < 1)
  - Phase boundary:     energetic susceptibility diverges at transition
  - Stress cascade:     E_ego -> Psi -> P_error ~ exp(beta * Psi)
  - Delusion filter:    plausibility flags on narrative claims
  - Six Sigma CTQ:      waste_factor <= 0.30 or intervention is implausible

Alternative computing paradigms (ternary, quantum, stochastic,
neuromorphic, reservoir, memristive, approximate) applied across
five physical domains (electric, gravity, magnetic, sound, thermal)
reveal that binary yes/no carbon accounting erases the continuous
physics that determines whether an intervention actually works.

Applied to: ocean timber sequestration, stratospheric aerosol
injection, and arbitrary climate finance schemes.

Core equation:
    E_total = E_base / (1 - r_effective)
    where r_effective = weighted recycling fraction
    across all overhead layers

Dependencies: None (stdlib only)
"""

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any


# ═══════════════════════════════════════════════════════════════
# PHYSICAL CONSTANTS
# ═══════════════════════════════════════════════════════════════

K_B_EV = 8.617333262145e-5   # eV/K
MJ_PER_DOLLAR_GLOBAL = 5.7   # MJ primary energy per $1 GDP (world avg)
CO2_PER_MJ_KG = 0.070        # kg CO2 per MJ (global grid mix)
CH4_GWP_20YR = 80.0          # 20-year GWP for methane


# ═══════════════════════════════════════════════════════════════
# OVERHEAD LAYER DEFINITIONS
# ═══════════════════════════════════════════════════════════════

@dataclass
class OverheadLayer:
    """
    Single layer of financial system energy overhead.

    name:        human identifier
    r_low:       conservative recycling fraction (MJ added / MJ base)
    r_high:      extractive-case recycling fraction
    description: what this layer represents physically
    """
    name: str
    r_low: float
    r_high: float
    description: str


OVERHEAD_LAYERS = [
    OverheadLayer(
        name="leverage",
        r_low=0.11,
        r_high=0.56,
        description=(
            "Banking infrastructure maintaining 3-10x leverage "
            "per deployed dollar. Buildings, servers, staff, "
            "clearinghouses, custodians, auditors, regulators. "
            "Banking sector: ~2% of global electricity."
        ),
    ),
    OverheadLayer(
        name="margin_stack",
        r_low=0.23,
        r_high=1.40,
        description=(
            "Fund managers (15-25%), project developers (10-20%), "
            "verification bodies (5-10%), credit brokers (5-15%). "
            "Total intermediary capture: 35-70% of each dollar. "
            "r > 1 means intermediaries consume more energy "
            "than the project receives."
        ),
    ),
    OverheadLayer(
        name="taxation",
        r_low=0.04,
        r_high=0.68,
        description=(
            "Tax collection, processing, redistribution. "
            "Each margin transaction taxed, tax spent on "
            "government operations including military "
            "(DOD: ~77M barrels oil/year). "
            "Recursive: tax revenue generates taxable activity."
        ),
    ),
    OverheadLayer(
        name="narrative",
        r_low=0.05,
        r_high=0.40,
        description=(
            "PR firms, websites, social media campaigns, "
            "video production, data center infrastructure "
            "for ad targeting (GPU clusters 24/7), "
            "conference travel, white papers. "
            "Energy cost of persuasion often exceeds "
            "energy cost of intervention."
        ),
    ),
    OverheadLayer(
        name="political",
        r_low=0.11,
        r_high=0.30,
        description=(
            "Lobbyists ($300-800/hr), campaign contributions, "
            "think tanks, regulatory process (environmental "
            "review, public comment, legal challenges, "
            "compliance monitoring). Davos alone: ~1,500 "
            "private jets to discuss climate."
        ),
    ),
]


# ═══════════════════════════════════════════════════════════════
# ALTERNATIVE COMPUTING PARADIGM MATRIX
# ═══════════════════════════════════════════════════════════════
# From Geometric-to-Binary-Computational-Bridge:
# Binary carbon accounting (yes/no, sequestered/not) erases
# continuous physics. These paradigms recover what binary erases.

PARADIGM_MATRIX = {
    #                    electric  gravity  magnetic  sound  thermal
    "ternary":          (True,     True,    True,     True,  True),
    "quantum":          (True,     True,    False,    True,  False),
    "stochastic":       (True,     True,    False,    True,  True),
    "neuromorphic":     (True,     False,   False,    True,  False),
    "reservoir":        (True,     True,    True,     True,  True),
    "memristive":       (True,     False,   False,    False, False),
    "approximate":      (True,     True,    False,    False, True),
}

PARADIGM_DOMAINS = ("electric", "gravity", "magnetic", "sound", "thermal")

PARADIGM_RECOVERY = {
    "ternary": (
        "Binary sign bits erase the physically distinct ZERO/EQUILIBRIUM state. "
        "Carbon accounting says sequestered=1 or not=0. Reality has a third "
        "state: carbon in transit, decomposing, or chemically transforming."
    ),
    "quantum": (
        "Binary thresholding collapses continuous superpositions into false "
        "dichotomies. A tree is not alive=1 or dead=0 — it exists in a "
        "superposition of carbon flux states that measurement collapses."
    ),
    "stochastic": (
        "Binary declares probability distributions as point estimates. "
        "Every carbon measurement is a distribution, not a number. "
        "Reporting a single sequestration figure is a lie of precision."
    ),
    "neuromorphic": (
        "Binary treats time-series as independent frames. Carbon flux "
        "is event-driven: spikes of emission/absorption carry the signal, "
        "not the time-averaged value the spreadsheet reports."
    ),
    "reservoir": (
        "Binary processes domains independently. The ocean-atmosphere-soil "
        "system is a coupled dynamical reservoir where perturbation in one "
        "domain echoes through all others. Single-arrow models cannot see this."
    ),
    "memristive": (
        "Binary reads instantaneous state. Ecosystem state IS its history — "
        "a forest logged and regrown is not the same as one never logged. "
        "The hysteresis carries information that carbon tonnage erases."
    ),
    "approximate": (
        "Binary demands exact thresholds. Approximate computing gives "
        "confidence intervals. A project claiming 275,000 tonnes/year "
        "sequestration without error bars is not science."
    ),
}


def paradigm_coverage(paradigm: str) -> int:
    """Count how many physical domains a paradigm covers."""
    row = PARADIGM_MATRIX.get(paradigm, ())
    return sum(row) if row else 0


def domain_coverage(domain: str) -> int:
    """Count how many paradigms cover a given physical domain."""
    idx = PARADIGM_DOMAINS.index(domain) if domain in PARADIGM_DOMAINS else -1
    if idx < 0:
        return 0
    return sum(1 for row in PARADIGM_MATRIX.values() if row[idx])


# ═══════════════════════════════════════════════════════════════
# SCENARIO PRESETS
# ═══════════════════════════════════════════════════════════════

@dataclass
class Scenario:
    """Financial routing scenario for a climate dollar."""
    name: str
    E_base_MJ: float
    layer_positions: str       # 'low', 'mid', 'high', or 'none'
    recursive_r: float         # effective recycling fraction
    description: str


SCENARIOS = {
    "direct_action": Scenario(
        name="Direct action (no intermediaries)",
        E_base_MJ=5.0,
        layer_positions="none",
        recursive_r=0.0,
        description="You do the work yourself. No financial system overhead.",
    ),
    "efficient": Scenario(
        name="Efficient project finance",
        E_base_MJ=5.0,
        layer_positions="low",
        recursive_r=0.30,
        description="Low margin, fast permitting, minimal leverage.",
    ),
    "typical_climate": Scenario(
        name="Typical climate finance",
        E_base_MJ=6.0,
        layer_positions="mid",
        recursive_r=0.50,
        description="50% margin stack, 3-year permitting, standard leverage.",
    ),
    "carbon_speculation": Scenario(
        name="Carbon credit speculation",
        E_base_MJ=7.0,
        layer_positions="high",
        recursive_r=0.70,
        description="70% margin stack, 7-year permitting, high leverage, speculative.",
    ),
}


# ═══════════════════════════════════════════════════════════════
# PROJECT DEFINITIONS
# ═══════════════════════════════════════════════════════════════

@dataclass
class ClimateProject:
    """A climate intervention scheme to audit."""
    name: str
    capitalization_low_USD: float
    capitalization_high_USD: float
    annual_budget_low_USD: float
    annual_budget_high_USD: float
    claimed_annual_CO2_tonnes: float
    is_sequestration: bool
    description: str


PROJECTS = {
    "ocean_timber": ClimateProject(
        name="Ocean Timber Sequestration",
        capitalization_low_USD=50e6,
        capitalization_high_USD=200e6,
        annual_budget_low_USD=10e6,
        annual_budget_high_USD=50e6,
        claimed_annual_CO2_tonnes=275_000,
        is_sequestration=True,
        description=(
            "Cut 1M boreal trees/year, sink in deep ocean. "
            "Claimed: permanent carbon removal. "
            "Actual: net carbon source before financial overhead."
        ),
    ),
    "sai": ClimateProject(
        name="Stratospheric Aerosol Injection",
        capitalization_low_USD=500e6,
        capitalization_high_USD=5e9,
        annual_budget_low_USD=2e9,
        annual_budget_high_USD=10e9,
        claimed_annual_CO2_tonnes=0,
        is_sequestration=False,
        description=(
            "Mine bauxite, refine aluminum, mill to nanoparticles, "
            "fly 60,000 sorties/year into stratosphere. "
            "Masks warming but sequesters nothing. "
            "Termination shock if stopped. Perpetual commitment."
        ),
    ),
}


# ═══════════════════════════════════════════════════════════════
# CORE ENGINE — DOLLAR ENERGY COMPUTATION
# ═══════════════════════════════════════════════════════════════

def layer_energy(layer: OverheadLayer, position: str, E_base: float) -> float:
    """
    Energy added by a single overhead layer.

    Parameters:
        layer: OverheadLayer definition
        position: 'low', 'mid', 'high', or 'none'
        E_base: base energy per dollar (MJ)

    Returns:
        MJ added per dollar by this layer.
    """
    if position == "none":
        return 0.0
    if position == "low":
        r = layer.r_low
    elif position == "high":
        r = layer.r_high
    else:
        r = (layer.r_low + layer.r_high) / 2.0
    return r * E_base


def compute_dollar_energy(scenario: Scenario) -> dict:
    """
    Total energy cost per dollar for a given scenario.

    Returns dict with layer breakdown, recursive multiplier,
    and divergence flag.
    """
    E_base = scenario.E_base_MJ
    pos = scenario.layer_positions

    layer_breakdown = {}
    subtotal_additions = 0.0

    for layer in OVERHEAD_LAYERS:
        added = layer_energy(layer, pos, E_base)
        layer_breakdown[layer.name] = {
            "MJ_added": added,
            "r_fraction": added / E_base if E_base > 0 else 0.0,
            "description": layer.description,
        }
        subtotal_additions += added

    subtotal = E_base + subtotal_additions

    r = scenario.recursive_r
    if r >= 1.0:
        recursive_multiplier = float('inf')
        total_MJ = float('inf')
    else:
        recursive_multiplier = 1.0 / (1.0 - r)
        total_MJ = subtotal * recursive_multiplier

    overall_multiplier = total_MJ / E_base if E_base > 0 else float('inf')

    return {
        "scenario": scenario.name,
        "E_base_MJ": E_base,
        "layer_breakdown": layer_breakdown,
        "subtotal_before_recursion_MJ": subtotal,
        "recursive_r": r,
        "recursive_multiplier": recursive_multiplier,
        "total_MJ_per_dollar": total_MJ,
        "overall_multiplier": overall_multiplier,
        "divergent": r >= 1.0,
    }


def compute_project_audit(project: ClimateProject,
                          scenario: Scenario) -> dict:
    """
    Apply dollar energy metabolism to a specific climate project.

    Returns full audit with CO2 equivalence and comparison
    to claimed sequestration.
    """
    dollar_energy = compute_dollar_energy(scenario)
    MJ_per_dollar = dollar_energy["total_MJ_per_dollar"]

    results = {}
    for label, USD in [
        ("capitalization_low", project.capitalization_low_USD),
        ("capitalization_high", project.capitalization_high_USD),
        ("annual_budget_low", project.annual_budget_low_USD),
        ("annual_budget_high", project.annual_budget_high_USD),
    ]:
        if math.isinf(MJ_per_dollar):
            energy_TJ = float('inf')
            CO2_tonnes = float('inf')
        else:
            energy_MJ = USD * MJ_per_dollar
            energy_TJ = energy_MJ / 1e6
            CO2_tonnes = (energy_MJ * CO2_PER_MJ_KG) / 1000.0
        results[label] = {
            "USD": USD,
            "energy_TJ": energy_TJ,
            "CO2_tonnes": CO2_tonnes,
        }

    claimed = project.claimed_annual_CO2_tonnes
    if claimed > 0 and not math.isinf(results["annual_budget_low"]["CO2_tonnes"]):
        frac_low = results["annual_budget_low"]["CO2_tonnes"] / claimed
        frac_high = results["annual_budget_high"]["CO2_tonnes"] / claimed
    else:
        frac_low = float('inf')
        frac_high = float('inf')

    return {
        "project": project.name,
        "scenario": scenario.name,
        "dollar_energy": dollar_energy,
        "project_costs": results,
        "claimed_annual_CO2_tonnes": claimed,
        "funding_CO2_as_fraction_of_claimed": {
            "low_budget": frac_low,
            "high_budget": frac_high,
        },
        "is_sequestration": project.is_sequestration,
        "description": project.description,
    }


# ═══════════════════════════════════════════════════════════════
# GIBBS FREE ENERGY — THERMODYNAMIC BACKBONE
# ═══════════════════════════════════════════════════════════════
# From Geometric-to-Binary-Computational-Bridge: lcea_analysis.py
# Treats financial overhead as entropy dissipation.

def gibbs_free_energy(delta_H: float, T: float, delta_S: float) -> float:
    """
    DeltaG = DeltaH - T * DeltaS

    Parameters:
        delta_H: total energy input (MJ) — project budget + overhead
        T: system temperature (dimensionless stress multiplier)
        delta_S: entropy production rate (waste fraction)

    Returns:
        Energy available for useful climate work (MJ).
        Negative means the system does no useful work.
    """
    return delta_H - T * delta_S


def excess_gibbs(E_ego_history: List[float], dt: float = 1.0) -> float:
    """
    Cumulative excess Gibbs energy from overhead injection.
    DeltaG_excess = integral(E_ego) dt

    This excess dissipates through cascading failures.
    """
    return sum(E_ego_history) * dt


# ═══════════════════════════════════════════════════════════════
# STABILITY RATIO — CONVERGENCE TEST
# ═══════════════════════════════════════════════════════════════
# From computational_thermodynamics.py:
# stability_ratio = maintenance / restoration
# If > 1, system degrades faster than it recovers.

@dataclass
class StabilityMetrics:
    """Stability metrics for a financial intervention."""
    maintenance_cost_MJ: float    # annual overhead to keep project running
    restoration_rate_MJ: float    # annual useful climate work delivered
    stability_ratio: float        # maintenance / restoration (want < 1)
    sustainable: bool             # can this intervention be maintained?
    years_to_exhaustion: float    # time until budget consumed by overhead


def compute_stability(project: ClimateProject,
                      scenario: Scenario) -> StabilityMetrics:
    """
    Compute stability metrics for a climate finance intervention.

    A project is sustainable only if:
      1. Overhead < useful work delivered (stability_ratio < 1)
      2. Net energy is positive (Gibbs > 0)
    """
    de = compute_dollar_energy(scenario)

    annual_USD = (project.annual_budget_low_USD +
                  project.annual_budget_high_USD) / 2.0

    if math.isinf(de["total_MJ_per_dollar"]):
        return StabilityMetrics(
            maintenance_cost_MJ=float('inf'),
            restoration_rate_MJ=0.0,
            stability_ratio=float('inf'),
            sustainable=False,
            years_to_exhaustion=0.0,
        )

    total_energy = annual_USD * de["total_MJ_per_dollar"]
    overhead_energy = total_energy - (annual_USD * de["E_base_MJ"])
    useful_energy = annual_USD * de["E_base_MJ"]

    ratio = overhead_energy / useful_energy if useful_energy > 0 else float('inf')

    cap_USD = (project.capitalization_low_USD +
               project.capitalization_high_USD) / 2.0
    if overhead_energy > 0:
        years = (cap_USD * de["E_base_MJ"]) / overhead_energy
    else:
        years = float('inf')

    return StabilityMetrics(
        maintenance_cost_MJ=overhead_energy,
        restoration_rate_MJ=useful_energy,
        stability_ratio=ratio,
        sustainable=(ratio < 1.0),
        years_to_exhaustion=years,
    )


# ═══════════════════════════════════════════════════════════════
# PHASE BOUNDARY DETECTION
# ═══════════════════════════════════════════════════════════════
# From computational_thermodynamics.py:
# Energetic susceptibility diverges at transitions.

def phase_boundary_susceptibility(scenario: Scenario,
                                  perturbation: float = 0.01) -> float:
    """
    Detect where small changes in recycling fraction cause
    the system to flip from sustainable to divergent.

    Returns d(stability_multiplier)/d(r) — diverges at r=1.
    """
    r = scenario.recursive_r
    if r >= 1.0:
        return float('inf')

    r_plus = min(r + perturbation, 0.999)
    r_minus = max(r - perturbation, 0.0)

    mult_plus = 1.0 / (1.0 - r_plus)
    mult_minus = 1.0 / (1.0 - r_minus)

    return (mult_plus - mult_minus) / (r_plus - r_minus)


# ═══════════════════════════════════════════════════════════════
# STRESS CASCADE
# ═══════════════════════════════════════════════════════════════
# From lcea_analysis.py:
# E_ego is not absorbed — it converts into systemic stress
# which induces cascading failures.

def systemic_stress(E_ego: float, stress_function: str = "linear") -> float:
    """
    Stress conversion: Psi = f(E_ego)

    Parameters:
        E_ego: overhead energy injection (MJ)
        stress_function: 'linear', 'sqrt', or 'log'

    Returns:
        Dimensionless systemic stress level.
    """
    if stress_function == "sqrt":
        return math.sqrt(E_ego)
    elif stress_function == "log":
        return math.log1p(E_ego)
    return E_ego


def error_probability(beta: float, psi: float) -> float:
    """
    Error probability from systemic stress.
    P_error ~ exp(beta * Psi)

    Parameters:
        beta: stress-to-dissipation coupling (1/MJ)
        psi: systemic stress level

    Returns:
        Probability of misallocation, fraud, or diversion.
    """
    exponent = beta * psi
    if exponent > 700:
        return 1.0
    return min(1.0, math.exp(exponent))


def total_systemic_waste(E_ego: float, E_narrative: float,
                         E_lobby: float, E_surveillance: float) -> float:
    """E_waste = E_ego + E_narrative + E_lobby + E_surveillance"""
    return E_ego + E_narrative + E_lobby + E_surveillance


# ═══════════════════════════════════════════════════════════════
# DELUSION FILTER
# ═══════════════════════════════════════════════════════════════
# From ai_delusion_econ_checker.py:
# Flags narrative claims that violate physical constraints.

DELUSION_PATTERNS = {
    "hierarchy": [r"\btop[- ]?down\b", r"\bmanagement\b", r"\bchain of command\b"],
    "corporation": [r"\bcompany\b", r"\bcorporation\b", r"\bshareholder\b"],
    "efficiency": [r"\befficien(?:cy|t)\b", r"\bmaxim(?:ize|ization)\b", r"\bthroughput\b"],
    "optimization": [r"\boptimi[sz]e\b", r"\bperformance\b"],
    "productivity": [r"\bproductivit(?:y|ies)\b", r"\boutput\b"],
    "economics": [r"\beconomic(?:s|al)?\b", r"\bprofit\b", r"\bmarket\b", r"\bprice\b"],
    "permanence": [r"\bpermanent(?:ly)?\b", r"\bforever\b", r"\bindefinite(?:ly)?\b"],
    "net_zero": [r"\bnet[- ]?zero\b", r"\bcarbon[- ]?neutral\b"],
}


def extract_delusions(text: str) -> Counter:
    """Count narrative delusion pattern matches in claim text."""
    text_lower = text.lower()
    counts = Counter()
    for concept, patterns in DELUSION_PATTERNS.items():
        for pat in patterns:
            counts[concept] += len(re.findall(pat, text_lower))
    return counts


def plausibility_score(text: str) -> dict:
    """
    Plausibility flags (0 = plausible, 1 = questionable).

    Flags:
        efficiency_implausible: claims >100% efficiency
        profit_absolute: "profit always/never" language
        permanence_unphysical: claims permanent sequestration
        net_zero_unaudited: claims net-zero without energy audit
    """
    flags = {}

    flags["efficiency_implausible"] = (
        1 if re.search(
            r"(?:efficiency|throughput).{0,10}(?:>|\bmore than\b)\s*100", text
        ) else 0
    )

    flags["profit_absolute"] = (
        1 if re.search(r"\bprofit\b.*(?:\balways\b|\bnever\b)", text) else 0
    )

    flags["permanence_unphysical"] = (
        1 if re.search(
            r"\bpermanent(?:ly)?\b.*(?:sequest|remov|stor)", text, re.IGNORECASE
        ) else 0
    )

    flags["net_zero_unaudited"] = (
        1 if re.search(
            r"\bnet[- ]?zero\b", text, re.IGNORECASE
        ) and not re.search(
            r"\benergy audit\b|\bfull[- ]?cycle\b|\bscope [123]\b", text, re.IGNORECASE
        ) else 0
    )

    return flags


# ═══════════════════════════════════════════════════════════════
# SIX SIGMA CTQ — CLIMATE INTERVENTION TOLERANCES
# ═══════════════════════════════════════════════════════════════
# From six_sigma_audit.py:
# Critical-to-quality variables with hard physical limits.

TOLERANCES = {
    # key: (direction, limit, description)
    "waste_factor":      ("le", 0.30, "Financial overhead as fraction of total energy"),
    "carbon_ratio":      ("ge", 1.00, "Sequestered CO2 / emitted CO2 must exceed 1"),
    "reversibility":     ("ge", 0.50, "Fraction of intervention that can be undone"),
    "consent_fraction":  ("ge", 0.80, "Fraction of affected populations consulted"),
    "measurement_error": ("le", 0.20, "Uncertainty in claimed sequestration"),
    "abort_capability":  ("ge", 0.10, "Ability to stop and reverse if wrong"),
}


def _in_spec(value: float, direction: str, limit: float) -> bool:
    if direction == "ge":
        return value >= limit
    return value <= limit


def defect_rate(state: Dict[str, float]) -> dict:
    """
    Fraction of CTQ variables out of tolerance.
    """
    results = {}
    defects = 0
    total = 0
    for key, (direction, limit, desc) in TOLERANCES.items():
        val = state.get(key, 0.0)
        passed = _in_spec(val, direction, limit)
        results[key] = {
            "value": val, "limit": limit,
            "direction": direction, "pass": passed,
            "description": desc,
        }
        if not passed:
            defects += 1
        total += 1
    return {
        "details": results,
        "defects": defects,
        "total": total,
        "defect_rate": defects / total if total else 0.0,
    }


def process_capability(state: Dict[str, float]) -> dict:
    """
    Cp analog: how far each variable sits from its spec limit.
    Cp > 0 = in spec, Cp < 0 = out of spec.
    """
    caps = {}
    for key, (direction, limit, _desc) in TOLERANCES.items():
        val = state.get(key, 0.0)
        if direction == "ge":
            margin = val - limit
        else:
            margin = limit - val
        range_est = max(abs(limit), 0.01)
        cp = margin / range_est
        caps[key] = {"value": val, "margin": margin, "cp": round(cp, 3)}
    return caps


# ═══════════════════════════════════════════════════════════════
# GEOMETRIC SERIES EXPLORER
# ═══════════════════════════════════════════════════════════════

def explore_recycling_fraction(E_base: float = 6.0,
                               subtotal: float = 13.7,
                               r_range: Optional[List[float]] = None
                               ) -> List[Tuple[float, float, float]]:
    """
    Show how total energy scales with recycling fraction r.
    Demonstrates approach to divergence.

    Returns list of (r, total_MJ, multiplier) tuples.
    """
    if r_range is None:
        r_range = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5,
                   0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]

    results = []
    for r in r_range:
        if r >= 1.0:
            results.append((r, float('inf'), float('inf')))
        else:
            total = subtotal / (1.0 - r)
            multiplier = total / E_base
            results.append((r, total, multiplier))
    return results


# ═══════════════════════════════════════════════════════════════
# NEGATIVE EROI DETECTOR
# ═══════════════════════════════════════════════════════════════

def check_negative_eroi(layer_r_values: List[float]) -> dict:
    """
    Check if any overhead layer has r >= 1.0.
    This is the "intermediaries consume more than the project
    receives" condition.
    """
    total_r = sum(layer_r_values)
    max_r = max(layer_r_values) if layer_r_values else 0.0

    return {
        "any_layer_exceeds_1": max_r >= 1.0,
        "total_r_exceeds_1": total_r >= 1.0,
        "max_layer_r": max_r,
        "total_r": total_r,
        "verdict": (
            "NEGATIVE EROI: overhead exceeds project energy"
            if total_r >= 1.0
            else "Positive EROI at layer level (recursive effects may still push negative)"
        ),
    }


# ═══════════════════════════════════════════════════════════════
# BREAKEVEN FINDER
# ═══════════════════════════════════════════════════════════════

def find_breakeven_r(project: ClimateProject, E_base: float = 6.0,
                     subtotal: float = 13.7) -> Optional[float]:
    """
    Find recycling fraction r where funding CO2 = claimed sequestration.

    If claimed = 0 (SAI), returns 0.0 (always net negative).
    If no breakeven exists, returns None.
    """
    if project.claimed_annual_CO2_tonnes <= 0:
        return 0.0

    target_CO2_kg = project.claimed_annual_CO2_tonnes * 1000.0
    annual_USD = (project.annual_budget_low_USD +
                  project.annual_budget_high_USD) / 2.0

    numerator = annual_USD * subtotal * CO2_PER_MJ_KG
    denominator = target_CO2_kg

    ratio = numerator / denominator
    r_breakeven = 1.0 - ratio

    if r_breakeven < 0.0 or r_breakeven >= 1.0:
        return None
    return r_breakeven


# ═══════════════════════════════════════════════════════════════
# HANDSHAKE DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════
# From six_sigma_audit.py: combined narrative + field diagnostic.

def handshake(claim_text: str = "",
              ctq_state: Optional[Dict[str, float]] = None,
              project: Optional[ClimateProject] = None,
              scenario: Optional[Scenario] = None) -> dict:
    """
    Combined diagnostic: narrative delusions + field physics + verdict.

    Parameters:
        claim_text: marketing/PR text to scan for delusions
        ctq_state: dict of CTQ variable values
        project: ClimateProject to audit
        scenario: financial routing scenario

    Returns:
        Dict with narrative analysis, field analysis, and verdict.
    """
    result = {"narrative": None, "field": None,
              "energy": None, "verdict": "NOMINAL"}
    flags = []

    if claim_text:
        delusions = dict(extract_delusions(claim_text))
        plausibility = plausibility_score(claim_text)
        total_noise = sum(delusions.values())
        result["narrative"] = {
            "delusion_counts": delusions,
            "plausibility_flags": plausibility,
            "total_noise": total_noise,
        }
        if any(v == 1 for v in plausibility.values()):
            flags.append("PLAUSIBILITY_FAIL")
        if total_noise > 5:
            flags.append("HIGH_NOISE")

    if ctq_state is not None:
        dr = defect_rate(ctq_state)
        cp = process_capability(ctq_state)
        result["field"] = {
            "defect_rate": dr,
            "process_capability": cp,
        }
        if dr["defect_rate"] > 0.5:
            flags.append("MAJORITY_OUT_OF_SPEC")

    if project is not None and scenario is not None:
        audit = compute_project_audit(project, scenario)
        stability = compute_stability(project, scenario)
        result["energy"] = {
            "audit": audit,
            "stability": {
                "maintenance_MJ": stability.maintenance_cost_MJ,
                "restoration_MJ": stability.restoration_rate_MJ,
                "ratio": stability.stability_ratio,
                "sustainable": stability.sustainable,
                "years_to_exhaustion": stability.years_to_exhaustion,
            },
        }
        if not stability.sustainable:
            flags.append("UNSUSTAINABLE")
        if audit["dollar_energy"]["divergent"]:
            flags.append("DIVERGENT_SERIES")

    if flags:
        result["verdict"] = "ALERT"
    result["flags"] = flags
    return result


# ═══════════════════════════════════════════════════════════════
# FULL SIMULATION
# ═══════════════════════════════════════════════════════════════

def run_full_audit() -> dict:
    """Run complete audit across all scenarios and projects."""
    results = {}
    for proj_key, project in PROJECTS.items():
        results[proj_key] = {}
        for scen_key, scenario in SCENARIOS.items():
            results[proj_key][scen_key] = compute_project_audit(
                project, scenario
            )
    return results


# ═══════════════════════════════════════════════════════════════
# PRINT ENGINE
# ═══════════════════════════════════════════════════════════════

def print_dollar_anatomy():
    """Print the full energy anatomy of a dollar."""
    print()
    print("=" * 65)
    print("THE ENERGY ANATOMY OF A DOLLAR")
    print("Recursive metabolic cost of financial system overhead")
    print("=" * 65)
    print()

    for scenario in SCENARIOS.values():
        result = compute_dollar_energy(scenario)

        print(f"  {scenario.name}")
        print(f"  {'─' * 55}")
        print(f"    Base energy:              {result['E_base_MJ']:>8.1f} MJ")

        if scenario.layer_positions != "none":
            for lname, ldata in result["layer_breakdown"].items():
                if ldata["MJ_added"] > 0:
                    print(f"    + {lname:20s}      {ldata['MJ_added']:>8.2f} MJ"
                          f"  (r={ldata['r_fraction']:.2f})")

            print(f"    {'─' * 40}")
            print(f"    Subtotal:                 {result['subtotal_before_recursion_MJ']:>8.1f} MJ")
            print(f"    Recursive r:              {result['recursive_r']:>8.2f}")
            print(f"    Recursive multiplier:     {result['recursive_multiplier']:>8.2f}x")

        if math.isinf(result["total_MJ_per_dollar"]):
            print(f"    TOTAL:                    DIVERGENT (infinite)")
        else:
            print(f"    TOTAL:                    {result['total_MJ_per_dollar']:>8.1f} MJ per dollar")

        print(f"    Overall multiplier:       {result['overall_multiplier']:>8.1f}x base energy")
        print()


def print_geometric_series():
    """Print the geometric series table showing divergence."""
    print()
    print("=" * 65)
    print("GEOMETRIC SERIES: RECYCLING FRACTION vs TOTAL ENERGY")
    print("E_base = 6.0 MJ, Subtotal = 13.7 MJ (typical climate finance)")
    print("=" * 65)
    print()
    print(f"    {'r':>6s}  {'E_total (MJ)':>14s}  {'Multiplier':>12s}  {'Status'}")
    print(f"    {'─'*6}  {'─'*14}  {'─'*12}  {'─'*20}")

    for r, total, mult in explore_recycling_fraction():
        if math.isinf(total):
            print(f"    {r:>6.2f}  {'DIVERGENT':>14s}  {'INFINITE':>12s}"
                  f"  SYSTEM IS NET SINK")
        else:
            status = ""
            if r >= 0.7:
                status = "<- carbon speculation"
            elif r >= 0.5:
                status = "<- typical climate finance"
            elif r >= 0.3:
                status = "<- efficient finance"
            print(f"    {r:>6.2f}  {total:>14.1f}  {mult:>12.1f}x  {status}")

    print()
    print("  As r -> 1.0, energy cost -> infinity.")
    print("  The financial system's own metabolism")
    print("  consumes the project's energy budget.")
    print()


def print_negative_eroi_analysis():
    """Print EROI analysis for each scenario."""
    print()
    print("=" * 65)
    print("NEGATIVE EROI DETECTION")
    print("Does any layer consume more energy than it processes?")
    print("=" * 65)
    print()

    for pos_label, pos in [("Conservative", "low"),
                           ("Mid-range", "mid"),
                           ("Extractive", "high")]:
        E_base = 6.0
        r_values = [layer_energy(layer, pos, E_base) / E_base
                    for layer in OVERHEAD_LAYERS]
        names = [layer.name for layer in OVERHEAD_LAYERS]

        result = check_negative_eroi(r_values)

        print(f"  {pos_label} case:")
        for name, r in zip(names, r_values):
            flag = " <- EXCEEDS 1.0" if r >= 1.0 else ""
            print(f"    {name:20s}  r = {r:.3f}{flag}")
        print(f"    {'─' * 40}")
        print(f"    Total r:            {result['total_r']:.3f}")
        print(f"    Verdict:            {result['verdict']}")
        print()


def print_paradigm_matrix():
    """Print the alternative computing paradigm coverage matrix."""
    print()
    print("=" * 65)
    print("ALTERNATIVE COMPUTING PARADIGM MATRIX")
    print("What binary carbon accounting erases")
    print("=" * 65)
    print()
    print(f"  {'paradigm':<15s}", end="")
    for d in PARADIGM_DOMAINS:
        print(f"{d:>10s}", end="")
    print(f"  {'coverage':>8s}")
    print(f"  {'─'*15}", end="")
    for _ in PARADIGM_DOMAINS:
        print(f"{'─'*10}", end="")
    print(f"  {'─'*8}")

    for name, row in PARADIGM_MATRIX.items():
        print(f"  {name:<15s}", end="")
        for val in row:
            print(f"{'yes':>10s}" if val else f"{'·':>10s}", end="")
        print(f"  {sum(row):>5d}/5")

    print()
    print("  Domain coverage:")
    for d in PARADIGM_DOMAINS:
        c = domain_coverage(d)
        print(f"    {d:<12s}: {c}/7 paradigms")
    print()
    print("  Reservoir computing covers ALL domains — it sees the")
    print("  coupled dynamical system that single-arrow models miss.")
    print("  Memristive covers only electric — history-dependence")
    print("  requires a physical medium that retains state.")
    print()


def print_project_audits():
    """Print full audits for all project/scenario combinations."""
    results = run_full_audit()

    for proj_key, project in PROJECTS.items():
        print()
        print("=" * 65)
        print(f"PROJECT: {project.name.upper()}")
        print(f"  {project.description}")
        print("=" * 65)

        if project.claimed_annual_CO2_tonnes > 0:
            print(f"  Claimed annual sequestration:"
                  f" {project.claimed_annual_CO2_tonnes:,.0f} tonnes CO2")
        else:
            print(f"  Claimed sequestration: NONE (masking only)")
        print()

        for scen_key, scenario in SCENARIOS.items():
            audit = results[proj_key][scen_key]
            de = audit["dollar_energy"]

            print(f"  Scenario: {scenario.name}")
            print(f"  {'─' * 55}")

            if math.isinf(de["total_MJ_per_dollar"]):
                print(f"    Energy per dollar: DIVERGENT")
                print(f"    Multiplier: INFINITE")
            else:
                print(f"    Energy per dollar:"
                      f" {de['total_MJ_per_dollar']:.1f} MJ"
                      f"  ({de['overall_multiplier']:.1f}x)")

            for label in ["annual_budget_low", "annual_budget_high"]:
                pc = audit["project_costs"][label]
                tag = "low" if "low" in label else "high"

                if math.isinf(pc["CO2_tonnes"]):
                    print(f"    Annual budget ({tag}):"
                          f" ${pc['USD']/1e6:.0f}M -> INFINITE CO2")
                else:
                    print(f"    Annual budget ({tag}):"
                          f" ${pc['USD']/1e6:.0f}M ->"
                          f" {pc['energy_TJ']:.0f} TJ ->"
                          f" {pc['CO2_tonnes']:,.0f} t CO2")

            if project.claimed_annual_CO2_tonnes > 0:
                frac = audit["funding_CO2_as_fraction_of_claimed"]
                for bkey, blabel in [("low_budget", "low"),
                                     ("high_budget", "high")]:
                    f = frac[bkey]
                    if math.isinf(f):
                        print(f"    Funding CO2 ({blabel} budget)"
                              f" = INFINITE x claimed")
                    else:
                        print(f"    Funding CO2 ({blabel} budget)"
                              f" = {f:.2f}x claimed annual sequestration")
                        if f >= 1.0:
                            print(f"      ## FUNDING ALONE EMITS MORE"
                                  f" THAN PROJECT CLAIMS ##")

            print()

        r_break = find_breakeven_r(project)
        if project.claimed_annual_CO2_tonnes > 0:
            if r_break is None:
                print(f"  BREAKEVEN: Funding emissions EXCEED claimed benefit")
                print(f"             at ALL recycling fractions.")
            elif r_break <= 0.0:
                print(f"  BREAKEVEN: r = 0 (only direct action, zero overhead)")
            else:
                print(f"  BREAKEVEN r = {r_break:.3f}")
                print(f"    Funding CO2 = claimed CO2 when r = {r_break:.3f}")
                if r_break < 0.3:
                    print(f"    This requires financial efficiency that"
                          f" DOES NOT EXIST")
                    print(f"    in any known climate finance structure.")
        else:
            print(f"  BREAKEVEN: N/A — project claims no sequestration.")
            print(f"  All funding emissions are pure additional cost.")

        print()


def print_stability_analysis():
    """Print stability metrics for all project/scenario combinations."""
    print()
    print("=" * 65)
    print("STABILITY ANALYSIS")
    print("maintenance / restoration ratio (want < 1.0)")
    print("=" * 65)
    print()

    for proj_key, project in PROJECTS.items():
        print(f"  {project.name}:")
        for scen_key, scenario in SCENARIOS.items():
            sm = compute_stability(project, scenario)
            status = "SUSTAINABLE" if sm.sustainable else "UNSUSTAINABLE"
            if math.isinf(sm.stability_ratio):
                print(f"    {scenario.name:<35s}  ratio=INF  {status}")
            else:
                print(f"    {scenario.name:<35s}"
                      f"  ratio={sm.stability_ratio:.2f}  {status}")
        print()


def print_ctq_audit():
    """Print Six Sigma CTQ audit for both projects."""
    print()
    print("=" * 65)
    print("SIX SIGMA CTQ AUDIT")
    print("Critical-to-Quality variables for climate interventions")
    print("=" * 65)
    print()

    project_ctq = {
        "ocean_timber": {
            "waste_factor": 0.65,
            "carbon_ratio": 0.35,
            "reversibility": 0.0,
            "consent_fraction": 0.0,
            "measurement_error": 0.50,
            "abort_capability": 0.0,
        },
        "sai": {
            "waste_factor": 0.80,
            "carbon_ratio": 0.0,
            "reversibility": 0.0,
            "consent_fraction": 0.0,
            "measurement_error": 0.70,
            "abort_capability": 0.0,
        },
    }

    for proj_key, state in project_ctq.items():
        project = PROJECTS[proj_key]
        print(f"  {project.name}:")

        dr = defect_rate(state)
        cp = process_capability(state)

        for key, info in dr["details"].items():
            status = "PASS" if info["pass"] else "FAIL"
            cp_val = cp[key]["cp"]
            print(f"    {key:22s}  val={info['value']:.2f}"
                  f"  limit {info['direction']} {info['limit']:.2f}"
                  f"  Cp={cp_val:+.3f}  [{status}]")

        print(f"    {'─' * 50}")
        print(f"    Defect rate: {dr['defect_rate']:.0%}"
              f" ({dr['defects']}/{dr['total']})")
        print()


def print_verdicts():
    """Print thermodynamic verdicts."""
    print()
    print("=" * 65)
    print("THERMODYNAMIC VERDICTS")
    print("=" * 65)
    print()
    print("  1. The financial system is a heat engine that converts")
    print("     primary energy into claims on future energy.")
    print()
    print("  2. When you route a dollar through this engine to fund")
    print("     a climate project, the engine's own thermal losses")
    print("     exceed the project's energetic benefit in most")
    print("     configurations.")
    print()
    print("  3. The margin stack (r2) can exceed 1.0 in extractive")
    print("     configurations. This is the negative EROI condition:")
    print("     intermediaries consume more energy per dollar than")
    print("     the project receives.")
    print()
    print("  4. The recursive nature of overhead (each layer generates")
    print("     economic activity subject to all other layers) creates")
    print("     a geometric series that approaches divergence as the")
    print("     financial system becomes more complex.")
    print()
    print("  5. Binary carbon accounting (sequestered=1, not=0) erases")
    print("     the continuous physics across 7 paradigms and 5 domains.")
    print("     The paradigm matrix shows 35 cells of physical reality")
    print("     that a yes/no ledger cannot represent.")
    print()
    print("  6. The only climate interventions with closed energy")
    print("     budgets are:")
    print()
    print("       a. Direct action (no financial intermediation)")
    print("       b. Negative cost (stop subsidizing extraction)")
    print("       c. Regulatory prohibition (no transaction needed)")
    print()
    print("  7. The dollar is not neutral. The dollar is a unit of")
    print("     extraction wrapped in abstraction layers designed")
    print("     to make the extraction invisible.")
    print()
    print("=" * 65)
    print("  Leave the forest standing. It already works.")
    print("  It doesn't need funding. It doesn't need a pitch deck.")
    print("  It just needs to not be cut down.")
    print("  But 'don't cut it down' has no revenue model.")
    print("  And that's the whole problem.")
    print("=" * 65)
    print()


# ═══════════════════════════════════════════════════════════════
# COUPLING STATE — INTER-LAYER INTERFACE
# ═══════════════════════════════════════════════════════════════

def coupling_state() -> dict:
    """
    Export state dict for cascade engine integration.
    Follows earth-systems-physics convention.
    """
    typical = compute_dollar_energy(SCENARIOS["typical_climate"])
    return {
        "MJ_per_dollar_direct": MJ_PER_DOLLAR_GLOBAL,
        "MJ_per_dollar_typical_climate": typical["total_MJ_per_dollar"],
        "overhead_multiplier": typical["overall_multiplier"],
        "recursive_r": typical["recursive_r"],
        "divergent": typical["divergent"],
        "paradigm_coverage_total": sum(
            paradigm_coverage(p) for p in PARADIGM_MATRIX
        ),
        "paradigm_coverage_max": 5 * len(PARADIGM_MATRIX),
    }


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print_dollar_anatomy()
    print_geometric_series()
    print_negative_eroi_analysis()
    print_paradigm_matrix()
    print_stability_analysis()
    print_ctq_audit()
    print_project_audits()
    print_verdicts()
