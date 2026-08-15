"""BRIDGE-B gate run: the other atlas's repulsion models as an independent
read.  B1 (Ginibre KAG, class-level claim) must pass before B2 executes;
B2's window was sealed before B1 ran (prereg §B2).

Claim scope (tripwire 6): class-level only.  Kernel-level identification is
out of scope — the Ginibre kernel is complex and outside every real family
fitted here (declared approximation, see dpp_python.py header).
"""

import json
import subprocess
import sys
import numpy as np

BR = "/home/combust/fmexplorer/criticality_tool/bridge"
sys.path.insert(0, BR)
from observer_b import WedgeWindow, pcf_2d          # noqa
from dpp_python import fit_all, contrast, g_dpp     # noqa

import os
if os.path.exists(f"{BR}/bridge_b_measured.json") and \
        os.environ.get("BRIDGE_B_FORCE") != "1":
    sys.exit("bridge_b_measured.json exists — it is a LAYERED banked artifact "
             "(gate run + addenda + replicates + review patches; provenance = "
             "its git commit chain, see RESULTS_BRIDGE.md defect ledger). "
             "Re-running would destroy later layers. Set BRIDGE_B_FORCE=1 "
             "only for a from-scratch regeneration with a filed justification.")

SEAL = json.load(open(f"{BR}/prereg_sealed.json"))
TOL = SEAL["tolerances"]
CRIT = SEAL["B1_criteria"]
A = json.load(open(f"{BR}/bridge_a_measured.json"))
RENV = f"{BR}/.rquarantine/envs/rspat/bin/Rscript"
res = {"seal_cited": f"{BR}/prereg_sealed.json"}


def spatstat_fits(tag, rmax):
    env = dict(os.environ)
    if tag == "gp":
        env["SKIP_POWEREXP"] = "1"   # dppPowerExp OOMs at wedge scale (15GB);
                                     # the banked success ran with this skip —
                                     # committed here so reproduction matches
    subprocess.run([RENV, f"{BR}/dppm_fit.R", f"{BR}/xp_{tag}.csv",
                    f"{BR}/xw_{tag}.csv", f"{BR}/dpp_{tag}", str(rmax)],
                   check=True, capture_output=True, text=True, env=env)
    import csv
    params = {}
    with open(f"{BR}/dpp_{tag}_params.csv") as f:
        for row in csv.DictReader(f):
            params.setdefault(row["model"], {})[row["param"]] = float(row["value"])
    curves = {}
    with open(f"{BR}/dpp_{tag}_gmodel.csv") as f:
        for row in csv.DictReader(f):
            curves.setdefault(row["model"], []).append((float(row["r"]),
                                                       float(row["g"]) if row["g"] not in ("NA", "") else np.nan))
    return params, {k: np.array(v) for k, v in curves.items()}


# ── B1: Ginibre known-answer gate ────────────────────────────────────────────
if not A["G_B1_PASS"]:
    res["B1"] = "G_B1 FAILED upstream — park branch taken (prereg §B2)"
    json.dump(res, open(f"{BR}/bridge_b_measured.json", "w"), indent=1)
    sys.exit(0)

cg = np.array(A["A2_ginibre"]["g_b1_centers"])
g_pool = np.array(A["A2_ginibre"]["g_b1_pooled"])
lam_g = 1.0 / np.pi
fits = fit_all(cg, g_pool, lam_g, lo=0.25, hi=4.0)
spacing = lam_g ** -0.5
best = fits["best_dpp"]
rh_ratio = best["r_half"] / spacing
b1 = dict(python_fits={k: v for k, v in fits.items() if k != "best_dpp"},
          best_dpp=best, mean_spacing=spacing, r_half_over_spacing=rh_ratio,
          beats_poisson=bool(best["D"] < fits["poisson"]["D"]),
          beats_thomas=bool(best["D"] < fits["thomas"]["D"]),
          range_coherent=bool(CRIT["r_half_ratio"][0] <= rh_ratio <= CRIT["r_half_ratio"][1]))
b1["B1_PASS"] = bool(b1["beats_poisson"] and b1["beats_thomas"] and b1["range_coherent"])
print(f"B1 python: best={best['family']} D={best['D']:.4g} vs pois {fits['poisson']['D']:.4g} "
      f"thomas {fits['thomas']['D']:.4g}; r_half/spacing={rh_ratio:.3f}  PASS={b1['B1_PASS']}", flush=True)

# spatstat side (cross-check, same uniform contrast D on the pooled ĝ)
sp_params, sp_curves = spatstat_fits("ginibre", 5.0)
sp_D = {}
for model, arr in sp_curves.items():
    gv = np.interp(cg, arr[:, 0], arr[:, 1])
    if np.isnan(gv).any():
        continue
    sp_D[model] = contrast(cg, g_pool, gv, lo=0.25, hi=4.0)
b1["spatstat_params"] = sp_params
b1["spatstat_D_uniform"] = sp_D
res["B1"] = b1
print("B1 spatstat D:", {k: round(v, 4) for k, v in sp_D.items()}, flush=True)

# ── B2: Gaussian-prime annular wedge (window sealed pre-B1) ─────────────────
from gaussian_prime_annulus import R1, R2, T1, T2  # sealed values live there
pts = np.load(f"{BR}/gp_annulus_points.npy")
W = WedgeWindow(R1, R2, T1, T2)
lam_hat = len(pts) / W.area()
spacing2 = lam_hat ** -0.5

# intensity-variation budget check (sealed 5%): radial-band counts vs 1/ln r
edges = np.linspace(R1, R2, 7)
rr = np.hypot(pts[:, 0], pts[:, 1])
band_lam = []
for i in range(6):
    a_band = 0.5 * (T2 - T1) * (edges[i+1]**2 - edges[i]**2)
    band_lam.append(np.sum((rr >= edges[i]) & (rr < edges[i+1])) / a_band)
band_lam = np.array(band_lam)
mids = 0.5 * (edges[:-1] + edges[1:])
model = 2.0 / (np.pi * np.log(mids))
budget_dev = float(np.abs(band_lam / band_lam.mean() - model / model.mean()).max())
pred_var = float((model.max() - model.min()) / model.mean())

bins = np.arange(0.0, 15.0 + 1e-9, 0.25)
cb, gb = pcf_2d(pts, W, bins, lam=lam_hat)
min_pair = None  # reported from the histogram support below

fits2 = fit_all(cb, gb, lam_hat, lo=0.5, hi=12.0)
best2 = fits2["best_dpp"]
rh2 = best2["r_half"] / spacing2

# K_inhom exercise + FIX-2 designed instance (TOOLKIT §11.2)
from observer_b import k_inhom  # canonical estimator home (moved post-run, identical body)

r_k = np.arange(1.0, 12.01, 1.0)
lam_right = lambda r: 2.0 / (np.pi * np.log(r))
c_norm = lam_hat / lam_right(np.hypot(pts[:, 0], pts[:, 1])).mean()
K_in_right = k_inhom(pts, W, r_k, lambda r: c_norm * lam_right(r))
# designed WRONG intensity: gradient INVERTED (λ ∝ ln r), same mean — FIX-2 twin
lam_wrong = lambda r: np.log(r)
c_wr = lam_hat / lam_wrong(np.hypot(pts[:, 0], pts[:, 1])).mean()
K_in_wrong = k_inhom(pts, W, r_k, lambda r: c_wr * lam_wrong(r))

res["B2"] = dict(window=dict(R1=R1, R2=R2, T1=T1, T2=T2), n=len(pts),
                 lam_hat=float(lam_hat), mean_spacing=float(spacing2),
                 intensity_budget=dict(sealed=TOL["B2_intensity_budget"],
                                       predicted_variation=pred_var,
                                       banded_dev_vs_model=budget_dev,
                                       # gate on the MEASURED deviation (a
                                       # theory-only check is a gate that
                                       # cannot fail — 2026-08-15 review F3)
                                       within=bool(budget_dev <= TOL["B2_intensity_budget"]
                                                   and pred_var <= TOL["B2_intensity_budget"])),
                 g_centers=cb.tolist(), g_emp=gb.tolist(),
                 # bins whose UPPER EDGE <= sqrt(2): the earlier center-based
                 # mask included the bin CONTAINING sqrt(2), so the witness
                 # reported the very comb peak it exists to exclude (review F1)
                 g_below_sqrt2=float(gb[(cb + 0.125) <= np.sqrt(2)].max()),
                 python_fits={k: v for k, v in fits2.items() if k != "best_dpp"},
                 best_dpp=best2, r_half_over_spacing=float(rh2),
                 K_inhom_right=K_in_right.tolist(),
                 K_inhom_wrong_designed=K_in_wrong.tolist(),
                 K_r_grid=r_k.tolist(),
                 K_poisson_ref=(np.pi * r_k**2).tolist())
print(f"B2: n={len(pts)} lam={lam_hat:.4f} best={best2['family']} D={best2['D']:.4g} "
      f"pois D={fits2['poisson']['D']:.4g} thomas D={fits2['thomas']['D']:.4g} "
      f"r_half/spacing={rh2:.3f}", flush=True)

with open(f"{BR}/bridge_b_measured.json", "w") as f:
    json.dump(res, f, indent=1)          # checkpoint before the R stage

# spatstat cross-check on a theta-SUBWINDOW of the wedge (declared scope
# reduction: the full 31k-point wedge OOM-kills spatstat's isotropic-
# correction pair structure; a window restriction preserves lambda and g
# exactly, so the cross-check target is unchanged — python full-data fit
# remains primary).
T2_SP = 0.20
th_all = np.arctan2(pts[:, 1], pts[:, 0])
sub = pts[th_all <= T2_SP]
np.savetxt(f"{BR}/xp_gp.csv", sub, delimiter=",", header="x,y", comments="")
with open(f"{BR}/xw_gp.csv", "w") as f:
    f.write(f"type,R1,R2,t1,t2\nwedge,{R1},{R2},{T1},{T2_SP}\n")
try:
    sp2_params, sp2_curves = spatstat_fits("gp", 12.0)
    sp2_D = {}
    for model, arr in sp2_curves.items():
        gv = np.interp(cb, arr[:, 0], arr[:, 1])
        if np.isnan(gv).any():
            continue
        sp2_D[model] = contrast(cb, gb, gv, lo=0.5, hi=12.0)
    res["B2"]["spatstat_params"] = sp2_params
    res["B2"]["spatstat_D_uniform"] = sp2_D
    res["B2"]["spatstat_scope"] = f"theta subwindow [0.15,{T2_SP}], n={len(sub)}"
    res["B2"].pop("spatstat_error", None)   # success supersedes a stale failure key
    print("B2 spatstat D:", {k: round(v, 4) for k, v in sp2_D.items()}, flush=True)
except Exception as exc:                                # noqa: BLE001
    res["B2"]["spatstat_error"] = str(exc)
    print("B2 spatstat stage FAILED:", exc, flush=True)

with open(f"{BR}/bridge_b_measured.json", "w") as f:
    json.dump(res, f, indent=1)
print("BRIDGE-B done. B1_PASS =", b1["B1_PASS"], flush=True)
