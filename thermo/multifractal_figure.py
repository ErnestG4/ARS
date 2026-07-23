"""
thermo/multifractal_figure.py — plot the Gauss-map Lyapunov spectrum L(alpha) from
thermo/multifractal_measured.json, with its three exact landmarks marked.

Run:  python3 thermo/multifractal_figure.py   ->   thermo/multifractal_spectrum.png
"""
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    d = json.load(open(os.path.join(HERE, "multifractal_measured.json")))
    pts = [(float(c["alpha"]), float(c["L"])) for c in d["curve"]]
    # keep the physical branch (L in [0,1], alpha finite); the sweep is already ordered by s
    pts = [(a, L) for a, L in pts if -0.05 <= L <= 1.02 and a < 60]
    pts.sort()
    xs, ys = zip(*pts)

    phi = (1 + math.sqrt(5)) / 2
    alpha_min = 2 * math.log(phi)
    alpha_typ = math.pi ** 2 / (6 * math.log(2))

    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.plot(xs, ys, "-", color="#2b6cb0", lw=2, zorder=3, label="L(α) = dim_H {x : λ(x)=α}")

    # landmarks
    ax.scatter([alpha_typ], [1.0], color="#c53030", zorder=5, s=55)
    ax.annotate(r"peak: $(\pi^2/6\ln 2,\ 1)$" + f"\n({alpha_typ:.4f}, 1)",
                (alpha_typ, 1.0), textcoords="offset points", xytext=(10, -6), fontsize=9)
    ax.axvline(alpha_min, color="#718096", ls=":", lw=1.2, zorder=1)
    ax.annotate(r"golden edge $2\ln\varphi$" + f"\n{alpha_min:.4f}", (alpha_min, 0.12),
                textcoords="offset points", xytext=(8, 0), fontsize=9, color="#4a5568")
    ax.axhline(0.5, color="#38a169", ls="--", lw=1.2, zorder=1)
    ax.annotate("Good asymptote L → 1/2  (α → ∞)", (0.62 * max(xs), 0.5),
                textcoords="offset points", xytext=(0, 6), fontsize=9, color="#276749")

    ax.set_xlabel("Lyapunov exponent  α")
    ax.set_ylabel("L(α)  =  Hausdorff dimension")
    ax.set_title("Lyapunov multifractal spectrum of the Gauss map\n"
                 "(parametric from the gated pressure P(s); three exact landmarks)")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(alpha_min - 0.15, 1.02 * max(xs))
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    out = os.path.join(HERE, "multifractal_spectrum.png")
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main()
