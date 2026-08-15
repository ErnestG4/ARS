"""Survey arc D0: acquisition + provenance.  COMMITTED GENERATOR of
survey/MANIFEST.json (brief §3 D0: 'D0 is a cell, not a footnote').

Sealed at D0 (open questions resolved, derivations below):
  Q1  Tracer = LRG, NGC, slices 0.6-0.8 (primary) and 0.4-0.6 (comparison
      row).  Power seal from the released nz files (committed here as data):
      682,137 / 438,894 objects, 196.9 / 126.7 per deg^2, ~15.7k per 10x10
      tile, class-separation >= 93 sigma at every candidate R under a
      conservative w(theta) amplitude (A=0.02 at 1 deg, slope -0.7).  BGS
      fallback dry-run DISCHARGED: loader ran, power row computed (4x denser,
      also overpowered) — contingency proven executable, not needed.
  Q3  Catalog version v1.5 (clustering products present and current); NGC
      only (3755.8 deg^2, 3464.9 effective — contiguous).
  Randoms subset (numeric, sealed): 8 of 18 files (indices 0-7).  Derivation:
      randoms Z are data-shuffled, so in-slice density scales with the data's
      slice fraction; per file ~= 2500/deg^2 * slice_fraction(~0.46) ~= 6.4x
      data density.  Two DISJOINT 4-file splits (even indices -> mask-KAG
      half, odd -> measurement-null half; tripwire 2) give ~25x data density
      per split — RR shot noise negligible against DD.  Downloading all 18
      buys nothing the budget needs (9.9 GB saved).
Sequential downloads with size verification (parallel-curl corruption rule);
SHA256 manifest with row counts read from FITS headers.
"""

import hashlib
import json
import os
import subprocess
import sys

SV = "/home/combust/fmexplorer/criticality_tool/survey"
BASE = ("https://data.desi.lbl.gov/public/dr1/survey/catalogs/dr1/LSS/iron/"
        "LSScats/v1.5")

FILES = (["LRG_NGC_clustering.dat.fits"]
         + [f"LRG_NGC_{i}_clustering.ran.fits" for i in range(8)]
         + ["LRG_NGC_nz.txt", "BGS_BRIGHT_NGC_nz.txt"])

RANDOMS_SPLIT = dict(kag_half=[0, 2, 4, 6], null_half=[1, 3, 5, 7])


def remote_size(url):
    out = subprocess.run(["curl", "-sIL", "--max-time", "60", url],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.lower().startswith("content-length"):
            return int(line.split(":")[1])
    return None


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def fits_nrows(path):
    """NAXIS2 of HDU1 from the header block — no FITS library needed."""
    with open(path, "rb") as f:
        f.seek(2880)                      # skip primary HDU header block
        block = f.read(2880 * 4)
    for i in range(0, len(block) - 80, 80):
        card = block[i:i + 80].decode("ascii", "replace")
        if card.startswith("NAXIS2"):
            return int(card.split("=")[1].split("/")[0])
    return None


def main():
    manifest = dict(base_url=BASE, version="v1.5", tracer="LRG", cap="NGC",
                    randoms_split=RANDOMS_SPLIT, files={})
    for fn in FILES:
        path = f"{SV}/{fn}"
        url = f"{BASE}/{fn}"
        want = remote_size(url)
        have = os.path.getsize(path) if os.path.exists(path) else -1
        if have != want:
            print(f"downloading {fn} ({(want or 0)/1e6:.0f} MB)...", flush=True)
            subprocess.run(["curl", "-sL", "--max-time", "3600",
                            "-o", path, url], check=True)
            got = os.path.getsize(path)
            assert want is None or got == want, \
                f"SIZE MISMATCH {fn}: {got} != {want}"
        else:
            print(f"{fn}: present, size verified", flush=True)
        entry = dict(bytes=os.path.getsize(path), sha256=sha256(path))
        if fn.endswith(".fits"):
            entry["nrows"] = fits_nrows(path)
        manifest["files"][fn] = entry
        print(f"  {fn}: {entry['bytes']} bytes, "
              f"rows={entry.get('nrows')}, sha={entry['sha256'][:12]}", flush=True)
    with open(f"{SV}/MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=1)
    print("MANIFEST written", flush=True)


if __name__ == "__main__":
    main()
