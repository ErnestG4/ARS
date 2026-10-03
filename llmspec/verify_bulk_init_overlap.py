"""Synthetic known answers for bulk_init_overlap.py / bulk_init_overlap_verdict.py (BULK_INIT_OVERLAP_PREREG.md S2 known
answers + S3 words). NO real weight or bank file is touched. Exit 1 on any failure.
  (i)   W_t = alpha W_0 + eps G (eps = 1 % of the init scale, n = 256, 3 seeds): rho_bulk >= 0.99, |E_init - 1| <= 0.02,
        |alpha_hat/alpha - 1| <= 1e-3, d ~ eps; rho_proj_all == rho_full on a square matrix (identity, 1e-10); the sign map
        rho_from_sign = sin(pi (p_sign - 1/2)) agrees with rho_full to 0.01 (jointly Gaussian pair: exact in expectation);
        rho_near and rho_bulk_core are banked (A1) with rho_near >= 0.99 here.
  (ii)  W_t = fresh Gaussian (20 seeds): |rho_bulk| <= 5/n_bulk and |rho_full| <= 5/n for every seed; the empirical sd of
        rho_bulk is within 2x of 1/n_bulk; |p_sign - 1/2| <= 5 x 0.5/n; the Gaussian null (_gauss) obeys the same bound on
        every bank of (i)-(iii).
  (iii) W_t = alpha W_0 + rank-32 spike (spike singular values 20x sigma_max(alpha W_0)): the spike occupies k < 32,
        rho_bulk >= 0.98 while rho_top <= 0.20; the bulk-fitted scale alpha_bulk == alpha to 1e-3, and E_init_bulk ==
        (alpha_hat/alpha)^2 to 1 % -- the PREREG's E_init carries the GLOBAL alpha_hat, which the spike shifts by ~5 %
        here (a property of the sealed definition, made visible; alpha_S is banked as a descriptive for that reason).
  (iv)  wrong-instance null (another layer's W_0): |rho_bulk_wrong| <= 5/n_bulk on every bank of (i)-(iii).
  (v)   weight-decay prediction: lr_at == armb/q1_models.lr (the sealed AnnealingLR) on the 70M parameters at every step
        0..143000; W_t = prod_{k<t}(1 - wd lr_k) W_0 reproduces alpha_hat == alpha_wd(t) to 1e-10 at t in {1, 1430, 4000,
        143000} for pythia-1.4b; the transcribed weight-decay is 0.1 and lands in the banked file (cfg_weight_decay).
  (vi)  verdict words on synthetic banks run through the REAL chain (layer_outputs -> npz -> collect -> JSON ->
        bulk_init_overlap_verdict.main): 6 allow-listed models x 4 layers x 6 matrices (n = 384; bulk = k in [32, 256)),
        each with a step1 revision W_1 = W_0 + lr(1) sign(G) (Adam's first step; passes the A1 continuity gate at exactly
        1x the expectation) and a step143000 revision: INIT bank (0.8 W_0 + 5 % noise) -> INIT-DOMINATED BULK on BOTH rows
        (pythia-1.4b, pythia-410m-seeds); LEARNED bank (fresh Gaussian) -> LEARNED BULK; MIXED bank (noise amplitude
        log-uniform over 4 decades) -> MIXED; DISCONT bank = INIT bank but seed2's step1 descends from a DIFFERENT instance
        (dist_raw ~ sqrt 2, 1e5 x the band) and seed3 has no step1: gate FAIL / UNEVALUATED, both INAPPLICABLE, the seeds
        row reads INIT-DOMINATED over the 3 applicable runs and lists them; the 1.4B row is untouched. A non-allow-listed
        model is REFUSED; a 4-layer bank without --partial reads INCOMPLETE. Kosson / alpha_wd lines present in the JSON.
  (vii) resumability through run(): a synthetic 2-layer pythia-70m-seed1 (step0 + stepTEST written by torch.save as
        pytorch_model.bin, download_file patched to copy them; workers=2 spawn pool): init bank (2 files) + 2 layer files +
        DONE on the first run; the second run skips (DONE); the third with DONE removed has 0 layers to do; no mtime
        changes; collect() yields 12 final rows with alpha_hat ~ 0.9 and rho_bulk > 0.9 for the planted stepTEST.
        Without torch: CkptDict source, workers=1.
--redpath: override the verdict's INIT-DOMINATED threshold (init_rho -> -1.0) so (vi)'s LEARNED bank reads INIT-DOMINATED;
the (vi) check must FAIL (exit 0 iff it does).
"""
import os, sys, time, json, shutil, tempfile
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "armb"))
import bulk_init_overlap as B
import bulk_init_overlap_verdict as V
import remote_st as R
import stage3_extract_mf as X

if __name__ == "__main__":   # multiprocessing spawn re-imports this file in each worker
    RED = "--redpath" in sys.argv
    fails = []
    T0 = time.time()
    rng = np.random.default_rng(7)
    n = 256

    def refs_for(W0, seed, W0w):
        return {"gauss": B.gauss_like(W0, seed), "wrong": W0w}

    def bound_checks(tag, res, nb):
        for key in ("rho_bulk_gauss", "rho_bulk_wrong"):
            if not abs(res[key]) <= 5 / nb:
                fails.append(f"{tag}: |{key}| {abs(res[key]):.4f} > 5/n_bulk {5 / nb:.4f}")

    # (i) alpha W0 + eps G -----------------------------------------------------------------------------------------
    alpha = 0.7
    for sd in range(3):
        W0 = rng.standard_normal((n, n)); W0w = rng.standard_normal((n, n))
        Wt = alpha * W0 + 0.01 * rng.standard_normal((n, n))
        res = B.measure(Wt, W0, refs_for(W0, 11 + sd, W0w))
        nb = res["n_bulk"]
        dsign = abs(res["rho_from_sign"] - res["rho_full"])
        ok = res["rho_bulk"] >= 0.99 and abs(res["einit_bulk"] - 1) <= 0.02 and abs(res["alpha_hat"] / alpha - 1) <= 1e-3 \
            and abs(res["rho_proj_all"] - res["rho_full"]) <= 1e-10 and dsign <= 0.01 and res["rho_near"] >= 0.99
        print(f"(i) seed {sd}: rho_bulk {res['rho_bulk']:.5f} E_init {res['einit_bulk']:.5f} alpha_hat {res['alpha_hat']:.5f} (alpha {alpha}) "
              f"d {res['d']:.4f} rho_near {res['rho_near']:.5f} rho_core {res['rho_bulk_core']:.5f} rho_deep {res['rho_deep']:.5f} rho_top {res['rho_top']:.5f} "
              f"|proj_all-full| {abs(res['rho_proj_all'] - res['rho_full']):.1e} p_sign {res['p_sign']:.4f} rho_from_sign {res['rho_from_sign']:.4f} "
              f"(rho_full {res['rho_full']:.4f}) dist_raw {res['dist_raw']:.4f} n_bulk {nb} bands {res['band_edges'].tolist()}: {'ok' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"(i) seed {sd}: rho_bulk {res['rho_bulk']:.4f} E_init {res['einit_bulk']:.4f} alpha_hat {res['alpha_hat']:.4f}")
        bound_checks(f"(i) seed {sd}", res, nb)

    # (ii) fresh Gaussian --------------------------------------------------------------------------------------------
    rb, rg = [], []
    for sd in range(20):
        W0 = rng.standard_normal((n, n)); W0w = rng.standard_normal((n, n))
        Wt = rng.standard_normal((n, n))
        res = B.measure(Wt, W0, refs_for(W0, 100 + sd, W0w))
        nb = res["n_bulk"]
        rb.append(res["rho_bulk"]); rg.append(res["rho_bulk_gauss"])
        if not (abs(res["rho_bulk"]) <= 5 / nb and abs(res["rho_full"]) <= 5 / n and abs(res["p_sign"] - 0.5) <= 2.5 / n):
            fails.append(f"(ii) seed {sd}: rho_bulk {res['rho_bulk']:.4f} rho_full {res['rho_full']:.4f} p_sign {res['p_sign']:.4f}")
        bound_checks(f"(ii) seed {sd}", res, nb)
    sd_b, sd_g = np.std(rb, ddof=1), np.std(rg, ddof=1)
    print(f"(ii) 20 fresh-Gaussian seeds: max|rho_bulk| {np.abs(rb).max():.4f} (bound 5/n_bulk {5 / nb:.4f}); sd(rho_bulk) {sd_b:.4f}, "
          f"sd(rho_bulk_gauss) {sd_g:.4f} vs 1/n_bulk {1 / nb:.4f}")
    if not (0.5 / nb <= sd_b <= 2.0 / nb):
        fails.append(f"(ii) sd(rho_bulk) {sd_b:.4f} not within 2x of 1/n_bulk {1 / nb:.4f}")

    # (iii) alpha W0 + rank-32 spike -----------------------------------------------------------------------------------
    for sd in range(3):
        W0 = rng.standard_normal((n, n)); W0w = rng.standard_normal((n, n))
        Uq = np.linalg.qr(rng.standard_normal((n, 32)))[0]; Vq = np.linalg.qr(rng.standard_normal((n, 32)))[0]
        a = 20 * np.linalg.norm(alpha * W0, 2)
        Wt = alpha * W0 + (Uq * (a * (1 + 0.1 * rng.random(32)))) @ Vq.T
        res = B.measure(Wt, W0, refs_for(W0, 200 + sd, W0w))
        s = res["sig"]
        e_pred = (res["alpha_hat"] / alpha) ** 2            # E_init carries the GLOBAL alpha_hat, which the spike shifts
        ok = res["rho_bulk"] >= 0.98 and res["rho_top"] <= 0.20 and abs(res["einit_bulk"] / e_pred - 1) <= 0.01 \
            and abs(res["alpha_bulk"] / alpha - 1) <= 1e-3 and s[31] > 5 * s[32]
        print(f"(iii) seed {sd}: rho_bulk {res['rho_bulk']:.5f} rho_top {res['rho_top']:.5f} alpha_hat {res['alpha_hat']:.4f} (spike-shifted; alpha {alpha}) "
              f"alpha_bulk {res['alpha_bulk']:.5f} E_init_bulk {res['einit_bulk']:.4f} == (alpha_hat/alpha)^2 {e_pred:.4f} "
              f"E_init_top {res['einit_top']:.1e} s[31]/s[32] {s[31] / s[32]:.1f} rho_full {res['rho_full']:.4f}: {'ok' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"(iii) seed {sd}: rho_bulk {res['rho_bulk']:.4f} rho_top {res['rho_top']:.4f}")
        bound_checks(f"(iii) seed {sd}", res, res["n_bulk"])
    print(f"(iv) wrong-instance and Gaussian nulls: |rho_bulk| <= 5/n_bulk on all banks of (i)-(iii): "
          f"{'ok' if not [f for f in fails if 'wrong' in f or 'gauss' in f] else 'FAIL'}")

    # (v) weight-decay prediction --------------------------------------------------------------------------------------
    import q1_models as Q1
    steps = np.arange(0, 143001)
    mine = B.lr_at(steps, Q1.LR0, Q1.MINLR, Q1.W0, Q1.E)
    theirs = np.array([Q1.lr(int(k), Q1.W0) for k in steps])
    dlr = np.abs(mine - theirs).max()
    cfg, lr14, loga = B.schedule("pythia-1.4b")
    print(f"(v) lr_at vs q1_models.lr (70M params, every step 0..143000): max|diff| {dlr:.1e}; pythia-1.4b config: wd {cfg['weight_decay']} "
          f"lr {cfg['lr']} min_lr {cfg['min_lr']} warmup {cfg['warmup_steps']} iters {cfg['train_iters']}; lr(0)={lr14[0]:.2e} lr(1430)={lr14[1430]:.2e} "
          f"lr(142999)={lr14[-1]:.2e}; alpha_wd(143000) = {np.exp(loga[-1]):.5f}  (sum lr = {lr14.sum():.3f})")
    if dlr > 1e-15:
        fails.append(f"(v) lr_at differs from the sealed q1_models.lr by {dlr:.1e}")
    if cfg["weight_decay"] != 0.1 or B.config_for("pythia-410m-seed3")["weight_decay"] != 0.1:
        fails.append("(v) transcribed weight decay is not 0.1")
    W0 = rng.standard_normal((n, n))
    for t in (1, 1430, 4000, 143000):
        awd = B.alpha_wd("pythia-1.4b", t)
        prod = float(np.prod(1 - cfg["weight_decay"] * lr14[:t]))     # direct product, the PREREG formula
        res = B.measure(awd * W0, W0, {})
        rel = abs(res["alpha_hat"] / awd - 1)
        print(f"    t={t:6d}: alpha_wd {awd:.8f} (direct product {prod:.8f}) alpha_hat {res['alpha_hat']:.8f} rel {rel:.1e} rho_bulk {res['rho_bulk']:.6f} d {res['d']:.1e}")
        if rel > 1e-10 or abs(prod / awd - 1) > 1e-10 or res["d"] > 1e-10:
            fails.append(f"(v) t={t}: alpha_hat {res['alpha_hat']:.8f} != alpha_wd {awd:.8f}")

    # (vi) verdict words through the real chain -------------------------------------------------------------------------
    tmp = Path(tempfile.mkdtemp(prefix="bio_verify_", dir=os.environ.get("TMPDIR")))
    nv, LAYERS, REV = 384, 4, "step143000"
    expect = {"INIT": "INIT-DOMINATED BULK", "LEARNED": "LEARNED BULK", "MIXED": "MIXED", "DISCONT": "INIT-DOMINATED BULK"}
    cfg410 = B.config_for("pythia-410m-seed1")
    t6 = time.time()
    n_meas = 0
    for bank in expect:
        out_root, res_dir = tmp / bank / "cache", tmp / bank / "results"
        for model in B.ALLOW:
            cfgm = B.config_for(model)
            lr1 = B.schedule_at(model, 1)["lr_1"]
            w0 = {L: {M: rng.standard_normal((nv, nv)) for M in B.MATS} for L in range(LAYERS)}
            revs = {REV: {}, "step1": {}}
            for L in range(LAYERS):
                for M in B.MATS:
                    base = w0[L][M]
                    if bank == "DISCONT" and model == "pythia-410m-seed2":
                        base = rng.standard_normal((nv, nv))            # step >= 1 descends from a DIFFERENT instance (issue #203)
                    revs["step1"][(L, M)] = base + lr1 * np.sign(rng.standard_normal((nv, nv)))
                    if bank == "LEARNED":
                        revs[REV][(L, M)] = rng.standard_normal((nv, nv))
                    elif bank == "MIXED":
                        revs[REV][(L, M)] = 0.8 * base + 10 ** rng.uniform(-2, 2) * rng.standard_normal((nv, nv))
                    else:
                        revs[REV][(L, M)] = 0.8 * base + 0.05 * rng.standard_normal((nv, nv))
            if bank == "DISCONT" and model == "pythia-410m-seed3":
                del revs["step1"]                                          # no step1 in the bank -> UNEVALUATED
            for rev, mats_by in revs.items():
                sched = B.schedule_at(model, B.step_of(rev))
                for L in range(LAYERS):
                    Lw = (L + 1) % LAYERS
                    out, _ = B.layer_outputs({M: mats_by[(L, M)] for M in B.MATS}, w0[L], w0[Lw], model, rev, L, Lw, cfgm, sched)
                    n_meas += len(B.MATS)
                    d = out_root / model / rev
                    d.mkdir(parents=True, exist_ok=True)
                    np.savez(d / f"L{L:02d}.npz", **out)
            J = B.collect(model, out_root, res_dir)
            if J["config"]["weight_decay"] != 0.1 or J["revs"][REV]["alpha_wd"] is None or J["revs"][REV]["kosson_rms_t"] is None:
                fails.append(f"(vi) {bank} {model}: JSON config/schedule lines missing or wrong")
        thr = '{"init_rho": -1.0}' if (RED and bank == "LEARNED") else None
        argv = ["--results", str(res_dir), "--partial", "--out", str(tmp / bank / "verdict.json")] + (["--thresholds", thr] if thr else [])
        v = V.main(argv)
        rows = [r for m in B.ALLOW for r in B.final_rows(json.loads((res_dir / f"{m}.json").read_text()), REV)]
        rho = np.array([r["rho_bulk"] for r in rows])
        words = v["words"]
        ok = words["pythia-1.4b"] == expect[bank] and words["pythia-410m-seeds"] == expect[bank]
        print(f"(vi) {bank} bank ({len(rows)} matrices): rho_bulk median {np.median(rho):.4f} p10 {np.percentile(rho, 10):.4f} p90 {np.percentile(rho, 90):.4f}; "
              f"rows 1.4B={words['pythia-1.4b']} seeds={words['pythia-410m-seeds']} pooled={words['pooled']} (expected {expect[bank]})"
              f"{' [RED: init_rho threshold -> -1.0]' if thr else ''}: {'ok' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"(vi) {bank} bank rows read {words}, expected {expect[bank]}")
        g = v["continuity_gate"]
        if bank == "DISCONT":
            inap = v["rows"]["pythia-410m-seeds"]["runs_inapplicable"]
            used = v["rows"]["pythia-410m-seeds"]["runs_used"]
            r2 = g["pythia-410m-seed2"]["ratio_over_expect"]["min"]
            ok_g = inap == {"pythia-410m-seed2": "FAIL", "pythia-410m-seed3": "UNEVALUATED"} and len(used) == 3 \
                and v["rows"]["pythia-410m-seeds"]["stats"]["n_matrices"] == 3 * LAYERS * 6 and g["pythia-1.4b"]["status"] == "PASS"
            print(f"    DISCONT gate: inapplicable {inap}; seeds row used {used} n={v['rows']['pythia-410m-seeds']['stats']['n_matrices']}; "
                  f"seed2 min ratio/expect {r2:.3g} (a different instance), 1.4B {g['pythia-1.4b']['status']}: {'ok' if ok_g else 'FAIL'}")
            if not ok_g:
                fails.append(f"(vi) DISCONT gate: {inap} used {used}")
        else:
            rat = [g[m]["ratio_over_expect"] for m in B.ALLOW]
            ok_g = all(g[m]["status"] == "PASS" for m in B.ALLOW) and all(abs(r["max"] - 1) < 1e-6 and abs(r["min"] - 1) < 1e-6 for r in rat)
            if not ok_g:
                fails.append(f"(vi) {bank}: continuity gate not PASS at ratio 1: {[(m, g[m]['status']) for m in B.ALLOW]}")
            if bank == "INIT":
                print(f"    continuity gate on every run: {[g[m]['status'] for m in B.ALLOW]}, ratio/expect min {min(r['min'] for r in rat):.6f} "
                      f"max {max(r['max'] for r in rat):.6f} (Adam first step = exactly 1x; lr(1) = {g['pythia-1.4b']['lr_1']:.3e} / {g['pythia-410m-seed1']['lr_1']:.3e})")
        if bank == "MIXED":
            tb = v["rows"]["pooled"]["tables"]
            print(f"    MIXED tables: per-type Q n={tb['per_type']['Q']['rho_bulk']['n']}, near-octave row n={tb['near_octave_32_64']['rho_near']['n']}, "
                  f"deep-octave row n={tb['deep_octave']['rho_deep']['n']}, red-flag frac(alpha_hat > alpha_wd) {tb['alpha']['red_flag_frac_alpha_hat_gt_alpha_wd']:.2f} "
                  f"(synthetic: alpha 0.8 vs alpha_wd 1.4B {B.alpha_wd('pythia-1.4b', 143000):.3f} / 410M {B.alpha_wd('pythia-410m-seed1', 143000):.3f}); "
                  f"kosson einit_pred median {tb['kosson_prior']['einit_pred']['median']:.3g}; trajectory revs {list(v['trajectory']['pooled'])}")
    print(f"    (vi) chain time {time.time() - t6:.1f}s for {n_meas} measurements at n={nv}")
    try:
        V.main(["--results", str(tmp / "INIT" / "results"), "--models", "pythia-410m-seed7", "--partial", "--out", str(tmp / "x.json")])
        fails.append("(vi) verdict did not refuse pythia-410m-seed7")
        refused = False
    except SystemExit as e:
        refused = "REFUSED" in str(e)
        if not refused:
            fails.append(f"(vi) unexpected exit {e}")
    v_inc = V.main(["--results", str(tmp / "INIT" / "results"), "--models", "pythia-1.4b", "--out", str(tmp / "y.json")])
    print(f"    non-allow-listed model refused: {refused}; 4-layer bank without --partial reads {v_inc['words']['pythia-1.4b']} (expected INCOMPLETE)")
    if v_inc["words"]["pythia-1.4b"] != "INCOMPLETE":
        fails.append("(vi) short bank without --partial did not read INCOMPLETE")

    # (vii) resumability through run() ---------------------------------------------------------------------------------
    try:
        import torch
    except ImportError:
        torch = None
    model, D, FF, H = "pythia-70m-seed1", 512, 2048, 8
    B.CONFIG[model] = dict(cfg410, source="SYNTHETIC TEST (verify_bulk_init_overlap (vii)); not the 70M yml")
    sd0, sdT = {}, {}
    for L in range(2):
        p = f"gpt_neox.layers.{L}."
        for name, shape in ((p + "attention.query_key_value.weight", (3 * D, D)), (p + "attention.dense.weight", (D, D)),
                            (p + "mlp.dense_h_to_4h.weight", (FF, D)), (p + "mlp.dense_4h_to_h.weight", (D, FF))):
            w0 = rng.standard_normal(shape).astype(np.float16)
            sd0[name] = w0
            sdT[name] = (0.9 * w0.astype(np.float64) + 0.02 * rng.standard_normal(shape)).astype(np.float16)
    sd0["gpt_neox.layers.0.attention.bias"] = sdT["gpt_neox.layers.0.attention.bias"] = np.ones((1, 1, 4, 4), dtype=np.bool_)
    src = {}
    if torch is not None:
        for rev, sd in (("step0", sd0), ("stepTEST", sdT)):
            src[rev] = tmp / f"{rev}.bin"
            torch.save({k: torch.from_numpy(v) for k, v in sd.items()}, src[rev])
        R.download_file = lambda repo, fn, rev, dest, **kw: (shutil.copy(src[rev], dest), Path(dest))[1]
        workers = 2
    else:
        print("(vii) torch not available: CkptDict source, workers=1")
        X._open = lambda m, r, s: X.CkptDict(sd0 if r == "step0" else sdT)
        workers = 1
    outroot = tmp / "bio"
    t = time.time()
    B.run(model, "stepTEST", workers=workers, out_root=outroot)
    print(f"(vii) first run {time.time() - t:.1f}s (workers={workers}, torch .bin={torch is not None})")
    d = outroot / model / "stepTEST"
    files = sorted(d.glob("L*.npz")) + sorted((outroot / model / "init").glob("L*.npz"))
    mt = {f: f.stat().st_mtime_ns for f in files}
    if len(files) != 4 or not (d / "DONE").exists():
        fails.append(f"(vii) first run produced {len(files)} files (want 2 layer + 2 init), DONE {(d / 'DONE').exists()}")
    B.run(model, "stepTEST", workers=workers, out_root=outroot)            # DONE -> skip
    (d / "DONE").unlink()
    B.run(model, "stepTEST", workers=workers, out_root=outroot)            # per-layer skip, DONE rewritten
    same = all(f.stat().st_mtime_ns == mt[f] for f in files)
    bins_left = list((HERE / "cache" / "bin_tmp").glob("*pythia-70m-seed1*"))
    print(f"    second/third runs: files untouched {same}; DONE restored {(d / 'DONE').exists()}; test .bin left in cache/bin_tmp: {len(bins_left)}")
    if not same or not (d / "DONE").exists() or bins_left:
        fails.append("(vii) resumability: files rewritten, DONE missing, or .bin not cleaned")
    J = B.collect(model, outroot, tmp / "bio_results")
    rows = B.final_rows(J, "stepTEST")
    z = np.load(files[0])
    ah = np.array([r["alpha_hat"] for r in rows]); rb = np.array([r["rho_bulk"] for r in rows])
    print(f"    collect: {len(rows)} rows; alpha_hat {ah.min():.4f}..{ah.max():.4f} (planted 0.9); rho_bulk min {rb.min():.4f}; "
          f"banked cfg_weight_decay {float(z['cfg_weight_decay'])}, wrong_layer {int(z['wrong_layer'])}, keys {len(z.files)}, "
          f"MLP_IN r={int(z['r_MLP_IN'])} bands {z['band_edges_MLP_IN'].tolist()}; kosson_rms_peak {float(z['kosson_rms_peak']):.4f}")
    if len(rows) != 12 or not (np.all(np.abs(ah - 0.9) < 0.01) and rb.min() > 0.9) or float(z["cfg_weight_decay"]) != 0.1:
        fails.append(f"(vii) collect: rows {len(rows)} alpha_hat range {ah.min():.4f}..{ah.max():.4f} rho_bulk min {rb.min():.4f}")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"total {time.time() - T0:.1f}s")
    print(("REDPATH failures: " if RED else "FAILURES: ") + str(fails or "none"))
    sys.exit((0 if fails else 1) if RED else (1 if fails else 0))
