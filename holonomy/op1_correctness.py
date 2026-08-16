"""OP1 correctness cell (the §3-forced consequence of the failed materiality
pass) — COMMITTED GENERATOR of holonomy/op1_correctness.json.

THREE-EVENT LABEL: (1) OP1 banked RULED_CONSISTENT without correctness
evidence; (2) materiality pass (ADD-1) found the ruling load-bearing at the
RIGID_GUE gate (margin 1.4x |Delta| < k=3); (3) this cell, run under
addendum ADD-3.

PREDICTION, STATED BEFORE THE RUN (in this docstring, committed first):
the matched-lens configuration is correct.  A surrogate null must answer
"what would a marginal-only process look like THROUGH THIS APPARATUS."  The
deg-6 lens absorbs fluctuation (lowers Sigma^2).  If the null band skips the
lens while data passes it, renewal-class DATA (lensed, ~2.9) is compared to
an UNLENSED null band (~3.6) and reads below-null — spurious rigidity
evidence, false-RIGID-ward bias for exactly the marginal-only class the
gate exists to reject.  Matched-lens keeps data and null common-mode.

Truth by construction: renewal-class data is NOT rigid; its correct reading
against its own null is z ~ 0.  Comparator: |z_mixed| vs |z_matched| for
lensed renewal data against (matched-lens vs unlensed) null bands.  Orders
separate at >= k * SE => RULED_CORRECT for the MATCHED_LENS invariant.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (ROOT, f"{ROOT}/cross_substrate", f"{ROOT}/holonomy"):
    if p not in sys.path:
        sys.path.insert(0, p)

N, L, SEEDS, DEG = 1200, 20.0, 64, 6
K_ARC = 3.0

# First run (SEEDS=8, 2026-08-16): z_matched=-0.19, z_mixed=-0.82,
# sep=0.63+-0.64 — DIRECTION CONFIRMED, UNDERPOWERED at k=3.  Extension:
# one pre-committed rerun at SEEDS=64 (renewal-only, no eigensolve; the
# arc's standard seed-increase hatch), banked whichever way it lands.
FIRST_RUN = dict(seeds=8, z_matched=-0.19, z_mixed=-0.82,
                 separation=0.63, separation_se=0.64,
                 note="direction confirmed, underpowered")


def main():
    from longrange_discriminator import wigner_renewal, longrange_stats
    lensed, unlensed = [], []
    for k in range(SEEDS):
        rng = np.random.default_rng(9200 + k)
        pos = wigner_renewal(N, rng)
        lensed.append(longrange_stats(pos, L, unfold_deg=DEG)["sigma2"])
        unlensed.append(longrange_stats(pos, L)["sigma2"])
    lensed, unlensed = np.array(lensed), np.array(unlensed)
    # renewal-class "data" arm: fresh seeds, through the lens (as data would)
    data = []
    for k in range(SEEDS):
        rng = np.random.default_rng(9300 + k)
        data.append(longrange_stats(wigner_renewal(N, rng), L,
                                    unfold_deg=DEG)["sigma2"])
    data = np.array(data)
    dm, dse = float(data.mean()), float(data.std(ddof=1) / np.sqrt(SEEDS))

    def z_against(band):
        bm, bs = float(band.mean()), float(band.std(ddof=1))
        return (dm - bm) / bs, bm, bs

    z_matched, mm, ms = z_against(lensed)
    z_mixed, um, us = z_against(unlensed)
    sep = abs(z_mixed) - abs(z_matched)
    # SE of the separation, dominated by the data-arm mean error in band-sd units
    sep_se = float(np.hypot(dse / ms, dse / us))
    ruled = bool(sep >= K_ARC * sep_se and abs(z_matched) < abs(z_mixed))
    out = dict(
        three_event_label=["RULED_CONSISTENT banked without correctness leg",
                           "ADD-1 materiality found ruling load-bearing "
                           "(margin 1.4x < k=3)",
                           "this cell run under addendum ADD-3"],
        prediction="matched-lens correct; mixed order biases marginal-class "
                   "data toward false rigidity (docstring, committed first)",
        n=N, L=L, seeds=SEEDS, unfold_deg=DEG,
        renewal_null_lensed=dict(mean=mm, sd=ms),
        renewal_null_unlensed=dict(mean=um, sd=us),
        renewal_data_lensed=dict(mean=dm, sem=dse),
        z_matched=float(z_matched), z_mixed=float(z_mixed),
        separation=float(sep), separation_se=sep_se,
        first_run=FIRST_RUN,
        ruled_correct_matched_lens=ruled)
    json.dump(out, open(f"{ROOT}/holonomy/op1_correctness.json", "w"),
              indent=1)
    print(f"OP1 correctness: z_matched={z_matched:+.2f} "
          f"z_mixed={z_mixed:+.2f} sep={sep:.2f}±{sep_se:.2f} -> "
          f"RULED_CORRECT(matched_lens)={ruled}")
    # exit 0 = generated + banked; the ruled flag is DATA (pinned by
    # verify_holonomy) — non-separation is a banked outcome, not a failure.


if __name__ == "__main__":
    main()
