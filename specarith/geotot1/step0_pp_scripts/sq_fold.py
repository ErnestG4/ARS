import numpy as np, sys
sys.path.insert(0,'.')
from pp_fold import maxpq, F, isprime, D
from math import gcd
def phi_count(q): return sum(1 for a in range(1,q) if gcd(a,q)==1)
def run(qs_r, label):
    rows=[]
    for q,r in qs_r:
        m=maxpq(q); ph=len(m)
        nb=[];k=1
        while len(nb)<4:
            for c in (q-k,q+k):
                if isprime(c) and len(nb)<4: nb.append(c)
            k+=1
        mnb=[maxpq(c) for c in nb]
        row=[]
        for N in (3,4,5):
            e=2*D[N]-1
            Kq=(m<=N).sum()*q/ph/q**e
            Kn=np.mean([(mm<=N).sum()*c/len(mm)/c**e for mm,c in zip(mnb,nb)])
            Fp=(F(r,N)*q/ph/q**e) if r else 0.0
            row+=[Kq-Kn,Fp]
        rows.append(row)
    R=np.array(rows)
    for i,N in enumerate((3,4,5)):
        ex=R[:,2*i]; fp=R[:,2*i+1]
        print(f"{label} N={N}: n={len(R)} excess={ex.mean():.4f}+-{ex.std()/np.sqrt(len(ex)):.4f} folded={fp.mean():.4f} diff={(ex-fp).mean():.4f}+-{(ex-fp).std()/np.sqrt(len(ex)):.4f}")
if __name__=="__main__":
    comp=[r for r in range(317,1000) if not isprime(r)][::4]
    run([(r*r,r) for r in comp],"composite r^2")
    cubes=[p**3 for p in range(47,100) if isprime(p)]
    run([(q,None) for q in cubes],"p^3 (no fold)")
