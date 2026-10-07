"""Write seals/PH6_SEAL_6.0.json (seal §0 procedure). Run ONLY after Will has decided the proposed amendments and the
seal text carries them in its Amendments section; the seal commit is a separate, deliberate step.

Usage:  python make_seal_json.py ZEROS1 MAASS_CSV CHI4_ZEROS [--decisions "A1=yes,A3=yes,..."]

Pins (sha256): the seal text, the decisions file, every code file the gate run imports, the three data inputs, and every
pre-read output the gate run reads (tables, rhs_*.npz, nulls_*.npz, design and known-answer JSON) — review v2 N9.
Also records the pinned definitions of A10 so they are part of the sealed object.
"""
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRE = os.path.join(HERE, "results", "preread")
CODE = ["ph6lib.py", "preread.py", "gates.py", "rulings.py", "classes.py", "chi4_zeros_v2.py"]
TEXT = ["PH6_SEAL_6.0.md", "PH6_DECISIONS_2026-10-07.md", "PH6_PROPOSED_AMENDMENTS.md"]

PINNED_DEFINITIONS = {
    "RP15_replacement": "ph6lib.psi_asymptotic(u) = log(max(|u|, 2)/2)",
    "RP8_terms_dropped": "even sector: 2 sum Lambda(n)/n g(2 log n) and -(2/4pi) int h psi(1+ir)",
    "RP9_construction": "hyperbolic term rebuilt with the whole class weight of the t^2+4 discriminants in place of t^2-4",
    "RP7_construction": "each sector's identity read on the other sector's levels; h(i/2) added where the even identity has it",
    "RP12_construction": "picket sum multiplied by e^{tau/2} (eigenvalues E_n - i/2)",
    "null_construction": {"t_min": 7.0, "upper_margin": "1.02 E_hi + 50", "central_fraction": 0.8,
                          "n_mat": "ceil(n/0.8) + 10", "calibration_seeds": {"gue": [1000, 1099], "poisson": [2000, 2099]},
                          "heldout_seeds": {"gue": [1100, 1199], "poisson": [2100, 2199]}},
    "chi4_zeros_recipe": "chi4_zeros_v2.py: 40 cost-balanced interval calls, lfunzeros divz 64, realprecision 38 via GP "
                         "strings; merge with dedupe, |N - Nbar| < 2, min gap > 1e-8, S-block means within 0.6; "
                         "accuracy: realprecision 57 on [0,1000] and [T-100, T], delta = 10 x max |diff|",
}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    zeros1, maass, chi4 = sys.argv[1:4]
    decisions = sys.argv[sys.argv.index("--decisions") + 1] if "--decisions" in sys.argv else None
    if decisions is None:
        raise SystemExit("refusing: pass --decisions with Will's answers to the proposed amendments")
    files = {}
    for f in TEXT + CODE:
        files[os.path.join(HERE, f)] = sha(os.path.join(HERE, f))
    for f in [zeros1, maass, chi4, chi4.replace(".txt", ".accuracy.json"), chi4.replace(".txt", ".merge.json")]:
        files[os.path.abspath(f)] = sha(f)
    pre = sorted(glob.glob(os.path.join(PRE, "preread_tables.json")) + glob.glob(os.path.join(PRE, "rhs_*.npz"))
                 + glob.glob(os.path.join(PRE, "nulls_*.npz")) + glob.glob(os.path.join(PRE, "design_table.json"))
                 + glob.glob(os.path.join(PRE, "null_known_answers.json")))
    need = ["rhs_G0.npz", "rhs_G0c.npz", "rhs_G1_even.npz", "rhs_G1_odd.npz", "rhs_G2.npz", "rhs_G4_confusable.npz",
            "rhs_G4_incommensurate.npz", "nulls_G0_gue.npz", "nulls_G0c_gue.npz", "nulls_G2_gue.npz"]
    missing = [n for n in need if not os.path.exists(os.path.join(PRE, n))]
    if missing:
        raise SystemExit(f"refusing: pre-read outputs missing {missing}")
    for p in pre:
        files[p] = sha(p)
    head = subprocess.run(["git", "-C", HERE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = dict(seal="PH6_SEAL_6.0", parent_commit=head, decisions=decisions, pinned_definitions=PINNED_DEFINITIONS,
               files=files)
    os.makedirs(os.path.join(HERE, "seals"), exist_ok=True)
    with open(os.path.join(HERE, "seals", "PH6_SEAL_6.0.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote seals/PH6_SEAL_6.0.json: {len(files)} files pinned; parent {head[:10]}")


if __name__ == "__main__":
    main()
