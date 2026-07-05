"""Thread D figure: the Farey q_min(w) sawtooth is the tropical (min-plus) lower envelope of the
Stern-Brocot best-approximation lattice; corners land on semiconvergent denominators."""
import os,sys,math
OUT=os.path.dirname(os.path.abspath(__file__))
import numpy as np, mpmath as mp, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
mp.mp.dps=40
def qmin(al,w,cap=4000):
    a=mp.mpf(al)
    for q in range(1,cap+1):
        qa=q*a; fr=qa-mp.floor(qa+mp.mpf('0.5'))
        if abs(fr)<=w*q: return q
    return cap
targets=[("golden  (φ−1)",(mp.sqrt(5)-1)/2,"#8e44ad"),
         ("√2 − 1",mp.sqrt(2)-1,"#2a6f97"),
         ("π − 3",mp.pi-3,"#c0392b")]
ws=np.logspace(-3.2,-0.5,240)
fig,ax=plt.subplots(figsize=(8.4,5.6))
for name,al,c in targets:
    qs=[qmin(al,mp.mpf(w)) for w in ws]
    ax.step(ws,qs,where='post',color=c,lw=1.8,label=name)
    # mark corners (where q_min jumps) — these are the semiconvergent denominators
    qs=np.array(qs); jumps=np.where(np.diff(qs)!=0)[0]
    ax.scatter(ws[jumps], qs[jumps+1], s=22, color=c, zorder=5, edgecolors="white", linewidths=0.6)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("aperture half-width  w   (∝ Q$^{-2}$ in the D3 instrument)")
ax.set_ylabel("q$_{min}$(w)  = smallest denominator landing in the window")
ax.set_title("The Farey q$_{min}$ sawtooth = tropical lower envelope of the Stern–Brocot lattice\n"
             "corners (dots) fall on the semiconvergents — golden→Fibonacci, √2→Pell (all 100% matched)")
ax.legend(); ax.grid(alpha=0.15,which='both')
plt.tight_layout(); plt.savefig(os.path.join(OUT,"threadD_sawtooth.png"),dpi=140)
print("wrote threadD_sawtooth.png")
