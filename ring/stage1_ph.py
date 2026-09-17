"""Stage 1, measure 2 — PH H1 on population-vector clouds off the ring, with its nulls.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage1_ph_measured.json.
Pre-registration: RING_BRIEF.md "Measure 2 — pre-registration" (commit a975089),
including five predictions P1-P5 derived from c (contour) and omega (drive)
BEFORE this file ran. This file computes; verify_ring.py R9 scores.

Clouds:  A intact driven  (eps=0,   gamma=0.02)         positive
         B pinned driven  (eps=0.1, gamma=0.02)         wells, still traverses
         C intact undriven(eps=0,   gamma=0)            16 static bumps
         D pinned undriven converged (eps=0.1, gamma=0, relaxed 2000 tau)  negative
         E1/E2 pinned undriven TRANSIENT sampled over W=50 / 200 tau after a
               100 tau relax -- the confusable placed at a contour coordinate
               (arc length L = c*eps*W: 0.15 rad gaps / 0.58 rad covered)
Arms:    jitter ladder on A, B, E2; within-cell ISI-order scramble on A, B, C, E2;
         subsetting sweep q on every base cloud; 3 emission seeds.
Statistic: r12 = longest H1 bar / second longest (ripser, H1, cocycles kept).

PRE-SEAL PILOT (2026-09-16, one seed, cloud A/D/E only; disclosed, not absorbed):
  * tau_c(A) under the R_MIN=3 definition was CENSORED at the ladder's top rung
    (r12 = 5.1 at tau_j = 100). The ladder RANGE is extended to 1000 tau so the
    boundary is not "where the window ran out". Prediction P1 (30 tau) is kept
    exactly as sealed and will be scored as it stands.
  * E1 read r12 = 28.8 > E2 = 23.6: the coordinate prediction failed as designed
    because the covering condition is L + w >= 2*pi/B with w the BUMP WIDTH
    (the Rips metric resolution), not L >= 2*pi/B. With B=16 (spacing 0.39 rad)
    and w ~ 0.6 rad the gaps are bridged at any L. E is redesigned pre-seal:
    B_E = 4 (spacing 1.57 rad > w), W_E in {100, 400} tau (L = 0.29 -> gap 0.68
    rad open; L = 1.16 -> covered). P5's "E1 < E2" is re-sealed against THIS
    design; the failure of the first form is recorded in RING_BRIEF.md.

V2 (2026-09-16, after the v1 run was banked and read): two SURROGATE defects
found by arms reading against their sealed predictions, fixed, re-sealed.
  * ISI scramble ANCHORED each unit's train at its first spike time. On cloud C
    (one sweep of the ring) firing ONSET is ordered by angle, so onset order --
    a sequence channel -- survived the "sequence-destroying" surrogate, and C
    kept 40% of its H1 bar (b1 76-89 vs 210) where P4 said the arm would be a
    no-op. v2 adds a uniform random circular offset per unit.
  * Jitter CLIPPED to [0, t_max]; at tau_j >= t_max/3 the clipped spikes piled
    up at the window edges and manufactured a b1 = 1230 bar (r12 = 751) on
    E:400 at tau_j = 1000 -- pileup, not structure. v2 wraps modulo t_max.
The v1 table is superseded in git history (its commit is named in RING_BRIEF.md).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

import numpy as np
from ripser import ripser
from persim import bottleneck

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.ringnet import coupling, heterogeneity, bump_init, gain, order_parameter, BETA  # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED                                # noqa: E402

C_CONTOUR = 2.9048e-02       # from stage1_contour_measured.json, used for E's coordinate
INSTRUMENT = Model("ring_ph_v2", [   # v2: scramble offset + jitter wrap
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("B", DECLARED, value=16, why="bumps per cloud, off-grid starts (undriven clouds)"),
    Param("seed_xi", DECLARED, value=1, why="same heterogeneity pattern as the other tables"),
    Param("gamma", DECLARED, value=0.02, why="odd-coupling drive; omega = gamma rad/tau "
                                             "(calibrated), one rotation per 314 tau"),
    Param("T_drive", DECLARED, value=1000.0, why="~3 rotations; 2000 bins at Delta=0.5"),
    Param("rho", DECLARED, value=50.0, why="spikes per tau per unit rate; ~800 spikes/tau "
                                          "population total, ~1 per unit per bin at the peak"),
    Param("bin", DECLARED, value=0.5, why="population-vector bin, tau"),
    Param("smooth_sigma", DECLARED, value=1.0, why="Gaussian smoothing of counts across bins, tau"),
    Param("n_points_max", DECLARED, value=600, why="random subsample fed to ripser; 2000-pt Rips "
                                                   "is fine singly, ~150 of them are not"),
    Param("R_MIN", DECLARED, value=3.0, why="r12 above this = H1 rank 1 detected; declared "
                                            "before the run, scored by verify_ring R9"),
    Param("B_E", DECLARED, value=4, why="bumps for the E clouds; spacing 2pi/4 = 1.57 rad "
                                        "exceeds the bump width so gaps can exist"),
    Param("W_E", TESTED, sweep=[100.0, 400.0], why="transient window for E; arc length "
                                                    "L = c*eps*W straddles the covering "
                                                    "condition L + w >= 2pi/B_E"),
    Param("q", TESTED, sweep=[1.0, 0.5, 0.25], why="top-q fraction by population activity "
                                                    "(di Sarra's load-bearing step)"),
    Param("tau_j", TESTED, sweep=[0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0],
          why="jitter ladder, tau; P1-P3 predict where r12 falls below R_MIN"),
    Param("seed_emit", TESTED, sweep=[11, 12, 13], why="Poisson emission / subsample seeds"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
TH = 2 * np.pi * np.arange(N) / N
W_EVEN = coupling(N, P["J0"].value, P["J1"].value)
W_ODD = P["J1"].value * np.sin(TH[:, None] - TH[None, :]) / N
XI = heterogeneity(N, P["seed_xi"].value)


# ── ring trajectories → rate matrix (n_t, N) ──────────────────────────────────
def simulate(eps, gamma, T_relax, T_sample, angles):
    W = W_EVEN + gamma * W_ODD
    h = eps * XI
    r = bump_init(N, np.asarray(angles))
    I0 = P["I0"].value
    for _ in range(int(round(T_relax / dt))):
        r += dt * (-r + gain(r @ W.T + I0 + h))
    n = int(round(T_sample / dt))
    out = np.empty((n, len(angles), N))
    for k in range(n):
        r += dt * (-r + gain(r @ W.T + I0 + h))
        out[k] = r
    return out                                   # (n_steps, B, N)


def cloud_rates(name):
    gam = P["gamma"].value
    B = P["B"].value
    offgrid = 2 * np.pi * (np.arange(B) + 0.37) / B
    if name == "A":
        R = simulate(0.0, gam, 50.0, P["T_drive"].value, [0.37])
    elif name == "B":
        R = simulate(0.1, gam, 50.0, P["T_drive"].value, [0.37])
    elif name == "C":
        R = simulate(0.0, 0.0, 50.0, P["T_drive"].value / B, offgrid)
    elif name == "D":
        R = simulate(0.1, 0.0, 2000.0, P["T_drive"].value / B, offgrid)
    elif name.startswith("E"):
        W_E = float(name.split(":")[1])
        B_E = P["B_E"].value
        R = simulate(0.1, 0.0, 100.0, W_E, 2 * np.pi * (np.arange(B_E) + 0.37) / B_E)
    else:
        raise ValueError(name)
    # concatenate bumps along time: (n_steps*B, N) -- each bump is its own segment
    n_steps, B_, _ = R.shape
    return R.transpose(1, 0, 2).reshape(B_ * n_steps, N), n_steps, B_


# ── spikes ────────────────────────────────────────────────────────────────────
def emit(rates, rng):
    """Poisson spikes per (step, unit); returns list of spike-time arrays per unit."""
    lam = P["rho"].value * rates * dt
    counts = rng.poisson(lam)                     # (n_t, N)
    spikes = []
    for i in range(N):
        idx = np.nonzero(counts[:, i])[0]
        reps = counts[idx, i]
        t = np.repeat(idx, reps) * dt + rng.random(reps.sum()) * dt
        spikes.append(np.sort(t))
    return spikes


def jitter(spikes, tau_j, rng, t_max):
    # wrap, never clip: clipping piles spikes at the window edges (v1 defect)
    return [np.sort(np.mod(s + rng.normal(0, tau_j, s.size), t_max)) for s in spikes]


def isi_scramble(spikes, rng, t_max):
    """Within-cell ISI-order scramble: marginal ISI distribution kept, sequence
    destroyed. v2: the rebuilt train gets a uniform random circular offset --
    anchoring at the first spike preserved onset order (v1 defect, cloud C)."""
    out = []
    for s in spikes:
        if s.size < 3:
            out.append(s); continue
        isi = np.diff(s); rng.shuffle(isi)
        t = np.concatenate([[0.0], np.cumsum(isi)]) + rng.random() * t_max
        out.append(np.sort(np.mod(t, t_max)))
    return out


# ── population vectors → PH ───────────────────────────────────────────────────
def popvecs(spikes, t_max):
    nb = int(np.ceil(t_max / P["bin"].value))
    X = np.zeros((nb, N))
    edges = np.arange(nb + 1) * P["bin"].value
    for i, s in enumerate(spikes):
        X[:, i] = np.histogram(s, bins=edges)[0]
    # gaussian smoothing along time (per unit)
    sig = P["smooth_sigma"].value / P["bin"].value
    k = np.arange(-int(4 * sig), int(4 * sig) + 1)
    ker = np.exp(-0.5 * (k / sig) ** 2); ker /= ker.sum()
    Xs = np.stack([np.convolve(X[:, i], ker, mode="same") for i in range(N)], 1)
    return Xs


def ph_stat(X, q, rng):
    act = X.sum(1)
    keep = np.argsort(act)[::-1][: max(20, int(q * len(act)))]
    Xq = X[keep]
    if len(Xq) > P["n_points_max"].value:
        Xq = Xq[rng.choice(len(Xq), P["n_points_max"].value, replace=False)]
    res = ripser(Xq, maxdim=1, do_cocycles=True)
    h1 = res["dgms"][1]
    pers = np.sort(h1[:, 1] - h1[:, 0])[::-1] if len(h1) else np.array([0.0])
    b1 = float(pers[0]) if len(pers) else 0.0
    b2 = float(pers[1]) if len(pers) > 1 else 1e-12
    return dict(r12=b1 / max(b2, 1e-12), b1=b1, b2=b2, n_h1=int(len(h1)),
                n_points=int(len(Xq))), h1


def main():
    t0 = time.time()
    rows = []
    base_dgm = {}
    clouds = ["A", "B", "C", "D"] + [f"E:{w:g}" for w in P["W_E"].sweep]
    for name in clouds:
        rates, n_steps, B_ = cloud_rates(name)
        t_max = rates.shape[0] * dt
        for seed in P["seed_emit"].sweep:
            rng = np.random.default_rng(seed)
            sp = emit(rates, rng)
            X = popvecs(sp, t_max)
            for q in P["q"].sweep:
                st, h1 = ph_stat(X, q, np.random.default_rng(seed + 1000))
                rows.append(dict(cloud=name, arm="base", q=q, seed=seed, tau_j=None, **st))
                if q == 0.5:
                    base_dgm[(name, seed)] = h1
            print(f"{name:<6} base   seeds/q done  r12(q=.5,seed={seed})="
                  f"{[r['r12'] for r in rows if r['cloud']==name and r['seed']==seed and r['q']==0.5][0]:.2f}")
            # jitter ladder (A, B, E2) at q=0.5
            if name in ("A", "B", f"E:{P['W_E'].sweep[-1]:g}"):
                for tj in P["tau_j"].sweep:
                    spj = jitter(sp, tj, rng, t_max)
                    st, h1 = ph_stat(popvecs(spj, t_max), 0.5, np.random.default_rng(seed + 1000))
                    st["bottleneck_to_base"] = float(bottleneck(base_dgm[(name, seed)], h1))
                    rows.append(dict(cloud=name, arm="jitter", q=0.5, seed=seed, tau_j=tj, **st))
                print(f"{name:<6} jitter seed={seed}: r12 by tau_j = "
                      + " ".join(f"{r['r12']:.1f}" for r in rows if r['cloud']==name and r['arm']=='jitter' and r['seed']==seed))
            # within-cell ISI-order scramble (A, B, C, E2) at q=0.5
            if name in ("A", "B", "C", f"E:{P['W_E'].sweep[-1]:g}"):
                sps = isi_scramble(sp, rng, t_max)
                st, h1 = ph_stat(popvecs(sps, t_max), 0.5, np.random.default_rng(seed + 1000))
                st["bottleneck_to_base"] = float(bottleneck(base_dgm[(name, seed)], h1))
                rows.append(dict(cloud=name, arm="scramble", q=0.5, seed=seed, tau_j=None, **st))
                print(f"{name:<6} scramble seed={seed}: r12={st['r12']:.2f}")

    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(),
               c_contour=C_CONTOUR, predictions_ref="RING_BRIEF.md 'Measure 2 — pre-registration' (a975089)",
               rows=rows, wall_s=round(time.time() - t0, 1), numpy=np.__version__)
    path = os.path.join(HERE, "stage1_ph_measured.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path} ({len(rows)} rows, {out['wall_s']}s)")


if __name__ == "__main__":
    main()
