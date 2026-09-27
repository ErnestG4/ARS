"""Arm B, Stage B0 (ARMB brief v0 §3): throughput / VRAM / wall-clock / disk benchmark. REPORT AND STOP -- Will picks
model size, stop step and arm set from this.

Per candidate size (Pythia-31M / 70M / 160M, unmodified HF GPTNeoX configs = Pythia's released yml: small numbers only
differ in width/depth; lr 1e-3/1e-3/6e-4):
  - fp32 master weights on GPU, bf16 autocast (brief §2 precision), sdpa attention, random tokens (throughput only).
  - micro-batch sweep (x 2048 tokens) for forward+backward; activation checkpointing only if a micro-batch OOMs without it.
  - one FULL optimizer step at the best micro-batch = 1024 sequences by gradient accumulation (Pythia's batch), with
    grad-clip 1.0 and fused AdamW(betas 0.9/0.95, eps 1e-8, wd 0.1), timed end to end.
  - Muon step overhead: Newton-Schulz-5 orthogonalisation (Keller Jordan reference coefficients, bf16) of every 2D hidden
    matrix, timed separately (the update rule itself is Will's call at B1; only its cost is measured here).
  - fp32 state_dict size, and save time to WSL ext4 (scratch file, deleted). D: is NOT written (disk is Will's call).
Data feed: HTTP-range read rate of shard 0 of EleutherAI/pile-standard-pythia-preshuffled (4.2 MB per step needed).
GPU only: hard-asserts CUDA and logs the device; never falls back. Output: results/armb_b0_bench.json.
"""
import json, os, sys, time
from pathlib import Path
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import remote_st as RS  # noqa: E402

assert torch.cuda.is_available(), "Arm B is GPU-only: CUDA not available"
DEV = torch.device("cuda")
torch.cuda.set_per_process_memory_fraction(0.80)          # leave room for Will's desktop use of the card
SEQ, BATCH = 2048, 1024
SIZES = {"pythia-31m": 1e-3, "pythia-70m": 1e-3, "pythia-160m": 6e-4}
OUT = ROOT / "results" / "armb_b0_bench.json"
SCRATCH = Path(os.environ.get("ARMB_SCRATCH", "/tmp"))


def sync_time(fn, n):
    torch.cuda.synchronize(); t = time.time()
    for _ in range(n):
        fn()
    torch.cuda.synchronize(); return (time.time() - t) / n


def build(name, ckpt=False):
    from transformers import AutoConfig, GPTNeoXForCausalLM
    cfg = AutoConfig.from_pretrained("EleutherAI/" + name); cfg._attn_implementation = "sdpa"
    m = GPTNeoXForCausalLM(cfg).to(DEV)
    if ckpt:
        m.gradient_checkpointing_enable()
    m.train(); return m, cfg


def fwd_bwd(m, mb, vocab):
    x = torch.randint(0, vocab, (mb, SEQ), device=DEV)
    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss = m(input_ids=x, labels=x).loss
    loss.backward()


def ns5(G, steps=5):
    a, b, c = 3.4445, -4.7750, 2.0315
    X = G.bfloat16(); X = X / (X.norm() + 1e-7)
    tr = X.size(0) > X.size(1)
    if tr:
        X = X.T
    for _ in range(steps):
        A = X @ X.T; B = b * A + c * A @ A; X = a * X + B @ X
    return X.T if tr else X


def bench_size(name, lr):
    rec = {"lr_peak_from_yml": lr}
    best = None
    for mb in (4, 8, 16, 32, 64):
        fitted = False
        for use_ckpt in (False, True):
            try:
                torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
                m, cfg = build(name, use_ckpt)
                fwd_bwd(m, mb, cfg.vocab_size); m.zero_grad(set_to_none=True)
                t = sync_time(lambda: fwd_bwd(m, mb, cfg.vocab_size), 3)
                peak = torch.cuda.max_memory_allocated() / 2**30
                tps = mb * SEQ / t
                rec[f"mb{mb}{'_ckpt' if use_ckpt else ''}"] = {"s_per_micro": t, "tokens_per_s": tps, "peak_GiB": peak}
                print(f"{name} mb {mb} ckpt {use_ckpt}: {tps:,.0f} tok/s, peak {peak:.1f} GiB", flush=True)
                if best is None or tps > best[1]:
                    best = (mb, tps, use_ckpt)
                del m; fitted = True; break
            except torch.OutOfMemoryError:
                print(f"{name} mb {mb} ckpt {use_ckpt}: OOM", flush=True)
                m = None; torch.cuda.empty_cache()
        RS.check_stop()
        if not fitted:
            break
    # full step: the fastest micro-batch that still fits once optimizer state is resident (fall back downward)
    order = sorted({int(k[2:].split("_")[0]) for k in rec if k.startswith("mb")}, key=lambda b: -rec.get(f"mb{b}", {"tokens_per_s": 0})["tokens_per_s"])
    for mb in order:
        try:
            torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
            m, cfg = build(name, False)
            n_params = sum(p.numel() for p in m.parameters())
            opt = torch.optim.AdamW(m.parameters(), lr=lr, betas=(0.9, 0.95), eps=1e-8, weight_decay=0.1, fused=True)

            def full_step():
                for _ in range(BATCH // mb):
                    fwd_bwd(m, mb, cfg.vocab_size)
                torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step(); opt.zero_grad(set_to_none=True)
            full_step()                                          # warm (allocates optimizer state)
            t_step = sync_time(full_step, 1); use_ckpt = False
            break
        except torch.OutOfMemoryError:
            print(f"{name} full step mb {mb}: OOM, falling back", flush=True)
            m = opt = None; torch.cuda.empty_cache()
    if name == "pythia-70m":                                     # engineering option: torch.compile (maths unchanged)
        mc = torch.compile(m)
        fwd_bwd(mc, mb, cfg.vocab_size); m.zero_grad(set_to_none=True)
        fwd_bwd(mc, mb, cfg.vocab_size); m.zero_grad(set_to_none=True)
        tc = sync_time(lambda: fwd_bwd(mc, mb, cfg.vocab_size), 5); m.zero_grad(set_to_none=True)
        rec["compiled_tokens_per_s_mb"] = [mb * SEQ / tc, mb]
        print(f"{name} compiled mb {mb}: {mb * SEQ / tc:,.0f} tok/s", flush=True)
    peak_full = torch.cuda.max_memory_allocated() / 2**30
    hidden2d = [p for n, p in m.named_parameters() if p.ndim == 2 and "embed" not in n]
    t_muon = sync_time(lambda: [ns5(p.data) for p in hidden2d], 5)
    sd = {k: v.detach().float().cpu() for k, v in m.state_dict().items()}
    fp = SCRATCH / f"armb_b0_{name}.pt"
    t0 = time.time(); torch.save(sd, fp); os.sync(); t_save = time.time() - t0
    size_mb = fp.stat().st_size / 1e6; fp.unlink()
    rec.update({"n_params": n_params, "best_micro_batch": mb, "activation_ckpt": use_ckpt,
                "s_per_full_step_adamw": t_step, "peak_GiB_full_step": peak_full,
                "s_muon_ns5_overhead_per_step": t_muon, "n_hidden_2d": len(hidden2d),
                "ckpt_fp32_MB": size_mb, "adam_state_MB": 2 * size_mb, "ckpt_save_s_ext4": t_save})
    print(name, json.dumps({k: v for k, v in rec.items() if not k.startswith("mb")}), flush=True)
    del m, opt; torch.cuda.empty_cache()
    return rec


def data_feed():
    import requests
    url = "https://huggingface.co/datasets/EleutherAI/pile-standard-pythia-preshuffled/resolve/main/document-00000-of-00020.bin"
    s = requests.Session(); step_bytes = BATCH * 2049 * 2; n = 5; t = time.time(); got = 0
    for i in range(n):
        lo = i * step_bytes
        r = s.get(url, headers={"Range": f"bytes={lo}-{lo + step_bytes - 1}"}, timeout=120); r.raise_for_status()
        got += len(r.content)
    return {"MB_per_s": got / 1e6 / (time.time() - t), "bytes_per_step": step_bytes, "steps_read": n}


def main():
    out = json.loads(OUT.read_text()) if OUT.exists() else {}
    out["device"] = torch.cuda.get_device_name(0); out["torch"] = torch.__version__
    print("device:", out["device"], flush=True)
    for name, lr in SIZES.items():
        if name not in out:
            out[name] = bench_size(name, lr); OUT.write_text(json.dumps(out, indent=1))
    if "data_feed" not in out:
        out["data_feed"] = data_feed(); OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps(out["data_feed"]))


if __name__ == "__main__":
    try:
        main()
    except RS.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
