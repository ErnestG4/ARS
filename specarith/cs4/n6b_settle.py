"""Round 80 settling test (POST-HOC; the original G-b3 FAIL stays as sealed): G-b3 re-read under corrected (B)'s own
kernel instead of the two-period triangular average (l6/N6_CLOSEOUT.md §3; declared before computing).

Kernel (derived from b2_est.py). Window starts are u_q + jL with u_q = qL/NU (q < NU = 32, L* = 4), so every start lies
on the grid kΔ, Δ = L/NU = 1/8; a window belongs to the segment holding its start (start // G); each offset puts
exactly G/L windows in a segment. Linearised, k̄₃ − κ₃ = (1/NU) Σ_q (1/n_q) Σ_j ψ(d_qj), so a segment's mean of ψ has
variance (1/M²) Σ_{i,i'} C(x_i − x_i'), M = NU·G/L = G/Δ, and W(G) = G·Var = Δ Σ_k c_k C(kΔ) with c_k the lag counts
of the enumerated starts divided by M. `kernel` builds c_k by enumerating the starts and checks it against the closed
Bartlett form (1 − |k|/M); the known answer applies it to stage (a)'s exact U(N) C(kΔ) (l6/results/n6a, C_*.npz) and
must reproduce stage (a)'s W_B(G) to 1e-9 relative at G = 300, 1,000, 3,000 and 10,000, or the test is void.

Point evaluation. The kernel is global (r ∈ [0, G)). A point value is one member of an exact partition of it:
τ(x) = cos²(π/2·β(|x|/h)), β the smootherstep 6t⁵ − 15t⁴ + 10t³, h = 5, satisfies Σ_j τ(r − jh) = 1, so
W = Σ_j [Δ Σ_k c_k τ(kΔ − jh) C(kΔ)] exactly. At r₀ the local kernel is w(r) = c(r)·τ(r − r₀) on r = r₀ + kΔ,
|k| < 40 (79 points), normalised to Σw = 1; c is taken at G = 10,000 (the slope over ±5 changes w by ≤ 5·10⁻⁴).
Its transfer at 1.04 cycles per unit is ≤ 5.4·10⁻⁵ (G-b3's two-period average: ~10⁻²); at 0.02 it is 0.980.

Quantity (G-b3's, unchanged): the (3, 3) piece at ζ PMAX 10³, ℓ = 15.75, 4 in-window nodes (distinct-node rule, valid
here: the integrand vanishes at in-cluster coincidence), brute = Σ_k classes (ρ₆ − ρ₃ρ₃), extraction = class 0 − ρ₃ρ₃,
both under w. Points r₀ = 100 and 300. Tolerance (G-b3's original): |brute − extraction| ≤ 0.01·|brute|.

Witnesses (in `summary`, on the real per-point values):
- tone: A_t·e^{±2πi·1.04(r − r₀)} added to classes ±1, A_t = 16 (the largest measured class-1 amplitude, close-out
  §3.2); predicted change of brute − extraction 2A_t·T(1.04); measured must match within 1%, and must stay ≤ 10% of the
  tolerance (a near-carrier leak cannot decide the reading);
- slow: A_s·cos(2π·0.02(r − r₀)) added to classes ±1 (half each), |A_s| = 3 × tolerance with the sign of the measured
  gap (so the plant cannot cancel it); predicted change A_s·T(0.02);
  measured must match within 1%, and the planted reading must FAIL (the test can see slow content).
WITNESS_OK iff all four hold at both points. PASS iff WITNESS_OK, the known answer holds, and both points are within
tolerance; FAIL iff WITNESS_OK and either point is outside it (the slow-content share (brute − extraction)/brute is
reported at each point); otherwise VOID.

  python n6b_settle.py kernel C_DIR OUT_DIR      → OUT_DIR/KERNEL.json (known answer)
  python n6b_settle.py jobs                      the declared task list
  python n6b_settle.py task R0 K OUT_DIR         one point r₀ + KΔ → OUT_DIR/s_*.json
  python n6b_settle.py summary OUT_DIR           → OUT_DIR/SETTLE.json
"""
import glob
import json
import math
import os
import sys
import time

import numpy as np

import n6b_extract as E

L, NU = 4.0, 32
DELTA = L / NU
GS = (300, 1000, 3000, 10000)
W_STAGE_A = {300: 0.21119077178567092, 1000: 0.2111170342651325, 3000: 0.2110959159432208, 10000: 0.21108850739246948}
ELL, PMAX, NQ = 15.75, 1000, 4
R0S = (100.0, 300.0)
H, G_LOCAL = 5.0, 10000
KH = int(round(H / DELTA)) - 1                     # 39: τ vanishes at |k| = 40
TOL = 0.01
F_TONE, A_TONE, F_SLOW = 1.04, 16.0, 0.02


def lag_counts(G):
    """c_k for k ≥ 0, from the estimator's window starts in one segment: offsets u_q = qL/NU, starts u_q + jL,
    segment = start // G (b2_est.Acc.add_block); the starts are integers in units of Δ."""
    starts = []
    s0 = 7 * G                                   # an interior segment; any segment gives the same starts mod G
    for q in range(NU):
        u = q * L / NU
        j = np.arange(math.ceil((s0 - u) / L), math.floor((s0 + G - u) / L) + 1)
        st = u + L * j
        st = st[(st // G) == s0 // G]
        starts.append(np.rint(st / DELTA).astype(np.int64))
    st = np.sort(np.concatenate(starts))
    M = len(st)
    occ = np.zeros(st[-1] - st[0] + 1)
    np.add.at(occ, st - st[0], 1.0)
    n = 1 << int(np.ceil(np.log2(2 * len(occ))))
    ac = np.rint(np.fft.irfft(np.abs(np.fft.rfft(occ, n)) ** 2, n)[:len(occ)])   # pair counts by lag (exact integers)
    cnt = np.concatenate([[ac[0]], 2 * ac[1:]])                                  # both signs of a nonzero lag
    return np.pad(cnt, (0, max(0, M - len(cnt))))[:M] / M, M


def kernel(c_dir, out_dir):
    k = np.concatenate([np.load(f)["k"] for f in sorted(glob.glob(os.path.join(c_dir, "C_*.npz")))])
    C = np.concatenate([np.load(f)["C"] for f in sorted(glob.glob(os.path.join(c_dir, "C_*.npz")))])
    o = np.argsort(k)
    k, C = k[o], C[o]
    assert np.array_equal(k, np.arange(len(k))), "missing C(kΔ) points"
    res = dict(label="round 80 settling test: kernel derived from b2_est and the stage (a) known answer", G={})
    ok = True
    for G in GS:
        c, M = lag_counts(G)
        assert M == round(G / DELTA), (G, M)
        kk = np.arange(M)
        bart = np.where(kk == 0, 1.0, 2.0 * (1 - kk / M))
        W = float(DELTA * np.sum(c * C[:M]))
        rel = abs(W / W_STAGE_A[G] - 1)
        res["G"][str(G)] = dict(M=M, max_dev_from_bartlett=float(np.max(np.abs(c - bart))), W_kernel=W,
                                W_stage_a=W_STAGE_A[G], rel=rel, ok=bool(rel <= 1e-9))
        ok &= rel <= 1e-9
        print(G, M, f"W {W:.12f}  stage (a) {W_STAGE_A[G]:.12f}  rel {rel:.1e}")
    res["KNOWN_ANSWER_OK"] = bool(ok)
    json.dump(res, open(os.path.join(out_dir, "KERNEL.json"), "w"), indent=1)
    return 0


def _beta(t):
    t = np.clip(t, 0.0, 1.0)
    return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3


def local_weights(r0):
    kk = np.arange(-KH, KH + 1)
    r = r0 + kk * DELTA
    w = (1 - r / G_LOCAL) * np.cos(np.pi / 2 * _beta(np.abs(kk * DELTA) / H)) ** 2
    return kk, r, w / w.sum()


def transfer(r0, f):
    kk, r, w = local_weights(r0)
    return float(np.sum(w * np.cos(2 * np.pi * f * (r - r0))))


def jobs():
    return [(r0, k) for r0 in R0S for k in range(-KH, KH + 1)]


def task(r0, k, out_dir):
    path = os.path.join(out_dir, f"s_{r0}_{k:+03d}.json")
    if os.path.exists(path):
        return 0
    r = r0 + k * DELTA
    XA, WA = E._tuples(NQ, 3)
    PA, PB = np.repeat(XA, len(XA), 0), np.tile(XA, (len(XA), 1))
    W = np.repeat(WA, len(XA)) * np.tile(WA, len(XA))
    M = E.FilteredModel("zeta", ELL, pmax=PMAX)
    ds = [PA[:, j] for j in range(3)] + [PB[:, j] + r for j in range(3)]
    from ratios_t6 import guard
    guard(ds)
    t = time.time()
    cls = M.rho_cls(ds, {3, 4, 5})
    prod = np.real(M.rho([PA[:, j] for j in range(3)]) * M.rho([PB[:, j] for j in range(3)]))
    g = {str(c): [float(np.sum(W * np.real(v))), float(np.sum(W * np.imag(v)))] for c, v in cls.items()}
    g["0"][0] -= float(np.sum(W * prod))
    rec = dict(r0=r0, k=k, r=r, g=g, wall_s=round(time.time() - t, 1))
    tmp = f"{path}.{os.getpid()}.part"                # per-process temp name: concurrent duplicates cannot interleave
    json.dump(rec, open(tmp, "w"))
    os.replace(tmp, path)
    print(r0, k, rec["wall_s"], flush=True)
    return 0


def _read(r0, cls_vals):
    """brute and extraction under the local kernel from per-point class values {class: complex array over k}."""
    kk, r, w = local_weights(r0)
    brute = float(np.real(np.sum(w * sum(cls_vals.values()))))
    ext = float(np.real(np.sum(w * cls_vals["0"])))
    return brute, ext


def summary(out_dir):
    kern = json.load(open(os.path.join(out_dir, "KERNEL.json")))
    res = dict(label="round 80 settling test (POST-HOC): G-b3 under corrected (B)'s kernel", points={},
               KNOWN_ANSWER_OK=kern["KNOWN_ANSWER_OK"])
    wit_ok, inside = True, True
    for r0 in R0S:
        kk, r, w = local_weights(r0)
        recs = [json.load(open(os.path.join(out_dir, f"s_{r0}_{k:+03d}.json"))) for k in kk]
        cl = {c: np.array([complex(*d["g"][c]) for d in recs]) for c in recs[0]["g"]}
        brute, ext = _read(r0, cl)
        tol = TOL * abs(brute)
        diff = brute - ext
        # witnesses
        x = r - r0
        tone = A_TONE * np.exp(2j * np.pi * F_TONE * x)
        clt = dict(cl, **{"1": cl["1"] + tone, "-1": cl["-1"] + np.conj(tone)})
        bt, et = _read(r0, clt)
        d_tone, p_tone = (bt - et) - diff, 2 * A_TONE * transfer(r0, F_TONE)
        a_s = 3 * tol * (1.0 if diff >= 0 else -1.0)            # same sign as the gap, so the plant cannot cancel it
        slow = 0.5 * a_s * np.cos(2 * np.pi * F_SLOW * x)
        cls_ = dict(cl, **{"1": cl["1"] + slow, "-1": cl["-1"] + slow})
        bs, es = _read(r0, cls_)
        d_slow, p_slow = (bs - es) - diff, a_s * transfer(r0, F_SLOW)
        wt = dict(predicted=p_tone, measured=d_tone, match=bool(abs(d_tone - p_tone) <= 0.01 * abs(p_tone) + 1e-15),
                  below_tenth_tol=bool(abs(d_tone) <= 0.1 * tol), T=transfer(r0, F_TONE), A=A_TONE, f=F_TONE)
        ws = dict(predicted=p_slow, measured=d_slow, match=bool(abs(d_slow - p_slow) <= 0.01 * abs(p_slow)),
                  planted_fails=bool(abs(bs - es) > TOL * abs(bs)), T=transfer(r0, F_SLOW), A=a_s, f=F_SLOW)
        wit_ok &= wt["match"] and wt["below_tenth_tol"] and ws["match"] and ws["planted_fails"]
        ok = abs(diff) <= tol
        inside &= ok
        res["points"][str(r0)] = dict(brute=brute, extraction=ext, diff=diff, tol=tol, within=bool(ok),
                                      slow_share=diff / brute, witness_tone=wt, witness_slow=ws,
                                      per_class={c: [complex(np.sum(w * v)).real, complex(np.sum(w * v)).imag]
                                                 for c, v in cl.items()})
        print(f"r0={r0}: brute {brute:+.6f} ext {ext:+.6f} diff {diff:+.3e} tol {tol:.3e} within {ok} "
              f"share {diff / brute:+.4f} | tone {d_tone:.3e}/{p_tone:.3e} slow {d_slow:.3e}/{p_slow:.3e}")
    res["WITNESS_OK"] = bool(wit_ok)
    valid = res["WITNESS_OK"] and res["KNOWN_ANSWER_OK"]
    res["READING"] = ("PASS" if inside else "FAIL") if valid else "VOID"
    print("READING", res["READING"])
    json.dump(res, open(os.path.join(out_dir, "SETTLE.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "kernel":
        sys.exit(kernel(sys.argv[2], sys.argv[3]))
    if sys.argv[1] == "jobs":
        for j in jobs():
            print(*j)
        sys.exit(0)
    if sys.argv[1] == "task":
        sys.exit(task(float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]))
    if sys.argv[1] == "summary":
        sys.exit(summary(sys.argv[2]))
