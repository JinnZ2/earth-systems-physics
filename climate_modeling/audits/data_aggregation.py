# audits/data_aggregation.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, compare_biomass
from ..models.grass import GrassCarbonBalance
from ..forcing import FatTailedForcing


class DailyMeanForcing:
    """Replace a full forcing's temperature with its per-day mean (keeping the
    diurnal light schedule). This is what fitting/forcing on daily-aggregated
    data does — it discards the sub-daily extremes that drive nonlinear loss."""

    def __init__(self, full_forcing, duration, period=24.0, day_fraction=0.5):
        self.period = period
        self.day_fraction = day_fraction
        n_days = int(duration // period) + 1
        self._means = []
        for d in range(n_days):
            temps = [full_forcing(tt)["temperature"]
                     for tt in np.arange(d * period, (d + 1) * period, 1.0)]
            self._means.append(float(np.mean(temps)))

    def __call__(self, t):
        idx = min(int(t // self.period), len(self._means) - 1)
        phase = (t % self.period) / self.period
        return {"temperature": self._means[idx],
                "light": 1.0 if phase < self.day_fraction else 0.0}


class DataAggregationAudit(BaseAudit):
    duration = 150.0

    def __init__(self):
        super().__init__(
            "Data Aggregation Error",
            "True system driven by hourly fat-tailed temperature; audited model "
            "sees only daily means. Jensen's inequality biases the response.")
        self._forcing = None

    def generate_true_system(self):
        self._forcing = FatTailedForcing(
            T_mean=22, amplitude=6, df=3, scale=5, seed=99)
        return GrassCarbonBalance(), self._forcing, [100.0]

    def generate_audited_model(self):
        return GrassCarbonBalance()

    def audited_forcing(self, true_forcing):
        return DailyMeanForcing(true_forcing, self.duration)

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        m["failure_detected"] = m["rmse"] > 3.0
        return m
