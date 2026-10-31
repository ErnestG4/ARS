# Cross-check of local factors A_r(q), q = prime power, by an independent route:
# BLS (CMP 176) eq: alpha(q;r) = q |M_{q,r}| / |M_q|, M_q = SL2(Z/q), M_{q,r} = trace r.
# beta(a,q) = q^{-1} sum_r alpha(q;r) e(a r/q);  A_r(q) = sum_{(a,q)=1} |beta(a,q)|^2 e(a r / q).
# Compared against Peter's closed form (theorem, Intro) and BLS's closed form (oddprpower).
import numpy as np, sys
from fractions import Fraction
def trace_counts(q):
    # count SL2(Z/q) elements by trace, via (a,d) and counting (b,c) with bc = ad-1
    cnt_bc = np.zeros(q, dtype=np.int64)          # number of (b,c) with b*c = m mod q
    b = np.arange(q)
    for bb in range(q):
        np.add.at(cnt_bc, (bb*b) % q, 1)
    tot = np.zeros(q, dtype=np.int64)
    for a in range(q):
        d = np.arange(q)
        m = (a*d - 1) % q
        np.add.at(tot, (a+d) % q, cnt_bc[m])
    return tot
def A_route(q):
    t = trace_counts(q); M = t.sum()
    alpha = q*t/M
    r = np.arange(q)
    from math import gcd
    A = np.zeros(q)
    for a in range(1,q+1):
        if gcd(a,q)!=1: continue
        beta = (alpha*np.exp(2j*np.pi*a*r/q)).sum()/q
        A += (abs(beta)**2*np.exp(2j*np.pi*a*r/q)).real
    return A
def leg(x,p):
    x%=p
    if x==0: return 0
    return 1 if pow(x,(p-1)//2,p)==1 else -1
def A_peter(r,p,b):
    if p>2:
        if b==1:
            s=sum(leg((n*n-4)*((n+r)**2-4),p) for n in range(p))
            return (p*s-1)/(p*p-1)**2
        pb=p**b; e=leg(-1,p)**b; pre=1/((p*p-1)**2*p**(3*b-4))
        if r%pb==0: v=2*pb*(1-1/p)
        elif r%(pb//p)==0: v=-2*p**(b-1)
        elif (r-4)%pb==0 or (r+4)%pb==0: v=e*pb*(1-1/p)
        elif (r-4)%(pb//p)==0 or (r+4)%(pb//p)==0: v=-e*p**(b-1)
        else: v=0
        return pre*v
    else:
        if b==1: return (1 if r%2==0 else -1)/9
        if b==2: return (1 if r%4==0 else (-1 if r%4==2 else 0))/18
        if b in (3,5): return 0.0
        if b==4: return (1 if r%16==0 else (-1 if r%16==8 else 0))/(9*16)
        pb=2**b; pre=1/(9*2**(2*b-4)); rr=r%pb
        if rr==0: return 2*pre
        if rr==pb//2: return -2*pre
        if rr in ((4+pb//4)%pb, (-(4+pb//4))%pb): return pre
        if rr in ((4+pb//4+pb//2)%pb, (-(4+pb//4+pb//2))%pb): return -pre
        return 0.0
def A_bls(r,p,n):   # odd p, n>=2, BLS eq (oddprpower)
    pn=p**n; eps=-1 if (n%2==1 and p%4==3) else 1
    pre=1/(p**(2*n)*(1-p**-2))
    if r%pn==0: v=2*(1-1/p)
    elif r%(pn//p)==0: v=-2/p
    elif (r-4)%pn==0 or (r+4)%pn==0: v=eps*(1-1/p)
    elif (r-4)%(pn//p)==0 or (r+4)%(pn//p)==0: v=-eps/p
    else: v=0
    return pre*v
if __name__=="__main__":
    for p,bmax in [(2,7),(3,4),(5,3),(7,2),(11,2),(13,2)]:
      for b in range(1,bmax+1):
          q=p**b; A=A_route(q)
          dP=max(abs(A[r]-A_peter(r,p,b)) for r in range(q))
          line=f"p={p} b={b} q={q}: max|route-Peter|={dP:.2e}"
          if p>2 and b>=2:
              dB=max(abs(A[r]-A_bls(r,p,b)) for r in range(q))
              ratio=A[0]/A_bls(0,p,b)
              line+=f"  max|route-BLS|={dB:.2e}  route/BLS at r=0: {ratio:.6f} (1/(1-p^-2)={1/(1-p**-2):.6f})"
          print(line); sys.stdout.flush()
