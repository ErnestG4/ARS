"""Stage 1: bank raw attention spectra for one (model, revision). Resumable per layer; honours STOP.

Banks (raw object, per no-forbidden-recompute): cache/spectra/<model>/<rev>/L<layer>.npz with
  sig_head_<M>  (n_head, d_head)  singular values of the per-head d_head x d_model block, fp64
  sig_full_<M>  (d_model,)        singular values of the full layer matrix, fp64
  grid_<M>      json              G4 grid audit of the stored tensor
  rownorm_<M>   (n_head, d_head)  row norms of each per-head block (dead-row diagnostic)
  rms_head_<M>  (n_head,)         entry rms per head (precision floor = u * rms * (sqrt p + sqrt n))
Raw tensors are banked too: cache/weights/<model>/<rev>/L<layer>_<M>.npy (OLMo F32 as stored; Pythia as fp16,
asserted lossless because its F32 checkpoints are fp16 upcasts).
for M in Q, K, V, O.  Usage: stage1_spectra.py <model> <rev> [<rev> ...]
"""
import json, sys, time
from pathlib import Path
import numpy as np
import remote_st as R
import specs as S
import peaks as P

ROOT = Path(__file__).resolve().parent
EST = "stage1-spectra-v2 (direct svdvals fp64 cuda)"


def bank(model, rev):
    c = S.MODELS[model]
    d = ROOT / "cache" / "spectra" / model / rev
    d.mkdir(parents=True, exist_ok=True)
    idx = None
    for L in range(c["n_layer"]):
        f = d / f"L{L:02d}.npz"
        if f.exists():
            continue
        R.check_stop()
        if idx is None:
            idx = R.index(c["repo"], rev)
        t = time.time()
        blocks = S.attn_blocks(model, idx, L, R.fetch)
        out = {}
        wd = ROOT / "cache" / "weights" / model / rev
        wd.mkdir(parents=True, exist_ok=True)
        for M, (full, ph, dt) in blocks.items():
            if model.startswith("pythia"):   # stored F32 values are fp16 upcasts (G4): fp16 is LOSSLESS
                f16 = full.astype(np.float16)
                assert np.array_equal(f16.astype(np.float32), full), "not on the fp16 grid; refusing lossy save"
                np.save(wd / f"L{L:02d}_{M}.npy", f16)
            else:
                np.save(wd / f"L{L:02d}_{M}.npy", full)
            out[f"rownorm_{M}"] = np.linalg.norm(ph.astype(np.float64), axis=-1)
            out[f"rms_head_{M}"] = np.sqrt((ph.astype(np.float64) ** 2).mean(axis=(-1, -2)))
            out[f"sig_head_{M}"] = P.singvals(ph)
            out[f"sig_full_{M}"] = P.singvals(full)[0]
            out[f"grid_{M}"] = np.array(json.dumps(S.grid_audit(full, dt)))
        out["estimator_version"] = np.array(EST)
        tmp = f.with_suffix(".tmp.npz")
        np.savez(tmp, **out)
        tmp.rename(f)
        print(f"{model} {rev} L{L:02d} {time.time()-t:.1f}s", flush=True)
    (d / "DONE").write_text(EST)


if __name__ == "__main__":
    model, revs = sys.argv[1], sys.argv[2:]
    try:
        for rev in revs:
            bank(model, rev)
    except R.Stopped as e:
        print("STOPPED:", e, flush=True)
        sys.exit(3)
