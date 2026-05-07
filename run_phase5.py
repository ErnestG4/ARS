"""
Phase 5 — tonight's run list.  Wider cross-signal application of the
calibrated analytical-passage-time NNS metric, plus EEG event-time NNS.

Sources:
    Local synthesis (instantaneous):
        - Liouville function support (n with λ(n) = +1)
        - Twin prime lower members up to 10^7
        - Gaussian prime norms up to 10^5
        - Random prime-density control (Poisson with intensity 1/log(n))

    Odlyzko zero tables (downloaded):
        - zeros1: first 100,000 ζ zeros (height 14 → 75k)
        - zeros6: first 2,001,052 ζ zeros (height 14 → 1.13M)

    PhysioNet EEG (downloaded):
        - S001R01.edf: 64-channel 160-Hz rest recording, 61 s

Methods:
    - Frequency-list signals (ζ, primes, eigenvalues, etc.):
      analytical passage-time NNS via per-PLL framework
    - EEG zero-crossings: direct NNS of event times
"""
import os, sys, time
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')
DATA = os.path.join(THIS_DIR, "data")

from pll_bank import farey_rationals
from universality import (
    nns_poisson, nns_goe, nns_gue,
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    _ks_pvalue,
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PLOT_DIR = os.path.join(THIS_DIR, "plots")

SR_DEFAULT = 44100.0
DUR_DEFAULT = 300.0
FC_REF_DEFAULT = 115.55
Q_MAX = 8
LOCK_CONFIRM_S = 20e-3
TONGUE_PREFAC  = 0.05
TRANSIENT_S = 0.500


def analytical_nns(t_n_array, fc_ref, q_max, dur_s, transient_s,
                    lock_confirm_s, tongue_prefac, sr, min_events=10,
                    enforce_sr_cap=False):
    pairs = farey_rationals(q_max)
    pooled = []
    info = []
    for p, q in pairs:
        f_pll = fc_ref * p / q
        if f_pll <= 5.0: continue
        if enforce_sr_cap and f_pll >= sr * 0.45: continue   # PLL nyquist constraint, off by default for analytical
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


def direct_nns(events):
    """Pooled NNS of a single point process — sort, normalise spacings by mean."""
    e = np.sort(np.asarray(events, dtype=np.float64))
    sp = np.diff(e)
    if sp.size == 0 or sp.mean() <= 0: return np.zeros(0)
    return sp / sp.mean()


def ks_to(s, theory_cdf):
    s = np.sort(np.asarray(s, dtype=np.float64))
    n = s.size
    if n < 5: return float('nan')
    F_em = np.arange(1, n + 1) / n
    return float(np.max(np.abs(F_em - theory_cdf(s))))


def classify(pooled):
    if pooled.size < 5:
        return dict(ks_p=np.nan, ks_o=np.nan, ks_u=np.nan,
                    best='insufficient', mass03=np.nan, gap=np.nan, n=pooled.size)
    ks_p = ks_to(pooled, nns_cdf_poisson)
    ks_o = ks_to(pooled, nns_cdf_goe)
    ks_u = ks_to(pooled, nns_cdf_gue)
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(ks_p=ks_p, ks_o=ks_o, ks_u=ks_u, best=best,
                mass03=float((pooled < 0.3).mean()),
                gap=ks_o - ks_u, n=pooled.size)


# ──────────────────────────────────────────────────────────────────────────────
# 1. LOCAL SYNTHESIS
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 100)
print("Local synthesis")
print("=" * 100)

def primes_up_to(N):
    s = np.ones(N + 1, dtype=bool); s[0] = s[1] = False
    for i in range(2, int(np.sqrt(N)) + 1):
        if s[i]: s[i*i::i] = False
    return np.where(s)[0]

print("  primes_up_to(10**7) …")
t0 = time.perf_counter()
primes = primes_up_to(10**7)
print(f"    {primes.size} primes up to 10^7  ({time.perf_counter()-t0:.1f}s)")

# Twin primes: lower members p such that p+2 also prime
mask = np.zeros(10**7 + 3, dtype=bool); mask[primes] = True
twin_lower = primes[mask[primes + 2]]
print(f"  twin primes (lower members) up to 10^7: {twin_lower.size} pairs")

# Liouville function: λ(n) = (-1)^Ω(n) where Ω = # prime factors with multiplicity
# Use sieve to compute Ω(n) up to N, then partition
def liouville_signs(N):
    omega = np.zeros(N + 1, dtype=np.int32)
    for p in primes_up_to(N):
        for k in range(1, 30):
            pk = p ** k
            if pk > N: break
            omega[pk::pk] += 1
    omega[0] = 0
    lam = np.where(omega % 2 == 0, 1, -1)
    lam[0] = 0
    return lam

print("  liouville signs up to 10**5 …")
t0 = time.perf_counter()
lam = liouville_signs(10**5)
liouville_plus = np.where(lam == 1)[0]
liouville_minus = np.where(lam == -1)[0]
print(f"    +1 positions: {liouville_plus.size}, −1 positions: {liouville_minus.size}  "
      f"({time.perf_counter()-t0:.1f}s)")

# Gaussian prime norms: a²+b² = p with p prime ≡ 1 (mod 4), or |a| or |b| prime ≡ 3 (mod 4)
print("  gaussian prime norms up to 10**5 …")
t0 = time.perf_counter()
norm_max = 10**5
norms = set()
for p in primes:
    if p > norm_max: break
    if p % 4 == 1:
        # p = a² + b²; norm of the Gaussian prime = p
        norms.add(int(p))
    elif p % 4 == 3:
        # |a| = p, b = 0 (or vice versa), norm = p²
        if p * p <= norm_max: norms.add(int(p * p))
norms.add(2)   # 2 = (1+i)(1-i), norm = 2
gauss_norms = np.sort(np.array(sorted(norms), dtype=np.float64))
print(f"    {gauss_norms.size} distinct Gaussian prime norms ≤ 10^5  "
      f"({time.perf_counter()-t0:.1f}s)")

# Random prime-density control: Poisson process with intensity 1/log(n)
print("  random prime-density Poisson control …")
rng = np.random.default_rng(0)
N_target = primes[primes <= 10000].size   # ~1229 primes up to 10000
density_pts = []
n = 2.0
while n < 10000 and len(density_pts) < N_target * 2:
    intensity = 1.0 / np.log(max(n, 2))
    gap = rng.exponential(1.0 / intensity)
    n += gap
    density_pts.append(n)
poisson_density_match = np.array(density_pts[:N_target], dtype=np.float64)
print(f"    {poisson_density_match.size} Poisson-density control points  "
      f"(matches {N_target} primes ≤ 10000)")
print()


# ──────────────────────────────────────────────────────────────────────────────
# 2. ODLYZKO TABLES
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 100)
print("Loading Odlyzko zero tables")
print("=" * 100)
zeros1 = np.loadtxt(os.path.join(DATA, "odlyzko_zeros1.txt"))
zeros6 = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"))
print(f"  zeros1: {zeros1.size} zeros, range [{zeros1[0]:.2f}, {zeros1[-1]:.2f}]")
print(f"  zeros6: {zeros6.size} zeros, range [{zeros6[0]:.2f}, {zeros6[-1]:.2f}]")
# For the height-dependence test, take the first 50k vs last 50k of zeros6
zeros6_low  = zeros6[:50000]
zeros6_high = zeros6[-50000:]
print(f"    low chunk:  range [{zeros6_low[0]:.2f}, {zeros6_low[-1]:.2f}]")
print(f"    high chunk: range [{zeros6_high[0]:.2f}, {zeros6_high[-1]:.2f}]")
print()


# ──────────────────────────────────────────────────────────────────────────────
# 3. EEG (PhysioNet)
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 100)
print("EEG zero-crossings in θ band (4–8 Hz)")
print("=" * 100)
import pyedflib
from scipy.signal import butter, sosfiltfilt

f = pyedflib.EdfReader(os.path.join(DATA, "physionet_S001R01.edf"))
chans = f.signals_in_file
sr_eeg = f.getSampleFrequency(0)
duration = f.getFileDuration()
# Pick Fcz (frontal-central), a common θ-band site
labels = [f.getLabel(i) for i in range(chans)]
chan_idx = labels.index('Fcz.') if 'Fcz.' in labels else 0
sig_eeg = f.readSignal(chan_idx)
f.close()
print(f"  channel: {labels[chan_idx]} ({chan_idx})  sr={sr_eeg} Hz  dur={duration} s")
print(f"  raw RMS = {np.sqrt(np.mean(sig_eeg.astype(np.float64)**2)):.2f} µV")

# Bandpass 4–8 Hz
sos = butter(4, [4.0, 8.0], btype='band', fs=sr_eeg, output='sos')
sig_theta = sosfiltfilt(sos, sig_eeg)
print(f"  θ-band RMS = {np.sqrt(np.mean(sig_theta**2)):.2f} µV")

# Zero-crossings (positive-going)
sign_change = (sig_theta[:-1] < 0) & (sig_theta[1:] >= 0)
zc_idx = np.where(sign_change)[0]
zc_times = (zc_idx + 0.5) / sr_eeg   # in seconds
print(f"  positive-going zero crossings: {zc_times.size} events over {duration} s "
      f"(≈ {zc_times.size/duration:.2f} Hz, expected ~6 Hz centre of θ band)")
print()


# ──────────────────────────────────────────────────────────────────────────────
# 4. CLASSIFICATION
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 100)
print("Phase 5 classification")
print("=" * 100)

# Frequency-list signals — apply per-PLL passage-time framework
freq_list_signals = [
    ('ζ Odlyzko zeros1[1..1000]',       zeros1[:1000],        FC_REF_DEFAULT),
    ('ζ Odlyzko zeros1[first 10000]',   zeros1[:10000],       FC_REF_DEFAULT * 5),
    ('ζ Odlyzko zeros1[first 100000]',  zeros1,               FC_REF_DEFAULT * 50),
    ('ζ Odlyzko zeros6[low 50k]',       zeros6_low,           FC_REF_DEFAULT * 50),
    ('ζ Odlyzko zeros6[high 50k]',      zeros6_high,          FC_REF_DEFAULT * 5000),
    ('primes ≤ 10^4',                   primes[primes <= 10**4].astype(np.float64),  FC_REF_DEFAULT),
    ('primes ≤ 10^5',                   primes[primes <= 10**5].astype(np.float64),  FC_REF_DEFAULT * 5),
    ('primes ≤ 10^6',                   primes[primes <= 10**6].astype(np.float64),  FC_REF_DEFAULT * 50),
    ('twin primes (lower) ≤ 10^7',      twin_lower.astype(np.float64),               FC_REF_DEFAULT * 100),
    ('Liouville +1 positions ≤ 10^5',   liouville_plus.astype(np.float64),           FC_REF_DEFAULT),
    ('Liouville −1 positions ≤ 10^5',   liouville_minus.astype(np.float64),          FC_REF_DEFAULT),
    ('Gaussian prime norms ≤ 10^5',     gauss_norms,                                 FC_REF_DEFAULT * 5),
    ('Poisson density control',         poisson_density_match,                       FC_REF_DEFAULT),
]

results = {}
print(f"  {'signal':<38}  {'fc_ref':>9}  {'#PLLs':>5}  {'n':>6}  "
      f"{'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  {'gap':>6}  {'<0.3':>5}  best")
for name, t_n, fc_ref in freq_list_signals:
    if t_n.size < 100:
        print(f"  {name:<38}  insufficient input ({t_n.size})")
        continue
    pooled, info = analytical_nns(t_n, fc_ref, Q_MAX, DUR_DEFAULT, TRANSIENT_S,
                                    LOCK_CONFIRM_S, TONGUE_PREFAC, SR_DEFAULT)
    cl = classify(pooled)
    results[name] = dict(pooled=pooled, info=info, fc_ref=fc_ref, **cl)
    nplls = len(info)
    if cl['n'] < 50:
        print(f"  {name:<38}  {fc_ref:9.2f}  {nplls:5d}  {cl['n']:6d}  "
              f"insufficient pooled spacings")
    else:
        print(f"  {name:<38}  {fc_ref:9.2f}  {nplls:5d}  {cl['n']:6d}  "
              f"{cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  {cl['ks_u']:5.3f}  "
              f"{cl['gap']:+6.3f}  {cl['mass03']:5.3f}  {cl['best']}")
print()


# Direct NNS for EEG zero-crossings
print("  EEG zero-crossings (direct NNS):")
eeg_pooled = direct_nns(zc_times)
eeg_cl = classify(eeg_pooled)
print(f"    n={eeg_cl['n']}  KS_P={eeg_cl['ks_p']:.3f}  KS_O={eeg_cl['ks_o']:.3f}  "
      f"KS_U={eeg_cl['ks_u']:.3f}  gap={eeg_cl['gap']:+.3f}  mass<0.3={eeg_cl['mass03']:.3f}  "
      f"best={eeg_cl['best']}")
results['EEG θ zero-crossings (Fcz, rest)'] = dict(pooled=eeg_pooled, **eeg_cl,
                                                    fc_ref=None)
print()


# ──────────────────────────────────────────────────────────────────────────────
# 5. CROSS-SIGNAL TABLE
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 100)
print("Phase 5 cross-signal classification table")
print("=" * 100)
print(f"  {'signal':<40}  {'best':<8}  {'gap':>6}  {'KS_min':>6}  {'mass<0.3':>8}  n")
for name, r in results.items():
    if r.get('n', 0) < 50:
        print(f"  {name:<40}  insufficient")
        continue
    ks_min = min(r['ks_p'], r['ks_o'], r['ks_u'])
    print(f"  {name:<40}  {r['best']:<8}  {r['gap']:+6.3f}  {ks_min:6.3f}  "
          f"{r['mass03']:8.3f}  {r['n']}")
print()


# ──────────────────────────────────────────────────────────────────────────────
# 6. PLOT
# ──────────────────────────────────────────────────────────────────────────────
n_panels = sum(1 for r in results.values() if r.get('n', 0) >= 50)
ncols = 4
nrows = (n_panels + ncols - 1) // ncols
fig, axes = plt.subplots(nrows, ncols, figsize=(15, 3 * nrows), sharey=True, sharex=True)
axes = np.array(axes).reshape(-1)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 41)
i = 0
for name, r in results.items():
    if r.get('n', 0) < 50: continue
    ax = axes[i]; i += 1
    ax.hist(r['pooled'], bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"n={r['n']}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.2, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.2, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.6, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.4)
    ax.set_title(f"{name}\nbest={r['best']}, gap={r['gap']:+.3f}", fontsize=8)
    ax.grid(True, alpha=0.3)
for j in range(i, len(axes)): axes[j].axis('off')
axes[0].legend(fontsize=7, loc='upper right')
fig.suptitle(f"Phase 5 — cross-signal NNS classification")
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(os.path.join(PLOT_DIR, "16_phase5_cross_signal.png"), dpi=110)
plt.close(fig)
print(f"  → plots/16_phase5_cross_signal.png")

# Pickle results
import pickle
out_pkl = os.path.join(THIS_DIR, "phase5_results.pkl")
with open(out_pkl, 'wb') as f:
    pickle.dump({k: {kk: vv for kk, vv in r.items() if kk not in ('pooled', 'info')}
                  for k, r in results.items()}, f)
print(f"  → {out_pkl}")
