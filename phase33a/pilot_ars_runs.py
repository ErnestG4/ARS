import os
"""
phase33a/pilot_ars_runs.py — Phase 33a pilot (lean).

Apply NNS + RF engines to TOA event sequences from 5 representative
NANOGrav 15-yr pulsars under two extraction modes:

  (A) raw TOAs (subsampled to ≤3000 events for tractability) — asks
      whether the NNS engine reads pulsar physics or observation
      schedule on the published-TOA timeseries.
  (B) epoch-collapsed (one timestamp per distinct observation epoch,
      TOAs within 1 hr collapsed to first) — asks the same question
      at observation-epoch granularity.

Lean parameters: q_max=30 (structural assessment, not §7.ter.13-
validated precision), 1 rate-matched uniform-Poisson surrogate seed.
At this q_max threshold, the §7.ter.13 1.5× absolute threshold is
not valid; we use matched real-vs-surrogate z-scores as discriminant
(per the q_max=30 caveat in EPISTEMIC_STATE.md).

Outputs: data/phase33a_results/pilot_classifications.parquet
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(os.path.expandvars(os.path.expanduser("$HOME/fmexplorer/criticality_tool")))
DATA = ROOT / 'data' / 'phase33a_results'

sys.path.insert(0, str(ROOT))

from arithmetic_toolkit import joint_q_profile, padic_amplitude_v4

PULSARS = ['B1855+09', 'J0030+0451', 'J0613-0200', 'J1909-3744',
           'J0740+6620']

PRIMES = (2, 3, 5, 7, 11, 13)
Q_MAX = 30
N_SEEDS = 2
MAX_RAW_EVENTS = 3000  # subsample cap for raw-TOA mode


def epoch_collapse(toas: np.ndarray, eps_seconds: float = 3600.0
                   ) -> np.ndarray:
    toas_sorted = np.sort(toas)
    iei = np.diff(toas_sorted)
    is_first = np.concatenate([[True], iei > eps_seconds])
    return toas_sorted[is_first]


def run_one(pulsar: str, events: np.ndarray, mode: str) -> dict:
    events = np.sort(events.astype(float))
    events = events - events[0]
    n = len(events)
    dur = float(events[-1])
    if dur <= 0 or n < 30:
        return None

    print(f"    [{mode}] computing NNS+RF on n={n}, dur={dur/86400/365.25:.1f}yr…",
          flush=True)
    nns = joint_q_profile(events, q_max=Q_MAX)
    ks_gue_med = float(np.median(nns['ks_gue_q']))
    rep_med = float(np.median(nns['rep_int_q']))
    rf = padic_amplitude_v4(events, q_max=Q_MAX)
    real_p = {int(p): float(rf['per_prime'][p]['normalised_per_q'])
              for p in PRIMES}
    dom_p = int(rf['dominant_prime_per_q'])

    print(f"    [{mode}] computing surrogates…", flush=True)
    sur_real_p = {int(p): [] for p in PRIMES}
    sur_ks, sur_rep = [], []
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(20260511 + seed)
        sur = np.sort(rng.uniform(0, dur, size=n))
        sur_nns = joint_q_profile(sur, q_max=Q_MAX)
        sur_rf = padic_amplitude_v4(sur, q_max=Q_MAX)
        sur_ks.append(float(np.median(sur_nns['ks_gue_q'])))
        sur_rep.append(float(np.median(sur_nns['rep_int_q'])))
        for p in PRIMES:
            sur_real_p[int(p)].append(
                float(sur_rf['per_prime'][p]['normalised_per_q']))

    sur_ks_a = np.asarray(sur_ks)
    sur_rep_a = np.asarray(sur_rep)
    z_ks = (ks_gue_med - sur_ks_a.mean()) / max(sur_ks_a.std(), 1e-6)
    z_rep = (rep_med - sur_rep_a.mean()) / max(sur_rep_a.std(), 1e-6)

    row = dict(pulsar=pulsar, mode=mode, n_events=int(n),
               duration_sec=dur, duration_yr=dur / (365.25 * 86400),
               ks_gue_med=ks_gue_med, rep_med=rep_med,
               ks_gue_med_z=float(z_ks), rep_med_z=float(z_rep),
               sur_ks_mean=float(sur_ks_a.mean()),
               sur_rep_mean=float(sur_rep_a.mean()),
               dominant_prime=dom_p)
    for p in PRIMES:
        s = np.asarray(sur_real_p[int(p)])
        z = (real_p[int(p)] - s.mean()) / max(s.std(), 1e-6)
        row[f'real_p{p}'] = real_p[int(p)]
        row[f'sur_mean_p{p}'] = float(s.mean())
        row[f'z_p{p}'] = float(z)
    return row


def main():
    rows = []
    for pulsar in PULSARS:
        print(f"\n=== {pulsar} ===", flush=True)
        df = pd.read_feather(DATA / f'{pulsar}.feather')
        toas_all = df['toas'].values

        # Mode A: raw TOAs, subsampled if huge
        if len(toas_all) > MAX_RAW_EVENTS:
            rng = np.random.default_rng(0)
            idx = np.sort(rng.choice(len(toas_all), size=MAX_RAW_EVENTS,
                                     replace=False))
            raw = toas_all[idx]
            note = f" (subsampled from {len(toas_all)})"
        else:
            raw = toas_all
            note = ""
        print(f"  Raw TOAs: n={len(raw)}{note}", flush=True)
        r = run_one(pulsar, raw, 'raw_toas')
        if r is not None:
            r['raw_full_n'] = int(len(toas_all))
            rows.append(r)
            print(f"    NNS: ks_gue_med={r['ks_gue_med']:.3f} z={r['ks_gue_med_z']:+.2f}  "
                  f"rep_med={r['rep_med']:.3f} z={r['rep_med_z']:+.2f}", flush=True)
            print(f"    RF dom_p={r['dominant_prime']}  "
                  + "  ".join(f"p{p}={r[f'real_p{p}']:.2f}(z{r[f'z_p{p}']:+.1f})"
                              for p in PRIMES),
                  flush=True)

        # Mode B: epoch-collapsed
        epoch = epoch_collapse(toas_all)
        print(f"  Epoch-collapsed: n={len(epoch)}", flush=True)
        r = run_one(pulsar, epoch, 'epoch_collapsed')
        if r is not None:
            r['raw_full_n'] = int(len(toas_all))
            rows.append(r)
            print(f"    NNS: ks_gue_med={r['ks_gue_med']:.3f} z={r['ks_gue_med_z']:+.2f}  "
                  f"rep_med={r['rep_med']:.3f} z={r['rep_med_z']:+.2f}", flush=True)
            print(f"    RF dom_p={r['dominant_prime']}  "
                  + "  ".join(f"p{p}={r[f'real_p{p}']:.2f}(z{r[f'z_p{p}']:+.1f})"
                              for p in PRIMES),
                  flush=True)

    out = pd.DataFrame(rows)
    out.to_parquet(DATA / 'pilot_classifications.parquet', index=False)
    print(f"\nWrote {DATA}/pilot_classifications.parquet "
          f"({len(out)} rows)", flush=True)


if __name__ == '__main__':
    main()
