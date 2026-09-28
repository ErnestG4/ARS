"""Arm B GPU queue (ARMB_PREREG.md; Will's rule 09-27: A1 does not start until A0 passes B-G1). Runs detached.
A0 -> [wait for B-G1 verdicts on every gating step AND step 3000; all PASS] -> A1 -> A2 -> M0s1 -> M0s2.
A FAIL anywhere, a manual STOP, or a trainer error ends the queue. M0 arms are not queued here (need Muon + index maps).
Each trainer run is resumable: re-running this script continues where it stopped (finished arms are skipped by their
trainlog reaching the arm's stop step)."""
import json, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
PY = "/home/combust/fmexplorer/bin/python3"
GATE = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, 2000, 3000]
STOPS = {"A0": 3000, "A1": 5000, "A2": 3000, "M0s1": 3000, "M0s2": 3000}


def done(arm):
    f = HERE / "staging" / arm / "trainlog.jsonl"
    if not f.exists():
        return False
    last = f.read_text().strip().splitlines()[-1:]
    return bool(last) and json.loads(last[0])["step"] >= STOPS[arm]


def verdicts():
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "spot", "cat ~/llmspec_armb/bg1/bg1_verdicts.jsonl 2>/dev/null || true"],
                       capture_output=True, text=True, timeout=60)
    return {v["step"]: v for v in map(json.loads, r.stdout.split("\n")) if v} if r.returncode == 0 else None


def log(msg):
    with open(HERE / "queue_runner.log", "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + msg + "\n")


def run(arm):
    if done(arm):
        log(f"{arm} already complete"); return True
    log(f"{arm} start")
    rc = subprocess.run([PY, str(HERE / "train.py"), arm], stdout=open(HERE / f"train_{arm}.log", "a"), stderr=subprocess.STDOUT).returncode
    log(f"{arm} exit rc={rc}"); return rc == 0 and done(arm)


def main():
    if not run("A0"):
        sys.exit(3)
    t0 = time.time()
    while True:
        if (ROOT / "STOP").exists():
            log("STOP present: " + (ROOT / "STOP").read_text()); sys.exit(3)
        v = verdicts() or {}
        fails = [s for s in GATE if s in v and not v[s]["pass"]]
        if fails:
            log(f"B-G1 FAIL at {fails}: queue ends"); (ROOT / "STOP").write_text(f"B-G1 FAIL step {fails[0]}"); sys.exit(3)
        if all(s in v for s in GATE):
            log("B-G1 PASS on every gating step and 3000: A1 queued"); break
        if time.time() - t0 > 3 * 3600:
            log("B-G1 verdicts incomplete after 3 h: queue ends (check the spot daemon)"); sys.exit(3)
        time.sleep(60)
    for arm in ("A1", "A2", "M0s1", "M0s2"):
        if not run(arm):
            sys.exit(3)
    log("queue complete (A0, A1, A2, M0s1, M0s2)")


if __name__ == "__main__":
    main()
