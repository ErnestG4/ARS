# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2 archive count report (Will, 2026-11-04: "−148: the final manifest's count check must cover −148 explicitly.
Report its segment counts against expectation alongside the others."). Counts and hashes only; no statistic of the
angles (the rows' angles are never computed here).

From the 18 MANIFEST.json files:
- per field: all_integrity (each segment's norms equal its principal split primes, fn1h2_archive._check), total rows,
  total split count, rows / split (genus equidistribution: ½), rows against li(X*)/4 = 220,553,720 (Chebotarev density
  1/4; deviation also in units of √(li(X*)/4));
- per segment: rows / (the median over the 18 fields of that segment's rows); min and max per field, and the
  segments outside [0.98, 1.02];
- **−148 explicitly**, plus an independent recount at segments 0, 100 and 199: primes by the shared sieve, split and
  principal by Euler's criterion pow(·, (p−1)/2, p) on D and on the genus discriminant 37 (not the generator's
  Kronecker tables), against the manifest's rows. Same recount for −52 (same Cornacchia type) for comparison.

  python fn1h2_counts.py ROOT OUT_JSON
"""
import json, math, os, sys

import numpy as np

import fn1h2_archive as H
import rq1_angles as R

LI_QUARTER = 882214879.2047648 / 4


def recount(D, k, q):
    ps = R.primes_in(max(k * H.SEG, 2), (k + 1) * H.SEG)
    n = 0
    for p in ps.tolist():
        if p == 2 or (-D) % p == 0:
            continue
        if pow(D % p, (p - 1) // 2, p) == 1 and pow(q % p, (p - 1) // 2, p) == 1:
            n += 1
    return n


def main(root, out):
    res = dict(label="FN1-h2 archive counts (counts and hashes only)", li_X_over_4=LI_QUARTER, fields={})
    rows = {}
    for D in H.FIELDS:
        m = json.load(open(os.path.join(root, f"archive_2e10_D{-D}", "MANIFEST.json")))
        r = np.array([s["rows"] for s in m["segments"]], float)
        rows[D] = r
        res["fields"][str(D)] = dict(all_integrity=m["all_integrity"], rows=int(m["rows"]), split=int(m["split_count"]),
                                     rows_over_split=m["rows"] / m["split_count"],
                                     rows_over_li4=m["rows"] / LI_QUARTER,
                                     dev_sqrt_units=(m["rows"] - LI_QUARTER) / math.sqrt(LI_QUARTER),
                                     segments=len(m["segments"]))
    med = np.median(np.array([rows[D] for D in H.FIELDS]), axis=0)
    for D in H.FIELDS:
        q = rows[D] / med
        res["fields"][str(D)].update(seg_ratio_min=float(q.min()), seg_ratio_max=float(q.max()),
                                     seg_outside_2pct=[int(k) for k in np.where((q < 0.98) | (q > 1.02))[0]])
    rc = {}
    for D, gq in ((-148, 37), (-52, 13)):
        m = json.load(open(os.path.join(root, f"archive_2e10_D{-D}", "MANIFEST.json")))["segments"]
        rc[str(D)] = {str(k): dict(manifest=m[k]["rows"], euler=recount(D, k, gq)) for k in (0, 100, 199)}
    res["independent_recount"] = rc
    res["minus148"] = dict(res["fields"]["-148"], recount=rc["-148"],
                           recount_ok=all(v["manifest"] == v["euler"] for v in rc["-148"].values()))
    res["all_ok"] = all(f["all_integrity"] and f["segments"] == 200 for f in res["fields"].values()) and \
        all(v["manifest"] == v["euler"] for d in rc.values() for v in d.values())
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    for D, f in res["fields"].items():
        print(f"{D:>5} integrity {f['all_integrity']} rows {f['rows']:,} rows/split {f['rows_over_split']:.5f} "
              f"rows/(li/4) {f['rows_over_li4']:.5f} seg ratio [{f['seg_ratio_min']:.3f}, {f['seg_ratio_max']:.3f}] "
              f"outside2% {f['seg_outside_2pct'][:5]}")
    print("-148 recount", rc["-148"], "-52 recount", rc["-52"])
    print("ALL_OK", res["all_ok"])
    return 0 if res["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
