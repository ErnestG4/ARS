"""RQ1 Step 3 read (RQ1_SEAL.md §5; runs only after the seal is approved, stamped and Bitcoin-attested).

For each X ∈ {1e10, 1e11}:
  n = # ℤ[√2] split primes ≤ X (manifest rows); the ℤ[i] set is its first n split primes (matched N = 2n ideals).
  θ arrays (both ideals) for each field, sorted; R_F(β) = Var/(N/K), K = round(N^β), β on the grid.
  θ maps (§1): ℤ[√2] θ = log|π/π′|/(2 log ε) ∈ [0, ½] for the stored reduced generator (rq1_angles.thetas_from_ab);
  ℤ[i] θ = atan(u/v)/(π/2) ∈ (0, ½) for the stored pair 0 < u < v; each with its mirror 1 − θ (the other ideal).
  D(β) = R_ℤ[√2] − R_ℤ[i]; SE_diff from the sealed model (se_diff, c = C_SE, round-88 mirror calibration).
B2 (round 89, margin rule; b2_rule, shared with rq1_witness.py): PASS iff D > k·s·SE_diff at every remaining gated
  cell, FAIL iff any fails. k, the remaining cells and the per-cell SE scale s (1 unless the SE check against the
  witness triggered) come from SELECTION_JSON (rq1_witness.py select, on the round-88 replicates); CONFIRM_JSON
  (rq1_witness.py confirm, fresh seeds; "-" if no k was selected) must confirm that rule. If no k qualified or
  confirmation failed, B2 is UNPOWERED and the reading is descriptive only (D and magnitudes at every β, no
  verdict). Both files are inputs and their sha256 are pinned in the seal. A hash mismatch on any archive segment raises, so no output is written:
  VOID (hash).

Estimator: RW eq. 1.2 on θ ∈ [0, 1), window 1/K, exact. Streaming over the sorted θ: the breakpoints θ ± w/2 are the
sorted array shifted, merged by two pointers; Σ len·(count − Nw)² accumulated centred with Kahan summation;
single-threaded and deterministic (the double read must be byte-identical).

  python rq1_read.py ZS2_DIR ZI_DIR SELECTION_JSON CONFIRM_JSON OUT_JSON
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
from numba import njit

import rq1_angles as R

BETAS = [0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90]
XS = [10 ** 10, 10 ** 11]
GATED = {10 ** 10: [0.40, 0.45], 10 ** 11: [0.40, 0.45]}   # round 88: powered cells on the mirror calibration (HEURISTIC_B_MIRROR.json);
                                                          # round 89: the cells the witness covers (the SE check may remove some)
C_SE = 0.6271633049515984                                 # round 88: smallest symmetrised c (Poisson, K = 20)
LOGEPS2 = 2.0 * math.log(1 + math.sqrt(2.0))


@njit(cache=False, nogil=True)
def var_stream(th, K):
    """Exact ∫₀¹ (N(c) − Nw)² dc for sorted th in [0, 1), window w = 1/K (circular)."""
    N = th.shape[0]
    w = 1.0 / K
    h = w / 2.0
    mean = N * w
    # count at c = 0: points within h of 0 on the circle
    c0 = 0
    for i in range(N):
        if th[i] < h:
            c0 += 1
        else:
            break
    for i in range(N - 1, -1, -1):
        if th[i] > 1.0 - h:
            c0 += 1
        else:
            break
    # events: starts at (θ − h) mod 1 (+1), ends at (θ + h) mod 1 (−1); each list is the sorted θ rotated
    # starts: θ ≥ h give θ − h (ascending), then θ < h give θ − h + 1 (ascending)
    i0 = 0
    while i0 < N and th[i0] < h:
        i0 += 1
    j0 = 0
    while j0 < N and th[j0] < 1.0 - h:
        j0 += 1
    # ends: θ ≥ 1 − h give θ + h − 1 (ascending), then θ < 1 − h give θ + h
    si, ei = 0, 0
    cnt = c0
    pos = 0.0
    acc, comp = 0.0, 0.0
    for _ in range(2 * N):
        if si < N:
            k = i0 + si
            s = th[k] - h if k < N else th[k - N] - h + 1.0
        else:
            s = 2.0
        if ei < N:
            k = j0 + ei
            e = th[k] + h - 1.0 if k < N else th[k - N] + h
        else:
            e = 2.0
        if s <= e:
            nxt, d = s, 1
            si += 1
        else:
            nxt, d = e, -1
            ei += 1
        dv = cnt - mean
        y = (nxt - pos) * dv * dv - comp
        t = acc + y
        comp = (t - acc) - y
        acc = t
        pos = nxt
        cnt += d
    dv = cnt - mean
    y = (1.0 - pos) * dv * dv - comp
    acc += y
    return acc


def field_thetas(ab, field):
    """θ ∈ [0, ½] per stored row (float64): ℤ[√2] reduced generator (a, b), or ℤ[i] pair (u, v) with 0 < u < v."""
    if field == "zs2":
        return R.thetas_from_ab(ab)[0]
    return np.arctan(ab[:, 0].astype(np.float64) / ab[:, 1].astype(np.float64)) / (math.pi / 2)


def se_diff(r_s2, r_zi, K, c=C_SE):
    """The sealed SE model: each R has relative SD sqrt(2/(c K)); the two fields are independent."""
    s = math.sqrt(2 / (c * K))
    return math.hypot(r_s2 * s, r_zi * s)


def b2_rule(D, SE=None, rule=None):
    """D, SE: {(X, β): R_ℤ[√2] − R_ℤ[i]}, {(X, β): SE_diff}. rule (round 89): dict(k, cells [(X, β)], scale
    {(X, β): s}); PASS iff D > k·s·SE_diff at every cell of the rule, else FAIL. rule None: the round-88 sign rule
    (k = 0 at every GATED cell)."""
    if rule is None:
        rule = dict(k=0.0, cells=[(X, b) for X in XS for b in GATED[X]], scale={})
    return "PASS" if all(D[c] > rule["k"] * rule["scale"].get(c, 1.0) * (SE[c] if rule["k"] else 0.0)
                         for c in rule["cells"]) else "FAIL"


def load_rule(sel_path, conf_path):
    """The confirmed B2 rule from the round-89 selection and confirmation summaries, or None (B2 UNPOWERED).
    conf_path "-": no confirmation was run (no k selected)."""
    sel = json.load(open(sel_path))
    if sel["chosen_k"] is None:
        return None
    conf = json.load(open(conf_path))
    if not conf["OK"] or conf["rule"] != sel["rule"]:
        return None
    r = sel["rule"]
    cells = [(int(float(X)), float(b)) for X, b in r["cells"]]
    return dict(k=float(r["k"]), cells=cells, scale={(int(float(X)), float(b)): s for X, b, s in r["scale"]})


def load_field(d, field, n):
    """θ (both ideals) for the first n split primes of the archive in d, sorted; built segment by segment
    (each segment's sha256 checked against the manifest) to bound peak memory."""
    man = json.load(open(os.path.join(d, "MANIFEST.json")))
    th = np.empty(2 * n, np.float64)
    got = 0
    for s in man["segments"]:
        if got >= n:
            break
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        ab = np.load(path)[: n - got]
        t1 = field_thetas(ab, field)
        th[got:got + len(ab)] = t1
        th[n + got:n + got + len(ab)] = np.mod(1.0 - t1, 1.0)
        got += len(ab)
    assert got == n
    th.sort()
    return th


def sorted_uniform(N, rng, chunk=1 << 26, out=None, scale=1.0):
    """N sorted i.i.d. uniforms on [0, scale) without a sort: normalised cumulative sums of N + 1 exponential spacings
    (written into out if given)."""
    if out is None:
        out = np.empty(N, np.float64)
    tot, i = 0.0, 0
    while i < N:
        m = min(chunk, N - i)
        e = rng.standard_exponential(m)
        np.cumsum(e, out=out[i:i + m])
        out[i:i + m] += tot
        tot = out[i + m - 1]
        i += m
    tot += rng.standard_exponential()
    if scale == 1.0:
        out /= tot                                   # unchanged from the round-87 version (estimator check)
    else:
        out *= scale / tot
    return out


def n_below(d, X):
    man = json.load(open(os.path.join(d, "MANIFEST.json")))
    return int(sum(s["rows"] for s in man["segments"] if s["hi"] <= X))


def ratios(th, Ks):
    N = len(th)
    return [var_stream(th, K) / (N / K) for K in Ks]


def main(zs2, zi, sel, conf, out):
    res = dict(label="RQ1 read (sealed reading B)", rows={})
    rule = load_rule(sel, conf)
    res["rule"] = dict(selection_sha256=hashlib.sha256(open(sel, "rb").read()).hexdigest(),
                       confirm_sha256=None if conf == "-" else hashlib.sha256(open(conf, "rb").read()).hexdigest(),
                       confirmed=rule is not None,
                       k=None if rule is None else rule["k"],
                       cells=[] if rule is None else [[X, b] for X, b in rule["cells"]],
                       scale=[] if rule is None else [[X, b, s] for (X, b), s in rule["scale"].items()])
    D, SE = {}, {}
    for X in XS:
        n = n_below(zs2, X)
        N = 2 * n
        Ks = [int(round(N ** b)) for b in BETAS]
        r_s2 = ratios(load_field(zs2, "zs2", n), Ks)
        r_zi = ratios(load_field(zi, "zi", n), Ks)
        rows = []
        for b, K, a, c in zip(BETAS, Ks, r_s2, r_zi):
            se = se_diff(a, c, K)
            gated = rule is not None and (X, b) in rule["cells"]
            D[(X, b)], SE[(X, b)] = a - c, se
            rows.append(dict(beta=b, K=K, R_zs2=a, R_zi=c, D=a - c, SE_diff=se, D_over_SE=(a - c) / se,
                             heuristic_logX=1.8489 / math.log(X), heuristic_logN=1.8489 / math.log(N),
                             B2_gated=gated, B2_cell_holds=bool(gated and (a - c) > rule["k"] * rule["scale"].get(
                                 (X, b), 1.0) * se)))
            print(X, b, K, f"{a:.6f} {c:.6f} D {a - c:+.6f} SE {se:.4f}", "gated" if gated else "", flush=True)
        res["rows"][str(X)] = dict(n_split=n, N=N, rows=rows)
    res["B2"] = "UNPOWERED" if rule is None else b2_rule(D, SE, rule)
    res["READING"] = "DESCRIPTIVE (B2 UNPOWERED; no verdict)" if rule is None else res["B2"]
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print("B2", res["B2"], "READING", res["READING"])
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:6]))
