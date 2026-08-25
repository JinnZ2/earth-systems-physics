# audits/threshold_smoothing.py
# climate_modeling
# CC0 — No Rights Reserved

from .base_audit import BaseAudit, compare_biomass, first_below
from ..models.grass import GrassCarbonBalance
from ..models.base import smoothstep
from ..forcing import RampForcing


class _SharpGrass(GrassCarbonBalance):
    """True: near-step respiration rise (sharp smoothstep)."""
    def _respiration(self, T):
        return super()._respiration(T) + 0.8 * smoothstep(T - 35.0, k=5.0)


class _WideGrass(GrassCarbonBalance):
    """Audited: same magnitude spread over a wide sigmoid — the transition is
    smeared across many degrees, so the onset appears earlier and gentler."""
    def _respiration(self, T):
        return super()._respiration(T) + 0.8 * smoothstep(T - 35.0, k=0.4)


class ThresholdSmoothingAudit(BaseAudit):
    duration = 120.0

    def __init__(self):
        super().__init__(
            "Threshold Smoothing",
            "True system: near-step respiration increase. Audited model spreads "
            "the same rise over a wide sigmoid, mis-timing the die-off.")

    def generate_true_system(self):
        return _SharpGrass(), RampForcing(
            T_start=20, T_end=40, duration=100, amplitude=3), [100.0]

    def generate_audited_model(self):
        return _WideGrass()

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        t_true, y_true = true_output
        t_aud, y_aud = audited_output
        m["collapse_true_hr"] = first_below(t_true, y_true[0], 10.0)
        m["collapse_audited_hr"] = first_below(t_aud, y_aud[0], 10.0)
        m["failure_detected"] = m["rmse"] > 5.0
        return m
