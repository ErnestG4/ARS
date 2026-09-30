"""Stage 3 extractor: bank raw spectral objects for one Pythia checkpoint (no statistics chosen here).

STREAMS tensors from HF by HTTP range straight into RAM -> GPU (remote_st.fetch); NO checkpoint touches disk
(2026-09-25: banking full checkpoints filled the Windows host disk). Writes cache/s3/<model>/<rev>/L<layer>.npz +
GLOBAL.npz. Resumable per layer; honours STOP and the host-disk reserve. GPU fp64 throughout.

Per layer, for M in Q, K, V, O (2048x2048 full), MLP_IN (8192x2048), MLP_OUT (2048x8192):
  sig_<M>            all singular values, descending (fp64, direct SVD)
  U32_<M>, V32_<M>   top-32 left/right singular vectors (fp32; ~110 MB per checkpoint in total)
  ipr_u_<M>, ipr_v_<M>   IPR sum(u^4) of EVERY left/right singular vector (same order as sig)
  pt_u_<M>, pt_v_<M>     Porter-Thomas KS: KS distance of sqrt(n)*u to N(0,1), every vector
  rms_<M>            entry rms (precision floor = u * rms * (sqrt m + sqrt n))
Per head h (16) for Q, K, V, O: sighead_<M> (16,128) descending.
Circuits per head (LayerNorm gains FOLDED, LN centering and all biases IGNORED -- declared):
  ov_eig      (16,128) complex  eig(V_h diag(g1) O_h)            [= nonzero eig of O_h V_h diag(g1)]
  qk_eig_nr   (16,96)  complex  eig(K_nr diag(g1) (Q_nr diag(g1))^T), non-rotary dims 32..127
  qk_sym_nr   (16,)             symmetric-energy fraction of M = (Q_nr g1)^T (K_nr g1): (|M|^2+tr(M M))/(2|M|^2)
  qk_eig_full (16,128) complex, qk_sym_full (16,)  same over all 128 dims (rotary dims included; flagged)
  copy_eig    (16,128) complex  eig(V_h diag(g1) W_E^T W_U~ O_h), W_U~ = W_U diag(g_f)   [full OV circuit]
GLOBAL.npz: sig_EMB, sig_UNEMB, g_f; right vectors: IPR/PT for all + top-32; left vectors: top-32 + their IPR/PT.
  The 50304 x 2048 embedding matrices are handled in vocab chunks under the GPU cap: sigma^2 and V from the
  chunk-accumulated fp64 Gram W^T W (eigh). Gram error ~1e-16 * sigma_max^2 sits far below the fp16 storage
  floor (u = 2^-11), so no resolvable sigma is lost. U_32 = W V_32 / sigma_32. W_E^T W_U~ is chunk-accumulated.
Usage: stage3_extract.py <model> <rev> [<rev> ...]
"""
import os, sys, time, json
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from pathlib import Path
import numpy as np
import torch
import remote_st as R

ROOT = Path(__file__).resolve().parent
DEV = "cuda"
# Memory budget after three WSL crashes (Windows commit exhaustion, 2026-09-25): checkpoint tensors live on the
# GPU as fp16 -- EXACT, since Pythia's stored F32 values are fp16 upcasts (asserted per tensor) -- and are
# upcast to fp64 per matrix for SVD / to fp32 per layer for the forward pass. Hard per-process cap: an
# overrun raises OutOfMemoryError instead of taking the WSL VM down.
GPU_CAP_GB = 6.0
if torch.cuda.is_available():
    torch.cuda.set_per_process_memory_fraction(GPU_CAP_GB * 2 ** 30 / torch.cuda.get_device_properties(0).total_memory)
EST = "stage3-extract-v1 (fp64 cuda svd; LN gains folded, centering/bias ignored)"
import mcfg
H, DH, D, ROT = 16, 128, 2048, 32     # pythia-1.4b defaults; set_model() switches them (G3 replication)


def set_model(model):
    global H, DH, D, ROT
    c = mcfg.get(model)
    H, DH, D, ROT = c["H"], c["DH"], c["D"], c["ROT"]
SQ2 = np.sqrt(2.0)


class Ckpt:
    """Streams tensors HF -> GPU, cached as fp16 (exact: asserted on the fp16 grid); t() hands out fp64 copies."""
    def __init__(self, model, rev):
        self.repo, self.rev = mcfg.get(model)["repo"], rev
        self.idx = R.index(self.repo, rev)
        self.h = self.idx
        self.gpu = {}

    def get32(self, k):
        if k not in self.gpu:
            a, _ = R.fetch(self.idx, k)
            a16 = a.astype(np.float16)
            assert np.array_equal(a16.astype(np.float32), a), f"{k}: not on the fp16 grid; fp16 cache would be lossy"
            self.gpu[k] = torch.from_numpy(a16).to(DEV)
        return self.gpu[k]

    def t(self, k):
        return self.get32(k).to(torch.float64)   # fp16 -> fp64 is exact

    def fetch_all(self):
        """Stream every tensor with remote_st.fetch_many (4 tensors in flight, keep-alive; byte-identical to fetch)."""
        for k, a, _ in R.fetch_many(self.idx, [k for k in self.idx if k not in self.gpu]):
            a16 = a.astype(np.float16)
            assert np.array_equal(a16.astype(np.float32), a), f"{k}: not on the fp16 grid; fp16 cache would be lossy"
            self.gpu[k] = torch.from_numpy(a16).to(DEV)


class CkptBin(Ckpt):
    """Same interface as Ckpt for repos that publish only pytorch_model.bin (PolyPythias). The .bin is downloaded to
    cache/bin_tmp (parallel ranges, size + LFS sha256 verified), loaded with torch.load(weights_only=True, mmap=True),
    and every floating parameter is cached on the GPU as fp16 (asserted exact). Non-parameter buffers (causal-mask
    'attention.bias' / 'masked_bias', rotary 'inv_freq') are skipped: build_model rebuilds them. close() deletes the file
    and evicts its pages. Equivalence with the safetensors path: verify_bin_path.py."""
    SKIP = ("attention.bias", "attention.masked_bias", "inv_freq")

    def __init__(self, model, rev, repo=None, fn="pytorch_model.bin"):
        self.repo, self.rev = repo or mcfg.get(model)["repo"], rev
        self.path = R.download_file(self.repo, fn, rev, ROOT / "cache" / "bin_tmp" / f"{self.repo.replace('/', '__')}__{rev}.bin")
        self.sd = torch.load(self.path, map_location="cpu", weights_only=True, mmap=True)
        self.idx = {k: None for k, v in self.sd.items() if v.is_floating_point() and not k.endswith(self.SKIP)}
        self.h = self.idx
        self.gpu = {}

    def get32(self, k):
        if k not in self.gpu:
            a = self.sd[k].float().numpy()
            a16 = a.astype(np.float16)
            assert np.array_equal(a16.astype(np.float32), a), f"{k}: not on the fp16 grid; fp16 cache would be lossy"
            self.gpu[k] = torch.from_numpy(a16).to(DEV)
        return self.gpu[k]

    def fetch_all(self):
        for k in self.idx:
            self.get32(k)

    def close(self):
        self.sd = None
        try:
            R.evict(self.path)
        finally:
            self.path.unlink(missing_ok=True)


def make_ckpt(model, rev):
    return CkptBin(model, rev) if mcfg.get(model).get("fmt") == "bin" else Ckpt(model, rev)


def build_model(ck):
    """GPTNeoX on the meta device, weights ASSIGNED from the streamed GPU tensors (no second copy)."""
    from transformers import AutoConfig, GPTNeoXForCausalLM
    cfg = AutoConfig.from_pretrained(ck.repo, revision=ck.rev)
    cfg._attn_implementation = "eager"
    with torch.device("meta"):
        m = GPTNeoXForCausalLM(cfg)
    sd = {k: v for k, v in ck.gpu.items() if k in m.state_dict()}   # fp16 on GPU
    missing, unexpected = m.load_state_dict(sd, strict=False, assign=True)
    assert not missing, f"missing weights: {missing[:5]}"
    for name, mod in m.named_modules():          # non-persistent buffers (rotary inv_freq) left on meta: rebuild
        if any(b.is_meta for b in mod.buffers(recurse=False)):
            if hasattr(mod, "rope_init_fn") or "rotary" in name:   # model-agnostic (reads cfg)
                new = type(mod)(cfg, device=DEV)
                parent = m.get_submodule(name.rsplit(".", 1)[0]) if "." in name else m
                setattr(parent, name.rsplit(".", 1)[-1], new)
    bad = [n for n, t in list(m.named_parameters()) + list(m.named_buffers()) if t.is_meta]
    assert not bad, f"meta tensors left: {bad[:5]}"
    # EXACT fp32 inference with fp16 storage: each module's parameters are swapped for transient fp32 copies
    # just before it runs and the ORIGINAL fp16 tensors (shared with ck.gpu) are restored after -- no second
    # resident copy; fp16 -> fp32 is exact for these values, so the arithmetic equals an fp32 model's.
    def up(mod, args):
        for p in mod.parameters():
            p._orig16 = p.data
            p.data = p.data.float()
    def down(mod, args, out):
        for p in mod.parameters():
            p.data = p._orig16
            del p._orig16
    for mod in [m.gpt_neox.embed_in, m.embed_out, m.gpt_neox.final_layer_norm, *m.gpt_neox.layers]:
        mod.register_forward_pre_hook(up)
        mod.register_forward_hook(down)
    return m.eval()


@torch.no_grad()
def markers(ck, probes):
    """STAGE3_PREREG Events: text loss, sink (mean attention to position 0, queries >= 16), induction
    (attention i -> i-255 on r++r, second half) and second-half loss on the repeated sequences."""
    m = build_model(ck)
    nL, nH = m.config.num_hidden_layers, m.config.num_attention_heads
    ce = torch.nn.functional.cross_entropy
    sink = torch.zeros(nL, nH, device=DEV); tl = []
    text = torch.as_tensor(probes["text"], device=DEV)
    for b in range(len(text)):               # batch 1; outputs freed each step (peak GPU logged)
        ids = text[b:b + 1]
        o = m(ids, output_attentions=True)
        tl.append(ce(o.logits[:, :-1].flatten(0, 1).float(), ids[:, 1:].flatten(), reduction="none"))
        for L, A in enumerate(o.attentions):
            sink[L] += A[:, :, 16:, 0].mean(-1).sum(0)
        del o
    sink /= len(text)
    ind = torch.zeros(nL, nH, device=DEV); rl = []
    rep = torch.as_tensor(probes["rep"], device=DEV)
    i = torch.arange(256, 512, device=DEV)
    for b in range(len(rep)):
        ids = rep[b:b + 1]
        o = m(ids, output_attentions=True)
        rl.append(ce(o.logits[:, 256:-1].flatten(0, 1).float(), ids[:, 257:].flatten(), reduction="none"))
        for L, A in enumerate(o.attentions):
            ind[L] += A[:, :, i, i - 255].mean(-1).sum(0)
        del o
    ind /= len(rep)
    del m
    return {"loss_text": float(torch.cat(tl).mean()), "loss_rep2": float(torch.cat(rl).mean()),
            "sink_mean": sink.cpu().numpy(), "sink_frac": float((sink > 0.5).float().mean()),
            "induction": ind.cpu().numpy(), "estimator_version": "stage3-markers-v1"}


def vec_stats(U):
    """U (n, k) columns = unit vectors. IPR and Porter-Thomas KS (vs N(0,1) of sqrt(n) u)."""
    n = U.shape[0]
    ipr = (U ** 4).sum(0)
    z = torch.sort(U * np.sqrt(n), dim=0).values
    F = 0.5 * (1 + torch.erf(z / SQ2))
    i = torch.arange(1, n + 1, device=U.device, dtype=U.dtype)[:, None]
    ks = torch.maximum((i / n - F).amax(0), (F - (i - 1) / n).amax(0))
    return ipr.cpu().numpy(), ks.cpu().numpy()


def full_svd(W, out, M):
    U, s, Vh = torch.linalg.svd(W, full_matrices=False)
    out[f"sig_{M}"] = s.cpu().numpy()
    out[f"U32_{M}"] = U[:, :32].float().cpu().numpy()
    out[f"V32_{M}"] = Vh[:32].T.float().cpu().numpy()
    out[f"ipr_u_{M}"], out[f"pt_u_{M}"] = vec_stats(U)
    out[f"ipr_v_{M}"], out[f"pt_v_{M}"] = vec_stats(Vh.T)
    out[f"rms_{M}"] = np.array(float(W.pow(2).mean().sqrt()))


def sym_frac(A, B):
    """M = A^T B with A, B (r, D): symmetric-energy fraction via r x r traces."""
    AA, BB, BA = A @ A.T, B @ B.T, B @ A.T
    f2 = torch.trace(AA @ BB)
    trMM = torch.trace(BA @ BA)
    return float((f2 + trMM) / (2 * f2))


def layer(ck, L, EU):
    p = f"gpt_neox.layers.{L}."
    qkv = ck.t(p + "attention.query_key_value.weight").reshape(H, 3, DH, D)
    Wo = ck.t(p + "attention.dense.weight")
    g1 = ck.t(p + "input_layernorm.weight")
    out = {}
    mats = {"Q": qkv[:, 0].reshape(H * DH, D), "K": qkv[:, 1].reshape(H * DH, D),
            "V": qkv[:, 2].reshape(H * DH, D), "O": Wo,
            "MLP_IN": ck.t(p + "mlp.dense_h_to_4h.weight"), "MLP_OUT": ck.t(p + "mlp.dense_4h_to_h.weight")}
    for M, W in mats.items():
        full_svd(W, out, M)
    Oh = Wo.reshape(D, H, DH).permute(1, 0, 2)          # (H, D, DH): column block per head
    for j, M in enumerate("QKV"):
        out[f"sighead_{M}"] = torch.linalg.svdvals(qkv[:, j]).cpu().numpy()
    out["sighead_O"] = torch.linalg.svdvals(Oh).cpu().numpy()
    Qg, Kg, Vg = (qkv[:, j] * g1 for j in range(3))       # fold LN gain into input columns
    out["ov_eig"] = torch.linalg.eigvals(Vg @ Oh).cpu().numpy()
    out["copy_eig"] = torch.linalg.eigvals(Vg @ EU @ Oh).cpu().numpy()
    Qn, Kn = Qg[:, ROT:], Kg[:, ROT:]
    out["qk_eig_nr"] = torch.linalg.eigvals(Kn @ Qn.transpose(1, 2)).cpu().numpy()
    out["qk_eig_full"] = torch.linalg.eigvals(Kg @ Qg.transpose(1, 2)).cpu().numpy()
    out["qk_sym_nr"] = np.array([sym_frac(Qn[h], Kn[h]) for h in range(H)])
    out["qk_sym_full"] = np.array([sym_frac(Qg[h], Kg[h]) for h in range(H)])
    out["estimator_version"] = np.array(EST)
    return out


def run(model, rev):
    set_model(model)
    d = ROOT / "cache" / "s3" / model / rev
    d.mkdir(parents=True, exist_ok=True)
    if (d / "DONE").exists():
        return
    ck = make_ckpt(model, rev)
    n_layer = 1 + max(int(k.split(".")[2]) for k in ck.h if k.startswith("gpt_neox.layers."))
    mk = d / "MARKERS.npz"
    if not mk.exists():
        R.check_stop()
        t = time.time()
        ck.fetch_all()
        print(f"{model} {rev} streamed {sum(v.numel() for v in ck.gpu.values())*4/1e9:.2f} GB in {time.time()-t:.0f}s", flush=True)
        probes = np.load(ROOT / "results" / "probes.npz")
        out = markers(ck, probes)
        R.durable_save(mk, lambda t: np.savez(t, **out))
        print(f"{model} {rev} markers loss_text={out['loss_text']:.3f} loss_rep2={out['loss_rep2']:.3f} "
              f"sink_frac={out['sink_frac']:.3f} max_induction={out['induction'].max():.3f} "
              f"peak_gpu={torch.cuda.max_memory_allocated()/2**30:.2f}GiB", flush=True)
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()
    gf = ck.t("gpt_neox.final_layer_norm.weight")
    WE16, WU16 = ck.get32("gpt_neox.embed_in.weight"), ck.get32("embed_out.weight")   # fp16 resident
    CH = 4096
    EU = torch.zeros(D, D, device=DEV, dtype=torch.float64)          # W_E^T W_U diag(g_f), chunked over vocab
    for i in range(0, WE16.shape[0], CH):
        EU += WE16[i:i + CH].double().T @ (WU16[i:i + CH].double() * gf)
    g = d / "GLOBAL.npz"
    if not g.exists():
        out = {"g_f": gf.cpu().numpy()}
        for name, W16 in (("EMB", WE16), ("UNEMB", WU16)):
            G = torch.zeros(D, D, device=DEV, dtype=torch.float64)
            for i in range(0, W16.shape[0], CH):
                c = W16[i:i + CH].double(); G += c.T @ c
            ev, V = torch.linalg.eigh(G)
            order = torch.argsort(ev, descending=True)
            ev, V = ev[order].clamp_min(0), V[:, order]
            sig = ev.sqrt()
            out[f"sig_{name}"] = sig.cpu().numpy()
            out[f"V32_{name}"] = V[:, :32].float().cpu().numpy()
            out[f"ipr_v_{name}"], out[f"pt_v_{name}"] = vec_stats(V)
            U32 = torch.cat([W16[i:i + CH].double() @ V[:, :32] for i in range(0, W16.shape[0], CH)]) / sig[:32]
            out[f"U32_{name}"] = U32.float().cpu().numpy()
            out[f"ipr_u32_{name}"], out[f"pt_u32_{name}"] = vec_stats(U32)
            out[f"rms_{name}"] = np.array(float(torch.sqrt(torch.trace(G) / W16.numel())))
            del G, V, U32
            torch.cuda.empty_cache()
        R.durable_save(g, lambda t: np.savez(t, **out))
    for L in range(n_layer):
        f = d / f"L{L:02d}.npz"
        if f.exists():
            continue
        R.check_stop()
        t = time.time()
        out = layer(ck, L, EU)
        R.durable_save(f, lambda t: np.savez(t, **out))
        print(f"{model} {rev} L{L:02d} {time.time()-t:.1f}s peak_gpu={torch.cuda.max_memory_allocated()/2**30:.2f}GiB", flush=True)
        torch.cuda.empty_cache()
    ck.gpu.clear(); torch.cuda.empty_cache()
    if hasattr(ck, "close"):
        ck.close()
    R.durable_save(d / "DONE", lambda t: t.write_text(EST))


if __name__ == "__main__":
    try:
        for rev in sys.argv[2:]:
            run(sys.argv[1], rev)
    except R.Stopped as e:
        print("STOPPED:", e, flush=True); sys.exit(3)
