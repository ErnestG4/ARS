"""Q4EXT Amendment 2 (Q4EXT_PREREG.md, sealed by Will 2026-10-04 as DESCRIPTIVE). Order: gate -> columns -> plots.

gate     Item 5 (runs FIRST): are the three Muon runs' initialisations distinct? Elementwise Pearson correlation of the
         step-0 checkpoints the runs actually started from (spot:~/llmspec_armb/ckpt/<arm>/step00000.pt, sha-verified),
         per layer and type: M0s1 (EleutherAI/pythia-70m step0) vs M0s2 (pythia-70m-seed1 step0) vs M0s3 (pythia-70m-seed2
         step0); A0 vs M0s1 is the known answer (same source -> 1.000). DISTINCT iff |corr| < 0.05 on every matrix.
         -> results/armb_q4ext_amend2_gate.json. If M0s3 vs M0s1 is NOT distinct, the one-draw Muon spread is relabelled
         "same-init rerun spread" (an order/nondeterminism floor), wherever it is quoted.
columns  Items 2-4, per checkpoint on the DW0 cadence (every 100 steps + the log steps), A0 and M0s1 to 10000, M0s3 to
         3000, per layer and type (Q, K, V, O, MLP_IN, MLP_OUT):
           sigma_1; row magnitude rm = ||W||_F / sqrt(rows) (rms row norm); coherence = sigma_1 / rm (Muown's
           factorisation sigma_1 = row-magnitude x row-coherence; CC's operationalisation, declared here); max row norm;
           stable rank of W - W_0 = ||dW||_F^2 / ||dW||_2^2;
           per head h: sigma_1(W_Q^h W_K^h^T) (64 x 64; Kimi K2's QK-clip quantity).
         -> cache/armb/<arm>/AM2_<t>.npz (resumable).
summary  Tables + plots: results/armb_q4ext_amend2.json, plots/armb_q4ext_amend2_*.png; Muon-only ceiling 0.2 sqrt(max(A,B))/wd
         (wd 0.1 sealed) and the e-fold (lr wd)^-1 = 1e4 drawn on the Muon sigma_1 panels; row 16 as a reference band (the ten
         AdamW reference runs' stable rank at the shared steps, from the B4 refs bank, vs the two Muon runs).
GPU (CkptArmb, as q4ext_extract.py dw0). DESCRIPTIVE ONLY.
"""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
ARMS = {"A0": 10000, "M0s1": 10000, "M0s3": 3000}
TYPES = ["Q", "K", "V", "O", "MLP_IN", "MLP_OUT"]
WD = 0.1                     # sealed (ARMB_PREREG.md:35; muon.py)


def gate():
    import torch
    import b4_extract as E
    cks = {a: E.CkptArmb(a, 0) for a in ("A0", "M0s1", "M0s2", "M0s3")}
    pairs = [("A0", "M0s1"), ("M0s1", "M0s2"), ("M0s1", "M0s3"), ("M0s2", "M0s3")]
    out = {"rule": "DISTINCT iff |corr| < 0.05 on every matrix; A0 vs M0s1 is the known answer (same init source -> 1.000)",
           "sha256": {a: c.sha256 for a, c in cks.items()}, "pairs": {}}
    for a, b in pairs:
        cs = []
        for L in range(E.NL):
            ma, mb = E.mats(cks[a].t, L), E.mats(cks[b].t, L)
            for M in TYPES:
                x, y = ma[M].flatten(), mb[M].flatten(); x = x - x.mean(); y = y - y.mean()
                cs.append(float((x @ y) / (x.norm() * y.norm())))
        cs = np.array(cs)
        out["pairs"][f"{a}_vs_{b}"] = {"min": float(cs.min()), "max": float(cs.max()), "max_abs": float(np.abs(cs).max()),
                                       "n": int(cs.size), "distinct": bool(np.abs(cs).max() < 0.05)}
        print(f"{a} vs {b}: corr min {cs.min():.4f} max {cs.max():.4f} -> {'DISTINCT' if np.abs(cs).max() < 0.05 else 'NOT DISTINCT'}", flush=True)
    for c in cks.values(): c.close()
    ka = out["pairs"]["A0_vs_M0s1"]["min"] > 0.999
    out["known_answer_pass"] = bool(ka)
    out["m0s3_init_distinct_from_m0s1"] = out["pairs"]["M0s1_vs_M0s3"]["distinct"]
    out["spread_label"] = ("Muon-side init+order spread (one draw)" if out["m0s3_init_distinct_from_m0s1"]
                           else "same-init rerun spread (order/nondeterminism floor), NOT an init spread")
    (ROOT / "results" / "armb_q4ext_amend2_gate.json").write_text(json.dumps(out, indent=1))
    print("GATE known answer", "PASS" if ka else "FAIL", "| M0s3 vs M0s1:", out["spread_label"], flush=True)
    return out


def columns(arms):
    import torch
    import b4_extract as E, q4ext_extract as QX
    QX.inject()
    H, DH = E.H, E.DH
    for arm in arms:
        d = E.CACHE / arm
        steps = QX.dw0_steps(arm)
        todo = [t for t in steps if not (d / f"AM2_{t:05d}.npz").exists()]
        if not todo:
            print(f"{arm}: nothing to do", flush=True); continue
        c0 = E.CkptArmb(arm, 0); m0 = {L: E.mats(c0.t, L) for L in range(E.NL)}
        for t in todo:
            E.R.check_stop()
            ck = E.CkptArmb(arm, t); res = {}
            for L in range(E.NL):
                mt = E.mats(ck.t, L)
                for M in TYPES:
                    W = mt[M]; s = torch.linalg.svdvals(W)
                    rn = W.norm(dim=1); rm = float(W.norm() / np.sqrt(W.shape[0]))
                    dW = W - m0[L][M]; sd = torch.linalg.svdvals(dW)
                    res[f"L{L:02d}_{M}_sigma1"] = np.array(float(s[0]))
                    res[f"L{L:02d}_{M}_rowmag"] = np.array(rm)
                    res[f"L{L:02d}_{M}_coherence"] = np.array(float(s[0]) / rm)
                    res[f"L{L:02d}_{M}_rownorm_max"] = np.array(float(rn.max()))
                    res[f"L{L:02d}_{M}_dW0_sr"] = np.array(float((sd ** 2).sum() / sd[0] ** 2) if float(sd[0]) > 0 else np.nan)
                Q = mt["Q"].reshape(H, DH, -1); K = mt["K"].reshape(H, DH, -1)
                res[f"L{L:02d}_QK_head_sigma1"] = np.array([float(torch.linalg.matrix_norm(Q[h] @ K[h].T, 2)) for h in range(H)])
            res["ckpt_sha256"] = np.array(ck.sha256); ck.close()
            E.R.durable_save(d / f"AM2_{t:05d}.npz", lambda p: np.savez(p, **res))
            print(f"{arm} AM2 step {t} done", flush=True)
        c0.close(); torch.cuda.empty_cache()


def summary():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    CACHE = ROOT / "cache" / "armb"; NL = 6
    gate_r = json.loads((ROOT / "results" / "armb_q4ext_amend2_gate.json").read_text())
    out = {"gate": {k: gate_r[k] for k in ("known_answer_pass", "m0s3_init_distinct_from_m0s1", "spread_label")}, "arms": {}}
    series = {}
    for arm in ARMS:
        fs = sorted((CACHE / arm).glob("AM2_*.npz")); ts = [int(f.stem[4:]) for f in fs]; rows = {}
        for t, f in zip(ts, fs):
            z = np.load(f); r = {}
            for M in TYPES:
                for q in ("sigma1", "rowmag", "coherence", "rownorm_max", "dW0_sr"):
                    r[f"{M}_{q}"] = float(np.nanmean([float(z[f"L{L:02d}_{M}_{q}"]) for L in range(NL)]))
            hk = np.concatenate([z[f"L{L:02d}_QK_head_sigma1"] for L in range(NL)])
            r["QK_head_sigma1_median"] = float(np.median(hk)); r["QK_head_sigma1_max"] = float(hk.max())
            rows[t] = r
        series[arm] = (ts, rows)
        if ts:
            out["arms"][arm] = {"n_steps": len(ts), "first": rows[ts[0]], "at_3000": rows.get(3000), "last_step": ts[-1], "last": rows[ts[-1]]}
    # reference band (item 6): ten AdamW reference runs' stable rank at the shared steps (B4 refs bank, cache/s3)
    band = {}
    for t in (512, 1000, 2000, 3000):
        vals = {M: [] for M in ("Q", "K")}
        for mdl in ["pythia-70m"] + [f"pythia-70m-seed{k}" for k in range(1, 10)]:
            dd = ROOT / "cache" / "s3" / mdl / f"step{t}"
            if not (dd / "L00.npz").exists(): continue
            for M in ("Q", "K"):
                srs = []
                for L in range(NL):
                    z = np.load(dd / f"L{L:02d}.npz"); key = f"sig_{M}" if f"sig_{M}" in z.files else None
                    if key is None: continue
                    s = z[key]; srs.append(float((s ** 2).sum() / s[0] ** 2))
                if srs: vals[M].append(float(np.mean(srs)))
        muon = {}
        for arm in ("M0s1", "M0s2"):
            dd = CACHE / arm / f"step{t:05d}"
            if (dd / "L00.npz").exists():
                muon[arm] = {M: float(np.mean([float((lambda s: (s ** 2).sum() / s[0] ** 2)(np.load(dd / f"L{L:02d}.npz")[f"sig_{M}"])) for L in range(NL)])) for M in ("Q", "K")}
        band[t] = {"adamw_ref_n": len(vals["Q"]), "adamw_ref_minmax": {M: ([min(v), max(v)] if v else None) for M, v in vals.items()}, "muon": muon}
    out["row16_reference_band"] = band
    (ROOT / "results" / "armb_q4ext_amend2.json").write_text(json.dumps(out, indent=1, default=float))
    # plots
    (ROOT / "plots").mkdir(exist_ok=True)
    for q, title in (("sigma1", "sigma_1"), ("rowmag", "row magnitude (rms row norm)"), ("coherence", "coherence = sigma_1 / row magnitude"), ("dW0_sr", "stable rank of W - W0")):
        fig, axes = plt.subplots(2, 3, figsize=(13, 6.5))
        for ax, M in zip(axes.ravel(), TYPES):
            for arm, (ts, rows) in series.items():
                if ts: ax.plot(ts, [rows[t][f"{M}_{q}"] for t in ts], "o-", ms=2, lw=1, label=arm)
            if q == "sigma1":
                A, B = (2048, 512) if M.startswith("MLP") else (512, 512)
                ax.axhline(0.2 * np.sqrt(max(A, B)) / WD, color="tab:red", ls=":", lw=1, label="Muon-only ceiling 0.2√max/wd (PARTIAL)")
                ax.axvline(1.0 / (1e-3 * WD), color="0.5", ls="--", lw=0.8, label="(lr·wd)⁻¹ = 1e4 (Muon)")
            ax.set_xscale("symlog", linthresh=100); ax.set_title(f"{M}: {title}", fontsize=9)
        axes[0, 0].legend(fontsize=6); fig.suptitle(f"Q4EXT Amendment 2 (descriptive): {title}; spread label: {out['gate']['spread_label']}", fontsize=9)
        fig.tight_layout(); fig.savefig(ROOT / "plots" / f"armb_q4ext_amend2_{q}.png", dpi=120); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    for arm, (ts, rows) in series.items():
        if ts: ax.plot(ts, [rows[t]["QK_head_sigma1_median"] for t in ts], "-", label=f"{arm} median"); ax.plot(ts, [rows[t]["QK_head_sigma1_max"] for t in ts], ":", label=f"{arm} max")
    ax.set_xscale("symlog", linthresh=100); ax.set_title("per-head σ₁(W_Q^h W_K^hᵀ)"); ax.legend(fontsize=7); fig.tight_layout()
    fig.savefig(ROOT / "plots" / "armb_q4ext_amend2_qkhead.png", dpi=120); plt.close(fig)
    print("WROTE results/armb_q4ext_amend2.json + plots/armb_q4ext_amend2_*.png AMEND2_SUMMARY_DONE")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("gate", "all"):
        g = gate()
        if not g["known_answer_pass"]:
            print("GATE KNOWN ANSWER FAILED: stopping before columns"); sys.exit(2)
    if cmd in ("columns", "all"): columns(list(ARMS))
    if cmd in ("summary", "all"): summary()
    print("AMEND2_DONE", cmd)
