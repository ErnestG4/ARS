"""
cross_substrate/allen_avalanche.py — neural-criticality (Beggs-Plenz) cross-reference.

The criticality literature characterizes cortical population activity by neuronal-AVALANCHE
statistics: size P(S)~S^−τ and duration P(T)~T^−α power laws, with the crackling-noise scaling
relation ⟨S⟩(T) ~ T^{1/(σνz)}, where at criticality 1/(σνz) = (α−1)/(τ−1). This places each Allen
recording in that framework and asks the cross-reference question: **do our universality-class
fingerprints (I.5q, W1δ, Family II) correlate with avalanche-criticality measures — i.e. where do
"critical" recordings sit on our landscape?**

Per (session, block): pool all good target-area units' spikes; bin at Δt = population mean ISI
(standard Beggs choice); avalanche = run of non-empty bins bounded by empty bins; collect sizes
(Σ spikes) + durations (n bins). MLE power-law exponents (Clauset, discrete, x≥xmin) + crackling
exponent (regress ⟨S|T⟩) vs predicted (α−1)/(τ−1); |Δ_crackling| is a distance-from-criticality.
Then merge with per-(session) median fingerprint from allen-depth.jsonl.

Blocks: spontaneous (canonical) + drifting_gratings. Cheap (binning + fits). Cached data only.
Run: --run.  Out: coordinates/allen-avalanche.jsonl + prints the cross-reference table.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import glob
import json
import sys

import numpy as np
import h5py

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT,):
    if p not in sys.path:
        sys.path.insert(0, p)

CACHE = os.path.expandvars("$HOME/fmexplorer/allen_cache")
NWB_GLOB = CACHE + "/session_*/session_*.nwb"
COORD = os.path.join(_HERE, "coordinates")
from cross_substrate.allen_depth import build_targets       # noqa: E402
BLOCKS = ["spontaneous", "drifting_gratings"]


def _pop_spikes(h, unit_rows, t0, t1):
    """All spikes from the given unit rows within [t0,t1], pooled and sorted."""
    sti = h["units/spike_times_index"]
    chunks = []
    for r in unit_rows:
        lo = 0 if r == 0 else int(sti[r - 1])
        hi = int(sti[r])
        spk = h["units/spike_times"][lo:hi]
        i0 = np.searchsorted(spk, t0, "left")
        i1 = np.searchsorted(spk, t1, "left")
        if i1 > i0:
            chunks.append(spk[i0:i1])
    return np.sort(np.concatenate(chunks)) if chunks else np.zeros(0)


def _avalanches(spikes, dt):
    """Bin pooled spikes at dt; avalanches = runs of non-empty bins. Returns (sizes, durations)."""
    if spikes.size < 100:
        return np.array([]), np.array([])
    t0, t1 = spikes[0], spikes[-1]
    nb = max(2, int(np.ceil((t1 - t0) / dt)))
    counts, _ = np.histogram(spikes, bins=nb, range=(t0, t1))
    active = counts > 0
    sizes, durs, s, d = [], [], 0, 0
    for c, a in zip(counts, active):
        if a:
            s += c; d += 1
        elif d > 0:
            sizes.append(s); durs.append(d); s, d = 0, 0
    if d > 0:
        sizes.append(s); durs.append(d)
    return np.array(sizes, float), np.array(durs, float)


def _mle_exponent(x, xmin):
    """Clauset discrete-ish MLE: τ = 1 + n / Σ ln(x/(xmin−0.5)). Returns (exp, n_used)."""
    xx = x[x >= xmin]
    if xx.size < 30:
        return None, xx.size
    return 1.0 + xx.size / np.sum(np.log(xx / (xmin - 0.5))), xx.size


def _crackling(sizes, durs):
    """Empirical ⟨S|T⟩ scaling exponent via log-log regression of mean size vs duration."""
    if sizes.size < 30:
        return None
    ut = np.unique(durs)
    xs, ys = [], []
    for t in ut:
        m = durs == t
        if m.sum() >= 3:
            xs.append(t); ys.append(sizes[m].mean())
    if len(xs) < 4:
        return None
    return float(np.polyfit(np.log(xs), np.log(ys), 1)[0])


def run():
    targets = build_targets()
    recs = []
    print("AVALANCHE CRITICALITY — per (session, block): τ (size), α (duration), crackling\n")
    print(f"{'session':>10s} {'block':>17s} {'nunits':>6s} {'navl':>6s} {'τ':>5s} {'α':>5s} "
          f"{'crk':>5s} {'pred':>5s} {'|Δ|':>5s}")
    for f in sorted(glob.glob(NWB_GLOB)):
        sid = int(os.path.basename(os.path.dirname(f)).split("_")[1])
        rows = targets[targets["session_id"] == sid]
        with h5py.File(f, "r") as h:
            ids = h["units/id"][:]
            row_of = {int(u): r for r, u in enumerate(ids)}
            urows = [row_of[int(u)] for u in rows["unit_id"] if int(u) in row_of]
            for blk in BLOCKS:
                key = f"intervals/{blk}_presentations"
                if key not in h:
                    continue
                st, sp = h[key]["start_time"][:], h[key]["stop_time"][:]
                t0, t1 = float(st.min()), float(sp.max())
                spikes = _pop_spikes(h, urows, t0, t1)
                if spikes.size < 1000:
                    continue
                isi = np.diff(spikes)
                dt = float(np.mean(isi[isi > 0])) if (isi > 0).any() else 1e-3
                sizes, durs = _avalanches(spikes, dt)
                tau, ns = _mle_exponent(sizes, 2.0)
                alpha, nd = _mle_exponent(durs, 2.0)
                crk = _crackling(sizes, durs)
                pred = ((alpha - 1) / (tau - 1)) if (tau and alpha and tau > 1) else None
                dcrk = abs(crk - pred) if (crk is not None and pred is not None) else None
                recs.append({"substrate": "allen-avalanche",
                             "cell_id": f"{sid}/{blk}",
                             "session": sid, "block": blk, "n_units": len(urows),
                             "n_avalanches": int(sizes.size), "dt_ms": dt * 1000,
                             "tau_size": tau, "alpha_dur": alpha, "crackling": crk,
                             "crackling_pred": pred, "crackling_dev": dcrk})
                def s(v):
                    return f"{v:.2f}" if isinstance(v, (int, float)) else "  -"
                print(f"{sid:>10d} {blk:>17s} {len(urows):>6d} {int(sizes.size):>6d} "
                      f"{s(tau):>5s} {s(alpha):>5s} {s(crk):>5s} {s(pred):>5s} {s(dcrk):>5s}",
                      flush=True)
    with open(os.path.join(COORD, "allen-avalanche.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ {len(recs)} (session,block) avalanche records banked")
    _cross_reference(recs)


def _cross_reference(recs):
    """Merge per-session avalanche criticality with per-session median fingerprint (depth)."""
    dp = os.path.join(COORD, "allen-depth.jsonl")
    if not os.path.exists(dp):
        print("  (allen-depth.jsonl not present yet — run cross-reference after depth completes)")
        return
    import pandas as pd
    df = pd.DataFrame([{**json.loads(l)["axes_computed"], "session": json.loads(l)["session"],
                        "stim": json.loads(l)["stimulus"]} for l in open(dp)])
    print("\nCROSS-REFERENCE — criticality-deviation vs fingerprint (per session, drifting gratings):")
    av = {r["session"]: r for r in recs if r["block"] == "drifting_gratings"}
    rows = []
    for sid, a in av.items():
        sub = df[(df["session"] == sid) & (df["stim"] == "drifting_gratings")]
        if len(sub) < 10 or a["crackling_dev"] is None:
            continue
        rows.append((a["crackling_dev"], sub["I.5q_ks_gue_med"].median(),
                     sub["I.1_w1_clock"].median()))
    if len(rows) >= 5:
        from scipy import stats
        rows = np.array(rows)
        r1, p1 = stats.spearmanr(rows[:, 0], rows[:, 1])
        r2, p2 = stats.spearmanr(rows[:, 0], rows[:, 2])
        print(f"  ρ(|Δ_crackling|, med I.5q) = {r1:+.3f} (p={p1:.2f}, n={len(rows)})")
        print(f"  ρ(|Δ_crackling|, med W1δ) = {r2:+.3f} (p={p2:.2f})")
        print("  (near-critical = small |Δ_crackling|; does it track fingerprint position?)")


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
