"""Phase 6.1 pre-read (PH6_SEAL 6.1 §7.1–7.2): known answers on the zeros and matched-size bands. No candidate is read.

  python preread61.py zeros_bands OUT [DRAWS]

- T1 on the zeros (G0-c set: first 30,000 zeros, zeros1, sha256-pinned): δ_n = (n − ½) − N̄(γ_n), N̄ = θ/π + 1 (exact
  Riemann–Siegel θ, mpmath); δ̄, block means (30 blocks of 1000), the block-to-block SD, the slope of δ_n on log γ_n and
  its block-jackknife SD; τ₁ = max(5·SD_blocks, 0.02) (D3).
- Matched-size ⟨r̃⟩ bands at W = 30,000 levels: Poisson; GOE/GUE/GSE from the Dumitriu–Edelman Hermite tridiagonal
  (β = 1, 2, 4), central window of a size-5W matrix (as ARS-RH Phase 1); band = [2.5, 97.5] percentiles of DRAWS draws.
  Labels: large-N constants (rtilde_refs.py, D4).
- The zeros' ⟨r̃⟩ (raw γ spacings; the ratio is locally unfolding-free) against each band; a picket fence (⟨r̃⟩ = 1).
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
from scipy.linalg import eigh_tridiagonal

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from rtilde_refs import LARGE_N  # noqa: E402

ZEROS1 = "/home/combust/fmexplorer/criticality_tool/data/odlyzko_zeros1.txt"
ZEROS1_SHA256 = "3436c916a7878261ac183fd7b9448c9a4736b8bbccf1356874a6ce1788541632"   # specarith/DATA_MANIFEST.md
W = 30_000


def rtilde(levels):
    s = np.diff(np.sort(levels))
    return float((np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])).mean())


def beta_window(Wn, beta, rng):
    n = 5 * Wn
    d = math.sqrt(2.0) * rng.standard_normal(n)
    b = np.sqrt(rng.chisquare(beta * np.arange(n - 1, 0, -1)))
    ev = eigh_tridiagonal(d, b, eigvals_only=True, select="i", select_range=(2 * Wn, 3 * Wn - 1))
    return np.sort(ev)


def zeros_bands(out, draws=200, seed=20261008):
    import mpmath as mp
    h = hashlib.sha256(open(ZEROS1, "rb").read()).hexdigest()
    if h != ZEROS1_SHA256:
        raise SystemExit(f"REFUSED: zeros1 sha256 {h} != pinned")
    z = np.loadtxt(ZEROS1)[:W]
    mp.mp.dps = 30
    nbar = np.array([float(mp.siegeltheta(g) / mp.pi + 1) for g in z])
    n = np.arange(1, W + 1)
    delta = (n - 0.5) - nbar
    blocks = delta.reshape(30, -1)
    bm = blocks.mean(axis=1)
    sd_blocks = float(bm.std(ddof=1))
    X = np.log(z)
    slope = float(np.polyfit(X, delta, 1)[0])
    jk = []
    for k in range(30):
        m = np.ones(W, bool)
        m[k * 1000:(k + 1) * 1000] = False
        jk.append(np.polyfit(X[m], delta[m], 1)[0])
    jk = np.array(jk)
    sd_slope = float(math.sqrt((30 - 1) / 30 * np.sum((jk - jk.mean()) ** 2)))
    t1 = dict(delta_bar=float(delta.mean()), sd_blocks=sd_blocks, sd_of_mean=sd_blocks / math.sqrt(30),
              tau1=max(5 * sd_blocks, 0.02), slope=slope, sd_slope_jackknife=sd_slope,
              tau1_slope=max(5 * sd_slope, 0.02), block_means=bm.tolist())
    t1["zeros_PASS"] = bool(abs(t1["delta_bar"]) <= t1["tau1"] and abs(slope) <= t1["tau1_slope"])
    print("T1 zeros:", {k: v for k, v in t1.items() if k != "block_means"}, flush=True)

    rng = np.random.default_rng(seed)
    bands = {}
    if draws == 0:                     # bands come from bands61.py (spot); merge them here
        bands = {k: {kk: vv for kk, vv in v.items() if kk != "values"}
                 for k, v in json.load(open(os.path.join(out, "bands61.json")))["bands"].items()}
        gens = {}
    else:
        gens = {"Poisson": lambda: np.cumsum(rng.exponential(1.0, W)),
                "GOE": lambda: beta_window(W, 1, rng), "GUE": lambda: beta_window(W, 2, rng),
                "GSE": lambda: beta_window(W, 4, rng)}
    for name, gen in gens.items():
        v = np.array([rtilde(gen()) for _ in range(draws)])
        bands[name] = dict(label_large_N=LARGE_N[name], mean=float(v.mean()), sd=float(v.std(ddof=1)),
                           band=[float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))], draws=draws)
        print(name, {k: (round(x, 5) if isinstance(x, float) else x) for k, x in bands[name].items()}, flush=True)
    rz = rtilde(z)
    inside = {k: bool(b["band"][0] <= rz <= b["band"][1]) for k, b in bands.items()}
    zsc = {k: (rz - b["mean"]) / b["sd"] for k, b in bands.items()}
    picket = rtilde(np.arange(W, dtype=float))
    res = dict(W=W, zeros_rtilde=rz, zeros_inside=inside, zeros_z_vs_band=zsc, picket_rtilde=picket, T1=t1, bands=bands)
    print("zeros <r~> =", round(rz, 5), "inside:", inside, "z:", {k: round(v, 2) for k, v in zsc.items()}, flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "preread61_zeros_bands.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "zeros_bands":
        zeros_bands(sys.argv[2], *(int(a) for a in sys.argv[3:]))
