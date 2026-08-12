#!/usr/bin/env python3
"""Resume of campaign_v15 after the 2026-08-12 reboot killed it mid-§6.iv-b.
Stages 1-3 (reference gates, §6.iii, §6.iv-a) completed with PASS verdicts and banked
artifacts before the reboot; this runs the remaining two stages with the same status handling.
"""
import json, os, subprocess, sys, time

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATUS = "derivflow/campaign_v15_status.json"
MARKER = "derivflow/campaign_v15.DONE"
PY = sys.executable
STAGES = [("sec6ivb_ensemble", ["derivflow/track0_ensemble.py"], False),
          ("science", ["derivflow/science_rate_question.py"], False)]

st = json.load(open(STATUS))
st["resumed_after_reboot"] = time.time()
for name, cmd, gated in STAGES:
    t0 = time.time()
    st["stages"][name] = {"state": "RUNNING"}
    json.dump(st, open(STATUS, "w"), indent=1)
    p = subprocess.run([PY] + cmd, capture_output=True, text=True)
    tail = "\n".join((p.stdout + p.stderr).strip().splitlines()[-12:])
    st["stages"][name] = {"state": "DONE" if p.returncode == 0 else "FAILED",
                          "returncode": p.returncode,
                          "minutes": round((time.time() - t0) / 60, 1), "tail": tail}
    json.dump(st, open(STATUS, "w"), indent=1)
st["finished"] = time.time()
json.dump(st, open(STATUS, "w"), indent=1)
open(MARKER, "w").write("done\n")
