# Near-palindrome census among good fractions a/q: outer match length j = max{j: a_i = a_{L+1-i}, i<=j}.
import numpy as np, sys
sys.path.insert(0,'.')
from pp_fold import maxpq, isprime, D
from math import gcd
def cf(a,q):
    ds=[]
    while a: ds.append(q//a); q,a=a,q%a
    return ds
def census(q,N):
    a=np.arange(1,q,dtype=np.int64); a=a[np.gcd(a,q)==1]
    m=maxpq(q); good=a[m<=N]
    near=0
    for x in good:
        w0=cf(int(x),q); best=False
        for w in (w0, w0[:-1]+[w0[-1]-1,1]):
            L=len(w); j=0
            while j<L//2 and w[j]==w[L-1-j]: j+=1
            if j>=L//2-TH and L>=8: best=True
        near+=best
    return len(good), near, len(a)
def nbr(q,k=4):
    nb=[];d=1
    while len(nb)<k:
        for c in (q-d,q+d):
            if isprime(c) and len(nb)<k: nb.append(c)
        d+=1
    return nb
N=int(sys.argv[1]); TH=int(sys.argv[2])
e=2*D[N]-1
groups={"prime p^2":[p*p for p in range(317,1000) if isprime(p)][::10],
        "even r^2":[r*r for r in range(318,1000,2) if not isprime(r//2) or True][::30],
        "odd composite r^2":[r*r for r in range(319,1000,2) if not isprime(r)][::12]}
for g,qs in groups.items():
    ex=[];nr=[];nn=[]
    for q in qs:
        c,near,ph=census(q,N)
        nb=nbr(q)
        cn=[census(b,N) for b in nb]
        Kq=c*q/ph/q**e
        Kb=np.mean([cc*b/pp/b**e for (cc,_,pp),b in zip(cn,nb)])
        ex.append(Kq-Kb); nr.append(near*q/ph/q**e); nn.append(np.mean([nn_*b/pp/b**e for (_,nn_,pp),b in zip(cn,nb)]))
    ex=np.array(ex);nr=np.array(nr);nn=np.array(nn)
    print(f"N={N} {g}: n={len(qs)} excess={ex.mean():.4f}+-{ex.std()/np.sqrt(len(ex)):.4f}; near-palindromes(K units) q={nr.mean():.4f}, nbr primes={nn.mean():.4f}; excess-(near_q-near_nbr)={(ex-nr+nn).mean():.4f}+-{(ex-nr+nn).std()/np.sqrt(len(ex)):.4f}",flush=True)
