#!/usr/bin/env python3
"""ROADMAP Step 1 — standalone k=1 lattice computation (instrument credibility for F-2).

Part A (the pre-committed adjudication): equally spaced roots at n in {1024, 2048, 4096},
differentiate ONCE, rootfind directly, apply the gap-ratio statistic on RAW central-window gaps —
no flow harness pipeline, NO free-convolution reference, no unfolding. The rtilde statistic is
locally insensitive to smooth density, so real bulk dynamics must appear in raw gaps; a clean raw
result puts the flagged value on the reference layer. Window: central BULK_FRACTION = 0.20
(track0_harness.py declared-constants block), same convention as the flow rows.

Rootfinder note: diff_step's electrostatic bisection+Newton is used as the rootfinder (certified
to 1.35e-13 of local spacing by the Hermite gate); it is NOT the suspect — the suspect is the
near-atomic free-convolution reference. Independence check: 5 central roots per n are re-derived
by mpmath Newton (dps 30) from exact lattice points.

Part B (attribution probe, runs regardless of branch): the pipeline readout (reference_cdf
unfolding) recomputed on the SAME standalone p' roots under {GRID_PTS 4001, eps}, {16001, eps},
{4001, 2*eps} at each n. Suspect named in advance: at n=4096 the 4001-point reference grid is
COARSER than the root spacing (aliasing crossover) — predicts the artifact appears at n=4096,
shrinks with the finer grid, and is insensitive to eps-doubling.
"""
import json
import numpy as np
from mpmath import mp
import track0_iid_scaling as TIS
from track0_harness import diff_step, bulk_idx, rtilde, BULK_FRACTION
from free_conv import F_empirical
from track0_iid_scaling import reference_cdf

NS = [1024, 2048, 4096]
FLAGGED = {}  # filled from the banked science artifact for comparison


def raw_rtilde(roots, m):
    gaps = np.diff(roots[bulk_idx(m)])
    return 1.0 - rtilde(gaps)


def mp_verify(seed, roots64, n, n_check=5):
    mp.dps = 30
    mid = (n - 1) // 2
    devs = []
    for j in range(mid - n_check // 2, mid + (n_check + 1) // 2):
        x = mp.mpf(roots64[j])
        for _ in range(4):
            s = mp.fsum(1 / (x - mp.mpf(-1) - mp.mpf(2 * i) / (n - 1)) for i in range(n))
            sp = -mp.fsum(1 / (x - mp.mpf(-1) - mp.mpf(2 * i) / (n - 1)) ** 2 for i in range(n))
            x = x - s / sp
        devs.append(abs(float(x - mp.mpf(roots64[j]))))
    return max(devs)


def main():
    sci = json.load(open("derivflow/science_rate_question.json"))
    for n in NS:
        FLAGGED[n] = sci["picket"][str(n)]["1"]["one_minus_rtilde"]
    out = {"step": "ROADMAP Step 1", "rows": []}
    for n in NS:
        seed = np.linspace(-1.0, 1.0, n)
        r1 = diff_step(seed)
        m = n - 1
        raw = raw_rtilde(r1, m)
        spacing = 2.0 / (n - 1)
        mpdev = mp_verify(seed, r1, n) / spacing
        row = {"n": n, "raw_one_minus_rtilde": raw, "pipeline_flagged": FLAGGED[n],
               "ratio_pipeline_over_raw": FLAGGED[n] / raw if raw > 0 else None,
               "mp_rootfinder_dev_of_spacing": mpdev}
        # Part B: pipeline readout on the SAME roots, three variants
        F_seed = F_empirical(seed)
        for label, gp, epsf in [("grid4001_eps", 4001, TIS.EPS_FRAC),
                                ("grid16001_eps", 16001, TIS.EPS_FRAC),
                                ("grid4001_2eps", 4001, 2 * TIS.EPS_FRAC)]:
            TIS.GRID_PTS, TIS.EPS_FRAC_SAVE = gp, TIS.EPS_FRAC
            TIS.EPS_FRAC = epsf
            F_at, diag = reference_cdf(F_seed, r1, 1.0 / n, m)
            TIS.EPS_FRAC = TIS.EPS_FRAC_SAVE
            u = F_at * m
            row[label] = 1.0 - rtilde(np.diff(u[bulk_idx(m)]))
        TIS.GRID_PTS = 4001
        out["rows"].append(row)
        print(f"n={n}: RAW={raw:.3e}  pipeline_flagged={FLAGGED[n]:.3e}  "
              f"(x{row['ratio_pipeline_over_raw']:.1f})  mp_dev={mpdev:.1e}", flush=True)
        print(f"        variants: grid4001={row['grid4001_eps']:.3e}  "
              f"grid16001={row['grid16001_eps']:.3e}  2eps={row['grid4001_2eps']:.3e}", flush=True)
    with open("derivflow/step1_lattice_k1.json", "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
