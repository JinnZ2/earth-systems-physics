# assumption_validator/registry.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Assumption registry wired directly to layer coupling_state outputs.
# Variable names and units match layer outputs exactly.
# The physics engine generates state. This reads it and tells you
# when the equations that generated it are no longer valid.

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum


# ─────────────────────────────────────────────
# RISK LEVELS
# ─────────────────────────────────────────────

class RiskLevel(Enum):
    GREEN  = "GREEN"   # stable — equations valid
    YELLOW = "YELLOW"  # transition — equations degrading
    RED    = "RED"     # regime changed — equations invalid


# ─────────────────────────────────────────────
# BOUNDARY DEFINITION
# ─────────────────────────────────────────────

@dataclass
class AssumptionBoundary:
    """
    Defines the stability envelope for one assumption.
    green_range  : (min, max) — equations fully valid
    yellow_range : (min, max) — transition, caution
    red_threshold: value beyond which regime has changed
    higher_is_worse: True if increasing value = increasing risk
    source_layer : which physics layer produces this variable
    layer_key    : exact key in that layer's coupling_state output
    """
    name            : str
    parameter       : str
    units           : str
    green_range     : Tuple[float, float]
    yellow_range    : Tuple[float, float]
    red_threshold   : float
    higher_is_worse : bool
    source_layer    : int
    layer_key       : str
    couplings       : List[str]  = field(default_factory=list)
    rate_of_change  : float      = 0.0   # units/year, + = worsening
    notes           : str        = ""

    def assess(self, value: float) -> Tuple[RiskLevel, float, float]:
        """
        Assess risk for a given value.
        Returns (RiskLevel, confidence_penalty 0-1, proximity_to_red 0-1)
        """
        if value is None:
            return (RiskLevel.GREEN, 0.0, 0.0)

        v = float(value)

        if self.higher_is_worse:
            if v <= self.green_range[1]:
                return (RiskLevel.GREEN, 0.0, 0.0)
            elif v <= self.yellow_range[1]:
                progress = (v - self.green_range[1]) / (
                    self.yellow_range[1] - self.green_range[1] + 1e-30)
                penalty  = 0.3 * progress
                proximity = (v - self.yellow_range[0]) / (
                    self.red_threshold - self.yellow_range[0] + 1e-30)
                return (RiskLevel.YELLOW, penalty, min(1.0, proximity))
            else:
                excess    = (v - self.red_threshold) / (self.red_threshold + 1e-30)
                penalty   = min(1.0, 0.8 + 0.2 * excess)
                return (RiskLevel.RED, penalty, 1.0)
        else:
            # lower is worse
            if v >= self.green_range[0]:
                return (RiskLevel.GREEN, 0.0, 0.0)
            elif v >= self.yellow_range[0]:
                progress  = (self.green_range[0] - v) / (
                    self.green_range[0] - self.yellow_range[0] + 1e-30)
                penalty   = 0.3 * progress
                proximity = (self.yellow_range[1] - v) / (
                    self.yellow_range[1] - self.red_threshold + 1e-30)
                return (RiskLevel.YELLOW, penalty, min(1.0, proximity))
            else:
                deficit   = (self.red_threshold - v) / (abs(self.red_threshold) + 1e-30)
                penalty   = min(1.0, 0.8 + 0.2 * deficit)
                return (RiskLevel.RED, penalty, 1.0)

    def proximity_to_red(self, value: float) -> float:
        _, _, prox = self.assess(value)
        return prox


# ─────────────────────────────────────────────
# REGISTRY
# Keyed by assumption ID.
# layer_key must match exact key in layer coupling_state output.
# ─────────────────────────────────────────────

REGISTRY: Dict[str, AssumptionBoundary] = {

    # ── LAYER 0 — ELECTROMAGNETICS ──────────────────────────────────
    "em_plasma_frequency": AssumptionBoundary(
        name            = "Ionospheric Plasma Frequency",
        parameter       = "plasma_frequency_hz",
        units           = "Hz",
        green_range     = (0, 8e6),
        yellow_range    = (8e6, 12e6),
        red_threshold   = 12e6,
        higher_is_worse = True,
        source_layer    = 0,
        layer_key       = "plasma_frequency_hz",
        couplings       = ["iono_critical_freq", "hf_propagation"],
        notes           = "Rising electron density raises plasma freq — HF comms regime change"
    ),

    # ── LAYER 1 — MAGNETOSPHERE ──────────────────────────────────────
    "mag_standoff_Re": AssumptionBoundary(
        name            = "Magnetopause Standoff Distance",
        parameter       = "magnetopause_standoff_Re",
        units           = "Earth radii",
        green_range     = (8, 12),
        yellow_range    = (5, 8),
        red_threshold   = 5,
        higher_is_worse = False,
        source_layer    = 1,
        layer_key       = "magnetopause_standoff_Re",
        couplings       = ["iono_joule_heating", "grid_gic", "aurora_energy"],
        rate_of_change  = 0.0,
        notes           = "Standoff < 5 Re = extreme storm, radiation belt disruption"
    ),

    "mag_rotation_coupling": AssumptionBoundary(
        name            = "Earth Rotation Rate Perturbation",
        parameter       = "omega_change_rads",
        units           = "rad/s",
        green_range     = (-1e-14, 1e-14),
        yellow_range    = (-1e-13, 1e-13),
        red_threshold   = 1e-12,
        higher_is_worse = True,
        source_layer    = 1,
        layer_key       = "rotation_coupling",
        couplings       = ["atmo_coriolis", "litho_lod", "grid_frequency"],
        rate_of_change  = 1.4e-15,
        notes           = "Climate mass redistribution already measurable in LOD"
    ),

    # ── LAYER 2 — IONOSPHERE ─────────────────────────────────────────
    "iono_critical_freq": AssumptionBoundary(
        name            = "Ionospheric Critical Frequency",
        parameter       = "critical_frequency_hz",
        units           = "Hz",
        green_range     = (0, 8e6),
        yellow_range    = (8e6, 15e6),
        red_threshold   = 15e6,
        higher_is_worse = True,
        source_layer    = 2,
        layer_key       = "critical_frequency_hz",
        couplings       = ["hf_comms", "em_plasma_frequency"],
        notes           = "Above 15 MHz dayside F2 — propagation assumptions break"
    ),

    "iono_joule_heating": AssumptionBoundary(
        name            = "Ionospheric Joule Heating Rate",
        parameter       = "joule_heating_Wm3",
        units           = "W/m³",
        green_range     = (0, 1e-8),
        yellow_range    = (1e-8, 1e-6),
        red_threshold   = 1e-5,
        higher_is_worse = True,
        source_layer    = 2,
        layer_key       = "joule_heating_Wm3",
        couplings       = ["atmo_circulation", "thermosphere_winds"],
        notes           = "High joule heating drives thermosphere expansion — satellite drag changes"
    ),

    "iono_schumann_shift": AssumptionBoundary(
        name            = "Schumann Resonance Frequency Shift",
        parameter       = "schumann_f1_shift_hz",
        units           = "Hz",
        green_range     = (-0.05, 0.05),
        yellow_range    = (-0.2, 0.2),
        red_threshold   = 0.5,
        higher_is_worse = True,
        source_layer    = 2,
        layer_key       = "schumann_f1_shift_hz",
        couplings       = ["atmo_lightning", "iono_height"],
        notes           = "Shift encodes ionosphere height change from thermosphere warming"
    ),

    # ── LAYER 3 — ATMOSPHERE ──────────────────────────────────────────
    "atmo_ghg_forcing": AssumptionBoundary(
        name            = "GHG Radiative Forcing",
        parameter       = "GHG_forcing_Wm2",
        units           = "W/m²",
        green_range     = (0, 1.0),
        yellow_range    = (1.0, 4.5),
        red_threshold   = 4.5,
        higher_is_worse = True,
        source_layer    = 3,
        layer_key       = "GHG_forcing_Wm2",
        couplings       = ["hydro_SST", "bio_permafrost", "atmo_hadley"],
        rate_of_change  = 0.05,
        notes           = "4.5 W/m² = 2xCO2 forcing — nonlinear feedbacks dominate above"
    ),

    "atmo_net_forcing": AssumptionBoundary(
        name            = "Net Atmospheric Radiative Forcing",
        parameter       = "net_forcing_Wm2",
        units           = "W/m²",
        green_range     = (-1.0, 1.0),
        yellow_range    = (1.0, 3.7),
        red_threshold   = 3.7,
        higher_is_worse = True,
        source_layer    = 3,
        layer_key       = "net_forcing_Wm2",
        couplings       = ["hydro_OHC", "bio_NEP", "litho_ice_melt"],
        rate_of_change  = 0.04,
        notes           = "3.7 W/m² = 2xCO2 threshold for nonlinear climate response"
    ),

    "atmo_coriolis": AssumptionBoundary(
        name            = "Coriolis Parameter (f)",
        parameter       = "coriolis_f_rads",
        units           = "rad/s",
        green_range     = (8e-5, 1.2e-4),   # mid-latitude f range
        yellow_range    = (6e-5, 8e-5),
        red_threshold   = 5e-5,
        higher_is_worse = False,
        source_layer    = 3,
        layer_key       = "coriolis_f_rads",
        couplings       = ["atmo_jet_stream", "hydro_AMOC", "mag_rotation_coupling"],
        rate_of_change  = -1e-10,
        notes           = "f decreases as Earth slows — all geostrophic equations shift"
    ),

    "atmo_jet_shear": AssumptionBoundary(
        name            = "Jet Stream Thermal Wind Shear",
        parameter       = "jet_shear_proxy",
        units           = "m/s/m",
        green_range     = (-1e-3, -2e-4),   # negative = westerly shear
        yellow_range    = (-2e-4, 0),
        red_threshold   = 0,
        higher_is_worse = True,
        source_layer    = 3,
        layer_key       = "jet_shear_proxy",
        couplings       = ["atmo_blocking", "atmo_hadley", "bio_crop_yield"],
        rate_of_change  = 5e-6,
        notes           = "Shear → 0 means jet meanders freely — blocking, persistent extremes"
    ),

    "atmo_hadley_extent": AssumptionBoundary(
        name            = "Hadley Cell Poleward Extent",
        parameter       = "hadley_extent_deg",
        units           = "degrees latitude",
        green_range     = (25, 32),
        yellow_range    = (32, 38),
        red_threshold   = 38,
        higher_is_worse = True,
        source_layer    = 3,
        layer_key       = "hadley_extent_deg",
        couplings       = ["atmo_jet_stream", "bio_drought", "hydro_precip"],
        rate_of_change  = 0.3,
        notes           = "Expansion shifts subtropical dry belts poleward — desertification"
    ),

    "atmo_convection": AssumptionBoundary(
        name            = "Convective Instability",
        parameter       = "convection_active",
        units           = "boolean",
        green_range     = (0, 0),
        yellow_range    = (0, 1),
        red_threshold   = 1,
        higher_is_worse = True,
        source_layer    = 3,
        layer_key       = "convection_active",
        couplings       = ["iono_gravity_waves", "hydro_precipitation"],
        notes           = "Active convection = gravity wave source upward to ionosphere"
    ),

    # ── LAYER 4 — HYDROSPHERE ─────────────────────────────────────────
    "hydro_AMOC_collapse": AssumptionBoundary(
        name            = "AMOC Collapse Risk",
        parameter       = "AMOC_collapse_risk",
        units           = "boolean",
        green_range     = (0, 0),
        yellow_range    = (0, 1),
        red_threshold   = 1,
        higher_is_worse = True,
        source_layer    = 4,
        layer_key       = "AMOC_collapse_risk",
        couplings       = ["atmo_jet_stream", "bio_amazon", "hydro_SST_dist"],
        notes           = "IRREVERSIBLE threshold — collapse on human timescales"
    ),

    "hydro_AMOC_transport": AssumptionBoundary(
        name            = "AMOC Heat Transport",
        parameter       = "AMOC_heat_transport_W",
        units           = "W",
        green_range     = (1.0e15, 1.5e15),
        yellow_range    = (0.5e15, 1.0e15),
        red_threshold   = 0.5e15,
        higher_is_worse = False,
        source_layer    = 4,
        layer_key       = "AMOC_heat_transport_W",
        couplings       = ["atmo_north_atlantic", "bio_marine_productivity"],
        rate_of_change  = -2e13,
        notes           = "Heat transport decline = North Atlantic climate reorganization"
    ),

    "hydro_arctic_amplification": AssumptionBoundary(
        name            = "Arctic Amplification Temperature",
        parameter       = "arctic_amplification_K",
        units           = "K",
        green_range     = (0, 1.5),
        yellow_range    = (1.5, 3.0),
        red_threshold   = 4.0,
        higher_is_worse = True,
        source_layer    = 4,
        layer_key       = "arctic_amplification_K",
        couplings       = ["atmo_jet_shear", "bio_permafrost", "litho_ice_loss"],
        rate_of_change  = 0.15,
        notes           = "3x global mean — reduces pole-equator gradient, weakens jet"
    ),

    "hydro_ice_albedo": AssumptionBoundary(
        name            = "Ice-Albedo Feedback Forcing",
        parameter       = "ice_albedo_feedback_Wm2",
        units           = "W/m²",
        green_range     = (0, 0.5),
        yellow_range    = (0.5, 2.0),
        red_threshold   = 2.0,
        higher_is_worse = True,
        source_layer    = 4,
        layer_key       = "ice_albedo_feedback_Wm2",
        couplings       = ["atmo_net_forcing", "hydro_arctic_amplification"],
        rate_of_change  = 0.05,
        notes           = "Self-amplifying — more forcing from less ice"
    ),

    "hydro_committed_warming": AssumptionBoundary(
        name            = "Committed Warming Timescale",
        parameter       = "committed_warming_timescale_yr",
        units           = "years",
        green_range     = (0, 100),
        yellow_range    = (100, 300),
        red_threshold   = 300,
        higher_is_worse = True,
        source_layer    = 4,
        layer_key       = "committed_warming_timescale_yr",
        couplings       = ["atmo_GHG_forcing", "bio_ecosystem_response"],
        notes           = "Long timescale = forcing already locked in exceeds current manifestation"
    ),

    # ── LAYER 5 — LITHOSPHERE ─────────────────────────────────────────
    "litho_LOD_change": AssumptionBoundary(
        name            = "Length of Day Change",
        parameter       = "LOD_change_ms",
        units           = "milliseconds",
        green_range     = (-0.5, 0.5),
        yellow_range    = (0.5, 2.0),
        red_threshold   = 5.0,
        higher_is_worse = True,
        source_layer    = 5,
        layer_key       = "LOD_change_ms",
        couplings       = ["mag_rotation_coupling", "atmo_coriolis", "grid_frequency"],
        rate_of_change  = 0.02,
        notes           = "LOD change already measurable from Greenland melt — GPS precision"
    ),

    "litho_polar_drift": AssumptionBoundary(
        name            = "Polar Drift Rate",
        parameter       = "polar_drift_deg_yr",
        units           = "degrees/year",
        green_range     = (0, 0.005),
        yellow_range    = (0.005, 0.02),
        red_threshold   = 0.05,
        higher_is_worse = True,
        source_layer    = 5,
        layer_key       = "polar_drift_deg_yr",
        couplings       = ["mag_rotation_coupling", "litho_crustal_stress"],
        rate_of_change  = 0.001,
        notes           = "GPS already detects polar shift matching Greenland melt signal"
    ),

    "litho_fault_stress": AssumptionBoundary(
        name            = "Sea Level Load Fault Coulomb Stress",
        parameter       = "fault_coulomb_change_Pa",
        units           = "Pa",
        green_range     = (-1e4, 1e4),
        yellow_range    = (1e4, 1e5),
        red_threshold   = 1e5,
        higher_is_worse = True,
        source_layer    = 5,
        layer_key       = "fault_coulomb_change_Pa",
        couplings       = ["litho_seismicity", "hydro_SLR"],
        notes           = "Sea level load redistributes stress — same physics as reservoir seismicity"
    ),

    "litho_volcanic_enhancement": AssumptionBoundary(
        name            = "Volcanic Activity Enhancement",
        parameter       = "volcanic_enhancement",
        units           = "multiplier",
        green_range     = (0.8, 1.2),
        yellow_range    = (1.2, 2.0),
        red_threshold   = 3.0,
        higher_is_worse = True,
        source_layer    = 5,
        layer_key       = "volcanic_enhancement",
        couplings       = ["atmo_AOD", "bio_photosynthesis", "litho_CO2_outgas"],
        rate_of_change  = 0.02,
        notes           = "Ice unloading enhances volcanism — Iceland 30-50x post-glacial"
    ),

    # ── LAYER 6 — BIOSPHERE ──────────────────────────────────────────
    "bio_NEP_sink": AssumptionBoundary(
        name            = "Net Ecosystem Productivity (carbon sink)",
        parameter       = "NEP_carbon_sink",
        units           = "boolean",
        green_range     = (1, 1),   # True = sink
        yellow_range    = (0, 1),
        red_threshold   = 0,        # False = source
        higher_is_worse = False,
        source_layer    = 6,
        layer_key       = "NEP_carbon_sink",
        couplings       = ["atmo_CO2_growth", "bio_permafrost", "bio_amazon"],
        notes           = "Ecosystem flips to carbon source — self-amplifying loop initiates"
    ),

    "bio_permafrost_flux": AssumptionBoundary(
        name            = "Permafrost Carbon Flux",
        parameter       = "permafrost_CO2_GtC_yr",
        units           = "GtC/year",
        green_range     = (0, 0.5),
        yellow_range    = (0.5, 1.5),
        red_threshold   = 1.5,
        higher_is_worse = True,
        source_layer    = 6,
        layer_key       = "permafrost_CO2_GtC_yr",
        couplings       = ["atmo_GHG_forcing", "bio_CH4", "hydro_arctic"],
        rate_of_change  = 0.08,
        notes           = "Self-amplifying, irreversible at scale — 1.5T tonnes C frozen"
    ),

    "bio_permafrost_CH4": AssumptionBoundary(
        name            = "Permafrost Methane Flux",
        parameter       = "permafrost_CH4_GtC_yr",
        units           = "GtC/year",
        green_range     = (0, 0.05),
        yellow_range    = (0.05, 0.2),
        red_threshold   = 0.2,
        higher_is_worse = True,
        source_layer    = 6,
        layer_key       = "permafrost_CH4_GtC_yr",
        couplings       = ["atmo_GHG_forcing", "bio_permafrost_flux"],
        rate_of_change  = 0.01,
        notes           = "CH4 GWP 28x CO2 — small flux = large forcing"
    ),

    "bio_ocean_pH": AssumptionBoundary(
        name            = "Ocean pH",
        parameter       = "ocean_pH",
        units           = "pH units",
        green_range     = (8.05, 8.20),
        yellow_range    = (7.95, 8.05),
        red_threshold   = 7.95,
        higher_is_worse = False,
        source_layer    = 6,
        layer_key       = "ocean_pH",
        couplings       = ["bio_coral", "bio_marine_productivity", "bio_ocean_carbon"],
        rate_of_change  = -0.002,
        notes           = "26% more acidic since industrial — aragonite saturation threshold"
    ),

    "bio_coral_dissolution": AssumptionBoundary(
        name            = "Coral Dissolution Active",
        parameter       = "coral_dissolution_active",
        units           = "boolean",
        green_range     = (0, 0),
        yellow_range    = (0, 1),
        red_threshold   = 1,
        higher_is_worse = True,
        source_layer    = 6,
        layer_key       = "coral_dissolution_active",
        couplings       = ["bio_ocean_pH", "bio_marine_productivity"],
        notes           = "Once aragonite saturation < 1.0 — structural dissolution begins"
    ),

    "bio_marine_productivity": AssumptionBoundary(
        name            = "Marine Productivity Change",
        parameter       = "marine_productivity_change_frac",
        units           = "fraction",
        green_range     = (-0.05, 0.05),
        yellow_range    = (-0.2, -0.05),
        red_threshold   = -0.2,
        higher_is_worse = False,
        source_layer    = 6,
        layer_key       = "marine_productivity_change_frac",
        couplings       = ["hydro_stratification", "bio_ocean_carbon", "bio_food_web"],
        rate_of_change  = -0.005,
        notes           = "Ocean produces 50% of Earth's O2 — stratification already reducing"
    ),

    "bio_amazon_tipping": AssumptionBoundary(
        name            = "Amazon Tipping Point Proximity",
        parameter       = "amazon_tipping_proximity",
        units           = "fraction (0=stable, 1=tipped)",
        green_range     = (0, 0.4),
        yellow_range    = (0.4, 0.7),
        red_threshold   = 0.8,
        higher_is_worse = True,
        source_layer    = 6,
        layer_key       = "amazon_tipping_proximity",
        couplings       = ["bio_NEP_sink", "atmo_CO2_growth", "hydro_SA_precip"],
        rate_of_change  = 0.03,
        notes           = "~20% cleared now, threshold ~25-40% — interaction with drought/fire"
    ),

    "bio_co2_accumulation": AssumptionBoundary(
        name            = "Atmospheric CO₂ Accumulation Rate",
        parameter       = "atmospheric_CO2_accumulation",
        units           = "ppm/year",
        green_range     = (0, 0.5),
        yellow_range    = (0.5, 3.0),
        red_threshold   = 3.5,
        higher_is_worse = True,
        source_layer    = 6,
        layer_key       = "atmospheric_CO2_accumulation",
        couplings       = ["atmo_GHG_forcing", "bio_permafrost_flux", "bio_amazon_tipping"],
        rate_of_change  = 0.05,
        notes           = "Sinks absorbing only 45% of anthropogenic emissions"
    ),

    "bio_planetary_boundaries": AssumptionBoundary(
        name            = "Planetary Boundaries Crossed",
        parameter       = "planetary_boundaries_crossed",
        units           = "count (of 9)",
        green_range     = (0, 2),
        yellow_range    = (2, 5),
        red_threshold   = 6,
        higher_is_worse = True,
        source_layer    = 6,
        layer_key       = "planetary_boundaries_crossed",
        couplings       = ["all"],
        rate_of_change  = 0.1,
        notes           = "Interaction effects between crossed boundaries unquantified"
    ),
}


# ─────────────────────────────────────────────
# COUPLING GRAPH
# Which assumptions propagate failure to which others
# ─────────────────────────────────────────────

COUPLING_GRAPH: Dict[str, List[str]] = {
    "mag_rotation_coupling":    ["atmo_coriolis", "litho_LOD_change", "grid_frequency"],
    "litho_LOD_change":         ["mag_rotation_coupling", "atmo_coriolis"],
    "atmo_coriolis":            ["atmo_jet_shear", "hydro_AMOC_transport", "atmo_hadley_extent"],
    "atmo_jet_shear":           ["bio_crop_yield", "atmo_blocking", "atmo_hadley_extent"],
    "atmo_ghg_forcing":         ["hydro_SST", "bio_permafrost_flux", "hydro_arctic_amplification"],
    "hydro_AMOC_collapse":      ["atmo_jet_shear", "bio_amazon_tipping", "hydro_SST_dist"],
    "hydro_AMOC_transport":     ["atmo_net_forcing", "bio_marine_productivity"],
    "hydro_arctic_amplification": ["atmo_jet_shear", "bio_permafrost_flux", "litho_ice_loss"],
    "hydro_ice_albedo":         ["atmo_net_forcing", "hydro_arctic_amplification"],
    "bio_permafrost_flux":      ["atmo_ghg_forcing", "bio_permafrost_CH4", "bio_co2_accumulation"],
    "bio_permafrost_CH4":       ["atmo_ghg_forcing", "bio_permafrost_flux"],
    "bio_NEP_sink":             ["bio_co2_accumulation", "bio_permafrost_flux", "bio_amazon_tipping"],
    "bio_amazon_tipping":       ["bio_NEP_sink", "atmo_ghg_forcing", "hydro_SA_precip"],
    "bio_ocean_pH":             ["bio_coral_dissolution", "bio_marine_productivity"],
    "bio_marine_productivity":  ["bio_co2_accumulation", "bio_food_web"],
    "litho_volcanic_enhancement": ["atmo_net_forcing", "bio_marine_productivity"],
}


# ─────────────────────────────────────────────
# REGISTRY READER
# Reads layer coupling_state outputs and returns full assessment
# ─────────────────────────────────────────────

def assess_from_layer_states(layer_states: Dict[int, Dict]) -> Dict[str, Dict]:
    """
    Read all layer coupling_state outputs and return assumption assessments.
    layer_states : dict keyed by layer number (0-6) containing coupling_state output
    returns      : dict keyed by assumption ID with full assessment
    """
    results = {}

    for assumption_id, boundary in REGISTRY.items():
        layer_output = layer_states.get(boundary.source_layer, {})
        value = layer_output.get(boundary.layer_key)

        if value is None:
            results[assumption_id] = {
                "id":      assumption_id,
                "name":    boundary.name,
                "status":  "UNKNOWN",
                "value":   None,
                "message": f"Key '{boundary.layer_key}' not found in layer {boundary.source_layer} output",
            }
            continue

        # Boolean handling
        if isinstance(value, bool):
            numeric = 1.0 if value else 0.0
        elif isinstance(value, str):
            results[assumption_id] = {
                "id":      assumption_id,
                "name":    boundary.name,
                "status":  "INFO",
                "value":   value,
                "message": value,
            }
            continue
        else:
            numeric = float(value)

        risk, penalty, proximity = boundary.assess(numeric)

        results[assumption_id] = {
            "id":               assumption_id,
            "name":             boundary.name,
            "status":           risk.value,
            "value":            numeric,
            "units":            boundary.units,
            "confidence_penalty": penalty,
            "proximity_to_red": proximity,
            "green_range":      boundary.green_range,
            "red_threshold":    boundary.red_threshold,
            "couplings":        boundary.couplings,
            "notes":            boundary.notes,
            "source_layer":     boundary.source_layer,
            "layer_key":        boundary.layer_key,
        }

    return results


def global_confidence_multiplier(assessments: Dict[str, Dict]) -> float:
    """
    Compute overall confidence multiplier across all assessed assumptions.
    Product of (1 - penalty) for all assumptions with numeric penalties.
    """
    multiplier = 1.0
    for data in assessments.values():
        penalty = data.get("confidence_penalty", 0.0)
        if isinstance(penalty, (int, float)):
            multiplier *= (1.0 - penalty)
    return max(0.0, multiplier)


def detect_cascade_risk(assessments: Dict[str, Dict]) -> Dict:
    """
    Detect convergence of failures across coupled assumptions.
    Returns cascade level and active coupling pathways.
    """
    yellow = [k for k, v in assessments.items() if v.get("status") == "YELLOW"]
    red    = [k for k, v in assessments.items() if v.get("status") == "RED"]

    # Find coupled pairs both degraded
    coupled_degraded = []
    degraded_set = set(yellow + red)
    for src, targets in COUPLING_GRAPH.items():
        if src in degraded_set:
            for tgt in targets:
                if tgt in degraded_set:
                    coupled_degraded.append((src, tgt))

    # Deduplicate
    coupled_degraded = list(set(
        tuple(sorted(pair)) for pair in coupled_degraded
    ))

    n_red    = len(red)
    n_yellow = len(yellow)
    n_coupled= len(coupled_degraded)

    if n_red >= 3 or (n_red >= 2 and n_coupled >= 2):
        level   = "CRITICAL"
        message = "System entering unknown state — multiple coupled assumptions have left stable regime"
    elif n_red >= 1 and n_coupled >= 2:
        level   = "HIGH"
        message = "Cascade propagating — one RED assumption driving coupled YELLOWs"
    elif n_coupled >= 3:
        level   = "MODERATE"
        message = "Multiple coupled assumption pairs degrading simultaneously"
    elif n_yellow >= 4:
        level   = "LOW"
        message = "Broad degradation across assumptions — monitor coupling"
    else:
        level   = "MINIMAL"
        message = "No cascade convergence detected"

    irreversible = [k for k in red if "IRREVERSIBLE" in REGISTRY.get(k, AssumptionBoundary(
        "", "", "", (0,1), (0,1), 0, True, 0, "", notes="")).notes.upper()]

    return {
        "cascade_level":       level,
        "message":             message,
        "red_assumptions":     red,
        "yellow_assumptions":  yellow,
        "coupled_degraded":    coupled_degraded,
        "irreversible_active": irreversible,
        "n_red":               n_red,
        "n_yellow":            n_yellow,
        "n_coupled_pairs":     n_coupled,
    }


def full_report(layer_states: Dict[int, Dict]) -> Dict:
    """
    Single call: layer states in, full validity report out.
    """
    assessments  = assess_from_layer_states(layer_states)
    multiplier   = global_confidence_multiplier(assessments)
    cascade      = detect_cascade_risk(assessments)

    return {
        "assumptions":                  assessments,
        "global_confidence_multiplier": multiplier,
        "cascade":                      cascade,
        "summary": {
            "total":   len(assessments),
            "green":   len([v for v in assessments.values() if v.get("status") == "GREEN"]),
            "yellow":  len([v for v in assessments.values() if v.get("status") == "YELLOW"]),
            "red":     len([v for v in assessments.values() if v.get("status") == "RED"]),
            "unknown": len([v for v in assessments.values() if v.get("status") == "UNKNOWN"]),
        }
    }
