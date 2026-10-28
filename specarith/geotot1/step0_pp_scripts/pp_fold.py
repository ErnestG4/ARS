# For q=p^2, p in [317,997]: c_N(q) by vectorised Euclid; compare K(p^2) with nearby primes, and with folded count F_N(p).
import numpy as np, sys
from math import gcd
D={3:0.70566090802873823,4:0.78894555748315397,5:0.83682944368120882}
def maxpq(q):
    a=np.arange(1,q,dtype=np.int64); a=a[np.gcd(a,q)==1]
    x=np.full(a.shape,q,dtype=np.int64); y=a.copy(); m=np.zeros(a.shape,dtype=np.int64)
    # a/q: first quotient q//a ...
    num=a.copy(); den=np.full(a.shape,q,dtype=np.int64)  # fraction num/den <1
    act=num>0
    while act.any():
        qq=den[act]//num[act]; r=den[act]%num[act]
        m[act]=np.maximum(m[act],qq)
        den[act]=num[act]; num[act]=r
        act=num>0
    return m
def cf(a,q):
    ds=[]
    while a: ds.append(q//a); q,a=a,q%a
    return ds
def F(p,N):
    # folded members: a/p in E_N canonical with b_s+1<=N; last digit of folded word is b_1 (if s>1) -> if b_1==1 need b_2+1<=N
    cnt=0
    for a in range(1,p):
        if gcd(a,p)!=1: continue
        b=cf(a,p)
        if max(b)>N: continue
        w=b[:-1]+[b[-1]+1,b[-1]-1]+b[-2::-1]
        if w[-1]==1: w=w[:-2]+[w[-2]+1]
        if max(w)<=N: cnt+=1
    return cnt
def isprime(n):
    if n<2: return False
    i=2
    while i*i<=n:
        if n%i==0: return False
        i+=1
    return True
def _main():
  pass
if __name__=="__main__":
    ps=[p for p in range(317,998) if isprime(p)]
    step=int(sys.argv[1]) if len(sys.argv)>1 else 1
    ps=ps[::step]
    rows=[]
    for p in ps:
        q=p*p
        m=maxpq(q); phi=len(m)
        # 4 nearest primes
        nb=[]; k=1
        while len(nb)<4:
            for c in (q-k,q+k):
                if isprime(c) and len(nb)<4: nb.append(c)
            k+=1
        mnb=[maxpq(c) for c in nb]
        row=[p]
        for N in (3,4,5):
            e=2*D[N]-1
            Kq=(m<=N).sum()*q/phi/q**e
            Kn=np.mean([(mm<=N).sum()*c/len(mm)/c**e for mm,c in zip(mnb,nb)])
            Fp=F(p,N)*q/phi/q**e
            row+= [Kq-Kn, Fp]
        rows.append(row); print(*[f"{v:.4f}" if isinstance(v,float) else v for v in row], flush=True)
    R=np.array(rows,dtype=float)
    for i,N in enumerate((3,4,5)):
        ex=R[:,1+2*i]; fp=R[:,2+2*i]
        print(f"N={N}: n={len(R)} mean excess K(p^2)-K(4 nbr primes) = {ex.mean():.4f} +- {ex.std()/np.sqrt(len(ex)):.4f}; mean folded prediction = {fp.mean():.4f}; mean(excess - folded) = {(ex-fp).mean():.4f} +- {(ex-fp).std()/np.sqrt(len(ex)):.4f}; corr={np.corrcoef(ex,fp)[0,1]:.3f}")
