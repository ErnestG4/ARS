"""BLIND measurement of the fifth (log2 3/2) dim at depths 10-13 (beyond the old q=15601 frontier),
via the certified fast solver. Pipeline FROZEN: bands_W_fast -> dim = ln q/ln(q/W). Seal NOT opened here."""
import sys,math,json,time; import numpy as np, mpmath as mp
sys.path.insert(0,'.')
from task1_pi_depth5 import potential, cf_frac, convergents
from sparse_floquet_fast import bands_W_fast, inertia_nb
mp.mp.dps=60
A=cf_frac(mp.log(mp.mpf(3)/2)/mp.log(2),16); ps,qs=convergents(A)
DEPTHS={10:(ps[9],qs[9]),11:(ps[10],qs[10]),12:(ps[11],qs[11]),13:(ps[12],qs[12])}
LAM=8.0
_=bands_W_fast(potential(ps[5],qs[5],LAM))   # warm JIT (q=53)
out={"substrate":"fifth log2(3/2)","lambda":LAM,"note":"BLIND — seal not opened","depths":{}}
for d,(p,q) in DEPTHS.items():
    t=time.time(); V=potential(p,q,LAM); W,nb,ep,ea=bands_W_fast(V); dt=time.time()-t
    assert nb==q, f"count_eq_q FAIL depth {d}: {nb}!={q}"
    hi=float(V.max())+2.5
    assert inertia_nb(V,hi,1.0)==q and inertia_nb(V,hi,-1.0)==q
    dim=math.log(q)/math.log(q/W)
    out["depths"][str(d)]=dict(q=int(q),p=int(p),a=int(A[d-1]),W=W,dim=dim,count_eq_q=True,wall_s=dt)
    print(f"depth {d}: q={q:>7} a={A[d-1]} count_eq_q=True W={W:.8e} dim={dim:.5f} [{dt:.0f}s]",flush=True)
    json.dump(out,open("G_fifth_measured.json","w"),indent=1)
print("BLIND MEASUREMENT COMPLETE. wrote G_fifth_measured.json (seal still sealed)")
