#!/usr/bin/env python3
# archive_siting_bias.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# MARKER: archive siting bias. A place marker for a sensed shape, not a
# thesis. The prose marker lives in ARCHIVE_SITING_BIAS.md; this file is
# the computable half.
#
# SHAPE
#   archive_location  = f(preservation conditions)
#   source_location   = g(process physics)
#   bias_sign         = sign( corr(f, g) )          knowable a priori
#   bias_magnitude    = h( transport operator, distance )
#   correctability    = class( transport operator )
#
# The environment that PRESERVES is not the environment that HOSTS.
# Where the two anti-correlate, every reconstruction built from the
# archive carries a bias whose sign is known before any data exist.
#
# ENERGY-FLOW READ
#   source box ──transport operator──▶ archive box ──inversion──▶ estimate
#                (loss λ, exchange k)                (assumes mixing)
#   The operator attenuates the signal between source and archive. The
#   inversion, if it does not model the attenuation, returns
#   A = estimate / truth < 1. The attenuation is set by λ/k: short-lived
#   species lose more in transit, so the bias grows as lifetime shrinks.
#
# Refutation protocol: every function returns a falsifiable field. If a
# measurement refutes a claim, update CLAIM_TABLE. Never retune to save it.
#
# Stdlib only.

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

# =====================================================================
# CALIBRATION POINT 1 — CH4, physical transport
# Lamantia et al., Nature (2026), doi 10.1038/s41586-026-10938-1
# Nevado Huascarán Summit Core A, 9.122°S 77.605°W, 6768 m asl
# 2,000 yr record, n=51 CH4, n=5 d13C-CH4, no replicates
# Data + box-model code: doi 10.5281/zenodo.18657346
# =====================================================================

CH4_BOXES = ("NH", "TN", "TS", "SH")          # 30-90N, 0-30N, 0-30S, 30-90S

# Average source strength 0-1800 CE, Tg/yr. SH is fixed in both runs.
CH4_SOURCE_POLAR_ONLY_TG_YR = {"NH": 36.0, "TN": 82.0, "TS": 81.0, "SH": 10.0}
CH4_SOURCE_WITH_SCA_TG_YR = {"NH": 36.0, "TN": 88.0, "TS": 125.0, "SH": 10.0}

# Pre-industrial concentration offsets, SCA (Huascarán) minus polar core, ppb.
CH4_OFFSET_SCA_MINUS_POLAR_PPB = {
    "GISP2": 46.0,       # Greenland
    "NEEM": 48.0,        # Greenland
    "Law Dome": 78.0,    # Antarctica
    "WAIS": 94.0,        # Antarctica
}

# Interpolated pole-to-pole gradient (GISP2 minus WAIS), ppb.
CH4_IPD_PPB = {"800-1750 CE": 44.0, "800-1750 CE sigma": 7.0, "PI 0-1850": 48.0}

# Error budget the two-endpoint model carried, Tg/yr unless stated.
CH4_ERROR_BUDGET = {
    "missing_equatorial_box_tg_yr": 50.0,           # +24 %
    "lifetime_perturbation_pm30pct_tg_yr": None,    # "smaller than above"
    "transport_exchange_pm30pct_tg_yr": 17.5,       # max
    "tn_interpolated_vs_real_tg_yr": 3.0,           # max (East Rongbuk swap)
    "monte_carlo_obs_noise_ts_box_pct": 2.59,
}

# Archive validation figures.
CH4_ARCHIVE_VALIDATION = {
    "sca_vs_mauna_loa_1985_2012_ppb": 4.0,
    "measurement_sd_ppb": 3.7,
    "pc1_covariance_with_gisp2_wais_pct": 91.0,
    "dust_ca_correlation": False,
    "visible_melt_layers": False,
}

# Confound, unresolved in the published data: polar-only TS is SOLVED by
# the model; with SCA, TS is PRESCRIBED by observation. Part of the +54 %
# is a change in what the box IS. Partial defence: swapping TN between
# interpolated and real data moved results by at most 3 Tg/yr.
CH4_CONFOUND = (
    "TS solved (polar-only) vs TS prescribed (with SCA): the +54% mixes a "
    "change in the box's role with a change in its value. Not separable "
    "from the published data; see soft_prior_sweep() for the separation "
    "procedure on a self-consistent synthetic truth."
)

# =====================================================================
# CALIBRATION POINT 2 — ENSO, statistical transport (the contrasting case)
# =====================================================================

ENSO_CALIBRATION = {
    "centre_of_action": "eastern + central equatorial Pacific",
    "at_source_archive": "coral; records ~50 yr, longest < 200 yr, sporadic",
    "remote_archive": "tree ring / sediment / ice / teleconnected coral; "
                      "long, numerous, stationarity-dependent",
    "in_band_attenuation": "< 1  (all methods lose ENSO variance in "
                           "pseudoproxy tests)",
    "low_frequency_attenuation": ">= 1 possible (multiproxy reconstructions "
                                 "find MORE low-frequency variance than "
                                 "models; method bias may overstate it)",
    "non_stationary": True,   # teleconnections documented as non-stationary
    "network_caution": "single teleconnected region or < ~20 proxies",
}

# =====================================================================
# ATTENUATION FACTOR
# A = (source estimate from remote archive)
#     / (source estimate from at-source archive)
# =====================================================================


def attenuation_factor(remote_estimate: float, at_source_estimate: float) -> float:
    """A = remote / at-source. A < 1 means the remote archive under-reads.

    remote_estimate     : source strength inferred from the remote archive
    at_source_estimate  : source strength inferred with the at-source record
    Units cancel; both in the same unit.
    """
    if at_source_estimate == 0:
        raise ZeroDivisionError("at-source estimate is zero; A undefined")
    return remote_estimate / at_source_estimate


def bias_direction(A: float, tol: float = 0.02) -> int:
    """-1 under-read (A<1), +1 over-read (A>1), 0 faithful within tol."""
    if A < 1.0 - tol:
        return -1
    if A > 1.0 + tol:
        return +1
    return 0


def ch4_attenuation() -> Dict[str, float]:
    """Attenuation factors from the published CH4 box-model runs.

    Returns TS box and combined-tropics A. Expected 0.65 and 0.77 (ASB-04).
    """
    po, sca = CH4_SOURCE_POLAR_ONLY_TG_YR, CH4_SOURCE_WITH_SCA_TG_YR
    return {
        "TS": attenuation_factor(po["TS"], sca["TS"]),
        "tropics": attenuation_factor(po["TN"] + po["TS"], sca["TN"] + sca["TS"]),
        "TN": attenuation_factor(po["TN"], sca["TN"]),
    }


def ch4_error_localization() -> Dict[str, object]:
    """Where did the polar-only estimate move when the at-source record
    was added? Per-box delta, per-box fraction, and the share of the
    total delta landing in the unmeasured cell (TS).
    """
    po, sca = CH4_SOURCE_POLAR_ONLY_TG_YR, CH4_SOURCE_WITH_SCA_TG_YR
    delta = {b: sca[b] - po[b] for b in CH4_BOXES}
    frac = {b: (delta[b] / po[b] if po[b] else 0.0) for b in CH4_BOXES}
    total = sum(delta.values())
    return {
        "delta_tg_yr": delta,
        "delta_frac": frac,
        "total_delta_tg_yr": total,
        "share_in_unmeasured_box": (delta["TS"] / total) if total else 0.0,
        "falsifier": "a re-run of the Zenodo model in which the largest "
                     "delta lands in a measured box",
    }


def offset_vs_gradient_ratio(offset_ppb: Optional[float] = None,
                             gradient_ppb: Optional[float] = None) -> float:
    """The offset the two-endpoint system could not see, divided by the
    gradient it was built to resolve. Defaults: WAIS offset 94 / IPD 48.
    ~2 means the invisible term is twice the resolved signal.
    """
    o = CH4_OFFSET_SCA_MINUS_POLAR_PPB["WAIS"] if offset_ppb is None else offset_ppb
    g = CH4_IPD_PPB["PI 0-1850"] if gradient_ppb is None else gradient_ppb
    return o / g


def siting_bias_vs_envelope(missing_box_term: Optional[float] = None,
                            envelope_terms: Optional[Sequence[float]] = None
                            ) -> Dict[str, object]:
    """ASB-05: does the siting bias exceed the full quantified parameter
    uncertainty of the model carrying it? Compares the missing-box term
    against the largest quantified perturbation term.
    """
    m = (CH4_ERROR_BUDGET["missing_equatorial_box_tg_yr"]
         if missing_box_term is None else missing_box_term)
    if envelope_terms is None:
        envelope_terms = [v for k, v in CH4_ERROR_BUDGET.items()
                          if k.endswith("_tg_yr") and v is not None
                          and k != "missing_equatorial_box_tg_yr"]
    env = max(envelope_terms) if envelope_terms else 0.0
    return {
        "missing_box_term": m,
        "envelope_max": env,
        "ratio": (m / env) if env else float("inf"),
        "exceeds_envelope": m > env,
        "falsifier": "a case where the missing-box term sits inside the "
                     "quantified parameter envelope",
    }


# =====================================================================
# FOUR-BOX STEADY-STATE MODEL (independent re-derivation, NOT the
# Zenodo code, which was not reachable from the session that wrote this)
#
#   E_i = B_i / tau_i + sum_adj (B_i - B_j) / tau_x
#
# Boxes NH | TN | TS | SH, chain adjacency. Each 30-degree tropical band
# and each 30-90 polar cap holds one quarter of the atmosphere
# (sin 30 = 0.5), so boxes are equal-mass.
# =====================================================================

TG_PER_PPB_GLOBAL_CH4 = 2.78          # Tg CH4 per ppb, whole atmosphere
TG_PER_PPB_BOX = TG_PER_PPB_GLOBAL_CH4 / 4.0
CH4_LIFETIME_YR = 9.1                 # tropospheric, IPCC AR6 order
DEFAULT_EXCHANGE_YR = 0.5             # adjacent-box exchange, illustrative

# Box centre latitudes for interpolation of the unmeasured tropics.
BOX_CENTRE_LAT = {"NH": 60.0, "TN": 15.0, "TS": -15.0, "SH": -60.0}


def _solve_linear(a: List[List[float]], b: List[float]) -> List[float]:
    """Gaussian elimination with partial pivoting. Small dense systems."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[piv] = m[piv], m[col]
        if abs(m[col][col]) < 1e-15:
            raise ValueError("singular system")
        for r in range(n):
            if r == col:
                continue
            f = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= f * m[col][c]
    return [m[i][n] / m[i][i] for i in range(n)]


@dataclass
class FourBoxModel:
    """Chain of four equal-mass boxes with first-order loss and exchange.

    lifetime_yr : per-box lifetime (dict) or a scalar applied to all
    exchange_yr : adjacent-box exchange timescale (scalar)
    tg_per_ppb  : mass-to-mixing-ratio conversion per box
    """
    lifetime_yr: object = CH4_LIFETIME_YR
    exchange_yr: float = DEFAULT_EXCHANGE_YR
    tg_per_ppb: float = TG_PER_PPB_BOX
    boxes: tuple = CH4_BOXES

    def _tau(self, box: str) -> float:
        if isinstance(self.lifetime_yr, dict):
            return float(self.lifetime_yr[box])
        return float(self.lifetime_yr)

    def _adjacent(self, i: int) -> List[int]:
        return [j for j in (i - 1, i + 1) if 0 <= j < len(self.boxes)]

    def forward(self, sources_tg_yr: Dict[str, float]) -> Dict[str, float]:
        """Steady-state concentrations (ppb) from sources (Tg/yr)."""
        n = len(self.boxes)
        k = 1.0 / self.exchange_yr
        a = [[0.0] * n for _ in range(n)]
        for i, bx in enumerate(self.boxes):
            a[i][i] = 1.0 / self._tau(bx) + k * len(self._adjacent(i))
            for j in self._adjacent(i):
                a[i][j] = -k
        b = [float(sources_tg_yr[bx]) for bx in self.boxes]
        burden = _solve_linear(a, b)
        return {bx: burden[i] / self.tg_per_ppb for i, bx in enumerate(self.boxes)}

    def invert(self, conc_ppb: Dict[str, float]) -> Dict[str, float]:
        """Sources (Tg/yr) from steady-state concentrations (ppb).
        Direct: no solve needed."""
        k = 1.0 / self.exchange_yr
        out = {}
        for i, bx in enumerate(self.boxes):
            B = conc_ppb[bx] * self.tg_per_ppb
            e = B / self._tau(bx)
            for j in self._adjacent(i):
                e += k * (B - conc_ppb[self.boxes[j]] * self.tg_per_ppb)
            out[bx] = e
        return out

    def interpolate_tropics(self, c_nh: float, c_sh: float) -> Dict[str, float]:
        """Linear-in-latitude interpolation between the two polar boxes,
        the move a polar-only reconstruction makes for the boxes it
        cannot see."""
        lat_n, lat_s = BOX_CENTRE_LAT["NH"], BOX_CENTRE_LAT["SH"]
        out = {}
        for bx in self.boxes:
            w = (BOX_CENTRE_LAT[bx] - lat_s) / (lat_n - lat_s)
            out[bx] = c_sh + w * (c_nh - c_sh)
        out["NH"], out["SH"] = c_nh, c_sh
        return out

    def polar_only_inversion(self, c_nh: float, c_sh: float) -> Dict[str, float]:
        """Sources inferred when only the two polar archives exist."""
        return self.invert(self.interpolate_tropics(c_nh, c_sh))

    def soft_prior_inversion(self, c_nh: float, c_sh: float,
                             c_ts_obs: float, weight: float,
                             c_tn_obs: Optional[float] = None) -> Dict[str, float]:
        """TS concentration = weight * observed + (1 - weight) * interpolated.
        weight 0 -> polar-only (TS solved); weight 1 -> TS prescribed.
        This is the separation procedure for the CH4_CONFOUND.

        c_tn_obs : if given, TN is prescribed too (the East Rongbuk swap).
                   If not, TN stays interpolated and the TN error is
                   dumped into the TS source through the exchange term,
                   so A_TS overshoots 1 even at weight 1."""
        c = self.interpolate_tropics(c_nh, c_sh)
        c["TS"] = weight * c_ts_obs + (1.0 - weight) * c["TS"]
        if c_tn_obs is not None:
            c["TN"] = c_tn_obs
        return self.invert(c)


def synthetic_ch4_demo(model: Optional[FourBoxModel] = None,
                       true_sources: Optional[Dict[str, float]] = None
                       ) -> Dict[str, object]:
    """Self-consistent test of the mechanism (ASB-02, ASB-03).

    Take the +SCA source column as truth, forward-model concentrations,
    then run the polar-only inversion on the two polar boxes only and
    read back A for TS and the tropics. Any A < 1 here is the operator
    plus the interpolation doing the attenuation, nothing else.
    """
    model = model or FourBoxModel()
    truth = dict(true_sources or CH4_SOURCE_WITH_SCA_TG_YR)
    conc = model.forward(truth)
    remote = model.polar_only_inversion(conc["NH"], conc["SH"])
    A_ts = attenuation_factor(remote["TS"], truth["TS"])
    A_trop = attenuation_factor(remote["TN"] + remote["TS"],
                                truth["TN"] + truth["TS"])
    A_global = attenuation_factor(sum(remote.values()), sum(truth.values()))
    return {
        "true_sources_tg_yr": truth,
        "concentrations_ppb": conc,
        "tropical_offset_ppb": {
            "TS_minus_NH": conc["TS"] - conc["NH"],
            "TS_minus_SH": conc["TS"] - conc["SH"],
        },
        "remote_sources_tg_yr": remote,
        "A_TS": A_ts,
        "A_tropics": A_trop,
        # ATTRIBUTION vs TOTAL: interpolation moves source between boxes
        # (attribution error) at any lifetime; only loss in the unseen
        # boxes changes the global total, and that scales with 1/lifetime.
        "A_global": A_global,
        "bias_direction": bias_direction(A_trop),
        "falsifier": "A >= 1 for a physical-transport operator with the "
                     "source in an unmeasured box (refutes ASB-03)",
    }


def soft_prior_sweep(weights: Sequence[float] = (0.0, 0.25, 0.5, 0.75, 1.0),
                     model: Optional[FourBoxModel] = None,
                     true_sources: Optional[Dict[str, float]] = None,
                     tn_observed: bool = False) -> List[Dict[str, float]]:
    """HANDOFF item 1, generic form: A_TS as the at-source record moves
    from soft prior (weight 0) to prescribed (weight 1).

    On a self-consistent truth A_TS rises monotonically with weight.
    With tn_observed=False it OVERSHOOTS 1 at weight 1: the still-
    interpolated neighbour (TN) is too low, and the exchange term
    charges that deficit to the prescribed box. With tn_observed=True
    (the East Rongbuk swap) A_TS = 1 at weight 1 exactly. Prescribing
    one tropical box while interpolating the other is therefore itself
    a bias, of the opposite sign.

    On the real data the same sweep run in the Zenodo model separates
    the prescribed-vs-solved confound; that run is still owed.
    """
    model = model or FourBoxModel()
    truth = dict(true_sources or CH4_SOURCE_WITH_SCA_TG_YR)
    conc = model.forward(truth)
    rows = []
    for w in weights:
        est = model.soft_prior_inversion(
            conc["NH"], conc["SH"], conc["TS"], w,
            c_tn_obs=conc["TN"] if tn_observed else None)
        rows.append({"weight": w,
                     "A_TS": attenuation_factor(est["TS"], truth["TS"]),
                     "TS_estimate_tg_yr": est["TS"]})
    return rows


# =====================================================================
# T-1  LIFETIME SCALING  (closes ASB-06)
# Same geometry, vary lifetime only. Predict monotone: shorter lifetime,
# larger deviation of A from 1.
# =====================================================================

SPECIES_LIFETIME_YR = {
    # tropospheric lifetimes, order-of-magnitude; CO2 has no first-order
    # chemical sink on these timescales, represented by a long effective
    # lifetime so the model runs.
    "CO2": 1.0e4,
    "N2O": 116.0,
    "CH4": 9.1,
    "CO": 0.17,   # ~2 months
}

CH4_MEASURED_A = {"TS": 0.65, "tropics": 0.77}   # calibration point


def lifetime_scaling(lifetimes_yr: Optional[Dict[str, float]] = None,
                     exchange_yr: float = DEFAULT_EXCHANGE_YR,
                     true_sources: Optional[Dict[str, float]] = None
                     ) -> Dict[str, object]:
    """Predicted A_TS per species from the four-box model, same source
    geometry, lifetime varied. Returns the ranking and whether the
    prediction is monotone in lifetime (ASB-06).
    """
    lifetimes = dict(lifetimes_yr or SPECIES_LIFETIME_YR)
    truth = dict(true_sources or CH4_SOURCE_WITH_SCA_TG_YR)
    rows = []
    for sp, tau in sorted(lifetimes.items(), key=lambda kv: kv[1]):
        m = FourBoxModel(lifetime_yr=tau, exchange_yr=exchange_yr)
        d = synthetic_ch4_demo(m, truth)
        rows.append({"species": sp, "lifetime_yr": tau,
                     "A_TS": d["A_TS"], "A_tropics": d["A_tropics"],
                     "A_global": d["A_global"],
                     "deviation": 1.0 - d["A_TS"],
                     "deviation_global": 1.0 - d["A_global"]})
    devs = [r["deviation"] for r in rows]   # sorted short -> long lifetime
    gdevs = [r["deviation_global"] for r in rows]
    monotone = all(devs[i] >= devs[i + 1] for i in range(len(devs) - 1))
    monotone_global = all(gdevs[i] >= gdevs[i + 1] - 1e-12
                          for i in range(len(gdevs) - 1))
    # Geometric floor: the per-box deviation that survives as lifetime
    # -> infinity. Set by interpolation alone, not by the operator.
    floor = rows[-1]["deviation"] if rows else None
    return {
        "ranking_short_to_long": rows,
        "monotone": monotone,
        "monotone_global": monotone_global,
        "geometric_floor_deviation": floor,
        "calibration_point": {"CH4": CH4_MEASURED_A},
        "falsifier": "a long-lived species showing larger A-deviation than a "
                     "short-lived one, same geometry",
        "note": "Per-box A saturates at a geometric floor for tau >> exchange "
                "time: interpolation misattributes source between boxes at "
                "any lifetime. The GLOBAL total is what lifetime governs: "
                "A_global -> 1 for long-lived species (CO2, N2O), < 1 for "
                "CH4, far below 1 for CO. ASB-06 as written is a claim about "
                "the total; the attribution error has no lifetime floor. "
                "CO has no polar-derived at-source constraint; the predicted "
                "A for CO is the size of the error in any polar-derived "
                "tropical CO history.",
    }


# =====================================================================
# T-2  ENSO A BY FREQUENCY BAND  (closes ASB-08)
# =====================================================================


def enso_band_attenuation(variance_retained_in_band: Optional[float] = None,
                          variance_retained_low_freq: Optional[float] = None
                          ) -> Dict[str, object]:
    """Convert published pseudoproxy variance-retention figures into A per
    band. Amplitude A = sqrt(variance ratio). Values are not hard-coded:
    the marker records the sign, not the number. Pass the figures from
    the pseudoproxy study being tested.
    """
    def a_from_var(v):
        return None if v is None else math.sqrt(v)
    a_band = a_from_var(variance_retained_in_band)
    a_low = a_from_var(variance_retained_low_freq)
    out = {
        "A_enso_band": a_band,
        "A_low_frequency": a_low,
        "predicted": {"enso_band": "A < 1", "low_frequency": "A >= 1"},
        "sign_frequency_dependent": None,
        "falsifier": "ENSO variance loss uniform across all frequency bands",
    }
    if a_band is not None and a_low is not None:
        out["sign_frequency_dependent"] = (bias_direction(a_band)
                                          != bias_direction(a_low))
    return out


# =====================================================================
# T-4  NETWORK GEOMETRY  (closes ASB-01, ASB-02)
# Correlate proxy-network spatial density against the source-strength
# map. Negative correlation predicts the bias sign directly.
# =====================================================================


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    """Pearson correlation on equal-length sequences. Returns 0 for a
    degenerate (zero-variance) input."""
    n = len(x)
    if n != len(y) or n < 2:
        raise ValueError("need two equal-length sequences of length >= 2")
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return 0.0
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sxx * syy)


def network_geometry(proxy_density: Sequence[float],
                     source_strength: Sequence[float],
                     tol: float = 0.1) -> Dict[str, object]:
    """Per-cell proxy density vs per-cell source strength on the same grid.

    corr < -tol : archive anti-correlates with source -> predicted under-read
    corr > +tol : archive co-locates with source     -> predicted over-read
                  is NOT implied; the reconstruction is at-source, A ~ 1
    |corr| <= tol : no siting bias predicted from geometry alone
    """
    r = pearson(proxy_density, source_strength)
    if r < -tol:
        sign, word = -1, "UNDER_READ"
    elif r > tol:
        sign, word = 0, "AT_SOURCE"
    else:
        sign, word = 0, "NO_SITING_BIAS_FROM_GEOMETRY"
    return {
        "correlation": r,
        "predicted_bias_sign": sign,
        "predicted": word,
        "falsifier": "a proxy class whose preservation conditions are "
                     "independent of climate/chemistry (ASB-01), or an "
                     "anti-correlated physical case that OVER-reads (ASB-02)",
    }


# =====================================================================
# OPERATOR CLASS -> CORRECTABILITY  (HANDOFF item 4: decision procedure
# with a measurable stationarity criterion, closes ASB-07)
#
#   PHYSICAL   + STATIONARY      A is a CONSTANT      correct a priori
#   PHYSICAL   + NON-STATIONARY  A(t), drift known    correct per era
#   STATISTICAL+ STATIONARY      calibration holds    correct by calibration
#   STATISTICAL+ NON-STATIONARY  A is a RANDOM VAR    bound only
#   ROUTING_RULE                 -> statistical, drift with practice
# =====================================================================

OPERATOR_KINDS = ("physical", "statistical", "routing_rule")

CORRECTABILITY = {
    ("physical", True): "CORRECTABLE_A_PRIORI",
    ("physical", False): "CORRECTABLE_PER_ERA",
    ("statistical", True): "CORRECTABLE_BY_CALIBRATION",
    ("statistical", False): "BOUNDABLE_ONLY",
}

# Stationarity criterion: the operator's parameter drift across eras,
# as max |p - mean| / |mean|, must sit inside the perturbation envelope
# the reconstruction already quantifies. Default 0.30 = the +/-30 %
# perturbation the CH4 box model carried. Drift inside the envelope is
# already paid for; drift outside it is a new variable.
DEFAULT_DRIFT_ENVELOPE = 0.30


def stationarity_index(parameter_history: Sequence[float]) -> float:
    """max |p_i - mean| / |mean| over eras. 0 = perfectly stationary."""
    vals = [float(v) for v in parameter_history]
    if not vals:
        raise ValueError("empty parameter history")
    mean = sum(vals) / len(vals)
    if mean == 0:
        return float("inf")
    return max(abs(v - mean) for v in vals) / abs(mean)


def classify_operator(kind: str,
                      parameter_history: Optional[Sequence[float]] = None,
                      drift_envelope: float = DEFAULT_DRIFT_ENVELOPE
                      ) -> Dict[str, object]:
    """Decision procedure. Not a judgement call.

    kind               : 'physical' | 'statistical' | 'routing_rule'
    parameter_history  : the operator's key parameter across eras
                         (CH4: lifetime or exchange rate; ENSO:
                         teleconnection regression slope per window).
                         None -> for physical, assumed stationary
                         (fixed constants); for statistical or routing
                         rule, assumed NON-stationary (no evidence of
                         stability means none is claimed).
    drift_envelope     : stationarity threshold on stationarity_index
    """
    if kind not in OPERATOR_KINDS:
        raise ValueError(f"kind must be one of {OPERATOR_KINDS}")
    family = "statistical" if kind == "routing_rule" else kind
    if parameter_history is None:
        s_idx = None
        stationary = (family == "physical")
        basis = ("fixed constants assumed" if stationary
                 else "no parameter history supplied; drift assumed")
    else:
        s_idx = stationarity_index(parameter_history)
        stationary = s_idx <= drift_envelope
        basis = f"stationarity_index {s_idx:.3f} vs envelope {drift_envelope}"
    corr = CORRECTABILITY[(family, stationary)]
    return {
        "kind": kind,
        "family": family,
        "stationary": stationary,
        "stationarity_index": s_idx,
        "drift_envelope": drift_envelope,
        "basis": basis,
        "correctability": corr,
        "A_is": ("CONSTANT" if corr == "CORRECTABLE_A_PRIORI"
                 else "FUNCTION_OF_ERA" if corr == "CORRECTABLE_PER_ERA"
                 else "CALIBRATED_CONSTANT" if corr == "CORRECTABLE_BY_CALIBRATION"
                 else "RANDOM_VARIABLE"),
        "falsifier": "an a priori correction that verifies against an "
                     "at-source record for a non-stationary operator "
                     "(refutes ASB-07)",
    }


# =====================================================================
# T-3  A PRIORI BOUND COVERAGE  (closes ASB-07)
# =====================================================================


def a_priori_bound(kind: str, lifetime_yr: float,
                   exchange_yr: float = DEFAULT_EXCHANGE_YR,
                   exchange_uncertainty: float = 0.3,
                   true_sources: Optional[Dict[str, float]] = None
                   ) -> Dict[str, object]:
    """Predicted A_TS interval from operator parameters BEFORE consulting
    the at-source record. Physical operators only; statistical operators
    return no bound (that is the claim).
    """
    if kind != "physical":
        return {"kind": kind, "bound": None,
                "reason": "no a priori bound for non-physical operators"}
    lo_x = exchange_yr * (1.0 - exchange_uncertainty)
    hi_x = exchange_yr * (1.0 + exchange_uncertainty)
    a_vals = []
    for x in (lo_x, exchange_yr, hi_x):
        d = synthetic_ch4_demo(FourBoxModel(lifetime_yr=lifetime_yr,
                                            exchange_yr=x), true_sources)
        a_vals.append(d["A_TS"])
    return {"kind": kind, "lifetime_yr": lifetime_yr,
            "bound": (min(a_vals), max(a_vals)), "central": a_vals[1]}


def bound_coverage(bound: Optional[Sequence[float]], measured_A: float
                   ) -> Dict[str, object]:
    """Did the later measurement fall inside the a priori bound?"""
    if bound is None:
        return {"covered": None, "reason": "no bound to test"}
    lo, hi = bound
    return {"covered": lo <= measured_A <= hi, "bound": (lo, hi),
            "measured_A": measured_A}


# =====================================================================
# SIBLING ARCHIVES — untested, same predicted shape
# =====================================================================

SIBLING_ARCHIVES = [
    {"archive": "ice cores", "preservation_condition": "cold, dry, high accumulation",
     "under_sampled_host": "low latitude, low altitude",
     "predicted_bias_sign": -1, "status": "CALIBRATED (CH4, this file)"},
    {"archive": "corals", "preservation_condition": "reef-forming water",
     "under_sampled_host": "outside reef range",
     "predicted_bias_sign": -1, "status": "untested"},
    {"archive": "tree rings", "preservation_condition": "seasonally limiting growth",
     "under_sampled_host": "wet tropics",
     "predicted_bias_sign": -1, "status": "untested"},
    {"archive": "speleothems", "preservation_condition": "carbonate terrain",
     "under_sampled_host": "non-carbonate",
     "predicted_bias_sign": -1, "status": "untested"},
    {"archive": "sediment cores", "preservation_condition": "anoxic basin",
     "under_sampled_host": "productive oxic zone",
     "predicted_bias_sign": -1, "status": "untested"},
    {"archive": "fossils", "preservation_condition": "rapid burial",
     "under_sampled_host": "upland habitat",
     "predicted_bias_sign": -1, "status": "untested"},
    {"archive": "documents", "preservation_condition": "dry storage, stable institutions",
     "under_sampled_host": "humid, non-literate, mobile",
     "predicted_bias_sign": -1, "status": "untested; routing-rule operator (ASB-09)"},
]

# =====================================================================
# CLAIM TABLE  — refutation protocol: update the claim, never retune
# =====================================================================

CLAIM_TABLE = [
    {"id": "ASB-01",
     "claim": "Archive location for preserved-medium proxies is set by "
              "preservation conditions, not source location",
     "refuted_by": "a proxy class whose preservation conditions are "
                   "independent of climate/chemistry",
     "status": "MARKER", "test": "T-4"},
    {"id": "ASB-02",
     "claim": "Where the two anti-correlate, remote reconstruction under-reads "
              "source strength; sign known a priori",
     "refuted_by": "a case with anti-correlated siting where the remote "
                   "reconstruction OVER-read the source, physical operator",
     "status": "SUPPORTED (CH4, n=1)", "test": "T-4"},
    {"id": "ASB-03",
     "claim": "A < 1 for physical-transport operators",
     "refuted_by": "measured A >= 1 in a physical-transport case",
     "status": "SUPPORTED (CH4, n=1; four-box synthetic)", "test": "T-1"},
    {"id": "ASB-04",
     "claim": "CH4 A = 0.65 (TS box), 0.77 (combined tropics)",
     "refuted_by": "reanalysis of the Zenodo box model returning different ratios",
     "status": "MEASURED (published source strengths)", "test": "HANDOFF-1"},
    {"id": "ASB-05",
     "claim": "Siting bias can exceed the full quantified parameter "
              "uncertainty of the model carrying it",
     "refuted_by": "a case where the missing-box term is inside the "
                   "parameter envelope",
     "status": "SUPPORTED (CH4: 50 vs 17.5 Tg/yr)", "test": "-"},
    {"id": "ASB-06",
     "claim": "Bias magnitude scales inversely with species atmospheric lifetime",
     "refuted_by": "a long-lived species showing larger A-deviation than a "
                   "short-lived one, same geometry",
     "status": "PREDICTED (four-box); unmeasured beyond CH4", "test": "T-1"},
    {"id": "ASB-07",
     "claim": "Correctability is set by operator class: physical+stationary "
              "correctable, statistical+non-stationary boundable only",
     "refuted_by": "an a priori correction that verifies against an "
                   "at-source record for a non-stationary operator",
     "status": "MARKER", "test": "T-3"},
    {"id": "ASB-08",
     "claim": "For statistical operators the bias sign is frequency dependent",
     "refuted_by": "ENSO variance loss found uniform across all frequency bands",
     "status": "MARKER (ENSO literature, sign only)", "test": "T-2"},
    {"id": "ASB-09",
     "claim": "The axis extends to non-geophysical archives whose "
              "event->record transport is a routing rule",
     "refuted_by": "a routing-rule archive whose bias proves correctable a priori",
     "status": "MARKER", "test": "-"},
]

TESTS = {
    "T-1": {"closes": ["ASB-06"], "function": "lifetime_scaling",
            "prediction": "shorter lifetime -> larger deviation of A from 1"},
    "T-2": {"closes": ["ASB-08"], "function": "enso_band_attenuation",
            "prediction": "A < 1 in ENSO band, A >= 1 at low frequency"},
    "T-3": {"closes": ["ASB-07"], "function": "a_priori_bound + bound_coverage",
            "prediction": "physical cases hit the bound; statistical miss >= 1 band"},
    "T-4": {"closes": ["ASB-01", "ASB-02"], "function": "network_geometry",
            "prediction": "negative density/source correlation -> under-read"},
}

HANDOFF = [
    "1. Re-run the Zenodo box model with TS SOLVED under an SCA soft prior "
    "(soft_prior_sweep on the real data). Not done: zenodo.org unreachable "
    "from the drafting session.",
    "2. Run T-1 across the species list; the CO cell has no at-source "
    "constraint and the predicted A is the error size.",
    "3. Run T-4 on the PAGES-class proxy network against gridded source maps.",
    "4. classify_operator() is the decision procedure; the stationarity "
    "criterion is stationarity_index vs the model's own perturbation envelope.",
]


def claims_by_status(prefix: str) -> List[str]:
    return [c["id"] for c in CLAIM_TABLE if c["status"].startswith(prefix)]


# =====================================================================
# AUDIT — roll-up for one reconstructed quantity
# =====================================================================


def audit(remote_estimate: float, at_source_estimate: float,
          operator_kind: str,
          parameter_history: Optional[Sequence[float]] = None,
          proxy_density: Optional[Sequence[float]] = None,
          source_strength: Optional[Sequence[float]] = None
          ) -> Dict[str, object]:
    """One quantity, one read: A, direction, operator class, correctability,
    and (if a network map is given) the a priori sign from geometry, with
    the check of whether the geometry prediction matched the measured sign.
    """
    A = attenuation_factor(remote_estimate, at_source_estimate)
    d = bias_direction(A)
    op = classify_operator(operator_kind, parameter_history)
    out = {
        "A": A,
        "bias_direction": d,
        "read": {-1: "UNDER_READ", 0: "FAITHFUL", 1: "OVER_READ"}[d],
        "operator": op,
        "correctability": op["correctability"],
        "claims_touched": ["ASB-02", "ASB-03"] if operator_kind == "physical"
                          else ["ASB-07", "ASB-08"],
        "falsifier": "at-source record contradicting the sign predicted "
                     "from geometry and operator class",
    }
    if proxy_density is not None and source_strength is not None:
        g = network_geometry(proxy_density, source_strength)
        out["geometry"] = g
        out["geometry_sign_matched"] = (g["predicted_bias_sign"] == d
                                        if g["predicted_bias_sign"] != 0
                                        else None)
        if operator_kind == "physical" and g["predicted_bias_sign"] == -1 and d == +1:
            out["refutes"] = "ASB-02"
    return out


# =====================================================================
# REPORT
# =====================================================================


def _fmt_row(cells, widths):
    return "  ".join(str(c).ljust(w) for c, w in zip(cells, widths))


def report() -> str:
    lines = []
    A = ch4_attenuation()
    loc = ch4_error_localization()
    env = siting_bias_vs_envelope()
    lines.append("ARCHIVE SITING BIAS — MARKER (computable half)")
    lines.append("=" * 62)
    lines.append("CALIBRATION 1  CH4, physical transport (Lamantia 2026)")
    lines.append(_fmt_row(("box", "polar-only", "+SCA", "delta", "frac"),
                          (8, 10, 8, 8, 8)))
    for b in CH4_BOXES:
        lines.append(_fmt_row((b, CH4_SOURCE_POLAR_ONLY_TG_YR[b],
                               CH4_SOURCE_WITH_SCA_TG_YR[b],
                               f"{loc['delta_tg_yr'][b]:+.0f}",
                               f"{loc['delta_frac'][b]:+.0%}"),
                              (8, 10, 8, 8, 8)))
    lines.append(f"share of delta in unmeasured box (TS): "
                 f"{loc['share_in_unmeasured_box']:.0%}")
    lines.append(f"A_TS = {A['TS']:.2f}   A_tropics = {A['tropics']:.2f}"
                 f"   A_TN = {A['TN']:.2f}")
    lines.append(f"offset/gradient (WAIS 94 / IPD 48) = "
                 f"{offset_vs_gradient_ratio():.2f}")
    lines.append(f"missing-box term {env['missing_box_term']:.0f} vs envelope "
                 f"max {env['envelope_max']:.1f} Tg/yr -> "
                 f"exceeds = {env['exceeds_envelope']}")
    lines.append("")
    demo = synthetic_ch4_demo()
    lines.append("FOUR-BOX SYNTHETIC (independent, not the Zenodo code)")
    lines.append(f"  tau={CH4_LIFETIME_YR} yr, exchange={DEFAULT_EXCHANGE_YR} yr")
    lines.append("  conc ppb: " + ", ".join(
        f"{b} {demo['concentrations_ppb'][b]:.0f}" for b in CH4_BOXES))
    lines.append("  polar-only sources: " + ", ".join(
        f"{b} {demo['remote_sources_tg_yr'][b]:.0f}" for b in CH4_BOXES))
    lines.append(f"  A_TS = {demo['A_TS']:.2f}   A_tropics = {demo['A_tropics']:.2f}"
                 f"   A_global = {demo['A_global']:.2f}")
    lines.append("  soft-prior sweep  w: A_TS (TN interpolated | TN observed)")
    for r0, r1 in zip(soft_prior_sweep(), soft_prior_sweep(tn_observed=True)):
        lines.append(f"    {r0['weight']:.2f}: {r0['A_TS']:.2f} | {r1['A_TS']:.2f}")
    lines.append("")
    ls = lifetime_scaling()
    lines.append("T-1 LIFETIME SCALING (same geometry)")
    for r in ls["ranking_short_to_long"]:
        lines.append(f"  {r['species']:<4} tau={r['lifetime_yr']:>8.2f} yr  "
                     f"A_TS={r['A_TS']:.2f}  A_trop={r['A_tropics']:.2f}"
                     f"  A_global={r['A_global']:.2f}")
    lines.append(f"  monotone per-box = {ls['monotone']}   "
                 f"monotone global = {ls['monotone_global']}   "
                 f"geometric floor = {ls['geometric_floor_deviation']:.2f}")
    lines.append(f"  CH4 measured A_TS {CH4_MEASURED_A['TS']}")
    lines.append("")
    lines.append("OPERATOR CLASS -> CORRECTABILITY")
    for kind, hist in (("physical", None), ("physical", [9.1, 8.0, 12.5]),
                       ("statistical", [0.5, 0.52, 0.48]),
                       ("statistical", [0.5, 0.2, 0.8]),
                       ("routing_rule", None)):
        c = classify_operator(kind, hist)
        lines.append(f"  {kind:<12} hist={str(hist):<18} -> {c['correctability']}")
    lines.append("")
    lines.append("CLAIM TABLE")
    for c in CLAIM_TABLE:
        lines.append(f"  {c['id']}  {c['status']:<44} test {c['test']}")
    lines.append("")
    lines.append("HANDOFF")
    for h in HANDOFF:
        lines.append("  " + h)
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
