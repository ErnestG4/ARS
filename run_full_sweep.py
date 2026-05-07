"""
Full parameter sweep for the criticality tool.

Dimensions:
    fc_ref_vals  = np.logspace(log10(2), log10(500), 50)   # 50 points, 2–500 Hz
    q_max_vals   = [6, 8, 10, 12, 16]
    kp_vals      = [0.02, 0.05, 0.10, 0.20]
    signals      = ['zeta', 'white_noise', 'poisson_zeta_like']

3 signals × 5 q_max × 4 K_p × 50 fc_ref = 3000 cells.

Per-cell metrics (recorded to HDF5):
    F_aggregate_L1    — aggregate Fano factor at L=1 mean-spacing unit
    F_perpll_mean     — mean per-PLL Fano at L=1 across locking PLLs
    F_perpll_std      — std of those per-PLL Fanos
    n_locking_plls    — count of PLLs with lock_fraction > 1%
    n_events_total    — total lock onsets across the bank
    depth_kl          — KL(observed depth | geometric 2^−d)
    mean_lock_ms, mean_slip_ms — global dwell means

Batching strategy: for each (signal, q_max, K_p) outer-iteration, build a
single super-bank of all 50 fc_ref's PLLs (chunked if memory is tight),
run pll_bank_gpu once on the signal, then slice the resulting lock_map
back into 50 cells for analysis.  This minimises kernel launches without
exceeding GPU memory at q_max=16 (worst case ~14 GB if not chunked).
"""
import os
import sys
import time

import h5py
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')

from pll_bank import pll_bank_gpu, PLLParams, farey_rationals, GPU_NAME  # noqa: E402
from intermittency import fast_sweep_summary  # noqa: E402
import signal_gen  # noqa: E402

import cupy as cp  # noqa: E402

# ── Sweep config ──────────────────────────────────────────────────────────────
SR        = 44100.0
DUR_S     = 30.0
NZ        = 100
N_SAMPLES = int(SR * DUR_S)

FC_REF_VALS = np.logspace(np.log10(2.0), np.log10(500.0), 50)
QMAX_VALS   = [6, 8, 10, 12, 16]
KP_VALS     = [0.02, 0.05, 0.10, 0.20]
SIGNAL_NAMES = ['zeta', 'white_noise', 'poisson_zeta_like']

# Memory budget: keep each launch's lock_map under ~8 GB.
# lock_map size = N_PLL_per_launch × N_SAMPLES bytes.  N_SAMPLES = 1.323 M.
# Per-launch PLLs cap = 8e9 / 1.323e6 ≈ 6000.  Use 5000 as the cap.
PLL_LIMIT_PER_LAUNCH = 5000

OUTPUT_PATH = os.path.join(THIS_DIR, "sweep_results.h5")


# ── Build signals once ────────────────────────────────────────────────────────
print(f"Building signals (sr={SR}, duration={DUR_S}s, n_zeros={NZ}) …")
sig_zeta    = signal_gen.make_zeta_signal(sr=SR, duration=DUR_S, n_zeros=NZ)
sig_noise   = signal_gen.make_white_noise(sr=SR, duration=DUR_S)
sig_poisson = signal_gen.make_poisson_zeta_like(sr=SR, duration=DUR_S, n_points=NZ, seed=0)
SIGNALS = {'zeta': sig_zeta, 'white_noise': sig_noise, 'poisson_zeta_like': sig_poisson}
for name, s in SIGNALS.items():
    rms = float(np.sqrt(np.mean(s.astype(np.float64) ** 2)))
    print(f"  {name:20s}: len={len(s)} samples, RMS={rms:.5f}, "
          f"range [{s.min():.3f}, {s.max():.3f}]")
print()


# ── Pre-compute Farey banks ───────────────────────────────────────────────────
FAREY_BY_QMAX = {q: farey_rationals(q) for q in QMAX_VALS}
print("Farey bank sizes:")
for q in QMAX_VALS:
    print(f"  q_max={q:2d}: {len(FAREY_BY_QMAX[q])} pairs")
print()


# ── Compose flat list of cells, prepare HDF5 ──────────────────────────────────
N_CELLS = len(SIGNAL_NAMES) * len(QMAX_VALS) * len(KP_VALS) * len(FC_REF_VALS)
print(f"Total cells: {N_CELLS}")
print(f"GPU: {GPU_NAME}")
print()

# Output arrays — one row per cell.
SCALAR_FIELDS = [
    'F_aggregate_L1', 'F_perpll_mean', 'F_perpll_std',
    'n_locking_plls', 'n_events_total', 'depth_kl',
    'mean_lock_ms', 'mean_slip_ms',
    'n_plls_total',
]
out = {f: np.full(N_CELLS, np.nan, dtype=np.float64) for f in SCALAR_FIELDS}
out['signal_idx'] = np.zeros(N_CELLS, dtype=np.int32)
out['q_max']      = np.zeros(N_CELLS, dtype=np.int32)
out['kp']         = np.zeros(N_CELLS, dtype=np.float32)
out['fc_ref']     = np.zeros(N_CELLS, dtype=np.float64)
out['fc_idx']     = np.zeros(N_CELLS, dtype=np.int32)
# Depth-event-count matrix: rows are cells, columns are depths 0..15.
DEPTH_MAX = 16
out['depth_event_counts'] = np.zeros((N_CELLS, DEPTH_MAX), dtype=np.int64)
out['depth_pll_counts']   = np.zeros((N_CELLS, DEPTH_MAX), dtype=np.int64)


def cell_index(sig_i, q_i, k_i, fc_i):
    return ((sig_i * len(QMAX_VALS) + q_i) * len(KP_VALS) + k_i) * len(FC_REF_VALS) + fc_i


def in_band(f):
    return 5.0 < f < SR * 0.45


# ── Sweep ─────────────────────────────────────────────────────────────────────
t_total0 = time.perf_counter()
total_gpu_seconds = 0.0
total_cpu_seconds = 0.0
cells_done = 0
N_outer = len(SIGNAL_NAMES) * len(QMAX_VALS) * len(KP_VALS)
i_outer = 0

for sig_i, sig_name in enumerate(SIGNAL_NAMES):
    sig = SIGNALS[sig_name]
    for q_i, q_max in enumerate(QMAX_VALS):
        pairs = FAREY_BY_QMAX[q_max]
        for k_i, kp in enumerate(KP_VALS):
            i_outer += 1
            params = PLLParams(K_p=kp, K_i=kp * 0.05, rho=0.95)
            # Build all PLLs for all 50 fc_refs in this outer cell.
            # Track ((fc_idx, pair_idx) → flat_pll_idx) so we can slice later.
            flat_pll_freqs = []
            flat_pairs     = []           # which (p,q) does each PLL belong to
            cell_pll_index = [[] for _ in range(len(FC_REF_VALS))]   # per-fc_ref → indices in flat
            cell_pairs_map = [[] for _ in range(len(FC_REF_VALS))]   # per-fc_ref → pair list
            for fc_i, fc_ref in enumerate(FC_REF_VALS):
                for pair in pairs:
                    f_pll = fc_ref * pair[0] / pair[1]
                    if in_band(f_pll):
                        idx = len(flat_pll_freqs)
                        flat_pll_freqs.append(f_pll)
                        flat_pairs.append(pair)
                        cell_pll_index[fc_i].append(idx)
                        cell_pairs_map[fc_i].append(pair)

            flat_freqs_arr = np.asarray(flat_pll_freqs, dtype=np.float32)
            n_total = flat_freqs_arr.size

            # Run pll_bank_gpu, chunking the PLL set if it exceeds the memory cap.
            t0 = time.perf_counter()
            if n_total <= PLL_LIMIT_PER_LAUNCH:
                lock_map_full, _ = pll_bank_gpu(sig, flat_freqs_arr, SR, params,
                                                return_phase_error=False)
            else:
                # Concatenate chunks to keep memory within budget.
                chunks = []
                for s_start in range(0, n_total, PLL_LIMIT_PER_LAUNCH):
                    s_end = min(s_start + PLL_LIMIT_PER_LAUNCH, n_total)
                    sub = flat_freqs_arr[s_start:s_end]
                    lm_chunk, _ = pll_bank_gpu(sig, sub, SR, params, return_phase_error=False)
                    chunks.append(lm_chunk)
                lock_map_full = np.concatenate(chunks, axis=0)
            t_gpu = time.perf_counter() - t0
            total_gpu_seconds += t_gpu

            # Analyze each fc_ref cell.
            t0 = time.perf_counter()
            for fc_i, fc_ref in enumerate(FC_REF_VALS):
                pll_idx = cell_pll_index[fc_i]
                cell_pairs = cell_pairs_map[fc_i]
                if len(pll_idx) == 0:
                    ci = cell_index(sig_i, q_i, k_i, fc_i)
                    out['signal_idx'][ci] = sig_i
                    out['q_max'][ci] = q_max
                    out['kp'][ci] = kp
                    out['fc_ref'][ci] = fc_ref
                    out['fc_idx'][ci] = fc_i
                    out['n_plls_total'][ci] = 0
                    continue
                cell_lm = lock_map_full[pll_idx]
                summary = fast_sweep_summary(cell_lm, SR, cell_pairs)
                ci = cell_index(sig_i, q_i, k_i, fc_i)
                for f in SCALAR_FIELDS:
                    if f == 'n_plls_total':
                        out[f][ci] = len(pll_idx)
                    else:
                        out[f][ci] = summary[f]
                out['signal_idx'][ci] = sig_i
                out['q_max'][ci] = q_max
                out['kp'][ci] = kp
                out['fc_ref'][ci] = fc_ref
                out['fc_idx'][ci] = fc_i
                # Pack depth histograms by depth value.
                for d_val, evt_c, pll_c in zip(summary['depths'],
                                                summary['depth_event_counts'],
                                                summary['depth_pll_counts']):
                    if 0 <= d_val < DEPTH_MAX:
                        out['depth_event_counts'][ci, d_val] = evt_c
                        out['depth_pll_counts'][ci, d_val]   = pll_c
                cells_done += 1
            t_cpu = time.perf_counter() - t0
            total_cpu_seconds += t_cpu

            elapsed = time.perf_counter() - t_total0
            avg_per_outer = elapsed / i_outer
            eta_outer = avg_per_outer * (N_outer - i_outer)
            print(f"  [{i_outer:2d}/{N_outer}] {sig_name:18s} q_max={q_max:2d} K_p={kp:.2f}  "
                  f"PLLs={n_total:5d}  gpu={t_gpu:5.1f}s cpu={t_cpu:5.1f}s   "
                  f"ETA {eta_outer/60:.1f} min")
            # Free GPU memory between outer iterations.
            del lock_map_full
            cp.get_default_memory_pool().free_all_blocks()


print()
print(f"  totals  gpu={total_gpu_seconds/60:.1f} min   cpu={total_cpu_seconds/60:.1f} min   "
      f"wall={(time.perf_counter()-t_total0)/60:.1f} min")


# ── Save HDF5 ────────────────────────────────────────────────────────────────
print(f"\nSaving {OUTPUT_PATH}")
with h5py.File(OUTPUT_PATH, 'w') as f:
    f.attrs['sr'] = SR
    f.attrs['duration_s'] = DUR_S
    f.attrs['n_zeros'] = NZ
    f.attrs['fc_ref_min'] = FC_REF_VALS[0]
    f.attrs['fc_ref_max'] = FC_REF_VALS[-1]
    f.attrs['fc_ref_n']   = len(FC_REF_VALS)
    f.attrs['gpu_name']   = GPU_NAME or 'cpu'
    f.create_dataset('fc_ref_vals', data=FC_REF_VALS)
    f.create_dataset('q_max_vals',  data=np.array(QMAX_VALS, dtype=np.int32))
    f.create_dataset('kp_vals',     data=np.array(KP_VALS,   dtype=np.float64))
    f.create_dataset('signal_names', data=np.array(SIGNAL_NAMES, dtype='S32'))
    for name, arr in out.items():
        f.create_dataset(name, data=arr, compression='gzip')

print(f"\nWrote {N_CELLS} cells to {OUTPUT_PATH}.")
