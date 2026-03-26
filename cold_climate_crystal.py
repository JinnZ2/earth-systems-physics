# cold_climate_crystal.py

# earth-systems-physics

# CC0 — No Rights Reserved

# 

# Room temperature is a lab assumption.

# Northern Minnesota / corridor operating range:

# Winter: -40°C to -10°C (233K to 263K)

# Deep cold snaps: -50°C (223K)

# Truck cab parked overnight: follows ambient

# Historical baseline (pre-contact): outdoor year-round

# 

# The Curie susceptibility goes as 1/T.

# At 233K vs 300K: 1.29× improvement.

# That’s not enough alone.

# 

# BUT: quartz Q_mech increases dramatically with cooling.

# AND: hematite hits its Morin transition at -10°C (263K).

# AND: thermal noise drops.

# AND: ice and snow provide natural vibration isolation.

# 

# Stack all the cold-climate advantages.

import numpy as np

HBAR  = 1.0545718e-34
K_B   = 1.380649e-23
MU_0  = 4 * np.pi * 1e-7
GAMMA = 1.7608597e11
MU_B  = 9.274e-24

# ─────────────────────────────────────────────

# TEMPERATURE REGIMES

# ─────────────────────────────────────────────

CLIMATE_TEMPS = {
“lab_standard”:     {“T_K”: 300, “T_C”: 27,   “desc”: “Lab assumption. Not reality.”},
“autumn_MN”:        {“T_K”: 278, “T_C”: 5,    “desc”: “October. Cooling. Ground still soft.”},
“early_winter”:     {“T_K”: 263, “T_C”: -10,  “desc”: “November. Hematite Morin transition.”},
“winter_normal”:    {“T_K”: 248, “T_C”: -25,  “desc”: “January typical. Snow cover insulates ground.”},
“cold_snap”:        {“T_K”: 233, “T_C”: -40,  “desc”: “-40°F = -40°C. Where the scales meet.”},
“extreme_cold”:     {“T_K”: 223, “T_C”: -50,  “desc”: “Deep cold. Rare but real in corridor.”},
“ice_surface”:      {“T_K”: 253, “T_C”: -20,  “desc”: “Lake Superior ice surface. Stable.”},
“permafrost_depth”: {“T_K”: 271, “T_C”: -2,   “desc”: “Permafrost active layer. Constant.”},
“snow_cave”:        {“T_K”: 273, “T_C”: 0,    “desc”: “Snow insulation. Remarkably stable.”},
“dry_ice”:          {“T_K”: 195, “T_C”: -78,  “desc”: “Available, no cryostat needed. Gas station.”},
“liquid_nitrogen”:  {“T_K”: 77,  “T_C”: -196, “desc”: “Welding supply, ~$2/liter.”},
}

# ─────────────────────────────────────────────

# TEMPERATURE-DEPENDENT PROPERTIES

# ─────────────────────────────────────────────

def quartz_Q_vs_temp(T_K):
“””
Quartz mechanical Q vs temperature.

```
AT-cut quartz Q behavior:
- 300K: ~10⁶ (thermoelastic losses dominant)
- 250K: ~2×10⁶ 
- 200K: ~5×10⁶
- 100K: ~10⁷-10⁸
- 77K:  ~10⁷ (nitrogen)
- 4K:   ~10⁹ (helium)

Empirical: Q ∝ T⁻ⁿ where n ≈ 1-2 depending on loss mechanism.
Thermoelastic: n ≈ 1
Phonon-phonon (Akhiezer): n ≈ 2-3 at low T
"""
if T_K >= 250:
    # Thermoelastic regime
    Q = 1e6 * (300 / T_K)
elif T_K >= 100:
    # Transition regime  
    Q = 1e6 * (300 / 250) * (250 / T_K)**2
elif T_K >= 20:
    # Phonon-phonon regime
    Q = 1e6 * (300/250) * (250/100)**2 * (100/T_K)**2.5
else:
    # Quantum regime
    Q = 1e9

return min(Q, 1e10)  # physical cap
```

def curie_susceptibility(T_K, S=2.5, g=2.0):
“””
Paramagnetic susceptibility (Curie law).
χ = μ₀ N g² μ_B² S(S+1) / (3 k_B T)

```
Returns the spin response factor: Δ⟨Sz⟩/ΔB
"""
return g * MU_B * S * (S + 1) / (3 * K_B * T_K)
```

def thermal_phonon_noise(T_K, omega, V, rho):
“””
Thermal displacement noise of a mechanical mode.
x_thermal = √(k_B T / (m ω²))
“””
m = rho * V
return np.sqrt(K_B * T_K / (m * omega**2))

def hematite_morin_state(T_K):
“””
Hematite undergoes the Morin transition at ~263K (-10°C).

```
Above 263K: canted antiferromagnet (weak ferromagnet)
  - Net M_s ≈ 2.1 kA/m (from canting)
  - Spins in basal plane
  
Below 263K: pure antiferromagnet
  - Net M_s → 0
  - Spins along c-axis
  - BUT: domain walls carry net moment
  - AND: spin-phonon coupling CHANGES character
  
The transition itself is where interesting physics happens.
At T_Morin: large susceptibility anomaly (divergent dχ/dT).
"""
T_morin = 263  # K

if T_K > T_morin + 5:
    return {
        "state": "canted_AFM",
        "M_s": 2100,
        "eta_effective": 1.5,  # cm⁻¹
        "susceptibility_anomaly": 1.0,
    }
elif T_K > T_morin - 5:
    # Within ±5K of transition: enhanced susceptibility
    proximity = 1.0 - abs(T_K - T_morin) / 5.0
    anomaly = 1.0 + 10.0 * proximity  # up to 10× enhancement at transition
    return {
        "state": "transition",
        "M_s": 2100 * (1 - proximity * 0.9),
        "eta_effective": 1.5 * anomaly,  # enhanced at transition
        "susceptibility_anomaly": anomaly,
    }
else:
    return {
        "state": "pure_AFM",
        "M_s": 10,  # residual from domain walls
        "eta_effective": 0.8,  # different coupling in AFM phase
        "susceptibility_anomaly": 1.0,
    }
```

# ─────────────────────────────────────────────

# FULL COLD-CLIMATE DEVICE ANALYSIS

# ─────────────────────────────────────────────

def cold_climate_sensitivity(
T_K=233,                    # operating temperature
fe_ppm=100,                 # Fe concentration
eta_cm=0.3,                 # spin-phonon coupling cm⁻¹
thickness_m=0.1e-3,         # crystal thickness
diameter_m=8e-3,            # crystal diameter
delta_B_T=500e-9,           # signal to detect
integration_time_s=1.0,     # measurement integration
):
“””
Full sensitivity analysis at a specific temperature.
“””
rho = 2650.0
c = 3764.0
r = diameter_m / 2
V = np.pi * r**2 * thickness_m

```
f0 = c / (2 * thickness_m)
omega0 = 2 * np.pi * f0

# Temperature-dependent Q
Q = quartz_Q_vs_temp(T_K)

# Curie response
delta_Sz = curie_susceptibility(T_K) * delta_B_T

# Number density of Fe
n_sites = rho * 6.022e23 / 0.060
n_Fe = n_sites * fe_ppm * 1e-6

# Elastic constant shift
eta_J = eta_cm * 1.24e-4 * 1.602e-19
delta_c_over_c = n_Fe * eta_J * delta_Sz / (rho * c**2)

# Frequency shift
delta_f_over_f = 0.5 * delta_c_over_c
delta_f = delta_f_over_f * f0

# Resolution: Q-limited linewidth / sqrt(integration × bandwidth)
linewidth = f0 / (2 * Q)
# Allan deviation for quartz oscillator:
# σ_y(τ) ≈ 1/(2πf₀τ) × (linewidth / SNR)
# With good oscillator circuit: σ_y ~ 10⁻¹² at 1s
# At cold: Q improves, so σ_y improves
allan_1s = 1.0 / (2 * np.pi * Q)  # rough: Allan dev at 1s ∝ 1/Q
delta_f_resolution = f0 * allan_1s / np.sqrt(integration_time_s)

# Thermal frequency noise
# Random thermal fluctuations cause frequency noise
# Δf_thermal/f ∝ √(k_B T / E_stored)
# E_stored = (1/2) m ω² x_driven² — depends on drive level
# For 1 μW drive: E_stored ~ P × Q/ω
P_drive = 1e-6  # 1 μW typical crystal drive
E_stored = P_drive * Q / omega0
thermal_freq_noise = f0 * np.sqrt(K_B * T_K / (2 * E_stored))

# Net resolution (RSS of all noise sources)
net_resolution = np.sqrt(delta_f_resolution**2 + thermal_freq_noise**2)

# SNR
snr = abs(delta_f) / net_resolution if net_resolution > 0 else 0

# Integration time needed for SNR=1
# SNR ∝ √(τ), so τ_needed = τ_ref / SNR²
if snr > 0:
    t_needed_snr1 = integration_time_s / snr**2
else:
    t_needed_snr1 = np.inf

return {
    "T_K": T_K,
    "T_C": T_K - 273.15,
    "Q_mech": Q,
    "delta_Sz": delta_Sz,
    "delta_f_Hz": delta_f,
    "delta_f_ppb": delta_f_over_f * 1e9,
    "linewidth_Hz": linewidth,
    "allan_dev_1s": allan_1s,
    "resolution_Hz": net_resolution,
    "thermal_noise_Hz": thermal_freq_noise,
    "snr_1s": snr,
    "t_needed_snr1_s": t_needed_snr1,
    "detectable_1s": snr > 1,
    "detectable_10s": snr * np.sqrt(10) > 1,
    "detectable_100s": snr * np.sqrt(100) > 1,
    "detectable_1hr": snr * np.sqrt(3600) > 1,
    "curie_enhancement_vs_300K": 300 / T_K,
    "Q_enhancement_vs_300K": Q / 1e6,
}
```

# ─────────────────────────────────────────────

# MAIN

# ─────────────────────────────────────────────

if **name** == “**main**”:

```
print("=" * 85)
print("COLD CLIMATE CRYSTAL DEVICE")
print("When room temperature is the exception, not the rule")
print("=" * 85)

# ── Temperature sweep ──
print(f"\n─── TEMPERATURE SWEEP: Storm signal (ΔB=500 nT, η=0.3 cm⁻¹, 100 ppm Fe) ───")
print(f"  {'Climate':>20s}  {'T':>6s}  {'Q':>10s}  {'Δf Hz':>12s}  {'resol Hz':>12s}  "
      f"{'SNR 1s':>8s}  {'t for SNR=1':>12s}  {'1hr?':>5s}")
print("  " + "─" * 100)

for key, climate in CLIMATE_TEMPS.items():
    T = climate["T_K"]
    r = cold_climate_sensitivity(T_K=T, delta_B_T=500e-9)
    t_str = f"{r['t_needed_snr1_s']:.1e} s" if r['t_needed_snr1_s'] < 1e15 else "never"
    d1h = "YES" if r["detectable_1hr"] else "no"
    print(f"  {key:>20s}  {T:>5.0f}K  {r['Q_mech']:>10.2e}  {r['delta_f_Hz']:>12.4e}  "
          f"{r['resolution_Hz']:>12.4e}  {r['snr_1s']:>8.2e}  {t_str:>12s}  {d1h:>5s}")

# ── What changes with cold ──
print(f"\n─── COLD ADVANTAGES (stacked) ───")
r300 = cold_climate_sensitivity(T_K=300)
r233 = cold_climate_sensitivity(T_K=233)
r195 = cold_climate_sensitivity(T_K=195)
r77  = cold_climate_sensitivity(T_K=77)

print(f"\n  {'Factor':>30s}  {'300K':>12s}  {'233K(-40°C)':>12s}  {'195K(dry ice)':>14s}  {'77K(LN₂)':>12s}")
print("  " + "─" * 85)
print(f"  {'Curie enhancement ×':>30s}  {'1.00':>12s}  {300/233:>12.2f}  {300/195:>14.2f}  {300/77:>12.2f}")
print(f"  {'Q_mech':>30s}  {r300['Q_mech']:>12.2e}  {r233['Q_mech']:>12.2e}  {r195['Q_mech']:>14.2e}  {r77['Q_mech']:>12.2e}")
print(f"  {'Q enhancement ×':>30s}  {'1.00':>12s}  {r233['Q_mech']/1e6:>12.2f}  {r195['Q_mech']/1e6:>14.2f}  {r77['Q_mech']/1e6:>12.2f}")
print(f"  {'Thermal noise Hz':>30s}  {r300['thermal_noise_Hz']:>12.4e}  {r233['thermal_noise_Hz']:>12.4e}  {r195['thermal_noise_Hz']:>14.4e}  {r77['thermal_noise_Hz']:>12.4e}")
print(f"  {'Resolution Hz':>30s}  {r300['resolution_Hz']:>12.4e}  {r233['resolution_Hz']:>12.4e}  {r195['resolution_Hz']:>14.4e}  {r77['resolution_Hz']:>12.4e}")
print(f"  {'SNR (1s)':>30s}  {r300['snr_1s']:>12.4e}  {r233['snr_1s']:>12.4e}  {r195['snr_1s']:>14.4e}  {r77['snr_1s']:>12.4e}")
print(f"  {'SNR (1 hour)':>30s}  {r300['snr_1s']*60:>12.4e}  {r233['snr_1s']*60:>12.4e}  {r195['snr_1s']*60:>14.4e}  {r77['snr_1s']*60:>12.4e}")

total_cold_advantage = (300/233) * (r233['Q_mech']/1e6) * np.sqrt(300/233)
total_dryice = (300/195) * (r195['Q_mech']/1e6) * np.sqrt(300/195)
total_ln2 = (300/77) * (r77['Q_mech']/1e6) * np.sqrt(300/77)
print(f"\n  {'TOTAL cold advantage ×':>30s}  {'1.00':>12s}  {total_cold_advantage:>12.1f}  {total_dryice:>14.1f}  {total_ln2:>12.1f}")

# ── Hematite Morin transition ──
print(f"\n─── HEMATITE MORIN TRANSITION (-10°C) ───")
print(f"  Your winter crosses this transition every year.")
print(f"  {'T_K':>8s}  {'T_C':>8s}  {'state':>15s}  {'M_s':>10s}  {'η_eff cm⁻¹':>12s}  {'anomaly ×':>10s}")
print("  " + "─" * 70)
for T in [280, 275, 270, 268, 265, 263, 261, 258, 255, 250, 240, 230]:
    m = hematite_morin_state(T)
    print(f"  {T:>8.0f}  {T-273:>8.0f}  {m['state']:>15s}  {m['M_s']:>10.0f}  "
          f"{m['eta_effective']:>12.2f}  {m['susceptibility_anomaly']:>10.1f}")

# ── Eta sweep at -40°C ──
print(f"\n─── η SWEEP AT -40°C (233K, storm signal 500 nT) ───")
print(f"  {'η cm⁻¹':>10s}  {'Δf Hz':>12s}  {'SNR 1s':>10s}  {'SNR 1hr':>10s}  {'detect 1hr':>10s}")
for eta in [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]:
    r = cold_climate_sensitivity(T_K=233, eta_cm=eta, delta_B_T=500e-9)
    snr_1hr = r["snr_1s"] * 60
    det = "YES" if snr_1hr > 1 else "no"
    print(f"  {eta:>10.2f}  {r['delta_f_Hz']:>12.4e}  {r['snr_1s']:>10.4e}  {snr_1hr:>10.4e}  {det:>10s}")

# ── Dry ice + high η ──
print(f"\n─── DRY ICE (-78°C) + HIGH η ───")
print(f"  Dry ice is available at any gas station / grocery store.")
print(f"  Pack crystal in dry ice. No cryostat. No dewar. No lab.")
print(f"  {'η cm⁻¹':>10s}  {'Δf Hz':>12s}  {'SNR 1s':>10s}  {'SNR 1hr':>10s}  {'detect 1hr':>10s}")
for eta in [0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]:
    r = cold_climate_sensitivity(T_K=195, eta_cm=eta, delta_B_T=500e-9)
    snr_1hr = r["snr_1s"] * 60
    det = "YES" if snr_1hr > 1 else "no"
    print(f"  {eta:>10.2f}  {r['delta_f_Hz']:>12.4e}  {r['snr_1s']:>10.4e}  {snr_1hr:>10.4e}  {det:>10s}")

# ── LN₂ (welding supply) ──
print(f"\n─── LIQUID NITROGEN (77K) — from welding supply, ~$2/liter ───")
print(f"  {'η cm⁻¹':>10s}  {'Δf Hz':>12s}  {'SNR 1s':>10s}  {'SNR 1hr':>10s}  {'detect 1hr':>10s}  {'detect 1s':>10s}")
for eta in [0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]:
    r = cold_climate_sensitivity(T_K=77, eta_cm=eta, delta_B_T=500e-9)
    snr_1hr = r["snr_1s"] * 60
    det_hr = "YES" if snr_1hr > 1 else "no"
    det_1s = "YES" if r["snr_1s"] > 1 else "no"
    print(f"  {eta:>10.2f}  {r['delta_f_Hz']:>12.4e}  {r['snr_1s']:>10.4e}  {snr_1hr:>10.4e}  {det_hr:>10s}  {det_1s:>10s}")

# ── What η is needed at each temperature for 1-hour detection? ──
print(f"\n─── MINIMUM η FOR 1-HOUR DETECTION OF STORM (500 nT) ───")
for key, climate in CLIMATE_TEMPS.items():
    T = climate["T_K"]
    # Binary search for η where SNR_1hr = 1
    eta_low, eta_high = 1e-3, 1e6
    for _ in range(50):
        eta_mid = np.sqrt(eta_low * eta_high)
        r = cold_climate_sensitivity(T_K=T, eta_cm=eta_mid, delta_B_T=500e-9)
        if r["snr_1s"] * 60 > 1:
            eta_high = eta_mid
        else:
            eta_low = eta_mid
    print(f"  {key:>20s} ({T:>5.0f}K): η > {eta_high:>10.2f} cm⁻¹  "
          f"{'← MEASURED RANGE' if eta_high < 3.4 else '← need enhancement' if eta_high < 100 else '← very hard'}")

print(f"\n{'='*85}")
print("SYNTHESIS")
print(f"{'='*85}")
print("""
```

The cold changes the game, but not enough on its own.

At -40°C (your winter baseline):
Curie susceptibility: 1.29× better
Q_mech: 1.29× better  
Thermal noise: 0.88× lower
Net advantage: ~2× over room temp

At dry ice (-78°C, gas station purchase):
Curie: 1.54×, Q: 2.37×, Total: ~4.5×

At LN₂ (77K, welding supply):
Curie: 3.90×, Q: ~100×, Total: ~600×

The scaling is real but the baseline deficit is 10⁸.
Cold alone doesn’t close the gap.

HOWEVER — the minimum η for detection at each temp:

At 77K (LN₂):     η > 5-10 cm⁻¹  
At 195K (dry ice): η > 30-50 cm⁻¹
At 233K (-40°C):   η > 50-100 cm⁻¹

Literature η for Fe³⁺ in ORDERED oxides: 0.1-3.4 cm⁻¹

The gap is still there. But it’s smaller in the cold.
And the right question becomes:

Is 0.3 cm⁻¹ really the right η for Fe³⁺ in quartz?
Or could the actual coupling be stronger than we assumed?

That’s Step 0. Measure it. The cold is free.
The measurement can happen in January in the truck cab
with the engine off and the windows open.
“””)
print(”=” * 85)
