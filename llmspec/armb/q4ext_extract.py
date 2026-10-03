"""Q4EXT descriptive extraction (Q4EXT_PREREG.md §2, 3e52ea3): the SEALED B4 extractor (b4_extract.run_arm, seal verified
through b4_analyze.verify_seal) with the arms' stops extended AT RUNTIME, exactly as a0r_score.py does -- A0 -> 10000,
M0s1 -> 10000, M0s3 (third Muon seed, W = 1430, stop 3000) added. GPU only. Resumable: run_arm skips every step with a
DONE marker, so the <= 3000 part of A0 / M0s1 (already banked by B4) is not recomputed.

Second pass (`dw0`): per grid step at the 100-step cadence (+ the log steps), per layer and type, ||W_t - W_0||_F,
||W_t||_F and sigma_1 from the checkpoints themselves (the bank holds spectra, not weights) -> cache/armb/<arm>/DW0_<t>.npz.
DESCRIPTIVE ONLY (prereg §2): nothing here chooses a statistic; q4ext_descriptive.py plots and tabulates.

Usage: q4ext_extract.py extract [arms...] | dw0 [arms...] | all | dry
"""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
EXT = {"A0": 10000, "M0s1": 10000, "M0s3": 3000}
W_M0S3 = 1430
SUBS = []


def inject():
    import grids, q1_models as QM, q1_warp as W
    for arm, stop in EXT.items():
        grids.STOPS[arm] = stop; W.STOP[arm] = stop
        if arm not in QM.ARMS:
            QM.ARMS[arm] = W_M0S3; QM._CX[arm] = QM.cum(W_M0S3, 12000)
    SUBS.append({"runtime": f"grids.STOPS/q1_warp.STOP <- {EXT}; q1_models.ARMS/_CX += M0s3 (W {W_M0S3})"})
    return grids, QM, W


def dw0_steps(arm):
    from grids import arm_grid
    g = arm_grid(arm)
    return [t for t in g if t % 100 == 0 or t in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)]


def stage_extract(arms):
    import b4_analyze as B; B.verify_seal()
    import b4_extract as E; inject(); E.STOPS.update(EXT)
    for arm in arms:
        E.run_arm(arm); print(f"extract done {arm}", flush=True)


def stage_dw0(arms):
    import torch
    import b4_extract as E; inject()
    for arm in arms:
        out_dir = E.CACHE / arm
        todo = [t for t in dw0_steps(arm) if not (out_dir / f"DW0_{t:05d}.npz").exists()]
        if not todo:
            print(f"dw0 {arm}: nothing to do", flush=True); continue
        c0 = E.CkptArmb(arm, 0); m0 = {L: E.mats(c0.t, L) for L in range(E.NL)}
        for t in todo:
            E.R.check_stop()
            ck = E.CkptArmb(arm, t); res = {}
            for L in range(E.NL):
                mt = E.mats(ck.t, L)
                for M in mt:
                    dw = mt[M] - m0[L][M]
                    res[f"L{L:02d}_{M}_dw0_fro"] = np.array(float(dw.norm()))
                    res[f"L{L:02d}_{M}_w_fro"] = np.array(float(mt[M].norm()))
                    res[f"L{L:02d}_{M}_sigma1"] = np.array(float(torch.linalg.matrix_norm(mt[M], 2)))
            res["ckpt_sha256"] = np.array(ck.sha256); ck.close()
            fp = out_dir / f"DW0_{t:05d}.npz"; E.R.durable_save(fp, lambda p: np.savez(p, **res))
            print(f"{arm} dw0 step {t} done", flush=True)
        c0.close(); del m0; torch.cuda.empty_cache()


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "dry"; arms = sys.argv[2:] or list(EXT)
    if cmd == "dry":
        grids, *_ = inject()
        import b4_extract as E
        for arm in arms:
            g = grids.arm_grid(arm); done = sum((E.CACHE / arm / f"step{t:05d}" / "DONE").exists() for t in g)
            dd = sum((E.CACHE / arm / f"DW0_{t:05d}.npz").exists() for t in dw0_steps(arm))
            print(f"{arm}: stop {grids.STOPS[arm]} grid {len(g)} steps, {done} banked, {len(g)-done} to extract; "
                  f"dw0 {dd}/{len(dw0_steps(arm))} done")
        print(json.dumps(SUBS)); return
    if cmd in ("extract", "all"): stage_extract(arms)
    if cmd in ("dw0", "all"): stage_dw0(arms)
    print("Q4EXT_EXTRACT_DONE", cmd, arms, flush=True)


if __name__ == "__main__":
    main()
