# SPDX-License-Identifier: AGPL-3.0-or-later
"""L13 slices (Will, 2026-11-03; descriptive, new run, no relabelling of RQ1 or RQ1-c).

Brief (verbatim): "For ℤ[√2] and ℤ[i], take consecutive disjoint slices at matched N and form second differences
R₁ − 2R₂ + R₃ to cancel linear drift. Commit the method and the cost first. Run it after ARSv2's first wave has its
cores."

Why: L13's two empirical SEs (block arcs, residue-class subsets) disagreed at all 16 cells, and its report named a
matched disjoint-X-range method as what would settle it. FN1's L16 found that differencing two disjoint slices cancels
the drift along prime order, giving noise consistent with the SE model there. This applies the same idea to RQ1's two
fields, with second differences, so a linear drift in prime order cancels exactly.

Method (committed before running):
- Data: the pinned 10¹² archives (`/mnt/data/rq1/archive_1e12_zs2`, `..._zi`), rows read only below the 10¹¹ boundary,
  i.e. the already-read range. Segment sha256 is checked on load, as in rq1_l13.load_half.
- Slices: n_s = rq1_read.n_below(zs2, 10¹⁰) (RQ1's matched n at 10¹⁰), J = ⌊n_below(zs2, 10¹¹) / n_s⌋ slices
  S_j = rows [j·n_s, (j + 1)·n_s), j = 0 … J − 1. That is 9 if the archive counts are as expected. The same row ranges
  are used for both fields (RQ1's matched-N convention).
- Per slice and β ∈ {0.40, 0.45, 0.55, 0.60} (L13's cells): N = 2n_s, K = round(N^β),
  R_j = var_stream(full_sorted(θ over S_j), K)/(N/K).
  - Guard: S_0 is RQ1's 10¹⁰ set, so R_0 must equal the sealed read's R (results/read/read1.json) bit for bit, else
    stop.
- Second differences d_t = R_t − 2R_{t+1} + R_{t+2}, t = 0 … J − 3. Under R_j = a + b·j + ε_j with independent ε of
  SD σ: E d = 0 and Var d = 6σ².
  - **Primary:** σ̂² = Σ_t d_t² / (6(J − 2)), unbiased under that model even though consecutive d overlap.
  - **90% interval:** from the exact null distribution of the quadratic form Σd²/(6(J − 2)σ²) for i.i.d. normal ε,
    by 200,000 seeded draws (seed 20261103).
  - Relative: σ̂_rel = σ̂ / mean_j R_j.
- **Comparison with the sealed SE model:** model_rel(K) = √(2/(cK)), c = C_SE (the same model as L13). Reported as
  model/empirical (L13's orientation) and empirical/model (L16's).
- **Reading, as in L13** (declared): "below" (noise below the model) if the 90% interval of model/empirical lies above
  1; "above" if below 1; else "consistent". Set beside L13's methods A and B at the 10¹⁰ cells (the slices' N is the
  10¹⁰ N). Descriptive only.
- **Also reported (descriptive):**
  - mean(d) / its null SE, a curvature check: a quadratic drift leaves a constant 2c in d and inflates σ̂;
  - the curvature-corrected σ̂_c² = Σ(d − d̄)² / (6(J − 3)) (approximate);
  - the three disjoint triples (0,1,2), (3,4,5), (6,7,8) alone (independent d, 3 df);
  - per-slice R and the drift slope.
- **No relabelling** of RQ1, RQ1-c or L13's table.

Cost model (rq1_l13's constants, spot core-s):
- load: m_load(2·n_used) per field;
- per slice: sort ≈ 0.5·m_load(N) and 4 passes of m_pass(N).
- With n_s ≈ 2.28·10⁸ and J = 9, that is ≈ 204 s + 9 × (11 + 67) s ≈ 0.25 core-h per field, **≈ 0.5 core-h in total**.
- Stop rule: 1.25× the model after any stage, armed once the modelled work is ≥ 60 s (as L13).

  python rq1_l13_slices.py selftest              synthetic: σ̂ recovers σ with and without a linear drift
  python rq1_l13_slices.py run ZS2_DIR ZI_DIR OUT_JSON
"""
import hashlib, json, math, os, sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

import rq1_read as Q
import rq1_angles as RA
import rq1_l13 as L

HERE = os.path.dirname(os.path.abspath(__file__))
BETAS = [0.40, 0.45, 0.55, 0.60]
NT = int(os.environ.get("READ_THREADS", "8"))
SEED = 20261103


def load_rows(d, field, lo, hi):
    """θ ∈ [0, ½] for archive rows [lo, hi) (segment sha256 checked)."""
    man = json.load(open(os.path.join(d, "MANIFEST.json")))
    out, pos = [], 0
    for s in man["segments"]:
        r = s["rows"]
        if pos + r <= lo:
            pos += r
            continue
        if pos >= hi:
            break
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        ab = np.load(path)[max(lo - pos, 0): min(hi - pos, r)]
        out.append(RA.thetas_from_ab(ab)[0] if field == "zs2" else Q.field_thetas(ab, field))
        pos += r
    t = np.concatenate(out)
    assert len(t) == hi - lo
    return t


def null_quantiles(J, draws=200_000, seed=SEED):
    e = np.random.default_rng(seed).standard_normal((draws, J))
    d = e[:, :-2] - 2 * e[:, 1:-1] + e[:, 2:]
    q = (d ** 2).sum(1) / (6 * (J - 2))
    return float(np.quantile(q, 0.05)), float(np.quantile(q, 0.95))


def summarise(R, K, q05, q95):
    R = np.asarray(R); J = len(R)
    d = R[:-2] - 2 * R[1:-1] + R[2:]
    s2 = float((d ** 2).sum() / (6 * (J - 2)))
    s = math.sqrt(s2); m = float(R.mean()); rel = s / m
    lo_s, hi_s = s / math.sqrt(q95), s / math.sqrt(q05)            # 90% interval for σ
    mr = L.model_rel(K)
    ratio = mr / rel
    ci = [mr / (hi_s / m), mr / (lo_s / m)]
    cls = "below" if ci[0] > 1 else ("above" if ci[1] < 1 else "consistent")
    trip = [float(R[i] - 2 * R[i + 1] + R[i + 2]) for i in range(0, J - 2, 3)]
    sc2 = float(((d - d.mean()) ** 2).sum() / (6 * (J - 3))) if J > 3 else None
    se_dbar = math.sqrt(6 * s2) / math.sqrt(len(d))
    return dict(K=K, R=R.tolist(), d=d.tolist(), sigma=s, sigma_rel=rel, model_rel=mr,
                model_over_emp=ratio, model_over_emp_ci90=ci, emp_over_model=1 / ratio, classification=cls,
                drift_slope_per_slice=float(np.polyfit(np.arange(J), R, 1)[0]),
                curvature_check=dict(mean_d=float(d.mean()), z=float(d.mean() / se_dbar)),
                sigma_rel_curv_corrected=(math.sqrt(sc2) / m if sc2 is not None else None),
                disjoint_triples=dict(d=trip, sigma_rel=math.sqrt(sum(x * x for x in trip) / (6 * len(trip))) / m))


def selftest():
    rng = np.random.default_rng(7)
    J = 9; q05, q95 = null_quantiles(J, 50_000)
    for drift in (0.0, -0.01):
        est = []
        for _ in range(4000):
            R = 0.8 + drift * np.arange(J) + 0.005 * rng.standard_normal(J)
            d = R[:-2] - 2 * R[1:-1] + R[2:]
            est.append((d ** 2).sum() / (6 * (J - 2)))
        print(f"drift {drift}: mean σ̂²/σ² = {np.mean(est) / 0.005 ** 2:.3f} (expect 1.000); null q05 {q05:.3f} q95 {q95:.3f}")
    print("selftest done")


def run(zs2, zi, out):
    side = out + ".cost"
    read1 = json.load(open(os.path.join(HERE, "results/read/read1.json")))
    sealed = {r["beta"]: r for r in read1["rows"][str(10 ** 10)]["rows"]}
    n_s = Q.n_below(zs2, 10 ** 10)
    J = Q.n_below(zs2, 10 ** 11) // n_s
    N = 2 * n_s
    Ks = [int(round(N ** b)) for b in BETAS]
    q05, q95 = null_quantiles(J)
    cost = L.Cost()
    res = dict(label="L13 slices: second differences of R over consecutive disjoint slices at matched N (descriptive)",
               n_slice=n_s, J=J, N=N, betas=BETAS, C_SE=Q.C_SE, null_q=[q05, q95], fields={})
    with ThreadPoolExecutor(NT) as pool:
        for f, d in (("zs2", zs2), ("zi", zi)):
            Rs = {b: [] for b in BETAS}
            for j in range(J):
                th = L.full_sorted(load_rows(d, f, j * n_s, (j + 1) * n_s))
                rr = list(pool.map(lambda K: Q.var_stream(th, K) / (N / K), Ks))
                del th
                if j == 0:
                    key = "R_zs2" if f == "zs2" else "R_zi"
                    for b, K, r in zip(BETAS, Ks, rr):
                        assert sealed[b]["K"] == K and sealed[b][key] == r, ("slice 0 differs from the sealed read", f, b)
                for b, r in zip(BETAS, rr):
                    Rs[b].append(r)
                cost.add(f"{f} slice {j}", L.m_load(N) + 0.5 * L.m_load(N) + 4 * L.m_pass(N), side)
            res["fields"][f] = {str(b): summarise(Rs[b], K, q05, q95) for b, K in zip(BETAS, Ks)}
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    for f, v in res["fields"].items():
        for b, s in v.items():
            print(f, b, "K", s["K"], "model/emp %.3f [%.3f, %.3f] %s" % (s["model_over_emp"], *s["model_over_emp_ci90"],
                  s["classification"]), "curv z %.2f" % s["curvature_check"]["z"], flush=True)
    print("done")


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        selftest()
    elif sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3], sys.argv[4])
