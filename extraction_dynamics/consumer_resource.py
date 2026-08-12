# consumer_resource.py
# earth-systems-physics / extraction_dynamics
# CC0 — No Rights Reserved
#
# The consumer-resource pair, and the one term that changes its class.
#
#   dN/dt = r*N*(1 - N/K) - f(N)*P            resource
#   dP/dt = e*f(N)*P - m*P                    predator, COUPLED
#   dP/dt = e*f(N)*P - m*P + S                extractor, S = exogenous subsidy
#
# S is the whole pathology in one term.
#
# With S >> e*f(N)*P the consumer persists as N -> 0. Self-limitation is
# not weak in that regime — it is ABSENT. The pair has no interior
# equilibrium reachable from the resource side, because the consumer's
# fate stopped depending on the resource.
#
# Everything usually proposed as governance for such a system (quota,
# licence, closed season, gear rule, certification) is an attempt to
# re-supply by fiat the negative feedback that S deleted. That is not an
# argument against governance. It is a statement about what governance
# is doing here, and therefore about how much of it is required and what
# happens the moment it lapses.
#
# Standard library only.

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

from functional_response import response as _functional_response

# ─────────────────────────────────────────────
# STATE AND PARAMETERS
# ─────────────────────────────────────────────


@dataclass
class Params:
    """
    Consumer-resource parameters.

    r  : resource intrinsic rate of increase       (1/time)
    K  : resource carrying capacity                (density)
    a  : consumer attack rate                      (1/(density*time))
    h  : consumer handling time                    (time/item)
    q  : refuge exponent, 1 = Type II, 2 = Type III
    e  : conversion efficiency, resource -> consumer
    m  : consumer per-capita loss rate             (1/time)
    S  : EXOGENOUS SUBSIDY to the consumer         (consumer units/time)
         Zero for an ecological predator. Non-zero whenever the consumer
         is maintained by anything that does not come from N: fossil
         energy, an alternate prey base, a state transfer, an insurance
         payout, a parent company.
    kind : functional response, 'I' | 'II' | 'III'
    """
    r: float = 0.5
    K: float = 1.0
    a: float = 2.0
    h: float = 1.0
    q: float = 2.0
    e: float = 0.2
    m: float = 0.2
    S: float = 0.0
    kind: str = "III"


def intake(N: float, p: Params) -> float:
    """Per-consumer intake f(N) under the configured functional response."""
    return _functional_response(N, p.a, p.h, p.q, p.kind)


def resource_growth(N: float, p: Params) -> float:
    """Logistic recruitment r*N*(1 - N/K). Zero for a mined stock (r=0)."""
    return p.r * N * (1.0 - N / p.K) if p.K > 0 else 0.0


def dN_dt(N: float, P: float, p: Params) -> float:
    """Resource rate of change: recruitment minus consumption."""
    return resource_growth(N, p) - intake(N, p) * P


def dP_dt(N: float, P: float, p: Params) -> float:
    """
    Consumer rate of change.

    The subsidy S enters additively and does NOT scale with P, because a
    subsidy that scaled with the consumer would just be a modified
    conversion efficiency and would still vanish with the consumer. The
    point of S is that it is supplied from outside the pair.
    """
    return p.e * intake(N, p) * P - p.m * P + p.S


# ─────────────────────────────────────────────
# THE DIAGNOSTIC
# ─────────────────────────────────────────────


def coupling_index(N: float, P: float, p: Params) -> float:
    """
    Fraction of the consumer's gross gain that comes from THIS resource.

        C = e*f(N)*P / (e*f(N)*P + S)

    1.0 : fully coupled — an ecological predator
    0.5 : half the consumer's income is independent of the resource
    0.0 : fully subsidised — the resource is irrelevant to the
          consumer's persistence

    Evaluated at a state, because coupling is not a fixed property: a
    fleet can be coupled at high stock and uncoupled at low stock. That
    state dependence is exactly how the transition is missed.
    """
    gain = p.e * intake(N, p) * P
    denom = gain + p.S
    if denom <= 0:
        return 0.0
    return gain / denom


def persists_at_zero_resource(p: Params) -> bool:
    """
    Does the consumer survive the resource's extinction?

    dP/dt at N=0 is -m*P + S. With S > 0 the consumer has a positive
    influx that no longer depends on the resource at all, and settles at
    P* = S/m rather than going extinct.
    """
    return p.S > 0.0


def refuge_at_zero(p: Params) -> float:
    """Consumer's equilibrium standing stock at N = 0: P* = S/m."""
    return p.S / p.m if p.m > 0 else float("inf")


def classify(N: float, P: float, p: Params,
             coupled_threshold: float = 0.8) -> Dict[str, object]:
    """
    Classify the interaction from the equations at a given state.

    coupled_threshold : coupling index above which the consumer is
                        treated as genuinely coupled

    Returns the interaction name plus the quantities the classification
    rests on, so the verdict can be argued with.
    """
    C = coupling_index(N, P, p)
    recruits = p.r > 0.0
    coupled = C >= coupled_threshold and p.S == 0.0

    if not recruits:
        name = "mining"
    elif coupled:
        name = "predation"
    else:
        name = "hyperpredation"

    return {
        "interaction":        name,
        "coupling_index":     C,
        "subsidy":            p.S,
        "resource_recruits":  recruits,
        "consumer_at_N_zero": refuge_at_zero(p),
        "persists_at_zero_resource": persists_at_zero_resource(p),
        "internal_brake": (
            "prey depletion removes the consumer's growth term"
            if name == "predation" else
            "NONE — the subsidy survives resource extinction"
            if name == "hyperpredation" else
            "NONE — the resource has no recruitment term"
        ),
    }


# ─────────────────────────────────────────────
# INTEGRATION
# ─────────────────────────────────────────────


@dataclass
class Trajectory:
    """Result of a simulation run."""
    t: List[float] = field(default_factory=list)
    N: List[float] = field(default_factory=list)
    P: List[float] = field(default_factory=list)
    coupling: List[float] = field(default_factory=list)

    @property
    def N_final(self) -> float:
        return self.N[-1] if self.N else float("nan")

    @property
    def P_final(self) -> float:
        return self.P[-1] if self.P else float("nan")

    @property
    def N_min(self) -> float:
        return min(self.N) if self.N else float("nan")


def _rk4_step(N: float, P: float, p: Params, dt: float):
    """One classical Runge-Kutta 4 step on the pair."""
    k1n, k1p = dN_dt(N, P, p), dP_dt(N, P, p)
    k2n, k2p = (dN_dt(N + 0.5 * dt * k1n, P + 0.5 * dt * k1p, p),
                dP_dt(N + 0.5 * dt * k1n, P + 0.5 * dt * k1p, p))
    k3n, k3p = (dN_dt(N + 0.5 * dt * k2n, P + 0.5 * dt * k2p, p),
                dP_dt(N + 0.5 * dt * k2n, P + 0.5 * dt * k2p, p))
    k4n, k4p = (dN_dt(N + dt * k3n, P + dt * k3p, p),
                dP_dt(N + dt * k3n, P + dt * k3p, p))
    N_next = N + dt / 6.0 * (k1n + 2 * k2n + 2 * k3n + k4n)
    P_next = P + dt / 6.0 * (k1p + 2 * k2p + 2 * k3p + k4p)
    return max(N_next, 0.0), max(P_next, 0.0)


def simulate(N0: float, P0: float, p: Params,
             t_end: float = 200.0, dt: float = 0.01,
             extinction_threshold: float = 1e-4,
             record_every: int = 10) -> Trajectory:
    """
    Integrate the pair.

    extinction_threshold : density below which the resource is treated as
                           functionally extinct (recorded, not clamped)
    """
    traj = Trajectory()
    N, P, t = N0, P0, 0.0
    steps = int(t_end / dt)
    for i in range(steps + 1):
        if i % record_every == 0:
            traj.t.append(t)
            traj.N.append(N)
            traj.P.append(P)
            traj.coupling.append(coupling_index(N, P, p))
        N, P = _rk4_step(N, P, p, dt)
        t += dt
    return traj


def outcome(traj: Trajectory, p: Params,
            extinction_threshold: Optional[float] = None) -> Dict[str, object]:
    """
    Classify the run's outcome. The signature to look for is
    RESOURCE_EXTINCT_CONSUMER_PERSISTS — that combination is impossible
    for a coupled predator and diagnostic of a subsidised one.

    extinction_threshold : density treated as functional extinction.
        Defaults to 1% of K, because functional extinction is a
        statement about a stock relative to its own capacity, not an
        absolute count.
    """
    if extinction_threshold is None:
        extinction_threshold = 0.01 * p.K
    N_end, P_end = traj.N_final, traj.P_final
    resource_gone = N_end < extinction_threshold
    consumer_gone = P_end < extinction_threshold

    if resource_gone and not consumer_gone:
        mode = "RESOURCE_EXTINCT_CONSUMER_PERSISTS"
    elif resource_gone and consumer_gone:
        mode = "BOTH_EXTINCT"
    elif consumer_gone:
        mode = "CONSUMER_EXTINCT_RESOURCE_RECOVERS"
    else:
        mode = "COEXISTENCE"

    return {
        "mode":              mode,
        "N_final":           N_end,
        "P_final":           P_end,
        "N_min":             traj.N_min,
        "depletion":         1.0 - N_end / p.K if p.K > 0 else float("nan"),
        "coupling_final":    traj.coupling[-1] if traj.coupling else float("nan"),
        "subsidy_supported_consumer": refuge_at_zero(p),
        "diagnostic": (
            "consumer outlived its resource — only possible with an "
            "exogenous subsidy; this is hyperpredation, not predation"
            if mode == "RESOURCE_EXTINCT_CONSUMER_PERSISTS" else
            "consumer declined with its resource — coupling intact"
        ),
    }


if __name__ == "__main__":
    print("CONSUMER-RESOURCE: WHAT THE SUBSIDY TERM DOES")
    print("=" * 70)

    # e is chosen so that e*f(K) > m: the coupled predator is viable on
    # this prey alone, which is what makes the comparison fair. A
    # predator failing that inequality goes extinct with no help from
    # anyone — see energy_return.predator_persistence.
    shared = dict(r=0.5, K=1.0, a=2.0, h=1.0, e=0.45, m=0.2)

    runs = [
        ("coupled predator, Type III",
         Params(**shared, q=2.0, S=0.0, kind="III")),
        ("coupled predator, Type II (refuge removed)",
         Params(**shared, q=1.0, S=0.0, kind="II")),
        ("subsidised extractor, Type III",
         Params(**shared, q=2.0, S=0.05, kind="III")),
        ("subsidised extractor, Type II (refuge removed)",
         Params(**shared, q=1.0, S=0.05, kind="II")),
    ]

    for label, p in runs:
        traj = simulate(0.9, 0.1, p, t_end=300.0)
        out = outcome(traj, p)
        cls = classify(0.9, 0.1, p)
        print(f"\n{label}")
        print(f"  class at start : {cls['interaction']} "
              f"(coupling {cls['coupling_index']:.3f})")
        print(f"  N: 0.900 -> {out['N_final']:.4f}   "
              f"(min {out['N_min']:.4f})")
        print(f"  P: 0.100 -> {out['P_final']:.4f}")
        print(f"  outcome        : {out['mode']}")

    print("\n\nCONSUMER STANDING STOCK AT RESOURCE EXTINCTION  (P* = S/m)")
    print("=" * 70)
    for S in (0.0, 0.01, 0.05, 0.2):
        p = Params(**shared, S=S)
        print(f"  S = {S:5.3f}  ->  P*(N=0) = {refuge_at_zero(p):6.3f}   "
              f"persists: {persists_at_zero_resource(p)}")
