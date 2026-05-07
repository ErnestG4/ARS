"""USGS earthquake event-time NNS classification.

5 years of M ≥ 4.5 events (USGS FDSN-WS public API).  Hypothesis test:
do earthquake event times exhibit any random-matrix universality class,
or do they follow the clustered-Poisson predicted by ETAS (epidemic-type
aftershock sequence) models?

Three analyses on the same data:

1. **Global**: all events worldwide pooled — NNS of inter-event times.
   Expected behavior: heavily Poisson-clustered (mass<0.3 ≫ Poisson)
   due to mainshock-aftershock sequences.

2. **By region**: split into ~10° lat/lon tiles, run per-tile NNS.
   Tests whether localised seismicity has different stats.

3. **By magnitude band**: M 4.5–5.0, M 5.0–5.5, M 5.5–6.0, M ≥ 6.0.
   Larger events are rarer; their inter-event times should approach
   pure Poisson if the ETAS effect washes out at high magnitude.

Output:
    data/earthquake_results.json
    plots/23_earthquake_nns.png
"""
import os, sys, json
from datetime import datetime, timezone
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from universality import (
    nns_poisson, nns_goe, nns_gue,
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    _ks_pvalue,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
INPUT = os.path.join(DATA, "usgs_M45_5yr.csv")


def parse_csv(path):
    """Return (times_seconds, mags, lats, lons) from USGS CSV."""
    times, mags, lats, lons = [], [], [], []
    with open(path) as f:
        header = f.readline().strip().split(',')
        i_t = header.index('time')
        i_m = header.index('mag')
        i_lat = header.index('latitude')
        i_lon = header.index('longitude')
        for line in f:
            cols = line.rstrip('\n').split(',')
            try:
                # USGS time format: 2024-12-30T23:56:29.977Z
                t = datetime.fromisoformat(cols[i_t].replace('Z', '+00:00'))
                times.append(t.timestamp())
                mags.append(float(cols[i_m]) if cols[i_m] else float('nan'))
                lats.append(float(cols[i_lat]) if cols[i_lat] else float('nan'))
                lons.append(float(cols[i_lon]) if cols[i_lon] else float('nan'))
            except Exception:
                continue
    return (np.array(times, dtype=np.float64),
            np.array(mags, dtype=np.float64),
            np.array(lats, dtype=np.float64),
            np.array(lons, dtype=np.float64))


def normalised_spacings(events):
    e = np.sort(np.asarray(events, dtype=np.float64))
    sp = np.diff(e)
    if sp.size == 0 or sp.mean() <= 0: return np.zeros(0)
    return sp / sp.mean()


def classify(spacings):
    if spacings.size < 50: return dict(n=int(spacings.size), best='insufficient')
    s = np.sort(spacings); n = s.size
    F_em = np.arange(1, n + 1) / n
    ks_p = float(np.max(np.abs(F_em - nns_cdf_poisson(s))))
    ks_o = float(np.max(np.abs(F_em - nns_cdf_goe(s))))
    ks_u = float(np.max(np.abs(F_em - nns_cdf_gue(s))))
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=n, ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                gap=ks_o - ks_u, mass03=float((spacings < 0.3).mean()), best=best)


print(f"Loading {INPUT}…")
times, mags, lats, lons = parse_csv(INPUT)
times.sort()
print(f"  {times.size} events parsed")
t_span_yrs = (times.max() - times.min()) / (365.25 * 86400)
print(f"  span: {t_span_yrs:.2f} years")
print(f"  rate: {times.size/t_span_yrs:.0f} events/year")
print(f"  magnitude range: [{mags.min():.1f}, {mags.max():.1f}]")
print()


# ─── 1. Global NNS ────────────────────────────────────────────────────────────
print("=" * 90)
print("1. Global event-time NNS (all events worldwide pooled)")
print("=" * 90)
sp_global = normalised_spacings(times)
cl_global = classify(sp_global)
print(f"  n={cl_global['n']}, KS_P={cl_global['ks_p']:.3f}, KS_GOE={cl_global['ks_o']:.3f}, "
      f"KS_GUE={cl_global['ks_u']:.3f}, gap={cl_global['gap']:+.3f}, "
      f"mass<0.3={cl_global['mass03']:.3f}, best={cl_global['best']}")
print()


# ─── 2. Magnitude bands ───────────────────────────────────────────────────────
print("=" * 90)
print("2. By magnitude band")
print("=" * 90)
print(f"  {'band':<12}  {'n_evt':>6}  {'n_pool':>7}  {'KS_P':>5}  {'KS_O':>5}  "
      f"{'KS_U':>5}  {'gap':>6}  {'mass<0.3':>8}  best")
mag_bands = [
    ('M 4.5–5.0', 4.5, 5.0),
    ('M 5.0–5.5', 5.0, 5.5),
    ('M 5.5–6.0', 5.5, 6.0),
    ('M 6.0–7.0', 6.0, 7.0),
    ('M ≥ 7.0',   7.0, 99.0),
]
mag_results = {}
for name, lo, hi in mag_bands:
    mask = (mags >= lo) & (mags < hi)
    t = np.sort(times[mask])
    sp = normalised_spacings(t)
    cl = classify(sp)
    mag_results[name] = dict(cl=cl, spacings=sp, n_events=int(mask.sum()))
    if cl.get('best') == 'insufficient':
        print(f"  {name:<12}  {int(mask.sum()):>6}  insufficient")
    else:
        print(f"  {name:<12}  {int(mask.sum()):>6}  {cl['n']:>7}  "
              f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
              f"{cl['gap']:+6.3f}  {cl['mass03']:8.3f}  {cl['best']}")
print()


# ─── 3. By region (lat/lon tiles) ─────────────────────────────────────────────
print("=" * 90)
print("3. By 30° lat × 30° lon tile (only tiles with ≥ 500 events)")
print("=" * 90)
tile_lat = (np.floor(lats / 30) * 30).astype(int)
tile_lon = (np.floor(lons / 30) * 30).astype(int)
tile_id = tile_lat * 1000 + tile_lon
unique_tiles = np.unique(tile_id)

print(f"  {'tile':<22}  {'n_evt':>6}  {'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  "
      f"{'gap':>6}  {'mass<0.3':>8}  best")
tile_results = []
for tid in unique_tiles:
    mask = (tile_id == tid)
    if mask.sum() < 500: continue
    t = np.sort(times[mask])
    sp = normalised_spacings(t)
    cl = classify(sp)
    lat_lo = tid // 1000
    lon_lo = tid % 1000
    if lon_lo > 180: lon_lo -= 1000   # negative-lon tile
    tile_str = f'lat[{lat_lo:+d},{lat_lo+30:+d}] lon[{lon_lo:+d},{lon_lo+30:+d}]'
    tile_results.append(dict(tile=tile_str, n_events=int(mask.sum()),
                              cl=cl, spacings=sp))
    if cl.get('best') == 'insufficient':
        print(f"  {tile_str:<22}  {int(mask.sum()):>6}  insufficient")
    else:
        print(f"  {tile_str:<22}  {int(mask.sum()):>6}  {cl['ks_p']:5.3f}  "
              f"{cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
              f"{cl['gap']:+6.3f}  {cl['mass03']:8.3f}  {cl['best']}")
print()


# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey=True, sharex=True)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 41)

# Top row: global + 2 magnitude bands
panels = [('global', dict(cl=cl_global, spacings=sp_global, n_events=times.size))]
for name, lo, hi in mag_bands[:2]:
    panels.append((name, mag_results[name]))
for ax, (name, r) in zip(axes[0], panels):
    if r['cl'].get('best') == 'insufficient':
        ax.set_title(f"{name}: insufficient"); continue
    ax.hist(r['spacings'], bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"n={r['cl']['n']}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.2, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.6, label='GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.6)
    ax.set_title(f"{name}\nbest={r['cl']['best']}, mass<0.3={r['cl']['mass03']:.2f}",
                  fontsize=9)
    ax.grid(True, alpha=0.3)

# Bottom row: 3 highest-event-count tiles
top_tiles = sorted(tile_results, key=lambda x: -x['n_events'])[:3]
for ax, r in zip(axes[1], top_tiles):
    if r['cl'].get('best') == 'insufficient':
        ax.set_title(f"insufficient"); continue
    ax.hist(r['spacings'], bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"n={r['cl']['n']}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.4, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.2, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.6, label='GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.6)
    ax.set_title(f"{r['tile']}\nbest={r['cl']['best']}, mass<0.3={r['cl']['mass03']:.2f}",
                  fontsize=8)
    ax.grid(True, alpha=0.3)
axes[0,0].legend(fontsize=7, loc='upper right')
axes[0,0].set_ylabel('global / mag bands\nP(s)')
axes[1,0].set_ylabel('top regions\nP(s)')
axes[1,0].set_xlabel('s'); axes[1,1].set_xlabel('s'); axes[1,2].set_xlabel('s')
fig.suptitle(f"USGS earthquake inter-event NNS, M≥4.5, 2020–2024 ({times.size} events)")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOTS, "23_earthquake_nns.png"), dpi=110)
plt.close(fig)
print(f"  → plots/23_earthquake_nns.png")


# Save results
out = dict(
    n_events=int(times.size),
    span_years=float(t_span_yrs),
    global_nns=cl_global,
    by_magnitude={k: v['cl'] for k, v in mag_results.items()},
    by_tile=[
        {'tile': r['tile'], 'n_events': r['n_events'], **r['cl']}
        for r in tile_results
    ],
)
with open(os.path.join(DATA, "earthquake_results.json"), 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"  → data/earthquake_results.json")
