"""The dial-2.0 residual: measure the fit's finite-n response DIRECTLY.
COMMITTED GENERATOR of holonomy/p1_finite_n_arm.json.

This is the corrected design registered in COMMUTATOR_TABLE.md after the
n-scaling attempt came back normalization-dependent and was declared
inconclusive.  The problem there: the unfolded coordinate has unit mean spacing
by construction, so n and the geometry cannot be varied independently, and the
three natural normalizations disagreed on the sign.

THE DESIGN.  Run the P1 pair on a substrate with NO TREND (a = 0).  Then the
continuum prediction is EXACTLY ZERO by construction -- there is no trend to
generate spurious variance -- so whatever Delta the pair produces is the finite-n
fit response, measured directly rather than inferred from a scaling exponent.
Then ask the accounting question: does it account for the +0.224 seen at the
sealed geometry (dial 2.0, L=10, a=0.25)?

WHY IT IS NOT INERT (checked before running, per the standing rule).  At a = 0
the raw coordinate x equals the unfolded GUE sequence, so one might expect both
orderings to recover the identity and cancel.  They do not: order A fits a
degree-5 polynomial to the counting function over ALL n_full points and order B
fits one over the central n_W only.  The counting function of an unfolded
spectrum fluctuates, a degree-5 polynomial absorbs some of that fluctuation, and
the amount absorbed differs between the two ranges.  The arm therefore CAN fire,
and the script asserts it does before reading anything else -- if Delta at a = 0
is statistically indistinguishable from zero, the arm is inert and says so
instead of returning a null.

Seeds are PAIRED across the a-sweep: the underlying GUE spectrum depends only on
(N, seed), so the same spectra are reused at every a and the a-dependence is a
within-spectrum contrast rather than a between-sample one.

PREDICTION, COMMITTED BEFORE THE RUN: the a=0 finite-n response is NON-ZERO but
SMALLER than +0.224 -- the two prior candidates (absorption ~80x too small,
continuum ill-conditioning ~3.6x short) were both shortfalls, so the expectation
is a third partial contribution rather than a full explanation. A response that
MATCHES +0.224 would close the residual as FINITE_N; one that is negligible
would leave MISSING_TERM as the reading.
"""
import json, sys
import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")
from transitions import (gen_gue_unfolded, make_trend_maps, p1_apply,   # noqa: E402
                         sigma2_at)
import predict_p1 as PP
from condfit import fit_eval                                            # noqa: E402                                                 # noqa: E402

N_FULL, N_W, DIAL, DEG = 1200, 600, 2.0, 5
ELL, L = N_W / DIAL, N_W / 60.0
SEEDS, N_MAT = 24, 2048
A_SWEEP = [0.0, 0.05, 0.10, 0.25]
TARGET = 0.2242                     # the residual to be accounted for


def predict(a):
    """Continuum prediction at trend amplitude a (exactly 0 when a = 0)."""
    if a == 0.0:
        return 0.0
    u = np.linspace(0.0, float(N_FULL), 48001)
    x_of_u, _ = make_trend_maps(a, ELL, u_hi=float(N_FULL))
    x = x_of_u(u)
    lo, hi = (N_FULL - N_W) / 2.0, (N_FULL + N_W) / 2.0
    w = (u >= lo) & (u <= hi)
    fA = fit_eval(x, u, DEG, x[w])
    fB = fit_eval(x[w], u[w] - lo, DEG, x[w])
    return float(PP.spurious_var(fA, u[w], L) - PP.spurious_var(fB, u[w], L))


def main():
    spectra = {}
    for s in range(SEEDS):                       # paired across the a-sweep
        ua = gen_gue_unfolded(N_MAT, s)
        lo = (len(ua) - N_FULL) // 2
        u = ua[lo:lo + N_FULL]
        spectra[s] = u - u[0]
    out = dict(geometry=dict(n_full=N_FULL, n_W=N_W, dial=DIAL, L=L, deg=DEG,
                             seeds=SEEDS), target_residual=TARGET,
               prediction="a=0 response NON-ZERO but SMALLER than +0.2242",
               rows={})
    print(f"dial {DIAL}, L={L}, n_full={N_FULL}, {SEEDS} paired seeds\n")
    print(f"{'a':>6} {'measured Δ':>18} {'predicted':>11} {'residual':>10} {'note':>26}")
    for a in A_SWEEP:
        pred = predict(a)
        x_of_u, _ = (make_trend_maps(a, ELL, u_hi=float(N_FULL)) if a else (lambda z: z, None))
        d = []
        for s in range(SEEDS):
            x = x_of_u(spectra[s]) if a else spectra[s]
            sA = sigma2_at(p1_apply(x, "unfold_then_window", DEG, N_W), [L])[0]
            sB = sigma2_at(p1_apply(x, "window_then_unfold", DEG, N_W), [L])[0]
            d.append(sA - sB)
        d = np.asarray(d, float); d = d[np.isfinite(d)]
        meas, sem = float(d.mean()), float(d.std(ddof=1) / np.sqrt(d.size))
        resid = meas - pred
        out["rows"][f"{a:.2f}"] = dict(a=a, measured=meas, sem=sem, predicted=pred,
                                       residual=resid, z_from_zero=meas / sem)
        note = "<- FINITE-N ARM (pred=0)" if a == 0.0 else ""
        print(f"{a:>6.2f} {meas:>+11.4f}±{sem:<6.4f} {pred:>+11.4f} {resid:>+10.4f} {note:>26}")

    z0 = out["rows"]["0.00"]["z_from_zero"]
    fn = out["rows"]["0.00"]["measured"]
    out["non_inertness"] = dict(z_at_a0=z0, fires=bool(abs(z0) >= 3.0))
    print(f"\nNON-INERTNESS: a=0 response is {fn:+.4f} at {abs(z0):.1f} sem from zero -> "
          f"{'ARM FIRES' if abs(z0) >= 3.0 else 'ARM IS INERT (result unreadable)'}")
    if abs(z0) < 3.0:
        out["verdict"] = "ARM_INERT — no finite-n response to measure; test says nothing"
    else:
        frac = fn / TARGET
        out["fraction_of_target"] = frac
        out["verdict"] = (
            "FINITE_N_ACCOUNTS — the no-trend fit response alone covers the residual"
            if 0.7 <= frac <= 1.4 else
            f"PARTIAL — the finite-n response is {frac:.0%} of the residual; "
            "a contribution, not the explanation"
            if abs(frac) >= 0.05 else
            "NEGLIGIBLE — finite-n fit response cannot explain the residual; MISSING_TERM stands")
        print(f"  a=0 response is {frac:.1%} of the +{TARGET:.4f} target")
    print(f"\nVERDICT: {out['verdict']}")
    json.dump(out, open(f"{ROOT}/holonomy/p1_finite_n_arm.json", "w"), indent=1)


if __name__ == "__main__":
    main()
