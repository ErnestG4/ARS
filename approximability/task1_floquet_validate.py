import os
import sys, math, time
sys.path.insert(0,os.path.expandvars("$HOME/fmexplorer/mathtest"))
sys.path.insert(0,os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))
import numpy as np
from numpy.linalg import eigvalsh
from refsuite.d1_fibonacci import fibonacci_word, fib, discriminant, _bands_from_grid

def floquet_bands_from_V(V):
    q=len(V); H=np.zeros((q,q)); np.fill_diagonal(H,V)
    idx=np.arange(q-1); H[idx,idx+1]=1.0; H[idx+1,idx]=1.0
    Hp=H.copy(); Hp[0,q-1]=1.0;  Hp[q-1,0]=1.0
    Ha=H.copy(); Ha[0,q-1]=-1.0; Ha[q-1,0]=-1.0
    edges=np.sort(np.concatenate([eigvalsh(Hp),eigvalsh(Ha)]))
    return [(edges[2*j],edges[2*j+1]) for j in range(q)]

# ---------- GOLDEN CROSS-CHECK vs trusted refsuite discriminant grid ----------
print("=== GOLDEN: Floquet(word) vs refsuite discriminant-grid ===")
lam=8.0
for k in (8,10,12):
    w=fibonacci_word(k); q=len(w); assert q==fib(k)
    V=np.array([lam if c=='a' else 0.0 for c in w])
    fb=floquet_bands_from_V(V)
    # refsuite trusted grid bands (fine)
    E=np.linspace(-2.5,lam+2.5, 4_000_000)
    with np.errstate(over="ignore",invalid="ignore"):
        D=discriminant(E,k,lam)
    gb=_bands_from_grid(E,D)
    # match: for each grid band, nearest floquet band-center distance
    fc=np.array([(lo+hi)/2 for lo,hi in fb]); gc=np.array([(lo+hi)/2 for lo,hi in gb])
    maxd=0.0
    for c in gc:
        maxd=max(maxd, float(np.min(np.abs(fc-c))))
    tw_f=sum(hi-lo for lo,hi in fb); tw_g=sum(hi-lo for lo,hi in gb)
    print(f"k={k} F_k={q}: floquet_bands={len(fb)} grid_bands={len(gb)} "
          f"(grid resolves {len(gb)}/{q}) max_center_mismatch(gridband->floquet)={maxd:.2e} "
          f"totwidth floquet={tw_f:.6e} grid={tw_g:.6e}")

# ---------- pi MIDPOINT certification (robust, no edge-sensitivity) ----------
print("\n=== pi: midpoint certification of Floquet bands (band mid ->|disc|<=2, gap mid ->>2) ===")
def cf_conv(al):
    ps=[1,0];qs=[0,1];o=[]
    for a in al: ps=[ps[1],a*ps[1]+ps[0]];qs=[qs[1],a*qs[1]+qs[0]];o.append((ps[1],qs[1]))
    return o
def potV(p,q,lam):
    V=lam*(((np.arange(q)*p)%q)>=(q-p)).astype(float)
    assert int(round(V.sum()/lam))==p
    return V
def disc_scalar(E,V):
    q=len(V);m=np.array([[E-V[0],-1.0],[1.0,0.0]])
    for n in range(1,q):
        m=np.array([[E-V[n],-1.0],[1.0,0.0]])@m
        if not np.isfinite(m).all(): return math.inf
    return m[0,0]+m[1,1]
for (p,q) in cf_conv([7,15,1,292])[:3]:
    V=potV(p,q,lam); fb=floquet_bands_from_V(V)
    band_ok=sum(1 for lo,hi in fb if abs(disc_scalar((lo+hi)/2,V))<=2.0+1e-6)
    gaps=[( fb[j][1], fb[j+1][0]) for j in range(len(fb)-1) if fb[j+1][0]-fb[j][1]>1e-12]
    gap_ok=sum(1 for lo,hi in gaps if abs(disc_scalar((lo+hi)/2,V))>2.0)
    print(f"q={q} p={p}: band-mid |disc|<=2: {band_ok}/{len(fb)}   gap-mid |disc|>2: {gap_ok}/{len(gaps)}")
