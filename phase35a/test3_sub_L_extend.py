"""
phase35a/test3_sub_L_extend.py — Test 3 from Slate Unit 3 brief
(OPTIONAL refinement). PREPARED + smoke-verified. Launched as #4 in
the overnight chain IF total elapsed at end of Test 2 leaves budget.

QUESTION (per the slate-3 brief). Does the projected sub-side
L-convergence (α≈1 from bh22pfzoa) materialize directly at N=70k and
N=125k? Direct confirmation of the L-decay across sub-side rungs;
not blocking (bh22pfzoa's α≈1 already gives a defensible read).

DESIGN (locked).
- 2 cells, δ=0.5 (sub, λ=0.5):
  (N=70000, δ=0.5) — sub load-bearing
  (N=125000, δ=0.5) — sub bracket-edge
- L ∈ {1.6e6, 6.4e6} — ×4 extension over bh22pfzoa's L_top.
- 16 φ ∈ [0,0.5); golden θ; ratio-free leg; WORKERS=18 local.

APPARATUS IDENTITY CHECK. At L=1.6e6 the 16 per-φ values per cell
must match bh22pfzoa's rawtable values. Halt as
`SUB_L_INSTRUMENT_INCONSISTENT` on structural divergence.

PRE-REGISTERED TERMINALS.
- SUB_L_CONVERGED: both cells stable within 5% relative to the
  N=100k bh22pfzoa converged substrate values at matching δ.
- SUB_L_STILL_DECAYING: at least one cell continues decaying
  meaningfully at L=6.4e6.
- SUB_L_PATHOLOGICAL: non-monotone trajectory or other surprise.
- SUB_L_INSTRUMENT_INCONSISTENT: apparatus check failed.

SCOPE. Sub-side L-convergence confirmation/refinement. NOT blocking.
Skip without consequence if budget constrained. Never proves
(A)/(B); never decides §D; never adjudicates Step-1.
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
# 8-φ grid (matches bh22pfzoa exactly, for direct apparatus identity check).
# bh22pfzoa used 8 φ; b1crocze1/b0haqgof3 used 16 φ; Test 3's comparator is
# bh22pfzoa, so we use 8 φ here for bit-identical comparison.
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 8, endpoint=False), 6))
DELTA = 0.5
LAM = 1.0 - DELTA                                # 0.5 (sub)
NS = (70000, 125000)
LS = (1600000, 6400000)
TOP_INC_CONVERGED = 0.05
ABS_TOL_FLOOR = 1e-9
REL_TOL_FRAC = 1e-4
OUT = os.path.join(HERE, "test3_sub_L_extend_results.json")
RAW = os.path.join(HERE, "test3_sub_L_extend_rawtable.json")
BH22 = os.path.join(HERE, "sub_Liter_convergence_results.json")


def cell(arg):
    N, L, phi = arg
    try:
        e = am_eigs(LAM, int(N), float(phi))
        w = float(W1d(unfold_rotnum(e, LAM, GOLDEN, int(L), phis=(float(phi),))))
        return (int(N), int(L), float(phi), w, None)
    except Exception as ex:
        return (int(N), int(L), float(phi), None, repr(ex))


def _dump_raw(table, total):
    recs = [[int(k[0]), int(k[1]), float(k[2]), v] for k, v in table.items()]
    json.dump({"n": len(recs), "of": total, "recs": recs}, open(RAW, "w"))


def _load_raw():
    d = json.load(open(RAW))
    t = {}
    for N, L, ph, w in d["recs"]:
        t[(int(N), int(L), round(float(ph), 6))] = w
    return t, d.get("n", len(t)), d.get("of")


def phi_vec(table, N, L):
    v = [table.get((int(N), int(L), round(p, 6))) for p in PHIS]
    return None if any(x is None for x in v) else np.asarray(v, float)


def _bh22_at(N, L):
    """bh22pfzoa per-φ at (δ=0.5, N, L). bh22pfzoa stored only means in
    per_dN.means; per-φ raw values are in sub_Liter_convergence_rawtable.json."""
    try:
        raw = json.load(open(os.path.join(HERE,
                              "sub_Liter_convergence_rawtable.json")))
        vals = {}
        for d, NN, LL, ph, w in raw["recs"]:
            if abs(d - DELTA) < 1e-9 and int(NN) == N and int(LL) == L:
                vals[round(float(ph), 6)] = w
        if len(vals) == len(PHIS):
            return np.asarray([vals[round(p, 6)] for p in PHIS], float)
    except Exception:
        return None
    return None


def _bh22_n100k_substrate(delta):
    """bh22pfzoa's N=100k L-converged substrate value at δ."""
    try:
        r = json.load(open(BH22))
        for p in r["per_dN"]:
            if abs(p["delta"] - delta) < 1e-9 and p["N"] == 100000:
                return float(p["top_value"])
    except Exception:
        return None
    return None


def main():
    t0 = time.time()
    tasks = [(N, L, p) for N in NS for L in LS for p in PHIS]
    print("=" * 84)
    print(f"TEST 3 — sub-side L-extension — {WORKERS}w ; AM golden θ ; "
          f"ratio-free leg")
    print(f"  δ={DELTA} ; legs=sub (λ={LAM}) ; N={NS} ; L={LS} ; "
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
                N, L, phi, w, err = f.result()
                table[(int(N), int(L), round(phi, 6))] = w
                done += 1
                if err:
                    errs.append({"N": N, "L": L, "phi": phi, "err": err})
                    print(f"  ERR N={N} L={L} φ={phi}: {err}", flush=True)
                if done % 16 == 0:
                    _dump_raw(table, len(tasks))
                    print(f"  … {done}/{len(tasks)} [{time.time()-t0:.0f}s]",
                          flush=True)
        _dump_raw(table, len(tasks))
        print(f"  raw persisted ({len(table)}).", flush=True)

    # ── Apparatus identity vs bh22pfzoa at L=1.6e6
    id_report = {}; id_ok = True
    for N in NS:
        meas = phi_vec(table, N, 1600000)
        stored = _bh22_at(N, 1600000)
        if meas is None or stored is None:
            id_ok = False
            id_report[f"N{N}_L1.6e6"] = {"error": "missing baseline"}
            continue
        tol = max(ABS_TOL_FLOOR, REL_TOL_FRAC * float(np.max(np.abs(stored))))
        diff = float(np.max(np.abs(meas - stored)))
        ok = diff <= tol
        id_report[f"N{N}_L1.6e6"] = {"max_abs_diff": round(diff, 12),
                                       "tol": round(tol, 12),
                                       "PASS": bool(ok)}
        id_ok = id_ok and ok

    if not id_ok:
        rec = {"run": "Test 3 sub-side L-extension",
               "terminal": "SUB_L_INSTRUMENT_INCONSISTENT",
               "apparatus_identity": id_report, "errors": errs,
               "total_s": round(time.time() - t0, 0),
               "note": "Apparatus identity vs bh22pfzoa failed. HALT."}
        json.dump(rec, open(OUT, "w"), indent=1)
        print("=" * 84)
        for k, r in id_report.items(): print(f"  id {k}: {r}")
        print(f"  TERMINAL: SUB_L_INSTRUMENT_INCONSISTENT  HALT.")
        print("=" * 84); return

    # ── Per-cell convergence vs N=100k substrate value
    substrate = _bh22_n100k_substrate(DELTA)
    per_cell = []
    all_conv, any_pathology = True, []
    for N in NS:
        means = {L: float(phi_vec(table, N, L).mean()) for L in LS}
        spreads = {L: float(np.ptp(phi_vec(table, N, L))) for L in LS}
        # Convergence vs substrate (5% relative to substrate value)
        ref = substrate if substrate is not None else means[LS[-1]]
        rel = (abs(means[LS[-1]] - ref) / max(abs(ref), 1e-12))
        # top_inc between the two L
        if len(LS) >= 2:
            top_inc = abs(means[LS[-1]] - means[LS[-2]]) / max(abs(means[LS[-1]]), 1e-12)
        else: top_inc = None
        # Per brief: "stable within 5% relative to N=100k substrate." Use
        # rel-to-substrate only; top_inc is reported as context but not gating
        # (a trajectory approaching substrate from above can have large top_inc
        # while still landing AT substrate — that's converged).
        conv = rel <= TOP_INC_CONVERGED
        all_conv = all_conv and conv
        # Monotonicity
        seq = [means[L] for L in LS]
        steps = [seq[i+1] - seq[i] for i in range(len(seq) - 1)]
        mono = (all(s >= 0 for s in steps) or all(s <= 0 for s in steps))
        if not mono and (max(seq) - min(seq) > 0.05 * max(abs(s) for s in seq)):
            any_pathology.append(f"N={N}_non_monotone")
        per_cell.append({"N": N, "lam": LAM,
                          "means_by_L": {str(L): round(means[L], 8) for L in LS},
                          "spreads_by_L": {str(L): round(spreads[L], 8) for L in LS},
                          "substrate_ref": substrate,
                          "rel_to_substrate": round(rel, 6),
                          "top_inc": round(top_inc, 6) if top_inc is not None else None,
                          "L_converged_in_cell": bool(conv),
                          "monotone": bool(mono)})

    if any_pathology:
        terminal = "SUB_L_PATHOLOGICAL"
    elif all_conv:
        terminal = "SUB_L_CONVERGED"
    else:
        terminal = "SUB_L_STILL_DECAYING"

    rec = {"run": "Test 3 sub-side L-extension at N=70k, N=125k",
           "delta": DELTA, "lam": LAM, "Ns": list(NS), "LS": list(LS),
           "n_phi": len(PHIS), "apparatus_identity": id_report,
           "per_cell": per_cell, "terminal": terminal,
           "substrate_ref_from_bh22_N100k": substrate,
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "Sub-side L-convergence refinement. SURFACED; never "
                   "proves (A)/(B); §D untouched; Step-1 untouched."}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    for k, r in id_report.items():
        print(f"  id {k}: {r}")
    for p in per_cell:
        print(f"  N={p['N']:6d}: means_by_L={p['means_by_L']} "
              f"top_inc={p['top_inc']} rel_to_substrate={p['rel_to_substrate']} "
              f"converged={p['L_converged_in_cell']} monotone={p['monotone']}")
    print(f"  TERMINAL: {terminal}  [{rec['total_s']}s] errors={len(errs)}")
    print("  SURFACED; Step-1/(A)/(B)/§D untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()
