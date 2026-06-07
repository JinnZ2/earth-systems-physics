"""
thermo.py  --  CC0

Thermodynamic primitives for atmospheric stability. stdlib only.
Every function is a measurement model with explicit units. No narrative.

UNITS
  z   m          height
  T   K          temperature
  theta K        potential temperature
  U   m/s        zonal wind
  dU/dz 1/s      vertical shear  (S)
  N   1/s        Brunt-Vaisala frequency
  f   1/s        Coriolis parameter
  dT/dy K/m      meridional temperature gradient

CONSTANTS
  g  = 9.81 m/s^2
  cp = 1004 J/kg/K
  Rd = 287 J/kg/K
  Gamma_d = g/cp ~ 9.8 K/km  (dry adiabatic lapse rate)
"""

import math

G = 9.81
CP = 1004.0
RD = 287.0
GAMMA_D = G / CP                     # ~0.00977 K/m  = 9.77 K/km
OMEGA_EARTH = 7.292e-5               # rad/s


def coriolis(lat_deg):
    """f = 2*Omega*sin(lat).  1/s"""
    return 2.0 * OMEGA_EARTH * math.sin(math.radians(lat_deg))


def beta(lat_deg, R_earth=6.371e6):
    """beta = df/dy = 2*Omega*cos(lat)/R.  1/(m s)"""
    return 2.0 * OMEGA_EARTH * math.cos(math.radians(lat_deg)) / R_earth


def brunt_vaisala_sq(T, env_lapse):
    """
    N^2 = (g/T)*(Gamma_d - Gamma_env)   [1/s^2]
    env_lapse = -dT/dz   (positive when T decreases with height), K/m.
    N^2 > 0 stable, < 0 convectively unstable.
    """
    return (G / T) * (GAMMA_D - env_lapse)


def brunt_vaisala(T, env_lapse):
    """N [1/s]; returns signed sqrt: negative N means convectively unstable."""
    n2 = brunt_vaisala_sq(T, env_lapse)
    return math.copysign(math.sqrt(abs(n2)), n2)


def thermal_wind_shear(dTdy, f, T):
    """
    Vertical shear from thermal wind balance:
      dU/dz = -(g/(f*T)) * dT/dy     [1/s]
    dTdy in K/m (negative in NH: warm equatorward). Returns S = dU/dz.
    """
    if f == 0:
        return float("inf")
    return -(G / (f * T)) * dTdy


def richardson(N2, shear):
    """Ri = N^2 / S^2. KH/shear instability when Ri < 0.25."""
    if shear == 0:
        return float("inf")
    return N2 / (shear * shear)


def lapse_from_gradient_aloft(env_lapse_surface, warming_index):
    """
    Crude vertical-structure knob. Warming increases upper-tropospheric
    stability (moist-adiabatic tropical warming aloft) -> larger effective
    lapse difference -> changes N with height. Returns adjusted env_lapse.
    warming_index in [0,1].
    """
    # warming aloft reduces environmental lapse rate (more stable) slightly
    return env_lapse_surface * (1.0 - 0.15 * warming_index)
