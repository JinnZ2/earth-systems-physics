# skyrmion_phonon_coupling.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
skyrmion_phonon_coupling.py
───────────────────────────
Internal modes of magnetic skyrmions and their coupling to the
phonon field.

A skyrmion is a topologically protected magnetic texture; it
does not spontaneously unwind into a uniform ferromagnet (see
skyrmion_rkky.py for Q = ±1 topological charge). But it is not
rigid — it has three low-energy internal modes that modulate
its shape and position:

  1. Gyrotropic:  rigid-body circular motion of the skyrmion
                  center. The lowest-frequency mode, typically
                  0.1-1 GHz. Couples strongly to in-plane
                  shear phonons.

  2. Breathing:   radial oscillation (radius expanding and
                  contracting). Typically 1-10 GHz. Couples
                  isotropically to longitudinal acoustic and
                  bulk phonons.

  3. Elliptic:    second-order deformation that tilts the
                  circular profile into an ellipse. Typically
                  2-4× the breathing frequency. Couples to
                  anisotropic strain.

Each mode has a characteristic frequency set by the skyrmion
radius, the magnetic anisotropy, and the exchange stiffness.
Each one couples to phonons through spin-lattice interaction,
creating skyrmion-phonon hybrid quasiparticles (extending the
magnon-polaron concept of magnon_polaron_hybridization.py from
uniform spin waves to topological textures).

Place in the repo:
  - Complements skyrmion_rkky.py (which provides Q, RKKY
    coupling, LLG integrator, and reference materials) with
    the skyrmion-phonon interaction channel
  - Extends the magnon-phonon coupling story covered by
    magnon_polaron_hybridization.py and multi_channel_coupling.py
    from uniform spin-wave modes to topological internal modes
  - References materials from SKYRMION_MATERIALS in
    skyrmion_rkky.py and adds spin-wave parameters (exchange
    stiffness, saturation magnetization, anisotropy) needed
    for frequency calculations

Physics references:
  Gyrotropic mode:
    ω_G = (γ / M_s) · (K_eff · f_G(R))
    where f_G is a geometric factor ~1 / (π R²) for a 2D
    skyrmion in the Thiele-equation approximation.

  Breathing mode (radial):
    ω_B ~ (2 A / M_s) · (1 / R²)
    where A is the exchange stiffness (J/m). Scales as 1/R²
    because the exchange restoring force goes as the curvature.

  Elliptic mode:
    ω_E ≈ 2 · ω_B (ellipticity is second harmonic of radial
    oscillation under weak confinement).

  Coupling to phonons: via magnetoelastic interaction
    H_me = B₁ (Σᵢ εᵢᵢ mᵢ²) + B₂ (Σᵢ≠ⱼ εᵢⱼ mᵢ mⱼ)
  Each internal mode couples to different strain components.

CC0 — No rights reserved.
"""

import math
from typing import Dict, List, Optional, Tuple

import numpy as np


# ════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════

GAMMA_E = 1.7608597e11   # electron gyromagnetic ratio (rad / s / T)
MU_0    = 4.0 * np.pi * 1e-7  # vacuum permeability (H / m)
HBAR    = 1.0545718e-34  # reduced Planck (J · s)
K_B     = 1.380649e-23   # Boltzmann (J / K)
# Typical phonon velocity range for order-of-magnitude checks
V_SOUND_TYPICAL = 5000.0  # m / s


# ════════════════════════════════════════════════════════
# SKYRMION INTERNAL MODES
# ════════════════════════════════════════════════════════
#
# Three low-energy modes, each with a characteristic frequency
# scaling and a dominant phonon-coupling channel.

SKYRMION_INTERNAL_MODES = {
    "gyrotropic": {
        "order":  1,  # rigid-body translation
        "symmetry": "circular COM motion in-plane",
        "typical_freq_GHz": "0.1 - 1",
        "freq_scaling": "~ K_eff / (M_s · R²)",
        "phonon_channel": "in-plane shear (transverse acoustic)",
        "coupling_type": (
            "magnetoelastic B₂ (off-diagonal strain couples to "
            "in-plane mᵢmⱼ)"
        ),
        "observability": (
            "Microwave resonance + FMR in thin films; visible as "
            "lowest-frequency skyrmion peak"
        ),
    },
    "breathing": {
        "order": 2,  # radial
        "symmetry": "radial expansion / contraction (isotropic)",
        "typical_freq_GHz": "1 - 10",
        "freq_scaling": "~ 2A / (M_s · R²)",
        "phonon_channel": (
            "longitudinal acoustic + bulk volume phonons"
        ),
        "coupling_type": (
            "magnetoelastic B₁ (diagonal strain couples to mᵢ²)"
        ),
        "observability": (
            "Microwave absorption spectroscopy; scales with "
            "external field"
        ),
    },
    "elliptic": {
        "order": 3,  # shape distortion
        "symmetry": "second-order profile distortion (2-fold)",
        "typical_freq_GHz": "2 - 20",
        "freq_scaling": "~ 2 · ω_breathing (weak confinement)",
        "phonon_channel": "anisotropic shear phonons",
        "coupling_type": (
            "magnetoelastic B₂ + quadrupolar strain coupling"
        ),
        "observability": (
            "Higher-harmonic FMR sidebands; hardest mode to "
            "observe in isolation"
        ),
    },
}


# ════════════════════════════════════════════════════════
# SPIN-WAVE MATERIAL PARAMETERS
# ════════════════════════════════════════════════════════
#
# Parameters needed to compute skyrmion internal-mode
# frequencies: exchange stiffness A (J/m), saturation
# magnetization M_s (A/m), effective anisotropy K_eff
# (J/m³), and a representative sound speed for phonon
# coupling estimates.
#
# Sources: experimental literature on magnon dispersion,
# FMR, and neutron scattering for each material. Numbers
# are order-of-magnitude reliable; precise values vary with
# sample preparation and temperature.

SKYRMION_SPINWAVE_PARAMS = {
    "MnSi": {
        "A_exchange_Jm":      8.2e-13,
        "M_s_A_m":            1.52e5,
        "K_eff_Jm3":          1.4e4,
        "sound_speed_ms":     4450.0,
        "reference_T_K":      29.0,
        "notes": (
            "Classic B20 helimagnet. DMI-stabilized. Gyrotropic "
            "mode ~ 1 GHz. Breathing ~ 9 GHz at skyrmion phase."
        ),
    },
    "FeGe": {
        "A_exchange_Jm":      8.8e-12,
        "M_s_A_m":            3.84e5,
        "K_eff_Jm3":          1.0e4,
        "sound_speed_ms":     4800.0,
        "reference_T_K":      278.0,
        "notes": (
            "Near-room-temperature helimagnet. DMI-stabilized. "
            "Larger skyrmions (~35 nm), so internal modes are "
            "at lower frequencies than MnSi."
        ),
    },
    "Gd2PdSi3": {
        "A_exchange_Jm":      2.5e-13,
        "M_s_A_m":            7.5e5,
        "K_eff_Jm3":          4.0e4,
        "sound_speed_ms":     3800.0,
        "reference_T_K":      21.0,
        "notes": (
            "Centrosymmetric, RKKY-stabilized. Small skyrmions "
            "(~2.5 nm) -> high internal-mode frequencies. "
            "Kurumaji et al. 2019."
        ),
    },
    "Gd3Ru4Al12": {
        "A_exchange_Jm":      3.0e-13,
        "M_s_A_m":            6.8e5,
        "K_eff_Jm3":          3.5e4,
        "sound_speed_ms":     3600.0,
        "reference_T_K":      18.5,
        "notes": (
            "Centrosymmetric, RKKY-stabilized. Triangular "
            "skyrmion lattice. Hirschberger et al. 2019."
        ),
    },
    "GdRu2Si2": {
        "A_exchange_Jm":      2.8e-13,
        "M_s_A_m":            8.2e5,
        "K_eff_Jm3":          6.0e4,
        "sound_speed_ms":     4000.0,
        "reference_T_K":      46.0,
        "notes": (
            "Centrosymmetric, RKKY-stabilized. Among smallest "
            "skyrmions (~1.9 nm). Khanh et al. 2020."
        ),
    },
}


# ════════════════════════════════════════════════════════
# MODE FREQUENCIES
# ════════════════════════════════════════════════════════

def gyrotropic_frequency_Hz(
    radius_nm: float,
    M_s_A_m: float,
    K_eff_Jm3: float,
    gamma: float = GAMMA_E,
    topological_charge: float = 1.0,
) -> float:
    """Gyrotropic-mode frequency for an isolated skyrmion.

    Approximation (Thiele equation, symmetric confinement):
        ω_G ≈ γ · K_eff / (4π · M_s · |Q|)

    The gyrotropic mode is a rigid-body circular motion of the
    skyrmion center of mass. The restoring force comes from the
    anisotropy-derived confining potential; the gyrovector
    G ∝ M_s · Q provides the Magnus-like force that makes the
    motion circular. This closed form drops the explicit R
    dependence (it cancels between stiffness ∝ K_eff·R² and
    gyrovector magnitude ∝ M_s·R²).

    Numbers are order-of-magnitude reliable; the actual
    frequency depends on field, temperature, and confinement
    geometry. Typical values: 0.1-1 GHz.

    Args:
        radius_nm:          included for API parity with the
                            other mode functions; not used in
                            the symmetric approximation
        M_s_A_m:            saturation magnetization (A / m)
        K_eff_Jm3:          effective anisotropy (J / m³)
        gamma:              gyromagnetic ratio (rad / s / T)
        topological_charge: |Q|, default 1

    Returns:
        Gyrotropic frequency in Hz (not angular frequency).
    """
    if radius_nm <= 0 or M_s_A_m <= 0:
        raise ValueError("radius and M_s must be positive")
    if topological_charge == 0:
        raise ValueError("topological_charge must be non-zero")
    omega = (
        gamma * K_eff_Jm3
        / (4.0 * math.pi * M_s_A_m * abs(topological_charge))
    )
    return float(abs(omega) / (2.0 * math.pi))


def breathing_frequency_Hz(
    radius_nm: float,
    A_exchange_Jm: float,
    M_s_A_m: float,
    gamma: float = GAMMA_E,
) -> float:
    """Breathing (radial) mode frequency for an isolated skyrmion.

    Approximation:
        ω_B ≈ γ · (2 A / M_s) · (1 / R²)

    The exchange stiffness A provides the restoring force
    against radial expansion; the 1/R² scaling comes from the
    curvature term in the Euler-Lagrange equation for a
    radially-symmetric magnetic texture. No μ₀ factor — the
    exchange field 2A/(M_s·R²) is already in A/m.

    For MnSi (R=9 nm, A=0.82 pJ/m, M_s=1.5×10⁵ A/m) this gives
    ~4 GHz, within a factor of ~2 of the experimental ~9 GHz
    breathing mode. The discrepancy is the geometric order-
    unity factor this closed form drops.

    Args:
        radius_nm:     skyrmion radius in nm
        A_exchange_Jm: exchange stiffness (J / m)
        M_s_A_m:       saturation magnetization (A / m)
        gamma:         gyromagnetic ratio (rad / s / T)

    Returns:
        Breathing frequency in Hz.
    """
    if radius_nm <= 0 or M_s_A_m <= 0 or A_exchange_Jm <= 0:
        raise ValueError("radius, A, M_s must all be positive")
    R = radius_nm * 1e-9
    omega = gamma * (2.0 * A_exchange_Jm / M_s_A_m) * (1.0 / (R * R))
    return float(abs(omega) / (2.0 * math.pi))


def elliptic_frequency_Hz(
    breathing_freq_Hz: float,
    multiplier: float = 2.0,
) -> float:
    """Elliptic-mode frequency ≈ multiplier · breathing frequency.

    Under weak confinement (typical for skyrmion lattices in
    thin films), the elliptic (shape-distortion) mode is the
    second harmonic of the radial mode. The multiplier is ~2
    but ranges up to ~4 for strongly confined skyrmions.
    """
    if breathing_freq_Hz <= 0:
        raise ValueError("breathing_freq_Hz must be positive")
    return float(multiplier * breathing_freq_Hz)


def all_internal_modes_Hz(
    radius_nm: float,
    A_exchange_Jm: float,
    M_s_A_m: float,
    K_eff_Jm3: float,
    elliptic_multiplier: float = 2.0,
    gamma: float = GAMMA_E,
) -> Dict[str, float]:
    """Compute all three internal-mode frequencies in one call.

    Returns a dict with keys "gyrotropic", "breathing",
    "elliptic" (all in Hz).
    """
    f_g = gyrotropic_frequency_Hz(
        radius_nm, M_s_A_m, K_eff_Jm3, gamma,
    )
    f_b = breathing_frequency_Hz(
        radius_nm, A_exchange_Jm, M_s_A_m, gamma,
    )
    f_e = elliptic_frequency_Hz(f_b, elliptic_multiplier)
    return {
        "gyrotropic": f_g,
        "breathing":  f_b,
        "elliptic":   f_e,
    }


def modes_for_material(
    material: str,
    radius_nm: Optional[float] = None,
) -> Dict[str, float]:
    """Compute internal modes for a material from the catalog.

    Uses SKYRMION_SPINWAVE_PARAMS for A, M_s, K_eff; uses the
    material's reference radius unless overridden.

    Args:
        material:  key into SKYRMION_SPINWAVE_PARAMS
        radius_nm: override radius; if None, the function
                   pulls the reference radius from
                   skyrmion_rkky.SKYRMION_MATERIALS if
                   available, otherwise raises.
    """
    if material not in SKYRMION_SPINWAVE_PARAMS:
        raise KeyError(
            f"unknown material {material!r}; available: "
            f"{sorted(SKYRMION_SPINWAVE_PARAMS.keys())}"
        )
    p = SKYRMION_SPINWAVE_PARAMS[material]
    if radius_nm is None:
        # cross-reference skyrmion_rkky for the reference radius
        try:
            from skyrmion_rkky import SKYRMION_MATERIALS
        except ImportError as e:
            raise RuntimeError(
                "radius_nm not supplied and skyrmion_rkky not "
                "importable; cannot look up reference radius"
            ) from e
        if material not in SKYRMION_MATERIALS:
            raise KeyError(
                f"{material} not in skyrmion_rkky.SKYRMION_MATERIALS"
            )
        radius_nm = SKYRMION_MATERIALS[material]["skyrmion_radius_nm"]
    return all_internal_modes_Hz(
        radius_nm=radius_nm,
        A_exchange_Jm=p["A_exchange_Jm"],
        M_s_A_m=p["M_s_A_m"],
        K_eff_Jm3=p["K_eff_Jm3"],
    )


# ════════════════════════════════════════════════════════
# PHONON COUPLING ESTIMATION
# ════════════════════════════════════════════════════════

def phonon_wavenumber_match(
    mode_frequency_Hz: float,
    sound_speed_ms: float = V_SOUND_TYPICAL,
) -> float:
    """Phonon wavenumber k that matches a given mode frequency.

    Linear phonon dispersion ω = c_s · k gives:
        k = 2π · f / c_s

    The matched phonon wavelength λ = c_s / f is the relevant
    length scale for magnon-polaron hybridization — when this
    wavelength matches the skyrmion radius, coupling is
    maximized.

    Returns:
        Wavenumber k in 1 / m.
    """
    if mode_frequency_Hz <= 0 or sound_speed_ms <= 0:
        raise ValueError("frequency and sound speed must be positive")
    return float(2.0 * math.pi * mode_frequency_Hz / sound_speed_ms)


def phonon_wavelength_m(
    mode_frequency_Hz: float,
    sound_speed_ms: float = V_SOUND_TYPICAL,
) -> float:
    """Phonon wavelength at a given frequency (meters)."""
    if mode_frequency_Hz <= 0 or sound_speed_ms <= 0:
        raise ValueError("frequency and sound speed must be positive")
    return float(sound_speed_ms / mode_frequency_Hz)


def coupling_strength(
    mode_name: str,
    skyrmion_radius_nm: float,
    mode_frequency_Hz: float,
    sound_speed_ms: float = V_SOUND_TYPICAL,
    B_magnetoelastic_J_m3: float = 1.0e6,
) -> Dict[str, float]:
    """Estimate the skyrmion-phonon coupling for one internal mode.

    The coupling strength depends on two ratios:

        η_spatial = R / λ_phonon
            How well does the phonon wavelength match the
            skyrmion size? Maximum coupling at η_spatial ≈ 1.
            For η_spatial << 1 the phonon averages over the
            skyrmion profile (weak coupling); for η_spatial
            >> 1 the phonon oscillates faster than the
            skyrmion can respond.

        g_me = B · V_sk / (ℏω)
            Dimensionless magnetoelastic coupling. B is the
            magnetoelastic constant (J/m³), V_sk ≈ π R² · t
            is the skyrmion volume, ω is the mode angular
            frequency.

    The overall coupling g ~ g_me · η_spatial · (channel
    form factor from SKYRMION_INTERNAL_MODES).

    Args:
        mode_name:            "gyrotropic", "breathing", or
                              "elliptic"
        skyrmion_radius_nm:   skyrmion radius in nm
        mode_frequency_Hz:    frequency of the internal mode
        sound_speed_ms:       phonon velocity in the relevant
                              branch (shear for gyrotropic,
                              longitudinal for breathing)
        B_magnetoelastic_J_m3: magnetoelastic constant. Typical
                              values: B₁ ~ 10⁶-10⁷ J/m³ for
                              iron-group magnets.

    Returns:
        dict with g_dimensionless, phonon_wavelength_nm,
        eta_spatial, channel, and notes.
    """
    if mode_name not in SKYRMION_INTERNAL_MODES:
        raise KeyError(
            f"unknown mode {mode_name!r}; must be one of "
            f"{sorted(SKYRMION_INTERNAL_MODES.keys())}"
        )
    mode_spec = SKYRMION_INTERNAL_MODES[mode_name]

    R = skyrmion_radius_nm * 1e-9
    lam = phonon_wavelength_m(mode_frequency_Hz, sound_speed_ms)
    eta = R / lam

    # Assume thin film; treat thickness ~ R for volume estimate.
    V_sk = math.pi * R * R * R
    omega = 2.0 * math.pi * mode_frequency_Hz
    g_me = B_magnetoelastic_J_m3 * V_sk / (HBAR * omega)

    g_dimensionless = g_me * eta

    return {
        "mode": mode_name,
        "channel": mode_spec["phonon_channel"],
        "phonon_wavelength_nm": lam * 1e9,
        "eta_spatial": eta,
        "g_magnetoelastic": g_me,
        "g_dimensionless": g_dimensionless,
        "notes": (
            "Maximum coupling near eta_spatial ≈ 1; "
            "current value is " + ("well matched" if 0.5 <= eta <= 2.0
            else "off-resonance") + "."
        ),
    }


# ════════════════════════════════════════════════════════
# AI REFERENCE
# ════════════════════════════════════════════════════════

AI_REFERENCE = {
    "purpose": (
        "Skyrmion internal modes (gyrotropic, breathing, "
        "elliptic) and their coupling to the phonon field. "
        "Extends the magnon-phonon coupling story of "
        "magnon_polaron_hybridization.py from uniform spin "
        "waves to topological magnetic textures."
    ),
    "when_to_apply": [
        (
            "You have a skyrmion-hosting material and want to "
            "estimate the frequencies of its three internal "
            "modes (gyrotropic, breathing, elliptic)."
        ),
        (
            "You want to know which phonon channel couples most "
            "strongly to each internal mode."
        ),
        (
            "You are designing an experiment that drives or "
            "reads out a skyrmion via acoustic excitation."
        ),
        (
            "You are pairing this with skyrmion_rkky.py to make "
            "a full skyrmion-system model: RKKY stabilization + "
            "topological protection + phonon transduction."
        ),
    ],
    "key_exports": {
        "SKYRMION_INTERNAL_MODES": (
            "Dict of 3 modes: gyrotropic, breathing, elliptic. "
            "Each has order, symmetry, typical frequency range, "
            "scaling law, dominant phonon channel, coupling "
            "type (B₁ vs B₂ magnetoelastic), and observability."
        ),
        "SKYRMION_SPINWAVE_PARAMS": (
            "Dict of 5 materials with spin-wave parameters "
            "(exchange stiffness, saturation magnetization, "
            "anisotropy, sound speed) needed to compute "
            "mode frequencies."
        ),
        "gyrotropic_frequency_Hz": (
            "ω_G ≈ γ K_eff / (4π M_s |Q|). Thiele-equation "
            "approximation, R-independent in symmetric limit."
        ),
        "breathing_frequency_Hz": (
            "ω_B ≈ γ × 2A / (M_s R²). Exchange-limited radial "
            "mode. No μ₀ factor — internal exchange field is "
            "already in A/m."
        ),
        "elliptic_frequency_Hz": (
            "ω_E ≈ 2 × ω_B under weak confinement."
        ),
        "all_internal_modes_Hz": (
            "Compute all three frequencies in one call."
        ),
        "modes_for_material": (
            "Look up spin-wave params by material key and "
            "compute modes; cross-references "
            "skyrmion_rkky.SKYRMION_MATERIALS for radius."
        ),
        "coupling_strength": (
            "Estimate skyrmion-phonon coupling via eta_spatial "
            "(R / phonon-wavelength) and magnetoelastic g_me."
        ),
    },
    "integration_with_other_modules": {
        "skyrmion_rkky.py": (
            "Provides Q, RKKY coupling, LLG integrator, and "
            "SKYRMION_MATERIALS catalog. This module reuses "
            "the same material keys and adds spin-wave "
            "parameters."
        ),
        "magnon_polaron_hybridization.py": (
            "Established the magnon-polaron concept for uniform "
            "spin-wave modes in quartz + Fe defects. This "
            "module generalizes to topological textures: the "
            "three skyrmion internal modes each hybridize with "
            "a different phonon channel."
        ),
        "multi_channel_coupling.py": (
            "Provides the 5 coupling channels (magnetostrictive, "
            "optical phonon, acoustic phonon, thermal, piezo, "
            "spin-orbit). Skyrmion internal modes couple "
            "through the same magnetoelastic constants (B₁ "
            "for diagonal strain, B₂ for off-diagonal)."
        ),
    },
    "assumptions_stated": [
        (
            "Frequencies are closed-form order-of-magnitude "
            "estimates. Experimental values can differ by a "
            "factor of 2-5 due to dropped geometric factors, "
            "confinement details, and temperature dependence."
        ),
        (
            "Gyrotropic formula is R-independent; for strongly "
            "confined skyrmions the frequency acquires an "
            "additional ~1/R dependence."
        ),
        (
            "Breathing formula uses exchange stiffness alone; "
            "for skyrmions near the collapse transition, "
            "anisotropy and field contributions become "
            "significant."
        ),
        (
            "Elliptic multiplier defaults to 2 (weak "
            "confinement); for strongly confined skyrmions it "
            "can be as high as 4."
        ),
        (
            "Magnetoelastic constants default to B ~ 10⁶ J/m³; "
            "real values range from 10⁵ (weakly coupled) to "
            "10⁸ (strongly coupled) depending on the material."
        ),
    ],
}


# ════════════════════════════════════════════════════════
# PRINT SUMMARY
# ════════════════════════════════════════════════════════

def print_summary() -> None:
    """Run the full reference walkthrough."""
    bar = "=" * 72
    sub = "-" * 72

    print(bar)
    print("SKYRMION-PHONON COUPLING — REFERENCE")
    print(bar)
    print()
    print(AI_REFERENCE["purpose"])
    print()

    print(sub)
    print("THREE INTERNAL MODES")
    print(sub)
    for name, spec in SKYRMION_INTERNAL_MODES.items():
        print(f"\n  {name}  (order {spec['order']})")
        print(f"    symmetry:   {spec['symmetry']}")
        print(f"    frequency:  {spec['typical_freq_GHz']} GHz")
        print(f"    scaling:    {spec['freq_scaling']}")
        print(f"    phonon:     {spec['phonon_channel']}")
    print()

    print(sub)
    print("MODE FREQUENCIES BY MATERIAL")
    print(sub)
    header = (
        f"  {'material':<12s}  "
        f"{'R (nm)':>7s}  "
        f"{'ω_G (GHz)':>10s}  "
        f"{'ω_B (GHz)':>10s}  "
        f"{'ω_E (GHz)':>10s}"
    )
    print(header)
    print(f"  {'-' * 70}")
    try:
        from skyrmion_rkky import SKYRMION_MATERIALS
        radius_source = SKYRMION_MATERIALS
    except ImportError:
        radius_source = {}
    for name in SKYRMION_SPINWAVE_PARAMS:
        R_nm = radius_source.get(name, {}).get(
            "skyrmion_radius_nm", 10.0
        )
        modes = modes_for_material(name, radius_nm=R_nm)
        print(
            f"  {name:<12s}  {R_nm:>7.1f}  "
            f"{modes['gyrotropic']/1e9:>10.3f}  "
            f"{modes['breathing']/1e9:>10.3f}  "
            f"{modes['elliptic']/1e9:>10.3f}"
        )
    print()

    print(sub)
    print("PHONON COUPLING — GdRu2Si2 breathing mode")
    print(sub)
    modes = modes_for_material("GdRu2Si2")
    p = SKYRMION_SPINWAVE_PARAMS["GdRu2Si2"]
    for mode_name in ("gyrotropic", "breathing", "elliptic"):
        c = coupling_strength(
            mode_name=mode_name,
            skyrmion_radius_nm=1.9,
            mode_frequency_Hz=modes[mode_name],
            sound_speed_ms=p["sound_speed_ms"],
        )
        print(f"\n  mode: {mode_name}")
        print(f"    frequency:            {modes[mode_name]/1e9:.2f} GHz")
        print(f"    channel:              {c['channel']}")
        print(f"    phonon wavelength:    {c['phonon_wavelength_nm']:.1f} nm")
        print(f"    eta_spatial (R/λ):    {c['eta_spatial']:.3e}")
        print(f"    g_magnetoelastic:     {c['g_magnetoelastic']:.3e}")
        print(f"    g_dimensionless:      {c['g_dimensionless']:.3e}")
    print()

    print(sub)
    print("ASSUMPTIONS — stated")
    print(sub)
    for i, a in enumerate(AI_REFERENCE["assumptions_stated"], 1):
        print(f"  {i}. {a}")
    print()
    print(bar)


if __name__ == "__main__":
    print_summary()
