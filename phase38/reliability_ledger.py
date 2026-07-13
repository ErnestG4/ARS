"""
Phase 38 — the Reliability Ledger (runner).

Deliverable: every empirical per-unit axis on Allen carries a banked split-half rho
against its admissibility gate, or it carries no orthogonality verdict at all.
Axis survival is a byproduct.  See PHASE38_RELIABILITY_LEDGER_BRIEF.md.

Banks per-window RAW values for ALL THREE axes on the SAME 5-window partition, so
they share one rho scale:  z_w0..4 (p7 @ 100 independent surrogates),
rep_med_w0..4, ks_gue_med_w0..4.

The four bound requirements, enforced structurally:

  B1 FREEZE THE UNFOLD.  run_phase21_falsification.unfold_unit_mean divides by the
     mean spacing computed *per call* (self-derived rate).  Windowed, each window
     would normalise by its own mean and rho would not transport to the banked R^2.
     Here `mu` is computed ONCE on the full train and applied to every window.
  B2 MATCH THE DECIMATION REGIME.  JPF_CAP=5000 stride-decimates full trains but not
     windows (~n/5) -- silently different estimators across the split.  Decimation is
     DISABLED for both.  (cf. stride_decimation_destroys_prime_angle_structure)
  B3 FIX THE q-SET.  rep_med = median(rep_int_q over well-powered q).  The well set is
     recomputed per window upstream, so the median would run over a different q-set in
     each window -- inter-window disagreement manufactured by aperture drift.  Here a
     single common q-set (well-powered in the full train AND all 5 windows) is used
     everywhere.  n_q_common is banked; if it collapses, that is the finding.
  B4 COHORT INVARIANCE.  rho rises monotonically with event count, so trimming the
     cohort to make windowed rep_med computable INFLATES rho.  This runner trims
     nothing: it emits a row for every cell with a per-cell status flag, and the
     analysis stage re-measures R^2 on whatever cohort it gates.

  p7 REPAIR.  phase32b re-seeded default_rng(seed + 98765) *inside* the window loop,
  so with win_dur constant the surrogate triple was a deterministic function of n --
  equal-n cells got byte-identical surrogates.  The calibrator gate showed this leaks
  rho=+0.257 on cells with NO per-cell axis.  Here every (cell, window) draws its own
  independent surrogates.  rep_med/ks_gue_med use NO surrogates: no surrogate count
  can ever raise their rho, which is set by events-per-window and B1-B3.

Run:  $HOME/fmexplorer/bin/python3 phase38/reliability_ledger.py
"""

import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "phase24"))

from arithmetic_toolkit import (  # noqa: E402
    joint_q_profile, joint_quadrant_diagnostic, padic_amplitude_v4,
)
from loader import load_session  # noqa: E402
from run_per_session_h2 import chunks_for  # noqa: E402

Q_MAX_PADIC = 200
Q_MAX_JQP = 50          # run_phase21_falsification convention
MIN_EVENTS_PER_Q = 30   # run_phase21_falsification convention
N_SURR = 100            # the repair (was 3)
N_WINDOWS = 5
MIN_EVENTS_PER_WINDOW = 30
BIN_MS_MAT = 5.0
N_WORKERS = 10          # worker_count_bandwidth_bound

SESSIONS = [(732592105, "wt"), (791319847, "Vip"), (760693773, "Sst"),
            (762602078, "Sst"), (797828357, "Pvalb"), (755434585, "Vip")]

OUT = Path(ROOT_DIR) / "data" / "phase38_results"
OUT.mkdir(parents=True, exist_ok=True)


# ---- B1 + B2: frozen unfold, no decimation --------------------------------
def full_train_mu(sp):
    """The ONE divisor. Computed on the full train, applied to every window."""
    d = np.diff(sp)
    d = d[d > 0]
    return float(d.mean()) if d.size and d.mean() > 0 else float("nan")


def frozen_unfold(events, mu):
    """Unfold with an externally supplied mu. No stride decimation (B2)."""
    if events.size < 2 or not np.isfinite(mu):
        return np.zeros(0)
    d = np.diff(events)
    d = d[d > 0]
    if d.size == 0:
        return np.zeros(0)
    return np.cumsum(np.concatenate([[0.0], d / mu]))


def q_profile(unfolded):
    if unfolded.size < MIN_EVENTS_PER_Q:
        return None
    j = joint_q_profile(unfolded, q_max=Q_MAX_JQP, min_events_per_q=MIN_EVENTS_PER_Q)
    return joint_quadrant_diagnostic(j)


def _qcol(df):
    return df["q"].to_numpy() if "q" in df.columns else df.index.to_numpy()


def p7_of(events):
    return float(padic_amplitude_v4(events, q_max=Q_MAX_PADIC)["per_prime"][7]["normalised_per_q"])


def _cell(task):
    sid, cre, uid, sp_cat, total_dur, cell_idx = task
    win_dur = total_dur / N_WINDOWS
    row = dict(session_id=sid, cre_line=cre, unit_id=uid,
               total_events=int(sp_cat.size), status="OK")

    mu = full_train_mu(sp_cat)                                    # B1
    if not np.isfinite(mu):
        row["status"] = "NO_UNFOLD"
        return row

    # ---- windows -----------------------------------------------------------
    wins, ok = [], True
    for w in range(N_WINDOWS):
        m = (sp_cat >= w * win_dur) & (sp_cat < (w + 1) * win_dur)
        ev = sp_cat[m] - w * win_dur
        row[f"n_w{w}"] = int(ev.size)
        wins.append(ev)
        if ev.size < MIN_EVENTS_PER_WINDOW:
            ok = False
    if not ok:
        row["status"] = "UNDERCOUNT"

    # ---- p7 @ 100 independent surrogates (the repair) ----------------------
    rng = np.random.default_rng(20260709 + cell_idx)
    for w, ev in enumerate(wins):
        if ev.size < MIN_EVENTS_PER_WINDOW:
            row[f"z_w{w}"] = np.nan
            continue
        real = p7_of(ev)
        sur = np.array([p7_of(np.sort(rng.uniform(0, win_dur, ev.size))) for _ in range(N_SURR)])
        row[f"z_w{w}"] = float((real - sur.mean()) / max(sur.std(), 1e-6))

    # ---- B3: common well-powered q-set across full train + all 5 windows ---
    prof_full = q_profile(frozen_unfold(sp_cat, mu))
    profs = [q_profile(frozen_unfold(ev, mu)) if ev.size >= MIN_EVENTS_PER_Q else None
             for ev in wins]
    if prof_full is None or any(p is None for p in profs):
        row["status"] = "UNDERCOUNT_Q" if row["status"] == "OK" else row["status"]
        row["n_q_common"] = 0
        return row

    common = set(_qcol(prof_full)[~prof_full["underpowered"].to_numpy()])
    for p in profs:
        common &= set(_qcol(p)[~p["underpowered"].to_numpy()])
    common = np.array(sorted(common))
    row["n_q_common"] = int(common.size)
    if common.size == 0:
        row["status"] = "NO_COMMON_Q"
        return row

    def med(prof, col):
        q = _qcol(prof)
        sel = np.isin(q, common)
        return float(np.nanmedian(prof[col].to_numpy()[sel]))

    row["rep_med_full"] = med(prof_full, "rep_int_q")
    row["ks_gue_med_full"] = med(prof_full, "ks_gue_q")
    for w, p in enumerate(profs):
        row[f"rep_med_w{w}"] = med(p, "rep_int_q")
        row[f"ks_gue_med_w{w}"] = med(p, "ks_gue_q")
    return row


def build_tasks(rec, sid, cre, unit_ids, start_idx):
    nmo = chunks_for(rec, "natural_movie_one")
    bin_s = BIN_MS_MAT / 1000.0
    chunk_bins = [int(np.ceil((b - a) / bin_s)) for a, b in nmo]
    total_dur = float(sum(chunk_bins) * bin_s)
    offs = np.concatenate(([0.0], np.cumsum([nb * bin_s for nb in chunk_bins])))
    tasks = []
    for k, u in enumerate(unit_ids):
        sp_all = np.asarray(rec.spike_times.get(int(u), np.zeros(0)))
        parts = []
        for c, ((cs, _), nb) in enumerate(zip(nmo, chunk_bins)):
            cdur = nb * bin_s
            m = (sp_all >= cs) & (sp_all < cs + cdur)
            parts.append(sp_all[m] - cs + offs[c])
        sp_cat = np.sort(np.concatenate(parts)) if parts else np.zeros(0)
        tasks.append((sid, cre, int(u), sp_cat, total_dur, start_idx + k))
    return tasks, total_dur


def main():
    cohort = pd.read_parquet(ROOT_DIR + "/data/phase32b_results/per_cell_decomposition_merged.parquet")
    cohort = cohort[(cohort.p7_status == "OK") & (cohort.p7_n_windows_used == 5)]
    print(f"cohort (matches banked R^2): {len(cohort)} cells — NO trimming (B4)")

    rows, idx = [], 0
    for sid, cre in SESSIONS:
        t0 = time.time()
        rec = load_session(sid)
        uids = cohort.loc[cohort.session_id == sid, "unit_id"].astype(int).tolist()
        tasks, dur = build_tasks(rec, sid, cre, uids, idx)
        idx += len(tasks)
        print(f"  session {sid} ({cre}): {len(tasks)} cells, nmo_dur={dur:.1f}s — dispatching {N_WORKERS} workers")
        with Pool(N_WORKERS) as pool:
            rows.extend(pool.map(_cell, tasks, chunksize=1))
        print(f"    done in {time.time()-t0:.0f}s")
        del rec

    df = pd.DataFrame(rows)
    df.to_parquet(OUT / "per_cell_windowed_axes.parquet", index=False)
    print(f"\nbanked {len(df)} rows -> data/phase38_results/per_cell_windowed_axes.parquet")
    print(df.status.value_counts().to_string())
    if "n_q_common" in df:
        print(f"n_q_common: median={df.n_q_common.median():.0f}  min={df.n_q_common.min()}  max={df.n_q_common.max()}")


if __name__ == "__main__":
    main()
