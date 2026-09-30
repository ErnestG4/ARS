"""Fail-closed test of the queue runner's B-G1 gate (Will 09-28). A red path per failure mode; the real banked A0
verdicts (results/armb_bg1_verdicts_A0.jsonl) must PASS; every corruption must end in STOP without proceeding.
Uses wait_gate() with a fake fetch, a temporary STOP path and a 0.2 s timeout; the queue log is silenced."""
import json, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import queue_runner as Q

Q.log = lambda msg: None
REAL = (HERE.parent / "results" / "armb_bg1_verdicts_A0.jsonl").read_text()
recs = [json.loads(l) for l in REAL.splitlines() if l.strip()]


def text(rs):
    return "\n".join(json.dumps(r) for r in rs) + "\n"


def edit(i, **kw):
    rs = [dict(r) for r in recs]; rs[i].update(kw); return text(rs)


CASES = {                                   # name: ((rc, text), expected state, expect proceed)
    "real_A0_verdicts":        ((0, REAL), "PASS", True),
    "missing_file":            ((0, ""), "PENDING", False),
    "empty_file":              ((0, "\n\n"), "PENDING", False),
    "unparseable_line":        ((0, REAL + "{not json\n"), "CORRUPT", False),
    "truncated_last_line":     ((0, REAL.rstrip("\n")[:-20] + "\n"), "CORRUPT", False),
    "missing_key":             ((0, text([{k: v for k, v in r.items() if k != "pass"} if i == 3 else r for i, r in enumerate(recs)])), "CORRUPT", False),
    "one_gating_FAIL":         ((0, edit(8, **{"pass": False})), "FAIL", False),
    "wrong_scorer_sha":        ((0, edit(0, scorer_sha256="0" * 64)), "CORRUPT", False),
    "wrong_band_sha":          ((0, edit(5, band_sha256="f" * 64)), "CORRUPT", False),
    "conflicting_duplicate":   ((0, REAL + json.dumps(dict(recs[2], **{"pass": False})) + "\n"), "CORRUPT", False),
    "step_3000_missing":       ((0, text([r for r in recs if r["step"] != 3000])), "PENDING", False),
    "ssh_unreachable":         ((255, ""), "UNREACHABLE", False),
}


def main():
    ok_all = True
    for name, ((rc, txt), exp_state, exp_proceed) in CASES.items():
        state, detail = Q.gate_state(rc, txt)
        stop = Path(tempfile.mkdtemp()) / "STOP"
        proceeded = Q.wait_gate(lambda: (rc, txt), timeout=0.2, poll=0.05, stopfile=stop)
        good = state == exp_state and proceeded == exp_proceed and (stop.exists() != exp_proceed)
        ok_all &= good
        print(f"{'ok ' if good else 'BAD'} {name:24s} state={state:11s} proceeded={proceeded!s:5s} STOP={'yes' if stop.exists() else 'no ':3s} | {detail[:70]}")
    print("ALL FAIL-CLOSED CASES PASS" if ok_all else "FAILURES PRESENT")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
