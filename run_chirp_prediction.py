"""
Task 3 — analytical chirp-geometry depth prediction.

For a chirp signal whose components have instantaneous frequency
    f_inst_n(t) = t_n / (t + 1)   (the form used in make_zeta_signal etc.)
the n-th tone passes through a PLL at f_pll at time
    t* = t_n / f_pll - 1
and the local sweep rate at that crossing is
    |df_inst/dt|  =  t_n / (t+1)²  =  f_pll² / t_n.

The PLL's lock tongue at p/q has width Δf_pq, which scales heuristically as
(p+q)^(−2) in the Farey arrangement.  Time spent inside the tongue is
    Δτ_pq,n = Δf_pq / |df_inst/dt|  ∝  (p+q)^(−2) · t_n / f_pll²
where f_pll = fc_ref · p/q.

Two predictions follow:

    A.  Lock-events: tone n produces an event at p/q if Δτ_pq,n exceeds
        the lock-confirmation window N_lock/sr, AND if the crossing time
        t* falls inside the recording.  Count those events; group by
        Stern-Brocot depth.
    B.  Dwell-weighted:  Σ_n Δτ_pq,n  for each (p,q), grouped by depth.
        This is the "expected total locked time" at each depth.

Compare both predictions to the observed depth distribution from
sweep_results.h5 and from gue_calibration_results.pkl.  Differences =
residuals attributable to arithmetic structure.
"""
import os, sys, pickle
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, '$HOME/fmexplorer/riemann_explorer')

from pll_bank import farey_rationals
from intermittency import stern_brocot_depth
import scanner   # for ZETA_ZEROS
import signal_gen


SR  = 44100.0
DUR = 30.0
NZ  = 100

LOCK_CONFIRM_MS  = 20.0    # default PLLParams.lock_confirm_ms
N_LOCK = LOCK_CONFIRM_MS * SR * 0.001

# tongue width prefactor: scales arbitrary, only relative depth shape matters
# Use: Δf ≈ k * (p+q)^(-2)  with k tuned so that simple rationals (p+q ≈ 2) at
# fc_ref ≈ 115 have ~few-Hz tongue, consistent with 5%-of-f_pll LP bandwidth.
TONGUE_PREFACTOR = 0.05    # 5% tongue at p+q=2 (matches 5% LP bandwidth)


def predict_depth_dist(zeros, q_max, fc_ref, dur_s, mode='events'):
    """
    `mode='events'`    : count crossings with sufficient dwell duration
    `mode='dwell'`     : sum dwell durations
    Returns: dict {depth → predicted_count, depth → n_rationals_at_depth}
    """
    pairs = farey_rationals(q_max)
    pred = {}
    n_at = {}
    for p, q in pairs:
        f_pll = fc_ref * p / q
        if not (5.0 < f_pll < SR * 0.45):
            continue
        d = stern_brocot_depth(p, q)
        n_at[d] = n_at.get(d, 0) + 1
        # Zero passes through f_pll at t* = t_n / f_pll - 1, in seconds.
        # In-band condition: 0 <= t* <= dur_s, i.e. f_pll <= t_n <= f_pll * (dur_s+1).
        in_band = zeros[(zeros >= f_pll) & (zeros <= f_pll * (dur_s + 1))]
        if in_band.size == 0:
            continue
        # Tongue width at (p, q) ; prefactor scales with f_pll for narrow-LP design.
        Δf = TONGUE_PREFACTOR * f_pll * (2.0 / (p + q)) ** 2
        # Sweep rate at f_pll for tone t_n: |df/dt| = f_pll² / t_n
        # Dwell duration in samples
        dwell_s = Δf * in_band / (f_pll ** 2)        # dwell in seconds for each tone
        if mode == 'events':
            qualifying = (dwell_s * SR >= N_LOCK).sum()
            pred[d] = pred.get(d, 0) + int(qualifying)
        else:  # dwell-weighted
            pred[d] = pred.get(d, 0.0) + float(dwell_s.sum())
    return pred, n_at


def to_dist(d_count, depths_to_use):
    """Convert dict {depth → count} to fractional distribution over depths_to_use."""
    arr = np.array([d_count.get(d, 0) for d in depths_to_use], dtype=np.float64)
    s = arr.sum()
    return arr / s if s > 0 else arr


def kl(p, q):
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    mask = (p > 0) & (q > 0)
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))


# ── Load observed data ────────────────────────────────────────────────────────
print("Loading observed distributions …")
with open(os.path.join(THIS_DIR, "gue_calibration_results.pkl"), 'rb') as f:
    cal = pickle.load(f)
results_obs = cal['results']     # (sig_name, q_max, fc_ref) → fast_sweep_summary

# Generate signals to extract zero-arrays for prediction
ACTUAL_NZ = min(NZ, len(scanner.ZETA_ZEROS))
zeta_zeros = scanner.ZETA_ZEROS[:ACTUAL_NZ].astype(np.float64)
# GUE eigenvalues — same generation as signal_gen.make_gue_eigenvalue_signal
rng = np.random.default_rng(42)
A = (rng.standard_normal((ACTUAL_NZ, ACTUAL_NZ)) + 1j * rng.standard_normal((ACTUAL_NZ, ACTUAL_NZ))) / np.sqrt(2)
H = (A + A.conj().T) / np.sqrt(2 * ACTUAL_NZ)
eig = np.sort(np.linalg.eigvalsh(H).real)
spacings = np.diff(eig)
eig_unfolded = (eig - eig[0]) / spacings.mean()
z_min = float(scanner.ZETA_ZEROS[0])
z_max = float(scanner.ZETA_ZEROS[ACTUAL_NZ - 1])
gue_zeros = z_min + eig_unfolded * (z_max - z_min) / eig_unfolded.max()

# Poisson-FM "zeros" — same range, uniform
rng2 = np.random.default_rng(0)
poiss_zeros = np.sort(rng2.uniform(z_min, z_max, ACTUAL_NZ))

ZEROS_BY_SIGNAL = {'zeta': zeta_zeros, 'gue': gue_zeros, 'poiss': poiss_zeros}

print(f"  ζ heights      : range [{zeta_zeros.min():.2f}, {zeta_zeros.max():.2f}]")
print(f"  GUE rescaled   : range [{gue_zeros.min():.2f}, {gue_zeros.max():.2f}]")
print(f"  Poisson-FM     : range [{poiss_zeros.min():.2f}, {poiss_zeros.max():.2f}]")
print()


# ── Compute predictions and residuals at each (signal × cell) ─────────────────
QMAX_LIST = [8, 16]
FC_LIST   = [30.0, 100.0, 115.55, 300.0]

print("=" * 100)
print(f"Predicted (events-with-sufficient-dwell) vs observed depth distribution")
print(f"  PARAMS: lock_confirm = {LOCK_CONFIRM_MS} ms,   tongue_prefactor = {TONGUE_PREFACTOR}")
print("=" * 100)
for q_max in QMAX_LIST:
    print(f"\n  q_max = {q_max}")
    for fc_ref in FC_LIST:
        print(f"\n    fc_ref = {fc_ref:6.2f}")
        # Determine the union of depths present
        depths_obs = set()
        for sig in ['zeta', 'gue', 'poiss']:
            r = results_obs[(sig, q_max, fc_ref)]
            depths_obs.update(int(d) for d in r['depths'] if r['depth_event_counts'][int(np.where(r['depths']==d)[0][0])] > 0)
        depths_pred = set()
        for sig in ['zeta', 'gue', 'poiss']:
            zeros = ZEROS_BY_SIGNAL[sig]
            pred_e, _ = predict_depth_dist(zeros, q_max, fc_ref, DUR, mode='events')
            depths_pred.update(d for d in pred_e if pred_e[d] > 0)
        depths = sorted(depths_obs | depths_pred)
        print(f"      depths considered: {depths}")
        for sig in ['zeta', 'gue', 'poiss']:
            zeros = ZEROS_BY_SIGNAL[sig]
            pred_e, n_at = predict_depth_dist(zeros, q_max, fc_ref, DUR, mode='events')
            pred_d, _    = predict_depth_dist(zeros, q_max, fc_ref, DUR, mode='dwell')
            obs = results_obs[(sig, q_max, fc_ref)]
            obs_dict = dict(zip(obs['depths'].astype(int), obs['depth_event_counts'].astype(int)))
            obs_dist  = to_dist(obs_dict, depths)
            pred_e_dist = to_dist(pred_e,    depths)
            pred_d_dist = to_dist(pred_d,    depths)
            kl_e = kl(obs_dist, pred_e_dist) if pred_e_dist.sum() > 0 else float('nan')
            kl_d = kl(obs_dist, pred_d_dist) if pred_d_dist.sum() > 0 else float('nan')
            kl_g = kl(obs_dist, np.array([2.0**(-d) for d in depths]) /
                                  sum(2.0**(-d) for d in depths)) if obs_dist.sum() > 0 else float('nan')
            obs_str  = " ".join(f"{x:4.2f}" for x in obs_dist)
            pred_str = " ".join(f"{x:4.2f}" for x in pred_e_dist)
            print(f"      {sig:>6s}  obs : {obs_str}    KL(obs∥pred_e)={kl_e:5.3f}  "
                  f"KL(obs∥geom)={kl_g:5.3f}")
            print(f"      {' ':>6s}  pred: {pred_str}    KL(obs∥pred_d)={kl_d:5.3f}")

print()
print("=" * 100)
print("Interpretation")
print("=" * 100)
print("""
  • If KL(obs∥pred_e) is small for all signals: chirp geometry alone explains
    the observed depth distribution.  No arithmetic fingerprint detected.
  • If KL(obs∥pred_e) is small for the nulls but not for ζ: ζ has structure
    beyond the chirp geometry — that residual is the arithmetic fingerprint.
  • Either way, KL(obs∥pred) should be SMALLER than KL(obs∥geometric) — the
    chirp prediction is a much closer baseline than the p-adic uniform prior.
""")


# ── Tabular summary for the headline cell ─────────────────────────────────────
print("=" * 100)
print("Headline: q_max=16, fc_ref=115.55, K_p=0.02 — predicted vs observed")
print("=" * 100)
fc_ref, q_max = 115.55, 16
depths = list(range(0, 16))
print(f"  {'sig':>6}  " + " ".join(f"d={d:>2}" for d in depths) + "    KL(obs∥pred)  KL(obs∥geom)")
for sig in ['zeta', 'gue', 'poiss']:
    zeros = ZEROS_BY_SIGNAL[sig]
    pred_e, _ = predict_depth_dist(zeros, q_max, fc_ref, DUR, mode='events')
    obs = results_obs[(sig, q_max, fc_ref)]
    obs_dict = dict(zip(obs['depths'].astype(int), obs['depth_event_counts'].astype(int)))
    obs_dist  = to_dist(obs_dict, depths)
    pred_e_dist = to_dist(pred_e, depths)
    kl_e = kl(obs_dist, pred_e_dist)
    geom_norm = np.array([2.0**(-d) for d in depths])
    geom_norm /= geom_norm.sum()
    kl_g = kl(obs_dist, geom_norm)
    obs_str  = " ".join(f"{x:5.3f}" for x in obs_dist)
    pred_str = " ".join(f"{x:5.3f}" for x in pred_e_dist)
    print(f"  obs  {sig:>4s}: {obs_str}    KL_pred={kl_e:6.3f}  KL_geom={kl_g:6.3f}")
    print(f"  pred {sig:>4s}: {pred_str}")
    diff = obs_dist - pred_e_dist
    print(f"  resid     : " + " ".join(f"{x:+5.2f}" for x in diff))
    print()
