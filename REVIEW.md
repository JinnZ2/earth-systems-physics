# Repository Review — earth-systems-physics

**Date:** 2026-07-08  
**Scope:** All files in `JinnZ2/earth-systems-physics`, with focus on modules added during the Layer 6 / kicked-relaxor / metrology build cycle.

---

## Summary Table

| Section | Finding Count | Severity Range |
|---------|--------------|----------------|
| 1. Inconsistencies | 9 | Medium–High |
| 2. Markdown Information Gaps | 7 | Low–High |
| 3. Code Audit | 6 | Low–High |
| 4. Organizational Structure | 5 | Low–Medium |
| 5. Limitations Mitigation Checklist | 5 | Medium |
| 6. Discoverability & Crawler Optimization | 5 | Low–Medium |

---

## Section 1 — Inconsistencies

### 1.1 `fixed_point` signature clash  
**Severity: High**

`boreal_recovery_ratchet.py:31`:
```python
def fixed_point(tau, K, r, T):
```

`kicked_relaxor_kernel.py:21`:
```python
def fixed_point(A, tau, r, T):
```

Same equation, different argument order and different second-parameter name (`K` vs `A`). A caller that switches between the two — or any future code that tries to unify them — will silently receive wrong results because positional arguments swap without error.

**Fix:** Standardize on the kernel's signature as the canonical form. In `boreal_recovery_ratchet.py` rename `K` → `A` and reorder so `A` is first:

```python
# boreal_recovery_ratchet.py:31  (was: def fixed_point(tau, K, r, T))
def fixed_point(A, tau, r, T):
    e = math.exp(-T / tau)
    return A * (1.0 - e) / (1.0 - r * e)
```

Update all three call sites in the same file (lines ~44, ~70, ~92) accordingly.

---

### 1.2 Iteration-count parameter has three names  
**Severity: Medium**

| File | Parameter name | Concept |
|------|---------------|---------|
| `boreal_recovery_ratchet.py:37` | `n_rot` | number of harvest rotations |
| `kicked_relaxor_kernel.py:54` | `n_kicks` | number of perturbation events |
| `fuel_load_ratchet.py:38` | `n_fires` | number of fire events |

All three count the same structural thing: how many times the kick fires. Domain-specific names are acceptable where they aid readability, but the kernel (`kicked_relaxor_kernel.py`) should use a generic name so it does not imply a domain. `n_kicks` is already the right choice there; the domain modules can alias it.

**Fix (kernel only):** No change needed — `n_kicks` is already neutral. Add a one-line docstring note that domain wrappers use `n_rot` / `n_fires` as aliases.

---

### 1.3 `MODES` dict mutated in-place under `__main__`, imported as live reference  
**Severity: High**

`boreal_recovery_ratchet.py:77–78`:
```python
for m in MODES.values():
    m["r"] = min(0.45, m["r"] + 0.30)   # keep legacy islands → L holds
report(T=70)
```

`boreal_carbon_ledger.py:9`:
```python
from boreal_recovery_ratchet import MODES, simulate
```

If any test or script imports `boreal_carbon_ledger` after running (or importing) `boreal_recovery_ratchet` as `__main__`, `MODES` already has mutated `r` values. The mutation is invisible to callers.

**Fix:** Deepcopy `MODES` before the leverage demonstration, or extract the mutated version as a separate dict:

```python
# boreal_recovery_ratchet.py — replace lines 76-81
if __name__ == "__main__":
    report(T=70)
    print("\n--- LEVERAGE: retention r high (variable-retention harvest) ---")
    import copy
    modes_leverage = copy.deepcopy(MODES)
    for m in modes_leverage.values():
        m["r"] = min(0.45, m["r"] + 0.30)
    report_modes(modes_leverage, T=70)   # factor out report() to accept a modes arg
```

---

### 1.4 `Alternative.name` used as a long description string  
**Severity: Medium**

`curiosity_engine.py:51`:
```python
class Alternative:
    name: str
    differs_by: str
    status: str
```

`amoc_case.py:50–59` (all four positional first args):
```python
Alternative("same spatial markers but under FAST (real, accelerating) forcing", ...),
Alternative("smooth monotonic approach to tipping (no oscillation)", ...),
Alternative("markers are response-to-weakening only, never cross to collapse", ...),
Alternative("the ~25yr lead transferred directly to the real world", ...),
```

The field is named `name` but contains a 60–80 character sentence. Any code that uses `.name` as a short label (table headers, logging, dictionaries keyed by name) will produce unreadable output.

**Fix:** Rename `name` → `description`, add a short `label` field, and update call sites:

```python
@dataclass
class Alternative:
    label: str          # short identifier, e.g. "fast-forcing"
    description: str    # full explanatory sentence
    differs_by: str
    status: str
```

Or, if label is overhead, keep `name` and document it as a sentence-length description. The key issue is naming the field `name` when it holds a sentence.

---

### 1.5 Two Layer-0 modules with diverging APIs  
**Severity: Medium**

`layer_0_electromagnetics.py` — the canonical coupling-state module used by the cascade engine (`cascade_engine.py:28`).

`layer_0_emag.py` — the "alternate API" FFT-based time-series module (`cascade_engine.py:1634`, imported lazily inside a function). Its own header says:

> "Standalone module — does NOT yet replace layer_0_electromagnetics.py for the cascade engine."

The two modules share a namespace prefix but serve different purposes and are never reconciled. Future contributors will be confused about which one is authoritative.

**Fix:** Add a `# STATUS: ALTERNATE API — see layer_0_electromagnetics.py for the primary coupling interface` banner to the top of `layer_0_emag.py`, and document the intended migration path in `CLAUDE.md` under the architecture section.

---

### 1.6 Two CLAIM_TABLE files  
**Severity: Low**

`CLAIM_TABLE.json` — referenced by `CLAIM_SCHEMA.py:90–112` as the canonical machine-readable claim index.

`CLAIM_TABLE.earth.json` — generated by `claim_ledger.py:301` (`dump_ledger(path="CLAIM_TABLE.earth.json")`).

These are not the same schema. The `.earth.json` variant is a ledger dump; the plain `.json` is the vocabulary index. The different names are not explained anywhere.

**Fix:** Add comments to `CLAIM_SCHEMA.py` and `claim_ledger.py` distinguishing the two files' roles and generation paths. If `CLAIM_TABLE.json` is hand-authored, say so. If it too should be generated, wire it up.

---

### 1.7 Two `constraint_RFL_geometry` files at different versions  
**Severity: Medium**

`constraint_RFL_geometry.py` — header: `v5`; used by `earth_physics_constraints.py:24` and `stommel_amoc.py:15`.

`constraint_RFL_geometry_v32.py` — header: `v3.2`; not imported by anything in the repo.

A `v3.2` file co-existing with a `v5` file suggests the numbering tracks different lineages that were never merged. The orphan file will confuse contributors.

**Fix:** Either delete `constraint_RFL_geometry_v32.py` if it is superseded, or document what it provides that `v5` does not and give it a stable unique name that conveys its purpose (e.g., `constraint_RFL_geometry_cascade_coupler.py`).

---

### 1.8 `To- add.md` — space in filename  
**Severity: Low**

`To- add.md` contains a space and a hyphen. Shell expansion, git tab-completion, and automated tooling all require quoting this name. It is not referenced from any other file.

**Fix:**
```bash
git mv "To- add.md" TODO.md
```

---

### 1.9 `layer_0_emag` referenced in comments but imported lazily without guard  
**Severity: Low**

`cascade_engine.py:1634`:
```python
from layer_0_emag import (
    DynamoResponseConfig, compute_l0_response, L0Output
)
```

This import lives inside `run_cascade_history()`, so it does not fail at module load. However, the comment at line 1552 and the type annotation `l0_spectral: Any` at line 1569 both reference `layer_0_emag` as if it is always present. If `layer_0_emag.py` is ever moved or renamed, the type hint `Any` will silently remain (no error at annotation time).

**Fix:** Change the annotation from `Any` to `"L0Output"` (string forward reference) or add `TYPE_CHECKING` guards so the annotation is checked by static analysis tools.

---

## Section 2 — Markdown Information Gaps

### 2.1 README.md is severely outdated  
**Severity: High**

`README.md` is 147 lines. Its file tree (lines 103–120) lists only the original 8 layer files, `cascade_engine.py`, and `assumption_validator/`. It does not mention:

- Any of the ~80 systems-analysis modules documented in `CLAUDE.md`
- The `boundary_waters/`, `oil_phase_shift/`, `calibration/`, `tools/`, `ai_reference/`, `experiments/` subdirectories
- Any of the 16 modules added in the Layer 6 / kicked-relaxor / metrology build cycle

A first-time visitor reading README.md sees a project roughly 1/6 its actual scope.

**Fix:** The README does not need to duplicate CLAUDE.md's full module table. It should at minimum:
1. Replace the outdated file tree with a pointer to CLAUDE.md for full structure.
2. Add a one-paragraph "Extended modules" section listing the major subsystems (systems-analysis guards, oil_phase_shift, boundary_waters, calibration, ai_reference).
3. Link `kicked_relaxor_synthesis.md` as the entry point for the Layer 6 ecosystem work.

---

### 2.2 `kicked_relaxor_synthesis.md` not linked from README  
**Severity: Medium**

`kicked_relaxor_synthesis.md` is the richest cross-domain synthesis in the repository — it derives the shared kernel, the critical period, and the empirical anchors for both boreal extraction and Indigenous fire management. It is not mentioned in `README.md` or `CLAUDE.md`.

**Fix:** Add to `README.md`:
```markdown
## Cross-Domain Synthesis

[`kicked_relaxor_synthesis.md`](kicked_relaxor_synthesis.md) — One kicked-relaxor kernel
with two sign conventions: boreal extraction collapse and fire-exclusion megafire are the
same stroboscopic map. Includes T_crit derivation and empirical anchors.
```

And add `kicked_relaxor_synthesis.md` to the file structure table in `CLAUDE.md`.

---

### 2.3 `DIFFERENTIAL_FRAME.md` not referenced anywhere  
**Severity: Low**

`DIFFERENTIAL_FRAME.md` exists in the repo root but is not mentioned in README.md, CLAUDE.md, or any Python module.

**Fix:** Either link it from the appropriate section of CLAUDE.md (likely the epistemology / constraint-accountability section), or if it is a draft, add a `# STATUS: DRAFT` header to flag it.

---

### 2.4 Layer 6 ecosystem modules absent from CLAUDE.md file structure  
**Severity: Medium**

The `CLAUDE.md` file structure section and systems-analysis table do not list any of the following files added in this build cycle:

- `cascade_transfer.py` / `cascade_transfer_demo.py`
- `scope_carrier_density.py`
- `frozen_flow_audit.py`
- `curiosity_engine.py` / `amoc_case.py`
- `universe_constraint.py`
- `continuity_audit.py`
- `boreal_recovery_ratchet.py` / `boreal_carbon_ledger.py`
- `fuel_load_ratchet.py`
- `permafrost_abrupt_ledger.py`
- `amoc_hysteresis_gate.py`
- `measurement_corruption_taf.py`
- `kicked_relaxor_kernel.py`
- `stressor_nonadditivity.py`

**Fix:** Add these to the systems-analysis modules table in CLAUDE.md. Suggested grouping: a new "Ratchet dynamics & ecosystem accounting" sub-table covering the kicked-relaxor family, and a "Metrology" row for `measurement_corruption_taf.py`.

---

### 2.5 `kicked_relaxor_synthesis.md` Section 7 Provenance table missing `stressor_nonadditivity.py`  
**Severity: Low**

`kicked_relaxor_synthesis.md:147–154` lists the provenance graph for the kernel family. `stressor_nonadditivity.py` is the multi-stressor synergy audit (another "omitted-pool" signature, same audit discipline) but is not in the table.

**Fix:** Add one line to the provenance table:
```
stressor_nonadditivity.py       adjacent (interaction-term omitted pool, synergistic amplification)
```

---

### 2.6 `ASSESS.md` not cross-referenced from README or CLAUDE.md  
**Severity: Low**

`ASSESS.md` (assessment protocol for AI systems) is listed in CLAUDE.md's file structure but not in README.md. New contributors who read only the README will not know it exists.

**Fix:** Add a one-line reference to `ASSESS.md` in the README under a "For AI systems" or "Assessment" heading.

---

### 2.7 `To- add.md` has no header explaining its purpose  
**Severity: Low**

The file name implies a to-do list, but it is not readable from any other file and its content is unknown without opening it. After renaming (see 1.8), it should be referenced from the README or converted to GitHub Issues.

---

## Section 3 — Code Audit

### 3.1 Zero test coverage for ~16 new modules  
**Severity: High**

`test_smoke.py` has 308 tests. A search for the names of all modules added in this build cycle returns zero matches:

```
cascade_transfer, scope_carrier_density, frozen_flow_audit,
curiosity_engine, amoc_case, universe_constraint, continuity_audit,
boreal_recovery_ratchet, boreal_carbon_ledger, fuel_load_ratchet,
permafrost_abrupt_ledger, amoc_hysteresis_gate, measurement_corruption_taf,
kicked_relaxor_kernel, stressor_nonadditivity
```

None of these are exercised by the test suite. CI will pass on pushes that break any of them.

**Fix:** Add a `TestLayer6EcosystemModules` class to `test_smoke.py` with at minimum one smoke test per module. Minimal pattern (import + run `__main__` logic via function call):

```python
class TestKickedRelaxorKernel(unittest.TestCase):
    def test_fixed_point_reach_pole(self):
        from kicked_relaxor_kernel import fixed_point
        xstar = fixed_point(A=1.0, tau=120, r=0.10, T=70)
        self.assertAlmostEqual(xstar, 0.47, places=1)

    def test_critical_period_returns_float(self):
        from kicked_relaxor_kernel import critical_period
        Tc = critical_period(A=1.0, tau=25, r=0.10, theta=0.70, orientation="avoid")
        self.assertIsInstance(Tc, float)
        self.assertGreater(Tc, 0)

    def test_simulate_ratcheted_returns_list(self):
        from kicked_relaxor_kernel import simulate_ratcheted
        traj = simulate_ratcheted(A=1.0, tau0=120, r=0.10, T=70, n_kicks=5)
        self.assertEqual(len(traj), 5)
```

---

### 3.2 `kicked_relaxor_kernel.py:99` — silent None when `T_crit` is undefined  
**Severity: Medium**

```python
Tc_str = f"T_crit={Tc:.0f}y" if Tc else ""
print(f"{name:<34}{xs_fix/A:>10.2f}{xs_rat:>14.2f}{orient:>9}  {v}  [{Tc_str}]")
```

When `critical_period()` returns `None` (because `e_star` is out of (0,1)), the bracket prints as `[]` with no explanation. The math has broken — the system has no finite critical period — but the printout is identical in format to a successful row, just with an empty annotation.

**Fix:**
```python
Tc_str = f"T_crit={Tc:.0f}y" if Tc is not None else "T_crit=NONE(e* out of range)"
```

---

### 3.3 `cascade_engine.py:22–23` — hard module-level imports without fallback  
**Severity: Medium**

```python
from soil_interface            import coupling_state as soil_iface_state
from stabilizing_capacity      import (
```

These imports execute at module load. If `soil_interface.py` or `stabilizing_capacity.py` raise an error, the entire cascade engine becomes unimportable — including for tests that do not use those modules. The layer files themselves (`layer_0_electromagnetics.py`, etc.) are imported the same way and have the same exposure.

**Fix (minimal):** Wrap these two in try/except with a clear warning:

```python
try:
    from soil_interface import coupling_state as soil_iface_state
except ImportError:
    soil_iface_state = None  # optional module; soil nutrient coupling disabled
```

This is especially important because `soil_interface` and `stabilizing_capacity` are not listed in the CI-tested module set.

---

### 3.4 `boreal_recovery_ratchet.py` — `MODES` imported as a live mutable reference  
**Severity: High** (duplicate of 1.3, code-audit perspective)

`boreal_carbon_ledger.py:9` imports `MODES` directly:
```python
from boreal_recovery_ratchet import MODES, simulate
```

If `boreal_recovery_ratchet` is ever run as `__main__` before this import (e.g., in an interactive session, or by a test that imports the module while another test runs the script), the `r` values in `MODES` will have been permanently mutated for the process lifetime. The carbon ledger will then compute incorrect results without any error.

**Fix:** Same as 1.3 — deepcopy before mutation. Additionally, `boreal_carbon_ledger.py` should import a `get_modes()` factory function rather than the bare dict:

```python
# boreal_recovery_ratchet.py — add
import copy
def get_modes():
    """Return a fresh copy of MODES (safe for concurrent/sequential use)."""
    return copy.deepcopy(MODES)
```

---

### 3.5 `measurement_corruption_taf.py` — `sweep()` hardcodes `sigma0/(1-m)` in print but uses `detect()` for logic  
**Severity: Low**

`measurement_corruption_taf.py:42`:
```python
print(f"{m:>5.2f}{sigma0/(1-m):>8.2f}{z:>7.2f}{zc:>8.2f}  {v}")
```

The sigma printed here recalculates `sigma0/(1-m)` directly, bypassing the `max(1e-3, ...)` guard inside `detect()` (line 26). For m=1.0 this would produce a ZeroDivisionError in the print statement even though `detect()` itself is guarded.

The existing sweep only tests up to m=0.60 so this never fires. But if a caller adds m=1.0 to the list, the logic succeeds and the print crashes.

**Fix:** Capture sigma from inside `detect()` instead of recomputing:

```python
def detect(true_trend, horizon, sigma0, m, f):
    sigma = sigma0 / max(1e-3, (1.0 - m))
    z = (true_trend * horizon) / sigma
    z_crit = 1.96 * (1.0 + f)
    return z, z_crit, z > z_crit, sigma   # add sigma to return

# sweep() — line 38
z, zc, ok, sigma = detect(true_trend, horizon, sigma0, m, f)
# line 42 — replace sigma0/(1-m) with sigma
print(f"{m:>5.2f}{sigma:>8.2f}{z:>7.2f}{zc:>8.2f}  {v}")
```

---

### 3.6 `amoc_hysteresis_gate.py` — `LOCKED` verdict path never reached in the demo  
**Severity: Low**

`amoc_hysteresis_gate.py` defines a `LOCKED` verdict when `min(co2_path) >= C_RECOVER` after collapse. The demo in `__main__` runs a CO2 path that peaks at 550 ppm and returns to 400 ppm — above the 350 ppm recovery threshold — so `LOCKED` fires. But there is no demonstration of the case where CO2 dips below 350 ppm. The `LOCKED` branch logic is exercised, but the "gate opens" case is not shown, making it impossible to verify the full hysteresis loop from the demo output alone.

**Fix:** Add a third scenario to the demo where CO2 drops below 350:

```python
run_scenario("recovery-possible (CO2 dips to 320 ppm)",
             list(range(280, 490, 5)) + list(range(490, 315, -5)))
```

---

## Section 4 — Organizational Structure Suggestions

### 4.1 Root directory has 113 Python files with no domain grouping  
**Severity: Medium**

The repo root currently holds 113 `.py` files. The three natural clusters that have emerged but not been formalized:

1. **Ratchet dynamics / ecosystem accounting**: `kicked_relaxor_kernel.py`, `boreal_recovery_ratchet.py`, `boreal_carbon_ledger.py`, `fuel_load_ratchet.py`, `permafrost_abrupt_ledger.py`, `amoc_hysteresis_gate.py`, `stressor_nonadditivity.py`, `measurement_corruption_taf.py`

2. **Inference / epistemic guards**: `cascade_transfer.py`, `cascade_transfer_demo.py`, `scope_carrier_density.py`, `frozen_flow_audit.py`, `curiosity_engine.py`, `amoc_case.py`, `universe_constraint.py`, `continuity_audit.py`

3. **Device / instrumentation**: `magnonic_sublayer.py`, `magnon_polaron_hybridization.py`, `confined_magnon_polaron.py`, `multi_channel_coupling.py`, `earth_magnomechanical.py`, `cavity_optomagnonics.py`, `banded_crystal_computer.py`, `cold_climate_crystal.py`, `crystal_device_gradient.py`, `skyrmion_rkky.py`, `skyrmion_phonon_coupling.py`

Moving these into `ratchet_dynamics/`, `inference_guards/`, and `instrumentation/` would reduce root-level clutter without breaking the existing subdirectory pattern. The physics layers (layer_0 through layer_7) should remain in root as they are the canonical stack.

**Suggested migration:** This is a significant rename operation. Before acting, update `cascade_engine.py` imports and `test_smoke.py` accordingly.

---

### 4.2 `constraint_RFL_geometry_v32.py` is an orphan  
**Severity: Medium**

Nothing imports `constraint_RFL_geometry_v32.py`. It co-exists with `constraint_RFL_geometry.py` at an earlier version number (v3.2 vs v5), creating confusion about which is current.

**Action:** Run `grep -r "constraint_RFL_geometry_v32" .` — if nothing imports it, delete it and add a note to the git commit explaining that v5 supersedes it. If it provides unique features not in v5, extract those features into v5 and then delete the file.

---

### 4.3 Version numbers embedded in filenames are an antipattern  
**Severity: Low**

`constraint_RFL_geometry_v32.py` uses a version number as part of the filename. This is a code-review smell: version history belongs in git, not filenames. When v33 exists, v32 becomes permanent clutter.

**Action:** Establish a convention: no version suffixes in filenames. Track version in the module docstring and git log.

---

### 4.4 `kicked_relaxor_synthesis.md` should live in a `docs/` folder  
**Severity: Low**

The repo root currently holds `REVIEW.md`, `ASSESS.md`, `DIFFERENTIAL_FRAME.md`, `kicked_relaxor_synthesis.md`, `To- add.md`, `CLAUDE.md`, and `README.md` — seven Markdown files. As cross-domain synthesis documents accumulate, the root becomes noisy.

**Suggested structure:**
```
docs/
  kicked_relaxor_synthesis.md
  DIFFERENTIAL_FRAME.md
  ASSESS.md
```

Keep `README.md`, `CLAUDE.md`, `LICENSE` in root (tooling expects them there). Move the rest.

---

### 4.5 `experiments/` folder contains only two files  
**Severity: Low**

`experiments/magnetometer_build.py` and `experiments/Possibilities.md` are the only files in `experiments/`. The folder is valid but could absorb the `cascade_transfer_demo.py` and `scope_carrier_density.py` demo scripts if the convention is "standalone runnable explorations."

**Action:** Either expand the `experiments/` convention to cover demo scripts, or rename it `demos/` to make the scope clearer.

---

## Section 5 — Limitations Mitigation Checklist

### 5.1 `REFUTATION_PROTOCOL` is named but not defined  
**Severity: Medium**

`kicked_relaxor_synthesis.md:139`:
> "If data refutes, update the claim — never the simulation (REFUTATION_PROTOCOL)."

`REFUTATION_PROTOCOL` is a named protocol referenced as if it is a defined procedure, but there is no file, function, or section in the repo that defines what it specifies. A reader who wants to follow the protocol cannot.

**Fix:** Either:
- Define `REFUTATION_PROTOCOL` as a section in `kicked_relaxor_synthesis.md` (preferred — keep the definition next to the claim), or
- Create `docs/REFUTATION_PROTOCOL.md` with the explicit protocol steps and link it from the synthesis document.

At minimum, the protocol should specify: what counts as refuting data, who updates which file, how the falsification verdict is recorded.

---

### 5.2 Inline GAP flags are not machine-trackable  
**Severity: Medium**

`stressor_nonadditivity.py:56–57`:
```python
print("GAP (honest, per Bahn): not yet generalizable across climate zones /")
print("ecosystem types — needs matched multifactor experiments elsewhere.")
```

This GAP declaration is printed to stdout but is not captured in any structured form — not in `assumption_validator/registry.py`, not in `CLAIM_TABLE.json`, not in any `ai_reference/` catalog. It cannot be queried, tracked, or surfaced by the REST API.

**Fix:** Register the gap as an assumption boundary in `assumption_validator/registry.py`:
```python
{
    "id": "stressor_nonadditivity_generalizability",
    "description": "Synergistic amplification factor (gamma=3.0) calibrated on grassland C-uptake; not yet validated across climate zones or ecosystem types",
    "risk_level": "medium",
    "layer": 6,
    "source": "stressor_nonadditivity.py",
}
```

---

### 5.3 Confidence cap of 0.94 in `universe_constraint.py` is an ungrounded heuristic  
**Severity: Low**

`universe_constraint.py:144`:
```python
return min(requested, 0.94)
```

The comment says `# 0.94: room always kept` but does not derive the value. Why 0.94 and not 0.95 or 0.90? As written, it is an arbitrary ceiling that the module cannot justify from its own physics.

**Fix:** Add a comment explaining the derivation or reasoning:
```python
# 0.94: empirical floor for irreducible model-reality gap at current observational
# density; chosen to leave >1 sigma room while remaining above the heuristic
# ceiling for empirical science claims (~0.95 convention).
```

If no derivation exists, rename the magic number to a named constant with a TODO:
```python
MAX_EMPIRICAL_CONFIDENCE = 0.94  # TODO: derive from Lloyd bound + observational coverage
```

---

### 5.4 Carbon budget numbers in `permafrost_abrupt_ledger.py` will age  
**Severity: Medium**

`permafrost_abrupt_ledger.py:19`:
```python
BUDGET_REDUCT = {"1.5C": (0.13, 0.37), "2.0C": (0.10, 0.24)}
```

These ranges are seeded from Schadel et al. 2026. Carbon budgets are updated annually (IPCC AR7 is in progress). The module has no mechanism to flag that its seed values may be stale.

**Fix:** Add a `SEEDED_DATE` constant and a runtime check:

```python
SEEDED_DATE = "2026"       # Schadel et al., Comms Earth Environ 2026
SEEDED_BUDGET_YEAR = 2026  # year the booked budgets were current

# In report() or at module load:
import datetime
current_year = datetime.date.today().year
if current_year > SEEDED_BUDGET_YEAR + 2:
    import warnings
    warnings.warn(
        f"permafrost_abrupt_ledger: seed values from {SEEDED_BUDGET_YEAR}; "
        "carbon budgets should be updated from current IPCC/GCP figures.",
        UserWarning
    )
```

---

### 5.5 `boreal_recovery_ratchet.py` fixed-point and simulate return different things  
**Severity: Low**

`fixed_point()` returns a scalar (the stroboscopic fixed point). `simulate()` returns a list of tuples `(frac, L, tau_eff)`. A caller that wants "what is the steady-state recovery under ratcheted conditions?" must know to use `simulate()[-1][0]` rather than `fixed_point()`. This is not documented.

**Fix:** Add a helper:
```python
def steady_state(mode, T, n_rot=8):
    """Return the final ratcheted recovery fraction for mode dict at period T."""
    return simulate(mode, T, n_rot)[-1][0]
```

And document in `fixed_point()`'s docstring that it gives the constant-tau fixed point, while `simulate()` gives the ratcheted trajectory.

---

## Section 6 — Discoverability & Crawler Optimization

### 6.1 No `CITATION.cff` file  
**Severity: Medium**

GitHub renders a "Cite this repository" button only when a `CITATION.cff` file is present. Without it, researchers who want to cite the repo have no machine-readable citation to use, and DOI minting (via Zenodo) requires manual setup.

**Fix:** Create `CITATION.cff`:
```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
title: "earth-systems-physics"
authors:
  - family-names: "JinnZ2"
license: CC0-1.0
repository-code: "https://github.com/JinnZ2/earth-systems-physics"
abstract: >
  A coupled differential equation framework mapping Earth physics as
  constraint layers from orbital forcing through biosphere. Pure Python.
  Not a climate model. A physics inventory and constraint stack.
keywords:
  - earth-systems
  - cascade-dynamics
  - constraint-layers
  - kicked-relaxor
  - carbon-accounting
  - biosphere
  - magnomechanical
  - ecosystem-physics
```

---

### 6.2 Repository has no topic tags  
**Severity: Low**

GitHub topic tags (set in the repo Settings → Topics) make the repository discoverable via topic search. Currently there are none. Suggested tags:

`earth-systems`, `physics`, `differential-equations`, `carbon-accounting`, `biosphere`, `cascade-dynamics`, `constraint-physics`, `cc0`, `python`, `climate-physics`

**Fix:** Add via GitHub Settings → Topics (cannot be done via git; requires a UI action or the GitHub API).

---

### 6.3 README's "File Structure" section is stale and misleads crawlers  
**Severity: High**

Web crawlers (GitHub search, Sourcegraph, academic indexers) parse README.md as the primary entry point. The current README file tree shows 11 files; the actual repo has 113+ Python files across 6+ subdirectories. This gap means:

- Search results for "boreal recovery ratchet python" or "AMOC hysteresis CO2" will not surface this repo even though it contains matching code.
- AI systems reading the README to understand the repo scope will dramatically underestimate what is here.

**Fix:** Replace the static file tree with a summary block pointing to CLAUDE.md:

```markdown
## File Structure

The full module inventory (113+ files across physics layers, systems-analysis
guards, ratchet dynamics, metrology, and sub-projects) is documented in
[`CLAUDE.md`](CLAUDE.md).

Core files:
- `cascade_engine.py` — coupling propagation across all layers
- `kicked_relaxor_kernel.py` — shared kernel for extraction and fire-exclusion dynamics
- `test_smoke.py` — 308 tests (CI: Python 3.10–3.12)
- `assumption_validator/` — REST API + 36 assumption boundaries
```

---

### 6.4 Key synthesis documents are not linked from README  
**Severity: Medium**

The following documents represent the repo's most original contributions, but none is linked from `README.md`:

| Document | Content |
|----------|---------|
| `kicked_relaxor_synthesis.md` | Cross-domain kernel unification |
| `DIFFERENTIAL_FRAME.md` | (contents unknown without reading) |
| `ASSESS.md` | Assessment protocol for AI systems |
| `ai_reference/README.md` | Machine-readable catalog entry point |

A crawler or researcher who reads only `README.md` will not find these.

**Fix:** Add a "Key documents" section to README.md with one-line descriptions and links.

---

### 6.5 `ai_reference/` catalog is not referenced from the top-level README  
**Severity: Low**

`ai_reference/` contains 33 `.jsonl` catalogs (242 records) specifically designed for downstream AI tool ingestion. Its own `README.md` explains the format. But the top-level `README.md` does not mention it at all.

AI systems that index the repo will not know the catalogs exist unless they traverse the full directory tree. The catalog's value is zero if no AI tool finds it.

**Fix:** Add to README.md:
```markdown
## Machine-Readable Exports

[`ai_reference/`](ai_reference/) contains 33 JSONL catalogs (242 records) 
auto-exported from source modules — mechanisms, assumption boundaries, cascade 
scenarios, feedback loops, and more. See [`ai_reference/README.md`](ai_reference/README.md)
for ingestion instructions.
```

---

*REVIEW.md generated 2026-07-08. All file paths are repo-relative. Line numbers reference the state of the branch at time of review.*
