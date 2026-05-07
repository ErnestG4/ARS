"""
Fungal mycelium electrical-spike NNS via the ARS analytical passage-time
metric.

Data: 18 CSVs from Adamatzky-style fungal recordings (Pleurotus ostreatus
and grain-substrate fruiting bodies), 8 differential channels each, 1 Hz
sampling, 60-93 h duration.

Pipeline:
  1. Per channel, rolling-median baseline subtraction (1-h window).
  2. Threshold spike detection at 3σ / 4σ / 6σ above detrended baseline,
     min spike width 10 s, min ISI 120 s.
  3. Pick the threshold that gives 20–150 spikes per channel.
  4. Run analytical-passage-time NNS through Farey PLL bank (q_max=8) on
     each (file, channel) spike sequence.
  5. Pool all spike events across files and channels for the headline
     classification.
  6. ISI histogram across all channels — look for two-population structure
     (Adamatzky reports peaks near 2.6 min and 14 min).

Output:
  data/fungal_results.json
  plots/29_fungal_nns.png
  plots/30_fungal_isi.png
"""
import os, sys, json, glob, time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from pll_bank import farey_rationals
from universality import nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(THIS_DIR, "data")
PLOT_DIR = os.path.join(THIS_DIR, "plots")
FUNGI_ROOT = os.path.join(THIS_DIR, "fungi", "Experiments Electrical Recordings")

THRESHOLDS = [3.0, 4.0, 6.0]
TARGET_LO, TARGET_HI = 20, 150
WINDOW_SEC = 3600
MIN_ISI_SEC = 120
MIN_SPIKE_WIDTH_SEC = 10
Q_MAX = 8


# ─── CSV loading ──────────────────────────────────────────────────────────────

def hhmmss_to_sec(s):
    s = s.strip().strip('"')
    h, m, sec = s.split(':')
    return int(h) * 3600 + int(m) * 60 + int(sec)


def load_fungal_csv(path):
    # First column is HH:MM:SS index strings; remaining columns are float voltages.
    df = pd.read_csv(path, low_memory=False)
    # Original index column may be unnamed ('') or labelled — take col 0.
    idx_col = df.columns[0]
    idx_strs = df[idx_col].astype(str).str.strip().str.strip('"')
    df = df.drop(columns=[idx_col])
    # Cast voltage columns to float32 to halve memory.
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce').astype(np.float32)
    df.columns = [c.strip().strip('"') for c in df.columns]
    df.index = idx_strs.map(hhmmss_to_sec).to_numpy()
    return df


# ─── Spike detection ──────────────────────────────────────────────────────────

def detect_spikes(time_sec, voltage, threshold_std, window_sec=WINDOW_SEC,
                  min_isi_sec=MIN_ISI_SEC, min_spike_width_sec=MIN_SPIKE_WIDTH_SEC):
    """Threshold-cross spike detection on a rolling-median-detrended channel."""
    series = pd.Series(voltage, index=time_sec)
    baseline = series.rolling(window=window_sec, center=True, min_periods=60).median()
    detrended = (series - baseline).to_numpy()
    detrended = np.nan_to_num(detrended, nan=0.0)
    std = float(np.nanstd(detrended))
    if std <= 0:
        return np.zeros(0)
    threshold = threshold_std * std

    above = detrended > threshold
    if above.sum() < 2:
        return np.zeros(0)
    a = above.astype(np.int8)
    starts = np.where(np.diff(a) == 1)[0] + 1
    ends   = np.where(np.diff(a) == -1)[0] + 1
    if starts.size == 0 or ends.size == 0:
        return np.zeros(0)
    if ends[0] < starts[0]:
        ends = ends[1:]
    n = min(starts.size, ends.size)
    starts, ends = starts[:n], ends[:n]

    t_arr = np.asarray(time_sec)
    v_arr = np.asarray(voltage)
    out, last = [], -np.inf
    for s, e in zip(starts, ends):
        if e <= s: continue
        width = t_arr[e - 1] - t_arr[s]
        if width < min_spike_width_sec: continue
        peak = t_arr[s + int(np.argmax(v_arr[s:e]))]
        if peak - last > min_isi_sec:
            out.append(peak)
            last = peak
    return np.asarray(out, dtype=np.float64)


# ─── Analytical passage-time NNS (Farey bank, q_max = 8) ─────────────────────

def analytical_nns(t_n_array, fc_ref, q_max=Q_MAX):
    """Pool passage-time spacings across all Farey p:q PLL bands, q ≤ q_max."""
    if t_n_array.size < 5:
        return np.zeros(0), []
    pairs = farey_rationals(q_max)
    pooled, info = [], []
    for p, q in pairs:
        if q == 0: continue
        f_pll = fc_ref * p / q
        if f_pll <= 0: continue
        passage = t_n_array * f_pll - 1.0  # passage-time integer index
        # keep monotone-increasing positives
        passage = np.sort(passage[passage > 0])
        if passage.size < 5: continue
        sp = np.diff(passage)
        if sp.size == 0 or sp.mean() <= 0: continue
        pooled.append(sp / sp.mean())
        info.append((p, q, int(passage.size)))
    return (np.concatenate(pooled) if pooled else np.zeros(0)), info


def classify(pooled):
    if pooled.size < 50: return dict(n=int(pooled.size), best='insufficient')
    s = np.sort(pooled); n = s.size
    F = np.arange(1, n + 1) / n
    ks_p = float(np.max(np.abs(F - nns_cdf_poisson(s))))
    ks_o = float(np.max(np.abs(F - nns_cdf_goe(s))))
    ks_u = float(np.max(np.abs(F - nns_cdf_gue(s))))
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=n, ks_p=ks_p, ks_o=ks_o, ks_u=ks_u, gap=ks_o - ks_u,
                mass03=float((pooled < 0.3).mean()), best=best)


def direct_nns(spike_times):
    """NNS computed directly from spike inter-event times."""
    if spike_times.size < 5: return dict(n=int(spike_times.size), best='insufficient')
    sp = np.diff(np.sort(spike_times))
    if sp.size == 0 or sp.mean() <= 0:
        return dict(n=int(sp.size), best='insufficient')
    return classify(sp / sp.mean())


# ─── Find files ───────────────────────────────────────────────────────────────

def _main():
    files = sorted(p for p in glob.glob(os.path.join(FUNGI_ROOT, '**', '*.csv'),
                                         recursive=True)
                   if 'Zone.Identifier' not in p)
    print(f"Found {len(files)} CSV files\n")
    for f in files:
        print(f"  {Path(f).name}  ({os.path.getsize(f) / 1e6:.1f} MB)")
    print()


    # ─── Walk each file × channel ────────────────────────────────────────────────

    print("=" * 110)
    print("Per-(file, channel) spike detection + NNS classification")
    print("=" * 110)
    print(f"  {'file':<40} {'channel':<7} {'thresh':>6} {'n_sp':>4} "
          f"{'KS_P':>5} {'KS_O':>5} {'KS_U':>5} {'gap':>6} {'m<0.3':>5} best")

    per_unit = []     # one record per (file, channel)
    all_isi = []
    all_spike_seqs = []
    files_loaded = 0

    t_start = time.time()
    for f in files:
        try:
            df = load_fungal_csv(f)
        except Exception as exc:
            print(f"  [skip] {Path(f).name}: load error: {exc}")
            continue
        files_loaded += 1
        name = Path(f).stem[:38]
        duration_h = (df.index[-1] - df.index[0]) / 3600.0
        t_arr = df.index.to_numpy()

        for ch in df.columns:
            # try thresholds, pick one that hits TARGET_LO..TARGET_HI
            v = df[ch].to_numpy(dtype=np.float64)
            chosen_thr, chosen_spikes = None, None
            # Sort thresholds high→low so we find the most-conservative count
            # in the target window.
            for thr in sorted(THRESHOLDS, reverse=True):
                sp = detect_spikes(t_arr, v, threshold_std=thr)
                if TARGET_LO <= sp.size <= TARGET_HI:
                    chosen_thr, chosen_spikes = thr, sp
                    break
                if chosen_spikes is None or abs(sp.size - 60) < abs(chosen_spikes.size - 60):
                    chosen_thr, chosen_spikes = thr, sp

            n_sp = chosen_spikes.size
            record = dict(file=Path(f).name, channel=ch, threshold=chosen_thr,
                          n_spikes=int(n_sp),
                          duration_h=float(duration_h))
            if n_sp >= 20:
                cl = direct_nns(chosen_spikes)
                for k, v_ in cl.items():
                    record[f"direct_{k}"] = v_
                pooled, info = analytical_nns(chosen_spikes,
                                               fc_ref=1.0 / np.median(np.diff(np.sort(chosen_spikes))))
                cl_a = classify(pooled)
                for k, v_ in cl_a.items():
                    record[f"farey_{k}"] = v_
                isi = np.diff(np.sort(chosen_spikes))
                all_isi.append(isi)
                all_spike_seqs.append(chosen_spikes)
                print(f"  {name:<40} {ch[:5]:<7} {chosen_thr:>6.1f} {n_sp:>4} "
                      f"{cl.get('ks_p',0):.3f} {cl.get('ks_o',0):.3f} {cl.get('ks_u',0):.3f} "
                      f"{cl.get('gap',0):+6.3f} {cl.get('mass03',0):.3f} {cl.get('best','—')}")
            else:
                print(f"  {name:<40} {ch[:5]:<7} {chosen_thr:>6.1f} {n_sp:>4}  insufficient")
            per_unit.append(record)
        elapsed = time.time() - t_start
        print(f"  [{Path(f).name}: {duration_h:.1f}h, total elapsed {elapsed:.0f}s]")

    print()
    print(f"Loaded {files_loaded}/{len(files)} files")
    print(f"(file, channel) units with ≥20 spikes: {len(all_spike_seqs)}")


    # ─── Pooled across all units (direct NNS) ────────────────────────────────────

    print()
    print("=" * 110)
    print("POOLED across all (file, channel) units with ≥20 spikes")
    print("=" * 110)

    per_unit_normspacings = []
    for spikes in all_spike_seqs:
        sp = np.diff(np.sort(spikes))
        if sp.size > 0 and sp.mean() > 0:
            per_unit_normspacings.append(sp / sp.mean())

    if per_unit_normspacings:
        pool = np.concatenate(per_unit_normspacings)
        pooled_direct = classify(pool)
        print(f"  Direct NNS pool : n={pooled_direct['n']:,}  "
              f"KS_P={pooled_direct['ks_p']:.3f}  KS_O={pooled_direct['ks_o']:.3f}  "
              f"KS_U={pooled_direct['ks_u']:.3f}  gap={pooled_direct['gap']:+.3f}  "
              f"mass<0.3={pooled_direct['mass03']:.3f}  best={pooled_direct['best']}")
    else:
        pooled_direct = dict(best='insufficient', n=0)
        print("  Direct NNS pool : insufficient")

    # Pooled Farey-bank passage-time NNS (use the union of normalised passage
    # samples from each unit's analytical_nns)
    pooled_farey_lists = []
    for spikes in all_spike_seqs:
        isi_med = float(np.median(np.diff(np.sort(spikes))))
        if isi_med <= 0: continue
        p, _ = analytical_nns(spikes, fc_ref=1.0 / isi_med)
        if p.size > 0:
            pooled_farey_lists.append(p)
    if pooled_farey_lists:
        pf = np.concatenate(pooled_farey_lists)
        pooled_farey = classify(pf)
        print(f"  Farey bank pool : n={pooled_farey['n']:,}  "
              f"KS_P={pooled_farey['ks_p']:.3f}  KS_O={pooled_farey['ks_o']:.3f}  "
              f"KS_U={pooled_farey['ks_u']:.3f}  gap={pooled_farey['gap']:+.3f}  "
              f"mass<0.3={pooled_farey['mass03']:.3f}  best={pooled_farey['best']}")
    else:
        pooled_farey = dict(best='insufficient', n=0)


    # ─── ISI distribution + 2.6 / 14 min two-peak check ───────────────────────────

    if all_isi:
        isi_all_sec = np.concatenate(all_isi)
        isi_min = isi_all_sec / 60.0
        print()
        print("=" * 110)
        print(f"ISI distribution: n={isi_min.size:,}  "
              f"mean={isi_min.mean():.2f} min  median={np.median(isi_min):.2f} min  "
              f"std={isi_min.std():.2f} min")
        print("=" * 110)
        # Histogram counts for the 2.6 / 14 min predicted peaks
        bins = np.arange(0, max(60, isi_min.max()) + 1, 0.5)
        hist, edges = np.histogram(isi_min, bins=bins)
        centres = 0.5 * (edges[:-1] + edges[1:])
        for target in (2.6, 14.0):
            idx = int(np.argmin(np.abs(centres - target)))
            local = hist[max(0, idx - 2):idx + 3].sum()
            print(f"  count near {target:.1f} min: {local:5d} "
                  f"(bin centres {centres[max(0,idx-2)]:.1f}..{centres[min(len(centres)-1,idx+2)]:.1f})")
        # Detect peaks via simple max-in-window on histogram
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(hist, height=max(5, hist.max() / 8), distance=4)
        if peaks.size:
            print(f"  detected histogram peaks (≥{max(5, hist.max() // 8)} count, ≥2 min apart):")
            for k in peaks[:8]:
                print(f"    {centres[k]:5.1f} min   count={hist[k]}")
    else:
        isi_min = np.zeros(0)


    # ─── Plots ────────────────────────────────────────────────────────────────────

    if per_unit_normspacings:
        fig, ax = plt.subplots(1, 1, figsize=(8, 5))
        bins_s = np.linspace(0, 4, 41)
        s_grid = np.linspace(0.001, 4, 200)
        ax.hist(pool, bins=bins_s, density=True, alpha=0.55, color='C0',
                 label=f'fungal pool n={pool.size:,}')
        from universality import nns_poisson, nns_goe, nns_gue
        ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.2, label='Poisson')
        ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.2, label='GOE')
        ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.5, label='Wigner GUE')
        ax.set_xlim(0, 4); ax.set_ylim(0, 1.4)
        ax.set_xlabel('normalised inter-spike spacing s')
        ax.set_ylabel('P(s)')
        cl = pooled_direct
        ax.set_title(f"Fungal mycelium spike NNS (direct) — best={cl.get('best','—')}, "
                     f"KS_GUE={cl.get('ks_u', 0):.3f}, mass<0.3={cl.get('mass03', 0):.3f}")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOT_DIR, "29_fungal_nns.png"), dpi=110)
        plt.close(fig)
        print("\n  → plots/29_fungal_nns.png")

    if isi_min.size:
        fig, ax = plt.subplots(1, 1, figsize=(8, 5))
        bins_isi = np.arange(0, min(60.0, isi_min.max()) + 0.5, 0.5)
        ax.hist(isi_min, bins=bins_isi, color='C1', alpha=0.7)
        for target in (2.6, 14.0):
            ax.axvline(target, color='r', ls='--', lw=1, alpha=0.8,
                       label=f'Adamatzky peak {target} min' if target == 2.6 else None)
        ax.axvline(14.0, color='r', ls='--', lw=1, alpha=0.8)
        ax.set_xlabel('ISI (minutes)')
        ax.set_ylabel('count')
        ax.set_title(f"Fungal ISI distribution (n={isi_min.size:,}, mean={isi_min.mean():.1f} min)")
        ax.set_xlim(0, min(60, isi_min.max()))
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOT_DIR, "30_fungal_isi.png"), dpi=110)
        plt.close(fig)
        print("  → plots/30_fungal_isi.png")


    # ─── Save results ─────────────────────────────────────────────────────────────

    out = dict(
        config=dict(thresholds=THRESHOLDS, target_spikes=[TARGET_LO, TARGET_HI],
                    window_sec=WINDOW_SEC, min_isi_sec=MIN_ISI_SEC,
                    min_spike_width_sec=MIN_SPIKE_WIDTH_SEC, q_max=Q_MAX),
        n_files=files_loaded, n_units=len(per_unit),
        n_units_classified=len(all_spike_seqs),
        pooled_direct=pooled_direct, pooled_farey=pooled_farey,
        isi=dict(n=int(isi_min.size),
                 mean_min=float(isi_min.mean()) if isi_min.size else 0,
                 median_min=float(np.median(isi_min)) if isi_min.size else 0,
                 std_min=float(isi_min.std()) if isi_min.size else 0,
                 count_near_2_6_min=int(((isi_min > 2.0) & (isi_min < 3.2)).sum()) if isi_min.size else 0,
                 count_near_14_min=int(((isi_min > 12.0) & (isi_min < 16.0)).sum()) if isi_min.size else 0),
        per_unit=per_unit,
    )
    with open(os.path.join(DATA_DIR, "fungal_results.json"), 'w') as f_out:
        json.dump(out, f_out, indent=2, default=str)
    print(f"  → data/fungal_results.json")


if __name__ == "__main__":
    _main()
