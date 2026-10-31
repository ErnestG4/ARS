import numpy as np, sys
sys.path.insert(0, sys.argv[1])
from check_local import trace_counts
from math import gcd
def primes_of(q):
    s=set(); n=q; d=2
    while d*d<=n:
        while n%d==0: s.add(d); n//=d
        d+=1
    if n>1: s.add(n)
    return s
for q in [2,3,4,5,6,8,9,12,15,16,25,27,30,32,49]:
    t=trace_counts(q); alpha=q*t/t.sum(); r=np.arange(q); md=0
    pf=np.prod([1-w**-2 for w in primes_of(q)])
    for a in range(1,q):
        if gcd(a,q)!=1: continue
        beta=(alpha*np.exp(2j*np.pi*a*r/q)).sum()/q
        K=sum(np.exp(2j*np.pi*(a*d+a*pow(d,-1,q))/q) for d in range(1,q) if gcd(d,q)==1)
        md=max(md,abs(beta-K/(q*q*pf)))
    print(q, f"{md:.2e}")
