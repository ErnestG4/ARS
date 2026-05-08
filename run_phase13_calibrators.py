"""
Phase 13 Tier 1 — β-ensemble calibrator zoo.

Class-identification verdict on the LLM residual-norm-peak fingerprint.
Generate calibrator point processes whose universality class is
mathematically known, fingerprint each, find the closest match to the
LLM cluster centroid in the 4-vector (KS_GUE, mass<0.3, F(T=5),
rep_int) space.

Calibrators:
    β-ensemble (Hermite, Dumitriu-Edelman tridiagonal):
        β ∈ {1, 2, 3, 4, 6, 8}   ← β=2 is GUE, β=1 GOE, β=4 GSE,
                                    β > 4 sharper-than-GSE repulsion
    Hard-core (Matérn-II thinning):
        min_spacing ∈ {0.3, 0.5, 0.7} (raw units, post-norm
        min spacing ≈ min_spacing/mean_raw)
    Ginibre projection:
        projection ∈ {"real_part", "symmetric_part_eigvals"}

n_points = 2000, 5 seeds per cell.

LLM cluster: 9 Phase 10 (Qwen 2.5 3B fp16/int8/int4 × 3 stim) + 9 Phase 11
(Qwen, Mistral, TinyLlama × 3 stim) residual_norm_peaks cells = 18 cells.

Verdict criteria:
    closest calibrator in normalised 4-vector Euclidean
    if min_distance(LLM_centroid, closest) < 0.05 AND closest's
       KS_min < 0.05 → class identified
    else → non-standard repulsion class

Output:
    data/phase13_calibrators.json
    plots/40_phase13_calibrators.png
"""
import os, sys, json, time
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from signal_gen import (make_beta_ensemble_eigenvalues,
                         make_hardcore_process,
                         make_ginibre_projected)
from arithmetic_toolkit import full_analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")

N_POINTS = 2000
N_SEEDS = 5
ANCHOR_FC_REF = 115.55      # ζ-anchor cell
ANCHOR_Q_MAX = 8

CALIBRATORS = [
    *[(f"beta={b}", "beta_ensemble", b) for b in (1, 2, 3, 4, 6, 8)],
    *[(f"hardcore min={ms}", "hardcore", ms) for ms in (0.3, 0.5, 0.7)],
    ("ginibre_real_part", "ginibre", "real_part"),
    ("ginibre_symmetric",  "ginibre", "symmetric_part_eigvals"),
]


def _generate(kind, param, n_points, seed):
    if kind == "beta_ensemble":
        return make_beta_ensemble_eigenvalues(n_points, param, seed=seed)
    if kind == "hardcore":
        return make_hardcore_process(n_points, param, seed=seed)
    if kind == "ginibre":
        return make_ginibre_projected(n_points, param, seed=seed)
    raise ValueError(kind)


def _fingerprint(t_k):
    """Run full_analysis at the anchor cell, return the 10-vector."""
    res = full_analysis(t_k, label="cal", q_max=ANCHOR_Q_MAX,
                         fc_ref=ANCHOR_FC_REF,
                         ramanujan_q_max=200)
    if 'error' in res:
        return None
    return dict(fingerprint_vector=res['fingerprint_vector'],
                primary_nns=res['primary_nns'],
                fano_F_at_5=res['fano_curve'].get('F_at_5'),
                rep_int=res['pair_correlation'].get('repulsion_integral', 0),
                mass03=res['primary_nns']['mass03'],
                ks_u=res['primary_nns']['ks_u'])


# ─── Load existing LLM cells ────────────────────────────────────────────────

def _load_llm_cells():
    """Read residual_norm_peaks cells from Phase 10 + Phase 11 dumps."""
    cells = []
    p10_path = os.path.join(DATA, "phase10_llm_fingerprints.json")
    p11_path = os.path.join(DATA, "phase11_model_family.json")
    if os.path.exists(p10_path):
        with open(p10_path) as f:
            d = json.load(f)
        for q, stims in d.items():
            for stim, methods in stims.items():
                rn = methods.get("residual_norm_peaks")
                if rn and 'fingerprint_vector' in rn:
                    cells.append(dict(label=f"P10|{q}|{stim}",
                                       fingerprint_vector=rn['fingerprint_vector'],
                                       ks_u=rn['fingerprint_vector'][0],
                                       mass03=rn['fingerprint_vector'][3],
                                       fano_F_at_5=rn['fingerprint_vector'][5],
                                       rep_int=rn['fingerprint_vector'][6]))
    if os.path.exists(p11_path):
        with open(p11_path) as f:
            d = json.load(f)
        for mdl, stims in d.items():
            for stim, methods in stims.items():
                rn = methods.get("residual_norm_peaks")
                if rn and 'fingerprint_vector' in rn:
                    cells.append(dict(label=f"P11|{mdl}|{stim}",
                                       fingerprint_vector=rn['fingerprint_vector'],
                                       ks_u=rn['fingerprint_vector'][0],
                                       mass03=rn['fingerprint_vector'][3],
                                       fano_F_at_5=rn['fingerprint_vector'][5],
                                       rep_int=rn['fingerprint_vector'][6]))
    return cells


# ─── Sweep ────────────────────────────────────────────────────────────────────

def main():
    t_start = time.time()
    print("=" * 110)
    print(f"Phase 13 Tier 1 — calibrator zoo at n_points={N_POINTS}, seeds={N_SEEDS}")
    print(f"  anchor cell: q_max={ANCHOR_Q_MAX}, fc_ref={ANCHOR_FC_REF}")
    print("=" * 110)
    print(f"  {'calibrator':<22}  {'med KS_GUE':>11}  {'med KS_GOE':>11}  "
          f"{'med mass<.3':>12}  {'med F(T=5)':>11}  {'med rep_int':>12}  {'IQR KS_GUE':>12}")
    print("  " + "-" * 110)

    cal_results = {}
    for label, kind, param in CALIBRATORS:
        seed_fps = []
        for seed in range(N_SEEDS):
            t0 = time.time()
            t_k = _generate(kind, param, N_POINTS, seed=seed)
            fp = _fingerprint(t_k)
            if fp is None:
                continue
            seed_fps.append(fp)
        if not seed_fps:
            print(f"  {label:<22}  no successful seeds")
            continue
        # Aggregate across seeds: compute median/IQR of each scalar
        ks_u_arr = np.array([fp['ks_u'] for fp in seed_fps])
        mass_arr = np.array([fp['mass03'] for fp in seed_fps])
        f5_arr   = np.array([fp['fano_F_at_5'] for fp in seed_fps])
        ri_arr   = np.array([fp['rep_int'] for fp in seed_fps])
        ks_o_arr = np.array([fp['primary_nns']['ks_o'] for fp in seed_fps])
        ks_p_arr = np.array([fp['primary_nns']['ks_p'] for fp in seed_fps])
        cal_results[label] = dict(
            kind=kind, param=str(param),
            n_seeds=len(seed_fps),
            median=dict(ks_u=float(np.median(ks_u_arr)),
                         ks_o=float(np.median(ks_o_arr)),
                         ks_p=float(np.median(ks_p_arr)),
                         mass03=float(np.median(mass_arr)),
                         F_at_5=float(np.median(f5_arr)),
                         rep_int=float(np.median(ri_arr))),
            iqr=dict(ks_u=float(np.subtract(*np.percentile(ks_u_arr, [75, 25]))),
                      mass03=float(np.subtract(*np.percentile(mass_arr, [75, 25]))),
                      F_at_5=float(np.subtract(*np.percentile(f5_arr, [75, 25]))),
                      rep_int=float(np.subtract(*np.percentile(ri_arr, [75, 25]))))
        )
        m = cal_results[label]['median']
        i = cal_results[label]['iqr']
        ks_min_self = min(m['ks_u'], m['ks_o'], m['ks_p'])
        cal_results[label]['ks_min_to_own_class'] = ks_min_self
        cal_results[label]['best_self_label'] = (
            ['GUE','GOE','Poisson'][np.argmin([m['ks_u'], m['ks_o'], m['ks_p']])])
        print(f"  {label:<22}  {m['ks_u']:>11.4f}  {m['ks_o']:>11.4f}  "
              f"{m['mass03']:>12.4f}  {m['F_at_5']:>11.4f}  {m['rep_int']:>12.4f}  "
              f"{i['ks_u']:>12.4f}")

    # ─── LLM cluster ────────────────────────────────────────────────────────
    llm_cells = _load_llm_cells()
    print(f"\nLLM residual_norm_peaks cells loaded: {len(llm_cells)}")
    if not llm_cells:
        print("  no LLM cells found — Phase 10/11 JSON missing.  Skipping comparison.")
        return

    llm_4v = np.array([[c['ks_u'], c['mass03'], c['fano_F_at_5'], c['rep_int']]
                        for c in llm_cells])
    centroid = np.median(llm_4v, axis=0)
    print(f"  LLM centroid (4-vec): KS_GUE={centroid[0]:.3f}  "
          f"mass<.3={centroid[1]:.3f}  F(T=5)={centroid[2]:.3f}  "
          f"rep_int={centroid[3]:.3f}")

    # ─── 4-vector distance comparison ───────────────────────────────────────
    cal_4v = []
    cal_labels = []
    for lbl, r in cal_results.items():
        m = r['median']
        cal_4v.append([m['ks_u'], m['mass03'], m['F_at_5'], m['rep_int']])
        cal_labels.append(lbl)
    cal_4v = np.array(cal_4v)

    # Normalise each axis by combined LLM+calibrator IQR
    all_pts = np.vstack([llm_4v, cal_4v])
    iqr = np.subtract(*np.percentile(all_pts, [75, 25], axis=0))
    iqr = np.where(iqr > 0, iqr, 1.0)

    cal_n = cal_4v / iqr
    centroid_n = centroid / iqr
    llm_n = llm_4v / iqr

    dists_to_centroid = np.linalg.norm(cal_n - centroid_n, axis=1)
    dist_order = np.argsort(dists_to_centroid)
    print("\n" + "=" * 110)
    print("Calibrators ranked by Euclidean distance to LLM centroid (normalised 4-vector)")
    print("=" * 110)
    print(f"  {'rank':>4}  {'calibrator':<22}  {'dist':>7}  "
          f"{'med KS_GUE':>11}  {'med mass<.3':>12}  {'med F(T=5)':>11}  "
          f"{'KS_min_self':>12}")
    for rank_i, idx in enumerate(dist_order, start=1):
        r = cal_results[cal_labels[idx]]
        m = r['median']
        ks_min = r['ks_min_to_own_class']
        print(f"  {rank_i:>4}  {cal_labels[idx]:<22}  {dists_to_centroid[idx]:>7.3f}  "
              f"{m['ks_u']:>11.4f}  {m['mass03']:>12.4f}  {m['F_at_5']:>11.4f}  "
              f"{ks_min:>12.4f}")

    # ─── Per-LLM-cell mapping ───────────────────────────────────────────────
    nearest_per_cell = {}
    for k, c_n in enumerate(llm_n):
        d_to_cal = np.linalg.norm(cal_n - c_n, axis=1)
        nearest = int(np.argmin(d_to_cal))
        nearest_per_cell[llm_cells[k]['label']] = dict(
            calibrator=cal_labels[nearest], distance=float(d_to_cal[nearest]))

    print("\n  LLM cells: nearest calibrator per cell")
    from collections import Counter
    nn_counter = Counter(v['calibrator'] for v in nearest_per_cell.values())
    print(f"  Modal nearest calibrator across {len(llm_cells)} cells: "
          f"{nn_counter.most_common(3)}")

    # ─── VERDICT ────────────────────────────────────────────────────────────
    closest_idx = dist_order[0]
    closest_label = cal_labels[closest_idx]
    closest_dist = float(dists_to_centroid[closest_idx])
    closest_ks_min_self = cal_results[closest_label]['ks_min_to_own_class']

    print("\n" + "=" * 110)
    print("VERDICT")
    print("=" * 110)
    print(f"  Closest calibrator to LLM centroid: {closest_label}")
    print(f"  Normalised Euclidean distance:      {closest_dist:.3f}")
    print(f"  Closest calibrator KS_min (self):   {closest_ks_min_self:.4f}")
    print(f"  Best self-fit label of closest:     {cal_results[closest_label]['best_self_label']}")
    print()
    if closest_dist < 0.05 and closest_ks_min_self < 0.05:
        print(f"  ✓ CLASS IDENTIFIED: LLM residual-norm peaks live in the "
              f"{closest_label} class.")
        verdict = 'class_identified'
    elif closest_dist < 0.05:
        print(f"  ⚠ CLOSE-MATCH but the calibrator itself is not at clean")
        print(f"    Wigner quality (KS_min_self = {closest_ks_min_self:.3f}).  ")
        print(f"    Meaningful only if the calibrator is independently validated.")
        verdict = 'close_match_calibrator_unclean'
    else:
        print(f"  ✗ NO MATCH on the standard sweep.  LLM residual-norm peaks live")
        print(f"    in a non-standard repulsion class with respect to β-ensembles,")
        print(f"    hard-core, and Ginibre projections at this anchor.  Closest")
        print(f"    fingerprint is {closest_label} at distance {closest_dist:.3f}.")
        verdict = 'no_standard_match'

    # ─── Save ──────────────────────────────────────────────────────────────
    out = dict(
        config=dict(n_points=N_POINTS, n_seeds=N_SEEDS,
                     anchor_fc_ref=ANCHOR_FC_REF, anchor_q_max=ANCHOR_Q_MAX),
        calibrators=cal_results,
        llm_cells_used=len(llm_cells),
        llm_centroid_4v=dict(ks_u=float(centroid[0]),
                              mass03=float(centroid[1]),
                              F_at_5=float(centroid[2]),
                              rep_int=float(centroid[3])),
        normalised_4v_iqr=dict(ks_u=float(iqr[0]),
                                 mass03=float(iqr[1]),
                                 F_at_5=float(iqr[2]),
                                 rep_int=float(iqr[3])),
        distances_to_centroid={cal_labels[i]: float(dists_to_centroid[i])
                                  for i in range(len(cal_labels))},
        per_llm_cell_nearest=nearest_per_cell,
        verdict=verdict,
        closest_calibrator=closest_label,
        closest_distance=closest_dist,
    )
    with open(os.path.join(DATA, "phase13_calibrators.json"), 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  → data/phase13_calibrators.json")

    # ─── Plot ──────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    # 2D scatter: mass<.3 vs KS_GUE
    cal_x = [r['median']['mass03'] for r in cal_results.values()]
    cal_y = [r['median']['ks_u']  for r in cal_results.values()]
    ax.scatter(cal_x, cal_y, c='C1', s=80, label='calibrators', alpha=0.7)
    for lbl, x, y in zip(cal_labels, cal_x, cal_y):
        ax.annotate(lbl, (x, y), fontsize=7, ha='left', va='center',
                    xytext=(4, 0), textcoords='offset points')
    llm_x = llm_4v[:, 1]; llm_y = llm_4v[:, 0]
    ax.scatter(llm_x, llm_y, c='C0', s=40, marker='x',
                label=f'LLM cells (n={len(llm_cells)})')
    ax.scatter([centroid[1]], [centroid[0]], c='C0', s=200, marker='*',
                edgecolors='black', linewidths=1.5, label='LLM centroid', zorder=5)
    ax.set_xlabel('mass<0.3 (median)')
    ax.set_ylabel('KS_GUE (median)')
    ax.set_title('Phase 13: calibrator zoo vs LLM cluster')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc='best')

    ax = axes[1]
    # KS_GUE vs F(T=5)
    cal_x = [r['median']['F_at_5'] for r in cal_results.values()]
    cal_y = [r['median']['ks_u']  for r in cal_results.values()]
    ax.scatter(cal_x, cal_y, c='C1', s=80, alpha=0.7)
    for lbl, x, y in zip(cal_labels, cal_x, cal_y):
        ax.annotate(lbl, (x, y), fontsize=7, ha='left', va='center',
                    xytext=(4, 0), textcoords='offset points')
    llm_x = llm_4v[:, 2]; llm_y = llm_4v[:, 0]
    ax.scatter(llm_x, llm_y, c='C0', s=40, marker='x')
    ax.scatter([centroid[2]], [centroid[0]], c='C0', s=200, marker='*',
                edgecolors='black', linewidths=1.5, zorder=5)
    ax.set_xlabel('F(T=5) (median)')
    ax.set_ylabel('KS_GUE (median)')
    ax.set_title('KS_GUE vs F(T=5)')
    ax.grid(True, alpha=0.3)

    fig.suptitle(f"Phase 13 calibrator zoo — verdict: {verdict}", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "40_phase13_calibrators.png"), dpi=120)
    plt.close(fig)
    print(f"  → plots/40_phase13_calibrators.png")
    print(f"\nTotal time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
