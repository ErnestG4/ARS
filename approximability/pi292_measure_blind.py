"""BLIND measurement of pi (a=292) dim at depths 6,7,8 via the certified+JIT sparse solver.
Pipeline FROZEN: bands_W_fast -> W -> dim = ln q / ln(q/W) (the certified formula). The seal is NOT
opened here — this script only measures and logs. Comparison is a separate step. main/refsuite untouched."""
import sys,time,math,json; import numpy as np, mpmath as mp
sys.path.insert(0,'.')
from task1_pi_depth5 import potential, cf_frac, convergents
from sparse_floquet_fast import bands_W_fast, inertia_nb
mp.mp.dps=60
picf=cf_frac(mp.pi,12); ps,qs=convergents(picf)
DEPTHS={6:(ps[5],qs[5]),7:(ps[6],qs[6]),8:(ps[7],qs[7])}
LAM=8.0
# warm JIT on a tiny case
_=bands_W_fast(potential(ps[2],qs[2],LAM))
out={"lambda":LAM,"note":"BLIND — seal not opened","depths":{}}
for depth,(p,q) in DEPTHS.items():
    t=time.time(); V=potential(p,q,LAM)
    W,nb,ep,ea=bands_W_fast(V); dt=time.time()-t
    assert nb==q, f"count_eq_q FAIL depth {depth}: {nb}!={q}"
    # Sylvester completeness re-assert per sector
    hi=float(V.max())+2.5
    assert inertia_nb(V,hi,1.0)==q and inertia_nb(V,hi,-1.0)==q
    dim=math.log(q)/math.log(q/W)
    out["depths"][str(depth)]=dict(q=int(q),p=int(p),W=W,dim=dim,count_eq_q=bool(nb==q),wall_s=dt)
    print(f"depth {depth}: q={q:>7} count_eq_q=True  W={W:.8e}  dim={dim:.5f}  [{dt:.0f}s]", flush=True)
    json.dump(out, open("pi292_measured.json","w"), indent=1)   # checkpoint after each depth
print("BLIND MEASUREMENT COMPLETE. wrote pi292_measured.json (seal still sealed)")
