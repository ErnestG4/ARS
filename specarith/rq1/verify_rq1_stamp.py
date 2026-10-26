"""Verify the RQ1 seal's OpenTimestamps receipt without a local Bitcoin node (as specarith/cs4/verify_prestamp.py).

`ots info` replays the receipt's operations from the stamp manifest's sha256 to each Bitcoin merkle root; each root must
equal the block header's merkle root served by two independent explorers (blockstream.info, mempool.space). Also: the
receipt commits to the manifest's sha256; every path's sha256 in the manifest is that of the blob at tag rq1-seal; the
tag object is the listed one. Writes timestamps/RQ1_SEAL_STAMP_2026-10-26_VERIFY.json.
Exit 0 only if at least one Bitcoin attestation verifies on both explorers and every check holds.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(HERE, "timestamps")
MANIFEST = os.path.join(TS, "RQ1_SEAL_STAMP_2026-10-26.txt")
RECEIPT = MANIFEST + ".ots"
TAG = "rq1-seal"
OTS = os.path.expanduser("~/.local/ots-venv/bin/ots")
EXPLORERS = ("https://blockstream.info/api", "https://mempool.space/api")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode()


def git(*a):
    return subprocess.run(["git", *a], cwd=HERE, capture_output=True, check=True).stdout


info = subprocess.run([OTS, "info", RECEIPT], capture_output=True, text=True, check=True).stdout
digest = re.search(r"File sha256 hash: ([0-9a-f]{64})", info).group(1)
roots = re.findall(r"BitcoinBlockHeaderAttestation\((\d+)\)\s*\n\s*# Bitcoin block merkle root ([0-9a-f]{64})", info)
calendars = re.findall(r"PendingAttestation\('([^']+)'\)", info)
att = []
for h, root in roots:
    rec = dict(height=int(h), merkle_root=root, explorers={})
    for api in EXPLORERS:
        bh = get(f"{api}/block-height/{h}").strip()
        b = json.loads(get(f"{api}/block/{bh}"))
        rec["explorers"][api.split("/")[2]] = dict(block_hash=bh, merkle_root=b["merkle_root"], height=b["height"],
                                                    time_utc=datetime.datetime.fromtimestamp(
                                                        b["timestamp"], datetime.timezone.utc).isoformat())
    e = list(rec["explorers"].values())
    rec["verified"] = all(x["merkle_root"] == root and x["height"] == int(h) for x in e) and \
        len({x["block_hash"] for x in e}) == 1
    rec["block_hash"], rec["time_utc"] = e[0]["block_hash"], e[0]["time_utc"]
    att.append(rec)
man_b = open(MANIFEST, "rb").read()
man = man_b.decode()
pairs = re.findall(r"(specarith/\S+)\s*\n\s*sha256 ([0-9a-f]{64})", man)
ok = dict(receipt_commits_to_manifest=digest == sha(man_b),
          manifest_hashes_match_tag=len(pairs) == 12 and all(sha(git("show", f"{TAG}:{p}")) == h for p, h in pairs),
          tag_object_matches=re.search(r"object ([0-9a-f]{40})", man).group(1) == git("rev-parse", TAG).decode().strip(),
          tag_commit_matches=re.search(r"on commit ([0-9a-f]{40})", man).group(1)
          == git("rev-parse", TAG + "^{commit}").decode().strip(),
          bitcoin_attested=len(att) >= 1, all_attestations_verify=bool(att) and all(a["verified"] for a in att))
earliest = min(att, key=lambda a: a["height"]) if att else None
out = dict(manifest=os.path.relpath(MANIFEST, HERE), manifest_sha256=sha(man_b), receipt=os.path.relpath(RECEIPT, HERE),
           receipt_sha256=sha(open(RECEIPT, "rb").read()), paths_checked=len(pairs),
           attestations=sorted(att, key=lambda a: a["height"]), calendars=calendars,
           earliest=dict(height=earliest["height"], block_hash=earliest["block_hash"], time_utc=earliest["time_utc"])
           if earliest else None,
           method="ots info merkle roots vs block headers from two explorers (no local Bitcoin node for ots verify)",
           checks=ok)
json.dump(out, open(os.path.join(TS, "RQ1_SEAL_STAMP_2026-10-26_VERIFY.json"), "w"), indent=1)
for a in out["attestations"]:
    print(f"block {a['height']} {a['block_hash'][:20]}… {a['time_utc']}  merkle root matches both explorers: {a['verified']}")
print("calendars:", calendars)
print(json.dumps(ok))
sys.exit(0 if all(ok.values()) else 1)
