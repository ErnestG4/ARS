"""Arm 1 robustness: is the cubic gamma SPLIT stable under the unfold-degree lens parameter, or a deg=16
conditioning artifact? Recompute gamma for high-gamma (cbrt11,cbrt3,cbrt12) vs low-gamma (cbrt4,cbrt9,plastic)
cubics + golden at UDEG in {10,14,16,20}. If the ordering (high>low) holds across deg, SPLIT is real."""
import os,sys,math
_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,_ROOT); sys.path.insert(0,os.path.join(_ROOT,"cross_substrate"))
import numpy as np, mpmath as mp
mp.mp.dps=60
from cross_substrate.sturmian_hamiltonian_run import sturmian_eigs
from cross_substrate.longrange_discriminator import unfold_empirical
from cross_substrate.axes import II1_sigma2_at_L
import warnings; warnings.filterwarnings('ignore')
LAM=16.0;N=4200;L_GRID=[2.,3.,5.,8.,12.,20.,30.];SEEDS=(0.1234,0.31,0.53)
logL=np.log(L_GRID)
def gamma(alpha,udeg):
    cur=[]
    for phi in SEEDS:
        e=np.sort(np.asarray(sturmian_eigs(alpha,phi,lam=LAM,n=N),float))
        k=int(len(e)*0.12);e=e[k:len(e)-k];u=np.sort(unfold_empirical(e,udeg))
        cur.append([II1_sigma2_at_L(u,L) for L in L_GRID])
    m=np.array(cur).mean(0);return float(np.polyfit(logL,np.log(m),1)[0])
subs={'cbrt11':mp.cbrt(11),'cbrt3':mp.cbrt(3),'cbrt12':mp.cbrt(12),
      'cbrt4':mp.cbrt(4),'cbrt9':mp.cbrt(9),'plastic':mp.findroot(lambda x:x**3-x-1,1.3),'golden':(mp.sqrt(5)-1)/2}
frac=lambda x:float(mp.frac(mp.mpf(x)))
print(f"{'sub':12s} "+" ".join(f"deg{d}".rjust(7) for d in (10,14,16,20)))
rows={}
for n,x in subs.items():
    a=frac(x);gs=[gamma(a,d) for d in (10,14,16,20)];rows[n]=gs
    print(f"{n:12s} "+" ".join(f"{g:.3f}".rjust(7) for g in gs),flush=True)
# ordering check: min(high three) > max(low three) at each deg?
hi=['cbrt11','cbrt3','cbrt12'];lo=['cbrt4','cbrt9','plastic']
print("\nordering (min_high > max_low) per deg:")
for i,d in enumerate((10,14,16,20)):
    mh=min(rows[n][i] for n in hi);ml=max(rows[n][i] for n in lo)
    print(f"  deg{d}: min_high={mh:.3f} max_low={ml:.3f} -> {'SEPARATED' if mh>ml else 'OVERLAP'}")
