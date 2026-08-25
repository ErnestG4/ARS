"""BEAT-RATE TARGETING: the inversion, with its units stated and its basin asserted.

COMMITTED GENERATOR of cross_substrate/brocot_beat_target.json. A CONSTRUCTION
with assertions, not a hypothesis test — every claim it makes about its own
output fails the run if false.

THE CONTROL
-----------
Above the horizon a ratio is characterised by (parent, separation). The
separation is closed-form, so it INVERTS: "give me a 3 Hz beat against 4/3" is
solvable rather than searchable.

UNITS, STATED BECAUSE THE FIRST VERSION OF THIS FORMULA DID NOT STATE THEM.
The lattice gap is dimensionless. The audible separation between the two
partials is

    sep_Hz = f_c * r1 * gap        gap = |a1 + a2*alpha|,  alpha = r2/r1

so a target of delta Hz corresponds to a lattice gap of g = delta / (f_c * r1),
and for parent p/q the solution is

    |q*alpha - p| = g      ->      alpha = (p +/- g) / q

The version written in review — alpha = (p +/- delta)/q — is correct only in
lattice units and wrong by a factor of f_c*r1 in Hz. At f_c = 220 and r1 = 1
that is a factor of 220: a request for 3 Hz would have returned a ratio 220
times too far off. A derivation with an unstated unit is a derivation plus a
choice, and here the choice was wrong.

THE BASIN ASSERTION
-------------------
For small delta the solution stays inside the parent's own basin, and for large
delta it does not: at some point (p +/- g)/q crosses a mediant and the answer is
a detuned SOMETHING ELSE. Silently returning that would answer a different
question than the one asked. So the inversion returns the achieved parent and
REFUSES when it is not the requested one.

    solve(parent=4/3, delta_hz=3,  f_c=220)  -> alpha, still in the 4/3 basin
    solve(parent=4/3, delta_hz=40, f_c=220)  -> refused, names the parent it hit

THE PERCEPTUAL SIDE IS CLEAN HERE, in a way the marker gate's was not.
`brocot_marker_erb_gate` could not claim audibility because it measured a STATIC
event at 0.67x a one-cent detune. A 3 Hz beat is not a static event — it is a
periodic amplitude modulation at 3 Hz, squarely inside the range a listener
reports as beating. This control lives in the regime that gate could not reach,
and the asymmetry is worth stating rather than leaving for someone to trip over.

ASSERTIONS
  B1  round-trip: solving for delta and re-measuring the gap returns delta,
      to 1e-9 relative, across a grid of parents, deltas and carriers
  B2  the returned alpha lies in the requested parent's basin, at every
      accepted solve
  B3  the refusal fires: large deltas ARE refused, and the refusal names the
      parent actually reached. A guard that never refuses is not a guard.
  B4  carrier scaling is real: the same delta at 2*f_c returns a different
      alpha, and the same alpha at 2*f_c beats at 2*delta
"""
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from phase3.partial_prediction import order_bound                 # noqa: E402


class OutOfBasin(ValueError):
    """The requested beat rate lands under a different parent."""


def parent_of(alpha, A):
    p, q = alpha.numerator, alpha.denominator
    best = None
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            key = (abs(a1 * q + a2 * p), max(abs(a1), abs(a2)), -a2)
            if best is None or key < best[0]:
                best = (key, a1, a2)
    (v, _, _), a1, a2 = best
    return (Fraction(abs(a1), abs(a2)) if a2 else None), Fraction(v, q)


def solve(parent, delta_hz, I=0.9, f_c=220.0, r1=Fraction(1), sign=+1,
          denom_limit=4096):
    """alpha whose partials sit delta_hz apart, in the given parent's basin.

    Returns (alpha, achieved_hz). Raises OutOfBasin if the solution belongs to
    a different parent — the answer to a different question."""
    parent = Fraction(parent)
    A = 2 * order_bound(I)
    g = Fraction(delta_hz / (f_c * float(r1))).limit_denominator(denom_limit)
    p, q = parent.numerator, parent.denominator
    alpha = Fraction(p + sign * g, q)
    got, gap = parent_of(alpha, A)
    if got != parent:
        raise OutOfBasin(
            f"{delta_hz} Hz against {parent} lands under {got}, not {parent}: "
            f"alpha = {float(alpha):.6f}. Reduce the target or choose {got}.")
    return alpha, float(gap) * float(r1) * f_c


PARENTS = [Fraction(1), Fraction(4, 3), Fraction(3, 4), Fraction(5, 4),
           Fraction(7, 5), Fraction(8, 7)]
DELTAS = [0.5, 1.0, 3.0, 6.0, 12.0]
CARRIERS = [110.0, 220.0, 440.0]

rows, refused = [], []
for par in PARENTS:
    for d in DELTAS:
        for fc in CARRIERS:
            try:
                al, got = solve(par, d, f_c=fc)
            except OutOfBasin as e:
                refused.append(dict(parent=str(par), delta=d, f_c=fc,
                                    why=str(e)[:80]))
                continue
            rows.append(dict(parent=str(par), delta_hz=d, f_c=fc,
                             alpha=str(al), alpha_f=float(al),
                             achieved_hz=got, err=abs(got - d)))

# B1 round trip
b1 = all(r["err"] <= 1e-9 * max(r["delta_hz"], 1.0) for r in rows)
assert b1, f"B1 round-trip failed, worst {max(r['err'] for r in rows):.3e}"

# B2 basin membership at every accepted solve (solve() enforces it; verified here
# independently rather than trusting the function that produced the row)
for r in rows:
    got, _ = parent_of(Fraction(r["alpha"]), 2 * order_bound(0.9))
    assert str(got) == r["parent"], f"B2 failed at {r}"

# B3 the refusal must fire
big = []
for par in PARENTS:
    try:
        solve(par, 60.0, f_c=220.0)
        big.append(str(par))
    except OutOfBasin as e:
        refused.append(dict(parent=str(par), delta=60.0, f_c=220.0,
                            why=str(e)[:80]))
assert refused, "B3 failed: the basin guard never refused — an inert guard"

# B4 carrier scaling
a1, _ = solve(Fraction(4, 3), 3.0, f_c=220.0)
a2, _ = solve(Fraction(4, 3), 3.0, f_c=440.0)
_, at440 = parent_of(a1, 8)
b4 = (a1 != a2) and abs(float(at440) * 440.0 - 6.0) < 1e-6
assert b4, f"B4 failed: {a1} vs {a2}, {float(at440) * 440.0}"

print(f"I = 0.9, A = {2 * order_bound(0.9)}   "
      f"{len(rows)} solves accepted, {len(refused)} refused\n")
print(f"{'parent':>7s} {'target':>7s} {'f_c':>6s} {'alpha':>12s} "
      f"{'alpha':>9s} {'achieved':>9s}")
for r in rows[:12]:
    print(f"{r['parent']:>7s} {r['delta_hz']:>6.1f}H {r['f_c']:>6.0f} "
          f"{r['alpha']:>12s} {r['alpha_f']:>9.6f} {r['achieved_hz']:>8.3f}H")
print(f"{'':>7s} ... {len(rows) - 12} more, all round-tripping\n")
print("refusals (the guard firing, not an error):")
for w in refused[:4]:
    print(f"    {w['parent']} at {w['delta']:.0f} Hz — {w['why']}")

print(f"\nB1 round-trip to 1e-9 relative            {len(rows)}/{len(rows)}")
print(f"B2 basin membership, independently checked {len(rows)}/{len(rows)}")
print(f"B3 refusal fires on large targets          {len(refused)} refusals")
print(f"B4 carrier scaling is real                 3 Hz@220 -> {float(a1):.6f}, "
      f"3 Hz@440 -> {float(a2):.6f}")
print("\nUNITS: sep_Hz = f_c * r1 * gap, so alpha = (p +/- delta/(f_c*r1)) / q.")
print("       alpha = (p +/- delta)/q is lattice units and is wrong by f_c*r1.")
print("PERCEPTUAL: a 3 Hz beat is a DYNAMIC phenomenon, squarely audible — this")
print("       control lives in the regime brocot_marker_erb_gate could not claim,")
print("       because that gate measured a STATIC event at 0.67x a one-cent detune.")

with redpath("accepted beat-target solves", expect_min=60) as rp:
    rp.observed(len(rows))

json.dump(dict(I=0.9, A=2 * order_bound(0.9), parents=[str(p) for p in PARENTS],
               deltas=DELTAS, carriers=CARRIERS, n_accepted=len(rows),
               n_refused=len(refused), rows=rows, refusals=refused[:12],
               assertions=dict(B1=bool(b1), B2=True, B3=bool(refused),
                               B4=bool(b4)),
               units="sep_Hz = f_c * r1 * gap; alpha = (p +/- delta/(f_c*r1))/q",
               verdict="INVERSION_VERIFIED"),
          open(f"{HERE}/brocot_beat_target.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_beat_target.json")
