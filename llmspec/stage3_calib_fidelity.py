"""ADDENDUM S2 item 3 (STAGE3_SEED_PREREG.md): calibrator-fidelity test for the per-head-Q drift residual. FROZEN by commit.
Per run: for each of the 384 per-head-Q spectra at step 143000, fit the calibrator density (stage2_g7.fit_mixture on
lambda = sigma^2) and measure mismatch = KS distance between the head's lambda values and that mixture CDF. Heads are
split into mismatch quartiles within the run. For each quartile: q_obs = s3stats bulk q on the quartile's heads, and
q_density = the same pipeline on COE levels mapped through those heads' fitted densities (R = 10); residual = q_obs -
q_density. Verdict over runs (n = number of 410M runs available; issued only at n = 10; SE = SD / sqrt(n), a t with n-1
df):
  CALIBRATOR_SHORTFALL  iff |mean residual(Q1 = lowest mismatch)| < 1 SE AND Spearman(quartile, mean residual) <= -0.8
  RESIDUAL_NOT_FIDELITY iff mean residual(Q1) <= -2 SE
  INCONCLUSIVE otherwise.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, t as tdist
import s3stats as S, stage2_g7 as G
ROOT = Path(__file__).resolve().parent
RUNS = ["pythia-410m"] + [f"pythia-410m-seed{k}" for k in range(1, 10)]


def run_one(m, R=10, seed=0):
    Z = [np.load(ROOT / "cache" / "s3" / m / "step143000" / f"L{l:02d}.npz") for l in range(24)]
    spectra = list(np.concatenate([z["sighead_Q"] for z in Z]))
    lam = [np.sort(np.asarray(s, float) ** 2) for s in spectra]
    fits = [G.fit_mixture(x) for x in lam]
    ks = []
    for x, f in zip(lam, fits):
        F = f.cdf(x); i = np.arange(1, len(x) + 1)
        ks.append(max((i / len(x) - F).max(), (F - (i - 1) / len(x)).max()))
    ks = np.array(ks); qcut = np.quantile(ks, [0.25, 0.5, 0.75])
    bins = np.digitize(ks, qcut)
    rng = np.random.default_rng(seed); res = []
    for b in range(4):
        idx = np.where(bins == b)[0]
        qo = S.local_stats([spectra[i] for i in idx], "bulk")["q_kde"]
        qd = np.mean([S.local_stats([np.sqrt(np.clip(np.sort(fits[i].icdf(G.cue_phases(64, rng, 1))), 1e-300, None)) for i in idx], "bulk")["q_kde"] for _ in range(R)])
        res.append({"quartile": b, "n_heads": int(len(idx)), "ks_median": float(np.median(ks[idx])), "q_obs": qo, "q_density": float(qd), "residual": float(qo - qd)})
    return res


def main():
    fp = ROOT / "results" / "stage3_calib_fidelity.json"
    out = json.loads(fp.read_text()) if fp.exists() else {"doc": __doc__, "runs": {}}
    for m in RUNS:
        if m in out["runs"] or not (ROOT / "cache" / "s3" / m / "step143000" / "DONE").exists():
            continue
        out["runs"][m] = run_one(m); fp.write_text(json.dumps(out, indent=1))
        print(m, [round(r["residual"], 3) for r in out["runs"][m]], flush=True)
    n = len(out["runs"])
    Rm = np.array([[r["residual"] for r in v] for v in out["runs"].values()])       # (n, 4)
    mean, se = Rm.mean(0), Rm.std(0, ddof=1) / np.sqrt(n)
    rho = float(spearmanr(np.arange(4), mean)[0])
    t1 = float(mean[0] / se[0]); p1 = float(tdist.cdf(t1, n - 1))
    out["summary"] = {"n_runs": n, "mean_residual_by_quartile": mean.tolist(), "se_by_quartile": se.tolist(),
                      "spearman_quartile_vs_residual": rho, "t_Q1": t1, "df": n - 1, "p_one_sided_Q1": p1}
    if n < 10:
        out["verdict"] = "INTERIM (n < 10; no verdict issued)"
    elif abs(t1) < 1 and rho <= -0.8:
        out["verdict"] = "CALIBRATOR_SHORTFALL"
    elif t1 <= -2:
        out["verdict"] = "RESIDUAL_NOT_FIDELITY"
    else:
        out["verdict"] = "INCONCLUSIVE"
    fp.write_text(json.dumps(out, indent=1))
    print(json.dumps(out["summary"], indent=1), "\nverdict:", out["verdict"])


if __name__ == "__main__":
    main()
