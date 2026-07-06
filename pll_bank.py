"""
Farey PLL bank — second-order phase-locked loops, one per rational ratio.

The bank tracks instantaneous phase of components in the input signal at a
list of natural frequencies (f_carrier · p/q for each Farey rational p/q).
A PLL at frequency f_pll locks when the signal contains a component near
f_pll with sufficient power; it slips otherwise.  The lock/slip time series
is the per-PLL intermittency record we hand off to the universality
analyzer.

Per-PLL computation (matches the GPU kernel layout in CRITICALITY_BRIEF.md
§Module 1):

    1.  Quadrature mix the signal with a local oscillator at f_pll:
          I[n] = x[n] · cos(2π·f_pll·n/sr)
          Q[n] = x[n] · -sin(2π·f_pll·n/sr)
    2.  IIR low-pass I, Q at cutoff f_pll · 0.05 to isolate the narrowband
        component near f_pll.
    3.  Instantaneous BASEBAND phase of the narrowband signal (the carrier
        at f_pll has already been removed by mixing):
          φ_sig[n] = atan2(Q_lp[n], I_lp[n])
    4.  Second-order PLL on the BASEBAND phase.  φ_osc tracks the deviation
        from f_pll, not the full oscillator phase, since mixing has already
        de-rotated by f_pll:
          e   = sin(φ_sig - φ_osc)
          v   = ρ·v + K_i·e
          dφ  = K_p·e + v
          φ_osc += dφ
    5.  Lock when |e| < θ_lock continuously for N_lock samples.

Note on the formulation: the original spec in CRITICALITY_BRIEF.md adds
2π·f_pll/sr to φ_osc each sample, but that mixes frames — φ_sig is at
baseband after quadrature mixing, so φ_osc must also live at baseband.
The deviation-tracking form here lets the integrator absorb any frequency
detune (steady-state v ≈ 2π·Δf/sr), and the loop gains K_p / K_i become
independent of f_pll.

Quadrature mixing + IIR LP is the GPU-friendly alternative to a per-PLL
FFT-Hilbert (which would dominate runtime); on CPU the same approach keeps
parity with the GPU kernel for verification.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.signal import lfilter

# ── Backend detection ─────────────────────────────────────────────────────────
GPU_AVAILABLE = False
GPU_NAME = None
try:
    import cupy as cp
    GPU_AVAILABLE = True
    GPU_NAME = cp.cuda.runtime.getDeviceProperties(0)['name'].decode()
except Exception:
    cp = None


# ── PLL parameters ────────────────────────────────────────────────────────────
@dataclass
class PLLParams:
    """Per-bank parameters.  Defaults follow CRITICALITY_BRIEF.md §1 guidelines."""
    K_p:     float = 0.10               # proportional gain
    K_i:     float = 0.005              # integral gain
    rho:     float = 0.95               # loop-filter pole
    theta_lock_rad: float = math.pi / 6 # 30° phase-error threshold
    lock_confirm_ms: float = 20.0       # samples must satisfy threshold this long
    bw_frac: float = 0.05               # IIR LP cutoff = bw_frac · f_pll
    # Lock requires the narrowband power |I_lp|² + |Q_lp|² to exceed
    # power_floor_frac · (input RMS)² .  Prevents detuned-but-phase-coherent
    # residuals from spuriously triggering lock.  Math: an amplitude-A tone
    # at f_pll has |I|² + |Q|² → A²/4 ; signal RMS² = A²/2 ; so an FM Bessel
    # sideband of amplitude A·|J_n| has narrowband_power / RMS² = |J_n|²/2.
    #     0.03 admits |J_n| ≥ 0.245  (J_3 at β=3 ≈ 0.31  ✓; J_4 at β=3 ≈ 0.13 ✗)
    #     0.01 admits |J_n| ≥ 0.141  (J_4 at β=3 just makes it; lets in a
    #                                  30%-detuned residual at ~1.4% of RMS²)
    power_floor_frac: float = 0.03


# ── Single CPU PLL ────────────────────────────────────────────────────────────
def single_pll_cpu(
    signal: np.ndarray,
    f_pll:  float,
    sr:     float,
    params: Optional[PLLParams] = None,
    state:  Optional[dict] = None,
    signal_rms: Optional[float] = None,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Run one PLL over `signal`.  Returns (lock_map, phase_error, end_state).

      lock_map      uint8 [len(signal)]  — 1 if locked at sample n, else 0
      phase_error   float32 [len(signal)] — instantaneous PLL phase error
      end_state     dict — final {phi_osc, v, I_lp, Q_lp, narrowband_power}
                          for chunk continuation

    `state` lets callers chain PLL invocations across chunks (zero-init if None).
    `signal_rms` may be passed when the input signal RMS is computed once at
    the bank level (saves recomputation per PLL); otherwise it's measured
    here on the full chunk.
    """
    if params is None:
        params = PLLParams()

    x = np.asarray(signal, dtype=np.float64)
    N = x.shape[0]
    if signal_rms is None:
        signal_rms = float(np.sqrt(np.mean(x * x))) if N > 0 else 0.0
    power_floor = params.power_floor_frac * (signal_rms * signal_rms)

    # Persistent state across chunks
    if state is None:
        phi_osc = 0.0
        v       = 0.0
        I_lp    = 0.0
        Q_lp    = 0.0
        sample_offset = 0
    else:
        phi_osc = float(state['phi_osc'])
        v       = float(state['v'])
        I_lp    = float(state['I_lp'])
        Q_lp    = float(state['Q_lp'])
        sample_offset = int(state.get('sample_offset', 0))

    # IIR LP coefficient.  Continuous-time pole at f_pll · bw_frac.
    fc_lp = max(f_pll * params.bw_frac, 1.0)
    alpha = 1.0 - math.exp(-2.0 * math.pi * fc_lp / sr)

    omega_pll = 2.0 * math.pi * f_pll / sr
    K_p   = params.K_p
    K_i   = params.K_i
    rho   = params.rho
    theta = params.theta_lock_rad
    N_lock = max(1, int(round(sr * params.lock_confirm_ms * 0.001)))

    lock_map    = np.zeros(N, dtype=np.uint8)
    phase_error = np.zeros(N, dtype=np.float32)

    # Per-sample loop.  Tight Python loop; numba could speed this up later.
    consec_in_threshold = 0
    for n in range(N):
        # Quadrature mix.  Reference oscillator phase = ω_pll · (sample_offset + n).
        # Wrap to keep numerical precision; the cos/sin functions handle modulo.
        phi_ref = omega_pll * (sample_offset + n)
        I = x[n] * math.cos(phi_ref)
        Q = x[n] * -math.sin(phi_ref)

        # 1-pole IIR LP on I, Q.
        I_lp = (1.0 - alpha) * I_lp + alpha * I
        Q_lp = (1.0 - alpha) * Q_lp + alpha * Q

        # Narrowband instantaneous phase.
        phi_sig = math.atan2(Q_lp, I_lp)

        # PLL update.  φ_osc tracks the BASEBAND deviation; mixing has already
        # de-rotated by f_pll, so we don't add ω_pll back here.
        e    = math.sin(phi_sig - phi_osc)
        v    = rho * v + K_i * e
        dphi = K_p * e + v
        phi_osc += dphi

        phase_error[n] = e

        # Lock detection: phase coherence AND narrowband power above floor,
        # sustained for N_lock samples.
        narrowband_power = I_lp * I_lp + Q_lp * Q_lp
        if abs(e) < theta and narrowband_power >= power_floor:
            consec_in_threshold += 1
        else:
            consec_in_threshold = 0
        lock_map[n] = 1 if consec_in_threshold >= N_lock else 0

    end_state = {
        'phi_osc': phi_osc,
        'v':       v,
        'I_lp':    I_lp,
        'Q_lp':    Q_lp,
        'sample_offset': sample_offset + N,
    }
    return lock_map, phase_error, end_state


# ── CPU bank (joblib over PLLs) ───────────────────────────────────────────────
def pll_bank_cpu(
    signal: np.ndarray,
    f_plls: np.ndarray,
    sr:     float,
    params: Optional[PLLParams] = None,
    n_jobs: int = -1,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run a bank of PLLs in parallel (joblib over CPU cores).
    Returns (lock_map[N_pll × N], phase_error[N_pll × N]).
    """
    if params is None:
        params = PLLParams()
    f_plls = np.asarray(f_plls, dtype=np.float64)
    x = np.asarray(signal, dtype=np.float64)
    rms = float(np.sqrt(np.mean(x * x))) if len(x) > 0 else 0.0

    try:
        from joblib import Parallel, delayed
    except ImportError:
        Parallel = None

    def run_one(f_pll):
        return single_pll_cpu(x, float(f_pll), sr, params, signal_rms=rms)[:2]

    if Parallel is not None and n_jobs != 1:
        results = Parallel(n_jobs=n_jobs, prefer='threads')(
            delayed(run_one)(f) for f in f_plls)
    else:
        results = [run_one(f) for f in f_plls]

    lock_map    = np.stack([r[0] for r in results], axis=0)
    phase_error = np.stack([r[1] for r in results], axis=0)
    return lock_map, phase_error


# ── GPU kernel (CuPy) ─────────────────────────────────────────────────────────
#
# Layout: one CUDA thread per PLL; each thread iterates over all samples
# sequentially.  The PLL recurrence is inherently sequential per-sample, so
# parallelism comes from running many PLLs concurrently — not from splitting
# one PLL across threads.  (The brief's per-sample-thread layout in §1 is
# inconsistent with the per-sample state dependency; this is the corrected
# design.)
#
# Per-thread state held in registers: phi_osc, v, I_lp, Q_lp, consec_count.
# Output arrays: lock_map[N_pll × N] uint8, phase_error[N_pll × N] float32.
#
_PLL_KERNEL_SRC = r"""
extern "C" __global__
void pll_bank(
    const float* __restrict__ signal, const int N,
    const float* __restrict__ f_plls,  const int N_pll,
    const float sr,
    const float K_p, const float K_i, const float rho,
    const float theta_lock, const int N_lock,
    const float bw_frac,
    const float power_floor,
    const int    write_phase_error,              // 0 → skip phase_error writes
    unsigned char* __restrict__ lock_map,        // [N_pll × N]
    float*         __restrict__ phase_error)     // [N_pll × N] — may be unused
{
    const int p = blockIdx.x * blockDim.x + threadIdx.x;
    if (p >= N_pll) return;

    const float PI2 = 6.28318530718f;
    const float f_pll     = f_plls[p];
    const float omega_pll = PI2 * f_pll / sr;
    const float fc_lp     = (f_pll * bw_frac > 1.f) ? (f_pll * bw_frac) : 1.f;
    const float alpha     = 1.f - expf(-PI2 * fc_lp / sr);

    float phi_osc = 0.f;
    float v       = 0.f;
    float I_lp    = 0.f;
    float Q_lp    = 0.f;
    int   consec  = 0;

    const long row = (long)p * (long)N;

    for (int n = 0; n < N; n++){
        // Quadrature mix.
        const float phi_ref = omega_pll * (float)n;
        const float c       = cosf(phi_ref);
        const float s       = sinf(phi_ref);
        const float x       = signal[n];
        const float I       =  x * c;
        const float Q       = -x * s;

        // 1-pole IIR LP.
        I_lp = (1.f - alpha) * I_lp + alpha * I;
        Q_lp = (1.f - alpha) * Q_lp + alpha * Q;

        // Narrowband baseband phase.
        const float phi_sig = atan2f(Q_lp, I_lp);

        // PLL update on baseband (no ω_pll term — mixing already removed it).
        const float e    = sinf(phi_sig - phi_osc);
        v                = rho * v + K_i * e;
        const float dphi = K_p * e + v;
        phi_osc         += dphi;

        if (write_phase_error) phase_error[row + n] = e;

        // Lock detection: phase coherence AND narrowband power above floor,
        // sustained for N_lock samples.
        const float p_nb = I_lp * I_lp + Q_lp * Q_lp;
        if (fabsf(e) < theta_lock && p_nb >= power_floor) {
            consec += 1;
        } else {
            consec = 0;
        }
        lock_map[row + n] = (consec >= N_lock) ? 1 : 0;
    }
}
"""

_pll_compiled = None

def pll_bank_gpu(
    signal: np.ndarray,
    f_plls: np.ndarray,
    sr:     float,
    params: Optional[PLLParams] = None,
    return_phase_error: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Run a bank of PLLs on the GPU.  Returns (lock_map[N_pll × N], phase_error).
    Falls back to pll_bank_cpu if CuPy or kernel compilation fails.

    With return_phase_error=False, the kernel skips per-sample phase_error
    writes (saving 4 bytes/sample/PLL) and the returned phase_error is an
    empty array.  Use this for sweeps where only the lock_map is consumed
    downstream — it cuts GPU memory by ~5×.
    """
    global _pll_compiled
    if not GPU_AVAILABLE:
        # CPU fallback always returns full phase error.
        return pll_bank_cpu(signal, f_plls, sr, params)
    if params is None:
        params = PLLParams()

    if _pll_compiled is None:
        try:
            _pll_compiled = cp.RawKernel(_PLL_KERNEL_SRC, 'pll_bank')
        except Exception:
            return pll_bank_cpu(signal, f_plls, sr, params)

    f_plls = np.asarray(f_plls, dtype=np.float32)
    x      = np.asarray(signal, dtype=np.float32)
    N      = int(x.shape[0])
    N_pll  = int(f_plls.shape[0])
    rms    = float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) if N > 0 else 0.0

    sig_g     = cp.asarray(x)
    f_plls_g  = cp.asarray(f_plls)
    lock_g    = cp.zeros((N_pll, N), dtype=cp.uint8)
    if return_phase_error:
        err_g = cp.zeros((N_pll, N), dtype=cp.float32)
    else:
        # Tiny dummy buffer; the kernel won't write to it (write_phase_error=0).
        err_g = cp.zeros(1, dtype=cp.float32)

    threads_per_block = 32
    blocks = (N_pll + threads_per_block - 1) // threads_per_block

    n_lock = max(1, int(round(sr * params.lock_confirm_ms * 0.001)))
    power_floor = params.power_floor_frac * (rms * rms)

    _pll_compiled(
        (blocks,), (threads_per_block,),
        (sig_g, np.int32(N),
         f_plls_g, np.int32(N_pll),
         np.float32(sr),
         np.float32(params.K_p), np.float32(params.K_i), np.float32(params.rho),
         np.float32(params.theta_lock_rad), np.int32(n_lock),
         np.float32(params.bw_frac),
         np.float32(power_floor),
         np.int32(1 if return_phase_error else 0),
         lock_g, err_g),
    )
    cp.cuda.Device(0).synchronize()
    if return_phase_error:
        return cp.asnumpy(lock_g), cp.asnumpy(err_g)
    return cp.asnumpy(lock_g), np.zeros(0, dtype=np.float32)


# ── Farey rationals ───────────────────────────────────────────────────────────
def farey_rationals(q_max: int) -> list[tuple[int, int]]:
    """
    Return all p/q in lowest terms with q ≤ q_max, in the range [1/q_max, q_max].
    Includes both sub- and super-unison ratios.

    Built from the Farey sequence F_{q_max} (fractions in [0,1] in reduced form),
    augmented with their reciprocals (excluding 0/1 and including 1/1 once).
    """
    from math import gcd
    sub = []   # p/q with p ≤ q  (in (0, 1])
    for q in range(1, q_max + 1):
        for p in range(1, q + 1):
            if gcd(p, q) == 1:
                sub.append((p, q))
    # Reciprocals, excluding 1/1 to avoid duplicate.
    sup = [(q, p) for (p, q) in sub if p != q]
    pairs = sub + sup
    # Filter to range [1/q_max, q_max].
    pairs = [(p, q) for (p, q) in pairs
             if (1.0 / q_max) <= (p / q) <= q_max]
    # Sort by ratio for predictable ordering.
    pairs.sort(key=lambda pq: pq[0] / pq[1])
    return pairs
