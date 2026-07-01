#!/usr/bin/env python3
# kicked_relaxor_kernel.py
# earth-systems-physics / cascade_transfer — the sign-agnostic kernel.
# ONE stroboscopic map underlies boreal_recovery_ratchet (extraction collapse)
# AND fuel_load_ratchet (fire-exclusion megafire). They are not analogous —
# they are the SAME map. Only the valuation of the relaxation target A and
# which side of a threshold counts as failure differ.
#
#   between kicks:  x_pre' = A - (A - x_post) * exp(-T/tau)
#   at each kick:   x_post = r * x_pre            (0 < r < 1)
#   fixed point:    x* = A*(1 - e) / (1 - r*e),   e = exp(-T/tau)
#
# orientation "reach" : system SHOULD reach A (mature forest). fail if x* < theta.
# orientation "avoid" : system SHOULD avoid A (max fuel).       fail if x* > theta.
# The stable point the math finds = where a sustainable kick-period sits.
# CC0. stdlib only.

import math


def fixed_point(A, tau, r, T):
    """Stroboscopic (pre-kick) fixed point. One formula, both domains."""
    e = math.exp(-T / tau)
    return A * (1.0 - e) / (1.0 - r * e)


def verdict(x_star, A, theta, orientation):
    frac = x_star / A
    if orientation == "reach":
        return "OK" if frac >= theta else "FAIL (never reaches safe pole)"
    if orientation == "avoid":
        return "OK" if frac <= theta else "FAIL (ratchets to unsafe pole)"
    raise ValueError(orientation)


# name, A, tau, r, T, theta, orientation, source
CASES = [
    ("boreal bryophyte  (harvest 70y)", 1.0, 120, 0.10, 70, 0.70, "reach"),
    ("boreal broadleaf  (harvest 70y)", 1.0,  30, 0.15, 70, 0.70, "reach"),
    ("cultural burning  (return  5y)",  1.0,  25, 0.10,  5, 0.50, "avoid"),
    ("fire suppression  (return 90y)",  1.0,  25, 0.10, 90, 0.50, "avoid"),
]


def critical_period(A, tau, r, theta, orientation):
    """Kick period T at which x*/A crosses theta — the sustainability boundary."""
    # solve A(1-e)/(1-r e) = theta*A  ->  e = (1-theta)/(1 - r*theta)
    e_star = (1.0 - theta) / (1.0 - r * theta)
    if not (0.0 < e_star < 1.0):
        return None
    return -tau * math.log(e_star)


if __name__ == "__main__":
    print(f"{'case':<34}{'x*/A':>7}{'orient':>9}  verdict")
    for name, A, tau, r, T, theta, orient in CASES:
        xs = fixed_point(A, tau, r, T)
        Tc = critical_period(A, tau, r, theta, orient)
        print(f"{name:<34}{xs/A:>7.2f}{orient:>9}  {verdict(xs, A, theta, orient)}"
              f"   [T_crit={Tc:.0f}y]" if Tc else "")
    print("\nSame formula x* = A(1-e)/(1-r*e) for every row.")
    print("orientation only flips which side of theta is failure.")
    print("reach: keep T >= T_crit (long recovery window: retention, longer rotation).")
    print("avoid: keep T <= T_crit (frequent low-severity kicks: cultural burning).")
    print("=> failure is ALWAYS the kick period on the wrong side of T_crit.")
    print("   extraction violates by kicking too OFTEN; fire-exclusion, too RARELY.")
    print("   one boundary object, two directions of violation.")
