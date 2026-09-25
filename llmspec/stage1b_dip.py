"""Stage 1b (POST-HOC, declared as such 2026-09-25 after Stage 1 showed the sealed KDE rule counts tail specks):
Hartigan's dip test per head, whose null is ALL unimodal densities (heavy tails included).

calibrate  -> seals/stage1b_dip_calibration.json (committed BEFORE `apply` touches a real head)
  Unit: per-head sigma of a 128 x 2048 block, x = sigma / median (the dip is location-scale invariant anyway).
  Rule: a head is MULTIMODAL iff dip p < 0.01 (diptest's interpolated table p, uniform-null, conservative).
  FALSE-POSITIVE rate on the nearest confusables (matched shape, 2000 draws each):
    mp          Gaussian entries
    t2.5/t3/t4  Student-t entries (heavy-tailed, unimodal singular-value spectra)
    spiked1/3/10  Gaussian + rank-k signal, strengths U(0.6, 2.0) (BBP outliers detach; still one bulk)
    lognorm0.3/0.5  sigma drawn i.i.d. lognormal (smooth unimodal right tail)
  LICENCE: the dip rule is licensed only if EVERY confusable class has FPR <= 0.02. Otherwise Stage 1b reports
  NOT LICENSED and the Stage 1 question stays UNRESOLVED.
  POWER: two-component spectra x ~ w N(1, sd^2) + (1-w) N(1+d, sd^2), n = 128, 1000 reps,
    d in {0.1, 0.2, 0.3, 0.5}, sd in {0.03, 0.1}, w in {0.5, 0.8} -> P(p < 0.01). Reported with every result.
apply      -> results/stage1b_dip.json
  For each Stage 1 run x matrix type: the fraction of heads with p < 0.01, over (i) all 128 levels and
  (ii) levels >= 0.1 x median (the OLMo dead-row cluster excluded, as in A1). A matrix type SHOWS PEAKS iff the
  fraction is >= 0.10 AND binom P(X >= k | n, f0) < 1e-3, with f0 = max(0.01, worst confusable FPR).
  G0 at step 0 (with the sampling allowance the sealed G0 lacked): passes unless binom P(X >= k | n, f0) < 0.01.
"""
import json, sys
from pathlib import Path
import numpy as np
import torch
import diptest
from scipy.stats import binom

ROOT = Path(__file__).resolve().parent
SEAL = ROOT / "seals" / "stage1b_dip_calibration.json"
DEV = "cuda"
ALPHA = 0.01


def pvals(xs):
    return np.array([diptest.diptest(np.asarray(x, dtype=np.float64))[1] for x in xs])


def svals(W):
    return torch.linalg.svdvals(W).cpu().numpy()


def confusable(kind, n, seed, p=128, q=2048):
    g = torch.Generator(device=DEV).manual_seed(seed)
    out = []
    for i in range(0, n, 250):
        k = min(250, n - i)
        if kind == "mp":
            W = torch.randn((k, p, q), generator=g, device=DEV, dtype=torch.float64)
        elif kind.startswith("t"):
            nu = float(kind[1:])
            z = torch.randn((k, p, q), generator=g, device=DEV, dtype=torch.float64)
            chi = torch.distributions.Chi2(torch.tensor(nu, device=DEV, dtype=torch.float64)).sample((k, p, q))
            W = z / torch.sqrt(chi / nu)
        elif kind.startswith("spiked"):
            r = int(kind[6:])
            W = torch.randn((k, p, q), generator=g, device=DEV, dtype=torch.float64) / np.sqrt(q)
            u = torch.linalg.qr(torch.randn((k, p, r), generator=g, device=DEV, dtype=torch.float64))[0]
            v = torch.linalg.qr(torch.randn((k, q, r), generator=g, device=DEV, dtype=torch.float64))[0]
            th = 0.6 + 1.4 * torch.rand((k, r), generator=g, device=DEV, dtype=torch.float64)
            W = W + (u * th[:, None, :]) @ v.transpose(1, 2)
        elif kind.startswith("lognorm"):
            s = float(kind[7:])
            rng = np.random.default_rng(seed + i)
            out.append(np.exp(s * rng.standard_normal((k, p))))
            continue
        out.append(svals(W))
    sig = np.concatenate(out)
    return sig / np.median(sig, axis=1, keepdims=True)


def calibrate():
    res = {"rule": __doc__, "alpha": ALPHA, "fpr": {}, "power": {}}
    for j, kind in enumerate(["mp", "t2.5", "t3", "t4", "spiked1", "spiked3", "spiked10", "lognorm0.3", "lognorm0.5"]):
        x = confusable(kind, 2000, 100 + j)
        p = pvals(x)
        res["fpr"][kind] = {"n": len(p), "fpr": float((p < ALPHA).mean())}
        print("FPR", kind, res["fpr"][kind], flush=True)
    rng = np.random.default_rng(7)
    for d in (0.1, 0.2, 0.3, 0.5):
        for sd in (0.03, 0.1):
            for w in (0.5, 0.8):
                comp = rng.random((1000, 128)) < w
                x = np.where(comp, 1.0, 1.0 + d) + sd * rng.standard_normal((1000, 128))
                res["power"][f"d{d}_sd{sd}_w{w}"] = float((pvals(x) < ALPHA).mean())
    print("POWER", res["power"], flush=True)
    res["worst_fpr"] = max(v["fpr"] for v in res["fpr"].values())
    res["licensed"] = bool(res["worst_fpr"] <= 0.02)
    res["f0"] = max(0.01, res["worst_fpr"])
    SEAL.write_text(json.dumps(res, indent=1))
    print("worst FPR", res["worst_fpr"], "licensed", res["licensed"])


def apply():
    cal = json.loads(SEAL.read_text())
    f0 = cal["f0"]
    runs = [("olmo2-1b", "main", "final"), ("olmo2-1b", "stage1-step1907359-tokens4001B", "stage1_end"),
            ("olmo2-1b", "stage1-step0-tokens0B", "step0"), ("pythia-1.4b", "step143000", "final"),
            ("pythia-1.4b", "step0", "step0")]
    out = {"licensed": cal["licensed"], "f0": f0, "runs": {}}
    for model, rev, tag in runs:
        L = 16 if model.startswith("olmo") else 24
        Z = [np.load(ROOT / "cache" / "spectra" / model / rev / f"L{l:02d}.npz") for l in range(L)]
        r = {}
        for M in "QKVO":
            sig = np.concatenate([z[f"sig_head_{M}"] for z in Z])
            med = np.median(sig, 1)
            ok = med > 0
            xs = sig[ok] / med[ok, None]
            p_all = pvals(xs)
            p_trim = pvals([x[x >= 0.1] for x in xs])
            n = len(xs)
            v = {"n_heads": int(n), "n_zero_median": int((~ok).sum())}
            for name, p in (("all_levels", p_all), ("trim_nearzero", p_trim)):
                k = int((p < ALPHA).sum())
                v[name] = {"k": k, "frac": k / n, "binom_p": float(binom.sf(k - 1, n, f0)) if k else 1.0,
                           "shows_peaks": bool(k / n >= 0.10 and (binom.sf(k - 1, n, f0) if k else 1.0) < 1e-3)}
            if tag == "step0":
                v["G0_pass"] = bool((binom.sf(v["all_levels"]["k"] - 1, n, f0) if v["all_levels"]["k"] else 1.0) >= 0.01)
            r[M] = v
            print(model, tag, M, {kk: (vv["k"], round(vv["frac"], 3), vv["shows_peaks"]) for kk, vv in v.items()
                                  if isinstance(vv, dict)}, v.get("G0_pass", ""), flush=True)
        out["runs"][f"{model}:{tag}:{rev}"] = r
    (ROOT / "results" / "stage1b_dip.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"calibrate": calibrate, "apply": apply}[sys.argv[1]]()
