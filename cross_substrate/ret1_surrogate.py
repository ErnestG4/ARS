"""
cross_substrate/ret1_surrogate.py — surrogate-null for retinal ks_gue: is it structured or just in-range?

"ks_gue median 0.477 in the neural band" is a PRECONDITION (computable, non-degenerate), not a finding.
To make it a finding, test whether each RGC's real ks_gue is distinguishable from rate-matched surrogates
that destroy temporal structure. Two nulls per cell:
  - Poisson:    n spikes uniform on [0,T] (rate-matched, destroys ALL structure incl. refractoriness/bursts)
  - ISI-shuffle: permute the real ISIs (preserves ISI marginal incl. bursts/refractoriness, destroys order)
Per cell: real ks_gue, K surrogate ks_gue each → z = (real - mean_surr)/std_surr. If real systematically
departs from Poisson, ks_gue carries structure beyond rate. ISI-shuffle ≈ Poisson would localize structure
to the ISI marginal; ISI-shuffle ≈ real (and both ≠ Poisson) would mean the structure is in the ISI
distribution not in sequence. Reuses ret1_port loader + ars_classify.

Run: --run [--k 10] [--workers 10].  Out: coordinates/ret1-surrogate.jsonl
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np
import scipy.io

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify                                             # noqa: E402

DATA = os.path.expandvars("$HOME/fmexplorer/crcns_cache/ret1/crcns_ret-1/Data")
COORD = os.path.join(_HERE, "coordinates")
K_DEFAULT = 10


def _ksg(spk):
    try:
        v = classify(np.sort(spk)).get("ks_gue_med")
        return float(v) if v is not None and np.isfinite(v) else None
    except Exception:
        return None


def _extract():
    """All (rid, cell, spk, T) over the longest white-noise block per recording."""
    out = []
    for f in sorted(glob.glob(os.path.join(DATA, "*.mat"))):
        rid = os.path.basename(f).replace(".mat", "")
        m = scipy.io.loadmat(f, squeeze_me=True, struct_as_record=False)
        stim = np.atleast_1d(m["stimulus"]); ncell = int(getattr(m["datainfo"], "Ncell")); nstim = len(stim)
        sp = np.asarray(m["spikes"], dtype=object)
        if sp.ndim == 1:
            sp = sp.reshape(ncell, nstim) if nstim == 1 else sp.reshape(nstim, ncell).T
        elif sp.shape[0] != ncell and sp.shape[1] == ncell:
            sp = sp.T
        durs = [float(s.frame) * int(s.Nframes) for s in stim]
        blk = int(np.argmax(durs)); T = durs[blk]
        for i in range(ncell):
            spk = np.sort(np.atleast_1d(sp[i, blk]).astype(float))
            spk = spk[np.isfinite(spk)]
            if spk.size >= 100:
                out.append((rid, i, spk, T))
    return out


def _task(arg):
    rid, cell, spk, T, K, seed = arg
    rng = np.random.RandomState(seed)
    real = _ksg(spk)
    isi = np.diff(spk)
    pois, shuf = [], []
    for _ in range(K):
        ps = np.sort(rng.uniform(0, T, spk.size))
        pois.append(_ksg(ps))
        sh = spk[0] + np.concatenate([[0.0], np.cumsum(rng.permutation(isi))])
        shuf.append(_ksg(sh))
    pois = [v for v in pois if v is not None]; shuf = [v for v in shuf if v is not None]
    def stat(real, surr):
        if real is None or len(surr) < 3:
            return None, None
        mu, sd = float(np.mean(surr)), float(np.std(surr))
        z = (real - mu) / sd if sd > 0 else None
        return mu, z
    pmu, pz = stat(real, pois); smu, sz = stat(real, shuf)
    return {"substrate": "ret1-surrogate", "recording": rid, "cell": cell, "n": int(spk.size),
            "rate_hz": round(spk.size / T, 4), "ks_gue_real": real,
            "ks_gue_poisson_mean": pmu, "z_vs_poisson": pz,
            "ks_gue_isishuffle_mean": smu, "z_vs_isishuffle": sz,
            "K": len(pois), "computed_date": date.today().isoformat()}


def run(K=K_DEFAULT, workers=10):
    cells = _extract()
    tasks = [(rid, c, spk, T, K, 1000 + i) for i, (rid, c, spk, T) in enumerate(cells)]
    out = open(os.path.join(COORD, "ret1-surrogate.jsonl"), "w")
    print(f"ret-1 SURROGATE-NULL — {len(tasks)} RGCs x {K} (Poisson + ISI-shuffle), {workers}w")
    recs = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(_task, tasks):
            out.write(json.dumps(r) + "\n"); recs.append(r)
    out.close()
    # summary
    real = np.array([r["ks_gue_real"] for r in recs if r["ks_gue_real"] is not None])
    pm = np.array([r["ks_gue_poisson_mean"] for r in recs if r["ks_gue_poisson_mean"] is not None])
    sm = np.array([r["ks_gue_isishuffle_mean"] for r in recs if r["ks_gue_isishuffle_mean"] is not None])
    pz = np.array([r["z_vs_poisson"] for r in recs if r["z_vs_poisson"] is not None])
    sz = np.array([r["z_vs_isishuffle"] for r in recs if r["z_vs_isishuffle"] is not None])
    from scipy import stats
    print(f"\nn={len(recs)} cells")
    print(f"  real ks_gue        median={np.median(real):.3f}")
    print(f"  Poisson-surr ks_gue median={np.median(pm):.3f}   (rate-matched, structure destroyed)")
    print(f"  ISI-shuffle  ks_gue median={np.median(sm):.3f}   (ISI marginal preserved, order destroyed)")
    print(f"  z(real vs Poisson):    median={np.median(pz):+.2f}  |z|>2 in {(np.abs(pz)>2).mean()*100:.0f}% of cells")
    print(f"  z(real vs ISIshuffle): median={np.median(sz):+.2f}  |z|>2 in {(np.abs(sz)>2).mean()*100:.0f}% of cells")
    kp = stats.ks_2samp(real, pm); print(f"  KS real-vs-Poisson distributions: D={kp.statistic:.3f} p={kp.pvalue:.1e}")
    print("  -> real != Poisson => retinal ks_gue carries temporal structure beyond rate (not just in-range).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--k", type=int, default=K_DEFAULT)
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.run:
        run(a.k, a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
