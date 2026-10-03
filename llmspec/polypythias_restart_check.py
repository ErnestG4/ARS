"""Provenance check for PolyPythias seeds 3 and 4 (the two 'late loss spike' runs), 2026-10-03. CPU, streams .bin files.
Trigger: BULK_INIT_OVERLAP found their late checkpoints suddenly re-correlated with the initialisation (seed 4 at 128k:
rho_bulk 0.99, alpha_hat 0.97, d 0.26 -- the signature of a ~step-1000 checkpoint; seed 3 at 96k: rho 0.79, alpha_hat 0.71).
Question: are the late checkpoints continuations of their own earlier checkpoints, or early-training states re-uploaded /
restarted? READING RULE (declared before running): for each seed, layers {0, 12, 23}, matrices Q and MLP_IN, the
elementwise Pearson correlation between every pair of the 26 schedule revisions. For a late revision L in {96000, 128000,
143000}: CONTINUATION iff its best-correlated other revision is a grid neighbour and correlation falls monotonically with
grid distance; RESTART/MISLABEL CANDIDATE iff some revision s <= 16000 correlates with W_L more strongly than L's
predecessor does, or corr(W_L, W_s) > 0.9 for some s <= 4000. Seed 1 is the control (expected CONTINUATION everywhere).
Output: results/polypythias_restart_check.json (full 26x26 correlation matrices per seed/layer/matrix + the readings)."""
import json, sys, time, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import remote_st as R, mcfg, stage3_extract_mf as X
REVS = Path(HERE / "pythia_1.4b_schedule.txt").read_text().split()
STEP = {r: int(r[4:]) for r in REVS}; ORDER = sorted(REVS, key=lambda r: STEP[r])
LATE = ["step96000", "step128000", "step143000"]; LAYERS = [0, 12, 23]; MATS = ["Q", "MLP_IN"]
def load(model, rev, c):
    p = R.download_file(c["repo"], "pytorch_model.bin", rev, HERE / "cache" / "bin_tmp" / f"{c['repo'].replace('/', '__')}__{rev}.bin")
    ck = X.CkptBin(str(p)); out = {}
    for L in LAYERS:
        m = X.layer_mats(ck, L, c)
        for M in MATS:
            out[(L, M)] = np.asarray(m[M], dtype=np.float32).ravel()
    Path(p).unlink(missing_ok=True); return out
def main(seeds):
    res = {"revs": ORDER, "late": LATE, "layers": LAYERS, "mats": MATS, "seeds": {}}
    for seed in seeds:
        model = f"pythia-410m-seed{seed}"; c = mcfg.MODELS[model]; (HERE / "cache" / "bin_tmp").mkdir(parents=True, exist_ok=True)
        W = {}; t0 = time.time()
        for rev in ORDER:
            R.check_stop() if hasattr(R, "check_stop") else None
            W[rev] = load(model, rev, c); print(model, rev, "loaded", f"{time.time()-t0:.0f}s", flush=True)
        entry = {}
        for L in LAYERS:
            for M in MATS:
                A = np.stack([W[r][(L, M)] for r in ORDER]); A = A - A.mean(1, keepdims=True); A /= np.linalg.norm(A, axis=1, keepdims=True)
                C = A @ A.T; key = f"L{L:02d}_{M}"; entry[key] = {"corr": C.round(6).tolist(), "readings": {}}
                for Lr in LATE:
                    i = ORDER.index(Lr); row = C[i].copy(); row[i] = -1; j = int(np.argmax(row)); pred = ORDER[i - 1]
                    early_best = max((C[i][ORDER.index(s)] for s in ORDER if STEP[s] <= 16000 and s != Lr), default=-1)
                    early4k = max((C[i][ORDER.index(s)] for s in ORDER if STEP[s] <= 4000), default=-1)
                    word = ("RESTART/MISLABEL CANDIDATE" if (early_best > C[i][i - 1] or early4k > 0.9) else "CONTINUATION")
                    entry[key]["readings"][Lr] = {"best_other": ORDER[j], "best_corr": float(row[j]), "pred": pred, "pred_corr": float(C[i][i - 1]),
                                                   "best_early<=16k": float(early_best), "best<=4k": float(early4k), "word": word}
        res["seeds"][model] = entry
        words = sorted({r["word"] for e in entry.values() for r in e["readings"].values()}); print(model, "WORDS:", words, flush=True)
        (HERE / "results" / "polypythias_restart_check.json").write_text(json.dumps(res, indent=0))
    print("done", flush=True)
if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [4, 3, 1])
