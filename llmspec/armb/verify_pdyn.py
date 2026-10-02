"""Known answers for the parametric-dynamics pipeline (pdyn_m2, pdyn_m3) on pdyn_calib's synthetic families.
Synthetic only -- NO cache/armb read. Shapes 512x512 (symmetric, eigenvalues), 2048x512 and 512x2048 (singular
values); time grid = the real Arm B grid (grids.arm_grid, 161 checkpoints to 3000) unless --grid; x_step 0.1 at the
10-step cadence (--xstep; the "DBM-rate assumption"). The unfolding is the pipeline's own (top-K stripped first, kde(c)
per checkpoint, c from --kde-c, default 32, see pdyn_m2); (b) is repeated at every c in --kde-sweep to show
the unfolding does not launder beta=2 / Poisson into beta=1 (Will 2026-10-01). Windows [0,500) and [500,3001) are
never pooled.

Known answers (ZD scale k = K/(pi beta <v^2>_i) with beta = 1 ALWAYS, so a beta = 2 process reads with k doubled):
  median |k|: beta=1 1/sqrt(3) = 0.577; beta=2 0.879; Poisson walk ~ 0.3 (no repulsion: curvature = smooth GP +
  crossing kinks); literal DBM: Gaussian k of sd sqrt(2)/(pi x_step) and C_lag[1] = 0; shuffled order: iid
  positions -> finite-difference velocities correlate at EXACTLY -1/2 at lag 1 and 0 beyond.
Checks (exit 1 on any failure; the FAILURES line lists them; seeds 0..NSEED-1 per family):
 (a) C1 smooth beta=1, 3 shapes: velocities Gaussian in [500,3001) (|skew| < 0.25, |excess kurtosis| < 0.5,
     KS < 0.03; effective n ~ n_band * span/tau); seed-mean median |k| in [0,500) (x_step ~ 0.1) within 0.08 of
     0.577 (the ZD normalisation at the real cadence; the per-step value is in PDYN_PIPELINE_NOTES); C_lag[1..6] of
     two independent draws within 0.1 and masked C(x) (bins with >= 10 pairs) within 0.15, both windows.
 (a-dbm) literal DBM at the same x_step: |C_lag[1]| < 0.1 (white velocities); median |k| within 15% of the
     Gaussian prediction 0.6745 sqrt(2)/(pi x_step) (the FD curvature of independent increments; no ZD tail).
 (b) separation statistic S = median |k| in [500,3001), same unfolding, matched x_step, NSEED seeds each:
     every Poisson seed S < 0.45 < every beta=1 seed; every beta=2 seed S > 0.80 > every beta=1 seed (declared
     thresholds for kde_c = 32 at x_step ~ 0.2: beta1 reads 0.68-0.70, beta2 0.93, Poisson 0.12); for every c in the sweep the ORDER Poisson < beta1 < beta2 must hold on the seed means
     and the seed-dispersion z = |m1 - m2| / sqrt(s1^2 + s2^2) must exceed 3. Sample size: random partitions of the
     band's levels into blocks of m levels (one seed); the smallest m with block z > 3 is printed with
     n = m * (T - 2) curvature samples.
 (c) C3 shuffled checkpoint order: C_lag[1] within 0.1 of the exact iid prediction for the window's spacing (-1/2 when
     uniform; -0.32 in [0,500) because of the log steps) and |C_lag[2..3]| < 0.1, both windows.
 (d) C5 sign flips (joint and independent): every M3 metric array bit-identical (np.array_equal).
 (e) planted avoided crossing (two-level system in the top-16): one event on pair 0, |t_min - t0| <= 5 steps,
     |g_min - 2c| <= 0.1 * 2c, theta within 5 deg of the analytic rotation, NOT ambiguous; with the coupling below
     the gap rule's reach (2c = 0.2 x per-step change) the event IS flagged ambiguous.
 (C4) fp32 round-trip floor is REPORTED (bf16 as comparison), not gated.
--redpath: flip (b)'s beta=2 threshold so the beta=1 seeds must satisfy S > 0.80 (they cannot); exit 0 iff the
     check fails. Runtime is printed.
"""
import sys, time, argparse
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pdyn_m2 as M2, pdyn_m3 as M3, pdyn_calib as C  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--redpath", action="store_true"); ap.add_argument("--grid", default="real")
ap.add_argument("--xstep", type=float, default=0.1); ap.add_argument("--kde-c", type=float, default=32.0)
ap.add_argument("--kde-sweep", type=float, nargs="*", default=[4.0, 8.0, 16.0, 32.0]); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--nseed", type=int, default=4)
A = ap.parse_args()
RED = A.redpath; fails = []; T0 = time.time()
times = C.parse_grid(A.grid); WIN = "[500,3001)"; WIN0 = "[0,500)"
rng = np.random.default_rng(A.seed)
SEEDS = [A.seed + 1000 * i for i in range(A.nseed)]
TH_PO, TH_B2, MED1 = 0.45, 0.80, 1 / np.sqrt(3)


def w(res, win=WIN): return res["windows"][win]


def med(res, win=WIN): return w(res, win)["curvature"]["abs_k_median"]


def sep_scan(k1, k2, blocks=(5, 10, 25, 50, 100, 200)):
    out = []
    for m in blocks:
        s1, s2 = [], []
        for kk, s in ((k1, s1), (k2, s2)):
            nb = kk.shape[1]; perm = rng.permutation(nb)
            for j in range(0, nb - m + 1, m):
                s.append(np.median(np.abs(kk[:, perm[j:j + m]])))
        if len(s1) < 2 or len(s2) < 2:
            out.append((m, float("nan"))); continue
        out.append((m, float(abs(np.mean(s1) - np.mean(s2)) / np.sqrt(np.var(s1, ddof=1) + np.var(s2, ddof=1)))))
    return out


def zsep(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return abs(a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) + b.var(ddof=1))


print(f"grid {A.grid}: {len(times)} checkpoints; xstep {A.xstep}; kde_c {A.kde_c}; seeds {SEEDS}")
# ---------------------------------------------------------------- (a) C1 beta = 1
print("(a) C1 smooth beta=1 (known answer: median |k| = 0.577 at x_step -> 0)")
beta1 = {}
for name, fam, n, m in (("sym512", "c1_sym", 512, 512), ("rect2048x512", "c1_rect", 512, 2048), ("rect512x2048", "c1_rect", 2048, 512)):
    t1 = time.time()
    rs = []
    for sd in SEEDS:
        S = C.make(fam, n, m, times, A.xstep, sd); rs.append((S, M2.analyse(S, times, kde_c=A.kde_c)))
    beta1[name] = rs
    r1, r2 = rs[0][1], rs[1][1]
    for line in M2.summary_lines(r1): print("   ", name, "seed0", line)
    v = w(r1)["velocity"]
    meds0 = [med(r, WIN0) for _, r in rs]; meds1 = [med(r) for _, r in rs]
    dlag = max(np.max(np.abs(w(r1, ww)["autocorr"]["C_lag"][1:7] - w(r2, ww)["autocorr"]["C_lag"][1:7])) for ww in (WIN0, WIN))
    dCx = max(np.nanmax(np.abs(w(r1, ww)["autocorr"]["C"][:20] - w(r2, ww)["autocorr"]["C"][:20])) for ww in (WIN0, WIN))
    print(f"    {name}: velocity skew {v['skew']:+.3f} exkurt {v['ex_kurt']:+.3f} KS {v['ks_gauss']:.3f} | median|k| per seed {WIN0} {np.round(meds0, 3)} "
          f"mean {np.mean(meds0):.3f}; {WIN} {np.round(meds1, 3)} mean {np.mean(meds1):.3f} | two draws: max|dC_lag[1..6]| {dlag:.3f} max|dC(x<=2)| {dCx:.3f} "
          f"| nu_fixed {w(r1)['curvature']['nu_fixed']:.3f} gamma_free {w(r1, WIN0)['curvature']['gamma_free']:.3f} ({time.time() - t1:.0f}s)")
    if abs(v["skew"]) > 0.25: fails.append(f"(a) {name} velocity skew {v['skew']:.3f}")
    if abs(v["ex_kurt"]) > 0.5: fails.append(f"(a) {name} velocity exkurt {v['ex_kurt']:.3f}")
    if v["ks_gauss"] > 0.03: fails.append(f"(a) {name} velocity KS {v['ks_gauss']:.3f}")
    if abs(np.mean(meds0) - MED1) > 0.08: fails.append(f"(a) {name} seed-mean median|k| {np.mean(meds0):.3f} not {MED1:.3f} +- 0.08")
    if dlag > 0.1: fails.append(f"(a) {name} C_lag draws differ by {dlag:.3f}")
    if dCx > 0.15: fails.append(f"(a) {name} C(x) draws differ by {dCx:.3f}")
S_dbm = C.make("c1_dbm", 512, 512, times, A.xstep, A.seed)
rd = M2.analyse(S_dbm, times, kde_c=A.kde_c); d = w(rd)
print(f"    DBM literal: x_step {d['x_step_mean']:.3f} C_lag[1..3] {np.round(d['autocorr']['C_lag'][1:4], 3)} velocity skew {d['velocity']['skew']:+.3f} exkurt {d['velocity']['ex_kurt']:+.3f} "
      f"| k: median|k| {d['curvature']['abs_k_median']:.3f} (Gaussian sd sqrt2/(pi x_step) -> median {0.6745 * np.sqrt(2) / (np.pi * d['x_step_mean']):.3f}) "
      f"exkurt {d['curvature']['k_ex_kurt']:.2f} nu_fixed {d['curvature']['nu_fixed']:.2f}")
dbm_pred = 0.6745 * np.sqrt(2) / (np.pi * d["x_step_mean"])
if abs(d["autocorr"]["C_lag"][1]) > 0.1: fails.append(f"(a-dbm) C_lag1 {d['autocorr']['C_lag'][1]:.3f}")
if abs(d["curvature"]["abs_k_median"] / dbm_pred - 1) > 0.15: fails.append(f"(a-dbm) median|k| {d['curvature']['abs_k_median']:.3f} vs Gaussian prediction {dbm_pred:.3f}")

# ---------------------------------------------------------------- (b) witnesses must fail
print(f"(b) witnesses (same unfolding, matched x_step): S = median|k| in {WIN}; thresholds Poisson < {TH_PO} < beta1 < {TH_B2} < beta2 at kde_c={A.kde_c:g}")
S1s = [S for S, _ in beta1["sym512"]]
S2s = [C.make("c2_sym", 512, 512, times, A.xstep, sd) for sd in SEEDS]
SPs = [C.make("c2_poisson", 512, 512, times, A.xstep, sd) for sd in SEEDS]
for c in sorted(set(A.kde_sweep) | {A.kde_c}):
    R1 = [M2.analyse(S, times, kde_c=c) for S in S1s]; R2 = [M2.analyse(S, times, kde_c=c) for S in S2s]; RP = [M2.analyse(S, times, kde_c=c) for S in SPs]
    m1, m2, mp = [med(r) for r in R1], [med(r) for r in R2], [med(r) for r in RP]
    nf = [np.mean([w(r)["curvature"]["nu_fixed"] for r in R]) for R in (R1, R2, RP)]
    xs = [np.mean([w(r)["x_step_mean"] for r in R]) for R in (R1, R2, RP)]
    z12, z1p = zsep(m1, m2), zsep(m1, mp)
    print(f"    kde_c={c:g}: x_step {xs[0]:.3f}/{xs[1]:.3f}/{xs[2]:.3f} | median|k| beta1 {np.round(m1, 3)} beta2 {np.round(m2, 3)} poisson {np.round(mp, 3)} "
          f"| seed-z beta1:beta2 {z12:.1f} beta1:poisson {z1p:.1f} | nu_fixed means {nf[0]:.3f}/{nf[1]:.3f}/{nf[2]:.3f}")
    if not (np.mean(mp) < np.mean(m1) < np.mean(m2)): fails.append(f"(b) kde_c={c:g} order wrong: {np.mean(mp):.3f} {np.mean(m1):.3f} {np.mean(m2):.3f}")
    if z12 < 3: fails.append(f"(b) kde_c={c:g} beta1:beta2 seed-z {z12:.1f} < 3")
    if z1p < 3: fails.append(f"(b) kde_c={c:g} beta1:poisson seed-z {z1p:.1f} < 3")
    if c == A.kde_c:
        if not (max(mp) < TH_PO < min(m1)): fails.append(f"(b) Poisson threshold: max poisson {max(mp):.3f}, min beta1 {min(m1):.3f}")
        b2_ok = min(m2) > TH_B2 > max(m1)
        if RED: b2_ok = min(m1) > TH_B2            # flipped: the beta=1 seeds must now read as beta=2
        if not b2_ok: fails.append(f"(b) beta=2 threshold: min beta2 {min(m2):.3f}, max beta1 {max(m1):.3f} (thr {TH_B2}{', FLIPPED' if RED else ''})")
        Tm = w(R1[0])["T"] - 2
        for lab, R in (("beta2", R2), ("poisson", RP)):
            zz = sep_scan(w(R1[0])["k_samples"].reshape(Tm, -1), w(R[0])["k_samples"].reshape(Tm, -1))
            first = next((m for m, z in zz if z > 3), None)
            print(f"    block scan (one seed) beta1 vs {lab}: " + ", ".join(f"m={m}: z={z:.1f}" for m, z in zz)
                  + f" -> smallest block with z>3: {first} levels = {first * Tm if first else None} curvature samples (T-2={Tm})")

# ---------------------------------------------------------------- (c) shuffle
print("(c) C3 shuffled order (known answer: iid positions -> pooled lag-1 FD-velocity correlation "
      "-sum 1/(d_k d_k+1) / sum 2/d_k^2 * (T-1)/(T-2) = -1/2 for uniform spacing; 0 beyond lag 1)")
rs_ = M2.analyse(C.shuffle(S1s[0], A.seed), times, kde_c=A.kde_c)
for ww in (WIN0, WIN):
    r_ = w(rs_, ww); dts = np.diff(times[(times >= r_["t0"]) & (times <= r_["t1"])])
    pred = -(np.sum(1 / (dts[1:] * dts[:-1])) / (len(dts) - 1)) / (np.sum(2 / dts ** 2) / len(dts))
    cl = r_["autocorr"]["C_lag"][1:4]
    print(f"    {ww}: C_lag[1..3] = {np.round(cl, 3)} (exact lag-1 for this spacing {pred:.3f}; unshuffled {np.round(w(beta1['sym512'][0][1], ww)['autocorr']['C_lag'][1:4], 3)})")
    if abs(cl[0] - pred) > 0.1 or np.max(np.abs(cl[1:])) > 0.1: fails.append(f"(c) {ww} C_lag {np.round(cl, 3)} vs {pred:.3f}")

# ---------------------------------------------------------------- (d)/(e) M3
print("(d) C5 sign flips -> M3 bit-identical")
sig, U, V, truth = C.planted_crossing(times, K=16, t0=1500.0, slope=1e-3, coupling=0.05, seed=A.seed)
r0 = M3.analyse(sig, U, V, times)
for joint in (True, False):
    U2, V2 = C.sign_flips(U, V, A.seed + 5, joint=joint)
    r1_ = M3.analyse(sig, U2, V2, times)
    m0, m1_ = M3.metric_arrays(r0), M3.metric_arrays(r1_)
    same = all(np.array_equal(m0[k], m1_[k]) for k in m0)
    print(f"    joint={joint}: identical {same} ({', '.join(f'{k}:{m0[k].shape}' for k in m0)})")
    if not same: fails.append(f"(d) joint={joint} not bit-identical")
print("(e) planted avoided crossing")
ev = [e for e in r0["events"] if e["pair"] == 0]
print("   ", M3.summary_lines(r0)[0])
if len(ev) != 1:
    fails.append(f"(e) {len(ev)} events on pair 0 (want 1)")
else:
    e = ev[0]; th_exp = C.expected_rotation(truth, e["k"])
    print(f"    event: t_min {e['t_min']:.1f} (true {truth['t_min']}), g_min {e['g_min']:.4f} (true {truth['g_min']}), theta_u {e['theta_u']:.1f} "
          f"theta_v {e['theta_v']:.1f} (analytic {th_exp:.1f} deg), ambiguous {e['ambiguous']}")
    if abs(e["t_min"] - truth["t_min"]) > 5: fails.append(f"(e) t_min {e['t_min']:.1f}")
    if abs(e["g_min"] - truth["g_min"]) > 0.1 * truth["g_min"]: fails.append(f"(e) g_min {e['g_min']:.4f}")
    if abs(e["theta_u"] - th_exp) > 5 or abs(e["theta_v"] - th_exp) > 5: fails.append(f"(e) theta {e['theta_u']:.1f}/{e['theta_v']:.1f} vs {th_exp:.1f}")
    if e["ambiguous"]: fails.append("(e) clean crossing flagged ambiguous")
sig2, U2, V2, truth2 = C.planted_crossing(times, K=16, t0=1500.0, slope=1e-3, coupling=0.005, seed=A.seed)
r2_ = M3.analyse(sig2, U2, V2, times)
ev2 = [e for e in r2_["events"] if e["pair"] == 0]
print(f"    tight crossing (2c = {truth2['g_min']}, per-step change 0.025): events {len(ev2)}, ambiguous {[e['ambiguous'] for e in ev2]}, "
      f"g_min {[round(e['g_min'], 4) for e in ev2]}; ambiguous (step,level) frac {r2_['ambiguous_frac']:.3f}")
if not ev2 or not all(e["ambiguous"] for e in ev2): fails.append("(e) tight crossing not flagged ambiguous")

# ---------------------------------------------------------------- C4 round-trip floor (reported)
fl = C.roundtrip_floor(2048, 512, times[:40], C.tau_for_xstep(512, A.xstep), 16, (0.1, 0.9), A.kde_c, A.seed)
print(f"(C4) fp32 round-trip floor (2048x512, entries rms 0.02, 40 checkpoints): per-step unfolded displacement rms {fl['step_rms']:.4f} spacings; "
      f"fp32 {fl['fp32']['unfolded_rms']:.2e} (ratio {fl['fp32']['ratio_to_step']:.2e}, raw rel {fl['fp32']['raw_rel_rms']:.1e}); "
      f"bf16 (comparison) {fl['bf16']['unfolded_rms']:.3f} (ratio {fl['bf16']['ratio_to_step']:.2f}, raw rel {fl['bf16']['raw_rel_rms']:.1e})")

print(f"runtime {time.time() - T0:.0f}s")
print(("REDPATH failures: " if RED else "FAILURES: ") + str(fails or "none"))
sys.exit((0 if fails else 1) if RED else (1 if fails else 0))
