"""
run_phase20_5_distinctness_revalidation.py — Phase 20.5 panel-extension
re-validation of Phase 19's principled-claim discipline.

Re-runs the pairwise distinctness matrix (Phase 19) against the
**extended** calibrator panel (8 stationary + 6 transition = 14
calibrators).  Compares the resulting equivalence-class structure
to the Phase 19 baseline (11 classes from 14 extractors).  Reports
whether the four principled claims (BR_artifact, primes-BR_artifact,
ζ-TR, LLM-BR_artifact) survive the extended panel.

Outputs:
  data/phase20_5_distinctness_extended.parquet
  data/phase20_5_distinctness_revalidation.parquet
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from calibrator_panel import EXTENDED_CALIBRATORS
from extractor_distinctness import (
    extractor_for_events, _quadrants_per_q,
    _q_disagreement_count,
)
from extractors import EXTRACTORS
from llm_extractors import LLM_EXTRACTORS
from run_phase19_distinctness_matrix import (
    llm_extractor_adapter, build_extractor_panel,
    UnionFind, DIST_T, Q_MAX, MIN_EVENTS,
)
from run_phase19_finding_revalidation import (
    PRINCIPLED_CLAIMS, equivalence_classes_from_matrix,
    classes_spanned, verdict_for,
)

DATA = Path(THIS_DIR) / 'data'
DATA.mkdir(parents=True, exist_ok=True)

N_SEEDS = 5
SEED_THRESHOLD = 4


def main():
    panel = build_extractor_panel()
    names = [n for n, _ in panel]
    print("=" * 100)
    print(f"Phase 20.5 — Phase 19 distinctness re-validation against "
          f"EXTENDED panel")
    print(f"  extractors: {len(names)}, calibrators: "
          f"{len(EXTENDED_CALIBRATORS)} "
          f"(8 stationary + 6 transition), seeds: {N_SEEDS}")
    print("=" * 100)

    # Precompute per-(calibrator, seed, extractor) quadrants
    cache = {}
    t_start = time.time()
    for cal_name, cal_gen in EXTENDED_CALIBRATORS:
        for seed in range(N_SEEDS):
            try:
                t_k = cal_gen(seed)
            except Exception as e:
                print(f"    {cal_name} seed={seed}: gen failed: {e}")
                continue
            for ext_name, ext_fn in panel:
                try:
                    events = np.sort(np.asarray(ext_fn(t_k),
                                                  dtype=np.float64))
                except Exception as e:
                    cache[(cal_name, seed, ext_name)] = None
                    continue
                qd = _quadrants_per_q(events, q_max=Q_MAX,
                                        min_events=MIN_EVENTS)
                cache[(cal_name, seed, ext_name)] = qd
        print(f"    {cal_name}: complete  "
              f"⏱{time.time() - t_start:.0f}s")

    # Pairwise distinctness
    rows = []
    for ext_a, ext_b in combinations(names, 2):
        max_disagree = 0
        disagreeing_class = None
        for cal_name, _ in EXTENDED_CALIBRATORS:
            n_dis_seeds = 0
            for seed in range(N_SEEDS):
                qd_a = cache.get((cal_name, seed, ext_a))
                qd_b = cache.get((cal_name, seed, ext_b))
                if qd_a is None or qd_b is None:
                    continue
                if _q_disagreement_count(qd_a, qd_b) > 0:
                    n_dis_seeds += 1
            if n_dis_seeds > max_disagree:
                max_disagree = n_dis_seeds
                if n_dis_seeds >= SEED_THRESHOLD:
                    disagreeing_class = cal_name
        rows.append(dict(
            ext_a=ext_a, ext_b=ext_b,
            distinct=bool(max_disagree >= SEED_THRESHOLD),
            max_disagree_seeds=int(max_disagree),
            disagreeing_class=disagreeing_class,
        ))

    df = pd.DataFrame(rows)
    out = DATA / 'phase20_5_distinctness_extended.parquet'
    df.to_parquet(out, index=False)
    print(f"\n  → {out}  ({len(df)} pairs)")

    # Equivalence classes
    classes = equivalence_classes_from_matrix(df, names)
    classes.sort(key=lambda c: (-len(c), sorted(c)[0]))
    print()
    print("=" * 100)
    print(f"Equivalence classes (extended panel): {len(classes)} classes "
          f"from {len(names)} extractors")
    print("=" * 100)
    for i, c in enumerate(classes):
        print(f"  Class {i + 1} ({len(c)}): {sorted(c)}")

    # Compare against Phase 19 baseline
    baseline_path = DATA / 'phase19_distinctness_matrix.parquet'
    if baseline_path.exists():
        baseline_df = pd.read_parquet(baseline_path)
        baseline_classes = equivalence_classes_from_matrix(
            baseline_df, names)
        print(f"\n  Phase 19 baseline (8 stationary calibrators only): "
              f"{len(baseline_classes)} classes")
        delta = len(classes) - len(baseline_classes)
        print(f"  Delta: {delta:+d} class{'es' if abs(delta) != 1 else ''}")
        if delta == 0:
            print("  → equivalence-class count UNCHANGED by panel extension")
        elif delta > 0:
            print(f"  → {delta} additional class{'es' if delta > 1 else ''} "
                  f"emerged on extended panel; some pairs that were "
                  f"non-distinct on stationary calibrators are distinct "
                  f"on transition calibrators")
        else:
            print(f"  → {-delta} fewer class{'es' if -delta > 1 else ''}; "
                  f"transition calibrators reveal additional disagreements "
                  f"that merge equivalence classes (unexpected — investigate)")

    # Re-validate principled claims
    print()
    print("=" * 100)
    print("Principled-claim re-validation against extended panel")
    print("=" * 100)
    revalid_rows = []
    for claim in PRINCIPLED_CLAIMS:
        n_classes_intersected, classes_intersected = classes_spanned(
            claim['supporting_extractors'], classes)
        verdict = verdict_for(n_classes_intersected)
        revalid_rows.append(dict(
            claim=claim['name'],
            classification=claim['classification'],
            n_supporting_extractors=len(claim['supporting_extractors']),
            n_equivalence_classes_spanned_extended=n_classes_intersected,
            verdict_extended=verdict,
        ))
        print(f"  CLAIM: {claim['name']}")
        print(f"    classification:        {claim['classification']}")
        print(f"    supporting extractors: "
              f"{len(claim['supporting_extractors'])}")
        print(f"    classes spanned (ext): {n_classes_intersected}")
        print(f"    verdict (ext):         {verdict.upper()}")
    pd.DataFrame(revalid_rows).to_parquet(
        DATA / 'phase20_5_distinctness_revalidation.parquet', index=False)
    print(f"\n  → {DATA}/phase20_5_distinctness_revalidation.parquet")
    print(f"\n  total time: {time.time() - t_start:.0f}s")


if __name__ == '__main__':
    main()
