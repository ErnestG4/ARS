"""
thermo/tier1_compare.py — TIER-1 STEP 3: unseal and compare against published dim E_A.

Runs ONLY after thermo/TIER1_PREREG_SEALED.json is committed. Reads the sealed predictions and
compares against published / literature values. The seal's own validity is the cross-route
agreement (already in the sealed file, literature-independent); this step asks the separate
question of whether the sealed numbers match the outside world.

Published anchors (filled in at step-3 time, from primary sources, at full length):
  - E_2 = {1,2}: 0.5312805062772051416... (Jenkinson-Pollicott, arXiv 1611.09276) -- the CONTROL.
  - Other alphabets: Jenkinson-Pollicott 2001, ETDS 21 "Computing the dimension of dynamically
    defined sets: E_2 and bounded continued fractions", and Good (1941) for coarse checks.

Any alphabet lacking a trustworthy published value is reported as PREDICTION-ONLY (cross-route
validated, not yet externally confirmed) -- NOT quietly dropped.
"""
from __future__ import annotations

import json
import os

import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
mp.mp.dps = 60

# Published values, keyed by alphabet tuple. Populate from primary text layer at step-3 time.
# E_2 is the only one this session gated; others left None until a full-length source is read.
PUBLISHED = {
    (1, 2): "0.53128050627720514162446864736847178549305910901839",
    # (1, 2, 3): "...",   # <- fill from JP 2001 primary source before trusting
}


def main():
    sealed = json.load(open(os.path.join(HERE, "TIER1_PREREG_SEALED.json")))
    print("TIER-1 STEP 3 — sealed predictions vs published values\n")
    rows = []
    for pred in sealed["predictions"]:
        A = tuple(pred["alphabet"])
        d1 = mp.mpf(pred["route1_collocation"])
        pub = PUBLISHED.get(A)
        if pub is None:
            print(f"  {str(A):>14s}  {mp.nstr(d1, 24)}   PREDICTION-ONLY "
                  f"(routes agree {pred['routes_agree_digits']:.1f} dig; no full-length "
                  f"published value read)")
            rows.append({"alphabet": list(A), "status": "prediction_only",
                         "value": pred["route1_collocation"],
                         "routes_agree_digits": pred["routes_agree_digits"]})
            continue
        dp = float(-mp.log10(abs(d1 - mp.mpf(pub)) / abs(d1)))
        tag = "CONTROL" if A == (1, 2) else "match"
        print(f"  {str(A):>14s}  {mp.nstr(d1, 24)}   vs published -> {dp:.1f} digits [{tag}]")
        rows.append({"alphabet": list(A), "status": "compared", "digits_vs_published": dp,
                     "is_control": A == (1, 2)})
    out = {"comparison": rows}
    json.dump(out, open(os.path.join(HERE, "tier1_compare_measured.json"), "w"),
              indent=2, default=str)
    print("\nwrote tier1_compare_measured.json")


if __name__ == "__main__":
    main()
