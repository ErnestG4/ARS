"""RQ1 pre-read archive check list (round 91): every segment file of both archives with its manifest hash, in
`sha256sum -c` format, paths as on spot under ~/tmp/claude/specarith/rq1/. Generated from the pinned manifest copies
(results/archive_zs2/MANIFEST.json aa6d15fc…, results/archive_zi/MANIFEST.json 8fd61856…; the spot manifests are
checked against the same hashes by read_pins.sha256). No segment is opened here.

  python rq1_segment_list.py > archive_segments.sha256
"""
import hashlib
import json

PINS = {"archive": ("results/archive_zs2/MANIFEST.json", "aa6d15fc67b262021f4ccda3dc9ebf6edf064bb84762fcf4ed46626ebc5722f1"),
        "archive_zi": ("results/archive_zi/MANIFEST.json", "8fd61856ea8a76c9b6fdc9f0f2e5cd6affc60d98a6ddae3e35b29d57b982d0cb")}

for d, (path, pin) in PINS.items():
    raw = open(path, "rb").read()
    assert hashlib.sha256(raw).hexdigest() == pin, path
    segs = json.loads(raw)["segments"]
    assert [s["k"] for s in segs] == list(range(len(segs))), path
    for s in segs:
        print(f"{s['sha256']}  {d}/seg_{s['k']:04d}.npy")
