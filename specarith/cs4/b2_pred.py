"""Corrected (B): the data-free prediction at F6 (CORRECTED_B_DESIGN.md §3; rounds 57–58). L = L* from the committed
L rule (results/b2_rule.json; fails closed without it). Nothing is downloaded: heights come from the declared ranges
(../ph2r2/FRESH_SET_F6.md).

Per F6 file, at its zero-weighted mean height: κ₃^sine(L*) and Δκ₃(L*) = 3ΔF₂ + ΔF₃ (followup_k3.terms; FastZeta),
with route (a)'s checks as relative changes of Δκ₃ (μ units, since μ̂ = (k̄₃ − κ₃^sine)/Δκ₃):
  - prime cutoff 3·10⁵ → 10⁶;  - quadrature, triangle order 48 → 32;
  - file average: Simpson over (t0, mean, t1) at the lowest file, scaled to the others by Var ℓ (as route (a)).
δμ_sys = the w_f-pooled sum of those contributions. TAGGABLE iff Δκ₃ ≠ 0 at every file.

  python b2_pred.py run CHUNK NCHUNKS OUT_DIR     (spot)
  python b2_pred.py merge OUT_DIR                 → results/b2_pred.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import followup_pred as P  # noqa: E402
import route_a_zeta as RZ  # noqa: E402

F6 = {"zeros_46646000.dat": (46_646_000, 48_746_000),
      "zeros_256646000.dat": (256_646_000, 258_746_000),
      "zeros_2365046000.dat": (2_365_046_000, 2_367_146_000),
      "zeros_10630646000.dat": (10_630_646_000, 10_632_746_000)}
M_B = (32, 48)
PM, PM_HI = RZ.PMAX_MAIN, RZ.PMAX_CHECK


def L_star():
    p = os.path.join(HERE, "results", "b2_rule.json")
    if not os.path.exists(p):
        raise SystemExit("REFUSED: no results/b2_rule.json (the L rule has not been applied)")
    return float(json.load(open(p))["L_star"])


def jobs(L):
    J = []
    for f in F6:
        for pm in (PM, PM_HI):
            for m in M_B:
                J.append((f, "mean", pm, m, L))
        if f == P.lowest(F6):
            J += [(f, "t0", PM, M_B[1], L), (f, "t1", PM, M_B[1], L)]
    return J


def run_one(job):
    import cs4fast as Fz
    import followup_k3 as K
    f, which, pm, m, L = job
    t = P.height(F6, f, which)
    Z = Fz.FastZeta(t, pmax=pm)
    return dict(file=f, which=which, pmax=pm, m=m, L=L, t=t, **K.terms(Z, L, m))


def key(r):
    return (r["file"], r["which"], r["pmax"], r["m"], r["L"])


def run(chunk, nchunks, out_dir):
    L = L_star()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"b2pred_c{chunk:02d}.jsonl")
    done = {key(r) for r in map(json.loads, open(path))} if os.path.exists(path) else set()
    for i, j in enumerate(jobs(L)):
        if i % nchunks != chunk or j in done:
            continue
        r = run_one(j)
        with open(path, "a") as fh:
            fh.write(json.dumps(r) + "\n")
        print(json.dumps(r), flush=True)


def merge(out_dir):
    L = L_star()
    rows = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("b2pred_c") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows.setdefault(key(r), r)
    missing = set(jobs(L)) - set(rows)
    if missing:
        raise SystemExit(f"merge: {len(missing)} jobs missing")
    w, nf = P.counts(F6)
    g = lambda f, which, pm, m: rows[(f, which, pm, m, L)]                                    # noqa: E731
    dk = lambda r: 3 * r["dF2"] + r["dF3"]                                                    # noqa: E731
    f0 = P.lowest(F6)
    r0 = g(f0, "mean", PM, M_B[1])
    fav = abs((dk(g(f0, "t0", PM, M_B[1])) + 4 * dk(r0) + dk(g(f0, "t1", PM, M_B[1]))) / 6 - dk(r0)) / abs(dk(r0))
    v0 = P.var_ell(*F6[f0])
    res = dict(observable="corrected (B): offset-averaged k3 of the count", L=L, NU=32, pmax=PM, pmax_check=PM_HI,
               m_tri=M_B, weights=w, n_f=nf, files={})
    for f in F6:
        r = g(f, "mean", PM, M_B[1])
        d = dk(r)
        dmu = dict(cutoff=abs(dk(g(f, "mean", PM_HI, M_B[1])) - d) / abs(d),
                   quad=abs(dk(g(f, "mean", PM, M_B[0])) - d) / abs(d), file_average=fav * P.var_ell(*F6[f]) / v0)
        res["files"][f] = dict(t_mean=P.height(F6, f), ell_mean=RZ.ell_of(P.height(F6, f)), dF2=r["dF2"],
                               dF3=r["dF3"], dkappa3=d, kappa3_sine=L + 3 * r["F2_sine"] + r["F3_sine"], dmu=dmu)
        print(f"{f}: ℓ̄ {res['files'][f]['ell_mean']:.4f}  Δκ₃ {d:+.4e}  κ₃^sine {res['files'][f]['kappa3_sine']:.6f}  δμ "
              + ", ".join(f"{k} {v:.1e}" for k, v in dmu.items()), flush=True)
    res["delta_mu_sys"] = float(sum(w[f] * sum(res["files"][f]["dmu"].values()) for f in F6))
    res["TAGGABLE"] = bool(all(abs(v["dkappa3"]) > 0 for v in res["files"].values()))
    json.dump(res, open(os.path.join(HERE, "results", "b2_pred.json"), "w"), indent=1)
    print(f"δμ_sys {res['delta_mu_sys']:.2e}; TAGGABLE {res['TAGGABLE']}", flush=True)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif sys.argv[1] == "merge":
        sys.exit(merge(sys.argv[2]))
