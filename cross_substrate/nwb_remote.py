"""
cross_substrate/nwb_remote.py — stream-read only the units/behavior tables of huge raw-ecephys NWBs
over HTTP range requests, without downloading the (30-70 GB) raw voltage traces.

h5py accepts any binary file-like object exposing read/seek/tell. HttpRangeFile implements that against
a DANDI S3 asset using urllib Range headers + a small LRU block cache. This is the stdlib-only sibling of
the fsspec remote-HDF5 region-scan discipline (no fsspec/remfile/pip needed; venv_allen311 has h5py only).

resolve_dandi_url(dandiset, asset_id) -> final S3 url (follows the /download/ 302).
open_remote_nwb(url) -> h5py.File backed by HttpRangeFile.
"""
from __future__ import annotations

import io
import urllib.request
from collections import OrderedDict

import h5py

UA = "ars-nwb-remote/1.0 (research; range-reads units table only)"


def resolve_dandi_url(dandiset: str, asset_id: str, version: str = "draft") -> str:
    """Resolve the DANDI /download/ endpoint (302 -> public S3 url). GET (HEAD is 403 on the bucket)."""
    dl = (f"https://api.dandiarchive.org/api/dandisets/{dandiset}"
          f"/versions/{version}/assets/{asset_id}/download/")
    req = urllib.request.Request(dl, headers={"User-Agent": UA, "Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl()


class HttpRangeFile(io.RawIOBase):
    """Read-only seekable file-like over HTTP range requests, with a block cache (for HDF5 metadata)."""

    def __init__(self, url: str, block: int = 1 << 20, max_blocks: int = 512, size: int | None = None):
        self.url = url
        self.block = block
        self._pos = 0
        self._cache: "OrderedDict[int, bytes]" = OrderedDict()
        self._max_blocks = max_blocks
        self._size = size if size is not None else self._probe_size()

    def _probe_size(self) -> int:
        # range GET 0-0 -> Content-Range: bytes 0-0/TOTAL (HEAD is 403 on the bucket)
        req = urllib.request.Request(self.url, headers={"User-Agent": UA, "Range": "bytes=0-0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            cr = r.headers.get("Content-Range")
            if cr:
                return int(cr.split("/")[-1])
            cl = r.headers.get("Content-Length")
            return int(cl)

    def _fetch_block(self, idx: int) -> bytes:
        if idx in self._cache:
            self._cache.move_to_end(idx)
            return self._cache[idx]
        start = idx * self.block
        end = min(start + self.block, self._size) - 1
        if end < start:
            return b""
        req = urllib.request.Request(
            self.url, headers={"User-Agent": UA, "Range": f"bytes={start}-{end}"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                break
            except Exception:
                if attempt == 3:
                    raise
        self._cache[idx] = data
        self._cache.move_to_end(idx)
        if len(self._cache) > self._max_blocks:
            self._cache.popitem(last=False)
        return data

    # --- io.RawIOBase interface ---
    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self._pos

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self._pos = offset
        elif whence == io.SEEK_CUR:
            self._pos += offset
        elif whence == io.SEEK_END:
            self._pos = self._size + offset
        return self._pos

    def read(self, size=-1):
        if size is None or size < 0:
            size = self._size - self._pos
        size = min(size, self._size - self._pos)
        if size <= 0:
            return b""
        out = bytearray()
        pos = self._pos
        while size > 0:
            bidx = pos // self.block
            off = pos - bidx * self.block
            blk = self._fetch_block(bidx)
            take = min(size, len(blk) - off)
            if take <= 0:
                break
            out += blk[off:off + take]
            pos += take
            size -= take
        self._pos = pos
        return bytes(out)

    def readinto(self, b):
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


def open_remote_nwb(url: str, **kw) -> h5py.File:
    rf = HttpRangeFile(url, **kw)
    return h5py.File(rf, "r")


def open_dandi_asset(dandiset: str, asset_id: str, size: int | None = None,
                     version: str = "draft", **kw) -> h5py.File:
    url = resolve_dandi_url(dandiset, asset_id, version)
    return open_remote_nwb(url, size=size, **kw)
