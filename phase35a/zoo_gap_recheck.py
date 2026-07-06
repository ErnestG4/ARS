"""
phase35a/zoo_gap_recheck.py — Step-1 ratio-clean zoo-gap recheck
(Will 2026-05-17, "finish what §Q3 interrupted"). The certified grid's
BR_artifact / "demonstrated zoo gap" verdict was downgraded to
not-ratio-clean because AM cells were unfolded ratio-dependently
(unfold_ids_ref) while calibrators were ratio-free. The leg is now
RATIO_FREE_VALIDATED (commit 61e11d5). This re-runs the *identical*
certified-grid classification with AM cells unfolded by the validated
ratio-free unfold_rotnum, side-by-side with the certified (ids-leg)
verdicts.

Question: ratio-cleanly, where does AM land per λ — does BR_artifact
("no calibrator class / the gap") survive, and is sub≠super a clean
classifier-level split (the ratio-immune substrate fact)?

SCOPING / arc-finish. asymmetric label. No §3 adjudication, no
stamping; Class II blocked until §3 supplies a generator.
"""
from __future__ import annotations
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from unfold_rotnum import am_eigs, unfold_rotnum, spacings, W1d, GOLDEN

Q_MAX, MIN_EV = 30, 30
SUB = [0.10, 0.50, 0.95]
SUP = [1.05, 1.25, 2.00]
NCELL = 2584                       # the certified-grid classifier N (direct comparability)
LITER = 1_000_000                  # validated-converged regime (re-gate G3)
PHIS = (0.0, 0.33)


def quad_occ(unf):
    ev = np.sort(unf)
    j = joint_q_profile(ev, q_max=Q_MAX, min_events_per_q=MIN_EV)
    qd = joint_quadrant_diagnostic(j)
    vc = qd['quadrant'].value_counts(normalize=True)
    dom = max(vc.index, key=lambda k: vc[k])
    return dom, {k: round(float(v), 3) for k, v in vc.items()}


def load_certified():
    """Certified-grid (ids-leg, ratio-contaminated) quadrant @N=2584, if present."""
    p = os.path.join(HERE, "regated_instrument_results.json")
    out = {}
    if not os.path.exists(p):
        return out
    try:
        rec = json.load(open(p))
        for r in rec.get("records", []):
            if r.get("N") == 2584 and r.get("unfold") == "ids" and "lam" in r:
                out[float(r["lam"])] = r.get("quad", "?")
    except Exception:
        pass
    return out


def run():
    cert = load_certified()
    print("=" * 82)
    print("RATIO-CLEAN ZOO-GAP RECHECK — validated unfold_rotnum vs certified ids-leg")
    print(f"  N={NCELL} L_iter={LITER} φ={PHIS} ; classifier = joint_quadrant_diagnostic")
    print("=" * 82)
    print(f"{'λ':>6} {'regime':>5} | {'rotnum dom':>12} {'occ':>34} "
          f"{'W1δ':>8} {'var(s)':>8} | {'ids-leg (certified)':>18}")
    rows = []
    for regime, lams in (("SUB", SUB), ("SUP", SUP)):
        for lam in lams:
            occ_acc = {}
            w_acc, v_acc = [], []
            for phi in PHIS:
                e = am_eigs(lam, NCELL, phi)
                uf = unfold_rotnum(e, lam, GOLDEN, LITER, phis=(phi,))
                dom, occ = quad_occ(uf)
                for k, vv in occ.items():
                    occ_acc[k] = occ_acc.get(k, 0.0) + vv / len(PHIS)
                w_acc.append(W1d(uf)); v_acc.append(float(np.var(spacings(uf))))
            dom = max(occ_acc, key=occ_acc.get)
            occ_s = " ".join(f"{k}:{v:.2f}" for k, v in sorted(occ_acc.items(),
                              key=lambda kv: -kv[1])[:3])
            wv, vv = float(np.mean(w_acc)), float(np.mean(v_acc))
            ids_q = cert.get(lam, "—")
            rows.append({"lam": lam, "regime": regime, "rotnum_dom": dom,
                         "rotnum_occ": {k: round(v, 3) for k, v in occ_acc.items()},
                         "W1d": round(wv, 5), "var_s": round(vv, 5),
                         "ids_leg_certified_quad": ids_q})
            print(f"{lam:>6.2f} {regime:>5} | {dom:>12} {occ_s:>34} "
                  f"{wv:>8.4f} {vv:>8.4f} | {str(ids_q):>18}")

    # Recheck verdicts (asymmetric — arc-finish, not a discovery)
    sub_w = [r["W1d"] for r in rows if r["regime"] == "SUB"]
    sup_w = [r["W1d"] for r in rows if r["regime"] == "SUP"]
    sub_super_clean = (max(sub_w) < 0.5 * min(sup_w)) if (sub_w and sup_w) else None
    rotnum_quads = {r["rotnum_dom"] for r in rows}
    ids_quads = {str(r["ids_leg_certified_quad"]) for r in rows}
    changed = any(str(r["rotnum_dom"]) != str(r["ids_leg_certified_quad"])
                  and r["ids_leg_certified_quad"] not in ("—", "?") for r in rows)
    print("=" * 82)
    print(f"sub W1δ {sorted(sub_w)}  vs  sup W1δ {sorted(sup_w)}  "
          f"→ ratio-clean sub≠super split: {sub_super_clean}")
    print(f"rotnum quadrants {rotnum_quads}  |  certified ids-leg quadrants {ids_quads}")
    print(f"ratio-clean unfolding CHANGED the certified verdict on some cell: {changed}")
    print("READ: does BR_artifact ('no calibrator class / the gap') survive")
    print("ratio-cleanly, and is sub≠super a clean classifier-level split?")
    print("Inspect above — no auto-adjudication; arc-finish, not a §3/discovery call.")
    print("=" * 82)
    json.dump({"scoping_arc_finish": True, "leg": "unfold_rotnum (VALIDATED)",
               "rows": rows, "sub_super_clean_split": sub_super_clean,
               "verdict_changed_vs_certified": changed},
              open(os.path.join(HERE, "zoo_gap_recheck_results.json"), "w"), indent=1)


if __name__ == "__main__":
    run()
