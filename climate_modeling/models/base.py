# models/base.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Abstract model interface. Every model implements derivative(t, state,
# forcing_value) and inherits a scipy-backed simulate() harness. Forcing is a
# callable f(t) -> dict of instantaneous environmental scalars.

from abc import ABC, abstractmethod

import numpy as np
from scipy.integrate import solve_ivp

from .. import config


class BaseModel(ABC):
    """Abstract base for all dynamical models in the audit lab."""

    @abstractmethod
    def derivative(self, t, state, forcing_value):
        """Return d(state)/dt as a list.

        Parameters
        ----------
        t : float
            Time (hr).
        state : sequence of float
            Current state vector.
        forcing_value : dict
            Instantaneous environmental scalars, e.g.
            ``{"temperature": T, "light": 0/1}``.
        """
        raise NotImplementedError

    def simulate(self, forcing, initial_state, t_span=None, max_step=None):
        """Integrate the model over ``t_span`` under a forcing callable.

        Parameters
        ----------
        forcing : callable
            ``forcing(t)`` returns the forcing dict at time ``t``.
        initial_state : sequence of float
            Initial state vector.
        t_span : tuple of float, optional
            ``(t0, t1)`` integration window in hours. Defaults to
            ``(0, SIM_DEFAULTS["duration_hours"])``.
        max_step : float, optional
            Maximum integrator step (hr).

        Returns
        -------
        (t, y) : (ndarray, ndarray)
            ``t`` shape ``(n_times,)``; ``y`` shape ``(n_states, n_times)``.
        """
        if t_span is None:
            t_span = (0.0, config.SIM_DEFAULTS["duration_hours"])
        if max_step is None:
            max_step = config.SIM_DEFAULTS["max_step"]

        def rhs(t, y):
            return self.derivative(t, y, forcing(t))

        sol = solve_ivp(
            rhs, t_span, np.asarray(initial_state, dtype=float),
            max_step=max_step,
            rtol=config.SIM_DEFAULTS["rtol"],
            atol=config.SIM_DEFAULTS["atol"],
        )
        return sol.t, sol.y


def smoothstep(x, k=1.0):
    """Continuous 0->1 transition (steep tanh). A drop-in for a hard
    ``if x > 0`` threshold that keeps the ODE right-hand side differentiable,
    so adaptive integrators don't stall on a discontinuity. ``k`` sets
    sharpness (larger = closer to a step)."""
    return 0.5 * (1.0 + np.tanh(k * x))


def align(t_ref, t_src, y_src):
    """Linearly interpolate a source trajectory onto a reference time grid.

    Parameters
    ----------
    t_ref : ndarray
        Reference times to sample at.
    t_src, y_src : ndarray
        Source times and a single state row.

    Returns
    -------
    ndarray
        ``y_src`` resampled at ``t_ref`` (constant extrapolation at edges,
        which is numpy's ``interp`` default).
    """
    return np.interp(t_ref, t_src, y_src)
