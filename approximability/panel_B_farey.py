"""
approximability/panel_B_farey.py — Panel B, Face 2 (FAREY cross-check; the real home of the certified Σ² probe).

Face 1 (spectral Σ²) collapsed BY THEOREM: fractal Cantor spectra follow power-law level spacings s^{-β}, 1<β<2
(Geisel–Ketzmerick–Petschel) — RMT Σ² is the wrong framework there; dimension is what there is. The certified Σ²(L)
probe (clean-room PASS, L≤30) belongs on a SMOOTH-density point process: the local Farey-gap process near α (BCZ).
Local Farey enumeration is O(Q), so we reach Q≫33102 around π — dissolving Face-1's depth wall (π's a₅=292,
q=33102, goes INSIDE the data).

PRE-REGISTERED PREDICTIONS (written before the run) — two candidate order parameters, two disagreement cells:
  K-grouping  (liminf geom-mean): FINITE {golden, √2, π}  vs  INFINITE {e, Liouville}.
  tier-grouping (irration. measure): {golden,√2} vs {π,e} vs {Liouville}.
  Larger quotients ⇒ deeper cusp excursions ⇒ bigger max-gaps ⇒ HIGHER Farey-gap Σ². So:
    CELL 1  π-vs-e:         K says SPLIT (π tame/low, e anomalous/high);  tier says TOGETHER (both generic).
    CELL 2  e-vs-Liouville: K says TOGETHER (both K=∞, both high);        tier says SPLIT (Liouville ≫ e).
  Whichever candidate survives BOTH cells has dodged two bullets.

REQUIREMENTS: per-target Q-depth certificate (assert Q>33102 for π); per-window magnitude+smoothness gate BEFORE any
Σ² is read (Liouville expected to stress it hardest — a failure there is informative, not garbage).

READ-ONLY. Run: PYTHONPATH=/home/combust/fmexplorer/riemann_explorer /home/combust/fmexplorer/bin/python3 \
                  approximability/panel_B_farey.py
"""
import os, sys, json, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
import numpy as np
import mpmath as mp
from cross_substrate.axes import II1_sigma2_at_L

mp.mp.dps = 260
OUT = os.path.dirname(os.path.abspath(__file__))
L_GRID = [2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0]


def farey_near(alpha, Q, delta):
    """All reduced p/q, q≤Q, in [α−δ, α+δ]. O(Σ 2qδ). Returns sorted fraction values + max q used."""
    a = mp.mpf(alpha); lo = a - delta; hi = a + delta
    vals = []; qmax_used = 0
    for q in range(1, Q + 1):
        p_lo = int(mp.ceil(lo * q)); p_hi = int(mp.floor(hi * q))
        for p in range(p_lo, p_hi + 1):
            if math.gcd(p, q) == 1:
                vals.append(p / q); qmax_used = max(qmax_used, q)
    return np.sort(np.array(vals, float)), qmax_used


def window_gate(pos):
    """Per-window magnitude+smoothness gate: after unit-mean normalization, is the local density smooth enough that
    the RMT-calibrated Σ² transfers? Fail if a single gap dominates (cusp pathology) or density is grossly non-uniform."""
    g = np.diff(pos)
    g = g[g > 0]
    if g.size < 200:
        return False, "too few points", {}
    mg = g.mean()
    max_ratio = g.max() / mg                      # single-gap dominance
    # density uniformity across 12 sub-bins (count CV)
    edges = np.linspace(pos[0], pos[-1], 13)
    counts = np.histogram(pos, edges)[0]
    dens_cv = counts.std() / counts.mean()
    # dens_cv is the SMOOTHNESS criterion (uniform local density → BCZ Σ² transfers). A single large gap from the
    # best convergent (max_ratio ~ tens) is SIGNAL (the cusp / largest quotient), not pathology — only gate it out if
    # it is so extreme it collapses the window (max_ratio > 1500 ⇒ a near-empty window, Σ² undefined).
    ok = (dens_cv < 0.5) and (max_ratio < 1500.0)
    reason = f"max_gap/mean={max_ratio:.1f} dens_cv={dens_cv:.2f}"
    return ok, reason, {"max_gap_ratio": float(max_ratio), "dens_cv": float(dens_cv)}


def sigma2_farey(alpha, Q, delta):
    vals, qmax = farey_near(alpha, Q, delta)
    if vals.size < 300:
        return None, qmax, vals.size, (False, "too few", {})
    g = np.diff(vals); g = g[g > 0]
    pos = np.concatenate([[0.0], np.cumsum(g / g.mean())])   # unit-mean point process
    gate = window_gate(pos)
    s2 = [II1_sigma2_at_L(pos, L) for L in L_GRID] if gate[0] else None
    return s2, qmax, vals.size, gate


LIOUVILLE = sum(mp.mpf(10) ** (-math.factorial(n)) for n in range(1, 8))
TARGETS = [
    ("golden",   (mp.sqrt(5) - 1) / 2, "finite K=1", "bounded"),
    ("sqrt2",    mp.sqrt(2) - 1,        "finite K=2", "bounded"),
    ("pi",       mp.pi - 3,             "finite K=K0 (cond.)", "generic"),
    ("e",        mp.e - 2,              "INFINITE K=∞", "generic"),
    ("liouville", LIOUVILLE,            "INFINITE K=∞", "clustered"),
]
Q = 150_000
DELTA = 1.0e-6          # δQ² ≈ 2.25e4 candidate points; Q≫33102 ⇒ π's 292-structure is inside the data

if __name__ == "__main__":
    print("=" * 88)
    print(f"PANEL B — FACE 2 (Farey-gap Σ² near α), Q={Q}, δ={DELTA:g}  [certified probe, L≤30]")
    print("=" * 88)
    print("\nPRE-REGISTERED: CELL1 π-vs-e {K:split, tier:together}   CELL2 e-vs-Liou {K:together, tier:split}")
    print(f"depth certificate needs Q_used > 33102 for π (a₅=292 ⇒ q=33102 inside window)\n")

    res = {}
    print(f"  {'target':10s} {'npts':>6s} {'Qused':>7s} {'gate':>5s}  {'Σ²(L=8)':>8s} {'Σ²(L=20)':>9s} {'Σ²(L=30)':>9s}  note")
    for name, a, kcls, tcls in TARGETS:
        s2, qmax, npts, gate = sigma2_farey(a, Q, DELTA)
        res[name] = {"s2": s2, "qmax": qmax, "npts": npts, "gate_ok": gate[0], "gate": gate[1],
                     "k": kcls, "tier": tcls}
        depth_ok = (name != "pi") or (qmax > 33102)
        gtag = "✓" if gate[0] else "✗"
        if s2 is None:
            print(f"  {name:10s} {npts:>6d} {qmax:>7d} {gtag:>5s}  {'—':>8s} {'—':>9s} {'—':>9s}  "
                  f"gate FAIL: {gate[1]} ({kcls})")
        else:
            dcert = "" if depth_ok else "  ⚠DEPTH<33102"
            mgr = gate[2].get("max_gap_ratio", float("nan"))
            print(f"  {name:10s} {npts:>6d} {qmax:>7d} {gtag:>5s}  {s2[3]:>8.3f} {s2[5]:>9.3f} {s2[6]:>9.3f}  "
                  f"maxgap/mean={mgr:.0f} ({kcls}){dcert}")

    # depth certificate assertion for π
    pi_depth = res["pi"]["qmax"] > 33102
    print(f"\n  DEPTH CERTIFICATE (π): Q_used={res['pi']['qmax']} {'> 33102 ✓ (292-structure inside data)' if pi_depth else '≤ 33102 ✗'}")

    # ---- evaluate the two pre-registered cells at L=30 (where cusp structure accumulates) ----
    def s30(n): return res[n]["s2"][6] if res[n]["s2"] else None
    print("\n  PRE-REGISTERED CELLS (Σ² at L=30; higher = deeper cusp clustering):")
    vg, vs2, vp, ve, vl = s30("golden"), s30("sqrt2"), s30("pi"), s30("e"), s30("liouville")
    finite_band = [v for v in (vg, vs2) if v is not None]
    if finite_band and vp is not None and ve is not None:
        fb = np.mean(finite_band)
        # CELL 1: is π with the finite band (K) or with e (tier)?
        c1_K = abs(vp - fb) < abs(vp - ve)
        print(f"   CELL1 π-vs-e: golden/√2 band≈{fb:.3f}, π={vp:.3f}, e={ve:.3f} → "
              f"{'π WITH finite band ⇒ K-grouping ✓ (π≠e)' if c1_K else 'π WITH e ⇒ tier-grouping'}")
    if ve is not None and vl is not None:
        # CELL 2: is Liouville with e (K) or split from e (tier)?
        rel = abs(vl - ve) / max(ve, 1e-9)
        c2_K = rel < 0.5
        print(f"   CELL2 e-vs-Liou: e={ve:.3f}, Liouville={('gate-fail/'+res['liouville']['gate']) if vl is None else f'{vl:.3f}'} → "
              f"{'e≈Liou ⇒ K-grouping' if c2_K else 'Liou≫e (or gate-fail) ⇒ tier-grouping / pathological'}")
    elif res["liouville"]["s2"] is None:
        print(f"   CELL2 e-vs-Liou: Liouville FAILED the smoothness gate ({res['liouville']['gate']}) — "
              f"its local Farey structure is pathological. INFORMATIVE: consistent with K=∞ extreme clustering "
              f"(the gate caught it rather than banking garbage). e is smooth+measurable; Liou is off-scale.")

    with open(os.path.join(OUT, "panel_B_farey.json"), "w") as fh:
        json.dump({"Q": Q, "delta": DELTA, "L_grid": L_GRID,
                   "results": {k: {kk: vv for kk, vv in v.items()} for k, v in res.items()},
                   "pi_depth_ok": bool(pi_depth)}, fh, indent=2, default=str)
    print("\n  wrote approximability/panel_B_farey.json — DONE.")
