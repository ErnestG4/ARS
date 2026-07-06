"""
run_phase20_calibrators.py — Phase 20 Tier 2.

Two calibrations:

  1. **MRAI timer artifact**: BGP routers batch updates and emit them at
     30-second boundaries (RFC 4271 default minRouteAdvertisementInterval).
     Synthesise a Poisson process at high rate, quantise timestamps to
     30-second boundaries with small jitter, run joint_q_profile.
     Expected: TL spike at q corresponding to 30s, BL elsewhere.

  2. **Quiescent-period BGP baseline + sub-window stability**: run
     joint_q_profile on the Sep 27 quiescent data per collector.
     Sub-window into 5-minute slices, compute classification per
     sub-window, measure agreement.

Outputs:
  data/phase20_calibrators.parquet
  plots/53_phase20_mrai_artifact.png
  plots/54_phase20_subwindow_stability.png
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from bgp_pipeline import COLLECTORS, WINDOWS, load_cell_parquet, \
    cell_parquet_exists
from dfa import dfa_hurst

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = Path(THIS_DIR) / 'data'
PLOTS = Path(THIS_DIR) / 'plots'
PARQUET_ROOT = DATA / 'phase20_facebook_2021'

# joint_q_profile parameters tuned for the BGP timescale.  The MRAI
# 30-second period falls at roughly q=30 if events are sampled at
# 1-second mean spacing (we unfold to unit-mean below).
Q_MAX = 60
MIN_EVENTS = 30
SUBWINDOW_SECONDS = 5 * 60   # 5-minute sub-windows


# ─── MRAI synthetic calibrator ───────────────────────────────────────────


def synthesise_mrai_signal(rate_per_sec: float = 10.0,
                            duration_sec: float = 3600.0,
                            mrai_period_sec: float = 30.0,
                            jitter_sec: float = 0.05,
                            seed: int = 0) -> np.ndarray:
    """Poisson process at rate_per_sec, quantised to nearest mrai
    boundary with Gaussian jitter."""
    rng = np.random.default_rng(seed)
    n = int(rate_per_sec * duration_sec)
    raw_times = np.cumsum(rng.exponential(1.0 / rate_per_sec, size=n))
    quantised = np.round(raw_times / mrai_period_sec) * mrai_period_sec
    jittered = quantised + jitter_sec * rng.standard_normal(n)
    return np.sort(jittered[(jittered >= 0) & (jittered <= duration_sec)])


def unfold_unit_mean(t: np.ndarray) -> np.ndarray:
    """Rescale event times so mean inter-event spacing is 1.0."""
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))


def primary_quadrant(events, q_max=Q_MAX, min_events=MIN_EVENTS):
    if events.size < min_events:
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    j = joint_q_profile(events, q_max=q_max, min_events_per_q=min_events)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    counts = well['quadrant'].value_counts()
    return (str(counts.idxmax()),
            float(well['rep_int_q'].median()),
            float(well['ks_gue_q'].median()),
            int(events.size))


# ─── Sub-window stability ────────────────────────────────────────────────


def subwindow_classifications(parquet_path: Path,
                                subwindow_sec: float = SUBWINDOW_SECONDS,
                                jpf_cap: int = 5000,
                                ) -> pd.DataFrame:
    """Sub-window the parsed events at the given resolution and
    classify each.  Returns DataFrame with columns:
      subwindow_start_us, n_events, primary, rep_med, ks_gue_med.

    `jpf_cap`: subsampling cap per sub-window for joint_q_profile
    runtime control (sub-windows with > jpf_cap events get strided
    subsampled).
    """
    df = load_cell_parquet(parquet_path, columns=['timestamp_us'])
    if len(df) == 0:
        return pd.DataFrame()
    ts = df['timestamp_us'].to_numpy()
    sub_us = int(subwindow_sec * 1_000_000)
    t0 = int(ts.min())
    t1 = int(ts.max())
    rows = []
    for s in range(t0, t1, sub_us):
        e = s + sub_us
        mask = (ts >= s) & (ts < e)
        ev_us = ts[mask]
        n_full = ev_us.size
        if n_full > jpf_cap:
            ev_us = ev_us[::max(1, n_full // jpf_cap)]
        ev = ev_us.astype(np.float64) / 1_000_000
        if ev.size < MIN_EVENTS:
            rows.append(dict(subwindow_start_us=s, n_events=int(n_full),
                              primary='underpowered',
                              rep_med=float('nan'),
                              ks_gue_med=float('nan')))
            continue
        ev_unit = unfold_unit_mean(ev)
        primary, rep, ks, n = primary_quadrant(ev_unit)
        rows.append(dict(subwindow_start_us=s, n_events=int(n_full),
                          primary=primary, rep_med=rep, ks_gue_med=ks))
    return pd.DataFrame(rows)


def stability_metric(class_series: pd.Series) -> dict:
    """Quantify stability of a sequence of primary-quadrant labels.
    Returns mode label, mode fraction, and unique-label count."""
    well = class_series[class_series != 'underpowered']
    if len(well) == 0:
        return dict(mode=None, mode_frac=0.0, n_unique=0,
                     n_underpowered=int((class_series == 'underpowered').sum()),
                     n_total=int(len(class_series)))
    counts = well.value_counts()
    return dict(
        mode=str(counts.idxmax()),
        mode_frac=float(counts.iloc[0] / counts.sum()),
        n_unique=int(counts.size),
        n_underpowered=int((class_series == 'underpowered').sum()),
        n_total=int(len(class_series)),
    )


# ─── Main ────────────────────────────────────────────────────────────────


def main():
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows = []

    # ─── MRAI calibrator ───────────────────────────────────────────────
    print("=" * 80)
    print("Tier 2.1 — MRAI synthetic calibrator (joint_q_profile + DFA)")
    print("=" * 80)
    for seed in range(3):
        ev = synthesise_mrai_signal(seed=seed)
        ev_unit = unfold_unit_mean(ev)
        primary, rep, ks, n = primary_quadrant(ev_unit)
        # Kitsak-style DFA on the IEI sequence — does the timer rhythm
        # alone reproduce long-range-correlated signatures?  Standard
        # expectation: H ≈ 0.5 (timer is short-range periodic, not LRC).
        iei = np.diff(ev)
        try:
            dfa_res = dfa_hurst(iei)
            hurst = dfa_res['hurst']
            r2 = dfa_res['r2']
        except Exception as e:
            hurst = float('nan'); r2 = float('nan')
        rows.append(dict(kind='mrai_synthetic', seed=seed,
                          primary=primary, rep_med=rep,
                          ks_gue_med=ks, n_events=n,
                          dfa_hurst=hurst, dfa_r2=r2))
        print(f"  seed={seed} n={n:,} primary={primary} "
              f"rep_med={rep:.3f} ks_gue_med={ks:.3f}  "
              f"H_DFA={hurst:.3f} (r²={r2:.3f})")

    # MRAI joint_q_profile detail for the plot
    ev = synthesise_mrai_signal(seed=0)
    ev_unit = unfold_unit_mean(ev)
    j_mrai = joint_q_profile(ev_unit, q_max=Q_MAX,
                              min_events_per_q=MIN_EVENTS)
    qd_mrai = joint_quadrant_diagnostic(j_mrai)

    # ─── Quiescent BGP baseline + Kitsak-consistency check ────────────
    print("\n" + "=" * 80)
    print("Tier 2.2 — Quiescent BGP per-collector baseline + Kitsak DFA")
    print("=" * 80)
    print("  Kitsak et al. 2015 reported H ≈ 0.7–0.9 for backbone BGP.")
    print("  Operational reference: BGP at rest is long-range correlated.")
    quiescent_jpf = {}
    # Performance caps: large quiescent parquets (37M rows) collapse to
    # ~84K unique-second event-times after np.diff>0 filtering, but
    # joint_q_profile at that scale is still slow (~20 min per cell).
    # Cap at 5000 events for joint_q_profile to stay within Phase 20 PoC
    # compute budget; full-scale results are obtainable as a follow-up.
    JPF_CAP = 5000
    DFA_CAP = 50_000
    for collector in COLLECTORS:
        p = PARQUET_ROOT / f"{collector}_quiescent.parquet"
        if not cell_parquet_exists(p):
            print(f"  {collector}: parquet not found ({p.name})")
            continue
        df = load_cell_parquet(p, columns=['timestamp_us'])
        if len(df) < MIN_EVENTS:
            print(f"  {collector}: only {len(df)} events; skipping")
            continue
        ev_us_full = df['timestamp_us'].to_numpy(dtype=np.int64)
        # joint_q_profile at JPF_CAP
        ev_us = ev_us_full
        if ev_us.size > JPF_CAP:
            ev_us = ev_us[::max(1, ev_us.size // JPF_CAP)]
        ev = ev_us.astype(np.float64) / 1_000_000
        ev_unit = unfold_unit_mean(ev)
        primary, rep, ks, n = primary_quadrant(ev_unit)
        # DFA on a separately-subsampled IEI series (more events than
        # JPF for tighter Hurst estimate).
        iei_us = np.diff(ev_us_full).astype(np.float64)
        if iei_us.size > DFA_CAP:
            iei_us = iei_us[:DFA_CAP]
        try:
            dfa_res = dfa_hurst(iei_us)
            hurst = dfa_res['hurst']
            r2 = dfa_res['r2']
        except Exception as e:
            hurst = float('nan'); r2 = float('nan')
        # Kitsak-consistency assessment
        kitsak_consistent = (0.6 <= hurst <= 1.0) if np.isfinite(hurst) \
                              else False
        rows.append(dict(kind='quiescent_baseline', seed=0,
                          collector=collector,
                          primary=primary, rep_med=rep,
                          ks_gue_med=ks, n_events=n,
                          dfa_hurst=hurst, dfa_r2=r2,
                          kitsak_consistent=bool(kitsak_consistent)))
        consistency_tag = "✓ Kitsak-consistent" if kitsak_consistent \
                          else "✗ NOT Kitsak-consistent"
        print(f"  {collector}: n={n:,}  primary={primary} "
              f"rep_med={rep:.3f}  H_DFA={hurst:.3f} (r²={r2:.3f})  "
              f"{consistency_tag}")
        # joint_q_profile DataFrame for plot inset (already subsampled)
        quiescent_jpf[collector] = joint_quadrant_diagnostic(
            joint_q_profile(ev_unit, q_max=Q_MAX,
                             min_events_per_q=MIN_EVENTS))

    # Cross-check the joint-plane vs DFA reading: report the
    # consistency / inconsistency map explicitly so Tier 3 cascade
    # results are interpreted with this baseline in hand.
    print("\n  Joint-plane × DFA consistency map (per Delta 1):")
    for r in rows:
        if r['kind'] != 'quiescent_baseline':
            continue
        h = r.get('dfa_hurst', float('nan'))
        if not np.isfinite(h):
            verdict = "DFA failed"
        elif r['primary'] == 'BL' and h > 0.6:
            verdict = ("joint-plane reads Poisson but DFA reads LRC — "
                        "framework operates at a different scale or "
                        "doesn't capture LRC")
        elif r['primary'] == 'BL' and h <= 0.6:
            verdict = "joint-plane reads Poisson, DFA agrees (no LRC)"
        elif r['primary'] in ('TR', 'BR_artifact', 'BR_novel') and h > 0.6:
            verdict = "joint-plane non-Poisson, DFA LRC — broadly consistent"
        else:
            verdict = (f"joint-plane={r['primary']}, H={h:.3f} — "
                        f"check interpretation")
        print(f"    {r['collector']:<22} {verdict}")

    # ─── Sub-window stability ────────────────────────────────────────
    print("\n" + "=" * 80)
    print("Tier 2.3 — Sub-window stability across 5-min slices")
    print("=" * 80)
    subwindow_per_collector = {}
    for collector in COLLECTORS:
        for window_name in ('quiescent', 'normal_load'):
            p = PARQUET_ROOT / f"{collector}_{window_name}.parquet"
            if not cell_parquet_exists(p):
                continue
            t0 = time.time()
            sw = subwindow_classifications(p, subwindow_sec=SUBWINDOW_SECONDS)
            if len(sw) == 0:
                print(f"  {collector}/{window_name}: no data")
                continue
            stats = stability_metric(sw['primary'])
            print(f"  {collector}/{window_name}: {len(sw)} sub-windows  "
                  f"mode={stats['mode']} mode_frac={stats['mode_frac']:.2f}  "
                  f"unique={stats['n_unique']}  "
                  f"underpowered={stats['n_underpowered']}  "
                  f"⏱{time.time() - t0:.0f}s")
            rows.append(dict(kind='subwindow_stability', seed=0,
                              collector=collector, window=window_name,
                              mode=stats['mode'],
                              mode_frac=stats['mode_frac'],
                              n_unique=stats['n_unique'],
                              n_underpowered=stats['n_underpowered'],
                              n_total=stats['n_total']))
            subwindow_per_collector[(collector, window_name)] = sw

    # Save
    out = DATA / 'phase20_calibrators.parquet'
    pd.DataFrame(rows).to_parquet(out, index=False)
    print(f"\n  → {out}")

    # ─── Plot 53 — MRAI artifact ─────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    ax = axes[0]
    ax.plot(qd_mrai['q'], qd_mrai['rf_amplitude_q'], 'k.-', label='|a_q|')
    ax.set_xlabel('q (Farey denominator)')
    ax.set_ylabel('|a_q| (Ramanujan-Fourier amplitude)')
    ax.set_title('MRAI synthetic — RF amplitude per q\n'
                  '(spike at q=30 corresponds to 30-s timer)')
    ax.axvline(30, color='red', ls='--', alpha=0.5,
                label='MRAI 30s')
    ax.legend(); ax.grid(alpha=0.3)
    ax = axes[1]
    ax.plot(qd_mrai['q'], qd_mrai['rep_int_q'], 'b.-')
    ax.set_xlabel('q')
    ax.set_ylabel('rep_int_q')
    ax.set_title('MRAI synthetic — repulsion integral per q')
    ax.axvline(30, color='red', ls='--', alpha=0.5)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS / '53_phase20_mrai_artifact.png', dpi=130)
    plt.close()
    print(f"  → {PLOTS}/53_phase20_mrai_artifact.png")

    # ─── Plot 54 — sub-window stability ──────────────────────────────
    if subwindow_per_collector:
        fig, axes = plt.subplots(len(COLLECTORS), 1,
                                  figsize=(12, 2.5 * len(COLLECTORS)),
                                  sharex=False)
        if len(COLLECTORS) == 1:
            axes = [axes]
        quad_colors = {'BL': '#2ca02c', 'TR': '#1f77b4',
                        'BR_artifact': '#d62728', 'BR_novel': '#9467bd',
                        'TL': '#ff7f0e',
                        'underpowered': '#cccccc',
                        'ambiguous': '#888888'}
        for i, collector in enumerate(COLLECTORS):
            ax = axes[i]
            for window_name, marker in [('quiescent', 'o'),
                                          ('normal_load', 's')]:
                key = (collector, window_name)
                if key not in subwindow_per_collector:
                    continue
                sw = subwindow_per_collector[key]
                t_hours = (sw['subwindow_start_us']
                            - sw['subwindow_start_us'].min()) \
                           / (3600 * 1_000_000)
                colors = [quad_colors.get(p, '#888') for p in sw['primary']]
                ax.scatter(t_hours, [window_name] * len(sw),
                            c=colors, marker=marker, s=15, alpha=0.7)
            ax.set_title(f'{collector}', fontsize=10)
            ax.set_xlabel('hours from window start')
            ax.set_yticks([0, 1])
            ax.set_yticklabels(['quiescent', 'normal_load'])
            ax.grid(alpha=0.3)
        from matplotlib.patches import Patch
        handles = [Patch(color=c, label=l) for l, c in quad_colors.items()]
        fig.legend(handles=handles, loc='upper right',
                    bbox_to_anchor=(1.0, 0.99), fontsize=8)
        plt.tight_layout()
        plt.savefig(PLOTS / '54_phase20_subwindow_stability.png', dpi=130,
                     bbox_inches='tight')
        plt.close()
        print(f"  → {PLOTS}/54_phase20_subwindow_stability.png")


if __name__ == '__main__':
    main()
