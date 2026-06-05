"""
cross_substrate/longrange_audit.py — point the falsification loop at the verdict's
OWN statistic. For each banked universality claim, compare the NNS (marginal)
verdict against the long-range class verdict (Σ²/Δ₃ vs GUE & renewal ensembles).
Which claims earn 'GUE class' (RIGID_GUE) and which collapse to 'marginal matches
GUE' (MARGINAL_ONLY)? Some confirm, some downgrade — that is the audit.

Controls (known answers): real GUE → RIGID_GUE; Poisson → not GUE either way;
Wigner-renewal decoy → MARGINAL_ONLY.
"""
from __future__ import annotations

import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_HERE, _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from longrange_discriminator import (longrange_verdict, ks_gue, wigner_renewal,
                                     gue_positions, poisson_positions)
import run_phase18_finding_validation as H

N_SEEDS = 12
AUDIT_L = 50.0      # fixed L + n_ref → one memoized reference ensemble for all rows
AUDIT_NREF = 2000


def _row(name, events):
    e = np.sort(np.asarray(events, dtype=np.float64))
    ks = ks_gue(e)
    v = longrange_verdict(e, L=AUDIT_L, n_seeds=N_SEEDS, n_ref=AUDIT_NREF)
    s2 = v.get("sigma2") or {}
    # marginal verdict from ks_gue (the NNS claim): GUE-like if ks_gue small
    nns = "GUE-marginal" if (ks is not None and ks < 0.06) else "not-GUE-marginal"
    cls = v["verdict"]
    obs_s2 = s2.get("obs", float("nan"))
    # GUARD: a properly-unfolded process cannot be much floppier than Poisson
    # (Σ²_Poisson(L)=L). σ² > L on a putative-GUE sequence ⇒ residual density trend
    # / mis-unfolding, NOT a real long-range readout. Don't call it a downgrade.
    if np.isfinite(obs_s2) and obs_s2 > AUDIT_L:
        upshot = "UNRELIABLE (σ²>Poisson → mis-unfolded, not a valid rigidity readout)"
    elif cls == "RIGID_GUE":
        upshot = "CONFIRMED GUE-class"
    elif nns == "GUE-marginal" and cls == "MARGINAL_ONLY":
        upshot = "marginal-only (verify unfolding; pooled⇒superposition expected)"
    elif cls == "INTERMEDIATE":
        upshot = "INTERMEDIATE"
    else:
        upshot = "n/a"
    print(f"  {name:20s} n={e.size:>6d}  ks_gue={ks:.3f} ({nns:16s})  "
          f"σ²={s2.get('obs', float('nan')):7.3f}  "
          f"[GUE {s2.get('gue',{}).get('mean',float('nan')):.2f} | "
          f"renewal {s2.get('renewal',{}).get('mean',float('nan')):.2f}]  "
          f"z_gue={s2.get('z_vs_gue',float('nan')):5.1f} z_ren={s2.get('z_vs_renewal',float('nan')):5.1f}"
          f"  → {cls:13s} {upshot}")
    return dict(name=name, n=int(e.size), ks_gue=ks, longrange=cls, upshot=upshot)


def main():
    print("=" * 110)
    print("LONG-RANGE AUDIT — does each NNS universality verdict survive a long-range statistic?")
    print("=" * 110)
    rng = np.random.default_rng(0)

    print("\nControls (known answers):")
    _row("real_GUE", gue_positions(4000, rng))
    _row("poisson", poisson_positions(4000, np.random.default_rng(1)))
    _row("wigner_renewal_decoy", wigner_renewal(4000, np.random.default_rng(2)))

    print("\nBanked arithmetic universality claims (the Phase-18 STOP-CONDITION subjects):")
    findings = [
        ("zeta_first_2000", lambda: H.load_zeta_first(n=2000)),
        ("zeta_high_height", lambda: H.load_zeta_high(n=4000)),
        ("lmfdb_ec_pooled", H.load_lmfdb_pooled),
        ("dirichlet_pooled", H.load_dirichlet_pooled),
    ]
    for name, loader in findings:
        try:
            ev = loader()
        except Exception as e:
            print(f"  {name:20s} load FAILED: {e}")
            continue
        if np.asarray(ev).size < 200:
            print(f"  {name:20s} too few events ({np.asarray(ev).size})")
            continue
        _row(name, ev)

    print("\nBound: RIGID_GUE earns 'GUE class'; MARGINAL_ONLY means the NNS verdict "
          "certified only the marginal — the class claim is not supported by the "
          "long-range structure on this statistic.")


if __name__ == "__main__":
    main()
