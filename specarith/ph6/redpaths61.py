"""PH6_SEAL 6.1 §7.2 known answers and red paths from the matched-size bands (bands61.json); no candidate is read.

- Red paths: each Poisson/GOE/GUE/GSE draw classified by (i) the rule AS WRITTEN in §5 (class assigned only if the value
  lies inside exactly one band, else ambiguous) and (ii) for comparison, nearest band mean in band-SD units. Each draw is
  classified against bands built from the OTHER draws (leave-one-out percentiles), so a draw never defines its own band.
- The zeros' known answer (first 3·10⁴ zeros, zeros1 sha256-pinned): ⟨r̃⟩ against each band, z-scores; T2 as written
  (inside the GUE band) and T4 as written.
- Picket fence: ⟨r̃⟩ = 1 (crystal).

  python redpaths61.py BANDS_JSON OUT
"""
import hashlib
import json
import os
import sys

import numpy as np

ZEROS1 = "/home/combust/fmexplorer/criticality_tool/data/odlyzko_zeros1.txt"
ZEROS1_SHA256 = "3436c916a7878261ac183fd7b9448c9a4736b8bbccf1356874a6ce1788541632"


def rtilde(levels):
    s = np.diff(np.sort(levels))
    return float((np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])).mean())


def classify(v, bands):
    inside = [k for k, b in bands.items() if b["band"][0] <= v <= b["band"][1]]
    as_written = inside[0] if len(inside) == 1 else ("ambiguous" if inside else "none")
    nearest = min(bands, key=lambda k: abs(v - bands[k]["mean"]) / bands[k]["sd"])
    return as_written, nearest


def main(path, out):
    B = json.load(open(path))["bands"]
    vals = {k: np.array(b["values"]) for k, b in B.items()}
    conf_w = {k: {} for k in vals}
    conf_n = {k: {} for k in vals}
    for k, v in vals.items():
        for i, x in enumerate(v):
            loo = {}
            for kk, vv in vals.items():
                w = np.delete(vv, i) if kk == k else vv
                loo[kk] = dict(band=[float(np.percentile(w, 2.5)), float(np.percentile(w, 97.5))],
                               mean=float(w.mean()), sd=float(w.std(ddof=1)))
            a, n = classify(x, loo)
            conf_w[k][a] = conf_w[k].get(a, 0) + 1
            conf_n[k][n] = conf_n[k].get(n, 0) + 1
    bands = {k: dict(band=b["band"], mean=b["mean"], sd=b["sd"], label=b["label_large_N"]) for k, b in B.items()}
    if hashlib.sha256(open(ZEROS1, "rb").read()).hexdigest() != ZEROS1_SHA256:
        raise SystemExit("REFUSED: zeros1 hash")
    z = np.loadtxt(ZEROS1)[:30_000]
    rz = rtilde(z)
    zs = {k: (rz - b["mean"]) / b["sd"] for k, b in bands.items()}
    zw, zn = classify(rz, bands)
    picket = rtilde(np.arange(30_000, dtype=float))
    res = dict(bands=bands, red_paths_as_written=conf_w, red_paths_nearest=conf_n,
               zeros=dict(rtilde=rz, z_vs_bands=zs, T2_as_written_inside_GUE=bool(
                   bands["GUE"]["band"][0] <= rz <= bands["GUE"]["band"][1]), T4_as_written=zw, T4_nearest=zn),
               picket_rtilde=picket)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "redpaths61.json"), "w"), indent=1)
    for k in bands:
        print(f"{k}: band [{bands[k]['band'][0]:.5f}, {bands[k]['band'][1]:.5f}] mean {bands[k]['mean']:.5f} "
              f"sd {bands[k]['sd']:.5f} (label {bands[k]['label']:.4f})  as-written {conf_w[k]}  nearest {conf_n[k]}")
    print(f"zeros <r~> {rz:.5f}; z vs bands {{{', '.join(f'{k}: {v:+.1f}' for k, v in zs.items())}}}; "
          f"T2 as written (inside GUE band): {res['zeros']['T2_as_written_inside_GUE']}; T4 as written: {zw}; "
          f"nearest: {zn}; picket <r~> = {picket}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
