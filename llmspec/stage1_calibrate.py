"""Stage 1 peak criterion: MP-calibrated KDE (Will, 2026-09-25, v1.1 §8.1 answer).

Run BEFORE any real weights are examined. Output: seals/stage1_peak_criterion.json.

Rule (declared here, frozen by the seal):
  x = sigma / median(sigma) per spectrum; Gaussian KDE with a FIXED bandwidth h_shape
  (mean Silverman bandwidth over MP null draws of that shape), grid step h/8 in x units;
  a mode is a KDE local max with prominence >= p x max density.
  PRIMARY (the rule Will approved): count ALL modes; p*_all = smallest grid value with
    P(n_modes == 1) >= 0.99 on calibration set A (Gaussian fp64).
  SECONDARY (declared refinement, reported alongside, never substituted): a mode is MASSIVE if
    its basin (between adjacent density minima) holds >= m_min points, m_min = max(5, 0.02 n);
    p*_massive calibrated the same way on the massive count. Purpose: tell narrow multi-point
    peaks (aim 1) from isolated BBP outliers (aim 2). A primary 'peaks' verdict carried only by
    modes the secondary rule rejects is labelled OUTLIER_MODES_ONLY.
  If p* sits on the grid floor (0.0) the flag p_star_on_floor is set: the criterion is then
  "any local max" and its specificity comes from h alone (reported, not hidden).
  POWER (the criterion must be able to fire): two-component spectra, n points i.i.d. from
  equal-weight Gaussians of width w at 1 -/+ delta/2 (x units), detection = P(>=2 modes) per
  rule, over delta x w. The minimum resolvable separation is reported with the seal.
  Holdout B and every variant (bf16/fp16 grid, truncated-normal, uniform entries) must give
  P(==1) >= 0.985 for both rules.
Units: per-head block (128 x 2048; OLMo 2 1B and Pythia-1.4B share it) = primary;
       full layer matrix (2048 x 2048) = secondary (Diffract's unit is ambiguous).
"""
import json, sys, time
from pathlib import Path
import numpy as np
import torch
import peaks as P

import os
OUT = Path(__file__).resolve().parent / "seals" / os.environ.get("SEAL_OUT", "stage1_peak_criterion.json")
PGRID = np.round(np.concatenate([[0.0, 1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 3e-3], np.arange(0.005, 0.1, 0.005),
                                 np.arange(0.1, 0.51, 0.02)]), 5)


def null_spectra(shape, n, seed, variant="gauss"):
    g = torch.Generator(device=P.DEV).manual_seed(seed)
    out = []
    bs = max(1, int(2 ** 26 // (shape[0] * shape[1])))
    for i in range(0, n, bs):
        k = min(bs, n - i)
        W = torch.randn((k, *shape), generator=g, device=P.DEV, dtype=torch.float64)
        if variant == "trunc2":   # truncated normal at +-2 sd (resample-free approx: clip -> redraw)
            bad = W.abs() > 2
            while bad.any():
                W[bad] = torch.randn(int(bad.sum()), generator=g, device=P.DEV, dtype=torch.float64)
                bad = W.abs() > 2
        elif variant == "uniform":
            W = (torch.rand((k, *shape), generator=g, device=P.DEV, dtype=torch.float64) - 0.5) * np.sqrt(12)
        W = W * 0.02
        if variant == "bf16":
            W = W.to(torch.bfloat16).to(torch.float64)
        elif variant == "fp16":
            W = W.to(torch.float16).to(torch.float64)
        out.append(P.singvals(W))
    return P.normalise(np.concatenate(out))


def scan(xs, h, m_min):
    KD = [P.kde(x, h) for x in xs]
    tab = {}
    for p in PGRID:
        a = np.empty(len(xs), int); m = np.empty(len(xs), int)
        for i, (g, d) in enumerate(KD):
            a[i], m[i], _ = P.modes(g, d, xs[i], p, m_min)
        tab[float(p)] = {"P_all_eq1": float((a == 1).mean()), "P_massive_eq1": float((m == 1).mean())}
    return tab


def power(n, h, p_all, p_mass, m_min, reps=400, seed=7):
    rng = np.random.default_rng(seed)
    out = {}
    for w in (0.01, 0.03):
        for delta in (0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.20, 0.30):
            X = np.where(rng.random((reps, n)) < 0.5, 1 - delta / 2, 1 + delta / 2) + w * rng.standard_normal((reps, n))
            a, _ = P.count_batch(X, h, p_all, m_min)
            _, m = P.count_batch(X, h, p_mass, m_min)
            out[f"d{delta:.2f}_w{w}"] = {"P_all_ge2": float((a >= 2).mean()), "P_massive_ge2": float((m >= 2).mean())}
    return out


def main():
    res = {"rule": __doc__, "units": {}}
    for unit, shape, nA, nB, nV in [("per_head", (128, 2048), 5000, 5000, 1000),
                                    ("full_matrix", (2048, 2048), 300, 300, 100)]:
        t = time.time()
        n = shape[0]
        m_min = max(5, int(np.ceil(0.02 * n)))
        A = null_spectra(shape, nA, 1)
        h = float(P.silverman(A).mean())
        tabA = scan(A, h, m_min)
        pick = lambda key: min([float(p) for p in PGRID if tabA[float(p)][key] >= 0.99], default=None)
        p_all, p_mass = pick("P_all_eq1"), pick("P_massive_eq1")
        print(unit, "h", h, "p*_all", p_all, "p*_massive", p_mass, f"{time.time()-t:.0f}s", flush=True)
        r = {"shape": shape, "n_calibA": nA, "m_min": m_min, "h_shape": h,
             "p_star_all": p_all, "p_star_massive": p_mass,
             "scanA": {str(k): v for k, v in tabA.items()}, "checks": {}}
        if p_all is not None and p_mass is not None:
            for name, seed, var, nn in [("holdout_gauss", 2, "gauss", nB), ("bf16", 3, "bf16", nV),
                                        ("fp16", 4, "fp16", nV), ("trunc2", 5, "trunc2", nV),
                                        ("uniform", 6, "uniform", nV)]:
                X = null_spectra(shape, nn, seed, var)
                a, _ = P.count_batch(X, h, p_all, m_min)
                _, m = P.count_batch(X, h, p_mass, m_min)
                r["checks"][name] = {"n": nn, "P_all_eq1": float((a == 1).mean()),
                                     "P_all_ge2": float((a >= 2).mean()),
                                     "P_massive_eq1": float((m == 1).mean()),
                                     "P_massive_ge2": float((m >= 2).mean()),
                                     "pass": bool((a == 1).mean() >= 0.985 and (m == 1).mean() >= 0.985)}
                print(" ", name, r["checks"][name], flush=True)
            r["power"] = power(n, h, p_all, p_mass, m_min)
            print("  power", {k: v for k, v in r["power"].items() if k.endswith("w0.01")}, flush=True)
        r["p_star_on_floor"] = {"all": p_all == 0.0, "massive": p_mass == 0.0}
        res["units"][unit] = r
    res["decision_rule"] = {
        "per_matrix_type_primary": "per-head unit, PRIMARY (all-modes) rule: matrix type 'shows peaks' iff fraction of heads with "
        ">=2 modes >= 0.10 AND binomial P(X>=k | n_heads, 0.01) < 1e-3",
        "per_matrix_type_secondary": "full-matrix unit, PRIMARY rule: 'shows peaks' iff >= 25% of layers have >=2 "
        "modes AND binomial P(X>=k | n_layers, 0.01) < 1e-3",
        "model": "model 'shows peaks' iff any of Q,K,V shows peaks at the primary unit; if only the "
        "secondary unit shows peaks, verdict = PEAKS_AT_LAYER_UNIT_ONLY and aim 1 proceeds at that unit",
        "secondary": "the same two rules are evaluated with the massive-mode count at p*_massive and "
        "reported; primary-yes/secondary-no = OUTLIER_MODES_ONLY",
        "G0_empirical": "step-0 checkpoints must reproduce >= 0.985 unimodal per head under both rules; "
        "else the criterion is suspect, not the weights",
    }
    res["all_checks_pass"] = all(c["pass"] for u in res["units"].values() for c in u["checks"].values()) \
        and all(u["p_star_all"] is not None and u["p_star_massive"] is not None for u in res["units"].values())
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1))
    print("all_checks_pass", res["all_checks_pass"])


if __name__ == "__main__":
    main()
