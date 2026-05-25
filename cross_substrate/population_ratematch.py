"""
cross_substrate/population_ratematch.py — rate-match de-confound of the population AREA effect.

population_strat found the avalanche observable (avl-onset) carries a strong, consistent AREA ordering
(Kendall W=0.78: V1/lateral low → higher-areas/LGN high). But areas differ in unit count AND firing rate,
and avalanche structure is rate-dependent ([[ars_rate_dependence_lesson]]) — so the raw area effect may be
mediated by rate, not independent of it. This recomputes the area effect under MATCHED conditions:

  within each (session, block), match every area to a COMMON (N_match units, R_match total spikes):
    • N_match = min area unit-count in that (session,block)  → controls unit count
    • R_match = min over areas of pooled-spike-count at N_match → controls total population rate
  subsample units + thin the pooled train to (N_match, R_match), recompute avl-onset q; K repeats averaged.

If the area ordering SURVIVES rate-matching (W stays high, same order) ⇒ area effect is INDEPENDENT of
rate (biological). If it COLLAPSES (W→0) ⇒ the area effect was rate-MEDIATED. Both are clean verdicts.
corr-eig is carried along as a control (matched to N_match units; it was area-invariant raw).

Out: coordinates/population-ratematch.jsonl + figure P_population_ratematch.png. Run: --run [--workers 10].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np
import h5py

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify                                              # noqa: E402
from cross_substrate.allen_depth import build_targets, NWB_GLOB                # noqa: E402
from cross_substrate.population_fingerprint import _corr_eig, _avalanche_onsets, _fp, _f  # noqa: E402
from cross_substrate.population_strat import BLOCKS, MIN_UNITS, DT             # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
K_REPEATS = 5
SEED = 20260525


def _read_unit_spikes(h, rows, t0, t1):
    sti = h["units/spike_times_index"]; st_all = h["units/spike_times"]
    out = []
    for r in rows:
        lo = 0 if r == 0 else int(sti[r - 1]); hi = int(sti[r])
        spk = st_all[lo:hi]
        out.append(spk[(spk >= t0) & (spk < t1)])
    return out


def _avl_q(pooled):
    if pooled.size < 200:
        return None
    isi = np.diff(pooled); dt_av = float(np.mean(isi[isi > 0])) if (isi > 0).any() else 5e-3
    onsets = _avalanche_onsets(pooled, dt_av)
    if onsets is None or len(onsets) < 50:
        return None
    return _f(_fp(onsets, is_positions=True).get("I.8_brody_q"))


def _corr_q(per_unit, t0, t1):
    nb = max(4, int((t1 - t0) / DT)); edges = np.linspace(t0, t1, nb + 1)
    M = np.array([np.histogram(s, bins=edges)[0] for s in per_unit], float).T
    pos = _corr_eig(M)
    return _f(_fp(pos, is_positions=True).get("I.8_brody_q")) if pos is not None else None


def _task(arg):
    f, sid, blk, t0, t1, area_rows = arg
    rng = np.random.default_rng(SEED + hash((sid, blk)) % 10_000)
    with h5py.File(f, "r") as h:
        area_units = {a: _read_unit_spikes(h, rows, t0, t1) for a, rows in area_rows.items()}
    N_match = min(len(u) for u in area_units.values())
    # expected pooled spikes at N_match per area (mean rate × N_match), to set the common R_match
    exp_pooled = {a: sum(s.size for s in us) * N_match / len(us) for a, us in area_units.items()}
    R_match = int(min(exp_pooled.values()))
    recs = []
    for a, us in area_units.items():
        avl_qs, corr_qs = [], []
        for k in range(K_REPEATS):
            pick = rng.choice(len(us), N_match, replace=False)
            sub = [us[i] for i in pick]
            pooled = np.sort(np.concatenate(sub)) if sub else np.zeros(0)
            if pooled.size > R_match:                          # thin to common total spikes
                pooled = np.sort(rng.choice(pooled, R_match, replace=False))
            avl_qs.append(_avl_q(pooled))
            corr_qs.append(_corr_q(sub, t0, t1))
        def _avg(xs):
            v = [x for x in xs if isinstance(x, float)]
            return float(np.mean(v)) if v else None
        recs.append({"substrate": "population-ratematch", "cell_id": f"{sid}/{a}/{blk}",
                     "session": sid, "area": a, "block": blk,
                     "N_match": int(N_match), "R_match": int(R_match),
                     "avl_q_matched": _avg(avl_qs), "corr_q_matched": _avg(corr_qs),
                     "source_artifact": f"generated (rate-matched N={N_match},R={R_match}, K={K_REPEATS})",
                     "computed_date": date.today().isoformat()})
    return recs


def _build_tasks(files, targets):
    tasks = []
    for f in files:
        sid = int(os.path.basename(os.path.dirname(f)).split("_")[1])
        srows = targets[targets["session_id"] == sid]
        areas = [a for a, c in srows.groupby("area").size().items() if c >= MIN_UNITS]
        if len(areas) < 2:
            continue
        with h5py.File(f, "r") as h:
            row_of = {int(u): r for r, u in enumerate(h["units/id"][:])}
            for blk in BLOCKS:
                key = f"intervals/{blk}_presentations"
                if key not in h:
                    continue
                st, sp = h[key]["start_time"][:], h[key]["stop_time"][:]
                t0, t1 = float(st.min()), float(sp.max())
                area_rows = {}
                for a in areas:
                    rows = [row_of[int(u)] for u in srows[srows["area"] == a]["unit_id"].astype(int)
                            if int(u) in row_of]
                    if len(rows) >= MIN_UNITS:
                        area_rows[a] = rows
                if len(area_rows) >= 2:
                    tasks.append((f, sid, blk, t0, t1, area_rows))
    return tasks


def _kendall_w(rank_matrix):
    R = np.asarray(rank_matrix, float); n, k = R.shape
    if n < 2 or k < 2:
        return None
    cs = R.sum(axis=0)
    return float(12 * np.sum((cs - cs.mean()) ** 2) / (n ** 2 * (k ** 3 - k)))


def run(workers=10):
    targets = build_targets()
    files = sorted(glob.glob(NWB_GLOB))
    tasks = _build_tasks(files, targets)
    print(f"RATE-MATCH DE-CONFOUND — {len(tasks)} (session,block) cells, K={K_REPEATS} repeats, {workers}w")
    out = os.path.join(COORD, "population-ratematch.jsonl")
    t0 = time.perf_counter()
    allrecs = []
    with open(out, "w") as fh, ProcessPoolExecutor(max_workers=workers) as ex:
        for recs in ex.map(_task, tasks):
            for r in recs:
                fh.write(json.dumps(r) + "\n"); fh.flush(); allrecs.append(r)
    print(f"→ {len(allrecs)} matched cells in {(time.perf_counter()-t0)/60:.1f} min\n")

    # area Kendall-W under matching, vs the raw W=0.78
    from scipy import stats
    for key, lab, raw in [("avl_q_matched", "avl-onset (matched)", 0.783),
                          ("corr_q_matched", "corr-eig (matched, control)", 0.045)]:
        groups, areas_seen = {}, set()
        for r in allrecs:
            if isinstance(r.get(key), float):
                groups.setdefault((r["session"], r["block"]), {})[r["area"]] = r[key]
                areas_seen.add(r["area"])
        areas = sorted(areas_seen)
        rm = [[g[a] for a in areas] for g in groups.values() if all(a in g for a in areas)]
        if len(rm) >= 2:
            ranks = np.array([stats.rankdata(row) for row in rm])
            W = _kendall_w(ranks)
            meanq = {a: float(np.mean([row[i] for row in rm])) for i, a in enumerate(areas)}
            order = sorted(meanq, key=meanq.get)
            print(f"{lab}: W={W:.3f} (raw {raw:.3f}, n={len(rm)} groups)")
            print(f"   low→high q: {' < '.join(f'{a}({meanq[a]:.2f})' for a in order)}")
            if key == "avl_q_matched":
                verdict = ("SURVIVES rate-matching ⇒ area effect INDEPENDENT of rate (biological)"
                           if W > 0.4 else
                           "COLLAPSES under rate-matching ⇒ area effect was rate-MEDIATED")
                print(f"   ⇒ {verdict}")
    print("\nFlag, don't interpret — verdict is Will's.")
    _figure(allrecs)


def _figure(allrecs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    areas = sorted(set(r["area"] for r in allrecs))
    fig, ax = plt.subplots(figsize=(8, 5))
    by = {a: [r["avl_q_matched"] for r in allrecs if r["area"] == a and isinstance(r.get("avl_q_matched"), float)]
          for a in areas}
    order = sorted(areas, key=lambda a: np.mean(by[a]) if by[a] else 0)
    ax.boxplot([by[a] for a in order], labels=order, showmeans=True)
    ax.set_ylabel("avl-onset Brody q (rate-matched)")
    ax.set_title("Avalanche AREA effect under rate-matching (N_match units + R_match spikes)\n"
                 "does the V1/lateral-low → higher-area/LGN-high ordering survive?")
    ax.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P_population_ratematch.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.run:
        run(a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
