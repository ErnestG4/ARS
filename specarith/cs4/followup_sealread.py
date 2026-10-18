"""The two route (a) replications' sealed read, dry run, refusal checks, joint-reading witnesses and seal builder
(rounds 50–53; mirrors route_a_sealread.py). The estimators, calibration and rule are followup_read.py's; this file adds
only the read's safeguards and the joint reading. OBS is A (F4, the NNN spacing law) or B (F5, κ₃ of the count).

  python followup_sealread.py read OBS LABEL [DATA_DIR]   REFUSED unless seals/FOLLOWUP_<OBS>_SEAL.json exists and pins
                                    this code and every module the read imports, the interpreter, the prediction, the
                                    calibration, the weights and the derived inputs, and the prediction matches the
                                    OpenTimestamps-stamped manifest (checked without git or the seal); every md5 is
                                    checked against the pins BEFORE any file is decoded; each file's heights must lie in
                                    its range. Writes results/followup_read/<OBS>/LABEL/ and prints NO estimate.
  python followup_sealread.py compare OBS                 run1 and run2 must be bit-identical, else VOID; then the report
  python followup_sealread.py sample OUT_DIR              (char GPU) CUE_1000 spacings for the seven stand-ins (.npy)
  python followup_sealread.py synth OUT_DIR FILE          a stand-in: those spacings placed at FILE's geometry (Platt)
  python followup_sealread.py pipeline OUT_DIR FILE       the stand-in decoded by the read's path vs its own spacings
  python followup_sealread.py dryrun_prepare OBS SYNTH_DIR
  python followup_sealread.py dryrun_read OBS LABEL SYNTH_DIR
  python followup_sealread.py dryrun_record OBS SYNTH_DIR
  python followup_sealread.py refusals OBS                every refusal fires on a constructed defect
  python followup_sealread.py witness                     the joint reading on constructed verdicts
  python followup_sealread.py seal OBS [--check]          build seals/FOLLOWUP_<OBS>_SEAL.json (on Will's go)

Joint reading (round 50; declared in both seals): each test keeps its calibrated false-FAIL rate; family-wise
1 − (1 − α_A)(1 − α_B). Both PASS: replication of route (a) by two further observables. Exactly one FAIL: a FAIL for that
observable, attribution limited to "observable-specific model terms or estimator", not a refutation of route (a). Both
FAIL: route (a)'s PASS is called into question, reported plainly. Any other verdict (MODEL MISFIT, UNRESOLVED, FIT
FAILURE) is reported as such and is not a PASS.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
import followup_read as FR  # noqa: E402
import ph2lib  # noqa: E402
import route_a_read as RR  # noqa: E402

SEAL = {o: os.path.join(HERE, "seals", f"FOLLOWUP_{o}_SEAL.json") for o in "AB"}
TEXT = {o: os.path.join(HERE, f"FOLLOWUP_{o}_SEAL.md") for o in "AB"}
FRESH = os.path.join(HERE, "..", "ph2r2", "data", "platt_fresh")
FRESH_PINS = os.path.join(HERE, "..", "ph2r2", "FRESH_SETS_F4_F5.md")
CODE = ["followup_sealread.py", "followup_read.py", "followup_fit.py", "followup_nnn.py", "followup_pred.py",
        "route_a_read.py", "route_a_zeta.py", "../ph2/ph2lib.py"]
MD5 = {"A": {"zeros_252446000.dat": "4d9c80df1f369a48e985cf5f2da870e6",
             "zeros_2369246000.dat": "d2d328ee9dc75e908f4194d6aa45e0db",
             "zeros_10634846000.dat": "873b302f888a8c58642ca9a6f4952a79"},
       "B": {"zeros_36146000.dat": "8fb15afc113768103c1b3891a83f9d54",
             "zeros_244046000.dat": "4f19fac76037c7f361b1a0c12a706b9b",
             "zeros_2377646000.dat": "abbec916f56f69bc96df594e735c5401",
             "zeros_10643246000.dat": "916639a260da1c6b84b291260b5627e6"}}
TAG = {"A": "followup-a-prediction", "B": "followup-b-prediction"}
# pinned after each declaration (route (a)'s CALIB_SHA256 practice); None = not declared yet → every read refuses
CALIB_SHA256 = {"A": "3f039fce96aa6094cfc8fd94ec255ed4fce85fcf25c64d59d4f83ab008300336",
                "B": "4d5ad7eb17f03cb9ee8e767158338c3aa0b44bc495d8e2d85961ad36cc3a9428"}
DERIVED = {"A": {}, "B": {"cuen_r53": "results/followup_cuen_r53.json"}}
SEED = 20261018
DPS = 45
READ_OUT = os.path.join(HERE, "results", "followup_read")
DRY_OUT = os.path.join(HERE, "results", "followup_dryrun")
# the prediction manifest stamped with OpenTimestamps (948d1ad6; Bitcoin block 971918, dae368bb)
PRESTAMP = os.path.join(HERE, "timestamps", "FOLLOWUP_PRESTAMP_2026-10-17.txt")
PRESTAMP_OTS = PRESTAMP + ".ots"
PRESTAMP_SHA256 = "995dc21c86f47e60013997b0dcc50c0a5074fec3ce087ea5571ed48304cf82fc"
PRESTAMP_VERIFY = os.path.join(HERE, "timestamps", "FOLLOWUP_PRESTAMP_2026-10-17_VERIFY.json")
OTS_MAGIC = b"\x00OpenTimestamps\x00\x00Proof\x00\xbf\x89\xe2\xe8\x84\xe8\x92\x94"


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


def env():
    import mpmath
    import scipy
    return dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__, mpmath=mpmath.__version__)


def stamp_check(obs, pred_path=None, manifest=PRESTAMP, receipt=PRESTAMP_OTS):
    """The prediction JSON's sha256 must equal the one in the OpenTimestamps-stamped manifest, whose sha256 must be the
    digest the receipt commits to and the pinned PRESTAMP_SHA256. No git, no seal."""
    pred_path = FR.PRED[obs] if pred_path is None else pred_path
    head = open(receipt, "rb").read(len(OTS_MAGIC) + 2 + 32)
    if not (head.startswith(OTS_MAGIC) and head[len(OTS_MAGIC):len(OTS_MAGIC) + 2] == b"\x01\x08"
            and head[len(OTS_MAGIC) + 2:].hex() == PRESTAMP_SHA256):
        raise SystemExit("REFUSED: the OpenTimestamps receipt does not commit to the pinned prediction manifest")
    if sha(manifest) != PRESTAMP_SHA256:
        raise SystemExit("REFUSED: the prediction manifest differs from the OpenTimestamps-stamped one")
    m = re.search(rf"\({obs}\) prediction\s+\S+\s*\n\s*sha256 ([0-9a-f]{{64}})", open(manifest).read())
    if not m or sha(pred_path) != m.group(1):
        raise SystemExit("REFUSED: the prediction JSON's sha256 differs from the OpenTimestamps-stamped manifest's")
    return m.group(1)


def check_seal(obs, seal_path):
    if not os.path.exists(seal_path):
        raise SystemExit(f"REFUSED: no FOLLOWUP_{obs}_SEAL.json — F{FR.SET[obs]} zeros are not decoded before the seal")
    stamp_check(obs)
    seal = json.load(open(seal_path))
    if seal.get("env") != env():
        raise SystemExit(f"REFUSED: interpreter {env()} differs from the sealed {seal.get('env')}")
    for f in CODE:
        if sha(os.path.join(HERE, f)) != seal["code_sha256"][f]:
            raise SystemExit(f"REFUSED: {f} differs from the sealed code")
    if sha(FR.PRED[obs]) != seal["prediction_sha256"]:
        raise SystemExit("REFUSED: the prediction file differs from the sealed one")
    if CALIB_SHA256[obs] is None or CALIB_SHA256[obs] != seal["calibration_sha256"] \
            or sha(FR.CALIB[obs]) != seal["calibration_sha256"]:
        raise SystemExit("REFUSED: the calibration differs from the sealed one (or is not declared)")
    w, _ = FR.weights(obs)
    if any(abs(w[f] - seal["weights"][f]) > 1e-15 for f in FR.FILES[obs]):
        raise SystemExit("REFUSED: pooling weights differ from the sealed ones")
    for k, h in seal["derived_sha256"].items():
        if sha(os.path.join(HERE, DERIVED[obs][k])) != h:
            raise SystemExit(f"REFUSED: derived file {DERIVED[obs][k]} differs from the sealed one")
    return seal


def decode(path, t0, t1):
    """The read's decode (Phase 2's Platt path) with the height-range check; returns the zeros (mpf)."""
    pairs, _ = ph2lib.read_platt_file(path)
    g = ph2lib.platt_to_mpf(pairs, dps=DPS)
    if not (g[0] >= t0 and g[-1] < t1):
        raise SystemExit(f"REFUSED: {path} heights [{float(g[0])}, {float(g[-1])}] outside the pinned [{t0}, {t1})")
    return g


def sequence(obs, f, path):
    t0, t1 = FR.FILES[obs][f]
    g = decode(path, t0, t1)
    s, x = FR.unfold(g, t0, dps=DPS - 5)
    meta = dict(first=float(g[0]), last=float(g[-1]), n_zeros=len(g), mean_spacing=float(s.mean()),
                sha256_spacings=hashlib.sha256(np.ascontiguousarray(s).tobytes()).hexdigest())
    seq = FR.seq_A(s) if obs == "A" else FR.seq_B(x)
    return seq, meta


def _one_file(job):
    obs, f, p, seed, i = job
    seq, meta = sequence(obs, f, p)
    pred = json.load(open(FR.PRED[obs]))
    rng = np.random.default_rng([seed, FR.SET[obs], i])
    if obs == "A":
        m = FR.ModelA(pred["files"][f]["dp_nodes"], pred["n_f"][f])
        r = FR.fit_file_A(m, seq, rng)
        meta.update(gof_groups=m.n_groups, gof_merges=m.merges)
    else:
        r = FR.fit_file_B(pred["files"][f], seq, rng)
    meta["sha256_sequence"] = hashlib.sha256(np.ascontiguousarray(seq).tobytes()).hexdigest()
    print(f"{f}: decoded {meta['n_zeros']} zeros, fitted", flush=True)
    return f, dict(r, **meta)


def evaluate(obs, per_file, cal):
    pred = json.load(open(FR.PRED[obs]))
    w, _ = FR.weights(obs)
    return FR.rule(obs, per_file, w, cal, FR.dmu_sys(obs, pred), FR.g_files(obs, pred))


def read(obs, label, data_dir=FRESH, seal_path=None, out_base=None, seed=SEED):
    """One read into out_base/OBS/label. Prints no estimate: interpretation waits for compare()."""
    seal_path = SEAL[obs] if seal_path is None else seal_path
    out_base = READ_OUT if out_base is None else out_base
    seal = check_seal(obs, seal_path)
    paths = {}
    for f in FR.FILES[obs]:                                     # every md5 before any decode
        p = os.path.join(data_dir, f)
        if not os.path.exists(p) or md5(p) != seal["md5"][f]:
            raise SystemExit(f"REFUSED: {p} missing or md5 differs from the pin")
        paths[f] = p
    from multiprocessing import Pool
    with Pool(len(paths)) as pool:
        got = pool.map(_one_file, [(obs, f, p, seed, i) for i, (f, p) in enumerate(paths.items())])
    recs = dict(got)
    cal = json.load(open(FR.CALIB[obs]))
    v = evaluate(obs, recs, cal)
    res = dict(seal=seal.get("seal"), observable=obs, env=env(), records=recs, result=v)
    out_dir = os.path.join(out_base, obs, label)
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, "FOLLOWUP_READ.json"), "w"), indent=1, default=float)
    print(f"read {obs}/{label}: written to {out_dir} (no estimate printed; run compare after the second run)", flush=True)
    return res


def compare(obs, out_base=None):
    out_base = os.path.join(READ_OUT if out_base is None else out_base, obs)
    a, b = (os.path.join(out_base, r, "FOLLOWUP_READ.json") for r in ("run1", "run2"))
    ha, hb = sha(a), sha(b)
    ok = ha == hb
    json.dump(dict(run1_sha256=ha, run2_sha256=hb, bit_identical=ok), open(os.path.join(out_base, "COMPARE.json"), "w"),
              indent=1)
    if not ok:
        raise SystemExit(f"VOID: run1 and run2 differ ({ha[:16]} vs {hb[:16]}); the read is void, nothing is interpreted")
    res = json.load(open(a))
    open(os.path.join(out_base, "FOLLOWUP_READ.md"), "w").write(report_md(obs, res["result"]))
    print(f"run1 = run2 bit for bit (sha256 {ha[:16]}…)\n" + report_md(obs, res["result"]))
    return res


def report_md(obs, v):
    if v["verdict"] == "FIT FAILURE":
        return f"({obs}) verdict (sealed rule): **FIT FAILURE** — {v['failures']}\n"
    n = len(v["mu_file"])
    L = [f"({obs}) verdict (sealed rule): **{v['verdict']}**",
         f"μ̃_pool = {v['mu_pool']:.4f} ± {2 * v['se_pool']:.4f} (band ±{v['band']:.4f}); files within 3 SE: "
         f"{v['files_within_3se']}/{n} (need {v['files_needed']})"
         + (f"; misfit: {v['misfit_files']}" if obs == "A" else ""), "", "| file | μ̃_f | SE_f |", "|---|---|---|"]
    L += [f"| {f} | {v['mu_file'][f]:+.4f} | {v['se_file'][f]:.4f} |" for f in v["mu_file"]]
    return "\n".join(L) + "\n"


def joint(va, vb):
    """Round 50's joint reading on the two verdicts."""
    a, b = va["verdict"], vb["verdict"]
    if a == "PASS" and b == "PASS":
        return "both PASS: replication of route (a) by two further observables"
    if {a, b} <= {"PASS", "FAIL"} and (a == "FAIL") != (b == "FAIL"):
        o = "A" if a == "FAIL" else "B"
        return (f"exactly one FAIL ({o}): a FAIL for that observable, attributed only to observable-specific model terms "
                "or estimator; not a refutation of route (a)")
    if a == "FAIL" and b == "FAIL":
        return "both FAIL: route (a)'s PASS is called into question"
    return f"no joint reading: (A) {a}, (B) {b} — reported as such; not a PASS"


def familywise(alpha_a, alpha_b):
    return 1 - (1 - alpha_a) * (1 - alpha_b)


# ---------------------------------------------------------------- stand-ins: pipeline identity and dry run
def _all_files():
    return [(o, i, f) for o in "AB" for i, f in enumerate(FR.FILES[o])]


def sample(out_dir):
    """CUE_1000 spacings for each F4/F5 stand-in (char GPU; seeds [20261017, 53, 7, SET, i], disjoint from every other
    use): the pre-data count less 100, so the last placed level stays below t1."""
    import cbe
    os.makedirs(out_dir, exist_ok=True)
    for o, i, f in _all_files():
        _, nf = FR.weights(o)
        n = int(nf[f]) - 100
        rng = np.random.default_rng([20261017, 53, 7, FR.SET[o], i])
        need = -(-n // 1000)
        sp = np.concatenate([cbe.spacings(cbe.sample(rng, min(2000, need - k), 1000, 2.0, gpu=True)[0]).ravel()
                             for k in range(0, need, 2000)])[:n]
        np.save(os.path.join(out_dir, f + ".npy"), sp)
        print(f, n, float(sp.min()), flush=True)


def _obs_of(f):
    return next(o for o in "AB" if f in FR.FILES[o])


def synth(out_dir, f):
    sp = np.load(os.path.join(out_dir, f + ".npy"))
    g = RR.place(FR.FILES[_obs_of(f)][f][0], sp)
    RR.write_platt(os.path.join(out_dir, f), g)
    print(f, len(sp), md5(os.path.join(out_dir, f)), flush=True)


def pipeline(out_dir, f):
    """Pipeline identity at the file's full geometry: the stand-in decoded by the read's path (decode → unfold →
    sequence) against the sequence built directly from its own spacings (positions 0.5 + cumulative sums, as placed)."""
    o = _obs_of(f)
    sp = np.load(os.path.join(out_dir, f + ".npy"))
    t0 = FR.FILES[o][f][0]
    g = decode(os.path.join(out_dir, f), *FR.FILES[o][f])
    s_back, x_back = FR.unfold(g, t0, dps=DPS - 5)
    del g
    if o == "A":
        seq_dir, seq_back = FR.seq_A(sp), FR.seq_A(s_back)
    else:
        x = (np.longdouble(0.5) + np.concatenate([[0.0], np.cumsum(sp.astype(np.longdouble))])).astype(float)
        seq_dir, seq_back = FR.seq_B(x), FR.seq_B(x_back)
    res = dict(file=f, observable=o, n=len(sp), max_abs_spacing_err=float(np.max(np.abs(s_back - sp))),
               sequence_identical=bool(len(seq_dir) == len(seq_back) and np.array_equal(seq_dir, seq_back)),
               n_sequence=len(seq_back))
    json.dump(res, open(os.path.join(out_dir, f"pipeline_{f}.json"), "w"), indent=1)
    print(res, flush=True)
    return res


def dry_seal(obs, path, md5s, calib_sha=None):
    w, _ = FR.weights(obs)
    seal = dict(seal="DRYRUN (not a seal)", observable=obs, env=env(),
                code_sha256={f: sha(os.path.join(HERE, f)) for f in CODE},
                derived_sha256={k: sha(os.path.join(HERE, p)) for k, p in DERIVED[obs].items()},
                prediction_sha256=sha(FR.PRED[obs]),
                calibration_sha256=CALIB_SHA256[obs] if calib_sha is None else calib_sha, weights=w, md5=md5s)
    json.dump(seal, open(path, "w"), indent=1)


def dryrun_prepare(obs, synth_dir):
    os.makedirs(DRY_OUT, exist_ok=True)
    dry_seal(obs, os.path.join(DRY_OUT, f"DRYRUN_SEAL_{obs}.json"),
             {f: md5(os.path.join(synth_dir, f)) for f in FR.FILES[obs]})


def dryrun_read(obs, label, synth_dir):
    read(obs, label, synth_dir, os.path.join(DRY_OUT, f"DRYRUN_SEAL_{obs}.json"), DRY_OUT)


def dryrun_record(obs, synth_dir):
    """The two dry-run reads must be bit-identical; the CUE stand-ins (μ = 0) must read FAIL (the calibration's power at
    μ = 0); shifted to μ = 1 (each file's μ̂ + g_f) the same results are reported descriptively (one draw)."""
    res = compare(obs, DRY_OUT)
    cal = json.load(open(FR.CALIB[obs]))
    pred = json.load(open(FR.PRED[obs]))
    g = FR.g_files(obs, pred)
    v1 = evaluate(obs, {f: dict(r, mu=r["mu"] + g[f]) for f, r in res["records"].items()}, cal)
    pl = {f: json.load(open(os.path.join(synth_dir, f"pipeline_{f}.json"))) for f in FR.FILES[obs]}
    expect = dict(bit_identical_runs=json.load(open(os.path.join(DRY_OUT, obs, "COMPARE.json")))["bit_identical"],
                  standin_reads_fail=res["result"]["verdict"] == "FAIL",
                  pipeline_identity=all(p["sequence_identical"] for p in pl.values()))
    rec = dict(observable=obs, env=res["env"], standin=res["result"],
               shifted_to_mu1_single_draw=dict(verdict=v1["verdict"], mu_pool=v1.get("mu_pool")), pipeline=pl,
               as_expected=expect, md5={f: md5(os.path.join(synth_dir, f)) for f in FR.FILES[obs]})
    json.dump(rec, open(os.path.join(DRY_OUT, f"FOLLOWUP_{obs}_DRYRUN.json"), "w"), indent=1, default=float)
    print("dry run:", rec["shifted_to_mu1_single_draw"], "as expected:", expect, flush=True)
    return 0 if all(expect.values()) else 1


# ---------------------------------------------------------------- refusal red paths
def refusals(obs):
    """Each refusal must fire on a constructed defect; nothing is decoded (every case stops before decode)."""
    files = list(FR.FILES[obs])
    tmp = tempfile.mkdtemp(dir=os.path.join(HERE, "results"))
    cases = {}
    try:
        for f in files:
            open(os.path.join(tmp, f), "wb").write(b"not a zero file")
        good = {f: md5(os.path.join(tmp, f)) for f in files}
        sp = os.path.join(tmp, "seal.json")
        csha = sha(FR.CALIB[obs])

        def attempt(name, mutate=None, md5s=good, data=tmp):
            dry_seal(obs, sp, dict(md5s), calib_sha=csha)
            if mutate:
                s = json.load(open(sp))
                mutate(s)
                json.dump(s, open(sp, "w"))
            saved = CALIB_SHA256[obs]
            CALIB_SHA256[obs] = csha
            try:
                read(obs, "x", data, sp, os.path.join(tmp, "out"))
                cases[name] = "NOT REFUSED"
            except SystemExit as e:
                cases[name] = str(e)
            except Exception as e:                                        # noqa: BLE001 (a crash is not a refusal)
                cases[name] = f"CRASH {type(e).__name__}: {e}"
            finally:
                CALIB_SHA256[obs] = saved

        dry_seal(obs, sp, dict(good), calib_sha=csha)                  # positive control
        saved = CALIB_SHA256[obs]
        CALIB_SHA256[obs] = csha
        try:
            check_seal(obs, sp)
            control = True
        except SystemExit:
            control = False
        finally:
            CALIB_SHA256[obs] = saved
        try:
            read(obs, "x", tmp, os.path.join(tmp, "absent.json"), os.path.join(tmp, "out"))
            cases["no_seal"] = "NOT REFUSED"
        except SystemExit as e:
            cases["no_seal"] = str(e)
        attempt("interpreter_mismatch", lambda s: s["env"].update(numpy="0.0"))
        attempt("code_mismatch", lambda s: s["code_sha256"].update({CODE[0]: "0" * 64}))
        attempt("prediction_mismatch", lambda s: s.update(prediction_sha256="0" * 64))
        attempt("calibration_mismatch", lambda s: s.update(calibration_sha256="0" * 64))
        attempt("weights_mismatch", lambda s: s["weights"].update({files[0]: 0.5}))
        if DERIVED[obs]:
            attempt("derived_mismatch", lambda s: s["derived_sha256"].update({next(iter(DERIVED[obs])): "0" * 64}))
        # the calibration not yet declared (pin None): every read refuses
        dry_seal(obs, sp, dict(good), calib_sha=csha)
        saved = CALIB_SHA256[obs]
        CALIB_SHA256[obs] = None
        try:
            read(obs, "x", tmp, sp, os.path.join(tmp, "out"))
            cases["calibration_undeclared"] = "NOT REFUSED"
        except SystemExit as e:
            cases["calibration_undeclared"] = str(e)
        finally:
            CALIB_SHA256[obs] = saved
        # a prediction one byte off the stamped one, with the seal rebuilt to agree: only the stamp check can refuse it
        bad = os.path.join(tmp, "pred_tampered.json")
        b = bytearray(open(FR.PRED[obs], "rb").read())
        b[-2] = ord("0") if b[-2] != ord("0") else ord("1")
        open(bad, "wb").write(bytes(b))
        saved_pred = FR.PRED[obs]
        try:
            FR.PRED[obs] = bad
            attempt("prediction_vs_stamp")
        finally:
            FR.PRED[obs] = saved_pred
        if "OpenTimestamps" not in cases["prediction_vs_stamp"]:
            cases["prediction_vs_stamp"] = "WRONG REFUSAL: " + cases["prediction_vs_stamp"]
        man = os.path.join(tmp, "manifest_tampered.txt")
        open(man, "w").write(open(PRESTAMP).read().replace("5b32efbb", "5b32efbc"))
        try:
            stamp_check(obs, manifest=man)
            cases["stamp_manifest_tampered"] = "NOT REFUSED"
        except SystemExit as e:
            cases["stamp_manifest_tampered"] = str(e)
        rc = os.path.join(tmp, "receipt_tampered.ots")
        b = bytearray(open(PRESTAMP_OTS, "rb").read())
        b[len(OTS_MAGIC) + 2] ^= 1
        open(rc, "wb").write(bytes(b))
        try:
            stamp_check(obs, receipt=rc)
            cases["stamp_receipt_tampered"] = "NOT REFUSED"
        except SystemExit as e:
            cases["stamp_receipt_tampered"] = str(e)
        attempt("md5_mismatch", md5s=dict(good, **{files[-1]: "0" * 32}))
        os.remove(os.path.join(tmp, files[1]))
        attempt("file_missing")
        import mpmath as mp
        lo = os.path.join(tmp, "lo.dat")
        RR.write_platt(lo, [mp.mpf(1000.5), mp.mpf(1001.25)])
        try:
            decode(lo, *FR.FILES[obs][files[0]])
            cases["heights_outside_range"] = "NOT REFUSED"
        except SystemExit as e:
            cases["heights_outside_range"] = str(e)
        vb = os.path.join(tmp, "void")
        for r, txt in (("run1", '{"result": 1}'), ("run2", '{"result": 2}')):
            os.makedirs(os.path.join(vb, obs, r))
            open(os.path.join(vb, obs, r, "FOLLOWUP_READ.json"), "w").write(txt)
        try:
            compare(obs, vb)
            cases["runs_differ"] = "NOT VOIDED"
        except SystemExit as e:
            cases["runs_differ"] = "REFUSED (" + str(e) + ")" if str(e).startswith("VOID") else str(e)
    finally:
        shutil.rmtree(tmp)
    ok = control and all(v.startswith("REFUSED") for v in cases.values())
    print(f"({obs}) {'positive control':24s} {'passes the pin checks' if control else 'REFUSED (wrongly)'}")
    for k, v in cases.items():
        print(f"({obs}) {k:24s} {v[:110]}")
    print(f"({obs}) REFUSALS", "PASS" if ok else "FAIL")
    return ok, dict(control=control, cases=cases)


# ---------------------------------------------------------------- joint-reading witnesses
def witness():
    """Every arm of the joint reading fires on constructed verdict pairs, and the family-wise rate is the product rule."""
    V = lambda v: dict(verdict=v)                                         # noqa: E731
    want = {("PASS", "PASS"): "both PASS", ("FAIL", "PASS"): "exactly one FAIL (A)",
            ("PASS", "FAIL"): "exactly one FAIL (B)", ("FAIL", "FAIL"): "both FAIL",
            ("MODEL MISFIT", "PASS"): "no joint reading", ("PASS", "UNRESOLVED"): "no joint reading",
            ("FIT FAILURE", "FAIL"): "no joint reading"}
    cases = {f"{a}/{b}": dict(got=joint(V(a), V(b)), ok=joint(V(a), V(b)).startswith(w)) for (a, b), w in want.items()}
    fw = abs(familywise(0.05, 0.05) - 0.0975) < 1e-12
    ok = all(c["ok"] for c in cases.values()) and fw
    for k, c in cases.items():
        print(f"{k:24s} {c['got'][:90]}  {'ok' if c['ok'] else 'WRONG'}")
    print("family-wise(0.05, 0.05) = 0.0975:", fw)
    print("WITNESS", "PASS" if ok else "FAIL")
    return ok, dict(cases=cases, familywise_check=fw)


# ---------------------------------------------------------------- seal builder
def tagged_sha(obs):
    rel = os.path.relpath(FR.PRED[obs], os.path.join(HERE, "..", ".."))
    blob = subprocess.run(["git", "show", f"{TAG[obs]}:{rel}"], cwd=HERE, capture_output=True, check=True).stdout
    return hashlib.sha256(blob).hexdigest()


def seal(obs, check_only=False):
    pins = dict(re.findall(r"\| (zeros_\d+\.dat) \| \[[^|]*\) \| [^|]* \| ([0-9a-f]{32}) \|", open(FRESH_PINS).read()))
    dry = json.load(open(os.path.join(DRY_OUT, f"FOLLOWUP_{obs}_DRYRUN.json")))
    pv = json.load(open(PRESTAMP_VERIFY))
    gates = json.load(open(os.path.join(HERE, "results", "followup_gates.json")))
    prestamp_ok = (all(pv["checks"].values()) and pv["manifest_sha256"] == PRESTAMP_SHA256
                   and pv["receipt_sha256"] == sha(PRESTAMP_OTS) and stamp_check(obs) == sha(FR.PRED[obs]))
    cals = {o: json.load(open(FR.CALIB[o])) for o in "AB"}
    alpha = {o: cals[o]["operating_characteristics"]["declared"]["false_fail"] for o in "AB"}
    checks = dict(text_exists=os.path.exists(TEXT[obs]), prestamp_bitcoin_verified=prestamp_ok,
                  dryrun_as_expected=all(dry["as_expected"].values()), dryrun_under_this_interpreter=dry["env"] == env(),
                  refusals=refusals(obs)[0], witness=witness()[0],
                  md5_match_pins=all(pins.get(f) == m for f, m in MD5[obs].items()),
                  prediction_is_tagged=sha(FR.PRED[obs]) == tagged_sha(obs),
                  calibration_pinned=CALIB_SHA256[obs] is not None and sha(FR.CALIB[obs]) == CALIB_SHA256[obs],
                  other_calibration_pinned=all(CALIB_SHA256[o] is not None and sha(FR.CALIB[o]) == CALIB_SHA256[o]
                                               for o in "AB"),
                  gates_taggable=bool(gates["TAGGABLE"][obs]), rule_selftest=bool(FR.rule_selftest()),
                  no_calibration_failures=not cals[obs]["fit_failures"] and cals[obs]["boot_failures"] == 0)
    if not all(checks.values()):
        raise SystemExit(f"REFUSED: {[k for k, v in checks.items() if not v]}")
    if check_only:
        print("checks (nothing written):", checks)
        return 0
    w, nf = FR.weights(obs)
    pred = json.load(open(FR.PRED[obs]))
    cal = cals[obs]
    out = dict(seal=f"FOLLOWUP_{obs}_SEAL", observable=obs, env=env(), text=os.path.basename(TEXT[obs]),
               text_sha256=sha(TEXT[obs]), code_sha256={f: sha(os.path.join(HERE, f)) for f in CODE},
               prediction=dict(tag=TAG[obs], file=os.path.relpath(FR.PRED[obs], HERE)),
               prediction_sha256=sha(FR.PRED[obs]), calibration_sha256=CALIB_SHA256[obs],
               derived_sha256={k: sha(os.path.join(HERE, p)) for k, p in DERIVED[obs].items()},
               md5=MD5[obs], files={f: dict(t0=t0, t1=t1) for f, (t0, t1) in FR.FILES[obs].items()}, weights=w, n_f=nf,
               rule=dict(dmu_sys=FR.dmu_sys(obs, pred), g=FR.g_files(obs, pred), block=cal["block"],
                         block_lens=list(FR.BLOCK_LENS[obs]), bias={f: c["bias"] for f, c in cal["files"].items()},
                         sd={f: c["sd"] for f, c in cal["files"].items()},
                         T={f: c["T"] for f, c in cal["files"].items()} if obs == "A" else None,
                         k_pool=FR.K_POOL, k_file=FR.K_FILE, files_needed=len(FR.FILES[obs]) - 1,
                         misfit_files=FR.MISFIT_FILES if obs == "A" else None, resolve_2se=FR.RESOLVE_2SE),
               operating_characteristics=cal["operating_characteristics"]["declared"],
               joint_reading=dict(alpha_A=alpha["A"], alpha_B=alpha["B"], familywise=familywise(alpha["A"], alpha["B"]),
                                  arms=witness()[1]["cases"]),
               prestamp=dict(manifest=os.path.relpath(PRESTAMP, HERE), manifest_sha256=PRESTAMP_SHA256,
                             receipt_sha256=sha(PRESTAMP_OTS), earliest_bitcoin_block=pv["earliest"],
                             bitcoin_blocks=[a["height"] for a in pv["attestations"]], method=pv["method"]),
               dryrun=dry["as_expected"], checks=checks)
    os.makedirs(os.path.dirname(SEAL[obs]), exist_ok=True)
    json.dump(out, open(SEAL[obs], "w"), indent=1, sort_keys=True)
    print("wrote", SEAL[obs])
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "read":
        read(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else FRESH)
    elif cmd == "compare":
        compare(sys.argv[2])
    elif cmd == "sample":
        sample(sys.argv[2])
    elif cmd == "synth":
        synth(sys.argv[2], sys.argv[3])
    elif cmd == "pipeline":
        pipeline(sys.argv[2], sys.argv[3])
    elif cmd == "dryrun_prepare":
        dryrun_prepare(sys.argv[2], sys.argv[3])
    elif cmd == "dryrun_read":
        dryrun_read(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "dryrun_record":
        sys.exit(dryrun_record(sys.argv[2], sys.argv[3]))
    elif cmd == "refusals":
        sys.exit(0 if refusals(sys.argv[2])[0] else 1)
    elif cmd == "witness":
        sys.exit(0 if witness()[0] else 1)
    elif cmd == "seal":
        sys.exit(seal(sys.argv[2], "--check" in sys.argv))
