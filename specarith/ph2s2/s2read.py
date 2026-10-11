"""PH2S Stage 2 read (PH2S_SEAL_2.0): CS08's theory-fixed prediction of the tapered window-variance growth g_B on F2, and
the dry run through the same code.

  python s2read.py read      REFUSED unless seals/PH2S_SEAL_2.0.json exists and pins this code, and every F2 file's md5
                             matches the pin BEFORE it is decoded; F2 files in ../ph2r2/data/platt_fresh/
                             -> results/read/S2_READ.json + S2_READ.md
  python s2read.py dryrun    the same evaluation on (i) F1 (seen; decoded again through the read path; prediction
                             interpolated in ℓ and held at the end values; expect PASS, and the stored tapered.py
                             values reproduced), (ii) a GUE stand-in at F2 geometry (windows drawn from the Stage 2
                             GUE baseline, f2_gue_levels.py) against the ζ prediction (expect
                             FAIL) and (iii) against the GUE prediction (expect PASS), plus the precision-guard witness
                             (expect NOT RESOLVABLE on a would-be PASS) -> results/dryrun/S2_DRYRUN.json

Rules (sealed; Will, twenty-seventh round option (a), twenty-eighth round pooling C). Per F2 file f:
ĝ_f = √(v̂_B(10⁴)/v̂_B(100)), with v̂_B the successive-difference estimator (tapered.pooled_diff),
SE_f = ½·ĝ_f·√(rSE₁₀₀² + rSE₁₀⁴²) (lag-0–2 SEs), z_f = (ĝ_f − g_pred,f)/SE_f. Pooled with weights fixed pre-data,
W_f ∝ n_f(10⁴) − 1 (successive differences at b = 10⁴, from the pinned height range; ΣW = 1):
d_pool = ΣW(ĝ − g_pred), SE_pool = √(ΣW²·SE_f²), z_pool = d_pool/SE_pool.
  - Precision guard (reads only SEs): RESOLVABLE iff 2·SE_pool ≤ 0.07; otherwise NOT RESOLVABLE.
  - PASS iff RESOLVABLE and |z_pool| ≤ 2 (R2) and ≥ 4 of 5 files have |z_f| ≤ 3 (R1); otherwise FAIL.
  - Reported regardless of verdict: pooled ĝ_B ± 95% CI (± 2·SE_pool) beside the pooled prediction (same weights),
    per-file ĝ_f ± SE_f beside g_pred,f, and the v̂_B ladder (descriptive).
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ph2r2"))
sys.path.insert(0, os.path.join(HERE, "..", "ph2s"))

import tapered as T

SEAL = os.path.join(HERE, "seals", "PH2S_SEAL_2.0.json")
FRESH = os.path.join(HERE, "..", "ph2r2", "data", "platt_fresh")
PRED = os.path.join(HERE, "..", "cs4", "results", "gs_zeta", "gs_zeta_B_summary.json")
TAP = os.path.join(HERE, "results", "tapered")
TAP_F2GUE = os.path.join(HERE, "results", "tapered_f2gue")    # Stage 2 GUE baseline (24 × 10⁶, f2_gue_levels.py)
CODE = ("s2read.py", "tapered.py", "../ph2r2/r2prep.py", "../ph2r2/r2run.py")
G_GUE_B = 0.959137                                   # sine kernel through the same assembly (cs4/gs_unitary_lag1.py)
K_POOL, K_FILE, MIN_AGREE, GUARD = 2.0, 3.0, 4, 0.07
# F2 (ph2r2/FRESH_SETS_F1_F3.md): prediction key (zero-weighted mean ℓ) -> (file, t0, t1, md5)
F2 = {"15.7502": ("zeros_42446000.dat", 42_446_000, 44_546_000, "b9e8b34c5bab7367b68848c9e61940b0"),
      "16.4972": ("zeros_90746000.dat", 90_746_000, 92_846_000, "8b05f3b38121178a7e563517ea08d0fe"),
      "17.2491": ("zeros_193646000.dat", 193_646_000, 195_746_000, "69b955f15e063c3646f4c92092f12290"),
      "19.5003": ("zeros_1848446000.dat", 1_848_446_000, 1_850_546_000, "2169ed28b1dba1b889ccb25778eba4fc"),
      "21.75": ("zeros_17541746000.dat", 17_541_746_000, 17_543_846_000, "c706184af0a09d8f0df825ee9a81718a")}
F1_ELL = dict(F1a=14.4625, F1b=15.4741, F1c=17.7481, F1d=19.2500, F1e=21.5000, F1x=22.1000)


def windows_from_range(t0, t1):
    """n_windows(b) for a file's pinned height range, as tapered.window_sums lays them out (no zero read)."""
    nbar = lambda t: t / (2 * math.pi) * math.log(t / (2 * math.pi * math.e)) + 7 / 8
    sig = lambda b: b / math.sqrt(2 * math.pi)
    return {b: len(np.arange(nbar(t0) + 4 * sig(b), nbar(t1) - 4 * sig(b), 3 * b)) for b in T.LADDER}


def f2_windows():
    return {ell: windows_from_range(t0, t1) for ell, (_, t0, t1, _) in F2.items()}


def pool_weights(nwin):
    """Twenty-eighth round, C: W_f ∝ n_f(10⁴) − 1, normalised; nwin = {name: windows_from_range(...)}."""
    raw = {n: float(v[10_000] - 1) for n, v in nwin.items()}
    s = sum(raw.values())
    return {n: x / s for n, x in raw.items()}


def predictions():
    return {ell: row["g_B"] for ell, row in json.load(open(PRED)).items() if ell != "gue_B"}


def decode(path):
    import r2prep as P
    import r2run as RR
    t = RR.read_platt_heights(path)
    return t, np.asarray(P.nbar(t), float)


def file_record(x):
    """The tapered ladder of one unfolded sequence (window sums kept) and its estimator-B statistics."""
    lad = T.ladder(x)
    rec = dict(n_levels=len(x), ladder={b: dict(n_windows=v["n_windows"]) for b, v in lad.items()})
    vb = {}
    for b in T.LADDER:
        v, se, n = T.pooled_diff([dict(ladder=lad)], b)
        vb[b] = (v, se)
        rec["ladder"][str(b)].update(vB=v, vB_se=se, n_diffs=n)
    g = math.sqrt(vb[10_000][0] / vb[100][0])
    rec.update(g=g, se_g=0.5 * g * math.hypot(vb[100][1] / vb[100][0], vb[10_000][1] / vb[10_000][0]))
    return rec, lad


def stats_from_sums(sums100, sums1e4):
    lad = {"100": dict(sums=list(sums100)), "10000": dict(sums=list(sums1e4))}
    v = {b: T.pooled_diff([dict(ladder=lad)], b)[:2] for b in (100, 10_000)}
    g = math.sqrt(v[10_000][0] / v[100][0])
    return g, 0.5 * g * math.hypot(v[100][1] / v[100][0], v[10_000][1] / v[10_000][0])


def evaluate(files, weights):
    """files: {name: dict(g, se_g, g_pred)} for the five test files; weights: {name: W_f} fixed pre-data (pool_weights).
    The guard reads only the SEs and the fixed weights."""
    names = list(files)
    g = np.array([files[n]["g"] for n in names])
    se = np.array([files[n]["se_g"] for n in names])
    gp = np.array([files[n]["g_pred"] for n in names])
    W = np.array([weights[n] for n in names])
    assert abs(W.sum() - 1) < 1e-12 and (W > 0).all()
    z = (g - gp) / se
    se_pool = float(math.sqrt(np.sum(W ** 2 * se ** 2)))
    d_pool = float(np.sum(W * (g - gp)))
    z_pool = d_pool / se_pool
    agree = int(np.sum(np.abs(z) <= K_FILE))
    resolvable = 2 * se_pool <= GUARD
    R2 = abs(z_pool) <= K_POOL
    R1 = agree >= MIN_AGREE
    verdict = "NOT RESOLVABLE" if not resolvable else ("PASS" if (R1 and R2) else "FAIL")
    g_pool = float(np.sum(W * g))
    gp_pool = float(np.sum(W * gp))
    return dict(per_file={n: dict(g=float(g[i]), se_g=float(se[i]), g_pred=float(gp[i]), z=float(z[i]), weight=float(W[i]),
                                  within_3se=bool(abs(z[i]) <= K_FILE)) for i, n in enumerate(names)},
                se_pool=se_pool, guard_2se_pool=2 * se_pool, resolvable=bool(resolvable),
                d_pool=d_pool, z_pool=float(z_pool), files_within_3se=agree, R1=bool(R1), R2=bool(R2),
                g_pool=g_pool, g_pool_ci95=[g_pool - 2 * se_pool, g_pool + 2 * se_pool], g_pred_pool=gp_pool,
                verdict=verdict)


def report_md(res, title):
    L = [f"# {title}", "", f"**Verdict: {res['verdict']}**", "",
         f"- Pooled ĝ_B = {res['g_pool']:.4f}, 95% CI [{res['g_pool_ci95'][0]:.4f}, {res['g_pool_ci95'][1]:.4f}];"
         f" pooled prediction {res['g_pred_pool']:.4f} (same weights).",
         f"- d_pool = {res['d_pool']:+.4f} ± {res['se_pool']:.4f}, z_pool = {res['z_pool']:+.2f} (R2: |z_pool| ≤ 2 → "
         f"{'yes' if res['R2'] else 'no'}).",
         f"- Files within 3 SE: {res['files_within_3se']} of 5 (R1: ≥ 4 → {'yes' if res['R1'] else 'no'}).",
         f"- Precision guard: 2·SE_pool = {res['guard_2se_pool']:.4f} ≤ 0.07 → "
         f"{'RESOLVABLE' if res['resolvable'] else 'NOT RESOLVABLE'}.", "",
         "| file | ĝ_B ± SE | g_pred | z |", "|---|---|---|---|"]
    L += [f"| {n} | {r['g']:.4f} ± {r['se_g']:.4f} | {r['g_pred']:.4f} | {r['z']:+.2f} |" for n, r in res["per_file"].items()]
    return "\n".join(L) + "\n"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def read():
    if not os.path.exists(SEAL):
        raise SystemExit("REFUSED: no PH2S_SEAL_2.0.json — F2 zeros are not decoded before the seal")
    seal = json.load(open(SEAL))
    for f in CODE:
        if sha(os.path.join(HERE, f)) != seal["code_sha256"][f]:
            raise SystemExit(f"REFUSED: {f} differs from the sealed code")
    if sha(PRED) != seal["prediction_sha256"]:
        raise SystemExit("REFUSED: the prediction file differs from the sealed one")
    pred = predictions()
    paths = {}
    for ell, (fname, _, _, _) in F2.items():                 # every md5 before any decode
        p = os.path.join(FRESH, fname)
        if hashlib.md5(open(p, "rb").read()).hexdigest() != seal["f2_md5"][fname]:
            raise SystemExit(f"REFUSED: {p} md5 differs from the pin")
        paths[ell] = p
    recs, files = {}, {}
    for ell, p in paths.items():
        t, x = decode(p)
        t0, t1 = F2[ell][1], F2[ell][2]
        if not (t[0] >= t0 and t[-1] < t1):
            raise SystemExit(f"REFUSED: {p} heights outside the pinned range")
        rec, _ = file_record(x)
        recs[ell] = rec
        files[ell] = dict(g=rec["g"], se_g=rec["se_g"], g_pred=pred[ell])
        print(ell, "ĝ_B %.4f ± %.4f  (pred %.4f)" % (rec["g"], rec["se_g"], pred[ell]), flush=True)
    nwin = f2_windows()
    W = pool_weights(nwin)
    if any(abs(W[e] - seal["pool_weights"][e]) > 1e-15 for e in F2):
        raise SystemExit("REFUSED: pooling weights differ from the sealed ones")
    for ell, rec in recs.items():                            # descriptive: the data's window counts vs the pinned ones
        rec["n_windows_pinned"] = nwin[ell]
    res = evaluate(files, W)
    out = os.path.join(HERE, "results", "read")
    os.makedirs(out, exist_ok=True)
    json.dump(dict(records=recs, result=res), open(os.path.join(out, "S2_READ.json"), "w"), indent=1, default=float)
    open(os.path.join(out, "S2_READ.md"), "w").write(report_md(res, "PH2S Stage 2 read (PH2S_SEAL_2.0) — F2"))
    print(report_md(res, "PH2S Stage 2 read"))


def dryrun(seed=20261014):
    pred = predictions()
    xs = sorted(float(e) for e in pred)
    interp = lambda l: float(np.interp(l, xs, [pred[k] for k in sorted(pred, key=float)]))
    out = {}
    # (i) F1 through the read path (seen data)
    import s1lib as S1
    f1, repro = {}, {}
    for name, (fname, _, _) in S1.F1.items():
        _, x = decode(os.path.join(FRESH, fname))
        rec, lad = file_record(x)
        stored = json.load(open(os.path.join(TAP, f"zeros_{name}.json")))
        repro[name] = max(abs(float(np.max(np.abs(np.asarray(lad[str(b)]["sums"]) - np.asarray(stored["ladder"][str(b)]["sums"])))))
                          for b in T.LADDER)
        if name != "F1x":
            f1[name] = dict(g=rec["g"], se_g=rec["se_g"], g_pred=interp(F1_ELL[name]))
        print(name, "ĝ_B %.4f ± %.4f  pred(interp) %.4f  max |Δ sums| vs stored %.1e"
              % (rec["g"], rec["se_g"], interp(F1_ELL[name]), repro[name]), flush=True)
    w_f1 = pool_weights({n: windows_from_range(S1.F1[n][1], S1.F1[n][2]) for n in f1})
    out["F1_seen"] = evaluate(f1, w_f1)
    out["F1_seen"].update(expected="PASS", sums_reproduce_stored_max_abs=repro)
    # (ii)/(iii) GUE stand-in at F2 geometry: windows drawn i.i.d. from the pooled Stage 2 GUE window sums
    rng = np.random.default_rng(seed)
    G = [json.load(open(os.path.join(TAP_F2GUE, f))) for f in sorted(os.listdir(TAP_F2GUE)) if f.startswith("gue_gue_L1000000")]
    pool = {b: np.concatenate([np.asarray(g["ladder"][str(b)]["sums"]) for g in G]) for b in (100, 10_000)}
    nw = f2_windows()
    stand = {}
    for ell in F2:
        stand[ell] = stats_from_sums(rng.choice(pool[100], nw[ell][100]), rng.choice(pool[10_000], nw[ell][10_000]))
    W = pool_weights(nw)
    out["GUE_vs_zeta"] = evaluate({e: dict(g=g, se_g=s, g_pred=pred[e]) for e, (g, s) in stand.items()}, W)
    out["GUE_vs_zeta"]["expected"] = "FAIL"
    out["GUE_vs_GUE"] = evaluate({e: dict(g=g, se_g=s, g_pred=G_GUE_B) for e, (g, s) in stand.items()}, W)
    out["GUE_vs_GUE"]["expected"] = "PASS"
    # (iv) guard witness: a would-be PASS (ĝ = prediction) with per-file SE 0.10 -> 2·SE_pool ≥ 0.089 > 0.07
    out["guard_witness"] = evaluate({e: dict(g=pred[e], se_g=0.10, g_pred=pred[e]) for e in F2}, W)
    out["guard_witness"]["expected"] = "NOT RESOLVABLE"
    out["as_expected"] = {k: out[k]["verdict"] == out[k]["expected"] for k in ("F1_seen", "GUE_vs_zeta", "GUE_vs_GUE",
                                                                             "guard_witness")}
    out["F1_sums_reproduce"] = max(repro.values()) < 1e-6
    d = os.path.join(HERE, "results", "dryrun")
    os.makedirs(d, exist_ok=True)
    json.dump(out, open(os.path.join(d, "S2_DRYRUN.json"), "w"), indent=1, default=float)
    print({k: out[k]["verdict"] for k in out["as_expected"]}, "as expected:", out["as_expected"],
          "F1 sums reproduce:", out["F1_sums_reproduce"])
    print(report_md(out["F1_seen"], "Dry run: F1 (seen; interpolated prediction)"))


if __name__ == "__main__":
    {"read": read, "dryrun": dryrun}[sys.argv[1]]()
