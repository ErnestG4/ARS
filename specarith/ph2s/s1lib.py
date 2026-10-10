"""PH2S Stage 1 library: the shrink statistic on any bin, for zeros windows and mapped long-GUE sequences, and the arms'
verdict rules (PH2S_SEAL_DRAFT §§2–3). Reuses the sealed R₂ code's generic functions (imported, not modified):
g0b.contributions, g0b.boot_sd_sum, g0b.nbar_inv, r2prep.nbar / f_raw / FAMILY / U_MAX, r2run.expected_contribution,
r2run.read_platt_heights.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ph2r2"))
import g0b as G          # noqa: E402
import r2prep as P       # noqa: E402
import r2run as RR       # noqa: E402

PRIMARY = (0.5, 0.3)
FAMILY = list(P.FAMILY)
B_SHORT, B_LONG = 100, 10_000
BOOT_B = 400
L_PRIMARY, L_SECONDARY = 1_000_000, 200_000
# F1 (ph2r2/FRESH_SETS_F1_F3.md v2): five core bins (arms A–C) + the extreme for arm D
F1 = {"F1a": ("zeros_10946000.dat", 10_946_000, 13_046_000),
      "F1b": ("zeros_31946000.dat", 31_946_000, 34_046_000),
      "F1c": ("zeros_319646000.dat", 319_646_000, 321_746_000),
      "F1d": ("zeros_1438946000.dat", 1_438_946_000, 1_441_046_000),
      "F1e": ("zeros_13660946000.dat", 13_660_946_000, 13_663_046_000),
      "F1x": ("zeros_24891746000.dat", 24_891_746_000, 24_893_846_000)}
CORE = ("F1a", "F1b", "F1c", "F1d", "F1e")
R = {n: (RR.PLATT[n], *P.BINS[n]) for n in P.BINS}          # seen R₂ bins (dry run / sensitivity only)


def geometry(t0, t1):
    tc = 0.5 * (t0 + t1)
    return dict(t0=float(t0), t1=float(t1), tc=tc, L_c=math.log(tc / P.TWO_PI), delta=P.TWO_PI / math.log(tc / P.TWO_PI),
                n_zeros=float(P.nbar(t1) - P.nbar(t0)))


def bin_geometry(name):
    _, t0, t1 = (F1 if name in F1 else R)[name]
    return geometry(t0, t1)


def drift_removed(c, levels, g, u, w):
    """R₂ A3 on an arbitrary bin: c̃_i = c_i·e(t_c)/e(t_i), e on a 257-point grid across [t0, t1)."""
    grid = np.linspace(g["t0"], g["t1"], 257)
    e = RR.expected_contribution(grid, u, w, g["delta"])
    ec = float(RR.expected_contribution(g["tc"], u, w, g["delta"])[0])
    return c * (ec / np.interp(levels, grid, e))


def growth(levels, g, u, w, seed):
    """Drift-removed g = SD_MBB(10⁴)/SD_MBB(100) of the window's per-level contributions (one window). seed: a tuple,
    unique per (arm, sequence/window, bin, member) — independent bootstraps (the longbase v1 lesson)."""
    c = G.contributions(levels, u, w, g["delta"])
    cd = drift_removed(c, levels, g, u, w)
    rng = np.random.default_rng(list(seed))
    s_short = G.boot_sd_sum(cd, B_SHORT, rng, BOOT_B)
    s_long = G.boot_sd_sum(cd, B_LONG, rng, BOOT_B)
    return s_long / s_short


def growth_raw(levels, g, u, w, seed):
    c = G.contributions(levels, u, w, g["delta"])
    rng = np.random.default_rng(list(seed))
    return G.boot_sd_sum(c, B_LONG, rng, BOOT_B) / G.boot_sd_sum(c, B_SHORT, rng, BOOT_B)


def map_gue(u_levels, g):
    """Unit-density GUE levels (starting at 0) onto the bin's ζ heights: t = N̄⁻¹(N̄(t0) + ½ + u)."""
    return G.nbar_inv(float(P.nbar(g["t0"])) + 0.5 + u_levels, g["tc"])


def zero_windows(path, L):
    lev = RR.read_platt_heights(path)
    return [lev[k * L:(k + 1) * L] for k in range(len(lev) // L)]


def mean_se(v):
    v = np.asarray(v, float)
    if len(v) < 2:
        return float(v.mean()) if len(v) else float("nan"), math.inf
    return float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v)))


Phi = lambda z: 0.5 * math.erfc(-z / math.sqrt(2))


# ---------------------------------------------------------------- verdict rules (precision-only guards)
def bin_shrink(gB, seB, gZ, seZ, d_ref):
    d = gB - gZ
    se = math.sqrt(seB ** 2 + seZ ** 2)
    nr = (not math.isfinite(se)) or 3 * se >= d_ref          # achieved precision guard: never reads where d landed
    return dict(d=d, se=se, SHRINK=bool((not nr) and d > 3 * se), NOT_RESOLVABLE_achieved=bool(nr))


def arm_count(bins, resolvable):
    """A/B: PASS iff ≥ 4 of the 5 core bins shrink; NOT RESOLVABLE if fewer than 4 core bins are resolvable (pre-data
    or achieved)."""
    ok = [b for b in CORE if resolvable[b] and not bins[b]["NOT_RESOLVABLE_achieved"]]
    if len(ok) < 4:
        return "NOT RESOLVABLE"
    return "PASS" if sum(bins[b]["SHRINK"] for b in CORE) >= 4 else "FAIL"


def arm_width(d_by_member, se_by_member):
    """C: Δ_u = mean over core bins of d(u, 0.3) − d(u, 0.15); PASS iff Δ_u > 0 for ≥ 3 of 4 u and mean_u Δ_u > 2·SE."""
    Ds, Vs = [], []
    for u in (0.5, 1.0, 1.5, 2.0):
        a, b = f"{u}_0.3", f"{u}_0.15"
        diff = [d_by_member[a][n] - d_by_member[b][n] for n in CORE]
        var = [se_by_member[a][n] ** 2 + se_by_member[b][n] ** 2 for n in CORE]
        Ds.append(float(np.mean(diff)))
        Vs.append(float(np.sum(var)) / len(CORE) ** 2)
    m, se = float(np.mean(Ds)), math.sqrt(float(np.sum(Vs))) / 4
    verdict = "PASS" if (sum(x > 0 for x in Ds) >= 3 and m > 2 * se) else "FAIL"
    return dict(delta_u=Ds, mean=m, se=se, verdict=verdict)


def arm_height(Ls, ds, ses):
    """D: weighted least squares of d on L; PASS iff slope + 2·SE(slope) < 0."""
    Ls, ds, w = np.asarray(Ls), np.asarray(ds), 1 / np.asarray(ses) ** 2
    Lb = np.sum(w * Ls) / np.sum(w)
    sxx = np.sum(w * (Ls - Lb) ** 2)
    slope = float(np.sum(w * (Ls - Lb) * (ds - np.sum(w * ds) / np.sum(w))) / sxx)
    se = float(1 / math.sqrt(sxx))
    return dict(slope=slope, se=se, verdict="PASS" if slope + 2 * se < 0 else "FAIL")
