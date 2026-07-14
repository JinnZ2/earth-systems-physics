# audits/temporal_aggregation_extremes.py
# climate_modeling
# CC0 — No Rights Reserved

from .base_audit import BaseAudit, compare_biomass, first_below
from ..models.cascade_grass import CascadeGrass
from ..models.grass import GrassCarbonBalance
from ..forcing import FatTailedForcing
from .data_aggregation import DailyMeanForcing


class TemporalAggregationExtremesAudit(BaseAudit):
    """Like the data-aggregation audit, but the true system is the
    cascade-capable grass: short-duration extremes trigger a threshold+memory
    collapse that vanishes entirely once the forcing is averaged to daily
    means. Averaging doesn't just bias the estimate — it erases the cascade."""

    duration = 150.0

    def __init__(self):
        super().__init__(
            "Temporal Aggregation Extremes",
            "True cascade system crashes on hourly extremes; audited model on "
            "daily-mean forcing never sees the peaks and predicts no collapse.")

    def generate_true_system(self):
        m = CascadeGrass()
        return m, FatTailedForcing(
            T_mean=24, amplitude=6, df=3, scale=4, seed=7), m.initial_state

    def generate_audited_model(self):
        return GrassCarbonBalance()

    def audited_init(self, true_init):
        return [float(true_init[0])]

    def audited_forcing(self, true_forcing):
        return DailyMeanForcing(true_forcing, self.duration)

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        t_true, y_true = true_output
        m["collapse_true_hr"] = first_below(t_true, y_true[0], 10.0)
        m["failure_detected"] = m["audited_min"] > m["true_min"] + 2.0
        return m
