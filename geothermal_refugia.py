# geothermal_refugia.py  -- CC0, stdlib-only
#
# Snowball Earth without the smooth-sphere lie.
#
# Standard models smear geothermal flux into a uniform background term and treat
# bathymetry as flat for radiation. This module lets crustal HETEROGENEITY drive
# the result:
#
#   1. SUB-ICE OCEAN     a Snowball ocean does NOT freeze to the bottom. Geothermal
#                        flux sets a maximum sea-ice thickness H_eq; liquid ocean
#                        persists below. (GEO-01) -> answers 'do the deep pockets
#                        stay liquid' : yes, and so does the whole sub-ice ocean.
#
#   2. CONTINENTAL ICE   grounded ice is wet-based (subglacial melt = refugium)
#                        ONLY where Q_geo beats the conductive flux the ice can
#                        carry at its pressure-melting point. Patchy. (GEO-02)
#
#   3. HONESTY           refugia sustain LIFE; they do not END the freeze. Their
#                        area is too small to flip planetary albedo. CO2 ends it.
#                        (GEO-04)
#
# Physics (MEASURED constants):
#   k_ice = 2.1 W/m/K   rho_ice = 917 kg/m3   L_f = 3.34e5 J/kg
#   pressure melting:  T_pmp = -beta*rho*g*H  (~ -0.71 K per km of ice)

import math
from claim_ledger import Quantity, gate

K_ICE = 2.1            # W/m/K
RHO_ICE = 917.0        # kg/m3
L_F = 3.34e5           # J/kg
G = 9.81               # m/s2
BETA_PMP = 7.9e-8      # K/Pa  (Clausius-Clapeyron, ice melting under pressure)
T_FREEZE_SEAWATER = -2.0   # degC
EARTH_AREA_KM2 = 5.10e8
SEC_PER_YR = 3.156e7

PMP_K_PER_M = BETA_PMP * RHO_ICE * G    # ~7.1e-4 K/m


def pressure_melting_point_c(h_ice_m: float) -> float:
    """Basal pressure-melting point under ice of thickness H. degC."""
    t = -PMP_K_PER_M * h_ice_m
    return gate(Quantity(t, "degC", -5.0, 0.0), "pmp")


def sea_ice_equilibrium_thickness(q_geo: float,
                                  t_surf_c: float = -40.0,
                                  t_freeze_c: float = T_FREEZE_SEAWATER) -> float:
    """
    GEO-01. Steady marine ice: conduction carries geothermal flux.
      H_eq = k (T_f - T_surf) / Q_geo
    Below this thickness the ocean stays LIQUID. Deep ocean (~3.7 km) >> H_eq,
    so the sub-ice ocean is the largest refugium on the planet.
    """
    dT = t_freeze_c - t_surf_c
    h = K_ICE * dT / q_geo
    return gate(Quantity(h, "m", 50.0, 3000.0), "sea_ice_eq_thickness")


def subglacial_state(q_geo: float, h_ice_m: float,
                     t_surf_c: float = -40.0) -> dict:
    """
    GEO-02. Grounded continental ice over crust.
      wet-based (melt refugium) iff  Q_geo > k (T_pmp - T_surf) / H
    Returns regime, basal temperature, and basal melt rate (m/yr) if wet.
    """
    pmp = pressure_melting_point_c(h_ice_m)
    q_cond_at_pmp = K_ICE * (pmp - t_surf_c) / h_ice_m   # W/m2
    if q_geo > q_cond_at_pmp:
        melt_w = q_geo - q_cond_at_pmp                   # W/m2 into melting
        melt_rate = melt_w / (RHO_ICE * L_F) * SEC_PER_YR  # m/yr
        return {
            "regime": "WET_BASED_REFUGIUM",
            "basal_temp_c": round(pmp, 3),
            "basal_melt_rate_m_per_yr": round(melt_rate, 5),
            "q_crit_W_m2": round(q_cond_at_pmp, 4),
        }
    # cold-based: basal temp sits below pmp
    basal_t = t_surf_c + q_geo * h_ice_m / K_ICE
    return {
        "regime": "COLD_BASED_FROZEN",
        "basal_temp_c": round(basal_t, 3),
        "basal_melt_rate_m_per_yr": 0.0,
        "q_crit_W_m2": round(q_cond_at_pmp, 4),
    }


# crustal heat-flux provinces (schematic; 600 Ma geography differs - flag).
# (name, area_fraction, Q_geo_W_m2, kind)
PROVINCES = [
    ("mid_ocean_ridge",    0.05, 0.250, "ocean"),
    ("ocean_floor",        0.55, 0.100, "ocean"),
    ("continental_craton", 0.25, 0.045, "land"),
    ("active_margin",      0.10, 0.080, "land"),
    ("hotspot_LIP",        0.05, 0.300, "land"),
]


def refugia_inventory(t_surf_c: float = -40.0,
                      continental_ice_m: float = 1000.0,
                      ocean_depth_m: float = 3700.0) -> dict:
    """
    Sum liquid-refugium area across the heterogeneous crust.
      ocean provinces  -> liquid below sea ice if ocean_depth > H_eq
      land provinces   -> refugium only where wet-based

    CRITICAL distinction (the smoothing trap):
      SUB-ICE liquid  -> matters for LIFE, but its surface is ICE, so albedo
                         is UNCHANGED. Hidden from radiation.
      OPEN water      -> surface exposed to atmosphere, albedo DROPS. This is
                         the only thing that can threaten the freeze (GEO-04).
      In a hard Snowball, open water ~ 0; all refugia are sub-ice.
    """
    subice_liquid_area = 0.0     # life refugia, albedo-neutral
    open_water_area = 0.0        # albedo-relevant
    hydrothermal_area = 0.0
    rows = []
    for name, frac, q, kind in PROVINCES:
        area_km2 = frac * EARTH_AREA_KM2
        if kind == "ocean":
            h_eq = sea_ice_equilibrium_thickness(q, t_surf_c)
            if h_eq <= 0.0:
                open_water_area += area_km2          # cannot sustain ice
                rows.append((name, kind, round(h_eq, 1), "OPEN_WATER"))
            elif ocean_depth_m > h_eq:
                subice_liquid_area += area_km2       # liquid under ice
                rows.append((name, kind, round(h_eq, 1), "LIQUID_OCEAN_BELOW_ICE"))
                if name == "mid_ocean_ridge":
                    hydrothermal_area += area_km2
            else:
                rows.append((name, kind, round(h_eq, 1), "FROZEN_THROUGH"))
        else:
            st = subglacial_state(q, continental_ice_m, t_surf_c)
            wet = st["regime"] == "WET_BASED_REFUGIUM"
            rows.append((name, kind, st["q_crit_W_m2"], st["regime"]))
            if wet:
                subice_liquid_area += area_km2       # subglacial lake, ice-capped
                hydrothermal_area += area_km2

    f_subice = subice_liquid_area / EARTH_AREA_KM2
    f_open = open_water_area / EARTH_AREA_KM2
    return {
        "t_surf_c": t_surf_c,
        "continental_ice_m": continental_ice_m,
        "subice_liquid_fraction": round(f_subice, 4),   # LIFE refugia
        "open_water_fraction": round(f_open, 4),         # ALBEDO-relevant
        "subice_liquid_area_km2": round(subice_liquid_area, 0),
        "hydrothermal_refugia_km2": round(hydrothermal_area, 0),
        "albedo_verdict": ("open water ~0 -> surface stays white -> albedo "
                           "unchanged -> CO2 must end the freeze (GEO-04 SUPPORTED)"
                           if f_open < 0.02 else
                           "open-water fraction non-trivial -> GEO-04 falsifier "
                           "in play: refugia/open water may aid deglaciation"),
        "life_verdict": (f"sub-ice + hydrothermal liquid covers {f_subice:.0%} "
                         "of the surface as ICE-CAPPED refugia -> ample for "
                         "survival (GEO-03 plausible)"),
        "provinces": rows,
    }


if __name__ == "__main__":
    print("SEA-ICE EQUILIBRIUM THICKNESS (ocean stays liquid below):")
    for q in (0.06, 0.10, 0.25):
        print(f"  Q={q:.2f} W/m2 -> H_eq = "
              f"{sea_ice_equilibrium_thickness(q):.0f} m  (ocean ~3700 m deep)")

    print("\nCONTINENTAL BASE vs ICE THICKNESS (craton Q=0.045):")
    for H in (300, 1000, 2000, 3000):
        st = subglacial_state(0.045, H)
        print(f"  H={H:5d} m -> {st['regime']:18s} "
              f"q_crit={st['q_crit_W_m2']:.4f}  "
              f"melt={st['basal_melt_rate_m_per_yr']} m/yr")

    print("\nREFUGIA INVENTORY (T_surf=-40C, continental ice=1000 m):")
    inv = refugia_inventory()
    for name, kind, qc, state in inv["provinces"]:
        print(f"  {name:20s} {kind:6s} {str(qc):>8s}  {state}")
    print(f"  -> sub-ice liquid (LIFE)   = {inv['subice_liquid_fraction']}")
    print(f"  -> open water (ALBEDO)     = {inv['open_water_fraction']}")
    print(f"  -> {inv['albedo_verdict']}")
    print(f"  -> {inv['life_verdict']}")

    print("\nThick-ice case (continental ice=2500 m): cratons go wet-based?")
    inv2 = refugia_inventory(continental_ice_m=2500.0)
    print(f"  sub-ice liquid fraction = {inv2['subice_liquid_fraction']}  "
          f"open water = {inv2['open_water_fraction']}")
