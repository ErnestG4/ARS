"""
ARS-RH Phase 3b (fixed) — curvature-matched decoy battery for zeta-low-gamma Sigma^2.
Flat Poisson/GUE decoys certified an order that under-fits zeta-low-gamma's steep log-density
(caught by the theta-exact cross-check). Complete the battery with curvature-matched decoys:
GUE & Poisson on the zeta-low-gamma R-vM backbone. Find a GENERAL unfolding that recovers
known Sigma^2 through the curvature AND keeps Poisson=L (no over-smoothing). Then read zeta.
FIX vs first run: inversion grid now covers the full block gamma-range (+margin); local
unfold centered (conditioning); spline unfold added as the curvature-capable general path.
"""
import json, math, os, warnings
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.interpolate import UnivariateSpline
warnings.simplefilter("ignore", np.exceptions.RankWarning)
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
RNG=np.random.default_rng(20260726); EULER=0.5772156649015329
def rvm_N(t): tt=t/(2*math.pi); return tt*np.log(tt)-tt+7.0/8.0
N=2000; Ls=np.array([1,2,4,8,16,32],float)
z6=np.sort(np.loadtxt(os.path.join(ROOT,'data','odlyzko_zeros6.txt')))
blk=z6[:N]; t0=blk[0]; N0=rvm_N(t0); gmid=float(blk[N//2])
GMAX=float(blk[-1])+200.0                                   # FIX: cover full block range + margin
_G=np.linspace(5.0,GMAX,5_000_000); _NN=rvm_N(_G)
def rvm_inv(v): return np.interp(v,_NN,_G)
def sigma2(xi,Ls,step=0.25):
    xi=np.sort(xi);lo,hi=xi[0],xi[-1];o=[]
    for L in Ls:
        s=np.arange(lo,hi-L,step);c=np.searchsorted(xi,s+L)-np.searchsorted(xi,s);o.append(float(np.var(c)))
    return np.array(o)
def u_poly(x,order):
    x=np.sort(x);xm=x.mean();r=np.arange(1,len(x)+1)
    return np.polyval(np.polyfit(x-xm,r,order),x-xm)
def u_spline(x,srel):
    x=np.sort(x);r=np.arange(1,len(x)+1.)
    sp=UnivariateSpline(x,r,k=3,s=srel*len(x)); return sp(x)
def gue_unit(N):
    n=5*N;d=math.sqrt(2)*RNG.standard_normal(n);b=np.sqrt(RNG.chisquare(2*np.arange(n-1,0,-1)))
    ev=np.sort(eigh_tridiagonal(d,b,eigvals_only=True,select='i',select_range=(2*N,3*N-1)))
    s=np.diff(ev);return np.concatenate([[0.],np.cumsum(s/s.mean())])
def gue_analytic(Ls): return np.array([(1/math.pi**2)*(math.log(2*math.pi*L)+EULER+1) for L in Ls])
def gue_bb(): return rvm_inv(N0+gue_unit(N))
def pois_bb(): u=np.sort(RNG.exponential(1.,N).cumsum()); return rvm_inv(N0+u)
print("=== Phase 3b FIXED: curvature-matched decoys (gamma_mid=%.0f, grid to %.0f) ==="%(gmid,GMAX),flush=True)
print("GUE analytic:",["%.3f"%v for v in gue_analytic(Ls)],flush=True)
# sanity: theta on backbone must be exact GUE (rvm_N o rvm_inv = id)
tchk=np.array([sigma2(rvm_N(gue_bb()),Ls) for _ in range(6)]).mean(0)
print("theta-on-backbone (must=GUE analytic):",["%.3f"%v for v in tchk],flush=True)
B=10
methods=[("poly5",lambda x:u_poly(x,5)),("poly9",lambda x:u_poly(x,9)),("poly13",lambda x:u_poly(x,13)),
         ("spline1e-3",lambda x:u_spline(x,1e-3)),("spline1e-2",lambda x:u_spline(x,1e-2)),
         ("spline5e-2",lambda x:u_spline(x,5e-2))]
gate={}
print("\n[curvature gate] recover GUE=analytic AND Poisson=L through the backbone curvature:",flush=True)
for name,fn in methods:
    g=np.array([sigma2(fn(gue_bb()),Ls) for _ in range(B)]).mean(0)
    p=np.array([sigma2(fn(pois_bb()),Ls) for _ in range(B)]).mean(0)
    ge=np.abs(g-gue_analytic(Ls))/gue_analytic(Ls); pr=p[-1]/Ls[-1]
    ok=(ge.max()<0.30) and (0.75<=pr<=1.25)
    print("  %-11s GUE:%s (relerr %.2f) Pois_ratio %.2f %s"%(name,["%.3f"%v for v in g],ge.max(),pr,"PASS" if ok else "fail"),flush=True)
    gate[name]={"gue_relerr":float(ge.max()),"pois_ratio":float(pr),"pass":bool(ok)}
passing=[m for m,_ in methods if gate[m]["pass"]]
print("\n  general methods passing curvature gate:",passing,flush=True)
res={"gamma_mid":gmid,"Ls":list(Ls),"gate":gate,"passing":passing,"gue_analytic":gue_analytic(Ls).tolist()}
if passing:
    M=passing[0]; fn=dict(methods)[M]
    band=np.array([sigma2(fn(gue_bb()),Ls) for _ in range(30)]); bm,bs=band.mean(0),band.std(0)
    sz=sigma2(fn(blk),Ls); st=sigma2(rvm_N(blk),Ls); dev=(sz-bm)/bs
    agree=float(np.max(np.abs(sz-st)/np.maximum(st,1e-9)))
    print("\n[zeta-low-gamma] curvature-matched, method=%s"%M,flush=True)
    print("  zeta Sigma^2 (general):",["%.3f"%v for v in sz],flush=True)
    print("  zeta Sigma^2 (theta)  :",["%.3f"%v for v in st],flush=True)
    print("  GUE-on-backbone band  :",["%.3f"%v for v in bm],"+/-",["%.3f"%v for v in bs],flush=True)
    print("  (zeta-GUE)/sd         :",["%+.2f"%v for v in dev]," (neg=MORE rigid than GUE)",flush=True)
    print("  general-vs-theta relerr: %.3f %s"%(agree,"(AGREE)" if agree<0.2 else "(DISAGREE)"),flush=True)
    res["zeta"]={"method":M,"sigma2_general":sz.tolist(),"sigma2_theta":st.tolist(),
                 "gue_band_mean":bm.tolist(),"gue_band_sd":bs.tolist(),"dev_over_sd":dev.tolist(),
                 "general_vs_theta_relerr":agree}
else:
    print("  NO general unfolding threads curvature-vs-oversmoothing at low gamma -> verdict via theta-exact only (bespoke).",flush=True)
    st=sigma2(rvm_N(blk),Ls)
    # theta-only: compare zeta to theta-unfolded GUE-on-backbone (both bespoke, apples-to-apples)
    band=np.array([sigma2(rvm_N(gue_bb()),Ls) for _ in range(30)]); bm,bs=band.mean(0),band.std(0)
    dev=(st-bm)/bs
    print("  zeta Sigma^2 (theta)  :",["%.3f"%v for v in st],flush=True)
    print("  GUE band (theta)      :",["%.3f"%v for v in bm],flush=True)
    print("  (zeta-GUE)/sd [theta] :",["%+.2f"%v for v in dev]," (neg=MORE rigid)",flush=True)
    res["zeta_theta_only"]={"sigma2_theta":st.tolist(),"gue_band_mean":bm.tolist(),"gue_band_sd":bs.tolist(),"dev_over_sd":dev.tolist()}
json.dump(res,open(os.path.join(HERE,"phase3b_curvature_measured.json"),"w"),indent=2)
print("\nDONE",flush=True)
