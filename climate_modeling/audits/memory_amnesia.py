# audits/memory_amnesia.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, compare_biomass
from ..models.base import BaseModel, smoothstep
from ..forcing import HeatwaveForcing


class _MemoryGrass(BaseModel):
    """True system: heat exposure accumulates damage V that suppresses future
    photosynthesis. After a heatwave the system stays depressed — it remembers."""

    def __init__(self):
        self.P_max = 2.0
        self.T_opt = 25.0
        self.sigma = 8.0
        self.R_base = 0.01
        self.Q10 = 2.0
        self.damage_rate = 0.2
        self.damage_decay = 0.01
        self.threshold = 30.0

    def derivative(self, t, state, forcing_value):
        C = max(state[0], 0.0)
        V = min(max(state[1], 0.0), 1.0)
        T = forcing_value["temperature"]
        light = forcing_value.get("light", 1.0)
        P = self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2)) * (1 - V)
        if not light:
            P = 0.0
        R = self.R_base * self.Q10 ** ((T - 20.0) / 10.0)
        over = smoothstep(T - self.threshold, k=2.0)
        dV = self.damage_rate * over - self.damage_decay * V
        return [P - R * C, dV]


class _AmnesiaGrass(BaseModel):
    """Audited system: no damage memory; photosynthesis depends only on the
    instantaneous temperature, so it 'recovers' fully after every heatwave."""

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


class MemoryAmnesiaAudit(BaseAudit):
    duration = 150.0

    def __init__(self):
        super().__init__(
            "Memory Amnesia",
            "True system accumulates heat damage that suppresses later growth; "
            "audited memoryless model overestimates post-heatwave recovery.")

    def generate_true_system(self):
        forcing = HeatwaveForcing(T_mean=22, amplitude=8, delta=12,
                                  window=(50.0, 90.0))
        return _MemoryGrass(), forcing, [100.0, 0.0]

    def generate_audited_model(self):
        return _AmnesiaGrass()

    def audited_init(self, true_init):
        return [float(true_init[0])]

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        t_true, y_true = true_output
        t_aud, y_aud = audited_output
        # compare recovery window after the heatwave
        post = t_true > 95.0
        true_post = float(np.mean(np.asarray(y_true[0])[post]))
        aud_b = np.interp(t_true, t_aud, np.asarray(y_aud[0]))
        aud_post = float(np.mean(aud_b[post]))
        m["post_heat_true"] = true_post
        m["post_heat_audited"] = aud_post
        m["failure_detected"] = aud_post > true_post + 3.0
        return m
