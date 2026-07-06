"""Session H Arm 1 — the crossover surface (a=1 slice). Fit g(1, older-block fraction) from banked
π + fifth a=1 steps ONLY, seal it, then φ (pure a=1) tests it out-of-sample.

GATE 1 (operational defs, from the certified pipeline): per convergent step,
  factor_n = W_{n-1}/W_n  (W from bands_W_fast, the certified O(q)-mem solver);
  q_growth_n = q_n/q_{n-1};  MARGIN M_n = ln(factor_n) - ln(q_growth_n).
  sign(M_n) predicts dim retreat (M>0 -> dim drops) — verified on π (all +) and the fifth (depth-12 M~0 straddle).
  For a=1 steps, factor_n IS g(1, older-block fraction q_{n-2}/q_n). BASE_SEED=20240517.
"""
import sys,math,json; import numpy as np, mpmath as mp
sys.path.insert(0,'.')
from task1_pi_depth5 import potential, cf_frac, convergents
from sparse_floquet_fast import bands_W_fast
mp.mp.dps=60; LAM=8.0

def W_of(p,q):
    W,nb,_,_=bands_W_fast(potential(p,q,LAM)); assert nb==q; return W
_=bands_W_fast(potential(1,53,LAM))  # warm

# ---- banked W (expensive depths) ----
pim=json.load(open('pi292_measured.json'))['depths']       # pi q6,q7,q8
gm=json.load(open('G_fifth_measured.json'))['depths']       # fifth q10..13
fl=json.load(open('fifth_ladder.json'))['results']['lam8.0']

# pi convergents
pcf=cf_frac(mp.pi,12); pps,pqs=convergents(pcf)
# fifth convergents
acf=cf_frac(mp.log(mp.mpf(3)/2)/mp.log(2),16); aps,aqs=convergents(acf)

def factor_step(Wprev,Wn): return Wprev/Wn

# ---- a=1 factor points (f, factor, substrate) ----
pts=[]
# pi a3 (q113): W2(q106),W3(q113) via solver
W_106=W_of(pps[1],106); W_113=W_of(pps[2],113)
pts.append((7/113, factor_step(W_106,W_113), 'pi_a3'))
# pi a5 (q33215): W4=W5=0.007435 banked -> factor~1
pts.append((113/33215, 0.007435/0.007435, 'pi_a5'))  # ~1 (a5=1, tiny fraction)
# pi a6 (q66317): W5=0.007435, W6 banked
pts.append((33102/66317, factor_step(0.007435, pim['6']['W']), 'pi_a6'))
# pi a7 (q99532): W6,W7 banked
pts.append((33215/99532, factor_step(pim['6']['W'], pim['7']['W']), 'pi_a7'))
# fifth a6 (q53): W(q41),W(q53) from fifth_ladder dims -> W=q^(1-1/dim)
def W_from_dim(q,dim): return q**(1-1/dim)
W41=W_from_dim(41, fl['41']['dim_bandscaling']); W53=W_from_dim(53, fl['53']['dim_bandscaling'])
pts.append((12/53, factor_step(W41,W53), 'fifth_a6'))
# fifth a12,a13 (q111202,q190537): from G data
pts.append((31867/111202, factor_step(gm['11']['W'], gm['12']['W']), 'fifth_a12'))
pts.append((79335/190537, factor_step(gm['12']['W'], gm['13']['W']), 'fifth_a13'))

pts.sort()
print("a=1 factor table (banked pi + fifth), by older-block fraction:")
print(f"  {'fraction':>9} {'factor g(1,f)':>13} {'substrate':>10}")
for f,g,s in pts: print(f"  {f:>9.4f} {g:>13.4f} {s:>10}")

# ---- FIT g(1,f): monotone interpolation of ln(factor) vs fraction (the sealed curve) ----
fa=np.array([f for f,_,_ in pts]); ga=np.array([g for _,g,_ in pts])
def g_curve(f): return float(np.exp(np.interp(f, fa, np.log(ga))))
# crossover: M(1,f)=0 needs factor(f)=q_growth. For a=1, q_growth depends on CF; report where g(1,f)=phi (golden
# q-growth) as the phi-relevant crossover, and tabulate g on a grid.
grid=np.linspace(0.05,0.5,19); sealed_curve=[(float(f),g_curve(f)) for f in grid]
phi=(1+5**0.5)/2
# phi crossover: dim drops iff g(1,f) > q_growth; for phi q_growth->phi=1.618
print(f"\nsealed g(1,f) at phi's fraction 0.382 = {g_curve(0.382):.3f} ; phi q-growth (F ratio->phi) = {phi:.3f}")
print(f"  => predicted phi margin M = ln(g)-ln(phi) = {math.log(g_curve(0.382))-math.log(phi):+.3f} "
      f"({'phi RETREATS' if g_curve(0.382)>phi else 'phi RISES'})")

sealed=dict(gate1_defs="factor=W_{n-1}/W_n; M=ln(factor)-ln(q_n/q_{n-1}); a=1 factor = g(1, q_{n-2}/q_n)",
            a1_points=[(float(f),float(g),s) for f,g,s in pts], sealed_g1_curve=sealed_curve,
            phi_fraction_limit=1/phi**2, phi_q_growth=phi, g1_at_0382=g_curve(0.382),
            prediction=("phi's a=1 factors (fractions spanning 0.333-0.5, converging to 0.382) fall on the sealed "
                        "g(1,f) curve fit from pi+fifth ONLY. If they do, a=1 thinning is substrate-INDEPENDENT "
                        "(computable from fraction). If phi deviates (e.g. constant golden 2.51 regardless of f), "
                        "a=1 carries substrate/self-similarity structure beyond the older-block fraction."),
            falsifier="phi's measured g(1,f) deviates >15% from the sealed curve at matched fraction.")
json.dump(sealed, open('H_phi_prediction_SEALED.json','w'), indent=1, default=float)
print("\nwrote H_phi_prediction_SEALED.json (byte-locked before phi measurement)")
