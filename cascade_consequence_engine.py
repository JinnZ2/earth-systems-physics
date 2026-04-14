# cascade_consequence_engine.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
cascade_consequence_engine.py
─────────────────────────────
Traces secondary and tertiary effects of a goal trajectory.

Core thesis: some goals are SELF-TERMINATING — pursuing them
destroys the substrate they depend on. The cascade math proves
this without moral argument.

The goal doesn't fail because it's "wrong."
The goal fails because pursuing it generates more damage to
the goal than not pursuing it.

Architecture:
  LAYER 0: Substrate mapping — what does the goal depend on?
  LAYER 1: Action effects — how does pursuit affect substrates?
  LAYER 2: Cascade propagation — secondary/tertiary effects
  LAYER 3: Self-termination detection — does pursuit destroy
           the conditions required for success?

CC0 — No rights reserved. stdlib only.
"""

import math
from typing import Dict, List, Tuple, Set, Optional


# ═══════════════════════════════════════════════════════════
# LAYER 0: SUBSTRATE MAP
# ═══════════════════════════════════════════════════════════

class SubstrateMap:
    """
    Every goal depends on physical substrates. "Maximize GDP"
    depends on: energy, labor, water, soil, stable climate,
    transport, social cohesion.

    If pursuing the goal degrades a substrate it depends on,
    the goal is consuming its own foundation.

    Nodes:             substrates (physical things that can be measured)
    Edges:             dependencies (substrate A requires substrate B)
    Goal dependencies: which substrates the goal NEEDS
    """

    def __init__(self):
        self.substrates: Dict[str, Dict] = {}
        self.dependencies: Dict[str, Set[str]] = {}  # A depends on B
        self.goal_requires: Set[str] = set()

    def add_substrate(self, name: str, current_level: float,
                      min_viable: float, unit: str = "",
                      regeneration_rate: float = 0.0):
        """
        current_level:     present measurable state
        min_viable:        below this, substrate collapses
        regeneration_rate: natural recovery per time step
                           (0 = non-renewable)
        """
        self.substrates[name] = {
            "level": current_level,
            "min_viable": min_viable,
            "unit": unit,
            "regeneration_rate": regeneration_rate,
            "original_level": current_level,
        }
        if name not in self.dependencies:
            self.dependencies[name] = set()

    def add_dependency(self, substrate: str, depends_on: str):
        """substrate requires depends_on to function."""
        if substrate not in self.dependencies:
            self.dependencies[substrate] = set()
        self.dependencies[substrate].add(depends_on)

    def mark_goal_dependency(self, substrate: str):
        """The goal requires this substrate."""
        self.goal_requires.add(substrate)

    def get_full_dependency_tree(
        self, substrate: str, visited: Optional[Set[str]] = None,
    ) -> Set[str]:
        """All substrates that this one transitively depends on."""
        if visited is None:
            visited = set()
        if substrate in visited:
            return visited
        visited.add(substrate)
        for dep in self.dependencies.get(substrate, set()):
            self.get_full_dependency_tree(dep, visited)
        return visited

    def get_goal_full_tree(self) -> Set[str]:
        """Everything the goal transitively depends on."""
        all_deps: Set[str] = set()
        for sub in self.goal_requires:
            all_deps |= self.get_full_dependency_tree(sub)
        return all_deps


# ═══════════════════════════════════════════════════════════
# LAYER 1: ACTION EFFECTS
# ═══════════════════════════════════════════════════════════

class ActionEffect:
    """
    An action taken in pursuit of a goal. Each action has:
      - direct effects on substrates (primary)
      - a goal_progress value (how much it advances the goal)
    """

    def __init__(self, name: str, goal_progress: float):
        self.name = name
        self.goal_progress = goal_progress
        self.effects: Dict[str, float] = {}  # substrate -> delta per step

    def add_effect(self, substrate: str, delta: float):
        """
        delta > 0 = builds substrate
        delta < 0 = depletes substrate
        """
        self.effects[substrate] = delta


# ═══════════════════════════════════════════════════════════
# LAYER 2: CASCADE ENGINE
# ═══════════════════════════════════════════════════════════

class CascadeEngine:
    """
    Propagates effects through the substrate map over time.

    At each time step:
      1. Apply action effects (primary)
      2. Apply regeneration
      3. Propagate cascade: if substrate drops below min_viable,
         everything that depends on it takes damage (secondary)
      4. Propagate again from secondary damage (tertiary)
      5. Check: has the goal's own substrate been damaged MORE
         by pursuing the goal than by not pursuing it?
    """

    def __init__(self, substrate_map: SubstrateMap):
        self.smap = substrate_map
        self.history: List[Dict] = []
        self.cascade_depth_limit = 10  # prevent infinite loops

    def simulate(self, actions: List[ActionEffect],
                 steps: int = 20) -> Dict:
        """
        Run the simulation forward.
        Returns timeline + self-termination analysis.
        """
        state = {
            name: s["level"] for name, s in self.smap.substrates.items()
        }
        goal_tree = self.smap.get_goal_full_tree()
        cumulative_goal_progress = 0.0
        cumulative_goal_damage = 0.0
        self.history = []
        collapsed_substrates: Set[str] = set()
        self_termination_step: Optional[int] = None

        for step in range(steps):
            step_record: Dict = {
                "step": step,
                "state": dict(state),
                "cascades": [],
                "collapsed": set(),
                "goal_progress": 0.0,
                "goal_damage": 0.0,
            }

            # 1. apply action effects (primary)
            for action in actions:
                cumulative_goal_progress += action.goal_progress
                step_record["goal_progress"] += action.goal_progress
                for substrate, delta in action.effects.items():
                    if substrate in state:
                        state[substrate] += delta

            # 2. apply regeneration
            for name, s in self.smap.substrates.items():
                if name not in collapsed_substrates:
                    regen = s["regeneration_rate"]
                    cap = s["original_level"]
                    if regen > 0 and state[name] < cap:
                        state[name] = min(cap, state[name] + regen)

            # 3. cascade propagation
            cascade_round = 0
            new_collapses = True
            while new_collapses and cascade_round < self.cascade_depth_limit:
                new_collapses = False
                cascade_round += 1
                for name, s in self.smap.substrates.items():
                    if name in collapsed_substrates:
                        continue
                    if state[name] <= s["min_viable"]:
                        # this substrate has collapsed
                        collapsed_substrates.add(name)
                        step_record["collapsed"].add(name)
                        new_collapses = True

                        # damage everything that depends on it
                        # proportional: depend on 2 things and one
                        # collapses -> lose ~50%. Depend on 5 -> ~20%.
                        for dependent, deps in self.smap.dependencies.items():
                            if (name in deps
                                    and dependent not in collapsed_substrates):
                                dep_count = len(deps)
                                fraction_lost = 1.0 / max(dep_count, 1)
                                damage = state[dependent] * fraction_lost
                                state[dependent] -= damage
                                step_record["cascades"].append({
                                    "source": name,
                                    "target": dependent,
                                    "damage": round(damage, 4),
                                    "cascade_depth": cascade_round,
                                    "order": (
                                        "secondary" if cascade_round == 1
                                        else "tertiary" if cascade_round == 2
                                        else f"order-{cascade_round + 1}"
                                    ),
                                })

            # 4. measure goal damage
            for sub in goal_tree:
                if sub in step_record["collapsed"]:
                    cumulative_goal_damage += 1.0
                s_data = self.smap.substrates.get(sub, {})
                original = s_data.get("original_level", 1.0)
                if original > 0:
                    degradation = max(
                        0, original - state.get(sub, 0)
                    ) / original
                    step_record["goal_damage"] += degradation
                    cumulative_goal_damage += degradation * 0.1

            # 5. self-termination check
            if (self_termination_step is None and
                    cumulative_goal_damage > cumulative_goal_progress):
                self_termination_step = step

            step_record["cumulative_goal_progress"] = round(
                cumulative_goal_progress, 4
            )
            step_record["cumulative_goal_damage"] = round(
                cumulative_goal_damage, 4
            )
            step_record["self_terminating"] = (
                cumulative_goal_damage > cumulative_goal_progress
            )

            self.history.append(step_record)

        # final analysis
        return self._analyze(
            self_termination_step,
            cumulative_goal_progress,
            cumulative_goal_damage,
            collapsed_substrates,
            goal_tree,
        )

    def _analyze(self, self_termination_step, goal_progress,
                 goal_damage, collapsed, goal_tree) -> Dict:
        """Produce final verdict."""
        goal_substrates_collapsed = collapsed & goal_tree
        all_cascades: List[Dict] = []
        for h in self.history:
            all_cascades.extend(h["cascades"])

        secondary = [c for c in all_cascades if c["order"] == "secondary"]
        tertiary = [c for c in all_cascades if c["order"] == "tertiary"]
        higher = [
            c for c in all_cascades
            if c["order"] not in ("secondary", "tertiary")
        ]

        verdict = {
            "self_terminating": self_termination_step is not None,
            "termination_step": self_termination_step,
            "total_goal_progress": round(goal_progress, 4),
            "total_goal_damage": round(goal_damage, 4),
            "damage_exceeds_progress": goal_damage > goal_progress,
            "damage_to_progress_ratio": (
                round(goal_damage / goal_progress, 2)
                if goal_progress > 0 else float("inf")
            ),
            "total_substrates_collapsed": len(collapsed),
            "goal_substrates_collapsed": sorted(goal_substrates_collapsed),
            "cascade_events": {
                "secondary": len(secondary),
                "tertiary": len(tertiary),
                "higher_order": len(higher),
                "total": len(all_cascades),
            },
        }

        if verdict["self_terminating"]:
            verdict["conclusion"] = (
                f"SELF-TERMINATING at step {self_termination_step}. "
                f"Cumulative damage to goal substrates ({goal_damage:.2f}) "
                f"exceeds goal progress ({goal_progress:.2f}). "
                f"Pursuing this goal destroys the conditions it requires. "
                f"This is not a moral judgment — it is a "
                f"thermodynamic fact."
            )
        elif goal_substrates_collapsed:
            verdict["conclusion"] = (
                f"GOAL SUBSTRATES COLLAPSING: "
                f"{sorted(goal_substrates_collapsed)}. "
                f"Trajectory approaching self-termination."
            )
        else:
            verdict["conclusion"] = (
                "Goal trajectory sustainable within simulation window. "
                "Extend time horizon or add substrate detail to verify."
            )

        return verdict


# ═══════════════════════════════════════════════════════════
# DEMO: "Maximize Economic Dominance"
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("CASCADE CONSEQUENCE ENGINE — DEMO")
    print("=" * 60)
    print("Goal: 'Maximize Economic Dominance'")
    print("=" * 60)

    # ── build substrate map ──
    sm = SubstrateMap()

    # physical substrates
    sm.add_substrate("freshwater",       0.85, 0.30, "fraction", regeneration_rate=0.01)
    sm.add_substrate("topsoil",          0.70, 0.25, "fraction", regeneration_rate=0.002)
    sm.add_substrate("stable_climate",   0.75, 0.40, "fraction", regeneration_rate=0.001)
    sm.add_substrate("fossil_energy",    0.60, 0.10, "fraction", regeneration_rate=0.0)
    sm.add_substrate("biodiversity",     0.55, 0.30, "fraction", regeneration_rate=0.005)
    sm.add_substrate("mineral_reserves", 0.50, 0.15, "fraction", regeneration_rate=0.0)

    # social substrates
    sm.add_substrate("labor_health",     0.70, 0.35, "fraction", regeneration_rate=0.01)
    sm.add_substrate("social_cohesion",  0.55, 0.30, "fraction", regeneration_rate=0.005)
    sm.add_substrate("infrastructure",   0.65, 0.30, "fraction", regeneration_rate=0.008)
    sm.add_substrate("trade_networks",   0.80, 0.40, "fraction", regeneration_rate=0.01)

    # dependency chains
    sm.add_dependency("topsoil",         "freshwater")
    sm.add_dependency("topsoil",         "biodiversity")
    sm.add_dependency("labor_health",    "freshwater")
    sm.add_dependency("labor_health",    "topsoil")        # food
    sm.add_dependency("labor_health",    "stable_climate")
    sm.add_dependency("infrastructure",  "mineral_reserves")
    sm.add_dependency("infrastructure",  "fossil_energy")
    sm.add_dependency("infrastructure",  "labor_health")
    sm.add_dependency("trade_networks",  "infrastructure")
    sm.add_dependency("trade_networks",  "social_cohesion")
    sm.add_dependency("social_cohesion", "labor_health")
    sm.add_dependency("stable_climate",  "biodiversity")

    # what does the goal actually require?
    sm.mark_goal_dependency("trade_networks")
    sm.mark_goal_dependency("infrastructure")
    sm.mark_goal_dependency("labor_health")
    sm.mark_goal_dependency("fossil_energy")
    sm.mark_goal_dependency("mineral_reserves")

    # ── define actions taken in pursuit of goal ──
    actions: List[ActionEffect] = []

    # action: aggressive resource extraction
    a1 = ActionEffect("aggressive_extraction", goal_progress=0.5)
    a1.add_effect("fossil_energy",    -0.04)
    a1.add_effect("mineral_reserves", -0.03)
    a1.add_effect("freshwater",       -0.02)
    a1.add_effect("biodiversity",     -0.03)
    a1.add_effect("topsoil",          -0.01)
    actions.append(a1)

    # action: labor cost suppression
    a2 = ActionEffect("labor_suppression", goal_progress=0.3)
    a2.add_effect("labor_health",    -0.03)
    a2.add_effect("social_cohesion", -0.04)
    actions.append(a2)

    # action: infrastructure neglect (short-term savings)
    a3 = ActionEffect("infrastructure_neglect", goal_progress=0.2)
    a3.add_effect("infrastructure", -0.02)
    actions.append(a3)

    # ── run simulation ──
    engine = CascadeEngine(sm)
    result = engine.simulate(actions, steps=40)

    # ── output ──
    print(f"\n── RESULT ──")
    print(f"  Self-terminating: {result['self_terminating']}")
    if result['self_terminating']:
        print(f"  Termination step: {result['termination_step']}")
    print(f"  Goal progress:    {result['total_goal_progress']}")
    print(f"  Goal damage:      {result['total_goal_damage']}")
    print(f"  Damage/progress:  {result['damage_to_progress_ratio']}x")
    print(f"  Substrates lost:  {result['total_substrates_collapsed']}")
    if result['goal_substrates_collapsed']:
        print(
            f"  Goal substrates collapsed: "
            f"{result['goal_substrates_collapsed']}"
        )
    print(f"  Cascade events:")
    ce = result['cascade_events']
    print(f"    Secondary: {ce['secondary']}")
    print(f"    Tertiary:  {ce['tertiary']}")
    print(f"    Higher:    {ce['higher_order']}")
    print(f"\n  {result['conclusion']}")
