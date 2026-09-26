"""Gate-first ladder, step 2 (STAGE3_PREREG.md, SEALED NULL): the DENSITY-MATCHED WITNESS for a VIOLATED cell.
For every spectrum in the cell's pool (per-head: every head; full: every layer), fit that spectrum's own density of
lambda = sigma^2 with stage2_g7.fit_mixture (the G7 machinery; Gaussian mixture, K by BIC), draw COE(N) levels (N =
spectrum length), map them through that density's inverse CDF, and run the IDENTICAL s3stats pipeline (bulk band, kde(4))
on the pool. R = 10 replicate pools.
Reading (registered): if the density-matched witness reproduces the observed deviation within tolerance
(|dq_obs - dq_density| <= 0.10 and |drt_obs - drt_density| <= 0.010, where dq_density = q_density - q_witness(G1)), the cell
is DENSITY_ARTIFACT, not beta != 1. Otherwise it goes to step 3 (precision floor), and only then to FINDING_CANDIDATE.
Usage: LLMSPEC_MODEL=<model> [LLMSPEC_WITNESS=<model>] stage3_ladder.py <type> <step>
"""
import json, os, sys
from pathlib import Path
import numpy as np
import mcfg, s3stats as S, stage2_g7 as G
ROOT = Path(__file__).resolve().parent


def main(T, step, R=10, seed=0):
    model = mcfg.name(); C = mcfg.get()
    wsrc = os.environ.get("LLMSPEC_WITNESS")
    wit = json.loads((ROOT / "results" / f"stage3_witness{mcfg.suffix(wsrc) if wsrc else mcfg.suffix()}.json").read_text())
    ref = wit["types"][T]["runs"]["witness_fp16_final"]
    Z = [np.load(ROOT / "cache" / "s3" / model / f"step{step}" / f"L{l:02d}.npz") for l in range(C["n_layer"])]
    spectra = list(np.concatenate([z[f"sighead_{T[5:]}"] for z in Z])) if T.startswith("head_") else [z[f"sig_{T}"] for z in Z]
    obs = S.local_stats(spectra, "bulk")
    dq_obs, drt_obs = obs["q_kde"] - ref["bulk:q_kde"]["mean"], obs["rt"] - ref["bulk:rt"]["mean"]
    targets = [G.fit_mixture(np.sort(np.asarray(s, float) ** 2)) for s in spectra]
    rng = np.random.default_rng(seed)
    qs, rts = [], []
    for r in range(R):
        syn = []
        for s, Tg in zip(spectra, targets):
            u = G.cue_phases(len(s), rng, 1)                       # COE(N): exactly uniform density, beta = 1
            lam = np.sort(Tg.icdf(u))
            syn.append(np.sqrt(np.clip(lam, 1e-300, None)))
        st = S.local_stats(syn, "bulk")
        qs.append(st["q_kde"]); rts.append(st["rt"])
    dq_d, drt_d = float(np.mean(qs)) - ref["bulk:q_kde"]["mean"], float(np.mean(rts)) - ref["bulk:rt"]["mean"]
    reproduced = abs(dq_obs - dq_d) <= 0.10 and abs(drt_obs - drt_d) <= 0.010
    out = {"model": model, "type": T, "step": step, "observed": {"q": obs["q_kde"], "rt": obs["rt"], "dq": dq_obs, "drt": drt_obs},
           "density_matched": {"q_mean": float(np.mean(qs)), "q_sd": float(np.std(qs, ddof=1)), "rt_mean": float(np.mean(rts)),
                               "dq": dq_d, "drt": drt_d, "R": R},
           "K_counts": np.bincount([len(t.w) for t in targets]).tolist(),
           "label": "DENSITY_ARTIFACT" if reproduced else "NOT_REPRODUCED -> ladder step 3 (precision floor)"}
    fp = ROOT / "results" / "stage3_ladder.json"
    allr = json.loads(fp.read_text()) if fp.exists() else {}
    allr[f"{model}|{T}|{step}"] = out
    fp.write_text(json.dumps(allr, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
