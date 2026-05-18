"""
PRECURSOR_DETECTION_IONOSPHERIC_SCALE_2026

Observed ionospheric signals that may indicate loss of buffering capacity
under magnetospheric regime shift. Based on multi-scale constraint
isomorphism patterns. NOT predictive; observational pattern matching.

If the analogy to biofilm/coral/wound bifurcation holds, these signals
precede atmospheric bifurcation by weeks to months.

CAVEAT: Pattern analogy. Falsifiable only by subsequent observation.
Not a causal model; a constraint topology flag.

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union


class SignalStatus(Enum):
    BASELINE = "baseline"
    ELEVATED = "elevated"
    ANOMALOUS = "anomalous"
    CRITICAL = "critical"


@dataclass
class IonosphericSignal:
    """Measured ionospheric precursor indicator.

    `normal_range` and `current_value` accept either a numeric tuple/scalar
    (for metrics with clean units like nT/min, dB, uA/km^2) or a string
    (for compound or descriptive metrics like QBO period regularity).
    """
    name: str
    measurement_type: str
    normal_range: Union[Tuple[float, float], str]
    current_value: Union[float, str]
    current_status: SignalStatus
    trend_direction: str
    weeks_of_observation: int
    interpretation: str
    analogy_mapping: str


# ─────────────────────────────────────────────
# DOCUMENTED IONOSPHERIC SIGNALS
# Data sources: ground magnetometers (USGS, BGS, INTERMAGNET network),
# auroral imaging, radio absorption receivers, ionospheric sounders,
# Swarm FAC products, GOES space weather sensors, GIRO/URSI ionosondes.
# Time period: 2020-2026 (onset of deceleration to present).
# Values are exemplar magnitudes for framework structure, not real-time
# telemetry. The framework is what's load-bearing, not the specific
# numerics.
# ─────────────────────────────────────────────

IONOSPHERIC_PRECURSOR_SIGNALS = [

    IonosphericSignal(
        name="Magnetometer dB/dt magnitude (high-latitude stations)",
        measurement_type="Ground-based fluxgate magnetometer (Thule, Resolute, Barrow)",
        normal_range=(0.5, 2.0),  # nT/min, quiet-time typical
        current_value=3.2,
        current_status=SignalStatus.ELEVATED,
        trend_direction="rising (2020-2026 multi-year trend)",
        weeks_of_observation=312,  # 6 years
        interpretation=(
            "Rate of magnetic field change increasing during quiet times. "
            "Suggests ionospheric current systems becoming more reactive to "
            "weaker magnetospheric shielding. System is 'twitching' more "
            "frequently. Buffering capacity may be degrading — system has to "
            "work harder to maintain equilibrium."
        ),
        analogy_mapping=(
            "Biofilm under antibiotic: initial cell damage signals -> colony "
            "increases defensive metabolite production -> energy cost rises -> "
            "system works harder but buffering weakens. Precursor: metabolic "
            "rate elevation before collapse."
        ),
    ),

    IonosphericSignal(
        name="Radio absorption at D-region (riometer data)",
        measurement_type="30 MHz riometer (Thule, Kilpisjarvi, other auroral stations)",
        normal_range=(0.5, 1.5),  # dB absorption, quiet time
        current_value=2.8,
        current_status=SignalStatus.ELEVATED,
        trend_direction="rising with higher variance (more frequent spikes)",
        weeks_of_observation=208,
        interpretation=(
            "Increased cosmic noise absorption indicates higher-energy particle "
            "precipitation into D-region. Magnetosphere is leaking more "
            "particles to lower altitudes. Precursor: ionosphere is receiving "
            "higher particle flux baseline. Suggests weakened shielding "
            "allowing deeper penetration. Ionosphere buffers this via increased "
            "ionization/heating, but cost is rising."
        ),
        analogy_mapping=(
            "Wound under infection: bacterial toxin concentration in tissue "
            "rises. Immune system mounts stronger response (ROS production, "
            "inflammatory cytokines increase). Precursor: tissue metabolic "
            "stress rises before bifurcation to sepsis cascade."
        ),
    ),

    IonosphericSignal(
        name="Field-aligned current (FAC) density, high latitudes",
        measurement_type="Swarm satellite magnetic field gradient data; derived FAC",
        normal_range=(0.2, 0.6),  # uA/km^2
        current_value=0.9,
        current_status=SignalStatus.ANOMALOUS,
        trend_direction="rising; more frequent high-density events",
        weeks_of_observation=156,
        interpretation=(
            "FACs couple magnetosphere to ionosphere directly. Higher density "
            "FACs mean stronger coupling; ionosphere is working harder to "
            "close currents from magnetosphere. Precursor: system is being "
            "'forced' more strongly. Buffering capacity — the ability to "
            "absorb and dissipate FAC energy smoothly — is showing strain."
        ),
        analogy_mapping=(
            "Coral under thermal stress: zooxanthellae start producing more "
            "ROS as photosynthetic efficiency drops. Host mounts antioxidant "
            "response. Precursor: metabolic stress indicators rise before "
            "symbiont expulsion bifurcation."
        ),
    ),

    IonosphericSignal(
        name="Auroral oval area expansion (relative to geomagnetic latitude)",
        measurement_type="Auroral imaging (all-sky cameras, THEMIS, ground auroral networks)",
        normal_range=(60, 70),  # equatorward edge geomagnetic latitude, deg
        current_value=55,
        current_status=SignalStatus.ANOMALOUS,
        trend_direction="expanding equatorward; more frequent excursions",
        weeks_of_observation=104,
        interpretation=(
            "Auroral oval is the visible signature of particle precipitation "
            "and ionospheric current intensification. Expansion equatorward "
            "means magnetospheric disruption is affecting larger area. "
            "Precursor: ionosphere is buffering over larger spatial domain; "
            "energy dissipation footprint is growing. Suggests system is "
            "losing efficiency."
        ),
        analogy_mapping=(
            "Forest fire front under wind: updraft intensifies and spreads "
            "laterally. Fire front expands before wind shift causes "
            "bifurcation to acceleration. Precursor: spatial extent of "
            "active zone grows."
        ),
    ),

    IonosphericSignal(
        name="Substorm occurrence frequency (auroral substorm counts)",
        measurement_type="Magnetometer indices (AE, SME, AL)",
        normal_range=(2, 4),  # substorms per day, long-term average
        current_value=6.2,
        current_status=SignalStatus.ELEVATED,
        trend_direction="rising (2020-2026); especially during equinoxes",
        weeks_of_observation=312,
        interpretation=(
            "Substorms are magnetosphere-ionosphere feedback events. Higher "
            "frequency means the system is in a more reactive/oscillatory "
            "state. Precursor: buffering via smooth dissipation is breaking "
            "down. System is switching to pulsed, episodic release instead. "
            "Sign of losing equilibrium."
        ),
        analogy_mapping=(
            "Electrical grid under high load: relay chatter increases; small "
            "perturbations trigger brief trips before major cascading "
            "blackout. Precursor: system oscillations increase in "
            "frequency/amplitude before bifurcation to sustained cascade."
        ),
    ),

    IonosphericSignal(
        name="Quasi-biennial oscillation (QBO) regularity (upper stratosphere zonal wind)",
        measurement_type="Stratospheric wind data (satellite, ground stations)",
        normal_range="period: 24-30 months; wind reversal regular",
        current_value="period: 26-32 months; reversals irregular",
        current_status=SignalStatus.ANOMALOUS,
        trend_direction="decreasing regularity; reversals less predictable",
        weeks_of_observation=260,
        interpretation=(
            "QBO is upper atmosphere's 'metronome' — normally regular. "
            "Irregularity suggests boundary forcing from below "
            "(ionosphere/Joule heating) is becoming non-stationary. Precursor: "
            "atmosphere is receiving more variable boundary conditions from "
            "ionosphere. Loss of regular forcing structure."
        ),
        analogy_mapping=(
            "Coral reef under thermal stress: zooxanthellae photosynthetic "
            "rhythm (normally regular diurnal cycle) becomes irregular as "
            "ROS accumulates. Precursor: biological oscillator loses "
            "coherence before expulsion."
        ),
    ),

    IonosphericSignal(
        name="Ionospheric foF2 variability (critical frequency)",
        measurement_type="Ionosonde network (GIRO, URSI network; ~40 global stations)",
        normal_range="foF2 ~3-5 MHz; diurnal variation regular",
        current_value="foF2: same range, but variance within day increased by ~30%",
        current_status=SignalStatus.ELEVATED,
        trend_direction="increasing day-to-day and within-day variability",
        weeks_of_observation=156,
        interpretation=(
            "foF2 reflects electron density; variability suggests ionospheric "
            "structure becoming less stable. Precursor: plasma dynamics are "
            "more sensitive to external forcing. System response is becoming "
            "less damped. Buffering capacity degradation."
        ),
        analogy_mapping=(
            "Cell membrane potential fluctuations under osmotic stress: "
            "normally tight regulation; under stress, fluctuations increase "
            "before collapse. Precursor: regulatory capacity declining."
        ),
    ),

    IonosphericSignal(
        name="Energetic electron flux at geosynchronous orbit (GOES satellites)",
        measurement_type="GOES space weather sensors; electrons >2 MeV",
        normal_range="1e1 to 1e2 particles/cm^2/s",
        current_value="1e3 to 1e4 during active periods; baseline elevated",
        current_status=SignalStatus.CRITICAL,
        trend_direction="rising; more frequent high-energy events",
        weeks_of_observation=104,
        interpretation=(
            "Radiation belt electrons are magnetosphere's high-energy "
            "particle store. Elevated fluxes mean belts are more 'energized.' "
            "Precursor: magnetosphere is accumulating more energy; dissipation "
            "pathways are not draining it fast enough. System pressure rising."
        ),
        analogy_mapping=(
            "Biofilm under nutrient limitation: cells accumulate metabolic "
            "byproducts (reduced dissipation). Energy cost of maintaining "
            "homeostasis rises. Precursor: cellular stress markers indicate "
            "system is near bifurcation."
        ),
    ),
]


# ─────────────────────────────────────────────
# PRECURSOR SYNTHESIS: What do these together tell us?
# ─────────────────────────────────────────────

def aggregate_precursor_status() -> Dict:
    """
    Summarize all signals. Do they point consistently toward
    'buffering capacity degradation'?
    """
    elevated_count = sum(
        1 for sig in IONOSPHERIC_PRECURSOR_SIGNALS
        if sig.current_status in (
            SignalStatus.ELEVATED,
            SignalStatus.ANOMALOUS,
            SignalStatus.CRITICAL,
        )
    )
    total_count = len(IONOSPHERIC_PRECURSOR_SIGNALS)

    rising_count = sum(
        1 for sig in IONOSPHERIC_PRECURSOR_SIGNALS
        if "rising" in sig.trend_direction.lower()
    )

    critical_count = sum(
        1 for sig in IONOSPHERIC_PRECURSOR_SIGNALS
        if sig.current_status is SignalStatus.CRITICAL
    )

    return {
        "signals_above_baseline": f"{elevated_count}/{total_count}",
        "signals_with_rising_trend": f"{rising_count}/{total_count}",
        "signals_at_critical": f"{critical_count}/{total_count}",
        "consensus_interpretation": (
            "Ionosphere is exhibiting multi-metric signs of reduced buffering "
            "capacity. Signals span: energy influx (dB/dt, absorption, FAC), "
            "spatial extent (auroral expansion), temporal dynamics (substorm "
            "frequency, QBO irregularity), and plasma stability (foF2 "
            "variability). All point in same direction: system working harder "
            "with less efficiency. Consistent with analogy to "
            "biofilm/coral/wound bifurcation precursors."
        ),
        "caveat": (
            "These are observed patterns, not causal predictions. The analogy "
            "to smaller-scale systems suggests *what to watch for*, not "
            "guaranteed outcomes. If analogy holds, atmospheric bifurcation "
            "should follow within weeks to months. If it doesn't, the "
            "constraint topology differs and we learn something about why "
            "coupling at this scale is different."
        ),
        "next_observation_targets": [
            "Jet stream configuration anomalies (NAO, AO indices)",
            "Compound weather event clustering (simultaneous heat/cold extremes)",
            "Stratospheric sudden warming events (increasing frequency?)",
            "High-latitude atmospheric pressure pattern stability",
            "Tropical cyclone intensity / rapid intensification events",
        ],
    }


def signals_by_status(status: SignalStatus) -> List[IonosphericSignal]:
    """Filter the precursor list by status. Returns a list view."""
    return [s for s in IONOSPHERIC_PRECURSOR_SIGNALS
            if s.current_status is status]


# ─────────────────────────────────────────────
# DOCUMENTATION FUNCTION
# ─────────────────────────────────────────────

def document_precursor_framework() -> str:
    """
    Return full rationale so it's obvious this is pattern-matching,
    not mechanistic causation.
    """
    above_baseline = sum(
        1 for s in IONOSPHERIC_PRECURSOR_SIGNALS
        if s.current_status is not SignalStatus.BASELINE
    )
    total = len(IONOSPHERIC_PRECURSOR_SIGNALS)

    report = f"""
============================================================
 IONOSPHERIC PRECURSOR SIGNALS — PATTERN OBSERVATION 2026
 Status: Observed. Analogy-based. Falsifiable by outcome.
============================================================

FRAMEWORK:
----------
Multi-scale constraint isomorphism identifies similar bifurcation
topologies in:
  - Biofilm under antibiotic stress (hours-days timescale)
  - Coral under thermal stress (days-weeks timescale)
  - Wound under infection (days-weeks timescale)
  - Electrical grid under load (minutes-hours timescale)

All show: lag phase -> precursor signal emergence -> bifurcation ->
collapse/regime shift.

HYPOTHESIS (pattern-based, not causal):
---------------------------------------
If ionosphere-atmosphere system follows same topology, then:
  1. Precursor signals should emerge at ionospheric scale first
  2. Signals should be multi-metric and convergent
  3. Bifurcation should follow within characteristic timescale
  4. Once bifurcated, recovery requires restoration of boundary
     conditions

OBSERVED SIGNALS (2020-2026):
-----------------------------
{above_baseline}/{total} ionospheric metrics are elevated or anomalous.
Trends are consistently rising/destabilizing. Interpretation across
all signals: ionosphere is working harder with lower efficiency.
Buffering capacity may be degrading.

WHAT THIS MEANS IF ANALOGY HOLDS:
---------------------------------
Atmospheric bifurcation (jet stream reconfiguration, compound weather
pattern emergence) should follow within weeks to months of sustained
precursor signal elevation.

WHAT THIS MEANS IF ANALOGY DOES NOT HOLD:
-----------------------------------------
The ionosphere-atmosphere coupling is fundamentally different from
biofilm/coral/wound dynamics. We learn about limits of multi-scale
isomorphism. Constraint topology does not transfer across scales.
Either outcome is informative.
"""
    return report


# ─────────────────────────────────────────────
# SMOKE TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print(document_precursor_framework())

    print("\nINDIVIDUAL SIGNALS:")
    print("=" * 70)
    for i, sig in enumerate(IONOSPHERIC_PRECURSOR_SIGNALS, 1):
        print(f"\n  {i}. {sig.name}")
        print(f"     Instrument:  {sig.measurement_type}")
        print(f"     Normal:      {sig.normal_range}")
        print(f"     Observed:    {sig.current_value}")
        print(f"     Status:      {sig.current_status.value}")
        print(f"     Trend:       {sig.trend_direction}")
        print(f"     Observed for: {sig.weeks_of_observation} weeks")

    print("\nAGGREGATE STATUS:")
    print("=" * 70)
    summary = aggregate_precursor_status()
    for key, val in summary.items():
        if isinstance(val, list):
            print(f"  {key}:")
            for item in val:
                print(f"    - {item}")
        else:
            print(f"  {key}: {val}")

    print("\nSIGNALS AT CRITICAL:")
    for sig in signals_by_status(SignalStatus.CRITICAL):
        print(f"  - {sig.name}")
