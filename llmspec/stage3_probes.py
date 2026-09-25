"""Build the fixed Stage 3 probe set once (STAGE3_PREREG.md, Events). Writes results/probes.npz + its sha256.

text: the first 64 documents of NeelNanda/pile-10k (in file order) with >= 512 Pythia tokens, first 512 tokens
      each. The prereg says "first 512 tokens each", so documents shorter than 512 tokens are skipped; this reading
      is recorded here. Training-distribution proxy; possibly seen in training (flagged).
rep:  32 sequences r ++ r, |r| = 256, r uniform over token ids 1000..49999, seed 20260925.
"""
import hashlib, io, json
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
import requests
from huggingface_hub import hf_hub_url
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "probes.npz"


def main():
    if OUT.exists():
        print("exists", OUT); return
    fn = "data/train-00000-of-00001-4746b8785c874cc7.parquet"
    r = requests.get(hf_hub_url("NeelNanda/pile-10k", fn, repo_type="dataset"), timeout=300)
    assert len(r.content) == 33262901, len(r.content)
    tab = pq.read_table(io.BytesIO(r.content))            # in memory; no disk cache
    texts = tab.column("text").to_pylist()
    tok = Tokenizer.from_str(requests.get(hf_hub_url("EleutherAI/pythia-1.4b", "tokenizer.json"), timeout=120).text)
    text, used = [], []
    for i, t in enumerate(texts):
        ids = tok.encode(t).ids
        if len(ids) >= 512:
            text.append(ids[:512]); used.append(i)
        if len(text) == 64:
            break
    rng = np.random.default_rng(20260925)
    r0 = rng.integers(1000, 50000, size=(32, 256))
    rep = np.concatenate([r0, r0], 1)
    OUT.parent.mkdir(exist_ok=True)
    np.savez(OUT, text=np.array(text, dtype=np.int64), rep=rep.astype(np.int64), doc_index=np.array(used))
    h = hashlib.sha256(OUT.read_bytes()).hexdigest()
    (ROOT / "results" / "probes.sha256").write_text(h + "  probes.npz\n")
    print("probes", np.array(text).shape, rep.shape, "docs", used[:5], "...", used[-1], "sha256", h)


if __name__ == "__main__":
    main()
