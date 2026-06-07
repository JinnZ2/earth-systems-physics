# atmospheric_instability

CC0. stdlib-only Python. No dependencies. No network. Runs on a phone.

A substrate-primary explorer for pattern-forming instabilities in the
atmosphere and the cascades between them. Same idea as washboard roads — a
forcing meets a resonant mode meets a dissipation, and a pattern grows — but
applied to the dynamical instability zoo, and asking what happens as the
background state deforms under warming.

## The geometry

```
background state ──┐
 (gradient, shear, │   forcing  ──┐
  stratification)  │              ├── growth_rate = (forcing − dissipation)
 warming_index ────┘   damping ───┘            per instability kernel
        │
        v
 7 instability kernels evaluated ──> active set (growth_rate > 0)
        │
        v
 coupling graph: a broken mode mixes / deposits momentum / releases heat
        │         ──> pushes OTHER modes toward (or away from) threshold
        v
 cascade chain  +  Monte Carlo ensemble (does it grow under real noise?)
```

## The kernels (instabilities.py)

```
kelvin_helmholtz   shear at a density interface   Ri = N²/S² < 0.25
baroclinic_eady    mid-latitude cyclogenesis      σ = 0.31·f·|dU/dz|/N
inertial           absolute-vorticity sign flip   f·(f−dU/dy) < 0
symmetric          slantwise convection           PV·f < 0
gravity_wave       saturation / overturning       amplitude > intrinsic speed
convective         static instability             N² < 0
rossby_barotropic  jet-curvature PV gradient       β − d²U/dy² changes sign
```

## The climate knob (climate_state.py)

`warming_index` w ∈ [0,1] deforms the background:

- lower-troposphere meridional gradient WEAKENS (Arctic amplification)
- upper-tropospheric tropical gradient STRENGTHENS
- stratification rises slightly aloft; jet curvature sharpens

Same physics, shifted background, different dominant modes. **The headline
result the model reproduces from first principles**: lower-level baroclinic
growth falls with warming while upper-level rises — the observed jet/storm-track
"tug of war" (CLAIM A1).

## Files

```
thermo.py          Brunt-Väisälä, thermal wind, Richardson, Coriolis, β
instabilities.py   the 7 growth-rate kernels
climate_state.py   background state + warming deformation
coupling.py        directed mode-interaction graph + cascade tracer
explorer.py        evaluate / sweep / find zero-crossings / 2D surface
ensemble.py        Monte Carlo perturbation: activation probability + growth
cascade_run.py     entry point
CLAIM_TABLE.atmos.json   6 falsifiable claims (A2, A6 verified in-repo)
```

## Run

```
python3 cascade_run.py                       # sweep + cascade at 45N, lower
python3 cascade_run.py --lat 60 --level upper
python3 cascade_run.py --cascade --w 0.7     # trace the cascade chain
python3 cascade_run.py --surface             # ASCII growth surface (lat × warming)
python3 cascade_run.py --ensemble --w 0.7    # Monte Carlo: P(active), 24h amplify
python3 cascade_run.py --json                # machine-readable sweep + crossings
```

## Where to push it (open build targets)

```
- horizontal wavenumber spectrum  : replace single-mode kernels with k-resolved
                                     growth (most-unstable wavelength per mode)
- moist baroclinic                 : latent heating -> higher Eady growth
- explicit vertical structure      : multi-layer, real mode shapes
- coupling calibration             : turn the hypothesis edges (coupling.py) into
                                     data-fit couplings from reanalysis composites
- time integration                 : nonlinear amplitude eqs, finite-amplitude
                                     equilibration (the washboard analogy made literal)
```

## Methodology

If reanalysis or radiosonde data refutes a CLAIM, **update the claim — do not
retune the model to fit.** The coupling graph is the most model-dependent layer
and every edge is individually falsifiable.
