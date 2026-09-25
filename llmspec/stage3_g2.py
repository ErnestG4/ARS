"""Stage 3 G2 functional witness (brief v1.1 §5 G2). PRE-REGISTERED by this commit, before it runs.

Question (Diffract replication, first): for Pythia-1.4B at step 143000, does permuting singular values WITHIN a band
of every layer weight matrix change the text-probe loss? For each of the 144 layer matrices (24 layers x
Q, K, V, O, MLP_IN, MLP_OUT; Q/K/V permuted as full 2048 x 2048 blocks of the fused QKV), W = U diag(sigma) V^T
(fp64 SVD) is rebuilt as U diag(pi(sigma)) V^T, where pi permutes sigma inside a rank band (bands as in
STAGE3_PREREG: LOWER [0.01, 0.10), BULK [0.10, 0.90), UPPER [0.90, 0.99), by ascending rank). The rebuilt W is
stored back in fp16, the model's own storage precision. Embeddings, LayerNorms and biases are untouched.
Conditions (the same permutation seed family for every matrix):
  identity  (pi = id)          -> CONTROL: measures SVD-rebuild + fp16 re-rounding error alone
  bulk      x 3 seeds
  full      x 3 seeds          (all sigma permuted)
  upper     x 3 seeds
  lower     x 3 seeds
Metric: mean next-token loss on the fixed text probes (results/probes.npz, 64 x 512), exact fp32 compute (the
verified fp16-storage + transient-fp32 model). The baseline is the unmodified checkpoint.
Readings, fixed now:
  identity |dloss| must be <= 0.01 nats, or the witness is broken (reported, and nothing else is read).
  A band is FUNCTIONALLY INERT if its mean dloss <= 3x the identity |dloss| + 0.01 nats, and FUNCTIONAL
  otherwise. Diffract's pattern replicates iff bulk is INERT and full is FUNCTIONAL with dloss >= 1 nat.
  A band that Stage 3 finds spectrally anomalous but that is functionally inert is reported as exactly that.
Output: results/stage3_g2.json (resumable per condition). Honours STOP and the GPU cap.
"""
import os, sys, json, time
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from pathlib import Path
import numpy as np
import torch
import remote_st as R
import stage3_extract as X
import s3stats as S

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "stage3_g2.json"
REV = "step143000"
CONDS = [("identity", 0)] + [(b, s) for b in ("bulk", "full", "upper", "lower") for s in (1, 2, 3)]


def perm_sigma(sig_desc, band, seed):
    n = len(sig_desc)
    asc = sig_desc[::-1].copy()
    if band == "identity":
        return sig_desc.copy()
    rng = np.random.default_rng(seed)
    if band == "full":
        idx = np.arange(n)
    else:
        a, b = S.band_idx(n, band)
        idx = np.arange(a, b)
    asc[idx] = asc[rng.permutation(idx)]
    return asc[::-1].copy()


def targets(L):
    p = f"gpt_neox.layers.{L}."
    return [(p + "attention.query_key_value.weight", j) for j in range(3)] + \
           [(p + "attention.dense.weight", None), (p + "mlp.dense_h_to_4h.weight", None), (p + "mlp.dense_4h_to_h.weight", None)]


@torch.no_grad()
def text_loss(m, probes):
    text = torch.as_tensor(probes["text"], device=X.DEV)
    ls = []
    for b in range(len(text)):
        ids = text[b:b + 1]
        o = m(ids)
        ls.append(torch.nn.functional.cross_entropy(o.logits[0, :-1].float(), ids[0, 1:], reduction="none"))
        del o
    return float(torch.cat(ls).mean())


def main():
    res = json.loads(OUT.read_text()) if OUT.exists() else {"doc": __doc__, "rev": REV, "conds": {}}
    # QKV note: the three 2048 x 2048 blocks of one fused tensor are permuted in turn; each block's SVD is taken
    # from the fused tensor's current contents, and blocks do not overlap, so every block starts from original.
    probes = np.load(ROOT / "results" / "probes.npz")
    ck = X.Ckpt("pythia-1.4b", REV)
    ck.fetch_all()
    m = X.build_model(ck)
    names = [n for L in range(24) for n, _ in targets(L)]
    names = list(dict.fromkeys(names))
    params = dict(m.named_parameters())

    def restore():
        """Re-stream the original tensors from HF (no resident second copy: that would double GPU memory)."""
        for n in names:
            a, _ = R.fetch(ck.idx, n)
            a16 = a.astype(np.float16)
            assert np.array_equal(a16.astype(np.float32), a)
            params[n].data.copy_(torch.from_numpy(a16).to(X.DEV))
    if "baseline" not in res:
        res["baseline"] = text_loss(m, probes)
        R.durable_save(OUT, lambda p: p.write_text(json.dumps(res, indent=1)))
    print("baseline", res["baseline"], flush=True)
    for band, seed in CONDS:
        key = f"{band}:{seed}"
        if key in res["conds"]:
            continue
        R.check_stop()
        t = time.time()
        for L in range(24):
            for name, j in targets(L):
                P = params[name]
                W16 = P.data if j is None else P.data.reshape(16, 3, 128, 2048)[:, j].reshape(2048, 2048)
                U, s, Vh = torch.linalg.svd(W16.double(), full_matrices=False)   # from the ORIGINAL (restored) weights
                s2 = torch.from_numpy(perm_sigma(s.cpu().numpy(), band, seed + 1000 * L + (j or 0))).to(X.DEV)
                Wn = ((U * s2) @ Vh).half()
                if j is None:
                    P.data.copy_(Wn)
                else:
                    P.data.reshape(16, 3, 128, 2048)[:, j].copy_(Wn.reshape(16, 128, 2048))
                del U, s, Vh, Wn
            torch.cuda.empty_cache()
        loss = text_loss(m, probes)
        res["conds"][key] = {"loss": loss, "dloss": loss - res["baseline"]}
        restore()
        R.durable_save(OUT, lambda p: p.write_text(json.dumps(res, indent=1)))
        print(f"{key}: loss {loss:.4f} dloss {loss - res['baseline']:+.4f} ({time.time()-t:.0f}s, "
              f"peak_gpu={torch.cuda.max_memory_allocated()/2**30:.2f}GiB)", flush=True)
    ident = abs(res["conds"]["identity:0"]["dloss"])
    res["identity_ok"] = ident <= 0.01
    thr = 3 * ident + 0.01
    res["readings"] = {}
    for band in ("bulk", "full", "upper", "lower"):
        d = float(np.mean([res["conds"][f"{band}:{s}"]["dloss"] for s in (1, 2, 3)]))
        res["readings"][band] = {"mean_dloss": d, "FUNCTIONAL": d > thr}
    res["diffract_replicates"] = bool(res["identity_ok"] and not res["readings"]["bulk"]["FUNCTIONAL"]
                                      and res["readings"]["full"]["mean_dloss"] >= 1.0)
    R.durable_save(OUT, lambda p: p.write_text(json.dumps(res, indent=1)))
    print(json.dumps({k: res[k] for k in ("identity_ok", "readings", "diffract_replicates")}, indent=1))


if __name__ == "__main__":
    try:
        main()
    except R.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
