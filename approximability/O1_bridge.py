"""O1 — verify the theta_inf = L_a / C_a bridge across the metallic ladder a=1..5.
SEALED (O1_bridge_prereg_SEALED.json): L_a exact = log((a+sqrt(a^2+4))/2); C_a via the validated Panel-A
growth-rate engine (dim*ln lambda, lambda->inf extrapolation over convergence-gated lambda). a=4 reproduces
Panel A 1.021607 (CALIBRATION); a=5 is the new run. Propagate C error -> theta_inf; golden self-check
(measured 0.548615 vs closed-form 0.545979 = the -0.4% C error) sets the bridge error budget.
Nothing here writes outside approximability/. Engine imported read-only from cross_substrate/."""
import os, sys, json, math
import numpy as np
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
from cross_substrate.trace_map_dimension import band_widths, _potential, cf_convergent

# Validated Panel-A engine extrapolates dim*ln(lambda) in 1/ln(lambda)->0 over CONVERGENCE-GATED lambda.
# The resolvable points are the LOW lambda; the high-lambda deep-window bands fall below float precision
# (MORNING_lambda wall) and the gate drops them. Must include low lambda to reproduce Panel A's C-values.
DEGT_LAMS = [2.0, 4.0, 8.0, 16.0, 32.0, 48.0, 64.0, 128.0]
PHI = 0.1234
PANEL_A_C = {1: 0.8771395920989912, 2: 0.8667114809952847, 3: 0.9133488642506151, 4: 1.0216069200712872}

def metallic(n):
    s = math.sqrt(n*n + 4.0)
    return dict(n=n, alpha=(s-n)/2.0, eps=(n+s)/2.0, levy=math.log((n+s)/2.0))

def conv_denoms(a, qmax):
    """convergent denominators of [a;a,a,...], STRICTLY below qmax (dense eigvalsh is O(q^3))."""
    qs=[1, a]; ps=[0, 1]
    while True:
        nq = a*qs[-1]+qs[-2]
        if nq >= qmax: break
        qs.append(nq); ps.append(a*ps[-1]+ps[-2])
    return ps, qs

def dim_growth_q(alpha, lam, qlist):
    levels=[]
    for qt in qlist:
        p, q = cf_convergent(alpha, qt)
        w = band_widths(_potential(q, p, lam, PHI))
        if w.size > 2: levels.append((q, w))
    seen={}
    for q,w in levels: seen[q]=w
    levels=sorted(seen.items())
    if len(levels)<3: return None
    logq=np.array([math.log(q) for q,_ in levels])
    dgrid=np.linspace(0.02,0.999,300)
    P=np.array([np.polyfit(logq, np.array([math.log(np.sum(w**d)) for _,w in levels]),1)[0] for d in dgrid])
    sign=np.sign(P); cross=np.where(np.diff(sign)!=0)[0]
    if cross.size==0: return None
    i=cross[0]
    return float(dgrid[i]-P[i]*(dgrid[i+1]-dgrid[i])/(P[i+1]-P[i]))

def C_of(a, qmax=4000, verbose=True):   # dense eigvalsh is O(q^3); Panel A capped ~1597. 4000 keeps runs minutes.
    m=metallic(a); alpha=m['alpha']
    _,qs=conv_denoms(a, qmax); qs=[q for q in qs if q>=5]
    # shallow vs deep windows (convergence gate), Panel-A shifted-window style: drop one level from each end
    # so both windows keep >=3 distinct levels even when few convergents fit under the q<4000 dense cap.
    shallow=qs[:-1]; deep=qs[1:]
    conv=[]; allp=[]
    for lam in DEGT_LAMS:
        ds=dim_growth_q(alpha,lam,shallow); dd=dim_growth_q(alpha,lam,deep)
        ok = ds is not None and dd is not None and abs(ds-dd)<0.02
        allp.append((lam,ds,dd,ok))
        if verbose: print(f"  a={a} lam={lam:6.1f} ds={ds} dd={dd} conv={ok}",flush=True)
        if ok: conv.append((1.0/math.log(lam), dd*math.log(lam), lam))
    if len(conv)<3: return None,None,allp,qs[-1]
    x=np.array([c[0] for c in conv]); y=np.array([c[1] for c in conv])
    A=np.vstack([x,np.ones_like(x)]).T
    coef,res,_,_=np.linalg.lstsq(A,y,rcond=None)
    C=float(coef[1])
    # error bar: residual-based std of the intercept
    yhat=A@coef; dof=max(1,len(x)-2); s2=float(np.sum((y-yhat)**2)/dof)
    cov=s2*np.linalg.inv(A.T@A); C_err=float(math.sqrt(cov[1,1]))
    return C, C_err, allp, qs[-1]

def main():
    out={'sealed_pred': json.load(open('O1_bridge_prereg_SEALED.json'))['theta_inf_pred_LoverC'], 'rungs':{}}
    for a in (4,5):
        print(f"=== C(a={a}) ===",flush=True)
        C,Cerr,allp,qdeep=C_of(a)
        m=metallic(a); L=m['levy']
        rec=dict(a=a, L=L, C=C, C_err=Cerr, q_deep=qdeep,
                 theta_inf=(L/C if C else None),
                 theta_err=(abs(L/(C*C))*Cerr if (C and Cerr) else None),
                 lam_points=[(lp[0],lp[1],lp[2],lp[3]) for lp in allp])
        if a==4 and C:
            rec['calibration_vs_panelA']=dict(panelA=PANEL_A_C[4], measured=C, delta_pct=100*(C-PANEL_A_C[4])/PANEL_A_C[4])
        out['rungs'][str(a)]=rec
        print(f"  -> C(a={a})={C} +/- {Cerr}  theta_inf={rec['theta_inf']}",flush=True)
        json.dump(out, open('O1_bridge_measured.json','w'), indent=1, default=float)
    print("\nwrote O1_bridge_measured.json")

if __name__=='__main__':
    main()
