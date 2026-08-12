# simulation.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Level-0 harness: run a model under full vs aggregated forcing and quantify
# the Jensen-inequality bias that temporal averaging of a nonlinear response
# introduces. Used directly by experiments.py and reused by several audits.

import numpy as np

from .models.grass import GrassCarbonBalance
from .forcing import DiurnalTemperature, AggregatedForcingWrapper
from . import config


def run_grass_comparison(params=None, T_mean=20.0, amplitude=10.0,
                         duration_hours=None, max_step=None, initial_C=100.0):
    """Integrate the grass model under full diurnal forcing and under an
    aggregated (constant-mean-temperature) forcing with the same light cycle.

    Returns
    -------
    dict
        Final carbon under each forcing, the absolute error between them, and
        the raw trajectories (``t``/``y`` arrays) for plotting or inspection.
    """
    if duration_hours is None:
        duration_hours = config.SIM_DEFAULTS["duration_hours"]

    model = GrassCarbonBalance(params)
    full = DiurnalTemperature(T_mean=T_mean, amplitude=amplitude)
    agg = AggregatedForcingWrapper(full, T_mean)

    t_span = (0.0, duration_hours)
    t_full, y_full = model.simulate(full, [initial_C], t_span, max_step)
    t_agg, y_agg = model.simulate(agg, [initial_C], t_span, max_step)

    final_full = float(y_full[0, -1])
    final_agg = float(y_agg[0, -1])
    return {
        "final_C_full": final_full,
        "final_C_agg": final_agg,
        "error": abs(final_full - final_agg),
        "t_full": t_full, "y_full": y_full,
        "t_agg": t_agg, "y_agg": y_agg,
    }
