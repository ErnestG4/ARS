"""Coverage test (H_cov vs H_motion) + the jitter ladder's construction boundary.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage1_coverage_measured.json.
Pre-registration: RING_BRIEF.md "Coverage test + construction boundary" (c478fa0),
arms F1-F6b with numeric predictions. This file computes; verify_ring.py R10 scores.

Reuses stage1_ph's emission / binning / PH pipeline (imported), with a local
simulator so coupling and drive can vary per arm. Every arm carries, at every
jitter rung, the SMOOTHING-MATCHED baseline: the unjittered spikes smoothed at
sigma = sqrt(sigma_s^2 + tau_j^2). Gaussian jitter is, in expectation, that
smoothing plus random misassignment; the matched baseline is what separates
the ladder's constructive side from its destructive side.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.ringnet import coupling, heterogeneity, bump_init, gain, order_parameter, BETA  # noqa: E402
from ring import stage1_ph as PH                                                      # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED                                # noqa: E402

FINE = [30.0, 50.0, 70.0, 100.0, 140.0, 200.0, 300.0]
INSTRUMENT = Model("ring_coverage_v1", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("seed_xi", DECLARED, value=1, why="same heterogeneity pattern"),
    Param("rho", DECLARED, value=50.0, why="as stage1_ph"),
    Param("bin", DECLARED, value=0.5, why="as stage1_ph"),
    Param("sigma_s0", DECLARED, value=1.0, why="baseline smoothing, tau (stage1_ph value)"),
    Param("n_points_max", DECLARED, value=600, why="as stage1_ph"),
    Param("R_MIN", DECLARED, value=3.0, why="as stage1_ph"),
    Param("tau_fine", TESTED, sweep=FINE, why="fine jitter ladder around the banked tau_c"),
    Param("gamma_F2", TESTED, sweep=[0.01, 0.02, 0.04], why="F2: speed at fixed 3 rotations"),
    Param("rot_F3", TESTED, sweep=[1, 3, 10], why="F3: coverage multiplicity at fixed speed"),
    Param("JJ_F4", TESTED, sweep=["-2,4", "-6,8", "-0.5,2.5"],
          why="F4: (J0,J1) -> bump FWHM 2.06 / 1.57 / 2.65 rad (1.69x span) at fixed speed; "
              "the pre-registered set (-1,3),(-4,6) spanned only 1.33x and was swapped "
              "pre-seal (RING_BRIEF S2)"),
    Param("sweeps_F5", TESTED, sweep=[1, 3], why="F5: blocks per unit for the static-bump cloud"),
    Param("sigma_F6", TESTED, sweep=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0],
          why="F6: smoothing scale, no jitter -- the construction boundary"),
    Param("seed_emit", TESTED, sweep=[21, 22], why="emission/subsample seeds (F5 uses 21,22,23)"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
TH = 2 * np.pi * np.arange(N) / N
XI = heterogeneity(N, P["seed_xi"].value)


def simulate(J0, J1, eps, gamma, T_relax, T_sample, angles):
    W = coupling(N, J0, J1) + gamma * J1 * np.sin(TH[:, None] - TH[None, :]) / N
    h = eps * XI
    I0 = P["I0"].value
    r = bump_init(N, np.asarray(angles))
    for _ in range(int(round(T_relax / dt))):
        r += dt * (-r + gain(r @ W.T + I0 + h))
    n = int(round(T_sample / dt))
    out = np.empty((n, len(angles), N))
    for k in range(n):
        r += dt * (-r + gain(r @ W.T + I0 + h))
        out[k] = r
    return out.transpose(1, 0, 2).reshape(len(angles) * n, N)


def fwhm(J0, J1):
    """bump full width at half max, rad, at eps=0, undriven, converged."""
    r = simulate(J0, J1, 0.0, 0.0, 300.0, dt, [0.37])[-1]
    half = r.max() / 2
    return float(2 * np.pi * (r > half).sum() / N)


def popvecs_sigma(spikes, t_max, sigma):
    """stage1_ph.popvecs with an explicit smoothing sigma (tau)."""
    old = PH.P["smooth_sigma"].value
    PH.P["smooth_sigma"].value = sigma
    try:
        return PH.popvecs(spikes, t_max)
    finally:
        PH.P["smooth_sigma"].value = old


def ladder(rates, seeds, taus, label, extra):
    """base + jittered + smoothing-matched at each rung; rows appended to ROWS."""
    t_max = rates.shape[0] * dt
    s0 = P["sigma_s0"].value
    for seed in seeds:
        rng = np.random.default_rng(seed)
        sp = PH.emit(rates, rng)
        st, _ = PH.ph_stat(popvecs_sigma(sp, t_max, s0), 0.5, np.random.default_rng(seed + 1000))
        ROWS.append(dict(arm=label, kind="base", seed=seed, tau_j=None, sigma=s0, **extra, **st))
        for tj in taus:
            spj = PH.jitter(sp, tj, rng, t_max)
            st, _ = PH.ph_stat(popvecs_sigma(spj, t_max, s0), 0.5, np.random.default_rng(seed + 1000))
            ROWS.append(dict(arm=label, kind="jitter", seed=seed, tau_j=tj, sigma=s0, **extra, **st))
            sm = float(np.sqrt(s0 ** 2 + tj ** 2))
            st, _ = PH.ph_stat(popvecs_sigma(sp, t_max, sm), 0.5, np.random.default_rng(seed + 1000))
            ROWS.append(dict(arm=label, kind="matched", seed=seed, tau_j=tj, sigma=sm, **extra, **st))
    med = lambda k, tj=None: float(np.median([r["r12"] for r in ROWS if r["arm"] == label and r["kind"] == k
                                               and (tj is None or r["tau_j"] == tj)
                                               and all(r[kk] == vv for kk, vv in extra.items())]))
    print(f"{label:<18} {extra}  base={med('base'):.1f}  jitter:"
          + " ".join(f"{med('jitter', t):.1f}" for t in taus)
          + "  matched:" + " ".join(f"{med('matched', t):.1f}" for t in taus))


ROWS = []


def main():
    t0 = time.time()
    seeds = P["seed_emit"].sweep
    # F1 — fine ladder on A and B (J0=-2,J1=4, gamma=0.02, 3 rotations ~ 942 tau)
    for name, eps in (("A", 0.0), ("B", 0.1)):
        rates = simulate(-2.0, 4.0, eps, 0.02, 50.0, 3 * 2 * np.pi / 0.02, [0.37])
        ladder(rates, seeds, FINE, "F1", dict(cloud=name, eps=eps, gamma=0.02, rot=3, J0=-2.0, J1=4.0))
    # F2 — speed at fixed 3 rotations
    for g in P["gamma_F2"].sweep:
        rates = simulate(-2.0, 4.0, 0.0, g, 50.0, 3 * 2 * np.pi / g, [0.37])
        ladder(rates, seeds, FINE, "F2", dict(cloud="A", eps=0.0, gamma=g, rot=3, J0=-2.0, J1=4.0))
    # F3 — coverage multiplicity at fixed speed
    for rot in P["rot_F3"].sweep:
        rates = simulate(-2.0, 4.0, 0.0, 0.02, 50.0, rot * 2 * np.pi / 0.02, [0.37])
        ladder(rates, seeds, FINE, "F3", dict(cloud="A", eps=0.0, gamma=0.02, rot=rot, J0=-2.0, J1=4.0))
    # F4 — bump width at fixed speed
    widths = {}
    for jj in P["JJ_F4"].sweep:
        J0, J1 = map(float, jj.split(","))
        widths[jj] = fwhm(J0, J1)
        rates = simulate(J0, J1, 0.0, 0.02, 50.0, 3 * 2 * np.pi / 0.02, [0.37])
        ladder(rates, seeds, FINE, "F4", dict(cloud="A", eps=0.0, gamma=0.02, rot=3, J0=J0, J1=J1))
        print(f"   width FWHM({jj}) = {widths[jj]:.3f} rad")
    # F5 — C1 vs C3 under scramble (3 seeds)
    B = 16
    offgrid = 2 * np.pi * (np.arange(B) + 0.37) / B
    for sweeps in P["sweeps_F5"].sweep:
        seg = 1000.0 / (B * sweeps)
        one = simulate(-2.0, 4.0, 0.0, 0.0, 50.0, seg, offgrid)
        rates = np.concatenate([one] * sweeps, 0)
        t_max = rates.shape[0] * dt
        for seed in (21, 22, 23):
            rng = np.random.default_rng(seed)
            sp = PH.emit(rates, rng)
            st, _ = PH.ph_stat(popvecs_sigma(sp, t_max, 1.0), 0.5, np.random.default_rng(seed + 1000))
            ROWS.append(dict(arm="F5", kind="base", seed=seed, tau_j=None, sigma=1.0, cloud=f"C{sweeps}",
                             sweeps=sweeps, **st))
            sps = PH.isi_scramble(sp, rng, t_max)
            st, _ = PH.ph_stat(popvecs_sigma(sps, t_max, 1.0), 0.5, np.random.default_rng(seed + 1000))
            ROWS.append(dict(arm="F5", kind="scramble", seed=seed, tau_j=None, sigma=1.0, cloud=f"C{sweeps}",
                             sweeps=sweeps, **st))
            print(f"F5 C{sweeps} seed={seed}: base r12={ROWS[-2]['r12']:.1f} scramble r12={st['r12']:.2f} b1={st['b1']:.1f}")
    # F6 — construction boundary: sigma sweep, no jitter, on A and E2
    ratesA = simulate(-2.0, 4.0, 0.0, 0.02, 50.0, 1000.0, [0.37])
    ratesE = simulate(-2.0, 4.0, 0.1, 0.0, 100.0, 400.0, 2 * np.pi * (np.arange(4) + 0.37) / 4)
    for name, rates in (("A", ratesA), ("E2", ratesE)):
        t_max = rates.shape[0] * dt
        for seed in seeds:
            sp = PH.emit(rates, np.random.default_rng(seed))
            for sg in P["sigma_F6"].sweep:
                st, _ = PH.ph_stat(popvecs_sigma(sp, t_max, sg), 0.5, np.random.default_rng(seed + 1000))
                ROWS.append(dict(arm="F6", kind="sigma", seed=seed, tau_j=None, sigma=sg, cloud=name, **st))
        print(f"F6 {name}: r12 by sigma = " + " ".join(
            f"{np.median([r['r12'] for r in ROWS if r['arm']=='F6' and r['cloud']==name and r['sigma']==sg]):.1f}"
            for sg in P["sigma_F6"].sweep))
        # F6b — smoothing-matched ladder on E2 (A and B already carry it from F1)
        if name == "E2":
            ladder(rates, seeds, FINE, "F6b", dict(cloud="E2", eps=0.1, gamma=0.0, rot=0, J0=-2.0, J1=4.0))

    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), widths=widths,
               fine=FINE, rows=ROWS, wall_s=round(time.time() - t0, 1), numpy=np.__version__)
    path = os.path.join(HERE, "stage1_coverage_measured.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path} ({len(ROWS)} rows, {out['wall_s']}s)")


if __name__ == "__main__":
    main()
