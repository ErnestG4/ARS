"""
GATE 0g — does a detection floor calibrated on strata B/C transfer to stratum A?

Reviewer: "B and C are closer than the cbrt m arm, but they're cyclic and the target is S3 --
different Galois module structure, different regulator behaviour. So a detection floor calibrated
on B/C is a floor for CYCLIC objects, and applying it to A assumes the marginal lambda-event
statistics match across Galois groups. Comparable across strata in one pass, and it either
licenses the transfer or doesn't."

This is the cross-substrate validity bridge: measure a SHARED anchor in both substrates.
The anchors that the floor actually depends on:
  [L] Levy:  log q_n / n  -> pi^2/(12 ln 2) = 1.18657.  Sets PQs per unit u.
  [E] tail:  P(lambda >= A) -> 1.4427/A (Bosma-Jager-Wiedijk, EXACT for A >= 2). Sets events per PQ.
  [R] events per unit u = [E]/[L]. THIS is the quantity the detector sees, and the only one that
      has to match for a floor to transfer.
  [K] Khinchin geometric mean -> 2.68545, as a fourth independent anchor.

NOT the sealed statistic. No cross-object correlation is computed here, and no pair of stratum-A
objects is ever brought together. Marginals are exactly what the literature already reports as
generic; the point here is the COMPARISON ACROSS STRATA, which is what licenses (or refuses) the
floor transfer.

Objects are taken with DISTINCT DISCRIMINANTS -- gate0e found the coefficient box yields many
polynomials per field, and correlated objects are one witness.
"""
from __future__ import annotations
import json, math, os

import mpmath as mp
from gate0_ladder import convergents, lam
from gate0b_stratify import mobius_of_cubic, disc, irreducible
from gate0e_precision import cf_of_mpf

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)
mp.mp.dps = 1260
NOBJ, A_EV = 24, 20
LEVY = math.pi ** 2 / (12 * math.log(2))
KHIN = 2.6854520010653064


def anchors(a0):
    """[L] Levy, [E] tail at A_EV, [R] events per unit u, [K] Khinchin -- one object."""
    P0, Q0 = convergents(a0)
    n = len(a0) - 45
    u_end = math.log(Q0[n - 1])
    lams = [lam(a0, Q0, i) for i in range(1, n)]
    nev = sum(1 for x in lams if x >= A_EV)
    gm = math.exp(sum(math.log(x) for x in a0[1:n]) / (n - 1))
    return {"levy": u_end / (n - 1), "tail": nev / (n - 1),
            "rate_u": nev / u_end, "khinchin": gm, "n_pq": n - 1, "n_ev": nev}


def _by_height(box):
    """enumerate coefficient triples in order of INCREASING height max(|A|,|B|,|C|).
    A raw triple loop returns a thin slice (every object sharing the smallest A), which is a
    sampling-frame defect of exactly the kind gate0f was about."""
    for h in range(1, box + 1):
        for A in range(-h, h + 1):
            for B in range(-h, h + 1):
                for C in range(-h, h + 1):
                    if max(abs(A), abs(B), abs(C)) == h:
                        yield A, B, C


def collect(kind, want=NOBJ, box=30):
    """distinct-discriminant objects, enumerated by increasing height: kind in {'S3','B','C'}."""
    out, seen = [], set()
    if True:
        if True:
            for A, B, C in _by_height(box):
                D = disc(A, B, C)
                if D <= 0 or D in seen or not irreducible(A, B, C):
                    continue
                sq = math.isqrt(D) ** 2 == D
                if kind == "S3":
                    if sq:
                        continue
                else:
                    if not sq:
                        continue
                    M = mobius_of_cubic(A, B, C)
                    if M is None:
                        continue
                    t = abs(M[4])
                    if (kind == "B") != (t == 1):
                        continue
                seen.add(D)
                out.append((A, B, C, D))
                if len(out) >= want:
                    return out
    return out


def mean_sem(v):
    m = sum(v) / len(v)
    s = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1) / len(v))
    return m, s


if __name__ == "__main__":
    p_("=== GATE 0g — do the marginal anchors match ACROSS GALOIS GROUPS? ===")
    p_(f"events at lambda >= {A_EV}; {NOBJ} objects per stratum, DISTINCT discriminants\n")

    res = {}
    for kind, lbl in (("S3", "A: S3 (target)"), ("B", "B: cyclic |t|=1"), ("C", "C: cyclic |t|>1")):
        objs = collect(kind)
        rows = []
        for A, B, C, D in objs:
            r = mp.polyroots([1, A, B, C], maxsteps=400, extraprec=800)
            rows.append(anchors(cf_of_mpf(sorted(mp.re(x) for x in r)[0])))
        res[kind] = {"label": lbl, "n_objects": len(rows),
                     "n_pq_total": sum(x["n_pq"] for x in rows),
                     "n_ev_total": sum(x["n_ev"] for x in rows)}
        for key in ("levy", "tail", "rate_u", "khinchin"):
            m, s = mean_sem([x[key] for x in rows])
            res[kind][key] = [m, s]
        p_(f"  {lbl:<18s} {len(rows):>3d} objects, {res[kind]['n_pq_total']:>6d} PQs, "
           f"{res[kind]['n_ev_total']:>5d} events")

    # REFERENCE for the LAMBDA tail is 1/(A ln2), NOT the Gauss-Kuzmin tail log2(1+1/A) for a.
    # P(theta <= z) = z/ln2 for z <= 1/2 (Bosma-Jager-Wiedijk) and theta = 1/lambda, so
    # P(lambda >= A) = 1/(A ln 2) = 1.4427/A exactly for A >= 2. Using the a-tail here was the
    # same a-versus-lambda convention slip the seal now fixes, and it manufactured a +2 sem offset.
    TAIL = 1.0 / (A_EV * math.log(2))
    ref = {"levy": LEVY, "tail": TAIL, "rate_u": TAIL / LEVY, "khinchin": KHIN}
    p_(f"\n  {'anchor':>10s} {'theory':>10s} " +
       "".join(f"{res[k]['label'].split(':')[0]:>18s}" for k in ("S3", "B", "C")))
    for key, nm in (("levy", "Levy"), ("tail", "P(lam>=A)"), ("rate_u", "ev/unit u"),
                    ("khinchin", "Khinchin")):
        cells = "".join(f"{res[k][key][0]:>11.5f}+-{res[k][key][1]:<6.5f}" for k in ("S3", "B", "C"))
        p_(f"  {nm:>10s} {ref[key]:>10.5f} {cells}")

    p_(f"\n  CROSS-STRATUM DIFFERENCES, in sem units (the gate: does the floor transfer?)")
    p_(f"  {'anchor':>10s} {'A vs B':>10s} {'A vs C':>10s} {'B vs C':>10s} {'A vs theory':>13s}")
    verdict = {}
    for key, nm in (("levy", "Levy"), ("tail", "P(lam>=A)"), ("rate_u", "ev/unit u"),
                    ("khinchin", "Khinchin")):
        def z(k1, k2):
            m1, s1 = res[k1][key]; m2, s2 = res[k2][key]
            return (m1 - m2) / math.sqrt(s1 * s1 + s2 * s2)
        zt = (res["S3"][key][0] - ref[key]) / res["S3"][key][1]
        verdict[key] = [z("S3", "B"), z("S3", "C"), z("B", "C"), zt]
        p_(f"  {nm:>10s} {z('S3','B'):>+10.2f} {z('S3','C'):>+10.2f} {z('B','C'):>+10.2f} "
           f"{zt:>+13.2f}")

    worst = max(abs(v) for k in ("levy", "tail", "rate_u", "khinchin") for v in verdict[k][:3])
    key_z = abs(verdict["rate_u"][0]), abs(verdict["rate_u"][1])
    p_(f"\n  worst |z| across all anchors and all stratum pairs: {worst:.2f}")
    p_(f"  the anchor the floor ACTUALLY depends on is  ev/unit u:  "
       f"A vs B {verdict['rate_u'][0]:+.2f}, A vs C {verdict['rate_u'][1]:+.2f} sem")
    ok = max(key_z) < 2.0
    p_(f"  -> {'TRANSFER LICENSED' if ok else 'TRANSFER NOT LICENSED'} on the event-rate anchor "
       f"at this power ({NOBJ} objects/stratum).")
    p_(f"  NOT claimed: that the strata are identical in every respect -- only that the ONE")
    p_(f"  quantity a coincidence floor depends on (events per unit u) agrees to "
       f"{max(key_z):.1f} sem, and the sem is {100*res['S3']['rate_u'][1]/res['S3']['rate_u'][0]:.1f}% "
       f"of the value, so the test could have caught a {100*2*res['S3']['rate_u'][1]/res['S3']['rate_u'][0]:.0f}% difference.")

    json.dump({"A_event": A_EV, "n_objects": NOBJ, "strata": res, "theory": ref,
               "cross_z": verdict, "transfer_licensed": bool(ok)},
              open(os.path.join(HERE, "gate0g_marginals_measured.json"), "w"), indent=2)
    p_("\nwrote gate0g_marginals_measured.json")
