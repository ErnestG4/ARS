"""Per-model tensor layout -> per-head blocks (d_head x d_model) and full layer matrices.

G5 slot: every value carries (model, variant, step, layer, matrix, head, band, metric, estimator_version).
"""
import numpy as np

MODELS = {
    "olmo2-1b": dict(repo="allenai/OLMo-2-0425-1B", n_layer=16, n_head=16, d_head=128, d_model=2048,
                     flags="QK-norm (full-width q_norm/k_norm) + full RoPE: no position-free W_Q^T W_K; Q,K analysed separately"),
    "pythia-1.4b": dict(repo="EleutherAI/pythia-1.4b", n_layer=24, n_head=16, d_head=128, d_model=2048,
                        flags="partial rotary (25%), no QK-norm"),
}


def attn_blocks(model, idx, layer, fetch):
    """Return {matrix: (full_matrix (d_model x d_model, rows=out), per_head (n_head, d_head, d_model)),
    dtype}. O per head = the d_model x d_head column block, transposed to d_head x d_model
    (same singular values)."""
    c = MODELS[model]
    H, dh, D = c["n_head"], c["d_head"], c["d_model"]
    out = {}
    if model.startswith("olmo2"):
        p = f"model.layers.{layer}.self_attn."
        for m in "qkv":
            W, dt = fetch(idx, p + f"{m}_proj.weight")
            out[m.upper()] = (W, W.reshape(H, dh, D), dt)
        W, dt = fetch(idx, p + "o_proj.weight")
        out["O"] = (W, W.reshape(D, H, dh).transpose(1, 2, 0), dt)
    else:
        p = f"gpt_neox.layers.{layer}.attention."
        W, dt = fetch(idx, p + "query_key_value.weight")      # (3*D, D), rows = (head, qkv, d_head)
        Wr = W.reshape(H, 3, dh, D)
        for j, m in enumerate("QKV"):
            ph = Wr[:, j]
            out[m] = (ph.reshape(H * dh, D), ph, dt)
        W, dt = fetch(idx, p + "dense.weight")
        out["O"] = (W, W.reshape(D, H, dh).transpose(1, 2, 0), dt)
    return out


def grid_audit(W, dtype):
    """Fraction of F32 entries exactly on the bf16 / fp16 grids (G4: are these upcasts or fp32 masters?)."""
    if dtype != "F32":
        return {"stored": dtype}
    u = np.ascontiguousarray(W, dtype=np.float32).view(np.uint32)
    on_bf16 = float(((u & 0xFFFF) == 0).mean())
    on_fp16 = float((W.astype(np.float16).astype(np.float32) == W).mean())
    return {"stored": dtype, "frac_on_bf16_grid": on_bf16, "frac_on_fp16_grid": on_fp16}
