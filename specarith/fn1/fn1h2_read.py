# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2 read (FN1H2_SEAL.md, draft as revised 2026-11-04 after Will's D1–D5 rulings).

  python fn1h2_read.py refs  PINS OUT [X]    pre-seal D2 (b): the nine h = 1 references only (seen data, no h = 2 data)
  python fn1h2_read.py dry   PINS OUT [X]    §9.F rehearsal: h = 2 sets from the pins file's "dry" block (synthetic
                                             fixtures, fn1h2_fixtures.py), everything else as the read; X (default X*)
                                             lets the rehearsal run the whole pipeline at a smaller cutoff (2·10⁹),
                                             with its own refs file at that X
  python fn1h2_read.py read  PINS OUT        the sealed read (X = X* enforced)

Sets (all cut at X* = 2·10¹⁰ by manifest segment, hi ≤ X*):
- h = 1 reference: the nine class-number-1 fields (fn1_pins2.json's archives; seen data), all split primes p ≤ X*.
- h = 2: the 18 principal-prime archives (fn1h2_archive.py), all principal split primes p ≤ X*.
- χ′ control (D5, descriptive): each h = 1 reference set restricted to p with (5/p) = +1, i.e. p mod 5 ∈ {1, 4}.
- matched-N reference (descriptive): each h = 1 field's first n̄ rows, n̄ = the mean principal count of the nine primary
  h = 2 sets.
θ and its mirror 1 − θ, sorted; N = 2n; R(K) = var_stream(θ, K)/(N/K) (rq1_read.var_stream, exact) at the fixed
K_P = 57,801 / 7,873 / 2,906 (β 0.55 / 0.45 / 0.40; stage 1's K), the same K for every set, normalised by each set's
own N/K.

Guards (raise, no output): every manifest sha256 against PINS; every loaded segment sha256 against its manifest; in
dry / read mode the recomputed h = 1 references must equal the committed D2 (b) file (PINS "refs": path + sha256)
bit for bit; the (★) predictions file pinned by sha256; mount guard on /mnt/data.

Primary (β 0.55): reference line R = a + b·C by OLS over the nine h = 1 references (C_F = log(|D|(w/2)²)).
s = mean_{nine primary h = 2}(R_h2,j − a − b·C_j) / b.
  CONDUCTOR iff s > −0.4·log 4 (−0.5545); L-VALUE iff s < −0.6·log 4 (−0.8318); else INCONCLUSIVE;
  VOID (reference slope ≤ 0) if b ≤ 0.
K0 (descriptive; Will 2026-11-04: "K0 descriptive"): quadratic q(C) = a₂ + b₂C + c₂C² by OLS over the nine h = 1
references, frozen; the within-h = 2 quadratic coefficient over the nine primary fields with its SE and
t = sign(c₂)·ĉ₂,h2 / SE (6 df), reported with no verdict. Quadratic sensitivity check (descriptive; Will 2026-11-04):
s against q instead of the line, argmin over s of Σ_primary (R_h2,j − q(C_j + s))², shown beside the primary.
Descriptive (no verdict): s at β 0.45 / 0.40 (their own lines); s_j per field (all 18; K2 = −15 flagged); the mean s
over all 18 and over the descriptive nine (extrapolation outside the h = 1 C range flagged); the matched-N reference
and s against it; the χ′ control's ΔR = R_thin − R_ref per h = 1 field beside (★)'s committed "runs in X" and "runs
in N" values; within-field drift of each h = 2 set (8 contiguous prime-order segments, fn1_read2.seg_noise); the
Spearman ρ of R_h2 on C over the 18 (seeded permutation p, 200,000 draws); the controls (Will: "L′/L(1) and Chen's
term are controls"): Pearson r of s_j (β 0.55) with L′/L(1, χ_D) and with Chen's L-term −2·L′/L(2, χ_D) from the
committed `lead/FN1H2_CONTROLS.json` (pinned), over the nine primary fields (exact two-sided permutation p over 9!) and
over all 18 (r only).
Output: JSON, sorted keys, no timings (sidecar OUT.timing). stdout prints only "done".
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import rq1_read as Q
except ImportError:
    sys.path.insert(0, os.path.join(HERE, "..", "rq1"))
    import rq1_read as Q
import rq1_zw as Z
import fn1_archive as FA
import fn1h2_archive as H
import fn1_read2 as F2

XSTAR = 2 * 10 ** 10
BETAS = ["0.55", "0.45", "0.4"]
KP = {"0.55": 57801, "0.45": 7873, "0.4": 2906}
H1 = ["-7", "-8", "-11", "zi", "-19", "zw", "-43", "-67", "-163"]
C1 = {"-7": math.log(7), "-8": math.log(8), "-11": math.log(11), "zi": math.log(16), "-19": math.log(19),
      "zw": math.log(27), "-43": math.log(43), "-67": math.log(67), "-163": math.log(163)}
H2 = [str(d) for d in H.FIELDS]
PRIMARY = [str(d) for d in H.PRIMARY]
C2 = {d: math.log(-int(d)) for d in H2}
CUT_C, CUT_L = -0.4 * math.log(4), -0.6 * math.log(4)
ALPHA_K0 = 0.05
SEED_RHO18 = 20261104


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def theta_norm(field, rows):
    if field == "zi":
        u, v = rows[:, 0].astype(np.int64), rows[:, 1].astype(np.int64)
        return Q.field_thetas(rows, "zi"), u * u + v * v
    if field == "zw":
        u, v = rows[:, 0].astype(np.int64), rows[:, 1].astype(np.int64)
        return Z.thetas_zw(rows), u * u + 3 * v * v
    D = int(field)
    if D in H.FIELDS:
        return H.thetas(D, rows), H.norm_of(D, rows)
    return FA.thetas(D, rows), FA.norm_of(D, rows)


def load(d, field, pinned_sha, X=XSTAR, chi5=False, nmax=None, keep_half=False):
    """Rows with p ≤ X (segments with hi ≤ X), optionally only (5/p) = +1, optionally the first nmax rows."""
    mp = os.path.join(d, "MANIFEST.json")
    assert sha_file(mp) == pinned_sha, ("manifest pin", d)
    man = json.load(open(mp))
    segs = [s for s in man["segments"] if s["hi"] <= X]
    assert segs and segs[-1]["hi"] == X, ("archive does not reach X", d)
    parts, got = [], 0
    for s in segs:
        if nmax is not None and got >= nmax:
            break
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        rows = np.load(path)
        assert len(rows) == s["rows"], ("segment rows", path)
        t, p = theta_norm(field, rows)
        if chi5:
            r = p % 5
            t = t[(r == 1) | (r == 4)]
        if nmax is not None:
            t = t[: nmax - got]
        parts.append(t)
        got += len(t)
    half = np.concatenate(parts)
    del parts
    if nmax is not None:
        assert len(half) == nmax, ("rows", d, len(half), nmax)
    n = len(half)
    th = np.empty(2 * n, np.float64)
    th[:n] = half
    th[n:] = np.mod(1.0 - half, 1.0)
    th.sort()
    return th, (half if keep_half else None), n


def Rs(th):
    N = len(th)
    return {b: float(Q.var_stream(th, K) / (N / K)) for b, K in KP.items()}


def refs(pins, X):
    out = {}
    for f in H1:
        a = pins["archives"][f]
        th, _, n = load(a["dir"], f, a["manifest_sha256"], X=X)
        out[f] = dict(n=n, N=2 * n, R=Rs(th))
        del th
    return out


def line(R, C, fields):
    x = np.array([C[f] for f in fields]); y = np.array([R[f] for f in fields])
    A = np.vstack([np.ones(len(x)), x]).T
    return np.linalg.lstsq(A, y, rcond=None)[0]


def quad(R, C, fields):
    x = np.array([C[f] for f in fields]); y = np.array([R[f] for f in fields])
    A = np.vstack([np.ones(len(x)), x, x * x]).T
    return np.linalg.lstsq(A, y, rcond=None)[0]


def classify(s, b):
    if b <= 0:
        return "VOID (reference slope <= 0)"
    return "CONDUCTOR" if s > CUT_C else ("L-VALUE" if s < CUT_L else "INCONCLUSIVE")


T95_6 = 1.9431802803927816          # one-sided 5% point of Student t, 6 df


def k0_test(Rh2, q):
    """K0: the within-h = 2 curvature has the sign of the frozen h = 1 quadratic's, significantly (one-sided t, 6 df)."""
    if q[2] == 0:
        return dict(reading="descriptive; h = 1 quadratic coefficient is 0")
    x = np.array([C2[d] for d in PRIMARY]); y = np.array([Rh2[d] for d in PRIMARY])
    A = np.vstack([np.ones(9), x, x * x]).T
    coef, rss = np.linalg.lstsq(A, y, rcond=None)[:2]
    s2 = float(((y - A @ coef) ** 2).sum()) / 6
    se = math.sqrt(s2 * np.linalg.inv(A.T @ A)[2, 2])
    t = float(np.sign(q[2]) * coef[2] / se) if se > 0 else float("nan")
    return dict(h1_c2=float(q[2]), h2_c2=float(coef[2]), h2_c2_se=se, t=t, t_one_sided_5pct=T95_6,
                reading="descriptive (Will 2026-11-04: K0 descriptive; no verdict)")


def s_quad(R2, q):
    """Sensitivity check (descriptive; Will 2026-11-04): s against the frozen h = 1 quadratic, argmin over s in
    [−4, 4] (grid step 1e-4) of Σ_primary (R_h2,j − q(C_j + s))²."""
    c = np.array([C2[d] for d in PRIMARY]); y = np.array([R2[d] for d in PRIMARY])
    g = np.arange(-40000, 40001) * 1e-4
    x = c[None, :] + g[:, None]
    sse = ((y[None, :] - (q[0] + q[1] * x + q[2] * x * x)) ** 2).sum(1)
    i = int(np.argmin(sse))
    return dict(s=float(g[i]), at_grid_edge=bool(i in (0, len(g) - 1)), sse=float(sse[i]),
                classified_by_primary_cuts=classify(float(g[i]), 1.0))


_PERMS = None


def corr_perm(x, y):
    """Pearson r and its exact two-sided permutation p over 9! (descriptive)."""
    global _PERMS
    import itertools
    if _PERMS is None:
        _PERMS = np.array(list(itertools.permutations(range(9))))
    x = np.asarray(x) - np.mean(x); y = np.asarray(y) - np.mean(y)
    d = math.sqrt((x @ x) * (y @ y)); r = (x @ y) / d
    st = (y[_PERMS] @ x) / d
    return dict(r=float(r), p_exact_two_sided=float(np.mean(np.abs(st) >= abs(r) - 1e-12)))


def rho18(R):
    x = np.array([C2[d] for d in H2]); y = np.array([R[d] for d in H2])
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    r = float(np.corrcoef(rx, ry)[0, 1])
    rng = np.random.default_rng(SEED_RHO18)
    perm = np.array([np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(200_000)])
    return dict(rho=r, p_perm_one_sided=float((perm >= r).mean()))


def main(mode, pins_path, out, X=XSTAR):
    T0 = time.time()
    assert mode in ("refs", "dry", "read")
    X = int(float(X))
    assert mode != "read" or X == XSTAR, "the read runs at X* only"
    assert os.path.ismount("/mnt/data"), "mount guard"
    pins = json.load(open(pins_path))
    timing = {}
    t = time.time(); ref = refs(pins, X); timing["refs"] = time.time() - t
    res = dict(mode=mode, X_star=XSTAR, X=X, K_P=KP, h1_refs=ref, pins_sha256=sha_file(pins_path))
    if mode == "refs":
        res["label"] = "FN1-h2 pre-seal D2 (b): the nine h = 1 references at X* and K_P (seen data; no h = 2 data)"
        json.dump(res, open(out, "w"), indent=1, sort_keys=True)
        json.dump(timing, open(out + ".timing", "w"))
        print("done")
        return 0
    rp, rs = pins["refs"]["path"], pins["refs"]["sha256"]
    assert sha_file(rp) == rs, ("refs pin", rp)
    committed = json.load(open(rp))["h1_refs"]
    assert committed == ref, "recomputed h = 1 references differ from the committed D2 (b) file"
    pp, ps = pins["pred"]["path"], pins["pred"]["sha256"]
    assert sha_file(pp) == ps, ("pred pin", pp)
    pred = json.load(open(pp))
    h2pins = pins["dry" if mode == "dry" else "h2"]
    Rh2, n2, drift = {}, {}, {}
    t = time.time()
    for d in H2:
        a = h2pins[d]
        th, half, n = load(a["dir"], d, a["manifest_sha256"], X=X, keep_half=True)
        Rh2[d] = Rs(th); n2[d] = n
        del th
        drift[d] = F2.seg_noise(half, n, KP["0.55"], 0.55)
        del half
    timing["h2"] = time.time() - t
    res["h2"] = {d: dict(n=n2[d], N=2 * n2[d], R=Rh2[d], C=C2[d], primary=d in PRIMARY) for d in H2}
    res["h2_drift_beta055"] = drift
    tests = {}
    for b in BETAS:
        Rref = {f: ref[f]["R"][b] for f in H1}
        a0, b0 = line(Rref, C1, H1)
        R2 = {d: Rh2[d][b] for d in H2}
        sj = {d: (R2[d] - a0 - b0 * C2[d]) / b0 for d in H2}
        s = float(np.mean([sj[d] for d in PRIMARY]))
        o = dict(line=[float(a0), float(b0)], s=s, s_j=sj, s_all18=float(np.mean(list(sj.values()))),
                 s_descriptive9=float(np.mean([sj[d] for d in H2 if d not in PRIMARY])))
        if b == "0.55":
            o["verdict"] = classify(s, b0)
            q = quad(Rref, C1, H1)
            o["K0_quadratic"] = [float(v) for v in q]
            o["K0"] = k0_test(R2, q)
            o["s_quadratic_reference"] = s_quad(R2, q)
            o["rho18"] = rho18(R2)
        tests[b] = o
    res["tests"] = tests
    cp_, cs_ = pins["controls"]["path"], pins["controls"]["sha256"]
    assert sha_file(cp_) == cs_, ("controls pin", cp_)
    ctl = json.load(open(cp_))["h2"]
    sj = tests["0.55"]["s_j"]
    res["controls"] = {key: dict(primary9=corr_perm([sj[d] for d in PRIMARY], [ctl[d][key] for d in PRIMARY]),
                                 all18_pearson=float(np.corrcoef([sj[d] for d in H2], [ctl[d][key] for d in H2])[0, 1]))
                       for key in ("LpL1", "chen_Lterm")}
    res["primary"] = dict(beta=0.55, s=tests["0.55"]["s"], verdict=tests["0.55"]["verdict"], cuts=[CUT_C, CUT_L],
                          s_quadratic_reference_descriptive=tests["0.55"]["s_quadratic_reference"])
    # descriptive: χ′ control and matched-N reference
    t = time.time()
    nbar = int(round(np.mean([n2[d] for d in PRIMARY])))
    chi, mN = {}, {}
    for f in H1:
        a = pins["archives"][f]
        th, _, n = load(a["dir"], f, a["manifest_sha256"], X=X, chi5=True)
        Rt = Rs(th); del th
        chi[f] = dict(n=n, R=Rt, dR={b: Rt[b] - ref[f]["R"][b] for b in BETAS},
                      pred_dR_runs_in_X={b: pred["h1"][b][f]["dR_runs_in_X"] for b in BETAS},
                      pred_dR_runs_in_N={b: pred["h1"][b][f]["dR_runs_in_N"] for b in BETAS})
        th, _, n = load(a["dir"], f, a["manifest_sha256"], X=X, nmax=nbar)
        mN[f] = dict(n=n, R=Rs(th)); del th
    timing["controls"] = time.time() - t
    res["chi5_control"] = chi
    a0, b0 = line({f: mN[f]["R"]["0.55"] for f in H1}, C1, H1)
    res["matched_N"] = dict(n_bar=nbar, refs=mN, line=[float(a0), float(b0)],
                            s=float(np.mean([(Rh2[d]["0.55"] - a0 - b0 * C2[d]) / b0 for d in PRIMARY])))
    res["label"] = f"FN1-h2 {mode}"
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    timing["total_wall"] = time.time() - T0
    timing["cpu_s"] = time.process_time()
    json.dump(timing, open(out + ".timing", "w"))
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
