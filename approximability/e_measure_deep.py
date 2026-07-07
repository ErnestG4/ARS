import sys,json; import mpmath as mp
sys.path.insert(0,'.')
from task1_pi_depth5 import potential, cf_frac, convergents
from sparse_floquet_fast import bands_W_fast
mp.mp.dps=120; LAM=8.0
e=mp.e; cf=cf_frac(e,30); ps,qs=convergents(cf)
_=bands_W_fast(potential(1,53,LAM))
out={}
for n in (13,14):
    q=int(qs[n]); W,nb,ep,ea=bands_W_fast(potential(int(ps[n]),q,LAM)); assert nb==q
    out[str(n)]=dict(q=q, a=cf[n], W=W)
    json.dump(out, open('e_W_deep.json','w'), indent=1)
    print(f"n={n} q={q} W={W:.6e} DONE", flush=True)
print("deep DONE")
