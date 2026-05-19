"""
phase35a/t0_existing_data_read.py — SLICING-COMPARISON, the
existing-data T0 read (Will's explicit compute-go 2026-05-19,
"launch the first" = item (a): the pre-anything T0 instance).

This is a READ of the banked ratio-free sub/super W1δ data
(`sensitivity_confirm_results.json`: rotation-number leg, NO ref-N,
N∈{50000,70000,100000}, λ_sub=0.5 / λ_sup=1.5, 16 φ∈[0,0.5), L=1e5,
golden θ) **reframed under the signed-off T0-Excise schema**. NOT a
new eigensolve; no slate-2-numeric dependency; G1a-met. The
designation of this banked contrast as the T0 existing-data instance
is pre-registered and signed off (rev-3 §3; slate-2 §A: δ_max=0.5 is
the banked-continuity outermost rung) — so this is a SANCTIONED
re-scoping, not a silent purpose-violation.

PRE-REGISTERED (discriminant_exact_question_check — this IS a verdict
read, so mandatory & recorded):
 EXACT QUESTION: at the δ_max=0.5 rung, on the banked ratio-free
 data, is the sub-bracket (λ=0.5) vs super-bracket (λ=1.5) W1δ
 contrast significant against the §C α-ensemble floor —
 i.e. DISJOINT and inter-bracket gap ≥ max(sub_spread, sup_spread) —
 per N∈{50000,70000,100000}?
 CODED TEST = the §C significance criterion VERBATIM
 (= the signed-off slate-2 §C generalization of the validated
 `sensitivity_confirm` criterion) applied to the stored
 sub_spread/sup_spread/gap/disjoint. NOT a new discriminant; NOT a
 re-run. Honest terminals:
  T0_DELTA_MAX_SIGNIFICANT      — criterion holds at ALL three N;
  T0_DELTA_MAX_NOT_SIGNIFICANT  — holds at none;
  T0_DELTA_MAX_MIXED            — holds at some N, not others
                                  (report per-N honestly, no soften).

SCOPE / CEILING (rev-3 §4 T0; asymmetric label): this is the
**T0-Excise treatment's δ_max observable** — the AC-vs-PP
spectral-type contrast at fixed detuning δ=0.5, with λ=1 + its whole
neighbourhood EXCISED. **It says NOTHING about the critical point.**
It is instrument/methodology validation, never "AM characterized,"
never a discovery. The banked `SENSITIVITY_VALIDATED_NON_CIRCULAR`
verdict is **NOT inherited** — same numbers, different (T0) question.
brief-and-hold; nothing else runs; banked Step-1 untouched.
"""
from __future__ import annotations
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sensitivity_confirm_results.json")
OUT = os.path.join(HERE, "t0_existing_data_results.json")


def main():
    src = json.load(open(SRC))
    assert src["lam"] == {"sub": 0.5, "sup": 1.5}, "unexpected λ pair"
    assert src["L"] == 100000, "unexpected L_iter"
    print("=" * 84)
    print("EXISTING-DATA T0 READ — δ_max=0.5 rung (λ=0.5 vs λ=1.5), "
          "banked ratio-free leg")
    print("  §C criterion VERBATIM on banked sub/super W1δ α-ensembles "
          "(no re-run; no slate-2 dep)")
    print("=" * 84)
    per_N, all_sig, any_sig = [], True, False
    for r in src["per_N"]:
        N = r["N"]
        floor = max(r["sub_spread"], r["sup_spread"])   # §C: own-ensemble noise
        sig = bool(r["disjoint"] and r["gap"] >= floor)
        all_sig &= sig
        any_sig |= sig
        per_N.append({"N": N, "sub_spread": r["sub_spread"],
                      "sup_spread": r["sup_spread"], "gap": r["gap"],
                      "disjoint": r["disjoint"], "C_floor": round(floor, 6),
                      "gap_minus_floor": round(r["gap"] - floor, 6),
                      "T0_significant": sig})
        print(f"  N={N:7d} | sub_spr={r['sub_spread']:.6f} "
              f"sup_spr={r['sup_spread']:.6f} gap={r['gap']:.6f} "
              f"§C-floor={floor:.6f} gap−floor={r['gap']-floor:+.6f} "
              f"disjoint={r['disjoint']} → "
              f"{'T0-SIGNIFICANT' if sig else 'NOT-SIGNIFICANT'}")
    terminal = ("T0_DELTA_MAX_SIGNIFICANT" if all_sig else
                "T0_DELTA_MAX_NOT_SIGNIFICANT" if not any_sig else
                "T0_DELTA_MAX_MIXED")
    rec = {"read_only": True, "source": os.path.basename(SRC),
           "instance": "T0-Excise existing-data δ_max=0.5 rung "
                       "(banked ratio-free leg; pre-anything; G1a-met)",
           "criterion": "§C verbatim: disjoint AND gap >= "
                        "max(sub_spread,sup_spread)",
           "per_N": per_N, "terminal": terminal,
           "sensitivity_verdict_inherited": False,
           "ceiling": "T0 excises λ=1 + neighbourhood — says NOTHING "
                      "about the critical point; AC-vs-PP spectral-type "
                      "contrast at fixed detuning δ=0.5 only",
           "scope": "instrument/methodology validation; asymmetric "
                    "label; NOT an AM discovery; brief-and-hold"}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    print(f"  TERMINAL: {terminal}")
    print("  CEILING: T0 excises λ=1 — says NOTHING about the critical "
          "point (AC-vs-PP contrast at δ=0.5 only).")
    print("  Banked SENSITIVITY verdict NOT inherited (same numbers, "
          "T0 question). Instrument/methodology, not a discovery.")
    print("  brief-and-hold; nothing else runs; Step-1 untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()
