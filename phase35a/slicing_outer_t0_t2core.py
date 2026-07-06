"""
phase35a/slicing_outer_t0_t2core.py — SLICING-COMPARISON: the
outer-rung new T0 + T2-core run (Will's explicit compute-go
2026-05-19, "run the outer-rung new T0, T2-core"). Signed-off spec:
slate unit 2 rev-3 (§A ladder/δ-conditional classification, §B
w-ladder, §C floor) + rev-3 brief §4 (T0, T2-core).

SUBSTRATE: almost-Mathieu, golden θ, throughout. (75025=F₂₅ here is
only an N value — a commensurate point for the §A apparatus
N-robustness check; the BAR-scoped Fibonacci/DGY *substrate*
campaign is §D, G1b-held, SEPARATE, NOT invoked here.) Ratio-free
rotation-number leg (`unfold_rotnum`, no ref-N — G1a-met). MP 50w/
56-core (combust@10.0.0.225 dev box) thread-pinned, pure
deterministic ⇒ bit-identical-serial (worker count does not affect
results — only wall time).

"Outer-rung" is OPERATIONAL, not a hard δ-line (slate-2 §A rev-3,
the §Q3 don't-assume-a-boundary discipline): the per-rung N-drift
classification decides it; T0/T2-core then run on the OUTER rungs
only. Inner/ambiguous rungs are G1b-held (pending the §D campaign) —
NOT measured here.

PRE-REGISTERED (discriminant_exact_question_check — three verdict
determinations, mandatory & recorded; each coded test is the EXACT
question, verbatim from the signed-off spec, not a proxy):

 (I) PER-RUNG δ-CONDITIONAL CLASSIFICATION (§A rev-3).
  EXACT Q: per bracket rung, across N∈{70000,75025,100000}, is the
  W1δ φ-ensemble-mean N-trajectory a *separable monotone drift toward
  the off-critical expectation* (the rung crossing N_c(δ) — a
  G1b-class resolution-crossover signature), or N-stable, or
  uncallable?
  CODED: per (λ,N) the exact 16-φ∈[0,0.5) α-ensemble of W1δ
  (L=1e5, golden θ); §C noise scale = max over the 3 N of the
  per-N ensemble spread (max−min). Then:
   • N-STABLE  — total N-swing of the ensemble-mean ≤ §C noise scale
     ⇒ rung OUTER (G2-scoped, MET; runnable now).
   • RELIABLE-MONOTONE-DRIFT — ensemble-mean monotone in N (both
     consecutive steps same sign) AND |total swing| ≥ SEP·(§C noise
     scale) AND directed toward the bracket's off-critical
     expectation (sub/AC: W1δ ↓ toward clock-like as N↑; sup/PP:
     W1δ ↑ toward Poisson-like) ⇒ rung INNER / critical-adjacent
     (G1b-class; G1b-HELD; excluded from the non-singular structure).
   • AMBIGUOUS — neither cleanly ⇒ default G1b-CONDITIONAL
     (conservative; Will §A rider — the campaign does not get to call
     a thin/uncallable rung OUTER by under-power).
  SEP (separability factor) = 2.0 — proposed-not-fixed numeric within
  the fixed reliability structure; ambiguous defaults conservative so
  under-power is safe. Reports the operationally-MEASURED
  δ_res(N≈7e4) = largest δ classified inner-or-ambiguous (not a
  pre-guessed constant).

 (II) T0-EXCISE on OUTER rungs, across the §B w-ladder.
  EXACT Q: at fixed primary N=70000, with λ=1+neighbourhood excised,
  is the subcritical(λ=1−δ) vs supercritical(λ=1+δ) W1δ contrast §C-
  significant at MATCHED detuning, and is the conclusion WIDTH-ROBUST
  across w∈{0.01,0.02,0.04,0.08}?
  CODED: §C criterion VERBATIM (disjoint AND gap ≥ max(sub_spread,
  sup_spread) on the φ-ensembles) per matched-δ outer pair; per w,
  the contrast uses only OUTER rungs with δ>w. WIDTH_ROBUST iff the
  significant/not conclusion is invariant across the whole w-ladder;
  else WIDTH_DEPENDENT — the w-dependence IS the finding (localizes &
  names the w at which it changes). No tuning: reported across the
  ENTIRE ladder.

 (III) T2-CORE on OUTER rungs (two-sided limit, fixed N).
  EXACT Q: at fixed N=70000, does each bracket's W1δ ensemble-mean
  trajectory approach a limiting value as δ→0 over the OUTER
  (resolved) δ-range — the critical slice as a *derived* two-sided-
  limit object?
  CODED: per side, the last-step change in ensemble-mean over the
  inner-most OUTER rungs vs the §C noise scale. CONVERGED iff
  |last-step Δ| ≤ §C noise scale at the inner-most outer δ; else
  UNREACHED. CEILING (rev-3 §4 T2, stated not hedged): this is NOT a
  direct λ=1 measurement; by construction the limit is taken only
  over OUTER rungs (the near-critical rungs that would probe δ→0 are
  G1b-HELD), so T2-core characterises the approach over the resolved
  range ONLY — `..._UNREACHED_BY_CONSTRUCTION` is the expected honest
  landing unless the outer range already shows clean convergence
  before δ_res.

SCOPE: instrument/methodology measurement under the signed-off spec.
Asymmetric labels — NEVER "AM characterized," never a discovery; no
§3 adjudication; no Class-II. T0 ceiling: says NOTHING about λ=1.
brief-and-hold beyond this go; banked Step-1 untouched; G1b-held
items (T1/T1′/T2-N-refine/inner-δ-rungs) NOT run here; T3 §3-(A)-held.
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

WORKERS = 50
LITER = 100_000
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 6))
NS = (70000, 75025, 100000)            # primary 70000 + robustness {F25, 1e5}
NPRIMARY = 70000
SEP = 2.0                              # §A separability factor (proposed-not-fixed)
OUT = os.path.join(HERE, "slicing_outer_t0_t2core_results.json")
CKPT = os.path.join(HERE, "slicing_outer_t0_t2core_ckpt.json")
RAW = os.path.join(HERE, "slicing_outer_t0_t2core_rawtable.json")

# §A symmetric geometric detuning ladder, δ∈[0.005,0.5], 8/side (signed off)
DELTAS = tuple(np.round(np.geomspace(0.005, 0.5, 8), 6))
W_LADDER = (0.01, 0.02, 0.04, 0.08)    # §B declared excision-width cut

# hard-assert F25 (the burned off-by-one — standard indexing F0=0,F1=1)
def _fib_assert():
    a, b = 0, 1
    for _ in range(25):
        a, b = b, a + b
    assert a == 75025, f"F25 must be 75025, got {a}"
_fib_assert()


def cell(arg):
    """(side, delta, lam, N, phi) → (..., W1δ, err). Pure & deterministic."""
    side, delta, lam, N, phi = arg
    try:
        e = am_eigs(lam, int(N), float(phi))
        w = float(W1d(unfold_rotnum(e, lam, GOLDEN, LITER, phis=(float(phi),))))
        return (side, float(delta), float(lam), int(N), float(phi), w, None)
    except Exception as ex:
        return (side, float(delta), float(lam), int(N), float(phi), None, repr(ex))


def ens(table, side, delta, N):
    """φ-ensemble (list over PHIS) of W1δ at (side,δ,N); None if any missing."""
    v = [table.get((side, round(delta, 6), N, round(p, 6))) for p in PHIS]
    return None if any(x is None for x in v) else np.asarray(v, float)


def classify(table, side, delta):
    """§A rev-3 operational δ-conditional classification across NS."""
    means, floors = {}, {}
    for N in NS:
        a = ens(table, side, delta, N)
        if a is None:
            return {"class": "ERROR", "delta": delta, "side": side}
        means[N] = float(a.mean()); floors[N] = float(a.max() - a.min())
    noise = max(floors.values())                       # §C noise scale
    seq = [means[N] for N in NS]                        # N-ordered (NS ascending)
    swing = seq[-1] - seq[0]
    steps = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
    monotone = (all(s >= 0 for s in steps) or all(s <= 0 for s in steps))
    # off-critical expectation direction: sub/AC ⇒ resolves DOWN (toward
    # clock-like) as N↑ ; sup/PP ⇒ resolves UP (toward Poisson-like).
    toward_off = (swing < 0) if side == "sub" else (swing > 0)
    if abs(swing) <= noise:
        cls = "OUTER"                                   # N-stable ⇒ G2/runnable
    elif monotone and abs(swing) >= SEP * noise and toward_off:
        cls = "INNER"                                   # G1b-class / G1b-held
    else:
        cls = "AMBIGUOUS"                               # ⇒ G1b-conditional
    return {"class": cls, "delta": float(delta), "side": side,
            "means": means, "C_noise": round(noise, 6),
            "swing": round(swing, 6), "monotone": monotone,
            "toward_off_critical": toward_off}


def _dump_raw(table, total):
    recs = [[k[0], float(k[1]), int(k[2]), float(k[3]), v]
            for k, v in table.items()]
    json.dump({"n": len(recs), "of": total, "recs": recs}, open(RAW, "w"))


def _load_raw():
    d = json.load(open(RAW))
    t = {(s, round(float(dl), 6), int(N), round(float(ph), 6)): w
         for s, dl, N, ph, w in d["recs"]}
    return t, d.get("n", len(t)), d.get("of")


def main():
    t0 = time.time()
    tasks = []
    for d in DELTAS:
        tasks += [("sub", d, round(1.0 - d, 6), N, p) for N in NS for p in PHIS]
        tasks += [("sup", d, round(1.0 + d, 6), N, p) for N in NS for p in PHIS]
    print("=" * 90)
    print(f"SLICING OUTER-RUNG T0 + T2-CORE — {WORKERS}w ; AM golden θ ; "
          f"ratio-free leg ; L={LITER}")
    print(f"  δ-ladder(8/side)={list(DELTAS)} ; NS={NS} ; "
          f"w-ladder={W_LADDER} ; SEP={SEP}")
    print(f"  {len(tasks)} tasks. Outer = operational (§A drift "
          f"classification); inner/ambiguous ⇒ G1b-held, NOT measured.")
    print("=" * 90, flush=True)
    errs = []
    table = None
    if os.path.exists(RAW):
        t_raw, n_raw, of_raw = _load_raw()
        if n_raw == of_raw == len(tasks):
            table = t_raw
            print(f"  ANALYZE-ONLY: loaded COMPLETE raw table "
                  f"({n_raw}/{of_raw}) — skipping the ~2h compute.",
                  flush=True)
        else:
            print(f"  raw table present but INCOMPLETE "
                  f"({n_raw}/{of_raw}) — recomputing from scratch.",
                  flush=True)
    if table is None:
        table, done = {}, 0
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            for f in as_completed([ex.submit(cell, a) for a in tasks]):
                side, d, lam, N, phi, w, err = f.result()
                table[(side, round(d, 6), N, round(phi, 6))] = w
                done += 1
                if err:
                    errs.append({"side": side, "delta": d, "N": N,
                                 "phi": phi, "err": err})
                    print(f"  ERR {side} δ={d} N={N} φ={phi}: {err}",
                          flush=True)
                if done % 64 == 0:
                    _dump_raw(table, len(tasks))      # REAL table ckpt
                    print(f"  … {done}/{len(tasks)} "
                          f"[{time.time()-t0:.0f}s]", flush=True)
        # Persist the full raw table BEFORE any post-processing, so a
        # post-proc bug can never again discard the ~2h compute (the
        # bzztfdy2n lesson). A re-run is then instant analyze-only.
        _dump_raw(table, len(tasks))
        print(f"  raw table persisted ({len(table)}/{len(tasks)}) — "
              f"post-processing now free to re-run.", flush=True)

    # ── (I) classification ────────────────────────────────────────────────
    cls = {}
    for d in DELTAS:
        for side in ("sub", "sup"):
            cls[(side, round(d, 6))] = classify(table, side, d)
    outer = {s: sorted(d for d in DELTAS
                       if cls[(s, round(d, 6))]["class"] == "OUTER")
             for s in ("sub", "sup")}
    inner_or_amb = [d for d in DELTAS for s in ("sub", "sup")
                    if cls[(s, round(d, 6))]["class"] in ("INNER", "AMBIGUOUS")]
    delta_res = max(inner_or_amb) if inner_or_amb else None   # measured boundary

    # ── (II) T0-Excise on OUTER rungs across the §B w-ladder (fixed N) ─────
    def sig_pair(side_a, side_b, d):
        a = ens(table, side_a, d, NPRIMARY); b = ens(table, side_b, d, NPRIMARY)
        if a is None or b is None:
            return None
        lo, hi = (a, b) if a.mean() <= b.mean() else (b, a)
        gap = hi.min() - lo.max()
        floor = max(a.max() - a.min(), b.max() - b.min())     # §C verbatim
        return {"delta": float(d), "gap": round(float(gap), 6),
                "C_floor": round(float(floor), 6),
                "disjoint": bool(gap > 0),
                "significant": bool(gap > 0 and gap >= floor)}
    t0_w = {}
    for w in W_LADDER:
        pairs = [sig_pair("sub", "sup", d) for d in DELTAS
                 if d > w and d in outer["sub"] and d in outer["sup"]]
        pairs = [p for p in pairs if p]
        concl = ("ALL_SIGNIFICANT" if pairs and all(p["significant"] for p in pairs)
                 else "NONE_SIGNIFICANT" if pairs and not any(p["significant"] for p in pairs)
                 else "MIXED" if pairs else "NO_OUTER_PAIRS")
        t0_w[w] = {"matched_pairs": pairs, "conclusion": concl}
    concls = {v["conclusion"] for v in t0_w.values()
              if v["conclusion"] != "NO_OUTER_PAIRS"}
    t0_terminal = ("T0_WIDTH_ROBUST_" + concls.pop()
                   if len(concls) == 1 else
                   "T0_WIDTH_DEPENDENT" if len(concls) > 1 else
                   "T0_NO_OUTER_PAIRS")

    # ── (III) T2-core on OUTER rungs (two-sided limit, fixed N) ────────────
    t2 = {}
    for side in ("sub", "sup"):
        od = outer[side]
        if len(od) < 2:
            t2[side] = {"terminal": "T2CORE_INSUFFICIENT_OUTER", "outer": od}
            continue
        od_in = sorted(od)                                   # δ ascending → δ→0 at head
        m = [float(ens(table, side, d, NPRIMARY).mean()) for d in od_in]
        noise_in = max(np.ptp(ens(table, side, od_in[0], N)) for N in NS)
        last_step = abs(m[1] - m[0])                         # innermost-outer step
        reached = last_step <= noise_in
        # honest: limit is over OUTER range only — inner rungs (δ→0) G1b-held
        term = ("T2CORE_LIMIT_REACHED_OVER_OUTER_RANGE" if reached else
                "T2CORE_LIMIT_UNREACHED_BY_CONSTRUCTION")
        t2[side] = {"terminal": term, "outer_deltas": od_in,
                    "ens_means": [round(x, 6) for x in m],
                    "innermost_outer_step": round(last_step, 6),
                    "noise_at_innermost": round(float(noise_in), 6),
                    "ceiling": "NOT a direct λ=1 measurement; limit over "
                               "OUTER (resolved) range only — near-critical "
                               "rungs G1b-held"}

    rec = {"spec": "slate-2 rev-3 §A/§B/§C + rev-3 brief §4 T0/T2-core",
           "substrate": "AM golden θ (75025=F25 is an N value only; "
                        "§D Fib/DGY substrate campaign is separate/G1b-held)",
           "ratio_free_leg": True, "deltas": list(DELTAS), "Ns": list(NS),
           "Nprimary": NPRIMARY, "w_ladder": list(W_LADDER), "SEP": SEP,
           "classification": {f"{s}|{d}": cls[(s, round(d, 6))]
                              for d in DELTAS for s in ("sub", "sup")},
           "outer": {k: [float(x) for x in v] for k, v in outer.items()},
           "delta_res_measured": (float(delta_res) if delta_res else None),
           "T0_w_ladder": {str(k): v for k, v in t0_w.items()},
           "T0_terminal": t0_terminal,
           "T2core": t2,
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "scope": "instrument/methodology under signed-off spec; "
                    "asymmetric label; NOT AM-characterized/§3/Class-II; "
                    "T0 says nothing about λ=1; brief-and-hold; "
                    "Step-1 untouched"}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 90)
    print(f"  (I) outer sub={outer['sub']} sup={outer['sup']} ; "
          f"measured δ_res(N≈7e4)={delta_res}")
    print(f"  (II) T0 terminal: {t0_terminal}")
    for w in W_LADDER:
        print(f"       w={w}: {t0_w[w]['conclusion']}")
    print(f"  (III) T2-core: sub={t2['sub']['terminal']} "
          f"sup={t2['sup']['terminal']}")
    print(f"  [{rec['total_s']}s] errors={len(errs)}")
    print("  Instrument/methodology under signed-off spec. T0 says NOTHING")
    print("  about λ=1. Inner/ambiguous rungs G1b-held (not measured here).")
    print("  Asymmetric label; no §3; no Class-II; brief-and-hold; "
          "Step-1 untouched.")
    print("=" * 90)


if __name__ == "__main__":
    main()
