"""Round 72 (descriptive / exploratory): the CUE scatter control (CUE_SCATTER_CONTROL.md) and the pair-connected
approximation's validation against the long CUE baseline (PAIR_APPROX.md). Spot, CPU.

  python round72.py ctrl R OUT_DIR          sequence R as one 10⁵ segment: μ̂ and own-bootstrap SEs (same seeds as
                                            l6_base.stats; SEs checked bitwise against results/base/stats)
  python round72.py ctrl_cat J OUT_DIR      10⁶ segment J = sequences 10J..10J+9 concatenated (seams every 10⁵)
  python round72.py ctrl_summary OUT_DIR    → OUT_DIR/CTRL_SUMMARY.json
  python round72.py resp R OUT_DIR          response k = dμ̂/dδ per (test, file) on sequence R, δ = 1e-3 and 2e-3
  python round72.py pair_summary OUT_DIR    → OUT_DIR/PAIR_SUMMARY.json
"""
import glob
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l6_base as B  # noqa: E402

GEN = os.path.join(HERE, "results", "base", "gen")
STATS = os.path.join(HERE, "results", "base", "stats")
GS = ("300", "1000", "3000", "10000")
DELTAS = (1e-3, 2e-3)
CAT_SEED = 72                                   # kind seed for the 10⁶ segments (new values; R = J)


def _files(S):
    RA, FR, BR = S[0], S[1], S[2]
    return (("route_a", list(RA.F3)), ("A", list(FR.FILES["A"])), ("B2", list(BR.FILES)))


def _run(x_or_X, kind_seed, r, S, concat):
    """l6_base._stats_one's loop, also keeping μ̂ (identical calls and seeds)."""
    RA, FR, BR, E, BP, fits, models, pb = S
    if concat:
        X = x_or_X
        sp = np.concatenate([np.diff(x) for x in X])
    else:
        x = x_or_X
        sp = np.diff(x)
    out = {}
    for ti, (test, files) in enumerate(_files(S)):
        out[test] = {}
        for fi, f in enumerate(files):
            rng = np.random.default_rng([20261020, 66, ti, fi, kind_seed, r])
            if test == "route_a":
                res = RA.fit_file(fits[f], sp, rng, RA.BLOCK_LENS, gof=False)
                se, n, mu = {str(k): v for k, v in res["se"].items()}, res["n"], res["mu"]
            elif test == "A":
                res = FR.fit_file_A(models[f], FR.seq_A(sp), rng)
                se, n, mu = res.get("se"), res["n"], res.get("mu")
            else:
                L = BP.L_star()
                if concat:
                    a = E.Acc(L, X.shape[0] * X.shape[1], E.SEGS)
                    a.add_block(X, float(X.shape[1]), np.arange(X.shape[0]) * float(X.shape[1]))
                    raw = a.result(rng, BR.B_BOOT)
                    n = int(X.size)
                else:
                    raw = E.zeros_stats(x, L, rng, n_boot=BR.B_BOOT)
                    n = int(len(x))
                fr = BR.fit(pb["files"][f], raw)
                se, mu = {str(k): v for k, v in fr["se"].items()}, fr["mu"]
            out[test][f] = dict(mu=mu, se=se, n=int(n))
    return out


def ctrl(r, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    S = B._setup()
    x = np.load(os.path.join(GEN, f"cue_{r:03d}.npy"))
    t = time.time()
    res = _run(x, B.KIND_SEED["cue"], r, S, False)
    old = json.load(open(os.path.join(STATS, f"stats_cue_{r:03d}.json")))["stats"]
    same = all(res[t_][f]["se"] == old[t_][f]["se"] and res[t_][f]["n"] == old[t_][f]["n"] for t_ in res for f in res[t_])
    rec = dict(r=r, segment="1e5", se_equal_stored=bool(same), stats=res, wall_s=round(time.time() - t, 1), env=B.env())
    json.dump(rec, open(os.path.join(out_dir, f"ctrl_{r:03d}.json"), "w"), indent=1)
    print(r, "se_equal_stored", same, rec["wall_s"], flush=True)
    return 0 if same else 1


def ctrl_cat(j, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    S = B._setup()
    X = np.stack([np.load(os.path.join(GEN, f"cue_{r:03d}.npy")) for r in range(10 * j, 10 * j + 10)])
    t = time.time()
    res = _run(X, CAT_SEED, j, S, True)
    rec = dict(j=j, segment="1e6", sequences=list(range(10 * j, 10 * j + 10)), stats=res,
               wall_s=round(time.time() - t, 1), env=B.env())
    json.dump(rec, open(os.path.join(out_dir, f"ctrlcat_{j}.json"), "w"), indent=1)
    print(j, rec["wall_s"], flush=True)
    return 0


def _chi2(mu, se):
    from scipy.stats import chi2
    mu, se = np.asarray(mu, float), np.asarray(se, float)
    w = 1 / se ** 2
    m = float(np.sum(w * mu) / np.sum(w))
    x = float(np.sum((mu - m) ** 2 / se ** 2))
    dof = len(mu) - 1
    return dict(chi2=x, dof=dof, chi2_per_dof=x / dof, percentile=float(100 * chi2.cdf(x, dof)), weighted_mean=m)


def ctrl_summary(out_dir):
    from scipy.stats import chi2
    A = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(out_dir, "ctrl_[0-9]*.json")))]
    C = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(out_dir, "ctrlcat_*.json")))]
    cals = {"route_a": "results/calib/route_a_calib_declared.json", "A": "results/calib/followup_calib_A_declared.json",
            "B2": "results/calib/b2_calib_declared.json"}
    lo, hi = chi2.ppf(0.025, 49) / 49, chi2.ppf(0.975, 49) / 49
    res = dict(n_seg_1e5=len(A), n_seg_1e6=len(C), all_se_equal_stored=all(a["se_equal_stored"] for a in A),
               band_49=[lo, hi], tests={})
    for test in B.TESTS:
        cal = json.load(open(os.path.join(B.CS4, cals[test])))["files"]
        files = list(A[0]["stats"][test])
        rows = {}
        for f in files:
            row = {}
            for name, recs in (("seg_1e5", A), ("seg_1e6", C)):
                ok = [a for a in recs if a["stats"][test][f]["mu"] is not None and a["stats"][test][f]["se"]]
                row[name] = {G: _chi2([a["stats"][test][f]["mu"] for a in ok], [a["stats"][test][f]["se"][G] for a in ok])
                             for G in GS}
                row[name + "_n"] = len(ok)
            sb = cal[f]["se_boot_mean"]["300"]
            row["file_size_cal"] = dict(sd=cal[f]["sd"], se_boot_mean_300=sb, proxy_chi2_per_dof=(cal[f]["sd"] / sb) ** 2,
                                        R=cal[f]["R"])
            rows[f] = row
        med = float(np.median([rows[f]["seg_1e5"]["300"]["chi2_per_dof"] for f in files]))
        reading = "approx 1" if lo <= med <= hi else ("low: stop and diagnose" if med < lo else "high")
        res["tests"][test] = dict(files=rows, median_chi2_per_dof_1e5_G300=med, reading=reading)
    res["label"] = "round 72; DESCRIPTIVE (CUE_SCATTER_CONTROL.md)"
    json.dump(res, open(os.path.join(out_dir, "CTRL_SUMMARY.json"), "w"), indent=1)
    for test, v in res["tests"].items():
        print(test, "median chi2/dof (1e5, G=300):", round(v["median_chi2_per_dof_1e5_G300"], 3), v["reading"])
        for f, r in v["files"].items():
            print("  ", f[:18], " ".join(f"1e5 G{G} {r['seg_1e5'][G]['chi2_per_dof']:.2f} ({r['seg_1e5'][G]['percentile']:.0f})"
                                         for G in GS),
                  "| 1e6 G300", f"{r['seg_1e6']['300']['chi2_per_dof']:.2f} ({r['seg_1e6']['300']['percentile']:.0f})",
                  "| file-size cal proxy", f"{r['file_size_cal']['proxy_chi2_per_dof']:.2f}")
    print("all SEs equal stored:", res["all_se_equal_stored"])
    return 0


def _mu_only(test, f, sp, x, S):
    RA, FR, BR, E, BP, fits, models, pb = S
    rng = np.random.default_rng(0)
    if test == "route_a":
        return RA.fit_file(fits[f], sp, rng, (), gof=False)["mu"]
    if test == "A":
        return FR.fit_file_A(models[f], FR.seq_A(sp), rng, block_lens=())["mu"]
    raw = E.zeros_stats(x, BP.L_star(), rng, n_boot=2)
    t = pb["files"][f]
    return (raw["k3bar"] - t["kappa3_sine"]) / t["dkappa3"]


def resp(r, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    S = B._setup()
    x = np.load(os.path.join(GEN, f"cue_{r:03d}.npy"))
    t = time.time()
    out = {}
    for test, files in _files(S):
        out[test] = {}
        for f in files:
            row = {}
            for d in DELTAS:
                mp_ = _mu_only(test, f, np.diff(x) / (1 + d), x / (1 + d), S)
                mm = _mu_only(test, f, np.diff(x) / (1 - d), x / (1 - d), S)
                row[str(d)] = None if mp_ is None or mm is None else (mp_ - mm) / (2 * d)
            out[test][f] = row
    rec = dict(r=r, k=out, deltas=DELTAS, wall_s=round(time.time() - t, 1), env=B.env())
    json.dump(rec, open(os.path.join(out_dir, f"resp_{r:03d}.json"), "w"), indent=1)
    print(r, rec["wall_s"], flush=True)
    return 0


def pair_summary(out_dir):
    Rr = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(out_dir, "resp_*.json")))]
    cue = B._load(STATS, "cue")
    s2 = {G: B.sigma2_exact(float(G)) for G in GS}
    res = dict(sigma2_cue=s2, n_resp=len(Rr), tests={})
    for test in B.TESTS:
        V = B._var_table(cue, test)
        res["tests"][test] = {}
        valid = True
        informative = False
        for f in V:
            ks = {d: np.array([r["k"][test][f][str(d)] for r in Rr if r["k"][test][f][str(d)] is not None]) for d in DELTAS}
            k = ks[DELTAS[1]]
            km, kse = float(k.mean()), float(k.std(ddof=1) / math.sqrt(len(k)))
            k2 = km ** 2
            k2_se = 2 * abs(km) * kse
            W = {G: V[f][G] for G in GS}
            Wm = {G: float(W[G].mean()) for G in GS}
            Wse = {G: float(W[G].std(ddof=1) / math.sqrt(len(W[G]))) for G in GS}
            dmeas = W["300"] - W["10000"]
            dm, dse = float(dmeas.mean()), float(dmeas.std(ddof=1) / math.sqrt(len(dmeas)))
            g = s2["300"] / 300 - s2["10000"] / 10000
            dp, dpse = k2 * g, k2_se * g
            zf = (dm - dp) / math.sqrt(dse ** 2 + dpse ** 2)
            x = np.array([s2[G] / float(G) for G in GS])
            y = np.array([Wm[G] for G in GS])
            w = 1 / np.array([Wse[G] for G in GS]) ** 2
            A = float(np.sum(w * (y - k2 * x)) / np.sum(w))
            pred = A + k2 * x
            zres = ((y - pred) / np.array([Wse[G] for G in GS])).tolist()
            ok = abs(zf) <= 3 and all(abs(z) <= 3 for z in zres)
            inf = dp >= 2 * dse
            valid &= ok
            informative |= inf
            res["tests"][test][f] = dict(
                k=km, k_se=kse, k_delta_1e3=float(ks[DELTAS[0]].mean()), k_linearity=float(ks[DELTAS[0]].mean() / km),
                W_mean=Wm, W_se=Wse, fall_measured=[dm, dse], fall_predicted=[dp, dpse], z_fall=zf,
                A=A, W_pred=dict(zip(GS, pred.tolist())), z_resid=dict(zip(GS, zres)),
                pair_share_300=k2 * s2["300"] / 300 / Wm["300"], informative=bool(inf), ok=bool(ok))
        res["tests"][test]["_reading"] = ("validates" if valid and informative else
                                          "uninformative (predicted fall below 2 SE of the measured fall in every file)"
                                          if valid else "does not validate")
    res["label"] = "round 72; EXPLORATORY (PAIR_APPROX.md); CUE only, not applied to zeta"
    json.dump(res, open(os.path.join(out_dir, "PAIR_SUMMARY.json"), "w"), indent=1)
    for test in B.TESTS:
        t = res["tests"][test]
        print(test, t["_reading"])
        for f, v in t.items():
            if f.startswith("_"):
                continue
            print("  ", f[:18], f"k {v['k']:+.4g}±{v['k_se']:.2g} (lin {v['k_linearity']:.3f})",
                  f"fall meas {v['fall_measured'][0]:.3g}±{v['fall_measured'][1]:.2g} pred {v['fall_predicted'][0]:.3g}"
                  f"±{v['fall_predicted'][1]:.2g} z {v['z_fall']:+.2f}",
                  "resid z", [round(z, 2) for z in v["z_resid"].values()], f"pair share {v['pair_share_300']:.3f}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "ctrl":
        sys.exit(ctrl(int(sys.argv[2]), sys.argv[3]))
    if cmd == "ctrl_cat":
        sys.exit(ctrl_cat(int(sys.argv[2]), sys.argv[3]))
    if cmd == "ctrl_summary":
        sys.exit(ctrl_summary(sys.argv[2]))
    if cmd == "resp":
        sys.exit(resp(int(sys.argv[2]), sys.argv[3]))
    if cmd == "pair_summary":
        sys.exit(pair_summary(sys.argv[2]))
    raise SystemExit(f"unknown command {cmd}")
