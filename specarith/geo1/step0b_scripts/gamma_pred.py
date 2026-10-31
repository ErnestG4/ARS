# Peter's Euler product gamma(r)+1 = prod_p (1 + sum_{b>=1} A_r(p^b)), evaluated numerically.
import numpy as np, sys
sys.path.insert(0, sys.argv[1])
from check_local import A_peter
P=int(sys.argv[2]); R=list(range(0,int(sys.argv[3])+1))
sieve=np.ones(P+1,bool); sieve[:2]=False
for i in range(2,int(P**.5)+1):
    if sieve[i]: sieve[i*i::i]=False
primes=np.nonzero(sieve)[0]
logprod={r:0.0 for r in R}
for p in primes:
    p=int(p)
    if p>2:
        n=np.arange(p,dtype=np.int64)
        chi=np.full(p,-1,np.int64); chi[(n*n)%p]=1; chi[0]=0
        base=(n*n-4)%p
    for r in R:
        if p==2:
            s=sum(A_peter(r,2,b) for b in range(1,64))
        else:
            v=(base*(((n+r)*(n+r)-4)%p))%p
            S=int(chi[v].sum())
            s=(p*S-1)/(p*p-1)**2
            b=2
            while True:
                pb1=p**(b-1)
                if r!=0 and pb1>abs(r)+4: break
                if r==0 and p**(-2*b)<1e-20: break
                s+=A_peter(r,p,b); b+=1
        logprod[r]+=np.log1p(s)
for r in R:
    print(r, f"{np.expm1(logprod[r]):.6f}")
