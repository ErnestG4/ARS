"""
run_phase18_surrogate_calibration.py — Phase 18 Tier 2 calibration.

For each (known-artifact signal) × (surrogate) cell:

  1. Build the raw signal and the extractor pipeline that produces events.
  2. Compute the original joint_q_profile classification.
  3. Apply the relevant surrogate (continuous-domain on raw, event-domain
     on events).
  4. Run the SAME extractor (where applicable) on the surrogate output.
  5. Compute the surrogate joint_q_profile classification.
  6. Record whether the surrogate produces the same primary quadrant as
     the original (CATCH) or a different one (NO CATCH).

  A surrogate that catches an artifact reproduces the artifact's
  classification when fed structurally similar noise that preserves only
  the property the surrogate is designed to preserve.  This validates that
  the surrogate has falsification power for that artifact class.

Output:
  data/phase18_surrogate_calibration.parquet
  plots/50_phase18_surrogate_catch_matrix.png
"""
from __future__ import annotations
import os, sys, time
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from extractors import (
    extract_find_peaks_prominence,
    extract_threshold_crossing,
    extract_modular_bin_events,
    extract_direct_events,
)
from surrogates import (
    phase_randomized,
    cumulant_matched_continuous,
    phase_randomized_events,
    hawkes_matched_events,
    cumulant_matched_events,
    _simulate_hawkes,
)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")

N_SAMPLES = 8192          # continuous-signal length
N_EVENTS_TARGET = 1500    # for event-only signals
Q_MAX = 50
MIN_EVENTS = 30
N_SEEDS = 3


# ─── Signal generators (raw + extractor) ─────────────────────────────────


def _ar1(rng, n, rho=0.85):
    e = rng.standard_normal(n)
    x = np.zeros(n)
    x[0] = e[0]
    s = np.sqrt(1 - rho ** 2)
    for i in range(1, n):
        x[i] = rho * x[i - 1] + s * e[i]
    return x


def _one_over_f(rng, n, alpha=1.0):
    """1/f^α noise via spectral shaping of Gaussian noise."""
    freqs = np.fft.rfftfreq(n, d=1.0)
    spectrum = np.zeros_like(freqs)
    spectrum[1:] = 1.0 / (freqs[1:] ** (alpha / 2.0))
    spectrum[0] = 0.0
    Z = (rng.standard_normal(freqs.size) +
         1j * rng.standard_normal(freqs.size))
    Z[0] = 0.0
    Y = Z * spectrum
    if (n % 2) == 0:
        Y[-1] = Y[-1].real
    return np.fft.irfft(Y, n=n)


def gen_sinusoid_white(seed, n=N_SAMPLES, freq=37, snr=2.0):
    rng = np.random.default_rng(seed)
    t = np.arange(n) / n
    sig = snr * np.sin(2 * np.pi * freq * t * (n / 100)) \
        + rng.standard_normal(n)
    return sig.astype(np.float64)


def gen_ar1(seed, n=N_SAMPLES):
    rng = np.random.default_rng(seed)
    return _ar1(rng, n, rho=0.9)


def gen_iid_exponential(seed, n=N_SAMPLES):
    rng = np.random.default_rng(seed)
    return rng.exponential(1.0, size=n).astype(np.float64)


def gen_one_over_f(seed, n=N_SAMPLES):
    rng = np.random.default_rng(seed)
    return _one_over_f(rng, n, alpha=1.0)


def gen_integer_spaced(seed, n=N_EVENTS_TARGET):
    """Deterministic integer-spaced events (seed unused)."""
    return np.arange(1, n + 1, dtype=np.float64)


def gen_hawkes_pure(seed, T=4000.0):
    """Pure Hawkes process at moderate self-excitation — clustering is
    the dominant structural feature.  Original classification expected:
    BL (super-Poisson clustering, high mass<0.3).  hawkes_matched is the
    surrogate designed to reproduce this clustering, so it should catch.
    """
    rng = np.random.default_rng(seed)
    t_full = _simulate_hawkes(0.3, 0.8, 1.3, T, rng)
    if t_full.size < 100:
        # Fall back to Poisson at the same rate; catch logic still valid.
        return np.cumsum(rng.exponential(1.0, size=300))
    return t_full


# ─── Extractor wrappers ─────────────────────────────────────────────────


def find_peaks_on_continuous(sig, prominence=0.3):
    """find_peaks on a real-valued continuous signal — returns sample
    indices as float event-times."""
    from scipy.signal import find_peaks
    if sig.size < 5:
        return np.zeros(0)
    prom_thr = max(prominence * float(sig.std()), 1e-9)
    peaks, _ = find_peaks(sig, prominence=prom_thr)
    return peaks.astype(np.float64)


def threshold_on_continuous(sig, k=1.0):
    """Up-crossings of mean + k·σ on a real-valued continuous signal."""
    if sig.size < 2:
        return np.zeros(0)
    thr = sig.mean() + k * sig.std()
    above = sig > thr
    if above.sum() < 2:
        return np.zeros(0)
    transitions = np.diff(above.astype(np.int8))
    return (np.where(transitions == 1)[0] + 1).astype(np.float64)


# ─── Signal panel ─────────────────────────────────────────────────────────
#
# Each entry: (name, kind, raw_gen, extractor, extractor_kwargs).
#   kind: 'continuous' (raw is sampled signal; extractor is continuous-input
#                       function) or 'events' (raw is event sequence;
#                       extractor is point-process function)


SIGNAL_PANEL = [
    dict(name='find_peaks_sinusoid_white',
         kind='continuous',
         raw_gen=gen_sinusoid_white,
         extractor=find_peaks_on_continuous,
         ekw={'prominence': 0.3}),
    dict(name='find_peaks_ar1',
         kind='continuous',
         raw_gen=gen_ar1,
         extractor=find_peaks_on_continuous,
         ekw={'prominence': 0.3}),
    dict(name='threshold_iid_exponential',
         kind='continuous',
         raw_gen=gen_iid_exponential,
         extractor=threshold_on_continuous,
         ekw={'k': 1.0}),
    dict(name='threshold_one_over_f',
         kind='continuous',
         raw_gen=gen_one_over_f,
         extractor=threshold_on_continuous,
         ekw={'k': 1.0}),
    dict(name='modular_bin_integer_spaced',
         kind='events',
         raw_gen=gen_integer_spaced,
         extractor=lambda ev, **kw: extract_modular_bin_events(ev),
         ekw={}),
    dict(name='hawkes_pure',
         kind='events',
         raw_gen=gen_hawkes_pure,
         extractor=lambda ev, **kw: extract_direct_events(ev),
         ekw={}),
]


SURROGATE_NAMES = ['phase_randomized', 'hawkes_matched', 'cumulant_matched']


# ─── Surrogate dispatchers (raw + events) ─────────────────────────────────


def apply_surrogate_continuous(sig, name, rng, extractor, ekw):
    """Run a surrogate on a continuous input, then re-extract events."""
    if name == 'phase_randomized':
        sig_s = phase_randomized(sig, rng=rng)
        return extractor(sig_s, **ekw)
    if name == 'cumulant_matched':
        sig_s = cumulant_matched_continuous(sig, rng=rng)
        return extractor(sig_s, **ekw)
    if name == 'hawkes_matched':
        # No continuous Hawkes surrogate: fit Hawkes to events extracted
        # from sig, regenerate, return.
        events = extractor(sig, **ekw)
        if events.size < 20:
            return np.zeros(0)
        return hawkes_matched_events(events, rng=rng)
    raise ValueError(name)


def apply_surrogate_events(events, name, rng):
    """Run a surrogate on an event input (kind='events' panel rows)."""
    if name == 'phase_randomized':
        return phase_randomized_events(events, rng=rng)
    if name == 'hawkes_matched':
        return hawkes_matched_events(events, rng=rng)
    if name == 'cumulant_matched':
        return cumulant_matched_events(events, rng=rng)
    raise ValueError(name)


# ─── Classification ───────────────────────────────────────────────────────


def primary_quadrant(events):
    """Return (quadrant, rep_med, ks_gue_med, n_events) of the well-powered
    rows of joint_q_profile + diagnostic.  Uses the most common quadrant
    among well-powered q-bands."""
    if events.size < MIN_EVENTS:
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    j = joint_q_profile(events, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    counts = well['quadrant'].value_counts()
    primary = str(counts.idxmax())
    rep_med = float(well['rep_int_q'].median())
    ks_med = float(well['ks_gue_q'].median())
    return primary, rep_med, ks_med, int(events.size)


# ─── Main calibration loop ────────────────────────────────────────────────


def main():
    rows = []
    t_start = time.time()
    print("=" * 100)
    print(f"Phase 18 Tier 2 calibration — {len(SIGNAL_PANEL)} signals × "
          f"{len(SURROGATE_NAMES)} surrogates × {N_SEEDS} seeds")
    print("=" * 100)

    for sig_def in SIGNAL_PANEL:
        name = sig_def['name']
        kind = sig_def['kind']
        gen = sig_def['raw_gen']
        extractor = sig_def['extractor']
        ekw = sig_def['ekw']

        for seed in range(N_SEEDS):
            t0 = time.time()
            try:
                raw = gen(seed)
            except Exception as e:
                print(f"  {name} seed={seed}: gen failed: {e}")
                continue

            if kind == 'continuous':
                orig_events = extractor(raw, **ekw)
            else:
                orig_events = extractor(raw)

            orig_q, orig_rep, orig_ks, orig_n = primary_quadrant(orig_events)
            print(f"  {name:<30} seed={seed}  ORIGINAL  "
                  f"n={orig_n:>5,}  rep_med={orig_rep:.3f}  "
                  f"ks_gue_med={orig_ks:.3f}  → {orig_q}")

            for surr in SURROGATE_NAMES:
                rng = np.random.default_rng(seed * 100 + hash(surr) % 50000)
                try:
                    if kind == 'continuous':
                        surr_events = apply_surrogate_continuous(
                            raw, surr, rng, extractor, ekw)
                    else:
                        # Spec: re-extract events from the surrogate using
                        # the same extractor used on the original input.
                        surr_pre = apply_surrogate_events(
                            raw, surr, rng)
                        surr_events = extractor(surr_pre)
                except Exception as e:
                    print(f"      {surr:<20}: surrogate FAILED: {e}")
                    rows.append(dict(
                        signal=name, kind=kind, seed=seed,
                        surrogate=surr,
                        orig_quadrant=orig_q, orig_rep=orig_rep,
                        orig_ks_gue=orig_ks, orig_n=orig_n,
                        surr_quadrant='error', surr_rep=float('nan'),
                        surr_ks_gue=float('nan'), surr_n=0,
                        catch=False))
                    continue

                surr_q, surr_rep, surr_ks, surr_n = primary_quadrant(surr_events)
                # CATCH = surrogate reproduces the same primary quadrant.
                # underpowered surrogates are not evaluated as catches.
                if surr_q == 'underpowered' or orig_q == 'underpowered':
                    catch = False
                else:
                    catch = (surr_q == orig_q)

                rows.append(dict(
                    signal=name, kind=kind, seed=seed,
                    surrogate=surr,
                    orig_quadrant=orig_q, orig_rep=orig_rep,
                    orig_ks_gue=orig_ks, orig_n=orig_n,
                    surr_quadrant=surr_q, surr_rep=surr_rep,
                    surr_ks_gue=surr_ks, surr_n=surr_n,
                    catch=bool(catch)))
                tag = 'CATCH' if catch else '----'
                print(f"      {surr:<20}  surr n={surr_n:>5,}  "
                      f"rep={surr_rep:.3f}  ks={surr_ks:.3f}  "
                      f"→ {surr_q:<12} {tag}")
            print(f"      ⏱ {time.time() - t0:.1f}s")

    df = pd.DataFrame(rows)
    out_path = os.path.join(DATA, 'phase18_surrogate_calibration.parquet')
    df.to_parquet(out_path)
    print(f"\n  → {out_path}  ({len(df)} rows)")

    # ── Aggregate: per (signal, surrogate) catch fraction ──────────────────
    agg = (df.groupby(['signal', 'surrogate'])
             .agg(catches=('catch', 'sum'),
                  total=('catch', 'count'),
                  orig_quadrant=('orig_quadrant',
                                  lambda x: x.value_counts().index[0]),
                  surr_q_mode=('surr_quadrant',
                                lambda x: x.value_counts().index[0]))
             .reset_index())
    agg['catch_rate'] = agg['catches'] / agg['total']
    print()
    print("=" * 100)
    print("Catch matrix (signal × surrogate):  catch fraction across seeds")
    print("=" * 100)
    pivot = agg.pivot(index='signal', columns='surrogate',
                       values='catch_rate')
    print(pivot.to_string(float_format=lambda v: f"{v:.2f}"))

    # ── Plot ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    pivot_arr = pivot.reindex(
        index=[s['name'] for s in SIGNAL_PANEL],
        columns=SURROGATE_NAMES,
    )
    im = ax.imshow(pivot_arr.values, aspect='auto', cmap='RdYlGn',
                    vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(SURROGATE_NAMES)))
    ax.set_xticklabels(SURROGATE_NAMES, rotation=20, ha='right')
    ax.set_yticks(np.arange(len(SIGNAL_PANEL)))
    ax.set_yticklabels([s['name'] for s in SIGNAL_PANEL])
    for i in range(pivot_arr.shape[0]):
        for j in range(pivot_arr.shape[1]):
            v = pivot_arr.values[i, j]
            txt = f"{v:.2f}" if not np.isnan(v) else '—'
            ax.text(j, i, txt, ha='center', va='center',
                     color='black' if 0.3 < v < 0.7 else 'white')
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('catch rate (fraction of seeds catching)')
    ax.set_title('Phase 18 Tier 2 — Surrogate catch matrix\n'
                  '(catch = surrogate reproduces original primary quadrant)')
    plt.tight_layout()
    out_png = os.path.join(PLOTS, '50_phase18_surrogate_catch_matrix.png')
    plt.savefig(out_png, dpi=130)
    plt.close()
    print(f"\n  → {out_png}")
    print(f"\n  total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
