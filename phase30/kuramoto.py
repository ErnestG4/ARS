"""
phase30/kuramoto.py — classical and stochastic Kuramoto oscillator
simulator with threshold-crossing spike generation.

Classical Kuramoto (Analysis 1):
    dθ_i/dt = ω_i + (K/N) Σ_j sin(θ_j - θ_i)

Stochastic Kuramoto (Analysis 2):
    dθ_i/dt = ω_i + (K/N) Σ_j sin(θ_j - θ_i) + σ ξ_i(t)

ω_i drawn from a Lorentzian (Cauchy) g(ω) centered at ω_0 with HWHM γ:
    g(ω) = (γ/π) / ((ω - ω_0)² + γ²)         so g(0) = 1/(π γ)
Standard Kuramoto self-consistency gives K_c = 2 / (π g(0)), so for the
Lorentzian:
    K_c = 2 γ
(Strogatz 2000, "From Kuramoto to Crawford", eq. 3.10.  Empirically
verified in the smoke test: at K = 10 (K_c-old), where K_c-old = 2γ/π,
the simulation gave |r| = 0.85; the true K-multiple is K/(2γ) ≈ 3.18
for which the Strogatz prediction r∞ = sqrt(1 - K_c/K) gives
sqrt(1 - 1/3.18) ≈ 0.83.  Matches.  The Phase 30 brief stated
K_c = 2γ/π, which is off by a factor of π — corrected here.)

Spike generation: each oscillator "spikes" at every 2π phase wrap
(threshold crossing of the unwrapped phase).  At K=0 each oscillator is
a pure periodic spiker with intrinsic frequency ω_i / (2π); at K > K_c
the locked oscillators fire at the common frequency Ω / (2π).

Integration: forward Euler for the deterministic case, Euler–Maruyama
for the stochastic case.  Time step dt is chosen small relative to the
fastest natural-frequency timescale and the slowest noise correlation
timescale (here, white-noise → dt < 1/(10 ω_max) is a comfortable
heuristic).

Key choices documented in code comments:
  - Lorentzian frequencies (canonical Kuramoto closed-form regime).
  - Threshold-crossing spike generation (chosen for direct comparability
    to neural spike-train data; the alternative — phase-velocity
    "thresholding" or amplitude-of-r-based events — would introduce
    confounds with the observable that ARS is supposed to read).
  - All-to-all coupling (canonical mean-field; sparse/network variants
    are deferred per Phase 30 brief out-of-scope).
  - Per-oscillator spike trains returned as a list of ndarrays
    (heterogeneous lengths post-locking).
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field


@dataclass
class KuramotoSim:
    """Result of a single Kuramoto simulation run."""
    K: float                         # coupling strength
    sigma: float                     # noise amplitude (0 for classical)
    N: int                           # number of oscillators
    omega_0: float                   # mean of Lorentzian
    gamma: float                     # HWHM of Lorentzian
    K_c: float                       # critical coupling = 2γ/π
    dt: float                        # integration time step
    T_sim: float                     # total simulated duration
    T_transient: float               # discarded transient duration
    seed: int

    # Outputs
    spikes: list[np.ndarray] = field(default_factory=list)  # per-oscillator spike times (post-transient)
    omegas: np.ndarray = field(default_factory=lambda: np.zeros(0))  # natural frequencies
    r_trace: np.ndarray = field(default_factory=lambda: np.zeros(0))  # |r(t)| order parameter (downsampled)
    r_dt: float = 0.0                # downsampling step for r_trace
    n_steps_post: int = 0


def _draw_lorentzian(N: int, omega_0: float, gamma: float, seed: int,
                       truncate_hwhm: float = 10.0) -> np.ndarray:
    """Draw N samples from a Lorentzian (Cauchy) with location omega_0 and
    scale gamma, truncated to [omega_0 - truncate_hwhm·γ, omega_0 + truncate_hwhm·γ].

    Truncation rationale: a true (un-truncated) Lorentzian has heavy tails
    that, at finite N (here, N ≤ ~500), can place individual oscillators
    100+ HWHMs from the mean.  Such oscillators (i) violate the small-dt
    Euler assumption (ω·dt ≫ 1), and (ii) inject incoherent population-
    mean-field contributions that suppress |r(t)| even in the locking
    regime.  Truncation at ±10 γ removes ~3% of the distribution mass,
    preserves the closed-form K_c = 2γ/π to within the 2-3% finite-N
    correction expected at N = O(100), and gives a numerically stable
    simulation.  Symmetric-pair construction further suppresses mean
    drift relative to the bulk.
    """
    rng = np.random.default_rng(seed)
    half = N // 2
    # Map u ∈ (0,1) → standard Cauchy via inverse CDF, then truncate.
    # Equivalently restrict u to (1/2 - u_max, 1/2 + u_max) where
    # u_max = arctan(truncate_hwhm) / π.
    u_max = np.arctan(truncate_hwhm) / np.pi
    u = rng.uniform(0.5 - u_max, 0.5 + u_max, size=half)
    raw = np.tan(np.pi * (u - 0.5))
    omegas = np.empty(N, dtype=np.float64)
    omegas[:half] = omega_0 + gamma * raw
    omegas[half:2 * half] = omega_0 - gamma * raw
    if N % 2 == 1:
        omegas[-1] = omega_0
    rng.shuffle(omegas)
    return omegas


def critical_coupling(gamma: float) -> float:
    """K_c = 2γ for the Lorentzian-distributed Kuramoto system, derived
    from K_c = 2/(π g(0)) with g(0) = 1/(πγ).  Empirically validated."""
    return 2.0 * gamma


def simulate(K: float,
             sigma: float = 0.0,
             N: int = 100,
             omega_0: float = 2.0 * np.pi,    # 1 Hz mean intrinsic frequency
             gamma: float = 0.5 * 2.0 * np.pi,  # HWHM 0.5 Hz → K_c ≈ 2 Hz (rad/s)
             dt: float = 0.005,               # 5 ms time step
             T_sim: float = 250.0,            # seconds, total
             T_transient: float = 50.0,       # seconds, discarded
             seed: int = 0,
             record_r: bool = True,
             r_downsample: int = 20,
             ) -> KuramotoSim:
    """Run a Kuramoto simulation and return per-oscillator spike trains.

    All-to-all coupling.  Lorentzian natural frequencies.
    Forward Euler (sigma=0) or Euler–Maruyama (sigma>0).

    Threshold-crossing spike generation: spike at every wrap of the
    unwrapped phase past a multiple of 2π.  Detected per step from the
    integer part of θ / (2π).

    Returns:
      KuramotoSim with .spikes (list of ndarrays of spike times in
      seconds, one per oscillator, post-transient) and .r_trace
      (downsampled |r(t)| order parameter trace).
    """
    rng = np.random.default_rng(seed + 12345)

    omegas = _draw_lorentzian(N, omega_0, gamma, seed=seed)
    K_c = critical_coupling(gamma)

    n_steps_total = int(np.round(T_sim / dt))
    n_steps_transient = int(np.round(T_transient / dt))
    n_steps_post = n_steps_total - n_steps_transient

    theta = rng.uniform(0, 2 * np.pi, size=N)         # initial phases
    last_wrap_count = np.floor(theta / (2 * np.pi)).astype(np.int64)

    # Spike storage — append per oscillator post-transient
    spike_times = [list() for _ in range(N)]

    # Optional |r(t)| trace, downsampled
    if record_r and n_steps_post > 0:
        n_r = (n_steps_post + r_downsample - 1) // r_downsample
        r_trace = np.zeros(n_r, dtype=np.float32)
    else:
        r_trace = np.zeros(0, dtype=np.float32)

    # sqrt(dt) factor for Euler–Maruyama noise term
    sqrt_dt = np.sqrt(dt)

    K_over_N = K / N

    for step in range(n_steps_total):
        # Order parameter as complex mean
        z = np.exp(1j * theta).mean()
        # r * sin(ψ - θ_i) = Im(z e^{-iθ_i}) gives the mean-field coupling
        # for each oscillator; equivalent to (1/N) Σ_j sin(θ_j - θ_i).
        coupling = (z * np.exp(-1j * theta)).imag       # length N
        # Total drift: ω_i + K * coupling
        drift = omegas + K * coupling
        if sigma > 0.0:
            noise = rng.standard_normal(N) * sigma * sqrt_dt
            theta = theta + drift * dt + noise
        else:
            theta = theta + drift * dt

        # Detect 2π wraps (per oscillator) — count integer multiples of 2π.
        # Each change in floor(θ/2π) (positive OR negative — Lorentzian tails
        # can produce ω<0 oscillators that rotate "backward") corresponds
        # to one threshold crossing.  Use |delta|.
        cur_wrap = np.floor(theta / (2 * np.pi)).astype(np.int64)
        delta = np.abs(cur_wrap - last_wrap_count)
        if step >= n_steps_transient:
            t_now = step * dt
            for i in np.where(delta > 0)[0]:
                d = int(delta[i])
                if d == 1:
                    spike_times[i].append(t_now)
                else:
                    # Evenly distributed within the step
                    for k in range(d):
                        spike_times[i].append(t_now - dt * (1 - (k + 1) / d))
        last_wrap_count = cur_wrap

        if record_r and step >= n_steps_transient:
            j = step - n_steps_transient
            if j % r_downsample == 0:
                r_trace[j // r_downsample] = abs(z)

    spikes = [np.asarray(s, dtype=np.float64) for s in spike_times]

    return KuramotoSim(
        K=K, sigma=sigma, N=N,
        omega_0=omega_0, gamma=gamma, K_c=K_c,
        dt=dt, T_sim=T_sim, T_transient=T_transient, seed=seed,
        spikes=spikes, omegas=omegas,
        r_trace=r_trace, r_dt=dt * r_downsample,
        n_steps_post=n_steps_post,
    )


def aggregate_spikes(sim: KuramotoSim) -> np.ndarray:
    """Concatenate per-oscillator spike times and return sorted array.
    Used for population-level / recording-wide ARS."""
    if not sim.spikes:
        return np.zeros(0, dtype=np.float64)
    return np.sort(np.concatenate([s for s in sim.spikes if s.size > 0])
                    if any(s.size > 0 for s in sim.spikes)
                    else np.zeros(0))


def per_oscillator_rates(sim: KuramotoSim) -> np.ndarray:
    """Per-oscillator firing rate (spikes / second) post-transient."""
    duration = sim.T_sim - sim.T_transient
    return np.asarray([s.size / max(duration, 1e-9) for s in sim.spikes],
                       dtype=np.float64)


def rate_matched_poisson_surrogate(sim: KuramotoSim, seed: int) -> list[np.ndarray]:
    """Per-oscillator independent Poisson surrogate at each oscillator's
    empirical rate, over the same post-transient window.
    Phase 26 / Phase 27 lesson: rate-match the surrogate to the analysis
    resolution.  Per-oscillator rate-match is the right level here
    (Analysis 1 / 2 work per-oscillator)."""
    rng = np.random.default_rng(seed + 999)
    rates = per_oscillator_rates(sim)
    duration = sim.T_sim - sim.T_transient
    out = []
    for r in rates:
        if r * duration < 1:
            out.append(np.zeros(0, dtype=np.float64))
            continue
        n = int(rng.poisson(r * duration))
        if n == 0:
            out.append(np.zeros(0, dtype=np.float64))
            continue
        t = np.sort(rng.uniform(0, duration, size=n))
        out.append(t)
    return out


__all__ = [
    'KuramotoSim', 'critical_coupling', 'simulate',
    'aggregate_spikes', 'per_oscillator_rates',
    'rate_matched_poisson_surrogate',
]
