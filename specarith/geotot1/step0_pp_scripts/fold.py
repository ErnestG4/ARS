# Check the folding identity with X=0: [b1..b_{s-1}, b_s+1, b_s-1, b_{s-1},...,b_1] has denominator r^2 when a/r=[b1..bs].
from math import gcd
from fractions import Fraction
def cf(a,q):
    ds=[]
    while q: ds.append(a//q); a,q=q,a%q
    return ds[1:]  # drop b0=0
def val(ds):
    x=Fraction(0)
    for d in reversed(ds): x=1/(d+x)
    return x
bad=0; n=0
for r in range(3,400):
    for a in range(1,r):
        if gcd(a,r)!=1: continue
        b=cf(a,r)
        if b[-1]<2: continue
        for X in range(0,4):
            if X==0:
                w=b[:-1]+[b[-1]+1, b[-1]-1]+b[-2::-1]
                w=[d for d in w]  # b[-1]-1>=1 since canonical
            else:
                w=b+[X,1,b[-1]-1]+b[-2::-1]
            w=[d for d in w if True]
            if 0 in w: continue
            f=val(w); n+=1
            if f.denominator!=(X+1)*r*r: bad+=1
print("tested",n,"failures",bad)
# example
print(cf(3,7), val(cf(3,7)[:-1]+[cf(3,7)[-1]+1,cf(3,7)[-1]-1]+cf(3,7)[-2::-1]))
