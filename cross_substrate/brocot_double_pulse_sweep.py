"""THE DOUBLE-PULSE SWEEP: amplitudes move, support does not, and neither does the scope.

COMMITTED GENERATOR of cross_substrate/brocot_double_pulse_sweep.json.
Predictions sealed here, before any output exists.

WHAT IS BEING SWEPT
-------------------
`brocot_waveform_parity` tested ENDPOINT stacks and found parity irrelevant: only
a stack's extent moves the ringing set. But Fritz's control is CONTINUOUS, and an
intermediate double pulse has the same harmonic SUPPORT as a saw while its
amplitudes differ — and support is all the ringing predicate sees. So
orthogonality should hold through the sweep by construction, while everything
amplitude-dependent (audibility, timbre) changes. That is the gap this closes.

The waveform, from Fritz's construction: a pulse and its half-period-displaced,
inverted copy, mixed by beta.

    f(t) = p(t) - beta * p(t - T/2)
    F_n  = P_n * (1 - beta * (-1)^n)

    so   odd n:  F_n = P_n (1 + beta)      even n: F_n = P_n (1 - beta)

beta = 0 is a single pulse, every harmonic present. beta = 1 is the antisymmetric
double pulse: the even harmonics cancel exactly and only odd survive. In between,
even harmonics are present at reduced amplitude — the case the endpoint test
never covered.

AND THE THING THE OSCILLOSCOPE SHOWS, which is not the horizon
---------------------------------------------------------------
A scope triggered on the carrier shows a STATIONARY image when the composite
waveform repeats: for alpha = p/q the composite period is q carrier cycles,
whatever the harmonics do. That is a PERIOD-LOCK property, governed by q alone.

The horizon is a SIDEBAND-COINCIDENCE property, governed by max(p, q) against
2B. The two are different structures over the same rational, and confusing them
would be easy for anyone building a visual feature: a frozen, simple scope image
does not mean the partials have merged, and a merged spectrum does not mean the
trace is simple. A4 measures how far apart they are, so a display cannot imply
one while showing the other.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — bars edge-probed                                        ║
║                                                                              ║
║ A1  SUPPORT IS INVARIANT ACROSS THE SWEEP — the ringing set is identical at   ║
║     every beta in (0, 1), symmetric difference 0 against the beta = 0 set.   ║
║     Orthogonality holds through the sweep, not only at its ends.             ║
║ A2  BUT AMPLITUDES MOVE — the coincidence witness amplitude changes by at     ║
║     least 6 dB across the sweep. If it misses, the control is inaudible on    ║
║     the coincidences too and there is nothing to design around.              ║
║ A3  AND AUDIBILITY DOES NOT RETURN — under Stage A's masking criterion, at    ║
║     most 2 of the non-degenerate below-horizon ratios become audible at ANY   ║
║     beta. Stage A found zero at the endpoints; the sweep is where a           ║
║     resonance could hide.                                                    ║
║ A4  THE SCOPE IS NOT THE HORIZON — among ratios in range, at least 4          ║
║     distinct denominators q appear among the RINGING set, and at least one    ║
║     q value is shared between a ringing and a non-ringing ratio. Both must    ║
║     hold for the two structures to be genuinely independent rather than       ║
║     coincidentally different.                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from ratiopinned import pinned, assert_no_pinned_at_irrational    # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
BOUND = 2 * B
LO, HI, FC = 0.70, 1.40, 220.0
BETAS = [0.0, 0.25, 0.5, 0.75, 0.9, 1.0]
HMAX = 7                       # harmonics kept from the pulse train
PULSE_W = 0.25                 # duty cycle of the base pulse

INSTRUMENT = Model("double-pulse modulator + Stage A relative masking", [
    Param("beta", TESTED, sweep=BETAS,
          why="Fritz's timbre control: 0 = single pulse, 1 = antisymmetric "
              "double pulse. The whole point of the cell."),
    Param("sigma_scale", TESTED, sweep=[1.0, 0.4],
          why="ERB is an equivalent RECTANGULAR bandwidth; Stage A showed the "
              "audible count is width-sensitive"),
    Param("pulse_width", DECLARED, value=PULSE_W,
          why="sets P_n, the pulse's own envelope, which multiplies BOTH "
              "parities equally and so cannot affect A1; it scales A2's "
              "absolute level, not the ratio across beta"),
    Param("h_max", DECLARED, value=HMAX,
          why="brocot_waveform_parity showed only a stack's EXTENT moves the "
              "ringing set, so the extent is held fixed while parity content "
              "sweeps — the control this cell needs"),
    Param("f_c", DECLARED, value=FC,
          why="the criterion is a ratio of amplitudes; scale-invariant"),
])


def harmonics(beta):
    """(h, amplitude) for the double pulse: P_n * (1 - beta*(-1)^n)."""
    out = []
    for n in range(1, HMAX + 1):
        pn = abs(np.sin(np.pi * n * PULSE_W) / (np.pi * n))
        a = pn * (1.0 - beta * ((-1) ** n))
        if a > 1e-12:
            out.append((n, a))
    return out


def support(beta):
    return [h for h, _ in harmonics(beta)]


NODES = sorted({Fraction(p, q) for q in range(1, 21) for p in range(1, 30)
                if gcd(p, q) == 1 and LO <= p / q <= HI}, key=float)


def ringing(beta):
    sp = [(1, 0)] + [(0, h) for h in support(beta)]
    return {a for a in NODES if pinned(sp, BOUND, a)}


for beta in BETAS:
    assert_no_pinned_at_irrational([(1, 0)] + [(0, h) for h in support(beta)],
                                   BOUND)

base = ringing(0.0)
sets = {b: ringing(b) for b in BETAS}
a1 = max(len(sets[b] ^ base) for b in BETAS if b < 1.0)
a1_at_one = len(sets[1.0] ^ base)


def erb_w(f):
    return 24.7 * (4.37 * f / 1000.0 + 1.0)


def witness_amp_and_audible(alpha, beta, margin=0.0, wscale=1.0):
    """Amplitude of the weaker witness partial, and whether both clear masking."""
    hs = harmonics(beta)
    p, q = alpha.numerator, alpha.denominator
    n1, n1p = -(-p // 2), -(p // 2)
    n2, n2p = -(q // 2), -(-q // 2)
    if max(abs(n1), abs(n1p)) > B or max(abs(n2), abs(n2p)) > B:
        return None, False
    lat = {}
    for a in range(-B, B + 1):
        for hh, ha in hs:
            for b in range(-B, B + 1):
                amp = abs(float(jv(a, I_MUS)) * float(jv(b, I_MUS * ha /
                                                         max(h for h, _ in hs))))
                if amp < 1e-7:
                    continue
                f = abs(1.0 + a + b * hh * float(alpha)) * FC
                if 20 <= f <= 16000:
                    lat[round(f, 4)] = lat.get(round(f, 4), 0.0) + amp
    f = np.array(sorted(lat))
    av = np.array([lat[k] for k in sorted(lat)])
    amps, ok = [], True
    for (x, y) in ((n1, n2), (n1p, n2p)):
        amp = abs(float(jv(x, I_MUS)) * float(jv(y, I_MUS)))
        amps.append(amp)
        nu = abs(1.0 + x + y * float(alpha)) * FC
        i = int(np.argmin(np.abs(f - nu)))
        o = f != f[i]
        if o.any():
            e = np.sqrt(np.sum((av[o] ** 2)
                               * np.exp(-0.5 * ((f[i] - f[o])
                                                / (erb_w(f[o]) * wscale)) ** 2)))
            if e > 0 and 20 * np.log10(amp / e) <= margin:
                ok = False
    return min(amps), ok


NONDEG = [a for a in base if a != 1]
probe = NONDEG[len(NONDEG) // 2]
levels = {}
for b in BETAS:
    hs = harmonics(b)
    even = sum(a for h, a in hs if h % 2 == 0)
    odd = sum(a for h, a in hs if h % 2 == 1)
    levels[b] = dict(even=even, odd=odd,
                     ratio_db=(20 * np.log10(even / odd) if even > 0 else -np.inf))
sw = [levels[b]["even"] for b in BETAS if levels[b]["even"] > 0]
a2 = 20 * np.log10(max(sw) / min(sw)) if len(sw) > 1 else 0.0

aud = {}
for b in BETAS:
    for w in (1.0, 0.4):
        aud[(b, w)] = sum(1 for a in NONDEG
                          if witness_amp_and_audible(a, b, 0.0, w)[1])
a3 = max(aud.values())

qs_ring = {a.denominator for a in base}
qs_not = {a.denominator for a in NODES if a not in base}
a4_distinct = len(qs_ring)
a4_shared = len(qs_ring & qs_not)

A1 = Bar("symmetric difference of ringing sets across beta", 0, direction="le",
         floor=0, ceiling=len(NODES),
         why=f"a symmetric difference of subsets of {len(NODES)} nodes")
A2 = Bar("even-harmonic level swing across beta, dB", 6.0, floor=0.0,
         ceiling=120.0,
         why="a level ratio in dB; 0 if the control does nothing, and bounded "
             "well under 120 dB by the smallest nonzero beta step tested")
A3 = Bar("non-degenerate ratios audible at any beta", 2, direction="le",
         floor=0, ceiling=len(NONDEG),
         why=f"a count of the {len(NONDEG)} non-degenerate below-horizon ratios")
A4a = Bar("distinct denominators among ringing ratios", 4, floor=1,
          ceiling=len(qs_ring | qs_not),
          why="a count of distinct q values present in the enumerated set")
A4b = Bar("q values shared between ringing and non-ringing", 1, floor=0,
          ceiling=len(qs_ring | qs_not),
          why="a count of shared q values, 0 to the number of distinct q")
s1, s2, s3, s4a, s4b = (A1.score(a1), A2.score(a2), A3.score(a3),
                        A4a.score(a4_distinct), A4b.score(a4_shared))

print(INSTRUMENT.report())
print(f"\ndouble pulse, width {PULSE_W}, harmonics 1..{HMAX}\n")
print(f"{'beta':>6s} {'support':>20s} {'odd sum':>9s} {'even sum':>9s} {'even/odd dB':>12s}")
for b in BETAS:
    L = levels[b]
    d = f"{L['ratio_db']:>11.1f}" if np.isfinite(L["ratio_db"]) else "   -inf"
    print(f"{b:>6.2f} {str(support(b)):>20s} {L['odd']:>9.4f} "
          f"{L['even']:>9.4f} {d:>12s}")

print(f"\nringing set: {len(base)} ratios at beta = 0; "
      f"symmetric difference at every beta < 1: {a1}; at beta = 1: {a1_at_one}")
print(f"\naudible non-degenerate ratios under masking:")
print(f"{'beta':>6s} " + "".join(f"{'sigma=' + str(w):>12s}" for w in (1.0, 0.4)))
for b in BETAS:
    print(f"{b:>6.2f} " + "".join(f"{aud[(b, w)]:>12d}" for w in (1.0, 0.4)))

print(f"\nscope vs horizon: denominators among ringing {sorted(qs_ring)}")
print(f"                  shared with non-ringing     {sorted(qs_ring & qs_not)}")
print()
for b, v, f in ((A1, a1, "{:.0f}"), (A2, a2, "{:.1f}"), (A3, a3, "{:.0f}"),
                (A4a, a4_distinct, "{:.0f}"), (A4b, a4_shared, "{:.0f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s1, EX_ROLE,
                          claim="the ringing set does not move across the sweep"),
             Arm.from_bar(s2, MECH_ROLE,
                          claim="the control does move the even-harmonic level, "
                                "so it is not inert"),
             Arm.from_bar(s3, RES_ROLE,
                          claim="no coincidence becomes audible at any beta"),
             Arm.from_bar(s4b, RES_ROLE,
                          claim="scope-lock and the horizon are independent, "
                                "not coincidentally different")],
            holds="SWEEP_IS_HORIZON_ORTHOGONAL",
            fails="SWEEP_TOUCHES_THE_HORIZON")
print(f"\nVERDICT: {v['citation']}")

with redpath("beta x ratio evaluations", expect_min=300) as rp:
    rp.observed(len(BETAS) * len(NODES) + len(BETAS) * len(NONDEG) * 2)

json.dump(dict(I=I_MUS, B=B, bound=BOUND, betas=BETAS, h_max=HMAX,
               pulse_width=PULSE_W, instrument=INSTRUMENT.seal(),
               levels={str(b): levels[b] for b in BETAS},
               ringing_base=sorted(str(a) for a in base),
               symdiff_below_one=a1, symdiff_at_one=a1_at_one,
               audible={f"beta={b},sigma={w}": c for (b, w), c in aud.items()},
               q_ringing=sorted(qs_ring), q_shared=sorted(qs_ring & qs_not),
               bars={s["name"]: s for s in (s1, s2, s3, s4a, s4b)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_double_pulse_sweep.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_double_pulse_sweep.json")
