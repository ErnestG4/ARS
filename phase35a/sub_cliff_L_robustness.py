"""
phase35a/sub_cliff_L_robustness.py — overnight follow-on (Will's
explicit 6h forward-go 2026-05-19, "run any extra versions of this we
may want"; in-line with the sub-resolution / (A)-vs-(B) thread ONLY).
PREPARED + smoke-verified; LAUNCH after bxtbmjoqv finishes. Useful
REGARDLESS of bxtbmjoqv's terminal ⇒ NOT contingent on adjudicating
the probe.

CONTEXT. slicing_outer HALT: sub rungs sit-then-cliff
{≈0.34 @70k, ≈0.33 @75k, ≈0.001-0.017 @100k}. Two live readings:
(A) estimator defect; (B) genuine resolution crossover. Only DGY
(§D) discriminates definitively. This run is a NON-adjudicating
mechanism diagnostic with TWO pre-registered sub-questions:

 Q1 — LOCAL REPRODUCTION. Does the sit-then-cliff reproduce on the
 local box (numpy 2.4.4, no VMware/contention) at L=1e5? CLIFF
 NOT reproduced ⇒ it was env/contention/version-specific (major;
 surface). Reproduced ⇒ the phenomenon is real and leg-intrinsic.

 Q2 — L_iter ROBUSTNESS (the mechanism discriminator obtainable
 WITHOUT DGY). unfold_rotnum's L is a convergence parameter; G4
 validated L-convergence only at λ∈{0,0.5,1} at FIXED test energies,
 NOT in the vary-N near-critical-sub regime. At the plateau anchor
 N=70000 and the resolved anchor N=100000, is W1δ L-invariant
 (L=1e5 vs 4e5, within the §C φ-noise)?
  • plateau (70000) L-INVARIANT ⇒ the ≈0.34 is NOT an
    L-underconvergence ⇒ consistent with (B) (under-resolved by N).
  • plateau (70000) L-SENSITIVE ⇒ the ≈0.34 moves with L ⇒
    (A)-flavor: estimator/L underconvergence contributes at that N.

PRE-REGISTERED (discriminant_exact_question_check):
 EXACT Q1: per sub rung (λ=1−δ, 8 §A δ), does local L=1e5 show the
  shape [m(70k)>NEAR_CLOCK AND m(75k)>NEAR_CLOCK AND m(100k)≤NEAR_CLOCK]?
  ALL 8 ⇒ CLIFF_REPRODUCES_LOCAL ; else CLIFF_NOT_REPRODUCED (flag).
 EXACT Q2: per rung, |m(N,1e5) − m(N,4e5)| ≤ §C-noise(N) at N∈{70k,100k}?
  (§C-noise = max over the contributing ensembles of the 16-φ spread.)
  ALL rungs plateau&resolved L-invariant ⇒ CLIFF_L_INVARIANT
   (L-stable ⇒ N-driven ⇒ (B)-consistent) ;
  any rung plateau(70k) L-sensitive ⇒ PLATEAU_L_SENSITIVE
   ((A)-flavor evidence ⇒ strengthens escalate-to-§D) ;
  else L_ROBUSTNESS_INDETERMINATE.
 NEAR_CLOCK = 0.05 (proposed-not-fixed; structure fixed). Server
 slicing sub means are read-only CROSS-REFERENCE for Q1 (reported as
 per-N |local−server| determinism deltas) — NOT spliced into any
 terminal (§5 apparatus-invariance: one clean local apparatus).

SCOPE. Instrument-mechanism diagnosis, sub-side only, in-line with
the probe. NEVER proves (A) (only DGY does); CLIFF_L_INVARIANT
supports (B)-consistency and PLATEAU_L_SENSITIVE is (A)-flavor — both
SURFACED for Will, NOT auto-adjudicated; does NOT defer/cancel §D and
does NOT decide bxtbmjoqv. No §3, no Class-II, Step-1 NOT
retro-adjudicated. Local WORKERS=18, MP thread-pinned, pure
deterministic ⇒ bit-identical-serial. Hardened (rawtable
persist-before-postproc + 64-ckpt + analyze-only). brief-and-hold
semantics: this runs under Will's explicit 6h forward-go, then HOLDS.
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
DELTAS = tuple(np.round(np.geomspace(0.005, 0.5, 8), 6))      # §A sub ladder
# (N, L) combos: L=1e5 at {70k,75k,100k} = local sit-then-cliff (Q1);
#                L=4e5 at {70k,100k}      = L-robustness vs 1e5 (Q2)
COMBOS = ((70000, 100000), (75025, 100000), (100000, 100000),
          (70000, 400000), (100000, 400000))
NEAR_CLOCK = 0.05                                             # proposed-not-fixed
OUT = os.path.join(HERE, "sub_cliff_L_robustness_results.json")
RAW = os.path.join(HERE, "sub_cliff_L_robustness_rawtable.json")
SLICING = os.path.join(HERE, "slicing_outer_t0_t2core_results.json")


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
             for d in DELTAS for (N, L) in COMBOS for p in PHIS]
    print("=" * 84)
    print(f"SUB-CLIFF L-ROBUSTNESS + LOCAL-REPRO — {WORKERS}w ; AM golden θ ; "
          f"ratio-free leg")
    print(f"  sub δ(8)={list(DELTAS)}")
    print(f"  (N,L) combos={COMBOS} ; {len(tasks)} tasks")
    print("  Q1 local-repro of sit-then-cliff ; Q2 L-invariance of plateau. "
          "Never proves (A); surfaced not adjudicated.")
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

    srv = {}
    if os.path.exists(SLICING):
        try:
            cl = json.load(open(SLICING))["classification"]
            for d in DELTAS:
                srv[round(d, 6)] = cl.get(f"sub|{d}", {}).get("means", {})
        except Exception as ex:
            srv = {"error": repr(ex)}

    per, q1_all, q2_plateau_sensitive, q2_any_indet = [], True, False, False
    for d in DELTAS:
        rec_d = {"delta": d, "lam_sub": round(1.0 - d, 6)}
        m, sp = {}, {}
        ok = True
        for (N, L) in COMBOS:
            a = ens(table, d, N, L)
            if a is None:
                ok = False; break
            m[(N, L)] = float(a.mean()); sp[(N, L)] = float(a.max() - a.min())
        if not ok:
            rec_d["error"] = True; per.append(rec_d)
            q1_all = False; q2_any_indet = True; continue
        # Q1 local sit-then-cliff shape at L=1e5
        m70, m75, m100 = m[(70000, 100000)], m[(75025, 100000)], m[(100000, 100000)]
        shape = bool(m70 > NEAR_CLOCK and m75 > NEAR_CLOCK and m100 <= NEAR_CLOCK)
        q1_all &= shape
        # Q2 L-invariance at plateau(70k) and resolved(100k)
        n70 = max(sp[(70000, 100000)], sp[(70000, 400000)])
        n100 = max(sp[(100000, 100000)], sp[(100000, 400000)])
        d70 = abs(m[(70000, 100000)] - m[(70000, 400000)])
        d100 = abs(m[(100000, 100000)] - m[(100000, 400000)])
        plat_inv = d70 <= n70
        res_inv = d100 <= n100
        if not plat_inv:
            q2_plateau_sensitive = True
        if not (plat_inv and res_inv) and plat_inv:
            q2_any_indet = True
        rec_d.update({
            "L1e5_means": {"70000": round(m70, 6), "75025": round(m75, 6),
                           "100000": round(m100, 6)},
            "Q1_sit_then_cliff_local": shape,
            "plateau70k_1e5": round(m[(70000, 100000)], 6),
            "plateau70k_4e5": round(m[(70000, 400000)], 6),
            "plateau70k_dL": round(d70, 6), "plateau70k_Cnoise": round(n70, 6),
            "plateau70k_L_invariant": bool(plat_inv),
            "resolved100k_1e5": round(m[(100000, 100000)], 6),
            "resolved100k_4e5": round(m[(100000, 400000)], 6),
            "resolved100k_L_invariant": bool(res_inv)})
        sv = srv.get(round(d, 6)) if isinstance(srv, dict) and "error" not in srv else None
        if sv:
            rec_d["xref_server_minus_local_L1e5"] = {
                k: round(float(sv[k]) - m[(int(k), 100000)], 6)
                for k in ("70000", "75025", "100000") if k in sv}
        per.append(rec_d)

    q1 = "CLIFF_REPRODUCES_LOCAL" if q1_all else "CLIFF_NOT_REPRODUCED"
    if q2_plateau_sensitive:
        q2 = "PLATEAU_L_SENSITIVE"
    elif q2_any_indet:
        q2 = "L_ROBUSTNESS_INDETERMINATE"
    else:
        q2 = "CLIFF_L_INVARIANT"
    rec = {"run": "sub-cliff L-robustness + local reproduction",
           "readings": {"A": "estimator/L defect", "B": "N-resolution crossover"},
           "combos": [list(c) for c in COMBOS], "deltas": list(DELTAS),
           "NEAR_CLOCK": NEAR_CLOCK, "Q1_terminal": q1, "Q2_terminal": q2,
           "per_rung": per, "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "Q1 CLIFF_NOT_REPRODUCED ⇒ env/version-specific (major). "
                   "Q2 CLIFF_L_INVARIANT ⇒ (B)-consistent (N-driven); "
                   "PLATEAU_L_SENSITIVE ⇒ (A)-flavor ⇒ strengthens §D. "
                   "NEVER proves (A); SURFACED not adjudicated; §D not "
                   "decided here; Step-1 not retro-adjudicated."}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    for p in per:
        if p.get("error"):
            print(f"  δ={p['delta']}  ERROR"); continue
        print(f"  δ={p['delta']:.6f}  L1e5{p['L1e5_means']}  Q1shape="
              f"{p['Q1_sit_then_cliff_local']}  plat70k 1e5={p['plateau70k_1e5']}"
              f" 4e5={p['plateau70k_4e5']} dL={p['plateau70k_dL']} "
              f"Cn={p['plateau70k_Cnoise']} Linv={p['plateau70k_L_invariant']}")
    print(f"  Q1: {q1}   Q2: {q2}   [{rec['total_s']}s] errors={len(errs)}")
    print("  Q1_not_repro⇒env-specific(major). Q2_L_invariant⇒(B)-consistent;")
    print("  PLATEAU_L_SENSITIVE⇒(A)-flavor⇒§D. Never proves (A); SURFACED,")
    print("  not adjudicated; §D not decided; Step-1 untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()
