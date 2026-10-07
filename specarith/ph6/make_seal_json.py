"""Write seals/PH6_SEAL_6.0.json (seal §0 procedure). Run ONLY after Will has decided the proposed amendments and the
seal text carries them in its Amendments section; the seal commit is a separate, deliberate step.

Usage:  python make_seal_json.py ZEROS1 MAASS_CSV CHI4_ZEROS --decisions "A1=yes,A3=yes,A4b=no,A5=yes,A6=yes,..." \\
                                 [--pre results/preread_proposed] [--dry]

Pins (review v3 M1/M2):
- text, code and every pre-read output by path RELATIVE to this directory (the gate run may execute on spot);
- the three data inputs and the chi4 accuracy/merge reports BY ROLE (zeros1, maass, chi4, chi4_accuracy, chi4_merge), with
  their sha256 and the level counts the pre-read tables used;
- the environment (python, numpy, scipy, mpmath, cypari2, PARI).
Checks before writing (review v3 M3, m1, m5): the decisions are structured; the pre-read's configs are exactly the sealed
set plus the windows of the approved amendments (A1 -> G1s_a/b, A6 -> G2s_a/b) and G2's E_hi is 4e4 iff A4b = yes; every
rhs/nulls file the gate run will open exists; the chi4 list covers G2's E_hi and has the tables' level count.
"""
import hashlib
import json
import os
import platform
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = ["ph6lib.py", "preread.py", "gates.py", "rulings.py", "classes.py", "chi4_zeros_v2.py"]
TEXT = ["PH6_SEAL_6.0.md", "PH6_DECISIONS_2026-10-07.md", "PH6_PROPOSED_AMENDMENTS.md"]
BASE_CONFIGS = {"G0", "G0s_a", "G0s_b", "G0s_c", "G0c", "G1", "G2"}
WINDOWS = {"A1": {"G1s_a", "G1s_b"}, "A6": {"G2s_a", "G2s_b"}}
AMENDMENTS = ["A1", "A3", "A4b", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"]

PINNED_DEFINITIONS = {
    "RP15_replacement": "ph6lib.psi_asymptotic(u) = log(max(|u|, 2)/2)",
    "RP8_terms_dropped": "even sector: 2 sum Lambda(n)/n g(2 log n) and -(2/4pi) int h psi(1+ir)",
    "RP9_construction": "hyperbolic term rebuilt with the whole class weight of the t^2+4 discriminants in place of t^2-4",
    "RP7_construction": "each sector's identity read on the other sector's levels; h(i/2) added where the even identity has it",
    "RP12_construction": "picket sum multiplied by e^{tau/2} (eigenvalues E_n - i/2)",
    "null_construction": {"t_min": 7.0, "upper_margin": "1.02 E_hi + 50", "central_fraction": 0.8,
                          "n_mat": "ceil(n/0.8) + 10", "calibration_seeds": {"gue": [1000, 1099], "poisson": [2000, 2099]},
                          "heldout_seeds": {"gue": [1100, 1199], "poisson": [2100, 2199]}},
    "chi4_zeros_recipe": "chi4_zeros_v2.py: cost-balanced interval calls lfunzeros(lfuncreate(-4), [a,b], 64) at "
                         "realprecision 38 via GP strings (one run directory per height range, combined by a jobs.txt "
                         "listing every p38 chunk); merge with dedupe, |N - Nbar| < 2, min gap > 1e-8, S-block means within "
                         "0.6 (blocks of 250; the last partial block is not checked); accuracy: realprecision 57 on [0,1000] "
                         "and [T-100, T], delta = 10 x max |diff|, floored at 1e-30",
}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def parse_decisions(text):
    d = {}
    for item in text.split(","):
        k, v = item.split("=")
        k, v = k.strip(), v.strip().lower()
        if k not in AMENDMENTS or v not in ("yes", "no"):
            raise SystemExit(f"refusing: decision '{item}' is not KEY=yes|no with KEY in {AMENDMENTS}")
        d[k] = v == "yes"
    missing = [k for k in AMENDMENTS if k not in d]
    if missing:
        raise SystemExit(f"refusing: no decision for {missing}")
    return d


def environment():
    import numpy, scipy, mpmath, cypari2
    return dict(python=platform.python_version(), numpy=numpy.__version__, scipy=scipy.__version__,
                mpmath=mpmath.__version__, cypari2=getattr(cypari2, "__version__", "?"),
                pari=str(cypari2.Pari().version()))


def main():
    zeros1, maass, chi4 = sys.argv[1:4]
    if "--decisions" not in sys.argv:
        raise SystemExit("refusing: pass --decisions with Will's answers to every proposed amendment")
    dec = parse_decisions(sys.argv[sys.argv.index("--decisions") + 1])
    pre_rel = sys.argv[sys.argv.index("--pre") + 1] if "--pre" in sys.argv else "results/preread"
    pre = os.path.join(HERE, pre_rel)
    tab = json.load(open(os.path.join(pre, "preread_tables.json")))
    cfgs = set(tab["configs"])
    want = set(BASE_CONFIGS)
    for a, w in WINDOWS.items():
        if dec[a]:
            want |= w
    if cfgs != want:
        raise SystemExit(f"refusing: pre-read configs {sorted(cfgs)} != sealed set + approved windows {sorted(want)}")
    g2_hi = tab["configs"]["G2"]["E_hi"]
    if (g2_hi == 40000.0) != dec["A4b"]:
        raise SystemExit(f"refusing: G2 E_hi = {g2_hi} but A4b = {dec['A4b']}")
    need = [f"rhs_{n}.npz" for n in ("G0", "G0s_a", "G0s_b", "G0s_c", "G0c", "G2", "G4_confusable", "G4_incommensurate")]
    need += [f"rhs_{g}_{s}.npz" for g in ("G1",) + tuple(sorted(WINDOWS["A1"] if dec["A1"] else ())) for s in ("even", "odd")]
    need += [f"rhs_{g}.npz" for g in sorted(WINDOWS["A6"] if dec["A6"] else ())]
    need += [f"nulls_{n}_{k}.npz" for n in ("G0", "G0c", "G2") for k in ("gue", "poisson")]
    missing = [n for n in need if not os.path.exists(os.path.join(pre, n))]
    if missing:
        raise SystemExit(f"refusing: pre-read outputs missing {missing}")
    # chi4 list consistent with the tables (review v3 M1, m5)
    merge = json.load(open(chi4.replace(".txt", ".merge.json")))
    upper = max(c["b"] for c in merge["chunks"])
    n_chi = sum(1 for _ in open(chi4) if _.strip())
    if upper < g2_hi or n_chi != tab["gates"]["G2"]["n_levels"]:
        raise SystemExit(f"refusing: chi4 list (upper {upper}, n {n_chi}) does not match G2 (E_hi {g2_hi}, "
                         f"n {tab['gates']['G2']['n_levels']})")
    files = {f: sha(os.path.join(HERE, f)) for f in TEXT + CODE}
    for n in sorted(os.listdir(pre)):
        if n.endswith((".npz", ".json")):
            files[os.path.join(pre_rel, n)] = sha(os.path.join(pre, n))
    data = {"zeros1": dict(sha256=sha(zeros1), n=tab["gates"]["G0"]["n_levels"]),
            "maass": dict(sha256=sha(maass), n_even=tab["gates"]["G1_even"]["n_levels"],
                          n_odd=tab["gates"]["G1_odd"]["n_levels"]),
            "chi4": dict(sha256=sha(chi4), n=n_chi, upper=upper),
            "chi4_accuracy": dict(sha256=sha(chi4.replace(".txt", ".accuracy.json"))),
            "chi4_merge": dict(sha256=sha(chi4.replace(".txt", ".merge.json")))}
    head = subprocess.run(["git", "-C", HERE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = dict(seal="PH6_SEAL_6.0", commit=head, commit_note="parent of the seal commit (the commit that adds this file)",
               pre_dir=pre_rel, decisions=dec, pinned_definitions=PINNED_DEFINITIONS, environment=environment(),
               files=files, data=data)
    if "--dry" in sys.argv:          # all checks, no file: a seal JSON on disk would satisfy gates.check_seal
        print(f"DRY: checks passed; would pin {len(files)} files + {len(data)} data inputs; pre {pre_rel}")
        return
    os.makedirs(os.path.join(HERE, "seals"), exist_ok=True)
    with open(os.path.join(HERE, "seals", "PH6_SEAL_6.0.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote seals/PH6_SEAL_6.0.json: {len(files)} files + {len(data)} data inputs pinned; pre {pre_rel}; "
          f"parent {head[:10]}")


if __name__ == "__main__":
    main()
