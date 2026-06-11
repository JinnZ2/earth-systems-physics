# cascade_transfer_demo.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# End-to-end transfer + three-way falsification demo.
# Pretrain on Holocene-dense (cheap). Freeze coupling topology.
# Transfer to regime-sparse by retraining deform + leak only.
# verdict() separates: GREEN / RED-falsefit / RED-honestfail.
#
# The leak[] channel is the imbalance DOF. Without it a conserving model
# cannot false-fit (it just fails) and the two RED modes collapse into one.
# Penalize leak during training; verdict checks whether the optimizer
# reached for it anyway. That reach IS the lie.
#
# stdlib only.

import math
import random

random.seed(7)

# ── layer stack and frozen coupling topology ──────────────────────────────

LAYERS = list(range(-1, 7))          # -1..6  (orbit -> surface)
N      = len(LAYERS)
IDX    = {L: i for i, L in enumerate(LAYERS)}
TOPO   = [[0]*N for _ in range(N)]
for i in range(N-1):
    TOPO[i+1][i] = 1                  # forward cascade
TOPO[IDX[6]][IDX[0]] = 1             # dynamo spectral resonance -> surface
EDGES  = [(i, j) for i in range(N) for j in range(N) if TOPO[i][j]]


# ── model: conserving exchange + explicit leak (imbalance) ────────────────

class CascadeTransfer:
    def __init__(self):
        self.K      = {e: random.gauss(0, 0.05) for e in EDGES}  # structural
        self.deform = [0.0] * N        # regime-warming sensitivity
        self.leak   = [0.0] * N        # imbalance channel (penalized)
        self.frozen = False

    def step(self, state, w):
        """
        Conserving exchange: for each edge (i←j), i gains t, j loses t.
        Exchange terms cancel in the sum. leak[] is the only path by which
        sum(nxt) can depart from sum(state).
        """
        d = list(self.leak)            # leak enters as net imbalance per layer
        for (i, j) in EDGES:
            t    = self.K[(i, j)] * math.tanh(state[j]) * (1.0 + self.deform[i] * w)
            d[i] += t                  # receiver gains
            d[j] -= t                  # source loses (conserving exchange)
        return [state[k] + d[k] for k in range(N)]

    def conservation_residual(self, state, nxt):
        # exchange cancels; residual == |sum(leak)| by construction
        return abs(sum(nxt) - sum(state))

    # ── params depend on freeze state ────────────────────────────────────

    def _params(self):
        p = []
        if not self.frozen:
            p += [('K', e) for e in EDGES]
        p += [('d', i) for i in range(N)]
        p += [('l', i) for i in range(N)]
        return p

    def _get(self, p):
        if p[0] == 'K': return self.K[p[1]]
        if p[0] == 'd': return self.deform[p[1]]
        return self.leak[p[1]]

    def _set(self, p, v):
        if   p[0] == 'K': self.K[p[1]]      = v
        elif p[0] == 'd': self.deform[p[1]]  = v
        else:             self.leak[p[1]]    = v

    def _loss(self, data, leak_pen):
        fit = 0.0
        for state, w, target in data:
            nxt  = self.step(state, w)
            fit += sum((nxt[k] - target[k])**2 for k in range(N))
        fit /= len(data)
        cons = sum(self.leak)**2            # net imbalance, penalized
        return fit + leak_pen * cons

    def fit(self, data, lr=0.04, epochs=1200, leak_pen=0.02, h=1e-5,
            clip=0.15, mom=0.9):
        """
        Batch gradient descent with momentum and learning rate annealing.

        leak_pen : penalizes Σ(leak)² during training. Note: this does NOT
                   prevent the optimizer from growing leak when fit gain exceeds
                   penalty cost. The penalty shapes the equilibrium; verdict()
                   is the actual gate.
        """
        params = self._params()
        vel    = {id(p): 0.0 for p in params}
        for ep in range(epochs):
            base  = self._loss(data, leak_pen)
            grads = []
            for p in params:                        # all grads vs frozen base
                v = self._get(p)
                self._set(p, v + h)
                l1 = self._loss(data, leak_pen)
                self._set(p, v)
                grads.append((l1 - base) / h)
            step = lr * (0.5 ** (ep / 400))         # anneal
            for p, g in zip(params, grads):
                u = mom * vel[id(p)] - step * g
                u = max(-clip, min(clip, u))
                vel[id(p)] = u
                self._set(p, self._get(p) + u)
        return self

    def freeze_structure(self):
        """Topology + coupling magnitudes locked. deform and leak remain free."""
        self.frozen = True
        return self

    def verdict(self, target, fit_tol=1e-2, cons_tol=1e-2):
        """
        Three-way falsification on held-out data.

        cons = |Σ leak|.  After the conserving exchange, this is the only
        quantity that measures whether the optimizer reached for the cheat.

        GREEN       : fit good AND |Σ leak| ≤ cons_tol
        RED/FALSE FIT : fit good AND |Σ leak| > cons_tol  ← the dangerous one
        RED/HONEST FAIL : fit bad (regime broke coupling FORM)
        """
        fit = sum(
            sum((self.step(s, w)[k] - t[k])**2 for k in range(N))
            for s, w, t in target
        ) / len(target)
        cons = abs(sum(self.leak))   # net imbalance the model carried

        if fit <= fit_tol and cons <= cons_tol:
            return ("GREEN", "invariance held — coupling form survives regime",        fit, cons)
        if fit <= fit_tol and cons > cons_tol:
            return ("RED ", "FALSE FIT — leak absorbed a conservation break",          fit, cons)
        return ("RED ", "HONEST FAIL — regime broke coupling FORM, not coefficients",  fit, cons)


# ── synthetic truth generators (three regimes) ───────────────────────────

K_TRUE   = {e: random.uniform(0.10, 0.25) * random.choice([-1, 1]) for e in EDGES}
DEF_TRUE = [random.uniform(0.1, 0.4) for _ in range(N)]
SRC      = 0.12            # false-fit hidden source (state-independent, rides on w)
EXTRA    = (IDX[3], IDX[0])   # honest-fail off-topology skip: layer 0 → layer 3
E_OFF    = 0.30


def _exchange(state, w):
    d = [0.0] * N
    for (i, j) in EDGES:
        t    = K_TRUE[(i, j)] * math.tanh(state[j]) * (1.0 + DEF_TRUE[i] * w)
        d[i] += t
        d[j] -= t
    return d


def truth_green(state, w):
    """Conserving exchange — same structural form, different deform regime."""
    d = _exchange(state, w)
    return [state[k] + d[k] for k in range(N)]


def truth_falsefit(state, w):
    """Adds a net source term: sum(nxt) > sum(state). Requires leak to fit."""
    d = _exchange(state, w)
    for k in range(N):
        d[k] += SRC * w                  # non-conserving offset
    return [state[k] + d[k] for k in range(N)]


def truth_honestfail(state, w):
    """Adds an off-topology edge (0→3 skip). Conserving but wrong FORM."""
    d = _exchange(state, w)
    i, j = EXTRA
    t    = E_OFF * math.tanh(state[j]) * (1.0 + w)
    d[i] += t
    d[j] -= t                             # conserving, but not in TOPO
    return [state[k] + d[k] for k in range(N)]


def sample(gen, n, w_lo, w_hi):
    out = []
    for _ in range(n):
        s = [random.uniform(-0.6, 0.6) for _ in range(N)]
        w = random.uniform(w_lo, w_hi)
        out.append((s, w, gen(s, w)))
    return out


# ── pipeline ─────────────────────────────────────────────────────────────

def run(label, target_gen):
    holocene = sample(truth_green,  80, 0.0, 0.2)   # dense, cheap, low warming
    target   = sample(target_gen,   20, 0.6, 1.0)   # sparse, expensive, warming
    holdout  = sample(target_gen,   20, 0.6, 1.0)

    m = CascadeTransfer().fit(holocene, epochs=1500)  # pretrain (all params)
    m.freeze_structure().fit(target, epochs=1200)     # transfer (deform+leak only)
    code, why, fit, cons = m.verdict(holdout)
    print(f"  {label:12s} -> {code} | fit={fit:.2e}  cons={cons:.2e} | {why}")


if __name__ == "__main__":
    print("REGIME TRANSFER VERDICTS (frozen coupling, deform+leak retrained)\n")
    run("conserving",  truth_green)
    run("hidden-src",  truth_falsefit)
    run("off-form",    truth_honestfail)
