"""Effect of the J13 sign erratum (CS08_ERRATUM.md §4) on Stage 2's windowed quantities. In the two-pair geometry
(x₁,₂ = ∓d₁/2, x₃,₄ = r ∓ d₂/2) the correction is Δρ₄ = (2/ℓ⁴)·Σ over the 8 J13 terms of S13 (corrected sign), and every
S13 summand carries an r-phase p^{±i(2 + k₁ + k₂)r_t}, k ≥ 0 (expand z_p(1 + x) = Σ_k p^{−k(1+x)}): no constant part,
lowest frequency 2·log 2·2π/ℓ per unit spacing. So Δρ₄ has Bohr mean 0, and against Stage 2's Gaussian windows
exp(−πr²/2b²) (b ≥ 100) it integrates to ≲ √2·b·sup|Δρ₄|·exp(−ω²b²/2π), ω ≥ 0.39 (ℓ ≤ 22.1): ≈ e^{−240}.

Numerical check of both claims at the Stage 2 heights, d₁ = d₂ = 0.5 (the bump's centre) and two off-centre pairs,
r ∈ [0, 2000] on Δr = 0.05, primes ≤ 10⁴ (summands ~ log⁴p/p³; the tail beyond 10⁴ is < 1e-9 of the sum):
  mean over r ∈ [100, 2000] against the RMS (must be ≤ 1e-2 of the RMS: an almost-periodic sum's running mean),
  I(b) = ∫ exp(−πr²/2b²) Δρ₄ dr for b = 100 (must be ≤ 1e-12 absolute; v_B(100) ≈ 0.075).

  python check_s13_stage2.py  →  results/check_s13_stage2.json
"""
import json
import math
import os

import numpy as np

import cs4fast as F
import cs4lib as C

HERE = os.path.dirname(os.path.abspath(__file__))


def delta_rho4(Z, d1, d2, r):
    s = 2 * math.pi / Z.ell
    xs = [np.full(r.shape, -d1 / 2 * s), np.full(r.shape, d1 / 2 * s), (r - d2 / 2) * s, (r + d2 / 2) * s]
    tot = np.zeros(r.shape, complex)
    for P, M in C.index_terms(4):
        if sorted((len(P), len(M))) != [1, 3]:
            continue
        A = [F.mk(+1, p, xs[p]) for p in P]
        B = [F.mk(-1, m, xs[m]) for m in M]
        if len(A) > len(B):
            A, B = B, A
        tot += 2 * Z.S13(A[0].v, *[b.v for b in B])
    return tot / Z.ell ** 4


def main():
    r = np.arange(0, 2000, 0.05) + 0.025
    out = dict(rows=[])
    for ell in (15.7502, 17.2491, 21.75):
        Z = F.FastZeta(2 * math.pi * math.exp(ell), pmax=10_000)
        for d1, d2 in ((0.5, 0.5), (0.2, 0.9), (1.2, 0.4)):
            D = delta_rho4(Z, d1, d2, r)
            far = r >= 100
            rms = float(np.sqrt(np.mean(np.abs(D[far]) ** 2)))
            mean = float(abs(np.mean(D[far])))
            I100 = float(abs(2 * np.sum(np.exp(-np.pi * r ** 2 / (2 * 100.0 ** 2)) * D) * 0.05))
            row = dict(ell=ell, d1=d1, d2=d2, sup=float(np.max(np.abs(D))), rms_far=rms, mean_far=mean,
                       max_imag=float(np.max(np.abs(D.imag))), I_b100=I100,
                       PASS=bool(mean <= 1e-2 * rms and I100 <= 1e-12))
            out["rows"].append(row)
            print(row, flush=True)
    out["PASS"] = all(x["PASS"] for x in out["rows"])
    print("S13 erratum, Stage 2 windowed quantities unaffected:", "PASS" if out["PASS"] else "FAIL")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "check_s13_stage2.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
