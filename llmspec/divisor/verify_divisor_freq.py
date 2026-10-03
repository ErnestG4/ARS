"""verify_divisor_freq.py -- synthetic known answers and red paths for the A3 frequency control, run BEFORE sealing and
BEFORE any count or activation is read. Synthetic 'activations' on the 0-99 open lattice (d = 256, 16 templates):
  comb   : Lorentzian cycle + v (x) c_syn, a frequency comb along a synthetic log-frequency profile c_syn with peaks at
           multiples of 10 (+3), of 5 (+2), even numbers (+1), powers of 2 (+1.5)  -> classes 2, 4, 5, 10 excess
  plant  : Lorentzian cycle + a genuine class-5 excess (f = 0.8) built ORTHOGONALLY to c_syn (residualised)
Checks:
 (1) can-fire: the comb profile's own DFT puts > 10 % of its power in classes {2, 4, 5, 10}.
 (2) comb BEFORE residualisation: the sealed test rejects d = 5 and d = 2 (the profile's dominant classes; p < 0.05/17) in >= 4/5 datasets; p for d = 10 and 4 printed.
 (3) comb AFTER residualisation on c_syn: no class among {2, 4, 5, 10} rejected at 0.05/17 in >= 4/5 datasets (VANISHES).
 (4) genuine plant AFTER residualisation: d = 5 still rejected in >= 4/5 (SURVIVES).
 (5) wrong-instance covariate: residualising the comb on a SHUFFLED profile leaves the comb's d = 5 rejection in >= 4/5
     (the regression removes only what it is told to).
 --redpath: residualising on the comb's exact activation direction via the plant's own class harmonics (an 'oracle' that
            is NOT the sealed covariate) must make the genuine plant vanish -> shows check (4) can go red.
"""
import argparse, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import divisor_spectrum as S, divisor_freq_control as F

N, D, T = 100, 256, 16


def profile():
    i = np.arange(N); c = np.log(1000 + 200.0 * (i < 10)) - np.log(1000)      # small numbers a bit commoner
    c += 3.0 * (i % 10 == 0) + 2.0 * (i % 5 == 0) + 1.0 * (i % 2 == 0) + 1.5 * np.isin(i, [1, 2, 4, 8, 16, 32, 64])
    return c - c.mean()


def dataset(rng, comb=None, plant=None, noise=0.05):
    Lhat = S.lorentz_shape(N, 0.3, "open"); _, dcl = S.divisor_classes(N)
    X = S.synth(N, D, 6, Lhat, 0.0, rng)
    if comb is not None:
        v = rng.normal(size=D); v /= np.linalg.norm(v); X = X + 1.5 * np.outer(comb, v)
    if plant is not None:
        c, f = plant
        Xp = S.synth(N, D, 6, Lhat, 0.0, rng, plant=(dcl, 5, f)) - X * 0
        # keep only the planted part orthogonal to c: residualise the plant on c before adding it
        P = Xp - np.outer(c, c @ Xp / (c @ c)); X = X + (P - P.mean(0))
    return X[None] + rng.normal(size=(T, N, D)) * noise


def run(X, rng, B=600, Bs=500):
    return S.run_concept("syn", X, "open", B, Bs, rng, [], 0, 17, log=lambda *a: None)


def resid(X, c):
    Xbar = X.mean(0); C = c[:, None]; beta = np.linalg.lstsq(C, Xbar - Xbar.mean(0), rcond=None)[0]
    return X - (C @ beta)[None]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--redpath", action="store_true"); a = ap.parse_args()
    rng = np.random.default_rng(11); fails = []; c = profile(); H = 0.05 / 17
    def check(cond, msg):
        print(("PASS " if cond else "FAIL ") + msg); (None if cond else fails.append(msg))
    frac, _ = F.comb_spectrum(c); s = sum(frac.get(d, 0) for d in (2, 4, 5, 10))
    check(s > 0.10, f"(1) comb profile can fire: {s:.2f} of its power in classes 2/4/5/10 ({ {d: round(v, 2) for d, v in frac.items()} })")
    n2 = n3 = n4 = n5 = 0; reps = 5
    for i in range(reps):
        Xc = dataset(rng, comb=c)
        r = run(Xc, rng); n2 += (r["p"][5] < H) and (r["p"][2] < H); print(f"     comb before: p5={r['p'][5]:.4f} p2={r['p'][2]:.4f} p10={r['p'][10]:.4f} p4={r['p'][4]:.4f}")
        r = run(resid(Xc, c), rng); n3 += all(r["p"][d] >= H for d in (2, 4, 5, 10))
        Xp = dataset(rng, plant=(c, 0.8))
        r = run(resid(Xp, c), rng); n4 += r["p"][5] < H
        r = run(resid(Xc, rng.permutation(c)), rng); n5 += r["p"][5] < H
    check(n2 >= 4, f"(2) comb detected before residualisation {n2}/{reps}")
    check(n3 >= 4, f"(3) comb VANISHES after residualisation {n3}/{reps}")
    check(n4 >= 4, f"(4) genuine class-5 plant SURVIVES residualisation {n4}/{reps}")
    check(n5 >= 4, f"(5) wrong-instance covariate leaves the comb {n5}/{reps}")
    if a.redpath:
        red = 0
        for i in range(3):
            Xp = dataset(rng, plant=(c, 0.8)); Xbar = Xp.mean(0); Xbar -= Xbar.mean(0)
            # oracle covariates: the class-5 harmonics' own cos/sin profiles (NOT the sealed covariate)
            n = np.arange(N); Cor = np.stack([f(2 * np.pi * k * n / N) for k in (20, 40) for f in (np.cos, np.sin)], 1)
            beta = np.linalg.lstsq(Cor, Xbar, rcond=None)[0]; Xo = Xp - (Cor @ beta)[None]
            r = run(Xo, rng); red += r["p"][5] >= H
        print(("RED  " if red >= 2 else "FAIL ") + f"(redpath) oracle covariates erase the genuine plant {red}/3 (check 4 would FAIL)")
        if red < 2: fails.append("redpath did not go red")
    print("FAILURES:", fails or "none"); sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
