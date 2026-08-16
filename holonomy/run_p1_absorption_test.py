"""Test of the P1 absorption upgrade (holonomy seal addendum ADD-7).
COMMITTED GENERATOR of holonomy/p1_absorption_test.json.

The amended prediction (trend + absorption) was derived parameter-free and
committed BEFORE this scoring runs.  Three tests, in increasing strength:

  T1 IN-SAMPLE RESCORE  — do the 15 sealed cells agree better?  A term that
     only helps the one violated cell and hurts others is not a term.
  T2 DIAL-INDEPENDENCE  — the derivation says the absorption depends on
     (n_full, n_W, deg, L) ONLY, so the trend-only residuals must be FLAT
     across the dial at fixed L.  This is the derivation's own falsifier.
  T3 OUT-OF-SAMPLE      — two dial values never measured (1.5, 3.0), fresh
     seeds, scored against both predictions.  Banked whichever way it lands.
"""

import hashlib
import json
import sys

import numpy as np
from scipy.stats import norm

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

SEAL = json.load(open(f"{ROOT}/holonomy/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/holonomy/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f}"

from transitions import gen_trended_set, p1_apply, sigma2_at        # noqa: E402
import predict_p1 as PP                                             # noqa: E402

P1 = SEAL["p1"]
K = SEAL["k_arc"]
MEAS = json.load(open(f"{ROOT}/holonomy/p1_measured.json"))
PRED = json.load(open(f"{ROOT}/holonomy/p1_prediction.json"))
ABS = json.load(open(f"{ROOT}/holonomy/p1_absorption.json"))
OUT = {}


def cellname(f):
    return f"L{f * P1['n_W']:.1f}"


# ── T1 in-sample rescore ────────────────────────────────────────────────────
print("T1 in-sample rescore (trend-only vs trend+absorption)", flush=True)
n_cells = len(P1["dials"]) * len(P1["L_fracs"])
zfam = float(norm.isf(2.0 * norm.sf(K) / (2.0 * n_cells)))
rows, z_old, z_new = {}, [], []
for dial in P1["dials"]:
    for f in P1["L_fracs"]:
        cn = cellname(f)
        cell = MEAS["synth"][f"dial{dial}"]["cells"][cn]
        p_tr = PRED["prediction"][f"dial{dial}"][cn]["delta_pred"]
        p_ab = ABS["rows"][cn]["delta_absorb"]
        zo = (cell["mean"] - p_tr) / cell["sem"]
        zn = (cell["mean"] - (p_tr + p_ab)) / cell["sem"]
        rows[f"dial{dial}|{cn}"] = dict(measured=cell["mean"],
                                        sem=cell["sem"], pred_trend=p_tr,
                                        pred_absorb=p_ab,
                                        z_trend_only=float(zo),
                                        z_amended=float(zn))
        z_old.append(abs(zo))
        z_new.append(abs(zn))
z_old, z_new = np.array(z_old), np.array(z_new)
OUT["T1"] = dict(z_fam=zfam, rows=rows,
                 max_z_trend_only=float(z_old.max()),
                 max_z_amended=float(z_new.max()),
                 n_pass_trend_only=int((z_old <= zfam).sum()),
                 n_pass_amended=int((z_new <= zfam).sum()),
                 mean_abs_z_trend_only=float(z_old.mean()),
                 mean_abs_z_amended=float(z_new.mean()),
                 improved=bool(z_new.mean() < z_old.mean()))
print(f"  cells passing: {OUT['T1']['n_pass_trend_only']}/{n_cells} -> "
      f"{OUT['T1']['n_pass_amended']}/{n_cells}; mean|z| "
      f"{z_old.mean():.2f} -> {z_new.mean():.2f}; max|z| "
      f"{z_old.max():.2f} -> {z_new.max():.2f}", flush=True)

# ── T2 dial-independence (the derivation's own falsifier) ──────────────────
print("T2 dial-independence of the trend-only residual", flush=True)
t2 = {}
for f in P1["L_fracs"]:
    cn = cellname(f)
    res = np.array([MEAS["synth"][f"dial{d}"]["cells"][cn]["mean"]
                    - PRED["prediction"][f"dial{d}"][cn]["delta_pred"]
                    for d in P1["dials"]])
    sems = np.array([MEAS["synth"][f"dial{d}"]["cells"][cn]["sem"]
                     for d in P1["dials"]])
    chi2 = float((((res - res.mean()) / sems) ** 2).sum())
    t2[cn] = dict(residuals=res.tolist(), sems=sems.tolist(),
                  mean=float(res.mean()),
                  predicted_constant=ABS["rows"][cn]["delta_absorb"],
                  chi2_flatness=chi2, dof=len(res) - 1,
                  flat=bool(chi2 <= 3 * (len(res) - 1)))
    print(f"  {cn}: residuals {np.round(res, 3).tolist()} vs predicted "
          f"constant {ABS['rows'][cn]['delta_absorb']:+.4f} | "
          f"flatness chi2={chi2:.1f}/{len(res) - 1}dof "
          f"flat={t2[cn]['flat']}", flush=True)
OUT["T2"] = dict(rows=t2, dial_independent=bool(all(v["flat"]
                                                    for v in t2.values())))

# ── T3 out-of-sample dials ─────────────────────────────────────────────────
print("T3 out-of-sample dials (1.5, 3.0), fresh seeds", flush=True)
OOS = [1.5, 3.0]
t3 = {}
for dial in OOS:
    ell = P1["n_W"] / dial
    dd = {f: [] for f in P1["L_fracs"]}
    for s in range(SEAL["p1_seeds"]):
        st = gen_trended_set(seed=90_000 + s, N=2048, n_keep=P1["n_full"],
                             a=P1["a"], ell=ell)
        A = p1_apply(st["x"], "unfold_then_window", P1["deg"], P1["n_W"])
        B = p1_apply(st["x"], "window_then_unfold", P1["deg"], P1["n_W"])
        Ls = [f * P1["n_W"] for f in P1["L_fracs"]]
        sA, sB = sigma2_at(A, Ls), sigma2_at(B, Ls)
        for f, a, b in zip(P1["L_fracs"], sA, sB):
            dd[f].append(a - b)
    # trend prediction at the new dial, from the SAME committed function
    u_full = np.linspace(0.0, P1["n_full"], 48001)
    x_of_u, _ = __import__("transitions").make_trend_maps(P1["a"], ell,
                                                          u_hi=P1["n_full"])
    x_full = x_of_u(u_full)
    lo, hi = (P1["n_full"] - P1["n_W"]) / 2.0, (P1["n_full"] + P1["n_W"]) / 2.0
    win = (u_full >= lo) & (u_full <= hi)
    cA = np.polyfit(x_full, u_full, P1["deg"])
    cB = np.polyfit(x_full[win], u_full[win] - lo, P1["deg"])
    phi_A = np.polyval(cA, x_full[win])
    phi_B = np.polyval(cB, x_full[win])
    for f in P1["L_fracs"]:
        L = f * P1["n_W"]
        cn = cellname(f)
        vA = PP.spurious_var(phi_A, u_full[win], L)
        vB = PP.spurious_var(phi_B, u_full[win], L)
        p_tr = vA - vB
        p_ab = ABS["rows"][cn]["delta_absorb"]
        d = np.array(dd[f])
        sem = float(d.std(ddof=1) / np.sqrt(len(d)))
        t3[f"dial{dial}|{cn}"] = dict(
            measured=float(d.mean()), sem=sem, pred_trend=float(p_tr),
            pred_amended=float(p_tr + p_ab),
            z_trend_only=float((d.mean() - p_tr) / sem),
            z_amended=float((d.mean() - p_tr - p_ab) / sem))
        r = t3[f"dial{dial}|{cn}"]
        print(f"  dial {dial} {cn}: meas {d.mean():+.4f}+-{sem:.4f} | "
              f"trend {p_tr:+.4f} (z={r['z_trend_only']:+.2f}) | amended "
              f"{p_tr + p_ab:+.4f} (z={r['z_amended']:+.2f})", flush=True)
zo3 = np.array([abs(v["z_trend_only"]) for v in t3.values()])
zn3 = np.array([abs(v["z_amended"]) for v in t3.values()])
zfam3 = float(norm.isf(2.0 * norm.sf(K) / (2.0 * len(t3))))
OUT["T3"] = dict(rows=t3, z_fam=zfam3,
                 n_pass_trend_only=int((zo3 <= zfam3).sum()),
                 n_pass_amended=int((zn3 <= zfam3).sum()), n_cells=len(t3),
                 mean_abs_z_trend_only=float(zo3.mean()),
                 mean_abs_z_amended=float(zn3.mean()),
                 improved=bool(zn3.mean() < zo3.mean()))
print(f"  out-of-sample: {OUT['T3']['n_pass_trend_only']}/{len(t3)} -> "
      f"{OUT['T3']['n_pass_amended']}/{len(t3)} passing; mean|z| "
      f"{zo3.mean():.2f} -> {zn3.mean():.2f}", flush=True)

OUT["verdict"] = dict(
    term_sign_confirmed=bool(all(
        ABS["rows"][cellname(f)]["delta_absorb"] > 0
        for f in P1["L_fracs"])),
    in_sample_improved=OUT["T1"]["improved"],
    dial_independent=OUT["T2"]["dial_independent"],
    out_of_sample_improved=OUT["T3"]["improved"])
json.dump(OUT, open(f"{ROOT}/holonomy/p1_absorption_test.json", "w"), indent=1)
print(f"VERDICT: {OUT['verdict']}", flush=True)
