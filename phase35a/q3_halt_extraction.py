"""
phase35a/q3_halt_extraction.py — §Q3 (SCOPING; signed off rev-6, 2026-05-17).

Executes the two-boundary HALT extraction exactly as pre-registered in
PHASE35A_BRIEF.md rev 6. NOT 35a execution; §3 untouched; brief-and-hold
on §3/35a stands. NO auto-adjudication of §3.

Pre-registered spec (rev-6, signed off — reproduced so the run is the spec):
  • φ-seeds PAIRED across the Fibonacci-N ladder: one fixed φ-set (n_φ=12)
    reused at every N, so the increment is a true paired difference.
  • Statistic: W1δ_φ(λ,N) = E|s−1| of the trimmed unit-mean spacings of the
    CERTIFIED IDS-leg unfolding (unfold_ids_ref vs a fixed high-N reference).
  • Floor discipline: W1δ ≠ KS ⇒ floors are the empirical φ-ensemble noise
    of THIS statistic, never 0.8687/√n.
  • L (onset of resolvable structure): L-statistic = mean_φ W1δ ;
    L-floor = std_φ(W1δ_φ)/√n_φ (single-measurement) ;
    L = smallest N with mean_φ W1δ > c_L·L-floor, c_L = 2.
  • U (convergence to the limiting law): per consecutive Fibonacci pair k,
    paired per-φ increment δ_φ(k)=W1δ_φ(F_{k+1})−W1δ_φ(F_k) ;
    ΔW1δ(k)=mean_φ δ_φ(k) ; U-floor(k)=std_φ(δ_φ(k))/√n_φ (paired-difference,
    measured directly — NOT single-measurement, NOT assumed √2σ) ;
    U = first k where |ΔW1δ(k)| ≤ c_U·U-floor(k), c_U = 1, SUSTAINED over
    ≥2 consecutive Fibonacci steps (k and k+1). Early-stop on U.
  • Returns: L always; U or pre-registered U_NOT_REACHED at N_max=F_26=121393.
  • §Q3a = the pre-existing-N rungs (≤ F_21=10946); §Q3b = the F_22..F_26
    extension; one sweep, labelled.
  • L-bound analytic cross-check (binds to L only; U's predictor is §3):
    first Cantor-hierarchy gap k=2, width g₂≈λ² (leading constant 1 —
    a PRE-REGISTERED modelling choice, flagged), spectral width W≈4+4λ,
    resolved when g₂ > W/N ⇒ analytic-L N_aL ≈ W/λ². AGREE if empirical
    L within a factor 3 (≈1.5 Fibonacci steps) of N_aL, else
    DISAGREE_FINDING (recorded, not a failure — exactly the rev-6 spec).

Cost (calibrated 2026-05-17, O(N²) eigvalsh_tridiagonal): N=46368 16s,
F_26=121393 110s. Early-stop-on-U ⇒ common case ≈30–40 min; F_26 the
pre-registered hard cap only in the deep tail.
"""
from __future__ import annotations
import os, sys, json, time, warnings
import numpy as np
from scipy.linalg import eigvalsh_tridiagonal

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

GOLDEN = (np.sqrt(5.0) - 1.0) / 2.0

# pre-registered constants (rev-6)
N_PHI   = 12
C_L     = 2.0
C_U     = 1.0
LAMBDAS = [0.10, 0.30, 0.50]          # Class-II small-λ corner (0.10 = key)
XCHK_K  = 2                           # first Cantor-hierarchy gap (k=1 = principal, trivially resolved)
XCHK_TOL_FACTOR = 3.0                 # AGREE iff within ×3 of analytic-L
PHIS    = np.linspace(0.0, 1.0, N_PHI, endpoint=False)   # PAIRED across the ladder


def fib_upto(kmax):
    F = [1, 1]
    while len(F) <= kmax:
        F.append(F[-1] + F[-2])
    return F

FIB   = fib_upto(27)
K_LO, K_HI = 12, 26                   # F_12=144 … F_26=121393 (N_max)
LADDER = [FIB[k] for k in range(K_LO, K_HI + 1)]
N_MAX  = FIB[26]                      # 121393
N_REF  = FIB[27]                      # 196418  (> N_max ⇒ valid IDS ref over the whole range)
PREEXIST_TOP = FIB[21]               # 10946 — §Q3a/§Q3b boundary


def am_eigs(lam, N, phi):
    n = np.arange(N, dtype=np.float64)
    d = 2.0 * lam * np.cos(2.0 * np.pi * (GOLDEN * n + phi))
    return eigvalsh_tridiagonal(d, np.ones(N - 1))


def unfold_ids_ref(eigs, eigs_ref):
    er = np.sort(eigs_ref)
    idx = np.searchsorted(er, np.sort(eigs), side="right")
    return (idx / er.size) * len(eigs)


def W1d_phi(lam, N, phi, ref):
    u = unfold_ids_ref(am_eigs(lam, N, phi), ref)
    d = np.diff(np.sort(u))
    d = d[int(0.02 * len(d)):int(0.98 * len(d))]
    m = d.mean()
    s = d / m if m > 0 else d
    return float(np.mean(np.abs(s - 1.0)))          # Wasserstein-1 to δ(s−1)


def run():
    log = {"spec": "rev-6 signed-off; SCOPING; §3 untouched",
           "constants": {"n_phi": N_PHI, "c_L": C_L, "c_U": C_U,
                          "N_max": N_MAX, "N_ref": N_REF,
                          "xcheck_k": XCHK_K, "xcheck_tol_factor": XCHK_TOL_FACTOR},
           "lambdas": {}}
    print("=" * 80)
    print("§Q3 HALT extraction — rev-6 spec (SCOPING; §3 untouched; brief-and-hold)")
    print(f"  paired φ n={N_PHI} ; c_L={C_L} c_U={C_U} ; N_max=F_26={N_MAX} ; "
          f"N_ref=F_27={N_REF} ; λ={LAMBDAS}")
    print(f"  ladder F_{K_LO}..F_{K_HI} ; §Q3a ≤ {PREEXIST_TOP} ; §Q3b > {PREEXIST_TOP}")
    print("=" * 80)

    for lam in LAMBDAS:
        t0 = time.time()
        print(f"\n── λ={lam}  building IDS reference (N_ref={N_REF}, 1 φ) …",
              flush=True)
        ref = np.sort(am_eigs(lam, N_REF, 0.0))
        print(f"   ref built ({time.time()-t0:.0f}s)")

        rungs = []                                   # per-N: dict
        W = {}                                       # N -> per-φ W1δ array (paired)
        L_N = None
        U_k = None
        u_cond_hist = []                             # bool per consecutive pair
        verdict = None

        # analytic-L cross-check (binds to L only; pre-registered model)
        W_spec = 4.0 + 4.0 * lam                     # ~spectral width
        g_k = lam ** XCHK_K                           # first Cantor-hier gap width
        N_aL = W_spec / g_k                           # resolved when g_k > W/N

        prev_meanW = None
        for i, N in enumerate(LADDER):
            ts = time.time()
            w = np.array([W1d_phi(lam, N, p, ref) for p in PHIS])  # paired φ
            W[N] = w
            meanW = float(w.mean())
            Lfloor = float(w.std(ddof=1) / np.sqrt(N_PHI))
            regime = "Q3a" if N <= PREEXIST_TOP else "Q3b"
            # L: first N with mean_φ W1δ > c_L·Lfloor
            if L_N is None and meanW > C_L * Lfloor:
                L_N = N
            drift = (meanW / prev_meanW) if prev_meanW else float("nan")
            rungs.append({"N": N, "regime": regime, "meanW": round(meanW, 6),
                          "Lfloor": round(Lfloor, 6), "c_L*Lfloor": round(C_L*Lfloor, 6),
                          "drift_ratio": round(drift, 3) if prev_meanW else None,
                          "eig_s": round(time.time()-ts, 1)})
            print(f"   N={N:7d} [{regime}] meanW1δ={meanW:.5f} "
                  f"Lfloor={Lfloor:.5f} c_L·fl={C_L*Lfloor:.5f}"
                  f"{' ←L' if L_N==N else ''}  drift×{drift:.2f}"
                  f"  ({rungs[-1]['eig_s']:.0f}s)", flush=True)
            prev_meanW = meanW

            # U test on the consecutive pair (N_{i-1}, N_i)
            if i >= 1:
                Nprev = LADDER[i-1]
                dphi = W[N] - W[Nprev]               # PAIRED per-φ increment
                dW = float(dphi.mean())
                Ufloor = float(dphi.std(ddof=1) / np.sqrt(N_PHI))
                cond = abs(dW) <= C_U * Ufloor
                u_cond_hist.append((Nprev, N, dW, Ufloor, cond))
                print(f"      ΔW1δ({Nprev}→{N})={dW:+.5f} "
                      f"Ufloor={Ufloor:.5f} c_U·fl={C_U*Ufloor:.5f} "
                      f"within={cond}", flush=True)
                # U = first k with cond sustained over ≥2 consecutive steps
                if (U_k is None and len(u_cond_hist) >= 2
                        and u_cond_hist[-1][4] and u_cond_hist[-2][4]):
                    U_k = Nprev
                    verdict = "U_REACHED"
                    print(f"   *** U REACHED (sustained ≥2 steps) at N≈{U_k} "
                          f"— early-stop ***", flush=True)
                    break
            if N >= N_MAX:
                verdict = "U_NOT_REACHED"
                print(f"   *** N_max=F_26={N_MAX} reached without sustained U "
                      f"⇒ U_NOT_REACHED (pre-registered) ***", flush=True)
                break

        if verdict is None:                          # ladder exhausted < N_max (shouldn't happen)
            verdict = "U_NOT_REACHED"

        # L-bound analytic cross-check
        if L_N is not None:
            ratio = L_N / N_aL
            agree = (1.0 / XCHK_TOL_FACTOR) <= ratio <= XCHK_TOL_FACTOR
            xchk = {"empirical_L_N": L_N, "analytic_L_N": round(N_aL, 1),
                    "ratio": round(ratio, 3),
                    "result": "AGREE_L_DOUBLY_CERTIFIED" if agree
                              else "DISAGREE_RECORDED_FINDING",
                    "model": f"k={XCHK_K}, g_k=λ^{XCHK_K} (const 1, pre-registered), W≈4+4λ"}
        else:
            xchk = {"empirical_L_N": None, "analytic_L_N": round(N_aL, 1),
                    "result": "L_NOT_RESOLVED_ON_LADDER"}

        lam_rec = {"L_N": L_N, "L_regime": ("Q3a" if (L_N and L_N <= PREEXIST_TOP)
                                            else "Q3b" if L_N else None),
                   "U_verdict": verdict, "U_N": U_k,
                   "u_cond_history": [[a, b, round(c, 6), round(d, 6), bool(e)]
                                       for (a, b, c, d, e) in u_cond_hist],
                   "rungs": rungs, "xcheck_L": xchk,
                   "wall_s": round(time.time() - t0, 0)}
        log["lambdas"][str(lam)] = lam_rec
        print(f"   λ={lam}: L={L_N} ({lam_rec['L_regime']}) ; {verdict}"
              f"{f' @N≈{U_k}' if U_k else ''} ; xcheck={xchk['result']} "
              f"(emp L={L_N} vs analytic {N_aL:.0f}) ; {lam_rec['wall_s']:.0f}s")

    out = os.path.join(THIS_DIR, "q3_halt_results.json")
    with open(out, "w") as f:
        json.dump(log, f, indent=1)
    print("\n" + "=" * 80)
    print("§Q3 done. SCOPING only — NO §3 adjudication; brief-and-hold stands.")
    print("Read L (+ its L-bound cross-check) and U/U_NOT_REACHED per λ above.")
    print(f"record → {out}")
    print("=" * 80)


if __name__ == "__main__":
    run()
