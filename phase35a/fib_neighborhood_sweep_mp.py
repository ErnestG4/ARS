"""
phase35a/fib_neighborhood_sweep_mp.py — OVERNIGHT Fibonacci-neighbourhood
structure run, MULTI-CORE (Will 2026-05-18; box has 24 cores, 10 workers
⇒ non-disruptive). Supersedes the serial fib_neighborhood_sweep.py
(kept in git as provenance). Each (N,λ,φ)→W1δ is a PURE DETERMINISTIC
function ⇒ parallel results are BIT-IDENTICAL to serial: parallelisation
changes only scheduling, NOT the computation. The controlled experiment
(N the only independent variable; exact rate-run instrument) is intact.

Knob-setting (Will's 3 delegated knobs, upgraded since cores removed the
cost grading — transparent for review): rung range **F16..F26**;
ALL rungs FULL neighbourhood (no cost-grading); density = tight cluster
F_n±{1,2,3,5,8} + interval @¼,½,¾ toward F_{n+1}. Rationale: the rate
anomaly is in F21..F24 (10000..46368) — full cluster+interval THERE
maximises commensurability(sharp-cluster) vs log-periodic(smooth-
interval) discrimination exactly where it matters; F25,F26 extend
"progressively higher N" (crossover asymptotes there; commensurability/
log-periodic persists).

EXACT rate setup UNCHANGED: golden θ, λ_sub=0.5/λ_sup=1.5,
16 φ∈[0,0.5) (period-0.5-confirmed exact α-null), L_iter=1e5.
SCOPING / instrument N-behaviour — asymmetric label, NEVER a finding.
OUT: rate extrapolation, sensitivity re-measure, any AM result.
brief-and-hold; Class II blocked; no §3 adjudication.
"""
from __future__ import annotations
import os
# thread-pin BEFORE numpy import: 10 single-threaded workers, no
# BLAS/OMP oversubscription on the 24-core box ⇒ truly non-disruptive.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
import sys, json, time, traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from unfold_rotnum import am_eigs, unfold_rotnum, W1d, GOLDEN

WORKERS = 10
LAM = {"sub": 0.50, "sup": 1.50}
LITER = 100_000
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 6))
OUT = os.path.join(HERE, "fib_neighborhood_mp_results.json")
CLUSTER = [1, 2, 3, 5, 8]
INTERVAL_FR = (0.25, 0.5, 0.75)


def fib(kmax):
    F = [0, 1]
    while len(F) <= kmax:
        F.append(F[-1] + F[-2])
    return F
FIB = fib(27)
assert FIB[16] == 987 and FIB[24] == 46368 and FIB[26] == 121393
RUNGS = list(range(16, 27))                       # F16..F26, all FULL


def task(arg):
    """Pure deterministic unit: (N, regime, λ, φ) → W1δ. Picklable."""
    N, regime, lam, phi = arg
    try:
        e = am_eigs(lam, int(N), float(phi))
        w = float(W1d(unfold_rotnum(e, lam, GOLDEN, LITER, phis=(float(phi),))))
        return (N, regime, float(phi), w, None)
    except Exception as ex:
        return (N, regime, float(phi), None, repr(ex))


def rung_points(n):
    Fn, Fn1 = FIB[n], FIB[n + 1]
    pts = {Fn: "Fn"}
    for d in CLUSTER:
        pts[Fn + d] = f"+{d}"; pts[Fn - d] = f"-{d}"
    for fr in INTERVAL_FR:
        pts[int(round(Fn + fr * (Fn1 - Fn)))] = f"int{fr}"
    return pts                                     # {N: kind}


def main():
    t0 = time.time()
    # build N -> (rung Fn, kind); smallest-N-first task order (completion-priority)
    Nmeta = {}
    for n in RUNGS:
        for N, kind in rung_points(n).items():
            Nmeta.setdefault(int(N), (FIB[n], n, kind))
    Ns = sorted(Nmeta)
    tasks = [(N, reg, LAM[reg], ph) for N in Ns for reg in ("sub", "sup")
             for ph in PHIS]
    print("=" * 86)
    print(f"FIB-NEIGHBOURHOOD MP — {WORKERS} workers / 24 cores "
          f"(thread-pinned, non-disruptive)")
    print(f"  exact rate setup: λ {LAM['sub']}/{LAM['sup']}, L={LITER}, "
          f"{len(PHIS)} φ∈[0,0.5) ; N only var ; rungs F16..F26 ALL FULL")
    print(f"  {len(Ns)} N-points, {len(tasks)} pure tasks "
          f"(bit-identical to serial)")
    print("=" * 86, flush=True)

    acc = {N: {"sub": {}, "sup": {}} for N in Ns}     # N -> regime -> {phi:w}
    rec = {"scoping_instrument_Nbehaviour": True, "exact_rate_setup": True,
           "parallel_bit_identical_to_serial": True, "workers": WORKERS,
           "lam": LAM, "L": LITER, "nphi": len(PHIS),
           "rungs": {str(FIB[n]): {"F_n": FIB[n], "n": n, "mode": "full",
                                    "points": []} for n in RUNGS},
           "N_to_rung": {str(N): FIB[Nmeta[N][1]] for N in Ns}}
    done_N = set()
    nres = 0
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(task, a) for a in tasks]    # submitted smallest-N-first
        for fut in as_completed(futs):
            N, reg, ph, w, err = fut.result()
            nres += 1
            acc[N][reg][ph] = (w, err)
            # when an N has all 16 φ for BOTH regimes → finalise + checkpoint
            if (N not in done_N and len(acc[N]["sub"]) == len(PHIS)
                    and len(acc[N]["sup"]) == len(PHIS)):
                done_N.add(N)
                sv = np.array([acc[N]["sub"][p][0] for p in PHIS
                               if acc[N]["sub"][p][0] is not None], float)
                pv = np.array([acc[N]["sup"][p][0] for p in PHIS
                               if acc[N]["sup"][p][0] is not None], float)
                Fn, n, kind = Nmeta[N]
                if sv.size and pv.size:
                    ss = float(sv.max() - sv.min()); sp = float(pv.max() - pv.min())
                    gp = float(pv.min() - sv.max())
                    pt = {"N": N, "kind": kind, "sub_spread": round(ss, 7),
                          "sup_spread": round(sp, 7), "gap": round(gp, 7),
                          "sub_mean": round(float(sv.mean()), 7),
                          "sup_mean": round(float(pv.mean()), 7),
                          "exact_crit": bool(gp > 0 and gp >= max(ss, sp))}
                else:
                    pt = {"N": N, "kind": kind, "error": "missing φ results"}
                rec["rungs"][str(Fn)]["points"].append(pt)
                if nres % 32 == 0 or len(done_N) % 5 == 0:
                    rec["elapsed_s"] = round(time.time() - t0, 0)
                    json.dump(rec, open(OUT, "w"), indent=1)
                    print(f"   [{len(done_N):3d}/{len(Ns)} N done, "
                          f"{nres}/{len(tasks)} tasks, "
                          f"{rec['elapsed_s']:.0f}s] N={N} F_{n} {kind} "
                          f"sup_spread={pt.get('sup_spread','ERR')} "
                          f"gap={pt.get('gap','ERR')}", flush=True)

    # per-rung quick read (within-neighbourhood variation = the discriminant)
    for n in RUNGS:
        r = rec["rungs"][str(FIB[n])]
        ss = [p["sup_spread"] for p in r["points"] if "sup_spread" in p]
        gg = [p["gap"] for p in r["points"] if "gap" in p]
        fn = next((p for p in r["points"] if p.get("kind") == "Fn"
                   and "sup_spread" in p), None)
        if ss and fn:
            r["sup_spread_at_Fn"] = fn["sup_spread"]
            r["sup_spread_neigh_range"] = round(max(ss) - min(ss), 7)
            r["gap_neigh_range"] = round(max(gg) - min(gg), 7) if gg else None
    rec["total_s"] = round(time.time() - t0, 0)
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 86)
    print(f"DONE {rec['total_s']}s ({WORKERS} workers). Per-rung "
          f"sup_spread@Fn / neigh-range / gap-neigh-range in JSON.")
    print("Outcome-map read = the report (PRE-REGISTERED: neigh-flat⇒crossover/")
    print("ladder-representative ; sharp-cluster⇒commensurability-band-edge ;")
    print("smooth-interval⇒log-periodic ; + gap-own-F_n-structure sub-question).")
    print("SCOPING / instrument N-behaviour, NEVER a finding. brief-and-hold.")
    print("=" * 86)


if __name__ == "__main__":
    main()
