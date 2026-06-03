"""
LMFDB elliptic curve L-function family survey — Katz–Sarnak empirical test.

For each isogeny class of elliptic curves over Q with conductor ≤ 99
(from the user-supplied LMFDB dump), pick a representative curve,
compute the L-function root number and ~500 zeros via PARI, and run the
calibrated analytical passage-time NNS classifier.

The Katz–Sarnak conjecture predicts:
    root_number = +1 (even functional eqn)  →  orthogonal even (SO(even))
    root_number = -1 (odd functional eqn)   →  orthogonal odd  (SO(odd))
Both lie in the GOE class for the bulk pair-correlation but differ in
their behaviour near s=0.

Output:
    data/lmfdb_zeros.json     — per-curve metadata + zero list
    plots/17_lmfdb_family.png — NNS panels grouped by root number
    table printed to stdout
"""
import os, sys, time, json, re
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '$HOME/fmexplorer/riemann_explorer')

from pll_bank import farey_rationals
from universality import (
    nns_poisson, nns_goe, nns_gue,
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    _ks_pvalue,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import cypari2
pari = cypari2.Pari()


# ─── Config ───────────────────────────────────────────────────────────────────
INPUT_FILE  = os.path.join(THIS_DIR, "lmfdb_ec_curvedata_0507_1029.txt")
ZEROS_JSON  = os.path.join(THIS_DIR, "data", "lmfdb_zeros.json")
PLOT_DIR    = os.path.join(THIS_DIR, "plots")

# Analytical NNS framework — scaled down for L-function zeros which have
# lower mean spacing than ζ.  fc_ref=1 + q_max=8 gives PLL bands of
# width 75–4500 in zero-height units; with ~1 zero/unit at conductor≤100
# we get hundreds of zeros per band, plenty for NNS statistics.
SR        = 44100.0
DUR       = 300.0
FC_REF    = 1.0
Q_MAX     = 8
LOCK_CONFIRM_S = 20e-3
TONGUE_PREFAC  = 0.05
TRANSIENT_S    = 0.500

# Compute zeros up to height 200 — keeps PARI lfunzeros under ~1 s/curve
# even for conductor near 100.
ZERO_HEIGHT_LIMIT = 200.0

# Time budget per curve, beyond which we abort and skip.
PER_CURVE_TIMEOUT_S = 30.0


def analytical_nns(t_n_array, fc_ref, q_max, dur_s, transient_s,
                    lock_confirm_s, tongue_prefac, sr, min_events=10):
    pairs = farey_rationals(q_max)
    pooled = []
    info = []
    for p, q in pairs:
        f_pll = fc_ref * p / q
        if f_pll <= 0.5: continue
        elig = ((t_n_array >= (transient_s + 1.0) * f_pll) &
                (t_n_array <= (dur_s + 1.0) * f_pll))
        elig_t = np.sort(t_n_array[elig])
        threshold = lock_confirm_s * f_pll / (tongue_prefac * (2.0 / (p + q)) ** 2)
        qualifying = elig_t[elig_t >= threshold]
        if qualifying.size < min_events + 1: continue
        spacings = np.diff(qualifying) / f_pll
        if spacings.size == 0 or spacings.mean() <= 0: continue
        pooled.append(spacings / spacings.mean())
        info.append(dict(p=p, q=q, f_pll=f_pll, n_passages=int(qualifying.size)))
    pooled = np.concatenate(pooled) if pooled else np.zeros(0)
    return pooled, info


def ks_to(s, theory_cdf):
    s = np.sort(np.asarray(s, dtype=np.float64))
    n = s.size
    if n < 5: return float('nan')
    F_em = np.arange(1, n + 1) / n
    return float(np.max(np.abs(F_em - theory_cdf(s))))


def classify(pooled):
    if pooled.size < 50:
        return dict(n=int(pooled.size), best='insufficient')
    ks_p = ks_to(pooled, nns_cdf_poisson)
    ks_o = ks_to(pooled, nns_cdf_goe)
    ks_u = ks_to(pooled, nns_cdf_gue)
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=int(pooled.size), ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                gap=ks_o - ks_u, mass03=float((pooled < 0.3).mean()), best=best)


# ─── Parse the LMFDB curve dump ───────────────────────────────────────────────
print("Parsing LMFDB curve dump …")
re_line = re.compile(
    r'"([\w.]+)"\s+"([\w.]+)"\s+(\d+)\s+(\d+)\s+\[[^\]]*\]\s+\d+\s+\[([^\]]+)\]'
)
curves_all = []
with open(INPUT_FILE) as f:
    for line in f:
        m = re_line.match(line.strip())
        if not m: continue
        label, klass, conductor, rank, ainvs_str = m.groups()
        ainvs = [int(x.strip()) for x in ainvs_str.split(",")]
        curves_all.append(dict(label=label, klass=klass,
                                 conductor=int(conductor), rank=int(rank),
                                 ainvs=ainvs))
print(f"  {len(curves_all)} curves loaded; "
      f"{len(set(c['klass'] for c in curves_all))} isogeny classes.")
print()


# Pick one representative per isogeny class — the lex-first curve in the class.
classes = {}
for c in curves_all:
    classes.setdefault(c['klass'], c)   # first wins (lex order from file)
reps = sorted(classes.values(), key=lambda c: (c['conductor'], c['klass']))
print(f"  {len(reps)} isogeny-class representatives.")
print()


# ─── Compute root numbers and zeros via PARI ──────────────────────────────────
print(f"Computing root numbers + zeros up to height {ZERO_HEIGHT_LIMIT} per curve…")
print(f"  {'#':>3}  {'label':<10}  {'cond':>5}  {'rank':>4}  {'rt#':>3}  "
      f"{'#zeros':>6}  {'cpu_s':>6}")
results_per_curve = []
t_total0 = time.perf_counter()
import sys
def _flush(): sys.stdout.flush()
for i, c in enumerate(reps):
    t0 = time.perf_counter()
    try:
        E = pari.ellinit(c['ainvs'])
        rt = int(pari.ellrootno(E))
        L = pari.lfuncreate(E)
        zeros = pari.lfunzeros(L, ZERO_HEIGHT_LIMIT)
        zeros = np.array([float(z) for z in zeros], dtype=np.float64)
    except Exception as e:
        print(f"  {i+1:>3}  {c['label']:<10}  {c['conductor']:>5}  "
              f"{c['rank']:>4}  ERR  {str(e)[:40]}", flush=True)
        continue
    dt = time.perf_counter() - t0
    if zeros.size < 50:
        print(f"  {i+1:>3}  {c['label']:<10}  {c['conductor']:>5}  "
              f"{c['rank']:>4}  {rt:>+3d}  {zeros.size:>6}  {dt:>6.1f}  "
              f"(too few zeros, skipping)", flush=True)
        continue
    print(f"  {i+1:>3}  {c['label']:<10}  {c['conductor']:>5}  "
          f"{c['rank']:>4}  {rt:>+3d}  {zeros.size:>6}  {dt:>6.1f}", flush=True)
    results_per_curve.append(dict(c, root_number=rt,
                                    zeros=zeros.tolist(), n_zeros=int(zeros.size)))
print(f"\n  total compute time: {(time.perf_counter()-t_total0)/60:.1f} min  "
      f"({len(results_per_curve)} curves)\n")


# Save the JSON
os.makedirs(os.path.dirname(ZEROS_JSON), exist_ok=True)
with open(ZEROS_JSON, 'w') as f:
    json.dump(results_per_curve, f)
print(f"  zeros saved to {ZEROS_JSON}\n")


# ─── Run the analytical NNS classifier per curve ──────────────────────────────
print("=" * 110)
print("Per-curve NNS classification")
print("=" * 110)
print(f"  {'label':<10}  {'cond':>4}  {'rt#':>3}  {'n_z':>5}  {'#PLLs':>5}  "
      f"{'n_pool':>7}  {'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  {'gap':>+6}  best")
for r in results_per_curve:
    zeros = np.array(r['zeros'])
    pooled, info = analytical_nns(zeros, FC_REF, Q_MAX, DUR, TRANSIENT_S,
                                    LOCK_CONFIRM_S, TONGUE_PREFAC, SR)
    cl = classify(pooled)
    r['classification'] = cl
    if cl.get('best') == 'insufficient':
        print(f"  {r['label']:<10}  {r['conductor']:>4}  {r['root_number']:>+3}  "
              f"{r['n_zeros']:>5}  {len(info):>5}  {cl['n']:>7}  "
              f"insufficient pooled")
    else:
        print(f"  {r['label']:<10}  {r['conductor']:>4}  {r['root_number']:>+3}  "
              f"{r['n_zeros']:>5}  {len(info):>5}  {cl['n']:>7}  "
              f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
              f"{cl['gap']:+6.3f}  {cl['best']}")
print()


# ─── Aggregate by root number ─────────────────────────────────────────────────
print("=" * 110)
print("Aggregate by root number — Katz–Sarnak family signature")
print("=" * 110)
def aggregate_pool(group):
    arrs = []
    for r in group:
        if r.get('classification', {}).get('best') == 'insufficient': continue
        zeros = np.array(r['zeros'])
        pooled, _ = analytical_nns(zeros, FC_REF, Q_MAX, DUR, TRANSIENT_S,
                                     LOCK_CONFIRM_S, TONGUE_PREFAC, SR)
        if pooled.size > 50: arrs.append(pooled)
    return np.concatenate(arrs) if arrs else np.zeros(0)


print(f"  {'group':<24}  {'n_curves':>8}  {'n_pooled':>9}  "
      f"{'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  {'gap':>+6}  "
      f"{'mass<0.3':>8}  best")
groups = {
    'all curves':        results_per_curve,
    'root_number = +1':  [r for r in results_per_curve if r['root_number'] == +1],
    'root_number = -1':  [r for r in results_per_curve if r['root_number'] == -1],
    'rank = 0':          [r for r in results_per_curve if r['rank'] == 0],
    'rank ≥ 1':          [r for r in results_per_curve if r['rank'] >= 1],
}
agg_results = {}
for name, group in groups.items():
    pooled = aggregate_pool(group)
    cl = classify(pooled)
    agg_results[name] = cl
    if cl.get('best') == 'insufficient':
        print(f"  {name:<24}  {len(group):>8}  insufficient")
    else:
        print(f"  {name:<24}  {len(group):>8}  {cl['n']:>9}  "
              f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
              f"{cl['gap']:+6.3f}  {cl['mass03']:8.3f}  {cl['best']}")
print()


# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 41)
group_to_plot = [
    ('all curves',       'C0'),
    ('root_number = +1', 'C1'),
    ('root_number = -1', 'C2'),
]
for ax, (name, _) in zip(axes, group_to_plot):
    pooled = aggregate_pool(groups[name])
    if pooled.size < 50:
        ax.set_title(f"{name}: insufficient"); continue
    ax.hist(pooled, bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"n={pooled.size}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.4, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.6, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
    cl = agg_results[name]
    ax.set_title(f"{name}\nbest={cl['best']}, gap={cl['gap']:+.3f}, mass<0.3={cl['mass03']:.3f}",
                  fontsize=9)
    ax.set_xlabel('normalised spacing s')
    ax.grid(True, alpha=0.3)
axes[0].set_ylabel('P(s)')
axes[0].legend(fontsize=7, loc='upper right')
fig.suptitle(f"LMFDB elliptic curve L-functions, conductor ≤ 99 — "
              f"Katz–Sarnak family symmetry test")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOT_DIR, "17_lmfdb_family.png"), dpi=110)
plt.close(fig)
print(f"  → plots/17_lmfdb_family.png\n")


# Save the full results
out = dict(
    config=dict(fc_ref=FC_REF, q_max=Q_MAX, dur=DUR,
                  zero_height_limit=ZERO_HEIGHT_LIMIT),
    n_curves=len(results_per_curve),
    aggregates=agg_results,
    per_curve=[
        {**{k: v for k, v in r.items() if k != 'zeros'},
         'classification': r.get('classification', {})}
        for r in results_per_curve
    ],
)
out_json = os.path.join(THIS_DIR, "data", "lmfdb_results.json")
with open(out_json, 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"  → {out_json}")
