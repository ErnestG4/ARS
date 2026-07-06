"""Depth-5 pi approximant (q=33215, a_5=1) spectral dim via Floquet dense eigensolve.
Thread-1 PREDICTION (pre-registered): a_5=1 with older-block fraction q3/q5=113/33215=0.34%
=> total bandwidth PRESERVED (ratio W5/W4~1, deficit far below float64), dim barely moves from
depth-4's 0.6798 (like the a_3=1 step 0.6244->0.6276). Confirmation run. Seed 20240517."""
import sys, math, json, time, gc
sys.path.insert(0,"/home/combust/fmexplorer/riemann_explorer")
import numpy as np
import scipy.linalg as sla
sys.path.insert(0,".")
from task1_pi_depth5 import potential, cf_frac, convergents
import mpmath as mp; mp.mp.dps=80

t0=time.time()
cf=cf_frac(mp.pi,12); ps,qs=convergents(cf)
p,q = ps[4], qs[4]   # depth-5: q=33215, a_5=1
lam=8.0
V=potential(p,q,lam)
assert q==33215, (p,q)
print(f"[{time.time()-t0:.0f}s] potential built q={q} p={p} impurities={int(round(V.sum()/lam))}", flush=True)

def periodic_edges(V, corner):
    q=len(V); H=np.zeros((q,q), dtype=np.float64); np.fill_diagonal(H,V)
    idx=np.arange(q-1); H[idx,idx+1]=1.0; H[idx+1,idx]=1.0
    H[0,q-1]=corner; H[q-1,0]=corner
    w=sla.eigvalsh(H, overwrite_a=True, driver='evr')
    del H; gc.collect(); return w

print(f"[{time.time()-t0:.0f}s] periodic...", flush=True); ep=periodic_edges(V,+1.0)
print(f"[{time.time()-t0:.0f}s] antiperiodic...", flush=True); ea=periodic_edges(V,-1.0)
edges=np.sort(np.concatenate([ep,ea])); np.save("depth5_q33215_edges.npy", edges)
widths=edges[1::2]-edges[0::2]; gaps=edges[2::2]-edges[1:-1:2]
nb=widths.size; tw=float(widths.sum()); mw=tw/nb; dim=math.log(nb)/math.log(1.0/mw)
prec=np.finfo(float).eps*(lam+2.0)
W4=0.007434711  # banked depth-4 total width (lam=8)
out=dict(seed=20240517, q=q, p=p, lam=lam, bands=nb, count_eq_q=(nb==q),
         total_width=tw, mean_width=mw, dim=dim, dim_x_lnlam=dim*math.log(lam),
         W5_over_W4=tw/W4, dim_depth4=0.6798,
         width_med=float(np.median(widths)), n_bands_below_prec=int((widths<prec).sum()),
         frac_width_in_narrow=float(widths[widths<1e-8].sum()/tw), wall_s=time.time()-t0)
json.dump(out, open("depth5_q33215_floquet.json","w"), indent=1)
print("RESULT", json.dumps(out), flush=True); print("DONE", flush=True)
