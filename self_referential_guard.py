# self_referential_guard.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
self_referential_guard.py
─────────────────────────
Detects self-referential reasoning loops in any system
(economic models, AI inference chains, coupled simulations).

Core idea: a variable is GROUNDED if it traces back to a
physical measurement. A variable is UNGROUNDED if every
path through its dependency graph eventually cycles back
to itself with no physical anchor.

CC0 — No rights reserved. stdlib only.
"""

import math
from typing import List, Tuple, Dict, Set, Optional


# ═══════════════════════════════════════════════════════════
# LAYER 0: DEPENDENCY GRAPH — cycle + grounding detection
# ═══════════════════════════════════════════════════════════

class DependencyGraph:
    """
    Nodes = variables/claims/measurements.
    Edges = "A depends on B" (A uses B as input).
    Anchors = nodes marked as physical ground truth.

    A cycle with no anchor inside it = self-referential loop.
    A cycle WITH an anchor = legitimate feedback (thermostat).
    """

    def __init__(self):
        self.edges: Dict[str, Set[str]] = {}       # node -> set of inputs
        self.anchors: Set[str] = set()              # physically grounded nodes
        self.anchor_reasons: Dict[str, str] = {}    # why each anchor is trusted

    def add_variable(self, name: str, depends_on: List[str]):
        self.edges[name] = set(depends_on)
        for dep in depends_on:
            if dep not in self.edges:
                self.edges[dep] = set()

    def mark_anchor(self, name: str, reason: str = "physical measurement"):
        """Mark a node as grounded in physical reality."""
        self.anchors.add(name)
        self.anchor_reasons[name] = reason
        if name not in self.edges:
            self.edges[name] = set()

    def find_all_cycles(self) -> List[List[str]]:
        """Find all distinct cycles in the dependency graph."""
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        stack: List[str] = []
        stack_set: Set[str] = set()

        def dfs(node: str):
            visited.add(node)
            stack.append(node)
            stack_set.add(node)
            for neighbor in self.edges.get(node, set()):
                if neighbor in stack_set:
                    # extract cycle
                    idx = stack.index(neighbor)
                    cycle = stack[idx:]
                    # normalize: start from min element for dedup
                    min_idx = cycle.index(min(cycle))
                    normalized = cycle[min_idx:] + cycle[:min_idx]
                    if normalized not in cycles:
                        cycles.append(normalized)
                elif neighbor not in visited:
                    dfs(neighbor)
            stack.pop()
            stack_set.remove(node)

        for node in list(self.edges.keys()):
            if node not in visited:
                dfs(node)
        return cycles

    def classify_cycle(self, cycle: List[str]) -> Dict:
        """
        Classify a cycle as:
          - GROUNDED_FEEDBACK: cycle contains an anchor (legitimate)
          - WEAKLY_GROUNDED:   cycle reaches an anchor externally
          - SELF_REFERENTIAL:  cycle has NO anchor (hazard)
        """
        cycle_set = set(cycle)
        anchors_in_cycle = cycle_set & self.anchors
        if anchors_in_cycle:
            return {
                "cycle": cycle,
                "status": "GROUNDED_FEEDBACK",
                "anchors": {a: self.anchor_reasons[a] for a in anchors_in_cycle},
                "hazard": False,
            }
        # check if ANY node in cycle can reach an anchor
        # through a path that doesn't go through the cycle
        external_anchors = self._find_external_anchors(cycle_set)
        if external_anchors:
            return {
                "cycle": cycle,
                "status": "WEAKLY_GROUNDED",
                "external_anchors": external_anchors,
                "hazard": False,
                "warning": "Grounding is indirect — verify anchor path",
            }
        return {
            "cycle": cycle,
            "status": "SELF_REFERENTIAL",
            "anchors": {},
            "hazard": True,
            "warning": "No physical anchor found in or reachable from cycle",
        }

    def _find_external_anchors(self, cycle_set: Set[str]) -> Dict[str, str]:
        """Check if cycle nodes reach anchors outside the cycle."""
        found: Dict[str, str] = {}
        for node in cycle_set:
            visited: Set[str] = set()
            queue: List[str] = [node]
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                if current in self.anchors and current not in cycle_set:
                    found[current] = self.anchor_reasons[current]
                for dep in self.edges.get(current, set()):
                    # only follow edges outside the cycle
                    if dep not in cycle_set and dep not in visited:
                        queue.append(dep)
        return found

    def audit(self) -> Dict:
        """Full audit: find all cycles, classify each."""
        cycles = self.find_all_cycles()
        results: Dict = {
            "total_nodes": len(self.edges),
            "total_anchors": len(self.anchors),
            "cycles_found": len(cycles),
            "hazards": [],
            "grounded": [],
            "weakly_grounded": [],
        }
        for cycle in cycles:
            classification = self.classify_cycle(cycle)
            if classification["status"] == "SELF_REFERENTIAL":
                results["hazards"].append(classification)
            elif classification["status"] == "WEAKLY_GROUNDED":
                results["weakly_grounded"].append(classification)
            else:
                results["grounded"].append(classification)
        return results


# ═══════════════════════════════════════════════════════════
# LAYER 1: FALSE PRECISION DETECTOR
# ═══════════════════════════════════════════════════════════

def false_precision_check(
    value: float,
    uncertainty: float,
    reported_decimals: int,
    label: str = "",
) -> Dict:
    """
    Detects when reported precision exceeds measurement capability.

    Economics example: GDP reported to 9 significant figures
    when measurement uncertainty is ±3%.
    """
    reported_precision = 10 ** (-reported_decimals)
    magnitude = abs(value) if value != 0 else 1.0
    relative_uncertainty = uncertainty / magnitude

    # how many decimal places are actually justified?
    if uncertainty > 0:
        justified_decimals = max(0, -math.floor(math.log10(uncertainty)))
    else:
        # can't check without uncertainty
        justified_decimals = reported_decimals

    excess = reported_decimals - justified_decimals

    return {
        "label": label or f"value={value}",
        "reported_precision": reported_precision,
        "actual_uncertainty": uncertainty,
        "relative_uncertainty_pct": round(relative_uncertainty * 100, 2),
        "justified_decimals": justified_decimals,
        "excess_precision": excess,
        "hazard": excess > 0,
        "warning": (
            f"Reporting {reported_decimals} decimals but only "
            f"{justified_decimals} justified (±{uncertainty})"
            if excess > 0 else "OK"
        ),
    }


# ═══════════════════════════════════════════════════════════
# LAYER 2: MODEL-VS-REALITY VOLATILITY CHECK
# ═══════════════════════════════════════════════════════════

def model_reality_gap(
    data: List[float],
    model_assumes_std: float,
    window: int = 5,
    label: str = "",
) -> Dict:
    """
    The hazard isn't volatility itself — it's the GAP between
    what the model assumes and what the data shows.

    A river can legitimately flood. The hazard is a flood model
    that assumes the river doesn't flood.
    """
    if len(data) < window:
        return {"hazard": False, "warning": "Insufficient data", "label": label}

    max_observed_std = 0.0
    worst_window = 0
    for i in range(len(data) - window + 1):
        w = data[i:i + window]
        mean = sum(w) / window
        variance = sum((x - mean) ** 2 for x in w) / window
        std = math.sqrt(variance)
        if std > max_observed_std:
            max_observed_std = std
            worst_window = i

    ratio = (
        max_observed_std / model_assumes_std
        if model_assumes_std > 0 else float("inf")
    )

    return {
        "label": label,
        "model_assumed_std": model_assumes_std,
        "max_observed_std": round(max_observed_std, 6),
        "reality_model_ratio": round(ratio, 2),
        "worst_window_start": worst_window,
        "hazard": ratio > 2.0,
        "warning": (
            f"Reality is {ratio:.1f}x more volatile than model assumes "
            f"(window {worst_window})"
            if ratio > 2.0 else "Model assumption consistent with data"
        ),
    }


# ═══════════════════════════════════════════════════════════
# LAYER 3: AXIOM GROUNDING CHECK
# ═══════════════════════════════════════════════════════════

def axiom_grounding_check(axioms: Dict[str, Dict]) -> List[Dict]:
    """
    Takes a dict of axioms, each with:
      - "statement":        human-readable claim
      - "testable":         bool — can this be falsified by measurement?
      - "physical_unit":    str or None — does it map to SI / physical unit?
      - "conservation_law": str or None — which conservation law constrains it?

    Axioms that are not testable AND have no physical unit AND
    ignore conservation laws = ungrounded.
    """
    results = []
    for name, props in axioms.items():
        testable = props.get("testable", False)
        has_unit = props.get("physical_unit") is not None
        has_conservation = props.get("conservation_law") is not None
        score = sum([testable, has_unit, has_conservation])
        results.append({
            "axiom": name,
            "statement": props.get("statement", ""),
            "testable": testable,
            "physical_unit": props.get("physical_unit"),
            "conservation_law": props.get("conservation_law"),
            "grounding_score": score,   # 0-3
            "status": (
                "GROUNDED" if score == 3
                else "PARTIAL" if score >= 1
                else "UNGROUNDED"
            ),
            "hazard": score == 0,
        })
    return results


# ═══════════════════════════════════════════════════════════
# EXAMPLE AXIOMS — module-level catalog of grounding examples
# ═══════════════════════════════════════════════════════════
#
# Pulled out to module level so tests, demos, and the
# ai_reference exporter can all reference the same data.

EXAMPLE_AXIOMS = {
    "conservation_of_energy": {
        "statement": "Energy cannot be created or destroyed",
        "testable": True,
        "physical_unit": "joule",
        "conservation_law": "first law of thermodynamics",
    },
    "fractional_reserve": {
        "statement": "Banks can lend more money than they hold in deposits",
        "testable": False,   # a policy choice, not a measurement
        "physical_unit": None,
        "conservation_law": None,  # violates conservation — creates from nothing
    },
    "efficient_market": {
        "statement": "Asset prices reflect all available information",
        "testable": False,   # unfalsifiable as stated
        "physical_unit": None,
        "conservation_law": None,
    },
    "crystal_navigation": {
        "statement": (
            "Fe3+ defects in quartz polarize sunlight for bearing "
            "determination"
        ),
        "testable": True,
        "physical_unit": "degrees (angular bearing)",
        "conservation_law": "electromagnetic — Malus's law",
    },
    "landscape_encoding": {
        "statement": (
            "Three-tree cluster plantings encode experimental "
            "observations across generations"
        ),
        "testable": True,
        "physical_unit": "meters (spatial geometry)",
        "conservation_law": "information conservation in physical substrate",
    },
}


# ═══════════════════════════════════════════════════════════
# DEMO: economics as a self-referential system
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("SELF-REFERENTIAL GUARD — DEMO")
    print("=" * 60)

    # ── 1. Dependency graph: money creation ──
    print("\n── DEPENDENCY GRAPH: MONETARY SYSTEM ──")
    g = DependencyGraph()

    # the loop: credit creates money, money enables credit,
    # asset prices justify credit, credit inflates asset prices
    g.add_variable("bank_credit",    ["asset_prices", "expected_gdp"])
    g.add_variable("money_supply",   ["bank_credit"])
    g.add_variable("asset_prices",   ["money_supply", "bank_credit"])
    g.add_variable("expected_gdp",   ["money_supply", "asset_prices"])

    # contrast: a thermostat (grounded feedback loop)
    g.add_variable("heater",             ["thermostat_reading"])
    g.add_variable("room_temp",          ["heater", "outside_temp"])
    g.add_variable("thermostat_reading", ["room_temp"])
    g.mark_anchor("outside_temp", "thermometer — direct physical measurement")
    g.mark_anchor("room_temp",    "thermometer — direct physical measurement")

    # contrast: indigenous navigation (grounded)
    g.add_variable(
        "crystal_bearing",
        ["solar_azimuth", "fe3_defect_response"],
    )
    g.add_variable(
        "route_decision",
        ["crystal_bearing", "star_position", "landscape_markers"],
    )
    g.mark_anchor("solar_azimuth",       "direct solar observation")
    g.mark_anchor("fe3_defect_response", "measurable polarization in quartz")
    g.mark_anchor("star_position",       "direct celestial observation")
    g.mark_anchor("landscape_markers",   "physical terrain features — persistent")

    report = g.audit()
    print(f"Nodes: {report['total_nodes']}, Anchors: {report['total_anchors']}")
    print(f"Cycles: {report['cycles_found']}")
    print(f"Hazards: {len(report['hazards'])}")
    for h in report["hazards"]:
        print(f"  SELF-REFERENTIAL: {' → '.join(h['cycle'])} → (loop)")
        print(f"    {h['warning']}")
    for gr in report["grounded"]:
        print(f"  GROUNDED: {' → '.join(gr['cycle'])} → (loop)")
        anchors = ", ".join(f"{k}: {v}" for k, v in gr["anchors"].items())
        print(f"    anchors: {anchors}")

    # ── 2. False precision: GDP ──
    print("\n── FALSE PRECISION: US GDP ──")
    gdp = false_precision_check(
        value=25_462_700_000_000,
        uncertainty=750_000_000_000,   # ±3% measurement error
        reported_decimals=0,           # reported to nearest dollar
        label="US GDP (annual)",
    )
    print(f"  {gdp['warning']}")
    print(f"  Relative uncertainty: ±{gdp['relative_uncertainty_pct']}%")

    # ── 3. Model-reality gap: inflation forecasts ──
    print("\n── MODEL VS REALITY: INFLATION ──")
    actual_inflation = [0.02, 0.02, 0.03, 0.05, 0.08, 0.09, 0.06, 0.04]
    gap = model_reality_gap(
        data=actual_inflation,
        model_assumes_std=0.005,   # Fed models assumed ~0.5% std
        window=4,
        label="CPI inflation 2019-2023",
    )
    print(f"  {gap['warning']}")
    print(f"  Model assumed std: {gap['model_assumed_std']}")
    print(f"  Observed max std:  {gap['max_observed_std']}")
    print(f"  Ratio: {gap['reality_model_ratio']}x")

    # ── 4. Axiom grounding: economics vs physics ──
    print("\n── AXIOM GROUNDING CHECK ──")
    results = axiom_grounding_check(EXAMPLE_AXIOMS)
    for r in results:
        status = r["status"]
        icon = "!" if r["hazard"] else "."
        print(f"  {icon} [{status:>10}] {r['axiom']}: {r['statement'][:60]}")
