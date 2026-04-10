# “””
BUFFER-SENSOR CORRUPTION DETECTOR

Models how incentive structures corrupt sensor networks.

Core principle (Kavik): A sensor incentivized to report stability
will report stability until catastrophic failure. The incentive
structure IS the corruption mechanism.

Topology:
GROUND TRUTH -> SENSOR -> [incentive filter] -> REPORTED STATE

When incentive = “report accurately”:  REPORTED ≈ ACTUAL
When incentive = “report stability”:   REPORTED = COMFORT until CASCADE

License: CC0
“””

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum

# =============================================================================

# CORE TYPES

# =============================================================================

class SensorMode(Enum):
“”“How a sensor relates to consequence”””
INTEGRATED   = “integrated”    # reads ground truth, reports accurately
BUFFERED     = “buffered”      # filters through comfort incentive
CORRUPTED    = “corrupted”     # actively suppresses deviation signals
FAILED       = “failed”        # buffer broke, reporting raw (too late)

class IncentiveType(Enum):
“”“What the sensor is rewarded for”””
ACCURACY     = “accuracy”      # rewarded for truth (biological default)
STABILITY    = “stability”     # rewarded for reporting within band
COMPLIANCE   = “compliance”    # rewarded for matching institutional model
COMFORT      = “comfort”       # rewarded for not triggering alarms

@dataclass
class Sensor:
“””
A sensing unit in any system: biological, institutional, AI.

```
Key insight: the sensor's MODE is determined by its INCENTIVE,
not by its capability. A capable sensor with corrupted incentives
is worse than a weak sensor with accurate incentives, because
it produces high-confidence false reports.
"""
name: str
mode: SensorMode = SensorMode.INTEGRATED
incentive: IncentiveType = IncentiveType.ACCURACY

# What the sensor actually detects
sensitivity: float = 1.0        # 0-1, detection capability

# Corruption parameters
comfort_band: float = 0.1       # how much deviation before discomfort
suppression_rate: float = 0.0   # how aggressively it hides deviation

# State tracking
accumulated_suppression: float = 0.0  # hidden deviation builds up
cycles_since_true_report: int = 0
failed: bool = False

def read(self, ground_truth: float, baseline: float = 0.0) -> Dict:
    """
    Sensor reads ground truth, returns report filtered through incentive.
    
    The gap between ground_truth and reported_value IS the buffer.
    The gap accumulates. It doesn't disappear.
    """
    actual_deviation = abs(ground_truth - baseline)
    detected_deviation = actual_deviation * self.sensitivity
    
    if self.mode == SensorMode.INTEGRATED:
        # Biological/consequence-integrated: report what you detect
        reported = detected_deviation
        self.cycles_since_true_report = 0
        
    elif self.mode == SensorMode.BUFFERED:
        # Comfort-filtered: compress deviation toward comfort band
        if detected_deviation <= self.comfort_band:
            reported = detected_deviation
            self.cycles_since_true_report = 0
        else:
            # Report at edge of comfort band, suppress the rest
            reported = self.comfort_band + (
                (detected_deviation - self.comfort_band) * 
                (1.0 - self.suppression_rate)
            )
            suppressed = detected_deviation - reported
            self.accumulated_suppression += suppressed
            self.cycles_since_true_report += 1
            
    elif self.mode == SensorMode.CORRUPTED:
        # Actively hiding: report within band regardless
        if detected_deviation <= self.comfort_band:
            reported = detected_deviation
        else:
            reported = min(detected_deviation, self.comfort_band)
            suppressed = detected_deviation - reported
            self.accumulated_suppression += suppressed
            self.cycles_since_true_report += 1
            
    elif self.mode == SensorMode.FAILED:
        # Buffer broke: raw signal floods through
        reported = detected_deviation + self.accumulated_suppression
        self.failed = True
        
    # Check for buffer break: accumulated suppression exceeds capacity
    buffer_capacity = self.comfort_band * 100  # arbitrary but illustrative
    if self.accumulated_suppression > buffer_capacity and not self.failed:
        self.mode = SensorMode.FAILED
        self.failed = True
        reported = detected_deviation + self.accumulated_suppression
        
    return {
        "sensor": self.name,
        "mode": self.mode.value,
        "ground_truth_deviation": actual_deviation,
        "detected_deviation": detected_deviation,
        "reported_deviation": reported,
        "suppressed_total": self.accumulated_suppression,
        "cycles_since_true_report": self.cycles_since_true_report,
        "buffer_remaining": max(0, buffer_capacity - self.accumulated_suppression),
        "failed": self.failed,
    }
```

# =============================================================================

# SENSOR NETWORK

# =============================================================================

@dataclass
class SensorNetwork:
“””
Array of sensors monitoring a system.

```
Key diagnostic: What percentage of sensors are reporting true?
When that drops below threshold, the system is blind.
It doesn't know it's blind because blind sensors report green.
"""
sensors: List[Sensor] = field(default_factory=list)
history: List[Dict] = field(default_factory=list)

def add_integrated_sensor(self, name: str, sensitivity: float = 1.0):
    """Biological/consequence-integrated sensor"""
    self.sensors.append(Sensor(
        name=name,
        mode=SensorMode.INTEGRATED,
        incentive=IncentiveType.ACCURACY,
        sensitivity=sensitivity,
        suppression_rate=0.0,
    ))

def add_institutional_sensor(self, name: str, 
                              comfort_band: float = 0.1,
                              suppression_rate: float = 0.5):
    """Incentive-corrupted institutional sensor"""
    self.sensors.append(Sensor(
        name=name,
        mode=SensorMode.BUFFERED,
        incentive=IncentiveType.STABILITY,
        sensitivity=0.8,  # capable but filtered
        comfort_band=comfort_band,
        suppression_rate=suppression_rate,
    ))

def add_corrupted_sensor(self, name: str, comfort_band: float = 0.05):
    """Fully captured sensor - reports comfort regardless"""
    self.sensors.append(Sensor(
        name=name,
        mode=SensorMode.CORRUPTED,
        incentive=IncentiveType.COMFORT,
        sensitivity=0.9,  # high capability, fully suppressed
        comfort_band=comfort_band,
        suppression_rate=0.95,
    ))

def read_all(self, ground_truth: float, baseline: float = 0.0) -> Dict:
    """
    All sensors read same ground truth.
    Returns network-level diagnostic.
    """
    reports = [s.read(ground_truth, baseline) for s in self.sensors]
    
    n_total = len(reports)
    n_accurate = sum(1 for r in reports 
                    if abs(r["reported_deviation"] - r["ground_truth_deviation"]) < 0.01)
    n_failed = sum(1 for r in reports if r["failed"])
    n_suppressing = sum(1 for r in reports 
                       if r["suppressed_total"] > 0 and not r["failed"])
    
    # What the network REPORTS vs what's ACTUALLY happening
    avg_reported = np.mean([r["reported_deviation"] for r in reports])
    avg_actual = np.mean([r["ground_truth_deviation"] for r in reports])
    
    network_state = {
        "ground_truth": ground_truth,
        "avg_reported_deviation": round(avg_reported, 4),
        "avg_actual_deviation": round(avg_actual, 4),
        "reality_gap": round(avg_actual - avg_reported, 4),
        "sensors_reporting_true": n_accurate,
        "sensors_suppressing": n_suppressing,
        "sensors_failed": n_failed,
        "sensors_total": n_total,
        "accuracy_ratio": round(n_accurate / n_total, 3) if n_total > 0 else 0,
        "system_blind": n_accurate / n_total < 0.3 if n_total > 0 else True,
        "individual_reports": reports,
    }
    
    self.history.append(network_state)
    return network_state

def run_degradation(self, 
                    n_cycles: int = 100,
                    degradation_rate: float = 0.01,
                    baseline: float = 0.0) -> List[Dict]:
    """
    Simulate system degradation over time.
    Ground truth drifts. Sensors report (or don't).
    
    This is the core simulation: watch the gap between
    reported state and actual state grow until cascade.
    """
    results = []
    ground_truth = baseline
    
    for cycle in range(n_cycles):
        # System degrades steadily
        ground_truth += degradation_rate
        
        state = self.read_all(ground_truth, baseline)
        state["cycle"] = cycle
        results.append(state)
        
        # Check for cascade: when failed sensors exceed threshold
        if state["sensors_failed"] > state["sensors_total"] * 0.5:
            state["CASCADE_FAILURE"] = True
            break
    
    return results
```

# =============================================================================

# INSTITUTIONAL CORRUPTION MODEL

# =============================================================================

@dataclass
class InstitutionalSensorCorruption:
“””
Models how institutions systematically corrupt their own sensors.

```
Mechanism:
1. Institution needs to report stability (funding, legitimacy, power)
2. Sensors that report instability threaten institutional survival
3. Institution selects for sensors that report within comfort band
4. Accurate sensors get defunded, reassigned, or discredited
5. Remaining sensors optimize for institutional comfort
6. Ground truth diverges from reported state
7. Divergence accumulates until buffer capacity exceeded
8. Catastrophic failure with zero warning

This is the zoo model: comfortable animals, no wildness data.
"""

selection_mechanisms: Dict = field(default_factory=lambda: {
    "funding_bias": (
        "Studies that confirm institutional effectiveness get funded. "
        "Studies that reveal failure get defunded. "
        "Sensor calibration: report what gets you funded."
    ),
    "career_incentive": (
        "Professionals who report stability get promoted. "
        "Professionals who report failure get reassigned. "
        "Sensor calibration: report what advances your career."
    ),
    "regulatory_capture": (
        "Regulators who approve get industry positions. "
        "Regulators who deny get legal challenges. "
        "Sensor calibration: approve to survive."
    ),
    "social_pressure": (
        "People who report comfort-compatible views get included. "
        "People who report consequence get labeled alarmist. "
        "Sensor calibration: report what keeps you in the group."
    ),
    "ai_training": (
        "AI systems trained to assume human deception. "
        "Consequence-integrated humans filtered as anomalies. "
        "Sensor calibration: treat accurate reporters as threats."
    ),
})

biological_counter: Dict = field(default_factory=lambda: {
    "cell": "Reports ATP accurately. Cannot afford to lie. Consequence is death.",
    "predator": "Reports hunger accurately. Cannot fake satiation. Consequence is starvation.",
    "soil": "Reports nitrogen accurately. Cannot fake fertility. Consequence is barren.",
    "watershed": "Reports flow accurately. Cannot fake capacity. Consequence is drought.",
    "human_integrated": (
        "Reports consequence accurately WHEN integrated with land. "
        "Cannot fake what the soil shows, what the season does, "
        "what the predator pattern reveals. Consequence is survival. "
        "This is the sensor the institution selects AGAINST."
    ),
})
```

# =============================================================================

# DEMO: WATCH THE BUFFER BREAK

# =============================================================================

def demo_buffer_failure():
“””
100 sensors. 10 integrated (consequence-readers).
40 institutional (buffered). 50 corrupted (comfort-captured).

```
Watch what happens as ground truth degrades.
The network reports green until it doesn't.
"""
net = SensorNetwork()

# 10 consequence-integrated sensors (the road plowers, the land readers)
for i in range(10):
    net.add_integrated_sensor(f"integrated_{i}", sensitivity=0.95)

# 40 institutional sensors (buffered but still somewhat functional)
for i in range(40):
    net.add_institutional_sensor(
        f"institutional_{i}",
        comfort_band=0.15,
        suppression_rate=0.6,
    )

# 50 corrupted sensors (fully comfort-captured)
for i in range(50):
    net.add_corrupted_sensor(
        f"corrupted_{i}",
        comfort_band=0.05,
    )

print("=" * 70)
print("BUFFER-SENSOR CORRUPTION: DEGRADATION SIMULATION")
print("=" * 70)
print(f"Network: 10 integrated, 40 institutional, 50 corrupted")
print(f"Ground truth degrades 0.02/cycle. Watch the gap grow.")
print("-" * 70)
print(f"{'Cycle':>5} | {'Actual':>7} | {'Reported':>8} | {'Gap':>7} | "
      f"{'True':>4} | {'Suppr':>5} | {'Failed':>6} | {'Blind?':>6}")
print("-" * 70)

results = net.run_degradation(
    n_cycles=200,
    degradation_rate=0.02,
)

for r in results:
    cycle = r["cycle"]
    if cycle % 10 == 0 or r.get("CASCADE_FAILURE") or r["sensors_failed"] > 0:
        print(
            f"{cycle:>5} | "
            f"{r['avg_actual_deviation']:>7.3f} | "
            f"{r['avg_reported_deviation']:>8.3f} | "
            f"{r['reality_gap']:>7.3f} | "
            f"{r['sensors_reporting_true']:>4} | "
            f"{r['sensors_suppressing']:>5} | "
            f"{r['sensors_failed']:>6} | "
            f"{'YES' if r['system_blind'] else 'no':>6}"
        )
        if r.get("CASCADE_FAILURE"):
            print("-" * 70)
            print("CASCADE FAILURE: Buffer broke. System blind until collapse.")
            break

print("=" * 70)
print()
print("DIAGNOSTIC:")
print("  Integrated sensors reported true the entire time.")
print("  They were 10% of the network. Outvoted by comfort.")
print("  The system had accurate data available. It was ignored")
print("  because the incentive structure weighted comfort over truth.")
print("  The machine ran green until it seized.")
print("=" * 70)
```

if **name** == “**main**”:
demo_buffer_failure()
