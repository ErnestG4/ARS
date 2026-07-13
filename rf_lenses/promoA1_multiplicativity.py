"""Session A / Axis A1 — promote 'RF-multiplicativity R2' or kill it.

Adversarial: keep ONLY if METHOD_INVARIANT. The axis classifies substrates by the Kronecker R2 of
a_{q1q2} vs a_{q1}a_{q2}/a_1 (coprime), from ESTIMATED a_q (finite data), NOT the closed form.

Pre-registered confound (the decisive gate): c_q multiplicativity in q is a THEOREM, so R2=1 on arithmetic
could be re-deriving it, and dynamical R2~0 could be an SNR floor, not genuine non-multiplicativity. If a
MATCHED-SNR arithmetic control (same event count as the dynamical substrate) ALSO drops toward R2~0, the axis
is an SNR/N artifact -> KILL. If the arithmetic control stays high at matched N, the separation is genuine.

Battery: regression estimator {OLS,TheilSen,Huber} x q-support {all,prime-power,squarefree} x coprimality
{strict,relaxed} x a1-normalization {divide,omit} x matched-SNR control (banked instrument_confound.random_thin).
Read-only vs the tool. BASE_SEED=20240517.
"""
import os,sys,json,math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT); sys.path.insert(0,os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))
import numpy as np
import arithmetic_toolkit as at
import transition_calibrators_dynamical as tcd
from cross_substrate.instrument_confound import random_thin
from scipy import stats
from sklearn.linear_model import HuberRegressor
OUT=os.path.dirname(os.path.abspath(__file__)); SEED=20240517
QMAX=120

def is_prime_power(q):
    if q<2: return False
    d=2
    while d*d<=q:
        if q%d==0:
            while q%d==0: q//=d
            return q==1
        d+=1
    return True
def is_squarefree_q(q):
    d=2
    while d*d<=q:
        if q%(d*d)==0: return False
        d+=1
    return True

def aq_from_positions(pos, qmax=QMAX):
    """ESTIMATED signed a_q: bin event positions to an integer indicator, a_q=(1/phi(q))<f c_q>."""
    t=np.sort(np.asarray(pos,float))
    if t.size<5: return None
    nb=int(np.ceil(t.max()-t.min()))+1
    if nb<2*qmax: return None
    f=np.zeros(nb); idx=np.clip(np.floor(t-t.min()).astype(int),0,nb-1); np.add.at(f,idx,1.0)
    a=np.zeros(qmax+1)
    for q in range(1,qmax+1): a[q]=np.mean(f*at.ramanujan_sum_array(q,nb))/at.euler_phi(q)
    return a

def kronecker_R2(a, estimator="ols", support="all", coprime=True, normalize=True):
    a1=a[1]
    xs=[]; ys=[]
    for q1 in range(2,QMAX+1):
        if support=="prime_power" and not is_prime_power(q1): continue
        if support=="squarefree" and not is_squarefree_q(q1): continue
        for q2 in range(q1,QMAX//q1+1):
            if q1*q2>QMAX: break
            if support=="prime_power" and not is_prime_power(q2): continue
            if support=="squarefree" and not is_squarefree_q(q2): continue
            if coprime and math.gcd(q1,q2)!=1: continue
            if (not coprime) and math.gcd(q1,q2)==1: continue   # relaxed = NON-coprime pairs (leak test)
            pred=(a[q1]*a[q2]/a1) if normalize else (a[q1]*a[q2])
            xs.append(pred); ys.append(a[q1*q2])
    xs=np.array(xs); ys=np.array(ys); m=np.isfinite(xs)&np.isfinite(ys)
    xs,ys=xs[m],ys[m]
    if xs.size<6: return None
    # R2 of ys vs the fitted line by the chosen estimator (identity target -> R2 measures how well pred==meas)
    if estimator=="ols":
        b=np.polyfit(xs,ys,1); yhat=np.polyval(b,xs)
    elif estimator=="theilsen":
        sl,ic,_,_=stats.theilslopes(ys,xs); yhat=sl*xs+ic
    elif estimator=="huber":
        hr=HuberRegressor().fit(xs.reshape(-1,1),ys); yhat=hr.predict(xs.reshape(-1,1))
    ss_res=np.sum((ys-yhat)**2); ss_tot=np.sum((ys-ys.mean())**2)
    return float(1-ss_res/ss_tot) if ss_tot>0 else None

# ---------------- substrates (as event positions) ----------------
def sf_positions(N):
    s=np.ones(N+1,bool); s[0]=False; p=2
    while p*p<=N: s[p*p::p*p]=False; p+=1
    return np.nonzero(s[1:N+1])[0]+1
def prime_positions(N):
    s=np.ones(N+1,bool); s[:2]=False; p=2
    while p*p<=N:
        if s[p]: s[p*p::p]=False
        p+=1
    return np.nonzero(s[1:N+1])[0]+1
rng=np.random.default_rng(SEED)
def poisson_positions(nev): return np.cumsum(rng.exponential(1.0,nev))
def mg_positions():
    x=tcd.mackey_glass(tau=30.0,n_steps=300000,dt=0.1)
    return np.sort(np.asarray(tcd.MACKEY_GLASS_EXTRACTORS["running_mean_upcrossings"](x),float))

results={}

# ===== LAYER-ZERO A1-Z =====
print("="*70); print("A1-Z layer-zero gates")
z={}
# (1) c_q(n) integer-valued across the q-grid actually used
maxfrac=0.0
for q in range(1,QMAX+1):
    c=at.ramanujan_sum_array(q, 500); maxfrac=max(maxfrac, float(np.max(np.abs(c-np.round(c)))))
assert maxfrac<1e-9, f"c_q not integer-valued: {maxfrac}"
z["cq_integer_maxfrac"]=maxfrac; print(f"  (1) c_q(n) integer-valued: max frac part {maxfrac:.1e}  OK")
# (2) a_1 == known scalar on arithmetic controls
sfp=sf_positions(300000); a_full=aq_from_positions(sfp)
z["a1_squarefree"]=float(a_full[1]); z["a1_expected_6overpi2"]=6/math.pi**2
assert abs(a_full[1]-6/math.pi**2)<2e-3, a_full[1]
print(f"  (2) a_1(squarefree)={a_full[1]:.5f} vs 6/pi^2={6/math.pi**2:.5f}  OK")
# (3) estimator reproduces CLOSED-FORM c_q-based coefficients on held-out arithmetic control (induction-on-noise guard)
closed=lambda q: (6/math.pi**2)*at.mobius(q)/np.prod([p*p-1 for p in set(_pf(q))]) if q>1 else 6/math.pi**2
def _pf(n):
    f=[]; d=2
    while d*d<=n:
        while n%d==0: f.append(d); n//=d
        d+=1
    if n>1: f.append(n)
    return f
worst=max(abs(a_full[q]-closed(q)) for q in (2,3,5,6,7,10,15,30))
z["estimator_vs_closedform_worst"]=float(worst)
assert worst<5e-4, worst
print(f"  (3) estimated a_q vs closed-form squarefree coeffs: worst {worst:.1e}  OK (estimator trusted)")
results["layer_zero"]=z; print("  A1-Z PASS\n")

# ===== event-count budget for matched-SNR =====
mgp=mg_positions(); n_mg=mgp.size
print(f"Mackey-Glass event count (SNR target) = {n_mg}")
# matched-N arithmetic: squarefree over short window giving ~n_mg events (density 6/pi^2 -> N ~ n_mg/0.608)
N_match=int(n_mg/(6/math.pi**2))+2*QMAX      # ensure >=2*QMAX bins
sfp_match=sf_positions(N_match)
print(f"matched-N squarefree: N={N_match}, events={sfp_match.size}")
# also thinned-full (instrument_confound.random_thin) to n_mg events, over the FULL support (sparse control)
p_keep=n_mg/sfp.size; sfp_thin=random_thin(sfp.astype(float), p_keep, rng)
print(f"random_thin squarefree to p_keep={p_keep:.4f} -> {sfp_thin.size} events (sparse-over-full control)\n")

substrates={
 "squarefree_full":  sfp.astype(float),
 "primes_full":      prime_positions(300000).astype(float),
 "squarefree_matchN":sfp_match.astype(float),    # matched EVENT COUNT (short window) -- the decisive control
 "squarefree_thin":  np.sort(sfp_thin),          # matched count via random_thin over full support
 "mackey_glass":     mgp,
 "poisson_matchN":   poisson_positions(n_mg),
}
aq={name:aq_from_positions(pos) for name,pos in substrates.items()}

# ===== battery =====
battery=[]
for est in ("ols","theilsen","huber"):
    for sup in ("all","prime_power","squarefree"):
        for cop in (True,False):
            for nrm in (True,False):
                cfg=dict(estimator=est,support=sup,coprime=cop,normalize=nrm)
                row={"cfg":cfg,"R2":{}}
                for name,a in aq.items():
                    row["R2"][name]=(None if a is None else kronecker_R2(a,**cfg))
                battery.append(row)
results["battery"]=battery
results["event_counts"]={k:int(v.size) for k,v in substrates.items()}

# ===== verdict: is the arithmetic-vs-dynamical separation method-invariant AND not SNR? =====
def sep(row):
    R=row["R2"]
    arith=[R[k] for k in ("squarefree_full","primes_full") if R[k] is not None]
    dynam=[R[k] for k in ("mackey_glass","poisson_matchN") if R[k] is not None]
    if not arith or not dynam: return None
    return min(arith)-max(dynam)
def matchN_ok(row):
    R=row["R2"]
    # decisive: matched-N arithmetic still clearly separates from dynamical
    if R["squarefree_matchN"] is None or R["mackey_glass"] is None: return None
    return R["squarefree_matchN"]-max(x for x in (R["mackey_glass"],R["poisson_matchN"]) if x is not None)

seps=[sep(r) for r in battery if sep(r) is not None]
matchseps=[matchN_ok(r) for r in battery if matchN_ok(r) is not None]
n_sep_survive=sum(1 for s in seps if s>0.5)
n_match_survive=sum(1 for s in matchseps if s>0.5)
print("="*70); print("A1 BATTERY RESULT")
print(f"  configs run: {len(battery)}  (3 estimators x 3 supports x 2 coprimality x 2 normalization)")
print(f"  full-N separation (arith-dynam R2) > 0.5 in {n_sep_survive}/{len(seps)} configs")
print(f"  MATCHED-SNR separation (squarefree_matchN - dynamical) > 0.5 in {n_match_survive}/{len(matchseps)} configs")
# print a representative slice
print("\n  representative R2 by substrate (estimator=ols, support=all, coprime, normalize):")
r0=[r for r in battery if r["cfg"]=={'estimator':'ols','support':'all','coprime':True,'normalize':True}][0]
for k,v in r0["R2"].items(): print(f"    {k:20} R2={v}")
print("\n  matched-N control across estimators (support=all,coprime,normalize):")
for est in ("ols","theilsen","huber"):
    r=[r for r in battery if r["cfg"]=={'estimator':est,'support':'all','coprime':True,'normalize':True}][0]
    print(f"    {est:9}: squarefree_matchN R2={r['R2']['squarefree_matchN']}   MG R2={r['R2']['mackey_glass']}")

verdict = ("METHOD_INVARIANT_PROMOTE" if (n_sep_survive>=len(seps)*0.8 and n_match_survive>=len(matchseps)*0.8)
           else "SCOPE_OR_KILL")
results["verdict"]=dict(verdict=verdict, n_configs=len(battery),
                        fullN_sep_survive=n_sep_survive, matchSNR_sep_survive=n_match_survive,
                        total_sep=len(seps))
print(f"\n  A1 VERDICT: {verdict}  (matched-SNR is the decisive gate)")
json.dump(results, open(os.path.join(OUT,"promoA1.json"),"w"), indent=1, default=float)
print("wrote promoA1.json")
