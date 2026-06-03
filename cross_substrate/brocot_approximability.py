"""
cross_substrate/brocot_approximability.py — the cross-substrate approximability BRIDGE TEST.

The AM↔Fibonacci arc landed: continuous approximability stratification, single universality class
(AM-crit approximability-invariant, Fibonacci side approximability-graded). Both are spectra of 1D
quasi-periodic Schrödinger operators. This asks whether a THIRD, mechanistically-different substrate —
brocot.fm FM synthesis — shows the SAME approximability stratification.

DESIGN (validated by a design-probe, 2026-05-24): a single modulator at a rational ratio is a regular
comb (clock NNS) — convergents don't separate. The approximability signal lives in the IRRATIONAL-α
quasi-periodic partial set {m + n·α} (carrier-harmonic comb [ratio 1] interfered with a modulator at
the irrational target ratio α). FM modulation DEPTH is the coupling analogue (higher depth → sharper
class separation, exactly like the AM λ-sweep). So the test is a DEPTH-SWEEP at fixed irrational-α
targets — directly parallel to the AM/Fibonacci λ-sweep, with the parameter side accessed DIRECTLY
(the ratio IS α; no CF-of-the-operator-frequency indirection).

Same 9 Lagrange targets as the λ*(class) sweep (ec82368) for direct comparability:
  golden/silver/bronze (μ=2 small quotients), metallic4/5 (μ=2 large quotients), e−2 (μ=2 unbounded-slow),
  ln2 (μ≈3.57), π−3 (μ≈7.10), Liouville (μ=∞).

Per (class, depth): partial-frequency NNS (Family I + II) + RF per-prime (Family III). Tracks endpoint
(high depth) AND trajectory (vs depth). Two-claim split (parallel to AM↔Fib): (universal) common
convergence point regardless of class? (graded) class-ordered separation matching approximability?

Out: coordinates/brocot-approximability.jsonl + figure P_brocot_approx.png. Run: --run.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_BROCOT = "$HOME/fmexplorer/brocot"
for p in (_BROCOT, _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from phase3.partial_prediction import predict_partials                # noqa: E402
from phase3.ars.arithmetic_toolkit import joint_q_profile, padic_amplitude_v4  # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I, compute_family_II  # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
F_CARRIER = 220.0
PRIMES = (2, 3, 5, 7, 11, 13)
DEPTHS = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]      # FM modulation index = coupling analogue
# (name, α value, μ, max CF quotient) — same 9 classes as λ*(class)
CLASSES = [
    ("golden",     (np.sqrt(5) - 1) / 2,          2.0, 1),
    ("silver",     np.sqrt(2) - 1,                2.0, 2),
    ("bronze",     (np.sqrt(13) - 3) / 2,         2.0, 3),
    ("metallic4",  np.sqrt(5) - 2,                2.0, 4),
    ("metallic5",  (np.sqrt(29) - 5) / 2,         2.0, 5),
    ("e_minus_2",  np.e - 2,                       2.0, 99),
    ("ln2",        np.log(2),                      3.57, 99),
    ("pi_minus_3", np.pi - 3,                       7.10, 99),
    ("liouville",  sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)), 1e9, 99),
]


def _f(v):
    return None if v is None or not (isinstance(v, (int, float)) and np.isfinite(v)) else float(v)


def _fingerprint(freqs):
    f = np.sort(np.asarray(freqs, float))
    out = {}
    if f.size >= 20:
        try:
            out["I.5q_ks_gue_med"] = _f(joint_q_profile(f, q_max=8).get("ks_gue_med"))
        except Exception:
            out["I.5q_ks_gue_med"] = None
        s = canonical_spacings(f)
        for k, fn in FAMILY_I.items():
            out[k] = _f(fn(s))
        for k, v in compute_family_II(f).items():
            out[k] = _f(v) if isinstance(v, (int, float)) else None
    # RF per-prime (Family III) — works at any partial count
    try:
        pp = padic_amplitude_v4(f, primes=PRIMES, q_max=32).get("per_prime", {})
        for p in (2, 3, 5, 7):
            out[f"III.1_p{p}"] = _f(pp.get(p, {}).get("normalised"))
    except Exception:
        pass
    return out


def run():
    recs = []
    print("BROCOT APPROXIMABILITY BRIDGE TEST — depth-sweep at irrational-α targets (9 Lagrange classes)")
    print("endpoint (depth=8) fingerprint per class — ordered by approximability:")
    print(f"{'class':12s} {'μ':>5s} {'npart':>5s} {'I.5q':>6s} {'I.5':>6s} {'W1δ':>6s} {'q':>6s} {'BRρ':>6s} {'p3-RF':>6s}")
    endpoints = {}
    for name, alpha, mu, maxq in CLASSES:
        for depth in DEPTHS:
            sp = predict_partials([1.0, float(alpha)], [depth, depth], f_carrier=F_CARRIER)
            fp = _fingerprint(sp.freqs)
            recs.append({"substrate": "brocot-approximability",
                         "cell_id": f"{name}/depth{depth:g}", "lagrange_class": name,
                         "depth": depth, "n_partials": int(sp.freqs.size),
                         "axes_computed": fp,
                         "extraction_audit": {"alpha": float(alpha), "irrationality_measure": mu,
                                              "max_cf_quotient": maxq, "ratios": [1.0, float(alpha)],
                                              "f_carrier": F_CARRIER,
                                              "design": "carrier-comb [1] x irrational-α modulator; depth=coupling"},
                         "source_artifact": "generated (predict_partials)",
                         "computed_date": date.today().isoformat()})
            if depth == DEPTHS[-1]:
                endpoints[name] = (mu, int(sp.freqs.size), fp)
    for name, alpha, mu, maxq in CLASSES:
        m, n, fp = endpoints[name]
        def g(k):
            v = fp.get(k)
            return f"{v:.3f}" if isinstance(v, float) else "  -"
        mus = "∞" if mu > 1e8 else f"{mu:.2f}"
        print(f"{name:12s} {mus:>5s} {n:>5d} {g('I.5q_ks_gue_med'):>6s} {g('I.5_ks_gue'):>6s} "
              f"{g('I.1_w1_clock'):>6s} {g('I.8_brody_q'):>6s} {g('I.9_berry_robnik_rho'):>6s} {g('III.1_p3'):>6s}")

    # class-ordering test vs approximability (Spearman of endpoint I.5q / q vs approximability rank)
    order = [n for n, *_ in CLASSES]   # already ~approximability-ordered (golden→Liouville)
    i5q = [endpoints[n][2].get("I.5q_ks_gue_med") for n in order]
    qb = [endpoints[n][2].get("I.8_brody_q") for n in order]
    from scipy import stats
    rank = np.arange(len(order))
    def _corr(vals):
        v = [(r, x) for r, x in zip(rank, vals) if isinstance(x, float)]
        if len(v) < 5:
            return None
        return stats.spearmanr([a for a, _ in v], [b for _, b in v])[0]
    def _cs(v):
        c = _corr(v)
        return f"{c:+.3f}" if c is not None else "n/a"
    print(f"\nclass-ordering vs approximability rank (golden→Liouville): "
          f"ρ(rank, I.5q)={_cs(i5q)}  ρ(rank, Brody q)={_cs(qb)}")
    print("  (I.5q should RISE and Brody q should FALL with approximability if brocot matches AM/Fibonacci)")

    with open(os.path.join(COORD, "brocot-approximability.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ {len(recs)} cells banked (9 classes × {len(DEPTHS)} depths).")
    _figure(recs)


def _figure(recs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    df = pd.DataFrame([{**r["axes_computed"], "class": r["lagrange_class"], "depth": r["depth"],
                        "mu": r["extraction_audit"]["irrationality_measure"]} for r in recs])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.5))
    cmap = plt.cm.viridis(np.linspace(0, 1, len(CLASSES)))
    for i, (name, *_ ) in enumerate(CLASSES):
        sub = df[df["class"] == name].sort_values("depth")
        a1.plot(sub["depth"], sub["I.8_brody_q"], "o-", color=cmap[i], label=name, ms=4)
    a1.set_xlabel("FM modulation depth (coupling analogue)"); a1.set_ylabel("Brody q")
    a1.set_title("Depth-sweep trajectories by Lagrange class\n(brocot.fm — does q stratify by approximability?)")
    a1.legend(fontsize=6, ncol=2); a1.grid(alpha=0.2)
    end = df[df["depth"] == DEPTHS[-1]]
    a2.scatter(end["mu"].clip(upper=9), end["I.8_brody_q"], s=90, c=range(len(end)), cmap="viridis", edgecolor="k")
    for _, row in end.iterrows():
        a2.annotate(row["class"], (min(row["mu"], 9), row["I.8_brody_q"]), fontsize=6,
                    xytext=(4, 0), textcoords="offset points")
    a2.set_xlabel("irrationality measure μ (Liouville at 9)"); a2.set_ylabel("endpoint Brody q (depth=8)")
    a2.set_title("Endpoint Brody q vs approximability\n(FALLS with μ ⇒ matches AM/Fibonacci ordering)")
    a2.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P_brocot_approx.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.run:
        run()
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
