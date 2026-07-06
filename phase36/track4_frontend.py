"""
phase36/track4_frontend.py — Track 4 continuous front-end feasibility (Phase 36).

Calibrator-ONLY, falsification-gated. Config: phase36/TRACK4_CONFIG_JUSTIFICATION.md.
Ground truth: analytic Almost-Mathieu operator (golden θ), metal (λ<1, AC spectrum, transport) vs
insulator (λ>1, pure point, localized), transition at λ=1.

Two continuous front-ends feeding the validated core:
  F2 — spectral-measure → IDS-unfold (CONSERVATIVE; inherits banked IDS_LEG_RATIO_FREE). Estimate the
       DOS via Gaussian KDE on the eigenvalues, unfold eigenvalues through the smoothed cumulative DOS,
       read W1δ. Knob: KDE bandwidth h.
  F1 — Hilbert instantaneous-phase → rotation-number stream (THE real new test). Build the continuous
       wavepacket return amplitude φ(t)=⟨e₀|e^{−iHt}|e₀⟩=Σ_k w_k e^{−iE_k t} (w_k=|v_k[0]|²), band-pass
       Re φ(t), Hilbert → unwrapped instantaneous phase → 2π-crossing times → inter-crossing intervals →
       unit-mean → NNS W1δ / quadrant. Knob: filter band. Inherited confound: α (=operator phase φ, the
       N=2584-noisy d.o.f.) — swept INDEPENDENTLY of the band (pin α high-N-stable for the headline).

Promotion (pre-registered): a front-end recovers the banked metal↔insulator verdict (separation
bracketing λ=1 + NFP-in-metal + sensitivity floor no worse) AND is knob-robust. PASS → continuous arm
is a real missing piece. FAIL → §7.ter.19 reaffirmed with positive evidence (name the knob that broke it).
Out: phase36/track4_frontend_results.json + printed summary. NO real neural data.
"""
from __future__ import annotations
import os, sys, json
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.signal import butter, sosfiltfilt, hilbert
from scipy.stats import gaussian_kde

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE); P35A = os.path.join(ROOT, "phase35a")
for p in (ROOT, P35A):
    sys.path.insert(0, p)
from unfold_rotnum import am_diag, GOLDEN, W1d, spacings              # noqa: E402
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic  # noqa: E402

N = 2584                       # F_18, banked cell size
LAMS = [0.5, 0.85, 0.95, 1.05, 1.25, 1.5]   # λ=1 excluded (banked convention)
METAL, INSUL = 0.5, 1.5


def am_eig_full(lam, n, phi):
    d = am_diag(n, lam, GOLDEN, phi); e = np.ones(n - 1)
    return eigh_tridiagonal(d, e)          # E, V


# ── F2: spectral-measure (KDE-DOS) → IDS-unfold ────────────────────────────
def f2_unfold(lam, n, phi, h_factor=1.0):
    E, _ = am_eig_full(lam, n, phi)
    E = np.sort(E)
    kde = gaussian_kde(E, bw_method=h_factor * len(E) ** (-1 / 5.))  # h_factor × Silverman (1-D factor n^-1/5)
    grid = np.linspace(E.min() - 1, E.max() + 1, 8000)
    dens = kde(grid); cdf = np.cumsum(dens); cdf /= cdf[-1]
    unf = np.interp(E, grid, cdf) * len(E)          # smoothed-IDS unfold
    return round(float(W1d(unf)), 5)


def f2_run():
    res = {}
    for lam in (METAL, INSUL):
        res[lam] = {h: f2_unfold(lam, N, 0.0, h) for h in (0.25, 0.5, 1.0, 2.0)}
    # separation at each bandwidth, and robustness
    seps = {h: round(res[INSUL][h] - res[METAL][h], 5) for h in (0.25, 0.5, 1.0, 2.0)}
    sep_vals = list(seps.values())
    robust = (min(sep_vals) > 0) == (max(sep_vals) > 0) and (max(sep_vals) - min(sep_vals)) < abs(np.mean(sep_vals)) + 1e-9
    return dict(W1d=res, insul_minus_metal_by_h=seps,
                separates=bool(all(s > 0.02 for s in sep_vals)),
                knob_robust=bool(robust))


# ── F1: Hilbert phase → rotation-number stream ─────────────────────────────
def phi_t(lam, n, t, phi=0.0):
    E, V = am_eig_full(lam, n, phi)
    w = V[0, :] ** 2
    return (w[None, :] * np.exp(-1j * t[:, None] * E[None, :])).sum(1)


def f1_crossing_intervals(lam, n, phi, band, dt=0.1, T=600.0):
    t = np.arange(0, T, dt)
    sig = np.real(phi_t(lam, n, t, phi))
    fs = 1.0 / dt
    lo, hi = band
    sos = butter(4, [lo, hi], btype="band", fs=fs, output="sos")
    filt = sosfiltfilt(sos, sig)
    ana = hilbert(filt)
    ph = np.unwrap(np.angle(ana))
    # 2π-crossing times: where ph crosses successive multiples of 2π
    k0 = np.ceil(ph[0] / (2 * np.pi)); k1 = np.floor(ph[-1] / (2 * np.pi))
    if k1 <= k0 + 5:
        return None
    levels = 2 * np.pi * np.arange(k0, k1 + 1)
    cross_t = np.interp(levels, ph, t)       # ph monotone increasing (unwrapped) ⇒ valid
    iv = np.diff(cross_t)
    iv = iv[iv > 0]
    return iv


def f1_readout(lam, n, phi, band, dt=0.1, T=600.0):
    iv = f1_crossing_intervals(lam, n, phi, band, dt, T)
    if iv is None or iv.size < 60:
        return None
    s = iv / iv.mean()
    out = dict(n=int(iv.size), CV=round(float(s.std()), 4), W1d=round(float(W1d(np.cumsum(np.concatenate([[0.], s])))), 5))
    # quadrant readout if enough events
    if iv.size >= 200:
        pos = np.cumsum(np.concatenate([[0.], s]))
        try:
            j = joint_q_profile(pos, q_max=25, min_events_per_q=50)
            qd = joint_quadrant_diagnostic(j); w = qd[~qd['underpowered']]
            if len(w):
                out['rep_med'] = round(float(w['rep_int_q'].median()), 4)
                out['quad'] = dict(w['quadrant'].value_counts())
        except Exception:
            pass
    return out


def f1_run():
    # Spectral support ~[-(2+2λ),2+2λ]; the return-amplitude oscillation is O(1) rad/time. On the dt-grid
    # this lands at ~0.1-0.3 Hz. Low bands (<0.05) give too few 2π-crossings in the horizon — use T long
    # enough that the working bands yield ≥200 crossings (quadrant readout). DEFAULT chosen mid-support.
    DEFAULT_BAND = (0.05, 0.30); T = 2000.0
    out = dict(default_band=DEFAULT_BAND, T=T)
    # (1) metal vs insulator at default band, α=0 (headline; α pinned in the high-N-stable regime)
    out['metal'] = f1_readout(METAL, N, 0.0, DEFAULT_BAND, T=T)
    out['insul'] = f1_readout(INSUL, N, 0.0, DEFAULT_BAND, T=T)
    # (2) full λ-bracket (transition location)
    out['lambda_bracket'] = {lam: f1_readout(lam, N, 0.0, DEFAULT_BAND, T=T) for lam in LAMS}
    # (3) BAND knob-robustness (at pinned α=0) — only bands that yield enough crossings
    out['band_sweep'] = {}
    for band in [(0.05, 0.30), (0.10, 0.40), (0.15, 0.45), (0.08, 0.25)]:
        m = f1_readout(METAL, N, 0.0, band, T=T); ins = f1_readout(INSUL, N, 0.0, band, T=T)
        if m and ins:
            out['band_sweep'][str(band)] = dict(metal_W1d=m['W1d'], insul_W1d=ins['W1d'],
                                                 sep=round(ins['W1d'] - m['W1d'], 5))
    # (4) α CONFOUND sweep (independent of band; bounds phase-noise) at default band
    out['alpha_sweep'] = {}
    for a in (0.0, 0.13, 0.27, 0.41):
        m = f1_readout(METAL, N, a, DEFAULT_BAND, T=T); ins = f1_readout(INSUL, N, a, DEFAULT_BAND, T=T)
        if m and ins:
            out['alpha_sweep'][round(a, 2)] = dict(metal_W1d=m['W1d'], insul_W1d=ins['W1d'],
                                                    sep=round(ins['W1d'] - m['W1d'], 5))
    return out


def main():
    print("=" * 78); print("TRACK 4 — CONTINUOUS FRONT-END FEASIBILITY (Phase 36)"); print("=" * 78, flush=True)
    R = {}
    print("\n[F2] spectral-measure (KDE-DOS) → IDS-unfold ...", flush=True)
    R['F2'] = f2_run(); print("   ", R['F2'])
    print("\n[F1] Hilbert phase → rotation-number stream ...", flush=True)
    R['F1'] = f1_run()
    for k in ('metal', 'insul', 'default_band'):
        print(f"    {k}: {R['F1'][k]}")
    print("    λ-bracket:", R['F1']['lambda_bracket'])
    print("    band-sweep:", R['F1']['band_sweep'])
    print("    α-sweep:", R['F1']['alpha_sweep'])

    # ── promotion adjudication (pre-registered; STRICT: separation alone ≠ promotion) ──
    f2 = R['F2']
    # F2 promotion requires recovering the banked metal→FLOOR, not just a robust separation.
    BANKED_FLOOR = 0.02   # banked rotation-number leg: metal W1δ ≈ 0.005; allow generous floor band
    f2_metal_at_floor = bool(min(f2['W1d'][METAL].values()) < BANKED_FLOOR)
    f2['recovers_floor'] = f2_metal_at_floor
    # F1
    band_seps = [v['sep'] for v in R['F1']['band_sweep'].values()]
    alpha_seps = [v['sep'] for v in R['F1']['alpha_sweep'].values()]
    f1_band_robust = bool(len(band_seps) >= 2 and (all(s > 0 for s in band_seps) or all(s < 0 for s in band_seps)))
    f1_alpha_robust = bool(len(alpha_seps) >= 2 and (all(s > 0 for s in alpha_seps) or all(s < 0 for s in alpha_seps)))
    f1_separates = bool(R['F1']['metal'] and R['F1']['insul'] and
                        abs(R['F1']['insul']['W1d'] - R['F1']['metal']['W1d']) > 0.02)
    # λ-bracket monotonicity (transition location): W1δ monotone across λ where measured
    br = {k: v for k, v in R['F1']['lambda_bracket'].items() if v}
    br_w = [br[k]['W1d'] for k in sorted(br)]
    f1_bracket_monotone = bool(len(br_w) >= 4 and (np.all(np.diff(br_w) <= 1e-3) or np.all(np.diff(br_w) >= -1e-3)))
    R['verdict'] = dict(
        F2_separates=f2['separates'], F2_knob_robust=f2['knob_robust'], F2_recovers_floor=f2_metal_at_floor,
        F2_promoted=bool(f2['separates'] and f2['knob_robust'] and f2_metal_at_floor),
        F2_status=("PROMOTED" if (f2['separates'] and f2['knob_robust'] and f2_metal_at_floor)
                   else "SEPARATES_ROBUST_BUT_NO_FLOOR (smoothed DOS coarsens; floor needs exact rotation-number IDS)"),
        F1_separates=f1_separates, F1_band_robust=f1_band_robust, F1_alpha_robust=f1_alpha_robust,
        F1_bracket_monotone=f1_bracket_monotone,
        F1_promoted=bool(f1_separates and f1_band_robust and f1_alpha_robust),
        F1_n_bands_measured=len(band_seps), F1_n_alpha_measured=len(alpha_seps),
    )
    print("\n" + "=" * 78)
    print(" VERDICT:", R['verdict'])
    print("=" * 78)

    def _ser(o):
        if isinstance(o, np.bool_): return bool(o)
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return float(o)
        return str(o)
    json.dump(R, open(os.path.join(HERE, "track4_frontend_results.json"), "w"), indent=1, default=_ser)
    print(" → phase36/track4_frontend_results.json")


if __name__ == "__main__":
    main()
