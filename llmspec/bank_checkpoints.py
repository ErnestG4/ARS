"""Bank full HF checkpoints locally (sequential; size-verified; resumable; honours STOP).
Usage: bank_checkpoints.py <model-key> <rev> [<rev> ...]   -> cache/ckpt/<model>/<rev>/"""
import sys, os, time
from pathlib import Path
from huggingface_hub import hf_hub_download, HfApi
import remote_st as R
import specs as S

ROOT = Path(__file__).resolve().parent


def bank(model, rev):
    repo = S.MODELS[model]["repo"]
    d = ROOT / "cache" / "ckpt" / model / rev
    if (d / "DONE").exists():
        return
    info = HfApi().model_info(repo, revision=rev, files_metadata=True)
    want = {s.rfilename: s.size for s in info.siblings
            if s.rfilename.endswith(".safetensors") or s.rfilename in ("config.json", "model.safetensors.index.json")}
    t = time.time()
    for fn, size in want.items():
        R.check_stop()
        p = Path(hf_hub_download(repo, fn, revision=rev, local_dir=d))
        if size is not None and p.stat().st_size != size:
            raise IOError(f"size mismatch {p}: {p.stat().st_size} != {size}")
    (d / "DONE").write_text(f"{sum(v or 0 for v in want.values())} bytes")
    print(f"{model} {rev} banked {sum(v or 0 for v in want.values())/1e9:.2f} GB in {time.time()-t:.0f}s", flush=True)


if __name__ == "__main__":
    try:
        for rev in sys.argv[2:]:
            bank(sys.argv[1], rev)
    except R.Stopped as e:
        print("STOPPED:", e, flush=True); sys.exit(3)
