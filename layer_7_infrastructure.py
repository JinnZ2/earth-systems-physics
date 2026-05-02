# layer_7_infrastructure.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Layer 7: Built infrastructure (long pipelines, transmission grid).
# Sits ABOVE Layer 6 in the cascade. Consumes upstream EM forcing —
# specifically dB/dt at the surface, soil resistivity from Layer 5,
# and the asset-condition variables (coating defect fraction,
# transformer thresholds) — and reports infrastructure stress
# indicators. It is purely a sink: no feedback to Earth-system
# layers.
#
# Damage couples through three multiplicative factors identified in
# the design memo:
#       GIC current  x  coating defect fraction  x  inverse soil rho
# These are the levers operators actually have. The first is set by
# space weather and ground conductivity; the second and third by
# asset maintenance and siting.

import numpy as np
from scipy.constants import mu_0

# ─────────────────────────────────────────────
# CONSTANTS — ASSET / SOIL / ELECTROCHEMISTRY
# ─────────────────────────────────────────────

L_PIPE_DEFAULT          = 1000e3     # m   characteristic pipe length
SOIL_RHO_DEFAULT        = 100.0      # ohm·m  typical soil
COATING_DEFECT_DEFAULT  = 1e-3       # 0.1% breakdown — well-maintained pipe

# Faraday's electrochemical equivalent for Fe(II) loss:
#   k_Fe = M_Fe / (z F) = 55.845e-3 / (2 * 96485) ~ 2.894e-7 kg/C
FARADAY_FE              = 2.894e-7

# Default characteristic angular frequency of the geomagnetic
# disturbance feeding GIC. ~1e-2 rad/s corresponds to a 10-minute
# period — squarely in the Pc5 / substorm band that dominates GIC.
OMEGA_EFF_DEFAULT       = 1e-2       # rad/s

# Empirical network transfer (Boteler 1994 / Pirjola): the GIC
# current per unit horizontal E-field is essentially set by network
# topology, not by bulk-conductor resistance. 5-100 A per (V/km) is
# the observed range for major North American pipelines and grids.
GIC_TRANSFER_A_PER_V_PER_KM_DEFAULT = 50.0
GIC_REFERENCE_LENGTH_KM             = 1000.0   # normalising length
                                                # for sqrt(L) scaling

# Reference scales for the dimensionless damage index
I_GIC_REF_A             = 50.0       # A     modest storm current
DEFECT_REF              = 1e-3       # baseline coating-defect fraction
SOIL_RHO_REF            = 100.0      # ohm·m baseline soil resistivity


# ─────────────────────────────────────────────
# GROUND ELECTRIC FIELD
# Plane-wave / uniform half-space surface impedance.
# Dimensionally correct form needs the disturbance frequency.
# ─────────────────────────────────────────────

def ground_electric_field(dB_dt_Ts,
                          soil_rho_ohm_m=SOIL_RHO_DEFAULT,
                          omega_rads=OMEGA_EFF_DEFAULT):
    """
    Horizontal surface electric field induced by a time-varying B.
    Plane-wave approximation with uniform half-space, surface
    impedance Z = sqrt(j omega mu_0 / sigma):
        |E| = |dB/dt| * sqrt(2 rho / (omega mu_0))     [V/m]
    dB_dt_Ts        : geomagnetic time derivative (T/s)
    soil_rho_ohm_m  : soil resistivity (ohm·m)
    omega_rads      : characteristic angular frequency (rad/s).
                       Default 1e-2 rad/s ~ 10 min period (GIC band).
    returns: |E_horizontal| at the surface (V/m)
    """
    if soil_rho_ohm_m <= 0 or omega_rads <= 0:
        return 0.0
    return float(abs(dB_dt_Ts) * np.sqrt(2 * soil_rho_ohm_m
                                         / (omega_rads * mu_0)))


def gic_current(E_ground_Vm,
                L_m=L_PIPE_DEFAULT,
                transfer_A_per_V_per_km=GIC_TRANSFER_A_PER_V_PER_KM_DEFAULT):
    """
    Geomagnetically induced current along a long conductor, using
    the empirical network-transfer form (Boteler 1994 / Pirjola):
        I_GIC ~ K * E_horizontal * sqrt(L / L_ref)
    K (transfer_A_per_V_per_km) lumps the grounded-network topology;
    pure series-resistance models give answers orders of magnitude
    too large because real pipelines / grids leak current to soil
    at every grounded substation.
    E_ground_Vm                : induced surface E-field (V/m)
    L_m                        : asset length (m)
    transfer_A_per_V_per_km    : empirical transfer (A per V/km)
    returns: GIC current magnitude (A)
    """
    E_V_per_km = E_ground_Vm * 1000.0
    L_km       = max(L_m, 0.0) / 1000.0
    length_factor = np.sqrt(L_km / GIC_REFERENCE_LENGTH_KM)
    return abs(E_V_per_km) * transfer_A_per_V_per_km * length_factor


# ─────────────────────────────────────────────
# CORROSION (Faraday's law of electrolysis)
# ─────────────────────────────────────────────

def corrosion_mass_rate(I_GIC_A, coating_defect_fraction=COATING_DEFECT_DEFAULT):
    """
    Pipe-wall iron mass loss rate from electrochemical corrosion at
    coating defects.
        dm/dt = (M_Fe / z F) * I_defect
        I_defect = I_GIC * coating_defect_fraction
    The coating-defect fraction is the fraction of pipe surface
    where current can exit to soil; healthy coating restricts it
    to <0.1%.
    I_GIC_A                 : pipe current magnitude (A)
    coating_defect_fraction : 0..1
    returns: mass loss rate (kg Fe / s)
    """
    return abs(I_GIC_A) * coating_defect_fraction * FARADAY_FE


def damage_rate_index(I_GIC_A, coating_defect_fraction, soil_rho_ohm_m):
    """
    Composite damage-rate index combining the three multiplicative
    factors from the design memo:
        damage ~  (I_GIC / I_ref)
                * (defect / defect_ref)
                * (rho_ref / rho_soil)
    Lower soil resistivity worsens damage (more current finds soil).
    Dimensionless; 1.0 corresponds to a 50 A storm on a 0.1%-defect
    pipe in 100 ohm·m soil.
    """
    if soil_rho_ohm_m <= 0:
        return 0.0
    I_norm      = abs(I_GIC_A) / I_GIC_REF_A
    defect_norm = coating_defect_fraction / DEFECT_REF
    soil_norm   = SOIL_RHO_REF / soil_rho_ohm_m
    return I_norm * defect_norm * soil_norm


# ─────────────────────────────────────────────
# TRANSFORMER STRESS
# ─────────────────────────────────────────────

def transformer_half_cycle_saturation_risk(I_GIC_A, I_threshold_A=10.0):
    """
    Quasi-DC GIC drives transformer cores into half-cycle saturation,
    producing harmonic distortion, var demand, and core overheating.
    Heuristic risk:
        risk = 1 - exp(-|I| / I_threshold)
    I_GIC_A       : neutral DC current (A)
    I_threshold_A : transformer-class threshold (A; ~10 A typical
                    for large GSU banks)
    returns: 0..1 saturation risk
    """
    return 1.0 - np.exp(-abs(I_GIC_A) / I_threshold_A)


# ─────────────────────────────────────────────
# COUPLING INTERFACE
# ─────────────────────────────────────────────

def coupling_state(dB_dt_Ts=0.0,
                   soil_rho_ohm_m=SOIL_RHO_DEFAULT,
                   coating_defect_fraction=COATING_DEFECT_DEFAULT,
                   asset_length_m=L_PIPE_DEFAULT,
                   omega_rads=OMEGA_EFF_DEFAULT,
                   transfer_A_per_V_per_km=GIC_TRANSFER_A_PER_V_PER_KM_DEFAULT,
                   transformer_threshold_A=10.0):
    """
    Layer 7 state vector — infrastructure stress under upstream forcing.
    dB_dt_Ts                : surface dB/dt from L0/L1/L2 cascade (T/s)
    soil_rho_ohm_m          : ground resistivity (ohm·m) from L5
    coating_defect_fraction : asset-condition input (0..1)
    asset_length_m          : characteristic conductor length (m)
    omega_rads              : disturbance frequency for surface impedance
    transfer_A_per_V_per_km : empirical GIC network transfer (A per V/km)
    transformer_threshold_A : GIC saturation threshold (A)
    returns: dict of infrastructure stress indicators
    """
    E_ground = ground_electric_field(dB_dt_Ts, soil_rho_ohm_m, omega_rads)
    I_GIC    = gic_current(E_ground,
                           L_m=asset_length_m,
                           transfer_A_per_V_per_km=transfer_A_per_V_per_km)
    corrosion= corrosion_mass_rate(I_GIC, coating_defect_fraction)
    damage   = damage_rate_index(I_GIC, coating_defect_fraction, soil_rho_ohm_m)
    sat_risk = transformer_half_cycle_saturation_risk(I_GIC,
                                                      transformer_threshold_A)

    return {
        "ground_E_field_Vm":             E_ground,
        "ground_E_field_V_per_km":       E_ground * 1000.0,
        "gic_current_A":                 I_GIC,
        "corrosion_mass_rate_kg_s":      corrosion,
        "corrosion_mass_rate_kg_yr":     corrosion * 3.15576e7,
        "damage_rate_index":             damage,
        "transformer_saturation_risk":   float(sat_risk),
        "transformer_at_risk":           bool(sat_risk > 0.5),
        "soil_rho_ohm_m":                soil_rho_ohm_m,
        "coating_defect_fraction":       coating_defect_fraction,
        "asset_length_m":                asset_length_m,
        "dB_dt_Ts":                      dB_dt_Ts,
        "omega_rads":                    omega_rads,
        "cascade_from_ionosphere":       "Hall + Pedersen current sheets -> dB/dt at surface",
        "cascade_from_lithosphere":      "soil resistivity sets ground E-field magnitude",
        "cascade_from_orbital":          "secular dipole drift adjusts baseline B used by L2 conductivity",
        "note": "Layer 7 is a downstream sink — no feedback to Earth-system layers"
    }
