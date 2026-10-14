"""Route (a) read, dry run, refusal checks and seal builder (forty-first to forty-fourth rounds). The model, the estimator,
the calibration and the decision rule are route_a_read.py's (rule committed fd143231/ef7119f4; calibration declared and
pinned 397fe1f3); this file adds only the read's safeguards and the outcome table of the forty-third round.

  python route_a_sealread.py read [DATA_DIR]       REFUSED unless seals/ROUTE_A_SEAL.json exists and pins this code, the
                                                   prediction and the calibration, and all five F3 md5s match the pins
                                                   BEFORE any file is decoded; each file's heights must lie in its range
  python route_a_sealread.py sample OUT_DIR       (char, GPU) CUE_1000 spacings for the five stand-ins (.npy)
  python route_a_sealread.py synth OUT_DIR F       a stand-in for F3 file F: those spacings placed at its geometry
  python route_a_sealread.py dryrun SYNTH_DIR      the read() code on the stand-ins, under a dry-run seal pinning their md5s
  python route_a_sealread.py refusals              red paths: every refusal fires on a constructed defect
  python route_a_sealread.py seal [--check]        build seals/ROUTE_A_SEAL.json (on Will's go; commit + tag are his)

Outcome table (forty-third round; MODEL MISFIT reported independently of the row):
  (a) verdict PASS (μ̃_pool in the band, with the rule's per-file and GoF conditions)            → PASS
  (b) not PASS and μ̃_pool ∈ [0.955, 0.985]  → FAIL, read "the spacing law deviates from CS n ≤ 5 at μ = 1, in the
      direction of Phase 2's fitted law"; attributed (forty-fourth round) by the cumulant increments of
      results/route_a_cumul.json — pair arithmetic (C2), connected higher order (C3−C2, C4−C3, C5−C4) — and the
      estimator; truncation only if the n = 5 check fails to exclude it; a follow-up to separate them is pre-declared
  (c) any other μ̃_pool                      → FAIL, unattributed
  The rule's verdict (MODEL MISFIT > UNRESOLVED > PASS/FAIL) is reported as is beside the row.
"""
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
import ph2lib  # noqa: E402
import route_a_read as RR  # noqa: E402

SEAL = os.path.join(HERE, "seals", "ROUTE_A_SEAL.json")
TEXT = os.path.join(HERE, "ROUTE_A_SEAL.md")
FRESH = os.path.join(HERE, "..", "ph2r2", "data", "platt_fresh")
FRESH_PINS = os.path.join(HERE, "..", "ph2r2", "FRESH_SETS_F1_F3.md")
CODE = ["route_a_read.py", "route_a_sealread.py", "../ph2/ph2lib.py"]
F3_MD5 = {"zeros_15146000.dat": "12759c6bf4892f90244d240a7893c96a",
          "zeros_25646000.dat": "17769568c69cbabc1c47138f7159812e",
          "zeros_248246000.dat": "763374d804b79351fa5890bc56cae1b4",
          "zeros_2373446000.dat": "10af7827aba9e214d135847c686e6d69",
          "zeros_10639046000.dat": "6203cd45f34fb389b3be1108bdf9c913"}
ROW_B = (0.955, 0.985)
SEED = 20261014
DPS = 45
DERIVED = {"split": "results/route_a_split.json", "cumul": "results/route_a_cumul.json",
           "equiv": "results/route_a_equiv.json", "calib": "results/calib/route_a_calib_declared.json"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def decode(path, t0, t1):
    """The read's decode (route_a_read.spacings_from_platt's path) with the height-range check."""
    pairs, _ = ph2lib.read_platt_file(path)
    g = ph2lib.platt_to_mpf(pairs, dps=DPS)
    if not (g[0] >= t0 and g[-1] < t1):
        raise SystemExit(f"REFUSED: {path} heights [{float(g[0])}, {float(g[-1])}] outside the pinned [{t0}, {t1})")
    s = ph2lib.unfolded_spacings(g, dps=DPS - 5)
    return s, float(g[0]), float(g[-1])


def outcome(v):
    """The forty-third round's row for a rule() result v (the verdict is reported beside it, unchanged)."""
    if v["verdict"] == "PASS":
        return "a"
    return "b" if ROW_B[0] <= v["mu_pool"] <= ROW_B[1] else "c"


def evaluate(per_file):
    w, _ = RR.weights()
    v = RR.rule(per_file, w, RR.calib())
    v["row"] = outcome(v)
    v["model_misfit_flag"] = len(v["misfit_files"]) >= RR.MISFIT_FILES
    return v


def check_seal(seal_path):
    if not os.path.exists(seal_path):
        raise SystemExit("REFUSED: no ROUTE_A_SEAL.json — F3 zeros are not decoded before the seal")
    seal = json.load(open(seal_path))
    for f in CODE:
        if sha(os.path.join(HERE, f)) != seal["code_sha256"][f]:
            raise SystemExit(f"REFUSED: {f} differs from the sealed code")
    if sha(RR.PRED) != seal["prediction_sha256"]:
        raise SystemExit("REFUSED: the prediction file differs from the sealed one")
    if RR.CALIB_SHA256 != seal["calibration_sha256"] or sha(RR.CALIB_JSON) != seal["calibration_sha256"]:
        raise SystemExit("REFUSED: the calibration differs from the sealed one")
    w, _ = RR.weights()
    if any(abs(w[f] - seal["weights"][f]) > 1e-15 for f in RR.F3):
        raise SystemExit("REFUSED: pooling weights differ from the sealed ones")
    return seal


def read(data_dir=FRESH, seal_path=SEAL, out_dir=None, seed=SEED):
    seal = check_seal(seal_path)
    paths = {}
    for f in RR.F3:                                            # every md5 before any decode
        p = os.path.join(data_dir, f)
        if not os.path.exists(p) or md5(p) != seal["f3_md5"][f]:
            raise SystemExit(f"REFUSED: {p} missing or md5 differs from the pin")
        paths[f] = p
    from multiprocessing import Pool
    with Pool(len(paths)) as pool:                             # one process per file; seeds fixed per file
        got = pool.map(_one_file, [(f, p, seed, i) for i, (f, p) in enumerate(paths.items())])
    recs = dict(got)
    per_file = {f: {k: recs[f][k] for k in ("mu", "flag", "se", "n", "n_window", "chi2")} for f in recs}
    v = evaluate(per_file)
    res = dict(seal=seal.get("seal"), records=recs, result=v)
    out_dir = out_dir or os.path.join(HERE, "results", "read")
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, "ROUTE_A_READ.json"), "w"), indent=1, default=float)
    open(os.path.join(out_dir, "ROUTE_A_READ.md"), "w").write(report_md(v))
    print(report_md(v))
    return res


def _one_file(job):
    f, p, seed, i = job
    t0, t1 = RR.F3[f]
    s, g0, g1 = decode(p, t0, t1)
    fit = RR.MuFit.for_file(f)
    r = RR.fit_file(fit, s, np.random.default_rng([seed, i]), RR.BLOCK_LENS)
    z, edges = fit.gof_detail(s, r["mu"])
    print(f"{f}: n {len(s)}  μ̂ {r['mu']:+.4f}  SE " + " ".join(f"{k}:{x:.4f}" for k, x in r["se"].items())
          + f"  χ² {r['chi2']:.1f}", flush=True)
    return f, dict(r, first=g0, last=g1, mean_spacing=float(s.mean()), gof_residuals=z.tolist(), gof_edges=edges.tolist(),
                   sha256_spacings=hashlib.sha256(np.ascontiguousarray(s).tobytes()).hexdigest())


def report_md(v):
    L = [f"verdict (sealed rule): **{v['verdict']}**;  outcome row: **({v['row']})**"
         + ("  — MODEL MISFIT flagged" if v["model_misfit_flag"] else ""),
         f"μ̃_pool = {v['mu_pool']:.4f} ± {2 * v['se_pool']:.4f} (95% CI [{v['ci95'][0]:.4f}, {v['ci95'][1]:.4f}]); "
         f"files within 3 SE: {v['files_within_3se']}/5; GoF pass: {v['gof_pass_files']}/5; misfit: {v['misfit_files']}",
         "", "| file | μ̃_f | SE_f |", "|---|---|---|"]
    L += [f"| {f} | {v['mu_file'][f]:+.4f} | {v['se_file'][f]:.4f} |" for f in v["mu_file"]]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- dry run: CUE stand-ins at F3 geometry
def sample(out_dir):
    """CUE_1000 spacings for each F3 stand-in (char GPU sampler, as the calibration; seeds disjoint from it): the
    pre-data spacing count less 100, so the last placed level stays below t1."""
    import cbe
    os.makedirs(out_dir, exist_ok=True)
    _, nf = RR.weights()
    for i, f in enumerate(RR.F3):
        n = int(nf[f]) - 100
        rng = np.random.default_rng([SEED, 7, i])
        need = -(-n // 1000)
        sp = np.concatenate([cbe.spacings(cbe.sample(rng, min(2000, need - k), 1000, 2.0, gpu=True)[0]).ravel()
                             for k in range(0, need, 2000)])[:n]
        np.save(os.path.join(out_dir, f + ".npy"), sp)
        print(f, n, float(sp.min()), flush=True)


def synth(out_dir, f):
    """The stand-in for F3 file f: sample()'s spacings placed at the file's height with exact θ, in the Platt format."""
    sp = np.load(os.path.join(out_dir, f + ".npy"))
    g = RR.place(RR.F3[f][0], sp)
    RR.write_platt(os.path.join(out_dir, f), g)
    print(f, len(sp), md5(os.path.join(out_dir, f)), flush=True)


def dry_seal(path, md5s):
    w, _ = RR.weights()
    seal = dict(seal="DRYRUN (not a seal)", code_sha256={f: sha(os.path.join(HERE, f)) for f in CODE},
                prediction_sha256=sha(RR.PRED), calibration_sha256=RR.CALIB_SHA256, weights=w, f3_md5=md5s)
    json.dump(seal, open(path, "w"), indent=1)


def dryrun(synth_dir):
    """read() on the CUE stand-ins (expected: not PASS, row (c), μ̃_pool ≈ 0), then the rule's rows on the same per-file
    results shifted to μ = 1 (expected PASS, row (a)) and to Phase 2's fitted SECONDARY μ* (expected row (b))."""
    out = os.path.join(HERE, "results", "dryrun")
    os.makedirs(out, exist_ok=True)
    md5s = {f: md5(os.path.join(synth_dir, f)) for f in RR.F3}
    sp = os.path.join(out, "DRYRUN_SEAL.json")
    dry_seal(sp, md5s)
    res = read(synth_dir, sp, out)
    per = {f: {k: res["records"][f][k] for k in ("mu", "se", "chi2")} for f in RR.F3}
    eqv = json.load(open(os.path.join(HERE, DERIVED["equiv"])))["files"]
    mus = {f: eqv[f]["mu"]["fit_sec: Phase 2 SECONDARY fitted (interp.)"] for f in RR.F3}
    shifted = {}
    for name, sh in (("mu1", {f: 1.0 for f in RR.F3}), ("fit_sec", mus)):
        v = evaluate({f: dict(per[f], mu=per[f]["mu"] + sh[f]) for f in RR.F3})
        shifted[name] = dict(verdict=v["verdict"], row=v["row"], mu_pool=v["mu_pool"], se_pool=v["se_pool"])
    expect = dict(standin_row_c=res["result"]["row"] == "c" and res["result"]["verdict"] != "PASS",
                  mu1_PASS=shifted["mu1"]["verdict"] == "PASS" and shifted["mu1"]["row"] == "a",
                  fit_sec_row_b=shifted["fit_sec"]["row"] == "b")
    rec = dict(standin=res["result"], shifted=shifted, as_expected=expect, md5=md5s)
    json.dump(rec, open(os.path.join(out, "ROUTE_A_DRYRUN.json"), "w"), indent=1, default=float)
    print("dry run:", {k: v for k, v in shifted.items()}, "as expected:", expect, flush=True)
    return 0 if all(expect.values()) else 1


# ---------------------------------------------------------------- refusal red paths
def refusals():
    """Each refusal must fire on a constructed defect; nothing is decoded (every case stops before decode)."""
    tmp = tempfile.mkdtemp(dir=os.path.join(HERE, "results"))
    cases = {}
    try:
        for f in RR.F3:
            open(os.path.join(tmp, f), "wb").write(b"not a zero file")
        good = {f: md5(os.path.join(tmp, f)) for f in RR.F3}
        sp = os.path.join(tmp, "seal.json")

        def attempt(name, mutate=None, files=good, data=tmp):
            dry_seal(sp, dict(files))
            if mutate:
                s = json.load(open(sp))
                mutate(s)
                json.dump(s, open(sp, "w"))
            try:
                read(data, sp, os.path.join(tmp, "out"))
                cases[name] = "NOT REFUSED"
            except SystemExit as e:
                cases[name] = str(e)
            except Exception as e:                                        # noqa: BLE001 (a crash is not a refusal)
                cases[name] = f"CRASH {type(e).__name__}: {e}"

        dry_seal(sp, dict(good))                      # positive control: a correct seal passes every pin check
        try:
            check_seal(sp)
            control = all(md5(os.path.join(tmp, f)) == good[f] for f in RR.F3)
        except SystemExit:
            control = False
        try:
            read(tmp, os.path.join(tmp, "absent.json"), os.path.join(tmp, "out"))
            cases["no_seal"] = "NOT REFUSED"
        except SystemExit as e:
            cases["no_seal"] = str(e)
        attempt("code_mismatch", lambda s: s["code_sha256"].update({CODE[0]: "0" * 64}))
        attempt("prediction_mismatch", lambda s: s.update(prediction_sha256="0" * 64))
        attempt("calibration_mismatch", lambda s: s.update(calibration_sha256="0" * 64))
        attempt("weights_mismatch", lambda s: s["weights"].update({list(RR.F3)[0]: 0.5}))
        attempt("md5_mismatch", files=dict(good, **{list(RR.F3)[-1]: "0" * 32}))
        os.remove(os.path.join(tmp, list(RR.F3)[2]))
        attempt("file_missing")
        # the height-range check, on a two-zero Platt file below file 1's range
        import mpmath as mp
        lo = os.path.join(tmp, "lo.dat")
        RR.write_platt(lo, [mp.mpf(1000.5), mp.mpf(1001.25)])
        try:
            decode(lo, *RR.F3[list(RR.F3)[0]])
            cases["heights_outside_range"] = "NOT REFUSED"
        except SystemExit as e:
            cases["heights_outside_range"] = str(e)
    finally:
        shutil.rmtree(tmp)
    ok = control and all(v.startswith("REFUSED") for v in cases.values())
    print(f"{'positive control':24s} {'passes the pin checks' if control else 'REFUSED (wrongly)'}")
    for k, v in cases.items():
        print(f"{k:24s} {v[:110]}")
    print("REFUSALS", "PASS" if ok else "FAIL")
    return ok


# ---------------------------------------------------------------- seal builder
def tagged_prediction_sha():
    rel = os.path.relpath(RR.PRED, os.path.join(HERE, "..", ".."))
    blob = subprocess.run(["git", "show", f"route-a-prediction:{rel}"], cwd=HERE, capture_output=True, check=True).stdout
    return hashlib.sha256(blob).hexdigest()


def seal(check_only=False):
    import re
    pins = dict(re.findall(r"\| (zeros_\d+\.dat) \| \[[^|]*\) \| [^|]* \| ([0-9a-f]{32}) \|", open(FRESH_PINS).read()))
    dry = json.load(open(os.path.join(HERE, "results", "dryrun", "ROUTE_A_DRYRUN.json")))
    cum = json.load(open(os.path.join(HERE, DERIVED["cumul"])))
    spl = json.load(open(os.path.join(HERE, DERIVED["split"])))
    bins = {b: json.load(open(os.path.join(HERE, "results", "ph2bins", f"{b}.json"))) for b in
            ("P1", "P2", "P3", "P4", "P5", "P6")}
    checks = dict(text_exists=os.path.exists(TEXT), dryrun_as_expected=all(dry["as_expected"].values()),
                  refusals=refusals(), f3_md5_match_pins=all(pins.get(f) == m for f, m in F3_MD5.items()),
                  prediction_is_tagged=sha(RR.PRED) == tagged_prediction_sha(),
                  calibration_pinned=sha(RR.CALIB_JSON) == RR.CALIB_SHA256, split_gate=bool(spl["gate"]["PASS"]),
                  cumul_gate=bool(cum["gate"]["PASS"]), ph2bins_bit_exact=all(b["pipeline_bit_exact"] for b in bins.values()),
                  rule_selftest=bool(RR.rule_selftest()["PASS"]))
    if not all(checks.values()):
        raise SystemExit(f"REFUSED: {[k for k, v in checks.items() if not v]}")
    if check_only:
        print("checks (nothing written):", checks)
        return 0
    w, nf = RR.weights()
    cal = RR.calib()
    out = dict(seal="ROUTE_A_SEAL", text=os.path.basename(TEXT), text_sha256=sha(TEXT),
               code_sha256={f: sha(os.path.join(HERE, f)) for f in CODE},
               prediction=dict(tag="route-a-prediction", file=os.path.relpath(RR.PRED, HERE)),
               prediction_sha256=sha(RR.PRED), calibration_sha256=RR.CALIB_SHA256,
               derived_sha256={k: sha(os.path.join(HERE, p)) for k, p in DERIVED.items()},
               f3_md5=F3_MD5, f3_files={f: dict(t0=t0, t1=t1) for f, (t0, t1) in RR.F3.items()}, weights=w, n_f=nf,
               rule=dict(misfit_files=RR.MISFIT_FILES, gof_bins=RR.GOF_BINS, gof_familywise=RR.GOF_FAMILYWISE,
                         block=cal["block"], block_lens=list(RR.BLOCK_LENS), dmu_sys=RR.DMU_SYS, s_max=RR.S_MAX,
                         T={f: cal["files"][f]["T"] for f in RR.F3}, bias={f: cal["files"][f]["bias"] for f in RR.F3}),
               outcome_rows=dict(a="PASS", b=dict(mu_pool=list(ROW_B), reading="deviates from CS n<=5 at mu = 1, in the "
                                 "direction of Phase 2's fitted law", attribution=cum["increments"]), c="FAIL, unattributed"),
               operating_characteristics=cal["operating_characteristics"], dryrun=dry["as_expected"], checks=checks)
    os.makedirs(os.path.dirname(SEAL), exist_ok=True)
    json.dump(out, open(SEAL, "w"), indent=1, sort_keys=True)
    print("wrote", SEAL)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "read":
        read(sys.argv[2] if len(sys.argv) > 2 else FRESH)
    elif cmd == "sample":
        sample(sys.argv[2])
    elif cmd == "synth":
        synth(sys.argv[2], sys.argv[3])
    elif cmd == "dryrun":
        sys.exit(dryrun(sys.argv[2]))
    elif cmd == "refusals":
        sys.exit(0 if refusals() else 1)
    elif cmd == "seal":
        sys.exit(seal("--check" in sys.argv))
