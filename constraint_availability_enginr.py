# constraint_accountability_engine.py
# CC0 — no rights reserved

"""
Engine: Constraint Accountability Chain
Walks the decision genome forward and backward.
Computes reversion energy, cascade risk,
phenotype expression, and mutation analysis.

stdlib only. No dependencies.
"""

import hashlib
import time
import math
from typing import Optional


# ── DECISION NODE ────────────────────────────

class DecisionNode:
    def __init__(
        self,
        actor_role: str,
        layer: int,
        comfort_captured: float,
        constraint_at_stake: str,
        ground_signal: float,
        reported_signal: float,
        mechanism: str,
        parent: Optional['DecisionNode'] = None,
        tenure: float = 0.0,
    ):
        self.node_id = hashlib.sha256(
            f"{actor_role}:{layer}:{time.time()}".encode()
        ).hexdigest()[:16]
        self.timestamp = time.time()
        self.parent = parent
        self.parent_id = parent.node_id if parent else None
        self.children = []

        # actor
        self.actor_role = actor_role
        self.layer = layer
        self.tenure = tenure
        self.comfort_captured = comfort_captured

        # decision
        self.constraint = constraint_at_stake
        self.ground_signal = ground_signal
        self.reported_signal = reported_signal
        self.delta = abs(ground_signal - reported_signal)
        self.choice = (
            "direct_sense" if self.delta < 0.05
            else "comfort_protect"
        )
        self.mechanism = mechanism

        # inheritance
        self.compounded = False
        self.override_attempted = False
        self.override_succeeded = False
        self._compute_inheritance()

        if parent:
            parent.children.append(self)

    def _compute_inheritance(self):
        if not self.parent:
            return
        if self.parent.choice == "comfort_protect":
            if self.choice == "direct_sense":
                self.override_attempted = True
                # override only succeeds if actor has
                # more comfort capital than parent
                # (institutional leverage)
                self.override_succeeded = (
                    self.comfort_captured > self.parent.comfort_captured
                )
                if not self.override_succeeded:
                    # forced back to comfort — dominant gene wins
                    self.reported_signal = self.parent.reported_signal
                    self.delta = abs(self.ground_signal - self.reported_signal)
                    self.choice = "comfort_protect"
                    self.mechanism = "delegate_down"
            else:
                self.compounded = True

    @property
    def reversion_cost(self) -> float:
        """Energy to undo this node's distortion.
        Scales with tenure (entrenchment) and
        downstream dependent count."""
        base = self.delta * (1 + self.tenure)
        downstream = self._count_downstream()
        return base * (1 + 0.5 * downstream)

    def _count_downstream(self) -> int:
        count = len(self.children)
        for c in self.children:
            count += c._count_downstream()
        return count


# ── ACCOUNTABILITY CHAIN ─────────────────────

class AccountabilityChain:
    def __init__(self, chain_id: str, constraint_domain: str):
        self.chain_id = chain_id
        self.constraint_domain = constraint_domain
        self.nodes: list[DecisionNode] = []
        self.epigenetic_events: list[dict] = []

    def add_decision(self, **kwargs) -> DecisionNode:
        parent = self.nodes[-1] if self.nodes else None
        node = DecisionNode(parent=parent, **kwargs)
        self.nodes.append(node)
        return node

    def add_epigenetic_event(
        self,
        factor: str,
        effect: str,
        magnitude: float,
    ):
        self.epigenetic_events.append({
            "factor": factor,
            "effect": effect,
            "magnitude": magnitude,
            "timestamp": time.time(),
        })

    # ── GENOME ANALYSIS ──────────────────

    @property
    def mutations(self) -> dict:
        comfort = sum(1 for n in self.nodes if n.choice == "comfort_protect")
        direct = sum(1 for n in self.nodes if n.choice == "direct_sense")
        total = len(self.nodes)

        # longest comfort streak
        streak = 0
        max_streak = 0
        for n in self.nodes:
            if n.choice == "comfort_protect":
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0

        # last direct sense
        last_direct = None
        for n in reversed(self.nodes):
            if n.choice == "direct_sense":
                last_direct = n.node_id
                break

        # cumulative drift
        drift = 0.0
        if self.nodes:
            drift = abs(
                self.nodes[0].ground_signal
                - self.nodes[-1].reported_signal
            )

        return {
            "total_comfort_choices": comfort,
            "total_direct_sense_choices": direct,
            "comfort_ratio": comfort / total if total else 0,
            "longest_comfort_streak": max_streak,
            "last_direct_sense": last_direct,
            "drift_from_origin": drift,
        }

    # ── PHENOTYPE EXPRESSION ─────────────

    @property
    def phenotype(self) -> dict:
        if not self.nodes:
            return {
                "institutional_blindness": 0,
                "ratchet_depth": 0,
                "reversion_energy": 0,
                "cascade_risk": 0,
                "time_to_failure": float('inf'),
            }

        # signal fidelity: product of (1 - delta) across chain
        fidelity = 1.0
        for n in self.nodes:
            fidelity *= (1 - n.delta)
        blindness = 1 - max(fidelity, 0)

        # ratchet depth: consecutive comfort from top
        ratchet = 0
        for n in reversed(self.nodes):
            if n.choice == "comfort_protect":
                ratchet += 1
            else:
                break

        # total reversion energy
        reversion = sum(n.reversion_cost for n in self.nodes
                       if n.choice == "comfort_protect")

        # cascade risk: nonlinear in blindness
        # sigmoid centered at 0.7 blindness
        cascade = 1 / (1 + math.exp(-12 * (blindness - 0.7)))

        # time to failure: inverse of cascade risk * drift rate
        m = self.mutations
        if m["comfort_ratio"] > 0 and cascade > 0.01:
            drift_rate = m["drift_from_origin"] / max(len(self.nodes), 1)
            ttf = (1 - blindness) / (drift_rate * cascade + 1e-9)
        else:
            ttf = float('inf')

        # apply epigenetic modifiers
        for event in self.epigenetic_events:
            if event["effect"] == "activates_direct_sense":
                cascade *= (1 - 0.3 * event["magnitude"])
            elif event["effect"] == "reinforces_comfort":
                cascade = min(1.0, cascade * (1 + 0.3 * event["magnitude"]))

        return {
            "institutional_blindness": round(blindness, 4),
            "ratchet_depth": ratchet,
            "reversion_energy": round(reversion, 4),
            "cascade_risk": round(cascade, 4),
            "time_to_failure": round(ttf, 4),
        }

    # ── CHAIN TRAVERSAL ──────────────────

    def walk_backward(self, from_node_id: Optional[str] = None):
        """Yield nodes from terminal back to origin.
        Trace the comfort ancestry."""
        if from_node_id:
            node = next((n for n in self.nodes if n.node_id == from_node_id), None)
        else:
            node = self.nodes[-1] if self.nodes else None
        while node:
            yield node
            node = node.parent

    def find_comfort_origin(self) -> Optional[DecisionNode]:
        """Find the first comfort choice in the chain.
        Patient zero of institutional blindness."""
        for node in self.nodes:
            if node.choice == "comfort_protect":
                return node
        return None

    def find_override_failures(self) -> list[DecisionNode]:
        """Find all nodes where direct sensing was
        attempted but overridden by comfort dominance."""
        return [
            n for n in self.nodes
            if n.override_attempted and not n.override_succeeded
        ]

    # ── REPORTING ────────────────────────

    def report(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "constraint_domain": self.constraint_domain,
            "total_nodes": len(self.nodes),
            "mutations": self.mutations,
            "phenotype": self.phenotype,
            "override_failures": len(self.find_override_failures()),
            "comfort_origin": (
                self.find_comfort_origin().node_id
                if self.find_comfort_origin() else None
            ),
            "epigenetic_events": len(self.epigenetic_events),
        }


# ── DEMO: MANUFACTURING FLOOR ───────────────

if __name__ == "__main__":
    chain = AccountabilityChain(
        chain_id="mfg_plant_7",
        constraint_domain="safety_signal",
    )

    # Layer 0: laborer sees crack in press frame
    chain.add_decision(
        actor_role="press_operator",
        layer=0,
        comfort_captured=0.05,
        constraint_at_stake="hydraulic_press_frame_integrity",
        ground_signal=0.82,    # real risk level
        reported_signal=0.82,  # reports honestly
        mechanism="direct_sense",
        tenure=8.0,
    )

    # Layer 1: supervisor softens it
    chain.add_decision(
        actor_role="shift_supervisor",
        layer=1,
        comfort_captured=0.25,
        constraint_at_stake="hydraulic_press_frame_integrity",
        ground_signal=0.82,
        reported_signal=0.55,  # "it's manageable"
        mechanism="attenuation",
        tenure=3.0,
    )

    # Layer 2: plant manager reframes
    chain.add_decision(
        actor_role="plant_manager",
        layer=2,
        comfort_captured=0.55,
        constraint_at_stake="hydraulic_press_frame_integrity",
        ground_signal=0.82,
        reported_signal=0.30,  # "scheduled maintenance item"
        mechanism="reframe",
        tenure=5.0,
    )

    # Layer 3: regional director normalizes
    chain.add_decision(
        actor_role="regional_director",
        layer=3,
        comfort_captured=0.75,
        constraint_at_stake="hydraulic_press_frame_integrity",
        ground_signal=0.82,
        reported_signal=0.10,  # "within operational parameters"
        mechanism="normalize",
        tenure=7.0,
    )

    # Layer 4: maintenance tech tries to override
    chain.add_decision(
        actor_role="maintenance_tech",
        layer=1,
        comfort_captured=0.15,
        constraint_at_stake="hydraulic_press_frame_integrity",
        ground_signal=0.82,
        reported_signal=0.82,  # tries direct sense
        mechanism="direct_sense",
        tenure=12.0,
    )

    # epigenetic: OSHA inspection incoming
    chain.add_epigenetic_event(
        factor="regulatory_pressure",
        effect="activates_direct_sense",
        magnitude=0.6,
    )

    # ── OUTPUT ───────────────────────────
    report = chain.report()
    print("=" * 50)
    print(f"CHAIN: {report['chain_id']}")
    print(f"DOMAIN: {report['constraint_domain']}")
    print(f"NODES: {report['total_nodes']}")
    print("-" * 50)
    print("MUTATIONS:")
    for k, v in report['mutations'].items():
        print(f"  {k}: {v}")
    print("-" * 50)
    print("PHENOTYPE:")
    for k, v in report['phenotype'].items():
        print(f"  {k}: {v}")
    print("-" * 50)
    print(f"OVERRIDE FAILURES: {report['override_failures']}")
    print(f"COMFORT ORIGIN: {report['comfort_origin']}")
    print(f"EPIGENETIC EVENTS: {report['epigenetic_events']}")
    print("=" * 50)

    # walk backward from terminal
    print("\nANCESTRY WALK (terminal → origin):")
    for node in chain.walk_backward():
        print(
            f"  [{node.layer}] {node.actor_role}: "
            f"ground={node.ground_signal} → "
            f"reported={node.reported_signal} "
            f"({node.choice}|{node.mechanism})"
        )
