# audits/stationarity.py
# climate_modeling
# CC0 — No Rights Reserved

from .base_audit import BaseAudit, compare_biomass
from ..models.grass import GrassCarbonBalance
from ..forcing import TrendForcing, DiurnalTemperature


class StationarityAudit(BaseAudit):
    """True system experiences a slow warming trend (non-stationary mean).
    The audited model was fitted/forced on an early stationary window and
    projects forward assuming the climate stays put, so its error grows with
    time as the true environment drifts away from the calibration window."""

    duration = 200.0

    def __init__(self):
        super().__init__(
            "Stationarity Assumption",
            "True forcing warms steadily; audited model assumes the early "
            "stationary climate persists. Error accumulates as the world drifts.")

    def generate_true_system(self):
        return GrassCarbonBalance(), TrendForcing(
            T_start=20.0, trend_rate=0.03, amplitude=5.0), [100.0]

    def generate_audited_model(self):
        return GrassCarbonBalance()

    def audited_forcing(self, true_forcing):
        # stationary projection: hold the mean at the initial value, same cycle
        return DiurnalTemperature(T_mean=20.0, amplitude=5.0)

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        m["failure_detected"] = m["rmse"] > 5.0
        return m
