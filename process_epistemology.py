# “””
PROCESS EPISTEMOLOGY ENGINE

State-based vs Process-based knowledge frameworks.

Core insight (Kavik):
English:  “The truck is red.”     -> fixed property of object
Ojibwe:   “The truck is redding.” -> temporal process, headed somewhere

This is not a linguistic curiosity. It is an epistemological framework
that determines whether your models can see change coming.

Every institutional model that fails does so because it treats
dynamic processes as fixed states. This engine makes that
failure mechanism explicit and measurable.

License: CC0
“””

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
import numpy as np

# =============================================================================

# TWO WAYS OF KNOWING

# =============================================================================

class Epistemology(Enum):
“””
How a knowledge system relates to time and change.
“””
STATE_BASED   = “state”    # “The X is Y” — freezes property
PROCESS_BASED = “process”  # “The X is Y-ing” — tracks trajectory

@dataclass
class StateModel:
“””
English/Western institutional knowledge model.

```
Treats properties as fixed until proven otherwise.
Requires EVIDENCE of change before updating.
Cannot see change that hasn't yet crossed a threshold.

"The soil is fertile."      <- until test says otherwise
"The economy is stable."    <- until GDP says otherwise
"The patient is healthy."   <- until labs say otherwise
"The ecosystem is intact."  <- until species count says otherwise

Failure mode: threshold blindness. Everything is fine
until the state label changes, then suddenly it's a crisis.
No intermediate awareness. No trajectory sensing.
"""
name: str
properties: Dict[str, str] = field(default_factory=dict)
thresholds: Dict[str, float] = field(default_factory=dict)

def assess(self, measurements: Dict[str, float]) -> Dict[str, str]:
    """
    State model assessment: binary. Property holds or doesn't.
    No trajectory information. No velocity. No "where is this headed?"
    """
    assessment = {}
    for prop, threshold in self.thresholds.items():
        value = measurements.get(prop, 0)
        if value >= threshold:
            assessment[prop] = self.properties.get(prop, "stable")
        else:
            assessment[prop] = f"FAILED (was: {self.properties.get(prop, 'stable')})"
    return assessment
```

@dataclass
class ProcessModel:
“””
Ojibwe/consequence-integrated knowledge model.

```
Treats ALL properties as processes with trajectory.
Does not require evidence of change — assumes change is constant.
Tracks direction, velocity, acceleration, coupling.

"The soil is in a state of fertility, trending toward depletion
 at rate X, coupled to water and pollinator processes."

"The economy is in a state of apparent stability, but the 
 velocity of debt accumulation suggests phase transition
 within N cycles."

"The patient is in a state of current function, but inflammation
 markers are accelerating, suggesting systemic shift."

Advantage: sees change BEFORE threshold crossing.
Sees trajectory. Sees coupling. Sees where things are headed.
"""
name: str
processes: Dict[str, 'Process'] = field(default_factory=dict)

def assess(self, measurements: Dict[str, float], 
           previous: Optional[Dict[str, float]] = None,
           dt: float = 1.0) -> Dict[str, Dict]:
    """
    Process model assessment: trajectory-aware.
    Every measurement is a process with direction.
    """
    assessment = {}
    for name, current_value in measurements.items():
        process = self.processes.get(name)
        if process:
            process.update(current_value, dt)
            assessment[name] = process.state()
        else:
            # New process — initialize
            p = Process(name=name, current=current_value)
            if previous and name in previous:
                p.velocity = (current_value - previous[name]) / dt
            self.processes[name] = p
            assessment[name] = p.state()
    return assessment
```

@dataclass
class Process:
“””
A property understood as process, not state.

```
"The truck is redding" means:
- Current state: red
- Velocity: fading (UV exposure, oxidation)
- Acceleration: faster in summer (more UV)
- Trajectory: will be pink, then primer, then rust
- Coupling: connected to body integrity, resale value, owner attention

This is more information than "the truck is red."
It is ACTIONABLE information. You can intervene at any point
on the trajectory. You can't intervene on a fixed state
because a fixed state doesn't tell you where it's going.
"""
name: str
current: float = 0.0
velocity: float = 0.0
acceleration: float = 0.0
history: List[float] = field(default_factory=list)

# Process awareness
trajectory: str = "stable"  # improving, stable, degrading, collapsing
time_to_threshold: Optional[float] = None

def update(self, new_value: float, dt: float = 1.0):
    """Update process with new measurement"""
    self.history.append(self.current)
    
    old_velocity = self.velocity
    self.velocity = (new_value - self.current) / dt
    self.acceleration = (self.velocity - old_velocity) / dt
    self.current = new_value
    
    # Trajectory classification
    if self.velocity > 0.01 and self.acceleration > 0:
        self.trajectory = "improving_accelerating"
    elif self.velocity > 0.01:
        self.trajectory = "improving"
    elif self.velocity < -0.01 and self.acceleration < 0:
        self.trajectory = "degrading_accelerating"
    elif self.velocity < -0.01:
        self.trajectory = "degrading"
    elif abs(self.velocity) <= 0.01 and abs(self.acceleration) > 0.005:
        self.trajectory = "stable_but_stressed"
    else:
        self.trajectory = "stable"

def state(self) -> Dict:
    return {
        "name": self.name,
        "current": round(self.current, 4),
        "velocity": round(self.velocity, 4),
        "acceleration": round(self.acceleration, 4),
        "trajectory": self.trajectory,
        "reading": self._ojibwe_reading(),
    }

def _ojibwe_reading(self) -> str:
    """
    Generate process-aware reading.
    Not "the X is Y" but "the X is Y-ing toward Z."
    """
    if self.trajectory == "stable":
        return f"{self.name} is in a state of current value ({self.current:.2f}), holding"
    elif "improving" in self.trajectory:
        accel = ", accelerating" if "accelerating" in self.trajectory else ""
        return f"{self.name} is strengthening ({self.velocity:+.3f}/t{accel})"
    elif "degrading" in self.trajectory:
        accel = ", accelerating" if "accelerating" in self.trajectory else ""
        return f"{self.name} is weakening ({self.velocity:+.3f}/t{accel})"
    elif self.trajectory == "stable_but_stressed":
        return f"{self.name} appears stable but acceleration detected ({self.acceleration:+.4f}/t²)"
    return f"{self.name}: {self.current:.2f}"
```

# =============================================================================

# COMPARATIVE FAILURE ANALYSIS

# =============================================================================

@dataclass
class EpistemologyComparison:
“””
Run the same data through both frameworks.
Watch what each one sees and misses.
“””

```
failure_cases: Dict = field(default_factory=lambda: {
    "soil_fertility": {
        "scenario": (
            "Soil nitrogen declines 2% per year for 20 years, "
            "then accelerates to 8% per year as biome collapses."
        ),
        "state_model_sees": (
            "Year 1-15: 'Soil is fertile' (above threshold). "
            "Year 16: 'Soil is depleted' (below threshold). "
            "Response: emergency fertilizer application. "
            "Total warning time: ZERO. Binary flip."
        ),
        "process_model_sees": (
            "Year 1: 'Soil fertility is declining at 2%/yr.' "
            "Year 5: 'Decline rate stable but coupled to water table.' "
            "Year 10: 'Decline accelerating. Biome stress detected.' "
            "Year 12: 'Acceleration increasing. Cascade probable within 5yr.' "
            "Response window: 12+ YEARS of trajectory data."
        ),
    },
    "institutional_trust": {
        "scenario": (
            "Public trust in institution declines slowly, "
            "then collapses when single event reveals gap "
            "between reported and actual state."
        ),
        "state_model_sees": (
            "'Institution is trusted' -> 'Institution is not trusted.' "
            "Binary flip attributed to the triggering event. "
            "'The scandal caused the trust collapse.' "
            "No awareness of 15 years of trust erosion."
        ),
        "process_model_sees": (
            "'Trust is weakening at rate X, accelerating when promises '  "
            "'diverge from outcomes. Current trajectory: threshold crossing ' "
            "'in approximately N years. Any triggering event will catalyze.' "
            "The scandal didn't cause collapse. It revealed it."
        ),
    },
    "ecosystem_collapse": {
        "scenario": (
            "170 miles of agricultural corridor. "
            "Insects decline over decades. Birds follow. "
            "During peak spring migration: zero insects, zero birds."
        ),
        "state_model_sees": (
            "'Ecosystem is functional' (species still present in surveys). "
            "Then: 'Ecosystem has collapsed' (zero observations). "
            "Response: shock. 'How did this happen so fast?'"
        ),
        "process_model_sees": (
            "'Insect populations weakening at rate X, accelerating.' "
            "'Bird populations tracking insect decline with lag Y.' "
            "'Soil biome coupling detected: chemical inputs correlate.' "
            "'Trajectory: functional extinction in Z growing seasons.' "
            "Not shock. Measurement. The process was visible for decades."
        ),
    },
    "personal_health": {
        "scenario": (
            "Person manages chronic condition with medication. "
            "Underlying cause progresses. Medication masks signal. "
            "Organ failure appears 'sudden.'"
        ),
        "state_model_sees": (
            "'Patient is managed' (labs within range). "
            "Then: 'Patient is in crisis' (organ failure). "
            "'Sudden onset.' Medication adjustment."
        ),
        "process_model_sees": (
            "'Inflammatory markers trending upward despite medication.' "
            "'Organ function declining at rate X under medication mask.' "
            "'Medication is buffer, not treatment. Buffer capacity ' "
            "'depleting. Underlying process accelerating.' "
            "Not sudden. Buffered. Different thing entirely."
        ),
    },
})

diagnostic: str = (
    "In every case, the state model produces a binary surprise. "
    "In every case, the process model produces years of trajectory data. "
    "The state model isn't wrong about the current state. "
    "It's blind to the PROCESS that state is embedded in. "
    "'The truck IS red' is not false. It's incomplete. "
    "It tells you nothing about where the redness is headed. "
    "And if your entire institutional apparatus is built on state models, "
    "you will be perpetually surprised by processes that were visible "
    "to anyone reading trajectory instead of label."
)
```

# =============================================================================

# DEMO

# =============================================================================

def demo_epistemology_comparison():
“””
Same declining system. Two frameworks. Different awareness.
“””
print(”=” * 70)
print(“PROCESS EPISTEMOLOGY: STATE vs PROCESS AWARENESS”)
print(”=” * 70)
print()

```
# Simulate declining system
state_m = StateModel(
    name="Institutional Assessment",
    properties={"fertility": "fertile", "stability": "stable"},
    thresholds={"fertility": 0.3, "stability": 0.4},
)

process_m = ProcessModel(name="Ground-Truth Reading")

np.random.seed(42)

threshold = 0.3
value = 1.0
decline_rate = 0.03

print(f"System starts at 1.0, threshold at {threshold}")
print(f"Declining ~3%/year with accelerating degradation")
print("-" * 70)
print(f"{'Year':>4} | {'Value':>6} | {'State Model':>20} | {'Process Reading'}")
print("-" * 70)

prev_measurements = None

for year in range(30):
    # Accelerating decline
    decline_rate *= 1.05
    value = max(0, value - decline_rate + np.random.normal(0, 0.01))
    
    measurements = {"fertility": value}
    
    # State model: binary
    state_result = state_m.assess(measurements)
    state_label = state_result.get("fertility", "?")
    
    # Process model: trajectory
    process_result = process_m.assess(measurements, prev_measurements)
    process_reading = process_result.get("fertility", {}).get("reading", "?")
    
    prev_measurements = measurements.copy()
    
    if year % 3 == 0 or value < threshold or year > 20:
        print(f"{year:>4} | {value:>6.3f} | {state_label:>20} | {process_reading}")

print("-" * 70)
print()
print("DIAGNOSTIC:")
print("  State model reported 'fertile' until threshold crossing.")
print("  Then reported 'FAILED' with zero prior warning.")
print("  Process model reported trajectory THE ENTIRE TIME.")
print("  Same data. Different epistemology. Different awareness.")
print()
print("  English: 'The soil is fertile.'  (until it isn't)")
print("  Ojibwe:  'The soil is fertiling, weakening, headed toward barren.'")
print()
print("  One framework surprises you. The other prepares you.")
print("  The choice of framework IS the choice of outcome.")
print("=" * 70)
```

if **name** == “**main**”:
demo_epistemology_comparison()
