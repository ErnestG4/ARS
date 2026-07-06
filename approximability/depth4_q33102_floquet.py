"""Depth-4 pi approximant (q=33102, includes a_4=292) spectral dimension via
Floquet periodic/antiperiodic dense eigensolve (overwrite_a=True -> in-place
tridiagonalization, ~8.8GB peak). Certified method (see task1_floquet_depths123).
Runs lam=8 only (primary 292 pre-registration). Seed 20240517."""
import sys, math, json, time, gc
sys.path.insert(0,"/home/combust/fmexplorer/riemann_explorer")
import numpy as np
import scipy.linalg as sla
sys.path.insert(0,".")
from task1_pi_depth5 import potential, cf_frac, convergents
import mpmath as mp; mp.mp.dps=80

t0=time.time()
cf=cf_frac(mp.pi,12); ps,qs=convergents(cf)
p,q = ps[3], qs[3]   # depth-4: (4687, 33102)
lam=8.0
V=potential(p,q,lam)              # asserts impurity count == p == 4687
assert q==33102 and p==4687, (p,q)
print(f"[{time.time()-t0:.0f}s] potential built q={q} p={p} impurities={int(V.sum()/lam)}", flush=True)

def periodic_edges(V, corner):
    q=len(V)
    H=np.zeros((q,q), dtype=np.float64)
    np.fill_diagonal(H,V)
    idx=np.arange(q-1); H[idx,idx+1]=1.0; H[idx+1,idx]=1.0
    H[0,q-1]=corner; H[q-1,0]=corner
    w=sla.eigvalsh(H, overwrite_a=True, driver='evr')  # MRRR: fast + low-workspace (eigvals only), in-place tridiag
    del H; gc.collect()
    return w

print(f"[{time.time()-t0:.0f}s] solving periodic (corner=+1)...", flush=True)
ep=periodic_edges(V, +1.0)
print(f"[{time.time()-t0:.0f}s] periodic done. solving antiperiodic (corner=-1)...", flush=True)
ea=periodic_edges(V, -1.0)
print(f"[{time.time()-t0:.0f}s] antiperiodic done.", flush=True)

edges=np.sort(np.concatenate([ep,ea]))
np.save("depth4_q33102_edges.npy", edges)             # for later diagnostics/reruns
widths=edges[1::2]-edges[0::2]                          # band widths (q of them)
gaps=edges[2::2]-edges[1:-1:2]                          # gap widths (q-1 of them)
nb=widths.size; tw=float(widths.sum()); mw=tw/nb
dim=math.log(nb)/math.log(1.0/mw)
# HONEST resolution caveat: eigenvalue precision ~ eps*||H|| ~ 1e-13*lam. Bands
# narrower than that are width-unreliable (though they contribute negligibly to tw).
prec=np.finfo(float).eps*(lam+2.0)
out=dict(seed=20240517, q=q, p=p, lam=lam, bands=nb, count_eq_q=(nb==q),
         total_width=tw, mean_width=mw, dim=dim, dim_x_lnlam=dim*math.log(lam),
         width_min=float(widths.min()), width_med=float(np.median(widths)),
         width_max=float(widths.max()), n_bands_below_prec=int((widths<prec).sum()),
         eig_prec_est=float(prec), n_closed_gaps=int((gaps<prec).sum()),
         frac_width_in_narrow=float(widths[widths<1e-8].sum()/tw),
         wall_s=time.time()-t0)
json.dump(out, open("depth4_q33102_floquet.json","w"), indent=1)
print("RESULT", json.dumps(out), flush=True)
print("DONE", flush=True)
