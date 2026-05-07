"""
Phase 1.3 — GPU PLL kernel parity test.

Compares GPU bank output to CPU per-PLL output on the same signals and
verifies the lock fractions and phase errors match within tolerance.
"""
import math
import os
import sys
import time

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

from pll_bank import (  # noqa: E402
    single_pll_cpu, pll_bank_cpu, pll_bank_gpu,
    PLLParams, farey_rationals,
    GPU_AVAILABLE, GPU_NAME,
)


SR = 44100.0
DUR = 4.0
N = int(SR * DUR)


def make_tone(freq, sr=SR, dur=DUR, amp=1.0):
    t = np.arange(int(sr * dur), dtype=np.float64) / sr
    return (amp * np.cos(2 * np.pi * freq * t)).astype(np.float32)


def make_fm(fc, fm, beta, sr=SR, dur=DUR, amp=1.0):
    t = np.arange(int(sr * dur), dtype=np.float64) / sr
    return (amp * np.cos(2 * np.pi * fc * t + beta * np.sin(2 * np.pi * fm * t))).astype(np.float32)


print(f"GPU available: {GPU_AVAILABLE}  ({GPU_NAME})")
assert GPU_AVAILABLE, "GPU not available — skipping GPU tests"

params = PLLParams()

# ──────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("Test G1 — pure tone bank: 4 PLLs, expect all to match CPU output")
print("=" * 72)
sig = make_tone(440.0)
f_plls = np.array([110.0, 220.0, 440.0, 880.0], dtype=np.float32)

t0 = time.perf_counter()
lock_gpu, err_gpu = pll_bank_gpu(sig, f_plls, SR, params)
t_gpu = time.perf_counter() - t0

t0 = time.perf_counter()
lock_cpu_list = []
err_cpu_list  = []
for f in f_plls:
    lock, err, _ = single_pll_cpu(sig, float(f), SR, params)
    lock_cpu_list.append(lock); err_cpu_list.append(err)
lock_cpu = np.stack(lock_cpu_list, axis=0)
err_cpu  = np.stack(err_cpu_list,  axis=0)
t_cpu = time.perf_counter() - t0

print(f"  GPU bank (4 PLLs)  : {t_gpu*1000:6.1f} ms")
print(f"  CPU loop (4 PLLs)  : {t_cpu*1000:6.1f} ms")
print()

print("  per-PLL lock_fraction (after 200ms settle):")
print("  (max|Δerr| compared only on samples both backends call locked —")
print("   off-frequency PLLs have float-precision noise in the unlocked phase trace)")
n0 = int(SR * 0.2)
all_ok = True
for i, f in enumerate(f_plls):
    fg = float(lock_gpu[i, n0:].mean())
    fc = float(lock_cpu[i, n0:].mean())
    diff = abs(fg - fc)
    both_locked = (lock_gpu[i] == 1) & (lock_cpu[i] == 1)
    if both_locked.any():
        err_diff = float(np.abs(err_gpu[i, both_locked] - err_cpu[i, both_locked]).max())
    else:
        err_diff = 0.0   # no overlap → not meaningful
    status = "✓" if (diff < 0.05 and err_diff < 1e-3) else "✗"
    if status == "✗":
        all_ok = False
    print(f"    f_pll={f:7.1f}  GPU={fg:.3f}  CPU={fc:.3f}  "
          f"|Δlock|={diff:.4f}  max|Δerr|(when locked)={err_diff:.4e}  {status}")
assert all_ok, "FAIL: GPU↔CPU divergence on tone bank"
print("  PASS")
print()

# ──────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("Test G2 — pure FM bank: 9 PLLs at sideband frequencies")
print("=" * 72)
fc, fm, beta = 220.0, 165.0, 3.0
sig = make_fm(fc, fm, beta)
f_plls = np.array([fc + n * fm for n in range(-4, 5) if fc + n * fm > 5.0],
                  dtype=np.float32)

t0 = time.perf_counter()
lock_gpu, err_gpu = pll_bank_gpu(sig, f_plls, SR, params)
t_gpu = time.perf_counter() - t0

t0 = time.perf_counter()
lock_cpu, err_cpu = pll_bank_cpu(sig, f_plls, SR, params)
t_cpu = time.perf_counter() - t0

print(f"  GPU bank ({len(f_plls)} PLLs)  : {t_gpu*1000:6.1f} ms")
print(f"  CPU bank ({len(f_plls)} PLLs)  : {t_cpu*1000:6.1f} ms")
print(f"  speedup            : {t_cpu/max(t_gpu, 1e-9):.1f}×")
print()
print("  per-PLL lock_fraction (after 200ms settle):")
n0 = int(SR * 0.2)
all_ok = True
for i, f in enumerate(f_plls):
    fg = float(lock_gpu[i, n0:].mean())
    fc_v = float(lock_cpu[i, n0:].mean())
    diff = abs(fg - fc_v)
    both_locked = (lock_gpu[i] == 1) & (lock_cpu[i] == 1)
    if both_locked.any():
        err_diff = float(np.abs(err_gpu[i, both_locked] - err_cpu[i, both_locked]).max())
    else:
        err_diff = 0.0
    status = "✓" if (diff < 0.05 and err_diff < 5e-3) else "✗"
    if status == "✗":
        all_ok = False
    print(f"    f_pll={f:7.1f}  GPU={fg:.3f}  CPU={fc_v:.3f}  "
          f"|Δlock|={diff:.4f}  max|Δerr|(when locked)={err_diff:.4e}  {status}")
assert all_ok, "FAIL: GPU↔CPU divergence on FM bank"
print("  PASS")
print()

# ──────────────────────────────────────────────────────────────────────────────
print("=" * 72)
print("Test G3 — full Farey bank (q_max=8) on FM signal")
print("=" * 72)
fc = 220.0
pairs = farey_rationals(8)
f_plls = np.array([fc * p / q for p, q in pairs if 5.0 < fc * p / q < SR * 0.45],
                  dtype=np.float32)
print(f"  {len(f_plls)} PLLs (q_max=8) on FM(fc={fc}, fm=165, β=3)")

sig = make_fm(220.0, 165.0, 3.0)
t0 = time.perf_counter()
lock_gpu, err_gpu = pll_bank_gpu(sig, f_plls, SR, params)
t_gpu = time.perf_counter() - t0
print(f"  GPU bank time: {t_gpu*1000:6.1f} ms ({len(f_plls) * N / max(t_gpu, 1e-9) / 1e6:.0f} M-PLL-samples/sec)")

# Find which Farey rationals lock:
n0 = int(SR * 0.2)
print()
print("  Farey rationals that locked >50% (after 200ms):")
print(f"  {'p:q':>6}  {'f_pll':>6}  {'lock':>6}  {'onset_ms':>8}")
for i, (p, q) in enumerate(pairs):
    f = fc * p / q
    if not (5.0 < f < SR * 0.45):
        continue
    j = np.where(np.isclose(f_plls, f))[0]
    if len(j) == 0: continue
    j = j[0]
    frac = float(lock_gpu[j, n0:].mean())
    if frac > 0.50:
        onset_idx = int(np.argmax(lock_gpu[j] > 0))
        onset_ms = 1000.0 * onset_idx / SR if lock_gpu[j, onset_idx] else float('inf')
        print(f"  {p}:{q:<3d}  {f:6.1f}  {frac:.3f}  {onset_ms:7.1f}")

# Sanity: white noise must lock < 10% on average
print()
sig_noise = (np.random.default_rng(0).standard_normal(N) * 0.5).astype(np.float32)
lock_noise, _ = pll_bank_gpu(sig_noise, f_plls, SR, params)
mean_noise_frac = float(lock_noise[:, n0:].mean())
max_noise_frac  = float(lock_noise[:, n0:].mean(axis=1).max())
print(f"  white noise: mean lock_frac across PLLs = {mean_noise_frac:.4f}, "
      f"max per-PLL = {max_noise_frac:.4f}")
assert max_noise_frac < 0.10, f"FAIL: noise locked some PLL at {max_noise_frac:.3f}"
print("  PASS")
print()

print("=" * 72)
print("PHASE 1 GPU PARITY TESTS PASSED")
print("=" * 72)
