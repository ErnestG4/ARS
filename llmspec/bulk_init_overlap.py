"""Bulk-initialisation overlap extractor (BULK_INIT_OVERLAP_PREREG.md, sealed 2026-10-02): CPU-ONLY, numpy/scipy fp64.

Question: how much of the trained bulk is still the step-0 initialisation? For every (model, revision, layer, matrix M in
{Q, K, V, O, MLP_IN, MLP_OUT}) with W_t the trained matrix and W_0 the SAME matrix at the model's step-0 revision:
  alpha_hat   = <W_t, W_0>_F / ||W_0||_F^2                      least-squares scale of the init inside W_t   (PREREG S2)
  alpha_wd(t) = prod_{k=1..t} (1 - wd * lr(k-1))                 weight-decay shrink prediction from the published schedule
  d           = ||W_t - alpha_hat W_0||_F / ||W_t||_F           relative residual after removing the shrunk init
  rho_S       = <P_S W_t, P_S W_0>_F / (||P_S W_t||_F ||P_S W_0||_F)   P_S = U_S U_S^T (.) V_S V_S^T, (U, s, V) = SVD(W_t)
  E_init_S    = alpha_hat^2 ||P_S W_0||_F^2 / ||P_S W_t||_F^2   fraction of the trained energy in S accounted for by the init
over the index sets S (singular index k, descending sigma; bands = stage3_extract_mf.band_edges(r): [0,32), then octaves
[32,64), [64,128), ..., clipped at r = min(m, n)):
  top       k <  32                         (the spike edge s0 = 32 of MF_EXPLORE / ARMA)
  bulk      32 <= k < e_last                (k >= 32 EXCLUDING the deepest octave [e_last, r) -- the set the S3 reading rule counts;
                                             MF_EXPLORE S3: the deepest octave is its own regime)
  bulk_all  k >= 32                         (PREREG S2's literal "k >= s0", incl. the deepest octave; descriptive)
  deep      e_last <= k < r                 (the deepest octave, reported separately, never counted)
  near      32 <= k < 64                    (A1: the octave next to the spike, reported as its own row like deep; level
                                             repulsion rotates P_t there -- expected to read LOWER for a geometric reason)
  bulk_core 64 <= k < e_last                (bulk minus near; descriptive)
  band      every band of band_edges(r)     (per-band rho / E_init trajectory, descriptive)
Amendment A1 lines (all banked per matrix, per reference; none changes a threshold):
  dist_raw  = ||W_t - W_0||_F / ||W_0||_F   the step-0 CONTINUITY distance; at step1 it is expected ~ lr(1)/rms(W_0) (Adam's
                                             first step moves every element by exactly lr); the verdict script gates runs on it
  p_sign    = mean(sign W_t == sign W_0), rho_from_sign = sin(pi (p - 1/2))  (inverse Gaussian map; beside rho_full)
  rms_ref, rms_wt; per revision: lr_t, alpha_wd, kosson_rms_t = sqrt(lr_t / 2 wd), kosson_rms_peak, lr_1; collect() adds
  the implied einit_pred = (alpha_wd rms_W0)^2 / ((alpha_wd rms_W0)^2 + kosson_rms_t^2) and rho_pred = sqrt(einit_pred)
  (reported-only priors from A1, never thresholds).
  alpha_S   = <P_S W_t, P_S W_0>_F / ||P_S W_0||_F^2  (descriptive, not in the PREREG: the LS scale fitted inside S; E_init_S
                                                     uses the global alpha_hat, which a strong top can shift -- verify (iii))
rho_full is the UNPROJECTED cosine <W_t, W_0>/(||W_t|| ||W_0||); rho_proj_all is the same through U U^T (.) V V^T (equal to
rho_full for square W, strictly smaller for rectangular W where U spans only the column space of W_t; banked for the check).
Implementation: C = U^T W_0 V (r x r) once per reference matrix; <P_S W_t, P_S W_0> = sum_{k in S} s_k C_kk,
||P_S W_0||^2 = ||C[S,S]||_F^2 (the full block, off-diagonal included), ||P_S W_t||^2 = sum_{k in S} s_k^2.
Nulls (PREREG S2, same construction, W_0 replaced): suffix _gauss -- an independent iid N(0,1) matrix rescaled to ||W_0||_F,
seed = first 8 bytes of sha256("bio|<model>|<rev>|L<layer>|<M>") (banked, default_rng PCG64); suffix _wrong -- the step-0
matrix of the SAME type from layer (L+1) mod n_layers (banked: wrong_layer). alpha_hat / d / rho_* / E_init_* are all
recomputed against the replacement.
Weight-decay prediction: lr(k) is the GPT-NeoX AnnealingLR as sealed in armb/q1_models.py (linear warmup over W = 0.01 x
143000 = 1430 steps, cosine to min_lr with the /E quirk, update k uses lr(k-1)); peak lr, min_lr, warmup, train-iters and
weight-decay are TRANSCRIBED in CONFIG below from EleutherAI/pythia models/{1.4B/pythia-1.4b,410M/pythia-410m}.yml
(github main a19eecb8, fetched 2026-10-02: "weight-decay": 0.1, "lr": 2e-4 / 3e-4, "min_lr": 2e-5 / 3e-5, "warmup": 0.01,
"train-iters" = "lr-decay-iters" = 143000, "lr-decay-style": "cosine"). The decay is taken as DECOUPLED
(W <- (1 - lr wd) W - lr update; GPT-NeoX "Adam" = DeepSpeed FusedAdam in adam_w mode, as sealed in armb/ARMB_PREREG.md
B1a); PolyPythias seeds use the 410M yml (same config, different seed; mcfg convention). Every number is banked with the
config it came from (keys cfg_*); nothing is assumed silently.
Data path = stage3_extract_mf (imported): CkptST (safetensors by HTTP range, remote_st), CkptBin (PolyPythias .bin, numpy
reader), layer_mats orientation (Q/K/V rows (head, d_head) x D from the fused QKV; O as stored; MLP_IN 4D x D; MLP_OUT
D x 4D), fp16-grid assertion, STOP + 10 GB disk guard (stage3_extract_mf.check_stop, probing this module's output root).
The step-0 matrices are banked ONCE per model as fp16 (lossless: asserted on the fp16 grid) in <out>/<model>/init/L<layer>.npz
and re-read for every revision (26 revisions would otherwise re-stream / re-download step 0 each time).
Outputs: <out>/<model>/<rev>/L<layer>.npz (durable_save; resumable: existing layer files are skipped; DONE per revision),
then results/bulk_init_overlap/<model>.json (everything scalar, nested rev -> layer -> M -> ref), <model>_long.csv (one row
per rev x layer x M x ref), <model>_bands.csv (one row per band). Verdict words live in bulk_init_overlap_verdict.py.
Usage: bulk_init_overlap.py <model> <rev> [<rev> ...] [--workers N] [--threads T] [--layers 0,1,...] [--out DIR]
                            [--results DIR] [--no-collect]
  Models outside ALLOW (pythia-1.4b, pythia-410m-seed1..5) are REFUSED unless --out is given (synthetic / test runs only;
  seeds 6-9, 410m-std, 1b, 70m and Arm B stay UNREAD per PREREG S1). Caller applies nice/ionice (spot rules).
"""
import os, sys


def _threads_from_argv():
    if "--threads" in sys.argv:
        t = sys.argv[sys.argv.index("--threads") + 1]
        for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
            os.environ[k] = t


_threads_from_argv()
from pathlib import Path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import time, hashlib, json, csv, math
import numpy as np
from scipy.linalg import svd as _svd
import remote_st as R
import mcfg
import stage3_extract_mf as X

OUT_ROOT = ROOT / "cache" / "bio"
RESULTS = ROOT / "results" / "bulk_init_overlap"
EST = "bulk-init-overlap-v1 (cpu fp64 scipy gesdd; C = U^T W0 V block projections; gauss + wrong-layer nulls; AnnealingLR wd)"
ALLOW = ("pythia-1.4b",) + tuple(f"pythia-410m-seed{k}" for k in range(1, 6))
MATS = X.MATS
SPIKE = X.SPIKE
SETS = ("top", "bulk", "bulk_all", "deep", "near", "bulk_core")
REFS = ("init", "gauss", "wrong")
SCALARS = ("alpha_hat", "d", "dist_raw", "rms_ref", "p_sign", "rho_from_sign", "rho_full", "rho_proj_all") \
    + tuple(f"rho_{s}" for s in SETS) + tuple(f"einit_{s}" for s in SETS) + tuple(f"alpha_{s}" for s in SETS)

# Transcribed from EleutherAI/pythia models/*.yml @ a19eecb8 (2026-10-02); see module docstring. Values are READ here, not assumed.
_YML = "https://github.com/EleutherAI/pythia/blob/a19eecb807ec2c79a39ebf18108816e6ffffc1d5/models/"
CONFIG = {
    "pythia-1.4b": dict(weight_decay=0.1, lr=2.0e-4, min_lr=2.0e-5, warmup=0.01, train_iters=143000, lr_decay_iters=143000,
                        lr_decay_style="cosine", optimizer="Adam (GPT-NeoX; DeepSpeed FusedAdam, adam_w_mode = decoupled decay)",
                        source=_YML + "1.4B/pythia-1.4b.yml"),
    "pythia-410m": dict(weight_decay=0.1, lr=3.0e-4, min_lr=3.0e-5, warmup=0.01, train_iters=143000, lr_decay_iters=143000,
                        lr_decay_style="cosine", optimizer="Adam (GPT-NeoX; DeepSpeed FusedAdam, adam_w_mode = decoupled decay)",
                        source=_YML + "410M/pythia-410m.yml"),
}
DECAY_FORM = "decoupled: W_t = prod_{k=1..t} (1 - lr(k-1) * wd) W_0 + (update terms); alpha_wd(t) = that product"


def config_for(model):
    """The yml block a model's weight-decay prediction uses (PolyPythias seeds -> the 410M yml; recorded as cfg_source)."""
    if model in CONFIG:
        return dict(CONFIG[model], applies_to=model)
    if model.startswith("pythia-410m"):
        return dict(CONFIG["pythia-410m"], applies_to=model, note="PolyPythias seed: 410M yml, different seed (mcfg convention)")
    raise KeyError(f"no transcribed config for {model}; add it to CONFIG from the published yml before running")


# ---------------------------------------------------------------- STOP / disk guard on THIS output root
def check_stop(out_root=None):
    X.check_stop(out_root or OUT_ROOT)


R.check_stop = lambda: check_stop(OUT_ROOT)


# ---------------------------------------------------------------- LR schedule and weight-decay prediction
def lr_at(n, peak, min_lr, warmup_steps, total):
    """GPT-NeoX v1.0 AnnealingLR (armb/q1_models.lr, sealed B1a): lr used by optimizer update n+1. Vectorised over n."""
    n = np.asarray(n, dtype=np.float64)
    num = np.minimum(n, total - warmup_steps)
    warm = peak * num / warmup_steps if warmup_steps > 0 else np.full_like(num, peak)
    cos = np.maximum(peak / 2.0 * (np.cos(np.pi * (num - warmup_steps) / total) + 1.0), min_lr)
    return np.where((warmup_steps > 0) & (n <= warmup_steps), warm, cos)


def schedule(model):
    """(cfg, lr array over k = 0..train_iters-1, log alpha_wd over t = 0..train_iters)."""
    c = config_for(model)
    W = int(round(c["warmup"] * c["train_iters"]))
    lr = lr_at(np.arange(c["train_iters"]), c["lr"], c["min_lr"], W, c["lr_decay_iters"])
    log_a = np.concatenate([[0.0], np.cumsum(np.log1p(-c["weight_decay"] * lr))])
    return dict(c, warmup_steps=W), lr, log_a


def alpha_wd(model, step):
    """prod_{k=1..step} (1 - wd * lr(k-1)) from the transcribed config; step 0 -> 1."""
    c, lr, log_a = schedule(model)
    if step < 0 or step > c["train_iters"]:
        raise ValueError(f"step {step} outside [0, {c['train_iters']}]")
    return float(np.exp(log_a[step]))


def schedule_at(model, step):
    """Reported-only schedule lines at one checkpoint: alpha_wd(step), lr(step) (the lr the NEXT update would use), the
    Kosson equilibrium rms sqrt(eta / 2 lambda) per element at lr(step) and at peak lr (A1: declared expectation, not a
    threshold). step < 0 (synthetic revision names) -> NaN except the peak value."""
    cfg, lr, log_a = schedule(model)
    wd = cfg["weight_decay"]
    out = {"alpha_wd": float("nan"), "lr_t": float("nan"), "kosson_rms_t": float("nan"),
           "kosson_rms_peak": math.sqrt(cfg["lr"] / (2 * wd)), "lr_1": float(lr[1]) if len(lr) > 1 else float("nan")}
    if 0 <= step <= cfg["train_iters"]:
        lt = float(lr[min(step, len(lr) - 1)])
        out.update(alpha_wd=float(np.exp(log_a[step])), lr_t=lt, kosson_rms_t=math.sqrt(lt / (2 * wd)))
    return out


def step_of(rev):
    return int(rev[4:]) if rev.startswith("step") and rev[4:].isdigit() else -1


# ---------------------------------------------------------------- measurement
def index_sets(r):
    """band_edges(r) and the named index sets as (lo, hi) slices. bulk = [32, e_last) is EMPTY (None) when r <= 64."""
    e = X.band_edges(r)
    top = (0, int(e[1]))
    deep = (int(e[-2]), int(e[-1])) if len(e) >= 3 else (int(e[-1]), int(e[-1]))
    bulk_all = (int(e[1]), r)
    bulk = (int(e[1]), deep[0]) if deep[0] > e[1] else None
    near = (int(e[1]), int(e[2])) if len(e) >= 3 and e[2] > e[1] else None          # A1: the octave next to the spike, own row
    core = (int(e[2]), deep[0]) if len(e) >= 4 and deep[0] > e[2] else None          # bulk minus near (descriptive)
    return e, {"top": top, "bulk": bulk, "bulk_all": bulk_all, "deep": deep, "near": near, "bulk_core": core}


def null_seed(model, rev, L, M):
    return int.from_bytes(hashlib.sha256(f"bio|{model}|{rev}|L{L}|{M}".encode()).digest()[:8], "little")


def gauss_like(W0, seed):
    """iid N(0,1) of W0's shape rescaled to ||W0||_F exactly."""
    G = np.random.default_rng(seed).standard_normal(W0.shape)
    return G * (np.linalg.norm(W0) / np.linalg.norm(G))


def _ref_stats(U, s, Vh, Wt, Ref, sets, edges, fro_t):
    """All scalars of one reference matrix Ref (W0 or a null) against the decomposed W_t."""
    ip = float(np.vdot(Wt, Ref))
    f0 = float(np.linalg.norm(Ref))
    a = ip / f0 ** 2
    p = float(np.mean((Wt * Ref) > 0))                       # per-element sign agreement (a zero counts as disagreement)
    out = {"alpha_hat": a, "d": float(np.linalg.norm(Wt - a * Ref)) / fro_t, "rho_full": ip / (fro_t * f0), "frob_ref": f0,
           "dist_raw": float(np.linalg.norm(Wt - Ref)) / f0,   # ||W_t - Ref||_F / ||Ref||_F: the A1 step-0 continuity distance
           "rms_ref": f0 / math.sqrt(Ref.size), "p_sign": p,
           "rho_from_sign": math.sin(math.pi * (p - 0.5))}     # inverse of the Gaussian map p = 1/2 + arcsin(rho)/pi
    C = (U.T @ Ref) @ Vh.T                     # r x r: Ref seen in W_t's singular bases
    cd = np.diag(C)
    num_k = s * cd                              # <P_S W_t, P_S Ref> = sum_{k in S} s_k C_kk
    s2 = s * s

    nan3 = (float("nan"),) * 3

    def one(lo, hi):
        """(rho_S, E_init_S, alpha_S) for k in [lo, hi); alpha_S = <P_S W_t, P_S Ref> / ||P_S Ref||^2 is the LS scale fitted
        INSIDE S (descriptive; E_init uses the PREREG's global alpha_hat, which a strong top can contaminate)."""
        if lo >= hi:
            return nan3
        n_ = float(num_k[lo:hi].sum()); c2 = float((C[lo:hi, lo:hi] ** 2).sum()); t2 = float(s2[lo:hi].sum())
        if t2 <= 0 or c2 <= 0:
            return nan3
        return n_ / math.sqrt(t2 * c2), a * a * c2 / t2, n_ / c2

    out["rho_proj_all"], _, _ = one(0, len(s))
    for name, sl in sets.items():
        rho, e, al = one(*sl) if sl is not None else nan3
        out[f"rho_{name}"], out[f"einit_{name}"], out[f"alpha_{name}"] = rho, e, al
    nb = len(edges) - 1
    rb, eb = np.empty(nb), np.empty(nb)
    for b in range(nb):
        rb[b], eb[b], _ = one(int(edges[b]), int(edges[b + 1]))
    out["rho_band"], out["einit_band"] = rb, eb
    return out


def measure(Wt, W0, refs):
    """One matrix: SVD of W_t (fp64 gesdd) + every PREREG S2 quantity for W0 ('init') and for each null in refs
    ({'gauss': G, 'wrong': W0'}). Returns a flat dict: <stat>_<ref-suffix> with suffix '' for init, '_gauss', '_wrong'."""
    Wt = np.asarray(Wt, dtype=np.float64)
    U, s, Vh = _svd(Wt, full_matrices=False, lapack_driver="gesdd", check_finite=False)
    r = len(s)
    edges, sets = index_sets(r)
    fro_t = float(np.linalg.norm(Wt))
    out = {"sig": s, "band_edges": edges, "frob_wt": fro_t, "rms_wt": fro_t / math.sqrt(Wt.size), "r": r,
           "n_bulk": (sets["bulk"][1] - sets["bulk"][0]) if sets["bulk"] else 0,
           "n_deep": sets["deep"][1] - sets["deep"][0]}
    for suffix, Ref in (("", W0),) + tuple((f"_{k}", v) for k, v in refs.items()):
        Ref = np.asarray(Ref, dtype=np.float64)
        assert Ref.shape == Wt.shape, f"reference shape {Ref.shape} != {Wt.shape}"
        for k, v in _ref_stats(U, s, Vh, Wt, Ref, sets, edges, fro_t).items():
            out[f"{k}{suffix}"] = v
    return out


# ---------------------------------------------------------------- step-0 bank (fp16, lossless) and per-layer extraction
def init_path(out_root, model, L):
    return Path(out_root) / model / "init" / f"L{L:02d}.npz"


def load_init(path):
    z = np.load(path)
    return {M: z[M].astype(np.float64) for M in MATS}


def save_init(path, mats):
    for M in MATS:
        a16 = mats[M].astype(np.float16)
        assert np.array_equal(a16.astype(np.float64), mats[M]), f"{M}: step-0 values not on the fp16 grid; refusing lossy bank"
    R.durable_save(path, lambda t: np.savez(t, **{M: mats[M].astype(np.float16) for M in MATS}, estimator_version=np.array(EST)))


def layer_outputs(mats, w0, w0_wrong, model, rev, L, wrong_layer, cfg, sched):
    """Every banked object of one layer from already-fetched matrices (mats, w0, w0_wrong: {M: fp64 array}); the config
    block and sched = schedule_at(model, step) are computed ONCE by the parent and recorded here. Returns (dict for
    np.savez, per-matrix seconds)."""
    step = step_of(rev)
    out = {"estimator_version": np.array(EST), "model": np.array(model), "rev": np.array(rev), "layer": np.array(L),
           "step": np.array(step), "wrong_layer": np.array(wrong_layer),
           **{k: np.array(v) for k, v in sched.items()},
           "cfg_weight_decay": np.array(cfg["weight_decay"]), "cfg_lr": np.array(cfg["lr"]), "cfg_min_lr": np.array(cfg["min_lr"]),
           "cfg_warmup": np.array(cfg["warmup"]), "cfg_train_iters": np.array(cfg["train_iters"]),
           "cfg_source": np.array(cfg["source"]), "cfg_decay_form": np.array(DECAY_FORM)}
    tm = {}
    for M in MATS:
        t1 = time.time()
        seed = null_seed(model, rev, L, M)
        G = gauss_like(w0[M], seed)
        res = measure(mats[M], w0[M], {"gauss": G, "wrong": w0_wrong[M]})
        del G
        for k, v in res.items():
            out[f"{k}_{M}"] = np.asarray(v)
        out[f"gauss_seed_{M}"] = np.array(seed, dtype=np.uint64)
        tm[M] = time.time() - t1
    return out, tm


def extract_layer(ck, model, rev, L, path, w0, w0_wrong, wrong_layer, cfg, sched):
    """Fetch one layer, compute, durable_save. Returns per-matrix seconds."""
    t0 = time.time()
    mats = X.layer_mats(ck, L, mcfg.get(model))
    tf = time.time() - t0
    out, tm = layer_outputs(mats, w0, w0_wrong, model, rev, L, wrong_layer, cfg, sched)
    R.durable_save(path, lambda t: np.savez(t, **out))
    tm["fetch"] = tf
    tm["total"] = time.time() - t0
    return tm


def _init_worker(args):
    model, L, path, src, out_root = args
    try:
        check_stop(out_root)
        ck = X._open(model, "step0", src)
        save_init(Path(path), X.layer_mats(ck, L, mcfg.get(model)))
        return L, "ok", {"init": 0.0}
    except R.Stopped as e:
        return L, "stopped", str(e)


def _worker(args):
    model, rev, L, path, src, out_root, p0, p0w, wrong_layer, cfg, sched = args
    try:
        check_stop(out_root)
        w0, w0w = load_init(p0), load_init(p0w)
        tm = extract_layer(X._open(model, rev, src), model, rev, L, Path(path), w0, w0w, wrong_layer, cfg, sched)
        return L, "ok", tm
    except R.Stopped as e:
        return L, "stopped", str(e)


def _fmt(tm):
    return " ".join(f"{k}={v:.1f}s" for k, v in tm.items())


def _run_jobs(fn, jobs, workers, label):
    """Run jobs through fn sequentially or in a spawn pool; raise Stopped on the first stop."""
    stopped = None
    if workers <= 1:
        for j in jobs:
            L, st, tm = fn(j)
            if st != "ok":
                stopped = tm; break
            print(f"{label} L{L:02d} {_fmt(tm)}", flush=True)
    else:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(workers) as pool:
            for L, st, tm in pool.imap_unordered(fn, jobs):
                if st != "ok":
                    stopped = tm
                    pool.terminate(); break
                print(f"{label} L{L:02d} {_fmt(tm)}", flush=True)
    if stopped is not None:
        raise R.Stopped(stopped)


def _source(model, rev):
    """(ck, src for workers, bin_path or None): download the .bin once (PolyPythias) or index the safetensors."""
    c = mcfg.get(model)
    if c.get("fmt") == "bin":
        (ROOT / "cache" / "bin_tmp").mkdir(parents=True, exist_ok=True)
        bin_path = R.download_file(c["repo"], "pytorch_model.bin", rev,
                                   ROOT / "cache" / "bin_tmp" / f"{c['repo'].replace('/', '__')}__{rev}.bin")
        return X._open(model, rev, str(bin_path)), str(bin_path), bin_path
    ck = X._open(model, rev, None)
    return ck, ck.idx, None


def _release(bin_path):
    if bin_path is not None:
        try:
            R.evict(bin_path)
        finally:
            bin_path.unlink(missing_ok=True)


def ensure_init(model, layers, out_root, workers):
    """Bank the step-0 matrices (fp16, lossless) for `layers` (plus their wrong-instance partners) if not yet present."""
    out_root = Path(out_root)
    need = sorted({L for L in layers if not init_path(out_root, model, L).exists()})
    if not need:
        return
    init_path(out_root, model, 0).parent.mkdir(parents=True, exist_ok=True)
    ck, src, bin_path = _source(model, "step0")
    try:
        nL = X.n_layers(ck)
        need = [L for L in need if L < nL]
        print(f"{model} step0 init bank: {len(need)} layers to bank, workers {workers}", flush=True)
        _run_jobs(_init_worker, [(model, L, str(init_path(out_root, model, L)), src, str(out_root)) for L in need],
                  workers, f"{model} init")
    finally:
        _release(bin_path)


def run(model, rev, workers=1, layers=None, out_root=None):
    out_root = Path(out_root or OUT_ROOT)
    d = out_root / model / rev
    d.mkdir(parents=True, exist_ok=True)
    if (d / "DONE").exists():
        print(f"{model} {rev} DONE exists; skipping", flush=True)
        return
    check_stop(out_root)
    cfg = config_for(model)
    sched = schedule_at(model, step_of(rev))
    ck, src, bin_path = _source(model, rev)
    try:
        nL = X.n_layers(ck)
        if nL != mcfg.get(model)["n_layer"]:
            print(f"NOTE {model} {rev}: checkpoint has {nL} layers, mcfg says {mcfg.get(model)['n_layer']} (synthetic?)", flush=True)
        want = list(layers) if layers is not None else list(range(nL))
        todo = [L for L in want if not (d / f"L{L:02d}.npz").exists()]
        if todo:
            ensure_init(model, sorted(set(todo) | {(L + 1) % nL for L in todo}), out_root, workers)
        print(f"{model} {rev} layers {nL}, to do {len(todo)}, workers {workers}, alpha_wd {sched['alpha_wd']:.6g}", flush=True)
        jobs = [(model, rev, L, str(d / f"L{L:02d}.npz"), src, str(out_root), str(init_path(out_root, model, L)),
                 str(init_path(out_root, model, (L + 1) % nL)), (L + 1) % nL, cfg, sched) for L in todo]
        _run_jobs(_worker, jobs, workers, f"{model} {rev}")
    finally:
        if layers is None:
            _release(bin_path)
        elif bin_path is not None:
            R.evict(bin_path)
    if layers is None and all((d / f"L{L:02d}.npz").exists() for L in range(nL)):
        R.durable_save(d / "DONE", lambda t: t.write_text(EST))
        print(f"{model} {rev} DONE", flush=True)


# ---------------------------------------------------------------- collection: npz bank -> JSON + long CSVs
def _f(x):
    x = float(x)
    return None if math.isnan(x) else x


def layer_record(z):
    """One L<layer>.npz -> {M: {"r", "n_bulk", "n_deep", "band_edges", "init": {...}, "gauss": {...}, "wrong": {...}}}."""
    rec = {}
    for M in MATS:
        m = {"r": int(z[f"r_{M}"]), "n_bulk": int(z[f"n_bulk_{M}"]), "n_deep": int(z[f"n_deep_{M}"]),
             "band_edges": [int(v) for v in z[f"band_edges_{M}"]], "frob_wt": float(z[f"frob_wt_{M}"]),
             "rms_wt": float(z[f"rms_wt_{M}"]), "gauss_seed": int(z[f"gauss_seed_{M}"])}
        for ref in REFS:
            sfx = "" if ref == "init" else f"_{ref}"
            m[ref] = {k: _f(z[f"{k}{sfx}_{M}"]) for k in SCALARS}
            m[ref]["frob_ref"] = float(z[f"frob_ref{sfx}_{M}"])
            m[ref]["rho_band"] = [_f(v) for v in z[f"rho_band{sfx}_{M}"]]
            m[ref]["einit_band"] = [_f(v) for v in z[f"einit_band{sfx}_{M}"]]
        # A1 reported-only lines: the shrunk init's per-element rms vs the Kosson equilibrium rms of the update part, and the
        # E_init / rho they would imply if the two were orthogonal (NOT a threshold; a prior for the reading).
        awd, k_t = float(z["alpha_wd"]), float(z["kosson_rms_t"])
        init_rms = awd * m["init"]["rms_ref"]
        e_pred = init_rms ** 2 / (init_rms ** 2 + k_t ** 2) if np.isfinite(awd) and np.isfinite(k_t) else float("nan")
        m["kosson"] = {"init_rms_shrunk": _f(init_rms), "kosson_rms_t": _f(k_t), "einit_pred": _f(e_pred),
                       "rho_pred": _f(math.sqrt(e_pred)) if np.isfinite(e_pred) else None}
        rec[M] = m
    return rec


def collect(model, out_root=None, results=None):
    """Every <out>/<model>/<rev>/L*.npz present -> results/<model>.json, <model>_long.csv, <model>_bands.csv."""
    out_root, results = Path(out_root or OUT_ROOT), Path(results or RESULTS)
    results.mkdir(parents=True, exist_ok=True)
    cfg, _, _ = schedule(model)
    J = {"model": model, "estimator_version": EST, "config": cfg, "decay_form": DECAY_FORM,
         "prereg": "BULK_INIT_OVERLAP_PREREG.md (+ Amendment A1)",
         "sets": {"top": "k < 32", "bulk": "32 <= k < e_last (deepest octave excluded; the S3 counted set)", "bulk_all": "k >= 32",
                  "deep": "deepest octave [e_last, r) (own row)", "near": "[32, 64), the octave next to the spike (A1: own row)",
                  "bulk_core": "[64, e_last) = bulk minus near (descriptive)"}, "revs": {}}
    long_rows, band_rows = [], []
    for rd in sorted((p for p in (out_root / model).iterdir() if p.is_dir() and p.name.startswith("step")),
                     key=lambda p: step_of(p.name)):
        rev = rd.name
        files = sorted(rd.glob("L[0-9][0-9].npz"))
        if not files:
            continue
        step = step_of(rev)
        sched = schedule_at(model, step)
        rv = {"step": step, **{k: _f(v) for k, v in sched.items()}, "done": (rd / "DONE").exists(), "layers": {}}
        for f in files:
            z = np.load(f)
            L = int(z["layer"])
            rec = layer_record(z)
            rv["layers"][str(L)] = {"wrong_layer": int(z["wrong_layer"]), **rec}
            for M, m in rec.items():
                for ref in REFS:
                    base = dict(model=model, rev=rev, step=step, layer=L, M=M, ref=ref, r=m["r"], n_bulk=m["n_bulk"], n_deep=m["n_deep"],
                                alpha_wd=rv["alpha_wd"], lr_t=rv["lr_t"], kosson_rms_t=rv["kosson_rms_t"], rms_wt=m["rms_wt"])
                    long_rows.append({**base, **{k: m[ref][k] for k in SCALARS}})
                    for b in range(len(m["band_edges"]) - 1):
                        band_rows.append({**base, "band": b, "k_lo": m["band_edges"][b], "k_hi": m["band_edges"][b + 1],
                                          "rho": m[ref]["rho_band"][b], "einit": m[ref]["einit_band"][b]})
        J["revs"][rev] = rv
    R.durable_save(results / f"{model}.json", lambda t: t.write_text(json.dumps(J, indent=1)))
    for name, rows in ((f"{model}_long.csv", long_rows), (f"{model}_bands.csv", band_rows)):
        if rows:
            def _w(t, rows=rows):
                with open(t, "w", newline="") as fh:
                    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                    w.writeheader(); w.writerows(rows)
            R.durable_save(results / name, _w)
    print(f"{model}: {len(J['revs'])} revs, {len(long_rows)} matrix rows -> {results / (model + '.json')}", flush=True)
    return J


def final_rows(J, rev="step143000"):
    """Flat per-matrix rows at one revision from a model JSON (what the verdict reads)."""
    rows = []
    rv = J["revs"].get(rev)
    if rv is None:
        return rows
    for L, lay in rv["layers"].items():
        for M in MATS:
            m = lay[M]
            i = m["init"]
            rows.append(dict(model=J["model"], rev=rev, layer=int(L), M=M, r=m["r"], n_bulk=m["n_bulk"],
                             rho_bulk=i["rho_bulk"], rho_bulk_gauss=m["gauss"]["rho_bulk"], rho_bulk_wrong=m["wrong"]["rho_bulk"],
                             rho_deep=i["rho_deep"], rho_near=i["rho_near"], rho_bulk_core=i["rho_bulk_core"], rho_top=i["rho_top"],
                             rho_bulk_all=i["rho_bulk_all"], rho_full=i["rho_full"], rho_from_sign=i["rho_from_sign"], p_sign=i["p_sign"],
                             einit_bulk=i["einit_bulk"], einit_deep=i["einit_deep"], einit_near=i["einit_near"],
                             alpha_hat=i["alpha_hat"], alpha_bulk=i["alpha_bulk"], alpha_wd=rv["alpha_wd"], d=i["d"],
                             dist_raw=i["dist_raw"], rms_w0=i["rms_ref"], rms_wt=m["rms_wt"], lr_1=rv["lr_1"],
                             kosson_einit_pred=m["kosson"]["einit_pred"], kosson_rho_pred=m["kosson"]["rho_pred"]))
    return rows


def _cli(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("revs", nargs="+")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--threads", type=str, default=None)        # consumed before numpy import (see top of file)
    ap.add_argument("--layers", type=str, default=None)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--results", type=str, default=None)
    ap.add_argument("--no-collect", action="store_true")
    a = ap.parse_args(argv)
    if a.model not in ALLOW and a.out is None:
        raise SystemExit(f"REFUSED: {a.model} not in the allow-list {list(ALLOW)} (PREREG S1: held out / UNREAD); pass --out for synthetic runs")
    layers = [int(x) for x in a.layers.split(",")] if a.layers else None
    try:
        for rev in a.revs:
            run(a.model, rev, workers=a.workers, layers=layers, out_root=a.out)
    except R.Stopped as e:
        print("STOPPED:", e, flush=True); sys.exit(3)
    if not a.no_collect:
        collect(a.model, a.out, a.results)


if __name__ == "__main__":
    _cli(sys.argv[1:])
