"""
cross_substrate/brocot_landscape.py — brocot.fm landscape placement (deliverable 1).

Fingerprints the full phase3 pull_index corpus (4,310 exemplars across 33 musical-family categories)
on the cross-substrate instrument: partial-frequency NNS (Family I, where ≥20 partials) + RF per-prime
(Family III, all). Predicts each exemplar's partial spectrum analytically (predict_partials from its
operator config — no audio). Banks the brocot.fm substrate and asks where its families sit on the
landscape (and whether the prime-named families carry their prime in the RF leg).

Out: coordinates/brocot-landscape.jsonl. Run: --run.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
for p in (_BROCOT, _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from phase3.partial_prediction import predict_partials                # noqa: E402
from phase3.config import path_ratio                                  # noqa: E402
from phase3.ars.arithmetic_toolkit import padic_amplitude_v4          # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I, compute_family_II  # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
PRIMES = (2, 3, 5, 7, 11, 13)


def _f(v):
    return None if v is None or not (isinstance(v, (int, float)) and np.isfinite(v)) else float(v)


def _fingerprint(freqs):
    f = np.sort(np.asarray(freqs, float))
    out = {"n_partials": int(f.size)}
    if f.size >= 20:
        s = canonical_spacings(f)
        for k, fn in FAMILY_I.items():
            out[k] = _f(fn(s))
        for k, v in compute_family_II(f).items():
            out[k] = _f(v) if isinstance(v, (int, float)) else None
    try:
        pp = padic_amplitude_v4(f, primes=PRIMES, q_max=32).get("per_prime", {})
        for p in PRIMES:
            out[f"III.1_p{p}"] = _f(pp.get(p, {}).get("normalised"))
    except Exception:
        pass
    return out


def _task(arg):
    cat, preset, nops, obj, ratios, depths, fc = arg
    try:
        # eps=5e-3 + max_partials cap bound the deep-8-modulator Cartesian-product blowup
        sp = predict_partials(ratios, depths, f_carrier=fc, eps=5e-3, max_partials=1500)
    except Exception:
        return None
    fp = _fingerprint(sp.freqs)
    return {"substrate": "brocot.fm", "cell_id": f"{cat}/{preset}", "category": cat, "n_ops": nops,
            "axes_computed": fp,
            "extraction_audit": {"preset": preset, "objective": obj,
                                 "n_partials": fp["n_partials"], "f_carrier": fc},
            "source_artifact": "generated (predict_partials from pull_index config)",
            "computed_date": date.today().isoformat()}


def run(workers=10):
    d = json.load(open(os.path.join(_BROCOT, "resources/pull_index.json")))
    cats, fc = d["categories"], d["f_carrier_ref"]
    tasks = []
    for cat, cd in cats.items():
        for i, ex in enumerate(cd.get("exemplars", [])):
            rd = [(path_ratio(o["path"]), o["depth"]) for o in ex.get("ops", [])
                  if o.get("enabled") and o.get("path", "") != ""]
            if rd:
                tasks.append((cat, ex.get("preset", i), ex.get("n_ops"), ex.get("objective"),
                              [r for r, _ in rd], [dp for _, dp in rd], fc))
    out = os.path.join(COORD, "brocot-landscape.jsonl")
    recs, n_nns = [], 0
    with open(out, "w") as fh, ProcessPoolExecutor(max_workers=workers) as ex:
        for rec in as_completed([ex.submit(_task, t) for t in tasks]):
            r = rec.result()
            if r is None:
                continue
            fh.write(json.dumps(r) + "\n"); fh.flush()
            recs.append(r)
            if r["axes_computed"].get("I.8_brody_q") is not None:
                n_nns += 1
    print(f"BROCOT.FM LANDSCAPE — {len(recs)}/{len(tasks)} exemplars fingerprinted ({n_nns} with NNS Family I)")

    # per-category placement (median), + RF dominant-prime for the prime-named families
    import pandas as pd
    df = pd.DataFrame([{**r["axes_computed"], "category": r["category"]} for r in recs])
    print(f"\n{'category':18s} {'n':>4s} {'medI.5':>7s} {'medW1δ':>7s} {'medQ':>6s} {'medΣ²':>8s} {'RF: p2/p3/p5/p7':>22s}")
    for cat in sorted(df["category"].unique()):
        sub = df[df["category"] == cat]
        def m(k):
            v = sub[k].dropna() if k in sub else []
            return f"{np.median(v):.3f}" if len(v) else "  -"
        rf = "/".join(m(f"III.1_p{p}") for p in (2, 3, 5, 7))
        print(f"{cat:18s} {len(sub):>4d} {m('I.5_ks_gue'):>7s} {m('I.1_w1_clock'):>7s} "
              f"{m('I.8_brody_q'):>6s} {m('II.1_sigma2_L'):>8s} {rf:>22s}")
    print("\n→ coordinates/brocot-landscape.jsonl. (Do the Prime-p families carry p in the RF leg?)")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.run:
        run()
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
