# audits/audit_registry.py
# climate_modeling
# CC0 — No Rights Reserved
#
# The full audit suite. Every entry is a controlled experiment whose true
# generative process is known, so a detected failure is a genuine failure of a
# modelling simplification. Many target the same underlying danger: systematic
# UNDERESTIMATION of how fast a system can collapse.

from .phase_change import PhaseChangeAudit
from .stationarity import StationarityAudit
from .missing_feedback import MissingFeedbackAudit
from .omitted_variable import OmittedVariableAudit
from .data_aggregation import DataAggregationAudit
from .cascade_speed import CascadeSpeedAudit
from .missing_positive_feedback import MissingPositiveFeedbackAudit
from .threshold_smoothing import ThresholdSmoothingAudit
from .temporal_aggregation_extremes import TemporalAggregationExtremesAudit
from .spatial_homogenization import SpatialHomogenizationAudit
from .memory_amnesia import MemoryAmnesiaAudit
from .cross_system_coupling import CrossSystemCouplingAudit
from .buffer_exhaustion import BufferExhaustionAudit
from .clustered_extremes import ClusteredExtremesAudit
from .gaussian_blindness import GaussianBlindnessAudit
from .incentive_bias import IncentiveBiasAudit


def all_audits():
    """Return a fresh list of audit instances (stateless to re-run)."""
    return [
        PhaseChangeAudit(),
        StationarityAudit(),
        MissingFeedbackAudit(),
        OmittedVariableAudit(),
        DataAggregationAudit(),
        CascadeSpeedAudit(),
        MissingPositiveFeedbackAudit(),
        ThresholdSmoothingAudit(),
        TemporalAggregationExtremesAudit(),
        SpatialHomogenizationAudit(),
        MemoryAmnesiaAudit(),
        CrossSystemCouplingAudit(),
        BufferExhaustionAudit(),
        ClusteredExtremesAudit(),
        GaussianBlindnessAudit(),
        IncentiveBiasAudit(),
    ]


ALL_AUDITS = all_audits()
