"""Thread E figure: Sigma^2(L) — MG chaos reads stably rigid; the crystal spectrum's
reading diverges with unfold degree (singular density = un-readable by Family II)."""
import os,sys,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT); sys.path.insert(0,"/home/combust/fmexplorer/riemann_explorer")
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from cross_substrate.longrange_discriminator import longrange_stats
import transition_calibrators_dynamical as tcd
OUT=os.path.dirname(os.path.abspath(__file__))

def s2curve(pos, deg=None, bw=None):
    st=longrange_stats(np.sort(np.asarray(pos,float)), unfold_deg=deg, unfold_bw=bw)
    L=np.asarray(st["L"],float); s2=np.asarray(st["sigma2"],float)
    m=np.isfinite(L)&np.isfinite(s2)&(L>=1); return L[m],s2[m]

e=np.load(os.path.join(ROOT,"approximability/fifth_edges_lam8_q665.npy"))
crystal=np.sort((e[0::2]+e[1::2])/2)
mg=tcd.mackey_glass(tau=30.0,n_steps=300000,dt=0.1)
mg_ev={k:np.sort(np.asarray(fn(mg),float)) for k,fn in tcd.MACKEY_GLASS_EXTRACTORS.items()}

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5.3))
Lref=np.linspace(1,14,50)
ax1.plot(Lref,Lref,'k--',lw=1,label="Poisson  Σ²=L")
ax1.plot(Lref,(1/np.pi**2)*(np.log(2*np.pi*Lref)+0.5772+1),'k:',lw=1.2,label="GUE  ~(1/π²)lnL")
for k,ev in mg_ev.items():
    L,s2=s2curve(ev,deg=6); ax1.plot(L,s2,'-o',ms=3,color="#2a6f97",alpha=0.8,
        label=("Mackey–Glass chaos (3 extractors)" if k==list(mg_ev)[0] else None))
for deg,c in zip((4,6,12,20),["#f4a259","#e07a5f","#c0392b","#7b1e1e"]):
    L,s2=s2curve(crystal,deg=deg); ax1.plot(L,s2,'-s',ms=3,color=c,label=f"crystal, unfold deg={deg}")
ax1.set_yscale("log"); ax1.set_xlabel("L"); ax1.set_ylabel("Σ²(L)")
ax1.set_title("MG chaos reads stably RIGID (near GUE);\nthe crystal reading DIVERGES with unfold degree")
ax1.legend(fontsize=8, loc="upper left")

# panel 2: Sigma^2/L vs unfold degree
degs=[4,6,8,12,16,20,28]
cr_ratio=[];
for d in degs:
    L,s2=s2curve(crystal,deg=d); cr_ratio.append(np.mean(s2[L>=2]/L[L>=2]))
mg_ratio=[]
for k,ev in mg_ev.items():
    r=[]
    for d in degs:
        L,s2=s2curve(ev,deg=d); r.append(np.mean(s2[L>=2]/L[L>=2]))
    mg_ratio.append(r)
ax2.plot(degs,cr_ratio,'-s',color="#c0392b",lw=2,label="crystal (never converges)")
for r in mg_ratio:
    ax2.plot(degs,r,'-o',color="#2a6f97",alpha=0.8)
ax2.axhline(1,color='k',ls='--',lw=1,label="Poisson");
ax2.text(28,1.05,"Poisson",ha="right",fontsize=8)
ax2.set_yscale("log"); ax2.set_xlabel("unfold polynomial degree"); ax2.set_ylabel("⟨Σ²/L⟩")
ax2.set_title("Crystal Family-II reading is a free parameter of the unfold\n(singular density → un-readable); MG stable ~0.2 (rigid)")
ax2.legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(OUT,"threadE_rigidity.png"),dpi=140)
print("wrote threadE_rigidity.png  crystal Σ²/L by deg:",[round(x,1) for x in cr_ratio])
print("MG Σ²/L (per extractor, stable):",[[round(x,3) for x in r] for r in mg_ratio])
