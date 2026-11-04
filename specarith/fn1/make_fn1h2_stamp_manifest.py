# SPDX-License-Identifier: AGPL-3.0-or-later
"""Write the FN1-h2 sealing timestamp manifest (timestamps/FN1H2_SEAL_STAMP_2026-11-04.txt) from the local annotated tag
fn1h2-seal: tag object, commit, and the sha256 of each sealed path's blob at the tag (`git show fn1h2-seal:<path>`). Only
this manifest's sha256 goes to the OpenTimestamps calendars. Refuses to overwrite. (As make_fn1_stamp2_manifest.py.)
"""
import hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "timestamps", "FN1H2_SEAL_STAMP_2026-11-04.txt")
TAG = "fn1h2-seal"
F = "specarith/fn1/"
H2 = (15, 20, 24, 35, 40, 51, 52, 88, 91, 115, 123, 148, 187, 232, 235, 267, 403, 427)
PATHS = [F + p for p in (
    "FN1H2_SEAL.md", "fn1h2_read.py", "fn1h2_pins.json", "run_fn1h2_read_one.sh", "run_fn1h2_read_cmp.sh",
    "queue_fn1h2_read_pueue.sh", "fn1h2_archive.py", "fn1h2_make_pins.py", "fn1h2_costs.py", "fn1h2_counts.py",
    "fn1h2_fixtures.py", "run_fn1h2_dry.sh", "fn1_read2.py", "fn1_archive.py", "fn1_pins2.json",
    "lead/fn1h2_pred.py", "lead/FN1H2_PRED.json", "lead/fn1h2_controls.py", "lead/FN1H2_CONTROLS.json",
    "lead/fn1h2_sim.py", "lead/FN1H2_R_DERIVATION.md", "lead/FN1_L17_PREREQS.md",
    "results/h2/FN1H2_REFS.json", "results/h2/FN1H2_SIM.json", "results/h2/GENERATOR_SELFTEST.txt",
    "results/h2/dry/cmp.txt", "results/h2/dry2/cmp.txt",
    *[f"results/h2/manifests/MANIFEST_D{d}.json" for d in H2],
    "results/h2/manifests/MANIFEST_SHA256.txt", "results/h2/manifests/COUNTS.json")] + [
    "specarith/rq1/rq1_read.py", "specarith/rq1/rq1_zw.py", "specarith/rq1/rq1_angles.py", "specarith/rq1/rq1_archive.py",
    "specarith/safeio.py", "specarith/ph2/PH2_DECISIONS_2026-10-07.md"]


def git(*a):
    return subprocess.run(["git", *a], cwd=HERE, capture_output=True, check=True).stdout


if os.path.exists(OUT):
    sys.exit("REFUSED: manifest exists")
tag_obj = git("rev-parse", TAG).decode().strip()
commit = git("rev-parse", TAG + "^{commit}").decode().strip()
L = ["FN1-h2 sealing timestamp manifest (OpenTimestamps; order: seal -> stamp -> Bitcoin attestation verified on two",
     "explorers -> sequential double read through the queue -> cmp -> verdicts). Only this file's sha256 is submitted to the",
     "OpenTimestamps calendars; the receipt is FN1H2_SEAL_STAMP_2026-11-04.txt.ots.",
     "Statement: at the time of stamping, no statistic of the h = 2 principal-prime sets (18 fields, p <= 2e10) has been",
     "computed. Their archives were only generated, integrity-checked, counted and hashed (with an Euler-criterion recount",
     "of the row counts at three segments of -148 and -52). Every 9.F rehearsal used seeded random fixtures in their place.",
     "The h = 1 references were computed before the seal on seen data (D2 (b)) and are pinned. Nothing from the h = 2",
     "archives will be read until this receipt is Bitcoin-attested and verified on two explorers; the read launcher",
     "refuses without that record.",
     "",
     f"repo                          criticality_tool, branch specarith",
     f"tag {TAG}                    object {tag_obj}",
     f"                              on commit {commit}"]
for p in PATHS:
    L.append(f"                              {p}")
    L.append(f"                              sha256 {hashlib.sha256(git('show', f'{TAG}:{p}')).hexdigest()}")
L.append(f"(sha256 of `git show {commit}:<path>`; the tag {TAG} resolves to that commit; {len(PATHS)} paths)")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "x").write("\n".join(L) + "\n")
print("written", OUT, len(PATHS), "paths")
