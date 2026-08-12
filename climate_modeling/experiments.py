# experiments.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Level-1 experiments: predefined hypothesis tests on the ecological models
# themselves (as opposed to the Level-2 audits, which are experiments ABOUT
# the modelling process). These quantify the aggregation bias that averaging a
# nonlinear response introduces.

from .simulation import run_grass_comparison


def experiment_aggregation_bias(amplitude=10.0, Q10=2.0):
    """Aggregation (constant-mean) forcing vs full diurnal forcing.

    Because both photosynthesis (Gaussian) and respiration (Q10) are nonlinear
    in temperature, replacing the diurnal cycle with its mean biases the
    predicted carbon pool (Jensen's inequality). Returns the absolute error.
    """
    r = run_grass_comparison(params={"Q10": Q10}, amplitude=amplitude)
    return r["error"]


def experiment_amplitude_sweep(amplitudes=(0.0, 5.0, 10.0, 15.0), Q10=2.0):
    """Hold the mean fixed, sweep the diurnal amplitude. A flat cycle
    (amplitude 0) has zero aggregation gap; wider cycles generally open a
    larger one. The relationship is NOT strictly monotonic, because
    photosynthesis is non-monotonic in temperature (Gaussian about T_opt), so
    a wide swing can straddle the optimum and partly cancel — a feature of the
    nonlinearity, not a bug. The robust claim is: amplitude 0 -> no bias, and
    a nonlinear response under a non-trivial cycle -> nonzero bias.

    Returns a list of (amplitude, error) pairs.
    """
    return [(a, experiment_aggregation_bias(amplitude=a, Q10=Q10))
            for a in amplitudes]


if __name__ == "__main__":
    print("Aggregation bias vs diurnal amplitude (Q10=2):")
    for amp, err in experiment_amplitude_sweep():
        print(f"  amplitude={amp:>5.1f} C -> error={err:.4f} gC")
