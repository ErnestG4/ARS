"""Stage 3 G1 pooled-null witness + G4 precision + mp_fit_v1 margins + G0 KS reference (STAGE3_PREREG.md).

For each matrix type (full Q/K/V/O 2048^2, MLP_IN 8192x2048, MLP_OUT 2048x8192: K = 24 matrices per pool;
per-head Q/K/V/O 128x2048: K = 384 per pool):
  Gaussian entries scaled to the real entry rms (mean over layers, from the banked Stage 3 extraction), then
  (i) rounded to the fp16 grid (the witness proper, G4 inside it) and (ii) left in fp64 (the G4 contrast).
  Local statistics via s3stats.local_stats on every band, R = 20 replicate pools (fp16, final-checkpoint scale)
  = THE WITNESS. Checks, R = 5 each: fp64 at the final scale (G4) and fp16 at the step-0 scale (scale
  invariance). If the two scales differ by > 0.002 in bulk <r~> or > 0.03 in bulk q, the witness must be
  regenerated per checkpoint (flagged, not silently pooled).
Singular values here come from fp64 Gram eigvalsh on the GPU: 25x faster than svdvals on this card, and it
agrees with svdvals to 1.2e-10 relative on 2048^2 Gaussian (worst sigma_min; measured 2026-09-25). The real
matrices use direct SVD.
Also banked from the same R=20 draws: per matrix sigma_max/E+, sigma_min/E-, and the KS distance of
sigma^2/(n_max s^2) to MP(c = n_min/n_max) -> tau+ (99th pct), tau- (1st pct), KS 95th pct.
G0 reading of the prereg's "pooled KS <= 95th pct of the same KS": per matrix, with the count of step-0
matrices above the 95th pct tested binomially (p >= 0.01 passes). Clarified pre-data, before step 0 is analysed.
Output: results/stage3_witness.json (+ raw witness sigma quantiles).
"""
import json, sys, time
from pathlib import Path
import numpy as np
import torch
import s3stats as S
import remote_st as R

ROOT = Path(__file__).resolve().parent
DEV = "cuda"
import mcfg
_C = mcfg.get()
MODEL = mcfg.name()
TYPES = {**{M: (m, n, _C["n_layer"]) for M, (m, n) in mcfg.full_shapes().items()},
         **{f"head_{M}": (_C["DH"], _C["D"], _C["n_layer"] * _C["H"]) for M in "QKVO"}}
# pythia-1.4b: identical to the original hard-coded table (Q..O 2048^2 x24, MLP 8192x2048 x24, heads 128x2048 x384)
R_MAIN, R_CHECK = 20, 5


def mp_cdf(c):
    a, b = (1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2
    g = np.linspace(a, b, 40001)
    f = np.sqrt(np.clip((b - g) * (g - a), 0, None)) / (2 * np.pi * c * g + 1e-300)
    F = np.concatenate([[0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(g))]); F /= F[-1]
    return lambda x: np.interp(x, g, F)


def sig_batch(m, n, k, scale, fp16, gen):
    out = []
    for i in range(k):
        W = torch.randn((m, n), generator=gen, device=DEV, dtype=torch.float64) * scale
        if fp16:
            W = W.half().double()
        A = W @ W.T if m <= n else W.T @ W
        out.append(torch.linalg.eigvalsh(A).clamp_min(0).sqrt().flip(0).cpu().numpy())
    return out


def rms_table(rev):
    d = ROOT / "cache" / "s3" / MODEL / rev
    Z = [np.load(d / f"L{l:02d}.npz") for l in range(_C["n_layer"])]
    t = {M: float(np.mean([float(z[f"rms_{M}"]) for z in Z])) for M in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")}
    for M in "QKVO":   # per-head blocks share their full matrix's entries
        t[f"head_{M}"] = t[M]
    return t


def main():
    scales = {"final": rms_table("step143000"), "step0": rms_table("step0")}
    fp = ROOT / "results" / f"stage3_witness{mcfg.suffix()}.json"
    out = {"doc": __doc__, "scales": scales, "types": {}}
    if fp.exists():                      # resumable: keep finished types (same scales), redo the rest
        old = json.loads(fp.read_text())
        if old.get("scales") == scales:
            out["types"] = old["types"]
    if all(T in out["types"] for T in TYPES):
        print("witness complete; nothing to do"); return
    gen = torch.Generator(device=DEV).manual_seed(20260925)
    for T, (m, n, K) in TYPES.items():
        if T in out["types"]:
            continue
        R.check_stop()
        t0 = time.time()
        nmin, nmax = min(m, n), max(m, n)
        cdf = mp_cdf(nmin / nmax)
        res = {"shape": [m, n], "K": K, "runs": {}}
        sig_main = []
        for tag, scale_key, fp16, R_ in (("witness_fp16_final", "final", True, R_MAIN),
                                         ("check_fp64_final", "final", False, R_CHECK),
                                         ("check_fp16_step0", "step0", True, R_CHECK)):
            s = scales[scale_key][T]
            reps = []
            for r in range(R_):
                R.check_stop()
                sp = sig_batch(m, n, K, s, fp16, gen)
                if tag == "witness_fp16_final":
                    sig_main.extend(sp)
                reps.append({b: S.local_stats(sp, b) for b in S.BANDS})
            agg = {}
            for b in S.BANDS:
                for key in ("rt", "q_kde", "q_local"):
                    vals = np.array([rp[b][key] for rp in reps if rp[b][key] is not None], float)
                    agg[f"{b}:{key}"] = {"mean": float(vals.mean()), "sd": float(vals.std(ddof=1)) if len(vals) > 1 else None,
                                         "n": int(len(vals))}
                if b == "bulk":
                    for key in ("sigma2", "delta3"):
                        v = np.array([rp[b][key] for rp in reps], float)
                        agg[f"bulk:{key}"] = {"mean": v.mean(0).tolist(), "sd": v.std(0, ddof=1).tolist()}
            res["runs"][tag] = agg
        # margins + KS reference from the witness draws (s = scale, entries var s^2)
        s = scales["final"][T]
        Ep = s * (np.sqrt(m) + np.sqrt(n)); Em = s * abs(np.sqrt(m) - np.sqrt(n))
        smax = np.array([x[0] for x in sig_main]) / Ep
        smin = np.array([x[-1] for x in sig_main]) / Em if Em > 0 else None
        ks = []
        for x in sig_main:
            y = np.sort(x ** 2 / (nmax * s * s)); F = cdf(y); i = np.arange(1, len(y) + 1)
            ks.append(max((i / len(y) - F).max(), (F - (i - 1) / len(y)).max()))
        res["tau_plus"] = float(np.quantile(smax, 0.99))
        res["tau_minus"] = float(np.quantile(smin, 0.01)) if smin is not None else None
        res["ks95"] = float(np.quantile(ks, 0.95))
        res["n_draws"] = len(sig_main)
        w, c16, c0 = (res["runs"][k] for k in ("witness_fp16_final", "check_fp64_final", "check_fp16_step0"))
        res["G4_bulk_rt_fp16_minus_fp64"] = w["bulk:rt"]["mean"] - c16["bulk:rt"]["mean"]
        res["G4_lower_rt_fp16_minus_fp64"] = w["lower:rt"]["mean"] - c16["lower:rt"]["mean"]
        res["scale_invariance_bulk_rt"] = w["bulk:rt"]["mean"] - c0["bulk:rt"]["mean"]
        res["scale_invariance_bulk_q"] = w["bulk:q_kde"]["mean"] - c0["bulk:q_kde"]["mean"]
        res["scale_invariant"] = bool(abs(res["scale_invariance_bulk_rt"]) <= 0.002 and abs(res["scale_invariance_bulk_q"]) <= 0.03)
        res["beta1_not_poisson"] = bool(w["bulk:rt"]["mean"] >= 0.3863 + 0.10 and abs(res["G4_bulk_rt_fp16_minus_fp64"]) <= 0.01)
        out["types"][T] = res
        print(f"{T}: bulk rt {w['bulk:rt']['mean']:.4f}+-{w['bulk:rt']['sd']:.4f} q {w['bulk:q_kde']['mean']:.3f} "
              f"| G4 bulk {res['G4_bulk_rt_fp16_minus_fp64']:+.4f} lower {res['G4_lower_rt_fp16_minus_fp64']:+.4f} "
              f"| scale-inv {res['scale_invariant']} | tau+ {res['tau_plus']:.4f} ks95 {res['ks95']:.4f} "
              f"({time.time()-t0:.0f}s)", flush=True)
        R.durable_save(fp, lambda p: p.write_text(json.dumps(out, indent=1)))


if __name__ == "__main__":
    try:
        main()
    except R.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
