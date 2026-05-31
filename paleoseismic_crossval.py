# paleoseismic_crossval.py  -- CC0, stdlib-only
#
# Two distinct falsification tests. They are deliberately separated because
# blurring them is how the seductive synchrony claim survives peer review.
#
# SYN-01  CO-DATING (defensible local claim)
#   For each narrative, test whether the Wang/Skempton mechanism is
#   PHYSICALLY PLAUSIBLE given local earthquake context (M, r).
#   SUPPORTED if >= PLAUSIBLE_FRACTION of narratives exceed the Wang threshold
#   at the documented or inferred local seismicity.
#   Mechanism is MEASURED (AQ-01/AQ-02), so SYN-01 lives or dies on whether
#   the energy density at the narrative site is sufficient — not on abstract
#   cross-continental correlation.
#
# SYN-02  SYNCHRONY (seductive claim, built to stay DEAD)
#   Tests whether events in DIFFERENT continental regions cluster tighter than
#   a Poisson null once dating smear is convolved in.
#   Requires: tight dates (smear < TIGHT_SMEAR_YR) from >= MIN_TIGHT_DATES
#   different regions. Without these, NOT_SUPPORTED by construction.
#   As shipped: placeholder smear = 5000 yr >> TIGHT_SMEAR_YR. NOT_SUPPORTED.
#
# Time convention: t in years BEFORE PRESENT (BP), t >= 0.

import math
import random

from aquifer_pressure_head import seismic_energy_density, classify_response

# ── PLACEHOLDER NARRATIVE DATA ────────────────────────────────────────────────
#
# Format:
#   t_bp          : years before present (central estimate)
#   date_smear_yr : 1-sigma uncertainty on t_bp (determines SYN-02 eligibility)
#   region        : continent / ocean-basin identifier (for SYN-02 grouping)
#   M_context     : plausible local earthquake magnitude (from regional geology)
#   r_context_km  : plausible epicentral distance to aquifer/emergence site (km)
#   source        : "synthetic_placeholder" until real provenance exists
#
# Replace with real, provenanced entries to test against the world.
# SYN-01 is SUPPORTED on these placeholders (mechanism is plausible).
# SYN-02 is NOT_SUPPORTED (smear too large, sample too sparse).

PALEOSEISMIC_NARRATIVES = [
    {"t_bp": 8200,   "date_smear_yr": 5000, "region": "N_Atlantic",
     "M_context": 7.0, "r_context_km": 80,   "source": "synthetic_placeholder"},
    {"t_bp": 11500,  "date_smear_yr": 5000, "region": "E_Mediterranean",
     "M_context": 6.5, "r_context_km": 60,   "source": "synthetic_placeholder"},
    {"t_bp": 14700,  "date_smear_yr": 5000, "region": "Pacific_Rim",
     "M_context": 7.5, "r_context_km": 100,  "source": "synthetic_placeholder"},
    {"t_bp": 25000,  "date_smear_yr": 5000, "region": "S_Asia",
     "M_context": 6.0, "r_context_km": 70,   "source": "synthetic_placeholder"},
    {"t_bp": 55000,  "date_smear_yr": 5000, "region": "W_Africa",
     "M_context": 5.5, "r_context_km": 90,   "source": "synthetic_placeholder"},
]

# ── PARAMETERS ────────────────────────────────────────────────────────────────

PLAUSIBLE_FRACTION = 0.5    # SYN-01: fraction of narratives needing non-NONE
TIGHT_SMEAR_YR     = 1000   # SYN-02: maximum date_smear_yr to count as "tight"
MIN_TIGHT_DATES    = 3      # SYN-02: minimum tight-dated events needed from
                            #          distinct regions to attempt the test
N_MC_TRIALS        = 1000   # Poisson null shuffle iterations
MC_SEED            = 42
T_RANGE_BP         = (0, 150000)


# ── SYN-01: MECHANISM PLAUSIBILITY ───────────────────────────────────────────

def syn01_mechanism_check(narratives: list = None,
                           s_base: float = 0.0) -> dict:
    """
    SYN-01: is the Wang/Skempton mechanism physically plausible for each
    narrative given local M and r?

    Returns SUPPORTED if >= PLAUSIBLE_FRACTION of entries exceed the energy
    threshold at s_base coupling.  s_base lowers thresholds (AQ-03).

    Returns NOT_SUPPORTED if sample is too small or fraction is below threshold.
    """
    if narratives is None:
        narratives = PALEOSEISMIC_NARRATIVES

    n = len(narratives)
    plausible = 0
    details = []
    for entry in narratives:
        M = entry["M_context"]
        r = entry["r_context_km"]
        e = seismic_energy_density(M, r)
        cls = classify_response(e, s_base)
        is_plausible = cls != "NONE"
        if is_plausible:
            plausible += 1
        details.append({
            "t_bp": entry["t_bp"],
            "region": entry["region"],
            "M": M, "r_km": r,
            "e_J_m3": round(e, 6),
            "classification": cls,
            "plausible": is_plausible,
        })

    frac = plausible / n if n else 0.0
    if n < 2:
        verdict = "NOT_SUPPORTED"
        reason = f"insufficient entries: {n}"
    elif frac >= PLAUSIBLE_FRACTION:
        verdict = "SUPPORTED"
        reason = (f"{plausible}/{n} = {frac:.0%} narratives have a plausible "
                  f"seismic mechanism (>= {PLAUSIBLE_FRACTION:.0%} required). "
                  f"Wang/Skempton threshold exceeded at documented M, r.")
    else:
        verdict = "NOT_SUPPORTED"
        reason = (f"only {plausible}/{n} = {frac:.0%} narratives exceed the "
                  f"energy threshold (need {PLAUSIBLE_FRACTION:.0%}).")
    return {
        "verdict":    verdict,
        "reason":     reason,
        "plausible_fraction": round(frac, 3),
        "n_narratives": n,
        "s_base":     s_base,
        "details":    details,
    }


# ── SYN-02: CROSS-CONTINENTAL SYNCHRONY ──────────────────────────────────────

def _poisson_min_gap(n: int, T: float, n_mc: int = N_MC_TRIALS,
                     seed: int = MC_SEED) -> dict:
    """
    Monte-Carlo null: minimum inter-event gap distribution for n events
    placed uniformly at random in [0, T].
    Returns p05 (5th pct = typical minimum gap) and full distribution stats.
    """
    rng = random.Random(seed)
    min_gaps = []
    for _ in range(n_mc):
        times = sorted(rng.uniform(0, T) for _ in range(n))
        if len(times) < 2:
            min_gaps.append(T)
        else:
            gaps = [times[i+1] - times[i] for i in range(len(times)-1)]
            min_gaps.append(min(gaps))
    min_gaps.sort()
    return {
        "p05": min_gaps[int(0.05 * n_mc)],
        "p50": min_gaps[int(0.50 * n_mc)],
        "p95": min_gaps[int(0.95 * n_mc)],
    }


def syn02_synchrony_test(narratives: list = None) -> dict:
    """
    SYN-02: do cross-continental narrative dates cluster tighter than
    independent Poisson seismicity?

    Gate 1: require >= MIN_TIGHT_DATES entries with date_smear_yr < TIGHT_SMEAR_YR
            from at least 2 distinct regions.  Without tight dates the test
            cannot distinguish real synchrony from a dating-resolution illusion.
    Gate 2 (if passed): observed minimum inter-event gap < Poisson null p05
            (i.e. significantly TIGHTER than chance).

    With placeholder data (smear = 5000 yr >> 1000 yr): Gate 1 fails ->
    NOT_SUPPORTED. That is the honest default.
    """
    if narratives is None:
        narratives = PALEOSEISMIC_NARRATIVES

    # Gate 1: collect tight-dated entries from distinct regions
    tight = [e for e in narratives
             if e.get("date_smear_yr", 1e9) < TIGHT_SMEAR_YR]
    tight_regions = set(e["region"] for e in tight)

    if len(tight) < MIN_TIGHT_DATES or len(tight_regions) < 2:
        return {
            "verdict":    "NOT_SUPPORTED",
            "reason":     (f"insufficient tight-dated entries: {len(tight)} "
                           f"with smear < {TIGHT_SMEAR_YR} yr from "
                           f"{len(tight_regions)} region(s); need "
                           f"{MIN_TIGHT_DATES} from >=2 regions. "
                           f"Most likely a dating-resolution artifact. "
                           f"Supply provenanced radiocarbon/U-Pb dates to retry."),
            "n_tight":    len(tight),
            "tight_regions": sorted(tight_regions),
        }

    # Gate 2: clustering test on tight-dated events
    T_range = T_RANGE_BP[1] - T_RANGE_BP[0]
    times = sorted(e["t_bp"] for e in tight)
    if len(times) < 2:
        obs_min_gap = T_range
    else:
        gaps = [times[i+1] - times[i] for i in range(len(times)-1)]
        obs_min_gap = min(gaps)

    null = _poisson_min_gap(len(tight), T_range)
    if obs_min_gap < null["p05"]:
        verdict = "SUPPORTED"
        reason = (f"observed min gap {obs_min_gap:.0f} yr < Poisson p05 "
                  f"({null['p05']:.0f} yr) with {len(tight)} tight-dated events "
                  f"from {len(tight_regions)} regions.")
    else:
        verdict = "NOT_SUPPORTED"
        reason = (f"observed min gap {obs_min_gap:.0f} yr >= Poisson p05 "
                  f"({null['p05']:.0f} yr); clustering not significant.")

    return {
        "verdict":       verdict,
        "reason":        reason,
        "n_tight":       len(tight),
        "tight_regions": sorted(tight_regions),
        "obs_min_gap_yr": obs_min_gap,
        "poisson_p05_yr": null["p05"],
        "poisson_p50_yr": null["p50"],
    }


# ── COMBINED REPORT ───────────────────────────────────────────────────────────

def run_falsification(narratives: list = None,
                       s_base: float = 0.0,
                       verbose: bool = False) -> dict:
    """
    Run both SYN-01 and SYN-02. Returns combined verdict dict.

    SYN-01 SUPPORTED  -> local seismic mechanism is plausible.
    SYN-02 NOT_SUPPORTED -> synchrony not demonstrated (expected default).
    """
    r1 = syn01_mechanism_check(narratives, s_base)
    r2 = syn02_synchrony_test(narratives)

    result = {
        "syn01_verdict": r1["verdict"],
        "syn01_reason":  r1["reason"],
        "syn02_verdict": r2["verdict"],
        "syn02_reason":  r2["reason"],
        "syn01_plausible_fraction": r1["plausible_fraction"],
        "syn02_n_tight":            r2.get("n_tight", 0),
    }

    if verbose:
        print("=== SYN-01: LOCAL SEISMIC MECHANISM ===")
        print(f"  verdict : {r1['verdict']}")
        print(f"  reason  : {r1['reason']}")
        print()
        print("=== SYN-02: CROSS-CONTINENTAL SYNCHRONY ===")
        print(f"  verdict : {r2['verdict']}")
        print(f"  reason  : {r2['reason']}")

    return result


if __name__ == "__main__":
    result = run_falsification(verbose=True)
    print(f"\nSYN-01: {result['syn01_verdict']}")
    print(f"SYN-02: {result['syn02_verdict']}")
