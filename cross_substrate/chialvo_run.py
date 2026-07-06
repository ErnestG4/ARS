"""
cross_substrate/chialvo_run.py — Track 1.1 calibrator (Phase 36 Torus-Breakdown Extension).

The Chialvo (1995) neuron map is a 2-D discrete-time map with a Neimark-Sacker (NS) bifurcation
→ invariant closed curve (2-torus) → Arnold tongues / mode-locking → quasiperiodicity→chaos via
torus breakdown. It is a controlled CALIBRATOR (not a substrate-of-study): a system whose
breakdown generates the kind of quasiperiodic→chaotic transition the torus-breakdown lens targets.

Map:
    x_{n+1} = x_n^2 · exp(y_n - x_n) + k
    y_{n+1} = a·y_n - b·x_n + c
  x = activation (fast), y = recovery (slow); (a,b,c,k) params.

Ground-truth transition loci (this is what makes it a calibrator):
  - **NS onset** (torus birth): analytic — the fixed point's Jacobian complex-conjugate eigenvalue
    pair crosses the unit circle, i.e. det J(fixed pt) = 1 with |tr J| < 2. Solved by 1-D root-find
    in the bifurcation parameter. (`ns_locus`)
  - **Torus breakdown** (quasiperiodicity→chaos): λ₁ crosses 0 from below. λ₁ via tangent-space
    (Benettin) iteration of the 2-D map — exact in sign AND magnitude for known equations
    (same tool class as mg_lyapunov_benettin / dynamical_breadth). (`chialvo_lyapunov`)

Per-calibrator protocol (matches run_phase20_5_calibrators + dynamical_breadth conventions):
  events = median-upcrossing transitions of x_n (NOT find_peaks); IEI → cumsum → event times.
  - detection: swept-parameter trajectory through the λ₁=0 locus → characterize_transition.
  - no-false-positive: stationary pure-quasiperiodic regime (λ₁≈0, smooth torus) → flat trajectory.
  - sensitivity: N floor for reliable detection.
  - engine attribution: which axis (rep_int NNS vs rf_amplitude RF) carries the signal.

This module holds the DYNAMICS + locus tools only (gate-independent). The instrument-run harness
that feeds events through joint_q_profile/characterize_transition is `chialvo_calibrate.py`, run
ONLY after Track 0 passes (strict gate).
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import brentq

# ── CANONICAL CALIBRATOR ROUTE (located 2026-05-31 by λ₁-Benettin scan) ────────────────────────
# Fix (b, k); sweep the recovery-decay `a` as the bifurcation parameter. As a↑ the system runs
#   smooth 2-torus (λ₁≈0)  →  Arnold-tongue mode-locking windows (λ₁<0)  →  torus  →  CHAOS (λ₁>0),
# i.e. a textbook quasiperiodicity→chaos via torus breakdown. λ₁=0→+ crossing (the breakdown locus)
# is located exactly by tangent-space Benettin (known equations). Event counts are adequate
# (~1500–2100 median-upcrossings per 40k iter) on BOTH sides — usable for the diagnostic.
A, C = 0.89, 0.28        # A here is only the default/QUASIPERIODIC anchor; `a` is the swept knob.
B = 0.45                 # fixed for the route
K_CAL = 0.06             # fixed for the route
A_QUASI = 0.89           # pure quasiperiodic torus (λ₁≈0)        — the no-false-positive regime
A_CHAOS = 0.97           # developed chaos (λ₁≈+0.054)            — the post-breakdown regime
A_BREAKDOWN = 0.962      # torus→chaos breakdown locus (λ₁ crosses 0+); Arnold tongues at a≈0.925–0.95


def chialvo_step(x, y, a=A, b=B, c=C, k=0.03):
    return x * x * np.exp(y - x) + k, a * y - b * x + c


def chialvo_iterate(k, n, discard=2000, a=A, b=B, c=C, x0=0.9, y0=0.2):
    """Iterate the map; return (x_seq, y_seq) of length n after discarding transient."""
    x, y = float(x0), float(y0)
    for _ in range(discard):
        x, y = chialvo_step(x, y, a, b, c, k)
    xs = np.empty(n); ys = np.empty(n)
    for i in range(n):
        x, y = chialvo_step(x, y, a, b, c, k)
        xs[i] = x; ys[i] = y
    return xs, ys


def _fixed_point(k, a=A, b=B, c=C):
    """Solve x* = x*^2 exp(y*-x*) + k with y* = (c - b x*)/(1-a). 1-D root in x*."""
    def g(xs):
        ys = (c - b * xs) / (1.0 - a)
        return xs * xs * np.exp(ys - xs) + k - xs
    # bracket: scan for a sign change in a physical range
    grid = np.linspace(0.01, 3.0, 4000)
    vals = np.array([g(v) for v in grid])
    sign = np.sign(vals)
    idx = np.where(np.diff(sign) != 0)[0]
    if idx.size == 0:
        return None
    i = idx[0]
    xs = brentq(g, grid[i], grid[i + 1])
    return xs, (c - b * xs) / (1.0 - a)


def _jacobian(x, y, a=A, b=B, c=C):
    e = np.exp(y - x)
    return np.array([[x * (2.0 - x) * e, x * x * e],
                     [-b, a]])


def ns_locus(k_lo=0.0, k_hi=0.2, a=A, b=B, c=C):
    """Neimark-Sacker onset: smallest k where det J(fixed pt)=1 with complex eigenvalues
    (|tr J| < 2). Returns (k_NS, fixed_pt, eigs) or None."""
    def detm1(k):
        fp = _fixed_point(k, a, b, c)
        if fp is None:
            return np.nan
        J = _jacobian(fp[0], fp[1], a, b, c)
        return np.linalg.det(J) - 1.0
    ks = np.linspace(k_lo, k_hi, 800)
    d = np.array([detm1(k) for k in ks])
    valid = np.isfinite(d)
    ks, d = ks[valid], d[valid]
    sgn = np.sign(d)
    idx = np.where(np.diff(sgn) != 0)[0]
    for i in idx:
        try:
            kns = brentq(lambda kk: np.linalg.det(_jacobian(*_fixed_point(kk, a, b, c), a, b, c)) - 1.0,
                         ks[i], ks[i + 1])
        except Exception:
            continue
        fp = _fixed_point(kns, a, b, c)
        J = _jacobian(fp[0], fp[1], a, b, c)
        eg = np.linalg.eigvals(J)
        if abs(np.trace(J)) < 2.0 and np.iscomplexobj(eg):  # complex pair => NS (not saddle-node)
            return kns, fp, eg
    return None


def chialvo_lyapunov(k, n=200_000, discard=20_000, a=A, b=B, c=C, x0=0.9, y0=0.2):
    """Largest Lyapunov exponent λ₁ via tangent-space (Benettin) iteration of the 2-D map.
    Exact sign+magnitude for known equations. λ₁<0: fixed point/cycle; ≈0: quasiperiodic torus;
    >0: chaos. The λ₁=0 crossing is the torus-breakdown (quasiperiodicity→chaos) locus."""
    x, y = float(x0), float(y0)
    for _ in range(discard):
        x, y = chialvo_step(x, y, a, b, c, k)
    v = np.array([1.0, 0.0]); lsum = 0.0
    for _ in range(n):
        J = _jacobian(x, y, a, b, c)
        v = J @ v
        nv = np.hypot(v[0], v[1])
        if nv > 0:
            lsum += np.log(nv); v /= nv
        x, y = chialvo_step(x, y, a, b, c, k)
    return lsum / n


def median_upcrossing_events(x):
    """Event times = upward crossings of the running... here global median of x_n (matches the
    dynamical_breadth 'median-upcrossing transitions, NOT find_peaks' event convention). Returns
    integer crossing indices as event 'times' (uniform clock); downstream renormalises to unit mean."""
    x = np.asarray(x, float)
    med = np.median(x)
    above = x >= med
    up = np.where((~above[:-1]) & (above[1:]))[0] + 1
    return up.astype(np.float64)


def chialvo_swept_a_events(a_start, a_end, n_iter, b=B, c=C, k=K_CAL, x0=0.9, y0=0.2, discard=2000):
    """Sweep the recovery-decay `a` linearly while iterating (parameter-swept trajectory through the
    torus-breakdown locus), return median-upcrossing event times over the whole sweep. Mirrors
    logistic_period_doubling_sweep → logistic_to_events. This is the CANONICAL detection trajectory:
    a_start in the torus regime (≈0.89) → a_end in chaos (≈0.975)."""
    x, y = float(x0), float(y0)
    for _ in range(discard):
        x, y = chialvo_step(x, y, a_start, b, c, k)
    a_seq = np.linspace(a_start, a_end, n_iter)
    xs = np.empty(n_iter)
    for i in range(n_iter):
        x, y = chialvo_step(x, y, a_seq[i], b, c, k)
        xs[i] = x
    return median_upcrossing_events(xs)


def chialvo_swept_a_events_tagged(a_start, a_end, n_iter, b=B, c=C, k=K_CAL, x0=0.9, y0=0.2, discard=2000):
    """As chialvo_swept_a_events, but ALSO return the bifurcation-parameter value `a` at each event —
    so sub-windows (equal event count, hence UNEQUAL a-spans) can be tagged with their a-range and
    each of the TWO edges (torus→mode-locking, mode-locking→chaos) located in a. Returns
    (event_indices, a_at_event)."""
    x, y = float(x0), float(y0)
    for _ in range(discard):
        x, y = chialvo_step(x, y, a_start, b, c, k)
    a_seq = np.linspace(a_start, a_end, n_iter)
    xs = np.empty(n_iter)
    for i in range(n_iter):
        x, y = chialvo_step(x, y, a_seq[i], b, c, k)
        xs[i] = x
    med = np.median(xs)
    above = xs >= med
    up = np.where((~above[:-1]) & (above[1:]))[0] + 1
    return up.astype(np.float64), a_seq[up]


def chialvo_stationary_events(a, n_iter, b=B, c=C, k=K_CAL, x0=0.9, y0=0.2, discard=2000):
    """Median-upcrossing events for a STATIONARY regime at fixed `a` (e.g. A_QUASI for the
    no-false-positive test, A_CHAOS for the chaotic-regime read)."""
    xs = chialvo_iterate(k, n_iter, discard=discard, a=a, b=b, c=c, x0=x0, y0=y0)[0]
    return median_upcrossing_events(xs)


__all__ = ["chialvo_step", "chialvo_iterate", "ns_locus", "chialvo_lyapunov",
           "median_upcrossing_events", "chialvo_swept_a_events", "chialvo_swept_a_events_tagged",
           "chialvo_stationary_events", "_fixed_point", "_jacobian", "A", "B", "C", "K_CAL",
           "A_QUASI", "A_CHAOS", "A_BREAKDOWN"]


if __name__ == "__main__":
    # Self-test of the DYNAMICS ONLY (no instrument): confirm the canonical route's anchors.
    print("Chialvo calibrator route self-test (b=%.2f k=%.2f; sweep a)" % (B, K_CAL))
    for label, a in (("QUASI", A_QUASI), ("BREAKDOWN", A_BREAKDOWN), ("CHAOS", A_CHAOS)):
        lam = chialvo_lyapunov(K_CAL, n=120_000, discard=20_000, a=a, b=B)
        nev = chialvo_stationary_events(a, 80_000).size
        regime = "chaos" if lam > 0.01 else ("torus/quasi" if lam > -0.008 else "periodic")
        print(f"  a={a:.3f} [{label:9s}]: λ₁={lam:+.5f} [{regime:11s}]  upcross-events(80k)={nev}")
    sweep_ev = chialvo_swept_a_events(A_QUASI, A_CHAOS + 0.005, 80_000)
    print(f"  swept a={A_QUASI}→{A_CHAOS+0.005}: {sweep_ev.size} upcross-events (detection trajectory)")
