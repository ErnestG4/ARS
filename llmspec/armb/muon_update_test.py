"""SEALED pre-launch Muon update test (ARMB_PREREG.md amendment B1a-A6 §2; criterion committed at 7d1f1e9 BEFORE this
script existed). No training. GPU (the real CUDA fp16 path), VRAM-capped so it can share the card with a running arm.

pythia-70m step128 weights; two consecutive optimizer steps on the first 64 sequences of update 129's and update 130's
batches; lr 1e-3, wd 0.1; loss scale 4096 then 8192 (exercises unscale consistency across a scale change).
Variants (all clip the global grad norm to 1.0 before the optimizer, as the trainer does):
  REF       fp32 grads (no autocast), MuonHybrid with fp32 NS
  PATH      the trainer's path: fp16 autocast, micro-batches of 8 with loss x scale x 8/32 (Pythia-matched per-token
            factor), non-finite check, unscale by scale x 64/32, clip; MuonHybrid with bf16 NS, fp32 momentum
  PATH_ns32 PATH with fp32 NS
  REF_ns16  REF grads with bf16 NS
  RED       PATH with the fused QKV orthogonalised as ONE 1536 x 512 matrix (split_qkv=False)
Compared: the parameter change after step 2 per type (Q, K, V, O, MLP_IN, MLP_OUT over all layers): rel_err, cosine vs REF.
Criteria and decision: see the amendment (copied into the output). Output: results/armb_muon_update_test.json.
"""
import json, sys
from pathlib import Path
import numpy as np, torch

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import train as TR  # noqa: E402  (DynamicLossScaler, data reader, constants)
from muon import MuonHybrid, MUON_VERSION  # noqa: E402
torch.cuda.set_per_process_memory_fraction(0.40)
DEV = "cuda"; H, DH, D = 8, 64, 512; N, MICRO, SEQ = 64, 4, 2048   # MICRO 4 (not the trainer's 8): VRAM cap while A0 trains; per-token factor unchanged (loss x scale x MICRO/32); per-micro fp16 param-grad sums are half the trainer's = a HARDER underflow condition


def weights():
    from safetensors.torch import load_file
    tmp = HERE / "_p70m_step128.safetensors"
    with TR.RS.requests.get("https://huggingface.co/EleutherAI/pythia-70m/resolve/step128/model.safetensors", stream=True, timeout=300) as r, open(tmp, "wb") as f:
        r.raise_for_status()
        for c in r.iter_content(1 << 22):
            f.write(c)
    sd = {k: v.float() for k, v in load_file(str(tmp)).items()}; tmp.unlink(); return sd


def fresh(sd):
    from transformers import AutoConfig, GPTNeoXForCausalLM
    cfg = AutoConfig.from_pretrained("EleutherAI/pythia-70m"); cfg._attn_implementation = "sdpa"
    m = GPTNeoXForCausalLM(cfg); m.load_state_dict(sd, strict=False); return m.to(DEV).train()


def batch(update_k):
    raw = TR.read_bytes((update_k - 1) * 1024 * TR.SAMPLE_BYTES, N * TR.SAMPLE_BYTES)
    return torch.from_numpy(np.frombuffer(raw, dtype=np.uint16).reshape(N, 2049).astype(np.int64)).to(DEV)


def grads_ref(m, x):
    for i in range(0, N, MICRO):
        xb = x[i:i + MICRO]; lg = m(input_ids=xb[:, :SEQ]).logits
        (torch.nn.functional.cross_entropy(lg.float().reshape(-1, lg.size(-1)), xb[:, 1:].reshape(-1)) * (MICRO / N)).backward()
    return True


def grads_path(m, x, scale):
    for i in range(0, N, MICRO):
        xb = x[i:i + MICRO]
        with torch.autocast("cuda", dtype=torch.float16):
            lg = m(input_ids=xb[:, :SEQ]).logits
        (torch.nn.functional.cross_entropy(lg.float().reshape(-1, lg.size(-1)), xb[:, 1:].reshape(-1)) * (scale * MICRO / TR.PYTHIA_MICRO)).backward()
    gs = [p.grad for p in m.parameters() if p.grad is not None]
    ok = not bool(torch.stack([torch.logical_not(torch.isfinite(g).all()) for g in gs]).any())
    if ok:
        for g in gs:
            g.div_(scale * N / TR.PYTHIA_MICRO)
    return ok


def run(sd, xs, path, ns_dtype, split=True):
    m = fresh(sd); opt = MuonHybrid(m, H, DH, ns_dtype=ns_dtype, split_qkv=split)
    w0 = {n: p.detach().clone() for n, p in m.named_parameters() if n.endswith(TR.TYPES["Q_K_V"]) or n.endswith(("attention.dense.weight", "mlp.dense_h_to_4h.weight", "mlp.dense_4h_to_h.weight"))}
    for x, scale in zip(xs, (4096.0, 8192.0)):
        ok = grads_path(m, x, scale) if path else grads_ref(m, x)
        assert ok, "overflow in the test batch (unexpected at this scale)"
        torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step(1e-3); opt.zero_grad()
    out = {"Q": [], "K": [], "V": [], "O": [], "MLP_IN": [], "MLP_OUT": []}
    for n, p in m.named_parameters():
        if n not in w0:
            continue
        d = (p.detach() - w0[n]).double()
        if n.endswith("attention.query_key_value.weight"):
            dv = d.view(H, 3, DH, D)
            for j, t in enumerate("QKV"):
                out[t].append(dv[:, j].flatten())
        else:
            t = "O" if n.endswith("attention.dense.weight") else ("MLP_IN" if "h_to_4h" in n else "MLP_OUT")
            out[t].append(d.flatten())
    del m, opt; torch.cuda.empty_cache()
    return {t: torch.cat(v) for t, v in out.items()}


def cmp(a, ref):
    return {t: {"rel_err": float((a[t] - ref[t]).norm() / ref[t].norm()),
                "cosine": float(a[t] @ ref[t] / (a[t].norm() * ref[t].norm()))} for t in ref}


def main():
    sd = weights(); xs = [batch(129), batch(130)]
    ref = run(sd, xs, False, torch.float32)
    res = {"doc": __doc__, "muon_version": MUON_VERSION, "micro_batch": MICRO, "micro_batch_note": "4 instead of the trainer 8 (VRAM cap while A0 trains); per-token factor identical; harder underflow condition",
           "PATH": cmp(run(sd, xs, True, torch.bfloat16), ref),
           "PATH_ns32": cmp(run(sd, xs, True, torch.float32), ref),
           "REF_ns16": cmp(run(sd, xs, False, torch.bfloat16), ref),
           "RED_fused_qkv": cmp(run(sd, xs, True, torch.bfloat16, split=False), ref)}
    T = list(ref)
    i_ = all(res["PATH_ns32"][t]["rel_err"] <= 0.01 and res["PATH_ns32"][t]["cosine"] >= 0.9999 for t in T)
    ii = all(res["PATH"][t]["cosine"] >= 0.995 and res["PATH"][t]["rel_err"] <= 0.1
             and abs(res["PATH"][t]["rel_err"] - res["REF_ns16"][t]["rel_err"]) <= 0.01 for t in T)
    iii = all(res["RED_fused_qkv"][t]["rel_err"] > 0.1 for t in "QKV")
    res["criteria"] = {"i_plumbing": i_, "ii_bf16_ns": ii, "iii_red_fires": iii}
    res["DECISION"] = ("PASS: NS bf16" if (i_ and ii and iii) else "PASS: NS fp32" if (i_ and iii) else "BLOCKED")
    (ROOT / "results" / "armb_muon_update_test.json").write_text(json.dumps(res, indent=1))
    for k in ("PATH", "PATH_ns32", "REF_ns16", "RED_fused_qkv"):
        print(k, {t: (round(v["rel_err"], 5), round(v["cosine"], 6)) for t, v in res[k].items()})
    print("criteria", res["criteria"], "->", res["DECISION"])


if __name__ == "__main__":
    main()
