"""
cross_substrate/hc3_cv2_diagnostic.py — dataset-selection call BEFORE any CA1 pull.

Pass-2 left 20/44 CA3 interneurons INDETERMINATE on the rate-robust local axis
I.12_cv2 at residual z~1.6. Is that indeterminacy SAMPLING-LIMITED (independent
per-unit noise → combining more interneurons converges to a population verdict →
CA1 pull worth it) or τ-SYSTEMATIC (a shared apparatus mis-attribution that does
NOT shrink with N → more units can't manufacture a decision → need a better-
characterized apparatus instead)?

Test on the 44 units already in hand:
  (1) Are the SIGNED cv2 residuals (emp − wide-null mean) consistently same-signed?
  (2) Does the consistent component sit ABOVE or INSIDE the τ-uncertainty floor?
      τ-floor is decomposed by quadrature: run the wide null at rel_err=0 (sampling
      sd σ_samp) and rel_err=0.5 (sampling+τ sd σ_tot); τ-floor = √(σ_tot²−σ_samp²).
      Sampling floor shrinks as σ_samp/√N; the τ-floor, if the apparatus mis-
      estimate is correlated across units (same rig/sorter), does NOT shrink.

Verdict:
  CONSISTENT + CLEAR (|r̄| > τ-floor)        → pull worth it (population verdict reachable)
  SCATTERED                                  → no signal; pull won't help
  CONSISTENT but BURIED (|r̄| < τ-floor)     → τ-systematic; need better apparatus, not more units
"""
from __future__ import annotations

import glob
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import instrument_confound as ic
from hc3_instrument_pass import parse_units, load_cellmap, CAP, HW_REFRACTORY_S

AX = "I.12_cv2"
N_SEEDS = 24
SESSIONS = ["ec016.41/ec016.674", "ec016.44/ec016.733",
            "ec016.45/ec016.749", "ec016.47/ec016.799"]


def _diag(arg):
    spk, label = arg
    full = np.sort(np.asarray(spk, dtype=np.float64))
    spk = full[:CAP] if full.size > CAP else full
    m = ic.mean_isi(spk)
    if not np.isfinite(m) or m <= 0 or spk.size < 200:
        return None
    floor = ic.estimate_deadtime_floor(spk, pct=0.5, rel_err=0.5)
    tau_wide = floor["tau_frac"]
    if tau_wide is None or tau_wide <= 0:
        return None
    emp = ic.axis_values(spk).get(AX)
    if emp is None:
        return None
    # wide null, point-τ (sampling only) and τ-uncertain (sampling + τ)
    s0 = ic.apparatus_subtracted_comparison(spk, tau_wide, tau_frac_rel_err=0.0,
                                            n_seeds=N_SEEDS, base_seed=11)
    sT = ic.apparatus_subtracted_comparison(spk, tau_wide, tau_frac_rel_err=0.5,
                                            n_seeds=N_SEEDS, base_seed=11)
    if AX not in s0 or AX not in sT:
        return None
    mu0 = s0[AX]["injected_null"]["mean"]
    samp = s0[AX]["injected_null"]["sd"]
    tot = sT[AX]["injected_null"]["sd"]
    tau_floor = math.sqrt(max(tot * tot - samp * samp, 0.0))
    r = emp - mu0                                   # SIGNED residual
    # bracket zone on cv2 (tight = hw refractory)
    tau_tight = min(HW_REFRACTORY_S / m, 0.5 * tau_wide)
    br = ic.apparatus_bracket(spk, tau_tight, tau_wide, n_seeds=N_SEEDS)
    zone = br.get(AX, {}).get("zone")
    return dict(label=label, n=int(spk.size), mean_isi=m, emp=emp, mu0=mu0,
                r=r, samp=samp, tot=tot, tau_floor=tau_floor, zone=zone)


def main():
    cm = load_cellmap()
    args = []
    for s in SESSIONS:
        sdir = os.path.expanduser(f"~/fmexplorer/crcns_cache/sessions/{s}")
        topdir, session = s.split("/")
        units, tmax, sr = parse_units(sdir, topdir, session, cm)
        for u in units:
            if u["region"] == "CA3" and u["celltype"] == "inhibitory" and u["spk"].size >= 200:
                args.append((u["spk"], f"{session}_e{u['ele']}c{u['clu']}"))
    print(f"CA3 interneurons in hand: {len(args)} units across {len(SESSIONS)} sessions")

    with ProcessPoolExecutor(max_workers=10) as ex:
        recs = [r for r in ex.map(_diag, args) if r is not None]
    print(f"computed {len(recs)} units on {AX}\n")

    r = np.array([x["r"] for x in recs])
    samp = np.array([x["samp"] for x in recs])
    tauf = np.array([x["tau_floor"] for x in recs])
    n = len(r)
    indet = [x for x in recs if x["zone"] == "INDETERMINATE"]

    # (1) sign consistency
    npos, nneg = int(np.sum(r > 0)), int(np.sum(r < 0))
    maj = max(npos, nneg)
    # two-sided binomial sign test p
    from math import comb
    p_sign = sum(comb(n, k) for k in range(maj, n + 1)) / 2 ** n * 2
    p_sign = min(1.0, p_sign)
    sign = "+" if npos >= nneg else "-"

    # (2) consistent component vs floors
    rbar = float(np.mean(r))
    samp_pop = float(np.sqrt(np.mean(samp ** 2)) / np.sqrt(n))   # shrinks with N
    tau_sys = float(np.mean(tauf))                              # correlated → no √N
    tau_indep = float(np.sqrt(np.mean(tauf ** 2)) / np.sqrt(n))  # independent → √N

    print(f"SIGN CONSISTENCY (signed cv2 residual emp−null):")
    print(f"  {npos} positive / {nneg} negative of {n}  (sign {sign}, two-sided p={p_sign:.4g})")
    print(f"  INDETERMINATE-on-cv2 subset: {len(indet)} units; "
          f"{sum(1 for x in indet if x['r']>0)}+/{sum(1 for x in indet if x['r']<0)}-")
    print(f"\nCONSISTENT COMPONENT vs FLOORS:")
    print(f"  mean signed residual  r̄        = {rbar:+.4f}")
    print(f"  sampling floor (σ̄/√N)          = {samp_pop:.4f}   (shrinks with N)")
    print(f"  τ-floor, systematic (mean)     = {tau_sys:.4f}   (correlated → does NOT shrink)")
    print(f"  τ-floor, independent (√N)      = {tau_indep:.4f}")
    print(f"  |r̄| / τ-floor(sys)             = {abs(rbar)/tau_sys if tau_sys>0 else float('inf'):.2f}")
    print(f"  per-unit |r|>τ_floor (clear):  {sum(1 for x in recs if abs(x['r'])>x['tau_floor'])}/{n}")

    # verdict — require a real MARGIN over the systematic floor; a ratio ~1 is
    # sitting ON the floor, not clear of it (a 6% margin is within our own
    # modeling slop on rel_err).
    MARGIN = 1.5
    consistent = p_sign < 0.05
    ratio_sys = abs(rbar) / tau_sys if tau_sys > 0 else float("inf")
    clear_sys = ratio_sys > MARGIN
    clear_indep = abs(rbar) > tau_indep
    print(f"\nVERDICT (clear requires |r̄| > {MARGIN}× the floor):")
    if not consistent:
        v = ("SCATTERED → no consistent signal; more interneurons will NOT "
             "manufacture a verdict. CA1 pull NOT worth it on cv2.")
    elif clear_sys:
        v = ("CONSISTENT + CLEAR of even the systematic τ-floor by >1.5× → genuine "
             "biological component; population verdict reachable. CA1 pull WORTH IT.")
    elif clear_indep:
        v = (f"CONSISTENT but the consistent component sits ON the systematic τ-floor "
             f"(ratio {ratio_sys:.2f}, no real margin). It clears the floor ONLY if τ "
             f"errors are INDEPENDENT across units (√N); if the apparatus mis-estimate "
             f"is shared across same-rig/sorter units (likely), it is BURIED. The "
             f"indeterminacy is τ-LIMITED, not sampling-limited. → DON'T pull CA1 on "
             f"this. Collapse the τ-floor first: documented hardware dead time for "
             f"these Mizuseki/Buzsáki recordings (rel_err→small moves it to the √N "
             f"regime where the signal is ~{abs(rbar)/tau_indep:.0f}σ clear), or a "
             f"slower comparison population (smaller apparatus/ISI ratio).")
    else:
        v = ("CONSISTENT but BURIED in the τ-floor → τ-systematic; more units can't "
             "separate biology from apparatus. Need better-characterized apparatus, "
             "NOT a CA1 pull.")
    print(f"  {v}")


if __name__ == "__main__":
    main()
