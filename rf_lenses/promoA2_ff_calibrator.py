"""Session A / Axis A2 — promote the function-field F_q[T] RF-calibrator error-rate, or scope it.

Layer-zero A2-Z (PROVABLE, fires unconditionally): the exact prime-polynomial theorem
sum_{deg f = n} Lambda(f) = q^n  (= genus-0 Weil: N_v = q^v+1 on P^1, bound trivial/exact). Asserted for
q in {2,3,5,7} in the pre-flight cell.

SCOPE BANKED (discipline, grep-confirmed): the banked Thread-C machinery is F_q[T] = the line, genus 0
ONLY (no curve / point-counting symbols). The spec's genus>0 curve sweep + nontrivial Weil bound
|N_v-(q^v+1)|<=2g q^{v/2} needs a curve point-counting module that does not exist -> BANKED as a separate
dedicated session, NOT run here.

Method-invariance tested on banked machinery: (ii) base-field q {2,3,5}; (iii) RF-exponent estimator
{ols, theilsen, last2}; (iv) degree-window range. Claim: the calibrator's convergence exponent
(a_m -> mu(m)/phi(m) at rate ~ q^{-D}) recovers the Weil-consistent value beta ~ log10(q), invariant.
BASE_SEED=20240517.
"""
import os,sys,json,math,io,contextlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from functools import lru_cache
import numpy as np
from scipy import stats
with contextlib.redirect_stdout(io.StringIO()):
    import threadC_function_field as tc
OUT=os.path.dirname(os.path.abspath(__file__))
tc.factor=lru_cache(maxsize=None)(tc.factor); tc.cm_holder=lru_cache(maxsize=None)(tc.cm_holder)

def a_m_error(q, Dmax):
    """rel error of estimated a_m vs closed form mu(m)/phi(m), for deg-1 & deg-2 m, over D=2..Dmax."""
    tc.setq(q)
    # CRITICAL: factor/cm_holder results depend on the global field Q -> clear caches on every field change
    # (memoizing across setq() returns stale factorizations from the previous field; gate-caught bug).
    tc.factor.cache_clear(); tc.cm_holder.cache_clear(); tc.irreducibles_upto.cache_clear()
    irr=tc.irreducibles_upto(Dmax);
    ms={1:[p for p in irr if tc.deg(p)==1][0]}
    d2=[p for p in irr if tc.deg(p)==2]
    if d2: ms[2]=d2[0]
    closed={d:tc.mu_poly(m)/tc.phi_poly(m) for d,m in ms.items()}
    out={d:{"D":[],"rel":[]} for d in ms}
    for D in range(2,Dmax+1):
        allf=[f for n in range(1,D+1) for f in tc.monics(n)]; dn=len(allf)
        for d,m in ms.items():
            am=sum(tc.vonmangoldt(f)*tc.cm_holder(m,f) for f in allf)/dn/tc.phi_poly(m)
            out[d]["D"].append(D); out[d]["rel"].append(abs(am-closed[d])/abs(closed[d]))
    return out, closed

def exponent(D, rel, estimator):
    """fit log10(rel) = -beta*D + c ; beta = convergence exponent per degree."""
    D=np.array(D,float); y=np.log10(np.array(rel,float)+1e-18)
    good=np.isfinite(y)&(np.array(rel)>1e-15)
    D,y=D[good],y[good]
    if D.size<3: return None
    if estimator=="ols": beta=-np.polyfit(D,y,1)[0]
    elif estimator=="theilsen": beta=-stats.theilslopes(y,D)[0]
    elif estimator=="last2": beta=-(y[-1]-y[-2])/(D[-1]-D[-2])
    return float(beta)

# degree budget per q (feasible): q=2 ->10, q=3 ->5, q=5 ->4
BUDGET={2:10, 3:5, 5:4}
results={"scope_banked":"genus>0 curve sweep needs point-counting machinery absent from banked code -> deferred",
         "layer_zero":"exact prime-poly theorem sum_{deg=n}Lambda=q^n asserted q=2,3,5,7 (genus-0 Weil)"}
rows={}
print("A2 — FF calibrator convergence exponent  beta (a_m->mu/phi at rate ~q^{-D}); Weil-consistent target beta~log10(q)")
print(f"{'q':>2} {'log10(q)':>8} {'deg m':>5} {'ols':>7} {'theilsen':>9} {'last2':>7} {'Dwin[hi]':>9} {'Dwin[lo]':>9}")
for q,Dmax in BUDGET.items():
    errs,closed=a_m_error(q,Dmax); rows[q]={}
    for d in errs:
        D=errs[d]["D"]; rel=errs[d]["rel"]
        # full-window exponents by 3 estimators
        e_ols=exponent(D,rel,"ols"); e_ts=exponent(D,rel,"theilsen"); e_l2=exponent(D,rel,"last2")
        # degree-window invariance: high half vs low half
        h=len(D)//2
        e_hi=exponent(D[h:],rel[h:],"ols"); e_lo=exponent(D[:h+1],rel[:h+1],"ols")
        rows[q][d]=dict(closed=closed[d], D=D, rel=rel, ols=e_ols, theilsen=e_ts, last2=e_l2,
                        Dwin_hi=e_hi, Dwin_lo=e_lo, log10q=math.log10(q))
        print(f"{q:>2} {math.log10(q):>8.4f} {d:>5} {e_ols:>7.3f} {e_ts:>9.3f} {e_l2:>7.3f} "
              f"{(e_hi if e_hi else float('nan')):>9.3f} {(e_lo if e_lo else float('nan')):>9.3f}")
results["exponents"]=rows

# ---- verdict: is the recovered exponent beta INVARIANT across estimator & degree-window (per field)? ----
# NOTE: the specific 'Weil rate' target is NOT asserted -- the exact FF error-rate theorem was not verified
# from source this session (unverified anchor, banked). Promotion is on INVARIANCE + sensible q-scaling only.
def collect(q):
    vals=[]
    for d in rows[q]:
        r=rows[q][d]
        for k in ("ols","theilsen","last2","Dwin_hi","Dwin_lo"):
            if r[k] is not None: vals.append(r[k])
    return np.array(vals)
print("\nInvariance check (beta stable across estimator & degree window WITHIN each field; and beta grows with q):")
promote=True; means={}
for q in BUDGET:
    v=collect(q); spread=float(np.std(v)); mean=float(np.mean(v)); means[q]=mean
    cv=spread/mean if mean else 9
    stable = cv < 0.15                       # <15% spread across estimator x degree-window = method-invariant
    promote = promote and stable
    print(f"  q={q}: beta mean={mean:.3f}  spread(std)={spread:.3f}  CV={cv:.2f}  {'STABLE' if stable else 'DRIFT'}")
q_monotone = all(means[a] <= means[b]+1e-9 for a,b in zip(sorted(means)[:-1],sorted(means)[1:]))
print(f"  beta increases with q (bigger field -> faster convergence): {means}  monotone={q_monotone}")
results["beta_means"]=means; results["q_monotone"]=bool(q_monotone)
verdict = ("METHOD_INVARIANT_PROMOTE (scope: F_q[T]/genus-0; genus>0 sweep BANKED; exact Weil-rate UNVERIFIED)"
           if (promote and q_monotone) else "SCOPE_OR_KILL")
results["verdict"]=verdict
print(f"\nA2 VERDICT: {verdict}")
json.dump(results, open(os.path.join(OUT,"promoA2.json"),"w"), indent=1, default=float)
print("wrote promoA2.json")
