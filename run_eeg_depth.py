"""
Phase-5 EEG depth study.  Apply the analytical-NNS classifier to θ-band
(4–8 Hz) zero-crossings of the PhysioNet EEGMMIDB recordings.

Protocol (per user's brief):
    Subjects:    S001 … S005  (use whatever is locally available)
    Channels:    Fcz, Cz, Pz, Fp1, Fp2  (central line + frontal)
    Conditions:  R01  rest, eyes open
                 R02  rest, eyes closed
                 R04  motor imagery
                 R05  motor imagery / movement (mixed)
                 R06  motor imagery
    Band:        4–8 Hz (θ)
    Events:      positive-going zero-crossings of the band-passed signal
    Min events:  200 per (subject, channel, condition) segment

For each (subject × channel × condition) tuple compute KS distances
to Wigner GUE / GOE / Poisson, the gap, and the best fit.  Aggregate
by condition, channel, and (where data permits) by subject.

Output:
    data/eeg_results.json
    plots/18_eeg_depth.png
"""
import os, sys, json, glob
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


PHYSIONET_DIR = os.path.join(THIS_DIR, "physionet.org", "files",
                              "eegmmidb", "1.0.0")
PLOT_DIR = os.path.join(THIS_DIR, "plots")
DATA_DIR = os.path.join(THIS_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

CHANNELS  = ['Fcz.', 'Cz..', 'Pz..', 'Fp1.', 'Fp2.']
THETA_LO, THETA_HI = 4.0, 8.0
MIN_EVENTS = 200

CONDITIONS = {
    'rest_eyes_open':  ['R01'],
    'rest_eyes_closed': ['R02'],
    'motor_imagery':   ['R04', 'R05', 'R06'],
}


def theta_zero_crossings(sig, sr):
    sos = butter(4, [THETA_LO, THETA_HI], btype='band', fs=sr, output='sos')
    bandpassed = sosfiltfilt(sos, sig)
    sign_change = (bandpassed[:-1] < 0) & (bandpassed[1:] >= 0)
    zc_idx = np.where(sign_change)[0]
    return (zc_idx + 0.5) / sr


def load_eeg(subject, run):
    path = os.path.join(PHYSIONET_DIR, subject, f"{subject}{run}.edf")
    if not os.path.exists(path): return None, None, None
    f = pyedflib.EdfReader(path)
    sr = f.getSampleFrequency(0)
    labels = [f.getLabel(i) for i in range(f.signals_in_file)]
    chans = {}
    for ch in CHANNELS:
        if ch in labels:
            idx = labels.index(ch)
            chans[ch] = f.readSignal(idx)
    duration = f.getFileDuration()
    f.close()
    return chans, sr, duration


def normalised_spacings(events):
    e = np.sort(np.asarray(events, dtype=np.float64))
    sp = np.diff(e)
    if sp.size == 0 or sp.mean() <= 0: return np.zeros(0)
    return sp / sp.mean()


def classify(spacings):
    if spacings.size < 5:
        return dict(n=int(spacings.size), best='insufficient')
    F_em = np.arange(1, spacings.size + 1) / spacings.size
    s_sorted = np.sort(spacings)
    ks_p = float(np.max(np.abs(F_em - nns_cdf_poisson(s_sorted))))
    ks_o = float(np.max(np.abs(F_em - nns_cdf_goe(s_sorted))))
    ks_u = float(np.max(np.abs(F_em - nns_cdf_gue(s_sorted))))
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=int(spacings.size), ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                gap=ks_o - ks_u, mass03=float((spacings < 0.3).mean()), best=best)


# ─── Find available subjects ──────────────────────────────────────────────────
all_subjects = sorted([d for d in os.listdir(PHYSIONET_DIR)
                          if d.startswith('S') and os.path.isdir(
                              os.path.join(PHYSIONET_DIR, d))])
print(f"All subjects locally available: {len(all_subjects)} (S001…S{len(all_subjects):03d})")
# User's brief: start with 5 subjects.  Use the first N subjects who have all
# 14 .edf runs locally; right now S001..S003 are fully downloaded.
SUBJECTS_USED = []
for s in all_subjects:
    n_files = len([f for f in os.listdir(os.path.join(PHYSIONET_DIR, s))
                    if f.endswith('.edf')])
    if n_files >= 7: SUBJECTS_USED.append(s)
    if len(SUBJECTS_USED) >= 5: break
subjects_avail = SUBJECTS_USED
print(f"Subjects used (per brief): {subjects_avail}")
print()


# ─── Run per-cell analysis ────────────────────────────────────────────────────
print("=" * 110)
print("Per-segment EEG θ-band NNS classification")
print("=" * 110)
print(f"  {'subject':<7}  {'channel':<5}  {'condition':<18}  "
      f"{'n_events':>8}  {'KS_P':>5}  {'KS_O':>5}  {'KS_U':>5}  "
      f"{'gap':>6}  {'mass<0.3':>8}  best")

results_segments = []
condition_pool   = defaultdict(list)
channel_pool     = defaultdict(list)
subject_pool     = defaultdict(list)

for subj in subjects_avail:
    for cond_name, runs in CONDITIONS.items():
        # Compute per-run normalised spacings, pool them (NOT pool events first
        # — that introduces a huge synthetic gap between runs that dominates
        # the mean spacing and makes everything look near-zero).
        spacings_by_chan = {}
        events_count_by_chan = {}
        for run in runs:
            chans, sr, dur = load_eeg(subj, run)
            if chans is None: continue
            for ch, sig in chans.items():
                ev = theta_zero_crossings(sig, sr)
                if ev.size < 20:                # skip mostly-empty runs
                    continue
                run_sp = normalised_spacings(ev)
                spacings_by_chan.setdefault(ch, []).append(run_sp)
                events_count_by_chan[ch] = events_count_by_chan.get(ch, 0) + ev.size
        for ch, sp_list in spacings_by_chan.items():
            sp = np.concatenate(sp_list)
            if sp.size < MIN_EVENTS:
                print(f"  {subj:<7}  {ch:<5}  {cond_name:<18}  "
                      f"{sp.size:>8}  insufficient (<{MIN_EVENTS})")
                continue
            events = np.zeros(events_count_by_chan[ch])  # for the count column only
            cl = classify(sp)
            row = dict(subject=subj, channel=ch, condition=cond_name,
                        n_events=int(events.size), **cl, spacings=sp.tolist())
            results_segments.append(row)
            print(f"  {subj:<7}  {ch:<5}  {cond_name:<18}  "
                  f"{cl['n']:>8}  {cl['ks_p']:5.3f}  {cl['ks_o']:5.3f}  "
                  f"{cl['ks_u']:5.3f}  {cl['gap']:+6.3f}  {cl['mass03']:8.3f}  "
                  f"{cl['best']}")
            # Pool by axis
            condition_pool[cond_name].append(sp)
            channel_pool[ch].append(sp)
            subject_pool[subj].append(sp)
print()


# ─── Aggregate by axis ────────────────────────────────────────────────────────
def agg_print(name, pool):
    if not pool: return None
    s = np.concatenate(pool)
    cl = classify(s)
    print(f"  {name:<28}  n_segments={len(pool):>2}  n_pooled={cl['n']:>6}  "
          f"KS_P={cl['ks_p']:.3f}  KS_O={cl['ks_o']:.3f}  KS_U={cl['ks_u']:.3f}  "
          f"gap={cl['gap']:+.3f}  mass<0.3={cl['mass03']:.3f}  best={cl['best']}")
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


# ─── Compare conditions on the same subject ──────────────────────────────────
print("=" * 110)
print("Within-subject: condition deltas (KS_two-sample between conditions)")
print("=" * 110)
print(f"  {'subject':<7}  {'cond_A':<18}  {'cond_B':<18}  {'KS_two':>7}  {'p':>6}")
def ks_two_sample(a, b):
    s1, s2 = np.sort(a), np.sort(b)
    n1, n2 = s1.size, s2.size
    if n1 < 5 or n2 < 5: return float('nan'), float('nan')
    pts = np.concatenate([s1, s2])
    cdf1 = np.searchsorted(s1, pts, side='right') / n1
    cdf2 = np.searchsorted(s2, pts, side='right') / n2
    ks = float(np.max(np.abs(cdf1 - cdf2)))
    p = _ks_pvalue(ks, int(n1 * n2 / (n1 + n2)))
    return ks, p

for subj in subjects_avail:
    sub_cond = defaultdict(list)
    for r in results_segments:
        if r['subject'] != subj: continue
        sub_cond[r['condition']].append(r['spacings'])
    cond_pooled = {k: np.concatenate(v) if v else np.zeros(0) for k, v in sub_cond.items()}
    cond_names = list(cond_pooled.keys())
    for i in range(len(cond_names)):
        for j in range(i + 1, len(cond_names)):
            a, b = cond_pooled[cond_names[i]], cond_pooled[cond_names[j]]
            if a.size < 50 or b.size < 50: continue
            ks, p = ks_two_sample(a, b)
            print(f"  {subj:<7}  {cond_names[i]:<18}  {cond_names[j]:<18}  "
                  f"{ks:7.4f}  {p:6.3f}")
print()


# ─── Plot histograms grouped by condition ────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
s_grid = np.linspace(0.001, 4.0, 200)
bin_edges = np.linspace(0, 4, 41)
for ax, cond_name in zip(axes, CONDITIONS.keys()):
    pool = condition_pool.get(cond_name, [])
    if not pool: ax.set_title(f"{cond_name}: no data"); continue
    s = np.concatenate(pool)
    ax.hist(s, bins=bin_edges, density=True, alpha=0.55, color='C0',
            label=f"n={s.size}")
    ax.plot(s_grid, nns_poisson(s_grid), 'g--', lw=1.2, label='Poisson')
    ax.plot(s_grid, nns_goe(s_grid),     'C2-', lw=1.2, label='GOE')
    ax.plot(s_grid, nns_gue(s_grid),     'r-',  lw=1.6, label='Wigner GUE')
    ax.set_xlim(0, 4); ax.set_ylim(0, 1.2)
    cl = agg_cond.get(cond_name, {})
    ax.set_title(f"{cond_name}\nbest={cl.get('best','—')}, "
                  f"gap={cl.get('gap', 0):+.3f}, mass<0.3={cl.get('mass03', 0):.3f}",
                  fontsize=9)
    ax.set_xlabel('normalised spacing s')
    ax.grid(True, alpha=0.3)
axes[0].set_ylabel('P(s)')
axes[0].legend(fontsize=7, loc='upper right')
fig.suptitle(f"PhysioNet EEGMMIDB θ-band zero-crossings — NNS by condition")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(PLOT_DIR, "18_eeg_depth.png"), dpi=110)
plt.close(fig)
print(f"  → plots/18_eeg_depth.png\n")


# ─── Save JSON ────────────────────────────────────────────────────────────────
out = dict(
    config=dict(channels=CHANNELS, conditions=CONDITIONS,
                  theta_band=[THETA_LO, THETA_HI], min_events=MIN_EVENTS),
    subjects=subjects_avail,
    aggregates=dict(by_condition=agg_cond, by_channel=agg_chan, by_subject=agg_subj),
    segments=[{k: v for k, v in r.items() if k != 'spacings'} for r in results_segments],
)
out_json = os.path.join(DATA_DIR, "eeg_results.json")
with open(out_json, 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f"  → {out_json}")
