# cascade_transfer.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Regime transfer for the coupled eight-layer cascade.
# Freeze coupling topology + coupling magnitudes. Retrain deform + leak.
#
# Three structural changes from the first version:
#
#   1. step() → conserving exchange (nxt[i] += t, nxt[j] -= t per edge).
#      Conservation is structural, not penalty-hoped-for. The exchange
#      terms cancel in the sum by construction.
#
#   2. leak[] channel added. This is the load-bearing change.
#      leak[i] * w is an explicit imbalance DOF the optimizer can reach
#      for during transfer. Without this lever the model can't false-fit,
#      and FALSE-FIT collapses into HONEST-FAIL — you lose the ability to
#      distinguish "matched data by breaking physics" from "couldn't match
#      data." The lever is what makes the lie measurable.
#
#   3. verdict() reads cons = |Σ leak|, not raw flux residual.
#      Directly: did the optimizer reach for the cheat?
#
# Note on the training-time penalty: conserve_penalty does NOT prevent
# cheating. The optimizer will drive |Σ leak| as high as needed when fit
# gain exceeds penalty cost. The training-time regularizer is not the
# safeguard — verdict() is. The penalty only shapes how much leak grows
# before the fit gradient and penalty gradient equilibrate.
#
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
        self.K      = [[random.gauss(0, 0.1) if TOPO[i][j] else 0.0
                        for j in range(N)] for i in range(N)]
        # DEFORMATION: per-layer warming sensitivity (transfer subspace)
        self.deform = [0.0] * N
        # LEAK: imbalance DOF — the explicit cheat lever.
        # sum(nxt) - sum(state) = w * sum(leak) after each step.
        # When verdict() reads |Σ leak| > cons_tol after transfer,
        # the optimizer reached for the lever; the fit is false.
        self.leak   = [0.0] * N
        self.frozen = False

    def step(self, state, w, dt=1.0):
        """
        Conserving exchange step.

        For each directed edge (i←j) in TOPO:
          flux = K[i][j] * state[j] * (1 + deform[i] * w)
          t    = dt * tanh(flux)
          nxt[i] += t     receiver gains
          nxt[j] -= t     source loses

        Exchange terms cancel pairwise in the sum: Σ(nxt) = Σ(state)
        up to the leak channel. Conservation is structural.

        leak[i] * w is then added to each layer. This is the only path
        by which the optimizer can move Σ(nxt) away from Σ(state). It is
        intentionally explicit so verdict() can measure it.

        state : per-layer scalar list (length N)
        w     : warming index (scalar)
        dt    : timestep (default 1.0)
        """
        nxt = list(state)
        for i in range(N):
            for j in range(N):
                if TOPO[i][j]:
                    flux = self.K[i][j] * state[j] * (1.0 + self.deform[i] * w)
                    t    = dt * math.tanh(flux)
                    nxt[i] += t   # receiver gains
                    nxt[j] -= t   # source loses (conserving exchange)
        for i in range(N):
            nxt[i] += self.leak[i] * w   # imbalance channel
        return nxt

    def conservation_residual(self, state, nxt):
        """
        Returns |Σ leak| — the static signature of the cheat.

        After the conserving exchange, Σ(nxt) - Σ(state) = w * Σ(leak),
        so |Σ leak| directly answers whether the optimizer reached for the
        imbalance DOF. state and nxt are unused; accepted for API symmetry
        with the calling loop in fit().
        """
        return abs(sum(self.leak))

    # ── learnable params depend on freeze state ──────────────────────────

    def _params(self):
        if self.frozen:
            # K locked (structural invariant).
            # deform and leak are both free — leak is the transfer-phase lever.
            return ([('d', i) for i in range(N)]
                    + [('l', i) for i in range(N)])
        return ([('K', i, j) for i in range(N) for j in range(N) if TOPO[i][j]]
                + [('d', i) for i in range(N)]
                + [('l', i) for i in range(N)])

    def _get(self, p):
        if p[0] == 'd': return self.deform[p[1]]
        if p[0] == 'l': return self.leak[p[1]]
        return self.K[p[1]][p[2]]

    def _set(self, p, v):
        if p[0] == 'd':   self.deform[p[1]]    = v
        elif p[0] == 'l': self.leak[p[1]]       = v
        else:             self.K[p[1]][p[2]]    = v

    def fit(self, data, lr=0.01, epochs=200, conserve_penalty=10.0,
            grad_clip=1.0, weight_clip=3.0):
        """
        Train on data.

        data             : list of (state, w, target_state) triples
        lr               : learning rate
        epochs           : training epochs
        conserve_penalty : weight on |Σ leak| in the loss.
                           WARNING: this does NOT prevent cheating. The
                           optimizer will grow leak whenever fit gain exceeds
                           the penalty cost. The training-time regularizer
                           is not the safeguard — verdict() is. The penalty
                           only shapes how large |Σ leak| becomes before the
                           two gradients equilibrate.
        grad_clip        : per-parameter gradient magnitude limit.
        weight_clip      : per-parameter absolute bound after update.
                           Both clips required: without weight_clip, slow
                           accumulation over epochs saturates tanh and kills
                           conservation gradients.

        When frozen=True  : K locked; deform and leak update (transfer phase).
        When frozen=False : K, deform, and leak all update (pretrain phase).
        """
        for _ in range(epochs):
            for state, w, target in data:
                nxt  = self.step(state, w)
                err  = sum((nxt[i] - target[i])**2 for i in range(N))
                cons = abs(sum(self.leak))   # |Σ leak| — not raw flux
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
        Uses _get/_set accessors so perturbation is visible inside step().
        """
        v = self._get(p)
        self._set(p, v + h)
        nxt = self.step(state, w)
        l1  = (sum((nxt[i] - target[i])**2 for i in range(N))
               + cp * abs(sum(self.leak)))
        self._set(p, v)
        return (l1 - base) / h

    def freeze_structure(self):
        """
        TRANSFER POINT: K (topology weights) locked.
        deform and leak remain free.

        Call after pretraining on Holocene-dense data. During transfer,
        the optimizer can grow leak to fit non-conservative regime targets.
        verdict() then reads |Σ leak| to determine if it did.
        """
        self.frozen = True
        return self

    def verdict(self, target_data, fit_tol=1e-2, cons_tol=1e-3):
        """
        Three-way falsification verdict on held-out regime-shift data.

        cons = |Σ leak|.  Not the raw flux residual — the raw residual
        could be small simply because the exchange is conserving by design.
        Σ leak is the specific lever the optimizer has available to break
        conservation; its magnitude is the honest measure of the cheat.

        GREEN       : fit_err ≤ fit_tol AND |Σ leak| ≤ cons_tol
                      Coupling form invariant across regime. Deformation
                      absorbed the shift without breaking conservation.

        RED / FALSE FIT : fit_err ≤ fit_tol AND |Σ leak| > cons_tol
                      Optimizer reached for the imbalance DOF.
                      Model fits data by breaking physics — the dangerous
                      failure mode. The training-time penalty did not stop it.

        RED / HONEST FAIL : fit_err > fit_tol
                      Deformation cannot close the gap. Regime broke coupling
                      FORM, not just coefficients. Assumption_validator RED
                      at the boundary where the assumed invariant lives.

        Returns (color, reason, fit_err, cons).
        """
        fit_err = 0.0
        for state, w, target in target_data:
            nxt      = self.step(state, w)
            fit_err += sum((nxt[i] - target[i])**2 for i in range(N))
        fit_err /= len(target_data)
        cons = abs(sum(self.leak))   # |Σ leak|

        if fit_err <= fit_tol and cons <= cons_tol:
            return ("GREEN", "invariance held — coupling form survives regime",
                    fit_err, cons)
        if fit_err <= fit_tol and cons > cons_tol:
            return ("RED", "FALSE FIT — optimizer reached for the imbalance DOF",
                    fit_err, cons)
        return ("RED", "honest fail — regime broke coupling FORM, not coefficients",
                fit_err, cons)


# ── pipeline ──────────────────────────────────────────────────────────────
# m = CascadeTransfer().fit(holocene_dense)          # pretrain, cheap, all params
# m.freeze_structure().fit(regime_sparse, epochs=50) # transfer, deform+leak free
# print(m.verdict(regime_holdout))                   # GREEN / RED + reason
#
# The falsification reads: if fit is good AND |Σ leak| is large,
# the optimizer cheated during transfer. The training-time penalty did
# not stop it — cons_tol in verdict() is the actual gate.
