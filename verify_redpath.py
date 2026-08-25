"""Board row for the non-vacuity floor itself.

WHAT TURNS THIS RED: redpath stops refusing a probe that falls below its planted
floor, a probe that never counts its own reach, or a declared `expect_exit` that
is unsupplied or wrong.

WHY IT EXISTS: adversarial review found `expect_exit` accepted and used by
nothing — a parameter that looked like a guard and guarded nothing — and noted
that the module preaching "a red-path must assert its own reach" had no
self-test and no board row proving `VacuousRedPath` could raise at all. The
guard against vacuous guards was itself unverified.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = subprocess.run([sys.executable, os.path.join(HERE, "redpath.py")],
                   capture_output=True, text=True, cwd=HERE)
ok = p.returncode == 0 and "REDPATH_SELF_TEST_PASS" in p.stdout
print("non-vacuity floor guard\n")
print(f"  {'PASS' if ok else 'FAIL'}  redpath refuses a short probe, a silent "
      "probe, and a bad expect_exit")
if not ok:
    print((p.stderr.strip().splitlines() or ["(no stderr)"])[-1])
    print("\nVERIFY_REDPATH: FAIL")
    sys.exit(1)
print("\nVERIFY_REDPATH: PASS — the floor that polices every other probe is "
      "itself red-pathed.")
