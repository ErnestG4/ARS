"""POST-HOC confound checks requested in review (2026-09-25 ~23:55). Descriptive; nothing here re-labels a sealed verdict.
(a) LR schedule (Pythia-1.4B config: Adam, lr 2e-4, warmup 0.01 x 143000 = 1430 steps, cosine to 2e-5 over 143000,
    GPT-NeoX AnnealingLR) -> LR integral per schedule interval, to set beside every turning point.
(b) Outlier count vs the moving MP edge: layer-mean tau+ * E+ (mp_fit_v2 scale) against sigma_max and sigma at
    ranks 50/100/200.
(c) Localisation coordinates, step 143000 and 8000: LEFT (output-space) top-8 vectors of Q/K/V: mass on rotary head
    dims (isotropic 0.25) and on the single heaviest head (isotropic 1/16); RIGHT (residual-space) top-8 vectors: mass
    on the 8 residual coordinates with the largest |LayerNorm gain| (isotropic 8/2048), and cross-matrix sharing of
    the heaviest residual coordinates.
(d) QK symmetric fraction for heads the induction score identifies (final-step induction > 0.3) vs all other heads.
(e) Population sink measures: mean attention to position 0, and the fraction of heads above 0.1/0.2/0.3/0.5.
"""
import json, math
from pathlib import Path
import numpy as np, pandas as pd
import remote_st as R
ROOT = Path(__file__).resolve().parent
S3 = ROOT / "cache" / "s3" / "pythia-1.4b"
df = pd.read_parquet(ROOT / "results" / "stage3_long.parquet")
steps = sorted(set(df.step))
out = {"doc": __doc__}

# (a)
W, T, LR0, LRmin = 1430, 143000, 2e-4, 2e-5
def lr(t):
    t = np.asarray(t, float)
    return np.where(t < W, LR0 * t / W, LRmin + (LR0 - LRmin) / 2 * (np.cos(np.pi * (t - W) / (T - W)) + 1))
ts = np.arange(0, T + 1)
cum = np.concatenate([[0], np.cumsum(lr(ts[:-1]))])
out["lr"] = {"warmup_end": W, "intervals": [{"from": a, "to": b, "steps": b - a, "lr_integral": float(cum[b] - cum[a]),
                                              "lr_at_to": float(lr(b))} for a, b in zip(steps[:-1], steps[1:])]}
print("(a) LR integral per interval:", [(i["from"], i["to"], f"{i['lr_integral']:.3g}") for i in out["lr"]["intervals"] if i["to"] <= 8000])

# (b)
wit = json.loads((ROOT / "results" / "stage3_witness.json").read_text())
rows = []
for s in steps:
    for M in ("O", "MLP_OUT", "Q", "K"):
        m, n = {"O": (2048, 2048), "Q": (2048, 2048), "K": (2048, 2048), "MLP_OUT": (2048, 8192)}[M]
        sc = df[(df.step == s) & (df.matrix == M) & (df.metric == "mp2_scale")].sort_values("layer").value.values
        cnt = df[(df.step == s) & (df.matrix == M) & (df.metric == "mp2_n_upper_outliers")].sort_values("layer").value.values
        sig = np.array([np.load(S3 / f"step{s}" / f"L{l:02d}.npz")[f"sig_{M}"] for l in range(24)])
        edge = wit["types"][M]["tau_plus"] * sc * (np.sqrt(m) + np.sqrt(n))
        rows.append({"step": s, "M": M, "count": cnt.mean(), "edge": edge.mean(), "sig_max": sig[:, 0].mean(),
                     "sig_r50": sig[:, 49].mean(), "sig_r100": sig[:, 99].mean(), "sig_r200": sig[:, 199].mean(),
                     "sig_median": np.median(sig, 1).mean()})
tb = pd.DataFrame(rows)
out["outlier_vs_edge"] = tb.to_dict("records")
print("(b)\n", tb[tb.M.isin(["O", "MLP_OUT"]) & tb.step.isin([512, 1000, 2000, 3000, 4000, 8000, 32000, 143000])].round(3).to_string(index=False))

# (c)
loc = {}
for rev in ("step8000", "step143000"):
    idx = R.index("EleutherAI/pythia-1.4b", rev)
    res = []
    for l in range(24):
        z = np.load(S3 / rev / f"L{l:02d}.npz")
        g1 = np.abs(R.fetch(idx, f"gpt_neox.layers.{l}.input_layernorm.weight")[0].astype(np.float64))
        topg = np.argsort(-g1)[:8]
        heavy = {}
        for M in ("Q", "K", "V"):
            U = z[f"U32_{M}"][:, :8].astype(np.float64) ** 2          # (2048 out, 8)
            Vr = z[f"V32_{M}"][:, :8].astype(np.float64) ** 2         # (2048 residual, 8)
            head_mass = U.reshape(16, 128, 8).sum(1)                  # (16, 8)
            rot = U.reshape(16, 128, 8)[:, :32].sum((0, 1)).mean()
            res.append({"layer": l, "M": M, "left_rotary_mass": float(rot),
                        "left_top_head_mass": float(head_mass.max(0).mean()),
                        "right_mass_on_top8_LNgain": float(Vr[topg].sum(0).mean()),
                        "right_top8_coord_mass": float(np.sort(Vr.sum(1))[::-1][:8].sum() / 8)})
            heavy[M] = set(np.argsort(-Vr.sum(1))[:8])
        res[-1]["QKV_shared_heavy_residual_coords"] = len(heavy["Q"] & heavy["K"] & heavy["V"])
        res[-1]["heavy_coords_in_LN_top8"] = len(heavy["Q"] & set(topg))
    r = pd.DataFrame(res)
    loc[rev] = r.to_dict("records")
    g = r.groupby("M")[["left_rotary_mass", "left_top_head_mass", "right_mass_on_top8_LNgain", "right_top8_coord_mass"]].mean()
    print(f"(c) {rev} (isotropic: rotary 0.25, top head 0.0625, LN-top8 0.0039, top8-coords 0.0039):\n", g.round(4).to_string())
    print("    per-layer Q/K/V shared heavy residual coords (of 8):", r.QKV_shared_heavy_residual_coords.dropna().astype(int).tolist(),
          "| Q-heavy coords among LN-gain top8:", r.heavy_coords_in_LN_top8.dropna().astype(int).tolist())
out["localisation"] = loc

# (d)
mk = np.load(S3 / "step143000" / "MARKERS.npz")["induction"]
ind_heads = {(int(l), int(h)) for l, h in zip(*np.where(mk > 0.3))}
nul = json.loads((ROOT / "results" / "stage3_circuit_null.json").read_text())["qk_sym_nr"]
q = df[(df.metric == "qk_sym_nr") & (df.matrix == "QK")].copy()
q["ind"] = [(int(l), int(h)) in ind_heads for l, h in zip(q.layer, q["head"])]
q["dev"] = (q.value - 0.5).abs()
tab = q.groupby(["step", "ind"]).agg(median=("value", "median"), med_absdev=("dev", "median"),
                                     frac_out=("value", lambda s: float(((s < nul["1"]) | (s > nul["99"])).mean()))).unstack("ind")
out["qk_induction_heads"] = {"heads": sorted(ind_heads), "table": json.loads(tab.to_json())}
print(f"(d) induction heads (final > 0.3): {len(ind_heads)} {sorted(ind_heads)}")
print(tab[tab.index.isin([0, 256, 512, 1000, 2000, 4000, 8000, 32000, 143000])].round(3).to_string())

# (e)
sk = []
for s in steps:
    m = np.load(S3 / f"step{s}" / "MARKERS.npz")["sink_mean"]
    sk.append({"step": s, "mean": float(m.mean()), **{f"frac>{t}": float((m > t).mean()) for t in (0.1, 0.2, 0.3, 0.5)}})
out["sink_population"] = sk
print("(e)\n", pd.DataFrame(sk).round(3).to_string(index=False))
(ROOT / "results" / "stage3_confounds.json").write_text(json.dumps(out, indent=1, default=float))
