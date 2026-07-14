# audits/clustered_extremes.py
# climate_modeling
# CC0 — No Rights Reserved

from .base_audit import BaseAudit, compare_biomass
from ..models.cascade_grass import CascadeGrass
from ..forcing import AutoregressiveExtremesForcing, GaussianForcing


class ClusteredExtremesAudit(BaseAudit):
    """True forcing has AR(1) heavy-tailed noise: extremes arrive in clusters
    (a heatwave that persists). The audited model assumes independent Gaussian
    noise of the *same variance*, so it never produces the sustained run of
    extremes that exhausts the cascade system's recovery between shocks."""

    duration = 150.0

    # AR(1) parameters (module-level so the matched-variance Gaussian can be
    # built from exactly the same numbers).
    _T_MEAN = 23.0
    _AMP = 4.0
    _AR = 0.90
    _DF = 3
    _SCALE = 1.8
    _VULN_DECAY = 0.12   # fast enough that isolated spikes recover between them

    def __init__(self):
        super().__init__(
            "Clustered Extremes",
            "True forcing: autocorrelated heavy-tailed extremes (clustered "
            "heatwaves that persist). Audited: independent Gaussian noise of the "
            "same MARGINAL variance — brief isolated crossings the cascade "
            "recovers from, so it never sees the sustained run that collapses "
            "the true system.")

    def _marginal_variance(self):
        # Var of AR(1) with heavy-tailed innovations:
        #   innovation var = scale^2 * df/(df-2); marginal = innov / (1 - ar^2)
        innov = self._SCALE ** 2 * self._DF / (self._DF - 2)
        return innov / (1.0 - self._AR ** 2)

    def generate_true_system(self):
        m = CascadeGrass({"vuln_decay": self._VULN_DECAY})
        forcing = AutoregressiveExtremesForcing(
            T_mean=self._T_MEAN, amplitude=self._AMP, ar_coef=self._AR,
            df=self._DF, scale=self._SCALE, seed=7)
        return m, forcing, m.initial_state

    def generate_audited_model(self):
        return CascadeGrass({"vuln_decay": self._VULN_DECAY})

    def audited_forcing(self, true_forcing):
        # same marginal variance, serial dependence destroyed
        return GaussianForcing(
            T_mean=self._T_MEAN, amplitude=self._AMP,
            variance=self._marginal_variance(), seed=123)

    def compute_audit_metrics(self, true_output, audited_output):
        m = compare_biomass(true_output, audited_output)
        m["marginal_variance"] = self._marginal_variance()
        # clustered forcing digs a deeper hole than independent noise
        m["failure_detected"] = m["audited_min"] > m["true_min"] + 2.0
        return m
