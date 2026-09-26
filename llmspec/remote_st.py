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


def durable_save(path, save_fn):
    """Write via a tmp file, fsync it, rename, fsync the directory. A WSL crash on 2026-09-25 left zero-length
    files behind an atomic rename (the rename reached disk, the data did not); this ordering prevents that.
    The tmp name ends in the target's own suffix so np.save/np.savez do not append another."""
    import os
    path = Path(path)
    tmp = path.with_name(path.stem + ".tmp" + path.suffix)
    save_fn(tmp)
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
        os.posix_fadvise(f.fileno(), 0, 0, os.POSIX_FADV_DONTNEED)   # written pages leave the page cache, which
                                                                   # counts against vmmemWSL (host commit)
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


HOST_DISK = "/mnt/c"          # WSL `df /` reports the VHD; the VHD grows into C:, which is what fills
HOST_RESERVE_GB = 10.0        # Will, 2026-09-25: keep 10 GB free on C: at all times


def check_stop():
    import shutil
    if STOP.exists():
        raise Stopped("llmspec/STOP present")
    free = shutil.disk_usage(HOST_DISK).free / 1e9
    if free < HOST_RESERVE_GB:
        raise Stopped(f"host disk {HOST_DISK} free {free:.1f} GB < reserve {HOST_RESERVE_GB} GB")


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


CHUNK = 32 * 2 ** 20
THREADS = 8


def _get_parallel(url, lo, hi):
    """Range-fetch [lo, hi] in CHUNK pieces on THREADS threads into ONE in-memory buffer (no disk, no shared
    file). Each piece is size-verified by _get; memory is bounded by the tensor size."""
    n = hi - lo + 1
    if n <= CHUNK:
        return _get(url, lo, hi)
    from concurrent.futures import ThreadPoolExecutor
    buf = bytearray(n)
    def piece(o):
        e = min(o + CHUNK, n) - 1
        buf[o:e + 1] = _get(url, lo + o, lo + e)
    with ThreadPoolExecutor(THREADS) as ex:
        list(ex.map(piece, range(0, n, CHUNK)))
    return bytes(buf)


# ---- fast path (2026-09-25): keep-alive sessions + CDN URL resolved once per file + tensor-level concurrency.
# Measured on a real layer set: per-request TCP/TLS + redirect overhead held fetch() to ~19 MB/s; sessions alone give
# ~25 MB/s; 4 tensors in flight give ~76 MB/s. Output is byte-identical to fetch() (verify_fetch.py).
import threading
_tl = threading.local()
_cdn = {}
_cdn_lock = threading.Lock()


def _sess():
    if not hasattr(_tl, "s"):
        _tl.s = requests.Session()
    return _tl.s


def _resolve(h, refresh=False):
    u = hf_hub_url(h["repo"], h["fn"], revision=h["rev"])
    with _cdn_lock:
        if refresh or u not in _cdn:
            r = _sess().get(u, headers={"Range": "bytes=0-0"}, allow_redirects=True, timeout=120)
            if r.status_code != 206:
                raise IOError(f"resolve {u}: status {r.status_code}")
            _cdn[u] = r.url
        return _cdn[u]


def _get_s(h, lo, hi, tries=6):
    err = ""
    for i in range(tries):
        try:
            r = _sess().get(_resolve(h, refresh=i > 0), headers={"Range": f"bytes={lo}-{hi}"}, timeout=300)
            if r.status_code == 206 and len(r.content) == hi - lo + 1:
                return r.content
            err = f"status {r.status_code} len {len(r.content)} want {hi-lo+1}"   # e.g. an expired signed URL
        except requests.RequestException as e:
            err = repr(e)
        time.sleep(2 ** i)
    raise IOError(f"range fetch failed {h['fn']}@{h['rev']} {lo}-{hi}: {err}")


def _decode(raw, t):
    arr = np.frombuffer(raw, dtype=DT[t["dtype"]]).reshape(t["shape"])
    if t["dtype"] == "BF16":
        arr = (arr.astype(np.uint32) << 16).view(np.float32)
    return arr


def fetch_many(idx, names, tensors_in_flight=4, chunk=8 * 2 ** 20):
    """Yield (name, array, dtype) for `names`, up to `tensors_in_flight` tensors downloading at once, each split into
    `chunk` pieces. Memory is bounded by the tensors in flight. Order follows `names`."""
    from concurrent.futures import ThreadPoolExecutor
    check_stop()
    pieces = ThreadPoolExecutor(8)

    def one(name):
        h = idx[name]; t = h["tensors"][name]; a, b = t["data_offsets"]
        lo, nb = h["data_start"] + a, b - a
        raw = b"".join(pieces.map(lambda o: _get_s(h, lo + o, lo + min(o + chunk, nb) - 1), range(0, nb, chunk)))
        return name, _decode(raw, t), t["dtype"]

    with ThreadPoolExecutor(tensors_in_flight) as ex:
        futs = [ex.submit(one, n) for n in names]
        for f in futs:
            yield f.result()
            check_stop()
    pieces.shutdown()


def download_file(repo, fn, rev, dest, chunk=16 * 2 ** 20, threads=8):
    """Download one HF file to `dest` by parallel range requests (keep-alive, CDN URL resolved once), each piece written
    at its own offset (os.pwrite) in ONE process -- not the xargs-style shared-path corruption pattern. Size and LFS
    sha256 are verified before returning; on any mismatch the file is deleted and IOError raised. No xet cache is used."""
    import os, hashlib
    from concurrent.futures import ThreadPoolExecutor
    from huggingface_hub import HfApi
    check_stop()
    info = HfApi().model_info(repo, revision=rev, files_metadata=True)
    sib = [x for x in info.siblings if x.rfilename == fn][0]
    size, sha = sib.size, (sib.lfs.sha256 if sib.lfs else None)
    h = {"repo": repo, "fn": fn, "rev": rev}
    dest = Path(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(dest, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.ftruncate(fd, size)
        def piece(o):
            b = _get_s(h, o, min(o + chunk, size) - 1)
            os.pwrite(fd, b, o)
        with ThreadPoolExecutor(threads) as ex:
            list(ex.map(piece, range(0, size, chunk)))
        os.fsync(fd)
    finally:
        os.close(fd)
    hs = hashlib.sha256()
    with open(dest, "rb") as f:
        for blk in iter(lambda: f.read(64 * 2 ** 20), b""):
            hs.update(blk)
    if dest.stat().st_size != size or (sha and hs.hexdigest() != sha):
        dest.unlink(missing_ok=True)
        raise IOError(f"download verify failed {repo}/{fn}@{rev}")
    return dest


def evict(path):
    import os
    fd = os.open(path, os.O_RDONLY)
    try:
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
    finally:
        os.close(fd)


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
    raw = _get_parallel(url, h["data_start"] + a, h["data_start"] + b - 1)
    arr = np.frombuffer(raw, dtype=DT[t["dtype"]]).reshape(t["shape"])
    if t["dtype"] == "BF16":
        arr = (arr.astype(np.uint32) << 16).view(np.float32)
    return arr, t["dtype"]
