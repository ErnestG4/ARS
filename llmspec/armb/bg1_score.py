"""B-G1 anchor-gate scorer (armb/ARMB_PREREG.md §3; frozen with the B1a seal). Runs on spot (CPU, fp64 SVD).

Modes (all resumable; outputs under $BG1_DIR, default ~/llmspec_armb/bg1):
  probe      fetch the 64-sample loss probe from the preshuffled standard Pile (indices seeded 20260927 in
             [142000*1024, 143000*1024)), save probe.npy + sha256
  band       score the 10 reference runs (pythia-70m + PolyPythias seed1..9) at every gating + extra step -> band.jsonl
  validate   §3.5: (i) leave-one-seed-out specificity, (ii) red-path HF-default init at step 0,
             (iii) red-path step misalignment (step 2t scored as step t, t in {256, 512, 1000}) -> validate.json
  a0 <ckpt.pt> <step>   score one A0 checkpoint (fp32 state_dict, ROUNDED TO fp16 for commensurability), append a
             verdict line to bg1_verdicts.jsonl (fail-fast semantics are applied by the GPU-side runner)
Metrics per checkpoint: layer-mean stable rank ||W||_F^2/||W||_2^2 and layer-mean Frobenius norm for Q, K, V (split
from the fused QKV as reshape(H, 3, DH, D), exactly as Stage 3), O, MLP_IN, MLP_OUT; probe loss (from step 16 on).
Decision: z = (x - m)/(s sqrt(1 + 1/n)) over the n reference runs; PASS at a step iff |z| <= T(n) at every metric,
T(n) = t_{n-1} quantile at two-sided Bonferroni 0.05/164 (T(10) = 5.67, T(9) = 6.05).
"""
import hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
import requests
import torch
from scipy.stats import t as tdist

H, DH, D, NL = 8, 64, 512, 6
TYPES = ["Q", "K", "V", "O", "MLP_IN", "MLP_OUT"]
GATE_STEPS = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, 2000]
EXTRA_STEPS = [3000, 4000, 5000]
LOSS_FROM = 16
FAMILY = sum(12 + (s >= LOSS_FROM) for s in GATE_STEPS)
assert FAMILY == 164, FAMILY
REFS = ["EleutherAI/pythia-70m"] + [f"EleutherAI/pythia-70m-seed{k}" for k in range(1, 10)]
DATA = "https://huggingface.co/datasets/EleutherAI/pile-standard-pythia-preshuffled/resolve/main/"
SHARD_BYTES, SAMPLE_BYTES, N_SHARDS = 30_000_000_000, 2049 * 2, 20
PROBE_N, PROBE_SEED, PROBE_LO, PROBE_HI = 64, 20260927, 142000 * 1024, 143000 * 1024
OUT = Path(os.environ.get("BG1_DIR", str(Path.home() / "llmspec_armb" / "bg1")))
TMP = Path(os.environ.get("BG1_TMP", str(Path.home() / "tmp" / "claude")))
SES = requests.Session()


def T_crit(n):
    return float(tdist.ppf(1 - 0.05 / (2 * FAMILY), n - 1))


assert abs(T_crit(10) - 5.67) < 0.01, T_crit(10)


def metric_names(step):
    names = [f"{k}_{M}" for M in TYPES for k in ("sr", "fro")]
    return names + (["loss"] if step >= LOSS_FROM else [])


def http(url, headers=None, tries=10, stream=False):
    """GET with retries on EVERY network step (memo §4): resolve, redirect and body."""
    err = None
    for i in range(tries):
        try:
            r = SES.get(url, headers=headers or {}, timeout=300, stream=stream, allow_redirects=True)
            if r.status_code in (200, 206):
                return r
            err = f"HTTP {r.status_code}"
        except (requests.RequestException, IOError) as e:
            err = repr(e)
        time.sleep(min(2 ** i, 120))
    raise RuntimeError(f"GET {url} failed after {tries} tries: {err}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- probe
def read_bytes(lo, n):
    out = b""
    while n > 0:
        sh, off = divmod(lo, SHARD_BYTES)
        take = min(n, SHARD_BYTES - off)
        url = DATA + f"document-{sh:05d}-of-{N_SHARDS:05d}.bin"
        b = http(url, {"Range": f"bytes={off}-{off + take - 1}"}).content
        assert len(b) == take, (len(b), take)
        out += b; lo += take; n -= take
    return out


def probe_indices():
    rng = np.random.default_rng(PROBE_SEED)
    return np.sort(rng.choice(np.arange(PROBE_LO, PROBE_HI), PROBE_N, replace=False))


def make_probe():
    fp = OUT / "probe.npy"
    if fp.exists():
        return
    idx = probe_indices()
    toks = np.stack([np.frombuffer(read_bytes(int(i) * SAMPLE_BYTES, SAMPLE_BYTES), dtype=np.uint16) for i in idx])
    np.save(fp, toks)
    (OUT / "probe_meta.json").write_text(json.dumps({"indices": idx.tolist(), "sha256": sha256(fp),
                                                      "shape": list(toks.shape)}, indent=1))
    print("probe", toks.shape, sha256(fp), flush=True)


def load_probe():
    fp = OUT / "probe.npy"; meta = json.loads((OUT / "probe_meta.json").read_text())
    assert sha256(fp) == meta["sha256"], "probe sha256 mismatch"
    return torch.from_numpy(np.load(fp).astype(np.int64))


# ---------------------------------------------------------------- weights
def load_ref(repo, step):
    """fp32 state dict of a released checkpoint (fp16 storage upcast). Streams to a temp file, deletes it."""
    TMP.mkdir(parents=True, exist_ok=True)
    for fn in ("model.safetensors", "pytorch_model.bin"):
        url = f"https://huggingface.co/{repo}/resolve/step{step}/{fn}"
        try:
            head = SES.head(url, allow_redirects=True, timeout=60)
        except requests.RequestException:
            head = None
        if head is None or head.status_code != 200:
            continue
        tmp = TMP / f"bg1_{repo.split('/')[-1]}_{step}_{fn}"
        with open(tmp, "wb") as f:
            for chunk in http(url, stream=True).iter_content(1 << 22):
                f.write(chunk)
        try:
            if fn.endswith(".safetensors"):
                from safetensors.torch import load_file
                sd = load_file(str(tmp))
            else:
                sd = torch.load(str(tmp), map_location="cpu", weights_only=True)
        finally:
            tmp.unlink()
        return {k: v.float() for k, v in sd.items() if torch.is_floating_point(v)}, fn
    raise RuntimeError(f"no weights for {repo} step{step}")


def load_a0(path):
    sd = torch.load(path, map_location="cpu", weights_only=True)
    return {k: v.half().float() for k, v in sd.items() if torch.is_floating_point(v)}      # fp16 commensurability


# ---------------------------------------------------------------- metrics
def weight_metrics(sd):
    acc = {f"{k}_{M}": [] for M in TYPES for k in ("sr", "fro")}
    for L in range(NL):
        p = f"gpt_neox.layers.{L}."
        qkv = sd[p + "attention.query_key_value.weight"].double().reshape(H, 3, DH, D)
        mats = {"Q": qkv[:, 0].reshape(H * DH, D), "K": qkv[:, 1].reshape(H * DH, D), "V": qkv[:, 2].reshape(H * DH, D),
                "O": sd[p + "attention.dense.weight"].double(), "MLP_IN": sd[p + "mlp.dense_h_to_4h.weight"].double(),
                "MLP_OUT": sd[p + "mlp.dense_4h_to_h.weight"].double()}
        for M, W in mats.items():
            s = torch.linalg.svdvals(W); f2 = float((s ** 2).sum())
            acc[f"sr_{M}"].append(f2 / float(s[0]) ** 2); acc[f"fro_{M}"].append(f2 ** 0.5)
    return {k: float(np.mean(v)) for k, v in acc.items()}


def probe_loss(sd, probe):
    from transformers import AutoConfig, GPTNeoXForCausalLM
    cfg = AutoConfig.from_pretrained("EleutherAI/pythia-70m")
    m = GPTNeoXForCausalLM(cfg)
    missing, _ = m.load_state_dict(sd, strict=False)
    params = {n for n, _ in m.named_parameters()}
    assert not (set(missing) & params), f"missing parameters: {sorted(set(missing) & params)[:5]}"
    m.eval(); tot, cnt = 0.0, 0
    with torch.no_grad():
        for i in range(0, len(probe), 8):
            x = probe[i:i + 8]
            logits = m(input_ids=x[:, :-1]).logits
            ce = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), x[:, 1:].reshape(-1), reduction="sum")
            tot += float(ce); cnt += x[:, 1:].numel()
    return tot / cnt


def score(sd, step, probe):
    r = weight_metrics(sd)
    if step >= LOSS_FROM:
        r["loss"] = probe_loss(sd, probe)
    return r


# ---------------------------------------------------------------- gate
def band_rows():
    fp = OUT / "band.jsonl"
    return [json.loads(l) for l in fp.read_text().splitlines()] if fp.exists() else []


def gate_step(x, step, refs):
    """refs: list of metric dicts (the reference runs at this step). Returns (pass, worst_metric, worst_z, T, n)."""
    n = len(refs); T = T_crit(n); worst = (None, 0.0)
    for k in metric_names(step):
        v = np.array([r[k] for r in refs]); m, s = v.mean(), v.std(ddof=1)
        z = (x[k] - m) / (s * np.sqrt(1 + 1 / n))
        if abs(z) > abs(worst[1]):
            worst = (k, float(z))
    return abs(worst[1]) <= T, worst[0], worst[1], T, n


def refs_at(rows, step, exclude=None):
    return [r["metrics"] for r in rows if r["step"] == step and r["repo"] != exclude]


def do_band():
    probe = load_probe(); rows = band_rows(); have = {(r["repo"], r["step"]) for r in rows}
    for repo in REFS:
        for step in GATE_STEPS + EXTRA_STEPS:
            if (repo, step) in have:
                continue
            sd, fn = load_ref(repo, step)
            rec = {"repo": repo, "step": step, "file": fn, "metrics": score(sd, step, probe)}
            with open(OUT / "band.jsonl", "a") as f:
                f.write(json.dumps(rec) + "\n"); f.flush(); os.fsync(f.fileno())
            print(repo, step, "ok", flush=True)
    print("band sha256", sha256(OUT / "band.jsonl"), flush=True)


def do_validate():
    rows = band_rows(); probe = load_probe(); out = {"band_sha256": sha256(OUT / "band.jsonl"), "T10": T_crit(10), "T9": T_crit(9)}
    assert len({(r["repo"], r["step"]) for r in rows}) == len(REFS) * len(GATE_STEPS + EXTRA_STEPS)
    # (i) leave-one-seed-out specificity: every reference run, scored against the other 9, at every gating step
    loso = {}
    for repo in REFS:
        per = []
        for step in GATE_STEPS:
            x = next(r["metrics"] for r in rows if r["repo"] == repo and r["step"] == step)
            ok, k, z, T, n = gate_step(x, step, refs_at(rows, step, exclude=repo))
            per.append({"step": step, "pass": bool(ok), "worst": k, "z": z})
        loso[repo] = {"fails": sum(not p["pass"] for p in per), "worst": max(per, key=lambda p: abs(p["z"]))}
    out["i_loso"] = {"runs": loso, "n_runs_failing": sum(v["fails"] > 0 for v in loso.values()),
                     "PASS": all(v["fails"] == 0 for v in loso.values())}
    # (ii) red-path: HF default init (N(0, initializer_range) everywhere) at step 0 must FAIL
    from transformers import AutoConfig, GPTNeoXForCausalLM
    torch.manual_seed(0)
    bad = GPTNeoXForCausalLM(AutoConfig.from_pretrained("EleutherAI/pythia-70m"))
    sd = {k: v.detach().half().float() for k, v in bad.state_dict().items() if torch.is_floating_point(v)}
    ok, k, z, T, n = gate_step(score(sd, 0, probe), 0, refs_at(rows, 0))
    out["ii_hf_default_init"] = {"gate_pass": bool(ok), "worst": k, "z": z, "T": T, "RED_PATH_FIRES": not ok}
    # (iii) red-path: step misalignment -- run r's step 2t scored as step t against the other 9
    mis = []
    for repo in REFS:
        for t_ in (256, 512, 1000):
            x = next(r["metrics"] for r in rows if r["repo"] == repo and r["step"] == 2 * t_)
            ok, k, z, T, n = gate_step(x, t_, refs_at(rows, t_, exclude=repo))
            mis.append({"repo": repo, "t": t_, "gate_pass": bool(ok), "worst": k, "z": z})
    nf = sum(not m["gate_pass"] for m in mis)
    out["iii_step_misalignment"] = {"cases": mis, "n_fail": nf, "n": len(mis),
                                    "by_t": {t_: sum(not m["gate_pass"] for m in mis if m["t"] == t_) for t_ in (256, 512, 1000)},
                                    "RED_PATH_FIRES": nf > len(mis) / 2}
    out["GATE_LICENSED"] = bool(out["i_loso"]["PASS"] and out["ii_hf_default_init"]["RED_PATH_FIRES"]
                                and out["iii_step_misalignment"]["RED_PATH_FIRES"])
    (OUT / "validate.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk not in ("runs", "cases")})
                      for k, v in out.items()}, indent=1))


def do_a0(path, step):
    rows = band_rows(); probe = load_probe()
    x = score(load_a0(path), step, probe)
    ok, k, z, T, n = gate_step(x, step, refs_at(rows, step))
    rec = {"step": step, "pass": bool(ok), "worst": k, "z": z, "T": T, "n": n, "gating": step in GATE_STEPS,
           "metrics": x, "ckpt_sha256": sha256(path), "band_sha256": sha256(OUT / "band.jsonl"),
           "scorer_sha256": sha256(__file__), "time": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with open(OUT / "bg1_verdicts.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n"); f.flush(); os.fsync(f.fileno())
    print(json.dumps({k: rec[k] for k in ("step", "pass", "worst", "z", "T")}), flush=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    mode = sys.argv[1]
    if mode == "probe":
        make_probe()
    elif mode == "band":
        do_band()
    elif mode == "validate":
        do_validate()
    elif mode == "a0":
        do_a0(sys.argv[2], int(sys.argv[3]))
    else:
        raise SystemExit(__doc__)
