"""Thread B figure: the multiplicativity scatter a_{q1q2} vs a_{q1}a_{q2}/a_1.
Multiplicative-arithmetic substrates fall on the diagonal (R2=1); dynamical ones scatter."""
import os,sys,math,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT); sys.path.insert(0,os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import arithmetic_toolkit as at, transition_calibrators_dynamical as tcd
OUT=os.path.dirname(os.path.abspath(__file__)); QMAX=200; N=300000; rng=np.random.default_rng(20240517)

def aq_arith(fvals):
    a=np.zeros(QMAX+1)
    for q in range(1,QMAX+1): a[q]=np.mean(fvals*at.ramanujan_sum_array(q,fvals.size))/at.euler_phi(q)
    return a
def sf():
    s=np.ones(N+1,bool); s[0]=False; p=2
    while p*p<=N: s[p*p::p*p]=False; p+=1
    return s[1:N+1].astype(float)
def aq_events(t):
    t=np.sort(t); nb=int(np.ceil(t.max()-t.min()))+1; f=np.zeros(nb)
    idx=np.clip(np.floor(t-t.min()).astype(int),0,nb-1); np.add.at(f,idx,1.0); return aq_arith(f)
def pairs(a):
    a1=a[1]; xs=[];ys=[]
    for q1 in range(2,QMAX+1):
        for q2 in range(q1,QMAX//q1+1):
            if q1*q2>QMAX or math.gcd(q1,q2)!=1: continue
            xs.append(a[q1]*a[q2]/a1); ys.append(a[q1*q2])
    return np.array(xs),np.array(ys)

asf=aq_arith(sf())
mg=tcd.mackey_glass(tau=30.0,n_steps=300000,dt=0.1)
amg=aq_events(np.sort(tcd.MACKEY_GLASS_EXTRACTORS["running_mean_upcrossings"](mg)))

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12,5.3))
for ax,a,title,c in [(ax1,asf,"squarefree (multiplicative arithmetic)","#8e44ad"),
                     (ax2,amg,"Mackey–Glass chaos (dynamical)","#2a6f97")]:
    x,y=pairs(a); lim=max(np.abs(x).max(),np.abs(y).max())*1.1
    ax.plot([-lim,lim],[-lim,lim],'k--',lw=1,alpha=0.6,label="a$_{q_1q_2}$=a$_{q_1}$a$_{q_2}$/a$_1$")
    ax.scatter(x,y,s=14,color=c,alpha=0.6,edgecolors='none')
    ss=1-np.sum((y-x)**2)/np.sum((y-y.mean())**2)
    ax.set_xlabel(r"predicted  $a_{q_1}a_{q_2}/a_1$"); ax.set_ylabel(r"measured  $a_{q_1 q_2}$")
    ax.set_title(f"{title}\nKronecker R²={ss:.4f}"); ax.legend(fontsize=9); ax.set_aspect('equal','box')
    ax.set_xlim(-lim,lim); ax.set_ylim(-lim,lim)
plt.tight_layout(); plt.savefig(os.path.join(OUT,"threadB_multiplicativity.png"),dpi=140)
print("wrote threadB_multiplicativity.png")
