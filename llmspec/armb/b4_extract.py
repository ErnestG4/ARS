"""Arm B, stage B4 extraction (ARMB_PREREG_B1B.md; sealed with the B4 amendment). GPU only (hard-asserted).
Reuses Stage 3's extraction UNCHANGED -- stage3_extract.layer() and stage3_extract.markers() (estimator
"stage3-extract-v1", "stage3-markers-v1"), imported, not re-typed -- on:
  (a) every checkpoint on each arm's sealed grid: spot:~/llmspec_armb/ckpt/<arm>/step{t:05d}.pt, pulled over ssh and
      sha256-verified against its .ok marker, fp32 masters kept as fp32 on the GPU (CkptArmb). Output:
      cache/armb/<arm>/step{t:05d}/L{l:02d}.npz + MARKERS.npz (+ DONE).
  (b) the 10 B-G1 reference runs (pythia-70m, pythia-70m-seed1..9) at the shared steps, through stage3_extract.run()
      itself (Stage 3's own path): cache/s3/<model>/step{t}/...  (Q4's AdamW reference spread for metrics outside
      the B-G1 band, and the descriptive A0 - Pythia comparison).
  (c) dW stable ranks for the sealed Q3 / Q4 intervals: armb/<arm>/DW_<t1>_<t2>.npz (per layer, per type Q, K, V, O,
      MLP_IN, MLP_OUT; ||dW||_F^2 / ||dW||_2^2 from fp64 singular values), and for the reference runs at the shared
      intervals [512, 1000], [1000, 2000], [2000, 3000].
W_E^T W_U~ for the copy circuit is formed exactly as stage3_extract.run / verify_refactor_regression do (vocab chunks of
4096, fp64, W_U~ = W_U diag(g_f)). Nothing here chooses or computes a test statistic: b4_analyze.py does.
Usage: b4_extract.py arm <arm>        (all grid checkpoints of that arm, then its dW intervals; resumable)
       b4_extract.py refs             (the 10 reference runs at the shared steps + their dW intervals; + pythia-70m
                                       step143000, the rms source stage3_witness.py needs for the 70M witness)
"""
import hashlib, io, json, os, subprocess, sys
from pathlib import Path
import numpy as np
import torch

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
assert torch.cuda.is_available(), "B4 extraction is GPU-only"
import stage3_extract as X  # noqa: E402  (sets its own 6 GB per-process GPU cap)
import remote_st as R  # noqa: E402
import q1_licence as QL  # noqa: E402

H, DH, D, NL = 8, 64, 512, 6
STOPS = {"A0": 3000, "A1": 5000, "A2": 3000, "M0s1": 3000, "M0s2": 3000}
SHARED = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, 2000, 3000]
REFS = ["pythia-70m"] + [f"pythia-70m-seed{k}" for k in range(1, 10)]
# sealed Q3 intervals (B1b Q3) + Q4 shared intervals; (L) intervals are derived from the sealed LR function below
Q3_S = [(100, 130), (200, 230), (300, 330), (400, 430), (1000, 1025), (2000, 2025)]
Q4_SHARED_INTERVALS = [(512, 1000), (1000, 2000), (2000, 3000)]
CACHE = ROOT / "cache" / "armb"


class CkptArmb:
    """Same interface as stage3_extract.Ckpt for an Arm B checkpoint; fp32 kept as fp32 (masters are not on the fp16 grid)."""
    SKIP = ("attention.bias", "attention.masked_bias", "inv_freq")

    def __init__(self, arm, step):
        self.repo, self.rev = "EleutherAI/pythia-70m", "step0"          # config.json source only
        f = f"~/llmspec_armb/ckpt/{arm}/step{step:05d}.pt"
        raw = subprocess.run(["ssh", "-o", "BatchMode=yes", "spot", f"cat {f}"], capture_output=True, check=True).stdout
        ok = subprocess.run(["ssh", "-o", "BatchMode=yes", "spot", f"cat {f}.ok"], capture_output=True, text=True, check=True).stdout.strip()
        assert hashlib.sha256(raw).hexdigest() == ok, f"{arm} step {step}: sha256 != .ok marker"
        sd = torch.load(io.BytesIO(raw), map_location="cpu", weights_only=True)
        self.gpu = {k: v.float().to(X.DEV) for k, v in sd.items() if v.is_floating_point() and not k.endswith(self.SKIP)}
        self.idx = self.h = {k: None for k in self.gpu}
        self.sha256 = ok

    def get32(self, k):
        return self.gpu[k]

    def t(self, k):
        return self.gpu[k].to(torch.float64)

    def fetch_all(self):
        pass

    def close(self):
        self.gpu.clear(); torch.cuda.empty_cache()


def eu_matrix(ck):
    gf = ck.t("gpt_neox.final_layer_norm.weight")
    WE, WU = ck.get32("gpt_neox.embed_in.weight"), ck.get32("embed_out.weight")
    EU = torch.zeros(D, D, device=X.DEV, dtype=torch.float64)
    for i in range(0, WE.shape[0], 4096):
        EU += WE[i:i + 4096].double().T @ (WU[i:i + 4096].double() * gf)
    return EU


def extract_ckpt(ck, d):
    d.mkdir(parents=True, exist_ok=True)
    if (d / "DONE").exists():
        return
    probes = np.load(ROOT / "results" / "probes.npz")
    if not (d / "MARKERS.npz").exists():
        out = X.markers(ck, probes); R.durable_save(d / "MARKERS.npz", lambda t: np.savez(t, **out))
    EU = eu_matrix(ck)
    for L in range(NL):
        f = d / f"L{L:02d}.npz"
        if not f.exists():
            out = X.layer(ck, L, EU); R.durable_save(f, lambda t: np.savez(t, **out))
    R.durable_save(d / "DONE", lambda t: t.write_text(json.dumps({"est": X.EST, "ckpt_sha256": getattr(ck, "sha256", None)})))


def mats(sd_t, L):
    p = f"gpt_neox.layers.{L}."
    qkv = sd_t(p + "attention.query_key_value.weight").reshape(H, 3, DH, D)
    return {"Q": qkv[:, 0].reshape(H * DH, D), "K": qkv[:, 1].reshape(H * DH, D), "V": qkv[:, 2].reshape(H * DH, D),
            "O": sd_t(p + "attention.dense.weight"), "MLP_IN": sd_t(p + "mlp.dense_h_to_4h.weight"),
            "MLP_OUT": sd_t(p + "mlp.dense_4h_to_h.weight")}


def dw_ranks(ck1, ck2, out_fp):
    if out_fp.exists():
        return
    res = {}
    for L in range(NL):
        a, b = mats(ck1.t, L), mats(ck2.t, L)
        for M in a:
            s = torch.linalg.svdvals(b[M] - a[M])
            res[f"L{L:02d}_{M}_sr"] = np.array(float((s ** 2).sum() / s[0] ** 2)) if float(s[0]) > 0 else np.array(np.nan)
            res[f"L{L:02d}_{M}_fro"] = np.array(float((s ** 2).sum().sqrt()))
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    R.durable_save(out_fp, lambda t: np.savez(t, **res))


def lr_intervals():
    """(L) intervals of B1b Q3: early starts 100, 200, 300 on A0's schedule, extended on the 10-step grid until the
    cumulative applied LR matches that of [1000, 1025]."""
    import q1_models as QM
    C = QM._C0; target = C[1025] - C[1000]; out = []
    for a in (100, 200, 300):
        b = a
        while C[b] - C[a] < target and b < 500:
            b += 10
        out.append((a, b))
    return out


def run_arm(arm):
    X.set_model("pythia-70m")
    from grids import arm_grid
    for t in arm_grid(arm):                                  # B1a-A8 / B4 amendment 2 (A2 dense)
        R.check_stop()
        d = CACHE / arm / f"step{t:05d}"
        if (d / "DONE").exists():
            continue
        ck = CkptArmb(arm, t); extract_ckpt(ck, d); ck.close()
        print(f"{arm} step {t} extracted", flush=True)
    ivs = sorted(set(Q3_S + lr_intervals() + [iv for iv in Q4_SHARED_INTERVALS if iv[1] <= STOPS[arm]]))
    for a, b in ivs:
        fp = CACHE / arm / f"DW_{a:05d}_{b:05d}.npz"
        if fp.exists():
            continue
        c1, c2 = CkptArmb(arm, a), CkptArmb(arm, b); dw_ranks(c1, c2, fp); c1.close(); c2.close()
        print(f"{arm} dW [{a}, {b}] done", flush=True)


def run_refs():
    R.check_stop(); X.run("pythia-70m", "step143000")    # rms source for stage3_witness.py at 70M shapes (unchanged code)
    for m in REFS:
        for t in SHARED:
            R.check_stop(); X.run(m, f"step{t}")
        for a, b in Q4_SHARED_INTERVALS:
            fp = ROOT / "cache" / "s3" / m / f"DW_{a:05d}_{b:05d}.npz"
            if fp.exists():
                continue
            X.set_model(m); c1, c2 = X.make_ckpt(m, f"step{a}"), X.make_ckpt(m, f"step{b}")
            c1.fetch_all(); c2.fetch_all(); dw_ranks(c1, c2, fp)
            for c in (c1, c2):
                c.gpu.clear(); getattr(c, "close", lambda: None)()
            torch.cuda.empty_cache(); print(f"{m} dW [{a}, {b}] done", flush=True)


if __name__ == "__main__":
    try:
        if sys.argv[1] == "arm":
            run_arm(sys.argv[2])
        elif sys.argv[1] == "refs":
            run_refs()
        else:
            raise SystemExit(__doc__)
    except R.Stopped as e:
        print("STOPPED:", e, flush=True); sys.exit(3)
