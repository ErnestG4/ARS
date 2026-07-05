"""The Diatonic Hamiltonian: spectrum of the Sturmian operator at alpha=log2(3/2)
across the full convergent ladder q<=15601, lam in {8,24,32}.

CERTIFIED PATH ONLY. potential/cf_frac/convergents imported verbatim from task1_pi_depth5.
periodic_edges is byte-identical to the certified depth4/depth5 Floquet scripts (the
q=33102/33215 banked path); bs_dim/box_dim are byte-identical to the certified estimators
inside task1_pi_depth5. No new physics; the ONLY new input is alpha. Seed 20240517.

Outputs per (lam,depth): exact bands, total bandwidth, both dim estimators + agreement<=0.02
bank flag. Plus per-step width ratios, running geomean K, gap-labeling for q=12,q=53.
Run: PYTHONPATH=/home/combust/fmexplorer/riemann_explorer /home/combust/fmexplorer/bin/python3 \
     approximability/fifth_ladder.py
"""
import os, sys, math, json, time, gc
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT); sys.path.insert(0, OUT)
import numpy as np
import scipy.linalg as sla
import mpmath as mp
from task1_pi_depth5 import potential, cf_frac, convergents

SEED = 20240517
LAMBDAS = [8.0, 24.0, 32.0]
t0 = time.time()

# ---- CERTIFIED Floquet operator (verbatim from depth4_q33102_floquet.py / depth5) ----
def periodic_edges(V, corner):
    q = len(V); H = np.zeros((q, q), dtype=np.float64); np.fill_diagonal(H, V)
    idx = np.arange(q - 1); H[idx, idx + 1] = 1.0; H[idx + 1, idx] = 1.0
    H[0, q - 1] = corner; H[q - 1, 0] = corner
    w = sla.eigvalsh(H, overwrite_a=True, driver='evr')
    del H; gc.collect(); return w

def floquet_bands(V):
    ep = periodic_edges(V, +1.0); ea = periodic_edges(V, -1.0)
    edges = np.sort(np.concatenate([ep, ea]))
    return edges

# ---- CERTIFIED dimension estimators (verbatim from task1_pi_depth5 __main__) ----
def bs_dim(bands, q):
    if not bands: return float("nan")
    mw = sum(hi - lo for lo, hi in bands) / len(bands)
    return math.log(q) / math.log(1.0 / mw) if 0 < mw < 1 else float("nan")

def box_dim(bands, e0, e1, n=12):
    span = e1 - e0; mw = sum(hi - lo for lo, hi in bands) / max(1, len(bands))
    counts, scales, eps = [], [], span
    for _ in range(n):
        s = set()
        for lo, hi in bands:
            for b in range(int((lo - e0) / eps), int((hi - e0) / eps) + 1): s.add(b)
        counts.append(len(s)); scales.append(eps); eps /= 2
        if eps < 2 * mw: break
    if len(counts) < 3: return float("nan")
    return float(np.polyfit(np.log2(1 / np.array(scales)), np.log2(counts), 1)[0])

# ---- CF (two-precision banked) + ladder ----
mp.mp.dps = 80
alpha = mp.log(mp.mpf(3) / mp.mpf(2)) / mp.log(mp.mpf(2))
cf = cf_frac(alpha, 12)
ps, qs = convergents(cf)
LADDER = [(ps[k], qs[k], (cf[k] if k < len(cf) else None)) for k in range(len(qs)) if qs[k] <= 15601]
# running geomean K_k = (a_1..a_k)^{1/k}
Krun = {}
prod = 1
for k in range(len(cf)):
    prod *= cf[k]; Krun[qs[k]] = prod ** (1.0 / (k + 1))
print(f"[{time.time()-t0:.0f}s] alpha=log2(3/2)={mp.nstr(alpha,20)}  cf={cf}")
print(f"    ladder q<=15601: {[q for _,q,_ in LADDER]}")

results = {}
for lam in LAMBDAS:
    e0, e1 = -2.5, lam + 2.5
    per_depth = {}
    prev_tw = None; prev_q = None
    for (p, q, a) in LADDER:
        td = time.time()
        if q == 1:
            # period-1 = constant potential lam: band [lam-2,lam+2], analytic (Floquet corner ill-defined at q=1)
            edges = np.array([lam - 2.0, lam + 2.0]); bands = [(lam - 2.0, lam + 2.0)]
        else:
            V = potential(p, q, lam)              # asserts impurity count == p (layer-zero gate)
            edges = floquet_bands(V)
            bands = [(edges[2 * j], edges[2 * j + 1]) for j in range(q)]
        nb = len(bands); tw = float(sum(hi - lo for lo, hi in bands)); mw = tw / nb
        d_bs = bs_dim(bands, q)
        d_box = box_dim(bands, e0, e1) if q >= 5 else float('nan')  # box needs >=3 scales
        agree = (abs(d_bs - d_box) <= 0.02) if (np.isfinite(d_bs) and np.isfinite(d_box)) else False
        ratio = (tw / prev_tw) if prev_tw else None
        rec = dict(q=q, p=p, a_to_here=a, bands=nb, count_eq_q=(nb == q),
                   total_width=tw, mean_width=mw, dim_bandscaling=d_bs, dim_boxcount=d_box,
                   estimator_agreement=(abs(d_bs - d_box) if np.isfinite(d_box) else None),
                   agree_le_0p02=bool(agree), width_ratio_vs_prev=ratio,
                   step_quotient=a, K_running=Krun.get(q), outside_proven_regime=(lam <= 20),
                   dim_x_lnlam=(d_bs * math.log(lam)) if np.isfinite(d_bs) else None,
                   banked=bool((nb == q or q == 1) and (agree or q < 5) and 0 < d_bs < 1),
                   wall_s=time.time() - td)
        per_depth[q] = rec
        # save edges for the figure (small)
        np.save(os.path.join(OUT, f"fifth_edges_lam{int(lam)}_q{q}.npy"), edges)
        print(f"  lam={lam:>4} q={q:6d} p={p:6d} a={str(a):>3} bands={nb} tw={tw:.6e} "
              f"dim_bs={d_bs:.4f} dim_box={d_box:.4f} agree={agree} "
              f"W/Wprev={('%.4f'%ratio) if ratio else '   -  '} K={Krun.get(q):.3f} [{rec['wall_s']:.1f}s]")
        prev_tw = tw; prev_q = q
    results[f"lam{lam}"] = per_depth
    json.dump(dict(seed=SEED, alpha=mp.nstr(alpha, 30), cf=cf, ladder=[q for _, q, _ in LADDER],
                   K_running={str(k): v for k, v in Krun.items()}, results=results),
              open(os.path.join(OUT, "fifth_ladder.json"), "w"), indent=1)
    print(f"[{time.time()-t0:.0f}s] lam={lam} done, checkpointed.")

print(f"\n[{time.time()-t0:.0f}s] LADDER COMPLETE. wrote fifth_ladder.json")
