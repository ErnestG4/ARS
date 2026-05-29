"""
cross_substrate/crcns_fetch.py — download hc-3 session tarballs, extract only the small spike/position/
config files (.clu/.res/.whl/.xml/.nrs/.par), delete the tarball. Sequential + size-verify (no parallel-curl).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crcns_client import CRCNS

RAW = "/home/combust/fmexplorer/crcns_cache/raw"
SESS = "/home/combust/fmexplorer/crcns_cache/sessions"
COORD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coordinates")
KEEP = ["*.clu.*", "*.res.*", "*.whl", "*.xml", "*.nrs", "*.par", "*.states*", "*.sts.*"]


def _load_picks():
    pj = os.path.join(COORD, "crcns_picks.json")
    if os.path.exists(pj):
        return [(o["topdir"], o["session"], o.get("size")) for o in json.load(open(pj))]
    return []


PICKS = _load_picks()


def main():
    c = CRCNS()
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(SESS, exist_ok=True)
    for td, se, approx in PICKS:
        sdir = os.path.join(SESS, td, se)
        if os.path.isdir(sdir) and any(f.endswith(tuple(".res." + str(i) for i in range(1, 17)))
                                       or ".res." in f for f in os.listdir(sdir)):
            print(f"{se}: already extracted, skip"); continue
        # exact size from portal listing (approx given is rounded)
        try:
            entries = dict((n, s) for n, s in c.listdir(f"hc-3/{td}"))
            fn = f"{se}.tar.gz"
            size = entries.get(fn)
        except Exception as e:
            print(f"{se}: listdir failed {e}; using approx"); size = None
        tar = os.path.join(RAW, f"{se}.tar.gz")
        print(f"{se}: downloading ({(size or approx)/1e6:.0f} MB)...", flush=True)
        try:
            c.download(f"hc-3/{td}/{se}.tar.gz", tar, expected_size=size)
        except Exception as e:
            print(f"{se}: DOWNLOAD FAILED {e}"); continue
        # extract small files
        cmd = ["tar", "xzf", tar, "-C", SESS, "--wildcards", "--no-anchored"] + KEEP
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"{se}: extract warn: {r.stderr[:200]}")
        os.remove(tar)
        nfiles = len(os.listdir(sdir)) if os.path.isdir(sdir) else 0
        print(f"{se}: extracted {nfiles} files, tarball deleted", flush=True)
    print("DONE fetch")


if __name__ == "__main__":
    main()
