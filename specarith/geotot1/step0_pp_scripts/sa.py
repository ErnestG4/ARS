# Strong approximation check: image of Gamma_{1,2} (det 1, products of pairs) and of G_{1..N} mod n.
import itertools, sys
def mul(A,B,n):
    a,b,c,d=A; e,f,g,h=B
    return ((a*e+b*g)%n,(a*f+b*h)%n,(c*e+d*g)%n,(c*f+d*h)%n)
def closure(gens,n):
    I=(1,0,0,1); seen={I}; frontier=[I]
    while frontier:
        nf=[]
        for X in frontier:
            for g in gens:
                Y=mul(X,g,n)
                if Y not in seen: seen.add(Y); nf.append(Y)
        frontier=nf
    return seen
def M(a): return (0,1,1,a)
def sl2size(n):
    # |SL2(Z/n)| = n^3 prod_{p|n}(1-p^-2)
    s=n**3; m=n; p=2
    ps=set()
    while p*p<=m:
        while m%p==0: ps.add(p); m//=p
        p+=1
    if m>1: ps.add(m)
    from fractions import Fraction
    f=Fraction(s)
    for p in ps: f*=Fraction(p*p-1,p*p)
    return int(f)
for n in [2,3,4,8,16,32,9,27,81,5,25,125,7,49,6,12,36,72]:
    A=[1,2]
    G2=closure([mul(M(a),M(b),n) for a in A for b in A],n)
    sizes=[len(G2)]
    for N in (3,4,5):
        GN=closure([M(a)%n if False else tuple(x%n for x in M(a)) for a in range(1,N+1)],n)
        sizes.append(len(GN))
    pm=2*sl2size(n) if n>2 else sl2size(n)
    print(n, "SL2:",sl2size(n), "Gamma12:",sizes[0], "G_N(N=3,4,5) det+-1:",sizes[1:], "expected det+-1 group:",pm)
