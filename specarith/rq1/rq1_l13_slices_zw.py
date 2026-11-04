# SPDX-License-Identifier: AGPL-3.0-or-later
"""L13 slices for ℤ[ω] (Will, 2026-11-03; descriptive, new run, no relabelling).

Brief (verbatim): "Tonight: slices for ℤ[ω], same method as 4ed68e0f, β 0.40–0.60. Commit the cost first. P4's
ordering needs it."

Method: exactly rq1_l13_slices.py (55fe5b23, run as 4ed68e0f); its functions are imported unchanged.
- Data: the pinned 10¹² ℤ[ω] archive (`/mnt/data/rq1/archive_1e12_zw`), rows read only below RQ1-c's 10¹¹ matched n,
  i.e. the already-read range (the RQ1-c read's 10¹¹ ℤ[ω] cell used rows [0, n(10¹¹))). Segment sha256 checked on
  load; the manifest's sha256 is checked against `rq1c_read_pins.sha256`.
- Slices: n_s = rq1_read.n_below(zs2, 10¹⁰) (the same 227,524,967 rows as 4ed68e0f), J = ⌊n_below(zs2, 10¹¹)/n_s⌋ = 9,
  S_j = ℤ[ω] rows [j·n_s, (j + 1)·n_s): the same row ranges as the ℤ[√2] / ℤ[i] slices (RQ1's matched-N convention).
- β ∈ {0.40, 0.45, 0.55, 0.60}, K = round(N^β), N = 2n_s: the same K as 4ed68e0f (2,906 / 7,873 / 57,801 / 156,616).
- Per slice R_j = var_stream(full_sorted(θ_ω over S_j), K)/(N/K); θ_ω = rq1_zw.thetas_zw (the RQ1-c read's map).
- **Guard:** S_0 is RQ1-c's 10¹⁰ ℤ[ω] set, so R_0 at β 0.40 / 0.45 / 0.55 must equal the RQ1-c read's P4 cells
  (`results/rq1c_read_void/read1.json`, P4 cells at 10¹⁰) bit for bit, else stop. (β 0.60 at 10¹⁰ was not read for ℤ[ω].)
- σ̂² = Σd²/(6(J − 2)) from the second differences, 90% interval from the exact i.i.d.-normal null (200,000 draws, seed
  20261103), model/empirical against model_rel(K) = √(2/(cK)), c = C_SE, reading below / consistent / above: all as
  4ed68e0f (rq1_l13_slices.summarise).
- Also reported, descriptive: the same table for ℤ[√2] and ℤ[i] copied from `results/l13/L13_SLICES.json` (not
  recomputed), so the three fields sit side by side at β 0.55, P4's cell.

Cost model (rq1_l13_slices.py's, one field): load + sort + 4 passes per slice,
9 × (m_load(N) + 0.5·m_load(N) + 4·m_pass(N)) ≈ 0.22 core-h; the two-field run measured 0.87× its model.
**≈ 0.25 core-h** with ℤ[ω]'s heavier angle map (atan2 of a 3-term form). Stop rule 1.25× (rq1_l13.Cost, as 4ed68e0f).
Queue: spot pueue `specarith-scored` (label specarith:rq1-l13-slices-zw).

  python rq1_l13_slices_zw.py run ZS2_DIR ZW_DIR OUT_JSON
"""
import hashlib, json, os, sys

import numpy as np

import rq1_read as Q
import rq1_zw as Z
import rq1_l13 as L
import rq1_l13_slices as S

HERE = os.path.dirname(os.path.abspath(__file__))


def load_rows_zw(d, lo, hi):
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
        uv = np.load(path)[max(lo - pos, 0): min(hi - pos, r)]
        out.append(Z.thetas_zw(uv))
        pos += r
    t = np.concatenate(out)
    assert len(t) == hi - lo
    return t


def check_manifest_pin(d):
    mp = os.path.join(d, "MANIFEST.json")
    h = hashlib.sha256(open(mp, "rb").read()).hexdigest()
    pins = open(os.path.join(HERE, "rq1c_read_pins.sha256")).read()
    assert h in pins, ("zw manifest not pinned", h)


def run(zs2, zw, out):
    side = out + ".cost"
    check_manifest_pin(zw)
    rc = json.load(open(os.path.join(HERE, "results/rq1c_read_void/read1.json")))
    sealed = rc["P4"]["cells"]["1e+10"]
    n_s = Q.n_below(zs2, 10 ** 10)
    J = Q.n_below(zs2, 10 ** 11) // n_s
    N = 2 * n_s
    Ks = [int(round(N ** b)) for b in S.BETAS]
    q05, q95 = S.null_quantiles(J)
    cost = L.Cost()
    Rs = {b: [] for b in S.BETAS}
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(S.NT) as pool:
        for j in range(J):
            th = L.full_sorted(load_rows_zw(zw, j * n_s, (j + 1) * n_s))
            rr = list(pool.map(lambda K: Q.var_stream(th, K) / (N / K), Ks))
            del th
            if j == 0:
                for b, K, r in zip(S.BETAS, Ks, rr):
                    if str(b) in sealed:
                        assert sealed[str(b)]["K"] == K and sealed[str(b)]["R_zw"] == r, ("slice 0 differs", b)
            for b, r in zip(S.BETAS, rr):
                Rs[b].append(r)
            cost.add(f"zw slice {j}", L.m_load(N) + 0.5 * L.m_load(N) + 4 * L.m_pass(N), side)
    prev = json.load(open(os.path.join(HERE, "results/l13/L13_SLICES.json")))
    res = dict(label="L13 slices, Z[omega] (descriptive; method 4ed68e0f / rq1_l13_slices.py)",
               n_slice=n_s, J=J, N=N, betas=S.BETAS, C_SE=Q.C_SE, null_q=[q05, q95],
               fields={"zw": {str(b): S.summarise(Rs[b], K, q05, q95) for b, K in zip(S.BETAS, Ks)}},
               copied_from_L13_SLICES={f: prev["fields"][f] for f in ("zs2", "zi")})
    assert prev["n_slice"] == n_s and prev["J"] == J
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    for b, s in res["fields"]["zw"].items():
        print("zw", b, "K", s["K"], "model/emp %.3f [%.3f, %.3f] %s" % (s["model_over_emp"], *s["model_over_emp_ci90"],
              s["classification"]), "curv z %.2f" % s["curvature_check"]["z"], flush=True)
    print("done")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3], sys.argv[4])
