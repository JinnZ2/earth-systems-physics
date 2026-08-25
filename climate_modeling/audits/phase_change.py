# audits/phase_change.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, compare_biomass, first_below
from ..models.grass import GrassCarbonBalance
from ..models.base import smoothstep
from ..forcing import RampForcing


class _StepRespirationGrass(GrassCarbonBalance):
    """True system: respiration jumps sharply (steep smoothstep) above 35 C."""
    def _respiration(self, T):
        base = super()._respiration(T)
        return base + 0.8 * smoothstep(T - 35.0, k=5.0)   # near-step


class PhaseChangeAudit(BaseAudit):
    duration = 120.0

    def __init__(self):
        super().__init__(
            "Phase Change Blindness",
            "True system has a near-step respiration cliff at 35 C; the audited "
            "model is smooth and never anticipates the sudden die-off.")

    def generate_true_system(self):
        # ramp peaks just past the 35 C cliff: the smooth baseline survives at
        # reduced biomass, but the true near-step respiration kills the stand.
        return _StepRespirationGrass(), RampForcing(
            T_start=20, T_end=36, duration=120, amplitude=2), [100.0]

    def generate_audited_model(self):
        return GrassCarbonBalance()

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        t_true, y_true = true_output
        t_aud, y_aud = audited_output
        collapse_true = first_below(t_true, y_true[0], 10.0)
        collapse_aud = first_below(t_aud, y_aud[0], 10.0)
        m["collapse_true_hr"] = collapse_true
        m["collapse_audited_hr"] = collapse_aud
        # audited is dangerously optimistic: reads healthier through the cliff
        m["failure_detected"] = m["optimism_gap"] > 5.0 or m["rmse"] > 10.0
        return m
