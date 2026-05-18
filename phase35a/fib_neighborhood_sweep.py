"""
phase35a/fib_neighborhood_sweep.py — OVERNIGHT Fibonacci-neighborhood structure run
(Will brief 2026-05-18). Discriminates the rate run's flat-then-steep
sup_spread decay: localization-length CROSSOVER vs log-periodic/
COMMENSURABILITY structure tied to the golden-mean continued fraction.
Logically UPSTREAM of any large-N rate extrapolation (ladder
representativeness is unknown until this runs).

EXACT rate-run setup UNCHANGED (clean controlled experiment; N the ONLY
independent variable): golden-mean θ, λ_sub=0.5/λ_sup=1.5, dense
period-0.5-confirmed α-null (16 φ over [0,0.5)), L_iter=1e5. SCOPING /
instrument N-behaviour characterisation — asymmetric label, NEVER a
finding; OUT: large-N rate extrapolation, sensitivity re-measurement,
any AM result. brief-and-hold; Class II blocked; no §3 adjudication.

Graded design (timing-sized, ~8h, completion-priority — smallest rungs
first, incremental checkpoint after EVERY N-point so an overrun loses
only the expensive top):
  full neighbourhood  (cluster±{1,2,3,5,8} + interval@¼,½,¾): F16..F20
  tight-cluster only  (±{1,2,3,5,8}, 11 pt):                  F21..F23
  reduced tight       (±{1,3,8}, 7 pt):                        F24
Triple per N: sub_spread, sup_spread, gap (+EXACT-crit). Sub-question:
the gap's own F_n structure (gap/sub_mean/sup_mean tracked per N).
"""
from __future__ import annotations
import os, sys, json, time, traceback
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from unfold_rotnum import am_eigs, unfold_rotnum, W1d, GOLDEN

LAM_SUB, LAM_SUP = 0.50, 1.50
LITER = 100_000
PHIS = list(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 6))  # exact period-0.5
OUT = os.path.join(HERE, "fib_neighborhood_results.json")


def fib(kmax):
    F = [0, 1]
    while len(F) <= kmax:
        F.append(F[-1] + F[-2])
    return F
FIB = fib(26)
assert FIB[16] == 987 and FIB[24] == 46368 and FIB[21] == 10946


def ensemble(lam, N):
    vals = []
    for phi in PHIS:
        e = am_eigs(lam, int(N), phi)
        vals.append(W1d(unfold_rotnum(e, lam, GOLDEN, LITER, phis=(phi,))))
    a = np.asarray(vals)
    return float(a.min()), float(a.max()), float(a.mean())


def measure(N):
    smn, smx, smean = ensemble(LAM_SUB, N)
    pmn, pmx, pmean = ensemble(LAM_SUP, N)
    sub_spread = smx - smn
    sup_spread = pmx - pmn
    gap = pmn - smx
    crit = bool(gap > 0 and gap >= max(sub_spread, sup_spread))
    return {"N": int(N), "sub_spread": round(sub_spread, 7),
            "sup_spread": round(sup_spread, 7), "gap": round(gap, 7),
            "sub_mean": round(smean, 7), "sup_mean": round(pmean, 7),
            "exact_crit": crit}


CLUSTER_FULL = [1, 2, 3, 5, 8]
CLUSTER_RED = [1, 3, 8]


def rung_points(n, mode):
    Fn = FIB[n]
    offs = CLUSTER_FULL if mode in ("full", "tight") else CLUSTER_RED
    pts = [Fn] + [Fn + d for d in offs] + [Fn - d for d in offs]
    kinds = {Fn: "Fn"}
    for d in offs:
        kinds[Fn + d] = f"+{d}"; kinds[Fn - d] = f"-{d}"
    if mode == "full":
        Fn1 = FIB[n + 1]
        for fr in (0.25, 0.5, 0.75):
            p = int(round(Fn + fr * (Fn1 - Fn)))
            pts.append(p); kinds[p] = f"int{fr}"
    return sorted(set(pts)), kinds


# rung -> mode (smallest first; completion-priority)
PLAN = ([(n, "full") for n in range(16, 21)]      # F16..F20 full
        + [(n, "tight") for n in range(21, 24)]   # F21..F23 tight-11
        + [(24, "reduced")])                       # F24 tight-7


def run():
    t0 = time.time()
    rec = {"scoping_instrument_Nbehaviour": True, "exact_rate_setup": True,
           "lam_sub": LAM_SUB, "lam_sup": LAM_SUP, "L": LITER, "nphi": len(PHIS),
           "plan": [(FIB[n], m) for n, m in PLAN], "rungs": {}}
    print("=" * 84)
    print("FIBONACCI-NEIGHBOURHOOD STRUCTURE RUN — overnight, completion-priority")
    print(f"  exact rate setup: λ {LAM_SUB}/{LAM_SUP}, L={LITER}, "
          f"{len(PHIS)} φ∈[0,0.5) ; N = only variable")
    print("=" * 84, flush=True)
    for n, mode in PLAN:
        Fn = FIB[n]
        pts, kinds = rung_points(n, mode)
        rrec = {"F_n": Fn, "mode": mode, "points": []}
        print(f"\n── F_{n}={Fn}  [{mode}]  {len(pts)} N-points "
              f"({time.time()-t0:.0f}s elapsed)", flush=True)
        for N in pts:
            ts = time.time()
            try:
                m = measure(N)
            except Exception as ex:
                m = {"N": int(N), "error": repr(ex)}
                traceback.print_exc()
            m["kind"] = kinds.get(N, "?")
            m["wall_s"] = round(time.time() - ts, 1)
            rrec["points"].append(m)
            sp = m.get("sup_spread", "ERR"); gp = m.get("gap", "ERR")
            print(f"   N={N:7d} [{m['kind']:>7}] sup_spread={sp} gap={gp} "
                  f"crit={m.get('exact_crit','?')} ({m['wall_s']}s)", flush=True)
            rec["rungs"][str(Fn)] = rrec            # checkpoint after EVERY point
            rec["elapsed_s"] = round(time.time() - t0, 0)
            json.dump(rec, open(OUT, "w"), indent=1)
        # per-rung quick read (within-neighbourhood variation = the discriminant)
        ss = [p["sup_spread"] for p in rrec["points"] if "sup_spread" in p]
        gg = [p["gap"] for p in rrec["points"] if "gap" in p]
        fn_pt = next((p for p in rrec["points"] if p.get("kind") == "Fn"), None)
        if ss and fn_pt and "sup_spread" in fn_pt:
            rrec["sup_spread_neigh_range"] = round(max(ss) - min(ss), 7)
            rrec["sup_spread_at_Fn"] = fn_pt["sup_spread"]
            rrec["gap_neigh_range"] = round(max(gg) - min(gg), 7) if gg else None
            print(f"   ↳ F_{n}: sup_spread@Fn={fn_pt['sup_spread']} "
                  f"neigh-range={rrec['sup_spread_neigh_range']} "
                  f"gap-neigh-range={rrec.get('gap_neigh_range')}", flush=True)
        json.dump(rec, open(OUT, "w"), indent=1)
    rec["total_s"] = round(time.time() - t0, 0)
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    print(f"DONE {rec['total_s']}s. Per-rung: sup_spread@Fn, neigh-range, "
          f"gap-neigh-range in JSON. Outcome-map read = the report (pre-registered:")
    print("  neigh flat ⇒ crossover/ladder-representative ; sharp cluster ⇒")
    print("  commensurability band-edge ; smooth interval ⇒ log-periodic).")
    print("  SCOPING / instrument N-behaviour, NEVER a finding. brief-and-hold.")
    print("=" * 84)


if __name__ == "__main__":
    run()
