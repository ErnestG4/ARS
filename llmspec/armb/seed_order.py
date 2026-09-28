#!/usr/bin/env python
"""seed_order.py -- reconstruct PolyPythia per-seed training batches (GPT-NeoX GPT2Dataset order).

Source of truth: EleutherAI/pile-preshuffled-seeds `dataset.py` (downloaded to
~/llmspec_armb/data/dataset.py, 11113 bytes). This module follows it exactly:

  * MMapIndexedDataset.Index.__init__ (dataset.py L88-125): the .idx header is
    9-byte magic, <Q version, <B dtype code (8 -> uint16), <Q len, <Q doc_count,
    then int32 sizes[len], int64 pointers[len] (BYTE offsets into the .bin), int64 doc_idx.
  * MMapIndexedDataset.get (L203-214): tokens of document d, from token `offset`,
    `length` tokens, live at bytes [pointers[d] + 2*offset, + 2*length) of the .bin.
  * GPT2Dataset.__getitem__ (L259-282):
        idx = shuffle_idx[i]
        (f, off_f) = sample_idx[idx]; (l, off_l) = sample_idx[idx + 1]
        if f == l:  doc_idx[f][off_f : off_l + 1]
        else:       doc_idx[f][off_f:] ++ doc_idx[f+1..l-1] (whole) ++ doc_idx[l][: off_l + 1]
    -> 2049 tokens per sample (seq_len 2048 + 1).
  * read_dataset (L285-303): the maps address prefix "pile_20B_tokenizer_text_document"
    (.idx + .bin); "Num batches == len(ds) / 1024" -> global sample i is in training
    step k = i // 1024 + 1 (batch 1024).

The .bin addressed is the UNSHUFFLED tokenized Pile, 664,230,651,068 bytes (= last
pointer + 2*last size of the .idx), which is on HF only as
EleutherAI/pythia_pile_idxmaps: pile_20B_tokenizer_text_document-000NN-of-00132.bin
(133 shards of 5e9 bytes, the last 4,230,651,068; same .idx sha256 d0119215...).
It is read here with HTTP range requests; nothing large is downloaded.

Known-answer reference: EleutherAI/pile-standard-pythia-preshuffled document-000NN-of-00020.bin
(21 shards, 30e9 bytes except the last) whose document.idx holds 146,432,000 docs of
exactly 2049 tokens with pointer i*4098, i.e. seed-1234 training samples in order.

CLI:
  python seed_order.py check [nsteps]           # seed0 (1234) steps 1..nsteps vs preshuffled
  python seed_order.py materialise SEED K0 K1   # steps K0..K1 -> seed{SEED}_batches/step{k:05d}.npy
  python seed_order.py manifest SEED            # (re)write seed{SEED}_batches/MANIFEST.json
"""
import asyncio
import glob
import hashlib
import json
import os
import struct
import sys
import time
import urllib.parse as up

import httpx
import numpy as np

DATA = os.path.expanduser("~/llmspec_armb/data")
IDX_PATH = os.path.join(DATA, "pile_20B_tokenizer_text_document.idx")
SEQ = 2049
BATCH = 1024
RAW_REPO = "EleutherAI/pythia_pile_idxmaps"
RAW_SHARD = 5_000_000_000
RAW_NSHARD = 133
RAW_TOTAL = 664_230_651_068
PRE_REPO = "EleutherAI/pile-standard-pythia-preshuffled"
PRE_SHARD = 30_000_000_000
PRE_NSHARD = 21
PRE_TOTAL = 600_078_336_000
CONC = 128


def raw_name(s):
    return f"pile_20B_tokenizer_text_document-{s:05d}-of-00132.bin"


def pre_name(s):
    return f"document-{s:05d}-of-00020.bin"


# ---------------------------------------------------------------- index (dataset.py L88-125)
_IDX = None


def base_index():
    global _IDX
    if _IDX is None:
        with open(IDX_PATH, "rb") as fh:
            assert fh.read(9) == b"MMIDIDX\x00\x00"
            assert struct.unpack("<Q", fh.read(8)) == (1,)
            (code,) = struct.unpack("<B", fh.read(1))
            assert code == 8, code  # uint16
            n = struct.unpack("<Q", fh.read(8))[0]
            struct.unpack("<Q", fh.read(8))
            off = fh.tell()
        mm = np.memmap(IDX_PATH, mode="r", order="C")
        sizes = np.frombuffer(mm, dtype=np.int32, count=n, offset=off)
        ptrs = np.frombuffer(mm, dtype=np.int64, count=n, offset=off + 4 * n)
        assert int(ptrs[-1]) + 2 * int(sizes[-1]) == RAW_TOTAL
        _IDX = (sizes, ptrs)
    return _IDX


_MAPS = {}


def seed_maps(seed):
    """seed 0 -> seed0/*_1234s_*, seed N -> seedN/*_Ns_* (read_dataset L292-294)."""
    if seed not in _MAPS:
        d = os.path.join(DATA, f"seed{seed}")
        (p,) = glob.glob(os.path.join(d, "*_doc_idx.npy"))
        pre = p[: -len("_doc_idx.npy")]
        m = tuple(np.load(pre + suf, allow_pickle=False, mmap_mode="r")
                  for suf in ("_doc_idx.npy", "_sample_idx.npy", "_shuffle_idx.npy"))
        _MAPS[seed] = m
    return _MAPS[seed]


def sample_pieces(seed, i):
    """GPT2Dataset.__getitem__ (dataset.py L259-280) as a list of (doc, tok_offset, tok_len)."""
    doc_idx, sample_idx, shuffle_idx = seed_maps(seed)
    sizes, _ = base_index()
    idx = int(shuffle_idx[i])
    f, off_f = int(sample_idx[idx][0]), int(sample_idx[idx][1])
    l, off_l = int(sample_idx[idx + 1][0]), int(sample_idx[idx + 1][1])
    if f == l:
        return [(int(doc_idx[f]), off_f, off_l - off_f + 1)]
    d0 = int(doc_idx[f])
    pieces = [(d0, off_f, int(sizes[d0]) - off_f)]
    for j in range(f + 1, l):
        dj = int(doc_idx[j])
        pieces.append((dj, 0, int(sizes[dj])))
    pieces.append((int(doc_idx[l]), 0, off_l + 1))
    return pieces


def step_plan(seed, step):
    """(1024 samples) -> list of (sample_row, token_col, global_byte, nbytes)."""
    _, ptrs = base_index()
    plan = []
    for r, i in enumerate(range((step - 1) * BATCH, step * BATCH)):
        col = 0
        for d, off, ln in sample_pieces(seed, i):
            if ln > 0:
                plan.append((r, col, int(ptrs[d]) + 2 * off, 2 * ln))
            col += ln
        assert col == SEQ, (seed, step, i, col)
    return plan


# ---------------------------------------------------------------- HTTP range reader
class Fetcher:
    def __init__(self, conc=CONC):
        self.conc = conc
        self.urls = {}  # (repo, fname) -> (signed_url, expires)
        self.client = None
        self.sem = None
        self.nreq = 0

    async def __aenter__(self):
        lim = httpx.Limits(max_connections=self.conc, max_keepalive_connections=self.conc)
        self.client = httpx.AsyncClient(http2=True, limits=lim, timeout=120)
        self.sem = asyncio.Semaphore(self.conc)
        self.lock = asyncio.Lock()
        return self

    async def __aexit__(self, *a):
        await self.client.aclose()

    async def _signed(self, repo, fname, force=False):
        key = (repo, fname)
        u = self.urls.get(key)
        if u is not None and not force and u[1] - time.time() >= 300:
            return u[0]
        async with self.lock:
            u = self.urls.get(key)
            if u is not None and not force and u[1] - time.time() >= 300:
                return u[0]
            r = await self.client.get(f"https://huggingface.co/datasets/{repo}/resolve/main/{fname}",
                                      headers={"Range": "bytes=0-0"}, follow_redirects=False)
            assert r.status_code in (301, 302, 307), (r.status_code, fname)
            loc = r.headers["location"]
            exp = up.parse_qs(up.urlparse(loc).query).get("Expires", [str(int(time.time()) + 3000)])[0]
            u = (loc, int(exp))
            self.urls[key] = u
            return u[0]

    async def get(self, repo, fname, a, n):
        last = None
        for attempt in range(10):
            try:
                async with self.sem:
                    url = await self._signed(repo, fname, force=attempt > 0 and last == 403)
                    r = await self.client.get(url, headers={"Range": f"bytes={a}-{a + n - 1}"})
                    self.nreq += 1
                if r.status_code == 206 and len(r.content) == n:
                    return r.content
                last = r.status_code
            except (httpx.HTTPError, AssertionError) as e:
                last = repr(e)
            await asyncio.sleep(min(60, 2 ** attempt))
        raise RuntimeError(f"range read failed {fname} {a}+{n}: {last}")

    async def read_concat(self, repo, name_fn, shard_bytes, g, n):
        """Read n bytes at global offset g of the concatenated shards (split at shard edges)."""
        out, parts = [], []
        while n > 0:
            s, o = divmod(g, shard_bytes)
            k = min(n, shard_bytes - o)
            parts.append((s, o, k))
            g += k
            n -= k
        bufs = await asyncio.gather(*[self.get(repo, name_fn(s), o, k) for s, o, k in parts])
        return b"".join(bufs)


async def _reconstruct(fx, seed, step):
    plan = step_plan(seed, step)
    out = np.zeros((BATCH, SEQ), dtype=np.uint16)
    bufs = await asyncio.gather(*[fx.read_concat(RAW_REPO, raw_name, RAW_SHARD, g, nb)
                                  for _, _, g, nb in plan])
    for (r, c, _, nb), b in zip(plan, bufs):
        out[r, c:c + nb // 2] = np.frombuffer(b, dtype=np.uint16)
    return out


async def _preshuffled(fx, step):
    """Pythia standard (seed 1234) batch `step`: bytes [(step-1)*1024*4098, step*1024*4098)."""
    g0 = (step - 1) * BATCH * SEQ * 2
    chunk = 64 * SEQ * 2
    bufs = await asyncio.gather(*[fx.read_concat(PRE_REPO, pre_name, PRE_SHARD, g0 + j * chunk, chunk)
                                  for j in range(BATCH // 64)])
    return np.frombuffer(b"".join(bufs), dtype=np.uint16).reshape(BATCH, SEQ).copy()


def reconstruct(seed, step):
    """Training step `step` (1-based) of PolyPythia seed `seed` -> (1024, 2049) uint16."""
    async def go():
        async with Fetcher() as fx:
            return await _reconstruct(fx, seed, step)
    return asyncio.run(go())


# ---------------------------------------------------------------- CLI tasks
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 24), b""):
            h.update(blk)
    return h.hexdigest()


async def _check(nsteps):
    n_match = n_tot = 0
    first = None
    async with Fetcher() as fx:
        for k in range(1, nsteps + 1):
            a, b = await asyncio.gather(_reconstruct(fx, 0, k), _preshuffled(fx, k))
            eq = np.all(a == b, axis=1)
            n_match += int(eq.sum())
            n_tot += BATCH
            if first is None and not eq.all():
                r = int(np.argmin(eq))
                col = int(np.argmax(a[r] != b[r]))
                first = dict(step=k, row=r, sample=(k - 1) * BATCH + r, col=col,
                             recon=a[r, max(0, col - 3):col + 4].tolist(),
                             ref=b[r, max(0, col - 3):col + 4].tolist())
            print(f"step {k}: {int(eq.sum())}/1024 match; cum {n_match}/{n_tot}; req {fx.nreq}", flush=True)
    res = dict(n_match=n_match, n_total=n_tot, first_mismatch=first, PASS=(n_match == n_tot))
    print("RESULT", json.dumps(res), flush=True)
    return res


def _outdir(seed):
    d = os.path.join(DATA, f"seed{seed}_batches")
    os.makedirs(d, exist_ok=True)
    return d


async def _materialise(seed, k0, k1, par=4):
    od = _outdir(seed)
    log = os.path.join(od, "steps.jsonl")
    done = {}
    if os.path.exists(log):
        for line in open(log):
            j = json.loads(line)
            done[j["step"]] = j
    todo = []
    for k in range(k0, k1 + 1):
        p = os.path.join(od, f"step{k:05d}.npy")
        if k in done and os.path.exists(p) and os.path.getsize(p) == done[k]["bytes"] \
                and sha256_file(p) == done[k]["sha256"]:
            continue
        todo.append(k)
    print(f"seed {seed}: {len(todo)} steps to do of {k1 - k0 + 1}", flush=True)
    t0 = time.time()
    async with Fetcher() as fx:
        q = asyncio.Queue()
        for k in todo:
            q.put_nowait(k)
        cnt = [0]

        async def worker():
            while not q.empty():
                k = q.get_nowait()
                arr = await _reconstruct(fx, seed, k)
                assert arr.shape == (BATCH, SEQ) and arr.dtype == np.uint16
                p = os.path.join(od, f"step{k:05d}.npy")
                np.save(p + ".tmp.npy", arr)
                os.replace(p + ".tmp.npy", p)
                rec = dict(step=k, file=os.path.basename(p), bytes=os.path.getsize(p), sha256=sha256_file(p))
                with open(log, "a") as fh:
                    fh.write(json.dumps(rec) + "\n")
                cnt[0] += 1
                el = time.time() - t0
                print(f"step {k} done; {cnt[0]}/{len(todo)} in {el:.0f}s; "
                      f"ETA {el / cnt[0] * (len(todo) - cnt[0]) / 3600:.2f} h; req {fx.nreq}", flush=True)

        await asyncio.gather(*[worker() for _ in range(par)])


def write_manifest(seed):
    od = _outdir(seed)
    files = sorted(glob.glob(os.path.join(od, "step*.npy")))
    rec = {}
    for p in files:
        rec[os.path.basename(p)] = dict(bytes=os.path.getsize(p), sha256=sha256_file(p))
    src = {}
    for p in [IDX_PATH] + sorted(glob.glob(os.path.join(DATA, f"seed{seed}", "*.npy"))):
        src[os.path.relpath(p, DATA)] = dict(bytes=os.path.getsize(p), sha256=sha256_file(p))
    man = dict(
        description=f"PolyPythia seed {seed} training batches, steps as step{{k:05d}}.npy, "
                    f"uint16 (1024, 2049); step k = global samples [(k-1)*1024, k*1024).",
        generator="seed_order.py", generator_sha256=sha256_file(os.path.abspath(__file__)),
        index_maps_repo="EleutherAI/pile-preshuffled-seeds", token_bin_repo=RAW_REPO,
        token_bin=dict(shards=[raw_name(s) for s in range(RAW_NSHARD)], total_bytes=RAW_TOTAL,
                       shard_bytes=RAW_SHARD),
        source_files=src, n_files=len(rec), files=rec, created=time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    with open(os.path.join(od, "MANIFEST.json"), "w") as fh:
        json.dump(man, fh, indent=1)
    print(f"MANIFEST: {len(rec)} files", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "check":
        res = asyncio.run(_check(int(sys.argv[2]) if len(sys.argv) > 2 else 50))
        sys.exit(0 if res["PASS"] else 1)
    elif cmd == "materialise":
        seed, k0, k1 = map(int, sys.argv[2:5])
        asyncio.run(_materialise(seed, k0, k1))
        write_manifest(seed)
    elif cmd == "manifest":
        write_manifest(int(sys.argv[2]))
    else:
        raise SystemExit(__doc__)
