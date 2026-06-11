# transfer_kernel.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Regime transfer kernel for earth-systems-physics.
# Pretrain on Holocene-dense data; transfer to regime-shift-sparse data.
# Freezes structure (coupling topology), retrains only deformation params.
# stdlib only.

import math
import random


class Kernel:
    def __init__(self, n_struct, n_deform):
        # structural params: coupling topology, conservation coefficients
        self.struct = [random.gauss(0, 0.1) for _ in range(n_struct)]
        # deformation params: regime-dependent (warming index, dk/dt)
        self.deform = [0.0] * n_deform
        self.frozen = False

    def forward(self, x):
        s = sum(w * xi for w, xi in zip(self.struct, x))
        d = sum(w * xi for w, xi in zip(self.deform, x[:len(self.deform)]))
        return math.tanh(s) + d   # structure + deformation correction

    def fit(self, data, lr=0.01, epochs=200):
        """
        Train kernel on data.

        data   : list of (x_vec, y) pairs
        lr     : learning rate
        epochs : training epochs

        When frozen=True only deform params update (transfer phase).
        When frozen=False both struct and deform params update (pretrain phase).

        Uses finite-difference gradients; stdlib only.
        """
        # Build (group_list, index) refs so in-place writes reach self.struct / self.deform.
        # Concatenating the two lists would create a copy and break in-place updates.
        if self.frozen:
            param_refs = [(self.deform, i) for i in range(len(self.deform))]
        else:
            param_refs = ([(self.struct, i) for i in range(len(self.struct))]
                          + [(self.deform, i) for i in range(len(self.deform))])

        for _ in range(epochs):
            for x, y in data:
                err = self.forward(x) - y
                for group, i in param_refs:
                    group[i] -= lr * err * self._grad(x, group, i)
        return self

    def _grad(self, x, group, idx, h=1e-5):
        """
        Finite-difference gradient of forward() w.r.t. group[idx].
        group is the actual list (self.struct or self.deform), so
        perturbations are visible inside forward().
        """
        group[idx] += h
        f1 = self.forward(x)
        group[idx] -= 2 * h
        f0 = self.forward(x)
        group[idx] += h
        return (f1 - f0) / (2 * h)

    def freeze_structure(self):
        """
        Transfer point: invariants locked, deformation subspace open.
        Call after pretraining; subsequent fit() calls update only deform.
        """
        self.frozen = True
        return self


# ── usage pipeline ────────────────────────────────────────
# 1. pretrain on Holocene-dense data (cheap regime)
# k = Kernel(n_struct=12, n_deform=3).fit(holocene_data)
#
# 2. freeze invariants, transfer to regime-shift data (sparse, expensive)
# k.freeze_structure().fit(regime_shift_data, epochs=50)
#
# 3. falsification hook:
#    if frozen-structure transfer beats full retrain on sparse target data
#    → invariance hypothesis holds
#    if not → the "invariant" wasn't (regime shift broke structure, not
#    just parameters — your assumption_validator RED condition)
