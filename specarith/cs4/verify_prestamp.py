"""Verify a route (a) OpenTimestamps receipt without a local Bitcoin node: the pre-decode manifest (round 47; default)
or, with an argument, another manifest such as the seal's (round 48: python verify_prestamp.py SEAL).

ots verify needs bitcoind; this does the same comparison by hand: `ots info` replays the receipt's operations from the
manifest's sha256 to each Bitcoin merkle root, and each root must equal the block header's merkle root as served by two
independent explorers (blockstream.info, mempool.space). Also checks that the receipt commits to the manifest's sha256
and that the manifest's hashes hold: for the pre-decode manifest, its prediction hash is the prediction file's; for the
seal manifest, every listed path's sha256 is that of the blob at tag route-a-seal and the tag object is the listed one.
Writes timestamps/<manifest stem>_VERIFY.json (ROUTE_A_PRESTAMP_VERIFY.json for the default).
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
SEAL_MODE = len(sys.argv) > 1 and sys.argv[1] == "SEAL"
MANIFEST = os.path.join(TS, "ROUTE_A_SEAL_STAMP_2026-10-15.txt" if SEAL_MODE else "ROUTE_A_PRESTAMP_2026-10-14.txt")
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
ok = dict(receipt_commits_to_manifest=digest == sha(MANIFEST))
if SEAL_MODE:
    def git(*a):
        return subprocess.run(["git", *a], cwd=HERE, capture_output=True, check=True).stdout
    pairs = re.findall(r"(specarith/\S+)\s*\n\s*sha256 ([0-9a-f]{64})", man)
    pred_in_manifest = dict(pairs)["specarith/cs4/results/route_a_zeta.json"]
    ok["manifest_hashes_match_tag"] = len(pairs) == 6 and all(
        hashlib.sha256(git("show", f"route-a-seal:{p}")).hexdigest() == h for p, h in pairs)
    ok["tag_object_matches"] = re.search(r"object ([0-9a-f]{40})", man).group(1) == git("rev-parse", "route-a-seal").decode().strip()
else:
    pred_in_manifest = re.search(r"prediction file at the tag\s+\S+\s*\n\s*sha256 ([0-9a-f]{64})", man).group(1)
ok.update(prediction_matches_manifest=pred_in_manifest == sha(PRED), bitcoin_attested=len(att) >= 1,
          all_attestations_verify=bool(att) and all(a["verified"] for a in att))
earliest = min(att, key=lambda a: a["height"]) if att else None
out = dict(manifest=os.path.relpath(MANIFEST, HERE), manifest_sha256=sha(MANIFEST), receipt=os.path.relpath(RECEIPT, HERE),
           receipt_sha256=sha(RECEIPT), prediction_sha256_in_manifest=pred_in_manifest,
           attestations=sorted(att, key=lambda a: a["height"]), calendars=calendars,
           earliest=dict(height=earliest["height"], block_hash=earliest["block_hash"], time_utc=earliest["time_utc"])
           if earliest else None,
           method="ots info merkle roots vs block headers from two explorers (no local Bitcoin node for ots verify)",
           checks=ok)
stem = "ROUTE_A_SEAL_STAMP" if SEAL_MODE else "ROUTE_A_PRESTAMP"
json.dump(out, open(os.path.join(TS, f"{stem}_VERIFY.json"), "w"), indent=1)
for a in out["attestations"]:
    print(f"block {a['height']} {a['block_hash'][:20]}… {a['time_utc']}  merkle root matches both explorers: {a['verified']}")
print("calendars:", calendars)
print(json.dumps(ok))
sys.exit(0 if all(ok.values()) else 1)
