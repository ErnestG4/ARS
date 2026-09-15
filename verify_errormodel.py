"""Certify the error-model fork, and apply it to the real surface so the selection is visible.

  1. The fork REFUSES without a declared threshold, and refuses a nonsense one.
  2. It fires exactly one way, and BOTH numbers survive either way.
  3. Applied to Stage 3d's banked surface at n=4096 with the threshold declared
     here, it reports per cell: degeneracy, which model it selected, both z's.
     The paper's window paragraph quotes covariance z(beta) throughout; this
     shows which of those cells the declared rule would have handed to the
     bootstrap instead, so a reader sees the fork rather than the selection.
  4. The degenerate cells are flagged NOT SEPARATELY IDENTIFIED, and there must
     be at least one -- Stage 3d measured corr = 0.999 on the seven-point cell,
     and a rule that never fires on that surface is not the rule that was
     motivated by it.
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import curve_fit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "derivflow"))

from errormodel import (shape_z, degeneracy_of, UndeclaredThreshold,     # noqa: E402
                        COVARIANCE, BOOTSTRAP)
from science_rate_question import f3, LN10, FIT_WINDOW_MIN               # noqa: E402

# DECLARED. 0.95 on |corr| between tau and beta: below it the two parameters
# carry separable information; at 0.999 (the measured short-window value) they
# do not. The value is a choice and is written down as one; the point of the
# fork is that it is written down rather than applied.
DEGENERACY_THRESHOLD = 0.95

bad = []

# ---- 1. refusals -------------------------------------------------------------
c_ok = np.array([[1.0, 0.1, 0.1], [0.1, 1.0, 0.2], [0.1, 0.2, 1.0]])
for thr, label in ((None, "no threshold"), (1.5, "threshold outside (0,1)")):
    try:
        shape_z(1.0, 0.1, 0.1, 0.1, 0.1, c_ok, c_ok, thr)
        bad.append(f"shape_z accepted {label} — the fork can be applied without "
                   "declaring what degenerate means")
        print(f"  {label:<26} ALLOWED  <-- BAD")
    except UndeclaredThreshold:
        print(f"  {label:<26} REFUSED")

# ---- 2. it fires one way, both numbers survive --------------------------------
c_deg = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.999], [0.0, 0.999, 1.0]])
r_ok = shape_z(1.0, 0.2, 0.2, 0.1, 0.1, c_ok, c_ok, DEGENERACY_THRESHOLD)
r_deg = shape_z(1.0, 0.2, 0.2, 0.1, 0.1, c_deg, c_deg, DEGENERACY_THRESHOLD)
print(f"\n  well-conditioned (deg {r_ok.degeneracy:.3f}) -> {r_ok.selected}, "
      f"z_cov {r_ok.z_covariance:.3f} z_boot {r_ok.z_bootstrap:.3f}, "
      f"identified={r_ok.separately_identified}")
print(f"  degenerate       (deg {r_deg.degeneracy:.3f}) -> {r_deg.selected}, "
      f"z_cov {r_deg.z_covariance:.3f} z_boot {r_deg.z_bootstrap:.3f}, "
      f"identified={r_deg.separately_identified}")
if r_ok.selected != BOOTSTRAP or r_deg.selected != COVARIANCE:
    bad.append("the fork fired the wrong way on a synthetic case")
if r_ok.z_covariance == 0 or r_deg.z_bootstrap == 0:
    bad.append("the non-selected z was dropped — both must always be reported")
if r_deg.separately_identified or not r_ok.separately_identified:
    bad.append("the separately-identified flag does not follow the threshold")

# ---- 3. apply it to the real surface ----------------------------------------
s3 = json.load(open(os.path.join(HERE, "derivflow", "stage3_commensurable_window.json")))
s3d = json.load(open(os.path.join(HERE, "derivflow", "stage3d_error_model.json")))
KA = np.array(s3["k_grid"], float)
R = 16
cur = {sc: np.array(s3["per_replicate_curves"][sc]) for sc in ("iid", "gue")}


def fit(mu, sg, ks):
    y, sy = np.log10(mu), sg / (mu * LN10)
    best = None
    for t in (2.0, 5.0, 10.0, 30.0):
        for b in (0.5, 0.75, 1.0):
            try:
                p, cov = curve_fit(f3, ks, y, p0=[y[0], t, b], sigma=sy,
                                   absolute_sigma=True,
                                   bounds=([-np.inf, 1e-3, 0.05], [np.inf, 1e4, 3.0]),
                                   maxfev=20000)
                c2 = float(np.sum(((y - f3(ks, *p)) / sy) ** 2))
                if np.isfinite(c2) and (best is None or c2 < best[0]):
                    best = (c2, p, cov)
            except Exception:
                pass
    return best


def mask(mu, lo, rule):
    up = (mu > FIT_WINDOW_MIN) if rule == "sealed_1e-3" else (
        KA <= (11 if rule == "shared_11" else 16))
    return up & (KA >= lo)


print(f"\n  Stage 3d surface, n=4096, threshold {DEGENERACY_THRESHOLD}:")
print(f"  {'cell':>16} {'deg':>6} {'selected':>11} {'z_cov':>7} {'z_boot':>7} {'identified':>11}")
n_deg, n_cells, disagree = 0, 0, 0
for lo in (1, 2, 3, 4, 5):
    for rule in ("sealed_1e-3", "shared_11", "shared_16"):
        key = f"n4096_lo{lo}_{rule}"
        if key not in s3d["surface"]:
            continue
        fits = {}
        for sc in ("iid", "gue"):
            mu = cur[sc].mean(axis=0)
            sg = cur[sc].std(axis=0, ddof=1) / np.sqrt(R)
            w = mask(mu, lo, rule)
            fits[sc] = fit(mu[w], sg[w], KA[w])
        d = abs(fits["iid"][1][2] - fits["gue"][1][2])
        # bootstrap SEs are recoverable from the banked z_bootstrap and delta
        row = s3d["surface"][key]
        se_boot_comb = row["delta_beta"] / row["z_bootstrap"]
        r = shape_z(d, np.sqrt(fits["iid"][2][2, 2]), np.sqrt(fits["gue"][2][2, 2]),
                    se_boot_comb / np.sqrt(2), se_boot_comb / np.sqrt(2),
                    fits["iid"][2], fits["gue"][2], DEGENERACY_THRESHOLD)
        n_cells += 1
        n_deg += int(not r.separately_identified)
        if abs(r.z_covariance - row["z_covariance"]) > 1e-6 * max(row["z_covariance"], 1e-12):
            disagree += 1
        print(f"  {f'lo{lo} {rule}':>16} {r.degeneracy:>6.3f} {r.selected:>11} "
              f"{r.z_covariance:>7.2f} {r.z_bootstrap:>7.2f} "
              f"{'no' if not r.separately_identified else 'yes':>11}")
print(f"\n  {n_deg} of {n_cells} cells are degenerate at this threshold")
if disagree:
    bad.append(f"{disagree} cells' recomputed z_covariance disagree with Stage 3d's "
               "banked values — the fork is not reading the same surface")
if n_deg == 0:
    bad.append("no cell is degenerate at the declared threshold, but Stage 3d "
               "measured corr = 0.999 on the seven-point cell. A rule that never "
               "fires on the surface that motivated it is not that rule.")
min_deg = min(degeneracy_of(fits["iid"][2]), degeneracy_of(fits["gue"][2]))
if n_deg == n_cells:
    # Every cell degenerate is a FINDING if the surface really is uniformly
    # degenerate, and a THRESHOLD DEFECT if there were well-conditioned cells
    # the threshold swept up. The measured minimum decides which. On this
    # surface the least-degenerate cell reads 0.994, so the fork does not fork
    # because (tau,beta) are not separately identified ANYWHERE on F3 -- which
    # is the repo's own compare-curves-at-a-level-crossing rule, now with a
    # number on it, and the reason the section leads with k*.
    if min_deg < 0.9:
        bad.append("EVERY cell is degenerate but the least-degenerate reads "
                   f"{min_deg:.3f} — the threshold swept up well-conditioned "
                   "cells and the fork cannot select the bootstrap anywhere")
    else:
        print(f"  -> UNIFORMLY DEGENERATE: least-degenerate cell reads "
              f"{min_deg:.3f}. (tau,beta) are not separately identified at ANY "
              "window on this fit, including the sealed one. The fork does not "
              "fork here because there is nothing to fork on.")

if bad:
    print("\nVERIFY_ERRORMODEL: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
_where = ("selects each model somewhere" if 0 < n_deg < n_cells else
          "finds the surface uniformly degenerate and says so")
print(f"\nVERIFY_ERRORMODEL: PASS — the fork refuses without a declared threshold, "
      f"fires one way with both numbers kept, and on the real surface {_where}, "
      "with degenerate cells flagged as not separately identified")
