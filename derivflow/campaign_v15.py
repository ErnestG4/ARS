#!/usr/bin/env python3
"""v1.5.1 corrected-instrument recompute campaign (seal post_seal_change_protocol).

Order: archive v1-grid artifacts -> reference known-answer gates (abort on FAIL) ->
§6.iii re-run (pre-committed rule) -> §6.iv-a re-run -> §6.iv-b re-run -> science re-run
(v1.5.1 band adjudication). Status written to campaign_v15_status.json after each stage;
DONE marker file at campaign_v15.DONE. Abort leaves status + partial artifacts for review.
"""
import json, os, shutil, subprocess, sys, time

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATUS = "derivflow/campaign_v15_status.json"
MARKER = "derivflow/campaign_v15.DONE"
PY = sys.executable

ARCHIVE = ["track0_iid_scaling.json", "track0_jitter_floor.json",
           "track0_ensemble.json", "science_rate_question.json"]
STAGES = [
    ("reference_gates", ["derivflow/reference_v2_gates.py"], True),
    ("sec6iii_rescale", ["derivflow/track0_iid_scaling.py"], True),
    ("sec6iva_jitter", ["derivflow/track0_jitter_floor.py"], True),
    ("sec6ivb_ensemble", ["derivflow/track0_ensemble.py"], False),
    ("science", ["derivflow/science_rate_question.py"], False),
]


def put(status):
    with open(STATUS, "w") as f:
        json.dump(status, f, indent=1)


def main():
    st = {"campaign": "v1.5.1 corrected instrument", "started": time.time(), "stages": {}}
    os.makedirs("derivflow/archive_v1grid", exist_ok=True)
    for a in ARCHIVE:
        src = f"derivflow/{a}"
        if os.path.exists(src):
            shutil.copy2(src, f"derivflow/archive_v1grid/{a}")
    st["archived"] = ARCHIVE
    put(st)
    for name, cmd, gated in STAGES:
        t0 = time.time()
        st["stages"][name] = {"state": "RUNNING"}
        put(st)
        p = subprocess.run([PY] + cmd, capture_output=True, text=True)
        tail = "\n".join((p.stdout + p.stderr).strip().splitlines()[-12:])
        st["stages"][name] = {"state": "DONE" if p.returncode == 0 else "FAILED",
                              "returncode": p.returncode,
                              "minutes": round((time.time() - t0) / 60, 1), "tail": tail}
        put(st)
        if gated and p.returncode != 0:
            st["aborted_at"] = name
            put(st)
            break
    st["finished"] = time.time()
    st["total_hours"] = round((st["finished"] - st["started"]) / 3600, 2)
    put(st)
    open(MARKER, "w").write("done\n")


if __name__ == "__main__":
    main()
