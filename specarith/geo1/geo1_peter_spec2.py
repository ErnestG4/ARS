"""GEO1 bridge-kit A2, rebuilt evaluator (GEO1_BRIDGE_A2_DERIVATION.md §5; Will approved one rebuild).

Frequencies a/q with q ≤ Q_EX = 10⁴ are summed one by one, with exact weights: the product of the exact DFT weights of
the CRT components a_i/p_i^k_i, where a_i = a·(q/p_i^k_i)⁻¹ mod p_i^k_i. The kernel is
K_L(θ) = sin²(πLθ)/(L² sin²(πθ)). Frequencies with q > Q_EX keep geo1_peter_spec's flat weights; the q > Q tail is as
there. The cutoff and the second witness were committed (7135d9e6) before this file was written.

  python geo1_peter_spec2.py unittest                  small exactly periodic products: spectral sum = direct, 1e-10
  python geo1_peter_spec2.py check OUT_JSON             check 1 on both planted witnesses (unchanged criterion)
  python geo1_peter_spec2.py predict PRED_JSON OUT_JSON  the zero-parameter prediction (only after check 1 passes)
"""
import json
import math
import sys

import numpy as np
from numba import njit

import geo1_peter_seal as S
import geo1_peter_spec as V1
from geo1_peter import primes_upto, trace_density

Q_EX = 10 ** 4
LS = V1.LS
WITNESSES = [dict(name="planted_997_seed20261109", pmax=997, seed=20261109),
             dict(name="planted_499_seed20261110", pmax=499, seed=20261110)]


@njit(cache=False)
def _inv(a, m):
    t, nt, r, nr = 0, 1, m, a % m
    while nr:
        qq = r // nr
        t, nt = nt, t - qq * nt
        r, nr = nr, r - qq * nr
    return t % m


@njit(cache=False)
def exact_sum(Qex, spf, Np, Bp, offs, wcat, Ls):
    nL = Ls.shape[0]
    acc = np.zeros(nL)
    mass = 0.0
    pr = np.zeros(16, np.int64)
    mm = np.zeros(16, np.int64)
    iv = np.zeros(16, np.int64)
    sc = np.zeros(16, np.int64)
    for q in range(2, Qex + 1):
        x = q
        w = 0
        ok = True
        while x > 1:
            p = spf[x]
            k = 0
            m = 1
            while x % p == 0:
                x //= p
                k += 1
                m *= p
            if k > Bp[p]:
                ok = False
                break
            pr[w] = p
            mm[w] = m
            w += 1
        if not ok:
            continue
        for i in range(w):
            iv[i] = _inv((q // mm[i]) % mm[i], mm[i])
            sc[i] = Np[pr[i]] // mm[i]
        for a in range(1, q):
            wt = 1.0
            good = True
            for i in range(w):
                ai = (a % mm[i]) * iv[i] % mm[i]
                if ai % pr[i] == 0:
                    good = False
                    break
                wt *= wcat[offs[pr[i]] + ai * sc[i]]
            if not good:
                continue
            mass += wt
            th = a / q
            s2 = math.sin(math.pi * th) ** 2
            for li in range(nL):
                L = Ls[li]
                acc[li] += wt * math.sin(math.pi * L * th) ** 2 / (float(L) * L * s2)
    return acc, mass


@njit(cache=False)
def flat_sum_from(qmin, Qmax, spf, wp, small, Ls):
    """geo1_peter_spec.spec_sum restricted to q ≥ qmin."""
    nL = Ls.shape[0]
    acc = np.zeros(nL)
    massq = 0.0
    ps = np.zeros(16, np.int64)
    for q in range(qmin, Qmax + 1):
        x = q
        W = 1.0
        phi = 1.0
        w = 0
        while x > 1:
            p = spf[x]
            k = 0
            while x % p == 0:
                x //= p
                k += 1
            if p <= 13:
                if k >= small.shape[1]:
                    W = 0.0
                    break
                W *= small[p, k]
            else:
                if k > 1:
                    W = 0.0
                    break
                W *= wp[p]
            phi *= (p - 1.0) * p ** (k - 1.0)
            ps[w] = p
            w += 1
            if W == 0.0:
                break
        if W == 0.0:
            continue
        massq += W * phi
        for li in range(nL):
            L = Ls[li]
            T = 0.0
            for mask in range(1 << w):
                d = 1
                sg = 1.0
                for j in range(w):
                    if mask >> j & 1:
                        d *= ps[j]
                        sg = -sg
                e = q // d
                m = L // e
                s = L - m * e
                T += sg * e * (s * (m + 1.0) ** 2 + (e - s) * float(m) * m) / (float(L) * L)
            acc[li] += W * T
    return acc, massq


def delta_closed(p):
    n = np.arange(p)
    return (p * p + p * S.legendre_vec(p, n * n - 4)) / (p * p - 1.0)


def exact_tables(r, mode, primes_B):
    """primes_B: [(p, B, table mod p^B)]. Returns (Np, Bp, offs, wcat): normalised |ĝ/ĝ(0)|² per frequency index."""
    top = max(p for p, _, _ in primes_B)
    Np = np.ones(top + 1, np.int64)
    Bp = np.zeros(top + 1, np.int64)
    offs = np.zeros(top + 1, np.int64)
    parts, off = [], 0
    for p, B, tab in primes_B:
        q = p ** B
        g = tab if mode == 0 else tab * np.roll(tab, -(r % q))
        G = np.fft.fft(g) / q
        parts.append(np.abs(G / G[0]) ** 2)
        Np[p], Bp[p], offs[p] = q, B, off
        off += q
    return Np, Bp, offs, np.concatenate(parts)


def model_primes(pmax):
    """[(p, B, δ table mod p^B)] for p ≤ pmax: counted tables for p ≤ 13 (BPOW), closed form above."""
    out = []
    for p in primes_upto(pmax):
        p = int(p)
        B = S.BPOW.get(p, 1)
        tab = trace_density(p ** B) if p in S.BPOW else delta_closed(p)
        out.append((p, B, np.asarray(tab, np.float64)))
    return out


_SPF = None


def spf():
    global _SPF
    if _SPF is None:
        _SPF = V1.spf_sieve(V1.Q)
    return _SPF


def curve(r, mode, c0, pmax_planted=None):
    pe = min(Q_EX, pmax_planted or Q_EX)
    Np, Bp, offs, wcat = exact_tables(r, mode, model_primes(pe))
    Bfull = np.zeros(Q_EX + 1, np.int64)
    Bfull[:len(Bp)] = Bp
    Nfull = np.ones(Q_EX + 1, np.int64)
    Nfull[:len(Np)] = Np
    ofull = np.zeros(Q_EX + 1, np.int64)
    ofull[:len(offs)] = offs
    accx, mx = exact_sum(Q_EX, spf(), Nfull, Bfull, ofull, wcat, LS)
    small, wp, Mt = V1.weights(r, mode, pmax_planted)
    accf, mf = flat_sum_from(Q_EX + 1, V1.Q, spf(), wp, small, LS)
    _, mflat_ex = flat_sum_from(2, Q_EX, spf(), wp, small, LS[:1])
    E2 = c0 * (accx + accf + (Mt - mx - mf) / LS)
    return np.sqrt(E2), dict(M_total=Mt, mass_exact_q_le_Qex=mx, mass_flat_q_le_Qex=mflat_ex, mass_flat_rest=mf)


def unittest():
    """Spectral sum (all exact, Q_EX ≥ period) against the direct mean over all window positions."""
    res = []
    cases = (((5, 7), 0, 0), ((5, 7), 2, 1), ((3, 11, 13), 0, 0), ((3, 11, 13), 4, 1),
             (((5, 2), 7), 0, 0), (((5, 2), 7), 3, 1), (((2, 4), (3, 2)), 2, 1))
    for spec, r, mode in cases:
        pb = []
        for e in spec:
            p, B = (e, 1) if isinstance(e, int) else e
            pb.append((p, B, np.asarray(trace_density(p ** B) if B > 1 or p == 2 else delta_closed(p), np.float64)))
        primes = [p for p, _, _ in pb]
        period = int(np.prod([p ** B for p, B, _ in pb]))
        n = np.arange(period * 3 + 400)
        x = np.ones(len(n))
        for p, B, d in pb:
            q = p ** B
            x *= d[n % q] if mode == 0 else d[n % q] * d[(n + r) % q]
        x = x / x[:period].mean() - 1.0
        Ls = np.array([3, 10, 37, 100, 250], np.int64)
        direct = []
        for L in Ls:
            cs = np.concatenate([[0.0], np.cumsum(x)])
            wm = (cs[np.arange(period) + L] - cs[np.arange(period)]) / L
            direct.append(math.sqrt(np.mean(wm ** 2)))
        Np, Bp, offs, wcat = exact_tables(r, mode, pb)
        pad = lambda v, fill: np.concatenate([v, np.full(period + 1 - len(v), fill, np.int64)])
        acc, m = exact_sum(period, V1.spf_sieve(period), pad(Np, 1), pad(Bp, 0), pad(offs, 0), wcat, Ls)
        spec = np.sqrt(acc)
        err = float(np.max(np.abs(spec - np.array(direct)) / np.array(direct)))
        res.append(dict(primes=[[p, B] for p, B, _ in pb], r=r, mode=mode, max_rel_err=err))
        print(primes, r, mode, "max rel err", err)
    ok = all(x["max_rel_err"] < 1e-10 for x in res)
    print("UNITTEST_PASS", ok)
    return 0 if ok else 1


def check(out):
    res = dict(L=LS.tolist(), Q_EX=Q_EX, witnesses={})
    ok_all = True
    for wdef in WITNESSES:
        tabs = S.tables(wdef["pmax"])
        rng = np.random.default_rng(wdef["seed"])
        shifts = [int(rng.integers(q)) for q, _ in tabs]
        a = S.delta(0, 3 * 10 ** 6 - 2, tabs, shifts) - 1.0
        rs = [0, 1, 2, 4]
        ex = S.planted_exact(rs, tabs, 1.0)
        meas = V1.measure(a, rs)
        rows = {}
        for key in ["alpha"] + rs:
            mean_ref = 0.0 if key == "alpha" else ex[key]
            E_meas = np.array([math.sqrt(np.mean((w - mean_ref) ** 2)) for w in meas[key]])
            mode = 0 if key == "alpha" else 1
            c0 = 1.0 if key == "alpha" else (1 + ex[key]) ** 2
            E_pred, info = curve(0 if key == "alpha" else key, mode, c0, pmax_planted=wdef["pmax"])
            if key == "alpha":
                exact_m2 = float(np.prod([np.mean(t ** 2) for _, t in tabs]) - 1)
            else:
                exact_m2 = float(np.prod([np.mean((t * np.roll(t, -(key % q))) ** 2)
                                          / np.mean(t * np.roll(t, -(key % q))) ** 2 for q, t in tabs]) - 1)
            m = (LS >= 1e3) & (LS <= 1e5)
            ratio = E_meas / E_pred
            s_meas, s_pred = V1.slope(LS, E_meas), V1.slope(LS, E_pred)
            ok = bool(np.all(np.abs(ratio[m] - 1) <= 0.25) and abs(s_meas - s_pred) <= 0.05
                      and abs(info["M_total"] / exact_m2 - 1) <= 0.01)
            ok_all &= ok
            rows[str(key)] = dict(E_meas=E_meas.tolist(), E_pred=E_pred.tolist(), ratio=ratio.tolist(),
                                  slope_meas=s_meas, slope_pred=s_pred, M_exact=exact_m2, ok=ok,
                                  max_abs_ratio_dev_1e3_1e5=float(np.max(np.abs(ratio[m] - 1))), **info)
            print(wdef["name"], key, f"slope meas {s_meas:.3f} pred {s_pred:.3f}; meas/pred [1e3,1e5] "
                  f"{ratio[m].min():.3f}–{ratio[m].max():.3f}; M {info['M_total']:.5f} exact {exact_m2:.5f}; "
                  f"exact/flat mass q<=Qex {info['mass_exact_q_le_Qex']:.5f}/{info['mass_flat_q_le_Qex']:.5f}; ok {ok}",
                  flush=True)
        res["witnesses"][wdef["name"]] = rows
    res["CHECK1_PASS"] = bool(ok_all)
    json.dump(res, open(out, "w"), indent=1)
    print("CHECK1_PASS", ok_all)
    return 0


def predict(pred_json, out):
    chk = json.load(open(out.replace("PREDICT", "CHECK1")))
    assert chk["CHECK1_PASS"], "check 1 failed: no prediction (Will, 2026-10-31)"
    pred = json.load(open(pred_json))
    lags = S.lags_of(pred)
    g = {r: pred["gamma"][str(r)]["gamma"] for r in lags}
    res = dict(L=LS.tolist(), Q_EX=Q_EX, rows={})
    E, info = curve(0, 0, 1.0)
    res["rows"]["alpha"] = dict(E_pred=E.tolist(), slope_pred=V1.slope(LS, E), gamma0_peter=g[0], **info,
                                check2_ok=bool(abs(info["M_total"] / g[0] - 1) <= 0.01))
    print("alpha", V1.slope(LS, E), info["M_total"], g[0], flush=True)
    for r in lags:
        E, info = curve(r, 1, (1 + g[r]) ** 2)
        res["rows"][str(r)] = dict(E_pred=E.tolist(), slope_pred=V1.slope(LS, E), **info)
        print(r, f"slope {V1.slope(LS, E):.3f}", flush=True)
    json.dump(res, open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "unittest":
        sys.exit(unittest())
    if m == "check":
        sys.exit(check(sys.argv[2]))
    sys.exit(predict(sys.argv[2], sys.argv[3]))
