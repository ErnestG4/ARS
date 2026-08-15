"""Comb arc G1: exact-offset pair counting on integer coordinates.
COMMITTED GENERATOR discipline: every banked number descends from this file
plus singular_series.py; no distance binning anywhere (the B2 pcf bins were
the pilot's convenience, not the calibrator's instrument).

Estimator (sealed): for offset h and point set P in window W,
  C(h)  = #{ z in P : z+h in P }                     (z+h in W is implied)
  E(h)  = sum_{z in P, z+h in W} rho_model(|z+h|)    (null expectation)
  rho_model(r) = 2 * lambda_model(r) = 4/(pi ln r)   (checkerboard occupancy;
                 lambda validated to 0.04% vs Landau in bridge B2)
  S'_hat(class) = sum_{h in class} C(h) / sum_{h in class} E(h)
  sigma          = sqrt(sum C) / sum E               (Poisson)
The window indicator inside E matches the count restriction exactly — exact
border correction for lattice offsets (no correction-weight code path).
Under the support null (independent checkerboard occupancy at rho_model),
S' == 1 identically; the science is entirely in S' != 1.

One transition per path (bridge tripwire 1): raw integer coordinates
throughout; nothing here unfolds or reweights.
"""

import json
import sys
import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool")
from phase34d.gaussian_primes import sieve_primes, split_p_as_sum_of_two_squares

ENC = 1 << 26   # coordinate encoder: a*ENC + b  (coords < 2^25 in all bands)


def lam_model(r):
    return 2.0 / (np.pi * np.log(r))


def build_points(norm_lo, norm_hi, t1, t2):
    """Split Gaussian primes (canonical a>=b>0 rep) with norm in [lo,hi],
    angle in [t1,t2].  Returns int64 array (n,2)."""
    primes = sieve_primes(int(norm_hi))
    primes = primes[(primes >= norm_lo) & (primes % 4 == 1)]
    # Canonical reps have a >= b > 0, i.e. theta in (0, pi/4]. A window with
    # t2 > pi/4 CANNOT be filled by this builder — the conjugate reps (b,a)
    # are never emitted, and E(h) would integrate an area the data never
    # covers (a ~16%-low bias for the originally sealed [0.45,0.85] extension
    # wedge; 2026-08-15 review finding, seal addendum re-specifies extension
    # geometry to theta [0.36,0.78]).  Refuse loudly rather than bias.
    assert t2 <= np.pi / 4, (f"build_points: t2={t2} exceeds pi/4 — canonical "
                             "reps cannot fill this window (see seal addendum "
                             "2026-08-15)")
    pts = []
    for p in primes:
        a, b = split_p_as_sum_of_two_squares(int(p))
        th = np.arctan2(b, a)
        if t1 <= th <= t2:
            pts.append((a, b))
    if not pts:                       # empty window degrades, not crashes
        return np.empty((0, 2), dtype=np.int64)
    return np.array(pts, dtype=np.int64)


def in_window(xy, norm_lo, norm_hi, t1, t2):
    n = xy[:, 0].astype(np.float64) ** 2 + xy[:, 1].astype(np.float64) ** 2
    th = np.arctan2(xy[:, 1], xy[:, 0])
    return (n >= norm_lo) & (n <= norm_hi) & (th >= t1) & (th <= t2)


def canonical_half(offsets):
    """Exactly one of {h, -h} per pair: (c,d) with c>0, or c==0 and d>0.
    Counting BOTH would tally each unordered pair twice with perfectly
    correlated counts, inflating naive Poisson z-scores by sqrt(2) — the
    estimator KAG caught exactly this on first run."""
    return [h for h in offsets if h[0] > 0 or (h[0] == 0 and h[1] > 0)]


def measure(pts, classes, norm_lo, norm_hi, t1, t2):
    """Per-class S'_hat with Poisson sigma.  classes: {cid: {offsets: [...]}}
    Counts run over the canonical half-set (unordered pairs once)."""
    enc = np.sort(pts[:, 0] * ENC + pts[:, 1])
    out = {}
    for cid, cl in classes.items():
        Csum, Esum = 0, 0.0
        for h in canonical_half(cl["offsets"]):
            shifted = pts + np.array(h, dtype=np.int64)
            m = in_window(shifted, norm_lo, norm_hi, t1, t2)
            sh = shifted[m]
            r = np.hypot(sh[:, 0].astype(float), sh[:, 1].astype(float))
            Esum += float((2.0 * lam_model(r)).sum())
            senc = sh[:, 0] * ENC + sh[:, 1]
            idx = np.searchsorted(enc, senc)
            idx = np.clip(idx, 0, len(enc) - 1)
            Csum += int((enc[idx] == senc).sum())
        if Esum <= 0.0:               # no expectation mass: degrade to a
            out[cid] = dict(C=Csum, E=Esum, S_hat=float("nan"),
                            sigma=float("inf"))   # power check catches this
        else:
            out[cid] = dict(C=Csum, E=Esum, S_hat=Csum / Esum,
                            sigma=float(np.sqrt(max(Csum, 1)) / Esum))
    return out


# ── KAG: null recovery on synthetic checkerboard occupation ─────────────────

def synthetic_null(norm_lo, norm_hi, t1, t2, seed):
    """Independent occupation of checkerboard sites at rho_model(r) in the
    window — the §1 support null realized exactly."""
    rng = np.random.default_rng(seed)
    rhi = int(np.ceil(np.sqrt(norm_hi)))
    a = np.arange(0, rhi + 1, dtype=np.int64)
    A, B = np.meshgrid(a, a, indexing="ij")
    xy = np.column_stack([A.ravel(), B.ravel()])
    xy = xy[(xy[:, 0] + xy[:, 1]) % 2 == 1]           # checkerboard support
    xy = xy[in_window(xy, norm_lo, norm_hi, t1, t2)]
    r = np.hypot(xy[:, 0].astype(float), xy[:, 1].astype(float))
    keep = rng.uniform(size=len(xy)) < 2.0 * lam_model(r)
    return xy[keep]


def kag(classes, norm_lo=9_000_000, norm_hi=12_960_000, t1=0.45, t2=0.65,
        seeds=(601, 602, 603, 604, 605, 606, 607, 608)):
    """Null-recovery gate on the synthetic support null.  Two arms:
      (i)  worst |z| <= 4.5 over all seeds x classes (multiplicity-aware);
      (ii) global bias: |grand mean of per-seed mean-z| <= max(3*SD/sqrt(n_seeds), 0.3).
    Arm (ii) self-calibrates its sigma from across-seed scatter because
    per-class z's WITHIN a seed are positively correlated (classes share
    endpoints; cov = rho^3(1-rho) per shared-site triple) — an
    independence-based threshold false-fired on first run and is wrong in
    principle, not just unlucky.  The 0.3 floor (~0.2% on S') is far below
    every science tolerance.  A true systematic keeps the scatter small and
    pushes the grand mean, so the self-calibrated arm still fires."""
    rows = []
    for s in seeds:
        pts = synthetic_null(norm_lo, norm_hi, t1, t2, s)
        res = measure(pts, classes, norm_lo, norm_hi, t1, t2)
        zs = [(v["S_hat"] - 1.0) / v["sigma"] for v in res.values()]
        rows.append(dict(seed=s, n=len(pts), worst_z=float(max(abs(z) for z in zs)),
                         mean_z=float(np.mean(zs))))
        print(f"  KAG seed {s}: n={len(pts)} worst |z| = {rows[-1]['worst_z']:.2f} "
              f"mean z = {rows[-1]['mean_z']:+.3f}", flush=True)
    worst_all = max(r["worst_z"] for r in rows)
    means = np.array([r["mean_z"] for r in rows])
    grand, sd = float(means.mean()), float(means.std(ddof=1))
    thresh = max(3.0 * sd / np.sqrt(len(seeds)), 0.3)
    ok = worst_all <= 4.5 and abs(grand) <= thresh
    print(f"  KAG: worst |z| = {worst_all:.2f} (<=4.5), grand mean z = "
          f"{grand:+.3f} (|.| <= {thresh:.3f})", flush=True)
    return dict(rows=rows, worst_z=worst_all, grand_mean_z=grand,
                sd_of_means=sd, bias_threshold=thresh,
                n_classes=len(classes), PASS=bool(ok))
