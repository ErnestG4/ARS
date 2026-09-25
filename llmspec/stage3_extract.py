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
GLOBAL.npz: sig_EMB, sig_UNEMB (+ top-32 vectors, per-vector IPR/PT), g_f.
Usage: stage3_extract.py <model> <rev> [<rev> ...]
"""
import sys, time, json
from pathlib import Path
import numpy as np
import torch
import remote_st as R

ROOT = Path(__file__).resolve().parent
DEV = "cuda"
EST = "stage3-extract-v1 (fp64 cuda svd; LN gains folded, centering/bias ignored)"
H, DH, D, ROT = 16, 128, 2048, 32
SQ2 = np.sqrt(2.0)


class Ckpt:
    def __init__(self, model, rev):
        import specs as S
        self.idx = R.index(S.MODELS[model]["repo"], rev)
        self.h = self.idx

    def t(self, k):
        a, _ = R.fetch(self.idx, k)
        return torch.from_numpy(np.array(a, dtype=np.float32)).to(DEV, torch.float64)


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
    d = ROOT / "cache" / "s3" / model / rev
    d.mkdir(parents=True, exist_ok=True)
    if (d / "DONE").exists():
        return
    ck = Ckpt(model, rev)
    n_layer = 1 + max(int(k.split(".")[2]) for k in ck.h if k.startswith("gpt_neox.layers."))
    gf = ck.t("gpt_neox.final_layer_norm.weight")
    WE, WU = ck.t("gpt_neox.embed_in.weight"), ck.t("embed_out.weight")
    EU = WE.T @ (WU * gf)                                   # (D, D) = W_E^T W_U diag(g_f)
    g = d / "GLOBAL.npz"
    if not g.exists():
        out = {"g_f": gf.cpu().numpy()}
        full_svd(WE, out, "EMB"); full_svd(WU, out, "UNEMB")
        np.savez(d / "GLOBAL.tmp.npz", **out); (d / "GLOBAL.tmp.npz").rename(g)
    for L in range(n_layer):
        f = d / f"L{L:02d}.npz"
        if f.exists():
            continue
        R.check_stop()
        t = time.time()
        out = layer(ck, L, EU)
        np.savez(d / f"L{L:02d}.tmp.npz", **out); (d / f"L{L:02d}.tmp.npz").rename(f)
        print(f"{model} {rev} L{L:02d} {time.time()-t:.1f}s", flush=True)
        torch.cuda.empty_cache()
    (d / "DONE").write_text(EST)


if __name__ == "__main__":
    try:
        for rev in sys.argv[2:]:
            run(sys.argv[1], rev)
    except R.Stopped as e:
        print("STOPPED:", e, flush=True); sys.exit(3)
