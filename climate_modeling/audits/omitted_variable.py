# audits/omitted_variable.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, compare_biomass
from ..models.base import BaseModel
from ..forcing import DiurnalTemperature, MoistureForcing


class _MoistureLimitedGrass(BaseModel):
    """True growth depends on a hidden soil-moisture driver as well as
    temperature. The modeller who never measured moisture assumes it constant."""

    def __init__(self, assumed_moisture=None):
        self.P_max = 2.0
        self.T_opt = 25.0
        self.sigma = 8.0
        self.R_base = 0.01
        self.Q10 = 2.0
        self.transfer = 0.004
        self.assumed_moisture = assumed_moisture   # None -> use forcing value

    def derivative(self, t, state, forcing_value):
        C = max(state[0], 0.0)
        T = forcing_value["temperature"]
        light = forcing_value.get("light", 1.0)
        moisture = (self.assumed_moisture if self.assumed_moisture is not None
                    else forcing_value.get("moisture", 0.5))
        P = self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2)) * moisture
        if not light:
            P = 0.0
        R = self.R_base * self.Q10 ** ((T - 20.0) / 10.0)
        return [P - R * C - self.transfer * C]


class OmittedVariableAudit(BaseAudit):
    duration = 150.0

    def __init__(self):
        super().__init__(
            "Omitted Variable",
            "True growth depends on a hidden, oscillating soil-moisture driver; "
            "audited model assumes constant moisture and mis-tracks the system.")

    def generate_true_system(self):
        base = DiurnalTemperature(T_mean=22, amplitude=8)
        forcing = MoistureForcing(base, period=50.0, mean=0.5, amp=0.35)
        return _MoistureLimitedGrass(assumed_moisture=None), forcing, [100.0]

    def generate_audited_model(self):
        return _MoistureLimitedGrass(assumed_moisture=0.7)

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        m["failure_detected"] = m["rmse"] > 3.0
        return m
