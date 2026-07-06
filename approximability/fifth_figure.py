"""The diatonic quasicrystal assembling: band centers vs depth (the Cantor set refining),
with the major gaps of the q=53 approximant labeled by pitch class (Bellissard). lam=8."""
import os, sys, math, json
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OUT)
import numpy as np, mpmath as mp
mp.mp.dps=60
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

alpha=float(mp.log(mp.mpf(3)/2)/mp.log(2))
L=json.load(open(os.path.join(OUT,"fifth_ladder.json")))
ladder=L["ladder"]; cf=L["cf"]
depths=[q for q in ladder if q>=5]

def q2bands(lam=8.0):
    return [((lam-math.sqrt(lam*lam+16))/2,0.0),(lam,(lam+math.sqrt(lam*lam+16))/2)]

fig,ax=plt.subplots(figsize=(13,7.5))
# pitch-class gap guides from q=53 gap-labeling: k*alpha mod1 -> energy via the q=53 IDS staircase
e53=np.load(os.path.join(OUT,"fifth_edges_lam8_q53.npy"))
b53=[(e53[2*j],e53[2*j+1]) for j in range(53)]
# major gaps of q=53 and their pitch-class label (small k)
NAMES={1:"fifth (3/2)",2:"maj 2nd (2 fifths)",3:"3 fifths",4:"maj 3rd (4 fifths)"}
gapmarks=[]
for j in range(52):
    g=b53[j+1][0]-b53[j][1]; ids=(j+1)/53.0
    # nearest small k
    best=min(range(1,6),key=lambda k:min(abs((k*alpha)%1-ids),abs((k*alpha)%1-ids+1),abs((k*alpha)%1-ids-1)))
    d=min(abs((best*alpha)%1-ids),abs((best*alpha)%1-ids+1),abs((best*alpha)%1-ids-1))
    if g>0.03 and d<0.01 and best in NAMES:
        gapmarks.append(((b53[j][1]+b53[j+1][0])/2, g, best))
for xc,g,k in sorted(gapmarks,key=lambda t:-t[1])[:4]:
    ax.axvspan(xc-0.04, xc+0.04, color="#d98a3d", alpha=0.16, zorder=0)
    ax.text(xc, len(depths)-0.4, NAMES[k], rotation=90, va="top", ha="center",
            fontsize=8.5, color="#a5641f")

for yi,q in enumerate(depths):
    if q==2: bands=q2bands()
    else:
        e=np.load(os.path.join(OUT,f"fifth_edges_lam8_q{q}.npy"))
        bands=[(e[2*j],e[2*j+1]) for j in range(q)]
    centers=np.array([(lo+hi)/2 for lo,hi in bands])
    ax.scatter(centers, np.full_like(centers,yi), s=6, marker="|",
               color="#1a3d6d", linewidths=0.6, zorder=3)
    ax.text(-3.15, yi, f"q={q}", va="center", ha="right", fontsize=9)
    ai = cf[ladder.index(q)]
    ax.text(11.35, yi, f"a={ai}", va="center", ha="left", fontsize=8,
            color=("#c0392b" if ai>=5 else "#999"))

ax.set_yticks([]); ax.set_xlim(-3.5,11.9); ax.set_ylim(-0.6,len(depths)-0.2)
ax.set_xlabel("energy E   (λ=8)")
ax.set_title("The Diatonic Hamiltonian — the quasicrystal spectrum assembling along the fifth's convergents\n"
             r"$\alpha=\log_2(3/2)$; band centers per approximant. Shaded: q=53 spectral gaps labeled by pitch class (Bellissard).")
plt.tight_layout()
plt.savefig(os.path.join(OUT,"fifth_spectrum_ladder.png"),dpi=135)
print("wrote fifth_spectrum_ladder.png  gapmarks(kept):",[(round(x,3),k) for x,_,k in gapmarks])
