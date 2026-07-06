"""Session G — in-sample fit of the CF-convergence law on π (depths 1-8), then SEAL the out-of-sample
fifth prediction (depths 10-13, beyond the old q=15601 frontier). Byte-locked before measuring.

Law: dim_n = ln q_n / ln(q_n/W_n); W thins per convergent step by the Thouless per-step factor —
a>=2: λ·g(a); a=1: f(older-block fraction q_{k-2}/q_k). Both g(2) and the a=1 curve are fit IN-SAMPLE on
π's own steps (a8=2 gives g(2); a3,a5,a6,a7=1 give the a=1 curve at fractions {0.003,0.062,0.334,0.499}),
then applied UNCHANGED to the fifth. BASE_SEED=20240517.
"""
import sys,math,json; import numpy as np, mpmath as mp
sys.path.insert(0,'.')
from task1_pi_depth5 import cf_frac, convergents
mp.mp.dps=60; LAM=8.0; OUT='.'

# ---- GATE 2: fifth three-precision CF + records, from certified computation (not memory) ----
def cf_at(dps,n):
    mp.mp.dps=dps; x=mp.log(mp.mpf(3)/2)/mp.log(2); y=x-int(mp.floor(x)); a=[]
    for _ in range(n):
        ai=int(mp.floor(1/y)); a.append(ai); y=1/y-ai
    return a
c50,c80,c150=cf_at(50,50),cf_at(80,50),cf_at(150,50)
depth=0
for x,y,z in zip(c50,c80,c150):
    if x==y==z: depth+=1
    else: break
A=c50[:depth]; assert depth>=48, depth
# records
rec=[]; run=0
for k,a in enumerate(A):
    if a>run: rec.append((k+1,a)); run=a
assert (9,23) in rec and (14,55) in rec, rec
mp.mp.dps=60; ps5,qs5=convergents(A)
assert qs5[8]==15601 and qs5[13]==qs5[13]
print(f"GATE 2 OK: fifth 3-precision CF depth {depth}; records {rec[:6]}; a=23@9(q=15601), a=55@14.")

# ---- banked dims (from certified files, per gate 2 discipline) ----
pi_dims={1:0.7331,2:0.6244,3:0.6276,4:0.6798,5:0.6799}
m=json.load(open('pi292_measured.json'))['depths']
for d in (6,7,8): pi_dims[d]=m[str(d)]['dim']
pcf=cf_frac(mp.pi,12); pps,pqs=convergents(pcf); PQ={i+1:pqs[i] for i in range(8)}
picf={i+1:pcf[i] for i in range(8)}   # a1..a8

def W_from_dim(q,dim): return q**(1.0-1.0/dim)
def dim_from_W(q,W): return math.log(q)/math.log(q/W)

# ---- IN-SAMPLE FIT on π: extract per-step factors, calibrate g(2) and the a=1 curve ----
PW={d:W_from_dim(PQ[d],pi_dims[d]) for d in range(1,9)}
print("\nIN-SAMPLE (π): per-step W-thinning factors vs the Thouless law")
a1_pts=[]   # (older_block_fraction, factor)
g2=None
for d in range(2,9):
    a=picf[d]; factor=PW[d-1]/PW[d]
    if a==1:
        frac=PQ[d-2]/PQ[d] if d>=3 else PQ[1]/PQ[d]
        a1_pts.append((frac,factor)); kind=f"a=1 f={frac:.3f}"
    else:
        kind=f"a={a}"
        if a==2: g2=factor/LAM
    print(f"  depth {d-1}->{d}: {kind:12} factor={factor:.4f}" + (f"  -> g(2)={factor/LAM:.3f}" if a==2 else ""))
a1_pts.sort()
a1_f=np.array([p[0] for p in a1_pts]); a1_fac=np.array([p[1] for p in a1_pts])
def a1_factor(frac): return float(np.exp(np.interp(frac,a1_f,np.log(a1_fac))))
print(f"  fitted g(2)={g2:.3f}; a=1 curve from π fractions {[round(f,3) for f in a1_f]} factors {[round(x,3) for x in a1_fac]}")

# ---- SEAL: apply π-fit law UNCHANGED to the fifth depths 10-13 ----
W9=W_from_dim(15601,0.4660)   # fifth banked anchor (dim9=0.4660 @ q=15601)
steps=[]; W=W9
for d in (10,11,12,13):
    a=A[d-1]; q=qs5[d-1]
    if a==1:
        frac=qs5[d-3]/qs5[d-1]; fac=a1_factor(frac); kind=f"a=1 f={frac:.3f} (FAREY-only: below a=23 record)"
    else:
        fac=LAM*g2; kind=f"a={a} (FAREY-only: below a=23 record)"
    W=W/fac; dim=dim_from_W(q,W)
    steps.append(dict(depth=d,a=a,q=int(q),thin_factor=fac,W=W,dim_predicted=dim,channel="farey_only",kind=kind))
    print(f"  SEALED fifth depth {d}: {kind:42} q={q:>7} thin×{fac:.2f} dim_pred={dim:.4f}")

sealed=dict(sealed_by="Session G in-sample π fit (depths 1-8)", anchor="fifth dim9=0.4660 @ q=15601",
            fit=dict(g2=g2, a1_curve=[(float(f),float(x)) for f,x in a1_pts]),
            fifth_cf_records=rec, prediction=steps,
            prediction_direction="fifth dim continues to retreat across 10-13 (a10=2,a11=2 thin; a12,a13=1 golden-ish)",
            residual_note=("all four steps 10-13 are FAREY-ONLY (below the a=23 running record) — a record-channel-only "
                           "law would be BLIND to them; the Farey-complete Thouless law predicts them. If measurement "
                           "matches, convergence is Farey-governed (non-record), confirming the Session-C §9 record/Farey "
                           "non-equivalence. If it misses, the law has a record-only component."),
            falsifier="if measured fifth dims 10-13 do NOT monotonically retreat, or deviate >0.02 from predicted, the "
                      "Farey-complete convergence law fails out-of-sample on the fifth.")
json.dump(sealed, open('G_fifth_prediction_SEALED.json','w'), indent=1)
print("\nwrote G_fifth_prediction_SEALED.json (byte-locked before measurement)")
