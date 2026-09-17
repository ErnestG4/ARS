"""Stage 3b — recurrence: L4b (observational, sealed to fail), I1/I2 (intervention), T1 (traversal statistic).

GENERATOR. Sealed before its output (sealgen.sh). Output: stage3b_recurrence_measured.json.
Pre-registration: RING_BRIEF.md "Stage 3b — recurrence" (8591ff5). verify_ring.py R13 scores.

L4b: tangent-projected transverse residual about an order-8 Fourier manifold
model, at the rate level (no spikes) and at rho = 50. Sealed to FAIL to separate
A_n from IND_n; the reason found is recorded.
I1:  along-manifold kick (rotate the state by delta) on three systems sharing
     the trajectory psi(t) = omega t: ring eps=0 (continuous attractor), ring
     eps=0.1 (discrete attractor, slow restoring force), IND_u (independent
     first-order units, no recurrence). Retention of the phase offset at 300 tau.
I2:  transverse kick; both return; rate not kind.
T1:  total variation / net winding and jump count on the lifted path
     (B-avg rail: the signal is 15 boundaries, an average cannot see them).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.ringnet import coupling, heterogeneity, bump_init, gain, order_parameter, BETA  # noqa: E402
from ring import stage1_ph as PH                                                      # noqa: E402
from ring import stage3_lift as S3                                                    # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED                                # noqa: E402

warnings.filterwarnings("ignore")
INSTRUMENT = Model("ring_recurrence_v1", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("gamma", DECLARED, value=0.02, why="drive, omega = gamma"),
    Param("fourier_order", DECLARED, value=8, why="L4b manifold model order in the lifted coordinate"),
    Param("sigma_n", DECLARED, value=0.05, why="L4b input noise, as stage3_lift L4"),
    Param("bin_L4b", DECLARED, value=0.1, why="L4b bin, tau"),
    Param("sigma_s_L4b", DECLARED, value=0.2, why="L4b smoothing, tau"),
    Param("delta_kick", DECLARED, value=0.3, why="I1 along-manifold kick, rad (inside a pinned basin)"),
    Param("eta_kick", DECLARED, value=0.2, why="I2 transverse kick amplitude (relative to |r|)"),
    Param("tau_u", DECLARED, value=1.0, why="IND_u unit time constant; the only dynamics it has"),
    Param("T_obs", DECLARED, value=300.0, why="I1 observation window; the pinned ring's restoring "
                                             "time is 1/0.015 = 67 tau, so 300 tau resolves it"),
    Param("T_pre", DECLARED, value=200.0, why="run before the kick"),
    Param("seed_emit", TESTED, sweep=[41, 42, 43], why="L4b/T1 emission seeds; I1/I2 kick directions"),
    Param("eps_I1", TESTED, sweep=[0.0, 0.1], why="continuous vs discrete attractor under the same kick"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
TH = 2 * np.pi * np.arange(N) / N
W_EVEN = coupling(N, P["J0"].value, P["J1"].value)
W_ODD = P["J1"].value * np.sin(TH[:, None] - TH[None, :]) / N
XI = heterogeneity(N, 1)
I0 = P["I0"].value


def rotate(r, delta):
    """rotate a pattern on the ring by delta rad (periodic interpolation)"""
    src = np.mod(TH - delta, 2 * np.pi)
    return np.interp(src, TH, r, period=2 * np.pi)


def step_ring(r, W, h, noise=0.0):
    return r + dt * (-r + gain(r @ W.T + I0 + h + noise))


def step_ind(r, target, tau_u):
    return r + dt * (-r + target) / tau_u


# ── L4b ──────────────────────────────────────────────────────────────────────
def fourier_manifold(X, phi, K):
    cols = [np.ones_like(phi)] + [f(k * phi) for k in range(1, K + 1) for f in (np.cos, np.sin)]
    A = np.stack(cols, 1)
    coef, *_ = np.linalg.lstsq(A, X, rcond=None)
    m = A @ coef
    dcols = [np.zeros_like(phi)] + [g for k in range(1, K + 1) for g in (-k * np.sin(k * phi), k * np.cos(k * phi))]
    dm = np.stack(dcols, 1) @ coef
    return m, dm


def tau_perp(X, phi, K):
    m, dm = fourier_manifold(X, phi, K)
    e = X - m
    t = dm / np.maximum(np.linalg.norm(dm, axis=1, keepdims=True), 1e-12)
    e_perp = e - (e * t).sum(1, keepdims=True) * t
    e_perp -= e_perp.mean(0)
    v = (e_perp ** 2).sum()
    ac = []
    for lag in range(1, 200):
        c = (e_perp[lag:] * e_perp[:-lag]).sum() / v
        ac.append(c)
        if c < 0.05:
            break
    ac = np.array(ac)
    return float(0.5 + ac.clip(0, None).sum()), [float(a) for a in ac[:8]], float(np.sqrt((e_perp ** 2).mean()))


def rate_cloud(rates, bin_w, sigma_s):
    stp = int(round(bin_w / dt))
    X = rates[::stp]
    sig = sigma_s / bin_w
    k = np.arange(-int(4 * sig), int(4 * sig) + 1); ker = np.exp(-0.5 * (k / sig) ** 2); ker /= ker.sum()
    return np.stack([np.convolve(X[:, i], ker, mode="same") for i in range(X.shape[1])], 1)


def main():
    t0 = time.time()
    rows = []
    prof, psi0 = S3.bump_profile()
    g = P["gamma"].value

    # ── L4b ──
    for seed in P["seed_emit"].sweep:
        rng = np.random.default_rng(seed + 700)
        ratesAn = S3.simulate(g, 50.0, 1000.0, 0.37, sigma_n=P["sigma_n"].value, rng=rng)
        _, psiAn = order_parameter(ratesAn)
        ratesINDn = S3.ind_rates(psiAn, prof, psi0)
        for level in ("rates", "spikes"):
            out = {}
            for name, rates in (("A_n", ratesAn), ("IND_n", ratesINDn)):
                if level == "rates":
                    X = rate_cloud(rates, P["bin_L4b"].value, P["sigma_s_L4b"].value)
                else:
                    PH.P["rho"].value = 50.0
                    sp = PH.emit(rates, np.random.default_rng(seed))
                    X = S3.popvecs(sp, rates.shape[0] * dt, P["bin_L4b"].value, P["sigma_s_L4b"].value)
                L = S3.lift(X)
                if L is None or L["mode"] != "standard":
                    rows.append(dict(arm="L4b", level=level, cloud=name, seed=seed, readable=False)); continue
                tau, ac, rms = tau_perp(X, L["phi"], P["fourier_order"].value)
                rows.append(dict(arm="L4b", level=level, cloud=name, seed=seed, readable=True,
                                 tau_perp_tau=tau * P["bin_L4b"].value, ac=ac, e_perp_rms=rms))
                out[name] = tau * P["bin_L4b"].value
            if len(out) == 2:
                print(f"L4b {level:<6} seed={seed}: tau_perp A_n={out['A_n']:.3f} IND_n={out['IND_n']:.3f} "
                      f"ratio={out['A_n'] / max(out['IND_n'], 1e-9):.2f}")

    # ── I1 / I2 ──
    T_pre, T_obs, delta, eta, tau_u = (P["T_pre"].value, P["T_obs"].value, P["delta_kick"].value,
                                       P["eta_kick"].value, P["tau_u"].value)
    n_pre, n_obs = int(round(T_pre / dt)), int(round(T_obs / dt))
    for seed in P["seed_emit"].sweep:
        rng = np.random.default_rng(seed + 900)
        for eps in P["eps_I1"].sweep:
            W = W_EVEN + g * W_ODD; h = eps * XI
            r = bump_init(N, np.array([0.37]))[0]
            for _ in range(int(round(2000.0 / dt))):
                r = step_ring(r, W, h)
            base = r.copy()
            # unkicked reference and kicked runs, integrated in lockstep
            for kind in ("along", "transverse"):
                r_ref, r_k = base.copy(), base.copy()
                if kind == "along":
                    r_k = rotate(r_k, delta)
                else:
                    v = rng.standard_normal(N)
                    r_prime = (np.roll(base, -1) - np.roll(base, 1)) / (2 * 2 * np.pi / N)
                    v -= (v @ r_prime) / (r_prime @ r_prime) * r_prime
                    v *= eta * np.linalg.norm(base) / np.linalg.norm(v)
                    r_k = r_k + v
                dpsi, dperp = [], []
                for k in range(n_obs):
                    r_ref = step_ring(r_ref, W, h); r_k = step_ring(r_k, W, h)
                    if k % 20 == 0:
                        _, p1 = order_parameter(r_ref[None, :]); _, p2 = order_parameter(r_k[None, :])
                        dpsi.append(float(np.angle(np.exp(1j * (p2[0] - p1[0])))))
                        dperp.append(float(np.linalg.norm(r_k - rotate(r_ref, dpsi[-1])) / np.linalg.norm(r_ref)))
                rows.append(dict(arm="I", system=f"ring_eps{eps:g}", kick=kind, seed=seed, eps=eps,
                                 dpsi_0=dpsi[0], dpsi_10=dpsi[int(10 / dt / 20)], dpsi_end=dpsi[-1],
                                 retention=dpsi[-1] / delta if kind == "along" else None,
                                 dperp_0=dperp[0], dperp_10=dperp[int(10 / dt / 20)], dperp_end=dperp[-1],
                                 dpsi_trace=dpsi[::15], dperp_trace=dperp[::15]))
                x = rows[-1]
                print(f"I  ring eps={eps:<4} {kind:<10} seed={seed}: dpsi 0/10/end = {x['dpsi_0']:+.3f}/{x['dpsi_10']:+.3f}/"
                      f"{x['dpsi_end']:+.3f}  dperp 0/10/end = {x['dperp_0']:.3f}/{x['dperp_10']:.3f}/{x['dperp_end']:.3f}")
        # IND_u: independent first-order units tracking prof(theta - psi(t)), psi = omega t + psi_start
        psi_start = 0.37
        r_ref = prof.copy(); r_ref = rotate(r_ref, psi_start - psi0)
        for k in range(n_pre):                      # settle on the moving target
            tgt = rotate(prof, psi_start + g * k * dt - psi0)
            r_ref = step_ind(r_ref, tgt, tau_u)
        base = r_ref.copy(); k0 = n_pre
        for kind in ("along", "transverse"):
            r_ref, r_k = base.copy(), base.copy()
            if kind == "along":
                r_k = rotate(r_k, delta)
            else:
                v = rng.standard_normal(N)
                r_prime = (np.roll(base, -1) - np.roll(base, 1)) / (2 * 2 * np.pi / N)
                v -= (v @ r_prime) / (r_prime @ r_prime) * r_prime
                v *= eta * np.linalg.norm(base) / np.linalg.norm(v)
                r_k = r_k + v
            dpsi, dperp = [], []
            for k in range(n_obs):
                tgt = rotate(prof, psi_start + g * (k0 + k) * dt - psi0)
                r_ref = step_ind(r_ref, tgt, tau_u); r_k = step_ind(r_k, tgt, tau_u)
                if k % 20 == 0:
                    _, p1 = order_parameter(r_ref[None, :]); _, p2 = order_parameter(r_k[None, :])
                    dpsi.append(float(np.angle(np.exp(1j * (p2[0] - p1[0])))))
                    dperp.append(float(np.linalg.norm(r_k - rotate(r_ref, dpsi[-1])) / np.linalg.norm(r_ref)))
            rows.append(dict(arm="I", system="IND_u", kick=kind, seed=seed, eps=None,
                             dpsi_0=dpsi[0], dpsi_10=dpsi[int(10 / dt / 20)], dpsi_end=dpsi[-1],
                             retention=dpsi[-1] / delta if kind == "along" else None,
                             dperp_0=dperp[0], dperp_10=dperp[int(10 / dt / 20)], dperp_end=dperp[-1],
                             dpsi_trace=dpsi[::15], dperp_trace=dperp[::15]))
            x = rows[-1]
            print(f"I  IND_u        {kind:<10} seed={seed}: dpsi 0/10/end = {x['dpsi_0']:+.3f}/{x['dpsi_10']:+.3f}/"
                  f"{x['dpsi_end']:+.3f}  dperp 0/10/end = {x['dperp_0']:.3f}/{x['dperp_10']:.3f}/{x['dperp_end']:.3f}")

    # ── T1 ──
    ratesA = S3.simulate(g, 50.0, 1000.0, 0.37)
    _, psiA = order_parameter(ratesA)
    ratesIND = S3.ind_rates(psiA, prof, psi0)
    B = 16
    offgrid = 2 * np.pi * (np.arange(B) + 0.37) / B
    segs = [S3.simulate(0.0, 50.0, 1000.0 / B, a) for a in offgrid]
    ratesD = np.concatenate([S3.simulate(0.0, 2000.0, 1000.0 / B, a) for a in offgrid[:3]], 0)  # 3 clusters, no motion
    PH.P["rho"].value = 50.0
    for seed in P["seed_emit"].sweep:
        perm = np.random.default_rng(seed + 500).permutation(B)
        clouds = {"A": ratesA, "IND": ratesIND, "C_ord": np.concatenate(segs, 0),
                  "C_perm": np.concatenate([segs[i] for i in perm], 0), "D": ratesD}
        for name, rates in clouds.items():
            sp = PH.emit(rates, np.random.default_rng(seed))
            X = S3.popvecs(sp, rates.shape[0] * dt, 0.5, 1.0)
            L = S3.lift(X)
            if L is None or L["mode"] != "standard":
                rows.append(dict(arm="T1", cloud=name, seed=seed, readable=False))
                print(f"T1 {name:<6} seed={seed}: UNREADABLE")
                continue
            d = np.angle(np.exp(1j * np.diff(L["phi"])))
            tv = float(np.abs(d).sum()); net = float(abs(L["lift"][-1] - L["lift"][0]))
            J = int((np.abs(d) > np.pi / 2).sum())
            R = tv / max(net, 1e-9)
            rows.append(dict(arm="T1", cloud=name, seed=seed, readable=True, tv=tv, net=net, R=R, J=J,
                             net_turns=net / (2 * np.pi)))
            print(f"T1 {name:<6} seed={seed}: TV={tv:.1f} net={net:.2f} ({net / 2 / np.pi:.2f} turns) R={R:.2f} J={J}")

    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), rows=rows,
               wall_s=round(time.time() - t0, 1), numpy=np.__version__)
    path = os.path.join(HERE, "stage3b_recurrence_measured.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path} ({len(rows)} rows, {out['wall_s']}s)")


if __name__ == "__main__":
    main()
