"""Session J — blind cubic measurement. Measures W at every convergent denominator (q<CAP) for the
13-cubic pool; saves (substrate, n, a, a_prev, a_next, f, q, W) per step. No comparison to seal here (blind)."""
import sys,json; import mpmath as mp
sys.path.insert(0,'.')
from task1_pi_depth5 import potential, cf_frac, convergents
from sparse_floquet_fast import bands_W_fast
mp.mp.dps=250; LAM=8.0; CAP=60000
cubics={'cbrt2':mp.cbrt(2),'cbrt3':mp.cbrt(3),'cbrt5':mp.cbrt(5),'cbrt7':mp.cbrt(7),'cbrt6':mp.cbrt(6),
        'cbrt4':mp.cbrt(4),'cbrt9':mp.cbrt(9),'cbrt10':mp.cbrt(10),'cbrt11':mp.cbrt(11),'cbrt12':mp.cbrt(12),
        'plastic':mp.findroot(lambda x:x**3-x-1,1.3),'cbrt2p1':mp.cbrt(2)+1,
        'root_x3_3x_1':mp.findroot(lambda x:x**3-3*x-1,1.9)}
# GATE: irreducible cubic (each satisfies its minimal poly; no rational root)
polys={'cbrt2':'x^3-2','cbrt3':'x^3-3','cbrt5':'x^3-5','cbrt7':'x^3-7','cbrt6':'x^3-6','cbrt4':'x^3-4',
       'cbrt9':'x^3-9','cbrt10':'x^3-10','cbrt11':'x^3-11','cbrt12':'x^3-12','plastic':'x^3-x-1',
       'cbrt2p1':'x^3-3x^2+3x-3','root_x3_3x_1':'x^3-3x-1'}
_=bands_W_fast(potential(1,53,LAM))
def W_of(p,q):
    W,nb,ep,ea=bands_W_fast(potential(p,q,LAM)); assert nb==q,(q,nb); return W
out=[]
for name,x in cubics.items():
    cf=cf_frac(x,45); ps,qs=convergents(cf); qs=[int(v) for v in qs]
    Wc={}
    maxn=0
    for n in range(1,len(qs)):
        if qs[n]>=CAP: break
        maxn=n
    for n in range(1,maxn+1):
        Wc[n]=W_of(int(ps[n]),qs[n])
    for n in range(2,maxn):
        if n-1 not in Wc: continue
        f=qs[n-2]/qs[n]; factor=Wc[n-1]/Wc[n]
        out.append(dict(sub=name,n=n,a=cf[n],a_prev=cf[n-1],a_next=cf[n+1],
                        f=f,q=qs[n],W=Wc[n],factor=factor,g=factor/LAM))
    json.dump({'poly':polys,'steps':out}, open('J_measured.json','w'), indent=1, default=float)
    print(f"{name} ({polys[name]}): {maxn} depths, deepest q={qs[maxn]}", flush=True)
print(f"DONE: {len(out)} steps total")
