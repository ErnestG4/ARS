"""
cross_substrate/cf_discriminator.py — does brocot read CF BOUNDEDNESS or QUADRATICITY?

cf_mechanism.py confirmed the split (brocot Brody q STEPS on the bounded/quadratic-vs-transcendental CF
binary; operator D_box is CONTINUOUS in μ; e−2 the discriminator). But it had to flag one confound: for
NATURAL α, "bounded" (small partial quotients) and "quadratic" (eventually-periodic CF, the Lagrange
class) coincide — every metallic mean is BOTH, every transcendental we used is NEITHER. So "brocot follows
the bounded/quadratic dichotomy" hid two distinct claims and we couldn't say which.

THE DECISIVE, PERFECTLY-CONTROLLED EXPERIMENT: hold the CF quotient ALPHABET fixed at {1,2} (so boundedness
and μ=2 are IDENTICAL across the group) and vary ONLY periodicity:
  • periodic_12   = [0; 1,2,1,2, …]            — bounded + QUADRATIC      (control)
  • thue_morse_12 = quotients from Thue–Morse  — bounded + NON-quadratic  (test)
  • fib_word_12   = quotients from Fibonacci-word — bounded + NON-quadratic (test, replicate)
All three have max quotient 2, μ=2, near-identical convergent growth. They differ ONLY in periodicity.

PREDICTION:
  • if brocot reads BOUNDEDNESS  → all three sit with the metallic means (Brody q ≈ 1); periodicity is invisible.
  • if brocot reads QUADRATICITY → periodic_12 stays q≈1 but TM/fib-word DROP toward the transcendentals.
Operator D_box is the CONTROL: all are μ=2 ⇒ should stay HIGH with golden regardless of periodicity (the
operators read μ, so they must be blind to this split — the mirror of e).

Anchors for the table: golden/silver (bounded-quadratic, q≈1) and e−2/liouville (unbounded-non-quadratic,
q drops). Reuses brocot_approximability's depth-sweep fingerprint + the gaah/ext_harper eigensolves @λ=1.

Out: coordinates/cf-discriminator.jsonl + figure P_cf_discriminator.png. Run: --run [--workers 10].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# brocot_approximability sets up the brocot sys.path on import and exposes the shared fingerprint
from cross_substrate.brocot_approximability import _fingerprint, predict_partials, DEPTHS, F_CARRIER  # noqa: E402
from cross_substrate.quasiperiodic_operators import OPERATORS, PHIS                                    # noqa: E402
from cross_substrate.sturmian_hamiltonian_run import box_dim                                           # noqa: E402
from cross_substrate.cf_mechanism import max_cf_quotient                                               # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
N_OP = 50_000              # match the banked quasiperiodic-operators standard
OPS = ("gaah", "ext_harper")


# ---- CF construction --------------------------------------------------------------------------------
def alpha_from_cf(quotients):
    """Evaluate the simple continued fraction [0; a1, a2, …] by reverse recurrence (a0=0)."""
    x = 0.0
    for a in reversed(quotients):
        x = 1.0 / (a + x)
    return float(x)


def thue_morse_quotients(L, lo=1):
    """Quotients from the Thue–Morse sequence: a_n = lo + (popcount(n) mod 2) ∈ {lo, lo+1}.
    Bounded; the TM sequence is non-periodic ⇒ the number is NOT quadratic (Lagrange)."""
    return [lo + (bin(n).count("1") & 1) for n in range(L)]


def fib_word_quotients(L, lo=1):
    """Quotients from the Fibonacci word (S1='0', S2='01', S_{n+1}=S_n+S_{n-1}), mapped to {lo, lo+1}.
    Bounded; Sturmian ⇒ non-periodic ⇒ NOT quadratic (and transcendental, Adamczewski–Bugeaud)."""
    s0, s1 = "0", "01"
    while len(s1) < L:
        s0, s1 = s1, s1 + s0
    return [lo + int(ch) for ch in s1[:L]]


_L = 90   # depth: {1,2}-quotients ⇒ denominators ≫ 1e16 well before this; safe for double precision
# (name, α, type, μ) — type: BQ bounded-quadratic / BN bounded-NONquadratic / UN unbounded-nonquadratic
TARGETS = [
    ("golden",        (np.sqrt(5) - 1) / 2,                          "BQ", 2.0),
    ("silver",        np.sqrt(2) - 1,                                "BQ", 2.0),
    ("periodic_12",   alpha_from_cf([1, 2] * (_L // 2)),             "BQ", 2.0),   # control
    ("thue_morse_12", alpha_from_cf(thue_morse_quotients(_L)),       "BN", 2.0),   # TEST
    ("fib_word_12",   alpha_from_cf(fib_word_quotients(_L)),         "BN", 2.0),   # TEST (replicate)
    ("e_minus_2",     np.e - 2,                                      "UN", 2.0),
    ("liouville",     sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)), "UN", 1e9),
]


# ---- operator side (control) ------------------------------------------------------------------------
def _op_task(arg):
    opname, alpha, phi = arg
    ev = OPERATORS[opname](1.0, float(phi), float(alpha), n=N_OP)
    return opname, box_dim(ev)


def operator_dbox(workers):
    """gaah+ext_harper D_box @λ=1, mean over phases — the same statistic cf_mechanism loaded."""
    tasks = [(op, a, phi) for _, a, _, _ in TARGETS for op in OPS for phi in PHIS]
    amap = {n: a for n, a, _, _ in TARGETS}
    by = {}   # (name) -> list of box_dims (both ops pooled, matching cf_mechanism._load_operator_dbox)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        # rebuild task→name mapping by index groups
        idx = 0
        order = [(n, op, phi) for n, a, _, _ in TARGETS for op in OPS for phi in PHIS]
        for (name, op, phi), (rop, db) in zip(order, ex.map(_op_task, tasks)):
            if db is not None and np.isfinite(db):
                by.setdefault(name, []).append(float(db))
    return {n: float(np.mean(v)) for n, v in by.items() if v}


# ---- brocot side (discriminator) --------------------------------------------------------------------
def brocot_q(alpha):
    """endpoint (max-depth) Brody q from the carrier-comb × irrational-α depth-sweep (brocot bridge)."""
    sp = predict_partials([1.0, float(alpha)], [DEPTHS[-1], DEPTHS[-1]], f_carrier=F_CARRIER)
    fp = _fingerprint(sp.freqs)
    return fp.get("I.8_brody_q"), int(sp.freqs.size), fp


def run(workers):
    print("CF-DISCRIMINATOR — boundedness vs quadraticity (alphabet held at {1,2}, periodicity varied)")
    t0 = time.perf_counter()
    od = operator_dbox(workers)

    rows, recs = [], []
    for name, alpha, typ, mu in TARGETS:
        q, npart, fp = brocot_q(alpha)
        mxq = max_cf_quotient(alpha, 300)
        rows.append((name, typ, mxq, mu, q, od.get(name)))
        recs.append({"substrate": "cf-discriminator", "cell_id": name, "target": name,
                     "cf_type": typ, "max_cf_quotient": mxq, "irrationality_measure": mu,
                     "alpha": float(alpha), "n_partials": npart,
                     "brocot_brody_q": q, "operator_dbox_gaah_exthar_mean": od.get(name),
                     "axes_computed": fp,
                     "source_artifact": "generated (predict_partials + gaah/ext_harper eigensolve @λ=1)",
                     "computed_date": date.today().isoformat()})

    print(f"\n{'target':14s} {'type':>4s} {'maxQ':>5s} {'μ':>5s} {'brocot_q':>9s} {'op_Dbox':>8s}")
    for name, typ, mxq, mu, q, dbox in rows:
        mus = "∞" if mu > 1e8 else f"{mu:.2f}"
        print(f"{name:14s} {typ:>4s} {mxq:>5.0f} {mus:>5s} "
              f"{(f'{q:.3f}' if isinstance(q, float) else '   -'):>9s} "
              f"{(f'{dbox:.3f}' if isinstance(dbox, float) else '  -'):>8s}")

    # the decisive readout: where do the bounded-NONquadratic {1,2} targets land?
    def _q(n):
        return dict((r[0], r[4]) for r in rows).get(n)
    def _d(n):
        return dict((r[0], r[5]) for r in rows).get(n)
    bq_anchor = np.mean([v for v in (_q("golden"), _q("silver"), _q("periodic_12")) if isinstance(v, float)])
    un_anchor = np.mean([v for v in (_q("e_minus_2"), _q("liouville")) if isinstance(v, float)])
    bn = {n: _q(n) for n in ("thue_morse_12", "fib_word_12")}
    print(f"\nbrocot-q anchors: bounded-quadratic {{golden,silver,periodic_12}} mean={bq_anchor:.3f}  |  "
          f"unbounded-nonquadratic {{e,liouville}} mean={un_anchor:.3f}")
    print(f"bounded-NONquadratic TESTS: thue_morse_12={bn['thue_morse_12']}, fib_word_12={bn['fib_word_12']}")
    mid = 0.5 * (bq_anchor + un_anchor)
    side = []
    for n, v in bn.items():
        if isinstance(v, float):
            side.append("BOUNDEDNESS" if v > mid else "QUADRATICITY")
    verdict = side[0] if side and all(s == side[0] for s in side) else "SPLIT/AMBIGUOUS"
    print(f"  → both bounded-NONquadratic tests fall on the {verdict} side "
          f"(midpoint q={mid:.3f}; >mid ⇒ with bounded/metallic ⇒ BOUNDEDNESS; <mid ⇒ with transcendentals ⇒ QUADRATICITY)")
    # operator control: all bounded (μ=2) should stay high; periodicity invisible
    bnd_dbox = [_d(n) for n in ("golden", "silver", "periodic_12", "thue_morse_12", "fib_word_12")
                if isinstance(_d(n), float)]
    print(f"\noperator-Dbox CONTROL: all bounded targets (μ=2) D_box={np.mean(bnd_dbox):.3f}±{np.std(bnd_dbox):.3f} "
          f"(golden {_d('golden'):.3f}) vs liouville {_d('liouville'):.3f} — operators "
          f"{'BLIND to periodicity (flat across bounded) ⇒ confirms they read μ' if np.std(bnd_dbox) < 0.03 else 'show structure (check)'}.")
    print("\n[discriminator] alphabet held at {1,2}, only periodicity varied ⇒ decomposes the bounded/"
          "quadratic confound cf_mechanism had to flag. Flag, don't interpret — verdict is Will's.")

    with open(os.path.join(COORD, "cf-discriminator.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ {len(recs)} targets in {(time.perf_counter()-t0)/60:.1f} min. banked cf-discriminator.jsonl.")
    _figure(rows)


def _figure(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.5), sharex=True)
    names = [r[0] for r in rows]
    x = np.arange(len(names))
    colby = {"BQ": "#1f77b4", "BN": "crimson", "UN": "#d62728"}
    cols = [colby[r[1]] for r in rows]
    qv = [r[4] if isinstance(r[4], float) else np.nan for r in rows]
    dv = [r[5] if isinstance(r[5], float) else np.nan for r in rows]
    a1.scatter(x, qv, s=110, c=cols, edgecolor="k", zorder=4)
    a1.axhline(np.nanmean([qv[i] for i in range(len(rows)) if rows[i][1] == "BQ"]), ls=":", color="#1f77b4",
               label="bounded-quadratic anchor")
    a1.axhline(np.nanmean([qv[i] for i in range(len(rows)) if rows[i][1] == "UN"]), ls=":", color="#d62728",
               label="unbounded anchor")
    a1.set_ylabel("brocot Brody q"); a1.set_title(
        "DISCRIMINATOR — brocot q (red = bounded-NONquadratic {1,2})\nwith blue anchor ⇒ BOUNDEDNESS; "
        "toward red line ⇒ QUADRATICITY")
    a1.legend(fontsize=7); a1.grid(alpha=0.2)
    a2.scatter(x, dv, s=110, c=cols, edgecolor="k", zorder=4)
    a2.set_ylabel("operator D_box (gaah+ext_harper @λ=1)")
    a2.set_title("CONTROL — operator D_box\n(flat across all bounded ⇒ blind to periodicity, reads μ)")
    a2.grid(alpha=0.2)
    for ax in (a1, a2):
        ax.set_xticks(x); ax.set_xticklabels(names, rotation=35, ha="right", fontsize=7)
    p = os.path.join(_HERE, "figures", "P_cf_discriminator.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.run:
        run(a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
