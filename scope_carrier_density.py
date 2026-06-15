"""
scope_carrier_density.py
====================================================================
The LLSVP density "conflict" as a scope-carrier demonstration.

CLAIM under test:
  two methods report OPPOSITE-SIGN density anomalies for the same
  region, and this is NOT a contradiction. it is two scoped
  functionals of one field. restore the carrier (the sensitivity
  kernel) and the disagreement becomes a second equation that
  RESOLVES the vertical structure neither method could see alone.

  reported value  =  <K | drho>  =  integral K(z) * drho(z) dz
     drho(z) = the real field        (scope-INVARIANT)
     K(z)    = the method's kernel    (the SCOPE / carrier)
  stripping K and comparing <K1|drho> vs <K2|drho> as if both were
  drho is the scope-carrier violation.

stdlib only. CC0. github.com/JinnZ2  (scope_carrier_check family)
====================================================================
"""

import math

# --------------------------------------------------------------------
# DOMAIN: height z above the core-mantle boundary, 0..1000 km
# --------------------------------------------------------------------
Z0, Z1, DZ = 0.0, 1000.0, 2.0
GRID = [Z0 + i * DZ for i in range(int((Z1 - Z0) / DZ) + 1)]

def integ(f):                      # trapezoid over the grid
    vals = [f(z) for z in GRID]
    return DZ * (sum(vals) - 0.5 * (vals[0] + vals[-1]))

def normalize(K):                  # unit-integral kernel -> output is a weighted avg
    A = integ(K)
    return lambda z: K(z) / A

# --------------------------------------------------------------------
# THE TRUE FIELD  (scope-invariant) — STRATIFIED, sign changes w/ depth
#   dense basal sliver  (chemical pile)   : 0-100 km  drho = +1.5 %
#   hot buoyant bulk    (thermal)         : 100-1000 km drho = -0.5 %
# --------------------------------------------------------------------
DENSE_TOP   = 100.0
DRHO_DENSE  = +1.5
DRHO_BULK   = -0.5

def drho(z):
    return DRHO_DENSE if z < DENSE_TOP else DRHO_BULK

def layer_dense(z): return 1.0 if z < DENSE_TOP else 0.0
def layer_bulk(z):  return 0.0 if z < DENSE_TOP else 1.0

# --------------------------------------------------------------------
# THE TWO CARRIERS (kernels) — different physics, different depth weight
#   tidal    : body tides. broad, deep-weighted (gravitational lever to
#              deep mass). SEES the basal sliver (peak at the CMB).
#   stoneley : CMB normal modes. kinetic energy rho*u^2 peaks a bit ABOVE
#              the very base; thin basal sliver is under-resolved.
# --------------------------------------------------------------------
K_tidal    = normalize(lambda z: math.exp(-z / 250.0))
K_stoneley = normalize(lambda z: math.exp(-((z - 250.0) / 120.0) ** 2))
# a REDUNDANT carrier: looks like tidal. used to show carrier contrast
# is what gives resolving power (same carrier => no new information).
K_tidal2   = normalize(lambda z: math.exp(-z / 270.0))

def project(K):                    # <K | drho>
    return integ(lambda z: K(z) * drho(z))

def weights(K):                    # how much of K sits on each layer
    return integ(lambda z: K(z) * layer_dense(z)), \
           integ(lambda z: K(z) * layer_bulk(z))

# --------------------------------------------------------------------
# 2x2 SOLVE (stdlib, closed form)
# --------------------------------------------------------------------
def solve2(M, y):
    (a, b), (c, d) = M
    det = a * d - b * c
    if abs(det) < 1e-9:
        return None, det
    x0 = (y[0] * d - y[1] * b) / det
    x1 = (a * y[1] - c * y[0]) / det
    return (x0, x1), det

def row_normalized_det(M):         # carrier-contrast metric in [0,1]-ish
    (a, b), (c, d) = M
    n1 = math.hypot(a, b); n2 = math.hypot(c, d)
    return abs(a / n1 * d / n2 - b / n1 * c / n2)   # |sin(angle between rows)|


# ====================================================================
if __name__ == "__main__":
    print("=" * 66)
    print("STEP 1 — forward project the ONE field through each carrier")
    print("-" * 66)
    y_tidal    = project(K_tidal)
    y_stoneley = project(K_stoneley)
    print(f"  true field: +{DRHO_DENSE}% (0-{DENSE_TOP:.0f}km)  "
          f"{DRHO_BULK}% ({DENSE_TOP:.0f}-1000km)")
    print(f"  <K_tidal   | drho> = {y_tidal:+.3f} %   (denser)")
    print(f"  <K_stoneley| drho> = {y_stoneley:+.3f} %   (lighter)")
    print(f"  --> OPPOSITE SIGNS from ONE field. neither method is wrong.")

    print("\n" + "=" * 66)
    print("STEP 2 — recover the carriers (per-layer weights = matrix M)")
    print("-" * 66)
    a, b = weights(K_tidal)
    c, d = weights(K_stoneley)
    print(f"  K_tidal    weight  dense={a:.3f}  bulk={b:.3f}")
    print(f"  K_stoneley weight  dense={c:.3f}  bulk={d:.3f}")
    print(f"  (tidal puts {a:.0%} on the sliver; stoneley only {c:.0%})")

    print("\n" + "=" * 66)
    print("STEP 3 — joint inversion: 2 scoped numbers -> vertical structure")
    print("-" * 66)
    M = [[a, b], [c, d]]
    x, det = solve2(M, [y_tidal, y_stoneley])
    print(f"  solve  M x = [{y_tidal:+.3f}, {y_stoneley:+.3f}]")
    print(f"  recovered  drho_dense = {x[0]:+.3f} %   (true {DRHO_DENSE:+.1f})")
    print(f"  recovered  drho_bulk  = {x[1]:+.3f} %   (true {DRHO_BULK:+.1f})")
    print(f"  carrier-contrast (|sin angle between kernels|) = "
          f"{row_normalized_det(M):.3f}")
    print(f"  --> the DISAGREEMENT was the resolving power. one field,")
    print(f"      two carriers, the layering falls out.")

    print("\n" + "=" * 66)
    print("STEP 4 — degeneracy control: two REDUNDANT carriers")
    print("-" * 66)
    a2, b2 = weights(K_tidal2)
    Mbad = [[a, b], [a2, b2]]
    contrast = row_normalized_det(Mbad)
    xbad, detbad = solve2(Mbad, [project(K_tidal), project(K_tidal2)])
    print(f"  K_tidal2 ~ K_tidal (same carrier shape)")
    print(f"  carrier-contrast = {contrast:.4f}   (near 0 = redundant)")
    if xbad:
        print(f"  recovered drho_dense = {xbad[0]:+.2f}  drho_bulk = {xbad[1]:+.2f}")
        print(f"  --> ill-conditioned: tiny carrier diff, layering NOT separable.")
    print(f"  same carrier twice = no new information. you need CONTRAST,")
    print(f"  not another measurement. more single-method numbers don't help.")
    print("=" * 66)
