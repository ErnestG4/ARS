"""Stream single tensors out of HF safetensors files by HTTP range (no full download).

Headers are cached under cache/headers; tensors are fetched sequentially, size-verified,
and returned as numpy. STOP file (llmspec/STOP) aborts cleanly between tensors.
"""
import json, os, struct, time, hashlib
from pathlib import Path
import numpy as np
import requests
from huggingface_hub import hf_hub_url

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
STOP = ROOT / "STOP"
DT = {"F32": np.float32, "F16": np.float16, "BF16": np.uint16, "F64": np.float64}


class Stopped(Exception):
    pass


def check_stop():
    if STOP.exists():
        raise Stopped("llmspec/STOP present")


def _get(url, lo, hi, tries=6):
    for i in range(tries):
        try:
            r = requests.get(url, headers={"Range": f"bytes={lo}-{hi}"}, timeout=300)
            if r.status_code == 206 and len(r.content) == hi - lo + 1:
                return r.content
            err = f"status {r.status_code} len {len(r.content)} want {hi-lo+1}"
        except requests.RequestException as e:
            err = repr(e)
        time.sleep(2 ** i)
    raise IOError(f"range fetch failed {url} {lo}-{hi}: {err}")


def header(repo, fn, rev):
    key = hashlib.sha1(f"{repo}|{fn}|{rev}".encode()).hexdigest()[:16]
    p = CACHE / "headers" / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text())
    url = hf_hub_url(repo, fn, revision=rev)
    n = struct.unpack("<Q", _get(url, 0, 7))[0]
    h = json.loads(_get(url, 8, 8 + n - 1))
    out = {"repo": repo, "fn": fn, "rev": rev, "data_start": 8 + n, "tensors": h}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out))
    return out


def index(repo, rev):
    """tensor name -> (file, header) for sharded or single-file checkpoints."""
    from huggingface_hub import HfApi
    files = HfApi().list_repo_files(repo, revision=rev)
    st = [f for f in files if f.endswith(".safetensors")]
    m = {}
    for f in st:
        h = header(repo, f, rev)
        for k in h["tensors"]:
            if k != "__metadata__":
                m[k] = h
    return m


def fetch(idx, name):
    """Return (array as stored dtype -> float64 view for bf16 handled by caller, dtype str)."""
    check_stop()
    h = idx[name]
    t = h["tensors"][name]
    a, b = t["data_offsets"]
    url = hf_hub_url(h["repo"], h["fn"], revision=h["rev"])
    raw = _get(url, h["data_start"] + a, h["data_start"] + b - 1)
    arr = np.frombuffer(raw, dtype=DT[t["dtype"]]).reshape(t["shape"])
    if t["dtype"] == "BF16":
        arr = (arr.astype(np.uint32) << 16).view(np.float32)
    return arr, t["dtype"]
