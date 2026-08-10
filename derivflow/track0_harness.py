#!/usr/bin/env python3
"""derivflow Track-0 harness — root-space differentiation flow + Hermite self-map gate.

Scope: derivflow/TRACK0_SCOPE.md (v1.1). This file implements the harness and runs the
Hermite known-answer gate (§5c / §6). The other three seeds run only after this gate is green.

HERMITE CONVENTION (pinned): physicists' H_n throughout — recurrence H_{k+1} = 2x H_k - 2k H_{k-1},
identity H_n' = 2n H_{n-1}, roots of H_m supported on ~[-sqrt(2m), +sqrt(2m)].
Probabilists' He_n differs by a sqrt(2) dilation (He_n(x) = 2^{-n/2} H_n(x/sqrt 2)); scipy's
roots_hermite is physicists'. A convention slip is a multiplicative sqrt(2) on every position and
must blow the raw-position gate by ~5 orders, not eat quietly into a tolerance budget.

GATE STRUCTURE (Will's note 1): the identity H_n' = 2n H_{n-1} moves ROOTS with NO rescaling;
rescaling enters only at the unfolding layer (support shrinks ~ 2*sqrt(2(n-k)) at step k). Two
independent comparisons, both required green:
  A (raw positions): flowed roots vs reference Hermite roots. AUTHORITATIVE reference is mpmath
    at elevated precision (Newton-refined via the recurrence) at checkpoints, so the gate measures
    the iteration, not scipy's float64 reference. Per-step scipy comparison is ADVISORY (logged).
  B (unfolding layer): unfolded bulk mean spacing vs 1, per-step semicircle radius sqrt(2m).
Structural checks every step: strict interlacing brackets — violation is a hard FAIL, not a warning.
"""
import json, sys, time
import numpy as np
from scipy.special import roots_hermite
from mpmath import mp

# ---- declared constants (TRACK0_SCOPE §4-§6; do not tune after seeing results) ----
N_SEED = 512               # seed degree n
M_MIN = 32                 # stop when n-k roots remain (s_max = 1 - M_MIN/N_SEED ~ 0.9375)
RAW_TOL = 1e-9             # gate A: max |x_i - ref_i| / local mean spacing, vs mpmath reference
UNFOLD_MEAN_TOL = 0.02     # gate B: |bulk mean unfolded spacing - 1|; O(1/m) finite-size headroom
BULK_FRACTION = 0.20       # central flat window; Phase 1/3 convention (central W of 5W,
                           # arsrh/phase1_zeta_crossover.py:48) — applied identically at every s
MIN_WINDOWED_SPACINGS = 64 # readout power floor vs POST-WINDOW count (Will's note 3); Phase 1
                           # mapped jitter sd(W)~c/sqrt(W), no fixed floor — this is the harness
                           # floor; the seal must state its own W and power at seal time
N_CHECKPOINTS = 8          # mpmath gate-A checkpoints, spread over k incl. first and last
MPMATH_DPS = 40            # elevated precision for the authoritative reference
SIGMA2_LS = [4, 8, 16]     # number-variance box lengths logged along the flow


class GateFail(Exception):
    pass


def diff_step(r):
    """Roots of p' from roots r of p: solve S(x) = sum 1/(x-r_i) = 0 on each (r_i, r_{i+1}).

    S is strictly decreasing on each interval (S' = -sum (x-r_i)^-2 < 0) with S -> +inf/-inf at
    the ends, so each bracket holds exactly one root: bisection cannot lose or duplicate one.
    """
    a, b = r[:-1].copy(), r[1:].copy()
    if not np.all(b > a):
        raise GateFail("degenerate bracket: input roots not strictly increasing")
    lo, hi = a.copy(), b.copy()
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        s = np.sum(1.0 / (mid[:, None] - r[None, :]), axis=1)
        neg = s < 0.0                      # S decreasing: S(mid)<0 -> root left of mid
        hi = np.where(neg, mid, hi)
        lo = np.where(neg, lo, mid)
    x = 0.5 * (lo + hi)
    for _ in range(3):                     # Newton polish, clamped to the bracket
        d = x[:, None] - r[None, :]
        s = np.sum(1.0 / d, axis=1)
        sp = -np.sum(1.0 / d**2, axis=1)
        x = np.clip(x - s / sp, a + 1e-300, b - 1e-300)
    if not (np.all(x > a) & np.all(x < b) & np.all(np.diff(x) > 0)):
        raise GateFail("interlacing violated after solve")
    return x


def hermite_roots_mp(m, seed_f64):
    """Authoritative H_m roots: Newton on the recurrence at MPMATH_DPS from float64 seeds."""
    mp.dps = MPMATH_DPS
    out = []
    for x0 in seed_f64:
        x = mp.mpf(x0)
        for _ in range(4):
            hkm1, hk = mp.mpf(1), 2 * x   # H_0, H_1
            for j in range(1, m):
                hkm1, hk = hk, 2 * x * hk - 2 * j * hkm1
            x = x - hk / (2 * m * hkm1)   # H_m'(x) = 2m H_{m-1}(x)
        out.append(x)
    return out


def unfold_semicircle(r, m):
    """Unfold vs the per-step semicircle: radius sqrt(2m), CDF 1/2 + (y sqrt(1-y^2) + asin y)/pi."""
    y = np.clip(r / np.sqrt(2.0 * m), -1.0, 1.0)
    return m * (0.5 + (y * np.sqrt(1.0 - y * y) + np.arcsin(y)) / np.pi)


def bulk_idx(m):
    w = max(2, int(np.ceil(BULK_FRACTION * m)))
    i0 = (m - w) // 2
    return slice(i0, i0 + w)


def rtilde(gaps):
    return float(np.mean(np.minimum(gaps[:-1], gaps[1:]) / np.maximum(gaps[:-1], gaps[1:])))


def sigma2(u, L):
    """Number variance: variance of counts in length-L boxes slid along the unfolded window."""
    t0 = np.arange(u[0], u[-1] - L, 0.5)
    if len(t0) < 8:
        return None
    counts = np.searchsorted(u, t0 + L) - np.searchsorted(u, t0)
    return float(np.var(counts))


def scaled_dev(x, ref):
    gaps = np.diff(ref)
    local = np.empty_like(ref)
    local[1:-1] = 0.5 * (gaps[:-1] + gaps[1:])
    local[0], local[-1] = gaps[0], gaps[-1]
    return float(np.max(np.abs(x - ref) / local))


def run_hermite_gate():
    t_start = time.time()
    n = N_SEED
    r = roots_hermite(n)[0]
    ks = list(range(1, n - M_MIN + 1))
    cps = sorted(set(np.linspace(1, ks[-1], N_CHECKPOINTS, dtype=int).tolist()))
    steps, checkpoints, verdict, fail_reason = [], [], "PASS", None
    try:
        for k in ks:
            r = diff_step(r)
            m = n - k
            ref64 = roots_hermite(m)[0]
            dev64 = scaled_dev(r, ref64)                 # advisory (float64 reference)
            u = unfold_semicircle(r, m)
            bi = bulk_idx(m)
            ub = u[bi]
            du = np.diff(ub)
            mean_dev = abs(float(np.mean(du)) - 1.0)
            if mean_dev > UNFOLD_MEAN_TOL:               # gate B, every step
                raise GateFail(f"unfold bulk mean spacing off by {mean_dev:.4g} at k={k} (m={m})")
            rb = r[bi]
            gaps = np.diff(rb)
            rt = rtilde(np.diff(ub)) if len(ub) > 2 else None
            rec = {"k": k, "m": m, "s": k / n, "dev_vs_scipy": dev64,
                   "unfold_mean_dev": mean_dev, "unfold_max_gap_dev": float(np.max(np.abs(du - 1.0))),
                   "windowed_spacings": len(du), "readout_powered": len(du) >= MIN_WINDOWED_SPACINGS,
                   "rtilde_bulk": rt,
                   "one_minus_rtilde": (1.0 - rt) if rt is not None else None,
                   "sigma2": {str(L): sigma2(ub, L) for L in SIGMA2_LS}}
            steps.append(rec)
            if k in cps:                                  # gate A, authoritative
                refmp = hermite_roots_mp(m, ref64)
                mp.dps = MPMATH_DPS
                dev_mp = max(abs(mp.mpf(xi) - ri) for xi, ri in zip(r, refmp))
                local = float(np.median(np.diff(ref64)))
                dev_mp_scaled = float(dev_mp) / local
                ref_floor = max(abs(mp.mpf(xi) - ri) for xi, ri in zip(ref64, refmp))
                checkpoints.append({"k": k, "m": m, "s": k / n,
                                    "dev_vs_mpmath_scaled": dev_mp_scaled,
                                    "scipy_ref_floor_scaled": float(ref_floor) / local})
                if dev_mp_scaled > RAW_TOL:
                    raise GateFail(f"raw-position dev {dev_mp_scaled:.3g} > {RAW_TOL} at k={k}")
    except GateFail as e:
        verdict, fail_reason = "FAIL", str(e)
    out = {"gate": "hermite-self-map", "scope": "TRACK0_SCOPE.md v1.1", "verdict": verdict,
           "fail_reason": fail_reason,
           "constants": {"N_SEED": N_SEED, "M_MIN": M_MIN, "RAW_TOL": RAW_TOL,
                         "UNFOLD_MEAN_TOL": UNFOLD_MEAN_TOL, "BULK_FRACTION": BULK_FRACTION,
                         "MIN_WINDOWED_SPACINGS": MIN_WINDOWED_SPACINGS,
                         "MPMATH_DPS": MPMATH_DPS, "N_CHECKPOINTS": N_CHECKPOINTS},
           "runtime_s": round(time.time() - t_start, 1),
           "checkpoints": checkpoints, "steps": steps}
    with open("derivflow/track0_hermite_gate.json", "w") as f:
        json.dump(out, f, indent=1)
    powered = [x for x in steps if x["readout_powered"]]
    print(f"VERDICT: {verdict}" + (f" — {fail_reason}" if fail_reason else ""))
    print(f"steps run: {len(steps)}/{len(ks)}  (s up to {steps[-1]['s']:.4f})" if steps else "no steps")
    if checkpoints:
        w = max(c["dev_vs_mpmath_scaled"] for c in checkpoints)
        fl = max(c["scipy_ref_floor_scaled"] for c in checkpoints)
        print(f"gate A worst dev vs mpmath (scaled): {w:.3g}   (tol {RAW_TOL}; scipy ref floor {fl:.3g})")
    if steps:
        print(f"gate B worst unfold mean dev: {max(x['unfold_mean_dev'] for x in steps):.3g} (tol {UNFOLD_MEAN_TOL})")
        print(f"advisory worst dev vs scipy ref: {max(x['dev_vs_scipy'] for x in steps):.3g}")
        print(f"readout-powered steps (post-window >= {MIN_WINDOWED_SPACINGS}): {len(powered)}, "
              f"last at s = {powered[-1]['s']:.3f}" if powered else "no powered readout steps")
    print(f"runtime: {out['runtime_s']}s -> derivflow/track0_hermite_gate.json")
    return verdict


if __name__ == "__main__":
    sys.exit(0 if run_hermite_gate() == "PASS" else 1)
