# “””
CONSEQUENCE VELOCITY ENGINE

The missing variable in every institutional model.

Core principle (Kavik): Consequence doesn’t sit still when deferred.
It compounds. It couples with other deferred consequences.
It phase-shifts into something you can’t price because it’s
no longer the original consequence — it’s the consequence
of trying to avoid the consequence.

English says: “The truck is red.” (fixed state, permanent property)
Ojibwe says:  “The truck is in a state of redness.” (process, temporal, headed somewhere)

Institutional models freeze consequence as a fixed future cost.
This engine models consequence as a PROCESS with velocity,
acceleration, coupling, and phase transition.

License: CC0
“””

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# =============================================================================

# CORE: CONSEQUENCE AS PROCESS, NOT STATE

# =============================================================================

@dataclass
class Consequence:
“””
A consequence is not a fixed cost. It is a process with:
- position:     current magnitude
- velocity:     rate of change (is it getting worse?)
- acceleration: rate of rate of change (is the worsening accelerating?)
- coupling:     connections to other consequences
- buffer:       how much deferral capacity remains

```
English model:  consequence = fixed_number (wrong)
Process model:  consequence = f(t, coupling, buffer_state) (correct)
"""
name: str
domain: str  # ecological, social, economic, physiological, institutional

# Kinematics of consequence
position: float = 0.0        # current magnitude
velocity: float = 0.0        # d(position)/dt
acceleration: float = 0.0    # d(velocity)/dt — consequence of deferring consequence

# Buffer state
buffer_capacity: float = 1.0   # how much can be deferred
buffer_used: float = 0.0       # how much HAS been deferred
buffer_remaining: float = 1.0  # capacity - used

# Coupling to other consequences
coupled_to: List[str] = field(default_factory=list)
coupling_strength: Dict[str, float] = field(default_factory=dict)

# Phase state
phase: str = "deferred"  # deferred -> accumulating -> cascading -> realized
realized: bool = False

def defer(self, amount: float) -> Dict:
    """
    Attempt to defer consequence by amount.
    
    Key insight: deferral doesn't remove consequence.
    It adds to velocity (consequence moves faster)
    and reduces buffer capacity (less room to defer next time).
    
    This is the thermodynamic cost of comfort.
    """
    if self.realized:
        return {"deferred": False, "reason": "Already realized. Buffer broke."}
    
    actually_deferred = min(amount, self.buffer_remaining)
    overflow = amount - actually_deferred
    
    self.buffer_used += actually_deferred
    self.buffer_remaining = self.buffer_capacity - self.buffer_used
    
    # Deferral ACCELERATES consequence — this is the key mechanic
    # Every deferral makes the next consequence arrive faster
    self.velocity += actually_deferred * 0.1
    self.acceleration += actually_deferred * 0.01
    
    if overflow > 0:
        # Buffer broke — consequence realizes immediately
        self.position += overflow
        self.phase = "cascading"
        
    return {
        "deferred": actually_deferred,
        "overflow": overflow,
        "buffer_remaining": self.buffer_remaining,
        "new_velocity": self.velocity,
        "phase": self.phase,
    }

def step(self, dt: float = 1.0) -> Dict:
    """
    Advance consequence by one time step.
    Position updates from velocity. Velocity updates from acceleration.
    Buffer degrades over time (entropy).
    """
    # Physics: consequence moves
    self.velocity += self.acceleration * dt
    self.position += self.velocity * dt
    
    # Buffer degrades naturally (entropy cost of maintaining deferral)
    entropy_cost = self.buffer_used * 0.01 * dt
    self.buffer_capacity = max(0, self.buffer_capacity - entropy_cost)
    self.buffer_remaining = max(0, self.buffer_capacity - self.buffer_used)
    
    # Phase transitions
    if self.buffer_remaining <= 0 and self.phase == "deferred":
        self.phase = "accumulating"
    if self.velocity > 0.5 and self.phase == "accumulating":
        self.phase = "cascading"
    if self.position > self.buffer_capacity * 2:
        self.phase = "realized"
        self.realized = True
    
    return self.state()

def state(self) -> Dict:
    return {
        "name": self.name,
        "domain": self.domain,
        "position": round(self.position, 4),
        "velocity": round(self.velocity, 4),
        "acceleration": round(self.acceleration, 4),
        "buffer_remaining": round(self.buffer_remaining, 4),
        "phase": self.phase,
        "realized": self.realized,
    }
```

# =============================================================================

# CONSEQUENCE FIELD: COUPLED SYSTEM

# =============================================================================

@dataclass
class ConsequenceField:
“””
Multiple consequences coupled together.

```
When one consequence accelerates, coupled consequences feel it.
When one buffer breaks, coupled buffers get stressed.
This is why failures cascade — they're not independent.

The institutional model treats each problem as separate.
The consequence field shows they're all coupled.
"""
consequences: Dict[str, Consequence] = field(default_factory=dict)
history: List[Dict] = field(default_factory=list)

def add(self, consequence: Consequence):
    self.consequences[consequence.name] = consequence

def couple(self, name_a: str, name_b: str, strength: float = 0.1):
    """Bidirectional coupling between two consequences"""
    a = self.consequences[name_a]
    b = self.consequences[name_b]
    a.coupled_to.append(name_b)
    a.coupling_strength[name_b] = strength
    b.coupled_to.append(name_a)
    b.coupling_strength[name_a] = strength

def step(self, dt: float = 1.0) -> Dict:
    """
    Advance all consequences. Propagate coupling.
    
    Coupling mechanic: when consequence A accelerates,
    consequence B feels it proportional to coupling strength.
    When A's buffer breaks, B's buffer gets stressed.
    """
    # First: propagate coupling effects
    coupling_effects = {}
    for name, c in self.consequences.items():
        effects = []
        for coupled_name in c.coupled_to:
            coupled = self.consequences.get(coupled_name)
            if coupled:
                strength = c.coupling_strength.get(coupled_name, 0.1)
                # Velocity propagation
                vel_transfer = coupled.velocity * strength
                # Buffer stress propagation
                if coupled.phase in ("cascading", "realized"):
                    buffer_stress = strength * 0.5
                else:
                    buffer_stress = 0
                effects.append((vel_transfer, buffer_stress))
        coupling_effects[name] = effects
    
    # Apply coupling
    for name, effects in coupling_effects.items():
        c = self.consequences[name]
        for vel_transfer, buffer_stress in effects:
            c.velocity += vel_transfer
            c.buffer_capacity = max(0, c.buffer_capacity - buffer_stress)
            c.buffer_remaining = max(0, c.buffer_capacity - c.buffer_used)
    
    # Step all consequences
    states = {}
    for name, c in self.consequences.items():
        states[name] = c.step(dt)
    
    # Field-level diagnostics
    n_total = len(self.consequences)
    n_deferred = sum(1 for s in states.values() if s["phase"] == "deferred")
    n_accumulating = sum(1 for s in states.values() if s["phase"] == "accumulating")
    n_cascading = sum(1 for s in states.values() if s["phase"] == "cascading")
    n_realized = sum(1 for s in states.values() if s["phase"] == "realized")
    
    field_state = {
        "consequences": states,
        "deferred": n_deferred,
        "accumulating": n_accumulating,
        "cascading": n_cascading,
        "realized": n_realized,
        "total": n_total,
        "system_phase": (
            "stable" if n_cascading == 0 and n_realized == 0
            else "degrading" if n_cascading > 0 and n_realized == 0
            else "failing" if n_realized > 0 and n_realized < n_total
            else "collapsed"
        ),
    }
    
    self.history.append(field_state)
    return field_state
```

# =============================================================================

# COMFORT AUDIT: THE COST OF BUFFERING

# =============================================================================

@dataclass
class ComfortAudit:
“””
Measures the actual cost of choosing comfort over consequence.

```
For any action: what is the immediate consequence?
If buffered: where does the consequence go?
What is the velocity of the deferred consequence?
What is it coupled to?

This is what's missing from every institutional model.
They price the buffer. They don't price the consequence velocity.
"""

examples: Dict = field(default_factory=lambda: {
    "atmospheric_injection": {
        "action": "Inject sulfates to reduce warming",
        "immediate_consequence_if_felt": "Temperature signal drives behavior change",
        "buffer_mechanism": "Sulfate veil blocks signal",
        "deferred_consequence": "Albedo change, monsoon disruption, ocean acidification continues",
        "consequence_velocity": "Accelerating — coupled to water cycle, agriculture, migration",
        "coupling": ["water_cycle", "food_production", "migration", "ocean_chemistry"],
        "what_breaks": "Monsoon timing, crop calendars, coastal ecosystems",
        "cost_of_comfort": "Temporary temperature relief, permanent planetary disruption",
    },
    "medication_as_buffer": {
        "action": "Medicate symptom instead of addressing cause",
        "immediate_consequence_if_felt": "Pain/discomfort drives investigation of root cause",
        "buffer_mechanism": "Medication suppresses signal",
        "deferred_consequence": "Root cause progresses undetected, secondary organ damage",
        "consequence_velocity": "Accelerating — root cause compounds while signal suppressed",
        "coupling": ["organ_systems", "metabolic_function", "cognitive_function"],
        "what_breaks": "Organ failure, systemic cascade, 'sudden' crisis",
        "cost_of_comfort": "Temporary symptom relief, permanent system degradation",
    },
    "child_adderall": {
        "action": "Medicate child for classroom compliance",
        "immediate_consequence_if_felt": "Child's behavior signals classroom/system dysfunction",
        "buffer_mechanism": "Medication suppresses signal (child's behavior)",
        "deferred_consequence": "Dopamine sensitivity altered, sleep architecture disrupted, "
                               "classroom dysfunction unaddressed",
        "consequence_velocity": "Accelerating — neurological development window is finite",
        "coupling": ["child_development", "education_system", "family_dynamics"],
        "what_breaks": "Adult mental health, addiction vulnerability, learning capacity",
        "cost_of_comfort": "Teacher/parent comfort now, child's neurological future",
    },
    "soil_extraction": {
        "action": "Maximize crop yield without regeneration cycle",
        "immediate_consequence_if_felt": "Declining yield signals soil depletion",
        "buffer_mechanism": "Synthetic fertilizer masks depletion signal",
        "deferred_consequence": "Soil biome death, water table contamination, "
                               "pollinator collapse, carbon release",
        "consequence_velocity": "Accelerating — 170 miles of dead ecology is the measurement",
        "coupling": ["water_systems", "insect_populations", "bird_migration", "human_food"],
        "what_breaks": "Entire food production substrate",
        "cost_of_comfort": "Cheap food now, no food later",
    },
    "emotional_buffering": {
        "action": "Avoid feeling emotional consequence of one's actions",
        "immediate_consequence_if_felt": "Emotional pain drives behavior modification",
        "buffer_mechanism": "Projection, blame, substance use, narrative reframing",
        "deferred_consequence": "Relationship damage accumulates, pattern repeats, "
                               "consequence transfers to others",
        "consequence_velocity": "Accelerating — each buffered interaction adds to pattern",
        "coupling": ["relationships", "community_trust", "children", "institutional_culture"],
        "what_breaks": "Social fabric, trust networks, family systems",
        "cost_of_comfort": "Emotional comfort now, isolation and system failure later",
    },
    "economic_extraction": {
        "action": "Extract labor at bare maintenance (modern or historical)",
        "immediate_consequence_if_felt": "Worker departure signals unfair exchange",
        "buffer_mechanism": "Mandate participation (slavery, debt, insurance requirements)",
        "deferred_consequence": "Innovation suppression, skill atrophy, system brittleness, "
                               "sensor network corruption",
        "consequence_velocity": "Accelerating — every suppressed innovator is lost capacity",
        "coupling": ["innovation_pipeline", "social_stability", "infrastructure_maintenance"],
        "what_breaks": "Entire productive capacity of extracted population",
        "cost_of_comfort": "Cheap labor now, civilizational fragility",
    },
})
```

# =============================================================================

# DEMO: COUPLED CONSEQUENCE CASCADE

# =============================================================================

def demo_consequence_cascade():
“””
Model five coupled consequences being deferred.
Watch how deferral in one domain accelerates failure in others.
“””
field = ConsequenceField()

```
# Five consequence domains
field.add(Consequence("soil_depletion", "ecological", buffer_capacity=2.0))
field.add(Consequence("water_contamination", "ecological", buffer_capacity=1.5))
field.add(Consequence("pollinator_collapse", "ecological", buffer_capacity=1.0))
field.add(Consequence("food_system_fragility", "economic", buffer_capacity=2.5))
field.add(Consequence("social_instability", "social", buffer_capacity=3.0))

# Coupling — everything connects
field.couple("soil_depletion", "water_contamination", 0.15)
field.couple("soil_depletion", "pollinator_collapse", 0.2)
field.couple("soil_depletion", "food_system_fragility", 0.25)
field.couple("water_contamination", "pollinator_collapse", 0.15)
field.couple("water_contamination", "food_system_fragility", 0.2)
field.couple("pollinator_collapse", "food_system_fragility", 0.3)
field.couple("food_system_fragility", "social_instability", 0.35)
field.couple("social_instability", "food_system_fragility", 0.15)  # feedback

print("=" * 78)
print("CONSEQUENCE VELOCITY ENGINE: COUPLED CASCADE SIMULATION")
print("=" * 78)
print("Five consequences, coupled. Each deferred by 0.1/cycle.")
print("Watch velocity, coupling, and phase transitions.")
print("-" * 78)

header = f"{'Cycle':>5} | {'Phase':>10} | "
header += " | ".join(f"{n[:8]:>8}" for n in field.consequences.keys())
print(header)
print("-" * 78)

for cycle in range(80):
    # Each cycle: try to defer each consequence a little
    for name, c in field.consequences.items():
        if not c.realized:
            c.defer(0.1)
    
    state = field.step(dt=1.0)
    
    if cycle % 5 == 0 or state["system_phase"] != "stable":
        phases = [s["phase"][:4] for s in state["consequences"].values()]
        velocities = [f"{s['velocity']:>8.3f}" for s in state["consequences"].values()]
        print(f"{cycle:>5} | {state['system_phase']:>10} | " + " | ".join(velocities))
        
        if state["system_phase"] == "collapsed":
            break

print("-" * 78)
print()
print("DIAGNOSTIC:")
print("  Each consequence was deferred by a small amount each cycle.")
print("  Deferral increased velocity. Velocity propagated through coupling.")
print("  Buffers degraded from entropy. First buffer break cascaded.")
print("  System reported 'stable' until it was 'failing.'")
print("  No gradual warning. Green -> catastrophe.")
print()
print("  This is what happens when you model consequence as fixed cost")
print("  instead of process with velocity and coupling.")
print("  The institutional model sees five separate manageable problems.")
print("  The consequence field sees one coupled system accelerating toward failure.")
print("=" * 78)
```

if **name** == “**main**”:
demo_consequence_cascade()
