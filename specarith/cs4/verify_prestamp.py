"""Verify the route (a) pre-decode OpenTimestamps receipt (round 47) without a local Bitcoin node.

ots verify needs bitcoind; this does the same comparison by hand: `ots info` replays the receipt's operations from the
manifest's sha256 to each Bitcoin merkle root, and each root must equal the block header's merkle root as served by two
independent explorers (blockstream.info, mempool.space). Also checks that the receipt commits to the manifest's sha256
and that the manifest's prediction hash is the prediction file's. Writes timestamps/ROUTE_A_PRESTAMP_VERIFY.json.
Exit 0 only if at least one Bitcoin attestation verifies on both explorers and every attestation present matches.
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
MANIFEST = os.path.join(TS, "ROUTE_A_PRESTAMP_2026-10-14.txt")
RECEIPT = MANIFEST + ".ots"
PRED = os.path.join(HERE, "results", "route_a_zeta.json")
OTS = os.path.expanduser("~/.local/ots-venv/bin/ots")
EXPLORERS = ("https://blockstream.info/api", "https://mempool.space/api")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode()


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
man = open(MANIFEST).read()
pred_in_manifest = re.search(r"prediction file at the tag\s+\S+\s*\n\s*sha256 ([0-9a-f]{64})", man).group(1)
ok = dict(receipt_commits_to_manifest=digest == sha(MANIFEST), prediction_matches_manifest=pred_in_manifest == sha(PRED),
          bitcoin_attested=len(att) >= 1, all_attestations_verify=bool(att) and all(a["verified"] for a in att))
earliest = min(att, key=lambda a: a["height"]) if att else None
out = dict(manifest=os.path.relpath(MANIFEST, HERE), manifest_sha256=sha(MANIFEST), receipt=os.path.relpath(RECEIPT, HERE),
           receipt_sha256=sha(RECEIPT), prediction_sha256_in_manifest=pred_in_manifest,
           attestations=sorted(att, key=lambda a: a["height"]), calendars=calendars,
           earliest=dict(height=earliest["height"], block_hash=earliest["block_hash"], time_utc=earliest["time_utc"])
           if earliest else None,
           method="ots info merkle roots vs block headers from two explorers (no local Bitcoin node for ots verify)",
           checks=ok)
json.dump(out, open(os.path.join(TS, "ROUTE_A_PRESTAMP_VERIFY.json"), "w"), indent=1)
for a in out["attestations"]:
    print(f"block {a['height']} {a['block_hash'][:20]}… {a['time_utc']}  merkle root matches both explorers: {a['verified']}")
print("calendars:", calendars)
print(json.dumps(ok))
sys.exit(0 if all(ok.values()) else 1)
