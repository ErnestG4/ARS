"""ADDENDUM S4 (STAGE3_SEED_PREREG.md): known-answer licence for the density-matched calibrator, then a re-score of the
10-run per-head-Q drift with a LICENSED calibrator. FROZEN by commit before it runs. The Addendum-S1/S2 verdict
(FINDING_CANDIDATE, frozen drift test) and the S2 fidelity verdict (INCONCLUSIVE) stand as sealed; this is a separately
labelled re-score, not a relabelling.

WHY. The S2 fidelity test found the residual (observed - calibrator) perfectly monotone in calibrator mismatch, reversing
sign at the best fidelity: artefact-like, but its rule could not call it. Calibrators cannot be judged on the real spectra:
a density flexible enough to fit a head's own 64 levels can encode their actual spacings and reproduce the real q by
construction. They are judged on synthetic spectra with a KNOWN answer, built on realistic per-head shapes.

TRUTH SHAPES (two families; a calibrator must pass BOTH, so no family wins by matching its own construction):
  T_lam : adaptive Gaussian KDE of the head's lambda = sigma^2, bandwidth 2 x local mean spacing (k = 5 neighbours each
          side), TRUNCATED to lambda >= 0 (real per-head-Q lambda reaches 0.0097 x the head median; an untruncated kernel
          leaks 1.6-6.8% of its mass below 0, which clipping turns into tied levels)
  T_log : the same KDE on log lambda (positive support by construction)
  built from the 384 per-head-Q spectra of standard pythia-410m, step 143000. Scope: this certifies calibrator fidelity for
  truths smooth at >= 2 local spacings. Density structure at < 2 spacings is, from one 64-level spectrum, indistinguishable
  from spacing correlation; no calibrator can resolve it and none is claimed to.
CONDITIONS, paired (per head: one COE(64) draw u):
  (a) NULL    : T^-1(u)                 (true beta = 1)
  (b) PLANTED : T^-1(plant_f(u)), plant_f replaces round(f x 64) randomly chosen levels of u by i.i.d. uniforms (a
                Poisson admixture). f is fixed by a pilot on flat coordinates (20 pools, paired) as the grid value in
                {0.02, 0.04, ..., 0.20} whose mean q shift is closest to -0.020. Known effects E_q = mean[q(b) - q(a)],
                E_rt = mean[rt(b) - rt(a)] through the same truth.
CALIBRATORS (each fitted to the synthetic spectrum's own lambda, never to T):
  v1        : stage2_g7.fit_mixture, the frozen drift test's calibrator, used EXACTLY as stage3_ladder.py uses it
              (untruncated; icdf clipped at 1e-300). Its bias is reported whatever happens.
  v2_c{4,8,16}  : adaptive KDE on lambda, bandwidth c x local mean spacing, truncated to lambda >= 0
  v3_c{4,8,16}  : adaptive KDE on log lambda, bandwidth c x local mean spacing (log domain)
  All inverse CDFs of v2/v3 and of the truths are solved by bisection (80 halvings), never read off a grid.
PAIRED EVALUATION (removes the pool-to-pool noise, sd ~0.011 in q, without circularity): per pool a FRESH draw u' (independent
  of the u the calibrator was fitted on) is pushed through the truth and through every fitted calibrator.
    bias_X(k)   = mean over pools [X(T^-1 u') - X(Fhat_a,k^-1 u')]      (the residual calibrator k manufactures under the null)
    absorb_X(k) = mean over pools [X(Fhat_b,k^-1 u') - X(Fhat_a,k^-1 u')]
    recovery_X(k) = (E_X - absorb_X(k)) / E_X     (1 = the planted effect fully survives calibration; 0 = fully absorbed)
  X in {q (bulk kde(4) Brody q), rt (bulk <r~>)}, both computed exactly as s3stats.local_stats computes them (a fast path
  asserted bit-identical to local_stats at start). R = 100 pools of 384 heads per truth family; seed 20260927 + pool.
LICENCE, per arm X (q, rt), per calibrator k, required under BOTH truth families:
  the 95% interval of bias_X (mean +- 1.96 SE over pools) lies within +-tol_X, tol_q = 0.005, tol_rt = 0.0005
  (a quarter of the observed means, -0.0197 and -0.0021), AND recovery_X in [0.7, 1.3].
  Selection: among licensed k, the smallest max-over-families |bias_X|. The selection sees only synthetic data.
RE-SCORE (the 10 runs, per-head Q, step 143000): for the selected k per arm, residual_X(run) = X_obs - mean over 50 draws of
  X(Fhat_k^-1 u'), Fhat_k fitted to that run's 384 heads. The S1/S2 lattice is applied unchanged to (residual_q, residual_rt):
  t = mean/SE, SE = SD/sqrt(10), df 9; UNFOLDING-EXPLAINED iff |t_q| < 3 AND |t_rt| < 3; FINDING_CANDIDATE iff t_q <= -3 OR
  t_rt <= -3; otherwise MIXED. An arm with no licensed calibrator is NOT RESOLVABLE; the lattice is then read on the other arm
  alone and labelled as such (one arm quiet does not make UNFOLDING-EXPLAINED). No arm licensed -> NOT RESOLVABLE.
  REGRESSION GATE: v1 residual_q through this code must agree with the frozen drift test's per-run residual_q within 0.012
  (3 x the ladder's R = 10 noise) on every run; else the re-score is REFUSED.
  DESCRIPTIVE ONLY: every calibrator's real residuals are tabulated; no verdict is read from an unselected calibrator.
Output: results/stage3_calib_v2.json (pool records in results/stage3_calib_v2_pools.jsonl, resumable). STOP-aware.
"""
import json, os, sys
from pathlib import Path
from multiprocessing import Pool
import numpy as np
from scipy.special import ndtr
from scipy.stats import t as tdist
import s3stats as S, stage2_g7 as G
import remote_st as RS

ROOT = Path(__file__).resolve().parent
RUNS = ["pythia-410m"] + [f"pythia-410m-seed{k}" for k in range(1, 10)]
KINDS = ["v1", "v2_c4", "v2_c8", "v2_c16", "v3_c4", "v3_c8", "v3_c16"]
FAMS = ["T_lam", "T_log"]
R_POOLS, SEED, TOL = 100, 20260927, {"q": 0.005, "rt": 0.0005}
OUT = ROOT / "results" / "stage3_calib_v2.json"
POOLS = ROOT / "results" / "stage3_calib_v2_pools.jsonl"
F_PLANT = None


def q_rt(spectra):
    """bulk (q_kde, rt) exactly as s3stats.local_stats computes them (asserted at start)."""
    parts, rts = [], []
    for sig in spectra:
        lam = np.sort(np.asarray(sig, dtype=np.float64) ** 2); a, b = S.band_idx(len(lam), "bulk")
        raw = np.diff(lam[a:b]); r = raw[1:] / raw[:-1]
        rts.append(np.minimum(r, 1 / r) if np.all(raw > 0) else np.full(len(r), np.nan))
        s = np.diff(G.unfold(lam, "kde", 4))[a:b - 1]
        parts.append(s / (s[s > 0].mean() if np.any(s > 0) else np.nan))
    s, rt = np.concatenate(parts), np.concatenate(rts)
    q = None if float((s <= 0).mean()) > S.NONPOS_MAX else S.I8_brody_q_unbounded(s[s > 0])
    return q, (float(np.nanmean(rt)) if np.isfinite(rt).any() else None)


class KDE:
    """Adaptive Gaussian KDE: bandwidth c x local mean spacing (k = 5 each side). log=True: on log x (positive support);
    else on x, truncated to x >= 0. Inverse CDF by bisection."""
    def __init__(self, x, c, log=False, k=5):
        x = np.sort(np.asarray(x, float)); self.log = log
        if log:
            x = np.log(np.clip(x, 1e-300, None))
        n = len(x); j = np.arange(n); lo, hi = np.maximum(j - k, 0), np.minimum(j + k, n - 1)
        self.x = x
        self.b = np.maximum(c * (x[hi] - x[lo]) / (hi - lo), 1e-12 * (x[-1] - x[0]))
        self.lo, self.hi = float((x - 12 * self.b).min()), float((x + 12 * self.b).max())
        self.c0 = 0.0
        if not log:
            self.c0 = float(self._raw(0.0)); self.lo = max(self.lo, 0.0)

    def _raw(self, t):
        t = np.asarray(t, float)
        return ndtr((t[..., None] - self.x) / self.b).mean(-1)

    def icdf(self, u):
        target = self.c0 + np.asarray(u, float) * (1 - self.c0)
        lo, hi = np.full(target.shape, self.lo), np.full(target.shape, self.hi)
        for _ in range(80):
            mid = (lo + hi) / 2; below = self._raw(mid) < target
            lo, hi = np.where(below, mid, lo), np.where(below, hi, mid)
        v = (lo + hi) / 2
        return np.exp(v) if self.log else v


def fit(kind, lam):
    if kind == "v1":
        return G.fit_mixture(lam)
    fam, c = kind.split("_c")
    return KDE(lam, float(c), log=(fam == "v3"))


def truth(fam, lam):
    return KDE(lam, 2.0, log=(fam == "T_log"))


def coe(n, rng):
    return G.cue_phases(n, rng, 1)


def plant(u, f, rng):
    u = u.copy(); m = int(round(f * len(u)))
    if m:
        idx = rng.choice(len(u), m, replace=False); u[idx] = rng.random(m)
    return np.sort(u)


def to_sig(u, F):
    return np.sqrt(np.clip(np.sort(F.icdf(u)), 1e-300, None))     # identical to stage3_ladder.py's mapping


def real_heads(m):
    return [s for l in range(24) for s in np.load(ROOT / "cache" / "s3" / m / "step143000" / f"L{l:02d}.npz")["sighead_Q"]]


def pilot_one(i):
    rng = np.random.default_rng(SEED + 10_000 + i)
    us = [coe(64, rng) for _ in range(384)]
    q0, r0 = q_rt([np.sort(u) for u in us]); out = {}
    for f in np.round(np.arange(0.02, 0.201, 0.02), 2):
        q1, r1 = q_rt([plant(u, f, rng) for u in us]); out[f"{f:.2f}"] = (q1 - q0, r1 - r0)
    return out


def pool_one(args):
    fam, r, f = args
    rng = np.random.default_rng(SEED + r + (0 if fam == "T_lam" else 1_000_000))
    T = [truth(fam, np.sort(s ** 2)) for s in real_heads("pythia-410m")]
    u = [coe(64, rng) for _ in T]; ub = [plant(x, f, rng) for x in u]; up = [coe(64, rng) for _ in T]
    A = [to_sig(x, t) for x, t in zip(u, T)]; B = [to_sig(x, t) for x, t in zip(ub, T)]
    rec = {"fam": fam, "pool": r, "a": q_rt(A), "b": q_rt(B), "truth_fresh": q_rt([to_sig(x, t) for x, t in zip(up, T)])}
    for k in KINDS:
        Fa = [fit(k, np.sort(s ** 2)) for s in A]; Fb = [fit(k, np.sort(s ** 2)) for s in B]
        rec[k] = {"cal_a": q_rt([to_sig(x, F) for x, F in zip(up, Fa)]), "cal_b": q_rt([to_sig(x, F) for x, F in zip(up, Fb)])}
    return rec


def real_one(args):
    m, k, draws = args
    rng = np.random.default_rng(SEED + 7 + RUNS.index(m) * 100 + KINDS.index(k))
    H = real_heads(m); qo, ro = q_rt(H); Fs = [fit(k, np.sort(s ** 2)) for s in H]
    qc = [q_rt([to_sig(coe(len(s), rng), F) for s, F in zip(H, Fs)]) for _ in range(draws)]
    mq, mr = float(np.mean([c[0] for c in qc])), float(np.mean([c[1] for c in qc]))
    return {"run": m, "kind": k, "q_obs": qo, "rt_obs": ro, "q_cal": mq, "rt_cal": mr, "res_q": qo - mq, "res_rt": ro - mr}


def save(out):
    RS.durable_save(OUT, lambda p: p.write_text(json.dumps(out, indent=1, default=float)))


def summarise(recs):
    ka = {}
    for fam in FAMS:
        rr = [d for d in recs if d["fam"] == fam]
        ka[fam] = {"n_pools": len(rr)}
        for i, X in enumerate(("q", "rt")):
            E = np.array([d["b"][i] - d["a"][i] for d in rr])
            ka[fam][f"E_{X}"] = [float(E.mean()), float(E.std(ddof=1) / np.sqrt(len(E)))]
            for k in KINDS:
                bias = np.array([d["truth_fresh"][i] - d[k]["cal_a"][i] for d in rr])
                absb = np.array([d[k]["cal_b"][i] - d[k]["cal_a"][i] for d in rr])
                se = float(bias.std(ddof=1) / np.sqrt(len(bias)))
                rec_ratio = float((E.mean() - absb.mean()) / E.mean())
                ka[fam].setdefault(k, {})[X] = {"bias": float(bias.mean()), "bias_se": se, "absorb": float(absb.mean()),
                                                 "recovery": rec_ratio,
                                                 "pass": bool(abs(bias.mean()) + 1.96 * se <= TOL[X] and 0.7 <= rec_ratio <= 1.3)}
    return ka


def main(workers=10):
    out = json.loads(OUT.read_text()) if OUT.exists() else {"doc": __doc__}
    H = real_heads("pythia-410m"); ref = S.local_stats(H, "bulk"); fast = q_rt(H)
    assert fast == (ref["q_kde"], ref["rt"]), (fast, ref["q_kde"], ref["rt"])
    out["fastpath_identity"] = {"local_stats": [ref["q_kde"], ref["rt"]], "q_rt": list(fast), "identical": True}
    with Pool(workers) as P:
        if "pilot" not in out:
            RS.check_stop()
            res = P.map(pilot_one, range(20))
            grid = {f: [float(np.mean([x[f][0] for x in res])), float(np.mean([x[f][1] for x in res]))] for f in res[0]}
            fbest = min(grid, key=lambda f: abs(grid[f][0] + 0.020))
            out["pilot"] = {"grid_mean_dq_drt": grid, "f": float(fbest)}; save(out)
        f = out["pilot"]["f"]; print("pilot f =", f, out["pilot"]["grid_mean_dq_drt"][f"{f:.2f}"], flush=True)
        done = {(d["fam"], d["pool"]) for d in map(json.loads, POOLS.read_text().splitlines())} if POOLS.exists() else set()
        todo = [(fam, r, f) for r in range(R_POOLS) for fam in FAMS if (fam, r) not in done]
        for rec in P.imap_unordered(pool_one, todo):
            with open(POOLS, "a") as fh:
                fh.write(json.dumps(rec, default=float) + "\n"); fh.flush(); os.fsync(fh.fileno())
            print(f"{rec['fam']} pool {rec['pool']:3d}: " + " ".join(
                f"{k} {rec['truth_fresh'][0] - rec[k]['cal_a'][0]:+.4f}" for k in KINDS), flush=True)
            RS.check_stop()
        recs = [json.loads(l) for l in POOLS.read_text().splitlines()]
        ka = summarise(recs)
        for fam in FAMS:
            assert ka[fam]["n_pools"] == R_POOLS, (fam, ka[fam]["n_pools"])
        out["known_answer"] = ka
        lic = {X: [k for k in KINDS if all(ka[fam][k][X]["pass"] for fam in FAMS)] for X in ("q", "rt")}
        sel = {X: (min(lic[X], key=lambda k: max(abs(ka[fam][k][X]["bias"]) for fam in FAMS)) if lic[X] else None)
               for X in ("q", "rt")}
        out["licensed"], out["selected"] = lic, sel; save(out)
        print(json.dumps({"known_answer": ka, "licensed": lic, "selected": sel}, indent=1), flush=True)
        # real runs: every calibrator (descriptive table), v1 for the regression gate, the selected ones for the verdict
        real = out.get("real", [])
        have = {(d["run"], d["kind"]) for d in real}
        jobs = [(m, k, 50) for k in KINDS for m in RUNS if (m, k) not in have]
        for rec in P.imap_unordered(real_one, jobs):
            real.append(rec); out["real"] = real; save(out)
            print(f"real {rec['run']:20s} {rec['kind']:7s} res_q {rec['res_q']:+.4f} res_rt {rec['res_rt']:+.5f}", flush=True)
            RS.check_stop()
    drift = {r["run"]: r["residual_q"] for r in json.loads((ROOT / "results" / "stage3_drift_test.json").read_text())["rows"]}
    v1 = {d["run"]: d for d in out["real"] if d["kind"] == "v1"}
    gate = {m: [v1[m]["res_q"], drift[m], bool(abs(v1[m]["res_q"] - drift[m]) <= 0.012)] for m in RUNS}
    out["regression_gate"] = {"rows": gate, "PASS": all(g[2] for g in gate.values())}
    arms = {}
    for X in ("q", "rt"):
        k = sel[X]
        if k is None:
            arms[X] = {"calibrator": None, "status": "NOT RESOLVABLE (no licensed calibrator)"}; continue
        v = np.array([d[f"res_{X}"] for d in out["real"] if d["kind"] == k]); assert len(v) == 10
        se = float(v.std(ddof=1) / np.sqrt(10)); t = float(v.mean() / se)
        arms[X] = {"calibrator": k, "mean": float(v.mean()), "se": se, "t": t, "df": 9, "p_one_sided": float(tdist.cdf(t, 9))}
    out["rescore"] = arms
    if not out["regression_gate"]["PASS"]:
        out["verdict"] = "REFUSED (v1 regression gate failed)"
    else:
        live = [X for X in ("q", "rt") if arms[X].get("calibrator")]
        if not live:
            out["verdict"] = "NOT RESOLVABLE (no arm licensed)"
        else:
            ts = {X: arms[X]["t"] for X in live}
            if any(t <= -3 for t in ts.values()):
                v = "FINDING_CANDIDATE"
            elif all(abs(t) < 3 for t in ts.values()) and len(live) == 2:
                v = "UNFOLDING-EXPLAINED"
            elif all(abs(t) < 3 for t in ts.values()):
                v = "QUIET ON THE LICENSED ARM ONLY (other arm NOT RESOLVABLE; not UNFOLDING-EXPLAINED)"
            else:
                v = "MIXED"
            out["verdict"] = v + ("" if len(live) == 2 else f" [arms read: {live}]")
    save(out)
    print(json.dumps({k: out[k] for k in ("regression_gate", "rescore", "verdict")}, indent=1, default=float))


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    try:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 10)
    except RS.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
