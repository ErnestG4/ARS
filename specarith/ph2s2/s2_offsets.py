"""Round 56 grid-anchoring sibling check, Stage 2 (DESCRIPTIVE; F2 is seen data; no verdict changes).

Stage 2's tapered window sums (tapered.window_sums) put window centres at x[0] + 4σ + 3b·k, anchored to the file's
first zero. Origin-shift red path: shift every centre by u = k/8 (k = 0..7, unit-spacing units), recompute ĝ_B per F2
file through the sealed estimator (s2read.stats_from_sums), pool with the sealed weights, and report the spread of
the pooled ĝ_B against Stage 2's 95% CI half-width (2·SE_pool = 0.0351). u = 0 must reproduce the sealed read exactly.

  python s2_offsets.py run ELL OUT_DIR      (spot; one process per F2 file; md5 against the F2 pin before decoding)
  python s2_offsets.py merge OUT_DIR        → OUT_DIR/S2_OFFSETS.json
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ph2r2"))
sys.path.insert(0, os.path.join(HERE, "..", "ph2s"))
import s2read as S  # noqa: E402
import tapered as T  # noqa: E402

OFFSETS = [k / 8 for k in range(8)]


def run(ell, out_dir):
    fname, t0, t1, pin = S.F2[ell]
    p = os.path.join(S.FRESH, fname)
    if hashlib.md5(open(p, "rb").read()).hexdigest() != pin:
        raise SystemExit(f"REFUSED: {p} md5 differs from the pin")
    t, x = S.decode(p)
    if not (t[0] >= t0 and t[-1] < t1):
        raise SystemExit(f"REFUSED: {p} heights outside the pinned range")
    m, w = T.pairs(x)
    rows = []
    for u in OFFSETS:
        s100 = T.window_sums(m, w, x[0] + u, x[-1], 100)
        s1e4 = T.window_sums(m, w, x[0] + u, x[-1], 10_000)
        g, se = S.stats_from_sums(s100, s1e4)
        rows.append(dict(u=u, g=g, se_g=se, n100=len(s100), n1e4=len(s1e4)))
        print(f"{ell} u={u:.3f}: ĝ_B {g:.5f} ± {se:.5f} (windows {len(s100)}, {len(s1e4)})", flush=True)
    os.makedirs(out_dir, exist_ok=True)
    json.dump(dict(ell=ell, file=fname, rows=rows), open(os.path.join(out_dir, f"s2off_{ell}.json"), "w"), indent=1)


def merge(out_dir):
    sealed = json.load(open(os.path.join(HERE, "results", "read", "S2_READ.json")))
    W = S.pool_weights(S.f2_windows())
    per = {e: json.load(open(os.path.join(out_dir, f"s2off_{e}.json")))["rows"] for e in S.F2}
    pooled = []
    for k, u in enumerate(OFFSETS):
        g = sum(W[e] * per[e][k]["g"] for e in S.F2)
        pooled.append(dict(u=u, g_pool=g))
    gp = np.array([r["g_pool"] for r in pooled])
    ci_half = sealed["result"]["guard_2se_pool"]
    files = {}
    for e in S.F2:
        g = np.array([r["g"] for r in per[e]])
        se0 = per[e][0]["se_g"]
        files[e] = dict(g_u=g.tolist(), spread=float(g.max() - g.min()), sd=float(g.std(ddof=1)), se_g=se0,
                        max_dev_over_se=float(np.max(np.abs(g - g[0])) / se0),
                        u0_reproduces_sealed=abs(g[0] - sealed["records"][e]["g"]) < 1e-12)
    out = dict(label="descriptive (round 56 sibling sweep); F2 is seen data; no verdict changes", offsets=OFFSETS,
               pooled=pooled, pooled_spread=float(gp.max() - gp.min()), pooled_sd=float(gp.std(ddof=1)),
               stage2_ci_half_width=ci_half, spread_over_ci_half=float((gp.max() - gp.min()) / ci_half),
               files=files, red_path_pass=all(f["max_dev_over_se"] <= 1 for f in files.values()))
    json.dump(out, open(os.path.join(out_dir, "S2_OFFSETS.json"), "w"), indent=1)
    print(f"pooled ĝ_B over 8 offsets: {gp.min():.5f}–{gp.max():.5f} (spread {gp.max() - gp.min():.5f}, SD "
          f"{gp.std(ddof=1):.5f}) against Stage 2's 95% CI half-width {ci_half:.4f}")
    for e, f in files.items():
        print(f"  {e}: spread {f['spread']:.5f}, max |ĝ(u) − ĝ(0)|/SE {f['max_dev_over_se']:.3f}, u=0 = sealed: "
              f"{f['u0_reproduces_sealed']}")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "merge":
        merge(sys.argv[2])
