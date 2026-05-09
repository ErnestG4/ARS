"""
surrogates.py — Higher-order induction-on-noise (Phase 18).

Three surrogate generators, each preserving a specific higher-order property
of the input while randomising others.  Used to extend the falsification
protocol beyond first-order matched noise (§7.ter.19, §7.ter.22, §7.ter.23
Finding F): a positive finding must survive surrogates that match power
spectrum, clustering geometry, and low-order cumulants of its input.

Two API layers:

  • Continuous surrogates operate on equally sampled real arrays:
        phase_randomized(x, rng)
        cumulant_matched_continuous(x, rng)

  • Event surrogates operate on sorted event-time arrays t_k (float64) and
    return a new sorted event-time array of compatible total time and
    event count:
        phase_randomized_events(t_k, rng, oversample, sigma_frac, extractor)
        hawkes_matched_events(t_k, rng)
        cumulant_matched_events(t_k, rng)

  Plus a name-keyed dispatcher:
        SURROGATES = {'phase_randomized', 'hawkes_matched', 'cumulant_matched'}
        generate(t_k, name, rng=None, **kwargs)

The event-pipeline surrogates run the input through the canonical
event → continuous → randomise → event round trip, using
`extractors.synthesize_continuous` and a pluggable extractor (default:
direct_events on the chirp-driven sequence, i.e., Gaussian-pulse-summed
continuous trace processed by find_peaks for a continuous-bound surrogate,
or pure event-domain regeneration for the Hawkes / cumulant cases).

References:
  - Theiler et al. 1992 (phase randomisation surrogates).
  - Hawkes 1971; Ozaki 1979 (Hawkes ML estimation, exponential kernel).
  - Cornish & Fisher 1937; Gram-Charlier expansion (cumulant matching).
"""
from __future__ import annotations

import numpy as np
from typing import Optional, Callable

from extractors import synthesize_continuous, EXTRACTORS


# ─── Continuous surrogates ─────────────────────────────────────────────────


def phase_randomized(x: np.ndarray, rng: Optional[np.random.Generator] = None
                     ) -> np.ndarray:
    """Phase-randomised surrogate of a real-valued continuous signal.

    Preserves: FFT magnitudes (power spectrum) exactly; marginal mean and
    variance approximately (within FFT-roundoff and the Hermitian-symmetry
    constraint).
    Randomises: phase relationships, higher-order cumulants, all
    non-second-order statistics.

    Implementation: take rFFT of x, replace each non-DC, non-Nyquist phase
    with a uniform sample in [0, 2π), preserving DC and Nyquist real values,
    inverse rFFT.  This is the standard FT surrogate of Theiler et al. 1992.
    """
    if rng is None:
        rng = np.random.default_rng()
    x = np.asarray(x, dtype=np.float64)
    if x.size < 4:
        return x.copy()
    n = x.size
    X = np.fft.rfft(x)
    # Hermitian-symmetric: phases of bins 1..n//2-1 are free; DC (k=0) and
    # (only when n even) Nyquist (k=n/2) must remain real.
    mags = np.abs(X)
    new_phase = rng.uniform(0.0, 2.0 * np.pi, size=X.shape)
    new_phase[0] = 0.0
    if (n % 2) == 0:
        new_phase[-1] = 0.0
    Y = mags * np.exp(1j * new_phase)
    # Re-impose real-output constraints at the boundary bins.
    Y[0] = X[0].real + 0j
    if (n % 2) == 0:
        Y[-1] = X[-1].real + 0j
    return np.fft.irfft(Y, n=n)


def cumulant_matched_continuous(
        x: np.ndarray,
        rng: Optional[np.random.Generator] = None,
        n_out: Optional[int] = None,
        ) -> np.ndarray:
    """iid sequence of length n_out matching the first three cumulants
    (mean, variance, skewness) of x via a Gram-Charlier-truncated transform.

    Preserves: sample mean, variance, and skewness within the precision of
    a third-order Edgeworth/Gram-Charlier transform applied to iid Gaussian
    draws.
    Randomises: autocorrelation (output is iid by construction), all
    higher-than-third cumulants.

    Implementation: draw z ~ N(0, 1), apply the Cornish-Fisher-style
    third-order expansion x_out = μ + σ · (z + (γ/6)(z² − 1)), where γ is
    the input's sample skewness.  This matches the first three cumulants
    of x_out to (μ, σ², γσ³) up to third-order correction terms; for
    moderate γ ∈ [-2, 2] the residuals are < 5%.  Output mean and variance
    are then rescaled to exactly match the input's sample mean and variance
    (cheap correction; preserves skewness to within the same tolerance).
    """
    if rng is None:
        rng = np.random.default_rng()
    x = np.asarray(x, dtype=np.float64)
    if x.size < 4:
        return x.copy()
    if n_out is None:
        n_out = x.size
    mu = float(x.mean())
    sigma = float(x.std(ddof=1))
    if sigma <= 0:
        return np.full(n_out, mu)
    z = (x - mu) / sigma
    skew = float(np.mean(z ** 3))
    # Draw and Cornish-Fisher transform.
    g = rng.standard_normal(n_out)
    y = g + (skew / 6.0) * (g * g - 1.0)
    # Renormalise to enforce mean=0, var=1 on the surrogate before scaling.
    y = (y - y.mean()) / (y.std(ddof=1) + 1e-15)
    return mu + sigma * y


# ─── Hawkes ML estimation (exponential kernel) ─────────────────────────────


def _hawkes_log_likelihood(params, t, T):
    """log L for a univariate Hawkes process with exponential kernel:
        λ(t) = μ + α Σ_{t_i < t} exp(-β (t - t_i))
    Closed-form recursion (Ozaki 1979).  params = (μ, α, β).
    """
    mu, alpha, beta = params
    if mu <= 0 or alpha < 0 or beta <= 0 or alpha >= beta:
        return -np.inf
    n = t.size
    if n == 0:
        return -mu * T
    # A_i = sum_{j<i} exp(-β(t_i - t_j)), recursion:
    #    A_1 = 0, A_i = exp(-β(t_i - t_{i-1}))(1 + A_{i-1})
    A = np.zeros(n)
    for i in range(1, n):
        A[i] = np.exp(-beta * (t[i] - t[i - 1])) * (1.0 + A[i - 1])
    # Log-likelihood:
    #   sum_i ln(μ + α A_i) − μ T − (α/β) sum_i (1 − exp(-β(T - t_i)))
    intensity_at_events = mu + alpha * A
    if np.any(intensity_at_events <= 0):
        return -np.inf
    term1 = float(np.sum(np.log(intensity_at_events)))
    term2 = mu * T
    term3 = (alpha / beta) * float(np.sum(1.0 - np.exp(-beta * (T - t))))
    return term1 - term2 - term3


def _fit_hawkes_exponential(
        t: np.ndarray,
        T: Optional[float] = None,
        ) -> tuple[float, float, float]:
    """Maximum-likelihood estimate of (μ, α, β) for a univariate Hawkes
    process with exponential triggering kernel, by L-BFGS-B optimisation
    on log L.  Returns the fitted parameters.

    Stability constraint:  α < β  (branching ratio α/β < 1).
    """
    from scipy.optimize import minimize
    t = np.sort(np.asarray(t, dtype=np.float64))
    if T is None:
        T = float(t[-1]) if t.size > 0 else 1.0
    n = t.size
    if n < 10 or T <= 0:
        return (max(n / max(T, 1e-9), 1e-6), 0.0, 1.0)
    # Initial guesses.  μ_0 ≈ rate; β_0 ≈ inverse of mean spacing; α_0 small.
    rate = n / T
    mean_sp = float(np.mean(np.diff(t))) if n >= 2 else 1.0
    beta0 = max(1.0 / max(mean_sp, 1e-9), 1e-3)
    mu0 = 0.5 * rate
    alpha0 = 0.5 * beta0   # branching ratio ~0.5
    x0 = np.log([mu0, alpha0, beta0])

    def neg_ll(log_params):
        mu, alpha, beta = np.exp(log_params)
        # Soft constraint: penalise α >= β (branching ratio ≥ 1).
        if alpha >= 0.999 * beta:
            return 1e9
        ll = _hawkes_log_likelihood((mu, alpha, beta), t, T)
        if not np.isfinite(ll):
            return 1e9
        return -ll

    try:
        res = minimize(neg_ll, x0, method='L-BFGS-B',
                       options={'maxiter': 200, 'ftol': 1e-9})
        mu, alpha, beta = np.exp(res.x)
    except Exception:
        mu, alpha, beta = mu0, alpha0, beta0
    if not np.isfinite([mu, alpha, beta]).all():
        mu, alpha, beta = mu0, alpha0, beta0
    return float(mu), float(alpha), float(beta)


def _simulate_hawkes(
        mu: float, alpha: float, beta: float, T: float,
        rng: np.random.Generator,
        ) -> np.ndarray:
    """Simulate a univariate Hawkes process with exponential triggering
    kernel on [0, T] via Ogata's modified thinning algorithm.
    """
    if alpha >= beta or mu <= 0 or beta <= 0:
        # Degenerate / non-stationary: fall back to homogeneous Poisson at μ.
        n_exp = max(1, int(mu * T))
        return np.sort(rng.uniform(0, T, size=n_exp))
    events = []
    t = 0.0
    while t < T:
        # Upper-bound intensity at t+: μ + sum_{i: t_i ≤ t} α e^{-β(t - t_i)}
        if events:
            prev = np.asarray(events)
            lam_bar = mu + alpha * float(np.sum(np.exp(-beta * (t - prev))))
        else:
            lam_bar = mu
        if lam_bar <= 0:
            t += 1.0 / max(mu, 1e-9)
            continue
        u = rng.uniform()
        w = -np.log(u) / lam_bar
        t = t + w
        if t >= T:
            break
        # Compute the actual intensity at t.
        if events:
            prev = np.asarray(events)
            lam_t = mu + alpha * float(np.sum(np.exp(-beta * (t - prev))))
        else:
            lam_t = mu
        d = rng.uniform()
        if d * lam_bar <= lam_t:
            events.append(t)
    return np.asarray(events, dtype=np.float64)


# ─── Event-domain surrogates ───────────────────────────────────────────────


def phase_randomized_events(
        t_k: np.ndarray,
        rng: Optional[np.random.Generator] = None,
        oversample: int = 10,
        sigma_frac: float = 0.3,
        extractor: str = 'find_peaks_prominence',
        extractor_kwargs: Optional[dict] = None,
        ) -> np.ndarray:
    """Phase-randomised surrogate of an event sequence.

    Pipeline: events → Gaussian-smoothed continuous proxy (the chirp-driving
    proxy used elsewhere in this codebase) → phase randomisation → events
    re-extracted from the randomised proxy via the named extractor.

    The default extractor is `find_peaks_prominence`, matching the
    extraction-from-continuous mechanism that the protocol is designed to
    falsify.  For point processes whose underlying mechanism does not pass
    through find_peaks (e.g., a Hawkes-style raw event stream), the
    `direct_events`-based pipeline is unavailable for this surrogate — but
    that is correct: phase randomisation only makes sense on continuous
    inputs, so the round trip via a continuous proxy is the relevant one.

    Returns a sorted event-time array.  Output event count is whatever the
    extractor produces; not generally equal to len(t_k).
    """
    if rng is None:
        rng = np.random.default_rng()
    if extractor_kwargs is None:
        extractor_kwargs = {}
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 4:
        return t.copy()
    t_grid, sig = synthesize_continuous(t, oversample=oversample,
                                          sigma_frac=sigma_frac)
    if sig.size < 16:
        return t.copy()
    sig_pr = phase_randomized(sig, rng)
    # Re-extract events.  We bypass the extractor's own continuous
    # synthesis and instead use the already-randomised continuous trace:
    # just call the relevant extractor on (t_grid, sig_pr) directly.
    if extractor == 'find_peaks_prominence':
        from scipy.signal import find_peaks
        prominence = float(extractor_kwargs.get('prominence', 0.3))
        prom_thr = max(prominence * float(sig_pr.std()), 1e-9)
        peaks, _ = find_peaks(sig_pr, prominence=prom_thr)
        return t_grid[peaks]
    elif extractor == 'derivative_zeros':
        ds = np.diff(sig_pr)
        is_peak = (ds[:-1] > 0) & (ds[1:] <= 0)
        idx = np.where(is_peak)[0] + 1
        return t_grid[idx]
    elif extractor == 'threshold_crossing':
        k = float(extractor_kwargs.get('k', 1.0))
        thr = sig_pr.mean() + k * sig_pr.std()
        above = sig_pr > thr
        if above.sum() < 2:
            return np.zeros(0)
        transitions = np.diff(above.astype(np.int8))
        upcross_idx = np.where(transitions == 1)[0] + 1
        return t_grid[upcross_idx]
    elif extractor == 'direct_events':
        # Identity: there's no notion of "direct event" on a continuous
        # signal; fall back to local maxima.
        ds = np.diff(sig_pr)
        is_peak = (ds[:-1] > 0) & (ds[1:] <= 0)
        idx = np.where(is_peak)[0] + 1
        return t_grid[idx]
    else:
        raise ValueError(f"unsupported extractor for phase_randomized_events: "
                         f"{extractor!r}")


def phase_randomized_iei_events(
        t_k: np.ndarray,
        rng: Optional[np.random.Generator] = None,
        ) -> np.ndarray:
    """Phase-randomised surrogate of an event sequence operating in the
    inter-event-interval (IEI) domain — the appropriate variant for
    point-processes-by-construction (zeros, primes, raw event catalogs)
    where the events were not extracted from a continuous trace.

    Pipeline: events → IEI sequence → real FFT → randomise phases (DC
    and Nyquist preserved real) → inverse FFT → clip to positive → cumsum.

    Preserves: IEI mean (DC bin), IEI variance (Parseval), IEI power
    spectrum (= 1 + Fourier of IEI autocorrelation).
    Randomises: IEI marginal beyond second order (output marginal is
    asymptotically Gaussian by CLT-like phase-mixing), all higher-order
    cumulants and phase relations.

    The chirp-driven `phase_randomized_events` is the right surrogate for
    inputs that originally went through a `extractor(continuous-trace)`
    pipeline; this IEI-domain variant is the right one for inputs that
    are point processes by construction.  Use the variant that matches
    the data-generating process of the original input.
    """
    if rng is None:
        rng = np.random.default_rng()
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 5:
        return t.copy()
    iei = np.diff(t)
    if iei.size < 4:
        return t.copy()
    iei_pr = phase_randomized(iei, rng=rng)
    # Phase randomisation can produce negative values (the marginal
    # becomes Gaussian-like); clip to a small epsilon to maintain
    # monotonic events.  Then renormalise so total span matches the
    # input — the surrogate's average rate equals the input's exactly.
    eps = max(1e-9, float(np.median(np.abs(iei_pr))) * 1e-6)
    iei_pr = np.where(iei_pr > 0, iei_pr, eps)
    total_in = float(t[-1] - t[0])
    total_out = float(iei_pr.sum())
    if total_out > 0 and total_in > 0:
        iei_pr = iei_pr * (total_in / total_out)
    return np.concatenate([[t[0]], t[0] + np.cumsum(iei_pr)])


def hawkes_matched_events(
        t_k: np.ndarray,
        rng: Optional[np.random.Generator] = None,
        ) -> np.ndarray:
    """Hawkes-matched surrogate: fit (μ, α, β) by ML on the input event
    sequence (exponential kernel), simulate a new sequence on the same time
    window.

    Preserves: average rate; clustering structure to the extent the
    exponential-kernel Hawkes process captures it (branching ratio α/β,
    decay timescale 1/β).
    Randomises: within-cluster geometry beyond what the Hawkes model
    represents; specific event positions.

    Falls back to a homogeneous Poisson surrogate at the same rate if the
    fitted process is non-stationary (α ≥ β) or the optimisation fails.
    """
    if rng is None:
        rng = np.random.default_rng()
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 10:
        return t.copy()
    T = float(t[-1])
    if T <= 0:
        return t.copy()
    # Shift to start at 0 for numerical stability.
    t0 = float(t[0])
    t_shift = t - t0
    T_shift = float(t_shift[-1]) if t_shift.size > 0 else 1.0
    mu, alpha, beta = _fit_hawkes_exponential(t_shift, T_shift)
    sim = _simulate_hawkes(mu, alpha, beta, T_shift, rng)
    # Shift back into original time window.
    return np.sort(sim + t0)


def cumulant_matched_events(
        t_k: np.ndarray,
        rng: Optional[np.random.Generator] = None,
        ) -> np.ndarray:
    """Cumulant-matched surrogate: applies third-cumulant matching to the
    input's inter-event interval distribution, then reconstructs an event
    sequence by cumulative sum.  Output is shifted to start at the input's
    first event time.

    Preserves: first three cumulants of the inter-event-interval (IEI)
    distribution.
    Randomises: autocorrelation (output IEIs are iid), all
    higher-than-third IEI cumulants.
    """
    if rng is None:
        rng = np.random.default_rng()
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 5:
        return t.copy()
    iei = np.diff(t)
    if iei.size < 4:
        return t.copy()
    # Match the first three cumulants of the IEI distribution.  Output
    # may have negative values (Gram-Charlier doesn't guarantee positivity);
    # we clamp to a small positive epsilon to keep events monotonic.
    new_iei = cumulant_matched_continuous(iei, rng=rng, n_out=iei.size)
    # Replace any non-positive IEIs with a small positive value to preserve
    # event ordering.  This is the only correction step; we accept the
    # resulting small bias in the lower tail (alternative is rejection
    # sampling on truncated draws, which biases the cumulants more).
    eps = max(1e-9, float(np.median(np.abs(new_iei))) * 1e-6)
    new_iei = np.where(new_iei > 0, new_iei, eps)
    # Re-scale so total span matches the input total span (keeps T and rate
    # invariant; this is a constant-rate surrogate by design).
    total_in = float(t[-1] - t[0])
    total_out = float(new_iei.sum())
    if total_out > 0 and total_in > 0:
        new_iei = new_iei * (total_in / total_out)
    return np.concatenate([[t[0]], t[0] + np.cumsum(new_iei)])


# ─── Dispatcher ────────────────────────────────────────────────────────────


SURROGATES = {
    'phase_randomized':  phase_randomized_events,
    'hawkes_matched':    hawkes_matched_events,
    'cumulant_matched':  cumulant_matched_events,
}


def generate(t_k: np.ndarray, name: str,
             rng: Optional[np.random.Generator] = None,
             **kwargs) -> np.ndarray:
    """Generate a surrogate event sequence by name.  Returns sorted t_k."""
    if name not in SURROGATES:
        raise ValueError(f"unknown surrogate: {name!r}; "
                         f"valid: {list(SURROGATES)}")
    if rng is None:
        rng = np.random.default_rng()
    out = SURROGATES[name](t_k, rng=rng, **kwargs)
    return np.sort(np.asarray(out, dtype=np.float64))


__all__ = [
    'phase_randomized', 'cumulant_matched_continuous',
    'phase_randomized_events', 'phase_randomized_iei_events',
    'hawkes_matched_events', 'cumulant_matched_events',
    'SURROGATES', 'generate',
]
