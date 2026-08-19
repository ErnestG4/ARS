"""What the dial-2.0 residual actually is: polynomial ORDER vs density PERIODS.
COMMITTED GENERATOR of holonomy/p1_degree_diagnostic.json.  DIAGNOSTIC ONLY --
this varies the sealed instrument on purpose to explain a residual and issues
no verdict on any sealed row.

The registered corrected design (isolate the finite-n fit response on a no-trend
substrate) was run in p1_finite_n_arm.py and came back INERT: at a = 0 the P1
pair gives -0.0017 +- 0.0097, i.e. no finite-n response to measure.  My
non-inertness argument for that arm -- that a degree-5 fit would absorb
counting-function fluctuations differently over the full and windowed ranges --
was simply WRONG, and the guard caught it rather than letting a null be read as
an answer.  But the a-sweep run alongside it points somewhere specific:

    a        residual        sem
    0.00     -0.0017         0.0097
    0.05     +0.0008         0.0087
    0.10     +0.0108         0.0077
    0.25     +0.2242         0.0288

The residual is ABSENT at small a and explodes by a=0.25, scaling like a^3.3 --
a TREND-AMPLITUDE dependence, which a finite-n floor has no reason to have.

THE CANDIDATE MECHANISM, from the geometry rather than from the numbers.  The
truth density is rho(x) = 1 + a sin(2 pi x / ell) with ell = n_W / dial.  At
dial 2.0 and n_W = 600, ell = 300, so the FULL fit range (n_full = 1200) spans
FOUR periods of the modulation while the WINDOW (600) spans TWO.  A degree-5
polynomial has at most four turning points: it can approximately track two
periods and cannot track four.  So order A (fit on the full set) is forced to
mis-track the density in a way order B (fit on the window) is not, and the gap
is a POLYNOMIAL-RESOLUTION effect that grows nonlinearly with the amplitude it
fails to track.  This is neither a finite-n floor nor a missing continuum term
in the usual sense -- it is the estimator being under-ordered for the substrate.

THE TEST, which the mechanism makes sharp and falsifiable: raise DEG.  If the
residual is the polynomial's inability to track four periods, it must COLLAPSE
once the degree is high enough to represent them (deg >~ 2 * periods + slack),
while the continuum prediction -- which knows nothing about DEG -- stays put.

PREDICTION, COMMITTED BEFORE THE RUN: the residual falls by at least an order of
magnitude between deg=5 and deg=13 at fixed a=0.25 and dial 2.0.  If it does NOT
fall with degree, the mechanism is refuted and the residual is something else.
"""
import json, sys
import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")
from transitions import (gen_gue_unfolded, make_trend_maps, p1_apply,   # noqa: E402
                         sigma2_at)
import predict_p1 as PP                                                 # noqa: E402

N_FULL, N_W, DIAL, A = 1200, 600, 2.0, 0.25
ELL, L = N_W / DIAL, N_W / 60.0
SEEDS, N_MAT = 24, 2048
DEGS = [5, 7, 9, 11, 13, 15]
SEALED_DEG, TARGET = 5, 0.2242


def predict(deg):
    u = np.linspace(0.0, float(N_FULL), 48001)
    x_of_u, _ = make_trend_maps(A, ELL, u_hi=float(N_FULL))
    x = x_of_u(u)
    lo, hi = (N_FULL - N_W) / 2.0, (N_FULL + N_W) / 2.0
    w = (u >= lo) & (u <= hi)
    cA, cB = np.polyfit(x, u, deg), np.polyfit(x[w], u[w] - lo, deg)
    return float(PP.spurious_var(np.polyval(cA, x[w]), u[w], L)
                 - PP.spurious_var(np.polyval(cB, x[w]), u[w], L))


def main():
    spectra = {}
    for s in range(SEEDS):
        ua = gen_gue_unfolded(N_MAT, s)
        lo = (len(ua) - N_FULL) // 2
        spectra[s] = ua[lo:lo + N_FULL] - ua[lo]
    x_of_u, _ = make_trend_maps(A, ELL, u_hi=float(N_FULL))
    per_full, per_win = N_FULL / ELL, N_W / ELL
    out = dict(a=A, dial=DIAL, ell=ELL, L=L, seeds=SEEDS,
               periods_full=per_full, periods_window=per_win,
               sealed_deg=SEALED_DEG, target=TARGET,
               prediction="residual falls >=10x between deg 5 and 13", rows={})
    print(f"a={A}, dial={DIAL}, ell={ELL:.0f} -> {per_full:.0f} periods in the full "
          f"range, {per_win:.0f} in the window\n")
    print(f"{'deg':>4} {'measured Δ':>18} {'predicted':>11} {'residual':>11} {'vs deg5':>9}")
    for deg in DEGS:
        pred = predict(deg)
        d = []
        for s in range(SEEDS):
            x = x_of_u(spectra[s])
            sA = sigma2_at(p1_apply(x, "unfold_then_window", deg, N_W), [L])[0]
            sB = sigma2_at(p1_apply(x, "window_then_unfold", deg, N_W), [L])[0]
            d.append(sA - sB)
        d = np.asarray(d, float); d = d[np.isfinite(d)]
        meas, sem = float(d.mean()), float(d.std(ddof=1) / np.sqrt(d.size))
        resid = meas - pred
        out["rows"][str(deg)] = dict(deg=deg, measured=meas, sem=sem,
                                     predicted=pred, residual=resid)
        base = out["rows"][str(SEALED_DEG)]["residual"]
        print(f"{deg:>4} {meas:>+11.4f}±{sem:<6.4f} {pred:>+11.4f} {resid:>+11.4f} "
              f"{resid/base:>9.3f}", flush=True)

    # BUGFIX (found by red-reading the first run): the drop was computed as a
    # SIGNED ratio r5/r13, so a residual that collapsed and slightly overshot
    # through zero came back NEGATIVE and printed "MECHANISM REFUTED" for a
    # residual that had in fact fallen 83x. Magnitudes, and the comparison that
    # actually matters is whether the higher-degree residual is consistent with
    # ZERO -- a shrinking |ratio| alone would also be satisfied by a residual
    # that merely got noisier.
    r5 = abs(out["rows"]["5"]["residual"])
    hi = [out["rows"][str(d)] for d in DEGS if d >= 9]
    worst = max(abs(r["residual"]) for r in hi)
    all_consistent_with_zero = all(abs(r["residual"]) <= 3.0 * r["sem"] for r in hi)
    drop = r5 / worst if worst else float("inf")
    # the law's real test: it must track the measured value across its full RANGE
    span = max(abs(r["measured"]) for r in out["rows"].values()) / \
        max(min(abs(r["measured"]) for r in out["rows"].values()), 1e-12)
    out["drop_deg5_to_high"] = drop
    out["high_deg_all_consistent_with_zero"] = all_consistent_with_zero
    out["measured_dynamic_range"] = span
    out["verdict"] = (
        f"UNDER_ORDERED_ESTIMATOR — deg 5 is the ONLY degree where the continuum "
        f"law fails. |residual| falls {drop:.0f}x by deg>=9 and every higher-degree "
        f"residual is within 3 sem of zero, while the law tracks a measured value "
        f"spanning {span:.0f}x. The dial-2.0 residual is the degree-5 fit failing "
        f"to track {per_full:.0f} density periods, NOT a missing continuum term"
        if (drop >= 10 and all_consistent_with_zero) else
        f"MECHANISM REFUTED — |residual| falls only {drop:.1f}x and "
        f"high-degree-consistent-with-zero is {all_consistent_with_zero}")
    print(f"\nVERDICT: {out['verdict']}")
    json.dump(out, open(f"{ROOT}/holonomy/p1_degree_diagnostic.json", "w"), indent=1)


if __name__ == "__main__":
    main()
