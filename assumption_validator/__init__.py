# assumption_validator/__init__.py
# earth-systems-physics
# CC0 — No Rights Reserved

from assumption_validator.registry import (
    REGISTRY,
    AssumptionBoundary,
    RiskLevel,
    assess_from_layer_states,
    global_confidence_multiplier,
    detect_cascade_risk,
    full_report,
    COUPLING_GRAPH,
)

from assumption_validator.monitors import (
    EarthSystemsMonitor,
    MonitorState,
    AssumptionRecord,
    CascadeSnapshot,
    Alert,
    print_report,
    print_alert,
)

__all__ = [
    "REGISTRY",
    "AssumptionBoundary",
    "RiskLevel",
    "assess_from_layer_states",
    "global_confidence_multiplier",
    "detect_cascade_risk",
    "full_report",
    "COUPLING_GRAPH",
    "EarthSystemsMonitor",
    "MonitorState",
    "AssumptionRecord",
    "CascadeSnapshot",
    "Alert",
    "print_report",
    "print_alert",
]

__version__ = "0.1.0"
