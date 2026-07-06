"""
transition_calibrators_dynamical.py — Phase 20.5 Tier 1.B.

Parameter-driven (dynamical) transition calibrators: regime-shift
sequences emerging from underlying nonlinear dynamical systems as a
control parameter varies across bifurcation thresholds.  Connects the
framework to four decades of established nonlinear dynamics benchmark
work (Feigenbaum 1978, May 1976, Mackey-Glass 1977, Lorenz 1963).

Three systems in priority order:

  1. Logistic map x_{n+1} = r·x_n·(1 − x_n)  — fully discrete, no
     extraction step needed.  Bifurcation parameter r ∈ (1, 4):
       r ∈ (1, 3)             stable fixed point
       r ∈ (3, 1+√6)           period-2
       r ∈ (1+√6, ~3.544)      period-4
       r ∈ (~3.544, ~3.564)    period-8
       r ∈ (~3.569, 4)         chaos (with periodic windows)

  2. Mackey-Glass dx/dt = β·x(t-τ)/(1 + x(t-τ)^n) − γ·x(t)  —
     continuous trajectory, requires event extraction; per Phase 19
     discipline, three mechanism-distinct extractors with consensus
     classification.  Bifurcation parameter τ:
       τ < ~6                  stable equilibrium
       τ ∈ (~6, ~17)           periodic
       τ > ~17                 chaotic

  3. Lorenz dx/dt = σ(y-x), dy/dt = x(ρ-z)−y, dz/dt = xy−βz  —
     continuous; events are lobe-transitions of the butterfly
     attractor.  Optional / Phase 22+ if budget exhausted.
"""
from __future__ import annotations

import os, sys
from typing import Optional

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)


# ─── Logistic map ──────────────────────────────────────────────────────────


def logistic_iterate(r: float, x0: float, n_iter: int,
                       discard: int = 200) -> np.ndarray:
    """Iterate x_{n+1} = r·x_n·(1−x_n) for n_iter+discard steps,
    return the last n_iter values (after settling transient)."""
    x = float(x0)
    out = np.empty(n_iter, dtype=np.float64)
    # Discard transient
    for _ in range(discard):
        x = r * x * (1.0 - x)
    for i in range(n_iter):
        x = r * x * (1.0 - x)
        out[i] = x
    return out


def logistic_iterate_swept_r(
        r_start: float, r_end: float,
        x0: float, n_iter: int,
        discard: int = 200,
        ) -> np.ndarray:
    """Iterate logistic map with r varying linearly from r_start to
    r_end across n_iter steps."""
    rs = np.linspace(r_start, r_end, n_iter)
    x = float(x0)
    # Discard at r_start
    for _ in range(discard):
        x = r_start * x * (1.0 - x)
    out = np.empty(n_iter, dtype=np.float64)
    for i, r in enumerate(rs):
        x = r * x * (1.0 - x)
        out[i] = x
    return out


def logistic_iterate_round_trip(
        r_lo: float, r_hi: float,
        x0: float, n_iter_each: int,
        discard: int = 200,
        ) -> np.ndarray:
    """Sweep r from r_lo to r_hi, then back to r_lo; return all
    iterations."""
    forward = logistic_iterate_swept_r(r_lo, r_hi, x0, n_iter_each, discard)
    # Continue from last x
    x = float(forward[-1])
    rs = np.linspace(r_hi, r_lo, n_iter_each)
    backward = np.empty(n_iter_each, dtype=np.float64)
    for i, r in enumerate(rs):
        x = r * x * (1.0 - x)
        backward[i] = x
    return np.concatenate([forward, backward])


def logistic_to_events(x_seq: np.ndarray, mode: str = 'iei') -> np.ndarray:
    """Convert a logistic-map iteration sequence to an event-time
    sequence for joint_q_profile.

    Modes:
      - 'iei': treat successive differences |x_{n+1} − x_n| as IEIs;
        cumsum to event times.  This embeds the dynamics as a
        point process whose IEI distribution captures the regime.
      - 'cumsum': events at cumulative sum of x_n (positive values
        only — periodic regimes give clean periodic events; chaotic
        regimes give Wigner-like spread).
      - 'index': events at fractional-part bin-crossings (like a
        first-return map at level 0.5).
    """
    x = np.asarray(x_seq, dtype=np.float64)
    if mode == 'iei':
        iei = np.abs(np.diff(x))
        iei = iei[iei > 1e-12]
        if iei.size == 0:
            return np.array([0.0])
        iei = iei / iei.mean()
        return np.cumsum(np.concatenate([[0.0], iei]))
    elif mode == 'cumsum':
        ev = np.cumsum(np.maximum(x, 1e-9))
        sp = np.diff(ev)
        sp = sp[sp > 0]
        if sp.size and sp.mean() > 0:
            ev = np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))
        return ev
    elif mode == 'index':
        # First-return events at each upcrossing of 0.5
        above = x > 0.5
        transitions = np.diff(above.astype(np.int8))
        upcross = np.where(transitions == 1)[0] + 1
        if upcross.size < 2:
            return np.zeros(0)
        ev = upcross.astype(np.float64)
        sp = np.diff(ev)
        sp = sp[sp > 0]
        if sp.size and sp.mean() > 0:
            ev = np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))
        return ev
    else:
        raise ValueError(f"unknown mode: {mode}")


LOGISTIC_REGIMES = [
    ('stable_fp',  2.5,  'stable fixed point'),
    ('period_2',   3.2,  'period-2 limit cycle'),
    ('period_4',   3.5,  'period-4 limit cycle'),
    ('chaos',      3.7,  'chaotic'),
    ('period_3',   3.83, 'period-3 window inside chaos'),
]


# ─── Mackey-Glass DDE ──────────────────────────────────────────────────────


def mackey_glass(
        tau: float,
        n_steps: int,
        beta: float = 0.2, gamma: float = 0.1, n_pow: float = 10.0,
        dt: float = 0.1,
        x0: float = 1.2,
        discard: int = 5000,
        ) -> np.ndarray:
    """Integrate Mackey-Glass DDE via explicit Euler with linear
    interpolation for the delayed term.

      dx/dt = β · x(t-τ) / (1 + x(t-τ)^n) − γ · x(t)

    Returns the trajectory (n_steps,) sampled every dt after a
    `discard`-step transient.
    """
    n_delay = max(1, int(round(tau / dt)))
    # Initialise history with x0 for t ∈ [-τ, 0]
    history = np.full(n_delay, x0, dtype=np.float64)
    # Allocate output
    total_steps = discard + n_steps
    x = np.empty(total_steps + n_delay, dtype=np.float64)
    x[:n_delay] = history
    for i in range(n_delay, n_delay + total_steps):
        x_delayed = x[i - n_delay]
        dx = beta * x_delayed / (1.0 + x_delayed ** n_pow) \
             - gamma * x[i - 1]
        x[i] = x[i - 1] + dt * dx
    return x[n_delay + discard:]


MACKEY_GLASS_REGIMES = [
    ('stable',          4.0,  'stable equilibrium'),
    ('periodic',        10.0, 'periodic limit cycle'),
    ('period_doubled',  17.0, 'period-doubled (boundary)'),
    ('chaotic',         23.0, 'chaotic'),
    ('deeper_chaos',    30.0, 'deeper chaos'),
]


# ─── Mackey-Glass extractors (Phase 19 mechanism-distinct discipline) ──────


def mackey_glass_extract_running_mean_upcrossings(
        x: np.ndarray, window: int = 200) -> np.ndarray:
    """Events at upcrossings of the trailing-window mean."""
    n = x.size
    if n < window + 5:
        return np.zeros(0)
    # Trailing mean via cumulative sum
    cs = np.cumsum(x)
    means = (cs[window:] - cs[:-window]) / window
    sig = x[window:]
    above = sig > means
    transitions = np.diff(above.astype(np.int8))
    upcross = np.where(transitions == 1)[0] + 1 + window
    return upcross.astype(np.float64)


def mackey_glass_extract_local_maxima(
        x: np.ndarray, prominence_frac: float = 0.5,
        window: int = 500) -> np.ndarray:
    """Local maxima with prominence threshold = prominence_frac · σ
    of trailing-window x."""
    from scipy.signal import find_peaks
    if x.size < window + 5:
        return np.zeros(0)
    sigma = float(np.std(x[:window]))
    prom = max(prominence_frac * sigma, 1e-9)
    peaks, _ = find_peaks(x, prominence=prom)
    return peaks.astype(np.float64)


def mackey_glass_extract_envelope_upcrossings(
        x: np.ndarray, k: float = 1.0) -> np.ndarray:
    """Events at upcrossings of mean + k·σ on the analytic-signal
    envelope of x."""
    from scipy.signal import hilbert
    if x.size < 16:
        return np.zeros(0)
    analytic = hilbert(x - x.mean())
    env = np.abs(analytic)
    thr = env.mean() + k * env.std()
    above = env > thr
    if above.sum() < 2:
        return np.zeros(0)
    transitions = np.diff(above.astype(np.int8))
    upcross = np.where(transitions == 1)[0] + 1
    return upcross.astype(np.float64)


MACKEY_GLASS_EXTRACTORS = {
    'running_mean_upcrossings': mackey_glass_extract_running_mean_upcrossings,
    'local_maxima_prominence':  mackey_glass_extract_local_maxima,
    'envelope_upcrossings':     mackey_glass_extract_envelope_upcrossings,
}


def mackey_glass_to_events(x: np.ndarray, extractor: str) -> np.ndarray:
    """Apply a named extractor and return unit-mean event-time
    sequence."""
    if extractor not in MACKEY_GLASS_EXTRACTORS:
        raise ValueError(f"unknown extractor: {extractor}")
    raw = MACKEY_GLASS_EXTRACTORS[extractor](x)
    if raw.size < 2:
        return raw
    sp = np.diff(raw)
    sp = sp[sp > 0]
    if sp.size and sp.mean() > 0:
        return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))
    return raw


# ─── Logistic-sweep helper (period-doubling cascade events) ───────────────


def logistic_period_doubling_sweep(
        r_start: float = 2.5, r_end: float = 3.9,
        n_iter: int = 10_000, x0: float = 0.5,
        ) -> np.ndarray:
    """Slow sweep across r, capturing the period-doubling cascade as
    a single trajectory."""
    return logistic_iterate_swept_r(r_start, r_end, x0, n_iter)


# ─── Lorenz system (priority 3, optional) ─────────────────────────────────


def lorenz_integrate(
        rho: float,
        n_steps: int,
        sigma: float = 10.0, beta: float = 8.0 / 3.0,
        dt: float = 0.01,
        x0: tuple = (1.0, 1.0, 1.0),
        discard: int = 5000,
        ) -> np.ndarray:
    """RK4 integration of the Lorenz system.  Returns (n_steps, 3)
    trajectory."""
    x, y, z = x0
    out = np.empty((n_steps + discard, 3), dtype=np.float64)
    for i in range(n_steps + discard):
        # RK4
        def f(state):
            x, y, z = state
            return np.array([sigma * (y - x),
                              x * (rho - z) - y,
                              x * y - beta * z])
        s = np.array([x, y, z])
        k1 = f(s)
        k2 = f(s + 0.5 * dt * k1)
        k3 = f(s + 0.5 * dt * k2)
        k4 = f(s + dt * k3)
        s = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        x, y, z = s
        out[i] = [x, y, z]
    return out[discard:]


def lorenz_lobe_transition_events(traj: np.ndarray) -> np.ndarray:
    """Events at lobe-transition crossings: x changes sign (the
    butterfly attractor's two wings are at x>0 and x<0).  Returns
    unit-mean event-time sequence."""
    x = traj[:, 0]
    above = x > 0
    transitions = np.diff(above.astype(np.int8))
    crossings = np.where(transitions != 0)[0]
    if crossings.size < 2:
        return np.zeros(0)
    sp = np.diff(crossings).astype(np.float64)
    sp = sp[sp > 0]
    if sp.size and sp.mean() > 0:
        return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))
    return crossings.astype(np.float64)


__all__ = [
    'logistic_iterate', 'logistic_iterate_swept_r',
    'logistic_iterate_round_trip', 'logistic_to_events',
    'LOGISTIC_REGIMES',
    'mackey_glass', 'mackey_glass_to_events',
    'MACKEY_GLASS_EXTRACTORS', 'MACKEY_GLASS_REGIMES',
    'logistic_period_doubling_sweep',
    'lorenz_integrate', 'lorenz_lobe_transition_events',
]
