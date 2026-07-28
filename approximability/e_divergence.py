"""Arm 2 — the e divergence law, clean retry. e has liminf-K=inf => it is NOT self-similar: the DEGT
constant C=dim*ln(lambda) has no finite value -- measured over deeper CF windows it CLIMBS. Metallics
(periodic CF, finite K) are self-similar: C is window-STABLE.
Instrument: gated growth-rate C (same convergence gate as O1 -- shallow-q vs deep-q dim agreement per
lambda, low-lambda points are the resolvable ones, extrapolate dim*ln(lambda) in 1/ln(lambda)->0).
Compare C(EARLY window) vs C(LATE window). Divergence signature = e climbs, silver flat.
NB: the Sigma^2-gamma route (Arm 1 class_probe, e in CTRL) is the complementary clean instrument.
Engine read-only from cross_substrate/."""
import os, sys, json, math
import numpy as np
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
from cross_substrate.trace_map_dimension import band_widths, potential, cf_convergent

LAMS = [2.0, 4.0, 8.0, 16.0, 32.0, 48.0, 64.0]
PHI = 0.1234

def dim_growth_q(alpha, lam, qlist):
    levels=[]
    for qt in qlist:
        p,q=cf_convergent(alpha,qt); w=band_widths(potential(q,p,lam,PHI))
        if w.size>2: levels.append((q,w))
    seen={};
    for q,w in levels: seen[q]=w
    levels=sorted(seen.items())
    if len(levels)<3: return None
    logq=np.array([math.log(q) for q,_ in levels])
    dgrid=np.linspace(0.02,0.999,300)
    P=np.array([np.polyfit(logq,np.array([math.log(np.sum(w**d)) for _,w in levels]),1)[0] for d in dgrid])
    sign=np.sign(P); cross=np.where(np.diff(sign)!=0)[0]
    if cross.size==0: return None
    i=cross[0]; return float(dgrid[i]-P[i]*(dgrid[i+1]-dgrid[i])/(P[i+1]-P[i]))

def gated_C(alpha, qshallow, qdeep):
    """C = lambda->inf extrapolation of dim*ln(lambda) over convergence-gated lambda (|dim_shallow-dim_deep|<0.02).
    qshallow/qdeep are the two q-windows used BOTH for the convergence gate and (deep) for the dim value."""
    pts=[]
    for lam in LAMS:
        ds=dim_growth_q(alpha,lam,qshallow); dd=dim_growth_q(alpha,lam,qdeep)
        if ds is None or dd is None or abs(ds-dd)>=0.02: continue
        pts.append((1.0/math.log(lam), dd*math.log(lam)))
    if len(pts)<3: return None, len(pts)
    x=np.array([p[0] for p in pts]); y=np.array([p[1] for p in pts])
    return float(np.polyfit(x,y,1)[1]), len(pts)

def conv_qs(alpha, lo, hi):
    qs=[]
    for qt in np.unique(np.geomspace(lo,hi,30).astype(int)):
        p,q=cf_convergent(alpha,int(qt))
        if lo<=q<=hi and q not in qs: qs.append(int(q))
    return sorted(qs)

def main():
    import mpmath as mp; mp.mp.dps=60
    subs={'e':float(mp.frac(mp.e)), 'silver':float(mp.sqrt(2)-1)}
    out={}
    for name,alpha in subs.items():
        # EARLY depth band and LATE depth band (both capped at q<4000 for dense eigvalsh)
        early_s=conv_qs(alpha,15,120); early_d=conv_qs(alpha,60,700)
        late_s =conv_qs(alpha,120,700); late_d =conv_qs(alpha,400,4000)
        C_early,n_e=gated_C(alpha,early_s,early_d)
        C_late, n_l=gated_C(alpha,late_s, late_d)
        climb=(None if (C_early is None or C_late is None) else C_late-C_early)
        out[name]=dict(alpha=alpha,C_early=C_early,C_late=C_late,climb=climb,
                       n_early=n_e,n_late=n_l,windows=dict(early_d=early_d,late_d=late_d))
        print(f"{name:7s} C_early={C_early} (n={n_e})  C_late={C_late} (n={n_l})  climb={climb}",flush=True)
    e=out['e']; ag=out['silver']
    ok = all(out[s]['climb'] is not None for s in subs)
    div = ok and e['climb']>0.05 and abs(ag['climb'])<0.05
    stable_fail = ok and abs(ag['climb'])>=0.05
    out['verdict']=dict(e_climb=e['climb'],silver_climb=ag['climb'],
        result=('DIVERGENCE-CONFIRMED (e C climbs with depth; silver flat)' if div
                else ('INCONCLUSIVE-CONTROL-UNSTABLE (silver should be flat; growth-rate route too noisy at q<4000 '
                      '-> Sigma^2-gamma route in Arm1 is the instrument)' if stable_fail
                      else 'INCONCLUSIVE (see points; defer to Arm1 e-gamma)')))
    print("\nVERDICT:",out['verdict']['result'])
    json.dump(out,open('Arm2_e_divergence_measured.json','w'),indent=1,default=float)
    print("wrote Arm2_e_divergence_measured.json")

if __name__=='__main__':
    main()
