"""Seed-1 identity check (ARMB_PREREG.md amendment B1a-A9; this file is SEALED with it, before it runs).

Question: are the rebuilt seed-1 batches (armb/seed_order.py; spot ~/llmspec_armb/data/seed1_batches, B1a-A7) the
batches PolyPythias `pythia-70m-seed1` actually trained on? The seed0 known-answer check validated the METHOD; this
checks the seed-1 OUTPUT. If it fails, Q4's second pair (M0-s2 vs released seed1) falls.

Runs: 128 AdamW steps each, A0's exact configuration and update code (armb/train.py: build, param_groups,
DynamicLossScaler, lr_at, W = 1430, fp16 autocast, Pythia per-token loss scaling, clip 1.0, TF32 off, micro 8). No
checkpoints are uploaded; weights stay in memory.
  K   init pythia-70m        data standard order (PileOrder)            vs released pythia-70m        known answer
  Km  init pythia-70m        data seed-1 order                          vs released pythia-70m        known WRONG data
  T   init pythia-70m-seed1  data seed-1 order                          vs released pythia-70m-seed1  the test
  C1  init pythia-70m-seed1  data standard order                        vs released pythia-70m-seed1  confuser
  C2  init pythia-70m-seed1  data seed-1 order shifted +1 (k+1 at k)    vs released pythia-70m-seed1  off-by-one confuser
Statistic, at t in {16, 32, 64, 128}: rho(t) = Pearson correlation over every entry of the four weight types in all 6
  layers (fused QKV, attention.dense, h_to_4h, 4h_to_h) between D_ours = fp16(W_ours(t)) - W_rel(0) and
  D_rel = W_rel(t) - W_rel(0) (released fp16 weights; W_ours(0) == W_rel(0) is asserted).
  (Per-step changes at t <= 16 are near fp16 resolution: lr(1) ~ 7e-7 vs a spacing ~1.5e-5 at |w| ~ 0.02, hence t <= 128.)
Verdict (SEALED):
  m(t) = (rho_K(t) + rho_Km(t)) / 2, the right/wrong midpoint from the known-answer system.
  INSTRUMENT: requires rho_K(t) > rho_Km(t) at all four t; otherwise the verdict is INCONCLUSIVE (instrument does not
    separate right from wrong data) and no identity claim is made either way.
  A run is RIGHT-LIKE at t iff rho(t) >= m(t), else WRONG-LIKE.
  CONFIRMED  iff instrument holds, T is right-like at all four t, AND C1 and C2 are wrong-like at all four t
             (the confusers are the red path: the rule must reject them).
  REFUTED    iff instrument holds and T is wrong-like at all four t (reported with which confuser, if any, is right-like).
  INCONCLUSIVE otherwise.
Descriptive (no verdict): per-type rho, relative distance ||D_ours - D_rel|| / ||D_rel||, the loss trajectories.
Data integrity: seed-1 batches 1..129 are copied from spot once and each is sha256-verified against the generator's
  steps.jsonl record (fail closed); standard batches stream by HTTP range as in training.
Output: results/armb_seed1_identity.json.  Usage: seed1_identity.py [fetch|run|all]
"""
import hashlib, io, json, os, subprocess, sys, time
from pathlib import Path
import numpy as np
import torch

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import train as TR  # noqa: E402  (asserts CUDA; A0's model / optimizer / scaler / schedule definitions)
import remote_st as RS  # noqa: E402

OUT = Path(os.environ.get("S1ID_OUT", str(ROOT / "results" / "armb_seed1_identity.json")))  # override: tests only
CACHE = HERE / "_seed1_cache"
STEPS, CHECK = 128, (16, 32, 64, 128)
W = TR.ARMS["A0"][0]
RUNS = {"K": ("EleutherAI/pythia-70m", "std", 0), "Km": ("EleutherAI/pythia-70m", "seed1", 0),
        "T": ("EleutherAI/pythia-70m-seed1", "seed1", 0), "C1": ("EleutherAI/pythia-70m-seed1", "std", 0),
        "C2": ("EleutherAI/pythia-70m-seed1", "seed1", 1)}
TYPES = list(TR.TYPES.values())


def fetch():
    CACHE.mkdir(exist_ok=True)
    recs = subprocess.run(["ssh", "-o", "BatchMode=yes", TR.SPOT, f"cat {TR.SEED1_DIR}/steps.jsonl"],
                          capture_output=True, text=True, check=True).stdout
    rec = {}
    for ln in recs.splitlines():
        if ln.strip():
            r = json.loads(ln); rec[r["step"]] = r
    for k in range(1, STEPS + 2):
        fp = CACHE / f"step{k:05d}.npy"; r = rec[k]
        if fp.exists() and hashlib.sha256(fp.read_bytes()).hexdigest() == r["sha256"]:
            continue
        raw = subprocess.run(["ssh", "-o", "BatchMode=yes", TR.SPOT, f"cat {TR.SEED1_DIR}/{r['file']}"],
                             capture_output=True, check=True).stdout
        assert hashlib.sha256(raw).hexdigest() == r["sha256"], f"seed-1 batch {k}: sha256 mismatch"
        RS.durable_save(fp, lambda p: p.write_bytes(raw))
    print("seed-1 batches 1..%d cached and verified" % (STEPS + 1), flush=True)


def seed1_batch(k):
    raw = (CACHE / f"step{k:05d}.npy").read_bytes(); arr = np.load(io.BytesIO(raw))
    assert arr.shape == (TR.BATCH, 2049) and arr.dtype == np.uint16
    return arr, hashlib.sha256(arr.tobytes()).hexdigest()


def load_release(repo, t):
    for fn in ("model.safetensors", "pytorch_model.bin"):
        url = f"https://huggingface.co/{repo}/resolve/step{t}/{fn}"
        if RS.requests.head(url, allow_redirects=True, timeout=60).status_code != 200:
            continue
        tmp = HERE / f"_rel_{repo.split('/')[1]}_{t}_{fn}"
        for i in range(8):
            try:
                with RS.requests.get(url, stream=True, timeout=300) as r, open(tmp, "wb") as f:
                    r.raise_for_status()
                    for c in r.iter_content(1 << 22):
                        f.write(c)
                break
            except Exception as e:  # noqa: BLE001
                print("release fetch retry", repo, t, e, flush=True); time.sleep(20 * (i + 1))
        if fn.endswith(".safetensors"):
            from safetensors.torch import load_file
            sd = load_file(str(tmp))
        else:
            sd = torch.load(str(tmp), map_location="cpu", weights_only=True)
        tmp.unlink()
        return {k: v for k, v in sd.items() if any(k.endswith(s) for s in TYPES)}
    raise RuntimeError(f"no weights for {repo} step{t}")


def flat(sd, keys):
    return torch.cat([sd[k].float().reshape(-1) for k in keys])


def train_run(name):
    init, data, shift = RUNS[name]
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    model = TR.build(init)
    opt = torch.optim.AdamW(TR.param_groups(model), lr=0.0, betas=(0.9, 0.95), eps=1e-8, fused=True)
    scaler = TR.DynamicLossScaler(); n_applied = n_skipped = 0; losses = []; snaps = {}

    def micro_loss(xb):
        with torch.autocast("cuda", dtype=torch.float16):
            logits = model(input_ids=xb[:, :TR.SEQ]).logits
        return torch.nn.functional.cross_entropy(logits.float().reshape(-1, logits.size(-1)), xb[:, 1:].reshape(-1))
    cmicro = torch.compile(micro_loss)
    names = [n for n, _ in model.named_parameters() if any(n.endswith(s) for s in TYPES)]
    snaps[0] = {n: p.detach().half().float().cpu() for n, p in model.named_parameters() if n in names}
    std = TR.PileOrder(1, STEPS) if data == "std" else None
    for k in range(1, STEPS + 1):
        RS.check_stop()
        lr = TR.lr_at(n_applied, W)
        for gp in opt.param_groups:
            gp["lr"] = lr
        arr, bh = std.next() if std else seed1_batch(k + shift)
        x = torch.from_numpy(arr.astype(np.int64)).to(TR.DEV)
        tot = torch.zeros((), device=TR.DEV); scale = scaler.cur_scale
        for i in range(0, TR.BATCH, TR.MICRO):
            loss = cmicro(x[i:i + TR.MICRO])
            (loss * (scale * TR.MICRO / TR.PYTHIA_MICRO)).backward(); tot += loss.detach() * (TR.MICRO / TR.BATCH)
        grads = [p.grad for p in model.parameters() if p.grad is not None]
        overflow = bool(torch.stack([torch.logical_not(torch.isfinite(g).all()) for g in grads]).any())
        if overflow:
            n_skipped += 1; opt.zero_grad(set_to_none=True)
        else:
            for g in grads:
                g.div_(scale * TR.BATCH / TR.PYTHIA_MICRO)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); opt.zero_grad(set_to_none=True); n_applied += 1
        scaler.update_scale(overflow); losses.append(float(tot))
        if k in CHECK:
            snaps[k] = {n: p.detach().half().float().cpu() for n, p in model.named_parameters() if n in names}
        if k % 16 == 0:
            print(f"{name} step {k} loss {float(tot):.4f} lr {lr:.3e} scale {scale:g} skipped {n_skipped}", flush=True)
    del model, opt; torch.cuda.empty_cache()
    return snaps, losses, n_skipped, names


def decide(rho):
    """The sealed verdict rule (docstring). rho: {run: {t: value}} for the five runs at the four CHECK steps."""
    m = {t: (rho["K"][t] + rho["Km"][t]) / 2 for t in CHECK}
    inst = all(rho["K"][t] > rho["Km"][t] for t in CHECK)
    right = {n: [rho[n][t] >= m[t] for t in CHECK] for n in ("T", "C1", "C2")}
    if not inst:
        v = "INCONCLUSIVE (instrument does not separate right from wrong data on the known-answer system)"
    elif all(right["T"]) and not any(right["C1"]) and not any(right["C2"]):
        v = "CONFIRMED"
    elif not any(right["T"]):
        v = "REFUTED" + f" (right-like confuser: {[c for c in ('C1', 'C2') if all(right[c])]})"
    else:
        v = "INCONCLUSIVE"
    return {"midpoint": m, "instrument_holds": inst, "right_like": right, "VERDICT": v}


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("fetch", "all"):
        fetch()
    if which == "fetch":
        return
    res = json.loads(OUT.read_text()) if OUT.exists() else {"doc": __doc__, "runs": {}}
    rel = {}
    if any(n not in res["runs"] for n in RUNS):
        for repo in ("EleutherAI/pythia-70m", "EleutherAI/pythia-70m-seed1"):
            rel[repo] = {t: load_release(repo, t) for t in (0,) + CHECK}
    for name in RUNS:
        if name in res["runs"]:
            continue
        t0 = time.time(); snaps, losses, nsk, names = train_run(name); R = rel[RUNS[name][0]]
        keys = [n for n in names]; rk = {n: next(k for k in R[0] if k.endswith(n.split("gpt_neox.")[-1])) for n in keys}
        base_o = flat(snaps[0], keys); base_r = flat({n: R[0][rk[n]] for n in keys}, keys)
        assert torch.equal(base_o, base_r), f"{name}: our step0 != released step0"
        rec = {"rho": {}, "rel_dist": {}, "rho_type": {}, "losses": losses, "n_skipped": nsk}
        for t in CHECK:
            Do = flat(snaps[t], keys) - base_o; Dr = flat({n: R[t][rk[n]] for n in keys}, keys) - base_r
            rec["rho"][t] = float(torch.corrcoef(torch.stack([Do, Dr]))[0, 1])
            rec["rel_dist"][t] = float((Do - Dr).norm() / Dr.norm())
            rec["rho_type"][t] = {}
            for s in TYPES:
                ks = [n for n in keys if n.endswith(s)]
                a = flat(snaps[t], ks) - flat(snaps[0], ks); b = flat({n: R[t][rk[n]] for n in ks}, ks) - flat({n: R[0][rk[n]] for n in ks}, ks)
                rec["rho_type"][t][s] = float(torch.corrcoef(torch.stack([a, b]))[0, 1])
        res["runs"][name] = rec
        RS.durable_save(OUT, lambda p: p.write_text(json.dumps(res, indent=1)))
        print(name, {t: round(v, 4) for t, v in rec["rho"].items()}, f"({time.time()-t0:.0f}s)", flush=True)
    rho = {n: {int(t): v for t, v in res["runs"][n]["rho"].items()} for n in RUNS}
    res["verdict"] = decide(rho)
    RS.durable_save(OUT, lambda p: p.write_text(json.dumps(res, indent=1)))
    print("VERDICT:", res["verdict"]["VERDICT"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except RS.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
