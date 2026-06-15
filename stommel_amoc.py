# stommel_amoc.py
# repo: earth-systems-physics   CC0   stdlib only   phone-buildable
# Replaces the linearized AMOC gate in layer_hydrosphere() with the real
# two-box salt-advection bistability. Hysteresis, not threshold.
#
# Stommel '61 two-box (T,S contrast between low & high latitude box):
#   q = k * |a*dT - b*dS|              flow magnitude, sign-agnostic transport
#   dT/dt = -(dT - dT_atm)/t_r - |q| dT
#   dS/dt =  H(t)            - |q| dS          H = freshwater hosing forcing
# Steady state in salinity gives a CUBIC in q -> up to 3 roots -> bistable.
# Thermal mode (q>0, sinking at pole) vs haline mode (q<0, collapsed).

import math
from dataclasses import dataclass
from constraint_RFL_geometry import Hypothesis, Constraint, Space, Tournament

# ----- physical-ish nondim params (CLAIMS, refutable) -----
A_T   = 0.2     # thermal expansion contribution to density contrast
B_S   = 0.8     # haline contraction contribution  (haline > thermal -> bistable regime)
K_FLOW= 1.0     # flow constant
T_R   = 1.0     # thermal relaxation time (fast vs salt)
DT_ATM= 1.0     # imposed equator-pole thermal contrast

# ============================================================
# 1. CORE: solve steady-state q for a given hosing H
#    At SS:  dT* = dT_atm / (1 + t_r|q|)  ,  dS* = H/|q|
#    density contrast  D = a*dT* - b*dS* ,  and  q = k*D
#    -> self-consistent root solve in q.
# ============================================================
def _q_residual(q, H):
    aq = abs(q)
    if aq < 1e-9:
        return q - K_FLOW*(A_T*DT_ATM)        # q->0 limit: salt term blows, handled by bracket
    dT = DT_ATM / (1.0 + T_R*aq)
    dS = H / aq
    D  = A_T*dT - B_S*dS
    return q - K_FLOW*D

def _bisect(f, lo, hi, H, it=200):
    flo, fhi = f(lo,H), f(hi,H)
    if flo*fhi > 0: return None
    for _ in range(it):
        mid = 0.5*(lo+hi); fm = f(mid,H)
        if abs(fm) < 1e-10: return mid
        if flo*fm < 0: hi, fhi = mid, fm
        else:          lo, flo = mid, fm
    return 0.5*(lo+hi)

def steady_states(H):
    """Return all real steady q roots by scanning sign changes. 1 or 3 roots."""
    roots, xs = [], [(-3.0 + 0.01*i) for i in range(601)]   # scan q in [-3,3]
    for i in range(len(xs)-1):
        lo, hi = xs[i], xs[i+1]
        if lo > -1e-6 and lo < 1e-6: continue                # skip singular q=0
        try:
            if _q_residual(lo,H)*_q_residual(hi,H) < 0:
                r = _bisect(_q_residual, lo, hi, H)
                if r is not None and abs(r) > 1e-4:
                    if not any(abs(r-x) < 1e-3 for x in roots):
                        roots.append(round(r,5))
        except ZeroDivisionError:
            continue
    return sorted(roots)

def stability(q, H, eps=1e-4):
    """Numerical d(residual)/dq. Stable branch: residual crosses + -> - (slope>0 here)."""
    return (_q_residual(q+eps,H) - _q_residual(q-eps,H))/(2*eps)

# ============================================================
# 2. HYSTERESIS LOOP: sweep H up then down, track which branch you sit on
#    This is the whole point: path determines state.
# ============================================================
def hysteresis_sweep(H_max=0.6, steps=60):
    Hs_up   = [H_max*i/steps for i in range(steps+1)]
    Hs_down = list(reversed(Hs_up))
    # start on thermal (strong) branch: pick most positive q
    def pick(branch_sign, q_prev, H):
        rs = steady_states(H)
        rs = [r for r in rs if stability(r,H) > 0]            # stable only
        if not rs: return q_prev, 0
        # stay closest to previous q (branch continuity)
        return min(rs, key=lambda r: abs(r-q_prev)), len(rs)
    q = max(steady_states(0.0) or [1.0])
    up = []
    for H in Hs_up:
        q,n = pick(+1,q,H); up.append((round(H,4), q, n))
    down = []
    for H in Hs_down:
        q,n = pick(-1,q,H); down.append((round(H,4), q, n))
    return up, down

# ============================================================
# 3. EARLY WARNING: critical slowing down near the fold
#    Recovery rate = |slope of residual| at the stable root.
#    -> 0 as you approach the saddle-node. THIS is the precursor.
# ============================================================
def recovery_rate(H):
    rs = [r for r in steady_states(H) if stability(r,H) > 0]
    if not rs: return 0.0
    q = max(rs, key=abs)                  # operating (thermal) branch
    return abs(stability(q,H))            # -> 0 at the bifurcation

def fold_scan(H_max=0.6, steps=60):
    out = []
    for i in range(steps+1):
        H = H_max*i/steps
        roots = steady_states(H)
        stab  = [r for r in roots if stability(r,H) > 0]
        out.append({"H":round(H,4), "n_roots":len(roots),
                    "n_stable":len(stab), "recovery":round(recovery_rate(H),4)})
    return out

# ============================================================
# 4. ASCII: hysteresis loop + critical-slowing curve
# ============================================================
def viz_hysteresis(up, down, w=58):
    print("\n"+"="*w); print("AMOC HYSTERESIS  (q vs freshwater H)".center(w)); print("="*w)
    qs = [q for _,q,_ in up+down]
    qlo, qhi = min(qs), max(qs)
    span = (qhi-qlo) or 1.0
    def row(H,q,mark):
        col = int((q-qlo)/span*(w-14))
        line = " "*col + mark
        print(f"H={H:4.2f} q={q:+5.2f} |{line}")
    print("-- ramp UP (forcing on) -->")
    for H,q,n in up[::6]: row(H,q,"█")
    print("-- ramp DOWN (forcing off) --> (note: does NOT retrace)")
    for H,q,n in down[::6]: row(H,q,"○")

def viz_slowing(scan, w=58):
    print("\n"+"="*w); print("CRITICAL SLOWING  (recovery rate -> 0 = jump imminent)".center(w)); print("="*w)
    rmax = max(s["recovery"] for s in scan) or 1.0
    for s in scan[::4]:
        bar = "▇"*int(s["recovery"]/rmax*(w-22))
        flag = "  <== FOLD" if s["n_stable"]==1 and s["recovery"]<0.05 else ""
        print(f"H={s['H']:4.2f} r={s['recovery']:5.2f} |{bar}{flag}")

# ============================================================
# 5. FuncCoupling drop-in for layer_hydrosphere()
#    Replaces the linear amoc_strength line. Emits the real branch state.
# ============================================================
def amoc_coupling_factory():
    """Returns a FuncCoupling-compatible lambda: freshwater_flux -> amoc_strength.
       amoc_strength = |q| on the branch you're continuously on from thermal start."""
    from earth_physics_constraints import FuncCoupling
    def amoc_q(p):
        H = p.get("freshwater_flux", 0.0)
        rs = [r for r in steady_states(H) if stability(r,H) > 0]
        if not rs: return 0.0
        return abs(max(rs, key=abs))      # thermal branch magnitude
    return FuncCoupling("amoc_stommel", ["freshwater_flux"], "amoc_strength", amoc_q)

# ============================================================
# 6. DEMO
# ============================================================
def demo():
    print("=== STOMMEL TWO-BOX AMOC : BISTABILITY + HYSTERESIS ===\n")

    for H in [0.0, 0.1, 0.2, 0.3, 0.5]:
        rs = steady_states(H)
        tag = "BISTABLE" if len(rs) >= 3 else "single"
        print(f"H={H:4.2f}  roots={rs}  [{tag}]")

    up, down = hysteresis_sweep(H_max=0.6, steps=60)
    viz_hysteresis(up, down)

    scan = fold_scan(H_max=0.6, steps=60)
    viz_slowing(scan)

    # the trap, stated plainly:
    H_collapse = next((s["H"] for s in scan if s["n_stable"]==1), None)
    H_recover  = None
    for H,q,n in down:
        if n >= 1 and abs(q) > 0.3:     # thermal branch reappears
            H_recover = H
    print("\n"+"-"*58)
    print(f"collapse forcing (ramp up):   H ~ {H_collapse}")
    print(f"recovery forcing (ramp down): H ~ {H_recover}")
    print("gap between them = hysteresis width = the part a threshold model erases.")

if __name__ == "__main__":
    demo()
