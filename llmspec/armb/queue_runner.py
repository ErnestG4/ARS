"""Arm B GPU queue (ARMB_PREREG.md; Will's rule 09-27: A1 does not start until A0 passes B-G1). Runs detached.
A0 -> [wait for B-G1 verdicts on every gating step AND step 3000; all PASS] -> A1 -> A2 -> M0s1 -> M0s2.
FAIL-CLOSED (Will 09-28): only a complete, well-formed, sealed-provenance all-PASS verdict set proceeds; FAIL/CORRUPT write
STOP at once; PENDING/UNREACHABLE past the timeout write STOP. A manual STOP or a trainer error also ends the queue.
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


SCORER_SHA = "e24e570c7f709a3c735024f6b253512ceaaacc6fc5873862be1f8f179334fa4a"   # sealed bg1_score.py (B1a-A2)
BAND_SHA = "c51a4d6abb8e9efe8dd3009dc3b0ac5c391ef5fa4d72aba4075a6db1673875ca"     # sealed reference band


def fetch_verdicts():
    """(returncode, text) of spot's verdict file. A missing file yields rc 0 and empty text (-> PENDING)."""
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "spot", "cat ~/llmspec_armb/bg1/bg1_verdicts.jsonl 2>/dev/null || true"],
                           capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout
    except subprocess.TimeoutExpired:
        return 255, ""


def gate_state(rc, text):
    """FAIL-CLOSED gate decision. Returns (state, detail); only "PASS" lets the queue proceed.
      UNREACHABLE  ssh failed                                      -> wait; STOP at the timeout
      CORRUPT      any non-blank line unparseable, a record missing keys, a step not an int, duplicate steps with
                   different verdicts, or provenance (scorer/band sha256) not the sealed values -> STOP now
      FAIL         any gating step with pass == false               -> STOP now
      PENDING      file missing / empty / some gating steps not yet scored -> wait; STOP at the timeout
      PASS         every gating step present, all pass == true, sealed provenance on every record"""
    if rc != 0:
        return "UNREACHABLE", f"ssh rc={rc}"
    v = {}
    for i, l in enumerate(text.splitlines()):
        if not l.strip():
            continue
        try:
            rec = json.loads(l)
            st, ok = rec["step"], rec["pass"]
            assert isinstance(st, int) and isinstance(ok, bool)
        except Exception as e:
            return "CORRUPT", f"line {i + 1} unparseable/invalid: {e!r}"
        if rec.get("scorer_sha256") != SCORER_SHA or rec.get("band_sha256") != BAND_SHA:
            return "CORRUPT", f"step {st}: provenance not the sealed scorer/band"
        if st in v and v[st]["pass"] != ok:
            return "CORRUPT", f"step {st}: conflicting verdicts"
        v[st] = rec
    fails = [s for s in GATE if s in v and not v[s]["pass"]]
    if fails:
        return "FAIL", f"B-G1 FAIL step {fails[0]} ({v[fails[0]].get('worst')} z={v[fails[0]].get('z')})"
    missing = [s for s in GATE if s not in v]
    if missing:
        return "PENDING", f"{len(missing)} gating steps not scored (first {missing[0]})"
    return "PASS", f"{len(GATE)} gating steps PASS"


def log(msg):
    with open(HERE / "queue_runner.log", "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + msg + "\n")


def run(arm):
    if done(arm):
        log(f"{arm} already complete"); return True
    log(f"{arm} start")
    rc = subprocess.run([PY, str(HERE / "train.py"), arm], stdout=open(HERE / f"train_{arm}.log", "a"), stderr=subprocess.STDOUT).returncode
    log(f"{arm} exit rc={rc}"); return rc == 0 and done(arm)


def wait_gate(fetch, timeout, poll, stopfile=None):
    """Block until the gate is PASS (return True) or fail closed: write STOP and return False."""
    stopfile = stopfile or (ROOT / "STOP"); t0 = time.time()
    while True:
        if stopfile.exists():
            log("STOP present: " + stopfile.read_text()); return False
        state, detail = gate_state(*fetch())
        if state == "PASS":
            log("B-G1 " + detail + ": next arm queued"); return True
        if state in ("FAIL", "CORRUPT"):
            log(f"B-G1 {state}: {detail}: queue ends"); stopfile.write_text(f"B-G1 {state}: {detail}"); return False
        if time.time() - t0 > timeout:
            log(f"B-G1 {state} after {timeout} s: {detail}: queue ends")
            stopfile.write_text(f"B-G1 {state} after timeout: {detail}"); return False
        time.sleep(poll)


def main():
    if not run("A0"):
        sys.exit(3)
    if not wait_gate(fetch_verdicts, timeout=3 * 3600, poll=60):
        sys.exit(3)
    for arm in ("A1", "A2", "M0s1", "M0s2"):
        if not run(arm):
            sys.exit(3)
    log("queue complete (A0, A1, A2, M0s1, M0s2)")


if __name__ == "__main__":
    main()
