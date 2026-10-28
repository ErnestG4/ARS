import numpy as np, sys
sys.path.insert(0,'.')
from pp_fold import maxpq, isprime, D
def fac(n):
    f=[];p=2
    while p*p<=n:
        while n%p==0: f.append(p); n//=p
        p+=1
    if n>1: f.append(n)
    return f
def base(q):
    nb=[];k=1
    while len(nb)<4:
        for c in (q-k,q+k):
            if isprime(c) and len(nb)<4: nb.append(c)
        k+=1
    return nb
cache={}
def K(q,N):
    if q not in cache:
        m=maxpq(q); cache[q]=m
    m=cache[q]; e=2*D[N]-1
    return (m<=N).sum()*q/len(m)/q**e
comp=[r for r in range(317,1000) if not isprime(r)][::8]
out=[]
for r in comp:
    q=r*r
    for lab,qq in (("sq",q),("sq-1",q-1),("sq+2",q+2)):
        nb=base(qq)
        ex=[K(qq,N)-np.mean([K(c,N) for c in nb]) for N in (3,4,5)]
        out.append((lab,r,qq,ex))
    cache.clear()
for lab in ("sq","sq-1","sq+2"):
    E=np.array([o[3] for o in out if o[0]==lab])
    print(lab, "n",len(E), "mean excess N=3,4,5:", np.round(E.mean(0),4), "+-", np.round(E.std(0)/np.sqrt(len(E)),4))
for o in out:
    if o[0]=="sq": print(o[1], fac(o[1]), np.round(o[3],3))
