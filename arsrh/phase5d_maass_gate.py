"""
Phase 5d — R-016 (the Maass Sigma^2 leg, with the trend out) + the r-tilde invariance one-liner.

R-016 gates the arc's only candidate theorem-grade long-range calibrator: Luo-Sarnak number variance
for arithmetic hyperbolic surfaces. NOTE (§0b): "Luo" appears NOWHERE in this repo -- the long-range
brief does not flag it. The paper is real; the attribution to the brief is UNRESOLVED and is filed as
such. The substance is tested here on its merits.

  M1. r-tilde invariance, MEASURED not argued: <r~> on raw R vs pipeline-unfolded vs detrended.
      CP1 survives Phase 5c because r-tilde is unfold-invariant -- an invariance measured on ZETA and
      transferred to Maass by argument. This converts it to a measurement.
  M2. Sigma^2 per sector: pipeline unfold vs trend-removed vs theory-affine-without-final-rescale.
  M3. Is there any L window where the Poisson linear prediction is testable at all?
"""
from __future__ import annotations
import json, math, os, csv
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
EULER = 0.5772156649015329
OUT = {"anti_claim": "instrument gate on a long-range calibrator; NOT about RH",
       "provenance_note": "Luo-Sarnak is NOT cited anywhere in this repo; attribution to the "
                          "long-range brief is UNRESOLVED. Paper is real; pointer is not in-repo."}


def sigma2(xi, Ls, step=0.25):
    xi = np.sort(xi); lo, hi = xi[0], xi[-1]; out = []
    for L in Ls:
        starts = np.arange(lo, hi - L, step)
        c = np.searchsorted(xi, starts + L) - np.searchsorted(xi, starts)
        out.append(float(np.var(c)))
    return np.array(out)


def mean_rtilde(x):
    s = np.diff(np.sort(x)); s = s[s > 0]
    r = np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])
    return float(r.mean())


def goe_sigma2(L):
    return (2 / math.pi ** 2) * (math.log(2 * math.pi * L) + EULER + 1 - math.pi ** 2 / 8)


rr = list(csv.DictReader(open(os.path.join(ROOT, "sessionK", "maass_level1_partial.csv"))))
R_all = np.array([float(r["r"]) for r in rr]); sym = np.array([int(r["symmetry"]) for r in rr])
SECTOR_B = {0: -2.0 / math.pi, 1: 0.0}
Ls = np.array([1.0, 2.0, 4.0, 8.0, 15.0])
BANKED_RT = {0: 0.3992236272087822, 1: 0.42665331698924214}   # maass_analysis_measured / phase4

p("=== Phase 5d — R-016 + the invariance one-liner ===")
p("§0b: Luo-Sarnak is NOT cited in this repo. Attribution UNRESOLVED; substance tested on merits.\n")

res = {}
for s in (0, 1):
    R = np.sort(R_all[sym == s]); ix = np.arange(1, len(R) + 1, dtype=float)
    a, b = 1.0 / 24.0, SECTOR_B[s]
    y = ix - (a * R ** 2 + b * R * np.log(R))
    M = np.vstack([R, np.ones_like(R)]).T
    (c, d), *_ = np.linalg.lstsq(M, y, rcond=None)
    u_aff = a * R ** 2 + b * R * np.log(R) + c * R + d          # theory-affine, NO final rescale
    S = ix - u_aff
    trend = np.polyval(np.polyfit(R, S, 2), R)
    u_det = u_aff + trend                                        # trend folded into the smooth model
    sp = np.diff(u_aff)
    u_pipe = np.concatenate([[0.0], np.cumsum(sp / sp.mean())])  # what maass_analysis.py does
    spd = np.diff(u_det)
    u_detpipe = np.concatenate([[0.0], np.cumsum(spd / spd.mean())])

    # ---- M1 invariance
    rt = {"raw_R": mean_rtilde(R), "pipeline_unfold": mean_rtilde(u_pipe),
          "theory_affine_norescale": mean_rtilde(u_aff), "detrended": mean_rtilde(u_detpipe)}
    # ---- M2 sigma^2
    s2 = {"pipeline": sigma2(u_pipe, Ls).tolist(),
          "theory_affine_norescale": sigma2(u_aff, Ls).tolist(),
          "detrended": sigma2(u_detpipe, Ls).tolist()}
    varS = {"before": float(np.var(S)), "after": float(np.var(S - trend))}
    res[s] = {"n": int(len(R)), "mean_spacing_u_aff": float(sp.mean()),
              "rtilde": rt, "sigma2": s2, "VarS": varS,
              "sat_2VarS_before": 2 * varS["before"], "sat_2VarS_after": 2 * varS["after"],
              "banked_rtilde": BANKED_RT[s]}

    p(f"--- parity {s}  (n={len(R)}, realized mean spacing of theory-affine unfold = {sp.mean():.5f})")
    p(f"  [M1] <r~>   raw R {rt['raw_R']:.5f} | pipeline {rt['pipeline_unfold']:.5f} | "
      f"theory-affine {rt['theory_affine_norescale']:.5f} | detrended {rt['detrended']:.5f}")
    p(f"       banked (CP1/Phase 4) = {BANKED_RT[s]:.5f};  max spread across all four = "
      f"{max(rt.values())-min(rt.values()):.5f}")
    p(f"  [M2] Sigma^2 at L = {list(Ls.astype(int))}:")
    p(f"       pipeline (banked path) : " + " ".join("%7.4f" % v for v in s2["pipeline"]))
    p(f"       trend removed          : " + " ".join("%7.4f" % v for v in s2["detrended"]))
    p(f"       no final rescale       : " + " ".join("%7.4f" % v for v in s2["theory_affine_norescale"]))
    p(f"       Poisson reference (=L) : " + " ".join("%7.4f" % v for v in Ls))
    p(f"       GOE reference          : " + " ".join("%7.4f" % goe_sigma2(v) for v in Ls))
    p(f"       Var[S] {varS['before']:.4f} -> {varS['after']:.4f} after detrend; "
      f"saturation 2Var[S] {2*varS['before']:.4f} -> {2*varS['after']:.4f}")

# ---- M3
p("\n[M3] is there ANY L window where the Poisson linear prediction is testable?")
for s in (0, 1):
    sat = res[s]["sat_2VarS_after"]
    s2p = np.array(res[s]["sigma2"]["pipeline"])
    ok = [float(L) for L, v in zip(Ls, s2p) if abs(v - L) / L < 0.2]
    p(f"  parity {s}: Sigma^2 saturates near 2Var[S] = {sat:.3f} after detrending, i.e. below ONE mean")
    p(f"            spacing. L values where the measured Sigma^2 is within 20% of Poisson's L: {ok or 'NONE'}")
    p(f"            measured Sigma^2(15) = {s2p[-1]:.3f} against a Poisson prediction of 15.0 "
      f"({15/s2p[-1]:.0f}x short)")
OUT["sectors"] = res
OUT["M3"] = {"poisson_window_exists": False}

json.dump(OUT, open(os.path.join(HERE, "phase5d_maass_gate_measured.json"), "w"), indent=2, default=float)
p("\nwrote phase5d_maass_gate_measured.json")
