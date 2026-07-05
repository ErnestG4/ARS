"""Thread C figure: F_2[T] von Mangoldt RF coefficients converge geometrically to the closed
form mu(m)/phi(m) — a conjecture-free (Weil, no RH) arithmetic ground-truth calibrator."""
import os,sys,io,contextlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from functools import lru_cache
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
with contextlib.redirect_stdout(io.StringIO()):
    import threadC_function_field as tc
OUT=os.path.dirname(os.path.abspath(__file__))
tc.setq(2); tc.irreducibles_upto.cache_clear(); irr=tc.irreducibles_upto(10)
tc.factor=lru_cache(maxsize=None)(tc.factor); tc.cm_holder=lru_cache(maxsize=None)(tc.cm_holder)
ms={1:[p for p in irr if tc.deg(p)==1][0], 2:[p for p in irr if tc.deg(p)==2][0]}
closed={d:tc.mu_poly(m)/tc.phi_poly(m) for d,m in ms.items()}
Ds=[4,6,8,10]; rel={1:[],2:[]}
for D in Ds:
    allf=[f for n in range(1,D+1) for f in tc.monics(n)]; dn=len(allf)
    for d,m in ms.items():
        a=sum(tc.vonmangoldt(f)*tc.cm_holder(m,f) for f in allf)/dn/tc.phi_poly(m)
        rel[d].append(abs(a-closed[d])/abs(closed[d]))
fig,ax=plt.subplots(figsize=(7.2,5))
for d,c in [(1,"#c0392b"),(2,"#2a6f97")]:
    ax.semilogy(Ds,rel[d],'-o',color=c,lw=2,label=f"deg(m)={d}: a$_m$→μ/φ = {closed[d]:.4f}")
ax.semilogy(Ds,[2.0**-(D-1) for D in Ds],'k:',lw=1,label=r"$\sim q^{-D}$ reference")
ax.set_xlabel("truncation degree  D  (mean over monic f, deg f ≤ D)")
ax.set_ylabel("relative error  |a$_m$ − μ(m)/φ(m)|")
ax.set_title("Function-field calibrator (F$_2$[T]): RF coefficients of the von Mangoldt Λ\n"
             "converge geometrically to the closed form — provable (Weil), no RH")
ax.legend(fontsize=9); ax.set_xticks(Ds)
plt.tight_layout(); plt.savefig(os.path.join(OUT,"threadC_convergence.png"),dpi=140)
print("wrote threadC_convergence.png  rel errors:",{d:[round(x,4) for x in rel[d]] for d in rel})
