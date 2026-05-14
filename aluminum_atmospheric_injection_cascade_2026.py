"""
ALUMINUM_ATMOSPHERIC_INJECTION_CASCADE_2026

Coupled four-layer Earth-systems simulation modeling consequences of
aluminum particulate injection (stratospheric aerosol injection / SAI).

    Layer 1: Crustal substrate quantum coherence (magnetite / banded iron)
    Layer 2: Ionospheric plasma state
    Layer 3: Atmospheric chemistry and charge distribution
    Layer 4: Aluminum forcing perturbation

Coupling mechanisms:
    - Merle nonlinear evolution equations (soliton decomposition,
      blow-up rates)
    - Higher-order interactions (triplet coupling beyond pairwise)
    - Rate-induced tipping (rapid forcing exceeds tracking capacity)

Output: Monte Carlo distribution of cascade outcomes; flags substrate
coherence collapse, ionospheric destabilization, atmospheric phase
transitions.

Standard library only. CC0 Public Domain.
Run: python aluminum_atmospheric_injection_cascade_2026.py
"""

import math
import random
import statistics
from typing import Dict, List, Tuple, Optional


# ─────────────────────────────────────────────
# PHYSICAL CONSTANTS AND BASELINE PARAMETERS
# ─────────────────────────────────────────────

# Crustal substrate (banded iron formation, Archean basement)
MAGNETITE_COHERENCE_BASELINE = 1.0       # normalized substrate coupling strength
MAGNETITE_DECOHERENCE_RATE = 0.001       # natural relaxation per year
BIF_QUANTUM_COUPLING_EFFICIENCY = 0.85   # fraction transmitting to biosphere

# Ionosphere (D, E, F layers; charge density baseline)
IONOSPHERIC_PLASMA_DENSITY = 1.0         # normalized
IONOSPHERIC_CONDUCTIVITY = 1.0           # normalized
SCHUMANN_RESONANCE_BASELINE_HZ = 7.83    # planetary EM resonance

# Atmosphere (chemistry, charge distribution)
ATMOSPHERIC_CHARGE_GRADIENT = 130.0      # V/m fair-weather field
ATMOSPHERIC_CHEMISTRY_INTEGRITY = 1.0    # normalized stability index
OZONE_LAYER_INTEGRITY = 1.0              # normalized

# Aluminum forcing (the perturbation under test)
ALUMINUM_INJECTION_RATE_TG_PER_YEAR = 5.0  # teragrams Al2O3 per year (SAI proposals)
ALUMINUM_RESIDENCE_TIME_YEARS = 1.5         # stratospheric residence time
ALUMINUM_REACTIVITY_FACTOR = 0.7            # fraction reaching reactive state


# ─────────────────────────────────────────────
# COUPLING TENSORS (pairwise + higher-order interactions)
# Layer indices: 0 = crust, 1 = ionosphere, 2 = atmosphere, 3 = aluminum
# ─────────────────────────────────────────────

LAMBDA_PAIRWISE: Dict[Tuple[int, int], float] = {
    (0, 1): 0.30,   # crust - ionosphere (BIF magnetic coupling to ionosphere)
    (0, 2): 0.15,   # crust - atmosphere (direct EM, geogenic emissions)
    (1, 2): 0.65,   # ionosphere - atmosphere (strong charge coupling)
    (1, 3): 0.45,   # ionosphere - aluminum (plasma chemistry, charge effects)
    (2, 3): 0.85,   # atmosphere - aluminum (direct chemistry)
    (0, 3): 0.10,   # crust - aluminum (deposition, weathering)
}

# Higher-order (triplet) coupling. From Ghosh-Shrimali 2026:
# triplet coupling can trigger cascades at strengths where pairwise alone fails.
LAMBDA_TRIPLET: Dict[Tuple[int, int, int], float] = {
    (0, 1, 2): 0.55,    # crust-ionosphere-atmosphere natural Earth circuit
    (1, 2, 3): 0.75,    # ionosphere-atmosphere-aluminum (perturbation triplet)
    (0, 2, 3): 0.40,    # crust-atmosphere-aluminum (deposition feedback)
    (0, 1, 3): 0.35,    # crust-ionosphere-aluminum (long-range EM)
}


# ─────────────────────────────────────────────
# MERLE NONLINEAR EVOLUTION (singularity / blow-up detection)
# Singularity timing: T_max - t ~ exp(-c * E(t))
# Energy concentration rate signals approach to collapse.
# ─────────────────────────────────────────────

def energy_concentration(state: Dict[str, float]) -> float:
    """
    Compute total nonlinear energy concentration across coupled layers.
    Used to detect approach to singularity (cascade tipping).
    """
    crust = state["crust_coherence"]
    iono  = state["iono_density"]
    atmo  = state["atmo_integrity"]
    al    = state["aluminum_load"]
    # Nonlinear source term: aluminum amplifies through coupling
    return (
        al * al * (1.0 / max(crust, 0.01))
        + (1.0 - atmo) ** 2 * iono
        + LAMBDA_TRIPLET[(1, 2, 3)] * al * (1.0 - atmo) * iono
    )


def blow_up_rate(state_history: List[float]) -> float:
    """
    Log-log blow-up rate estimator (Merle framework).
    Returns rate of energy concentration acceleration.
    Higher = closer to singularity.
    """
    if len(state_history) < 3:
        return 0.0
    e1, e2, e3 = state_history[-3], state_history[-2], state_history[-1]
    if e1 <= 0 or e2 <= 0 or e3 <= 0:
        return 0.0
    return (
        math.log(max(e3, 1e-9))
        - 2 * math.log(max(e2, 1e-9))
        + math.log(max(e1, 1e-9))
    )


# ─────────────────────────────────────────────
# COUPLED EVOLUTION STEP
# ─────────────────────────────────────────────

def evolve_step(state: Dict[str, float],
                dt: float,
                al_input: float,
                noise_amplitude: float = 0.05) -> Dict[str, float]:
    """
    One time step of coupled four-layer system.
    Crust, ionosphere, atmosphere, aluminum evolve under pairwise +
    triplet coupling.
    """
    crust = state["crust_coherence"]
    iono  = state["iono_density"]
    atmo  = state["atmo_integrity"]
    al    = state["aluminum_load"]

    # Aluminum dynamics: input, residence decay
    d_al = al_input - (al / ALUMINUM_RESIDENCE_TIME_YEARS)

    # Atmosphere: degraded by aluminum reactivity, ozone interference
    d_atmo = (
        -ALUMINUM_REACTIVITY_FACTOR * al * 0.1
        - LAMBDA_PAIRWISE[(2, 3)] * al * 0.05
        - LAMBDA_TRIPLET[(1, 2, 3)] * al * iono * 0.02
        + 0.01 * (1.0 - atmo) * -1.0  # weak natural recovery toward 1
    )
    # Drive atmo back toward integrity if no forcing
    d_atmo += 0.005 * (ATMOSPHERIC_CHEMISTRY_INTEGRITY - atmo)

    # Ionosphere: aluminum charge effects, crust feedback
    d_iono = (
        -LAMBDA_PAIRWISE[(1, 3)] * al * 0.04
        + LAMBDA_PAIRWISE[(0, 1)] * (crust - 1.0) * 0.05
        - LAMBDA_TRIPLET[(0, 1, 2)] * (1.0 - atmo) * 0.03
    )

    # Crust coherence: slow degradation under sustained perturbation
    d_crust = (
        -MAGNETITE_DECOHERENCE_RATE
        - LAMBDA_TRIPLET[(0, 2, 3)] * al * (1.0 - atmo) * 0.01
        - LAMBDA_PAIRWISE[(0, 3)] * al * 0.005
    )

    # Stochastic noise (rate-induced tipping element)
    d_atmo += random.gauss(0, noise_amplitude * 0.5)
    d_iono += random.gauss(0, noise_amplitude * 0.5)

    return {
        "crust_coherence": max(0.0, crust + d_crust * dt),
        "iono_density":    max(0.0, iono + d_iono * dt),
        "atmo_integrity":  max(0.0, min(1.0, atmo + d_atmo * dt)),
        "aluminum_load":   max(0.0, al + d_al * dt),
    }


# ─────────────────────────────────────────────
# CASCADE DETECTION
# ─────────────────────────────────────────────

def detect_cascade(state: Dict[str, float],
                   blow_rate: float) -> Tuple[bool, str]:
    """
    Returns (cascade_triggered, mode) for current state.
    Modes: STABLE, ATMOSPHERIC_DESTABILIZATION, IONOSPHERIC_COLLAPSE,
           SUBSTRATE_DECOHERENCE, FULL_CASCADE, SINGULARITY_APPROACH.
    """
    crust = state["crust_coherence"]
    iono  = state["iono_density"]
    atmo  = state["atmo_integrity"]

    if crust < 0.5 and iono < 0.5 and atmo < 0.5:
        return True, "FULL_CASCADE"
    if atmo < 0.4:
        return True, "ATMOSPHERIC_DESTABILIZATION"
    if iono < 0.4:
        return True, "IONOSPHERIC_COLLAPSE"
    if crust < 0.6:
        return True, "SUBSTRATE_DECOHERENCE"
    if blow_rate > 0.5:
        return True, "SINGULARITY_APPROACH"
    return False, "STABLE"


# ─────────────────────────────────────────────
# MONTE CARLO SIMULATION DRIVER
# ─────────────────────────────────────────────

def run_simulation(years: int = 50,
                   dt: float = 0.5,
                   al_rate: float = ALUMINUM_INJECTION_RATE_TG_PER_YEAR,
                   noise: float = 0.05) -> Dict:
    """
    Run a single trajectory of the coupled system under sustained
    aluminum injection.
    """
    state = {
        "crust_coherence": MAGNETITE_COHERENCE_BASELINE,
        "iono_density":    IONOSPHERIC_PLASMA_DENSITY,
        "atmo_integrity":  ATMOSPHERIC_CHEMISTRY_INTEGRITY,
        "aluminum_load":   0.0,
    }
    energy_history: List[float] = []
    cascade_year: Optional[float] = None
    cascade_mode = "STABLE"

    n_steps = int(years / dt)
    for step in range(n_steps):
        e = energy_concentration(state)
        energy_history.append(e)
        rate = blow_up_rate(energy_history) if len(energy_history) >= 3 else 0.0

        triggered, mode = detect_cascade(state, rate)
        if triggered and cascade_year is None:
            cascade_year = step * dt
            cascade_mode = mode

        state = evolve_step(state, dt, al_rate, noise)

    return {
        "final_state":  state,
        "cascade_year": cascade_year,
        "cascade_mode": cascade_mode,
        "max_energy":   max(energy_history) if energy_history else 0.0,
        "final_energy": energy_history[-1] if energy_history else 0.0,
    }


def monte_carlo(n_runs: int = 1000,
                years: int = 50,
                al_rate: float = ALUMINUM_INJECTION_RATE_TG_PER_YEAR,
                master_seed: Optional[int] = None) -> Dict:
    """
    Run Monte Carlo over n_runs trajectories.
    Returns distribution of cascade outcomes, modes, and timing.
    master_seed : optional int making the sweep reproducible (otherwise
                   the global random state is whatever the import time
                   left it at).
    """
    if master_seed is not None:
        random.seed(master_seed)

    results = []
    modes: Dict[str, int] = {}
    cascade_years: List[float] = []

    for _ in range(n_runs):
        r = run_simulation(years=years, al_rate=al_rate)
        results.append(r)
        m = r["cascade_mode"]
        modes[m] = modes.get(m, 0) + 1
        if r["cascade_year"] is not None:
            cascade_years.append(r["cascade_year"])

    return {
        "n_runs": n_runs,
        "mode_distribution": {m: c / n_runs for m, c in modes.items()},
        "p_any_cascade": (
            sum(1 for r in results if r["cascade_year"] is not None)
            / n_runs
        ),
        "cascade_year_median": (
            statistics.median(cascade_years) if cascade_years else None
        ),
        "cascade_year_min": (min(cascade_years) if cascade_years else None),
        "cascade_year_max": (max(cascade_years) if cascade_years else None),
    }


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("ALUMINUM ATMOSPHERIC INJECTION CASCADE — Monte Carlo")
    print("=" * 60)
    print(f"Injection rate:       "
          f"{ALUMINUM_INJECTION_RATE_TG_PER_YEAR} Tg/yr Al2O3")
    print(f"Residence time:       "
          f"{ALUMINUM_RESIDENCE_TIME_YEARS} yr")
    print(f"Simulation horizon:   50 yr")
    print(f"Coupled layers:       crust / ionosphere / atmosphere / aluminum")
    print()

    summary = monte_carlo(n_runs=1000, years=50, master_seed=2026)
    print(f"Total cascade probability: {summary['p_any_cascade']*100:.1f}%")
    print(f"Median time to cascade:    {summary['cascade_year_median']} yr")
    print(f"Range:                     "
          f"{summary['cascade_year_min']} - "
          f"{summary['cascade_year_max']} yr")
    print()
    print("Cascade mode distribution:")
    for mode, frac in sorted(summary["mode_distribution"].items(),
                             key=lambda x: -x[1]):
        print(f"  {mode:35s} {frac*100:.1f}%")
