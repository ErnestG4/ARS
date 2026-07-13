"""
Task 1 — GUE calibration depth profile.

Generate a synthetic chirp signal whose "frequencies" are eigenvalues of a
GUE random matrix (analytically known to follow GUE level statistics, the
same conjectured statistics of the ζ zeros).  Run the same Farey PLL bank
on it that we ran on ζ, and ask: does it produce the depth-4 peak?

If yes → depth-4 is a property of ANY GUE-spaced chirp run through this
detector, not specific to the Riemann zeros.  If no → depth-4 is specific
to ζ structure beyond GUE-class spacing statistics.

Configuration:
    K_p     = 0.02       (tongue boundary, most stable from Task 0 sweep)
    fc_ref  ∈ {30, 100, 115, 300} Hz (representative + max-separation cell)
    q_max   ∈ {8, 16}
    signal  = make_gue_eigenvalue_signal(n_points=100, dur=30s)
    compare to: same parameters on ζ from the existing sweep_results.h5
"""
import os, sys, time
import numpy as np
import h5py

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))

from pll_bank import pll_bank_gpu, PLLParams, farey_rationals, GPU_NAME
from intermittency import fast_sweep_summary
import signal_gen
import cupy as cp


SR  = 44100.0
DUR = 30.0
NZ  = 100

FC_REFS  = [30.0, 100.0, 115.55, 300.0]
QMAXES   = [8, 16]
K_P      = 0.02


# Build all three signals (regenerate ζ + Poisson-FM null with same seed for parity).
print("Generating signals …")
sig_zeta = signal_gen.make_zeta_signal(sr=SR, duration=DUR, n_zeros=NZ)
sig_gue  = signal_gen.make_gue_eigenvalue_signal(sr=SR, duration=DUR, n_points=NZ, seed=42,
                                                   rescale_to_zeta_range=True)
sig_pois = signal_gen.make_poisson_zeta_like(sr=SR, duration=DUR, n_points=NZ, seed=0)
for name, s in [('ζ', sig_zeta), ('GUE', sig_gue), ('Poisson-FM', sig_pois)]:
    rms = float(np.sqrt(np.mean(s.astype(np.float64) ** 2)))
    print(f"  {name:11s}: RMS={rms:.5f}  range=[{s.min():.4f}, {s.max():.4f}]")
print()

print(f"GPU: {GPU_NAME}")
print(f"K_p={K_P}, q_max={QMAXES}, fc_ref={FC_REFS}")
print()


def run_cell(signal, fc_ref, q_max, kp):
    pairs = farey_rationals(q_max)
    freqs = []
    pairs_kept = []
    for p, q in pairs:
        f = fc_ref * p / q
        if 5.0 < f < SR * 0.45:
            freqs.append(f)
            pairs_kept.append((p, q))
    freqs = np.asarray(freqs, dtype=np.float32)
    params = PLLParams(K_p=kp, K_i=kp * 0.05, rho=0.95)
    lock_map, _ = pll_bank_gpu(signal, freqs, SR, params, return_phase_error=False)
    summary = fast_sweep_summary(lock_map, SR, pairs_kept)
    del lock_map
    cp.get_default_memory_pool().free_all_blocks()
    return summary


# ── Run all 8 configurations × 3 signals = 24 cells ───────────────────────────
results = {}
print(f"  {'signal':12s}  {'q_max':>5}  {'fc_ref':>7}  {'F_agg':>6}  {'F_pp_mean':>9}  "
      f"{'n_lock':>6}  {'n_evt':>5}  {'depth_kl':>8}  {'mean_lock_ms':>12}")
for q_max in QMAXES:
    for fc_ref in FC_REFS:
        for sig_name, sig in [('zeta', sig_zeta), ('gue', sig_gue), ('poiss', sig_pois)]:
            t0 = time.perf_counter()
            s = run_cell(sig, fc_ref, q_max, K_P)
            dt = time.perf_counter() - t0
            results[(sig_name, q_max, fc_ref)] = s
            print(f"  {sig_name:12s}  {q_max:5d}  {fc_ref:7.2f}  "
                  f"{s['F_aggregate_L1']:6.3f}  {s['F_perpll_mean']:9.3f}  "
                  f"{s['n_locking_plls']:6d}  {s['n_events_total']:5d}  "
                  f"{s['depth_kl']:8.3f}  {s['mean_lock_ms']:12.2f}    [{dt:.1f}s]")
print()

# ── Depth histograms — side-by-side comparison ────────────────────────────────
print("=" * 90)
print("Depth histograms — fraction of events at each depth, for q_max=8 (most-quoted config)")
print("=" * 90)
q_show = 8
all_depths = sorted(set(d for s in results.values() for d in s['depths']))
print(f"  {'fc_ref':>7}  {'sig':>6}  " + "  ".join(f"d={d:>1}" for d in all_depths)
      + "  KL_geom  n_evt")
for fc_ref in FC_REFS:
    for sig_name in ['zeta', 'gue', 'poiss']:
        s = results[(sig_name, q_show, fc_ref)]
        total = max(int(s['depth_event_counts'].sum()), 1)
        dist = {int(d): int(c) for d, c in zip(s['depths'], s['depth_event_counts'])}
        row = "  ".join(f"{dist.get(d, 0)/total:>3.2f}" for d in all_depths)
        print(f"  {fc_ref:7.2f}  {sig_name:>6}  {row}  {s['depth_kl']:7.3f}  {s['n_events_total']:>5d}")
    print()

print("=" * 90)
print("Depth histograms — q_max=16 (highest-resolution Farey bank)")
print("=" * 90)
q_show = 16
all_depths = sorted(set(d for k, s in results.items() if k[1] == q_show for d in s['depths']))
print(f"  {'fc_ref':>7}  {'sig':>6}  " + "  ".join(f"d={d:>1}" for d in all_depths)
      + "  KL_geom  n_evt")
for fc_ref in FC_REFS:
    for sig_name in ['zeta', 'gue', 'poiss']:
        s = results[(sig_name, q_show, fc_ref)]
        total = max(int(s['depth_event_counts'].sum()), 1)
        dist = {int(d): int(c) for d, c in zip(s['depths'], s['depth_event_counts'])}
        row = "  ".join(f"{dist.get(d, 0)/total:>3.2f}" for d in all_depths)
        print(f"  {fc_ref:7.2f}  {sig_name:>6}  {row}  {s['depth_kl']:7.3f}  {s['n_events_total']:>5d}")
    print()


# ── Headline comparison: peak depth + KL ──────────────────────────────────────
print("=" * 90)
print("Peak depth (depth bin with most events) and KL_geometric — by signal")
print("=" * 90)
print(f"  {'q_max':>5}  {'fc_ref':>7}  {'ζ peak':>6}  {'ζ frac':>6}  {'GUE peak':>8}  "
      f"{'GUE frac':>8}  {'Poiss peak':>10}  {'Poiss frac':>10}  "
      f"{'KL ζ':>6}  {'KL GUE':>6}  {'KL Poi':>6}")
for q_max in QMAXES:
    for fc_ref in FC_REFS:
        sz = results[('zeta', q_max, fc_ref)]
        sg = results[('gue',  q_max, fc_ref)]
        sp = results[('poiss', q_max, fc_ref)]
        def peak_of(s):
            tot = s['depth_event_counts'].sum()
            if tot == 0: return None, 0.0
            i = int(np.argmax(s['depth_event_counts']))
            return int(s['depths'][i]), float(s['depth_event_counts'][i]) / tot
        pz, fz = peak_of(sz)
        pg, fg = peak_of(sg)
        pp, fp = peak_of(sp)
        print(f"  {q_max:5d}  {fc_ref:7.2f}  "
              f"{pz!s:>6}  {fz:6.3f}  "
              f"{pg!s:>8}  {fg:8.3f}  "
              f"{pp!s:>10}  {fp:10.3f}  "
              f"{sz['depth_kl']:6.3f}  {sg['depth_kl']:6.3f}  {sp['depth_kl']:6.3f}")
print()


# ── Verdict ───────────────────────────────────────────────────────────────────
print("=" * 90)
print("Verdict")
print("=" * 90)
zeta_peaks = [results[('zeta', q, fc)] for q in QMAXES for fc in FC_REFS]
gue_peaks  = [results[('gue',  q, fc)] for q in QMAXES for fc in FC_REFS]

zeta_peak_d4 = sum(1 for s in zeta_peaks
                    if s['depths'][int(np.argmax(s['depth_event_counts']))] == 4)
gue_peak_d4  = sum(1 for s in gue_peaks
                    if s['depths'][int(np.argmax(s['depth_event_counts']))] == 4)
print(f"  ζ cells with peak at depth=4   : {zeta_peak_d4}/{len(zeta_peaks)}")
print(f"  GUE cells with peak at depth=4 : {gue_peak_d4}/{len(gue_peaks)}")
print()
print(f"  mean KL_ζ  = {np.mean([s['depth_kl'] for s in zeta_peaks]):.3f}")
print(f"  mean KL_G  = {np.mean([s['depth_kl'] for s in gue_peaks]):.3f}")
print()
print("  If GUE peak is also at depth=4 with similar KL → depth-4 is a")
print("  GUE-chirp property; the brief's 'p-adic structure' hypothesis is mild.")
print("  If GUE peak shifts or KL is much lower than ζ → ζ has arithmetic")
print("  structure beyond its conjectured GUE spacing; depth-4 is specific.")

# Save raw results for downstream Task 3.
import pickle
out_pkl = os.path.join(THIS_DIR, "gue_calibration_results.pkl")
with open(out_pkl, 'wb') as f:
    pickle.dump({'results': results, 'fc_refs': FC_REFS, 'qmaxes': QMAXES,
                  'kp': K_P, 'sr': SR, 'dur': DUR, 'nz': NZ}, f)
print(f"\n  raw → {out_pkl}")
