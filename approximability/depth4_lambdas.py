"""Depth-4 q=33102 Floquet for lam in {24,32} (robustness of the depth-4 dim-rise
falsification). Sequential, one matrix at a time (~8.8GB peak). Seed 20240517."""
import sys, math, json, time, gc
sys.path.insert(0,"/home/combust/fmexplorer/riemann_explorer")
import numpy as np, scipy.linalg as sla
sys.path.insert(0,".")
from task1_pi_depth5 import potential, cf_frac, convergents
import mpmath as mp; mp.mp.dps=80
cf=cf_frac(mp.pi,12); ps,qs=convergents(cf); p,q=ps[3],qs[3]
def edges(V,corner):
    n=len(V);H=np.zeros((n,n));np.fill_diagonal(H,V)
    idx=np.arange(n-1);H[idx,idx+1]=1.0;H[idx+1,idx]=1.0
    H[0,n-1]=corner;H[n-1,0]=corner
    w=sla.eigvalsh(H,overwrite_a=True,driver='evr');del H;gc.collect();return w
for lam in (24.0,32.0):
    t0=time.time();V=potential(p,q,lam)
    print(f"lam={lam} start q={q} p={p} imp={int(V.sum()/lam)}",flush=True)
    ep=edges(V,1.0);print(f"lam={lam} periodic done {time.time()-t0:.0f}s",flush=True)
    ea=edges(V,-1.0);print(f"lam={lam} antiperiodic done {time.time()-t0:.0f}s",flush=True)
    e=np.sort(np.concatenate([ep,ea]));w=e[1::2]-e[0::2]
    nb=w.size;tw=float(w.sum());mw=tw/nb;dim=math.log(nb)/math.log(1/mw)
    out=dict(seed=20240517,q=q,p=p,lam=lam,bands=nb,count_eq_q=(nb==q),total_width=tw,
             mean_width=mw,dim=dim,dim_x_lnlam=dim*math.log(lam),
             width_med=float(np.median(w)),n_bands_below_prec=int((w<2.3e-15).sum()),
             frac_width_in_narrow=float(w[w<1e-8].sum()/tw),wall_s=time.time()-t0)
    json.dump(out,open(f"depth4_q33102_lam{int(lam)}.json","w"),indent=1)
    print("RESULT",json.dumps(out),flush=True)
print("ALL DONE",flush=True)
