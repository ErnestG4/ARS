"""Pre-data check (Will, 09-27): does Pythia-70M show the 4k->5k low-rank update burst that STAGE3_FINDINGS §12 found
on 1.4B (V 111 -> 35, O 179 -> 45, MLP_OUT 314 -> 193 in the 4k->5k interval, recovering by 7k->8k; Q/K no dip)?
Decides A0's stop step: 5000 only if the burst is present in Pythia-70M. Criterion FROZEN by commit before running.

Released checkpoints (reference data only; no arm exists): pythia-70m steps 3000, 4000, 5000, 6000 (primary);
PolyPythias pythia-70m-seed1..9 at the same steps (descriptive: is it run-specific?).
Per 1000-step interval I = [t, t+1000]: layer-mean stable rank of dW = W(t+1000) - W(t), per type (Q, K, V from the
fused QKV as Stage 3; O; MLP_IN; MLP_OUT), fp64.
Burst ratio r_M = sr(dW, 4k->5k) / mean(sr(dW, 3k->4k), sr(dW, 5k->6k)).
  PRESENT  iff r <= 0.5 for >= 2 of {V, O, MLP_OUT}          -> A0 stop 5000
  ABSENT   iff r >= 0.8 for all of {V, O, MLP_OUT}           -> A0 stop 3000
  otherwise AMBIGUOUS                                        -> A0 stop 3000 (Will's rule: 5000 only if shown), reported
Output: results/armb_burst_check_70m.json.
"""
import json, os, sys, tempfile
from pathlib import Path
import numpy as np, requests, torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import remote_st as RS  # noqa: E402

H, DH, D, NL = 8, 64, 512, 6
STEPS = [3000, 4000, 5000, 6000]
RUNS = ["EleutherAI/pythia-70m"] + [f"EleutherAI/pythia-70m-seed{k}" for k in range(1, 10)]
TMP = Path(os.environ.get("ARMB_SCRATCH", tempfile.gettempdir()))


def load(repo, step):
    for fn in ("model.safetensors", "pytorch_model.bin"):
        url = f"https://huggingface.co/{repo}/resolve/step{step}/{fn}"
        if requests.head(url, allow_redirects=True, timeout=60).status_code != 200:
            continue
        tmp = TMP / f"burst_{repo.split('/')[-1]}_{step}_{fn}"
        for i in range(10):
            try:
                with requests.get(url, stream=True, timeout=300) as r, open(tmp, "wb") as f:
                    r.raise_for_status()
                    for c in r.iter_content(1 << 22):
                        f.write(c)
                break
            except (requests.RequestException, IOError):
                if i == 9:
                    raise
        try:
            if fn.endswith(".safetensors"):
                from safetensors.torch import load_file
                sd = load_file(str(tmp))
            else:
                sd = torch.load(str(tmp), map_location="cpu", weights_only=True)
        finally:
            tmp.unlink()
        return {k: v.double() for k, v in sd.items() if torch.is_floating_point(v)}
    raise RuntimeError(f"{repo} step{step}: no weights")


def mats(sd, L):
    p = f"gpt_neox.layers.{L}."
    qkv = sd[p + "attention.query_key_value.weight"].reshape(H, 3, DH, D)
    return {"Q": qkv[:, 0].reshape(H * DH, D), "K": qkv[:, 1].reshape(H * DH, D), "V": qkv[:, 2].reshape(H * DH, D),
            "O": sd[p + "attention.dense.weight"], "MLP_IN": sd[p + "mlp.dense_h_to_4h.weight"],
            "MLP_OUT": sd[p + "mlp.dense_4h_to_h.weight"]}


def sr(W):
    s = torch.linalg.svdvals(W.cuda()); return float((s ** 2).sum() / s[0] ** 2)


def main():
    assert torch.cuda.is_available()
    out = {"doc": __doc__, "runs": {}}
    for repo in RUNS:
        sds = {s: load(repo, s) for s in STEPS}
        iv = {}
        for a, b in zip(STEPS[:-1], STEPS[1:]):
            iv[f"{a}-{b}"] = {M: float(np.mean([sr(mats(sds[b], L)[M] - mats(sds[a], L)[M]) for L in range(NL)]))
                              for M in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")}
        r = {M: iv["4000-5000"][M] / np.mean([iv["3000-4000"][M], iv["5000-6000"][M]]) for M in iv["4000-5000"]}
        tri = [r[M] for M in ("V", "O", "MLP_OUT")]
        verdict = "PRESENT" if sum(x <= 0.5 for x in tri) >= 2 else ("ABSENT" if all(x >= 0.8 for x in tri) else "AMBIGUOUS")
        out["runs"][repo] = {"interval_sr": iv, "ratio": r, "verdict": verdict}
        print(repo, verdict, {M: round(v, 2) for M, v in r.items()}, flush=True)
        del sds; RS.check_stop()
    prim = out["runs"]["EleutherAI/pythia-70m"]["verdict"]
    out["primary_verdict"] = prim
    out["A0_stop"] = 5000 if prim == "PRESENT" else 3000
    out["seed_counts"] = {v: sum(x["verdict"] == v for x in out["runs"].values()) for v in ("PRESENT", "ABSENT", "AMBIGUOUS")}
    (ROOT / "results" / "armb_burst_check_70m.json").write_text(json.dumps(out, indent=1))
    print("PRIMARY:", prim, "-> A0 stop", out["A0_stop"], "| all runs:", out["seed_counts"])


if __name__ == "__main__":
    main()
