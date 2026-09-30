"""Gradient underflow test (ARMB_PREREG.md amendment B1a-A5 §3; criterion + decision rule committed at bec421b, BEFORE
this script ran). No training.

Weights: EleutherAI/pythia-70m step128 (released). Data: the first 64 sequences of update 129's batch (preshuffled
samples [128*1024, 128*1024 + 64)). Target: the gradient of the mean token CE over those 64 x 2048 predictions,
accumulated over 8 micro-batches of 8.
  G_ref  : fp32, no autocast
  G_cur  : fp16 autocast, per-micro loss x 4096 x 8/1024 (the failed A0's scaling), unscaled after accumulation
  G_fix  : fp16 autocast, per-micro loss x 4096 x 8/32 (Pythia-matched per-token factor), unscaled after accumulation
  G_bf16 : bf16 autocast, unscaled
Reported: rel_err = ||G - G_ref|| / ||G_ref||, cosine(G, G_ref), the fraction of entries with G == 0 where G_ref != 0;
MEASURED per-token factor in the graph = mean|d(scaled loss)/d logits| (hook on the fp16 logits) / mean|softmax - onehot|
(from the fp32 pass): Pythia's derived value is 4096 / (32 x 2048) = 0.0625.
CONFIRMED iff rel_err(G_cur) > 2 rel_err(G_fix) AND rel_err(G_fix) <= 2 rel_err(G_bf16). Output: results/armb_grad_underflow.json.
"""
import json, sys
from pathlib import Path
import numpy as np, torch

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import remote_st as RS  # noqa: E402
from bg1_score import read_bytes, SAMPLE_BYTES  # noqa: E402

assert torch.cuda.is_available(); DEV = "cuda"
torch.cuda.set_per_process_memory_fraction(0.85)
N, MICRO, SEQ, SCALE = 64, 8, 2048, 4096.0


def model_at(step):
    from transformers import AutoConfig, GPTNeoXForCausalLM
    from safetensors.torch import load_file
    cfg = AutoConfig.from_pretrained("EleutherAI/pythia-70m"); cfg._attn_implementation = "sdpa"
    m = GPTNeoXForCausalLM(cfg)
    tmp = HERE / f"_p70m_step{step}.safetensors"
    with RS.requests.get(f"https://huggingface.co/EleutherAI/pythia-70m/resolve/step{step}/model.safetensors", stream=True, timeout=300) as r, open(tmp, "wb") as f:
        r.raise_for_status()
        for c in r.iter_content(1 << 22):
            f.write(c)
    sd = load_file(str(tmp)); tmp.unlink()
    m.load_state_dict({k: v.float() for k, v in sd.items()}, strict=False)
    return m.to(DEV).train()


def grads(m, x, dtype, micro_scale, unscale):
    m.zero_grad(set_to_none=True); rec = {"abs_logit_grad": [], "logit_grad_zero_frac": []}
    for i in range(0, N, MICRO):
        xb = x[i:i + MICRO]
        if dtype is None:
            logits = m(input_ids=xb[:, :SEQ]).logits
        else:
            with torch.autocast("cuda", dtype=dtype):
                logits = m(input_ids=xb[:, :SEQ]).logits

        def hook(g):
            rec["abs_logit_grad"].append(float(g.float().abs().mean())); rec["logit_grad_zero_frac"].append(float((g == 0).float().mean()))
        logits.register_hook(hook)
        loss = torch.nn.functional.cross_entropy(logits.float().reshape(-1, logits.size(-1)), xb[:, 1:].reshape(-1))
        (loss * micro_scale).backward()
    g = torch.cat([p.grad.double().flatten() / unscale for p in m.parameters() if p.grad is not None])
    return g, {k: float(np.mean(v)) for k, v in rec.items()}


def main():
    raw = read_bytes(128 * 1024 * SAMPLE_BYTES, N * SAMPLE_BYTES)
    x = torch.from_numpy(np.frombuffer(raw, dtype=np.uint16).reshape(N, 2049).astype(np.int64)).to(DEV)
    m = model_at(128)
    nm = N // MICRO
    with torch.no_grad():                                   # mean |softmax - onehot| for the per-token factor
        so = []
        for i in range(0, N, MICRO):
            xb = x[i:i + MICRO]; lg = m(input_ids=xb[:, :SEQ]).logits.float()
            p = torch.softmax(lg, -1); p.scatter_add_(-1, xb[:, 1:].unsqueeze(-1), -torch.ones_like(xb[:, 1:], dtype=p.dtype).unsqueeze(-1))
            so.append(float(p.abs().mean())); del lg, p
        mean_so = float(np.mean(so))
    ntok = MICRO * SEQ
    G_ref, _ = grads(m, x, None, 1.0, nm)
    cases = {"cur": (torch.float16, SCALE * MICRO / 1024, SCALE * MICRO / 1024 * nm),
             "fix": (torch.float16, SCALE * MICRO / 32, SCALE * MICRO / 32 * nm),
             "bf16": (torch.bfloat16, 1.0, nm)}
    out = {"doc": __doc__, "pythia_per_token_factor_derived": SCALE / (32 * SEQ), "mean_abs_softmax_minus_onehot": mean_so}
    nz = G_ref != 0
    for name, (dt, ms, us) in cases.items():
        G, rec = grads(m, x, dt, ms, us)
        out[name] = {"rel_err": float((G - G_ref).norm() / G_ref.norm()),
                     "cosine": float((G @ G_ref) / (G.norm() * G_ref.norm())),
                     "zero_where_ref_nonzero": float(((G == 0) & nz).double().sum() / nz.double().sum()),
                     "per_micro_scale": ms, "per_token_factor_derived": ms / ntok,
                     "per_token_factor_measured": rec["abs_logit_grad"] / mean_so,
                     "logit_grad_zero_frac": rec["logit_grad_zero_frac"]}
        print(name, {k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in out[name].items()}, flush=True)
    c, f, b = out["cur"]["rel_err"], out["fix"]["rel_err"], out["bf16"]["rel_err"]
    out["CONFIRMED"] = bool(c > 2 * f and f <= 2 * b)
    out["measured_ratio_fix_over_cur"] = out["fix"]["per_token_factor_measured"] / out["cur"]["per_token_factor_measured"]
    (ROOT / "results" / "armb_grad_underflow.json").write_text(json.dumps(out, indent=1))
    print("CONFIRMED:", out["CONFIRMED"], "| measured per-token factor fix/cur:", round(out["measured_ratio_fix_over_cur"], 3),
          "| fix measured", round(out["fix"]["per_token_factor_measured"], 5), "vs Pythia derived", out["pythia_per_token_factor_derived"])


if __name__ == "__main__":
    main()
