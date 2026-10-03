"""Divisor Harmonics v0 -- GPU extraction (brief §5.1). Residual stream (resid_post of every block, plus the embedding
output as 'layer 0' of the hidden-state stack) at the item tokens, for every concept x template x item of templates.py.

Stored per model/checkpoint, fp32:  results/divisor/acts/<tag>.npz with, per concept c,
    <c>_last  : (L+1, T, N, d)  hidden state at the LAST item token  (PRIMARY read, brief §3)
    <c>_first : (L+1, T, N, d)  hidden state at the FIRST item token (only when any item is multi-token; descriptive)
plus 'layers' (L), 'd', 'model', 'revision_or_ckpt', 'prompt_sha256' (sha256 over the frozen prompt list).
GPU-only hard assert. Right padding (causal LM: later pad tokens cannot touch earlier positions); positions gathered.

Usage:  python3 divisor_extract.py --model EleutherAI/pythia-1.4b --revision step143000 --tag pythia-1.4b
        python3 divisor_extract.py --ckpt ~/llmspec_div/A0/step01000.pt --tag A0_step01000   (GPTNeoX pythia-70m config)
"""
import argparse, hashlib, json, pathlib, sys, time
import numpy as np, torch
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import templates as T

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="EleutherAI/pythia-70m"); ap.add_argument("--revision", default="step143000")
    ap.add_argument("--ckpt", default=None, help="Arm B state_dict (.pt); model = GPTNeoX with the pythia-70m config")
    ap.add_argument("--tag", required=True); ap.add_argument("--out", default="results/divisor/acts")
    ap.add_argument("--batch", type=int, default=50)
    a = ap.parse_args()
    assert torch.cuda.is_available(), "GPU-only (brief): refusing to run on CPU"
    dev = torch.device("cuda")
    from transformers import AutoTokenizer, AutoConfig, GPTNeoXForCausalLM
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m")      # one tokenizer for every Pythia size and Arm B
    if a.ckpt:
        cfg = AutoConfig.from_pretrained("EleutherAI/pythia-70m"); cfg._attn_implementation = "eager"
        model = GPTNeoXForCausalLM(cfg)
        sd = torch.load(a.ckpt, map_location="cpu", weights_only=True)
        missing, unexpected = model.load_state_dict(sd, strict=False)
        assert not unexpected and all(k.endswith(("rotary_emb.inv_freq", "masked_bias", "bias")) or "rotary" in k
                                      for k in missing), (missing[:5], unexpected[:5])
        src = str(a.ckpt)
    else:
        model = GPTNeoXForCausalLM.from_pretrained(a.model, revision=a.revision, torch_dtype=torch.float32,
                                                   attn_implementation="eager")
        src = f"{a.model}@{a.revision}"
    model = model.to(dev).eval()
    L, d = model.config.num_hidden_layers, model.config.hidden_size
    out = {"layers": np.int64(L), "d": np.int64(d), "model": np.array(src), "tag": np.array(a.tag)}
    allp = []
    t0 = time.time()
    for name, (items, tps, N, bc, role) in T.CONCEPTS.items():
        P = T.prompts(name); allp += [p for row in P for p in row]
        multi = False
        X_last = np.zeros((L + 1, len(tps), N, d), np.float32); X_first = np.zeros_like(X_last)
        for ti, t in enumerate(tps):
            pre_len = len(tok.encode(t[:-2].rstrip()))
            ids = [tok.encode(p) for p in P[ti]]
            for i in ids: assert len(i) > pre_len, (name, t)
            if any(len(i) - pre_len > 1 for i in ids): multi = True
            for b0 in range(0, N, a.batch):
                chunk = ids[b0:b0 + a.batch]; ml = max(len(i) for i in chunk)
                inp = torch.zeros((len(chunk), ml), dtype=torch.long); att = torch.zeros_like(inp)
                for j, i in enumerate(chunk): inp[j, :len(i)] = torch.tensor(i); att[j, :len(i)] = 1
                with torch.no_grad():
                    hs = model(input_ids=inp.to(dev), attention_mask=att.to(dev), output_hidden_states=True).hidden_states
                H = torch.stack(hs, 0).float().cpu().numpy()          # (L+1, B, ml, d)
                for j, i in enumerate(chunk):
                    X_last[:, ti, b0 + j] = H[:, j, len(i) - 1]; X_first[:, ti, b0 + j] = H[:, j, pre_len]
        out[f"{name}_last"] = X_last
        if multi: out[f"{name}_first"] = X_first
        print(f"{a.tag}: {name:9s} N={N:3d} T={len(tps)} L={L} d={d} multi_token={multi}  {time.time()-t0:.0f}s", flush=True)
    out["prompt_sha256"] = np.array(hashlib.sha256("\n".join(allp).encode()).hexdigest())
    pathlib.Path(a.out).mkdir(parents=True, exist_ok=True)
    fp = pathlib.Path(a.out) / f"{a.tag}.npz"
    np.savez(fp, **out)
    man = pathlib.Path(a.out) / "manifest.jsonl"
    with open(man, "a") as f:
        f.write(json.dumps({"tag": a.tag, "src": src, "file": str(fp), "bytes": fp.stat().st_size,
                            "sha256": hashlib.sha256(fp.read_bytes()).hexdigest(), "prompt_sha256": str(out["prompt_sha256"]),
                            "time": time.strftime("%Y-%m-%dT%H:%M:%S")}) + "\n")
    print(f"WROTE {fp} ({fp.stat().st_size/1e6:.0f} MB)  EXTRACT_DONE {a.tag}", flush=True)

if __name__ == "__main__":
    main()
