# global_temperature_august_2026.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Observed state of the global surface, August 2026: the warmest
# August in every major record, and — in ERA5 — the joint warmest
# month ever measured.
#
# SOURCES (all published 9-12 September 2026)
# -------------------------------------------
# C3S/ECMWF   Copernicus Climate Change Service monthly bulletin,
#             ERA5 reanalysis. Absolute temperature, anomalies against
#             1991-2020 and 1850-1900, 12-month running mean, boreal
#             summer, extra-polar SST, Europe.
# NOAA NCEI   "Monitoring Global Temperature and Precipitation in
#             August 2026", NOAAGlobalTemp, 1850-2026 record.
# NASA GISS   Warmest August (as reported by WMO; GISTEMP).
# WMO         "Earth has hottest August on record" — cites all three.
# NSIDC       Arctic and Antarctic August sea-ice extents and ranks.
# NOAA CPC    ENSO Diagnostic Discussion, September 2026; weekly
#             Nino 3.4.
# Berkeley Earth  July 2026 Temperature Update (13 Aug 2026), used
#             for the year-to-date odds and the daily Nino 3.4 figure.
#
# Two earlier C3S bulletins supply the comparison points and are
# marked as such in PROVENANCE: July 2023 (the month August 2026
# tied) and August 2024 (the previous August record and the previous
# 12-month running mean).
#
# WHAT THIS MODULE IS
# -------------------
# A monthly observed-state snapshot in the style of
# state_of_the_climate_2025.py, with provenance per constant. It
# exists because the 2025 report closed on one structural finding —
# a top-three year with NO El Nino — and August 2026 supplies the
# other half of that superposition: the same rising baseline with a
# strong El Nino on top of it. The two together let the ENSO
# modulation be MEASURED against the baseline rather than asserted.
#
# It also computes the quantities the bulletins imply but do not
# tabulate: the seasonal-cycle offset hidden inside an "absolute
# record", the dataset-dependence of record margins, the swing of
# the 12-month running mean through one ENSO cycle, and the realised
# global-temperature sensitivity to Nino 3.4 so far in this event.
#
# Nothing here is a projection. One function reports a documented
# PATTERN (the year after an El Nino onset has been the record year)
# and labels it as a pattern, not a forecast.
#
# Standard library only.

from typing import Dict, List, Optional, Tuple

from state_of_the_climate_2025 import (
    GLOBAL_TEMP_RANK_2025,
    ENSO_STATE_2025,
    WARMEST_YEAR_WITHOUT_EL_NINO,
    enso_decoupling_check,
)

# ─────────────────────────────────────────────
# METADATA
# ─────────────────────────────────────────────

DATA_YEAR = 2026
DATA_MONTH = 8
BULLETIN_PUBLISHED = (2026, 9, 10)          # C3S and NOAA within a day
DATASETS_RANKING_WARMEST_AUGUST = ("ERA5 (C3S)", "NOAAGlobalTemp", "GISTEMP")


# ─────────────────────────────────────────────
# ERA5 — SURFACE AIR TEMPERATURE
# ─────────────────────────────────────────────

# August 2026
AUG_2026_SAT_C = 16.96                      # global mean, absolute
AUG_2026_ANOM_1991_2020_C = 0.85
AUG_2026_ANOM_PREINDUSTRIAL_C = 1.65        # vs 1850-1900

# The month it tied: July 2023 (C3S July 2023 bulletin). Absolute
# temperatures differ by less than 0.01 C, which C3S reports as a tie.
JUL_2023_SAT_C = 16.95
JUL_2023_ANOM_1991_2020_C = 0.72
TIE_TOLERANCE_C = 0.01

# The previous August record, held jointly by 2023 and 2024
# (C3S August 2024 bulletin).
AUG_2023_2024_SAT_C = 16.82
AUG_2023_2024_ANOM_1991_2020_C = 0.71

# 12-month running means against 1850-1900
RUNNING_12MO_SEP2025_AUG2026_C = 1.48       # this bulletin
RUNNING_12MO_SEP2023_AUG2024_C = 1.64       # C3S August 2024 bulletin
FIRST_MONTH_ABOVE_1P5_SINCE = (2025, 11)    # Nov 2025 was the last one

# Boreal summer (June-August), anomaly vs 1991-2020
JJA_2026_ANOM_C = 0.69                      # joint warmest with 2024
JJA_2024_ANOM_C = 0.69
JJA_2023_ANOM_C = 0.66

WESTERN_EUROPE_WARMEST_SUMMER = True        # surpasses 2003
WESTERN_EUROPE_PREVIOUS_RECORD_SUMMER = 2003

# Paris Agreement metric: a 20-year mean, not a month or a year.
PARIS_THRESHOLD_C = 1.5
PARIS_AVERAGING_YEARS = 20

# Multi-decadal warming rate used ONLY to separate trend from ENSO in
# the running-mean swing below. ~0.2 C/decade is the round number
# every major dataset returns for the last 30-40 years; it is not a
# result of this module and is flagged approximate in PROVENANCE.
TREND_C_PER_YR_APPROX = 0.020


# ─────────────────────────────────────────────
# ERA5 — EXTRA-POLAR SEA SURFACE TEMPERATURE (60S-60N)
# ─────────────────────────────────────────────

SST_EXTRAPOLAR_AUG_2026_C = 21.07           # monthly mean, record for August
SST_EXTRAPOLAR_PREV_AUG_RECORD_C = 20.98    # August 2023
SST_EXTRAPOLAR_DAILY_RECORD_C = 21.10       # all-time daily
SST_EXTRAPOLAR_DAILY_RECORD_DATE = (2026, 8, 22)
SST_EXTRAPOLAR_PREV_DAILY_RECORD_C = 21.09  # March 2024
SST_EXTRAPOLAR_PREV_DAILY_RECORD_MONTH = (2024, 3)
# The climatological maximum of extra-polar SST falls in March-April.
# An all-time daily record in late August is therefore set against
# the seasonal cycle, not with it.
SST_SEASONAL_MAX_MONTHS = (3, 4)


# ─────────────────────────────────────────────
# NOAA NCEI — NOAAGlobalTemp
# ─────────────────────────────────────────────

NOAA_AUG_2026_ANOM_20TH_CENTURY_C = 1.32    # 2.38 F
NOAA_AUG_2026_ANOM_20TH_CENTURY_F = 2.38
NOAA_RECORD_START = 1850
NOAA_MARGIN_OVER_2023_2024_C = 0.08         # 0.14 F
NOAA_RECORD_WARM_SURFACE_FRACTION = 0.132   # 13.2% of land+ocean area
NOAA_RECORD_WARM_AREA_RANK_ANY_MONTH = 3    # since 1951
NOAA_ALL_TEN_WARMEST_AUGUSTS_SINCE = 2016
NOAA_OCEAN_AUG_2026_RECORD = True
NOAA_LAND_AUG_2026_RANK_NOTE = "near-record warm"
NOAA_WARMEST_AUGUST_CONTINENTS = ("North America", "Africa")
NOAA_ASIA_AUG_2026_RANK = 2


# ─────────────────────────────────────────────
# NSIDC — SEA ICE, AUGUST 2026 MONTHLY MEANS
# ─────────────────────────────────────────────

ARCTIC_ICE_AUG_2026_MKM2 = 5.56
ARCTIC_ICE_AUG_2026_RANK_LOWEST = 7
ARCTIC_ICE_AUG_2026_ABOVE_2012_MKM2 = 0.84
ANTARCTIC_ICE_AUG_2026_MKM2 = 16.46
ANTARCTIC_ICE_AUG_2026_RANK_LOWEST = 3


# ─────────────────────────────────────────────
# ENSO — THE EVENT UNDER THE RECORD
# ─────────────────────────────────────────────

ENSO_STATE_AUG_2026 = "el_nino_strong_strengthening"
CPC_ADVISORY_IN_EFFECT = True
NINO34_WEEKLY_AUG_2026_C = 2.7              # week centred 12 Aug 2026
NINO34_RELATIVE_WEEK_ENDING_30_AUG_C = 2.45 # relative index (tropics-detrended)
CPC_P_VERY_STRONG_WINTER_2026_27 = 0.90     # "greater than 90%"
NINO34_FORECAST_PEAK_C = 3.6                # consensus plume, mid-2026
NINO34_PREVIOUS_RECORD_C = 2.75             # 2015-16 (1877-78: 2.73)

# Berkeley Earth, July 2026 update
BERKELEY_JUL_2026_ANOM_C = 1.56
BERKELEY_JUL_2026_UNCERTAINTY_C = 0.09
BERKELEY_JUL_2026_RANK = 2
BERKELEY_P_2026_WARMEST_YEAR = 0.69


# ─────────────────────────────────────────────
# DERIVED — WHAT THE BULLETINS IMPLY BUT DO NOT TABULATE
# ─────────────────────────────────────────────


def climatology_1991_2020_C(absolute_C: float, anomaly_C: float) -> float:
    """Back out the 1991-2020 calendar-month climatology from an
    absolute temperature and its anomaly (both in C)."""
    return absolute_C - anomaly_C


def absolute_vs_anomaly_tie() -> Dict[str, object]:
    """
    ERA5 calls August 2026 the JOINT warmest month with July 2023 —
    in absolute temperature. But July is the warmest calendar month
    of the global mean (Northern Hemisphere land dominates the
    seasonal cycle), so an August that matches a July in absolute
    terms has beaten it in anomaly terms by the seasonal offset.

    Returns both climatologies, the offset between them, and the
    anomaly by which August 2026 exceeds July 2023.
    """
    aug_clim = climatology_1991_2020_C(AUG_2026_SAT_C, AUG_2026_ANOM_1991_2020_C)
    jul_clim = climatology_1991_2020_C(JUL_2023_SAT_C, JUL_2023_ANOM_1991_2020_C)
    return {
        "aug_2026_absolute_C":        AUG_2026_SAT_C,
        "jul_2023_absolute_C":        JUL_2023_SAT_C,
        "absolute_difference_C":      round(AUG_2026_SAT_C - JUL_2023_SAT_C, 3),
        "tie_in_absolute_terms":      round(abs(AUG_2026_SAT_C - JUL_2023_SAT_C), 3)
                                      <= TIE_TOLERANCE_C,
        "aug_climatology_C":          round(aug_clim, 2),
        "jul_climatology_C":          round(jul_clim, 2),
        "seasonal_offset_C":          round(jul_clim - aug_clim, 2),
        "anomaly_excess_over_jul_2023_C":
            round(AUG_2026_ANOM_1991_2020_C - JUL_2023_ANOM_1991_2020_C, 2),
        "largest_anomaly_on_record":  AUG_2026_ANOM_1991_2020_C
                                      > JUL_2023_ANOM_1991_2020_C,
        "implication": (
            "An 'absolute record tie' understates the anomaly record by "
            "the seasonal-cycle offset. Compare anomalies, not absolutes, "
            "across calendar months."
        ),
    }


def record_margins() -> Dict[str, object]:
    """
    How far August 2026 beat the previous August record, by dataset.

    ERA5 (full-coverage reanalysis, 1991-2020 anomalies) and
    NOAAGlobalTemp (station + SST analysis, 20th-century anomalies)
    agree on the rank and disagree on the margin by nearly a factor
    of two. The margin of a record is a dataset property at the
    0.05 C level; the rank is not.
    """
    era5_margin = AUG_2026_ANOM_1991_2020_C - AUG_2023_2024_ANOM_1991_2020_C
    return {
        "era5_margin_C":     round(era5_margin, 2),
        "noaa_margin_C":     NOAA_MARGIN_OVER_2023_2024_C,
        "ratio_era5_to_noaa": round(era5_margin / NOAA_MARGIN_OVER_2023_2024_C, 2),
        "spread_C":          round(era5_margin - NOAA_MARGIN_OVER_2023_2024_C, 2),
        "rank_agrees":       True,
        "implication": (
            "State the dataset with any record margin. Rank is robust "
            "across ERA5, NOAA and GISTEMP; the size of the margin is not."
        ),
    }


def running_mean_modulation(trend_C_per_yr: float = TREND_C_PER_YR_APPROX
                            ) -> Dict[str, float]:
    """
    Swing of the 12-month running mean through one ENSO cycle.

    Sep 2023-Aug 2024 (post-El Nino) : 1.64 C above 1850-1900
    Sep 2025-Aug 2026 (post-La Nina/neutral, El Nino onset) : 1.48 C

    Two years of trend should have ADDED ~0.04 C. The mean instead
    fell 0.16 C, so the ENSO-attributable swing of the 12-month mean
    is ~0.20 C peak-to-trough. That is the modulation amplitude the
    2025 report's structural finding left unmeasured.
    """
    years = 2.0
    observed_change = RUNNING_12MO_SEP2025_AUG2026_C - RUNNING_12MO_SEP2023_AUG2024_C
    trend_contribution = trend_C_per_yr * years
    enso_swing = trend_contribution - observed_change
    return {
        "mean_sep2023_aug2024_C":  RUNNING_12MO_SEP2023_AUG2024_C,
        "mean_sep2025_aug2026_C":  RUNNING_12MO_SEP2025_AUG2026_C,
        "observed_change_C":       round(observed_change, 2),
        "trend_contribution_C":    round(trend_contribution, 2),
        "enso_swing_C":            round(enso_swing, 2),
        "swing_over_trend_years":  round(enso_swing / trend_C_per_yr, 1),
    }


def enso_superposition_check() -> Dict[str, object]:
    """
    Both halves of the superposition, now observed.

    2025      : ENSO neutral to La Nina-like -> top-three year
                (state_of_the_climate_2025.enso_decoupling_check)
    Aug 2026  : strong El Nino, Nino 3.4 ~ +2.7 -> record month,
                1.65 C above pre-industrial against a 1.48 C 12-month
                mean.

    The monthly excess over the running mean (0.17 C) at a Nino 3.4
    of +2.7 C gives a REALISED sensitivity of ~0.06 C per C of
    Nino 3.4. The global response lags Nino 3.4 by roughly a season
    and the event is still strengthening, so this is a lower bound,
    not the coefficient.
    """
    prior = enso_decoupling_check()
    excess = AUG_2026_ANOM_PREINDUSTRIAL_C - RUNNING_12MO_SEP2025_AUG2026_C
    return {
        "neutral_year_2025": {
            "rank":          GLOBAL_TEMP_RANK_2025,
            "enso_state":    ENSO_STATE_2025,
            "record_without_el_nino": WARMEST_YEAR_WITHOUT_EL_NINO,
        },
        "el_nino_month_2026": {
            "anomaly_preindustrial_C": AUG_2026_ANOM_PREINDUSTRIAL_C,
            "running_12mo_C":          RUNNING_12MO_SEP2025_AUG2026_C,
            "monthly_excess_C":        round(excess, 2),
            "nino34_C":                NINO34_WEEKLY_AUG_2026_C,
            "enso_state":              ENSO_STATE_AUG_2026,
        },
        "realised_sensitivity_C_per_C_nino34":
            round(excess / NINO34_WEEKLY_AUG_2026_C, 3),
        "sensitivity_is_lower_bound": True,
        "record_requires_el_nino":    not prior["record_without_el_nino"],
        "enso_still_modulates":       excess > 0,
        "implication": (
            "ENSO neither makes nor is needed for records: a neutral year "
            "ranks top-three on the baseline alone, and a strong El Nino "
            "adds ~0.2 C on top of it. Attribute the LEVEL to the "
            "baseline and the EXCURSION to ENSO; never the reverse."
        ),
    }


def paris_threshold_status() -> Dict[str, object]:
    """
    Where 1.5 C stands on each averaging window.

    A month above 1.5 C is not a crossing; a 12-month mean above it
    is not a crossing either (Sep 2023-Aug 2024 was 1.64 and then
    fell back). The Paris metric is a 20-year mean.
    """
    return {
        "threshold_C":              PARIS_THRESHOLD_C,
        "monthly_aug_2026_C":       AUG_2026_ANOM_PREINDUSTRIAL_C,
        "monthly_above":            AUG_2026_ANOM_PREINDUSTRIAL_C > PARIS_THRESHOLD_C,
        "running_12mo_C":           RUNNING_12MO_SEP2025_AUG2026_C,
        "running_12mo_above":       RUNNING_12MO_SEP2025_AUG2026_C > PARIS_THRESHOLD_C,
        "running_12mo_shortfall_C": round(PARIS_THRESHOLD_C
                                          - RUNNING_12MO_SEP2025_AUG2026_C, 2),
        "prior_12mo_peak_C":        RUNNING_12MO_SEP2023_AUG2024_C,
        "prior_12mo_peak_above":    RUNNING_12MO_SEP2023_AUG2024_C > PARIS_THRESHOLD_C,
        "defining_window_years":    PARIS_AVERAGING_YEARS,
        "crossing_established":     False,
        "first_month_above_since":  FIRST_MONTH_ABOVE_1P5_SINCE,
    }


def sst_record_against_season() -> Dict[str, object]:
    """
    Extra-polar SST set its all-time DAILY record on 22 August 2026,
    a month when the seasonal cycle sits well below its March-April
    maximum. The previous record was set in March 2024, at the
    seasonal peak. A record set off-peak means the anomaly against
    climatology is larger than the record-to-record difference shows.
    """
    return {
        "aug_2026_monthly_C":        SST_EXTRAPOLAR_AUG_2026_C,
        "prev_august_record_C":      SST_EXTRAPOLAR_PREV_AUG_RECORD_C,
        "august_margin_C":           round(SST_EXTRAPOLAR_AUG_2026_C
                                           - SST_EXTRAPOLAR_PREV_AUG_RECORD_C, 2),
        "daily_record_C":            SST_EXTRAPOLAR_DAILY_RECORD_C,
        "daily_record_date":         SST_EXTRAPOLAR_DAILY_RECORD_DATE,
        "prev_daily_record_C":       SST_EXTRAPOLAR_PREV_DAILY_RECORD_C,
        "prev_daily_record_month":   SST_EXTRAPOLAR_PREV_DAILY_RECORD_MONTH,
        "set_at_seasonal_peak":      SST_EXTRAPOLAR_DAILY_RECORD_DATE[1]
                                     in SST_SEASONAL_MAX_MONTHS,
        "anomaly_understated_by_absolute_comparison": True,
    }


def el_nino_following_year_pattern() -> Dict[str, object]:
    """
    A documented PATTERN, labelled as such. In each of the last three
    strong El Ninos the second calendar year of the event was the
    record year at the time:

        1997-98 -> 1998     2015-16 -> 2016     2023-24 -> 2024

    The 2026-27 event is forecast to peak above all of them. This
    function does not project 2027; it reports that the pattern
    exists and that 2026 already carries a 69% chance (Berkeley
    Earth, July) of being the record year on its own.
    """
    return {
        "kind": "pattern_not_projection",
        "onset_to_record_year": [
            {"event": "1997-98", "record_year": 1998},
            {"event": "2015-16", "record_year": 2016},
            {"event": "2023-24", "record_year": 2024},
        ],
        "current_event": "2026-27",
        "current_event_second_year": 2027,
        "p_2026_warmest_year_berkeley_july": BERKELEY_P_2026_WARMEST_YEAR,
        "forecast_peak_vs_previous_record_C":
            round(NINO34_FORECAST_PEAK_C - NINO34_PREVIOUS_RECORD_C, 2),
        "caveat": (
            "Three instances. The pattern is the lagged global response "
            "to Nino 3.4; it says nothing about magnitude in 2027."
        ),
    }


def sea_ice_state() -> Dict[str, object]:
    """Both poles for the month, as monthly-mean extents with ranks."""
    return {
        "arctic_mkm2":           ARCTIC_ICE_AUG_2026_MKM2,
        "arctic_rank_lowest":    ARCTIC_ICE_AUG_2026_RANK_LOWEST,
        "arctic_above_2012_mkm2": ARCTIC_ICE_AUG_2026_ABOVE_2012_MKM2,
        "antarctic_mkm2":        ANTARCTIC_ICE_AUG_2026_MKM2,
        "antarctic_rank_lowest": ANTARCTIC_ICE_AUG_2026_RANK_LOWEST,
        "note": (
            "Antarctic August extent is 3rd lowest — inside the post-2016 "
            "low state that 2023, 2024 and 2025 also occupied — as the "
            "next super El Nino arrives on top of it."
        ),
    }


# ─────────────────────────────────────────────
# PROVENANCE
# ─────────────────────────────────────────────

PROVENANCE: Dict[str, Dict[str, str]] = {
    "AUG_2026_SAT_C": {
        "value": "16.96 C global mean surface air temperature",
        "dataset": "ERA5",
        "source": "C3S monthly bulletin, August 2026 (pub. Sep 2026)",
    },
    "AUG_2026_ANOM_1991_2020_C": {
        "value": "+0.85 C vs 1991-2020; warmest August in ERA5",
        "dataset": "ERA5",
        "source": "C3S monthly bulletin, August 2026",
    },
    "AUG_2026_ANOM_PREINDUSTRIAL_C": {
        "value": "+1.65 C vs 1850-1900; first month above 1.5 C since "
                 "Nov 2025",
        "dataset": "ERA5",
        "source": "C3S monthly bulletin, August 2026",
    },
    "JUL_2023_SAT_C": {
        "value": "16.95 C, +0.72 C vs 1991-2020 — the month tied "
                 "(difference < 0.01 C)",
        "dataset": "ERA5",
        "source": "C3S monthly bulletin, July 2023 (comparison point)",
    },
    "AUG_2023_2024_SAT_C": {
        "value": "16.82 C, +0.71 C vs 1991-2020 — previous joint August "
                 "record",
        "dataset": "ERA5",
        "source": "C3S monthly bulletin, August 2024 (comparison point)",
    },
    "RUNNING_12MO_SEP2025_AUG2026_C": {
        "value": "1.48 C above 1850-1900, 12-month mean",
        "dataset": "ERA5",
        "source": "C3S monthly bulletin, August 2026",
    },
    "RUNNING_12MO_SEP2023_AUG2024_C": {
        "value": "1.64 C above 1850-1900, 12-month mean",
        "dataset": "ERA5",
        "source": "C3S monthly bulletin, August 2024 (comparison point)",
    },
    "JJA_2026_ANOM_C": {
        "value": "+0.69 C vs 1991-2020; joint warmest boreal summer with "
                 "2024 (0.69); 2023 was 0.66",
        "dataset": "ERA5",
        "source": "C3S monthly bulletin, August 2026",
    },
    "SST_EXTRAPOLAR_AUG_2026_C": {
        "value": "21.07 C monthly mean 60S-60N, record for August "
                 "(previous 20.98, Aug 2023); daily record 21.10 C on "
                 "22 Aug 2026 exceeding 21.09 C (Mar 2024)",
        "dataset": "ERA5",
        "source": "C3S monthly bulletin, August 2026",
    },
    "NOAA_AUG_2026_ANOM_20TH_CENTURY_C": {
        "value": "+1.32 C (2.38 F) vs 20th-century mean; warmest August "
                 "1850-2026; +0.08 C over the 2023/2024 tie",
        "dataset": "NOAAGlobalTemp",
        "source": "NOAA NCEI Global Climate Report, August 2026",
    },
    "NOAA_RECORD_WARM_SURFACE_FRACTION": {
        "value": "13.2% of land+ocean area record warm — largest August "
                 "extent, 3rd for any month since 1951",
        "dataset": "NOAAGlobalTemp",
        "source": "NOAA NCEI Global Climate Report, August 2026",
    },
    "ARCTIC_ICE_AUG_2026_MKM2": {
        "value": "5.56 million km2, 7th lowest August; 0.84 million km2 "
                 "above the 2012 record low",
        "dataset": "NSIDC Sea Ice Index",
        "source": "NSIDC, August 2026 analysis",
    },
    "ANTARCTIC_ICE_AUG_2026_MKM2": {
        "value": "16.46 million km2, 3rd lowest August",
        "dataset": "NSIDC Sea Ice Index",
        "source": "NSIDC, August 2026 analysis",
    },
    "NINO34_WEEKLY_AUG_2026_C": {
        "value": "+2.7 C weekly Nino 3.4 centred 12 Aug 2026; relative "
                 "Nino 3.4 +2.45 C week ending 30 Aug; El Nino Advisory; "
                 ">90% chance of a very strong event, NH winter 2026-27",
        "dataset": "OISST / CPC",
        "source": "NOAA CPC ENSO Diagnostic Discussion, Sep 2026; "
                  "Berkeley Earth July 2026 update",
    },
    "BERKELEY_P_2026_WARMEST_YEAR": {
        "value": "69% chance 2026 is the warmest year; July 2026 "
                 "1.56 +/- 0.09 C, 2nd warmest July",
        "dataset": "Berkeley Earth",
        "source": "Berkeley Earth July 2026 Temperature Update",
    },
    "TREND_C_PER_YR_APPROX": {
        "value": "0.020 C/yr — APPROXIMATE multi-decadal rate used only "
                 "to separate trend from ENSO in the running-mean swing",
        "dataset": "round number, all major datasets",
        "source": "not a measurement of this module",
    },
}


def provenance(name: str) -> Optional[Dict[str, str]]:
    """Source record for a constant, or None if not individually cited."""
    return PROVENANCE.get(name)


# ─────────────────────────────────────────────
# HAND-OFF TO THE CASCADE ENGINE
# ─────────────────────────────────────────────


def baseline_overrides() -> Dict[str, float]:
    """
    BASELINE keys this month's observations update.

    Only the ENSO anomaly: it is the one BASELINE variable that this
    bulletin measures directly and that the engine already carries
    (Layer 4 `enso_feedback_strength` reads `SST_enso`). Global
    surface temperature is NOT overridden — BASELINE's 288 K is a
    reference state, and the anomaly here is against 1850-1900, not
    against that reference.

        from cascade_engine import BASELINE
        from global_temperature_august_2026 import baseline_overrides
        p = dict(BASELINE); p.update(baseline_overrides())
    """
    return {"SST_enso": NINO34_WEEKLY_AUG_2026_C}


def records_broken() -> List[Dict[str, object]]:
    """Every quantity the September 2026 bulletins record as a high."""
    return [
        {"quantity": "August global surface air temperature",
         "kind": "record_high", "value": AUG_2026_ANOM_1991_2020_C,
         "units": "C vs 1991-2020", "dataset": "ERA5"},
        {"quantity": "any-month global surface air temperature (absolute)",
         "kind": "record_high_joint", "value": AUG_2026_SAT_C,
         "units": "C", "dataset": "ERA5"},
        {"quantity": "any-month anomaly vs 1991-2020",
         "kind": "record_high", "value": AUG_2026_ANOM_1991_2020_C,
         "units": "C", "dataset": "ERA5"},
        {"quantity": "August global temperature",
         "kind": "record_high", "value": NOAA_AUG_2026_ANOM_20TH_CENTURY_C,
         "units": "C vs 20th century", "dataset": "NOAAGlobalTemp"},
        {"quantity": "August global ocean temperature",
         "kind": "record_high", "value": None,
         "units": "", "dataset": "NOAAGlobalTemp"},
        {"quantity": "record-warm surface area, any August",
         "kind": "record_high", "value": NOAA_RECORD_WARM_SURFACE_FRACTION,
         "units": "fraction", "dataset": "NOAAGlobalTemp"},
        {"quantity": "extra-polar SST, August mean",
         "kind": "record_high", "value": SST_EXTRAPOLAR_AUG_2026_C,
         "units": "C", "dataset": "ERA5"},
        {"quantity": "extra-polar SST, daily all-time",
         "kind": "record_high", "value": SST_EXTRAPOLAR_DAILY_RECORD_C,
         "units": "C", "dataset": "ERA5"},
        {"quantity": "boreal summer JJA",
         "kind": "record_high_joint", "value": JJA_2026_ANOM_C,
         "units": "C vs 1991-2020", "dataset": "ERA5"},
        {"quantity": "western Europe summer",
         "kind": "record_high", "value": None,
         "units": "", "dataset": "ERA5"},
    ]


if __name__ == "__main__":
    print(f"GLOBAL SURFACE, AUGUST {DATA_YEAR}")
    print(f"warmest August in: {', '.join(DATASETS_RANKING_WARMEST_AUGUST)}")
    print("=" * 72)

    print("\nERA5")
    print(f"  absolute {AUG_2026_SAT_C:.2f} C  |  +{AUG_2026_ANOM_1991_2020_C:.2f} "
          f"vs 1991-2020  |  +{AUG_2026_ANOM_PREINDUSTRIAL_C:.2f} vs 1850-1900")
    t = absolute_vs_anomaly_tie()
    print(f"  ties July 2023 in absolute terms: {t['tie_in_absolute_terms']}; "
          f"anomaly larger by {t['anomaly_excess_over_jul_2023_C']:.2f} C "
          f"(seasonal offset {t['seasonal_offset_C']:.2f} C)")
    m = record_margins()
    print(f"  margin over previous August record: ERA5 {m['era5_margin_C']:.2f} C, "
          f"NOAA {m['noaa_margin_C']:.2f} C  (ratio {m['ratio_era5_to_noaa']})")

    print("\n1.5 C")
    p = paris_threshold_status()
    print(f"  month {p['monthly_aug_2026_C']:.2f}  |  12-month "
          f"{p['running_12mo_C']:.2f}  |  prior 12-month peak "
          f"{p['prior_12mo_peak_C']:.2f}  |  defining window "
          f"{p['defining_window_years']} yr  |  crossing established: "
          f"{p['crossing_established']}")
    r = running_mean_modulation()
    print(f"  12-month mean swing through one ENSO cycle: "
          f"{r['observed_change_C']:+.2f} C observed vs "
          f"{r['trend_contribution_C']:+.2f} C trend -> ENSO swing "
          f"~{r['enso_swing_C']:.2f} C = {r['swing_over_trend_years']:.0f} yr of trend")

    print("\nENSO SUPERPOSITION")
    e = enso_superposition_check()
    n, o = e["neutral_year_2025"], e["el_nino_month_2026"]
    print(f"  2025 : rank {n['rank']} with ENSO {n['enso_state']}")
    print(f"  2026 : Aug {o['anomaly_preindustrial_C']:.2f} C vs 12-mo "
          f"{o['running_12mo_C']:.2f} -> excess {o['monthly_excess_C']:.2f} C "
          f"at Nino 3.4 +{o['nino34_C']:.1f}")
    print(f"  realised sensitivity >= "
          f"{e['realised_sensitivity_C_per_C_nino34']:.3f} C per C Nino 3.4")
    print(f"  -> {e['implication']}")

    print("\nOCEAN")
    s = sst_record_against_season()
    print(f"  extra-polar SST {s['aug_2026_monthly_C']:.2f} C "
          f"(+{s['august_margin_C']:.2f} over Aug 2023); daily record "
          f"{s['daily_record_C']:.2f} C on "
          f"{'-'.join(str(x) for x in s['daily_record_date'])}, set at "
          f"seasonal peak: {s['set_at_seasonal_peak']}")

    print("\nSEA ICE (NSIDC, monthly mean)")
    i = sea_ice_state()
    print(f"  Arctic {i['arctic_mkm2']:.2f} Mkm2 ({i['arctic_rank_lowest']}th lowest)"
          f"  |  Antarctic {i['antarctic_mkm2']:.2f} Mkm2 "
          f"({i['antarctic_rank_lowest']}rd lowest)")

    print("\nPATTERN (not projection)")
    f = el_nino_following_year_pattern()
    for row in f["onset_to_record_year"]:
        print(f"  {row['event']} -> {row['record_year']}")
    print(f"  {f['current_event']} -> {f['current_event_second_year']} ?   "
          f"P(2026 warmest, Berkeley July) = {f['p_2026_warmest_year_berkeley_july']:.0%}")

    print("\nRECORDS")
    for rec in records_broken():
        print(f"  {rec['kind']:18s} {rec['quantity']}  [{rec['dataset']}]")

    print("\nBASELINE OVERRIDES FOR THE CASCADE ENGINE")
    for k, v in baseline_overrides().items():
        print(f"  {k:12s} {v}")
