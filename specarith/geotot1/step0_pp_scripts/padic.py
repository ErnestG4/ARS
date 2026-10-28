# Enumerate canonical E_N fractions with denominator <= Q; test p-adic exponent dependence of c(q)*q/phi(q).
import numpy as np, sys
N=int(sys.argv[1]); Q=int(sys.argv[2])
delta={3:0.70566090802873823,4:0.78894555748315397,5:0.83682944368120882}[N]
c=np.zeros(Q+1,dtype=np.int64)
u=np.array([1]*N,dtype=np.int64); v=np.arange(1,N+1,dtype=np.int64)  # bottom rows after one digit
last=np.arange(1,N+1)
while len(v):
    m=v<=Q; u,v,last=u[m],v[m],last[m]
    canon=last>=2
    np.add.at(c,v[canon],1)
    nu=[];nv=[];nl=[]
    for a in range(1,N+1):
        nu.append(v); nv.append(a*v+u); nl.append(np.full(len(v),a))
    u=np.concatenate(nu); v=np.concatenate(nv); last=np.concatenate(nl)
# phi
phi=np.arange(Q+1,dtype=np.float64)
for p in range(2,Q+1):
    if phi[p]==p:
        phi[p::p]*= (1-1/p)
q=np.arange(Q+1,dtype=np.float64)
# check c(q) vs a few direct values
def cf_ok(a,b,N):
    ds=[]
    while b:
        ds.append(a//b); a,b=b,a%b
    return ds
import math
for qq in [97,360,1000,Q]:
    direct=sum(1 for a in range(1,qq) if math.gcd(a,qq)==1 and max(cf_ok(a,qq,N)[1:])<=N)
    assert direct==c[qq],(qq,direct,c[qq])
lo=Q//10
qs=np.arange(lo,Q+1)
K=c[qs]*qs/phi[qs]/qs**(2*delta-1)
def v_p(n,p):
    k=0
    while n%p==0: n//=p;k+=1
    return k
print("N",N,"Q",Q,"window",lo,Q,"mean K all",K.mean())
for p in (2,3,5,7):
    vals=np.array([v_p(int(x),p) for x in qs])
    row=[]
    for k in range(0,6):
        sel=vals==k if k<5 else vals>=5
        if sel.sum()>20:
            row.append(f"v={k}{'+' if k==5 else ''}: n={sel.sum()} K={K[sel].mean():.4f}+-{K[sel].std()/np.sqrt(sel.sum()):.4f}")
    print(" p=",p,"; ".join(row))
