"""
Phase 13 Tier 1 v2 — extended calibrator zoo with uniform-jitter family.

Tier 1 v1 returned NO MATCH for the LLM cluster on the standard sweep
(β-ensemble, hard-core, Ginibre).  Inspection revealed the LLM cluster
sits at rep_int = 0.900 — the saturation value for a *near-uniform*
process, not a Wigner-Dyson β-ensemble.

This v2 extension adds the uniform-with-jitter family
(t_n = n + jitter · N(0,1)) to the calibrator zoo and re-runs the
4-vector distance comparison.  Re-uses Tier 1 v1 results from
data/phase13_calibrators.json for the existing calibrators (no need
to re-run the slow Ginibre).

Output:
    data/phase13_calibrators.json (updated in-place with uniform_jitter)
    plots/40_phase13_calibrators.png (regenerated)
"""
import os, sys, json, time
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from signal_gen import make_uniform_jitter
from arithmetic_toolkit import full_analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
N_POINTS = 2000
N_SEEDS = 5
ANCHOR_FC_REF = 115.55
ANCHOR_Q_MAX = 8

JITTER_VALUES = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]


def _fingerprint(t_k):
    res = full_analysis(t_k, label="cal", q_max=ANCHOR_Q_MAX,
                         fc_ref=ANCHOR_FC_REF, ramanujan_q_max=200)
    if 'error' in res:
        return None
    return dict(ks_u=res['primary_nns']['ks_u'],
                ks_o=res['primary_nns']['ks_o'],
                ks_p=res['primary_nns']['ks_p'],
                mass03=res['primary_nns']['mass03'],
                F_at_5=res['fano_curve'].get('F_at_5'),
                rep_int=res['pair_correlation'].get('repulsion_integral', 0))


def main():
    # Load existing v1 results
    json_path = os.path.join(DATA, "phase13_calibrators.json")
    with open(json_path) as f:
        existing = json.load(f)
    cal_results = dict(existing.get('calibrators', {}))

    print("=" * 110)
    print(f"Phase 13 Tier 1 v2 — adding uniform-jitter sweep (n={N_POINTS}, "
          f"seeds={N_SEEDS})")
    print("=" * 110)
    print(f"  {'jitter':<14}  {'med KS_GUE':>11}  {'med mass<.3':>12}  "
          f"{'med F(T=5)':>11}  {'med rep_int':>12}")

    for jitter in JITTER_VALUES:
        label = f"uniform jitter={jitter}"
        seed_fps = []
        for seed in range(N_SEEDS):
            t = make_uniform_jitter(N_POINTS, jitter, seed=seed)
            fp = _fingerprint(t)
            if fp is not None:
                seed_fps.append(fp)
        if not seed_fps:
            continue
        ks_u = np.array([s['ks_u'] for s in seed_fps])
        ks_o = np.array([s['ks_o'] for s in seed_fps])
        ks_p = np.array([s['ks_p'] for s in seed_fps])
        mass = np.array([s['mass03'] for s in seed_fps])
        f5   = np.array([s['F_at_5'] for s in seed_fps])
        ri   = np.array([s['rep_int'] for s in seed_fps])
        med = dict(ks_u=float(np.median(ks_u)),
                    ks_o=float(np.median(ks_o)),
                    ks_p=float(np.median(ks_p)),
                    mass03=float(np.median(mass)),
                    F_at_5=float(np.median(f5)),
                    rep_int=float(np.median(ri)))
        iqr = dict(ks_u=float(np.subtract(*np.percentile(ks_u, [75, 25]))),
                    mass03=float(np.subtract(*np.percentile(mass, [75, 25]))),
                    F_at_5=float(np.subtract(*np.percentile(f5, [75, 25]))),
                    rep_int=float(np.subtract(*np.percentile(ri, [75, 25]))))
        ks_min = min(med['ks_u'], med['ks_o'], med['ks_p'])
        cal_results[label] = dict(kind='uniform_jitter', param=str(jitter),
                                    n_seeds=len(seed_fps),
                                    median=med, iqr=iqr,
                                    ks_min_to_own_class=ks_min,
                                    best_self_label=['GUE','GOE','Poisson'][
                                        np.argmin([med['ks_u'], med['ks_o'], med['ks_p']])])
        print(f"  {label:<14}  {med['ks_u']:>11.4f}  {med['mass03']:>12.4f}  "
              f"{med['F_at_5']:>11.4f}  {med['rep_int']:>12.4f}")

    # ─── LLM cluster (re-load from existing) ────────────────────────────────
    llm_centroid = existing['llm_centroid_4v']
    centroid = np.array([llm_centroid['ks_u'], llm_centroid['mass03'],
                          llm_centroid['F_at_5'], llm_centroid['rep_int']])
    print(f"\nLLM centroid (4-vec): KS_GUE={centroid[0]:.3f}  "
          f"mass<.3={centroid[1]:.3f}  F(T=5)={centroid[2]:.3f}  "
          f"rep_int={centroid[3]:.3f}")

    # Build full calibrator 4-vector matrix
    cal_4v = []
    cal_labels = []
    for lbl, r in cal_results.items():
        m = r['median']
        cal_4v.append([m['ks_u'], m['mass03'], m['F_at_5'], m['rep_int']])
        cal_labels.append(lbl)
    cal_4v = np.array(cal_4v)

    # Re-load LLM cell raw 4-vectors
    llm_cells = []
    p10 = json.load(open(os.path.join(DATA, "phase10_llm_fingerprints.json")))
    for q, stims in p10.items():
        for stim, methods in stims.items():
            rn = methods.get("residual_norm_peaks")
            if rn and 'fingerprint_vector' in rn:
                fp = rn['fingerprint_vector']
                llm_cells.append((f"P10|{q}|{stim}", fp[0], fp[3], fp[5], fp[6]))
    p11 = json.load(open(os.path.join(DATA, "phase11_model_family.json")))
    for mdl, stims in p11.items():
        for stim, methods in stims.items():
            rn = methods.get("residual_norm_peaks")
            if rn and 'fingerprint_vector' in rn:
                fp = rn['fingerprint_vector']
                llm_cells.append((f"P11|{mdl}|{stim}", fp[0], fp[3], fp[5], fp[6]))
    llm_4v = np.array([(c[1], c[2], c[3], c[4]) for c in llm_cells])

    # Renormalise jointly
    all_pts = np.vstack([llm_4v, cal_4v])
    iqr = np.subtract(*np.percentile(all_pts, [75, 25], axis=0))
    iqr = np.where(iqr > 0, iqr, 1.0)
    cal_n = cal_4v / iqr
    centroid_n = centroid / iqr
    llm_n = llm_4v / iqr

    dists = np.linalg.norm(cal_n - centroid_n, axis=1)
    order = np.argsort(dists)
    print("\n" + "=" * 110)
    print("Calibrators ranked by Euclidean distance to LLM centroid (extended sweep)")
    print("=" * 110)
    print(f"  {'rank':>4}  {'calibrator':<22}  {'dist':>7}  "
          f"{'med KS_GUE':>11}  {'med mass<.3':>12}  {'med F(T=5)':>11}  "
          f"{'med rep_int':>12}  {'KS_min_self':>12}")
    for ri, idx in enumerate(order, start=1):
        r = cal_results[cal_labels[idx]]
        m = r['median']
        ks_min = r['ks_min_to_own_class']
        print(f"  {ri:>4}  {cal_labels[idx]:<22}  {dists[idx]:>7.3f}  "
              f"{m['ks_u']:>11.4f}  {m['mass03']:>12.4f}  {m['F_at_5']:>11.4f}  "
              f"{m['rep_int']:>12.4f}  {ks_min:>12.4f}")
        if ri >= 12: break

    # Per-LLM-cell nearest
    nearest = {}
    for k, c_n in enumerate(llm_n):
        d = np.linalg.norm(cal_n - c_n, axis=1)
        i = int(np.argmin(d))
        nearest[llm_cells[k][0]] = dict(calibrator=cal_labels[i],
                                          distance=float(d[i]))
    from collections import Counter
    counter = Counter(v['calibrator'] for v in nearest.values())
    print(f"\nModal nearest calibrator across {len(llm_cells)} LLM cells: "
          f"{counter.most_common(5)}")

    # ─── VERDICT ─────────────────────────────────────────────────────────────
    closest_idx = order[0]
    closest_label = cal_labels[closest_idx]
    closest_dist = float(dists[closest_idx])
    closest_ks_min_self = cal_results[closest_label]['ks_min_to_own_class']
    print("\n" + "=" * 110)
    print("VERDICT (extended)")
    print("=" * 110)
    print(f"  Closest calibrator to LLM centroid: {closest_label}")
    print(f"  Normalised Euclidean distance:      {closest_dist:.3f}")
    print(f"  Closest calibrator KS_min (self):   {closest_ks_min_self:.4f}")
    if closest_dist < 0.5:
        print(f"\n  ✓ CLASS IDENTIFIED at extended sweep:")
        print(f"    LLM residual-norm peaks are closest to the {closest_label} family.")
        verdict = 'class_identified_uniform'
    elif closest_dist < 1.0:
        print(f"\n  ⚠ CLOSE but not at acceptance distance.  Best match {closest_label}")
        print(f"    at distance {closest_dist:.3f}.  Per-axis comparison:")
        m = cal_results[closest_label]['median']
        print(f"      KS_GUE   : LLM={centroid[0]:.3f}  cal={m['ks_u']:.3f}")
        print(f"      mass<.3  : LLM={centroid[1]:.3f}  cal={m['mass03']:.3f}")
        print(f"      F(T=5)   : LLM={centroid[2]:.3f}  cal={m['F_at_5']:.3f}")
        print(f"      rep_int  : LLM={centroid[3]:.3f}  cal={m['rep_int']:.3f}")
        verdict = 'close_match_uniform_family'
    else:
        print(f"\n  ✗ Still NO MATCH.  Closest is {closest_label} at {closest_dist:.3f}.")
        verdict = 'no_match'

    # Save back into JSON
    existing['calibrators'] = cal_results
    existing['extended_verdict'] = verdict
    existing['extended_closest'] = closest_label
    existing['extended_closest_distance'] = closest_dist
    existing['extended_per_llm_cell_nearest'] = nearest
    existing['extended_modal_nearest'] = dict(counter.most_common(5))
    with open(json_path, 'w') as f:
        json.dump(existing, f, indent=2, default=str)
    print(f"\n  → data/phase13_calibrators.json (updated)")

    # ─── Plot ────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, (xi, xlabel, yi, ylabel) in zip(
            axes,
            [(1, 'mass<0.3', 0, 'KS_GUE'),
             (2, 'F(T=5)', 0, 'KS_GUE'),
             (3, 'repulsion_integral', 0, 'KS_GUE')]):
        cal_x = cal_4v[:, xi]
        cal_y = cal_4v[:, yi]
        cm = ['C1' if not lbl.startswith('uniform') else 'C3' for lbl in cal_labels]
        ax.scatter(cal_x, cal_y, c=cm, s=80, alpha=0.7)
        for lbl, x, y, c in zip(cal_labels, cal_x, cal_y, cm):
            ax.annotate(lbl[:14], (x, y), fontsize=6, ha='left',
                        xytext=(4, 0), textcoords='offset points')
        ax.scatter(llm_4v[:, xi], llm_4v[:, yi], c='C0', s=30, marker='x',
                    label=f'LLM cells')
        ax.scatter([centroid[xi]], [centroid[yi]], c='C0', s=200, marker='*',
                    edgecolors='black', linewidths=1.5, label='LLM centroid', zorder=5)
        ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
    axes[0].legend(fontsize=8)
    fig.suptitle(f"Phase 13 v2 — calibrator zoo + uniform-jitter family — verdict: {verdict}")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "40_phase13_calibrators.png"), dpi=120)
    plt.close(fig)
    print(f"  → plots/40_phase13_calibrators.png")


if __name__ == '__main__':
    main()
