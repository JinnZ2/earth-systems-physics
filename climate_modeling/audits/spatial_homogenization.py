# audits/spatial_homogenization.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, first_below
from ..models.base import BaseModel, smoothstep
from ..forcing import TwoPatchForcing


class _TwoPatchFire(BaseModel):
    """True system: a hot (vulnerable) patch and a cool (robust) patch. When
    the hot patch dies back, fire spreads to the cool patch. Collapse ignites
    locally and propagates — invisible to a spatially-averaged model."""

    def __init__(self):
        self.P_max = 2.0
        self.T_opt = 25.0
        self.sigma = 8.0
        self.R_base = 0.01
        self.Q10 = 2.0
        self.threshold = 33.0
        self.resp_jump = 0.8
        self.fire_spread = 0.05

    def _patch(self, C, T, light):
        P = self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2)) if light else 0.0
        R = self.R_base * self.Q10 ** ((T - 20.0) / 10.0)
        R += self.resp_jump * smoothstep(T - self.threshold, k=3.0)
        return P, R

    def derivative(self, t, state, forcing_value):
        C1 = max(state[0], 0.0)
        C2 = max(state[1], 0.0)
        T1 = forcing_value["temperature_1"]
        T2 = forcing_value["temperature_2"]
        light = forcing_value.get("light", 1.0)
        P1, R1 = self._patch(C1, T1, light)
        P2, R2 = self._patch(C2, T2, light)
        # fire spreads to patch 2 once patch 1 has collapsed
        fire = self.fire_spread * C2 * smoothstep(15.0 - C1, k=1.0)
        dC1 = P1 - R1 * C1
        dC2 = P2 - R2 * C2 - fire
        return [dC1, dC2]


class _SinglePatchAverage(BaseModel):
    """Audited system: one homogeneous patch at the mean of the two
    temperatures. The average never crosses the threshold the hot patch does."""

    def __init__(self):
        self.P_max = 2.0
        self.T_opt = 25.0
        self.sigma = 8.0
        self.R_base = 0.01
        self.Q10 = 2.0

    def derivative(self, t, state, forcing_value):
        C = max(state[0], 0.0)
        T = 0.5 * (forcing_value["temperature_1"] + forcing_value["temperature_2"])
        light = forcing_value.get("light", 1.0)
        P = self.P_max * np.exp(-((T - self.T_opt) ** 2) / (2 * self.sigma ** 2)) if light else 0.0
        R = self.R_base * self.Q10 ** ((T - 20.0) / 10.0)
        return [P - R * C]


class SpatialHomogenizationAudit(BaseAudit):
    duration = 150.0

    def __init__(self):
        super().__init__(
            "Spatial Homogenization",
            "True system: two patches, a vulnerable one ignites and fire spreads. "
            "Audited model averages space and never crosses the local threshold.")

    def generate_true_system(self):
        return _TwoPatchFire(), TwoPatchForcing(
            T_mean1=32, T_mean2=22, amplitude=4), [100.0, 100.0]

    def generate_audited_model(self):
        return _SinglePatchAverage()

    def audited_init(self, true_init):
        return [float(true_init[0])]

    def compute_audit_metrics(self, true_output, audited_output):
        t_true, y_true = true_output
        t_aud, y_aud = audited_output
        total_true = np.asarray(y_true[0]) + np.asarray(y_true[1])
        aud_b = np.interp(t_true, t_aud, np.asarray(y_aud[0]))
        # compare per-patch-average true against single audited patch
        mean_patch_true = total_true / 2.0
        rmse = float(np.sqrt(np.mean((mean_patch_true - aud_b) ** 2)))
        collapse_true = first_below(t_true, mean_patch_true, 20.0)
        collapse_aud = first_below(t_aud, y_aud[0], 20.0)
        return {
            "rmse": rmse,
            "true_total_final": float(total_true[-1]),
            "audited_final": float(aud_b[-1]),
            "collapse_true_hr": collapse_true,
            "collapse_audited_hr": collapse_aud,
            "failure_detected": aud_b[-1] > mean_patch_true[-1] + 5.0,
        }
