"""
thermo/farey_orbit_check.py — the direct dynamical leg of the P4 attribution.

thermo/pressure_sweep.py established the attribution from the OPERATOR side (any finite
alphabet {1..A} gives an entire P_A, so the s=1/2 singularity is manufactured purely by
the a -> infinity tail). This is the independent DYNAMICAL leg, run directly on the Farey
map so the conclusion does not rest on one argument.

Farey map:   F(x) = x/(1-x)   for 0 < x <= 1/2      (left branch, near the neutral point)
             F(x) = (1-x)/x   for 1/2 < x < 1       (right branch)
F'(0) = 1 -- the indifferent/neutral fixed point at the origin. This is the intermittency.

Claim under test (handoff section 7 asserts the opposite):
    LARGE partial quotients are the slow orbits lingering near 0; the golden tail
    [0;1,1,1,...] takes the left branch NEVER and is the fastest-returning orbit.

METHOD -- iterate the CONTINUED FRACTION symbolically, not the real number.
On CF digits the Farey map acts exactly:
    [a1, a2, ...] -> [a1 - 1, a2, ...]   if a1 >= 2   (left branch)
    [a1, a2, ...] -> [a2, a3, ...]       if a1 == 1   (right branch)
so an excursion starting at partial quotient a takes exactly a-1 left steps before the
right branch fires.

    Two bugs this rewrite fixes, both of which produced a false INCONCLUSIVE:
    (1) iterating a FINITE CF such as [1]*60 iterates a RATIONAL, which is absorbed by
        the neutral fixed point once the expansion is exhausted -- golden falsely showed
        341 left-branch steps with a single 340-long dwell run, which is the absorption,
        not the dynamics.
    (2) the dwell run is a-1, not a (predicted a). Off-by-one in the prediction, not the
        measurement: from [a,...] it takes a-1 decrements to reach [1,...].
    Symbolic CF iteration is exact for the periodic (quadratic-irrational) starting
    points used here, so neither failure mode can recur.
"""
from __future__ import annotations

import json
import os

import mpmath as mp

mp.mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))


def x_from_cf(digits, depth=30):
    """x = [0; a1, a2, ...] from the leading CF digits (high precision, for reporting)."""
    d = digits[:depth]
    v = mp.mpf(d[-1])
    for a in reversed(d[:-1]):
        v = a + 1 / v
    return 1 / v


def farey_orbit_cf(period, steps):
    """Iterate the Farey map symbolically on the purely periodic CF [period] repeated."""
    def digit(i):
        return period[i % len(period)]

    head = 0                      # index of the current leading digit in the periodic word
    cur = digit(0)                # current (possibly decremented) leading partial quotient
    left = 0
    minx = mp.mpf(1)
    dwell, run = [], 0
    for _ in range(steps):
        tail = [cur] + [digit(head + 1 + k) for k in range(40)]
        minx = min(minx, x_from_cf(tail))
        if cur >= 2:
            cur -= 1
            left += 1
            run += 1
        else:
            head += 1
            cur = digit(head)
            if run:
                dwell.append(run)
            run = 0
    if run:
        dwell.append(run)
    return {"left_steps": left, "min_x": minx, "dwell_runs": dwell}


def main():
    STEPS = 400
    cases = [("golden  [1,1,1,...]", [1]), ("silver  [2,2,2,...]", [2]),
             ("[5,5,5,...]", [5]), ("[20,20,...]", [20]), ("[50,50,...]", [50])]
    print(f"Farey map, {STEPS} steps, symbolic CF iteration (exact).")
    print("Left branch = the neutral-point (intermittent) region.\n")
    print(f"  {'start':22s} {'a':>4s} {'left steps':>11s} {'min |x|':>12s} {'dwell runs':>22s}")
    rows = []
    for name, per in cases:
        r = farey_orbit_cf(per, STEPS)
        runs = r["dwell_runs"][:5]
        rows.append({"start": name, "a": per[0], "left_steps": r["left_steps"],
                     "min_x": mp.nstr(r["min_x"], 8), "dwell_runs": runs,
                     "predicted_dwell": per[0] - 1})
        print(f"  {name:22s} {per[0]:4d} {r['left_steps']:11d} "
              f"{mp.nstr(r['min_x'], 6):>12s} {str(runs):>22s}")

    golden = rows[0]
    dwell_equals_a_minus_1 = all(
        all(d == r["predicted_dwell"] for d in r["dwell_runs"]) for r in rows[1:] if r["dwell_runs"])
    golden_never = golden["left_steps"] == 0
    # proximity to the neutral point deepens as a grows (min|x| ~ 1/a)
    mins = [float(mp.mpf(r["min_x"])) for r in rows]
    monotone_min = all(mins[i + 1] < mins[i] for i in range(len(mins) - 1))
    # fraction of time spent in the intermittent region grows with a
    frac = [r["left_steps"] / STEPS for r in rows]
    monotone_frac = all(frac[i + 1] > frac[i] for i in range(len(frac) - 1))

    out = {"rows": rows, "steps": STEPS,
           "dwell_run_equals_a_minus_1": dwell_equals_a_minus_1,
           "golden_never_enters_left_branch": golden_never,
           "min_x_decreases_as_a_grows": monotone_min,
           "intermittent_fraction_increases_with_a": monotone_frac,
           "intermittent_fraction": frac,
           "VERDICT": ("LARGE_PARTIAL_QUOTIENTS_ARE_THE_SLOW_ORBITS"
                       if (dwell_equals_a_minus_1 and golden_never and monotone_min
                           and monotone_frac) else "INCONCLUSIVE")}
    print(f"\n  dwell run == a-1 exactly        : {dwell_equals_a_minus_1}")
    print(f"  golden never takes left branch  : {golden_never}  "
          f"(0 of {STEPS} steps in the intermittent region)")
    print(f"  min|x| decreases as a grows     : {monotone_min}   ~1/a, i.e. deeper into the cusp")
    print(f"  intermittent fraction rises w/ a: {monotone_frac}   {[round(f, 3) for f in frac]}")
    print(f"\n  VERDICT: {out['VERDICT']}")
    p = os.path.join(HERE, "farey_orbit_measured.json")
    json.dump(out, open(p, "w"), indent=2, default=str)
    print("wrote", p)


if __name__ == "__main__":
    main()
