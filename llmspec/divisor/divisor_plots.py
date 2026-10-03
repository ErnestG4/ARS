"""Divisor Harmonics v0 -- figures (brief §7). (a) per concept: P(n) with the Lorentzian fit, bars coloured by divisor
class d = N/gcd(n,N), bootstrap 5-95 % band of the null; (b) months and hours: projections onto each harmonic pair
(polygon families; aliasing illustration, NOT evidence). Reads results/divisor/<tag>_last_primary.json and the acts npz.

Usage: python3 divisor_plots.py results/divisor/pythia-1.4b_last_primary.json results/divisor/acts/pythia-1.4b.npz
"""
import json, math, pathlib, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import divisor_spectrum as S, templates as T

def main(res_json, acts_npz, outdir="plots/divisor"):
    R = json.load(open(res_json)); tag = R["tag"]; out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    cmap = plt.get_cmap("tab10")
    fig, axes = plt.subplots(1, len(R["concepts"]), figsize=(4.2 * len(R["concepts"]), 3.6))
    for ax, (name, r) in zip(axes, R["concepts"].items()):
        n = np.arange(1, len(r["P"]) + 1); dcl = np.array(r["dcl"]); cls = sorted(set(dcl.tolist()))
        col = {c: cmap(i % 10) for i, c in enumerate(cls)}
        ax.bar(n, r["P"], color=[col[c] for c in dcl], width=0.8)
        ax.plot(n, r["Lhat"], "k-", lw=1.2, label=f"Lorentzian fit σ={r['sigma']:.2f}")
        ax.set_yscale("log"); ax.set_xlabel("harmonic n"); ax.set_title(f"{name} (N={r['N']}, {r['role']})", fontsize=9)
        for c in cls:
            tag_c = f"d={c}" + ("" if 1 < c < r["N"] else " (trivial)")
            z = r["z"].get(str(c), r["z"].get(c)); p = r["p"].get(str(c), r["p"].get(c))
            ax.plot([], [], "s", color=col[c], label=f"{tag_c}: z={z:+.1f} p={p:.3g}")
        ax.legend(fontsize=6, loc="best")
    fig.suptitle(f"{tag}: item-axis power spectra at the primary layers {R['primary_layers_hidden_idx']} (read={R['read']})", fontsize=9)
    fig.tight_layout(); fig.savefig(out / f"{tag}_spectra.png", dpi=130); plt.close(fig)
    # polygon projections (months, hours)
    z = np.load(acts_npz, allow_pickle=False); L = int(z["layers"]); idx = S.primary_layers(L)
    for name in ("months", "hours"):
        key = f"{name}_{R['read']}"
        if key not in z.files: continue
        X = z[key][idx].mean(0).mean(0).astype(np.float64); X -= X.mean(0); N = X.shape[0]
        F = np.fft.fft(X, axis=0) / N
        ks = list(range(1, N // 2 + 1)); fig, axes = plt.subplots(1, len(ks), figsize=(2.6 * len(ks), 2.8))
        items = T.CONCEPTS[name][0]
        for ax, k in zip(np.atleast_1d(axes), ks):
            u, v = np.real(F[k]), np.imag(F[k])
            Q, _ = np.linalg.qr(np.stack([u, v], 1)) if np.linalg.norm(v) > 1e-12 else (np.stack([u / np.linalg.norm(u), np.zeros_like(u)], 1), None)
            P2 = X @ Q
            ax.plot(np.r_[P2[:, 0], P2[0, 0]], np.r_[P2[:, 1], P2[0, 1]], "-", color="0.7", lw=0.8)
            ax.scatter(P2[:, 0], P2[:, 1], c=np.arange(N), cmap="hsv", s=18)
            for i, it in enumerate(items):
                ax.annotate(it[:3], (P2[i, 0], P2[i, 1]), fontsize=5, alpha=0.8)
            ax.set_title(f"n={k}: d={N // math.gcd(k, N)}-gon", fontsize=8); ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
        fig.suptitle(f"{tag} {name}: projections onto each harmonic plane (aliasing geometry; not evidence)", fontsize=9)
        fig.tight_layout(); fig.savefig(out / f"{tag}_{name}_polygons.png", dpi=130); plt.close(fig)
    print(f"plots -> {out}/{tag}_*.png")

if __name__ == "__main__":
    main(*sys.argv[1:])
