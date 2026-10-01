"""Synthetic known answers for stage3_extract_mf (n = 512, H = 8, d_head = 64). Exit 1 on any failure.
  (a) Haar-random unit vectors (4096 independent sphere-uniform, and the singular vectors of a 512 x 512 Gaussian):
      mean M_q == n * B(q+1/2, (n-1)/2) / B(1/2, (n-1)/2)  [exact; the Gaussian form n^{1-q} 2^q Gamma(q+1/2)/sqrt(pi) is
      its large-n limit], |z| < 4 and rel. error < 5 %; box moments at ell: mean sum_b mu_b^q ==
      (n/ell) * B(ell/2+q, (n-ell)/2) / B(ell/2, (n-ell)/2) [exact; -> n^{1-q} ell^{q-1} as ell grows], same tolerance.
  (b) a planted localised top vector (mass on 8 contiguous entries, one box of size 8): M_2 > 10 * 3/n, and the box
      ratio box(ell=32)/box(ell=2) at q=2 is off the Haar expectation by > 2x (it is 4 vs 8.5); bulk vectors stay Haar.
  (c) null draw: ||G||_F == ||W||_F to 1e-12; mean squared row/column norms over 64 seeds == those of W (|z| < 5 per
      row/column, grand ratio within 1 %); same seed -> identical G; (model, rev, layer, M) seeds all distinct.
  (d) resumability through run(): a synthetic 2-layer checkpoint (pytorch_model.bin written by torch.save, read by the
      numpy reader, workers=2 spawn pool) extracts once; the second run skips (DONE) and a third run with DONE removed
      has 0 layers to do; file mtimes unchanged. Without torch: CkptDict source, workers=1.
  (e) numpy .bin reader == torch.save for fp16 / fp32 / bf16 / non-contiguous tensors (skipped without torch).
  (f) the fp16-grid assertion fires on an off-grid fp32 value; ipr == M_2 column; subsample == first 16 vectors.
--redpath: flip the planted-vector detection threshold in (b) (require M_2 < 10 * 3/n, i.e. 'bulk-like'); the check
must FAIL on the planted vector (exit 0 iff it does)."""
import os, sys, time, shutil, tempfile
from pathlib import Path
import numpy as np
from scipy.special import betaln, gammaln
import stage3_extract_mf as X
import remote_st as R

if __name__ == "__main__":   # multiprocessing spawn re-imports this file in each worker
    RED = "--redpath" in sys.argv
    fails = []
    rng = np.random.default_rng(5)
    n, H, DH, D, FF = 512, 8, 64, 512, 2048
    Q = X.Q_GRID
    ELL = X.box_sizes(DH)


    def E_mom(q, n):
        return n * np.exp(betaln(q + 0.5, (n - 1) / 2) - betaln(0.5, (n - 1) / 2))


    def E_box(q, n, ell):
        return (n / ell) * np.exp(betaln(ell / 2 + q, (n - ell) / 2) - betaln(ell / 2, (n - ell) / 2))


    def ztest(name, sample, expect, rows, rel_tol=0.05):
        """sample (N, ..., 7) per-vector values over Q_GRID; expect broadcastable. q = 1 is the normalisation (M_1 == 1
        identically, zero variance): checked for equality; the other q by |z| < 4 and relative error < rel_tol."""
        one = np.abs(sample[..., 1] - 1).max()
        sample, expect = sample[..., [0, 2, 3, 4, 5, 6]], expect[..., [0, 2, 3, 4, 5, 6]]
        m, se = sample.mean(0), sample.std(0, ddof=1) / np.sqrt(len(sample))
        z, rel = (m - expect) / se, np.abs(m / expect - 1)
        worst = np.unravel_index(np.argmax(np.abs(z)), z.shape)
        print(f"  {name}: max|M_1 - 1| {one:.1e}; max|z| {np.abs(z).max():.2f} at {rows(worst)}, max rel {rel.max():.4f} (tol {rel_tol})")
        if one > 1e-5 or np.abs(z).max() >= 4 or rel.max() >= rel_tol:
            fails.append(f"{name}: M_1 dev {one:.1e} |z| {np.abs(z).max():.2f} rel {rel.max():.4f}")


    # (a) Haar vectors ------------------------------------------------------------------------------------------------
    G = rng.standard_normal((n, 4096))
    Uind = G / np.sqrt((G * G).sum(0))
    st, bands = X.side_stats(Uind, dh=DH)
    Em = np.array([E_mom(q, n) for q in Q])
    print(f"(a) Gaussian-limit form at q=4: {n ** (1 - 4) * 2 ** 4 * np.exp(gammaln(4.5)) / np.sqrt(np.pi):.4e}, exact {Em[-1]:.4e}")
    ztest("Haar M_q (4096 independent)", st["mom"].astype(np.float64), Em, lambda w: f"q={Q[[0, 2, 3, 4, 5, 6][w[0]]]}")
    Eb = np.array([[E_box(q, n, ell) for q in Q] for ell in ELL])
    ztest("Haar box moments", st["box"].astype(np.float64), Eb, lambda w: f"ell={ELL[w[0]]} q={Q[[0, 2, 3, 4, 5, 6][w[1]]]}")
    for ell, row in zip(ELL, Eb):
        print(f"    ell={ell:3d}: exact/asymptotic(n^(1-q) ell^(q-1)) at q=2: {row[3] / (n ** -1 * ell):.4f}, q=4: {row[6] / (n ** -3 * ell ** 3):.4f}")
    Ug = np.linalg.svd(rng.standard_normal((n, n)), full_matrices=False)[0]
    st2, _ = X.side_stats(Ug, dh=DH)
    ztest("Haar M_q (singular vectors of a 512x512 Gaussian)", st2["mom"].astype(np.float64), Em, lambda w: f"q={Q[[0, 2, 3, 4, 5, 6][w[0]]]}", rel_tol=0.10)

    # (b) planted localised vector -----------------------------------------------------------------------------------
    psi = np.zeros(n); psi[64:72] = 1 / np.sqrt(8)
    phi = rng.standard_normal(n); phi /= np.linalg.norm(phi)
    W = 200.0 * np.outer(psi, phi) + rng.standard_normal((n, n))   # sigma_max(Z) ~ 2 sqrt(n) = 45
    out = {}
    X.matrix_stats(W, "Q", DH, out)
    m2, box = out["mom_u_Q"][0, 3], out["box_u_Q"][0]
    assert abs(abs(out["sub_u_Q"][0, 0].astype(np.float64)) @ psi) > 0.99, "planted vector is not the top left vector"
    thr = 10 * 3 / n
    hit = (m2 < thr) if RED else (m2 > thr)
    print(f"(b) planted M_2 = {m2:.4f} vs threshold {thr:.4f} ({'RED: require <' if RED else 'require >'}): {'ok' if hit else 'FAIL'}")
    if not hit:
        fails.append(f"planted M_2 {m2:.4f} {'<' if RED else '>'} {thr:.4f} not met")
    ratio_p, ratio_h = box[2, 3] / box[0, 3], Eb[2, 3] / Eb[0, 3]
    print(f"    box(32)/box(2) at q=2: planted {ratio_p:.3f} vs Haar {ratio_h:.3f}")
    if abs(np.log(ratio_p / ratio_h)) <= np.log(2):
        fails.append(f"planted box ratio {ratio_p:.3f} within 2x of Haar {ratio_h:.3f}")
    bulk = out["mom_u_Q"][32:, 3].astype(np.float64)
    print(f"    bulk (k>=32) mean M_2 {bulk.mean():.5f} vs Haar {Em[3]:.5f}")
    if abs(bulk.mean() / Em[3] - 1) > 0.05:
        fails.append("bulk vectors of the planted matrix not Haar-like")

    # (c) null draw -------------------------------------------------------------------------------------------------
    Wn = rng.standard_normal((n, 384)) * np.exp(0.5 * rng.standard_normal((n, 1))) * np.exp(0.5 * rng.standard_normal((1, 384)))
    rn2, cn2 = (Wn * Wn).sum(1), (Wn * Wn).sum(0)
    seeds = [X.null_seed("m", "r", 0, f"M{i}") for i in range(64)]
    R2, C2, fro = [], [], []
    for s in seeds:
        Gn, c = X.null_draw(Wn, s)
        R2.append((Gn * Gn).sum(1)); C2.append((Gn * Gn).sum(0)); fro.append(np.linalg.norm(Gn) / np.linalg.norm(Wn))
    R2, C2 = np.array(R2), np.array(C2)
    print(f"(c) ||G||_F/||W||_F max dev {np.abs(np.array(fro) - 1).max():.2e}; null_scale {c:.6f}")
    if np.abs(np.array(fro) - 1).max() > 1e-12:
        fails.append("Frobenius norm not exact")
    for name, S, ref in (("row", R2, rn2), ("col", C2, cn2)):
        z = (S.mean(0) - ref) / (S.std(0, ddof=1) / np.sqrt(len(S)))
        grand = S.mean(0).sum() / ref.sum()
        print(f"    {name} norms^2 over 64 draws: max|z| {np.abs(z).max():.2f}, grand ratio {grand:.4f}")
        if np.abs(z).max() >= 5 or abs(grand - 1) > 0.01:
            fails.append(f"null {name} norms: max|z| {np.abs(z).max():.2f} grand {grand:.4f}")
    G1, _ = X.null_draw(Wn, seeds[0]); G2, _ = X.null_draw(Wn, seeds[0])
    if not np.array_equal(G1, G2):
        fails.append("null draw not deterministic")
    allseeds = {X.null_seed(m, r, L, M) for m in ("pythia-1.4b", "pythia-410m-seed1") for r in ("step0", "step143000")
                for L in range(24) for M in X.MATS}
    print(f"    deterministic: {np.array_equal(G1, G2)}; distinct seeds {len(allseeds)}/{2 * 2 * 24 * 6}")
    if len(allseeds) != 2 * 2 * 24 * 6:
        fails.append("seed collision")

    # (d)+(e) resumability through run(), .bin reader -----------------------------------------------------------------
    tmp = Path(tempfile.mkdtemp(prefix="mf_verify_", dir=os.environ.get("TMPDIR")))
    try:
        import torch
    except ImportError:
        torch = None
    sd = {}
    for L in range(2):
        p = f"gpt_neox.layers.{L}."
        sd[p + "attention.query_key_value.weight"] = rng.standard_normal((3 * D, D)).astype(np.float16)
        sd[p + "attention.dense.weight"] = rng.standard_normal((D, D)).astype(np.float16)
        sd[p + "mlp.dense_h_to_4h.weight"] = rng.standard_normal((FF, D)).astype(np.float16)
        sd[p + "mlp.dense_4h_to_h.weight"] = rng.standard_normal((D, FF)).astype(np.float16)
    sd["gpt_neox.layers.0.attention.bias"] = np.ones((1, 1, 4, 4), dtype=np.bool_)
    if torch is not None:
        bin_path = tmp / "pytorch_model.bin"
        extra = {"x.f32": torch.randn(7, 5), "x.bf16": torch.randn(4, 6).bfloat16(), "x.nc": torch.randn(6, 8).half().t().contiguous().t()}
        bin_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({**{k: torch.from_numpy(v) for k, v in sd.items()}, **extra}, bin_path)
        idx = X.bin_index(bin_path)
        bad = [k for k, t in extra.items() if not np.array_equal(X.bin_tensor(bin_path, idx[k]).astype(np.float32), t.float().numpy())]
        bad += [k for k, v in sd.items() if not np.array_equal(X.bin_tensor(bin_path, idx[k]), v)]
        print(f"(e) numpy .bin reader vs torch.save: {len(idx)} tensors, mismatches {bad}")
        if bad:
            fails.append(f"bin reader mismatch {bad}")
        model = "pythia-70m-seed1"
        src_copy = tmp / "src.bin"
        shutil.copy(bin_path, src_copy)
        R.download_file = lambda repo, fn, rev, dest, **kw: (shutil.copy(src_copy, dest), Path(dest))[1]
        workers = 2
    else:
        print("(e) torch not available: .bin reader check SKIPPED; (d) runs on a CkptDict source, workers=1")
        model = "pythia-70m"
        X.CkptST = lambda m, r, idx=None: X.CkptDict(sd)
        X._open = lambda m, r, s: X.CkptDict(sd)
        workers = 1
    outroot = tmp / "mf"
    t = time.time()
    X.run(model, "stepTEST", workers=workers, out_root=outroot)
    print(f"(d) first run {time.time() - t:.1f}s (workers={workers})")
    d = outroot / model / "stepTEST"
    files = sorted(d.glob("L*.npz"))
    mt = {f: f.stat().st_mtime_ns for f in files}
    if len(files) != 2 or not (d / "DONE").exists():
        fails.append(f"first run produced {len(files)} layer files, DONE {(d / 'DONE').exists()}")
    X.run(model, "stepTEST", workers=workers, out_root=outroot)            # DONE -> skip
    (d / "DONE").unlink()
    X.run(model, "stepTEST", workers=workers, out_root=outroot)            # per-layer skip, DONE rewritten
    same = all(f.stat().st_mtime_ns == mt[f] for f in files)
    print(f"    second/third runs: layer files untouched {same}; DONE restored {(d / 'DONE').exists()}")
    if not same or not (d / "DONE").exists():
        fails.append("resumability: files rewritten or DONE missing")
    z = np.load(files[0])
    cmp = {k: z[k].shape for k in ("sig_Q", "mom_u_Q", "box_u_Q", "box_v_O", "hist_u_MLP_IN", "sub_u_MLP_IN", "rownorm_MLP_IN", "null_seed_Q")}
    print(f"    banked (d=512 synthetic): {cmp}; keys {len(z.files)}; box keys {[k for k in z.files if k.startswith('box')]}")
    if "box_v_Q" in z.files or "box_u_O" in z.files or "box_u_MLP_IN" in z.files:
        fails.append("box moments banked on a non-nested side")
    # (f) guards and identities
    try:
        X.CkptDict({"w": np.array([1.0 + 2 ** -14], dtype=np.float32)}).get_many(["w"]); fails.append("fp16-grid assertion did not fire")
        fired = False
    except AssertionError:
        fired = True
    ipr_ok = np.allclose(z["ipr_u_MLP_IN"], z["mom_u_MLP_IN"][:, 3], rtol=1e-5) and np.allclose(z["ipr_v_O_null"], z["mom_v_O_null"][:, 3], rtol=1e-5)
    print(f"(f) fp16-grid assertion fires: {fired}; ipr == M_2 column: {ipr_ok}; sub == first 16 of band: ", end="")
    sub_ok = np.allclose(st["sub"][1].astype(np.float64), Uind[:, 32:48].T, atol=1e-3)
    print(sub_ok)
    if not ipr_ok or not sub_ok:
        fails.append("ipr/sub identity")
    shutil.rmtree(tmp, ignore_errors=True)
    print(("REDPATH failures: " if RED else "FAILURES: ") + str(fails or "none"))
    sys.exit((0 if fails else 1) if RED else (1 if fails else 0))
