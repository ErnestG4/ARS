"""
cross_substrate/agreement_check.py — formalize the I.5q ↔ I.5 agreement.

Question: is the cheap q-banded `I.5q_ks_gue_med` (Phase 2a, harvestable for
every ARS-classify substrate) an UNBIASED proxy for the matched object-(a)
`I.5_ks_gue` (Phase 2b, requires raw event trains)? If yes within documented
conditions, the 2a-only substrates (Allen, Kuramoto) are trustable as placed and
their costly matched recompute can be deferred/skipped.

Test: regress  I.5q = a + b·I.5.  Unbiased ⟺ a=0, b=1.

Three regressions (per-substrate-vs-pooled discipline — Will):
  R1 pvc-11 internal (n=1159): leg difference ONLY (both legs ~JPF-capped 1500),
     at the narrow I.5≈0.5 operating point.
  R2 per-substrate medians (7 pts, equal weight, full range 0.27–0.92): the
     headline cross-substrate slope test. Confounds leg + N-difference for the
     arithmetic substrates (object-a full-N vs q-banded capped) — stated.
  R3 all matched cells pooled (flag: pvc-11 dominates by count).

Plus: residual structure (vs n_events, vs I.5 as class proxy, per substrate) and
the small-N floor (where |I.5−I.5q| blows up).

Out: agreement_check.json + figures/AGR_*.png
"""
from __future__ import annotations

import glob
import json
import os

import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
FIGDIR = os.path.join(_HERE, "figures")
os.makedirs(FIGDIR, exist_ok=True)

MATCHED = ["pvc-11", "L-zeros", "mertens", "liouville", "maass-gamma0",
           "gaussian-primes", "eisenstein-primes"]


def collect():
    """Per-cell (substrate, I.5, I.5q, n) where both legs present."""
    rows = []
    for sub in MATCHED:
        for l in open(os.path.join(COORD, f"{sub}.jsonl")):
            r = json.loads(l)
            a = r["axes_computed"]
            i5, i5q = a.get("I.5_ks_gue"), a.get("I.5q_ks_gue_med")
            if not (isinstance(i5, (int, float)) and isinstance(i5q, (int, float))):
                continue
            aud = r.get("extraction_audit", {})
            n = aud.get("n_events_used") or aud.get("n_events") \
                or (aud.get("object_a_recompute") or {}).get("n_events_banked")
            rows.append({"substrate": sub, "cell": r["cell_id"],
                         "i5": float(i5), "i5q": float(i5q),
                         "n": int(n) if n else None})
    return rows


def regress(i5, i5q, label):
    i5, i5q = np.asarray(i5, float), np.asarray(i5q, float)
    if i5.size < 2:
        return {"label": label, "n": int(i5.size), "insufficient": True}
    lr = stats.linregress(i5, i5q)
    # tests vs unbiased null (slope=1, intercept=0)
    t_slope = (lr.slope - 1.0) / lr.stderr if lr.stderr > 0 else np.nan
    df = i5.size - 2
    p_slope1 = float(2 * stats.t.sf(abs(t_slope), df)) if df > 0 and np.isfinite(t_slope) else None
    p_int0 = (float(2 * stats.t.sf(abs(lr.intercept / lr.intercept_stderr), df))
              if df > 0 and lr.intercept_stderr > 0 else None)
    resid = i5q - (lr.intercept + lr.slope * i5)
    return {"label": label, "n": int(i5.size),
            "slope": float(lr.slope), "slope_stderr": float(lr.stderr),
            "intercept": float(lr.intercept),
            "intercept_stderr": float(lr.intercept_stderr),
            "pearson_r": float(lr.rvalue), "r2": float(lr.rvalue ** 2),
            "p_slope_eq_1": p_slope1, "p_intercept_eq_0": p_int0,
            "mean_abs_resid": float(np.mean(np.abs(resid))),
            "max_abs_resid": float(np.max(np.abs(resid))),
            "unbiased_at_5pct": bool(
                (p_slope1 is None or p_slope1 > 0.05) and
                (p_int0 is None or p_int0 > 0.05))}


def main():
    rows = collect()
    by = {}
    for r in rows:
        by.setdefault(r["substrate"], []).append(r)

    print("=" * 78)
    print("AGREEMENT CHECK — is I.5q an unbiased proxy for I.5 (object-a)?")
    print("   regress  I.5q = a + b·I.5 ;  unbiased ⟺ b=1, a=0")
    print("=" * 78)

    out = {"regressions": {}, "per_cell_diff": [], "small_n": {}}

    # exclude the documented small-N outlier from the proxy fits; report it separately
    OUTLIER = ("liouville", "sub_high")
    clean = [r for r in rows if (r["substrate"], r["cell"].split("/")[-1]
                                 if "/" in r["cell"] else r["cell"]) != OUTLIER
             and r["cell"] != "sub_high"]

    # R1 pvc-11 internal
    p = by.get("pvc-11", [])
    R1 = regress([r["i5"] for r in p], [r["i5q"] for r in p],
                 "R1_pvc11_internal_leg_only_N_matched")
    # R2 per-substrate medians (clean, equal weight)
    meds = []
    for sub, rs in by.items():
        rc = [r for r in rs if r["cell"] != "sub_high"]
        if rc:
            meds.append((sub, float(np.median([r["i5"] for r in rc])),
                         float(np.median([r["i5q"] for r in rc]))))
    R2 = regress([m[1] for m in meds], [m[2] for m in meds],
                 "R2_per_substrate_medians_equal_weight")
    # R3 all matched cells pooled (clean)
    R3 = regress([r["i5"] for r in clean], [r["i5q"] for r in clean],
                 "R3_all_cells_pooled_pvc11_dominates")

    for R in (R1, R2, R3):
        out["regressions"][R["label"]] = R
        if R.get("insufficient"):
            print(f"\n[{R['label']}] insufficient n")
            continue
        print(f"\n[{R['label']}] n={R['n']}")
        print(f"   slope     = {R['slope']:.4f} ± {R['slope_stderr']:.4f}"
              f"   (p[slope=1]={R['p_slope_eq_1']})")
        print(f"   intercept = {R['intercept']:.4f} ± {R['intercept_stderr']:.4f}"
              f"   (p[int=0]={R['p_intercept_eq_0']})")
        print(f"   r={R['pearson_r']:.4f}  mean|resid|={R['mean_abs_resid']:.4f}"
              f"  max|resid|={R['max_abs_resid']:.4f}")
        print(f"   → UNBIASED at 5%: {R['unbiased_at_5pct']}")

    # per-substrate |diff| + small-N floor
    print("\n[per-cell |I.5 − I.5q| and n] (sorted by n)")
    cells = sorted(rows, key=lambda r: (r["n"] or 0))
    for r in cells:
        d = abs(r["i5"] - r["i5q"])
        out["per_cell_diff"].append({"substrate": r["substrate"], "cell": r["cell"],
                                     "n": r["n"], "abs_diff": round(d, 4)})
        if r["n"] is None or r["n"] < 300 or d > 0.05:
            tag = "  <-- DIVERGES" if d > 0.05 else ""
            print(f"   {r['substrate']:16s} {r['cell'][:26]:26s} n={str(r['n']):>6s} "
                  f"|diff|={d:.4f}{tag}")

    # Two DISTINCT failure modes (residual structure):
    #  (i)  small-N: instability of the q-banded median when few q-bands powered
    #  (ii) condition-specific: pvc-11 gratings cells diverge at large n
    #       (strong stimulus-locking) — NOT a sample-size effect.
    fail = [r for r in cells if r["n"] and abs(r["i5"] - r["i5q"]) > 0.05]
    smalln_fail = [r for r in fail if r["n"] < 300]
    cond_fail = [r for r in fail if r["n"] >= 300]
    agree = [r for r in cells if r["n"] and abs(r["i5"] - r["i5q"]) <= 0.05]
    floor = {
        "smallN_fail_cells": [{"substrate": r["substrate"], "cell": r["cell"],
                               "n": r["n"], "abs_diff": round(abs(r["i5"] - r["i5q"]), 4)}
                              for r in smalln_fail],
        "condition_fail_cells_n_ge_300": len(cond_fail),
        "condition_fail_all_pvc11_gratings": all(
            r["substrate"] == "pvc-11" for r in cond_fail),
        "max_n_that_fails_smallN": int(max((r["n"] for r in smalln_fail), default=0)),
        "min_n_that_agrees": int(min((r["n"] for r in agree), default=0)),
    }
    floor["recommended_min_n"] = (max(100, floor["max_n_that_fails_smallN"] + 1)
                                  if smalln_fail else 100)
    floor["note"] = ("Two failure modes separated. SMALL-N: bracketed by "
                     f"largest-failing n={floor['max_n_that_fails_smallN']} "
                     f"(liouville sub_high) and smallest-agreeing n={floor['min_n_that_agrees']}; "
                     f"recommend n ≥ {floor['recommended_min_n']}. CONDITION: the "
                     f"{len(cond_fail)} large-n failures are all pvc-11 gratings "
                     "(stimulus-locking), not a sample-size effect.")
    out["small_n"] = floor

    # residual-by-condition for pvc-11 (the substrate-property residual)
    cond = {}
    for l in open(os.path.join(COORD, "pvc-11.jsonl")):
        rr = json.loads(l); a = rr["axes_computed"]
        i5, i5q = a.get("I.5_ks_gue"), a.get("I.5q_ks_gue_med")
        if isinstance(i5, float) and isinstance(i5q, float):
            cond.setdefault(rr["meta"]["subset"], []).append(abs(i5 - i5q))
    out["pvc11_residual_by_condition"] = {
        s: {"n": len(v), "mean_abs_diff": round(float(np.mean(v)), 4),
            "frac_gt_0p05": round(float(np.mean(np.array(v) > 0.05)), 3)}
        for s, v in sorted(cond.items())}

    print(f"\n[failure modes]")
    print(f"   SMALL-N: fails at n≤{floor['max_n_that_fails_smallN']}, "
          f"agrees from n≥{floor['min_n_that_agrees']} → recommend n ≥ "
          f"{floor['recommended_min_n']}")
    print(f"   CONDITION: {len(cond_fail)} large-n failures, "
          f"all pvc-11 gratings={floor['condition_fail_all_pvc11_gratings']}")
    print(f"   pvc-11 mean|diff| by condition:")
    for s, d in out["pvc11_residual_by_condition"].items():
        print(f"      {s:16s} mean={d['mean_abs_diff']:.4f}  "
              f"frac>0.05={d['frac_gt_0p05']}")

    _figs(rows, R2)
    with open(os.path.join(_HERE, "agreement_check.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\n→ wrote agreement_check.json + figures/AGR_*.png")


COLORS = {"pvc-11": "#1f77b4", "L-zeros": "#d62728", "mertens": "#9467bd",
          "liouville": "#8c564b", "maass-gamma0": "#e377c2",
          "gaussian-primes": "#ff7f0e", "eisenstein-primes": "#bcbd22"}


def _figs(rows, R2):
    # scatter I.5 vs I.5q with y=x and per-substrate-median fit
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.6))
    for sub in MATCHED:
        rs = [r for r in rows if r["substrate"] == sub]
        if not rs:
            continue
        ax1.scatter([r["i5"] for r in rs], [r["i5q"] for r in rs], s=28, alpha=0.5,
                    color=COLORS[sub], edgecolor="k", linewidth=0.3, label=sub)
    lim = [0, 1]
    ax1.plot(lim, lim, "k--", lw=1, label="y = x (unbiased)")
    if not R2.get("insufficient"):
        xs = np.linspace(0, 1, 50)
        ax1.plot(xs, R2["intercept"] + R2["slope"] * xs, "r-", lw=1.2,
                 label=f"median fit: slope={R2['slope']:.3f}")
    ax1.set_xlabel("I.5 (object-a, matched-to-AM)")
    ax1.set_ylabel("I.5q (q-banded, cheap harvest)")
    ax1.set_title("Proxy scatter — all matched cells")
    ax1.legend(fontsize=7); ax1.grid(alpha=0.2)

    # |diff| vs n (small-N floor)
    for sub in MATCHED:
        rs = [r for r in rows if r["substrate"] == sub and r["n"]]
        if not rs:
            continue
        ax2.scatter([r["n"] for r in rs], [abs(r["i5"] - r["i5q"]) for r in rs],
                    s=40, alpha=0.6, color=COLORS[sub], edgecolor="k",
                    linewidth=0.3, label=sub)
    ax2.axhline(0.05, color="r", ls=":", lw=1, label="0.05 divergence band")
    ax2.set_xscale("log")
    ax2.set_xlabel("n_events (q-banded leg)")
    ax2.set_ylabel("|I.5 − I.5q|")
    ax2.set_title("Small-N floor: agreement vs sample size")
    ax2.legend(fontsize=7); ax2.grid(alpha=0.2)
    p = os.path.join(FIGDIR, "AGR_proxy_and_floor.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
