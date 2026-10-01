"""Known answers for mf_explore.py on a FAKE cache/mf (built with stage3_extract_mf's own matrix_stats / null_draw, so the
keys and shapes are the real ones): d_model 256, 4 heads of 64, MLP 1024, 2 layers, 2 checkpoints (step0, step143000),
three models under allowed names (the names are only directory labels here):
  pythia-1.4b         iid Gaussian matrices (singular vectors Haar on both sides)
  pythia-410m-seed1   iid Gaussian matrices
  pythia-410m-seed2   as seed1, but K = U diag(s) V^T with V block-diagonal (32 Haar 8x8 blocks): EVERY right singular
                      vector of K is supported on 8 contiguous entries; U Haar; s = singular values of a Gaussian.
Checks (exit 1 on any failure):
  (i)   pure Gaussian models: |log(trained/null)| of the band-mean M_q and |trained/Haar - 1| within sampling noise
        (thresholds per q, see TOL), box-moment departures (trained - null, and trained alone) within noise of 0;
  (ii)  seed2: K side v, every bulk band: log(trained/null) at q = 4 > 3 and tail mass of n*psi^2 above 10 > 0.5;
        K side u and all other matrices of seed2 stay within (i)'s noise;
  (iii) the allow-list refuses pythia-70m and pythia-410m-seed6 (non-zero exit, 'REFUSED' on stderr, no output dir);
  (iv)  output files present (json per model + seed mean over seeds 1,2; csv tables; scaling.csv; SUMMARY.md; figures).
--redpath: flip (ii)'s threshold (require log(trained/null) at q=4 < 3 on the planted side); the check must FAIL
(exit 0 iff it does). Scratch: $MFX_SCRATCH or a mkdtemp under $TMPDIR."""
import os, sys, json, time, shutil, tempfile, subprocess, csv
from pathlib import Path
import numpy as np
import stage3_extract_mf as X

HERE = Path(__file__).resolve().parent
PY = sys.executable
TOL = {0.5: 0.25, 1.5: 0.25, 2.0: 0.25, 2.5: 0.25, 3.0: 0.4, 4.0: 0.8}     # |log ratio| noise bounds (q = 1 is identically 0)


def gaussian_mats(rng, D, FF):
    return {"Q": rng.standard_normal((D, D)), "K": rng.standard_normal((D, D)), "V": rng.standard_normal((D, D)),
            "O": rng.standard_normal((D, D)), "MLP_IN": rng.standard_normal((FF, D)), "MLP_OUT": rng.standard_normal((D, FF))}


def planted_K(rng, D, blk=8):
    """W = U diag(s) V^T, V block-diagonal (Haar blk x blk blocks) so every right singular vector sits on blk contiguous
    entries. Singular value k is assigned to block k mod (D/blk), so each block holds singular values spread over the
    whole spectrum and the column norms are block-HOMOGENEOUS: the norm-preserving null then stays delocalised and the
    departure is structure, not the norm profile."""
    U = np.linalg.qr(rng.standard_normal((D, D)))[0]
    s = np.linalg.svd(rng.standard_normal((D, D)), compute_uv=False)
    nb = D // blk
    blocks = [np.linalg.qr(rng.standard_normal((blk, blk)))[0] for _ in range(nb)]
    V = np.zeros((D, D))
    for k in range(D):
        j, c = k % nb, k // nb                       # singular value k -> block j, column c of that block
        V[j * blk:(j + 1) * blk, k] = blocks[j][:, c]
    assert np.allclose(V.T @ V, np.eye(D))
    return (U * s) @ V.T


def write_layer(path, mats, DH, model, rev, L):
    out = {"q_grid": X.Q_GRID, "box_ell": X.box_sizes(DH), "hist_edges": X.HIST_EDGES, "estimator_version": np.array("fake")}
    for M in X.MATS:
        W = mats[M]
        X.matrix_stats(W, M, DH, out)
        seed = X.null_seed(model, rev, L, M)
        G, scale = X.null_draw(W, seed)
        X.matrix_stats(G, M, DH, out, suffix="_null")
        out[f"null_seed_{M}"] = np.array(seed, dtype=np.uint64); out[f"null_scale_{M}"] = np.array(scale)
    np.savez(path, **out)


def build(root, D=256, H=4, DH=64, FF=1024):
    rng = np.random.default_rng(11)
    for model in ("pythia-1.4b", "pythia-410m-seed1", "pythia-410m-seed2"):
        for rev in ("step0", "step143000"):
            d = root / model / rev
            d.mkdir(parents=True, exist_ok=True)
            for L in range(2):
                mats = gaussian_mats(rng, D, FF)
                if model == "pythia-410m-seed2":
                    mats["K"] = planted_K(rng, D)
                write_layer(d / f"L{L:02d}.npz", mats, DH, model, rev, L)
            (d / "DONE").write_text("fake")


def load_csv(p):
    with open(p) as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    RED = "--redpath" in sys.argv
    fails = []
    scratch = Path(os.environ.get("MFX_SCRATCH") or tempfile.mkdtemp(prefix="mfx_verify_", dir=os.environ.get("TMPDIR")))
    root, out = scratch / "cache_mf", scratch / "out"
    shutil.rmtree(root, ignore_errors=True); shutil.rmtree(out, ignore_errors=True)
    t = time.time(); build(root); print(f"fake cache built in {time.time() - t:.1f}s at {root}")
    sizes = sorted(p.stat().st_size for p in root.rglob("L*.npz"))
    print(f"  layer file sizes {sizes[0] / 1e6:.2f}-{sizes[-1] / 1e6:.2f} MB (real: ~22 MB)")

    # run the explorer (subprocess, like the real use) ---------------------------------------------------------------
    cmd = [PY, str(HERE / "mf_explore.py"), "--root", str(root), "--models", "pythia-1.4b", "pythia-410m-seed1",
           "pythia-410m-seed2", "--out", str(out), "--revs", "step0", "step143000", "--workers", "2"]
    t = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(HERE))
    print(f"mf_explore exit {p.returncode} in {time.time() - t:.1f}s wall (incl. figures)")
    for line in p.stdout.splitlines():
        print("  | " + line)
    if p.returncode != 0:
        print(p.stderr); fails.append(f"mf_explore exit {p.returncode}")

    # (i) pure Gaussian: ratios within noise --------------------------------------------------------------------------
    def worst(rows, key, pred=lambda r: True):
        w = (0.0, None)
        for r in rows:
            if pred(r) and r[key] != "":
                v = abs(float(r[key]))
                if v > w[0]:
                    w = (v, r)
        return w

    def check_noise(model, exclude=lambda r: False):
        mom = load_csv(out / f"mom_{model}.csv"); box = load_csv(out / f"box_{model}.csv")
        for q, tol in TOL.items():
            sel = lambda r, q=q: float(r["q"]) == q and not exclude(r)
            for key, rows, name in (("log_trained_over_null", mom, "mom log(T/N)"), ("logmean_trained", mom, "mom mean log(M_q/Haar)"),
                                    ("diff", box, "box T-N"), ("logdep_trained", box, "box log(T/Haar)")):
                v, r = worst(rows, key, sel)
                tag = f"{r['M']}/{r['side']}/{r['band']}/{r['rev']}" + (f"/ell={r['ell']}" if 'ell' in r else "") if r else "-"
                flag = "" if v < tol else "  <-- FAIL"
                print(f"    {model:20s} q={q:<3g} {name:24s} max|.| {v:.3f} (tol {tol}) at {tag}{flag}")
                if v >= tol:
                    fails.append(f"(i) {model} q={q} {name} {v:.3f} >= {tol} at {tag}")
            v, r = worst(mom, "trained_over_haar", sel)        # ratio itself near 1
            dev = max(abs(float(r2["trained_over_haar"]) - 1) for r2 in mom if sel(r2))
            if dev >= tol:
                fails.append(f"(i) {model} q={q} trained/Haar - 1 = {dev:.3f} >= {tol}")

    print("(i) pure Gaussian models")
    for model in ("pythia-1.4b", "pythia-410m-seed1"):
        check_noise(model)

    # (ii) planted ----------------------------------------------------------------------------------------------------
    print("(ii) planted: pythia-410m-seed2, K side v")
    mom2 = load_csv(out / "mom_pythia-410m-seed2.csv"); hist2 = load_csv(out / "hist_pythia-410m-seed2.csv")
    planted = [r for r in mom2 if r["M"] == "K" and r["side"] == "v" and float(r["q"]) == 4.0 and r["band"] != "spike"]
    vals = [float(r["log_trained_over_null"]) for r in planted]
    thr = 3.0
    hit = all((v < thr) if RED else (v > thr) for v in vals)
    print(f"    log(trained/null) at q=4 over bulk bands: min {min(vals):.2f} max {max(vals):.2f} vs {thr} "
          f"({'RED: require <' if RED else 'require >'}): {'ok' if hit else 'FAIL'}   "
          f"[trained/Haar {min(float(r['trained_over_haar']) for r in planted):.3g}..{max(float(r['trained_over_haar']) for r in planted):.3g}, "
          f"Haar E[M_4] {planted[0]['haar_E_mom']}, n {planted[0]['n']}]")
    if not hit:
        fails.append(f"(ii) planted log(T/N) q=4 {'<' if RED else '>'} {thr} not met: {min(vals):.2f}..{max(vals):.2f}")
    tails = [float(r["tail10_trained"]) for r in hist2 if r["M"] == "K" and r["side"] == "v" and r["band"] != "spike"]
    tnull = [float(r["tail10_null"]) for r in hist2 if r["M"] == "K" and r["side"] == "v" and r["band"] != "spike"]
    pt = float(hist2[0]["tail10_pt"])
    print(f"    entry fraction with n*psi^2 above 10: trained {min(tails):.4f}..{max(tails):.4f} (8 of 256 entries carry the mass: "
          f"ceiling 8/256 = {8 / 256:.4f}), null {min(tnull):.2e}..{max(tnull):.2e}, PT {pt:.2e}; require trained > 3x null and > 5x PT")
    if not all(t > 3 * nl and t > 5 * pt for t, nl in zip(tails, tnull)):
        fails.append(f"(ii) planted tail10 {min(tails):.4f} not > 3x null ({max(tnull):.2e}) and 5x PT ({pt:.2e})")
    check_noise("pythia-410m-seed2", exclude=lambda r: r["M"] == "K" and r["side"] == "v")

    # (iii) allow-list -----------------------------------------------------------------------------------------------
    print("(iii) allow-list")
    for bad in ("pythia-70m", "pythia-410m-seed6"):
        o2 = scratch / f"out_{bad}"
        p2 = subprocess.run([PY, str(HERE / "mf_explore.py"), "--root", str(root), "--models", "pythia-1.4b", bad,
                             "--out", str(o2)], capture_output=True, text=True, cwd=str(HERE))
        refused = p2.returncode != 0 and "REFUSED" in p2.stderr and not o2.exists()
        print(f"    --models pythia-1.4b {bad}: exit {p2.returncode}, stderr tail: {p2.stderr.strip().splitlines()[-1][:110] if p2.stderr.strip() else ''}; refused {refused}")
        if not refused:
            fails.append(f"(iii) {bad} not refused")

    # (iv) outputs ----------------------------------------------------------------------------------------------------
    want = ["mf_explore_pythia-1.4b.json", "mf_explore_pythia-410m-seed1.json", "mf_explore_pythia-410m-seedmean.json",
            "mom_pythia-1.4b.csv", "box_pythia-1.4b.csv", "head_pythia-1.4b.csv", "hist_pythia-1.4b.csv", "normcv_pythia-1.4b.csv",
            "mom_pythia-410m-seedmean.csv", "scaling.csv", "SUMMARY.md", "fig_a_momratio_q2_pythia-1.4b.png",
            "fig_a_momratio_q4_pythia-410m-seedmean.png", "fig_b_box_q2_pythia-1.4b.png", "fig_c_tail_pythia-410m-seedmean.png"]
    missing = [w for w in want if not (out / w).exists()]
    sm = json.load(open(out / "mf_explore_pythia-410m-seedmean.json")) if (out / "mf_explore_pythia-410m-seedmean.json").exists() else {}
    nseeds = sm.get("revs", {}).get("step0", {}).get("n_seeds")
    hd = load_csv(out / "head_pythia-1.4b.csv")
    print(f"(iv) outputs: {len(list(out.iterdir()))} files; missing {missing or 'none'}; seed mean n_seeds {nseeds}; "
          f"head table H={hd[0]['H']} DH={hd[0]['DH']} headmax trained {hd[0]['headmax_trained']} null {hd[0]['headmax_null']} haar_mc {hd[0]['headmax_haar_mc']}")
    if missing or nseeds != 2:
        fails.append(f"(iv) missing {missing}, n_seeds {nseeds}")
    print(f"    SUMMARY.md head: " + " / ".join(l for l in (out / "SUMMARY.md").read_text().splitlines() if l.startswith("| 1 |"))[:300])
    print(("REDPATH failures: " if RED else "FAILURES: ") + str(fails or "none"))
    sys.exit((0 if fails else 1) if RED else (1 if fails else 0))
