# skyrmion_rkky.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
skyrmion_rkky.py
────────────────
Magnetic skyrmions stabilized by RKKY (Ruderman-Kittel-Kasuya-
Yosida) oscillatory exchange coupling.

Provides:
  - Topological charge calculation (skyrmion number Q)
  - RKKY oscillatory coupling J(r) in 1D, 2D, 3D
  - Skyrmion ansatz field generator (Néel and Bloch types)
  - Single-step Landau-Lifshitz-Gilbert (LLG) integrator
  - Reference parameters for known skyrmion-hosting materials

Place in the repo:
  - Companion to layer_0b_magnomechanical.py and
    magnonic_sublayer.py — extends the magnomechanical layer
    with topological magnetic textures
  - Skyrmions are stable because Q is a topological invariant,
    not because of energy minimization alone — they cannot be
    smoothly deformed into the uniform ferromagnetic state
  - RKKY coupling is one of the stabilization mechanisms for
    skyrmion lattices in centrosymmetric materials, i.e.
    materials that lack the Dzyaloshinskii-Moriya interaction
    (DMI) used by classic non-centrosymmetric skyrmion hosts
    like MnSi and FeGe

Physics references:
  Topological charge:
    Q = (1 / 4π) ∫ m · (∂m/∂x × ∂m/∂y) dx dy
    Counts how many times m wraps the unit sphere over the
    2D plane. Q = ±1 for a single skyrmion. Topologically
    protected: cannot change by smooth deformation of m.

  RKKY interaction:
    H_RKKY = -Σᵢⱼ Jᵢⱼ Sᵢ · Sⱼ
    The coupling Jᵢⱼ oscillates with distance. In d dimensions
    the asymptotic form is:
      d=1:  J(r) ∝ -cos(2 k_F r) / r
      d=2:  J(r) ∝  cos(2 k_F r) / r²
      d=3:  J(r) ∝ [2 k_F r cos(2 k_F r) - sin(2 k_F r)] / r⁴
    The sign oscillation creates the frustration that
    stabilizes skyrmion lattices without DMI.

  Landau-Lifshitz-Gilbert equation:
    ∂m/∂t = -|γ| m × H_eff + α m × ∂m/∂t
    Implicit form solved here in explicit Landau-Lifshitz form:
      ∂m/∂t = -|γ|/(1+α²) m × H_eff
              -α |γ|/(1+α²) m × (m × H_eff)

CC0 — No rights reserved.
"""

import math
from typing import Dict, List, Tuple, Optional

import numpy as np


# ════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════

GAMMA_E = 1.7608597e11   # electron gyromagnetic ratio (rad / s / T)
HBAR    = 1.0545718e-34  # reduced Planck constant (J · s)
K_B     = 1.380649e-23   # Boltzmann constant (J / K)
MU_0    = 4 * np.pi * 1e-7  # vacuum permeability (H / m)


# ════════════════════════════════════════════════════════
# REFERENCE MATERIALS
# ════════════════════════════════════════════════════════
#
# Approximate parameters for materials that host skyrmion
# lattice phases. Sources are experimental literature on
# small-angle neutron scattering and Lorentz TEM imaging.

SKYRMION_MATERIALS = {
    "MnSi": {
        "type": "non-centrosymmetric",
        "skyrmion_radius_nm": 9.0,
        "ordering_temperature_K": 29.5,
        "stabilization_mechanism": (
            "Dzyaloshinskii-Moriya interaction"
        ),
        "rkky_relevant": False,
        "notes": (
            "Classic B20 helimagnet; first observed skyrmion "
            "lattice (Mühlbauer et al. 2009)"
        ),
    },
    "Gd2PdSi3": {
        "type": "centrosymmetric",
        "skyrmion_radius_nm": 2.5,
        "ordering_temperature_K": 21.0,
        "stabilization_mechanism": (
            "RKKY frustration + 4-spin interaction"
        ),
        "rkky_relevant": True,
        "notes": (
            "Triangular lattice; Kurumaji et al. 2019. "
            "Small skyrmions stabilized by RKKY without DMI."
        ),
    },
    "Gd3Ru4Al12": {
        "type": "centrosymmetric",
        "skyrmion_radius_nm": 2.8,
        "ordering_temperature_K": 18.5,
        "stabilization_mechanism": (
            "RKKY oscillation + competing Heisenberg"
        ),
        "rkky_relevant": True,
        "notes": (
            "Hirschberger et al. 2019 — skyrmion lattice "
            "in a centrosymmetric crystal."
        ),
    },
    "GdRu2Si2": {
        "type": "centrosymmetric",
        "skyrmion_radius_nm": 1.9,
        "ordering_temperature_K": 46.0,
        "stabilization_mechanism": (
            "RKKY + magnetic anisotropy"
        ),
        "rkky_relevant": True,
        "notes": (
            "Khanh et al. 2020 — among the smallest "
            "centrosymmetric skyrmions reported."
        ),
    },
    "FeGe": {
        "type": "non-centrosymmetric",
        "skyrmion_radius_nm": 35.0,
        "ordering_temperature_K": 278.0,
        "stabilization_mechanism": (
            "Dzyaloshinskii-Moriya interaction"
        ),
        "rkky_relevant": False,
        "notes": (
            "Near-room-temperature skyrmion host; "
            "Yu et al. 2011"
        ),
    },
}


# ════════════════════════════════════════════════════════
# TOPOLOGICAL CHARGE
# ════════════════════════════════════════════════════════

def compute_topological_charge(m: np.ndarray) -> float:
    """Compute the skyrmion number Q for a 2D magnetization field.

    Q = (1 / 4π) ∫ m · (∂m/∂x × ∂m/∂y) dx dy

    Uses central-difference approximation for the partial
    derivatives. For a textbook skyrmion ansatz contained well
    inside the grid, |Q| is very close to 1.

    Args:
        m: numpy array of shape (nx, ny, 3), normalized
           magnetization vector field. |m| should be 1 at every
           site (pass through make_skyrmion_field for a guarantee).

    Returns:
        Topological charge Q. ±1 for a single skyrmion, 0 for
        a uniform ferromagnet, larger integers for higher-order
        textures.
    """
    if m.ndim != 3 or m.shape[2] != 3:
        raise ValueError(
            f"m must have shape (nx, ny, 3); got {m.shape}"
        )

    dm_dx = np.zeros_like(m)
    dm_dy = np.zeros_like(m)
    for c in range(3):
        dm_dx[..., c] = np.gradient(m[..., c], axis=0)
        dm_dy[..., c] = np.gradient(m[..., c], axis=1)

    # ∂m/∂x × ∂m/∂y at every grid point
    cross = np.cross(dm_dx, dm_dy)
    integrand = np.sum(m * cross, axis=-1)
    Q = float(np.sum(integrand) / (4.0 * np.pi))
    return Q


# ════════════════════════════════════════════════════════
# RKKY COUPLING
# ════════════════════════════════════════════════════════

def rkky_coupling(
    r: float,
    k_F: float,
    J0: float = 1.0,
    dimension: int = 3,
) -> float:
    """RKKY exchange coupling J(r) for a given distance.

    The asymptotic form of the RKKY interaction in d dimensions:

        d=1:  J(r) ∝ -cos(2 k_F r) / r
        d=2:  J(r) ∝  cos(2 k_F r) / r²
        d=3:  J(r) ∝ [2 k_F r cos(2 k_F r) - sin(2 k_F r)] / r⁴

    The oscillation period 2π / (2 k_F) = π / k_F sets the
    frustration length scale. When this length matches the
    skyrmion radius, the lattice phase is energetically
    favorable in centrosymmetric materials.

    Args:
        r: distance between magnetic moments (any consistent unit)
        k_F: Fermi wave vector in conduction band (1 / r-units)
        J0: overall coupling strength (energy units)
        dimension: 1, 2, or 3

    Returns:
        J(r), can be positive (FM) or negative (AFM).
    """
    if r <= 0:
        raise ValueError("r must be positive")
    if dimension not in (1, 2, 3):
        raise ValueError(
            f"dimension must be 1, 2, or 3; got {dimension}"
        )

    x = 2.0 * k_F * r
    if dimension == 1:
        return float(J0 * (-math.cos(x) / r))
    if dimension == 2:
        return float(J0 * math.cos(x) / (r ** 2))
    return float(
        J0 * (x * math.cos(x) - math.sin(x)) / (r ** 4)
    )


def rkky_period(k_F: float) -> float:
    """RKKY oscillation period in distance units.

    Returns π / k_F. Two adjacent zero crossings of J(r) are
    separated by this distance.
    """
    return math.pi / k_F


# ════════════════════════════════════════════════════════
# SKYRMION ANSATZ
# ════════════════════════════════════════════════════════

def make_skyrmion_field(
    nx: int,
    ny: int,
    radius: float,
    polarity: int = 1,
    vorticity: int = 1,
    helicity: float = 0.0,
    center: Optional[Tuple[float, float]] = None,
) -> np.ndarray:
    """Generate a textbook skyrmion magnetization field.

    Standard ansatz:
        m_x = sin(θ(r)) cos(vorticity · φ + helicity)
        m_y = sin(θ(r)) sin(vorticity · φ + helicity)
        m_z = cos(θ(r)) · polarity

    where θ(r) is a smooth profile that goes from π at the core
    to 0 at infinity (so m_z(0) = -polarity, m_z(∞) = +polarity),
    and φ is the in-plane azimuth.

    Args:
        nx, ny:    grid dimensions
        radius:    skyrmion radius in lattice units
        polarity:  ±1; sign that flips the m_z direction
        vorticity: integer winding number (default 1)
        helicity:  in-plane phase (default 0 = Néel skyrmion;
                   π/2 = Bloch skyrmion)
        center:    (x0, y0) center coordinates; default is
                   the grid center

    Returns:
        numpy array of shape (nx, ny, 3) with |m|=1 at every site.
    """
    if center is None:
        center = ((nx - 1) / 2.0, (ny - 1) / 2.0)

    x = np.arange(nx).reshape(-1, 1) - center[0]
    y = np.arange(ny).reshape(1, -1) - center[1]
    r = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)

    # Smooth profile: θ(0) = π, θ(∞) → 0
    # Gaussian profile gives Q ≈ ±1 for radius << grid size.
    theta = np.pi * np.exp(-(r / radius) ** 2)

    sign = float(polarity)

    m = np.zeros((nx, ny, 3))
    m[..., 0] = np.sin(theta) * np.cos(vorticity * phi + helicity)
    m[..., 1] = np.sin(theta) * np.sin(vorticity * phi + helicity)
    m[..., 2] = np.cos(theta) * sign

    # Numerical normalization
    norms = np.sqrt(np.sum(m ** 2, axis=-1, keepdims=True))
    m = m / np.clip(norms, 1e-12, None)

    return m


def make_uniform_field(
    nx: int, ny: int, direction: Tuple[float, float, float] = (0, 0, 1),
) -> np.ndarray:
    """Uniform ferromagnetic background. Q = 0 by construction."""
    d = np.array(direction, dtype=float)
    d = d / np.linalg.norm(d)
    m = np.zeros((nx, ny, 3))
    m[..., :] = d
    return m


# ════════════════════════════════════════════════════════
# LLG INTEGRATOR
# ════════════════════════════════════════════════════════

def llg_step(
    m: np.ndarray,
    H_eff: np.ndarray,
    gamma: float = GAMMA_E,
    alpha: float = 0.05,
    dt: float = 1e-13,
) -> np.ndarray:
    """One timestep of the Landau-Lifshitz-Gilbert equation.

    The Gilbert form:
        ∂m/∂t = -|γ| m × H_eff + α m × ∂m/∂t

    Solved in the explicit Landau-Lifshitz form (algebraically
    equivalent, with ∂m/∂t isolated on the left):
        ∂m/∂t = -|γ| / (1 + α²) m × H_eff
                - α |γ| / (1 + α²) m × (m × H_eff)

    Args:
        m:     current magnetization, shape (..., 3), |m|=1
        H_eff: effective field (T), same shape as m
        gamma: gyromagnetic ratio (rad / s / T)
        alpha: Gilbert damping (dimensionless)
        dt:    timestep (seconds)

    Returns:
        new m, renormalized to |m|=1.
    """
    if m.shape != H_eff.shape:
        raise ValueError(
            "m and H_eff must have the same shape; "
            f"got {m.shape} vs {H_eff.shape}"
        )
    if m.shape[-1] != 3:
        raise ValueError(
            f"last axis must be size 3; got {m.shape[-1]}"
        )

    g = abs(gamma) / (1.0 + alpha ** 2)
    cross1 = np.cross(m, H_eff)
    cross2 = np.cross(m, cross1)

    dm_dt = -g * cross1 - alpha * g * cross2
    m_new = m + dt * dm_dt

    norms = np.sqrt(np.sum(m_new ** 2, axis=-1, keepdims=True))
    return m_new / np.clip(norms, 1e-12, None)


# ════════════════════════════════════════════════════════
# DEMO
# ════════════════════════════════════════════════════════

def print_summary() -> None:
    """Build a skyrmion ansatz, compute Q, sample RKKY coupling,
    run one LLG step. Verifies the math runs end-to-end."""
    bar = "=" * 70
    sub = "-" * 70

    print(bar)
    print("SKYRMION + RKKY — REFERENCE")
    print(bar)
    print()
    print("Topological charge:")
    print("  Q = (1 / 4π) ∫ m · (∂m/∂x × ∂m/∂y) dx dy")
    print("RKKY coupling (centrosymmetric stabilization):")
    print("  J(r) ∝ cos(2 k_F r) / r^d")
    print("Landau-Lifshitz-Gilbert dynamics:")
    print("  ∂m/∂t = -|γ| m × H_eff + α m × ∂m/∂t")
    print()

    print(sub)
    print("REFERENCE MATERIALS")
    print(sub)
    for name, spec in SKYRMION_MATERIALS.items():
        tag = "RKKY" if spec["rkky_relevant"] else "DMI "
        print(
            f"  {name:14s}  r={spec['skyrmion_radius_nm']:>5.1f} nm  "
            f"T_c={spec['ordering_temperature_K']:>5.1f} K  [{tag}]"
        )
    print()

    print(sub)
    print("TOPOLOGICAL CHARGE — verification")
    print(sub)
    m_uniform = make_uniform_field(64, 64)
    Q_uniform = compute_topological_charge(m_uniform)
    print(f"  Uniform ferromagnet:                   Q = {Q_uniform:+.4f}")

    m_neel = make_skyrmion_field(
        nx=128, ny=128, radius=12.0,
        polarity=1, vorticity=1, helicity=0.0,
    )
    Q_neel = compute_topological_charge(m_neel)
    print(f"  Néel skyrmion (polarity=+1):           Q = {Q_neel:+.4f}")

    m_neel_neg = make_skyrmion_field(
        nx=128, ny=128, radius=12.0,
        polarity=-1, vorticity=1, helicity=0.0,
    )
    Q_neel_neg = compute_topological_charge(m_neel_neg)
    print(f"  Polarity-flipped (polarity=-1):        Q = {Q_neel_neg:+.4f}")

    m_bloch = make_skyrmion_field(
        nx=128, ny=128, radius=12.0,
        polarity=1, vorticity=1, helicity=math.pi / 2,
    )
    Q_bloch = compute_topological_charge(m_bloch)
    print(f"  Bloch skyrmion (helicity=π/2):         Q = {Q_bloch:+.4f}")
    print()
    print("  (Néel and Bloch share the same Q — helicity does not")
    print("   affect topology, only the in-plane texture.)")
    print()

    print(sub)
    print("RKKY COUPLING J(r)")
    print(sub)
    k_F = 1.0  # arbitrary inverse-length units
    period = rkky_period(k_F)
    print(f"  k_F = {k_F:.2f},  oscillation period π/k_F = {period:.3f}")
    print(
        f"  {'r':>8}  {'J_1D':>10s}  {'J_2D':>10s}  {'J_3D':>10s}"
    )
    for r in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0):
        j1 = rkky_coupling(r, k_F, J0=1.0, dimension=1)
        j2 = rkky_coupling(r, k_F, J0=1.0, dimension=2)
        j3 = rkky_coupling(r, k_F, J0=1.0, dimension=3)
        print(
            f"  {r:>8.2f}  {j1:>+10.4f}  {j2:>+10.4f}  {j3:>+10.4f}"
        )
    print()
    print("  Sign oscillation creates the frustration that stabilizes")
    print("  skyrmion lattices in centrosymmetric materials (no DMI).")
    print()

    print(sub)
    print("LLG STEP — single integration")
    print(sub)
    # Tilted spin in a uniform field along z
    m_test = np.array([[[math.sin(0.3), 0.0, math.cos(0.3)]]])
    H_test = np.array([[[0.0, 0.0, 1.0]]])  # 1 T along z
    m_new = llg_step(m_test, H_test, alpha=0.05, dt=1e-13)
    print(
        f"  Initial m: ({m_test[0,0,0]:+.4f}, {m_test[0,0,1]:+.4f}, "
        f"{m_test[0,0,2]:+.4f})"
    )
    print(f"  After 1 step (1 ps, α=0.05):")
    print(
        f"             ({m_new[0,0,0]:+.4f}, {m_new[0,0,1]:+.4f}, "
        f"{m_new[0,0,2]:+.4f})"
    )
    print(
        f"  |m| (should be 1.0):  "
        f"{float(np.linalg.norm(m_new[0,0])):.6f}"
    )
    print()
    print(bar)


if __name__ == "__main__":
    print_summary()
