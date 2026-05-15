"""
phase34d/run_cross_phase.py — cross-phase joint statement.

Per Phase 34d brief §C: Eisenstein-prime-angle substrate is structurally
tied to L(·, χ₋₃) (the Legendre-symbol Dirichlet character mod 3). Phase
34c classified the real-Dirichlet stratum NULL_IN_ORTHOGONAL_CHANNELS_BEYOND_RMT.
If Phase 34d-E lands NULL_BEYOND_HECKE, the joint statement is:
  TWO ARS readouts of the same underlying arithmetic object (Q(√−3)) at
  two different spectral coordinates BOTH land null beyond their respective
  right nulls.

This is convergent-null across coordinates of one arithmetic substrate —
stronger than direction-match. Phase 34f Bianchi-Maass-on-PSL(2, O_K) would
add the third coordinate.

Outputs
-------
data/phase34d_results/cross_phase_34d_to_34c_dirichlet.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34d_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_eisenstein_substantive():
    p = OUT_DIR / 'eisenstein_substantive_ars.json'
    if not p.exists():
        return None
    with open(p) as f:
        return json.load(f)


def load_phase34c_dirichlet_real():
    p = Path(ROOT_DIR) / 'data' / 'phase34c_results' / 'surveys.json'
    if not p.exists():
        return None
    with open(p) as f:
        surv = json.load(f)
    panels = surv.get('panels', {})
    return panels.get('dirichlet-real-Sp')


def extract_verdict(panel: dict) -> dict:
    """Pull the headline verdict elements from a panel dict.

    Handles both Phase 34d (this phase: keys nns_full, vs_poisson, vs_cue)
    and Phase 34c surveys (keys nns_reproduction, vs_poisson_wrong_null,
    vs_rmt_right_null).
    """
    if panel is None:
        return {'status': 'absent'}
    out = {'status': 'present'}

    # NNS: handle both naming conventions
    nns = panel.get('nns_full') or panel.get('nns') or panel.get('nns_reproduction')
    if nns:
        out['nns_primary'] = nns.get('primary')
        out['nns_rep_med'] = nns.get('rep_med')
        out['nns_ks_gue'] = nns.get('ks_gue_med')

    # vs nulls — try 34d keys first, then 34c keys
    for our_key, c_key in (('vs_poisson', 'vs_poisson_wrong_null'),
                            ('vs_cue', 'vs_rmt_right_null')):
        v = panel.get(our_key) or panel.get(c_key)
        if v is None:
            continue
        # 34d uses spike_qs / dominant_prime_per_q_real / dom_per_q_pvalue
        # 34c uses rf_spike_qs_real / rf_survivors etc.
        spikes = v.get('spike_qs')
        if spikes is None:
            spikes = v.get('rf_spike_qs_real', [])
        survivors = v.get('rf_survivors', {})
        p_at = {}
        if 'p_values_per_q' in v:
            p_at = {int(q): float(p) for q, p in v['p_values_per_q'].items()
                    if int(q) in (spikes or [])}
        elif survivors:
            # 34c survivors is a dict keyed by q-string of bools
            p_at = {int(q): None for q in spikes if str(q) in survivors}
        out[our_key] = {
            'spike_qs': spikes,
            'p_values_at_spikes': p_at,
            'dom_per_q_real': v.get('dominant_prime_per_q_real')
                              or v.get('dom_per_q_real'),
            'dom_per_q_pvalue': v.get('dom_per_q_pvalue'),
        }
    return out


def main():
    print("=" * 78)
    print("Phase 34d cross-phase: Eisenstein angle ↔ 34c χ₋₃ Sp stratum")
    print("=" * 78)

    eis = load_eisenstein_substantive()
    dir_real = load_phase34c_dirichlet_real()

    eis_verdict = extract_verdict(
        (eis or {}).get('panels', {}).get('eisenstein_X1e6'))
    dir_verdict = extract_verdict(dir_real)

    print("\nEisenstein X=10⁶ (this phase, angle coordinate):")
    print(json.dumps(eis_verdict, indent=2))
    print("\nPhase 34c Dirichlet real-Sp (χ₋₃ stratum, zero coordinate):")
    print(json.dumps(dir_verdict, indent=2))

    # Joint statement: each substrate's "null beyond right null" status
    # is captured by spike_qs == [] against the right null
    def is_null_beyond_right_null(verdict):
        if verdict.get('status') != 'present':
            return None
        vc = verdict.get('vs_cue')
        if vc is None:
            return None
        return (not vc.get('spike_qs', None))  # empty list or None → null

    eis_null = is_null_beyond_right_null(eis_verdict)
    dir_null = is_null_beyond_right_null(dir_verdict)

    if eis_null is None or dir_null is None:
        joint = "INDETERMINATE (one or both panels missing right-null comparison)"
    elif eis_null and dir_null:
        joint = "CONVERGENT_NULL_ACROSS_COORDINATES (both null beyond right null)"
    elif eis_null and not dir_null:
        joint = "DIVERGENT (angle null, zero non-null)"
    elif not eis_null and dir_null:
        joint = "DIVERGENT (angle non-null, zero null)"
    else:
        joint = "CONVERGENT_SIGNAL (both non-null)"

    out = {
        'phase': '34d',
        'cross_phase': '34d-E (Eisenstein angles) ↔ 34c Dirichlet real-Sp (χ₋₃)',
        'arithmetic_object': 'Q(√−3)',
        'coordinates': {
            'angle': '34d-E prime-angle on [0, π/3)',
            'zero': '34c real-character Dirichlet L-zeros (χ₋₃ stratum)',
        },
        'eisenstein_verdict': eis_verdict,
        'dirichlet_real_verdict': dir_verdict,
        'joint_statement': joint,
        'note': (
            "If both null beyond respective right nulls: two ARS readouts of "
            "one arithmetic object Q(√−3) at distinct spectral coordinates "
            "are convergently featureless. This forward-binds Phase 34f "
            "Bianchi-Maass-on-PSL(2, O_K) as the third coordinate."
        ),
    }

    out_path = OUT_DIR / 'cross_phase_34d_to_34c_dirichlet.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\n→ wrote {out_path}")
    print(f"\nJOINT STATEMENT: {joint}")


if __name__ == '__main__':
    main()
