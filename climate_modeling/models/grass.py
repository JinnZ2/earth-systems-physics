# models/grass.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Grass carbon-balance model. The canonical "smooth, memoryless, single-state"
# model that most audits treat as the simplified (audited) baseline against a
# richer true system.

import numpy as np

from .base import BaseModel
from .. import config


class GrassCarbonBalance(BaseModel):
    """Single-state grass carbon pool driven by temperature and light.

    dC/dt = P(T, light) - R(T) * C - transfer * C

    Photosynthesis is a Gaussian response in temperature, gated by light.
    Respiration follows a Q10 (exponential) temperature law.
    """

    def __init__(self, params=None):
        p = dict(config.GRASS_DEFAULTS)
        if params:
            p.update(params)
        self.params = p
        self.P_max = p["P_max"]
        self.T_opt = p["T_opt"]
        self.sigma = p["sigma"]
        self.R_base = p["R_base"]
        self.Q10 = p["Q10"]
        self.transfer = p["transfer"]

    def _photosynthesis(self, T, light):
        """Gaussian temperature response (gC/hr); zero when unlit."""
        if not light:
            return 0.0
        return self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2))

    def _respiration(self, T):
        """Q10 respiration rate (1/hr) referenced to 20 deg C."""
        return self.R_base * self.Q10 ** ((T - 20.0) / 10.0)

    def derivative(self, t, state, forcing_value):
        C = max(state[0], 0.0)   # biomass is non-negative; clamp prevents the
        T = forcing_value["temperature"]  # -R*C runaway if C dips below zero
        light = forcing_value.get("light", 1.0)
        P = self._photosynthesis(T, light)
        R = self._respiration(T)
        dCdt = P - R * C - self.transfer * C
        return [dCdt]
