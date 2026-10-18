"""Corrected (B): the offset-averaged k₃ estimator (CORRECTED_B_DESIGN.md §1), one code path for the zeros' read, the CUE
calibration, the CUE_N known-answer slope and the selftests.

Input: pieces of unfolded positions, each (x sorted within [0, span), span, base): the zeros are one piece (x relative
to N̄(t₀), span = x_last, base = 0); CUE_1000 is one piece per matrix (span = N, base = matrix index × N). For each
offset u_k = kL/NU (k = 0…NU−1), the windows [u_k + jL, u_k + (j + 1)L), j < ⌊(span − u_k)/L⌋, of every piece; d = count
− round(L). k₃(u_k) is the k-statistic of all those counts; k̄₃ = mean over k.
Bootstrap (joint over offsets): the global axis (base + position) is cut into segments of G units; a window belongs to
the segment holding its global start; a replicate resamples segments with replacement — the same draw for every
offset — and recomputes k̄₃ from the resampled segment sums of 1, d, d², d³. SE_boot(G) = SD over B replicates.
"""
import math

import numpy as np

NU = 32
SEGS = (300, 1000, 3000, 10_000)


class Acc:
    """Per-(offset, segment) sums of 1, d, d², d³ for each segment length G; streamed piece by piece."""

    def __init__(self, L, total_span, segs=SEGS, nu=NU):
        self.L, self.nu, self.segs = float(L), nu, tuple(segs)
        self.c0 = int(round(L))
        self.nseg = {G: int(math.floor(total_span / G)) + 1 for G in self.segs}
        self.S = {G: np.zeros((4, nu, self.nseg[G])) for G in self.segs}

    def add_block(self, x, span, base):
        """x: (k, n) positions of k pieces of equal span (rows sorted, each in [0, span)); base: (k,) global bases."""
        x = np.atleast_2d(x)
        k = x.shape[0]
        base = np.asarray(base, float).reshape(k)
        rows = np.broadcast_to(np.arange(k)[:, None], x.shape)
        for q in range(self.nu):
            u = q * self.L / self.nu
            nw = int((span - u) // self.L)
            if nw <= 0:
                continue
            j = np.floor((x - u) / self.L).astype(np.int64)
            ok = (x >= u) & (j < nw)
            cnt = np.bincount(rows[ok] * nw + j[ok], minlength=k * nw).astype(float)
            d = cnt - self.c0
            start = (base[:, None] + u + self.L * np.arange(nw)[None, :]).ravel()
            for G in self.segs:
                seg = np.minimum((start // G).astype(np.int64), self.nseg[G] - 1)
                for p in range(4):
                    self.S[G][p, q] += np.bincount(seg, weights=d ** p, minlength=self.nseg[G])

    @staticmethod
    def _k3(n, s1, s2, s3):
        m1, m2, m3 = s1 / n, s2 / n, s3 / n
        return n * n * (m3 - 3 * m1 * m2 + 2 * m1 ** 3) / ((n - 1) * (n - 2))

    def k3_offsets(self):
        G = self.segs[0]
        T = self.S[G].sum(axis=2)                       # (4, nu)
        return np.array([self._k3(*T[:, q]) for q in range(self.nu)])

    def result(self, rng, n_boot=200):
        k3u = self.k3_offsets()
        out = dict(L=self.L, NU=self.nu, k3bar=float(k3u.mean()), k3_u=k3u.tolist(), se_boot={}, n_windows=float(
            self.S[self.segs[0]][0].sum(axis=1).mean()))
        for G in self.segs:
            S = self.S[G]
            ns = self.nseg[G]
            idx = rng.integers(0, ns, (n_boot, ns))
            C = np.zeros((n_boot, ns))
            np.add.at(C, (np.repeat(np.arange(n_boot), ns), idx.ravel()), 1.0)
            T = np.einsum("pqs,bs->bpq", S, C)          # (B, 4, nu)
            k3 = self._k3(T[:, 0], T[:, 1], T[:, 2], T[:, 3])
            out["se_boot"][str(G)] = float(np.std(k3.mean(axis=1), ddof=1))
        return out


def zeros_stats(x, L, rng, n_boot=200, segs=SEGS):
    """The read on one zeros file: x = N̄(γ) − N̄(t₀), increasing, ≥ 0."""
    a = Acc(L, x[-1], segs)
    a.add_block(x[None, :], float(x[-1]), [0.0])
    return a.result(rng, n_boot)


def cue_stats(sampler, n, L, rng, n_mat=1000, chunk=2000, n_boot=200, segs=SEGS):
    """CUE_N: ⌈n/n_mat⌉ matrices (sampler(rng, k) → (k, n_mat) eigenphases), each its own piece."""
    need = -(-n // n_mat)
    a = Acc(L, need * n_mat, segs)
    done = 0
    while need > 0:
        k = min(chunk, need)
        th = np.asarray(sampler(rng, k))
        x = np.sort(np.mod(th, 2 * np.pi), axis=1) * n_mat / (2 * np.pi)
        a.add_block(x, float(n_mat), (done + np.arange(k)) * n_mat)
        done += k
        need -= k
    return a.result(rng, n_boot)
