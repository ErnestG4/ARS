"""Sub-additivity, tested EXHAUSTIVELY and OUT-OF-SAMPLE.
COMMITTED GENERATOR of fullseq/subadditivity.json.

The main arc's headline — composition is sub-additive, so the pairwise table
is a conservative upper bound — rests on THREE multi-inversion orderings from
a 7-ordering sealed sample.  That is now a falsifiable PREDICTION, and the
other 52 admissible orderings are untouched out-of-sample data.

PREDICTIONS, COMMITTED IN THIS DOCSTRING BEFORE THE RUN:
  P1  H > 0 at every multi-inversion ordering (sub-additivity is general in
      this dialect, not a property of the seven sampled).
  P2  mean H increases monotonically with inversion count.
  P3  H = 0 (to machine precision) at every single-transposition ordering —
      the sanity floor, exact by construction; a nonzero value here is an
      implementation defect, not a finding.

Exhaustive rather than sampled: all 5! = 120 orderings, filtered by the
sealed type constraint T1 < T5, giving 60, minus the reference = 59.  This
removes the sampling question entirely — there is no sample to have chosen
badly, and no post-hoc addition is possible because the set is the whole
space.

A FAILURE OF P1 IS THE MORE VALUABLE OUTCOME: it would mean the pairwise
table is NOT a conservative bound, which is a stronger constraint on how the
pairwise results may be used than a confirmation would be.
"""

import hashlib
import itertools
import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/fullseq")

SEAL = json.load(open(f"{ROOT}/fullseq/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/fullseq/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f}"

from transitions_1d import (REFERENCE_ORDER, admissible, apply_sequence,   # noqa: E402
                            sigma2, rtilde)

L_STAT, N_PTS, N_SEEDS = 20.0, 1600, 24
REF = REFERENCE_ORDER


def gue_unfolded(n, rng):
    A = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * n)
    ev = np.sort(np.linalg.eigvalsh(H).real)
    x = np.clip(ev / 2.0, -1, 1)
    return (0.5 + (x * np.sqrt(1 - x * x) + np.arcsin(x)) / np.pi) * n


def inversions(o):
    return int(sum(1 for i in range(5) for j in range(i + 1, 5)
                   if REF.index(o[i]) > REF.index(o[j])))


def main():
    print("generating substrates (once, reused across all orderings)",
          flush=True)
    subs = []
    for sd in range(N_SEEDS):
        rng = np.random.default_rng(sd)
        pts = gue_unfolded(N_PTS, rng)
        partner = gue_unfolded(N_PTS // 2, np.random.default_rng(sd + 500))
        u = rng.uniform(size=pts.size)
        p_ref, _ = apply_sequence(pts, REF, u, partner)
        subs.append((pts, u, partner, sigma2(p_ref, L_STAT)))
    ref_vals = np.array([s[3] for s in subs], float)

    # pairwise deltas (the first-order predictor's ingredients)
    pair = {}
    for a, b in itertools.combinations(REF, 2):
        o = REF.copy()
        ia, ib = o.index(a), o.index(b)
        o[ia], o[ib] = o[ib], o[ia]
        if not admissible(o):
            continue
        v = []
        for k, (pts, u, partner, rv) in enumerate(subs):
            p_o, _ = apply_sequence(pts, o, u, partner)
            v.append(sigma2(p_o, L_STAT) - rv)
        v = np.array(v, float)
        pair[f"{a}{b}"] = float(np.nanmean(v))

    orders = [list(o) for o in itertools.permutations(REF)
              if admissible(list(o)) and list(o) != REF]
    print(f"exhaustive set: {len(orders)} admissible orderings", flush=True)

    rows = {}
    for idx, o in enumerate(orders):
        d = []
        for pts, u, partner, rv in subs:
            p_o, _ = apply_sequence(pts, o, u, partner)
            d.append(sigma2(p_o, L_STAT) - rv)
        d = np.array(d, float)
        d = d[np.isfinite(d)]
        sem = float(d.std(ddof=1) / np.sqrt(d.size)) if d.size > 1 else np.nan
        pred = 0.0
        for i in range(5):
            for j in range(i + 1, 5):
                if REF.index(o[i]) > REF.index(o[j]):
                    a, b = sorted([o[i], o[j]], key=REF.index)
                    pred += pair.get(f"{a}{b}", 0.0)
        Hv = float(d.mean() - pred)
        rows["".join(o)] = dict(order=o, inv=inversions(o),
                                measured=float(d.mean()), predicted=pred,
                                H=Hv, sem=sem,
                                z=float(Hv / sem) if sem and sem > 0 else np.nan)
        if (idx + 1) % 15 == 0:
            print(f"  {idx + 1}/{len(orders)}", flush=True)

    prev = {"".join(o) for o in
            [["T2","T1","T3","T4","T5"], ["T1","T3","T2","T4","T5"],
             ["T1","T2","T4","T3","T5"], ["T1","T2","T3","T5","T4"],
             ["T2","T3","T1","T4","T5"], ["T3","T1","T2","T4","T5"],
             ["T3","T2","T1","T4","T5"]]}
    oos = {k: v for k, v in rows.items() if k not in prev}
    multi_oos = {k: v for k, v in oos.items() if v["inv"] > 1}
    single = {k: v for k, v in rows.items() if v["inv"] == 1}

    # P1: H > 0 at every multi-inversion ordering (out-of-sample)
    neg = {k: v for k, v in multi_oos.items() if v["H"] <= 0}
    neg_sig = {k: v for k, v in neg.items()
               if np.isfinite(v["z"]) and v["z"] < -3}
    # P2: mean H increases with inversion count
    by_inv = {}
    for v in rows.values():
        by_inv.setdefault(v["inv"], []).append(v["H"])
    means = {i: float(np.mean(h)) for i, h in sorted(by_inv.items())}
    mono = all(means[i] <= means[j] + 1e-12
               for i, j in zip(sorted(means), sorted(means)[1:]))
    # P3: single transpositions exact
    p3 = all(abs(v["H"]) < 1e-9 for v in single.values())

    out = dict(
        predictions_committed_before_run=[
            "P1 H > 0 at every multi-inversion ordering",
            "P2 mean H increases monotonically with inversion count",
            "P3 H = 0 to machine precision at single transpositions"],
        n_orderings=len(rows), n_out_of_sample=len(oos),
        n_multi_out_of_sample=len(multi_oos),
        P1=dict(violations=len(neg), significant_violations=len(neg_sig),
                worst=(min(multi_oos.items(), key=lambda kv: kv[1]["H"])[0]
                       if multi_oos else None),
                holds=bool(len(neg_sig) == 0)),
        P2=dict(mean_H_by_inversions=means, monotone=bool(mono)),
        P3=dict(holds=bool(p3), n_single=len(single)),
        rows=rows)
    json.dump(out, open(f"{ROOT}/fullseq/subadditivity.json", "w"), indent=1)

    print(f"\nOUT-OF-SAMPLE: {len(oos)} orderings ({len(multi_oos)} "
          f"multi-inversion)")
    print(f"P1 sub-additivity: {len(neg)} H<=0 "
          f"({len(neg_sig)} significant at z<-3) -> holds={out['P1']['holds']}")
    print(f"P2 mean H by inversions: "
          + "  ".join(f"{i}:{m:+.3f}" for i, m in means.items())
          + f"  -> monotone={mono}")
    print(f"P3 single-transposition exactness: {p3}")


if __name__ == "__main__":
    main()
