"""Stage 1 existence check: apply the SEALED peak criterion (seals/stage1_peak_criterion.json)
to banked spectra. Written and committed before any real spectrum was examined.

Decision checkpoints (declared): OLMo = `main` (final, post stage-2); Pythia-1.4B = step143000.
Also reported: OLMo stage1-step1907359 (end of stage 1); step-0 of both = G0 empirical null.
Outputs: results/stage1_long.parquet (G5 columns), results/stage1_verdict.json, plots/stage1_*.png
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import binom
from scipy.integrate import quad
import peaks as P
import specs as S

ROOT = Path(__file__).resolve().parent
SEAL = json.loads((ROOT / "seals" / "stage1_peak_criterion.json").read_text())
RUNS = [("olmo2-1b", "main", "final"), ("olmo2-1b", "stage1-step1907359-tokens4001B", "stage1_end"),
        ("olmo2-1b", "stage1-step0-tokens0B", "step0"),
        ("pythia-1.4b", "step143000", "final"), ("pythia-1.4b", "step0", "step0")]
MATS = "QKVO"
EST = "stage1-analyze-v1"


def load(model, rev):
    d = ROOT / "cache" / "spectra" / model / rev
    assert (d / "DONE").exists(), f"spectra not banked: {d}"
    L = S.MODELS[model]["n_layer"]
    return [np.load(d / f"L{l:02d}.npz") for l in range(L)]


def mp_sigma_pdf(c):
    """MP singular-value density for aspect c = p/n <= 1 (entries var 1/n): lambda = s^2 has
    density sqrt((b-l)(l-a)) / (2 pi c l) on [a,b], a,b = (1 -/+ sqrt c)^2. Returns (pdf(s), median)."""
    a, b = (1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2
    fl = lambda l: np.sqrt(max((b - l) * (l - a), 0)) / (2 * np.pi * c * l)
    fs = lambda s: 2 * s * fl(s * s)
    lo, hi = np.sqrt(a), np.sqrt(b)
    tot = quad(fs, lo, hi, limit=200)[0]
    assert abs(tot - 1) < 1e-3, f"MP pdf does not integrate to 1 (c={c}): {tot}"
    grid = np.linspace(lo, hi, 20001)
    cdf = np.cumsum([fs(s) for s in grid]); cdf /= cdf[-1]
    med = float(grid[np.searchsorted(cdf, 0.5)])
    return fs, lo, hi, med


def rule_verdict(k, n, frac_min):
    p = float(binom.sf(k - 1, n, 0.01)) if k > 0 else 1.0
    return {"k": int(k), "n": int(n), "frac": k / n, "binom_p_null01": p,
            "shows_peaks": bool(k / n >= frac_min and p < 1e-3)}


def main():
    assert SEAL["all_checks_pass"], "seal checks did not pass; Stage 1 not licensed"
    uh, uf = SEAL["units"]["per_head"], SEAL["units"]["full_matrix"]
    rows, verdict, keep = [], {}, {}
    for model, rev, tag in RUNS:
        Ls = load(model, rev)
        step = rev
        v = {}
        for M in MATS:
            xs = P.normalise(np.concatenate([z[f"sig_head_{M}"] for z in Ls]))  # (L*H, d_head)
            H = Ls[0][f"sig_head_{M}"].shape[0]
            a, _, info_a = P.count_batch(xs, uh["h_shape"], uh["p_star_all"], uh["m_min"], keep_info=True)
            _, m = P.count_batch(xs, uh["h_shape"], uh["p_star_massive"], uh["m_min"])
            xf = P.normalise(np.stack([z[f"sig_full_{M}"] for z in Ls]))
            af, _ = P.count_batch(xf, uf["h_shape"], uf["p_star_all"], uf["m_min"])
            _, mf = P.count_batch(xf, uf["h_shape"], uf["p_star_massive"], uf["m_min"])
            keep[(model, tag, M)] = (xs, a, info_a, xf, af)
            for i in range(len(xs)):
                for met, val in (("n_modes_all", a[i]), ("n_modes_massive", m[i])):
                    rows.append((model, "base", step, i // H, M, i % H, "all", met, float(val), EST))
            for l in range(len(xf)):
                for met, val in (("n_modes_all", af[l]), ("n_modes_massive", mf[l])):
                    rows.append((model, "base", step, l, M, -1, "all", met, float(val), EST))
            grid = [json.loads(str(z[f"grid_{M}"])) for z in Ls]
            v[M] = {
                "per_head_primary": rule_verdict(int((a >= 2).sum()), len(a), 0.10),
                "per_head_secondary_massive": rule_verdict(int((m >= 2).sum()), len(m), 0.10),
                "full_primary": rule_verdict(int((af >= 2).sum()), len(af), 0.25),
                "full_secondary_massive": rule_verdict(int((mf >= 2).sum()), len(mf), 0.25),
                "unimodal_frac_all": float((a == 1).mean()), "unimodal_frac_massive": float((m == 1).mean()),
                "G4_grid": {"stored": grid[0]["stored"],
                            "min_frac_on_bf16": min(g.get("frac_on_bf16_grid", np.nan) for g in grid),
                            "min_frac_on_fp16": min(g.get("frac_on_fp16_grid", np.nan) for g in grid)},
            }
        prim = any(v[M]["per_head_primary"]["shows_peaks"] for M in "QKV")
        sec = any(v[M]["per_head_secondary_massive"]["shows_peaks"] for M in "QKV")
        full = any(v[M]["full_primary"]["shows_peaks"] for M in "QKV")
        if prim and not sec:
            label = "OUTLIER_MODES_ONLY"
        elif prim:
            label = "PEAKS"
        elif full:
            label = "PEAKS_AT_LAYER_UNIT_ONLY"
        else:
            label = "NO_PEAKS"
        v["model_label"] = label
        if tag == "step0":
            v["G0_pass"] = all(v[M]["unimodal_frac_all"] >= 0.985 and v[M]["unimodal_frac_massive"] >= 0.985
                               for M in MATS)
        v["flags"] = S.MODELS[model]["flags"]
        verdict[f"{model}:{tag}:{rev}"] = v
        print(model, tag, label, {M: (v[M]["per_head_primary"]["k"], v[M]["per_head_secondary_massive"]["k"],
                                      v[M]["full_primary"]["k"]) for M in MATS}, flush=True)

    o = verdict["olmo2-1b:final:main"]["model_label"]
    p = verdict["pythia-1.4b:final:step143000"]["model_label"]
    peaks = lambda lab: lab in ("PEAKS", "PEAKS_AT_LAYER_UNIT_ONLY")
    if not peaks(o):
        dec = "OLMO_NO_PEAKS: aim 1 dropped/deferred; record null replication of Diffract under the sealed criterion"
    elif not peaks(p):
        dec = "OLMO_ONLY: aim 1 proceeds on OLMo; architectural difference is a stated hypothesis"
    else:
        dec = "BOTH: aim 1 trajectory work moves to Pythia"
    g0 = {k: v.get("G0_pass") for k, v in verdict.items() if "step0" in k}
    verdict["_decision"] = {"olmo_final": o, "pythia_final": p, "stage1_decision": dec, "G0": g0,
                            "resolution_note": "per-head criterion resolves narrow peaks separated by >= ~0.12 "
                            "(sigma/median units); full-matrix unit is far coarser (h=%.3f)" % uf["h_shape"]}
    (ROOT / "results").mkdir(exist_ok=True)
    df = pd.DataFrame(rows, columns=["model", "variant", "step", "layer", "matrix", "head", "band", "metric",
                                     "value", "estimator_version"])
    df.to_parquet(ROOT / "results" / "stage1_long.parquet")
    (ROOT / "results" / "stage1_verdict.json").write_text(json.dumps(verdict, indent=1))
    print(json.dumps(verdict["_decision"], indent=1))
    plots(keep, uh, uf)


def plots(keep, uh, uf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = ROOT / "plots"; out.mkdir(exist_ok=True)
    fs_h, lo_h, hi_h, med_h = mp_sigma_pdf(128 / 2048)
    fs_f, lo_f, hi_f, med_f = mp_sigma_pdf(1.0 - 1e-9)
    bins = np.linspace(0, 3, 61)   # FIXED binning in x = sigma/median, all heads
    for (model, tag, M), (xs, a, info, xf, af) in keep.items():
        L = S.MODELS[model]["n_layer"]; H = S.MODELS[model]["n_head"]
        fig, axs = plt.subplots(L, H, figsize=(H * 1.1, L * 0.8), sharex=True)
        sg = np.linspace(lo_h, hi_h, 300)
        for i, x in enumerate(xs):
            ax = axs[i // H, i % H]
            ax.hist(np.clip(x, 0, 3), bins=bins, density=True, color="0.7")
            g, d = P.kde(x, uh["h_shape"])
            ax.plot(g, d, lw=0.6, color="C0" if a[i] < 2 else "C3")
            ax.plot(sg / med_h, [fs_h(s) * med_h for s in sg], lw=0.5, color="k", ls="--")
            ax.set_xlim(0, 3); ax.set_yticks([]); ax.tick_params(labelsize=4)
            if a[i] >= 2:
                ax.set_title(f"L{i//H}h{i%H} m={a[i]}", fontsize=4, color="C3", pad=1)
        fig.suptitle(f"{model} {tag} W_{M} per-head sigma/median (grey: fixed bins; line: sealed KDE, red = >=2 modes; "
                     f"dashed: MP c=1/16 median-matched)", fontsize=7)
        fig.savefig(out / f"stage1_{model}_{tag}_{M}_heads.png", dpi=110); plt.close(fig)
        fig, axs = plt.subplots(1, L, figsize=(L * 1.2, 1.4), sharey=True)
        sg = np.linspace(lo_f + 1e-6, hi_f - 1e-6, 300)
        for l, x in enumerate(xf):
            ax = axs[l]
            ax.hist(np.clip(x, 0, 4), bins=np.linspace(0, 4, 81), density=True, color="0.7")
            g, d = P.kde(x, uf["h_shape"])
            ax.plot(g, d, lw=0.6, color="C0" if af[l] < 2 else "C3")
            ax.plot(sg / med_f, [fs_f(s) * med_f for s in sg], lw=0.5, color="k", ls="--")
            ax.set_xlim(0, 4); ax.set_title(f"L{l}", fontsize=5); ax.tick_params(labelsize=4)
        fig.suptitle(f"{model} {tag} W_{M} full layer matrix", fontsize=7)
        fig.savefig(out / f"stage1_{model}_{tag}_{M}_full.png", dpi=110, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    main()
