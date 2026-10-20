"""L6 long CUE baseline (L6_BASELINE_DESIGN.md, approved round 66). Step 0 here; generation, gates and comparisons are
added in later commits, each before it runs.

Step 0 (design §2) — cbe.py's red paths before any baseline sequence is drawn (spot, CPU, gpu = False):
  python l6_base.py step0 selftest OUT.json    V1–V4 exactly as cbe.py's own selftest (incl. V4's red path)
  python l6_base.py step0 v5 OUT.json          N = 10⁴: Prüfer roots against dense CMV eigvals, max |Δθ|·N/2π ≤ 1e-8
  python l6_base.py step0 v67 OUT.json         N = 10⁵ (β = 2): certify() passes on a real draw; red paths: one root
                                               duplicated, two roots swapped, one root deleted (count check) — each must be
                                               refused; V7: every accepted root's residual |ψ_{N−1}(θ) − c_m| < F_ACCEPT,
                                               reported with its maximum; wall time of one N = 10⁵ draw recorded.
Seeds: [20261020, 65, 900 + k] (step 0 only; disjoint from the baseline's [20261020, 65, r], r < 50).
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cs4"))
import cbe  # noqa: E402

V5_TOL = 1e-8


def env():
    import scipy
    return dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__)


def step0_selftest(out):
    t = time.time()
    res = cbe.selftest(gpu=False)
    res["wall_s"] = round(time.time() - t, 1)
    res["env"] = env()
    json.dump(res, open(out, "w"), indent=1, default=float)
    return 0 if res["PASS"] else 1


def step0_v5(out, N=10_000):
    rng = np.random.default_rng([20261020, 65, 905])
    a = cbe.verblunsky(rng, 1, N, 2.0)
    t = time.time()
    th, it = cbe.roots_np(a)
    t_pr = time.time() - t
    t = time.time()
    ref = cbe.dense_phases(a[0])
    t_d = time.time() - t
    dd = np.angle(np.exp(1j * (th[0] - ref))) * N / cbe.TWO_PI
    worst = float(np.abs(dd).max())
    res = dict(N=N, max_abs_unfolded_diff=worst, tol=V5_TOL, iters=int(it), t_prufer_s=round(t_pr, 1),
               t_dense_s=round(t_d, 1), PASS=bool(worst <= V5_TOL), env=env())
    json.dump(res, open(out, "w"), indent=1)
    print(res, flush=True)
    return 0 if res["PASS"] else 1


def refused(th):
    try:
        cbe.certify(th)
        return False
    except RuntimeError:
        return True


def step0_v67(out, N=100_000):
    rng = np.random.default_rng([20261020, 65, 967])
    a = cbe.verblunsky(rng, 1, N, 2.0)
    t = time.time()
    th, it = cbe.roots_np(a)
    wall = time.time() - t
    ok_real = not refused(th) and th.shape == (1, N)
    dup = th.copy()
    dup[0, N // 2] = dup[0, N // 2 - 1]
    swp = th.copy()
    swp[0, [N // 3, N // 3 + 1]] = swp[0, [N // 3 + 1, N // 3]]
    dele = np.delete(th, N // 4, axis=1)
    red = dict(duplicated=refused(dup), swapped=refused(swp), deleted_count_check=dele.shape[1] != N)
    c0, _ = cbe.targets(a)
    c = c0[:, None] + cbe.TWO_PI * np.arange(N)[None, :]
    phi, _ = cbe.phi_np(a, th)
    resid = np.abs(N * th - c + phi)
    sp = cbe.spacings(th)
    res = dict(N=N, iters=int(it), wall_s=round(wall, 1), certify_real=bool(ok_real), red_paths=red,
               V6_PASS=bool(ok_real and all(red.values())), max_residual=float(resid.max()),
               F_ACCEPT=cbe.F_ACCEPT, V7_PASS=bool(resid.max() < cbe.F_ACCEPT),
               psi_headroom_ulp=float(np.spacing(cbe.TWO_PI * N)), min_spacing=float(sp.min()),
               mean_spacing=float(sp.mean()), env=env())
    res["PASS"] = res["V6_PASS"] and res["V7_PASS"]
    json.dump(res, open(out, "w"), indent=1)
    print(res, flush=True)
    return 0 if res["PASS"] else 1


if __name__ == "__main__":
    if sys.argv[1] == "step0":
        sys.exit({"selftest": step0_selftest, "v5": step0_v5, "v67": step0_v67}[sys.argv[2]](sys.argv[3]))
