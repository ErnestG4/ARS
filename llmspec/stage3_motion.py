"""Stage 3 motion pass (STAGE3_PREREG.md, Motion): Delta W between consecutive schedule revisions.

Streams each revision once (HF -> GPU, fp16, exact), layer by layer, keeping only the PREVIOUS revision's 24 x 6
layer matrices resident (~2.7 GB fp16) plus one current layer. Per layer and matrix type, with Delta W = W_b - W_a in fp64:
  dW_fro_rel       ||Delta W||_F / ||W_a||_F
  dW_stable_rank   ||Delta W||_F^2 / sigma_max(Delta W)^2
  dW_frac_top32    ||U32_a^T Delta W||_F^2 / ||Delta W||_F^2, where U32_a are W_a's top-32 left singular vectors
                   banked by stage3_extract (fp32; the fraction is a ratio of squared norms, so fp32 vectors are
                   ample); an isotropic Delta W would give 32 / n_rows.
Output: cache/s3_motion/<a>__<b>.npz per pair (resumable; honours STOP and the host-disk reserve).
"""
import os, sys, time
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from pathlib import Path
import numpy as np
import torch
import remote_st as R
import stage3_extract as X

ROOT = Path(__file__).resolve().parent
EST = "stage3-motion-v1"
MATS = ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")


def fetch_layer(idx, L):
    """One layer's six matrices, streamed HF -> GPU as fp16 (exact: asserted on the fp16 grid)."""
    p = f"gpt_neox.layers.{L}."
    def g(k):
        a, _ = R.fetch(idx, p + k)
        a16 = a.astype(np.float16)
        assert np.array_equal(a16.astype(np.float32), a), f"{k}: not on the fp16 grid"
        return torch.from_numpy(a16).to(X.DEV)
    qkv = g("attention.query_key_value.weight").reshape(16, 3, 128, 2048)
    return {"Q": qkv[:, 0].reshape(2048, 2048), "K": qkv[:, 1].reshape(2048, 2048), "V": qkv[:, 2].reshape(2048, 2048),
            "O": g("attention.dense.weight"), "MLP_IN": g("mlp.dense_h_to_4h.weight"), "MLP_OUT": g("mlp.dense_4h_to_h.weight")}


def main(revs):
    """GPU holds the previous revision's layer matrices (fp16, ~2.7 GB) plus ONE layer of the current revision:
    each current layer is streamed, compared with prev[L], then replaces it."""
    import specs as S
    out_dir = ROOT / "cache" / "s3_motion"; out_dir.mkdir(parents=True, exist_ok=True)
    prev = {}
    for i, rev in enumerate(revs):
        a = revs[i - 1] if i else None
        pair = out_dir / f"{a}__{rev}.npz" if a else None
        need_pair = pair is not None and not pair.exists()
        need_next = i + 1 < len(revs) and not (out_dir / f"{rev}__{revs[i+1]}.npz").exists()
        if not need_pair and not need_next:
            prev = {}
            continue
        R.check_stop()
        t = time.time()
        idx = R.index(S.MODELS["pythia-1.4b"]["repo"], rev)
        do_pair = need_pair and len(prev) == 24
        Ua = [np.load(ROOT / "cache" / "s3" / "pythia-1.4b" / a / f"L{L:02d}.npz") for L in range(24)] if do_pair else None
        res = {}
        for L in range(24):
            R.check_stop()
            cur = fetch_layer(idx, L)
            if do_pair:
                for M in MATS:
                    Wa, Wb = prev[L][M].double(), cur[M].double()
                    dW = Wb - Wa
                    f2 = float((dW ** 2).sum())
                    smax = float(torch.linalg.matrix_norm(dW, ord=2)) if f2 > 0 else 0.0
                    U = torch.from_numpy(Ua[L][f"U32_{M}"]).to(X.DEV, torch.float64)
                    res[f"L{L:02d}_{M}_dW_fro_rel"] = np.sqrt(f2) / float(Wa.norm())
                    res[f"L{L:02d}_{M}_dW_stable_rank"] = f2 / smax ** 2 if smax > 0 else np.nan
                    res[f"L{L:02d}_{M}_dW_frac_top32"] = float(((U.T @ dW) ** 2).sum()) / f2 if f2 > 0 else np.nan
                    del Wa, Wb, dW, U
            prev[L] = cur
            torch.cuda.empty_cache()
        if do_pair:
            res["estimator_version"] = np.array(EST)
            R.durable_save(pair, lambda p: np.savez(p, **res))
        print(f"{rev} {'pair ' + a + '__' + rev if do_pair else 'loaded as base'} {time.time()-t:.0f}s "
              f"peak_gpu={torch.cuda.max_memory_allocated()/2**30:.2f}GiB", flush=True)


if __name__ == "__main__":
    revs = open(ROOT / "pythia_1.4b_schedule.txt").read().split()
    revs.sort(key=lambda r: int(r.replace("step", "")))
    try:
        main(revs)
    except R.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
