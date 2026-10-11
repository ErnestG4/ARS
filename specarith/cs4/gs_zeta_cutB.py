"""Prime-cutoff convergence of the estimator-B prediction (twenty-fifth round, Will): the lag term Cov(3b)/b at b = 10⁴
is the sealed quantity's one unchecked piece. Amendment 4's diagnostic (`diag_pmax.py`) covered lag 0 at b ≤ 300 only,
and its cutoff sensitivity grew with b at low cutoffs (0.64% at b = 100, 0.75% at b = 300).

One height (ℓ = 15.7502, the lowest F2 file), every node pair, prime cutoff 10⁶, on the production lattice
r = 5 + 0.5k out to the estimator-B grid end (the stored long grid plus `gs_zeta_ext.py`), and the short grid. The
comparison is against the stored cutoff-3·10⁵ values (`gs_zeta.py` pairs + `gs_zeta_ext.py` ext), assembled exactly as
`gs_zeta_B.py` does. The stored values reproduce across a re-initialised evaluator to ≤ 3e-8 per pair (§6.2's overlap),
so a fresh 3·10⁵ run is not repeated.

Changed with the cutoff: c_short (short-range I₄), c_non (long-range I₄ and Cov), and I₂. Held at 3·10⁵: I₃ (mpmath ρ₃,
changes < 1e-4 over the whole ladder; it enters v(100) and v(10⁴) almost equally).

  python gs_zeta_cutB.py pairs PMAX CHUNK NCHUNKS OUT   -> OUT/P{PMAX}/p{i}_{j}.npz
  python gs_zeta_cutB.py summary PMAX OUT RESULTS_DIR   -> OUT/cutB_summary.json  (RESULTS_DIR = results/gs_zeta)
"""
import json
import math
import os
import sys
import time

import numpy as np

import gs_unitary as G
import gs_zeta as Z
import gs_zeta_B as B
import gs_zeta_ext as E

ELL = "15.7502"


def full_grid():
    n = int(round((E.ext_grid()[-1] - Z.R_LO) / Z.DR_L)) + 1
    n += n % 2
    return Z.R_LO + Z.DR_L * np.arange(n)


def pairs(pmax, chunk, nchunks, out):
    import cs4lr as LR
    lr = LR.LongRangeZeta(Z.tval(float(ELL)), pmax=pmax)
    rs, r = Z.short_grid(), full_grid()
    d = os.path.join(out, f"P{pmax}")
    os.makedirs(d, exist_ok=True)
    for k, (i, j) in enumerate(Z.PAIRS):
        if k % nchunks != chunk:
            continue
        fn = os.path.join(d, f"p{i:02d}_{j:02d}.npz")
        if os.path.exists(fn):
            continue
        t0 = time.time()
        o, n = lr.connected(Z.DN[i], Z.DN[j], rs)
        full = o + n
        tail_s = max(lr.diag.values())
        _, nl = lr.connected(Z.DN[i], Z.DN[j], r, nonosc_only=True)
        tail_l = max(lr.diag.values())
        np.savez(fn, c_short=full.real, c_non=nl.real, imag_max=max(np.abs(full.imag).max(), np.abs(nl.imag).max()),
                 tail=max(tail_s, tail_l), secs=time.time() - t0)
        print(ELL, i, j, "%.0fs" % (time.time() - t0), flush=True)


def assemble_new(out, pmax):
    rs, r = Z.short_grid(), full_grid()
    cs_, cl_ = G.chi(rs), 1 - G.chi(r)
    Cs, Cl = np.zeros(len(rs)), np.zeros(len(r))
    imag, tail = 0.0, 0.0
    for (i, j) in Z.PAIRS:
        z = np.load(os.path.join(out, f"P{pmax}", f"p{i:02d}_{j:02d}.npz"))
        wgt = 4 * Z.DW[i] * Z.FD[i] * Z.DW[j] * Z.FD[j] * (1 if i == j else 2)
        Cs += wgt * cs_ * z["c_short"]
        Cl += wgt * cl_ * z["c_non"]
        imag, tail = max(imag, float(z["imag_max"])), max(tail, float(z["tail"]))
    return rs, Cs, r, Cl, imag, tail


def summary(pmax, out, rd):
    import cs4fast as F
    res = json.load(open(os.path.join(rd, f"gs_zeta_L{ELL}.json")))
    rs, Cs0, r0, Cl0, _ = B.assemble(rd, ELL)
    rs1, Cs1, r1, Cl1, imag, tail = assemble_new(out, pmax)
    assert len(r0) == len(r1) and np.allclose(r0, r1), "grids differ"
    fz = F.FastZeta(Z.tval(float(ELL)), pmax=pmax)
    I2_1 = 2 * float(np.sum(Z.DW * Z.FD ** 2 * np.array([fz.R2(x).real for x in Z.DN])))
    rows = {}
    for b in Z.LADDER:
        I3 = res["I3"][str(b)]
        c0 = {P: B.cov_over_b(rs, Cs, rr, Cl, b, 0.0) for P, (Cs, rr, Cl) in (("old", (Cs0, r0, Cl0)), ("new", (Cs1, r1, Cl1)))}
        c1 = {P: B.cov_over_b(rs, Cs, rr, Cl, b, 3.0 * b) for P, (Cs, rr, Cl) in (("old", (Cs0, r0, Cl0)), ("new", (Cs1, r1, Cl1)))}
        v_old = math.sqrt(2) * res["I2"] + 2 * math.sqrt(2) * I3 + c0["old"]
        v_new = math.sqrt(2) * I2_1 + 2 * math.sqrt(2) * I3 + c0["new"]
        rows[b] = dict(v_old=v_old, v_stored=res["v"][str(b)], v_new=v_new, cov1_old=c1["old"], cov1_new=c1["new"],
                       vB_old=v_old - c1["old"], vB_new=v_new - c1["new"],
                       d_cov1_over_vB=(c1["new"] - c1["old"]) / (v_old - c1["old"]),
                       d_v_over_v=(v_new - v_old) / v_old,
                       d_vB_over_vB=((v_new - c1["new"]) - (v_old - c1["old"])) / (v_old - c1["old"]))
    gB = {P: math.sqrt(rows[10_000][f"vB_{P}"] / rows[100][f"vB_{P}"]) for P in ("old", "new")}
    s = dict(ell=ELL, pmax_old=res["pmax"], pmax_new=pmax, I2_old=res["I2"], I2_new=I2_1, rungs=rows,
             g_B_old=gB["old"], g_B_new=gB["new"], d_g_B=gB["new"] - gB["old"], new_imag_max=imag, new_fourier_tail=tail,
             recheck_v_old_vs_stored=max(abs(x["v_old"] - x["v_stored"]) for x in rows.values()))
    for b, x in rows.items():
        print("b=%5d  Cov(3b)/b %+.6e -> %+.6e (Δ/v_B %+.1e) | v %.6f -> %.6f (Δ/v %+.1e) | v_B Δ/v_B %+.1e"
              % (b, x["cov1_old"], x["cov1_new"], x["d_cov1_over_vB"], x["v_old"], x["v_new"], x["d_v_over_v"],
                 x["d_vB_over_vB"]))
    print("g_B %.6f -> %.6f (Δ %+.1e) | I2 %.8f -> %.8f | recheck v_old vs stored ≤ %.0e | new |Im| %.1e tail %.1e"
          % (gB["old"], gB["new"], s["d_g_B"], res["I2"], I2_1, s["recheck_v_old_vs_stored"], imag, tail))
    json.dump(s, open(os.path.join(out, "cutB_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "pairs":
        pairs(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        assert sys.argv[1] == "summary"
        summary(int(sys.argv[2]), sys.argv[3], sys.argv[4])
