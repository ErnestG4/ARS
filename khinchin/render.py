"""Khinchin Landscape — Phase 2 renders R1-R6 (spec sec 5, 5b).

    python3 render.py phase1

Colour: 'berlin' (Crameri, perceptually uniform diverging) centred on log2 K0,
cool below Khinchin / warm above, neutral-dark at K0, achromatic grey for masked.
The rate field is 'cividis' (perceptually uniform, CVD-safe sequential).
"""
import json
import os
import textwrap
import sys
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
from PIL import Image

import kcore as kc
from compute import CONFIGS, DATA, HERE

warnings.filterwarnings('ignore', r'All-NaN|Mean of empty')
Image.MAX_IMAGE_PIXELS = None

REN = os.path.join(HERE, 'renders')
SURFACE, INK, INK2 = '#1a1a19', '#ffffff', '#c3c2b7'
SER1, SER2 = '#3987e5', '#d95926'
SPAN = 1.5                      # log2 K half-range about K0
VMIN, VMAX = kc.LOG2_K0 - SPAN, kc.LOG2_K0 + SPAN
KTICKS = [1.0, 1.5, 2.0, kc.KHINCHIN_K0, 4.0, 6.0]

plt.rcParams.update({
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE,
    'savefig.facecolor': SURFACE, 'text.color': INK,
    'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
    'axes.edgecolor': '#4a4a48', 'font.size': 9, 'axes.titlesize': 11,
    'figure.dpi': 140,
})


def caption(fig, text, width=175):
    """Footnote text, hard-wrapped: a single long line makes bbox_inches='tight'
    expand the canvas to fit it (it blew R1z out to 4964 px wide)."""
    fig.text(0.008, 0.012, '\n'.join(textwrap.wrap(text, width)),
             fontsize=7, color=INK2, va='bottom')


def cmap_K():
    c = matplotlib.colormaps['berlin'].copy()
    c.set_bad('#8a8a8a')
    return c


def cmap_rate():
    c = matplotlib.colormaps['cividis'].copy()
    c.set_bad('#8a8a8a')
    return c


def load(tag):
    d = os.path.join(DATA, 'derived')
    F = dict(
        log2K=np.load(os.path.join(d, f'log2K_{tag}.npy'), mmap_mode='r'),
        S1=np.load(os.path.join(d, f'S1_shadow_n64_{tag}.npy'), mmap_mode='r'),
        S2=np.load(os.path.join(d, f'S2_rate_{tag}.npy'), mmap_mode='r'),
        horizon=np.load(os.path.join(DATA, f'horizon_{tag}.npy')),
        quots=np.load(os.path.join(DATA, f'quotients_{tag}.npy'), mmap_mode='r'))
    F['cfg'] = CONFIGS[tag]
    B = F['cfg']['B']
    xi = kc.grid_offset(B, F['cfg']['offset'])
    F['xi_frac'] = float(xi >> (B - 53)) / float(1 << 53)   # 2^B overflows a float
    return F


def col_of_alpha(a, F):
    N = F['cfg']['N']
    return int(round(a * N - F['xi_frac']))


def alpha_of_col(i, F):
    return (i + F['xi_frac']) / F['cfg']['N']


def take(A, f):
    """Display reduction by STRIDE, not by averaging.

    Averaging f adjacent columns divides the per-column spread by sqrt(f), which is
    precisely the contrast these fields exist to show (and it silently made the
    standardised render look like a dead N(0,1/16) field). Subsampling keeps every
    displayed pixel an honest single column; the cost is that a flare in a skipped
    column is not shown, which the zooms cover at native resolution.
    """
    return np.asarray(A[:, ::max(1, f)], dtype=np.float32)


def anchor_log2K(key, D):
    seq = kc.anchor_sequence(key, D)
    v = np.full(D, np.nan, dtype=np.float32)
    la = np.array([kc.ilog2(a) for a in seq], dtype=np.float64)
    v[:len(seq)] = np.cumsum(la) / np.arange(1, len(seq) + 1)
    return v


def kbar(fig, im, ax, label='K_n  (geometric mean of a_1..a_n)'):
    cb = fig.colorbar(im, ax=ax, pad=0.012, extend='both', fraction=0.026)
    cb.set_ticks([np.log2(k) for k in KTICKS])
    cb.set_ticklabels([('K₀ = 2.6855' if abs(k - kc.KHINCHIN_K0) < 1e-9
                        else f'{k:g}') for k in KTICKS])
    cb.set_label(label, color=INK2)
    cb.ax.tick_params(colors=INK2)
    cb.outline.set_edgecolor('#4a4a48')
    return cb


def anchor_ticks(ax, F, lo=0.0, hi=1.0, y=None):
    """Anchor rules + labels, staggered so near-neighbours (e-2, sqrt3-1) don't collide."""
    items = sorted(((s['approx'], s['label']) for s in kc.ANCHORS.values()
                    if s['approx'] is not None and lo <= s['approx'] <= hi))
    prev, row = -1e9, 0
    for a, label in items:
        row = (row + 1) % 2 if (a - prev) < 0.05 * (hi - lo) else 0
        prev = a
        ax.axvline(a, color=INK, lw=0.6, alpha=0.45, ls=(0, (4, 3)))
        ax.annotate(label, xy=(a, y if y is not None else 0),
                    xytext=(0, 4 + 11 * row), textcoords='offset points',
                    ha='center', va='bottom', fontsize=7.5, color=INK)


# ----------------------------------------------------------------------------
def R1(F, tag, logdepth=False):
    D, N = F['log2K'].shape
    red = max(1, N // 4096)
    A = take(F['log2K'], red)
    suffix, rows = '', np.arange(D)
    if logdepth:
        rows = np.unique(np.round(np.logspace(0, np.log10(D), 900)).astype(int)) - 1
        A = A[rows]
        suffix = '_logdepth'
    fig, ax = plt.subplots(figsize=(15, 6.4))
    im = ax.imshow(A, aspect='auto', cmap=cmap_K(), norm=Normalize(VMIN, VMAX),
                   extent=[0, 1, D, 1] if not logdepth else None,
                   interpolation='nearest', origin='upper')
    if logdepth:
        ax.set_yticks(np.searchsorted(rows, [0, 9, 99, 999, D - 1]))
        ax.set_yticklabels(['1', '10', '100', '1000', str(D)])
        ax.set_xticks(np.linspace(0, A.shape[1], 6))
        ax.set_xticklabels([f'{v:g}' for v in np.linspace(0, 1, 6)])
    else:
        anchor_ticks(ax, F, y=D)
    ax.set_xlabel(r'$\alpha$'), ax.set_ylabel('continued-fraction depth  n')
    ax.set_title(f'R1 — the Khinchin landscape: $K_n(\\alpha)$ over the unit interval'
                 f'   [N={N}, D={D}, B={F["cfg"]["B"]}'
                 f'{", log depth" if logdepth else ""}]', color=INK)
    kbar(fig, im, ax)
    caption(fig,
             f'every {red}th column shown, no averaging — each pixel column is one real '
             f'column; a flare in a skipped column is not shown (see R3, native). '
             f'Depth axis runs downward: the field converges to K₀ with depth.')
    p = os.path.join(REN, f'R1_global{suffix}_{tag}.png')
    fig.savefig(p, bbox_inches='tight'), plt.close(fig)
    return p


def birkhoff_sd(F, max_lag=16):
    """sigma_B for log2 a under the Gauss map, DERIVED FROM THE FIELD (not a literal).

    The partial quotients are not independent, so the CLT scale for K_n is the
    Birkhoff/Green-Kubo sd  sigma_B^2 = Var(f) + 2*sum_k Cov(f, f o T^k),
    not the marginal Gauss-Kuzmin sd. Standardising by the marginal sd leaves
    sd(z) ~ 0.93 at every depth; this closes that gap. The autocovariances
    alternate and decay by the Gauss-Kuzmin-Wirsing ratio ~ -0.3036.
    """
    X = np.asarray(F['quots'][:512, ::4], dtype=np.float64)
    X = X[:, np.isfinite(X).all(0)]
    f = X - X.mean()
    var = float((f * f).mean())
    cov = [float((f[:-k] * f[k:]).mean()) for k in range(1, max_lag + 1)]
    return float(np.sqrt(var + 2.0 * sum(cov))), var, cov


def R1z(F, tag):
    """Depth-standardised companion: z = (log2 K_n - log2 K0) * sqrt(n) / sd_GK.

    Same field, monotone rescaling. K_n has spread ~ sd/sqrt(n), so the absolute
    render necessarily goes quiet with depth and hides everything below n~300.
    Dividing by that shrinking scale holds contrast constant at every depth, so a
    column that genuinely refuses K0 would grow as sqrt(n) and stand out as a
    saturated vein at ALL depths. This is the render that can answer whether the
    exceptional set is visible here.
    """
    D, N = F['log2K'].shape
    red = max(1, N // 4096)
    A = take(F['log2K'], red)
    n = np.arange(1, D + 1, dtype=np.float32)[:, None]
    sB, var, cov = birkhoff_sd(F)
    Z = (A - kc.LOG2_K0) * np.sqrt(n) / sB
    rows = np.unique(np.round(np.logspace(0, np.log10(D), 900)).astype(int)) - 1
    fig, ax = plt.subplots(figsize=(15, 6.4))
    im = ax.imshow(Z[rows], aspect='auto', cmap=cmap_K(), norm=Normalize(-3, 3),
                   interpolation='nearest')
    ax.set_yticks(np.searchsorted(rows, [0, 9, 99, 999, D - 1]))
    ax.set_yticklabels(['1', '10', '100', '1000', str(D)])
    ax.set_xticks(np.linspace(0, Z.shape[1], 6))
    ax.set_xticklabels([f'{v:g}' for v in np.linspace(0, 1, 6)])
    ax.set_xlabel(r'$\alpha$'), ax.set_ylabel('continued-fraction depth  n  (log)')
    ax.set_title('R1z — the same field, depth-standardised: '
                 r'$z=(\log_2 K_n-\log_2 K_0)\sqrt{n}/\sigma_{B}$', color=INK)
    cb = fig.colorbar(im, ax=ax, pad=0.012, extend='both', fraction=0.026)
    cb.set_label('z  (standard deviations from Khinchin)', color=INK2)
    cb.ax.tick_params(colors=INK2), cb.outline.set_edgecolor('#4a4a48')
    # statistic on the FULL field, not the subsampled display
    tot = hit = 0
    for c0 in range(0, N, 8192):
        blk = np.asarray(F['log2K'][D // 2:, c0:c0 + 8192], dtype=np.float32)
        zz = (blk - kc.LOG2_K0) * np.sqrt(np.arange(D // 2 + 1, D + 1,
                                                    dtype=np.float32))[:, None] / sB
        ok = np.isfinite(zz)
        tot += int(ok.sum()); hit += int((np.abs(zz) > 3)[ok].sum())
    frac = hit / max(1, tot)
    caption(fig,
             f'Constant contrast at every depth. Generic columns stay N(0,1) noise; a '
             f'column refusing K₀ would saturate as a vein at all depths. σ_B={sB:.4f} '
             f'is the Birkhoff sd derived from the field (marginal Gauss–Kuzmin sd is '
             f'{kc.GK_SD_LOG2A:.4f}; the quotients are correlated, lag-1 cov {cov[0]:+.4f}). '
             f'Fraction of |z|>3 below n=D/2: {frac*100:.3f}% vs 0.270% for N(0,1) — the '
             f'deficit is finite-n skewness of a heavy-right-tailed summand, which decays '
             f'with depth (tails 0.0015%/0.276% at n=16 → 0.053%/0.067% at n=2048). The '
             f'exceptional set has measure zero, so a Lebesgue-sampled grid contains no '
             f'such column — the veins of the exceptional set are absent BY CONSTRUCTION, '
             f'not by failure; they appear only as the inserted exact anchors in R2/R4.')
    p = os.path.join(REN, f'R1z_standardised_{tag}.png')
    fig.savefig(p, bbox_inches='tight'), plt.close(fig)
    return p, frac


def zoom(F, tag, centre, half, name, title, anchor_key=None, shallow=48):
    """Zoom panel: raw quotient magnitudes at shallow depth (where flare anatomy
    lives) above the K field on a LOG depth axis.

    A linear depth axis spends ~95% of its pixels on n>100, by which point a
    rational flare -- a giant quotient at n~2 -- has long since washed out of the
    running mean. The flare is only visible shallow, and it is visible in the raw
    quotients, not in K.
    """
    D, N = F['log2K'].shape
    c0 = max(0, col_of_alpha(centre - half, F))
    c1 = min(N, col_of_alpha(centre + half, F))
    ext = [alpha_of_col(c0, F), alpha_of_col(c1, F)]
    Araw = np.asarray(F['quots'][:shallow, c0:c1], dtype=np.float32)
    A = np.asarray(F['log2K'][:, c0:c1], dtype=np.float32)
    rows = np.unique(np.round(np.logspace(0, np.log10(D), 700)).astype(int)) - 1

    has_anchor = anchor_key is not None
    fig = plt.figure(figsize=(13, 7.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 2.1],
                          width_ratios=[30, 1] if has_anchor else [1, 0.0001],
                          hspace=0.16, wspace=0.02)

    axq = fig.add_subplot(gs[0, 0])
    imq = axq.imshow(Araw, aspect='auto', cmap=cmap_rate(), vmin=0, vmax=12,
                     extent=ext + [shallow, 1], interpolation='nearest')
    axq.set_ylabel('depth n')
    axq.set_title(title, color=INK)
    cbq = fig.colorbar(imq, ax=axq, pad=0.012, extend='max', fraction=0.026)
    cbq.set_label(r'$\log_2 a_n$  (quotient size)', color=INK2)
    cbq.ax.tick_params(colors=INK2), cbq.outline.set_edgecolor('#4a4a48')

    ax = fig.add_subplot(gs[1, 0], sharex=axq)
    im = ax.imshow(A[rows], aspect='auto', cmap=cmap_K(), norm=Normalize(VMIN, VMAX),
                   extent=ext + [len(rows), 0], interpolation='nearest')
    ax.set_yticks([np.searchsorted(rows, v) for v in [0, 9, 99, 999, D - 1]])
    ax.set_yticklabels(['1', '10', '100', '1000', str(D)])
    ax.set_xlabel(r'$\alpha$'), ax.set_ylabel('depth  n   (log)')
    kbar(fig, im, ax)
    if has_anchor:
        for a_ in (axq, ax):
            a_.axvline(centre, color=INK, lw=0.7, alpha=0.5, ls=(0, (4, 3)))
        axa = fig.add_subplot(gs[1, 1])
        axa.imshow(anchor_log2K(anchor_key, D)[rows, None], aspect='auto', cmap=cmap_K(),
                   norm=Normalize(VMIN, VMAX), interpolation='nearest')
        axa.set_xticks([]), axa.set_yticks([])
        axa.set_title('exact\nanchor', fontsize=7.5, color=INK)
        for sp in axa.spines.values():
            sp.set_edgecolor(INK), sp.set_linewidth(0.8)
    caption(fig,
            'Native grid resolution, no averaging. Top: raw quotient sizes -- a rational '
            'flare is one enormous quotient at small n, inherited from the nearby p/q, and '
            'it is gone from K within ~100 steps. Bottom: the same window in K on a log '
            'depth axis.' + (' The narrow strip is the anchor\'s EXACT closed-form CF, '
            'inserted for comparison -- it is NOT grid data: the exceptional set has '
            'measure zero and cannot appear in a Lebesgue-sampled field.'
            if has_anchor else ''))
    p_ = os.path.join(REN, f'{name}_{tag}.png')
    fig.savefig(p_, bbox_inches='tight'), plt.close(fig)
    return p_


def R5(F, tag):
    D, N = F['log2K'].shape
    idx = np.arange(0, N, max(1, N // 16384))
    K1024 = 2.0 ** np.asarray(F['log2K'][1023, idx], dtype=np.float32)
    a1 = np.rint(2.0 ** np.asarray(F['quots'][0, idx], dtype=np.float32)).astype(int)
    a64 = np.rint(2.0 ** np.asarray(F['quots'][63, idx], dtype=np.float32)).astype(int)
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.3))

    ax = axs[0]
    ax.hist(K1024[np.isfinite(K1024)], bins=90, range=(2.2, 3.25), color=SER1)
    ax.axvline(kc.KHINCHIN_K0, color=SER2, lw=2)
    ax.annotate(f'K₀ = {kc.KHINCHIN_K0:.6f}', xy=(kc.KHINCHIN_K0, 0.94),
                xycoords=('data', 'axes fraction'), xytext=(6, 0),
                textcoords='offset points', color=SER2, fontsize=8.5)
    ax.set_title(f'K at depth 1024 across {len(idx)} columns'), ax.set_xlabel('K')
    ax.set_ylabel('columns')

    for ax, samp, law, lab, ttl in (
            (axs[1], a1, lambda k: 1.0 / (k * (k + 1.0)), '1/(k(k+1))  exact',
             r'$a_1$  vs its exact law for a uniform grid'),
            (axs[2], a64, lambda k: np.log2(1 + 1 / (k * (k + 2.0))),
             r'Gauss-Kuzmin  $\log_2(1+\frac{1}{k(k+2)})$',
             r'$a_{64}$  vs Gauss-Kuzmin')):
        ks = np.arange(1, 13)
        obs = np.array([(samp == k).mean() for k in ks])
        ax.bar(ks - 0.19, obs, width=0.38, color=SER1, label='observed')
        ax.bar(ks + 0.19, [law(k) for k in ks], width=0.38, color=SER2, label=lab)
        ax.set_yscale('log'), ax.set_xlabel('k'), ax.set_ylabel('P(a = k)')
        ax.set_title(ttl), ax.legend(frameon=False, fontsize=7.5, labelcolor=INK2)
    fig.text(0.008, 0.005, 'Centre panel corrects spec sec 4 G1: on a Lebesgue-uniform '
             'grid a_1 follows 1/(k(k+1)), not Gauss-Kuzmin. Gauss-Kuzmin is the n→∞ '
             'law and is tested at n = 64 (right).', fontsize=7, color=INK2)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    p = os.path.join(REN, f'R5_companion_{tag}.png')
    fig.savefig(p, bbox_inches='tight'), plt.close(fig)
    return p


def R6(F, tag):
    D, N = F['log2K'].shape
    red = max(1, N // 2400)
    panels = [('K  (running geometric mean)', take(F['log2K'], red), cmap_K(),
               Normalize(VMIN, VMAX), 'K'),
              ('S1  running-min shadow of K  (n₀ = 64)', take(F['S1'], red),
               cmap_K(), Normalize(VMIN, VMAX), 'K'),
              ('S2  rate  #{k≤n : a_k ≥ 2} / n', take(F['S2'], red),
               cmap_rate(), Normalize(0, 1), 'rate')]
    dis = np.load(os.path.join(DATA, 'derived', f'disagree_{tag}.npy'))
    n = (len(dis) // red) * red
    dis_r = dis[:n].reshape(-1, red).mean(axis=1)   # rug: keep the density, not a stride

    fig, axs = plt.subplots(3, 1, figsize=(14, 11.5), sharex=True)
    for ax, (ttl, A, cm, nm, kind) in zip(axs, panels):
        im = ax.imshow(A, aspect='auto', cmap=cm, norm=nm, extent=[0, 1, D, 1],
                       interpolation='nearest')
        ax.set_title(ttl, color=INK, loc='left')
        ax.set_ylabel('depth  n')
        if kind == 'K':
            kbar(fig, im, ax)
        else:
            cb = fig.colorbar(im, ax=ax, pad=0.012, fraction=0.026)
            cb.set_label('fraction of steps with a ≥ 2', color=INK2)
            cb.ax.axhline(kc.GK_RATE_A_GE_2, color=SER2, lw=1.6)
            cb.ax.tick_params(colors=INK2), cb.outline.set_edgecolor('#4a4a48')
    axs[-1].set_xlabel(r'$\alpha$')
    anchor_ticks(axs[0], F, y=D)
    ax2 = axs[-1].inset_axes([0, -0.13, 1, 0.06])
    ax2.imshow(dis_r[None, :], aspect='auto', cmap='Greys_r', vmin=0, vmax=1,
               extent=[0, 1, 0, 1])
    ax2.set_yticks([]), ax2.set_xticks([])
    ax2.set_ylabel('disagree', rotation=0, ha='right', va='center', fontsize=7.5,
                   color=INK2, labelpad=6)
    fig.suptitle('R6 — triptych: running mean, running-min shadow, and a≥2 rate, '
                 'shared α axis', color=INK, y=0.995)
    caption(fig,
             'S1 is a DOWNWARD-BIASED shadow of liminf K, not liminf K: the running min '
             'from n₀ converges to the tail-inf (≤ liminf) and transient dips bias it '
             'low. Burn-in sensitivity: median shadow K = 2.255 (n₀=16) vs 2.455 (n₀=64). '
             'Rug = columns with K within 5% of K₀ but shadow below 0.75·K₀ — an '
             'ILLUSTRATION of where the running-mean and running-min axes part ways. '
             'S1 lives on the liminf-K axis; the butterfly\'s fine classification lives on '
             'the CF-boundedness axis; these are non-equivalent criteria and no identity '
             'is claimed here.')
    fig.tight_layout(rect=[0, 0.055, 1, 0.985])
    p = os.path.join(REN, f'R6_triptych_{tag}.png')
    fig.savefig(p, bbox_inches='tight'), plt.close(fig)
    return p


def masters(F, tag):
    """True 16-bit single-channel PNG masters of the raw fields, native resolution."""
    out = []
    meta = {}
    for name, A, lo, hi in (('K', F['log2K'], VMIN, VMAX),
                            ('S1', F['S1'], VMIN, VMAX),
                            ('S2', F['S2'], 0.0, 1.0)):
        X = np.asarray(A, dtype=np.float32)
        bad = ~np.isfinite(X)
        q = np.nan_to_num(np.clip((X - lo) / (hi - lo), 0, 1), nan=0.0)
        u = (q * 65534.0 + 1.0).astype(np.uint16)   # 0 reserved for masked
        u[bad] = 0
        p = os.path.join(REN, f'master16_{name}_{tag}.png')
        Image.fromarray(u, mode='I;16').save(p, optimize=False)
        meta[name] = dict(file=os.path.basename(p), shape=list(X.shape),
                          value_lo=float(lo), value_hi=float(hi),
                          encoding='v = lo + (px-1)/65534*(hi-lo); px==0 means masked',
                          quantity=('log2 K_n' if name in ('K', 'S1') else 'a>=2 rate'))
        out.append(p)
    json.dump(meta, open(os.path.join(REN, f'master16_{tag}_scaling.json'), 'w'), indent=2)
    return out


def R7(F, tag, ncols_generic=40, wide=14):
    """R7 — constructed exceptional atlas.

    The theorem forbids SAMPLING the exceptional set: a Lebesgue grid meets it with
    probability zero, at any N/D/B (see R1z). Nothing forbids EXHIBITING it. Left:
    columns drawn from the grid. Right: columns BUILT, not measured -- so their CFs
    are exact at every depth and no trust horizon applies. The a.e. plateau is
    sampled; the filigree is constructed; the figure says which is which.
    """
    D, N = F['log2K'].shape
    rows = np.unique(np.round(np.logspace(0, np.log10(D), 700)).astype(int)) - 1
    G = np.asarray(F['log2K'][:, ::max(1, N // ncols_generic)][:, :ncols_generic],
                   dtype=np.float32)
    cols = kc.constructed_columns(D)
    blocks, labels, finals, classes = [], [], [], []
    for label, cls, q in cols:
        v = np.full(D, np.nan, dtype=np.float32)
        lk = kc.running_log2K(q)
        v[:len(lk)] = lk
        blocks.append(np.repeat(v[:, None], wide, axis=1))
        labels.append(label), finals.append(lk[-1]), classes.append(cls)
    C = np.concatenate(blocks, axis=1)

    fig = plt.figure(figsize=(15.5, 7.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[ncols_generic, C.shape[1]], wspace=0.03)
    axg = fig.add_subplot(gs[0, 0])
    axg.imshow(G[rows], aspect='auto', cmap=cmap_K(), norm=Normalize(VMIN, VMAX),
               interpolation='nearest')
    axg.set_yticks([np.searchsorted(rows, v) for v in [0, 9, 99, 999, D - 1]])
    axg.set_yticklabels(['1', '10', '100', '1000', str(D)])
    axg.set_xticks([]), axg.set_ylabel('depth  n   (log)')
    axg.set_title(f'SAMPLED — {ncols_generic} columns of the Lebesgue grid\n'
                  'every one generic, a.e. → K₀', color=INK, fontsize=9.5)

    axc = fig.add_subplot(gs[0, 1], sharey=axg)
    im = axc.imshow(C[rows], aspect='auto', cmap=cmap_K(), norm=Normalize(VMIN, VMAX),
                    interpolation='nearest')
    axc.set_xticks([wide * (i + 0.5) for i in range(len(labels))])
    axc.set_xticklabels([f'{l}\nK={2**min(f, 40):.3g}' if f < 40 else f'{l}\nK=10^{f*0.30103:.0f}'
                         for l, f in zip(labels, finals)],
                        rotation=90, fontsize=6.8, color=INK2)
    axc.tick_params(labelleft=False)
    for i in range(1, len(labels)):
        axc.axvline(wide * i - 0.5, color=SURFACE, lw=1.2)
    axc.set_title('CONSTRUCTED — measure zero, NOT grid data\n'
                  'built sequences: exact CF at every depth, no trust horizon',
                  color=INK, fontsize=9.5)
    kbar(fig, im, axc)
    bounds = [i for i in range(1, len(classes)) if classes[i] != classes[i - 1]]
    for i in bounds:                      # class boundaries: brighter, wider rule
        axc.axvline(wide * i - 0.5, color=INK, lw=1.6, alpha=0.75)
    caption(fig,
            'R7 is the honest home for "veins that refuse": they cannot be sampled, so they '
            'are exhibited. Left is data; right is construction, and the two are never mixed '
            'in one axis. Bounded-type F_m are the Cantor sets of quotients ≤ m (Hensley / '
            'Jenkinson–Pollicott dimension theory); noble tails are eventually-all-1s; the '
            'growth classes diverge and saturate the warm end by design. No claim is made '
            'that any named real belongs to any of these classes.')
    p_ = os.path.join(REN, f'R7_atlas_{tag}.png')
    fig.savefig(p_, bbox_inches='tight'), plt.close(fig)
    return p_


def main(tag='phase1'):
    os.makedirs(REN, exist_ok=True)
    F = load(tag)
    zpath, zfrac = R1z(F, tag)
    print(f'  R1z: |z|>3 fraction below n=D/2 = {zfrac*100:.4f}%  (N(0,1): 0.2700%)')
    made = [R1(F, tag), R1(F, tag, logdepth=True), zpath,
            zoom(F, tag, kc.ANCHORS['phi']['approx'], 0.02, 'R2_noble',
                 'R2 — noble filigree: the quiet around 1/φ (badly approximable '
                 '⇒ no strong rational flares)', 'phi'),
            zoom(F, tag, 0.5, 0.01, 'R3_flare',
                 'R3 — anatomy of a rational flare at α = 1/2 '
                 '(short inherited prefix, then one enormous quotient)'),
            zoom(F, tag, kc.ANCHORS['e_m2']['approx'], 0.005, 'R4_slow',
                 'R4 — slow vein: the neighbourhood of e−2, whose own K diverges',
                 'e_m2'),
            R5(F, tag), R6(F, tag), R7(F, tag)]
    made += masters(F, tag)
    for p in made:
        print(f'  {os.path.getsize(p)/1e6:8.2f} MB  {p}')
    return made


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'phase1')
