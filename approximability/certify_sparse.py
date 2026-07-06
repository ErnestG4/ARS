"""Certify the sparse inertia-bisection solver against the certified dense engine on the OVERLAP.
Gate 3 (make-or-break): the new module must reproduce dense W + dim + count_eq_q at small q before it is
trusted. It does. Then the compute wall is stated (depths 6-8 do not run in-session). Dense engine untouched."""
import sys,time,math; sys.path.insert(0,'.')
import numpy as np, mpmath as mp, scipy.linalg as sla
from task1_pi_depth5 import potential, cf_frac, convergents
from sparse_floquet import bands_W
mp.mp.dps=60

def dense_Wdim(V):
    q=len(V)
    def edges(c):
        H=np.zeros((q,q)); np.fill_diagonal(H,V); idx=np.arange(q-1)
        H[idx,idx+1]=1; H[idx+1,idx]=1; H[0,q-1]=c; H[q-1,0]=c
        return np.sort(sla.eigvalsh(H))
    e=np.sort(np.concatenate([edges(1.0),edges(-1.0)])); w=e[1::2]-e[0::2]
    W=float(w.sum()); return W, math.log(q)/math.log(q/W)

if __name__=="__main__":
    picf=cf_frac(mp.pi,12); pps,pqs=convergents(picf)
    acf=cf_frac(mp.log(mp.mpf(3)/2)/mp.log(2),12); aps,aqs=convergents(acf)
    tests=[("pi",pps[2],113),("fifth",aps[aqs.index(306)],306),("fifth",aps[aqs.index(665)],665)]
    print("GATE 3 — sparse (inertia-bisection) vs certified dense, on overlap:")
    allok=True
    for tag,p,q in tests:
        V=potential(p,q,8.0)
        t=time.time(); Ws,nb=bands_W(V); ts=time.time()-t
        Wd,dimd=dense_Wdim(V); dims=math.log(q)/math.log(q/Ws)
        ok=(nb==q) and abs(Ws-Wd)/Wd<1e-6 and abs(dims-dimd)<1e-4
        allok=allok and ok
        print(f"  {tag} q={q:>4}: count_eq_q={nb==q} Wrel={abs(Ws-Wd)/Wd:.1e} "
              f"dim_sparse={dims:.5f} dim_dense={dimd:.5f} PASS={ok} [{ts:.1f}s]")
    print(f"\nGATE 3 {'PASS — module trusted on overlap' if allok else 'FAIL'}.")
    print("COMPUTE WALL: pure-Python inertia is O(q) per eval, un-vectorizable across its recurrence dim; full")
    print("extraction is O(q²·bisection-depth). q=665→7.7s ⇒ q₆=66317 ~20 h, q₈=265381 ~weeks. No JIT (numba/")
    print("cython absent). O(q) MEMORY though — the banked 'RAM wall' is solved; the real blocker is COMPUTE.")
    print("=> depths 6-8 NOT run this session. Seal stays locked. Unblock: compiled inertia (numba/cython/C).")
