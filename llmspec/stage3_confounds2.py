"""POST-HOC second-round review checks (2026-09-26 ~00:10). Descriptive.
(f) MP-fit validity over time: per matrix, the KS of sigma^2/(n_max s^2) to MP(c) at the mp_fit_v2 (median-matched)
    scale, against the G1 witness 95th percentile. Where the fit FAILS, "outlier vs MP edge" is undefined, and only
    top-k sigma (k = 1, 4, 16, 64) and a gap criterion are reported. Gap criterion: in descending sigma, the index of
    the largest RATIO sigma_i / sigma_{i+1} over i < 10% of n (the number of values before the largest gap).
(g) Head / rotary concentration of the top-8 LEFT vectors of Q, K, V at step 143000 (and 8000), against a
    WITHIN-HEAD RANDOM ROTATION null (each head block W_h -> R_h W_h, R_h Haar; keeps every head's spectrum and norm,
    scrambles its output directions; 3 draws). Also direct norms: the heaviest head's Frobenius share (vs 1/16), max /
    median head spectral norm, and the rotary rows' share of ||W||_F^2 (vs 0.25).
(h) Residual-side localisation on RAW W and on the LayerNorm-FOLDED W diag(g1) (the transform the model applies):
    top-8 right-vector mass on the 8 largest-|g1| coordinates (isotropic 8/2048), the heaviest-coordinate mass, and
    the Q/K/V sharing of the 8 heaviest residual coordinates.
Top vectors come from the fp64 Gram eigh (exact to working precision for the top of the spectrum).
"""
import json
from pathlib import Path
import numpy as np, pandas as pd, torch
import remote_st as R
ROOT = Path(__file__).resolve().parent
S3 = ROOT / "cache" / "s3" / "pythia-1.4b"
DEV = "cuda"
out = {"doc": __doc__}

# (f)
wit = json.loads((ROOT / "results" / "stage3_witness.json").read_text())
df = pd.read_parquet(ROOT / "results" / "stage3_long.parquet")
def mp_cdf(c):
    a, b = (1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2
    g = np.linspace(a, b, 40001); f = np.sqrt(np.clip((b - g) * (g - a), 0, None)) / (2 * np.pi * c * g + 1e-300)
    F = np.concatenate([[0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(g))]); return g, F / F[-1]
SH = {"Q": (2048, 2048), "K": (2048, 2048), "V": (2048, 2048), "O": (2048, 2048), "MLP_IN": (8192, 2048), "MLP_OUT": (2048, 8192)}
rows = []
for s in sorted(set(df.step)):
    for M, (m, n) in SH.items():
        nmax, nmin = max(m, n), min(m, n); g, F = mp_cdf(nmin / nmax); med_x = float(np.interp(0.5, F, g))
        ks, gapk, top = [], [], []
        for l in range(24):
            sig = np.load(S3 / f"step{s}" / f"L{l:02d}.npz")[f"sig_{M}"]
            sc = np.median(sig) / np.sqrt(nmax * med_x)
            x = np.sort(sig ** 2 / (nmax * sc * sc)); Fx = np.interp(x, g, F); i = np.arange(1, len(x) + 1)
            ks.append(max((i / len(x) - Fx).max(), (Fx - (i - 1) / len(x)).max()))
            kk = int(0.1 * len(sig)); r = sig[:kk] / sig[1:kk + 1]; gapk.append(int(np.argmax(r)) + 1)
            top.append([sig[0], sig[3], sig[15], sig[63]])
        ks = np.array(ks); top = np.array(top)
        rows.append({"step": s, "M": M, "ks_median": float(np.median(ks)), "frac_fit_fails": float((ks > wit["types"][M]["ks95"]).mean()),
                     "gap_count_median": float(np.median(gapk)), "s1": top[:, 0].mean(), "s4": top[:, 1].mean(),
                     "s16": top[:, 2].mean(), "s64": top[:, 3].mean()})
f = pd.DataFrame(rows); out["mp_fit_validity"] = f.to_dict("records")
print("(f) MP fit validity + top-k sigma (layer means):")
print(f[f.step.isin([0, 256, 512, 1000, 2000, 4000, 8000, 32000, 143000])].round(3).to_string(index=False))

# (g)(h)
gen = torch.Generator(device=DEV).manual_seed(11)
def haar(k, n):
    Z = torch.randn((k, n, n), generator=gen, device=DEV, dtype=torch.float64)
    Q, Rr = torch.linalg.qr(Z); return Q * torch.sign(torch.diagonal(Rr, dim1=1, dim2=2))[:, None, :]
def top_left(W, k=8):
    return torch.linalg.eigh(W @ W.T)[1][:, -k:]
def top_right(W, k=8):
    return torch.linalg.eigh(W.T @ W)[1][:, -k:]
res = {}
for rev in ("step8000", "step143000"):
    idx = R.index("EleutherAI/pythia-1.4b", rev)
    recs = []
    for L in range(24):
        R.check_stop()
        p = f"gpt_neox.layers.{L}."
        got = {k: a for k, a, _ in R.fetch_many(idx, [p + "attention.query_key_value.weight", p + "input_layernorm.weight"])}
        qkv = torch.from_numpy(got[p + "attention.query_key_value.weight"].astype(np.float64)).to(DEV).reshape(16, 3, 128, 2048)
        g1 = torch.from_numpy(got[p + "input_layernorm.weight"].astype(np.float64)).to(DEV)
        topg = set(torch.argsort(g1.abs(), descending=True)[:8].tolist())
        heavy = {"raw": {}, "fold": {}}
        for j, M in enumerate("QKV"):
            Wh = qkv[:, j]                                            # (16 heads, 128, 2048)
            W = Wh.reshape(2048, 2048)
            Ul = top_left(W) ** 2                                      # (2048, 8)
            hm = Ul.reshape(16, 128, 8).sum(1)
            rot = float(Ul.reshape(16, 128, 8)[:, :32].sum((0, 1)).mean())
            nl = [];  nr = []
            for _ in range(3):
                Wr = (haar(16, 128) @ Wh).reshape(2048, 2048)
                Un = top_left(Wr) ** 2
                nl.append(float(Un.reshape(16, 128, 8).sum(1).max(0).values.mean()))
                nr.append(float(Un.reshape(16, 128, 8)[:, :32].sum((0, 1)).mean()))
            hf = (Wh ** 2).sum((1, 2)); hs = torch.linalg.matrix_norm(Wh, ord=2)
            rec = {"layer": L, "M": M, "top_head_mass": float(hm.max(0).values.mean()), "top_head_mass_null": float(np.mean(nl)),
                   "rotary_mass": rot, "rotary_mass_null": float(np.mean(nr)),
                   "top_head_frob_share": float(hf.max() / hf.sum()), "head_specnorm_max_over_median": float(hs.max() / hs.median()),
                   "rotary_rows_frob_share": float((Wh[:, :32] ** 2).sum() / (Wh ** 2).sum())}
            for kind, Wx in (("raw", W), ("fold", W * g1)):
                Vr = top_right(Wx) ** 2
                w = Vr.sum(1)
                rec[f"{kind}_mass_on_LNtop8"] = float(Vr[list(topg)].sum(0).mean())
                rec[f"{kind}_heaviest8_mass"] = float(torch.sort(w, descending=True).values[:8].sum() / 8)
                heavy[kind][M] = set(torch.argsort(w, descending=True)[:8].tolist())
            recs.append(rec)
        for kind in ("raw", "fold"):
            recs[-1][f"{kind}_QKV_shared_heavy"] = len(heavy[kind]["Q"] & heavy[kind]["K"] & heavy[kind]["V"])
            recs[-1][f"{kind}_Q_heavy_in_LNtop8"] = len(heavy[kind]["Q"] & topg)
    r = pd.DataFrame(recs); res[rev] = r.to_dict("records")
    cols = ["top_head_mass", "top_head_mass_null", "rotary_mass", "rotary_mass_null", "top_head_frob_share",
            "head_specnorm_max_over_median", "rotary_rows_frob_share", "raw_mass_on_LNtop8", "fold_mass_on_LNtop8",
            "raw_heaviest8_mass", "fold_heaviest8_mass"]
    print(f"\n(g)(h) {rev} (isotropic: head 0.0625, rotary 0.25, LN-top8 0.0039, heaviest8 >= 0.0039):")
    print(r.groupby("M")[cols].mean().round(4).T.to_string())
    print("  shared heavy residual coords Q&K&V per layer  raw:", r.raw_QKV_shared_heavy.dropna().astype(int).tolist())
    print("                                              folded:", r.fold_QKV_shared_heavy.dropna().astype(int).tolist())
    print("  Q heavy coords in LN-gain top8  raw:", r.raw_Q_heavy_in_LNtop8.dropna().astype(int).tolist(), " folded:", r.fold_Q_heavy_in_LNtop8.dropna().astype(int).tolist())
out["head_rotary_ln"] = res
(ROOT / "results" / "stage3_confounds2.json").write_text(json.dumps(out, indent=1, default=float))
