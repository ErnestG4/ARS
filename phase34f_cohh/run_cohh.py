"""
phase34f_cohh/run_cohh.py — cohomological-H execution through the gates.

Default run = §6 engine synthetic pre-validation (zero data; MUST pass
before the engine touches real data — the §7.ter.55/57 discipline that
caught the Berry-Robnik bug) THEN §4 decode gate (fetch + select the
prime-ideal ordering empirically via the bc≠0 base-change signature),
then STOP and write a checkpoint report. The substantive per-stratum
per-field Sato-Tate verdict is `--substantive` (run only after the §4
gate is reviewed — a wrong decode silently corrupts every verdict).

Outputs: data/phase34f_cohh/checkpoint_gate.json  (and st_results.json
on --substantive)
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
from scipy.stats import kstest

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS)
from bianchi_data_loader import (FIELDS, fetch, parse_newforms,
                                 prime_ideals, select_ordering, rp_good,
                                 stratum)

OUT = os.path.join(os.path.dirname(THIS), "data", "phase34f_cohh")
os.makedirs(OUT, exist_ok=True)


def semicircular_cdf(x):
    """SU(2) Sato-Tate CDF on [−2,2] (the documented Phase 34e form)."""
    x = np.clip(np.asarray(x, float), -2.0, 2.0)
    return (x * 0.5 * np.sqrt(np.maximum(1.0 - x * x / 4.0, 0.0))
            + np.arcsin(x * 0.5)) / np.pi + 0.5


def _draw_semicircular(n, rng):
    """Exact rejection sampler for density ∝ √(4−x²) on [−2,2]."""
    out = np.empty(0)
    while len(out) < n:
        x = rng.uniform(-2.0, 2.0, size=2 * n)
        keep = x[rng.uniform(0, 2.0, size=2 * n) <= np.sqrt(4.0 - x * x)]
        out = np.concatenate([out, keep])
    return out[:n]


def gate_6_engine_prevalidation(seed=0) -> dict:
    """§6 — multi-seed instrument validation (statistically correct).

    Under H0 (sample IS from the CDF) the KS p-value is Uniform(0,1), so a
    single-draw `p>0.05` gate false-fails ≈5% even for a perfect engine.
    The right criterion: over K seeds the true-measure rejection rate at
    α=0.05 must be ≈α (NOT ≈1) and the p-values ≈Uniform — a real
    CDF/sampler mismatch drives that rejection rate → 1. The wrong measure
    must be rejected almost always (engine has power).
    """
    K, n, alpha = 50, 4000, 0.05
    rng = np.random.default_rng(seed)
    p_pos, p_neg = [], []
    for _ in range(K):
        p_pos.append(kstest(_draw_semicircular(n, rng),
                             semicircular_cdf).pvalue)
        p_neg.append(kstest(rng.uniform(-2.0, 2.0, size=n),
                             semicircular_cdf).pvalue)
    p_pos, p_neg = np.array(p_pos), np.array(p_neg)
    rej_pos = float(np.mean(p_pos < alpha))   # ≈α if engine correct
    rej_neg = float(np.mean(p_neg < alpha))   # ≈1 if engine has power
    checks = {
        # not systematically rejecting truth (≈α; mismatch ⇒ →1)
        "true_measure_not_systematically_rejected": bool(rej_pos <= 0.20),
        "true_measure_pvalues_uniformish": bool(np.median(p_pos) >= 0.15),
        # decisive power against the wrong measure
        "wrong_measure_rejected": bool(rej_neg >= 0.95),
    }
    return dict(
        K=K, n=n, alpha=alpha,
        pos=dict(reject_rate=rej_pos, median_p=float(np.median(p_pos))),
        neg=dict(reject_rate=rej_neg, median_p=float(np.median(p_neg))),
        checks=checks, passed=all(checks.values()))


def gate_4_decode(forms_by_field: dict) -> dict:
    out = {}
    for fld, forms in forms_by_field.items():
        sel = select_ordering(forms)
        strat = {"A": 0, "B": 0, "C": 0}
        for f in forms:
            strat[stratum(f)] += 1
        sel["n_forms"] = len(forms)
        sel["strata_counts"] = strat
        out[fld] = sel
    return out


def main():
    substantive = "--substantive" in sys.argv
    print("=" * 70)
    print("cohomological-H — gate run (§6 engine pre-validation → §4 decode)")
    print("=" * 70)

    g6 = gate_6_engine_prevalidation()
    print(f"§6 engine pre-validation (K={g6['K']} seeds, n={g6['n']}): "
          f"true-measure reject_rate={g6['pos']['reject_rate']:.3f} "
          f"(≈α=0.05 ⇒ ok), median_p={g6['pos']['median_p']:.3f}; "
          f"wrong-measure reject_rate={g6['neg']['reject_rate']:.3f} "
          f"→ {'PASS' if g6['passed'] else 'FAIL'}")
    if not g6["passed"]:
        json.dump({"gate6": g6, "verdict": "ENGINE_PREVALIDATION_FAILED"},
                  open(os.path.join(OUT, "checkpoint_gate.json"), "w"), indent=2)
        sys.exit("§6 FAILED — engine does not recover the known target; "
                 "do NOT proceed to real data (§7.ter.55).")

    forms_by_field = {}
    for fld in FIELDS:
        path = fetch(fld)
        forms = list(parse_newforms(path))
        st = parse_newforms.stats
        print(f"  {fld}: parsed {st['n_ok']} forms (skipped {st['n_bad']} "
              f"malformed) from {os.path.basename(path)}")
        forms_by_field[fld] = forms

    g4 = gate_4_decode(forms_by_field)
    print("\n§4 decode gate (empirical prime-ideal ordering selection):")
    for fld, r in g4.items():
        print(f"  {fld}  verdict={r['verdict']}  strata A/B/C="
              f"{r['strata_counts']['A']}/{r['strata_counts']['B']}/"
              f"{r['strata_counts']['C']}  (n={r['n_forms']})")
        for od, m in r["report"].items():
            print(f"    [{od:9s}] bc-pair-eq={m['frac_pair_equal_bc']:.4f} "
                  f"genuine-pair-eq={m['frac_pair_equal_genuine']:.4f} "
                  f"RP-within={m['frac_RP_within']:.5f}")

    all_resolved = all(r["verdict"].startswith("RESOLVED")
                       for r in g4.values())
    verdict = ("GATES_PASSED_DECODE_RESOLVED_READY_FOR_SUBSTANTIVE"
               if all_resolved else
               "DECODE_UNRESOLVED_HALT_NO_SUBSTANTIVE_VERDICT")
    report = {"gate6": g6, "gate4": g4, "verdict": verdict}
    json.dump(report, open(os.path.join(OUT, "checkpoint_gate.json"), "w"),
              indent=2, default=float)
    print(f"\n→ {verdict}")
    print(f"→ wrote {os.path.join(OUT, 'checkpoint_gate.json')}")

    if not all_resolved:
        sys.exit("§4 decode UNRESOLVED — halting before any substantive "
                 "Sato-Tate verdict (a wrong decode silently corrupts "
                 "every verdict; §D.0b). Report + investigate.")

    if not substantive:
        print("\n[checkpoint] §6+§4 passed. Substantive Sato-Tate held "
              "for review — rerun with --substantive after the §4 gate "
              "report is checked.")
        return

    # ---- substantive (only reached with --substantive AND gates passed) ----
    # Discipline (§7.ter.57 / Phase-34d finite-X): at pooled n = 1e5–1e7
    # a KS p-value is uninformative — it →0 for any infinitesimal
    # finite-P deviation. The verdict uses the KS *statistic* (effect
    # size) + a Chen-2019 finite-P scan (does the deviation shrink as
    # the prime bound grows, i.e. is it the NLO correction tail?), NOT
    # the p-value. CM stratum (A) is the negative control: it MUST be
    # non-semicircular (it targets the Hecke-character measure, §5).
    P_CUTS = [1000, 10000, 100000, 1000000]
    st_out = {}
    for fld, forms in forms_by_field.items():
        od = g4[fld]["ordering"]
        maxlen = max(len(f["ap"]) for f in forms)
        ide = prime_ideals(fld, maxlen, od)
        for s in ("A", "B", "C"):
            chunks = []
            for f in forms:
                if stratum(f) == s:
                    g = rp_good(f, ide)
                    if g:
                        chunks.append(np.array(g, float))   # (x, norm)
            if not chunks:
                st_out[f"{fld}:{s}"] = dict(n=0, verdict="EMPTY")
                continue
            arr = np.concatenate(chunks)
            x_all, nrm = arr[:, 0], arr[:, 1]
            keep = (x_all >= -2.0) & (x_all <= 2.0)
            x_all, nrm = x_all[keep], nrm[keep]
            n = int(len(x_all))
            if n < 200:
                st_out[f"{fld}:{s}"] = dict(n=n, verdict="UNDERPOWERED")
                continue
            ks_full = kstest(x_all, semicircular_cdf)
            scan = []
            for P in P_CUTS:
                xp = x_all[nrm <= P]
                if len(xp) >= 200:
                    scan.append((P, int(len(xp)),
                                 float(kstest(xp, semicircular_cdf).statistic)))
            ks0 = scan[0][2] if scan else float("nan")
            ksN = scan[-1][2] if scan else float("nan")
            chen_shrinks = bool(len(scan) >= 2 and ksN <= ks0 + 1e-4)
            ks_small = bool(ks_full.statistic <= 0.05)
            if s == "A":
                # negative control: CM must NOT be semicircular
                ok = bool(ks_full.statistic >= 0.10)
                verdict = (f"SATO_TATE_CM_NON_SEMICIRCULAR_AS_EXPECTED_"
                           f"DESCRIPTIVE_ONLY_A_({fld})" if ok else
                           f"CM_UNEXPECTEDLY_SEMICIRCULAR_A_({fld})_INVESTIGATE")
            else:
                if ks_small and chen_shrinks:
                    verdict = (f"SATO_TATE_VALIDATED_AT_FINITE_P_WITH_"
                               f"CORRECTION_{s}_({fld})")
                else:
                    verdict = f"SATO_TATE_ENGINE_DISCREPANCY_{s}_({fld})"
            st_out[f"{fld}:{s}"] = dict(
                n=n, ks_full_stat=float(ks_full.statistic),
                ks_full_p=float(ks_full.pvalue),
                ks_full_p_note="UNINFORMATIVE at this n; not used for verdict",
                finite_P_scan=[dict(P_max=P, n=nn, ks_stat=k)
                               for P, nn, k in scan],
                chen2019_deviation_shrinks_with_P=chen_shrinks,
                verdict=verdict)
            print(f"  {fld} {s}: n={n} KS_full={ks_full.statistic:.4f} "
                  f"scan[{P_CUTS[0]}→{P_CUTS[-1]}]="
                  f"{ks0:.4f}→{ksN:.4f} chen_shrinks={chen_shrinks} "
                  f"→ {verdict.split('(')[0]}")
    # cell-level verdict (asymmetric — proven-theorem-calibration tier)
    def _ok(key, pre):
        v = st_out.get(key, {}).get("verdict", "")
        return v.startswith(pre)
    flds = list(forms_by_field)
    c_ok = all(_ok(f"{f}:C", "SATO_TATE_VALIDATED_AT_FINITE_P") for f in flds)
    b_ok = all(_ok(f"{f}:B", "SATO_TATE_VALIDATED_AT_FINITE_P") for f in flds)
    a_ok = all(_ok(f"{f}:A", "SATO_TATE_CM_NON_SEMICIRCULAR") for f in flds)
    cell = ("COHOMOLOGICAL_H_METHODOLOGY_VALIDATED_AT_FINITE_P"
            if (c_ok and b_ok and a_ok) else
            "COHOMOLOGICAL_H_PARTIAL")
    json.dump({"gate6": g6, "gate4": g4, "sato_tate": st_out,
               "cell_verdict": cell,
               "label_discipline": "proven-theorem-calibration tier "
               "(METHODS §1); instrument validation NOT discovery; does "
               "NOT touch the Q(√−3) Δ-closer; large-n KS p-values "
               "uninformative — verdict on KS-statistic + Chen-2019 "
               "finite-P scan"},
              open(os.path.join(OUT, "st_results.json"), "w"),
              indent=2, default=float)
    print(f"\n→ cell verdict: {cell}")
    print(f"→ wrote {os.path.join(OUT, 'st_results.json')}")


if __name__ == "__main__":
    main()
