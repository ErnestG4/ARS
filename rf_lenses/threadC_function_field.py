"""Thread C — function-field arithmetic calibrator over F_q[T] (Acta Math. Sinica 2022 RF theory).

Goal: a CONJECTURE-FREE arithmetic ground truth for the RF idea. In F_q[T], irreducible polys play
the role of primes, zeta is rational (Weil, no RH), and the RF/Ramanujan machinery has closed forms.
NOTE (honest scope): the toolkit's RF engine uses INTEGER Ramanujan sums c_q(n); the function-field
theory needs POLYNOMIAL Ramanujan sums c_m(f). So this is a self-contained calibrator (a new generator +
its provable checks), not a run of the integer engine.

Layers (each a provable gate):
 L0  F_q[T] arithmetic validated vs Gauss's exact irreducible count I(n)=(1/n) sum_{d|n} mu(d) q^{n/d}.
 L1  polynomial Ramanujan sum c_m(f) via Holder |d|-weighted identity; verify multiplicativity
     c_{m1 m2}=c_{m1}c_{m2} for coprime m (FF analogue of Thread B layer-zero).
 L2  RF expansion of the FF von Mangoldt Lambda; check the coefficients follow the closed form
     mu_poly(m)/phi_poly(m) (the Hardy analogue) -> the ground-truth calibration.
BASE_SEED=20240517.
"""
import os,sys,json,math,itertools
OUT=os.path.dirname(os.path.abspath(__file__))
from functools import lru_cache

# ============ F_q[T] arithmetic (q prime; polynomials as tuples of coeffs, low->high, monic normalized) ============
Q=None
def setq(q): global Q; Q=q
def deg(f):
    return len(f)-1 if f else -1
def trim(f):
    f=list(f)
    while f and f[-1]%Q==0: f.pop()
    return tuple(x%Q for x in f)
def padd(a,b):
    n=max(len(a),len(b)); r=[( (a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0))%Q for i in range(n)]
    return trim(r)
def pmul(a,b):
    if not a or not b: return ()
    r=[0]*(len(a)+len(b)-1)
    for i,ai in enumerate(a):
        if ai%Q==0: continue
        for j,bj in enumerate(b): r[i+j]=(r[i+j]+ai*bj)%Q
    return trim(r)
def pdivmod(a,b):
    a=list(trim(a)); b=trim(b); db=deg(b)
    lead_inv=pow(b[-1],Q-2,Q) if Q>2 else 1
    quo=[0]*(max(0,len(a)-len(b)+1))
    while trim(a) and deg(a)>=db:
        da=deg(a); c=(a[-1]*lead_inv)%Q; sh=da-db; quo[sh]=c
        for j in range(len(b)): a[sh+j]=(a[sh+j]-c*b[j])%Q
        a=list(trim(a))
    return trim(quo), trim(a)
def pmod(a,b): return pdivmod(a,b)[1]
def pgcd(a,b):
    a,b=trim(a),trim(b)
    while b:
        a,b=b,pmod(a,b)
    # normalize monic
    if a and a[-1]!=1:
        inv=pow(a[-1],Q-2,Q) if Q>2 else 1; a=trim([x*inv%Q for x in a])
    return a
def is_monic(f): return f and f[-1]==1
def monics(n):
    """all monic polys of degree n"""
    for coeffs in itertools.product(range(Q),repeat=n):
        yield tuple(coeffs)+(1,)
def norm(f): return Q**deg(f)          # |f| = q^{deg f}

@lru_cache(maxsize=None)
def irreducibles_upto(D):
    """list of monic irreducibles of degree 1..D by trial division"""
    irr=[]
    for n in range(1,D+1):
        for f in monics(n):
            # test irreducible: not divisible by any smaller-degree irreducible
            red=False
            for g in irr:
                if deg(g)*2>n: break
                if pmod(f,g)==(): red=True; break
            if not red: irr.append(f)
    return tuple(sorted(irr,key=lambda p:(deg(p),p)))

def gauss_count(n):
    tot=0
    for d in range(1,n+1):
        if n%d==0:
            # mobius(d)
            m=d; mu=1; p=2; ok=True
            while p*p<=m:
                if m%p==0:
                    m//=p
                    if m%p==0: mu=0; break
                    mu=-mu
                p+=1
            if mu!=0 and m>1: mu=-mu
            if mu!=0: tot+=mu*Q**(n//d)
    return tot//n

# ---------- L0: validate arithmetic via Gauss count ----------
res={}
for q in (2,3):
    setq(q); irreducibles_upto.cache_clear()
    D=6 if q==2 else 4
    irr=irreducibles_upto(D)
    by_deg={}
    for p in irr: by_deg[deg(p)]=by_deg.get(deg(p),0)+1
    checks=[(n, by_deg.get(n,0), gauss_count(n)) for n in range(1,D+1)]
    ok=all(a==b for _,a,b in checks)
    res[f"F{q}"]={"D":D,"gauss_check":checks,"L0_pass":ok}
    print(f"F_{q}[T]  irreducible counts (enumerated vs Gauss I(n)):")
    for n,a,b in checks: print(f"   deg {n}: enum={a:6d}  Gauss={b:6d}  {'OK' if a==b else 'MISMATCH'}")
    print(f"   L0 {'PASS' if ok else 'FAIL'}\n")

json.dump(res, open(os.path.join(OUT,"threadC_L0.json"),"w"), indent=1)
print("wrote threadC_L0.json")

# ============ L1: factorization, mu/phi, divisors, polynomial Ramanujan sum ============
def factor(f):
    """factor monic f into [(irr, exp)]"""
    f=trim(f); facs={}
    D=deg(f); irr=irreducibles_upto(max(1,D))
    for p in irr:
        if deg(p)>deg(f): break
        while deg(f)>=deg(p):
            q_,r_=pdivmod(f,p)
            if r_==(): f=q_; facs[p]=facs.get(p,0)+1
            else: break
    return facs   # f reduced to () means fully factored (monic)
def mu_poly(m):
    if m==(1,): return 1
    fac=factor(m)
    if any(e>1 for e in fac.values()): return 0
    return (-1)**len(fac)
def phi_poly(m):
    fac=factor(m); v=norm(m)
    for p in fac: v=v*(norm(p)-1)//norm(p)
    return v
def divisors(m):
    """all monic divisors of m"""
    fac=list(factor(m).items()); divs=[(1,)]  # the constant poly 1
    for p,e in fac:
        new=[]
        pw=(1,)
        for k in range(e+1):
            for d in divs: new.append(pmul(d,pw))
            pw=pmul(pw,p)
        divs=new
    return divs
def cm_holder(m,f):
    """polynomial Ramanujan sum via Holder: c_m(f)=sum_{d|gcd(f,m)} |d| mu(m/d)."""
    g=pgcd(f,m); s=0
    for d in divisors(g):
        q_,_=pdivmod(m,d); s+=norm(d)*mu_poly(trim(q_))
    return s
def vonmangoldt(f):
    """Lambda(f)=deg(P) if f=P^k (prime power), else 0."""
    fac=factor(f)
    if len(fac)==1:
        (p,e),=fac.items(); return deg(p)
    return 0

resB={}
for q in (2,3):
    setq(q); irreducibles_upto.cache_clear(); _=irreducibles_upto(6 if q==2 else 4)
    irr=irreducibles_upto(6 if q==2 else 4)
    # L1: multiplicativity c_{m1 m2}=c_{m1}c_{m2} for coprime m1,m2
    worst=0.0; tested=0
    ms=[p for p in irr if deg(p)<=2]
    for i in range(len(ms)):
        for j in range(len(ms)):
            m1,m2=ms[i],ms[j]
            if pgcd(m1,m2)!=(1,): continue
            m12=pmul(m1,m2)
            for f in list(monics(1))+list(monics(2))+[(0,)*0+(0,1,1)]:
                f=trim(f) if f else (0,)
                if not f: continue
                lhs=cm_holder(m12,f); rhs=cm_holder(m1,f)*cm_holder(m2,f)
                worst=max(worst,abs(lhs-rhs)); tested+=1
    # L2: RF coefficient a_m of Lambda vs closed form mu(m)/phi(m)
    D=8 if q==2 else 5
    allf=[f for n in range(1,D+1) for f in monics(n)]
    denom=len(allf)
    test_m=[(1,)]+[p for p in irr if deg(p)<=2][:6]
    rows=[]
    for m in test_m:
        num=sum(vonmangoldt(f)*cm_holder(m,f) for f in allf)
        a_m=num/denom/phi_poly(m)
        pred=mu_poly(m)/phi_poly(m)
        rows.append(dict(m_deg=deg(m), phi=phi_poly(m), a_m=a_m, closed_mu_over_phi=pred,
                         rel=abs(a_m-pred)/(abs(pred)+1e-12)))
    resB[f"F{q}"]={"L1_cm_multiplicativity_maxerr":worst,"L1_tested":tested,"D":D,"L2_rows":rows}
    print(f"\nF_{q}[T]:  L1 c_m multiplicativity max err = {worst:.2e} over {tested} (m,f) pairs")
    print(f"  L2 RF coefficients of von Mangoldt vs closed form mu(m)/phi(m)  (mean over deg f<= {D}):")
    print(f"   {'deg m':>6} {'phi(m)':>7} {'a_m(measured)':>14} {'mu/phi(closed)':>15} {'rel':>9}")
    for r in rows:
        print(f"   {r['m_deg']:>6} {r['phi']:>7} {r['a_m']:>14.6f} {r['closed_mu_over_phi']:>15.6f} {r['rel']:>9.2e}")

import json
json.dump(resB, open(os.path.join(OUT,"threadC_L1L2.json"),"w"), indent=1, default=float)
print("\nwrote threadC_L1L2.json")
