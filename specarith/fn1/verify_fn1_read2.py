# SPDX-License-Identifier: AGPL-3.0-or-later
"""Check the FN1 stage-2 sealed read record in results/stage2/read/ (written after the read; it decides nothing).

Checks, independently of fn1_read2.py:
1. READ1.json and READ2.json are byte-identical, and their sha256 is the one in status.txt; cmp.txt is empty;
   status.txt has "read1 rc 0", "read2 rc 0" and "cmp 0".
2. The read used the sealed pins (pins_sha256) on the sealed slice (n_lo, n_hi, n).
3. Each sealed label follows from its own statistic under the seal's rules (FN1_STAGE2_SEAL.md §2):
   - rank arms: PASS iff sum_d2 <= 26 (and rho > 0); the primary is two-way, a FAIL there is informative iff the
     read-time power >= 0.80; β 0.45 / 0.40 are one-way;
   - −7: T = min(R_−7 − R_−8, R_−7 − R_−11) recomputed from R; PASS iff T > m; one-way;
   - the ℤ[√2] placement is not in the verdict lattice, and its descriptive flag matches R at every β.
4. The report FN1_STAGE2_READ_REPORT.md names each sealed label and the read sha256.
Exits 0 iff all hold.
"""
import hashlib, json, os, sys

H = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(H, "results", "stage2", "read")
PINS = "c511e4a4549c14ca0913753d8d32b0822b5840714d9311a17e060a9a74b404ce"
ONE_WAY_FAIL = "FAIL (one-way arm: FAIL not informative)"
UNPOWERED = "FAIL (UNPOWERED at the read-time noise)"
bad = []


def need(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        bad.append(msg)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


r1, r2 = os.path.join(D, "READ1.json"), os.path.join(D, "READ2.json")
b1, b2 = open(r1, "rb").read(), open(r2, "rb").read()
need(b1 == b2, "READ1.json and READ2.json byte-identical")
s = sha(r1)
status = open(os.path.join(D, "status.txt")).read().splitlines()
need(os.path.getsize(os.path.join(D, "cmp.txt")) == 0, "cmp.txt empty")
for ln in ("read1 rc 0", "read2 rc 0", "cmp 0"):
    need(ln in status, f"status.txt has '{ln}'")
need(sum(1 for ln in status if ln.startswith(s + " ")) == 2, f"status.txt sha256 lines match the local reads ({s[:8]})")

d = json.loads(b1)
need(d["pins_sha256"] == PINS, "pins_sha256 is the sealed fn1_pins2.json")
need((d["n_lo"], d["n_hi"], d["n"]) == (227524967, 2059026114, 1831501147), "slice rows as sealed")

v, t, R = d["verdict"], d["tests"], d["R"]
need(set(v) == {"primary_beta055", "secondary_beta045", "secondary_beta040", "minus7_beta055"},
     "verdict lattice keys as sealed (no placement verdict)")


def rank_label(b, two_way):
    rt = t[b]["rank_test_C"]
    if rt["sum_d2"] <= 26 and rt["rho"] > 0:
        return "PASS"
    if not two_way:
        return ONE_WAY_FAIL
    return "FAIL" if d["read_time_noise"][b]["power_at_read_noise"] >= 0.80 else UNPOWERED


for key, b, tw in (("primary_beta055", "0.55", True), ("secondary_beta045", "0.45", False),
                   ("secondary_beta040", "0.4", False)):
    need(v[key] == rank_label(b, tw), f"{key} = {v[key]!r} follows from sum_d2 {t[b]['rank_test_C']['sum_d2']}")
m7 = t["minus7_beta055"]
T = min(R["-7"]["0.55"] - R["-8"]["0.55"], R["-7"]["0.55"] - R["-11"]["0.55"])
need(abs(T - m7["T"]) < 1e-12, f"−7 T recomputed from R ({T:.6f})")
need(v["minus7_beta055"] == ("PASS" if T > m7["margin"] else ONE_WAY_FAIL),
     f"minus7_beta055 = {v['minus7_beta055']!r} follows from T {T:.4f} vs m {m7['margin']:.4f}")
for b in ("0.55", "0.45", "0.4"):
    z = R["-67"][b] < R["zs2"][b] < R["-163"][b]
    need(t[b]["zs2_between_m67_m163"] == z, f"ℤ[√2] placement flag at β {b} matches R ({z})")

rep = open(os.path.join(H, "FN1_STAGE2_READ_REPORT.md"), encoding="utf-8").read()
need(s in rep, "report carries the read sha256")
need(ONE_WAY_FAIL in rep, "report carries the −7 one-way FAIL label verbatim")
print("READ RECORD", "OK" if not bad else f"BAD ({len(bad)})")
sys.exit(0 if not bad else 1)
