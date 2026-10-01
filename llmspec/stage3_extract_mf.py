"""Stage 3 multifractality extractor (arm B re-extraction; briefs/README.md "Bulk-vector arm"): CPU-ONLY, numpy/scipy fp64.

Banks, for one Pythia checkpoint, the bulk singular-VECTOR objects the GPU extractor (stage3_extract.py) does not keep:
|psi|^2 moments, head-nested box moments, pooled |psi|^2 histograms, per-band vector subsamples, and a norm-preserving
Gaussian null -- for EVERY singular vector of the six per-layer matrices, both sides. No statistic is chosen here.

Runs on the 128 GB CPU box ("spot"): tensors stream HF -> RAM by HTTP range (remote_st), SVD is scipy gesdd in fp64,
nothing touches a GPU. Output cache/mf/<model>/<rev>/L<layer>.npz (durable_save; resumable per layer: existing files are
skipped) + DONE per revision. Honours llmspec/STOP and a 10 GB free-disk reserve (see check_stop: remote_st's guard keys on
remote_st.HOST_DISK, a WSL host mount that does not exist on spot, so this module rebinds remote_st.check_stop to a guard
that checks HOST_DISK when present AND the output filesystem).

Matrix set and orientation = stage3_extract.layer(): Q, K, V = rows (head, d_head) x D from the fused query_key_value
(H, 3, DH, D) tensor; O = attention.dense.weight as stored (D x H*DH, columns head-nested); MLP_IN = dense_h_to_4h
(4D x D); MLP_OUT = dense_4h_to_h (D x 4D). Pythia stepN checkpoints store F32 values on the fp16 grid: asserted per
tensor (same assertion as the GPU extractor), then upcast to fp64. PolyPythias (fmt="bin") ship fp16 pytorch_model.bin:
downloaded ONCE per revision to cache/bin_tmp (remote_st.download_file: size + LFS sha256 verified), read with a
pure-numpy zip/pickle reader (no torch needed on spot; bit-exactness vs torch.save: verify_mf_extract.py), deleted after.

Per layer, per matrix M in {Q, K, V, O, MLP_IN, MLP_OUT} with W (m x n), U (m x r), V (n x r), r = min(m, n),
index k = 0 (largest sigma) .. r-1, side s in {u, v} (psi = column k of U or V, length n_s = m or n):
  sig_<M>              (r,)        f64   singular values, descending (scipy gesdd, fp64)
  rownorm_<M>          (m,)        f64   ||W_{i,:}||_2;  colnorm_<M> (n,) f64  ||W_{:,j}||_2;  rms_<M> () f64 sqrt(mean W^2)
  ipr_<s>_<M>          (r,)        f64   sum psi^4  (== stage3_extract's ipr_u_/ipr_v_; cross-check on an overlapping ckpt)
  mom_<s>_<M>          (r, 7)      f32   M_q = sum_i |psi_i|^{2q}, q in Q_GRID = (0.5, 1, 1.5, 2, 2.5, 3, 4), box size 1
  box_<s>_<M>          (r, 4, 7)   f32   head-nested side ONLY (u for Q/K/V, v for O): coarse-grain |psi_i|^2 into
                                         contiguous boxes of size ell in BOX_ELL = (2, 8, 32, d_head), mu_b = sum_box psi_i^2,
                                         bank sum_b mu_b^q. (MLP sides and residual sides are not nested: absent.)
  hist_<s>_<M>         (nb, 60)    i64   pooled histogram of n_s * psi_i^2 per index band, log bins HIST_EDGES = logspace(-4, 3, 61)
  histof_<s>_<M>       (nb, 2)     i64   [below 1e-4, above 1e3] counts per band (np.histogram drops them; banked so the
                                         pooled count per band is recoverable)
  sub_<s>_<M>          (nb, 16, n_s) f16 the first 16 vectors of each band (deterministic subsample)
  bands: [0, 32) spike, then octaves [32, 64), [64, 128), ... clipped at r:  band_edges (nb+1,) i64 (per file; r-dependent)
Null (one draw per matrix), same keys with suffix _null (sig_<M>_null, rownorm_<M>_null, ..., box_u_Q_null, ...):
  G = c * D_r Z D_c / ||W||_F with Z iid N(0,1), D_r = diag(rownorm), D_c = diag(colnorm). With c = 1 this gives
  E||G_{i,:}||^2 = rownorm_i^2, E||G_{:,j}||^2 = colnorm_j^2 and E||G||_F^2 = ||W||_F^2 exactly (rank-one product scaling);
  the global factor c = ||W||_F / ||D_r Z D_c / ||W||_F||_F (banked as null_scale_<M>, = 1 + O((mn)^-1/2)) then makes
  ||G||_F = ||W||_F EXACTLY. Seed = first 8 bytes of sha256("<model>|<rev>|L<layer>|<M>") (banked: null_seed_<M>, u64),
  generator numpy default_rng (PCG64) standard_normal -- reproducible.
Per file: q_grid (7,), box_ell (4,), hist_edges (61,), band_edges, estimator_version.
Usage: stage3_extract_mf.py <model> <rev> [<rev> ...] [--workers N] [--threads T] [--layers 0,1,...] [--out DIR]
  --workers N  layers in a multiprocessing pool (spawn; each worker streams its own tensors; main does the DONE marker)
  --threads T  BLAS threads PER WORKER (OMP/OPENBLAS/MKL_NUM_THREADS, set before numpy import; default: leave the env)
  --layers     subset (testing);  --out DIR  output root instead of cache/mf (testing; keeps held-out models out of the bank)
Caller applies nice/ionice (spot rules).
"""
import os, sys


def _threads_from_argv():
    if "--threads" in sys.argv:
        t = sys.argv[sys.argv.index("--threads") + 1]
        for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
            os.environ[k] = t


_threads_from_argv()
import time, hashlib, shutil, zipfile, pickle
from collections import OrderedDict
from pathlib import Path
import numpy as np
from scipy.linalg import svd as _svd
import remote_st as R
import mcfg

ROOT = Path(__file__).resolve().parent
OUT_ROOT = ROOT / "cache" / "mf"
EST = "stage3-extract-mf-v1 (cpu fp64 scipy gesdd; moments/box/hist/sub both sides; D_r Z D_c null, Frobenius-exact)"
Q_GRID = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0])
HIST_EDGES = np.logspace(-4, 3, 61)
N_SUB = 16
SPIKE = 32
MATS = ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")
NESTED_SIDE = {"Q": "u", "K": "u", "V": "u", "O": "v"}     # the (head, d_head) index: rows of Q/K/V, columns of O


# ---------------------------------------------------------------- STOP / disk guard (works where HOST_DISK is absent)
def check_stop(out_root=None):
    if R.STOP.exists():
        raise R.Stopped("llmspec/STOP present")
    probe = [R.HOST_DISK]
    p = Path(out_root or OUT_ROOT)
    while not p.exists():
        p = p.parent
    probe.append(str(p))
    for d in probe:
        if os.path.isdir(d):
            free = shutil.disk_usage(d).free / 1e9
            if free < R.HOST_RESERVE_GB:
                raise R.Stopped(f"disk {d} free {free:.1f} GB < reserve {R.HOST_RESERVE_GB} GB")


R.check_stop = check_stop      # remote_st.fetch/fetch_many/download_file look this name up at call time


# ---------------------------------------------------------------- statistics on one side (columns of U or V)
def band_edges(r):
    e = [0, min(SPIKE, r)]
    while e[-1] < r:
        e.append(min(2 * e[-1], r))
    return np.array(e, dtype=np.int64)


def box_sizes(dh):
    return np.array([2, 8, 32, dh], dtype=np.int64)


def vec_moments(P, q=Q_GRID):
    """P (n, r) = psi_i^2 per column -> (r, len(q)) of sum_i P^q."""
    return np.stack([P.sum(0) if qq == 1.0 else (P ** qq).sum(0) for qq in q], axis=1)


def box_moments(P, ells, q=Q_GRID):
    """P (n, r) -> (r, len(ells), len(q)): sum over contiguous boxes of size ell of (sum_box P)^q. ell must divide n."""
    n, r = P.shape
    out = np.empty((r, len(ells), len(q)))
    for a, ell in enumerate(ells):
        assert n % ell == 0, f"box size {ell} does not divide n={n}"
        mu = P.reshape(n // ell, ell, r).sum(1)
        out[:, a, :] = vec_moments(mu, q)
    return out


def hist_bands(P, bands, edges=HIST_EDGES):
    """Pooled histogram of n * psi_i^2 per index band -> (nb, len(edges)-1) i64, plus (nb, 2) under/overflow counts."""
    n = P.shape[0]
    H = np.zeros((len(bands) - 1, len(edges) - 1), dtype=np.int64)
    OF = np.zeros((len(bands) - 1, 2), dtype=np.int64)
    for b in range(len(bands) - 1):
        v = (n * P[:, bands[b]:bands[b + 1]]).ravel()
        H[b] = np.histogram(v, bins=edges)[0]
        OF[b] = [(v < edges[0]).sum(), (v > edges[-1]).sum()]
    return H, OF


def subsample(U, bands, k=N_SUB):
    """(nb, k, n) f16: the first k vectors (columns) of each band; zero-padded if a band is shorter than k."""
    out = np.zeros((len(bands) - 1, k, U.shape[0]), dtype=np.float16)
    for b in range(len(bands) - 1):
        lo, hi = bands[b], min(bands[b] + k, bands[b + 1])
        out[b, :hi - lo] = U[:, lo:hi].T.astype(np.float16)
    return out


def side_stats(U, dh=None):
    """All per-side objects for U (n, r), columns = unit vectors. dh != None -> head-nested side: box moments too."""
    P = U * U
    bands = band_edges(U.shape[1])
    H, OF = hist_bands(P, bands)
    out = {"ipr": (P * P).sum(0), "mom": vec_moments(P).astype(np.float32), "hist": H, "histof": OF,
           "sub": subsample(U, bands)}
    if dh is not None:
        out["box"] = box_moments(P, box_sizes(dh)).astype(np.float32)
    return out, bands


def null_seed(model, rev, L, M):
    return int.from_bytes(hashlib.sha256(f"{model}|{rev}|L{L}|{M}".encode()).digest()[:8], "little")


def null_draw(W, seed):
    """G = c * diag(rownorm) Z diag(colnorm) / ||W||_F, Z iid N(0,1) from default_rng(seed); c makes ||G||_F = ||W||_F
    exactly (c = 1 + O((mn)^-1/2)); row/column squared norms are preserved in expectation (see module docstring)."""
    rn = np.sqrt((W * W).sum(1))
    cn = np.sqrt((W * W).sum(0))
    F = np.sqrt((rn * rn).sum())
    Z = np.random.default_rng(seed).standard_normal(W.shape)
    G = (rn[:, None] / F) * Z * cn[None, :]
    c = F / np.sqrt((G * G).sum())
    return G * c, float(c)


def matrix_stats(W, M, dh, out, suffix=""):
    """SVD of W (fp64) and every banked object for one matrix, written into `out` as <key>_<s>_<M><suffix>."""
    U, s, Vh = _svd(W, full_matrices=False, lapack_driver="gesdd", check_finite=False)
    out[f"sig_{M}{suffix}"] = s
    out[f"rownorm_{M}{suffix}"] = np.sqrt((W * W).sum(1))
    out[f"colnorm_{M}{suffix}"] = np.sqrt((W * W).sum(0))
    out[f"rms_{M}{suffix}"] = np.array(np.sqrt((W * W).mean()))
    bands = None
    for side, X in (("u", U), ("v", Vh.T)):
        st, bands = side_stats(X, dh if NESTED_SIDE.get(M) == side else None)
        for k, v in st.items():
            out[f"{k}_{side}_{M}{suffix}"] = v
    out["band_edges"] = bands


# ---------------------------------------------------------------- checkpoint sources (CPU, fp64 out, fp16-grid asserted)
def _fp16_exact(a, k):
    a16 = a.astype(np.float16)
    assert np.array_equal(a16.astype(np.float32), a.astype(np.float32)), f"{k}: not on the fp16 grid"
    return a16.astype(np.float64)


class CkptST:
    """Safetensors by HTTP range (remote_st); `idx` may be passed in from the parent process (headers are disk-cached)."""
    def __init__(self, model, rev, idx=None):
        self.repo, self.rev = mcfg.get(model)["repo"], rev
        self.idx = idx or R.index(self.repo, rev)
        self.names = list(self.idx)

    def get_many(self, keys):
        return {k: _fp16_exact(a, k) for k, a, _ in R.fetch_many(self.idx, keys)}


def bin_index(path):
    """Index a torch zip checkpoint (pytorch_model.bin) WITHOUT torch: {name: (storage key, dtype, offset, shape, stride)}.
    Unpickles data.pkl with torch's reducers replaced by tuple builders; storages are read lazily by bin_tensor."""
    DT = {"HalfStorage": np.float16, "FloatStorage": np.float32, "DoubleStorage": np.float64, "BFloat16Storage": "bf16",
          "LongStorage": np.int64, "IntStorage": np.int32, "ByteStorage": np.uint8, "BoolStorage": np.bool_}

    def rebuild(storage, offset, size, stride, *rest):
        return ("tensor", storage, int(offset), tuple(int(x) for x in size), tuple(int(x) for x in stride))

    class Unp(pickle.Unpickler):
        def find_class(self, mod, name):
            if name in ("_rebuild_tensor_v2", "_rebuild_tensor_v3"):
                return rebuild
            if name == "_rebuild_parameter":
                return lambda data, *a: data
            if mod == "torch" and name in DT:
                return DT[name]
            if (mod, name) == ("collections", "OrderedDict"):
                return OrderedDict
            raise pickle.UnpicklingError(f"refusing {mod}.{name}")

        def persistent_load(self, pid):
            assert pid[0] == "storage", pid
            return ("storage", pid[2], pid[1])        # key, dtype

    with zipfile.ZipFile(path) as zf:
        pkl = [n for n in zf.namelist() if n.endswith("/data.pkl") or n == "data.pkl"][0]
        prefix = pkl[:-len("data.pkl")]
        with zf.open(pkl) as f:
            sd = Unp(f).load()
    out = {}
    for k, t in sd.items():
        if isinstance(t, tuple) and t[0] == "tensor":
            _, (_, key, dt), off, shape, stride = t
            out[k] = (f"{prefix}data/{key}", dt, off, shape, stride)
    return out


def bin_tensor(path, ent):
    name, dt, off, shape, stride = ent
    with zipfile.ZipFile(path) as zf:
        raw = zf.read(name)
    if dt == "bf16":
        a = (np.frombuffer(raw, dtype=np.uint16).astype(np.uint32) << 16).view(np.float32)
    else:
        a = np.frombuffer(raw, dtype=dt)
    it = a.itemsize
    return np.array(np.lib.stride_tricks.as_strided(a[off:], shape, tuple(s * it for s in stride)))


class CkptBin:
    """PolyPythias: the .bin was downloaded by the parent (download_file, verified); each worker reads its own tensors."""
    def __init__(self, path):
        self.path = Path(path)
        self.idx = bin_index(self.path)
        self.names = list(self.idx)

    def get_many(self, keys):
        return {k: _fp16_exact(bin_tensor(self.path, self.idx[k]), k) for k in keys}


class CkptDict:
    """Synthetic source for tests: {name: array}."""
    def __init__(self, d):
        self.d, self.names = d, list(d)

    def get_many(self, keys):
        return {k: _fp16_exact(np.asarray(self.d[k]), k) for k in keys}


def layer_mats(ck, L, c):
    H, DH, D = c["H"], c["DH"], c["D"]
    p = f"gpt_neox.layers.{L}."
    names = [p + "attention.query_key_value.weight", p + "attention.dense.weight",
             p + "mlp.dense_h_to_4h.weight", p + "mlp.dense_4h_to_h.weight"]
    t = ck.get_many(names)
    qkv = t[names[0]].reshape(H, 3, DH, D)
    return {"Q": qkv[:, 0].reshape(H * DH, D), "K": qkv[:, 1].reshape(H * DH, D), "V": qkv[:, 2].reshape(H * DH, D),
            "O": t[names[1]], "MLP_IN": t[names[2]], "MLP_OUT": t[names[3]]}


def n_layers(ck):
    return 1 + max(int(k.split(".")[2]) for k in ck.names if k.startswith("gpt_neox.layers."))


def extract_layer(ck, model, rev, L, path):
    """Compute + durable_save one layer file. Returns per-matrix seconds."""
    c = mcfg.get(model)
    t0 = time.time()
    mats = layer_mats(ck, L, c)
    tf = time.time() - t0
    out = {"q_grid": Q_GRID, "box_ell": box_sizes(c["DH"]), "hist_edges": HIST_EDGES, "estimator_version": np.array(EST)}
    tm = {}
    for M in MATS:
        t1 = time.time()
        W = mats[M]
        matrix_stats(W, M, c["DH"], out)
        seed = null_seed(model, rev, L, M)
        G, scale = null_draw(W, seed)
        matrix_stats(G, M, c["DH"], out, suffix="_null")
        out[f"null_seed_{M}"] = np.array(seed, dtype=np.uint64)
        out[f"null_scale_{M}"] = np.array(scale)
        del G
        tm[M] = time.time() - t1
    R.durable_save(path, lambda t: np.savez(t, **out))
    tm["fetch"] = tf
    tm["total"] = time.time() - t0
    return tm


def _open(model, rev, src):
    """src: None -> fresh safetensors index; dict -> the parent's remote_st.index ({tensor: header}); str -> .bin path."""
    if src is None:
        return CkptST(model, rev)
    if isinstance(src, dict):
        return CkptST(model, rev, idx=src)
    return CkptBin(src)


def _worker(args):
    model, rev, L, path, src, out_root = args
    try:
        check_stop(out_root)
        tm = extract_layer(_open(model, rev, src), model, rev, L, Path(path))
        return L, "ok", tm
    except R.Stopped as e:
        return L, "stopped", str(e)


def _fmt(tm):
    return " ".join(f"{k}={v:.1f}s" for k, v in tm.items())


def run(model, rev, workers=1, layers=None, out_root=None):
    c = mcfg.get(model)
    out_root = Path(out_root or OUT_ROOT)
    d = out_root / model / rev
    d.mkdir(parents=True, exist_ok=True)
    if (d / "DONE").exists():
        print(f"{model} {rev} DONE exists; skipping", flush=True)
        return
    check_stop(out_root)
    bin_path = None
    if c.get("fmt") == "bin":
        (ROOT / "cache" / "bin_tmp").mkdir(parents=True, exist_ok=True)
        bin_path = R.download_file(c["repo"], "pytorch_model.bin", rev,
                                   ROOT / "cache" / "bin_tmp" / f"{c['repo'].replace('/', '__')}__{rev}.bin")
        ck, src = CkptBin(bin_path), str(bin_path)
    else:
        ck = CkptST(model, rev)
        src = ck.idx
    nL = n_layers(ck)
    todo = [L for L in (layers if layers is not None else range(nL)) if not (d / f"L{L:02d}.npz").exists()]
    print(f"{model} {rev} layers {nL}, to do {len(todo)}, workers {workers}", flush=True)
    stopped = None
    jobs = [(model, rev, L, str(d / f"L{L:02d}.npz"), src, str(out_root)) for L in todo]
    if workers <= 1:
        for j in jobs:
            L, st, tm = _worker(j)
            if st != "ok":
                stopped = tm; break
            print(f"{model} {rev} L{L:02d} {_fmt(tm)}", flush=True)
    else:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(workers) as pool:
            for L, st, tm in pool.imap_unordered(_worker, jobs):
                if st != "ok":
                    stopped = tm
                    pool.terminate(); break
                print(f"{model} {rev} L{L:02d} {_fmt(tm)}", flush=True)
    if bin_path is not None and (stopped is None and layers is None):
        try:
            R.evict(bin_path)
        finally:
            bin_path.unlink(missing_ok=True)
    if stopped is not None:
        raise R.Stopped(stopped)
    if layers is None and all((d / f"L{L:02d}.npz").exists() for L in range(nL)):
        R.durable_save(d / "DONE", lambda t: t.write_text(EST))
        print(f"{model} {rev} DONE", flush=True)


def _cli(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("revs", nargs="+")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--threads", type=str, default=None)        # consumed before numpy import (see top of file)
    ap.add_argument("--layers", type=str, default=None)
    ap.add_argument("--out", type=str, default=None)
    a = ap.parse_args(argv)
    layers = [int(x) for x in a.layers.split(",")] if a.layers else None
    try:
        for rev in a.revs:
            run(a.model, rev, workers=a.workers, layers=layers, out_root=a.out)
    except R.Stopped as e:
        print("STOPPED:", e, flush=True); sys.exit(3)


if __name__ == "__main__":
    _cli(sys.argv[1:])
