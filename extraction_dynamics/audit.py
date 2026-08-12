# audit.py
# earth-systems-physics / extraction_dynamics
# CC0 — No Rights Reserved
#
# The runner: takes a described system, returns its interaction class,
# the state of its low-density refuge, whether a pit exists, and whether
# the consumer is energetically coupled to the resource it consumes.
#
# Every verdict comes with the quantity it rests on and the measurement
# that would overturn it. A verdict with no falsifier is not reported.
#
# Standard library only.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from consumer_resource import (
    Params, classify, coupling_index, intake, outcome, simulate,
    refuge_at_zero,
)
from depensation import predator_pit
from energy_return import predator_persistence, subsidy_required
from functional_response import refuge_index, escape_density
from interaction_taxonomy import INTERACTIONS

# ─────────────────────────────────────────────
# SYSTEM SPECIFICATION
# ─────────────────────────────────────────────


@dataclass
class System:
    """
    A described consumer-resource system.

    Everything here is a measurement or an explicit assumption. Fields
    left at their defaults are assumptions, and the audit says so.
    """
    name:            str
    N:               float          # current resource stock
    P:               float          # current consumer stock
    params:          Params
    # optional recruitment description for the pit analysis
    alpha:           Optional[float] = None   # max recruitment
    beta:            Optional[float] = None   # half-saturation spawners
    natural_mortality: float = 0.0
    depensatory:     bool = True
    # provenance
    stock_measured:  bool = False
    subsidy_measured: bool = False
    notes:           str = ""


# ─────────────────────────────────────────────
# AUDIT
# ─────────────────────────────────────────────


def audit(system: System, horizon: float = 300.0) -> Dict[str, object]:
    """
    Run the full diagnostic on a system.

    Returns a dict with five sections:
      classification : what kind of interaction this is, and why
      energetics     : whether the consumer is viable on this resource
      refuge         : the state of the low-density refuge
      pit            : whether an escape threshold exists, and where
      projection     : where the equations take this system

    Plus `falsifiers`: the measurements that would change each verdict.
    """
    p = system.params
    f_N = intake(system.N, p)

    cls = classify(system.N, system.P, p)
    energetics = predator_persistence(p.e, f_N, p.m)
    energetics["subsidy_required_total"] = subsidy_required(
        p.e, f_N, p.m, system.P)

    # Refuge: evaluated at 5% of capacity, the density where the
    # question actually matters.
    N_low = 0.05 * p.K
    refuge = {
        "refuge_index_at_5pct_K": refuge_index(N_low, p.a, p.h, p.q,
                                               p.kind, N_ref=p.K),
        "q":                      p.q,
        "response_type":          p.kind,
        "refuge_present":         p.kind == "III" and p.q > 1.2,
        "protective_density":     escape_density(p.a, p.h, p.q,
                                                 N_max=p.K),
    }

    if system.alpha is not None and system.beta is not None:
        pit = predator_pit(
            system.alpha, system.beta, p.a, p.h, p.q, system.P,
            kind="depensatory" if system.depensatory else "compensatory",
            response_kind=p.kind,
            natural_mortality=system.natural_mortality,
            S_max=max(2.0 * p.K, 2.0),
        )
    else:
        pit = {"pit_present": None,
               "note": "recruitment curve not supplied (alpha, beta) — "
                       "pit analysis skipped rather than guessed"}

    traj = simulate(system.N, system.P, p, t_end=horizon)
    proj = outcome(traj, p)

    interaction = INTERACTIONS.get(cls["interaction"])
    verdict = _verdict(cls, energetics, refuge, pit, proj)

    return {
        "system":          system.name,
        "classification":  cls,
        "bounding_feedback": (interaction.bounding_feedback
                              if interaction else "unknown"),
        "energetics":      energetics,
        "refuge":          refuge,
        "pit":             pit,
        "projection":      proj,
        "verdict":         verdict,
        "provenance": {
            "stock_measured":   system.stock_measured,
            "subsidy_measured": system.subsidy_measured,
            "notes":            system.notes,
            "warning": (None if system.stock_measured and
                        system.subsidy_measured else
                        "one or more inputs are assumed rather than "
                        "measured; the classification inherits that "
                        "uncertainty"),
        },
        "falsifiers":      falsifiers(system),
    }


def _verdict(cls, energetics, refuge, pit, proj) -> Dict[str, object]:
    """
    Condense the sections into the two findings that matter, keeping
    them separate because they have different remedies.
    """
    uncoupled = cls["interaction"] in ("hyperpredation", "mining")
    refuge_gone = not refuge["refuge_present"]

    if uncoupled and refuge_gone:
        headline = "UNCOUPLED_AND_UNREFUGED"
        reading = ("consumer does not decline with the resource AND the "
                   "resource has no low-density protection. Both brakes "
                   "are absent; the trajectory runs to depletion unless "
                   "something outside the pair stops it.")
    elif uncoupled:
        headline = "UNCOUPLED_REFUGE_INTACT"
        reading = ("consumer is subsidised, but the low-density refuge "
                   "still bends the pursuit curve. The refuge is the only "
                   "brake in the system — protecting it is not a "
                   "secondary concern, it is the concern.")
    elif refuge_gone:
        headline = "COUPLED_REFUGE_REMOVED"
        reading = ("consumer still declines with the resource, so the "
                   "system is self-limiting — but the limit now binds "
                   "at a lower stock, and depensation can turn that into "
                   "a pit.")
    else:
        headline = "COUPLED_AND_REFUGED"
        reading = "both brakes present; this is an ecological interaction"

    return {
        "headline":            headline,
        "reading":             reading,
        "consumer_uncoupled":  uncoupled,
        "refuge_removed":      refuge_gone,
        "energetically_viable_on_resource": energetics["persists"],
        "escape_threshold":    pit.get("escape_threshold"),
        "projected_outcome":   proj["mode"],
    }


def falsifiers(system: System) -> List[Dict[str, str]]:
    """
    What measurement would overturn each verdict.

    A classification that cannot be overturned by a measurement is an
    opinion with subscripts.
    """
    return [
        {
            "claim": "the consumer is uncoupled from this resource",
            "falsified_by": "showing the consumer's numerical response "
                            "tracks this resource's density: fleet size, "
                            "effort, or population declining with stock "
                            "in the absence of regulation",
            "statistic": "regression of consumer growth rate on resource "
                         "density; coupling requires a positive slope "
                         "that survives controlling for policy",
        },
        {
            "claim": "the low-density refuge has been removed",
            "falsified_by": "fitting Type II and Type III to CPUE-versus-"
                            "abundance by decade and finding Type III "
                            "still wins with q well above 1",
            "statistic": "functional_response.fit_functional_response on "
                         "the decade's data",
        },
        {
            "claim": "recruitment is depensatory",
            "falsified_by": "showing per-capita recruitment RISES as "
                            "spawner biomass falls, i.e. compensation is "
                            "intact at low stock",
            "statistic": "slope of log(R/S) against S at the low end of "
                         "the observed range",
        },
        {
            "claim": "the consumer is not energetically viable on this "
                     "resource",
            "falsified_by": "an energy budget showing e*f(N) >= m without "
                            "counting subsidised inputs",
            "statistic": "energy_return.predator_persistence with "
                         "measured intake and metabolic cost",
        },
    ]


def compare(systems: Sequence[System], horizon: float = 300.0
            ) -> List[Dict[str, object]]:
    """Audit several systems and return the headline rows side by side."""
    rows = []
    for s in systems:
        r = audit(s, horizon)
        rows.append({
            "system":        s.name,
            "interaction":   r["classification"]["interaction"],
            "coupling":      r["classification"]["coupling_index"],
            "refuge":        r["refuge"]["refuge_index_at_5pct_K"],
            "viable_on_resource": r["energetics"]["persists"],
            "headline":      r["verdict"]["headline"],
            "outcome":       r["projection"]["mode"],
        })
    return rows


if __name__ == "__main__":
    print("EXTRACTION AUDIT")
    print("=" * 78)

    base = dict(r=0.5, K=1.0, a=2.0, h=1.0, e=0.45, m=0.2)

    systems = [
        System("ecological predator",
               N=0.8, P=0.1,
               params=Params(**base, q=2.0, S=0.0, kind="III"),
               alpha=1.0, beta=0.5, natural_mortality=0.4,
               stock_measured=True, subsidy_measured=True,
               notes="reference case: no subsidy, refuge intact"),
        System("subsidised fleet, refuge intact",
               N=0.8, P=0.1,
               params=Params(**base, q=2.0, S=0.05, kind="III"),
               alpha=1.0, beta=0.5, natural_mortality=0.4,
               stock_measured=True, subsidy_measured=True,
               notes="fuel subsidy present, acoustic detection not yet "
                     "deployed"),
        System("subsidised fleet, refuge removed",
               N=0.8, P=0.1,
               params=Params(**base, q=1.0, S=0.05, kind="II"),
               alpha=1.0, beta=0.5, natural_mortality=0.4,
               stock_measured=True, subsidy_measured=True,
               notes="fuel subsidy plus pooled-fleet acoustic routing"),
        System("mined stock (no recruitment)",
               N=0.8, P=0.1,
               params=Params(r=0.0, K=1.0, a=2.0, h=1.0, q=1.0, e=0.45,
                             m=0.2, S=0.05, kind="II"),
               stock_measured=True, subsidy_measured=False,
               notes="fossil aquifer; r = 0 by hydrogeology, not by "
                     "assumption"),
    ]

    rows = compare(systems)
    print(f"\n{'system':34s} {'class':16s} {'coup':>5} {'refuge':>7} "
          f"{'headline':26s}")
    print("-" * 78)
    for r in rows:
        print(f"{r['system']:34s} {r['interaction']:16s} "
              f"{r['coupling']:5.2f} {r['refuge']:7.3f} {r['headline']:26s}")

    print("\n\nFULL AUDIT — 'subsidised fleet, refuge removed'")
    print("=" * 78)
    full = audit(systems[2])
    v = full["verdict"]
    print(f"  headline : {v['headline']}")
    print(f"  reading  : {v['reading']}")
    print(f"  outcome  : {v['projected_outcome']}")
    print(f"  escape threshold (biomass, not effort): "
          f"{v['escape_threshold']:.4f}")
    print(f"  consumer standing stock at N=0: "
          f"{full['classification']['consumer_at_N_zero']:.4f}")
    print(f"  viable on this resource alone: "
          f"{full['energetics']['persists']} "
          f"(deficit {full['energetics']['deficit']:.4f})")
    print("\n  falsifiers:")
    for f in full["falsifiers"]:
        print(f"    - {f['claim']}")
        print(f"        overturned by: {f['falsified_by']}")
