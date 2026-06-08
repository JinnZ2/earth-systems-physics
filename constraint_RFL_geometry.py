# constraint_RFL_geometry.py  v5
# repo: precursor-detection / RFL-engine   CC0   stdlib only   phone-buildable
#
# v5 – OSCILLATION, MULTI-TARGET, VISUALIZER.
#   - Oscillation axes: frequency, phase, Q_factor
#   - OscillationCoupling: computes resonant amplification from periodic inputs
#   - MultiTargetPlayground: finds recipes hitting multiple emergent targets simultaneously
#   - ASCII visualizer: cluster map, recipe tree, viable region scans

from dataclasses import dataclass, field
import itertools, math

# ============================================================
# 1. SPACE
# ============================================================
@dataclass
class Space:
    axes: list
    weights: dict = field(default_factory=dict)

    def weight(self, axis: str) -> float:
        return self.weights.get(axis, 1.0)

# ============================================================
# 2. HYPOTHESIS
# ============================================================
@dataclass
class Hypothesis:
    name: str
    coords: dict
    uncertainty: dict
    note: str = ""

    def distance_to(self, other: "Hypothesis", space: Space) -> float:
        sq = 0.0
        for axis in space.axes:
            diff = self.coords.get(axis, 0.0) - other.coords.get(axis, 0.0)
            w = space.weight(axis)
            sq += w * diff * diff
        return math.sqrt(sq)

    def effective_radius(self, other: "Hypothesis", space: Space) -> float:
        total = 0.0
        for axis in space.axes:
            s1 = self.uncertainty.get(axis, 0.0)
            s2 = other.uncertainty.get(axis, 0.0)
            sigma = s1 + s2
            total += sigma * sigma
        return math.sqrt(total)

# ============================================================
# 3. CONSTRAINT
# ============================================================
@dataclass
class Constraint:
    name: str
    coeffs: dict
    bound: float
    op: str = ">"
    desc: str = ""

    def violation(self, h: Hypothesis) -> float:
        val = sum(self.coeffs.get(k, 0.0) * h.coords.get(k, 0.0) for k in h.coords)
        if self.op == ">":
            return max(0.0, self.bound - val)
        elif self.op == "<":
            return max(0.0, val - self.bound)
        else:
            return abs(val - self.bound)

    def sigma_normal(self, h: Hypothesis) -> float:
        variance = 0.0
        for axis, coeff in self.coeffs.items():
            sigma_axis = h.uncertainty.get(axis, 0.0)
            variance += (coeff * sigma_axis) ** 2
        return math.sqrt(variance)

    def kills(self, h: Hypothesis, k_sigma: float = 2.0) -> tuple[bool, float, float]:
        v = self.violation(h)
        sigma = self.sigma_normal(h)
        return v > k_sigma * sigma, v, sigma

# ============================================================
# 4. COUPLING (base)
# ============================================================
@dataclass
class Coupling:
    name: str
    input_axes: list
    output_axis: str
    coeff: float = 1.0
    op: str = "product"
    threshold: float = 0.5

    def compute(self, base_point: dict) -> float:
        if self.op == "product":
            val = self.coeff
            for ax in self.input_axes:
                val *= base_point.get(ax, 0.0)
            return val
        elif self.op == "sum":
            return self.coeff * sum(base_point.get(ax, 0.0) for ax in self.input_axes)
        elif self.op == "threshold":
            if all(base_point.get(ax, 0.0) > self.threshold for ax in self.input_axes):
                return self.coeff
            else:
                return 0.0
        return 0.0

# ============================================================
# 5. OSCILLATION COUPLING – frequency, phase, Q-factor resonance
# ============================================================
@dataclass
class OscillationCoupling:
    name: str
    frequency_axis: str      # normalized frequency (0..1, where 1 = resonant)
    phase_axis: str          # phase alignment (0..1, 1 = perfect alignment)
    q_factor_axis: str       # quality factor (0..1, higher = sharper resonance)
    output_axis: str
    base_amplitude: float = 1.0

    def compute(self, base_point: dict) -> float:
        f = base_point.get(self.frequency_axis, 0.0)
        phase = base_point.get(self.phase_axis, 0.0)
        Q = base_point.get(self.q_factor_axis, 0.0)
        if Q == 0:
            return 0.0
        # Resonant amplification: gain = Q * cos(phase*pi/2) * exp(- (f-1)^2 / (2*(1/Q)^2) )
        # This creates a peak near f=1, phase=0, with width inversely proportional to Q
        detuning = f - 1.0
        sigma = 1.0 / (Q + 1e-6)  # width of resonance
        resonance_shape = math.exp(- (detuning**2) / (2 * sigma**2))
        phase_factor = math.cos(phase * math.pi / 2)  # 1 when phase=0, 0 when phase=1
        gain = Q * resonance_shape * phase_factor
        return self.base_amplitude * gain

# ============================================================
# 6. COMPOUND HYPOTHESIS (updated for oscillation)
# ============================================================
@dataclass
class CompoundHypothesis:
    name: str
    bases: list
    couplings: list          # Coupling or OscillationCoupling
    note: str = ""

    def emerge(self) -> Hypothesis:
        coords = {}
        uncertainty = {}
        for h in self.bases:
            coords.update(h.coords)
            uncertainty.update(h.uncertainty)
        for coup in self.couplings:
            val = coup.compute(coords)
            coords[coup.output_axis] = val
            # simple uncertainty prop
            var = 0.0
            for ax in (coup.input_axes if hasattr(coup, 'input_axes') else
                       [coup.frequency_axis, coup.phase_axis, coup.q_factor_axis]):
                var += (uncertainty.get(ax, 0.1)) ** 2
            uncertainty[coup.output_axis] = math.sqrt(var)
        return Hypothesis(self.name, coords, uncertainty, self.note)

# ============================================================
# 7. TOURNAMENT
# ============================================================
@dataclass
class Tournament:
    space: Space
    hypotheses: list
    constraints: list
    distinct_threshold: float = 1.0

    def run(self, k_sigma: float = 2.0) -> dict:
        resolved = []
        for item in self.hypotheses:
            if isinstance(item, CompoundHypothesis):
                resolved.append(item.emerge())
            else:
                resolved.append(item)

        alive = []
        killed = []
        for h in resolved:
            violations = []
            dead = False
            for c in self.constraints:
                is_killed, v, sigma = c.kills(h, k_sigma)
                if is_killed:
                    dead = True
                    violations.append({
                        "constraint": c.name,
                        "violation": round(v, 3),
                        "sigma_normal": round(sigma, 3),
                        "k_sigma": k_sigma
                    })
            if dead:
                killed.append((h, violations))
            else:
                alive.append(h)

        pairs = list(itertools.combinations(alive, 2))
        conflicts = []
        distinct = []
        for h1, h2 in pairs:
            d = h1.distance_to(h2, self.space)
            r = h1.effective_radius(h2, self.space)
            if d < r * self.distinct_threshold:
                conflicts.append((h1.name, h2.name, round(d,3), round(r,3)))
            else:
                distinct.append((h1.name, h2.name, round(d,3), round(r,3)))

        parent = {h.name: h.name for h in alive}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[ry] = rx
        for h1, h2 in pairs:
            d = h1.distance_to(h2, self.space)
            r = h1.effective_radius(h2, self.space)
            if d < r * self.distinct_threshold:
                union(h1.name, h2.name)
        clusters = {}
        for h in alive:
            root = find(h.name)
            clusters.setdefault(root, []).append(h.name)

        viability = len(alive)
        diversity = len(distinct)
        num_clusters = len(clusters)
        collapse = (num_clusters <= 1 and viability > 1)

        return {
            "alive": [h.name for h in alive],
            "killed": [{"name": h.name, "violations": vlist} for h, vlist in killed],
            "conflicts": conflicts,
            "distinct_pairs": distinct,
            "clusters": clusters,
            "score": {
                "viability": viability,
                "diversity": diversity,
                "connected_regions": num_clusters,
                "collapse": collapse
            },
            "resolved_hypotheses": resolved
        }

# ============================================================
# 8. MULTI-TARGET PLAYGROUND
# ============================================================
class MultiTargetPlayground:
    def __init__(self, space, constraints, input_axes, output_axes,
                 input_ranges, coupling_templates, k_sigma=2.0):
        self.space = space
        self.constraints = constraints
        self.input_axes = input_axes
        self.output_axes = output_axes   # list of axis names that must hit targets
        self.input_ranges = input_ranges
        self.coupling_templates = coupling_templates  # list of (Coupling/OscillationCoupling, output_axis)
        self.k_sigma = k_sigma

    def explore(self, targets, tolerance=0.05):
        """
        targets: dict {output_axis: target_value}
        Returns recipes where all outputs hit their targets within tolerance.
        """
        axis_values = []
        for ax in self.input_axes:
            low, high, step = self.input_ranges[ax]
            vals = []
            v = low
            while v <= high + 1e-9:
                vals.append(round(v, 4))
                v += step
            axis_values.append(vals)

        recipes = []
        for combo in itertools.product(*axis_values):
            input_dict = {ax: combo[i] for i, ax in enumerate(self.input_axes)}
            # compute all emergent values
            emergent = {}
            for coup, out_ax in self.coupling_templates:
                val = coup.compute(input_dict)
                emergent[out_ax] = val
            # check all targets
            all_hit = True
            for out_ax, target in targets.items():
                if abs(emergent.get(out_ax, 0.0) - target) > tolerance:
                    all_hit = False
                    break
            if not all_hit:
                continue
            # build full hypothesis and test constraints
            coords = dict(input_dict)
            coords.update(emergent)
            for ax in self.space.axes:
                if ax not in coords:
                    coords[ax] = 0.0
            uncertainty = {ax: 0.1 for ax in self.space.axes}
            h = Hypothesis("playground_candidate", coords, uncertainty)
            dead = False
            for c in self.constraints:
                if c.kills(h, self.k_sigma)[0]:
                    dead = True
                    break
            if not dead:
                recipes.append({
                    'inputs': input_dict,
                    'emergent': emergent,
                    'hypothesis': h
                })
        return recipes

# ============================================================
# 9. ASCII VISUALIZER
# ============================================================
def visualize_clusters(tournament_result, max_width=80):
    """ASCII art showing clusters and their connections."""
    print("\n" + "="*max_width)
    print("CLUSTER MAP".center(max_width))
    print("="*max_width)
    clusters = tournament_result["clusters"]
    for i, (root, members) in enumerate(clusters.items()):
        print(f"\n  Cluster {i+1} (root: {root}):")
        for j, m in enumerate(members):
            prefix = "  ├─ " if j < len(members)-1 else "  └─ "
            print(prefix + m)
    # distinct pairs
    if tournament_result["distinct_pairs"]:
        print("\n" + "-"*max_width)
        print("DISTINCT LINKS (no overlap):")
        for a, b, d, r in tournament_result["distinct_pairs"]:
            print(f"  {a} <─── {d:.2f} @ {r:.2f} ───> {b}")
    if tournament_result["conflicts"]:
        print("\n" + "-"*max_width)
        print("CONFLICT REGIONS (overlapping):")
        for a, b, d, r in tournament_result["conflicts"]:
            print(f"  {a} ~ {d:.2f} @ {r:.2f} ~ {b}")

def visualize_playground(recipes, max_width=80):
    """Show recipe tree from playground."""
    print("\n" + "="*max_width)
    print("PLAYGROUND RECIPE TREE".center(max_width))
    print("="*max_width)
    for i, r in enumerate(recipes):
        print(f"\n  Recipe {i+1}:")
        print(f"    Inputs: {r['inputs']}")
        print(f"    Emergent: {r['emergent']}")
        print(f"    Status: ALL CONSTRAINTS PASSED")

def visualize_viable_region(playground, target_output, scan_axes, fixed_vals,
                            resolution=10, max_width=80):
    """Scan 2D slice of viable region and show ASCII heatmap."""
    ax1, ax2 = scan_axes
    rng1 = playground.input_ranges[ax1]
    rng2 = playground.input_ranges[ax2]
    print("\n" + "="*max_width)
    print(f"VIABLE REGION SCAN: {ax1} vs {ax2}".center(max_width))
    print(f"Target: {target_output}".center(max_width))
    print("="*max_width)
    # build grid
    vals1 = [rng1[0] + i*(rng1[1]-rng1[0])/(resolution-1) for i in range(resolution)]
    vals2 = [rng2[0] + i*(rng2[1]-rng2[0])/(resolution-1) for i in range(resolution)]
    # header
    print(f"{'':>8}", end="")
    for v in vals1:
        print(f"{v:.2f} ", end="")
    print()
    for v2 in vals2:
        print(f"{v2:6.2f} |", end="")
        for v1 in vals1:
            test_dict = dict(fixed_vals)
            test_dict[ax1] = v1
            test_dict[ax2] = v2
            # compute emergent
            emergent = {}
            for coup, out_ax in playground.coupling_templates:
                emergent[out_ax] = coup.compute(test_dict)
            hit = all(abs(emergent.get(k,0.0)-target_output.get(k,0.0)) < 0.05
                      for k in target_output)
            # also quick constraint check
            coords = dict(test_dict)
            coords.update(emergent)
            for ax in playground.space.axes:
                if ax not in coords:
                    coords[ax] = 0.0
            uncertainty = {ax: 0.1 for ax in playground.space.axes}
            h = Hypothesis("scan", coords, uncertainty)
            passed = not any(c.kills(h)[0] for c in playground.constraints)
            if hit and passed:
                print("█ ", end="")
            elif passed:
                print("░ ", end="")
            else:
                print("· ", end="")
        print()

# ============================================================
# 10. DEMO v5 – Oscillation + Multi‑Target + Visualizer
# ============================================================
def demo_v5():
    # Space with oscillation axes
    axes = [
        "ice_mass_anomaly", "mantle_strain_memory", "rotational_coupling_efficiency",
        "emergent_mantle_anomaly",
        "core_osc_frequency", "core_osc_phase", "core_q_factor",
        "core_resonant_amplitude"
    ]
    space = Space(axes=axes)

    # Constraints
    constraints = [
        Constraint("rot_coupling_bound", {"rotational_coupling_efficiency":1.0}, 0.3, "<"),
        Constraint("ice_mass_limit", {"ice_mass_anomaly":1.0}, 0.6, "<"),
        Constraint("strain_limit", {"mantle_strain_memory":1.0}, 0.5, "<"),
        Constraint("q_factor_max", {"core_q_factor":1.0}, 0.8, "<"),  # realistic Q
        Constraint("amplitude_bound", {"core_resonant_amplitude":1.0}, 0.5, "<")  # emergent bound
    ]

    # Input axes for playground
    input_axes = [
        "ice_mass_anomaly", "mantle_strain_memory", "rotational_coupling_efficiency",
        "core_osc_frequency", "core_osc_phase", "core_q_factor"
    ]
    input_ranges = {
        "ice_mass_anomaly": (0.0, 0.6, 0.1),
        "mantle_strain_memory": (0.0, 0.5, 0.1),
        "rotational_coupling_efficiency": (0.0, 0.3, 0.05),
        "core_osc_frequency": (0.5, 1.5, 0.1),
        "core_osc_phase": (0.0, 1.0, 0.2),
        "core_q_factor": (0.0, 0.8, 0.1)
    }

    # Two coupling templates: one direct, one oscillatory
    direct_coupling = Coupling("direct_ice",
                               ["ice_mass_anomaly", "mantle_strain_memory", "rotational_coupling_efficiency"],
                               "emergent_mantle_anomaly", coeff=3.0, op="product")
    osc_coupling = OscillationCoupling("core_resonance",
                                       "core_osc_frequency", "core_osc_phase", "core_q_factor",
                                       "core_resonant_amplitude", base_amplitude=1.0)
    coupling_templates = [
        (direct_coupling, "emergent_mantle_anomaly"),
        (osc_coupling, "core_resonant_amplitude")
    ]

    # Multi‑target: hit both emergent values
    targets = {
        "emergent_mantle_anomaly": 0.18,
        "core_resonant_amplitude": 0.35
    }

    pg = MultiTargetPlayground(space, constraints, input_axes,
                               ["emergent_mantle_anomaly", "core_resonant_amplitude"],
                               input_ranges, coupling_templates)
    recipes = pg.explore(targets, tolerance=0.03)

    print("=== RFL v5 – OSCILLATION + MULTI‑TARGET + VISUALIZER ===")
    print(f"Targets: {targets}")
    print(f"Found {len(recipes)} recipes hitting both targets.\n")

    # Quick summary of top recipes
    for i, r in enumerate(recipes[:5]):
        print(f"Recipe {i+1}: inputs={r['inputs']}, emergent={r['emergent']}")

    # Visualize one recipe's playground region
    if recipes:
        visualize_playground(recipes)
        # Scan a 2D slice around the first recipe
        r0 = recipes[0]
        fixed = r0['inputs'].copy()
        del fixed["ice_mass_anomaly"]
        del fixed["mantle_strain_memory"]
        visualize_viable_region(pg, targets,
                                ["ice_mass_anomaly", "mantle_strain_memory"],
                                fixed, resolution=10)

    # Also run a simple tournament with oscillation hypotheses
    print("\n\n--- TOURNAMENT WITH OSCILLATION HYPOTHESES ---")
    # Build compound hypothesis from oscillation
    base1 = Hypothesis("core_state",
                       {"core_osc_frequency":0.95, "core_osc_phase":0.1, "core_q_factor":0.6},
                       {"core_osc_frequency":0.1, "core_osc_phase":0.1, "core_q_factor":0.1})
    base2 = Hypothesis("ice_state",
                       {"ice_mass_anomaly":0.5, "mantle_strain_memory":0.4, "rotational_coupling_efficiency":0.2},
                       {"ice_mass_anomaly":0.1, "mantle_strain_memory":0.1, "rotational_coupling_efficiency":0.05})
    cmpd = CompoundHypothesis("Oscillatory_Core+Ice",
                              [base1, base2],
                              [direct_coupling, osc_coupling],
                              "Core resonance amplifies ice-mass signal")
    # plain
    plain = Hypothesis("Plain_Ice_Only",
                       {"ice_mass_anomaly":0.5, "mantle_strain_memory":0.4, "rotational_coupling_efficiency":0.2,
                        "emergent_mantle_anomaly":0.12, "core_osc_frequency":0.0, "core_osc_phase":0.0,
                        "core_q_factor":0.0, "core_resonant_amplitude":0.0},
                       {"ice_mass_anomaly":0.1, "mantle_strain_memory":0.1, "rotational_coupling_efficiency":0.05,
                        "emergent_mantle_anomaly":0.02, "core_osc_frequency":0.0, "core_osc_phase":0.0,
                        "core_q_factor":0.0, "core_resonant_amplitude":0.0})

    tournament = Tournament(space, [plain, cmpd], constraints)
    result = tournament.run()
    print("ALIVE:", result["alive"])
    print("KILLED:", [k["name"] for k in result["killed"]])
    print("SCORE:", result["score"])
    visualize_clusters(result)

if __name__ == "__main__":
    demo_v5()
