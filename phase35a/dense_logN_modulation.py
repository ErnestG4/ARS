"""
phase35a/dense_logN_modulation.py — Step-1 DENSE-IN-LOG-N modulation
resolution (Will authorized 2026-05-19). The sound path to a real
lever-cost number: the Fib-neighbourhood run proved sup_spread & gap
are each [smooth inter-rung modulation] + [genuine underlying decay],
the Fibonacci ladder samples ONE phase ⇒ ladder rate-extrapolation
unsound. This resolves the modulation densely & uniformly in log N
(no ladder aliasing) so the decay can be separated and the rate pinned.

PRE-REGISTERED (before any result):
 EXACT QUESTION: N* where the DE-MODULATED decay of sup_spread drops
 below that of gap, worst-modulation-phase-safe; AND is the modulation
 log-φ-periodic so the decomposition is well-posed?
 Sampling: log-uniform N∈[6765,121393] (≈F20..F26), ~10 pts / log-φ
 period (lnφ=0.481211), N the ONLY variable; exact rate instrument
 UNCHANGED (λ_sub=0.5/λ_sup=1.5, 16 φ∈[0,0.5), L=1e5, golden θ);
 MP (18-worker), pure deterministic ⇒ bit-identical to serial.
 Analysis (tested, not assumed): raw dense data primary; FOLD-TEST
 period = lnφ (and 2·lnφ) by variance-explained of the folded mean
 (the exact log-periodicity test); decompose ONLY if fold clean —
 decay = smooth monotone (power-law vs linear-in-lnN tested, residuals
 reported), modulation = empirical folded waveform (non-parametric, NO
 imposed sinusoid); same for gap; N* = a BAND from de-modulated decays
 at the WORST modulation phase + residual/decay-law uncertainty, NEVER
 a single false-precise number; honest terminals pre-allowed:
 cleanly-pinned / bounded-but-wide / not-log-φ-periodic-⇒-not-pinnable
 (a legitimate characterised negative). Script dumps dense data + the
 fold-collapse diagnostic; the decomposition/N*-band read is the
 report, fully disciplined.

SCOPING / lever-cost. NOT a discovery, NOT §3, no stamping, Class II
blocked, brief-and-hold; OUT = sensitivity re-verdict / any AM result.
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
import sys, json, time, math
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from unfold_rotnum import am_eigs, unfold_rotnum, W1d, GOLDEN

WORKERS = 18
LAM = {"sub": 0.50, "sup": 1.50}
LITER = 100_000
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 6))
LNPHI = math.log((1 + 5 ** 0.5) / 2)               # ln φ ≈ 0.481211
N_LO, N_HI = 6765, 121393                           # ≈ F20 .. F26
PTS_PER_PERIOD = 10
OUT = os.path.join(HERE, "dense_logN_results.json")


def grid():
    nper = math.log(N_HI / N_LO) / LNPHI
    npts = int(round(nper * PTS_PER_PERIOD)) + 1
    xs = np.linspace(math.log(N_LO), math.log(N_HI), npts)
    Ns = sorted(set(int(round(math.exp(x))) for x in xs))
    return Ns


def task(arg):
    N, reg, lam, phi = arg
    try:
        e = am_eigs(lam, int(N), float(phi))
        w = float(W1d(unfold_rotnum(e, lam, GOLDEN, LITER, phis=(float(phi),))))
        return (N, reg, float(phi), w, None)
    except Exception as ex:
        return (N, reg, float(phi), None, repr(ex))


def main():
    t0 = time.time()
    Ns = grid()
    tasks = [(N, reg, LAM[reg], ph) for N in Ns for reg in ("sub", "sup")
             for ph in PHIS]
    print("=" * 88)
    print(f"DENSE-IN-LOG-N MODULATION RESOLUTION — {WORKERS}w/24core, "
          f"thread-pinned (non-disruptive)")
    print(f"  log-uniform N∈[{N_LO},{N_HI}] ~{PTS_PER_PERIOD}/log-φ-period "
          f"({len(Ns)} N-pts, {len(tasks)} pure tasks, bit-identical-serial)")
    print(f"  exact rate instrument UNCHANGED ; N the only variable")
    print("=" * 88, flush=True)
    acc = {N: {"sub": {}, "sup": {}} for N in Ns}
    rec = {"scoping_lever_cost": True, "exact_rate_setup": True,
           "parallel_bit_identical": True, "workers": WORKERS, "lam": LAM,
           "L": LITER, "nphi": len(PHIS), "lnphi": LNPHI,
           "N_lo": N_LO, "N_hi": N_HI, "pts_per_period": PTS_PER_PERIOD,
           "points": []}
    done = set(); nres = 0
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(task, a) for a in tasks]      # smallest-N-first
        for fut in as_completed(futs):
            N, reg, ph, w, err = fut.result(); nres += 1
            acc[N][reg][ph] = w
            if (N not in done and len([v for v in acc[N]["sub"].values()
                                       if v is not None]) == len(PHIS)
                    and len([v for v in acc[N]["sup"].values()
                             if v is not None]) == len(PHIS)):
                done.add(N)
                sv = np.array([acc[N]["sub"][p] for p in PHIS], float)
                pv = np.array([acc[N]["sup"][p] for p in PHIS], float)
                ss = float(sv.max() - sv.min()); sp = float(pv.max() - pv.min())
                gp = float(pv.min() - sv.max())
                rec["points"].append({
                    "N": N, "lnN": round(math.log(N), 6),
                    "fold_phase": round((math.log(N) - math.log(N_LO)) % LNPHI
                                        / LNPHI, 5),
                    "sub_spread": round(ss, 7), "sup_spread": round(sp, 7),
                    "gap": round(gp, 7), "sub_mean": round(float(sv.mean()), 7),
                    "sup_mean": round(float(pv.mean()), 7),
                    "exact_crit": bool(gp > 0 and gp >= max(ss, sp))})
                if nres % 32 == 0 or len(done) % 5 == 0:
                    rec["elapsed_s"] = round(time.time() - t0, 0)
                    rec["points"].sort(key=lambda d: d["N"])
                    json.dump(rec, open(OUT, "w"), indent=1)
                    print(f"   [{len(done):3d}/{len(Ns)} N, {nres}/{len(tasks)} "
                          f"tasks, {rec['elapsed_s']:.0f}s] N={N} "
                          f"sup_spread={round(sp,5)} gap={round(gp,5)} "
                          f"crit={rec['points'][-1]['exact_crit']}", flush=True)
    rec["points"].sort(key=lambda d: d["N"])

    # Pre-registered FOLD-TEST diagnostic (the exact log-periodicity test):
    # variance-explained by the period-folded mean vs the raw series, for
    # candidate periods lnφ and 2·lnφ. (Decay NOT removed here — this is the
    # raw diagnostic; the report does the disciplined decay+modulation
    # decomposition. A clean fold ⇒ decomposition well-posed.)
    P = rec["points"]
    lnN = np.array([p["lnN"] for p in P]);
    def fold_ve(series, period):
        ph = ((lnN - lnN[0]) % period) / period
        order = np.argsort(ph)
        y = np.array(series)[order]; x = ph[order]
        # binned folded-mean (12 bins) ; VE = 1 - SS_res/SS_tot after a
        # local linear lnN-detrend (separates a periodic fold from the
        # monotone decay without imposing the decay form)
        b = np.polyfit(lnN, series, 1); detr = np.array(series) - np.polyval(b, lnN)
        d = detr[order]
        bins = np.clip((x * 12).astype(int), 0, 11)
        fm = np.array([d[bins == k].mean() if np.any(bins == k) else 0.0
                       for k in range(12)])
        pred = fm[bins]
        sstot = float(np.sum((d - d.mean()) ** 2))
        ssres = float(np.sum((d - pred) ** 2))
        return round(1 - ssres / sstot, 4) if sstot > 0 else None
    for key in ("sup_spread", "gap"):
        s = [p[key] for p in P]
        rec.setdefault("fold_diagnostic", {})[key] = {
            "VE_lnphi": fold_ve(s, LNPHI), "VE_2lnphi": fold_ve(s, 2 * LNPHI),
            "note": "linear-lnN-detrended folded-mean variance-explained; "
                    "high VE@lnphi ⇒ log-φ-periodic ⇒ decomposition well-posed"}
    rec["total_s"] = round(time.time() - t0, 0)
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 88)
    print(f"DONE {rec['total_s']}s. fold-diagnostic (detrended VE): "
          f"{rec['fold_diagnostic']}")
    print("Decomposition / N*-band read = the report (pre-registered; honest")
    print("terminals: cleanly-pinned / bounded-but-wide / not-log-φ-periodic-")
    print("⇒-not-pinnable). SCOPING/lever-cost, NEVER a finding. brief-and-hold.")
    print("=" * 88)


if __name__ == "__main__":
    main()
