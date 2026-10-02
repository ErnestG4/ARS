"""Known answers for the C9 / C1-driver attribution controls (pdyn_c9.py). Synthetic only -- NO cache/armb read and
no phase-1 result read. Shape 512 x 512 (rectangular SVD, the pipeline's real object), time grid = the real W2 grid
(grids.arm_grid A0 restricted to [500, 3001): 102 checkpoints every 25 steps plus the log step 512), vrms matched to
--vrms spacings/step (default 0.0177 = A0 L0 Q on W2, x_step 0.44), the sealed pdyn_m2 PARAMS throughout.

A synthetic "real" series is a C1 draw warped by a PLANTED smooth drift (||W||_F x 1.5 and the band's log-sd x 1.2,
both linear in time), so the extraction has a known answer. Deviations use pdyn_c9's comparison: C_lag[1..6]
(tolerance 0.10) and the DENSE-bin C(x <= 2) (bins with >= 1000 pairs; tolerance 0.15); same-seed checks use half
those tolerances (0.05 / 0.075).

Checks (exit 1 on any failure; the FAILURES line lists them):
 (i)    zero drift: the C1 draw warped by the time-MEAN slow map (a fixed map, the real density shape, no drift) reads
        as its own unwarped self within half the two-draw tolerance; the scale-only map (time-mean shape x the planted
        ||W||_F(t)) gives C_lag[1..6] identical to the zero-drift map to 1e-9 (the sealed unfolding is
        dilation-invariant).
 (ii)   the control CAN fire: the zero map plus the planted rank-structured drift (lambda = 24 ranks, A = 20 and 50
        spacings end-to-end) fills the dip: C_lag[1] rises above the zero-drift value by > 0.10 and the dip depth
        (min C over dense bins, 0.3 <= x <= 2) rises by > 0.15, at A = 50 (reported for A = 5, 20, 50; the first run
        read the dip on a 10-pair bin and A = 50 did not fire -> dip taken on dense bins; A = 20, the largest amplitude
        whose vrms still matches within 5 %, moves C_lag[1] by +0.30 and the dip by +0.11).
 (iii)  tau_v -> 0 of the driver is the literal DBM: driver(tau_v = 0) and pdyn_calib.dbm_sym(rect) at the same
        matched vrms agree within the two-draw tolerance (lag 0.10, dense C(x) 0.15) and both have C_lag[1] below
        the C1 value by > 0.10 (no SA structure).
 (iii-b) tau_v = tau_C1 (the C1 draw's matched Gaussian-kernel time constant) reads as C1 within the two-draw
        tolerance (an independent C1 draw is the reference).
 (iv)   extraction known answer: slow_component (h = 32, sigma_t = 200) applied to the synthetic real recovers the
        planted log-quantile DRIFT (the time course minus its per-rank time mean; a time-constant rank-dependent
        offset is a fixed map, invisible to the pipeline up to the (i) footprint) with an rms error over the band and
        the inner window [t0 + 2 sigma_t, t1 - 2 sigma_t] no larger than 1.5 x the LEAKAGE of the beta = 1 motion
        through the same extraction on a zero-drift series (an independent C1 draw under a fixed map; measured
        ~0.3 spacings at h = 32, sigma_t = 200 -- the first run gated at an absolute 0.3 and read 0.311), and the
        planted edge-90 move over the inner window within 10 %;
        the matched C9 built from it (the planted SMOOTH drift imposed on an independent C1 draw) stays at C1 within
        the two-draw tolerance (a smooth deformation is removed by the per-checkpoint unfolding).
--redpath: flip (ii)'s threshold (the planted A = 50 drift must then NOT fill the dip); exit 0 iff (ii) fails.
"""
import sys, time, argparse, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pdyn_m2 as M2, pdyn_calib as C, pdyn_c9 as C9  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--redpath", action="store_true"); ap.add_argument("--vrms", type=float, default=0.0177)
ap.add_argument("--n", type=int, default=512); ap.add_argument("--seed", type=int, default=0)
A = ap.parse_args()
RED = A.redpath; fails = []; T0 = time.time()
g = C.real_grid(3000); tw = g[(g >= 500) & (g < 3001)]
n = A.n; m = n; V = A.vrms; DT = float(np.median(np.diff(tw)))
TOL_LAG, TOL_CX = C9.TOL["C_lag"], C9.TOL["Cx"]
HALF_LAG, HALF_CX = 0.05, 0.075
SIG_T, H = C9.VARIANTS["smooth"]["sigma_t"], C9.VARIANTS["smooth"]["h"]
print(f"grid: {len(tw)} checkpoints {tw[0]:.0f}..{tw[-1]:.0f} (median dt {DT:.0f}); shape {m}x{n}; target vrms {V} (x_step {V * DT:.3f}); seed {A.seed}")


def devs(ra, rb, min_pairs=C9.DENSE_PAIRS):
    """(max |dC_lag[1..6]|, max dense |dC(x<=2)|) between two pdyn_m2 window dicts."""
    x = ra["autocorr"]["x"]
    d_cx, d_lag, _ = C9.dev_curves(ra["autocorr"]["C"], ra["autocorr"]["n_pairs"], rb["autocorr"]["C"], rb["autocorr"]["n_pairs"], x,
                                   ra["autocorr"]["C_lag"], rb["autocorr"]["C_lag"], min_pairs)
    return d_lag * TOL_LAG, d_cx * TOL_CX


def lag(r, j=1): return float(r["autocorr"]["C_lag"][j])


def dipv(r): return C9.dip(r["autocorr"]["C"], r["autocorr"]["n_pairs"], r["autocorr"]["x"])[0]


def c1_matched(seed):
    tau = C.tau_for_xstep(n, V * DT, DT)
    S = C9.gen_c1(m, n, tw, tau, seed); r, _ = C9.m2_single(S, tw)
    tau *= float(r["vrms"]) / V
    S = C9.gen_c1(m, n, tw, tau, seed); r, _ = C9.m2_single(S, tw)
    return S, r, tau


# ---------------------------------------------------------------- setup: C1 draws and the synthetic real with a planted smooth drift
t1 = time.time()
S0, r0, tau0 = c1_matched(A.seed)                       # the draw every C9 variant warps
S1, r1, tau1 = c1_matched(A.seed + 1000)                # independent C1 reference
Sr_base, rr_base, _ = c1_matched(A.seed + 2000)         # base of the synthetic real
Sb = C9.strip_sort(Sr_base); n_eff = Sb.shape[1]
Lmean_base = np.log(Sb).mean(0)
tt = (tw - tw[0]) / (tw[-1] - tw[0])
scale = np.log(1.5) * tt                                 # ||W||_F x 1.5 over the window
stretch = 1.0 + 0.2 * tt                                 # band log-sd x 1.2
Ltrue = (Lmean_base[None, :] - Lmean_base.mean()) * stretch[:, None] + Lmean_base.mean() + scale[:, None]
S_real = C9.warp(Sr_base, Ltrue)                         # the synthetic real: planted smooth drift + beta=1 motion
r_real, _ = C9.m2_single(S_real, tw)
print(f"setup: C1 draws tau {tau0:.0f}/{tau1:.0f}; vrms {float(r0['vrms']):.5f} {float(r1['vrms']):.5f} (target {V}); synthetic real vrms {float(r_real['vrms']):.5f}; "
      f"C1 C_lag[1..3] {np.round(r0['autocorr']['C_lag'][1:4], 3)} / {np.round(r1['autocorr']['C_lag'][1:4], 3)} two-draw dev lag {devs(r0, r1)[0]:.3f} dense {devs(r0, r1)[1]:.3f} ({time.time() - t1:.0f}s)")
Sreal_stripped = C9.strip_sort(S_real)
a_, b_ = int(np.ceil(0.1 * n_eff)), int(np.ceil(0.9 * n_eff))

# ---------------------------------------------------------------- (i) zero drift and scale-only
t1 = time.time()
Lrec = C9.slow_component(Sreal_stripped, tw, H, SIG_T); Lmean = Lrec.mean(0)
r_zero, _ = C9.m2_single(C9.warp(S0, Lmean), tw)
fro = np.sqrt((S_real ** 2).sum(1)); Lscale = Lmean[None, :] + (np.log(fro) - np.log(fro).mean())[:, None]
r_scale, _ = C9.m2_single(C9.warp(S0, Lscale), tw)
dl, dc = devs(r_zero, r0); dls = float(np.max(np.abs(r_scale["autocorr"]["C_lag"][1:7] - r_zero["autocorr"]["C_lag"][1:7])))
print(f"(i) zero-drift warp vs same-seed C1: max|dC_lag[1..6]| {dl:.4f} (<= {HALF_LAG}), dense max|dC(x<=2)| {dc:.4f} (<= {HALF_CX}); "
      f"C_lag[1] {lag(r_zero):+.3f} vs {lag(r0):+.3f}; med|k| {r_zero['curvature']['abs_k_median']:.3f} vs {r0['curvature']['abs_k_median']:.3f} | "
      f"scale-only vs zero: max|dC_lag| {dls:.2e} (<= 1e-9; fro x{fro[-1] / fro[0]:.2f}) ({time.time() - t1:.0f}s)")
if dl > HALF_LAG: fails.append(f"(i) zero-drift C_lag dev {dl:.3f}")
if dc > HALF_CX: fails.append(f"(i) zero-drift dense C(x) dev {dc:.3f}")
if dls > 1e-9: fails.append(f"(i) scale-only not dilation-invariant: {dls:.2e}")

# ---------------------------------------------------------------- (ii) planted rank-structured drift fills the dip
t1 = time.time()
res_pl = {}
for amp in (5.0, 20.0, 50.0):
    Lpl = Lmean[None, :] + C9.planted_field(n_eff, tw, Lmean, amp)
    mk = lambda tau, _L=Lpl: C9.warp(C9.gen_c1(m, n, tw, tau, A.seed), _L)
    S, r, _, match = C9.match_scale(mk, V, tau0, mode="inv", extra=tw)
    res_pl[amp] = (r, match)
    print(f"(ii) planted A={amp:g} (lambda {C9.PLANTED_LAMBDA:g} ranks): C_lag[1] {lag(r):+.3f} (zero {lag(r_zero):+.3f}), C_lag[2] {lag(r, 2):+.3f}, dip {dipv(r):+.3f} (zero {dipv(r_zero):+.3f}), "
          f"med|k| {r['curvature']['abs_k_median']:.3f}, vrms/target {match['vrms_measured'] / V:.3f} (matched {match['matched']}, tau {match['tau'] if 'tau' in match else match['p']:.0f})")
r50 = res_pl[50.0][0]
d_lag1 = lag(r50) - lag(r_zero); d_dip = dipv(r50) - dipv(r_zero)
fires = (d_lag1 > TOL_LAG) and (d_dip > TOL_CX)
if RED: fires = not fires                                 # flipped: the planted drift must NOT fill the dip
print(f"(ii) A=50: dC_lag[1] {d_lag1:+.3f} (> {TOL_LAG}), d dip {d_dip:+.3f} (> {TOL_CX}) -> {'fires' if fires else 'DOES NOT FIRE'}{' (threshold FLIPPED)' if RED else ''} ({time.time() - t1:.0f}s)")
if not fires: fails.append(f"(ii) planted A=50 does not fill the dip: dC_lag1 {d_lag1:+.3f}, d dip {d_dip:+.3f}{' (FLIPPED)' if RED else ''}")

# ---------------------------------------------------------------- (iii) driver tau_v -> 0 is the literal DBM; (iii-b) tau_v = tau_C1 is C1
t1 = time.time()
s0 = np.sort(C9.svd(np.random.default_rng(A.seed).standard_normal((m, n)), compute_uv=False))[:n - C9.TOP_K]
Delta = (s0[b_ - 1] - s0[a_]) / (b_ - a_ - 1)
mk = lambda s: C9.gen_driver(m, n, tw, 0.0, s, A.seed + 5)
S_d0, r_d0, _, m_d0 = C9.match_scale(mk, V, V * Delta / math.sqrt(DT), mode="prop", extra=tw)
mk = lambda xs: C.dbm_sym(n, tw, xstep=xs, seed=A.seed + 6, rect=(m, n), dt_ref=DT)
S_db, r_db, _, m_db = C9.match_scale(mk, V, V * DT, mode="prop", extra=tw)
dl, dc = devs(r_d0, r_db)
print(f"(iii) driver tau_v=0: C_lag[1..3] {np.round(r_d0['autocorr']['C_lag'][1:4], 3)} med|k| {r_d0['curvature']['abs_k_median']:.3f} vrms/target {m_d0['vrms_measured'] / V:.3f} | "
      f"pdyn_calib.dbm_sym(rect): C_lag[1..3] {np.round(r_db['autocorr']['C_lag'][1:4], 3)} med|k| {r_db['curvature']['abs_k_median']:.3f} vrms/target {m_db['vrms_measured'] / V:.3f} | "
      f"dev lag {dl:.3f} (<= {TOL_LAG}) dense {dc:.3f} (<= {TOL_CX}); C_lag[1] below C1 by {lag(r0) - lag(r_d0):+.3f} / {lag(r0) - lag(r_db):+.3f} (> {TOL_LAG}) ({time.time() - t1:.0f}s)")
if dl > TOL_LAG or dc > TOL_CX: fails.append(f"(iii) driver tau_v=0 vs literal DBM: lag {dl:.3f} dense {dc:.3f}")
if (lag(r0) - lag(r_d0)) <= TOL_LAG or (lag(r0) - lag(r_db)) <= TOL_LAG: fails.append("(iii) DBM limit does not lose the SA lag-1 value")
t1 = time.time()
mk = lambda s: C9.gen_driver(m, n, tw, tau0, s, A.seed + 7)
S_dc, r_dc, _, m_dc = C9.match_scale(mk, V, V * Delta, mode="prop", extra=tw)
dl, dc = devs(r_dc, r1); dl0, dc0 = devs(r_dc, r0)
print(f"(iii-b) driver tau_v = tau_C1 = {tau0:.0f}: C_lag[1..3] {np.round(r_dc['autocorr']['C_lag'][1:4], 3)} med|k| {r_dc['curvature']['abs_k_median']:.3f} vrms/target {m_dc['vrms_measured'] / V:.3f} | "
      f"vs independent C1: dev lag {dl:.3f} (<= {TOL_LAG}) dense {dc:.3f} (<= {TOL_CX}); vs C1 seed 0: {dl0:.3f} / {dc0:.3f} ({time.time() - t1:.0f}s)")
if dl > TOL_LAG or dc > TOL_CX: fails.append(f"(iii-b) driver tau_v=tau_C1 vs C1: lag {dl:.3f} dense {dc:.3f}")

# ---------------------------------------------------------------- (iv) extraction known answer and the matched C9 of a smooth drift
t1 = time.time()
inner = (tw >= tw[0] + 2 * SIG_T) & (tw <= tw[-1] - 2 * SIG_T)
loc = np.gradient(Ltrue.mean(0))                                        # local log-spacing per rank
Drec = Lrec - Lrec[inner].mean(0); Dtrue = Ltrue - Ltrue[inner].mean(0)   # drift = time course minus per-rank mean
err = (Drec - Dtrue)[inner][:, a_:b_] / loc[None, a_:b_]
off = float(np.sqrt((((Lrec - Ltrue)[inner][:, a_:b_] / loc[None, a_:b_]) ** 2).mean()))
i0, i1 = np.where(inner)[0][[0, -1]]
mv_true = (Ltrue[i1, b_ - 1] - Ltrue[i0, b_ - 1]) / loc[b_ - 1]; mv_rec = (Lrec[i1, b_ - 1] - Lrec[i0, b_ - 1]) / loc[b_ - 1]
rms_err = float(np.sqrt((err ** 2).mean()))
Lnull = C9.slow_component(C9.strip_sort(C9.warp(S1, Lmean_base)), tw, H, SIG_T)      # zero-drift series: the extraction's leakage
leak = float(np.sqrt((((Lnull - Lnull[inner].mean(0))[inner][:, a_:b_] / loc[None, a_:b_]) ** 2).mean()))
print(f"(iv) extraction (h {H:g}, sigma_t {SIG_T:g}) vs planted: drift rms error over the band, inner window {rms_err:.3f} spacings (<= 1.5 x leakage; leakage on a zero-drift series {leak:.3f}; "
      f"the time-constant map offset is {off:.2f} spacings rms, not gated); edge-90 move over the inner window planted {mv_true:+.1f} recovered {mv_rec:+.1f} spacings (within 10 %); "
      f"planted total: fro x{fro[-1] / fro[0]:.2f}, logsd x{np.log(Sreal_stripped[-1, a_:b_]).std() / np.log(Sreal_stripped[0, a_:b_]).std():.2f}")
if rms_err > 1.5 * leak: fails.append(f"(iv) extraction rms error {rms_err:.3f} spacings > 1.5 x leakage {leak:.3f}")
if abs(mv_rec / mv_true - 1) > 0.10: fails.append(f"(iv) edge-90 move recovered {mv_rec:.1f} vs planted {mv_true:.1f}")
mk = lambda tau: C9.warp(C9.gen_c1(m, n, tw, tau, A.seed), Lrec)
S_m, r_m, _, m_m = C9.match_scale(mk, V, tau0, mode="inv", extra=tw)
dl, dc = devs(r_m, r0); dli, dci = devs(r_m, r1)
print(f"(iv) matched C9 of the planted smooth drift: C_lag[1..3] {np.round(r_m['autocorr']['C_lag'][1:4], 3)} med|k| {r_m['curvature']['abs_k_median']:.3f} vrms/target {m_m['vrms_measured'] / V:.3f} "
      f"(tau {m_m['p']:.0f} vs C1 {tau0:.0f}) | vs same-seed C1: dev lag {dl:.3f} dense {dc:.3f} (<= {TOL_LAG} / {TOL_CX}); vs independent C1: {dli:.3f} / {dci:.3f} | "
      f"synthetic real itself vs C1: lag {devs(r_real, r1)[0]:.3f} dense {devs(r_real, r1)[1]:.3f} ({time.time() - t1:.0f}s)")
if dl > TOL_LAG or dc > TOL_CX: fails.append(f"(iv) matched C9 of a smooth drift departs from C1: lag {dl:.3f} dense {dc:.3f}")

print(f"runtime {time.time() - T0:.0f}s")
print(("REDPATH failures: " if RED else "FAILURES: ") + str(fails or "none"))
red_fired = any(f.startswith("(ii)") for f in fails)
sys.exit((0 if red_fired else 1) if RED else (1 if fails else 0))
