"""
Read sweep_results.h5 and produce the five derived analyses requested:

  1.  F(fc_ref) curves per (signal × q_max × K_p) — does ζ separate from nulls?
  2.  fc_ref × q_max heatmap of depth_kl — does the anti-geometric depth
      signature persist across the parameter space?
  3.  K_p sensitivity — which K_p makes F most stable across fc_ref?
      That's the tongue-boundary K_p.
  4.  Signal separation — F_zeta / F_noise and F_zeta / F_poisson at every
      (fc_ref, q_max, K_p) cell; find the max-separation region.
  5.  Depth histogram across fc_ref — does the depth-4 peak shift with
      fc_ref (chirp artifact) or stay (intrinsic)?

Plus: search for any (fc_ref, q_max, K_p) cell where F_zeta < 1 — the GUE
level-repulsion signature we're ultimately looking for.

ASCII output for terminal-friendly reporting; PNG plots saved to plots/.
"""
import os, sys
import numpy as np
import h5py

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
H5_PATH  = os.path.join(THIS_DIR, "sweep_results.h5")
PLOT_DIR = os.path.join(THIS_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def reshape_4d(arr_flat, shape):
    """signal × q_max × K_p × fc_ref reshape from flat cell array."""
    return arr_flat.reshape(shape)


# ── Load ──────────────────────────────────────────────────────────────────────
print(f"reading {H5_PATH}")
with h5py.File(H5_PATH, 'r') as f:
    fc_ref_vals = f['fc_ref_vals'][:]
    q_max_vals  = f['q_max_vals'][:]
    kp_vals     = f['kp_vals'][:]
    signal_names = [n.decode() for n in f['signal_names'][:]]
    F_agg = f['F_aggregate_L1'][:]
    F_pp_mean = f['F_perpll_mean'][:]
    F_pp_std  = f['F_perpll_std'][:]
    n_lock = f['n_locking_plls'][:]
    n_evt  = f['n_events_total'][:]
    depth_kl = f['depth_kl'][:]
    mean_lock = f['mean_lock_ms'][:]
    mean_slip = f['mean_slip_ms'][:]
    n_plls    = f['n_plls_total'][:]
    depth_evt = f['depth_event_counts'][:]
    sr = f.attrs['sr']
    dur = f.attrs['duration_s']
    nz  = f.attrs['n_zeros']
    gpu = f.attrs.get('gpu_name', 'unknown')

shape = (len(signal_names), len(q_max_vals), len(kp_vals), len(fc_ref_vals))
F_agg     = F_agg.reshape(shape)
F_pp_mean = F_pp_mean.reshape(shape)
F_pp_std  = F_pp_std.reshape(shape)
n_lock    = n_lock.reshape(shape)
n_evt     = n_evt.reshape(shape)
depth_kl  = depth_kl.reshape(shape)
mean_lock = mean_lock.reshape(shape)
mean_slip = mean_slip.reshape(shape)
depth_evt = depth_evt.reshape(shape + (depth_evt.shape[-1],))

ZETA  = signal_names.index('zeta')
NOISE = signal_names.index('white_noise')
POISS = signal_names.index('poisson_zeta_like')

print(f"  config: sr={sr} duration={dur}s n_zeros={nz} GPU={gpu}")
print(f"  fc_ref: {len(fc_ref_vals)} pts in [{fc_ref_vals.min():.2f}, {fc_ref_vals.max():.1f}] Hz")
print(f"  q_max : {list(q_max_vals)}")
print(f"  K_p   : {list(kp_vals)}")
print(f"  signals: {signal_names}")
print()


# ── Helper: ASCII heatmap ─────────────────────────────────────────────────────
def ascii_heatmap_2d(grid, x_vals, y_vals, x_label, y_label,
                     title, log_x=False, vmin=None, vmax=None,
                     symbols=" ·-=+*#@█"):
    rows, cols = grid.shape
    if vmin is None:
        vmin = float(np.nanmin(grid))
    if vmax is None:
        vmax = float(np.nanmax(grid))
    rng = max(vmax - vmin, 1e-9)
    print(f"  {title}")
    print(f"  range [{vmin:.3f}, {vmax:.3f}], NaN shown as '?'")
    # Subsample columns to fit terminal (~70 char wide)
    max_cols = 60
    if cols > max_cols:
        idx = np.linspace(0, cols - 1, max_cols).astype(int)
    else:
        idx = np.arange(cols)
    header = f"  {y_label:>6} \\ {x_label}: "
    print(header + "  ".join(f"{x_vals[i]:6.1f}" for i in idx[::8]))
    for r in range(rows - 1, -1, -1):  # large y on top
        line = f"  {y_vals[r]:>6}  "
        for c in idx:
            v = grid[r, c]
            if np.isnan(v):
                line += "?"
            else:
                k = int(np.clip((v - vmin) / rng, 0, 1) * (len(symbols) - 1))
                line += symbols[k]
        print(line)


# ── Analysis 1 — F(fc_ref) curves ─────────────────────────────────────────────
print("=" * 78)
print("Analysis 1 — F_aggregate(fc_ref) curves: does ζ separate from nulls?")
print("=" * 78)
# Pick a representative (q_max, K_p) — middle of grid
q_show = list(q_max_vals).index(8) if 8 in q_max_vals else len(q_max_vals)//2
k_show = list(kp_vals).index(0.10) if 0.10 in kp_vals else len(kp_vals)//2
print(f"  showing at q_max={q_max_vals[q_show]}, K_p={kp_vals[k_show]}")
print()
print(f"  {'fc_ref':>7}  {'F_zeta':>8}  {'F_noise':>8}  {'F_poiss':>8}  {'ratio_z/n':>9}  {'ratio_z/p':>9}")
for fi in range(0, len(fc_ref_vals), 5):
    fc = fc_ref_vals[fi]
    Fz = F_agg[ZETA, q_show, k_show, fi]
    Fn = F_agg[NOISE, q_show, k_show, fi]
    Fp = F_agg[POISS, q_show, k_show, fi]
    rzn = Fz/Fn if Fn>0 and not np.isnan(Fn) else np.nan
    rzp = Fz/Fp if Fp>0 and not np.isnan(Fp) else np.nan
    print(f"  {fc:7.1f}  {Fz:8.3f}  {Fn:8.3f}  {Fp:8.3f}  {rzn:9.3f}  {rzp:9.3f}")
print()

# Plot F vs fc_ref for all (q_max, K_p) combinations.
fig, axes = plt.subplots(len(q_max_vals), len(kp_vals),
                          figsize=(4*len(kp_vals), 2.5*len(q_max_vals)),
                          sharex=True)
for qi, q in enumerate(q_max_vals):
    for ki, kp in enumerate(kp_vals):
        ax = axes[qi, ki] if len(q_max_vals) > 1 else axes[ki]
        ax.semilogx(fc_ref_vals, F_agg[ZETA, qi, ki, :], 'C0-', label='ζ', lw=2)
        ax.semilogx(fc_ref_vals, F_agg[NOISE, qi, ki, :], 'C1--', label='noise', lw=1)
        ax.semilogx(fc_ref_vals, F_agg[POISS, qi, ki, :], 'C2:', label='poiss-FM', lw=1)
        ax.axhline(1.0, color='k', lw=0.5, alpha=0.3)
        if qi == 0 and ki == 0:
            ax.legend(fontsize=7)
        if ki == 0:
            ax.set_ylabel(f'q={q}\nF_agg(L=1)')
        if qi == len(q_max_vals)-1:
            ax.set_xlabel('fc_ref (Hz)')
        ax.set_title(f'K_p={kp}', fontsize=9)
        ax.set_yscale('symlog', linthresh=1)
        ax.grid(True, alpha=0.3)
fig.suptitle("F_aggregate(fc_ref) per (q_max, K_p) for three signals\n(horizontal line at F=1; F<1 = GUE-like, F>1 = clustered)")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOT_DIR, "01_F_curves.png"), dpi=110)
plt.close(fig)
print(f"  → plots/01_F_curves.png saved")
print()


# ── Analysis 2 — fc_ref × q_max KL heatmap ────────────────────────────────────
print("=" * 78)
print("Analysis 2 — depth_kl heatmap (ζ signal): does anti-geometric persist?")
print("=" * 78)
# Average over K_p (they're all valid configurations)
kl_zeta = np.nanmean(depth_kl[ZETA], axis=1)   # (q_max, fc_ref)
print()
ascii_heatmap_2d(kl_zeta, fc_ref_vals, q_max_vals,
                  "fc_ref", "q_max",
                  "depth_kl(ζ) — ' ' = matches geometric, '█' = strongly anti-geometric",
                  vmin=0.0, vmax=float(np.nanmax(kl_zeta)))
print()
print(f"  ζ depth_kl statistics:")
print(f"    mean = {np.nanmean(kl_zeta):.3f}")
print(f"    max  = {np.nanmax(kl_zeta):.3f}")
print(f"    where in (q_max, fc_ref) is KL maximised?")
qi_max, fi_max = np.unravel_index(np.nanargmax(kl_zeta), kl_zeta.shape)
print(f"      → q_max={q_max_vals[qi_max]}, fc_ref={fc_ref_vals[fi_max]:.1f}, KL={kl_zeta[qi_max, fi_max]:.3f}")
print()
# Compare to nulls
kl_noise = np.nanmean(depth_kl[NOISE], axis=1)
kl_poiss = np.nanmean(depth_kl[POISS], axis=1)
print(f"  noise KL mean = {np.nanmean(kl_noise):.3f}, poisson-FM KL mean = {np.nanmean(kl_poiss):.3f}")

# Save heatmap PNG
fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
for ax, kl, name in zip(axes, [kl_zeta, kl_noise, kl_poiss],
                         ['ζ', 'white noise', 'Poisson-FM']):
    im = ax.imshow(kl, aspect='auto', origin='lower',
                    extent=[fc_ref_vals[0], fc_ref_vals[-1],
                            q_max_vals[0]-0.5, q_max_vals[-1]+0.5],
                    vmin=0, cmap='viridis')
    ax.set_xscale('log')
    ax.set_xlabel('fc_ref (Hz)')
    ax.set_title(f'depth_kl  {name}')
    plt.colorbar(im, ax=ax, fraction=0.04)
axes[0].set_ylabel('q_max')
fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "02_depth_kl_heatmap.png"), dpi=110)
plt.close(fig)
print(f"  → plots/02_depth_kl_heatmap.png saved")
print()


# ── Analysis 3 — K_p sensitivity ──────────────────────────────────────────────
print("=" * 78)
print("Analysis 3 — K_p sensitivity (variance of F across fc_ref per K_p)")
print("=" * 78)
# For each K_p, std of F across fc_ref (averaged across q_max)
F_std_by_kp = np.zeros((len(kp_vals), len(q_max_vals)))
for ki in range(len(kp_vals)):
    for qi in range(len(q_max_vals)):
        F_std_by_kp[ki, qi] = float(np.nanstd(F_agg[ZETA, qi, ki, :]))
print(f"  std(F_agg vs fc_ref) for ζ:")
print(f"  {'K_p':>6}  " + "  ".join(f"{'q='+str(q):>7}" for q in q_max_vals)
      + f"  {'mean':>7}")
for ki, kp in enumerate(kp_vals):
    row = "  ".join(f"{F_std_by_kp[ki, qi]:7.3f}" for qi in range(len(q_max_vals)))
    print(f"  {kp:6.2f}  {row}  {np.nanmean(F_std_by_kp[ki]):7.3f}")
ki_stable = int(np.argmin(np.nanmean(F_std_by_kp, axis=1)))
print(f"\n  → most stable K_p (smallest mean std): K_p={kp_vals[ki_stable]}")
print()


# ── Analysis 4 — signal separation ────────────────────────────────────────────
print("=" * 78)
print("Analysis 4 — F_zeta / F_noise and F_zeta / F_poisson")
print("=" * 78)
# White noise rarely locks → F_noise is mostly NaN.  That itself is a
# strong "noise is null" signal and we report that directly.  For the
# zeta-vs-poisson comparison, focus on cells where both are valid.
ratio_zp = np.where((F_agg[POISS] > 0) & ~np.isnan(F_agg[POISS]) & ~np.isnan(F_agg[ZETA]),
                    F_agg[ZETA] / F_agg[POISS], np.nan)
ratio_zn = np.where((F_agg[NOISE] > 0) & ~np.isnan(F_agg[NOISE]) & ~np.isnan(F_agg[ZETA]),
                    F_agg[ZETA] / F_agg[NOISE], np.nan)

# Cells where noise actually has a measurable F (rare):
n_noise_valid = int(np.sum(~np.isnan(F_agg[NOISE])))
n_zeta_valid  = int(np.sum(~np.isnan(F_agg[ZETA])))
n_poiss_valid = int(np.sum(~np.isnan(F_agg[POISS])))
print(f"  cells with valid F: ζ={n_zeta_valid}/3000, poiss-FM={n_poiss_valid}/3000, "
      f"noise={n_noise_valid}/3000")
print(f"    (white noise rarely locks → mostly NaN — this is correct null behaviour)")
print()

# Largest ζ vs Poisson-FM separation
if not np.all(np.isnan(ratio_zp)):
    flat_idx = np.nanargmax(np.abs(np.log(np.abs(ratio_zp))))
    qi, ki, fi = np.unravel_index(flat_idx, ratio_zp.shape)
    print(f"  max |log(F_zeta/F_poiss)| at q_max={q_max_vals[qi]}, K_p={kp_vals[ki]}, "
          f"fc_ref={fc_ref_vals[fi]:.2f}:")
    print(f"    F_zeta  = {F_agg[ZETA, qi, ki, fi]:.3f}")
    print(f"    F_poiss = {F_agg[POISS, qi, ki, fi]:.3f}")
    print(f"    ratio   = {ratio_zp[qi, ki, fi]:.3f}")
    print()

# How close to ratio=1 (no separation) does it get?
print(f"  ζ/poiss-FM ratio statistics across cells where both are valid:")
print(f"    min      = {float(np.nanmin(ratio_zp)):.3f}")
print(f"    median   = {float(np.nanmedian(ratio_zp)):.3f}")
print(f"    max      = {float(np.nanmax(ratio_zp)):.3f}")
print(f"    fraction with ratio > 1.5 (ζ ≥ 50% more clustered): "
      f"{float(np.nanmean(ratio_zp > 1.5)):.3f}")
print(f"    fraction with ratio < 0.67 (ζ ≥ 33% less clustered): "
      f"{float(np.nanmean(ratio_zp < 0.67)):.3f}")
print()

# Where is F_zeta < 1?  (GUE signature)
F_zeta = F_agg[ZETA]
sub_mask = (F_zeta < 1.0) & ~np.isnan(F_zeta)
print(f"  cells where F_zeta < 1 (GUE-like sub-Poisson signature):")
print(f"    count: {int(sub_mask.sum())} of {n_zeta_valid} valid cells")
if sub_mask.any():
    sub_indices = list(zip(*np.where(sub_mask)))
    for qi_, ki_, fi_ in sub_indices[:10]:
        print(f"    q_max={q_max_vals[qi_]}, K_p={kp_vals[ki_]}, "
              f"fc_ref={fc_ref_vals[fi_]:.2f}, F={F_zeta[qi_, ki_, fi_]:.3f}")
    if len(sub_indices) > 10:
        print(f"    ... and {len(sub_indices)-10} more")
else:
    print(f"    none — ζ is super-Poisson everywhere in the swept space")
print()


# ── Analysis 5 — depth histogram across fc_ref ────────────────────────────────
print("=" * 78)
print("Analysis 5 — depth-of-events distribution across fc_ref (ζ, q_max=8, K_p=0.10)")
print("=" * 78)
qi = list(q_max_vals).index(8) if 8 in q_max_vals else len(q_max_vals)//2
ki = list(kp_vals).index(0.10) if 0.10 in kp_vals else len(kp_vals)//2
# depth_evt[ZETA, qi, ki, :, :]  ⇒  (n_fc, max_depth)
hist = depth_evt[ZETA, qi, ki]   # (fc_ref, max_depth)
totals = hist.sum(axis=1, keepdims=True)
totals_safe = np.where(totals > 0, totals, 1)
hist_norm = hist / totals_safe
peak_depth_per_fc = np.argmax(hist_norm, axis=1)
print(f"  peak depth per fc_ref (ζ, q_max=8, K_p=0.10):")
print(f"  {'fc_ref':>7}  {'peak_depth':>10}  {'frac':>5}")
for fi in range(0, len(fc_ref_vals), 5):
    if totals[fi, 0] > 0:
        print(f"  {fc_ref_vals[fi]:7.1f}  {peak_depth_per_fc[fi]:10d}  "
              f"{hist_norm[fi, peak_depth_per_fc[fi]]:5.2f}")
    else:
        print(f"  {fc_ref_vals[fi]:7.1f}  {'(no events)':>10}")
print()
# Does peak depth shift with fc_ref?
valid_mask = totals.flatten() > 0
if valid_mask.sum() > 5:
    # Trend: correlate fc_ref index with peak depth
    fc_used = fc_ref_vals[valid_mask]
    pd_used = peak_depth_per_fc[valid_mask]
    if pd_used.std() > 0:
        corr = float(np.corrcoef(np.log10(fc_used), pd_used.astype(float))[0, 1])
        print(f"  correlation(log10(fc_ref), peak_depth) = {corr:+.3f}")
        if abs(corr) > 0.3:
            print(f"  → peak depth shifts with fc_ref → likely chirp artifact")
        else:
            print(f"  → peak depth roughly constant → consistent with intrinsic structure")
print()


# ── Investigate the F_zeta < 1 cell (and its surroundings) ────────────────────
print("=" * 78)
print("Bonus — characterising any cells with F_zeta < 1 (sub-Poisson candidates)")
print("=" * 78)
sub_idx = np.where((F_agg[ZETA] < 1.0) & ~np.isnan(F_agg[ZETA]))
for qi_, ki_, fi_ in zip(*sub_idx):
    fp = F_agg[POISS, qi_, ki_, fi_]
    print(f"  q_max={q_max_vals[qi_]:>2}  K_p={kp_vals[ki_]:.2f}  fc_ref={fc_ref_vals[fi_]:6.2f}  "
          f"F_zeta={F_agg[ZETA, qi_, ki_, fi_]:.3f}  "
          f"F_poiss={fp:.3f}  "
          f"n_evt={int(n_evt[ZETA, qi_, ki_, fi_]):4d}  "
          f"n_lock={int(n_lock[ZETA, qi_, ki_, fi_]):3d}  "
          f"depth_kl={depth_kl[ZETA, qi_, ki_, fi_]:.3f}")
    if not np.isnan(fp):
        print(f"      ζ vs Poisson-FM at same cell: {F_agg[ZETA, qi_, ki_, fi_]/fp:.3f}× "
              f"({'ζ MORE clustered' if F_agg[ZETA, qi_, ki_, fi_]>fp else 'ζ LESS clustered'})")
print()


# ── Summary ───────────────────────────────────────────────────────────────────
print("=" * 78)
print("Summary")
print("=" * 78)
print(f"  total cells:               {F_agg[ZETA].size}")
print(f"  valid F_zeta:              {int((~np.isnan(F_agg[ZETA])).sum())}")
print(f"  valid F_poiss:             {int((~np.isnan(F_agg[POISS])).sum())}")
print(f"  valid F_noise:             {int((~np.isnan(F_agg[NOISE])).sum())}  (mostly nan: noise rarely locks → null OK)")
print(f"  median F_zeta:             {float(np.nanmedian(F_agg[ZETA])):.3f}")
print(f"  median F_poiss:            {float(np.nanmedian(F_agg[POISS])):.3f}")
print(f"  median ζ/poiss ratio:      {float(np.nanmedian(F_agg[ZETA]/np.where(F_agg[POISS]>0, F_agg[POISS], np.nan))):.3f}")
print(f"  ζ/poiss > 1.5 fraction:    {float(np.nanmean((F_agg[ZETA]/np.where(F_agg[POISS]>0, F_agg[POISS], np.nan)) > 1.5)):.3f}")
print(f"  cells with F_zeta < 1:     {int(((F_agg[ZETA] < 1) & ~np.isnan(F_agg[ZETA])).sum())} of valid")
print(f"  most stable K_p:           {kp_vals[ki_stable]:.2f}")
print(f"  PNG plots:                 {PLOT_DIR}/")
