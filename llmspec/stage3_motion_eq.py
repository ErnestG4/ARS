"""POST-HOC (requested in review 2026-09-25 ~23:55): Delta W over EQUAL 1000-step intervals, to separate the
dynamics from checkpoint spacing. Consecutive-schedule intervals grow from 1 to 1000+ steps, and a sum over more
steps accumulates more independent directions, so "low-rank early, high-rank late" could be spacing alone.
Pairs (t, t+1000): t in 1k, 2k, 3k, 4k (spanning the warmup end at 1430), 7k, 15k, 31k, 63k, 127k, 142k.
Per layer and type: dW_stable_rank (scale-free), dW_fro_rel, dW_frac_top32 (top-32 left subspace of W_a from the
fp64 Gram eigh), and the LR integral over the interval (Pythia config: warmup 1430, cosine 2e-4 -> 2e-5), plus
dW_fro_per_lr = ||dW||_F / (||W_a||_F x LR integral). Output: cache/s3_motion_eq/<a>__<b>.npz (resumable).
"""
import os, sys, time
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from pathlib import Path
import numpy as np, torch
import remote_st as R
import stage3_extract as X
import stage3_motion as MO
import mcfg
ROOT = Path(__file__).resolve().parent
PAIRS = [(t, t + 1000) for t in (1000, 2000, 3000, 4000, 7000, 15000, 31000, 63000, 127000, 142000)]
Wu, T, LR0, LRmin = 1430, 143000, 2e-4, 2e-5
def lr(t):
    t = np.asarray(t, float)
    return np.where(t < Wu, LR0 * t / Wu, LRmin + (LR0 - LRmin) / 2 * (np.cos(np.pi * (t - Wu) / (T - Wu)) + 1))
def main():
    od = ROOT / "cache" / f"s3_motion_eq{mcfg.suffix()}"; od.mkdir(parents=True, exist_ok=True)
    NL, repo = mcfg.get()["n_layer"], mcfg.get()["repo"]
    for a, b in PAIRS:
        f = od / f"step{a}__step{b}.npz"
        if f.exists():
            continue
        R.check_stop(); t0 = time.time()
        ia, ib = R.index(repo, f"step{a}"), R.index(repo, f"step{b}")
        lri = float(lr(np.arange(a, b)).sum())
        res = {"lr_integral": lri}
        for L in range(NL):
            R.check_stop()
            A_, B_ = MO.fetch_layer(ia, L), MO.fetch_layer(ib, L)
            for M in MO.MATS:
                Wa = A_[M].double(); dW = B_[M].double() - Wa
                f2 = float((dW ** 2).sum()); smax = MO.sigma_max(dW) if f2 > 0 else 0.0
                G = Wa @ Wa.T
                U32 = torch.linalg.eigh(G)[1][:, -32:]
                res[f"L{L:02d}_{M}_dW_stable_rank"] = f2 / smax ** 2 if smax > 0 else np.nan
                res[f"L{L:02d}_{M}_dW_fro_rel"] = np.sqrt(f2) / float(Wa.norm())
                res[f"L{L:02d}_{M}_dW_fro_per_lr"] = np.sqrt(f2) / float(Wa.norm()) / lri
                res[f"L{L:02d}_{M}_dW_frac_top32"] = float(((U32.T @ dW) ** 2).sum()) / f2 if f2 > 0 else np.nan
                del Wa, dW, G, U32
            del A_, B_; torch.cuda.empty_cache()
        res["estimator_version"] = np.array("stage3-motion-eq-v1")
        R.durable_save(f, lambda p: np.savez(p, **res))
        sr = np.mean([res[f"L{L:02d}_Q_dW_stable_rank"] for L in range(NL)])
        print(f"step{a}__step{b}: lr_int {lri:.3f} mean Q dW stable rank {sr:.1f} ({time.time()-t0:.0f}s)", flush=True)
if __name__ == "__main__":
    try:
        main()
    except R.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
