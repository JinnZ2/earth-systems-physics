# audits/cascade_speed.py
# climate_modeling
# CC0 — No Rights Reserved

from .base_audit import BaseAudit, compare_biomass, first_below
from ..models.cascade_grass import CascadeGrass
from ..models.grass import GrassCarbonBalance
from ..forcing import FatTailedForcing


class CascadeSpeedAudit(BaseAudit):
    """The headline audit: the true system combines threshold, soil feedback,
    and heat-damage memory, driven by fat-tailed extremes. It collapses toward
    zero; the smooth, memoryless, single-state audited model only dips and
    recovers, systematically underestimating how fast collapse arrives."""

    duration = 150.0

    def __init__(self):
        super().__init__(
            "Cascade Speed Blindness",
            "True system: threshold + soil feedback + vulnerability memory under "
            "fat-tailed extremes. Audited: smooth, memoryless, single-state.")

    def generate_true_system(self):
        m = CascadeGrass()
        return m, FatTailedForcing(
            T_mean=24, amplitude=6, df=3, scale=4, seed=42), m.initial_state

    def generate_audited_model(self):
        return GrassCarbonBalance()

    def audited_init(self, true_init):
        return [float(true_init[0])]   # audited tracks biomass only

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        t_true, y_true = true_output
        m["collapse_true_hr"] = first_below(t_true, y_true[0], 10.0)
        t_aud, y_aud = audited_output
        m["collapse_audited_hr"] = first_below(t_aud, y_aud[0], 10.0)
        # true minimum crashes to ~0 while audited stays well above it
        m["failure_detected"] = (m["audited_min"] > m["true_min"] + 2.0)
        return m
