# state_of_the_climate_2025.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Observed state of the climate system in calendar year 2025.
#
# SOURCE
# ------
# "State of the Climate in 2025", 36th annual report, published as a
# special supplement to the Bulletin of the American Meteorological
# Society (BAMS), August 2026. 625 scientists, 60 countries.
# Compiled by NOAA NCEI. Arctic figures cross-checked against the
# NOAA Arctic Report Card 2025.
#
# NOTE ON THE REPORT YEAR. The BAMS State of the Climate series is
# published the following August: the 36th annual report appeared in
# August 2026 and documents calendar year 2025. A summary dating this
# report to August 2025 has the publication year wrong by one — that
# would be the 35th report, covering 2024. Every value in this module
# is the 2025 data year.
#
# WHAT THIS MODULE IS
# -------------------
# An observed-state snapshot with provenance attached to each value, in
# the style of earth_systems_constraints_2026.py. It supplies measured
# numbers to the cascade engine's BASELINE and computes the quantities
# the report's own text implies but does not tabulate: radiative
# forcing from the measured mixing ratios, the sea-level budget
# closure, and the multi-year-ice loss fraction against both baselines.
#
# It is not a projection and contains no scenario. Every number is a
# measurement or is derived from one in a documented line of code.
#
# Standard library only.

import math
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────
# REPORT METADATA
# ─────────────────────────────────────────────

REPORT_EDITION = 36
REPORT_DATA_YEAR = 2025
REPORT_PUBLISHED_YEAR = 2026
REPORT_PUBLISHED_MONTH = 8
REPORT_TITLE = "State of the Climate in 2025"
REPORT_VENUE = "Bulletin of the American Meteorological Society (BAMS), supplement"
REPORT_CONTRIBUTORS = 625
REPORT_COUNTRIES = 60


# ─────────────────────────────────────────────
# GREENHOUSE GASES — ALL THREE AT RECORD HIGHS
# ─────────────────────────────────────────────

CO2_PPM_2025 = 425.6                  # ppm, globally averaged
CO2_PPM_UNCERTAINTY = 0.1
CO2_PCT_ABOVE_PREINDUSTRIAL = 53.0

CH4_PPB_2025 = 1935.7                 # ppb
CH4_PCT_ABOVE_PREINDUSTRIAL = 166.0

N2O_PPB_2025 = 338.9                  # ppb
N2O_PCT_ABOVE_PREINDUSTRIAL = 26.0

# Pre-industrial references. The report states CO2 as ~278 ppm and gives
# percentage increases for all three. The CH4 and N2O pre-industrial
# values below are back-derived from those percentages so the module is
# internally consistent with its own source:
#     CH4:  1935.7 / 2.66 = 727.7 ppb
#     N2O:  338.9  / 1.26 = 269.0 ppb
# Both sit inside the accepted IPCC AR6 1750 ranges (CH4 729.2 ppb,
# N2O 270.1 ppb). Substitute the AR6 values if you need consistency
# with AR6 forcing tables instead.
CO2_PPM_PREINDUSTRIAL = 278.0
CH4_PPB_PREINDUSTRIAL = CH4_PPB_2025 / (1.0 + CH4_PCT_ABOVE_PREINDUSTRIAL / 100.0)
N2O_PPB_PREINDUSTRIAL = N2O_PPB_2025 / (1.0 + N2O_PCT_ABOVE_PREINDUSTRIAL / 100.0)

FOSSIL_CO2_PgC_YR_2025 = 10.3         # petagrams carbon per year
FOSSIL_CO2_PgC_YR_UNCERTAINTY = 0.5
FOSSIL_CO2_PgC_YR_1960s = 3.0         # petagrams carbon per year
FOSSIL_CO2_PgC_YR_1960s_UNCERTAINTY = 0.2


# ─────────────────────────────────────────────
# TEMPERATURE — WARMEST YEAR WITHOUT AN EL NINO
# ─────────────────────────────────────────────

GLOBAL_TEMP_RANK_2025 = 3             # among the three warmest on record
GLOBAL_TEMP_RECORD_START = 1850       # mid-1800s instrumental record
WARMEST_YEAR_WITHOUT_EL_NINO = True   # the structural finding
ENSO_STATE_2025 = "neutral_to_la_nina"
N_WARMEST_YEARS_CONSECUTIVE = 11      # 2015-2025 are the 11 warmest
WARMEST_YEARS_SPAN = (2015, 2025)

EUROPE_TEMP_RANK_2025 = 1             # warmest on record
SECOND_WARMEST_COUNTRIES_2025 = (
    "Russia", "China", "South Korea", "Argentina")


# ─────────────────────────────────────────────
# OCEAN — HEAT, SEA LEVEL, MARINE HEATWAVES
# ─────────────────────────────────────────────

OCEAN_HEAT_CONTENT_RECORD_2025 = True         # 0-2000 m, record high
OCEAN_SHARE_OF_EXCESS_HEAT = 0.90             # ~90% over the past ~50 yr

GMSL_MM_ABOVE_1993 = 111.2                    # global mean sea level
GMSL_CONSECUTIVE_RECORD_YEARS = 14
GMSL_ALTIMETRY_BASELINE_YEAR = 1993
SLR_THERMAL_MM_YR = 1.6                       # thermal expansion
SLR_MASS_MM_YR = 2.0                          # land ice melt

SST_RANK_2025 = 3                             # 3rd highest
SST_RECORD_LENGTH_YR = 172
MARINE_HEATWAVE_OCEAN_FRACTION = 0.87         # >=1 MHW during 2025


# ─────────────────────────────────────────────
# ARCTIC — THE ICE-AGE COLLAPSE
# ─────────────────────────────────────────────

ARCTIC_TEMP_RANK_2025 = 2                     # 2nd warmest
ARCTIC_RECORD_LENGTH_YR = 126
ARCTIC_AMPLIFICATION_FACTOR = 3.0             # ~3x the global rate

ARCTIC_MAX_ICE_RANK_2025 = 1                  # LOWEST maximum on record
ARCTIC_SATELLITE_RECORD_YR = 47
# The BAMS chapter and the NOAA Arctic Report Card 2025 rank the
# September minimum 10th lowest; a widely circulated summary says 11th.
# The sourced value is used and the discrepancy is recorded rather than
# silently resolved.
ARCTIC_MIN_ICE_RANK_2025 = 10
ARCTIC_MIN_ICE_RANK_DISPUTED = 11

# Ice older than 4 years, September minimum
MULTIYEAR_ICE_KM2_2025 = 95_000.0
MULTIYEAR_ICE_KM2_MEAN_2005_2024 = 326_000.0
MULTIYEAR_ICE_KM2_MEAN_1985_2004 = 1_720_000.0

TUNDRA_GREENNESS_RANK_2025 = 3                # 3rd highest on record


# ─────────────────────────────────────────────
# ANTARCTIC
# ─────────────────────────────────────────────

ANTARCTIC_TEMP_RANK_2025 = 1                  # warmest since records began
ANTARCTIC_RECORD_START = 1979
ANTARCTIC_MAX_ICE_RANK_2025 = 3               # 3rd lowest daily maximum
ANTARCTIC_MIN_ICE_RANK_2025 = 4               # 4th lowest daily minimum
ANTARCTIC_SEA_ICE_BELOW_AVERAGE_YEARS = 9     # nearly a decade


# ─────────────────────────────────────────────
# GLACIERS — 38 CONSECUTIVE YEARS OF LOSS
# ─────────────────────────────────────────────

GLACIER_CONSECUTIVE_LOSS_YEARS = 38
GLACIER_LOSS_M_WE_2025 = 1.0                  # >1 m water equivalent
GLACIER_YEARS_ABOVE_1M_WE = 4                 # 4th straight year
GLACIER_LOSS_SHARE_LAST_DECADE = 0.41         # of all loss since 1976
GLACIER_RECORD_START = 1976


# ─────────────────────────────────────────────
# TROPICAL CYCLONES
# ─────────────────────────────────────────────

NAMED_STORMS_2025 = 97
NAMED_STORMS_AVERAGE_1991_2020 = 87
CATEGORY_5_STORMS_2025 = 5
CATEGORY_5_NORTH_ATLANTIC_2025 = 3

MELISSA_MAX_WIND_MPH = 190.0
MELISSA_MIN_PRESSURE_HPA = 892.0
MELISSA_LANDFALL_CATEGORY = 5
MELISSA_FATALITIES = 95
MELISSA_DAMAGE_USD_BILLION = 12.2


# ─────────────────────────────────────────────
# RADIATIVE FORCING FROM THE MEASURED MIXING RATIOS
# Myhre et al. (1998) simplified expressions, as used in IPCC TAR/AR4.
# ─────────────────────────────────────────────


def co2_forcing_Wm2(C: float = CO2_PPM_2025,
                    C0: float = CO2_PPM_PREINDUSTRIAL) -> float:
    """
    CO2 radiative forcing: dF = 5.35 * ln(C/C0), W/m^2.

    C  : CO2 mixing ratio (ppm)
    C0 : reference mixing ratio (ppm)
    """
    if C <= 0 or C0 <= 0:
        raise ValueError("mixing ratios must be positive")
    return 5.35 * math.log(C / C0)


def _overlap(M: float, N: float) -> float:
    """CH4-N2O band overlap term f(M,N) from Myhre et al. (1998)."""
    return 0.47 * math.log(
        1.0 + 2.01e-5 * (M * N) ** 0.75 + 5.31e-15 * M * (M * N) ** 1.52)


def ch4_forcing_Wm2(M: float = CH4_PPB_2025,
                    M0: float = None,
                    N0: float = None) -> float:
    """
    CH4 radiative forcing including the N2O band overlap, W/m^2.

        dF = 0.036*(sqrt(M) - sqrt(M0)) - [f(M,N0) - f(M0,N0)]
    """
    M0 = CH4_PPB_PREINDUSTRIAL if M0 is None else M0
    N0 = N2O_PPB_PREINDUSTRIAL if N0 is None else N0
    return (0.036 * (math.sqrt(M) - math.sqrt(M0))
            - (_overlap(M, N0) - _overlap(M0, N0)))


def n2o_forcing_Wm2(N: float = N2O_PPB_2025,
                    N0: float = None,
                    M0: float = None) -> float:
    """
    N2O radiative forcing including the CH4 band overlap, W/m^2.

        dF = 0.12*(sqrt(N) - sqrt(N0)) - [f(M0,N) - f(M0,N0)]
    """
    N0 = N2O_PPB_PREINDUSTRIAL if N0 is None else N0
    M0 = CH4_PPB_PREINDUSTRIAL if M0 is None else M0
    return (0.12 * (math.sqrt(N) - math.sqrt(N0))
            - (_overlap(M0, N) - _overlap(M0, N0)))


def total_ghg_forcing_Wm2() -> Dict[str, float]:
    """
    Combined forcing from the three gases the report tabulates.

    This is the number the mixing ratios imply. It excludes halocarbons,
    tropospheric ozone, aerosols, and land-use albedo, so it is NOT the
    total anthropogenic forcing and must not be reported as one — the
    aerosol term in particular is large and negative.
    """
    co2 = co2_forcing_Wm2()
    ch4 = ch4_forcing_Wm2()
    n2o = n2o_forcing_Wm2()
    total = co2 + ch4 + n2o
    return {
        "CO2_Wm2":   co2,
        "CH4_Wm2":   ch4,
        "N2O_Wm2":   n2o,
        "total_Wm2": total,
        "CO2_share": co2 / total if total else float("nan"),
        "excludes":  ["halocarbons", "tropospheric_ozone",
                      "aerosol_direct", "aerosol_indirect",
                      "land_use_albedo", "black_carbon_on_snow"],
        "note": "three-gas forcing only; the aerosol terms are large and "
                "negative, so this is not total anthropogenic forcing",
    }


def emissions_growth_factor() -> Dict[str, float]:
    """Fossil CO2 emission rate now versus the 1960s."""
    factor = FOSSIL_CO2_PgC_YR_2025 / FOSSIL_CO2_PgC_YR_1960s
    return {
        "PgC_yr_2025":  FOSSIL_CO2_PgC_YR_2025,
        "PgC_yr_1960s": FOSSIL_CO2_PgC_YR_1960s,
        "factor":       factor,
        "GtCO2_yr_2025": FOSSIL_CO2_PgC_YR_2025 * 44.009 / 12.011,
    }


# ─────────────────────────────────────────────
# SEA-LEVEL BUDGET
# ─────────────────────────────────────────────


def sea_level_budget() -> Dict[str, object]:
    """
    Do the reported components add up to the reported rise?

    The report gives thermal expansion ~1.6 mm/yr and land-ice mass loss
    ~2.0 mm/yr. Their sum is the altimetric rate the budget has to
    reproduce. The mean rate implied by the cumulative rise since 1993
    is lower than the current rate because the rise is ACCELERATING —
    a budget that closes against the mean would be closing against the
    wrong number.
    """
    years = REPORT_DATA_YEAR - GMSL_ALTIMETRY_BASELINE_YEAR
    mean_rate = GMSL_MM_ABOVE_1993 / years if years else float("nan")
    component_sum = SLR_THERMAL_MM_YR + SLR_MASS_MM_YR
    return {
        "cumulative_mm":        GMSL_MM_ABOVE_1993,
        "years_since_baseline": years,
        "mean_rate_mm_yr":      mean_rate,
        "thermal_mm_yr":        SLR_THERMAL_MM_YR,
        "mass_mm_yr":           SLR_MASS_MM_YR,
        "component_sum_mm_yr":  component_sum,
        "mass_share":           SLR_MASS_MM_YR / component_sum,
        "current_exceeds_mean": component_sum > mean_rate,
        "acceleration_implied_mm_yr2": (
            2.0 * (component_sum - mean_rate) / years if years else float("nan")),
        "note": "mass loss now exceeds thermal expansion; the ice term "
                "is the one that is growing, and it is the one with no "
                "equilibrium on policy timescales",
    }


# ─────────────────────────────────────────────
# ARCTIC ICE AGE COLLAPSE
# ─────────────────────────────────────────────


def multiyear_ice_loss() -> Dict[str, float]:
    """
    Loss of ice older than four years, against both published baselines.

    Ice age is a proxy for thickness and therefore for the heat required
    to melt it. Replacing multi-year ice with first-year ice lowers the
    latent-heat barrier protecting the summer minimum: the same forcing
    removes more ice each year because what remains is thinner.
    """
    recent = MULTIYEAR_ICE_KM2_MEAN_2005_2024
    historic = MULTIYEAR_ICE_KM2_MEAN_1985_2004
    return {
        "km2_2025":               MULTIYEAR_ICE_KM2_2025,
        "km2_mean_2005_2024":     recent,
        "km2_mean_1985_2004":     historic,
        "loss_vs_2005_2024":      1.0 - MULTIYEAR_ICE_KM2_2025 / recent,
        "loss_vs_1985_2004":      1.0 - MULTIYEAR_ICE_KM2_2025 / historic,
        "remaining_fraction_of_1985_2004":
            MULTIYEAR_ICE_KM2_2025 / historic,
        "factor_below_historic":  historic / MULTIYEAR_ICE_KM2_2025,
    }


# ─────────────────────────────────────────────
# THE STRUCTURAL FINDING: WARMTH WITHOUT EL NINO
# ─────────────────────────────────────────────


def enso_decoupling_check(assumed_el_nino_required: bool = True
                          ) -> Dict[str, object]:
    """
    2023 and 2024 set records with a strong El Nino supplying part of
    the anomaly. 2025 reached the top three with ENSO neutral to
    La Nina-like.

    That breaks a working assumption used to read year-to-year records:
    that a record year implies an El Nino contribution, and that the
    following La Nina year should step back down. If the baseline has
    risen far enough that a neutral year lands in the top three, ENSO is
    now modulation on a trend rather than the source of the extremes,
    and "it was an El Nino year" stops being available as an explanation
    for the next record.

    Returns the flag a solver should set before attributing an anomaly
    to ENSO phase.
    """
    return {
        "year":                     REPORT_DATA_YEAR,
        "global_rank":              GLOBAL_TEMP_RANK_2025,
        "enso_state":               ENSO_STATE_2025,
        "record_without_el_nino":   WARMEST_YEAR_WITHOUT_EL_NINO,
        "assumption_holds":         not (assumed_el_nino_required
                                         and WARMEST_YEAR_WITHOUT_EL_NINO),
        "consecutive_warmest_years": N_WARMEST_YEARS_CONSECUTIVE,
        "implication": (
            "ENSO phase is modulation on a rising baseline, not the "
            "source of record years. Do not attribute a record to El "
            "Nino without checking the phase, and do not expect a "
            "La Nina year to return to a prior level."
        ),
    }


# ─────────────────────────────────────────────
# PROVENANCE
# ─────────────────────────────────────────────

# Every value with the chapter it comes from. Keys are the module-level
# constant names so a downstream consumer can trace any number back.
PROVENANCE: Dict[str, Dict[str, str]] = {
    "CO2_PPM_2025": {
        "value": "425.6 +/- 0.1 ppm",
        "chapter": "Global Climate — atmospheric composition",
        "source": "State of the Climate in 2025 (BAMS, 2026)",
    },
    "CH4_PPB_2025": {
        "value": "1935.7 ppb",
        "chapter": "Global Climate — atmospheric composition",
        "source": "State of the Climate in 2025 (BAMS, 2026)",
    },
    "N2O_PPB_2025": {
        "value": "338.9 ppb",
        "chapter": "Global Climate — atmospheric composition",
        "source": "State of the Climate in 2025 (BAMS, 2026)",
    },
    "FOSSIL_CO2_PgC_YR_2025": {
        "value": "10.3 +/- 0.5 PgC/yr",
        "chapter": "Global Climate — carbon cycle",
        "source": "State of the Climate in 2025 (BAMS, 2026)",
    },
    "GMSL_MM_ABOVE_1993": {
        "value": "111.2 mm above the 1993 altimetry baseline",
        "chapter": "Global Oceans — sea level",
        "source": "State of the Climate in 2025 (BAMS, 2026)",
    },
    "MARINE_HEATWAVE_OCEAN_FRACTION": {
        "value": "87% of ocean surface with >=1 marine heatwave",
        "chapter": "Global Oceans — marine heatwaves",
        "source": "State of the Climate in 2025 (BAMS, 2026)",
    },
    "MULTIYEAR_ICE_KM2_2025": {
        "value": "95,000 km2 of ice older than 4 years at the September "
                 "minimum",
        "chapter": "Arctic — sea ice",
        "source": "NOAA Arctic Report Card 2025; BAMS Arctic chapter",
    },
    "ARCTIC_MAX_ICE_RANK_2025": {
        "value": "lowest annual maximum in the 47-year satellite record "
                 "(March 2025)",
        "chapter": "Arctic — sea ice",
        "source": "NOAA Arctic Report Card 2025",
    },
    "GLACIER_CONSECUTIVE_LOSS_YEARS": {
        "value": "38th consecutive year of loss; >1 m w.e. for the 4th "
                 "straight year; 41% of loss since 1976 in the last decade",
        "chapter": "Global Climate — glaciers (WGMS reference glaciers)",
        "source": "State of the Climate in 2025 (BAMS, 2026)",
    },
    "MELISSA_MIN_PRESSURE_HPA": {
        "value": "892 hPa, 190 mph on 28 October 2025",
        "chapter": "Tropical Cyclones — North Atlantic",
        "source": "State of the Climate in 2025 (BAMS, 2026)",
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
    BASELINE keys this report updates, as measured values.

    Apply with:

        from cascade_engine import BASELINE
        from state_of_the_climate_2025 import baseline_overrides
        p = dict(BASELINE); p.update(baseline_overrides())

    Only quantities the report measures directly are included. Nothing
    here is tuned to make the model behave; if a value disagrees with a
    model expectation, the measurement is the one that stays.
    """
    return {
        "CO2_ppm":    CO2_PPM_2025,
        "delta_CO2":  CO2_PPM_2025 - CO2_PPM_PREINDUSTRIAL,
        "CH4_ppb":    CH4_PPB_2025,
        "N2O_ppb":    N2O_PPB_2025,
        "SLR_mm_since_1993": GMSL_MM_ABOVE_1993,
        "marine_heatwave_fraction": MARINE_HEATWAVE_OCEAN_FRACTION,
        "arctic_multiyear_ice_km2": MULTIYEAR_ICE_KM2_2025,
    }


def records_broken() -> List[Dict[str, object]]:
    """Every quantity the report records as an all-time high or low."""
    return [
        {"quantity": "CO2 concentration", "kind": "record_high",
         "value": CO2_PPM_2025, "units": "ppm"},
        {"quantity": "CH4 concentration", "kind": "record_high",
         "value": CH4_PPB_2025, "units": "ppb"},
        {"quantity": "N2O concentration", "kind": "record_high",
         "value": N2O_PPB_2025, "units": "ppb"},
        {"quantity": "fossil CO2 emissions", "kind": "record_high",
         "value": FOSSIL_CO2_PgC_YR_2025, "units": "PgC/yr"},
        {"quantity": "ocean heat content 0-2000 m", "kind": "record_high",
         "value": None, "units": "ZJ"},
        {"quantity": "global mean sea level", "kind": "record_high",
         "value": GMSL_MM_ABOVE_1993, "units": "mm above 1993"},
        {"quantity": "Arctic maximum sea ice extent", "kind": "record_low",
         "value": ARCTIC_MAX_ICE_RANK_2025, "units": "rank in 47-yr record"},
        {"quantity": "Antarctic annual temperature", "kind": "record_high",
         "value": ANTARCTIC_TEMP_RANK_2025, "units": "rank since 1979"},
        {"quantity": "Europe annual temperature", "kind": "record_high",
         "value": EUROPE_TEMP_RANK_2025, "units": "rank"},
    ]


if __name__ == "__main__":
    print(f"{REPORT_TITLE.upper()}  —  {REPORT_EDITION}th annual report")
    print(f"published {REPORT_PUBLISHED_MONTH:02d}/{REPORT_PUBLISHED_YEAR}, "
          f"data year {REPORT_DATA_YEAR}, "
          f"{REPORT_CONTRIBUTORS} scientists / {REPORT_COUNTRIES} countries")
    print("=" * 72)

    print("\nGREENHOUSE GASES")
    print(f"  CO2  {CO2_PPM_2025:7.1f} ppm   "
          f"(+{CO2_PCT_ABOVE_PREINDUSTRIAL:.0f}% vs "
          f"{CO2_PPM_PREINDUSTRIAL:.0f} ppm)")
    print(f"  CH4  {CH4_PPB_2025:7.1f} ppb   "
          f"(+{CH4_PCT_ABOVE_PREINDUSTRIAL:.0f}% vs "
          f"{CH4_PPB_PREINDUSTRIAL:.0f} ppb)")
    print(f"  N2O  {N2O_PPB_2025:7.1f} ppb   "
          f"(+{N2O_PCT_ABOVE_PREINDUSTRIAL:.0f}% vs "
          f"{N2O_PPB_PREINDUSTRIAL:.0f} ppb)")
    g = emissions_growth_factor()
    print(f"  fossil CO2 {g['PgC_yr_2025']:.1f} PgC/yr "
          f"= {g['GtCO2_yr_2025']:.1f} Gt CO2/yr, "
          f"{g['factor']:.1f}x the 1960s")

    print("\nRADIATIVE FORCING IMPLIED BY THOSE MIXING RATIOS")
    f = total_ghg_forcing_Wm2()
    print(f"  CO2 {f['CO2_Wm2']:.3f} + CH4 {f['CH4_Wm2']:.3f} + "
          f"N2O {f['N2O_Wm2']:.3f} = {f['total_Wm2']:.3f} W/m2")
    print(f"  CO2 share {f['CO2_share']:.1%}")
    print(f"  excludes: {', '.join(f['excludes'][:3])}, ...")

    print("\nTEMPERATURE")
    e = enso_decoupling_check()
    print(f"  global rank {e['global_rank']} with ENSO {e['enso_state']}")
    print(f"  record without El Nino: {e['record_without_el_nino']}")
    print(f"  warmest {e['consecutive_warmest_years']} years = "
          f"{WARMEST_YEARS_SPAN[0]}-{WARMEST_YEARS_SPAN[1]}")
    print(f"  -> {e['implication']}")

    print("\nSEA LEVEL")
    s = sea_level_budget()
    print(f"  {s['cumulative_mm']:.1f} mm above 1993 "
          f"({GMSL_CONSECUTIVE_RECORD_YEARS}th consecutive record year)")
    print(f"  mean rate since 1993 : {s['mean_rate_mm_yr']:.2f} mm/yr")
    print(f"  current components   : thermal {s['thermal_mm_yr']:.1f} + "
          f"mass {s['mass_mm_yr']:.1f} = {s['component_sum_mm_yr']:.1f} mm/yr")
    print(f"  mass share {s['mass_share']:.0%}; current rate exceeds the "
          f"mean: {s['current_exceeds_mean']}")

    print("\nOCEAN")
    print(f"  heat content 0-2000 m: record high = "
          f"{OCEAN_HEAT_CONTENT_RECORD_2025}")
    print(f"  SST rank {SST_RANK_2025} of {SST_RECORD_LENGTH_YR} years, "
          f"with cool ENSO")
    print(f"  {MARINE_HEATWAVE_OCEAN_FRACTION:.0%} of the ocean surface saw "
          f"at least one marine heatwave")

    print("\nARCTIC")
    m = multiyear_ice_loss()
    print(f"  temperature rank {ARCTIC_TEMP_RANK_2025} in "
          f"{ARCTIC_RECORD_LENGTH_YR} years; warming ~"
          f"{ARCTIC_AMPLIFICATION_FACTOR:.0f}x the global rate")
    print(f"  maximum extent: LOWEST in the "
          f"{ARCTIC_SATELLITE_RECORD_YR}-year satellite record")
    print(f"  ice >4 yr old: {m['km2_2025']:,.0f} km2")
    print(f"    -{m['loss_vs_2005_2024']:.0%} vs the 2005-2024 mean, "
          f"-{m['loss_vs_1985_2004']:.0%} vs the 1985-2004 mean")
    print(f"    {m['factor_below_historic']:.0f}x less than 1985-2004")

    print("\nGLACIERS")
    print(f"  {GLACIER_CONSECUTIVE_LOSS_YEARS} consecutive years of loss; "
          f">1 m w.e. for {GLACIER_YEARS_ABOVE_1M_WE} straight years")
    print(f"  {GLACIER_LOSS_SHARE_LAST_DECADE:.0%} of all loss since "
          f"{GLACIER_RECORD_START} occurred in the last decade")

    print("\nTROPICAL CYCLONES")
    print(f"  {NAMED_STORMS_2025} named storms "
          f"(1991-2020 average {NAMED_STORMS_AVERAGE_1991_2020}); "
          f"{CATEGORY_5_STORMS_2025} reached Cat 5")
    print(f"  Melissa: {MELISSA_MAX_WIND_MPH:.0f} mph, "
          f"{MELISSA_MIN_PRESSURE_HPA:.0f} hPa, "
          f"{MELISSA_FATALITIES} fatalities, "
          f"${MELISSA_DAMAGE_USD_BILLION}B damage")

    print("\nRECORDS BROKEN")
    for r in records_broken():
        print(f"  {r['kind']:12s} {r['quantity']}")

    print("\nBASELINE OVERRIDES FOR THE CASCADE ENGINE")
    for k, v in baseline_overrides().items():
        print(f"  {k:28s} {v}")
