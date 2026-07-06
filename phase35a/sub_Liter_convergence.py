"""
phase35a/sub_Liter_convergence.py — L_iter-CONVERGENCE SWEEP at fixed
N (Will's explicit go 2026-05-19 AM: "run the L_iter-convergence
sweep at fixed N", server, 48 threads). Decision-record option (i),
now authorized. In-line with the sub-resolution/(A)-vs-(B) thread.

CONTEXT. b626clevu Q2 = PLATEAU_L_SENSITIVE: subcritical W1δ from the
rotation-number leg is L_iter-UNDERCONVERGED — N=70k: L1e5≈0.343,
L4e5≈0.075 (dL≈0.27 ≫ §C φ-noise), still δ-independent, not
near-clock; N=100k itself weakly L-sensitive. The full L=1e5
N-structure {0.34@70k,0.33@75k,0.01@100k,0.40@125k,0.667@150k} may be
an L-underconvergence artifact (⇒ would favor (B): resolved sub value
near-clock δ-indep) OR a genuine non-clock/N-structured object (⇒
(A)-flavor). This sweep CHARACTERIZES the leg's L-convergence; it
does NOT discriminate (A)/(B) definitively — only §D/DGY does. It
SURFACES; it does not adjudicate, does not launch §D, does not
retro-adjudicate Step-1.

PRE-REGISTERED (discriminant_exact_question_check):
 EXACT QUESTION: at FIXED N, as L_iter increases over a BOUNDED
 ladder, does subcritical W1δ converge — and if so, toward the
 NEAR-CLOCK value with the {70k,100k,125k} N-structure COLLAPSING
 (⇒ the L=1e5 N-structure was an L-underconvergence artifact;
 resolved sub value near-clock δ-independent), or to a non-clock /
 N-dependent value, or not converge within the ladder?
 DESIGN (locked, justified):
  • δ = {0.005, 0.069475, 0.5} — 3 exact §A rungs spanning λ=0.995
    (near-critical) → 0.9305 → 0.5 (deep-AC). δ-independence is an
    ESTABLISHED invariant across slicing/bxtbmjoqv/b626clevu —
    sampled (not all 8) to CONFIRM it persists under the L-sweep
    while staying affordable, NOT redundantly recomputed.
  • N = {70000, 100000, 125000} — plateau anchor / "near-clock@1e5"
    / climbing@1e5; the minimum set to test whether the WHOLE L=1e5
    N-structure dissolves under L-convergence.
  • L = {100000, 400000, 1600000} — geometric ×4, BOUNDED. NOT
    chasing to extreme L (6.4e6+ is prohibitive and is the
    "chase-convergence" trap). If not converged by 1.6e6 the honest
    terminal says so; extending L is WILL'S call, not auto-chase.
  • 8 φ∈[0,0.5) (vs prior 16) — deliberate cost cut: the L-signal
    (ΔW1δ ~0.1-0.3 per L-step) dwarfs the φ-floor (~1e-4); 8 φ
    estimates the §C floor adequately. Noted, not hidden.
 CODED TEST per (δ,N): L-trajectory of the 8-φ α-ensemble mean W1δ;
  §C floor(δ,N,L) = φ-ensemble ptp; L_converged iff
  |mean(L_top) − mean(L_2nd)| ≤ max(floor_top, floor_2nd);
  near_clock iff mean(L_top) ≤ NEAR_CLOCK; plus log-log decay slope α
  (coarse 3-point indicator, NOT an over-fit verdict) and the
  N-structure-collapse check at L_top (do the 3 N agree within floor
  at near-clock?). NEAR_CLOCK=0.05 (proposed-not-fixed; structure
  fixed).
 HONEST TERMINALS (NEVER prove (A)/(B) — only §D/DGY; SURFACED):
  SUB_L_CONVERGES_NEAR_CLOCK  — ALL (δ,N) L-converged & near-clock &
   N-structure collapsed ⇒ L=1e5 N-structure was L-underconvergence;
   resolved sub value near-clock δ-indep. (Reported; Will adjudicates
   (A)/(B) & the Step-1 exposure — NOT concluded here.)
  SUB_L_CONVERGES_NONCLOCK   — converges but non-clock / N-dependent
   ⇒ (A)-flavor / unresolved.
  SUB_L_NOT_CONVERGED_WITHIN_LADDER — top-L increment ≫ floor for any
   (δ,N) ⇒ not converged by 1.6e6; trajectory+α surfaced; escalation
   (higher L? §D-with-L-first-class?) is WILL'S call.

SCOPE: characterization of the leg's subcritical L_iter-convergence
ONLY. NEVER proves (A)/(B); SURFACED not adjudicated; no §D launch;
no §3/Class-II; Step-1 NOT retro-adjudicated (banked Step-1
untouched). Server combust@10.0.0.225, ars env, WORKERS=48, MP
thread-pinned, pure deterministic ⇒ bit-identical-serial. Hardened
(rawtable persist-before-postproc + 64-ckpt + analyze-only). np.ptp
(NOT ndarray.ptp — numpy-2 lesson). brief-and-hold: runs under
Will's explicit go, then HOLDS for his review.
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

WORKERS = 48
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 8, endpoint=False), 6))
DELTAS = (0.005, 0.069475, 0.5)                  # exact §A rungs, λ=0.995/0.9305/0.5
NS = (70000, 100000, 125000)
LS = (100000, 400000, 1600000)                   # bounded geometric ×4
NEAR_CLOCK = 0.05
OUT = os.path.join(HERE, "sub_Liter_convergence_results.json")
RAW = os.path.join(HERE, "sub_Liter_convergence_rawtable.json")


def cell(arg):
    delta, lam, N, L, phi = arg
    try:
        e = am_eigs(lam, int(N), float(phi))
        w = float(W1d(unfold_rotnum(e, lam, GOLDEN, int(L), phis=(float(phi),))))
        return (float(delta), float(lam), int(N), int(L), float(phi), w, None)
    except Exception as ex:
        return (float(delta), float(lam), int(N), int(L), float(phi), None, repr(ex))


def _dump_raw(table, total):
    recs = [[float(k[0]), int(k[1]), int(k[2]), float(k[3]), v]
            for k, v in table.items()]
    json.dump({"n": len(recs), "of": total, "recs": recs}, open(RAW, "w"))


def _load_raw():
    d = json.load(open(RAW))
    t = {}
    for dl, N, L, ph, w in d["recs"]:
        t[(round(float(dl), 6), int(N), int(L), round(float(ph), 6))] = w
    return t, d.get("n", len(t)), d.get("of")


def ens(table, delta, N, L):
    v = [table.get((round(delta, 6), int(N), int(L), round(p, 6))) for p in PHIS]
    return None if any(x is None for x in v) else np.asarray(v, float)


def main():
    t0 = time.time()
    tasks = [(d, round(1.0 - d, 6), N, L, p)
             for d in DELTAS for N in NS for L in LS for p in PHIS]
    print("=" * 84)
    print(f"SUB L_iter-CONVERGENCE SWEEP — {WORKERS}w ; AM golden θ ; "
          f"ratio-free leg")
    print(f"  δ(sub)={DELTAS}  N(fixed)={NS}  L-ladder={LS}  "
          f"{len(PHIS)}φ  {len(tasks)} tasks")
    print("  Characterizes leg L-convergence; NEVER proves (A)/(B); "
          "SURFACED not adjudicated.")
    print("=" * 84, flush=True)

    errs, table = [], None
    if os.path.exists(RAW):
        tr, nr, ofr = _load_raw()
        if nr == ofr == len(tasks):
            table = tr
            print(f"  ANALYZE-ONLY: complete raw ({nr}) — skip compute.",
                  flush=True)
    if table is None:
        table, done = {}, 0
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            for f in as_completed([ex.submit(cell, a) for a in tasks]):
                d, lam, N, L, phi, w, err = f.result()
                table[(round(d, 6), int(N), int(L), round(phi, 6))] = w
                done += 1
                if err:
                    errs.append({"delta": d, "N": N, "L": L, "phi": phi,
                                 "err": err})
                    print(f"  ERR δ={d} N={N} L={L} φ={phi}: {err}", flush=True)
                if done % 64 == 0:
                    _dump_raw(table, len(tasks))
                    print(f"  … {done}/{len(tasks)} [{time.time()-t0:.0f}s]",
                          flush=True)
        _dump_raw(table, len(tasks))
        print(f"  raw persisted ({len(table)}) — postproc free to re-run.",
              flush=True)

    per, all_conv, all_nearclock = [], True, True
    Ltop, L2 = LS[-1], LS[-2]
    for d in DELTAS:
        for N in NS:
            m, fl = {}, {}
            ok = True
            for L in LS:
                a = ens(table, d, N, L)
                if a is None:
                    ok = False; break
                m[L] = float(a.mean()); fl[L] = float(np.ptp(a))
            if not ok:
                per.append({"delta": d, "N": N, "error": True})
                all_conv = False; all_nearclock = False; continue
            inc_top = abs(m[Ltop] - m[L2])
            floor_top = max(fl[Ltop], fl[L2])
            conv = inc_top <= floor_top
            nearc = m[Ltop] <= NEAR_CLOCK
            all_conv &= conv
            all_nearclock &= (conv and nearc)
            # coarse log-log decay slope α (W1δ ~ L^−α); 3-pt indicator only
            try:
                lx = np.log(np.array(LS, float))
                ly = np.log(np.array([m[L] for L in LS], float))
                alpha = float(-np.polyfit(lx, ly, 1)[0])
            except Exception:
                alpha = None
            per.append({"delta": d, "lam_sub": round(1.0 - d, 6), "N": N,
                        "means": {str(L): round(m[L], 6) for L in LS},
                        "floors": {str(L): round(fl[L], 6) for L in LS},
                        "top_increment": round(inc_top, 6),
                        "floor_top": round(floor_top, 6),
                        "L_converged": bool(conv),
                        "top_value": round(m[Ltop], 6),
                        "near_clock": bool(nearc),
                        "loglog_decay_alpha": (round(alpha, 4)
                                               if alpha is not None else None)})

    # N-structure-collapse at L_top: per δ, do the 3 N agree within floor
    # AND at near-clock?
    nstruct = {}
    for d in DELTAS:
        rows = [p for p in per if p.get("delta") == d and "means" in p]
        if len(rows) == len(NS):
            tops = [r["top_value"] for r in rows]
            fmax = max(r["floor_top"] for r in rows)
            collapsed = bool((max(tops) - min(tops)) <= fmax
                             and max(tops) <= NEAR_CLOCK)
            nstruct[str(d)] = {"top_values_by_N":
                               {str(NS[i]): tops[i] for i in range(len(NS))},
                               "spread": round(max(tops) - min(tops), 6),
                               "floor": round(fmax, 6),
                               "N_structure_collapsed": collapsed}
        else:
            nstruct[str(d)] = {"error": True}

    if not all_conv:
        terminal = "SUB_L_NOT_CONVERGED_WITHIN_LADDER"
    elif all_nearclock and all(v.get("N_structure_collapsed")
                               for v in nstruct.values() if "error" not in v):
        terminal = "SUB_L_CONVERGES_NEAR_CLOCK"
    else:
        terminal = "SUB_L_CONVERGES_NONCLOCK"

    rec = {"run": "subcritical L_iter-convergence sweep at fixed N",
           "readings": {"A": "estimator/L defect", "B": "N-resolution xover"},
           "deltas": list(DELTAS), "NS": list(NS), "LS": list(LS),
           "NEAR_CLOCK": NEAR_CLOCK, "terminal": terminal,
           "per_dN": per, "N_structure_at_Ltop": nstruct,
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "Characterization of leg L-convergence. NEVER proves "
                   "(A)/(B) (only §D/DGY). SURFACED not adjudicated; §D NOT "
                   "launched; Step-1 NOT retro-adjudicated. NOT_CONVERGED "
                   "⇒ escalation is Will's call (no auto-chase to higher L)."}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    for p in per:
        if p.get("error"):
            print(f"  δ={p['delta']} N={p['N']}  ERROR"); continue
        print(f"  δ={p['delta']:.6f} λ={p['lam_sub']:.4f} N={p['N']:6d} | "
              f"means={p['means']} | top_inc={p['top_increment']:.6f} "
              f"floor={p['floor_top']:.6f} conv={p['L_converged']} "
              f"top={p['top_value']:.6f} near_clock={p['near_clock']} "
              f"α≈{p['loglog_decay_alpha']}")
    for d, v in nstruct.items():
        if "error" not in v:
            print(f"  N-collapse δ={d}: {v['top_values_by_N']} "
                  f"spread={v['spread']} floor={v['floor']} "
                  f"collapsed={v['N_structure_collapsed']}")
    print(f"  TERMINAL: {terminal}  [{rec['total_s']}s] errors={len(errs)}")
    print("  NEVER proves (A)/(B); SURFACED; §D not launched; Step-1 "
          "untouched; NOT_CONVERGED⇒Will's call (no auto-chase).")
    print("=" * 84)


if __name__ == "__main__":
    main()
