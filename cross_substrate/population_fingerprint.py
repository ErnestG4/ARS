"""
cross_substrate/population_fingerprint.py — population-level fingerprints (finding §7(h) follow-up).

Avalanche-orthogonality (§7(h)) says population-collective structure is a DIFFERENT observable from
per-cell universality class. This builds population-level fingerprints by aggregating spike trains
across a spatially-organized population several ways, then fingerprinting each aggregate — asking
whether population-level fingerprints form a COHERENT landscape position or FRAGMENT by aggregation
choice. Focused: one Allen session × {spontaneous, drifting_gratings}.

Four aggregation choices (each a distinct "population observable"):
  A. CORR-EIG — pairwise spike-count correlation-matrix bulk eigenvalue spectrum (RMT of empirical
     covariance; a genuine spectral object — no extractor artifact). Outliers (global mode) dropped;
     bulk unfolded (polynomial-IDS), NNS fingerprinted. The principled anchor.
  B. AVL-ONSET — avalanche onset TIMES (population point process; reuses the §7(h) avalanche detector).
  C. SYNC-EVENT — population-rate threshold-upcrossing times (network events; threshold-extractor —
     FLAGGED per Finding F, cross-checked against the corr-eig anchor).
  D. RATE-PEAK — find_peaks on smoothed population rate (continuous-trace extraction — FLAGGED per
     §7.ter.19 as artifact-prone; included only as the known-artifact contrast).

Fingerprint each (I.5q + I.5 + W1δ + Brody q + Σ²) and compare to the calibration anchors. Cached
data, one session. Out: coordinates/population-fingerprint.jsonl. Run: --run [--session N].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import glob
import json
import sys
from datetime import date

import numpy as np
import h5py
from scipy.signal import find_peaks

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify, unfold_unit_mean                  # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I, compute_family_II  # noqa: E402
from cross_substrate.allen_depth import build_targets, NWB_GLOB      # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
BLOCKS = ["spontaneous", "drifting_gratings"]


def _f(v):
    return None if v is None or not np.isfinite(v) else float(v)


def _pop_spike_matrix(h, urows, t0, t1, dt):
    """Binned count matrix (T bins × N units) over [t0,t1] at bin dt; + pooled spike times."""
    sti = h["units/spike_times_index"]
    nb = max(4, int((t1 - t0) / dt))
    edges = np.linspace(t0, t1, nb + 1)
    M, pooled = [], []
    for r in urows:
        lo = 0 if r == 0 else int(sti[r - 1])
        hi = int(sti[r])
        spk = h["units/spike_times"][lo:hi]
        spk = spk[(spk >= t0) & (spk < t1)]
        M.append(np.histogram(spk, bins=edges)[0])
        pooled.append(spk)
    return np.array(M, float).T, (np.sort(np.concatenate(pooled)) if pooled else np.zeros(0)), edges


def _poly_unfold(x, deg=10):
    e = np.sort(np.asarray(x, float))
    c = np.polyfit(e, np.arange(1, e.size + 1, dtype=float), deg)
    return np.polyval(c, e)


def _fp(spacings_or_pos, is_positions=True):
    """Fingerprint: I.5/W1δ/Brody/BRρ (Family I) + Σ²/Δ₃ (Family II) from positions."""
    if is_positions:
        pos = np.asarray(spacings_or_pos, float)
        s = canonical_spacings(pos)
    else:
        s = np.asarray(spacings_or_pos, float)
        pos = np.cumsum(s)
    fI = {k: _f(fn(s)) for k, fn in FAMILY_I.items()}
    fII = {k: _f(v) if isinstance(v, (int, float)) else None for k, v in compute_family_II(pos).items()}
    return {**fI, **fII}


def _corr_eig(M):
    """Bulk eigenvalue NNS of the unit×unit spike-count correlation matrix."""
    keep = M.std(axis=0) > 0
    M = M[:, keep]
    if M.shape[1] < 20:
        return None
    C = np.corrcoef(M.T)
    ev = np.sort(np.linalg.eigvalsh(C))
    # drop global-mode outliers above the Marchenko-Pastur edge λ+ = (1+√(N/T))²
    q = M.shape[1] / M.shape[0]
    mp_plus = (1 + np.sqrt(q)) ** 2
    bulk = ev[ev < mp_plus * 1.1]
    bulk = bulk[bulk > 1e-6]
    if bulk.size < 30:
        return None
    return _poly_unfold(bulk)


def _avalanche_onsets(pooled, dt):
    if pooled.size < 200:
        return None
    counts, edges = np.histogram(pooled, bins=max(4, int((pooled[-1] - pooled[0]) / dt)))
    active = counts > 0
    onsets = []
    prev = False
    for i, a in enumerate(active):
        if a and not prev:
            onsets.append(edges[i])
        prev = a
    return np.array(onsets, float) if len(onsets) > 50 else None


def _sync_events(M, edges):
    pop = M.sum(axis=1)
    thr = pop.mean() + 2 * pop.std()
    up = (pop[1:] >= thr) & (pop[:-1] < thr)
    t = edges[:-1][1:][up]
    return t if t.size > 50 else None


def _rate_peaks(M, edges):
    pop = M.sum(axis=1).astype(float)
    if pop.size < 100:
        return None
    pk, _ = find_peaks(pop, prominence=pop.std() * 0.5)
    t = edges[:-1][pk]
    return t if t.size > 50 else None


def run(only_session=None):
    targets = build_targets()
    files = sorted(glob.glob(NWB_GLOB))
    if only_session:
        files = [f for f in files if f"session_{only_session}" in f]
    else:
        files = files[:1]                       # one session (focused study)
    recs = []
    print("POPULATION-LEVEL FINGERPRINTS — coherent landscape position or fragment by aggregation?")
    print(f"{'block':17s} {'aggregation':14s} {'n':>5s} {'I.5q':>6s} {'I.5':>6s} {'W1δ':>6s} {'q':>6s} {'BRρ':>6s} {'Σ²':>8s}")
    for f in files:
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
                M, pooled, edges = _pop_spike_matrix(h, urows, t0, t1, dt=0.025)
                isi = np.diff(pooled); dt_av = float(np.mean(isi[isi > 0])) if (isi > 0).any() else 5e-3
                aggs = {
                    "corr-eig": (_corr_eig(M), True, "spectral — no extractor"),
                    "avl-onset": (_avalanche_onsets(pooled, dt_av), True, "point process"),
                    "sync-event": (_sync_events(M, edges), True, "threshold-extractor (FLAGGED)"),
                    "rate-peak": (_rate_peaks(M, edges), True, "find_peaks (ARTIFACT-FLAGGED contrast)"),
                }
                for name, (obj, is_pos, note) in aggs.items():
                    if obj is None or len(obj) < 50:
                        continue
                    fp = _fp(obj, is_positions=is_pos)
                    try:
                        i5q = _f(classify(np.sort(np.asarray(obj, float))).get("ks_gue_med"))
                    except Exception:
                        i5q = None
                    ax = {"I.5q_ks_gue_med": i5q, **fp}
                    recs.append({"substrate": "population-fingerprint",
                                 "cell_id": f"{sid}/{blk}/{name}", "session": sid, "block": blk,
                                 "aggregation": name, "n": int(len(obj)),
                                 "axes_computed": ax,
                                 "extraction_audit": {"note": note, "n_units": len(urows)},
                                 "source_artifact": "generated (population aggregation)",
                                 "computed_date": date.today().isoformat()})
                    def g(k):
                        v = ax.get(k)
                        return f"{v:.3f}" if isinstance(v, float) else "  -"
                    print(f"{blk:17s} {name:14s} {len(obj):>5d} {g('I.5q_ks_gue_med'):>6s} "
                          f"{g('I.5_ks_gue'):>6s} {g('I.1_w1_clock'):>6s} {g('I.8_brody_q'):>6s} "
                          f"{g('I.9_berry_robnik_rho'):>6s} {g('II.1_sigma2_L'):>8s}")
    with open(os.path.join(COORD, "population-fingerprint.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ {len(recs)} population fingerprints banked. COHERENT (cluster) or FRAGMENT (scatter by "
          "aggregation)? Compare to calibration-anchors + per-cell Allen. Flag, don't interpret.")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--session", type=int, default=None)
    a = ap.parse_args()
    if a.run:
        run(a.session)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
