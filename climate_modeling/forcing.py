# forcing.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Environmental signal generators. Each is a callable f(t) -> dict returning
# the instantaneous forcing scalars a model consumes. Stochastic generators
# are seeded for reproducibility. These are the "experiment inputs": constant,
# ramping, trending, fat-tailed, autocorrelated-extreme, and multi-patch.

import numpy as np

from . import config


class DiurnalTemperature:
    """Full diurnal temperature cycle with a day/night light flag."""

    def __init__(self, T_mean=None, amplitude=None, day_fraction=None, period=None):
        d = config.FORCING_DEFAULTS
        self.T_mean = d["T_mean"] if T_mean is None else T_mean
        self.amplitude = d["amplitude"] if amplitude is None else amplitude
        self.day_fraction = d["day_fraction"] if day_fraction is None else day_fraction
        self.period = d["period"] if period is None else period

    def __call__(self, t):
        T = self.T_mean + self.amplitude * np.sin(2 * np.pi * t / self.period)
        phase = (t % self.period) / self.period
        light = 1.0 if phase < self.day_fraction else 0.0
        return {"temperature": T, "light": light}


class AggregatedForcingWrapper:
    """Keep a full forcing's light schedule but replace temperature with a
    constant mean — the correct 'aggregated' counterpart for Jensen-gap tests."""

    def __init__(self, full_forcing, T_mean):
        self.full_forcing = full_forcing
        self.T_mean = T_mean

    def __call__(self, t):
        raw = self.full_forcing(t)
        return {"temperature": self.T_mean, "light": raw["light"]}


class RampForcing:
    """Temperature ramps linearly from T_start to T_end over ``duration`` hr,
    with a diurnal cycle superimposed. Holds at T_end afterwards."""

    def __init__(self, T_start=20.0, T_end=40.0, duration=100.0,
                 amplitude=5.0, day_fraction=0.5, period=24.0):
        self.T_start = T_start
        self.T_end = T_end
        self.duration = duration
        self.amplitude = amplitude
        self.day_fraction = day_fraction
        self.period = period

    def __call__(self, t):
        if t <= self.duration:
            trend = self.T_start + (self.T_end - self.T_start) * t / self.duration
        else:
            trend = self.T_end
        diurnal = self.amplitude * np.sin(2 * np.pi * t / self.period)
        T = trend + diurnal
        phase = (t % self.period) / self.period
        light = 1.0 if phase < self.day_fraction else 0.0
        return {"temperature": T, "light": light}


class TrendForcing:
    """Diurnal cycle riding a slow linear warming trend (non-stationary mean)."""

    def __init__(self, T_start=20.0, trend_rate=0.02, amplitude=10.0,
                 day_fraction=0.5, period=24.0):
        self.T_start = T_start
        self.trend_rate = trend_rate      # deg C per hr
        self.amplitude = amplitude
        self.day_fraction = day_fraction
        self.period = period

    def __call__(self, t):
        trend = self.T_start + self.trend_rate * t
        diurnal = self.amplitude * np.sin(2 * np.pi * t / self.period)
        T = trend + diurnal
        phase = (t % self.period) / self.period
        light = 1.0 if phase < self.day_fraction else 0.0
        return {"temperature": T, "light": light}


# NOTE ON STOCHASTIC FORCING + ODEs
# A forcing driven by a fresh random draw on every call is NOT a function of t:
# solve_ivp evaluates the RHS at many internal and rejected steps, so per-call
# noise turns the RHS into white noise, the integrator stalls, and results
# depend on the number of evaluations. The correct construction pre-samples the
# noise on a fixed grid at construction time and INTERPOLATES in __call__, so
# forcing(t) is deterministic, reproducible, and integrator-friendly.
# A physical temperature cap keeps heavy-tailed spikes from producing absurd
# respiration transients.

TEMP_CAP_C = 55.0


class _PreSampledNoiseForcing:
    """Base for stochastic forcings with noise pre-sampled on a grid.

    Subclasses fill ``self._noise`` (aligned to ``self.grid``) in ``__init__``.
    ``__call__`` interpolates the noise, adds the diurnal cycle, applies the
    temperature cap, and returns the forcing dict.
    """

    def __init__(self, T_mean, amplitude, day_fraction, period, horizon, dt):
        self.T_mean = T_mean
        self.amplitude = amplitude
        self.day_fraction = day_fraction
        self.period = period
        self.grid = np.arange(0.0, horizon + dt, dt)
        self._noise = np.zeros_like(self.grid)

    def noise_at(self, t):
        return float(np.interp(t, self.grid, self._noise))

    def __call__(self, t):
        diurnal = self.amplitude * np.sin(2 * np.pi * t / self.period)
        T = min(self.T_mean + diurnal + self.noise_at(t), TEMP_CAP_C)
        phase = (t % self.period) / self.period
        light = 1.0 if phase < self.day_fraction else 0.0
        return {"temperature": T, "light": light}


class FatTailedForcing(_PreSampledNoiseForcing):
    """Diurnal cycle plus pre-sampled heavy-tailed (Student's t) noise ->
    occasional extreme spikes a Gaussian model of equal variance rarely makes."""

    def __init__(self, T_mean=20.0, amplitude=8.0, df=3, scale=3.0,
                 day_fraction=0.5, period=24.0, seed=123, horizon=300.0, dt=0.25):
        super().__init__(T_mean, amplitude, day_fraction, period, horizon, dt)
        self.df = df
        self.scale = scale
        rng = np.random.default_rng(seed)
        self._noise = rng.standard_t(df, size=self.grid.size) * scale

    def variance(self):
        """Variance of the noise term (finite for df > 2)."""
        if self.df > 2:
            return self.scale ** 2 * self.df / (self.df - 2)
        return float("inf")


class AutoregressiveExtremesForcing(_PreSampledNoiseForcing):
    """AR(1) heavy-tailed noise -> clustered heatwaves (serial dependence in
    the extremes) that independent-noise models never generate. Pre-sampled."""

    def __init__(self, T_mean=20.0, amplitude=8.0, ar_coef=0.7,
                 df=3, scale=3.0, day_fraction=0.5, period=24.0, seed=42,
                 horizon=300.0, dt=0.25):
        super().__init__(T_mean, amplitude, day_fraction, period, horizon, dt)
        self.ar_coef = ar_coef
        rng = np.random.default_rng(seed)
        innov = rng.standard_t(df, size=self.grid.size) * scale
        noise = np.empty_like(innov)
        prev = 0.0
        for i, e in enumerate(innov):
            prev = ar_coef * prev + e
            noise[i] = prev
        self._noise = noise


class GaussianForcing(_PreSampledNoiseForcing):
    """Diurnal cycle plus pre-sampled independent Gaussian noise of a chosen
    variance — the naive counterpart to the heavy-tailed forcings."""

    def __init__(self, T_mean=20.0, amplitude=8.0, variance=9.0,
                 day_fraction=0.5, period=24.0, seed=7, horizon=300.0, dt=0.25):
        super().__init__(T_mean, amplitude, day_fraction, period, horizon, dt)
        rng = np.random.default_rng(seed)
        self._noise = rng.normal(0.0, float(np.sqrt(variance)), size=self.grid.size)


class HeatwaveForcing:
    """Diurnal cycle with a scheduled heatwave window (a fixed +delta over a
    time interval) — deterministic, for memory / buffer-exhaustion audits."""

    def __init__(self, T_mean=22.0, amplitude=8.0, delta=10.0,
                 window=(50.0, 70.0), day_fraction=0.5, period=24.0):
        self.T_mean = T_mean
        self.amplitude = amplitude
        self.delta = delta
        self.window = window
        self.day_fraction = day_fraction
        self.period = period

    def __call__(self, t):
        T = self.T_mean + self.amplitude * np.sin(2 * np.pi * t / self.period)
        if self.window[0] < t < self.window[1]:
            T += self.delta
        phase = (t % self.period) / self.period
        light = 1.0 if phase < self.day_fraction else 0.0
        return {"temperature": T, "light": light}


class MoistureForcing:
    """Wrap a base temperature forcing and add a slow soil-moisture signal
    (0..1). Used by the omitted-variable audit as the hidden driver."""

    def __init__(self, base_forcing, period=50.0, mean=0.5, amp=0.3):
        self.base = base_forcing
        self.period = period
        self.mean = mean
        self.amp = amp

    def __call__(self, t):
        raw = dict(self.base(t))
        raw["moisture"] = self.mean + self.amp * np.sin(2 * np.pi * t / self.period)
        return raw


class TwoPatchForcing:
    """Two co-located patches: a hot (vulnerable) and a cool (robust) patch,
    sharing a diurnal cycle. For spatial-homogenization audits."""

    def __init__(self, T_mean1=25.0, T_mean2=20.0, amplitude=5.0,
                 day_fraction=0.5, period=24.0):
        self.T_mean1 = T_mean1
        self.T_mean2 = T_mean2
        self.amplitude = amplitude
        self.day_fraction = day_fraction
        self.period = period

    def __call__(self, t):
        diurnal = self.amplitude * np.sin(2 * np.pi * t / self.period)
        phase = (t % self.period) / self.period
        light = 1.0 if phase < self.day_fraction else 0.0
        return {"temperature_1": self.T_mean1 + diurnal,
                "temperature_2": self.T_mean2 + diurnal,
                "light": light}


class WarmRampForcing:
    """Slowly warming, always-lit forcing for cross-system coupling audits."""

    def __init__(self, T_start=25.0, rate=0.05):
        self.T_start = T_start
        self.rate = rate

    def __call__(self, t):
        return {"temperature": self.T_start + self.rate * t, "light": 1.0}
