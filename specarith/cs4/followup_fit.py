"""Round 50 (FOLLOWUP_REPLICATION_RULES.md, 4cd011d8): (A)'s fixed fit, its red paths, ∂μ*/∂μ and S_A; (B)'s L.
Data-free.

(A), §1 of the rules:
- bins with centre ≥ max(S_RES, route (a)'s S_TINY) only, S_RES the smallest 1e-4 bin centre from which p⁽²⁾_sine ≥ P2_RES
  on every later bin up to 3.0;
- the window is rejected if p⁽²⁾_sine (μ = 0) or the prediction (μ = 1) is ≤ 0 on any of its bins;
- the fit is bounded to the interval where the model density is positive on every bin of the window (and |μ| ≤ BOUND);
  a fit within 1e-6 of either end of that interval, a non-finite likelihood at μ̂, or a non-positive density at μ̂ is a
  failure (None plus the reason), never a value;
- skip rule only ("skip/rho5_zero" is the model; "skip/rho5_sine" is the other end of the T₅ bracket).
(A), §2–3: ∂μ*/∂μ from expected counts (1e9 per window) at μ′ = 0.98, 0.99, 1.01, 1.02; δμ_T5 = |μ* − 1|/(∂μ*/∂μ) with
the model at the primary end and expected counts from the other end at μ = 1; δμ_trunc by route (a)'s check-(c)
construction on 4·T6_CAP·|T₆^sine|, in μ units; SE_f = SD of the replicate fits / (∂μ*/∂μ); S_A and its three checks.
(B), §2 and §4: SE_f of μ̂_B from the k-statistic on the replicates; ∂μ*_B/∂μ = (the linear limit, evaluated) × (the
CUE_N slope, results/followup_cuen.json); metric |Σ w ∂μ*/∂μ| / (Σ w² SE²)^½; L = argmax (exact tie → smaller L).

  python followup_fit.py selftest                 (green and red paths; must pass before any calibration)
  python followup_fit.py window_A REPS_DIR        → results/followup_window_A.json
  python followup_fit.py window_B REPS_DIR        → results/followup_window_B.json
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import followup_nnn as N  # noqa: E402
import route_a_read as RR  # noqa: E402

HB, NBIN = 1e-4, 30_000
P2_RES, BOUND, EDGE = 1e-6, 20.0, 1e-6
GRID_A = np.round(np.arange(1.0, 3.0001, 0.1), 1)
GRID_L = ("0.5", "1.0", "1.5", "2.0", "3.0")
MODEL, OTHER = "skip/rho5_zero", "skip/rho5_sine"
TRUNC_FRAC, S_A_MAX = 0.01, 2.0
CENTRES = (np.arange(NBIN) + 0.5) * HB


def s_res(p2vals):
    bad = np.nonzero(p2vals < P2_RES)[0]
    return float(CENTRES[bad.max() + 1]) if len(bad) else float(CENTRES[0])


def fit_A(h, p0, dp, wbin):
    """Binned conditional ML amplitude on one window. Returns (μ̂, None) or (None, reason)."""
    if np.any(p0 <= 0):
        return None, "p_sine <= 0 in the window"
    if np.any(p0 + dp <= 0):
        return None, "prediction (μ = 1) density <= 0 in the window"
    lo, hi = -BOUND, BOUND
    pos, neg = dp > 0, dp < 0
    if pos.any():
        lo = max(lo, float(np.max(-p0[pos] / dp[pos])))
    if neg.any():
        hi = min(hi, float(np.min(p0[neg] / -dp[neg])))
    F0, FD = float(np.sum(p0 * wbin)), float(np.sum(dp * wbin))
    if FD > 0:
        lo = max(lo, -F0 / FD)
    elif FD < 0:
        hi = min(hi, F0 / -FD)
    if not lo < hi:
        return None, "no positive-density interval"
    n = h.sum()
    ok = h > 0

    def nll(mu):
        q = p0 + mu * dp
        if np.any(q <= 0) or F0 + mu * FD <= 0:
            return np.inf
        return -(np.sum(h[ok] * np.log(q[ok])) - n * np.log(F0 + mu * FD))
    mu = minimize_scalar(nll, bounds=(lo, hi), method="bounded", options=dict(xatol=1e-10)).x
    if mu - lo < EDGE or hi - mu < EDGE:
        return None, f"at the bound ({lo:.4g}, {hi:.4g})"
    if not np.isfinite(nll(mu)):
        return None, "likelihood not finite at the fit"
    if np.any(p0 + mu * dp <= 0):
        return None, "density <= 0 at the fit"
    return float(mu), None


def expected(p0, dp, mu):
    q = (p0 + mu * dp) * HB
    return q / q.sum() * 1e9


def selftest():
    import followup_select as OLD
    p2, _ = N.p2_sine()
    nnn = json.load(open(os.path.join(HERE, "results", "followup_nnn.json")))
    f = next(iter(RR.F3))
    sr = max(s_res(p2(CENTRES)), RR.S_TINY)
    sel = (CENTRES >= sr) & (CENTRES < 1.8)
    c = CENTRES[sel]
    p0 = p2(c)
    dp = N.nn_interp(nnn["files"][f][MODEL]["dp_nodes"], c)
    w = np.full(len(c), HB)
    ok = True
    # green: expected counts recover μ
    for m in (0.99, 1.01):
        mu, why = fit_A(expected(p0, dp, m), p0, dp, w)
        g = mu is not None and abs(mu - m) < 1e-6
        ok &= g
        print(f"green: expected counts at μ = {m} → {mu} ({why}) {'PASS' if g else 'FAIL'}")
    # green: a Poisson draw gives a finite fit
    rng = np.random.default_rng([20261016, 50, 0])
    h = rng.poisson(expected(p0, dp, 1.0) * 5e6 / 1e9).astype(float)
    mu, why = fit_A(h, p0, dp, w)
    g = mu is not None and abs(mu - 1) < 0.5
    ok &= g
    print(f"green: Poisson draw (5e6) → {mu} ({why}) {'PASS' if g else 'FAIL'}")
    # red 1: one injected negative interpolation bin at a bin with a positive count
    k = int(np.argmax(h))
    p0b = p0.copy()
    p0b[k] = -1e-9
    mu, why = fit_A(h, p0b, dp, w)
    r1 = mu is None
    old = OLD.fit_A(h, p0b, dp, w)
    old_bound = abs(abs(old) - 20) < 1e-3
    ok &= r1 and old_bound
    print(f"red 1: injected p_sine = −1e-9 at bin {k} (count {h[k]:.0f}) → {why!r} "
          f"{'PASS' if r1 else 'FAIL (returned a value)'}; the d3c50fa8 fit returns {old:.6f} "
          f"({'a bound value: the red path can fire' if old_bound else 'NOT a bound value'})")
    # red 2: a model whose density is non-positive near μ = 1 on a bin of the window
    dpb = dp.copy()
    j = int(np.argmax(h))
    dpb[j] = -2 * p0[j]
    mu, why = fit_A(expected(p0, dp, 1.0), p0, dpb, w)
    r2 = mu is None
    ok &= r2
    print(f"red 2: Δp⁽²⁾ := −2p_sine at bin {j} (density < 0 there for μ > 0.5) → {mu} ({why}) "
          f"{'PASS' if r2 else 'FAIL (returned a value)'}")
    print("selftest:", "PASS" if ok else "FAIL")
    return ok


# ------------------------------------------------------------------ (A)'s window
def load_reps(d):
    by = {}
    for fn in sorted(os.listdir(d)):
        if fn.startswith("reps_"):
            for line in open(os.path.join(d, fn)):
                r = json.loads(line)
                by.setdefault(r["file"], {})[r["rep"]] = r
    return by


_G = {}


def _invalid(s, why):
    """A window where the model itself is invalid (e.g. the μ = 1 density ≤ 0) cannot satisfy the S_A condition."""
    print(f"(A) s ≤ {s:.1f}: INVALID WINDOW — {why}", flush=True)
    return f"{s:.1f}", dict(valid=False, reason=why, t5_ok=False, trunc_ok=False, failures=0)


def _window(s):
    reps, nnn, sr, p0_all, trunc_all, wts = (_G[k] for k in ("reps", "nnn", "sr", "p0", "trunc", "w"))
    sel = np.nonzero((CENTRES >= sr) & (CENTRES < s - 1e-12))[0]
    c, p0 = CENTRES[sel], p0_all[sel]
    wbin = np.full(len(sel), HB)
    per = {}
    for f in RR.F3:
        dp = N.nn_interp(nnn["files"][f][MODEL]["dp_nodes"], c)
        dpo = N.nn_interp(nnn["files"][f][OTHER]["dp_nodes"], c)
        lim = {}
        for m in (0.98, 0.99, 1.01, 1.02):
            lim[m], why = fit_A(expected(p0, dp, m), p0, dp, wbin)
            if why:
                return _invalid(s, f"{f}: estimator-limit fit failed at μ′ = {m}: {why}")
        slope = (lim[1.01] - lim[0.99]) / 0.02
        lin = abs((lim[1.02] - lim[0.98]) / 0.04 - slope)
        mo, why = fit_A(expected(p0, dpo, 1.0), p0, dp, wbin)
        if why:
            return _invalid(s, f"{f}: T₅-bracket fit failed: {why}")
        mus, fails = [], []
        for k in sorted(reps[f]):
            h = _G["hist"][(f, k)][sel]
            mu, why = fit_A(h, p0, dp, wbin)
            (fails.append([k, why]) if why else mus.append(mu))
        se_raw = float(np.std(mus, ddof=1)) if len(mus) > 1 else float("nan")
        per[f] = dict(dmustar_dmu=slope, linearity=lin, se_raw=se_raw, se_mu=se_raw / slope,
                      dmu_T5=abs(mo - 1) / slope,
                      dmu_trunc=float(np.sum(trunc_all[sel] * np.abs(dp)) / np.sum(dp ** 2)) / slope,
                      n_fit=len(mus), failures=fails)
    se_pool = float(np.sqrt(sum(wts[f] ** 2 * per[f]["se_mu"] ** 2 for f in RR.F3)))
    t5 = float(sum(wts[f] * per[f]["dmu_T5"] for f in RR.F3))
    tr = float(sum(wts[f] * per[f]["dmu_trunc"] for f in RR.F3))
    out = dict(valid=True, files=per, se_pool_mu=se_pool, band=2 * se_pool, dmu_T5_pool=t5, dmu_trunc_pool=tr,
               dmustar_dmu_pool=float(sum(wts[f] * per[f]["dmustar_dmu"] for f in RR.F3)),
               t5_ok=t5 <= TRUNC_FRAC * 2 * se_pool, trunc_ok=tr <= TRUNC_FRAC * 2 * se_pool,
               failures=sum(len(per[f]["failures"]) for f in RR.F3))
    print(f"(A) s ≤ {s:.1f}: SE_pool {se_pool:.5f} (μ units), δμ_T5 {t5:.2e} (≤ {TRUNC_FRAC * 2 * se_pool:.2e}? "
          f"{out['t5_ok']}), δμ_trunc {tr:.2e} ({out['trunc_ok']}), ∂μ*/∂μ "
          f"{min(p['dmustar_dmu'] for p in per.values()):.5f}–{max(p['dmustar_dmu'] for p in per.values()):.5f}, "
          f"linearity ≤ {max(p['linearity'] for p in per.values()):.1e}, failures {out['failures']}", flush=True)
    return f"{s:.1f}", out


def window_A(reps_dir, procs=21):
    reps = load_reps(reps_dir)
    assert all(len(reps[f]) == 100 for f in RR.F3), {f: len(reps.get(f, {})) for f in RR.F3}
    nnn = json.load(open(os.path.join(HERE, "results", "followup_nnn.json")))
    p2, _ = N.p2_sine()
    p0_all = p2(CENTRES)
    sr = max(s_res(p0_all), RR.S_TINY)
    g = np.linspace(0, sr, 20001)
    mass = float(np.trapezoid(np.maximum(p2(g), 0), g))
    print(f"S_RES {sr:.4f} (p⁽²⁾_sine ≥ {P2_RES} from there on); sine mass below it {mass:.2e} per spacing"
          f"{' — OVER 1e-7: to Will' if mass > 1e-7 else ''}", flush=True)
    w, _ = RR.weights()
    _G.update(reps=reps, nnn=nnn, sr=sr, p0=p0_all, w=w,
              trunc=np.abs(N.nn_interp(nnn["trunc6_bound"], CENTRES)),
              hist={(f, k): np.load(os.path.join(reps_dir, reps[f][k]["hist"])).astype(float)[:NBIN]
                    for f in RR.F3 for k in reps[f]})
    with Pool(procs) as P:
        win = dict(P.map(_window, list(GRID_A)))
    good = [s for s in win if win[s]["t5_ok"]]
    SA = max(good, key=float) if good else None
    checks = {}
    if SA:
        checks = dict(contiguous=all(win[s]["t5_ok"] for s in win if float(s) <= float(SA)),
                      all_valid_below=all(win[s]["valid"] for s in win if float(s) <= float(SA)),
                      trunc6_at_SA=win[SA]["trunc_ok"], SA_le_2=float(SA) <= S_A_MAX,
                      no_failures=all(win[s]["failures"] == 0 for s in win if float(s) <= float(SA)))
    res = dict(round="fiftieth", rules="FOLLOWUP_REPLICATION_RULES.md (4cd011d8)", model=MODEL, other_end=OTHER,
               S_RES=sr, sine_mass_below_S_RES=mass, P2_RES=P2_RES, windows=win, S_A=SA, checks=checks,
               to_will=(SA is None) or not all(checks.values()) or mass > 1e-7)
    json.dump(res, open(os.path.join(HERE, "results", "followup_window_A.json"), "w"), indent=1)
    print(f"S_A = {SA}; checks {checks}" + ("  → TO WILL" if res["to_will"] else ""), flush=True)
    return 0


# ------------------------------------------------------------------ (B)'s window
def window_B(reps_dir):
    reps = load_reps(reps_dir)
    assert all(len(reps[f]) == 100 for f in RR.F3)
    k3 = json.load(open(os.path.join(HERE, "results", "followup_k3.json")))
    cu = json.load(open(os.path.join(HERE, "results", "followup_cuen.json")))
    w, _ = RR.weights()
    out = {}
    for L in GRID_L:
        sl, sl_se = cu["L"][L]["slope"], cu["L"][L]["slope_se"]
        per = {}
        for f in RR.F3:
            t = k3["files"][f][L]
            lim = ((t["kappa3_sine"] + 1.01 * t["dkappa3"] - t["kappa3_sine"]) / t["dkappa3"]
                   - (t["kappa3_sine"] + 0.99 * t["dkappa3"] - t["kappa3_sine"]) / t["dkappa3"]) / 0.02
            mus = []
            for r in reps[f].values():
                b = np.array(r["counts"][L], float)
                v = np.arange(len(b))
                W = b.sum()
                m = (v * b).sum() / W
                m3 = ((v - m) ** 3 * b).sum() / W
                mus.append((W * W * m3 / ((W - 1) * (W - 2)) - t["kappa3_sine"]) / t["dkappa3"])
            per[f] = dict(limit=lim, dmustar_dmu=lim * sl, se_raw=float(np.std(mus, ddof=1)))
        num = abs(sum(w[f] * per[f]["dmustar_dmu"] for f in RR.F3))
        den = float(np.sqrt(sum(w[f] ** 2 * per[f]["se_raw"] ** 2 for f in RR.F3)))
        out[L] = dict(files=per, cuen_slope=sl, cuen_slope_se=sl_se, metric=num / den, se_pool_raw=den)
        print(f"(B) L = {L}: CUE_N slope {sl:.4f} ± {sl_se:.4f}; limit {per[next(iter(RR.F3))]['limit']:.12f}; "
              f"SE_pool {den:.5f}; metric {num / den:.2f}", flush=True)
    best = max(GRID_L, key=lambda L: (out[L]["metric"], -float(L)))
    res = dict(round="fiftieth", rules="FOLLOWUP_REPLICATION_RULES.md (4cd011d8)", windows=out, L=best,
               slope_se_ok=all(out[L]["cuen_slope_se"] <= 0.05 for L in GRID_L))
    json.dump(res, open(os.path.join(HERE, "results", "followup_window_B.json"), "w"), indent=1)
    print(f"L = {best}; CUE_N slope SE ≤ 0.05 at every L: {res['slope_se_ok']}", flush=True)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    elif cmd == "window_A":
        sys.exit(window_A(sys.argv[2]))
    elif cmd == "window_B":
        sys.exit(window_B(sys.argv[2]))
