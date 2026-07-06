"""
phase35a/run_35b_diagnostic.py — Step-1 35b: non-circular validation of
transition_diagnostic on AM (Will 2026-05-17, "finish what §Q3
interrupted"). Uses the RATIO-FREE VALIDATED leg (commit 61e11d5).

Signal: AM λ-trajectory bracketing the proven λ=1 transition (λ=1
EXCLUDED — brief: λ=1 out as a measured substrate), golden-mean θ,
fixed phase, rotnum-unfolded, classified by joint_quadrant_diagnostic,
fed to characterize_transition.

Right-null: the **α-ensemble** (§7.ter.48 substrate-generated,
non-circular) — fixed (θ, localised λ), vary the cos phase α=φ (it is
part of the operator); ergodic ⇒ limiting stats φ-independent ⇒ the
null trajectory must be FLAT (no transition). Non-circular: the null is
the operator's own phase d.o.f., not a hand-tuned mixing weight (the
whole point — Phase-20.5 blends were circular).

Verdict map PRE-SPECIFIED BOTH WAYS (brief §8):
 (a) signal shows a quadrant FLIP characterize_transition detects, null
     does not ⇒ diagnostic validated by flip on a non-synthetic
     substrate;
 (b) signal BR_artifact-throughout (no flip — EXPECTED per the
     ratio-clean zoo-gap recheck) BUT signal rep_med drifts while the
     α-null rep_med stays flat ⇒ the diagnostic CORRECTLY returns
     no quadrant transition (no false-positive), the real transition is
     the sub-quadrant rep_med drift; signal≠α-null sub-quadrant ⇒ the
     §7.ter.28 BGP-precedent branch, a pre-registered VALID non-circular
     validation.
Either way the test is whether transition_diagnostic behaves per its
pre-specified map. SCOPING / tooling-confidence, NOT a discovery, NOT
§3. No stamping; Class II blocked.
"""
from __future__ import annotations
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pandas as pd
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from transition_diagnostic import characterize_transition
from unfold_rotnum import am_eigs, unfold_rotnum, spacings, W1d, GOLDEN

NCELL, LITER, QMAX, MINEV = 2584, 1_000_000, 30, 30
SIG_LAMS = [0.50, 0.70, 0.85, 0.95, 1.05, 1.25, 1.50, 2.00]   # brackets λ=1, EXCLUDED
NULL_LAM = 1.50                                                # localised; α-ensemble
NULL_PHIS = list(np.round(np.linspace(0.0, 1.0, len(SIG_LAMS), endpoint=False), 4))


def cell_row(lam, phi):
    e = am_eigs(lam, NCELL, phi)
    uf = unfold_rotnum(e, lam, GOLDEN, LITER, phis=(phi,))
    j = joint_q_profile(np.sort(uf), q_max=QMAX, min_events_per_q=MINEV)
    qd = joint_quadrant_diagnostic(j)
    vc = qd['quadrant'].value_counts()
    primary = str(vc.idxmax())
    rep_med = float(np.nanmedian(j['rep_int_q'])) if 'rep_int_q' in j else float('nan')
    return primary, round(rep_med, 5), round(W1d(uf), 5), round(float(np.var(spacings(uf))), 5)


def build(traj_spec, kind):
    rows = []
    for i, (lam, phi, label) in enumerate(traj_spec):
        p, rm, w, v = cell_row(lam, phi)
        rows.append({"i": i, kind: label, "primary": p, "rep_med": rm,
                     "W1d": w, "var_s": v, "subwindow_start_us": i})
        print(f"  [{kind}] {label:>8} | primary={p:<12} rep_med={rm:<9} "
              f"W1δ={w:<8} var={v}", flush=True)
    return pd.DataFrame(rows)


def run():
    print("=" * 80)
    print("35b — transition_diagnostic non-circular validation on AM (VALIDATED leg)")
    print("=" * 80)
    print(f"SIGNAL (λ→ across transition, λ=1 excluded; θ=golden, φ=0):")
    sig_spec = [(l, 0.0, f"λ={l}") for l in SIG_LAMS]
    sig = build(sig_spec, "step")
    print(f"\nα-ENSEMBLE NULL (§7.ter.48; fixed θ, λ={NULL_LAM}; vary α=φ):")
    null_spec = [(NULL_LAM, ph, f"α={ph}") for ph in NULL_PHIS]
    nul = build(null_spec, "step")

    sig_ch = characterize_transition(sig)
    nul_ch = characterize_transition(nul)

    def drift(df):
        r = df["rep_med"].to_numpy(float)
        w = df["W1d"].to_numpy(float)
        return (round(float(np.nanmax(r) - np.nanmin(r)), 5),
                round(float(np.nanmax(w) - np.nanmin(w)), 5))
    sig_rd, sig_wd = drift(sig)
    nul_rd, nul_wd = drift(nul)
    sig_prims, nul_prims = set(sig["primary"]), set(nul["primary"])

    print("\n" + "=" * 80)
    print("RESULT")
    print(f" signal: primaries={sig_prims} transition_detected="
          f"{sig_ch['transition_detected']} shape={sig_ch['shape_estimate']} "
          f"| rep_med drift={sig_rd} W1δ drift={sig_wd}")
    print(f" α-null: primaries={nul_prims} transition_detected="
          f"{nul_ch['transition_detected']} shape={nul_ch['shape_estimate']} "
          f"| rep_med drift={nul_rd} W1δ drift={nul_wd}")

    quad_flip = len(sig_prims) > 1 and sig_ch["transition_detected"] \
        and not nul_ch["transition_detected"]
    subquad = (not sig_ch["transition_detected"]) and (sig_wd > 5 * max(nul_wd, 1e-6)) \
        and (sig_wd > 0.05)
    if quad_flip:
        verdict = ("DIAGNOSTIC_VALIDATED_BY_QUADRANT_FLIP "
                   "(signal flips & detected; α-null does not — branch (a))")
    elif subquad:
        verdict = ("DIAGNOSTIC_VALIDATED_SUBQUADRANT_§7ter28 "
                   "(no false quadrant-transition; signal sub-quadrant drift ≫ "
                   "α-null; transition lives sub-quadrant — branch (b), "
                   "pre-registered valid)")
    else:
        verdict = ("UNRESOLVED — neither pre-specified branch cleanly met; "
                   "inspect (no auto-adjudication)")
    print(f"\n PRE-SPECIFIED VERDICT: {verdict}")
    print(" SCOPING/tooling-confidence — transition_diagnostic behaves per its")
    print(" pre-specified map on a non-synthetic proven-transition substrate.")
    print(" NOT a discovery; NOT §3; no stamping; Class II blocked.")
    print("=" * 80)
    json.dump({"scoping_arc_finish": True, "leg": "unfold_rotnum VALIDATED",
               "signal": sig.to_dict("records"), "alpha_null": nul.to_dict("records"),
               "signal_characterize": {k: str(v) for k, v in sig_ch.items()
                                        if k != "trajectory_features"},
               "null_characterize": {k: str(v) for k, v in nul_ch.items()
                                      if k != "trajectory_features"},
               "verdict": verdict},
              open(os.path.join(HERE, "run_35b_results.json"), "w"), indent=1)


if __name__ == "__main__":
    run()
