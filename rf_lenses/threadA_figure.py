"""Thread A figure: RF power spectrum of primes (singular-series even-q structure) +
the orthogonality plane (RF arithmetic concentration vs Family-II distance-from-Poisson)."""
import os,sys,json,math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT); sys.path.insert(0,"/home/combust/fmexplorer/riemann_explorer")
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import arithmetic_toolkit as at
OUT=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(OUT,"threadA.json")))

# recompute primes a_q^2 to q=60 for the bar panel
N=300000; s=np.ones(N+1,bool); s[:2]=False; p=2
while p*p<=N:
    if s[p]: s[p*p::p]=False
    p+=1
f=s[1:N+1].astype(float); Q=60
aq2=np.array([ (np.mean(f*at.ramanujan_sum_array(q,N))/at.euler_phi(q))**2 for q in range(1,Q+1)])

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5.2))
qq=np.arange(1,Q+1); even=(qq%2==0)
ax1.bar(qq[even],aq2[even],color="#c0392b",label="even q",width=0.9)
ax1.bar(qq[~even],aq2[~even],color="#2a6f97",label="odd q",width=0.9)
ax1.set_yscale("log"); ax1.set_xlabel("q"); ax1.set_ylabel(r"RF power $a_q^2$")
ax1.set_title("Primes: RF power spectrum = Hardy–Littlewood singular series\n(even-q dominance; Family II reads these same primes as Poisson)")
ax1.legend(); ax1.set_xlim(0.5,Q+.5)

names=list(d.keys())
x=[d[n]["RF_concentration"] for n in names]
y=[d[n]["familyII_ks_poisson"] for n in names]   # distance from Poisson (small = Poisson-like)
fit=[d[n]["familyII_bestfit"] for n in names]
col={"squarefree":"#8e44ad","primes":"#c0392b","poisson_flat":"#7f8c8d","gue_wigner_unit":"#2a6f97"}
for n in names:
    ax2.scatter(d[n]["RF_concentration"], d[n]["familyII_ks_poisson"], s=140,
                color=col.get(n,"#333"), zorder=3, edgecolors="white", linewidths=1.3)
    ax2.annotate(f"{n}\n(FamII={d[n]['familyII_bestfit']})",
                 (d[n]["RF_concentration"], d[n]["familyII_ks_poisson"]),
                 textcoords="offset points", xytext=(8,6), fontsize=9)
ax2.set_xscale("log"); ax2.set_xlabel("RF arithmetic concentration  max$(a_q^2)$/median  (log)")
ax2.set_ylabel("Family II  KS-distance to Poisson")
ax2.axvspan(1e3,1e6,color="#c0392b",alpha=0.06)
ax2.set_title("Orthogonality plane: primes are RF-structured but spacing-Poisson\n(the corner where Family III independent of Family II)")
plt.tight_layout(); plt.savefig(os.path.join(OUT,"threadA_orthogonality.png"),dpi=140)
print("wrote threadA_orthogonality.png")
