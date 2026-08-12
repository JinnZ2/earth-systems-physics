# cpr_game.py
# earth-systems-physics / experiments/cpr_composition
# CC0 — No Rights Reserved
#
# Common-pool resource game: the engine.
#
# This is the instrument for the diagnostic in extraction_dynamics/.
# The CPR game is a discrete-time consumer-resource pair in which the
# consumer's persistence is deliberately DECOUPLED from the resource:
# a participant's outside earnings do not fall when the stock does.
# That show-up fee is the subsidy term S, and the experiment asks what
# human groups do once it is present.
#
#   round t:  each player i requests x_i in [0, cap]
#             total = sum(x_i)
#             if total >= S:   proportional rationing, stock -> 0, COLLAPSE
#             else:            S_after = S - total
#                              S_next  = min(S_after + g*S_after*(1 - S_after/K), K)
#
# The regeneration term is the discrete logistic map. It is the same
# r*N*(1 - N/K) as the resource equation in
# extraction_dynamics/consumer_resource.py, integrated with a one-round
# Euler step because the participants act once per round.
#
# Standard library only, deterministic, no I/O. Everything that touches
# pandas, matplotlib, or oTree lives in another file.

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

# ─────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────


@dataclass(frozen=True)
class GameParams:
    """
    N            : players per group
    cap          : maximum request per player per round
    S0           : starting stock
    K            : carrying capacity
    g            : regeneration rate (tuned in the pilot)
    T            : number of rounds
    token_value  : USD per token, for the participant bonus
    show_up_fee  : USD paid regardless of outcome — this is the subsidy
                    term, stated explicitly rather than left implicit
    """
    N: int = 4
    cap: int = 8
    S0: float = 50.0
    K: float = 100.0
    g: float = 0.4
    T: int = 20
    token_value: float = 0.05
    show_up_fee: float = 6.00

    def max_group_request(self) -> int:
        """Total the group can demand in one round."""
        return self.N * self.cap


# ─────────────────────────────────────────────
# RESOURCE DYNAMICS
# ─────────────────────────────────────────────


def regenerate(S_after: float, g: float, K: float) -> float:
    """
    Discrete logistic regeneration, capped at K and floored at 0.

        S_next = S_after + g*S_after*(1 - S_after/K)

    Note for anyone changing g: this map is stable for g < 2, period
    doubles above it, and is chaotic near 2.57. The design range
    (0.2-0.6) is well inside the stable region, so any oscillation seen
    in the data is behavioural, not an artefact of the map.
    """
    if S_after <= 0:
        return 0.0
    return max(0.0, min(S_after + g * S_after * (1.0 - S_after / K), K))


def ration(requests: Sequence[int], S: float) -> List[int]:
    """
    Proportional rationing when demand meets or exceeds the stock, using
    largest-remainder allocation so that the integers sum to the stock
    actually available.

    Naive int() truncation destroys tokens that the stock could have
    supplied — the group is charged for a collapse it did not quite
    cause, and the payoff data inherits the error. Largest remainder
    keeps the accounting closed.
    """
    total = sum(requests)
    S_int = int(math.floor(max(S, 0.0)))
    if total <= 0 or S_int <= 0:
        return [0] * len(requests)
    if total <= S_int:
        return list(requests)

    exact = [r * S_int / total for r in requests]
    base = [int(math.floor(e)) for e in exact]
    remainder = S_int - sum(base)
    # distribute the remainder to the largest fractional parts, ties to
    # the lower player index (deterministic, documented, arbitrary)
    order = sorted(range(len(requests)),
                   key=lambda i: (-(exact[i] - base[i]), i))
    for i in order[:remainder]:
        base[i] += 1
    return base


@dataclass
class RoundResult:
    round: int
    stock_before: float
    requests: List[int]
    taken: List[int]
    total_taken: int
    stock_after_extraction: float
    stock_next: float
    collapsed: bool
    rationed: bool


def step(S: float, requests: Sequence[int],
         p: GameParams) -> Tuple[float, List[int], bool]:
    """
    One round: extract, then regenerate.

    Returns (S_next, taken, collapsed).

    Collapse is defined as demand meeting or exceeding the standing
    stock. The stock goes to zero and does not regenerate — zero is an
    absorbing state of the logistic map, which is the discrete-time
    version of the absorbing collapsed state in
    extraction_dynamics/depensation.py.
    """
    if S <= 0:
        return 0.0, [0] * len(requests), True
    total = sum(requests)
    if total >= S:
        return 0.0, ration(requests, S), True
    taken = list(requests)
    return regenerate(S - total, p.g, p.K), taken, False


# ─────────────────────────────────────────────
# POLICIES
# ─────────────────────────────────────────────


def sustainable_total(S: float, g: float, K: float) -> float:
    """
    The exact per-round harvest that leaves the stock unchanged.

    Solve S = A + g*A*(1 - A/K) for the post-harvest stock A, then the
    sustainable take is S - A:

        (g/K)*A^2 - (1+g)*A + S = 0
        A = [ (1+g) - sqrt((1+g)^2 - 4*g*S/K) ] / (2*g/K)

    This is a fixed point, not an approximation: taking exactly this
    much holds the stock constant forever. It is what the naive
    "split the stock evenly" heuristic is usually reaching for and
    always overshoots.

    Returns 0.0 when no positive harvest is sustainable at this stock.
    """
    if S <= 0 or g <= 0 or K <= 0:
        return 0.0
    disc = (1.0 + g) ** 2 - 4.0 * g * S / K
    if disc < 0:
        # S is above the highest stock this map can sustain in one step
        return max(0.0, S - K / 2.0)
    A = ((1.0 + g) - math.sqrt(disc)) / (2.0 * g / K)
    return max(0.0, S - A)


def msy_total(g: float, K: float) -> float:
    """Maximum sustainable yield of the logistic map: g*K/4, at S = K/2."""
    return g * K / 4.0


def policy_all_max(S: float, p: GameParams, n_max: Optional[int] = None
                   ) -> List[int]:
    """Every player requests the cap."""
    return [p.cap] * p.N


def policy_sustainable(S: float, p: GameParams,
                       n_max: Optional[int] = None) -> List[int]:
    """
    Every player requests an equal share of the exactly-sustainable
    total, floored to an integer and capped.

    NOT 'S/N'. Splitting the standing stock evenly is a collapse policy
    dressed as a fair one, and it fails in two different ways depending
    on where the cap binds:

      S <= N*cap : the request is S/N each, so the group requests the
                   WHOLE stock and collapses it in one round
      S >  N*cap : the cap truncates every request to the cap, so the
                   policy IS all-max (at S = 50, N = 4 it asks for 12
                   each, truncated to 8, which is the maximum)

    Either way the comparison arm is not a restraint arm, which is what
    the draft design had.
    """
    total = sustainable_total(S, p.g, p.K)
    per = int(math.floor(total / p.N))
    return [max(0, min(per, p.cap))] * p.N


def policy_mixed(S: float, p: GameParams, n_max: int = 0) -> List[int]:
    """
    n_max players request the cap; the rest request their share of what
    remains sustainable after the maximisers have taken theirs.

    This is the mechanical analogue of group composition: it is what the
    game predicts for n_high_d = 0..N if high-D players always maximise
    and the others restrain optimally. The experiment's H2 is a claim
    that real groups behave differently from this baseline — so the
    baseline has to be computed, not assumed.
    """
    n_max = max(0, min(n_max, p.N))
    n_rest = p.N - n_max
    maxers = [p.cap] * n_max
    if n_rest == 0:
        return maxers
    remaining = max(0.0, sustainable_total(S, p.g, p.K) - sum(maxers))
    per = int(math.floor(remaining / n_rest))
    return maxers + [max(0, min(per, p.cap))] * n_rest


POLICIES: Dict[str, Callable[..., List[int]]] = {
    "all_max": policy_all_max,
    "sustainable": policy_sustainable,
    "mixed": policy_mixed,
    "none": lambda S, p, n_max=None: [0] * p.N,
}


# ─────────────────────────────────────────────
# SIMULATION
# ─────────────────────────────────────────────


@dataclass
class GameResult:
    params: GameParams
    policy: str
    n_max: int
    history: List[RoundResult] = field(default_factory=list)

    @property
    def final_stock(self) -> float:
        return self.history[-1].stock_next if self.history else self.params.S0

    @property
    def collapsed(self) -> bool:
        return any(r.collapsed for r in self.history)

    @property
    def rounds_to_collapse(self) -> Optional[int]:
        for r in self.history:
            if r.collapsed:
                return r.round
        return None

    @property
    def total_extracted(self) -> int:
        return sum(r.total_taken for r in self.history)

    @property
    def per_player_extracted(self) -> List[int]:
        out = [0] * self.params.N
        for r in self.history:
            for i, t in enumerate(r.taken):
                out[i] += t
        return out

    def summary(self) -> Dict[str, object]:
        """Group-level record, matching the primary DV in the analysis."""
        rtc = self.rounds_to_collapse
        return {
            "policy":            self.policy,
            "n_max":             self.n_max,
            "g":                 self.params.g,
            "final_stock":       self.final_stock,
            "S_final_over_K":    self.final_stock / self.params.K,
            "collapsed":         self.collapsed,
            "rounds_to_collapse": rtc,
            # survival analysis needs the censoring indicator, not just
            # a duration: groups that never collapse are censored at T
            "duration":          rtc if rtc is not None else self.params.T,
            "event_observed":    rtc is not None,
            "total_extracted":   self.total_extracted,
            "payoff_usd":        self.total_extracted * self.params.token_value,
            "gini_extraction":   gini(self.per_player_extracted),
        }


def simulate(p: GameParams = GameParams(), policy: str = "all_max",
             n_max: int = 0,
             requests_fn: Optional[Callable[[float, GameParams], List[int]]]
             = None) -> GameResult:
    """
    Run one group for T rounds.

    policy       : key in POLICIES
    n_max        : number of maximisers, for the 'mixed' policy
    requests_fn  : optional override taking (stock, params) and returning
                   a request list — use it to replay observed data
    """
    if requests_fn is None:
        if policy not in POLICIES:
            raise ValueError(f"unknown policy '{policy}'; "
                             f"valid: {sorted(POLICIES)}")
        fn = POLICIES[policy]

        def requests_fn(S, params):          # noqa: F811 - deliberate
            return fn(S, params, n_max)

    result = GameResult(params=p, policy=policy, n_max=n_max)
    S = p.S0
    for t in range(1, p.T + 1):
        if S <= 0:
            break
        req = [max(0, min(int(x), p.cap)) for x in requests_fn(S, p)]
        if len(req) != p.N:
            raise ValueError(f"policy returned {len(req)} requests for "
                             f"{p.N} players")
        S_next, taken, collapsed = step(S, req, p)
        result.history.append(RoundResult(
            round=t,
            stock_before=S,
            requests=req,
            taken=taken,
            total_taken=sum(taken),
            stock_after_extraction=max(0.0, S - sum(taken)),
            stock_next=S_next,
            collapsed=collapsed,
            rationed=sum(req) >= S,
        ))
        S = S_next
        if collapsed:
            break
    return result


def gini(values: Sequence[float]) -> float:
    """
    Gini coefficient of within-group extraction. 0 = equal split,
    -> 1 = one player took everything. Returns 0.0 for an all-zero group
    (no extraction to distribute unequally).
    """
    v = sorted(float(x) for x in values)
    n = len(v)
    total = sum(v)
    if n == 0 or total <= 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(v))
    return (2.0 * cum) / (n * total) - (n + 1.0) / n


# ─────────────────────────────────────────────
# THE LINK TO extraction_dynamics/
# ─────────────────────────────────────────────


def subsidy_ratio(p: GameParams, rounds_survived: int) -> Dict[str, float]:
    """
    How much of a participant's earnings are independent of the stock.

        coupling = bonus / (bonus + show-up fee)

    This is the same coupling index as
    extraction_dynamics/consumer_resource.coupling_index, computed on
    money instead of biomass. At the default parameters a participant
    who extracts nothing for twenty rounds still earns the show-up fee,
    so the experiment is BY CONSTRUCTION a hyperpredation setup, not a
    predation one. Reporting this is not a criticism of the design —
    it is the design, and it is what makes the game a model of
    subsidised extraction rather than of subsistence.
    """
    max_bonus = p.cap * rounds_survived * p.token_value
    denom = max_bonus + p.show_up_fee
    return {
        "max_bonus_usd":   max_bonus,
        "show_up_fee_usd": p.show_up_fee,
        "coupling_index":  max_bonus / denom if denom > 0 else 0.0,
        "subsidy_share":   p.show_up_fee / denom if denom > 0 else 1.0,
    }


if __name__ == "__main__":
    p = GameParams()
    print("COMMON-POOL RESOURCE GAME")
    print("=" * 70)
    print(f"  N={p.N}  cap={p.cap}  S0={p.S0:.0f}  K={p.K:.0f}  "
          f"g={p.g}  T={p.T}")
    print(f"  group can demand {p.max_group_request()} per round; "
          f"MSY = {msy_total(p.g, p.K):.1f}")

    print("\nSUSTAINABLE TAKE IS A FIXED POINT, NOT A SPLIT")
    print("=" * 70)
    print(f"  {'stock':>7} {'sustainable total':>18} {'per player':>11} "
          f"{'naive S/N':>10}")
    for S in (20.0, 40.0, 50.0, 70.0, 90.0):
        st = sustainable_total(S, p.g, p.K)
        print(f"  {S:7.1f} {st:18.2f} {st / p.N:11.2f} {S / p.N:10.2f}")
    print("\n  The naive S/N split takes the WHOLE stock by construction:")
    print("  four players at S/N each is S. It collapses the pool in one")
    print("  round at any stock, and above S = N*cap it is truncated to")
    print("  the cap and becomes literally identical to all-max.")

    print("\n\nTHREE POLICIES AT g=0.4")
    print("=" * 70)
    for pol in ("all_max", "sustainable"):
        r = simulate(p, policy=pol)
        s = r.summary()
        print(f"  {pol:12s} final S={s['final_stock']:6.2f}  "
              f"collapsed={str(s['collapsed']):5s}  "
              f"round={s['rounds_to_collapse']}  "
              f"extracted={s['total_extracted']:4d}  "
              f"payoff=${s['payoff_usd']:.2f}")

    print("\n\nCOMPOSITION BASELINE — WHAT THE GAME PREDICTS MECHANICALLY")
    print("=" * 70)
    print(f"  {'n_max':>6} {'final S':>9} {'S/K':>7} {'collapse round':>15} "
          f"{'extracted':>10}")
    for k in range(p.N + 1):
        r = simulate(p, policy="mixed", n_max=k)
        s = r.summary()
        print(f"  {k:6d} {s['final_stock']:9.2f} {s['S_final_over_K']:7.3f} "
              f"{str(s['rounds_to_collapse']):>15} "
              f"{s['total_extracted']:10d}")
    print("\n  This is the H2 baseline. A behavioural effect of composition")
    print("  has to be measured against THIS curve, not against zero.")

    print("\n\nCOUPLING OF THE PARTICIPANT TO THE STOCK")
    print("=" * 70)
    sr = subsidy_ratio(p, p.T)
    print(f"  max bonus ${sr['max_bonus_usd']:.2f} vs show-up fee "
          f"${sr['show_up_fee_usd']:.2f}")
    print(f"  coupling index {sr['coupling_index']:.3f}  "
          f"(subsidy share {sr['subsidy_share']:.3f})")
    print("  The show-up fee is the subsidy term S. The design is a model")
    print("  of subsidised extraction, by construction.")
