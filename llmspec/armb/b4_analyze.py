"""Arm B, stage B4 analysis (ARMB_PREREG_B1B.md rev 2, sealed 766c92c; this code is sealed by the B4 amendment BEFORE
it reads any arm statistic beyond the B-G1 gate metrics). Reads b4_extract.py outputs + the sealed licence results.
Every threshold comes from the sealed text or the licence outputs; nothing is chosen from arm data.

Common measurements (declared here, all fixed before data):
  stable rank sr = sum(sigma^2)/sigma_1^2 (layer-mean per type); spectral entropy = -sum p ln p / ln n, p = sigma^2/sum;
  Frobenius = sqrt(sum sigma^2); top sigma = sigma_1.
  NOISE of a trajectory = SD of its residual about a Savitzky-Golay smooth on the grid index (window 9, order 2 for Q1
  as in q1_warp.noise_level; window 5, order 2 for Q2 as in q2_licence.x1), RELATIVE (residual / smooth) for stable
  rank / loss, ABSOLUTE for fractions; lag-1 autocorrelation of the residual > 0.25 -> the AR(1) licence row, else iid.
  Licence row = the next-higher tabulated noise level; above the largest level -> NOT LICENSED (descriptive).
B4 AMENDMENT 3 (2026-09-29, pre-data): noise rows are chosen in INJECTED units via noise_calib (the measured SG
    residual SD understates sigma), and a licence cell is used only if licensed for BOTH iid and AR(1) at that level
    (conservative combination: r* max, c_fit min, e / e_x max); the lag-1 type classifier is no longer used.
B4 AMENDMENT 2 (2026-09-28, pre-data): E4 cells from the v2 licence (armb_q1_warp_licence_v2.json; HALFWAY retired,
    midpoint confusers); SUPPORTED worded "X-driven" only where NO_SIMPLE_ANCHOR is licensed, else "the closest of the
    three models is X"; an unlicensed NO_SIMPLE_ANCHOR decision is reported INCONCLUSIVE; grids = grids.arm_grid.
Q1  primary metrics TP_O (sr of attention.dense) and TP_MLPOUT (sr of mlp.dense_4h_to_h); arms A0 (W 1430), A1 (2860),
    A2 (715). PRIMARY route E4 (q1_warp.decide with the licensed r*, c_fit for (arm, noise row)); SECONDARY location
    route (licensed estimator with the smallest worst-shape e(sigma); decidability e_c <= min inter-model gap / 3;
    CONSISTENT iff |t_X - P_m| <= e_c), used only for arms where E4 is not licensed. Verdict lattice as sealed.
Q2  events on A0 (M0 arms descriptive): E_ind (max induction >= 0.3), E_OV / E_QK (fraction of the 48 heads outside the
    70M product-Ginibre 1-99% band >= 0.5), E_MP(Q/K) (fraction of layers with MP KS > the 70M witness KS95 >= 0.9),
    E_sr(M) (layer-mean sr <= 1/2 its step-0 value), E_loss (Stage 3 text-probe loss below the midpoint of step 0 and
    step 3000). Crossing time = q2_licence.x1; interval +- e_x (the licence's WORST-SHAPE 95% quantile for the event's
    noise row: conservative, declared). PRECEDES iff intervals do not overlap. Wave: S = rho_Q + rho_K (Spearman of
    layer 0-5 vs t_half, ties averaged; a layer that never crosses is ranked last), exact permutation null (720^2).
Q3  A0: (S) [100,130] vs [1000,1025]; (L) [100, b_L] vs [1000,1025] (b_L from b4_extract.lr_intervals); ratio of
    layer-mean dW stable rank per type; LOW-RANK EARLY iff <= 0.5 in >= 4/6 types in BOTH; NOT iff >= 0.8 in >= 4/6 in
    BOTH; else INCONCLUSIVE. Per-layer ratios reported.
Q4  pairs d1 = M0s1 - A0, d2 = M0s2 - pythia-70m-seed1 at the shared steps (and the shared intervals for dW rank);
    OPTIMIZER-DIFFERENT iff same sign and |d_i| > T s_ref for both, s_ref = SD over the 10 reference runs, T = Bonferroni
    t_9 (two-sided 0.05) over the whole Q4 family (counted below). M0s1 - pythia-70m reported descriptively.
BULK NULL at MDD (armb_bulk_power_70m.json): per arm, per grid checkpoint, per cell (full Q/K/V/O/MLP_IN/MLP_OUT,
    per-head Q/K/V/O): |bulk <r~> - 70M witness mean| <= MDD -> HOLDS AT MDD; else VIOLATED -> ladder: density-matched
    COE witness with the S4-licensed <r~> calibrator (stage3_calib_v2 KDE, lambda domain, c = 16, truncated), R = 10;
    DENSITY_ARTIFACT iff |d_obs - d_density| <= MDD, else FINDING_CANDIDATE.
Usage: b4_analyze.py q1|q2|q3|q4|bulk|all   -> results/armb_b4_<q>.json
"""
import itertools, json, sys
from pathlib import Path
import numpy as np
from scipy.signal import savgol_filter
from scipy.stats import rankdata, t as tdist

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import q1_models as QM  # noqa: E402
import q1_licence as QL  # noqa: E402
import q1_warp as QW  # noqa: E402
import q2_licence as Q2L  # noqa: E402
import q1_warp_v2 as QW2  # noqa: E402  (B4 amendment 2: E4 licence v2; importing it points QW.window at the arm grids)
from grids import arm_grid  # noqa: E402  (B1a-A8: A2 dense grid)
import noise_calib as NC  # noqa: E402  (B4 amendment 3: measured -> injected noise units; both noise types)

H, DH, D, NL, ROT = 8, 64, 512, 6, 16
TYPES = ["Q", "K", "V", "O", "MLP_IN", "MLP_OUT"]
STOPS = {"A0": 3000, "A1": 5000, "A2": 3000, "M0s1": 3000, "M0s2": 3000}
SHARED = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, 2000, 3000]
REFS = ["pythia-70m"] + [f"pythia-70m-seed{k}" for k in range(1, 10)]
RES = ROOT / "results"


def load_json(name):
    return json.loads((RES / name).read_text())


# ---------------------------------------------------------------- loading
def ldir(src, t):
    return (ROOT / "cache" / "armb" / src / f"step{t:05d}") if src in STOPS else (ROOT / "cache" / "s3" / src / f"step{t}")


def layers(src, t):
    return [np.load(ldir(src, t) / f"L{L:02d}.npz") for L in range(NL)]


def markers(src, t):
    return np.load(ldir(src, t) / "MARKERS.npz")


def sr(s):
    s = np.asarray(s, float); return float((s ** 2).sum() / s[0] ** 2)


def entropy(s):
    p = np.asarray(s, float) ** 2; p = p / p.sum(); p = p[p > 0]; return float(-(p * np.log(p)).sum() / np.log(len(s)))


def layer_mean(src, t, M, f):
    return float(np.mean([f(z[f"sig_{M}"]) for z in layers(src, t)]))


def grid(arm):
    return arm_grid(arm)                                  # B1a-A8 / B4 amendment 2 (was QL.grid(STOPS[arm]))


def traj(src, steps, M, f=sr):
    return np.array([layer_mean(src, t, M, f) for t in steps])


# ---------------------------------------------------------------- noise + licence rows
def noise(y, win, rel):
    sm = savgol_filter(y, win, 2); r = (y - sm) / sm if rel else (y - sm)
    lag1 = float(np.corrcoef(r[:-1], r[1:])[0, 1]) if np.std(r) > 0 else 0.0
    return float(np.std(r, ddof=1)), ("ar" if lag1 > 0.25 else "iid"), lag1


def row(level, levels):
    up = [x for x in levels if x >= level]
    return min(up) if up else None


# ---------------------------------------------------------------- Q1
def q1():
    """B4 amendment 3: rows are chosen by NC.level (calibrated, max over iid/AR) and a cell is used only if licensed for
    BOTH noise types at that level (conservative: r* = max, c_fit = min, NSA licensed only if in both)."""
    warp = load_json("armb_q1_warp_licence_v2.json")["cells"]; loc = load_json("armb_q1_licence.json")["cells"]
    cal = load_json("armb_noise_calibration.json")["q1"]
    rng = np.random.default_rng(20261001); out = {}
    g0 = np.array(grid("A0"), float); REL = NC.REL
    for M, name in (("O", "TP_O"), ("MLP_OUT", "TP_MLPOUT")):
        y0 = traj("A0", grid("A0"), M); m0 = float(NC.measure(y0, 9, True)); L0 = NC.level(m0, cal["A0"], REL)
        best0 = None
        if L0 is not None:
            c = [loc[f"stop3000_s{L0}_{t}"]["licence"] for t in ("iid", "ar")]
            cands = [(E, max(c[0][E]["e_sigma_9875_worst_shape"], c[1][E]["e_sigma_9875_worst_shape"]))
                     for E in c[0] if c[0][E]["LICENSED"] and c[1][E]["LICENSED"]]
            best0 = min(cands, key=lambda z: z[1]) if cands else None
        t0 = tp0 = None
        if best0:
            est = QL.estimate(y0[None, :], g0, 3000, rng)[0]; j = {"E1": 0, "E2": 3, "E3": 6}[best0[0]]
            tp0, t0 = est[j], est[j + 1]
        rec = {"A0": {"noise_measured": m0, "noise_level_calibrated": L0, "estimator": best0, "has_tp": tp0, "t0": t0}}
        for X in ("A1", "A2"):
            gX = np.array(grid(X), float); yX = traj(X, grid(X), M); mX = float(NC.measure(yX, 9, True))
            LX = NC.level(mX, cal[X], REL); lvl = None if (L0 is None or LX is None) else max(L0, LX)
            cells = [warp.get(f"{X}_s{lvl}_{t}") for t in ("iid", "ar")] if lvl else [None, None]
            r = {"noise_measured": mX, "noise_level_calibrated": LX, "row_level": lvl}
            if all(cc and cc["LICENSED"] for cc in cells):
                r_star = max(cc["r_star"] for cc in cells); c_fit = min(cc["c_fit"] for cc in cells)
                nsa = all(cc["NSA_LICENSED"] for cc in cells)
                dec, sse, fr = QW.decide(g0, y0, gX, yX, X, r_star, c_fit)
                if dec == "NO_SIMPLE_ANCHOR" and not nsa:
                    dec = "INCONCLUSIVE (no-model outcome not licensed for this cell)"
                r.update({"route": "E4", "decision": dec, "sse": sse, "fit_ratio": fr, "r_star": r_star, "c_fit": c_fit,
                          "NSA_LICENSED": nsa, "wording": "X-driven" if nsa else "closest of the three models is X"})
            else:
                r.update({"route": "LOCATION"})
                if not tp0:
                    r["decision"] = "NOT APPLICABLE AT 70M (no licensed turning point in A0)"
                else:
                    stopX = 5000 if X == "A1" else 3000
                    lic = [loc.get(f"stop{stopX}_s{LX}_{t}", {}).get("licence", {}) for t in ("iid", "ar")] if LX else [{}, {}]
                    candX = [(E, max(lic[0][E]["e_sigma_9875_worst_shape"] or 1e9, lic[1][E]["e_sigma_9875_worst_shape"] or 1e9))
                             for E in lic[0] if lic[0][E]["LICENSED"] and lic[1].get(E, {}).get("LICENSED")]
                    if not candX:
                        r["decision"] = "DESCRIPTIVE (no licensed estimator at the arm's calibrated noise, both types)"
                    else:
                        E, eX = min(candX, key=lambda z: z[1]); e0 = best0[1]
                        est = QL.estimate(yX[None, :], gX, stopX, rng)[0]; j = {"E1": 0, "E2": 3, "E3": 6}[E]
                        tpX, tX = est[j], est[j + 1]
                        P = QM.predict(int(round(t0)), X); gap = QM.min_gap(int(round(t0)), X)
                        ec = {m: float(np.hypot(eX, (P["dLRINT_dt0"] if m == "LR_INT" else 1.0) * e0)) for m in ("STEP", "WARMUP", "LR_INT")}
                        r.update({"estimator": E, "t_X": tX, "has_tp": tpX, "P": P, "gap": gap, "e_c": ec,
                                  "decidable": bool(max(ec.values()) <= gap / 3)})
                        if not tpX:
                            r["decision"] = "TURNING POINT ABSENT IN ARM (reported, no model verdict)"
                        elif not r["decidable"]:
                            r["decision"] = "DESCRIPTIVE (not decidable: e_c > gap/3)"
                        else:
                            r["consistent"] = {m: bool(abs(tX - P[m]) <= ec[m]) for m in ("STEP", "WARMUP", "LR_INT")}
                            r["decision"] = "CONSISTENT: " + ",".join(m for m, v in r["consistent"].items() if v)
            rec[X] = r
        e4 = [rec[X]["decision"] for X in ("A1", "A2") if rec[X].get("route") == "E4"]
        if e4:
            if "NO_SIMPLE_ANCHOR" in e4:
                verdict = "NO SIMPLE ANCHOR"
            else:
                sup = [d for d in e4 if d in ("STEP", "WARMUP", "LR_INT")]
                if sup and len(set(sup)) == 1 and len(sup) == len(e4):
                    words = [rec[X]["wording"] for X in ("A1", "A2") if rec[X].get("route") == "E4"]
                    verdict = (f"SUPPORTED: {sup[0]}-driven" if all(w == "X-driven" for w in words)
                               else f"SUPPORTED: the closest of the three models is {sup[0]}")
                else:
                    verdict = "CONFLICT" if len(set(sup)) > 1 else "INCONCLUSIVE"
        else:
            cons = [rec[X].get("consistent") for X in ("A1", "A2") if rec[X].get("consistent")]
            if not cons:
                verdict = "DESCRIPTIVE / NOT APPLICABLE (see arms)"
            else:
                ok = [m for m in ("STEP", "WARMUP", "LR_INT") if all(c[m] for c in cons)
                      and all(any(not c[o] for c in cons) for o in ("STEP", "WARMUP", "LR_INT") if o != m)]
                verdict = (f"SUPPORTED: {ok[0]}" if len(ok) == 1 else
                           ("NO SIMPLE ANCHOR" if all(not any(c.values()) for c in cons) else "INCONCLUSIVE"))
        rec["VERDICT"] = verdict
        out[name] = rec
    return out


# ---------------------------------------------------------------- Q2
def ginibre_bands(n=4000, seed=20261002):
    rng = np.random.default_rng(seed); ov, qk = [], []
    for _ in range(n):
        V, O = rng.standard_normal((DH, D)), rng.standard_normal((D, DH))
        ev = np.linalg.eigvals(V @ O); ov.append(ev.real.sum() / np.abs(ev).sum())
        Q, K = rng.standard_normal((DH - ROT, D)), rng.standard_normal((DH - ROT, D))
        AA, BB, BA = Q @ Q.T, K @ K.T, K @ Q.T; f2 = np.trace(AA @ BB); qk.append((f2 + np.trace(BA @ BA)) / (2 * f2))
    return (np.quantile(ov, .01), np.quantile(ov, .99)), (np.quantile(qk, .01), np.quantile(qk, .99))


def mp_ks_frac(src, t, M, ks95):
    g = np.linspace(0, 4, 40001); F = np.concatenate([[0], np.cumsum(np.sqrt(np.clip((4 - g[1:]) * g[1:], 0, None)) / (2 * np.pi * g[1:]) * np.diff(g))])
    F = F / F[-1]; med_x = float(np.interp(0.5, F, g)); frac = []
    for z in layers(src, t):
        sig = z[f"sig_{M}"]; sc = np.median(sig) / np.sqrt(D * med_x); x = np.sort(sig ** 2 / (D * sc * sc))
        Fx = np.interp(x, g, F); i = np.arange(1, len(x) + 1)
        frac.append(max((i / len(x) - Fx).max(), (Fx - (i - 1) / len(x)).max()) > ks95)
    return float(np.mean(frac))


def events(src, steps, bands, wit):
    ovb, qkb = bands; g = np.array(steps, float); tr = {}
    tr["E_ind"] = (np.array([float(markers(src, t)["induction"].max()) for t in steps]), 0.3, +1, "abs")
    tr["E_OV"] = (np.array([float(np.mean([((lambda e: e.real.sum(-1) / np.abs(e).sum(-1))(z["ov_eig"]) < ovb[0]) |
                                            ((lambda e: e.real.sum(-1) / np.abs(e).sum(-1))(z["ov_eig"]) > ovb[1])
                                            for z in layers(src, t)])) for t in steps]), 0.5, +1, "abs")
    tr["E_QK"] = (np.array([float(np.mean([(z["qk_sym_nr"] < qkb[0]) | (z["qk_sym_nr"] > qkb[1]) for z in layers(src, t)]))
                            for t in steps]), 0.5, +1, "abs")
    for M in ("Q", "K"):
        tr[f"E_MP({M})"] = (np.array([mp_ks_frac(src, t, M, wit["types"][M]["ks95"]) for t in steps]), 0.9, +1, "abs")
    for M in TYPES:
        y = traj(src, steps, M); tr[f"E_sr({M})"] = (y, 0.5 * y[0], -1, "rel")
    lt = np.array([float(markers(src, t)["loss_text"]) for t in steps]); i3 = steps.index(3000)
    tr["E_loss"] = (lt, 0.5 * (lt[0] + lt[i3]), -1, "rel")
    lic = load_json("armb_q2_licence.json")["cells"]; cal = load_json("armb_noise_calibration.json")["q2"]["A0grid"]; out = {}
    for k, (y, thr, sgn, kind) in tr.items():
        m = float(NC.measure(y, 5, kind == "rel"))                                   # B4 amendment 3: calibrated row
        lvl = NC.level(m, cal, NC.ABS if kind == "abs" else NC.REL, prefix=f"{kind}_")
        ex = max(lic[f"{kind}_{lvl}_iid"]["e_x_95_worst_shape"], lic[f"{kind}_{lvl}_ar"]["e_x_95_worst_shape"]) if lvl else None
        tc = float(Q2L.x1(y[None, :], g, thr, sgn)[0])
        out[k] = {"t": None if np.isnan(tc) else tc, "e_x": ex, "noise_measured": m, "noise_level_calibrated": lvl}
    return out


def q2():
    bands = ginibre_bands(); wit = load_json("stage3_witness_pythia-70m.json")
    out = {"bands": {"ov": list(bands[0]), "qk": list(bands[1])}}
    for arm in ("A0", "M0s1", "M0s2"):
        ev = events(arm, grid(arm), bands, wit); pairs = {}
        for a, b in (("E_OV", "E_QK"), ("E_OV", "E_ind"), ("E_QK", "E_ind"), ("E_sr(Q)", "E_sr(V)"), ("E_MP(Q)", "E_ind")):
            A, B = ev[a], ev[b]
            if None in (A["t"], B["t"], A["e_x"], B["e_x"]):
                pairs[f"{a} vs {b}"] = "UNRESOLVED (event not crossed or noise above the licence)"
            elif A["t"] + A["e_x"] < B["t"] - B["e_x"]:
                pairs[f"{a} vs {b}"] = f"{a} PRECEDES {b}"
            elif B["t"] + B["e_x"] < A["t"] - A["e_x"]:
                pairs[f"{a} vs {b}"] = f"{b} PRECEDES {a}"
            else:
                pairs[f"{a} vs {b}"] = "SIMULTANEOUS AT THIS RESOLUTION"
        out[arm] = {"events": ev, "pairs": pairs, "wave": wave(arm), "role": "primary" if arm == "A0" else "descriptive"}
    return out


def wave(arm):
    steps = grid(arm); g = np.array(steps, float); th = {}
    for M in ("Q", "K", "V", "O"):
        t = []
        for L in range(NL):
            y = np.array([sr(layers(arm, s)[L][f"sig_{M}"]) for s in steps])
            v = float(Q2L.x1(y[None, :], g, 0.5 * y[0], -1)[0]); t.append(np.inf if np.isnan(v) else v)
        th[M] = t

    def rho(tv, perm):
        r1 = rankdata(np.array(tv)[list(perm)]); r0 = np.arange(1, NL + 1)
        return float(np.corrcoef(r0, r1)[0, 1]) if np.std(r1) > 0 else 0.0
    ident = tuple(range(NL)); perms = list(itertools.permutations(range(NL)))
    obs = {M: rho(th[M], ident) for M in th}
    nq = np.array([rho(th["Q"], p) for p in perms]); nk = np.array([rho(th["K"], p) for p in perms])
    S = obs["Q"] + obs["K"]; null = (nq[:, None] + nk[None, :]).ravel()
    p_up, p_lo = float((null >= S - 1e-12).mean()), float((null <= S + 1e-12).mean())
    verdict = ("Liu REPLICATES" if p_up < 0.05 and obs["Q"] > 0 and obs["K"] > 0 else
               ("OPPOSITE ORDER" if p_lo < 0.05 else "NOT RESOLVED (bounded null at 6 layers)"))
    return {"t_half": {M: [None if np.isinf(v) else v for v in th[M]] for M in th}, "rho": obs, "S": S,
            "p_upper": p_up, "p_lower": p_lo, "verdict": verdict}


# ---------------------------------------------------------------- Q3
def q3():
    import b4_extract as BX  # noqa: F401  (interval definitions only; importing asserts CUDA)
    bL = BX.lr_intervals()[0]; out = {}
    def dw(arm, a, b):
        z = np.load(ROOT / "cache" / "armb" / arm / f"DW_{a:05d}_{b:05d}.npz")
        return {M: np.array([float(z[f"L{L:02d}_{M}_sr"]) for L in range(NL)]) for M in TYPES}
    for arm in ("A0", "A1", "A2"):
        late = dw(arm, 1000, 1025); rec = {}
        for tag, (a, b) in (("S", (100, 130)), ("L", bL)):
            early = dw(arm, a, b)
            rec[tag] = {"interval": [a, b], "ratio": {M: float(early[M].mean() / late[M].mean()) for M in TYPES},
                        "per_layer": {M: (early[M] / late[M]).tolist() for M in TYPES}}
        low = all(sum(v <= 0.5 for v in rec[t]["ratio"].values()) >= 4 for t in ("S", "L"))
        notl = all(sum(v >= 0.8 for v in rec[t]["ratio"].values()) >= 4 for t in ("S", "L"))
        rec["VERDICT"] = "LOW-RANK EARLY" if low else ("NOT LOW-RANK EARLY" if notl else "INCONCLUSIVE")
        rec["role"] = "primary" if arm == "A0" else "descriptive"; out[arm] = rec
    return out


# ---------------------------------------------------------------- Q4
Q4_IVS = [(512, 1000), (1000, 2000), (2000, 3000)]
METRICS = {"sr": sr, "entropy": entropy, "fro": lambda s: float(np.sqrt((np.asarray(s, float) ** 2).sum())), "top": lambda s: float(s[0])}


def q4():
    fam = (len(METRICS) * len(TYPES) + 1) * len(SHARED) + len(Q4_IVS) * len(TYPES)
    T = float(tdist.ppf(1 - 0.05 / (2 * fam), 9)); cells, n_diff = [], 0

    def val(src, t, key):
        if key == "loss":
            return float(markers(src, t)["loss_text"])
        k, M = key.split(":"); return layer_mean(src, t, M, METRICS[k])
    keys = [f"{k}:{M}" for k in METRICS for M in TYPES] + ["loss"]
    for t in SHARED:
        for key in keys:
            ref = np.array([val(m, t, key) for m in REFS]); s = float(ref.std(ddof=1))
            d1 = val("M0s1", t, key) - val("A0", t, key); d2 = val("M0s2", t, key) - val("pythia-70m-seed1", t, key)
            dp = val("M0s1", t, key) - val("pythia-70m", t, key)
            diff = bool(np.sign(d1) == np.sign(d2) and s > 0 and abs(d1) > T * s and abs(d2) > T * s)
            n_diff += diff; cells.append({"step": t, "metric": key, "d1": d1, "d2": d2, "d1_vs_pythia": dp, "s_ref": s, "OPTIMIZER_DIFFERENT": diff})

    def dwv(src, a, b, M):
        base = (ROOT / "cache" / "armb" / src) if src in STOPS else (ROOT / "cache" / "s3" / src)
        z = np.load(base / f"DW_{a:05d}_{b:05d}.npz"); return float(np.mean([float(z[f"L{L:02d}_{M}_sr"]) for L in range(NL)]))
    for a, b in Q4_IVS:
        for M in TYPES:
            ref = np.array([dwv(m, a, b, M) for m in REFS]); s = float(ref.std(ddof=1))
            d1 = dwv("M0s1", a, b, M) - dwv("A0", a, b, M); d2 = dwv("M0s2", a, b, M) - dwv("pythia-70m-seed1", a, b, M)
            diff = bool(np.sign(d1) == np.sign(d2) and s > 0 and abs(d1) > T * s and abs(d2) > T * s)
            n_diff += diff; cells.append({"interval": [a, b], "metric": f"dW_sr:{M}", "d1": d1, "d2": d2, "s_ref": s, "OPTIMIZER_DIFFERENT": diff})
    return {"family": fam, "T": T, "n_optimizer_different": n_diff, "cells": cells,
            "note": "two pairs = 1 df: only LARGE-and-CONSISTENT effects are claimed; the rest is descriptive"}


# ---------------------------------------------------------------- bulk null at MDD
CELLS = {"Q": "full_sq", "K": "full_sq", "V": "full_sq", "O": "full_sq", "MLP_IN": "full_mlp", "MLP_OUT": "full_mlp",
         "head_Q": "head_qkv", "head_K": "head_qkv", "head_V": "head_qkv", "head_O": "head_O"}


def bulk():
    import s3stats as S
    import stage2_g7 as G
    import stage3_calib_v2 as CV
    mdd = load_json("armb_bulk_power_70m.json"); wit = load_json("stage3_witness_pythia-70m.json")["types"]
    rng = np.random.default_rng(20261003); out = {}
    for arm in STOPS:
        counts, flagged = {"HOLDS_AT_MDD": 0, "VIOLATED": 0}, []
        for t in grid(arm):
            Z = layers(arm, t)
            for cell, cls in CELLS.items():
                spectra = list(np.concatenate([z[f"sighead_{cell[5:]}"] for z in Z])) if cell.startswith("head_") else [z[f"sig_{cell}"] for z in Z]
                rt = S.local_stats(spectra, "bulk")["rt"]; ref = wit[cell]["runs"]["witness_fp16_final"]["bulk:rt"]["mean"]
                m = mdd[cls]["MDD"]; d = rt - ref
                if abs(d) <= m:
                    counts["HOLDS_AT_MDD"] += 1; continue
                counts["VIOLATED"] += 1; dd = []
                fits = [CV.KDE(np.sort(np.asarray(s, float) ** 2), 16.0) for s in spectra]
                for _ in range(10):
                    dd.append(S.local_stats([CV.to_sig(G.cue_phases(len(s), rng, 1), f) for s, f in zip(spectra, fits)], "bulk")["rt"] - ref)
                lab = "DENSITY_ARTIFACT" if abs(d - float(np.mean(dd))) <= m else "FINDING_CANDIDATE"
                flagged.append({"step": t, "cell": cell, "d_rt": d, "d_density": float(np.mean(dd)), "MDD": m, "label": lab})
        out[arm] = {"counts": counts, "violated": flagged,
                    "VERDICT": ("BULK NULL HOLDS AT MDD" if not flagged else
                                ("HOLDS (violations attributed DENSITY_ARTIFACT)" if all(f["label"] == "DENSITY_ARTIFACT" for f in flagged)
                                 else "FINDING_CANDIDATE PRESENT"))}
    return out


SEAL_FILES = ["armb/b4_analyze.py", "armb/noise_calib.py", "armb/q1_warp_v2.py", "armb/q1_warp.py", "armb/q1_licence.py",
              "armb/q1_models.py", "armb/q2_licence.py", "armb/grids.py", "armb/b4_extract.py", "s3stats.py",
              "stage3_calib_v2.py", "stage2_g7.py", "stage3_extract.py", "stage3_witness.py",
              "results/armb_q1_licence.json", "results/armb_q1_warp_licence_v2.json", "results/armb_q2_licence.json",
              "results/armb_noise_calibration.json", "results/armb_bulk_power_70m.json"]


def verify_seal():
    """FAIL-CLOSED seal check (Will 09-29): every file in the sealed manifest (armb/B4_SEAL.json, or $B4_SEAL for tests)
    must match its sha256, else exit 4 before anything is computed or written. A missing manifest also exits 4."""
    import hashlib, os
    fp = Path(os.environ.get("B4_SEAL", str(HERE / "B4_SEAL.json")))
    if not fp.exists():
        print(f"SEAL CHECK FAILED: manifest {fp} missing", flush=True); sys.exit(4)
    man = json.loads(fp.read_text())["files"]
    bad = [f for f in SEAL_FILES if f not in man or hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != man[f]]
    if bad:
        print(f"SEAL CHECK FAILED: {bad}", flush=True); sys.exit(4)
    print(f"seal check OK ({len(SEAL_FILES)} files)", flush=True)


if __name__ == "__main__":
    verify_seal()
    which = sys.argv[1]
    for q, fn in (("q1", q1), ("q2", q2), ("q3", q3), ("q4", q4), ("bulk", bulk)):
        if which in (q, "all"):
            (RES / f"armb_b4_{q}.json").write_text(json.dumps(fn(), indent=1, default=float))
            print(q, "written", flush=True)
