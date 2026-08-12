# audits/buffer_exhaustion.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, compare_biomass
from ..models.base import BaseModel
from ..forcing import HeatwaveForcing


class _BufferGrass(BaseModel):
    """True system: a soil-moisture buffer W sustains photosynthesis until it
    is drawn down by sustained heat. Once depleted, growth crashes suddenly —
    the slow trend hides a step response gated by a hidden reservoir."""

    def __init__(self):
        self.P_max = 2.0
        self.T_opt = 25.0
        self.sigma = 8.0
        self.R_base = 0.01
        self.Q10 = 2.0
        self.W_max = 50.0
        self.recharge = 0.02
        self.evap_rate = 0.6
        self.W_half = 25.0

    def derivative(self, t, state, forcing_value):
        C = max(state[0], 0.0)
        W = max(state[1], 0.0)
        T = forcing_value["temperature"]
        light = forcing_value.get("light", 1.0)
        moisture_factor = min(1.0, W / self.W_half)
        P = self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2)) * moisture_factor
        if not light:
            P = 0.0
        R = self.R_base * self.Q10 ** ((T - 20.0) / 10.0)
        dW = self.recharge * (self.W_max - W) - self.evap_rate * max(0.0, T - 25.0) * W / self.W_max
        return [P - R * C, dW]


class _NoBufferGrass(BaseModel):
    """Audited system: assumes soil moisture is never limiting."""

    def __init__(self):
        self.P_max = 2.0
        self.T_opt = 25.0
        self.sigma = 8.0
        self.R_base = 0.01
        self.Q10 = 2.0

    def derivative(self, t, state, forcing_value):
        C = max(state[0], 0.0)
        T = forcing_value["temperature"]
        light = forcing_value.get("light", 1.0)
        P = self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2))
        if not light:
            P = 0.0
        R = self.R_base * self.Q10 ** ((T - 20.0) / 10.0)
        return [P - R * C]


class BufferExhaustionAudit(BaseAudit):
    duration = 200.0

    def __init__(self):
        super().__init__(
            "Buffer Exhaustion",
            "True system: a soil-moisture buffer holds until sustained heat "
            "drains it, then growth crashes. Audited model assumes no buffer.")

    def generate_true_system(self):
        forcing = HeatwaveForcing(T_mean=24, amplitude=8, delta=12,
                                  window=(80.0, 160.0))
        return _BufferGrass(), forcing, [100.0, 50.0]

    def generate_audited_model(self):
        return _NoBufferGrass()

    def audited_init(self, true_init):
        return [float(true_init[0])]

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        t_true, y_true = true_output
        t_aud, y_aud = audited_output
        post = t_true > 160.0
        true_post = float(np.mean(np.asarray(y_true[0])[post]))
        aud_b = np.interp(t_true, t_aud, np.asarray(y_aud[0]))
        aud_post = float(np.mean(aud_b[post]))
        m["post_heat_true"] = true_post
        m["post_heat_audited"] = aud_post
        m["failure_detected"] = aud_post > true_post + 3.0
        return m
