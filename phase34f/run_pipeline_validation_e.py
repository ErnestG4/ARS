"""
phase34f/run_pipeline_validation_e.py — synthetic validation of the
3-D Bianchi Maass pipeline on the **Bianchi-Z[ω] (Q(√−3))** substrate,
for the 34f-E FIRST-MEASUREMENT leg.

Parallel to phase34f/run_pipeline_validation.py (34f-G Picard), with
the substrate-correct PINNED Humbert-direct volume
bianchi_z_omega_volume() ≈ 0.16915693 (= √3·L(2,χ_{-3})/8) in place of
picard_volume().  Same cubic Weyl-law unfolding x_j = vol·r_j³/(6π²),
same λ = r²+1 convention, same substrate-agnostic NNS engine +
synthetic-validated Berry-Robnik fitter.

§D.0a DATA-AVAILABILITY GATE FIRES (zomega_loader.data_availability_gate):
no accessible Bianchi-Z[ω] Maass eigenvalue dataset (LMFDB Bianchi
reCAPTCHA-blocked + primarily holomorphic; de-novo Hejhal-on-ℍ³ for the
order-6 unit group is the multi-week cost — PHASE34F_BRIEF §C.2/§C.3).
Substantive 34f-E-Δ = DATA_ACQUISITION_BLOCKED.

ASYMMETRIC-LABEL DISCIPLINE (PHASE34F_BRIEF §E.2 / METHODS §E): 34f-E-Δ
is a FIRST-MEASUREMENT substrate (no published anchor — Then 2003
covered Picard only; the Sarnak-anomaly extension to PSL(2,Z[ω]) is a
structural Hecke-algebra prediction, empirically unconfirmed).  This is
NOT a replication leg.  Pipeline-validation verdict on success:
PIPELINE_VALIDATED_READY_TO_FIRE; the substantive verdict on data
acquisition would be SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA /
..._WITH_FIELD_SHIFT / NO_ANOMALY_AT_PSL2_Z_OMEGA (PHASE34F_BRIEF §E.2).

Orbifold note (PHASE34F_BRIEF §B.2): PSL(2,Z[ω]) has elliptic fixed
points of orders 2 AND 3 (order-6 unit group), vs Picard's order-2
only.  bulk-NNS classification is robust to the extra Selberg
trace-formula elliptic terms (Test 1 is unfolding-scale-invariant);
the quantitative Berry-Robnik ρ MAY shift versus 34f-G — that shift
is an open empirical question resolved only on real Z[ω] data, NOT
something the synthetic harness can model.  The harness validates the
generic pipeline machinery on the substrate-correct volume.

What this script proves (identical 6-gate structure to 34f-G):
  1. Cubic Weyl-law unfolding with the Z[ω] volume → unit mean spacing.
  2. Synthetic Poisson spectrum (Sarnak-anomaly analog) → BL.
  3. Synthetic GOE β=1 spectrum (BGS-naive right-null analog) → TR.
  4. Berry-Robnik ρ recovery on the synthetic-validated fitter:
     Poisson→≈0, GOE→≈1, BR-0.3→≈0.3 within bootstrap σ.

Outputs:
  data/phase34f_results/pipeline_validation_e.json
"""
from __future__ import annotations

import json
import os
import sys
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

from bianchi_unfolding import (bianchi_z_omega_volume, picard_volume,
                                unfold_bianchi_3d, spacings,
                                mean_spacing_check)
from zomega_loader import data_availability_gate, normalization_gate
from ars_classify import classify
from run_berry_robnik import fit_rho

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34f_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def synth_weyl_3d(n: int, vol: float, jitter_kind: str,
                   seed: int = 0) -> np.ndarray:
    """Generate a synthetic Bianchi-Z[ω]-like spectrum.

    Target unfolded coordinate x_j = j + (fluctuation); invert via
    r_j = (x_j · 6π² / vol)^{1/3} so raw r follows the 3-D Weyl law and
    the fluctuation sets the NNS class.  Identical construction to the
    34f-G Picard harness; only `vol` differs.
    """
    rng = np.random.default_rng(seed)
    C = vol / (6.0 * np.pi ** 2)
    if jitter_kind == 'poisson':
        gaps = rng.exponential(1.0, size=n)
        x = np.cumsum(gaps)
    elif jitter_kind == 'goe_beta1':
        from rmt_sampler import sample_rmt_unfolded
        x = sample_rmt_unfolded(n + 200, beta=1.0,
                                rng=np.random.default_rng(seed))
        x = np.sort(x[~np.isnan(x)])[:n]
        x = x - x.min() + 1.0
    elif jitter_kind == 'berry_robnik_0p3':
        rho = 0.3
        n_goe = int(n * rho)
        n_poi = n - n_goe
        from rmt_sampler import sample_rmt_unfolded
        g = sample_rmt_unfolded(n_goe + 200, beta=1.0,
                                rng=np.random.default_rng(seed))
        g = np.sort(g[~np.isnan(g)])[:n_goe]
        g = (g - g.min()) / np.mean(np.diff(g))
        p = np.cumsum(rng.exponential(1.0, size=n_poi))
        g = g / rho
        p = p / (1.0 - rho)
        x = np.sort(np.concatenate([g, p]))[:n]
        # Match the goe branch's "unit mean spacing, start at 1"
        # convention so the inverted r = (x/C)^{1/3} is strictly
        # positive (real Maass spectral parameters are > 0; an x=0
        # boundary point is a synthetic-construction artifact).  A
        # constant shift of x leaves all spacings — hence NNS, rep_med,
        # ks, and the Berry-Robnik ρ — invariant.
        x = x - x.min() + 1.0
    else:
        raise ValueError(jitter_kind)
    x = np.sort(x)
    r = (x / C) ** (1.0 / 3.0)
    return r


def validate(jitter_kind: str, n: int = 5000, q_max: int = 30) -> dict:
    vol = bianchi_z_omega_volume()
    r = synth_weyl_3d(n, vol, jitter_kind)
    # §D.0b normalization gate on the synthetic stream (proves the gate
    # passes substrate-correct inputs through the real pipeline path).
    normalization_gate(r=r, lam_convention="r2+1", volume=vol)
    x = unfold_bianchi_3d(r, vol)
    s = spacings(x)
    msc = mean_spacing_check(s)
    cls = classify(x.astype(np.float64), q_max=q_max,
                   min_events_per_q=30, return_full=False)
    s_unit = s / np.mean(s)
    rho_fit = fit_rho(s_unit, n_bootstrap=20)
    print(f"  [{jitter_kind:>18s}] ⟨s⟩={msc['mean']:.4f} "
          f"primary={cls['primary']:>12s} rep_med={cls['rep_med']:.3f} "
          f"ρ={rho_fit['bootstrap_rho_mean']:.3f}±"
          f"{rho_fit['bootstrap_rho_std']:.3f}")
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
    print("Phase 34f-E — Bianchi-Z[ω] (Q(√−3)) 3-D Bianchi pipeline "
          "synthetic validation")
    print("=" * 78)
    da = data_availability_gate()
    print(f"§D.0a DATA-AVAILABILITY GATE: {da['status']} — {da['reason']}")
    print("FIRST-MEASUREMENT substrate (no published anchor; Then 2003")
    print("covered Picard only).  Substantive 34f-E-Δ = "
          f"{da['substantive_verdict']}.")
    print("This validates the methodology pipeline on synthetic spectra")
    print("with known ground truth, on the substrate-correct Z[ω] volume.")
    print()
    print(f"Picard volume      = {picard_volume():.8f}  (34f-G, reference)")
    print(f"Bianchi-Z[ω] volume = {bianchi_z_omega_volume():.8f}  "
          f"(34f-E, PINNED Humbert-direct √3·L(2,χ_-3)/8)")
    print()

    results = {}
    for kind in ('poisson', 'goe_beta1', 'berry_robnik_0p3'):
        results[kind] = validate(kind)

    poi = results['poisson']
    goe = results['goe_beta1']
    br = results['berry_robnik_0p3']
    checks = dict(
        unfolding_correct=bool(poi['unfold_pass'] or
                               abs(poi['mean_spacing'] - 1.0) < 0.05),
        poisson_classifies_BL=(poi['nns_primary'] == 'BL'),
        goe_classifies_TR=(goe['nns_primary'] in
                           ('TR', 'TR_GOE', 'BR_artifact')),
        poisson_rho_near_0=(poi['berry_robnik_rho'] < 0.15),
        goe_rho_near_1=(goe['berry_robnik_rho'] > 0.7),
        br_rho_near_0p3=(abs(br['berry_robnik_rho'] - 0.3) < 0.15),
    )
    print()
    print("=" * 78)
    print("Pipeline validation gates (34f-E Bianchi-Z[ω])")
    print("=" * 78)
    for k, v in checks.items():
        print(f"  {k:>28s}: {v}")
    all_pass = all(checks.values())
    verdict = ("PIPELINE_VALIDATED_READY_TO_FIRE" if all_pass
               else "PIPELINE_VALIDATION_PARTIAL — review gate failures")
    print(f"\n  → {verdict}")
    print("  (substantive 34f-E-Δ remains DATA_ACQUISITION_BLOCKED; the")
    print("   FIRST-MEASUREMENT verdict labels are SARNAK_ANOMALY_FIRST_")
    print("   MEASUREMENT_AT_PSL2_Z_OMEGA / _WITH_FIELD_SHIFT / NO_ANOMALY")
    print("   _AT_PSL2_Z_OMEGA per PHASE34F_BRIEF §E.2 — never 'replication')")

    out = OUT_DIR / 'pipeline_validation_e.json'
    with open(out, 'w') as f:
        json.dump({
            'phase': '34f-E',
            'substrate_role': 'FIRST_MEASUREMENT',
            'status': 'DATA_ACQUISITION_BLOCKED (no accessible Bianchi-Z[ω] '
                      'Maass dataset; LMFDB reCAPTCHA-blocked / holomorphic, '
                      'de-novo Hejhal-on-ℍ³ multi-week per §C.3); '
                      'methodology pipeline synthetic-validated',
            'bianchi_z_omega_volume': bianchi_z_omega_volume(),
            'picard_volume_reference': picard_volume(),
            'data_availability_gate': da,
            'synthetic_validation': results,
            'gates': {k: bool(v) for k, v in checks.items()},
            'verdict': verdict,
            'prespec_substantive_verdict_labels': [
                'SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA',
                'SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA_WITH_FIELD_SHIFT',
                'NO_ANOMALY_AT_PSL2_Z_OMEGA',
            ],
        }, f, indent=2)
    print(f"\n→ wrote {out}")


if __name__ == '__main__':
    main()
