"""Follow-up candidate (B), FOLLOWUP_SELECTION_RULE.md (round 48): the third cumulant of the counting function. Data-free.

For unit-density zeros the count N in a window of length L has
    κ₃(L) = L + 3·F₂(L) + F₃(L),  F₂ = 2∫₀ᴸ (L − u)(ρ₂(u) − 1) du,
    F₃ = 6 ∫∫_{u, v ≥ 0, u + v ≤ L} (L − u − v) κ₃^c(0, u, u + v) du dv,
κ₃^c(0, a, b) = ρ₃(0, a, b) − ρ₂(a) − ρ₂(b) − ρ₂(b − a) + 2 (the connected three-point function; factorial-cumulant
terms). Only ρ₁–ρ₃ enter, so there is no truncation and ∂κ₃/∂μ₄ = 0 identically. With Δ = CS − sine at the file's
zero-weighted mean height (FastZeta, primes ≤ 3·10⁵, as the prediction's T₂/T₃):
    Δκ₃ = 3·ΔF₂ + ΔF₃,   ∂κ₃/∂μ₃ = ΔF₃ (μ₃ scales κ₃^c's arithmetic part only; exact, linear),
    per-file amplitude μ̂_B = (k₃ − κ₃^sine)/Δκ₃, so ∂μ*_B/∂μ₃ = ΔF₃/Δκ₃,
and ΔF₃/Δκ₃ is also the round-46 split (the share of the arithmetic part from connected n ≥ 3 terms).
Quadrature: Gauss–Legendre, the triangle collapsed to the square (u = L·a, v = L(1 − a)·b), order M and M + 16 (the
difference is reported as the quadrature error); F₂ at order 96.

  python followup_k3.py run CHUNK NCHUNKS OUT_DIR       (spot)
  python followup_k3.py merge OUT_DIR                   → results/followup_k3.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cs4fast as F  # noqa: E402
import route_a_zeta as RZ  # noqa: E402

LS = tuple(float(v) for v in os.environ.get("K3_LS", "0.5,1.0,1.5,2.0,3.0").split(","))   # round 57: K3_LS=4.0,5.0,6.0
OUT_JSON = "followup_k3.json" if "K3_LS" not in os.environ else "followup_k3_r57.json"
MS = (32, 48)


def gl(m, a, b):
    x, w = np.polynomial.legendre.leggauss(m)
    return 0.5 * (b - a) * x + 0.5 * (b + a), 0.5 * (b - a) * w


def terms(Z, L, m):
    """(ΔF₂, ΔF₃, F₂^sine, F₃^sine) at window length L, triangle order m."""
    u, wu = gl(96, 0.0, L)
    r2z = np.real(RZ.rho(Z, [np.zeros_like(u), u]))
    r2s = RZ.sine_rho([np.zeros_like(u), u])
    f2z, f2s = 2 * np.sum(wu * (L - u) * (r2z - 1)), 2 * np.sum(wu * (L - u) * (r2s - 1))
    a, wa = gl(m, 0.0, 1.0)
    b, wb = gl(m, 0.0, 1.0)
    A, B = np.meshgrid(a, b, indexing="ij")
    W = np.outer(wa, wb) * L * L * (1 - A)                     # Jacobian of (a, b) → (u, v)
    U, V = (L * A).ravel(), (L * (1 - A) * B).ravel()
    W = W.ravel()
    z0 = np.zeros_like(U)

    def kc(rho):
        return rho([z0, U, U + V]) - rho([z0, U]) - rho([z0, U + V]) - rho([z0, V]) + 2

    kz = kc(lambda xs: np.real(RZ.rho(Z, xs)))
    ks = kc(RZ.sine_rho)
    f3z, f3s = 6 * np.sum(W * (L - U - V) * kz), 6 * np.sum(W * (L - U - V) * ks)
    return dict(dF2=float(f2z - f2s), dF3=float(f3z - f3s), F2_sine=float(f2s), F3_sine=float(f3s))


def jobs():
    return [(f, L, m) for f in RZ.F3 for L in LS for m in MS]


def run(chunk, nchunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"k3_c{chunk:02d}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["file"], r["L"], r["m"]) for r in map(json.loads, open(path))}
    for i, (f, L, m) in enumerate(jobs()):
        if i % nchunks != chunk or (f, L, m) in done:
            continue
        Z = F.FastZeta(RZ.height(f, "mean"), pmax=RZ.PMAX_MAIN)
        r = dict(file=f, L=L, m=m, **terms(Z, L, m))
        with open(path, "a") as fh:
            fh.write(json.dumps(r) + "\n")
        print(json.dumps(r), flush=True)


def merge(out_dir):
    rows = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("k3_c") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows.setdefault((r["file"], r["L"], r["m"]), r)
    missing = set(jobs()) - set(rows)
    if missing:
        raise SystemExit(f"merge: {len(missing)} jobs missing")
    res = dict(round="forty-eighth", candidate="B", definition=__doc__.split("\n\n")[0], files={})
    hi, lo = MS[1], MS[0]
    for f in RZ.F3:
        res["files"][f] = {}
        for L in LS:
            r, q = rows[(f, L, hi)], rows[(f, L, lo)]
            dk = 3 * r["dF2"] + r["dF3"]
            res["files"][f][str(L)] = dict(
                dF2=r["dF2"], dF3=r["dF3"], dkappa3=dk, kappa3_sine=L + 3 * r["F2_sine"] + r["F3_sine"],
                dmuB_dmu3=r["dF3"] / dk, connected_share=r["dF3"] / dk,
                quad_err_dF3=abs(r["dF3"] - q["dF3"]), quad_err_F3_sine=abs(r["F3_sine"] - q["F3_sine"]))
            print(f"{f} L {L}: Δκ₃ {dk:+.4e} (3ΔF₂ {3 * r['dF2']:+.4e}, ΔF₃ {r['dF3']:+.4e}); ∂μ*_B/∂μ₃ = connected share "
                  f"{r['dF3'] / dk:+.4f}; κ₃^sine {L + 3 * r['F2_sine'] + r['F3_sine']:.5f}; quad err ΔF₃ "
                  f"{abs(r['dF3'] - q['dF3']):.1e}", flush=True)
    json.dump(res, open(os.path.join(HERE, "results", OUT_JSON), "w"), indent=1)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "merge":
        sys.exit(merge(sys.argv[2]))
