import sys, math, json, time
sys.path.insert(0,"/home/combust/fmexplorer/riemann_explorer")
import numpy as np
from numpy.linalg import eigvalsh
sys.path.insert(0,".")
from task1_pi_depth5 import disc_fast, disc_direct, potential, cf_frac, convergents
import mpmath as mp; mp.mp.dps=60

cf=cf_frac(mp.pi,12); ps,qs=convergents(cf)
LAMS=[8.0,24.0,32.0]

def floquet_bands(V):
    q=len(V);H=np.zeros((q,q));np.fill_diagonal(H,V)
    idx=np.arange(q-1);H[idx,idx+1]=1;H[idx+1,idx]=1
    Hp=H.copy();Hp[0,q-1]=1;Hp[q-1,0]=1
    Ha=H.copy();Ha[0,q-1]=-1;Ha[q-1,0]=-1
    e=np.sort(np.concatenate([eigvalsh(Hp),eigvalsh(Ha)]))
    return [(e[2*j],e[2*j+1]) for j in range(q)]

# ---- recursion certification vs mechanical operator (q=7 only, decisive) ----
print("=== recursion (disc_fast) certification vs mechanical Floquet midpoints, lam=8 ===")
for level,(p,q) in [(1,(ps[0],qs[0])),(2,(ps[1],qs[1])),(3,(ps[2],qs[2]))]:
    V=potential(p,q,8.0); fb=floquet_bands(V)
    mids=np.array([(lo+hi)/2 for lo,hi in fb])
    dfast=disc_fast(mids,cf,level,8.0)
    ddir=np.array([disc_direct(float(m),p,q,8.0) for m in mids])
    fast_ok=int(np.sum(np.abs(dfast)<=2.0+1e-6)); dir_ok=int(np.sum(np.abs(ddir)<=2.0+1e-6))
    print(f"  level={level} q={q}: disc_fast |.|<=2 at mech-band-mids: {fast_ok}/{len(fb)}   "
          f"disc_direct: {dir_ok}/{len(fb)}  => recursion computes mechanical op: {fast_ok==len(fb)}")

# ---- BANK Floquet dimension for pi depths 1..3 (q=7,106,113), all lambdas ----
print("\n=== BANK: pi Floquet spectral dimension, depths 1-3 (band-count==q exact) ===")
bank={"seed":20240517,"method":"floquet_periodic_antiperiodic_eigensolve",
      "certified_against":"refsuite golden k=8,10 edges 1e-8; k=12 catches 144 vs grid 98; pi midpoint 100%",
      "pi_cf":cf[:5],"convergent_q":qs[:5],"depths":{}}
for lam in LAMS:
    rec={}
    for level in (1,2,3):
        p,q=ps[level-1],qs[level-1]
        fb=floquet_bands(potential(p,q,lam))
        nb=len(fb); tw=sum(hi-lo for lo,hi in fb); mw=tw/nb
        dim=math.log(nb)/math.log(1.0/mw) if 0<mw<1 else float('nan')
        rec[f"L{level}_q{q}"]={"bands":nb,"count_eq_q":nb==q,"total_width":tw,
                               "mean_width":mw,"dim":dim,"dim_x_lnlam":dim*math.log(lam)}
    bank["depths"][f"lam{lam}"]=rec
    seq=[rec[f"L{l}_q{qs[l-1]}"]["dim"] for l in (1,2,3)]
    print(f"  lam={lam}: dims depths1-3 = {[round(x,4) for x in seq]}  (q=7,106,113)")
json.dump(bank,open("task1_floquet_depths123.json","w"),indent=1)
print("\nwrote task1_floquet_depths123.json")
