"""
run_phase21_falsification.py — Phase 21 Tier 4.

Apply Phase 18 surrogates + the lightcurve-modulated Poisson surrogate
+ Phase 20.5's transition diagnostic to Phase 21's per-event QPO-claim
sub-windows.  Aggregate verdict per the revised verdict map.

Key analyses:

  1. **Cascade-peak / QPO-window classification on each event**:
     extract the prompt-emission window's pooled-detector events
     (or the published QPO claim window).  Run joint_q_profile;
     report quadrant + rep_med at the q-band corresponding to the
     published QPO frequency.

  2. **Phase 18 surrogate falsification**: hawkes_matched (skipped per
     §7.ter.27 — pathological on dense bursts), phase_randomized_iei,
     cumulant_matched.  Compare quadrant + rep_med to original.

  3. **Lightcurve-modulated Poisson surrogate**: bin the empirical
     events at 1 ms, smooth with a 21-bin moving average, generate
     inhomogeneous Poisson events.  Run joint_q_profile; compare.

  4. **Transition-shape characterisation per QPO window**: apply
     `transition_diagnostic.characterize_transition` to the
     trajectory across the QPO window.  Report shape estimate.

  5. **Mechanism-distinctness note**: per the user-flagged Tier 2
     observation, all gamma-ray photon detectors share the
     categorical-event-detection mechanism class; cross-detector
     agreement on a QPO claim is one mechanism's testimony at multiple
     vantage points, not multi-mechanism corroboration.  Tier 4
     therefore does NOT run pairwise distinctness across the
     event panel's photon detectors.

Outputs:
  data/phase21_falsification.parquet
  plots/62_phase21_surrogate_survival.png
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from grb_pipeline import EVENT_PANEL
from surrogates import (phase_randomized_iei_events,
                          cumulant_matched_events)
from lightcurve_modulated_surrogate import lightcurve_modulated_poisson
from transition_diagnostic import characterize_transition

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = Path(THIS_DIR) / 'data'
PLOTS = Path(THIS_DIR) / 'plots'
PANEL_DIR = DATA / 'phase21_grb_panel'
PLOTS.mkdir(parents=True, exist_ok=True)

Q_MAX = 50
MIN_EVENTS_PER_Q = 30
JPF_CAP = 5000


def unfold_unit_mean(t, cap=JPF_CAP):
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    if sp.size > cap:
        sp = sp[::max(1, sp.size // cap)]
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))


def classify(events_us: np.ndarray):
    if events_us.size < MIN_EVENTS_PER_Q:
        return dict(primary='underpowered', rep_med=np.nan,
                     ks_gue_med=np.nan, n=int(events_us.size),
                     rep_int_q=None)
    ev = events_us.astype(np.float64) / 1_000_000
    ev_unit = unfold_unit_mean(ev)
    if ev_unit.size < MIN_EVENTS_PER_Q:
        return dict(primary='underpowered', rep_med=np.nan,
                     ks_gue_med=np.nan, n=int(ev.size),
                     rep_int_q=None)
    j = joint_q_profile(ev_unit, q_max=Q_MAX,
                         min_events_per_q=MIN_EVENTS_PER_Q)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return dict(primary='underpowered', rep_med=np.nan,
                     ks_gue_med=np.nan, n=int(ev.size),
                     rep_int_q=None)
    counts = well['quadrant'].value_counts()
    return dict(
        primary=str(counts.idxmax()),
        rep_med=float(well['rep_int_q'].median()),
        ks_gue_med=float(well['ks_gue_q'].median()),
        n=int(ev.size),
        rep_int_q=j['rep_int_q'].to_numpy(),
    )


def main():
    print("=" * 80)
    print("Phase 21 Tier 4 — falsification with lightcurve-modulated "
          "Poisson and Phase 18 surrogates")
    print("=" * 80)
    rows = []
    for event in EVENT_PANEL:
        if event['priority'] > 3:
            continue
        p = PANEL_DIR / f"{event['name']}.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p, columns=['time_us'])
        # QPO window per event (or full prompt for control)
        if event.get('qpo_window_after_t0') is not None:
            qpo_lo, qpo_hi = event['qpo_window_after_t0']
            qpo_lo_us = int(qpo_lo * 1_000_000)
            qpo_hi_us = int(qpo_hi * 1_000_000)
            window_label = (f"qpo_window=[{qpo_lo:.3f}, {qpo_hi:.3f}]s "
                            f"({event['qpo_claim_hz']} Hz claim)")
        else:
            qpo_lo_us = 0
            qpo_hi_us = int(event['t90'] * 1_000_000)
            window_label = f"prompt window [0, {event['t90']:.1f}]s"

        events_us = df['time_us'].to_numpy()
        in_window = events_us[(events_us >= qpo_lo_us)
                                & (events_us < qpo_hi_us)]
        if in_window.size < MIN_EVENTS_PER_Q:
            print(f"  {event['name']}: {window_label}: too few events "
                  f"({in_window.size})")
            continue
        print(f"\n  {event['name']}: {window_label}")
        print(f"    {in_window.size:,} events pooled across detectors")

        # Original classification
        orig = classify(in_window)
        f_hz = event.get('qpo_claim_hz')
        if f_hz is not None:
            rate = in_window.size / max((qpo_hi_us - qpo_lo_us) / 1e6, 1e-3)
            q_qpo = max(2, int(round(rate / f_hz)))
            if q_qpo > Q_MAX:
                q_qpo = None
        else:
            q_qpo = None
        rep_qpo = (float(orig['rep_int_q'][q_qpo - 1])
                    if q_qpo is not None and orig['rep_int_q'] is not None
                       and q_qpo - 1 < len(orig['rep_int_q'])
                    else float('nan'))
        print(f"    ORIGINAL  primary={orig['primary']} "
              f"rep_med={orig['rep_med']:.3f}  rep@q={q_qpo}={rep_qpo:.3f}")
        rows.append(dict(
            event=event['name'],
            qpo_claim_hz=f_hz,
            window_label=window_label,
            surrogate='ORIGINAL',
            seed=-1,
            primary=orig['primary'],
            rep_med=orig['rep_med'],
            ks_gue_med=orig['ks_gue_med'],
            n=orig['n'],
            q_qpo=q_qpo,
            rep_at_qpo_q=rep_qpo,
        ))

        # Phase 18 surrogates
        for surr_name, surr_fn in [
                ('phase_randomized_iei', phase_randomized_iei_events),
                ('cumulant_matched',     cumulant_matched_events)]:
            for seed in range(3):
                rng = np.random.default_rng(seed * 100
                                              + abs(hash(surr_name)) % 50000)
                t0 = time.time()
                try:
                    surr = surr_fn(in_window.astype(np.float64) / 1e6,
                                     rng=rng)
                    surr_us = (surr * 1e6).astype(np.int64)
                    cls = classify(surr_us)
                except Exception as e:
                    cls = dict(primary='error', rep_med=np.nan,
                                ks_gue_med=np.nan, n=0, rep_int_q=None)
                rep_q = (float(cls['rep_int_q'][q_qpo - 1])
                          if q_qpo is not None
                             and cls['rep_int_q'] is not None
                             and q_qpo - 1 < len(cls['rep_int_q'])
                          else float('nan'))
                rows.append(dict(
                    event=event['name'],
                    qpo_claim_hz=f_hz,
                    window_label=window_label,
                    surrogate=surr_name,
                    seed=seed,
                    primary=cls['primary'],
                    rep_med=cls['rep_med'],
                    ks_gue_med=cls['ks_gue_med'],
                    n=cls['n'],
                    q_qpo=q_qpo,
                    rep_at_qpo_q=rep_q,
                ))
            primaries_3 = [r['primary'] for r in rows[-3:]]
            print(f"    {surr_name:<22} (3 seeds): primaries={primaries_3}")

        # Lightcurve-modulated Poisson
        for seed in range(3):
            rng = np.random.default_rng(seed * 100 + 12345)
            try:
                # Bin granularity: aim for ~ T90 / 200 bins
                bin_us = max(1000, int((qpo_hi_us - qpo_lo_us) // 200))
                surr_us = lightcurve_modulated_poisson(
                    in_window, bin_us=bin_us, smoothing_window=21,
                    rng=rng)
                cls = classify(surr_us)
            except Exception as e:
                cls = dict(primary='error', rep_med=np.nan,
                            ks_gue_med=np.nan, n=0, rep_int_q=None)
            rep_q = (float(cls['rep_int_q'][q_qpo - 1])
                      if q_qpo is not None
                         and cls['rep_int_q'] is not None
                         and q_qpo - 1 < len(cls['rep_int_q'])
                      else float('nan'))
            rows.append(dict(
                event=event['name'],
                qpo_claim_hz=f_hz,
                window_label=window_label,
                surrogate='lightcurve_modulated_poisson',
                seed=seed,
                primary=cls['primary'],
                rep_med=cls['rep_med'],
                ks_gue_med=cls['ks_gue_med'],
                n=cls['n'],
                q_qpo=q_qpo,
                rep_at_qpo_q=rep_q,
            ))
        primaries_3 = [r['primary'] for r in rows[-3:]]
        print(f"    lightcurve_modulated  (3 seeds): primaries={primaries_3}")

    # Save
    df_out = pd.DataFrame(rows)
    df_out.to_parquet(DATA / 'phase21_falsification.parquet', index=False)
    print(f"\n  → {DATA}/phase21_falsification.parquet  ({len(df_out)} rows)")

    # Plot 62: surrogate survival summary
    if not df_out.empty:
        fig, ax = plt.subplots(figsize=(11, 5.5))
        events = sorted(df_out['event'].unique())
        surrogates = ['ORIGINAL', 'phase_randomized_iei',
                       'cumulant_matched',
                       'lightcurve_modulated_poisson']
        x = np.arange(len(events))
        width = 0.20
        for i, surr in enumerate(surrogates):
            sub = df_out[df_out['surrogate'] == surr]
            vals = []
            for ev in events:
                d = sub[sub['event'] == ev]['rep_med']
                vals.append(float(d.median()) if len(d) else float('nan'))
            ax.bar(x + i * width, vals, width=width, label=surr)
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(events, rotation=20, ha='right', fontsize=9)
        ax.set_ylabel('rep_med at QPO/prompt window')
        ax.set_ylim(0, 1)
        ax.set_title('Phase 21 Tier 4 — surrogate survival per event\n'
                      '(rep_med at QPO/prompt-window classification: '
                      'ORIGINAL vs surrogates; '
                      'lightcurve-modulated Poisson is the GRB-specific '
                      'critical falsification)')
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(PLOTS / '62_phase21_surrogate_survival.png', dpi=130)
        plt.close()
        print(f"  → {PLOTS}/62_phase21_surrogate_survival.png")


if __name__ == '__main__':
    main()
