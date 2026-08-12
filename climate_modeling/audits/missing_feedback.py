# audits/missing_feedback.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, compare_biomass
from ..models.base import BaseModel
from ..models.grass import GrassCarbonBalance
from ..forcing import DiurnalTemperature


class _GrassSoilFeedback(BaseModel):
    """True system: grass biomass C coupled to soil carbon S, where soil
    fertility feeds back into photosynthesis. A reciprocal loop the audited
    single-state model omits entirely."""

    def __init__(self):
        self.P_max = 2.0
        self.T_opt = 25.0
        self.sigma = 8.0
        self.R_base = 0.01
        self.Q10 = 2.0
        self.transfer = 0.004
        self.decomp_base = 0.004
        self.feedback = 0.02

    def derivative(self, t, state, forcing_value):
        C = max(state[0], 0.0)
        S = max(state[1], 0.0)
        T = forcing_value["temperature"]
        light = forcing_value.get("light", 1.0)
        P = self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2))
        P = P * (1 + self.feedback * S) if light else 0.0
        R = self.R_base * self.Q10 ** ((T - 20.0) / 10.0)
        dC = P - R * C - self.transfer * C
        dS = self.transfer * C - self.decomp_base * S * self.Q10 ** ((T - 20.0) / 10.0)
        return [dC, dS]


class MissingFeedbackAudit(BaseAudit):
    duration = 150.0

    def __init__(self):
        super().__init__(
            "Missing Feedback",
            "True system: grass-soil fertility feedback. Audited model ignores "
            "soil carbon, missing the reciprocal loop that amplifies dynamics.")

    def generate_true_system(self):
        return _GrassSoilFeedback(), DiurnalTemperature(T_mean=23, amplitude=8), [100.0, 200.0]

    def generate_audited_model(self):
        return GrassCarbonBalance()

    def audited_init(self, true_init):
        return [float(true_init[0])]

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        m["failure_detected"] = m["rmse"] > 5.0
        return m
