"""Download the FINAL checkpoints (revision step143000) of Pythia-1.4B / 410M / 70M (safetensors + config + tokenizer)
into the HF cache. Network + disk only; no GPU. Sequential (parallel downloads to one disk are forbidden here)."""
import sys, time
from huggingface_hub import snapshot_download
for m in ["EleutherAI/pythia-70m", "EleutherAI/pythia-410m", "EleutherAI/pythia-1.4b"]:
    t = time.time()
    p = snapshot_download(m, revision="step143000", allow_patterns=["*.safetensors", "*.json", "*.txt", "tokenizer*"],
                          max_workers=1)
    print(f"{m} -> {p}  ({time.time()-t:.0f}s)", flush=True)
print("FETCH_DONE", flush=True)
