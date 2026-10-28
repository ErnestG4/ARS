"""RQ1-c pre-read archive check list (RQ1C_SEAL.md §5): every segment file of the three 10¹² archives with its manifest
hash, in `sha256sum -c` format, absolute paths on spot (/mnt/data/rq1/archive_1e12_{zs2,zi,zw}). Generated from the
pinned manifest copies (§6: zs2 4895bdfa…, zi 19a3a85e…, zw f3de0c07…; the spot manifests are checked against the same
hashes by rq1c_read_pins.sha256). No segment is opened here.

  python rq1c_segment_list.py > rq1c_archive_segments.sha256
"""
import hashlib
import json

PINS = {"zs2": "4895bdfae09e2618602e89c7a4a9d9fcd62b0ef613b5c77ec2abd4fdc04afb1e",
        "zi": "19a3a85e17a5606d8d8ac9d0f86a9207aa07690f9f7f0d5781350519cb883508",
        "zw": "f3de0c0761a838059269272d59327c1f31f54004cdece9d0fdeab388bbc456f8"}

for f, pin in PINS.items():
    raw = open(f"results/archive_1e12_{f}/MANIFEST.json", "rb").read()
    assert hashlib.sha256(raw).hexdigest() == pin, f
    segs = json.loads(raw)["segments"]
    assert [s["k"] for s in segs] == list(range(len(segs))), f
    for s in segs:
        print(f"{s['sha256']}  /mnt/data/rq1/archive_1e12_{f}/seg_{s['k']:04d}.npy")
