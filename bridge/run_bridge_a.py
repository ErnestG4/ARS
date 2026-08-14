"""BRIDGE-A gate run: shared calibrators through BOTH dialects.

Runs ONLY after bridge/prereg_sealed.json exists; every tolerance is read from
the seal, never typed here (tripwire 4).  Gate seeds are disjoint from the
pilot seeds (see pilot_tolerances.py header).

Transitions used on each path (tripwire 1 — one per path):
  zeta:    Riemann–von Mangoldt unfold (arsrh/phase1_zeta_crossover.py:61,
           reused by import) → stationary estimators.
  Poisson / Ginibre / GUE calibrators: already stationary → no transition.
"""

import json
import subprocess
import sys
import numpy as np

BR = "/home/combust/fmexplorer/criticality_tool/bridge"
sys.path.insert(0, BR)
sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool")
from observer_b import (k_1d, pcf_1d, sigma2_from_g_1d, sigma2_direct_1d,
                        RectWindow, DiskWindow,
                        k_2d, pcf_2d, sigma2_from_g_2d, disk_counts_grid)  # noqa
from ginibre_sampler import sample_ginibre, central_points                    # noqa
from universality import compute_nns, number_variance, pair_correlation       # noqa
from arsrh.phase1_zeta_crossover import unfold_zeta                           # noqa

SEAL = json.load(open(f"{BR}/prereg_sealed.json"))
TOL = SEAL["tolerances"]
res = {"seal_cited": f"{BR}/prereg_sealed.json"}

RENV = f"{BR}/.rquarantine/envs/rspat/bin/Rscript"


def rtilde(u):
    s = np.diff(np.sort(u))
    r = np.minimum(s[1:], s[:-1]) / np.maximum(s[1:], s[:-1])
    return float(r.mean())


# ── A1: 1-D pair ─────────────────────────────────────────────────────────────
r1 = np.arange(0.25, 5.01, 0.25)
bins1 = np.arange(0.0, 25.0 + 1e-9, 0.05)
L_LIST = [2.0, 5.0, 10.0, 20.0]

a1p = []
for s in (1, 2, 3):
    rng = np.random.default_rng(s)
    e = np.sort(rng.uniform(0, 100_000, 100_000))
    K = k_1d(e, r1, lam=1.0)
    c, g = pcf_1d(e, bins1, lam=1.0)
    m = c >= 0.25
    glue = []
    direct_v = sigma2_direct_1d(e, L_LIST)   # home semantics, fast (exact-equal)
    for L, dv in zip(L_LIST, direct_v):
        ident = sigma2_from_g_1d(c, g, L, lam=1.0)
        glue.append(dict(L=L, identity=float(ident), direct=float(dv),
                         rel=abs(ident - dv) / dv))
    a1p.append(dict(seed=s, devK=float(np.abs(K - 2 * r1).max()),
                    devg=float(np.abs(g[m] - 1.0).max()), glue=glue))
    print(f"A1 poisson seed {s} done", flush=True)
res["A1_poisson"] = a1p
res["G_A1_1d_PASS"] = bool(all(r_["devK"] <= TOL["G_A1_1d_K"] and r_["devg"] <= TOL["G_A1_1d_g"] for r_ in a1p))
res["G_A3_1d_pois_PASS"] = bool(all(gl["rel"] <= TOL["G_A3_1d_rel"] for r_ in a1p for gl in r_["glue"]))

# zeta window (primary GUE-class 1-D substrate, pre-step P2)
gam = np.loadtxt("/home/combust/fmexplorer/criticality_tool/data/odlyzko_zeros1.txt")
u = unfold_zeta(gam)                      # ONE transition on this path
c, g = pcf_1d(u, bins1)                   # lam from data span (≈1 after unfold)
m = (c >= 0.25) & (c <= 5.0)
sinc = np.sin(np.pi * c[m]) / (np.pi * c[m])
gue_dev = float(np.abs(g[m] - (1.0 - sinc**2)).max())
nns = compute_nns(u)
direct_z = sigma2_direct_1d(u, L_LIST)       # home semantics, fast (exact-equal)
# analytic reference curves are data-independent — pull them from the home
# harness on a dummy array (owner: universality.py number_variance docstring)
nv_ref = number_variance(np.arange(200, dtype=float), L_max=20.0, n_L=40)
glue_z = []
for L, dv in zip(L_LIST, direct_z):
    ident = sigma2_from_g_1d(c, g, L)
    glue_z.append(dict(L=L, identity=float(ident), direct=float(dv),
                       rel=abs(ident - dv) / dv))
res["A1_zeta"] = dict(n=len(u), gue_pcf_maxdev=gue_dev,
                      rtilde=rtilde(u),
                      ks_gue=float(nns.ks_gue), ks_poisson=float(nns.ks_poisson),
                      sigma2_L20_direct=float(direct_z[-1]),
                      sigma2_L20_gue_ref=float(np.interp(20.0, nv_ref["L"], nv_ref["gue"])),
                      glue=glue_z,
                      K_obsB=k_1d(u, r1).tolist())
res["G_A2_PASS"] = bool(gue_dev <= TOL["G_A2_gue_pcf"])
# Gate restricted to L<=5 (sealed): rigid substrates amplify identity noise
# by L^2/Sigma^2(L); L in {10,20} reported descriptively (seal G_A3 text).
res["G_A3_1d_zeta_PASS"] = bool(all(gl["rel"] <= TOL["G_A3_1d_gue_rel"][str(gl["L"])]
                                    for gl in glue_z if gl["L"] <= 5.0))
print(f"A1 zeta done: gue_pcf_maxdev={gue_dev:.4f} (tol {TOL['G_A2_gue_pcf']:.4f})", flush=True)

# ── A2: 2-D pair ─────────────────────────────────────────────────────────────
r2 = np.arange(0.25, 5.01, 0.25)
bins2 = np.arange(0.0, 5.0 + 1e-9, 0.1)
a2p = []
for s in (1, 2, 3):
    rng = np.random.default_rng(s)
    W = RectWindow(120.0, 120.0)
    n = rng.poisson(W.area())
    pts = rng.uniform(0, 120.0, size=(n, 2))
    K = k_2d(pts, W, r2, lam=1.0)
    L = np.sqrt(K / np.pi)
    c2, g2 = pcf_2d(pts, W, bins2, lam=1.0)
    m2 = c2 >= 0.25
    a2p.append(dict(seed=s, devL=float(np.abs(L - r2).max()),
                    devg=float(np.abs(g2[m2] - 1.0).max())))
    if s == 1:
        np.savetxt(f"{BR}/xp_pois2d.csv", pts, delimiter=",", header="x,y", comments="")
        our_K_pois = K
    print(f"A2 poisson seed {s} done", flush=True)
res["A2_poisson"] = a2p
res["G_A1_2d_PASS"] = bool(all(r_["devL"] <= TOL["G_A1_2d_L"] and r_["devg"] <= TOL["G_A1_2d_g"] for r_ in a2p))

# 2-D gluing gate (G-A3 2d): Poisson + Thomas designed instance, pooled
# grid-count direct variance vs identity on seed-averaged ĝ (pilot-4 config).
R_LIST = [2.0, 4.0, 6.0]
gl_bins = np.arange(0.0, 12.5 + 1e-9, 0.1)

def gluing_2d(tag, sampler, seeds, lam_true):
    # TRUE model intensity throughout (pilot-4 lesson): lambda-hat jitter is
    # amplified by (lam*pi*R^2)^2/Var in the identity — FIX-2 twin at the
    # gluing level; filed in TRANSLATION_TABLE row 4/5 and TOOLKIT §11.2.
    gs, lams = [], []
    counts = {R: [] for R in R_LIST}
    for s in seeds:
        pts, W = sampler(s)
        lam = lam_true
        lams.append(lam)
        cgl, ggl = pcf_2d(pts, W, gl_bins, lam=lam)
        gs.append(ggl)
        for R in R_LIST:
            counts[R].extend(disk_counts_grid(pts, W, R))
        print(f"A2 gluing {tag} seed {s} done", flush=True)
    g_pool = np.mean(gs, axis=0)
    lam_m = float(np.mean(lams))
    rows = []
    for R in R_LIST:
        cnt = np.array(counts[R])
        direct = float(cnt.var(ddof=1))
        ident = float(sigma2_from_g_2d(cgl, g_pool, R, lam_m))
        rows.append(dict(R=R, identity=ident, direct=direct, n_ind=len(cnt),
                         rel=abs(ident - direct) / direct))
    return rows

def _pois2d(s):
    rng = np.random.default_rng(s)
    W = RectWindow(120.0, 120.0)
    return rng.uniform(0, 120.0, size=(rng.poisson(W.area()), 2)), W

def _thomas(s):
    rng = np.random.default_rng(s)
    W = RectWindow(120.0, 120.0)
    KAPPA, MU, SIG = 0.05, 20, 1.5
    buf = 5 * SIG
    par = rng.uniform(-buf, 120 + buf,
                      size=(rng.poisson(KAPPA * (120 + 2 * buf) ** 2), 2))
    n_off = rng.poisson(MU, size=len(par))
    pts = np.concatenate([p + SIG * rng.standard_normal((k, 2))
                          for p, k in zip(par, n_off)])
    return pts[W.contains(pts)], W

res["A2_glue_pois"] = gluing_2d("pois", _pois2d, (1, 2, 3, 4, 5, 6), 1.0)
res["A2_glue_thomas"] = gluing_2d("thomas", _thomas,
                                  (310, 311, 312, 313, 314, 315), 1.0)  # kappa*mu
# Gated at R=2 only (sealed; pilot-4: identity error grows ~(lam*pi*R^2)^2/Var
# from the irreducible pcf baseline offset); R in {4,6} descriptive.
res["G_A3_2d_PASS"] = bool(
    all(r_["rel"] <= TOL["G_A3_2d_pois_rel"]
        for r_ in res["A2_glue_pois"] if r_["R"] <= 2.0) and
    all(r_["rel"] <= TOL["G_A3_2d_thomas_rel"]
        for r_ in res["A2_glue_thomas"] if r_["R"] <= 2.0))
print("G_A3_2d:", res["G_A3_2d_PASS"], flush=True)

# Ginibre gate ensemble
N = 2048
GIN_SEEDS = list(range(920, 932))
b1_bins = np.arange(0.0, 4.0 + 1e-9, 0.1)     # G-B1 config (pilot-3)
gs_b1, gs_gl, lam = [], [], 1.0 / np.pi
counts_gin = {R: [] for R in R_LIST}
for s in GIN_SEEDS:
    ev = sample_ginibre(N, s)
    pts, R = central_points(ev, N)
    W = DiskWindow(R)
    cb1, gb1 = pcf_2d(pts, W, b1_bins, lam=lam)
    gs_b1.append(gb1)
    cgl, ggl = pcf_2d(pts, W, gl_bins, lam=lam)
    gs_gl.append(ggl)
    for Rd in R_LIST:
        counts_gin[Rd].extend(disk_counts_grid(pts, W, Rd))
    if s == 920:
        np.savetxt(f"{BR}/xp_ginibre.csv", pts, delimiter=",", header="x,y", comments="")
        gin_window_R = R
        our_K_gin = k_2d(pts, W, r2, lam=lam)
    print(f"A2 ginibre seed {s} done", flush=True)
g_b1 = np.mean(gs_b1, axis=0)
mg = cb1 >= 0.25
dev_b1 = g_b1[mg] - (1.0 - np.exp(-cb1[mg]**2))
gin_rms = float(np.sqrt((dev_b1**2).mean()))
gin_max = float(np.abs(dev_b1).max())
# descriptive gluing row (class-I noise amplification documented in seal)
g_glp = np.mean(gs_gl, axis=0)
glue_gin = []
for Rd in R_LIST:
    cnt = np.array(counts_gin[Rd])
    direct = float(cnt.var(ddof=1))
    ident = float(sigma2_from_g_2d(cgl, g_glp, Rd, lam))
    amp = (lam * np.pi * Rd**2) / max(direct, 1e-9)
    glue_gin.append(dict(R=Rd, identity=ident, direct=direct, n_ind=len(cnt),
                         rel=abs(ident - direct) / direct,
                         noise_amplification=float(amp)))
res["A2_ginibre"] = dict(N=N, n_seeds=len(GIN_SEEDS),
                         pcf_rms_dev=gin_rms, pcf_max_abs_dev=gin_max,
                         glue_descriptive=glue_gin,
                         g_b1_centers=cb1.tolist(), g_b1_pooled=g_b1.tolist())
res["G_B1_PASS"] = bool(gin_rms <= TOL["G_B1_ginibre_pcf_rms"])
print(f"A2 ginibre pooled: pcf RMS dev={gin_rms:.4f} (tol {TOL['G_B1_ginibre_pcf_rms']:.4f}), "
      f"max={gin_max:.4f}", flush=True)

# ── spatstat cross-check (Observer B via the other atlas's own code) ─────────
with open(f"{BR}/xw_pois2d.csv", "w") as f:
    f.write("type,x0,x1,y0,y1\nrect,0,120,0,120\n")
with open(f"{BR}/xw_ginibre.csv", "w") as f:
    f.write(f"type,R\ndisk,{gin_window_R}\n")
xc = {}
for tag in ("pois2d", "ginibre"):
    subprocess.run([RENV, f"{BR}/spatstat_xcheck.R", f"{BR}/xp_{tag}.csv",
                    f"{BR}/xw_{tag}.csv", f"{BR}/xout_{tag}", "5.0"],
                   check=True, capture_output=True, text=True)
    Kcsv = np.genfromtxt(f"{BR}/xout_{tag}_K.csv", delimiter=",", names=True)
    ours = our_K_pois if tag == "pois2d" else our_K_gin
    theirs = np.interp(r2, Kcsv["r"], Kcsv["K_border"])
    mrel = (r2 >= 1.0)
    xc[tag] = float(np.abs((theirs[mrel] - ours[mrel]) / ours[mrel]).max())
    print(f"xcheck {tag}: max rel dev ours-vs-spatstat(border) = {xc[tag]:.4f}", flush=True)
res["spatstat_xcheck_maxrel"] = xc
res["XCHECK_PASS"] = bool(all(v <= TOL["XCHECK_rel"] for v in xc.values()))

with open(f"{BR}/bridge_a_measured.json", "w") as f:
    json.dump(res, f, indent=1)
print("BRIDGE-A GATES:", {k: v for k, v in res.items() if k.endswith("_PASS")}, flush=True)
