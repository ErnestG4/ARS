"""
phase35a/sub_resolution_probe.py — CHEAP PRE-DGY PROBE (Will's
direction 2026-05-19, post slicing_outer HALT). PREPARED, awaiting
Will's explicit go — brief-and-hold; nothing runs on write.

CONTEXT. slicing_outer_t0_t2core (server, 768 tasks, clean HALT)
classified ALL 8 subcritical rungs INNER on a sit-then-cliff vary-N
signature {≈0.343 @70k, ≈0.334 @75k, ≈0.001-0.017 @100k}. §A worked
(routed to G1b-held, T0 returned NO verdict — the post-§Q3 success).
Two LIVE readings, NOT adjudicable from that run:
  (A) estimator defect — unfold_rotnum sub rotnum broken at N≤75k.
  (B) genuine resolution crossover — sub under-resolved below
      N_c∈(75k,100k); 0.343 = under-res plateau, ~0.01@100k =
      resolved near-clock AC.
Only validate-on-known-truth (the §D DGY campaign) discriminates
(A)/(B) definitively. THIS probe is the cheap pre-DGY filter Will
specified: it can make (B) *strongly favored* (and thereby defer the
full §D campaign) or land INDETERMINATE (⇒ escalate to §D). It can
NEVER prove (A) — by design; respecting that only DGY discriminates.

It also fixes the ROOT ambiguity Will identified: the cliff landed on
the LAST of the slicing run's 3 N-points — the §A 3-point-rider
biting in data (3 pts can't separate "still falling" from
"fell-and-flat"). Extending the sub N-set ABOVE the cliff resolves
exactly that.

PRE-REGISTERED (discriminant_exact_question_check):
 EXACT QUESTION: are the subcritical rungs RESOLVED by N=100k —
 i.e. is W1δ FLAT across N∈{100000,125000,150000} within the
 substrate's own §C φ-noise AND at the near-clock resolved level
 (≪ the ≈0.34 plateau, consistent with the ~0.001-0.017 seen at
 N=100k in the completed slicing run)?
 CODED TEST (per sub rung λ=1−δ, the 8 §A δ):
  - exact 16-φ∈[0,0.5) α-ensemble of W1δ at each N (L=1e5, golden θ);
  - §C noise = max over the 3 N of the per-N ensemble spread;
  - FLAT iff (max−min of the 3 ensemble-means) ≤ §C noise
    (the §A N-stable criterion, verbatim, now ABOVE the cliff);
  - NEAR-CLOCK iff the flat level ≤ NEAR_CLOCK_MAX (≪ plateau).
 Terminals (honest; NO terminal asserts (A) — only DGY can):
  SUB_RESOLVED_AT_100K_B_FAVORED — ALL 8 rungs FLAT & NEAR-CLOCK ⇒
    resolved by 100k ⇒ (B) strongly favored in this N-range; the
    full §D DGY campaign is deferrable (not cancelled — DGY remains
    the definitive (A)/(B) discriminator generally).
  SUB_NONFLAT_OR_PLATEAU_INDETERMINATE — any rung non-flat, or flat
    at the plateau, or mixed ⇒ (A)/(B) NOT discriminable here ⇒
    ESCALATE to the full §D Fib/DGY validate-on-known-truth.
 NEAR_CLOCK_MAX = 0.05 — proposed-not-fixed numeric; the structure
 (flat-AND-near-clock ⇒ B-favored; else INDETERMINATE→§D) is fixed.
 The "resolved anchor" cross-check: the completed slicing run's
 server N=100k sub values (numpy 2.4.5) are loaded read-only and
 compared to this probe's local N=100k (numpy 2.4.4) — a free
 cross-env DETERMINISM check (deterministic leg ⇒ must match; a
 mismatch would itself be (A)-relevant). NOT spliced into the
 verdict — the verdict triplet is one clean local apparatus (§5
 apparatus-invariance: recompute 100k locally, do NOT cross-env
 splice).

SCOPE: instrument-resolution diagnosis under the signed-off spec;
asymmetric label; sub-side ONLY (sup was N-stable/OUTER, no
resolution concern). NOT an AM discovery, NO §3, NO Class-II, does
NOT retro-adjudicate Step-1 (the banked-contrast caveat is a separate
flagged note). Local, WORKERS=18 (Will: back to local). MP
thread-pinned, pure deterministic ⇒ bit-identical-serial. Hardened
(rawtable persist-before-postproc + 64-ckpt + analyze-only re-run) —
the bzztfdy2n lesson. brief-and-hold; banked Step-1 untouched.
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

WORKERS = 18                                   # Will: back to local 18 threads
LITER = 100_000
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 6))
NS = (100000, 125000, 150000)                  # ABOVE the slicing-run cliff
DELTAS = tuple(np.round(np.geomspace(0.005, 0.5, 8), 6))   # §A ladder (sub side)
NEAR_CLOCK_MAX = 0.05                          # proposed-not-fixed; structure fixed
OUT = os.path.join(HERE, "sub_resolution_probe_results.json")
RAW = os.path.join(HERE, "sub_resolution_probe_rawtable.json")
SLICING = os.path.join(HERE, "slicing_outer_t0_t2core_results.json")


def cell(arg):
    """(delta, lam, N, phi) → (..., W1δ, err). Pure & deterministic."""
    delta, lam, N, phi = arg
    try:
        e = am_eigs(lam, int(N), float(phi))
        w = float(W1d(unfold_rotnum(e, lam, GOLDEN, LITER, phis=(float(phi),))))
        return (float(delta), float(lam), int(N), float(phi), w, None)
    except Exception as ex:
        return (float(delta), float(lam), int(N), float(phi), None, repr(ex))


def _dump_raw(table, total):
    recs = [[float(k[0]), int(k[1]), float(k[2]), v] for k, v in table.items()]
    json.dump({"n": len(recs), "of": total, "recs": recs}, open(RAW, "w"))


def _load_raw():
    d = json.load(open(RAW))
    t = {}
    for dl, N, ph, w in d["recs"]:
        t[(round(float(dl), 6), int(N), round(float(ph), 6))] = w
    return t, d.get("n", len(t)), d.get("of")


def ens(table, delta, N):
    v = [table.get((round(delta, 6), N, round(p, 6))) for p in PHIS]
    return None if any(x is None for x in v) else np.asarray(v, float)


def main():
    t0 = time.time()
    tasks = [(d, round(1.0 - d, 6), N, p)        # subcritical: λ = 1 − δ
             for d in DELTAS for N in NS for p in PHIS]
    print("=" * 84)
    print(f"SUB-RESOLUTION PROBE — {WORKERS}w ; AM golden θ ; ratio-free leg ; "
          f"L={LITER}")
    print(f"  sub δ-ladder(8)={list(DELTAS)} ; NS(>cliff)={NS} ; "
          f"{len(tasks)} tasks")
    print("  (B)-favored or INDETERMINATE→§D ; NEVER proves (A). "
          "Pre-DGY filter.")
    print("=" * 84, flush=True)

    errs, table = [], None
    if os.path.exists(RAW):
        tr, nr, ofr = _load_raw()
        if nr == ofr == len(tasks):
            table = tr
            print(f"  ANALYZE-ONLY: complete raw table ({nr}) — skip compute.",
                  flush=True)
    if table is None:
        table, done = {}, 0
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            for f in as_completed([ex.submit(cell, a) for a in tasks]):
                d, lam, N, phi, w, err = f.result()
                table[(round(d, 6), N, round(phi, 6))] = w
                done += 1
                if err:
                    errs.append({"delta": d, "N": N, "phi": phi, "err": err})
                    print(f"  ERR δ={d} N={N} φ={phi}: {err}", flush=True)
                if done % 64 == 0:
                    _dump_raw(table, len(tasks))
                    print(f"  … {done}/{len(tasks)} [{time.time()-t0:.0f}s]",
                          flush=True)
        _dump_raw(table, len(tasks))
        print(f"  raw table persisted ({len(table)}) — postproc free to re-run.",
              flush=True)

    # cross-env determinism cross-check vs the completed server run @100k
    xcheck = {}
    if os.path.exists(SLICING):
        try:
            sl = json.load(open(SLICING))["classification"]
            for d in DELTAS:
                srv = sl.get(f"sub|{d}", {}).get("means", {}).get("100000")
                loc = ens(table, d, 100000)
                if srv is not None and loc is not None:
                    xcheck[str(d)] = {"server_2.4.5": round(float(srv), 6),
                                      "local_2.4.4_mean": round(float(loc.mean()), 6),
                                      "abs_diff": round(abs(float(srv) - float(loc.mean())), 6)}
        except Exception as ex:
            xcheck = {"error": repr(ex)}

    per = []
    all_flat_nearclock = True
    for d in DELTAS:
        means, spreads = {}, {}
        ok = True
        for N in NS:
            a = ens(table, d, N)
            if a is None:
                ok = False; break
            means[N] = float(a.mean()); spreads[N] = float(a.max() - a.min())
        if not ok:
            per.append({"delta": d, "error": True}); all_flat_nearclock = False
            continue
        noise = max(spreads.values())
        mvals = [means[N] for N in NS]
        flat = (max(mvals) - min(mvals)) <= noise
        near_clock = max(mvals) <= NEAR_CLOCK_MAX
        rung_b = bool(flat and near_clock)
        all_flat_nearclock &= rung_b
        per.append({"delta": d, "lam_sub": round(1.0 - d, 6),
                    "means": {str(N): round(means[N], 6) for N in NS},
                    "C_noise": round(noise, 6),
                    "mean_range": round(max(mvals) - min(mvals), 6),
                    "flat": bool(flat), "level": round(max(mvals), 6),
                    "near_clock": bool(near_clock), "B_favored_rung": rung_b})

    terminal = ("SUB_RESOLVED_AT_100K_B_FAVORED" if all_flat_nearclock
                else "SUB_NONFLAT_OR_PLATEAU_INDETERMINATE")
    rec = {"probe": "sub-resolution >cliff (pre-DGY filter for slicing HALT)",
           "readings": {"A": "estimator defect", "B": "resolution crossover"},
           "substrate": "AM golden θ; subcritical λ=1−δ; ratio-free leg",
           "NS": list(NS), "deltas": list(DELTAS), "L": LITER,
           "NEAR_CLOCK_MAX": NEAR_CLOCK_MAX, "per_rung": per,
           "xcheck_vs_server_100k": xcheck, "terminal": terminal,
           "note": "B_favored ⇒ §D deferrable (not cancelled — DGY remains "
                   "definitive (A)/(B)). INDETERMINATE ⇒ escalate to §D. "
                   "NEVER proves (A). Step-1 NOT retro-adjudicated.",
           "errors": errs, "total_s": round(time.time() - t0, 0)}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    for p in per:
        if p.get("error"):
            print(f"  δ={p['delta']}  ERROR"); continue
        print(f"  δ={p['delta']:.6f} λ={p['lam_sub']:.6f}  means={p['means']}  "
              f"range={p['mean_range']:.5f} §Cnoise={p['C_noise']:.5f}  "
              f"flat={p['flat']} near_clock={p['near_clock']} "
              f"→ B_rung={p['B_favored_rung']}")
    if xcheck and "error" not in xcheck:
        md = max((v["abs_diff"] for v in xcheck.values()), default=0.0)
        print(f"  cross-env @100k max|server2.4.5 − local2.4.4| = {md:.6f} "
              f"(deterministic leg ⇒ ~0 expected)")
    print(f"  TERMINAL: {terminal}  [{rec['total_s']}s] errors={len(errs)}")
    print("  B-favored ⇒ §D deferrable; INDETERMINATE ⇒ §D. Never proves (A).")
    print("  Instrument-resolution diagnosis; no §3/Class-II; Step-1 untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()
