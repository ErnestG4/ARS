"""Stage 3a — path-lifting: (n, theta) off the population cloud, with its ceiling.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage3_lift_measured.json.
Pre-registration: RING_BRIEF.md "Stage 3a — path-lifting" (620e975): invariants
under the lift's ambiguity stated first; arms L1-L4 with sealed predictions.
verify_ring.py R12 scores.

Pipeline: rates -> Poisson spikes (stage1_ph.emit) -> binned, smoothed population
vectors -> DREiMac CircularCoords (persistent cohomology, longest H1 class) ->
circular coordinate phi in [0, 2pi) -> lift to R by unwrapping -> winding count.
Ground truth is the bump angle psi(t) from the simulation. theta is compared only
after removing a monotone reparametrization (Fourier order <= 3 in psi), because
a cohomological coordinate is affine in the true angle only up to one.

L4 adds declared input noise to the ring so the bump diffuses and relaxes; the
independent-unit control IND_n is built on the ring's OWN noisy trajectory so
kinematics are identical by construction and transverse relaxation is the
only difference. That is the candidate instrument for the attractor rung.
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
from dreimac import CircularCoords

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.ringnet import coupling, heterogeneity, bump_init, gain, order_parameter, BETA  # noqa: E402
from ring import stage1_ph as PH                                                      # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED                                # noqa: E402

warnings.filterwarnings("ignore")
RHOS = [50.0, 15.0, 5.0, 1.5, 0.5]
INSTRUMENT = Model("ring_lift_v1", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("gamma", DECLARED, value=0.02, why="drive; omega = gamma; 3.18 rotations in T_drive"),
    Param("T_drive", DECLARED, value=1000.0, why="as stage1_ph cloud A"),
    Param("n_landmarks", DECLARED, value=150, why="DREiMac landmarks; cloud is 2000 points"),
    Param("perc", DECLARED, value=0.5, why="DREiMac cover-radius percentile"),
    Param("reparam_order", DECLARED, value=3, why="Fourier order removed before theta is called noise"),
    Param("continuity_step", DECLARED, value=float(np.pi / 4), why="|dphi| below this = continuous step"),
    Param("sigma_n", DECLARED, value=0.05, why="L4 input noise per unit per step (dt-scaled), so the "
                                              "bump diffuses along its marginal mode"),
    Param("bin_L4", DECLARED, value=0.1, why="L4 bin, tau"),
    Param("sigma_s_L4", DECLARED, value=0.2, why="L4 smoothing, tau; must be << 1/0.55 to see relaxation"),
    Param("rho", TESTED, sweep=RHOS, why="L2: emission rate, 100x span"),
    Param("bin_L2", TESTED, sweep=[0.5, 0.1], why="L2: bin width, to push theta noise up before the "
                                                    "coordinate fails"),
    Param("seed_emit", TESTED, sweep=[31, 32, 33], why="emission / permutation seeds"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
TH = 2 * np.pi * np.arange(N) / N
W_EVEN = coupling(N, P["J0"].value, P["J1"].value)
W_ODD = P["J1"].value * np.sin(TH[:, None] - TH[None, :]) / N


def simulate(gamma, T_relax, T_sample, angle, sigma_n=0.0, rng=None):
    W = W_EVEN + gamma * W_ODD
    I0 = P["I0"].value
    r = bump_init(N, np.array([angle]))
    for _ in range(int(round(T_relax / dt))):
        r += dt * (-r + gain(r @ W.T + I0))
    n = int(round(T_sample / dt))
    out = np.empty((n, N))
    for k in range(n):
        noise = (sigma_n * rng.standard_normal(N) / np.sqrt(dt)) if sigma_n > 0 else 0.0
        r += dt * (-r + gain(r @ W.T + I0 + noise))
        out[k] = r[0]
    return out


def bump_profile():
    """the ring's own converged bump profile, as a tuning curve of angle offset"""
    r = simulate(0.0, 300.0, dt, 0.0)[-1]
    _, psi = order_parameter(r[None, :])
    return r, float(psi[0])


def ind_rates(psi_t, prof, psi0):
    """independent units: rate_i(t) = prof(theta_i - (psi(t) - psi0)); no recurrence"""
    shift = psi_t - psi0
    idx = (np.arange(N)[None, :] - np.round(shift[:, None] / (2 * np.pi / N)).astype(int)) % N
    return prof[idx]


def popvecs(spikes, t_max, bin_w, sigma_s):
    ob, osg = PH.P["bin"].value, PH.P["smooth_sigma"].value
    PH.P["bin"].value, PH.P["smooth_sigma"].value = bin_w, sigma_s
    try:
        return PH.popvecs(spikes, t_max)
    finally:
        PH.P["bin"].value, PH.P["smooth_sigma"].value = ob, osg


def lift(X):
    """circular coordinate + lift; returns dict or None if no class is readable"""
    try:
        cc = CircularCoords(X, n_landmarks=P["n_landmarks"].value)
        dg = cc.dgms_[1]
        pers = np.sort(dg[:, 1] - dg[:, 0])[::-1] if len(dg) else np.array([0.0])
        try:
            phi = cc.get_coordinates(perc=P["perc"].value, cocycle_idx=0)
            mode = "standard"
        except Exception:
            phi = cc.get_coordinates(perc=P["perc"].value, cocycle_idx=0, standard_range=False)
            mode = "nonstandard_range"
    except Exception as e:              # noqa: BLE001
        return None
    phi = np.asarray(phi, dtype=float)
    return dict(phi=phi, lift=np.unwrap(phi), b1=float(pers[0]), b2=float(pers[1]) if len(pers) > 1 else 0.0,
                mode=mode)


def compare(lifted, psi_bin):
    """|n|, sign, k, theta residual after removing offset + order<=3 reparametrization."""
    psi_u = np.unwrap(psi_bin)
    n_true = int(np.floor(abs(psi_u[-1] - psi_u[0]) / (2 * np.pi) + 1e-9))
    wind = (lifted[-1] - lifted[0]) / (2 * np.pi)
    n_est = int(np.floor(abs(wind) + 1e-9))
    sgn = int(np.sign(wind)) if wind != 0 else 0
    # reparametrization fit: sgn*lift ~ psi_u + b + sum_k a_k cos(k psi) + c_k sin(k psi)
    K = P["reparam_order"].value
    cols = [np.ones_like(psi_u)] + [f(k * psi_u) for k in range(1, K + 1) for f in (np.cos, np.sin)]
    A = np.stack(cols, 1)
    y = sgn * lifted - psi_u
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    resid = np.angle(np.exp(1j * resid))
    aff = np.angle(np.exp(1j * (y - np.median(y))))
    frac_true = abs(psi_u[-1] - psi_u[0]) / (2 * np.pi)
    k_est = abs(wind) / max(frac_true, 1e-9)
    return dict(n_true=n_true, n_est=n_est, sign=sgn, k_est=float(k_est), wind_est=float(abs(wind)),
                wind_true=float(frac_true), theta_rms=float(np.sqrt((resid ** 2).mean())),
                theta_rms_affine_only=float(np.sqrt((aff ** 2).mean())))


def continuity(phi):
    d = np.abs(np.angle(np.exp(1j * np.diff(phi))))
    return float((d < P["continuity_step"].value).mean()), float((d > np.pi / 2).mean())


def transverse_tau(X, phi, n_bins=32):
    """autocorrelation time of residuals about the manifold curve m(phi), in bins"""
    b = ((phi % (2 * np.pi)) / (2 * np.pi) * n_bins).astype(int) % n_bins
    m = np.zeros((n_bins, X.shape[1]))
    for j in range(n_bins):
        if (b == j).any():
            m[j] = X[b == j].mean(0)
    res = X - m[b]
    res = res - res.mean(0)
    v = (res ** 2).sum()
    taus = []
    ac = []
    for lag in range(1, 60):
        c = (res[lag:] * res[:-lag]).sum() / v
        ac.append(c)
        if c < 0.05:
            break
    ac = np.array(ac)
    return float(0.5 + ac.clip(0, None).sum()), [float(a) for a in ac[:10]]


def main():
    t0 = time.time()
    rows = []
    prof, psi0 = bump_profile()
    ratesA = simulate(P["gamma"].value, 50.0, P["T_drive"].value, 0.37)
    _, psiA = order_parameter(ratesA)
    t_max = ratesA.shape[0] * dt
    step = int(round(0.5 / dt))
    psiA_bin = psiA[(np.arange(int(np.ceil(t_max / 0.5))) * step).clip(0, len(psiA) - 1)]

    def run_cloud(name, rates, psi_t, rho, bin_w, sigma_s, seed, extra=None):
        PH.P["rho"].value = rho
        rng = np.random.default_rng(seed)
        sp = PH.emit(rates, rng)
        X = popvecs(sp, rates.shape[0] * dt, bin_w, sigma_s)
        stp = int(round(bin_w / dt))
        pb = psi_t[(np.arange(X.shape[0]) * stp).clip(0, len(psi_t) - 1)]
        L = lift(X)
        row = dict(cloud=name, rho=rho, bin=bin_w, sigma_s=sigma_s, seed=seed, **(extra or {}))
        if L is None:
            row.update(readable=False)
            rows.append(row); return row, None, None
        cont, big = continuity(L["phi"])
        row.update(readable=True, mode=L["mode"], b1=L["b1"], b2=L["b2"], continuity=cont,
                   big_jump_frac=big, **compare(L["lift"], pb))
        rows.append(row)
        return row, X, L
    # L1 + L2: cloud A over rho and bin
    for bin_w in P["bin_L2"].sweep:
        sigma_s = 1.0 if bin_w == 0.5 else 0.2
        for rho in RHOS:
            for seed in P["seed_emit"].sweep:
                row, _, _ = run_cloud("A", ratesA, psiA, rho, bin_w, sigma_s, seed, dict(arm="L2"))
                print(f"L2 A bin={bin_w} rho={rho:<5} seed={seed}: " + (
                    f"|n|={row['n_est']}/{row['n_true']} sign={row['sign']:+d} k={row['k_est']:.2f} "
                    f"theta_rms={row['theta_rms']:.3f} (affine-only {row['theta_rms_affine_only']:.3f}) "
                    f"cont={row['continuity']:.3f} b1={row['b1']:.1f} [{row['mode']}]" if row["readable"]
                    else "UNREADABLE (no cohomology class)"))
    # L3: traversal detector across clouds at rho = 50
    ratesIND = ind_rates(psiA, prof, psi0)
    B = 16
    offgrid = 2 * np.pi * (np.arange(B) + 0.37) / B
    segs = [simulate(0.0, 50.0, P["T_drive"].value / B, a) for a in offgrid]
    psi_segs = [order_parameter(sg)[1] for sg in segs]
    for seed in P["seed_emit"].sweep:
        row, _, _ = run_cloud("IND", ratesIND, psiA, 50.0, 0.5, 1.0, seed, dict(arm="L3"))
        print(f"L3 IND seed={seed}: |n|={row.get('n_est')} cont={row.get('continuity', float('nan')):.3f}")
        rates_ord = np.concatenate(segs, 0); psi_ord = np.concatenate(psi_segs)
        row, _, _ = run_cloud("C_ord", rates_ord, psi_ord, 50.0, 0.5, 1.0, seed, dict(arm="L3"))
        print(f"L3 C_ord seed={seed}: |n|={row.get('n_est')}/{row.get('n_true')} cont={row.get('continuity', float('nan')):.3f}")
        perm = np.random.default_rng(seed + 500).permutation(B)
        rates_perm = np.concatenate([segs[i] for i in perm], 0); psi_perm = np.concatenate([psi_segs[i] for i in perm])
        row, _, _ = run_cloud("C_perm", rates_perm, psi_perm, 50.0, 0.5, 1.0, seed, dict(arm="L3", perm=[int(i) for i in perm]))
        print(f"L3 C_perm seed={seed}: |n|={row.get('n_est')} cont={row.get('continuity', float('nan')):.3f} "
              f"big-jump={row.get('big_jump_frac', float('nan')):.3f}")
    # L4: attractor rung -- noisy ring vs independent units on its own trajectory
    for seed in P["seed_emit"].sweep:
        rng = np.random.default_rng(seed + 700)
        ratesAn = simulate(P["gamma"].value, 50.0, P["T_drive"].value, 0.37, sigma_n=P["sigma_n"].value, rng=rng)
        _, psiAn = order_parameter(ratesAn)
        ratesINDn = ind_rates(psiAn, prof, psi0)
        out = {}
        for name, rates in (("A_n", ratesAn), ("IND_n", ratesINDn)):
            row, X, L = run_cloud(name, rates, psiAn, 50.0, P["bin_L4"].value, P["sigma_s_L4"].value, seed, dict(arm="L4"))
            if L is not None:
                tau, ac = transverse_tau(X, L["phi"])
                row.update(tau_tr_bins=tau, tau_tr_tau=tau * P["bin_L4"].value, ac_tr=ac)
                out[name] = row["tau_tr_tau"]
            print(f"L4 {name} seed={seed}: readable={row['readable']} |n|={row.get('n_est')} "
                  f"cont={row.get('continuity', float('nan')):.3f} tau_tr={row.get('tau_tr_tau', float('nan')):.3f} tau")
        if len(out) == 2:
            print(f"   ratio tau_tr(A_n)/tau_tr(IND_n) = {out['A_n'] / max(out['IND_n'], 1e-9):.2f}")

    PH.P["rho"].value = 50.0
    res = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), rows=rows,
               wall_s=round(time.time() - t0, 1), numpy=np.__version__)
    path = os.path.join(HERE, "stage3_lift_measured.json")
    with open(path, "w") as f:
        json.dump(res, f, indent=1)
    print(f"wrote {path} ({len(rows)} rows, {res['wall_s']}s)")


if __name__ == "__main__":
    main()
