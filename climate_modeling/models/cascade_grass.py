# models/cascade_grass.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Cascade-enabled grass: the "true" system that combines the features a smooth
# single-state model omits — a respiration threshold (phase change), a bounded
# soil-carbon feedback, and accumulated heat-damage memory. Driven by
# heavy-tailed forcing it collapses toward zero once a run of extremes hits,
# while the smooth GrassCarbonBalance baseline merely dips and recovers.
#
# Calibrated so that under FatTailedForcing(T_mean=24, amplitude=6, df=3,
# scale=4) over ~150 hr the biomass minimum reaches ~0 across seeds, whereas
# the smooth baseline stays near ~4. The threshold uses a continuous (tanh)
# transition so the ODE right-hand side stays differentiable and fast.

import numpy as np

from .base import BaseModel, smoothstep


class CascadeGrass(BaseModel):
    """Three-state grass: biomass C, soil carbon S, heat-damage memory V.

    - Threshold: respiration rises sharply (but continuously) above
      ``threshold_temp`` via a steep ``smoothstep``.
    - Feedback: soil carbon S raises photosynthesis through a *saturating*
      term (bounded, so the system cannot explode to infinity).
    - Memory: time above threshold accumulates vulnerability V, which
      amplifies the respiration rise and leaves the system primed to collapse
      faster on the next extreme.
    """

    def __init__(self, params=None):
        self.P_max = 2.0                # matches GRASS_DEFAULTS rate scale
        self.T_opt = 25.0
        self.sigma = 8.0
        self.R_base = 0.01
        self.Q10 = 2.0
        self.threshold_temp = 33.0
        self.respiration_jump = 0.8     # extra respiration well above threshold
        self.threshold_k = 1.0          # smoothstep sharpness (per deg C)
        self.feedback_strength = 0.15   # max fractional photosynthesis boost
        self.feedback_half = 150.0      # soil carbon at half-saturation
        self.vulnerability_rate = 0.15  # memory gain per hr fully above thresh
        self.vuln_decay = 0.02          # slow recovery
        self.decomp_base = 0.004
        self.transfer = 0.004
        if params:
            for k, v in params.items():
                setattr(self, k, v)
        # State: [C biomass, S soil carbon, V vulnerability]
        self.initial_state = np.array([100.0, 120.0, 0.0])

    def derivative(self, t, state, forcing_value):
        C = max(state[0], 0.0)
        S = max(state[1], 0.0)
        V = max(state[2], 0.0)
        T = forcing_value["temperature"]
        light = forcing_value.get("light", 1.0)

        over = smoothstep(T - self.threshold_temp, self.threshold_k)

        if light:
            boost = 1.0 + self.feedback_strength * (S / (S + self.feedback_half))
            P = self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2)) * boost
        else:
            P = 0.0

        R = self.R_base * self.Q10 ** ((T - 20.0) / 10.0)
        R += self.respiration_jump * (1.0 + V) * over

        dV = self.vulnerability_rate * over - self.vuln_decay * V
        decomp = self.decomp_base * S * self.Q10 ** ((T - 20.0) / 10.0)

        dC = P - R * C - self.transfer * C
        dS = self.transfer * C - decomp
        return [dC, dS, dV]
