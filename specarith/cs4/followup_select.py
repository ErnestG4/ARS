"""The follow-up observable choice, FOLLOWUP_SELECTION_RULE.md with amendment 1 (rounds 48–49). Data-free; mechanical.
Committed before the κ₃ terms (results/followup_k3.json), the NNN terms (results/followup_nnn.json) and the CUE replicates
(results/followup_reps/) were combined or read.

Global μ family: each candidate's per-file amplitude μ̂_f has ∂μ*_f/∂μ = 1 (an amplitude in its own linear family;
checked numerically for (A) from expected counts), so metric = 1/SE_pool with SE_pool = (Σ w_f² SE_f²)^½, w_f ∝ n_f.

(A) next-nearest-neighbour law, window s⁽²⁾ ≤ s:
- μ̂_f is the binned conditional ML on the replicate's 1e-4 histogram: maximise Σ_b h_b log q_μ(s_b), with
  q_μ = (p⁽²⁾_sine + μΔp⁽²⁾)/∫₀ˢ(p⁽²⁾_sine + μΔp⁽²⁾) at bin centres (s_b ≥ route (a)'s S_TINY).
- SE_f(s) is the SD of μ̂_f over the R = 100 replicates.
- δμ_trunc(s) = Σ|trunc|·|Δp⁽²⁾| / Σ(Δp⁽²⁾)² on the window grid (route (a)'s check (c) construction), with trunc
  interpolated from 4·T6_CAP·|T₆^sine| at the nodes. The pooled δμ_trunc uses w_f.
- S_A is the largest s on {1.0, 1.1, …, 3.0} with pooled δμ_trunc(s) ≤ 0.01 × 2·SE_pool(s). If there is none, (A) is not
  eligible. Its block-cut share is 1 by construction (Δp⁽²⁾ has no ρ₂ term).
- Variants: route (a)'s skip rule (primary) and every node; ΔT₅ = −T₅^sine (primary) and 0. The choice must be the same
  in all four, or it is reported as not robust and goes to Will.

(B) third cumulant of the count, window L:
- k₃ is the k-statistic of the counts, from each replicate's count distribution: W²·m₃/((W − 1)(W − 2)).
- μ̂_f = (k₃ − κ₃^sine(L))/Δκ₃,f(L), and SE_f(L) is its SD over the replicates.
- Block-cut share, per file: (ΔF₃ + 3L·ΔF₂)/(3ΔF₂ + ΔF₃). Pooled share = Σ w_f share_f, fixed here before any value
  was seen. L is eligible if the pooled share ≥ 0.55; (B) uses its eligible L with the highest metric.

Choice: the highest metric among eligible candidates; if neither is eligible, report and stop.

  python followup_select.py REPS_DIR        → results/followup_selection.json
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import followup_nnn as N  # noqa: E402
import route_a_read as RR  # noqa: E402

GRID_A = np.round(np.arange(1.0, 3.0001, 0.1), 1)
HB = 1e-4
SHARE_MIN, TRUNC_FRAC = 0.55, 0.01


def load_reps(d):
    rows = [json.loads(line) for fn in sorted(os.listdir(d)) if fn.startswith("reps_") for line in open(os.path.join(d, fn))]
    by = {}
    for r in rows:
        by.setdefault(r["file"], {})[r["rep"]] = r
    return by


_H = {}


def hists(reps, f):
    if f not in _H:
        _H[f] = [np.load(os.path.join(REPS, reps[f][k]["hist"])).astype(float) for k in sorted(reps[f])]
    return _H[f]


def fit_A(h, p0, dp, wbin):
    """Binned conditional ML amplitude on one window (arrays over the window's bins)."""
    n = h.sum()
    F0, FD = np.sum(p0 * wbin), np.sum(dp * wbin)
    ok = h > 0

    def nll(mu):
        q = p0 + mu * dp
        if np.any(q[ok] <= 0):
            return np.inf
        return -(np.sum(h[ok] * np.log(q[ok])) - n * np.log(F0 + mu * FD))
    return minimize_scalar(nll, bounds=(-20, 20), method="bounded", options=dict(xatol=1e-10)).x


def candidate_A(reps, nnn, variant):
    w, _ = RR.weights()
    p2, _ = N.p2_sine()
    centres = (np.arange(int(round(3.0 / HB))) + 0.5) * HB
    p0_all = p2(centres)
    trunc_all = np.abs(N.nn_interp(nnn["trunc6_bound"], centres))
    out = {}
    for s in GRID_A:
        nb = int(round(s / HB))
        sel = np.arange(nb)
        sel = sel[centres[sel] >= RR.S_TINY]
        se, dmu, chk = {}, {}, {}
        for f in RR.F3:
            dpf = N.nn_interp(nnn["files"][f][variant]["dp_nodes"], centres[sel])
            p0 = p0_all[sel]
            wbin = np.full(len(sel), HB)
            mus = [fit_A(h[sel], p0, dpf, wbin) for h in hists(reps, f)]
            se[f] = float(np.std(mus, ddof=1))
            dmu[f] = float(np.sum(trunc_all[sel] * np.abs(dpf)) / np.sum(dpf ** 2))
            # ∂μ*/∂μ = 1 check: expected counts of p_{1+ε} refitted
            exp = lambda m: (p0 + m * dpf) * HB / np.sum((p0 + m * dpf) * HB) * 1e9          # noqa: E731
            chk[f] = float((fit_A(exp(1.01), p0, dpf, wbin) - fit_A(exp(0.99), p0, dpf, wbin)) / 0.02)
        se_pool = float(np.sqrt(sum(w[f] ** 2 * se[f] ** 2 for f in RR.F3)))
        dmu_pool = float(sum(w[f] * dmu[f] for f in RR.F3))
        out[f"{s:.1f}"] = dict(se_file=se, se_pool=se_pool, dmu_trunc_file=dmu, dmu_trunc_pool=dmu_pool,
                               trunc_ok=dmu_pool <= TRUNC_FRAC * 2 * se_pool, dmustar_dmu_file=chk,
                               metric=float(sum(w[f] * chk[f] for f in RR.F3)) / se_pool)
        print(f"(A) {variant} s ≤ {s:.1f}: SE_pool {se_pool:.4f}, δμ_trunc {dmu_pool:.2e} (≤ {TRUNC_FRAC * 2 * se_pool:.2e}? "
              f"{out[f'{s:.1f}']['trunc_ok']}), ∂μ*/∂μ {min(chk.values()):.4f}–{max(chk.values()):.4f}, "
              f"metric {out[f'{s:.1f}']['metric']:.1f}", flush=True)
    ok = [s for s in out if out[s]["trunc_ok"]]
    SA = max(ok, key=float) if ok else None
    return dict(windows=out, S_A=SA, eligible=SA is not None, metric=out[SA]["metric"] if SA else None, share=1.0)


def candidate_B(reps, k3):
    w, _ = RR.weights()
    out = {}
    for L in ("0.5", "1.0", "1.5", "2.0", "3.0"):
        se, share = {}, {}
        for f in RR.F3:
            t = k3["files"][f][L]
            mus = []
            for r in reps[f].values():
                b = np.array(r["counts"][L], float)
                v = np.arange(len(b))
                W = b.sum()
                m = (v * b).sum() / W
                m3 = ((v - m) ** 3 * b).sum() / W
                k3s = W * W * m3 / ((W - 1) * (W - 2))
                mus.append((k3s - t["kappa3_sine"]) / t["dkappa3"])
            se[f] = float(np.std(mus, ddof=1))
            share[f] = (t["dF3"] + 3 * float(L) * t["dF2"]) / t["dkappa3"]
        se_pool = float(np.sqrt(sum(w[f] ** 2 * se[f] ** 2 for f in RR.F3)))
        sh = float(sum(w[f] * share[f] for f in RR.F3))
        out[L] = dict(se_file=se, se_pool=se_pool, share_file=share, share_pool=sh, eligible=sh >= SHARE_MIN,
                      metric=1.0 / se_pool)
        print(f"(B) L = {L}: SE_pool {se_pool:.4f}, block-cut share {sh:.3f} (eligible {sh >= SHARE_MIN}), metric "
              f"{1.0 / se_pool:.2f}", flush=True)
    el = [L for L in out if out[L]["eligible"]]
    best = max(el, key=lambda L: out[L]["metric"]) if el else None
    return dict(windows=out, L=best, eligible=best is not None, metric=out[best]["metric"] if best else None)


def main(reps_dir):
    global REPS
    REPS = reps_dir
    reps = load_reps(reps_dir)
    assert all(len(reps[f]) == 100 for f in RR.F3), {f: len(reps.get(f, {})) for f in RR.F3}
    nnn = json.load(open(os.path.join(HERE, "results", "followup_nnn.json")))
    k3 = json.load(open(os.path.join(HERE, "results", "followup_k3.json")))
    B = candidate_B(reps, k3)
    res = dict(round="forty-ninth", rule="FOLLOWUP_SELECTION_RULE.md + amendment 1", R=100, B=B, A={}, choice={})
    for variant in ("skip/rho5_zero", "skip/rho5_sine", "every_node/rho5_zero", "every_node/rho5_sine"):
        A = candidate_A(reps, nnn, variant)
        res["A"][variant] = A
        el = [(c, m) for c, m, e in (("A", A["metric"], A["eligible"]), ("B", B["metric"], B["eligible"])) if e]
        res["choice"][variant] = (max(el, key=lambda x: (x[1], x[0] == "A"))[0] if el else "NEITHER ELIGIBLE")
    ch = set(res["choice"].values())
    res["robust"] = len(ch) == 1
    res["chosen"] = ch.pop() if res["robust"] else None
    json.dump(res, open(os.path.join(HERE, "results", "followup_selection.json"), "w"), indent=1)
    print("choice per variant:", res["choice"], "→", res["chosen"] if res["robust"] else "NOT ROBUST (to Will)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
