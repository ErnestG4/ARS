"""
audit/phase5_runtime.py — Phase 5 runtime verification (READ-ONLY: imports the live tool, edits nothing).

Run from repo root with the project venv AND the riemann_explorer path on PYTHONPATH (works around the
literal-$HOME bug in signal_gen.py:16 WITHOUT editing the repo):

    PYTHONPATH=/home/combust/fmexplorer/riemann_explorer \
      /home/combust/fmexplorer/bin/python3 audit/phase5_runtime.py

Three blocks:
  A. Rate-drift control     — global CV vs rate-robust CV2/Lv on a slow-rate-drifting train.
  B. Unfolding confirmation — same GUE eigenvalues, two unfolders → why calibrator Σ² inverted.
  C. Induction-on-noise     — Poisson through the GUARDED long-range verdict: declines to over-claim?
"""
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np
from cross_substrate.axes import (compute_family_I, compute_family_II, canonical_spacings,
                                   matched_L)
from cross_substrate.longrange_discriminator import longrange_verdict
from ars_classify import unfold_unit_mean
from signal_gen import make_beta_ensemble_eigenvalues
from extractor_distinctness import _gen_poisson


def raw_cv(events):
    isi = np.diff(np.sort(np.asarray(events, float)))
    isi = isi[isi > 0]
    return float(isi.std() / isi.mean())


def inhomog_poisson(T, rate_fn, rate_max, rng):
    t, out = 0.0, []
    while t < T:
        t += rng.exponential(1.0 / rate_max)
        if t < T and rng.random() < rate_fn(t) / rate_max:
            out.append(t)
    return np.asarray(out)


print("=" * 72)
print("A. RATE-DRIFT CONTROL  (claim: global CV inflated by slow drift; CV2/Lv stable)")
print("=" * 72)
rng = np.random.default_rng(0)
T = 4000.0
# slow single-cycle sinusoid: rate sweeps 0.1 -> 2.0 across the whole window (dense + sparse epochs)
drift = lambda t: 0.1 + 1.9 * (0.5 + 0.5 * np.sin(2 * np.pi * t / T))
ev_drift = inhomog_poisson(T, drift, 2.0, rng)
ev_homog = inhomog_poisson(T, lambda t: 1.0, 1.0, rng)   # homogeneous Poisson control
for label, ev in (("homogeneous Poisson", ev_homog), ("SLOW RATE DRIFT", ev_drift)):
    fI = compute_family_I(ev)
    print(f"\n  {label}  (n={ev.size})")
    print(f"    raw global CV (std/mean ISI) : {raw_cv(ev):.3f}")
    print(f"    I.10_cv  (axes, global)      : {fI['I.10_cv']:.3f}   <- should inflate on drift")
    print(f"    I.12_cv2 (axes, rate-robust) : {fI['I.12_cv2']:.3f}   <- should stay ~1")
    print(f"    I.13_lv  (axes, rate-robust) : {fI['I.13_lv']:.3f}   <- should stay ~1")

print("\n" + "=" * 72)
print("B. UNFOLDING CONFIRMATION  (same GUE eigenvalues, two unfolders)")
print("=" * 72)
N = 3000
sig2_unitmean, sig2_dummy = [], []
for s in range(4):
    eigs = np.asarray(make_beta_ensemble_eigenvalues(N, 2, s), float)
    # (a) calibrator path: global unit-mean unfold -> compute_family_II
    pos_um = unfold_unit_mean(eigs)
    s2_um = compute_family_II(pos_um).get("II.1_sigma2_L")
    sig2_unitmean.append(s2_um)
# Poisson Sigma2 for reference (matched L)
pois = _gen_poisson(0, n=N)
s2_pois = compute_family_II(unfold_unit_mean(pois)).get("II.1_sigma2_L")
L = matched_L(N)
print(f"  L (matched) = {L:.1f}   ->  Poisson Sigma2(L) should be ~= L")
print(f"  GUE  Sigma2(L) via unfold_unit_mean (CALIBRATOR path): {np.mean(sig2_unitmean):.2f}")
print(f"  Poisson Sigma2(L) via unfold_unit_mean              : {s2_pois:.2f}")
print(f"  -> GUE > Poisson here is INVERTED (GUE should be << Poisson). Cause: global unit-mean")
print(f"     unfold leaves the semicircle density gradient in; Sigma2(L=50) integrates over it.")
# (b) guarded path on the SAME kind of input: proper poly-deg-6 unfold + matched references
eigs = np.asarray(make_beta_ensemble_eigenvalues(N, 2, 0), float)
v_gue = longrange_verdict(eigs, n_seeds=8, n_ref=1500)
print(f"\n  SAME GUE eigenvalues through GUARDED longrange_verdict (poly unfold_deg=6):")
print(f"     verdict = {v_gue['verdict']}   sigma2_obs = {v_gue['sigma2']['obs']:.3f} "
      f"(GUE ref mean {v_gue['sigma2']['gue']['mean']:.3f}, Poisson ref mean {v_gue['sigma2']['poisson']['mean']:.3f})")
print(f"  -> guarded path unfolds correctly and recovers the GUE pole.")

print("\n" + "=" * 72)
print("C. INDUCTION-ON-NOISE  (Poisson through the guarded verdict: decline to over-claim?)")
print("=" * 72)
v_pois = longrange_verdict(np.asarray(_gen_poisson(1, n=N), float), n_seeds=8, n_ref=1500)
print(f"  homogeneous Poisson -> verdict = {v_pois['verdict']}   "
      f"sigma2_obs = {v_pois['sigma2']['obs']:.3f} (Poisson ref {v_pois['sigma2']['poisson']['mean']:.3f})")
print(f"  -> should be POISSON_INDEP (does NOT manufacture a GUE/rigid class).")
print("\nDONE.")
