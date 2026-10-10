"""The Stage 2 tapered statistic (cs4/G_S_DESIGN.md §1), as declared: in unit-mean-spacing coordinates x,
  S(c; b) = Σ_{i≠j} F(x_i − x_j) · W_b((x_i + x_j)/2 − c),   W_b(y) = exp(−π y²/b²),
F the R₂ family bump (primary (u, w) = (0.5, 0.3); pairs with |x_i − x_j| ≤ U_MAX = 3), V(b) = sample variance of S over
window centres spaced 3b apart (the full ±4σ window inside the data, σ = b/√(2π)), v(b) = V(b)/b, on the ladder
b ∈ {100, 300, 1000, 3000, 10⁴}; g = √(v(10⁴)/v(100)).

Overnight use (Will, queue item 5; descriptive bridge, no verdict): F1 zeros (seen: decoded at the Stage 1 read; unfolded
by the exact smooth count N̄) and the Stage 1 long-GUE sequences (already unit density) as the matched baseline.

  python tapered.py zeros BIN OUT        F1 bin (F1a..F1x) from ph2r2/data/platt_fresh
  python tapered.py gue NPY OUT          one unfolded GUE sequence (.npy)
  python tapered.py summary OUT
"""
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ph2r2"))
sys.path.insert(0, os.path.join(HERE, "..", "ph2s"))

U, W, U_MAX = 0.5, 0.3, 3.0
LADDER = (100, 300, 1000, 3000, 10_000)


def F(d):
    return np.exp(-(d - U) ** 2 / (2 * W * W)) + np.exp(-(d + U) ** 2 / (2 * W * W))


def pairs(x):
    """Midpoints and weights 2F(Δ) of all pairs i < j with Δ = x_j − x_i ≤ U_MAX (each unordered pair counted for both
    orders, as Σ_{i≠j})."""
    mids, wts = [], []
    k = 1
    while k < len(x):
        d = x[k:] - x[:-k]
        m = d <= U_MAX
        if not m.any():
            break
        mids.append(0.5 * (x[k:] + x[:-k])[m])
        wts.append(2 * F(d[m]))
        k += 1
    m = np.concatenate(mids)
    w = np.concatenate(wts)
    o = np.argsort(m)
    return m[o], w[o]


def window_sums(m, w, lo, hi, b):
    sig = b / math.sqrt(2 * math.pi)
    centres = np.arange(lo + 4 * sig, hi - 4 * sig, 3 * b)
    S = np.empty(len(centres))
    for k, c in enumerate(centres):
        i0, i1 = np.searchsorted(m, c - 5 * sig), np.searchsorted(m, c + 5 * sig)
        S[k] = np.sum(w[i0:i1] * np.exp(-math.pi * (m[i0:i1] - c) ** 2 / b ** 2))
    return S


def ladder(x):
    m, w = pairs(x)
    out = {}
    for b in LADDER:
        S = window_sums(m, w, x[0], x[-1], b)
        if len(S) >= 3:
            out[str(b)] = dict(n_windows=len(S), mean=float(S.mean()), var=float(S.var(ddof=1)),
                               v=float(S.var(ddof=1) / b), sums=S.tolist())
    return out


def zeros(binname, out):
    import r2prep as P
    import r2run as RR
    import s1lib as S1
    fname = S1.F1[binname][0]
    t = RR.read_platt_heights(os.path.join(HERE, "..", "ph2r2", "data", "platt_fresh", fname))
    x = np.asarray(P.nbar(t), float)
    res = dict(kind="zeros", bin=binname, file=fname, n=len(x), ladder=ladder(x))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, f"zeros_{binname}.json"), "w"))
    print(binname, {b: round(v["v"], 5) for b, v in res["ladder"].items()}, flush=True)


def gue(npy, out):
    x = np.load(npy)
    res = dict(kind="gue", file=os.path.basename(npy), n=len(x), ladder=ladder(x))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "gue_" + os.path.basename(npy).replace(".npy", ".json")), "w"))
    print(os.path.basename(npy), {b: round(v["v"], 5) for b, v in res["ladder"].items()}, flush=True)


def pooled(recs, b):
    """Pool window sums across records (each record's sums centred on its own mean), v = V/b, with SE."""
    devs = []
    for r in recs:
        if str(b) in r["ladder"]:
            s = np.array(r["ladder"][str(b)]["sums"])
            devs.append(s - s.mean())
    d = np.concatenate(devs)
    dof = len(d) - len(devs)
    V = float(np.sum(d ** 2) / dof)
    return V / b, V / b * math.sqrt(2 / dof), len(d)


def summary(out):
    Z = {json.load(open(f))["bin"]: json.load(open(f)) for f in sorted(glob.glob(os.path.join(out, "zeros_*.json")))}
    G = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(out, "gue_*L1000000*.json")))]
    rows = {}
    gv = {b: pooled(G, b) for b in LADDER}
    rows["GUE (Stage 1, 16 x 1e6)"] = {str(b): gv[b] for b in LADDER}
    for n, r in Z.items():
        rows[n] = {str(b): pooled([r], b) for b in LADDER}
    lines = ["# Tapered statistic on F1 (descriptive bridge; seen data) and the Stage 1 GUE baseline", "",
             "v(b) = Var_c S(c; b)/b ± SE (windows); g = √(v(10⁴)/v(100)).", "",
             "| series | " + " | ".join(f"v({b})" for b in LADDER) + " | g |", "|---|" + "---|" * (len(LADDER) + 1)]
    for name, row in rows.items():
        g = math.sqrt(row["10000"][0] / row["100"][0])
        lines.append(f"| {name} | " + " | ".join(f"{row[str(b)][0]:.4f} ± {row[str(b)][1]:.4f}" for b in LADDER) + f" | {g:.3f} |")
    open(os.path.join(out, "TAPERED_SUMMARY.md"), "w").write("\n".join(lines) + "\n")
    json.dump(rows, open(os.path.join(out, "tapered_summary.json"), "w"), indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    {"zeros": lambda: zeros(sys.argv[2], sys.argv[3]), "gue": lambda: gue(sys.argv[2], sys.argv[3]),
     "summary": lambda: summary(sys.argv[2])}[sys.argv[1]]()
