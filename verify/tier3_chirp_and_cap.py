"""
tier3_chirp_and_cap.py  — independent verification harness (read-only).

Two checks:
  CHECK A  chirp GUE unfold bug (audit FIX-3):
           run_chirp_prediction.py:112-120 builds a GUE reference and unfolds
           it with the GLOBAL-MEAN method
               eig_unfolded = (eig - eig[0]) / spacings.mean()
           which fix_gue_generator.py:60 labels the "OLD broken procedure".
           Compare marginal NNS distance-to-GUE for global-mean vs the
           semicircle-CDF fix.

  CHECK B  phase20/21 JPF_CAP drift materiality (audit FIX-5):
           run_phase21_classification.py JPF_CAP=1500 vs
           run_phase21_calibrators.py JPF_CAP=5000; phase20 has no cap.
           Screen how many windows exceed 1500 and, for those, re-run the
           classify pipeline at cap 1500 vs 5000 and diff the quadrant.

Run:  PYTHONPATH=/home/combust/fmexplorer/riemann_explorer \
      /home/combust/fmexplorer/bin/python3 verify/tier3_chirp_and_cap.py

Does NOT edit or import-execute any tool/driver file.  fix_gue_generator.py
is NOT imported (its module body runs a full GPU PLL diagnostic on import);
its two pure-numpy unfold helpers are replicated VERBATIM below with line
citations, which the brief explicitly sanctions.
"""
import os, sys, json
from pathlib import Path
import numpy as np
import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
TOOL_DIR = THIS_DIR.parent
sys.path.insert(0, str(TOOL_DIR))

from cross_substrate.axes import I5_ks_gue, canonical_spacings, I8_brody_q, I10_cv
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic

DATA = TOOL_DIR / 'data'
OUT = []


def emit(s=""):
    print(s)
    OUT.append(s)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK A — chirp GUE unfold bug
# ═══════════════════════════════════════════════════════════════════════════

def gen_gue_eigenvalues_verbatim(N, seed):
    """VERBATIM replication of run_chirp_prediction.py:112-115
    (identical to fix_gue_generator.py gen_gue_eigenvalues, seed 42)."""
    rng = np.random.default_rng(seed)
    A = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * N)
    eig = np.sort(np.linalg.eigvalsh(H).real)
    return eig


# --- VERBATIM from fix_gue_generator.py:45-48 -------------------------------
def semicircle_cdf_unit(x):
    """CDF of semicircle rho(x) = (2/pi)*sqrt(1-x^2) on [-1, 1]."""
    x = np.clip(x, -1.0, 1.0)
    return 0.5 + (x * np.sqrt(1.0 - x * x) + np.arcsin(x)) / np.pi


# --- VERBATIM from fix_gue_generator.py:67-74 -------------------------------
def unfold_semicircle_R(eigs, R=None):
    eigs = np.asarray(eigs, dtype=np.float64)
    if R is None:
        R = 2.0                      # theoretical half-radius for this norm
    return semicircle_cdf_unit(eigs / R) * len(eigs)


def axes_triplet(s):
    s = np.asarray(s, dtype=np.float64)
    return dict(
        n=int(s.size),
        I5_ks_gue=I5_ks_gue(s),
        I8_brody_q=I8_brody_q(s),
        I10_cv=I10_cv(s),
    )


def check_A():
    emit("=" * 78)
    emit("CHECK A — chirp GUE unfold bug (audit FIX-3)")
    emit("=" * 78)
    emit("Source: run_chirp_prediction.py:112-120 builds the GUE reference and")
    emit("        unfolds via eig_unfolded=(eig-eig[0])/spacings.mean()  (line 117)")
    emit("        = fix_gue_generator.py:60 'OLD broken procedure' (unfold_global_mean).")
    emit("        Fix = semicircle-CDF unfold, fix_gue_generator.py:45-48 & 67-74.")
    emit("        (fix_gue_generator NOT imported: its module body runs a GPU PLL")
    emit("         diagnostic on import; the two pure helpers are replicated verbatim.)")
    emit("")
    # N=500 = fix_gue_generator's verification size; N=100 = script's actual size
    # (run_chirp_prediction ACTUAL_NZ = min(NZ=100, len(ZETA_ZEROS))).
    for N in (500, 100):
        eig = gen_gue_eigenvalues_verbatim(N, seed=42)
        emit(f"--- N={N} (seed 42), eig range [{eig.min():.4f}, {eig.max():.4f}] ---")

        # (a) GLOBAL-MEAN (current/buggy)  — brief-specified spacing object
        sp = np.diff(eig)
        s_global = sp / sp.mean()
        a = axes_triplet(s_global)

        # (b) SEMICIRCLE (the fix)
        pos = unfold_semicircle_R(eig)
        sp_semi = np.diff(pos)
        s_semi = sp_semi / sp_semi.mean()
        b = axes_triplet(s_semi)

        # cross-check via the canonical (2-98% trim) matched extractor
        a_c = axes_triplet(canonical_spacings((eig - eig[0]) / sp.mean()))
        b_c = axes_triplet(canonical_spacings(pos))

        emit(f"  (a) GLOBAL-MEAN : I5_ks_gue={a['I5_ks_gue']:.4f}  "
             f"I10_cv={a['I10_cv']:.4f}  I8_brody_q={a['I8_brody_q']:.3f}  (n={a['n']})")
        emit(f"  (b) SEMICIRCLE  : I5_ks_gue={b['I5_ks_gue']:.4f}  "
             f"I10_cv={b['I10_cv']:.4f}  I8_brody_q={b['I8_brody_q']:.3f}  (n={b['n']})")
        emit(f"      [canonical-trim x-check] global I5={a_c['I5_ks_gue']:.4f} "
             f"cv={a_c['I10_cv']:.4f} | semi I5={b_c['I5_ks_gue']:.4f} "
             f"cv={b_c['I10_cv']:.4f}")
        d_ks = a['I5_ks_gue'] - b['I5_ks_gue']
        d_cv = a['I10_cv'] - b['I10_cv']
        gue_cv = 0.5227  # CV of Wigner-GUE surmise spacings (analytic ~sqrt(3pi/8 -1))
        emit(f"      delta I5_ks_gue (global - semi) = {d_ks:+.4f}  "
             f"(>0 => global-mean reads FURTHER from GUE)")
        emit(f"      delta CV (global - semi)        = {d_cv:+.4f}  "
             f"(GUE-surmise CV ~= {gue_cv:.3f}; global CV inflated toward "
             f"semicircle if larger)")
        verdict = ("CORRUPTS: global-mean is measurably further from Wigner-GUE"
                   if d_ks > 0.02 else
                   "MARGINAL: difference below 0.02 in KS")
        emit(f"      -> {verdict}")
        emit("")
    return


# ═══════════════════════════════════════════════════════════════════════════
# CHECK B — JPF_CAP drift materiality
# ═══════════════════════════════════════════════════════════════════════════
Q_MAX_21 = 30
MIN_EVENTS_PER_Q_21 = 30
Q_MAX_20 = 60
MIN_EVENTS_20 = 30
PANEL21 = DATA / 'phase21_grb_panel'
PHASE20_ROOT = DATA / 'phase20_facebook_2021'


def unfold_unit_mean(t, cap):
    """VERBATIM from run_phase21_classification.py:59-68 (cap param exposed)."""
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    if sp.size > cap:
        sp = sp[::max(1, sp.size // cap)]
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))


def classify_subwindow_21(events_us, cap):
    """VERBATIM logic from run_phase21_classification.py:75-101 (classify_subwindow),
    with the cap threaded through unfold_unit_mean."""
    if events_us.size < MIN_EVENTS_PER_Q_21:
        return 'underpowered'
    ev = events_us.astype(np.float64) / 1_000_000
    ev_unit = unfold_unit_mean(ev, cap=cap)
    if ev_unit.size < MIN_EVENTS_PER_Q_21:
        return 'underpowered'
    j = joint_q_profile(ev_unit, q_max=Q_MAX_21, min_events_per_q=MIN_EVENTS_PER_Q_21)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return 'underpowered'
    return str(well['quadrant'].value_counts().idxmax())


def classify_subwindow_20(events_us, cap):
    """run_phase20_classification.py classify path (primary_quadrant, lines 65-76 +
    classify_event_window lines 95-104), Q_MAX=60.  cap=None reproduces the deployed
    (uncapped) unfold_unit_mean (lines 56-62); cap>0 injects the FIX-5 decimation."""
    if events_us.size < MIN_EVENTS_20:
        return 'underpowered'
    ev = events_us.astype(np.float64) / 1_000_000
    if cap is None:
        ev_unit = unfold_unit_mean(ev, cap=10 ** 18)   # effectively no cap
    else:
        ev_unit = unfold_unit_mean(ev, cap=cap)
    if ev_unit.size < MIN_EVENTS_20:
        return 'underpowered'
    j = joint_q_profile(ev_unit, q_max=Q_MAX_20, min_events_per_q=MIN_EVENTS_20)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return 'underpowered'
    return str(well['quadrant'].value_counts().idxmax())


def check_B():
    emit("=" * 78)
    emit("CHECK B — phase20/21 JPF_CAP drift materiality (audit FIX-5)")
    emit("=" * 78)
    emit("classification cap=1500 (run_phase21_classification.py:57 JPF_CAP);")
    emit("calibrators   cap=5000 (run_phase21_calibrators.py:58 JPF_CAP);")
    emit("phase20 unfold has NO cap (run_phase20_classification.py:56-62).")
    emit("The cap decimates spacings sp[::sp.size//cap] only when sp.size>cap,")
    emit("i.e. only windows with more events than the cap are affected.")
    emit("")

    # ---- item 1+2: materiality SCREEN from banked classification parquets ----
    bank20 = pd.read_parquet(DATA / 'phase20_classification.parquet')
    bank21 = pd.read_parquet(DATA / 'phase21_classification.parquet')
    emit("-- item 1/2: n_events screen (banked classification parquets) --")
    for tag, b in [('phase20', bank20), ('phase21', bank21)]:
        ne = b['n_events']
        emit(f"  {tag}: {len(b)} windows | n_events [{ne.min()}, {ne.max()}] | "
             f">1500: {int((ne > 1500).sum())} | >5000: {int((ne > 5000).sum())}")
    emit("  phase20: all windows are far above the cap; but phase20's deployed")
    emit("           unfold applies NO cap, so the 1500-vs-5000 drift is absent")
    emit("           from its banked result (tested below as uncapped vs cap).")
    n_affected_21 = int((bank21['n_events'] > 1500).sum())
    if n_affected_21 == 0:
        emit("  MATERIALITY: no phase21 window exceeds 1500 -> cap drift IMMATERIAL. Stop.")
        return
    emit(f"  MATERIALITY: {n_affected_21} phase21 windows exceed 1500 -> decimation "
         f"happens; proceed to re-run.")
    emit("")

    # ---- item 3 (phase21): re-run affected windows at cap 1500 vs 5000 -------
    emit("-- item 3: phase21 re-run at cap=1500 vs cap=5000 (affected windows) --")
    aff21 = bank21[bank21['n_events'] > 1500].copy()
    changed_1500_5000 = 0
    changed_vs_bank = 0
    nrecon_mismatch = 0
    rows = []
    panel_cache = {}
    for _, r in aff21.iterrows():
        ev_name = r['event']
        if ev_name not in panel_cache:
            p = PANEL21 / f"{ev_name}.parquet"
            panel_cache[ev_name] = pd.read_parquet(p, columns=['time_us'])['time_us'].to_numpy()
        times = panel_cache[ev_name]
        s_us = int(round(r['sub_start_s'] * 1_000_000))
        e_us = int(round(r['sub_end_s'] * 1_000_000))
        ev = times[(times >= s_us) & (times < e_us)]
        if abs(int(ev.size) - int(r['n_events'])) > 1:
            nrecon_mismatch += 1
        q1500 = classify_subwindow_21(ev, cap=1500)
        q5000 = classify_subwindow_21(ev, cap=5000)
        if q1500 != q5000:
            changed_1500_5000 += 1
        if str(q1500) != str(r['primary']):
            changed_vs_bank += 1
        rows.append((ev_name, r['sub_start_s'], int(ev.size),
                     str(r['primary']), q1500, q5000))
    emit(f"  affected windows re-run: {len(aff21)}")
    emit(f"  n_events reconstruction mismatch (>1 off banked): {nrecon_mismatch}/{len(aff21)}")
    emit(f"  quadrant CHANGES cap1500 vs cap5000: {changed_1500_5000}/{len(aff21)}")
    emit(f"  quadrant differs from banked (cap1500 re-run vs banked primary): "
         f"{changed_vs_bank}/{len(aff21)}")
    # show any that changed
    diffs = [x for x in rows if x[4] != x[5]]
    if diffs:
        emit("  windows changing quadrant (1500 vs 5000):")
        for (en, ss, n, bk, q1, q5) in diffs[:20]:
            emit(f"    {en} @{ss:.0f}s n={n} bank={bk} cap1500={q1} cap5000={q5}")
    else:
        emit("  (no phase21 affected window changes quadrant between cap 1500 and 5000)")
    # banked primary distribution among affected
    emit(f"  banked primary among affected: "
         f"{dict(aff21['primary'].value_counts())}")
    emit("")

    # ---- phase20 re-run: uncapped (deployed) vs cap 1500 vs cap 5000 ---------
    emit("-- phase20 re-run: uncapped (deployed) vs cap=1500 vs cap=5000 --")
    try:
        from bgp_pipeline import load_cell_parquet
    except Exception as e:
        emit(f"  BLOCKED: cannot import bgp_pipeline.load_cell_parquet ({e})")
        return
    emit("  (deployed phase20 = uncapped; its banked 'primary' IS the uncapped")
    emit("   result, so we use banked as the uncapped reference and only recompute")
    emit("   the capped variants — recomputing uncapped on full 35k-1M-event windows")
    emit("   is what the deployed run already did.)")
    emit("  NOTE: phase20 classify is Q_MAX=60 over ~1500/5000 capped points; the full")
    emit("  576-window x 2-cap grid is O(hours). This is a bounded STRATIFIED SAMPLE")
    emit("  (SAMPLE_PER_COLLECTOR windows evenly spaced in time per collector) — a")
    emit("  materiality screen, not exhaustive.")
    SAMPLE_PER_COLLECTOR = 16
    SUBWINDOW_US = 5 * 60 * 1_000_000
    changed_1500_5000_20 = 0
    changed_bank_vs_1500 = 0
    n20 = 0
    diffs20 = []
    for collector, g in bank20.groupby('collector'):
        p = PHASE20_ROOT / f"{collector}_event.parquet"
        try:
            ts = load_cell_parquet(p, columns=['timestamp_us'])['timestamp_us'].to_numpy()
        except Exception as e:
            emit(f"  BLOCKED collector {collector}: {e}")
            continue
        g = g.sort_values('subwindow_start_us')
        if len(g) > SAMPLE_PER_COLLECTOR:
            idx = np.linspace(0, len(g) - 1, SAMPLE_PER_COLLECTOR).round().astype(int)
            g = g.iloc[idx]
        for _, r in g.iterrows():
            s = int(r['subwindow_start_us'])
            ev = ts[(ts >= s) & (ts < s + SUBWINDOW_US)]
            if ev.size < MIN_EVENTS_20:
                continue
            n20 += 1
            qU = str(r['primary'])            # banked = deployed uncapped
            q1500 = classify_subwindow_20(ev, cap=1500)
            q5000 = classify_subwindow_20(ev, cap=5000)
            if q1500 != q5000:
                changed_1500_5000_20 += 1
            if qU != q1500:
                changed_bank_vs_1500 += 1
            if q1500 != q5000 or qU != q1500:
                diffs20.append((collector, s, int(ev.size), qU, q1500, q5000))
    emit(f"  phase20 windows re-run (well-powered, capped variants only): {n20}")
    emit(f"  quadrant CHANGES cap1500 vs cap5000: {changed_1500_5000_20}/{n20}")
    emit(f"  quadrant CHANGES banked-uncapped vs cap1500: {changed_bank_vs_1500}/{n20}")
    if diffs20:
        emit("  phase20 windows with any cap-sensitivity:")
        for (c, s, n, qU, q1, q5) in diffs20[:20]:
            emit(f"    {c} @{s} n={n} uncap(bank)={qU} cap1500={q1} cap5000={q5}")
    else:
        emit("  (no phase20 window changes quadrant across uncapped/1500/5000)")
    emit("")


def main():
    check_A()
    check_B()
    # write results
    res = THIS_DIR / 'tier3_results.md'
    with open(res, 'w') as f:
        f.write("# Tier-3 verification: chirp GUE unfold (FIX-3) + JPF_CAP drift (FIX-5)\n\n")
        f.write("Run: `PYTHONPATH=/home/combust/fmexplorer/riemann_explorer "
                "/home/combust/fmexplorer/bin/python3 verify/tier3_chirp_and_cap.py`\n\n")
        f.write("```\n")
        f.write("\n".join(OUT))
        f.write("\n```\n")
    print(f"\n[written] {res}")


if __name__ == '__main__':
    main()
