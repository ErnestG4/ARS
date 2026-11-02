# SPDX-License-Identifier: AGPL-3.0-or-later
"""Write the FN1 stage-2 sealing timestamp manifest (timestamps/FN1_STAGE2_SEAL_STAMP_2026-11-02.txt) from the local
annotated tag fn1-seal2: tag object, commit, and the sha256 of each sealed path's blob at the tag (`git show
fn1-seal2:<path>`). Only this manifest's sha256 goes to the OpenTimestamps calendars. Refuses to overwrite.
"""
import hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "timestamps", "FN1_STAGE2_SEAL_STAMP_2026-11-02.txt")
TAG = "fn1-seal2"
F = "specarith/fn1/"
PATHS = [F + p for p in (
    "FN1_STAGE2_SEAL.md", "fn1_read2.py", "fn1_pins2.json",
    "run_fn1_read2_one.sh", "run_fn1_read2_cmp.sh", "queue_fn1_read2_pueue.sh",
    "fn1_witness2.py", "fn1_make_pins2.py", "fn1_archive.py", "fn1_archive2_costs.py",
    "lead/fn1_stage2_constants.py", "lead/FN1_STAGE2_CONSTANTS.json", "lead/fn1_segnoise_betas.py",
    "lead/SEGNOISE_BETAS.json", "lead/fn1_stage2_reach.py", "lead/fn1_m7_persist_models.py",
    "results/stage2/FN1_WITNESS2_run1_FAILED.json", "results/stage2/FN1_WITNESS2_run2_FAILED.json",
    "results/stage2/FN1_WITNESS2_run3.json", "results/stage2/FN1_WITNESS2_run4.json",
    "results/stage2/FN1_STAGE2_REACH_FAILED.json", "results/stage2/FN1_STAGE2_REACH_run2.json",
    "results/stage2/FN1_M7_PERSIST_MODELS.json", "results/stage2/dry5/D1.json", "results/stage2/dry5/status.txt",
    *[f"results/manifests2/MANIFEST_D{d}.json" for d in (7, 8, 11, 19, 43, 67, 163)],
    "fn1_pins.json", "results/read/READ1.json")] + [
    "specarith/rq1/rq1_read.py", "specarith/rq1/rq1_zw.py", "specarith/rq1/rq1_angles.py", "specarith/rq1/rq1_archive.py",
    "specarith/safeio.py", "specarith/ph2/PH2_DECISIONS_2026-10-07.md"]


def git(*a):
    return subprocess.run(["git", *a], cwd=HERE, capture_output=True, check=True).stdout


if os.path.exists(OUT):
    sys.exit("REFUSED: manifest exists")
tag_obj = git("rev-parse", TAG).decode().strip()
commit = git("rev-parse", TAG + "^{commit}").decode().strip()
L = ["FN1 stage-2 sealing timestamp manifest (OpenTimestamps; order: seal -> stamp -> Bitcoin attestation verified on two",
     "explorers -> sequential double read through the queue -> cmp -> verdicts). Only this file's sha256 is submitted to the",
     "OpenTimestamps calendars; the receipt is FN1_STAGE2_SEAL_STAMP_2026-11-02.txt.ots.",
     "Statement: at the time of stamping, no statistic of the fresh slice (rows [227,524,967, 2,059,026,114) of every field)",
     "has been computed for the seven w = 2 fields (D = -7, -8, -11, -19, -43, -67, -163). Their 10^11 archives were only",
     "generated, integrity-checked and hashed, and a read-only comparison of manifest entries (k, rows, sha256) was made for",
     "the prefix guard. Every 9.F rehearsal used seeded random stand-in rows in their place. Z[i], Z[w] and Z[sqrt2] are",
     "partly seen, as seal 1b states. Nothing from the fresh slice will be read until this receipt is Bitcoin-attested and",
     "verified on two explorers; the read launcher refuses without that record.",
     "",
     f"repo                          criticality_tool, branch specarith",
     f"tag {TAG}                     object {tag_obj}",
     f"                              on commit {commit}"]
for p in PATHS:
    L.append(f"                              {p}")
    L.append(f"                              sha256 {hashlib.sha256(git('show', f'{TAG}:{p}')).hexdigest()}")
L.append(f"(sha256 of `git show {commit}:<path>`; the tag {TAG} resolves to that commit; {len(PATHS)} paths)")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "x").write("\n".join(L) + "\n")
print("written", OUT, len(PATHS), "paths")
