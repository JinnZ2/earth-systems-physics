# financial_energy_footprint.py
# earth-systems-physics
# CC0 -- No Rights Reserved
"""
Financial-system energy footprint: one instrument, three pieces assembled.

  BASE UNIT (flow-rate referent)
      M = DeltaE_net / Delta t
      DeltaE_net = E_delivered - E_waste - E_hidden
      Reduced from the TAF Money Equation (thermodynamic-accountability-
      framework/CLAUDE.md:3064) by [CHOICE 5].

  OVERHEAD MULTIPLIER (financial metabolism)
      E_total = E_base / (1 - r_effective)
      Layer values carried from dollar_energy_metabolism.OVERHEAD_LAYERS
      (imported, not copied). Every carried r is UNSOURCED in that file.

  DEPENDENCY CHAIN (uncategorized footprint)
      Named overhead categories that finance depends on but that energy
      accounting books under other sectors. Every r is UNMEASURED and is
      left empty -- no number is supplied for any of them.

How the pieces join:
      metabolism layers   -> E_waste    [CHOICE 3]
      dependency chain    -> E_hidden   [CHOICE 3]
      base energy         -> E_delivered [CHOICE 2]

Three status values for every r range:
      MEASURED            a value with a measurement record (none exist yet)
      CARRIED_UNSOURCED   a number found in this repo with no source
      UNMEASURED          no number; the range fields are None

Absent is never zero. An UNMEASURED term makes its bound one-sided, never
0.0. The banking ~2 % electricity figure is a Floor object, and a Floor
refuses to be read as a total.

Gaps are marked in-line as  GAP G-n  and listed in GAPS.
Choices are marked as [CHOICE n] and listed in CHOICES (--choices).

stdlib only. Python >= 3.8.

Usage:
    python financial_energy_footprint.py                 # strict reading
    python financial_energy_footprint.py --mode carried  # carried reading beside
    python financial_energy_footprint.py --choices
    python financial_energy_footprint.py --json
Tests:
    python test_financial_energy_footprint.py   (or pytest)
"""

import json
import sys
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import dollar_energy_metabolism as _dem


# ===========================================================================
# STATUS VOCABULARY
# ===========================================================================

MEASURED = "MEASURED"
CARRIED_UNSOURCED = "CARRIED_UNSOURCED"
UNMEASURED = "UNMEASURED"
R_STATUSES = (MEASURED, CARRIED_UNSOURCED, UNMEASURED)

UNBOUNDED = "UNBOUNDED"          # an upper bound that does not exist
DIVERGENT = "DIVERGENT"          # 1 / (1 - r) with r >= 1

TRUE, FALSE, UNDETERMINED = "TRUE", "FALSE", "UNDETERMINED"

EXACT = "EXACT"
UPPER_BOUND = "UPPER_BOUND"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

MODES = ("strict", "carried")


CHOICES = {
    1: ("r_effective = sum of r_i over every contributing layer and chain "
        "item, each weight 1. r_i is stated as MJ added per MJ base, so the "
        "sum is in one unit. The source docstring says 'weighted' and defines "
        "no weights anywhere (GAP G-2)."),
    2: ("E_delivered = E_base: all base energy is read as reaching the "
        "project. Any loss before the project is not modelled."),
    3: ("Metabolism-layer overhead is booked as E_waste (TAF glossary: "
        "delivered output that produced no mission value). Dependency-chain "
        "overhead is booked as E_hidden (TAF glossary: not accounted), "
        "because it is logged under non-finance categories."),
    4: ("Recursive overhead is split between E_waste and E_hidden in "
        "proportion to their first-order r shares (GAP G-10)."),
    5: ("Referent = the Money Equation with one receiver, F(t) = 1, L = 1, "
        "multiplier terms (1 + K_op*K_cred), alpha_planetary and D_complexity "
        "dropped, and (T + S) read as Delta t (GAP G-11)."),
    6: ("Threshold conditions are three-valued: TRUE when the lower bound "
        "crosses, FALSE when a finite upper bound stays below, UNDETERMINED "
        "otherwise. A band straddling a threshold is not resolved."),
    7: ("Default mode is 'strict': only MEASURED r values enter. 'carried' "
        "adds CARRIED_UNSOURCED values and labels every result as resting on "
        "them. The two are printed apart, never merged."),
    8: ("Three sink conditions are reported and none is picked: any layer "
        "r >= 1 (the order's statement), r_effective > 0.5 (recursive "
        "overhead exceeds delivered, so M < 0 before E_hidden), and "
        "r_effective >= 1 (series diverges) (GAP G-12)."),
}


# ===========================================================================
# DATA TYPES
# ===========================================================================

@dataclass(frozen=True)
class RRange:
    """
    A recycling-fraction range. r is MJ of overhead added per MJ of base
    energy at first order (dimensionless).

    lo, hi:  floats, or None when status is UNMEASURED.
    status:  one of R_STATUSES.
    source:  where the numbers came from, or why there are none.
    """
    lo: Optional[float]
    hi: Optional[float]
    status: str
    source: str

    def __post_init__(self):
        if self.status not in R_STATUSES:
            raise ValueError("unknown status %r" % (self.status,))
        if self.status == UNMEASURED:
            if self.lo is not None or self.hi is not None:
                raise ValueError("UNMEASURED carries no number; got %r..%r"
                                 % (self.lo, self.hi))
        else:
            if self.lo is None or self.hi is None:
                raise ValueError("%s needs both lo and hi" % self.status)
            if self.lo < 0 or self.hi < self.lo:
                raise ValueError("need 0 <= lo <= hi; got %r..%r"
                                 % (self.lo, self.hi))
        if not self.source.strip():
            raise ValueError("source is required, even to say there is none")


@dataclass(frozen=True)
class Layer:
    """One overhead term: a metabolism layer or a dependency-chain item."""
    name: str
    group: str              # "metabolism" -> E_waste, "chain" -> E_hidden
    r: RRange
    what: str
    logged_under: str = ""  # chain only: where accounting books it
    would_measure: str = ""


@dataclass(frozen=True)
class Floor:
    """
    A figure that bounds a quantity from below and is not its total.

    as_total() raises: a floor read as a total is the error this type
    exists to block.
    """
    value: float
    unit: str
    quantity: str
    excludes: Tuple[str, ...]
    status: str
    source: str

    def as_total(self):
        raise FloorIsNotATotal(
            "%s = %s %s is a FLOOR. It excludes: %s"
            % (self.quantity, self.value, self.unit, "; ".join(self.excludes)))


class FloorIsNotATotal(Exception):
    pass


# ===========================================================================
# PIECE 2 -- METABOLISM LAYERS (carried, unsourced)
# ===========================================================================
# GAP G-1: no layer r has a measurement record. The values below are the
# numbers in dollar_energy_metabolism.OVERHEAD_LAYERS, which states no source.
# GAP G-3: margin_stack r 0.23-1.40 is not reproducible from the stated
# 35-70 % money capture (capture: 0.35-0.70; capture/(1-capture): 0.54-2.33).
# GAP G-4: leverage r does not state how 3-10x positions became energy.

_CARRIED_SOURCE = ("dollar_energy_metabolism.OVERHEAD_LAYERS @ fd0d99a; "
                   "no citation, derivation or measurement in that file")

METABOLISM_LAYERS = tuple(
    Layer(
        name=lay.name,
        group="metabolism",
        r=RRange(lay.r_low, lay.r_high, CARRIED_UNSOURCED, _CARRIED_SOURCE),
        what=lay.description,
        would_measure=("energy consumed by the '%s' layer per unit energy "
                       "delivered to the funded project" % lay.name),
    )
    for lay in _dem.OVERHEAD_LAYERS
)

# GAP G-4: leverage multiplier. Positions per deployed dollar is carried; the
# energy per maintained position is unmeasured, so the multiplier has no
# energy value of its own here.
LEVERAGE_POSITIONS_PER_DOLLAR = RRange(
    3.0, 10.0, CARRIED_UNSOURCED,
    "work order + leverage layer description; no source")
ENERGY_PER_POSITION = None   # GAP G-4: UNMEASURED, MJ per position per year


# ===========================================================================
# PIECE 3 -- DEPENDENCY CHAIN (all UNMEASURED)
# ===========================================================================
# GAP G-5: every r below is UNMEASURED. No number is supplied.
# The logged_under column is the work order's claim (finance-dependent energy
# booked under non-finance categories), carried as stated; it has not been
# checked against any national or sector energy-accounting table.
# GAP G-8: no check that these items and the metabolism layers are disjoint
# (compliance_stack vs the political layer's regulatory process;
# hft_colocation vs the leverage layer's servers). Double counting is
# possible and unmeasured.

_CHAIN_SOURCE = "UNMEASURED: no value located in any reachable repository"

DEPENDENCY_CHAIN = (
    Layer("financial_software_developers", "chain",
          RRange(None, None, UNMEASURED, _CHAIN_SOURCE),
          "developers building and maintaining banking, trading and payment "
          "software",
          logged_under="software / information services",
          would_measure="finance-client share of developer facility and build "
                        "compute energy"),
    Layer("security_engineering", "chain",
          RRange(None, None, UNMEASURED, _CHAIN_SOURCE),
          "fraud detection, intrusion response, key management, pen testing",
          logged_under="IT / professional services",
          would_measure="finance-client share of security operations energy"),
    Layer("settlement_rails", "chain",
          RRange(None, None, UNMEASURED, _CHAIN_SOURCE),
          "payment networks, clearing, settlement messaging",
          logged_under="data centres / telecommunications",
          would_measure="network operator energy per settled transaction "
                        "times transaction count"),
    Layer("exchanges", "chain",
          RRange(None, None, UNMEASURED, _CHAIN_SOURCE),
          "matching engines, market-data distribution, order gateways",
          logged_under="data centres",
          would_measure="exchange facility energy, metered"),
    Layer("transaction_chip_fab", "chain",
          RRange(None, None, UNMEASURED, _CHAIN_SOURCE),
          "card chips, secure elements, HSMs, payment terminals (embodied)",
          logged_under="semiconductor manufacturing",
          would_measure="fab energy per die times finance-bound die volume"),
    Layer("hft_colocation", "chain",
          RRange(None, None, UNMEASURED, _CHAIN_SOURCE),
          "colocated trading servers, microwave and fibre latency links",
          logged_under="data centres / telecommunications",
          would_measure="colocation cage power plus link power, metered"),
    Layer("compliance_stack", "chain",
          RRange(None, None, UNMEASURED, _CHAIN_SOURCE),
          "KYC / AML screening, regulatory reporting, audit tooling",
          logged_under="professional services / data centres",
          would_measure="compliance compute and office energy attributable to "
                        "finance"),
    # GAP G-6: embodied energy of all finance infrastructure (buildings,
    # servers, terminals) beyond the chip item above. UNMEASURED.
    Layer("embodied_infrastructure", "chain",
          RRange(None, None, UNMEASURED, _CHAIN_SOURCE),
          "embodied energy of buildings, servers, networks and terminals "
          "serving finance",
          logged_under="construction / manufacturing",
          would_measure="life-cycle embodied energy amortised per year"),
)


# ===========================================================================
# THE 2 % FIGURE -- A FLOOR, NOT A TOTAL
# ===========================================================================
# GAP G-9: the ~2 % figure has no source anywhere in the repo. It is
# ELECTRICITY, not primary energy. It is held here only as a lower bound on
# the banking sector's own electricity, and it excludes everything in the
# dependency chain, all embodied energy, and the leverage multiplier.

BANKING_ELECTRICITY_FLOOR = Floor(
    value=0.02,
    unit="fraction of global electricity",
    quantity="banking-sector electricity",
    excludes=(
        "the dependency chain (DEPENDENCY_CHAIN, booked under other sectors)",
        "embodied energy of finance infrastructure",
        "the leverage multiplier (3-10x positions per deployed dollar)",
        "non-electric primary energy",
    ),
    status=CARRIED_UNSOURCED,
    source="dollar_energy_metabolism.py:87, inside a description string; "
           "no citation",
)


GAPS = (
    ("G-1", UNMEASURED, "every metabolism-layer r",
     "carried values have no source; strict mode excludes them",
     "per-layer energy consumed per unit energy delivered, metered"),
    ("G-2", "THIN", "r_effective weighting",
     "source docstring says 'weighted'; no weights are defined [CHOICE 1]",
     "a stated weighting with its derivation"),
    ("G-3", "THIN", "margin_stack money-to-energy conversion",
     "35-70 % capture does not reproduce r 0.23-1.40",
     "energy intensity of intermediary spend vs project spend"),
    ("G-4", UNMEASURED, "leverage multiplier energy",
     "3-10x positions carried; energy per position absent",
     "energy per maintained position per year"),
    ("G-5", UNMEASURED, "every dependency-chain r",
     "no value located; logged_under carried from the order, unverified",
     "sector energy tables split by finance-client share"),
    ("G-6", UNMEASURED, "embodied energy of finance infrastructure",
     "not in any source", "life-cycle inventory amortised per year"),
    ("G-7", "THIN", "non-negativity",
     "all bounds assume r_i >= 0 and E_hidden >= 0",
     "a case where an overhead term returns energy to the project"),
    ("G-8", "THIN", "layer overlap",
     "no disjointness check between layers and chain items",
     "an allocation key assigning each metered joule to one item"),
    ("G-9", "FLOOR", "banking ~2 % of global electricity",
     "unsourced; electricity only; excludes chain, embodied, leverage",
     "a cited sector electricity figure plus the excluded terms"),
    ("G-10", "THIN", "recursion split between E_waste and E_hidden",
     "proportional split is assumed [CHOICE 4]",
     "observed second-round spending by category"),
    ("G-11", "THIN", "referent reduced from the Money Equation",
     "F(t), L, p_i, K terms, alpha, D dropped; (T+S) read as dt [CHOICE 5]",
     "values for the dropped terms"),
    ("G-12", "THIN", "sink threshold",
     "three conditions reported, none picked [CHOICE 8]",
     "a stated definition of 'net energy sink' that selects one"),
)


# ===========================================================================
# PIECE 1 -- THE FLOW-RATE REFERENT (base unit)
# ===========================================================================

def flow_rate_referent(E_delivered: Optional[float],
                       E_waste: Optional[float],
                       E_hidden: Optional[float],
                       dt: Optional[float]) -> Dict:
    """
    M = (E_delivered - E_waste - E_hidden) / dt      [CHOICE 5]

    Parameters:
        E_delivered, E_waste, E_hidden: energy over the interval (any one
            energy unit, used consistently), or None when unmeasured.
        dt: interval length (> 0) in any one time unit, or None.

    Returns dict with:
        M:     the rate in (energy unit)/(time unit), or None
        bound: EXACT when all three energies are given;
               UPPER_BOUND when E_hidden is None (GAP G-7: E_hidden >= 0
               is assumed, so an unmeasured E_hidden can only lower M);
               NOT_COMPUTABLE when E_delivered, E_waste or dt is missing,
               or dt <= 0.
    A measured E_hidden of 0.0 is EXACT; None is not 0.0.
    """
    if E_delivered is None or E_waste is None or dt is None or dt <= 0:
        missing = [n for n, v in (("E_delivered", E_delivered),
                                  ("E_waste", E_waste), ("dt", dt))
                   if v is None]
        if dt is not None and dt <= 0:
            missing.append("dt <= 0")
        return {"M": None, "bound": NOT_COMPUTABLE, "missing": missing}
    if E_hidden is None:
        return {"M": (E_delivered - E_waste) / dt, "bound": UPPER_BOUND,
                "missing": ["E_hidden"]}
    return {"M": (E_delivered - E_waste - E_hidden) / dt, "bound": EXACT,
            "missing": []}


# ===========================================================================
# PIECE 2 -- THE OVERHEAD MULTIPLIER
# ===========================================================================

def multiplier(r: float):
    """1 / (1 - r) for r < 1; DIVERGENT for r >= 1."""
    if r >= 1.0:
        return DIVERGENT
    return 1.0 / (1.0 - r)


def contributes(layer: Layer, mode: str) -> bool:
    """Whether a layer's numbers enter under the given mode [CHOICE 7]."""
    if mode not in MODES:
        raise ValueError("mode must be one of %r" % (MODES,))
    if layer.r.status == MEASURED:
        return True
    if layer.r.status == CARRIED_UNSOURCED:
        return mode == "carried"
    return False


def r_effective(layers, mode: str = "strict") -> Dict:
    """
    r_effective band over a set of layers [CHOICE 1].

    lo: sum of lo over contributing layers. Valid as a floor because every
        excluded layer has r >= 0 (GAP G-7).
    hi: sum of hi over contributing layers, or UNBOUNDED when any layer is
        excluded (its r is unknown, so nothing caps the sum).
    Also returns the per-group (metabolism / chain) lo and hi.
    """
    lo = 0.0
    hi = 0.0
    excluded = []
    contributing = []
    by_group = {"metabolism": [0.0, 0.0], "chain": [0.0, 0.0]}
    for lay in layers:
        if contributes(lay, mode):
            contributing.append(lay.name)
            lo += lay.r.lo
            hi += lay.r.hi
            by_group[lay.group][0] += lay.r.lo
            by_group[lay.group][1] += lay.r.hi
        else:
            excluded.append(lay.name)
    hi_out = UNBOUNDED if excluded else hi
    group_out = {}
    for g, (glo, ghi) in by_group.items():
        g_excluded = [l.name for l in layers
                      if l.group == g and l.name in excluded]
        group_out[g] = {"lo": glo, "hi": UNBOUNDED if g_excluded else ghi}
    return {"lo": lo, "hi": hi_out, "contributing": contributing,
            "excluded": excluded, "by_group": group_out}


def threshold(lo: float, hi, t: float, strict: bool = False) -> str:
    """
    Three-valued test of r >= t (or r > t when strict) on a band [CHOICE 6].
    """
    crosses_lo = lo > t if strict else lo >= t
    if crosses_lo:
        return TRUE
    if hi != UNBOUNDED:
        below_hi = hi <= t if strict else hi < t
        if below_hi:
            return FALSE
    return UNDETERMINED


def any_layer_ge_1(layers, mode: str) -> str:
    """The order's condition: any single layer with r >= 1 [CHOICE 8]."""
    states = []
    for lay in layers:
        if contributes(lay, mode):
            states.append(threshold(lay.r.lo, lay.r.hi, 1.0))
        else:
            states.append(UNDETERMINED)
    if TRUE in states:
        return TRUE
    if states and all(s == FALSE for s in states):
        return FALSE
    return UNDETERMINED


def _overhead(E_base: float, r_part: float, r_total: float):
    """Energy of one overhead part under recursion [CHOICE 4] (GAP G-10)."""
    m = multiplier(r_total)
    if m == DIVERGENT:
        return DIVERGENT
    return E_base * r_part * m


def footprint(E_base: float = 1.0, dt: float = 1.0, mode: str = "strict",
              layers=None) -> Dict:
    """
    The assembled instrument.

    E_base:  base energy delivered to the project over dt (any energy unit).
             Default 1.0, so every energy output reads as a multiple of
             E_base. No default energy-per-dollar figure is carried: the
             source module's MJ_PER_DOLLAR_GLOBAL = 5.7 is unsourced.
    dt:      interval, > 0.
    mode:    'strict' or 'carried' [CHOICE 7].
    layers:  defaults to METABOLISM_LAYERS + DEPENDENCY_CHAIN.

    Returns bands, never points, wherever any term is excluded. A band end
    of UNBOUNDED means no bound exists on that side.
    """
    if layers is None:
        layers = METABOLISM_LAYERS + DEPENDENCY_CHAIN
    if E_base <= 0:
        raise ValueError("E_base must be > 0")
    reff = r_effective(layers, mode)
    lo, hi = reff["lo"], reff["hi"]
    g = reff["by_group"]

    def band(fn_lo, fn_hi):
        return {"lo": fn_lo, "hi": fn_hi}

    # E_total = E_base * multiplier(r)
    m_lo = multiplier(lo)
    m_hi = UNBOUNDED if hi == UNBOUNDED else multiplier(hi)
    E_total = band(
        DIVERGENT if m_lo == DIVERGENT else E_base * m_lo,
        m_hi if m_hi in (UNBOUNDED, DIVERGENT) else E_base * m_hi)

    # E_waste <- metabolism, E_hidden <- chain [CHOICE 3] [CHOICE 4].
    # Each part increases in both its own r and the total r, so the low end
    # uses every lo and the high end every hi.
    E_waste_lo = _overhead(E_base, g["metabolism"]["lo"], lo)
    E_hidden_lo = _overhead(E_base, g["chain"]["lo"], lo)
    if hi == UNBOUNDED:
        E_waste_hi = UNBOUNDED
        E_hidden_hi = UNBOUNDED
    else:
        E_waste_hi = _overhead(E_base, g["metabolism"]["hi"], hi)
        E_hidden_hi = _overhead(E_base, g["chain"]["hi"], hi)

    # E_delivered = E_base [CHOICE 2].
    # M high end: least overhead. If any chain item is excluded, E_hidden is
    # unmeasured there and M is an upper bound.
    chain_excluded = g["chain"]["hi"] == UNBOUNDED
    if E_waste_lo == DIVERGENT:
        M_hi = {"M": None, "bound": DIVERGENT, "missing": []}
    else:
        M_hi = flow_rate_referent(
            E_base, E_waste_lo,
            None if chain_excluded else E_hidden_lo, dt)
    # M low end: most overhead. Unbounded overhead leaves no lower end.
    if hi == UNBOUNDED or E_waste_hi == DIVERGENT:
        M_lo = {"M": None, "bound": UNBOUNDED, "missing": reff["excluded"]}
    else:
        M_lo = flow_rate_referent(E_base, E_waste_hi, E_hidden_hi, dt)

    return {
        "mode": mode,
        "E_base": E_base,
        "dt": dt,
        "r_effective": {"lo": lo, "hi": hi},
        "r_by_group": g,
        "contributing": reff["contributing"],
        "excluded": reff["excluded"],
        "E_total": E_total,
        "E_waste": band(E_waste_lo, E_waste_hi),
        "E_hidden": band(E_hidden_lo, E_hidden_hi),
        "M": {"lo": M_lo, "hi": M_hi},
        "sink_conditions": {                          # [CHOICE 8]
            "any_layer_r_ge_1": any_layer_ge_1(layers, mode),
            "r_effective_gt_half": threshold(lo, hi, 0.5, strict=True),
            "r_effective_ge_1": threshold(lo, hi, 1.0),
        },
        "rests_on_carried": mode == "carried" and any(
            l.r.status == CARRIED_UNSOURCED and contributes(l, mode)
            for l in layers),
    }


# ===========================================================================
# RENDER
# ===========================================================================

def _fmt(v) -> str:
    if v is None:
        return "None"
    if isinstance(v, str):
        return v
    return "%.4f" % v


def render(mode: str = "strict") -> str:
    """Deterministic ASCII report for one mode."""
    f = footprint(mode=mode)
    out = []
    out.append("FINANCIAL ENERGY FOOTPRINT  mode=%s  E_base=1 dt=1" % mode)
    if f["rests_on_carried"]:
        out.append("RESTS ON CARRIED_UNSOURCED VALUES -- not a measurement")
    else:
        out.append("only MEASURED values are summed; CARRIED_UNSOURCED values "
                   "are listed and excluded")
    out.append("")
    out.append("%-30s %-18s %8s %8s" % ("term", "status", "r_lo", "r_hi"))
    for lay in METABOLISM_LAYERS + DEPENDENCY_CHAIN:
        out.append("%-30s %-18s %8s %8s" % (
            lay.name, lay.r.status, _fmt(lay.r.lo), _fmt(lay.r.hi)))
    out.append("")
    r = f["r_effective"]
    out.append("r_effective      lo %s  hi %s" % (_fmt(r["lo"]), _fmt(r["hi"])))
    for key in ("E_total", "E_waste", "E_hidden"):
        out.append("%-16s lo %s  hi %s" % (
            key, _fmt(f[key]["lo"]), _fmt(f[key]["hi"])))
    for end in ("hi", "lo"):
        m = f["M"][end]
        out.append("M %-14s %s  [%s]" % (
            "(" + end + " end)", _fmt(m["M"]), m["bound"]))
    out.append("")
    out.append("sink conditions (none picked):")
    for k, v in f["sink_conditions"].items():
        out.append("  %-22s %s" % (k, v))
    out.append("")
    fl = BANKING_ELECTRICITY_FLOOR
    out.append("FLOOR  %s >= %s %s  [%s]" % (
        fl.quantity, fl.value, fl.unit, fl.status))
    for e in fl.excludes:
        out.append("  excludes: %s" % e)
    out.append("")
    out.append("excluded from the sum: %d of %d terms" % (
        len(f["excluded"]), len(METABOLISM_LAYERS + DEPENDENCY_CHAIN)))
    out.append("gaps: %s" % ", ".join(g[0] for g in GAPS))
    return "\n".join(out)


def render_choices() -> str:
    return "\n".join("[CHOICE %d] %s" % (k, CHOICES[k])
                     for k in sorted(CHOICES))


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        sys.stderr.write("refused: run test_financial_energy_footprint.py\n")
        return 2
    if "--choices" in argv:
        print(render_choices())
        return 0
    mode = "strict"
    if "--mode" in argv:
        i = argv.index("--mode")
        if i + 1 >= len(argv) or argv[i + 1] not in MODES:
            sys.stderr.write("--mode needs one of %r\n" % (MODES,))
            return 2
        mode = argv[i + 1]
    if "--json" in argv:
        print(json.dumps(footprint(mode=mode), indent=2, sort_keys=True))
        return 0
    print(render(mode))
    return 0


def coupling_state() -> dict:
    """Dict export, per repo convention."""
    f = footprint(mode="strict")
    return {
        "r_effective_lo_strict": f["r_effective"]["lo"],
        "r_effective_hi_strict": f["r_effective"]["hi"],
        "n_terms_unmeasured": sum(
            1 for l in METABOLISM_LAYERS + DEPENDENCY_CHAIN
            if l.r.status == UNMEASURED),
        "banking_electricity_floor": BANKING_ELECTRICITY_FLOOR.value,
    }


if __name__ == "__main__":
    sys.exit(main())
