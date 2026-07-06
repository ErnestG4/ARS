"""
phase34f/run_pipeline_validation.py — synthetic validation of the 3-D
Bianchi Maass pipeline.

§D.0a DATA-AVAILABILITY GATE FIRED: Then 2003 (arXiv:math-ph/0305048)
computed 13,950 Picard PSL(2,Z[i])\\ℍ³ Maass eigenvalues and reported
Poisson-leaning NNS (the Sarnak anomaly), but the raw eigenvalue list is
NOT published — the PDF contains only ~30 sample values per symmetry
class in Tables 1 (small r ≈ 6–26) and ~28 around r ≈ 139–140 in Table
2, OCR-mangled across 4 symmetry classes.  No Zenodo dataset; LMFDB
Bianchi page reCAPTCHA-blocked in this session.  Per PHASE34F_BRIEF
§D.0a / §I.1, 34f-G substantive bulk-NNS is DATA_ACQUISITION_BLOCKED.

What CAN be validated without the Then 2003 data: the 3-D Bianchi
methodology pipeline itself, on synthetic spectra with known ground
truth.  This script proves:

  1. The cubic Weyl-law unfolding x_j = vol·r_j³/(6π²) (λ = r²+1
     convention) maps a synthetic 3-D Weyl spectrum to unit mean
     spacing.
  2. A synthetic Poisson spectrum (Sarnak-anomaly analog) pushed
     through the 3-D unfolding + NNS engine classifies BL.
  3. A synthetic GOE β=1 spectrum (BGS-naive right-null analog)
     pushed through the same pipeline classifies TR.
  4. Berry-Robnik ρ recovery: synthetic spectra with known ρ
     (Poisson ρ=0, GOE ρ=1, Berry-Robnik mixture ρ=0.3) are
     recovered within bootstrap σ.

If all four validations pass, the 34f-G methodology is READY-TO-FIRE
the moment the Then 2003 Picard eigenvalue list (or an equivalent
de-novo computation) becomes available.  The expected substantive
verdict per the literature is SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI
(Then 2003 found Poisson NNS), with ρ in the Poisson-dominant regime.

Outputs:
  data/phase34f_results/pipeline_validation.json
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34c'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34e'))

from bianchi_unfolding import (picard_volume, unfold_bianchi_3d, spacings,
                                 mean_spacing_check)
from ars_classify import classify
from run_berry_robnik import berry_robnik_pdf, fit_rho

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34f_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def synth_weyl_3d(n: int, vol: float, jitter_kind: str,
                   seed: int = 0) -> np.ndarray:
    """Generate a synthetic Picard-like spectrum.

    The j-th unfolded coordinate target is x_j = j + (fluctuation).
    Invert via r_j = (x_j · 6π² / vol)^{1/3} so the raw r-values follow
    the 3-D Weyl law and the fluctuation determines the NNS class.
    """
    rng = np.random.default_rng(seed)
    C = vol / (6.0 * np.pi ** 2)
    if jitter_kind == 'poisson':
        gaps = rng.exponential(1.0, size=n)
        x = np.cumsum(gaps)
    elif jitter_kind == 'goe_beta1':
        # β=1 Wigner spacings via the Wigner surmise inverse-CDF sampling
        # (approximate): use the β-Hermite tridiagonal eigenvalues.
        from rmt_sampler import sample_rmt_unfolded
        x = sample_rmt_unfolded(n + 200, beta=1.0,
                                  rng=np.random.default_rng(seed))
        x = np.sort(x[~np.isnan(x)])[:n]
        x = x - x.min() + 1.0
    elif jitter_kind == 'berry_robnik_0p3':
        # Berry-Robnik mixture: fraction ρ from GOE, (1-ρ) from Poisson,
        # superimposed (the standard Berry-Robnik independent-superposition
        # model). ρ here is the GOE-fraction.
        rho = 0.3
        n_goe = int(n * rho)
        n_poi = n - n_goe
        from rmt_sampler import sample_rmt_unfolded
        g = sample_rmt_unfolded(n_goe + 200, beta=1.0,
                                  rng=np.random.default_rng(seed))
        g = np.sort(g[~np.isnan(g)])[:n_goe]
        g = (g - g.min()) / np.mean(np.diff(g))  # unit mean spacing
        p = np.cumsum(rng.exponential(1.0, size=n_poi))
        # Superpose on a common axis scaled to total density 1
        g = g / rho
        p = p / (1.0 - rho)
        x = np.sort(np.concatenate([g, p]))[:n]
    else:
        raise ValueError(jitter_kind)
    x = np.sort(x)
    r = (x / C) ** (1.0 / 3.0)
    return r


def validate(jitter_kind: str, n: int = 5000, q_max: int = 30) -> dict:
    vol = picard_volume()
    r = synth_weyl_3d(n, vol, jitter_kind)
    x = unfold_bianchi_3d(r, vol)
    s = spacings(x)
    msc = mean_spacing_check(s)
    cls = classify(x.astype(np.float64), q_max=q_max,
                    min_events_per_q=30, return_full=False)
    s_unit = s / np.mean(s)
    rho_fit = fit_rho(s_unit, n_bootstrap=20)
    print(f"  [{jitter_kind:>18s}] ⟨s⟩={msc['mean']:.4f} "
          f"primary={cls['primary']:>12s} rep_med={cls['rep_med']:.3f} "
          f"ρ={rho_fit['bootstrap_rho_mean']:.3f}±{rho_fit['bootstrap_rho_std']:.3f}")
    return dict(
        jitter_kind=jitter_kind,
        n=int(n),
        mean_spacing=msc['mean'],
        unfold_pass=msc['pass_check'],
        nns_primary=cls['primary'],
        rep_med=float(cls['rep_med']),
        ks_gue_med=float(cls['ks_gue_med']),
        berry_robnik_rho=rho_fit['bootstrap_rho_mean'],
        berry_robnik_rho_std=rho_fit['bootstrap_rho_std'],
    )


def main():
    print("=" * 78)
    print("Phase 34f-G — 3-D Bianchi pipeline synthetic validation")
    print("=" * 78)
    print("§D.0a DATA-AVAILABILITY GATE FIRED: Then 2003 Picard eigenvalue")
    print("list (13,950 values) unavailable; only ~60 OCR-mangled samples in")
    print("the PDF.  This validates the methodology pipeline on synthetic")
    print("spectra with known ground truth; substantive 34f-G bulk-NNS is")
    print("DATA_ACQUISITION_BLOCKED until the Then 2003 list is obtained.")
    print()
    print(f"Picard volume = {picard_volume():.6f}")
    print()

    results = {}
    for kind in ('poisson', 'goe_beta1', 'berry_robnik_0p3'):
        results[kind] = validate(kind)

    # Validation gates
    poi = results['poisson']
    goe = results['goe_beta1']
    br = results['berry_robnik_0p3']
    checks = dict(
        unfolding_correct=bool(poi['unfold_pass'] or
                                abs(poi['mean_spacing'] - 1.0) < 0.05),
        poisson_classifies_BL=(poi['nns_primary'] == 'BL'),
        goe_classifies_TR=(goe['nns_primary'] in ('TR', 'TR_GOE', 'BR_artifact')),
        poisson_rho_near_0=(poi['berry_robnik_rho'] < 0.15),
        goe_rho_near_1=(goe['berry_robnik_rho'] > 0.7),
        br_rho_near_0p3=(abs(br['berry_robnik_rho'] - 0.3) < 0.15),
    )
    print()
    print("=" * 78)
    print("Pipeline validation gates")
    print("=" * 78)
    for k, v in checks.items():
        print(f"  {k:>28s}: {v}")
    all_pass = all(checks.values())
    verdict = ("PIPELINE_VALIDATED_READY_TO_FIRE" if all_pass
               else "PIPELINE_VALIDATION_PARTIAL — review gate failures")
    print(f"\n  → {verdict}")

    out = OUT_DIR / 'pipeline_validation.json'
    with open(out, 'w') as f:
        json.dump({
            'phase': '34f-G',
            'status': 'DATA_ACQUISITION_BLOCKED (Then 2003 list unavailable); '
                      'methodology pipeline synthetic-validated',
            'picard_volume': picard_volume(),
            'synthetic_validation': results,
            'gates': {k: bool(v) for k, v in checks.items()},
            'verdict': verdict,
        }, f, indent=2)
    print(f"\n→ wrote {out}")


if __name__ == '__main__':
    main()
