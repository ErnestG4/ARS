"""verify_divisor.py -- synthetic known answers and red paths for divisor_spectrum.py (brief §6), run BEFORE sealing and
BEFORE any real activation is read. No real data is touched. Exit 0 = PASS. `--redpath` deliberately breaks the pipeline
and demands that the checks below go red.

Checks (declared geometries; the real-geometry power is re-measured inside the pipeline on each real run):
 (1) known answer, periodic: a Lorentzian process (sigma = 0.3, N = 12, k_eff = 6, d = 256, no planted excess) is fitted
     with sigma within a factor 1.6 and P(n) within the bootstrap envelope; the same for open BC (N = 100).
 (2) false alarms: on 12 null datasets per geometry (months N=12, hours N=24, numbers N=100 open) the per-class
     one-sided p < 0.05 rate is <= 0.15, and NO Holm rejection occurs across the 12 x 17 tests at the Holm level.
 (3) prime control N = 7: only the trivial class exists; the whiteness gate passes on 12 null datasets (>= 11/12).
 (4) planted excess: f = 0.8 of the Lorentzian power (a near-doubling, placed in one class) planted into months d=4
     (quarters) and hours d=12 (am/pm) is detected at the Holm first-step level in >= 8/10 datasets; the pipeline's own
     power table (f = 0.1 / 0.3 / 0.6 / 0.8) is printed -- smaller excesses are a measured power, not a pass criterion.
 (5) cycle gate (lag-1 autocorrelation vs item shuffles): white data does NOT fire it (p > 0.01 in >= 11/12),
     and a planted Lorentzian cycle DOES (p < 0.01 in >= 11/12).
 (6) mislabel red path: shuffling the ITEM order of a planted dataset destroys the detection (the statistic reads the
     item order, not the item identity).
"""
import argparse, math, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import divisor_spectrum as S

def make_dataset(N, d, k_eff, sigma, boundary, T, noise_sd, rng, plant=None, scale=1.0):
    """Synthetic (T, N, d) 'activations': one Lorentzian item matrix + independent per-template noise."""
    Lhat = scale * S.lorentz_shape(N, sigma, boundary)
    _, dcl = S.divisor_classes(N)
    X = S.synth(N, d, k_eff, Lhat, 0.0, rng, plant=(dcl, plant[0], plant[1]) if plant else None)
    return X[None] + rng.normal(size=(T, N, d)) * noise_sd, Lhat

def run(X, boundary, rng, B, Bs, grid, draws, nt=17):
    return S.run_concept("syn", X, boundary, B, Bs, rng, grid, draws, nt, log=lambda *a: None)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--redpath", action="store_true"); ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    rng = np.random.default_rng(7)
    B, Bs, draws, reps = (300, 400, 20, 6) if a.fast else (600, 1000, 40, 12)
    BP = 2000   # bootstrap size for the planted-excess checks: the smallest attainable p, 1/(BP+1), must sit below 0.05/17
    fails = []
    def check(cond, msg):
        print(("PASS " if cond else "FAIL ") + msg); (None if cond else fails.append(msg))

    # (1) known answers
    for N, bnd in ((12, "periodic"), (100, "open")):
        X, Lhat = make_dataset(N, 256, 6, 0.3, bnd, 16, 0.002, rng)          # negligible noise: tests the kernel math
        r = run(X, bnd, rng, B, Bs, [], 0)
        Xn_, _ = make_dataset(N, 256, 6, 0.3, bnd, 16, 0.02, rng)
        print(f"     info: with template noise 0.02 the two-parameter fit reads sigma = {run(Xn_, bnd, rng, 50, 50, [], 0)['sigma']:.3f}"
              f" (noise floor biases sigma low; the bootstrap reproduces this; sigma_hat is descriptive)")
        ratio = r["sigma"] / 0.3
        inside = np.mean([abs(math.log(p / l)) < 1.5 for p, l in zip(r["P"], r["Lhat"])])
        check(1 / 1.6 < ratio < 1.6, f"(1) sigma recovered N={N} {bnd}: {r['sigma']:.3f} vs 0.3 (ratio {ratio:.2f})")
        check(inside >= 0.9, f"(1) P(n) within e^1.5 of the fit on {inside:.0%} of harmonics (N={N})")
        if bnd == "open":
            rp = run(X, "periodic", rng, 50, 50, [], 0)
            check(rp["resid_max"] >= r["resid_max"] * 0.8, f"(1b) open data: open kernel fits no worse than periodic "
                  f"(resid_max open {r['resid_max']:.2f} vs periodic {rp['resid_max']:.2f})")

    # (2) false alarms + Holm, (3) prime, (5a) nouns-like
    fa = []; holm_rej = 0; white_prime = 0; cycle_null = 0
    for i in range(reps):
        tests = {}
        for N, bnd, nm in ((12, "periodic", "months"), (24, "periodic", "hours"), (100, "open", "numbers")):
            X, _ = make_dataset(N, 256, 5, 0.25, bnd, 16, 0.05, rng)
            r = run(X, bnd, rng, B, Bs, [], 0)
            for c in r["classes"]:
                if 1 < c < N: fa.append(r["p"][c] < 0.05); tests[f"{nm}:d{c}"] = r["p"][c]
        holm_rej += any(v[2] for v in S.holm(tests).values())
        X7, _ = make_dataset(7, 256, 4, 0.25, "periodic", 16, 0.05, rng)
        r7 = run(X7, "periodic", rng, B, Bs, [], 0)
        white_prime += r7["white_p"] > 0.01
        assert r7["classes"] == [7], r7["classes"]
        Xn = rng.normal(size=(16, 12, 256)) * 0.3 + rng.normal(size=(1, 12, 256))      # no cycle at all
        rn = run(Xn, "periodic", rng, B, Bs, [], 0)
        cycle_null += rn["cycle_p"] > 0.01
    check(np.mean(fa) <= 0.15, f"(2) per-class false-alarm rate at p<0.05: {np.mean(fa):.3f} over {len(fa)} class tests")
    check(holm_rej == 0, f"(2) Holm rejections on null data: {holm_rej}/{reps}")
    check(white_prime >= reps - 1, f"(3) prime control whiteness gate passes {white_prime}/{reps}")
    check(cycle_null >= reps - 1, f"(5a) cycle gate silent on white data {cycle_null}/{reps}")

    # (4) planted excess, (5b) cycle fires, (6) mislabel red path
    grid = [0.1, 0.3, 0.6, 0.8]; FP = 0.8
    det = {"months:4": 0, "hours:12": 0}; cyc = 0; mis = 0; nreps = 10 if not a.fast else 5
    for i in range(nreps):
        for N, c, key in ((12, 4, "months:4"), (24, 12, "hours:12")):
            X, _ = make_dataset(N, 256, 5, 0.25, "periodic", 16, 0.05, rng, plant=(c, FP))
            r = run(X, "periodic", rng, BP, Bs, grid if i == 0 else [], draws if i == 0 else 0)
            det[key] += r["p"][c] < 0.05 / 17
            if i == 0: print(f"     power table {key}: {r['power'][str(c)]}  smallest_f={r['smallest_f'][str(c)]}")
            if key == "months:4":
                cyc += r["cycle_p"] < 0.01
                perm = rng.permutation(N)
                rm = run(X[:, perm], "periodic", rng, BP, Bs, [], 0)
                mis += rm["p"][c] >= 0.05 / 17
    for k, v in det.items(): check(v >= 0.8 * nreps, f"(4) planted f={FP} in {k} detected at Holm level {v}/{nreps}")
    print(f"     info: cycle gate (lag-1 vs shuffles) fires on a BROAD Lorentzian cycle (sigma=0.25, q=0.51) in {cyc}/{nreps}")
    cyc2 = 0
    for i in range(nreps):
        X, _ = make_dataset(12, 256, 5, 0.6, "periodic", 16, 0.05, rng)
        cyc2 += run(X, "periodic", rng, 50, Bs, [], 0)["cycle_p"] < 0.01
    check(cyc2 >= nreps - 1, f"(5b) cycle gate fires on a Lorentzian cycle (sigma=0.6, q=0.76) {cyc2}/{nreps}")
    check(mis >= nreps - 1, f"(6) item-shuffled planted data is NOT detected {mis}/{nreps} (statistic reads the order)")

    if a.redpath:
        # break the pipeline: a fit that returns P itself leaves no residual -> planted excess invisible -> (4) must FAIL
        orig = S.fit_lorentz
        S.fit_lorentz = lambda P, N, b: (1.0, 1.0, P.copy())
        X, _ = make_dataset(12, 256, 5, 0.25, "periodic", 16, 0.05, rng, plant=(4, FP))
        r = run(X, "periodic", rng, BP, Bs, [], 0)
        S.fit_lorentz = orig
        red1 = r["p"][4] >= 0.05 / 17
        print(("RED  " if red1 else "FAIL ") + f"(redpath) identity 'fit' hides a planted excess: p={r['p'][4]:.3f} (must not detect)")
        # break the generator: a null that ignores noise/k_eff reads the real spread wrong -> false alarms climb
        orig2 = S.synth
        S.synth = lambda N, d, k, L, nv, rng_, plant=None: orig2(N, d, 1, L * 0.3, 0.0, rng_, plant)
        fa2 = []
        for i in range(4):
            X, _ = make_dataset(12, 256, 5, 0.25, "periodic", 16, 0.05, rng)
            r = run(X, "periodic", rng, B, Bs, [], 0); fa2 += [r["p"][c] < 0.05 for c in r["classes"]]
        S.synth = orig2
        red2 = np.mean(fa2) > 0.15
        print(("RED  " if red2 else "FAIL ") + f"(redpath) mis-scaled null inflates false alarms: rate {np.mean(fa2):.2f} (must exceed 0.15)")
        if not (red1 and red2): fails.append("redpath did not go red")
    print("FAILURES:", fails or "none")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
