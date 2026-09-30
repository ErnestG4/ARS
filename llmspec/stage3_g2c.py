"""Stage 3 G2c -- the SIZE of G2b's local shuffles, and a same-subspace control at THAT size. POST-HOC, DESCRIPTIVE
(Will's memo critique #11, 2026-09-27): "local shuffles cost ~0" needs the perturbation size next to it -- a shuffle
within k <= 32 neighbouring ranks may barely move the weights, in which case near-zero cost is expected whether or not
the ordering matters. Committed before it runs; no verdict of G2/G2b is changed by it.

Same checkpoint (pythia-1.4b step143000), probes, exact-fp32 model and fp16 re-storage as stage3_g2b.py; the local
permutation, seeds and scope (all 144 matrices) are G2b's exactly (stage3_g2b.local_perm, seed + 1000 L + j).
Per condition, per matrix, recorded:
  d_exact  = ||sigma' - sigma||_2 = ||U (sigma' - sigma) V^T||_F   (the shuffle's size before fp16 re-storage)
  d_eff    = ||half(W') - W16||_F                                  (what the model actually receives)
  fro      = ||W16||_F
  and, for comparison, G2's bulk shuffle (same seed) d_exact.
Conditions (seeds 1, 2, as G2b):
  local{k}:s        (k = 2, 8, 32) -- G2b's condition re-run; its dloss must reproduce G2b's banked value to 2e-4
                    (regression check: this is the same construction), else the script stops with rc 5.
  ctl_local{k}:s    W + U_b A V_b^T scaled per matrix to the local shuffle's d_exact -- G2b's sizematched_bulksub
                    construction (same generator seeds, so the same direction A) at the local shuffle's size.
Reading (declared now, descriptive; noise = the spread between seeds 1 and 2 of each condition):
  - if ctl_local{k} dloss is also ~0 (within the seed spread of local{k}, or |dloss| < 1e-3): near-zero local cost
    is what size alone predicts -- the k-sweep NEITHER supports NOR contradicts the "smooth, distributed" reading;
  - if ctl_local{k} dloss exceeds local{k} dloss beyond the seed spread: a local reordering is gentler than a generic
    same-subspace perturbation of equal size -- consistent with fine ordering carrying little;
  - if local{k} exceeds the control: local ordering costs more than its size.
  Also reported: d_eff / d_exact (whether fp16 re-storage dominates the perturbation), and the local/bulk size ratio.
Output: results/stage3_g2c.json (resumable per condition).
"""
import os, sys, json, time
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from pathlib import Path
import numpy as np
import torch
import remote_st as R
import stage3_extract as X
import stage3_g2 as G2
import stage3_g2b as G2B
import s3stats as S

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "stage3_g2c.json"
CONDS = [(f"{p}local{k}", s) for k in (2, 8, 32) for s in (1, 2) for p in ("", "ctl_")]


def main():
    res = json.loads(OUT.read_text()) if OUT.exists() else {"doc": __doc__, "conds": {}}
    g2b = json.loads((ROOT / "results" / "stage3_g2b.json").read_text())
    res["baseline"] = g2b["baseline"]
    probes = np.load(ROOT / "results" / "probes.npz")
    ck = X.Ckpt("pythia-1.4b", G2.REV); ck.fetch_all()
    m = X.build_model(ck)
    params = dict(m.named_parameters())
    names = list(dict.fromkeys(n for L in range(24) for n, _ in G2.targets(L)))

    def restore():
        for n, a, _ in R.fetch_many(ck.idx, names):
            a16 = a.astype(np.float16); assert np.array_equal(a16.astype(np.float32), a)
            params[n].data.copy_(torch.from_numpy(a16).to(X.DEV))

    for kind, seed in CONDS:
        key = f"{kind}:{seed}"
        if key in res["conds"]:
            continue
        R.check_stop(); t = time.time(); k = int(kind.split("local")[1]); per = []
        for L in range(24):
            for name, j in G2.targets(L):
                M = G2B.MNAME[(name.split(f"layers.{L}.")[1], j)]
                P = params[name]
                W16 = P.data if j is None else P.data.reshape(16, 3, 128, 2048)[:, j].reshape(2048, 2048)
                W16 = W16.clone(); W = W16.double()
                U, s, Vh = torch.linalg.svd(W, full_matrices=False)
                sd = s.cpu().numpy()
                sl = G2B.local_perm(sd, k, seed + 1000 * L + (j or 0))
                sb = G2.perm_sigma(sd, "bulk", seed + 1000 * L + (j or 0))
                d_exact = float(np.linalg.norm(sl - sd)); d_bulk = float(np.linalg.norm(sb - sd))
                if kind.startswith("ctl_"):
                    n = len(sd); a_, b_ = S.band_idx(n, "bulk"); lo_, hi_ = n - b_, n - a_
                    Ub, Vb = U[:, lo_:hi_], Vh[lo_:hi_]
                    gen = torch.Generator(device=X.DEV).manual_seed(seed * 100000 + 1000 * L + (j or 0) + 7)
                    Am = torch.randn((hi_ - lo_, hi_ - lo_), generator=gen, device=X.DEV, dtype=torch.float64)
                    P_ = Ub @ Am @ Vb
                    Wn = (W + P_ * (d_exact / float(P_.norm()))).half()
                    del P_, Am
                else:
                    Wn = ((U * torch.from_numpy(sl).to(X.DEV)) @ Vh).half()
                d_eff = float((Wn.double() - W).norm())
                per.append({"L": L, "M": M, "d_exact": d_exact, "d_eff": d_eff, "fro": float(W.norm()), "d_bulk": d_bulk})
                if j is None:
                    P.data.copy_(Wn)
                else:
                    P.data.reshape(16, 3, 128, 2048)[:, j].copy_(Wn.reshape(16, 128, 2048))
                del U, s, Vh, Wn, W, W16
            torch.cuda.empty_cache()
        loss = G2.text_loss(m, probes); dl = loss - res["baseline"]
        tot = lambda f: float(np.sqrt(sum(r[f] ** 2 for r in per)))
        rec = {"loss": loss, "dloss": dl, "d_exact_total": tot("d_exact"), "d_eff_total": tot("d_eff"),
               "fro_total": tot("fro"), "d_bulk_total": tot("d_bulk"),
               "rel_exact_median": float(np.median([r["d_exact"] / r["fro"] for r in per])), "per_matrix": per}
        if not kind.startswith("ctl_"):
            banked = g2b["conds"][key]["dloss"]; rec["g2b_banked_dloss"] = banked
            if abs(dl - banked) > 2e-4:
                print(f"REGRESSION FAIL {key}: dloss {dl:+.6f} vs banked {banked:+.6f}", flush=True); sys.exit(5)
        res["conds"][key] = rec
        restore()
        R.durable_save(OUT, lambda p: p.write_text(json.dumps(res, indent=1)))
        print(f"{key}: dloss {dl:+.5f}  d_exact {rec['d_exact_total']:.4f}  d_eff {rec['d_eff_total']:.4f}  "
              f"d_bulk {rec['d_bulk_total']:.3f}  fro {rec['fro_total']:.1f} ({time.time()-t:.0f}s)", flush=True)
    summ = {}
    for k in (2, 8, 32):
        lo = [res["conds"][f"local{k}:{s}"] for s in (1, 2)]; ct = [res["conds"][f"ctl_local{k}:{s}"] for s in (1, 2)]
        summ[f"k{k}"] = {"local_dloss": [c["dloss"] for c in lo], "ctl_dloss": [c["dloss"] for c in ct],
                         "d_exact_total": [c["d_exact_total"] for c in lo], "d_eff_over_exact": [c["d_eff_total"] / c["d_exact_total"] for c in lo],
                         "local_over_bulk_size": [c["d_exact_total"] / c["d_bulk_total"] for c in lo],
                         "rel_exact_median": [c["rel_exact_median"] for c in lo]}
    res["summary"] = summ
    R.durable_save(OUT, lambda p: p.write_text(json.dumps(res, indent=1)))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    try:
        main()
    except R.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
