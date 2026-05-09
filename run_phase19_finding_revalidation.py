"""
run_phase19_finding_revalidation.py — Phase 19 Tier 3.

Apply the empirical mechanism-distinctness criterion to the project's
existing claims of "principled (invariant across ≥ 4 distinct extractor
mechanisms)."

Method:

  1. For each principled claim, list the extractors originally invoked
     in support.
  2. Look up their pairwise distinctness in the Tier 2 matrix
     (`data/phase19_distinctness_matrix.parquet`).
  3. Count the number of *equivalence classes* spanned by the supporting
     extractors — i.e., the maximum number of pairwise-distinct extractors
     among them, equivalent to the count of distinct equivalence classes
     they intersect.
  4. Apply the criterion:
       - ≥ 4 distinct equivalence classes → claim **survives**
       - 2-3 distinct classes            → claim **downgraded**
       - 0-1 distinct class              → claim **retracted**

Output:
  data/phase19_finding_revalidation.parquet
"""
from __future__ import annotations
import os, sys
from itertools import combinations

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)


# ─── Findings panel ──────────────────────────────────────────────────────
#
# Each claim records:
#   name: a short identifier
#   source: section reference
#   classification: the claimed class
#   supporting_extractors: prefixed names matching the Tier 2 matrix
#   note: contextual background


PRINCIPLED_CLAIMS = [
    dict(
        name='br_artifact_principled',
        source='§7.ter.22 Tier 1',
        classification='BR_artifact',
        supporting_extractors=[
            'gen.direct_events',
            'gen.pll_passage',
            'gen.find_peaks_prominence',
            'gen.derivative_zeros',
            'gen.threshold_crossing',
            'gen.modular_bin_events',
        ],
        note='6/6 extractor invariance across the general extractor panel '
             'on uniform_jitter, primes, twin primes (the strongest '
             'finding in the original Phase 16 matrix).',
    ),
    dict(
        name='primes_principled_br_artifact',
        source='§7.ter.22 Tier 1',
        classification='BR_artifact',
        supporting_extractors=[
            'gen.direct_events',
            'gen.pll_passage',
            'gen.find_peaks_prominence',
            'gen.derivative_zeros',
            'gen.threshold_crossing',
            'gen.modular_bin_events',
        ],
        note='Same six general extractors invoked for primes specifically.',
    ),
    dict(
        name='zeta_principled_TR',
        source='§7.ter.22 Tier 1',
        classification='TR',
        supporting_extractors=[
            'gen.direct_events',
            'gen.pll_passage',
            'gen.find_peaks_prominence',
            'gen.derivative_zeros',
            'gen.threshold_crossing',
            # modular_bin reads ζ as BR_artifact per §7.ter.22 (C); not
            # part of the supporting set for this claim.
        ],
        note='5/6 extractor invariance for ζ, β=2 GUE, LMFDB EC; '
             'modular_bin_events is the dissenter.',
    ),
    dict(
        name='llm_universal_br_artifact',
        source='§7.ter.22 Tier 2 / Phase 16A.2; implicitly retracted '
                'in §7.ter.23',
        classification='BR_artifact',
        supporting_extractors=[
            # All 8 attention extractors as listed in §7.ter.22 amendment
            # (which reclassified attention_sink_events as BR_artifact
            # after the §7.ter.23 sink_events-as-threshold-upcrossing
            # diagnosis).
            'llm.residual_norm_peaks',
            'llm.attention_entropy_peaks',
            'llm.attention_target_jumps',
            'llm.attention_sink_events',
            'llm.layer_kl_divergence_events',
            'llm.attention_argmax_sink',
            'llm.attention_sink_residency_runs',
            'llm.attention_multi_head_sink_consensus',
        ],
        note='Phase 16A originally claimed 4 of 5 attention extractors '
             'agreeing on BR_artifact; Phase 16A.2 added 3 more state-'
             'based extractors agreeing on BR_artifact, and the §7.ter.22 '
             'amendment reclassified attention_sink_events as BR_artifact '
             'after the threshold-upcrossing diagnosis (§7.ter.23 Finding F). '
             'Phase 19 tests how many of these 8 extractors are '
             'mechanism-distinct on the calibrator panel.',
    ),
]


# ─── Matrix loader and equivalence-class lookup ──────────────────────────


def load_matrix(path):
    df = pd.read_parquet(path)
    return df


def equivalence_classes_from_matrix(df, all_extractors):
    """Build equivalence classes via union-find on not-distinct edges."""
    parent = {x: x for x in all_extractors}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for _, row in df.iterrows():
        if not row['distinct']:
            union(row['ext_a'], row['ext_b'])
    classes = {}
    for x in parent:
        r = find(x)
        classes.setdefault(r, set()).add(x)
    # Return list of frozensets sorted by representative
    return [frozenset(s) for s in classes.values()]


def classes_spanned(extractors, classes):
    """Return the number of distinct equivalence classes that the input
    extractor set intersects."""
    seen = set()
    for ext in extractors:
        for ci, c in enumerate(classes):
            if ext in c:
                seen.add(ci)
                break
    return len(seen), [list(classes[ci]) for ci in seen]


# ─── Verdict ─────────────────────────────────────────────────────────────


def verdict_for(n_classes):
    if n_classes >= 4:
        return 'survives'
    if n_classes >= 2:
        return 'downgraded'
    return 'retracted'


def main():
    matrix_path = os.path.join(THIS_DIR, 'data',
                                'phase19_distinctness_matrix.parquet')
    if not os.path.exists(matrix_path):
        print(f"FAIL: matrix not found at {matrix_path}.  "
              f"Run run_phase19_distinctness_matrix.py first.")
        sys.exit(1)
    df = load_matrix(matrix_path)
    all_ext = sorted(set(df['ext_a']).union(set(df['ext_b'])))
    classes = equivalence_classes_from_matrix(df, all_ext)
    print("=" * 100)
    print(f"Phase 19 Tier 3 — finding revalidation against the empirical "
          f"distinctness criterion")
    print(f"  matrix: {len(df)} pairs from {len(all_ext)} extractors")
    print(f"  equivalence classes: {len(classes)}")
    for i, c in enumerate(classes):
        print(f"    Class {i + 1} ({len(c)}): {sorted(c)}")
    print("=" * 100)

    rows = []
    for claim in PRINCIPLED_CLAIMS:
        name = claim['name']
        src = claim['source']
        clss = claim['classification']
        supports = claim['supporting_extractors']
        n_classes, classes_intersected = classes_spanned(supports, classes)
        v = verdict_for(n_classes)
        rows.append(dict(
            claim=name,
            source=src,
            classification=clss,
            n_supporting_extractors=len(supports),
            n_equivalence_classes_spanned=n_classes,
            verdict=v,
            classes_intersected=str(classes_intersected),
        ))
        print()
        print(f"  CLAIM: {name}")
        print(f"    source:                {src}")
        print(f"    classification:        {clss}")
        print(f"    supporting extractors: {len(supports)}")
        print(f"    equivalence classes spanned: {n_classes}")
        print(f"    verdict:               {v.upper()}")
        if v != 'survives':
            print(f"    note: {claim['note']}")
            print(f"    classes intersected:")
            for c in classes_intersected:
                print(f"      {sorted(c)}")

    out = pd.DataFrame(rows)
    out_path = os.path.join(THIS_DIR, 'data',
                             'phase19_finding_revalidation.parquet')
    out.to_parquet(out_path)
    print()
    print(f"  → {out_path}  ({len(out)} claims)")


if __name__ == '__main__':
    main()
