"""
phase35a/curiosity_theta_robustness.py — C1 from the Slate Unit 3
ADDENDUM (curiosity probe). PREPARED + smoke-verified. Launched as #2
in the overnight chain.

QUESTION (curiosity, in-scope). Is the φ-mode contamination at
b1crocze1/b0haqgof3's load-bearing cells θ-universal or
golden-mean-specific? Tests by re-running the same instrument at
those cells with an alternative Diophantine θ = silver mean √2−1.
Tells us whether the artifact structure is a property of the
leg × Diophantine-class interaction (any irrational θ shows similar
φ-mode contamination) or a golden-mean-specific phenomenon tied to
Fibonacci approximants.

DESIGN (locked, minimal).
- 2 cells, δ=0.5: sub (λ=0.5) + sup (λ=1.5), both at N=70000.
- L = 1×10⁵ only (the Step-1 L; the contamination magnitude lives
  here, and we want a direct comparison to b1crocze1/b0haqgof3
  ratios computed against the SAME L=1e5 spread).
- 16 φ ∈ [0,0.5); WORKERS=18 local; ratio-free leg.
- θ = √2 − 1 ≈ 0.41421356 (silver mean — standard Diophantine class,
  distinct from golden mean's Fibonacci-approximant structure).

NOTE on the ratio: this single-L run cannot compute the b1crocze1-
style ptp_φ(Δw)/spread_ref ratio because that requires two L points.
Instead, we measure the L=1e5 SPREAD itself at silver-θ and compare
to the golden-θ baseline. Pre-registered comparison: the L=1e5
spread under silver-θ versus golden-θ at the same (δ, N) cells.
If similar magnitude (within ~3×, same order) the contamination
structure scales with the Diophantine class generally; if wildly
different, it is golden-specific. NEVER adjudicates (A)/(B) and
NEVER produces a Step-1-direct ratio (single-L run by design).

APPARATUS NOTE. No prior-run identity check (novel θ). Reports its
own per-cell L=1e5 spreads + means for cross-θ comparison to
b1crocze1/b0haqgof3.

PRE-REGISTERED TERMINALS.
- THETA_SPREAD_TRACKS_GOLDEN — silver-θ L=1e5 spread within factor 3
  of golden-θ baseline on BOTH legs (same order of magnitude ⇒
  contamination structure is θ-class-universal rather than
  golden-specific).
- THETA_SPREAD_DEVIATES — >3× on either leg ⇒ θ-specific; flag,
  surface, do NOT adjudicate (A)/(B).
- THETA_SPREAD_MIXED — legs differ in direction or one matches
  while the other deviates ⇒ surface.

SCOPE. Single-L, curiosity probe. Single-L by design — cannot
substitute for b1crocze1/b0haqgof3 verdict on golden-θ. Never proves
(A)/(B); never adjudicates Step-1; never decides §D. Banked Step-1
untouched.
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
import sys, json, time
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from unfold_rotnum import am_eigs, unfold_rotnum, W1d, GOLDEN

WORKERS = 18
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 6))
DELTA = 0.5
N = 70000
L = 100000
LEGS = ("sub", "sup")                            # λ=0.5 / λ=1.5
SILVER = np.sqrt(2.0) - 1.0                       # ≈ 0.41421356
TOL_TRACKS_FACTOR = 3.0                           # within factor 3 ⇒ tracks
OUT = os.path.join(HERE, "curiosity_theta_robustness_results.json")
RAW = os.path.join(HERE, "curiosity_theta_robustness_rawtable.json")
B1CR = os.path.join(HERE, "sub_phi_resolved_L_results.json")
B0HA = os.path.join(HERE, "sup_phi_resolved_L_results.json")


def cell(arg):
    leg, phi = arg
    lam = 1.0 - DELTA if leg == "sub" else 1.0 + DELTA
    try:
        e = am_eigs(lam, int(N), float(phi), theta=SILVER)
        w = float(W1d(unfold_rotnum(e, lam, SILVER, int(L), phis=(float(phi),))))
        return (leg, float(phi), w, None)
    except Exception as ex:
        return (leg, float(phi), None, repr(ex))


def _dump_raw(table, total):
    recs = [[k[0], float(k[1]), v] for k, v in table.items()]
    json.dump({"n": len(recs), "of": total, "recs": recs}, open(RAW, "w"))


def _load_raw():
    d = json.load(open(RAW))
    t = {}
    for leg, ph, w in d["recs"]:
        t[(leg, round(float(ph), 6))] = w
    return t, d.get("n", len(t)), d.get("of")


def phi_vec(table, leg):
    v = [table.get((leg, round(p, 6))) for p in PHIS]
    return None if any(x is None for x in v) else np.asarray(v, float)


def _golden_baseline(leg):
    """Load golden-θ L=1e5 spread@N=70k from b1crocze1/b0haqgof3."""
    src = B1CR if leg == "sub" else B0HA
    try:
        r = json.load(open(src))
        for p in r["per_cell"]:
            if p.get("delta") == 0.5 and p.get("N") == 70000:
                return {"spread": float(p["spread_at_L_ref"]),
                        "mean": float(p["mean_at_L_ref"])}
    except Exception:
        return None
    return None


def main():
    t0 = time.time()
    tasks = [(leg, p) for leg in LEGS for p in PHIS]
    print("=" * 84)
    print(f"C1 — θ-robustness curiosity probe — {WORKERS}w ; "
          f"θ_silver=√2−1≈{SILVER:.8f} ; ratio-free leg")
    print(f"  δ={DELTA} ; legs={LEGS} ; N={N} ; L={L} (single-L) ; "
          f"{len(PHIS)}φ ; {len(tasks)} tasks")
    print("=" * 84, flush=True)

    errs, table = [], None
    if os.path.exists(RAW):
        tr, nr, ofr = _load_raw()
        if nr == ofr == len(tasks):
            table = tr
            print(f"  ANALYZE-ONLY: complete raw ({nr}).", flush=True)
    if table is None:
        table, done = {}, 0
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            for f in as_completed([ex.submit(cell, a) for a in tasks]):
                leg, phi, w, err = f.result()
                table[(leg, round(phi, 6))] = w
                done += 1
                if err:
                    errs.append({"leg": leg, "phi": phi, "err": err})
                    print(f"  ERR {leg} φ={phi}: {err}", flush=True)
                if done % 16 == 0:
                    _dump_raw(table, len(tasks))
                    print(f"  … {done}/{len(tasks)} [{time.time()-t0:.0f}s]",
                          flush=True)
        _dump_raw(table, len(tasks))
        print(f"  raw persisted ({len(table)}).", flush=True)

    per_leg = {}
    for leg in LEGS:
        v = phi_vec(table, leg)
        gold = _golden_baseline(leg)
        if v is None or gold is None:
            per_leg[leg] = {"error": "missing data or baseline"}; continue
        silver_spread = float(np.ptp(v))
        silver_mean = float(v.mean())
        ratio_spread = silver_spread / max(gold["spread"], 1e-12)
        ratio_mean = silver_mean / max(gold["mean"], 1e-12)
        tracks = (1.0 / TOL_TRACKS_FACTOR <= ratio_spread <= TOL_TRACKS_FACTOR)
        per_leg[leg] = {"lam": 1.0 - DELTA if leg == "sub" else 1.0 + DELTA,
                         "silver_L1e5_spread": round(silver_spread, 9),
                         "silver_L1e5_mean": round(silver_mean, 9),
                         "golden_L1e5_spread": round(gold["spread"], 9),
                         "golden_L1e5_mean": round(gold["mean"], 9),
                         "spread_ratio_silver_over_golden": round(ratio_spread, 4),
                         "mean_ratio_silver_over_golden": round(ratio_mean, 4),
                         "tracks_golden_within_3x": bool(tracks)}

    trackings = [v.get("tracks_golden_within_3x") for v in per_leg.values()
                 if "error" not in v]
    if not trackings or any(t is None for t in trackings):
        overall = "THETA_INDETERMINATE"
    elif all(trackings):
        overall = "THETA_SPREAD_TRACKS_GOLDEN"
    elif not any(trackings):
        overall = "THETA_SPREAD_DEVIATES"
    else:
        overall = "THETA_SPREAD_MIXED"

    rec = {"run": "C1 curiosity θ-robustness probe (silver mean)",
           "theta_silver": float(SILVER),
           "delta": DELTA, "N": N, "L": L, "legs": list(LEGS),
           "TOL_TRACKS_FACTOR": TOL_TRACKS_FACTOR,
           "per_leg": per_leg, "overall_terminal": overall,
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "Curiosity probe (single-L). Cannot compute a "
                   "Step-1-style ptp_phi(Δw)/spread ratio (needs two "
                   "L points). Compares silver-θ L=1e5 spread to "
                   "golden-θ baseline. Never adjudicates (A)/(B), "
                   "Step-1, §D. Surfaces for Will."}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    for leg, v in per_leg.items():
        if "error" in v: print(f"  {leg}: {v['error']}"); continue
        print(f"  {leg} (λ={v['lam']}): silver_spread={v['silver_L1e5_spread']} "
              f"golden_spread={v['golden_L1e5_spread']} "
              f"ratio={v['spread_ratio_silver_over_golden']} "
              f"tracks_within_3x={v['tracks_golden_within_3x']}")
    print(f"  TERMINAL: {overall}  [{rec['total_s']}s] errors={len(errs)}")
    print("  Curiosity probe. SURFACED; Step-1/(A)/(B)/§D untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()
