"""A CALIBRATOR THAT CAN ONLY FALSIFY THE INSTRUMENT — and measures its blind spot.

COMMITTED GENERATOR of csprng_calibrator.json.
Predictions sealed here, before any output exists.

THE IDEA, AND THE CATCH THAT CHANGES IT
---------------------------------------
The cleanest imaginable calibrator for this repo would be a Martin-Lof random
sequence: random relative to EVERY computable statistical test, so any nonzero
ARS reading on it is by construction a bug in the instrument and can be nothing
else. A calibrator that can only ever falsify the tool.

IT CANNOT BE BUILT. No Martin-Lof random sequence is computable -- that is close
to the definition. Omega is random and uncomputable; anything a program can emit
is, by being emitted, not ML-random. So the ideal calibrator is unavailable in
principle, not merely inconvenient.

THE BUILDABLE VERSION KEEPS THE ONE-SIDEDNESS ON DIFFERENT GROUNDS. Drive the
process from a cryptographically secure generator (`os.urandom`, ChaCha20 on
this platform). Then a departure from Poisson has exactly two explanations:

    (a) the instrument is wrong, or
    (b) the battery is a distinguisher against the stream cipher.

(b) would be a substantially larger result than anything this repo is testing,
so in practice the calibrator is one-sided: a reading is a bug. The
one-sidedness is now cryptographic rather than computability-theoretic, which is
weaker in kind and entirely sufficient in use.

AND THE SECOND HALF, WHICH IS THE POINT
---------------------------------------
No finite battery of tests is complete -- that IS the Martin-Lof theorem, and it
says there is always computable structure the current instruments do not see.
This repo has treated that as a reason never to retire the induction-on-noise
check. It can be turned from a slogan into a MEASUREMENT.

RANDU is a linear congruential generator (a = 65539, m = 2^31) famous for being
broken: its triples fall on 15 planes in the unit cube. It is one of the most
thoroughly documented failures in the history of pseudorandom generation. If the
ARS nearest-neighbour battery cannot tell RANDU from ChaCha20, then the battery's
blindness is not hypothetical -- it is exhibited, on a generator whose defect is
textbook.

That is the difference between "there exists structure we cannot see" as a
theorem and as an artifact.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                           ║
║                                                                              ║
║ P1  PREMISE — THE BATTERY CAN FAIL. A periodic control is rejected as        ║
║     Poisson at every seed (KS p < 0.01 against the Poisson NNS CDF). If the  ║
║     battery cannot reject anything, every null below is non-evidence and     ║
║     nothing in this cell is readable.                                        ║
║                                                                              ║
║ E1  THE CSPRNG READS POISSON at every seed: best-fit class is Poisson and    ║
║     KS p > 0.01. A miss here is, by the argument above, an instrument bug.   ║
║                                                                              ║
║ E2  AND SO DOES MERSENNE TWISTER. MT19937 is indistinguishable from the      ║
║     CSPRNG on this battery: it too reads Poisson at every seed. A NULL, and  ║
║     a powered one -- P1 establishes the battery can reject.                  ║
║                                                                              ║
║ E3  AND SO DOES RANDU. The textbook-broken generator reads Poisson at every  ║
║     seed. THIS IS THE CELL: the battery's incompleteness stops being a       ║
║     theorem about all finite batteries and becomes a measured property of    ║
║     THIS one, exhibited on a documented defect.                              ║
║                                                                              ║
║ M1  MECHANISM — THE STRUCTURE IS THERE AND THE INSTRUMENT IS THE WRONG       ║
║     SHAPE FOR IT. RANDU's defect is a 3-dimensional lattice; the NNS battery ║
║     is a 1-dimensional marginal test. So a 3-D lattice statistic on THE SAME ║
║     STREAM must catch RANDU decisively (>= 10x the spread of the CSPRNG's    ║
║     value) while the NNS battery does not. Without this arm, E3 is           ║
║     "we found nothing", which is compatible with there being nothing to      ║
║     find. With it, E3 is "the defect is present, measured, and invisible to  ║
║     this instrument" -- the confound constructed rather than assumed.        ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT THIS DOES NOT CLAIM. Not that the ARS battery is bad -- a 1-D marginal test
is not supposed to see a 3-D lattice, and the mechanism arm says so. It claims
that the battery's reach is BOUNDED and now has a witness, so "there is always
structure the instruments miss" can be cited to an artifact instead of to a
theorem about batteries in general.

TIER. The CSPRNG entry is THEOREM-tier for its Poisson label: exponential gaps
from uniform variates is exactly a homogeneous Poisson process, by construction
and not by conjecture. What is cryptographic rather than proven is only the
claim that the GENERATOR is indistinguishable from uniform.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PRE_ROLE,    # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE)
from universality import (nns_cdf_poisson, nns_cdf_goe,           # noqa: E402
                          nns_cdf_gue, _ks_pvalue)

N_POINTS = 400
SEEDS = list(range(20240517, 20240517 + 12))
KS_ALPHA = 0.01
LATTICE_FACTOR = 10.0

INSTRUMENT = Model("ARS nearest-neighbour battery on generator-driven Poisson "
                   "processes", [
    Param("generator", TESTED,
          sweep=["csprng_chacha20", "mt19937", "randu_lcg", "periodic_control"],
          why="THE ONLY THING THAT VARIES. The transform to a Poisson process "
              "is identical for all four, so any difference in the reading is "
              "a difference the battery sees in the GENERATOR"),
    Param("n_points", DECLARED, value=N_POINTS,
          why="400, the panel's standing size, so these entries are "
              "commensurable with the existing calibrator zoo"),
    Param("seeds", DECLARED, value=len(SEEDS),
          why="12 seeds; every arm is asserted AT EVERY SEED rather than on a "
              "mean, because a battery that reads Poisson on average while "
              "failing on one seed has not read Poisson"),
    Param("ks_alpha", DECLARED, value=KS_ALPHA,
          why="0.01 on the KS p-value. Deliberately permissive for the NULL "
              "arms (E1-E3), which makes them EASIER to pass and so makes P1's "
              "rejection of the periodic control the load-bearing check"),
])


def _uniforms_csprng(n):
    """OS CSPRNG: /dev/urandom, ChaCha20 on Linux. Not seedable, by design --
    a seeded CSPRNG stream would be reproducible and that is precisely the
    property this entry is NOT claiming to have."""
    raw = os.urandom(8 * n)
    ints = np.frombuffer(raw, dtype=np.uint64)
    return (ints >> np.uint64(11)) * (1.0 / 9007199254740992.0)


def _uniforms_mt(n, seed):
    return np.random.RandomState(seed).random_sample(n)


def _uniforms_randu(n, seed):
    """RANDU: x_{k+1} = 65539 x_k mod 2^31. Textbook-broken -- its consecutive
    triples lie on 15 planes. Included precisely because its defect is
    documented, so a null result here is a statement about the instrument."""
    m = 2 ** 31
    x = (2 * seed + 1) % m or 1
    out = np.empty(n)
    for i in range(n):
        x = (65539 * x) % m
        out[i] = x / m
    return out


def events_from_uniforms(u):
    """Uniforms -> exponential gaps -> unit-mean event times. Exactly the
    construction extractor_distinctness._gen_poisson uses, so the Poisson label
    is theorem-tier by construction."""
    u = np.clip(u, 1e-15, 1 - 1e-15)
    gaps = -np.log(u)
    return np.cumsum(gaps)


def _periodic(n, seed):
    rng = np.random.default_rng(seed)
    return np.sort(np.arange(1, n + 1) * 7.0 + 0.05 * rng.standard_normal(n))


def spacings(ev):
    d = np.diff(np.sort(ev))
    m = d.mean()
    return d / m if m > 0 else d


def classify(s):
    def ks(cdf):
        x = np.sort(s)
        n = x.size
        return float(np.max(np.abs(np.arange(1, n + 1) / n - cdf(x))))
    kp, ko, ku = ks(nns_cdf_poisson), ks(nns_cdf_goe), ks(nns_cdf_gue)
    best = min([("Poiss", kp), ("GOE", ko), ("GUE", ku)], key=lambda t: t[1])[0]
    return dict(ks_p=kp, ks_o=ko, ks_u=ku, best=best,
                pv_p=float(_ks_pvalue(kp, s.size)))


def lattice_stat(u):
    """M1's 3-D probe: RANDU's consecutive triples satisfy
    x_{k+2} - 6 x_{k+1} + 9 x_k = 0 (mod 1). Measure how tightly the triples
    concentrate on that relation. A generator with no such relation spreads
    the residual uniformly; RANDU pins it to a handful of planes."""
    if u.size < 3:
        return float("nan")
    r = (u[2:] - 6.0 * u[1:-1] + 9.0 * u[:-2]) % 1.0
    # distance to the nearest of the 15 planes k/15
    d = np.abs(r[:, None] - np.arange(16)[None, :] / 15.0).min(axis=1)
    return float(np.mean(d))


rows = []
for seed in SEEDS:
    ug = {"csprng_chacha20": _uniforms_csprng(N_POINTS + 2),
          "mt19937": _uniforms_mt(N_POINTS + 2, seed),
          "randu_lcg": _uniforms_randu(N_POINTS + 2, seed)}
    for name, u in ug.items():
        c = classify(spacings(events_from_uniforms(u)))
        rows.append(dict(gen=name, seed=seed, lattice=lattice_stat(u), **c))
    c = classify(spacings(_periodic(N_POINTS, seed)))
    rows.append(dict(gen="periodic_control", seed=seed,
                     lattice=float("nan"), **c))

by = {}
for r in rows:
    by.setdefault(r["gen"], []).append(r)

print(INSTRUMENT.report())
print(f"\n{len(SEEDS)} seeds x {N_POINTS} points, NNS battery vs Poisson/GOE/GUE\n")
print(f"{'generator':>20s} {'best (all seeds)':>18s} {'min pv_P':>9s} "
      f"{'reads Poisson':>14s} {'lattice mean-dist':>18s}")
for g, v in by.items():
    bests = sorted({r["best"] for r in v})
    minpv = min(r["pv_p"] for r in v)
    npois = sum(1 for r in v if r["best"] == "Poiss" and r["pv_p"] > KS_ALPHA)
    lat = [r["lattice"] for r in v if not np.isnan(r["lattice"])]
    ls = f"{float(np.mean(lat)):.5f}" if lat else "n/a"
    print(f"{g:>20s} {','.join(bests):>18s} {minpv:>9.4f} "
          f"{npois:>8d}/{len(v):<5d} {ls:>18s}")

n = len(SEEDS)
p1 = sum(1 for r in by["periodic_control"] if r["pv_p"] < KS_ALPHA)
e1 = sum(1 for r in by["csprng_chacha20"]
         if r["best"] == "Poiss" and r["pv_p"] > KS_ALPHA)
e2 = sum(1 for r in by["mt19937"]
         if r["best"] == "Poiss" and r["pv_p"] > KS_ALPHA)
e3 = sum(1 for r in by["randu_lcg"]
         if r["best"] == "Poiss" and r["pv_p"] > KS_ALPHA)
lat_c = float(np.mean([r["lattice"] for r in by["csprng_chacha20"]]))
lat_r = float(np.mean([r["lattice"] for r in by["randu_lcg"]]))
lat_ratio = lat_c / max(lat_r, 1e-12)

P1 = Bar("seeds where the periodic control is REJECTED as Poisson", n,
         floor=0, ceiling=n,
         why=f"a count over the {n} seeds; 0 is attainable by a battery that "
             "rejects nothing, which is exactly the failure this arm exists to "
             "exclude before any null below is read")
E1 = Bar("seeds where the CSPRNG reads Poisson", n, floor=0, ceiling=n,
         why=f"a count over the {n} seeds; both ends attainable")
E2 = Bar("seeds where MT19937 reads Poisson", n, floor=0, ceiling=n,
         why="same count; a MISS here would mean the battery distinguishes "
             "Mersenne Twister from a stream cipher, which would be a finding "
             "about the battery's reach in the opposite direction")
E3 = Bar("seeds where RANDU reads Poisson", n, floor=0, ceiling=n,
         why="same count; a MISS here would mean the battery DOES catch the "
             "textbook lattice defect and its reach is wider than claimed")
M1 = Bar("CSPRNG lattice-spread over RANDU lattice-spread", LATTICE_FACTOR,
         floor=0.0, ceiling=1e6,
         why="a ratio of mean distances to RANDU's 15 planes; 1.0 is 'no "
             "lattice structure detected' and is attainable, so the arm can "
             "fail and would then leave E3 as 'we found nothing'")

sP, s1, s2, s3 = P1.score(p1), E1.score(e1), E2.score(e2), E3.score(e3)
sM = M1.score(lat_ratio)
print()
for b, v, f in ((P1, p1, "{:.0f}"), (E1, e1, "{:.0f}"), (E2, e2, "{:.0f}"),
                (E3, e3, "{:.0f}"), (M1, lat_ratio, "{:.1f}")):
    print("  " + b.line(v, f))

arms = [Arm.from_bar(sP, PRE_ROLE, claim="the battery can reject something"),
        Arm.from_bar(s1, EX_ROLE, claim="the CSPRNG reads Poisson, so any "
                                        "reading here would be an instrument "
                                        "bug"),
        Arm.from_bar(s2, EX_ROLE, claim="and Mersenne Twister is "
                                        "indistinguishable from it"),
        Arm.from_bar(s3, EX_ROLE, claim="and so is RANDU, whose defect is "
                                        "textbook"),
        Arm.from_bar(sM, MECH_ROLE, claim="because the defect is a 3-D lattice "
                                          "and the battery is a 1-D marginal")]
v = compose(arms, holds="ONE_SIDED_CALIBRATOR_SEATED_BLIND_SPOT_EXHIBITED",
            fails="BATTERY_DISTINGUISHES_THE_GENERATORS")
print(f"\nVERDICT: {v['citation']}")

with redpath("generator x seed classifications", expect_min=40) as rp:
    rp.observed(len(rows))

json.dump(dict(n_points=N_POINTS, seeds=SEEDS, ks_alpha=KS_ALPHA,
               instrument=INSTRUMENT.seal(), rows=rows,
               periodic_rejected=p1, csprng_poisson=e1, mt_poisson=e2,
               randu_poisson=e3,
               lattice_csprng=lat_c, lattice_randu=lat_r,
               lattice_ratio=lat_ratio,
               tier_note="CSPRNG entry is THEOREM-tier for its Poisson label "
                         "(exponential gaps from uniforms IS a homogeneous "
                         "Poisson process, by construction). What is "
                         "cryptographic rather than proven is only that the "
                         "generator is indistinguishable from uniform.",
               ml_random_note="the ideal calibrator -- a Martin-Lof random "
                              "sequence -- is UNCOMPUTABLE and cannot be "
                              "built; this substitutes cryptographic "
                              "one-sidedness for computability-theoretic",
               bars={s["name"]: s for s in (sP, s1, s2, s3, sM)},
               verdict=v["head"], composed=v),
          open(f"{ROOT}/csprng_calibrator.json", "w"), indent=1)
print("\nwritten -> csprng_calibrator.json")
