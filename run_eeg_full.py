"""
EEG full-cohort analysis (extended from run_eeg_depth.py).

PhysioNet EEGMMIDB data was unpacked at S001..S031 (31 subjects, 14 records
each).  This script uses the analytical-NNS classifier on θ-band (4-8 Hz)
zero crossings across all 31 subjects, with the same channel/condition
protocol as run_eeg_depth.py.

Output (separate from the prior 3-subject run, which is preserved):
    data/eeg_full_results.json
    plots/28_eeg_full.png

The original prior run on S001..S003 reported KS_GUE ≈ 0.18 — 8× the
calibrator threshold (~0.022), i.e. NOT a clean Wigner GUE classification.
The 10× larger cohort here will tell us whether that 0.18 was a small-n
fluctuation or a stable property of the EEG zero-crossing process.
"""
import os, sys, json
from collections import defaultdict
import numpy as np
from scipy.signal import butter, sosfiltfilt
import pyedflib

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


PHYSIONET_DIR = os.path.join(THIS_DIR, "physionet.org",
                              "eeg-motor-movementimagery-dataset-1.0.0",
                              "files")
PLOT_DIR = os.path.join(THIS_DIR, "plots")
DATA_DIR = os.path.join(THIS_DIR, "data")

CHANNELS = ['Fcz.', 'Cz..', 'Pz..', 'Fp1.', 'Fp2.']
THETA_LO, THETA_HI = 4.0, 8.0
MIN_EVENTS = 200

CONDITIONS = {
    'rest_eyes_open':   ['R01'],
    'rest_eyes_closed': ['R02'],
    'motor_imagery':    ['R04', 'R05', 'R06'],
}


def theta_zero_crossings(sig, sr):
    sos = butter(4, [THETA_LO, THETA_HI], btype='band', fs=sr, output='sos')
    bp = sosfiltfilt(sos, sig)
    sc = (bp[:-1] < 0) & (bp[1:] >= 0)
    return (np.where(sc)[0] + 0.5) / sr


def load_eeg(subject, run):
    p = os.path.join(PHYSIONET_DIR, subject, f"{subject}{run}.edf")
    if not os.path.exists(p): return None, None
    f = pyedflib.EdfReader(p)
    sr = f.getSampleFrequency(0)
    labels = [f.getLabel(i) for i in range(f.signals_in_file)]
    chans = {}
    for ch in CHANNELS:
        if ch in labels:
            chans[ch] = f.readSignal(labels.index(ch))
    f.close()
    return chans, sr


def normalised_spacings(events):
    e = np.sort(np.asarray(events, dtype=np.float64))
    sp = np.diff(e)
    if sp.size == 0 or sp.mean() <= 0: return np.zeros(0)
    return sp / sp.mean()


def classify(spacings):
    if spacings.size < 5:
        return dict(n=int(spacings.size), best='insufficient')
    F_em = np.arange(1, spacings.size + 1) / spacings.size
    s = np.sort(spacings)
    ks_p = float(np.max(np.abs(F_em - nns_cdf_poisson(s))))
    ks_o = float(np.max(np.abs(F_em - nns_cdf_goe(s))))
    ks_u = float(np.max(np.abs(F_em - nns_cdf_gue(s))))
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=int(spacings.size), ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                gap=ks_o - ks_u, mass03=float((spacings < 0.3).mean()), best=best)


# ─── Subject discovery ────────────────────────────────────────────────────────
all_subjects = sorted(d for d in os.listdir(PHYSIONET_DIR)
                      if d.startswith('S') and os.path.isdir(os.path.join(PHYSIONET_DIR, d)))
SUBJECTS = []
for s in all_subjects:
    d = os.path.join(PHYSIONET_DIR, s)
    n_edf = len([f for f in os.listdir(d)
                 if f.endswith('.edf') and 'Zone' not in f])
    if n_edf >= 14:
        SUBJECTS.append(s)
print(f"Subjects with all 14 records: {len(SUBJECTS)}")
print(f"Used: {SUBJECTS}\n")


# ─── Per-segment classification ───────────────────────────────────────────────
print("=" * 110)
print("Per-segment EEG θ-band NNS classification")
print("=" * 110)
print(f"  {'subject':<7} {'channel':<5} {'condition':<18} "
      f"{'n':>6} {'KS_P':>5} {'KS_O':>5} {'KS_U':>5} {'gap':>6} {'m<0.3':>6} best")
results_segments = []
condition_pool = defaultdict(list)
channel_pool = defaultdict(list)
subject_pool = defaultdict(list)

for subj in SUBJECTS:
    for cond_name, runs in CONDITIONS.items():
        spacings_by_chan = {}
        for run in runs:
            chans, sr = load_eeg(subj, run)
            if chans is None: continue
            for ch, sig in chans.items():
                ev = theta_zero_crossings(sig, sr)
                if ev.size < 20: continue
                spacings_by_chan.setdefault(ch, []).append(normalised_spacings(ev))
        for ch, sp_list in spacings_by_chan.items():
            sp = np.concatenate(sp_list)
            if sp.size < MIN_EVENTS: continue
            cl = classify(sp)
            results_segments.append(dict(subject=subj, channel=ch,
                                         condition=cond_name, **cl,
                                         spacings=sp.tolist()))
            print(f"  {subj:<7} {ch:<5} {cond_name:<18} "
                  f"{cl['n']:>6} {cl['ks_p']:.3f} {cl['ks_o']:.3f} {cl['ks_u']:.3f} "
                  f"{cl['gap']:+6.3f} {cl['mass03']:.3f}  {cl['best']}")
            condition_pool[cond_name].append(sp)
            channel_pool[ch].append(sp)
            subject_pool[subj].append(sp)
print()


def agg_print(name, pool):
    if not pool: return None
    s = np.concatenate(pool)
    cl = classify(s)
    print(f"  {name:<28} n_seg={len(pool):>3} n={cl['n']:>7} "
          f"KS_P={cl['ks_p']:.3f} KS_O={cl['ks_o']:.3f} KS_U={cl['ks_u']:.3f} "
          f"gap={cl['gap']:+.3f} m<0.3={cl['mass03']:.3f} best={cl['best']}")
    return cl


print("=" * 110)
print("Aggregate by condition")
print("=" * 110)
agg_cond = {k: agg_print(k, v) for k, v in condition_pool.items()}
print()
print("=" * 110)
print("Aggregate by channel")
print("=" * 110)
agg_chan = {k: agg_print(k, v) for k, v in channel_pool.items()}
print()
print("=" * 110)
print("Aggregate by subject")
print("=" * 110)
agg_subj = {k: agg_print(k, v) for k, v in subject_pool.items()}
print()


# ─── Plot ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 41)
for ax, cond_name in zip(axes, CONDITIONS.keys()):
    pool = condition_pool.get(cond_name, [])
    if not pool: ax.set_title(f"{cond_name}: no data"); continue
    s = np.concatenate(pool)
    ax.hist(s, bins=bin_edges, density=True, alpha=0.55, color='C0', label=f"n={s.size}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.2, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.2, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.6, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
    cl = agg_cond.get(cond_name, {})
    ax.set_title(f"{cond_name}\nbest={cl.get('best','—')}, "
                 f"KS_GUE={cl.get('ks_u', 0):.3f}, m<0.3={cl.get('mass03', 0):.3f}",
                 fontsize=9)
    ax.set_xlabel('normalised spacing s')
    ax.grid(True, alpha=0.3)
axes[0].set_ylabel('P(s)')
axes[0].legend(fontsize=7, loc='upper right')
fig.suptitle(f"PhysioNet EEGMMIDB θ-band zero-crossings — full {len(SUBJECTS)}-subject cohort")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOT_DIR, "28_eeg_full.png"), dpi=110)
plt.close(fig)
print(f"  → plots/28_eeg_full.png")


out = dict(
    config=dict(channels=CHANNELS, conditions=CONDITIONS,
                theta_band=[THETA_LO, THETA_HI], min_events=MIN_EVENTS,
                n_subjects=len(SUBJECTS)),
    subjects=SUBJECTS,
    aggregates=dict(by_condition=agg_cond, by_channel=agg_chan, by_subject=agg_subj),
    segments=[{k: v for k, v in r.items() if k != 'spacings'} for r in results_segments],
)
with open(os.path.join(DATA_DIR, "eeg_full_results.json"), 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"  → data/eeg_full_results.json")
