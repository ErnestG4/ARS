import numpy as np, sys
sys.path.insert(0,'.')
from pp_fold import isprime
def meanS(q):
    num=np.arange(1,q,dtype=np.int64); den=np.full(num.shape,q,dtype=np.int64); s=np.zeros(num.shape,dtype=np.int64)
    act=num>0
    while act.any():
        qq=den[act]//num[act]; r=den[act]%num[act]
        s[act]+=qq; den[act]=num[act]; num[act]=r; act=num>0
    return s.mean()
a=6/np.pi**2
xs=[];ys=[]
for q0 in [1000,3000,10000,30000,100000,300000,1000000,3000000]:
    ps=[];q=q0
    while len(ps)<12:
        if isprime(q): ps.append(q)
        q+=1
    for p in ps:
        m=meanS(p); xs.append(np.log(p)); ys.append(m-a*np.log(p)**2)
    r=np.array(ys[-12:])-1.574*np.array(xs[-12:])
    print(q0, "resid vs 1.574: mean %.3f sd %.3f"%(r.mean(), r.std()))
X=np.array(xs);Y=np.array(ys)
b,g=np.polyfit(X,Y,1)
print("fit beta=%.4f gamma=%.4f"%(b,g))
