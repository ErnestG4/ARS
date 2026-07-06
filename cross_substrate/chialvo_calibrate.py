"""
cross_substrate/chialvo_calibrate.py — Track 1.1 instrument-run harness (Phase 36).

Feeds Chialvo events through the SAME lens the calibrator zoo uses (joint_q_profile →
joint_quadrant_diagnostic → characterize_transition), per the protocol in
phase36/TRACK1_1_CHIALVO_CONFIG_JUSTIFICATION.md. RUN ONLY AFTER Track 0 PASS (strict gate).

Protocol: (1) detection on swept-a trajectory, (2) no-false-positive on stationary torus & chaos,
(3) sensitivity N floor, (4) engine attribution (NNS rep_int vs RF rf_amplitude).

Out: cross_substrate/coordinates/chialvo.jsonl + phase36/track1_1_chialvo_results.json (printed summary).

VERDICT (2026-05-31): `FAILED — NOT-SPECTRALLY-SEPARABLE`. The median-upcrossing default observable
this harness runs is OBSERVABLE-MISMATCHED for this map (fast-oscillation period is regime-stable →
clock-like in every regime; only a combinatorial 2→3 interval-cardinality signature persists). The
amplitude reading |Δpeak-amp| separated in-sample but FAILED an out-of-sample check on a fresh (b,k)
slice — slice-specific, not a transition-class readout. See phase36/TRACK1_1_CHIALVO_FINDINGS.md for
the full observable investigation + out-of-sample guard. This harness is retained as the record of the
initial (timing-observable) attempt; do not read its DETECTED-but-NFP-FAILED auto-string as the verdict.
"""
from __future__ import annotations
import os, sys, json
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, _HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import chialvo_run as CH
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from transition_diagnostic import characterize_transition

# Calibrator-zoo instrument config (matched to run_phase20_5_calibrators — see config-justification)
N_SUBWINDOWS = 30
MIN_EVENTS_PER_SUB = 100
Q_MAX = 25


def chialvo_trajectory(events, n_subwindows=N_SUBWINDOWS, min_events=MIN_EVENTS_PER_SUB, q_max=Q_MAX,
                       tag_vals=None):
    """Like transition_diagnostic.trajectory_from_events, but ALSO records per-subwindow engine-axis
    series for attribution: rep_int median (NNS axis) and rf_spike fraction + rf_amplitude ratio
    (Ramanujan-Fourier axis). If `tag_vals` (array aligned with `events`, e.g. the bifurcation
    parameter a at each event) is given, also records each sub-window's mean tag value — so the TWO
    sweep edges can be located in a. Returns (traj_df, engine_series)."""
    events = np.asarray(events, float)
    tag_vals = None if tag_vals is None else np.asarray(tag_vals, float)
    t0, t1 = float(events.min()), float(events.max())
    edges = np.linspace(t0, t1, n_subwindows + 1)
    rows, rep_series, rfspk_series, rfamp_series, amean_series = [], [], [], [], []
    for i in range(n_subwindows):
        mask = (events >= edges[i]) & (events < edges[i + 1])
        ev = events[mask]
        a_mean = float(np.mean(tag_vals[mask])) if (tag_vals is not None and mask.any()) else np.nan
        sp = np.diff(ev); sp = sp[sp > 0]
        if ev.size < min_events or sp.size < 4 or sp.mean() <= 0:
            rows.append(dict(primary='underpowered', rep_med=np.nan))
            rep_series.append(np.nan); rfspk_series.append(np.nan); rfamp_series.append(np.nan)
            amean_series.append(a_mean); continue
        ev_unit = np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))
        try:
            j = joint_q_profile(ev_unit, q_max=q_max, min_events_per_q=min_events)
            qd = joint_quadrant_diagnostic(j)
            well = qd[~qd['underpowered']]
            if not len(well):
                rows.append(dict(primary='underpowered', rep_med=np.nan))
                rep_series.append(np.nan); rfspk_series.append(np.nan); rfamp_series.append(np.nan)
                amean_series.append(a_mean); continue
            primary = str(well['quadrant'].value_counts().idxmax())
            rep_med = float(well['rep_int_q'].median())
            rfspk = float(well['rf_spike'].mean())
            # rf_amplitude ratio: max |a_q| (q>=2) over median |a_q| (q>=2) — the RF "spikiness"
            rf_q2 = well.loc[well['q'] >= 2, 'rf_amplitude_q'] if 'q' in well else well['rf_amplitude_q']
            rf_med = float(np.median(rf_q2)) if len(rf_q2) else np.nan
            rf_ratio = float(np.max(rf_q2) / rf_med) if (len(rf_q2) and rf_med > 0) else np.nan
            rows.append(dict(primary=primary, rep_med=rep_med))
            rep_series.append(rep_med); rfspk_series.append(rfspk); rfamp_series.append(rf_ratio)
            amean_series.append(a_mean)
        except Exception:
            rows.append(dict(primary='underpowered', rep_med=np.nan))
            rep_series.append(np.nan); rfspk_series.append(np.nan); rfamp_series.append(np.nan)
            amean_series.append(a_mean)
    return pd.DataFrame(rows), dict(rep_int=np.array(rep_series), rf_spike_frac=np.array(rfspk_series),
                                    rf_amp_ratio=np.array(rfamp_series), a_mean=np.array(amean_series))


def _drift(series):
    s = series[np.isfinite(series)]
    return float(s.max() - s.min()) if s.size >= 2 else float('nan')


def _monotonicity(series):
    """Spearman-rank corr of series vs subwindow index (|.| measures how transition-shaped it is)."""
    s = series.copy(); idx = np.arange(s.size)
    m = np.isfinite(s)
    if m.sum() < 4:
        return float('nan')
    x, y = idx[m], s[m]
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def _max_change_a(series, a_mean):
    """Locate the a-value of the largest consecutive change in `series` (the 'edge' that axis marks),
    plus the size of that step. NaN-robust."""
    m = np.isfinite(series) & np.isfinite(a_mean)
    s, a = series[m], a_mean[m]
    if s.size < 3:
        return None, None
    d = np.abs(np.diff(s))
    i = int(np.argmax(d))
    return round(float((a[i] + a[i + 1]) / 2), 4), round(float(d[i]), 4)


def run_detection():
    # Two-edge sweep: torus → mode-locking (Arnold tongues) → chaos. Capture the FULL per-axis
    # sub-window series tagged with the bifurcation parameter a, so each edge can be located in a and
    # its RESOLUTION (quadrant flip vs sub-quadrant) measured rather than presumed.
    ev, a_at = CH.chialvo_swept_a_events_tagged(CH.A_QUASI, CH.A_CHAOS + 0.005, 200_000)
    traj, eng = chialvo_trajectory(ev, tag_vals=a_at)
    res = characterize_transition(traj)
    prim = list(traj['primary']); a_mean = eng['a_mean']
    # full per-subwindow series (for the findings doc — both edges visible here)
    series = [dict(a=round(float(a_mean[i]), 4) if np.isfinite(a_mean[i]) else None,
                   primary=prim[i],
                   rep_med=round(float(eng['rep_int'][i]), 4) if np.isfinite(eng['rep_int'][i]) else None,
                   rf_spike=round(float(eng['rf_spike_frac'][i]), 4) if np.isfinite(eng['rf_spike_frac'][i]) else None)
              for i in range(len(prim))]
    # quadrant-flip locations (label changes), tagged with a
    flips = [dict(a=series[i]['a'], frm=prim[i - 1], to=prim[i])
             for i in range(1, len(prim)) if prim[i] != prim[i - 1]
             and 'underpowered' not in (prim[i], prim[i - 1])]
    rep_mono, rfspk_mono, rfamp_mono = (_monotonicity(eng['rep_int']),
                                        _monotonicity(eng['rf_spike_frac']),
                                        _monotonicity(eng['rf_amp_ratio']))
    rep_edge_a, rep_edge_d = _max_change_a(eng['rep_int'], a_mean)
    rf_edge_a, rf_edge_d = _max_change_a(eng['rf_spike_frac'], a_mean)
    attrib = max((abs(rep_mono), 'NNS_rep_int'), (abs(rfspk_mono), 'RF_spike'),
                 (abs(rfamp_mono), 'RF_amplitude'), key=lambda t: (t[0] if np.isfinite(t[0]) else -1))
    return dict(n_events=int(ev.size), a_range=[round(float(np.nanmin(a_mean)), 3), round(float(np.nanmax(a_mean)), 3)],
                transition_detected=bool(res['transition_detected']),
                shape=res['shape_estimate'], confidence=float(res['shape_confidence']),
                origin=res['origin_class'], destination=res['destination_class'],
                period_doubling=bool(res['period_doubling_signature'] is not None),
                rep_int_drift=round(_drift(eng['rep_int']), 4),
                rf_spike_drift=round(_drift(eng['rf_spike_frac']), 4),
                rep_int_monotonicity=round(rep_mono, 3), rf_spike_monotonicity=round(rfspk_mono, 3),
                rf_amp_monotonicity=round(rfamp_mono, 3), engine_attribution=attrib[1],
                rep_int_edge_a=rep_edge_a, rep_int_edge_step=rep_edge_d,
                rf_spike_edge_a=rf_edge_a, rf_spike_edge_step=rf_edge_d,
                quadrant_flips=flips, primaries=sorted(set(prim)), series=series)


def run_nfp(a, label, n_events_target=2584):
    """No-false-positive on a STATIONARY regime: trajectory must be FLAT — no quadrant flip AND no
    monotone sub-quadrant drift (the stationary regime is the 'null' for the sub-quadrant branch,
    mirroring the AM α-null in run_35b)."""
    ev = CH.chialvo_stationary_events(a, 260_000)
    # first pass at the N=2584-event budget (matches banked AM NFP number)
    ev_budget = ev[:n_events_target] if ev.size > n_events_target else ev
    nsub_budget = max(8, int(ev_budget.size // MIN_EVENTS_PER_SUB))
    traj_b, _ = chialvo_trajectory(ev_budget, n_subwindows=nsub_budget)
    res_b = characterize_transition(traj_b)
    # extended pass at full zoo config + engine-series monotonicity (sub-quadrant flatness)
    traj_f, eng_f = chialvo_trajectory(ev)
    res_f = characterize_transition(traj_f)
    rep_mono, rfspk_mono = _monotonicity(eng_f['rep_int']), _monotonicity(eng_f['rf_spike_frac'])
    subquad_flat = (abs(rep_mono) < 0.5 if np.isfinite(rep_mono) else True) and \
                   (abs(rfspk_mono) < 0.5 if np.isfinite(rfspk_mono) else True)
    no_quad_flip = (not res_b['transition_detected']) and (not res_f['transition_detected'])
    return dict(regime=label, a=a, n_events_total=int(ev.size),
                budget_N=int(ev_budget.size), budget_nsub=nsub_budget,
                budget_transition_detected=bool(res_b['transition_detected']),
                budget_primaries=sorted(set(traj_b['primary'])),
                extended_transition_detected=bool(res_f['transition_detected']),
                extended_primaries=sorted(set(traj_f['primary'])),
                rep_int_monotonicity=round(rep_mono, 3) if np.isfinite(rep_mono) else None,
                rf_spike_monotonicity=round(rfspk_mono, 3) if np.isfinite(rfspk_mono) else None,
                no_quad_flip=bool(no_quad_flip), subquad_flat=bool(subquad_flat),
                no_false_positive=bool(no_quad_flip and subquad_flat))


def run_sensitivity():
    """N floor for reliable DETECTION on the swept trajectory: vary iteration count → event count."""
    out = []
    for n_iter in (20_000, 40_000, 80_000, 150_000, 300_000):
        ev = CH.chialvo_swept_a_events(CH.A_QUASI, CH.A_CHAOS + 0.005, n_iter)
        if ev.size < MIN_EVENTS_PER_SUB * 8:
            out.append(dict(n_iter=n_iter, n_events=int(ev.size), detected=None, note="too_few_events"))
            continue
        nsub = min(N_SUBWINDOWS, max(8, int(ev.size // MIN_EVENTS_PER_SUB)))
        traj, _ = chialvo_trajectory(ev, n_subwindows=nsub)
        res = characterize_transition(traj)
        out.append(dict(n_iter=n_iter, n_events=int(ev.size), n_subwindows=nsub,
                        detected=bool(res['transition_detected']), shape=res['shape_estimate']))
    floor = next((r["n_events"] for r in out if r.get("detected")), None)
    return dict(sweep=out, detection_floor_events=floor)


def run_qmax_guard():
    """Does the detection verdict move with q_max (25 vs 50)? (RF axis guard for high-order rotation no.)"""
    ev = CH.chialvo_swept_a_events(CH.A_QUASI, CH.A_CHAOS + 0.005, 200_000)
    res = {}
    for q in (25, 50):
        traj, _ = chialvo_trajectory(ev, q_max=q)
        r = characterize_transition(traj)
        res[q] = dict(detected=bool(r['transition_detected']), shape=r['shape_estimate'])
    res['stable'] = (res[25]['detected'] == res[50]['detected'])
    return res


def main():
    print("=" * 78); print("TRACK 1.1 — CHIALVO CALIBRATOR (Phase 36)"); print("=" * 78, flush=True)
    R = {}
    print("\n[1] detection (swept-a torus→chaos)...", flush=True)
    R['detection'] = run_detection(); print("   ", R['detection'])
    print("\n[2] no-false-positive (stationary torus A_QUASI)...", flush=True)
    R['nfp_quasi'] = run_nfp(CH.A_QUASI, "quasiperiodic_torus"); print("   ", R['nfp_quasi'])
    print("\n[2b] no-false-positive (stationary chaos A_CHAOS)...", flush=True)
    R['nfp_chaos'] = run_nfp(CH.A_CHAOS, "developed_chaos"); print("   ", R['nfp_chaos'])
    print("\n[3] sensitivity (detection N floor)...", flush=True)
    R['sensitivity'] = run_sensitivity(); print("   ", R['sensitivity'])
    print("\n[4] q_max guard (25 vs 50)...", flush=True)
    R['qmax_guard'] = run_qmax_guard(); print("   ", R['qmax_guard'])

    # ── adjudication: pre-registered BOTH branches (mirrors run_35b) ──────────────────────────
    d = R['detection']
    quad_flip = d['transition_detected']
    # carrying-axis swept monotonicity, and the SAME axis's stationary-torus monotonicity (the null)
    axis_map = {'NNS_rep_int': ('rep_int_monotonicity', 'rep_int_monotonicity'),
                'RF_spike': ('rf_spike_monotonicity', 'rf_spike_monotonicity'),
                'RF_amplitude': ('rf_amp_monotonicity', None)}
    det_key, nfp_key = axis_map.get(d['engine_attribution'], ('rf_spike_monotonicity', 'rf_spike_monotonicity'))
    swept_mono = abs(d.get(det_key) or 0.0)
    stat_mono = abs((R['nfp_quasi'].get(nfp_key) if nfp_key else 0.0) or 0.0)
    # sub-quadrant detection: strong swept drift on the carrying axis, ≫ the stationary baseline
    subquad_det = (not quad_flip) and swept_mono > 0.5 and swept_mono > 2.0 * max(stat_mono, 1e-6)
    nfp = R['nfp_quasi']['no_false_positive'] and R['nfp_chaos']['no_false_positive']
    floor = R['sensitivity']['detection_floor_events']

    if quad_flip and nfp:
        tag = "DETECTED-AT-LOCUS (quadrant) + NFP-CONFIRMED"
    elif subquad_det and nfp:
        tag = "DETECTED-SUBQUADRANT + NFP-CONFIRMED"
    elif (quad_flip or subquad_det) and not nfp:
        tag = "DETECTED-but-NFP-FAILED (false positive on a stationary regime)"
    else:
        tag = "FAILED-DETECTION (no transition registered at the known breakdown locus, any resolution)"
    R['status_tag'] = tag
    R['engine'] = d['engine_attribution']
    R['detection_floor_events'] = floor
    R['adjudication'] = dict(quad_flip=bool(quad_flip), subquad_detected=bool(subquad_det),
                             carrying_axis=d['engine_attribution'], swept_monotonicity=round(swept_mono, 3),
                             stationary_baseline_monotonicity=round(stat_mono, 3),
                             nfp_confirmed=bool(nfp))

    print("\n" + "=" * 78)
    print(f"STATUS: {tag}")
    print(f" branch: quad_flip={quad_flip}  subquad_detected={subquad_det}")
    print(f" carrying axis: {d['engine_attribution']}  swept|mono|={swept_mono:.3f} vs stationary baseline {stat_mono:.3f}")
    print(f" NFP: torus={R['nfp_quasi']['no_false_positive']} chaos={R['nfp_chaos']['no_false_positive']} | quad-flip detection floor ~{floor}")
    print("=" * 78)

    def _ser(o):
        if isinstance(o, (np.bool_,)): return bool(o)
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        return str(o)
    out = os.path.join(_ROOT, "phase36", "track1_1_chialvo_results.json")
    json.dump(R, open(out, "w"), indent=1, default=_ser)
    print(f" → {out}")
    return R


if __name__ == "__main__":
    main()
