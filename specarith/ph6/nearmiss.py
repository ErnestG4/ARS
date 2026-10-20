"""Phase 6 near-miss check (NEARMISS_RULE.md, round 67): the fixed-point hit rule. POST HOC, DESCRIPTIVE; no verdict.

  python nearmiss.py one ID OUT_DIR      ID in C1a C1b C2 C4 zeros gue  → OUT_DIR/nearmiss_ID.json
  python nearmiss.py summary OUT_DIR     → OUT_DIR/NEARMISS_SUMMARY.json, .md
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ph6lib as L  # noqa: E402

CANDS = ("C1a", "C1b", "C2", "C4")
B_W = 10                      # band half-width in resolution widths
STEP_W = 0.2                  # 6.0 fine grid step, in resolution widths
EXCL_W = 1.0                  # exclusion half-width around every log n, n = 2..90
Q = 99.0
N_FAKE = 200
FLAG_PCT = 95.0


def spectrum(sid):
    if sid in CANDS:
        meta = json.load(open(os.path.join(HERE, "results", "candidates", f"{sid}_res2.json")))
        p = os.path.join(HERE, "results", "candidates", f"{sid}_res2.npy")
        if hashlib.sha256(open(p, "rb").read()).hexdigest() != meta["sha256"]:
            raise SystemExit(f"REFUSED: {p} sha256 differs from its committed json")
        t = np.sort(np.load(p))
        top = float(t.max())
        read = json.load(open(os.path.join(HERE, "results", "read61", f"{sid}.json")))["T3"]["config"]
        if abs(top - read["E_hi"]) > 1e-3:
            raise SystemExit(f"REFUSED: {sid} top {top} differs from the read's E_hi {read['E_hi']}")
        return t, top, dict(source=p, sha256=meta["sha256"])
    import tests61 as T
    T.ZEROS6 = os.environ.get("ZEROS6", T.ZEROS6)          # spot copy; zeros_in still checks its sha256
    z = T.zeros_in(0, 1e9)[:30_000]
    top = float(z[-1])
    if sid == "zeros":
        return z, top, dict(source=T.ZEROS6, first=30_000)
    if sid == "gue":
        import preread as PR
        cfg = L.rule_config(0.0, top)
        seed = PR.CALIB_SEEDS["gue"] + 150
        lev = L.null_levels("gue", L.nbar_zeta, cfg.E_hi, np.random.default_rng(seed))
        return np.sort(lev[lev <= cfg.E_hi]), top, dict(source="ph6lib.null_levels gue", seed=seed)
    raise SystemExit(f"unknown spectrum {sid}")


def r_of(cfg, lev, taus):
    S, M = L.zero_sums(cfg, lev, taus, exact=True)
    sm = L.rhs_dirichlet(cfg, taus, 1, None, 0)["smooth"]
    return (S + M - sm) / cfg.norm


def fake_sets(non_pp, k):
    return [np.sort(np.random.default_rng([20261020, 67, j]).choice(non_pp, size=k, replace=False)) for j in range(N_FAKE)]


def one(sid, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    t, top, src = spectrum(sid)
    cfg = L.rule_config(0.0, top)
    lev = t[t <= top]
    w = 1.0 / cfg.sigma
    ns = L.LINE_NS
    pp = L.is_prime_power(ns)
    logs = np.log(ns.astype(float))
    ks = np.arange(-int(round(B_W / STEP_W)), int(round(B_W / STEP_W)) + 1)
    band_taus = logs[:, None] + ks[None, :] * STEP_W * w                           # (89, 101)
    near = np.min(np.abs(band_taus[:, :, None] - logs[None, None, :]), axis=2) <= EXCL_W * w + 1e-15
    taus = np.concatenate([logs, band_taus.ravel()])
    r = r_of(cfg, lev, taus)
    r0 = r[:len(ns)]
    rb = np.abs(r[len(ns):]).reshape(band_taus.shape)
    thr = np.array([np.percentile(rb[i][~near[i]], Q) for i in range(len(ns))])
    n_band = (~near).sum(axis=1)
    hit = np.abs(r0) > thr
    lam = L.mangoldt_upto(90)[ns]
    true_rate = float(hit[pp].mean())
    non_pp = np.where(~pp)[0]
    fr = np.array([hit[s].mean() for s in fake_sets(non_pp, int(pp.sum()))])
    pct = 100.0 * (np.sum(fr < true_rate) + 0.5 * np.sum(fr == true_rate)) / N_FAKE
    x = (lam / np.sqrt(ns))[pp]
    y = np.real(r0)[pp]
    from scipy.stats import pearsonr, spearmanr
    hp = hit[pp]
    res = dict(id=sid, source=src, config=dict(T0=cfg.T0, sigma=cfg.sigma, E_hi=cfg.E_hi), n_levels=int(len(lev)),
               resolution_width=w, band_points_used=dict(min=int(n_band.min()), max=int(n_band.max())),
               true_rate=true_rate, n_hits_true=int(hit[pp].sum()), n_true=int(pp.sum()),
               fake_rate=dict(mean=float(fr.mean()), q05=float(np.quantile(fr, 0.05)), q95=float(np.quantile(fr, 0.95)),
                              n_below=int(np.sum(fr < true_rate)), n_at_or_below=int(np.sum(fr <= true_rate))),
               percentile=float(pct), flag_followup=bool(pct > FLAG_PCT),
               corr_all=dict(pearson=float(pearsonr(x, y)[0]), spearman=float(spearmanr(x, y)[0]), n=int(len(x))),
               corr_hits=(dict(pearson=float(pearsonr(x[hp], y[hp])[0]), spearman=float(spearmanr(x[hp], y[hp])[0]),
                               n=int(hp.sum())) if hp.sum() >= 3 else dict(n=int(hp.sum()))),
               per_n=[dict(n=int(n), prime_power=bool(q), hit=bool(h), abs_r=float(abs(a)), re_r=float(np.real(a)),
                           threshold=float(th)) for n, q, h, a, th in zip(ns, pp, hit, r0, thr)],
               label="POST HOC, DESCRIPTIVE (NEARMISS_RULE.md); a percentile > 95 is flagged for a pre-registered "
                     "follow-up, not reported as a finding")
    json.dump(res, open(os.path.join(out_dir, f"nearmiss_{sid}.json"), "w"), indent=1)
    print(sid, f"true {res['n_hits_true']}/{res['n_true']}  fake mean {fr.mean():.3f}  pct {pct:.1f}  "
          f"r(Re r, Λ/√n) {res['corr_all']['pearson']:+.3f}", flush=True)
    return 0


def summary(out_dir):
    rows = [json.load(open(os.path.join(out_dir, f"nearmiss_{s}.json"))) for s in CANDS + ("zeros", "gue")
            if os.path.exists(os.path.join(out_dir, f"nearmiss_{s}.json"))]
    md = ["| spectrum | hits (true) | fake mean [5–95%] | percentile | Pearson (all 34) | Spearman (all 34) | flag |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['id']} | {r['n_hits_true']}/{r['n_true']} | {r['fake_rate']['mean']:.3f} "
                  f"[{r['fake_rate']['q05']:.3f}, {r['fake_rate']['q95']:.3f}] | {r['percentile']:.1f} | "
                  f"{r['corr_all']['pearson']:+.3f} | {r['corr_all']['spearman']:+.3f} | "
                  f"{'FLAG: pre-registered follow-up' if r['flag_followup'] else '—'} |")
    json.dump(dict(rows=[{k: v for k, v in r.items() if k != "per_n"} for r in rows]),
              open(os.path.join(out_dir, "NEARMISS_SUMMARY.json"), "w"), indent=1)
    open(os.path.join(out_dir, "NEARMISS_SUMMARY.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "one":
        sys.exit(one(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "summary":
        sys.exit(summary(sys.argv[2]))
