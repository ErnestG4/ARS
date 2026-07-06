"""
cross_substrate/crcns_client.py — minimal authenticated CRCNS download client (creds from ~/.netrc).

CRCNS download = POST to portal.nersc.gov/.../index.php with username/password/fn/submit='Login'.
A directory fn returns an HTML listing; a file fn returns the bytes. Reads creds from netrc machine
'crcns.org' (never echoed). Sequential + size-verify (NO parallel-curl — burned in Phase 24).

API: client = CRCNS(); client.listdir("hc-3") -> [(name, size_or_None)]; client.download("hc-3/x", dest).
"""
from __future__ import annotations

import netrc
import os
import re
import time

import requests

URL = "https://portal.nersc.gov/project/crcns/download/index.php"
_LISTING = re.compile(r'<a href="[^"]*?/([^"/]+)">([^<]+)</a>(?:\s*\((\d+)\))?')


class CRCNS:
    def __init__(self, machine="crcns.org"):
        n = netrc.netrc(os.path.expanduser("~/.netrc"))
        self.user, _, self.pw = n.authenticators(machine)
        self.s = requests.Session()

    def _post(self, fn, stream=False):
        return self.s.post(URL, data=dict(username=self.user, password=self.pw, fn=fn,
                                          submit="Login"), timeout=300, stream=stream)

    def listdir(self, fn):
        r = self._post(fn)
        if r.status_code != 200:
            raise RuntimeError(f"listdir {fn}: {r.status_code} {r.text[:150]}")
        if "Invalid user name" in r.text:
            raise RuntimeError("CRCNS auth rejected")
        out = []
        body = r.text[r.text.find("Contents of"):]
        for name, label, size in _LISTING.findall(body):
            out.append((name, int(size) if size else None))
        return out

    def download(self, fn, dest, expected_size=None, retries=3):
        """Stream a file to dest; size-verify. Skips if already present at expected size."""
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if expected_size and os.path.exists(dest) and os.path.getsize(dest) == expected_size:
            return dest, "cached"
        last = None
        for attempt in range(retries):
            try:
                r = self._post(fn, stream=True)
                if r.status_code != 200 or "Invalid user name" in (r.text[:200] if not r.raw else ""):
                    last = f"{r.status_code} {r.text[:120]}"
                    time.sleep(2); continue
                tmp = dest + ".part"
                n = 0
                with open(tmp, "wb") as fh:
                    for chunk in r.iter_content(1 << 20):
                        if chunk:
                            fh.write(chunk); n += len(chunk)
                if expected_size and n != expected_size:
                    last = f"size mismatch got {n} want {expected_size}"
                    os.remove(tmp); time.sleep(2); continue
                os.replace(tmp, dest)
                return dest, n
            except Exception as e:
                last = f"{type(e).__name__}: {e}"; time.sleep(3)
        raise RuntimeError(f"download {fn} failed after {retries}: {last}")


if __name__ == "__main__":
    import sys
    c = CRCNS()
    if len(sys.argv) > 1 and sys.argv[1] == "--ls":
        for name, size in c.listdir(sys.argv[2]):
            print(f"  {('DIR ' if size is None else f'{size:>12d}')}  {name}")
