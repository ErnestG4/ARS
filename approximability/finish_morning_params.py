"""
OVERNIGHT — the pending parameter turns (Task 2 + Part-I M=2000 + D1 λ→128/256), consolidated.

PARAMETER TURNS on the FROZEN clean-room refsuite: imports its functions with new params, writes to approximability/
(does NOT touch mathtest/ tables). No refsuite logic edits. Per-section try/except = checkpoint (one failure preserves
the rest). Seed 20240517. Pre-registrations are in MORNING.md and inline below.
"""
import os, sys, json, math, time
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/mathtest"))
import numpy as np, mpmath as mp
OUT = os.path.dirname(os.path.abspath(__file__))
GAMMA = 0.5772156649015329; PI2 = math.pi**2; K0 = 2.6854520010653064
res = {"seed": 20240517, "sections": {}}
CKPT = os.path.join(OUT, "finish_morning_params.json")
def save(): json.dump(res, open(CKPT, "w"), indent=2, default=str)
def sec(name, **kw): res["sections"][name] = kw; print(f"[{name}] " + json.dumps(kw, default=str)[:300]); save()


# ---------- Task 3: Part I at M=2000 (hard-pass the L=50 soft pass) ----------
try:
    t0 = time.time()
    from refsuite.schema import Table
    from refsuite.partI.run import run_partI, Config
    tbl = Table(); rep = run_partI(tbl, Config(M=2000))
    # extract L=50 Σ² ordering (analytic) + GUE closed-form check
    s2_50 = None
    for g in rep.get("gates", []):
        pass
    # pull from table rows
    rows = [r for r in (tbl.rows if hasattr(tbl, "rows") else [])]
    def rowval(stat, src, param, method):
        for r in rows:
            d = r.__dict__ if hasattr(r, "__dict__") else r
            if d.get("statistic")==stat and d.get("source")==src and d.get("parameter")==param and d.get("method")==method:
                return d
        return None
    gue50 = rowval("sigma2","GUE","L=50.0","analytic")
    pois50 = rowval("sigma2","Poisson","L=50.0","analytic")
    gue_closed = (1/PI2)*(math.log(2*math.pi*50)+GAMMA+1)
    sec("partI_M2000",
        wall_s=time.time()-t0, M=2000,
        gue_sigma2_L50=(gue50 or {}).get("sample_value"), gue_se=(gue50 or {}).get("sample_se"),
        gue_closed_form=gue_closed,
        gue_hard_pass=(gue50 is not None and abs(gue50["sample_value"]-gue_closed) <= max(3*gue50["sample_se"], 0.03*gue_closed)),
        poisson_sigma2_L50=(pois50 or {}).get("sample_value"),
        n_rows=len(rows), note="L=50 SE shrinks ~sqrt(10) vs M=200; hard-pass expected")
except Exception as e:
    sec("partI_M2000", ERROR=str(e))


# ---------- Task 3: the 3.5σ exceedance re-resolve (10× realizations) ----------
try:
    t0 = time.time()
    from refsuite.d2_cf import iid_gk_quotients, exceedance, exceedance_expected
    # NB: frozen exceedance(a,m)=count(a>=m); frozen gk_tail(m)=log2(1+1/m)=P(a>=m).
    # My original inline gk_tail=log2(1+1/(m+1))=P(a>=m+1) was an OFF-BY-ONE that
    # manufactured a phantom 3.5sigma "bias". Use the frozen baseline instead.
    def gk_tail(m): return math.log2(1.0 + 1.0/m)           # P(a>=m) via GK (frozen convention)
    N, m, MREAL = 100000, 10, 10000
    theory = N*gk_tail(m)
    rng = np.random.default_rng(20240517)
    cnts = np.array([exceedance(iid_gk_quotients(N, rng), m) for _ in range(MREAL)], float)
    samp = cnts.mean(); se = cnts.std()/math.sqrt(MREAL); sig = (samp-theory)/se
    sec("exceedance_reresolve",
        wall_s=time.time()-t0, N=N, m=m, realizations=MREAL, theory=theory,
        sample_mean=samp, se=se, sigma=sig,
        verdict=("regressed_to_theory" if abs(sig)<3 else "PERSISTS>3sigma_GENUINE_BIAS_ESCALATE"),
        note="prior 3.5σ at 1000 realizations; 10× data expected to regress")
except Exception as e:
    sec("exceedance_reresolve", ERROR=str(e))


# ---------- Task 3: D1 λ→{128,256} ----------
try:
    t0 = time.time()
    from refsuite.d1_fibonacci import band_scaling_dimension, find_bands_nested, box_count_dimension, LN_1_PLUS_SQRT2
    d1 = {}
    for lam in (128.0, 256.0):
        by, mv = find_bands_nested(20, lam)
        dim_bs = band_scaling_dimension(mv, lam)
        e0, e1 = -2.5, lam+2.5
        dim_box = box_count_dimension(by[mv], e0, e1)[0]  # returns (dim,scales,counts); take dim
        d1[lam] = {"max_valid_level": mv, "dim_band_scaling": dim_bs, "dim_box": dim_box,
                   "dim_times_lnlam": dim_bs*math.log(lam), "agree<=0.02": abs(dim_bs-dim_box)<=0.02}
    # non-increasing distance to DEGT on upper half {64,128,256} — need 64 too; recompute quickly
    d64 = band_scaling_dimension(find_bands_nested(20, 64.0)[1], 64.0)*math.log(64)
    seq = [d64, d1[128.0]["dim_times_lnlam"], d1[256.0]["dim_times_lnlam"]]
    devs = [abs(x-LN_1_PLUS_SQRT2) for x in seq]
    sec("d1_lambda_ext", wall_s=time.time()-t0, per_lambda=d1, DEGT=LN_1_PLUS_SQRT2,
        dim_lnlam_64_128_256=seq, dist_to_DEGT=devs, non_increasing=(devs[0]>=devs[1]>=devs[2]))
except Exception as e:
    sec("d1_lambda_ext", ERROR=str(e))


# ---------- Task 2: π Khinchin trajectory to N=1e5 (+ orbit-MC bands, exact controls) ----------
try:
    t0 = time.time()
    from refsuite.d2_cf import (cf_two_precision, running_geomean, exceedance, record_process,
                                max_over_N, gauss_orbit_quotients, iid_gk_quotients, cf_e_minus_2, cf_metallic)
    DEPTHS = [100, 1000, 10000, 100000]
    # π quotients, two-precision gated (Lévy: log10 q_N ~ 0.515 N ⇒ ~55k digits for 1e5)
    prec = int(0.515*100000) + 2000
    pi_q, agreed = cf_two_precision("pi", 100000, prec, int(1.1*prec))
    pi_q = np.array(pi_q)
    traj = {}
    for N in DEPTHS:
        if agreed < N:
            traj[N] = {"blocked": f"two-precision agreed only to depth {agreed}"}; continue
        a = pi_q[:N]
        traj[N] = {"geomean": running_geomean(a), "max_over_N": float(max_over_N(a)),
                   "exceed_m10": int(exceedance(a, 10)), "exceed_m292": int(exceedance(a, 292)),
                   "n_records": len(record_process(a)[0])}
    # orbit-MC 5-95% geomean bands at matching depths (arbiter null)
    rng = np.random.default_rng(20240517)
    bands = {}
    for N, no in [(100,4000),(1000,2000),(10000,600),(100000,200)]:
        gms = np.array([running_geomean(gauss_orbit_quotients(rng.random(), N)) for _ in range(no)])
        bands[N] = {"orbit_q05": float(np.percentile(gms,5)), "orbit_q95": float(np.percentile(gms,95)),
                    "orbit_mean": float(gms.mean())}
    # verdict: π geomean inside orbit band at each depth?
    for N in DEPTHS:
        if "geomean" in traj.get(N, {}) and N in bands:
            g = traj[N]["geomean"]
            traj[N]["inside_orbit_band"] = bands[N]["orbit_q05"] <= g <= bands[N]["orbit_q95"]
    sec("task2_pi_trajectory", wall_s=time.time()-t0, two_precision_agreed_depth=int(agreed),
        khinchin_K0=K0, pi=traj, orbit_bands=bands,
        exact_controls={"e_geomean_div": "K=∞ (spine)", "sqrt2_geomean": running_geomean(np.array(cf_metallic(2,10000))),
                        "golden_geomean": running_geomean(np.array(cf_metallic(1,10000)))})
except Exception as e:
    sec("task2_pi_trajectory", ERROR=str(e))

res["done"] = True; res["total_wall_s"] = None
save()
print("\nFINISH-MORNING PARAMS DONE — see finish_morning_params.json")
