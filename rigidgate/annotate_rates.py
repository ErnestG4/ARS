"""Recover denominators for this arc's boundary rates and attach intervals.
COMMITTED GENERATOR of rigidgate/rate_annotations.json.

The boundary-rate sweep's first obligation is our own house: 22 of the 41
denominator-less banked boundary rates are in this arc's artifacts.  Their n
are recoverable **only because the generators were committed** — the
committed-generator rule paying off in an audit nobody had in mind when it
was adopted.

The denominators are read from the generators' own sealed constants, NOT
guessed:

  gate_measured.R2.rows.*.{false_rigid_rate,gue_rigid_rate,poisson_rigid_rate}
      run_gate.py: SEAL["r2_draws"] = {renewal, gue, poisson}
  gate_measured.R3.f_grid.*.rigid_rate
      run_gate.py: SEAL["r3_family"]["draws_per_f"]
  kag_measured.witness.*.{gue_rigid_rate,poisson_rigid_rate}
      kag_gate.py: 16 GUE draws, 16 Poisson draws (literal in the A/B block)
  kag_measured.hyper_arm.*.gue_false_hyper_rate
      kag_gate.py: the same 16-draw GUE sample

Intervals and treatment come from the pinned convention in
`boundary_rate.py` (Clopper-Pearson, alpha 0.05) so a later re-run under a
different convention fails loudly rather than silently reclassifying a row.

WRITES A SIDECAR, NOT THE SEALED ARTIFACTS.  gate_measured.json and
kag_measured.json are inside the seal's blob-SHA freeze; editing them to add
denominators would break the freeze for a documentation improvement.  The
sidecar carries the n and the interval; the freeze stays intact.
"""

import json
import sys

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, ROOT)
from boundary_rate import classify, CONVENTION, ALPHA          # noqa: E402

SEAL = json.load(open(f"{ROOT}/rigidgate/prereg_sealed.json"))
R2 = SEAL["r2_draws"]
R3_DRAWS = SEAL["r3_family"]["draws_per_f"]
KAG_DRAWS = 16                    # kag_gate.py A/B block, literal

DENOMS = {
    "R2.false_rigid_rate": R2["renewal"],
    "R2.gue_rigid_rate": R2["gue"],
    "R2.poisson_rigid_rate": R2["poisson"],
    "R3.rigid_rate": R3_DRAWS,
    "kag.gue_rigid_rate": KAG_DRAWS,
    "kag.poisson_rigid_rate": KAG_DRAWS,
    "kag.gue_false_hyper_rate": KAG_DRAWS,
}


def collect(path, obj, out, kind):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, float) and v in (0.0, 1.0) and "rate" in k:
                n = DENOMS.get(f"{kind}.{k}")
                if n:
                    k_succ = int(round(v * n))
                    c = classify(k_succ, n)
                    out[f"{path}.{k}"] = dict(
                        rate=v, k=k_succ, n=n, lo=c["lo"], hi=c["hi"],
                        treatment=c["treatment"],
                        honest_claim=c["honest_claim"])
            collect(f"{path}.{k}", v, out, kind)
        return
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            collect(f"{path}[{i}]", v, out, kind)


def main():
    g = json.load(open(f"{ROOT}/rigidgate/gate_measured.json"))
    k = json.load(open(f"{ROOT}/rigidgate/kag_measured.json"))
    out = {}
    collect("gate_measured.R2", g.get("R2", {}), out, "R2")
    collect("gate_measured.R3", g.get("R3", {}), out, "R3")
    collect("kag_measured.witness", k.get("witness", {}), out, "kag")
    collect("kag_measured.hyper_arm", k.get("hyper_arm", {}), out, "kag")

    uninf = [p for p, r in out.items() if r["treatment"] == "UNINFORMATIVE"]
    rec = dict(convention=CONVENTION, alpha=ALPHA,
               denominator_source="sealed constants in the committed "
                                  "generators (run_gate.py, kag_gate.py) — "
                                  "recoverable ONLY because those generators "
                                  "were committed",
               sidecar_note="the sealed artifacts are inside a blob-SHA "
                            "freeze and are NOT edited; this file carries "
                            "the denominators and intervals alongside them",
               n_rows=len(out), n_uninformative=len(uninf),
               uninformative=uninf, rows=out)
    json.dump(rec, open(f"{ROOT}/rigidgate/rate_annotations.json", "w"),
              indent=1)
    print(f"annotated {len(out)} boundary rates "
          f"({CONVENTION}, alpha={ALPHA})")
    for p, r in sorted(out.items()):
        flag = "  <-- UNINFORMATIVE" if r["treatment"] == "UNINFORMATIVE" else ""
        print(f"  {p:<52} {r['rate']:.1f}  k={r['k']:>3}/{r['n']:<3} "
              f"{r['honest_claim']:>12}{flag}")
    print(f"\nuninformative rows: {len(uninf)}/{len(out)}")


if __name__ == "__main__":
    main()
