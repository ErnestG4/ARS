"""Corrected (B): the sealed read, dry run, refusal checks and seal builder (rounds 57–58; mirrors followup_sealread.py,
whose decode it uses). Estimator, calibration and rule are b2_read.py's; this file adds only the read's safeguards.

  python b2_sealread.py read LABEL [DATA_DIR]   REFUSED unless seals/CORRECTED_B_SEAL.json exists and pins this code and
                                every module the read imports, the interpreter, the prediction, L* (b2_rule.json), the
                                slope run (b2_cuen.json), the calibration and the weights, and the prediction matches the
                                OpenTimestamps-stamped manifest (checked without git or the seal); every md5 is checked
                                against the pins BEFORE any file is decoded; each file's heights must lie in its range.
                                Writes results/b2_read/LABEL/ and prints NO estimate.
  python b2_sealread.py compare                 run1 and run2 must be bit-identical, else VOID; then the report
  python b2_sealread.py sample OUT_DIR FILE     (spot, CPU) CUE_1000 spacings for one F6 stand-in (.npy)
  python b2_sealread.py synth OUT_DIR FILE      the stand-in placed at FILE's geometry (Platt format)
  python b2_sealread.py pipeline OUT_DIR FILE   the stand-in decoded by the read's path vs its own positions
  python b2_sealread.py dryrun_prepare SYNTH_DIR
  python b2_sealread.py dryrun_read LABEL SYNTH_DIR
  python b2_sealread.py dryrun_record SYNTH_DIR
  python b2_sealread.py refusals                every refusal fires on a constructed defect
  python b2_sealread.py seal [--check]          build seals/CORRECTED_B_SEAL.json (on Will's go)

The test stands alone (round 58): its verdict is reported as the corrected (B)'s, with its calibrated false-FAIL rate;
no joint reading with (A) or with the sealed (B).
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
import b2_est as E  # noqa: E402
import b2_pred as BP  # noqa: E402
import b2_read as BR  # noqa: E402
import followup_read as FR  # noqa: E402
import followup_sealread as FS  # noqa: E402
import route_a_read as RR  # noqa: E402

SEAL = os.path.join(HERE, "seals", "CORRECTED_B_SEAL.json")
TEXT = os.path.join(HERE, "CORRECTED_B_SEAL.md")
FRESH = os.path.join(HERE, "..", "ph2r2", "data", "platt_fresh")
FRESH_PINS = os.path.join(HERE, "..", "ph2r2", "FRESH_SET_F6.md")
CODE = ["b2_sealread.py", "b2_read.py", "b2_est.py", "b2_pred.py", "followup_sealread.py", "followup_read.py",
        "followup_fit.py", "followup_nnn.py", "followup_pred.py", "route_a_read.py", "route_a_zeta.py", "../ph2/ph2lib.py"]
MD5 = {"zeros_46646000.dat": "aa9f1f18b0e724dc54f3d184cc596bd2",
       "zeros_256646000.dat": "020344a4229d8fc85f73fa1180aef729",
       "zeros_2365046000.dat": "93c286212f9405741d6454370e0e108d",
       "zeros_10630646000.dat": "ec13d8753e5e6e0a1161539df1d14a0a"}
TAG = "corrected-b-prediction"
# pinned after the declaration; None = not declared yet → every read refuses
CALIB_SHA256 = "3cebd02dd989c50d42eadda4ce45339c0928b3d7c1a99d641686d2bf98dafd65"
DERIVED = {"L_rule": "results/b2_rule.json", "cuen": "results/b2_cuen.json"}
SEED = 20261019
SET = 6
DPS = FS.DPS
READ_OUT = os.path.join(HERE, "results", "b2_read")
DRY_OUT = os.path.join(HERE, "results", "b2_dryrun")
# the prediction manifest stamped with OpenTimestamps (2026-10-18 22:02 PDT); the verify record is written once the receipt
# is Bitcoin-attested and checked on two explorers (seal() fails closed until then)
PRESTAMP = os.path.join(HERE, "timestamps", "CORRECTED_B_PRESTAMP_2026-10-18.txt")
PRESTAMP_SHA256 = "1b110981c0853fa78f60289537a5f3d1243b343f9feabfba5ffbccdd4ea0eb52"
PRESTAMP_VERIFY = os.path.join(HERE, "timestamps", "CORRECTED_B_PRESTAMP_2026-10-18_VERIFY.json")
sha, md5, env, OTS_MAGIC = FS.sha, FS.md5, FS.env, FS.OTS_MAGIC


def stamp_check(pred_path=None, manifest=None, receipt=None):
    """The prediction JSON's sha256 must equal the one in the OpenTimestamps-stamped manifest, whose sha256 must be the
    digest the receipt commits to and the pinned PRESTAMP_SHA256. No git, no seal."""
    pred_path = BR.PRED if pred_path is None else pred_path
    manifest = PRESTAMP if manifest is None else manifest
    if manifest is None or PRESTAMP_SHA256 is None:
        raise SystemExit("REFUSED: the prediction is not OpenTimestamps-stamped yet (no pinned manifest)")
    receipt = manifest + ".ots" if receipt is None else receipt
    head = open(receipt, "rb").read(len(OTS_MAGIC) + 2 + 32)
    if not (head.startswith(OTS_MAGIC) and head[len(OTS_MAGIC):len(OTS_MAGIC) + 2] == b"\x01\x08"
            and head[len(OTS_MAGIC) + 2:].hex() == PRESTAMP_SHA256):
        raise SystemExit("REFUSED: the OpenTimestamps receipt does not commit to the pinned prediction manifest")
    if sha(manifest) != PRESTAMP_SHA256:
        raise SystemExit("REFUSED: the prediction manifest differs from the OpenTimestamps-stamped one")
    m = re.search(r"corrected \(B\) prediction\s+\S+\s*\n\s*sha256 ([0-9a-f]{64})", open(manifest).read())
    if not m or sha(pred_path) != m.group(1):
        raise SystemExit("REFUSED: the prediction JSON's sha256 differs from the OpenTimestamps-stamped manifest's")
    return m.group(1)


def check_seal(seal_path):
    if not os.path.exists(seal_path):
        raise SystemExit("REFUSED: no CORRECTED_B_SEAL.json — F6 zeros are not decoded before the seal")
    stamp_check()
    seal = json.load(open(seal_path))
    if seal.get("env") != env():
        raise SystemExit(f"REFUSED: interpreter {env()} differs from the sealed {seal.get('env')}")
    for f in CODE:
        if sha(os.path.join(HERE, f)) != seal["code_sha256"][f]:
            raise SystemExit(f"REFUSED: {f} differs from the sealed code")
    if sha(BR.PRED) != seal["prediction_sha256"]:
        raise SystemExit("REFUSED: the prediction file differs from the sealed one")
    if CALIB_SHA256 is None or CALIB_SHA256 != seal["calibration_sha256"] or sha(BR.CALIB) != seal["calibration_sha256"]:
        raise SystemExit("REFUSED: the calibration differs from the sealed one (or is not declared)")
    w, _ = BR.weights()
    if any(abs(w[f] - seal["weights"][f]) > 1e-15 for f in BR.FILES):
        raise SystemExit("REFUSED: pooling weights differ from the sealed ones")
    for k, h in seal["derived_sha256"].items():
        if sha(os.path.join(HERE, DERIVED[k])) != h:
            raise SystemExit(f"REFUSED: derived file {DERIVED[k]} differs from the sealed one")
    if BP.L_star() != seal["L_star"]:
        raise SystemExit("REFUSED: L* differs from the sealed one")
    return seal


def positions(f, path):
    t0, t1 = BR.FILES[f]
    g = FS.decode(path, t0, t1)
    s, x = FR.unfold(g, t0, dps=DPS - 5)
    meta = dict(first=float(g[0]), last=float(g[-1]), n_zeros=len(g), mean_spacing=float(s.mean()),
                sha256_positions=hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest())
    return x, meta


def _one_file(job):
    f, p, seed, i = job
    x, meta = positions(f, p)
    pred = json.load(open(BR.PRED))
    res = E.zeros_stats(x, BP.L_star(), np.random.default_rng([seed, SET, i]), n_boot=BR.B_BOOT)
    r = BR.fit(pred["files"][f], res)
    r["k3_u"] = res["k3_u"]
    print(f"{f}: decoded {meta['n_zeros']} zeros, estimated", flush=True)
    return f, dict(r, **meta)


def evaluate(per_file, cal):
    pred = json.load(open(BR.PRED))
    return BR.rule(per_file, cal, BR.dmu_sys(pred), BR.g_files())


def read(label, data_dir=FRESH, seal_path=SEAL, out_base=READ_OUT, seed=SEED):
    """One read into out_base/label. Prints no estimate: interpretation waits for compare()."""
    seal = check_seal(seal_path)
    paths = {}
    for f in BR.FILES:                                        # every md5 before any decode
        p = os.path.join(data_dir, f)
        if not os.path.exists(p) or md5(p) != seal["md5"][f]:
            raise SystemExit(f"REFUSED: {p} missing or md5 differs from the pin")
        paths[f] = p
    from multiprocessing import Pool
    with Pool(len(paths)) as pool:
        got = pool.map(_one_file, [(f, p, seed, i) for i, (f, p) in enumerate(paths.items())])
    recs = dict(got)
    cal = json.load(open(BR.CALIB))
    v = evaluate(recs, cal)
    res = dict(seal=seal.get("seal"), observable="corrected (B)", L_star=BP.L_star(), env=env(), records=recs, result=v)
    out_dir = os.path.join(out_base, label)
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, "B2_READ.json"), "w"), indent=1, default=float)
    print(f"read {label}: written to {out_dir} (no estimate printed; run compare after the second run)", flush=True)
    return res


def compare(out_base=READ_OUT):
    a, b = (os.path.join(out_base, r, "B2_READ.json") for r in ("run1", "run2"))
    ha, hb = sha(a), sha(b)
    ok = ha == hb
    json.dump(dict(run1_sha256=ha, run2_sha256=hb, bit_identical=ok), open(os.path.join(out_base, "COMPARE.json"), "w"),
              indent=1)
    if not ok:
        raise SystemExit(f"VOID: run1 and run2 differ ({ha[:16]} vs {hb[:16]}); the read is void, nothing is interpreted")
    res = json.load(open(a))
    open(os.path.join(out_base, "B2_READ.md"), "w").write(FS.report_md("corrected B", res["result"]))
    print(f"run1 = run2 bit for bit (sha256 {ha[:16]}…)\n" + FS.report_md("corrected B", res["result"]))
    return res


# ---------------------------------------------------------------- stand-ins: pipeline identity and dry run
def sample(out_dir, f):
    """CUE_1000 spacings for one F6 stand-in (CPU sampler, the calibration's algorithm; seeds [20261019, 58, 7, 6, i],
    disjoint from every other use): the pre-data count less 100, so the last placed level stays below t1."""
    import cbe
    os.makedirs(out_dir, exist_ok=True)
    i = list(BR.FILES).index(f)
    _, nf = BR.weights()
    n = int(nf[f]) - 100
    rng = np.random.default_rng([20261019, 58, 7, SET, i])
    need = -(-n // 1000)
    sp = np.concatenate([cbe.spacings(cbe.sample(rng, min(500, need - k), 1000, 2.0)[0]).ravel()
                         for k in range(0, need, 500)])[:n]
    np.save(os.path.join(out_dir, f + ".npy"), sp)
    print(f, n, float(sp.min()), flush=True)


def synth(out_dir, f):
    sp = np.load(os.path.join(out_dir, f + ".npy"))
    g = RR.place(BR.FILES[f][0], sp)
    RR.write_platt(os.path.join(out_dir, f), g)
    print(f, len(sp), md5(os.path.join(out_dir, f)), flush=True)


def pipeline(out_dir, f):
    """Pipeline identity at the file's full geometry: the stand-in decoded by the read's path (decode → unfold →
    zeros_stats) against the same estimator on its own positions (0.5 + exact cumulative sums, as placed)."""
    sp = np.load(os.path.join(out_dir, f + ".npy"))
    x_back, _ = positions(f, os.path.join(out_dir, f))
    x = (np.longdouble(0.5) + np.concatenate([[0.0], np.cumsum(sp.astype(np.longdouble))])).astype(float)
    L = BP.L_star()
    a = E.zeros_stats(x, L, np.random.default_rng(1), n_boot=20)
    b = E.zeros_stats(x_back, L, np.random.default_rng(1), n_boot=20)
    res = dict(file=f, n=len(sp), max_abs_position_err=float(np.max(np.abs(x_back - x))),
               k3_u_identical=a["k3_u"] == b["k3_u"], se_identical=a["se_boot"] == b["se_boot"],
               k3bar=b["k3bar"], n_windows=b["n_windows"])
    json.dump(res, open(os.path.join(out_dir, f"pipeline_{f}.json"), "w"), indent=1)
    print(res, flush=True)
    return res


def dry_seal(path, md5s, calib_sha=None):
    w, _ = BR.weights()
    seal = dict(seal="DRYRUN (not a seal)", observable="corrected (B)", env=env(), L_star=BP.L_star(),
                code_sha256={f: sha(os.path.join(HERE, f)) for f in CODE},
                derived_sha256={k: sha(os.path.join(HERE, p)) for k, p in DERIVED.items()},
                prediction_sha256=sha(BR.PRED), calibration_sha256=CALIB_SHA256 if calib_sha is None else calib_sha,
                weights=w, md5=md5s)
    json.dump(seal, open(path, "w"), indent=1)


def dryrun_prepare(synth_dir):
    os.makedirs(DRY_OUT, exist_ok=True)
    dry_seal(os.path.join(DRY_OUT, "DRYRUN_SEAL.json"), {f: md5(os.path.join(synth_dir, f)) for f in BR.FILES})


def dryrun_read(label, synth_dir):
    read(label, synth_dir, os.path.join(DRY_OUT, "DRYRUN_SEAL.json"), DRY_OUT)


def dryrun_record(synth_dir):
    """The two dry-run reads must be bit-identical; the CUE stand-ins (μ = 0) must read FAIL (the calibration's power at
    μ = 0); shifted to μ = 1 (each file's μ̂ + g) the same results are reported descriptively (one draw)."""
    res = compare(DRY_OUT)
    cal = json.load(open(BR.CALIB))
    g = BR.g_files()
    v1 = evaluate({f: dict(r, mu=r["mu"] + g[f]) for f, r in res["records"].items()}, cal)
    pl = {f: json.load(open(os.path.join(synth_dir, f"pipeline_{f}.json"))) for f in BR.FILES}
    expect = dict(bit_identical_runs=json.load(open(os.path.join(DRY_OUT, "COMPARE.json")))["bit_identical"],
                  standin_reads_fail=res["result"]["verdict"] == "FAIL",
                  pipeline_identity=all(p["k3_u_identical"] and p["se_identical"] for p in pl.values()))
    rec = dict(env=res["env"], standin=res["result"], shifted_to_mu1_single_draw=dict(verdict=v1["verdict"],
               mu_pool=v1.get("mu_pool")), pipeline=pl, as_expected=expect,
               md5={f: md5(os.path.join(synth_dir, f)) for f in BR.FILES})
    json.dump(rec, open(os.path.join(DRY_OUT, "CORRECTED_B_DRYRUN.json"), "w"), indent=1, default=float)
    print("dry run:", rec["shifted_to_mu1_single_draw"], "as expected:", expect, flush=True)
    return 0 if all(expect.values()) else 1


# ---------------------------------------------------------------- refusal red paths
def refusals():
    """Each refusal must fire on a constructed defect; nothing is decoded (every case stops before decode)."""
    global CALIB_SHA256
    files = list(BR.FILES)
    tmp = tempfile.mkdtemp(dir=os.path.join(HERE, "results"))
    cases = {}
    try:
        for f in files:
            open(os.path.join(tmp, f), "wb").write(b"not a zero file")
        good = {f: md5(os.path.join(tmp, f)) for f in files}
        sp = os.path.join(tmp, "seal.json")
        csha = sha(BR.CALIB)

        def attempt(name, mutate=None, md5s=good, data=tmp, pin=csha):
            global CALIB_SHA256
            dry_seal(sp, dict(md5s), calib_sha=csha)
            if mutate:
                s = json.load(open(sp))
                mutate(s)
                json.dump(s, open(sp, "w"))
            saved = CALIB_SHA256
            CALIB_SHA256 = pin
            try:
                read("x", data, sp, os.path.join(tmp, "out"))
                cases[name] = "NOT REFUSED"
            except SystemExit as e:
                cases[name] = str(e)
            except Exception as e:                                        # noqa: BLE001 (a crash is not a refusal)
                cases[name] = f"CRASH {type(e).__name__}: {e}"
            finally:
                CALIB_SHA256 = saved

        dry_seal(sp, dict(good), calib_sha=csha)                          # positive control
        saved = CALIB_SHA256
        CALIB_SHA256 = csha
        try:
            check_seal(sp)
            control = True
        except SystemExit:
            control = False
        finally:
            CALIB_SHA256 = saved
        try:
            read("x", tmp, os.path.join(tmp, "absent.json"), os.path.join(tmp, "out"))
            cases["no_seal"] = "NOT REFUSED"
        except SystemExit as e:
            cases["no_seal"] = str(e)
        attempt("interpreter_mismatch", lambda s: s["env"].update(numpy="0.0"))
        attempt("code_mismatch", lambda s: s["code_sha256"].update({CODE[0]: "0" * 64}))
        attempt("prediction_mismatch", lambda s: s.update(prediction_sha256="0" * 64))
        attempt("calibration_mismatch", lambda s: s.update(calibration_sha256="0" * 64))
        attempt("weights_mismatch", lambda s: s["weights"].update({files[0]: 0.5}))
        attempt("derived_mismatch", lambda s: s["derived_sha256"].update({"L_rule": "0" * 64}))
        attempt("L_star_mismatch", lambda s: s.update(L_star=3.0))
        attempt("calibration_undeclared", pin=None)
        bad = os.path.join(tmp, "pred_tampered.json")
        b = bytearray(open(BR.PRED, "rb").read())
        b[-2] = ord("0") if b[-2] != ord("0") else ord("1")
        open(bad, "wb").write(bytes(b))
        saved_pred = BR.PRED
        try:
            BR.PRED = bad
            attempt("prediction_vs_stamp")
        finally:
            BR.PRED = saved_pred
        if "OpenTimestamps" not in cases["prediction_vs_stamp"]:
            cases["prediction_vs_stamp"] = "WRONG REFUSAL: " + cases["prediction_vs_stamp"]
        man = os.path.join(tmp, "manifest_tampered.txt")
        txt = open(PRESTAMP).read()
        h = sha(BR.PRED)
        open(man, "w").write(txt.replace(h, h[:-1] + ("0" if h[-1] != "0" else "1")))
        try:
            stamp_check(manifest=man, receipt=PRESTAMP + ".ots")
            cases["stamp_manifest_tampered"] = "NOT REFUSED"
        except SystemExit as e:
            cases["stamp_manifest_tampered"] = str(e)
        rc = os.path.join(tmp, "receipt_tampered.ots")
        b = bytearray(open(PRESTAMP + ".ots", "rb").read())
        b[len(OTS_MAGIC) + 2] ^= 1
        open(rc, "wb").write(bytes(b))
        try:
            stamp_check(receipt=rc)
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
            FS.decode(lo, *BR.FILES[files[0]])
            cases["heights_outside_range"] = "NOT REFUSED"
        except SystemExit as e:
            cases["heights_outside_range"] = str(e)
        vb = os.path.join(tmp, "void")
        for r, txt in (("run1", '{"result": 1}'), ("run2", '{"result": 2}')):
            os.makedirs(os.path.join(vb, r))
            open(os.path.join(vb, r, "B2_READ.json"), "w").write(txt)
        try:
            compare(vb)
            cases["runs_differ"] = "NOT VOIDED"
        except SystemExit as e:
            cases["runs_differ"] = "REFUSED (" + str(e) + ")" if str(e).startswith("VOID") else str(e)
    finally:
        shutil.rmtree(tmp)
    ok = control and all(v.startswith("REFUSED") for v in cases.values())
    print(f"{'positive control':24s} {'passes the pin checks' if control else 'REFUSED (wrongly)'}")
    for k, v in cases.items():
        print(f"{k:24s} {v[:110]}")
    print("REFUSALS", "PASS" if ok else "FAIL")
    return ok, dict(control=control, cases=cases)


# ---------------------------------------------------------------- seal builder
def tagged_sha():
    rel = os.path.relpath(BR.PRED, os.path.join(HERE, "..", ".."))
    blob = subprocess.run(["git", "show", f"{TAG}:{rel}"], cwd=HERE, capture_output=True, check=True).stdout
    return hashlib.sha256(blob).hexdigest()


def seal(check_only=False):
    pins = dict(re.findall(r"\| (zeros_\d+\.dat) \| \[[^|]*\) \| [^|]* \| ([0-9a-f]{32}) \|", open(FRESH_PINS).read()))
    dry = json.load(open(os.path.join(DRY_OUT, "CORRECTED_B_DRYRUN.json")))
    pv = json.load(open(PRESTAMP_VERIFY))
    gates = json.load(open(os.path.join(HERE, "results", "b2_gates.json")))
    prestamp_ok = (all(pv["checks"].values()) and pv["manifest_sha256"] == PRESTAMP_SHA256
                   and pv["receipt_sha256"] == sha(PRESTAMP + ".ots") and stamp_check() == sha(BR.PRED))
    cal = json.load(open(BR.CALIB))
    checks = dict(text_exists=os.path.exists(TEXT), prestamp_bitcoin_verified=prestamp_ok,
                  dryrun_as_expected=all(dry["as_expected"].values()), dryrun_under_this_interpreter=dry["env"] == env(),
                  refusals=refusals()[0], md5_match_pins=pins == MD5,
                  prediction_is_tagged=sha(BR.PRED) == tagged_sha(),
                  calibration_pinned=CALIB_SHA256 is not None and sha(BR.CALIB) == CALIB_SHA256,
                  gates_pass=bool(gates["all_pass"]), read_selftest=bool(BR.selftest()[0]),
                  no_calibration_failures=not cal["fit_failures"], calibration_at_Lstar=cal["L"] == BP.L_star())
    if not all(checks.values()):
        raise SystemExit(f"REFUSED: {[k for k, v in checks.items() if not v]}")
    if check_only:
        print("checks (nothing written):", checks)
        return 0
    w, nf = BR.weights()
    pred = json.load(open(BR.PRED))
    out = dict(seal="CORRECTED_B_SEAL", observable="corrected (B): offset-averaged k3 of the count", env=env(),
               L_star=BP.L_star(), NU=E.NU, text=os.path.basename(TEXT), text_sha256=sha(TEXT),
               code_sha256={f: sha(os.path.join(HERE, f)) for f in CODE},
               prediction=dict(tag=TAG, file=os.path.relpath(BR.PRED, HERE)), prediction_sha256=sha(BR.PRED),
               calibration_sha256=CALIB_SHA256, derived_sha256={k: sha(os.path.join(HERE, p)) for k, p in DERIVED.items()},
               md5=MD5, files={f: dict(t0=t0, t1=t1) for f, (t0, t1) in BR.FILES.items()}, weights=w, n_f=nf,
               rule=dict(dmu_sys=BR.dmu_sys(pred), g=BR.g_files(), block=cal["block"], segs=list(E.SEGS),
                         bias={f: c["bias"] for f, c in cal["files"].items()},
                         sd={f: c["sd"] for f, c in cal["files"].items()}, k_pool=FR.K_POOL, k_file=FR.K_FILE,
                         files_needed=len(BR.FILES) - 1, resolve_2se=FR.RESOLVE_2SE),
               operating_characteristics=cal["operating_characteristics"],
               prestamp=dict(manifest=os.path.relpath(PRESTAMP, HERE), manifest_sha256=PRESTAMP_SHA256,
                             receipt_sha256=sha(PRESTAMP + ".ots"), earliest_bitcoin_block=pv["earliest"],
                             bitcoin_blocks=[a["height"] for a in pv["attestations"]], method=pv["method"]),
               dryrun=dry["as_expected"], checks=checks)
    os.makedirs(os.path.dirname(SEAL), exist_ok=True)
    json.dump(out, open(SEAL, "w"), indent=1, sort_keys=True)
    print("wrote", SEAL)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "read":
        read(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else FRESH)
    elif cmd == "compare":
        compare()
    elif cmd == "sample":
        sample(sys.argv[2], sys.argv[3])
    elif cmd == "synth":
        synth(sys.argv[2], sys.argv[3])
    elif cmd == "pipeline":
        pipeline(sys.argv[2], sys.argv[3])
    elif cmd == "dryrun_prepare":
        dryrun_prepare(sys.argv[2])
    elif cmd == "dryrun_read":
        dryrun_read(sys.argv[2], sys.argv[3])
    elif cmd == "dryrun_record":
        sys.exit(dryrun_record(sys.argv[2]))
    elif cmd == "refusals":
        sys.exit(0 if refusals()[0] else 1)
    elif cmd == "seal":
        sys.exit(seal("--check" in sys.argv))
