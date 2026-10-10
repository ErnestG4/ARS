"""PH2S Stage 1 pre-read (PH2S_SEAL_DRAFT §4), no F1 zero read.

  python s1preread.py baseline GUEDIR OUT BIN SEED     one GUE seed mapped onto BIN (F1a..F1x or R1..R5): growth for all
                                                        8 members at L = 10⁶, the primary at L = 2·10⁵; also raw growth
                                                        (no drift removal) for the primary at 10⁶ (red path)
  python s1preread.py seen OUT BIN                      seen R zeros (R1..R5) in disjoint windows, same quantities
  python s1preread.py analyse OUT                       d_ref, per-bin power / resolvability, GUE-vs-GUE specificity,
                                                        seen-R sensitivity (dry run of arms A–D), drift red path, guard
                                                        witness -> OUT/preread.json
Bootstrap seeds: (arm 1 = GUE / 2 = zeros, seed or window, L, bin index, member index), all independent.
"""
import glob
import json
import math
import os
import sys

import numpy as np

import s1lib as S

BIN_IDX = {n: i for i, n in enumerate(list(S.F1) + list(S.R))}
MEM_IDX = {f"{u}_{w}": i for i, (u, w) in enumerate(S.FAMILY)}
PK = f"{S.PRIMARY[0]}_{S.PRIMARY[1]}"


def quantities(levels_by_L, g, name, arm, idx):
    out = {"1000000": {}, "200000": {}}
    for L, lev in levels_by_L.items():
        members = S.FAMILY if L == S.L_PRIMARY else [S.PRIMARY]
        for u, w in members:
            k = f"{u}_{w}"
            out[str(L)][k] = S.growth(lev, g, u, w, (arm, idx, L, BIN_IDX[name], MEM_IDX[k]))
    out["raw_primary_1000000"] = S.growth_raw(levels_by_L[S.L_PRIMARY], g, *S.PRIMARY,
                                              (arm + 10, idx, S.L_PRIMARY, BIN_IDX[name], 0))
    return out


def baseline(guedir, out, name, seed):
    g = S.bin_geometry(name)
    lev = {L: S.map_gue(np.load(os.path.join(guedir, f"gue_L{L}_s{seed:03d}.npy")), g) for L in (S.L_PRIMARY, S.L_SECONDARY)}
    rec = dict(bin=name, seed=seed, **quantities(lev, g, name, 1, seed))
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, f"base_{name}_s{seed:03d}.json"), "w"), indent=1)


def seen(out, name):
    g = S.bin_geometry(name)
    path = os.path.join(S.HERE, "..", "ph2r2", "data", "platt", S.R[name][0])
    W = {L: S.zero_windows(path, L) for L in (S.L_PRIMARY, S.L_SECONDARY)}
    recs = []
    for k in range(max(len(W[L]) for L in W)):
        lev = {L: W[L][k] for L in W if k < len(W[L])}
        q = {"1000000": {}, "200000": {}}
        for L, x in lev.items():
            for u, w in (S.FAMILY if L == S.L_PRIMARY else [S.PRIMARY]):
                q[str(L)][f"{u}_{w}"] = S.growth(x, g, u, w, (2, k, L, BIN_IDX[name], MEM_IDX[f"{u}_{w}"]))
        recs.append(dict(window=k, **q))
    os.makedirs(out, exist_ok=True)
    json.dump(recs, open(os.path.join(out, f"seen_{name}.json"), "w"), indent=1)


def load_base(out, name, seeds=None):
    recs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(out, f"base_{name}_s*.json")))]
    return [r for r in recs if seeds is None or r["seed"] in seeds]


def col(recs, L, k):
    return [r[str(L)][k] for r in recs if k in r[str(L)]]


def evaluate(core, zeros_vals, base_vals, d_ref, resolvable, Lbins):
    """zeros_vals / base_vals: {bin: {L: {member: [values]}}}. Returns arms A–D."""
    res = {}
    for L, arm in ((S.L_PRIMARY, "A"), (S.L_SECONDARY, "B")):
        bins = {}
        for n in zeros_vals:
            gZ, seZ = S.mean_se(zeros_vals[n][L][PK])
            gB, seB = S.mean_se(base_vals[n][L][PK])
            bins[n] = dict(gZ=gZ, seZ=seZ, gB=gB, seB=seB, **S.bin_shrink(gB, seB, gZ, seZ, d_ref[str(L)]))
        res[arm] = dict(bins=bins, verdict=arm_count(core, bins, resolvable[str(L)]))
    dm = {k: {} for k in MEM_IDX}
    sm = {k: {} for k in MEM_IDX}
    for k in MEM_IDX:
        for n in core:
            gZ, seZ = S.mean_se(zeros_vals[n][S.L_PRIMARY][k])
            gB, seB = S.mean_se(base_vals[n][S.L_PRIMARY][k])
            dm[k][n], sm[k][n] = gB - gZ, math.sqrt(seB ** 2 + seZ ** 2)
    res["C"] = arm_width(core, dm, sm)
    ds = [res["A"]["bins"][n]["d"] for n in Lbins]
    ses = [res["A"]["bins"][n]["se"] for n in Lbins]
    res["D"] = S.arm_height([S.bin_geometry(n)["L_c"] for n in Lbins], ds, ses)
    return res


def arm_count(core, bins, resolvable):
    ok = [b for b in core if resolvable.get(b, True) and not bins[b]["NOT_RESOLVABLE_achieved"]]
    if len(ok) < 4:
        return "NOT RESOLVABLE"
    # Will (2026-10-09): a bin NOT RESOLVABLE (pre-data or achieved) counts as not shrinking; the bar stays 4 of 5
    return "PASS" if sum(bins[b]["SHRINK"] for b in ok) >= 4 else "FAIL"


def arm_width(core, dm, sm):
    Ds, Vs = [], []
    for u in (0.5, 1.0, 1.5, 2.0):
        a, b = f"{u}_0.3", f"{u}_0.15"
        Ds.append(float(np.mean([dm[a][n] - dm[b][n] for n in core])))
        Vs.append(float(np.sum([sm[a][n] ** 2 + sm[b][n] ** 2 for n in core])) / len(core) ** 2)
    m, se = float(np.mean(Ds)), math.sqrt(float(np.sum(Vs))) / 4
    return dict(delta_u=Ds, mean=m, se=se, verdict="PASS" if (sum(x > 0 for x in Ds) >= 3 and m > 2 * se) else "FAIL")


def analyse(out):
    F1n, Rn = list(S.F1), list(S.R)
    base = {n: load_base(out, n) for n in F1n + Rn}
    seenZ = {n: json.load(open(os.path.join(out, f"seen_{n}.json"))) for n in Rn}
    vals = lambda recs: {L: {k: col(recs, L, k) for k in MEM_IDX} for L in (S.L_PRIMARY, S.L_SECONDARY)}
    zR = {n: {L: {k: [r[str(L)][k] for r in seenZ[n] if k in r[str(L)]] for k in MEM_IDX}
              for L in (S.L_PRIMARY, S.L_SECONDARY)} for n in Rn}
    bR = {n: vals(base[n]) for n in Rn}
    # seen effects (R zeros vs Stage 1 baseline mapped to R heights) -> d_ref = ½ smallest seen d, per L
    seen_d = {L: {n: S.mean_se(bR[n][L][PK])[0] - S.mean_se(zR[n][L][PK])[0] for n in Rn} for L in (S.L_PRIMARY, S.L_SECONDARY)}
    d_ref = {str(L): 0.5 * min(seen_d[L].values()) for L in seen_d}
    # predicted SE_Z for an F1 bin: per-window SD of g_Z on the seen R bins (pooled) / √(number of F1 windows)
    sdw = {L: float(np.sqrt(np.mean([np.var(zR[n][L][PK], ddof=1) for n in Rn]))) for L in seen_d}
    power, resolvable = {}, {}
    for L in seen_d:
        power[str(L)], resolvable[str(L)] = {}, {}
        for n in F1n:
            nw = int(S.bin_geometry(n)["n_zeros"] // L)
            seZ = sdw[L] / math.sqrt(nw) if nw > 1 else math.inf
            seB = S.mean_se(col(base[n], L, PK))[1]
            se = math.sqrt(seB ** 2 + seZ ** 2)
            p = S.Phi((d_ref[str(L)] - 3 * se) / se)
            power[str(L)][n] = dict(n_windows=nw, se_pred=se, power=p)
            resolvable[str(L)][n] = bool(p >= 0.80)
    # arm C and D power at the seen effects
    dryR = evaluate(Rn, zR, bR, d_ref, {str(L): {} for L in seen_d}, Rn)
    seCpred = math.sqrt(np.mean([power[str(S.L_PRIMARY)][n]["se_pred"] ** 2 for n in S.CORE])) * math.sqrt(2) / math.sqrt(len(S.CORE)) / 2
    powC = S.Phi((dryR["C"]["mean"] - 2 * seCpred) / seCpred)
    Ls = np.array([S.bin_geometry(n)["L_c"] for n in F1n])
    w = 1 / np.array([power[str(S.L_PRIMARY)][n]["se_pred"] for n in F1n]) ** 2
    se_slope = float(1 / math.sqrt(np.sum(w * (Ls - np.sum(w * Ls) / np.sum(w)) ** 2)))
    powD = S.Phi((-dryR["D"]["slope"] - 2 * se_slope) / se_slope)
    # specificity: GUE seeds 0–7 as the "zeros" against seeds 8–15, at F1 heights
    spec_z = {n: vals(load_base(out, n, set(range(8)))) for n in F1n}
    spec_b = {n: vals(load_base(out, n, set(range(8, 16)))) for n in F1n}
    spec = evaluate(list(S.CORE), spec_z, spec_b, d_ref, resolvable, F1n)
    # sensitivity / dry run on seen R zeros (code exercise, not evidence)
    # drift red path: raw vs drift-removed growth of the mapped GUE at each F1 bin
    drift = {n: dict(raw=S.mean_se([r["raw_primary_1000000"] for r in base[n]]),
                     drift_removed=S.mean_se(col(base[n], S.L_PRIMARY, PK))) for n in F1n}
    # precision-guard witness: a one-window zeros stand-in has SE_Z = ∞ -> NOT RESOLVABLE (achieved), whatever d is
    wit = S.bin_shrink(1.0, 0.01, 0.2, math.inf, d_ref[str(S.L_PRIMARY)])
    pre = dict(seen_d={str(L): v for L, v in seen_d.items()}, d_ref=d_ref, per_window_sd_seen={str(L): v for L, v in sdw.items()},
               power=power, resolvable=resolvable, power_C=powC, power_D=powD, se_slope_pred=se_slope,
               D_resolvable=bool(powD >= 0.80), C_resolvable=bool(powC >= 0.80),
               specificity=spec, dryrun_seen_R=dryR, drift_red_path=drift, guard_witness=wit,
               baseline={n: {str(L): {k: S.mean_se(bv) for k, bv in v.items()} for L, v in vals(base[n]).items()}
                         for n in F1n},
               n_gue_seeds={n: len(base[n]) for n in F1n + Rn})
    json.dump(pre, open(os.path.join(out, "preread.json"), "w"), indent=1, default=float)
    print(json.dumps(dict(d_ref=d_ref, power={L: {n: round(v["power"], 3) for n, v in p.items()} for L, p in power.items()},
                          power_C=round(powC, 3), power_D=round(powD, 3),
                          specificity={a: spec[a]["verdict"] for a in "ABCD"},
                          dryrun_seen_R={a: dryR[a]["verdict"] for a in "ABCD"},
                          witness=wit["NOT_RESOLVABLE_achieved"]), indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "baseline":
        baseline(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
    elif cmd == "seen":
        seen(sys.argv[2], sys.argv[3])
    elif cmd == "analyse":
        analyse(sys.argv[2])
