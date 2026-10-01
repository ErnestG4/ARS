"""A0r scoring wrapper (A0R_PREREG.md §2, sealed 94d18ae). COMMITTED BEFORE ANY A0r OUTPUT IS READ (2026-10-01).

Runs the SEALED Q1 pipeline on the identical-config rerun A0r with A0 as the reference, substituting ONLY the arm name.
No sealed file is edited: every sealed module is imported and its arm tables are extended at runtime, or (where an arm
tuple is a literal inside a function) its source is read, sha256-pinned against armb/B4_SEAL.json, and re-executed with
that literal replaced -- the substitutions are listed in the result JSON. The B4 seal check (b4_analyze.verify_seal)
runs first and fails closed.

Stages (each resumable; outputs under results/armb_a0r_*):
  1. extract   b4_extract.run_arm("A0r") -- GPU, the sealed B4 extraction on A0r's grid (= A0's), pulling the sha-verified
               checkpoints from spot. STOPS extended in b4_extract and grids (A0r: 3000).
  2. calib     noise_calib.calib_q1 on A0r's grid (identical to A0's grid and stop; computed anyway, same function, own rng
               draw) -> armb_a0r_noise_calibration.json
  3. licence   the q1_warp_v2 cell computation for X = "A0r" (W_X = 1430 = W_0: the three time maps coincide, so the cell
               cannot be LICENSED to separate models -- expected -- but its c_fit is exactly the licence for "fits the
               identity map within noise": the 99th percentile of the fit ratio under the true model at that noise level).
               -> armb_a0r_q1_warp_licence.json
  4. q1        b4_analyze.q1() verbatim with ("A1", "A2") -> ("A0r",) and the licence/calibration files pointed at the
               A0r ones -> armb_a0r_q1.json. Whatever route it takes (E4 or LOCATION) is reported as the sealed pipeline's
               known-answer reading.
  5. identity  W.decide(g0, y0, gX, yX, "A0r", r_star, c_fit) at A0r's calibrated noise level (conservative as in q1():
               c_fit = min over iid/ar, r_star = max): fit ratio of A0r vs A0 under the (coincident) maps, and c_pair =
               relative RMS of (A0r - A0)/A0 over the window for TP_O and TP_MLPOUT; A2's banked E4 fit ratio and its
               best-map relative RMS residual recomputed on the same footing for comparison.
  verdict (A0R_PREREG §2, read mechanically; 'licence margin' operationalised here, before the data is read, as the
  licence's SSE-ratio margin r* applied to squared residuals: (misfit_A2 / c_pair)^2 >= r*):
    (a) identity within noise (fit_ratio <= c_fit for both metrics AND q1() returns no non-identity verdict) AND
        (misfit_A2 / c_pair)^2 >= r*  for both metrics                     -> "NO SIMPLE ANCHOR STANDS (c_pair quoted)"
    (b) identity within noise but the margin fails for either metric       -> "NOT RESOLVABLE (misfit within paired divergence)"
    (c) fit_ratio > c_fit for either metric, or a non-identity q1 verdict  -> "NOT RESOLVABLE (pipeline mis-reads a known null)"
    anything else (e.g. no calibrated level)                                -> "INAPPLICABLE (declared outcome; reported, not scored)"
Usage: a0r_score.py extract | calib | licence | q1 | identity | all
"""
import hashlib, json, sys, types
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent; RES = ROOT / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
ARM, W_ARM, STOP_ARM = "A0r", 1430, 3000
SUBS = []   # every substitution made, recorded in the outputs


def sealed_source(rel):
    """Source of a sealed file, verified against armb/B4_SEAL.json (fail closed)."""
    seal = json.loads((HERE / "B4_SEAL.json").read_text()); files = seal.get("files", seal)
    fp = ROOT / rel; src = fp.read_bytes(); h = hashlib.sha256(src).hexdigest()
    want = files[rel] if isinstance(files[rel], str) else files[rel].get("sha256")
    assert h == want, f"SEAL MISMATCH {rel}: {h} != {want}"
    return src.decode()


def exec_with_subs(rel, subs, name):
    src = sealed_source(rel)
    for old, new in subs:
        assert src.count(old) >= 1, (rel, old)
        src = src.replace(old, new); SUBS.append({"file": rel, "old": old, "new": new, "n": None})
    mod = types.ModuleType(name); mod.__file__ = str(ROOT / rel)
    exec(compile(src, str(ROOT / rel), "exec"), mod.__dict__)
    return mod


def inject_arm():
    import grids, q1_models as QM, q1_warp as W
    grids.STOPS[ARM] = STOP_ARM; QM.ARMS[ARM] = W_ARM; QM._CX[ARM] = QM.cum(W_ARM, 12000); W.STOP[ARM] = STOP_ARM
    SUBS.append({"runtime": f"grids.STOPS/q1_models.ARMS,_CX/q1_warp.STOP += {ARM}: W {W_ARM}, stop {STOP_ARM}"})
    return grids, QM, W


def stage_extract():
    import b4_analyze as B; B.verify_seal()
    import b4_extract as E; grids, *_ = inject_arm(); E.STOPS[ARM] = STOP_ARM
    E.run_arm(ARM); print("extract done", flush=True)


def stage_calib():
    out = RES / "armb_a0r_noise_calibration.json"
    if out.exists():
        print("calib exists"); return
    import noise_calib as NC; grids, *_ = inject_arm()
    rng = np.random.default_rng(20261001)
    g = np.array(grids.arm_grid(ARM), float)
    res = {"doc": "noise_calib.calib_q1 on A0r's grid (== A0's), a0r_score.py stage 2", "q1": {ARM: NC.calib_q1(g, STOP_ARM, rng)}}
    out.write_text(json.dumps(res, indent=1, default=float)); print("calib written", flush=True)


def stage_licence():
    out = RES / "armb_a0r_q1_warp_licence.json"
    if out.exists() and len(json.loads(out.read_text())["cells"]) >= 8:
        print("licence exists"); return
    inject_arm()
    M = exec_with_subs("armb/q1_warp_v2.py",
                       [('for X in ("A1", "A2"):', f'for X in ("{ARM}",):'),
                        ('OUT = ROOT / "results" / "armb_q1_warp_licence_v2.json"', f'OUT = ROOT / "results" / "{out.name}"')],
                       "q1_warp_v2_a0r")
    M.main(); print("licence written", flush=True)


def stage_q1():
    inject_arm()
    cal0 = json.loads((RES / "armb_noise_calibration.json").read_text()); calr = json.loads((RES / "armb_a0r_noise_calibration.json").read_text())
    merged = RES / "armb_a0r_noise_calibration_merged.json"
    merged.write_text(json.dumps({"q1": {**cal0["q1"], **calr["q1"]}, "q2": cal0.get("q2", {})}, indent=1))
    B = exec_with_subs("armb/b4_analyze.py",
                       [('for X in ("A1", "A2"):', f'for X in ("{ARM}",):'),
                        ('for X in ("A1", "A2") if', f'for X in ("{ARM}",) if'),
                        ('load_json("armb_q1_warp_licence_v2.json")', 'load_json("armb_a0r_q1_warp_licence.json")'),
                        ('load_json("armb_noise_calibration.json")["q1"]', 'load_json("armb_a0r_noise_calibration_merged.json")["q1"]'),
                        ('STOPS = {"A0": 3000, "A1": 5000, "A2": 3000, "M0s1": 3000, "M0s2": 3000}',
                         'STOPS = {"A0": 3000, "A1": 5000, "A2": 3000, "M0s1": 3000, "M0s2": 3000, "A0r": 3000}')],
                       "b4_analyze_a0r")
    B.verify_seal(); B.PROV.clear(); res = B.q1()
    res["substitutions"] = SUBS; res["provenance"] = {"n_cache_files": len(B.PROV), "cache_sha256": dict(B.PROV)}
    (RES / "armb_a0r_q1.json").write_text(json.dumps(res, indent=1, default=float)); print("q1 written:", {k: v["VERDICT"] for k, v in res.items() if isinstance(v, dict) and "VERDICT" in v}, flush=True)


def stage_identity():
    grids, QM, W = inject_arm()
    import b4_analyze as B, noise_calib as NC
    B.STOPS[ARM] = STOP_ARM
    import q1_warp_v2 as V2                       # installs W.window = window_armgrid (arm grids)
    cal = json.loads((RES / "armb_a0r_noise_calibration_merged.json").read_text())["q1"]
    lic = json.loads((RES / "armb_a0r_q1_warp_licence.json").read_text())["cells"]
    lic2 = json.loads((RES / "armb_q1_warp_licence_v2.json").read_text())["cells"]
    q1_banked = json.loads((RES / "armb_b4_q1.json").read_text())
    out = {"doc": __doc__.split("Stages")[0], "metrics": {}}
    g0 = np.array(B.grid("A0"), float); gr = np.array(B.grid(ARM), float)
    for M, name in (("O", "TP_O"), ("MLP_OUT", "TP_MLPOUT")):
        y0 = B.traj("A0", B.grid("A0"), M); yr = B.traj(ARM, B.grid(ARM), M)
        m0 = float(NC.measure(y0, 9, True)); mr = float(NC.measure(yr, 9, True))
        L0 = NC.level(m0, cal["A0"], NC.REL); Lr = NC.level(mr, cal[ARM], NC.REL)
        lvl = None if (L0 is None or Lr is None) else max(L0, Lr)
        rec = {"noise_measured": {"A0": m0, ARM: mr}, "level": {"A0": L0, ARM: Lr, "row": lvl}}
        if lvl is not None:
            cells = [lic.get(f"{ARM}_s{lvl}_{t}") for t in ("iid", "ar")]
            c_fit = min(c["c_fit"] for c in cells); r_star = max((c["r_star"] or 1.0) for c in cells)
            dec, sse, fr = W.decide(g0, y0, gr, yr, ARM, r_star, c_fit)
            w = np.isin(gr, W.window(ARM)); c_pair = float(np.sqrt(np.mean(((yr[w] - np.interp(gr[w], g0, y0)) / np.interp(gr[w], g0, y0)) ** 2)))
            # A2 on the same footing: best-map relative RMS residual over its window, from the banked cache
            g2 = np.array(B.grid("A2"), float); y2 = B.traj("A2", B.grid("A2"), M)
            w2 = np.isin(g2, W.window("A2")); best2 = None
            a2 = q1_banked[name]["A2"]
            for m in W.MODELS:
                p = W.interp0(g0, y0, W.tau(g2[w2], "A2", m)); A = np.vstack([np.ones_like(p), p]).T
                c, *_ = np.linalg.lstsq(A, y2[w2], rcond=None); r = float(np.sqrt(np.mean(((y2[w2] - A @ c) / y2[w2]) ** 2)))
                if best2 is None or r < best2[1]:
                    best2 = (m, r)
            misfit_A2 = best2[1]
            # the licence's own margin: r* of A2's cell row (as used in its verdict), applied to squared residuals
            r_star_A2 = a2.get("r_star") or 1.0
            rec.update({"c_fit_identity": c_fit, "r_star_identity_cell": r_star, "fit_ratio_identity": fr, "decide": dec,
                        "sse": sse, "c_pair_relRMS": c_pair, "A2_best_map": best2[0], "A2_misfit_relRMS": misfit_A2,
                        "A2_banked": {k: a2.get(k) for k in ("decision", "fit_ratio", "c_fit", "r_star", "route")},
                        "margin_ratio_sq": (misfit_A2 / c_pair) ** 2 if c_pair > 0 else None, "r_star_A2": r_star_A2})
        out["metrics"][name] = rec
    q1r = json.loads((RES / "armb_a0r_q1.json").read_text())
    nonid = []
    for name in ("TP_O", "TP_MLPOUT"):
        v = q1r[name]["VERDICT"]; d = q1r[name][ARM].get("decision", "")
        if "NO SIMPLE ANCHOR" in v or v.startswith("SUPPORTED") or "NO_SIMPLE_ANCHOR" in d or d in ("STEP", "WARMUP", "LR_INT"):
            nonid.append((name, v, d))        # any map preference or NSA on an identity run = non-identity reading
    out["q1_sealed_verdicts"] = {n: {"VERDICT": q1r[n]["VERDICT"], ARM: q1r[n][ARM]} for n in ("TP_O", "TP_MLPOUT")}
    recs = out["metrics"]
    if any("fit_ratio_identity" not in r for r in recs.values()):
        verdict = "INAPPLICABLE (no calibrated noise level for a metric; reported, not scored)"
    elif nonid or any(r["fit_ratio_identity"] > r["c_fit_identity"] for r in recs.values()):
        verdict = "NOT RESOLVABLE (pipeline mis-reads a known null)"
    elif all(r["margin_ratio_sq"] is not None and r["margin_ratio_sq"] >= r["r_star_A2"] for r in recs.values()):
        verdict = "NO SIMPLE ANCHOR STANDS (c_pair quoted)"
    else:
        verdict = "NOT RESOLVABLE (misfit within paired divergence)"
    out["VERDICT"] = verdict; out["substitutions"] = SUBS
    (RES / "armb_a0r_identity.json").write_text(json.dumps(out, indent=1, default=float))
    print("identity written; VERDICT:", verdict, flush=True)
    for n, r in recs.items():
        print(n, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k in ("fit_ratio_identity", "c_fit_identity", "decide", "c_pair_relRMS", "A2_misfit_relRMS", "margin_ratio_sq", "r_star_A2")})


if __name__ == "__main__":
    which = sys.argv[1]
    for s, fn in (("extract", stage_extract), ("calib", stage_calib), ("licence", stage_licence), ("q1", stage_q1), ("identity", stage_identity)):
        if which in (s, "all"):
            print("== stage", s, flush=True); fn()
