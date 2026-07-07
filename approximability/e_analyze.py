"""Session I — e-as-magnitude-probe: unseal + analysis. Runs once e_W_deep.json lands.
Tightenings folded in: (1) f-conditioning on the primary a_prev regression; (2) deflated-n honesty
(effective n = distinct a=1 steps per class, not inflated); (3) a=1 boundary reduction already checked
(g~=factor/λ one continuous surface, H_direction_law boundary gap 0.0014)."""
import json,sys,math; import numpy as np, mpmath as mp
sys.path.insert(0,'.'); from task1_pi_depth5 import cf_frac, convergents
mp.mp.dps=120; LAM=8.0
e=mp.e; cf=cf_frac(e,20); ps,qs=convergents(cf); qs=[int(x) for x in qs]
W={int(k):v for k,v in json.load(open('e_W_cheap.json'))['W'].items()}
for k,v in json.load(open('e_W_deep.json')).items(): W[int(k)]=v['W']   # merge deep n=13,14

def estep(n):
    f=qs[n-2]/qs[n]; factor=W[n-1]/W[n]
    cls='post-big' if cf[n-1]>1 else ('pre-big' if cf[n+1]>1 else 'flat')
    return dict(n=n,a=cf[n],a_prev=cf[n-1],a_next=cf[n+1],cls=cls,f=f,factor=factor,g=factor/LAM)
a1_steps=[estep(n) for n in [3,5,6,8,9,11,12,14] if (n-1 in W and n in W)]
a2_steps=[estep(n) for n in [4,7,10,13] if (n-1 in W and n in W)]

# sealed g(1,f) curve (raw factor), from pi+fifth ONLY; convert to g~=factor/λ
seal=json.load(open('H_phi_prediction_SEALED.json')); curve=np.array(seal['sealed_g1_curve'])
def g1_sealed(f): return float(np.exp(np.interp(f, curve[:,0], np.log(curve[:,1]))))/LAM   # g~ units

print("=== e a=1 steps (blind), residual vs SEALED g~(1,f) curve (pi+fifth only) ===")
print(f"  {'n':>3} {'class':>9} {'a_prev':>6} {'a_next':>6} {'f':>6} {'g~_meas':>8} {'g~_seal':>8} {'resid':>7}")
for s in a1_steps:
    gs=g1_sealed(s['f']); s['resid']=s['g']-gs
    print(f"  {s['n']:>3} {s['cls']:>9} {s['a_prev']:>6} {s['a_next']:>6} {s['f']:>6.3f} {s['g']:>8.4f} {gs:>8.4f} {s['resid']:>+7.4f}")

# PRIMARY: post-big class residual vs a_prev, f-conditioned
post=[s for s in a1_steps if s['cls']=='post-big']
print(f"\n=== PRIMARY: post-big class ({len(post)} pts, a_prev={[s['a_prev'] for s in post]}), residual vs a_prev conditioned on f ===")
ap=np.array([s['a_prev'] for s in post]); rs=np.array([s['resid'] for s in post]); fs=np.array([s['f'] for s in post])
print(f"  g~ values: {[round(s['g'],4) for s in post]} (raw factor {[round(s['factor'],3) for s in post]})")
print(f"  residual range: [{rs.min():+.4f}, {rs.max():+.4f}]  span={rs.max()-rs.min():.4f}")
# simple slope resid vs a_prev (deflated n honesty)
if len(post)>=3:
    slope_ap=np.polyfit(ap,rs,1)[0]
    # partial: regress out f first
    rf=rs-np.polyfit(fs,rs,1)[0]*(fs-fs.mean()) if np.ptp(fs)>0 else rs
    slope_ap_condf=np.polyfit(ap,rf,1)[0] if np.ptp(ap)>0 else 0
    print(f"  slope(resid vs a_prev)={slope_ap:+.5f}/unit ; after conditioning on f: {slope_ap_condf:+.5f}/unit")
    print(f"  NOTE deflated-n: {len(post)} points, a_prev & f anti-correlated (r={np.corrcoef(ap,fs)[0,1]:+.2f}) => aliased; interpret span not slope")

# POOLED a=1 universality: pi+fifth+e on one g~(1,f)?
bank=json.load(open('H_direction_law.json'))
pool=[]
for sub in ('pi','fifth'):
    for r in bank[sub]['rows']:
        if r['a']==1: pool.append((sub,r['f'],r['factor']/LAM))
for s in a1_steps: pool.append(('e',s['f'],s['g']))
print(f"\n=== POOLED a=1 universality (pi+fifth+e, {len(pool)} pts): one g~(1,f) curve? ===")
pf=np.array([p[1] for p in pool]); pg=np.array([p[2] for p in pool])
# smooth 3-param fit g~ = A*f^B (through low-f) -- residual scatter by substrate
order=np.argsort(pf); coef=np.polyfit(pf,pg,3)
resid_pool=pg-np.polyval(coef,pf)
for sub in ('pi','fifth','e'):
    m=[i for i,p in enumerate(pool) if p[0]==sub]
    print(f"  {sub:>6}: n={len(m)} resid RMS={np.sqrt(np.mean(resid_pool[m]**2)):.4f} mean={np.mean(resid_pool[m]):+.4f}")
print(f"  pooled resid RMS={np.sqrt(np.mean(resid_pool**2)):.4f} (universal if e's RMS ~ pi/fifth and no substrate mean-offset)")

# a>=2 corroboration
print(f"\n=== a>=2 corroboration: e metallic g~(a) ===")
for s in a2_steps: print(f"  a={s['a']:>2} f={s['f']:.3f} g~={s['g']:.4f} (raw {s['factor']:.3f})")
print(f"  pi/fifth large-a g~~1.0; a=2 split pi 0.844 vs fifth 0.52-0.68 -- e's spine (4,6,8,10) is all SATURATED, does NOT sample a=2")

# retro: pi/fifth a=1 resid vs their neighborhood magnitude
print(f"\n=== RETRO-check: pi/fifth a=1 residual vs neighbor magnitude ===")
pineigh={0.062:(15,292),0.003:(292,1),0.499:(1,1),0.334:(1,2)}  # f:(a_prev,a_next) pi a3,a5,a6,a7
fifneigh={0.226:(3,5),0.287:(2,1),0.416:(1,None)}               # fifth a6,a12,a13
for sub,nn in (('pi',pineigh),('fifth',fifneigh)):
    for r in bank[sub]['rows']:
        if r['a']==1:
            key=min(nn.keys(),key=lambda k:abs(k-r['f'])); apr,anx=nn[key]
            gs=g1_sealed(r['f']); print(f"  {sub} f={r['f']:.3f} a_prev={apr} a_next={anx} resid={r['factor']/LAM-gs:+.4f}")

out=dict(a1_steps=a1_steps,post_big=post,pooled_resid_by_sub={},a2=a2_steps)
json.dump(out, open('e_analysis.json','w'), indent=1, default=float)
print("\nwrote e_analysis.json")
