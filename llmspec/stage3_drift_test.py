"""ADDENDUM S1 item 4 (STAGE3_SEED_PREREG.md, bb7e573): pre-registered noise-scaled test of the per-head-Q late-training
drift over all 10 410M runs (standard + seeds 1-9). FROZEN by commit before it is run on the full set.
Per run r, at per-head Q, step 143000:
  residual_q(r) = dq_obs(r) - dq_density(r), with dq_density from the density-matched COE witness (stage3_ladder.py,
  R = 10; computed here on demand for runs without a ladder entry)
  drt(r)        = observed d<r~> (no unfolding)
SE = SD over runs / sqrt(n). Verdicts:
  UNFOLDING-EXPLAINED  iff |mean residual_q| < 3 SE AND |mean drt| < 3 SE
  FINDING_CANDIDATE    iff mean residual_q <= -3 SE OR mean drt <= -3 SE (a first crack in the bulk null at ~0.1 in q)
  otherwise            MIXED (reported as such)
Refuses to issue a verdict with fewer than 10 runs (prints an interim table instead, labelled INTERIM).
"""
import json, os, subprocess, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent
RUNS = ["pythia-410m"] + [f"pythia-410m-seed{k}" for k in range(1, 10)]


def main():
    lad_fp = ROOT / "results" / "stage3_ladder.json"
    rows = []
    for m in RUNS:
        if not (ROOT / "results" / f"stage3_null_{m}.json").exists():
            continue
        lad = json.loads(lad_fp.read_text()) if lad_fp.exists() else {}
        key = f"{m}|head_Q|143000"
        if key not in lad:
            env = dict(os.environ, LLMSPEC_MODEL=m, OMP_NUM_THREADS="4")
            if m != "pythia-410m":
                env["LLMSPEC_WITNESS"] = "pythia-410m"
            subprocess.run([sys.executable, str(ROOT / "stage3_ladder.py"), "head_Q", "143000"], env=env, check=True,
                           stdout=subprocess.DEVNULL)
            lad = json.loads(lad_fp.read_text())
        e = lad[key]
        rows.append({"run": m, "dq_obs": e["observed"]["dq"], "dq_density": e["density_matched"]["dq"],
                     "residual_q": e["observed"]["dq"] - e["density_matched"]["dq"], "drt": e["observed"]["drt"]})
    n = len(rows)
    rq = np.array([r["residual_q"] for r in rows]); dr = np.array([r["drt"] for r in rows])
    se_q, se_r = rq.std(ddof=1) / np.sqrt(n), dr.std(ddof=1) / np.sqrt(n)
    out = {"doc": __doc__, "n_runs": n, "rows": rows, "mean_residual_q": float(rq.mean()), "se_residual_q": float(se_q),
           "z_residual_q": float(rq.mean() / se_q), "mean_drt": float(dr.mean()), "se_drt": float(se_r),
           "z_drt": float(dr.mean() / se_r)}
    if n < 10:
        out["verdict"] = "INTERIM (n < 10; no verdict issued)"
    elif abs(out["z_residual_q"]) < 3 and abs(out["z_drt"]) < 3:
        out["verdict"] = "UNFOLDING-EXPLAINED"
    elif out["z_residual_q"] <= -3 or out["z_drt"] <= -3:
        out["verdict"] = "FINDING_CANDIDATE"
    else:
        out["verdict"] = "MIXED"
    (ROOT / "results" / "stage3_drift_test.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("doc", "rows")}, indent=1))
    for r in rows:
        print(f"  {r['run']:20s} dq_obs {r['dq_obs']:+.3f} dq_density {r['dq_density']:+.3f} residual {r['residual_q']:+.3f} drt {r['drt']:+.4f}")


if __name__ == "__main__":
    main()
