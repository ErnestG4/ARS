"""Verify a follow-up (replication) OpenTimestamps receipt without a local Bitcoin node (round 53; verify_prestamp.py's
method): `ots info` replays the receipt from the manifest's sha256 to each Bitcoin merkle root, and each root must equal
the block header's merkle root on two independent explorers (blockstream.info, mempool.space). Also:
  - the receipt commits to the manifest's sha256;
  - every "<path>\\n  sha256 <hex>" pair in the manifest equals the sha256 of `git show <commit>:<path>`, with <commit>
    the manifest's "on commit <hex>" line;
  - every "tag <name>  object <hex>" line equals `git rev-parse <name>` (the local tag object).
Writes timestamps/<manifest stem>_VERIFY.json. Exit 0 only if at least one Bitcoin attestation verifies on both
explorers, every attestation present verifies, and every manifest check holds.

  python verify_followup_stamp.py timestamps/FOLLOWUP_PRESTAMP_2026-10-17.txt
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
OTS = os.path.expanduser("~/.local/ots-venv/bin/ots")
EXPLORERS = ("https://blockstream.info/api", "https://mempool.space/api")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode()


def git(*a):
    return subprocess.run(["git", *a], cwd=HERE, capture_output=True, check=True).stdout


def main(manifest):
    manifest = os.path.join(HERE, manifest) if not os.path.isabs(manifest) else manifest
    receipt = manifest + ".ots"
    info = subprocess.run([OTS, "info", receipt], capture_output=True, text=True, check=True).stdout
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
    man = open(manifest).read()
    commit = re.search(r"on commit ([0-9a-f]{40})", man).group(1)
    pairs = re.findall(r"(specarith/\S+)\s*\n\s*sha256 ([0-9a-f]{64})", man)
    tags = re.findall(r"tag (\S+)\s+object ([0-9a-f]{40})", man)
    hashes = {p: (h, hashlib.sha256(git("show", f"{commit}:{p}")).hexdigest()) for p, h in pairs}
    tagobj = {t: (o, git("rev-parse", t).decode().strip()) for t, o in tags}
    ok = dict(receipt_commits_to_manifest=digest == sha(manifest),
              manifest_hashes_match_commit=bool(pairs) and all(a == b for a, b in hashes.values()),
              tag_objects_match=all(a == b for a, b in tagobj.values()),
              tags_point_at_commit=all(git("rev-parse", f"{t}^{{commit}}").decode().strip() == commit for t, _ in tags),
              bitcoin_attested=len(att) >= 1, all_attestations_verify=bool(att) and all(a["verified"] for a in att))
    earliest = min(att, key=lambda a: a["height"]) if att else None
    out = dict(manifest=os.path.relpath(manifest, HERE), manifest_sha256=sha(manifest),
               receipt=os.path.relpath(receipt, HERE), receipt_sha256=sha(receipt), commit=commit,
               manifest_hashes={p: dict(listed=a, at_commit=b) for p, (a, b) in hashes.items()},
               tags={t: dict(listed=a, local=b) for t, (a, b) in tagobj.items()},
               attestations=sorted(att, key=lambda a: a["height"]), calendars_pending=calendars,
               earliest=dict(height=earliest["height"], block_hash=earliest["block_hash"], time_utc=earliest["time_utc"])
               if earliest else None,
               method="ots info merkle roots vs block headers from two explorers (no local Bitcoin node for ots verify)",
               checks=ok)
    stem = os.path.basename(manifest)[:-4]
    json.dump(out, open(os.path.join(HERE, "timestamps", f"{stem}_VERIFY.json"), "w"), indent=1)
    for a in out["attestations"]:
        print(f"block {a['height']} {a['block_hash'][:20]}… {a['time_utc']}  merkle root matches both explorers: "
              f"{a['verified']}")
    print("calendars still pending:", calendars)
    print(json.dumps(ok))
    return 0 if all(ok.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
