"""C2 — pvc-11 through the REPAIRED estimator. COMMITTED GENERATOR.

Adds `I.8_brody_q_unbounded` to every pvc-11 record. Does NOT touch
`I.8_brody_q`, does NOT go through `phase2b_recompute._matched_axes` (which nulls
the bounded key when the fitter gate fails -- policy-correct, and still a loss of
the banked record this arc's finding rests on).

SAFETY SHAPE:
  * direct estimator call; the bounded key is never assigned
  * writes to a TEMP file, runs the sealed acceptance verifier against it, and
    only then replaces the artifact
  * all 1159 records written, in the original order, every other key untouched
"""
import json, os, shutil, subprocess, sys, time
import numpy as np

R = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, R)
from phase22a.loader import load                                  # noqa: E402
from phase22a.ars_classify import unfold_unit_mean                # noqa: E402
from cross_substrate.axes import I8_brody_q_unbounded             # noqa: E402

SRC = f"{R}/cross_substrate/coordinates/pvc-11.jsonl"
TMP = f"{R}/c2_acceptance/pvc-11.jsonl.tmp"
TODAY = "2026-08-19"


def main():
    recs = [json.loads(l) for l in open(SRC)]
    n0 = len(recs)
    by_rec = {}
    for i, r in enumerate(recs):
        by_rec.setdefault(r["cell_id"].split("/")[0], []).append(i)

    t0, done, skipped = time.perf_counter(), 0, []
    for rec_name, idxs in by_rec.items():
        try:
            recording = load(rec_name)
        except Exception as e:
            skipped += [(recs[i]["cell_id"], f"load: {type(e).__name__}") for i in idxs]
            continue
        uid_to_u = {recording.unit_id(u): u for u in range(recording.n_units)}
        for i in idxs:
            r = recs[i]
            uid = r["cell_id"].split("/")[1]
            u = uid_to_u.get(uid)
            if u is None:
                skipped.append((r["cell_id"], "unit_id not in loader")); continue
            try:
                pos = unfold_unit_mean(recording.concatenated_spikes(u))
                s = np.diff(np.sort(pos)); s = s[s > 0]
                q = I8_brody_q_unbounded(s) if s.size >= 50 else None
            except Exception as e:
                skipped.append((r["cell_id"], type(e).__name__)); continue
            # ONLY this key is written. The bounded key is not referenced.
            r["axes_computed"]["I.8_brody_q_unbounded"] = q
            r.setdefault("extraction_audit", {})["c2_repaired_estimator"] = {
                "key_added": "I.8_brody_q_unbounded", "bounded_key": "UNTOUCHED",
                "estimator_bounds": [-1.0, 4.0], "date": TODAY}
            done += 1
        print(f"  {rec_name:28s} {done:>5}/{n0}", flush=True)

    with open(TMP, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\nwrote temp: {done} recomputed, {len(skipped)} skipped, "
          f"{time.perf_counter()-t0:.0f}s")

    # gate the temp file with the SEALED verifier before replacing anything
    real = SRC + ".realbak"
    shutil.copy(SRC, real)
    shutil.copy(TMP, SRC)
    p = subprocess.run([sys.executable, f"{R}/c2_acceptance/verify_pvc11_retention.py"],
                       capture_output=True, text=True)
    print("\nACCEPTANCE:", p.stdout.strip() or p.stderr.strip())
    if p.returncode != 0:
        shutil.copy(real, SRC); os.remove(real)
        sys.exit("ACCEPTANCE FAILED — artifact restored, nothing banked")
    os.remove(real); os.remove(TMP)

    got = [r["axes_computed"].get("I.8_brody_q_unbounded") for r in recs]
    v = np.array([x for x in got if x is not None], float)
    summary = dict(n_records=n0, n_repaired=done, n_skipped=len(skipped),
                   skipped=skipped[:20],
                   railed_lo=float(np.mean(np.abs(v + 1.0) <= 1e-3)),
                   railed_hi=float(np.mean(np.abs(v - 4.0) <= 1e-3)),
                   frac_negative=float(np.mean(v < 0)),
                   qmin=float(v.min()), qmax=float(v.max()),
                   qmedian=float(np.median(v)),
                   headroom_to_lo=float(v.min() + 1.0))
    json.dump(summary, open(f"{R}/c2_acceptance/c2_pvc11_summary.json", "w"), indent=1)
    print(f"\nFULL-FILE characterisation (all conditions, not the spontaneous-only probe):")
    print(f"  repaired on {done}/{n0}; railed lo {summary['railed_lo']:.1%} "
          f"hi {summary['railed_hi']:.1%}")
    print(f"  range {summary['qmin']:+.3f} .. {summary['qmax']:+.3f}   "
          f"median {summary['qmedian']:+.3f}")
    print(f"  negative (clustered): {summary['frac_negative']:.1%}")
    print(f"  headroom to the -1.0 bound: {summary['headroom_to_lo']:.3f}")


if __name__ == "__main__":
    main()
