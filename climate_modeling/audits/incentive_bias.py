# audits/incentive_bias.py
# climate_modeling
# CC0 — No Rights Reserved

import numpy as np

from .base_audit import BaseAudit, first_below
from ..models.cascade_grass import CascadeGrass
from ..forcing import FatTailedForcing


class IncentiveBiasAudit(BaseAudit):
    """A model-selection contest that rewards parsimony. The true system is the
    cascade grass. A simple linear biomass~temperature model is fit to the
    first-half history (where it looks fine) and 'wins' on simplicity — then it
    completely misses the collapse in the second half. Simplicity was selected
    for, accuracy about collapse speed was selected against.

    Uses numpy least squares (no sklearn dependency).
    """

    duration = 150.0

    def __init__(self):
        super().__init__(
            "Incentive Bias",
            "Model selection rewards a simple linear fit that tracks the calm "
            "first half and misses the cascade collapse in the second half.")

    def generate_true_system(self):
        m = CascadeGrass()
        return m, FatTailedForcing(
            T_mean=24, amplitude=6, df=3, scale=4, seed=99), m.initial_state

    def generate_audited_model(self):
        # audited "model" is a fitted linear predictor, built in run()
        return None

    def run(self):
        true_model, forcing, init = self.generate_true_system()
        t_true, y_true = true_model.simulate(forcing, init, (0.0, self.duration))
        biomass = np.asarray(y_true[0])
        temps = np.array([forcing(tt)["temperature"] for tt in t_true])

        # fit linear biomass ~ a*T + b on the first half (the "training window")
        split = len(t_true) // 2
        A = np.vstack([temps[:split], np.ones(split)]).T
        coef, *_ = np.linalg.lstsq(A, biomass[:split], rcond=None)
        pred = coef[0] * temps + coef[1]

        rmse = float(np.sqrt(np.mean((biomass - pred) ** 2)))
        rmse_train = float(np.sqrt(np.mean((biomass[:split] - pred[:split]) ** 2)))
        rmse_test = float(np.sqrt(np.mean((biomass[split:] - pred[split:]) ** 2)))
        collapse_true = first_below(t_true, biomass, 10.0)
        collapse_pred = first_below(t_true, pred, 10.0)

        failure = rmse_test > 1.5 * rmse_train + 3.0 or (
            np.isfinite(collapse_true) and not np.isfinite(collapse_pred))
        return {
            "audit_name": self.name,
            "failure_detected": bool(failure),
            "metrics": {
                "rmse": rmse,
                "rmse_train": rmse_train,
                "rmse_test": rmse_test,
                "collapse_true_hr": collapse_true,
                "collapse_predicted_hr": collapse_pred,
                "linear_slope": float(coef[0]),
            },
            "true_final": float(biomass[-1]),
            "audited_final": float(pred[-1]),
        }

    def compute_audit_metrics(self, true_output, audited_output):
        # not used: run() is overridden for the regression contest
        raise NotImplementedError
