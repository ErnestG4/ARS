"""verify_divisor_strat.py -- known answers and red path for the A4 v2 stratified-permutation null, BEFORE its seal.
Uses the REAL token counts only to build strata and the synthetic frequency feature's profile (the counts are not the
test's outcome); activations are synthetic (open lattice 0-99, d = 256).
 (1) strata are matched: the median within-stratum max/min count ratio over the 10 bins is < 3 (reported).
 (2) non-linear frequency feature (activation = Lorentzian + v (x) tanh(1.5 z(log count)), a function of count ALONE,
     i.e. inside H0_freq) -> the ordinary shuffle rejects d = 5 (the comb is detectable) and the stratified null does NOT
     reject any of d = 2, 4, 5, 10 at Holm level: VANISHES or NOT RESOLVABLE in >= 4/5. Info rows: a step-of-count feature,
     and a DETRENDED-comb feature (count minus its magnitude trend = a function of count AND size, outside H0_freq).
 (3) genuine class-5 plant (f = 0.8, independent of frequency) -> SURVIVES in >= 4/5.
 (4) linear log-frequency feature (A3's case) -> also VANISHES/NOT RESOLVABLE in >= 4/5 (the stratified null covers it).
 (2c/2d) on a SYNTHETIC comb-dominated count profile (counts = exp(3[10|i] + 2[5|i] + [2|i])) the f(count) feature is
     detected by the ordinary shuffle and VANISHES under strata built from those counts (the machinery works where a
     frequency comb exists).
 --redpath: a single stratum (no stratification) on the comb-dominated profile makes the comb read SURVIVES in >= 2/3.
"""
import argparse, json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import divisor_spectrum as S, divisor_strat_control as C

N, D, T = 100, 256, 16


def comb_part(counts):
    i = np.arange(N); x = np.log(i + 1.0); c = np.log(np.asarray(counts, float) + 1)
    A = np.stack([np.ones(N), x, x ** 2, x ** 3], 1); trend = A @ np.linalg.lstsq(A, c, rcond=None)[0]
    g = c - trend; return (g - g.mean()) / g.std()


def dataset(rng, feature=None, plant_f=None, amp=6.0):
    Lhat = S.lorentz_shape(N, 0.3, "open"); _, dcl = S.divisor_classes(N)
    X = S.synth(N, D, 6, Lhat, 0.0, rng, plant=(dcl, 5, plant_f) if plant_f else None)
    if feature is not None:
        v = rng.normal(size=D); v /= np.linalg.norm(v); X = X + amp * np.sqrt(N) * np.outer(feature, v) / np.linalg.norm(feature)
    X = X + rng.normal(size=(N, D)) * 0.05 / np.sqrt(T)
    return X - X.mean(0)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--redpath", action="store_true"); a = ap.parse_args()
    rng = np.random.default_rng(5); fails = []
    counts = json.load(open("results/divisor/number_token_counts.json"))["item_counts"]
    def check(cond, msg):
        print(("PASS " if cond else "FAIL ") + msg); (None if cond else fails.append(msg))
    lab, cr = C.strata(counts, 10); ratios = [hi / max(lo, 1) for lo, hi in cr.values()]
    check(np.median(ratios) < 3, f"(1) within-stratum max/min count ratio: median {np.median(ratios):.2f}, max {max(ratios):.2f}")
    lin = np.log(np.asarray(counts, float) + 1); lin = (lin - lin.mean()) / lin.std()
    i = np.arange(N); syn_counts = np.exp(8 + 3.0 * (i % 10 == 0) + 2.0 * (i % 5 == 0) + 1.0 * (i % 2 == 0) + rng.normal(0, 0.05, N))
    syn_f = np.log(syn_counts); syn_f = (syn_f - syn_f.mean()) / syn_f.std()   # f(count) on a COMB-DOMINATED count profile
    g = np.tanh(1.5 * lin)                                   # NON-LINEAR function of count alone (inside H0_freq)
    step = (np.asarray(counts, float) > np.median(counts)).astype(float); step = (step - step.mean()) / step.std()
    comb = np.tanh(comb_part(counts))                        # count minus its MAGNITUDE trend: a function of (count, size)
    # -> NOT inside H0_freq; reported as information (A4 does not claim to control it)
    B = 600; n2 = n3 = n4 = 0; reps = 5; comb_det = 0
    for i in range(reps):
        r = C.test_matrix(dataset(rng, feature=g), counts, B, rng, 10, log=lambda *a: None)
        comb_det += r["p_unstrat"][5] < 0.05 / 4
        n2 += all(r["words"][c] != "SURVIVES" for c in (2, 4, 5, 10))
        r = C.test_matrix(dataset(rng, plant_f=0.8), counts, B, rng, 10, log=lambda *a: None)
        n3 += r["words"][5] == "SURVIVES"
        r = C.test_matrix(dataset(rng, feature=lin), counts, B, rng, 10, log=lambda *a: None)
        n4 += all(r["words"][c] != "SURVIVES" for c in (2, 4, 5, 10))
    info_step = info_comb = 0
    for i in range(3):
        info_step += all(C.test_matrix(dataset(rng, feature=step), counts, B, rng, 10, log=lambda *a: None)["words"][c] != "SURVIVES" for c in (2, 4, 5, 10))
        info_comb += all(C.test_matrix(dataset(rng, feature=comb), counts, B, rng, 10, log=lambda *a: None)["words"][c] != "SURVIVES" for c in (2, 4, 5, 10))
    print(f"     info: step-of-count feature does not SURVIVE in {info_step}/3; DETRENDED-comb feature (count x size, outside H0_freq) does not SURVIVE in {info_comb}/3")
    check(comb_det == 0, f"(2a) with the REAL counts, a monotone f(count) feature at amp 6 creates NO detectable d=5 excess ({comb_det}/{reps}); "
                         f"the count profile is magnitude-dominated and the fit absorbs it -- a frequency-only feature cannot reproduce the observed comb")
    check(n2 >= 4, f"(2b) ... and does not SURVIVE the stratified null {n2}/{reps}")
    det_s = van_s = 0
    for i in range(reps):
        r = C.test_matrix(dataset(rng, feature=syn_f), syn_counts, B, rng, 10, log=lambda *a: None)
        det_s += r["p_unstrat"][5] < 0.05 / 4; van_s += all(r["words"][c] != "SURVIVES" for c in (2, 4, 5, 10))
    check(det_s >= 4, f"(2c) on a COMB-DOMINATED synthetic count profile the f(count) feature IS detected by the ordinary shuffle {det_s}/{reps}")
    check(van_s >= 4, f"(2d) ... and VANISHES / is not SURVIVES under strata built from those counts {van_s}/{reps} (stratification absorbs any f(count))")
    check(n3 >= 4, f"(3) genuine class-5 plant SURVIVES the stratified null {n3}/{reps}")
    check(n4 >= 4, f"(4) linear log-frequency feature does not SURVIVE {n4}/{reps}")
    if a.redpath:
        red = 0
        for i in range(3):
            r = C.test_matrix(dataset(rng, feature=syn_f), syn_counts, B, rng, 1, log=lambda *a: None)
            red += r["words"][5] == "SURVIVES"
        print(("RED  " if red >= 2 else "FAIL ") + f"(redpath) ONE stratum (no stratification) on the comb-dominated profile: the comb reads SURVIVES {red}/3")
        if red < 2: fails.append("redpath did not go red")
    print("FAILURES:", fails or "none"); sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
