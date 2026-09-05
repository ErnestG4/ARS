"""Session F — curve point-counter over F_p (genus 1, 2), the new machinery for the genus>0 FF calibrator.
CERTIFIED-BEFORE-TRUSTED: Hasse-Weil + RH-for-curves gates (both provable, Weil) + validation vs known a_p /
brute force. Direct enumeration only (SEA out of scope). BASE_SEED=20240517.
"""
import numpy as np

def legendre(a,p):
    a%=p
    if a==0: return 0
    return 1 if pow(a,(p-1)//2,p)==1 else -1

# ---------------- genus 1: y^2 = x^3 + a x + b ----------------
def count_g1_affine(a,b,p):
    """#affine points of y^2=x^3+ax+b over F_p (no point at infinity)."""
    n=0
    for x in range(p):
        rhs=(x*x*x + a*x + b)%p
        n += 1 + legendre(rhs,p)      # #y with y^2=rhs = 1+legendre (2 if QR, 1 if 0, 0 if non-QR)
    return n
def g1_Nv(a,b,p,vmax=6):
    """N_v = #E(F_{p^v}) for v=1..vmax via Frobenius. N_1 = #affine + 1 (point at infinity)."""
    assert (4*a*a*a+27*b*b)%p!=0, "singular curve"
    N1=count_g1_affine(a,b,p)+1
    ap=p+1-N1                         # trace of Frobenius
    # alpha+beta=ap, alpha*beta=p ; s_v=alpha^v+beta^v : s_v=ap*s_{v-1}-p*s_{v-2}
    s=[2,ap]
    for v in range(2,vmax+1): s.append(ap*s[v-1]-p*s[v-2])
    Nv=[p**v + 1 - s[v] for v in range(1,vmax+1)]
    return dict(N1=N1, ap=ap, Nv=Nv, power_sums=s[1:vmax+1], genus=1, p=p)

# ---------------- genus 2: y^2 = f(x), deg f = 5 (odd, one point at infinity) ----------------
def count_g2_affine(fc,p):
    """#affine points of y^2=f(x), fc = coeffs low->high."""
    n=0
    for x in range(p):
        rhs=0
        for c in reversed(fc): rhs=(rhs*x+c)%p
        n += 1 + legendre(rhs,p)
    return n
def _squarefree(f,p):
    """Is f squarefree over F_p, i.e. deg gcd(f,f')==0? Added 2026-09-05.

    WHY: g2_Nv previously asserted only degree and leading coefficient, so a
    SINGULAR f -- y^2=x^5+x^3=x^3(x^2+1), say -- returned confidently wrong N_v
    instead of failing. MORNING_F records singular curves being "filtered by a
    squarefree-f check", so Session F did that in its driver; the driver was
    never committed, and the check left the repo with it. An importer who does
    not know to filter is caught only when a Weil gate happens to notice, and
    Hasse-Weil is a loose bound, so sometimes it does not. Found by running the
    module on an unfiltered family (approximability/F_reproduce.py): two of 246
    cases failed gates that are theorems, and both were that same singular
    curve.

    This guard cannot change a correct result -- every smooth input is
    unaffected -- it only converts a silent wrong answer into a raise."""
    def trim(a):
        while a and a[-1]%p==0: a=a[:-1]
        return [c%p for c in a]
    def rem(a,b):
        a=a[:]; db=len(b)-1; inv=pow(b[-1],p-2,p)
        for i in range(len(a)-1,db-1,-1):
            c=(a[i]*inv)%p
            for j in range(db+1): a[i-db+j]=(a[i-db+j]-c*b[j])%p
        return trim(a)
    a,b=trim(list(f)),trim([(i*c)%p for i,c in enumerate(f)][1:])
    while b: a,b=b,rem(a,b)
    return max(len(a)-1,0)==0

def g2_Nv(fc,p,vmax=6):
    """genus-2 (deg f=5): 1 point at infinity. Need N1,N2 to fix the deg-4 L-poly, then all N_v."""
    assert len(fc)==6 and fc[5]%p!=0, "need deg-5 monic-ish f"
    assert _squarefree(fc,p), "singular curve: f is not squarefree mod p"
    N1=count_g2_affine(fc,p)+1
    # N2: count over F_{p^2}. Direct enumeration in F_{p^2} via a quadratic non-residue extension.
    N2=count_g2_over_Fp2(fc,p)+1
    # power sums s_v = sum alpha_i^v (i=1..4); N_v = p^v + 1 - s_v
    s1=p+1-N1
    s2=p*p+1-N2
    # elementary symmetric via Newton: e1=s1; s2 = e1*s1 - 2 e2 => e2=(e1*s1 - s2)/2
    assert (s1*s1 - s2) % 2 == 0, "N2 parity — miscount"
    e1=s1; e2=(e1*s1 - s2)//2
    # functional equation (genus 2): e3 = p*e1, e4 = p^2  (roots come in pairs alpha, p/alpha)
    e3=p*e1; e4=p*p
    # power sums via CORRECT Newton's identities (k<=4 carry the k*e_k correction term):
    #   p1=e1; p2=e1 p1 - 2 e2; p3=e1 p2 - e2 p1 + 3 e3; p4=e1 p3 - e2 p2 + e3 p1 - 4 e4;
    #   p_k = e1 p_{k-1} - e2 p_{k-2} + e3 p_{k-3} - e4 p_{k-4}  (k>=5)
    S=[0]*(vmax+1)              # S[v] = s_v, v=1..vmax
    S[1]=e1
    if vmax>=2: S[2]=e1*S[1]-2*e2
    if vmax>=3: S[3]=e1*S[2]-e2*S[1]+3*e3
    if vmax>=4: S[4]=e1*S[3]-e2*S[2]+e3*S[1]-4*e4
    for k in range(5,vmax+1): S[k]=e1*S[k-1]-e2*S[k-2]+e3*S[k-3]-e4*S[k-4]
    assert vmax<2 or S[2]==s2, "power-sum inconsistency vs N2"   # consistency gate
    Nv=[p**v+1-S[v] for v in range(1,vmax+1)]
    return dict(N1=N1,N2=N2,Nv=Nv,power_sums=S[1:vmax+1],e=[e1,e2,e3,e4],genus=2,p=p)

def count_g2_over_Fp2(fc,p):
    """#affine points over F_{p^2}=F_p[t]/(t^2-nr). Elements a+bt; count y with y^2=f(x)."""
    nr=next(k for k in range(2,p) if legendre(k,p)==-1)   # a non-residue
    # F_{p^2} arithmetic on pairs (a,b) meaning a+b*t, t^2=nr
    def mul(u,v):
        a,b=u; c,d=v; return ((a*c+b*d%p*nr)%p, (a*d+b*c)%p)
    def add(u,v): return ((u[0]+v[0])%p,(u[1]+v[1])%p)
    els=[(a,b) for a in range(p) for b in range(p)]
    # precompute squares map: value -> count of y with y^2=value
    sqcount={}
    for y in els:
        y2=mul(y,y); sqcount[y2]=sqcount.get(y2,0)+1
    n=0
    for x in els:
        # rhs = f(x) in F_{p^2}
        rhs=(0,0); xp=(1,0)
        for c in fc:
            rhs=add(rhs,mul((c%p,0),xp)); xp=mul(xp,x)
        n+=sqcount.get(rhs,0)
    return n

# ---------------- provable gates ----------------
def hasse_weil_gate(res, vmax=6):
    g=res['genus']; p=res['p']; ok=True
    for v,Nv in enumerate(res['Nv'][:vmax],start=1):
        bound=2*g*p**(v/2.0)
        if abs(Nv-(p**v+1))>bound+1e-9: ok=False
    return ok
def rh_gate(res):
    """L-poly roots (Frobenius eigenvalues) all have |alpha|=sqrt(p)."""
    p=res['p']
    if res['genus']==1:
        ap=res['ap']; disc=ap*ap-4*p
        # roots of T^2-ap T + p ; |root|=sqrt(p) iff disc<=0
        return disc<=0
    else:
        e1,e2,e3,e4=res['e']
        # char poly of Frobenius: T^4 - e1 T^3 + e2 T^2 - e3 T + e4 ; check all roots modulus sqrt(p)
        roots=np.roots([1,-e1,e2,-e3,e4])
        return bool(np.all(np.abs(np.abs(roots)-np.sqrt(p))<1e-6*np.sqrt(p)))
