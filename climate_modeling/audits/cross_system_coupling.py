# audits/cross_system_coupling.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, compare_biomass
from ..models.base import BaseModel
from ..forcing import WarmRampForcing


class _PollinatorPlant(BaseModel):
    """True system: plant reproduction REQUIRES pollinators (a saturating
    B/(B+B_half) factor gates growth), and the plant also suffers baseline
    mortality. Warming kills the temperature-sensitive pollinators first; once
    they are gone the plant can no longer reproduce and declines — a
    cross-system collapse that lags the temperature driver."""

    def __init__(self):
        self.r_plant = 0.08
        self.K = 100.0
        self.B_half = 10.0
        self.m_plant = 0.02
        self.poll_growth = 0.2
        self.poll_K = 50.0
        self.poll_death = 0.03
        self.heat_death = 0.02
        self.heat_thresh = 30.0

    def derivative(self, t, state, forcing_value):
        P = max(state[0], 0.0)
        B = max(state[1], 0.0)
        T = forcing_value["temperature"]
        pollination = B / (B + self.B_half)
        dP = self.r_plant * P * (1 - P / self.K) * pollination - self.m_plant * P
        dB = self.poll_growth * B * (1 - B / self.poll_K) - self.poll_death * B
        if T > self.heat_thresh:
            dB -= self.heat_death * (T - self.heat_thresh) * B
        return [dP, dB]


class _PlantOnly(BaseModel):
    """Audited system: assumes pollination is always fully available (the gate
    is pinned at 1). It never sees the pollinator collapse, so the plant holds
    near its mortality-limited equilibrium — the cross-system domino is
    invisible to it."""

    def __init__(self):
        self.r_plant = 0.08
        self.K = 100.0
        self.m_plant = 0.02

    def derivative(self, t, state, forcing_value):
        P = max(state[0], 0.0)
        dP = self.r_plant * P * (1 - P / self.K) - self.m_plant * P
        return [dP]


class CrossSystemCouplingAudit(BaseAudit):
    duration = 200.0

    def __init__(self):
        super().__init__(
            "Cross-System Coupling",
            "True system: plants depend on temperature-sensitive pollinators; "
            "warming collapses pollinators, then plants. Audited: plant only.")

    def generate_true_system(self):
        return _PollinatorPlant(), WarmRampForcing(T_start=26, rate=0.03), [50.0, 30.0]

    def generate_audited_model(self):
        return _PlantOnly()

    def audited_init(self, true_init):
        return [float(true_init[0])]

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        m["failure_detected"] = m["optimism_gap"] > 5.0 or m["rmse"] > 10.0
        return m
