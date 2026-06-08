# earth_physics_constraints.py
# repo: earth-systems-physics   CC0   stdlib only   phone-buildable
# Plugs into constraint_RFL_geometry.py v5.
#
# Every layer = flux_in -> store -> flux_out.
#   conservation law  -> Constraint op "≈" on emerged fluxes  (balance must hold)
#   instability gate  -> Constraint op ">"/"<" on emerged term (threshold flips basin)
#   cross-substrate    -> Coupling / OscillationCoupling / FuncCoupling
#
# Bounds below are CLAIMS, not tuning knobs. Field data refutes -> edit the claim.

import math
from dataclasses import dataclass
from constraint_RFL_geometry import (
    Space, Hypothesis, Constraint, Coupling, OscillationCoupling,
    CompoundHypothesis, Tournament
)

# ============================================================
# 0. GENERAL NONLINEAR COUPLING  (carries T^4, ln, sqrt, ^(1/6))
# ============================================================
@dataclass
class FuncCoupling:
    name: str
    input_axes: list
    output_axis: str
    fn: object                      # lambda(dict) -> float
    def compute(self, base_point: dict) -> float:
        return self.fn(base_point)

# ============================================================
# 1. PHYSICAL CONSTANTS
# ============================================================
S0    = 1361.0          # solar constant            W/m^2
SIGMA = 5.670e-8        # Stefan-Boltzmann          W/m^2/K^4
MU0   = 4*math.pi*1e-7  # vacuum permeability       H/m
G     = 9.81            # gravity                   m/s^2
CP    = 1004.0          # air heat capacity         J/kg/K
MP    = 1.673e-27       # proton mass               kg
R_E   = 6.371e6         # Earth radius              m

# ============================================================
# 2. CLAIMS  (falsifiable bounds -> NOAA / IERS / GRACE-FO adapters)
# ============================================================
CLAIMS = {
    "EEI_max":        1.5,    # top-of-atmosphere energy imbalance ceiling   W/m^2
    "lapse_dry":      9.76,   # dry adiabatic lapse  g/cp                     K/km
    "magpause_min":   6.0,    # min magnetopause standoff before strip risk   R_E
    "fp_hf_floor":    3.0e6,  # ionospheric F-layer plasma freq HF floor      Hz
    "amoc_fw_thresh": 0.10,   # freshwater hosing -> AMOC salt-advection flip  Sv-norm
    "mc_failure":     0.0,    # Mohr-Coulomb: shear must stay below strength   Pa
    "co2_holocene_hi":280.0,  # pre-industrial Holocene CO2 ceiling           ppm
    "npp_sink_floor": 0.0,    # net biosphere C uptake must stay >= 0
    "q_core_max":     0.8,    # core resonance Q ceiling (your v5)
}

@dataclass
class LayerSpec:
    axes: list
    couplings: list
    constraints: list
    note: str = ""

# ============================================================
# 3.  EM BASE  (geomagnetic dynamo)
#     store: B-field energy.  out: drives magnetopause standoff.
# ============================================================
def layer_em():
    axes = ["B_surface", "dipole_decay_rate", "B_energy_density"]
    couplings = [
        FuncCoupling("u_B", ["B_surface"], "B_energy_density",
                     lambda p: p["B_surface"]**2 / (2*MU0)),       # u = B^2/2mu0
    ]
    constraints = [
        # ∇·B = 0 is structural (no monopole) -> enforced by construction, not tested.
        Constraint("dipole_decay_bound", {"dipole_decay_rate":1.0}, 0.05, "<",
                   "secular decay < 5%/century or dynamo claim breaks"),
    ]
    return LayerSpec(axes, couplings, constraints, "EM dynamo: B^2 sets magnetic pressure")

# ============================================================
# 4.  MAGNETOSPHERE
#     pressure balance: B^2/2mu0 (compressed)  ==  rho_sw * v_sw^2  (dynamic)
#     standoff R_mp ~ (B_E^2 / (mu0 rho v^2))^(1/6)
# ============================================================
def layer_magnetosphere():
    axes = ["B_surface", "sw_density", "sw_velocity",
            "P_dyn", "magpause_standoff"]
    couplings = [
        FuncCoupling("P_dyn", ["sw_density","sw_velocity"], "P_dyn",
                     lambda p: p["sw_density"]*MP * p["sw_velocity"]**2),   # rho v^2
        FuncCoupling("standoff", ["B_surface","P_dyn"], "magpause_standoff",
                     lambda p: ( (p["B_surface"]**2)/(MU0 * max(p["P_dyn"],1e-30)) )**(1/6) / R_E
                               if p.get("P_dyn",0) > 0 else 0.0),
    ]
    constraints = [
        Constraint("magpause_floor", {"magpause_standoff":1.0},
                   CLAIMS["magpause_min"], ">",
                   "standoff < 6 R_E -> direct solar-wind atmospheric stripping"),
    ]
    return LayerSpec(axes, couplings, constraints, "pressure balance -> standoff distance")

# ============================================================
# 5.  IONOSPHERE
#     f_p = 8.98 * sqrt(n_e)   ; gates HF propagation & GIC coupling
# ============================================================
def layer_ionosphere():
    axes = ["electron_density", "plasma_freq"]
    couplings = [
        FuncCoupling("plasma_freq", ["electron_density"], "plasma_freq",
                     lambda p: 8.98 * math.sqrt(max(p["electron_density"],0.0))),
    ]
    constraints = [
        Constraint("hf_floor", {"plasma_freq":1.0}, CLAIMS["fp_hf_floor"], ">",
                   "f_p below HF floor -> ionosphere transparent, comms + shielding loss"),
    ]
    return LayerSpec(axes, couplings, constraints, "n_e -> plasma frequency gate")

# ============================================================
# 6.  ATMOSPHERE
#     radiative eq:   F_in = S0(1-a)/4   ==   F_out = sigma T^4   (+ CO2 forcing)
#     convective gate: env lapse > adiabatic -> unstable
# ============================================================
def layer_atmosphere():
    axes = ["albedo", "T_surface", "co2_ppm", "env_lapse",
            "F_in", "F_out", "F_co2", "EEI"]
    couplings = [
        FuncCoupling("F_in",  ["albedo"], "F_in",
                     lambda p: S0*(1-p["albedo"])/4),
        FuncCoupling("F_out", ["T_surface"], "F_out",
                     lambda p: SIGMA * p["T_surface"]**4),
        FuncCoupling("F_co2", ["co2_ppm"], "F_co2",
                     lambda p: 5.35*math.log(max(p["co2_ppm"],1.0)/280.0)),   # W/m^2
        FuncCoupling("EEI",   ["F_in","F_out","F_co2"], "EEI",
                     lambda p: (p["F_in"] + p["F_co2"]) - p["F_out"]),        # imbalance
    ]
    constraints = [
        Constraint("radiative_balance", {"EEI":1.0}, CLAIMS["EEI_max"], "<",
                   "|TOA imbalance| > 1.5 W/m^2 -> forced disequilibrium, energy accumulating"),
        Constraint("convective_stability", {"env_lapse":1.0}, CLAIMS["lapse_dry"], "<",
                   "env lapse > dry adiabatic -> absolute instability"),
    ]
    return LayerSpec(axes, couplings, constraints, "TOA flux balance + lapse-rate gate")

# ============================================================
# 7.  HYDROSPHERE
#     Clausius-Clapeyron vapor (~7%/K), AMOC salt-advection flip (Stommel)
#     ice melt -> freshwater -> AMOC ; ice mass -> lithosphere load
# ============================================================
def layer_hydrosphere():
    axes = ["dT", "ice_melt_rate", "freshwater_flux",
            "vapor_capacity", "amoc_strength", "ice_mass_anomaly"]
    couplings = [
        FuncCoupling("vapor_capacity", ["dT"], "vapor_capacity",
                     lambda p: 1.0 * (1.07 ** p["dT"])),                      # CC ~7%/K
        FuncCoupling("freshwater_flux", ["ice_melt_rate"], "freshwater_flux",
                     lambda p: p["ice_melt_rate"]),
        # AMOC: advective strength minus freshwater suppression (linearized Stommel)
        FuncCoupling("amoc_strength", ["freshwater_flux"], "amoc_strength",
                     lambda p: max(0.0, 1.0 - p["freshwater_flux"]/CLAIMS["amoc_fw_thresh"])),
    ]
    constraints = [
        Constraint("amoc_on", {"amoc_strength":1.0}, 0.0, ">",
                   "amoc -> 0 : salt-advection feedback collapses overturning"),
        Constraint("fw_hosing", {"freshwater_flux":1.0}, CLAIMS["amoc_fw_thresh"], "<",
                   "freshwater flux past hosing threshold flips basin"),
    ]
    return LayerSpec(axes, couplings, constraints, "CC vapor + AMOC freshwater gate")

# ============================================================
# 8.  LITHOSPHERE
#     isostasy / GIA: ice unload -> mantle strain (feeds your v5 emergent axis)
#     Mohr-Coulomb: tau = c + sigma_n tan(phi) ; failure when shear exceeds
# ============================================================
def layer_lithosphere():
    axes = ["ice_mass_anomaly", "cohesion", "normal_stress", "fric_angle",
            "shear_stress", "mantle_strain_memory", "rotational_coupling_efficiency",
            "shear_excess", "emergent_mantle_anomaly"]
    couplings = [
        # GIA: removing ice load drives strain (your existing emergent axis, now grounded)
        FuncCoupling("strain_from_unload", ["ice_mass_anomaly"], "mantle_strain_memory",
                     lambda p: 0.8 * p["ice_mass_anomaly"]),
        # Mohr-Coulomb strength vs applied shear
        FuncCoupling("mc_excess",
                     ["shear_stress","cohesion","normal_stress","fric_angle"],
                     "shear_excess",
                     lambda p: p["shear_stress"]
                               - (p["cohesion"] + p["normal_stress"]*math.tan(p["fric_angle"]))),
        # ice+strain feed rotational coupling -> your v5 core resonance input
        Coupling("rot_coupling",
                 ["ice_mass_anomaly","mantle_strain_memory"],
                 "rotational_coupling_efficiency", coeff=0.6, op="product"),
        Coupling("mantle_anomaly",
                 ["ice_mass_anomaly","mantle_strain_memory","rotational_coupling_efficiency"],
                 "emergent_mantle_anomaly", coeff=3.0, op="product"),
    ]
    constraints = [
        Constraint("mohr_coulomb", {"shear_excess":1.0}, CLAIMS["mc_failure"], "<",
                   "shear_excess > 0 -> brittle failure / seismic release"),
    ]
    return LayerSpec(axes, couplings, constraints, "GIA strain + brittle-failure gate")

# ============================================================
# 9.  CORE  (your v5 oscillation, now bottom of the cascade)
# ============================================================
def layer_core():
    axes = ["core_osc_frequency","core_osc_phase","core_q_factor",
            "core_resonant_amplitude"]
    couplings = [
        OscillationCoupling("core_resonance",
                            "core_osc_frequency","core_osc_phase","core_q_factor",
                            "core_resonant_amplitude", base_amplitude=1.0),
    ]
    constraints = [
        Constraint("q_ceiling", {"core_q_factor":1.0}, CLAIMS["q_core_max"], "<",
                   "Q above physical ceiling = unbounded ringing, unphysical"),
    ]
    return LayerSpec(axes, couplings, constraints, "rotational coupling -> core resonance")

# ============================================================
# 10. BIOSPHERE
#     C sink:  uptake(NPP) - release(respiration Q10) >= 0 ; CO2 baseline gate
# ============================================================
def layer_biosphere():
    axes = ["npp", "respiration", "dT", "co2_ppm", "net_c_uptake"]
    couplings = [
        FuncCoupling("resp_q10", ["respiration","dT"], "respiration_eff",
                     lambda p: p["respiration"] * (2.0 ** (p["dT"]/10.0))),   # Q10=2
        FuncCoupling("net_c", ["npp","respiration","dT"], "net_c_uptake",
                     lambda p: p["npp"] - p["respiration"]*(2.0**(p["dT"]/10.0))),
    ]
    constraints = [
        Constraint("sink_positive", {"net_c_uptake":1.0}, CLAIMS["npp_sink_floor"], ">",
                   "net uptake < 0 -> biosphere flips source, amplifies atmosphere layer"),
    ]
    return LayerSpec(axes, couplings, constraints, "NPP - Q10 respiration sink balance")

# ============================================================
# 11. ASSEMBLE FULL STACK  (cascade order, top -> core)
# ============================================================
def assemble_stack():
    layers = [
        ("em",            layer_em()),
        ("magnetosphere", layer_magnetosphere()),
        ("ionosphere",    layer_ionosphere()),
        ("atmosphere",    layer_atmosphere()),
        ("hydrosphere",   layer_hydrosphere()),
        ("lithosphere",   layer_lithosphere()),
        ("core",          layer_core()),
        ("biosphere",     layer_biosphere()),
    ]
    axes, couplings, constraints = [], [], []
    for _, L in layers:
        for a in L.axes:
            if a not in axes: axes.append(a)
        couplings += L.couplings
        constraints += L.constraints
    return Space(axes=axes), couplings, constraints, layers

# ============================================================
# 12. DEMO  -- present-ish vs CO2-forced, run cascade
# ============================================================
def demo():
    space, couplings, constraints, layers = assemble_stack()

    base_state = {
        "B_surface": 3.0e-5, "dipole_decay_rate": 0.02,
        "sw_density": 5e6, "sw_velocity": 4e5,
        "electron_density": 1e12,
        "albedo": 0.30, "T_surface": 288.0, "env_lapse": 6.5,
        "dT": 1.2, "ice_melt_rate": 0.04,
        "cohesion": 1e6, "normal_stress": 5e6, "fric_angle": 0.52,
        "shear_stress": 2e6,
        "ice_mass_anomaly": 0.4,
        "core_osc_frequency": 0.95, "core_osc_phase": 0.1, "core_q_factor": 0.6,
        "npp": 60.0, "respiration": 55.0,
    }

    def run(label, co2, melt):
        coords = dict(base_state); coords["co2_ppm"] = co2; coords["ice_melt_rate"] = melt
        bases = [Hypothesis("seed", coords, {a:0.05 for a in coords})]
        cmpd  = CompoundHypothesis(label, bases, couplings).emerge()
        t = Tournament(space, [cmpd], constraints).run()
        print(f"\n[{label}]  CO2={co2} melt={melt}")
        for k in ["EEI","amoc_strength","emergent_mantle_anomaly",
                  "shear_excess","net_c_uptake","magpause_standoff"]:
            print(f"   {k:24s} = {cmpd.coords.get(k,0):.4g}")
        if t["killed"]:
            for kill in t["killed"]:
                for v in kill["violations"]:
                    print(f"   KILLED by {v['constraint']}  viol={v['violation']}")
        else:
            print("   ALL CONSTRAINTS PASS")

    print("=== EARTH PHYSICS CASCADE ===")
    run("holocene",  280, 0.01)
    run("forced",    420, 0.04)
    run("hosing",    500, 0.12)

if __name__ == "__main__":
    demo()
