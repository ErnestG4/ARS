"""
cross_substrate/rf_decoy_battery.py — the RF-engine (Ramanujan-Fourier) confound
run, built on the existing calibrator zoo.

Motivation (the long-range arc, applied to the RF side). On the NNS/spacing path
we learned an NNS verdict certifies the MARGINAL, not the universality class, and
we needed a Wigner-renewal DECOY (matched marginal, destroyed long-range order) to
separate them. The RF engine has its OWN observable — the indicator-mode Ramanujan-
Fourier amplitude a_q (joint_q_profile.rf_amplitude_q), which reads integer-PERIOD
structure on the raw event grid. The same three questions apply, and the calibrator
zoo (calibrator_panel.py) is the native known-answer substrate for all three:

  (1) POLE-ABSOLUTE GROUND TRUTH (no-false-NEGATIVE gate). period-known calibrators
      have a known a_q answer: periodic_q7 -> a_q peaks AT q=7; mixed_q7_q12 -> at 7
      and 12; poisson / GUE / GOE / GSE / zeta -> NO integer period -> a_q flat. The
      pass condition is the peak being ABSOLUTELY present at the right q (the absolute-
      not-ordinal rule that caught the Allen GUE-pole mislabel), and ABSENT on the
      no-period classes.

  (2) THE a_q DECOY (the missing zoo member). The RF analog of the Wigner-renewal
      decoy: a matched-marginal-but-order-destroyed twin. We build TWO twins per
      calibrator:
        - order-scramble: permute the ISI multiset and re-cumsum (IDENTICAL marginal
          multiset, serial order destroyed).
        - iid-marginal:   resample ISIs i.i.d. from the empirical marginal and cumsum
          (matched marginal DISTRIBUTION, independent).
      The order-scramble itself converts bounded phase jitter into an accumulated
      random walk, so we report BOTH twins: comparing a_q(orig) vs a_q(scramble) vs
      a_q(iid) disentangles whether the RF verdict rides on the MARGINAL (a_q survives
      both twins -> marginal-encodable, the RF analog of an NNS downgrade) or on
      genuine non-marginal serial ORDER (a_q collapses under scramble -> order-borne).
      We read the marginal observable ks_gue_q alongside, so the same run shows
      a_q vs ks_gue side by side per calibrator.

  (3) APPARATUS OPERATORS THROUGH PERIOD-KNOWN CALIBRATORS (no-false-POSITIVE gate).
      Push the apparatus stage through the zoo and demand the known answer survives:
        - dead-time on poisson / GUE: must NOT inject a spurious a_q peak (a fake
          period out of a refractory hole).
        - thinning on periodic_q7: the real a_q=7 must SURVIVE finite efficiency
          (not be erased -> a false "no period").

This is the RF-side counterpart of longrange_discriminator.validate() +
trial_psth_unfold.decoy_battery. It does NOT touch the spacing path; it exercises
arithmetic_toolkit.joint_q_profile (THE RF engine) directly.
"""
from __future__ import annotations

import os
import sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
# signal_gen re-uses riemann_explorer/scanner; its in-file path is de-identified
# to a literal '$HOME' that does not resolve, so add the sibling tool here.
_RIEMANN = os.path.join(os.path.dirname(os.path.dirname(_ROOT)), "riemann_explorer")
for p in (_HERE, _ROOT, _RIEMANN, os.path.expanduser(os.path.expanduser("~/fmexplorer/riemann_explorer"))):
    if p not in sys.path:
        sys.path.insert(0, p)

from arithmetic_toolkit import joint_q_profile
from calibrator_panel import STATIONARY_CALIBRATORS
from instrument_confound import apply_deadtime, random_thin, mean_isi

Q_MAX = 30
N_POINTS = 400


def _gen_rigid_grid_jittered(seed):
    """POSITIVE CONTROL for the decoy: events at a rigid 7-grid with LARGE i.i.d.
    POSITION jitter (bounded phase). The ISI marginal is BROAD (7 +/- big), so the
    period is NOT in the marginal — it lives in the bounded-phase serial ORDER (each
    interval compensates the last). a_q should read it on the original and the
    order-scramble should DESTROY it (-> ORDER_BORNE). If so, the test can detect
    non-marginal period structure, and periodic_q7's MARGINAL_ENCODABLE verdict is a
    true property of that (near-delta-marginal) substrate, not a blind test."""
    rng = np.random.default_rng(seed)
    t = np.arange(1, N_POINTS + 1, dtype=np.float64) * 7.0 \
        + rng.uniform(-1.0, 1.0, N_POINTS)      # bounded phase, broad ISI marginal
    return np.sort(t)


# Known a_q answer per calibrator: the integer period(s) the RF engine SHOULD see,
# or () for the no-integer-period classes (must stay flat).
KNOWN_PERIODS = {
    "poisson": (),
    "beta=1_GOE": (),
    "beta=2_GUE": (),
    "beta=4_GSE": (),
    "zeta_first_400": (),
    "uniform_jitter": (),
    "periodic_q7": (7,),
    "mixed_q7_q12": (7, 12),
    "rigid_grid_jittered": (7,),
}

# the zoo plus the order-borne positive control
CALIBRATORS = STATIONARY_CALIBRATORS + [("rigid_grid_jittered", _gen_rigid_grid_jittered)]


# ─── a_q observable extraction ────────────────────────────────────────────────

def aq_profile(t, q_max=Q_MAX):
    """Return (peak_q, peak_norm_amp, df) for the indicator-mode RF a_q spectrum.

    peak_norm_amp = rf_amplitude_q_normalized at the strongest q in 2..q_max — how
    far the dominant period stands above the mean a_q band (1.0 = no structure).
    """
    df = joint_q_profile(np.asarray(t, float), q_max=q_max)
    sub = df[df.q >= 2]
    amps = sub.rf_amplitude_q_normalized.to_numpy()
    if amps.size == 0 or not np.isfinite(amps).any():
        return 0, float("nan"), df
    i = int(np.nanargmax(amps))
    return int(sub.q.to_numpy()[i]), float(amps[i]), df


def aq_at(df, q):
    """Normalized a_q amplitude at a specific q."""
    row = df[df.q == q]
    if row.empty:
        return float("nan")
    return float(row.rf_amplitude_q_normalized.iloc[0])


def ksgue_at(df, q):
    row = df[df.q == q]
    if row.empty:
        return float("nan")
    return float(row.ks_gue_q.iloc[0])


# ─── marginal-preserving twins ────────────────────────────────────────────────

def order_scramble(t, rng):
    """Permute the ISI multiset and re-cumsum: IDENTICAL marginal multiset, serial
    order destroyed. The RF analog of the Wigner-renewal decoy."""
    t = np.sort(np.asarray(t, float))
    d = np.diff(t)
    d = d[d > 0]
    rng.shuffle(d)
    return t[0] + np.concatenate([[0.0], np.cumsum(d)])


def iid_marginal(t, rng):
    """Resample ISIs i.i.d. from the empirical marginal and cumsum: matched marginal
    DISTRIBUTION, independent. Distinguishes 'bounded-phase order' from the multiset."""
    t = np.sort(np.asarray(t, float))
    d = np.diff(t)
    d = d[d > 0]
    draw = rng.choice(d, size=d.size, replace=True)
    return t[0] + np.concatenate([[0.0], np.cumsum(draw)])


# ═════════════════════════════════════════════════════════════════════════════
# (1) + (2)  ground-truth + decoy
# ═════════════════════════════════════════════════════════════════════════════

def calibrate_floor(n_seeds=8):
    """The a_q noise floor. The MAX of rf_amplitude_q_normalized over ~29 q-bands
    is NOT ~1 — extreme-value inflation over many bands puts it ~4 even for a
    structureless process. The no-period classes ARE that calibration: a genuine
    period must clear their peak distribution, not a guessed constant. Returns
    (floor_95, samples) where floor_95 is the 95th pct of no-period peak amps."""
    peaks = []
    for name, gen in CALIBRATORS:
        if KNOWN_PERIODS.get(name, ()):       # skip the period-bearing classes
            continue
        for s in range(n_seeds):
            t = np.sort(np.asarray(gen(s), float))
            if t.size < 50:
                continue
            _, a, _ = aq_profile(t)
            if np.isfinite(a):
                peaks.append(a)
    peaks = np.asarray(peaks)
    return float(np.percentile(peaks, 95)), peaks


def run_ground_truth_and_decoy(n_seeds=8):
    rng = np.random.default_rng(20260604)
    floor, fp = calibrate_floor(n_seeds)
    print("=" * 78)
    print("(1) a_q POLE-ABSOLUTE GROUND TRUTH  +  (2) a_q ORDER/MARGINAL DECOY")
    print("=" * 78)
    print(f"a_q noise floor (no-period classes): median {np.median(fp):.2f}, "
          f"max {fp.max():.2f}, 95th pct = {floor:.2f}  (n={fp.size})")
    print("  -> a genuine period must clear this floor; it is NOT ~1 (extreme-value")
    print("     inflation of a normalized spectrum max over ~29 bands).")
    print("-" * 78)
    print(f"{'calibrator':<18}{'known':>7}{'peak_q':>7}{'aq@pk':>8}"
          f"{'aq_scr':>8}{'aq_iid':>8}{'ksgue@pk':>9}  verdict")
    print("-" * 78)
    summary = {"_floor95": floor}
    for name, gen in CALIBRATORS:
        known = KNOWN_PERIODS.get(name, ())
        pk_q, pk_a, scr_a, iid_a, ks_a = [], [], [], [], []
        for s in range(n_seeds):
            t = np.sort(np.asarray(gen(s), float))
            if t.size < 50:
                continue
            q, a, df = aq_profile(t)
            # read a_q at the known period if there is one, else at the observed peak
            ref_q = known[0] if known else q
            ts = order_scramble(t, rng)
            ti = iid_marginal(t, rng)
            _, _, dfs = aq_profile(ts)
            _, _, dfi = aq_profile(ti)
            pk_q.append(q); pk_a.append(aq_at(df, ref_q))
            scr_a.append(aq_at(dfs, ref_q)); iid_a.append(aq_at(dfi, ref_q))
            ks_a.append(ksgue_at(df, ref_q))
        if not pk_a:
            continue
        from collections import Counter
        modal_q = Counter(pk_q).most_common(1)[0][0]
        m_pk, m_scr, m_iid = np.nanmedian(pk_a), np.nanmedian(scr_a), np.nanmedian(iid_a)
        m_ks = np.nanmedian(ks_a)
        # verdict logic, against the CALIBRATED floor (not a guessed constant)
        if not known:
            verd = "FLAT_OK" if m_pk < floor else f"SPURIOUS_PEAK@{modal_q}(amp{m_pk:.1f})"
        else:
            present = m_pk >= floor and modal_q in known
            if not present:
                verd = (f"BELOW_FLOOR (peak@{modal_q} amp{m_pk:.1f} < floor{floor:.1f})"
                        if modal_q in known or m_pk < floor
                        else f"WRONG_PEAK@{modal_q}")
            else:
                # marginal-vs-order: does the peak survive the twins?
                scr_keep = m_scr / m_pk if m_pk else float("nan")
                iid_keep = m_iid / m_pk if m_pk else float("nan")
                if scr_keep < 0.4:
                    verd = f"ORDER_BORNE (scr {scr_keep:.0%} of peak)"
                elif iid_keep > 0.6:
                    verd = f"MARGINAL_ENCODABLE (iid {iid_keep:.0%})"
                else:
                    verd = f"MIXED (scr {scr_keep:.0%}, iid {iid_keep:.0%})"
        kstr = ",".join(map(str, known)) if known else "-"
        print(f"{name:<18}{kstr:>7}{modal_q:>7}{m_pk:>8.2f}{m_scr:>8.2f}"
              f"{m_iid:>8.2f}{m_ks:>9.3f}  {verd}")
        summary[name] = dict(known=known, peak_q=modal_q, aq_peak=m_pk,
                             aq_scramble=m_scr, aq_iid=m_iid, ksgue=m_ks, verdict=verd)
    print("-" * 78)
    print("FLAT_OK on no-period classes = no false a_q period (pole-absolute vs floor).")
    print("ORDER_BORNE = a_q carries non-marginal serial structure (the marginal")
    print("  surrogates destroy it) -> a genuine non-marginal observable, UNLIKE the")
    print("  NNS downgrade. MARGINAL_ENCODABLE = a_q rides the marginal (NNS-style).")
    return summary, floor


# ═════════════════════════════════════════════════════════════════════════════
# (3)  apparatus operators through period-known calibrators
# ═════════════════════════════════════════════════════════════════════════════

def run_apparatus_gate(floor, n_seeds=8):
    rng = np.random.default_rng(7654321)
    print("\n" + "=" * 78)
    print("(3) APPARATUS OPERATORS THROUGH PERIOD-KNOWN CALIBRATORS")
    print("=" * 78)
    print(f"  (gate against the calibrated a_q floor = {floor:.2f})")

    # 3a. dead-time on no-period classes must NOT inject a spurious a_q peak.
    #     A structureless process already peaks at ~floor (extreme-value); the test
    #     is INJECTION = post clearing the floor where pre did not (Delta above floor),
    #     not an absolute peak height.
    print("\n  3a. dead-time injection test (must NOT push a_q peak above floor):")
    print(f"      {'class':<14}{'tau/ISI':>8}{'aq_pk_pre':>11}{'aq_pk_post':>12}  gate")
    for name in ("poisson", "beta=2_GUE"):
        gen = dict(STATIONARY_CALIBRATORS)[name]
        for tau_frac in (0.3, 0.6):
            pre, post = [], []
            for s in range(n_seeds):
                t = np.sort(np.asarray(gen(s), float))
                tau = tau_frac * mean_isi(t)
                _, a0, _ = aq_profile(t)
                td = apply_deadtime(t, tau)
                if td.size < 50:
                    continue
                _, a1, _ = aq_profile(td)
                pre.append(a0); post.append(a1)
            m0, m1 = np.nanmedian(pre), np.nanmedian(post)
            gate = "OK (no injection)" if m1 < floor else "FAIL: spurious period"
            # per-realization companion (see 3b note): the fraction of
            # individual trains in which dead time DID push a_q above floor
            _p1 = np.asarray(post, float)
            _okm = np.isfinite(_p1)
            inj = float(np.mean(_p1[_okm] >= floor)) if _okm.any() else float("nan")
            print(f"      {name:<14}{tau_frac:>8.1f}{m0:>11.2f}{m1:>12.2f}  {gate}"
                  f"   [per-train injection {inj:.2f}]")

    # 3b. thinning on periodic_q7 — the real a_q=7 must SURVIVE finite efficiency.
    print("\n  3b. thinning survival test (real a_q=7 must stay above floor):")
    print(f"      {'p_keep':>8}{'peak_q':>8}{'aq@7':>8}  gate")
    gen7 = dict(STATIONARY_CALIBRATORS)["periodic_q7"]
    for p_keep in (1.0, 0.7, 0.4):
        pkq, a7 = [], []
        for s in range(n_seeds):
            t = np.sort(np.asarray(gen7(s), float))
            tt = t if p_keep >= 1.0 else random_thin(t, p_keep, rng)
            if tt.size < 50:
                continue
            q, _, df = aq_profile(tt)
            pkq.append(q); a7.append(aq_at(df, 7))
        from collections import Counter
        modal = Counter(pkq).most_common(1)[0][0]
        m7 = np.nanmedian(a7)
        gate = "OK" if (m7 >= floor) else "FAIL: period erased"
        # PER-REALIZATION ARM (2026-08-17, TOOLKIT §9 estimand rule). The
        # median across seeds says what a TYPICAL train does; the decoy
        # question — "did efficiency loss erase a genuine period?" — is asked
        # of ONE train. A median can sit comfortably above the floor while a
        # large minority of individual trains fall below it, and only the
        # per-train rate can see that. The per-seed values already exist in
        # a7; they were averaged away before being looked at. ADDITIVE: the
        # median-based `gate` above is unchanged.
        _a7 = np.asarray(a7, float)
        _ok = np.isfinite(_a7)
        surv = float(np.mean(_a7[_ok] >= floor)) if _ok.any() else float("nan")
        print(f"      {p_keep:>8.1f}{modal:>8}{m7:>8.2f}  {gate}"
              f"   [per-train survival {surv:.2f}]")
    print("\n  Dead time is subtractive (carves small spacings) — it cannot ADD a")
    print("  periodic comb, so 3a is the expected-pass control. 3b probes the real")
    print("  exposure: efficiency loss erasing a genuine period (the a_q analog of")
    print("  thinning driving NNS toward Poisson).")


if __name__ == "__main__":
    _, floor = run_ground_truth_and_decoy()
    run_apparatus_gate(floor)
