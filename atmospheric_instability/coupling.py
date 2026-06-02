"""
coupling.py  --  CC0

Mode interaction layer. When one instability becomes active and breaks, it
deposits momentum / mixes / releases heat -> changes the background -> can
trigger or suppress OTHER modes. This is the cascade engine.

Each edge is a physical mechanism with a sign:
  +  amplifying (breaking of A pushes B toward instability)
  -  damping    (breaking of A pushes B toward stability)

The graph is grounded in real feedbacks but is the most model-dependent layer
(see CLAIM_TABLE). Edges are hypotheses, each falsifiable.
"""

# edge: (source_mode, target_mode, sign, mechanism, strength 0..1)
COUPLING_EDGES = [
    ("convective", "gravity_wave", +1,
     "convective overturning launches gravity waves (momentum source)", 0.8),
    ("gravity_wave", "kelvin_helmholtz", +1,
     "GW breaking deposits momentum -> local shear spike -> Ri drops", 0.7),
    ("gravity_wave", "baroclinic_eady", +1,
     "GW drag modifies mean jet -> alters shear feeding baroclinic mode", 0.4),
    ("kelvin_helmholtz", "convective", -1,
     "KH turbulent mixing homogenizes layer -> raises N2 locally -> damps convection", 0.5),
    ("baroclinic_eady", "rossby_barotropic", +1,
     "baroclinic eddies feed jet meander -> sharpen curvature -> barotropic prone", 0.6),
    ("baroclinic_eady", "baroclinic_eady", -1,
     "eddy heat flux flattens meridional gradient -> self-limiting (negative feedback)", 0.7),
    ("rossby_barotropic", "baroclinic_eady", +1,
     "blocking/wave-breaking re-sharpens local gradients -> re-energizes baroclinic", 0.5),
    ("inertial", "symmetric", +1,
     "inertial adjustment lowers PV -> favors slantwise symmetric instability", 0.6),
    ("symmetric", "convective", +1,
     "slantwise overturning can trigger upright convection at saturation", 0.5),
    ("convective", "baroclinic_eady", -1,
     "deep convection vertically mixes -> reduces effective shear aloft", 0.3),
]


def build_adjacency():
    adj = {}
    for src, tgt, sign, mech, strength in COUPLING_EDGES:
        adj.setdefault(src, []).append((tgt, sign, mech, strength))
    return adj


def trace_cascade(active_modes, adj=None, max_depth=4):
    """
    Given a set of currently-active (broken) modes, trace which modes they
    push toward instability (sign +) following amplifying edges, breadth-first.

    Returns ordered list of cascade steps:
       [(depth, source, target, sign, mechanism, strength), ...]
    Damping edges are reported but do not propagate the cascade.
    """
    adj = adj or build_adjacency()
    steps = []
    seen = set(active_modes)
    frontier = [(0, m) for m in active_modes]

    while frontier:
        depth, node = frontier.pop(0)
        if depth >= max_depth:
            continue
        for tgt, sign, mech, strength in adj.get(node, []):
            steps.append((depth + 1, node, tgt, sign, mech, strength))
            if sign > 0 and tgt not in seen:
                seen.add(tgt)
                frontier.append((depth + 1, tgt))
    return steps


def cascade_reachable(active_modes, adj=None, max_depth=4):
    """Set of modes reachable via amplifying edges from the active set."""
    adj = adj or build_adjacency()
    seen = set(active_modes)
    frontier = list(active_modes)
    while frontier:
        node = frontier.pop()
        for tgt, sign, _m, _s in adj.get(node, []):
            if sign > 0 and tgt not in seen:
                seen.add(tgt)
                frontier.append(tgt)
    return seen - set(active_modes)
