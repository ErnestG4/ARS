"""Arm B trainer (ARMB_PREREG.md B1a + amendments A1-A3; B1b sealed 766c92c). GPU only. Detached + resumable.

Usage:  python armb/train.py <arm> [--stop N] [--test]
Arms (B1a-A1/A3): A0 (W 1430, stop 3000), A1 (W 2860, stop 5000), A2 (W 715, stop 3000); all AdamW, init =
EleutherAI/pythia-70m step0, data = the standard preshuffled Pile in Pythia's order. (M0-s1 / M0-s2 need the Muon
optimizer and, for s2, the seed-1 index maps: not implemented here yet; the trainer refuses them.)

Replica (B1a §1, traced to GPT-NeoX v1.0):
  - GPTNeoXForCausalLM, unmodified pythia-70m config, sdpa, torch.compile (engineering only).
  - fp32 masters, fp16 autocast with DYNAMIC LOSS SCALING (Will 09-27: fp16 to match Pythia; amendment B1a-A4),
    ported from DeeperSpeed@eb7f5cf (the version GPT-NeoX v1.0 pins) deepspeed/runtime/fp16/loss_scaler.py
    DynamicLossScaler with Pythia's config (initial_scale_power 12, loss_scale_window 1000, hysteresis 2,
    min_loss_scale 1). On overflow the update is SKIPPED, the LR scheduler is NOT advanced, the step counter and the
    data pointer ARE (DeeperSpeed engine._take_model_step). Loss = mean token CE over 1024 x 2048 predictions (inputs
    tokens[:2048], labels tokens[1:2049]) by 128 micro-batches of 8; forward + CE inside one compiled graph.
  - AdamW(betas 0.9/0.95, eps 1e-8, wd 0.1 decoupled; NO decay on LayerNorm params or any bias); grad clip 1.0.
  - LR: GPT-NeoX AnnealingLR incl. the /E cosine quirk (q1_models.lr); the n-th APPLIED update uses lr(n-1)
    (without overflow skips this is "update k uses lr(k-1)").
  - Update k reads preshuffled samples [(k-1)*1024, k*1024).
Checkpoints (B1a §2 grid truncated at stop): full fp32 state_dict to a local staging dir, uploaded to
spot:~/llmspec_armb/ckpt/<arm>/ by a background thread, sha256-verified remotely, marked .ok there, then deleted locally.
AdamW state at {1, 10, 100, 256, 512, 1000, 1430, 2000, 3000, 5000}. Rolling resume slot every 50 steps (local).
Per-step log (jsonl): loss, lr used, pre-clip grad norm, per-type update norm ||dW||, batch sha256.
Gate B-G1 (A0 only): a puller thread reads spot:~/llmspec_armb/bg1/bg1_verdicts.jsonl every 60 s; any FAIL writes
llmspec/STOP ("B-G1 FAIL step t") and training stops. Scoring itself runs on spot (armb/bg1_daemon.sh).
Built-in replica check: the step-1 checkpoint must be BIT-IDENTICAL to step 0 (lr(0) = 0), else the run aborts.
STOP-aware (llmspec/STOP) and disk-guarded (remote_st.check_stop: C: >= 10 GB free).
"""
import argparse, hashlib, io, json, math, os, queue, subprocess, sys, threading, time
from pathlib import Path
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import numpy as np
import torch

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import remote_st as RS  # noqa: E402
import q1_models as QM  # noqa: E402
import q1_licence as QL  # noqa: E402
from bg1_score import read_bytes, SAMPLE_BYTES, GATE_STEPS, EXTRA_STEPS  # noqa: E402

assert torch.cuda.is_available(), "Arm B is GPU-only: CUDA not available"
DEV = torch.device("cuda")
torch.cuda.set_per_process_memory_fraction(0.85)          # leave room for the desktop; an overrun raises OOM
ARMS = {"A0": (1430, 3000), "A1": (2860, 5000), "A2": (715, 3000), "M0s1": (1430, 3000), "M0s2": (1430, 3000)}
MUON_ARMS = {"M0s1", "M0s2"}  # Muon (armb/muon.py, bf16 NS per the sealed update test, B1a-A6)
INIT = {"M0s2": "EleutherAI/pythia-70m-seed1"}   # everything else starts from EleutherAI/pythia-70m step0 (B1a-A1)
SEED1_DIR = "~/llmspec_armb/data/seed1_batches"  # on spot; built by armb/seed_order.py (B1a-A7)
OPT_STEPS = {1, 10, 100, 256, 512, 1000, 1430, 2000, 3000, 5000}
BATCH, MICRO, SEQ = 1024, 8, 2048
PYTHIA_MICRO = 32   # Pythia's per-GPU micro-batch: DeepSpeed backpropagated cur_scale x (mean loss over 32 sequences), so the
                    # per-token gradient factor in the fp16 graph is cur_scale / (32 x 2048). We match it per token (B1a-A5).
SPOT = "spot"
REMOTE = "~/llmspec_armb/ckpt"


def ckpt_grid(stop):
    return [int(x) for x in QL.grid(stop)]


def lr_at(n, W):
    return QM.lr(n, W)


# ---------------------------------------------------------------- data
class PileOrder:
    """Pythia's order: update k (1-based) = preshuffled samples [(k-1)*1024, k*1024). Prefetches ahead."""
    def __init__(self, first_k, last_k, ahead=3):
        self.q = queue.Queue(maxsize=ahead); self.k = first_k
        self.t = threading.Thread(target=self._run, args=(first_k, last_k), daemon=True); self.t.start()

    def _run(self, a, b):
        for k in range(a, b + 1):
            raw = read_bytes((k - 1) * BATCH * SAMPLE_BYTES, BATCH * SAMPLE_BYTES)
            self.q.put((k, np.frombuffer(raw, dtype=np.uint16).reshape(BATCH, 2049), hashlib.sha256(raw).hexdigest()))

    def next(self):
        k, arr, h = self.q.get(); assert k == self.k, (k, self.k); self.k += 1
        return arr, h


class SeedBatches(PileOrder):
    """PolyPythias seed-1 order (M0s2): update k = spot:SEED1_DIR/step{k:05d}.npy, sha256-verified against the
    generator's steps.jsonl record before use (fails closed if the record or the file is missing / mismatched)."""
    def _run(self, a, b):
        for k in range(a, b + 1):
            for i in range(30):
                txt = subprocess.run(["ssh", "-o", "BatchMode=yes", SPOT, f"grep -h '\"step\": {k},' {SEED1_DIR}/steps.jsonl | tail -1"],
                                     capture_output=True, text=True).stdout.strip()
                if txt:
                    break
                time.sleep(60)                            # not materialised yet: wait (bounded, 30 min)
            rec = json.loads(txt)
            raw = subprocess.run(["ssh", "-o", "BatchMode=yes", SPOT, f"cat {SEED1_DIR}/{rec['file']}"], capture_output=True).stdout
            assert hashlib.sha256(raw).hexdigest() == rec["sha256"], f"seed-1 batch {k}: sha256 mismatch"
            arr = np.load(io.BytesIO(raw)); assert arr.shape == (BATCH, 2049) and arr.dtype == np.uint16
            self.q.put((k, arr, hashlib.sha256(arr.tobytes()).hexdigest()))


# ---------------------------------------------------------------- model / optimizer
def build(init_repo):
    from transformers import AutoConfig, GPTNeoXForCausalLM
    cfg = AutoConfig.from_pretrained("EleutherAI/pythia-70m"); cfg._attn_implementation = "sdpa"
    m = GPTNeoXForCausalLM(cfg)
    sd = None
    for fn in ("model.safetensors", "pytorch_model.bin"):          # PolyPythias seed repos ship fp16 .bin only
        url = f"https://huggingface.co/{init_repo}/resolve/step0/{fn}"
        if RS.requests.head(url, allow_redirects=True, timeout=60).status_code != 200:
            continue
        tmp = ROOT / "armb" / f"_init_step0_{fn}"
        with RS.requests.get(url, stream=True, timeout=300) as r, open(tmp, "wb") as f:
            r.raise_for_status()
            for c in r.iter_content(1 << 22):
                f.write(c)
        if fn.endswith(".safetensors"):
            from safetensors.torch import load_file
            sd = load_file(str(tmp))
        else:
            sd = torch.load(str(tmp), map_location="cpu", weights_only=True)
        tmp.unlink(); break
    assert sd is not None, f"no step0 weights for {init_repo}"
    missing, unexpected = m.load_state_dict({k: v.float() for k, v in sd.items() if torch.is_floating_point(v)}, strict=False)
    params = {n for n, _ in m.named_parameters()}
    assert not (set(missing) & params), sorted(set(missing) & params)[:5]
    return m.to(DEV).train()


def param_groups(m):
    """GPT-NeoX get_params_for_weight_decay_optimization: no decay for LayerNorm params and biases."""
    decay, no = [], []
    for mod in m.modules():
        for n, p in mod._parameters.items():
            if p is None:
                continue
            (no if isinstance(mod, torch.nn.LayerNorm) or n == "bias" else decay).append(p)
    return [{"params": decay, "weight_decay": 0.1}, {"params": no, "weight_decay": 0.0}]


TYPES = {"Q_K_V": "attention.query_key_value.weight", "O": "attention.dense.weight",
         "MLP_IN": "mlp.dense_h_to_4h.weight", "MLP_OUT": "mlp.dense_4h_to_h.weight"}


class DynamicLossScaler:
    """Line-for-line port of DeeperSpeed@eb7f5cf deepspeed/runtime/fp16/loss_scaler.py DynamicLossScaler.update_scale
    (init_scale = 2**initial_scale_power; delayed_shift = hysteresis; consecutive_hysteresis False)."""
    def __init__(self, init_scale=2 ** 12, scale_factor=2.0, scale_window=1000, min_scale=1, delayed_shift=2,
                 consecutive_hysteresis=False):
        self.cur_scale = float(init_scale); self.cur_iter = 0; self.last_overflow_iter = -1
        self.scale_factor = scale_factor; self.scale_window = scale_window; self.min_scale = min_scale
        self.delayed_shift = delayed_shift; self.cur_hysteresis = delayed_shift; self.consecutive_hysteresis = consecutive_hysteresis

    def update_scale(self, overflow):
        if overflow:
            if self.delayed_shift == 1 or self.cur_hysteresis == 1:
                if self.cur_scale == self.min_scale:
                    raise RuntimeError("Current loss scale already at minimum - cannot decrease scale anymore.")
                self.cur_scale = max(self.cur_scale / self.scale_factor, self.min_scale)
            else:
                self.cur_hysteresis -= 1
            self.last_overflow_iter = self.cur_iter
        else:
            if self.consecutive_hysteresis:
                self.cur_hysteresis = self.delayed_shift
            if (self.cur_iter - self.last_overflow_iter) % self.scale_window == 0:
                if not self.consecutive_hysteresis:
                    self.cur_hysteresis = self.delayed_shift
                self.cur_scale *= self.scale_factor
        self.cur_iter += 1

    def state(self):
        return dict(self.__dict__)

    def load(self, d):
        self.__dict__.update(d)


# ---------------------------------------------------------------- upload + gate threads
def sh(cmd, tries=8):
    for i in range(tries):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(min(2 ** i, 120))
    raise RuntimeError(f"{cmd}: {r.stderr[-300:]}")


class Uploader(threading.Thread):
    def __init__(self, arm):
        super().__init__(daemon=True); self.arm = arm; self.q = queue.Queue(); self.err = None
        sh(["ssh", "-o", "BatchMode=yes", SPOT, f"mkdir -p {REMOTE}/{arm}"])

    def run(self):
        while True:
            fp = self.q.get()
            if fp is None:
                return
            try:
                local = hashlib.sha256(fp.read_bytes()).hexdigest()
                sh(["rsync", "-a", "--partial", str(fp), f"{SPOT}:{REMOTE}/{self.arm}/"])
                rem = sh(["ssh", "-o", "BatchMode=yes", SPOT, f"sha256sum {REMOTE}/{self.arm}/{fp.name}"]).split()[0]
                assert rem == local, (fp.name, rem, local)
                sh(["ssh", "-o", "BatchMode=yes", SPOT, f"echo {local} > {REMOTE}/{self.arm}/{fp.name}.ok"])
                fp.unlink()
            except Exception as e:                       # keep the file locally; surface the error to the main loop
                self.err = repr(e)
            finally:
                self.q.task_done()


class GatePuller(threading.Thread):
    def __init__(self, stopfile):
        super().__init__(daemon=True); self.stopfile = stopfile; self.last = []; self.done = threading.Event()

    def run(self):
        while not self.done.is_set():
            try:
                txt = sh(["ssh", "-o", "BatchMode=yes", SPOT, "cat ~/llmspec_armb/bg1/bg1_verdicts.jsonl 2>/dev/null || true"], tries=3)
                self.last = [json.loads(l) for l in txt.splitlines() if l.strip()]
                for v in self.last:
                    if not v["pass"]:
                        self.stopfile.write_text(f"B-G1 FAIL step {v['step']} ({v['worst']} z={v['z']:.2f} T={v['T']:.2f})")
            except Exception:
                pass
            self.done.wait(60)


# ---------------------------------------------------------------- main loop
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("arm"); ap.add_argument("--stop", type=int); ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.arm not in ARMS:
        raise SystemExit(f"arm {a.arm}: not implemented in this trainer (M0 needs Muon / index maps)")
    W, stop = ARMS[a.arm]; stop = a.stop or stop
    arm = a.arm + ("_test" if a.test else "")
    stage = ROOT / "armb" / "staging" / arm; stage.mkdir(parents=True, exist_ok=True)
    logf = stage / "trainlog.jsonl"; resume = stage / "resume.pt"
    print("device:", torch.cuda.get_device_name(0), "| arm", arm, "W", W, "stop", stop, flush=True)
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    model = build(INIT.get(a.arm, "EleutherAI/pythia-70m")); print("init:", INIT.get(a.arm, "EleutherAI/pythia-70m"), "step0", flush=True)
    if a.arm in MUON_ARMS:
        from muon import MuonHybrid, MUON_VERSION
        opt = MuonHybrid(model, 8, 64, ns_dtype=torch.bfloat16); print("optimizer:", MUON_VERSION, flush=True)
    else:
        opt = torch.optim.AdamW(param_groups(model), lr=0.0, betas=(0.9, 0.95), eps=1e-8, fused=True)
    step, n_applied, n_skipped = 0, 0, 0
    scaler = DynamicLossScaler()
    if resume.exists():
        st = torch.load(resume, map_location=DEV, weights_only=False)
        model.load_state_dict(st["model"]); opt.load_state_dict(st["opt"]); step = st["step"]
        n_applied, n_skipped = st["n_applied"], st["n_skipped"]; scaler.load(st["scaler"])
        print("resumed at step", step, flush=True)

    def micro_loss(xb):
        with torch.autocast("cuda", dtype=torch.float16):
            logits = model(input_ids=xb[:, :SEQ]).logits
        return torch.nn.functional.cross_entropy(logits.float().reshape(-1, logits.size(-1)), xb[:, 1:].reshape(-1))
    cmicro = torch.compile(micro_loss)
    grid = set(ckpt_grid(stop)); up = Uploader(arm); up.start()
    gate = GatePuller(ROOT / "STOP") if a.arm == "A0" and not a.test else None
    if gate:
        gate.start()

    def save_ckpt(t):
        sd = {k: v.detach().float().cpu() for k, v in model.state_dict().items()}
        fp = stage / f"step{t:05d}.pt"
        RS.durable_save(fp, lambda p: torch.save(sd, p)); up.q.put(fp)
        if t in OPT_STEPS:
            fo = stage / f"optim{t:05d}.pt"
            RS.durable_save(fo, lambda p: torch.save(opt.state_dict(), p)); up.q.put(fo)
        return sd

    sd0 = save_ckpt(0) if step == 0 else None                  # kept in RAM for the step-1 replica check
    data = (SeedBatches if a.arm == "M0s2" else PileOrder)(step + 1, stop)
    while step < stop:
        RS.check_stop()
        if up.err:
            raise RuntimeError("upload failed: " + up.err)
        k = step + 1; lr = lr_at(n_applied, W)               # the n-th applied update uses lr(n-1); skips do not advance it
        if a.arm not in MUON_ARMS:
            for gp in opt.param_groups:
                gp["lr"] = lr
        arr, bh = data.next(); x = torch.from_numpy(arr.astype(np.int64)).to(DEV)
        before = {n: p.detach().clone() for n, p in model.named_parameters() if any(n.endswith(s_) for s_ in TYPES.values())}
        tot = torch.zeros((), device=DEV); scale = scaler.cur_scale
        for i in range(0, BATCH, MICRO):
            loss = cmicro(x[i:i + MICRO])
            (loss * (scale * MICRO / PYTHIA_MICRO)).backward(); tot += loss.detach() * (MICRO / BATCH)
        grads = [p.grad for p in model.parameters() if p.grad is not None]
        overflow = bool(torch.stack([torch.logical_not(torch.isfinite(g).all()) for g in grads]).any())
        if overflow:
            gn = float("nan"); n_skipped += 1; opt.zero_grad(set_to_none=True)
        else:
            for g in grads:
                g.div_(scale * BATCH / PYTHIA_MICRO)                 # -> the mean gradient over the 1024-sequence batch
            gn = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0))
            (opt.step(lr) if a.arm in MUON_ARMS else opt.step()); opt.zero_grad(set_to_none=True); n_applied += 1
        scaler.update_scale(overflow); step = k; tot = float(tot)
        dW = {}
        for n, p in model.named_parameters():
            for T_, suf in TYPES.items():
                if n.endswith(suf):
                    dW[T_] = dW.get(T_, 0.0) + float(((p.detach() - before[n]) ** 2).sum())
        rec = {"step": step, "loss": tot, "lr": lr, "grad_norm_preclip": gn, "dW_norm": {t: v ** 0.5 for t, v in dW.items()},
               "loss_scale": scale, "overflow": overflow, "n_applied": n_applied, "n_skipped": n_skipped,
               "batch_sha256": bh, "time": time.time()}
        with open(logf, "a") as f:
            f.write(json.dumps(rec) + "\n")
        if step in grid:
            sd = save_ckpt(step)
            if step == 1 and sd0 is not None:                      # replica check: lr(0) = 0 -> step1 == step0
                same = all(torch.equal(sd[k_], sd0[k_]) for k_ in sd0)
                print("replica check step1 == step0:", same, flush=True)
                if not same:
                    raise SystemExit("REPLICA CHECK FAILED: step1 != step0 although lr(0) = 0")
                sd0 = None
        if step % 50 == 0 or step == stop:
            RS.durable_save(resume, lambda p: torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "step": step,
                                                           "n_applied": n_applied, "n_skipped": n_skipped,
                                                           "scaler": scaler.state()}, p))
        if step % 10 == 0 or step <= 16:
            print(f"step {step} loss {tot:.4f} lr {lr:.3e} gn {gn:.3f} scale {scale:g} skipped {n_skipped}", flush=True)
    up.q.join(); up.q.put(None)
    if gate:
        gate.done.set()
    print("done", arm, "step", step, flush=True)


if __name__ == "__main__":
    try:
        main()
    except RS.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
