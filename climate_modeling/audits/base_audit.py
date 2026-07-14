# audits/base_audit.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Abstract audit. Each audit is a controlled experiment where the TRUE
# generative process is known (we built it), so any discrepancy from the
# SIMPLIFIED (audited) model is a genuine failure of a modelling assumption.
#
# The contract an audit implements:
#   generate_true_system()   -> (model, forcing, initial_state)
#   generate_audited_model() -> model
#   compute_audit_metrics(true_output, audited_output) -> dict incl.
#                               "failure_detected": bool
# Optional hooks let the audited run use different forcing / initial state:
#   audited_forcing(true_forcing) -> forcing
#   audited_init(true_init)       -> initial_state
#
# duration (hr) is an instance attribute; default 100.

from abc import ABC, abstractmethod

import numpy as np


class BaseAudit(ABC):
    duration = 100.0

    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def generate_true_system(self):
        """Return (model, forcing, initial_state) for the true process."""
        raise NotImplementedError

    @abstractmethod
    def generate_audited_model(self):
        """Return the simplified model under audit."""
        raise NotImplementedError

    @abstractmethod
    def compute_audit_metrics(self, true_output, audited_output):
        """Return a metrics dict including a ``failure_detected`` bool.

        ``true_output`` and ``audited_output`` are each ``(t, y)`` tuples.
        """
        raise NotImplementedError

    # --- optional hooks ---------------------------------------------------
    def audited_forcing(self, true_forcing):
        """Forcing to drive the audited model. Default: same as truth."""
        return true_forcing

    def audited_init(self, true_init):
        """Initial state for the audited model. Default: same as truth."""
        return true_init

    # --- driver -----------------------------------------------------------
    def run(self):
        true_model, forcing, init = self.generate_true_system()
        t_span = (0.0, self.duration)
        t_true, y_true = true_model.simulate(forcing, init, t_span)

        audited_model = self.generate_audited_model()
        a_forcing = self.audited_forcing(forcing)
        a_init = self.audited_init(init)
        t_aud, y_aud = audited_model.simulate(a_forcing, a_init, t_span)

        metrics = self.compute_audit_metrics((t_true, y_true), (t_aud, y_aud))
        failure = metrics.pop("failure_detected")
        return {
            "audit_name": self.name,
            "failure_detected": bool(failure),
            "metrics": metrics,
            "true_final": float(y_true[0, -1]),
            "audited_final": float(y_aud[0, -1]),
        }


def compare_biomass(true_output, audited_output):
    """Align the audited biomass row onto the true time grid and summarise the
    discrepancy. Returns rmse, the signed 'optimism gap' (audited minus true,
    positive = audited reads healthier than truth), and both minima — the
    shared vocabulary every audit's ``compute_audit_metrics`` builds on.
    """
    t_true, y_true = true_output
    t_aud, y_aud = audited_output
    true_b = np.asarray(y_true[0])
    aud_b = np.interp(t_true, t_aud, np.asarray(y_aud[0]))
    rmse = float(np.sqrt(np.mean((true_b - aud_b) ** 2)))
    optimism_gap = float(np.mean(aud_b - true_b))
    return {
        "rmse": rmse,
        "optimism_gap": optimism_gap,
        "true_min": float(true_b.min()),
        "audited_min": float(aud_b.min()),
        "true_final": float(true_b[-1]),
        "audited_final": float(aud_b[-1]),
    }


def first_below(t, series, level):
    """Interpolated time at which ``series`` first drops below ``level``.

    Returns ``inf`` if it never does. Used for collapse-timing metrics so a
    model that merely delays collapse still registers a finite gap.
    """
    series = np.asarray(series)
    below = np.where(series < level)[0]
    if below.size == 0:
        return float("inf")
    i = int(below[0])
    if i == 0:
        return float(t[0])
    y0, y1 = series[i - 1], series[i]
    t0, t1 = t[i - 1], t[i]
    if y1 == y0:
        return float(t1)
    frac = (level - y0) / (y1 - y0)
    return float(t0 + frac * (t1 - t0))
