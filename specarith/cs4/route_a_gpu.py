"""Route (a) terms with the prime sums on the GPU (CuPy), 2026-10-12.

Profile of a route (a) job: ~80% of the time is cs4fast.FastZeta.psum's prime-sum blocks, i.e. complex exponentials
p^{e} and elementwise arithmetic over (rows × primes) arrays of ~10⁷ entries. GPUZeta overrides only psum and Astar:
  - psum: the same summand functions f(P, p, lp, …) evaluated on device arrays, with P(e) = exp(e·log p) in complex
    double. Route (a)'s points lie in one gap s ≤ 1.8, so every phase |Im(e)|·log p is small; this is ASSERTED per call
    (≤ PHASE_MAX = 1e3 rad, double reduction error ≤ ~2e-13 rad) and the call fails closed otherwise.
  - Astar: cs4fast's formula transcribed for device arrays (np.prod over a list → a product loop; the resonance branch
    |1 − p^{b₁−b₂}| < 1e-2 by its 64-point θ-integral in double, under the same phase bound).
Everything else (ζ pieces via zeta_em, the assembly, the quadrature) is the CPU code, unchanged. cs4fast is not edited.

Validation before use (`validate`): finished long-double CPU jobs are recomputed; every term must agree to ABS_TOL
absolute (route (a)'s Δp is ~3e-2 and the bins resolve ~1e-4, so 1e-12 is far below anything that matters).

  python route_a_gpu.py validate OUT_DIR N        N finished jobs from OUT_DIR (largest s first)
  python route_a_gpu.py jobs OUT_DIR JOB [JOB ...]  compute jobs into terms_cj{iii}.jsonl, skipping any already done
"""
import glob
import json
import os
import sys
import time

import cupy as cp
import numpy as np

import cs4fast as F
import route_a_zeta as RA

PHASE_MAX = 1e3
ABS_TOL = 1e-12
CH = int(os.environ.get("GPU_CHUNK", "64"))


class GPUZeta(F.FastZeta):
    def __init__(self, t, pmax):
        super().__init__(t, pmax=pmax)
        self.p_g = cp.asarray(self.p)[None, :]
        self.lp_g = cp.asarray(self.lp)[None, :]
        self.lpmax = float(self.lp.max())

    def psum(self, f, *args, prod=False):
        args = [np.broadcast_to(np.asarray(a, complex), np.broadcast(*[np.asarray(b) for b in args]).shape) for a in args]
        bound = 4 * max(float(np.max(np.abs(a.imag))) for a in args) * self.lpmax
        if bound > PHASE_MAX:
            raise ValueError(f"phase bound {bound:.1f} rad > {PHASE_MAX} (GPU path is for route (a)'s small phases)")
        n = args[0].shape[0]
        out = cp.empty(n, complex)
        p, lp = self.p_g, self.lp_g
        P = lambda e: cp.exp(e * lp)
        for i in range(0, n, CH):
            sub = [cp.asarray(a[i:i + CH, None]) for a in args]
            m = f(P, p, lp, *sub)
            out[i:i + CH] = cp.exp(cp.log(m).sum(1)) if prod else m.sum(1)
        return cp.asnumpy(out)

    def Astar(self, a1, a2, b1, b2):
        def f(P, p, lp, a1, a2, b1, b2):
            zp = lambda x: 1 / (1 - P(-x))

            def Zp(X, Y):
                out = 1.0
                for x in X:
                    for y in Y:
                        out = out * (1 / zp(1 + x + y))
                return out
            A_, B_ = (a1, a2), (b1, b2)
            mA, mB = tuple(-x for x in A_), tuple(-x for x in B_)
            pref = Zp(A_, B_) * Zp(mA, mB) / (Zp(A_, mA) * Zp(B_, mB))
            T1 = zp(1 - a1 - b1) * zp(1 - a2 - b1) * zp(b2 - b1) / (zp(1) * zp(-a1 - b1) * zp(-a2 - b1) * zp(1 + b2 - b1))
            T2 = zp(1 - a1 - b2) * zp(1 - a2 - b2) * zp(b1 - b2) / (zp(1) * zp(-a1 - b2) * zp(-a2 - b2) * zp(1 + b1 - b2))
            fac = pref * P(-(a1 + a2 + b1 + b2)) * (1 - T1 - T2)
            q = P(b1 - b2)
            bad = cp.abs(1 - q) < 1e-2
            if bool(bad.any()):
                shape = bad.shape
                rows, cols = cp.nonzero(bad)
                pp = cp.broadcast_to(p, shape)[rows, cols]
                A1, A2 = cp.broadcast_to(a1, shape)[rows, cols], cp.broadcast_to(a2, shape)[rows, cols]
                Bb1, Bb2 = cp.broadcast_to(b1, shape)[rows, cols], cp.broadcast_to(b2, shape)[rows, cols]
                th = cp.arange(64) / 64
                e = cp.exp(2j * cp.pi * th)[None, :]
                lpp = cp.log(pp)[:, None]
                pw = lambda ex: cp.exp(ex[:, None] * lpp)
                g = 1.0
                for b in (Bb1, Bb2):
                    g = g / (1 - cp.conj(e) * pw(-0.5 + b))
                for a in (A1, A2):
                    g = g / (1 - e * pw(-0.5 + a))
                for a in (A1, A2):
                    g = g * (1 - cp.conj(e) * pw(-0.5 - a))
                for b in (Bb1, Bb2):
                    g = g * (1 - e * pw(-0.5 - b))
                integ = g.mean(1)
                prefb = cp.broadcast_to(pref, shape)[rows, cols]
                fac[rows, cols] = prefb * integ
            return fac
        return self.psum(f, a1, a2, b1, b2, prod=True)


def run_one(job):
    """route_a_zeta._run_one with GPUZeta in place of FastZeta (same jobs, same quadrature, same sine terms)."""
    f, which, pm, m, s = job
    t = RA.height(f, which)
    Z = GPUZeta(t, pmax=pm)
    Tz = RA.terms(Z, s, m)
    Ts = RA.terms(None, s, m)
    out = dict(file=f, which=which, t=t, ell=Z.ell, pmax=pm, m=m, s=s, zeta=Tz, sine=Ts, engine="gpu-cupy")
    if pm == RA.PMAX_MAIN and m == RA.M_QUAD and which == "mean":
        out["T5_sine"] = RA.T5_det(s, 10)
    return out


def done_keys(out_dir):
    keys = set()
    for fn in glob.glob(os.path.join(out_dir, "terms_c*.jsonl")):
        for line in open(fn):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            keys.add((r["file"], r["which"], r["pmax"], r["m"], r["s"]))
    return keys


def run_jobs(out_dir, idx):
    os.makedirs(out_dir, exist_ok=True)
    J = RA.jobs()
    for i in idx:
        if J[i] in done_keys(out_dir):
            continue
        t0 = time.time()
        r = run_one(J[i])
        r["secs"] = time.time() - t0
        with open(os.path.join(out_dir, f"terms_cj{i:03d}.jsonl"), "a") as fh:
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        print(i, J[i], "%.0fs" % r["secs"], flush=True)


def validate(out_dir, n, smallest=False):
    rows = []
    for fn in sorted(glob.glob(os.path.join(out_dir, "terms_c*.jsonl"))):
        rows += [json.loads(x) for x in open(fn)]
    rows = sorted(rows, key=lambda r: (r["s"] if smallest else -r["s"]))[:n]
    worst = 0.0
    for r in rows:
        j = (r["file"], r["which"], r["pmax"], r["m"], r["s"])
        t0 = time.time()
        new = run_one(j)
        d = max(abs(r["zeta"][k] - new["zeta"][k]) for k in ("T2", "T3", "T4"))
        worst = max(worst, d)
        print(f"job s={r['s']:.4f} pmax={r['pmax']} m={r['m']}: max |ΔT| {d:.2e} "
              f"(T4 {r['zeta']['T4']:.6e}); {time.time() - t0:.0f} s", flush=True)
    ok = worst <= ABS_TOL
    print(f"GPU validation on {len(rows)} finished jobs: worst |ΔT| {worst:.2e} vs {ABS_TOL:.0e}: {'PASS' if ok else 'FAIL'}",
          flush=True)
    return ok


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "validate":
        sys.exit(0 if validate(a[1], int(a[2]), smallest=len(a) > 3 and a[3] == "small") else 1)
    elif a[0] == "jobs":
        run_jobs(a[1], [int(x) for x in a[2:]])
    else:
        raise SystemExit(__doc__)
