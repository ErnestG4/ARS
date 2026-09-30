"""Stage 3 G2b -- controls for G2's bulk-permutation result. POST-HOC (requested in review 2026-09-25 ~23:55, after G2's
bulk:1 gave dloss +2.66 nats); PRE-REGISTERED by this commit, before it runs. Same checkpoint (step 143000), probes,
exact-fp32 model and fp16 re-storage as stage3_g2.py, whose identity control (dloss +0.0000) validates the rebuild.

Conditions (each applied to the stated scope; the SVD is always taken from the ORIGINAL matrix):
  sizematched:s  (s = 1, 2, 3; all 144 matrices)  W + G, G i.i.d. Gaussian with ||G||_F equal to ||W'_bulk(s) - W||_F
                 for that matrix (W'_bulk(s) = G2's bulk permutation, same seed). Same perturbation SIZE, no
                 singular-value structure.
  sizematched_bulksub:s  (s = 1, 2, 3; all 144 matrices)  AMENDMENT (review, before any G2b condition ran):
                 W + U_b A V_b^T, where U_b and V_b are W's singular vectors of the BULK band (the pairs G2's bulk shuffle
                 touches) and A is a k x k i.i.d. Gaussian, scaled so ||U_b A V_b^T||_F equals ||W'_bulk(s) - W||_F.
                 Same size AND same subspace as the treatment; the isotropic sizematched hits the top singular
                 directions the shuffle leaves untouched, so it is harsher than the treatment.
  local{k}:s     (k = 2, 8, 32; s = 1, 2; all matrices)  sigma permuted only within consecutive blocks of k ranks
                 inside the BULK band -- a graded, gentler shuffle.
  mpbulk:s       (s = 1, 2, 3; all matrices)  sigma permuted only among values at or below the fitted MP upper edge
                 (mp_fit_v2 scale x witness tau+), i.e. the MP-bulk definition, excluding detached outliers.
  dose_*         (bulk shuffle, seed 1)  scope = one matrix (L12 Q; L12 MLP_IN), one layer (L0; L12, all six), for
                 comparison with G2's all-144 bulk:1.
Readings, fixed now:
  SIZE (amended: the comparison is with the like-for-like control): if the mean sizematched_bulksub dloss >= 0.5 x
    the mean G2 bulk dloss, perturbation size explains at least half of the effect, and "the ordering of bulk
    singular values carries function" is NOT established. Otherwise ordering matters beyond size. The isotropic
    sizematched is reported as a harsher bound. (Both match ||W' - W||_F, never ||W||_F: a permutation preserves
    ||W||_F.)
  GRADED: local{k} dloss is reported against k, and mpbulk against bulk; no pass/fail.
  DOSE: dloss per scope is reported; no pass/fail.
Output: results/stage3_g2b.json (resumable per condition).
"""
import os, sys, json, time
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from pathlib import Path
import numpy as np
import torch
import remote_st as R
import stage3_extract as X
import stage3_g2 as G2
import stage3_analyze as A
import s3stats as S

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "stage3_g2b.json"
CONDS = ([("sizematched", s, None) for s in (1, 2, 3)] + [("sizematched_bulksub", s, None) for s in (1, 2, 3)] + [(f"local{k}", s, None) for k in (2, 8, 32) for s in (1, 2)]
         + [("mpbulk", s, None) for s in (1, 2, 3)]
         + [("dose_L12_Q", 1, [(12, "Q")]), ("dose_L12_MLP_IN", 1, [(12, "MLP_IN")]),
            ("dose_L0_all", 1, [(0, m) for m in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")]),
            ("dose_L12_all", 1, [(12, m) for m in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")])])
MNAME = {("attention.query_key_value.weight", 0): "Q", ("attention.query_key_value.weight", 1): "K",
         ("attention.query_key_value.weight", 2): "V", ("attention.dense.weight", None): "O",
         ("mlp.dense_h_to_4h.weight", None): "MLP_IN", ("mlp.dense_4h_to_h.weight", None): "MLP_OUT"}


def local_perm(sig_desc, k, seed):
    n = len(sig_desc); asc = sig_desc[::-1].copy()
    a, b = S.band_idx(n, "bulk")
    rng = np.random.default_rng(seed)
    for lo in range(a, b, k):
        idx = np.arange(lo, min(lo + k, b))
        asc[idx] = asc[rng.permutation(idx)]
    return asc[::-1].copy()


def mpbulk_perm(sig_desc, M, seed, wit):
    m, n = A.FULL[M]
    v2 = A.mp_fit_v2(sig_desc, m, n, wit["types"][M]["tau_plus"], wit["types"][M]["tau_minus"])
    edge = wit["types"][M]["tau_plus"] * v2["mp2_scale"] * (np.sqrt(m) + np.sqrt(n))
    asc = sig_desc[::-1].copy()
    idx = np.where(asc <= edge)[0]
    asc[idx] = asc[np.random.default_rng(seed).permutation(idx)]
    return asc[::-1].copy()


def main():
    res = json.loads(OUT.read_text()) if OUT.exists() else {"doc": __doc__, "conds": {}}
    g2 = json.loads((ROOT / "results" / "stage3_g2.json").read_text())
    res["baseline"] = g2["baseline"]
    wit = json.loads((ROOT / "results" / "stage3_witness.json").read_text())
    probes = np.load(ROOT / "results" / "probes.npz")
    ck = X.Ckpt("pythia-1.4b", G2.REV); ck.fetch_all()
    m = X.build_model(ck)
    params = dict(m.named_parameters())
    names = list(dict.fromkeys(n for L in range(24) for n, _ in G2.targets(L)))

    def restore():
        for n, a, _ in R.fetch_many(ck.idx, names):
            a16 = a.astype(np.float16); assert np.array_equal(a16.astype(np.float32), a)
            params[n].data.copy_(torch.from_numpy(a16).to(X.DEV))

    for kind, seed, scope in CONDS:
        key = f"{kind}:{seed}"
        if key in res["conds"]:
            continue
        R.check_stop(); t = time.time()
        for L in range(24):
            for name, j in G2.targets(L):
                M = MNAME[(name.split(f"layers.{L}.")[1], j)]
                if scope is not None and (L, M) not in scope:
                    continue
                P = params[name]
                W16 = P.data if j is None else P.data.reshape(16, 3, 128, 2048)[:, j].reshape(2048, 2048)
                W = W16.double()
                U, s, Vh = torch.linalg.svd(W, full_matrices=False)
                sd = s.cpu().numpy()
                sb = G2.perm_sigma(sd, "bulk", seed + 1000 * L + (j or 0))     # G2's exact bulk permutation
                if kind == "sizematched_bulksub":
                    d = float(((U * (torch.from_numpy(sb).to(X.DEV) - s)) @ Vh).norm())
                    n = len(sd); a_, b_ = S.band_idx(n, "bulk")
                    lo_, hi_ = n - b_, n - a_                                     # bulk band in DESCENDING order
                    Ub, Vb = U[:, lo_:hi_], Vh[lo_:hi_]
                    gen = torch.Generator(device=X.DEV).manual_seed(seed * 100000 + 1000 * L + (j or 0) + 7)
                    Am = torch.randn((hi_ - lo_, hi_ - lo_), generator=gen, device=X.DEV, dtype=torch.float64)
                    P_ = Ub @ Am @ Vb
                    Wn = (W + P_ * (d / float(P_.norm()))).half()
                    del P_, Am
                elif kind == "sizematched":
                    d = float(((U * (torch.from_numpy(sb).to(X.DEV) - s)) @ Vh).norm())
                    gen = torch.Generator(device=X.DEV).manual_seed(seed * 100000 + 1000 * L + (j or 0))
                    Gm = torch.randn(W.shape, generator=gen, device=X.DEV, dtype=torch.float64)
                    Wn = (W + Gm * (d / float(Gm.norm()))).half()
                else:
                    if kind.startswith("local"):
                        s2 = local_perm(sd, int(kind[5:]), seed + 1000 * L + (j or 0))
                    elif kind == "mpbulk":
                        s2 = mpbulk_perm(sd, M, seed + 1000 * L + (j or 0), wit)
                    else:                                                        # dose_*: G2's bulk permutation
                        s2 = sb
                    Wn = ((U * torch.from_numpy(s2).to(X.DEV)) @ Vh).half()
                if j is None:
                    P.data.copy_(Wn)
                else:
                    P.data.reshape(16, 3, 128, 2048)[:, j].copy_(Wn.reshape(16, 128, 2048))
                del U, s, Vh, Wn, W
            torch.cuda.empty_cache()
        loss = G2.text_loss(m, probes)
        res["conds"][key] = {"loss": loss, "dloss": loss - res["baseline"]}
        restore()
        R.durable_save(OUT, lambda p: p.write_text(json.dumps(res, indent=1)))
        print(f"{key}: dloss {loss - res['baseline']:+.4f} ({time.time()-t:.0f}s)", flush=True)
    bulk = np.mean([g2["conds"][f"bulk:{s}"]["dloss"] for s in (1, 2, 3)])
    sm = np.mean([res["conds"][f"sizematched:{s}"]["dloss"] for s in (1, 2, 3)])
    smb = np.mean([res["conds"][f"sizematched_bulksub:{s}"]["dloss"] for s in (1, 2, 3)])
    res["reading"] = {"g2_bulk_mean_dloss": bulk, "sizematched_bulksub_mean_dloss": smb,
                      "sizematched_isotropic_mean_dloss_harsher": sm,
                      "size_explains_half_or_more": bool(smb >= 0.5 * bulk)}
    R.durable_save(OUT, lambda p: p.write_text(json.dumps(res, indent=1)))
    print(json.dumps(res["reading"], indent=1))


if __name__ == "__main__":
    try:
        main()
    except R.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
