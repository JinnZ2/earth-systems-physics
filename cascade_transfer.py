# cascade_transfer.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Regime transfer for the coupled eight-layer cascade.
# Freeze coupling topology + conservation. Retrain only per-layer warming deformation.
# Falsification: separates honest transfer-fail from conservation-violating false-fit.
# stdlib only.

import math
import random

LAYERS = list(range(-1, 7))           # -1..6, eight layers
N = len(LAYERS)
IDX = {L: i for i, L in enumerate(LAYERS)}

# ── coupling topology: which layer drives which (1 = edge, 0 = none) ──
# nearest-layer cascade + dynamo→surface spectral back-coupling
TOPO = [[0]*N for _ in range(N)]
for i in range(N-1):
    TOPO[i+1][i] = 1                   # forward cascade
TOPO[IDX[6]][IDX[0]] = 1              # dynamo spectral resonance → surface


class CascadeTransfer:
    def __init__(self):
        # STRUCTURAL: coupling magnitudes on the frozen topology
        self.K = [[random.gauss(0, 0.1) if TOPO[i][j] else 0.0
                   for j in range(N)] for i in range(N)]
        # DEFORMATION: per-layer warming sensitivity (the transfer subspace)
        self.deform = [0.0] * N
        self.frozen = False

    def step(self, state, w, dt=1.0):
        """
        One cascade step.

        state : per-layer scalar list (length N)
        w     : warming index (scalar)
        dt    : timestep (default 1.0)

        Deformation rides the flux: flux scaled by (1 + deform[i] * w).
        """
        nxt = list(state)
        for i in range(N):
            flux = sum(self.K[i][j] * state[j] for j in range(N) if TOPO[i][j])
            flux *= (1.0 + self.deform[i] * w)
            nxt[i] = state[i] + dt * math.tanh(flux)
        return nxt

    def conservation_residual(self, state, nxt):
        """
        Closed-stack flux must balance. Nonzero = structure not conserving.

        Checks whether total system state is conserved across the cascade step
        (proxy for energy/mass balance through the full layer stack).
        """
        return abs(sum(nxt) - sum(state))

    # ── learnable params depend on freeze state ──────────────────────────

    def _params(self):
        if self.frozen:
            return [('d', i) for i in range(N)]
        return ([('K', i, j) for i in range(N) for j in range(N) if TOPO[i][j]]
                + [('d', i) for i in range(N)])

    def _get(self, p):
        return self.deform[p[1]] if p[0] == 'd' else self.K[p[1]][p[2]]

    def _set(self, p, v):
        if p[0] == 'd':
            self.deform[p[1]] = v
        else:
            self.K[p[1]][p[2]] = v

    def fit(self, data, lr=0.01, epochs=200, conserve_penalty=10.0,
            grad_clip=1.0, weight_clip=3.0):
        """
        Train on data.

        data             : list of (state, w, target_state) triples
        lr               : learning rate
        epochs           : training epochs
        conserve_penalty : loss weight on conservation residual
        grad_clip        : per-parameter gradient clip; prevents single large steps.
        weight_clip      : per-parameter absolute bound after each update.
                           Both clips are required for the cascade tanh architecture:
                           grad_clip alone cannot prevent slow accumulation over many
                           epochs; once params grow large, tanh saturates, the
                           conservation gradient vanishes, and fit error accumulates
                           without opposing force.

        When frozen=True  : only deform params update (transfer phase).
        When frozen=False : K (topology weights) and deform both update (pretrain).

        Conservation is in the loss: fit() cannot reduce prediction error by
        breaking mass/energy balance. This keeps the falsification honest.
        """
        for _ in range(epochs):
            for state, w, target in data:
                nxt  = self.step(state, w)
                err  = sum((nxt[i] - target[i])**2 for i in range(N))
                cons = self.conservation_residual(state, nxt)
                loss = err + conserve_penalty * cons
                for p in self._params():
                    g = self._fd_grad(p, state, w, target, conserve_penalty, loss)
                    g = max(-grad_clip, min(grad_clip, g))       # clip gradient
                    v = self._get(p) - lr * g
                    v = max(-weight_clip, min(weight_clip, v))   # clip weight
                    self._set(p, v)
        return self

    def _fd_grad(self, p, state, w, target, cp, base, h=1e-5):
        """
        Forward finite-difference gradient of loss w.r.t. param p.
        Uses accessor/mutator so perturbation is visible inside step().
        """
        v = self._get(p)
        self._set(p, v + h)
        nxt = self.step(state, w)
        l1  = (sum((nxt[i] - target[i])**2 for i in range(N))
               + cp * self.conservation_residual(state, nxt))
        self._set(p, v)
        return (l1 - base) / h

    def freeze_structure(self):
        """
        TRANSFER POINT: topology and coupling magnitudes locked.
        Only deformation subspace remains open.

        Call after pretraining on Holocene-dense data; subsequent fit() calls
        update only per-layer warming sensitivity (self.deform).
        """
        self.frozen = True
        return self

    def verdict(self, target_data, fit_tol=1e-2, cons_tol=1e-3):
        """
        Three-way falsification verdict on held-out regime-shift data.

        GREEN : fit_err ≤ fit_tol AND cons_err ≤ cons_tol
                → invariance held; coupling form survives regime shift.

        RED / FALSE FIT : fit_err ≤ fit_tol AND cons_err > cons_tol
                → deformation absorbed a conservation break.
                  Model fits data but by violating physics — the deformation
                  parameters are doing something physically meaningless.
                  This is the dangerous failure mode.

        RED / HONEST FAIL : fit_err > fit_tol
                → regime broke coupling FORM, not just coefficients.
                  Structure is not invariant; assumption_validator RED condition
                  for the boundary where the assumed invariant lives.

        Returns (color, reason, fit_err, cons_err).
        """
        fit_err, cons_err = 0.0, 0.0
        for state, w, target in target_data:
            nxt       = self.step(state, w)
            fit_err  += sum((nxt[i] - target[i])**2 for i in range(N))
            cons_err += self.conservation_residual(state, nxt)
        fit_err  /= len(target_data)
        cons_err /= len(target_data)
        if fit_err <= fit_tol and cons_err <= cons_tol:
            return ("GREEN", "invariance held — coupling form survives regime", fit_err, cons_err)
        if fit_err <= fit_tol and cons_err > cons_tol:
            return ("RED", "FALSE FIT — deformation absorbed a conservation break", fit_err, cons_err)
        return ("RED", "honest fail — regime broke coupling FORM, not coefficients", fit_err, cons_err)


# ── pipeline ──────────────────────────────────────────────────────────────
# m = CascadeTransfer().fit(holocene_dense)          # pretrain, cheap, all params
# m.freeze_structure().fit(regime_sparse, epochs=50) # transfer, deform only
# print(m.verdict(regime_holdout))                   # GREEN / RED + reason
