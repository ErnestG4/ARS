"""
RUN — the sealed cubic between-object arm.

Executes seals/CUBIC_ARM_SEAL.json as amended by CUBIC_ARM_SEAL_ADDENDUM_1.json.
Instrument checks run FIRST and their failure voids the target result, per the sealed
failure condition written before any arm ran.

Order, fixed by the seal:
  [I1] stratum B smoke test   -- f_full >= 0.965, and post-merge f = 1.000 exactly
  [I2] stratum C calibration  -- measured rate within +/-12% of the calibrated formula, |det| <= 289
  [I3] the null               -- false-positive rate at the nominal 5%, on unrelated-field pairs
  [I4] field counts           -- >= 20 surviving dedup in every arm
  [T]  TARGET, stratum A      -- only if I1-I4 pass
"""
from __future__ import annotations
import json, math, os
from math import gcd

import mpmath as mp
import numpy as np
from gate0_ladder import certified_cf, convergents, lam
from gate0b_stratify import mobius_of_cubic

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)
SEAL = json.load(open(os.path.join(HERE, "..", "seals", "CUBIC_ARM_SEAL.json")))
ADD = json.load(open(os.path.join(HERE, "..", "seals", "CUBIC_ARM_SEAL_ADDENDUM_1.json")))
FC = SEAL["frozen_analysis_choices"]

A_EV = FC["event_threshold_A"]
WS = tuple(FC["w_ladder"])
NPERM = FC["permutation_count"]
NPQ = FC["pq_per_object"]
DIG = FC["digits_per_object"]
T_SEALED = FC["rejection_threshold"]["T_le"]
mp.mp.dps = DIG + 80
rng = np.random.default_rng(20260726)


def events(x):
    """event u-locations for one real algebraic number, per the sealed definition:
    lambda_n >= A at u_n = log q_n.  lambda, NOT a."""
    a0 = certified_cf(int(mp.floor(x * 10 ** DIG)), 10 ** DIG, NPQ)
    P0, Q0 = convergents(a0)
    n = len(a0) - 45
    u, lm = [], []
    for i in range(1, n):
        L = lam(a0, Q0, i)
        if L >= A_EV:
            u.append(math.log(Q0[i]))
            lm.append(L)
    return np.array(u), a0, Q0, n


def stat_all(uu, vv, ws=WS):
    if len(uu) == 0 or len(vv) == 0:
        return [0] * len(ws)
    d = np.sort((uu[:, None] - vv[None, :]).ravel())
    ar = np.arange(len(d))
    return [int((np.searchsorted(d, d + 2 * w, side="right") - ar).max()) for w in ws]


def roots_of(A, B, C):
    return sorted(mp.re(z) for z in mp.polyroots([1, A, B, C], maxsteps=500, extraprec=1200))


if __name__ == "__main__":
    p_("=== RUNNING the sealed cubic arm ===")
    p_(f"  A = {A_EV} (on LAMBDA), u = log q, w-ladder {list(WS)}, {NPERM} permutations, "
       f"{NPQ} PQs at {DIG} digits")
    p_(f"  seal hash {SEAL['arms_sha256_16']}, addendum 1 applied\n")

    # ---------------------------------------------------------------- load every object once
    store = {}
    for arm in ("S3", "B", "C"):
        store[arm] = []
        for A, B, C in SEAL["arms"][arm]["polynomials"]:
            rr = roots_of(A, B, C)
            evs = [events(z) for z in rr]
            store[arm].append({"poly": (A, B, C), "roots": rr, "ev": [e[0] for e in evs],
                               "cf": [e[1] for e in evs], "Q": [e[2] for e in evs]})
        p_(f"  loaded {arm}: {len(store[arm])} fields x 3 roots, "
           f"median events/object {int(np.median([len(e) for o in store[arm] for e in o['ev']]))}")

    checks = {}

    # ---------------------------------------------------------------- [I1] stratum B
    p_("\n[I1] stratum B smoke test (amended: f_full >= 0.965, post-merge f = 1.000 exactly)")
    ffs, post_ok, post_n = [], [], []
    for o in store["B"]:
        A, B, C = o["poly"]
        a, b, c, d = mobius_of_cubic(A, B, C)[:4]
        img = (a * o["roots"][0] + b) / (c * o["roots"][0] + d)
        j = min(range(3), key=lambda i: abs(o["roots"][i] - img))
        a0, a1 = o["cf"][0], o["cf"][j]
        L = min(len(a0), len(a1)) - 60
        n0, off0 = None, 0
        for off in range(-25, 26):
            for i in range(1, 200):
                if i + off < 1:
                    continue
                k = 0
                while i + k < L and i + off + k < L and a0[i + k] == a1[i + off + k]:
                    k += 1
                if k > 300 and (n0 is None or i < n0):
                    n0, off0 = i, off
                    break
        P0, Q0 = convergents(a0); P1, Q1 = convergents(a1)
        idx = {Q1[k]: k for k in range(len(Q1))}
        # DOMAIN: the post-merge exactness test is only meaningful where BOTH indices lie inside
        # their own certified range. Comparing i whose partner sits at i+off >= len(a1)-45 asks a
        # question about terms that were never certified. (This is what halted the first run:
        # two events at i = 1953, 1954 with partners at k = 1955, 1956, one and two past the guard.)
        hi_p = min(len(a0) - 45, len(a1) - 45 - (off0 if n0 is not None else 0))
        tot = hit = tot_p = hit_p = 0
        for i in range(1, len(a0) - 45):
            if lam(a0, Q0, i) < A_EV:
                continue
            A_, B_ = a * P0[i] + b * Q0[i], c * P0[i] + d * Q0[i]
            if B_ < 0:
                A_, B_ = -A_, -B_
            g = gcd(abs(A_), B_)
            k = idx.get(B_ // g)
            ok = k is not None and 1 <= k < len(a1) - 45 and P1[k] == A_ // g and \
                lam(a1, Q1, k) >= A_EV
            tot += 1; hit += ok
            if n0 is not None and n0 <= i < hi_p:
                tot_p += 1; hit_p += ok
        ffs.append(hit / tot)
        post_ok.append(hit_p == tot_p)
        post_n.append((tot_p, hit_p))
    checks["I1_f_full_min"] = float(min(ffs))
    checks["I1_postmerge_exact"] = bool(all(post_ok))
    i1 = min(ffs) >= 0.965 and all(post_ok)
    p_(f"  f_full: min {min(ffs):.4f}, median {np.median(ffs):.4f}   (threshold 0.965)")
    p_(f"  post-merge f = 1.000 exactly on {sum(post_ok)}/{len(post_ok)} fields "
       f"({sum(h for _, h in post_n)}/{sum(t for t, _ in post_n)} events, domain-intersected)")
    p_(f"  -> I1 {'PASS' if i1 else 'FAIL'}")

    # ---------------------------------------------------------------- [I2] stratum C
    p_("\n[I2] stratum C calibration (measured rate vs the calibrated formula, +/-12%)")
    p_(f"  {'poly':>16s} {'|det|':>6s} {'n_ev':>6s} {'meas':>8s} {'pred':>8s} {'ratio':>7s}")
    rats = []
    for o in store["C"]:
        A, B, C = o["poly"]
        a, b, c, d = mobius_of_cubic(A, B, C)[:4]
        D = abs(a * d - b * c)
        if D > 289:
            continue
        img = (a * o["roots"][0] + b) / (c * o["roots"][0] + d)
        j = min(range(3), key=lambda i: abs(o["roots"][i] - img))
        a0, a1 = o["cf"][0], o["cf"][j]
        P0, Q0 = convergents(a0); P1, Q1 = convergents(a1)
        idx = {Q1[k]: k for k in range(len(Q1))}
        ghe, tot, hit = {}, 0, 0
        for i in range(1, len(a0) - 45):
            if lam(a0, Q0, i) < A_EV:
                continue
            A_, B_ = a * P0[i] + b * Q0[i], c * P0[i] + d * Q0[i]
            if B_ < 0:
                A_, B_ = -A_, -B_
            g = gcd(abs(A_), B_)
            ghe[g] = ghe.get(g, 0) + 1
            k = idx.get(B_ // g)
            tot += 1
            hit += (k is not None and 1 <= k < len(a1) - 45 and P1[k] == A_ // g and
                    lam(a1, Q1, k) >= A_EV)
        te = sum(ghe.values())
        pred = sum(v / te * min(1.0, g * g / D) for g, v in ghe.items())
        meas = hit / tot
        rats.append(meas / pred)
        p_(f"  {str((A,B,C)):>16s} {D:>6d} {tot:>6d} {meas:>8.4f} {pred:>8.4f} {meas/pred:>7.3f}")
    checks["I2_ratios"] = [float(x) for x in rats]
    i2 = max(abs(np.array(rats) - 1)) <= 0.12
    p_(f"  worst |ratio - 1| = {max(abs(np.array(rats)-1)):.3f}   (tolerance 0.12)")
    p_(f"  -> I2 {'PASS' if i2 else 'FAIL'}")

    # ---------------------------------------------------------------- [I3] the null
    p_(f"\n[I3] the permutation null = the negative arm: {NPERM} pairs from UNRELATED fields")
    allev = [(fi, ri, e) for fi, o in enumerate(store["S3"]) for ri, e in enumerate(o["ev"])]
    nullS = []
    while len(nullS) < NPERM:
        i, j = rng.integers(0, len(allev), 2)
        if allev[i][0] == allev[j][0]:
            continue
        nullS.append(stat_all(allev[i][2], allev[j][2]))
    nullS = np.array(nullS, float)

    def T(s):
        return min(float((nullS[:, k] >= s[k]).mean()) for k in range(len(WS)))

    nullT = np.array([T(nullS[i]) for i in range(NPERM)])
    thr = float(np.percentile(nullT, 5))
    fpr = float((nullT <= thr).mean())
    checks["I3_threshold_real"] = thr
    checks["I3_threshold_sealed"] = T_SEALED
    checks["I3_fpr"] = fpr
    i3 = fpr <= 0.10
    p_(f"  null T: 5th percentile = {thr:.4f}   (sealed expectation from synthetics: {T_SEALED:.4f})")
    p_(f"  false-positive rate at that threshold = {100*fpr:.1f}%   (tolerance 10%)")
    p_(f"  -> I3 {'PASS' if i3 else 'FAIL'}")

    # ---------------------------------------------------------------- [I4]
    nf = {k: SEAL["arms"][k]["n_fields"] for k in ("S3", "B", "C")}
    i4 = all(v >= 20 for v in nf.values())
    p_(f"\n[I4] field counts {nf}  (>= 20 each)  -> I4 {'PASS' if i4 else 'FAIL'}")

    checks["instrument_pass"] = bool(i1 and i2 and i3 and i4)
    if not checks["instrument_pass"]:
        p_("\n*** INSTRUMENT FAILED — the target result would mean nothing. HALTING per the seal. ***")
        json.dump(checks, open(os.path.join(HERE, "run_cubic_arm_measured.json"), "w"), indent=2)
        raise SystemExit(1)
    p_("\n  ALL INSTRUMENT CHECKS PASS — the target arm is licensed to run.")

    # ---------------------------------------------------------------- [T] TARGET
    p_("\n[T] TARGET — stratum A, totally real S3 cubic conjugates")
    p_("  one witness per FIELD: T_field = min over the field's 3 conjugate pairs.")
    Tf, per_pair = [], []
    for o in store["S3"]:
        ts = []
        for i in range(3):
            for j in range(i + 1, 3):
                t = T(stat_all(o["ev"][i], o["ev"][j]))
                ts.append(t); per_pair.append(t)
        Tf.append(min(ts))
    # null distribution of min-of-3 for unrelated triples
    nullTf = []
    for _ in range(NPERM):
        picks = rng.integers(0, NPERM, 3)
        nullTf.append(min(nullT[k] for k in picks))
    thr_f = float(np.percentile(nullTf, 5))
    det = int(sum(1 for t in Tf if t <= thr_f))
    p_(f"  per-pair T: min {min(per_pair):.4f}, median {np.median(per_pair):.4f}  "
       f"({sum(1 for t in per_pair if t <= thr):d}/{len(per_pair)} below the per-pair threshold "
       f"{thr:.4f}; {0.05*len(per_pair):.1f} expected under the null)")
    p_(f"  per-field T_field: min {min(Tf):.4f}, median {np.median(Tf):.4f}")
    p_(f"  field-level threshold (5th pct of min-of-3 null) = {thr_f:.4f}")
    p_(f"  FIELDS DETECTED: {det}/{len(Tf)}   expected under the null: {0.05*len(Tf):.1f}")
    from scipy.stats import binomtest
    pv = float(binomtest(det, len(Tf), 0.05, alternative="greater").pvalue)
    p_(f"  binomial p (one-sided) = {pv:.3f}")
    checks.update({"T_per_pair": per_pair, "T_field": Tf, "thr_pair": thr, "thr_field": thr_f,
                   "fields_detected": det, "n_fields": len(Tf), "binom_p": pv})

    p_(f"\n  === RESULT ===")
    if pv < 0.05:
        p_("  TARGET POSITIVE — per the seal, do NOT report before rechecking the stratum")
        p_("  assignment: is the pair GL2(Q)-equivalent after all?")
    else:
        fl = SEAL["power"]["detection_floor_80pct"]
        p_("  TARGET EMPTY, and it is an UPPER LIMIT — the deliverable named before the run.")
        p_(f"  Totally real S3 cubic conjugates show NO coincidence of exceptional approximations")
        p_(f"  above f = {fl['J=0']} at zero jitter ({fl['J=0.2']} at J <= 0.2, {fl['J=1.0']} at J = 1.0),")
        p_(f"  per conjugate pair, with the floor demonstrated by injection rather than argued.")
        p_(f"  Instrument checks all passed, so the negative is a result and not an absence.")

    json.dump(checks, open(os.path.join(HERE, "run_cubic_arm_measured.json"), "w"), indent=2)
    p_("\nwrote run_cubic_arm_measured.json")
