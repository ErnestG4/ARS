"""
phase35a/test1_flipN_phi.py — Test 1 from Slate Unit 3 brief, with
C2 (Fibonacci-N spot-check) folded in. PREPARED + smoke-verified.
Launched as #1 in the overnight chain.

QUESTION (per the slate-3 brief). Does the L=1e5 φ-contamination
magnitude at the sensitivity flip-N (N≈4.3e4) match the magnitude at
N=70k (b1crocze1/b0haqgof3), or does it differ structurally with N?
+ C2: does the Fibonacci-commensurate N=46368 (=F₂₄) anywhere between
{4.3e4, 5e4} give an anomalous contamination ratio?

DESIGN (locked).
- 6 cells, all δ=0.5: 3 N × 2 legs (sub λ=0.5, sup λ=1.5).
  N ∈ {43000, 46368 (=F₂₄, C2 add), 50000}.
- 16-φ ensemble (matches Step-1 / b1crocze1 / b0haqgof3 verbatim).
- L ∈ {1e5, 4e5, 1.6e6} (mirror b1crocze1/b0haqgof3 ladder).
- Golden θ; ratio-free leg (`unfold_rotnum`); WORKERS=18 (local).
- Hardened (rawtable persist + 32-ckpt + analyze-only).

APPARATUS IDENTITY CHECK. At (δ=0.5, N=50000, L=1e5):
  measured sub spread vs sensitivity_confirm.sub_spread@N=5e4=2.92e-04
  measured sup spread vs sensitivity_confirm.sup_spread@N=5e4=1.22862e-01
Tolerance: max(1e-9, 1e-4 × stored) (bit-determinism abs, with relax
for tiny). If either fails: terminal `FLIP_N_INSTRUMENT_INCONSISTENT`
and HALT (no per-cell terminals, surface for diagnostic).

PER-CELL ANALYSIS. Same as b1crocze1/b0haqgof3:
  per L: spread_L = ptp_φ(W1δ); mean_L = mean_φ(W1δ).
  per-φ shift: Δw(φ) = w(L=1e5, φ) − w(L_top, φ).
  ratio = ptp_φ(Δw) / spread@L=1e5.

PER-CELL TERMINAL (each cell):
  PHI_COMMON_MODE (ratio ≤ 0.25), PHI_DEPENDENT (≥ 1.0),
  PHI_INDETERMINATE (between).

PER-LEG RATIO-VS-N (primary brief terminal). Compare each leg's ratio
at flip-N={43000,50000} (excluding C2 N=46368) to the b1crocze1
(sub) or b0haqgof3 (sup) ratio at N=70k. 30% deviation threshold:
  FLIP_N_PHI_RATIO_MATCHES_N70K   — both N=4.3e4 and N=5e4 ratios
   within 30% of N=70k ratio on both legs.
  FLIP_N_PHI_RATIO_N_SCALES       — deviates >30% with MONOTONE
   N-dependence across {4.3e4, 5e4, 7e4}. Report α-exponent of
   ratio-vs-N per leg.
  FLIP_N_PHI_RATIO_NON_MONOTONE   — non-monotone across the 3-N
   ladder on at least one leg. SURFACE; do not adjudicate.
  FLIP_N_INSTRUMENT_INCONSISTENT  — apparatus check failed. HALT.

C2 SUB-TERMINAL (Fibonacci-N anomaly check). Per leg, compare
N=46368 ratio to {N=4.3e4, N=5e4} bracket. 30% deviation:
  COMMENSURATE_NO_ANOMALY — within 30% of bracket on both legs.
  COMMENSURATE_ANOMALY    — >30% deviation on either leg (flag,
   surface, NOT adjudicating commensurability).

SCOPE. φ-mode N-scaling characterization only. Does NOT adjudicate
Step-1 verdict (Will's). Does NOT address sup L-convergence (Test 2).
Never proves (A)/(B); never decides §D; banked Step-1 untouched.
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
NS = (43000, 46368, 50000)                     # 46368 = F₂₄ (C2 Fibonacci spot-check)
LS = (100000, 400000, 1600000)
LEGS = ("sub", "sup")                          # sub: λ=1−δ, sup: λ=1+δ
TOL_COMMON = 0.25
HI_DEP = 1.0
TOL_N_MATCH = 0.30                              # 30% N-ratio deviation threshold
TOL_C2_MATCH = 0.30                             # 30% Fibonacci-N anomaly threshold
ABS_TOL_FLOOR = 1e-6                            # apparatus identity tolerance
REL_TOL = 1e-3                                   # account for sensitivity_confirm's
                                                 # 6-decimal storage rounding
OUT = os.path.join(HERE, "test1_flipN_phi_results.json")
RAW = os.path.join(HERE, "test1_flipN_phi_rawtable.json")
SENS = os.path.join(HERE, "sensitivity_confirm_results.json")
B1CR = os.path.join(HERE, "sub_phi_resolved_L_results.json")
B0HA = os.path.join(HERE, "sup_phi_resolved_L_results.json")


def cell(arg):
    leg, N, L, phi = arg
    lam = 1.0 - DELTA if leg == "sub" else 1.0 + DELTA
    try:
        e = am_eigs(lam, int(N), float(phi))
        w = float(W1d(unfold_rotnum(e, lam, GOLDEN, int(L), phis=(float(phi),))))
        return (leg, int(N), int(L), float(phi), w, None)
    except Exception as ex:
        return (leg, int(N), int(L), float(phi), None, repr(ex))


def _dump_raw(table, total):
    recs = [[k[0], int(k[1]), int(k[2]), float(k[3]), v]
            for k, v in table.items()]
    json.dump({"n": len(recs), "of": total, "recs": recs}, open(RAW, "w"))


def _load_raw():
    d = json.load(open(RAW))
    t = {}
    for leg, N, L, ph, w in d["recs"]:
        t[(leg, int(N), int(L), round(float(ph), 6))] = w
    return t, d.get("n", len(t)), d.get("of")


def phi_vec(table, leg, N, L):
    v = [table.get((leg, int(N), int(L), round(p, 6))) for p in PHIS]
    return None if any(x is None for x in v) else np.asarray(v, float)


def _baseline_n70k_ratio(leg):
    """Load b1crocze1 (sub) or b0haqgof3 (sup) N=70k δ=0.5 ratio."""
    src = B1CR if leg == "sub" else B0HA
    try:
        r = json.load(open(src))
        for p in r["per_cell"]:
            if p.get("delta") == 0.5 and p.get("N") == 70000:
                return float(p["ratio_phi_shift_to_L_ref_spread"])
    except Exception:
        return None
    return None


def _baseline_sens(leg, N):
    """Load sensitivity_confirm stored spread for identity check."""
    try:
        r = json.load(open(SENS))
        for row in r["per_N"]:
            if row["N"] == N:
                return float(row["sub_spread" if leg == "sub"
                                  else "sup_spread"])
    except Exception:
        return None
    return None


def main():
    t0 = time.time()
    tasks = [(leg, N, L, p) for leg in LEGS for N in NS for L in LS
             for p in PHIS]
    print("=" * 84)
    print(f"TEST 1 — flip-N φ-check (+ C2 Fibonacci spot) — {WORKERS}w ; "
          f"AM golden θ ; ratio-free leg")
    print(f"  δ=0.5 ; legs={LEGS} ; N(s)={NS} ({'F24=46368 Fib' if 46368 in NS else ''}) ; "
          f"L={LS} ; {len(PHIS)}φ ; {len(tasks)} tasks")
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
                leg, N, L, phi, w, err = f.result()
                table[(leg, int(N), int(L), round(phi, 6))] = w
                done += 1
                if err:
                    errs.append({"leg": leg, "N": N, "L": L, "phi": phi,
                                 "err": err})
                    print(f"  ERR {leg} N={N} L={L} φ={phi}: {err}",
                          flush=True)
                if done % 32 == 0:
                    _dump_raw(table, len(tasks))
                    print(f"  … {done}/{len(tasks)} [{time.time()-t0:.0f}s]",
                          flush=True)
        _dump_raw(table, len(tasks))
        print(f"  raw persisted ({len(table)}) — postproc free to re-run.",
              flush=True)

    Lref, Ltop = LS[0], LS[-1]

    # ── apparatus identity check at N=50000 vs sensitivity_confirm ─────
    id_ok, id_report = True, {}
    for leg in LEGS:
        v = phi_vec(table, leg, 50000, Lref)
        stored = _baseline_sens(leg, 50000)
        if v is None or stored is None:
            id_ok = False
            id_report[leg + "_50k_L1e5"] = {"error": "missing data"}
            continue
        meas = float(np.ptp(v))
        tol = max(ABS_TOL_FLOOR, REL_TOL * float(stored))
        ok = abs(meas - stored) <= tol
        id_report[leg + "_50k_L1e5"] = {
            "measured_spread": round(meas, 9),
            "stored_spread": round(float(stored), 9),
            "abs_diff": round(abs(meas - stored), 9),
            "tol": round(tol, 9), "PASS": bool(ok)}
        id_ok = id_ok and ok

    if not id_ok:
        rec = {"run": "Test 1 flip-N φ-check",
               "terminal": "FLIP_N_INSTRUMENT_INCONSISTENT",
               "apparatus_identity": id_report, "errors": errs,
               "total_s": round(time.time() - t0, 0),
               "note": "Apparatus identity check failed vs "
                       "sensitivity_confirm. HALT. No per-cell terminals. "
                       "Surface for diagnostic. Banked Step-1 untouched."}
        json.dump(rec, open(OUT, "w"), indent=1)
        print("=" * 84)
        print("  APPARATUS IDENTITY: FAILED")
        for k, r in id_report.items():
            print(f"    {k}: {r}")
        print(f"  TERMINAL: FLIP_N_INSTRUMENT_INCONSISTENT  HALT.")
        print("=" * 84)
        return

    # ── per-cell ratios ────────────────────────────────────────────────
    per_cell = []
    for leg in LEGS:
        for N in NS:
            per_L = {L: phi_vec(table, leg, N, L) for L in LS}
            if any(v is None for v in per_L.values()):
                per_cell.append({"leg": leg, "N": N, "error": True}); continue
            spread_ref = float(np.ptp(per_L[Lref]))
            mean_ref = float(per_L[Lref].mean())
            spread_top = float(np.ptp(per_L[Ltop]))
            mean_top = float(per_L[Ltop].mean())
            dw = per_L[Lref] - per_L[Ltop]
            dw_ptp = float(np.ptp(dw))
            if spread_ref <= 0:
                term, ratio = "PHI_INDETERMINATE", None
            else:
                ratio = dw_ptp / spread_ref
                if ratio <= TOL_COMMON: term = "PHI_COMMON_MODE"
                elif ratio >= HI_DEP:   term = "PHI_DEPENDENT"
                else:                    term = "PHI_INDETERMINATE"
            per_cell.append({"leg": leg, "N": N, "lam": 1.0 - DELTA if leg == "sub" else 1.0 + DELTA,
                              "spread_at_L_ref": round(spread_ref, 9),
                              "mean_at_L_ref": round(mean_ref, 9),
                              "spread_at_L_top": round(spread_top, 9),
                              "mean_at_L_top": round(mean_top, 9),
                              "per_phi_shift_ptp": round(dw_ptp, 9),
                              "ratio": round(ratio, 4) if ratio is not None else None,
                              "terminal": term})

    # ── per-leg N-scaling vs N=70k baseline ───────────────────────────
    per_leg = {}
    for leg in LEGS:
        base70k = _baseline_n70k_ratio(leg)
        rows = [p for p in per_cell if p.get("leg") == leg and "ratio" in p
                and p["ratio"] is not None]
        ratios = {p["N"]: p["ratio"] for p in rows}
        # primary brief Ns (excluding C2 N=46368):
        primary_Ns = [N for N in NS if N != 46368]
        if base70k is None or any(N not in ratios for N in primary_Ns):
            per_leg[leg] = {"error": "missing baseline or cells"}
            continue
        # 30% N-match check
        devs = {N: abs(ratios[N] - base70k) / base70k for N in primary_Ns}
        matches_70k = all(devs[N] <= TOL_N_MATCH for N in primary_Ns)
        # 3-N ladder monotonicity (including 70k)
        Ns_full = sorted(primary_Ns + [70000])
        rs_full = [ratios[N] if N in ratios else base70k for N in Ns_full]
        steps = [rs_full[i+1] - rs_full[i] for i in range(len(rs_full) - 1)]
        monotone = (all(s >= 0 for s in steps) or all(s <= 0 for s in steps))
        # α-exponent for ratio-vs-N (log-log slope)
        try:
            lx = np.log(np.array(Ns_full, float))
            ly = np.log(np.array(rs_full, float))
            alpha = float(np.polyfit(lx, ly, 1)[0])
        except Exception:
            alpha = None
        # C2: N=46368 vs bracket (43000, 50000)
        c2_term = None
        if 46368 in ratios:
            r_brack_avg = (ratios[43000] + ratios[50000]) / 2.0
            c2_dev = abs(ratios[46368] - r_brack_avg) / abs(r_brack_avg)
            c2_term = ("COMMENSURATE_NO_ANOMALY" if c2_dev <= TOL_C2_MATCH
                       else "COMMENSURATE_ANOMALY")
        per_leg[leg] = {"baseline_N70k_ratio": base70k,
                         "ratios_by_N": ratios,
                         "N_match_dev_pct": {N: round(devs[N] * 100, 1) for N in primary_Ns},
                         "matches_70k_within_30pct": matches_70k,
                         "Ns_full": Ns_full,
                         "ratios_full": [round(r, 4) for r in rs_full],
                         "monotone": monotone,
                         "loglog_alpha_ratio_vs_N": round(alpha, 4) if alpha is not None else None,
                         "C2_F24_vs_bracket_dev_pct": round(c2_dev * 100, 1) if 46368 in ratios else None,
                         "C2_terminal": c2_term}

    # primary terminal
    if any("error" in v for v in per_leg.values()):
        primary = "FLIP_N_PHI_RATIO_INDETERMINATE"
    elif all(per_leg[leg]["matches_70k_within_30pct"] for leg in LEGS):
        primary = "FLIP_N_PHI_RATIO_MATCHES_N70K"
    elif all(per_leg[leg]["monotone"] for leg in LEGS):
        primary = "FLIP_N_PHI_RATIO_N_SCALES"
    else:
        primary = "FLIP_N_PHI_RATIO_NON_MONOTONE"

    rec = {"run": "Test 1 flip-N φ-check (+ C2 Fibonacci-N spot)",
           "delta": DELTA, "legs": list(LEGS), "Ns": list(NS), "LS": list(LS),
           "n_phi": len(PHIS), "TOL_COMMON": TOL_COMMON, "HI_DEP": HI_DEP,
           "TOL_N_MATCH": TOL_N_MATCH, "TOL_C2_MATCH": TOL_C2_MATCH,
           "apparatus_identity": id_report,
           "per_cell": per_cell, "per_leg": per_leg,
           "primary_terminal": primary,
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "φ-mode N-scaling characterization at flip-N + C2 "
                   "Fibonacci spot-check. NEVER adjudicates Step-1 verdict, "
                   "(A)/(B), §D. Surfaces magnitudes for Will's adjudication."}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    print("  APPARATUS IDENTITY (vs sensitivity_confirm @N=50k):")
    for k, r in id_report.items():
        print(f"    {k}: meas={r['measured_spread']} stored={r['stored_spread']} "
              f"diff={r['abs_diff']} tol={r['tol']} PASS={r['PASS']}")
    for p in per_cell:
        if p.get("error"): print(f"  cell {p['leg']} N={p['N']}  ERROR"); continue
        print(f"  {p['leg']} N={p['N']:5d} (λ={p['lam']}) | "
              f"spread@1e5={p['spread_at_L_ref']} mean@1e5={p['mean_at_L_ref']} "
              f"ptp_Δw={p['per_phi_shift_ptp']} ratio={p['ratio']} → {p['terminal']}")
    for leg, v in per_leg.items():
        if "error" in v: print(f"  {leg}: error {v['error']}"); continue
        print(f"  {leg}: baseline@70k={v['baseline_N70k_ratio']}  "
              f"ratios={v['ratios_by_N']}  "
              f"N-match-dev%={v['N_match_dev_pct']}  "
              f"monotone={v['monotone']}  α(ratio-vs-N)={v['loglog_alpha_ratio_vs_N']}  "
              f"C2_F24_dev%={v['C2_F24_vs_bracket_dev_pct']} → C2 {v['C2_terminal']}")
    print(f"  PRIMARY: {primary}  [{rec['total_s']}s] errors={len(errs)}")
    print("  Surfaced not adjudicated. §D/Step-1/(A)/(B) untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()
