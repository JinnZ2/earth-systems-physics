# audits/gaussian_blindness.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, compare_biomass
from ..models.base import BaseModel
from ..forcing import FatTailedForcing, GaussianForcing


class _ConvexHeatMortalityGrass(BaseModel):
    """True system whose heat mortality is CONVEX in the excursion magnitude:
    extra loss ~ (T - threshold)_+^2. A rare far-tail spike therefore does
    disproportionately more damage than several moderate crossings of the same
    total variance — the exact regime where the shape of the tail, not just its
    variance, decides the outcome."""

    def __init__(self, threshold=33.0, k_mort=0.02):
        self.P_max = 2.0
        self.T_opt = 25.0
        self.sigma = 8.0
        self.R_base = 0.01
        self.Q10 = 2.0
        self.transfer = 0.004
        self.threshold = threshold
        self.k_mort = k_mort

    def derivative(self, t, state, forcing_value):
        C = max(state[0], 0.0)
        T = forcing_value["temperature"]
        light = forcing_value.get("light", 1.0)
        P = self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2))
        if not light:
            P = 0.0
        R = self.R_base * self.Q10 ** ((T - 20.0) / 10.0)
        exc = max(0.0, T - self.threshold)
        mortality = self.k_mort * exc * exc
        return [P - R * C - self.transfer * C - mortality * C]


class GaussianBlindnessAudit(BaseAudit):
    """True forcing is heavy-tailed; the audited model assumes Gaussian noise
    of the *same variance*. Because damage is convex in excursion magnitude,
    the fat-tailed spikes collapse the true system while the variance-matched
    Gaussian — which almost never reaches that far into the tail — predicts the
    stand survives."""

    duration = 150.0

    def __init__(self):
        super().__init__(
            "Gaussian Blindness",
            "True forcing: fat-tailed (Student's t) extremes with convex heat "
            "mortality. Audited: Gaussian noise of equal variance, blind to the "
            "far-tail spikes that actually drive collapse.")
        self._true_forcing = None

    def generate_true_system(self):
        self._true_forcing = FatTailedForcing(
            T_mean=24, amplitude=5, df=3, scale=3.5, seed=13)
        return _ConvexHeatMortalityGrass(), self._true_forcing, [60.0]

    def generate_audited_model(self):
        return _ConvexHeatMortalityGrass()

    def audited_forcing(self, true_forcing):
        var = self._true_forcing.variance()   # match marginal variance exactly
        return GaussianForcing(T_mean=24, amplitude=5, variance=var, seed=113)

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        m["failure_detected"] = m["audited_min"] > m["true_min"] + 3.0
        return m
