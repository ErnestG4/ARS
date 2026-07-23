"""
thermo/tier1_compare.py — TIER-1 STEP 3: unseal and compare against published dim E_A.

Runs only AFTER thermo/TIER1_PREREG_SEALED.json is committed (commit b0b6228). The seal's own
validity is the literature-independent cross-route agreement; this step asks the separate
question of whether the sealed numbers match the outside world.

Standard notation: E_N = reals whose CF digits are all <= N, i.e. alphabet {1..N}. So the sealed
{1,2} is E_2, {1,2,3} is E_3, {1,2,3,4} is E_4, {1,2,3,4,5} is E_5. The {1,3} and {2,3} pairs
are the non-consecutive Cantor sets in Falk-Nussbaum's tables.

Published anchors, all pulled from primary text layers (pypdf), NOT summarised fetches:
  - E_2 = {1,2}:  Jenkinson-Pollicott, arXiv 1611.09276, 100 digits. The CONTROL.
  - {1,3}, {2,3}: Falk-Nussbaum, arXiv 1612.00870 / 1601.06737, as CONVERGING LOWER/UPPER
    BRACKETS (their method brackets the dimension; innermost pair is the tightest interval).
  - E_3, E_4, E_5: no high-precision published value located this session -> PREDICTION-ONLY
    (cross-route validated, externally unconfirmed), reported as such, not dropped.
"""
from __future__ import annotations

import json
import os

import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
mp.mp.dps = 60

# Exact published value (Jenkinson-Pollicott 1611.09276).
PUBLISHED_EXACT = {
    (1, 2): "0.53128050627720514162446864736847178549305910901839",
}
# Falk-Nussbaum bracketing bounds (arXiv 1612.00870). The dimension lies between the innermost
# lower and upper bounds; their published rows straddle it and tighten.
FN_BRACKETS = {
    (1, 3): ["0.454489076859422", "0.454489077843624",
             "0.454489077459035", "0.454489077707546"],
    (2, 3): ["0.337436780744847", "0.337436780851139",
             "0.337436780790228", "0.337436780817793"],
}


def main():
    sealed = json.load(open(os.path.join(HERE, "TIER1_PREREG_SEALED.json")))
    print("TIER-1 STEP 3 — sealed predictions vs published values")
    print("(seal committed at b0b6228 BEFORE any of these lookups)\n")
    rows = []
    for pred in sealed["predictions"]:
        A = tuple(pred["alphabet"])
        d1 = mp.mpf(pred["route1_collocation"])
        agree = pred["routes_agree_digits"]

        if A in PUBLISHED_EXACT:
            pub = mp.mpf(PUBLISHED_EXACT[A])
            dp = float(-mp.log10(abs(d1 - pub) / abs(d1)))
            print(f"  {str(A):>16s}  {mp.nstr(d1, 22)}  vs JP exact -> {dp:.1f} digits [CONTROL]")
            rows.append({"alphabet": list(A), "status": "control_exact",
                         "digits_vs_published": dp})
        elif A in FN_BRACKETS:
            b = sorted(mp.mpf(x) for x in FN_BRACKETS[A])
            inner = b[1:3]                    # tightest published interval
            inside_inner = inner[0] < d1 < inner[1]
            inside_outer = b[0] < d1 < b[-1]
            width = float(-mp.log10(inner[1] - inner[0]))
            print(f"  {str(A):>16s}  {mp.nstr(d1, 22)}  Falk-Nussbaum bracket "
                  f"[{mp.nstr(inner[0], 15)}, {mp.nstr(inner[1], 15)}]")
            print(f"  {'':>16s}  -> inside tightest published interval "
                  f"(~{width:.0f}-digit wide): {inside_inner}")
            rows.append({"alphabet": list(A), "status": "bracket_confirmed",
                         "inside_inner_bracket": bool(inside_inner),
                         "inside_outer_bracket": bool(inside_outer),
                         "bracket_width_digits": width,
                         "routes_agree_digits": agree})
        else:
            std = f"E_{max(A)}" if list(A) == list(range(1, max(A) + 1)) else str(A)
            print(f"  {str(A):>16s}  {mp.nstr(d1, 22)}  = {std}: PREDICTION-ONLY "
                  f"(routes agree {agree:.1f} dig; no full-length published value located)")
            rows.append({"alphabet": list(A), "status": "prediction_only",
                         "standard_name": std, "routes_agree_digits": agree})

    controls_ok = all(r.get("digits_vs_published", 99) > 20
                      for r in rows if r["status"] == "control_exact")
    brackets_ok = all(r["inside_inner_bracket"] for r in rows if r["status"] == "bracket_confirmed")
    out = {"comparison": rows,
           "control_matches_to_20plus_digits": controls_ok,
           "all_brackets_confirmed": brackets_ok,
           "TIER1_VERDICT": ("CONFIRMED — control exact, both external brackets contain the "
                             "sealed prediction, remaining alphabets cross-route validated"
                             if controls_ok and brackets_ok else "REVIEW")}
    print(f"\n  control reproduces JP dim E_2 to 20+ digits : {controls_ok}")
    print(f"  both Falk-Nussbaum brackets contain the seal : {brackets_ok}")
    print(f"\n  TIER-1 VERDICT: {out['TIER1_VERDICT']}")
    json.dump(out, open(os.path.join(HERE, "tier1_compare_measured.json"), "w"),
              indent=2, default=str)
    print("\nwrote tier1_compare_measured.json")


if __name__ == "__main__":
    main()
