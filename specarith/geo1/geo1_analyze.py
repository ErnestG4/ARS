"""GEO1 Step 1 gates and witness (GEO1_STEP1_PLAN.md §3–§4; tolerances fixed there before any run).

  python geo1_analyze.py WORDS_NPZ PARI_NPZ FORMS_JSON LIST6_JSON OUT_JSON

G1  class counts agree, every t: words (t ≤ T_w) = PARI Σ_u h⁺ (all classes) and words primitive = PARI g_prim; forms
    (t ≤ 40) = both. Red path: the wide sum Σ_u h(d) must differ from the words count at some t (the gate can fail).
G2  t = 6: the classes are exactly the cyclic words R⁴L, RL⁴, R²L² (run vectors [4,1], [1,4], [2,2]); R²L² has u = 2,
    d = 8; g(6) = h⁺(32) + h⁺(8) = 2 + 1.
G3  Sarnak / prime geodesic theorem: Π(T) = Σ_{3 ≤ t ≤ T} g_prim(t) against Li(x²), x = ε(T) = (T + √(T² − 4))/2:
    |Π/Li − 1| ≤ x^(−3/5)·ln(x²) at T = 10⁴, 10⁵, 10⁶. Red path: the wide sum must fail at T = 10⁶.
G4  Gauss–Kuzmin: pooled digit frequencies over primitive classes, t ≤ T_w, against −log₂(1 − 1/(k+1)²) (tail bin:
    log₂(1 + 1/(K+1))): total variation ≤ 0.05.
W   witness: random cyclic L/R words of matched letter length (seeded; 300 t, up to 1,000 words each, ≤ 2·10⁷ letters
    in all) must fail G4
    (TV from Gauss–Kuzmin > 0.10) and have geometric run lengths (TV from 2^−k ≤ 0.02).
"""
import json
import math
import sys

import mpmath as mp
import numpy as np

from geo1 import K, g_prim_from_all

SEED = 20261030


def gk(K):
    p = np.array([-math.log2(1 - 1 / (k + 1) ** 2) for k in range(1, K + 1)])
    return np.append(p, math.log2(1 + 1 / (K + 1)))


def tv(f, p):
    return 0.5 * float(np.abs(f - p).sum())


def main(wnpz, pnpz, fjson, ljson, out):
    w, p = np.load(wnpz), np.load(pnpz)
    fo, l6 = json.load(open(fjson)), json.load(open(ljson))
    res = {}
    tw = w["t"]
    Tw = int(tw[-1])
    tp = p["t"]
    assert tp[0] == 3 and np.array_equal(tp, np.arange(3, tp[-1] + 1))
    gall, gwide = p["g_all"], p["g_wide"]
    gprim = g_prim_from_all(tp, gall)
    gprim_w = g_prim_from_all(tp, gwide)
    # G1
    i = tw - 3
    eq_all = w["nall"] == gall[i]
    eq_prim = w["nprim"] == gprim[i]
    forms_ok = all(int(v) == int(w["nall"][int(t) - 3]) == int(gall[int(t) - 3]) for t, v in fo["classes"].items())
    wide_differs = int((w["nall"] != gwide[i]).sum())
    res["G1"] = dict(T_words=Tw, all_equal=bool(eq_all.all()), prim_equal=bool(eq_prim.all()),
                     n_t_mismatch_all=int((~eq_all).sum()), n_t_mismatch_prim=int((~eq_prim).sum()),
                     forms_TMAX=fo["TMAX"], forms_equal=bool(forms_ok),
                     red_path_wide_sum_differs_at_n_t=wide_differs, red_path_ok=bool(wide_differs > 0),
                     PASS=bool(eq_all.all() and eq_prim.all() and forms_ok and wide_differs > 0))
    # G2
    vecs = sorted(c["runs"] for c in l6["classes"])
    r2l2 = [c for c in l6["classes"] if c["runs"] == [2, 2]]
    ud = None
    if r2l2:
        a, b, c, d = r2l2[0]["matrix"]
        u = math.gcd(math.gcd(c, d - a), b)
        ud = [u, (36 - 4) // (u * u)]
    rows = p["rows"]
    g6 = {int(r[2]): (int(r[3]), int(r[4])) for r in rows if r[0] == 6}
    res["G2"] = dict(classes_t6=vecs, R2L2_u_d=ud, pari_t6={str(k): v for k, v in g6.items()}, g_all_6=int(gall[3]),
                     PASS=bool(vecs == [[1, 4], [2, 2], [4, 1]] and ud == [2, 8] and int(gall[3]) == 3))
    # G3
    mp.mp.dps = 30
    g3 = {}
    for name, g in (("hplus", gprim), ("wide_red_path", gprim_w)):
        cum = np.cumsum(g.astype(np.float64))
        rr = {}
        for T in (10 ** 4, 10 ** 5, 10 ** 6):
            if T > tp[-1]:
                continue
            x = (T + math.sqrt(T * T - 4)) / 2
            li = float(mp.li(x * x) - mp.li(2))
            rel = float(cum[T - 3]) / li - 1
            tol = x ** (-0.6) * math.log(x * x)
            rr[str(T)] = dict(Pi=float(cum[T - 3]), Li=li, rel_diff=rel, tol=tol, within=bool(abs(rel) <= tol))
        g3[name] = rr
    res["G3"] = dict(**g3, PASS=bool(all(v["within"] for v in g3["hplus"].values()) and len(g3["hplus"]) == 3),
                     red_path_fails=bool(not g3["wide_red_path"].get("1000000", {"within": True})["within"]))
    # G4
    p_gk = gk(K)
    h = w["hist"][:, 1:].sum(0).astype(np.float64)
    f = h / h.sum()
    res["G4"] = dict(T=Tw, digits=int(h.sum()), freq_1_5=f[:5].tolist(), gk_1_5=p_gk[:5].tolist(), TV=tv(f, p_gk),
                     tol=0.05, PASS=bool(tv(f, p_gk) <= 0.05))
    # witness
    rng = np.random.default_rng(SEED)
    cand = tw[(w["nprim"] > 0)]
    ts = np.sort(rng.choice(cand, size=min(300, len(cand)), replace=False))
    runs = []
    for t in ts:
        j = int(t) - 3
        L = max(2, int(round(w["slet"][j] / w["nprim"][j])))
        nwords = int(max(1, min(1000, w["nprim"][j], 2 * 10 ** 7 // (300 * L))))    # ≤ 2·10⁷ letters in all
        for _ in range(nwords):
            while True:
                x = rng.integers(0, 2, size=L)
                if 0 < x.sum() < L:
                    break
            k = int(np.argmax(x != x[-1]))                    # rotate to start at a run boundary
            x = np.roll(x, -k)
            cut = np.flatnonzero(np.diff(x)) + 1
            runs.extend(np.diff(np.concatenate([[0], cut, [L]])).tolist())
    rh = np.bincount(np.minimum(np.array(runs), K + 1), minlength=K + 2)[1:].astype(np.float64)
    fw = rh / rh.sum()
    geo = np.array([2.0 ** -k for k in range(1, K + 1)] + [2.0 ** -K])
    res["witness"] = dict(n_t=len(ts), runs=int(rh.sum()), TV_vs_GK=tv(fw, p_gk), TV_vs_geometric=tv(fw, geo),
                          PASS=bool(tv(fw, p_gk) > 0.10 and tv(fw, geo) <= 0.02))
    res["ALL_PASS"] = bool(all(res[k]["PASS"] for k in ("G1", "G2", "G3", "G4", "witness")) and res["G3"]["red_path_fails"])
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print(json.dumps({k: (v["PASS"] if isinstance(v, dict) else v) for k, v in res.items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:6]))
