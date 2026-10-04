"""POST-HOC re-score (Will, 2026-10-04) of the step-143000 seed criteria R1 (K rotary concentration + rotary-row norm
share) and R2 (cross-head sharing) for PolyPythias 410M seeds 3 and 4 at their LAST VALID checkpoints, after the
restart finding (BULK_INIT_OVERLAP_FINDINGS §3: seed 3 valid through 64000, seed 4 through 96000; later uploads come
from restarted runs). Uses stage3_repl.r1_r2 UNCHANGED, with only the revision substituted (it hard-codes step143000).

Rows (all labelled NON-FINAL states, POST HOC; the registered counts stand as registered):
  seed3@64000, seed4@96000                      -- the two invalid-at-143k seeds at their last valid checkpoint
  pythia-410m / seed1 / seed2 @64000 and @96000 -- controls: how far R1/R2 move between 64k/96k and 143k in normal runs
Output: results/stage3_seed_restart_rescore.json.  GPU (as stage3_repl).
"""
import importlib, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent; sys.path.insert(0, str(ROOT))

RUNS = [("pythia-410m-seed3", 64000), ("pythia-410m-seed4", 96000),
        ("pythia-410m", 64000), ("pythia-410m", 96000), ("pythia-410m-seed1", 64000), ("pythia-410m-seed1", 96000),
        ("pythia-410m-seed2", 64000), ("pythia-410m-seed2", 96000)]
OUT = ROOT / "results" / "stage3_seed_restart_rescore.json"


def score(model, step):
    os.environ["LLMSPEC_MODEL"] = model
    import mcfg, stage3_motion, stage3_repl
    for m in (mcfg, stage3_motion, stage3_repl):
        importlib.reload(m)
    orig = stage3_motion.LayerSource

    class Src(orig):
        def __init__(self, rev, model=None):
            assert rev == "step143000", rev                   # r1_r2's only call; substitute the revision
            super().__init__(f"step{step}", model)
    stage3_motion.LayerSource = Src
    try:
        r1, r2 = stage3_repl.r1_r2()
    finally:
        stage3_motion.LayerSource = orig
    return {"model": model, "step": step, "R1": r1, "R2": r2}


def main():
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    for model, step in RUNS:
        key = f"{model}@{step}"
        if key in res:
            print("skip", key); continue
        r = score(model, step); res[key] = r
        OUT.write_text(json.dumps(res, indent=1, default=float))
        print(key, "R1 mass %.3f null %.3f rows %.4f -> %s | R2 %s" % (r["R1"]["K_rotary_mass"], r["R1"]["within_head_rotation_null"],
              r["R1"]["rotary_rows_frob_share"], r["R1"]["REPLICATES"], r["R2"]["REPLICATES"]), flush=True)
    print("RESCORE_DONE")


if __name__ == "__main__":
    main()
